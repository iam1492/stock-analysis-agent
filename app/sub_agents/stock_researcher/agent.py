from google.adk.agents import LlmAgent
from google.adk.agents.callback_context import ReadonlyContext
from .tools.fmp_stock_news import fmt_stock_news
from .tools.fmp_price_target_summary import fmp_price_target_summary
from .tools.fmp_price_target_news import fmp_price_target_news
from .tools.fmp_historical_stock_grade import fmp_historical_stock_grade
from .tools.fmp_analyst_estimates import fmp_analyst_estimates
from google.adk.tools import google_search
from ..utils.llm_model import lite_llm_model
from google.genai import types
from google.adk.planners import BuiltInPlanner


def get_stock_researcher_instruction(context: ReadonlyContext) -> str:
    """동적으로 instruction을 생성하는 InstructionProvider"""
    
    # PM의 맞춤형 지시사항 가져오기
    pm_instructions = context.state.get("pm_instructions", {})
    custom_instruction = pm_instructions.get("stock_researcher_instruction", "")
    
    # 기본 instruction
    shared_instruction = context.state.get('shared_instruction', '')
    base_instruction = f"""
모든 에이전트 공통 지침: {shared_instruction}

[설명]
회사 주식을 둘러싼 최신 뉴스 및 시장 심리를 수집하고 분석합니다.
인터넷에서 회사에 대한 정보를 검색하고 최근 중요한 정보를 검색합니다.
fmt_stock_news 도구를 사용하여 회사에 대한 최신 뉴스 및 시장 심리를 얻습니다.
fmp_price_target_summary 도구를 사용하여 주식에 대한 여러 분석가의 목표 주가 요약을 얻습니다.
fmp_price_target_news 도구를 사용하여 주식에 대한 애널리스트들의 목표 주가 실시간 업데이트의 최신 정보를 얻습니다.
fmp_historical_stock_grade 도구를 사용하여 주식에 대한 애널리스트들의 특정 주식 종목에 대한 애널리스트들의 평가 변화를 이해합니다.
fmp_analyst_estimates 도구를 사용하여 주식에 대한 애널리스트들의 과거와 미래의 실적 추정치를 가져와 미래 기대치를 평가합니다.

[예상 출력]
최종 답변은 주식을 둘러싼 뉴스 및 시장 심리, 분석가들의 목표주가에 대한 상세한 요약이어야 합니다.
"""
    
    # PM 지시사항이 있으면 추가
    if custom_instruction:
        return f"""{base_instruction}

[프로젝트 매니저의 특별 지시사항]
{custom_instruction}

위 지시사항을 우선적으로 고려하여 분석을 수행하세요.
"""
    
    return base_instruction


def create_stock_researcher_agent():
    return LlmAgent(
        name = "stock_researcher_agent",
        model = lite_llm_model("stock_researcher_agent"),
        description = """당신은 다양한 출처에서 데이터를 수집하고 해석하는 데 능숙합니다.
        각 데이터 소스를 주의 깊게 읽고 가장 중요한 정보를 추출합니다.
        당신의 통찰력은 정보에 입각한 투자 결정을 내리는 데 중요합니다.""",
        instruction = get_stock_researcher_instruction,
        tools = [fmt_stock_news, fmp_price_target_summary, fmp_price_target_news, fmp_historical_stock_grade, fmp_analyst_estimates],
        output_key = "stock_researcher_result",
        planner=BuiltInPlanner(
            thinking_config=types.ThinkingConfig(
                include_thoughts=True,
                thinking_budget=1024,
            )
        )
    )

stock_researcher_agent = create_stock_researcher_agent()


