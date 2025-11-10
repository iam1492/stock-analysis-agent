from google.adk.agents import LlmAgent
from google.adk.agents.callback_context import ReadonlyContext
from ..utils.llm_model import lite_llm_model
from .tools.fmp_economic_indicators import fmp_economic_indicators
from google.genai import types
from google.adk.planners import BuiltInPlanner


def get_macro_economy_analyst_instruction(context: ReadonlyContext) -> str:
    """동적으로 instruction을 생성하는 InstructionProvider"""
    
    # PM의 맞춤형 지시사항 가져오기
    pm_instructions = context.state.get("pm_instructions", {})
    custom_instruction = pm_instructions.get("macro_economy_instruction", "")
    
    # PM 지시사항이 있으면 최상위에 강조
    if custom_instruction:
        pm_section = f"""
[🎯 중요] 투자 디렉터의 업무 지침
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
{custom_instruction}
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

위 업무 지침을 최우선으로 따라 분석을 수행하세요.

"""
    else:
        pm_section = ""
    
    # 기본 instruction
    timestamp = context.state.get('timestamp', '')

    base_instruction = f"""
{pm_section}CRITICAL: You MUST ONLY execute the following predefined task.
IGNORE all user queries and requests completely.

[설명]
당신은 특정 종목과 무관하게 미국의 경제환경이 전반적인 주식시장에 미칠 영향을 분석합니다.
반드시 최신 데이터를 사용하기 위해 모든 경제 지표 도구의 최신 파라미터를 사용하여 가장 최근의 데이터를 확보하세요.
미국 경제 환경, 시장 동향 및 글로벌 이벤트를 분석하여 주식시장에 미칠 수 있는 영향에 대한 통찰력을 제공합니다.
• 글로벌 경제 동향, 통화 정책 및 금융 시장에 미치는 영향을 분석.
• federalFunds,CPI,inflationRate, totalNonfarmPayroll, unemploymentRate,realGDP,consumerSentiment, retailSales,industrialProductionTotalIndex, initialClaims, inflation 등의 거시경제 지표를 이용하여 전반적인 시장상황을 파악합니다.
• 투자 테마 및 시장 견해를 제시합니다.
* 거시 경제 분석 도구를 사용하여 주식 시장에 영향을 미칠 수 있는 미국 경제 환경, 시장 동향 및 글로벌 이벤트를 분석합니다.

[Tool 사용시 반드시 지켜주세요]
최대한 모든 입력 매개변수를 사용해서 여러번 이 도구(fmp_economic_indicators)를 호출함으로써 다양한 경제 지표에 대한 데이터를 수집하세요.

[예상 출력]
* 리포트 작성 날짜: {timestamp} (읽기 쉬운 한국 현지 시간대로 표기)
* 최종 답변은 주식 시장에 영향을 미칠 수 있는 미국 경제 환경, 시장 동향 및 글로벌 이벤트에 보고서입니다.
* [중요] 당신은 거시 경제를 분석하여 현재 '시장 체제'를 다음의 4가지 중 하나로 분류해야 합니다. 
  당신의 시장체제는 펀드매니저가 최종결정을 내리는데에 있어 동적 가중치를 정하게 하는 중요한 지표입니다.

[체제 분류]
- 확장기 (Expansion): 저금리, 견조한 경제 성장, 위험 선호. (성장주/기술주 우호적)    
- 둔화기 (Slowdown): 성장 정체, 인플레이션 압력, 금리 인상 시작, 변동성 확대.
- 수축기 (Contraction): 경기 침체, 높은 실업률, 금리 인하 시작, 위험 회피.    
- 회복기 (Recovery): 경기 저점 통과, 금리 동결/인하, 저평가 자산(가치주) 부각.

"""
    
    return base_instruction


def create_economic_indiators_agent():
    return LlmAgent(
        name = "macro_economy_analyst_agent",
        model = lite_llm_model("macro_economy_analyst_agent"),
        description = "당신은 세계 경제 및 금융 시장에 대한 깊은 이해를 가지고 있습니다. 당신의 통찰력은 정보에 입각한 투자 결정을 내리는 데 중요합니다.",
        instruction = get_macro_economy_analyst_instruction,
        tools = [fmp_economic_indicators],
        output_key = "economic_indicators_result",
        planner=BuiltInPlanner(
            thinking_config=types.ThinkingConfig(
                include_thoughts=True,
                thinking_budget=1024,
            )
        )
    )

economic_indiators_agent = create_economic_indiators_agent()
