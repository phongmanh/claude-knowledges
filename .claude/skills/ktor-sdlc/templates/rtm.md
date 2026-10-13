# Requirements traceability matrix: <Service or feature>

Every requirement traces forward to design, code, tests and the release. Every test traces back to a requirement. Update this file in the same PR as the change.

| Req ID | Summary | Priority | Design (architecture § / feature design) | Endpoints, tables, events | Code (module / package, PRs) | Tests (IDs) | Result | Release |
|---|---|---|---|---|---|---|---|---|
| FR-001 | List the caller's notes | M | design/notes.md §1 | `GET /v1/notes`; `notes` | notes/api, notes/persistence, #12 #14 | UT-003, IT-004, IT-005, CT-001, AT-001 | Pass | 1.0.0 |
| FR-002 | Create a note | M | design/notes.md §1 | `POST /v1/notes`; `notes`; `NoteCreated` | notes/api, notes/application, #15 | UT-001, IT-001, IT-002, IT-003, AT-002 | | |
| NFR-PERF-01 | p95 ≤ <n> ms at <n> req/s | M | architecture.md §1, §9 | `GET /v1/notes`; `notes_owner_id_id_idx` | notes/persistence | ST-010 | | |

## Coverage checks
| Check | Required |
|---|---|
| Requirements without a design | 0 at G3 |
| Endpoints without a contract entry | 0 at G3 |
| Endpoints without the route-test matrix (401 / 400 / 404 / success) | 0 at G4 |
| Must requirements without a passing test | 0 at G5 |
| Tests without a requirement | 0 (trace them, or remove them) |
