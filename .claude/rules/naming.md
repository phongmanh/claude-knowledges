# Naming Conventions

- Composables: noun phrases (`ProfileScreen`, not `ShowProfile`)
- UseCases: verb phrase + `UseCase` suffix (`GetUserProfileUseCase`)
- Repositories: noun + `Repository` suffix, interface has no prefix, impl has `Impl` suffix
  (`UserRepository` / `UserRepositoryImpl`)
- Test files: `<ClassUnderTest>Test.kt`
- Resource IDs: `<screen>_<component>_<type>` (e.g. `login_email_input`)
