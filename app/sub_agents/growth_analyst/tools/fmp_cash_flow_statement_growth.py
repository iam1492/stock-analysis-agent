from ...utils.fmp_api_client import make_fmp_api_request

def fmp_cash_flow_statement_growth(ticker: str):
    """
    FMP 현금 흐름표 성장(cash flow statement growth) API를 사용하여 회사의 현금 흐름 성장률을 측정합니다. 
    시간 경과에 따라 회사의 현금 흐름이 얼마나 빠르게 증가하거나 감소하는지 확인합니다.
    입력 매개변수:
    - ticker(type:str): 회사의 티커(종목 코드).
    """
    params = {
        "symbol": ticker,
        "period": "quarter",
        "limit": 10
    }
    return make_fmp_api_request("cash-flow-statement-growth", params)
