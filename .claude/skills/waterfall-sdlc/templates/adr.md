# ADR-NNNN: <Decision title, e.g. "Use a modular monolith for the backend">

| Status | Date | Deciders | Consulted | Supersedes / superseded by |
|---|---|---|---|---|
| Proposed / Accepted / Deprecated / Superseded | YYYY-MM-DD | <names, roles> | <names, roles> | — |

> - Format based on MADR.
> - Write one decision per ADR.
> - Store it as `docs/sdlc/<initiative>/adr/NNNN-<kebab-title>.md`, or in the project's ADR folder.
> - Once accepted, an ADR is never edited. To change the decision, write a new ADR that supersedes this one.

## Context and problem statement
<What needs deciding, and why now. Link the requirement IDs (e.g. NFR-PERF-01) and the constraints.>

## Decision drivers
- <e.g. NFR-SCAL-01: handle 3× peak load>
- <e.g. team skills, budget, time to market>

## Considered options
1. <Option A>
2. <Option B>
3. <Option C>

## Decision matrix (for technology / stack choices)
- **Weights:** they sum to 100.
- **Scores:** score each option 1–5 on each criterion.
- **Total:** Σ(weight × score).

| Criterion | Weight | Option A | Option B | Option C |
|---|---|---|---|---|
| Fit with NFRs / quality goals | | | | |
| Team skills & hiring market | | | | |
| Maturity, community, long-term support | | | | |
| Security track record & patch cadence | | | | |
| Licence | | | | |
| Total cost (licences, infra, people) | | | | |
| Lock-in & exit path | | | | |
| Testability & tooling | | | | |
| Accessibility support | | | | |
| **Total** | 100 | | | |

PoC results, if any: <the question asked, the result, a link to the report>.

## Decision outcome
Chosen option: **<Option X>**, because <justification tied to the drivers>.

### Consequences
- **Positive:** …
- **Negative / trade-offs accepted:** …
- **Follow-up actions:** …

## Pros and cons of the options
### <Option A>
- Good, because …
- Bad, because …

### <Option B>
- Good, because …
- Bad, because …

## Links
Requirement IDs, related ADRs, PoC reports, references.
