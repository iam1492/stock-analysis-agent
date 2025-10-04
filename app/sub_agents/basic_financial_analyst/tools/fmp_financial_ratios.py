from ...utils.fmp_api_client import make_fmp_api_request

def fmp_financial_ratios(ticker: str):
    """
    FMP 재무 비율 API를 사용하여 회사의 필수 재무 비율(financial ratios)에 접근합니다. 
    수익성, 유동성, 레버리지 및 효율성 비율을 평가하여 성과를 측정하고 경쟁사와 비교합니다.
    입력 매개변수:
    - ticker(type:str): 회사의 티커(종목 코드).
    """
    params = {
        "symbol": ticker
    }
    return make_fmp_api_request("ratios", params)
