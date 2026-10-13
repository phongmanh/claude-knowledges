# Phase 5: Testing
**Gate:** G5 Release readiness (go/no-go). Never skipped or combined.
**Deliverables:** test execution reports, defect log, UAT sign-off, test summary report (in the [test plan](../templates/test-plan.md)), RTM update
**Load:** [testing](../reference/testing.md), [security-privacy](../reference/security-privacy.md), [performance-reliability](../reference/performance-reliability.md), [deployment-operations](../reference/deployment-operations.md)

## Goal
Prove on a production-like environment that the service meets every requirement and NFR under realistic load and failure, and give the go/no-go decision a base of evidence.

## Entry criteria
- G4 approved; the RC image is deployed to staging by digest, with production settings (only sizes differ).
- The test plan is approved; staging has realistic data volume (synthetic or anonymised, never raw production PII); test accounts exist in the identity provider.

## Activities
1. **Run the test levels** from the master test plan, against the **RC image**:

   | Level | What | Tools |
   |---|---|---|
   | Integration (`IT-`) | Already green in CI: routes, repositories, migrations, adapters | `testApplication`, Testcontainers, `MockEngine` |
   | Contract (`CT-`) | The served API vs the frozen contract; the oldest supported client's DTOs still parse every response | OpenAPI diff; consumer contract tests |
   | System (`ST-`) | End to end on staging, through the real identity provider and dependencies (or their sandboxes) | API test suite, the client apps |
   | Acceptance (`AT-`) | The product owner and pilot users | The acceptance outline, through the real client on staging |
2. **NFR tests**, each against its requirement's target:
   - **Performance and scalability:**
     - load test each critical endpoint at the target throughput and check p95/p99 (k6 thresholds);
     - a stress test beyond the peak to find the breaking point and see that the service sheds load (429/503) rather than collapsing;
     - a soak test (e.g. 2–4 h at peak) for leaks, pool exhaustion and slow growth in latency;
     - scale-out: add replicas under load and check throughput grows.
   - **Security:**
     - the ASVS checklist at the agreed level;
     - authorisation matrix tests: every endpoint with every role, and with another user's object IDs (BOLA);
     - DAST against staging (e.g. OWASP ZAP with the OpenAPI contract as input);
     - token tests: expired, wrong audience, wrong issuer, tampered signature, `alg: none`;
     - rate limits and body-size limits;
     - dependency and image scan results reviewed; secrets scan of the repository.
   - **Reliability and resilience:**
     - kill an instance mid-load: no failed requests beyond the in-flight ones, no duplicates on retry;
     - make the database unavailable, then restore it: readiness fails, the service recovers without a restart;
     - slow down and fail each dependency: timeouts fire, circuit breakers open, degraded responses as designed;
     - retry the same `Idempotency-Key`: one effect only.
   - **Deployment:**
     - a rolling deploy under load: zero failed requests;
     - the migration job against a copy of production-sized data, timed;
     - a rollback to the previous image with the new schema.
   - **Recovery:** restore the latest backup into a separate environment and measure the time against the RTO; check the data loss window against the RPO.
   - **Observability:** each alert fires in a controlled test and links to a working runbook; dashboards show the RC's metrics, logs and traces with the call ID end to end.
3. **Defects.**
   - Log each one with its steps, request ID, build (image digest) and severity:
     - S1: data loss or corruption, a security issue, an outage;
     - S2: a Must FR is broken, or an NFR target is missed, with no workaround;
     - S3: a workaround exists;
     - S4: cosmetic (e.g. a wording in an error `detail`).
   - Fix them in a new RC image. Re-run the affected tests plus a regression subset.
4. **Test summary report.** Results per level, NFR results against their targets, open defects by severity, residual risks, and a recommendation.
5. **Go/no-go.** Present the report and the G5 checklist to the product owner, the tech lead, the QA lead and the operations owner.

## Exit checklist (G5)
- [ ] Every Must FR has a passing `AT-` or `ST-` test; the RTM shows full coverage
- [ ] Every NFR measured and within target, or the gap formally accepted
- [ ] No open S1 or S2 defects; S3 defects reviewed and accepted
- [ ] ASVS checklist passed at the agreed level; authorisation matrix tests pass; no open high or critical DAST findings
- [ ] Resilience, rolling-deploy, rollback and restore tests passed; migration time known
- [ ] Contract checks pass, including against the oldest supported client
- [ ] Alerts, dashboards and runbooks verified
- [ ] UAT signed off; test summary report approved

## Pitfalls
- **Load testing an empty database,** where every query is fast.
- **Testing a different build** than the one that will be deployed. Promote the same image digest.
- **Only happy-path security tests.** Most API breaches are one user reading another user's data (BOLA).
- **Skipping the restore test,** so the first restore happens during an incident.
- **Testing resilience by reading the code** instead of breaking things on staging.
- **Lowering the exit criteria** to hit a date, instead of escalating the risk.
