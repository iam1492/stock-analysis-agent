# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is a **Stock Analysis Agent** - a multi-agent AI system for financial analysis using Google's ADK (Agent Development Kit). The system orchestrates 11 specialized AI agents that analyze different aspects of stock performance, from fundamental analysis to technical indicators and macroeconomic factors.

**Technology Stack:**
- **Backend**: Python 3.10-3.13 with Google ADK 1.17.0, FastAPI
- **Frontend**: Next.js 15.4.3 with React 19, TypeScript, Tailwind CSS
- **Database**: PostgreSQL 15 with Prisma ORM
- **Authentication**: NextAuth.js v5 with Google OAuth
- **Configuration**: Firebase Firestore for dynamic model configuration

## Essential Development Commands

### Quick Start
```bash
make install     # Install all dependencies (Python + Node.js)
make dev         # Run both backend and frontend in development mode
```

### Backend Development
```bash
make dev-backend     # Run backend API server (port 8000)
make adk-web        # Run ADK web interface (port 8501)
```

### Frontend Development
```bash
cd nextjs
npm run dev         # Run frontend development server (port 3000)
npm run build       # Build production app
npm run db:generate # Generate Prisma client
npm run db:migrate  # Run database migrations
```

### Code Quality
```bash
make lint           # Run all linting (Ruff, MyPy, ESLint, codespell)
```

### Docker
```bash
docker-compose up   # Full stack with PostgreSQL, backend, frontend, nginx
```

## Architecture Overview

### Multi-Agent Hierarchy
The system uses a hierarchical agent orchestration pattern:

```
Root Agent (Sequential)
├── Stock Analysis Department (Parallel)
│   ├── Financial Team (Sequential) - Fundamental analysis agents
│   ├── Quantitative Team (Sequential) - Quantitative analysis agents
│   └── Individual specialists (Technical, Macro, Research)
└── Hedge Fund Manager (Final synthesis)
```

### Key Directories
- **`/app`**: Python backend with agent orchestration
  - `agent.py`: Main orchestrator that coordinates all sub-agents
  - `sub_agents/`: 11 specialized financial analysis agents
  - `credentials/`: Firebase and service account configurations
- **`/nextjs`**: Next.js frontend application
  - `src/app/`: App Router pages and API routes
  - `src/components/`: Reusable React components
  - `prisma/`: Database schema and migrations

### Agent Pattern
Each agent follows a standardized factory pattern with:
- Dynamic model assignment from Firestore
- Shared instruction integration via `{shared_instruction}` template
- Specific financial data tools (FMP API integration)
- Consistent output format with FACT/OPINION sections

### Configuration Management
- **Firestore Collections**:
  - `stock_agents`: Agent-specific model configurations
  - `stock_agent_company/shared_instruction`: Global shared instructions
- **Caching**: In-memory caching with fallback defaults
- **Real-time Updates**: Configuration changes apply without deployment

### Frontend Architecture
- **Streaming**: Server-Sent Events (SSE) for real-time agent responses
- **State Management**: React Context with localStorage persistence
- **API Pattern**: `/api/run_sse` forwards to Python backend
- **Authentication**: NextAuth.js with Google OAuth

## Development Guidelines

### Adding New Agents
1. Create factory function in `app/sub_agents/`
2. Include `{shared_instruction}` template variable
3. Use `lite_llm_model()` for dynamic model assignment
4. Define specific tools and output key
5. Follow FACT/OPINION output format
6. Add to orchestrator hierarchy in `app/agent.py`

### Working with Configuration
- Runtime changes via Firestore (no deployment needed)
- Always provide fallback defaults
- Test Firestore unavailability scenarios
- Consider caching implications

### Frontend Development
- Use ChatProvider context for state management
- Follow SSE streaming patterns for real-time updates
- Implement proper error handling and loading states
- Maintain session persistence with localStorage

### Code Quality Standards
- **Python**: Ruff linting, MyPy type checking, strict typing
- **TypeScript**: ESLint rules, proper type definitions
- **Testing**: Jest for frontend, implement backend tests
- **Documentation**: Follow existing patterns for docstrings

### External API Integration
- Use existing FMP API client patterns in `app/tools/`
- Implement proper error handling and retries
- Follow rate limiting best practices
- Add caching where appropriate

## Common Tasks

### Running a Single Test
```bash
# Frontend tests
cd nextjs && npm test -- --testNamePattern="test name"

# Backend tests (when implemented)
uv run pytest path/to/test.py::test_function
```

### Database Operations
```bash
cd nextjs
npm run db:push     # Push schema changes
npm run db:migrate  # Run migrations
npm run db:seed     # Seed database
npm run db:studio   # Open Prisma Studio
```

### Checking Logs
```bash
# Backend logs show agent orchestration and tool usage
# Frontend browser console shows streaming and state updates
# Docker logs: docker-compose logs -f [service-name]
```

### Deployment Preparation
```bash
make lint           # Ensure code quality
npm run build       # Test frontend build
docker-compose build # Test container builds
```

## Important Notes

- **Agent Results**: Stored in session state, accessible across agent hierarchy
- **Shared Instructions**: Loaded once per session, available to all agents via template
- **Model Configuration**: Per-agent models loaded from Firestore at runtime
- **Error Handling**: Graceful degradation with fallbacks for external services
- **Caching**: Multiple levels (Firestore config, local storage, memory) for performance
- **Streaming**: Real-time updates via SSE, handle connection drops gracefully