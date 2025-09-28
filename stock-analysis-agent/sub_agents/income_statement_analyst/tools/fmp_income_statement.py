from ...utils.fmp_api_client import make_fmp_api_request

def fmp_income_statement(ticker: str, limit: int, period: str):
    """
    FMP 실시간 손익계산서 API를 사용하여 상장 기업, 비상장 기업 및 ETF의 실시간 손익계산서 데이터를 접근하세요.
    수익성을 추적하고, 경쟁사를 비교하며, 최신 재무 데이터를 통해 비즈니스 트렌드를 식별하세요.
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
    return make_fmp_api_request("income-statement", params)
