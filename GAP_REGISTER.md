# Gap register — 2026-11-13

| ID | Priority | Finding | Required response |
|---|---|---|---|
| G01 | P0 | Handoff contains no working desktop, PDF pipeline, citation resolver or offline E2E. | Implement and test; no sign-off. |
| G02 | P0 | Independent citation foreign keys do not guarantee version/page/block belong together. | Resolver and integrity constraints with negative tests. |
| G03 | P0 | AI output schema permits empty citations and cannot verify quote, span, bbox or entailment. | Fail-closed deterministic validation and support assessment. |
| G04 | P0 | Initial SQL lacked a migration runner and rollback/idempotency evidence. | Add transactional runner; verify adoption and backfill separately. |
| G05 | P0 | No trusted file picker capability or Tauri token handoff exists. | Implement desktop IPC before exposing file import. |
| G06 | P0 | Parser license and coordinate fidelity lack approval and testing. | Review license tree and rotated/cropped fixtures; PyMuPDF remains gated. |
| G07 | P1 | Schema lacks full job attempts, embedding provenance, validation issues, entity relations and analysis parameters. | Add reviewed migrations and backfill when implementing features. |
| G08 | P1 | OpenAPI stub and API implementation are incomplete. | Synchronize contract with actual routes and test it. |
| G09 | P1 | No golden corpus, OCR/retrieval accuracy or recovery benchmark. | Build rights-cleared suite and measure. |
| G10 | P1 | Rust/Cargo not found on PATH; desktop dependencies not established. | Provision only with authorization and verify Windows build. |
| G11 | P1 | Working directory is not a Git repository. | Record missing commit evidence; establish repository when permitted. |
