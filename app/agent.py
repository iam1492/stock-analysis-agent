from google.adk.agents import ParallelAgent, SequentialAgent
from .sub_agents.balance_sheet_analyst.agent import create_balance_sheet_agent
from .sub_agents.income_statement_analyst.agent import create_income_statement_agent
from .sub_agents.cash_flow_analyst.agent import create_cash_flow_statement_agent
from .sub_agents.stock_researcher.agent import create_stock_researcher_agent
from .sub_agents.hedge_fund_manager.agent import create_hedge_fund_manager_agent
from .sub_agents.senior_financial_advisor.agent import create_senior_financial_advisor_agent
from .sub_agents.basic_financial_analyst.agent import create_basic_financial_analyst_agent
from .sub_agents.technical_analyst.agent import create_technical_analyst_agent
from .sub_agents.intrinsic_value_analyst.agent import create_intrinsic_value_agent
from .sub_agents.senior_quantitative_advisor.agent import create_senior_quantitative_advisor_agent
from .sub_agents.growth_analyst.agent import create_growth_analyst_agent
from .sub_agents.macro_economy_analyst.agent import create_economic_indiators_agent
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
    callback_context.state["model"] = None


def update_session_context(callback_context: CallbackContext, user_id: str, model: str = None):
    """
    Update session context with user and model information.
    This is called from the streaming handler when a new analysis starts.
    """
    callback_context.state["user_id"] = user_id
    callback_context.state["model"] = model
    print(f"📝 Updated session context: user_id={user_id}, model={model}")


# Note: Agent result saving is now handled through streaming detection
# rather than direct agent callbacks to avoid Pydantic validation issues

def create_fundamental_analysis_agents(model_name=None):
    return ParallelAgent(
        name = "parallel_financial_agent",
        description = "Balance Sheet, Income Statement, Cash Flow Statement분석을 병렬로 수행하는 에이전트 입니다.",
        sub_agents = [
            create_balance_sheet_agent(model_name),
            create_income_statement_agent(model_name),
            create_cash_flow_statement_agent(model_name),
            create_basic_financial_analyst_agent(model_name)
        ]
    )

fundamental_analysis_agents = create_fundamental_analysis_agents()

def create_financial_team(model_name=None):
    return SequentialAgent(
        name = "financial_team_agents",
        description = "재무 팀의 여러 에이전트를 순차적으로 실행하여 정보를 취합하는 에이전트 입니다.",
        sub_agents = [create_fundamental_analysis_agents(model_name), create_senior_financial_advisor_agent(model_name)]
    )

financial_team = create_financial_team()

def create_quantitative_analysis_agents(model_name=None):
    return ParallelAgent(
        name = "quantitative_analysis_agents",
        description = "내재 가치 분석과 성장성 분석을 병렬적으로 수행하는 에이전트 입니다.",
        sub_agents = [create_intrinsic_value_agent(model_name), create_growth_analyst_agent(model_name)]
    )

def create_quantitative_analysis_team(model_name=None):
    return SequentialAgent(
        name = "quantitative_analysis_team",
        description = "Quantitative Analysis 팀의 여러 에이전트를 순차적으로 실행하여 정보를 취합하는 에이전트 입니다.",
        sub_agents = [create_quantitative_analysis_agents(model_name), create_senior_quantitative_advisor_agent(model_name)]
    )

quantitative_analysis_agents = create_quantitative_analysis_agents()
quantitative_analysis_team = create_quantitative_analysis_team()

def create_stock_analysis_department(model_name=None):
    return ParallelAgent(
        name = "stock_analysis_department",
        description = "주식 리서치, 재무팀 분석, 기술적 분석, 정량적 분석 그리고 매크로경제분석을 병렬적으로 수행하는 에이전트 입니다.",
        sub_agents = [
            create_stock_researcher_agent(model_name),
            create_financial_team(model_name),
            create_technical_analyst_agent(model_name),
            create_quantitative_analysis_team(model_name),
            create_economic_indiators_agent(model_name)
        ]
    )

def create_stock_analysis_company(model_name=None):
    return SequentialAgent(
        name = "root_agent",
        description = "여러 서브 에이전트의 결과를 종합하여 최종 투자 권고안을 작성하는 에이전트 입니다.",
        sub_agents = [create_stock_analysis_department(model_name), create_hedge_fund_manager_agent(model_name)],
        before_agent_callback=set_session
    )

stock_analysis_department = create_stock_analysis_department()
stock_analysis_company = create_stock_analysis_company()

def create_root_agent(model_name=None):
    return create_stock_analysis_company(model_name)

# Default root agent (can be overridden dynamically)
root_agent = create_root_agent()