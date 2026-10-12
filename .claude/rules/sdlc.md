---
paths:
  - "docs/sdlc/**"
---
# SDLC Documents

Applies to the deliverables of the android-sdlc workflow (`/android-sdlc`) under `docs/sdlc/<initiative-slug>/`.

- **Start from `STATUS.md`.** Check the current phase, and confirm the previous gate is approved before writing a later phase's deliverable.
- **Follow the template** in `.claude/skills/android-sdlc/templates/`, keeping its section order and tables.
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
