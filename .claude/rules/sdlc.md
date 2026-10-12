---
paths:
  - "docs/sdlc/**"
---
# SDLC Documents

Applies to the deliverables of the android-sdlc (`/android-sdlc`) and compose-multiplatform-sdlc (`/compose-multiplatform-sdlc`) workflows under `docs/sdlc/<initiative-slug>/`.

- **Start from `STATUS.md`.** Check the current phase, and confirm the previous gate is approved before writing a later phase's deliverable.
- **Follow the template** of the workflow that owns the workspace, keeping its section order and tables: `.claude/skills/compose-multiplatform-sdlc/templates/` when `STATUS.md` names that skill (an Android + iOS app), otherwise `.claude/skills/android-sdlc/templates/`.
- **Platforms.** In a compose-multiplatform-sdlc workspace, requirements, designs and tests apply to Android and iOS unless tagged `[Android]` or `[iOS]`, and every gate is checked on both.
- **IDs everywhere:**
  - `FR-nnn`;
  - `NFR-<ATTR>-nn`;
  - test IDs `UT-`/`IT-`/`UI-`/`ST-`/`AT-`.

  Every new requirement, design element and test gets an `rtm.md` row in the same change.
- **Never invent** numbers, approvals, approver names or sign-off dates. Mark unknowns `TBD-<n>` and assumptions `ASSUMPTION:`, and list both in `STATUS.md`.
- **Baselined documents.** A deliverable whose `STATUS.md` row says Approved is baselined.
  - Change it only through an approved `cr/CR-NNN-<title>.md`.
  - The `guard-sdlc-baseline.py` hook asks the user to confirm before such an edit.
- **Gate decisions** go only in the `STATUS.md` gate log, and only after the approver has given them in the conversation.
- **Keep documents short:** tables and bullets over prose; link instead of repeating.
