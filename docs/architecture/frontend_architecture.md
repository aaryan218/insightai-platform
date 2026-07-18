# Frontend Architecture — InsightAI Platform

*Location in repo: `docs/architecture/frontend_architecture.md`. Companion documents: `backend_architecture.md` (the API this app talks to), `system_overview.md`, `data_flow_diagram.md`. This document explains **why the frontend is built the way it is**, not just what each folder contains. Nothing in the tree structure is changed here — this is documentation, not a proposal.*

*A note on scope: the tree gives us file and folder names, not the contents of `package.json`. Where a decision depends on a specific library (state management, form validation, data-fetching cache) and that library isn't visible from the tree alone, I've said so explicitly rather than asserting it as fact — the same "state assumptions, don't paper over them" discipline the PRD applies to itself in §22.2.*

---

## 1. Purpose and Scope

The backend architecture doc made one idea load-bearing: draw the seams now, while the system is small, so splitting things apart later is an extraction, not a rewrite. The frontend follows the **same philosophy, adapted for the browser**: a strict layering between "what the user sees" (pages, components), "what the app knows and remembers" (state), and "how the app talks to the server" (the API client), enforced through folder boundaries and a couple of deliberately narrow choke points.

The short version, stated up front: **this frontend has the same three-layer shape as the backend — thin pages that call hooks, hooks that call one API client, and an API client that's the only thing in the entire app that knows an HTTP request exists.** Section 2 makes that parallel explicit, because once you see it, most of the folder structure below stops needing separate justification — it's the same pattern, applied once more.

---

## 2. Architectural Philosophy: The Same Layering Idea, Adapted for the Browser

On the backend, the rule is: **API → Service → Repository → DB**, one-way dependencies, no layer skipped. On the frontend, the direct analogue is:

| Backend | Frontend | Shared Job |
|---|---|---|
| `api/v1/endpoints/*.py` | `pages/*/*.tsx` | Thin. Wire up the URL/route, call exactly one hook or service method, render the result. No business logic. |
| `services/*.py` | `hooks/*.ts` | Own the orchestration: what to fetch, when to refetch, how to combine multiple calls, what "loading"/"error"/"success" actually means for this screen. |
| `repositories/*.py` | `services/apiClient.ts` | The single choke point that actually knows how to talk to the outside world (SQL for the backend, HTTP for the frontend). Everything above it is ignorant of the transport details. |
| `db/` (Postgres) | The InsightAI backend API | The actual source of truth. |

This isn't a coincidence and it isn't decoration — it's the same reasoning applied twice: **a page that fetches data directly, and a repository that contains business rules, fail for the same reason** — they can't be tested or replaced independently, and a change to "how we call the API" (add auth headers, retry on 401, switch base URLs per environment) has to be hunted down across every file that made its own `fetch()` call instead of living in one place. Keep reading with this table in mind; most of Sections 5–8 are just this idea worked out folder by folder.

---

## 3. System Component Map

```
┌───────────────────────────────────────────────────────────────────┐
│                          Browser (SPA)                                               │
│                                                                                    │
│   main.tsx  →  App.tsx  →  routes/AppRoutes.tsx                                   │
│                                  │                                                  │
│                     ┌────────────┴────────────┐                                     │
│                     ▼                         ▼                                      │
│              layouts/*                  pages/{auth,chat,churn,                     │
│         (AuthLayout,                     clv,dashboard,datasets,                     │
│          AppLayout, ...)                 forecasting,fraud,reports,                   │
│                     │                     segmentation,settings}/                     │
│                     │                          │                                       │
│                     ▼                          ▼                                       │
│              components/layout/          components/{common,charts,                    │
│         (PageHeader, Grid, ...)           dashboard,forms}/                            │
│                                                 │                                      │
│                                                 ▼                                      │
│                                            hooks/*.ts   ◄──── contexts/AuthContext.tsx │
│                                     (useDatasets, useChurnModel,    (identity, rarely   │
│                                      useTrainingJob, ...)            changes, read       │
│                                                 │                     everywhere)          │
│                                                 │                    store/index.ts          │
│                                                 │              (ephemeral client/UI state,     │
│                                                 │               sidebar open, active draft)      │
│                                                 ▼                                                  │
│                                     services/apiClient.ts                                            │
│                              (the ONLY thing that knows an HTTP                                        │
│                               request exists — auth headers, base                                       │
│                               URL, retries, error normalization,                                          │
│                               job-polling helper for async endpoints)                                       │
└───────────────────────────────────────┼───────────────────────────────────────────────────────────────┘
                                        │  HTTPS, JSON (types/ mirrors backend schemas/)
                                        ▼
                          InsightAI Backend API  (see backend_architecture.md)
```

