from ...utils.fmp_api_client import make_fmp_api_request
from datetime import datetime, timedelta
from cachetools import cached, TTLCache

# 1 day cache, max size 1024
@cached(cache=TTLCache(maxsize=1024, ttl=86400))
def fmp_economic_indicators(name: str):
    """
    FMP 경제 지표 API를 사용하여 GDP, 실업률, 인플레이션과 같은 주요 지표에 대한 실시간 및 과거 경제 데이터에 접근합니다. 이 데이터를 사용하여 경제 성과를 측정하고 성장 추세를 식별합니다.
    3년 간의 과거 데이터가 제공됩니다.
    이 데이터를 사용하여 경제 성과를 측정하고 전반적인 주식에 미치는 영향을 분석합니다.
    [중요] 최대한 모든 입력 매개변수를 사용해서 여러번 이 도구를 호출함으로써 다양한 경제 지표에 대한 데이터를 수집하세요.
    
    입력 매개변수:
    - name(type:str): 경제 지표의 이름입니다.(예: federalFunds,CPI,inflationRate, totalNonfarmPayroll, unemploymentRate,realGDP,consumerSentiment, retailSales,industrialProductionTotalIndex, initialClaims, inflation)
    """

    # Set from_date to 3 years ago from today with format 'YYYY-MM-DD'
    from_date = (datetime.now() - timedelta(days=3*365)).strftime('%Y-%m-%d')
    params = {
        "name": name,
        "from": from_date
    }
    return make_fmp_api_request("economic-indicators", params)
