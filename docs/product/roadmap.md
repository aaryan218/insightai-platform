# InsightAI — Product Roadmap

*Derived from the InsightAI PRD (v1.0), Section 20, cross-referenced with Sections 3, 4, 14, 18, and 21. This is a working roadmap, not a fixed schedule — see "How This Roadmap Works" below.*

---

## How This Roadmap Works

- **Phases are gated by evidence, not by calendar.** A phase ends when its milestones are met, not on a fixed date. The team should extend a phase rather than advance against unmet milestones.
- **Each phase proves one falsifiable hypothesis** before the next phase's investment is committed. This is the same philosophy behind the modular-monolith decision (PRD §14.1) and the "build the data-engineering stack only when earned" principle (PRD §14.4): build the narrowest thing that proves the value, and let real usage justify the next increment of complexity.
- **Every phase entry below has four parts:** Engineering Priorities, Expected Capabilities at Exit, Dependencies, and Measurable Milestones (the exit gate).
- **No calendar dates are attached to phases**, deliberately — see PRD §20.1. Advancing on schedule rather than on evidence is how roadmaps quietly turn into the "37-service, everything-at-once" architecture this roadmap is explicitly designed to avoid.

---

## Roadmap at a Glance

| Phase | Proves | Headline Deliverable | Exit Gate |
|---|---|---|---|
| **0 — Research** | The automated-analysis experience can hit a real trust bar | EDA + Visualization Agent prototype, scored against a benchmark suite | ≥85% EDA finding-precision; ≥90% chart-selection appropriateness |
| **1 — MVP** | The BI pillar (auto-analysis → dashboard) delivers real value fast | CSV/Snowflake → automatic analysis → shared dashboard, for design partners | 5–10 design partners on real data; ≥1 paid pilot |
| **2 — Version 1** | The ML pillar works end-to-end alongside BI | CSV/warehouse → deployed, monitored model; Notebook; basic Workflow Builder | Majority of tracked sessions hit deployment-time target; Business-tier retention tracked |
| **3 — Version 2** | The platform is enterprise-ready and the "AI Data Team" vision is real, not aspirational | Full RBAC/audit/SSO; incremental-vs-retrain automation in production; Guided Mode | ≥1 Enterprise contract closed; SOC 2 Type II observation started |
| **4 — Version 3** | The platform scales to large, compliance-heavy enterprises and an ecosystem | Expansion connectors; first data-engineering-stack components; Marketplace foundation | SOC 2 Type II certified; multiple VPC deployments live; first 3rd-party Marketplace workflow |
| **Beyond V3** | Full "AI Data Team" vision at scale | Majority of agent roster independently deployed; full data-eng stack where earned; mature Marketplace | Not pre-committed — evidence-gated, phase by phase |

---

## Phase 0 — Research

**Goal:** Validate that the core automatic-analysis experience (PRD §6.2) can meet its quality and trust bar *before* any product surface is built around it.

**Engineering Priorities**
- Build a throwaway prototype of the **EDA Agent** and **Visualization Agent** (§13.3–13.4) against a diverse benchmark set of real-world CSVs.
- Establish the evaluation methodology (§13.12 / §15 Observability) — build the measurement instrument *before* building the thing it will measure.

**Expected Capabilities at Exit**
- A benchmark suite with known-correct findings across a diverse set of datasets.
- A working (non-production-quality) prototype that can be scored against that suite.

**Dependencies:** None — this is the starting phase.

**Measurable Milestones (Exit Gate)**
- EDA Agent finding-precision exceeds **85%** across the benchmark suite (starting target, to be recalibrated once real data exists).
- Chart-selection appropriateness (§13.4) judged correct in **≥90%** of benchmark cases.

---

## Phase 1 — MVP

**Goal:** Ship the narrowest end-to-end slice that delivers on the core promise (§3) for a single objective, to a small number of design-partner customers, and validate willingness to pay.

**Engineering Priorities**
- Core Platform API as a **modular monolith** (§14.1, §14.3).
- Connectors: CSV/Excel + **one** warehouse connector (Snowflake — market position per §16.2).
- Production-quality automatic analysis flow (§6.2).
- **One** full objective path end-to-end: *"create a dashboard"* (§8.2) — not all six objectives from §6.3.

**Expected Capabilities at Exit**
- User connects a CSV or Snowflake table → gets an automatic analysis (§6.2) → produces and shares a dashboard (§8.2) with NL explanations (§8.4).
- Explicitly **out of scope**: ML training, Workflow Builder, Notebook, RBAC beyond basic single-team sharing.

**Dependencies:** Research Phase's validated EDA/Visualization Agent quality bar.

**Measurable Milestones (Exit Gate)**
- 5–10 design-partner customers using the product on real (not sample) data.
- Automatic analysis flow meets the **<60s** performance target (§15) on real customer datasets, not just benchmark data.
- At least one design partner converts to a paid pilot.

