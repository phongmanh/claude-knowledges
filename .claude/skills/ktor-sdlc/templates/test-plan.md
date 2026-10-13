# Test plan: <Service or feature>

| Version | Status | QA lead | Approvers |
|---|---|---|---|
| 0.1 | Draft | <name> | <product owner, tech lead, operations owner> |

## 1. Scope
- **In scope:** <FR and NFR IDs>
- **Out of scope:** <…>
- **Regression scope** (for a feature): <endpoints and flows to re-test>

## 2. Levels and tools
| Level | Scope | Tools | Runs on | Owner | When |
|---|---|---|---|---|---|
| Unit | Services, domain rules, mappers, validators | kotlin-test, coroutines-test, fakes | CI | Developers | Every PR |
| Integration | Routes (full pipeline), repositories, migrations, schema drift, DI graph, adapters | `testApplication`, Testcontainers PostgreSQL, `MockEngine` | CI with Docker | Developers | Every PR |
| Contract | Generated OpenAPI vs the frozen contract; oldest client's DTOs | OpenAPI diff; consumer contract tests | CI | Developers | Every PR |
| System | End to end through the real identity provider and dependency sandboxes | API test suite; client apps | Staging, RC image | QA | Phase 5 |
| NFR | Load, stress, soak; security; resilience; deployment and restore | k6; OWASP ZAP; fault injection; platform tools | Staging, RC image | QA, operations | Phase 5 |
| Acceptance | Must FRs | The acceptance outline, through the real client | Staging | Product owner, pilot users | Phase 5 |

## 3. Environments and load profiles
| Environment | Size vs production | Data | Purpose |
|---|---|---|---|
| CI | Containers | Generated per test | Unit, integration, contract |
| Staging | <e.g. same instance types, ½ replicas> | Synthetic or anonymised, at production volume (<n> rows in `notes`) | System, NFR, acceptance |

| Profile | Endpoints and mix | Rate | Duration | Pass criteria |
|---|---|---|---|---|
| Expected peak | `GET /v1/notes` 70%, `POST` 20%, `PUT` 10% | <n> req/s | 30 min | p95/p99 within NFR-PERF; errors < 0.1% |
| Stress | Same mix | Ramp to <n>× peak | Until failure | Sheds load with 429/503; recovers without restart |
| Soak | Same mix | Peak | 2–4 h | No growth in latency, memory or pool wait |

## 4. NFR tests
| NFR ID | Test | Method / tool | Target | Result |
|---|---|---|---|---|
| NFR-PERF-01 | Latency at peak | k6 expected-peak profile on staging | | |
| NFR-REL-01 | Restore | Restore the latest backup into a separate environment; time it | | |
| NFR-REL-02 | Retries and instance loss | Repeat `Idempotency-Key`; kill a replica under load | | |
| NFR-SEC-01 | ASVS level; authorisation matrix; DAST | Checklist; matrix tests; ZAP with the contract | | |
| NFR-OPS-01 | Zero-downtime deploy and rollback | Rolling deploy and rollback under load | | |

## 5. Acceptance outline
| AT ID | FR | Scenario (Given / When / Then) | Result |
|---|---|---|---|

## 6. Test data and accounts
- Test users in the identity provider, per role: <…>
- Synthetic data generator or anonymisation process: <…> (never raw production personal data)
- Sandboxes for third parties: <…>

## 7. Entry and exit criteria
| Level | Entry | Exit |
|---|---|---|
| System and NFR | G4 approved; RC image deployed to staging by digest | All `ST-` tests run; NFR targets met or gaps accepted; no open S1/S2 defects |
| Acceptance | System exit criteria met | Product owner signs off |

## 8. Defect severity
| Severity | Meaning |
|---|---|
| S1 | Data loss or corruption, a security issue, an outage |
| S2 | A Must FR is broken, or an NFR target is missed, with no workaround |
| S3 | A workaround exists |
| S4 | Cosmetic |

Each defect records the request ID and the image digest.

---

## Test summary report (Phase 5)
| Level | Planned | Run | Passed | Failed | Blocked |
|---|---|---|---|---|---|

- **NFR results vs targets:** <table or link>
- **Open defects:** S1 <n> · S2 <n> · S3 <n> · S4 <n> (accepted: <list>)
- **Residual risks:** <…>
- **Recommendation:** Go / Go with conditions / No-go, because <reason>
