# Phase 6: Deployment & transition
- **Gate:** G6 Operational acceptance & closure
- **Deliverables:** release runbook, [release checklist](../templates/release-checklist.md) with the go/no-go record, handover pack

## Goal
Release to production safely: monitoring verified, rollback rehearsed, users barely affected. Then hand over cleanly to operations and support, and close the project.

## Entry criteria
- G5 approved (release readiness), with the go decision recorded.
- Change approval obtained, if the organisation requires a change advisory board (CAB).
- Release window agreed with stakeholders and support.

## Activities
1. **Release plan and runbook.**
   - Write it step by step. Each step has an owner, timing, the command or action, a verification, and its rollback step.
   - Rehearse the whole runbook in staging (a "dress rehearsal"). The first deployment must not happen on launch day.
2. **Versioning and notes.**
   - Use semantic versioning for APIs and libraries.
   - Use a monotonic build number for mobile apps.
   - Write user-facing and internal release notes.
3. **Artifacts.**
   - Build once, then promote the **same signed artifact** through every environment.
   - Archive its SBOM and build provenance.
4. **Configuration.**
   - Set per-environment config and secrets through the secret manager.
   - Decide the default for each feature flag.
   - Test the kill switches.
5. **Data.**
   - Take a backup before any migration, and verify that it restores.
   - Rehearse the migrations and measure how long they take.
   - Run data migrations with reconciliation checks.
6. **Monitoring readiness.** Have these live **before** go-live:
   - dashboards, SLO tracking, alerts and synthetic checks;
   - a confirmed on-call schedule and escalation path;
   - an incident channel.
7. **Support readiness.**
   - Support staff are trained.
   - Knowledge-base articles and FAQs are written.
   - The escalation path (L1 → L2 → L3) is defined.
   - The status page and user help/docs are ready.
8. **Legal readiness.** Update the privacy policy and terms, the store privacy disclosures, the cookie banner and the accessibility statement.
9. **Go/no-go meeting.**
   - Use [templates/release-checklist.md](../templates/release-checklist.md).
   - **Agree the rollback triggers in advance**, so nobody debates them at 2 a.m. Examples: error rate > 2% for 10 min, p95 latency > 1.5× target, crash-free users < 99.5%.
10. **Go-live.**
    - Execute the runbook.
    - Verify with smoke tests, synthetic transactions, dashboards and key business metrics.
    - Keep stakeholders informed of status.
11. **Hypercare** (e.g. 1–2 weeks).
    - Monitoring is heightened, and incidents and feedback are triaged daily.
    - Fixes have a fast-track path.
    - The project team is on call alongside operations.
12. **Handover to operations.**
    - Runbooks: deploy, rollback, scale, restore, and the top known incidents.
    - Architecture and operations docs.
    - Ownership of the SLOs and alerts.
    - Access transferred **through the secret manager and access management, never in documents or chat**.
    - The known-issues list and the support model.
13. **Closure.**
    - Hold a lessons-learned session: what to keep, and what to change in this workflow.
    - Write the closure report.
    - Archive the project baseline.

## Platform specifics

### Mobile: an installed binary can't be rolled back
- **Release path:** internal → closed testing → (open testing) → production tracks.
- **Staged or phased rollout** (e.g. 1% → 5% → 20% → 50% → 100%). Halt it if crash rate, ANRs/hangs or key metrics cross agreed thresholds.
- **The real rollback tools are server-side:**
  - feature flags, remote config and kill switches;
  - a backend that stays compatible with older app versions;
  - a forced-update path (minimum supported version) for critical fixes.
- **Store listing:** for each locale, prepare screenshots, descriptions, privacy disclosures and the age rating. Submit early: review takes time and can end in rejection.
- **Signing and symbols:** use store-managed app signing, and back up the upload key securely. Upload symbol and mapping files so crash reports can be de-obfuscated.

### Frontend
- **Atomic deploys:** upload all of a version's assets before switching traffic to it.
- **Caching:**
  - content-hashed, immutable assets with long cache lifetimes;
  - HTML with a short cache;
  - CDN invalidation for the entry points.
- **Keep the previous version's chunks available** for a while, so sessions that are already open don't break.
- **Gradual rollout:** canary or percentage rollout through flags or edge routing, where available.
- **Rollback:** re-point to the previous build.
- **After release,** watch real-user monitoring closely (Core Web Vitals, JavaScript errors).

### Backend
- **Zero-downtime strategy:** rolling, blue-green, or **canary with automated rollback** when SLOs or the error rate regress.
- **Database changes** use **expand/contract**, so the old and new versions run side by side. Run destructive steps only after the new version is stable.
- **Infrastructure changes** go only through the IaC pipeline.
- **After each deploy,** run smoke tests and synthetic transactions.
- **Rollback** means redeploying the previous artifact. This is safe because migrations are backward compatible.

## Deliverables
- Release plan and runbook (rehearsed); release notes.
- The completed release checklist and the go/no-go decision record ([templates/release-checklist.md](../templates/release-checklist.md)).
- Deployment log; post-deployment verification report.
- Handover pack:
  - runbooks;
  - operations docs;
  - SLOs and alert ownership;
  - known issues;
  - the support model.
- Hypercare report, lessons learned, closure report.

## Exit gate checklist (G6)
- [ ] Deployed to production per the runbook; post-deployment verification passed
- [ ] Stable through hypercare; SLOs met; no open S1/S2 production defects
- [ ] Monitoring, alerting and on-call working; any incidents closed with postmortems
- [ ] Operations and support have accepted the handover pack
- [ ] Access and credentials transferred through the proper systems
- [ ] Lessons-learned session held
- [ ] Sponsor has signed project closure; production baseline archived

## Pitfalls
- **The first production deployment happens on launch day**, with no rehearsal.
- **Irreversible migrations** that make rollback impossible.
- **Monitoring and alerts set up after launch**, so users report the first incident.
- **No time budgeted for store review**, so a rejection delays the launch.
- **Secrets pasted** into handover documents or chat.
- **A big-bang release to 100% of users** with no flags and no staged rollout.
