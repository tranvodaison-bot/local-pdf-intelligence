# CTO-002R evidence — 2026-11-13

Baseline: `aecf11432703a9bce662c28fbfc0c1c408ffae5e`, PR #2 feature branch.

- Source test suite exit 0: 32 passed in 17.14s; `CTO-002R-python-tests.log`.
- PyInstaller 6.19.0 packaged a Windows sidecar binary. Initial attempts failed from cross-drive source/spec paths and an unresolved data path (`CTO-002R-sidecar-build.log`, `CTO-002R-sidecar-build-retry.log`); script retry succeeded (`CTO-002R-script-build.log`). Binary SHA-256 `c4dd9d35b0bcbaef64bb7f2d6d66e491f918a453a1051b013334032a12be2de8`. Artifact is local, unsigned and not a release.
- Frozen binary test suite exit 0: 4 passed in 11.05s (`CTO-002R-binary-tests.log`). Test calls the real packaged process, sends grant over stdin, imports synthetic PDF, kills/restarts process and reads registered content.
- Synthetic fixture SHA-256 before and after restart: `61d41ce9e47168c843bc39d566861e9307fbca4a364c6bfa9dc1d0328e174cf0`; equality demonstrated in `CTO-002R-sha256-test.log`. This is not a native desktop E2E.
- One concurrent run failed due to a 10-second shutdown timeout; sequential reruns passed. Root cause remains unknown.

**G1: NO-GO / NOT_ACCEPTED.** Native picker, desktop-managed sidecar lifecycle, persisted viewer, Windows native E2E and screenshot/video are missing. No user PDF or credentials were committed.

Native UI automation attempt: `cua.getState()` failed before opening a surface with `windows sandbox failed: orchestrator_helper_report_read_failed` (setup helper exited with status 1). No native UI interaction or screenshot was captured. This does not establish that the desktop application itself failed.
