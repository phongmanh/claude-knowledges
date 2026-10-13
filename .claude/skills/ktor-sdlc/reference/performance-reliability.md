# Performance, reliability & observability reference

Measure on a production-like environment with **realistic data volume**, the **release image** and the production JVM settings. The budgets come from the NFRs: latency per endpoint as p95/p99 at a stated throughput, availability as an SLO.

## Performance
### Latency budget
- **Budget per endpoint,** split across its parts: e.g. p95 200 ms = 20 ms in the service + 2 queries at ≤ 30 ms + one downstream call at ≤ 100 ms.
- **p95 and p99, never averages.** Measure at the target throughput, not on an idle system.
- **No sequential chain of remote calls** on the request path. Call independent dependencies concurrently (`coroutineScope { async {…}; async {…} }`), or move the work to a queue.

### Database
- **No N+1 queries.** Load a page of rows with one query, and related data with a second `WHERE id IN (…)` query or a join, never one query per row.
- **No unbounded queries.** Every list has a limit; every report or export pages through the data.
- **Indexes come from the real queries** in the feature designs. Check them with `EXPLAIN (ANALYZE, BUFFERS)` on production-sized data, and drop unused ones.
- **Short transactions.** No remote call, no wait and no user think-time inside a transaction. Hold row locks for milliseconds.
- **Connection pool.** Size it from the capacity model, not by guessing: roughly the number of concurrent queries the database can serve well, divided across replicas. A bigger pool usually makes a saturated database slower. Watch pool wait time (Hikari metrics).
- **Statement timeouts** on every transaction (`queryTimeout`), plus a server-side `statement_timeout` for the service's database user as a backstop.

### HTTP
- **Netty engine** by default; keep the engine's default thread settings unless profiling shows a need.
- **Compression** for responses larger than ~1 KB.
- **Conditional requests** (`ETag`, 304) and `Cache-Control` for cacheable reads.
- **Pagination and field selection** keep payloads small; a mobile client doesn't need every field on a list screen.
- **One `HttpClient` per downstream service,** reused, so connections are pooled and kept alive.

### JVM
- **Container-aware memory:** `-XX:MaxRAMPercentage=75` (or similar) instead of a fixed `-Xmx`, so the heap follows the container limit.
- **Garbage collector:** the JVM's default (G1) unless measurements show otherwise; for very large heaps with tight latency, ZGC by ADR.
- **Profile before optimising,** with async-profiler or JFR on a realistic load test.

## Reliability
- **Timeouts on every network call and query.** A call without a timeout can hold a coroutine, a connection and a pool slot forever.
  - HTTP clients: connect, request and socket timeouts (`HttpTimeout`), derived from the budget.
  - Database: the pool's `connectionTimeout`, the transaction's `queryTimeout`.
  - Incoming requests: the ingress or load balancer's request timeout is longer than the service's own timeouts, so the service answers first.
- **Retries:**
  - only for transient failures (connection errors, 502/503/504, 429) of **idempotent** operations, or requests with an `Idempotency-Key`;
  - exponential backoff with jitter, and a small maximum (e.g. 2 retries), honouring `Retry-After`;
  - only at one layer, so retries don't multiply across services.
