# LOCAL PDF INTELLIGENCE — CODEX HANDOFF v1.0
**Ngày khóa đặc tả:** 2026-11-13 | **Trạng thái:** DESIGN BASELINE — NOT IMPLEMENTED/NOT VERIFIED

## Mục tiêu
Windows desktop offline-first đọc PDF có OCR, hỏi đáp RAG, suy luận có trích dẫn đúng file/phiên bản/trang/vùng; kiểm chứng nguồn; không đụng file gốc. Không sao chép thương hiệu hoặc giao diện của NotebookLM.

## Bắt đầu cho Codex
1. Đọc `AGENTS.md`, `docs/00_PRODUCT_SCOPE.md`, `docs/01_ARCHITECTURE.md`, `docs/02_DATA_DICTIONARY.md`, `docs/03_API_CONTRACT.md`, `docs/04_PROCESSING_AND_AI.md`, `docs/05_SECURITY_AND_LICENSE.md`, `docs/06_ACCEPTANCE_AND_TESTS.md`.
2. Triển khai **Bước 1** theo `docs/07_DELIVERY_BACKLOG.md` và prompt `prompts/CODEX_MASTER_PROMPT.md`. Không tuyên bố hoàn thành nếu thiếu output test và bằng chứng.
3. Chạy kiểm tra migration SQLite qua `python scripts/verify_schema.py` (chỉ xác minh cú pháp/schema, **không phải test ứng dụng**).
4. Tạo backend và desktop theo kiến trúc; ưu tiên functional vertical slice: import PDF → parse → search → answer → click citation.

## Tệp quan trọng
- `db/001_initial.sql`: baseline SQL có khóa ngoại, chỉ mục, FTS5.
- `contracts/openapi.yaml`: API dự kiến; cần codegen/lint và contract test trước khi chốt.
- `docs/09_AI_OUTPUT_SCHEMAS.json`: structured response AI, minh bạch nguồn và suy luận.
- `docs/10_ADR_AND_RISKS.md`: quyết định/giả định/blockers.
- `docs/11_EVALUATION_DATASET.md`: yêu cầu bộ golden set, không tạo dữ liệu chứng cứ giả.
- `docs/12_HANDOVER_REGISTER.md`: trạng thái bằng chứng bàn giao.

## Chưa có gì được xây dựng
Không có app Windows, backend, AI model, OCR pipeline, hội thoại hay kiểm thử end-to-end được tạo ở đây. Repo là **bộ đặc tả để Codex thực hiện**. Nếu Codex muốn thay đổi hợp đồng API hay schema thì bắt buộc ADR + migration + test.
