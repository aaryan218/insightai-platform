# Backend Architecture — InsightAI Platform

*Location in repo: `docs/architecture/backend_architecture.md`. Companion documents: `system_overview.md` (cross-cutting, includes frontend), `ml_architecture.md` (deep dive on `ml/insightai_ml` internals), `data_flow_diagram.md`. This document explains **why the backend is built the way it is**, module by module, not just what each folder contains. Nothing in the tree structure is changed here — this is documentation, not a proposal.*

---

## 1. Purpose and Scope

This document exists because a tree listing tells you *what* exists, not *why*. Six months from now, someone will ask "why do we have both a `jobs/` folder and a `workers/` folder — isn't that the same thing?" or "why is `ml/` a totally separate top-level package instead of living inside `backend/app`?" Those are exactly the questions this document answers, decision by decision, the way I'd want them answered if I inherited this codebase.

The short version, stated up front so nothing below is a surprise: **this backend is a modular monolith, deliberately built with internal seams (a repository layer, a dependency-injection container, an internal event bus, a narrow ML interface, and Terraform modules that already mirror future service boundaries) so that splitting pieces off into real microservices later is a matter of moving code across a seam that already exists — not a rewrite.** Every structural decision documented below is in service of that one idea. Section 16 ties it back together explicitly.

---

## 2. Architectural Philosophy: Modular Monolith, Microservices as Earned

The product surface (EDA, dashboards, five ML verticals, a workflow builder, a notebook, RBAC/audit, a chat/NL-query layer) could plausibly be decomposed into a dozen-plus independently deployable services on day one. We didn't do that, for the same reason most experienced teams don't: **you can't correctly draw service boundaries before you have real usage data telling you where the actual coupling and scaling pressure live.** Guess wrong with a monolith and it's a refactor. Guess wrong with microservices and it's a distributed-systems migration — service-to-service auth, network retries, distributed tracing, and all — undertaken to fix boundaries nobody has validated yet.

So `backend/` is **one deployable FastAPI application**, internally organized into modules with enforced boundaries (services don't reach into other services' repositories; nothing bypasses the repository layer to touch the DB session directly). This gets us:

- **One thing to deploy, one thing to roll back, one place to look during an incident** — the operational surface area of a five-person team, not a fifty-service team.
- **The *option* to extract any module later**, because the module boundaries are enforced through code (imports, DI, interfaces), not just convention. A codebase organized this way can be split module-by-module as real scaling pressure demands it. A codebase that started as microservices without validated boundaries is materially harder to *consolidate* if those boundaries turn out wrong — and early-stage boundaries are usually wrong.

The concrete triggers for extracting a module into its own service are not calendar-based. They're: (a) a module's compute profile fundamentally diverges from the rest of the system (Training is the obvious first case — bursty, CPU/GPU-heavy, nothing like the rest of the request/response API), (b) a module needs to scale or fail independently for reliability reasons (Monitoring is the second case — it's a standing background process that should never be able to take down interactive dashboard requests), or (c) a team boundary forms around a module and extraction reduces coordination overhead. You'll notice `deployment-backend.yaml` and `deployment-worker.yaml` are already separate Kubernetes deployments (Section 10) — that's the monolith's codebase still, but already scaled independently, which is exactly the cheap, incremental first step before a real service split.

---

## 3. System Component Map

```
                        ┌─────────────────────┐
                        │   React Frontend      │
                        │   (Vite + TS)          │
                        └──────────┬───────────┘
                                   │  HTTPS
                                   ▼
                        ┌─────────────────────┐
                        │  nginx / API Gateway  │   (local: nginx.conf via docker-compose)
                        │  (prod: ALB/Ingress)   │   (prod: k8s ingress.yaml)
                        └──────────┬───────────┘
                                   │
                                   ▼
        ┌──────────────────────────────────────────────────┐
        │              backend/app  (FastAPI monolith)       │
        │                                                      │
        │  api/v1  →  services/  →  repositories/  →  db/      │
        │     ▲            │              │                    │
        │  middleware/   events/      models/ (ORM)             │
        │  auth/         core/ (DI)                              │
        │  exceptions/                                            │
        │                                                          │
        │  ml_interface/  ─────────────────┐                       │
        └───────────────────────────────────┼───────────────────┘
                                            │  in-process import (V1)
                                            │  → future: HTTP/gRPC (V2+)
                                            ▼
                        ┌─────────────────────────────┐
                        │  ml/insightai_ml (package)    │
                        │  churn · clv · fraud ·          │
                        │  forecasting · segmentation ·    │
                        │  eda · feature_engineering ·      │
                        │  explainability · drift · llm ·    │
                        │  pipelines · registry · tracking    │
                        └─────────────────────────────┘

        backend/app/workers/  ──publishes/consumes──▶  Redis (Celery broker)
        backend/app/jobs/     ──invoked by──▶  workers/ + scheduled beat

        Postgres (metadata: users, orgs, datasets, model registry, audit log)
        S3 / MinIO (blobs: raw datasets, model artifacts, generated reports)
        Prometheus + Grafana (backend-overview, ml-model-performance dashboards)
```

Everything below explains one box or one arrow in this diagram.

---

## 4. Layered Architecture Inside `backend/app`

The core of the backend follows a conventional four-layer design — **API → Service → Repository → Database** — enforced as a one-way dependency rule: API depends on Services, Services depend on Repositories, Repositories depend on the DB session. Nothing skips a layer (an endpoint never touches a repository directly; a repository never contains business logic). This isn't decoration — it's what makes every layer independently testable and independently replaceable.

### 4.1 `api/v1` — The Presentation / Transport Layer

```
api/v1/endpoints/{auth, chat, churn, clv, dashboard, datasets, eda,
                   forecasting, fraud, health, models_registry,
                   reports, segmentation, users}.py
api/v1/router.py
api/deps.py
```

- **Versioned from day one (`v1`).** Once a customer holds an API key (PRD §11.5) and has built an integration against our contract, we cannot casually change response shapes under them. Versioning the URL path costs nothing today and avoids a painful renegotiation later.
- **One file per domain capability, not per HTTP verb.** `churn.py` holds all churn-related routes; there's no `get_churn.py`/`post_churn.py` split. This mirrors the product's own objective surfaces (PRD §6.3, §7) — anyone looking for "how does churn prediction work end-to-end" starts in exactly one file.
- **`router.py` is the single point of route registration.** Every endpoint module exposes an `APIRouter`; `router.py` is the only place that assembles them under `/api/v1`. This means adding a new capability (say, a sixth ML vertical) never requires touching `main.py`, and there's exactly one place to see the full route surface at a glance.
- **`deps.py` centralizes FastAPI's `Depends()` wiring** — `get_current_user`, `get_db_session`, `require_permission(...)`, etc. Thirteen endpoint files needing "who's the authenticated user, and are they allowed to do this" is exactly the kind of logic that rots if duplicated thirteen times. One change to how auth works happens in one file.
- **Endpoints are intentionally thin.** An endpoint's job is: parse and validate the request against a `schemas/` model, call exactly one service method, return a `schemas/` model. No business logic, no direct DB access, no direct calls into `ml_interface/`. This is what lets us unit-test business logic (Section 13) without spinning up an HTTP server, and it's what makes an endpoint file readable as a table of contents rather than an implementation.

### 4.2 `schemas/` vs `models/` — Two Representations, On Purpose

This is a common point of confusion for anyone new to the codebase, so it's worth being explicit: **`app/models` is the SQLAlchemy ORM layer (what's actually in Postgres). `app/schemas` is the Pydantic layer (what actually crosses the wire as JSON).** They are not the same objects, and that's deliberate:

