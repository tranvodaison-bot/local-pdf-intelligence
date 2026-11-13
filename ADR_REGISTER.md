# ADR register

| ID | Status | Decision | Source |
|---|---|---|---|
| ADR-001–007 | PROPOSED | Baseline architecture, storage, source integrity, citations, local model, parser license, offline scope | `docs/10_ADR_AND_RISKS.md` |
| ADR-008 | ACCEPTED (foundation only) | Transactional migration checksum ledger; no silent adoption | `DECISION_LOG.md` |
| ADR-010 | ACCEPTED for prototype | Document structured 401/403 health errors and fail closed for browser Origin; Tauri origin policy remains pending. | `contracts/openapi.yaml` |
| ADR-009 | ACCEPTED for prototype | Local CLI may pass an absolute selected path to the registration service; HTTP does not accept paths. Use pypdf for structural checks; keep version PENDING. No desktop or parser license release approval is implied. | This register |

ADR-009 rationale: permit measurable read-only registration before Tauri capability handoff exists. Alternatives: wait for desktop or accept unrestricted HTTP paths; latter violates the security boundary. The CLI is not a replacement for the desktop permission model. Security limitations: a concurrent local actor could race path replacement; file identity and transactional filesystem guarantees require further design/testing before claiming source immutability against adversaries. All API, UI, data, migration and test changes require review if the contract changes.
