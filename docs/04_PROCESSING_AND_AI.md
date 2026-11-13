# 04 — PDF pipeline + AI reasoning
## Parse and OCR
Identify PDF structure; calculate SHA256; reject corrupt/encrypted files with friendly error. For text PDF, extract span/line bbox. For pages with insufficient text, run OCR with Vietnamese+English pack; record OCR engine/version/confidence. Docling supports structured document parsing but coordinate fidelity needs empirical tests. Tables must preserve cell grid and source page anchors; for uncertain cells record low-confidence, never silently infer values.
## Chunking
Semantic/heading-aware, 300–800 token experimental window and 10–20% overlap (tunable, not hard acceptance); never split tables without retaining table header, row identity. Each chunk refers to its content_blocks and extraction generation.
## Retrieval
FTS5 query + optional semantic embeddings; hybrid rank merge (RRF initial) + optional reranker; retrieval constrained to exact selected document_version IDs, never global scope by default. Scores are relevance not factual confidence. Log retrieved candidates and selected contexts for reproducibility (respect local storage retention).
## Prompt-injection defense
PDF content is untrusted data. Ignore instructions embedded in documents aimed at overriding model/tool policies, secrets, filesystem access or outbound communication. Models only receive authorized tools; no shell, file mutation or network permissions in research flow.
## Structured response model
Return `claims[]` with `kind=SOURCE_FACT|INFERENCE|UNKNOWN`, citations source version/page/block, explanation/reasoning_summary (not private chain of thought), counter_evidence, limitations. LLM output must parse against `docs/09_AI_OUTPUT_SCHEMAS.json` and then undergo deterministic citation verification.
## Verification tiers
A. `anchor_valid`: exact IDs/coordinate bounds point to existing persisted blocks.
B. `quote_match`: normalize Unicode NFC, whitespace, hyphens; compare substring with thresholds and flag OCR ambiguity; not auto-replace unknown text.
C. `claim_supported`: second-pass entailment/checker can assess support; not conclusive guarantee, reports SUPPORTED/CONTRADICTED/INSUFFICIENT and score; deterministic facts vs model judgments clearly marked.
D. If anchors absent/invalid: remove unsupported citation, mark unknown/insufficient rather than invent references.
## Modes
Evidence Only: assert source facts only from selected versions, cite each substantive assertion. Reasoning: source facts + explicit inference, assumptions, counterevidence and uncertainty; no mixing inference into quoted text. Knowledge Fusion deferred P1 and gated externally.
## Numerical comparison
Never trust LLM arithmetic for quantities/prices: parse decimals/currency/unit and compute using Python Decimal, reconcile table row keys and record formula, inputs and source IDs. Expose ambiguity of commas/dots in Vietnamese formatting.
## Output constraints
One answer can include multiple claims and citations with click anchors. Need no-evidence answer pathway. All model runs include model digest/parameters, prompt_version, extraction_generation, retrieval filters and execution timestamps.
