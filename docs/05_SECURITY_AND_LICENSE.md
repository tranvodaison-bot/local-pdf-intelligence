# 05 — Security, offline and license gate
## Security defaults
- Bind FastAPI to 127.0.0.1; per-session high-entropy bearer token, secure handoff via desktop IPC; rate limits, origin checking; avoid arbitrary command/file path APIs.
- No telemetry, external LLM or remote inference by default. Enforce offline test using blocked network at OS/firewall level; log model-download attempts and require approval.
- Keep secrets in OS-protected credential store where feasible; don't write tokens into logs/crash dumps. Local database may contain sensitive text; recommend full-disk encryption (BitLocker), permission-scoped app data and encrypted backups when available.
- PDF parser accepts untrusted inputs; quotas max file size/pages/runtime, sandbox worker/subprocess, MIME signature checks, decompression-bomb controls, malware scanning integration optional. No arbitrary file read from client-provided path; use desktop-selected capability token.
- Never follow PDF links or execute embedded JS/scripts automatically; render in hardened PDF.js with CSP. Disable dangerous Tauri plugins by default and restrict FS scopes.
- Avoid network listening except loopback. Backups have manifest SHA256 and tested restore; paths Unicode, symlinks and junction attacks tested.
## Dependencies/license decisions
Docling is MIT according to official site, but check dependency transitive licenses; offline weights require pre-provisioning. PDF.js Apache-2.0, verify official package licenses and bundling notices. Ollama/model licenses vary by model; never assume unrestricted commercial use.
**PyMuPDF is AGPLv3 / commercial dual-licensed.** Before distributing proprietary executable, obtain legal approval/commercial license or use an alternative parser with acceptable distribution terms. Do not include PyMuPDF by default in build until license gate passes. Assess pypdf, pdfplumber/pdfminer.six, pypdfium2 and respective binary dependencies/licenses for required features.
Qdrant local client is a development choice; benchmark Windows packaging and license obligations before shipping. Tauri sidecar bundling needs binary signature, auto-update policy and process shutdown controls.
## Threat checklist
Malicious PDF/prompt injection, path traversal, SSRF, local unauthorized API, secrets leakage in logs, model auto-pull, poisoned embeddings, stale cited source, wrong citation after OCR reprocessing, memory exhaustion, corrupted sqlite, backup data leaks, ransomware, insecure auto-updates.
## Supply-chain acceptance
Generate SBOM, pin versions + hashes, scan vulnerabilities, review licenses, and record exceptions before signed release. No secrets or confidential PDFs in repo/test artifacts.
