# 10 — ADR, risks, unresolved questions
## Proposed ADRs (status PROPOSED, not accepted)
ADR-001: Windows-first offline Tauri v2+React+Python FastAPI sidecar.
ADR-002: SQLite WAL/FTS5 as SSoT; optional local vector index not authoritative.
ADR-003: Immutable source file paths + hash; all derivatives under app-data.
ADR-004: Evidence schema strongly version- and bbox-bound; never cite unvalidated LLM text.
ADR-005: Models via Ollama adapter; no network egress by default.
ADR-006: Parser adapter and license review; no PyMuPDF until AGPL/commercial decision.
ADR-007: No network, automatic sync or external Skills in MVP.
## Blockers (need evaluation, not user interrogation before M0)
B01: License policy (proprietary vs open-source) affects PDF engine and packages.
B02: Actual Windows hardware and Ollama model availability affects RAM/GPU performance.
B03: OCR Vietnamese quality and table bbox mapping: evaluate from golden set.
B04: PDF.js page coordinate matrix under rotation/cropbox: integration fixture.
B05: Tauri sidecar antivirus/SmartScreen/signing/reproducible packaging.
B06: Distinction of OCR correct vs semantic answer grounded; verifier cannot certify legal truth.
## Risk matrix
P0: altered original source; fabricated citation; external egress; path traversal; corrupt DB; AGPL noncompliance.
P1: table/cell alignment; model hallucinates despite valid citation; stale index; duplicate versions; OCR confidence inaccessible; huge file crash.
P2: slow inference on CPU; model migration; high disk usage; UI accessibility issues.
## Change control
For each ADR revision: rationale, alternatives, migration/rollback, impact DB/API/UI/tests, reviewer acceptance. Do not silently re-scope P0.
