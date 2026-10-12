# Phase 1: Requirements analysis & specification
- **Gate:** G1 Requirements baseline (SRR)
- **Deliverables:** [SRS](../templates/srs.md), [RTM](../templates/rtm.md) v1, acceptance test plan (draft)

## Goal
Produce a complete, unambiguous, testable and prioritised specification of **what** the system must do and **how well**. Get it approved and baselined, so the later phases build on stable ground.

## Entry criteria
- G0 approved and the charter baselined.
- Stakeholders available for elicitation.

## Activities
1. **Elicitation.** Use several techniques; each one finds different things.
   - Interviews and workshops with every stakeholder group, including support, operations and legal.
   - Observing users at work.
   - Reviewing existing documents, systems, analytics, support tickets and competitors.
   - Personas, user journeys and task analysis (UX).
   - Throwaway wireframes or clickable prototypes. Use them **to check that you've understood the need**, not to design the final UI.
2. **Functional requirements.**
   - Write each one as a use case (actor, preconditions, main flow, alternate and exception flows, postconditions) or as a user story. Either way, give it an ID `FR-nnn` and acceptance criteria in Given/When/Then form.
   - Cover the unhappy paths: invalid input, no network, permission denied, timeouts, empty data, concurrent edits.
   - Keep a catalogue of business rules.
   - Build a domain model and glossary with one name per concept. These names become the vocabulary of the code.
   - Draw state diagrams for any entity with a lifecycle (order, payment, account).
   - List the external interfaces: other systems, third-party APIs, devices, files.
   - Capture data requirements:
     - entities and volumes;
     - **classification** (public, internal, confidential, restricted);
     - a **PII inventory**;
     - retention and deletion rules;
     - legacy data to migrate.
   - Include admin, support and reporting needs. Back-office users are users too.
3. **Non-functional requirements (NFRs).**
   - Specify every attribute that matters, using the pattern and example targets in [practices/quality-attributes.md](../practices/quality-attributes.md): performance, scalability, availability, security, privacy, maintainability, testability, accessibility, compatibility, observability, i18n and cost.
   - Give each NFR an ID, a measurable target, the conditions under which it applies, and how it will be measured. "Fast" is not an NFR; "Search API p95 ≤ 300 ms at 500 requests/s" is.
   - Agree the **top 3–5 quality goals**, in priority order. They drive the architecture in Phase 2 and settle trade-offs.
4. **Security and privacy requirements.**
   - Choose the verification standard and level:
     - **OWASP ASVS** level (L1–L3) for web and APIs.
     - **OWASP MASVS** with a MASTG testing profile (L1 or L2, plus R for resilience if needed) for mobile.
   - Write abuse and misuse cases for sensitive features: account takeover, scraping, payment fraud, data exfiltration.
   - Set the access-control requirements:
     - Authentication and session rules, e.g. per NIST SP 800-63B: MFA for privileged users, no forced periodic password changes, checks against breached-password lists.
     - A role/permission matrix.
     - Audit-logging needs.
     - Encryption requirements.
   - Privacy requirements: the lawful basis or consent for each purpose, data minimisation, data-subject rights (access, export, deletion), retention periods and cross-border transfers. Run a DPIA when the processing is high-risk.
   - Map each applicable regulation and store policy to concrete requirements with IDs, so they're traced and tested like everything else.
