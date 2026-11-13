# Test report

2026-11-13: `python -B scripts/verify_schema.py` exited 0. It checks schema creation, one FTS insertion/query, foreign_key_check and integrity_check in memory; it is not an application test.

## Foundation — 2026-11-13
Command: `python -m pytest -q -p no:cacheprovider tests/test_foundation.py` with `PYTHONDONTWRITEBYTECODE=1`. Exit 0; output: `4 passed in 0.74s`. Tests cover a Unicode database path, migration idempotency, foreign keys and integrity, failed migration rollback, checksum change and unknown-database rejection, and FastAPI TestClient token rejection/acceptance. No live network, desktop, PDF, OCR or end-to-end test was performed. Migration backfill and reverse migration are not implemented or tested.

## CTO-002 — 2026-11-13

- Windows/Python 3.14.2: `python -m pytest -q -p no:cacheprovider tests` — exit 0, **26 passed in 7.15s**. Includes API authentication, workspace persistence across sidecar process restarts, sidecar EOF shutdown, SQLite snapshot/restore and OpenAPI route checks.
- Frontend C: build workspace: `npm run build` — exit 0; TypeScript and Vite passed, bundle size warning.
- Browser smoke: `python -B tests/desktop_smoke.py` with `LPI_DESKTOP_ROOT` set to local build workspace — exit 0; synthetic two-page PDF search and missing-text case; source SHA-256 unchanged. Screenshot is browser-only.
- Windows Tauri: `npm run tauri -- build --no-bundle -- --locked`, `CARGO_NET_OFFLINE=true` — exit 0; executable observed running for five seconds. No native viewer interaction test or installer.
- GitHub Actions workflow: **NOT_RUN** at the time of writing; execution must be checked after push.
- No real user PDF, private data or credentials used in the above tests.

Lần chạy trước có 1 test timeout do gửi yêu cầu trước khi sidecar sẵn sàng; kiểm thử đã được sửa để chờ health và toàn bộ test được chạy lại thành công.
