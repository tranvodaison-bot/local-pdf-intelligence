# ADR register

| ID | Status | Decision | Source |
|---|---|---|---|
| ADR-001–007 | PROPOSED | Baseline architecture, storage, source integrity, citations, local model, parser license, offline scope | `docs/10_ADR_AND_RISKS.md` |
| ADR-008 | ACCEPTED (foundation only) | Transactional migration checksum ledger; no silent adoption | `DECISION_LOG.md` |
| ADR-012 | ACCEPTED for prototype | Annotate OpenAPI draft routes by implementation status; only health is implemented. | `contracts/openapi.yaml` |
| ADR-011 | ACCEPTED for isolated prototype | Use an OS file input for a session-only PDF.js viewer; no HTTP file paths or document persistence. Native capability and backend handoff remain open. | `apps/desktop` |
| ADR-010 | ACCEPTED for prototype | Document structured 401/403 health errors and fail closed for browser Origin; Tauri origin policy remains pending. | `contracts/openapi.yaml` |
| ADR-009 | ACCEPTED for prototype | Local CLI may pass an absolute selected path to the registration service; HTTP does not accept paths. Use pypdf for structural checks; keep version PENDING. No desktop or parser license release approval is implied. | This register |

ADR-009 rationale: permit measurable read-only registration before Tauri capability handoff exists. Alternatives: wait for desktop or accept unrestricted HTTP paths; latter violates the security boundary. The CLI is not a replacement for the desktop permission model. Security limitations: a concurrent local actor could race path replacement; file identity and transactional filesystem guarantees require further design/testing before claiming source immutability against adversaries. All API, UI, data, migration and test changes require review if the contract changes.

ADR-011 does not replace the trusted desktop capability required by G1. The viewer reads user-selected bytes for rendering, does not register the file and has no citation navigation. Browser smoke evidence is distinct from native Tauri end-to-end evidence. Production security, licensing and error recovery remain to be reviewed.

## ADR-013 — Workspace API increment (CTO-002)
Status: ACCEPTED for development. Add authenticated list/create routes backed by an existing locally configured SQLite database; the client cannot choose filesystem paths. New workspace IDs use UUID4. No schema migration required. Pagination and the Tauri-to-sidecar lifecycle remain outstanding. Restore is available only to a new database file through the local CLI, not as an HTTP operation.
