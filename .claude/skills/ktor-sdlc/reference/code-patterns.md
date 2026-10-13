# Code patterns

This is the canonical Kotlin for each concern in a Ktor service. When new code follows these shapes, every feature reads the same, and a reviewer can compare a PR against this one page. The project's own rules override it.

The example is a notes API (`/v1/notes`) in [module layout A](architecture.md#module-layout). The code was compiled and its tests run with Ktor 3.6, Kotlin 2.4, Exposed 1.5, Koin 4.2 and Flyway 13; when a newer version changes an API, follow the library and update this page. Imports are omitted, except the ones that are [easy to get wrong](#imports-that-are-easy-to-get-wrong).

## Kotlin style
- **Immutability:** `val` over `var`; read-only collection types in public APIs.
- **Null safety:** no `!!`. Use `?.`, `?:`, `checkNotNull(x) { "reason" }` or `requireNotNull(x) { "reason" }`.
- **Types:**
  - `data class` for models and DTOs; `@JvmInline value class` for IDs (`NoteId`, `UserId`);
  - `sealed class`/`sealed interface` for errors and outcomes;
  - a `when` over a sealed type lists every subtype, with no `else`.
- **Functions:** one job each, under ~30 lines. Use expression bodies when they fit on one line.
- **Named arguments** for booleans and for parameters of the same type.
- **No magic values:** `private const val` for limits, timeouts and sizes; configuration for anything that differs per environment.
- **Visibility:** `internal` by default in multi-module builds, `private` within files.
- **Comments** explain *why*, never *what*. KDoc only on public APIs that aren't obvious.

## Entry point and plugins
```kotlin
fun main(args: Array<String>) = EngineMain.main(args)

/** Entry point named in application.yaml (`ktor.application.modules`). */
fun Application.module() {
    configureApp(property<AppConfig>("app"))
}

/** Builds the whole application. Tests call it with a test [AppConfig] and Koin [overrides]. */
fun Application.configureApp(config: AppConfig, overrides: List<Module> = emptyList()) {
    install(Koin) {
        slf4jLogger()
        modules(appModule(config), notesModule)
        modules(overrides)
    }
    if (config.database.migrateOnStart) runMigrations(get())

    configureMonitoring(get())
    configureSerialization()
    configureStatusPages()
    configureHttp(config.http)
    configureSecurity(config.auth, get())
    configureValidation()
    configureRouting(config.http.serveApiDocs)
}
```
- **One `configureX()` extension per concern,** each in its own file under `core/http/`. `configureApp` reads like a table of contents.
- **Order:** monitoring first (so every call gets a call ID and is logged), then serialization, error handling, HTTP hardening, authentication, validation, and routing last.
- **No logic in `module()`.** It loads the configuration and delegates, so tests can build the same application with a different config.

`application.yaml`:
```yaml
ktor:
  deployment:
    port: ${PORT:8080}
    shutdownGracePeriod: 5000   # ms to stop taking new requests
    shutdownTimeout: 20000      # ms until the server stops, whatever is still running
  application:
    modules:
      - com.example.notes.ApplicationKt.module

app:
  database:
    url: ${DB_URL:jdbc:postgresql://localhost:5432/notes}
    user: ${DB_USER:notes}
    password: ${DB_PASSWORD}          # no default: the service refuses to start without it
    maxPoolSize: 10
    queryTimeoutSeconds: 5
    migrateOnStart: ${DB_MIGRATE_ON_START:false}
  auth:
    issuer: ${AUTH_ISSUER}
    audience: ${AUTH_AUDIENCE:notes-api}
    jwksUrl: ${AUTH_JWKS_URL}
  http:
    corsHosts: []
    maxBodyBytes: 1048576
    rateLimitPerMinute: 120
    serveApiDocs: ${SERVE_API_DOCS:false}
```

## Configuration
```kotlin
// Top level, not in a private companion: a private companion blocks the serializer lookup
// that getAs<DatabaseConfig>() does.
private const val MAX_POOL_SIZE = 50

/** The `app` section of application.yaml, loaded once at startup. Invalid values stop the start. */
@Serializable
data class AppConfig(
    val database: DatabaseConfig,
    val auth: AuthConfig,
    val http: HttpConfig,
)

@Serializable
data class DatabaseConfig(
    val url: String,
    val user: String,
    val password: String,
    val maxPoolSize: Int,
    val queryTimeoutSeconds: Int,
    val migrateOnStart: Boolean,
) {
    init {
        require(url.startsWith("jdbc:postgresql://")) { "app.database.url must be a PostgreSQL JDBC URL" }
        require(maxPoolSize in 1..MAX_POOL_SIZE) { "app.database.maxPoolSize must be in 1..$MAX_POOL_SIZE" }
    }

    // Keeps the password out of logs and error messages.
    override fun toString() = "DatabaseConfig(url=$url, user=$user, maxPoolSize=$maxPoolSize)"
}

@Serializable
data class AuthConfig(val issuer: String, val audience: String, val jwksUrl: String) {
    init {
        require(issuer.startsWith("https://")) { "app.auth.issuer must be an https URL" }
        require(jwksUrl.startsWith("https://")) { "app.auth.jwksUrl must be an https URL" }
    }
}

@Serializable
data class HttpConfig(
    val corsHosts: List<String>,
    val maxBodyBytes: Long,
    val rateLimitPerMinute: Int,
    val serveApiDocs: Boolean,
)
```

## Domain (pure Kotlin)
```kotlin
/**
 * Expected business failures. Services throw them; StatusPages maps each one to an HTTP status
 * and a problem+json body in one place. No stack trace: they are outcomes, not bugs.
 */
sealed class DomainError(val code: String, message: String) : RuntimeException(message, null, false, false) {
    class NotFound(resource: String, id: String) : DomainError("not_found", "$resource $id was not found")
    class Forbidden(action: String) : DomainError("forbidden", "You are not allowed to $action")
    class Conflict(detail: String) : DomainError("conflict", detail)
    class PreconditionFailed(detail: String) : DomainError("precondition_failed", detail)
    class Invalid(val reasons: List<String>) : DomainError("validation_failed", "The request is not valid")
}

@JvmInline
value class UserId(val value: String)

/** The authenticated user making the request, taken from the validated access token. */
data class Caller(val userId: UserId, val roles: Set<String>)

/** One page of a keyset-paginated list. */
data class Page<T>(val items: List<T>, val hasMore: Boolean)

@JvmInline
value class NoteId(val value: Uuid) // kotlin.uuid.Uuid

data class Note(
    val id: NoteId,
    val ownerId: UserId,
    val title: String,
    val body: String,
    val createdAt: Instant, // kotlin.time.Instant
    val updatedAt: Instant,
    val version: Long,
) {
    companion object {
        const val MAX_TITLE_LENGTH = 200
        const val MAX_BODY_LENGTH = 10_000
    }
}

data class NoteDraft(val title: String, val body: String)

/** Blocking. Call only inside `Transactor.inTransaction`. */
interface NoteRepository {
    fun findById(id: NoteId): Note?

    /** The owner's notes, newest first, strictly older than [after] when it is set. */
    fun findPage(owner: UserId, after: NoteId?, limit: Int): List<Note>

    fun insert(note: Note)

    /** Returns false when the stored version is no longer [expectedVersion]. */
    fun update(note: Note, expectedVersion: Long): Boolean

    fun delete(id: NoteId): Boolean
}
```
- The repository interface is a port, declared next to the model it stores. Its functions are blocking on purpose: they run inside a transaction that the service opens.
- Limits that both validation and the schema use (`MAX_TITLE_LENGTH`) are constants on the model, so they're defined once.

## Application services
```kotlin
/**
 * The transaction boundary, owned by services. Repository functions are blocking and run only
 * inside [inTransaction], which moves them off the request thread.
 */
interface Transactor {
    suspend fun <T> inTransaction(block: () -> T): T
}

fun interface IdGenerator {
    fun next(): Uuid
}

/** Injected so tests can replace them. Never hard-code `Dispatchers.IO` outside the DI module. */
data class AppDispatchers(val io: CoroutineDispatcher, val default: CoroutineDispatcher)

class NoteService(
    private val notes: NoteRepository,
    private val transactor: Transactor,
    private val clock: Clock,
    private val ids: IdGenerator,
) {
    suspend fun create(caller: Caller, draft: NoteDraft): Note {
        val now = clock.now()
        val note = Note(NoteId(ids.next()), caller.userId, draft.title, draft.body, now, now, version = 1)
        transactor.inTransaction { notes.insert(note) }
        return note
    }

    suspend fun get(caller: Caller, id: NoteId): Note =
        transactor.inTransaction { notes.findById(id) }.ownedBy(caller, id)

    suspend fun list(caller: Caller, after: NoteId?, limit: Int): Page<Note> {
        // One extra row tells whether another page exists.
        val rows = transactor.inTransaction { notes.findPage(caller.userId, after, limit + 1) }
        return Page(items = rows.take(limit), hasMore = rows.size > limit)
    }

    suspend fun update(caller: Caller, id: NoteId, expectedVersion: Long, draft: NoteDraft): Note =
        transactor.inTransaction {
            val current = notes.findById(id).ownedBy(caller, id)
            val updated = current.copy(
                title = draft.title,
                body = draft.body,
                updatedAt = clock.now(),
                version = current.version + 1,
            )
            if (current.version != expectedVersion || !notes.update(updated, expectedVersion)) {
                throw DomainError.PreconditionFailed("Note ${id.value} was changed by another request")
            }
            updated
        }

    suspend fun delete(caller: Caller, id: NoteId) {
        transactor.inTransaction {
            notes.findById(id).ownedBy(caller, id)
            notes.delete(id)
        }
    }

    // Another user's note answers 404, not 403, so callers can't probe which IDs exist.
    private fun Note?.ownedBy(caller: Caller, id: NoteId): Note =
        this?.takeIf { it.ownerId == caller.userId } ?: throw DomainError.NotFound("Note", id.value.toString())
}
```
- **Every method takes the `Caller`** and checks object-level access itself. A route can't forget it.
- **One transaction per use case.** Everything that must succeed or fail together (the change, an outbox event, an idempotency record) runs in one `inTransaction` block. A thrown `DomainError` rolls it back.
- **Time and IDs are injected,** so tests are deterministic. Never `Clock.System` or `Uuid.random()` inside logic.

## Persistence (Exposed + Flyway)
```kotlin
class ExposedTransactor(
    private val database: Database,
    private val dispatchers: AppDispatchers,
    private val queryTimeoutSeconds: Int,
) : Transactor {
    // JDBC blocks, so the transaction runs on the IO dispatcher. An exception thrown by the
    // block rolls the transaction back.
    override suspend fun <T> inTransaction(block: () -> T): T =
        withContext(dispatchers.io) {
            transaction(database) {
                queryTimeout = queryTimeoutSeconds
                block()
            }
        }
}

private const val CONNECTION_TIMEOUT_MS = 3_000L

fun createDataSource(config: DatabaseConfig): HikariDataSource =
    HikariDataSource(
        HikariConfig().apply {
            jdbcUrl = config.url
            username = config.user
            password = config.password
            maximumPoolSize = config.maxPoolSize
            connectionTimeout = CONNECTION_TIMEOUT_MS
            isAutoCommit = false
            // Start even when the database is down; the readiness probe reports it.
            initializationFailTimeout = -1
        },
    )

fun runMigrations(dataSource: DataSource) {
    Flyway.configure()
        .dataSource(dataSource)
        .locations("classpath:db/migration")
        .load()
        .migrate()
}

/** Entry point of the migration job that runs before each rollout. */
fun main() {
    val config = ApplicationConfig("migration.yaml").property("database").getAs<DatabaseConfig>()
    createDataSource(config).use(::runMigrations)
}
```

`src/main/resources/migration.yaml`:
```yaml
# Read by the migration job only. Ktor resolves every ${VAR} in a file when it loads it,
# so the job gets its own file and needs no settings except the database's.
database:
  url: ${DB_URL:jdbc:postgresql://localhost:5432/notes}
  user: ${DB_USER:notes}
  password: ${DB_PASSWORD}
  maxPoolSize: 1
  queryTimeoutSeconds: 300
  migrateOnStart: true
```

`src/main/resources/db/migration/V1__create_notes.sql`. Flyway owns the schema; never change a migration that has run anywhere, add a new one:
```sql
CREATE TABLE notes (
    id         UUID PRIMARY KEY,
    owner_id   VARCHAR(255) NOT NULL,
    title      VARCHAR(200) NOT NULL CHECK (length(trim(title)) > 0),
    body       TEXT         NOT NULL,
    created_at TIMESTAMPTZ  NOT NULL,
    updated_at TIMESTAMPTZ  NOT NULL,
    version    BIGINT       NOT NULL
);

-- Serves the keyset-paginated list: WHERE owner_id = ? AND id < ? ORDER BY id DESC.
CREATE INDEX notes_owner_id_id_idx ON notes (owner_id, id DESC);
```

```kotlin
/** Mirrors db/migration. Flyway owns the schema; this object only maps it. */
object NotesTable : Table("notes") {
    val id = uuid("id") // kotlin.uuid.Uuid
    val ownerId = varchar("owner_id", length = 255)
    val title = varchar("title", length = Note.MAX_TITLE_LENGTH)
    val body = text("body")
    val createdAt = timestamp("created_at") // exposed-kotlin-datetime: kotlin.time.Instant
    val updatedAt = timestamp("updated_at")
    val version = long("version")

    override val primaryKey = PrimaryKey(id)
}

class NoteRepositoryImpl : NoteRepository {
    override fun findById(id: NoteId): Note? =
        NotesTable.selectAll()
            .where { NotesTable.id eq id.value }
            .singleOrNull()
            ?.toNote()

    override fun findPage(owner: UserId, after: NoteId?, limit: Int): List<Note> {
        val query = NotesTable.selectAll().where { NotesTable.ownerId eq owner.value }
        if (after != null) query.andWhere { NotesTable.id less after.value }
        return query
            .orderBy(NotesTable.id, SortOrder.DESC)
            .limit(limit)
            .map { it.toNote() }
    }

    override fun insert(note: Note) {
        NotesTable.insert {
            it[id] = note.id.value
            it[ownerId] = note.ownerId.value
            it[title] = note.title
            it[body] = note.body
            it[createdAt] = note.createdAt
            it[updatedAt] = note.updatedAt
            it[version] = note.version
        }
    }

    override fun update(note: Note, expectedVersion: Long): Boolean =
        NotesTable.update({ (NotesTable.id eq note.id.value) and (NotesTable.version eq expectedVersion) }) {
            it[title] = note.title
            it[body] = note.body
            it[updatedAt] = note.updatedAt
            it[version] = note.version
        } == 1

    override fun delete(id: NoteId): Boolean =
        NotesTable.deleteWhere { NotesTable.id eq id.value } == 1
}

private fun ResultRow.toNote() =
    Note(
        id = NoteId(this[NotesTable.id]),
        ownerId = UserId(this[NotesTable.ownerId]),
        title = this[NotesTable.title],
        body = this[NotesTable.body],
        createdAt = this[NotesTable.createdAt],
        updatedAt = this[NotesTable.updatedAt],
        version = this[NotesTable.version],
    )
```
- **The Exposed DSL, not the DAO API.** Rows map to immutable domain models explicitly; no entity objects with hidden lazy loading.
- **`TIMESTAMPTZ` columns** with `timestamp()`: the round trip keeps the instant and microsecond precision, whatever the JVM time zone (checked against PostgreSQL in a +07:00 JVM). Run containers in UTC anyway.
- **Optimistic locking in SQL:** the `UPDATE … WHERE version = ?` changes zero rows when another request got there first.
- **The schema and the table objects can drift.** A test compares them ([testing.md](testing.md#schema-drift)).
- **Migrations run as a job before the rollout** (the `main` above, from the same image), not from every replica at startup. `migrateOnStart` is for local development.

## HTTP API
### Resources
```kotlin
const val DEFAULT_PAGE_SIZE = 20
const val MAX_PAGE_SIZE = 100

// Query parameters are nullable with no default: href() copies a parent's non-null
// parameters into every child URL it builds.
@Serializable
@Resource("/v1/notes")
class Notes(val cursor: String? = null, val limit: Int? = null) {
    @Serializable
    @Resource("{id}")
    class ById(val parent: Notes = Notes(), val id: String)
}
```
A default such as `limit: Int = 20` on the parent made `href(Notes.ById(id = …))` produce `/v1/notes/{id}?limit=20`. The route test that checks `Location` caught it.

### DTOs and mapping
```kotlin
@Serializable
data class NoteDraftRequest(val title: String, val body: String = "")

@Serializable
data class NoteResponse(
    val id: String,
    val title: String,
    val body: String,
    val createdAt: Instant, // serialized as ISO 8601
    val updatedAt: Instant,
    val version: Long,
)

@Serializable
data class NotePageResponse(val items: List<NoteResponse>, val nextCursor: String?)

fun NoteDraftRequest.toDraft() = NoteDraft(title = title.trim(), body = body)

fun Note.toResponse() = NoteResponse(id.value.toString(), title, body, createdAt, updatedAt, version)

fun Page<Note>.toResponse() =
    NotePageResponse(
        items = items.map { it.toResponse() },
        nextCursor = if (hasMore) items.lastOrNull()?.id?.let(NoteCursor::encode) else null,
    )

/** Strong ETag from the row version; clients send it back in If-Match. */
fun Note.etag() = "\"$version\""

/** The cursor is opaque to clients, so its encoding can change without breaking them. */
object NoteCursor {
    private val base64 = Base64.UrlSafe.withPadding(Base64.PaddingOption.ABSENT)

    fun encode(id: NoteId): String = base64.encode(id.value.toByteArray())

    fun decode(cursor: String): NoteId =
        try {
            NoteId(Uuid.fromByteArray(base64.decode(cursor)))
        } catch (e: IllegalArgumentException) {
            throw DomainError.Invalid(listOf("cursor: is not a valid cursor"))
        }
}

fun String.toNoteId(): NoteId =
    Uuid.parseOrNull(this)?.let(::NoteId) ?: throw DomainError.NotFound("Note", this)
```
- **Separate request and response DTOs.** The request has only what a client may set: no `id`, `ownerId`, `version` or timestamps.
- **A malformed ID is a 404,** the same as an unknown one.

### Validation
```kotlin
fun RequestValidationConfig.noteValidators() {
    validate<NoteDraftRequest> { request ->
        val reasons = buildList {
            if (request.title.isBlank()) add("title: must not be blank")
            if (request.title.length > Note.MAX_TITLE_LENGTH) {
                add("title: must be at most ${Note.MAX_TITLE_LENGTH} characters")
            }
            if (request.body.length > Note.MAX_BODY_LENGTH) {
                add("body: must be at most ${Note.MAX_BODY_LENGTH} characters")
            }
        }
        if (reasons.isEmpty()) ValidationResult.Valid else ValidationResult.Invalid(reasons)
    }
}

fun Application.configureValidation() {
    install(RequestValidation) {
        noteValidators()
    }
}
```
Each reason starts with the field name, so clients can show it next to the right input. Rules that need data (uniqueness, ownership, state) belong in the service, not here.

### Routes
```kotlin
fun Route.noteRoutes(service: NoteService) {
    get<Notes> { query ->
        val page = service.list(
            caller = call.caller(),
            after = query.cursor?.let(NoteCursor::decode),
            limit = (query.limit ?: DEFAULT_PAGE_SIZE).coerceIn(1, MAX_PAGE_SIZE),
        )
        call.respond(page.toResponse())
    }

    post<Notes> {
        val note = service.create(call.caller(), call.receive<NoteDraftRequest>().toDraft())
        call.response.header(HttpHeaders.Location, call.application.href(Notes.ById(id = note.id.value.toString())))
        call.response.header(HttpHeaders.ETag, note.etag())
        call.respond(HttpStatusCode.Created, note.toResponse())
    }

    get<Notes.ById> { route ->
        val note = service.get(call.caller(), route.id.toNoteId())
        call.response.header(HttpHeaders.ETag, note.etag())
        call.respond(note.toResponse())
    }

    put<Notes.ById> { route ->
        val expectedVersion = call.request.header(HttpHeaders.IfMatch)?.trim('"')?.toLongOrNull()
            ?: return@put call.respondProblem(
                HttpStatusCode.PreconditionRequired,
                code = "precondition_required",
                detail = "Send the note's ETag in If-Match",
            )
        val note = service.update(
            call.caller(),
            route.id.toNoteId(),
            expectedVersion,
            call.receive<NoteDraftRequest>().toDraft(),
        )
        call.response.header(HttpHeaders.ETag, note.etag())
        call.respond(note.toResponse())
    }

    delete<Notes.ById> { route ->
        service.delete(call.caller(), route.id.toNoteId())
        call.respond(HttpStatusCode.NoContent)
    }
}
```
- **A handler is parse → one service call → respond.** No `try`/`catch`: errors reach StatusPages.
- **The service comes in as a parameter** ([why](architecture.md#dependency-injection-koin)).

### Routing, health, metrics and API docs
```kotlin
private const val API_VERSION = "1.0"

/** Resolves each route group's dependencies from Koin once, at startup. */
fun Application.configureRouting(serveApiDocs: Boolean) {
    install(Resources)
    routing {
        healthRoutes(databaseHealth = get(), meterRegistry = get())
        if (serveApiDocs) apiDocsRoute()
        authenticate(JWT_AUTH) {
            rateLimit(API_RATE_LIMIT) {
                noteRoutes(service = get())
            }
        }
    }
}

// Built from the routes by the Ktor OpenAPI compiler plugin. CI diffs it against the contract approved at G3.
private fun Route.apiDocsRoute() {
    get("/openapi.json") {
        val doc = OpenApiDoc(info = OpenApiInfo(title = "Notes API", version = API_VERSION)) +
            call.application.routingRoot.descendants()
        call.respond(doc)
    }.hide()
}

private fun Route.healthRoutes(databaseHealth: DatabaseHealthCheck, meterRegistry: PrometheusMeterRegistry) {
    // Liveness: the process answers. Never checks dependencies, or a database outage restarts every pod.
    get("/health/live") { call.respond(HttpStatusCode.OK) }.hide()
    // Readiness: this instance can serve traffic now.
    get("/health/ready") {
        val status = if (databaseHealth.isHealthy()) HttpStatusCode.OK else HttpStatusCode.ServiceUnavailable
        call.respond(status)
    }.hide()
    // Scraped from inside the cluster; the ingress doesn't route /metrics.
    get("/metrics") { call.respondText(meterRegistry.scrape()) }.hide()
}

class DatabaseHealthCheck(
    private val database: Database,
    private val dispatchers: AppDispatchers,
) {
    suspend fun isHealthy(): Boolean =
        withContext(dispatchers.io) {
            try {
                transaction(database) {
                    queryTimeout = PING_TIMEOUT_SECONDS
                    exec("SELECT 1")
                }
                true
            } catch (e: SQLException) {
                log.warn("Database health check failed", e)
                false
            }
        }

    private companion object {
        const val PING_TIMEOUT_SECONDS = 2
        val log = LoggerFactory.getLogger(DatabaseHealthCheck::class.java)
    }
}
```
- **Everything under `authenticate` and `rateLimit` by default.** Only health, metrics and API docs are outside, and none of them return business data.
- **`hide()`** keeps infrastructure routes out of the OpenAPI document.
- Enable the OpenAPI compiler plugin in the build: `ktor { openApi { enabled = true } }` (needs the `ktor-server-routing-openapi` artifact).

## Errors (StatusPages)
```kotlin
private const val PROBLEM_TYPE_BASE = "https://api.example.com/problems/"

/** RFC 9457 problem details, with a stable `code` clients can switch on. */
@Serializable
data class Problem(
    val type: String,
    val title: String,
    val status: Int,
    val code: String,
    val detail: String? = null,
    val instance: String? = null,
    val errors: List<String> = emptyList(),
)

suspend fun ApplicationCall.respondProblem(
    status: HttpStatusCode,
    code: String,
    detail: String? = null,
    errors: List<String> = emptyList(),
) {
    val problem = Problem(
        type = PROBLEM_TYPE_BASE + code,
        title = status.description,
        status = status.value,
        code = code,
        detail = detail,
        instance = request.path(),
        errors = errors,
    )
    respondText(ApiJson.encodeToString(problem), ContentType.Application.ProblemJson, status)
}

fun Application.configureStatusPages() {
    install(StatusPages) {
        exception<DomainError> { call, error ->
            val errors = (error as? DomainError.Invalid)?.reasons.orEmpty()
            call.respondProblem(error.httpStatus(), error.code, error.message, errors)
        }
        exception<RequestValidationException> { call, error ->
            call.respondProblem(HttpStatusCode.BadRequest, "validation_failed", "The request is not valid", error.reasons)
        }
        exception<BadRequestException> { call, _ ->
            // The exception message names internal classes, so it is not sent to the client.
            call.respondProblem(HttpStatusCode.BadRequest, "malformed_request", "The request body or parameters are malformed")
        }
        exception<Throwable> { call, error ->
            call.application.log.error("Unhandled error on ${call.request.path()}", error)
            call.respondProblem(HttpStatusCode.InternalServerError, "internal_error")
        }
        status(
            HttpStatusCode.NotFound,
            HttpStatusCode.MethodNotAllowed,
            HttpStatusCode.UnsupportedMediaType,
            HttpStatusCode.PayloadTooLarge,
            HttpStatusCode.TooManyRequests,
        ) { call, status ->
            call.respondProblem(status, code = status.description.lowercase().replace(' ', '_'))
        }
    }
}

private fun DomainError.httpStatus() =
    when (this) {
        is DomainError.NotFound -> HttpStatusCode.NotFound
        is DomainError.Forbidden -> HttpStatusCode.Forbidden
        is DomainError.Conflict -> HttpStatusCode.Conflict
        is DomainError.PreconditionFailed -> HttpStatusCode.PreconditionFailed
        is DomainError.Invalid -> HttpStatusCode.BadRequest
    }
```
- **The body is written with `respondText` and the shared `ApiJson`,** so the content type is exactly `application/problem+json`, whatever the client's `Accept` header says.
- **`status(…)`** turns the empty 404, 405, 413, 415 and 429 responses that routing and plugins produce into problems too.

## Serialization
```kotlin
/** One JSON configuration for requests, responses and problem bodies. */
val ApiJson = Json {
    ignoreUnknownKeys = true // tolerant reader: newer clients may send fields this version doesn't know
    explicitNulls = false
}

fun Application.configureSerialization() {
    install(ContentNegotiation) { json(ApiJson) }
}
```

## Authentication
```kotlin
const val JWT_AUTH = "jwt"
private const val CLOCK_SKEW_SECONDS = 30L

fun Application.configureSecurity(config: AuthConfig, jwkProvider: JwkProvider) {
    install(Authentication) {
        jwt(JWT_AUTH) {
            // Signature from the identity provider's JWKS, plus issuer, audience and expiry.
            verifier(jwkProvider, config.issuer) {
                withAudience(config.audience)
                acceptLeeway(CLOCK_SKEW_SECONDS)
            }
            validate { credential -> credential.payload.subject?.let { JWTPrincipal(credential.payload) } }
            challenge { _, _ ->
                call.response.header(HttpHeaders.WWWAuthenticate, "Bearer")
                call.respondProblem(HttpStatusCode.Unauthorized, "unauthorized", "A valid bearer token is required")
            }
        }
    }
}

/** The caller of a route inside `authenticate(JWT_AUTH)`. */
fun ApplicationCall.caller(): Caller {
    val principal = checkNotNull(principal<JWTPrincipal>()) { "caller() used on a route without authenticate()" }
    val subject = checkNotNull(principal.subject) { "validate {} only accepts tokens with a subject" }
    val roles = principal.payload.getClaim("roles").asList(String::class.java).orEmpty().toSet()
    return Caller(UserId(subject), roles)
}
```
- **The service never issues tokens.** It verifies tokens from the identity provider (OpenID Connect): signature (keys from the JWKS, cached and rate-limited), issuer, audience, expiry.
- **Function-level checks** (roles) go in the service, next to the object-level check: `if ("admin" !in caller.roles) throw DomainError.Forbidden("delete other users' notes")`.

## HTTP hardening
```kotlin
val API_RATE_LIMIT = RateLimitName("api")
private const val MIN_COMPRESSED_BYTES = 1_024L

fun Application.configureHttp(config: HttpConfig) {
    // Only behind a proxy you control, which overwrites X-Forwarded-* on every request.
    install(XForwardedHeaders)
    install(DefaultHeaders) {
        header("X-Content-Type-Options", "nosniff")
        header("Referrer-Policy", "no-referrer")
    }
    install(HSTS) {
        maxAgeInSeconds = 365.days.inWholeSeconds
        includeSubDomains = true
    }
    install(Compression) {
        gzip { minimumSize(MIN_COMPRESSED_BYTES) }
    }
    install(ConditionalHeaders)
    install(RequestBodyLimit) {
        bodyLimit { config.maxBodyBytes }
    }
    // Browsers only: a mobile-only API leaves corsHosts empty and installs no CORS.
    if (config.corsHosts.isNotEmpty()) {
        install(CORS) {
            config.corsHosts.forEach { allowHost(it, schemes = listOf("https")) }
            allowHeader(HttpHeaders.Authorization)
            allowHeader(HttpHeaders.ContentType)
            allowHeader(HttpHeaders.IfMatch)
            exposeHeader(HttpHeaders.ETag)
            exposeHeader(HttpHeaders.Location)
            allowMethod(HttpMethod.Put)
            allowMethod(HttpMethod.Delete)
        }
    }
    install(RateLimit) {
        register(API_RATE_LIMIT) {
            rateLimiter(limit = config.rateLimitPerMinute, refillPeriod = 1.minutes)
            requestKey { call -> call.principal<JWTPrincipal>()?.subject ?: call.request.origin.remoteHost }
        }
    }
}
```
- **The RateLimit plugin counts per instance.** It protects each process; a global or per-tenant quota belongs in the API gateway or a shared store.
- **Never `anyHost()`** in CORS.

## Observability
```kotlin
private const val MAX_CALL_ID_LENGTH = 64

fun Application.configureMonitoring(meterRegistry: PrometheusMeterRegistry) {
    install(CallId) {
        retrieveFromHeader(HttpHeaders.XRequestId)
        generate { Uuid.random().toString() }
        verify { it.length in 1..MAX_CALL_ID_LENGTH }
        replyToHeader(HttpHeaders.XRequestId)
    }
    install(CallLogging) {
        callIdMdc("call_id")
        filter { call -> !call.request.path().startsWith("/health") }
        disableDefaultColors()
    }
    install(MicrometerMetrics) {
        registry = meterRegistry
    }
}
```
`logback.xml`: one JSON object per line, with the MDC (`call_id`) included:
```xml
<configuration>
    <appender name="JSON" class="ch.qos.logback.core.ConsoleAppender">
        <encoder class="net.logstash.logback.encoder.LogstashEncoder"/>
    </appender>
    <logger name="com.zaxxer.hikari" level="WARN"/>
    <root level="INFO">
        <appender-ref ref="JSON"/>
    </root>
</configuration>
```
- **Log events, not data:** `log.warn("Push service answered {}", status)`. Never log request bodies, tokens or personal data.
- **Placeholders, not string templates,** in log calls, so disabled levels cost nothing and log tools can group messages.

## Outbound HTTP
```kotlin
/** Port in the application layer. The HTTP adapter implements it. */
interface PushGateway {
    /** Best effort: returns false when the push service is unavailable. */
    suspend fun send(userId: UserId, message: String): Boolean
}

data class PushConfig(val baseUrl: String, val connectTimeoutMillis: Long, val requestTimeoutMillis: Long)

private val IDEMPOTENT_METHODS = setOf(HttpMethod.Get, HttpMethod.Head, HttpMethod.Put, HttpMethod.Delete)
private const val MAX_RETRIES = 2

/** One client per downstream service, created once and closed on shutdown. */
fun createPushClient(config: PushConfig): HttpClient =
    HttpClient(CIO) {
        expectSuccess = true
        install(HttpTimeout) {
            connectTimeoutMillis = config.connectTimeoutMillis
            requestTimeoutMillis = config.requestTimeoutMillis
        }
        install(HttpRequestRetry) {
            // Retry only what is safe to repeat; a POST is retried only with an Idempotency-Key.
            retryIf(MAX_RETRIES) { request, response ->
                request.method in IDEMPOTENT_METHODS && response.status.value >= 500
            }
            retryOnExceptionIf(MAX_RETRIES) { request, cause ->
                request.method in IDEMPOTENT_METHODS && cause is IOException
            }
            exponentialDelay()
        }
        install(ContentNegotiation) { json(ApiJson) }
        defaultRequest { url(config.baseUrl) }
    }

@Serializable
private data class PushRequest(val userId: String, val message: String)

class HttpPushGateway(private val client: HttpClient) : PushGateway {
    override suspend fun send(userId: UserId, message: String): Boolean =
        try {
            client.post("v1/pushes") {
                contentType(ContentType.Application.Json)
                setBody(PushRequest(userId.value, message))
            }
            true
        } catch (e: ResponseException) {
            log.warn("Push service answered {}", e.response.status)
            false
        } catch (e: IOException) {
            log.warn("Push service unreachable", e)
            false
        }

    private companion object {
        val log = LoggerFactory.getLogger(HttpPushGateway::class.java)
    }
}
```
- **Timeouts on every client,** derived from the endpoint's latency budget.
- **The adapter translates failures.** Here a push is best effort, so failures become `false`; a required dependency would throw a domain error that maps to 503 instead.
- **Bind it in Koin with `onClose`:** `single { createPushClient(config.push) } withOptions { onClose { it?.close() } }`.

## Dependency injection (Koin)
```kotlin
private const val JWKS_CACHE_SIZE = 10L
private const val JWKS_CACHE_HOURS = 24L
private const val JWKS_FETCHES_PER_MINUTE = 10L

@OptIn(ExperimentalUuidApi::class) // Uuid.generateV7()
fun appModule(config: AppConfig) = module {
    single { AppDispatchers(io = Dispatchers.IO, default = Dispatchers.Default) }
    single<Clock> { Clock.System }
    single<IdGenerator> { IdGenerator { Uuid.generateV7() } }

    single { createDataSource(config.database) } withOptions {
        bind<DataSource>()
        onClose { it?.close() }
    }
    single { Database.connect(get<DataSource>()) }
    single<Transactor> { ExposedTransactor(get(), get(), config.database.queryTimeoutSeconds) }
    single { DatabaseHealthCheck(get(), get()) }

    single { PrometheusMeterRegistry(PrometheusConfig.DEFAULT) }
    single<JwkProvider> {
        JwkProviderBuilder(URI(config.auth.jwksUrl).toURL())
            .cached(JWKS_CACHE_SIZE, JWKS_CACHE_HOURS, TimeUnit.HOURS)
            .rateLimited(JWKS_FETCHES_PER_MINUTE, 1, TimeUnit.MINUTES)
            .build()
    }
}

val notesModule = module {
    singleOf(::NoteRepositoryImpl) bind NoteRepository::class
    singleOf(::NoteService)
}
```
- **The DI module is the only place with `Dispatchers.IO`, `Clock.System` and real ID generation.**
- **Lazy by default:** the pool is created on first use, so tests that replace the repository never open a connection.

## Imports that are easy to get wrong
| Symbol | Import |
|---|---|
| Typed routes `get<Notes> {}`, `post`, `put`, `delete`, `href` | `io.ktor.server.resources.*` (not `io.ktor.server.routing.get`) |
| String routes `get("/health/live") {}` | `io.ktor.server.routing.get` |
| `@Resource` | `io.ktor.resources.Resource` |
| Koin lookup in `configureApp`/`configureRouting` | `org.koin.ktor.ext.get` |
| `property<AppConfig>("app")` | `io.ktor.server.config.property` |
| Exposed tables, operators (`eq`, `less`, `and`) | `org.jetbrains.exposed.v1.core.*` |
| Exposed JDBC queries and transactions (`selectAll`, `insert`, `transaction`, `Database`) | `org.jetbrains.exposed.v1.jdbc.*` |
| `timestamp()` for `kotlin.time.Instant` | `org.jetbrains.exposed.v1.datetime.timestamp` |
| Prometheus registry | `io.micrometer.prometheusmetrics.PrometheusMeterRegistry` (not the old `io.micrometer.prometheus`) |
| `OpenApiDoc`, `OpenApiInfo` / `hide()`, `plus` | `io.ktor.openapi.*` / `io.ktor.server.routing.openapi.*` |
| Client `IOException` | `kotlinx.io.IOException` |
| Testcontainers PostgreSQL (2.x) | `org.testcontainers.postgresql.PostgreSQLContainer` |

## Instead of … write …
| Instead of | Write |
|---|---|
| `environment.config.property("db.url").getString()` in a class | One `@Serializable` `AppConfig`, loaded once and injected |
| A secret with a default value in `application.yaml` | `${DB_PASSWORD}` with no default |
| A tool (e.g. the migration job) that loads `application.yaml` | Its own small config file: Ktor resolves every variable in a file when it loads it |
| A `private companion object` in a `@Serializable` class | Top-level `private const val`s: a private companion breaks `getAs<T>()` |
| Business logic or SQL in a route | A service method; a repository behind it |
| A repository or an Exposed table used in a route | A service call |
| `try`/`catch` in a route to build an error response | Throw a `DomainError`; StatusPages maps it |
| `call.respond(HttpStatusCode.BadRequest, "bad title")` | `RequestValidation`, or `DomainError.Invalid` → problem+json |
| Serializing a domain model or an Exposed row | A response DTO with only the fields the caller may see |
| `call.receive<Note>()` (mass assignment) | `call.receive<NoteDraftRequest>()` with only client-settable fields |
| 403 for another user's resource | 404, so IDs can't be probed |
| `transaction { }` called directly from a suspend function | `transactor.inTransaction { }` on the IO dispatcher |
| `newSuspendedTransaction`, or suspending inside a transaction | A blocking block inside `inTransaction`; do remote calls before or after it |
| `Dispatchers.IO`, `Clock.System`, `UUID.randomUUID()` in a class | Injected `AppDispatchers`, `Clock`, `IdGenerator` |
| `java.util.UUID`, `java.time.Instant` in new code | `kotlin.uuid.Uuid`, `kotlin.time.Instant` |
| Offset pagination over a large or changing table | A keyset cursor |
| Exposed `SchemaUtils.create` in production | A Flyway migration |
| Editing a migration that already ran | A new migration |
| `val service by inject<NoteService>()` in a route function | A `service: NoteService` parameter, resolved in `configureRouting` |
| `println`, `e.printStackTrace()` | An SLF4J logger with placeholders |
| `GlobalScope.launch`, `runBlocking`, `Thread.sleep` | `suspend` functions, `application.launch`, `delay`, a queue |
| `catch (e: Exception)` around suspend calls | Catch specific exceptions; never swallow `CancellationException` |
| An `HttpClient` created per request | One client per downstream service, closed with `onClose` |
| `HttpRequestRetry` with `retryOnServerErrors()` for every method | Retry only idempotent methods, or requests with an `Idempotency-Key` |
| `anyHost()` in CORS | An allow-list from configuration |
| `x!!` | `checkNotNull(x) { "…" }`, `?.`, `?:` |
