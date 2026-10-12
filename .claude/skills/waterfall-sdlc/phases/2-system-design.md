# Phase 2: System design (architecture)
**Gate:** G2 Architecture baseline (PDR)
**Deliverables:** [architecture document](../templates/architecture.md), [ADRs](../templates/adr.md), threat model, master test plan

## Goal
Decide **how** the system is structured to meet the SRS, especially its NFRs, and **choose the technology stack**. Set the strategies for security, data, integration, reliability, observability and delivery, and plan the system-level tests.

## Entry criteria
- G1 approved; the SRS and RTM are baselined.
- The top quality goals are ranked.

## Activities
1. **Architecture drivers.**
   - Turn the top NFRs into quality-attribute scenarios: *source → stimulus → environment → response → measure*. Example: "At 3× peak load, search p95 stays ≤ 300 ms."
   - List the constraints: budget, deadlines, team skills, compliance, existing systems, mandated platforms.
2. **Architecture style.**
   - Use the simplest style that meets the drivers. Usually that's a **modular monolith** with strict module boundaries.
   - Choose microservices, serverless or event-driven designs only when there's a written driver for them: independent scaling or deployment, team ownership boundaries, or very spiky or asynchronous workloads. Accept their operational cost knowingly.
   - Record the decision as an ADR.
3. **Technology stack selection.** This is where the stack gets decided.
   - **Decide each of these:**
     - mobile: native per platform vs. cross-platform;
     - web: framework and rendering strategy;
     - backend: language/runtime and framework;
     - data stores, hosting, CI/CD, observability, identity provider.
   - **Score the candidates** with a weighted decision matrix in the ADR. Criteria:
     - fit with the NFRs and quality goals;
     - team skills and the hiring market;
     - maturity, community and long-term support;
     - security track record and patch cadence;
     - licence;
     - total cost (licences, infrastructure, people);
     - lock-in and exit path;
     - testability and tooling;
     - accessibility support;
     - ecosystem support for the required integrations.
   - **Retire the riskiest unknowns** with time-boxed proofs of concept, e.g. offline sync, peak throughput, or a hard third-party integration. A PoC answers one question and is then thrown away.
   - **Write one ADR per decision**, accepted at G2.
4. **Structure and views** (C4 diagrams inside an arc42 document; see the [template](../templates/architecture.md)):
   - C4 Level 1, system context.
   - C4 Level 2, containers: apps, services, databases, queues, third parties.
   - A runtime view of the key scenarios.
   - A deployment view: environments, regions, network zones.
5. **Data architecture.**
   - Pick the store type for each access pattern. Relational is the default for transactional integrity. Use document, key-value, search, time-series or object storage only for a stated need.
   - Give each module or service ownership of its data. No two services write to the same tables.
   - Record where PII lives, and how it's protected, retained and deleted.
   - Plan backups.
   - Keep analytics separate from the transactional database.
   - Decide the approach to migrating legacy data.
6. **Integration architecture.**
   - Pick an API style for each interaction (REST, GraphQL, gRPC, events) and say why. Decide which calls are synchronous and which are asynchronous.
   - Add a backend-for-frontend or gateway when clients differ significantly.
   - Write a **versioning and compatibility policy**. Mobile apps stay installed for months, so the API must keep supporting older app versions for a defined window.
   - Put third-party integrations behind anti-corruption layers, with timeouts, retries and fallbacks.
7. **Security architecture.**
   - **Threat model:** a data-flow diagram with trust boundaries, STRIDE applied to each element, and mitigations mapped to requirement IDs. Use LINDDUN for privacy threats if useful.
   - **Identity:** a central identity provider; OAuth 2.x / OpenID Connect; PKCE for public clients (mobile apps and SPAs); token lifetimes and refresh rotation.
   - **Authorisation** enforced server-side (RBAC or ABAC), deny by default.
   - **Secrets and encryption:**
     - secrets in a secret manager, never in clients;
     - TLS 1.2+ everywhere, preferably 1.3;
     - encryption at rest;
     - key management and rotation.
   - **Network segmentation**, plus DDoS and WAF protection wherever the system is exposed.
   - **Supply-chain controls:** signed builds, an SBOM, a dependency policy.
8. **Scalability and performance.**
   - Build a capacity model from the load NFRs: instances, storage and throughput, with headroom (e.g. 2× the expected peak).
   - Use stateless services that scale horizontally.
   - Add caching layers (client, CDN, application, database), each with explicit invalidation rules.
   - Use queues for slow or spiky work.
   - Plan a database scaling path and take each step only when needed: indexes → read replicas → partitioning/sharding.
   - Split the latency budget across tiers. For example, a 300 ms p95 budget is shared by network, gateway, service and database.
9. **Reliability.**
   - Set an SLO for each critical user journey.
   - Analyse failure modes for every dependency: what happens if the database, queue or payment provider is down or slow?
   - Use redundancy across zones and design for graceful degradation.
   - Apply the resilience patterns: timeouts, retries with backoff, circuit breakers, bulkheads, idempotency.
   - Choose a disaster-recovery tier that meets the RPO/RTO: backup-restore, pilot light, warm standby or active-active. Cost rises with each tier.
