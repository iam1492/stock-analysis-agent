# Project Manager Agent Integration Guide

## 개요

Stock Analysis Agent에 **Project Manager Agent**가 통합되었습니다. 이제 사용자 쿼리를 분석하여 각 전문 팀에게 맞춤형 업무 지시를 생성하고, 각 팀은 이 지시사항에 따라 분석을 수행합니다.

## 변경된 아키텍처

### Before (이전)
```
User Query → root_agent → stock_analysis_department (5개 팀 병렬) → hedge_fund_manager
```

### After (현재)
```
User Query → root_agent → project_manager_agent → stock_analysis_department (5개 팀 병렬, PM instruction 적용) → hedge_fund_manager
```

## 주요 변경사항

### 1. 새로 추가된 파일

- **`app/sub_agents/project_manager/__init__.py`**: Project Manager 모듈 초기화
- **`app/sub_agents/project_manager/agent.py`**: Project Manager Agent 구현

### 2. 수정된 파일

#### Agent 파일 (InstructionProvider 패턴 적용)
- `app/sub_agents/stock_researcher/agent.py`
- `app/sub_agents/technical_analyst/agent.py`
- `app/sub_agents/senior_financial_advisor/agent.py`
- `app/sub_agents/senior_quantitative_advisor/agent.py`
- `app/sub_agents/macro_economy_analyst/agent.py`

#### Root Agent
- `app/agent.py`: 
  - Project Manager import 추가
  - `parse_pm_instructions()` 함수 추가
  - `create_stock_analysis_company()` 구조 변경

## 동작 방식

### 1. Project Manager Agent

**역할**: 사용자 쿼리를 분석하여 5개 전문 팀에게 맞춤형 업무 지시 생성

**출력 형식** (JSON):
```json
{
  "stock_researcher_instruction": "구체적인 리서치 지시...",
  "financial_team_instruction": "구체적인 재무 분석 지시...",
  "technical_analyst_instruction": "구체적인 기술 분석 지시...",
  "quantitative_team_instruction": "구체적인 정량 분석 지시...",
  "macro_economy_instruction": "구체적인 거시경제 분석 지시..."
}
```

### 2. Session State를 통한 Communication

```python
# Project Manager가 생성
session.state["pm_instructions"] = {
    "stock_researcher_instruction": "...",
    # ...
}

# 각 전문 에이전트가 읽기
def get_instruction(context: ReadonlyContext) -> str:
    pm_inst = context.state.get("pm_instructions", {}).get("key", "")
    # PM instruction 적용
```

### 3. InstructionProvider 패턴

각 전문 에이전트는 이제 **동적 instruction 함수**를 사용합니다:

```python
def get_agent_instruction(context: ReadonlyContext) -> str:
    """동적으로 instruction을 생성"""
    pm_instructions = context.state.get("pm_instructions", {})
    custom_instruction = pm_instructions.get("agent_key", "")
    
    base_instruction = "기본 instruction..."
    
    if custom_instruction:
        return f"{base_instruction}\n\n[프로젝트 매니저 지시]\n{custom_instruction}"
    
    return base_instruction
```

## 테스트 방법

### 1. 기본 환경 설정

```bash
# Backend 실행
cd app
python -m adk api_server

# 또는 ADK Web UI 실행
python -m adk web
```

### 2. 테스트 시나리오

#### 시나리오 1: 기본 분석 요청
```
입력: "테슬라 주식 분석해줘. 장기 투자 고려 중이야."

검증 포인트:
✓ PM이 5개 팀별 instruction 생성
✓ 각 instruction에 "테슬라" 또는 "TSLA" 포함
✓ "장기 투자" 관점이 반영됨
✓ 각 팀이 PM instruction을 반영한 분석 수행
✓ 최종 hedge fund manager 리포트 생성
```

