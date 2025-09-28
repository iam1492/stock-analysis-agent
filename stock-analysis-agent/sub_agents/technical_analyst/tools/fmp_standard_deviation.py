from ...utils.fmp_api_client import make_fmp_api_request

def fmp_standard_deviation(ticker: str):
    """
    Get historical standard deviation data for a stock ticker.
    Input paramter:
    - ticker(type:str): The ticker of a company.
    """
    params = {
        "symbol": ticker,
        "periodLength": 10,
        "timeframe": "1day"
    }
    return make_fmp_api_request("technical-indicators/std", params)
