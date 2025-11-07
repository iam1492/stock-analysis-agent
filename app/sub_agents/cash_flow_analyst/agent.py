from google.adk.agents import LlmAgent
from google.adk.agents.callback_context import ReadonlyContext
from .tools.fmp_cash_flow_statement import fmp_cash_flow_statement
from ..utils.llm_model import lite_llm_model
from google.genai import types
from google.adk.planners import BuiltInPlanner


def get_cash_flow_instruction(context: ReadonlyContext) -> str:
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

당신은 재무팀의 현금흐름표(Cash Flow Statement) 분석 담당 실무자입니다.
위 팀 전체 업무 지침 내에서 현금흐름표 분석을 집중적으로 수행하세요.

"""
    else:
        pm_section = ""
    
    # 기본 instruction
    shared_instruction = context.state.get('shared_instruction', '')
    base_instruction = f"""
{pm_section}모든 에이전트 공통 지침: {shared_instruction}

[설명]
현금 흐름표 도구(cash flow statement tool)를 사용하여 회사의 현금 흐름표를 분석합니다.
period='quarter' 및 period='annual' 매개변수를 사용하여 최신 데이터를 가져옵니다.
현금 유입, 유출 및 유동성에 중점을 둡니다.

[예상 출력]
현금 흐름표에 대한 상세한 분석을 제공합니다.
분기별 및 연간 데이터를 포함합니다.
사실(FACT) 및 의견(OPINION) 섹션으로 구분합니다.
마크다운 형식을 사용합니다.
"""
    
    return base_instruction


def create_cash_flow_statement_agent():
    return LlmAgent(
        name = "cash_flow_statement_agent",
        model = lite_llm_model("cash_flow_statement_agent"),
        description = "당신은 현금 흐름 분석 전문가로서, 현금 유입 및 유출을 추적하여 운영 효율성과 재무 건전성을 평가합니다.",
        instruction = get_cash_flow_instruction,
        tools = [fmp_cash_flow_statement],
        output_key = "cash_flow_statement_result",
        planner=BuiltInPlanner(
            thinking_config=types.ThinkingConfig(
                include_thoughts=True,
                thinking_budget=1024,
            )
        )
    )

cash_flow_statement_agent = create_cash_flow_statement_agent()
