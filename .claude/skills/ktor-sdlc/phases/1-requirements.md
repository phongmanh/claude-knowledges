# Phase 1: Requirements
**Gate:** G1 Requirements baseline
**Deliverables:** [requirements](../templates/requirements.md), acceptance outline (in the [test plan](../templates/test-plan.md)), [RTM](../templates/rtm.md), [STATUS](../templates/status.md)
**Load:** [api-design](../reference/api-design.md) (for consumer and compatibility questions), [security-privacy](../reference/security-privacy.md) (for the ASVS level and the data inventory), [performance-reliability](../reference/performance-reliability.md) (for SLO and NFR targets)

## Goal
Agree on what the service must do, for which clients, and how well, in terms a tester can verify. No design yet, except constraints the stakeholders impose.

## Entry criteria
- A sponsor and a product owner are named.
- The problem, the clients and their users are known, at least roughly.

## Activities
1. **Brief.** Capture:
   - the problem and who has it;
   - goals with measurable KPIs (e.g. "the app's sync completes for 99% of users within 5 s");
   - in and out of scope;
   - constraints: deadline, budget, team, mandated platforms, identity provider or data stores;
   - approvers and top risks.
2. **API consumers.** For each client: the mobile apps, web front ends, partners and other services. Record:
   - who owns it and how it authenticates;
   - its expected traffic;
   - for mobile apps, **the oldest app version that must keep working** and how long old versions stay in use;
   - how breaking changes and deprecations will be communicated.
3. **Functional requirements.** Write user or client stories, each with an ID (`FR-nnn`), a MoSCoW priority and Given/When/Then acceptance criteria. Cover the unhappy paths:
   - unauthenticated and unauthorised callers (someone else's resource);
   - invalid input, duplicates and concurrent edits;
   - retries of the same request (idempotency);
   - a dependency that is slow or down;
   - limits: page sizes, payload sizes, rates, quotas.
4. **Non-functional requirements.** Each one gets a target, the condition it's measured under, and a verification method. These NFRs are almost always needed:

   | Attribute | Example target (agree the real one) | Verified by |
   |---|---|---|
   | PERF latency | p95 ≤ 200 ms and p99 ≤ 500 ms for `GET /v1/notes` at 200 req/s | Load test (k6) on staging |
   | SCAL throughput | Peak 500 req/s at launch, 3× within 12 months, with horizontal scaling only | Load test; capacity model |
   | AVAIL | 99.9% of requests successful per 28 days (SLO), excluding announced maintenance | SLO dashboard |
   | REL recovery | RPO ≤ 5 min, RTO ≤ 1 h | Restore drill |
   | REL resilience | No data loss or duplicates when a client retries or an instance is killed mid-request | Resilience tests |
   | SEC | ASVS L2 (L1 only if no personal or sensitive data) | ASVS checklist, DAST, authorisation matrix tests |
   | PRIV | Data minimisation; retention periods; access, export and erasure within the legal deadline | Privacy review; tests of the retention job |
   | COMPAT | Every supported client version keeps working; additive changes only within a version | Contract tests against the oldest client's DTOs |
   | OBS | Every request traceable by request ID; RED metrics per endpoint; alerts for each SLO | Observability review |
   | MAINT | ktlint and detekt clean; coverage ≥ 80% in services and domain | CI |
   | OPS | Zero-downtime deploys; rollback in ≤ 10 min | Deployment rehearsal |
5. **Data inventory and classification.** For each kind of data: purpose, classification (public, internal, personal, sensitive), where it's stored, who it's shared with, retention and the legal basis. This feeds the threat model, the privacy controls and the ASVS level.
6. **Integrations.** For each external system: owner, protocol and contract status, environments (sandbox?), rate limits, SLAs, and what happens when it's down.
7. **Compliance.** GDPR, HIPAA, PCI-DSS, SOC 2 or sector rules that apply, data-residency constraints, and audit requirements. Choose the ASVS level.
8. **Acceptance outline.** Write one `AT-` scenario per Must story in the test plan, run on staging through the real client or API scripts.
9. **Validate.** Walk through the requirements with the product owner, a client developer (mobile or web), a backend developer, QA, security and operations. Each requirement must be clear, testable, necessary, and consistent with the others.
10. **Baseline.**
    - Create the RTM rows.
    - Resolve the open TBDs, or accept them explicitly.
    - Ask for sign-off.

## Exit checklist (G1)
- [ ] Every requirement has an ID, a priority and testable acceptance criteria, including the unhappy paths
- [ ] Every consumer is listed with its authentication, traffic and oldest supported version
- [ ] Every NFR has a number, a condition and a verification method; SLOs, RPO and RTO agreed
- [ ] Data inventory and classification complete; ASVS level and compliance scope chosen
- [ ] Integrations listed with their limits and failure behaviour
- [ ] No open TBD blocks a Must requirement
- [ ] Acceptance outline covers every Must requirement; RTM created
- [ ] Approved by the product owner and the tech lead; baseline tagged

## Pitfalls
- **Forgetting old clients.** A mobile app version from last year will still call the API next year.
- **Unmeasurable NFRs** like "fast", "scalable" or "highly available", which nobody can test.
- **Averages instead of percentiles,** or a latency target without a load level.
- **Designing endpoints in the requirements.** Requirements say what clients need; Phase 3 decides paths and payloads.
- **No owner for personal data,** so retention and erasure are discovered after launch.
- **Ignoring a dependency's rate limit or SLA,** which then caps the service's own.
