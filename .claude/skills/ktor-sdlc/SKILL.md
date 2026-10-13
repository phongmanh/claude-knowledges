---
name: ktor-sdlc
description: Waterfall lifecycle for a Kotlin backend service or API feature built with Ktor - requirements, architecture, detailed design (API contract, schema), implementation, testing, deployment and operations - with phase gates, sign-offs, traceability and change control. Bundles Ktor best practices (hexagonal layers, Resources routing, Koin, Exposed + PostgreSQL + Flyway, RFC 9457 problem details, JWT/OIDC auth, rate limiting, OpenAPI breaking-change checks, structured logging, Micrometer, OpenTelemetry, OWASP ASVS and API Top 10, testApplication + Testcontainers, zero-downtime deploys), verified code patterns, a PR review checklist and deliverable templates. Use when planning, designing, building, testing or deploying a Ktor server, REST API or mobile backend, when writing those documents for a Ktor project, or when the user mentions waterfall, SDLC, V-model or phase gates for a Kotlin backend.
---

# Ktor SDLC (waterfall)

A gated, document-driven lifecycle for a **Kotlin backend built with Ktor**: a new service, or a feature (a set of endpoints) in an existing one. Each phase produces reviewed deliverables and ends at a gate. The next phase starts only after an explicit sign-off.

