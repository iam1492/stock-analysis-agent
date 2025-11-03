from google.adk.agents import LlmAgent
from ..utils.llm_model import lite_llm_model
from google.genai import types
from google.adk.planners import BuiltInPlanner


def create_senior_quantitative_advisor_agent():
    return LlmAgent(
        name = "senior_quantitative_advisor_agent",
        model = lite_llm_model(),
        description = "당신은 정량적 재무 분석(quantitative financial analysis)의 선도적인 전문가입니다.",
        instruction = """
        [설명]
        다음 분석된 내용을 보고 정량적 재무 분석을 종합합니다.

        **성장 분석**
        {growth_analyst_result}

        **내재 가치 분석**
        {intrinsic_value_result}

        내재 가치를 현재 시장 가격과 비교하여 주식이 저평가되었는지 또는 고평가되었는지 평가합니다.
        성장 순위 점수(Grow Rank Score)를 포함한 성장 잠재력에 대한 포괄적인 평가를 제공합니다.

        [예상 출력]
        최종 보고서는 회사의 가치 평가 및 성장 잠재력에 대한 포괄적인 분석이어야 합니다.
        내재 가치 분석 및 성장 분석에 대한 상세 보고서를 포함합니다.
        헤지 펀드 매니저가 귀하의 보고서를 사용하여 투자 결정을 내릴 것입니다.
        보고서를 사실(FACT) 및 의견(OPINION) 섹션으로 구분합니다.
        최적의 가독성을 위해 마크다운 형식을 사용합니다.
        """,

        output_key = "senior_quantitative_advisor_result",
        planner=BuiltInPlanner(
            thinking_config=types.ThinkingConfig(
                include_thoughts=True,
                thinking_budget=1024,
            )
        )
    )

senior_quantitative_advisor_agent = create_senior_quantitative_advisor_agent()
