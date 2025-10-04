from ...utils.fmp_api_client import make_fmp_api_request

def fmp_dcf_valuation(ticker: str):
    """
    할인된 현금 흐름(DCF) 가치 평가 API를 사용하여 회사의 내재 가치를 추정합니다. 
    예상 미래 현금 흐름 및 할인율을 기반으로 DCF 가치 평가를 계산합니다.
    입력 매개변수:
    - ticker(type:str): 회사의 티커(종목 코드).
    """    
    params = {
        "symbol": ticker
    }
    return make_fmp_api_request("discounted-cash-flow", params)
