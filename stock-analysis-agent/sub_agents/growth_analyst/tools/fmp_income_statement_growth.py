from ...utils.fmp_api_client import make_fmp_api_request

def fmp_income_statement_growth(ticker: str):
    """
    손익 계산서 성장(income statement growth) API를 사용하여 주요 재무 성장 지표를 추적합니다. 
    시간 경과에 따른 수익, 이익 및 비용의 변화를 분석하여 회사의 재무 건전성과 운영 효율성에 대한 통찰력을 제공합니다.
    입력 매개변수:
    - ticker(type:str): 회사의 티커(종목 코드).
    """
    params = {
        "symbol": ticker,
        "period": "quarter",
        "limit": 10
    }
    return make_fmp_api_request("income-statement-growth", params)
