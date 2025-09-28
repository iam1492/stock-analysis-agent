from ...utils.fmp_api_client import make_fmp_api_request

def fmp_income_statement_growth(ticker: str):
    """
    Track key financial growth metrics with the Income Statement Growth API. 
    Analyze how revenue, profits, and expenses have evolved over time, offering insights into a company’s financial health and operational efficiency.
    Input paramter:
    - ticker(type:str): The ticker of a company.
    """
    params = {
        "symbol": ticker,
        "period": "quarter",
        "limit": 10
    }
    return make_fmp_api_request("income-statement-growth", params)