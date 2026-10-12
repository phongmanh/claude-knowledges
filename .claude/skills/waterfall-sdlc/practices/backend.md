# Backend best practices (APIs, data, infrastructure; any stack)

Engineering practices for services, APIs, data and infrastructure, grouped by quality attribute.

- **Targets and verification:** [quality-attributes.md](quality-attributes.md).
- **Lifecycle:**
  - design decisions: [Phase 2](../phases/2-system-design.md) and [Phase 3](../phases/3-detailed-design.md);
  - coding: [Phase 4](../phases/4-implementation.md);
  - tests: [Phase 5](../phases/5-testing.md);
  - release: [Phase 6](../phases/6-deployment.md).

## Architecture & maintainability
- **Start with a modular monolith.**
  - Align modules with business domains (bounded contexts).
  - Give each module its own data and a small public interface, and enforce the boundaries with automated dependency checks.
  - Extract a service only for a concrete driver: independent scaling, a different deployment cadence, team ownership, or isolation.
- **Hexagonal / clean architecture.** Domain logic sits at the centre, free of frameworks, databases and transport, with adapters at the edges. This keeps the core testable and the infrastructure replaceable.
- **API-first.** The contract (OpenAPI, AsyncAPI or protobuf) is the source of truth. Server stubs, clients, docs and mocks are generated from it or validated against it.
- **Twelve-Factor principles:**
  - config in the environment;
  - stateless processes;
  - backing services treated as attached resources;
  - dev/prod parity;
  - logs as event streams;
  - disposable processes.
- **Handle cross-cutting concerns one way**, through shared middleware: validation, errors, logging, authentication and authorisation.
- **No shared database between services.** Services integrate through APIs or events.
- **Automate checks and record decisions.** Run static analysis, formatting and architecture-conformance tests in CI. Write an ADR for each significant decision.

## API design
- **Resource-oriented design** with consistent naming and correct HTTP methods and status codes. If you chose GraphQL or gRPC, follow that style's conventions instead.
- **Errors** in a single format, RFC 9457 problem details, with stable, documented error codes. Never leak stack traces.
- **Pagination** on every collection, cursor-based for large or changing sets, with a maximum page size. Use consistent filtering and sorting.
- **Idempotency keys** on non-idempotent operations that clients may retry, such as creating orders or payments.
- **Concurrency and caching.** Use `ETag` with conditional requests: `If-Match` to prevent lost updates, `If-None-Match` for caching.
- **Versioning:**
  - Within a version, make only additive, backward-compatible changes.
  - A breaking change gets a new version, a deprecation period, and `Deprecation`/`Sunset` headers.
  - Keep supporting the oldest mobile app version that is still allowed.
- **Long-running operations** return `202 Accepted` plus a status resource (or use callbacks), rather than holding connections open.
- **Webhooks:**
  - Sign the payloads (e.g. with HMAC), and add timestamps to prevent replay.
  - Retry delivery with backoff, and make receivers idempotent.
  - Provide a way to replay events.
- **Contract hygiene:**
  - Validate requests and responses against the contract.
  - Publish rate-limit information in response headers.
  - Generate the documentation from the contract.

## Data management
- **Choose stores by access pattern.** Relational is the default for transactional data. Add another store (document, key-value, search, time-series, object) only for a stated need.
- **Schema:**
  - Enforce integrity with constraints in the database, not only in code: primary and foreign keys, unique, not-null, check.
  - Store money as a decimal plus a currency.
  - Store timestamps in UTC.
- **Indexes:** design them from real query patterns, verify them with execution plans on realistic volumes, and remove unused ones.
- **Migrations:**
  - Version and automate them, and review each one.
  - Achieve zero downtime with **expand → migrate → contract**.
  - Test every migration forwards and backwards on production-like data.
- **Transactions:** keep them short and choose isolation levels deliberately. Use optimistic locking (a version column) for concurrent edits.
- **Query hygiene:** no N+1 queries and no unbounded queries. Size connection pools from the capacity model.
- **Caching:**
  - Use cache-aside with TTLs and explicit invalidation.
  - Protect against stampedes with request coalescing or early refresh.
  - Never cache per-user data under a shared key.
- **Read replicas:** use them for read-heavy load, allowing for replication lag. Guarantee read-your-writes where it matters.
- **Lifecycle:** run archival and retention purges. Align soft vs. hard deletes with privacy erasure requirements.
- **Backups:**
  - Automated and encrypted.
  - Copied to another region or account.
  - Point-in-time recovery where the RPO needs it.
  - **Restore-tested regularly.**
- **External IDs:** make them non-sequential (UUID or ULID) to prevent enumeration.

