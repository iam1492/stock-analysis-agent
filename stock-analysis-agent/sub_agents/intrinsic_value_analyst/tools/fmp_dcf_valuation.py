from ...utils.fmp_api_client import make_fmp_api_request

def fmp_dcf_valuation(ticker: str):
    """
    Estimate the intrinsic value of a company with the FMP Discounted Cash Flow Valuation API. 
    Calculate the DCF valuation based on expected future cash flows and discount rates.
    Input paramter:
    - ticker(type:str): The ticker of a company.
    """    
    params = {
        "symbol": ticker
    }
    return make_fmp_api_request("discounted-cash-flow", params)
