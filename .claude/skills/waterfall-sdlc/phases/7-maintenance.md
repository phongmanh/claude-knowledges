# Phase 7: Operations & maintenance
**Gate:** a small gated cycle for each change
**Deliverables:** SLO reports, [change requests](../templates/change-request.md), postmortems, maintenance releases, end-of-life plan

## Goal
Keep the system reliable, secure, compliant and useful. Evolve it through controlled changes. Retire it cleanly when the time comes.

## Entry criteria
- G6 approved.
- Operations owns the system.
- The support model is live.

## Activities
1. **Operate against SLOs.**
   - Track SLOs and error budgets. When an error budget is spent, reliability work comes before features.
   - Make every alert actionable and link it to a runbook. Review noisy alerts regularly, because alert fatigue hides real incidents.
   - Run an on-call rotation with clear escalation.
2. **Incident and problem management.**
   - Every incident has a severity level, an incident lead, a timeline, and status-page updates.
   - Every significant incident gets a blameless postmortem. Track its action items to completion.
   - Problem management finds and fixes the root causes of recurring incidents.
3. **Capacity, cost and resilience reviews.** Run them on a schedule (e.g. capacity and cost monthly, a restore drill quarterly, a DR exercise yearly):
   - compare real load with the capacity model;
   - right-size resources;
   - prove the backups actually restore.
4. **Security operations.**
   - Set vulnerability remediation SLAs by severity in policy (e.g. critical ≤ 7 days, high ≤ 30 days).
   - Continuously check the deployed SBOMs against newly published vulnerabilities.
   - Patch operating systems, runtimes and base images.
   - Rotate keys and secrets.
   - Review access periodically (e.g. quarterly).
   - Repeat penetration tests periodically (e.g. yearly, or after a major change).
   - Keep a security incident response plan, including breach-notification duties (e.g. under GDPR, notify the authority within 72 hours where required).
5. **Compliance.**
   - Answer data-subject requests within the legal deadlines.
   - Run the retention and deletion jobs.
   - Keep audit evidence, and review policies.
6. **Change management.** Every change is a small waterfall cycle.
   - Classify each change by its maintenance type (ISO/IEC/IEEE 14764):
     - **corrective:** fix defects;
     - **adaptive:** keep up with OS, browser, platform or regulation changes;
     - **perfective:** enhancements and performance;
     - **preventive:** refactoring, upgrades, debt reduction.
   - Flow:
     1. Raise a [change request](../templates/change-request.md).
     2. Analyse its impact using the RTM.
     3. The CCB decides.
     4. Run phases 1–6 at the depth the [tailoring table](../SKILL.md#tailoring-application-vs-feature) sets for a feature. For a small fix, that can be: a spec in the ticket, a design note, the change with its tests, a regression run, and a standard release.
   - Production incidents and security fixes use the emergency path: expedited approval, then a retroactive review (see [governance](../governance.md#change-control)).
7. **Technical debt.**
   - Keep a debt register: item, impact, cost of delay, estimate.
   - Reserve capacity for preventive work (e.g. 15–20% of maintenance effort).
   - Use hotspot analysis (change frequency × complexity) to choose what to fix.
   - Follow the Boy Scout rule: leave the code cleaner than you found it.
8. **Feedback loop.** Support tickets, store reviews, analytics and user research feed the backlog for the next release. That release starts again at Phase 0 or 1.
9. **Keep documents alive.** Every change's Definition of Done includes updating the docs, runbooks and RTM.
10. **Decommissioning**, when the system reaches end of life:
    - Notify users and stakeholders.
    - Export or migrate the data, then delete it according to the retention rules.
    - Revoke keys, certificates, DNS entries and accounts.
    - Remove the store listings.
    - Archive the code and docs.
    - Shut down the infrastructure and billing.
    - Keep the required compliance records.

## Platform specifics

### Mobile
- **Every yearly OS release:** test the betas early, adapt to behaviour changes, and meet the store deadlines for targeting recent OS/SDK versions.
- **Platform changes:**
  - support new devices and form factors;
  - follow store policy updates (privacy, payments, content).
- **Retiring old versions:** use adoption data and the minimum-version mechanism.
- **Expiry dates:** track signing certificates, provisioning profiles and push credentials before they expire.
- **Per release, watch:** the crash-free rate, ANRs/hangs, ratings and reviews.

### Frontend
- Review the browser support matrix against real usage (e.g. twice a year).
- Keep frameworks and dependencies on supported major versions.
- Audit third-party scripts.
- Watch field Core Web Vitals and JavaScript error rates for regressions.
- Automate certificate renewal.
- Re-check accessibility whenever something changes.

### Backend
- **End-of-life dates:** track them for runtimes, frameworks, databases and OS images, and upgrade before support ends.
- **Database health:** watch index usage, bloat and growth. Archive or partition as the data grows.
- **API deprecation lifecycle:**
  1. Announce the deprecation.
  2. Send `Deprecation`/`Sunset` headers.
  3. Monitor usage.
  4. Remove the API.
- **Routine operations:**
  - monitor dead-letter queues and replay messages safely;
  - run retention purges;
  - tune autoscaling.

## Deliverables
- SLO and operations reports; capacity and cost reviews.
- Incident postmortems, with their actions tracked.
- Change requests and maintenance releases, each passing its own small gates.
- Vulnerability and patch reports; access review records.
- The technical debt register; updated docs, runbooks and RTM.
- An end-of-life plan, when relevant.

## Exit gate checklist (per change)
- [ ] CR approved with an impact analysis; tailoring depth agreed
- [ ] Requirements, design and tests updated for the change; RTM updated
- [ ] Regression suite passed; affected NFRs re-verified
- [ ] Release checklist completed; rollback ready
- [ ] Docs and runbooks updated; CR closed after verification in production

## Pitfalls
- **Alert fatigue:** so many alerts that the real ones get ignored.
- **Backups that have never been restored.**
- **Ignoring platform deprecations** until a store or vendor deadline forces a rush.
- **Technical debt that's listed but never scheduled.**
- **Hotfixes that bypass change control** and never get documented.
