# API design reference

HTTP and JSON conventions for every endpoint. Phase 3 writes each feature's contract with them; the [review checklist](review-checklist.md) checks the code against them. The code for each convention is in [code-patterns.md](code-patterns.md).

## Resources and methods
- **Nouns, plural, kebab-case:** `/v1/notes`, `/v1/notes/{id}`, `/v1/shared-notes`. Nest at most one level (`/v1/notes/{id}/attachments`).
- **Methods mean what HTTP says:**

  | Method | Use | Success | Idempotent |
  |---|---|---|---|
  | `GET` | Read a resource or a page of a collection | 200 | Yes |
  | `POST` | Create in a collection; an action that isn't CRUD (`/v1/notes/{id}/archive`) | 201 + `Location`, or 200 / 202 | No (yes with an `Idempotency-Key`) |
  | `PUT` | Replace a resource the client already has | 200 (or 204) | Yes |
  | `PATCH` | Partial update; only when clients really need it (JSON Merge Patch) | 200 | No |
  | `DELETE` | Remove | 204 | Yes |
- **Status codes clients can rely on:**

  | Status | When |
  |---|---|
  | 400 | Malformed JSON, wrong types, failed validation (`errors` lists each field) |
  | 401 | Missing, expired or invalid token (with `WWW-Authenticate: Bearer`) |
  | 403 | Valid caller, but the role may not perform this operation |
  | 404 | No such resource, **or the caller may not see it** (so IDs can't be probed) |
  | 409 | Conflicts with the current state (e.g. a duplicate unique value) |
  | 412 / 428 | `If-Match` doesn't match the current version / `If-Match` is required but missing |
  | 413 / 415 | Body too large / unsupported content type |
  | 429 | Rate limit exceeded (with `Retry-After`) |
  | 500 | A bug. Never used for expected outcomes |
  | 503 | Overloaded or a dependency is down (with `Retry-After` when known) |

## JSON
- **Field names in camelCase**, matching the Kotlin DTOs.
- **Explicit DTOs per endpoint direction:** a request DTO lists only what the client may set; a response DTO lists only what the caller may see. Domain models are never serialized directly (mass assignment, over-exposure).
- **Nulls.** An absent optional field is omitted (`explicitNulls = false`). A field is never sometimes absent and sometimes `null` with different meanings.
- **Timestamps** are ISO 8601 in UTC (`2026-03-01T10:15:30.123Z`), from `kotlin.time.Instant`.
- **Money** is a decimal string plus an ISO 4217 currency code (`{"amount": "12.50", "currency": "EUR"}`), never a floating-point number.
- **IDs** are opaque strings (UUID v7). Never sequential numbers, which leak volume and invite enumeration.
- **Enums** are strings. Clients must handle unknown values, so a new value is an additive change.

## Errors
Every error response is RFC 9457 problem details with `Content-Type: application/problem+json`:
```json
{
  "type": "https://api.example.com/problems/validation_failed",
  "title": "Bad Request",
  "status": 400,
  "code": "validation_failed",
  "detail": "The request is not valid",
  "instance": "/v1/notes",
  "errors": ["title: must not be blank"]
}
```
- **`code` is the contract.** Clients switch on it, never on `detail` or `title`. Codes are `snake_case`, stable and listed in the error-code catalogue of the OpenAPI contract.
- **`type`** is a URI under the API's documentation, one per code.
- **No internals.** No stack traces, exception class names, SQL or library messages in any response.
- **The same shape everywhere,** including 401 from the authentication challenge, 404 for unknown routes, 413, 415 and 429 from plugins. StatusPages produces all of them.

## Pagination, filtering and sorting
- **Every collection is paginated,** with a default and a maximum page size (e.g. 20 and 100). A larger `limit` is clamped to the maximum.
- **Keyset (cursor) pagination** by default: `GET /v1/notes?cursor=…&limit=20` returns `{"items": [...], "nextCursor": "…"}`. `nextCursor` is absent on the last page.
  - The cursor is opaque (e.g. base64url of the last ID), so its format can change without breaking clients.
  - With time-ordered UUID v7 IDs, "newest first" is `WHERE owner_id = ? AND id < :cursor ORDER BY id DESC LIMIT :limit + 1`, served by an index on `(owner_id, id)`.
  - Offset pagination only for small, stable sets, where skipping and duplicates don't matter.
- **Filters and sorting** use query parameters with an allow-list of fields (`?status=open&sort=-updatedAt`). Unknown fields are a 400, never passed through to SQL.

## Concurrency and caching
- **Optimistic locking** with a version column. Responses carry `ETag: "<version>"`.
- **Updates require `If-Match`.** A missing header is 428; a stale version is 412. The client re-reads and retries, so no update is lost.
- **Conditional reads.** `If-None-Match` with the current ETag gets 304 (the ConditionalHeaders plugin).
- **`Cache-Control`** is explicit on cacheable public resources; per-user responses are `private` or `no-store`.

## Idempotency
- **Retried creates must not duplicate.** Clients send an `Idempotency-Key` header (a UUID) on `POST` requests that create something they may retry: orders, payments, messages.
- **The server stores** the key, the caller and a hash of the request with the first response, for a retention window (e.g. 24 h). A repeat with the same key and body returns the stored response; the same key with a different body is 422.
- **Store the key in the same transaction** as the change it protects.

## Versioning and compatibility
- **The major version is in the path:** `/v1/…`. It changes only for a breaking change.
- **Within a version, changes are additive:**
  - new endpoints, new optional request fields, new response fields, new enum values;
  - never: removing or renaming a field, changing a type or its meaning, making an optional field required, tightening validation, changing a status code or an error `code`.
- **Tolerant reader on both sides.** The server ignores unknown request fields (`ignoreUnknownKeys = true`); clients ignore unknown response fields and enum values.
- **Old clients.** The oldest supported mobile app version is a requirement (Phase 1). Contract tests run against the DTOs that version uses.
- **Deprecation:**
  1. Announce it, with a date, to every consumer.
  2. Send `Deprecation` and `Sunset` headers on the old version, with a `Link` to the migration guide.
  3. Track usage per version and per client version; remove it only when usage is near zero and the sunset date has passed.
  4. Raise the minimum supported app version first where the client is a mobile app.

## Long-running work
- Return `202 Accepted` with a `Location` of a status resource (`/v1/exports/{id}`) instead of holding the connection open. Do the work in a queue consumer.
- The status resource reports `pending`, `running`, `succeeded` (with a link to the result) or `failed` (with a problem).

## Webhooks
- **Sign every payload** (e.g. HMAC-SHA256 over the timestamp and the body, with a per-subscriber secret) and include the timestamp, so receivers can reject replays older than a few minutes.
- **Deliver at least once,** retrying with exponential backoff, and give every event an ID so receivers can deduplicate.
- **Offer a replay** of past events for a subscriber.

## OpenAPI workflow
1. **Phase 3:** the feature design adds the endpoints to the contract (`docs/api/openapi.yaml`): paths, parameters, request and response schemas, error codes, security. G3 freezes it.
2. **Phase 4:** the routes are written against it. The Ktor OpenAPI compiler plugin builds a document from the routes and DTOs, which the service serves at `/openapi.json` outside production.
3. **CI** exports the generated document in a test ([testing.md](testing.md#contract-check)) and compares it with the frozen contract using an OpenAPI diff tool (e.g. `oasdiff breaking docs/api/openapi.yaml build/openapi/openapi.json --fail-on ERR`). A breaking difference fails the build; any difference needs a contract update in the same PR.
4. **Consumers** generate or check their clients from the contract, not from the code.

Generation from code is experimental in Ktor 3.6 and needs an ADR. Without it, keep the contract hand-written and validate responses against it in the contract tests instead.
