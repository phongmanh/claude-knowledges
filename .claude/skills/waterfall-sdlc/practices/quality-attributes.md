# Quality attributes: specify, verify, operate

For each quality attribute, this page covers three steps:
- turning it into measurable requirements (Phase 1);
- verifying it (Phase 5);
- watching it in production (Phase 7).

The engineering practices for each platform are in [mobile.md](mobile.md), [frontend.md](frontend.md) and [backend.md](backend.md). Attributes follow ISO/IEC 25010 (the product quality model).

## Writing a measurable NFR
`NFR-<ATTR>-<nn>: <system or component> shall <measurable behaviour> under <condition>, measured by <method>.`

- ✅ `NFR-PERF-01: The search API shall respond within 300 ms at p95 under a sustained 500 requests/s for 30 minutes, measured by a load test in staging.`
- ❌ "Search should be fast."
- Use percentiles (p95, p99), not averages. Averages hide the slow experiences.
- State the condition (load, device, network) and the measurement method. Without them, the NFR can't be tested.
- Targets below marked "e.g." are **examples**. Agree the real targets with stakeholders in the SRS. Values named as standards (Core Web Vitals, WCAG, availability arithmetic) are reference facts.

## Summary
| Attribute (ATTR) | ISO/IEC 25010 | Verified in Phase 5 by | Watched in Phase 7 via |
|---|---|---|---|
| [Performance](#performance-perf) (PERF) | Performance efficiency | Load/stress/soak tests, lab Core Web Vitals, device profiling | APM, real-user monitoring, mobile vitals |
| [Scalability](#scalability-scal) (SCAL) | Flexibility (scalability), performance efficiency (capacity) | Step-load and autoscaling tests | Saturation metrics, capacity reviews |
| [Availability & reliability](#availability--reliability-avail) (AVAIL) | Reliability | Failover tests, fault injection, restore and DR drills | SLOs, error budgets, incidents |
| [Security](#security-sec) (SEC) | Security | SAST, SCA, DAST, pen test, MASTG | Vulnerability management, security monitoring |
| [Privacy & compliance](#privacy--compliance-priv) (PRIV) | Security (confidentiality), functional suitability | Privacy review; consent, export and deletion tests | Data-subject request handling, audits |
| [Maintainability](#maintainability-maint) (MAINT) | Maintainability | Static analysis, architecture checks, review | Debt register, hotspot analysis |
| [Testability](#testability-test) (TEST) | Maintainability (testability) | Coverage, suite duration, flakiness | Escaped defects |
| [Usability & accessibility](#usability--accessibility-a11y) (A11Y) | Interaction capability | Usability tests, WCAG audit | Funnels, feedback, accessibility regressions |
| [Compatibility](#compatibility-compat) (COMPAT) | Compatibility, flexibility | Device and browser matrix, contract tests against old clients | Usage by OS, browser and app version |
| [Observability](#observability-obs) (OBS) | Maintainability (analysability) | OAT, game days | Mean time to detect / restore |
| [Internationalisation](#internationalisation-i18n) (I18N) | Interaction capability, flexibility | Pseudo-localisation, RTL tests, linguistic review | Locale-specific defects |
| [Cost efficiency](#cost-efficiency-cost) (COST) | — | Cost model vs. resource use measured in load tests | Cost per user or transaction |

## Performance (PERF)
**Example targets**
- **Mobile** (e.g.):
  - Cold start ≤ 2 s and warm start ≤ 1 s on the reference low-end device.
  - Fewer than 1% janky frames on key screens. Frames must render within the display's frame budget, about 16 ms at 60 Hz.
  - Download size ≤ 30 MB.
- **Web:**
  - Core Web Vitals "good" thresholds at p75 of field data: **LCP ≤ 2.5 s, INP ≤ 200 ms, CLS ≤ 0.1**. These are the standard thresholds.
  - A JavaScript budget per route (e.g. ≤ 200 KB compressed).
- **Backend** (e.g.):
  - For interactive reads at the expected peak: p95 ≤ 300 ms and p99 ≤ 800 ms.
  - Error rate < 0.1% under load.
  - CPU < 70% at peak.

**Principles**
- Measure before optimising.
- Set budgets and enforce them in CI.
- Optimise the critical path that users wait on.
- Use percentiles, not averages.
- Test with realistic data on low-end devices and slow networks.

**Verify:** load, stress, soak and spike tests; lab Core Web Vitals under throttling; profiling and benchmarks on devices.

**Operate:** APM traces; real-user monitoring (web); mobile vitals (startup, frames, ANRs). Alert on regressions in each release.

## Scalability (SCAL)
**Example targets**
- **Backend** (e.g.):
  - Handle 3× today's peak by adding instances, with cost growing no faster than load.
  - Scale out within 5 minutes.
  - Absorb three years of data growth without a redesign.
- **Mobile and web clients:**
  - Avoid a synchronised "thundering herd". For example, spread scheduled syncs over a time window with jitter.
  - Behave gracefully on HTTP 429/503.

**Principles**
- Stateless services that scale horizontally.
- Asynchronous processing to level out load.
- Caching close to the user.
- Partition only when measurements demand it.
- No single points of contention: no global locks, hot rows or hot keys.
- Backpressure and load shedding beat collapse.

**Verify:** step-load tests showing throughput grows as instances are added; tests that autoscaling works in both directions; the capacity model checked against the test results.

**Operate:** saturation metrics (CPU, memory, connections, queue depth); capacity reviews; cost per request.

## Availability & reliability (AVAIL)
**Example targets**
- **Backend** (e.g.):
  - An availability SLO for each critical journey, e.g. 99.9% per month.
  - RPO ≤ 15 min, RTO ≤ 1 h, MTTR ≤ 1 h.
- **Mobile** (e.g.):
  - Crash-free users ≥ 99.5% per release.
  - Key flows usable offline, as specified.
- **Web** (e.g.):
  - JavaScript error rate below 0.5% of page views.
  - Core content still renders when non-critical services fail.

**Downtime allowed per average month (≈ 730 h)**
| SLO | Downtime per month |
|---|---|
| 99% | ≈ 7.3 h |
| 99.5% | ≈ 3.65 h |
| 99.9% | ≈ 43.8 min |
| 99.95% | ≈ 21.9 min |
| 99.99% | ≈ 4.4 min |

Each extra "nine" costs much more in redundancy, automation and on-call. Choose a target per journey rather than one number for everything.

**Principles**
- Design for failure: every dependency will sometimes be slow or down.
- Put timeouts everywhere.
- Retry only when it's safe (the operation is idempotent), with backoff and jitter.
- Prefer graceful degradation to total failure.
- Make anything that might be repeated idempotent.
- A backup is only real once it has been restored.

**Verify:** failover tests, fault injection, duplicate-delivery tests, restore and DR drills.

**Operate:** SLO dashboards and error budgets; burn-rate alerts; incident management and blameless postmortems.

## Security (SEC)
**Example targets**
- **Web and API:** OWASP ASVS **Level 2** for most systems that handle personal or sensitive data. Level 1 is the minimum for anything internet-facing. Level 3 is for high-value targets such as finance, health or critical infrastructure.
- **Mobile:** OWASP MASVS with MASTG profile **L1**, or **L2** for sensitive data. Add **R** where resistance to reverse engineering and tampering matters.
- **At release:** zero open critical or high vulnerabilities.
- **Remediation SLAs** (e.g.): critical ≤ 7 days, high ≤ 30 days.

**Principles**
- Least privilege; deny by default.
- Defence in depth; secure defaults.
- Minimise the attack surface.
- Never trust input from clients or third parties.
- Fail securely.
- No security through obscurity, and no custom cryptography.
- Secrets never go in code or clients.
- Separation of duties.
- Zero trust between services.

**Secure SDLC map** (aligned with NIST SSDF SP 800-218 and OWASP SAMM)
| Phase | Security activities |
|---|---|
| 0 Initiation | Classify data; identify regulations; budget for security work and testing |
| 1 Requirements | Choose the ASVS/MASVS level; write security and privacy requirements and abuse cases; run a DPIA if needed |
| 2 System design | Threat model (STRIDE); identity and authorisation design; secrets and key management; security architecture review |
| 3 Detailed design | Validation per field; authorisation matrix; crypto choices; security logging; threat model per component |
| 4 Implementation | Secure coding standard; SAST, SCA and secrets scanning in CI; security-focused code review; SBOM |
| 5 Testing | DAST, API security tests, MASTG tests, configuration scanning, penetration test, verification of each mitigation |
| 6 Deployment | Hardened configuration; signed artifacts; secrets per environment; least-privilege access; WAF/DDoS protection where exposed |
| 7 Maintenance | Vulnerability management with SLAs; patching; key rotation; access reviews; monitoring; incident response |

**Verify:** SAST, SCA, secrets scanning, DAST, MASTG tests, pen test, IaC scanning (see [Phase 5](../phases/5-testing.md)).

**Operate:**
- Security monitoring and alerting, e.g. on authentication anomalies and privilege changes.
- A WAF.
- Vulnerability SLAs.
- Periodic access reviews and pen tests.

## Privacy & compliance (PRIV)
**Example targets**
- A complete data inventory and records of processing.
- Data-subject requests answered within the legal deadline (e.g. one month under GDPR).
- Retention periods enforced automatically.
- No PII in logs or analytics.
- A tested breach-notification procedure.

**Principles**
- Privacy by design and by default.
- Collect the minimum; use data only for its stated purpose.
- Consent that is informed, specific and revocable.
- Pseudonymise or tokenise where possible.
- Keep data in the required regions.
- Audit third-party SDKs and services for what they collect.

**Verify:**
- Follow up on the DPIA or privacy review.
- Test consent, export, deletion and retention.
- Check that store privacy disclosures match what the app actually collects.

**Operate:** a process for data-subject requests; retention jobs; periodic audits; updates whenever laws or store policies change.

## Maintainability (MAINT)
**Example targets** (e.g.)
- Zero new critical static-analysis issues per PR.
- Cyclomatic complexity per function ≤ 10–15.
- Duplication ≤ 3%.
- Architecture dependency rules enforced automatically.
- A new developer has the environment running within one day.

**Principles**
- SOLID; DRY, but without premature abstraction; KISS; YAGNI; separation of concerns; high cohesion and low coupling.
- Layered or clean architecture, with dependencies pointing inward. Modules have small public interfaces.
- One consistent way to do common things: errors, logging, validation, configuration.
- Decisions recorded as ADRs; docs kept as code; small PRs with mandatory review.
- The Boy Scout rule: leave the code cleaner than you found it.
- Few dependencies, kept current, each with an owner. Remove feature flags once they're done.

**Verify:** static analysis and architecture-conformance checks in CI; code review.

**Operate:** a technical debt register; hotspot analysis (churn × complexity); regular dependency upgrades.

## Testability (TEST)
**Example targets** (e.g.)
- Every requirement covered by at least one test (RTM).
- Line coverage on business logic ≥ 80%.
- PR pipeline ≤ 15 min.
- Flaky tests < 1%. Quarantine and fix them; never ignore them.

**Principles**
- Depend on abstractions and inject dependencies, including clocks, random sources and dispatchers/schedulers, so tests can control them.
- Keep business logic pure and free of framework, UI and I/O code.
- Contract-first interfaces enable mocks and parallel work.
- Follow the test pyramid: many fast unit tests, fewer integration tests, few end-to-end tests (critical journeys only).
- Give UIs stable test hooks. Accessibility identifiers and labels double as test selectors.
- Keep test environments ephemeral and reproducible, and use builders for test data.

**Verify:** coverage and RTM reports; suite duration; flakiness tracking; mutation testing for critical logic (optional).

**Operate:** analyse escaped defects, and add tests for them.

## Usability & accessibility (A11Y)
**Example targets**
- WCAG 2.2 Level AA.
- Key tasks completed by ≥ 90% of test users (e.g.).
- SUS score ≥ 75 (e.g.; 68 is average).
- Platform design guidelines followed.

**Reference values**
- **Contrast:** text ≥ 4.5:1, or ≥ 3:1 for large text. UI components and graphics ≥ 3:1.
- **Touch and click targets:** ≥ 48×48 dp on Android; ≥ 44×44 pt on iOS; on the web, at least 24×24 CSS px (WCAG 2.2 SC 2.5.8).
- **Reflow and zoom:** content reflows at 320 CSS px wide, and text scales to 200% without loss.

**Principles**
- Design every state.
- Write clear, specific error messages that offer a way to recover.
- Use consistent patterns.
- Don't rely on colour alone.
- Support screen readers, keyboard, switch access, font scaling and reduced motion.
- Use inclusive language.

**Verify:** usability tests; heuristic review; automated plus manual accessibility audit; conformance report.

**Operate:** funnel analytics; feedback channels; accessibility regression checks when things change.

## Compatibility (COMPAT)
**Example targets**
- A support matrix (OS versions, devices, browsers) based on real audience data.
- The API stays backward compatible with app versions released in the last e.g. 12 months.
- A graceful message for unsupported browsers.

**Principles**
- Use feature detection rather than user-agent sniffing.
- Build with progressive enhancement.
- Be a tolerant reader: ignore unknown fields and handle unknown enum values.
- Make only additive API changes.
- Prefer standard protocols and formats, to limit lock-in.

**Verify:** test the device and browser matrix on real devices; run contract tests against the oldest supported client.

**Operate:** track usage by OS, browser and app version to plan deprecations.

## Observability (OBS)
**Example targets**
- Every service emits structured logs, RED metrics and traces.
- Every alert has a runbook.
- Mean time to detect ≤ 5 min for issues that affect SLOs (e.g.).
- One correlation ID traces a request from the client to the database.

**Principles**
- Structured logs with consistent fields.
- Correlation and trace context propagated across clients, services and queues (OpenTelemetry).
- Use RED metrics (rate, errors, duration) for services and USE metrics (utilisation, saturation, errors) for resources.
- Alert on SLO burn rate rather than raw thresholds.
- Collect client telemetry: crashes and real-user performance.
- Keep audit logs separate from application logs.
- No PII in telemetry.

**Verify:** OAT checks; game days where the team diagnoses injected faults.

**Operate:** dashboards per service and per user journey; regular alert-hygiene reviews; log retention and cost controls.

## Internationalisation (I18N)
**Example targets**
- 100% of user-facing strings externalised.
- Supported locales listed.
- RTL layouts supported where needed.
- Dates, numbers and currencies formatted for the locale.

**Principles**
- Strings have keys, with ICU-style plurals and gender. Never concatenate translated fragments.
- Store times in UTC and display them in local time.
- Use Unicode (UTF-8) end to end.
- Layouts tolerate text expansion and mirror for RTL.
- Sorting and search are locale-aware.

**Verify:** pseudo-localisation, RTL testing, in-context linguistic review.

**Operate:** a translation workflow for new strings; track defects by locale.

## Cost efficiency (COST)
**Example targets** (e.g.)
- Infrastructure cost per monthly active user, or per 1,000 transactions, at or below an agreed amount.
- Budget alerts at 80% and 100%.

**Principles**
- Right-size resources and autoscale; scale idle workloads to zero.
- Cache to cut compute and egress.
- Use storage lifecycle policies.
- Tag every resource with an owner and an environment.
- Use reserved capacity for steady load and interruptible capacity for batch work.

**Verify:** compare the cost model with the resource use measured during load tests.

**Operate:** a monthly cost review per service and environment.

## Trade-offs
Attributes compete. Decide each trade-off explicitly in an ADR, guided by the quality goals ranked in Phase 1.

| Tension | Example |
|---|---|
| Security ↔ usability | MFA and short sessions add friction. Use risk-based step-up authentication. |
| Consistency ↔ availability/latency | Strong consistency across regions adds latency. Eventual consistency needs conflict handling. |
| Offline ↔ simplicity | Offline-first mobile needs sync and conflict resolution. |
| Scalability ↔ simplicity | Microservices let teams and parts scale independently, but add distributed-system complexity. |
| Performance ↔ maintainability | Hand-optimised code is harder to change. Optimise only measured hot spots. |
| Cost ↔ availability | Each extra nine of availability costs more redundancy and on-call. |
