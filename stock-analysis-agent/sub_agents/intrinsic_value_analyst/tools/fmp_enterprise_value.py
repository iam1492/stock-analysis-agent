from ...utils.fmp_api_client import make_fmp_api_request

def fmp_enterprise_value(ticker: str):
    """
    Access a company's enterprise value using the Enterprise Values API. 
    This metric offers a comprehensive view of a company's total market value by combining both its equity (market capitalization) and debt, providing a better understanding of its worth.
    Input paramter:
    - ticker(type:str): The ticker of a company.
    """
    
    params = {
        "symbol": ticker
    }
    return make_fmp_api_request("enterprise-values", params)
