# 06 — Definition of Done / Test plan
## P0 acceptance gates (binary)
1. Import text PDF and scan PDF in Vietnamese: actual parser + OCR produce page/block anchors; warnings on uncertainty.
2. Source immutability: input SHA256 before/after import, parse, search, export remains byte-identical; original never moved or deleted.
3. Offline: disconnect network after provisioning models; startup, import, ask, citation navigation and export work; no network egress.
4. Citation correctness: each displayed source link resolves to existing version/page/block and highlights expected bbox; test rotation, cropbox, zoom, searchable and OCR PDF. Any invalid anchors fail closed.
5. Evidence-only abstention: all unsupported questions return explicit NOT_ENOUGH_EVIDENCE; no citations fabricated.
6. Reasoning mode: factual statements anchored; inferences clearly labeled; conflicting sources surfaced.
7. Failure/recovery: corrupted PDF, password PDF, missing source, job killed mid-process, storage full, model unavailable, OCR timeout; recover/retry without data corruption.
8. Search: version filters enforced; no cross-workspace contamination; model switch does not return stale vector results.
9. Security: local API token mandatory, loopback only; no path traversal; prompt injection from PDF cannot trigger network or filesystem writes.
10. Backup/restore: all app data recoverable and source asset references validated; persistent queue survives restart.
11. Packaging: fresh Windows 11 offline install/uninstall; no reliance on Python/Node/Docker installed on end user device; models may be separately provisioned by explicit installer.
12. Quality: executable test suite, reports, source commit, reproducible build instructions and dependency/license inventory.
## Test pyramid
Unit: text normalization, page bbox transform, chunk ID, SHA hash, Decimal parse, citation validator, FTS filter. Integration: SQL FK/FTS, queue retries, parser adaptors, Ollama mocked/real, startup/shutdown. E2E: user-selected PDF -> page -> chat -> clicked citation -> export. Security: malicious input & invalid paths. Performance: measure on actual hardware and corpus, do not fabricate target latency.
## Golden evaluation dataset
At least 20 authorized sample documents covering Vietnamese text, scanned, tables, rotated/cropped pages, two-column, multi-version, encrypted, damaged, contradictory clauses, duplicate and unknown-answer. Avoid confidential source PDFs in public repository. Annotate ground truth page, bbox, expected answer, negative citations, table calculation; use scoring for recall@k, precision@k, grounded-claim rate, citation localization accuracy, unsupported-assertion rate, OCR CER/WER where ground truth exists.
## Evidence for each milestone
Commit hash; command+return code; tests passed/failed/skipped; screenshot/video; anonymized input hashes; migration checksum; coverage where available; known issues with severity P0/P1/P2; release artifact hash. Never certify on screenshots alone.
