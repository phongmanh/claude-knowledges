# Mobile best practices (iOS & Android, any stack)

Engineering practices for mobile apps, grouped by quality attribute.

- **Targets and verification:** [quality-attributes.md](quality-attributes.md).
- **Where these practices apply in the lifecycle:**
  - design decisions in [Phase 2](../phases/2-system-design.md) and [Phase 3](../phases/3-detailed-design.md);
  - coding in [Phase 4](../phases/4-implementation.md);
  - tests in [Phase 5](../phases/5-testing.md);
  - release in [Phase 6](../phases/6-deployment.md).

## Architecture & maintainability
- **Layered architecture (UI → domain → data)**, with dependencies pointing inward. The domain layer has no platform or UI dependencies, which makes it the part you can test and reuse.
- **Unidirectional data flow.** State flows down to the UI and events flow up. Each screen has one immutable UI state (e.g. Loading / Content / Empty / Error). This makes screens easier to reason about, test and restore.
- **No business logic in UI code** (screens, views, activities, view controllers). It belongs in view models or presenters and in the domain layer.
- **Repository pattern.** Repositories hide where data comes from (network, database, cache). The rest of the app doesn't need to know.
- **Dependency injection** for everything with side effects: network, storage, clock, dispatchers/schedulers. This enables testing and lets you swap implementations.
- **Modularise by feature.** Give each module a small public API, and share a design-system module. This improves build times, ownership and boundaries.
- **One consistent error model** (result types or sealed error hierarchies), mapped to user-facing messages in one place.
- **Native vs. cross-platform is a Phase 2 ADR.** Weigh platform API needs, performance, UI fidelity, team skills, code sharing and long-term support.
- **Enforce static analysis and formatting in CI**, and keep naming and structure consistent across features.

## Testability
- **Unit-test on the host.** Test business logic and view models on the host machine, with no device or emulator. Use fake repositories and controllable dispatchers and clocks, so the tests stay fast and reliable.
- **UI tests for critical user flows only.** Screenshot tests for design-system components and key screens catch visual regressions cheaply.
- **Stable selectors.** Accessibility identifiers and labels double as stable test selectors.
- **Mock the network at the HTTP layer**, with recorded or contract-generated responses. Never test against live services.
- **Real devices.** Use a device farm for the compatibility matrix, and run the UI suite on both the minimum and the latest OS versions.
- **Test upgrade paths.** Install the previous store version, create data, upgrade, and check the data survived.

## Performance
- **Never block the main/UI thread** with I/O, database work, parsing or heavy computation. The UI must respond within one frame.
- **Set a startup budget.** Defer non-critical initialisation, avoid synchronous disk or network access at launch, and initialise dependencies lazily. Use the platform's startup profiling and optimisation tools.
- **Rendering:**
  - Use stable keys and item recycling in lists.
  - Keep view hierarchies flat.
  - Avoid unnecessary re-renders and recomposition.
  - Paginate long lists.
- **Images:**
  - Decode them at display size.
  - Cache them in memory and on disk, with size limits.
  - Use modern formats.
  - Never load a full-resolution image into a thumbnail.
- **Memory:** keep no long-lived references to screens or contexts. Use leak detection in debug builds, and give every cache a bounded size.
- **Network:**
  - Compress responses and cache them using HTTP headers.
  - Batch and coalesce requests.
  - Prefetch on Wi-Fi or while charging when it makes sense.
  - Cancel requests when their screen closes.
- **Battery:**
  - Run background work through the platform job scheduler, with constraints (network, charging, idle).
  - Don't poll; batch background work instead.
  - Ask for the least precise location that works.
- **App size:**
  - Shrink code and resources.
  - Split builds by architecture and screen density.
  - Deliver rarely used features on demand.
  - Prefer vector assets.
- **Measure on low-end reference devices and slow networks**, not on developers' flagship phones. Track the budgets in every release.

## Scalability
- **Incremental (delta) sync** using server-provided tokens, instead of re-downloading everything.
- **Jitter and exponential backoff** on retries and scheduled syncs. This stops millions of devices from hitting the backend at the same moment (a "thundering herd").
- **Honour `Retry-After`** and HTTP 429/503 responses from the server.
- **Cache and coalesce identical requests**, and paginate any list that can grow.
- **Remote config and feature flags** can switch off heavy features or reduce polling to shed load during an incident.
- **Serve media through a CDN**, in appropriately sized variants.

## Reliability
- **Offline-first, where required.** The local database is the single source of truth: the UI reads from it, and the network refreshes it.
- **An outbox for writes.** Queue user actions locally and send them with **idempotency keys**, so a retry can never create a duplicate (e.g. two payments).
- **A defined conflict policy** (last write wins, field-level merge, or the user resolves). Decide it in Phase 2; don't discover it in production.
- **Survive process death and configuration changes.** Persist the essential UI state and restore the user exactly where they were.
- **Handle every network state:** offline, captive portal, slow, flaky, and switching between networks.
- **Parse tolerantly.** Ignore unknown fields, and handle unknown enum values and missing optional fields. The backend will evolve before old apps update.
- **On-device database migrations never lose data.** Test them from every supported previous version.
- **Kill switches and a forced-update mechanism** for critical defects, because a shipped binary can't be rolled back.