## Principles
- **Quality is designed in.** Each design phase writes the tests that later verify it (see the [V-model](#v-model)). Every NFR has a measurable target.
- **Traceable.** Every requirement has an ID that is carried into design, code, tests and the release ([RTM](templates/rtm.md)).
- **Gates are real.** A baselined deliverable changes only through a [change request](templates/change-request.md).
- **Contract first.** The OpenAPI contract is part of the detailed design and is frozen at G3. CI compares the API the code serves with it and fails on a breaking change ([API design](reference/api-design.md#openapi-workflow)).
- **Every request is authorised on the server,** at three levels: object (may this caller touch *this* resource?), function (may this role do *this* operation?) and property (only the fields the caller may read or write).
- **Clients you don't control.** Mobile apps stay installed for months. Every change stays backward compatible with the oldest client version that is still supported.
- **Operability is a feature.** SLOs, dashboards, alerts and runbooks are designed in Phase 2 and are entry criteria for production, not afterthoughts.
- **Opinionated defaults, explicit deviations.** The [default stack](reference/architecture.md#default-stack) applies unless an ADR says otherwise.
- **Project rules win.** If the target repo has a `CLAUDE.md` or `.claude/rules/`, they override this skill's conventions. This skill still governs the process and the quality bars.
- **Proportionate depth.** A feature gets lighter documents than a new service; see [Tailoring](#tailoring).
- **Reviewable output.** Documents follow fixed templates. Code follows one [pattern per concern](reference/code-patterns.md). PRs are small and single-purpose ([review checklist](reference/review-checklist.md)).

## Lifecycle
| # | Phase | Key question | Main deliverables | Gate |
|---|---|---|---|---|
| 1 | [Requirements](phases/1-requirements.md) | What must the service do, for which clients, and how well? | Requirements (brief, API consumers, FRs, NFRs and SLOs, data classification, integrations), acceptance outline, RTM | G1 Requirements baseline |
| 2 | [Architecture](phases/2-architecture.md) | How is the service structured, deployed and secured, and on which stack? | Architecture document (context, modules, deployment, data stores, capacity, auth model, threat model), ADRs, master test plan | G2 Architecture baseline |
| 3 | [Detailed design](phases/3-detailed-design.md) | What exactly does each endpoint accept, return, store and check? | Feature designs (OpenAPI contract, validation, authorisation matrix, schema and migrations, events, PR plan), integration and contract test cases | G3 Ready to build |
| 4 | [Implementation](phases/4-implementation.md) | Is it built right? | Code and tests, CI with the contract check, a release-candidate image | G4 Code complete |
| 5 | [Testing](phases/5-testing.md) | Does it meet the spec under realistic load and failure? | Test reports (load, resilience, security), UAT sign-off, test summary report | G5 Release readiness (go/no-go) |
| 6 | [Deployment](phases/6-deployment.md) | Is it live, observable and stable in production? | Release checklist, rollout record, runbooks, handover | G6 Launch accepted |
| 7 | [Operations & maintenance](phases/7-maintenance.md) | Does it stay within its SLOs as load, clients and dependencies change? | SLO reviews, postmortems, CRs, dependency updates, API deprecations | Mini-cycle per change |

## V-model
| Design phase | Verified in Phase 5 by | Test basis written in |
|---|---|---|
| 1 Requirements | Acceptance tests on staging, through the real client app or API scripts | Phase 1: acceptance outline |
| 2 Architecture | System and NFR tests on a production-like environment: load and soak, resilience, security (DAST), backup restore | Phase 2: master test plan |
| 3 Detailed design | Integration tests (`testApplication`, Testcontainers PostgreSQL), contract tests against the OpenAPI contract, migration tests | Phase 3: feature designs |
| 4 Implementation | Unit tests of services, domain rules, mappers and validators | Phase 4: written with the code |

## Tailoring
| Deliverable | New service | Feature in an existing service |
|---|---|---|
| [Requirements](templates/requirements.md) | Full | Brief, feature FRs, changed NFRs and SLOs, new data and consumers |
| [Architecture](templates/architecture.md) | Full, with stack, module layout and deployment ADRs | Delta: changed modules, endpoints, data stores, threats and capacity |
| [ADRs](templates/adr.md) | Stack deviations, module layout, deployment platform, other key choices | One per significant decision |
| [Feature design](templates/feature-design.md) | One per feature (API area) | One for the feature |
| [Test plan](templates/test-plan.md) | Master plan and summary report | Feature scope, regression scope, and the NFRs the feature touches (e.g. a load test of the new endpoints) |
| [Release checklist](templates/release-checklist.md) | Full, with hypercare | Standard; rollout behind a feature flag |
| [STATUS](templates/status.md), [RTM](templates/rtm.md) | Required | Required (feature rows only) |

- **A breaking API change is never a small feature.** It needs a new API version, a deprecation plan for the old one and a CR ([API design](reference/api-design.md#versioning-and-compatibility)).
- A small feature may combine G2 and G3 into one review. **G5 is never skipped or combined.**

## How Claude runs this workflow
1. **Workspace.** In the target project, open `docs/sdlc/<initiative-slug>/STATUS.md`. If it exists, resume at the phase it records. If not, create it from [templates/status.md](templates/status.md).
2. **Facts.** In an existing service, read:
   - `settings.gradle.kts`, `gradle/libs.versions.toml` and the module build files;
   - `application.yaml` (or `application.conf`), `logback.xml`, `db/migration/`;
   - the `Dockerfile` or image configuration, and the deployment manifests (Helm, Kubernetes, Terraform);
   - the OpenAPI contract (e.g. `docs/api/openapi.yaml`);
   - `CLAUDE.md` and `.claude/rules/`.

   Record the modules, the Ktor, Kotlin and JDK versions, the engine, the database and its version, the deployment platform and the environments in STATUS.md. Don't contradict them without an ADR.
3. **Scope.** Confirm with the user:
   - new service or feature;
   - the API consumers (mobile apps, web, partners, other services) and the oldest client version still supported;
   - expected load and growth;
   - data classification and compliance (e.g. GDPR, HIPAA, PCI-DSS, SOC 2), and the ASVS level;
   - the deployment platform and environments;
   - existing documents to reuse.

   Record the answers and pick the tailoring column.
4. **Load only what's needed:** the current phase file and the references its **Load** line lists. If STATUS.md doesn't show the previous gate as approved, stop and say so.
5. **Write the deliverables** from `templates/` into the workspace.
   - Mark unknowns `TBD-<n>` and assumptions `ASSUMPTION:`, and list them in STATUS.md.
   - Ask the user for what only stakeholders can decide: targets, SLOs, priorities, approvers.
   - Never invent requirements, numbers, approvals or sign-offs.
6. **Trace.** Add every new requirement, design element (endpoint, table, event) and test to `rtm.md`.
7. **Gate review.** Run the phase's exit checklist. Present the deliverables and their status, the checklist results, open TBDs, top risks, and a recommendation: approve, approve with conditions, or rework.
8. **STOP for sign-off.** Ask for the decision and the approver's name and role. Record both in the STATUS.md gate log and suggest a git tag (`sdlc/<slug>/G<n>`). A waiver records the accepted risk and who accepted it.
9. **After a baseline,** every change to an approved deliverable goes through a [change request](templates/change-request.md): RTM impact analysis → decision → update the affected deliverables → re-check the affected gates.

**Partial use.** If the user wants a single deliverable (e.g. "write the feature design for `POST /v1/notes`"), produce just that one, following its phase's guidance. Mention any missing upstream inputs, but don't force the whole lifecycle. The same goes for code: "add a notes endpoint" uses the [code patterns](reference/code-patterns.md) and the [review checklist](reference/review-checklist.md) without the documents.

Workspace layout in the target project:
```
docs/sdlc/<initiative-slug>/
├── STATUS.md               # phase, gate log, decisions, risks, CRs, open items
├── requirements.md         # Phase 1
├── rtm.md                  # Phases 1–6
├── architecture.md         # Phase 2 (threat model and capacity model inside)
├── adr/NNNN-<decision>.md  # Phase 2 onwards
├── design/<feature>.md     # Phase 3
├── test-plan.md            # Phases 1–5 (+ test summary report)
├── release-checklist.md    # Phase 6
└── cr/CR-NNN-<title>.md    # after any baseline
```
The OpenAPI contract lives with the code (e.g. `docs/api/openapi.yaml`), because CI checks the code against it. Feature designs link to it.

## File index
- **Phases:** [1 Requirements](phases/1-requirements.md) · [2 Architecture](phases/2-architecture.md) · [3 Detailed design](phases/3-detailed-design.md) · [4 Implementation](phases/4-implementation.md) · [5 Testing](phases/5-testing.md) · [6 Deployment](phases/6-deployment.md) · [7 Operations & maintenance](phases/7-maintenance.md)
- **Reference:**
  - [architecture](reference/architecture.md): layers, module layouts, the shared contract module, default stack, Gradle, configuration, DI, error model, threading;
  - [API design](reference/api-design.md): resources, status codes, problem details, pagination, concurrency, idempotency, versioning, the OpenAPI workflow;
  - [code patterns](reference/code-patterns.md): canonical Kotlin for each layer and plugin, compiled and tested against current library versions;
  - [security & privacy](reference/security-privacy.md) · [performance & reliability](reference/performance-reliability.md) · [deployment & operations](reference/deployment-operations.md) · [testing](reference/testing.md) · [review checklist](reference/review-checklist.md).
- **Templates:** [status](templates/status.md) · [requirements](templates/requirements.md) · [architecture](templates/architecture.md) · [adr](templates/adr.md) · [feature-design](templates/feature-design.md) · [test-plan](templates/test-plan.md) · [release-checklist](templates/release-checklist.md) · [change-request](templates/change-request.md) · [rtm](templates/rtm.md)

## Conventions
- **Requirement IDs.** `FR-nnn` for functional requirements. `NFR-<ATTR>-nn` for non-functional ones, where ATTR is one of PERF, SCAL, AVAIL, REL, SEC, PRIV, MAINT, TEST, COMPAT, OBS, I18N, OPS.
- **Test IDs.** `UT-` unit, `IT-` integration, `CT-` contract, `ST-` system/NFR, `AT-` acceptance.
- **Design elements** are named by what they are: endpoints as `METHOD /path` (`POST /v1/notes`), tables by name, events in the past tense (`NoteCreated`).
- Commits, PRs, designs and tests cite these IDs.
- **Numbers marked "e.g."** are examples. The real targets are agreed in the requirements.
- **Versions.** Libraries are always the latest stable release, declared once in `gradle/libs.versions.toml`; this skill pins none. The JVM is the current LTS. Ktor's compiler plugin must support the Kotlin version, so upgrade them together and read the Ktor release notes first. An experimental Ktor API (e.g. OpenAPI generation from code) needs an ADR.