- **Circuit breakers and bulkheads** for dependencies that fail or slow down: stop calling a failing dependency for a while (e.g. Resilience4j's Kotlin module), and give each dependency its own limit (a `Semaphore` or its own client), so one slow dependency can't use up every request coroutine.
- **Graceful degradation.** When a non-critical dependency fails, serve without it (e.g. no avatar URLs) instead of failing the whole request.
- **Load shedding.** Under overload, reject early with 429 or 503 and `Retry-After` (rate limits, concurrency limits) rather than queueing until everything times out.
- **Idempotency** for retried creates: the `Idempotency-Key` record is written in the same transaction as the change ([api-design.md](api-design.md#idempotency)).
- **Transactional outbox** for events: write the event to an `outbox` table in the same transaction as the change; a relay publishes it and marks it sent. Never "write to the database, then publish" as two steps that can half-fail.
- **Consumers are idempotent.** Delivery is at least once, so consumers deduplicate by message ID. Poison messages go to a dead-letter queue with an alert and a replay tool.
- **Scheduled jobs** are idempotent and run once at a time across replicas: a PostgreSQL advisory lock (`pg_try_advisory_lock`) or a lock row, or a platform scheduler (e.g. a Kubernetes CronJob) that starts one instance.
- **Health checks:**
  - liveness (`/health/live`): the process answers; never checks dependencies;
  - readiness (`/health/ready`): this instance can serve traffic; checks the database with a short timeout;
  - a startup probe if start-up is slow, so liveness doesn't kill a starting instance.
- **Graceful shutdown.** On SIGTERM the platform stops sending traffic; Ktor stops accepting new requests (`shutdownGracePeriod`), finishes in-flight ones within `shutdownTimeout`, and Koin closes the pool and clients. The platform's termination grace period is longer than `shutdownTimeout`.
- **Redundancy.** At least two replicas across availability zones; a managed database with a standby in another zone; the RPO and RTO proven by a restore drill.

## Scalability
- **Stateless instances.** No session state or caches that must be consistent in memory; anything shared lives in the database, a cache service or tokens. Any replica can serve any request.
- **Scale out on meaningful signals:** request concurrency, latency or queue depth, not CPU alone. Keep a minimum number of warm replicas.
- **Know the bottleneck.** The capacity model (Phase 2) names it, usually the database. Read replicas, caching and query work come before more service replicas.
- **Caching:** cache-aside with a TTL and explicit invalidation, for reads that are hot and tolerate staleness. Never cache per-user data under a shared key. Protect against stampedes (request coalescing, early refresh).
- **Asynchronous work** for slow, spiky or retryable tasks: accept the request, queue the work, return `202`.
- **Partition or shard only when measurements demand it,** but choose keys (e.g. tenant ID) that would allow it later.
- **Multi-tenancy:** a tenant ID on every tenant-owned row and in every query (or PostgreSQL row-level security), and per-tenant quotas to stop noisy neighbours.

## Observability
- **Structured logs.** One JSON object per line (Logback + logstash-logback-encoder), with timestamp, level, logger, message, `call_id` from the MDC, service, version and environment. INFO for business events, WARN for handled failures, ERROR for what needs a human. No personal data.
- **Correlation.** The CallId plugin reads or creates `X-Request-ID`, returns it, and puts it in the MDC. Downstream calls carry the trace context (OpenTelemetry propagates it), or the request ID as a header. Clients (the mobile app) send their own request ID, so a user's report can be traced.
- **Metrics (RED and USE).**
  - Per endpoint: request rate, errors (by status class), duration histograms, from MicrometerMetrics.
  - Resources: JVM memory and GC, the Hikari pool (active, idle, pending, wait time), dispatcher and thread usage.
  - Business metrics: e.g. notes created, sign-ups, failed payments.
  - Scraped from `/metrics` inside the cluster only.
- **Tracing.** OpenTelemetry spans for incoming requests, database calls and outbound HTTP, with context propagated across services and queues. The Java agent instruments Ktor, JDBC and the clients without code changes; choose the agent or library instrumentation in an ADR.
- **SLOs and alerts.**
  - An SLO per critical journey (e.g. 99.9% of `GET /v1/notes` succeed in < 300 ms over 28 days).
  - Alerts on error-budget burn rate (fast and slow windows), not on single spikes.
  - Every alert is actionable and links to a runbook.
- **Dashboards** per service: traffic, errors, latency percentiles, saturation (pool, CPU, memory), and the deploy markers.
- **Audit logs** stay separate from these, as described in [security-privacy.md](security-privacy.md#logging-and-audit).
- **Cost control.** Sample traces, set log retention per level, and drop noisy debug logs in production.
