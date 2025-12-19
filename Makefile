.PHONY: up down logs api tests test-cov lint etl-snap etl-jobs etl-user-emb

help:
	@echo "Available make commands:"
	@echo "  make up           - Start all Docker services (with hot-reload)"
	@echo "  make down         - Stop and remove Docker services"
	@echo "  make logs         - Tail Docker logs"
	@echo "  make api          - Show API access info (API runs automatically with 'make up')"
	@echo "  make tests        - Run pytest test suite in Docker"
	@echo "  make test-cov     - Run pytest with coverage report in Docker"
	@echo "  make lint         - Run pylint in Docker on app, scripts, and tests"
	@echo "  make etl-snap     - Load SNAP GitHub data into Neo4j (runs in Docker)"
	@echo "  make etl-jobs     - Load LinkedIn job listings into Neo4j (runs in Docker)"
	@echo "  make etl-user-emb - Create user embeddings in Neo4j (runs in Docker)"
	@echo "  make run        - Load all data into Neo4j"
	@echo "  make pip          - Install dependencies in Docker container"

up:
	docker compose up

down:
	docker compose down -v

logs:
	docker compose logs -f

api:
	@echo "Note: The API is already running in Docker via 'make up'."
	@echo "Access it at http://localhost:8000/docs"
	@echo "Code changes are automatically reloaded (hot-reload enabled)"

tests:
	docker compose run --rm tests

test-cov:
	@if command -v pytest >/dev/null 2>&1; then \
		if python -c "import pytest_cov" 2>/dev/null; then \
			echo "Running pytest with coverage locally..."; \
			PYTHONPATH=. pytest --cov=app --cov=scripts --cov-report=term-missing --cov-report=html || true; \
		else \
			echo "Installing pytest-cov..."; \
			python -m pip install -q pytest-cov pytest-asyncio && \
			if python -c "import pytest_cov" 2>/dev/null; then \
				echo "Running pytest with coverage locally..."; \
				PYTHONPATH=. pytest --cov=app --cov=scripts --cov-report=term-missing --cov-report=html || true; \
			else \
				echo "Failed to install pytest-cov. Trying Docker..."; \
				docker compose run --rm tests-cov 2>/dev/null || echo "Docker also failed."; \
			fi \
		fi \
	else \
		echo "pytest not found locally, trying Docker..."; \
		docker compose run --rm tests-cov 2>/dev/null || { \
			echo "Docker failed. Installing pytest and pytest-cov locally..."; \
			python -m pip install -q pytest pytest-cov pytest-asyncio && \
			if python -c "import pytest_cov" 2>/dev/null; then \
				PYTHONPATH=. pytest --cov=app --cov=scripts --cov-report=term-missing --cov-report=html || true; \
			else \
				echo "Failed to install dependencies."; \
			fi \
		}; \
	fi

lint:
	@if command -v pylint >/dev/null 2>&1; then \
		echo "Running pylint locally..."; \
		pylint app scripts tests --exit-zero || true; \
	else \
		echo "pylint not found locally, trying Docker..."; \
		docker compose run --rm lint 2>/dev/null || { \
			echo "Docker failed. Installing pylint locally..."; \
			python -m pip install -q pylint && \
			pylint app scripts tests --exit-zero || true; \
		}; \
	fi

etl-snap:
	docker compose exec api python -m scripts.load_snap

etl-jobs:
	docker compose exec api python -m scripts.load_jobs

etl-user-emb:
	docker compose exec api python -m scripts.create_user_embeddings

run:
	make pip
	make etl-snap
	make etl-jobs
	make etl-user-emb

pip:
	docker compose exec api pip install -r requirements.txt