5. **Prioritise with MoSCoW** (Must, Should, Could, Won't this time). Trace every requirement to a charter objective. A requirement with no objective is a candidate for removal (YAGNI).
6. **Quality review.** Inspect the SRS against the ISO/IEC/IEEE 29148 characteristics: each requirement must be necessary, unambiguous, complete, singular, feasible, verifiable, correct, consistent and traceable.
   - Hunt down weak words: "fast", "easy", "user-friendly", "flexible", "robust", "support", "etc.", "and/or", "as appropriate", "if possible".
7. **V-model: acceptance test plan.** From the acceptance criteria, draft the UAT plan (scenarios, data, who accepts) and the scope of OAT. Every Must requirement has at least one acceptance scenario.
8. **RTM v1.** Every requirement is in [rtm.md](../templates/rtm.md) with its ID, source, priority and acceptance criteria.
9. **Baseline.** Once approved, tag the SRS (e.g. `baseline/G1-srs-v1.0`). From then on, changes go through [change control](../governance.md#change-control).

## Platform specifics
Use these as completeness checklists. Each item becomes a requirement, or an explicit "not needed".

### Mobile
- Platforms and minimum OS versions (decide from your target audience's device data).
- Device classes (phone, tablet, foldable), orientation, multi-window.
- Offline behaviour **for each feature**: read-only? queued writes?
- Sync frequency, and the conflict policy (last write wins, merge, or the user resolves).
- Background work (sync, uploads, location) within OS limits.
- Push notifications: types, opt-in, preferences.
- Permissions: which are needed, why, and what happens when they're denied.
- Deep links and universal links.
- Budgets for download size, cold-start time, and battery and data use (e.g. "cold start ≤ 2 s on the reference low-end device").
- Accessibility: screen readers, system font scaling, contrast.
- Localisation, including right-to-left languages.
- In-app purchases and subscriptions (store billing rules).
- Store privacy disclosures, and **in-app account deletion** if the app has sign-up.
- Update policy: minimum supported app version, forced vs. flexible updates.
- Tracking consent (e.g. App Tracking Transparency on iOS).

### Frontend
- Browser and device support matrix (e.g. the last two versions of evergreen browsers, plus specific mobile browsers).
- Responsive breakpoints.
- Core Web Vitals targets at p75 for key pages: LCP ≤ 2.5 s, INP ≤ 200 ms, CLS ≤ 0.1.
- SEO: which pages must be indexable, their metadata, sharing previews.
- Accessibility: WCAG 2.2 AA as the default bar.
- i18n: locales, currencies, date and number formats, RTL.
- Offline or installable (PWA) needs, if any.
- Session timeout behaviour.
- Cookie consent and tracking rules for each region.

### Backend
- Consumers: which clients (mobile, web, partners, internal) call the API, and their usage patterns.
- Load profile: users, daily active users, peak requests per second, seasonal peaks, growth over 1–3 years.
- Latency targets (p95/p99) for each class of operation.
- Availability SLO, RPO and RTO.
- Data volume, growth and retention.
- Consistency needs for each domain (strong vs. eventual).
- Multi-tenancy and isolation.
- Batch and scheduled jobs; reporting and exports.
- Integrations: third-party SLAs, rate limits, behaviour on failure; webhooks in and out.
- Audit-trail requirements, data residency, back-office and admin operations.

## Deliverables
- **SRS** ([templates/srs.md](../templates/srs.md)): functional requirements with acceptance criteria, the NFR table, security and privacy requirements, data requirements, the platform checklists and a glossary.
- **UX artifacts**: personas, journeys, wireframes and prototypes, linked from the SRS.
- **DPIA**, if one is required.
- **Acceptance test plan** (draft), as a section of [templates/test-plan.md](../templates/test-plan.md).
- **RTM v1** ([templates/rtm.md](../templates/rtm.md)).

## Exit gate checklist (G1)
- [ ] Every requirement has an ID, source, priority and acceptance criteria
- [ ] Unhappy paths, admin/support needs and data requirements are covered
- [ ] Every NFR is measurable (target, condition, method); top quality goals are ranked
- [ ] Security standard and level chosen (ASVS / MASVS)
- [ ] Privacy and compliance requirements captured; DPIA done if required
- [ ] No open TBD on any Must requirement
- [ ] SRS inspected against the ISO/IEC/IEEE 29148 characteristics; weak words removed
- [ ] Acceptance test plan drafted; every Must requirement has an acceptance scenario
- [ ] RTM v1 complete
- [ ] Signed off by the PO, tech lead(s) and QA lead, plus security/privacy when data is sensitive
- [ ] Baseline tagged

## Pitfalls
- **Vague NFRs** ("scalable", "secure") that can't be designed for or tested.
- **Specifying only the happy paths**, forgetting offline, errors, empty states and permissions.
- **Forgetting actors**: admins, support staff, operations, auditors.
- **Hidden legacy data migration** that only surfaces in Phase 5.
- **Solution details inside requirements** ("use a queue"). Keep the SRS about *what*, not *how*, unless it's a genuine constraint.
- **Gold plating**: requirements nobody asked for and no objective needs.
