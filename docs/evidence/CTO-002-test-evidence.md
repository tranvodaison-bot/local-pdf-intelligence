# CTO-002 local evidence — 2026-11-13

Base master: `ce88e41fc24ddfa3f3259ed7b7f9fb4b9542ba6a`; work began from feature commit `06097a693b26f04bbc8d4a105875e043b4dee60d`.

- `python -m pytest -q -p no:cacheprovider tests`: exit 0, **26 passed in 7.15s** (Windows, Python 3.14.2).
- `npm run build`: exit 0; TypeScript/Vite succeeded, bundle size warning.
- `python -B tests/desktop_smoke.py`: exit 0; Edge headless selected a synthetic PDF, searched page two and a missing string, SHA-256 unchanged. `CTO-002-desktop-browser-smoke.png` is browser-only, not a native screenshot.
- `npm run tauri -- build --no-bundle -- --locked` with `CARGO_NET_OFFLINE=true`: exit 0; see `CTO-002-tauri-build.log`. Executable SHA-256 `d69b32f62f2daa92e3e641a009164d681dbbdb19a7970fb1ef04cdd4b2efe153`; process survived 5 seconds when started hidden.
- `python -B scripts/generate_dependency_inventory.py`: 526 components; 420 lack a license entry. It omits Python transitives, and optional packages are not filtered for release.

G1 **NOT_ACCEPTED**: native Tauri end-to-end, trusted file picker/backend integration, sidecar process management by desktop, persisted documents and source hash proof through the entire user workflow are not demonstrated. No installer or full license approval.

Lần chạy trước có 1 test timeout do gửi yêu cầu trước khi sidecar sẵn sàng; kiểm thử đã được sửa để chờ health và toàn bộ test được chạy lại thành công.

- GitHub Actions run `43393793402`, commit `e1f99af37bf40a67037e9257bd67d9ae0fedfc35`: **success** for Windows Python and frontend jobs; no native Tauri E2E.
