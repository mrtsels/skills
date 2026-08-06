# De-AI-ify Examples

From quant-academy task-4 C++ SVD project. Demonstrates before/after of user-correction.

## Code Comments

- C++ header: 262 → 206 lines. Long section dividers (`// ────────────────── 1.1 — Matrix ...`) replaced with `// 行优先矩阵`, `// 基础线代`, `// 幂迭代`
- pybind11 wrapper: 73 → 45 lines. Removed `// 转换函数 —— numpy <-> 我们自己的 Matrix`, kept just the code
- Python svd wrapper: 68 → 18 lines. Full numpy-style docstring → `"""cpp svd wrapper"""`

## Documentation

- validation_report.md: 74 → 41 lines. Removed "near machine epsilon", numbered algorithm steps, verdict table with all-✅, "Overall: PASS ✅". Replaced with single-paragraph algorithm description, raw data table, one-line conclusion.
- Then user said rewrite in English → stripped further. Then fixed Title Case on all headers.
- README: 82 → 48 lines. Removed Chinese/English mixing, long directory tree annotations, verbose build instructions with explanations.

## Key Principle

"人类不喜欢写那么多字" — when user says "still AI", cut more. The natural human tendency is to write LESS, not more.

## Session Pattern (2026-07-27)

User went through 5 rounds of de-AI-ifying task-4:
1. C++ comments trimmed (262 → 206 lines)
2. pybind/py files trimmed (73 → 45 cpp, 68 → 18 py)
3. validation_report rewritten from AI-formal → human Chinese
4. Then asked to rewrite in English
5. Then fixed capitalization

Each round the user said it was still too verbose. The lesson: don't stop after one pass. Humans write less than AI thinks they do. English reports need Title Case headers. READMEs should be code and commands, not explanations.

### Post-submission polish (2026-07-27, turns 5-7 after main work):

- validation_report rewritten in English, then capitalization fixed: section headers, table column names, code names (NumPy, Python, etc.) all Title Case
- README: stripped Chinese/English mix, long directory tree, verbose build explanations. Just code blocks and a single-line algorithm.
- LaTeX: all math in both README and report wrapped in `$...$`. Raw unicode math (`λ`, `σ`, `A^T A`) in markdown docs → LaTeX delimiters.
- .gitignore extracted from root to task-local for submission (academic context: shows git usage as part of deliverable)
