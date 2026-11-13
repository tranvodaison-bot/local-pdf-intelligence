# 07 — Implementation plan for Codex
Milestone time ranges are estimates subject to benchmark; **no work has been executed**.
## M0 — Repository / gates (day 1)
Establish monorepo, lint/test/CI, pre-commit, version pins/SBOM stub, license decision, SQLite migration, seed fake fixtures, Windows launch script. Exit: schema verifies, backend health test, UI shells launch locally, license decision logged.
## M1 — Vertical PDF slice (days 2–3)
Import text-PDF (read-only SHA), file registry, page text blocks/bbox, PDF.js viewer, location link. Exit: deterministic demo open→page→highlight using known fixture; source hash unchanged.
## M2 — OCR and retrieval (days 4–5)
Docling OCR worker, job recovery, Vietnamese OCR, FTS5, optional embeddings adapter. Exit: scans searchable with labeled confidence, filtered query and import duplicate handling.
## M3 — Chat and verification (days 6–8)
Ollama adapter, structured answer, evidence-only + reasoning, deterministic citation validator, no-answer state. Exit: golden cases with valid links; nonexistent citations blocked.
## M4 — Hardening/package (days 9–13)
Backup/restore, malformed PDF/safe limits, offline firewall test, regression, Tauri sidecar installer, manuals, known issues and report. Exit: fresh-machine acceptance signed using logs.
## Dependency order
License gate / UX auth scheme -> schema -> file read-only -> bbox viewer -> chunk + FTS -> embedding -> model -> citation validation -> security + installer.
## Detailed task cards
- P0-001: Tauri+FastAPI handshake and token: acceptance unauthorized GET rejected; fake backend tests.
- P0-002: file picker capability grants only selected PDFs; traversal test.
- P0-003: schema/migrations + foreign keys + FTS triggers / rebuild.
- P0-004: SHA stream + document version import idempotency and missing relink.
- P0-005: layout/parser bbox adapter with license gate and regression fixture.
- P0-006: OCR worker with partial status, cancel and retry after crash.
- P0-007: PDF.js coordinate-transform highlight.
- P0-008: retrieval exact version filter, FTS and optional vectors.
- P0-009: Ollama detection/model failure path + structured JSON.
- P0-010: evidence validation and unknown-answer handling.
- P0-011: export Markdown/JSON citation manifest.
- P0-012: backup/restore and offline, security and installer E2E.
## Three immediate actions
1. Run schema verifier and resolve errors; freeze migration 001 with ADR.
2. Scaffold backend+Tauri shell and verify localhost-only authenticated handshake.
3. Implement text-PDF vertical slice with bbox highlights and source immutability test before OCR/RAG.
