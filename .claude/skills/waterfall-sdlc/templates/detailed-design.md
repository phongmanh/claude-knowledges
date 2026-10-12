# Detailed design: <Component name>

| Version | Status | Owner | Reviewers | Last updated |
|---|---|---|---|---|
| 0.1 | Draft | <developer / tech lead> | <tech lead, QA, security, UX> | YYYY-MM-DD |

> Write one file per component (or per changed component), e.g. `docs/sdlc/<initiative>/design/<component>.md`.
>
> Match the depth to the risk. A trivial component may need only sections 1–3 and 13.

## 1. Overview
- **Responsibilities:** what the component does.
- **Not responsible for:** what it explicitly does **not** do.
- **Position in the architecture:** link the C4 container.

## 2. Requirements covered
| Requirement ID | How this component satisfies it |
|---|---|

## 3. Interfaces
- **Provided:** a link to the API contract file (OpenAPI / AsyncAPI / protobuf), plus the events it publishes.
- **Required:** each dependency, with its contract, timeout, retry policy and fallback.

## 4. Internal structure
A component diagram (C4 L3) or a module/class outline, plus the key abstractions.

## 5. Data
- **Schema / ERD** and constraints.
- **Indexes,** each with the queries it serves.
- **Migrations,** forward and rollback.
- **Retention and deletion** rules.
- **Sensitive fields** and how they're protected.

## 6. Key flows
- **Sequence diagrams** for the main flows **and the error/timeout paths**.
- **A state machine** for each entity with a lifecycle.

## 7. Error handling
| Error | Cause | Handling (retry / fallback / surface) | User-facing message key | Log level |
|---|---|---|---|---|

## 8. Security controls
- **Input validation** rules for each field (allow-lists).
- **Authorisation checks** for each operation, at object, function and property level.
- **Output encoding.**
- **Crypto:** vetted libraries only; the algorithm and how keys are used.
- **File handling.**
- **Threat-model threats** this component addresses (IDs).

## 9. Observability
- **Log events:** name, level, fields, PII redaction.
- **Metrics:** name, type, labels (keep cardinality low).
- **Traces and spans.**
- **Analytics events:** from the tracking plan, with any consent requirement.
- **Alerts:** condition, severity, runbook link.

## 10. Configuration and feature flags
| Key / flag | Purpose | Default | Per-environment values | Owner | Removal date |
|---|---|---|---|---|---|

## 11. Performance and scalability
- **Expected load** and the hot paths.
- **Caching:** keys, TTLs, invalidation.
- **Limits and budgets.**

## 12. Platform notes
- **Mobile:** UI state model, offline/sync, background work, permissions, lifecycle and process death.
- **Frontend:** component states and variants, keyboard and screen-reader behaviour, route and rendering mode, form validation.
- **Backend:** transactions and isolation, concurrency control, idempotency, jobs, message schemas.

## 13. Test design
| Test ID | Level (unit / integration / contract) | Requirement ID | Technique (boundary values, decision table, state transition, …) | Description |
|---|---|---|---|---|

## 14. Open issues
| ID | Question | Owner | Due |
|---|---|---|---|
