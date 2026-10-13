# Feature design: <Feature>

| FR IDs | Owner | Status | Contract | Client designs |
|---|---|---|---|---|
| FR-001, FR-002 | <developer> | Draft | `docs/api/openapi.yaml` (`/v1/notes`) | <links to the client screens that use it> |

## 1. Endpoints
| Endpoint | Purpose | FR | Auth | Success | Errors (status → `code`) |
|---|---|---|---|---|---|
| `GET /v1/notes` | The caller's notes, newest first, paginated | FR-001 | User token | 200 | 400 → `validation_failed` (bad cursor), 401 → `unauthorized` |
| `POST /v1/notes` | Create a note | FR-002 | User token | 201 + `Location`, `ETag` | 400 → `validation_failed`, 401 |
| `PUT /v1/notes/{id}` | Replace a note | FR-003 | User token | 200 + `ETag` | 400, 401, 404 → `not_found`, 412 → `precondition_failed`, 428 → `precondition_required` |

Contract: the paths above in `docs/api/openapi.yaml`, with request and response schemas and examples. Contract review by the client team: <name, date>.

## 2. Validation
| Field | Rules | Error reason |
|---|---|---|
| `title` | Required; not blank; ≤ 200 characters; trimmed | `title: must not be blank`, `title: must be at most 200 characters` |
| `body` | Optional; ≤ 10,000 characters | `body: must be at most 10000 characters` |
| `limit` (query) | 1–100; default 20; larger values clamped | — |
| `cursor` (query) | Opaque; from a previous response | `cursor: is not a valid cursor` |

Business rules checked by the service: <e.g. at most 1,000 notes per user → 409 `conflict`>

## 3. Authorisation
| Endpoint | User | Admin | Object-level rule | Test |
|---|---|---|---|---|
| `GET /v1/notes/{id}` | Owner only | Any note | Others get 404 | IT-004 |
| `PUT /v1/notes/{id}` | Owner only | No | Others get 404 | IT-006 |

## 4. Domain and services
```kotlin
data class Note(val id: NoteId, val ownerId: UserId, val title: String, val body: String,
                val createdAt: Instant, val updatedAt: Instant, val version: Long)

class NoteService(notes: NoteRepository, transactor: Transactor, clock: Clock, ids: IdGenerator) {
    suspend fun list(caller: Caller, after: NoteId?, limit: Int): Page<Note>
    suspend fun create(caller: Caller, draft: NoteDraft): Note
    suspend fun update(caller: Caller, id: NoteId, expectedVersion: Long, draft: NoteDraft): Note // PreconditionFailed
}
```
- Transaction boundaries: <one per method; `create` also writes the outbox row and the idempotency record>
- `DomainError` cases: <NotFound, PreconditionFailed, …>

## 5. Persistence
```sql
-- V3__create_notes.sql (expand-only)
CREATE TABLE notes ( … );
CREATE INDEX notes_owner_id_id_idx ON notes (owner_id, id DESC);
```
| Query | Used by | Index | Expected rows |
|---|---|---|---|
| `WHERE owner_id = ? AND id < ? ORDER BY id DESC LIMIT ?` | `GET /v1/notes` | `notes_owner_id_id_idx` | ≤ 101 |

- Migration plan: <expand-only in this release; backfill job: none; contract step: none / release <x>>
- Optimistic locking: `version` column; idempotency records: <table>; outbox rows: <events>

## 6. Events and integrations
| Event / call | Direction | Payload or endpoint | Delivery / timeout | Idempotency | If it fails |
|---|---|---|---|---|---|
| `NoteCreated` v1 | Published (outbox) | `{ noteId, ownerId, createdAt }` | At least once; ordered by `ownerId` | Consumers dedupe by event ID | Relay retries; DLQ after <n> |
| Push service | Outbound | `POST /v1/pushes` | <n> ms; no retry (POST) | — | Skipped and logged |

## 7. Caching and limits
- Caching: <none / what, TTL, invalidation>
- Limits: <page size, body size, per-user rate limit>

## 8. Observability
| Signal | Name | Fields / labels (no personal data) |
|---|---|---|
| Log | `note_created` | `call_id`, `note_id` |
| Metric | `notes_created_total` | — |
| Audit | — | — |
| Alert / SLO change | <none / …> | |

## 9. Test cases
| ID | Level | FR | Case |
|---|---|---|---|
| IT-001 | Integration | FR-002 | `POST /v1/notes` without a token → 401 problem |
| IT-002 | Integration | FR-002 | Blank title → 400 with `title: must not be blank` |
| IT-003 | Integration | FR-002 | Valid draft → 201 with `Location` and `ETag: "1"` |
| IT-004 | Integration | FR-001 | Another owner's note → 404 |
| IT-005 | Integration | FR-001 | Repository: page after a cursor returns older notes of that owner only (PostgreSQL) |
| CT-001 | Contract | FR-001, FR-002 | Generated OpenAPI matches the frozen contract |

## 10. PR slice plan
| # | PR | Layer | Est. changed lines |
|---|---|---|---|
| 1 | Migration + `NotesTable` + schema-drift test | Persistence | ~100 |
| 2 | Domain model, repository interface, `NoteRepositoryImpl` + Testcontainers tests | Domain, persistence | ~300 |
| 3 | `NoteService` + unit tests | Application | ~250 |
| 4 | Resources, DTOs, validation, routes, contract update + route tests | API | ~350 |
| 5 | Koin wiring, metrics, feature flag, runbook update | Wiring | ~100 |

## 11. Open questions
- <…>
