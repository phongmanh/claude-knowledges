# STATUS: <Initiative name>

> Project control file for the waterfall workflow. Claude reads this first to resume work.
>
> Keep it current. It's the single place for gate decisions, risks and open items.

| Field | Value |
|---|---|
| Initiative | <name> (`docs/sdlc/<initiative-slug>/`) |
| Type | New application / Feature in <existing app> |
| Platforms in scope | Mobile (iOS / Android) · Frontend (web) · Backend |
| Compliance | e.g. GDPR, PCI-DSS, WCAG 2.2 AA, store policies |
| Sponsor / PO | <name, role> / <name, role> |
| Current phase | 0 Initiation |
| Tailoring | Full (application) / Light (feature). See the tailoring table in the waterfall-sdlc skill. |
| Last updated | YYYY-MM-DD |

## Deliverables
| Phase | Deliverable | File | Status (Not started / Draft / In review / Approved) | Version |
|---|---|---|---|---|
| 0 | Charter / feature brief | charter.md | Not started | — |
| 1 | SRS | srs.md | Not started | — |
| 1–6 | RTM | rtm.md | Not started | — |
| 2 | Architecture + threat model | architecture.md | Not started | — |
| 2+ | ADRs | adr/NNNN-<decision>.md | — | — |
| 1–5 | Test plan + summary report | test-plan.md | Not started | — |
| 3 | Detailed designs | design/<component>.md | Not started | — |
| 6 | Release checklist | release-checklist.md | Not started | — |

## Gate log
Decision is one of: Approved / Approved with conditions / Rejected / Waived.

| Gate | Date | Decision | Approver (name, role) | Conditions or waiver risk | Baseline tag |
|---|---|---|---|---|---|
| G0 Charter approved | | | | | |
| G1 Requirements baseline | | | | | |
| G2 Architecture baseline | | | | | |
| G3 Ready to build | | | | | |
| G4 Code complete | | | | | |
| G5 Release readiness | | | | | |
| G6 Operational acceptance | | | | | |

## Gate conditions to close
| # | Condition | Gate | Owner | Due | Status |
|---|---|---|---|---|---|

## Decisions
| Date | Decision | Recorded in (ADR / minutes) |
|---|---|---|

## Risk register
| ID | Risk ("If …, then …") | Category | L (1–5) | I (1–5) | Score | Owner | Mitigation | Contingency | Trigger | Status |
|---|---|---|---|---|---|---|---|---|---|---|
| R-01 | | | | | | | | | | Open |

## Change requests
| CR ID | Title | Submitted | Status | Affected items | Decision date |
|---|---|---|---|---|---|

## Open items (TBDs, assumptions, questions)
A TBD that blocks a Must requirement blocks the gate.

| ID | Type (TBD / ASSUMPTION / Question) | Description | Blocks gate? | Owner | Status |
|---|---|---|---|---|---|
