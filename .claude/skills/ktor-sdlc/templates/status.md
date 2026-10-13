# STATUS: <Initiative name>

> The control file for the Ktor SDLC workflow (`ktor-sdlc` skill). Claude reads it first to resume work.
>
> Keep it current. It's the single place for gate decisions, risks and open items.

| Field | Value |
|---|---|
| Initiative | <name> (`docs/sdlc/<initiative-slug>/`) |
| Type | New service / Feature in <service> |
| Service | <name>, repository <link> |
| API consumers | e.g. Android app (oldest supported 2.3.0) · iOS app (oldest 2.3.0) · web · partner X |
| Toolchain | Kotlin <v> · Ktor <v> · JDK <v> · Exposed <v> · PostgreSQL <v> |
| Module layout | One module / Gradle modules per bounded context (ADR-<n>) |
| Deployment platform | e.g. Kubernetes on <cloud> / Cloud Run / ECS (ADR-<n>); regions <…> |
| Environments | dev · staging · production |
| OpenAPI contract | `docs/api/openapi.yaml` |
| Security level | ASVS L1 / L2 / L3 |
| Compliance | e.g. GDPR, HIPAA, PCI-DSS, SOC 2 |
| SLOs | e.g. 99.9% availability; p95 ≤ 200 ms on critical endpoints |
| Product owner / Tech lead / Ops owner | <name, role> / <name, role> / <name, role> |
| Current phase | 1 Requirements |
| Tailoring | Full (service) / Light (feature) |
| Last updated | YYYY-MM-DD |

## Deliverables
| Phase | Deliverable | File | Status (Not started / Draft / In review / Approved) | Version |
|---|---|---|---|---|
| 1 | Requirements | requirements.md | Not started | — |
| 1–6 | RTM | rtm.md | Not started | — |
| 2 | Architecture + threat model + capacity model | architecture.md | Not started | — |
| 2+ | ADRs | adr/NNNN-<decision>.md | — | — |
| 1–5 | Test plan + summary report | test-plan.md | Not started | — |
| 3 | Feature designs | design/<feature>.md | Not started | — |
| 6 | Release checklist | release-checklist.md | Not started | — |

The OpenAPI contract is baselined at G3 with the feature designs, but lives in the code repository (`docs/api/openapi.yaml`), where CI checks it.

## Gate log
Decision is one of: Approved / Approved with conditions / Rejected / Waived.

| Gate | Date | Decision | Approver (name, role) | Conditions or accepted risk | Tag |
|---|---|---|---|---|---|
| G1 Requirements baseline | | | | | |
| G2 Architecture baseline | | | | | |
| G3 Ready to build | | | | | |
| G4 Code complete | | | | | |
| G5 Release readiness | | | | | |
| G6 Launch accepted | | | | | |

## Decisions
| Date | Decision | Recorded in (ADR / minutes) |
|---|---|---|

## Risks
| ID | Risk ("If …, then …") | Likelihood (H/M/L) | Impact (H/M/L) | Owner | Mitigation | Status |
|---|---|---|---|---|---|---|
| R-01 | | | | | | Open |

## Change requests
| CR ID | Title | Status | Affected items | Decision date |
|---|---|---|---|---|

## Open items
A TBD that blocks a Must requirement blocks the gate.

| ID | Type (TBD / ASSUMPTION / Question) | Description | Blocks gate? | Owner | Status |
|---|---|---|---|---|---|
