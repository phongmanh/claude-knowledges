---
name: waterfall-sdlc
description: Stack-agnostic waterfall lifecycle for a new application or feature - initiation, requirements, system design, detailed design, implementation, testing, deployment and maintenance. Includes phase gates, traceability, change control, deliverable templates (charter, SRS, architecture, ADR, design, test plan, release checklist) and mobile/frontend/backend best practices for scalability, testability, maintainability, security and performance. Use when planning or building an app or feature end to end, when writing any of those documents, or when the user mentions waterfall, SDLC, V-model or phase gates.
---

# Waterfall SDLC

A gated, document-driven lifecycle for building a new application, or a feature in an existing one. It works with any technology stack. The stack is chosen inside the workflow, in Phase 2, and recorded in ADRs.

## Principles
- **Quality is designed in, not tested in.** Every design phase writes the test basis that later verifies it (see the V-model below). Non-functional requirements (NFRs) are measurable from day one.
- **Everything is traceable.** Each requirement has an ID and is traced forward to design, code, tests and release. Each design element and test traces back to a requirement. See the [RTM](governance.md#requirements-traceability-matrix-rtm).
- **Gates are real.** A phase starts only after the previous gate is approved. An approved (baselined) deliverable changes only through a [change request](governance.md#change-control).
- **Stack-agnostic until Phase 2.** Until the stack ADRs are accepted, refer to standards and capabilities (OWASP, WCAG, ISO, RFCs), never to products.
- **Proportionate depth.** Each document is as detailed as its risk needs and no more (KISS, YAGNI). A feature gets lighter deliverables than a new application; see [Tailoring](#tailoring-application-vs-feature).
- **Docs-as-code.** Deliverables live in the repository, are reviewed like code, and are tagged at each gate.

## Lifecycle at a glance
| # | Phase | Key question | Main deliverables | Gate |
|---|---|---|---|---|
| 0 | [Initiation & planning](phases/0-initiation.md) | Should we build it, and how will we run the project? | Charter, feasibility, plan, risk register | G0 Charter approved |
| 1 | [Requirements](phases/1-requirements.md) | What exactly must it do, and how well? | SRS with measurable NFRs, acceptance test plan, RTM | G1 Requirements baseline (SRR) |
| 2 | [System design](phases/2-system-design.md) | How is it structured, and on which stack? | Architecture document, ADRs, threat model, master test plan | G2 Architecture baseline (PDR) |
| 3 | [Detailed design](phases/3-detailed-design.md) | How is each part built? | Component designs, API contracts, data schema, UI specs, integration test cases | G3 Ready to build (CDR) |
| 4 | [Implementation](phases/4-implementation.md) | Is it built right? | Code, unit tests, CI quality gates, release candidate | G4 Code complete (TRR) |
| 5 | [Testing](phases/5-testing.md) | Does it meet the spec and the users' needs? | Test reports, UAT/OAT sign-off, test summary report | G5 Release readiness (PRR, go/no-go) |
| 6 | [Deployment](phases/6-deployment.md) | Is it live, stable and handed over? | Release runbook, go/no-go record, handover pack | G6 Operational acceptance & closure |
| 7 | [Maintenance](phases/7-maintenance.md) | Does it stay healthy and evolve safely? | SLO reports, change requests, postmortems, end-of-life plan | A small gated cycle for each change |

## V-model: each design phase writes its own tests
| Design phase (left side) | Verified in Phase 5 by | Test basis written in |
|---|---|---|
| 1 Requirements | Acceptance testing (UAT, OAT) | Phase 1: acceptance test plan |
| 2 System design | System testing: end to end, plus NFRs (performance, security, resilience, compatibility…) | Phase 2: master and system test plans |
| 3 Detailed design | Integration and contract testing | Phase 3: integration test cases |
| 4 Implementation | Unit and component testing | Phase 4: written together with the code |

## Tailoring: application vs feature
| Deliverable | New application | Feature in an existing app |
|---|---|---|
| [Charter](templates/charter.md) | Full charter and feasibility | One-page feature brief (same template, kept short) |
| [SRS](templates/srs.md) | Full SRS | Feature section: FRs, NFR changes, acceptance criteria |
| [Architecture](templates/architecture.md) | Full arc42 document, C4 L1–L2 | Delta: only the building blocks, flows and data that change |
| [ADRs](templates/adr.md) | Stack, architecture style, other key decisions | One per significant decision |
| Threat model | Whole system | Delta: new data flows and trust boundaries |
| [Detailed design](templates/detailed-design.md) | One per component | One per changed component |
| [Test plan](templates/test-plan.md) | Master plan plus a plan per level | Feature test plan plus regression scope |
| [Release checklist](templates/release-checklist.md) | Full, with hypercare | Standard checklist, rollout behind a feature flag |
| [STATUS](templates/status.md) and [RTM](templates/rtm.md) | Required | Required (feature rows only) |

- Every gate applies to both. A small feature may combine G0 with G1 and G2 with G3 into single reviews. **G5 (release readiness) is never skipped or combined.**
- When in doubt, start light. A gate reviewer can always ask for more depth.

## How Claude runs this workflow
1. **Workspace.** In the target project, open `docs/sdlc/<initiative-slug>/STATUS.md`. If it exists, read it and resume at the phase it records. If it doesn't, create it from [templates/status.md](templates/status.md).
2. **Scope.** Confirm with the user:
   - application or feature;
   - platforms in scope (mobile, frontend, backend);
   - compliance regimes (e.g. GDPR, HIPAA, PCI-DSS);
   - existing documents that can be reused.

   Record the answers in STATUS.md and pick the tailoring column.
3. **Load only what's needed.** Read the current phase file, plus the practice files for the in-scope platforms only. Check the entry criteria. If STATUS.md doesn't show the previous gate as approved, stop and say so.
4. **Produce the deliverables** from `templates/` into the workspace.
   - Mark unknowns `TBD-<n>` and assumptions `ASSUMPTION:`, and list them in STATUS.md.
   - Ask the user for anything only stakeholders can decide: targets, priorities, budgets, approvers.
   - Never invent requirements, numbers, approvals or sign-offs.
5. **Trace.** Add every new requirement, design element and test to `rtm.md`.
6. **Gate review.** Run the phase's exit checklist. Present a gate summary covering:
   - each deliverable and its status;
   - checklist results;
   - open TBDs;
   - top risks;
   - a recommendation: approve, approve with conditions, or rework.
7. **STOP for sign-off.** Ask for an explicit decision and the approver's name and role. Record both in the STATUS.md gate log and suggest a baseline tag.
   - Don't start the next phase until the gate is approved.
   - A waiver is recorded with the risk being accepted and who accepted it.
8. **After a baseline**, any change to an approved deliverable goes through [templates/change-request.md](templates/change-request.md): impact analysis via the RTM, then a decision, then updates to the affected deliverables and a re-check of the affected gates.
9. **Once the stack ADRs are accepted**, the project's own rules (e.g. `.claude/rules/`, `CLAUDE.md`) govern stack-specific conventions. This workflow keeps governing the process and the quality bars.

**Partial use.** If the user wants only one deliverable (e.g. "write an SRS"), produce just that one from its template, using the guidance of the matching phase. Mention any missing inputs from earlier phases, but don't force the whole lifecycle.

Workspace layout in the target project:
```
docs/sdlc/<initiative-slug>/
├── STATUS.md              # phase, gate log, risks, CRs, open items
├── charter.md             # Phase 0
├── srs.md                 # Phase 1
├── rtm.md                 # Phases 1–6
├── architecture.md        # Phase 2 (threat model in §8.1)
├── adr/NNNN-<decision>.md # Phase 2 onwards
├── design/<component>.md  # Phase 3
├── test-plan.md           # Phases 1–5 (+ test summary report)
├── release-checklist.md   # Phase 6
└── cr/CR-NNN-<title>.md   # after any baseline
```

## File index
- [governance.md](governance.md): gates, RACI, RTM, change control, risk, configuration management, quality metrics.
- **Phases:** [0 Initiation](phases/0-initiation.md) · [1 Requirements](phases/1-requirements.md) · [2 System design](phases/2-system-design.md) · [3 Detailed design](phases/3-detailed-design.md) · [4 Implementation](phases/4-implementation.md) · [5 Testing](phases/5-testing.md) · [6 Deployment](phases/6-deployment.md) · [7 Maintenance](phases/7-maintenance.md)
- **Practices:** [quality attributes](practices/quality-attributes.md) (all platforms: how to specify, verify and operate) · [mobile](practices/mobile.md) · [frontend](practices/frontend.md) · [backend](practices/backend.md)
- **Templates:** [status](templates/status.md) · [charter](templates/charter.md) · [srs](templates/srs.md) · [architecture](templates/architecture.md) · [adr](templates/adr.md) · [detailed-design](templates/detailed-design.md) · [test-plan](templates/test-plan.md) · [release-checklist](templates/release-checklist.md) · [change-request](templates/change-request.md) · [rtm](templates/rtm.md)

## Conventions used in every file
- **Requirement IDs.** `FR-nnn` for functional requirements. `NFR-<ATTR>-nn` for non-functional ones, where ATTR is one of PERF, SCAL, AVAIL, SEC, PRIV, MAINT, TEST, A11Y, COMPAT, OBS, I18N, COST. Designs, code, tests and CRs cite these IDs.
- **Numbers marked "e.g."** are examples only. The real targets are agreed in the SRS.
- **Platforms.** "Frontend" means web (browser) clients. "Mobile" means iOS and Android apps, whatever they're built with.
