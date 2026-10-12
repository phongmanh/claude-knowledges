# Phase 4: Implementation
**Gate:** G4 Code complete (TRR, test readiness review)
**Deliverables:** code, unit tests, CI pipeline, release candidate

## Goal
Build the system exactly as designed, with quality built in. The code is correct, secure, tested, reviewed, observable and documented, and it is integrated continuously.

## Entry criteria
- G3 approved; designs and contracts frozen.
- Development, CI and test environments available.
- Project coding standards agreed.

## Activities
1. **Engineering setup** (in the first days of the phase).
   - Lay out the repository as the design describes.
   - Work on short-lived branches off a **protected main** branch. A merge needs a review and green CI.
   - Commit messages and PR descriptions reference ticket and requirement IDs.
   - Make the developer environment reproducible. One command builds, tests and runs the system locally with seed data.
   - Define every environment as infrastructure as code. No manual changes.
2. **CI pipeline with quality gates on every pull request.** Fail fast, running the cheapest checks first:
   1. Build / compile.
   2. Formatting and lint.
   3. Static analysis: complexity, code smells, architecture and dependency rules.
   4. Unit tests, with a coverage floor.
   5. SAST (static security analysis).
   6. Dependency scanning (SCA). Fail on known high or critical vulnerabilities that have a fix.
   7. Secrets scanning.
   8. Licence compliance check.
   9. A versioned, reproducible build artifact plus its SBOM.

   Nightly or on merge, run the integration tests and longer analyses, then deploy to the test environment.
3. **Write code to the platform practices** ([mobile](../practices/mobile.md), [frontend](../practices/frontend.md), [backend](../practices/backend.md)) and to the project's own rules.
   - Follow SOLID, DRY, KISS and YAGNI.
   - Keep functions small and focused, with clear names. Avoid magic numbers. Prefer immutability.
   - Handle errors explicitly; never swallow an exception. Use the user-facing messages from the design.
   - Add the logs, metrics and analytics events designed in Phase 3. Never log secrets or PII.
   - Read configuration from the environment. Never hard-code URLs, keys or credentials.
4. **Unit tests, written with the code.**
   - Test-driven development is encouraged for domain logic.
   - Keep tests fast, deterministic and isolated: Arrange–Act–Assert, one behaviour per test.
   - Treat coverage as a floor, not a goal (e.g. ≥ 80% of lines in business logic). Test behaviour, not lines.
5. **Code review on every PR.** Check that:
   - the change matches the design and the requirement IDs, with no unrequested features (gold plating);
   - tests are adequate and meaningful, covering edge cases and error paths;
   - security holds: input validation, authorisation checks, secrets, injection, logging of sensitive data;
   - performance is sound: no N+1 queries, unbounded loops or queries, main-thread work or memory waste;
   - accessibility, i18n (no hard-coded user-facing text) and observability are handled;
   - contracts, messages and migrations stay backward compatible;
   - the code is readable and maintainable;
   - the PR is small enough to review well (e.g. under ~400 changed lines).
6. **Secure coding.** Follow the latest OWASP Top 10, OWASP API Security Top 10 and OWASP Mobile Top 10, plus the ASVS/MASVS level chosen in Phase 1.
7. **Dependencies.**
   - Add few, and vet each one: maintenance activity, licence, security history, size.
   - Pin versions with lockfiles.
   - Automate update PRs, and remove dependencies you no longer use.
8. **Integrate continuously.**
   - Merge to main at least daily.
   - Build against the contract mocks first, then switch to the real services as they land.

   This removes the classic waterfall "integration hell".
9. **Feature flags.** Hide incomplete or risky features behind flags. Every flag has an owner and a removal date.
10. **Write documentation as you go:**
    - a README for each module or service;
    - API docs generated from the contracts;
    - draft runbooks;
    - ADRs for any new significant decision.
11. **Control the baseline.**
    - Any deviation from the approved design or contract needs a CR.
    - Keep the RTM up to date: requirement → code/PR → unit tests.
12. **Track progress** against the WBS (earned value or burn-up). Report schedule risk early rather than squeezing the test phase later.

## Platform specifics
The detailed practices are in the practice files. The checks below are the implementation-phase items that most often go wrong.

### Mobile
- Nothing slow on the main thread. Work is lifecycle-aware and survives configuration changes and process death.
- Release builds:
  - code shrinking and obfuscation on;
  - debugging off;
  - verbose logging stripped;
  - symbol and mapping files archived.
- No secrets or API keys in the app binary. Sensitive data is stored only in storage backed by Keystore/Keychain.
- On every new screen, check accessibility labels, font scaling and touch targets.

### Frontend
- CI checks bundle-size and performance budgets for each route.
- Never inject raw HTML without a vetted sanitiser.
- Keep the code compatible with a strict Content Security Policy: no inline scripts.
- Include accessibility checks in component tests. Use semantic HTML before reaching for ARIA.
- Put no secrets in the bundle. Everything shipped to the browser is public.

### Backend
- **Access:** every endpoint requires authentication by default and authorises each object it touches.
- **Input:** validate inputs against the contract schema.
- **Queries and calls:** use parameterised queries only, set a timeout on every outbound call, and never run unbounded queries.
- **Migrations:** keep them backward compatible (expand/contract) and test them both up and down.
- **Operability:** emit structured logs with correlation IDs, expose health and readiness endpoints, and shut down gracefully.

## Deliverables
- Source code and IaC in version control; unit tests and coverage reports.
- The CI pipeline with the quality gates above.
- Reports from static analysis, SAST, SCA and the secrets scan, plus the SBOM.
- Developer docs (READMEs, generated API docs) and draft runbooks.
- A release candidate (RC) build, versioned and deployed to the test environment.
- The RTM, updated: requirement → code → unit tests.

## Exit gate checklist (G4)
- [ ] Every in-scope requirement implemented and merged (feature-complete)
- [ ] CI green on the release branch; coverage floor met
- [ ] No open critical or high findings from static analysis, SAST, SCA or secrets scanning, unless formally risk-accepted
- [ ] All code peer-reviewed; no unapproved deviations from the design or contracts
- [ ] Docs, draft runbooks and RTM updated
- [ ] RC deployed to the test environment and smoke-tested
- [ ] Test environment and test data ready (test readiness review)

## Pitfalls
- **"Testing is QA's job, later."** A defect found in Phase 5 costs far more to fix than one caught by a unit test or a review.
- **Long-lived branches and big-bang integration** at the end of the phase.
- **Silent scope creep:** building nice-to-haves nobody approved.
- **Changing contracts or schemas without a CR**, which breaks other teams.
- **Suppressing warnings or lowering gates** to hit a date.
- **Hard-coding configuration or secrets "just for now."**
