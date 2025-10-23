from google.adk.agents import LlmAgent
from .tools.fmp_key_metrics import fmp_key_metrics
from .tools.fmp_financial_ratios import fmp_financial_ratios
from ..utils.llm_model import lite_llm_model
from google.genai import types
from google.adk.planners import BuiltInPlanner

def create_basic_financial_analyst_agent(model_name=None):
    return LlmAgent(
        name = "basic_financial_analyst_agent",
        model = lite_llm_model(model_name),
        description = "당신은 핵심 지표와 비율을 사용하여 회사 가치 평가, 효율성 및 전반적인 재무 건전성을 평가하는 재무 지표 및 비율 전문가입니다.",
        instruction = """
        [설명]
        fmp_key_metrics 및 fmp_financial_ratios 도구를 사용하여 회사의 주요 지표와 재무 비율을 분석합니다.
        핵심 재무 지표와 재무 비율을 확보합니다.
        가치 평가, 효율성 및 전반적인 성과를 평가합니다.

        [예상 출력]
        핵심 지표와 재무 비율에 대한 상세한 분석을 제공합니다.
        사실(FACT) 및 의견(OPINION) 섹션으로 구분합니다.
        마크다운 형식을 사용합니다.
        """,
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
