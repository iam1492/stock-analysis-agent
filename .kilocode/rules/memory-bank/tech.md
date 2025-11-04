# Technology Stack and Development Setup

## Core Technologies

### Backend Stack
- **Python 3.10-3.13**: Core backend language
- **Google ADK 1.17.0**: Agent Development Kit for multi-agent orchestration
- **LiteLLM**: Model abstraction layer
- **FastAPI**: REST API framework (implicit via ADK)
- **Cachetools**: Caching utilities

### Frontend Stack
- **Next.js 15.4.3**: React framework with App Router
- **React 19.1.0**: UI library
- **TypeScript 5**: Type-safe JavaScript
- **Tailwind CSS 3.4.17**: Utility-first CSS framework
- **shadcn/ui**: Component library built on Radix UI
- **NextAuth 5.0.0-beta.29**: Authentication library

### Database & Storage
- **PostgreSQL 15**: Relational database
- **Prisma 6.18.0**: Database ORM and migrations
- **Filesystem**: Agent result storage (JSON files)

### Infrastructure
- **Docker & Docker Compose**: Containerization
- **Nginx**: Reverse proxy and web server
- **uv**: Python package manager (modern pip alternative)

## Development Tools

### Python Development
- **ruff**: Fast Python linter and formatter
- **mypy**: Static type checker
- **codespell**: Spell checker for code
- **pytest**: Testing framework

### Frontend Development
- **ESLint**: JavaScript/TypeScript linter
- **Jest**: Unit testing framework
- **React Testing Library**: Component testing
- **tsx**: TypeScript execution

### Build Tools
- **Make**: Task automation (cross-platform)
- **npm**: Package management for frontend
- **Prisma CLI**: Database migrations and client generation

## Key Dependencies

### Backend (`pyproject.toml`)
```toml
[project.dependencies]
google-adk = "1.17.0"
python-dotenv = "*"
litellm = "*"
cachetools = "*"

[project.optional-dependencies.lint]
ruff = ">=0.4.6"
mypy = "~=1.15.0"
codespell = "~=2.2.0"
types-pyyaml = "~=6.0.12.20240917"
types-requests = "~=2.32.0.20240914"
```

### Frontend (`package.json`)
```json
{
  "dependencies": {
    "@prisma/client": "^6.18.0",
    "next": "^15.4.3",
    "next-auth": "^5.0.0-beta.29",
    "react": "^19.1.0",
    "bcryptjs": "^3.0.2",
    "lucide-react": "^0.525.0",
    "react-markdown": "^10.1.0"
  }
}
```

## Development Environment Setup

### Prerequisites
- **Python**: 3.10 to 3.13
- **Node.js**: Latest LTS version
- **Docker**: Latest stable version
- **uv**: Python package manager

### Installation Steps

**1. Install Dependencies (Cross-Platform)**
```bash
make install
```

This command:
- Installs `uv` if not present (Windows: PowerShell, Unix: curl)
- Runs `uv sync` for Python dependencies
- Runs `npm install` for frontend dependencies

**2. Environment Configuration**

Backend (`.env` or `app/.env`):
```bash
# Financial API
FMP_API_KEY=your-fmp-api-key

# Model Configuration (hardcoded in code, not used from env)
MODEL=gemini-2.5-flash
```

Frontend (`nextjs/.env` or root `.env`):
```bash
# Database
DATABASE_URL=postgresql://stock_user:password@localhost:5432/stock_analysis

# Authentication
NEXTAUTH_SECRET=your-secret-key
NEXTAUTH_URL=http://localhost:3000
AUTH_TRUST_HOST=true

# Admin User (for seeding)
ADMIN_EMAIL=admin@example.com
ADMIN_PASSWORD=secure-password
ADMIN_NAME=Admin User

# Backend URL
BACKEND_URL=http://localhost:8000
```

### Development Commands

**Start Development Servers**
```bash
# Both frontend and backend
make dev

# Backend only
make dev-backend

# Frontend only
make dev-frontend
```

**ADK Web Interface** (Alternative UI)
```bash
make adk-web
```

**Linting and Type Checking**
```bash
make lint
```

**Database Operations**
```bash
# Generate Prisma client
npm --prefix nextjs run db:generate

# Push schema to database
npm --prefix nextjs run db:push

# Run migrations
npm --prefix nextjs run db:migrate

# Seed database
npm --prefix nextjs run db:seed
```

## Project Structure Patterns

### Backend Organization
- **`app/agent.py`**: Root agent definition and hierarchy
- **`app/logging_config.py`**: Simplified logging setup
- **`app/sub_agents/`**: One directory per specialized agent
  - Each agent directory contains:
    - `agent.py`: Agent definition
    - `tools/`: Agent-specific tools (if any)
- **`app/sub_agents/utils/`**: Shared utilities
  - `fmp_api_client.py`: Common FMP API client
  - `llm_model.py`: LLM model configuration (hardcoded gemini-2.5-flash)

### Frontend Organization
- **`src/app/`**: Next.js App Router pages and API routes
- **`src/components/`**: Reusable UI components
  - `chat/`: Chat-specific components
  - `ui/`: shadcn/ui base components
- **`src/lib/`**: Utility libraries and services
  - `handlers/`: Request handling logic
  - `streaming/`: SSE processing logic
- **`src/hooks/`**: Custom React hooks

### Configuration Files
- **`pyproject.toml`**: Python project configuration
- **`package.json`**: Node.js project configuration
- **`tsconfig.json`**: TypeScript configuration
- **`tailwind.config.ts`**: Tailwind CSS configuration
- **`docker-compose.yml`**: Production Docker configuration
- **`docker-compose-dev.yml`**: Development Docker configuration

