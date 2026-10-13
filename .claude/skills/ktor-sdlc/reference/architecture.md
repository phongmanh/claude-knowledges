# Architecture reference

Hexagonal (ports and adapters) layering for a Ktor service: the domain sits at the centre, free of frameworks, and Ktor, Exposed and HTTP clients are adapters at the edges. The canonical code for each piece is in [code-patterns.md](code-patterns.md); the HTTP conventions are in [api-design.md](api-design.md).

## Layers
```
inbound adapter (routes, DTOs, validation) ──▶ application (services, ports) ──▶ domain (models, rules, errors)
                                                     ▲ implemented by
                              outbound adapters (Exposed repositories, HTTP clients, queues)
```
- **Domain is pure Kotlin.** Models, value classes, invariants and the `DomainError` hierarchy. No Ktor, Exposed, JDBC, Koin or kotlinx.serialization types. `kotlin.time` and `kotlin.uuid` are allowed.
- **Application services** hold the use cases.
  - One service per aggregate (`NoteService`); each public method is one use case.
  - A service owns the transaction boundary (`Transactor`) and the object-level authorisation check.
  - It depends on ports: the repository interfaces (declared next to the domain models), `Transactor`, `IdGenerator`, `Clock`, gateways such as `PushGateway`.
  - If the project's rules require one class per use case (e.g. `CreateNoteUseCase`), follow them. The boundaries stay the same.
- **Inbound adapters** are the routes.
  - A route parses and validates the input, calls **one** service method, and maps the result to a response DTO.
  - Routes hold no SQL and no business rules, and never touch a repository.
- **Outbound adapters** implement the ports: Exposed tables and `…RepositoryImpl`, HTTP clients behind gateway interfaces. Table objects and DTOs never leave their adapter.
- **Dependencies point inward.** Koin binds the implementations to the ports.

## Module layout
Choose one layout in a Phase 2 ADR.

**A. One module, packages by feature**, for most services:
```
src/main/kotlin/com/example/notes/
├── Application.kt          # main(), module(), configureApp()
├── config/                 # AppConfig: the typed configuration
├── di/                     # appModule: infrastructure bindings
├── core/
│   ├── domain/             # DomainError, Caller, Page
│   ├── application/        # Transactor, IdGenerator, AppDispatchers
│   ├── persistence/        # DataSource, ExposedTransactor, migrations, database health check
│   └── http/               # plugins: serialization, status pages, security, monitoring, routing
└── notes/                  # one package per feature
    ├── domain/  application/  persistence/  api/
    └── NotesModule.kt      # the feature's Koin module
src/main/resources/         # application.yaml, logback.xml, db/migration/V1__create_notes.sql
```

**B. Gradle modules**, for growing services:
```
app/                # Application.kt, plugins, Koin start, configuration; depends on every feature
feature/<name>/     # one bounded context: domain, application, persistence and api packages
core/domain/        # shared domain types (Caller, DomainError, Page)
core/persistence/   # Transactor, DataSource, Flyway
core/http/          # shared plugins, problem details
core/testing/       # fakes, TestTokens, TestDatabase
api-contract/       # optional: a KMP module of DTOs and @Resource classes shared with clients (ADR)
build-logic/        # convention plugins
```
- **Features never depend on each other.** They talk through application-layer interfaces or events.
- **Each feature owns its tables.** No feature reads another feature's tables.
- **Size rule.** Choose B if any of these hold; otherwise choose A:
  - more than ~5 bounded contexts;
  - more than ~3 developers, or 2+ teams;
  - build times already hurt;
  - parts of the service may become separate deployments.
- **Package by feature in A.** That keeps a later move to B mechanical.
- **One deployable by default.** Split into separate services only for a concrete driver: independent scaling, a different deployment cadence, team ownership, or fault isolation. Record the driver in an ADR.

## Shared contract module
When the client is a Kotlin Multiplatform app, an `api-contract` KMP module can hold the `@Serializable` DTOs and the `@Resource` classes. The server and the app's Ktor client (with its Resources plugin) then use the same types. Choose it in an ADR, because it couples the server's and the app's release trains.
- **Only the wire contract is shared,** never domain models or server-side rules.
- **The module is a public API.** Within an API version, changes are additive only, and the OpenAPI check still runs.
- **Old apps keep old DTOs.** Shared code doesn't remove the need for [backward compatibility](api-design.md#versioning-and-compatibility).