- **API contract evolution and DB schema evolution are different concerns that change on different timelines.** A migration that renames a DB column shouldn't automatically break every client integration; a new field on an API response shouldn't necessarily require a DB migration if it's computed.
- **It prevents accidental data leakage.** `models/user.py` has a `hashed_password` column. `schemas/user.py`'s `UserResponse` simply doesn't have that field. If we returned the ORM object directly, we'd be one refactor away from leaking a password hash in a JSON response. This decoupling makes that class of bug structurally impossible rather than something we have to remember to avoid.
- **Request and response shapes are legitimately asymmetric** — `CreateUserRequest` doesn't have an `id` or `created_at`; `UserResponse` does. A single shared model can't cleanly express that; two purpose-built schemas can.

### 4.3 `services/` — Business Logic Layer

```
services/{auth, chat, churn, cleaning, clv, dashboard, dataset, eda,
          forecasting, fraud, notification, report, segmentation,
          sql_generation, user}_service.py
```

This is where the actual product logic lives, and — not by accident — it maps almost one-to-one onto the PRD's Agent Roster (§13.2): `eda_service` orchestrates what the EDA Agent contributes (§13.3), `churn_service`/`clv_service`/`fraud_service`/`forecasting_service`/`segmentation_service` each orchestrate a full Model Selection → Training → Evaluation cycle (§13.7) for their vertical, `dashboard_service` is the Analytics/Visualization Agent's home (§13.4–§13.5), `report_service` is the Report Generation Agent (§13.8). The service layer is the **orchestration layer** in practice — it's what calls repositories for persistence, calls `ml_interface/` for anything ML-shaped, publishes domain events, and enforces the human-approval checkpoints (PRD Design Principle 1) before anything consequential happens.

Two services deserve a specific callout:

- **`cleaning_service.py`** implements the PRD's explicit "propose, don't silently apply" pattern (§7.3): cleaning decisions are computed and returned as an editable plan, not executed against data until a human (or, later, a configured auto-approval policy) signs off. This service is the concrete code home of Design Principle 1 for the dataset-cleaning stage specifically.
- **`chat_service.py` + `sql_generation_service.py`** together back the natural-language query surface (§8, and the Priya persona in §4.2). `sql_generation_service` turns a business question into SQL (delegating to `ml/insightai_ml/llm/sql_generator.py`); `chat_service` owns the conversational turn-taking and result formatting. Keeping SQL generation as its own service — not folded into `chat_service` — means it can be reused anywhere a NL-to-SQL capability is needed (e.g., a future workflow-builder node) without depending on chat-specific state.

Why business logic lives here and nowhere else: an endpoint that contains business logic can only be exercised over HTTP; a repository that contains business logic can't be swapped for a different persistence strategy without carrying the logic along with it. Services are the one place business rules can be unit-tested with everything else (HTTP, DB) mocked out.

