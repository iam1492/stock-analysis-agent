from ...utils.fmp_api_client import make_fmp_api_request

def fmp_key_metrics(ticker: str):
    """
    FMP 재무 핵심 지표 API를 사용하여 회사의 필수 재무 지표(key metrics)에 접근합니다. 
    수익, 순이익, P/E 비율 등을 평가하여 성과를 측정하고 경쟁사와 비교합니다.
    입력 매개변수:
    - ticker(type:str): 회사의 티커(종목 코드).
    """
    params = {
        "symbol": ticker
    }
    return make_fmp_api_request("key-metrics", params)
