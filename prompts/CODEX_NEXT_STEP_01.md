# Prompt tác nghiệp Bước 1 (M0–M1)
1. Kiểm tra README, AGENTS, SQL schema và OpenAPI stub; lập ADR + license matrix.
2. Tạo repo monorepo `apps/desktop`, `apps/api`, `packages/contracts`, `tests`, `migrations`, `scripts`; build frontend Tauri+React+PDF.js; backend FastAPI with health/auth.
3. SQLite migrations: apply `db/001_initial.sql`, FK+FTS check, DB integrity test; versioning schema migration tool.
4. Implement read-only file selection+import with SHA256. Synthetic fixture PDF with selectable native text, import->page/block bboxes. No OCR at this stage.
5. Viewer click citation and bbox highlight, including zoom/rotation; invalid anchor renders error.
6. Execute tests on actual OS, include commands/output with machine details. Mark any unavailable runtime as NOT VERIFIED; do not fake screenshots.
Acceptance: smoke import PDF→page blocks→search term→navigate highlight; SHA before=after; backend only listens 127.0.0.1 with auth; all test artifacts recorded.
