# InsightAI - AI Customer Analytics Platform

Enterprise-grade AI/ML platform for customer analytics: segmentation, churn
prediction, CLV, fraud detection, sales forecasting, and an LLM-powered
business assistant.

## Repository Layout
- `backend/`   FastAPI service (Clean Architecture, DDD)
- `frontend/`  React + TypeScript + Vite SPA
- `ml/`        Standalone ML package (training, inference, registry)
- `infra/`, `terraform/`, `k8s/`, `docker/`  Infrastructure as code
- `docs/`      Architecture, API, database, deployment, product docs
- `scripts/`   Operational scripts (setup, migrations, deploy, tests)
- `notebooks/` Exploratory data science notebooks
- `tests/`     Cross-service end-to-end tests

## Getting Started
See `docs/deployment/local_setup.md`.

## Architecture
See `docs/architecture/system_overview.md` and `docs/architecture/adr/`.

## License
See `LICENSE`.





