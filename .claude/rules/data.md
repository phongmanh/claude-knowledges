---
paths:
  - "data/**"
  - "**/data/**"
---
# Data Layer

- Repository implementations live here; their interfaces live in `domain`.
- Remote: Retrofit with the project's existing serializer (kotlinx.serialization or Moshi). Never mix the two.
- Local: Room; DAOs return `Flow` for observable queries.
- Map DTOs to domain models with explicit `toDomain()` extensions; DTOs never leave this layer.
- Wrap every network call in a `Result`/`ApiResult`: no raw exceptions reach the domain layer.
- Each repository states its caching strategy explicitly (cache-then-network or network-then-cache) and handles offline and timeouts gracefully.
- API keys and base URLs come from `BuildConfig` or a secrets manager, never hardcoded.