## Security
Follow the MASVS level chosen in Phase 1 and the OWASP Mobile Top 10.
- **Storage:**
  - Keep secrets and tokens only in platform secure storage (Android Keystore, iOS Keychain).
  - Encrypt sensitive local data with keys held in that storage.
  - Keep nothing sensitive in plain preferences, logs, caches or backups.
- **No secrets in the binary.** Assume the app will be decompiled. Keys that matter stay on the backend; the client uses short-lived tokens tied to the user.
- **Network:**
  - TLS only, with cleartext disabled in the platform configuration (the Android network security configuration, iOS App Transport Security).
  - Pin certificates only if the threat model needs it, and then with backup pins and a rotation plan. Otherwise a certificate change can lock users out.
- **Authentication:**
  - OAuth 2.x / OpenID Connect with PKCE, through the system browser rather than an embedded web view.
  - Short-lived access tokens, with refresh-token rotation.
  - For high-value actions, biometrics bound to a keystore-protected key, not a simple yes/no check.
- **Platform interaction:**
  - Treat deep links, intents, URL schemes and push payloads as untrusted input.
  - Prefer verified app links and universal links.
  - Don't export components unless they need to be exported.
  - Harden web views: JavaScript off unless needed, no file access, origins on an allow-list.
- **Permissions:** request the minimum, at the moment it's needed, with a clear explanation. Handle denial gracefully.
- **Sensitive screens:**
  - Hide their content in the app-switcher snapshot.
  - Block screenshots where required.
  - Keep sensitive data out of the clipboard and notifications.
- **Release builds:** code shrinking and obfuscation on, debugging off, verbose logs stripped.
- **Backend trust:**
  - Use app attestation (e.g. Play Integrity, App Attest) to help the backend reject tampered clients.
  - Add root/jailbreak and tamper detection only when the risk profile (MASVS-RESILIENCE) calls for it.
- **Supply chain:** vet third-party SDKs (permissions, data collected, maintenance) and keep them up to date.

## Privacy
- Collect the minimum, and process data on the device when you can.
- Ask for tracking consent where required (e.g. App Tracking Transparency on iOS). Load analytics and ad SDKs only after consent.
- Keep store privacy disclosures accurate (privacy labels, the data safety form, privacy manifests), including what third-party SDKs collect.
- Offer **in-app account deletion** whenever the app lets users create an account. Both major stores require it.
- Never put PII in analytics events, logs or crash reports.

## Accessibility & UX
- **Follow the platform design guidelines** (Material Design, Human Interface Guidelines). Users expect native behaviour.
- **Screen readers** (TalkBack, VoiceOver):
  - Give every interactive element an accessible label, role and state.
  - Keep the focus order logical.
  - Group related content.
- **Text size:** support system font scaling (to at least 200%) and display size without clipping, using layouts that reflow.
- **Visual minimums:**
  - Touch targets ≥ 48×48 dp (Android) / 44×44 pt (iOS).
  - Text contrast ≥ 4.5:1.
  - Never use colour alone to convey meaning.
- **System settings and screen shapes:** respect reduce-motion and dark-mode settings. Adapt layouts to tablets, foldables, landscape and multi-window.
- **Every state:** design loading, empty, error, offline and permission-denied states, each with a clear next action.

## Internationalisation
- **Resources:** keep all user-facing text in resource files with keys. Handle plurals and gender with the platform's localisation features, and never concatenate strings.
- **Formatting:** format dates, times, numbers and currencies for the locale. Store times in UTC and display them in local time.
- **RTL:** support right-to-left layouts by using start/end instead of left/right, and mirror directional icons.
- **Testing and language choice:** test with pseudo-locales (long strings, accents, RTL). Support a per-app language preference where the platform allows it.

## Observability
- **Crash and ANR/hang reporting.** Upload symbol and mapping files for every release, so stack traces are readable.
- **Performance monitoring.** Track startup time, slow and frozen frames, and network latency and errors, broken down by app version, OS and device class.
- **Analytics events.** Define them in the tracking plan, use a naming convention, and respect consent.
- **Correlation IDs.** Send a correlation ID header with each API call, so a user's request can be traced into the backend.
- **Release-health dashboard.** Show crash-free users and sessions and adoption for each version. This drives the staged-rollout decisions.

## Delivery & release
- **Builds and signing:**
  - CI builds and tests every PR.
  - Only CI produces release builds, signed with keys kept in the CI secret store, never on laptops or in the repository.
  - Use store-managed app signing. Back up the upload key securely and document who owns it.
- **Versions and notes:** use monotonic build numbers, and write release notes for each locale.
- **Rollout:** release through tracks (internal → closed → open → production) with a **staged or phased rollout** and halt criteria.
- **Feature flags** separate deploying code from releasing a feature. Remove each flag after full rollout.
- **Forced updates:** check the minimum supported version at startup, so a version can be retired when needed.

## Compatibility
- **OS versions:** review the minimum and target OS versions every year, against audience data and store requirements.
- **Device matrix:** cover low-RAM devices, small and large screens, tablets and foldables, and manufacturers whose OS versions behave differently.
- **New OS releases:** check each major release's behaviour changes (permissions, background limits, privacy) against the app before it reaches users.
- **Missing hardware:** degrade gracefully when optional hardware (camera, biometrics, NFC, GPS) isn't there.
