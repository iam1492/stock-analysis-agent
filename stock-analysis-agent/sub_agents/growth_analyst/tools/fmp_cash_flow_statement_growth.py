from ...utils.fmp_api_client import make_fmp_api_request

def fmp_cash_flow_statement_growth(ticker: str):
    """
    Measure the growth rate of a company’s cash flow with the FMP Cashflow Statement Growth API. 
    Determine how quickly a company’s cash flow is increasing or decreasing over time.
    Input paramter:
    - ticker(type:str): The ticker of a company.
    """
    params = {
        "symbol": ticker,
        "period": "quarter",
        "limit": 10
    }
    return make_fmp_api_request("cash-flow-statement-growth", params)