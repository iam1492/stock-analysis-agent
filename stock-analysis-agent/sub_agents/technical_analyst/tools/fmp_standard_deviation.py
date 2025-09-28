import os
import requests

fmp_api_base_url = "https://financialmodelingprep.com/stable/"
def fmp_standard_deviation(ticker: str):
    """
    Standard Deviation (표준 편차) is a statistical measure that quantifies the amount of variation or dispersion in a set of values. In finance, it is commonly used to assess the volatility of a stock's price over a specific period. A higher standard deviation indicates greater price fluctuations, while a lower standard deviation suggests more stable prices.
    Input paramter:
    - ticker(type:str): The ticker of a company.
    """
    api_key = os.environ["FMP_API_KEY"]
    url = f"{fmp_api_base_url}/technical-indicators/standarddeviation?symbol={ticker}&periodLength=10&timeframe=1day&apikey={api_key}"
    response = requests.get(url)
    if response.status_code == 200:
        return response.json()
    else:
        return {"error": f"Failed to fetch data: {response.status_code}"}
