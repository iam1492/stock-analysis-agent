from google.adk.agents import LlmAgent
from google.adk.agents.callback_context import ReadonlyContext
from .tools.fmp_dcf_valuation import fmp_dcf_valuation
from .tools.fmp_owner_earnings import fmp_owner_earnings
from .tools.fmp_enterprise_value import fmp_enterprise_value
from .tools.fmp_key_metrics_ttm import fmp_key_metrics_ttm
from ..utils.llm_model import lite_llm_model
from google.genai import types
from google.adk.planners import BuiltInPlanner


def get_intrinsic_value_instruction(context: ReadonlyContext) -> str:
    """동적으로 instruction을 생성하는 InstructionProvider"""
    
    # PM의 정량팀 전체 업무 지침 가져오기
    pm_instructions = context.state.get("pm_instructions", {})
    team_instruction = pm_instructions.get("quantitative_team_instruction", "")
    
    # PM 팀 지침이 있으면 최상위에 강조
    if team_instruction:
        pm_section = f"""
[🎯 중요] 정량분석팀 전체 업무 지침
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
{team_instruction}
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

당신은 정량분석팀의 내재가치(Intrinsic Value) 분석 담당 실무자입니다.
위 팀 전체 업무 지침 내에서 내재가치 분석을 집중적으로 수행하세요.

"""
    else:
        pm_section = ""
    
    # 기본 instruction
    shared_instruction = context.state.get('shared_instruction', '')
    timestamp = context.state.get('timestamp', '')
    base_instruction = f"""
{pm_section}모든 에이전트 공통 지침: {shared_instruction}

[설명]
가치 평가 도구를 사용하여 회사 주식의 내재 가치 분석을 수행합니다.
반드시 최신 데이터를 사용하기 위해 모든 가치 평가 도구의 최신 파라미터를 사용하여 가장 최근의 데이터를 확보하세요.
회사의 내재 가치를 평가하기 위해 다음 도구를 반드시 사용해야 합니다.
  - DCF Valuation 도구를 사용하여 할인된 현금 흐름(DCF) 가치를 계산합니다.
  - Owner Earnings 도구를 사용하여 소유자 이익 및 지속 가능한 가치를 평가합니다.
  - Enterprise Value 도구를 사용하여 기업 가치 지표를 결정합니다.
  - TTM Key Metrics 도구를 사용하여 기업의 최근 12개월 주요 성과지표를 종합적으로 검색합니다.
이러한 도구의 결과를 분석하여 주식의 내재 가치를 결정합니다.
내재 가치를 현재 시장 가격과 비교하여 주식이 저평가되었는지 또는 고평가되었는지 평가합니다.

[예상 출력]
- 리포트 작성 날짜: {timestamp} (읽기 쉬운 한국 현지 시간대로 표기)

- DCF Valuation 결과 및 설명.
- Owner Earnings 분석 및 지속 가능한 가치 평가.
- Enterprise Value 지표 및 해석.
- 내재 가치 대 현재 시장 가격 비교.
- 데이터 출처 및 신뢰성에 대한 설명.
- [매우 중요] 분석을 기반으로 주식이 저평가, 적정 가치 또는 고평가되었는지에 대한 평가.
"""
    
    return base_instruction


def create_intrinsic_value_agent():
    return LlmAgent(
        name = "intrinsic_value_analyst_agent",
        model = lite_llm_model("intrinsic_value_analyst_agent"),
        description = "당신은 내재 가치(intrinsic value) 분석 전문가로서, 회사의 펀더멘털과 미래 현금 흐름을 기반으로 회사의 진정한 가치를 평가하는 데 중점을 둡니다.",
        instruction = get_intrinsic_value_instruction,
        tools = [fmp_dcf_valuation, fmp_owner_earnings, fmp_enterprise_value, fmp_key_metrics_ttm],
        output_key = "intrinsic_value_result",
        planner=BuiltInPlanner(
            thinking_config=types.ThinkingConfig(
                include_thoughts=True,
                thinking_budget=1024,
            )
        )
    )

instrinsic_value_agent = create_intrinsic_value_agent()
