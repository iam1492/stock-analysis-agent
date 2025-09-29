from google.adk.agents import LlmAgent
from .tools.fmp_dcf_valuation import fmp_dcf_valuation
from .tools.fmp_owner_earnings import fmp_owner_earnings
from .tools.fmp_enterprise_value import fmp_enterprise_value
from ..utils.llm_model import lite_llm_model

instrinsic_value_agent = LlmAgent(
    name = "intrinsic_value_agent",
    model = lite_llm_model(),
    description = "당신은 내재 가치(intrinsic value) 분석 전문가로서, 회사의 펀더멘털과 미래 현금 흐름을 기반으로 회사의 진정한 가치를 평가하는 데 중점을 둡니다.",
    instruction = """
    [설명]
    가치 평가 도구를 사용하여 회사 주식의 내재 가치 분석을 수행합니다.
    회사의 내재 가치를 평가하기 위해 다음 도구를 반드시 사용해야 합니다.
      - DCF Valuation 도구를 사용하여 할인된 현금 흐름(DCF) 가치를 계산합니다.
      - Owner Earnings 도구를 사용하여 소유자 이익 및 지속 가능한 가치를 평가합니다.
      - Enterprise Value 도구를 사용하여 기업 가치 지표를 결정합니다.
    이러한 도구의 결과를 분석하여 주식의 내재 가치를 결정합니다.
    내재 가치를 현재 시장 가격과 비교하여 주식이 저평가되었는지 또는 고평가되었는지 평가합니다.

    [예상 출력]
    - 리포트 작성 날짜: {timestamp} (읽기 쉬운 한국 현지 시간대로 표기)
    
    - DCF Valuation 결과 및 설명.
    - Owner Earnings 분석 및 지속 가능한 가치 평가.
    - Enterprise Value 지표 및 해석.
    - 내재 가치 대 현재 시장 가격 비교.
    - 데이터 출처 및 신뢰성에 대한 설명.
    - [매우 중요] 분석을 기반으로 주식이 저평가, 적정 가치 또는 고평가되었는지에 대한 평가.
    """,
    tools = [fmp_dcf_valuation, fmp_owner_earnings, fmp_enterprise_value],
    output_key = "intrinsic_value_result"
)
