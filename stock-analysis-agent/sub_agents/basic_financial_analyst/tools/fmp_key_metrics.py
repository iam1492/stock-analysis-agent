import os
import requests

fmp_api_base_url = "https://financialmodelingprep.com/stable/"
def fmp_key_metrics(ticker: str):
    """
    Access essential financial metrics for a company with the FMP Financial Key Metrics API. 
    Evaluate revenue, net income, P/E ratio, and more to assess performance and compare it to competitors.
    Input paramter:
    - ticker(type:str): The ticker of a company.
    """
    api_key = os.environ["FMP_API_KEY"]
    url = f"{fmp_api_base_url}/key-metrics?symbol={ticker}&apikey={api_key}"
    response = requests.get(url)
    if response.status_code == 200:
        return response.json()
    else:
        return {"error": f"Failed to fetch data: {response.status_code}"}
