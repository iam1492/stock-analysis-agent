from ...utils.fmp_api_client import make_fmp_api_request

def fmp_enterprise_value(ticker: str):
    """
    Enterprise Values API를 사용하여 회사의 기업 가치에 접근합니다. 
    이 지표는 회사의 자본(시가총액)과 부채를 모두 결합하여 회사의 총 시장 가치에 대한 포괄적인 시각을 제공하여 회사의 가치를 더 잘 이해할 수 있도록 합니다.
    입력 매개변수:
    - ticker(type:str): 회사의 티커(종목 코드).
    """
    
    params = {
        "symbol": ticker
    }
    return make_fmp_api_request("enterprise-values", params)
