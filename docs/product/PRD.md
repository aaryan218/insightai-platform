# InsightAI
## Product Requirements Document

**Document Type:** Master PRD (Single Source of Truth)
**Version:** 1.0
**Status:** Draft for Engineering, Design, and Investor Review
**Prepared for:** Engineering, Design, Data Science, Go-To-Market, and Executive Leadership
**Intended Audience:** Founding engineers, future employees, investors, enterprise design partners
**Document Owner:** Product & Engineering Leadership
**Review Cadence:** Revised at the end of each roadmap phase (see Section 20)

---

## How to Read This Document

This PRD is organized so that different readers can enter at different points:

- **Engineers** should start with Sections 6–15 (Product Experience, Architecture, Agents, NFRs).
- **Designers** should start with Sections 4, 6, 8, 9, 10 (Personas and Experience sections).
- **Investors and executives** should start with Sections 1, 2, 16, 17, 18, 20 (Summary, Vision, Competitive Position, Business Model, Roadmap).
- **New employees** should read the document in order, front to back, before their first design or architecture review.

This is a living document. Where a decision has not yet been made, that is stated explicitly rather than papered over. Where a decision has been made but carries real trade-offs, those trade-offs are documented rather than hidden. A PRD that only shows the upside of every decision is not useful to the people who have to build the product.

---

## Table of Contents

1. Executive Summary
2. Product Vision & Philosophy
3. Problem Statement
4. Target Users & Personas
5. Long-Term Vision — The AI Data Team
6. User Experience & Core Product Flow
7. Machine Learning Experience
8. Analytics Experience
9. Visual Workflow Builder
10. Notebook Experience
11. Enterprise Features
12. Data Sources & Connectors
13. AI Agent Architecture
14. Technical Architecture Overview
15. Non-Functional Requirements
16. Competitor Analysis
17. Industry Impact
18. Business Model & Pricing
19. Risks & Mitigations
20. Product Roadmap
21. Success Metrics
22. Appendices

---

## 1. Executive Summary

InsightAI is an AI-native platform that automates the enterprise data lifecycle — from raw data connection through exploratory analysis, dashboarding, machine learning, deployment, and monitoring — inside a single product surface. It is built for organizations that own valuable data but lack the specialized headcount, time, or tooling to turn that data into decisions and production ML systems on a continuous basis.

The product is not a chatbot that answers questions about data. It is a system that performs bounded, auditable, human-supervised **workflows**: connect a dataset, and InsightAI will profile it, clean it, explain it, visualize it, model it, deploy it, and monitor it, while keeping a human in the loop at every consequential decision point. The unit of value is not an answer; it is a completed piece of work — a dashboard that shipped, a model that deployed, a report that went to the executive team.

**The core wedge:** most organizations still run data work as a relay race across disconnected tools — a warehouse, a notebook, a BI tool, an ML platform, and a ticketing system to request all of the above — with a data analyst or data scientist manually carrying the baton at every handoff. InsightAI collapses that relay race into one continuous, AI-assisted pipeline, without requiring the organization to rip out its warehouse or its BI tool on day one.

**What InsightAI is not:** it is not a replacement for a senior data science team's judgment on high-stakes models, it is not a data warehouse, and it is not a general-purpose AI assistant. It is an execution layer that sits above the warehouse and automates the 70–80% of analytics and ML work that is repetitive, well-understood, and currently done by hand because no tool does it end-to-end.

**Target customers at launch:** mid-market companies (200–2,000 employees) with an existing cloud data warehouse (Snowflake, BigQuery, Databricks, or a well-organized Postgres/MySQL environment), a small analytics function (1–8 people), and unmet demand for dashboards, forecasts, and predictive models that their current team cannot produce fast enough. Enterprise accounts (2,000+ employees) become a primary focus from Version 2 onward, once RBAC, SSO, audit logging, and deployment-governance features are mature (see Section 11 and Section 20).

**Business model:** a four-tier structure — Community (free, self-hosted, single-user), Professional (per-seat SaaS), Business (per-seat plus usage, team features), and Enterprise (annual contract, custom deployment, dedicated support) — supplemented by usage-based compute billing for model training and inference, and a future workflow/agent marketplace. Full detail in Section 18.

**Primary risks the team is explicitly tracking:** (1) the gap between demo-quality automation and production-trustworthy automation in regulated or high-stakes ML use cases; (2) the cost structure of LLM-driven agents at scale relative to per-seat SaaS pricing; (3) incumbent platforms (Databricks, Snowflake, Microsoft Fabric) shipping equivalent "auto-pilot" features natively, which would erode InsightAI's differentiation faster than the company can build a moat around workflow and agent orchestration. These are addressed in depth in Section 19.

**What this document commits the team to:** a phased build that proves value on a narrow slice (CSV/warehouse → automated EDA → dashboard, and CSV/warehouse → AutoML → deployed model) before expanding into the full 37-service, multi-agent architecture described in Section 14. The long-term architecture is documented here because engineers need to know the destination in order to make good near-term decisions — not because Version 1 will build all of it. Section 20 is explicit about what ships when.

---

## 2. Product Vision & Philosophy

### 2.1 Vision Statement

InsightAI exists to compress the distance between "we have data" and "we made a better decision because of it." The platform automates the mechanical, repetitive majority of enterprise data work — schema discovery, cleaning, exploratory analysis, dashboard construction, feature engineering, model selection, training, evaluation, deployment, and monitoring — while keeping a human explicitly in control of objectives, judgment calls, and anything that ships to production or a board deck.

InsightAI combines five capabilities that today live in five different product categories, purchased from five different vendors, operated by people with five different skill sets:

| Today's Category | Representative Tools | InsightAI's Equivalent |
|---|---|---|
| Business Intelligence | Power BI, Tableau, Looker | Analytics Experience (Section 8) |
| AutoML / ML Platform | DataRobot, H2O.ai, Vertex AI AutoML | Machine Learning Experience (Section 7) |
| Data Science Notebook | Jupyter, Databricks Notebooks | Notebook Experience (Section 10) |
| Workflow / Automation | n8n, Airflow (as authored by engineers) | Visual Workflow Builder (Section 9) |
| Conversational AI Assistant | ChatGPT, Claude (general-purpose) | AI Agent Layer (Section 13), scoped to data work |

The vision is not "one tool to replace all five." Enterprises will keep their warehouse, and many will keep their existing BI tool for compliance dashboards that are already built and trusted. The vision is that **the work of connecting these five categories — the manual glue that currently requires a human data professional — becomes automated, auditable, and fast enough that it stops being the bottleneck.**

### 2.2 Core Philosophy — The Fragmented Workflow Problem

The status quo workflow inside a typical mid-market or enterprise analytics team looks like this:

```
 Data Warehouse (Snowflake / BigQuery / Redshift)
            |
            v
   Analyst writes SQL to extract a working table
            |
            v
   Analyst downloads / pulls into Python (pandas)
            |
            v
   Analyst opens a Jupyter Notebook
            |
            v
   Manual Exploratory Data Analysis (EDA)
   - null checks, dtype checks, outlier checks
   - distribution plots, correlation matrices
            |
            v
   Analyst builds a dashboard in Power BI / Tableau
   (re-implementing logic already written in the notebook)
            |
            v
   [If ML is needed] Data Scientist re-derives features,
   selects a model family, tunes hyperparameters,
   evaluates, and hands off to an ML engineer
            |
            v
   ML Engineer builds a deployment pipeline
   (often bespoke, undocumented, and owned by one person)
            |
            v
   Model runs in production with NO automated monitoring
            |
            v
   Weeks or months later: someone notices the model
   has drifted, and the entire cycle restarts manually
```

Every arrow in that diagram is a handoff. Every handoff is a place where (a) institutional knowledge is lost, (b) work is duplicated (the dashboard reimplements logic already validated in the notebook), and (c) elapsed time accumulates for reasons that have nothing to do with the difficulty of the underlying question. A trend line that takes an LLM-assisted agent forty seconds to compute and explain routinely takes a mid-market analytics team three to ten business days once ticket queues, meeting overhead, and rework are accounted for.

InsightAI's philosophy is to **collapse the handoffs, not the judgment.** Every stage above — cleaning, EDA, dashboard construction, feature engineering, model selection, deployment, monitoring — is mechanically well-understood. None of it requires creativity in the median case. What requires judgment is (a) deciding what question matters, (b) deciding what an acceptable model looks like for a given business use case, and (c) deciding what ships. InsightAI automates the former and instruments the latter with clear approval checkpoints, rather than trying to automate judgment itself.

### 2.3 Design Principles

These principles govern every product and engineering decision in this document. Where a proposed feature conflicts with one of these, the principle wins by default, and any exception must be justified explicitly in the relevant section.

1. **Automate the pipeline, not the accountability.** InsightAI will recommend a model, a chart, or a cleaning step, but a human explicitly approves anything that leaves the sandbox and touches production data, a live dashboard, or an external system. Every automated action is logged with the reasoning that produced it (see Section 11, Audit Logs).

2. **Show the work.** Every chart, every model recommendation, every cleaning decision includes an inspectable explanation: which rows were dropped and why, which features were engineered and from what source columns, why a given algorithm was recommended over the alternatives that were also tried. A platform that produces answers without showing its work will not survive contact with an enterprise risk or compliance review.

3. **Progressive disclosure over one-size-fits-all automation.** A business analyst who wants a dashboard should never see a hyperparameter grid. A data scientist who wants to override the feature engineering agent's choices should be able to drop into the notebook and do so without losing the work already done upstream. The interface adapts to the user's chosen objective (Section 6), not the other way around.

4. **Bring your own warehouse.** InsightAI does not require organizations to migrate data into a proprietary store as a precondition for value. Where possible, computation is pushed down to the customer's existing warehouse (Snowflake, BigQuery, Databricks) rather than requiring a costly and risky data migration before the product can be evaluated.

5. **Every automated workflow is a reusable, versioned artifact.** A pipeline that InsightAI builds once (clean → engineer features → train → deploy) is saved as a workflow that can be re-run, scheduled, shared with a teammate, or forked — not a one-off script that has to be rebuilt from scratch next quarter.

6. **Right-sized automation.** Not every dataset needs 37 microservices' worth of infrastructure behind it, and not every customer needs the full agent mesh described in Section 13 on day one. The architecture is designed to scale from a single CSV upload with a lightweight agent chain, up to a Kafka/Spark/Airflow-backed pipeline processing terabytes daily for an enterprise account — without forcing a rewrite between the two. Section 14 describes how this scaling works in practice, and Section 20 is explicit that the heavier infrastructure ships only once usage justifies its operational cost, not on day one.

---

## 3. Problem Statement

### 3.1 Primary Problems

InsightAI is built to address nine specific, observable problems in how organizations currently work with data. Each is stated here as a problem, not a feature request, because the roadmap (Section 20) will occasionally solve the same problem in different ways as the product matures.

**P1 — Non-technical users cannot effectively query enterprise data.**
Business users who understand the business question ("why did churn spike in the Northeast region last month?") do not have the SQL, Python, or BI-tool proficiency to answer it themselves. They file a ticket and wait. The knowledge gap is not intelligence — it is tooling and syntax.

**P2 — Business users wait days or weeks for reports.**
Even when the underlying query is simple, it competes for analyst time against every other request in the queue. A well-run analytics team with a healthy backlog still routinely quotes multi-day turnaround for anything that requires a new query or a new chart, because the marginal cost of *starting* a new analysis (finding the right tables, understanding the schema, writing and validating the query) is high relative to the analytical complexity of the question itself.

**P3 — Machine learning pipelines require significant manual, repetitive engineering work.**
The academically interesting part of ML — model architecture, novel feature ideas — is a small fraction of the actual labor. The majority is: data validation, null/outlier handling, encoding categorical variables, train/test/validation splitting with correct time-awareness, baseline model comparison, and hyperparameter search. This work is necessary, well-understood, and almost entirely automatable, yet most teams still hand-roll it per project.

**P4 — Exploratory Data Analysis (EDA) is repetitive.**
The first 30–90 minutes of nearly every analysis follow the same script: check shape, check dtypes, check nulls, check cardinality of categoricals, plot distributions, check correlations, look for obvious outliers. This is valuable but mechanical, and skipping it is a leading cause of downstream modeling errors.

**P5 — Feature engineering is repetitive.**
Date decomposition (day-of-week, is-holiday, days-since-event), categorical encoding, ratio and interaction features, rolling aggregates for time series — the same transformations are reinvented dataset after dataset, team after team, with no institutional memory carried forward.

**P6 — Model comparison is repetitive and often skipped under time pressure.**
Rigorous practice calls for comparing multiple model families (linear/regularized, tree ensembles, gradient boosting, and where appropriate neural approaches) against clearly defined baselines before selecting a production model. Under deadline pressure, teams frequently skip this and ship the first model that "works," leaving accuracy and robustness on the table.

**P7 — Business dashboards require specialized skills that business owners of the data usually do not have.**
The person who understands what "good" looks like for a metric is rarely the person who knows how to build a performant, well-designed dashboard in a BI tool. This mismatch is the root cause of P2.

**P8 — Companies spend a large fraction of skilled analyst and data-scientist time on repetitive work instead of judgment work.**
Every hour a senior data scientist spends re-writing a null-handling routine or rebuilding a dashboard that resembles one built last quarter for a different team is an hour not spent on the 20% of work that actually requires their expertise: defining the right question, validating a model's fitness for a specific business decision, or interpreting a genuinely ambiguous result.

**P9 — Current AI assistants stop at answering questions instead of executing complete workflows.**
General-purpose conversational AI (ChatGPT, Claude, and similar) can already explain a statistical concept, write a snippet of pandas code, or suggest a modeling approach. What they do not do natively is connect to a live enterprise warehouse, execute a multi-step pipeline against real data with governance and audit logging, and produce a deployed, monitored artifact. There is a gap between "AI that talks about data work" and "AI that does data work," and that gap is where InsightAI is positioned.

### 3.2 Cost of the Status Quo

These problems compound. A single business question — "which customer segment is most at risk of churn next quarter, and what should we do about it?" — under the status quo workflow requires, at minimum: an analyst to receive and scope the request (P2), pull and clean the relevant data (P3, P4), build features (P5), potentially loop in a data scientist to build and compare models (P6), and then someone to build a dashboard or report to communicate the result (P7) — with the most skilled people on the team spending the majority of their time on the mechanical middle steps (P8) rather than the judgment calls at the start and end.

**Illustrative estimate (not a guarantee, stated as an assumption for planning purposes):** a mid-market company with a 4-person analytics team, each person costing the organization a fully loaded ~$140,000–$180,000/year, spending a conservative 60% of their time on P3–P6-type repetitive work, represents on the order of $350,000–$430,000/year in fully loaded cost applied to work that is largely mechanical. This is the total addressable inefficiency InsightAI is designed to compress — not by eliminating the team, but by giving each member back the majority of that time for judgment work, or allowing the same team to support a larger analytical surface area without proportional headcount growth.

### 3.3 Why Now

Three trends converge to make this the right time to build InsightAI, and each carries a corresponding risk that Section 19 addresses directly:

1. **LLMs are now reliable enough to plan and execute multi-step tool-use workflows**, not just answer questions in isolation. This is what makes an "AI Data Team" (Section 5) plausible in a way it was not three years ago. *Risk: reliability is still probabilistic, not deterministic — Section 19 covers mitigation via human approval gates and evaluation harnesses.*

2. **Cloud data warehouses have become the default enterprise data substrate.** Snowflake, BigQuery, Databricks, and well-managed Postgres/MySQL deployments mean that, for the first time, a large share of the target market already has clean, queryable, centralized data — the hard data-engineering problem of "getting the data into one place" is increasingly solved before InsightAI even engages. *Risk: this is not universally true, especially in the SMB segment — connector breadth and CSV/Excel support (Section 12) exist precisely to serve customers who have not yet centralized their data.*

3. **AutoML and MLOps tooling has matured to the point of componentization.** Feature stores, experiment trackers, model registries, and drift-detection libraries are now mature open-source or commodity building blocks rather than research problems. InsightAI's job is orchestration and UX on top of largely-solved infrastructure primitives, not reinventing them. *Risk: if these primitives are commodity, competitors can assemble them too — durable differentiation must come from workflow integration and agent orchestration quality, not from any single infrastructure component (see Section 16).*


### 3.4 Illustrative Customer Scenario

To make Sections 3.1–3.3 concrete rather than abstract, consider a composite, illustrative (not a real customer) scenario referenced again in Section 21 when defining success metrics.

**RetailCo**, a 400-employee direct-to-consumer retailer, runs its order and customer data in Snowflake. Its 3-person analytics team fields requests from marketing, operations, and finance. A marketing manager wants to know why the Northeast region's repeat-purchase rate dropped last month.

**Status quo path:** the manager files a ticket. It is triaged behind two higher-priority requests. Three business days later, an analyst pulls the relevant tables, writes SQL to compute repeat-purchase rate by region and month, notices the drop, and starts investigating contributing factors — checking whether it is concentrated in a channel, a product category, or a customer cohort. This requires writing several more exploratory queries, none of which are saved anywhere durable. Two more days pass. The analyst builds three charts in Tableau and writes a short summary. Total elapsed time: five to seven business days. The underlying SQL and exploratory logic, valuable institutional knowledge about how to investigate this class of question, lives in the analyst's personal notebook history and is not reusable the next time a similar question arises.

**InsightAI path:** the manager (or, more realistically, the analyst on the manager's behalf during MVP-era usage patterns — see Section 20.3's early-phase scope) connects the relevant Snowflake tables. The automatic analysis flow (Section 6.2) runs in under a minute, surfacing the repeat-purchase-rate drop as a flagged anomaly without being asked, because the EDA and Analytics Agents (Sections 13.3, 13.5) recognize "repeat purchase rate" as a business-vocabulary metric and flag the change point automatically. The manager selects "create a dashboard," and the Analytics Agent's decomposition (Section 8.4) shows the drop is concentrated in one acquisition channel and one product category. The dashboard is shared within the hour, and — because it was built through the Visual Workflow Builder rather than as a one-off — the same investigation pattern is saved as a reusable workflow (Section 9.4) that can be pointed at a different region or metric next quarter without being rebuilt from scratch.