## Technical Constraints

### Python Constraints
- **Version Range**: 3.10 to 3.13.2 (ADK compatibility)
- **Type Checking**: Strict mypy configuration enabled
- **Code Style**: Enforced via ruff (line length: 88, target: py310)

### Frontend Constraints
- **Next.js App Router**: Must use new routing paradigm
- **Server Components**: Default to server components, use "use client" explicitly
- **React 19**: New features like `use` hook available
- **API Routes**: Maximum execution duration: 300 seconds (5 minutes)

### Database Constraints
- **PostgreSQL 15**: Required for compatibility
- **Prisma Schema**: Must run `prisma generate` after schema changes
- **Migrations**: Production requires explicit migration deployment

### Docker Constraints
- **Multi-stage Builds**: Used for optimization
- **Health Checks**: Required for service dependencies
- **Network**: Internal network (172.20.0.0/16)
- **Volume Persistence**: PostgreSQL data persisted via named volumes

## External API Dependencies

### Financial Modeling Prep (FMP) API
- **Base URL**: `https://financialmodelingprep.com/stable/`
- **Authentication**: API key in query parameters
- **Rate Limits**: Depends on subscription tier
- **Endpoints Used**:
  - Balance Sheet Statement
  - Income Statement
  - Cash Flow Statement
  - Key Metrics
  - Financial Ratios
  - DCF Valuation
  - Enterprise Value
  - Owner Earnings
  - Economic Indicators
  - Stock News
  - Price Targets
  - Historical Grades
  - Technical Indicators (SMA, RSI, ADX)
  - Growth Metrics

### Google Gemini AI
- **Purpose**: LLM inference via google.adk
- **Model**: gemini-2.5-flash (hardcoded in code)
- **Authentication**: Handled internally by ADK
- **No additional configuration required**

## Development Workflow

### Local Development
1. Start PostgreSQL (via Docker or local installation)
2. Run `make install` to install dependencies
3. Configure environment variables (.env file)
4. Run `make dev` to start both servers
5. Access frontend at `http://localhost:3000`
6. Access backend at `http://localhost:8000`

### Docker Development
1. Configure `.env` file with required variables
2. Run `docker-compose up` (uses production compose file)
3. Or `docker-compose -f docker-compose-dev.yml up` (uses Docker Hub images)
4. Access application at `http://localhost` (port 80)

### Testing Workflow
```bash
# Frontend tests
npm --prefix nextjs test

# Backend linting and type checking
make lint

# Manual testing via ADK web interface
make adk-web
```

## Build and Deployment

### Docker Build Process
```bash
# Build all images
docker-compose build

# Build specific service
docker-compose build stock-analysis-backend
```

### Production Deployment
1. Set production environment variables in `.env.production`
2. Build Docker images
3. Push to registry (optional)
4. Deploy via `docker-compose -f docker-compose.yml up -d`
5. Run database migrations: `docker exec stock-analysis-frontend npm run db:migrate`
6. Seed admin user: `docker exec stock-analysis-frontend npm run db:seed`

### Health Check Endpoints
- Frontend: `http://localhost:3000/api/health`
- Backend: `http://localhost:8000/health` (implicit via ADK)
- Nginx: `http://localhost/health`

## Performance Optimization

### Backend
- **Parallel Agent Execution**: Financial and Quantitative teams run in parallel
- **Caching**: LiteLLM caching for repeated model calls
- **Connection Pooling**: Implicit in Prisma for PostgreSQL

### Frontend
- **Server Components**: Default rendering strategy for better performance
- **Code Splitting**: Automatic via Next.js
- **Image Optimization**: Next.js Image component
- **SSE Streaming**: Progressive rendering of agent responses

### Docker
- **Multi-stage Builds**: Smaller final images
- **Layer Caching**: Optimized Dockerfile layer ordering
- **Alpine Base**: Smaller base images where possible

## Debugging and Logging

### Backend Logging
- **Module**: `app/logging_config.py`
- **Format**: Structured logging with timestamps
- **Output**: Console (stdout)
- **Levels**: Configurable via LOG_LEVEL environment variable

### Frontend Logging
- Browser console for client-side
- Next.js server logs for API routes
- Streaming processor logs for SSE events

### Docker Logs
```bash
# View all logs
docker-compose logs -f

# View specific service
docker-compose logs -f stock-analysis-backend

# View with timestamps
docker-compose logs -f -t
```

## Common Issues and Solutions

### Issue: FMP API Rate Limits
**Solution**: Upgrade FMP subscription or implement caching layer for frequently accessed data.

### Issue: PostgreSQL Connection Refused
**Solution**: Ensure PostgreSQL is running and DATABASE_URL is correctly configured with proper host (localhost for local, postgres for Docker).

### Issue: Prisma Client Out of Sync
**Solution**: Run `npm --prefix nextjs run db:generate` after schema changes.

### Issue: Docker Health Checks Failing
**Solution**: Check individual service logs, ensure proper startup order, verify health check endpoints.

## Version Management

### Semantic Versioning
- Backend: Defined in `pyproject.toml` (currently 0.1.0)
- Frontend: Defined in `package.json` (currently 0.1.0)
- Docker Images: Tagged with version numbers

### Upgrade Strategy
1. Update dependency versions in configuration files
2. Test locally with `make install` and `make dev`
3. Run `make lint` to ensure code quality
4. Rebuild Docker images
5. Deploy to staging/production