Everything below explains one box in this diagram.

---

## 4. Build Tooling and Project Setup

### 4.1 Vite, not Create React App / a hand-rolled Webpack config

Vite's native ESM dev server gives near-instant cold starts and hot-module-reload regardless of app size — which matters here specifically because the `pages/` tree already spans eleven verticals (Section 5.3) and will only grow (the Workflow Builder and Notebook surfaces from the PRD, §9–§10, aren't in this tree yet — see Section 16). A bundler that gets slower as the page count grows is a tax that compounds; Vite's dev-server architecture (esbuild-based pre-bundling, native ESM) is specifically designed not to. Production builds go through Rollup under the hood, which is a mature, well-understood story for the actual deployed artifact.

### 4.2 Two `tsconfig` files, on purpose

`tsconfig.json` governs the application code that ships to the browser (`src/`). `tsconfig.node.json` governs tooling that runs in Node during the build itself (`vite.config.ts`, `postcss.config.js`, `playwright.config.ts`). These have different valid target environments — app code can assume a DOM exists; build tooling can't and shouldn't. Splitting the config is what lets `vite.config.ts` use Node APIs without the app code accidentally getting Node types in its autocomplete, and vice versa.

### 4.3 Tailwind + PostCSS

Utility-first styling, no CSS-in-JS runtime cost, no separate stylesheet-per-component to keep in sync with markup. `tailwind.config.ts` is where the actual design system lives as data (color palette, spacing scale, typography scale) rather than scattered across component files — which matters directly for the Accessibility NFR (§15 of the PRD): a colorblind-safe default chart palette (required by §13.4's Visualization Agent) is a lot easier to guarantee and audit as a handful of named tokens in one config file than as ad hoc hex codes wherever a chart happens to be styled.

### 4.4 Entry Point Chain: `index.html` → `main.tsx` → `App.tsx`

`index.html` is the single static shell Vite injects the bundle into. `main.tsx` is the one place React actually mounts to the DOM, wraps the tree in top-level providers (auth context, the global store, routing), and nothing else — it's intentionally boring. `App.tsx` is the top of the actual component tree: it renders `routes/AppRoutes.tsx` and nothing else. If `App.tsx` starts accumulating logic beyond "assemble the providers and render the router," that's a signal something belongs in a hook or a layout instead.

### 4.5 `Dockerfile`

A multi-stage build is the expected shape here: a Node stage that runs `vite build` and produces static assets, handed off to a minimal static-file-serving stage (nginx or equivalent) for the actual runtime image — the same split of concerns as the backend's `Dockerfile`, just applied to "build once, serve statically" instead of "run a Python process." This is what `k8s/base/deployment-frontend.yaml` and `service-frontend.yaml` (see `backend_architecture.md`, Section 10) actually deploy: a lightweight static server, not a Node runtime.

---

## 5. Routing and Application Shell

### 5.1 `routes/AppRoutes.tsx` — One Route Registry

Every route in the app is registered in exactly one file, the same way `api/v1/router.py` is the one place every backend route is assembled (see `backend_architecture.md`, Section 4.1). This means the full navigable surface of the product is visible in one file, and adding a new page never means hunting through `App.tsx` or scattering `<Route>` declarations across the tree. It's also where route-level guards live — e.g., redirect to `pages/auth` if `AuthContext` has no valid session — kept out of individual pages so no page has to remember to check auth itself.

### 5.2 `layouts/` vs `components/layout/` — Two Similarly Named Things, Deliberately Different Jobs

This is a common source of "wait, where does this go" confusion in real codebases, so it's worth being explicit about the distinction rather than letting it stay implicit:

- **`layouts/`** (top-level) — full-page chrome wrapped around a *group* of routes: an `AuthLayout` (centered card, no nav) for `pages/auth`, and an `AppLayout` (sidebar + top nav + content area) for everything behind login. `AppRoutes.tsx` picks a layout per route group; a layout answers "what does the frame around this whole section look like."
- **`components/layout/`** — smaller, reusable *structural* building blocks used *inside* a layout or a page: a `PageHeader`, a responsive `Grid`, a `SplitPane`. A layout answers "what's the frame"; `components/layout/` pieces answer "how do I arrange things within that frame, consistently, wherever I need to." If this distinction ever gets blurry in practice, that's a sign one of the two folders is accumulating things that belong in the other — worth a periodic sanity check, not a structural problem today.

### 5.3 `pages/` — One Folder Per Capability, Mapped Directly Onto the Product

```
pages/{auth, chat, churn, clv, dashboard, datasets,
       forecasting, fraud, reports, segmentation, settings}/
```

This mirrors `backend/app/api/v1/endpoints/` almost exactly (`auth.py`, `chat.py`, `churn.py`, `clv.py`, `dashboard.py`, `datasets.py`, `forecasting.py`, `fraud.py`, `reports.py`, `segmentation.py`) and, one level up, mirrors the PRD's own objective surfaces (§6.3: create a dashboard, train a model, generate a report, and so on) and the five pre-built ML verticals discussed in `backend_architecture.md` §7.2. A few deliberate gaps are worth naming, because an absence in a mapping like this is a decision, not an oversight:

- **No `pages/eda/`.** The automatic analysis flow (§6.2 of the PRD) isn't a destination the user navigates to — it's what happens *inline*, automatically, the moment a dataset lands in `pages/datasets`. EDA results are a section of the datasets page, not a page of their own.
- **No `pages/models-registry/`.** Model registry data (versions, lineage, staging/production status) is surfaced *within* each vertical's page — the churn page shows the registry entries for churn models — rather than as one global, undifferentiated model list. A data scientist thinking about churn models wants churn context (features, target, business metric) alongside the registry entry, not a generic table stripped of that context.
- **No `pages/health/` or `pages/users/`.** `health` has no frontend surface at all (it's an ops/infra endpoint, consumed by load balancers and monitoring, not humans in the browser). `users` folds into `pages/settings` rather than standing alone, since user management is one settings concern among several (org membership, API keys, billing), not a first-class navigation destination on its own.

---

## 6. State Management Strategy

This is the section most worth reading carefully, because getting it wrong is the single most common way a React app accumulates bugs that are expensive to trace — data going stale, one component's update not being reflected in another, a "loading" spinner that never resolves because two components independently decided they owned the same fetch.

The rule this codebase follows: **there are three different kinds of state, and each one has exactly one legitimate home.**

| Kind of state | Example | Lives in | Why not elsewhere |
|---|---|---|---|
| **Identity / session** | Current user, auth token, org context | `contexts/AuthContext.tsx` | Needed by almost every component in the tree (route guards, the API client's auth header, the navbar), changes rarely (login/logout), and React Context's re-render cost is a non-issue for something that updates a handful of times per session. |
| **Ephemeral client/UI state** | Sidebar collapsed, active workflow-builder draft, which modal is open | `store/index.ts` | Needs to be read and written frequently from components that aren't necessarily parent/child (Context would force unrelated re-renders across the tree); doesn't need to persist past a page refresh; has nothing to do with the server. |
| **Server state** | Datasets, model results, dashboard KPIs, training job status | **`hooks/`, colocated with the fetch — not `store/` and not `contexts/`** | See below — this is the one that actually matters. |

**Server state is deliberately kept out of the global store.** Data that lives on the server (a dataset's profile, a model's leaderboard, a dashboard's KPIs) is not "app state" in the same sense the sidebar-open flag is — it can go stale the moment another user or another tab changes it, it needs to be refetched, deduplicated across components that ask for the same thing simultaneously, and eventually garbage-collected once nothing's using it. Putting it in a hand-rolled global store means reinventing all of that — cache invalidation, refetch-on-window-focus, request deduplication — by hand, which is exactly the kind of thing that looks fine for the first three pages and turns into a maintenance burden by the eleventh. This tree's shape (many `hooks/*.ts` files, one per data need, rather than a monolithic store slice per entity) is consistent with a query-cache-based data-fetching library (something in the React Query / TanStack Query family) rather than hand-managed fetch-and-`useState`. If the actual `package.json` says otherwise, that's worth reconciling explicitly — see the assumptions note at the top of this document — but the folder shape strongly implies "hooks own their own fetch and cache," not "one big store owns all server data."

This split also directly supports the backend's async job pattern (`backend_architecture.md` §6.2, and PRD §14.6/§22.3's submit → poll → retrieve contract): a hook like `useTrainingJob(jobId)` can own its own polling interval and expose a clean `status` to the page, without that polling logic leaking into a global store that every other part of the app would need to know how to ignore.

---

## 7. `hooks/` — The Orchestration Layer

This is the frontend's direct equivalent of the backend's `services/` layer (Section 2's table), and it's where most of the actual frontend "business logic" lives:

- **One hook (or a small family of hooks) per data need**, not one hook per component. `useDatasets()`, `useChurnModel(modelId)`, `useTrainingJob(jobId)` are each usable from any page or component that needs that data, without duplicating fetch/cache/error logic.
- **Hooks own the shape of "loading / error / success"** for whatever they wrap, so pages don't each reinvent their own loading-state handling. A page calls a hook and gets back something like `{ data, isLoading, error }` — the same discipline the backend's services apply by raising typed domain exceptions (`exceptions/domain_exceptions.py`) rather than letting every endpoint invent its own error shape.
- **Hooks are where multi-call orchestration happens.** A dashboard page might need KPI data, chart specs, and NL explanations from three different backend calls; the hook layer is where those get combined into one coherent object the page renders, rather than the page itself juggling three separate loading states.
- **Hooks own polling for async backend jobs** (Section 6, last paragraph) — the page doesn't know or care that a training job is implemented as submit-then-poll on the backend; it just sees a status that eventually resolves.

Keeping this logic in `hooks/` and out of `pages/` is what makes hooks independently testable (mount a hook in isolation, mock `apiClient`, assert on its returned state) without needing to render a full page — the same payoff the backend gets from keeping business logic in `services/` and out of `api/v1/endpoints/`.

---

## 8. `services/apiClient.ts` — The Single Data-Access Chokepoint

Every HTTP call in the entire application goes through this one file. No hook, no component, no page ever calls `fetch()` or an HTTP library directly. This buys the same thing the backend's repository layer buys for tenant scoping (`backend_architecture.md` §4.4): **one place where cross-cutting request concerns are structurally guaranteed, not hoped for.**

Concretely, this is where the following live, once, instead of being duplicated wherever a request happens to be made:

- **Auth header injection** — reading the token from `AuthContext` and attaching it to every request, so no hook has to remember to do this itself.
- **Base URL / environment configuration** — one place that knows whether it's talking to local Docker Compose, staging, or production.
- **Error normalization** — converting whatever shape the backend's `error_handler_middleware` returns (see `backend_architecture.md` §5.3) into a consistent error type the rest of the app can handle uniformly, so a hook doesn't need to know the difference between a 422 validation error and a 500.
- **The job-polling helper** — a small utility for the submit → poll → retrieve pattern (PRD §14.6, §22.3), used by any hook that needs to watch a long-running backend job to completion, implemented once rather than reinvented per hook.
- **Retry/backoff for transient failures** — consistent with the backend's own fault-tolerance NFR (§15) for connector/agent failures; the frontend's counterpart is not hammering a flaky network with a fresh retry policy invented in every hook that happens to need one.

If the backend API's base path, auth scheme, or error envelope ever changes, this is the one file that needs to change. Every hook above it stays untouched — the same "swap the implementation, not the call sites" property `ml_interface/` gives the backend (`backend_architecture.md` §7.1).

---

## 9. Component Architecture

### 9.1 `components/common/` — The Design-System Primitives

```
common/{Button, Card, ErrorBoundary, Loader, Modal, Navbar, Sidebar, Table}.tsx
```

These are the "dumb" building blocks: no data fetching, no business logic, no knowledge of what a "dataset" or a "churn model" is — just props in, markup out. `Button`, `Card`, `Modal`, `Loader`, `Table` are the alphabet every other component composes from; keeping them free of domain knowledge is what lets them be reused identically across all eleven `pages/` verticals without any of them accidentally depending on, say, churn-specific logic. `Navbar` and `Sidebar` are the exception in that they *are* somewhat structural rather than purely presentational, but they still take their content (nav items, active route) as props rather than knowing about routing or auth themselves — that knowledge lives in the `layouts/` that place them (Section 5.2).

### 9.2 `components/charts/` — One Component Per Chart Type

```
charts/{BarChart, ForecastChart, HeatmapChart, LineChart, PieChart, ScatterPlot}.tsx
```

This directly mirrors the PRD's Visualization Agent (§13.4), whose job is chart-*type selection* with an explicit rationale — "bar chart chosen over pie chart because there are 14 categories." Having one component per chart type, each with a narrow, well-typed prop interface, is what makes that selection logic (living in a hook or the dashboard page, calling out to the backend's Visualization Agent for the recommendation) able to just pick a component and render it, rather than one giant configurable "Chart" component with a sprawling prop surface trying to be six chart types at once. `ForecastChart` gets its own component rather than being `LineChart` with extra props specifically because forecasts have a structural requirement `LineChart` doesn't — a confidence-interval band around the point estimate, a hard requirement per PRD §7.8 ("a point forecast without an interval is treated as an incomplete deliverable"). Baking that into a dedicated component means it's structurally impossible to render a forecast without the interval, the same way keeping `hashed_password` out of `UserResponse` (see `backend_architecture.md` §4.2) makes leaking it structurally impossible rather than a discipline problem.

Accessibility lives here too: colorblind-safe default palettes (§15 NFR, §13.4) are a property of these six components, defined once against the Tailwind design tokens (Section 4.3), not a setting an individual page has to remember to apply.

### 9.3 `components/dashboard/` and `components/forms/` — Feature-Specific Composite Components

These sit one level up from `common/`: they *do* know about the domain (a dashboard KPI card, a cleaning-plan approval form) but are still reusable across more than one page — a KPI-card component used both on the main dashboard page and inside a report preview, a form-field pattern used across `datasets`, `settings`, and wherever a cleaning plan (PRD §7.3's "propose, don't silently apply" pattern) needs a human to review and approve before it executes. `components/forms/` is the natural home for whatever validation library the app uses (visible in `package.json`, not the tree) to keep field-level validation consistent everywhere a form appears, rather than each page inventing its own validation approach.

### 9.4 `ErrorBoundary` and Resilience

`common/ErrorBoundary.tsx` deserves a specific callout because it's the frontend's direct implementation of a PRD requirement stated explicitly as a named anti-pattern to avoid (§15, Fault Tolerance): *"graceful degradation... a dashboard remains viewable if the Analytics Agent's NL-explanation call fails, rather than the whole dashboard failing to render."* Wrapping individual widgets (a chart, an NL-explanation panel, a KPI card) in their own `ErrorBoundary` rather than one boundary around the whole page is what makes one failed backend call a contained, visible failure in one card — not a blank white screen for the entire dashboard. This is a small component with an outsized job: it's the concrete reason "a common anti-pattern in AI-feature products is making the entire page depend on the AI call succeeding" (§15) doesn't happen here.

---

## 10. `types/` — The Frontend Half of the API Contract

`types/` holds the TypeScript interfaces that mirror the backend's `schemas/` layer (`backend_architecture.md` §4.2) — `Dataset`, `ChurnResult`, `TrainingJob`, and so on. This is the frontend's side of the same "two representations, on purpose" decision the backend makes between `models/` and `schemas/`: the wire contract is its own explicit, typed thing, not inferred ad hoc from whatever a `fetch()` call happens to return.

Worth naming as a real, live risk rather than glossing over it: **these types are currently a second, manually-maintained copy of the backend's Pydantic schemas**, which means they can drift — a backend field rename or addition doesn't automatically show up here. FastAPI already auto-generates an OpenAPI spec for other reasons (`backend_architecture.md` §14 — API-key programmatic access, future SDK generation); that same spec is the natural source for **generating** `types/` instead of hand-maintaining it, once the API contract stabilizes enough that codegen churn stops being noisier than the manual drift it would prevent. Flagging this here rather than silently assuming it's already solved, the same way the PRD's own §22.2 flags its own placeholder assumptions instead of treating them as settled fact.

---

## 11. Styling System

Tailwind's utility classes plus `tailwind.config.ts`'s design tokens (Section 4.3) are the entire styling system — there's no separate CSS-in-JS runtime, no `.module.css` files scattered next to components, no global stylesheet fighting for specificity. The trade-off, stated plainly: utility-class markup is more verbose in the JSX than a semantic class name would be, in exchange for the design system being enforced by the config file (a spacing or color value literally isn't available unless it's a token) rather than by convention that's easy to drift from over time. For a product with this many distinct verticals (Section 5.3) needing to look and feel like one coherent app rather than eleven separately-styled features, enforcing the token constraint at the tooling level is worth the verbosity.

---

## 12. `utils/` and `constants/`

Both are intentionally small and boring: `utils/` holds pure, side-effect-free helper functions (date formatting, number formatting for currency/percentages in the CLV and forecasting pages, a debounce helper); `constants/` holds fixed values that would otherwise be magic strings scattered across the app (route paths, chart color tokens, API status enums shared with the `types/` layer). Neither should ever contain business logic that decides *what* the app does — that belongs in `hooks/` (Section 7). A utility function formats a number; a hook decides which number to fetch and what it means. Losing that distinction is how a `utils/` folder quietly turns into an undocumented second services layer.

---

## 13. Testing Strategy

```
frontend/tests/{e2e, unit}
frontend/playwright.config.ts
(root) /tests/e2e/{auth_flow, dashboard_flow, upload_and_predict_flow}.spec.ts
```

There are deliberately **two tiers** of end-to-end testing in this repo, and the distinction matters:

- **`frontend/tests/e2e/`** — Playwright specs scoped to the frontend alone, typically run against a mocked or lightweight-stubbed backend. These are fast, run in the frontend's own CI pipeline on every PR, and catch UI-layer regressions (a broken route, a form that doesn't validate, a chart that doesn't render) without needing a full backend + ML stack spun up.
- **Root `/tests/e2e/`** (documented in `backend_architecture.md` §13) — true full-stack journeys (`auth_flow`, `dashboard_flow`, `upload_and_predict_flow`) exercising frontend, backend, and `ml/` together against a real environment. These are slower and live at the repo root specifically because they're not "frontend tests" or "backend tests" — they're product tests, and they're what the PRD's "objective completion rate" business metric (§21.1) is actually measuring under the hood.

`frontend/tests/unit/` covers components and hooks in isolation — a hook tested with `apiClient` mocked (no network, no backend needed, same benefit the backend's `tests/unit/services/` gets from mocking repositories), and presentational components tested with React Testing Library against their prop contracts. This mirrors the backend's layered testing strategy directly: unit tests per layer, in isolation, with integration/e2e reserved for proving the layers actually work wired together.

---

## 14. Docker and Deployment

The frontend ships as a static build served by a lightweight web server (Section 4.5), deployed as its own Kubernetes `Deployment`/`Service` pair (`deployment-frontend.yaml`, `service-frontend.yaml` — see `backend_architecture.md` §10) sitting behind the same `ingress.yaml` that routes to the backend API. This is the cleanest possible scaling story for a SPA: it's stateless, cacheable, and horizontally scalable independent of the backend's own scaling needs (which, per `backend_architecture.md` §10, already scale differently between the API and worker deployments) — the frontend never needs the backend's request-concurrency or queue-depth signals to decide its own replica count.

---

## 15. Accessibility

WCAG 2.1 AA is a stated launch requirement in the PRD (§15 NFR), not a post-launch retrofit, and it shows up concretely in a few specific places in this tree: colorblind-safe chart palettes baked into `components/charts/` (Section 9.2) rather than left to per-page discretion, keyboard navigability as a property of `components/common/` primitives (a custom `Modal` or `Sidebar` built without keyboard-trap handling would violate this for every page that uses it, which is exactly why it's enforced once, at the primitive level, rather than per usage), and semantic structure enforced through `layouts/` and `components/layout/` rather than every page inventing its own heading hierarchy. Building this into the shared, reused layers (`common/`, `charts/`, `layouts/`) is what makes "accessible by default" true across all eleven verticals simultaneously, instead of being a checklist applied unevenly page by page.

---

## 16. What This Architecture Deliberately Does Not Do Yet

Worth stating plainly, the same way the backend doc does: this tree is the frontend for the **MVP/V1-phase product**, not a scaled-down attempt at the PRD's full vision.

- **`components/dashboard/`, `components/forms/`, and `components/layout/` are present but not yet fleshed out** in this snapshot of the tree — scaffolded ahead of need because the folder boundary is cheap to draw now and expensive to retrofit later (the same reasoning behind the backend's Terraform module boundaries, `backend_architecture.md` §11), not because they're unimportant.
- **No Workflow Builder or Notebook surface yet.** The PRD's Visual Workflow Builder (§9) and Notebook Experience (§10) are V1-roadmap items (per the product roadmap's Phase 2/Version 1 scope) that don't have a `pages/` entry in this tree yet — when they land, expect `pages/workflows/` and `pages/notebook/` as new, self-contained additions, following the exact same one-folder-per-capability pattern already established rather than requiring any change to the surrounding architecture.
- **No server-side rendering, no meta-framework (Next.js/Remix).** This is a client-rendered SPA behind an authenticated app shell — there's no SEO requirement for logged-in analytics dashboards, so the added complexity of SSR buys nothing here. Worth revisiting only if a genuinely public, unauthenticated, SEO-sensitive surface (a public status page, marketing site) ever needs to live in this same app — which argues for keeping that hypothetical surface in its own project rather than SSR-ifying this one.
- **No micro-frontend split**, even though `pages/` is already organized as eleven cleanly separable verticals. The same "don't decompose before real usage tells you where the pressure is" reasoning from `backend_architecture.md` §2 applies here: if one vertical (say, the chat/NL-query surface) ever needs an independent deploy cadence or a different team boundary, `pages/chat/` plus its own `hooks/` and `apiClient` usage is already isolated enough to extract without a rewrite. Nothing here is built for a scale this product doesn't have yet.

---

## 17. Closing Summary

The frontend and backend are built from the same underlying belief, expressed in two different languages: **a strict, one-way layering (thin surface → orchestration logic → single data-access choke point) is what makes a codebase testable in pieces, safe to change in one place, and cheap to re-architect later precisely because so little of it needs to change when the day comes.** `pages/` → `hooks/` → `apiClient.ts` is not a smaller, less-rigorous version of `endpoints/` → `services/` → `repositories/` — it's the identical discipline, and reading one half of this stack should make the other half feel unsurprising. That consistency is itself a design choice: an engineer moving from a backend service to a frontend hook shouldn't have to learn a new mental model to know where a piece of logic belongs.