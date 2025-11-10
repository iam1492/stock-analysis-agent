# Current Context

## Current Project State

The Stock Analysis Agent is a **production-ready** web application that provides AI-powered stock analysis through a chat interface. The system is currently deployed and operational with a streamlined, cloud-agnostic architecture.

## Recent Work

### Hedge Fund Manager Decision Framework Enhancement (Latest)
- ✅ **6단계 체계적 의사결정 프로세스 구현**: 시장 체제 식별 → 동적 가중치 적용 → 주식 유형 판단 → 점수화 → 안전장치 점검 → 최종 등급 결정
- ✅ **시장 체제별 동적 가중치 매트릭스**: 확장기/둔화기/수축기/회복기별로 최적화된 가중치 배분 (총합 100%)
- ✅ **주식 유형별 평가 조정**: 가치주(재무+DCF 우선) vs 성장주(성장률 우선, DCF 보수적 적용)
- ✅ **시스템적 안전장치 트리거**: 파산 위험, 회계 부정, 고평가, 악재 뉴스 감지 시 자동 등급 조정
- ✅ **점수화된 의사결정 프레임워크**: 0-100점 척도로 모든 분석 영역 평가, 총점 기반 등급 결정
- ✅ **Memory Bank 업데이트**: 새로운 의사결정 프레임워크를 반영하여 문서 업데이트

### OpenTelemetry Context Detachment Fix (Previous)
- ✅ **OpenTelemetry 완전 비활성화**: ADK 내부에서 발생하는 context detachment 오류 해결
- ✅ **환경 변수 설정**: `OTEL_SDK_DISABLED=true`, `OTEL_DISABLE_TELEMETRY=true`, `OTEL_TRACES_EXPORTER=none` 설정
- ✅ **Monkey Patching**: OpenTelemetry 모듈을 완전히 차단하여 초기화 자체를 방지
- ✅ **함수 오버라이딩**: `opentelemetry.context._RUNTIME_CONTEXT.detach`와 `reset` 함수를 안전한 버전으로 교체
- ✅ **예외 처리**: ValueError와 RuntimeError를 로깅하고 시스템 크래시 방지
- ✅ **다층적 접근**: 환경 변수 + 모듈 패칭 + 함수 오버라이딩으로 완벽한 비활성화 보장
- ✅ **오류 해결**: "Failed to detach context" 및 "ValueError: <Token...> was created in a different Context" 오류 완전 제거

### Stock Research Team Architecture Refactoring (Previous)
- ✅ **Stock Research Team 분리**: 기존 stock_researcher_agent를 web_researcher_agent와 analyst_opinion_analyst_agent로 분리
- ✅ **Tavily MCP 통합**: Firecrawl 대신 Tavily를 웹 리서치 도구로 채택하여 더 안정적인 성능 확보
- ✅ **병렬 처리 구조**: Web Researcher + Analyst Opinion Analyst가 병렬로 실행 후 Senior Research Advisor가 결과 통합
- ✅ **도구 재배치**: analyst_opinion_analyst 전용 tools 폴더 생성 및 FMP 분석가 도구들 이동
- ✅ **코드 정리**: 불필요한 stock_researcher 폴더 완전 제거 및 import 경로 정리
- ✅ **Memory Bank 업데이트**: 새로운 아키텍처를 반영하여 문서 업데이트

### Project Manager Agent Integration (Previous)
- ✅ **Project Manager Agent**: Added Project Manager as the first agent in the workflow
- ✅ **Customized Instructions**: Project Manager analyzes user queries and generates tailored instructions for each of the 5 analysis teams
- ✅ **Session State Communication**: Instructions passed through session state to specialized agents using InstructionProvider pattern
- ✅ **User Query Access**: Senior advisors now have access to original user queries for better context
- ✅ **Token Optimization**: Maintained `include_contents='none'` for senior advisors to reduce token usage while preserving user context
- ✅ **Logging Standardization**: Updated logging to use centralized logging configuration

