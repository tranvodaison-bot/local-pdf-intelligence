# 01 — Architecture
## Context and boundaries
Tauri v2 Desktop (React TS + PDF.js) <-> local FastAPI sidecar on loopback <-> application services <-> storage + model runtime. Ollama must be loopback-configured. Block external network by default. Sidecar packaging/port lifecycle, startup recovery and binary integrity require actual Windows testing.
## Bounded contexts / ownership
- Library: workspace, documents, versions, physical assets; owns hash and file metadata.
- Extraction: jobs, pages, blocks, tables, OCR confidence, artifacts.
- Search: FTS index and vector embeddings/collections, retriever, reranker.
- Research: conversations, messages, claims, citations, analysis run; **does not mutate Library**.
- Governance: settings, model registry, audit log, backup/restore, errors.
Cross-context writes only via services with transactional boundaries; async processing via durable SQLite job table, not memory-only queue.
## Executable seams
`PdfReaderAdapter`, `ParserAdapter`, `OcrAdapter`, `EmbeddingAdapter`, `VectorIndexAdapter`, `ChatModelAdapter`, `CitationResolver`, `ExportAdapter`. Define Protocols/ports and fake implementations for tests.
## Critical workflows
Import: select file -> validate type/size -> sha256 stream -> create asset reference and document version -> enqueue -> parse -> page/block/anchor -> FTS -> (optional) embed -> ready/partial/failed.
Query: workspace/doc filters -> retrieve (FTS + vectors) -> rerank -> context with stable chunk IDs -> LLM JSON answer -> deterministic citation validator -> display grounded answer or abstention -> link highlights.
Delete: soft-delete metadata; do not touch original; garbage collect derivative storage only with explicit confirmation and logged operation.
## Source path policy
`original_path` stores existing read-only reference, `derived_root` under application data user-selected folder, copy is optional explicit and marked `managed_copy`; never change originals. For moved/missing paths, mark MISSING and request relink matching SHA, never silently substitute.
## Data consistency
SQLite WAL, foreign_keys=ON, busy_timeout, transaction boundaries; atomic temp+rename for derived artifacts; recovery from power loss; FTS rebuild procedures. One writer and job concurrency limits.
## Citation coordinate strategy
Persist original page index 0-based and display page label 1-based; bbox `[x0,y0,x1,y1]` in PDF user-space or explicitly normalized coordinate_system with page width/height/rotation. Viewer must transform cropbox, zoom and rotation. Do not infer bbox from plain Markdown alone.
## Search index migration
Start SQLite FTS5 mandatory; optional Qdrant local persistent folder or SQLite vector plugin after benchmark. `chunk_id`, `embedding_model_id` and `index_generation` isolate versions; atomic swap of generation; rebuild vectors if embedding model changes.
## Frontend routes
`/library`, `/workspaces/:id`, `/research/:id`, `/settings`, `/jobs`, `/audit`. Three-panel layout: Sources / PDF viewer / AI chat. UI has evidence badges, OCR warnings, source version and model ID.
