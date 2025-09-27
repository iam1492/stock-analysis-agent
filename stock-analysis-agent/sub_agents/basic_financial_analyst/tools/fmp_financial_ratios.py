import os
import requests

fmp_api_base_url = "https://financialmodelingprep.com/stable/"
def fmp_financial_ratios(ticker: str):
    """
    Analyze a company's financial performance using the Financial Ratios API. 
    This API provides detailed profitability, liquidity, and efficiency ratios, enabling users to assess a company's operational and financial health across various metrics.
    Input paramter:
    - ticker(type:str): The ticker of a company.
    """
    api_key = os.environ["FMP_API_KEY"]
    url = f"{fmp_api_base_url}/ratios?symbol={ticker}&apikey={api_key}"
    response = requests.get(url)
    if response.status_code == 200:
        return response.json()
    else:
        return {"error": f"Failed to fetch data: {response.status_code}"}
