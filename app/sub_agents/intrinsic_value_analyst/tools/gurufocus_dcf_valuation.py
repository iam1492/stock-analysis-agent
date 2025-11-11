import requests
from bs4 import BeautifulSoup
import re
import sys
import json

def gurufocus_dcf(ticker: str):
    """
    도구명: gurufocus_dcf
    GuruFocus DCF 계산기에서 특정 티커의 DCF 데이터를 스크레이핑합니다.
    
    Input Param:
    ticker: 주식 티커
    
    파싱하는 데이터:
    1. Stock Price (주가)
    2. Fair Value (적정 가치) - 값이 'a' (N/A)인 경우 처리
    3. Margin of Safety (안전 마진)
    4. low_predictability (낮은 예측 가능성) 경고 여부 (True/False)
    - low_predictability가 true 인경우는 신뢰도가 낮아서 데이터를 활용하지 못함을 의미
    - low_predictability가 false 인경우는 신뢰도 양호
    
    [Return 예시]
    {
    "ticker": "AMZN",
    "stock_price": "$ 248.40",
    "fair_value": "$ 188.41",
    "margin_of_safety": "-31.84%",
    "low_predictability": false
    }
    """
    
    url = f"https://www.gurufocus.com/dcf-calculator?ticker={ticker}"
    
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }

    try:
        # 1. 웹페이지 요청
        response = requests.get(url, headers=headers)
        response.raise_for_status()

        # 2. BeautifulSoup으로 HTML 파싱
        soup = BeautifulSoup(response.text, 'html.parser')

        # 3. 경고 메시지 확인 (low_predictability)
        low_predictability = False # 기본값은 False
        warning_element = soup.find('span', class_='el-alert__title')
        if warning_element:
            warning_text = warning_element.get_text(strip=True)
            if "low predictability of business" in warning_text:
                low_predictability = True
        
        # 4. 데이터가 포함된 <script> 태그 찾기
        script_tag = soup.find('script', string=re.compile(r'window\.__NUXT__='))
        
        if not script_tag:
            print(f"Error: {ticker}의 NUXT 데이터 스크립트를 찾을 수 없습니다.", file=sys.stderr)
            return

        script_data = script_tag.string

        # 5. 정규 표현식으로 핵심 데이터 추출
        # 5-1. Stock Price
        price_match = re.search(r'price:(\d+\.?\d*),', script_data)
        
        # 5-2. Fair Value (음수, 양수, 'a' 모두 처리)
        fair_value_match = re.search(r'iv_dcEarning:(-?\d+\.?\d*|a),', script_data)

        stock_price = None
        fair_value = None

        # Stock Price 파싱
        if price_match:
            stock_price = float(price_match.group(1))
        else:
            print(f"Error: {ticker}의 Stock Price를 파싱할 수 없습니다.", file=sys.stderr)
            return

        # Fair Value 파싱
        if fair_value_match:
            fv_str = fair_value_match.group(1)
            # 값이 'a'가 아닐 때만 float으로 변환
            if fv_str != 'a':
                fair_value = float(fv_str)

        # 6. 결과 객체 생성
        result = {
            "ticker": ticker,
            "stock_price": f"$ {stock_price:.2f}",
            "fair_value": "N/A",
            "margin_of_safety": "N/A",
            "low_predictability": low_predictability
        }

        # 7. Fair Value가 N/A가 아닐 경우에만 Margin of Safety 계산
        if fair_value is not None:
            # 0으로 나누는 경우 방지
            if fair_value == 0:
                margin_of_safety = -float('inf') if stock_price > 0 else 0
            else:
                # 안전마진 공식: (적정가치 - 주가) / |적정가치|
                margin_of_safety = ((fair_value - stock_price) / abs(fair_value)) * 100
            
            result["fair_value"] = f"$ {fair_value:.2f}"
            result["margin_of_safety"] = f"{margin_of_safety:.2f}%"
        
        # 8. 결과 출력
        
        return json.dumps(result, indent=2)
    except requests.exceptions.RequestException as e:
        print(f"Error: {ticker} 페이지를 가져오는 중 오류 발생: {e}", file=sys.stderr)
    except Exception as e:
        print(f"Error: {ticker} 데이터 파싱 중 알 수 없는 오류 발생: {e}", file=sys.stderr)
