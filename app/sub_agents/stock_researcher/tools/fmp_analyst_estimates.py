from ...utils.fmp_api_client import make_fmp_api_request

def fmp_analyst_estimates(ticker: str):
    """
    FMP Financial Estimates API를 사용하여 주식 심볼별 애널리스트 과거와 미래의 재무 추정치 히스토리를 검색합니다. 
    업계 애널리스트들이 예측한 수익(revenue), 주당 순이익(EPS) 및 기타 주요 재무 지표와 같은 예상 수치를 확보하여 미래 투자 결정에 활용할 수 있습니다.
    입력 매개변수:
    - ticker(type:str): 회사의 티커(종목 코드).
    """
    params = {
        "symbol": ticker,
        "period": "annual",
        "page":0,
        "limit":10
    }
    return make_fmp_api_request("analyst-estimates", params)