### 4.4 `repositories/` — Data Access Layer (Repository Pattern)

```
repositories/{base, dataset, model, prediction, user}_repository.py
```

`base_repository.py` implements generic CRUD (`get`, `list`, `create`, `update`, `delete`) against a SQLAlchemy model; each domain repository extends it with the queries specific to that entity. Services never touch a SQLAlchemy `Session` directly — they call repository methods.

Two concrete reasons this layer exists, beyond "it's a clean pattern":

1. **It's the one and only choke point for tenant scoping.** The PRD (§14.5) names cross-tenant data leakage as a named security risk and is explicit that isolation must be "enforced centrally... rather than trusted to be applied consistently by every caller." The repository layer *is* that central enforcement point — every domain repository's queries are scoped by `organization_id`/`project_id` internally, so no service, no matter who writes it or when, can forget to add a `WHERE org_id = ...` clause. That's not a convention we're hoping engineers remember; it's structurally unavoidable.
2. **Services become unit-testable without a database.** Mock the repository, and `churn_service`'s orchestration logic can be tested in milliseconds with no Postgres running. This compounds with the DI container (Section 5.2) — repositories are injected, not imported, so a test double drops in cleanly.

### 4.5 `db/` — Persistence Infrastructure

- **SQLAlchemy declarative base + Alembic migrations**, not hand-run DDL. Every schema change is a reviewable, versioned, reversible file under `db/migrations/versions/`. This matters more here than in a typical CRUD app because the PRD's data model (§14.7) requires that "every mutable, consequential entity has a corresponding `*Version` entity" — schema evolution has to be tracked with the same rigor as the data itself, since rollback and lineage-reconstruction guarantees (§11.6) depend on the schema history being trustworthy.
- **`session.py`** provides a request-scoped session via FastAPI dependency injection (wired through `api/deps.py`) — one session per request, closed automatically, no session leakage across requests or accidental sharing between concurrent requests.
- **`init_db.py`** is the first-run bootstrap (seed roles, a default org for local dev, etc.) — deliberately separate from Alembic, which owns *schema* migrations, not *data* seeding.

### 4.6 `models/` — Core Data Model (ORM)

```
models/{audit_log, churn_result, clv_result, dataset, forecast_result,
        fraud_result, model_registry, prediction, segment, user}.py
```

This is the literal implementation of the simplified data model in PRD §14.7. Two decisions worth explaining:

