# Project: <App Name>

<One or two sentences: what the app does, target platform.>

## Architecture
- Clean Architecture + MVVM, strict unidirectional data flow.
- Calls flow `app` (presentation) → `domain` (business logic) → `data` (data sources). Dependencies point inward: `domain` is pure Kotlin and never imports from `app` or `data`; `data` implements the repository interfaces defined in `domain`.
- ViewModels call UseCases, never Repositories.

## Global Rules
- Kotlin only for new code (Java only in existing legacy modules); Hilt for DI; Coroutines + Flow for async — no RxJava or LiveData in new code.
- `val` over `var`; no `!!` — use `?.`, `?:` or `requireNotNull(x) { "reason" }`.
- Inject `CoroutineDispatcher`s; never hard-code `Dispatchers.IO`/`Default` outside DI modules.
- No hardcoded strings, colors or dimensions — use resources or design-system tokens; support dark mode.
- Every ViewModel, UseCase and Repository must be unit-testable by design.
- Follow SOLID, DRY, KISS, YAGNI.
- Fix ktlint/detekt/Lint warnings instead of suppressing them.
- Security: no secrets or API keys in source or version control; HTTPS only; store sensitive data in DataStore with keys in the Android Keystore (e.g. Tink) — `EncryptedSharedPreferences` is deprecated, don't use it; keep R8 obfuscation on for release builds.

## Before Finishing
Run `./gradlew ktlintCheck detekt test` and make sure it passes before calling a task done.
