# Release checklist & go/no-go: <release name / version>

| Release | Date / window | Release manager | Platforms |
|---|---|---|---|
| vX.Y.Z | YYYY-MM-DD HH:MM–HH:MM (time zone) | <name> | Mobile / Web / Backend |

## Quality (G5)
- [ ] Test summary report approved, with a Go recommendation
- [ ] No open S1/S2 defects; known issues documented and accepted by the PO
- [ ] Every NFR target met, or waived with a recorded risk acceptance
- [ ] UAT and OAT signed off

## Security
- [ ] No open critical or high findings; the pen test, if required, is closed
- [ ] Artifacts signed; SBOM archived
- [ ] Secrets set for each environment through the secret manager, never in config files or tickets

## Data
- [ ] Backup taken, and verified that it restores
- [ ] Migrations rehearsed with timing measured; backward compatible (expand/contract)
- [ ] Reconciliation plan ready for any data migration

## Operations readiness
- [ ] Runbook rehearsed in staging; every step has an owner and a timing
- [ ] Dashboards, SLO tracking, alerts and synthetic checks live
- [ ] On-call and escalation confirmed for the release window and for hypercare
- [ ] Feature-flag defaults set; kill switches tested

## Platform-specific
### Mobile
- [ ] Store listing, screenshots and release notes ready for each locale
- [ ] Privacy disclosures accurate
- [ ] Submitted for review with time to spare
- [ ] Staged/phased rollout plan and halt criteria defined
- [ ] Symbol and mapping files uploaded
- [ ] Minimum-version / forced-update mechanism verified
- [ ] Backend compatible with every supported app version

### Frontend
- [ ] Atomic deploy with hashed assets; previous chunks retained
- [ ] CDN invalidation planned
- [ ] Real-user monitoring and error tracking tagged with this release

### Backend
- [ ] Deployment strategy chosen (rolling / blue-green / canary), with automated rollback configured
- [ ] Post-deploy smoke tests and synthetic transactions ready

## Support & communication
- [ ] Support trained; knowledge base and FAQ ready; escalation path known
- [ ] Stakeholder and user communications scheduled; status page ready

## Legal
- [ ] Privacy policy, terms, cookie banner and accessibility statement updated where needed

## Rollback
**Triggers** (agreed in advance). For example:
- error rate > 2% for 10 min
- p95 latency > 1.5× target
- crash-free users < 99.5%
- a key business metric drops by more than X%

**Procedure:** <link to the runbook section>. For mobile, halt the rollout and use the kill switch or flags.

## Go / no-go decision
| Name | Role | Vote (Go / No-go) | Comment |
|---|---|---|---|
| | Sponsor / PO | | |
| | QA lead | | |
| | Security | | |
| | DevOps / SRE | | |
| | Release manager | | |

- **Decision:** Go / No-go
- **Date/time:**
- [ ] Decision recorded in the STATUS.md gate log
