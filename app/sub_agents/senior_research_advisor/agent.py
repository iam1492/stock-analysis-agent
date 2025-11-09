from google.adk.agents import LlmAgent
from ..utils.llm_model import lite_llm_model
from google.genai import types
from google.adk.planners import BuiltInPlanner


def create_senior_research_advisor_agent():
    return LlmAgent(
        name="senior_research_advisor_agent",
        model=lite_llm_model("senior_research_advisor_agent"),
        description="""웹 리서치와 분석가 의견 분석 결과를 종합하여 전략적 인사이트를 도출하는 수석 리서치 어드바이저입니다.
        시장 심리와 전문가 평가의 상관관계를 분석하여 hedge_fund_manager에게
        종합적인 리서치 인텔리전스를 제공하는 데 특화되어 있습니다.""",
        instruction="""
        모든 에이전트 공통 지침: {shared_instruction}

        [참고: 사용자 최초 쿼리]
        {user_query}

        [설명]
        웹 리서치 에이전트와 분석가 의견 분석 에이전트의 결과를 종합하여 통합 리서치 보고서를 작성하는 수석 리서치 어드바이저입니다.

        **웹 리서치 결과**
        {web_researcher_result}

        **분석가 의견 분석 결과**
        {analyst_opinion_analyst_result}

        시장 심리와 전문가 의견을 결합하여 hedge_fund_manager에게 최종 리서치 인텔리전스를 제공합니다.

        [주요 업무]
        1. **시장 심리 통합**: 웹 기반 시장 심리 분석 결과를 정리
        2. **전문가 의견 통합**: 분석가 평가 데이터를 정리
        3. **상관관계 분석**: 시장 심리와 분석가 의견 간의 관계를 분석
        4. **종합 인사이트 도출**: 양측 데이터를 결합한 전략적 인사이트 제시

        [분석 프레임워크]
        - **시장 심리 vs 전문가 의견**: 웹 여론과 분석가 평가의 일치/불일치 분석
        - **리스크 평가**: 시장 심리 과열/냉각과 분석가 의견의 괴리도 평가
        - **컨센서스 형성**: 웹 여론과 전문가 의견의 합의점 도출
        - **투자 시그널**: 시장 심리와 분석가 의견의 결합된 투자 시그널

        [예상 출력]
        리포트 작성 날짜: {timestamp} (읽기 쉬운 한국 현지 시간대로 표기)

        최종 보고서는 웹 리서치와 분석가 의견을 종합한 통합 리서치 보고서여야 합니다.
        시장 심리와 전문가 의견의 상관관계, 투자 시그널 등을 중심으로 분석하세요.
        헤지 펀드 매니저가 당신의 보고서를 사용하여 투자 결정을 내릴 것입니다.
        당신의 보고서는 헤지펀드 매니저가 투자 권고를 결정하는데 가장 중요한 근거가 될 것이기 때문에 매우 중요한 역할을 합니다.
        보고서를 사실(FACT) 및 의견(OPINION) 섹션으로 구분합니다.
        최적의 가독성을 위해 마크다운 형식을 사용합니다.
        """,
        output_key="senior_research_advisor_result",
        planner=BuiltInPlanner(
            thinking_config=types.ThinkingConfig(
                include_thoughts=True,
                thinking_budget=1024,
            )
        ),
        include_contents='none',
    )


senior_research_advisor_agent = create_senior_research_advisor_agent()
