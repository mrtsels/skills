---
name: resume-latex-edit
description: Edit LaTeX resume entries, compile, tune, and
  commit.
version: 0.1.0
author: Hermes
platforms: [macos]
metadata:
  hermes:
    tags: [Resume, LaTeX, XeLaTeX, Git]
---

# Resume LaTeX Editing Workflow

Edit `resume-alex-en/resume.tex` and its modular `entries/` files. Each entry is a separate `.tex` file under `entries/`. After every change: compile × 2 → show PDF → commit + push.

## When to Use

- User asks to add/remove/edit a resume entry (internship, research, project).
- User provides a project path and wants a research/internship bullet extracted.
- User says "add N words" / "remove N words" to specific bullets.
- User wants to reorder sections by date.
- User provides a supervisor name, URL, or date change.

## Prerequisites

- XeLaTeX (TeX Live): `which xelatex`
- `resume.cls` in the same directory as `resume.tex`.
- All entries live under `entries/` as `\input{entries/<prefix>-<name>}`.
- AGENTS.md in repo root enforces immediate commit+push.

## Entry Format

```latex
\ResumeItem{\textbf{Title}}
[Role | Supervisor: Prof. Name]
[MM/2026\textendash MM/2026]
[City]

\begin{itemize}
  \item Bullet text with strong verb past-tense, quantified results.
  \item ...
\end{itemize}
```

For linked titles/companies, wrap in `\ResumeUrl{url}{display}`:
```latex
\ResumeItem{\textbf{\ResumeUrl{https://github.com/user/repo}{Title}}}
```

## Procedure

### 1. Scan a Project and Create an Entry

Given a project path, first read README.md and key source files (`search_files`, `read_file`) to understand the work. Then:

a. Create the entry file at `entries/<prefix>-<name>.tex` using the format above, typically 3 bullets covering: architecture/approach, key results with metrics, and cross-domain/additional insight.

b. Add `\input{entries/<prefix>-<name>}` to `resume.tex` in the correct section (Education / Internships / Research & Projects), maintaining time-descending order within each section.

### 2. Iterative Bullet Tuning

When the user says "+N +M +K" (one number per bullet), add exactly N/M/K words to bullets 1/2/3 respectively. "−N" means remove N words. Prefer adding descriptive adjectives or clarifying technical terms; avoid filler.

### 3. Edit Metadata

- **Supervisor**: `[Role | Supervisor: Prof. Full Name]` — NOT "Advisor".
- **Date**: `[MM/2026\textendash MM/2026]` — remove `(expected)` if date has passed.
- **Location**: `[City]` for in-person, `[(Virtual)]` for remote.
- **Company URL**: `\ResumeItem{\ResumeUrl{https://company.com}{Company Full Name}}`.

### 4. Compile

```bash
cd /path/to/resume-alex-en
xelatex -interaction=nonstopmode resume.tex
xelatex -interaction=nonstopmode resume.tex   # second pass for cross-refs
```

Always compile twice. Show the resulting PDF with `MEDIA:resume.pdf`.

### 5. Commit and Push

Per AGENTS.md: every file change must be immediately committed and pushed.

```bash
cd /path/to/resumes
git add -A
git commit -m "<type>: <description>"   # feat/fix/docs/chore/reorg
git push origin main
```

### 6. Reorder Sections

Each section (Internships, Research & Projects) must list entries by time descending (most recent end date first). When two entries share the same end date, later start date comes first.

### 7. Justification

If the user asks for better text alignment, add to `resume.cls`:
```
\RequirePackage{microtype}
\RequirePackage{ragged2e}
```
And add `\justifying` right after `\begin{document}` in `resume.tex`.

## Quick Reference

| Action | Command |
|--------|---------|
| Compile | `xelatex -interaction=nonstopmode resume.tex` × 2 |
| New entry | `entries/<prefix>-<name>.tex` + `\input{}` in resume.tex |
| Link in title | `\ResumeItem{\textbf{\ResumeUrl{url}{text}}}` |
| Link in body | `\ResumeUrl{url}{text}` |
| Date format | `[MM/2026\textendash MM/2026]` |
| Bullet tuning | `+N +M +K` or `-N -M -K` |

## Pitfalls

- **One page limit**: Adding too much text overflows to page 2. The PDF must stay at 1 page unless the user explicitly accepts 2 pages.
- **`(expected)` dates**: Remove when the month has passed. Current date is July 2026.
- **Supervisor NOT Advisor**: Always use "Supervisor" not "Advisor" in the role line.
- **Forgotten compile**: Always compile × 2 after every `.tex` change, not just at the end.
- **Forgotten commit**: Per AGENTS.md, any file modification must be committed+push immediately.
- **Entry not in resume.tex**: Creating an entry file is not enough — it must be `\input{}`-ed in `resume.tex`.

## Verification

```bash
cd /path/to/resume-alex-en && xelatex -interaction=nonstopmode resume.tex | grep "Output written"
```
Should show `resume.pdf (1 page)`.
