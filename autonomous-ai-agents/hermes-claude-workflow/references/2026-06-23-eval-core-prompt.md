# 2026-06-23 — Eval Core (Phase 4.5.1 + 4.5.2)

**Model:** `deepseek-v4-pro`
**Cost:** TBD
**Worktree:** feat/eval-core

## Key design decisions
- Metrics bundle as dataclass (not plain dict)
- Evaluator supports per-category and per-source breakdown
- AlignmentError: constraint-aware (checks LEFT/RIGHT/TOP/BOTTOM alignment relationships)

## Prompt file
/tmp/bgg-prompt-D.md (see session transcript for full text)