- **`audit_log.py` is a single, generic table** (`actor`, `organization`, `project` (nullable), `action`, `resource_type`, `resource_id`, `timestamp`, `reasoning` (nullable)) rather than a per-feature audit table for datasets, models, dashboards, etc. This is a direct implementation of §14.7's third modeling decision: a single append-only, generically-referencing audit table stays queryable as one system of record across every entity type, which is what makes it usable during an actual compliance review (§11.4). Fragmenting it per feature would make "show me everything this user did last quarter" a UNION across a dozen tables instead of one filtered query.
- **One result table per ML capability** (`churn_result`, `clv_result`, `forecast_result`, `fraud_result`) rather than a single polymorphic `prediction` table with a JSON blob for the payload. Churn's output (probability + risk band), CLV's output (dollar value + confidence interval), forecast's output (point estimate + interval, per §7.8's non-negotiable requirement that a point forecast without an interval is incomplete), and fraud's output (anomaly score + contributing signals) are genuinely different shapes. Forcing them into one generic table trades away query-ability, indexing, and type safety for a "flexibility" nobody actually needs — each capability's consumers (dashboards, exports, the model registry's lineage links) want to query their own shape directly. The generic `prediction.py` model still exists as a thin, capability-agnostic summary row (for cross-capability views like "all predictions this week") that references the specific `*_result` row — best of both without the downsides of full polymorphism.

---

## 5. Cross-Cutting Concerns

### 5.1 `auth/` — Identity and Access Control

```
auth/{jwt_handler, oauth2, password_hashing, permissions, rbac}.py
```

Five files instead of one `auth.py`, because these are five concerns that change on different schedules and for different reasons:

- **`jwt_handler.py`** — token issuance/validation. Changes if we change token lifetime policy, signing algorithm, or add refresh-token rotation.
- **`oauth2.py`** — kept isolated specifically because SSO (SAML/OIDC) is named in the PRD as a **pluggable, later-phase** capability (§11.7) — "the architecture reserves the identity/authentication layer as a pluggable component specifically so that SSO can be added without a broader rearchitecture." Having OAuth2 already factored into its own module, separate from password auth, is exactly what makes that true rather than aspirational.
- **`password_hashing.py`** — hashing/verification primitives only; no policy logic.
- **`permissions.py` vs `rbac.py`** — this split deserves emphasis. `permissions.py` defines atomic capability checks (`can_deploy_model`, `can_approve_workflow`, `can_view_dashboard`). `rbac.py` maps roles (Org Admin, Team Admin, Project Contributor, Project Viewer, **Approver** — PRD §11.3) onto sets of those permissions. Splitting them is what lets the **Approver role stay separable from Contributor/Admin**, which the PRD calls out explicitly as a hard requirement: "in regulated or high-governance environments, the person who builds a model or workflow is often required, by policy, to be different from the person who approves it for production." If permission checks and role-to-permission mapping were tangled together, expressing that separation-of-duties requirement cleanly would be much harder.

### 5.2 `core/` — Configuration, DI Container, Security Primitives

```
core/{config, constants, container, di, logging_config, security}.py
```

- **`config.py`** — typed settings via `pydantic-settings`. All environment configuration is read once, validated against a schema, and fails fast at startup if something required is missing — we find out at deploy time, not three requests into production traffic.
- **`container.py` / `di.py`** — the dependency-injection container. Services and repositories are **constructed with their dependencies passed in** (a DB session, an `ml_interface` client, the event bus) rather than importing module-level singletons. This is not just testability (though it is that — every dependency is a clean substitution point for a test double). It's the mechanical precondition for the module-extraction story in Section 2: a service that receives its dependencies through a constructor doesn't care whether `ml_interface`'s client is backed by an in-process import or an HTTP call to a separately deployed service. Change the container's wiring, not the service.
- **`security.py`** — shared cryptographic primitives (token signing, secret handling) consumed by `auth/`.
- **`logging_config.py`** — structured (JSON) logging setup. This feeds three different downstream consumers: the Prometheus/Grafana stack (Section 12), the audit log (indirectly, via structured event capture), and — per the PRD's explicit warning (§15, Observability) that a "healthy" system can silently produce low-quality outputs — the eventual per-agent evaluation dashboards. Structured logs from day one means we're not retrofitting parseable logs onto a system that only ever emitted free-text strings.

### 5.3 `middleware/`

```
middleware/{cors, error_handler, logging, rate_limit, request_id}_middleware.py
```

- **`request_id_middleware.py`** generates a correlation ID per inbound request and propagates it through logs *and* into any Celery job triggered by that request. This sounds like a minor convenience until you're debugging "why did this retraining job run at 2am" and need to trace it back to the API call, user, and request that triggered it — which is exactly the kind of reconstruction the audit/lineage requirements (§11.4, §11.6) depend on being possible.
- **`logging_middleware.py`** — structured access logging (method, path, status, latency, correlation ID).
- **`error_handler_middleware.py`** — the single place that catches everything raised out of `exceptions/` (Section 5.4) and converts it into a consistent JSON error envelope. No endpoint hand-rolls its own error response shape.
- **`rate_limit_middleware.py`** — protects shared compute from a single tenant's runaway usage. This is the API-layer half of the cost-control story the PRD flags as a named business risk (§19.2: "usage-based costs are volatile... a purely per-seat model would leave InsightAI exposed to heavy users consuming disproportionate compute at a fixed price").
- **`cors_middleware.py`** — explicit origin allow-listing between the frontend and API, rather than a permissive wildcard.

### 5.4 `exceptions/`

```
exceptions/{base_exception, domain_exceptions, http_exceptions}.py
```

Three layers, intentionally: `domain_exceptions.py` defines business-rule failures in framework-agnostic terms (`InsufficientDataError`, `LeakageDetectedError`, `TargetNotLearnableError` — directly corresponding to the validation failures the PRD requires in §7.2). `http_exceptions.py` is the *only* place that knows how a domain exception maps to an HTTP status code and error payload. Services raise domain exceptions and never think about HTTP at all — which matters because services are also called from Celery workers (Section 6), where there's no HTTP response to shape in the first place. If a service raised `HTTPException` directly, it would be unusable outside a request context.

### 5.5 `events/` — Internal Event Bus

```
events/{dataset_events, event_bus, model_events}.py
```

This is easy to dismiss as unnecessary indirection inside a monolith — everything's in the same process, why not just call the next function directly? Two reasons:

1. **Decoupling producers from consumers that shouldn't know about each other.** When `dataset_service` finishes cleaning a dataset, it publishes `dataset.cleaned`. `eda_service` reacts to that event to kick off profiling; an audit listener reacts to the same event to write an audit-log row; a future notification listener could react to the same event to alert a subscriber. `dataset_service` doesn't import or know about any of them. Add a new reaction to "a dataset was cleaned" and you add a new listener — you don't touch `dataset_service` at all.
2. **This is the second, cheaper seam for future service extraction**, alongside `ml_interface` (Section 7.1). Modules that communicate by publishing typed events rather than calling each other's functions directly can be moved to separate processes later by swapping the in-process bus implementation for a real message broker (the PRD's target architecture already anticipates Kafka, §14.4) — without touching a single call site. We're paying a small amount of indirection now specifically to avoid a rewrite later.

`model_events.py` (`model.deployed`, `model.drift_detected`, `model.performance_decayed`) is what connects `ml/insightai_ml/drift/` to `app/jobs/drift_check_job.py` and ultimately to the incremental-vs-retrain decision framework (PRD §7.7) — the event is the trigger; the job/service pair is what acts on it.

---

## 6. Asynchronous and Background Processing

### 6.1 `jobs/` vs `workers/` — Why Both Exist

```
jobs/{cleanup_job, drift_check_job, scheduled_retraining}.py
workers/{celery_app, notification_worker, report_worker, training_worker}.py
```

This is the same separation of concerns as "endpoints are thin, services hold logic," applied to background work:

