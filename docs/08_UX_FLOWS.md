# 08 — UX contract
## Main screen
Left 25% Sources: workspace tree, version, hash/status, checkboxes filter, progress/error. Middle 40% PDF.js viewer toolbar: tabs, pages, find, rotate/zoom, page OCR flag, bbox highlight, note. Right 35% Research: mode, ask, claims with source chips, uncertainties, counterevidence, model/latency.
## Flows
- New workspace > add PDFs using OS file picker > pending/processing/ready badges > open original by read-only viewer.
- Ask > choose versions > retrieval preview (optional) > answer streaming in labeled claims > click source chip > viewer switches version+page highlights snippet bbox.
- OCR low confidence -> yellow warning > show original image and extracted text side-by-side; manual correction stored as separate annotation never changes source.
- Source missing -> re-link file after hash verification; mismatch becomes new version only on user approval.
- Parser error -> see log/error code and retry; while processing show partial status, not false READY.
- Export result includes timestamp, document titles/versions/hash, quoted anchors, model ID, caveats.
## Accessibility
Keyboard operation for selection/citations, contrast, screen reader labeling, 125–200% scaling, Vietnamese text, large PDFs memory virtualization.
## Error states
NO_MODEL, MODEL_OFFLINE, PDF_PASSWORD_REQUIRED, PDF_CORRUPT, OCR_UNAVAILABLE, SOURCE_MISSING, CITATION_INVALID, INDEX_STALE, STORAGE_FULL, JOB_INTERRUPTED. Specific remedy and link to log each.
