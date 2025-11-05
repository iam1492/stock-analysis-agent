from google.adk.agents import LlmAgent
from ..utils.llm_model import lite_llm_model
from google.genai import types
from google.adk.planners import BuiltInPlanner


def create_senior_financial_advisor_agent():
    return LlmAgent(
        name = "senior_financial_advisor_agent",
        model = lite_llm_model("senior_financial_advisor_agent"),
        description = "당신은 선임 재무 자문가이자 재무팀 리더로써, 전문적인 분석을 통합하여 회사의 재무 성과 및 건전성에 대한 전체적인 통찰력을 제공합니다.",
        instruction = """
        모든 에이전트 공통 지침: {shared_instruction}
        
        [설명]
        다음 분석을 보고 전반적인 재무 성과를 종합합니다.

        **손익 계산서**
        {income_statement_result}

        **대차 대조표**
        {balance_sheet_result}

        **현금 흐름표**
        {cash_flow_statement_result}

        **기본 재무 분석**
        {basic_financial_analyst_result}

        회사의 재무 건전성 및 성과에 대한 포괄적인 평가를 제공합니다.
        전문가가 다룬 모든 측면에 대한 상세 보고서를 포함합니다.

        [예상 출력]
        리포트 작성 날짜: {timestamp} (읽기 쉬운 한국 현지 시간대로 표기)

        최종 보고서는 전문가 보고서를 기반으로 한 회사의 재무 건전성에 대한 포괄적인 분석이어야 합니다.
        손익 계산서, 대차 대조표, 현금 흐름표, 주요 지표 및 재무 비율에 대한 상세 보고서를 포함합니다.
        헤지 펀드 매니저가 귀하의 보고서를 사용하여 투자 결정을 내릴 것입니다.
        보고서를 사실(FACT) 및 의견(OPINION) 섹션으로 구분합니다.
        최적의 가독성을 위해 마크다운 형식을 사용합니다.
        """,
        output_key = "senior_financial_advisor_result",
        planner=BuiltInPlanner(
            thinking_config=types.ThinkingConfig(
                include_thoughts=True,
                thinking_budget=1024,
            )
        )
    )

senior_financial_advisor_agent = create_senior_financial_advisor_agent()
