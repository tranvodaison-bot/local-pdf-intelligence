# Local API foundation

This is not a desktop application. Set a fresh session token of at least 32 characters via a secure process handoff and bind uvicorn exclusively to 127.0.0.1. The Tauri handshake and Origin verification are not implemented: do not expose this development API to untrusted clients. No document or AI endpoints exist yet.

`python -m uvicorn localpdf.main:app --host 127.0.0.1 --port 8765` from this directory after setting `LOCALPDF_SESSION_TOKEN`. Avoid putting the token in shell history or logs.