- **`jobs/` holds the actual logic** — what a cleanup pass does, what a drift check computes, what triggers a retraining evaluation. These are plain, testable classes/functions with no dependency on Celery's task-decorator API.
- **`workers/` holds the Celery wiring** — `celery_app.py` configures the broker/backend (Redis); `training_worker.py`, `report_worker.py`, and `notification_worker.py` are thin `@task`-decorated wrappers that invoke the corresponding job or service and handle Celery-specific concerns (retries, backoff, task routing).

Why bother separating them: the queueing mechanism is an infrastructure detail, and infrastructure details change. The roadmap already names Celery's eventual replacement for complex, cross-workflow scheduling (Airflow-class orchestration, once the Workflow Builder's own scheduler hits its limits — see the roadmap's extraction-trigger appendix). If job logic were written as Celery tasks directly, migrating off Celery would mean rewriting business logic. Because the logic lives in `jobs/` and workers are a thin adapter, migrating the *scheduling mechanism* later touches `workers/` only.

`drift_check_job.py` and `scheduled_retraining.py` are the concrete implementation of PRD §7.7's decision framework — `drift_check_job` computes the drift/performance-decay signals, `scheduled_retraining` implements the resulting decision table (no action / incremental update / full retrain-to-shadow), with the human-approval gate for full-retrain promotion enforced at the service layer, not inside the job itself (a job shouldn't be the thing deciding it's allowed to promote itself to production).

### 6.2 Celery + Redis

Training runs and report generation are long-running (minutes, sometimes longer) and must never block a request/response cycle. This is a direct, deliberate implementation of the API design principle in PRD §14.6: long-running operations use a submit → poll → retrieve pattern (see the illustrative `POST /v1/training-jobs` → `202 Accepted` → `GET .../job_id` contract in §22.3), never a long-held synchronous connection. The API layer's job is to validate the request, enqueue it, and return immediately with a poll URL.

Redis is the broker. In local dev (`docker-compose`) it also backs the rate limiter and a cache layer — one piece of infrastructure serving three purposes, which is the right amount of infra for this stage rather than standing up three separate systems before any of them are under real load.

Four worker types map directly onto the four kinds of async work the product actually needs today: `training_worker` (compute-heavy — and, per Section 2, the first candidate for extraction into its own service once training-job volume justifies it), `report_worker` (Report Generation Agent execution, §13.8), `notification_worker` (alerting — drift alerts, workflow-failure notifications per §9.5), and the periodic-beat-scheduled jobs (`cleanup_job`, `drift_check_job`) that don't need a dedicated worker type of their own.

---

## 7. The ML Boundary

This section covers the single most consequential structural decision in the codebase after the monolith-vs-microservices call itself.

### 7.1 `ml_interface/` — The Seam Between Product and ML

```
ml_interface/{feature_client, inference_client, model_loader}.py
```

`backend/app` never imports `ml/insightai_ml` directly from a service or endpoint. Everything ML-shaped goes through this narrow interface. Two reasons:

