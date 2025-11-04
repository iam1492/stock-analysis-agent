install:
ifeq ($(OS),Windows_NT)
	@echo "Running Windows install..."
	@where uv >nul 2>nul || ( \
		echo "uv is not installed. Installing uv..." && \
		powershell -Command "irm https://astral.sh/uv/install.ps1 | iex" \
	)
	@uv sync && npm --prefix nextjs install
else
	@echo "Running Unix/Linux/macOS install..."
	@command -v uv >/dev/null 2>&1 || { \
		echo "uv is not installed. Installing uv..."; \
		curl -LsSf https://astral.sh/uv/install.sh | sh; \
		source $$HOME/.cargo/env; \
	}
	@uv sync && npm --prefix nextjs install
endif

dev:
	make dev-backend & make dev-frontend

dev-backend:
	uv run adk api_server app --allow_origins="*"

dev-frontend:
	npm --prefix nextjs run dev

adk-web:
	uv run adk web --port 8501

lint:
	uv run codespell
	uv run ruff check . --diff
	uv run ruff format . --check --diff
	uv run mypy .
