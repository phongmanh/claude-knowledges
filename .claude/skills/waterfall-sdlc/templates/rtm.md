# Requirements Traceability Matrix: <Initiative name>

| Version | Last updated | Owner |
|---|---|---|
| 0.1 | YYYY-MM-DD | <PO / QA lead> |

> - **Living document.** Update it at every gate. Completeness is an exit criterion for G1–G5.
> - **Forward:** every requirement → design → code → tests → release.
> - **Backward:** every design element and test → a requirement. An orphan means gold plating or a missing requirement.

## Column guide
| Column | Filled in | Content |
|---|---|---|
| Req ID | Phase 1 | `FR-nnn`, `NFR-<ATTR>-nn` |
| Summary | Phase 1 | One line |
| Source | Phase 1 | Objective (OBJ-x), stakeholder or regulation |
| Priority | Phase 1 | Must / Should / Could / Won't |
| Design ref | Phases 2–3 | Architecture section, ADR, detailed-design section |
| Code ref | Phase 4 | Module, PR or commit |
| Test IDs | Phases 1–5 | Acceptance (AT), system (ST), performance (PT), integration (IT), unit (UT) |
| Result | Phase 5 | Pass / Fail / Blocked / Not run (+ date) |
| Release | Phase 6 | Version it shipped in |
| Status | All | Proposed / Approved / Designed / Implemented / Verified / Released / Changed (CR-x) / Deleted (CR-x) |

## Matrix
| Req ID | Summary | Source | Priority | Design ref | Code ref | Test IDs | Result | Release | Status |
|---|---|---|---|---|---|---|---|---|---|
| FR-001 | e.g. User can save a note while offline | OBJ-1 | Must | architecture §5 (sync); design/notes.md §6 | notes module, PR #42 | AT-003, ST-011, IT-020, UT-104 | Pass (YYYY-MM-DD) | 1.0.0 | Verified |
| NFR-PERF-01 | e.g. Notes list API p95 ≤ 300 ms at 500 requests/s | Stakeholder: operations | Must | architecture §10 (QS-2); ADR-0003 | notes API | PT-002 | Pass (YYYY-MM-DD) | 1.0.0 | Verified |

## Coverage summary (per gate)
| Gate | Requirements total | Fully traced for this gate | Gaps (IDs) |
|---|---|---|---|
| G1 | | | |
| G2 | | | |
| G3 | | | |
| G4 | | | |
| G5 | | | |
