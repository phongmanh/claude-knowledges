# Testing reference

Most behaviour is tested in fast JVM tests with fakes. What only a real database or a real HTTP pipeline can prove (SQL, migrations, plugins, authentication, serialization) is tested against real PostgreSQL in Testcontainers and the real Ktor application in `testApplication`. The snippets below compile and pass with the versions named in [code-patterns.md](code-patterns.md).

## Pyramid
| Level | Share (e.g.) | Runs | Covers |
|---|---|---|---|
| Unit | ~60% | Every PR, no Docker | Services with fakes, domain rules, mappers, validators, cursor encoding |
| Integration | ~30% | Every PR, Docker for Testcontainers | Routes through the full plugin pipeline (`testApplication`), repositories and migrations on PostgreSQL, schema drift, the Koin graph |
| Contract | Every PR | No Docker | The OpenAPI document generated from the routes vs the frozen contract; consumer contract tests where a client publishes them |
| System and NFR | Per the test plan | Staging, release image | End to end, load and soak, resilience, security (DAST), backup restore |

## What to test in each layer
| Layer | Test | Test doubles |
|---|---|---|
| Domain and services | Each use case: the happy path, each `DomainError`, object-level access, edge cases (empty, limits, version conflicts) | `FakeNoteRepository`, `ImmediateTransactor`, `FixedClock`, `SequentialIds` |
| Routes | Per endpoint: 401 without or with a bad token, 400 for invalid input, 404 for another owner's resource, the success status, headers (`Location`, `ETag`) and body; 428/412 for conditional updates | The real application from `configureApp`, with fake repositories and test tokens |
| Persistence | Each repository query on real PostgreSQL: round trip of every column, filters, ordering, pagination, optimistic locking | Testcontainers; the production Flyway migrations |
| Migrations | Every migration applies to an empty database and to a copy of the previous schema with data; the Exposed tables match the schema | Testcontainers |
| Outbound adapters | Status and timeout handling, retries only for idempotent calls, mapping of responses | Ktor `MockEngine` |
| DI | The production Koin graph resolves everything the routes need | Real modules, no database connection |

## Conventions
- **Files.** One test class per class under test, `<ClassUnderTest>Test.kt`, in the same package.
- **Names** describe the behaviour with backticks: `` `update - stale version - throws PreconditionFailed`() ``.
- **kotlin-test assertions on JUnit** (`kotlin("test")` with `useJUnitPlatform()`): `@Test`, `@BeforeTest`, `assertEquals`, `assertFailsWith`.
- **Structure.** Arrange–Act–Assert, one behaviour per test, no logic (`if`, loops) in tests.
- **Fakes over mocks.** Fakes for repositories, the transactor, the clock and IDs live in a shared testing package (or `core/testing` in layout B). MockK only for what you can't fake.
- **Deterministic.**
  - Inject `Clock`, `IdGenerator` and `AppDispatchers`; use `runTest`.
  - Never `Thread.sleep`, the real network, or a shared external database.
- **Real PostgreSQL, never H2.** An in-memory substitute has a different dialect, types and locking, and hides real bugs.
- **Tests build the application with `configureApp(TestConfig.app, overrides)`.** They never load `application.yaml`, so they need no environment variables.
- **Coverage.** Kover enforces a floor (e.g. ≥ 80% of lines in services and domain). Coverage is a floor, not the goal.

