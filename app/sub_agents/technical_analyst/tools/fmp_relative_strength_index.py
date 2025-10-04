from ...utils.fmp_api_client import make_fmp_api_request

def fmp_relative_strength_index(ticker: str):
    """
    주식 티커에 대한 과거 상대 강도 지수(RSI) 데이터를 가져옵니다.
    입력 매개변수:
    - ticker(type:str): 회사의 티커(종목 코드).
    """
    params = {
        "symbol": ticker,
        "periodLength": 10,
        "timeframe": "1day"
    }
    return make_fmp_api_request("technical-indicators/rsi", params)
