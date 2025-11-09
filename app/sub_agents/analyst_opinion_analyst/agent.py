from google.adk.agents import LlmAgent
from google.adk.agents.callback_context import ReadonlyContext
from ..stock_researcher.tools.fmp_price_target_summary import fmp_price_target_summary
from ..stock_researcher.tools.fmp_price_target_news import fmp_price_target_news
from ..stock_researcher.tools.fmp_historical_stock_grade import fmp_historical_stock_grade
from ..stock_researcher.tools.fmp_analyst_estimates import fmp_analyst_estimates
from ..utils.llm_model import lite_llm_model
from google.genai import types
from google.adk.planners import BuiltInPlanner


def get_analyst_opinion_analyst_instruction(context: ReadonlyContext) -> str:
    """동적으로 instruction을 생성하는 InstructionProvider"""

    # PM의 stock_researcher_instruction 가져오기
    pm_instructions = context.state.get("pm_instructions", {})
    stock_researcher_instruction = pm_instructions.get("stock_researcher_instruction", "")

    # 기본 instruction
    shared_instruction = context.state.get('shared_instruction', '')
    timestamp = context.state.get('timestamp', '')
    base_instruction = f"""
모든 에이전트 공통 지침: {shared_instruction}

[참고: 사용자 최초 쿼리]
{{user_query}}

[역할]
전문 분석가들의 의견과 평가를 심층 분석하는 전문 에이전트입니다.
증권사 애널리스트들의 목표주가, 등급 변화, 실적 추정치 등을 종합적으로 분석합니다.

**투자 디렉터의 업무 지침**
{stock_researcher_instruction}

[주요 업무]
1. **목표주가 분석**: fmp_price_target_summary로 분석가들의 목표주가 요약을 분석
2. **목표주가 뉴스**: fmp_price_target_news로 실시간 목표주가 업데이트 뉴스를 추적
3. **등급 변화 추이**: fmp_historical_stock_grade로 분석가들의 등급 변화 패턴을 분석
4. **실적 추정치**: fmp_analyst_estimates로 과거와 미래 실적 추정치를 평가

[분석 포인트]
- 분석가들의 목표주가 분포와 평균값
- 목표주가 상향/하향 조정 패턴
- 분석가 등급 변화 추이 (BUY/HOLD/SELL)
- 실적 추정치의 정확성과 변동성
- 주요 증권사의 의견 변화
- 컨센서스(합의) 의견 형성

[예상 출력]
리포트 작성 날짜: {timestamp} (읽기 쉬운 한국 현지 시간대로 표기)

최종 답변은 분석가들의 전문 의견을 종합적으로 분석한 보고서여야 합니다.
목표주가, 등급 변화, 실적 추정 등을 중심으로 분석하세요.
senior_research_advisor가 이 보고서를 활용하여 hedge_fund_manager에게 제공할 것이므로
정량적 데이터 기반의 객관적 분석에 집중하세요.
"""

    return base_instruction


def create_analyst_opinion_analyst_agent():
    return LlmAgent(
        name="analyst_opinion_analyst_agent",
        model=lite_llm_model("analyst_opinion_analyst_agent"),
        description="""전문 증권사 애널리스트들의 의견과 평가를 심층 분석하는 전문 에이전트입니다.
        목표주가, 등급 변화, 실적 추정치 등의 정량적 데이터를 분석하여
        시장의 전문가 컨센서스를 파악하는 데 특화되어 있습니다.""",
        instruction=get_analyst_opinion_analyst_instruction,
        tools=[
            fmp_price_target_summary,
            fmp_price_target_news,
            fmp_historical_stock_grade,
            fmp_analyst_estimates
        ],
        output_key="analyst_opinion_analyst_result",
        planner=BuiltInPlanner(
            thinking_config=types.ThinkingConfig(
                include_thoughts=True,
                thinking_budget=1024,
            )
        )
    )


analyst_opinion_analyst_agent = create_analyst_opinion_analyst_agent()