# Phase 2: Architecture
**Gate:** G2 Architecture baseline
**Deliverables:** [architecture document](../templates/architecture.md) (threat model and capacity model inside), [ADRs](../templates/adr.md), master [test plan](../templates/test-plan.md), RTM update
**Load:** [architecture](../reference/architecture.md), [api-design](../reference/api-design.md), [security-privacy](../reference/security-privacy.md), [performance-reliability](../reference/performance-reliability.md), [deployment-operations](../reference/deployment-operations.md), [testing](../reference/testing.md)

## Goal
Decide how the service is structured, deployed, secured and operated to meet the requirements, and fix the stack. Every feature is then designed against the same rules.

## Entry criteria
- G1 approved; the requirements and RTM are baselined.
- The top 3–5 quality goals are ranked (e.g. data integrity > availability > latency).

## Activities
1. **Drivers.**
   - Turn the top NFRs into scenarios, e.g. "At 500 req/s, `GET /v1/notes` answers in ≤ 200 ms at p95 while one database replica is down."
   - Map each scenario to a tactic, e.g. keyset pagination with a covering index; two replicas across zones.
2. **Context.** Draw the system context: clients, the service, its data stores, the identity provider, third-party APIs, queues. Mark the trust boundaries.
3. **Stack.**
   - Start from the [default stack](../reference/architecture.md#default-stack). Write an ADR only for a deviation or an open choice, e.g. Exposed vs jOOQ, Netty vs CIO, the tracing setup, OpenAPI generation from code.
   - Record the Ktor, Kotlin and JDK versions, and check that Ktor's compiler plugin supports the Kotlin version.
4. **Module layout.** Apply the [size rule](../reference/architecture.md#module-layout): one module with feature packages, or Gradle modules per bounded context. Record the choice in an ADR and draw the module graph. Decide whether a shared `api-contract` module with KMP clients is used ([shared contract module](../reference/architecture.md#shared-contract-module)).
5. **API style and versioning.**
   - REST + JSON per [api-design.md](../reference/api-design.md); GraphQL or gRPC only by ADR.
   - The versioning scheme, the deprecation process and the oldest supported client versions.
   - Where the OpenAPI contract lives and how CI checks it.
6. **Data stores.** For each store: what it holds, why this store (access pattern), consistency needs, size and growth, backup, retention.
   - PostgreSQL by default; any other store (cache, search, object storage, queue) needs a stated need.
   - Migration policy: Flyway, expand → migrate → contract, a migration job before each rollout.
7. **Authentication and authorisation model.**
   - The identity provider, token type and lifetime, the claims used (subject, roles, scopes, tenant).
   - The authorisation matrix: who may do what to which resources, including object-level rules (owner, member, admin).
   - Service-to-service authentication.
8. **Deployment topology.**
   - The platform (ADR), regions and zones, environments (dev, staging, production) and how they differ.
   - Replicas, probes, autoscaling signals, the ingress or load balancer, TLS termination, network boundaries.
   - Rollout strategy (rolling, canary, blue-green) and the rollback path.
9. **Capacity model.**
   - Expected and peak traffic per endpoint, data volume and growth.
   - The bottleneck (usually the database): connection limits, pool size per replica, replica count, the headroom.
   - Cost estimate.
10. **Reliability design.** Timeouts per dependency, retry and idempotency rules, circuit breakers, the outbox for events, scheduled jobs and their locking, graceful degradation. See [reliability](../reference/performance-reliability.md#reliability).
11. **Cross-cutting decisions.**
    - Configuration and secrets: `AppConfig`, the secret manager, rotation.
    - DI modules; the error model and the error-code catalogue.
    - Logging format and redaction; metrics; tracing; the audit log.
    - Feature flags and kill switches.
    - Time zones (UTC), IDs (UUID v7), money and i18n of server-generated text.
12. **Threat model.**
    - List the assets: personal data, credentials, tokens, money, availability.
    - List the entry points: each API group, webhooks, admin interfaces, queues, the database, CI/CD.
    - Apply STRIDE to each entry point, and walk through the OWASP API Security Top 10.
    - Map each mitigation to an ASVS control and a requirement ID.
13. **Observability and operations.**
    - SLOs per critical journey and their error-budget alerts.
    - Dashboards, on-call ownership, the runbooks to write before launch.
    - Backups, restore drills and the DR tier for the RPO and RTO.
14. **Build and delivery.**
    - CI stages as in [Phase 4](4-implementation.md#ci-pipeline); the image build, scanning, signing and promotion by digest.
    - Infrastructure as code; who can deploy to production and how.
15. **Test strategy.** The master test plan covers:
    - test levels, tools and where they run;
    - environments (ephemeral per PR where feasible, staging sized for load tests), test data without production PII;
    - load profiles and the NFR tests;
    - entry and exit criteria per level.
16. **Proofs of concept.** For each risky unknown, run a time-boxed, throwaway spike. Typical backend spikes:
    - the heaviest query on production-sized data, with its index;
    - throughput of the critical endpoint on one replica, to calibrate the capacity model;
    - integration with the identity provider (token claims, JWKS rotation);
    - a third-party API's real latency and failure modes;
    - an experimental library feature the design depends on.

    Record each outcome in its ADR.
17. **Review.** Walk each driver scenario through the design with the tech lead, a senior backend developer, a client developer, QA, security and operations.

## Exit checklist (G2)
- [ ] Each NFR maps to a tactic; driver scenarios walked through
- [ ] Stack deviations, module layout, deployment platform and API style recorded in accepted ADRs; versions compatible
- [ ] Context diagram, data stores, deployment topology and capacity model complete
- [ ] Authentication and authorisation model, including object-level rules, defined
- [ ] Threat model reviewed; mitigations mapped to ASVS controls and requirement IDs
- [ ] SLOs, alerts, backup and DR approach, and rollout and rollback strategy defined
- [ ] Master test plan with environments and load profiles approved
- [ ] Risky unknowns retired by a PoC or formally accepted
- [ ] RTM updated; baseline tagged

## Pitfalls
- **Microservices by default.** Several services multiply the deployment, data-consistency and observability work; start with one deployable unless a driver says otherwise.
- **A shared database between services,** which couples their schemas and releases.
- **No capacity model,** so the pool size, replica count and database size are guesses.
- **Authorisation as "check the token".** A valid token says who the caller is, not what they may touch.
- **Treating the threat model as paperwork.** Every mitigation must become a requirement or a design element.
- **Leaving operations to the end:** no SLOs, no runbooks and no restore drill until the week before launch.
