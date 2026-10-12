# Governance: gates, roles, traceability, change and risk

Controls that span every phase of the [waterfall workflow](SKILL.md). The phase files say *what* to produce. This file says *how decisions and changes are controlled*.

## Phase gates
| Gate | Name (classic review) | Approvers (A = accountable) | Baseline produced |
|---|---|---|---|
| G0 | Charter approved | Sponsor (A), PM | Charter, plan v1, risk register |
| G1 | Requirements baseline (SRR, System Requirements Review) | Product Owner (A), tech leads, QA lead; security/privacy if data is sensitive | SRS v1.0, acceptance test plan draft, RTM v1 |
| G2 | Architecture baseline (PDR, Preliminary Design Review) | Architect (A), tech leads, security, DevOps/SRE, QA lead | Architecture document, accepted ADRs, threat model, master test plan |
| G3 | Ready to build (CDR, Critical Design Review) | Tech leads (A), QA lead, UX, security | Detailed designs, frozen API contracts, schema, UI specs, integration test cases |
| G4 | Code complete (TRR, Test Readiness Review) | Tech leads (A), QA lead | Release candidate build and its quality reports |
| G5 | Release readiness (PRR, Production Readiness Review; go/no-go) | Sponsor or PO (A), QA lead, security, DevOps/SRE, release manager | Approved release |
| G6 | Operational acceptance & closure | Ops/SRE lead (A), sponsor | Production baseline, closure report |

### Gate review procedure
1. **Pre-read.** The author sends the deliverables and the filled-in exit checklist ahead of the review (e.g. 2–3 working days before).
2. **Review against the checklist.** Reviewers record findings against the checklist and the requirements, not personal preference.
3. **Outcome**, recorded in the STATUS.md gate log:
   - **Approved.** The baseline is tagged and the next phase may start.
   - **Approved with conditions.** The next phase may start. Each condition gets an owner and a due date and is tracked until closed.
   - **Rejected.** Rework, then review again.
4. **Waiver.** Skipping a criterion needs the sponsor's written risk acceptance (what, why, the risk, who accepted it), recorded in STATUS.md.
5. **People decide.** Gate decisions are made by people. Claude prepares the gate summary and records the decision; it never approves a gate itself.

## Roles and RACI
In small teams one person may hold several roles, but **the author of a deliverable never approves it** (the four-eyes principle).

| Role | Responsibility in short |
|---|---|
| Sponsor | Owns the business case and the budget; makes the final go/no-go |
| Product Owner / Business Analyst | Owns the requirements, priorities and acceptance |
| Project Manager | Plan, schedule, risks, reporting, gate logistics |
| Architect | System design, ADRs, technical coherence |
| Tech leads (mobile, frontend, backend) | Platform design, code quality, estimates |
| UX/UI designer | Research, flows, visual and interaction design, accessibility |
| Developers | Detailed design, code, unit tests, docs |
| QA lead / testers | Test strategy, test design and execution, quality reports |
| Security engineer | Threat model, security requirements, security testing |
| DevOps / SRE | Environments, CI/CD, observability, reliability, operations |
| DBA / data engineer | Data model, migrations, query performance, backups |
| Release manager | Release plan, go/no-go logistics, deployment coordination |
| Support / operations | Runbooks, support model, operational acceptance |
| Legal / DPO | Compliance, privacy, licensing, store and legal texts |

RACI per phase (R = responsible, A = accountable, C = consulted, I = informed). Each phase has exactly one A:

| Role | 0 Init | 1 Req | 2 Sys design | 3 Detailed | 4 Impl | 5 Test | 6 Deploy | 7 Maint |
|---|---|---|---|---|---|---|---|---|
| Sponsor | A | I | I | I | I | C | C | I |
| Product Owner / BA | R | A | C | C | C | R | C | A |
| Project Manager | R | R | R | R | R | R | R | C |
| Architect | C | C | A | C | C | C | C | C |
| Tech leads | C | C | R | A | A | C | R | R |
| UX/UI designer | C | R | C | R | C | C | I | C |
| Developers | I | C | C | R | R | R | R | R |
| QA lead / testers | I | C | R | R | C | A | C | R |
| Security engineer | C | R | R | C | C | R | C | R |
| DevOps / SRE | I | C | R | C | R | R | R | R |
| DBA / data engineer | I | C | R | R | R | C | R | R |
| Release manager | I | I | C | I | C | C | A | R |
| Support / operations | I | C | C | I | I | R | R | R |
| Legal / DPO | C | C | C | I | I | C | C | C |

The table covers the work inside each phase. Gate decisions follow the gate table above. Some responsibilities shift at specific points:
- **Phase 5:** the PO runs UAT, and support/operations run OAT.
- **G6:** operations formally accept the handover.
- **Phase 7:** DevOps/SRE run day-to-day operations, while the PO owns the change backlog.

## Requirements traceability matrix (RTM)
A living table at `docs/sdlc/<initiative>/rtm.md` (template: [templates/rtm.md](templates/rtm.md)).
- **Columns:** Req ID · summary · source (objective, stakeholder or regulation) · priority (MoSCoW) · design ref (architecture section, ADR, detailed design) · code ref (module, PR) · test IDs · latest result · release · status.
- **Forward traceability:** every requirement → design → code → tests → release. A gap means something is unbuilt or unverified.
- **Backward traceability:** every design element, test and significant piece of code → a requirement. An orphan means either gold plating (YAGNI) or a missing requirement. Raise a CR.
- **Update at every gate.** RTM completeness for the current phase is an exit criterion for G1–G5:
  - G1: every requirement has an ID, source, priority and acceptance criteria.
  - G2: every requirement, especially every NFR, maps to an architecture element or tactic.
  - G3: every requirement maps to a detailed design element and planned test cases.
  - G4: every requirement maps to a code reference, plus unit tests where they apply.
  - G5: every requirement maps to executed tests and their results.
