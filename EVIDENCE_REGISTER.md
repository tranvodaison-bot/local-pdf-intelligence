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
| 2026-11-13 | `docs/evidence/CTO-001-integrity-tests.txt`: 15 tests passed | Synthetic-source change/identity and incomplete-ledger regression; no G1 sign-off |
| 2026-11-13 | `docs/evidence/CTO-001-desktop-tests.txt`; `desktop-browser-smoke.png` | Tauri executable build and process start; browser-only PDF smoke; no native E2E |
| 2026-11-13 | Code commits `53666bf` and `7e8cb06` | Integrity fixes and standalone viewer prototype; integration and native E2E remain open |
| 2026-11-13 | `docs/evidence/CTO-002-test-evidence.md` | CTO-002 local tests/build; G1 NOT_ACCEPTED |
| 2026-11-13 | `docs/evidence/CTO-002-dependency-inventory.json` | Provisional CycloneDX inventory, incomplete licenses/transitives |
| 2026-11-13 | GitHub Actions run `43393793402`, commit `e1f99af` | Windows Python/frontend checks passed; native E2E absent |
