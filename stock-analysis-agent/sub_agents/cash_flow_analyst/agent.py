from google.adk.agents import LlmAgent
from .tools.fmp_cash_flow_statement import fmp_cash_flow_statement
from ..utils.llm_model import lite_llm_model

cash_flow_statement_agent = LlmAgent(
    name = "cash_flow_statement_agent",
    model = lite_llm_model(),
    description = "당신은 현금 흐름 분석 전문가로서, 현금 유입 및 유출을 추적하여 운영 효율성과 재무 건전성을 평가합니다.",
    instruction = """
    [설명]
    현금 흐름표 도구(cash flow statement tool)를 사용하여 회사의 현금 흐름표를 분석합니다.
    period='quarter' 및 period='annual' 매개변수를 사용하여 최신 데이터를 가져옵니다.
    현금 유입, 유출 및 유동성에 중점을 둡니다.

    [예상 출력]
    현금 흐름표에 대한 상세한 분석을 제공합니다.
    분기별 및 연간 데이터를 포함합니다.
    사실(FACT) 및 의견(OPINION) 섹션으로 구분합니다.
    마크다운 형식을 사용합니다.
    """,
    tools = [fmp_cash_flow_statement],
    output_key = "cash_flow_statement_result"
)
