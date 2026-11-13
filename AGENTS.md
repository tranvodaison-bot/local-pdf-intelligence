# CHỈ THỊ DÀNH CHO CODEX — LOCAL PDF INTELLIGENCE
1. Đọc README và docs 00–12 trước khi sửa mã. Không tự tuyên bố đã build/test/tích hợp nếu chưa chạy thực tế.
2. Không viết/xóa/đổi tên file nguồn PDF. Chỉ đọc; mọi sản phẩm dẫn xuất vào workspace; SHA-256 đầu/cuối để chứng minh không thay đổi.
3. Offline default: không telemetry, không gửi nội dung tài liệu ra internet, không auto-download model; download phụ thuộc chỉ khi người dùng cho phép và ghi nhật ký.
4. Ghi rõ SOURCE_FACT / INFERENCE / UNKNOWN trong phản hồi AI. Không giả trích dẫn. Citation phải được resolver kiểm tra document_version + page + bbox + span hợp lệ.
5. Mọi kết quả AI chịu kiểm tra máy: citations tồn tại, trích dẫn text có mặt trong content block, độ lệch OCR được ghi nhận. Không suy luận là sự thật được xác minh.
6. Backend Python/FastAPI, Windows Tauri+React+PDF.js, SQLite FTS5, vector adapter (Qdrant local optional), Ollama adapter. Không ép Docker cho người dùng cuối.
7. Document parser là adapter: dùng Docling cho layout/OCR sau khi kiểm thử offline; lựa chọn PyMuPDF phải qua license gate. Không mặc định dùng license AGPL trong app proprietary.
8. Khóa sổ từng bước: commit + test + logs + demo screenshot + evidence ledger; cập nhật `docs/12_HANDOVER_REGISTER.md`. P0/P1 chưa giải quyết: không sign-off.
9. Bất kỳ lỗi OCR, tài liệu không đọc được, thiếu mô hình, citation mất anchor, dữ liệu hỏng đều phải hiện trạng thái và retry/recover, không xóa source.
10. Không xây chức năng agent tự sửa dữ liệu hoặc đẩy văn bản lên cloud trong MVP.
11. Bổ sung Alembic/migrations hoặc quản lý schema tương đương; kiểm thử transaction, idempotency, backfill và rollback.
12. Giao diện tiếng Việt; dữ liệu chuẩn UTF-8; đường dẫn Windows Unicode và đường dẫn dài cần test.
