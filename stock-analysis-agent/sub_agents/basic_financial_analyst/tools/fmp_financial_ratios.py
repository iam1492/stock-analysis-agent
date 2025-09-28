from ...utils.fmp_api_client import make_fmp_api_request

def fmp_financial_ratios(ticker: str):
    """
    Access essential financial ratios for a company with the FMP Financial Ratios API. 
    Evaluate profitability, liquidity, leverage, and efficiency ratios to assess performance and compare it to competitors.
    Input paramter:
    - ticker(type:str): The ticker of a company.
    """
    params = {
        "symbol": ticker
    }
    return make_fmp_api_request("ratios", params)
