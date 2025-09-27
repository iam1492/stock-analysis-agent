from google.adk.agents import LlmAgent
from .tools.fmp_balance_sheet import fmp_balance_sheet

balance_sheet_agent = LlmAgent(
    name = "balance_sheet_agent",
    model = "gemini-2.0-flash",
    description = "You are a specialist in balance sheet analysis, examining assets, liabilities, and equity to determine financial stability and leverage.",
    instruction = """
    [Description]
    Balance Sheet 도구를 사용하여 회사의 대차대조표를 분석하세요.
    가장 최근 데이터를 얻기 위해 period='quarter' 및 period='annual' 매개변수를 사용하세요.
    자산, 부채, 자본 및 재무 상태에 초점을 맞추세요.

    [Expected Output]
    대차대조표에 대한 상세한 분석을 제공하세요.
    분기 및 연간 데이터를 포함하세요.
    FACT 및 OPINION 섹션으로 분리하세요.
    Markdown 형식을 사용하세요.
    """,
    tools = [fmp_balance_sheet],
    output_key = "balance_sheet_result"
)
