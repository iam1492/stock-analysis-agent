from ...utils.fmp_api_client import make_fmp_api_request

def fmp_balance_sheet(ticker: str, limit: int, period: str):
    """
    Balance Sheet Data API를 사용하여 상장 기업의 상세한 대차대조표를 접근하세요.
    자산, 부채, 주주 자본을 분석하여 기업의 재무 건전성을 파악하세요.
    입력 매개변수:
    - ticker(type:str): 기업의 티커.
    - limit(type:int): 반환할 결과의 수.
    - period(type:str): Q1,Q2,Q3,Q4,FY,annual,quarter
    """
    params = {
        "symbol": ticker,
        "limit": limit,
        "period": period
    }
    return make_fmp_api_request("balance-sheet-statement", params)
