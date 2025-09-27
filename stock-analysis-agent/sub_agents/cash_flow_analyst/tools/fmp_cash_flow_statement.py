import os
import requests

fmp_api_base_url = "https://financialmodelingprep.com/stable/"
def fmp_cash_flow_statement(ticker: str, limit: int, period: str):
    """
    Gain insights into a company's cash flow activities with the Cash Flow Statements API. 
    Analyze cash generated and used from operations, investments, and financing activities to evaluate the financial health and sustainability of a business.
    Input paramter:
    - ticker(type:str): The ticker of a company.
    - limit(type:int): The number of results to return.
    - period(type:str): Q1,Q2,Q3,Q4,FY,annual,quarter
    """
    api_key = os.environ["FMP_API_KEY"]
    url = f"{fmp_api_base_url}/cash-flow-statement?symbol={ticker}&limit={limit}&period={period}&apikey={api_key}"
    response = requests.get(url)
    if response.status_code == 200:
        return response.json()
    else:
        return {"error": f"Failed to fetch data: {response.status_code}"}