## Testability
- **Unit tests:** test pure domain logic in isolation, with injected clocks and ID generators.
- **Integration tests:** run against real dependencies (databases, queues, caches) started in ephemeral containers.
- **Consumer-driven contract tests** between services, and with the mobile and web clients.
- **API tests:** generate them from the contract or validate them against it.
- **Migration tests:** run them up and down on realistic data.
- **Idempotency and concurrency tests:** duplicate messages, parallel updates.
- **Load-test scripts:** version them with the code.
- **Ephemeral environments:** one per PR where feasible.

## Performance
- **Latency budgets per endpoint.** Measure p95/p99, not averages.
- **Avoid sequential chains of remote calls.** Parallelise or aggregate them, or move the work off the request path.
- **Efficient payloads:** compression, field selection, pagination and efficient serialisation.
- **Connection reuse:** keep-alive and pooling. Tune timeouts to the latency budget.
- **Precompute expensive aggregates**, and cache hot reads.
- **Profile under realistic load** before optimising anything.

## Scalability
- **Stateless services.** Keep session state in a shared store or in tokens. Scale horizontally behind load balancers with health checks.
- **Autoscale on meaningful signals.** Use latency, queue depth and concurrency, not CPU alone. Set minimums so some capacity stays warm.
- **Asynchronous processing:**
  - Use queues or streams for slow, spiky or retryable work.
  - Under overload, apply **backpressure** and **load shedding**: reject early with 429/503 rather than collapse.
- **Partition or shard only when measurements demand it.** Choose keys that would allow it later anyway. Avoid hot keys, hot rows and global locks.
- **Reduce load per request.** Add bulk/batch endpoints to cut chattiness, and put a CDN and caching in front of read-heavy endpoints.
- **Multi-tenancy:**
  - Choose the isolation model deliberately: a shared schema with tenant ID plus row-level security, a schema per tenant, or a database per tenant.
  - Set per-tenant quotas to stop noisy neighbours.

## Reliability
- **Timeouts on every network call and query.** A call without a timeout can hang a thread forever.
- **Retries** only for transient failures of idempotent operations, with exponential backoff, jitter and a retry budget, so they can't turn into a retry storm.
- **Circuit breakers** stop calls to a failing dependency. **Bulkheads** (a separate pool per dependency) stop one slow dependency from exhausting everything.
- **Graceful degradation.** Serve cached or partial results when a non-critical dependency fails.
- **Assume at-least-once delivery.** Idempotent consumers deduplicate by message ID.
- **Consistency across stores and services:**
  - Use a **transactional outbox** to update the database and publish an event atomically.
  - Use **sagas** with compensating actions instead of distributed transactions.
- **Dead-letter queues**, with alerts and safe replay tooling.
- **Health checks:**
  - **Liveness:** the process is alive.
  - **Readiness:** the service can take traffic. Check critical dependencies carefully here, to avoid cascading restarts.
  - **Startup probes** for services that start slowly.
- **Graceful shutdown.** Stop accepting new work, finish or hand back in-flight work, then close connections.
- **Redundancy and DR.** Run across availability zones. Have a DR plan for the chosen tier, with the RPO/RTO proven by drills.
- **Scheduled jobs** are idempotent and locked, so they never run twice at the same time.

## Security
Follow the ASVS level chosen in Phase 1, the OWASP Top 10 and the OWASP API Security Top 10.

- **Authentication:**
  - Use standard protocols (OAuth 2.x / OpenID Connect) through a central identity provider.
  - Require MFA for privileged users.
  - Validate each token's signature, issuer, audience and expiry. Keep tokens short-lived.
- **Authorisation on every request, server-side:**
  - **Object level:** the caller may access *this* resource (prevents BOLA/IDOR).
  - **Function level:** the caller's role may perform *this* operation (prevents BFLA).
  - **Property level:** explicit request and response models, so there's no mass assignment and no over-exposed fields.
- **Deny by default.** Grant least privilege to users, services and database accounts.
- **Input:**
  - Validate it against schemas (type, length, format, range, allow-lists).
  - Use parameterised queries only.
  - Encode output for its context.
- **SSRF:** keep an allow-list of outbound destinations for user-supplied URLs. Block internal address ranges and cloud metadata endpoints.
- **File uploads:**
  - Limit size and type, and check the content.
  - Scan for malware.
  - Store files outside the web root, under generated names.
- **Abuse protection.** Rate limits and anti-automation on login, sign-up, password reset, OTP and other sensitive business flows.
- **Secrets** live in a secret manager, are injected at runtime, and are rotated. Never put them in code, images, logs or tickets.
- **Encryption:**
  - TLS 1.2+ externally (prefer 1.3), and mTLS between services where warranted.
  - Encryption at rest with managed keys.
  - Envelope or field-level encryption for highly sensitive data.
