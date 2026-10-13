# Phase 4: Implementation
**Gate:** G4 Code complete
**Deliverables:** code with tests, CI pipeline, a release-candidate (RC) image, RTM update
**Load:** [code-patterns](../reference/code-patterns.md), [architecture](../reference/architecture.md), [api-design](../reference/api-design.md), [testing](../reference/testing.md), [review-checklist](../reference/review-checklist.md); for project setup, also [security-privacy](../reference/security-privacy.md), [performance-reliability](../reference/performance-reliability.md) and [deployment-operations](../reference/deployment-operations.md)

## Goal
Build the service exactly as designed, in small reviewed PRs, with tests and quality gates from the first commit, and an image that can be deployed the same way to every environment.

## Entry criteria
- G3 approved; feature designs and the OpenAPI contract frozen.
- The repository, CI runners with Docker, the container registry, a development database and an identity-provider test tenant are available.

## Activities
### Step 0: project setup (new service only)
1. **Build.**
   - The Gradle wrapper, a version catalog (`gradle/libs.versions.toml`) with every dependency at the latest stable version, the Ktor BOM, and convention plugins in `build-logic`.
   - The Ktor Gradle plugin for the fat JAR and the image; the OpenAPI compiler plugin if the ADR adopts it.
   - ktlint, detekt and Kover with a coverage floor.
2. **Application skeleton** following the [code patterns](../reference/code-patterns.md):
   - `main` with `EngineMain`, `application.yaml`, `AppConfig` with validation, `configureApp`;
   - Koin, the plugins (monitoring, serialization, StatusPages, HTTP hardening, authentication, validation, routing);
   - `/health/live`, `/health/ready`, `/metrics`;
   - JSON logging with the call ID.
3. **Persistence:** HikariCP, Exposed, Flyway with `V1__…sql`, the `Transactor`, the migration job's entry point and `migration.yaml`.
4. **Local environment:** a `docker compose` file with PostgreSQL (the production major version) for running the service locally; a README with the environment variables.
5. **Test infrastructure:** fakes, `TestConfig`, `TestTokens`, `TestDatabase` with Testcontainers, the schema-drift and DI-graph tests.
6. **Image:** non-root, minimal base, container-aware JVM flags; scanned; pushed by CI with the commit tag.
7. **Process:** the CI pipeline below, branch protection on `main`, a PR template that asks for the contract diff and migration notes.
8. **Prove the pipeline.** Before writing features, merge one tiny vertical slice through it and deploy it to the development environment, e.g. one authenticated endpoint that reads from one table, with its migration, tests and dashboard.

### Feature build order
Each step is one or more PRs, taken from the feature design's slice plan.
1. **Migration and table objects:** the Flyway migration and the Exposed table, with the schema-drift test.
2. **Domain:** models, value classes, `DomainError` cases, repository interfaces.
3. **Persistence:** the `…RepositoryImpl` with its Testcontainers tests.
4. **Outbound adapters:** gateways and clients, with `MockEngine` tests.
5. **Services:** the use cases with unit tests on fakes (access rules, errors, edge cases).
6. **API:** resources, DTOs, validators, routes, and the contract update; route tests for the full matrix.
7. **Wiring and operations:** Koin bindings (and the DI-graph test), feature flag, metrics, alerts and runbook updates.

### Coding rules
- Follow the [code patterns](../reference/code-patterns.md) and the project's own rules. Where they conflict, the project's rules win.
- Branch names, commits and PRs reference the ticket and the FR IDs.
- Keep the layers clean: no business logic or repository access in routes, no Ktor or Exposed types in the domain.
- Never block a request coroutine; JDBC only inside `transactor.inTransaction`.
- Hard-code nothing that differs per environment: URLs, limits that ops may tune, secrets.
- Handle every error path in the design through `DomainError` and StatusPages; never swallow an exception.
- Add the logs, metrics and audit events from the design. Never log personal data or tokens.
- **Keep the contract in step.** A change to a route or DTO updates `docs/api/openapi.yaml` in the same PR.

### CI pipeline
Cheapest checks first. Any failure blocks the merge.
1. `./gradlew assemble`
2. `./gradlew ktlintCheck detekt`
3. `./gradlew test` (unit and integration tests; Docker for Testcontainers), plus `koverVerify` with the coverage floor (e.g. ≥ 80% of lines in services and domain)
4. **Contract check:** the generated OpenAPI document vs `docs/api/openapi.yaml` (e.g. `oasdiff breaking … --fail-on ERR`); consumer contract verification if clients publish contracts
5. **Image:** build with the Ktor plugin or the `Dockerfile`; scan the image and the dependencies (fail on high or critical findings); secrets scan; SBOM
6. **Migrations:** run the migration job against a fresh database and against a copy of the previous release's schema
7. On merge to `main`: push the image (tagged with the commit), deploy to development, run smoke tests

### Pull requests
- **Size and checks:**
  - ≤ ~400 changed lines;
  - one concern;
  - CI green, including the contract check;
  - at least one approving review against the [review checklist](../reference/review-checklist.md).
- **Description:** what changed and why, with the FR IDs and endpoints; the contract diff; migration notes (what, how long, backward compatible?).
- **Deviations** from the approved design or contract need a CR, not just a PR comment.

### Definition of Done (per PR)
- Code follows the patterns; the review checklist passes.
- New logic has unit tests; new endpoints have the route-test matrix; new queries and migrations have Testcontainers tests.
- The OpenAPI contract matches the code.
- CI is green and the PR is reviewed.
- The RTM row is updated.

## Exit checklist (G4)
- [ ] All in-scope FRs implemented and merged; feature flags set for the release
- [ ] CI green on the release branch; coverage floor met; contract check passes against the frozen contract
- [ ] No open high or critical findings from static analysis, dependency, image or secrets scans, unless formally accepted
- [ ] All code reviewed; no unapproved deviations from the designs or the contract
- [ ] RC image built by CI, scanned, signed and pushed; its digest recorded
- [ ] Migrations for the release rehearsed against a copy of the previous schema
- [ ] RC deployed to staging; smoke tests pass; dashboards and alerts show it
- [ ] Test environment, test accounts and test data ready; RTM updated

## Pitfalls
- **Routes first,** against imagined services, then bending the domain to fit them.
- **Big-bang PRs** at the end of a feature.
- **Testing on H2** or with mocked repositories only, then finding SQL and migration bugs in staging.
- **The contract drifting from the code,** discovered by a client team after release.
- **A "temporary" secret or URL** in `application.yaml`, or a default password left in place.
- **Suppressing detekt warnings or disabling a scan** to make CI pass.
