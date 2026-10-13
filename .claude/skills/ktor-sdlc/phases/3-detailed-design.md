# Phase 3: Detailed design
**Gate:** G3 Ready to build
**Deliverables:** one [feature design](../templates/feature-design.md) per feature (`design/<feature>.md`), the OpenAPI contract for its endpoints, integration and contract test cases, RTM update
**Load:** [api-design](../reference/api-design.md), [code-patterns](../reference/code-patterns.md), [security-privacy](../reference/security-privacy.md), [testing](../reference/testing.md)

## Goal
Specify each feature precisely enough that any Kotlin developer can build it without guessing, a client team can build against its contract in parallel, and a reviewer can check the code against both.

## Entry criteria
- G2 approved; the architecture, authorisation model and ADRs are baselined.
- The client screens or flows that use the feature are known, so the payloads fit what clients actually need.

## Activities
Fill in the template for each feature:
1. **Endpoints.** For each one: `METHOD /path`, the purpose, the FR IDs, authentication, and the success status. Follow [api-design.md](../reference/api-design.md).
2. **Contract.** Write the OpenAPI for the endpoints in `docs/api/openapi.yaml`:
   - path and query parameters, request and response schemas, with examples;
   - every error status and its `code`;
   - pagination, `ETag`/`If-Match`, `Idempotency-Key` where they apply;
   - the security requirement.

   Share it with the client teams for review; it's frozen at G3.
3. **Validation rules.** Per request field: required, type, length, format, range, allowed values; and the business rules the service checks (uniqueness, state transitions, limits per user).
4. **Authorisation matrix.** Per endpoint and role: allowed or not, and the object-level rule (e.g. "owner only; others get 404"). These rows become route tests.
5. **Domain and services.** Models, value classes, `DomainError` cases, the service methods with their Kotlin signatures, and the transaction boundary of each (what must be atomic). Write signatures, not prose.
6. **Persistence.**
   - Tables, columns, types, constraints and indexes, as the Flyway migration SQL.
   - The queries each endpoint runs, and the index that serves each one.
   - The migration plan: expand-only in this release? Backfill? Contract in a later release?
   - Optimistic locking, idempotency records and outbox rows, if used.
7. **Events and integrations.** Events published (name in the past tense, payload, version, ordering key) through the outbox; events consumed and their deduplication; outbound calls with their timeouts, retries and failure behaviour.
8. **Caching and limits.** What is cached and how it's invalidated; rate limits, page sizes and payload limits specific to the feature.
9. **Observability.** Log events (with no personal data), business metrics, any new SLO or alert, and the audit-log events.
10. **Test cases.** Integration (`IT-`) and contract (`CT-`) cases, each traced to an FR: the route matrix (401, 400, 404 for others' resources, success, 409/412/428), repository queries, migrations, outbound adapters. Unit tests are written with the code in Phase 4.
11. **PR slice plan.** Split the work into small, reviewable PRs that follow the [build order](4-implementation.md#feature-build-order). Each PR has a one-line goal and stays at or below ~400 changed lines. A migration gets its own PR when it must deploy before the code that uses it.
12. **Review.** Walk through each design with the tech lead and another backend developer; the client team reviews the contract; security reviews the authorisation matrix; QA reviews the test cases.

## Exit checklist (G3)
- [ ] Every in-scope FR is covered by a feature design
- [ ] The OpenAPI contract for every endpoint is complete, reviewed by the client team, and frozen
- [ ] Validation rules and the authorisation matrix (including object-level rules) defined for every endpoint
- [ ] Service signatures, transaction boundaries and `DomainError` cases written in Kotlin
- [ ] Migration SQL, indexes per query, and the expand/contract plan written
- [ ] Events, outbound calls, timeouts and retries specified
- [ ] `IT-` and `CT-` test cases traced to FRs; RTM updated
- [ ] PR slice plan agreed; estimates fit the schedule
- [ ] Designs reviewed and approved; baseline tagged

## Pitfalls
- **Designing only the success response.** Most of an API's behaviour is in its errors, limits and edge cases.
- **Payloads shaped like tables** instead of like what clients need, which forces chatty clients or over-fetching.
- **Authorisation left to the implementation.** If the design doesn't say who may touch which object, the code won't check it.
- **A schema change without a migration plan,** or one that breaks the running version during the rollout.
- **Queries without an index decision,** found slow only under production data.
- **One giant PR per feature,** which nobody can review well.
