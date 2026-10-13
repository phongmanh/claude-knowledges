# Requirements: <Service or feature>

| Version | Status | Owner | Approvers |
|---|---|---|---|
| 0.1 | Draft | <product owner> | <product owner, tech lead> |

## 1. Brief
- **Problem:** <who has which problem today>
- **Goals and KPIs:** <measurable, e.g. "sync completes within 5 s for 99% of users">
- **In scope:** <…>
- **Out of scope:** <…>
- **Constraints:** <deadline, budget, team, mandated platform, identity provider, data stores, compliance>
- **Top risks:** <see the STATUS risk register>

## 2. API consumers
| Consumer | Owner | Authenticates with | Expected traffic (avg / peak) | Oldest version to support | How changes are announced |
|---|---|---|---|---|---|
| Android app | <team> | User access token (OIDC) | <n> / <n> req/s | <version>, until <date> | Release notes, deprecation headers |
| iOS app | <team> | User access token (OIDC) | | | |
| Partner X | <company> | Client credentials | | API v1 | Email + changelog, 6 months' notice |

## 3. Functional requirements
| ID | Story | Priority (M/S/C/W) | Acceptance criteria (Given / When / Then) |
|---|---|---|---|
| FR-001 | As a <client or user>, I want <goal>, so that <value> | M | Given … when … then …<br>Unauthorised: …<br>Invalid input: …<br>Retry of the same request: …<br>Dependency down: … |

## 4. Non-functional requirements
| ID | Requirement | Target and condition | Verified by |
|---|---|---|---|
| NFR-PERF-01 | Latency of <endpoint or journey> | p95 ≤ <n> ms, p99 ≤ <n> ms at <n> req/s | Load test on staging |
| NFR-SCAL-01 | Throughput | Peak <n> req/s at launch; <n>× growth in 12 months by adding replicas | Load test; capacity model |
| NFR-AVAIL-01 | Availability SLO | <99.9>% of requests successful per 28 days | SLO dashboard |
| NFR-REL-01 | Recovery | RPO ≤ <n> min, RTO ≤ <n> h | Restore drill |
| NFR-REL-02 | Retries and failures | No duplicates on client retries; no data loss when an instance dies | Resilience tests |
| NFR-SEC-01 | Security level | ASVS <L1/L2/L3> | ASVS checklist, DAST, authorisation tests |
| NFR-PRIV-01 | Privacy | <retention, erasure deadline, residency> | Privacy review; retention-job tests |
| NFR-COMPAT-01 | Client compatibility | Every supported client version keeps working; additive changes only within a version | Contract tests |
| NFR-OBS-01 | Observability | Request IDs end to end; RED metrics per endpoint; an alert per SLO | Observability review |
| NFR-OPS-01 | Deployability | Zero-downtime deploys; rollback in ≤ <n> min | Deployment rehearsal |
| NFR-MAINT-01 | Maintainability | ktlint and detekt clean; coverage ≥ <n>% in services and domain | CI |

## 5. Data inventory
| Data | Classification (public / internal / personal / sensitive) | Purpose | Stored where | Shared with | Retention | Legal basis |
|---|---|---|---|---|---|---|

## 6. Integrations
| System | Owner | Protocol and contract | Environments (sandbox?) | Limits and SLA | If it's down |
|---|---|---|---|---|---|
| Identity provider | | OIDC; JWKS at <url> | | | No new sign-ins; existing tokens stay valid until expiry |

## 7. Compliance
- Regulations: <GDPR, HIPAA, PCI-DSS, SOC 2, sector rules>
- Data residency: <regions>
- Audit requirements: <what must be logged, for how long>
- ASVS level: <L1/L2/L3>, because <reason>

## 8. Acceptance outline
One `AT-` scenario per Must FR, kept in [test-plan.md](test-plan.md) §5.

## 9. Assumptions and open items
- ASSUMPTION: <…>
- TBD-1: <…>

## 10. Sign-off
| Role | Name | Decision | Date |
|---|---|---|---|