#### 시나리오 2: 단기 트레이딩 관점
```
입력: "애플 주식을 단기 트레이딩 관점에서 분석해줘. 기술적 분석에 집중해주고, 특히 RSI 지표가 궁금해."

검증 포인트:
✓ PM이 "단기 트레이딩" 관점 파악
✓ Technical Analyst에 RSI 중심 분석 지시
✓ Financial Team에 단기 지표 중심 지시
✓ 최종 리포트가 단기 관점 반영
```

#### 시나리오 3: 비교 분석
```
입력: "마이크로소프트와 구글 중 어느 회사에 투자해야 할까? 장기 투자 고려 중"

검증 포인트:
✓ PM이 두 회사 비교 분석 지시
✓ 각 팀이 두 회사에 대한 비교 수행
✓ 최종 추천이 명확하게 표시
```

### 3. 디버깅 및 확인

#### PM Instruction 확인
실행 중 콘솔에 다음과 같은 로그가 표시됩니다:

```
✅ Project Manager instructions 파싱 완료: 5 개 팀
  - stock_researcher_instruction: 테슬라(TSLA)에 대한 최근 3개월 간 주요 뉴스와 애널리스트 평가를 조사하세요...
  - financial_team_instruction: 테슬라(TSLA)의 최근 5년간 재무제표를 분석하세요...
  - technical_analyst_instruction: 테슬라(TSLA) 주가의 장기 추세를 분석하세요...
  - quantitative_team_instruction: 테슬라(TSLA)의 내재가치를 DCF 모델로 계산하세요...
  - macro_economy_instruction: 현재 미국 경제 환경이 자동차 산업에 미치는 영향을 분석하세요...
```

#### Activity Timeline 확인
ADK Web UI나 Frontend에서:
- Project Manager의 thinking 과정
- 각 전문 팀의 thinking 과정
- Tool 사용 내역

## 구성 파일

### Firestore Model Configuration

Project Manager도 다른 에이전트와 동일하게 Firestore에서 모델 설정을 가져옵니다:

```python
# Firestore collection: stock_agents
# Document: project_manager_agent
{
  "model_id": "gemini-2.5-flash",  # 또는 다른 모델
  "enabled": true
}
```

## 문제 해결

### PM Instruction 파싱 실패

**증상**: 
```
⚠️ Project Manager instruction 파싱 실패: ...
```

**원인**: PM이 JSON 형식이 아닌 텍스트를 출력함

**해결**:
1. PM의 instruction을 확인하여 JSON 형식 강제
2. 모델을 더 강력한 것으로 변경 (예: gemini-2.5-pro)
3. Thinking budget 증가 (현재: 2048)

### 에이전트가 PM Instruction을 무시

**증상**: 에이전트가 기본 instruction만 사용

**원인**: `session.state["pm_instructions"]`가 비어있거나 파싱 실패

**해결**:
1. `parse_pm_instructions()` 로그 확인
2. PM의 출력 확인
3. Session state 디버깅

### 성능 문제

**증상**: PM이 instruction 생성에 시간이 너무 오래 걸림

**해결**:
1. PM 모델을 더 빠른 것으로 변경 (gemini-2.5-flash)
2. Thinking budget 감소
3. Instruction template 간소화

## 향후 개선 사항

### 1. PM Instruction 검증
- JSON schema validation 추가
- Instruction 품질 검증 로직

### 2. Fallback 메커니즘 강화
- PM 실패 시 자동 재시도
- 기본 템플릿 활용

### 3. 사용자 피드백 반영
- PM instruction 표시 (UI)
- 사용자가 instruction 수정 가능

### 4. 메트릭 수집
- PM instruction 생성 시간
- 에이전트별 instruction 활용도
- 최종 리포트 품질 vs PM instruction 상관관계

## 참고 자료

- ADK Documentation: [https://github.com/google/adk-docs](https://github.com/google/adk-docs)
- InstructionProvider Pattern: ADK Docs - "Accessing State in Instructions"
- Session State Management: ADK Docs - "State and Memory"

## 지원

문제가 발생하면:
1. Backend 로그 확인
2. ADK Web UI에서 activity timeline 확인
3. Session state 디버깅
4. GitHub Issues에 보고