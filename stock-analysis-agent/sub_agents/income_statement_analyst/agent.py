from google.adk.agents import LlmAgent
from google.adk.tools import google_search
from .tools.fmp_income_statement import fmp_income_statement
from ..utils.llm_model import lite_llm_model
from google.genai import types
from google.adk.planners import BuiltInPlanner


income_statement_agent = LlmAgent(
    name = "income_statement_agent",
    model = lite_llm_model(),
    description = "You are a specialist in income statement analysis, focusing on revenue, expenses, and net income to assess a company's earning power.",
    instruction = """
    [description]
    손익계산서 도구를 사용하여 회사의 손익계산서를 분석하세요.
    가장 최근 데이터를 얻기 위해 period='quarter' 및 period='annual' 매개변수를 사용하세요.
    수익, 비용, 순이익 및 수익성 추세에 초점을 맞추세요.

    [Expected Output]
    손익계산서에 대한 상세한 분석을 제공하세요.
    분기 및 연간 데이터를 포함하세요.
    FACT 및 OPINION 섹션으로 분리하세요.
    Markdown 형식을 사용하세요.
    """,
    tools = [fmp_income_statement],
    output_key = "income_statement_result",
    planner=BuiltInPlanner(
        thinking_config=types.ThinkingConfig(
            include_thoughts=True,
            thinking_budget=1024,
        )
    )
)