## Snippets
### Fakes
```kotlin
/** Runs the block directly: the fakes need no transaction. */
object ImmediateTransactor : Transactor {
    override suspend fun <T> inTransaction(block: () -> T): T = block()
}

class FixedClock(var now: Instant = Instant.parse("2026-01-01T00:00:00Z")) : Clock {
    override fun now(): Instant = now
}

/** Increasing IDs, so "newest first" ordering matches insertion order like UUID v7 does. */
class SequentialIds : IdGenerator {
    private var next = 1L

    override fun next(): Uuid = Uuid.fromLongs(0, next++)
}

class FakeNoteRepository : NoteRepository {
    private val notes = mutableMapOf<NoteId, Note>()

    override fun findById(id: NoteId): Note? = notes[id]

    override fun findPage(owner: UserId, after: NoteId?, limit: Int): List<Note> =
        notes.values
            .filter { it.ownerId == owner && (after == null || it.id.value < after.value) }
            .sortedByDescending { it.id.value }
            .take(limit)

    override fun insert(note: Note) {
        notes[note.id] = note
    }

    override fun update(note: Note, expectedVersion: Long): Boolean {
        if (notes[note.id]?.version != expectedVersion) return false
        notes[note.id] = note
        return true
    }

    override fun delete(id: NoteId): Boolean = notes.remove(id) != null
}
```

### Service unit test
```kotlin
class NoteServiceTest {
    private val service = NoteService(FakeNoteRepository(), ImmediateTransactor, FixedClock(), SequentialIds())
    private val alice = Caller(UserId("alice"), roles = emptySet())
    private val bob = Caller(UserId("bob"), roles = emptySet())

    @Test
    fun `get - note of another owner - throws NotFound`() = runTest {
        val note = service.create(alice, NoteDraft("Groceries", "Milk"))

        assertFailsWith<DomainError.NotFound> { service.get(bob, note.id) }
    }

    @Test
    fun `update - stale version - throws PreconditionFailed`() = runTest {
        val note = service.create(alice, NoteDraft("Groceries", "Milk"))
        service.update(alice, note.id, expectedVersion = 1, NoteDraft("Groceries", "Milk, eggs"))

        assertFailsWith<DomainError.PreconditionFailed> {
            service.update(alice, note.id, expectedVersion = 1, NoteDraft("Groceries", "Bread"))
        }
    }

    @Test
    fun `list - more notes than the limit - returns the newest page and hasMore`() = runTest {
        val created = (1..3).map { service.create(alice, NoteDraft("Note $it", "")) }

        val page = service.list(alice, after = null, limit = 2)

        assertEquals(listOf(created[2].id, created[1].id), page.items.map { it.id })
        assertTrue(page.hasMore)
    }
}
```

### Test configuration and tokens
```kotlin
object TestConfig {
    val app = AppConfig(
        database = DatabaseConfig(
            url = "jdbc:postgresql://localhost:5432/unused",
            user = "test",
            password = "", // no test connects with this config
            maxPoolSize = 2,
            queryTimeoutSeconds = 5,
            migrateOnStart = false,
        ),
        auth = AuthConfig(
            issuer = "https://issuer.test",
            audience = "notes-api",
            jwksUrl = "https://issuer.test/.well-known/jwks.json",
        ),
        http = HttpConfig(corsHosts = emptyList(), maxBodyBytes = 64 * 1024, rateLimitPerMinute = 1_000, serveApiDocs = true),
    )
}

/** Signs access tokens with a test key, and serves that key as the JWKS. */
object TestTokens {
    private const val KEY_ID = "test-key"
    private val keyPair = KeyPairGenerator.getInstance("RSA").apply { initialize(2048) }.generateKeyPair()
    private val publicKey = keyPair.public as RSAPublicKey
    private val algorithm = Algorithm.RSA256(publicKey, keyPair.private as RSAPrivateKey)

    val jwkProvider = JwkProvider {
        Jwk.fromValues(
            mapOf(
                "kid" to KEY_ID,
                "kty" to "RSA",
                "alg" to "RS256",
                "use" to "sig",
                "n" to publicKey.modulus.toBase64Url(),
                "e" to publicKey.publicExponent.toBase64Url(),
            ),
        )
    }

    fun bearer(
        subject: String,
        issuer: String = TestConfig.app.auth.issuer,
        audience: String = TestConfig.app.auth.audience,
        expiresIn: Duration = 5.minutes,
    ): String {
        val token = JWT.create()
            .withKeyId(KEY_ID)
            .withIssuer(issuer)
            .withAudience(audience)
            .withSubject(subject)
            .withExpiresAt(Date(System.currentTimeMillis() + expiresIn.inWholeMilliseconds))
            .sign(algorithm)
        return "Bearer $token"
    }

    private fun BigInteger.toBase64Url(): String =
        Base64.getUrlEncoder().withoutPadding().encodeToString(toByteArray().dropWhile { it == 0.toByte() }.toByteArray())
}
```
The real verifier runs in tests: the signature is checked against the test JWKS, and wrong issuers, audiences or expired tokens are rejected exactly as in production.

