from google.adk.agents import LlmAgent
from .tools.fmp_stock_news import fmt_stock_news
from .tools.fmp_price_target_summary import fmp_price_target_summary
from google.adk.tools import google_search
from ..utils.llm_model import lite_llm_model

stock_researcher_agent = LlmAgent(
    name = "stock_researcher_agent",
    model = lite_llm_model(),
    description = """You're skilled in gathering and interpreting data from various sources. 
    You read each data source carefuly and extract the most important information.
    Your insights are crucial for making informed investment decisions.""",
    instruction = """
    [Description]
    Gather and analyze the latest news and market sentinment surrounding 
    company's stock. 
    Search information abount company from internet and retrieve recent important information.
    Use fmt_stock_news tool to get the latest news and market sentiment about company.
    Use fmp_price_target_summary tool to get analysts' price target summary for the stock.

    [Expected Output]
    Your final answer MUST be a detailed summary of the news and market sentiment surrounding the stock.
    """,
    tools = [fmt_stock_news, fmp_price_target_summary],
    output_key = "stock_researcher_result"
)
