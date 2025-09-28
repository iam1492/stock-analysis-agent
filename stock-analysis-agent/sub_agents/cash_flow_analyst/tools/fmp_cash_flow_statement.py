from ...utils.fmp_api_client import make_fmp_api_request

def fmp_cash_flow_statement(ticker: str, limit: int, period: str):
    """
    Gain insights into a company's cash flow activities with the Cash Flow Statements API. 
    Analyze cash generated and used from operations, investments, and financing activities to evaluate the financial health and sustainability of a business.
    Input paramter:
    - ticker(type:str): The ticker of a company.
    - limit(type:int): The number of results to return.
    - period(type:str): Q1,Q2,Q3,Q4,FY,annual,quarter
    """
    params = {
        "symbol": ticker,
        "limit": limit,
        "period": period
    }
    return make_fmp_api_request("cash-flow-statement", params)
