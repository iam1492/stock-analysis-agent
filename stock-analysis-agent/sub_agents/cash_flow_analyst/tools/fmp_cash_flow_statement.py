from ...utils.fmp_api_client import make_fmp_api_request

def fmp_cash_flow_statement(ticker: str, limit: int, period: str):
    """
    현금 흐름표(cash flow statement) API를 사용하여 회사의 현금 흐름 활동에 대한 통찰력을 얻습니다. 
    영업, 투자 및 재무 활동에서 생성 및 사용된 현금을 분석하여 비즈니스의 재무 건전성과 지속 가능성을 평가합니다.
    입력 매개변수:
    - ticker(type:str): 회사의 티커(종목 코드).
    - limit(type:int): 반환할 결과의 수.
    - period(type:str): Q1,Q2,Q3,Q4,FY,annual,quarter
    """
    params = {
        "symbol": ticker,
        "limit": limit,
        "period": period
    }
    return make_fmp_api_request("cash-flow-statement", params)
