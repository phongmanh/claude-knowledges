# Phase 6: Deployment
**Gate:** G6 Launch accepted
**Deliverables:** completed [release checklist](../templates/release-checklist.md), rollout record, runbooks, handover pack
**Load:** [deployment-operations](../reference/deployment-operations.md), [performance-reliability](../reference/performance-reliability.md#observability), [security-privacy](../reference/security-privacy.md#privacy)

## Goal
Put the approved image into production safely and in stages, watch it, and hand it over to the team that runs it.

## Entry criteria
- G5 approved, with the go decision recorded.
- Production infrastructure exists as code and has been reviewed; access to deploy is limited to the pipeline and named people.
- The on-call owner is named and has access to dashboards, logs and runbooks.

## Activities
1. **Image and configuration.**
   - Deploy the exact image digest that passed G5. Never rebuild.
   - Production configuration and secrets are in place in the platform and the secret manager; values reviewed by a second person.
   - Development mode and API docs are off, unless the docs are intended to be public.
2. **Production readiness.**
   - Replicas, probes, resources, autoscaling and the disruption budget as designed.
   - Backups enabled and a restore tested on this environment's backups.
   - Dashboards, SLO alerts and runbooks live; the alert routing reaches the on-call owner.
   - Rate limits and quotas set for launch traffic.
   - DNS, TLS certificates (and their renewal), the ingress or gateway and the WAF configured.
3. **Database migrations.**
   - Run the migration job before the rollout, from the same image.
   - Watch for locks and duration; stop and follow the runbook if it exceeds the rehearsed time.
   - Migrations in this release are expand-only; the contract step is scheduled for a later release.
4. **Rollout through stages,** with the strategy from the architecture:
   - canary (e.g. 5% → 25% → 50% → 100%, with a hold of at least 30 minutes, or one traffic peak, per step), or
   - rolling with readiness gates, or
   - blue-green with a switch and the old environment kept for a quick switch back.

   New behaviour stays behind feature flags and is turned on gradually, by percentage, tenant or client version.
5. **Halt criteria**, agreed before the rollout starts. For example:
   - 5xx rate above 0.5% for 5 minutes;
   - p99 latency above the SLO threshold;
   - error-budget burn rate above 10× over a 10-minute window;
   - a new S1 defect;
   - a key business metric drops by more than an agreed percentage.

   On a halt:
   1. Stop the rollout.
   2. Turn off the feature flag if one isolates the problem.
   3. Otherwise roll back to the previous image digest (the schema stays compatible).
   4. Fix forward with a new RC through a G5-lite.
6. **Client coordination.** If clients depend on new endpoints, the server version ships and is stable first; then the client releases. Communicate deprecations with dates.
7. **Hypercare** (e.g. 1–2 weeks).
   - Review SLOs, error rates, latency, resource use, slow queries and support tickets every day.
   - Keep the on-call owner and a developer who knows the release available.
8. **Handover** to the operations owner:
   - runbooks for each alert, deploys, rollbacks, migrations, secret rotation, scaling and restores;
   - dashboards and alert owners;
   - the capacity model and the next review date;
   - open defects, known limitations and the contract-migration steps still to run.
9. **Close.**
   - Finish the RTM (requirement → release).
   - Record lessons learned.
   - Archive the baselines.

## Exit checklist (G6)
- [ ] Rollout reached 100% with no halt criteria hit, or every halt resolved
- [ ] SLOs and business metrics within target during hypercare
- [ ] Backups running and a restore verified in production
- [ ] Dashboards, alerts and runbooks live and owned
- [ ] Handover accepted by the operations owner
- [ ] RTM closed; lessons learned recorded

## Pitfalls
- **Rebuilding the image for production,** so what runs isn't what was tested.
- **Migrating and switching code in one step,** so a rollback finds a schema the old code can't read.
- **Inventing halt criteria** after things have gone wrong.
- **Releasing the client before the server** it needs is stable.
- **No kill switch** for a risky feature.
- **Hypercare without owners,** so warnings pile up in a channel nobody reads.
