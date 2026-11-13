# 00 — Product scope / PRD
## Người dùng, deployment
Một người dùng một máy Windows 11 x64 (mục tiêu), dữ liệu local; dự phòng nhiều workspace, không multi-tenant/server trong MVP. Tạo dự án Notebook/Workspace rồi nạp nhiều PDF.
## Jobs-to-be-done
- Đọc PDF gốc, tìm từ khóa, chọn đoạn, highlight, bookmark và ghi chú.
- Import PDF text/scan nhiều file, không sửa bản gốc; tiến độ OCR; quản lý lỗi.
- Chat theo 1/nhiều PDF, click citation để điều hướng chính xác; phân tích hợp đồng, pháp lý, hồ sơ xây dựng.
- Phân biệt chứng cứ, nhận định, giả định; xuất Markdown/JSON báo cáo kèm trích dẫn.
## MVP P0
A. Workspace/document manager: add file/folder, duplicate detection by hash, status, file version.
B. PDF viewer: render, zoom, navigation, search, selection, click-to-bbox highlight; password-protected PDF xử lý có thông báo.
C. Ingestion: queue async, cancel/retry, parser fallback, OCR Vietnamese, layout blocks, tables minimally with cell anchors.
D. SQLite metadata + FTS5, semantic search optional if embedding model available; fallback FTS only must work offline.
E. Ollama adapter and model detection; RAG Evidence-only and Reasoning modes; result with mandatory grounded citations or abstention.
F. Logs, failures, export analysis; backup/restore local; configuration path & model settings.
## P1 — After MVP
Cross-document compare, structured BOQ/table reconciler, claim graph, version comparison, knowledge notes, reranking benchmark, Markdown import/export.
## P2 — Later
Skills builder (approval), agents, Obsidian/Drive bridge with explicit approval, voice/audio, GIS/BIM links, web app multiuser.
## Out of scope P0
Auto-create legal conclusions as established fact; cloud upload, live sync, agents modifying source; OCR handwriting guarantee; exact parity with NotebookLM; perfect financial calculation by LLM.
## Success metrics — target pending baseline evaluation
- Source immutable SHA256 after all operations: 100% of test cases.
- All rendered citations resolve to existing version and block anchor; invalid citations displayed: 0.
- 100% unknown-answer tests do not fabricate source citations.
- Smoke offline with network disabled and installed models passes.
- Accuracy OCR/layout/retrieval must be measured with golden set; numerical pass thresholds calibrated before production signoff, not invented now.
