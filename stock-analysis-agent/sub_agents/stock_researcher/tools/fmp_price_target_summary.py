from ...utils.fmp_api_client import make_fmp_api_request

def fmp_price_target_summary(ticker: str):
    """
    목표 주가 요약(price target summary) API를 사용하여 주가에 대한 분석가의 기대치를 파악합니다. 
    이 API는 다양한 기간에 걸친 분석가의 평균 목표 주가에 대한 접근을 제공하여 투자자가 전문가 의견을 기반으로 미래 주식 성과를 평가하는 데 도움을 줍니다.
    입력 매개변수:
    - ticker(type:str): 회사의 티커(종목 코드).
    """
    params = {
        "symbol": ticker
    }
    return make_fmp_api_request("price-target-summary", params)