**Personas served:** Priya (Business Analyst), Marcus (Data Analyst) — the two beachhead personas whose value is shortest to demonstrate (§4).

---

## Phase 2 — Version 1

**Goal:** Complete the core objective set from §6.3 and prove the second major value pillar — automated ML — alongside the BI pillar validated in MVP.

**Engineering Priorities**
- **Machine Learning Experience end-to-end** (§7: validation → deployment). *Excludes* the full incremental-vs-retrain automation (§7.7) — that ships in V2, once there's a large enough production-model population to make the policy meaningful.
- **Notebook Experience** (§10).
- **Basic Visual Workflow Builder** (§9) — Source, Transform, ML, and Action node categories only. Control Flow's full Approval Gate enforcement is deferred, though a simple manual-approval step ships as a minimum-viable safety gate.
- Remaining launch connectors (§12.1): Databricks, PostgreSQL, MySQL, SQL Server, REST APIs.
- **Professional** and **Business** pricing tiers (§18.2) — self-serve signup and billing.

**Expected Capabilities at Exit**
- Full "CSV/warehouse → deployed, monitored model" path (§7.9).
- Full "open a notebook for advanced work" path (§10).
- Reusable workflows across the four shipped node categories.

**Dependencies:** MVP's validated dashboard/BI pillar and initial paying customers.

