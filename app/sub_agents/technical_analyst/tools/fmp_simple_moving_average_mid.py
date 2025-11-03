from ...utils.fmp_api_client import make_fmp_api_request

def fmp_simple_moving_average_mid_term_trend(ticker: str):
    """
    Simple Moving Average of period length 30
    중기 추세 기준선
    주식 티커 중기 추세에 대한 과거 단순 이동 평균 데이터를 가져옵니다.
    period length 30으로 고정
    
    입력 매개변수:
    - ticker(type:str): 회사의 티커(종목 코드).
    """
    params = {
        "symbol": ticker,
        "periodLength": 30,
        "timeframe": "1day"
    }
    return make_fmp_api_request("technical-indicators/sma", params)