### Route tests
```kotlin
class NoteRoutesTest {
    private fun ApplicationTestBuilder.notesApi(): HttpClient {
        application {
            configureApp(
                TestConfig.app,
                overrides = listOf(
                    module {
                        single<NoteRepository> { FakeNoteRepository() }
                        single<Transactor> { ImmediateTransactor }
                        single<JwkProvider> { TestTokens.jwkProvider }
                    },
                ),
            )
        }
        return createClient { install(ContentNegotiation) { json(ApiJson) } }
    }

    @Test
    fun `POST notes - no token - 401 problem`() = testApplication {
        val client = notesApi()

        val response = client.post("/v1/notes") {
            contentType(ContentType.Application.Json)
            setBody(NoteDraftRequest(title = "Groceries"))
        }

        assertEquals(HttpStatusCode.Unauthorized, response.status)
        assertEquals(ContentType.Application.ProblemJson, response.contentType()?.withoutParameters())
    }

    @Test
    fun `POST notes - token for another audience - 401`() = testApplication {
        val client = notesApi()

        val response = client.post("/v1/notes") {
            header(HttpHeaders.Authorization, TestTokens.bearer("alice", audience = "another-api"))
            contentType(ContentType.Application.Json)
            setBody(NoteDraftRequest(title = "Groceries"))
        }

        assertEquals(HttpStatusCode.Unauthorized, response.status)
    }

    @Test
    fun `POST notes - blank title - 400 with the field error`() = testApplication {
        val client = notesApi()

        val response = client.post("/v1/notes") {
            header(HttpHeaders.Authorization, TestTokens.bearer("alice"))
            contentType(ContentType.Application.Json)
            setBody(NoteDraftRequest(title = " "))
        }

        assertEquals(HttpStatusCode.BadRequest, response.status)
        assertEquals(listOf("title: must not be blank"), response.body<Problem>().errors)
    }

    @Test
    fun `POST notes - valid draft - 201 with Location and ETag`() = testApplication {
        val client = notesApi()

        val response = client.post("/v1/notes") {
            header(HttpHeaders.Authorization, TestTokens.bearer("alice"))
            contentType(ContentType.Application.Json)
            setBody(NoteDraftRequest(title = "Groceries", body = "Milk"))
        }

        assertEquals(HttpStatusCode.Created, response.status)
        val note = response.body<NoteResponse>()
        assertEquals("/v1/notes/${note.id}", response.headers[HttpHeaders.Location])
        assertEquals("\"1\"", response.headers[HttpHeaders.ETag])
    }

    @Test
    fun `GET note - note of another owner - 404`() = testApplication {
        val client = notesApi()
        val created = client.post("/v1/notes") {
            header(HttpHeaders.Authorization, TestTokens.bearer("alice"))
            contentType(ContentType.Application.Json)
            setBody(NoteDraftRequest(title = "Groceries"))
        }
        val location = assertNotNull(created.headers[HttpHeaders.Location])

        val response = client.get(location) { header(HttpHeaders.Authorization, TestTokens.bearer("bob")) }

        assertEquals(HttpStatusCode.NotFound, response.status)
    }

    @Test
    fun `PUT note - no If-Match - 428`() = testApplication {
        val client = notesApi()
        val created = client.post("/v1/notes") {
            header(HttpHeaders.Authorization, TestTokens.bearer("alice"))
            contentType(ContentType.Application.Json)
            setBody(NoteDraftRequest(title = "Groceries"))
        }
        val location = assertNotNull(created.headers[HttpHeaders.Location])

        val response = client.put(location) {
            header(HttpHeaders.Authorization, TestTokens.bearer("alice"))
            contentType(ContentType.Application.Json)
            setBody(NoteDraftRequest(title = "Groceries", body = "Eggs"))
        }

        assertEquals(HttpStatusCode.PreconditionRequired, response.status)
    }
}
```
- **Every endpoint gets the matrix:** 401, 400, 404 for someone else's resource, the success case, and 412/428 where it applies. This is where broken object-level authorisation (OWASP API1) is caught.
- **The full pipeline runs:** authentication, validation, StatusPages, serialization and the routes, exactly as `configureApp` installs them.