**Measurable Milestones (Exit Gate)**
- Time from dataset connection to first deployed model meets its target for a **majority** of tracked customer sessions (§21.2).
- Business-tier retention tracked for the first cohort (§21.4).
- **Architecture trigger fires:** Training Agent extracted into its own service (§14.1's first concrete extraction trigger) once training-job volume justifies it.

**Personas served:** Adds Dana (ML Engineer) and Alex (Data Scientist) to Priya and Marcus.

---

## Phase 3 — Version 2

**Goal:** Complete the Enterprise readiness bar (§11) and the full agent roster's standing/monitoring capability (§7.7, §13.10), enabling the Enterprise sales motion to begin in earnest.

**Engineering Priorities**
- Full **RBAC**/org/team/project hierarchy + Approver role (§11.2–11.3).
- **Audit logs** (§11.4), **API keys** (§11.5), full **version history and lineage** (§11.6), **SSO** (§11.7).
- Full **incremental-vs-full-retrain decision framework** (§7.7) in production, now justified by V1's accumulated production-model population.
- **Architecture trigger fires:** Monitoring Agent extracted into its own service (§14.1's second concrete extraction trigger).
- **Guided Mode** (§6.4) — serves the SMB Owner/Operator persona.
- **Report Generation Agent** (§13.8) reaches its "forwardable to a VP" quality bar.

**Expected Capabilities at Exit**
- Enterprise tier sellable (§18.2), with SSO and compliance documentation in progress.
- Standing, monitored models and workflows — the "AI Data Team" vision (§5) becomes real, not aspirational.
- SMB Owner/Operator persona served via Guided Mode.

**Dependencies:** V1's production-model population (to tune §7.7's policy) and initial Business-tier customer base (to validate RBAC/audit against real organizational structures).

**Measurable Milestones (Exit Gate)**
- SOC 2 Type II observation period initiated (§15, Security).
- At least one Enterprise-tier contract closed.
- Incremental-vs-retrain framework's automatic actions show **zero** customer-reported incidents of inappropriate automatic promotion during the opt-in automatic-promotion pilot.
- Report Generation Agent output requires no human edit before distribution in **≥80%** of a sampled evaluation set.

**Personas served:** Adds Sam (BI/governance), VP persona (via Report Generation Agent), SMB Owner/Operator.

---

## Phase 4 — Version 3

**Goal:** Broaden connector and data-engineering depth to serve the Large Enterprise Analytics Org persona at scale, and begin building toward the Marketplace.

**Engineering Priorities**
- Expansion connectors from §12.4's anticipated list — prioritized by **demonstrated V2 customer demand**, not the full list at once.
- Data-engineering-stack components from §14.4, introduced **individually** as their specific triggers are met (most likely Airflow-class orchestration first, given multi-customer workflow complexity growth — see Appendix A below).
- **Dedicated/VPC deployment** option (§14.5) for the most compliance-sensitive Enterprise accounts.
- **Marketplace foundation** work — harden the extensibility interface (§13.13) for third-party use (§18.5).

**Expected Capabilities at Exit**
- Large Enterprise Analytics Org persona fully served (§4.2).
- At least one non-CSV/warehouse data-engineering pattern (e.g., a streaming/event-based source, §12.4) in production for a real customer use case.
- Marketplace interface stable enough for a small, curated set of early third-party or customer-authored workflows.

**Dependencies:** V2's enterprise feature set and compliance progress; sustained multi-tenant scale sufficient to justify §14.4's additional infrastructure.

**Measurable Milestones (Exit Gate)**
- **SOC 2 Type II certification achieved.**
- Multiple Enterprise-tier accounts running dedicated/VPC deployments in production.
- First third-party or customer-authored Marketplace workflow published and used by an organization other than its author.

**Personas served:** Adds Large Enterprise Analytics Org — the last of the ten personas from §4.1.

---

## Beyond V3 — Long-Term Vision

No specific milestones are pre-committed this far out (per §20.1's philosophy — commitments are made phase by phase, based on accumulated evidence, not speculated years in advance). The direction:

- Majority of the agent roster (§13.2) operating as independently scaled, independently versioned services.
- Full data-engineering stack (§14.4: Airflow, Kafka, Spark, dbt, Great Expectations) available wherever customer scale actually justifies it.
- A mature **Marketplace** (§18.5) with real third-party agent and workflow contributions.
- **Guided Mode** (§6.4) mature enough to be the *default* experience for new signups, not just a persona-specific mode.

---

## Appendix A — Architecture Extraction Triggers

The modular monolith (§14.1) is split module-by-module only when a concrete trigger fires — not on a schedule:

| Module | Trigger Type | Fires In |
|---|---|---|
| **Training** | Compute profile diverges sharply (bursty, CPU/GPU-heavy) and bottlenecks or over-provisions shared infra | Phase 2 (V1) |
| **Monitoring** | Standing background process — its failure should never take down interactive dashboard requests | Phase 3 (V2) |
| *Others (Connector Management, Agent Pool members, etc.)* | Team boundary forms around the module, or its compute profile diverges | Phase 4+ (V3 and beyond), as usage reveals real coupling/scaling pressure |

**Data-engineering-stack components (§14.4)** — each is deferred until its specific trigger is met, not built speculatively:

| Component | Becomes necessary when… |
|---|---|
| Airflow / Prefect / Dagster | The Workflow Builder's own scheduler hits limits on cross-workflow dependency management at scale (many enterprise customers, complex interdependent DAGs) |
| Kafka (or managed equivalent) | Real customer need for sub-minute analytics emerges, and/or internal event needs outgrow simple queue-based messaging |
| Spark (or serverless equivalent) | Customer datasets routinely exceed the single-machine processing ceiling (~10–50 GB) — until then, compute pushdown (§12.3) handles this more cheaply |
| dbt | InsightAI's own transformation logic grows complex enough to benefit from dbt's testing/lineage tooling, or a customer's existing dbt project needs integration |
| Great Expectations (or equivalent) | Customers need to author custom validation rules beyond InsightAI's built-in checks (typically an Enterprise-tier need) |

Terraform/Helm/Kubernetes IaC is written from **day one** even for a single-monolith deployment (to establish the practice early), but the full multi-service Helm topology is built incrementally as services are actually extracted — not ahead of need.

---

## Appendix B — Persona Coverage by Phase

| Phase | Personas Newly Served | Personas Explicitly Deferred |
|---|---|---|
| MVP | Priya (Business Analyst), Marcus (Data Analyst) | Everyone else |
| V1 | + Dana (ML Engineer), Alex (Data Scientist) | Sam, VP, SMB Owner, Large Enterprise Org |
| V2 | + Sam (BI/Governance), VP (via Report Agent), SMB Owner/Operator, Jordan/Operations (fuller support) | Large Enterprise Analytics Org |
| V3 | + Large Enterprise Analytics Org | — (full persona set served) |

This sequencing exists because the three beachhead personas (Priya, Marcus, Dana — §4) represent the shortest path from signup to demonstrable value, and their satisfaction is a prerequisite for the other seven personas to trust the platform.

---

## Appendix C — Open Questions to Revisit at Each Phase Gate

Carried forward from PRD §22.4 — these should be explicitly revisited, not assumed, as each phase closes:

1. Does actual willingness-to-pay across Professional/Business/Enterprise match the illustrative tier structure (§18.2), once real pricing data exists?
2. Does the beachhead persona sequencing (Business Analyst → Data Analyst → ML Engineer) hold up against real MVP-phase usage data, or does usage reveal a different natural entry point?
3. At what *specific* usage threshold (concrete customer count or data volume, not a qualitative trigger) does each data-engineering-stack component in Appendix A actually need to be built?
4. How should the Marketplace's trust, review, and sandboxing model work in detail — deliberately left unspecified until Phase 4 is reached.

---

## Guardrails on This Roadmap Itself

Per §21.5: no adoption or time-saved metric at any phase gate is reviewed without its corresponding **quality** metric alongside it. Hitting a speed milestone (e.g., faster time-to-deployed-model) by quietly cutting corners on model quality or leaderboard rigor counts as a **miss**, not a win. Objective-completion metrics are likewise reviewed alongside downstream outcome signals (does a shared dashboard get viewed again next week; does a deployed model survive its first monitoring cycle without rollback) — a completed artifact is not the same as a trusted, used one.