from ...utils.fmp_api_client import make_fmp_api_request

def fmp_owner_earnings(ticker: str):
    """
    Retrieve a company's owner earnings with the Owner Earnings API, which provides a more accurate representation of cash available to shareholders by adjusting net income. 
    This metric is crucial for evaluating a company’s profitability from the perspective of investors.
    Input paramter:
    - ticker(type:str): The ticker of a company.
    """
    
    params = {
        "symbol": ticker
    }
    return make_fmp_api_request("owner-earnings", params)
