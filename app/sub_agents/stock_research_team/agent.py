from google.adk.agents import ParallelAgent, SequentialAgent
from ..web_researcher.agent import create_web_researcher_agent
from ..analyst_opinion_analyst.agent import create_analyst_opinion_analyst_agent
from ..senior_research_advisor.agent import create_senior_research_advisor_agent


def create_stock_research_team():
    """
    Stock Research Team: 웹 리서치와 분석가 의견 분석을 병렬로 수행한 후
    Senior Research Advisor가 결과를 종합하는 팀 구조
    """
    return SequentialAgent(
        name="stock_research_team",
        description="""웹 기반 리서치와 분석가 의견 분석을 병렬로 수행한 후
        결과를 종합하여 hedge_fund_manager에게 제공하는 리서치 팀입니다.""",
        sub_agents=[
            # 병렬 실행: 웹 리서치 + 분석가 의견 분석
            ParallelAgent(
                name="parallel_research_agents",
                description="웹 리서치와 분석가 의견 분석을 병렬로 수행하는 에이전트들",
                sub_agents=[
                    create_web_researcher_agent(),
                    create_analyst_opinion_analyst_agent()
                ]
            ),
            # 순차 실행: 결과 종합
            create_senior_research_advisor_agent()
        ]
    )


stock_research_team = create_stock_research_team()