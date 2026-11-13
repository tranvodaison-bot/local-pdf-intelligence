# Test report

2026-11-13: `python -B scripts/verify_schema.py` exited 0. It checks schema creation, one FTS insertion/query, foreign_key_check and integrity_check in memory; it is not an application test.

## Foundation — 2026-11-13
Command: `python -m pytest -q -p no:cacheprovider tests/test_foundation.py` with `PYTHONDONTWRITEBYTECODE=1`. Exit 0; output: `4 passed in 0.74s`. Tests cover a Unicode database path, migration idempotency, foreign keys and integrity, failed migration rollback, checksum change and unknown-database rejection, and FastAPI TestClient token rejection/acceptance. No live network, desktop, PDF, OCR or end-to-end test was performed. Migration backfill and reverse migration are not implemented or tested.
