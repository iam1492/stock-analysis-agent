from ...utils.fmp_api_client import make_fmp_api_request

def fmp_price_target_news(ticker: str):
    """
    FMP Price Target News API를 이용해 주식에 대한 애널리스트의 목표 주가 실시간 업데이트 정보를 가져옵니다. 
    최신 예측, 업데이트 시점의 주가, 그리고 심층적인 정보를 위한 신뢰할 수 있는 뉴스 소스 링크를 바로 확인할 수 있습니다.
    입력 매개변수:
    - ticker(type:str): 회사의 티커.
    """
    params = {
        "symbols": ticker,
        "limit": 10,
        "page": 0
    }
    return make_fmp_api_request("price-target-news", params)