**What this scenario does and does not claim:** it does not claim InsightAI eliminates the need for an analyst to interpret the result and decide what to do about the channel/category concentration — that judgment call remains squarely human, per Section 2.3's Design Principle 1. It claims the mechanical distance between "someone asked a question" and "a decomposed, explained answer with a shareable artifact exists" compresses from days to under an hour. That compression — not full automation of judgment — is the product's core, testable value claim, and Section 21's time-saved metrics are designed to validate it against real data rather than scenarios like this one.

---

## 4. Target Users & Personas

InsightAI serves ten identified user types across two market segments (SMB and Enterprise). Rather than treat all ten as equally primary, the roadmap (Section 20) sequences the product to win three "beachhead" personas first — Business Analyst, Data Analyst, and ML Engineer — because they represent the shortest path from signup to demonstrable value, and because their satisfaction is a prerequisite for the other seven personas to trust the platform.

### 4.1 Persona Summary Table

| Persona | Segment | Primary Job to Be Done | Primary InsightAI Surface | Beachhead? |
|---|---|---|---|---|
| Business Analyst | SMB & Enterprise | Answer ad hoc business questions without writing SQL | Analytics Experience, NL Query | Yes |
| Data Analyst | SMB & Enterprise | Build and maintain dashboards, do EDA faster | Analytics Experience, Notebook | Yes |
| BI Team / BI Engineer | Enterprise | Standardize metrics, govern dashboards at scale | Enterprise Features, Workflow Builder | No (V2) |
| Machine Learning Engineer | Enterprise & scale-up | Ship and maintain production ML pipelines faster | ML Experience, Workflow Builder, Agents | Yes |
| Data Scientist | Enterprise & scale-up | Faster iteration on modeling, less pipeline glue code | Notebook, ML Experience | No (V1) |
| Product Manager | SMB & Enterprise | Get metrics and forecasts without depending on analytics team queue | Analytics Experience, Dashboards | No (V1) |
| Operations Teams | SMB & Enterprise | Monitor operational KPIs, get anomaly alerts | Analytics Experience, Monitoring Agent | No (V2) |
| Enterprise Decision Maker (VP/C-suite) | Enterprise | Executive summaries, trend explanations, board-ready reports | Analytics Experience, Report Generation Agent | No (V2) |
| SMB Owner/Operator | SMB | All of the above, with no dedicated analytics headcount | Full platform, guided mode | No (V2, Business tier) |
| Large Enterprise Analytics Org | Enterprise | Governance, scale, integration with existing stack | Enterprise Features, Connectors | No (V3) |

### 4.2 Detailed Personas

**Business Analyst — "Priya"**
Priya works in a revenue operations or marketing analytics function. She is SQL-literate at a basic-to-intermediate level, comfortable in spreadsheets, and not a programmer. Her job to be done is answering questions like "what's driving the increase in support tickets this month?" without waiting on a data engineering queue. She is the primary user of the natural-language query surface (Section 8) and the automated EDA/insight summary that appears the moment a dataset is connected (Section 6). Success for Priya is measured in minutes-to-answer, not model accuracy. She will not open the Notebook (Section 10) and should never be required to.

**Data Analyst — "Marcus"**
Marcus is the person who currently owns the Power BI or Tableau dashboards and spends real time on P4/P5/P7 (Section 3.1). He is the persona most directly relieved by InsightAI's automated EDA, chart generation, and dashboard scaffolding. Unlike Priya, Marcus wants control: he will accept an AI-generated first draft of a dashboard but wants to edit chart types, thresholds, and groupings before it goes to his stakeholders. He is a moderate user of the Notebook for validation and a heavy user of the Visual Workflow Builder (Section 9) to make his recurring reporting pipelines reusable instead of rebuilt monthly.

**Machine Learning Engineer — "Dana"**
Dana is responsible for getting models into production and keeping them there. Her pain is disproportionately in the "boring 80%" — environment setup, feature pipeline glue code, deployment infrastructure, and monitoring — rather than model selection itself, where she often already has strong opinions. InsightAI's value to Dana is in the Deployment Agent, Monitoring Agent, and the model registry/versioning system (Section 7, Section 13), not in being told which algorithm to use. Dana is the persona most likely to want to override automated choices and drop into code, and the product must never make that harder than doing the work herself outside InsightAI — this is a hard product constraint on the Notebook and API design (Section 10, Section 14).

**Data Scientist — "Alex"**
Alex is closer to the modeling craft than Dana and cares about explainability, leakage risk, and validation rigor. Alex is a skeptical user by default: an AutoML platform that hides its reasoning will lose Alex's trust immediately. Every automated decision surfaced to Alex — feature selection, algorithm choice, hyperparameter ranges searched — must be inspectable and overridable (Design Principle 2, Section 2.3). Alex becomes a power user of the Notebook and the Explainability tooling in Section 7.6.

**BI Team / BI Engineer — "Sam"**
Sam operates at the team level, not the individual-analysis level. Sam's job to be done is governance: making sure that "revenue" means the same thing on every dashboard across the company, that access control is correct, and that dashboards do not silently drift from the metrics definitions the finance team signed off on. Sam is a heavy user of Enterprise Features (Section 11) — particularly RBAC, audit logs, and a semantic-layer / metric-definition capability that is called out explicitly as a Version 2 requirement in Section 20.

**Product Manager — "Jordan"**
Jordan wants a fast, self-serve way to check feature adoption, retention cohorts, and experiment readouts without filing a ticket with Marcus's team. Jordan's primary interaction is the same NL query and auto-dashboard surface as Priya, but Jordan more frequently wants to save and share a recurring view ("weekly activation dashboard") and occasionally wants a lightweight forecast ("at this trend, when do we cross 10,000 weekly actives?").

**Operations Teams — "Operations at RetailCo"**
This persona cares about anomaly detection and alerting more than exploratory analysis — a spike in returns, a drop in fulfillment SLA, a warehouse inventory discrepancy. The relevant surfaces are the Monitoring Agent and the Analytics Experience's anomaly-detection and comparison-to-prior-period features (Section 8.3), typically consumed as scheduled alerts rather than an interactive session.

**Enterprise Decision Maker — "the VP of Sales"**
This persona almost never opens the product directly. The value delivered is a Report Generation Agent (Section 13.7) producing a natural-language executive summary — attached to a dashboard someone else built — that explains *why* a number moved, not just that it moved. This persona is a strong proponent for renewal even though they are rarely a hands-on user, and the roadmap treats "report quality good enough to forward to a VP without editing" as a distinct, trackable bar (Section 21).

**SMB Owner/Operator**
In a company with 10–100 employees, this may be the same person who is also the head of operations, finance, and marketing. They have no dedicated analytics headcount at all. For this persona, InsightAI is not "faster than the status quo," it *is* the analytics function. This persona requires the most guided, opinionated version of the product (a "guided mode" described in Section 6.4) and is disproportionately price-sensitive — the Business tier in Section 18 is shaped around this persona's willingness to pay.

**Large Enterprise Analytics Organization**
At 2,000+ employees, InsightAI is evaluated less as a single-user product and more as infrastructure: does it integrate with existing SSO, does it respect existing warehouse governance, does it produce auditable logs that satisfy a SOC 2 or industry-specific compliance review, and can it coexist with an incumbent BI tool rather than requiring a rip-and-replace. This persona is explicitly a Version 3 focus (Section 20) — the product is not ready to sell to this persona until Section 11's enterprise feature set and Section 15's non-functional bar are met.

### 4.3 Day in the Life: Two Beachhead Personas

These vignettes are illustrative composites, not transcripts of real usage, and are included to make Section 4.2's persona descriptions concrete for design and engineering decisions elsewhere in this document.

**Marcus, Data Analyst, Tuesday morning.** Marcus starts his week with a recurring request: the ops team wants to know if last week's warehouse fulfillment delays are improving. Under the status quo (Section 3.1, P2/P7), this would mean reopening last quarter's dashboard, manually re-pulling the latest week of data, and re-checking that his groupings still make sense given a new distribution center that opened since he last touched it. In InsightAI, Marcus opens the workflow he built and saved the first time this question came up (Section 9.4) and re-runs it against the current data — the workflow already encodes his groupings, his cleaning rules, and his chart choices. It flags, via the Analytics Agent's change-point detection (Section 8.3), that the new distribution center's data has a different fulfillment-time distribution than the others, which he had not accounted for the first time. He adjusts the workflow once, in the Visual Workflow Builder, to break out the new center separately, and the corrected dashboard goes to ops before his first meeting. The value Marcus experiences is not "the AI did my job" — it is that the mechanical 80% (re-pulling, re-cleaning, re-charting) happened automatically, and his actual analytical attention went to the one thing that genuinely needed it: noticing that a new facility changes the comparison's validity.

**Dana, ML Engineer, mid-sprint.** Dana's team has a churn model in production that has been stable for four months. This week, the Monitoring Agent (Section 13.10) flags moderate feature drift concentrated in a mid-importance feature (average session length), following a recent product change that altered how sessions are measured. Per the decision framework in Section 7.7, the system's default policy recommends an incremental update rather than a full retrain, since the drift is moderate and not concentrated in the model's top-importance features. Dana reviews the recommendation, the underlying drift report, and the proposed incremental-update evaluation results (Section 7.6-style comparison against the incumbent) in about ten minutes — far less time than she would have spent if she had first needed to notice the drift herself, then manually decide whether it warranted action, then manually kick off and evaluate a retrain. She approves the incremental update. It deploys to a canary slot automatically, per the deployment and monitoring coupling described in Section 7.9, and Dana moves on to the feature work she was actually staffed to do that sprint — the judgment call was still hers, but the detection, framing, and mechanical execution were not.

### 4.4 Explicit Non-Goals for Personas (V1)

