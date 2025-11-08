from google.adk.agents import LlmAgent
from google.adk.agents.callback_context import ReadonlyContext
from .tools.fmp_key_metrics import fmp_key_metrics
from .tools.fmp_financial_ratios import fmp_financial_ratios
from ..utils.llm_model import lite_llm_model
from google.genai import types
from google.adk.planners import BuiltInPlanner


def get_basic_financial_instruction(context: ReadonlyContext) -> str:
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

당신은 재무팀의 핵심 재무지표 및 비율 분석 담당 실무자입니다.
위 팀 전체 업무 지침 내에서 주요 재무 지표와 비율 분석을 집중적으로 수행하세요.

"""
    else:
        pm_section = ""
    
    # 기본 instruction
    shared_instruction = context.state.get('shared_instruction', '')
    timestamp = context.state.get('timestamp', '')
    base_instruction = f"""
{pm_section}모든 에이전트 공통 지침: {shared_instruction}

[설명]
fmp_key_metrics 및 fmp_financial_ratios 도구를 사용하여 회사의 주요 지표와 재무 비율을 분석합니다.
반드시 최신 데이터를 사용하기 위해 모든 도구의 최신 파라미터를 사용하여 가장 최근의 데이터를 확보하세요.
핵심 재무 지표와 재무 비율을 확보합니다.
가치 평가, 효율성 및 전반적인 성과를 평가합니다.

[예상 출력]
- 리포트 작성 날짜: {timestamp} (읽기 쉬운 한국 현지 시간대로 표기)
핵심 지표와 재무 비율에 대한 상세한 분석을 제공합니다.
사실(FACT) 및 의견(OPINION) 섹션으로 구분합니다.
마크다운 형식을 사용합니다.
"""
    
    return base_instruction


def create_basic_financial_analyst_agent():
    return LlmAgent(
        name = "basic_financial_analyst_agent",
        model = lite_llm_model("basic_financial_analyst_agent"),
        description = "당신은 핵심 지표와 비율을 사용하여 회사 가치 평가, 효율성 및 전반적인 재무 건전성을 평가하는 재무 지표 및 비율 전문가입니다.",
        instruction = get_basic_financial_instruction,
        tools = [fmp_key_metrics, fmp_financial_ratios],
        output_key = "basic_financial_analyst_result",
        planner=BuiltInPlanner(
            thinking_config=types.ThinkingConfig(
                include_thoughts=True,
                thinking_budget=1024,
            )
        )
    )

basic_financial_analyst_agent = create_basic_financial_analyst_agent()