- **Passwords** are hashed with a slow, salted algorithm, per OWASP guidance. Argon2id is preferred; scrypt or bcrypt are acceptable.
- **Headers and CORS.** Send security headers on responses, and restrict CORS to an allow-list of origins.
- **Network:** private subnets for data stores, no public database endpoints, least-privilege network rules.
- **Audit logs** record security-relevant events (who, what, when, from where). They're tamper-evident and retained per policy.
- **Supply chain:** minimal, non-root container images; image and dependency scanning; signed artifacts and an SBOM.
- **Inventory.** Every API and version is documented and has an owner, so there are no forgotten "shadow" or "zombie" endpoints.
- **Third-party APIs.** Treat their responses as untrusted input: validate them, time them out, and limit how much you trust them.

## Privacy
- **Minimise data.** Keep the data classification and PII inventory current, and collect only what the requirements need.
- **Protect sensitive data.** Use field-level encryption or tokenisation, and pseudonymised IDs in analytics.
- **Redact PII and secrets in logs and traces.** Do it in the logging layer rather than relying on developer discipline.
- **Data residency** is enforced through deployment and storage configuration.
- **Data subjects:**
  - Run retention and deletion jobs automatically.
  - Provide processes (and endpoints) for data-subject access, export and erasure.
  - Keep consent records.
- **Compliance controls** are mapped to GDPR, HIPAA, PCI-DSS and SOC 2. Reduce scope where you can; for example, tokenised card data never touches your servers.

## Accessibility & UX
The backend shapes the client experience too:
- **Error responses** carry stable codes and field-level details, so clients can show specific, accessible messages.
- **Localised content and formats** are supported via `Accept-Language` wherever the server produces text (emails, notifications, PDFs).
- **Generated documents and emails** meet basic accessibility: structure, alt text, contrast.

## Internationalisation
- **Encoding:** use UTF-8 end to end (APIs, databases, files), with Unicode-aware validation, sorting and search.
- **Time:**
  - Store timestamps in UTC.
  - Return ISO 8601 timestamps with offsets.
  - Handle DST in scheduling.
- **Money:** store currency with ISO 4217 codes and decimal amounts. Do locale-aware formatting at the edge, never in stored data.

## Observability
- **Structured logs** (e.g. JSON), with a clear level policy and consistent fields:
  - timestamp, level, event name;
  - service, version, environment;
  - trace/correlation ID;
  - user/tenant ID, pseudonymised.
- **Metrics:**
  - RED (rate, errors, duration) per endpoint and per consumer.
  - USE (utilisation, saturation, errors) per resource.
  - Business metrics: orders, sign-ups, payments.
- **Distributed tracing** with OpenTelemetry, propagating context across services **and queues**.
- **SLOs with burn-rate alerts.** Every alert is actionable and linked to a runbook.
- **Dashboards** for each service and each critical journey.
- **Audit logs** are kept separate and immutable.
- **Retention and sampling** keep logging costs under control.

## Async & integration
- **Message and event contracts** are versioned (in schema files or a registry), with explicit rules for backward and forward compatibility.
- **Event names** are in the past tense and describe facts (`OrderPlaced`). Events carry IDs and essential data.
- **Ordering guarantees** only where needed, by partitioning on the entity key.
- **Poison messages** go to dead-letter queues. Replay is safe because consumers are idempotent.
- **Third-party APIs:**
  - Wrap them in anti-corruption layers.
  - Respect their rate limits.
  - Use their sandboxes for tests.

## Delivery & release
- **Infrastructure as code for everything.** Review it like application code and scan it for misconfiguration. No manual console changes.
- **Build once, promote everywhere.** The same immutable artifact (e.g. a container image) moves from dev to test to staging to production.
- **Environment parity.** Staging mirrors production's topology and configuration, scaled down, with the differences documented.
- **Zero-downtime deployments** (rolling, blue-green or canary), with automated rollback when SLOs regress. The pipeline runs migrations, and they're backward compatible.
- **Guardrails:**
  - Define resource requests, limits and autoscaling policies.
  - Use policy as code.
- **Cost and resilience:**
  - Tag costs by owner, service and environment, and set budget alerts.
  - Automate backups and DR.
- **Communicating changes:**
  - Publish release notes and an API changelog for consumers.
  - Tell client teams about deprecations well in advance.

## Compatibility
- **Backward compatibility** with every client version that is still supported, especially mobile apps.
- **Tolerant reader.** Ignore unknown fields, and never make a new field required for old clients.
- **Tests and metrics.** Run contract tests against the oldest supported client. Track usage per API version to plan removals.
