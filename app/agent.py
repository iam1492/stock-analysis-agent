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
from .sub_agents.project_manager.agent import create_project_manager_agent
from google.adk.agents.callback_context import CallbackContext
from .sub_agents.utils.firestore_config import FirestoreConfig
import uuid
import datetime
from zoneinfo import ZoneInfo


def set_session(callback_context: CallbackContext):
    """
    Sets a unique ID and timestamp in the callback context's state.
    This function is called before the main_loop_agent executes.
    Also loads shared instructions for all agents.
    """

    callback_context.state["unique_id"] = str(uuid.uuid4())
    callback_context.state["timestamp"] = datetime.datetime.now(
        ZoneInfo("UTC")
    ).isoformat()

    # Initialize agent result storage tracking
    callback_context.state["agent_results"] = {}
    callback_context.state["user_id"] = None
    
    # Load and cache shared instruction in session state
    shared_instruction = FirestoreConfig.get_shared_instruction()
    callback_context.state["shared_instruction"] = shared_instruction
    
    print(f"📝 Loaded shared instruction into session: {len(shared_instruction)} characters")


def update_session_context(callback_context: CallbackContext, user_id: str):
    """
    Update session context with user information.
    This is called from the streaming handler when a new analysis starts.
    """
    callback_context.state["user_id"] = user_id
    print(f"📝 Updated session context: user_id={user_id}")


# Note: Agent result saving is now handled through streaming detection
# rather than direct agent callbacks to avoid Pydantic validation issues

def create_fundamental_analysis_agents():
    return ParallelAgent(
        name = "parallel_financial_agent",
        description = "Balance Sheet, Income Statement, Cash Flow Statement분석을 병렬로 수행하는 에이전트 입니다.",
        sub_agents = [
            create_balance_sheet_agent(),
            create_income_statement_agent(),
            create_cash_flow_statement_agent(),
            create_basic_financial_analyst_agent()
        ]
    )

def create_financial_team():
    return SequentialAgent(
        name = "financial_team_agents",
        description = "재무 팀의 여러 에이전트를 순차적으로 실행하여 정보를 취합하는 에이전트 입니다.",
        sub_agents = [create_fundamental_analysis_agents(), create_senior_financial_advisor_agent()]
    )

def create_quantitative_analysis_agents():
    return ParallelAgent(
        name = "quantitative_analysis_agents",
        description = "내재 가치 분석과 성장성 분석을 병렬적으로 수행하는 에이전트 입니다.",
        sub_agents = [create_intrinsic_value_agent(), create_growth_analyst_agent()]
    )

def create_quantitative_analysis_team():
    return SequentialAgent(
        name = "quantitative_analysis_team",
        description = "Quantitative Analysis 팀의 여러 에이전트를 순차적으로 실행하여 정보를 취합하는 에이전트 입니다.",
        sub_agents = [create_quantitative_analysis_agents(), create_senior_quantitative_advisor_agent()]
    )

def create_stock_analysis_department():
    return ParallelAgent(
        name = "stock_analysis_department",
        description = "주식 리서치, 재무팀 분석, 기술적 분석, 정량적 분석 그리고 매크로경제분석을 병렬적으로 수행하는 에이전트 입니다.",
        sub_agents = [
            create_stock_researcher_agent(),
            create_financial_team(),
            create_technical_analyst_agent(),
            create_quantitative_analysis_team(),
            create_economic_indiators_agent()
        ]
    )

def create_stock_analysis_company():
    return SequentialAgent(
        name = "root_agent",
        description = "프로젝트 매니저가 업무를 분배하고, 여러 전문 에이전트가 분석을 수행한 후, 헤지펀드 매니저가 최종 투자 권고안을 작성하는 에이전트입니다.",
        sub_agents = [
            create_project_manager_agent(),
            create_stock_analysis_department(),
            create_hedge_fund_manager_agent()
        ],
        before_agent_callback=set_session
    )

def create_root_agent():
    return create_stock_analysis_company()

# Default root agent (can be overridden dynamically)
root_agent = create_root_agent()
