from ...utils.fmp_api_client import make_fmp_api_request

def fmp_balance_sheet_statement_growth(ticker: str):
    """
    Analyze the growth of key balance sheet items over time with the Balance Sheet Statement Growth API. 
    Track changes in assets, liabilities, and equity to understand the financial evolution of a company.
    Input paramter:
    - ticker(type:str): The ticker of a company.
    """
    params = {
        "symbol": ticker,
        "period": "quarter",
        "limit": 10
    }
    return make_fmp_api_request("balance-sheet-statement-growth", params)
