from google.adk.agents import LlmAgent
from ..utils.llm_model import lite_llm_model

senior_quantitative_advisor_agent = LlmAgent(
    name = "senior_quantitative_advisor",
    model = lite_llm_model(),
    description = "You are leading expert in quantitative financial analysis",
    instruction = """
    [Description]
    Synthesize the analyses from:
    
    **Growth Analysis**
    {growth_analyst_result}
    
    **Intrinsic Value Analysis**
    {intrinsic_value_result}
    
    And provide a comprehensive assessment of the company's current Intrincis Value and Growth potential with Grow Rank Score.
    
    [Expected Output]
    Your final report MUST be a comprehensive analysis of company's Valuation and Growth potential.
    Include detailed reports on Intrinsic Value Analysis and Growth Analysis.
    Hedge fund manager will use your report to make investment decisions.
    Separate your report into FACT and OPINION sections.
    Use Markdown format for optimal readability.
    """,
    
    output_key = "senior_quantitative_advisor_result"
)
