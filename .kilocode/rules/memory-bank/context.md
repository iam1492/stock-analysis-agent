# Current Context

## Current Project State

The Stock Analysis Agent is a **production-ready** web application that provides AI-powered stock analysis through a chat interface. The system is currently deployed and operational with a streamlined, cloud-agnostic architecture.

## Recent Work

### Project Manager Agent Integration (Latest)
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
1. **Multi-Agent Analysis System**: 12 specialized agents coordinating stock analysis (including Project Manager)
2. **Real-Time Streaming**: SSE-based streaming with activity timeline
3. **Financial Data Integration**: FMP API for comprehensive financial data
4. **Result Storage**: Filesystem-based agent result archival
5. **Simplified Infrastructure**: No cloud dependencies, local-first architecture

### Known Limitations
- Financial API (FMP) requires API key configuration
- Agent results not yet integrated with chat UI buttons
- No result persistence in database (only filesystem)
- Model configuration requires backend restart (not real-time)

## Removed Components

### Recently Removed (Latest Refactoring)
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