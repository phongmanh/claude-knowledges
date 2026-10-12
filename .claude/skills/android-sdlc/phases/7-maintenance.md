# Phase 7: Maintenance
**Gate:** each change runs a small gated cycle: CR → design delta (G3-lite) → G5 → staged release
**Deliverables:** vitals reviews, [change requests](../templates/change-request.md), hotfix releases, updated RTM and docs
**Load:** [review-checklist](../reference/review-checklist.md), [performance-reliability](../reference/performance-reliability.md), plus the phase files the change's size calls for

## Goal
Keep the app stable, secure and compliant as Android, Google Play, devices and dependencies change. Evolve it without breaking what works.

## Activities
1. **Monitor.**
   - Weekly: Android vitals (crash and ANR rates, startup, slow frames), crash reports, store reviews, KPIs.
   - Each release: compare against the previous release.
2. **Triage** by severity, with a response time for each:
   - S1 (crash spike, data loss, security issue): hotfix now.
   - S2: next release.
   - S3 and S4: backlog.
3. **Hotfix path.**
   1. Branch from the release tag.
   2. Make a minimal fix, with a test.
   3. Expedited review.
   4. G5-lite: the fix plus a regression subset.
   5. Staged rollout.
   6. Merge back to `main`.
4. **Change requests.** Every new feature, or change to baselined behaviour, starts with a CR: impact via the RTM, then a decision.
   - A small change runs design delta → implement → test → release.
   - A big one runs the full lifecycle in a new workspace.
5. **Yearly platform update.** For each new Android release:
   - read its behaviour changes and test the app on it;
   - raise `targetSdk` before Play's annual deadline (usually in August);
   - review `minSdk` against audience data.
6. **Dependencies.**
   - Automated update PRs every month (e.g. Renovate or Dependabot).
   - Security patches immediately.
   - Remove libraries that are no longer used.
7. **Tech debt.** Keep a ranked debt list, and reserve a fixed share of each release for it (e.g. 15–20%).
8. **Documentation.** When the code changes, update the architecture document, ADRs and feature designs in the same PR.
9. **End of life.** Retire a feature or an old version with notice:
   1. switch the flag off;
   2. remove the code;
   3. raise the minimum supported version;
   4. clean up the backend.

## Checklist per release
- [ ] Every change in scope has an approved CR; RTM updated
- [ ] Regression suite and affected NFR tests passed
- [ ] `targetSdk` and dependencies within policy
- [ ] Release checklist completed; staged rollout with halt criteria

## Pitfalls
- **Hotfixes that skip tests** and cause the next incident.
- **Missing the target-SDK deadline,** after which the app can't publish updates.
- **Letting dependencies age** until one update becomes a migration project.
- **Docs that stop matching the code** after the first year.
