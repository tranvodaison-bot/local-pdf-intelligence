# Baseline audit — CTO-001, 2026-11-13

- Workspace: `G:\My Drive\01_AI_SYSTEM\09_Apps_Project\08_Notebook_local`.
- Remote: `https://github.com/tranvodaison-bot/local-pdf-intelligence.git`; branch `master` and remote HEAD both `ce88e41fc24ddfa3f3259ed7b7f9fb4b9542ba6a` on inspection. Non-force push to feature branch required.
- Local source present: initial SQL, FastAPI health, migration runner, tests and specification. No Tauri frontend, PDF viewer, OCR or RAG implementation existed at audit.
- ZIP extracted in temporary workspace directory; all 23 manifest entries in archive matched. Workspace had 22 unchanged entries; `docs/12_HANDOVER_REGISTER.md` differed because it recorded subsequent foundation work. No entries missing. Manifest applies to original handoff, not subsequent edits.
- Existing `.gitignore` excludes PDF, env, models and SQLite; ZIP and user-supplied work order remain untracked and were not staged.
- `git ls-remote origin` returned HEAD and refs/heads/master at the SHA above. Remote read verified; feature-branch write to be verified by actual push.
- SQLite initial migration works in limited tests; cross-table citation consistency and real source anchors unresolved. Auth handshake, file picker, PDF rendering, extraction and end-to-end evidence absent. pypdf installed package metadata states BSD-3-Clause; transitive license review and release approval remain outstanding.
- Gate G0: baseline and Git remote read verified, with documented handover-register delta. Gate G1: NOT MET.
