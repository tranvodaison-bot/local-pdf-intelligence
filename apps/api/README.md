# Local API foundation

This is not a desktop application. Set a fresh session token of at least 32 characters via a secure process handoff and bind uvicorn exclusively to 127.0.0.1. The Tauri handshake is not implemented and all browser Origin headers are rejected: do not expose this development API to untrusted clients. No document or AI endpoints exist yet.

`python -m uvicorn localpdf.main:app --host 127.0.0.1 --port 8765` from this directory after setting `LOCALPDF_SESSION_TOKEN`. Avoid putting the token in shell history or logs.

## Local-only registration prototype

From `apps/api`, with locally provisioned `pypdf` (BSD-3-Clause metadata; transitive dependency and release license review still pending):

```powershell
python -m localpdf.cli --db "C:\absolute\workspace\library.sqlite" init-workspace --id demo --name "Tài liệu"
python -m localpdf.cli --db "C:\absolute\workspace\library.sqlite" import --workspace demo --file "C:\absolute\source\document.pdf"
```

The source is opened read-only, checked for header, size and parseability, rehashed and checked against the path identity before the database commit, then registered with status PENDING. Reimport in the same workspace returns `duplicate` without creating a second document. This is not a viewer, extraction, OCR, citation validation or trusted desktop selection. The path is accepted only from this explicitly invoked local CLI, not from the API. Do not point the database at the PDF source.

## Local database snapshot

`python -m localpdf.cli --db "C:\absolute\library.sqlite" backup --to "C:\absolute\new-backup.sqlite"`

`python -m localpdf.cli --db "C:\absolute\new-restored.sqlite" restore --from "C:\absolute\backup.sqlite"`

Both paths must be absolute and the destination must not exist. SQLite integrity is checked; source PDF files are references only and are not included. This initial utility does not supply encrypted backups, a manifest, source relinking or automated scheduling. Store snapshots in a protected location.

## CTO-002R sidecar prototype

`python -m localpdf.sidecar` consumes the session token as the first line of stdin, reports its loopback port, and terminates on EOF. The trusted parent can request a workspace-scoped, one-use 60-second file-selection grant via the control pipe; authenticated HTTP import accepts that grant, never a path. Registered bytes are returned only after SHA-256 verification. The native Tauri controller/picker is not connected yet.

For a development-only Windows binary, install PyInstaller only with approval, then run `scripts/build_sidecar.ps1 -BuildRoot <absolute-local-build-directory>` and capture its log. Do not distribute without license, security and native E2E review.
