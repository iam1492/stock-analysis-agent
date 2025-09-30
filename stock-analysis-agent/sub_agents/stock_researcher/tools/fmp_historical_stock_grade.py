from ...utils.fmp_api_client import make_fmp_api_request

def fmp_historical_stock_grade(ticker: str):
    """
    FMP Historical Grades API로 애널리스트 등급의 전체 기록에 접근하세요. 
    이 도구를 이용하면 특정 주식 종목에 대한 애널리스트 평가의 과거 변동 사항을 추적할 수 있습니다.
    이 도구의 핵심 가치는 특정 주식 종목에 대한 애널리스트들의 평가 변화를 이해하는 데 있습니다.
    
    입력 매개변수:
    - ticker(type:str): 회사의 티커.
    """
    
    params = {
        "symbol": ticker,
        "limit": 20
    }
    return make_fmp_api_request("grades-historical", params)
