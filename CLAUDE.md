# Project: <App Name>

## Overview
<One or two sentences: what the app does, target platform.>
- Language: Kotlin (Java only in legacy modules, do not add new Java code)
- Min SDK: <fill in> / Target SDK: <fill in>
- DI: Hilt
- Async: Coroutines + Flow (no RxJava in new code)

## Architecture
Clean Architecture, MVVM. Strict unidirectional data flow.
Layers: `app` (Presentation) → `domain` (Business logic) → `data` (Data sources)
Dependency rule: outer layers depend inward only. `domain` must never import from `app` or `data`.

## Instruction Index
- Code conventions & principles (SOLID, DRY, KISS, YAGNI, testing, security) → `@GUIDELINES.md`
- Presentation layer rules → `@app/CLAUDE.md`
- Domain layer rules → `@domain/CLAUDE.md`
- Data layer rules → `@data/CLAUDE.md`
- Cross-cutting rules (naming, git, PR process) → `@rules/naming.md`, `@rules/git.md`

## Global Rules
- Kotlin only for new code; `val` over `var`; avoid `!!`
- No hardcoded strings/colors/dimensions — use resources
- No secrets or API keys in source or version control
- Every ViewModel/UseCase/Repository must be unit-testable by design
- Follow SOLID, DRY, KISS, YAGNI — see `@GUIDELINES.md` for details

## Commands
- Build: `./gradlew assembleDebug`
- Test: `./gradlew test`
- Lint: `./gradlew ktlintCheck`
- Static analysis: `./gradlew detekt`

## When Making Changes
- Match existing patterns in the file/module before introducing new ones
- Prefer editing existing files over creating new ones unless the change clearly belongs in a new class
- Run lint/test commands above before considering a task done
