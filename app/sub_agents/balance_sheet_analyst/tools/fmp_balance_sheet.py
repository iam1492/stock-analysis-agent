from ...utils.fmp_api_client import make_fmp_api_request

def fmp_balance_sheet(ticker: str, limit: int, period: str):
    """
    Balance Sheet Data API를 사용하여 상장 기업의 상세한 대차대조표를 접근하세요.
    자산, 부채, 주주 자본을 분석하여 기업의 재무 건전성을 파악하세요.
    Response 데이터는 실제 공시가된 확정데이터입니다.
    최신 데이터를 파악하기 위해 quater데이터를 반드시 확인해야 합니다.
    이 데이터에는 예상치는 없습니다.
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
