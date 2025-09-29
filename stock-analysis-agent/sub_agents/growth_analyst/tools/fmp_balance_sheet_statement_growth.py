from ...utils.fmp_api_client import make_fmp_api_request

def fmp_balance_sheet_statement_growth(ticker: str):
    """
    대차대조표 성장(balance sheet statement growth) API를 사용하여 주요 대차대조표 항목의 시간 경과에 따른 성장을 분석합니다. 
    자산, 부채 및 자본의 변화를 추적하여 회사의 재무 변화를 이해합니다.
    입력 매개변수:
    - ticker(type:str): 회사의 티커(종목 코드).
    """
    params = {
        "symbol": ticker,
        "period": "quarter",
        "limit": 10
    }
    return make_fmp_api_request("balance-sheet-statement-growth", params)
