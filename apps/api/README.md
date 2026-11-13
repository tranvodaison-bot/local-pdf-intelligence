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
