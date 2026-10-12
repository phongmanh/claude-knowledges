# Phase 3: Detailed design
- **Gate:** G3 Ready to build (CDR)
- **Deliverables:** [detailed designs](../templates/detailed-design.md), API contracts, data schema, UI specs, integration test cases

## Goal
Specify every component in enough detail that it can be built easily and in parallel. Freeze the interfaces between teams, and design the tests that will verify each component.

## Entry criteria
- G2 approved: the architecture and ADRs are baselined and the stack is chosen.
- Project rules for the chosen stack exist or are being written (e.g. `.claude/rules/`, coding standards).

## Activities
1. **Component design.** Write one [detailed design](../templates/detailed-design.md) per component, or per changed component.
   - Responsibilities, public interfaces and dependencies. Add a C4 Level 3 diagram where it helps.
   - Sequence diagrams for the key flows, **including the error and timeout paths**. State machines for entities with a lifecycle.
   - Match the detail to the risk. Complex, critical or shared parts get a full design; trivial CRUD gets a paragraph.
2. **API contracts.** Machine-readable (OpenAPI, AsyncAPI or protobuf). Each contract covers:
   - operations, plus request and response schemas with validation rules (types, formats, lengths, ranges, required fields);
   - the error model (RFC 9457 problem details) and the error codes for each operation;
   - authentication, plus an **authorisation matrix**: role × operation × resource ownership;
   - pagination, filtering, sorting, idempotency keys, rate limits and examples.

   Consumers (mobile, web and partner teams) review each contract. After that it's **frozen**, and any change needs a CR. Generate mock servers from the contracts so clients and server can be built in parallel.
3. **Data design.**
   - Logical and physical ERD.
   - Constraints: primary and foreign keys, unique, not-null, check.
   - Indexes derived from the actual query patterns.
   - Types: money as a decimal with a currency; timestamps in UTC.
   - A delete strategy (soft vs. hard) consistent with the privacy erasure rules.
   - Column-level protection for sensitive data.
   - Versioned, reversible migration scripts; seed and test data.
   - Legacy data mapping with reconciliation rules (counts, checksums, samples).
4. **UI/UX design.**
   - High-fidelity designs for every screen **and every state**: loading, empty, error, offline, partial data, permission denied, success.
   - A navigation map.
   - Design tokens (colour, type, spacing, elevation), including dark mode.
   - Responsive and adaptive layouts.
   - Accessibility annotations: focus order, labels, roles, headings, contrast, touch and click target sizes, motion.
   - A copy deck with string keys (ready for i18n) that leaves room for text expansion (often 30% or more in some languages).
   - A usability test of a prototype with representative users before G3.
5. **Error handling, observability and configuration.**
   - An error taxonomy (validation, business rule, authentication, authorisation, not found, conflict, transient, fatal), and how each error maps across the layers to a user-facing message.
   - Timeout and retry values for each outbound call, and the fallbacks.
   - A log event catalogue: name, level, fields and **PII redaction**.
   - Metric names and labels (keep label cardinality low); trace spans.
   - An analytics tracking plan: event, properties, purpose, whether consent is needed.
   - Alert definitions with thresholds, each linked to a runbook.
   - Configuration keys per environment. Feature flags with an owner, a default and a **removal date**.
6. **Security controls in detail.**
   - Allow-list validation for each input field.
   - Output encoding for each context (HTML, URL, SQL, shell, logs).
   - An object-level authorisation check for every operation that takes a resource ID.
   - Cryptography: only vetted libraries and current algorithms, never custom crypto. Define key usage and rotation.
   - File uploads: type, size, scanning, storage location.
   - Security headers and session handling.
   - Update the threat model at component level.
7. **Test design (V-model).**
   - Integration and contract test cases, derived from the API contracts and sequence diagrams.
   - Unit test design for complex logic: equivalence partitions, boundary values, decision tables, state transitions.
   - Test data sets. Review the test cases with QA.
