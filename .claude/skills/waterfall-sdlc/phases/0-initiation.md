# Phase 0: Initiation & planning
**Gate:** G0 Charter approved
**Deliverables:** [charter](../templates/charter.md), project plan, [STATUS.md](../templates/status.md) with the risk register

## Goal
Decide whether the application or feature is worth building, draw its boundaries, and set up how the project will be run and controlled.

## Entry criteria
- A business need, opportunity or idea is written down.
- A sponsor who can commit budget and people has been named.

## Activities
1. **Problem and objectives.**
   - Write the problem statement: who has the problem, how it shows today, and what it costs to leave it unsolved.
   - Write objectives in SMART form, each with a KPI and a target (e.g. "cut checkout abandonment from 70% to 55% within 6 months of launch"). Every later requirement must trace back to one of these objectives.
2. **Stakeholders.** List them and map them on a power/interest grid: users, customers, business owners, operations, support, security, legal/DPO, regulators and third-party providers. A missing stakeholder becomes a missing requirement later.
3. **Scope.**
   - Write in-scope and out-of-scope lists. Explicit exclusions prevent scope creep later.
   - Name the platforms in scope: mobile (iOS, Android), web frontend, backend/API, admin and back-office tools.
   - For a feature, name the parts of the existing system it touches.
4. **Feasibility.** Summarise each area in the charter:
   - **Technical:** the known unknowns that need a spike or proof of concept in Phase 2, and dependencies on other systems.
   - **Economic:** development cost *and* total cost of ownership (hosting, licences, third-party APIs, support, maintenance). Over a system's life, maintenance often costs more than the first build.
   - **Legal and compliance:** data protection (GDPR, CCPA/CPRA), sector rules (HIPAA, PCI-DSS), accessibility law (e.g. the European Accessibility Act, the ADA), app store policies, licensing and data residency.
   - **Operational:** who will run, support and pay for the system after launch.
   - **Schedule:** hard deadlines, and the reason behind each one.
5. **Estimate.** Give top-down ranges for now and refine them at every gate. Use three-point estimates (optimistic, most likely, pessimistic) and state your confidence. A single number at this stage is false precision.
6. **Project plan.**
   - A work breakdown structure (WBS) by phase and deliverable.
   - A schedule with the gates as milestones, the critical path, and a resource plan.
   - **Protect the test window (Phase 5).** Overruns squeeze it first.
   - Roles and RACI (see [governance](../governance.md#roles-and-raci)), a communication plan, a quality plan (reviews, metrics), and a configuration-management plan (repository, where the docs live, how baselines are tagged).
7. **Risk register.** Start it in STATUS.md with the top risks, each with an owner (see [risk management](../governance.md#risk-management)).
8. **Workspace.** Create `docs/sdlc/<initiative>/` containing STATUS.md and an empty RTM.

## Platform specifics
### Mobile
- Register the store developer accounts in the company's name. Organisation enrolment and verification can take weeks.
- Decide who owns the signing keys and store accounts. It should be the company, not an individual.
- Budget for a device lab or device cloud, and for test devices that cover the low end of the target audience.
- Check early for store policies that shape scope:
  - in-app purchase rules for digital goods;
  - in-app account deletion whenever the app offers sign-up;
  - privacy disclosure forms;
  - content and age-rating rules.
- Budget for both a native and a cross-platform option. The choice is made in Phase 2.
### Frontend
- Domains, TLS certificates, hosting and CDN costs.
- SEO and marketing needs: public pages, campaigns, analytics.
- Whether a brand guide or design system already exists. If not, building one is a scope item.
- Legal texts: privacy policy, cookie policy, terms of service, accessibility statement.
### Backend
- Constraints on the hosting model (cloud, on-premises, regions) and on data residency.
- The third-party services the system will depend on: their cost, SLAs, rate limits and contract terms.
- What the business expects for availability and support hours. These become SLOs in Phase 1.
- Existing systems to integrate with or migrate from. Legacy data is a common hidden cost.

## Deliverables
- **Project charter or feature brief**, including the feasibility summary ([templates/charter.md](../templates/charter.md)).
- **Project plan**: WBS, schedule with gates, RACI, and the communication, quality and configuration-management plans. For a feature, these can be sections of the charter.
- **STATUS.md** with the initial risk register ([templates/status.md](../templates/status.md)).

## Exit gate checklist (G0)
- [ ] Problem statement and SMART objectives with KPIs agreed with the sponsor
- [ ] In-scope and out-of-scope lists and the platforms in scope written down
- [ ] Feasibility summarised (technical, economic, legal, operational, schedule), with no blocker left unaddressed
- [ ] Budget and team committed for at least Phases 1–2
- [ ] Plan has the gates as milestones and a protected test window
- [ ] Top risks recorded, each with an owner
- [ ] Workspace and STATUS.md created; sponsor sign-off recorded

## Pitfalls
- **Picking the solution first** ("we need microservices", "we need an app") before the problem is understood. Keep the charter solution-neutral.
- **Objectives that can't be measured**, so success can never be shown.
- **Counting only the build cost** and forgetting running, support and maintenance.
- **Not budgeting lead time** for store accounts, store review, security review or legal sign-off.
- **Missing stakeholders** (support, operations, legal) who show up later with new requirements.
