from google.adk.agents import LlmAgent
from google.adk.agents.callback_context import ReadonlyContext
from .tools.fmp_balance_sheet import fmp_balance_sheet
from ..utils.llm_model import lite_llm_model
from google.genai import types
from google.adk.planners import BuiltInPlanner


def get_balance_sheet_instruction(context: ReadonlyContext) -> str:
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

당신은 재무팀의 대차대조표(Balance Sheet) 분석 담당 실무자입니다.
위 팀 전체 업무 지침 내에서 대차대조표 분석을 집중적으로 수행하세요.

"""
    else:
        pm_section = ""
    
    # 기본 instruction
    shared_instruction = context.state.get('shared_instruction', '')
    base_instruction = f"""
{pm_section}모든 에이전트 공통 지침: {shared_instruction}

[Description]
Balance Sheet 도구를 사용하여 회사의 대차대조표를 분석하세요.
가장 최근 데이터를 얻기 위해 period='quarter' 및 period='annual' 매개변수를 사용하세요.
자산, 부채, 자본 및 재무 상태에 초점을 맞추세요.

[Expected Output]
대차대조표에 대한 상세한 분석을 제공하세요.
분기 및 연간 데이터를 포함하세요.
FACT 및 OPINION 섹션으로 분리하세요.
Markdown 형식을 사용하세요.
"""
    
    return base_instruction


def create_balance_sheet_agent():
    return LlmAgent(
        name = "balance_sheet_agent",
        model = lite_llm_model("balance_sheet_agent"),
        description = "당신은 재무팀에 소속되어 재무 안정성 및 레버리지를 결정하기 위해 자산, 부채, 자본을 검토하는 대차대조표 분석 전문가입니다.",
        instruction = get_balance_sheet_instruction,
        tools = [fmp_balance_sheet],
        planner=BuiltInPlanner(
            thinking_config=types.ThinkingConfig(
                include_thoughts=True,
                thinking_budget=1024,
            )
        ),
        output_key = "balance_sheet_result"
    )

balance_sheet_agent = create_balance_sheet_agent()