## Default stack
Always use the latest stable versions, declared in `gradle/libs.versions.toml`. A deviation needs an ADR.

| Concern | Default | Notes |
|---|---|---|
| Language and runtime | Kotlin (K2) on the current JDK LTS | Java only in legacy code |
| Build | Gradle Kotlin DSL, version catalog, the Ktor BOM, convention plugins in `build-logic` | The Ktor Gradle plugin (`io.ktor.plugin`) builds the fat JAR and the image |
| Server | Ktor with the Netty engine, started by `EngineMain` from `application.yaml` | CIO by ADR |
| Routing | Type-safe routes with the Resources plugin (`@Resource` classes) | Plain string routes for health and metrics |
| Serialization | kotlinx.serialization JSON through ContentNegotiation | One shared `Json` instance |
| DI | Koin (`koin-ktor`, `koin-logger-slf4j`) | Ktor's own DI plugin by ADR |
| Configuration | `application.yaml` with environment-variable substitution, loaded into one `@Serializable` `AppConfig` | No class reads the raw config |
| Database | PostgreSQL | Another store only for a stated access pattern |
| Data access | Exposed (JDBC, DSL API) behind repository interfaces; HikariCP pool | Exposed R2DBC or jOOQ by ADR |
| Migrations | Flyway SQL migrations in `db/migration/` | Flyway owns the schema; Exposed only maps it |
| Validation | The RequestValidation plugin for request shape; domain rules in services | |
| Errors | StatusPages → RFC 9457 `application/problem+json` | See [error model](#error-model) |
| Authentication | Authentication plugin with JWT (`ktor-server-auth-jwt`), verified against the identity provider's JWKS (OpenID Connect) | Sessions and CSRF only for browser clients |
| HTTP hardening | CORS (browsers only), DefaultHeaders, HSTS, XForwardedHeaders (behind a trusted proxy), RateLimit, RequestBodyLimit, Compression, ConditionalHeaders | See [security-privacy.md](security-privacy.md) |
| API documentation | The OpenAPI contract in the repo; the served document generated from the routes by the Ktor compiler plugin and compared with it in CI | Generation is experimental in Ktor 3.6: ADR |
| Outbound HTTP | Ktor client (CIO engine) with HttpTimeout and HttpRequestRetry, behind a gateway interface | One client per downstream service |
| Time and IDs | `kotlin.time.Instant` and an injected `Clock`; UUID v7 IDs from an injected `IdGenerator` (`Uuid.generateV7()`) | Time-ordered IDs make keyset pagination simple |
| Logging | SLF4J with Logback, JSON output (logstash-logback-encoder), CallLogging + CallId in the MDC | No PII |
| Metrics | MicrometerMetrics plugin with a Prometheus registry | |
| Tracing | OpenTelemetry (Java agent, or the Ktor instrumentation library) | Chosen in an ADR with the platform team |
| Testing | kotlin-test on JUnit, `testApplication` (ktor-server-test-host), Testcontainers PostgreSQL, fakes, Kover; k6 for load | MockK only where a fake can't work. See [testing.md](testing.md) |
| Static analysis | ktlint, detekt; dependency and image scanning in CI | |
| Packaging | An OCI image (Jib through the Ktor plugin, or a multi-stage `Dockerfile`), distroless or minimal JRE base, non-root | See [deployment-operations.md](deployment-operations.md) |

## Gradle conventions
- **One place for shared config.** The JVM toolchain, Kotlin compiler options, ktlint, detekt and Kover settings live only in convention plugins.
- **Ktor artifacts come from the Ktor BOM** (`platform(libs.ktor.bom)`), so they all have the same version. The Ktor Gradle plugin's version matches it.
- **The application entry point** is the project's own `main`, which calls `EngineMain.main(args)`; `application.yaml` names the module function.
- **Opt-ins are explicit.** Use `@OptIn` where an experimental API is used (e.g. `Uuid.generateV7()`), and record experimental Ktor APIs in an ADR.
- **Dependency scope.** `implementation` by default; `api` only when a type is part of a module's public API.
- **Visibility.** `internal` unless another module needs the declaration.

## Configuration
- **Every setting is in `application.yaml`**, with `${ENV_VAR:default}` substitution. A secret has **no default**, so the service refuses to start without it.
- **One typed `AppConfig`**, a `@Serializable` data class loaded once with `property<AppConfig>("app")` and passed to Koin. `init` blocks validate the values, so a bad config stops the start instead of failing later.
- **Secrets never reach logs.** A config class that holds a secret overrides `toString()`.
- **Environments differ only by environment variables** (Twelve-Factor). The same image runs everywhere.
- **Development mode is off in production.** `ktor.development` enables auto-reload and more detailed errors.

## Dependency injection (Koin)
- **Start Koin in `configureApp`**, the function that builds the whole application: `install(Koin) { slf4jLogger(); modules(appModule(config), notesModule) }`. `Application.module()`, the function `application.yaml` names, only loads the config and calls it.
- **Modules:**
  - `appModule(config)` for infrastructure: dispatchers, clock, IDs, `DataSource`, `Database`, `Transactor`, health checks, the meter registry, the `JwkProvider`, HTTP clients;
  - one module per feature for its repositories (`singleOf(::NoteRepositoryImpl) bind NoteRepository::class`) and services (`singleOf(::NoteService)`).
- **Singletons are stateless.** Services and repositories keep no per-request state.
- **Lifecycle.** Definitions that hold resources (`HikariDataSource`, `HttpClient`) close them in `onClose { it?.close() }`, which runs when the application stops.
- **Routes receive their dependencies as parameters,** resolved once in `configureRouting` (`noteRoutes(service = get())`), not with `by inject()` inside the route function:
  - the dependencies are visible in the signature;
  - a missing binding fails at startup, not on the first request;
  - a `by inject()` delegate used inside a plain `get("/path")` handler crashed the Ktor OpenAPI compiler plugin (Ktor 3.6.0 with Kotlin 2.4.21).
- **Tests add modules.** `configureApp(config, overrides)` loads the overrides last, and later definitions replace earlier ones.
- **Check the graph in a test.** Koin resolves at runtime, so a JVM test resolves everything the routes need from the production modules ([testing.md](testing.md#di-graph)).

## Error model
- **The domain defines a sealed `DomainError`** (`NotFound`, `Forbidden`, `Conflict`, `PreconditionFailed`, `Invalid`) with a stable `code`. It extends `RuntimeException` without a stack trace: it's an expected outcome, not a bug.
- **Services throw it; nothing in between catches it.** An exception thrown inside `Transactor.inTransaction` rolls the transaction back.
- **StatusPages is the only place that maps errors to HTTP.** Each `DomainError` becomes a status and a problem+json body ([api-design.md](api-design.md#errors)). Any other exception becomes a 500 `internal_error`, logged with the call ID; the client gets no details.
- **Outbound adapters translate library exceptions** (`ResponseException`, `IOException`) at their boundary, into a result or a domain error. Ktor-client and JDBC exceptions don't travel up into services.
- **`CancellationException` is never swallowed.** Catch specific exceptions, not `Exception` or `Throwable`, in code that suspends.

## Threading and coroutines
- **Never block a request coroutine.** JDBC is blocking, so all database work runs inside `Transactor.inTransaction`, which switches to the injected IO dispatcher.
- **Repository functions are plain blocking functions.** They run only inside a transaction, because Exposed binds the transaction to the thread, and they never suspend.
- **Pool sizes match.** The Hikari pool is smaller than the IO dispatcher's parallelism (64 threads, or the number of cores if higher). Requests wait at most `connectionTimeout` for a connection, then fail fast.
- **CPU-heavy work** runs in `withContext(dispatchers.default)`.
- **Timeouts come from the drivers.** `withTimeout` can't interrupt a blocking JDBC call, so set the query timeout on the transaction and the HTTP timeouts on the client.
- **Background work:**
  - short work tied to the process: `application.launch { … }`, which is cancelled when the application stops;
  - work that must survive a restart: a queue or the transactional outbox ([performance-reliability.md](performance-reliability.md#reliability)).

  Never `GlobalScope`, never `runBlocking`.
