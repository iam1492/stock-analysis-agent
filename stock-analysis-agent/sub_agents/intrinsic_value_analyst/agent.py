from google.adk.agents import LlmAgent
from .tools.fmp_dcf_valuation import fmp_dcf_valuation
from .tools.fmp_owner_earnings import fmp_owner_earnings
from .tools.fmp_enterprise_value import fmp_enterprise_value
from ..utils.llm_model import lite_llm_model

instrinsic_value_agent = LlmAgent(
    name = "intrinsic_value_agent",
    model = lite_llm_model(),
    description = "You are an expert in intrinsic value analysis, focusing on evaluating a company's true worth based on its fundamentals and future cash flows.",
    instruction = """
    [Description]
    Perform intrinsic value analysis of the company's stock using advanced valuation tools.
    MUST use the following tools to evaluate the company's intrinsic value:
      - DCF Valuation tool to calculate the Discounted Cash Flow (DCF) valuation.
      - Owner Earnings tool to assess the owner's earnings and sustainable value.
      - Enterprise Value tool to determine the enterprise value metrics.
    Analyze the results from these tools to determine the intrinsic value of the stock.
    Compare the intrinsic value with the current market price to assess if the stock is undervalued or overvalued.

    [Expected Output]
    - 리포트 작성 날짜: {timestamp} (읽기 쉬운 한국 현지 시간대로 표기)
    
    - DCF Valuation result and explanation.
    - Owner Earnings analysis and sustainable value assessment.
    - Enterprise Value metrics and interpretation.
    - Comparison of intrinsic value vs. current market price.
    - Explanation of data sources and reliability.
    - [VERY IMPORTANT] Assessment of whether the stock appears undervalued, fairly valued, or overvalued based on the analysis.
    """,
    tools = [fmp_dcf_valuation, fmp_owner_earnings, fmp_enterprise_value],
    output_key = "intrinsic_value_result"
)
