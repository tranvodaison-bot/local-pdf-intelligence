# Dependency installation evidence — 2026-11-13

User authorized downloading and installing Rust/Cargo and frontend dependencies during this task. No user PDF was transmitted.

- `winget install --id Rustlang.Rustup --exact --scope user --silent ...`: failed with `No applicable installer found`.
- Retry without `--scope`: winget fetched rustup 1.29.3 from `https://static.rust-lang.org/rustup/archive/1.29.3/x86_64-pc-windows-msvc/rustup-init.exe`, reported installer hash verified and installation success. Manifest-reported SHA-256 `38027d51d69a5d05493627a0634dbea52d6cd793c8f072d2373d3f4163eec7db`. Installed `rustc 1.100.0` and `cargo 1.100.0`.
- `npm install --no-audit --no-fund` in Google Drive workspace failed with EBADF. Retry in separate local C: workspace with isolated npm cache succeeded: 29 packages. See `npm-desktop-retry.log` and `apps/desktop/package-lock.json`.
- `npm run tauri -- build --no-bundle` downloaded Rust crates. First attempt failed due to missing icon; retry succeeded. See `tauri-build-retry.log` and `apps/desktop/src-tauri/Cargo.lock`.

Dependency checksums in lockfiles support reproduction. Full transitive license, vulnerability and supply-chain review is NOT COMPLETE; no distribution approval is implied.
