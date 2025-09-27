import os
import requests

fmp_api_base_url = "https://financialmodelingprep.com/stable/"
def fmt_stock_news(ticker: str):
    """
    FMP Search Stock News API를 사용하여 주식 관련 뉴스를 검색합니다.
    티커 심볼이나 회사 이름을 입력하여 특정 주식 뉴스를 찾아 최신 동향을 추적합니다.
    입력 매개변수:
    - ticker(type:str): 회사의 티커.
    """
    api_key = os.environ["FMP_API_KEY"]
    url = f"{fmp_api_base_url}/news/stock?symbols={ticker}&limit=50&apikey={api_key}"
    response = requests.get(url)
    if response.status_code == 200:
        return response.json()
    else:
        return {"error": f"Failed to fetch data: {response.status_code}"}
