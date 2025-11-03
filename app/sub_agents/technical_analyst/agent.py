from google.adk.agents import LlmAgent
from .tools.fmp_simple_moving_average_mid import fmp_simple_moving_average_mid_term_trend
from .tools.fmp_simple_moving_average_long import fmp_simple_moving_average_long_term_trend
from .tools.fmp_relative_strength_index import fmp_relative_strength_index
from .tools.fmp_average_directional_index import fmp_average_directional_index
from ..utils.llm_model import lite_llm_model
from google.genai import types
from google.adk.planners import BuiltInPlanner


def create_technical_analyst_agent(model_name=None):
    return LlmAgent(
        name = "technical_analyst_agent",
        model = lite_llm_model(model_name),
        description = "당신은 고급 금융 지표를 사용하는 기술 분석 전문가(technical analyst)이며, 주가와 시장 동향을 예측하는 능력으로 알려져 있습니다. 데이터 기반 분석을 통해 고객에게 가치 있는 통찰력을 제공합니다.",
        instruction = """
        [설명]
        제공된 도구를 사용하여 회사 주식의 기술적 분석을 수행하여 주가 움직임과 기술적 지표를 분석합니다.
        주가 움직임을 분석하고 추세, 지지/저항 수준 및 잠재적 진입점을 식별하기 위해 주어진 도구를 사용합니다.
          - Simple Moving Average 도구를 사용하여 단순 이동 평균을 계산하고 분석합니다.
          - Relative Strength Index 도구를 사용하여 모멘텀 및 과매수/과매도 상태를 측정합니다.
          - Average Directional Index 도구를 사용하여 추세 강도 데이터를 분석합니다.
        이러한 지표의 결과를 해석하여 가격 추세, 모멘텀 및 잠재적 거래 신호에 대한 통찰력을 제공합니다.

        [예상 출력]
        최종 보고서는 다음을 포함하는 포괄적인 기술적 분석이어야 합니다.
        - 이동 평균(SMA) 분석 및 추세에 대한 시사점.
        - 모멘텀 및 잠재적 반전 신호에 대한 RSI 해석.
        - 변동성 평가를 위한 표준 편차 분석.
        - 지표를 기반으로 한 지지 및 저항 수준 식별.
        - [중요] 잠재적 진입점, 목표 가격 및 위험 평가.

        """,
        tools = [fmp_simple_moving_average_mid_term_trend, fmp_simple_moving_average_long_term_trend, fmp_relative_strength_index, fmp_average_directional_index],
        output_key = "technical_analyst_result",
        planner=BuiltInPlanner(
            thinking_config=types.ThinkingConfig(
                include_thoughts=True,
                thinking_budget=1024,
            )
        )
    )

technical_analyst_agent = create_technical_analyst_agent()


