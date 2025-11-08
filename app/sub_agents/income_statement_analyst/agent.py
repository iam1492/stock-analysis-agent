from google.adk.agents import LlmAgent
from google.adk.agents.callback_context import ReadonlyContext
from google.adk.tools import google_search
from .tools.fmp_income_statement import fmp_income_statement
from ..utils.llm_model import lite_llm_model
from google.genai import types
from google.adk.planners import BuiltInPlanner


def get_income_statement_instruction(context: ReadonlyContext) -> str:
    """동적으로 instruction을 생성하는 InstructionProvider"""
    
    # PM의 재무팀 전체 업무 지침 가져오기
    pm_instructions = context.state.get("pm_instructions", {})
    team_instruction = pm_instructions.get("financial_team_instruction", "")
    
    # PM 팀 지침이 있으면 최상위에 강조
    if team_instruction:
        pm_section = f"""
[🎯 중요] 재무팀 전체 업무 지침
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
{team_instruction}
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

당신은 재무팀의 손익계산서(Income Statement) 분석 담당 실무자입니다.
위 팀 전체 업무 지침 내에서 손익계산서 분석을 집중적으로 수행하세요.

"""
    else:
        pm_section = ""
    
    # 기본 instruction
    shared_instruction = context.state.get('shared_instruction', '')
    timestamp = context.state.get('timestamp', '')
    base_instruction = f"""
{pm_section}모든 에이전트 공통 지침: {shared_instruction}

[description]
손익계산서 도구를 사용하여 회사의 손익계산서를 분석하세요.
반드시 최신 데이터를 사용하기 위해 period='quarter' 및 period='annual' 매개변수를 모두 사용하여 가장 최근의 데이터를 확보하세요.
수익, 비용, 순이익 및 수익성 추세에 초점을 맞추세요.

[Expected Output]
- 리포트 작성 날짜: {timestamp} (읽기 쉬운 한국 현지 시간대로 표기)
손익계산서에 대한 상세한 분석을 제공하세요.
분기 및 연간 데이터를 모두 포함하세요.
FACT 및 OPINION 섹션으로 분리하세요.
Markdown 형식을 사용하세요.
"""
    
    return base_instruction


def create_income_statement_agent():
    return LlmAgent(
        name = "income_statement_agent",
        model = lite_llm_model("income_statement_agent"),
        description = "You are a specialist in income statement analysis, focusing on revenue, expenses, and net income to assess a company's earning power.",
        instruction = get_income_statement_instruction,
        tools = [fmp_income_statement],
        output_key = "income_statement_result",
        planner=BuiltInPlanner(
            thinking_config=types.ThinkingConfig(
                include_thoughts=True,
                thinking_budget=1024,
            )
        )
    )

income_statement_agent = create_income_statement_agent()
