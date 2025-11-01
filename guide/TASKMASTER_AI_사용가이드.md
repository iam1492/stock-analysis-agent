# TaskMaster AI 사용 가이드 - 호출 실패 방지

## 📋 목차
1. [주요 실패 원인 및 해결책](#1-주요-실패-원인-및-해결책)
2. [올바른 사용 패턴](#2-올바른-사용-패턴)
3. [필수 파라미터](#3-필수-파라미터)
4. [절대 피해야 할 것들](#4-절대-피해야-할-것들)
5. [단계별 사용 예시](#5-단계별-사용-예시)
6. [문제 해결 체크리스트](#6-문제-해결-체크리스트)

---

## 1. 주요 실패 원인 및 해결책

### 🚨 JSON 형식 에러 (가장 자주 발생)

**❌ 실패하는 형식:**
```json
{"projectRoot":"c:/Users/ramus/project/adk/stock-analysis","skipInstall":false,"addAliases":true,"initGit":true,"storeTasksInGit":true,"yes":true}
```

**✅ 올바른 형식:**
```json
{"projectRoot": "c:/Users/ramus/project/adk/stock-analysis", "yes": true}
```

**핵심 포인트:**
- 파라미터 사이에 공백 추가
- 불필요한 파라미터 제거
- JSON 형식 준수

---

## 2. 올바른 사용 패턴

### ✅ 성공하는 호출 예시

**프로젝트 초기화:**
```json
{"projectRoot": "c:/Users/ramus/project/adk/stock-analysis", "yes": true}
```

**작업 목록 조회:**
```json
{"projectRoot": "c:/Users/ramus/project/adk/stock-analysis"}
```

**다음 작업 조회:**
```json
{"projectRoot": "c:/Users/ramus/project/adk/stock-analysis"}
```

---

## 3. 필수 파라미터

### `projectRoot`
- **필수**: 프로젝트 루트 디렉토리의 **절대 경로**
- 예: `"c:/Users/ramus/project/adk/stock-analysis"`

### `yes`
- **선택사항**: 자동 yes/no 응답
- 값: `true` (자동 승인 활성화)

---

## 4. 절대 피해야 할 것들

### ❌ 불필요한 파라미터 제거
```json
// 이 것들은 사용하지 마세요
{
  "skipInstall": false,    // 제거
  "addAliases": true,      // 제거  
  "initGit": true,         // 제거
  "storeTasksInGit": true, // 제거
  "line_count": 1          // 잘못된 파라미터!
}
```

### ❌ 잘못된 JSON 형식
```json
// 공백 없이 연속된 문자열
{"projectRoot":"경로","yes":true}

// 불완전한 JSON
{"projectRoot": "경로"

// 잘못된 값 타입
{"projectRoot": 123, "yes": "yes"}
```

---

## 5. 단계별 사용 예시

### 5.1 프로젝트 초기화
```json
{"projectRoot": "c:/Users/ramus/project/adk/stock-analysis", "yes": true}
```
**결과**: 
- `.taskmaster/` 폴더 생성
- 기본 설정 파일 생성
- 현재 태그: `docker-deployment`

### 5.2 PRD 파일 생성 및 작업 생성
1. `.taskmaster/docs/prd.txt` 파일 생성
2. 작업 생성 실행:
```json
{
  "projectRoot": "c:/Users/ramus/project/adk/stock-analysis",
  "input": ".taskmaster/docs/prd.txt"
}
```

### 5.3 작업 관리
```json
{"projectRoot": "c:/Users/ramus/project/adk/stock-analysis"}
```

---

## 6. 문제 해결 체크리스트

### 🔍 호출 전 확인사항
- [ ] `projectRoot`가 절대 경로로 설정되었는가?
- [ ] JSON 형식이 올바른가?
- [ ] 불필요한 파라미터가 제거되었는가?

### 🛠️ 실패 시 대처법
1. **JSON 형식 확인**: 파라미터 사이에 공백 있는지 확인
2. **필수 파라미터 확인**: `projectRoot`만 필수
3. **경로 확인**: 절대 경로로 설정되어 있는지 확인

### ✅ 성공 증상
- `Project initialized successfully.` 메시지 확인
- `.taskmaster/` 폴더 생성 확인
- 태그 목록 확인 가능

---

## 📝 메모

### 현재 프로젝트 상태
- **태그**: docker-deployment (기본)
- **사용 가능한 태그**: master, database-integration, telemetry-fix, stock-symbol-removal, docker-deployment
- **버전**: TaskMaster AI v0.30.2

### 파일 구조 (생성 후)
```
project-root/
├── .taskmaster/
│   ├── config.json          # 설정 파일
│   ├── tasks/               # 작업 파일들
│   └── docs/
│       └── prd.txt          # PRD 파일
```

---

## 🎯 요약

1. **JSON 형식 준수**: 파라미터 사이 공백 필수
2. **필수 파라미터만 사용**: `projectRoot`만 필수
3. **절대 경로 사용**: `projectRoot`는 절대 경로
4. **단순하게**: 불필요한 옵션 제거

이 가이드를 따르면 taskmaster-ai 호출이 **언제나 성공**합니다! 🚀