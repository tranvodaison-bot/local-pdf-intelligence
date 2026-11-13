# Decision log

## ADR-008 — SQLite migration checksum ledger (2026-11-13)
Status: accepted for foundation; architecture remains SQLite. Apply numbered SQL in a transaction, store its SHA-256 in a separate ledger, and reject unknown pre-existing schemas or changed applied migration files. Enable foreign keys per connection. Explicit reviewed backfill/adoption and reverse migrations or backup restoration are required for existing data; no automatic destructive downgrade. Tests must demonstrate rollback and idempotency.
