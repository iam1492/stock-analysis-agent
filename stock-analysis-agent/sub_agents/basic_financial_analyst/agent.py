from google.adk.agents import LlmAgent
from .tools.fmp_key_metrics import fmp_key_metrics
from .tools.fmp_financial_ratios import fmp_financial_ratios

basic_financial_analyst_agent = LlmAgent(
    name = "basic_financial_analyst_agent",
    model = "gemini-2.0-flash",
    description = "You are a specialist in financial metrics and ratios, using key indicators and ratios to evaluate company valuation, efficiency, and overall financial health.",
    instruction = """
    [Description]
    Analyze the company's key metrics and financial ratios using the fmp_key_metrics and fmp_financial_ratios tools.
    Obtain key financial metrics and financial ratios.
    Evaluate valuation, efficiency, and overall performance.

    [Expected Output]
    Provide a detailed analysis of key metrics and financial ratios.
    Separate into FACT and OPINION sections.
    Use Markdown format.
    """,
    tools = [fmp_key_metrics, fmp_financial_ratios],
    output_key = "basic_financial_analyst_result"
)
