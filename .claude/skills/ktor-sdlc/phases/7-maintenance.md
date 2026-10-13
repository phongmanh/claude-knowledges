# Phase 7: Operations & maintenance
**Gate:** each change runs a small gated cycle: CR → design delta (G3-lite, with the contract) → G5-lite → staged rollout
**Deliverables:** SLO reviews, postmortems, [change requests](../templates/change-request.md), hotfix releases, updated RTM, contract and docs
**Load:** [review-checklist](../reference/review-checklist.md), [performance-reliability](../reference/performance-reliability.md), [deployment-operations](../reference/deployment-operations.md), [api-design](../reference/api-design.md#versioning-and-compatibility), plus the phase files the change's size calls for

## Goal
Keep the service within its SLOs, secure and compliant as traffic, data, clients and dependencies change. Evolve the API without breaking any supported client.

## Activities
1. **Monitor.**
   - Weekly: SLOs and error budgets, latency percentiles, error rates per endpoint, saturation (pool, CPU, memory), slow queries, costs.
   - Each release: compare against the previous release.
2. **Error budget policy.** When a service has spent its error budget, reliability work takes priority over features until it recovers. Agree this with the product owner up front.
3. **Incidents.**
   - Severity by impact: S1 (outage, data loss, security breach), S2 (a Must feature broken or an SLO at risk), S3, S4.
   - Mitigate first (flag, scale, roll back), then fix.
   - A blameless postmortem for every S1 and S2: timeline, root cause, what helped and hurt, action items with owners and dates.
4. **Hotfix path.**
   1. Branch from the release tag.
   2. Make a minimal fix, with a test that failed before it.
   3. Expedited review.
   4. G5-lite: the fix, the affected tests and a regression subset on staging.
   5. Staged rollout with halt criteria.
   6. Merge back to `main`.
5. **Change requests.** Every new feature, or change to baselined behaviour, starts with a CR: impact via the RTM, then a decision.
   - A small, additive change runs design delta → contract update → implement → test → deploy.
   - A breaking change needs a new API version and a deprecation plan.
   - A big change runs the full lifecycle in a new workspace.
6. **API lifecycle.**
   - Track usage per endpoint, API version and client version.
   - Deprecate with notice: announce, send `Deprecation` and `Sunset` headers, follow up with the remaining callers, remove after the sunset date and when usage is near zero.
   - Finish the **contract** step of expand/contract migrations once no running version needs the old shape.
7. **Dependencies and runtime.**
   - Automated update PRs (e.g. Renovate or Dependabot) every month; security patches immediately.
   - Upgrade Kotlin and Ktor together (the Ktor compiler plugin must support the Kotlin version); read the Ktor and Exposed release notes for breaking changes.
   - Move to each new JDK LTS within its first year; refresh the base image regularly, even when the code doesn't change.
   - PostgreSQL major upgrades are planned operations with a rehearsal and a rollback plan.
8. **Capacity and cost.** Review traffic and data growth against the capacity model (e.g. monthly). Add indexes, archive or partition data, and resize before limits are hit.
9. **Security upkeep.** Rotate secrets on schedule; review access to production; re-run DAST and the authorisation tests for each significant change; keep the threat model current.
10. **DR drills.** Restore from backup on a schedule (e.g. quarterly), and fail over across zones or regions as the DR tier requires. Record the measured RPO and RTO.
11. **Data lifecycle.** Check that retention and erasure jobs run and complete; handle data-subject requests within the deadline.
12. **Tech debt.** Keep a ranked debt list and reserve a fixed share of each release for it (e.g. 15–20%).
13. **Documentation.** When the code changes, update the contract, the architecture document, ADRs, feature designs and runbooks in the same PR.
14. **End of life.** Retire an endpoint or a feature with notice: deprecate, switch the flag off, remove the code, then drop its data per the retention rules.

## Checklist per release
- [ ] Every change in scope has an approved CR; RTM and contract updated
- [ ] No breaking change within an API version; deprecations announced with dates
- [ ] Regression suite and affected NFR tests passed on staging
- [ ] Migrations expand-only, rehearsed and timed; pending contract steps tracked
- [ ] Dependencies and base image current; no unaccepted high or critical findings
- [ ] Release checklist completed; staged rollout with halt criteria

## Pitfalls
- **Hotfixes that skip tests** and cause the next incident.
- **Silent breaking changes,** such as a tighter validation rule or a renamed error code, that only an old client notices.
- **Never finishing the contract step,** so old columns and code paths pile up.
- **Letting dependencies and the JDK age** until one update becomes a migration project.
- **Alert fatigue:** alerts nobody acts on, until the real one is missed.
- **Docs and runbooks that stop matching the system** after the first year.