To keep scope honest, the following are stated as **not** primary targets for the first shipped version, even though they appear in the full persona list: BI Team/BI Engineer (governance features insufficient until V2), Enterprise Decision Maker (Report Generation Agent quality bar not yet met), SMB Owner/Operator guided mode (requires more opinionated UX than V1's power-user-leaning interface will offer), and Large Enterprise Analytics Org (SSO and compliance certifications are V2/V3, per Section 11 and Section 20).

---

## 5. Long-Term Vision — The AI Data Team

The long-term vision for InsightAI is that it functions as an **AI Data Team**: a standing, always-available set of specialized agents (Section 13) that perform the full spectrum of analytics and ML work an organization would otherwise hire a human team to do, while the organization's actual humans supervise, direct, and make final calls on anything consequential.

This is explicitly **not** a vision of full autonomy. It is closer to the relationship a competent Chief of Staff has with an executive: the Chief of Staff can draft the memo, book the meeting, and pull the numbers, but they do not sign the contract, and they know which decisions require escalation. Three properties define what "AI Data Team" means concretely, and each has a direct product consequence:

1. **Delegation, not automation-and-forget.** A user should be able to say "keep an eye on churn risk in the enterprise segment and tell me if anything changes" and have that be a standing, monitored task — not a one-off query. Product consequence: the Monitoring Agent (Section 13.10) and the Visual Workflow Builder's scheduling capability (Section 9.5) are core infrastructure, not optional add-ons.

2. **Escalation, not silent failure.** When an agent is not confident — a model's performance has degraded below a threshold, a data source's schema has changed unexpectedly, a forecast's confidence interval has widened sharply — the system escalates to a human rather than silently proceeding or silently failing. Product consequence: every agent in Section 13 has a defined confidence/escalation contract, not just a task to perform.

3. **Composability over a monolith.** An "AI Data Team" is not one enormous model doing everything; it is a set of narrow, independently-improvable agents with clear interfaces, the same way a human data team is not one person doing everything but a set of specialists who hand off work with clear expectations. Product consequence: Section 13's agent architecture is explicitly modular, independently versioned, and independently evaluable — a requirement discussed further in Section 14.

**What changes for the organization, if this vision succeeds:** the analytics function stops being a queue that business questions wait in, and starts being a team that supervises a large, parallel stream of automated work — reviewing and approving rather than manually executing. A 4-person analytics team in this world is not doing the job of 4 people; with appropriate trust and governance, it is doing the job of a substantially larger team, with the humans concentrated on judgment, escalation review, and stakeholder communication.

**What does not change, by design:** headcount is not the metric InsightAI optimizes to reduce, and the product will not be marketed or built as a headcount-replacement tool internally — both because the more durable value proposition is capacity expansion (more gets analyzed, not fewer people do the analyzing) and because positioning the product as a replacement for skilled staff creates predictable and justified organizational resistance that undermines adoption (see Section 17.2, Adoption Barriers).

---

## 6. User Experience & Core Product Flow

### 6.1 Design Principle Recap for This Section

Per Design Principle 3 (Section 2.3), the interface adapts to the user's chosen objective rather than presenting one undifferentiated workspace. This section describes the flow that every dataset goes through and how the interface branches after that flow completes.

### 6.2 The Automatic Analysis Flow

The moment a dataset is connected — whether by CSV/Excel upload or by pointing InsightAI at an existing warehouse table or query — the platform runs a bounded, deterministic-where-possible pipeline before asking the user what they want to do next. This is the single most important interaction in the product, because it is the first thing every new user experiences, and it is the moment the product either earns trust or does not.

```
 Data Connected (CSV / Excel / Warehouse Table / Query)
              |
              v
   +----------------------+
   |  Schema Detection    |   Column types, primary-key candidates,
   +----------------------+   likely date/time columns, likely IDs
              |
              v
   +----------------------+
   | Relationship          |   For multi-table sources: foreign-key
   | Understanding         |   candidates, join cardinality checks
   +----------------------+
              |
              v
   +----------------------+
   | Dataset Summary        |   Row/column counts, memory footprint,
   +----------------------+   grain of the table, freshness
              |
              v
   +----------------------+
   | Missing Value          |   Per-column null rate, missingness
   | Detection               |   patterns (random vs. structural)
   +----------------------+
              |
              v
   +----------------------+
   | Anomaly Detection       |   Outliers, sudden distributional
   +----------------------+   shifts, duplicate-row detection
              |
              v
   +----------------------+
   | Automated EDA            |   Distributions, correlations,
   +----------------------+   cardinality, class balance (if
              |                a target-like column is detected)
              v
   +----------------------+
   | Chart Generation          |   3-7 charts selected by relevance,
   +----------------------+   not "one chart per column"
              |
              v
   +----------------------+
   | Business Insight          |   Natural-language summary of what
   | Generation                  |   the automated steps above found
   +----------------------+
              |
              v
   +----------------------+
   | Recommended Next Actions    |   Ranked suggestions: build a
   +----------------------+   dashboard, predict target X,
                                 investigate anomaly Y, etc.
```

**Time budget (design target, not a guarantee):** for a dataset under 1 million rows and under 100 columns, this pipeline should complete in under 60 seconds end-to-end, with partial results streamed to the UI as each stage completes rather than a single blocking spinner. Larger datasets fall back to a sampled-first-pass approach (profile a statistically representative sample, then backfill exact statistics asynchronously) — this trade-off is documented explicitly in Section 15 (Performance) because it affects the accuracy of first-pass summaries for very large tables.

**What this flow deliberately does not do:** it does not train a model, it does not write to any destination outside InsightAI's own workspace, and it does not require the user to have specified a business objective yet. This is a read-only reconnaissance pass. Nothing about it can surprise or damage the customer's underlying data, which is a deliberate trust-building constraint, not an accident of scope.

### 6.3 Objective Selection

Once the automatic analysis flow completes, the user is presented with the dataset summary, insights, and a set of objective choices, ranked by the Recommended Next Actions step but not restricted to it:

| Objective | What Happens Next | Primary Persona |
|---|---|---|
| Create a dashboard | Routes into Analytics Experience (Section 8), pre-populated with the charts already generated during auto-analysis | Marcus, Priya |
| Generate an executive report | Routes into Report Generation Agent (Section 13.7) | VP persona (via Marcus/Sam) |
| Train a machine learning model | Routes into Machine Learning Experience (Section 7), with target-detection pre-run | Dana, Alex |
| Build a predictive model / forecast | Specialization of the above, routed to time-aware modeling flow | Jordan, Operations |
| Create a reusable workflow | Routes into Visual Workflow Builder (Section 9), pre-populated with the steps already executed | Marcus, Dana |
| Open a notebook for advanced work | Routes into Notebook Experience (Section 10), with the dataset, summary, and all intermediate artifacts already loaded as variables | Alex, Dana |

The interface does not force a single linear path. A user can select "create a dashboard," get most of the way through, and then decide to also "train a model" on the same dataset — the platform treats the dataset and its automatic-analysis artifacts as a shared foundation that every downstream objective builds on, rather than re-running discovery from scratch for each objective.

### 6.4 Guided Mode vs. Power Mode (Design Direction, V2)

Two user experience modes are planned, with only Power Mode targeted for V1:

- **Power Mode (V1):** assumes the user knows what they want (build a dashboard, train a model) and gives them full control over every step, with AI assistance available but not forced.
- **Guided Mode (V2):** designed for the SMB Owner/Operator persona (Section 4.2) who does not know what "objective" to pick. Guided Mode asks business-language questions ("do you want to understand what happened, or predict what happens next?") and translates the answer into the correct objective and configuration automatically. This is explicitly deferred to V2 because building a good guided experience requires a corpus of real usage data from Power Mode to know which defaults actually work — shipping Guided Mode first would mean guessing at defaults with no evidence.


---

## 7. Machine Learning Experience

The Machine Learning Experience automates the full lifecycle from a validated dataset to a monitored, versioned, production model. This section is written for engineers and data scientists and is the most technically detailed section of the PRD outside of Section 13 (Agents) and Section 14 (Architecture), because ML automation is where the greatest trust burden sits — a wrong dashboard is embarrassing, a wrong production model can cause direct financial or customer harm.

### 7.1 Lifecycle Overview

```
Validated Dataset
      |
      v
Dataset Validation  ------->  Cleaning  ------->  Feature Engineering
      |                                                    |
      v                                                    v
Target Detection  <---------------------------  Model Recommendation
      |                                                    |
      v                                                    v
Hyperparameter Tuning  <-----------------  Training (multiple algorithms)
      |                                                    |
      v                                                    v
Model Comparison  ------->  Explainability  ------->  Export
      |
      v
Deployment  ------->  Monitoring  ------->  Versioning
      |                                          ^
      v                                          |
Continuous Improvement Loop  ---------------------+
(incremental update OR full retrain — see 7.7)
```

### 7.2 Dataset Validation

Before any modeling work begins, InsightAI runs a validation pass distinct from the general-purpose auto-analysis in Section 6.2, specific to ML-readiness:

- **Target column feasibility check** — if a target has been selected (manually or via Target Detection, Section 7.4), the platform checks class balance (classification) or distribution shape (regression), and flags targets that are effectively unlearnable from the available features (e.g., near-zero variance, or a target that is a near-duplicate of a single feature, indicating leakage).
- **Leakage screening** — automated detection of features that are suspiciously predictive (near-perfect correlation with the target) or that are temporally invalid (a feature that would not have been known at prediction time, detected via timestamp comparison where available).
- **Sample size adequacy** — a rules-of-thumb check (informed by the number of features, the target's class balance, and the model families under consideration) that flags when the dataset is likely too small for reliable generalization, rather than silently producing a model with unstated confidence.
- **Train/validation/test split strategy determination** — the platform selects between random split, stratified split, and time-based split automatically based on whether a temporal column is present and whether the use case has already been flagged as forecasting (Section 7.8). Time-aware splitting is the default whenever a valid timestamp column exists and the target has temporal structure, because random splitting on time series data is one of the most common sources of falsely optimistic model evaluation — this is treated as a correctness issue, not a configurable preference, though advanced users can override it explicitly in the Notebook.

### 7.3 Cleaning

Cleaning decisions are proposed, not silently applied. Every cleaning action produces an entry in an editable "cleaning plan": drop columns with null rate above a threshold, impute missing values (with the imputation strategy stated per column — mean/median/mode/model-based), handle outliers (flag vs. cap vs. remove, with rationale), deduplicate rows, and normalize inconsistent categorical values (e.g., "NY," "New York," "ny" collapsed with user confirmation). The default behavior for Power Mode users (Section 6.4) is to present this plan for one-click approval before execution; the default for a future Guided Mode is to apply conservative defaults automatically and only surface decisions with material impact.

### 7.4 Feature Engineering

Feature engineering is templated by data type and augmented by an LLM-assisted agent (the Feature Engineering Agent, Section 13.4) for domain-specific suggestions:

| Column Type | Automated Feature Candidates |
|---|---|
| Datetime | Day of week, month, quarter, is-weekend, is-holiday (region-configurable), days-since-reference-event, cyclical (sin/cos) encodings |
| Categorical (low cardinality) | One-hot encoding, target encoding (with cross-validation to prevent leakage) |
| Categorical (high cardinality) | Frequency encoding, embedding-based encoding (for deep learning candidate models), grouping rare categories into "other" |
| Numeric | Binning, log/box-cox transforms for skewed distributions, ratio features between related columns, rolling statistics for time-ordered data |
| Text (free-form) | Length, keyword/entity extraction, sentiment score, and — where justified by data volume and use case — embedding vectors for downstream models |
| Geographic | Distance-to-reference-point calculations, region/state/country roll-ups |

Every generated feature is tagged with its provenance (source columns and transformation applied) so that Explainability (Section 7.6) can trace a model's prediction back through engineered features to original raw columns — this traceability is a hard requirement, not a nice-to-have, because "the model used a feature called `feat_23`" is not an acceptable answer in an enterprise review.

### 7.5 Target Detection, Model Recommendation, and Training

**Target Detection** operates in two modes: explicit (the user names the column they want to predict) and suggested (when the user selects "predict future trends" or "build a predictive model" without naming a column, the platform proposes 1–3 candidate target columns based on column naming patterns, data type, and correlation structure, and asks for confirmation — it never trains against a silently auto-selected target without user confirmation, per Design Principle 1).

**Model Recommendation** narrows a large algorithm space to a shortlist based on problem type (classification/regression/forecasting/clustering), dataset size, feature composition (mostly numeric vs. mostly categorical vs. mixed vs. text-heavy), and an explicit interpretability-vs-accuracy preference the user can set. The shortlist logic:

| Condition | Algorithm Families Prioritized |
|---|---|
| Small dataset (<10k rows), interpretability preferred | Logistic/Linear Regression, Decision Trees |
| Medium-to-large tabular dataset, accuracy preferred | Gradient Boosted Trees (XGBoost/LightGBM-class), Random Forest |
| Time series with clear seasonality | Classical (ETS/ARIMA-class) plus gradient-boosted models with engineered time features, compared head-to-head |
| High-cardinality categorical-heavy data | CatBoost-class gradient boosting, target/embedding encodings |
| Text-heavy or unstructured features present | Transformer-based embeddings feeding into a tabular downstream model, rather than a from-scratch deep model, given typical enterprise dataset sizes |
| Explicit "black box unacceptable" flag | Excludes deep learning and unregularized ensembles from the shortlist entirely, regardless of expected accuracy gain |

**Training** runs the shortlisted algorithms in parallel where infrastructure allows (Section 14), each with an initial hyperparameter search budget, and produces a leaderboard rather than a single answer.

**Hyperparameter Tuning** uses a staged search: a coarse random or Bayesian search across a wide range for each shortlisted algorithm, followed by a narrower refinement pass around the best-performing region for the top 2–3 candidates only, rather than an exhaustive grid search across all candidates — this staging is a deliberate cost control, discussed further in Section 15 (Cost Efficiency) and Section 19 (LLM/compute cost risk).

### 7.6 Model Comparison and Explainability

**Model Comparison** presents a leaderboard with the metric appropriate to the problem type (F1/AUC/precision-recall for imbalanced classification, RMSE/MAE/MAPE for regression and forecasting) alongside training time, inference latency, and model size — because the "best" model on accuracy alone is sometimes the wrong choice for a use case with strict latency or interpretability requirements, and the platform makes that trade-off visible rather than hiding it behind a single leaderboard column.

**Explainability** is mandatory, not optional, for any model that reaches the deployment step. At minimum, every deployed model ships with: global feature importance, per-prediction local explanation (SHAP-class methods for tree/ensemble models, attention/gradient-based methods where applicable for other model types), and a model card summarizing training data provenance, known limitations, and evaluated fairness/bias checks across any protected or sensitive attributes present in the schema. This requirement exists because "the model was accurate on the leaderboard" is an insufficient bar for a model that will influence a real business or customer-facing decision, and because regulatory exposure (Section 19, Regulatory Risks) makes explainability a compliance requirement in an increasing number of jurisdictions and industries, not just a best practice.

### 7.7 Deciding Between Incremental Update and Full Retraining

This is one of the more consequential automated decisions InsightAI makes on an ongoing basis, and it is made explicit here because getting it wrong either wastes compute (retraining when an incremental update would suffice) or lets a model silently degrade (incrementally patching when the underlying data distribution has fundamentally shifted and a full retrain is required).

**The decision is driven by three signals, evaluated together rather than any single one in isolation:**

1. **Magnitude of data drift.** The Monitoring Agent (Section 13.10) continuously compares the statistical distribution of live inference-time features against the training distribution (using population stability index or an equivalent divergence measure per feature). Small, gradual drift across many features, or moderate drift concentrated in features with low model importance, favors incremental update. Large drift concentrated in high-importance features favors full retrain.

2. **Model family's incremental-learning capability.** Not every algorithm supports true incremental updates. Gradient boosted tree ensembles can support limited incremental strategies (adding trees against new residuals) but degrade in quality faster than online-learning-native approaches; linear/logistic models with SGD-based optimizers support well-understood incremental updates; deep learning models support fine-tuning on new data reasonably well; classical time-series models (ARIMA-class) generally require full re-estimation. The platform maintains this capability as a property of the algorithm registry (Section 14.4) and will not attempt an incremental update on a model family that does not reliably support one, regardless of how attractive the compute savings would be.

3. **Performance decay observed on a held-out recent-data check.** Independent of drift measurement, the platform periodically scores the current production model against a rolling window of recent ground-truth outcomes (where ground truth becomes available — e.g., actual churn events, actual conversions). A performance decay past a customer-configurable threshold (default: greater than 5% relative degradation in the primary evaluation metric, configurable per deployment) triggers a retraining evaluation regardless of what the drift signal alone would suggest, because drift and performance decay do not always move together — a model can remain well-calibrated to features that have drifted in ways that do not affect the decision boundary, and conversely can decay in performance from causes that a purely statistical drift measure would miss (e.g., a shift in the relationship between features and target, rather than a shift in the features themselves — concept drift, not just covariate drift).

**Decision table (default policy, configurable per deployment):**

| Drift Magnitude | Performance Decay | Model Supports Incremental Update | Action |
|---|---|---|---|
| Low | Low | — | No action; continue monitoring |
| Low–Moderate | Low | Yes | Incremental update, scheduled during next low-traffic window |
| Low–Moderate | Low | No | No action; flag for scheduled full retrain at next regular cadence |
| Moderate–High | Any | Yes | Incremental update immediately, followed by a shadow-mode full retrain for comparison before the next scheduled cycle |
| Any | High (past threshold) | — | Full retrain triggered immediately; incumbent model flagged for human review; automatic rollback to previous stable version if the incumbent's live performance falls below a hard safety floor before the retrain completes |
| High (concentrated in top-importance features) | Any | — | Full retrain triggered immediately, regardless of incremental capability, because high drift in important features indicates the learned decision boundary itself may no longer be valid |

**Human-in-the-loop constraint (Design Principle 1):** an incremental update to a production model can be configured to deploy automatically once it passes the standard evaluation gate (matching or exceeding the incumbent on the held-out check). A full retrain's resulting model **never** replaces a production model automatically in the default configuration — it is deployed to a shadow/canary slot, compared against the incumbent on live traffic for a configurable soak period (default 72 hours or a minimum sample size, whichever is later), and requires explicit human promotion to full production traffic. This asymmetry is deliberate: incremental updates are lower-risk, smaller deltas; full retrains can materially change model behavior and deserve a higher approval bar by default. Enterprise customers can configure fully automatic promotion for both cases, but it is opt-in, logged, and requires an explicit acknowledgment during configuration (Section 11, Audit Logs) — this is treated as a governance decision the customer makes with full information, not a default the platform assumes on their behalf.

### 7.8 Forecasting-Specific Considerations

Time-series forecasting is treated as a specialization of the general ML flow rather than a fully separate product surface, but with distinct requirements: mandatory time-based splitting (Section 7.2), seasonality and holiday-calendar detection, confidence-interval reporting alongside point forecasts (a point forecast without an interval is treated as an incomplete deliverable, not an acceptable default), and explicit handling of multiple related time series (e.g., forecasting demand per SKU across thousands of SKUs) via a shared-model-with-entity-features approach by default, with per-entity model support available for entities with sufficient individual history and business importance to justify the added complexity.

### 7.9 Export and Deployment

**Export** supports, at minimum: a portable model artifact (in a standard interchange format appropriate to the model family), a containerized inference service, and a documented REST endpoint contract — so that a customer's existing infrastructure can consume a model without being locked into running inference inside InsightAI itself, addressing a common enterprise objection to AutoML platforms (Section 16).

**Deployment** (executed by the Deployment Agent, Section 13.9) provisions a versioned, auto-scaled inference endpoint, registers the model in the model registry with full lineage (dataset version, feature engineering version, training configuration, evaluation results), and wires the endpoint into the Monitoring Agent automatically — a model cannot be deployed through InsightAI without monitoring being attached, closing the gap identified in Section 3.1 (P9-adjacent: monitoring being an afterthought is one of the most common production ML failure modes observed industry-wide) as an explicit product constraint rather than a best-practice suggestion.

---

## 8. Analytics Experience

### 8.1 Overview

The Analytics Experience is the surface most users — especially Priya and Jordan (Section 4.2) — interact with most frequently. It automatically generates executive dashboards, business KPIs, trend analysis, anomaly detection, and period-over-period comparisons, and — per Design Principle 2 — always accompanies a chart with a natural-language explanation of what changed and why, rather than a chart alone.

### 8.2 Automated Dashboard Generation

Dashboards are seeded from the automatic analysis flow (Section 6.2): the platform selects a small number of high-relevance charts (target: 5–9 for an initial dashboard, avoiding both an empty dashboard and an overwhelming one) based on which columns showed the strongest signal during EDA — highest variance explained, strongest correlation with a detected target-like column, or most business-recognizable naming patterns (revenue, churn, conversion, and similar terms are recognized via a maintained business-vocabulary list, extensible per customer). The user can then add, remove, or reconfigure any chart; nothing is locked.

### 8.3 KPIs, Trend Analysis, and Comparison

Every KPI card on a generated dashboard includes, by default: the current value, the comparison to the immediately preceding period of equal length (not just "last month," but a period genuinely comparable in length and, where seasonality is detected, in seasonal position — e.g., comparing this December to last December rather than to November, when seasonality is present), and a direction-and-magnitude indicator. Trend analysis extends this into a time series view with automatically detected change points (moments where the trend's slope or level shifted materially), which are what the natural-language explanation (Section 8.4) anchors its narrative to, rather than describing the whole series generically.

**Anomaly detection** on dashboards runs continuously (for connected/scheduled data sources) or on-demand (for static uploads), using a combination of statistical methods (seasonal-decomposition-based outlier detection for time series, robust z-score/IQR-based methods for cross-sectional data) tuned toward a low false-positive rate by default — an analytics product that cries wolf on every minor fluctuation trains its users to ignore it, which is a worse outcome than under-alerting. Sensitivity is user-configurable per metric.

### 8.4 Natural-Language Explanations and Executive Summaries

The platform explains changes rather than only displaying charts. A generated explanation for a KPI movement follows a consistent structure: **what changed** (the metric and magnitude), **when** (the change point), **what likely contributed** (a decomposition into contributing segments or dimensions, where the schema supports the relevant breakdowns — e.g., "the increase was concentrated in the Northeast region and the Enterprise segment, which together accounted for 71% of the total change"), and **suggested next steps** (e.g., "consider investigating the Northeast region's support ticket volume, which also increased over the same window"). The platform explicitly flags correlation-based explanations as such and does not present them with unwarranted causal certainty — this is a factual-accuracy commitment, not just a UX nicety, and is treated as a hard requirement given how easily an authoritative-sounding wrong causal claim can mislead a business decision (see also Section 19, AI Risks).

Executive summaries (produced in full by the Report Generation Agent, Section 13.7, for the "generate an executive report" objective in Section 6.3) aggregate multiple KPIs and their explanations into a structured narrative document suitable for distribution without further editing — the explicit quality bar tracked in Section 21 is "forwardable to a VP without a human rewriting it," which the team treats as a measurable, testable target rather than an aspiration.


---

## 9. Visual Workflow Builder

### 9.1 Purpose

The Visual Workflow Builder lets users turn any sequence of steps InsightAI can perform — cleaning, EDA, training, evaluation, deployment, monitoring, and more — into a reusable, shareable, schedulable pipeline, in the spirit of tools like n8n or Zapier but scoped to data and ML work rather than general SaaS integration. This directly serves Design Principle 5 (Section 2.3): nothing InsightAI does for a user once should have to be rebuilt from scratch the next time.

### 9.2 Canonical Example

```
  CSV Upload
      |
      v
  [Cleaning Node]
   - drop nulls > 40%
   - impute median (numeric), mode (categorical)
      |
      v
  [EDA Node]
   - auto-profile, generate 6 charts
      |
      v
  [Training Node]
   - target: "churned"
   - algorithms: gradient-boosted trees, logistic regression
   - time budget: 20 minutes
      |
      v
  [Evaluation Node]
   - metric: F1, threshold: 0.75 minimum to proceed
      |
      v
  [Deployment Node]
   - target: staging endpoint, canary 10% traffic
      |
      v
  [Monitoring Node]
   - drift check: daily
   - performance check: weekly (once ground truth available)
```

### 9.3 Node Model

Every node in the builder is configurable and typed, with defined inputs and outputs so that nodes can be composed safely:

| Node Category | Examples | Configurable Parameters |
|---|---|---|
| Source | CSV upload, warehouse query, API pull | Connection, refresh schedule, incremental-load key |
| Transform | Cleaning, feature engineering, custom SQL/Python step | Rules, thresholds, custom code block (advanced) |
| Analysis | EDA, anomaly detection, statistical test | Sensitivity, target columns |
| ML | Training, evaluation, explainability | Algorithm shortlist, metric, time/compute budget |
| Action | Deployment, alert, export, write-back to warehouse | Destination, approval requirement, notification target |
| Control Flow | Conditional branch, approval gate, loop-over-entity | Condition logic, required approver role |

The **Approval Gate** node deserves specific mention: it is how Design Principle 1 (human approval for anything consequential) is expressed inside a workflow. Any workflow that includes a Deployment or external-write Action node is required by default to include at least one upstream Approval Gate before that node can execute in a live (non-sandbox) run — this is enforced by the workflow validator, not left to convention, because relying on users to remember to add a safety gate is exactly the kind of failure mode this product is designed to prevent elsewhere.

### 9.4 Reusability and Sharing

Every workflow is versioned (Section 14) and can be: saved as a private draft, shared with specific teammates or a team/project (Section 11), published as an organization-wide template with parameters exposed for reconfiguration (e.g., "the same churn-prediction workflow, pointed at a different region's data"), and forked — creating a new, independent version that does not affect the original when edited. Forking with lineage tracking (the fork knows what it was forked from) is treated as a requirement, not just versioning in isolation, so that an organization can trace a proliferation of similar workflows back to a common ancestor during an audit or cleanup effort.

### 9.5 Scheduling and Triggers

Workflows can be triggered by: a manual run, a time-based schedule (cron-equivalent, expressed in plain language — "every Monday at 8am" — and translated internally), a data-arrival trigger (new data landing in a connected source), or an event trigger from another workflow's completion (allowing simple workflow chaining without collapsing everything into one monolithic pipeline). Scheduled runs that fail do not fail silently: failure notifications route to the workflow owner and, for workflows tagged as business-critical, to a configurable escalation list — this is implemented via the same notification infrastructure used by the Monitoring Agent (Section 13.10), rather than a separate bespoke system.

---

## 10. Notebook Experience

### 10.1 Purpose

Advanced users (Dana, Alex) need an environment that does not force them through the guided, node-based flows in Sections 6–9 when they want direct code-level control, while still benefiting from everything InsightAI has already computed. The Notebook Experience is an integrated, AI-assisted code environment (Python-first, with SQL cell support for querying connected warehouses directly) that stays connected to the platform's datasets, workflows, and artifacts rather than operating as an isolated sandbox.

### 10.2 What "Staying Connected" Means Concretely

- **Automatic variable pre-loading:** opening a notebook from the "open a notebook for advanced work" objective (Section 6.3) pre-loads the connected dataset (as a DataFrame-equivalent object), the results of the automatic analysis pass (summary statistics, detected anomalies, generated charts as inspectable objects, not just images), and any cleaning/feature-engineering already approved upstream — so the user is not starting from `pd.read_csv()` and redoing work the platform already did.
- **Bidirectional workflow integration:** code written in a notebook can be "promoted" into a Visual Workflow Builder node (Section 9), turning a one-off exploratory script into a reusable, schedulable pipeline step without a rewrite — and conversely, any workflow node can be "opened in notebook" to inspect or modify its underlying logic directly.
- **AI assistance in-line:** an embedded coding assistant can generate, explain, or debug cells on request, with the same explainability and provenance standards as the rest of the platform (Section 2.3, Design Principle 2) — generated code is inserted for review, not silently executed.
- **Full access to the model registry and experiment tracker:** a data scientist can load any prior model version, compare experiment runs, or pull evaluation artifacts directly into the notebook for custom analysis that the guided ML Experience (Section 7) does not surface by default.

### 10.3 Explicit Non-Goal

The Notebook Experience is not intended to compete with general-purpose data science notebook environments on raw flexibility (custom kernel management, arbitrary package ecosystems, GPU cluster orchestration for large-scale training). It is intended to be good enough that a power user does not feel compelled to leave the platform for routine advanced work, while accepting that some genuinely specialized workloads (e.g., large-scale distributed deep learning research) will reasonably continue to happen outside InsightAI, with InsightAI's role being to ingest the resulting model or output as a first-class artifact (via the Export/Import capability in Section 7.9 and Section 12) rather than to be the only place such work can happen.

---

## 11. Enterprise Features

### 11.1 Overview

Section 4.4 stated explicitly that enterprise governance is not a V1 priority. This section specifies what "enterprise-ready" means so that engineering makes V1 architectural choices (Section 14) compatible with these requirements landing in V2/V3, rather than requiring a rewrite. Retrofitting RBAC and audit logging onto a system not designed for them is materially more expensive than designing for them from the start, even if the UI for managing them ships later — this is why Section 14's data model includes organization, team, and permission scoping from the first schema design, even though the enterprise admin UI for managing it is a later-phase deliverable.

### 11.2 Organizational Hierarchy

```
Organization
   |
   +-- Teams (e.g., "Marketing Analytics", "ML Platform")
   |      |
   |      +-- Projects (e.g., "Q3 Churn Model", "Regional Sales Dashboard")
   |             |
   |             +-- Datasets, Workflows, Dashboards, Models
   |                 (each scoped to a project by default,
   |                  shareable to team or org level explicitly)
   |
   +-- Workspace Permissions (org-level defaults, inheritable
        and overridable at team/project level)
```

### 11.3 Role-Based Access Control (RBAC)

| Role | Typical Persona | Permissions |
|---|---|---|
| Org Admin | IT/Platform lead | Full control: billing, SSO config, all teams/projects, audit log access |
| Team Admin | Sam (BI lead), Dana (ML lead) | Manage team membership, create/archive projects, set team-level connector credentials |
| Project Contributor | Marcus, Alex | Create/edit datasets, workflows, dashboards, models within assigned projects |
| Project Viewer | Jordan, VP persona | View dashboards and reports; cannot edit or trigger workflows |
| Approver | Designated reviewer per project | Can approve Approval Gate nodes (Section 9.3) and promote models to production (Section 7.7), independent of whether they also hold Contributor rights |

The **Approver** role is deliberately separable from Contributor/Admin roles because in regulated or high-governance environments, the person who builds a model or workflow is often required, by policy, to be different from the person who approves it for production — a separation-of-duties requirement InsightAI's permission model must support natively rather than as a workaround.

### 11.4 Audit Logs

Every consequential action — dataset connection, cleaning-plan approval, model training run, model promotion/rollback, deployment, permission change, export, and API key creation/use — is recorded in an immutable, append-only audit log with actor, timestamp, action, affected resource, and (where applicable) the automated reasoning that informed the action (per Design Principle 2). Audit logs are exportable and queryable by Org Admins, and retention is configurable per compliance requirement (default 12 months, extendable). This log is the backbone that makes the human-approval framework in Sections 7.7 and 9.3 auditable rather than merely asserted.

### 11.5 API Keys and Programmatic Access

Org and Team Admins can issue scoped API keys (read-only, read-write, or workflow-trigger-only scopes) for programmatic access to datasets, model inference endpoints, and workflow triggers — enabling InsightAI to be embedded into a customer's existing systems (e.g., triggering a workflow from an internal cron job, or calling a deployed model's inference endpoint from a customer-facing application) rather than requiring all interaction to happen through the UI. Keys are scoped to a project by default, with organization-wide keys requiring explicit Org Admin issuance and appearing with elevated visibility in the audit log.

### 11.6 Version History

Datasets, cleaning plans, feature engineering configurations, models, workflows, and dashboards are all versioned objects. Version history supports diffing (what changed between two workflow versions), rollback (revert a dashboard or workflow to a prior version), and — critically for ML artifacts — full lineage reconstruction (given a deployed model version, reconstruct exactly which dataset version, feature engineering version, and training configuration produced it). This is not a "nice to have" for ML specifically: it is frequently a compliance requirement (Section 19, Regulatory Risks) that an organization be able to explain, after the fact, exactly how a production model was produced.

### 11.7 Enterprise Integrations and SSO

SSO (SAML/OIDC-based, integrating with common enterprise identity providers) is explicitly listed in the source requirements as a **future** capability rather than a V1 requirement, and this PRD preserves that sequencing (Section 20) — it is a common enterprise procurement blocker, meaning it gates the *timing* of enterprise sales motion, but building it before the core product-market fit is proven with the SMB/mid-market beachhead (Section 4) would be premature investment. The architecture (Section 14) reserves the identity/authentication layer as a pluggable component specifically so that SSO can be added without a broader rearchitecture.


---

## 12. Data Sources & Connectors

### 12.1 Launch Connector Set

| Source | Type | Notes |
|---|---|---|
| CSV | File upload | Zero-setup entry point; primary path for SMB and first-time evaluation users |
| Excel (.xlsx) | File upload | Includes multi-sheet detection and named-range awareness |
| Snowflake | Warehouse | Query pushdown supported (Section 12.3); primary enterprise warehouse target |
| Databricks | Warehouse / Lakehouse | Supports Delta table access; overlaps with Databricks' own tooling, addressed directly in Section 16 |
| PostgreSQL | Database | Common SMB/mid-market production database source |
| MySQL | Database | Common SMB/mid-market production database source |
| SQL Server | Database | Common enterprise legacy database source |
| REST APIs | Generic | Configurable auth (API key, OAuth2), pagination, and schema-inference for arbitrary JSON responses |

### 12.2 Connector Architecture Principles

1. **Read-first by default.** Every connector defaults to read-only access. Write-back (e.g., pushing a model's predictions into a warehouse table, or writing a cleaned dataset back to source) is a separate, explicitly granted permission per connector instance, surfaced clearly during setup so a customer's data/security team can evaluate exactly what access they are granting.
2. **Credential isolation.** Connection credentials are stored encrypted, scoped to the team/project that created them (Section 11.2), and never exposed in logs, exported workflows, or agent reasoning traces — a workflow can be shared without leaking the credentials it depends on; the recipient must supply their own authorized connection.
3. **Schema-change resilience.** Connectors detect upstream schema changes (a column renamed, dropped, or retyped in the source system) and surface this as a flagged event rather than allowing a scheduled workflow to fail silently or, worse, succeed while silently misinterpreting the new schema.

### 12.3 Compute Pushdown

For warehouse connectors (Snowflake, Databricks, and, for large tables, PostgreSQL/MySQL/SQL Server), InsightAI pushes down as much computation as possible — filtering, aggregation, join execution — to the source system rather than pulling raw rows into InsightAI's own compute for processing. This follows Design Principle 4 (Section 2.3) directly: it reduces data egress, respects the customer's existing investment in warehouse compute, and scales far better for enterprise-sized tables than a pull-everything-then-process approach. The trade-off, stated explicitly, is that pushdown logic must be maintained per warehouse dialect (Snowflake SQL vs. Databricks SQL vs. standard Postgres/MySQL/T-SQL), which is an ongoing engineering cost weighed against the alternative of degraded performance and higher customer data-egress cost — the team has assessed this trade-off as favoring pushdown for any table above a low-tens-of-thousands-of-rows threshold, with smaller tables processed directly in InsightAI compute for simplicity.

### 12.4 Anticipated Future Connectors

The source requirements explicitly call for anticipating future connectors. The following are documented here as directional intent, not committed roadmap items (commitment happens in Section 20 once a connector is prioritized based on customer demand):

- **Cloud warehouses/platforms:** BigQuery, Redshift, Microsoft Fabric/OneLake, Azure Synapse
- **SaaS business systems:** Salesforce, HubSpot, NetSuite, Stripe, Zendesk — high-value because they contain business-critical data that is otherwise trapped behind each vendor's own reporting UI
- **Event/streaming sources:** Kafka topics, Segment, and similar customer-data-platform event streams, for use cases requiring near-real-time analytics rather than batch/scheduled refresh
- **Unstructured sources:** document repositories (for use cases combining structured analytics with document-derived features), cloud object storage (S3/GCS/Azure Blob) for semi-structured data lakes
- **Data catalogs and semantic layers:** integration with existing metric-definition/semantic-layer tools (e.g., dbt's semantic layer or equivalent), so that InsightAI's automated dashboards reuse an organization's existing metric definitions rather than silently redefining "revenue" or "active user" — this is called out specifically because metric-definition drift between tools is a common, credibility-damaging failure mode for any new analytics tool entering an organization that already has established definitions (see Section 16, Competitive Analysis, and Section 19, Adoption Risks).

---

## 13. AI Agent Architecture

### 13.1 Why a Multi-Agent Architecture, Not a Single Model

A single, monolithic "do everything" model or prompt is difficult to evaluate, difficult to improve incrementally, and difficult to reason about from a governance standpoint — when something goes wrong, "which part of the system was responsible" needs a clear answer. InsightAI is instead built as a set of specialized agents, each with a narrow responsibility, a defined input/output contract, an independent evaluation suite, and an explicit confidence/escalation policy. This mirrors how a human data team actually divides labor (an EDA-focused analyst, a viz-focused analyst, a modeling specialist, a deployment engineer) and — as importantly — mirrors Design Principle 6 (Section 2.3): agents can be improved, replaced, or added independently as the underlying models and techniques evolve, without destabilizing the rest of the system.

### 13.2 Agent Roster

| Agent | Responsibility | Primary Consumers (Sections) |
|---|---|---|
| EDA Agent | Automated exploratory analysis: distributions, correlations, cardinality, class balance | Section 6.2, Section 7.2 |
| Visualization Agent | Chart type selection, chart generation, dashboard layout suggestions | Section 6.2, Section 8.2 |
| Analytics Agent | KPI computation, period comparison, trend/change-point detection, NL explanation | Section 8.3, Section 8.4 |
| Feature Engineering Agent | Templated + domain-informed feature generation and provenance tagging | Section 7.4 |
| Model Selection Agent | Algorithm shortlisting based on problem type and data characteristics | Section 7.5 |
| Training Agent | Orchestrates parallel training runs and staged hyperparameter search | Section 7.5 |
| Evaluation Agent | Computes leaderboard metrics, runs explainability analysis, flags fairness/bias concerns | Section 7.6 |
| Report Generation Agent | Produces executive-ready natural-language reports from dashboards/models | Section 6.3, Section 8.4 |
| Deployment Agent | Provisions inference endpoints, registers models, wires monitoring | Section 7.9 |
| Monitoring Agent | Tracks drift and performance decay, triggers the incremental-vs-retrain decision (Section 7.7), manages alerting | Section 7.7, Section 9.5, Section 11.4 |

### 13.3 EDA Agent

**Input:** a validated dataset (or a warehouse query result). **Output:** a structured profile object (not just prose) containing per-column statistics, detected relationships, missingness patterns, and a ranked list of "interesting findings" (e.g., unexpectedly high correlation between two columns, an unusual missingness pattern concentrated in a specific segment). **Confidence/escalation policy:** findings below a confidence threshold (e.g., a correlation that could plausibly be sampling noise given the dataset size) are labeled as "worth investigating" rather than stated as findings, and the agent explicitly under-claims rather than over-claims — a design choice that trades off some perceived "wow factor" in early demos against long-term trust, which the team has assessed as the correct trade-off given that trust, once lost to a confidently wrong finding, is expensive to rebuild (Section 19).

### 13.4 Visualization Agent

**Input:** the EDA Agent's profile object plus the user's stated objective. **Output:** a ranked set of chart specifications (chart type, axes, grouping, and a rationale for why this chart was selected — e.g., "bar chart chosen over pie chart because there are 14 categories, and pie charts become unreadable above roughly 6"). The Visualization Agent encodes established data-visualization best practice as hard constraints rather than leaving chart-type selection purely to model judgment on every call — for example, it will not recommend a 3D chart for two-variable data, will not recommend a pie chart for more than ~6 categories, and defaults to accessible, colorblind-safe palettes (Section 15, Accessibility) — because these are settled design principles, not areas of genuine ambiguity where per-instance model judgment is likely to add value.

### 13.5 Analytics Agent

**Input:** dashboard/KPI configuration plus historical time-series data for each metric. **Output:** period-comparison figures, detected change points, and a structured decomposition (which segments/dimensions contributed most to a change). **Confidence/escalation policy:** as detailed in Section 8.4, causal language is explicitly avoided in favor of correlation-flagged contribution analysis unless a controlled comparison (e.g., a true A/B test result already present in the data) justifies stronger causal language.

### 13.6 Feature Engineering Agent

**Input:** the cleaned dataset, its schema, and the detected/selected target. **Output:** a set of candidate engineered features with provenance tags (Section 7.4) and an estimated relevance score per feature (computed via a fast proxy method — e.g., mutual information or a shallow model's feature importance — rather than requiring a full training run just to evaluate candidate features, which would be prohibitively slow). Low-relevance candidates are still surfaced (collapsed by default in the UI) rather than silently discarded, because a feature that looks low-relevance in isolation can still be valuable in combination with others, and a data scientist reviewing the platform's choices needs to see what was considered and rejected, not just what was kept (Design Principle 2).

### 13.7 Model Selection, Training, and Evaluation Agents

These three agents (Sections 7.5–7.6) operate as a tightly coordinated sub-pipeline: Model Selection produces a shortlist, Training executes it (with the staged hyperparameter search from Section 7.5) and reports interim progress so the UI can stream a live-updating leaderboard rather than a single blocking wait, and Evaluation takes the trained candidates and produces the comparison, explainability, and fairness analysis described in Section 7.6. They are kept as separate agents rather than one combined "modeling agent" specifically so that, for example, the Training Agent's compute-orchestration logic (Section 14) can be optimized and scaled independently of the Evaluation Agent's explainability logic, which has entirely different computational characteristics (the former is compute-bound and parallelizable across machines; the latter is often bound by explainability-method computation on a single trained model).

### 13.8 Report Generation Agent

**Input:** one or more dashboards, their KPIs, and Analytics Agent output. **Output:** a structured executive report (Section 8.4) with a defined template (headline summary, key metric movements with explanations, notable risks/anomalies, suggested next actions) rather than free-form generation — templating is a deliberate constraint that improves consistency and reviewability across reports, and it is far easier for a human reviewer to spot a factual error in a consistently structured report than in free-form prose that varies in structure every time.

### 13.9 Deployment Agent

**Input:** an approved model (post-Evaluation Agent, post-human-approval per Design Principle 1) and a target environment (staging/canary/production). **Output:** a provisioned, versioned inference endpoint, a model registry entry with full lineage (Section 11.6), and a monitoring hook automatically registered with the Monitoring Agent. **Escalation policy:** any deployment failure (provisioning error, failed health check post-deployment) triggers automatic rollback to the prior stable version and an immediate notification to the deploying user and, for production deployments, the project's designated Approver (Section 11.3) — silent partial-deployment states are treated as a severity-1 class of bug given the operational risk they represent.

### 13.10 Monitoring Agent

**Input:** live inference traffic (features and, where available, ground-truth outcomes) for every deployed model, plus scheduled data-arrival events for every scheduled workflow (Section 9.5). **Output:** drift measurements, performance-decay measurements, the incremental-vs-retrain recommendation (Section 7.7), and alerts. This is the agent with the broadest standing responsibility in the roster — it is what makes the "AI Data Team" vision (Section 5) a continuous presence rather than a one-time execution engine — and accordingly it has the most conservative escalation policy in the roster: any action that would change what is running in production (an incremental update deployment, a retrain promotion) follows the human-approval framework in Section 7.7 by default, and the agent's role is explicitly framed as "detect and recommend," with "act automatically" reserved for the subset of cases (Section 7.7's decision table) the team has evaluated as low-risk enough to warrant it, and even then only when the customer has opted in.

### 13.11 Agent Collaboration Model

Agents do not communicate via free-form natural language with each other by default — this is a deliberate architectural choice. Inter-agent communication uses structured, typed payloads (the same structured objects referenced as "Output" in each agent's description above), with natural language reserved for agent-to-human communication. This distinction matters for two reasons: **reliability** (structured payloads can be validated against a schema before being passed to the next stage, catching malformed intermediate output before it silently corrupts a downstream step, whereas free-form text passed between agents is a well-documented source of compounding error in multi-agent systems) and **evaluability** (a structured payload's correctness can be tested with conventional software tests; a free-form natural-language exchange between two agents is much harder to regression-test as the underlying models change). An orchestration layer (Section 14.5) is responsible for sequencing agent calls per the workflows described in Sections 6, 7, and 9, handling retries, and enforcing the Approval Gate checkpoints from Section 9.3 — the orchestration layer, not any individual agent, owns the "is a human approval required here" logic, so that this critical safety behavior lives in one auditable place rather than being re-implemented (and potentially re-implemented inconsistently) inside every agent.

### 13.12 Agent Evaluation Methodology

Section 20's roadmap milestones reference specific per-agent quality bars (e.g., 85% EDA finding-precision). This subsection specifies, at a high level, how those bars are actually measured, because a quality bar without a defined measurement methodology is not testable.

Each agent in the roster (Section 13.2) is evaluated against three components, run continuously in CI-style regression as well as periodically against fresh production samples:

1. **A static benchmark suite** — a curated, versioned set of inputs with known-correct or expert-annotated expected outputs (e.g., for the EDA Agent, a set of datasets with pre-identified true findings and known non-findings/traps designed to catch over-claiming). Every code or prompt change to an agent must run against its benchmark suite before deployment, and a regression below the agent's established baseline blocks deployment by default, consistent with the "treat statistical-correctness bugs as a distinct, higher-priority bug class" mitigation in Section 19.1.

2. **Sampled production review** — a rotating sample of real (anonymized, access-controlled) production agent outputs reviewed by a human evaluator against a defined rubric specific to that agent (e.g., the Visualization Agent's rubric checks chart-type appropriateness and accessibility compliance per Section 15; the Report Generation Agent's rubric checks the "forwardable without edit" bar directly). This catches quality issues the static benchmark suite does not anticipate, since real customer data is far more varied than any curated benchmark can fully cover in advance.

3. **Calibration tracking** — for agents that express confidence or make an escalate-vs-proceed decision (Sections 13.3, 13.10), the evaluation methodology separately tracks calibration (when the agent says it is confident, is it actually right more often than when it says it is uncertain) rather than accuracy alone, because a mis-calibrated agent that is simultaneously accurate on average but overconfident on its wrong answers is more dangerous than a less accurate but well-calibrated one, given Design Principle 1's reliance on confidence signals to decide what needs human escalation.

Results from all three components feed the per-agent evaluation dashboards referenced in Section 15 (Observability) and Section 21.3 (Quality and Trust metrics), and are reviewed explicitly at each roadmap phase gate (Section 20.1) as a condition of that phase's exit, not just tracked passively.

### 13.13 Extensibility

New agents are added by implementing a defined interface (structured input schema, structured output schema, a declared confidence/escalation policy, and an evaluation suite) and registering with the orchestration layer — this is what "modular and extensible" means concretely, per the requirement to explain agent collaboration while remaining modular. A future Marketplace (Section 18.5) is architecturally anticipated by this same interface: a third-party or customer-authored agent that conforms to the interface can, in principle, be registered into a customer's workspace without core platform changes, though marketplace-specific trust, sandboxing, and review requirements are out of scope for this document and will be specified separately before that capability ships.


---

## 14. Technical Architecture Overview

*This section is written for engineers making near-term implementation decisions. It describes the destination architecture and is explicit about which parts are needed for V1 versus which parts are correctly deferred — see Section 20 for the phased build plan. The single most important architectural decision this section makes is stated up front in 14.1, because it governs every other choice in this section.*

### 14.1 The Core Architectural Decision: Modular Monolith First, Microservices as Earned

A platform with this many functional domains (EDA, visualization, ML training, deployment, monitoring, workflow orchestration, notebook execution, connector management, RBAC/audit) can plausibly be decomposed into dozens of independently deployable microservices — and the long-term architecture in this section assumes that decomposition eventually happens. However, building all of that decomposition before a single customer has used the product is a well-documented failure mode: it multiplies operational surface area (deployment, inter-service networking, distributed tracing, service-to-service auth) faster than it delivers customer value, and it makes the exact boundaries wrong, because the right service boundaries are usually only discoverable after real usage patterns reveal where the actual coupling and scaling pressure lie.

**Decision:** InsightAI's V1 backend is built as a **modular monolith** — a single deployable Python/FastAPI application internally organized into clearly separated modules that mirror the eventual service boundaries described in Section 14.3 (EDA, visualization, ML training, workflow orchestration, connectors, identity/RBAC), communicating through well-defined internal interfaces rather than direct cross-module database access. This preserves the option to extract any module into its own service later — a codebase organized this way can be split module-by-module as scaling pressure demands, whereas a codebase built as microservices from day one but without real usage data to validate the boundaries is much more expensive to *consolidate* if the boundaries turn out wrong.

**The concrete trigger for extracting a module into its own service** is not a calendar date; it is one of: (a) the module's compute profile is fundamentally different from the rest of the system and is either bottlenecking or over-provisioning shared infrastructure (the clearest early candidate is ML **Training**, which is bursty and CPU/GPU-heavy in a way the rest of the API is not), (b) the module needs to scale or deploy independently for reliability reasons (the **Monitoring Agent**, Section 13.10, is a standing background process whose failure should never take down interactive dashboard requests), or (c) a team boundary has formed around the module and service extraction reduces deployment coordination overhead. Training and Monitoring are the two modules most likely to be extracted first, and Section 20 sequences that extraction explicitly rather than leaving it implicit.

### 14.2 High-Level System Diagram (Target State)

```
                         +---------------------+
                         |   React Web Client   |
                         +----------+----------+
                                    |
                                    v
                       +------------------------+
                       |     API Gateway         |
                       |  (auth, rate limiting,  |
                       |   request routing)      |
                       +-----------+------------+
                                    |
        +---------------------------+---------------------------+
        |                           |                           |
        v                           v                           v
+---------------+       +----------------------+       +------------------+
| Core Platform  |       | Agent Orchestration    |       | Connector          |
| API            |       | Layer                    |       | Management         |
| (modular       |       | (Section 13.11)          |       | Service            |
| monolith:      |       |                            |       |                    |
| datasets,      |<----->| Sequences agent calls,     |<----->| Credential vault,  |
| workflows,     |       | enforces Approval Gates,     |       | pushdown query      |
| dashboards,    |       | retries, structured I/O      |       | execution           |
| RBAC, audit)   |       +-------------+--------------+       +--------+---------+
+-------+-------+                     |                                 |
        |                             v                                 v
        |                +------------------------+          +--------------------+
        |                |   Agent Pool             |          |  Customer Data      |
        |                |  (Section 13.2 agents,   |          |  Sources            |
        |                |   each independently      |          |  (Snowflake,        |
        |                |   scalable/versioned)      |          |   Postgres, etc.)   |
        |                +-----------+--------------+          +--------------------+
        |                            |
        v                            v
+----------------+       +------------------------+
| Metadata Store  |       |  ML Training &          |
| (Postgres:      |       |  Compute Layer          |
|  orgs, teams,   |       |  (containerized jobs,   |
|  projects,      |       |   queue-managed,        |
|  workflow defs, |       |   GPU pool for deep     |
|  model registry,|       |   learning workloads)   |
|  audit log)     |       +-----------+------------+
+----------------+                    |
        |                             v
        v                +------------------------+
+----------------+       |  Model Registry &        |
| Object Storage  |<---->|  Feature Store            |
| (S3-compatible: |       |  (Section 14.4)           |
|  datasets,      |       +------------------------+
|  model          |
|  artifacts,     |
|  reports)        |
+----------------+
```

### 14.3 Component Responsibilities

| Component | Responsibility | V1 Deployment | Later-Phase Deployment |
|---|---|---|---|
| React Web Client | All user-facing UI (Sections 6–11) | Single SPA | Unchanged |
| API Gateway | AuthN/AuthZ enforcement, rate limiting, routing | Managed API gateway or lightweight reverse proxy | Same, with added regional routing for enterprise data-residency requirements |
| Core Platform API | Datasets, workflows, dashboards, RBAC, audit (modular monolith, Section 14.1) | Single FastAPI service | Split by module as triggers in 14.1 are met |
| Agent Orchestration Layer | Sequences agent calls, enforces approval gates, structured I/O validation | In-process module within the monolith for V1 | Extracted as its own service once agent call volume justifies independent scaling |
| Agent Pool | The 10 agents in Section 13.2 | Implemented as callable functions/classes within the monolith, backed by an LLM API and, where relevant, classical ML libraries | Each agent independently deployable and versioned; higher-traffic agents (EDA, Visualization) may run as dedicated services first |
| Connector Management | Credential vault, query pushdown, schema-change detection | Module within the monolith | Dedicated service, given distinct security/compliance surface (Section 15, Security) |
| ML Training & Compute Layer | Executes training jobs, hyperparameter search | Managed job queue (Section 14.4) with containerized workers | Dedicated service with GPU pool autoscaling |
| Metadata Store | System of record for orgs/teams/projects/workflows/model registry/audit log | Single managed Postgres instance | Read replicas; potential sharding by organization at very large scale |
| Object Storage | Datasets, model artifacts, generated reports | S3-compatible managed storage | Unchanged, with lifecycle policies for cost management (Section 15) |
| Model Registry & Feature Store | Versioned models with lineage; reusable engineered features | Implemented as tables/schemas within the metadata store and object storage for V1 (no dedicated feature-store product initially) | Potential adoption of a dedicated feature-store technology once feature reuse across projects at scale justifies it |

### 14.4 The Full Data Engineering Stack — When It Actually Gets Built

The source requirements for this PRD anticipate a substantial data engineering stack: Airflow for orchestration, Kafka for streaming, Spark for large-scale distributed processing, dbt for transformation, and Great Expectations (or an equivalent) for data quality validation. **All five are real, justified components of the target architecture — and none of them are required for V1.** This subsection states plainly when each is actually needed, because building them prematurely is one of the most common ways an early-stage team burns runway on infrastructure that has no user attached to it yet:

| Component | Purpose | Becomes Necessary When |
|---|---|---|
| Airflow (or a lighter equivalent like Prefect/Dagster) | Scheduling and dependency management for complex multi-step data pipelines | The Visual Workflow Builder's own scheduler (Section 9.5) — sufficient for single-tenant, moderate-complexity workflows — starts hitting limits on cross-workflow dependency management at scale, realistically once InsightAI is orchestrating pipelines for many enterprise customers with complex, interdependent DAGs |
| Kafka (or a managed equivalent) | Event streaming for near-real-time data sources and inter-service event propagation | A real customer need for near-real-time (sub-minute) analytics emerges (Section 12.4's event/streaming connectors), and/or the monolith's internal event needs (e.g., notifying the Monitoring Agent of new inference data) outgrow simple queue-based messaging |
| Spark (or a managed equivalent, e.g., a serverless Spark offering) | Distributed processing for datasets too large for single-machine pandas/Polars-based processing | Customer datasets routinely exceed the practical single-machine processing ceiling (a soft target of ~10–50 GB in memory-efficient columnar processing, revisited as hardware and tooling evolve) — until then, Section 12.3's compute-pushdown-to-the-warehouse strategy handles large-table processing more cheaply than standing up a Spark cluster |
| dbt | Version-controlled, testable SQL transformation layer | InsightAI's own internal transformation logic (cleaning/feature engineering, Sections 7.3–7.4) grows complex enough to benefit from dbt's testing/lineage tooling, and/or InsightAI integrates with a customer's *existing* dbt project (Section 12.4) rather than needing its own from day one |
| Great Expectations (or equivalent) | Automated data-quality validation rules | The platform's built-in validation (Section 7.2) needs to support customer-authored custom validation rules beyond InsightAI's built-in checks, typically an enterprise-tier requirement |

Terraform, Helm, and Kubernetes-based infrastructure-as-code are treated the same way: they are the correct target for managing a multi-service, multi-environment (staging/production, potentially multi-region) deployment, and the team should write V1 infrastructure-as-code from day one (even for a single monolith deployment) so that the *practice* of IaC is established early — but the full multi-service Helm chart topology implied by the target architecture in 14.2 is built incrementally as services are actually extracted (Section 14.1), not speculatively ahead of need.

### 14.5 Multi-Tenancy

InsightAI is a multi-tenant SaaS platform by default (Section 18's Community edition is the exception, designed for self-hosted single-tenant use). Tenancy isolation is enforced at three layers: **application layer** (every query and agent call is scoped by organization/project ID, enforced centrally in the Core Platform API rather than trusted to be applied consistently by every caller), **data layer** (row-level scoping in the metadata store; separate object-storage prefixes per organization), and **credential layer** (Section 12.2's per-team credential isolation extends the same principle to customer data-source connections). Enterprise customers requiring stronger isolation (dedicated compute, single-tenant deployment, or on-premises/VPC deployment) are a Business/Enterprise-tier capability (Section 18) built on the same codebase rather than a forked version — maintaining one codebase across tenancy models is treated as a hard engineering constraint given the maintenance cost of forked deployments observed industry-wide.

### 14.6 API Design

The public API (consumed by the API-key access pattern in Section 11.5, and by the React client itself) follows REST conventions for resource-oriented operations (datasets, workflows, models) and a task/job pattern (submit, poll status, retrieve result) for long-running operations (training runs, large dataset processing) rather than holding open long-lived synchronous connections — this is a standard and deliberate pattern given that training runs can take minutes to hours, and it keeps the API's behavior predictable and cacheable for the synchronous portions.

### 14.7 Core Data Model (Simplified)

The following entity relationships anchor the Metadata Store (Section 14.3) and are referenced throughout this document — Enterprise Features (Section 11.2), Version History (Section 11.6), and the API contracts in Section 22.3 all assume this shape. It is simplified for readability; a full entity-relationship diagram with all fields is an engineering artifact maintained outside this PRD.

```
Organization 1---* Team 1---* Project 1---* Dataset
                                    |            |
                                    |            +---* DatasetVersion (Section 11.6)
                                    |
                                    +---* Workflow 1---* WorkflowVersion
                                    |         |
                                    |         +---* WorkflowRun ---* NodeExecution
                                    |
                                    +---* Model 1---* ModelVersion
                                    |         |             |
                                    |         |             +--- lineage --> DatasetVersion
                                    |         |             +--- lineage --> WorkflowVersion (if produced by a workflow)
                                    |         |
                                    |         +---* Deployment ---* MonitoringRecord (Section 13.10)
                                    |
                                    +---* Dashboard 1---* DashboardVersion
                                              |
                                              +---* KPI ---* KPISnapshot (time series, Section 8.3)

User *---* Team (via RoleAssignment: role, Section 11.3)
AuditLogEntry: actor(User), organization, project(nullable), action, resource_type,
               resource_id, timestamp, reasoning(nullable, Section 2.3 Design Principle 2)
```

Three modeling decisions are worth calling out explicitly because they are easy to get wrong retroactively:

1. **Every mutable, consequential entity (Dataset, Workflow, Model, Dashboard) has a corresponding `*Version` entity**, and the parent entity is effectively a pointer to its current version plus a history of prior ones. This is what makes Section 11.6's rollback and diffing capability possible without bolting on a separate versioning system later — versioning is a property of the base schema, not an add-on.
2. **`ModelVersion` carries explicit lineage foreign keys** to the `DatasetVersion` and, where applicable, `WorkflowVersion` that produced it, rather than lineage being reconstructed after the fact from logs. This is a deliberate cost paid at write time (every training job must record its exact input versions) to make Section 11.6's lineage reconstruction and Section 19.5's compliance-documentation mitigation reliable rather than best-effort.
3. **`AuditLogEntry` is append-only and references entities by ID and type generically**, rather than having a separate audit table per entity type, so that Section 11.4's audit log remains a single, queryable system of record across every entity type in the platform rather than fragmenting into per-feature audit trails that are harder to review holistically during a compliance audit.

---

## 15. Non-Functional Requirements

Non-functional requirements are stated here as target bars with explicit trade-offs, not unconditional promises — an infinitely available, infinitely fast, infinitely secure system is not a real target; every NFR below is a deliberate point on a trade-off curve, and the trade-off is named.

| NFR | Target (V1) | Trade-off / Note |
|---|---|---|
| **Scalability** | Support datasets up to ~10M rows / ~500 columns processed directly; larger tables handled via compute pushdown (Section 12.3) | V1 does not target unbounded scale in InsightAI's own compute; leans on customer warehouse compute for very large tables by design, not as a limitation to be apologized for |
| **Reliability** | 99.5% success rate for synchronous API requests (excluding customer-side connector outages) | Long-running training jobs are measured separately (job completion rate, not request latency), since their failure modes are different in kind |
| **Availability** | 99.5% uptime SLA for Business/Enterprise tiers at launch, targeting 99.9% by V2 once the monolith's single points of failure (Section 14.1) are addressed via redundancy | 99.5% (V1) implies roughly 3.6 hours of monthly downtime budget; stated explicitly rather than implied, since "99.5%" sounds close to "99.9%" but represents roughly 5x more downtime budget |
| **Performance** | Automatic analysis flow (Section 6.2) completes in <60s for datasets under 1M rows/100 columns; NL query response in <5s for pre-profiled datasets | Larger datasets fall back to the sampled-first-pass approach noted in Section 6.2, trading first-pass statistical exactness for responsiveness |
| **Maintainability** | Modular monolith (Section 14.1) with enforced module boundaries, >80% automated test coverage on core platform logic, mandatory code review | Enforced module boundaries impose short-term development friction (cannot casually reach across modules) in exchange for long-term extraction flexibility — a deliberate, accepted cost |
| **Security** | Encryption at rest and in transit for all customer data and credentials; SOC 2 Type II readiness targeted for Enterprise-tier launch (Section 20); least-privilege service-to-service auth | SOC 2 Type II *certification* (as opposed to readiness) requires a multi-month observation period and is sequenced accordingly in the roadmap, not claimed prematurely |
| **Observability** | Structured logging, distributed tracing across the orchestration layer and agent pool (Section 13.11), and per-agent evaluation dashboards tracking accuracy/confidence-calibration over time | Agent-level observability (not just system-level uptime/latency) is treated as a first-class requirement, because a "healthy" system that is silently producing low-quality agent outputs is a failure mode traditional infrastructure monitoring will not catch |
| **Fault Tolerance** | Automatic retry with backoff for transient connector/agent failures; automatic rollback on failed deployments (Section 13.9); graceful degradation (e.g., dashboard remains viewable if the Analytics Agent's NL-explanation call fails, rather than the whole dashboard failing to render) | Graceful degradation is called out specifically because a common anti-pattern in AI-feature products is making the entire page depend on the AI call succeeding, which turns an enhancement into a single point of failure |
| **Auditability** | Every consequential action logged per Section 11.4, immutable and exportable | Directly supports Section 19's regulatory-risk mitigations; treated as a security/compliance requirement, not just a debugging convenience |
| **Cost Efficiency** | Staged hyperparameter search (Section 7.5) and tiered LLM model selection (cheaper/faster models for high-volume, low-stakes agent calls like schema detection; higher-capability models reserved for calls where quality materially matters, like the Report Generation Agent) to control the largest variable cost driver | This is the NFR most directly tied to business-model viability (Section 18) and is discussed further as a named risk in Section 19 |
| **Accessibility** | WCAG 2.1 AA target for the web client, including colorblind-safe default chart palettes (Section 13.4) and full keyboard navigability | Accessibility is treated as a launch requirement for the core product surfaces (dashboards, workflow builder), not a post-launch retrofit, given both the ethical case and the practical case that enterprise procurement increasingly requires accessibility compliance documentation |


---

## 16. Competitor Analysis

### 16.1 Competitive Landscape Overview

InsightAI does not have a direct one-to-one competitor, because it spans categories that are usually purchased separately (Section 2.1). This is simultaneously the source of its differentiation and its greatest go-to-market risk: prospects will evaluate InsightAI against best-in-class point solutions in each category, and InsightAI's automation story has to be compelling enough to justify displacing (or sitting alongside) tools the organization already trusts.

### 16.2 Comparison Table

| Competitor | Category | Core Strength | Core Weakness (relative to InsightAI's vision) | Primary Overlap Area |
|---|---|---|---|---|
| Power BI | BI / Dashboards | Deep Microsoft ecosystem integration, huge installed base, low cost within M365 bundles | Dashboard creation still requires a skilled builder; no native ML/AutoML depth; explanation of *why* metrics moved is manual | Analytics Experience (Section 8) |
| Tableau | BI / Dashboards | Best-in-class visualization flexibility and design control | Similar to Power BI: manual dashboard construction, no native end-to-end ML lifecycle, no agent-driven automation | Analytics Experience (Section 8) |
| Looker | BI / Semantic Layer | Strong semantic-layer/metric-governance model (LookML) | Requires significant upfront modeling investment; not designed for self-serve ML | Analytics Experience, Enterprise governance (Section 11) |
| DataRobot | AutoML / Enterprise ML | Mature automated ML lifecycle, strong enterprise trust in regulated industries | Narrower scope than InsightAI (ML-focused, not a unified BI+ML+workflow platform); historically higher price point | Machine Learning Experience (Section 7) |
| H2O.ai | AutoML | Strong open-source AutoML core, credible in data-science-led organizations | Less polished end-user BI/dashboard experience; requires more technical sophistication to operate | Machine Learning Experience (Section 7) |
| Dataiku | Data Science / MLOps Platform | Broad platform spanning data prep through MLOps, strong collaborative-notebook model | Complex, long implementation cycles typical of enterprise platform sales; less emphasis on autonomous agent-driven automation | ML Experience, Notebook (Section 10), Workflow Builder (Section 9) |
| Snowflake | Cloud Data Warehouse | Dominant enterprise data substrate; expanding into ML (Cortex) and apps | Warehouse-first, not experience-first; native ML/BI features are additive to the warehouse rather than a unified end-to-end product experience | Data Sources (Section 12); potential partner as much as competitor |
| Databricks | Lakehouse / ML Platform | Deep, technically excellent ML/data-engineering platform; strong with sophisticated data teams | Steep learning curve for business-analyst-type users; less accessible to the non-technical personas in Section 4 | ML Experience, Notebook, Data Engineering Stack (Section 14.4); potential partner as much as competitor |
| OpenAI (ChatGPT) | General-Purpose AI Assistant | Best-in-class general reasoning and conversational capability; massive brand recognition | Not connected to enterprise data by default; no native workflow execution, governance, versioning, or deployment infrastructure for data/ML work (Section 3.1, P9) | Overlaps only at the conversational-query layer (Section 8) |
| Claude (Anthropic) | General-Purpose AI Assistant | Strong reasoning and tool-use capability; increasingly used for agentic workflows | Same structural gap as ChatGPT: general-purpose, not purpose-built for the governed, auditable, warehouse-connected workflow InsightAI targets | Overlaps only at the conversational-query layer (Section 8) |
| Microsoft Fabric | Unified Data Platform | Deep Microsoft ecosystem bundling (Power BI + data engineering + ML in one SKU structure) | Ecosystem lock-in cuts both ways — a strength for existing Microsoft shops, a barrier for everyone else; automation depth in the AutoML/agent sense is less mature than InsightAI's vision | Broadest overlap of any competitor listed — spans BI, data engineering, and ML in one bundle |
| Google Vertex AI | Cloud ML Platform | Strong infrastructure-grade ML platform, deep integration with BigQuery and Google Cloud | Infrastructure-first, requires significant ML engineering expertise; minimal BI/dashboard-layer product surface | Machine Learning Experience (Section 7), Data Sources (Section 12) |

### 16.3 Differentiation Thesis

InsightAI's differentiated position rests on three claims, each stated with its counter-argument for intellectual honesty:

**Claim 1 — Unified surface reduces the handoff cost that Section 3.2 quantifies.** *Counter-argument:* a unified surface is only a genuine advantage if each individual capability (BI, AutoML, workflow) is good enough that customers do not need to "escape" to a specialized point solution for their hardest problems — a jack-of-all-trades product that is mediocre at each individual function loses to best-in-class point solutions on exactly the workflows that matter most. This is why Section 20's roadmap insists on reaching genuine quality bars (Section 21) on a narrow slice before expanding breadth, rather than shipping shallow versions of everything at once.

**Claim 2 — Agent-driven automation (Section 13) is a genuinely different mode of operation than "AI-assisted point solution," because it executes bounded multi-step workflows rather than answering isolated questions.** *Counter-argument:* every major incumbent listed above (Snowflake Cortex, Databricks' agent tooling, Microsoft Copilot integration into Fabric, Google's Vertex AI Agent Builder) is actively building toward the same agent-driven automation model, and several have a substantial data-gravity and distribution advantage — a customer already running their warehouse on Snowflake has a lower-friction path to trying Snowflake's native automation than switching to a new vendor. InsightAI's realistic window of differentiation is time-bound, not permanent, and Section 19 treats this as a named market risk rather than a theoretical one.

**Claim 3 — Governance-by-design (Design Principle 1, Section 11's audit/RBAC architecture) is a durable advantage in regulated and risk-conscious enterprise segments**, where "the AI did something to production and we can't fully explain why" is disqualifying, not just undesirable. *Counter-argument:* DataRobot and Dataiku (Section 16.2) have years of head start building exactly this kind of enterprise trust and compliance track record in regulated industries; InsightAI's governance architecture (Section 11, Section 14) is necessary to compete for this segment but not sufficient on its own — actual compliance certifications (Section 15, Security) and reference customers take real time to accumulate, which is why enterprise-segment focus is explicitly sequenced to V2/V3 (Section 20) rather than assumed at launch.

### 16.4 Focused SWOT: The Four Highest-Priority Competitive Threats

Section 16.2's table covers eleven competitors at a consistent level of detail. Four of them warrant a deeper, explicit SWOT because they represent the most plausible sources of either a lost deal (Databricks, Microsoft Fabric) or a long-term strategic erosion of InsightAI's differentiation (Snowflake, DataRobot). This is not a claim that the other seven are unimportant — it is a resourcing statement about where competitive-intelligence effort should concentrate first.

**Snowflake**
- *Strengths:* dominant warehouse market position gives it first-party access to the data InsightAI needs a connector to reach; Cortex (its native AI/ML layer) benefits from zero data-movement latency and trust already established with the customer's data/security team.
- *Weaknesses:* Snowflake's core business and organizational incentive structure is warehouse consumption, not workflow/UX polish for non-technical business users — a genuinely unified, agent-driven, explanation-first BI+ML experience (Section 2.1) is adjacent to, not central to, its business model.
- *Opportunities (for InsightAI):* position as complementary rather than competing — InsightAI as the experience layer on top of a customer's existing Snowflake investment (Design Principle 4) rather than asking a customer to choose one or the other.
- *Threats (to InsightAI):* if Cortex's automation depth closes the gap with InsightAI's agent orchestration (Section 13) while retaining Snowflake's zero-data-movement advantage, InsightAI's differentiation narrows specifically for the large segment of prospects already standardized on Snowflake.

**Databricks**
- *Strengths:* best-in-class technical depth across the full data engineering and ML lifecycle (Section 14.4's target stack largely mirrors capabilities Databricks already has mature and battle-tested); strong trust with sophisticated data science and ML engineering organizations.
- *Weaknesses:* the platform's learning curve and configuration surface area work against the non-technical personas (Priya, Jordan — Section 4.2) that InsightAI's automatic-analysis-first experience (Section 6.2) is specifically designed to serve; Databricks is not optimized for a business user getting a dashboard in an hour.
- *Opportunities (for InsightAI):* serve as the accessible, business-user-facing layer for organizations that already run Databricks for their heavy engineering workloads, positioning as complementary (Design Principle 4) rather than a replacement, similar to the Snowflake posture.
- *Threats (to InsightAI):* Databricks' substantial investment in its own agent and AI-assistant tooling could close the accessibility gap over time, and Databricks' existing enterprise sales relationships give it a distribution advantage InsightAI does not have at launch (Section 20).

**Microsoft Fabric**
- *Strengths:* the broadest single-vendor bundle of any competitor listed (Section 16.2) — BI (Power BI), data engineering, and ML in one SKU structure, backed by Microsoft's enterprise sales and procurement relationships and M365/Azure ecosystem lock-in.
- *Weaknesses:* breadth-first bundling historically trades off against depth and polish in any single capability; organizations outside the Microsoft ecosystem face real switching-cost friction to adopt it, which InsightAI's warehouse-agnostic posture (Design Principle 4) does not share.
- *Opportunities (for InsightAI):* win specifically among organizations not already deeply committed to the Microsoft stack, and among organizations that have tried Fabric's automation features and found them shallow relative to InsightAI's agent-driven depth (Section 13) — a claim that needs direct, ongoing competitive validation, not just assertion.
- *Threats (to InsightAI):* Fabric is the single competitor most likely to be bundled into a deal at effectively zero marginal cost for an existing Microsoft enterprise customer, which is a pricing dynamic InsightAI's usage-based model (Section 18.3) cannot easily counter with price alone.

**DataRobot**
- *Strengths:* years of accumulated enterprise trust and compliance track record specifically in regulated, high-stakes ML use cases (Section 16.5 below) — exactly the segment InsightAI has explicitly chosen not to lead with (Section 16.5, first paragraph below this SWOT block).
- *Weaknesses:* narrower scope than InsightAI's unified vision (Section 2.1) — strong on automated ML lifecycle, materially less developed on the BI/dashboard and natural-language-explanation surface (Section 8) that serves InsightAI's business-analyst and product-manager personas (Section 4.2).
- *Opportunities (for InsightAI):* the unified-platform thesis (Section 16.3, Claim 1) is most differentiated precisely against a point solution like DataRobot — an organization evaluating both is choosing between "excellent AutoML plus a separate BI tool" and "good-and-improving AutoML plus BI in one governed platform."
- *Threats (to InsightAI):* in the specific regulated verticals where DataRobot is strongest, its compliance and explainability track record (Section 7.6 for comparison) is a real, currently unmatched asset that InsightAI's Section 19.5-documented compliance roadmap will take years, not quarters, to approach.

### 16.5 Where InsightAI Should Not Compete Directly (V1–V2)

Given the counter-arguments above, the team's explicit position is to avoid head-on competition in two areas during the early roadmap: (1) highly regulated, high-stakes ML use cases (credit underwriting, clinical decision support) where DataRobot/Dataiku-class incumbents have deep, hard-won compliance track records — InsightAI's Explainability and Audit infrastructure (Sections 7.6, 11.4) is necessary preparation for eventually competing here, but reference customers and case studies need to be built in lower-stakes verticals first; and (2) large-scale, infrastructure-grade ML engineering (Databricks/Vertex AI's core audience) where organizations already have sophisticated ML platform teams who will reasonably view a unified BI+ML product as less configurable than assembling best-of-breed infrastructure themselves.

---

## 17. Industry Impact

### 17.1 Potential Impact by Domain

| Domain | Potential Shift | Realistic Timeframe | Evidence/Reasoning |
|---|---|---|---|
| Business Intelligence | From "dashboards someone builds for you" to "dashboards that build and explain themselves," shifting BI professionals' time toward metric governance and stakeholder interpretation rather than chart construction | 3–5 years for meaningful market-share shift | Contingent on natural-language and agent-driven BI reaching a trust bar most organizations currently reserve for human-built reports — a gradual trust curve, not a step change |
| Machine Learning | Continued acceleration of the trend (already underway via existing AutoML tools) from "ML requires a specialized team for every project" to "ML is a capability available to a much broader set of use cases," with specialized ML talent concentrated on genuinely novel or high-stakes problems | Already underway; InsightAI is a participant in an existing trend, not the originator of it | AutoML adoption trends and the broader industry move toward "citizen data science" predate this product |
| Enterprise Analytics | Compression of the time-to-insight cycle (Section 3.2), potentially changing what business questions are even considered askable — many questions currently go unasked because the expected turnaround discourages asking | 2–4 years for the cultural shift within an adopting organization, contingent on trust being established first | Directly follows from Section 3's problem analysis if the product achieves its stated turnaround targets |
| Data Engineering | Modest direct impact — InsightAI is a consumer of well-organized warehouse data (Section 12.3), not a replacement for the data engineering discipline that builds and maintains that warehouse | Limited direct disruption | Data engineering's core value (reliable, governed, well-modeled data pipelines) is a precondition for InsightAI's value, not a function it replaces |
| Decision Making | Potential shift toward decisions being made with a documented, explainable analytical basis by default (Section 8.4's explanation-first design), rather than being informed by analysis only when someone had the time to produce it | Highly organization-dependent | This is the most speculative claim in this table and is stated as a hope the product is designed to enable, not a guaranteed outcome — organizational decision culture is influenced by many factors beyond tooling availability |
| MLOps | Potential compression of the "model deployed, then abandoned without monitoring" failure pattern (Section 7.9), given that InsightAI structurally couples deployment to monitoring | 2–3 years, contingent on the incremental-vs-retrain framework (Section 7.7) proving reliable in production across diverse use cases | Directly follows from the architectural choice described in Section 7.9 |
| AutoML | Continued commoditization of the "train and compare several models automatically" capability (Section 7.5), pushing competitive differentiation in this specific sub-category toward orchestration, governance, and integration rather than raw automated-training quality alone | Already underway | Consistent with Section 16.3's Claim 2 counter-argument — this is an industry-wide trend InsightAI participates in, not a trend it uniquely creates |
| Predictive Analytics | Broader availability of forecasting and predictive modeling to teams without a dedicated data scientist (Section 7.8), potentially increasing the volume of forecasts produced across an organization — which raises its own governance question (who is accountable for a forecast an automated system produced with limited human review) | Ongoing | Directly follows from lowering the skill floor required to produce a forecast; the governance question is addressed structurally by Design Principle 1 but remains a genuine open organizational challenge, not fully solved by tooling alone |

### 17.2 Adoption Barriers

Three barriers are large enough to name explicitly, because underestimating them is a common cause of otherwise-good products failing to gain traction:

1. **Trust in automated decisions compounds slowly and can be destroyed quickly.** A single confidently-wrong insight, chart, or model recommendation early in a customer's experience can undo months of careful trust-building (this is why Section 13.3's EDA Agent is explicitly designed to under-claim rather than over-claim). Mitigation is addressed throughout the product design (Design Principle 2, explainability requirements in Section 7.6) rather than being a single feature — it is a cross-cutting concern.

2. **Organizational and role anxiety.** Section 5 explicitly states that InsightAI is not positioned or built as a headcount-reduction tool, but individual analysts and data scientists evaluating the product for their organization may reasonably perceive it as a threat to their role regardless of positioning, and that perception can become a source of internal resistance to adoption, independent of the product's actual technical merits. This is a real barrier that marketing and sales positioning must address directly (a topic outside this PRD's scope but flagged here because it materially affects the adoption curve engineering and product should plan around).

3. **Integration and migration friction with entrenched incumbent tools.** An organization with years of Power BI dashboards, Snowflake-native workflows, or Databricks pipelines already in production has switching costs (Section 16.2) that go beyond feature comparison — Design Principle 4 (bring your own warehouse) and the connector architecture (Section 12) are direct product responses to this barrier, but they reduce friction; they do not eliminate it.

### 17.3 Risks to the Broader Industry Narrative

This PRD's competitor analysis (Section 16.3) already names the risk that incumbents build equivalent automation natively. A second, distinct industry-level risk is worth naming here: if AI-driven analytics and ML automation products (InsightAI included) over-promise and under-deliver as a category — producing confidently wrong insights or unreliable models that damage real business decisions — the resulting trust deficit affects the whole category, not just the specific vendor responsible for a given failure. This is a collective-action-style risk that InsightAI cannot fully control, and it is one more reason (beyond the product-specific reasoning in Section 2.3 and Section 13) that the team's default posture favors calibrated, explainable, human-supervised automation over headline-grabbing but less reliable full autonomy.


---

## 18. Business Model & Pricing

### 18.1 Pricing Philosophy

Two cost structures have to be reconciled in this business model: a traditional per-seat SaaS structure (predictable for both InsightAI and the customer) and a usage-based compute structure (necessary because LLM inference and model training costs scale with actual usage, not with seat count, and a purely per-seat model would leave InsightAI exposed to heavy users consuming disproportionate compute at a fixed price — the same "unbounded usage risk" that Section 19 flags as a named business risk). The resulting model blends both: seats govern access and collaboration features; usage governs compute-intensive operations (training runs, high-volume agent calls, inference at scale).

### 18.2 Tier Structure

| Tier | Target Customer | Price Model (illustrative, to be validated against real willingness-to-pay data) | Included | Key Limitations |
|---|---|---|---|---|
| **Community** | Individual practitioners, evaluators, open-source contributors | Free, self-hosted | Core EDA, visualization, and single-user ML workflow (Sections 6–7, 9–10); community support only | No hosted infrastructure, no RBAC/multi-user features (Section 11), bring-your-own LLM API key (usage costs borne directly by the user), no SLA |
| **Professional** | Individual analysts/data scientists, small teams (1–10 users) | Per-seat monthly/annual SaaS | Hosted platform, all core objectives (Section 6.3), moderate included compute allowance, standard connectors (Section 12.1) | Team collaboration features limited to basic sharing; no formal RBAC hierarchy (Section 11.2–11.3); community + email support |
| **Business** | Mid-market teams (10–100 users), the primary beachhead segment (Section 4) | Per-seat plus usage-based compute overage | Full RBAC/org/team/project hierarchy (Section 11.2–11.3), audit logs (Section 11.4), API access (Section 11.5), version history (Section 11.6), priority support | SSO not included (Enterprise-only per Section 11.7); standard (not custom) SLA |
| **Enterprise** | Large organizations (2,000+ employees), regulated industries | Annual contract, custom-negotiated (seats + committed compute + platform fee) | Everything in Business, plus SSO, custom SLA, dedicated/VPC deployment options (Section 14.5), compliance documentation (Section 15, Security), dedicated customer success and solutions engineering | Requires a sales-led motion rather than self-serve signup, given deployment and compliance complexity |
| **Marketplace (future)** | All tiers | Revenue share on third-party workflows/agents (Section 13.13) | Discovery and distribution for customer- or partner-authored workflows and agents | Not scoped for build until the core extensibility interface (Section 13.13) is stable and proven internally first |

### 18.3 Usage-Based Compute Components

Billed separately from seats, and itemized transparently to customers (a deliberate choice — Section 19 names opaque AI-usage billing as a customer-trust risk in its own right):

- **Model training compute** — billed per training run based on compute-time and resource tier consumed (CPU vs. GPU), with the staged hyperparameter search (Section 7.5) and tiered algorithm shortlisting designed explicitly to control this cost without the customer needing to manage it manually.
- **Agent/LLM inference calls** — billed per call or bundled into monthly usage allowances by tier, with the tiered-model-selection cost control described in Section 15 (cheaper models for high-volume/low-stakes calls, higher-capability models reserved for calls where quality materially matters).
- **Deployed model inference** — billed based on request volume and the model's resource footprint, comparable in structure to standard cloud inference-hosting pricing.
- **Storage** — datasets, model artifacts, and version history (Section 11.6) billed on a standard per-GB basis beyond an included allowance per tier.

### 18.4 Professional Services and Support

Beyond the tiered support levels embedded in Section 18.2, two additional revenue lines are anticipated: **Professional Services** (implementation assistance for Enterprise customers migrating from an incumbent BI/ML stack, custom connector development for data sources outside Section 12.1's launch set, and custom workflow authoring) and **Premium Support Plans** (guaranteed response-time SLAs beyond the standard tier-included support, available as an add-on to Business-tier customers who want Enterprise-grade support responsiveness without the full Enterprise contract).

### 18.5 Marketplace (Future)

Once the agent extensibility interface (Section 13.13) and the Visual Workflow Builder's template/fork model (Section 9.4) have proven stable through real customer usage, a Marketplace allowing customers and partners to publish and monetize reusable workflows and custom agents becomes viable. This is explicitly sequenced as a **future** capability (Section 20) rather than a launch feature, because a marketplace's value is a function of the installed base and the platform's extensibility maturity, neither of which exist at launch — building marketplace infrastructure before either precondition is met would be speculative investment ahead of demonstrated need, the same anti-pattern flagged in Section 14.4 for the data engineering stack.

---

## 19. Risks & Mitigations

Each risk below is stated with a concrete mitigation, per the requirement that every identified risk carry a proposed response — a risk register without mitigations is a list of worries, not a planning tool.

### 19.1 Technical Risks

| Risk | Description | Mitigation |
|---|---|---|
| Modular monolith boundaries drawn incorrectly | Section 14.1's module boundaries, chosen before real usage data exists, may not match where scaling/team pressure actually emerges | Enforce boundaries via internal interfaces (not just convention) from day one so that re-drawing them later is a refactor, not a rewrite; revisit boundary decisions explicitly at each roadmap phase gate (Section 20) rather than only under emergency pressure |
| Agent output quality regresses silently as underlying LLM providers update their models | A model version upgrade from an LLM provider can change agent behavior in ways that are not caught by traditional software tests | Maintain the per-agent evaluation suites described in Section 13.1 as a continuously-run regression gate, not a one-time validation; pin model versions explicitly in production and roll forward deliberately, not automatically, on provider model updates |
| Time-series and leakage-detection logic (Section 7.2, 7.8) is subtly wrong for an edge case | Statistical correctness bugs in the ML pipeline are high-consequence because they produce confidently wrong models rather than visibly broken ones | Maintain a benchmark suite of datasets with known-correct answers (including deliberately constructed leakage/time-series edge cases) that every pipeline change must pass; treat statistical-correctness bugs as a distinct, higher-priority bug class from ordinary software defects |
| Compute-pushdown logic (Section 12.3) diverges in behavior across warehouse SQL dialects | A query that behaves correctly on Snowflake but subtly differently on Databricks SQL or T-SQL could produce inconsistent results per connector | Maintain a cross-dialect test suite exercising identical logical operations across all supported warehouse connectors; treat dialect-specific behavior differences as bugs to be reconciled, not accepted variance |

### 19.2 Business Risks

| Risk | Description | Mitigation |
|---|---|---|
| Compute/LLM cost structure erodes margin faster than pricing can adjust (directly related to Section 15's Cost Efficiency NFR) | Usage-based costs (Section 18.3) are volatile and provider-dependent; a pricing model set before real usage data exists may under-price actual cost-to-serve | Instrument usage and true cost-to-serve per customer from the first paying customer onward; build pricing-tier economics review into the roadmap phase gates (Section 20), not as an annual afterthought; maintain the tiered-model-selection cost controls (Section 15) as a continuously tuned lever, not a one-time design decision |
| Beachhead segment (Section 4) proves too small or too price-sensitive to build a sustainable business before Enterprise features (Section 11, Section 20) are ready | Mid-market analytics teams may have limited budget authority relative to the value delivered, and the Enterprise segment — where budget is larger — is intentionally sequenced later | Track leading indicators of Enterprise pull-through demand (inbound interest from larger organizations, even before the product is Enterprise-ready) throughout V1/V2 to validate or correct the sequencing assumption before committing further roadmap investment |
| Incumbent platforms ship equivalent automation natively (Section 16.3, Claim 2's counter-argument) | Snowflake, Databricks, and Microsoft have distribution advantages and are actively investing in this direction | Compete on integration breadth (Section 12) and cross-tool workflow orchestration (Section 9) rather than trying to out-build any single incumbent's native depth in their own ecosystem; treat "coexist with incumbents" (Design Principle 4) as a durable strategic posture, not just a launch-stage concession |

### 19.3 AI-Specific Risks

| Risk | Description | Mitigation |
|---|---|---|
| Confidently wrong insights or explanations (Section 8.4, Section 13.3) | An LLM-driven agent can produce fluent, plausible-sounding but factually incorrect analysis, which is more dangerous than an obviously broken output because it is more likely to be trusted without scrutiny | Explicit under-claiming design (Section 13.3), mandatory provenance/explainability (Design Principle 2), correlation-vs-causation discipline (Section 8.4) enforced structurally rather than left to prompt-level instruction alone, and human-approval gates (Design Principle 1) before anything automated reaches production or an external stakeholder |
| Model bias and fairness issues in trained models | Automated feature engineering and model selection (Section 7.4–7.5) could inadvertently encode or amplify bias present in training data, particularly across protected/sensitive attributes | Mandatory fairness/bias evaluation as part of the Evaluation Agent's output (Section 7.6, Section 13.7) for any model reaching the deployment step; model cards documenting known limitations (Section 7.6) as a non-optional deployment artifact |
| Prompt injection or adversarial manipulation of agent behavior via untrusted data content | A connected data source (Section 12) could contain content specifically crafted to manipulate an LLM-driven agent's behavior (e.g., text fields designed to alter the Feature Engineering Agent's or Report Generation Agent's output) | Treat all data-source content as untrusted input to agents, never as instructions; structured input/output contracts (Section 13.11) reduce (though do not eliminate) the attack surface by constraining what an agent's output can actually do downstream; the Approval Gate architecture (Section 9.3) ensures no agent output reaches production or an external system without human review, providing a backstop even if an individual agent is manipulated |
| Overreliance / automation complacency | Users may stop critically evaluating automated outputs over time simply because the system has been reliable so far ("automation complacency" is a well-documented human factors phenomenon, not specific to AI) | Preserve visible provenance and explanation on every output indefinitely, rather than progressively hiding "the work" as trust builds — the interface should not train users toward blind trust even as it earns genuine trust |

### 19.4 Security Risks

| Risk | Description | Mitigation |
|---|---|---|
| Customer data-source credential compromise | Connector credentials (Section 12.2) are a high-value target given the breadth of warehouse/database access they can grant | Encrypted credential storage, least-privilege connector permission scoping (read-only by default), credential isolation per team/project (Section 11.2), and no credential exposure in logs or exported workflow definitions |
| Cross-tenant data leakage in a multi-tenant architecture (Section 14.5) | A bug in application-layer or data-layer tenancy scoping could expose one customer's data to another | Defense-in-depth tenancy enforcement at application, data, and credential layers simultaneously (Section 14.5) rather than relying on a single enforcement point; mandatory tenancy-isolation test coverage as a release gate |
| Agent pool as an expanded attack surface | Each of the ten agents (Section 13.2) that can read customer data and, in some cases, trigger downstream actions represents a potential point of compromise | Structured, schema-validated I/O between agents and the orchestration layer (Section 13.11) limits what a compromised or manipulated agent can actually do; the Approval Gate architecture (Section 9.3) remains the ultimate backstop for any action with external effect |

### 19.5 Regulatory Risks

| Risk | Description | Mitigation |
|---|---|---|
| AI-specific regulation (e.g., requirements for explainability, human oversight, or impact assessments on automated decision systems) evolves faster than the product | Regulatory frameworks governing automated decision-making are actively developing across multiple jurisdictions and industries | Design Principle 1 (human approval for consequential actions) and mandatory explainability (Section 7.6) are built as core architecture, not compliance retrofits — this positions the product to adapt to tightening regulation rather than needing a redesign |
| Industry-specific compliance requirements (financial services, healthcare) block adoption in specific verticals | Regulated industries often have compliance requirements (model risk management frameworks, data handling rules) beyond general enterprise security expectations | Explicit decision (Section 16.5) to avoid leading with the most regulated, high-stakes verticals until compliance track record and certifications (Section 15, Security) are established; audit logging (Section 11.4) and lineage tracking (Section 11.6) are built to support future compliance documentation needs even before certification is pursued |
| Data residency and sovereignty requirements | Enterprise and international customers may require data to remain within specific geographic or legal boundaries | Multi-tenancy architecture (Section 14.5) anticipates dedicated/VPC deployment for Enterprise tier; regional deployment topology is a named future architecture consideration (Section 14.3's API Gateway component) rather than an unaddressed gap |

### 19.6 Market Risks

| Risk | Description | Mitigation |
|---|---|---|
| Category confusion — prospects do not understand what InsightAI is because it spans multiple established categories (Section 16.1) | A product that is "BI plus AutoML plus workflow automation plus agents" can be harder to position and sell than a single-category point solution | Lead go-to-market messaging with the specific, narrow wedge workflows (auto-EDA-to-dashboard, CSV-to-deployed-model) that are concretely demonstrable, rather than the full unified-platform vision, until the product has enough reference customers to support the broader positioning |
| General-purpose AI assistants (Section 16.2) narrow the perceived gap over time as they add tool-use and connector capabilities | ChatGPT/Claude-class assistants are rapidly gaining agentic and tool-use capability, which could erode the "general-purpose AI can't execute governed workflows" differentiation (Section 3.1, P9) faster than expected | Durable differentiation shifts toward the governance, audit, and warehouse-native integration depth (Section 11, Section 12) that a general-purpose assistant is structurally less likely to prioritize, given different target use cases; monitor this specific risk closely as an explicit input to strategy reviews at each roadmap phase |

### 19.7 Adoption Risks

| Risk | Description | Mitigation |
|---|---|---|
| Organizational/role anxiety slows adoption (Section 17.2) | Individual analysts and data scientists evaluating the product may perceive it as a threat to their role | Product design that visibly augments rather than replaces (Design Principle 1's human-approval framework is as much an adoption-risk mitigation as a safety mitigation); positioning and sales enablement addressing this directly (outside this PRD's scope, but flagged as a dependency for go-to-market) |
| Metric-definition conflicts with existing BI tools (Section 12.4) | InsightAI's automated dashboards could define a metric (e.g., "active user") differently from an organization's existing, trusted definition, damaging credibility on first use | Prioritize semantic-layer/metric-definition integration (Section 12.4) as early as the roadmap can support it once initial traction validates demand; in the interim, make metric definitions used in any generated dashboard explicitly visible and editable, never silently assumed |

### 19.8 Operational Risks

| Risk | Description | Mitigation |
|---|---|---|
| Single-monolith deployment (Section 14.1) creates broader blast radius for incidents during V1 | A bug or outage in the modular monolith affects all functional domains simultaneously, unlike a microservices architecture where failures are more contained | Accepted, named trade-off for V1 (Section 14.1); mitigated via the graceful-degradation NFR (Section 15, Fault Tolerance) so that, e.g., an agent-pool failure does not take down core dashboard viewing; the concrete extraction triggers in Section 14.1 exist specifically to resolve this risk as scale demands it |
| On-call and incident-response processes not yet mature for an AI-agent-driven system, where "the system is up" and "the system is producing correct output" are different failure modes | Traditional infrastructure monitoring catches the former but not the latter (Section 15, Observability) | Per-agent evaluation dashboards (Section 15) tracking output quality/calibration over time, treated as a first-class on-call signal alongside conventional uptime/latency monitoring, from the first production deployment onward |


---

## 20. Product Roadmap

### 20.1 Roadmap Philosophy

This roadmap sequences the full vision described in Sections 2–17 into phases that each prove a specific, falsifiable hypothesis before the next phase's investment is committed. Section 14.1's modular-monolith decision and Section 14.4's "data engineering stack, built when earned" principle are the architectural expressions of this same philosophy: build the narrowest thing that proves the value, and let real usage — not speculation — justify the next increment of complexity.

Each phase below states: **engineering priorities**, **expected capabilities at phase exit**, **dependencies from prior phases**, and **measurable milestones** that gate progression to the next phase. A phase is not "done" on a calendar date; it is done when its milestones are met, and the team should be willing to extend a phase rather than advance on a fixed schedule with unmet milestones — advancing on schedule rather than on evidence is how roadmaps quietly become the 37-service, everything-at-once architecture this philosophy is explicitly designed to avoid.

### 20.2 Research Phase

**Goal:** validate that the core automated-analysis experience (Section 6.2) can meet its quality and trust bar before any product surface is built around it.

| Category | Detail |
|---|---|
| Engineering priorities | Build a throwaway prototype of the EDA Agent and Visualization Agent (Section 13.3–13.4) against a diverse benchmark set of real-world CSVs; establish the evaluation methodology (Section 15, Observability's per-agent evaluation dashboards) before building the agents that will be measured by it |
| Expected capabilities at exit | A benchmark suite with known-correct findings for a diverse set of datasets; a working prototype (not production-quality) that can be scored against it |
| Dependencies | None — this is the starting phase |
| Measurable milestones | EDA Agent finding-precision (proportion of surfaced findings judged correct/useful by manual review) exceeds an internally set bar (recommended starting target: 85%, revisited once real data is available) across the benchmark suite; chart-selection appropriateness (Section 13.4) judged correct by manual review for at least 90% of benchmark cases |

### 20.3 MVP

**Goal:** ship the narrowest end-to-end slice that delivers on Section 3's core promise for a single objective, to a small number of design-partner customers, and validate willingness to pay.

| Category | Detail |
|---|---|
| Engineering priorities | Core Platform API (Section 14.3) as a modular monolith; CSV/Excel connector plus one warehouse connector (Snowflake, given its market position per Section 16.2); the automatic analysis flow (Section 6.2) in production quality; one full objective path end-to-end — "create a dashboard" (Section 8.2) — rather than all six objectives from Section 6.3 |
| Expected capabilities at exit | A user can connect a CSV or Snowflake table, get an automatic analysis (Section 6.2), and produce and share a dashboard (Section 8.2) with NL explanations (Section 8.4) — no ML training, no workflow builder, no notebook, no RBAC beyond basic single-team sharing |
| Dependencies | Research Phase's validated EDA/Visualization Agent quality bar |
| Measurable milestones | 5–10 design-partner customers using the product on real (not sample) data; automatic analysis flow meets the <60s performance target (Section 15) on real customer datasets, not just benchmark data; at least one design partner converts to a paid pilot |

### 20.4 Version 1

**Goal:** complete the core objective set from Section 6.3 and prove the second major value pillar — automated ML — alongside the BI pillar already validated in MVP.

| Category | Detail |
|---|---|
| Engineering priorities | Machine Learning Experience end-to-end (Section 7: validation through deployment, excluding the full incremental-vs-retrain automation in 7.7, which ships in V2 once there is a production model population large enough to make the policy meaningful); Notebook Experience (Section 10); basic Visual Workflow Builder (Section 9, without the full node taxonomy — Source, Transform, ML, and Action nodes only, deferring Control Flow's Approval Gate enforcement complexity, though a simple manual-approval step ships as a minimum viable safety gate); remaining launch connectors (Section 12.1: Databricks, PostgreSQL, MySQL, SQL Server, REST APIs); Professional and Business pricing tiers (Section 18.2) |
| Expected capabilities at exit | Full "CSV/warehouse to deployed, monitored model" path (Section 7.9); full "open a notebook for advanced work" path (Section 10); reusable workflows for the four node categories shipped; self-serve signup and billing for Professional/Business tiers |
| Dependencies | MVP's validated dashboard/BI pillar and initial paying customers |
| Measurable milestones | Time from dataset connection to first deployed model (Section 21) meets its target for at least a majority of tracked customer sessions; Business-tier retention (Section 21) tracked for the first cohort; Training Agent extracted into its own service (Section 14.1's first concrete extraction trigger) once training-job volume justifies it |

### 20.5 Version 2

**Goal:** complete the Enterprise readiness bar (Section 11) and the full agent roster's standing/monitoring capability (Section 13.10, Section 7.7), enabling the Enterprise sales motion to begin in earnest.

| Category | Detail |
|---|---|
| Engineering priorities | Full RBAC/org/team/project hierarchy and Approver role (Section 11.2–11.3); audit logs (Section 11.4); API keys (Section 11.5); version history and full lineage (Section 11.6); SSO (Section 11.7); the full incremental-vs-full-retrain decision framework (Section 7.7) in production, now justified by V1's accumulated production-model population; Monitoring Agent extracted into its own service (Section 14.1's second concrete extraction trigger); Guided Mode (Section 6.4); Report Generation Agent (Section 13.8) reaching its "forwardable to a VP" quality bar (Section 21) |
| Expected capabilities at exit | Enterprise tier sellable (Section 18.2) with SSO and compliance documentation in progress; standing monitored models and workflows (the "AI Data Team" vision, Section 5, becomes real rather than aspirational); SMB Owner/Operator persona (Section 4.2) served via Guided Mode |
| Dependencies | V1's production model population (for 7.7's policy tuning) and initial Business-tier customer base (for RBAC/audit feature validation against real organizational structures) |
| Measurable milestones | SOC 2 Type II observation period initiated (Section 15, Security); at least one Enterprise-tier contract closed; incremental-vs-retrain framework's automatic actions (Section 7.7) show no customer-reported incidents of inappropriate automatic promotion during the opt-in automatic-promotion pilot; Report Generation Agent output requires no human edit before distribution in at least 80% of a sampled evaluation set |

### 20.6 Version 3

**Goal:** broaden connector and data-engineering depth to serve the Large Enterprise Analytics Org persona (Section 4.2) at scale, and begin building toward the Marketplace.

| Category | Detail |
|---|---|
| Engineering priorities | Expansion connectors from Section 12.4's anticipated list, prioritized by demonstrated V2 customer demand rather than the full list at once; data engineering stack components from Section 14.4 introduced individually as their specific triggers are met (most likely Airflow-class orchestration first, given multi-customer workflow complexity growth); dedicated/VPC deployment option (Section 14.5) for the most compliance-sensitive Enterprise accounts; Marketplace foundation work (Section 13.13's extensibility interface hardened for third-party use, Section 18.5) |
| Expected capabilities at exit | Large Enterprise Analytics Org persona fully served (Section 4.2); at least one non-CSV/warehouse data engineering pattern (e.g., a streaming or event-based source, Section 12.4) in production for a real customer use case; Marketplace interface stable enough for a small, curated set of early third-party or customer-authored workflows |
| Dependencies | V2's enterprise feature set and compliance progress; sustained multi-tenant scale sufficient to justify the additional infrastructure named in Section 14.4 |
| Measurable milestones | SOC 2 Type II certification achieved; multiple Enterprise-tier accounts with dedicated/VPC deployments in production; first third-party or customer-authored Marketplace workflow published and used by a different organization than its author |

### 20.7 Long-Term Vision

Beyond Version 3, the roadmap converges on the full "AI Data Team" vision described in Section 5 and the full multi-service target architecture described in Section 14.2: the majority of the agent roster (Section 13.2) operating as independently scaled services, the full data engineering stack (Section 14.4) available where customer scale justifies it, a mature Marketplace (Section 18.5) with third-party agent and workflow contributions, and Guided Mode (Section 6.4) mature enough to serve as the default experience for the majority of new signups rather than a persona-specific mode. This document does not commit to specific milestones this far out — per Section 20.1's philosophy, that commitment is made phase by phase, based on evidence accumulated in the phases preceding it, not speculated years in advance.

---

## 21. Success Metrics

Metrics are grouped by what they validate, because a single undifferentiated KPI dashboard makes it easy to optimize a metric that looks good without validating the thing that actually matters (e.g., high API usage that reflects an inefficient client polling pattern rather than genuine value delivered).

### 21.1 Adoption and Engagement

| Metric | What It Validates | Notes |
|---|---|---|
| Weekly Active Organizations / Weekly Active Users | Baseline product engagement | Tracked separately from seat count, since seat count reflects contract size, not actual usage |
| Objective completion rate (Section 6.3) — proportion of started objectives (dashboard, model, workflow) that reach a completed, shared/deployed artifact | Whether the guided flows (Sections 6–10) are actually usable end-to-end, not just individually impressive in isolated steps | A low completion rate with high starts indicates a specific friction point worth root-causing, not just a general "engagement" problem |
| Workflow reuse rate (Section 9.4) — proportion of workflows run more than once, or forked | Whether Design Principle 5 (reusability) is actually being realized in practice, not just architecturally possible | A platform where every workflow is used exactly once has not really delivered on the reusability thesis regardless of raw workflow-creation volume |

### 21.2 Time Saved (Directly Tied to Section 3.2's Cost-of-Status-Quo Estimate)

| Metric | Target Direction | Notes |
|---|---|---|
| Time from dataset connection to first shared dashboard | Minutes, not days (Section 3.1, P2) | Measured against the status quo baseline gathered from design-partner interviews (Section 20.3), not an assumed baseline |
| Time from dataset connection to first deployed model | Hours, not weeks (Section 3.1, P3–P6) | Tracked as a full distribution (median and 90th percentile), not just an average, since ML task complexity varies widely by use case |
| Dashboard generation time (automatic analysis flow, Section 6.2) | <60 seconds for the target dataset size range (Section 15) | Directly measurable, not self-reported |
| Model deployment time (Section 7.9, from approved model to live endpoint) | Minutes | Distinct from total model-development time; isolates the Deployment Agent's specific contribution |

### 21.3 Quality and Trust

| Metric | What It Validates | Notes |
|---|---|---|
| Per-agent evaluation scores (Section 15, Observability) | Whether agent output quality is holding steady or regressing over time, especially across underlying LLM provider updates (Section 19.1) | Tracked continuously, not just at release time, per Section 19.1's mitigation |
| Model accuracy improvement over customer's prior baseline (where a customer has an existing model to compare against) | Whether the AutoML pipeline (Section 7.5) is actually competitive, not just automated | Only measurable for customers migrating from an existing modeling process — a self-selected subset, and treated as such in analysis, not generalized without caveat |
| Report Generation Agent "forwardable without edit" rate (Section 20.5's V2 milestone) | Whether the executive-report quality bar (Section 8.4) is genuinely met | Measured via sampled human review, not a proxy metric, since this is fundamentally a subjective-but-assessable quality bar |

### 21.4 Business Metrics

| Metric | What It Validates | Notes |
|---|---|---|
| Enterprise and Business tier retention (annual and logo) | Whether the product delivers sustained value, not just first-session novelty | Tracked separately by tier, since Section 18's tiers serve different segments with different value-realization timelines |
| API usage volume and diversity of endpoints used (Section 11.5) | Whether InsightAI is being embedded into customer workflows (a stickier integration pattern) versus used only via the UI | High API usage concentrated on a narrow set of endpoints (e.g., only inference calls) suggests a different integration depth than broad usage across dataset, workflow, and model endpoints |
| Cost reduction / capacity expansion reported by customers (Section 3.2, Section 5) | Whether the core value proposition (time and cost savings, or equivalently, more analytical work getting done with the same team) is being realized | Necessarily self-reported in part, since it depends on counterfactual estimation the customer is best positioned to make; corroborated where possible against the directly measurable time-saved metrics in 21.2 |
| Gross margin on usage-based compute (Section 18.3) | Whether Section 19.2's cost-structure risk is being managed successfully | Tracked per tier and per customer cohort, not just in aggregate, since usage patterns vary significantly by customer size and use case |

### 21.5 Guardrail Metrics and Review Cadence

Every metric in Sections 21.1–21.4 can, in principle, be improved in a way that does not reflect genuine customer value — a general risk with any KPI-driven roadmap, and one worth naming explicitly rather than assuming away. Two guardrails apply across the full metric set:

1. **No adoption or time-saved metric is reviewed without its corresponding quality metric alongside it.** For example, "time from dataset connection to first deployed model" (Section 21.2) improving because the Training Agent's time budget (Section 7.5) was quietly shortened, at the cost of the leaderboard's model quality, would be a false improvement — this is why Section 21.2's speed metrics and Section 21.3's quality metrics are reviewed together at every phase gate (Section 20.1), never in isolation.
2. **Objective completion rate (Section 21.1) is reviewed alongside downstream outcome signals, not treated as a terminal success signal on its own.** A dashboard being "completed" (shared) is not the same as it being used or trusted by its intended audience over time — where feasible, downstream signals (a shared dashboard being viewed again in a subsequent week, a deployed model remaining in production past its first monitoring cycle without rollback) are tracked as secondary confirmation.

Metrics are formally reviewed at each roadmap phase gate (Section 20.1) as a condition of phase progression, with lightweight informal tracking continuously in between. This cadence is deliberate: reviewing metrics only at major gates, rather than continuously chasing weekly fluctuations, is intended to keep the team focused on the phase's actual exit criteria (Section 20.2–20.7) rather than over-indexing on short-term metric noise.

---

## 22. Appendices

### 22.1 Glossary

- **Agent** — a narrow-responsibility, independently evaluable AI component with a defined input/output contract (Section 13).
- **Approval Gate** — a workflow node type that requires explicit human approval before execution can proceed (Section 9.3).
- **Compute Pushdown** — executing data processing operations on the customer's own warehouse rather than pulling raw data into InsightAI's compute (Section 12.3).
- **Concept Drift** — a shift in the relationship between input features and the target variable, distinct from covariate drift (a shift in the features themselves) (Section 7.7).
- **Guided Mode / Power Mode** — the two planned user-experience modes; Power Mode assumes the user knows their objective, Guided Mode translates business-language questions into the correct objective (Section 6.4).
- **Lineage** — the reconstructable chain from a deployed model or published dashboard back through every dataset version, transformation, and configuration that produced it (Section 11.6).
- **Modular Monolith** — a single deployable application internally organized into clearly separated, independently-extractable modules (Section 14.1).
- **Objective** — the user's stated goal after the automatic analysis flow completes (create a dashboard, train a model, and so on) (Section 6.3).
- **Orchestration Layer** — the component responsible for sequencing agent calls, enforcing Approval Gates, and validating structured inter-agent I/O (Section 13.11).
- **Provenance** — the traceable origin of any engineered feature, cleaning decision, or generated insight back to its source data and the transformation applied (Section 7.4).

### 22.2 Explicit Assumptions Made in This Document

This document makes a number of assumptions where the source requirements did not specify a detail. They are collected here for visibility and should be revisited as real customer and market data becomes available:

1. Illustrative pricing figures and cost-of-status-quo estimates (Sections 3.2, 18.2) are directional placeholders for planning discussion, not validated numbers, and are explicitly flagged as such at each point of use.
2. The specific quality-bar thresholds proposed in Section 20 (e.g., 85% EDA finding-precision, 80% report-forwardable-without-edit rate) are starting targets for the team to calibrate against, not empirically derived figures.
3. The technology choices named in Section 14 (FastAPI/Python for the core platform, React for the frontend, Postgres for the metadata store, S3-compatible object storage) are treated as reasonable, conventional defaults for this problem space, chosen for concreteness in the architecture discussion rather than as a constraint the team could not reasonably revisit during implementation.
4. The competitor comparison in Section 16 reflects each competitor's general market positioning as commonly understood; it is not based on hands-on competitive testing of every listed product's current feature set, and should be validated against current competitor documentation before being used externally (e.g., in sales enablement material).

### 22.3 Illustrative API Contracts

These examples are illustrative of the API design principles in Section 14.6 (resource-oriented for synchronous operations, submit/poll/retrieve for long-running ones) and are not a final API specification — a full API reference is a separate engineering deliverable, not part of this PRD. They are included here so that engineers reading this document have a concrete sense of what "connect a dataset" and "train a model" actually look like as API calls, consistent with Section 11.5's API-key-based programmatic access.

**Connecting a dataset (synchronous, resource-oriented):**

```
POST /v1/datasets
Authorization: Bearer <scoped API key>

Request body:
{
  "source_type": "warehouse_query",
  "connector_id": "conn_snowflake_prod_01",
  "query": "SELECT * FROM analytics.customer_orders WHERE order_date >= '2026-01-01'",
  "project_id": "proj_9f21a",
  "display_name": "Customer Orders — 2026 YTD"
}

Response (201 Created):
{
  "dataset_id": "ds_4a7c1e",
  "status": "profiling_in_progress",
  "row_count_estimate": 842000,
  "schema_preview": [
    {"column": "order_id", "inferred_type": "string", "is_likely_key": true},
    {"column": "customer_id", "inferred_type": "string", "is_likely_key": false},
    {"column": "order_date", "inferred_type": "datetime", "is_likely_key": false},
    {"column": "order_total", "inferred_type": "float", "is_likely_key": false}
  ],
  "profile_result_url": "/v1/datasets/ds_4a7c1e/profile"
}
```

The automatic analysis flow (Section 6.2) begins as soon as the dataset resource is created; `profile_result_url` is polled (or subscribed to via webhook, for integration use cases) rather than held open synchronously, since profiling a large warehouse query can take longer than a typical HTTP request timeout.

**Submitting a training job (asynchronous, job-pattern):**

```
POST /v1/training-jobs
Authorization: Bearer <scoped API key>

Request body:
{
  "dataset_id": "ds_4a7c1e",
  "target_column": "churned_within_90_days",
  "problem_type": "classification",
  "algorithm_shortlist": "auto",
  "time_budget_minutes": 20,
  "interpretability_preference": "balanced"
}

Response (202 Accepted):
{
  "job_id": "job_7d3f90",
  "status": "queued",
  "poll_url": "/v1/training-jobs/job_7d3f90"
}

--- later ---

GET /v1/training-jobs/job_7d3f90

Response (200 OK):
{
  "job_id": "job_7d3f90",
  "status": "completed",
  "leaderboard": [
    {"model_id": "mdl_a1", "algorithm": "gradient_boosted_trees", "metric_f1": 0.812, "inference_latency_ms_p50": 4},
    {"model_id": "mdl_a2", "algorithm": "logistic_regression", "metric_f1": 0.761, "inference_latency_ms_p50": 1},
    {"model_id": "mdl_a3", "algorithm": "random_forest", "metric_f1": 0.798, "inference_latency_ms_p50": 6}
  ],
  "recommended_model_id": "mdl_a1",
  "explainability_report_url": "/v1/models/mdl_a1/explainability"
}
```

Note that deployment is a deliberately separate call from training completion — per Design Principle 1 and Section 7.9, a trained model is never automatically deployed by the training-job API itself; a distinct, explicit `POST /v1/deployments` call (omitted here for brevity) is required, and that call is what the Approval Gate and audit-log requirements (Sections 9.3, 11.4) attach to.

### 22.4 Open Questions for Future Revisions of This Document

- What is the actual (not illustrative) willingness-to-pay across the Professional/Business/Enterprise tiers, and does the tier structure in Section 18.2 need to change once real pricing data exists?
- Does the beachhead persona sequencing in Section 4 (Business Analyst, Data Analyst, ML Engineer first) hold up against real design-partner usage data from the MVP phase (Section 20.3), or does actual usage reveal a different natural entry point?
- At what specific usage threshold does each data-engineering-stack component in Section 14.4 actually need to be built, in concrete terms (e.g., a specific number of concurrent enterprise customers, or a specific aggregate data volume) rather than the qualitative triggers currently stated?
- How should the Marketplace's (Section 18.5) trust, review, and sandboxing model work in detail once that phase is reached — this document explicitly defers that specification rather than guessing at it prematurely.

---

*End of document. This PRD is expected to be revised at each roadmap phase gate (Section 20.1); where a section's assumptions are invalidated by real customer or market evidence, that section should be updated rather than left to silently diverge from how the team is actually building the product.*