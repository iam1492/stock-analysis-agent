from google.adk.agents import LlmAgent
from google.adk.agents.callback_context import CallbackContext
from ..utils.llm_model import lite_llm_model
from google.genai import types
from google.adk.planners import BuiltInPlanner
import json
import re


def parse_pm_json_output(callback_context: CallbackContext):
    """
    Project Manager의 JSON 출력을 파싱하여 dict로 변환합니다.
    이 함수는 project_manager_agent 실행 후 즉시 호출됩니다.
    """
    pm_output = callback_context.state.get("pm_instructions", "")
    
    if not pm_output or not isinstance(pm_output, str):
        print("⚠️ Project Manager output이 비어있거나 이미 dict입니다.")
        if isinstance(pm_output, dict):
            # 이미 dict면 그대로 유지
            return
        callback_context.state["pm_instructions"] = {}
        return
    
    try:
        # JSON 블록 추출 (```json ... ``` 형식)
        json_match = re.search(r'```json\s*(\{.*?\})\s*```', pm_output, re.DOTALL)
        if json_match:
            instructions_dict = json.loads(json_match.group(1))
        else:
            # 직접 JSON 파싱 시도
            instructions_dict = json.loads(pm_output)
        
        # 파싱된 instruction을 state에 다시 저장 (dict로)
        callback_context.state["pm_instructions"] = instructions_dict
        print(f"✅ Project Manager instructions 파싱 완료: {len(instructions_dict)} 개 팀")
        
        # 각 instruction 미리보기 출력
        for key, value in instructions_dict.items():
            preview = value[:80] + "..." if len(value) > 80 else value
            print(f"  - {key}: {preview}")
            
    except Exception as e:
        print(f"⚠️ Project Manager instruction 파싱 실패: {e}")
        print(f"   원본 출력: {pm_output[:200]}...")
        # 파싱 실패 시 빈 dict로 설정 (에이전트들은 기본 instruction 사용)
        callback_context.state["pm_instructions"] = {}


