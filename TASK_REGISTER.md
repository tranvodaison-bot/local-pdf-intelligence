# Task register

| ID | Task / module | Priority | Status | Dependency | Acceptance / evidence |
|---|---|---|---|---|---|
| P0-00 | Audit baseline | P0 | IN_PROGRESS | None | Manifest inventory and gap register |
| P0-01 | SQLite migration | P0 | IN_PROGRESS | P0-00 | Transaction, idempotency, checksum and rollback tests |
| P0-02 | API authentication | P0 | IN_PROGRESS | P0-01 | Local access and rejection tests; desktop handshake remains |
| P0-03 | Trusted PDF picker and import | P0 | BLOCKED | Desktop IPC, parser license | Source hash unchanged; scoped capability and bbox tests |
| P0-04 | PDF viewer and citation | P0 | BLOCKED | P0-03, Tauri toolchain | Actual Windows E2E, rotation/crop tests |
| P0-05 | OCR, RAG and evidence validator | P0 | NOT_STARTED | P0-03, P0-04 | Golden cases and fail-closed citations |
| P0-06 | Backup, offline and release | P0 | NOT_STARTED | P0-01–05 | Windows acceptance and license evidence |

## CTO-001 execution

| ID | Task / module | Priority | Status | Dependency | Acceptance / evidence |
|---|---|---|---|---|---|
| CTO-001-G0 | Audit handoff and remote | P0 | VERIFIED | Remote read | `docs/governance/BASELINE_AUDIT.md` |
| CTO-001-IMPORT | Local CLI registration prototype | P0 | IN_PROGRESS | SQLite, pypdf | 12 tests in `docs/evidence/CTO-001-tests.txt`; trusted picker and race hardening outstanding |
| CTO-001-API | Auth and local-only health | P0 | IN_PROGRESS | Session token | TestClient and live loopback socket tests; Tauri handoff not verified |
| CTO-001-VIEWER | Tauri, React and PDF.js viewer | P0 | IN_PROGRESS | Trusted picker and backend integration | Windows exe built and process starts; browser synthetic PDF smoke passed; native Tauri interaction not tested |
| CTO-001-CI | CI lint/typecheck and tests | P1 | NOT_STARTED | Controlled dependency provisioning | No CI evidence |

## CTO-002 — Foundation recovery

| ID | Task / module | Priority | Status | Dependencies | Evidence / remaining acceptance |
|---|---|---|---|---|---|
| CTO-002-01 | Sidecar protocol and local auth | P0 | IN_PROGRESS | Tauri lifecycle, bundled runtime | Actual subprocess starts on loopback, token via stdin and EOF shutdown tested; Tauri integration not implemented |
| CTO-002-02 | Workspace API and persistence | P0 | IN_PROGRESS | Sidecar database configuration | Authenticated list/create and sidecar restart tests; document metadata and pagination missing |
| CTO-002-03 | PDF viewer text search | P0 | IN_PROGRESS | Tauri picker/backend | Browser synthetic PDF search smoke passed; native E2E and backend integration missing |
| CTO-002-04 | Backup/restore baseline | P1 | IN_PROGRESS | Backup manifests and source relinking | SQLite snapshot to new file and CLI tests pass; no encryption/manifest/source assets |
| CTO-002-05 | CI and dependency inventory | P1 | IN_PROGRESS | License/SBOM review | Windows CI passed for e1f99af; 526 provisional components, 420 unknown licenses |
| CTO-002-G1 | Foundation acceptance | P0 | BLOCKED | 01–05 and native Windows E2E | NOT_ACCEPTED: picker, desktop integration, real-source E2E, evidence and security remain |
