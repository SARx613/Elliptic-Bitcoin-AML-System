.PHONY: up down logs api tests lint etl-snap etl-jobs etl-user-emb

help:
	@echo "Available make commands:"
	@echo "  make up           - Start all Docker services (with hot-reload)"
	@echo "  make down         - Stop and remove Docker services"
	@echo "  make logs         - Tail Docker logs"
	@echo "  make api          - Show API access info (API runs automatically with 'make up')"
	@echo "  make tests        - Run pytest test suite in Docker"
	@echo "  make lint         - Run pylint in Docker on app, scripts, and tests"
	@echo "  make etl-snap     - Load SNAP GitHub data into Neo4j (runs in Docker)"
	@echo "  make etl-jobs     - Load LinkedIn job listings into Neo4j (runs in Docker)"
	@echo "  make etl-user-emb - Create user embeddings in Neo4j (runs in Docker)"
	@echo "  make begin        - Load all data into Neo4j"
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

lint:
	docker compose exec api pylint app scripts tests --exit-zero || true

etl-snap:
	docker compose exec api python -m scripts.load_snap

etl-jobs:
	docker compose exec api python -m scripts.load_jobs

etl-user-emb:
	docker compose exec api python -m scripts.create_user_embeddings

begin:
	make etl-snap
	make etl-jobs
	make etl-user-emb

pip:
	docker compose exec api pip install -r requirements.txt