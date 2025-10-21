from google.adk.agents import ParallelAgent, SequentialAgent
from .sub_agents.balance_sheet_analyst import balance_sheet_agent
from .sub_agents.income_statement_analyst import income_statement_agent
from .sub_agents.cash_flow_analyst import cash_flow_statement_agent
from .sub_agents.stock_researcher import stock_researcher_agent
from .sub_agents.hedge_fund_manager import hadge_fund_manager_agent
from .sub_agents.senior_financial_advisor import senior_financial_advisor_agent
from .sub_agents.basic_financial_analyst import basic_financial_analyst_agent
from .sub_agents.technical_analyst import technical_analyst_agent
from .sub_agents.intrinsic_value_analyst import instrinsic_value_agent
from .sub_agents.senior_quantitative_advisor import senior_quantitative_advisor_agent
from .sub_agents.growth_analyst import growth_analyst_agent
from .sub_agents.macro_economy_analyst import economic_indiators_agent
from google.adk.agents.callback_context import CallbackContext
import uuid
import datetime
from zoneinfo import ZoneInfo


def set_session(callback_context: CallbackContext):
    """
    Sets a unique ID and timestamp in the callback context's state.
    This function is called before the main_loop_agent executes.
    """

    callback_context.state["unique_id"] = str(uuid.uuid4())
    callback_context.state["timestamp"] = datetime.datetime.now(
        ZoneInfo("UTC")
    ).isoformat()

    # Initialize agent result storage tracking
    callback_context.state["agent_results"] = {}
    callback_context.state["user_id"] = None
    callback_context.state["stock_symbol"] = None


def update_session_context(callback_context: CallbackContext, user_id: str, stock_symbol: str):
    """
    Update session context with user and stock information.
    This is called from the streaming handler when a new analysis starts.
    """
    callback_context.state["user_id"] = user_id
    callback_context.state["stock_symbol"] = stock_symbol
    print(f"📝 Updated session context: user_id={user_id}, stock_symbol={stock_symbol}")


# Note: Agent result saving is now handled through streaming detection
# rather than direct agent callbacks to avoid Pydantic validation issues

fundamental_analysis_agents = ParallelAgent(
    name = "parallel_financial_agent",
    description = "Balance Sheet, Income Statement, Cash Flow Statement분석을 병렬로 수행하는 에이전트 입니다.",
    sub_agents = [balance_sheet_agent, income_statement_agent, cash_flow_statement_agent, basic_financial_analyst_agent]
)

financial_team = SequentialAgent(
    name = "financial_team_agents",
    description = "재무 팀의 여러 에이전트를 순차적으로 실행하여 정보를 취합하는 에이전트 입니다.",
    sub_agents = [fundamental_analysis_agents, senior_financial_advisor_agent]
)

quantitative_analysis_agents = ParallelAgent(
    name = "quantitative_analysis_agents",
    description = "내재 가치 분석과 성장성 분석을 병렬적으로 수행하는 에이전트 입니다.",
    sub_agents = [instrinsic_value_agent, growth_analyst_agent]  # Add intrinsic value analyst and growth analyst agents here when available
)

quantitative_analysis_team = SequentialAgent(
    name = "quantitative_analysis_team",
    description = "Quantitative Analysis 팀의 여러 에이전트를 순차적으로 실행하여 정보를 취합하는 에이전트 입니다.",
    sub_agents = [quantitative_analysis_agents, senior_quantitative_advisor_agent]
)

stock_analysis_department = ParallelAgent(
    name = "stock_analysis_department",
    description = "주식 리서치, 재무팀 분석, 기술적 분석, 정량적 분석 그리고 매크로경제분석을 병렬적으로 수행하는 에이전트 입니다.",
    sub_agents = [
        stock_researcher_agent,
        financial_team,
        technical_analyst_agent,
        quantitative_analysis_team,
        economic_indiators_agent
    ]
)

stock_analysis_company = SequentialAgent(
    name = "root_agent",
    description = "여러 서브 에이전트의 결과를 종합하여 최종 투자 권고안을 작성하는 에이전트 입니다.",
    sub_agents = [stock_analysis_department, hadge_fund_manager_agent],
    before_agent_callback=set_session
)

root_agent = stock_analysis_company