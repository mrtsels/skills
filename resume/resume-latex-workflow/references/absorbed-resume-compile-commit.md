---
name: resume-compile-commit
description: Compile LaTeX resumes twice, push fresh
  PDFs, enforce git discipline.
version: 0.1.0
author: Hermes
platforms: [macos]
metadata:
  hermes:
    tags: [Resume, LaTeX, XeLaTeX, Git]
---

# Resume Compile and Commit Workflow

Enforce the compile + commit cycle after every `.tex` change in any resume project (`resume-alex-en`, `resume-example-zh`, etc.). The core rule: delete old PDF, compile × 2, show fresh PDF, then git commit + push. Corrections from prior sessions: never show a stale PDF, never forget to commit.

## Prerequisites

- XeLaTeX: `which xelatex`
- `resume.cls` in the resume directory.
- AGENTS.md in repo root requiring immediate commit+push.

## Procedure

### 1. Clean Compile (× 2)

```bash
cd <resume-directory>          # e.g. resume-alex-en or resume-example-zh
rm -f resume.pdf               # MUST delete old PDF first
xelatex -interaction=nonstopmode resume.tex
xelatex -interaction=nonstopmode resume.tex
```

Delete the stale PDF before compiling to guarantee the output is fresh — showing a previous turn's PDF is a common failure mode.

### 2. Show Results

Display the new PDF via `MEDIA:resume.pdf` (or `main.pdf` for example resumes). Do NOT skip this step after compiling.

### 3. Git Commit

```bash
cd <project-root>              # e.g. /Users/minimx/Documents/resumes
git add -A
git commit -m "<type>: <description>"
git push origin main
```

Every `.tex` change must be immediately committed and pushed. No accumulation.

## Pitfalls

- **Stale PDF output**: The most common mistake. Always `rm -f resume.pdf` before compiling. Never assume a previous compile is still valid.
- **Skipped git push**: `git commit` alone leaves the work only local. Always run `git push origin main` after commit. The user can spot a missing push.
- **Skipped second pass**: Always compile exactly twice. Missing the second pass can produce wrong cross-references and page breaks.
- **Skipped commit**: After every file change (including new entries, metadata edits, word-count adjustments), commit immediately. Not at the end of a batch.
- **Skipped show**: After compiling, always include the `MEDIA:` reference so the user can see the result.
- **`main.tex` overrides `resume.cls`**: If you edit `resume.cls` but the PDF doesn't change, `main.tex` may have conflicting `\linespread` or `\ctexset` settings. Grep both files: `grep -n "linespread\|ctexset" resume.cls main.tex`.

## Verification

```bash
cd resume-alex-en && rm -f resume.pdf && xelatex resume.tex | grep "Output written"
```
Expected: `Output written on resume.pdf (1 page).`
