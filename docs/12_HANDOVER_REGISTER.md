# 12 — Artifact inventory / evidence register
As of 2026-11-13, all below are specifications, **not executable product features**.
| Artifact | State | Evidence | Next owner |
|---|---|---|---|
| PRD/scope | DRAFT | docs/00_PRODUCT_SCOPE.md | Product owner approve |
| Architecture | PROPOSED | docs/01_ARCHITECTURE.md | Codex ADR review |
| Data schema | PREPARED, syntax check pending | db/001_initial.sql | Codex integrate migrations |
| API contract | STUB | contracts/openapi.yaml | Codex expand/lint |
| AI pipeline | SPECIFIED | docs/04_PROCESSING_AND_AI.md | Codex implement |
| Security/license | PROPOSED | docs/05_SECURITY_AND_LICENSE.md | Review licensing |
| Evaluation | PLAN ONLY | docs/11_EVALUATION_DATASET.md | Assemble corpus |
| Desktop app | NOT STARTED | none | Codex |
| Backend app | NOT STARTED | none | Codex |
| E2E Windows acceptance | NOT RUN | none | QA |
| Installer | NOT STARTED | none | Codex |

Evidence must be updated with logs, commit IDs and screenshots. Never mark CLOSED based only on document existence.

## Foundation work — 2026-11-13

- **IN_PROGRESS:** migration runner and checksum ledger in `apps/api/localpdf/storage.py`; four foundation tests passed as recorded in `TEST_REPORT.md`. Backfill/adoption and reverse migration are not implemented.
- **IN_PROGRESS:** authenticated health route in `apps/api/localpdf/main.py`; exercised with TestClient only. Trusted Tauri token handoff, Origin verification, lifecycle and live loopback testing remain outstanding.
- **BLOCKED / NOT STARTED:** desktop, PDF import/viewer, OCR, RAG, citation resolver, backup/restore and packaging. Rust/Cargo was not found in PATH. No demo screenshot or application E2E evidence exists.
- **NOT SIGNED OFF:** unresolved P0/P1 issues are recorded in `GAP_REGISTER.md`; no release or product completion is claimed.

## CTO-001 foundation update

- **IN_PROGRESS:** local-only PDF registration prototype; validates a synthetic PDF, compares source hashes and registers PENDING metadata. See `docs/evidence/CTO-001-tests.txt`; no desktop picker capability or viewer.
- **IN_PROGRESS:** API rejects non-loopback peers and browser origins in TestClient; authenticated health and missing-token rejection verified on a live loopback socket. Tauri handshake remains unverified.
- **BLOCKED:** Tauri/React/PDF.js viewer and Windows end-to-end evidence; Rust/Cargo not found on PATH and frontend dependencies not provisioned.
- **NOT STARTED:** OCR, AI/RAG and citation validator under G1 gate. No release sign-off.

## CTO-001 integrity follow-up

- **IN_PROGRESS:** import checks open-file hash, size and path identity again before committing; regression tests exercise synthetic content change and simulated identity change. This does not close the local filesystem race window or establish a trusted desktop capability.
- **IN_PROGRESS:** migration runner rejects an existing incomplete checksum ledger; existing database adoption, backfill and reverse migration remain outstanding.
- **Evidence:** `docs/evidence/CTO-001-integrity-tests.txt`: 15 tests passed; G1 remains unmet.

## CTO-001 desktop prototype

- **IN_PROGRESS:** Tauri Windows executable built and process remained running for five seconds; React/PDF.js viewer opened and navigated a synthetic PDF in an Edge headless browser, hash unchanged. Screenshot is browser-only.
- **NOT VERIFIED:** actual native window PDF interaction, secure integration with backend, capability handoff, source race, installation and full offline checks. G1 remains NO-GO.
- Dependency installation was authorized and logged in `docs/evidence/DEPENDENCY_INSTALL_LOG.md`; transitive license/security approval remains pending.

## CTO-002 — Foundation recovery

- **IN_PROGRESS:** local sidecar protocol, authenticated workspace API and SQLite snapshot/restore to a new path. Tests include process restart and EOF shutdown; Tauri does not yet start or stop this sidecar.
- **IN_PROGRESS:** viewer searches existing PDF text and navigates to first matching page in a browser smoke test; no native Tauri PDF interaction evidence.
- **IN_PROGRESS:** GitHub Actions Windows Python/frontend jobs passed for e1f99af; dependency inventory is provisional and incomplete, native E2E is not covered.
- **G1 NOT_ACCEPTED:** trusted native picker, sidecar integration, persistent imported document workflow, Windows E2E, full license review and secure restore remain open. See `GAP_REGISTER.md` and CTO-002 evidence.
