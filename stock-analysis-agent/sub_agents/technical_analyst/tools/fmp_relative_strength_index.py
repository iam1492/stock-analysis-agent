import os
import requests

fmp_api_base_url = "https://financialmodelingprep.com/stable/"
def fmp_relative_strength_index(ticker: str):
    """
    Relative Strength Index (RSI) is a momentum oscillator that measures the speed and change of price movements. It oscillates between 0 and 100 and is typically used to identify overbought or oversold conditions in a stock. An RSI above 70 is generally considered overbought, while an RSI below 30 is considered oversold.
    Input paramter:
    - ticker(type:str): The ticker of a company.
    """
    api_key = os.environ["FMP_API_KEY"]
    url = f"{fmp_api_base_url}/technical-indicators/rsi?symbol={ticker}&periodLength=10&timeframe=1day&apikey={api_key}"
    response = requests.get(url)
    if response.status_code == 200:
        return response.json()
    else:
        return {"error": f"Failed to fetch data: {response.status_code}"}
