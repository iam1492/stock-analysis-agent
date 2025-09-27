import os
import requests
fmp_api_base_url = "https://financialmodelingprep.com/stable/"
def fmp_income_statement(ticker: str, limit: int, period: str):
    """
    FMP 실시간 손익계산서 API를 사용하여 상장 기업, 비상장 기업 및 ETF의 실시간 손익계산서 데이터를 접근하세요.
    수익성을 추적하고, 경쟁사를 비교하며, 최신 재무 데이터를 통해 비즈니스 트렌드를 식별하세요.
    입력 매개변수:
    - ticker(type:str): 기업의 티커.
    - limit(type:int): 반환할 결과의 수.
    - period(type:str): Q1,Q2,Q3,Q4,FY,annual,quarter
    """
    api_key = os.environ["FMP_API_KEY"]
    url = f"{fmp_api_base_url}/income-statement?symbol={ticker}&limit={limit}&period={period}&apikey={api_key}"
    response = requests.get(url)
    if response.status_code == 200:
        return response.json()
    else:
        return {"error": f"Failed to fetch data: {response.status_code}"}