### Firestore Dynamic Model Configuration (Previous)
- ✅ **Complete Firestore Integration**: Implemented dynamic AI model configuration for all 12 agents
- ✅ **Agent-Specific Models**: Each agent can now use different LLM models (e.g., hedge_fund_manager uses gemini-2.5-pro)
- ✅ **Real-Time Configuration**: Models can be changed via Firebase Console without code deployment
- ✅ **Zero Runtime Overhead**: Configurations loaded once at startup, cached in memory for O(1) lookups
- ✅ **Graceful Fallback**: System continues operating with default models if Firestore unavailable
- ✅ **Comprehensive Documentation**: Added setup guides, configuration management, and troubleshooting
- ✅ **Testing Infrastructure**: Created utility scripts for Firestore population and connection testing

### Infrastructure Simplification (Previous)
- Removed all Google Cloud and Vertex AI dependencies
- Eliminated OpenTelemetry tracing infrastructure
- Removed Agent Engine deployment support
- Simplified logging configuration (basic Python logging only)
- Cleaned up ~800+ lines of unused code
- System now fully cloud-agnostic

### Deployment Infrastructure
- Production deployment on VPS at `158.247.216.21`
- Docker-based containerization with multi-stage architecture
- Nginx reverse proxy with health checks
- PostgreSQL database for user sessions
- Local backend deployment only (no cloud dependencies)

### Agent Result Storage System
- File-based storage for agent analysis results
- Results organized by user_id and session_id
- API endpoints for saving/loading agent results
- Integration with streaming processor for automatic result capture

### Authentication System
- NextAuth.js with credential-based authentication
- PostgreSQL-backed user management
- Admin user seeding on startup
- Session-based authentication

## Current Technical Focus

### Active Components
1. **Multi-Agent Analysis System**: 13 specialized agents coordinating stock analysis (including Project Manager)
2. **Stock Research Team**: Web Researcher + Analyst Opinion Analyst (parallel) → Senior Research Advisor (synthesis)
3. **Real-Time Streaming**: SSE-based streaming with activity timeline
4. **Financial Data Integration**: FMP API for comprehensive financial data + Tavily for web research
5. **Result Storage**: Filesystem-based agent result archival
6. **Simplified Infrastructure**: No cloud dependencies, local-first architecture

### Known Limitations
- Financial API (FMP) requires API key configuration
- Agent results not yet integrated with chat UI buttons
- No result persistence in database (only filesystem)
- Model configuration requires backend restart (not real-time)

## Removed Components

### Recently Removed (Stock Research Team Refactoring)
- **app/sub_agents/stock_researcher/**: Complete directory with all tools and agent
- **Stock Researcher Tools**: fmp_price_target_summary, fmp_price_target_news, fmp_historical_stock_grade, fmp_analyst_estimates (moved to analyst_opinion_analyst/tools)

### Previously Removed (Infrastructure Simplification)
- **app/config.py**: Vertex AI initialization and Google Cloud setup
- **app/tracing_env.py**: OpenTelemetry environment management
- **app/disable_tracing.py**: Tracing disable configuration
- **app/engine_utils/**: Complete directory with Cloud Trace exporters and GCS utilities
- **Makefile deploy-adk command**: Agent Engine deployment functionality

### Architecture Changes
- No longer uses Google Cloud Platform services
- No OpenTelemetry instrumentation or tracing
- Simplified to local ADK API server deployment
- Cloud-agnostic infrastructure

## Next Steps

Potential areas for enhancement:
1. Integrate agent result viewing in the UI
2. Add result persistence to PostgreSQL database
3. Add user session history with result loading
4. Enhance error handling for streaming failures
5. Add analytics/monitoring for agent performance
6. Implement real-time model configuration reloading (hot-swap)
7. Add model performance tracking and A/B testing
8. Create admin UI for model configuration management

## Important Notes

- System is designed for Korean language output
- All agent prompts and reports are in Korean
- Uses hierarchical agent architecture (parallel + sequential)
- Streaming implementation follows ADK termination signal pattern
- Agent thinking processes are visible in real-time
- Completely cloud-agnostic - works without any cloud platform dependencies