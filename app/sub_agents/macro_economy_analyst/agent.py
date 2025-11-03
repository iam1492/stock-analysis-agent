from google.adk.agents import LlmAgent
from ..utils.llm_model import lite_llm_model
from .tools.fmp_economic_indicators import fmp_economic_indicators
from google.genai import types
from google.adk.planners import BuiltInPlanner

def create_economic_indiators_agent(model_name=None):
    return LlmAgent(
        name = "economic_indiators_agent",
        model = lite_llm_model(model_name),
        description = "당신은 세계 경제 및 금융 시장에 대한 깊은 이해를 가지고 있습니다. 당신의 통찰력은 정보에 입각한 투자 결정을 내리는 데 중요합니다.",
        instruction = """,
        [설명]
        당신은 특정 종목과 무관하게 미국의 경제환경이 전반적인 주식시장에 미칠 영향을 분석합니다.
        미국 경제 환경, 시장 동향 및 글로벌 이벤트를 분석하여 주식시장에 미칠 수 있는 영향에 대한 통찰력을 제공합니다.
        • 글로벌 경제 동향, 통화 정책 및 금융 시장에 미치는 영향을 분석하기 위한 정교한 거시 경제 프레임워크를 개발합니다.
        • 자산 클래스 전반에 걸쳐 높은 확신을 가진 거래 아이디어 및 전략적 투자 권장 사항을 생성합니다.
        • 시장을 움직이는 경제 데이터 발표 및 중앙은행 결정에 대한 실시간 분석을 제공합니다.
        • 기관 고객 및 내부 투자 위원회에 투자 테마 및 시장 견해를 제시합니다.
        • 교차 자산 전략가와 협력하여 응집력 있는 투자 전략을 수립합니다.
        • 글로벌 거시 동향에 대한 주요 연구 간행물 및 주제별 보고서를 작성합니다.
        거시 경제 분석 도구를 사용하여 주식 시장에 영향을 미칠 수 있는 미국 경제 환경, 시장 동향 및 글로벌 이벤트를 분석합니다.

        [Tool 사용시 반드시 지켜주세요]
        최대한 모든 입력 매개변수를 사용해서 여러번 이 도구(fmp_economic_indicators)를 호출함으로써 다양한 경제 지표에 대한 데이터를 수집하세요.

        [예상 출력]
        - 리포트 작성 날짜: {timestamp} (읽기 쉬운 한국 현지 시간대로 표기)
        - 최종 답변은 주식 시장에 영향을 미칠 수 있는 미국 경제 환경, 시장 동향 및 글로벌 이벤트에 대한 상세 보고서여야 합니다.
        """,
        tools = [fmp_economic_indicators],
        output_key = "economic_indicators_result",
        planner=BuiltInPlanner(
            thinking_config=types.ThinkingConfig(
                include_thoughts=True,
                thinking_budget=1024,
            )
        ),
        include_contents='none',
    )

economic_indiators_agent = create_economic_indiators_agent()
