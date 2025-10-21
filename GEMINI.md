# Project Overview

This is a stock analysis agent project with a Python backend and a Next.js frontend.

The backend is a Vertex AI Agent Engine application that uses the `google-adk` library to deploy and manage the agent. The agent is composed of several sub-agents, each responsible for a specific task in stock analysis, such as fundamental analysis, quantitative analysis, and technical analysis.

The frontend is a chat interface built with Next.js, React, and Tailwind CSS. It allows users to interact with the stock analysis agent.

# Building and Running

## Backend

To deploy the backend, run the following command:

```bash
python -m app.agent_engine_app
```

This will deploy the agent to Vertex AI Agent Engine.

## Frontend

To run the frontend, navigate to the `nextjs` directory and run the following commands:

```bash
npm install
npm run dev
```

This will start the development server at `http://localhost:3000`.

# Development Conventions

## Backend

The backend code is located in the `app` directory. The main application logic is in `app/agent_engine_app.py`, and the agent definition is in `app/agent.py`. The sub-agents are located in the `app/sub_agents` directory.

The backend uses `ruff`, `mypy`, and `codespell` for linting.

## Frontend

The frontend code is located in the `nextjs` directory. The main application component is in `nextjs/src/app/page.tsx`. The chat interface components are located in the `nextjs/src/components/chat` directory.

The frontend uses `eslint` for linting.