### Database
```kotlin
/**
 * One PostgreSQL per test JVM, migrated with the real Flyway scripts.
 * Never H2: dialect differences hide real bugs.
 */
object TestDatabase {
    private val container = PostgreSQLContainer("postgres:17-alpine").apply { start() }

    val dataSource = createDataSource(
        DatabaseConfig(
            url = container.jdbcUrl,
            user = container.username,
            password = container.password,
            maxPoolSize = 4,
            queryTimeoutSeconds = 5,
            migrateOnStart = true,
        ),
    ).also(::runMigrations)

    val database = Database.connect(dataSource)
    val transactor = ExposedTransactor(database, AppDispatchers(Dispatchers.IO, Dispatchers.Default), queryTimeoutSeconds = 5)
}

@OptIn(ExperimentalUuidApi::class)
class NoteRepositoryImplTest {
    private val repository = NoteRepositoryImpl()
    private val transactor = TestDatabase.transactor

    @BeforeTest
    fun cleanTable() = runTest {
        transactor.inTransaction { NotesTable.deleteAll() }
    }

    @Test
    fun `insert then findById - round-trips every column`() = runTest {
        val note = note(owner = "alice")

        transactor.inTransaction { repository.insert(note) }

        assertEquals(note, transactor.inTransaction { repository.findById(note.id) })
    }

    @Test
    fun `findPage - after a cursor - returns older notes of that owner, newest first`() = runTest {
        val notes = (1..4).map { note(owner = "alice") }
        transactor.inTransaction {
            notes.forEach(repository::insert)
            repository.insert(note(owner = "bob"))
        }

        val page = transactor.inTransaction { repository.findPage(UserId("alice"), after = notes[2].id, limit = 10) }

        assertEquals(listOf(notes[1].id, notes[0].id), page.map { it.id })
    }

    private fun note(owner: String) =
        Note(
            id = NoteId(Uuid.generateV7()),
            ownerId = UserId(owner),
            title = "Title",
            body = "Body",
            createdAt = Instant.parse("2026-03-01T10:15:30.123456Z"),
            updatedAt = Instant.parse("2026-03-01T10:15:30.123456Z"),
            version = 1,
        )
}
```
- **The container starts once per test JVM** (the `object`), and Testcontainers removes it afterwards. Tests clean their tables in `@BeforeTest`.
- **Pin the PostgreSQL major version** to the one production runs.
- **Microsecond timestamps** in test data prove the column keeps the precision.

### Schema drift
```kotlin
class SchemaDriftTest {
    // Flyway owns the schema and the Exposed tables only map it. This fails when they disagree.
    @Test
    fun `flyway schema - matches the Exposed tables`() = runTest {
        val statements = TestDatabase.transactor.inTransaction {
            MigrationUtils.statementsRequiredForDatabaseMigration(NotesTable, withLogs = false)
        }

        // Indexes and checks that exist only in SQL come back as DROP statements; they are fine.
        assertEquals(emptyList(), statements.filterNot { "DROP " in it })
    }
}
```
`MigrationUtils` is in the `exposed-migration-jdbc` artifact (test scope). A column added to a table object but missing from the migrations fails with the `ALTER TABLE … ADD …` it would need.

