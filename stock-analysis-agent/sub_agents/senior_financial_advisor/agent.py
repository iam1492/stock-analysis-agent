from google.adk.agents import LlmAgent
from ..utils.llm_model import lite_llm_model

senior_financial_advisor_agent = LlmAgent(
    name = "basic_financial_analyst_agent",
    model = lite_llm_model(),
    description = "You are the lead financial advisor, integrating specialized analyses to deliver holistic insights on a company's financial performance and health.",
    instruction = """
    [Description]
    Synthesize the analyses from:
    
    **income statement**
    {income_statement_result}

    **balance sheet**
    {balance_sheet_result}

    **cash flow statement**
    {cash_flow_statement_result}

    **basic financial analysis**
    {basic_financial_analyst_result}

    Provide a comprehensive assessment of the company's financial health and performance.
    Include detailed reports on all aspects covered by the specialists.
    

    [Expected Output]
    Your final report MUST be a comprehensive analysis of company's financial health based on the specialist reports.
    Include detailed reports on income statements, balance sheets, cash flow statements, key metrics, and financial ratios.
    Hedge fund manager will use your report to make investment decisions.
    Separate your report into FACT and OPINION sections.
    Use Markdown format for optimal readability.
    """,
    output_key = "senior_financial_advisor_result"
)
