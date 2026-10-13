# Release checklist: <Service> <version> (image <digest>)

| Release owner | Target date | Rollout strategy | G5 decision |
|---|---|---|---|
| <name> | YYYY-MM-DD | Canary / rolling / blue-green | <date, approver> |

## Build
- [ ] Image built by CI from the tag `v<version>`; the digest matches the one tested in G5
- [ ] Image scanned (no unaccepted high or critical findings), signed, SBOM attached
- [ ] Version and commit reported by the service (logs, metrics, `/health` or build info)

## Configuration and infrastructure
- [ ] Infrastructure changes applied through IaC and reviewed
- [ ] Production configuration and secrets in place; reviewed by a second person
- [ ] Development mode off; API docs off unless intended to be public
- [ ] Replicas, probes, resources, autoscaling and disruption budget as designed
- [ ] TLS certificates valid beyond the hypercare period; DNS, ingress and WAF configured

## Database
- [ ] Migrations for this release are expand-only and were rehearsed on production-sized data (duration: <n> min)
- [ ] Backup taken (or PITR confirmed) right before the migration
- [ ] Migration job ready to run from the release image with the DDL user

## Readiness
- [ ] G5 go decision recorded; test summary report approved
- [ ] Feature flags set; kill switches tested
- [ ] Dashboards, SLO alerts and runbooks live; alert routing reaches the on-call owner
- [ ] Client teams informed: new endpoints, deprecations, dates
- [ ] Support team briefed; known issues documented

## Rollout
| Step | Action / traffic share | Earliest time | Halt if… | Decision |
|---|---|---|---|---|
| 1 | Run the migration job | | It fails, or exceeds <n> min, or holds locks > <n> s | |
| 2 | Canary 5% (or the first rolling batch) | | 5xx > <n>% for 5 min; p99 > <n> ms; S1 defect | |
| 3 | 25% | ≥ 30 min after step 2 | Same, plus error-budget burn > <n>× | |
| 4 | 50% | | Same | |
| 5 | 100% | | Same; business metric drop > <n>% | |
| 6 | Turn on the feature flag gradually | | Same | |

On a halt:
1. Stop the rollout.
2. Turn off the feature flag if one isolates the problem.
3. Otherwise redeploy the previous image digest `<digest>`; the schema stays compatible.
4. Fix forward with a new RC through G5-lite.

## Hypercare (<n> days)
- [ ] Daily review of SLOs, errors, latency, saturation, slow queries and support tickets; findings logged

## Handover and sign-off
- [ ] Runbooks (alerts, deploy, rollback, migrations, secret rotation, scaling, restore), dashboards, open defects and known limitations handed over to <operations owner>
- [ ] Contract steps of expand/contract migrations scheduled: <release>
- [ ] RTM closed; lessons learned recorded

| Role | Name | Decision | Date |
|---|---|---|---|
