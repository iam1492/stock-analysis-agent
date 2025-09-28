from ...utils.fmp_api_client import make_fmp_api_request

def fmt_stock_news(ticker: str):
    """
    FMP Search Stock News API를 사용하여 주식 관련 뉴스를 검색합니다.
    티커 심볼이나 회사 이름을 입력하여 특정 주식 뉴스를 찾아 최신 동향을 추적합니다.
    입력 매개변수:
    - ticker(type:str): 회사의 티커.
    """
    params = {
        "symbols": ticker,
        "limit": 50
    }
    return make_fmp_api_request("news/stock", params)
