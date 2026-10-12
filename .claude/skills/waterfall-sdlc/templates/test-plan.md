# Test plan: <System or feature name>

| Version | Status | Owner | Approvers | Last updated |
|---|---|---|---|---|
| 0.1 | Draft | <QA lead> | <QA lead, PO, tech lead> | YYYY-MM-DD |

> Structure based on ISO/IEC/IEEE 29119-3.
>
> This file starts as the master test plan (Phase 2) and grows a section per test level:
> - acceptance tests, drafted in Phase 1;
> - system tests, in Phase 2;
> - integration tests, in Phase 3.
>
> For a feature, write a single plan and include the regression scope.

## 1. Scope and objectives
What is tested, what isn't, and why.

## 2. Test items and features
| Requirement ID | Feature | Test level(s) | Test case IDs |
|---|---|---|---|

## 3. Test levels and types
| Level | Basis (V-model) | Owner | Environment | Automation |
|---|---|---|---|---|
| Unit / component | Implementation | Developers | CI | Full |
| Integration / contract | Detailed design | Developers + QA | CI / test env | Full |
| System (functional) | System design + SRS | QA | Staging | High |
| System (non-functional) | NFRs | QA + SRE + security | Staging | Partial |
| Acceptance (UAT / OAT) | Requirements | PO / users / operations | Staging | Low |

## 4. Non-functional test approach
| NFR ID | Test type | Tool category | Load / data / device profile | Pass criterion |
|---|---|---|---|---|

## 5. Acceptance tests (drafted in Phase 1)
| Test ID | Requirement ID | Scenario (Given / When / Then) | Data | Accepted by |
|---|---|---|---|---|

## 6. Environments and test data
- **Environments:** how each one mirrors production. Document every difference.
- **Device / browser matrix:** …
- **Test data:**
  - synthetic or masked, never raw production PII;
  - how it is refreshed;
  - test accounts for each role.

## 7. Entry, exit, suspension and resumption criteria
| Level | Entry | Exit | Suspend when | Resume when |
|---|---|---|---|---|

## 8. Defect management
| Severity | Meaning |
|---|---|
| S1 critical | Crash, data loss or security breach; no workaround |
| S2 major | Key function broken; workaround is painful |
| S3 minor | Function impaired; reasonable workaround |
| S4 trivial | Cosmetic |

- **Priority** is recorded separately from severity.
- **Triage cadence:** e.g. daily during system testing.
- **Lifecycle:** New → Triaged → In progress → Fixed → Verified → Closed (or Rejected / Deferred).
- **Deferral rule:** the PO accepts the defect, and it goes on the known-issues list.

## 9. Schedule and responsibilities
## 10. Risks and contingencies
## 11. Deliverables and reporting
- **Deliverables:** execution logs, defect reports, NFR reports.
- **Metrics:** progress, pass rate, defect discovery vs. closure trend, requirement coverage.

---

# Test summary report: <release / RC version>

| Item | Result |
|---|---|
| Tests planned / executed / passed / failed / blocked | |
| Must requirements passed | x / y |
| Open defects by severity (S1 / S2 / S3 / S4) | |
| NFR results vs. targets | link |
| Open security findings (critical / high / medium / low) | |
| Accessibility conformance (WCAG 2.2 AA) | |
| UAT sign-off / OAT sign-off | |
| Known issues accepted by the PO | link |
| **Recommendation** | Go / Go with conditions / No-go |

- **Approved by:** <QA lead>
- **Date:** YYYY-MM-DD
