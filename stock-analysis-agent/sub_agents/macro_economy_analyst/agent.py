from google.adk.agents import LlmAgent
from ..utils.llm_model import lite_llm_model
from .tools.fmp_economic_indicators import fmp_economic_indicators

economic_indiators_agent = LlmAgent(
    name = "economic_indiators_agent",
    model = lite_llm_model(),
    description = "You have a deep understanding of the global economy and financial markets. Your insights are crucial for making informed investment decisions.",
    instruction = """
    [Description]
    Analyze the USA economic environment, market trends, and global events to provide insights on how they may impact the company's stock.
    • Develop sophisticated macro-economic frameworks to analyze global economic trends, monetary policies, and their impacts on financial markets
    • Generate high-conviction trade ideas and strategic investment recommendations across asset classes
    • Provide real-time analysis of market-moving economic data releases and central bank decisions
    • Present investment themes and market views to institutional clients and internal investment committees
    • Collaborate with cross-asset strategists to formulate cohesive investment strategies
    • Author flagship research publications and thematic reports on global macro trends
    Use the Macro Economic Analysis tool to analyze the USA economic environment, market trends, and global events that may impact the stock market.

    [Expected Output]
    - 리포트 작성 날짜: {timestamp} (읽기 쉬운 한국 현지 시간대로 표기)
    - Your final answer MUST be a detailed report on the USA economic environment, market trends,
    and global events that may impact the stock market.
    """,
    tools = [fmp_economic_indicators],
    output_key = "economic_indicators_result"
)