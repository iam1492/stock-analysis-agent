from ...utils.fmp_api_client import make_fmp_api_request
from datetime import datetime, timedelta
from cachetools import cached, TTLCache

# 1 day cache, max size 1024
@cached(cache=TTLCache(maxsize=1024, ttl=86400))
def fmp_economic_indicators(name: str, ticker: str):
    """
    Access real-time and historical economic data for key indicators like GDP, unemployment, and inflation with the FMP Economic Indicators API. Use this data to measure economic performance and identify growth trends.
    3 years of historical data is provided.
    Use this data to measure economic performance and and it's impact on company's({ticker}) stock.
    
    Input paramter:
    - name(type:str): The name of economic indicator.(e.g, federalFunds,CPI,inflationRate, totalNonfarmPayroll, unemploymentRate,realGDP,consumerSentiment, retailSales,industrialProductionTotalIndex, initialClaims, inflation)
    """

    # Set from_date to 3 years ago from today with format 'YYYY-MM-DD'
    from_date = (datetime.now() - timedelta(days=3*365)).strftime('%Y-%m-%d')
    params = {
        "name": name,
        "from": from_date
    }
    return make_fmp_api_request("economic-indicators", params)