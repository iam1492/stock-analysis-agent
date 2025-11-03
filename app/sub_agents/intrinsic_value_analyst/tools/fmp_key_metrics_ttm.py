from ...utils.fmp_api_client import make_fmp_api_request

def fmp_key_metrics_ttm(ticker: str):
    """
    TTM Key Metrics API를 사용하여 최근 12개월(TTM)의 주요 성과 지표를 종합적으로 검색합니다. 
    기업의 수익성, 자본 효율성, 유동성 관련 데이터에 접근하여 지난 1년간의 재무 건전성을 상세하게 분석할 수 있습니다.
    
    입력 매개변수:
    - ticker(type:str): 회사의 티커(종목 코드).
    """
    params = {
        "symbol": ticker
    }
    return make_fmp_api_request("key-metrics-ttm", params)
