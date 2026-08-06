---
name: project-to-resume
description: >-
  Extract project context and generate resume-ready bullets.
version: 0.1.0
author: Hermes
platforms: [macos, linux]
metadata:
  hermes:
    tags: [Resume, Content-Generation, CV]
---

# Project to Resume Bullet

Extract metadata from an arbitrary directory (code project or document-based workflow) and produce resume-ready bullet points following the style rules in `AGENTS.md`. Handles both code repos (README, source tree) and document-heavy directories (PDFs, spreadsheets, reports, financial data). Updates the `resume-xie` LaTeX source with the new content.

Designed to be invoked mid-conversation when the user says something like "add this to my resume" or "make this work for my CV."

## When to Use

- User says: "Add this to my resume" while inside any project/work directory.
- User says: "Turn this repo into a resume bullet."
- User says: "I worked on this project, write it up for my CV."
- User has just completed a task/challenge and wants to record it.
- The current working directory is NOT inside the `resumes/` repository.

## Prerequisites

- The directory must contain recognizable content: README, source code, PDFs, spreadsheets, markdown docs, or structured data files.
- The `resumes/` repository must exist at `~/Documents/resumes/`.
- The `resume-xie` instance must exist at `~/Documents/resumes/resume-xie/`.

## How to Run

This skill is NOT invoked by loading it alone. It defines a task template that you invoke:

1. Load the skill: `skill_view(name='project-to-resume')`
2. Follow the Procedure below for the current project directory.

## Procedure

### Phase 1 — Project reconnaissance

From the project directory, collect what's available:

**For code projects:**
1. **README** — read with `read_file`. Extract purpose, features, architecture, tech stack.
2. **Package manifest** — `pyproject.toml`, `package.json`, `Cargo.toml`, `go.mod`, or `CMakeLists.txt`. Extract dependencies, languages.
3. **Source tree** — `search_files(target='files', pattern='*.py')` (or language equivalent). Count files, identify architecture (CLI, server, library, notebook).
4. **Git metadata** — `git log --oneline -30` for volume; `git shortlog -sn` for contributor count.

**For document-based / workflow directories (e.g., `yuecai`):**
1. **Inventory** — `search_files(target='files', pattern='*.md')`, `*.pdf`, `*.xlsx`, `*.docx`, `*.csv`. Categorize what the directory contains.
2. **Key docs** — read any README, index, AGENTS.md, or summary files first. Then sample key reports, PDFs, spreadsheets using `read_file` (auto-extracts text from .docx/.xlsx).
3. **Structure** — list top-level subdirectories with `search_files`. Identify the domain (financial due diligence, research, data analysis, consulting).
4. **Git metadata** — same as code projects if `.git` exists.

### Phase 2 — Generate resume bullets

Using the collected data, write **2-3 bullet points** following these rules (from `AGENTS.md`):

- No articles (a, an, the) — unless grammatically unavoidable
- No passive voice — "was responsible for" → "Led"; "was involved in" → "Contributed to"
- No filler words — various, several, multiple, significant, very
- Each bullet starts with a **past-tense action verb**, no subject
- Nouns preferred over gerunds — "Reduced latency by 40%" not "Helped in reducing..."
- Include metrics where available

**Metrics for code projects:** lines of code, speedup factor, users, downloads, repo stars, test coverage, latency reduction.
**Metrics for document/work projects:** entities covered (funds, companies, reports), data points analyzed, documents produced, pages/reports delivered, meetings conducted, coverage rate (e.g. "100% asset coverage").

### Phase 3 — Integrate into resume-xie

1. Find the right section in `~/Documents/resumes/resume-xie/main.tex` — code projects go under `\section{Research \& Projects}`, work/internship content goes under `\section{Internships}` (add a new `\ResumeItem` with employer name).
2. Add a new `\ResumeItem` block with project title, subtitle (role + context), date (estimated), and Location.
3. Build with `latexmk` and verify the PDF compiles to 1 page.
4. Run the bullet-fill check (`latex-bullet-fill-optimizer`) to ensure last lines are ≥93%; if not, trim text.
5. `git add` + `git commit -m "feat: add <project-name> to resume"` + `git push`.

### Phase 4 — Record the decision

Save a memory so next time the directory is encountered, the agent knows it's already on the resume:

```
memory(action='add', target='memory',
       content='<project-name> resume bullet added (section: <section>, date: <date>)')
```

## Examples

**Code project:** User just pushed a CLI tool and says "add this to my resume." Phase 1 reads README, pyproject.toml, git log. Phase 2 produces:

```
\item Built CLI tool automating dataset cleaning and transformation pipelines; processed 10+ CSV/JSON formats with configurable schema validation and deduplication
\item Designed plugin-based architecture supporting custom transformation rules; reduced manual cleaning overhead by 80\% across 3 internal teams
\item Published as pip-installable package; achieved 100+ downloads in first week with CI/CD via GitHub Actions
```

**Document project (yuecai):** User says "add yuecai work to resume." Phase 1 inventories markdown reports, PDF due diligence packs, spreadsheets; reads the project AGENTS.md and a sample fund report. Phase 2 produces:

```
\item Conducted due diligence on 10+ private fund managers for FoF asset pool admission; organized audit reports, valuation statements, and questionnaires into numbered, source-mapped evidence packages
\item Analyzed fund strategy allocations and cross-product asset sizes across 6 internal fund-of-fund shared directories; reconciled asset coverage to 100\% using multi-source triangulation
\item Authored structured research visit memos and fund comparison reports used by investment committee for pool admission decisions
```

## Pitfalls

- **Don't invent metrics** — if no hard data exists, frame scope ("Covered N entities" or "Processed N data sources") instead of fabricating percentages.
- **Don't oversell** — a 2-day task gets 1 bullet, not 3.
- **Don't duplicate** — check the .tex file with `search_files` before adding.
- **Don't exceed 1 page** — if adding overflows the page, trim older content first.
- **Respect the style rules** — no articles, active voice, strong verbs.
- **For document projects:** the user may have detailed knowledge that isn't reflected in file contents. Use what's in the files as the factual base and ask the user to fill in scope/impact gaps rather than guessing.

## Verification

```bash
cd ~/Documents/resumes && git diff --stat
```
And:
```bash
python3 -c "import fitz; doc=fitz.open('resume-xie/main.pdf'); print(len(doc), 'page(s)')"
```
