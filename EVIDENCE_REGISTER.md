# Evidence register

| Date | Evidence | Scope |
|---|---|---|
| 2026-11-13 | `python -B scripts/verify_schema.py`: exit 0, PASS | Limited in-memory schema check |
| 2026-11-13 | Initial `git status`: not a git repository; subsequently initialized and committed as `98187bf` | Foundation commit; no demo screenshot |
| 2026-11-13 | Rust/Cargo not found in PATH | Tauri build not verified |
| 2026-11-13 | Manifest verification: 23 files, 0 mismatches | Extracted baseline integrity at time of check, before this register update |
| 2026-11-13 | `python -m pytest -q -p no:cacheprovider tests/test_foundation.py`: exit 0, 4 passed | Foundation tests only; see TEST_REPORT.md |
| 2026-11-13 | `docs/evidence/CTO-001-tests.txt`: 12 tests passed | Automated local tests; no GUI or installer |
| 2026-11-13 | `docs/governance/BASELINE_AUDIT.md` | ZIP manifest 23/23; remote read at ce88e41 |
| 2026-11-13 | Foundation implementation commit `031bf4f` | Local CLI import, API boundary and automated tests; not a G1 sign-off |