8. **Implementation plan.**
   - Tasks with estimates and dependencies, plus an **integration order** that lets the parts integrate early.
   - Coding standards, repository layout, and the branching and review policy.
   - A Definition of Done: code reviewed, tests written and passing, docs updated, RTM updated, no new critical findings.

## Platform specifics

### Mobile
- **UI and navigation:**
  - A UI state model for each screen (e.g. Loading / Content / Empty / Error) and the events it handles.
  - A navigation graph and deep-link map, with every deep-link parameter validated.
- **Offline and data:**
  - The offline data model and sync protocol: delta sync, tombstones for deletions, conflict rules, retry with backoff.
  - The on-device database schema and its migrations. An upgrade must never lose user data, so plan upgrade tests from every supported version.
- **Background work, permissions and push:**
  - Background job specs: constraints, frequency, retry.
  - Permission flows: rationale, denied, and "don't ask again".
  - Push payload schemas, and how pushes are handled when the app is in the foreground, in the background or terminated.
- **Startup and lifecycle:**
  - The startup sequence, with non-critical work deferred.
  - State restoration after process death.
  - Image sizes for each screen density.

### Frontend
- **Components:** a spec for each one covering props/inputs, states, variants, and keyboard and screen-reader behaviour (following the WAI-ARIA Authoring Practices).
- **Routes:** a route map with the rendering mode and data needs of each route.
- **URLs:** design them to be shareable and bookmarkable, and make the back button work.
- **Forms:** specs with the same validation rules on client and server, how errors are shown, and `autocomplete` attributes.
- **State:** the state shape and the cache keys.
- **Loading:** the loading strategy (skeletons, prefetching).
- **SEO:** metadata for each page.
- **Assets:** an asset budget for each route.

### Backend
- **Endpoints and queries:**
  - A spec for each endpoint, linked to the contract.
  - Query designs and execution plans for the hot paths, checked on realistic data volumes.
- **Transactions and concurrency:**
  - Transaction boundaries and isolation levels.
  - Concurrency control: optimistic locking with a version column.
- **Messaging and jobs:**
  - Message and event schemas with versioning rules; retry and dead-letter policies; idempotent consumers.
  - Scheduled jobs that are idempotent and locked so they can't run twice.
- **Caching and limits:**
  - Cache keys, TTLs and invalidation triggers.
  - Rate-limit values and outbound timeouts.

## Deliverables
- A detailed design for each component ([templates/detailed-design.md](../templates/detailed-design.md)).
- Frozen API contracts and mock servers.
- The database schema and migration plan, plus the legacy data mapping.
- UI specs, design tokens and the copy deck.
- Logging, metrics and analytics plans, and the alert definitions.
- The integration test plan and cases, plus unit test design notes.
- The implementation plan and the Definition of Done.
- RTM updated: requirement → design element → planned test cases. Threat model updated.

## Exit gate checklist (G3)
- [ ] Every component in scope has a design proportional to its risk
- [ ] API contracts reviewed by all consumers and frozen; mock servers available
- [ ] Schema, indexes and migration plan (including rollback) reviewed
- [ ] UI designs cover every state and have accessibility annotations; the prototype has been usability-tested
- [ ] Error handling, logging, metrics, analytics and alerts designed; PII redaction defined
- [ ] Security controls specified for each component; threat model updated
- [ ] Integration test cases written and reviewed with QA
- [ ] Implementation plan estimated and scheduled; Definition of Done agreed
- [ ] RTM links every requirement to a design element and a planned test
- [ ] Design inspection passed; baseline tagged

## Pitfalls
- **Happy-path-only designs** with no error, empty, offline or permission states.
- **Contracts that keep changing during implementation without CRs.** This is the main cause of late integration pain.
- **Missing indexes for the main queries**, or no rollback plan for migrations.
- **Over-specifying trivial code** while under-specifying the risky parts.
- **Analytics and logging designed after launch.** The first weeks of data are lost, or they leak PII.
