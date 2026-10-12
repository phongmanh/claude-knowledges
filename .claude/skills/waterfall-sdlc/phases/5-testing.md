# Phase 5: Testing (integration, system, acceptance)
**Gate:** G5 Release readiness (PRR, go/no-go)
**Deliverables:** [test plans and reports](../templates/test-plan.md), UAT and OAT sign-off, test summary report

## Goal
Verify that the system meets the SRS, both functional and non-functional requirements. Validate that it meets users' needs. Produce the evidence for the go/no-go decision.

## Entry criteria
- G4 approved.
- The release candidate is deployed to a **production-like staging** environment and has passed a smoke test.
- Test data is ready. It is synthetic or masked, and **never raw production PII**.
- Test cases have been reviewed.
- Test accounts exist for every role.
- The defect process is agreed.

## Activities
1. **Integration testing** (verifies the Phase 3 designs):
   - Run contract tests that verify each provider against its consumers' contracts.
   - Test against the real database engine running in containers, not an in-memory substitute that behaves differently.
   - Test third-party integrations against their sandboxes.
   - Run queue and event flows end to end.
   - Test the client ↔ API integration.
2. **Functional system testing** (verifies Phase 2 and the SRS):
   - Run end-to-end scenarios from the use cases, including alternate and exception flows.
   - Cover business rules, the role/permission matrix, data validation and error handling.
   - Test offline and poor-network behaviour, and upgrade paths.
3. **Non-functional system testing.** Verify each NFR with the method stated in the SRS. The [catalogue](#non-functional-test-catalogue) below lists the tests per attribute.
4. **Regression testing.** The automated suite (unit, integration and key end-to-end tests) runs on every build. A full regression runs on the final release candidate.
5. **Acceptance testing** (validates Phase 1):
   - **UAT.** Business users and the PO run the acceptance scenarios in staging and sign off.
   - **OAT (operational acceptance testing).** Check that:
     - alerts fire and reach on-call;
     - dashboards show the right data;
     - logs are searchable;
     - runbooks work;
     - backup and restore succeed;
     - deployment and rollback have been rehearsed.
   - **Beta or pilot (optional).** Use store test tracks for mobile, or a feature-flagged group of users for web.
6. **Defect management.**
   - Keep one tracker. Record **severity** (impact) separately from **priority** (urgency):
     - **S1 critical:** crash, data loss or security breach, with no workaround.
     - **S2 major:** a key function is broken, or the workaround is painful.
     - **S3 minor:** a function is impaired, but there is a reasonable workaround.
     - **S4 trivial:** cosmetic.
   - Triage daily during system testing.
   - Move each defect through this lifecycle: New → Triaged → In progress → Fixed → Verified → Closed. A defect can also end as Rejected or Deferred.
   - Verify every fix and cover it with a regression test.
   - A deferred defect needs PO acceptance and goes on the known-issues list.
   - Record the phase where each defect was introduced. This feeds the [defect leakage metrics](../governance.md#quality-assurance-and-metrics).
7. **Reporting.**
   - Track execution progress, pass rate, defect discovery vs. closure trends (the two should converge), requirement coverage and NFR results.
   - Finish with the test summary report and a go/no-go recommendation.

### Non-functional test catalogue
| Attribute | Tests | Pass criterion |
|---|---|---|
| Performance | Load (expected peak), stress (find the breaking point), soak (several hours, to find leaks), spike. **Backend:** p95/p99, throughput, errors, resource use. **Web:** lab Core Web Vitals on a throttled mid-tier device, plus bundle budgets. **Mobile:** cold and warm start, frame rendering (jank), memory, battery, network use and app size on low-end reference devices | NFR-PERF targets |
| Scalability | Step-load test showing throughput grows as instances are added; autoscaling up and down; capacity model checked against results | NFR-SCAL targets |
| Security | Authenticated DAST. API tests for broken object- and function-level authorisation, mass assignment and rate limits. Static and dynamic mobile tests per MASTG. IaC and cloud configuration scans. Audit of the final SBOM. Independent penetration test for high-risk systems. Each threat-model mitigation verified | No open critical/high findings; ASVS/MASVS level met |
| Accessibility | Automated scans (they catch only some issues) **plus** manual tests with screen readers, keyboard only, 200% zoom and font scaling, and contrast checks | WCAG 2.2 AA (or agreed exceptions); conformance report |
| Compatibility | Device and OS matrix, browser matrix, screen sizes, network conditions (offline, slow, high latency), locales, time zones and DST changes | Matrix passes |
| Reliability / resilience | Instance and zone failover; dependency outages and slowness via fault injection; duplicate message delivery (idempotency); recovery from a queue backlog; backup restore and DR drill | NFR-AVAIL targets; RPO/RTO met |
| Usability | Moderated or unmoderated tests of key tasks with representative users | Task success and SUS targets |
| Localisation | Pseudo-localisation, text expansion and truncation, RTL layouts, formats, in-context review of translations | No open S1/S2 defects |
| Install / upgrade / migration | **Mobile:** fresh install, and upgrade from **every supported version** with data preserved. **Web:** cache-busting after a deploy. **Backend:** migrations on a production-sized masked dataset (timing, rollback); data-migration reconciliation | Data intact; timings within the window |
| Privacy / compliance | Consent flows, data export and deletion, retention jobs, audit logs, store policy checklist | PRIV/SEC requirements pass |

## Platform specifics

### Mobile
- Test on real devices across the matrix, starting with low-end devices. Cover OS versions from the minimum supported up to the latest beta.
- Test interruptions: incoming calls, backgrounding, low battery, permission revocation, network switches, process death.
- Run the store pre-launch and review checks. Distribute the beta through store test tracks.

### Frontend
- Test across browsers, including real mobile browsers.
- Do keyboard-only and screen-reader passes on the key journeys.
- Measure lab performance for each key page under throttling. Check that field monitoring is wired up for after launch.
- Check deploy-time behaviour: users who still have the old version open keep working, with no missing chunks.

### Backend
- Run load tests against a production-like topology, with realistic data volumes and request mixes.
- Run chaos and fault-injection tests on dependencies. Test failover, and restoring from backup within the RTO.
- Rehearse migrations on production-sized data.
- Run API compatibility tests against the oldest supported client.

## Deliverables
- Integration, system, NFR and acceptance test plans and cases ([templates/test-plan.md](../templates/test-plan.md)).
- Execution logs and the defect log.
- Performance, security (including the pen test), accessibility conformance and compatibility reports.
- UAT and OAT sign-offs.
- The test summary report, with a go/no-go recommendation.
- A complete RTM: requirement → executed tests → results.

## Exit gate checklist (G5)
- [ ] 100% of planned tests executed; 100% of Must requirements passed
- [ ] 0 open S1/S2 defects; S3/S4 defects triaged, accepted by the PO and listed as known issues
- [ ] Every NFR target met, or formally waived with recorded risk acceptance
- [ ] No open critical/high security findings; ASVS/MASVS level verified
- [ ] WCAG 2.2 AA met (or exceptions accepted); conformance report done
- [ ] UAT and OAT signed off
- [ ] RTM complete; test summary report approved
- [ ] Go/no-go recommendation presented and the decision recorded

## Pitfalls
- **Overruns eat the test window.** Protect it in the plan, and cut scope through a CR rather than cutting testing.
- **The test environment isn't production-like** (different configuration, data size or topology).
- **Performance tests use tiny or unrealistic data** and request mixes.
- **Skipping mobile upgrade tests.** Data lost during an upgrade can't be rolled back.
- **Treating automated accessibility scans as a full audit.**
- **Using real production personal data** in test environments.
