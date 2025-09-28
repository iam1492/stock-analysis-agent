from ...utils.fmp_api_client import make_fmp_api_request

def fmp_simple_moving_average(ticker: str):
    """
    Get historical simple moving average data for a stock ticker.
    Input paramter:
    - ticker(type:str): The ticker of a company.
    """
    params = {
        "symbol": ticker,
        "periodLength": 10,
        "timeframe": "1day"
    }
    return make_fmp_api_request("technical-indicators/sma", params)
