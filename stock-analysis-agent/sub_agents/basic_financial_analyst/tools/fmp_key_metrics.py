from ...utils.fmp_api_client import make_fmp_api_request

def fmp_key_metrics(ticker: str):
    """
    Access essential financial metrics for a company with the FMP Financial Key Metrics API. 
    Evaluate revenue, net income, P/E ratio, and more to assess performance and compare it to competitors.
    Input paramter:
    - ticker(type:str): The ticker of a company.
    """
    params = {
        "symbol": ticker
    }
    return make_fmp_api_request("key-metrics", params)
