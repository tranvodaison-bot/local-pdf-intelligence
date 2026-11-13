# 03 — API contract
All routes prefix `/api/v1`, HTTP only 127.0.0.1, randomly generated per-start bearer token passed via secure Tauri IPC (never localStorage) + Origin verification. No CORS wildcard. `request_id` for traceability. Error JSON: `{code, message, details?, request_id}`. Client must not trust UI-only permissions.
- `GET /health`: runtime/storage/model readiness; no secrets.
- `GET/POST /workspaces`: list/create.
- `GET /workspaces/{id}/documents`: list with status/filter.
- `POST /documents/import`: `workspace_id`, selected local path via trusted desktop IPC; backend validates allow-list/selection tokens. In future multiuser version do not accept arbitrary filesystem paths from browser.
- `GET /documents/{id}` and `/versions/{version_id}`: metadata.
- `GET /versions/{version_id}/pages/{page_index}/blocks`: block metadata and anchors.
- `GET /versions/{version_id}/pages/{page_index}/render`: use a trusted PDF access protocol; prefer Tauri file-stream plugin scoped to selected asset. Prevent arbitrary file/path traversal.
- `GET /jobs/{id}`, `POST /jobs/{id}/cancel`, `POST /jobs/{id}/retry`.
- `POST /search`: workspace_id, document_version_ids, query, limit; returns ranked snippets+anchors.
- `POST /research/answer`: mode (EVIDENCE_ONLY|REASONING), question, selected versions; returns analysis_run_id, status, claims, citations, unknowns, model provenance.
- `GET /citations/{id}/resolve`: returns validated anchor or explicit error, no fabricated page.
- `GET /models`, `POST /models/validate`, `GET /audit`.
- `POST /export/research`: explicit user action to Markdown/JSON.
## Idempotency
`POST /documents/import` accepts Idempotency-Key; duplicate hash in same workspace should prompt reuse/link (not create silently). Jobs include source_sha/generation. Cancel cooperative; lifecycle recoverable.
## Pagination
Use cursor/keyset for lists; stable sorting updated_at DESC + ID. Define max page size and upload size via configurable limits. Version ID mandatory in all citation and analysis APIs.
## Event stream
Server-Sent Events `/api/v1/jobs/events` or scoped polling; no websocket requirement MVP. Persist job state regardless of UI presence.
**OpenAPI stub:** `contracts/openapi.yaml` documents initial core endpoints. Codex must expand all routes and validate schema with contract tests.