10. **Observability.**
    - Structured logs, metrics and distributed traces, using OpenTelemetry as the vendor-neutral standard.
    - Client telemetry: mobile crash and ANR reporting, web real-user monitoring.
    - SLO burn-rate alerting.
    - Correlation IDs carried from the client all the way to the database.
11. **Delivery.**
    - Environments: dev, test, a production-like staging, production.
    - Infrastructure as code.
    - CI/CD stages and quality gates (see [Phase 4](4-implementation.md)).
    - A strategy for configuration, feature flags and secrets in each environment.
    - A release strategy for each platform (see [Phase 6](6-deployment.md)).
12. **Cross-cutting decisions:**
    - error model;
    - logging policy (levels, PII redaction);
    - i18n approach;
    - accessibility through a design system;
    - time (store UTC);
    - ID strategy (external IDs that can't be guessed);
    - money (decimal amount plus currency);
    - pagination.
13. **Test strategy (V-model).** Write the master test plan using the [template](../templates/test-plan.md). It covers:
    - test levels, and the test types for each NFR;
    - environments;
    - test data (synthetic or masked);
    - the automation approach and test pyramid;
    - entry and exit criteria for each level;
    - the defect process;
    - tool *categories* (not specific tools).

    Then write the system test plan, derived from the SRS.
14. **Cost model.** Estimate infrastructure and service costs at launch and at the projected scale. Set budget alerts.
15. **Architecture review.** Walk through each quality scenario against the design with the tech leads, security, SRE and QA (ATAM-style). Record risks, sensitivity points and trade-offs.

## Platform specifics
These are the decisions to make and record. The practices behind them are in the practice files.

### Mobile ([practices/mobile.md](../practices/mobile.md))
- Native vs. cross-platform (ADR).
- Architecture pattern: layered, with unidirectional data flow.
- Offline model: is the local database the source of truth? What are the sync protocol and the conflict policy?
- Modules split by feature; a shared design system.
- How long older app versions stay supported, and a remote minimum-version check.
- Remote config, feature flags and kill switches.
- Push notification architecture; deep-link routing.
- Analytics tracking plan and crash-reporting approach.

### Frontend ([practices/frontend.md](../practices/frontend.md))
- Rendering strategy for each type of route (client-side, server-side, static, incremental, streaming), based on SEO and performance needs.
- Design system and component architecture.
- State management: server state vs. UI state.
- Auth/session pattern. A backend-for-frontend with httpOnly cookies is recommended over keeping tokens in browser storage.
- Content Security Policy approach.
- Asset and CDN strategy; performance budgets for each route.

### Backend ([practices/backend.md](../practices/backend.md))
- Contract format (OpenAPI, AsyncAPI or protobuf) as the source of truth.
- Module or service boundaries along business domains; who owns which data.
- Consistency model: transactions, transactional outbox, sagas.
- Zero-downtime migration strategy (expand/contract).
- Caching, rate limiting and quotas; the tenancy isolation model.
- Health checks, graceful shutdown, and the signals that drive autoscaling.

## Deliverables
- **Software architecture document** ([templates/architecture.md](../templates/architecture.md)): arc42 with C4 L1–L2, deployment, data, integration, cross-cutting concepts, quality scenarios and risks.
- **ADRs** ([templates/adr.md](../templates/adr.md)): stack choices, architecture style, and any other significant decision.
- **Threat model**, with mitigations mapped to requirements.
- **Capacity and cost model**; PoC reports.
- **Master and system test plans** ([templates/test-plan.md](../templates/test-plan.md)).
- **RTM updated**: requirement → architecture element or tactic.

## Exit gate checklist (G2)
- [ ] Every NFR maps to at least one architectural tactic; quality scenarios walked through
- [ ] ADRs for the stack and the architecture style accepted, with decision matrices
- [ ] Top technical risks retired by a PoC or formally accepted
- [ ] Threat model reviewed; mitigations mapped to requirement IDs
- [ ] Capacity model, SLOs, DR tier (RPO/RTO) and observability approach defined
- [ ] API versioning and compatibility policy defined, including older mobile app versions
- [ ] Environments, CI/CD and release strategy defined
- [ ] Master and system test plans approved
- [ ] Cost within budget
- [ ] RTM updated
- [ ] Reviewed by the architect, tech leads, security, SRE and QA
- [ ] Baseline tagged

## Pitfalls
- **Choosing technology because it's fashionable**, or because it looks good on a CV, instead of using the decision matrix.
- **Premature microservices:** paying the costs of a distributed system without the scale that justifies them.
- **No plan for operations:** observability, on-call, backups and DR bolted on as afterthoughts.
- **Forgetting that old mobile app versions** keep calling the API.
- **Designing only the happy path**, with no failure-mode analysis.
- **No capacity numbers**, which makes "scalable" impossible to verify.