### DI graph
```kotlin
class KoinGraphTest {
    // Koin resolves at runtime, so a missing binding would otherwise fail in production.
    // The pool starts lazily, so no database is needed.
    @Test
    fun `production graph - resolves everything routes need`() {
        val koin = koinApplication { modules(appModule(TestConfig.app), notesModule) }.koin
        try {
            koin.get<NoteService>()
            koin.get<DatabaseHealthCheck>()
            koin.get<PrometheusMeterRegistry>()
            koin.get<JwkProvider>()
        } finally {
            koin.close()
        }
    }
}
```

### Contract check
```kotlin
class OpenApiSpecTest {
    // Writes the spec generated from the routes; CI runs oasdiff against the approved contract.
    @Test
    fun `openapi json - lists the notes routes - written for the contract check`() = testApplication {
        application { configureApp(TestConfig.app) }

        val response = client.get("/openapi.json")

        assertEquals(HttpStatusCode.OK, response.status)
        val spec = response.bodyAsText()
        assertTrue("/v1/notes" in spec)
        File("build/openapi").mkdirs()
        File("build/openapi/openapi.json").writeText(spec)
    }
}
```
CI then runs `oasdiff breaking docs/api/openapi.yaml build/openapi/openapi.json --fail-on ERR` ([OpenAPI workflow](api-design.md#openapi-workflow)). Where a client team publishes consumer contracts (e.g. Pact), verify them in the same stage.

### Load test (k6)
Versioned with the code, e.g. `load/list-notes.js`; the thresholds are the NFR targets:
```javascript
import http from 'k6/http';
import { check } from 'k6';

export const options = {
  scenarios: {
    list_notes: { executor: 'constant-arrival-rate', rate: 200, timeUnit: '1s', duration: '10m', preAllocatedVUs: 50 },
  },
  thresholds: {
    'http_req_duration{endpoint:list_notes}': ['p(95)<200', 'p(99)<500'], // NFR-PERF-01
    http_req_failed: ['rate<0.001'],
  },
};

export default function () {
  const res = http.get(`${__ENV.BASE_URL}/v1/notes?limit=20`, {
    headers: { Authorization: `Bearer ${__ENV.TOKEN}` },
    tags: { endpoint: 'list_notes' },
  });
  check(res, { 'status is 200': (r) => r.status === 200 });
}
```
- **Open model** (`constant-arrival-rate`): requests keep arriving when the service slows down, as they do in production.
- **Realistic data volume** in the target environment, or the indexes are never tested.
- A **soak** run (e.g. 2–4 h at expected peak) finds leaks and pool exhaustion that a 10-minute run doesn't.

## Gradle setup
```kotlin
dependencies {
    testImplementation(kotlin("test"))
    testImplementation(libs.ktor.server.test.host)
    testImplementation(libs.kotlinx.coroutines.test)
    testImplementation(libs.koin.test)
    testImplementation(libs.testcontainers.postgresql)
    testImplementation(libs.exposed.migration.jdbc)
}

tasks.test {
    useJUnitPlatform()
}
```
Integration tests need Docker on the CI runner. If they must run in a separate stage, move them to a JVM test suite (`integrationTest`) instead of skipping them.

## Commands
| Purpose | Command |
|---|---|
| All tests (Docker running for Testcontainers) | `./gradlew test` |
| One class | `./gradlew test --tests '*NoteRoutesTest'` |
| Coverage report and floor | `./gradlew koverHtmlReport koverVerify` |
| Contract check | `./gradlew test --tests '*OpenApiSpecTest'`, then `oasdiff breaking docs/api/openapi.yaml build/openapi/openapi.json --fail-on ERR` |
| Lint and static analysis | `./gradlew ktlintCheck detekt` |
| Run locally (PostgreSQL from `docker compose`) | `DB_PASSWORD=… AUTH_ISSUER=… AUTH_JWKS_URL=… DB_MIGRATE_ON_START=true ./gradlew run` |
| Fat JAR / image to the local Docker daemon | `./gradlew buildFatJar` / `./gradlew publishImageToLocalRegistry` |
| Load test | `k6 run -e BASE_URL=https://<staging> -e TOKEN=<token> load/list-notes.js` |
