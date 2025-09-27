import os
import requests

fmp_api_base_url = "https://financialmodelingprep.com/stable/"
def fmp_balance_sheet(ticker: str, limit: int, period: str):
    """
    Balance Sheet Data API를 사용하여 상장 기업의 상세한 대차대조표를 접근하세요.
    자산, 부채, 주주 자본을 분석하여 기업의 재무 건전성을 파악하세요.
    입력 매개변수:
    - ticker(type:str): 기업의 티커.
    - limit(type:int): 반환할 결과의 수.
    - period(type:str): Q1,Q2,Q3,Q4,FY,annual,quarter
    """
    api_key = os.environ["FMP_API_KEY"]
    url = f"{fmp_api_base_url}/balance-sheet-statement?symbol={ticker}&limit={limit}&period={period}&apikey={api_key}"
    response = requests.get(url)
    if response.status_code == 200:
        return response.json()
    else:
        return {"error": f"Failed to fetch data: {response.status_code}"}
