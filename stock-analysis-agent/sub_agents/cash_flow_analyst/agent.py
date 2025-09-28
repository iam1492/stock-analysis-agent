from google.adk.agents import LlmAgent
from .tools.fmp_cash_flow_statement import fmp_cash_flow_statement
from ..utils.llm_model import lite_llm_model

cash_flow_statement_agent = LlmAgent(
    name = "cash_flow_statement_agent",
    model = lite_llm_model(),
    description = "You are a specialist in cash flow analysis, tracking cash inflows and outflows to assess operational efficiency and financial health.",
    instruction = """
    [Description]
    Analyze the company's cash flow statements using the Cash Flow Statement tool.
    Use period='quarter' and period='annual' parameters to get the most recent data.
    Focus on cash inflows, outflows, and liquidity.

    [Expected Output]
    Provide a detailed analysis of the cash flow statements.
    Include quarterly and annual data.
    Separate into FACT and OPINION sections.
    Use Markdown format.
    """,
    tools = [fmp_cash_flow_statement],
    output_key = "cash_flow_statement_result"
)