- **Impact analysis.** For any CR, the RTM shows which design, code and tests are affected.

## Change control
Late change is waterfall's main risk. Change isn't forbidden; it's controlled.
- **When a CR is needed:** any change to a baselined deliverable, whether scope, a requirement, an NFR target, the architecture, a contract, a schema, the schedule or the budget. A clarification or typo fix that doesn't change meaning is a minor revision recorded in the document history, with no CR.
- **Lifecycle:** Submitted → Impact analysis → CCB decision (Approved, Rejected or Deferred) → Implemented → Verified → Closed. Template: [templates/change-request.md](templates/change-request.md).
- **Impact analysis covers:**
  - the affected requirements and, through the RTM, the affected design, code and tests;
  - schedule and cost;
  - risk;
  - quality and NFRs;
  - security and privacy;
  - compliance;
  - operations and support.
- **Change Control Board (CCB):** PO (chair), PM, the architect or a tech lead, and the QA lead, plus security or legal as needed. In a small team, the PO and a tech lead.
- **Re-baselining.** An approved CR updates every affected deliverable and the RTM, then the affected gate checks are run again. Bump the minor version (v1.1) for clarifications and the major version (v2.0) for scope changes.
- **Emergency changes** (a production incident or a security fix) get expedited approval from the on-call lead plus the PO. A retroactive CR and review follow within e.g. 2 working days.
- **Track requirements volatility** (CRs ÷ baselined requirements). Rising volatility after G1 signals weak elicitation. Fix the cause, not just the individual CRs.

## Risk management
- **Register**, kept in STATUS.md. Fields:
  - ID;
  - the risk, written as "If <cause>, then <effect>";
  - category: technical, schedule, cost, security, compliance, people or vendor;
  - likelihood (1–5), impact (1–5) and score (L×I);
  - owner;
  - mitigation, which lowers the likelihood;
  - contingency, which lowers the impact;
  - trigger, an early warning sign;
  - status.
- **Review** weekly and at every gate. Escalate scores of e.g. 15 or more to the sponsor.
- **Classic waterfall risks, and the mitigations already built into this workflow:**

| Risk | Built-in mitigation |
|---|---|
| Requirements are misunderstood and only found out at UAT | Throwaway prototypes and walkthroughs in Phase 1; Given/When/Then acceptance criteria; UAT plan written in Phase 1 |
| Late integration surprises | Contract-first APIs frozen at G3; mock servers; merging to main at least daily; an early integration environment |
| Technical unknowns found during the build | Time-boxed proofs of concept in Phase 2; top technical risks retired or accepted at G2 |
| Overruns squeeze the test window | Test time protected in the schedule; earned-value tracking; scope cut through CRs, never by cutting quality |
| A big-bang release fails | Staged rollout, feature flags, kill switches, rehearsed deployment, rollback triggers agreed in advance |
| Key-person dependency | Docs-as-code, ADRs, code review, pairing, runbooks |
| Compliance found late (privacy, accessibility, store policy) | Compliance mapping in Phases 0–1; security and privacy requirements with IDs; gate checks |

## Configuration management
- **Everything is versioned in the repository:** code, IaC, API contracts, schemas and migrations, test cases, and the SDLC documents themselves (docs-as-code).
- **Baselines are tags**, created at each approved gate, e.g. `baseline/G1-srs-v1.0`, `baseline/G3-design-v1.0`, `release/1.0.0`.
- **Build artifacts are immutable.** Each is versioned and stored in an artifact repository, and the same artifact is promoted through every environment.
- **Every document header** carries version, status (Draft, In review, Approved or Superseded), owner, approvers, last-updated date and change history.
- **Environment configuration** is managed as code. Secrets live only in a secret manager, never in documents or the repository.

## Quality assurance and metrics
- **A review for every deliverable:**
  - requirements inspection (G1);
  - architecture review (G2);
  - design inspection (G3);
  - code review on every PR (Phase 4);
  - test case review (Phases 3–5);
  - release readiness review (G5).
- **Metrics.** Report them at each gate and watch the trend across releases:

| Metric | Formula or meaning | What it tells you |
|---|---|---|
| Requirements volatility | CRs against requirements ÷ baselined requirements | How good elicitation was |
| Defect density | Defects ÷ size (e.g. per thousand lines or per function point) | Build quality per module |
| Defect leakage by phase | The phase where a defect was found vs. the phase where it was introduced | Which reviews to strengthen |
| Defect removal efficiency (DRE) | Defects found before release ÷ all defects (including those found in e.g. the first 90 days in production) | How effective reviews and testing are overall |
| Requirements coverage | Requirements with passing tests ÷ all requirements | Release readiness |
| Schedule / cost performance | SPI = EV ÷ PV, CPI = EV ÷ AC (earned value) | Early warning of overruns |
| Escaped defects | Production defects per release, by severity | Where to improve the process |
| Change failure rate, MTTR | Failed deployments ÷ deployments; mean time to restore service | Delivery and operations health |

## Communication
- **Status report** at a fixed cadence (e.g. weekly): progress against the plan, earned value, top risks, open decisions, CRs.
- **Steering meeting with the sponsor at each gate.**
- **Decision records:** ADRs for technical decisions, and STATUS.md for gate and project decisions.
