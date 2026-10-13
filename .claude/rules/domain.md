---
paths:
  - "domain/**"
  - "**/domain/**"
---
# Domain Layer

- Pure Kotlin only: no Android framework dependencies (`Context`, `android.*`).
- One UseCase = one business action.
- UseCases depend on the repository interfaces defined in this layer, never on implementations.
- Domain models are separate from DTOs; mapping happens in `data`.
- Every UseCase gets a JVM-only unit test: no Robolectric, no instrumentation. A test that needs Android belongs in another module.
