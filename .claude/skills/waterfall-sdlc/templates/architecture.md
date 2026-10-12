# Software Architecture Document: <System name>

| Version | Status | Owner | Approvers | Last updated |
|---|---|---|---|---|
| 0.1 | Draft | <Architect> | <Architect, tech leads, security, SRE, QA> | YYYY-MM-DD |

> - **Structure:** arc42 (12 sections) with C4 diagrams.
> - **Diagrams:** prefer diagrams as code, stored next to this file.
> - **For a feature:** fill in only what changes (the delta), and link to the current architecture.

## 1. Introduction and goals
- **Requirements overview:** link to the SRS.
- **Top quality goals:** ranked, from SRS §5.
- **Stakeholders:** who they are, and what they expect from the architecture.

## 2. Constraints
Technical, organisational and regulatory constraints, plus conventions.

## 3. Context and scope
- **C4 Level 1, system context:** users, external systems and the data flows between them.
- **Business vs. technical context:** channels and protocols.

## 4. Solution strategy
- **Architecture style** and the reason for it (link the ADR).
- **Technology stack** (link an ADR for each decision):
  - mobile;
  - web;
  - backend;
  - data stores;
  - hosting;
  - CI/CD;
  - observability;
  - identity.
- **Key tactics:** how the top quality goals are achieved.

## 5. Building block view
- **C4 Level 2, containers:** apps, services, databases, queues and third parties, each with its responsibilities and technology.
- **C4 Level 3:** for complex containers, here or in the detailed designs.
- **Data ownership:** which module or service owns which data.

## 6. Runtime view
Sequence diagrams for the key scenarios, **including failure paths**: a dependency is down, a call times out or retries, a client is offline.

## 7. Deployment view
- **Environments:** dev, test, staging, production.
- **Regions and zones.**
- **Network zones and trust boundaries.**
- **Infrastructure as code:** where it lives.
- **Scaling units.**

## 8. Cross-cutting concepts
- **Security:** identity and access, authorisation model, secrets, encryption, and a summary of the threat model (full model in §8.1).
- **Data:** storage choices, consistency, migrations, backup and restore, retention.
- **Integration:** API styles, the versioning and compatibility policy (including old mobile app versions), events.
- **Resilience:** timeouts, retries, circuit breakers, idempotency, degradation.
- **Observability:** logs, metrics, traces, client telemetry, SLOs, alerting, correlation IDs.
- **Error handling and logging:** the error model, and the logging policy (including PII redaction).
- **Configuration:** config, feature flags and secrets for each environment.
- **Other conventions:** i18n, accessibility (design system), time (UTC), IDs, money.
- **Delivery:** CI/CD stages and quality gates, and the release strategy for each platform.

### 8.1 Threat model
Data-flow diagram with trust boundaries, plus STRIDE applied to each element.

| ID | Element / flow | Threat (STRIDE) | Mitigation | Requirement ID | Status |
|---|---|---|---|---|---|

## 9. Architecture decisions
| ADR | Title | Status | Date |
|---|---|---|---|

## 10. Quality requirements
| Scenario ID | Quality goal | Stimulus → Response | Measure | Tactics | NFR IDs |
|---|---|---|---|---|---|

### 10.1 Capacity model
Load assumptions (from the SRS), translated into instances, storage, throughput and headroom.

### 10.2 Cost model
Costs at launch and at the projected scale, plus budget alerts.

## 11. Risks and technical debt
| ID | Risk / debt | Impact | Mitigation | Owner |
|---|---|---|---|---|

## 12. Glossary
Link to the SRS glossary, and add technical terms here.

## Platform sections
### Mobile
- Architecture pattern
- Offline and sync model
- Modularisation
- Compatibility window for older app versions
- Remote config and kill switches
- Push notifications
- Deep links

### Frontend
- Rendering mode for each route
- Design system
- State management
- Session pattern
- Content Security Policy
- CDN and assets
- Performance budgets

### Backend
- Contract format
- Module/service boundaries
- Consistency (outbox, sagas)
- Migrations
- Caching
- Rate limits
- Tenancy
- Health checks, graceful shutdown, autoscaling

## Approval
| Name | Role | Decision | Date |
|---|---|---|---|