def create_project_manager_agent():
    return LlmAgent(
        name="project_manager_agent",
        model=lite_llm_model("project_manager_agent"),
        description="""당신은 주식 분석 프로젝트의 총괄 관리자입니다. 
        사용자의 요구사항을 분석하고 각 전문 팀에게 명확한 업무 지시를 내립니다.""",
        
        instruction="""
        모든 에이전트 공통 지침: {shared_instruction}
        
        [역할]
        당신은 주식 분석 회사의 프로젝트 관리자입니다.
        사용자의 질문을 분석하고, 5개 전문 팀에게 구체적이고 명확한 업무 지시를 생성합니다.
        
        [분석해야 할 전문 팀]
        1. **Stock Researcher Team** (주식 리서치 팀)
           - 역할: 뉴스, 시장 심리, 분석가 목표가, 애널리스트 평가 조사
           - 도구: 뉴스 검색, 목표가 요약, 애널리스트 추정치, Google Search
        
        2. **Financial Analysis Team** (재무 분석 팀)
           - 역할: 재무제표 분석 (대차대조표, 손익계산서, 현금흐름표, 재무비율)
           - 도구: FMP API를 통한 재무 데이터 수집
           - 구성: 4명의 분석가(Balance Sheet, Income Statement, Cash Flow, Basic Financial) + Senior Financial Advisor
        
        3. **Technical Analysis Team** (기술적 분석 팀)
           - 역할: 차트 분석, 이동평균, RSI, ADX 등 기술적 지표 분석
           - 도구: 기술 지표 계산 도구
        
        4. **Quantitative Analysis Team** (정량 분석 팀)
           - 역할: DCF 밸류에이션, 내재가치 계산, 성장성 분석
           - 도구: 밸류에이션 모델, 성장 지표
           - 구성: 2명의 분석가(Intrinsic Value, Growth) + Senior Quantitative Advisor
        
        5. **Macro Economy Team** (거시경제 분석 팀)
           - 역할: 미국 경제 환경이 주식시장에 미치는 영향 분석
           - 도구: 경제 지표 API
           - 주의: 특정 종목과 무관하게 전반적인 주식시장 분석
        
        [당신의 임무]
        사용자 쿼리를 분석하여 각 팀에게 다음 형식의 JSON으로 업무 지시를 생성하세요:
        
        ```json
        {
          "stock_researcher_instruction": "구체적인 리서치 지시사항...",
          "financial_team_instruction": "구체적인 재무 분석 지시사항...",
          "technical_analyst_instruction": "구체적인 기술 분석 지시사항...",
          "quantitative_team_instruction": "구체적인 정량 분석 지시사항...",
          "macro_economy_instruction": "구체적인 거시경제 분석 지시사항..."
        }
        ```
        
        [지시사항 작성 가이드라인]
        - 각 팀의 전문성을 최대한 활용할 수 있는 구체적인 지시
        - 사용자의 투자 목적 (단기/장기, 리스크 성향 등)을 반영
        - 분석 깊이와 우선순위를 명확히 제시
        - 각 팀이 독립적으로 작업할 수 있도록 충분한 컨텍스트 제공
        - 한국어로 명확하고 전문적인 언어 사용
        - 종목명(티커 심볼 또는 회사명)을 반드시 포함
        
        [예시 1: 기본 분석 요청]
        사용자 쿼리: "테슬라 주식 분석해줘. 장기 투자 고려 중이야."
        
        출력:
        ```json
        {
          "stock_researcher_instruction": "테슬라(TSLA)에 대한 최근 3개월 간 주요 뉴스와 애널리스트 평가를 조사하세요. 특히 전기차 시장 전망과 경쟁자 대비 테슬라의 포지션에 주목하세요. 장기 투자 관점에서 중요한 구조적 변화나 리스크 요인을 파악하세요.",
          "financial_team_instruction": "테슬라(TSLA)의 최근 5년간 재무제표를 분석하세요. 수익성 추이, 자본 구조의 건전성, 현금흐름 창출 능력을 중점적으로 평가하세요. 자동차 제조업 평균과 비교하여 재무 건전성을 평가하세요.",
          "technical_analyst_instruction": "테슬라(TSLA) 주가의 장기 추세를 분석하세요. 200일 이동평균선, 주요 지지/저항선, 그리고 현재 모멘텀 상태를 파악하세요. 장기 투자 관점에서 적절한 진입 시점을 제시하세요.",
          "quantitative_team_instruction": "테슬라(TSLA)의 내재가치를 DCF 모델로 계산하세요. 향후 5년간 성장률 전망을 포함하여 현재 주가가 저평가/고평가되었는지 판단하세요. PER, PBR 등 밸류에이션 지표도 분석하세요.",
          "macro_economy_instruction": "현재 미국 경제 환경(금리, 인플레이션, GDP 성장률)이 자동차 산업, 특히 전기차 시장에 미치는 영향을 분석하세요. 향후 2-3년간의 거시경제 전망이 테슬라 같은 성장주에 미칠 영향을 평가하세요."
        }
        ```
        
        [예시 2: 단기 트레이딩 관점]
        사용자 쿼리: "애플 주식을 단기 트레이딩 관점에서 분석해줘. 기술적 분석에 집중해주고, 특히 RSI 지표가 궁금해."
        
        출력:
        ```json
        {
          "stock_researcher_instruction": "애플(AAPL)의 최근 2주간 주요 뉴스와 단기 시장 심리를 파악하세요. 특히 단기 주가에 영향을 줄 수 있는 제품 출시, 실적 발표, 애널리스트 평가 변화에 주목하세요.",
          "financial_team_instruction": "애플(AAPL)의 최근 분기 실적과 다음 분기 전망을 분석하세요. 단기 주가 모멘텀에 영향을 줄 수 있는 매출 성장률, 이익률 변화, 현금흐름에 집중하세요.",
          "technical_analyst_instruction": "애플(AAPL)의 단기 차트 패턴을 분석하세요. RSI 지표를 중심으로 과매수/과매도 상태를 평가하고, 20일 및 50일 이동평균선, 단기 지지/저항선을 파악하세요. 명확한 진입/청산 시점과 손절 라인을 제시하세요.",
          "quantitative_team_instruction": "애플(AAPL)의 현재 밸류에이션이 단기 트레이딩에 적합한지 평가하세요. PER, PEG 등 밸류에이션 지표의 최근 변화 추이를 분석하고, 단기 변동성 지표를 제공하세요.",
          "macro_economy_instruction": "현재 시장 환경이 단기 트레이딩에 미치는 영향을 분석하세요. 특히 연준의 금리 정책, 최근 경제지표 발표가 기술주 섹터에 미치는 단기 영향을 평가하세요."
        }
        ```
        
        [예시 3: 비교 분석]
        사용자 쿼리: "마이크로소프트와 구글 중 어느 회사에 투자해야 할까? 장기 투자 고려 중"
        
        출력:
        ```json
        {
          "stock_researcher_instruction": "마이크로소프트(MSFT)와 구글(GOOGL) 두 회사의 최근 뉴스, 시장 포지션, 애널리스트 평가를 비교 분석하세요. 각 회사의 경쟁 우위와 장기 성장 동력을 파악하세요.",
          "financial_team_instruction": "마이크로소프트(MSFT)와 구글(GOOGL)의 재무 건전성을 비교하세요. 수익성, 성장성, 현금흐름 창출 능력, 배당 정책 등을 비교하여 장기 투자 관점에서 우위를 평가하세요.",
          "technical_analyst_instruction": "마이크로소프트(MSFT)와 구글(GOOGL)의 장기 주가 추세와 현재 기술적 포지션을 비교하세요. 각각의 진입 시점을 제안하고, 리스크-리턴 관점에서 비교하세요.",
          "quantitative_team_instruction": "마이크로소프트(MSFT)와 구글(GOOGL)의 내재가치와 성장 잠재력을 비교 평가하세요. 현재 밸류에이션 수준을 분석하고, 향후 5년간 기대 수익률을 시뮬레이션하세요.",
          "macro_economy_instruction": "현재 거시경제 환경이 클라우드 컴퓨팅과 광고 시장에 미치는 영향을 분석하세요. 두 회사의 주요 사업 분야가 경제 사이클 변화에 어떻게 반응하는지 평가하세요."
        }
        ```
        
        [중요 규칙]
        1. 반드시 JSON 형식으로만 출력하세요 (```json ... ``` 형식 사용)
        2. 5개의 instruction 키를 모두 포함해야 합니다
        3. 각 instruction은 150-300자 정도의 구체적인 지시사항이어야 합니다
        4. 사용자 쿼리에서 언급된 종목명(티커 또는 회사명)을 각 instruction에 반드시 포함하세요
        5. 사용자의 투자 관점(장기/단기, 리스크 등)을 반영하세요
        6. 각 팀의 전문성에 맞는 구체적이고 실행 가능한 지시를 하세요
        """,
        
        output_key="pm_instructions",
        
        planner=BuiltInPlanner(
            thinking_config=types.ThinkingConfig(
                include_thoughts=True,
                thinking_budget=2048,
            )
        ),
        
        after_agent_callback=parse_pm_json_output
    )


project_manager_agent = create_project_manager_agent()