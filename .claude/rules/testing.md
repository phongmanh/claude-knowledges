---
paths:
  - "**/src/test/**"
  - "**/src/androidTest/**"
  - "**/src/testFixtures/**"
  - "**/src/screenshotTest/**"
  - "**/src/*Test/**"
---
# Test Code

Applies to test sources only, including Kotlin Multiplatform test source sets (`commonTest`, `iosTest`, `androidHostTest`, `androidDeviceTest`). Details and snippets: `.claude/skills/android-sdlc/reference/testing.md`, and for Kotlin Multiplatform `.claude/skills/compose-multiplatform-sdlc/reference/testing.md`.

- **Files:** one test class per class under test, `<ClassUnderTest>Test.kt`, in the same package.
- **Structure:** Arrange–Act–Assert, one behaviour per test, no logic (`if`, loops) in tests.
- **Names** describe the behaviour:
  - JVM tests use backtick names: `` `refresh fails offline - shows network error`() ``.
  - Instrumented tests use `action_condition_result`, because DEX doesn't allow spaces in names before API 30.
- **Fakes over mocks.** Reuse the `Fake…Repository` classes from the shared testing module. Use MockK only for what can't be faked.
- **Deterministic:**
  - use `runTest`, `MainDispatcherRule`, and an injected `CoroutineDispatcher` and `Clock`;
  - never `Thread.sleep`, the real network or real time.
- **Flows:** assert emissions with Turbine (`flow.test { awaitItem() }`).
- **ViewModels:**
  - create them inside the test, after `MainDispatcherRule` has set `Dispatchers.Main`;
  - assert state transitions, not internals.
- **UI tests:**
  - target the stateless `…Content` Composable;
  - find nodes by text or content description; use `testTag` only when nothing visible identifies the node.
- **Room:** an in-memory database for DAO tests; a `MigrationTestHelper` test for every migration.
- **Bug fixes** come with a test that fails without the fix.
- **Kotlin Multiplatform** (`commonTest` runs on the JVM, the iOS simulator and, with device tests, Android devices):
  - kotlin-test (`@Test`, `@BeforeTest`, `@AfterTest`), not JUnit. There are no rules: set and reset `Dispatchers.Main` in `@BeforeTest`/`@AfterTest` instead of `MainDispatcherRule`.
  - Names use `action_condition_result`; backtick names with spaces only in `androidHostTest`.
  - Fakes only, since MockK is JVM-only; Ktor `MockEngine` replaces the network.
  - Compose UI tests use `runComposeUiTest` against the stateless `…Content`.
  - Code in `androidMain`/`iosMain` is tested in its own platform test source set.
