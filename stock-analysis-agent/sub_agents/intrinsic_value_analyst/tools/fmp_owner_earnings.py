from ...utils.fmp_api_client import make_fmp_api_request

def fmp_owner_earnings(ticker: str):
    """
    Owner Earnings API를 사용하여 회사의 소유자 이익을 검색합니다. 이는 순이익을 조정하여 주주에게 사용 가능한 현금을 보다 정확하게 나타냅니다. 
    이 지표는 투자자 관점에서 회사의 수익성을 평가하는 데 중요합니다.
    입력 매개변수:
    - ticker(type:str): 회사의 티커(종목 코드).
    """
    
    params = {
        "symbol": ticker
    }
    return make_fmp_api_request("owner-earnings", params)
