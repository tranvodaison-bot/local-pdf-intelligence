# 02 — Data contract / SSoT
## Canonical IDs
UUIDv7 preferred (UUID4 acceptable initially; never semantic filename IDs). Internal document ID stable across versions. Every logical change includes created_at UTC ISO8601 and updated_at as applicable. `sha256` is exact file-bytes identity.
## Core entities
- `workspaces`: top-level user collection.
- `documents`: stable logical identity; has many immutable versions.
- `file_assets`: original_path/reference and SHA-256; not owned destructively.
- `document_versions`: points to file_asset and revision label; processing status; unique per document/version_no.
- `pages`: page number, dimensions, rotation, OCR status.
- `content_blocks`: typed text/layout blocks, page bbox/coordinates, OCR confidence and reading order.
- `chunks`: retrieval units derived from blocks; never replace source blocks.
- `tables` + `table_cells`: table structure and row/column with source anchor.
- `jobs`: durable workflow/status/retry metadata.
- `analysis_runs`/`claims`/`citations`: provenance of each AI response; `citation` must link version+block.
- `conversations`/`messages`: chat and model/version provenance.
- `audit_logs`: append-only processing and security events.
- `model_registry`: track installed model checksum/ID, role and config.
## Status model
version: PENDING -> PROCESSING -> READY / PARTIAL / FAILED; MISSING separately if original disappears. Jobs: QUEUED -> RUNNING -> SUCCEEDED / FAILED / CANCELLED; retried via new attempt record. Claims: SOURCE_FACT, INFERENCE, UNKNOWN; citation verification VERIFIED_ANCHOR, UNRESOLVED, INVALID; do not equate anchor validity with truth/legal validity.
## Integrity invariants
(a) page belongs to version, (b) block belongs to page, (c) chunk references same version, (d) citation points to claim + block and page consistent, (e) version SHA immutable; (f) duplicate content hash may map to multiple user documents but deduplicate physical derived artifacts only after authorization, (g) never cascade-delete user source files.
## Canonical JSON for anchor
`{ "document_version_id":"uuid", "page_index":0, "block_id":"uuid", "bbox":[0,0,10,10], "coordinate_system":"pdf_points", "quote":"..." }`
## Indexing metadata
Store parser_version, OCR_engine/version/language, extraction_params_hash, embedding_model_digest, prompt_version, chunker_version, source_sha256. Rerun creates new processing generation; never overwrites evidence linked to a prior analysis.
## Migration policy
SQL in db/001_initial.sql is baseline design pending review. Production implementation must add migration runner, consistent IDs and deterministic, schema verified tests before freezing. Changing `bbox` representation requires backfill + viewer test.
