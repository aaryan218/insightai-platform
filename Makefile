# ---- InsightAI convenience commands ----

.PHONY: up down backend frontend test lint migrate seed

up:
	docker compose up --build

down:
	docker compose down

backend:
	cd backend && uvicorn app.main:app --reload

frontend:
	cd frontend && npm run dev

test:
	./scripts/run_tests.sh

lint:
	./scripts/lint_all.sh

migrate:
	./scripts/run_migrations.sh

seed:
	./scripts/seed_database.sh
