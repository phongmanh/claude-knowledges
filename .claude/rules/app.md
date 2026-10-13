---
paths:
  - "app/**"
  - "feature/**"
---
# Presentation Layer

- Activities, Fragments and Composables hold no business logic: they render state and forward events to the ViewModel.
- ViewModels expose state as `StateFlow` and one-time events as `SharedFlow`.
- One `sealed interface UiState` per screen, with at least `Loading`, `Success` and `Error`.
- Navigation lives in the navigation graph or a dedicated Navigator class, never inline in Composables.
- Every new Composable gets a `@Preview`.
- Critical user flows get a Compose instrumentation test.
