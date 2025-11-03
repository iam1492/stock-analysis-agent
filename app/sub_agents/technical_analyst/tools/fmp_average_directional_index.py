from ...utils.fmp_api_client import make_fmp_api_request

def fmp_average_directional_index(ticker: str):
    """
    Average Directional Index
    주식 티커에 대한 추세 강도 데이터(adx 14)를 가져옵니다.
    periodLegnth 14로 고정.
    입력 매개변수:
    - ticker(type:str): 회사의 티커(종목 코드).
    """
    params = {
        "symbol": ticker,
        "periodLength": 14,
        "timeframe": "1day"
    }
    return make_fmp_api_request("technical-indicators/adx", params)
