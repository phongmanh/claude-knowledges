# Software Requirements Specification: <System or feature name>

| Version | Status | Owner | Approvers | Last updated |
|---|---|---|---|---|
| 0.1 | Draft | <PO / BA> | <PO, tech lead(s), QA lead, security/privacy> | YYYY-MM-DD |

> Structure follows ISO/IEC/IEEE 29148. Write *what* the system does and *how well*, not *how* it does it.
>
> Every requirement has:
> - a unique ID;
> - a priority (MoSCoW);
> - a source;
> - acceptance criteria.
>
> Mark unknowns `TBD-<n>`. A Must requirement can't be approved while it has an open TBD.

## 1. Introduction
### 1.1 Purpose and scope
### 1.2 Definitions
See Appendix A (glossary).

### 1.3 References
Charter, regulations, standards, existing system documentation.

## 2. Overall description
### 2.1 Product perspective
The system's context: users and external systems. For a feature, the existing system it extends.

### 2.2 User classes and personas
### 2.3 Operating environment
| Platform | Versions / support matrix | Notes |
|---|---|---|
| Mobile | e.g. iOS ≥ x, Android ≥ y; phones, tablets | |
| Web | e.g. last 2 versions of evergreen browsers | |
| Backend | hosting/region constraints | |

### 2.4 Constraints
Regulatory, technical and business.

### 2.5 Assumptions and dependencies

## 3. Functional requirements
Group by feature or use case.

### FR-001 <Short name>
- **Description:** The system shall …
- **Rationale / source:** OBJ-x, a stakeholder, or a regulation
- **Priority:** Must / Should / Could / Won't
- **Acceptance criteria:**
  - Given … When … Then …
  - Given <error / offline / no permission> … When … Then …
- **Notes:** business rules (BR-x), related use case (UC-x)

## 4. External interface requirements
### 4.1 User interfaces
Link the wireframes. State the accessibility expectations.

### 4.2 Software interfaces
External systems and third-party APIs, including their limits.

### 4.3 Hardware and device interfaces
Camera, GPS, biometrics, …

### 4.4 Communication interfaces
Push notifications, email, SMS, webhooks.

## 5. Non-functional requirements
Pattern: `NFR-<ATTR>-nn: <component> shall <measurable behaviour> under <condition>, measured by <method>.`
See the quality-attributes practice file in the waterfall-sdlc skill for example targets.

**Top quality goals (ranked):** 1. … 2. … 3. …

| ID | Attribute | Requirement (target + condition) | Measurement method | Platform | Priority |
|---|---|---|---|---|---|
| NFR-PERF-01 | Performance | | | | |
| NFR-SCAL-01 | Scalability | | | | |
| NFR-AVAIL-01 | Availability / reliability | | | | |
| NFR-MAINT-01 | Maintainability | | | | |
| NFR-TEST-01 | Testability | | | | |
| NFR-A11Y-01 | Accessibility | e.g. All user interfaces conform to WCAG 2.2 AA | Accessibility audit | All UIs | Must |
| NFR-COMPAT-01 | Compatibility | | | | |
| NFR-OBS-01 | Observability | | | | |
| NFR-I18N-01 | Internationalisation | | | | |
| NFR-COST-01 | Cost | | | | |

Security and privacy NFRs (`NFR-SEC-nn`, `NFR-PRIV-nn`) go in §6.

## 6. Security and privacy requirements
- **Verification standard:**
  - Web/API: OWASP ASVS level <L1 / L2 / L3>.
  - Mobile: OWASP MASVS with MASTG profile <L1 / L2, + R>.
- **Data classification and PII inventory:** see §7.
- **Authentication and sessions:** …
- **Authorisation (role × permission matrix):**

| Role | Operation / resource | Allowed | Conditions (e.g. own records only) |
|---|---|---|---|

- **Audit logging:** which events are logged, and for how long they're kept.
- **Encryption:** in transit, at rest, and for any special fields.
- **Privacy:**
  - lawful basis or consent for each purpose;
  - data-subject rights (access, export, deletion);
  - retention;
  - cross-border transfers;
  - reference to the DPIA.
- **Abuse cases:** …
- **Compliance mapping:**

| Regulation / policy | Clause | Requirement ID(s) |
|---|---|---|

## 7. Data requirements
| Entity | Key attributes | Classification | PII? | Volume / growth | Retention & deletion | Source / migration |
|---|---|---|---|---|---|---|

## 8. Platform-specific requirements
Use the checklists in `phases/1-requirements.md` of the waterfall-sdlc skill. For each item, write a requirement or "Not needed".

### 8.1 Mobile
Offline behaviour, sync and conflicts, background work, push notifications, permissions, deep links, budgets, update policy, store requirements.

### 8.2 Frontend
Browser matrix, Core Web Vitals targets, SEO, PWA/offline, consent.

### 8.3 Backend
Load profile, latency, SLO, RPO/RTO, consistency, tenancy, jobs, integrations, audit, data residency.

## 9. Out of scope

## 10. Open issues
| ID | Question / TBD | Blocks (req IDs) | Owner | Due |
|---|---|---|---|---|

## Appendix A: Glossary
## Appendix B: Domain model and state diagrams
## Appendix C: Use cases, user journeys, wireframes

## Approval
| Name | Role | Decision | Date |
|---|---|---|---|
