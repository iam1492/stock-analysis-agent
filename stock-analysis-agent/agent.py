from google.adk.agents import ParallelAgent, SequentialAgent
from .sub_agents.balance_sheet_analyst import balance_sheet_agent
from .sub_agents.income_statement_analyst import income_statement_agent
from .sub_agents.cash_flow_analyst import cash_flow_statement_agent
from .sub_agents.stock_researcher import stock_researcher_agent
from .sub_agents.hedge_fund_manager import hadge_fund_manager_agent
from .sub_agents.senior_financial_advisor import senior_financial_advisor_agent
from .sub_agents.basic_financial_analyst import basic_financial_analyst_agent

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

stock_analysis_department = ParallelAgent(
    name = "stock_analysis_department",
    description = "주식 리서치, 재무팀 분석을 병렬적으로 수행하는 에이전트 입니다.",
    sub_agents = [stock_researcher_agent, financial_team]
)

stock_analysis_company = SequentialAgent(
    name = "root_agent",
    description = "여러 서브 에이전트의 결과를 종합하여 최종 투자 권고안을 작성하는 에이전트 입니다.",
    sub_agents = [stock_analysis_department, hadge_fund_manager_agent]
)

root_agent = stock_analysis_company