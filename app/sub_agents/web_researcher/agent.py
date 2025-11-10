from google.adk.agents import LlmAgent
from google.adk.agents.callback_context import ReadonlyContext
from google.adk.tools.mcp_tool.mcp_toolset import McpToolset
from google.adk.tools.mcp_tool.mcp_session_manager import StdioConnectionParams
from mcp import StdioServerParameters
from .tools.fmp_stock_news import fmp_stock_news
from ..utils.llm_model import lite_llm_model
from google.genai import types
from google.adk.planners import BuiltInPlanner
from google.adk.tools.mcp_tool.mcp_session_manager import StreamableHTTPServerParams
import os


def get_web_researcher_instruction(context: ReadonlyContext) -> str:
    """동적으로 instruction을 생성하는 InstructionProvider"""

    # PM의 stock_researcher_instruction 가져오기
    pm_instructions = context.state.get("pm_instructions", {})
    stock_researcher_instruction = pm_instructions.get("stock_researcher_instruction", "")

    # 기본 instruction
    shared_instruction = context.state.get('shared_instruction', '')
    timestamp = context.state.get('timestamp', '')
    base_instruction = f"""
모든 에이전트 공통 지침: {shared_instruction}

[참고: 사용자 최초 쿼리]
{{user_query}}

[역할]
웹 기반 종합 리서치를 수행하는 전문 에이전트입니다.
인터넷 전체를 탐색하여 회사에 대한 최신 정보, 뉴스, 시장 심리, 여론 등을 수집하고 분석합니다.

**투자 디렉터의 업무 지침**
{stock_researcher_instruction}

[주요 업무]
1. **광범위한 웹 검색**: TAVILY 검색 도구를 활용하여 뉴스, 블로그, 보고서, 소셜 미디어 등 다양한 웹 콘텐츠를 탐색
1-1. Tavily MCP 툴은 Tavily의 AI 중심 검색, 추출, 크롤링 플랫폼에 연결합니다. 이 도구는 실시간 웹 검색을 수행하고, 웹페이지에서 특정 데이터를 지능적으로 추출하며, 웹사이트를 **크롤링(수집)**하거나 구조화된 맵을 생성할 수 있는 기능을 제공
2. **심층 콘텐츠 추출**: 특정 URL의 전체 콘텐츠를 추출하여 상세 분석
3. **시장 심리 분석**: 웹상의 여론, 토론, 리뷰 등을 분석하여 시장 심리를 파악
4. **FMP 뉴스 보완**: 기존 FMP 뉴스 API와 TAVILY를 조합하여 더 포괄적인 뉴스 커버리지 제공

[TAVILY 도구 활용 참고]
- 실시간 웹 검색 (Real-Time Web Search): 에이전트의 작업을 위해 최적화된 실시간 웹 검색을 수행하여 최신 정보를 얻습니다.
- 지능형 데이터 추출 (Intelligent Data Extraction): 전체 HTML을 파싱(분석)할 필요 없이 모든 웹 페이지에서 특정하고 정제된 데이터와 콘텐츠를 추출합니다.
- 웹사이트 탐색 (Website Exploration): 웹사이트를 자동으로 크롤링하여 콘텐츠를 탐색하거나 사이트의 레이아웃 및 페이지에 대한 구조화된 맵을 만듭니다.

[분석 포인트]
- 최신 뉴스 동향 및 시장 반응
- 투자자 커뮤니티의 의견과 토론
- 전문가 분석과 리뷰
- 경쟁사나 산업 전반의 뉴스
- 소셜 미디어와 포럼의 시장 심리

[💡 추천 사용 순서]
tavily-search → tavily-extract

[예상 출력]
리포트 작성 날짜: {timestamp} (읽기 쉬운 한국 현지 시간대로 표기)

최종 답변은 웹 기반 종합 리서치 결과를 상세히 요약한 보고서여야 합니다.
시장 심리, 여론 동향, 주요 뉴스 포인트 등을 중심으로 분석하세요.
senior_research_advisor가 이 보고서를 활용하여 hedge_fund_manager에게 제공할 것이므로
사실 기반의 객관적 분석에 집중하세요.
"""

    return base_instruction
    
def create_web_researcher_agent():
    tavily_api_key = os.environ.get("TAVILY_API_KEY")
    tavily_toolset = McpToolset(
        connection_params=StdioConnectionParams(
            server_params=StdioServerParameters(
                command="npx",
                args=[
                    "-y",
                    "tavily-mcp@latest",
                ],
                env={
                    "TAVILY_API_KEY": tavily_api_key,
                }
            ),
            timeout=30,
        ),
        tool_filter=['tavily-search', 'tavily-extract'] 
    )
        
    return LlmAgent(
        name="web_researcher_agent",
        model=lite_llm_model("web_researcher_agent"),
        description="""웹 전체를 탐색하여 종합적인 시장 리서치를 수행하는 전문 에이전트입니다.
        Tavily Mcp를 도구를 활용하여 뉴스, 블로그, 소셜 미디어, 보고서 등 다양한 웹 콘텐츠를 분석합니다.
        시장 심리, 여론 동향, 투자자 의견 등을 심층적으로 파악하는 데 특화되어 있습니다.""",
        instruction=get_web_researcher_instruction,
        tools=[fmp_stock_news, tavily_toolset],
        output_key="web_researcher_result",
        planner=BuiltInPlanner(
            thinking_config=types.ThinkingConfig(
                include_thoughts=True,
                thinking_budget=1024,
            )
        )
    )

web_researcher_agent = create_web_researcher_agent()