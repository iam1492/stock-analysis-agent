from ...utils.fmp_api_client import make_fmp_api_request

def fmp_price_target_summary(ticker: str):
    """
    Gain insights into analysts' expectations for stock prices with the FMP Price Target Summary API. 
    This API provides access to average price targets from analysts across various timeframes, helping investors assess future stock performance based on expert opinions.
    입력 매개변수:
    - ticker(type:str): 회사의 티커.
    """
    params = {
        "symbol": ticker
    }
    return make_fmp_api_request("price-target-summary", params)
