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
