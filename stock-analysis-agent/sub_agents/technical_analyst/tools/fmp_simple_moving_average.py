import os
import requests

fmp_api_base_url = "https://financialmodelingprep.com/stable/"
def fmp_simple_moving_average(ticker: str):
    """
    Get historical simple moving average data for a stock ticker.
    Input paramter:
    - ticker(type:str): The ticker of a company.
    """
    api_key = os.environ["FMP_API_KEY"]
    url = f"{fmp_api_base_url}/technical-indicators/sma?symbol={ticker}&periodLength=10&timeframe=1day&apikey={api_key}"
    response = requests.get(url)
    if response.status_code == 200:
        return response.json()
    else:
        return {"error": f"Failed to fetch data: {response.status_code}"}