1. **Dependency-footprint isolation.** `ml/insightai_ml` pulls in `xgboost`, `lightgbm`, `prophet`, `shap`, and (for the fraud autoencoder) a deep-learning framework — a heavy, slow-to-install dependency tree that has nothing to do with serving a dashboard request or handling a login. If `backend/app` imported `ml/` directly and pervasively, every API server instance would carry that entire dependency tree just to occasionally call a predictor. Routing everything through `ml_interface` means the web-serving process's dependency footprint stays lean, and the heavy ML dependencies are only required where `ml_interface`'s concrete implementation actually needs them (today: in-process; later: inside the extracted ML service's own container).
2. **This is the literal, pre-built seam for the roadmap's first service extraction.** Because `feature_client` and `inference_client` are already narrow, typed interfaces rather than direct imports scattered across a dozen services, extracting `ml/` into its own deployed service later is a matter of swapping their implementation from an in-process function call to an HTTP or gRPC call — with **zero changes required anywhere else in `backend/app`**. This is what "the modular monolith preserves the option to extract a module later" (Section 2) looks like as actual code, not just a stated intention.

`model_loader.py` specifically handles caching a versioned model (pulled from the registry, backed by `ml/model_store/` and S3) in memory so `inference_client` doesn't reload weights from disk/S3 on every single prediction request — a straightforward but important performance detail once inference volume grows past trivial.

### 7.2 The `ml/insightai_ml` Package — Why It's a Separate Top-Level Package

`ml/` sits next to `backend/` and `frontend/` at the repo root — it is **not** `backend/app/ml`. This is deliberate, for three reasons:

- **Different release cadence.** Model and pipeline code (a new feature-engineering transform, a tuned hyperparameter search space, a new explainability method) changes on its own schedule, independent of API changes, and benefits from its own versioning and its own test suite (`ml/tests/`) gating changes before they reach `backend/app` at all.
- **Reusable outside the web server.** `ml/insightai_ml` is imported by `backend/app` through `ml_interface`, by Celery workers directly (training/inference happen inside `training_worker`, not inside the request-handling process), and by data scientists working in `notebooks/` — none of which should need to pull in FastAPI, Pydantic-for-web, or any HTTP-serving dependency just to run a model.
- **It's the direct code home of the PRD's Agent Roster (§13.2).** This mapping is worth spelling out explicitly, because it's what makes the ML package's internal organization legible against the product spec rather than looking like an arbitrary pile of ML code:

| `ml/insightai_ml/` subpackage | PRD Agent / Section | What it owns |
|---|---|---|
| `eda/` | EDA Agent (§13.3) | Profiling, correlation/distribution/outlier analysis, the structured "findings" object |
| `eda/report_generator.py`, frontend `charts/` | Visualization Agent (§13.4) | Chart-type selection logic and rationale |
| `feature_engineering/` | Feature Engineering Agent (§13.6) | Templated + provenance-tagged feature generation (§7.4) |
| `churn/`, `clv/`, `fraud/`, `forecasting/`, `segmentation/` | Model Selection, Training, Evaluation Agents (§13.7) | One subpackage per ML vertical, each with `trainer.py`, `predictor.py`, and model-family files — the concrete implementation of the algorithm-shortlist table in §7.5 |
| `evaluation/` | Evaluation Agent (§13.7) | Leaderboard metrics, cross-validation |
| `explainability/` | Evaluation Agent (§13.7) / §7.6's mandatory explainability requirement | SHAP-based feature importance, per-prediction local explanations, model-card generation |
| `drift/` | Monitoring Agent (§13.10) | Data-drift and concept-drift detection (§7.7's signal #1 and #3) |
| `registry/`, `tracking/` | Model Registry & lineage (§11.6, §14.7) | Versioning, experiment tracking, `ModelVersion` lineage foreign keys |
| `llm/` | Report Generation Agent (§13.8) + NL query surface (§8) | `chat_agent.py`, `sql_generator.py`, `query_executor.py`, `context_builder.py`, and `guardrails.py` |
| `pipelines/` | Orchestration Layer (§13.11), scoped to ML | `training_pipeline`, `inference_pipeline`, `retraining_pipeline`, `eda_pipeline` — what `jobs/`/`workers/` and `ml_interface` actually invoke |
| `data_engineering/` | Dataset Validation & Cleaning (§7.2–§7.3) | Cleaning, encoding, ingestion, schema inference, validation — reusable independent of any specific ML vertical |
| `common/` | — | Shared exceptions, I/O, logging, constants — prevents ten subpackages from each reinventing `io_utils.py` |

`llm/guardrails.py` deserves a specific callout: it's the concrete implementation of the prompt-injection mitigation the PRD names explicitly (§19.3) — "treat all data-source content as untrusted input to agents, never as instructions." Any text pulled from a connected data source (a free-text column, a customer's uploaded CSV) that flows into an LLM prompt passes through this module first, precisely because a connected dataset is an untrusted input surface, not a trusted instruction channel.

**One deliberate specialization worth naming explicitly:** the PRD's ML Experience (§7) describes a generic AutoML flow where a user names any target column and the platform figures out the rest. We've additionally pre-built five opinionated, high-demand verticals — churn, CLV, fraud, forecasting, segmentation — as accelerators on top of that generic flow, each with its own trainer/predictor and a pre-selected algorithm shortlist. This is the Model Recommendation shortlist logic (§7.5) made concrete and pre-wired for the five problem types that show up unprompted across nearly every enterprise analytics backlog (directly echoing §3.1's P3–P6 and the RetailCo scenario in §3.4), rather than making every customer discover that shortlist logic themselves from a blank canvas each time. The generic flow still exists underneath (a sixth, unlisted target column still goes through the same Model Selection Agent logic) — these five are the paved road, not the only road.

### 7.3 Model Registry and Experiment Tracking

`ml/mlruns/` and `ml/model_store/{staging, production, archive}/` are a lightweight, filesystem/S3-backed registry and experiment tracker for this stage — not a dedicated feature-store product. This is a direct, intentional application of the PRD's V1 sequencing (§14.3): the model registry and feature store are "implemented as tables/schemas within the metadata store and object storage for V1 (no dedicated feature-store product initially)," with a dedicated feature-store technology deferred until feature reuse across projects at scale actually justifies the added operational surface. `staging/production/archive` as plain directories (backed by S3 promotion in real environments) gives us the canary/shadow-deployment promotion flow required by §7.7 without adopting a heavier MLOps platform before we have the usage to justify it.

---

## 8. Data and Storage Strategy

Two fundamentally different kinds of data get two fundamentally different stores:

- **Postgres** — the system of record for *metadata*: users, organizations/teams/projects, dataset *metadata* (not the raw file), the model registry, predictions, and the audit log. This data is strongly relational (the entity graph in PRD §14.7 is full of foreign keys — `ModelVersion` → `DatasetVersion` → `WorkflowVersion` lineage chains, org → team → project → resource hierarchies) and needs transactional guarantees, particularly for anything touching RBAC or the audit log, where a lost or duplicated write is not an acceptable failure mode.
- **Object storage (S3 in production, MinIO locally)** — raw dataset files, model artifacts, and generated reports. Blobs don't belong in a relational database: they're far cheaper per GB in object storage, and the access pattern (fetch/store by key) doesn't need or benefit from Postgres's transactional machinery.

This split isn't a performance optimization bolted on later — it's the correct default from the start, because the two data shapes have genuinely different consistency requirements and cost profiles.

---

## 9. Local Development Environment (Docker Compose)

```
docker/{docker-compose.dev.yml, docker-compose.prod.yml, nginx.conf, postgres/init.sql}
docker-compose.yml   (root — default onboarding entrypoint)
```

- **`docker-compose.dev.yml`** is optimized for iteration speed: volume-mounted source (no rebuild-on-change), hot reload, verbose logging.
- **`docker-compose.prod.yml`** is intentionally closer to what Kubernetes will actually run in staging/production — built images rather than mounted source, production-equivalent env var wiring — so that "works in Docker Compose prod mode" is a meaningful signal before anything reaches a k8s manifest.
- **`nginx.conf`** plays the local stand-in for the API Gateway role a managed service (ALB, or the k8s Ingress controller) plays in real environments (§14.2's "API Gateway: auth, rate limiting, request routing" box). Keeping a reverse proxy in front of frontend + backend locally, even though the concrete implementation differs from production, keeps the two topologies conceptually aligned — nobody develops against a shape of system that doesn't exist anywhere else.
- **`postgres/init.sql`** handles first-run, deterministic bootstrap (enabling extensions like `pgcrypto`/`uuid-ossp`) that needs to exist *before* Alembic can run its first migration against a fresh database.

---

## 10. Deployment Architecture — Kubernetes (Kustomize)

```
k8s/base/{configmap, deployment-backend, deployment-frontend, deployment-worker,
           hpa, ingress, kustomization, secret, service-backend, service-frontend}.yaml
k8s/overlays/{dev, staging, production}/{kustomization, patch}.yaml
```

- **Kustomize over Helm, for now.** Kustomize needs no templating language, no chart-versioning discipline, no values-schema to maintain — `base/` stays plain, readable YAML, and each overlay expresses only the *diff* for that environment (replica counts, resource limits, environment-specific config). That's the right amount of tooling for one team running three environments off one codebase. Helm's added machinery earns its cost once there are multiple independently-versioned services each needing their own chart — which is exactly the point at which module extraction (Section 2) will make Helm worth reconsidering, not before.
- **`deployment-backend.yaml` and `deployment-worker.yaml` are already separate Deployments**, even though they're built from the same monolithic codebase and container image family. This is the cheapest possible way to express "Training/background work has a different compute and scaling profile than the interactive API" (the exact distinction the PRD names in §14.1) without yet paying for a fully separate service, repo, and deployment pipeline. The API scales on request concurrency (via `hpa.yaml`); the worker deployment scales — or should eventually scale — on queue depth, not HTTP traffic. Having them as separate Deployments today means that operational difference is already expressible, and it's a small step, not a rewrite, to eventually give `worker` its own image and repo entirely.
- **`ingress.yaml`** is the production entry point — TLS termination and routing, playing the role `nginx.conf` plays locally.
- **`overlays/{dev,staging,production}`** is the standard promotion path: the same base manifests, environment-specific patches only.

---

## 11. Infrastructure as Code (Terraform)

```
terraform/environments/{dev,staging,production}/{main.tf, terraform.tfvars}
terraform/modules/{vpc, iam, rds, eks, s3}/
```

- **Per-environment state, isolated by `environments/`.** A `terraform apply` in `dev` cannot touch `production` state — this is a deliberate blast-radius boundary, not just directory hygiene.
- **Modularized by resource type (`vpc`, `iam`, `rds`, `eks`, `s3`)** rather than one large `main.tf` per environment. This buys reusability (the same `vpc` module, parameterized differently per environment via `tfvars`) and reviewability — a pull request touching `modules/iam/` is self-evidently security-relevant in a way a monolithic Terraform file isn't.
- **These five modules map directly onto the target architecture's infrastructure needs** (PRD §14.2): `vpc` is the network isolation boundary that underlies multi-tenancy (§14.5); `eks` is the Kubernetes cluster hosting the monolith and workers (Section 10); `rds` is the Postgres metadata store (Section 8); `s3` is the object storage tier (Section 8); `iam` implements least-privilege service-to-service auth, called out explicitly as a Security NFR (§15).
- **Terraform exists from day one, even though V1 only deploys a monolith**, because the PRD is explicit on this point (§14.4): write infrastructure-as-code from day one "so that the *practice* of IaC is established early," even while the full multi-service Helm/Terraform topology implied by the target architecture is built incrementally, only as services are actually extracted. The module boundaries here are already drawn along the lines the eventual multi-service architecture will need — we're not speculatively building extra infrastructure, we're making sure the infrastructure we do need is organized correctly from the start.

---

## 12. Observability (Prometheus + Grafana)

```
monitoring/{alerting.md, prometheus/{alert_rules.yml, prometheus.yml},
            grafana/dashboards/{backend-overview.json, ml-model-performance.json}}
```

Two dashboards, and the distinction between them matters:

- **`backend-overview.json`** covers conventional infrastructure signals — request latency, error rate, throughput, queue depth. This is what satisfies the Reliability and Availability NFRs (§15) and is what a traditional on-call rotation would expect to see.
- **`ml-model-performance.json`** exists because of a warning the PRD states plainly (§15, Observability): *"a 'healthy' system that is silently producing low-quality agent outputs is a failure mode traditional infrastructure monitoring will not catch."* A model can be serving predictions with perfect latency and zero errors while being quietly, confidently wrong — drifted, decayed, or miscalibrated. This dashboard is where the drift and performance-decay signals from §7.7 and the per-agent evaluation/calibration tracking from §13.12 actually surface as first-class, on-call-visible signals, not something buried in a log line nobody's watching. Per §19.8, "the system is up" and "the system is producing correct output" are treated as genuinely different failure modes, each needing its own monitoring and — per `alerting.md` — potentially its own escalation path.

---

## 13. Testing Strategy

Testing is organized to mirror the layered architecture directly, which is what makes each layer's isolation (Sections 4 and 6) actually pay off:

- **`backend/tests/unit/{repositories, services, utils}`** — services are tested with repositories mocked (no DB needed, made possible by dependency injection, Section 5.2); repositories are tested against a real or in-memory test database with no service/HTTP layer involved. This is the direct payoff of keeping business logic out of endpoints and repositories: each layer can be proven correct in isolation, fast, without spinning up the whole stack.
- **`backend/tests/integration/{api, db}`** — real HTTP requests through the actual FastAPI app, and real queries against a real (test) Postgres instance. This is where we catch the class of bug that only shows up when the layers are actually wired together.
- **`tests/e2e/*.spec.ts`** (Playwright, top-level, not nested under `backend/`) — full-stack flows: `auth_flow`, `dashboard_flow`, `upload_and_predict_flow`. These exercise frontend + backend + `ml/` together and are, not coincidentally, exactly the user journeys the PRD tracks as business metrics under "objective completion rate" (§21.1) — if these specs are green, the thing the business actually measures is working.
- **`ml/tests/{unit, integration}`** — a separate suite for the ML package, gating any change to `ml/insightai_ml` before it can reach `backend/app` at all. Per the PRD's explicit risk framing (§19.1, §13.12), statistical-correctness bugs (a subtly wrong time-series split, a leakage-detection edge case) are treated as a distinct, higher-priority bug class from ordinary defects, precisely because they produce confidently wrong models rather than visibly broken ones. This suite is where the benchmark-dataset regression tests implied by that requirement live.

---

## 14. Framework and Technology Choices, Justified

| Choice | Why |
|---|---|
| **FastAPI** | Async-native (matters once LLM/chat endpoints and inference calls are I/O-bound waiting on `ml/` or external LLM APIs), builds directly on Pydantic (so `schemas/` is reused, not duplicated, for validation), and auto-generates an OpenAPI spec — which directly feeds the API-key programmatic access story (§11.5) and any future client SDK generation, for free. |
| **SQLAlchemy + Alembic** | The mature, de facto standard for this scale. No reason to reach for something more exotic (a query builder, a different ORM, a NewSQL store) before the current choice is actually earned out — consistent with the PRD's broader "commodity building blocks, don't reinvent them" philosophy (§14.4). |
| **Celery + Redis** | The simplest workable async task story for V1. The roadmap already names its eventual limits explicitly (cross-workflow DAG complexity is what eventually pulls in Airflow-class orchestration) — not adopting Airflow now is a documented, deliberate sequencing decision, not an oversight. |
| **Postgres** | Strongly relational entity graph (§14.7), transactional guarantees non-negotiable for RBAC/audit data. |
| **S3 / MinIO** | Cheapest, simplest store for blobs; MinIO gives local dev an S3-compatible target with zero cloud dependency. |
| **Kustomize (not Helm, yet)** | See Section 10 — right-sized for one team, one codebase, three environments. |

---

## 15. What This Architecture Deliberately Does Not Do Yet

Worth stating plainly, because it's easy to look at this tree and wonder if it's "the 37-service vision, built halfway." It isn't. This tree has:

- **No service mesh, no per-agent microservice, no Kafka, no dedicated feature-store product, no Airflow.** Every one of these is named explicitly in the PRD's roadmap as a V2/V3, earned-later decision (§14.4), not an oversight here.
- **No multi-region deployment.** One cluster per environment, for now — the `vpc`/`eks` Terraform modules could support it later, but nothing here builds it speculatively.
- **No literal microservices split**, even though `ml_interface`, the event bus, the repository pattern, and the Terraform module boundaries are all already drawn as if a split were coming — because it is, eventually, once usage tells us where.

This backend tree **is** the MVP/V1-phase architecture from the product roadmap, module for module — not a scaled-down attempt at the full target architecture, but the right-sized slice for this stage, built with the seams that make the *next* stage cheap.

---

## 16. Closing Summary

Every piece of indirection in this tree that might look like over-engineering at first glance — the repository pattern, the DI container, the internal event bus, `ml_interface` as a narrow boundary instead of direct imports, the `jobs`/`workers` split, Terraform modules already shaped like a future multi-service topology — exists for exactly one reason: **it's far cheaper to draw a seam now, while the system is small and one team owns all of it end to end, than to discover you need that seam later, under production load, after two years of code has grown across where the boundary should have been.**

That's the concrete, code-level expression of the PRD's central architectural bet (§14.1: modular monolith, microservices as earned) and its adjacent warning about governance (§11.1: retrofitting RBAC and audit logging onto a system not designed for them is materially more expensive than designing for them from the start). Nothing in this backend is built for a scale we don't have yet. Everything in this backend is built so that reaching that scale later is an extraction, not a rewrite.