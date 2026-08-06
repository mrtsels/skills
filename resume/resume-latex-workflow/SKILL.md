---
name: resume-latex-workflow
description: "Iterative resume editing with LaTeX: scan project → write entry → compile → refine bullets (+N -N) → commit. Covers the project-to-resume pipeline and the micro-adjustment cycle specific to this user."
version: 1.1.0
author: Hermes
platforms: [macos]
---

# Resume LaTeX Workflow — Iterative Editing Pipeline

> 本技能为 LaTeX 简历工作流类技能的伞(umbrella),已吸收以下技能(2026-08 合并):
> `latex-resume-workflow`、`resume-latex-edit`、`resume-latex-cn-workflow`、`resume-compile-commit`、
> `resumes-git-workflow`、`cjk-resume-setup`、`bilingual-latex-resume`、`bilingual-resume`、
> `resume-skills-layout`、`latex-resume-formatting`、`resume-ng`、`latex-bullet-fill-optimizer`。
> 各技能完整原文见 `references/absorbed-*.md`。


## When to Use

- User says "add this project to my resume"
- User is refining resume bullet points with word-count adjustments
- User needs a LaTeX resume compiled and previewed
- Working in `/Users/minimx/Documents/resumes/resume-alex/` or similar resume dir
- User drops a source (existing docx, repo path, PDF) and wants an entry extracted from it

## Prerequisites

- XeLaTeX (TeX Live): `which xelatex`
- Git root at `~/Documents/resumes/` (not a per-project subdir) — AGENTS.md at repo root enforces immediate commit+push
- Two entry classes: `resume-en.cls` (English, `\use_i:nn`) and `resume-zh.cls` (Chinese, `\use_ii:nn`)
- Entries are **bilingual** via `\resumeenif{EN content}{ZH content}` in a single `.tex` file
- All entries under `entries/` as `\input{entries/<prefix>-<name>}`

## File Layout

| Artifact | Path |
|----------|------|
| Main .tex | `resume.tex` |
| Document class | `resume.cls` |
| Entries | `entries/<prefix>-<name>.tex` |
| Output PDF | `resume.pdf` |

Naming convention: `internships-company.tex`, `research-project.tex`, `education-school.tex`.

## Entry Format

The resume uses **bilingual entries** — each `.tex` file under `entries/` holds both EN and ZH content via the `\resumeenif{}` macro. `resume-en.cls` activates `\use_i:nn` (shows EN block), `resume-zh.cls` activates `\use_ii:nn` (shows ZH block).

```latex
\resumeenif{
  \ResumeItem{\textbf{\ResumeUrl{url}{Company or Project Name}}}
  [Role | Supervisor: Prof. Full Name]
  [MM/2026\textendash MM/2026]
  [City]

  \begin{itemize}
    \item Past-tense action verb, quantified results, no articles a/an/the.
  \end{itemize}
}{
  \ResumeItem{\ResumeUrl{url}{中文公司名}}
  [中文职位]
  [2026/07\textendash 2026/08]
  [城市]

  \begin{itemize}
    \item 中文bullet，强动词开头，量化结果。
  \end{itemize}
}
```

## Procedure

### 1. Verify Company Name from Official Website

Before writing a company name in `\ResumeUrl{url}{Company Name}`, visit the official website to confirm the full legal name. Examples: Oakcean Capital Limited (oakceancapital.com), xQuant (xquant.com), Excellence Information Technology Corp., Ltd. (excellence.com.cn). Do not use shortened or assumed names.

### 2. Extract Content from Existing docx/PDF

When user provides a docx file, use `read_file` to auto-extract content. Match English resume style (strong past-tense verbs, quantified results). **Cross-check metrics against the actual source repo or report — docx claims may be stale or inaccurate.**

### 3. Scan Project Repo for Accurate Metrics

Given a source repo path:
- Read `README.md`, any report files (`reports/*.md`), and key source code
- Extract specific metrics (RMSE, accuracy, speedup, etc.) from the actual report
- Compare against any docx-derived numbers — use the report data if they differ

### 4. Create Entry File

a. Create the entry at `entries/<prefix>-<name>.tex` with 3 bullets: architecture/approach, key results with metrics, and ablation/insight.
b. Add `\input{entries/<prefix>-<name>}` to `resume.tex` in the correct section, maintaining time-descending order.

### 5. Iterative Bullet Tuning

The user gives shorthand for word-count adjustments:

| Input | Meaning |
|-------|---------|
| `#1 +2 |` | Bullet 1: +2 words |
| `#3 -1 |` | Bullet 3: -1 word |
| `+2 0 +3` | Bullet 1: +2, Bullet 2: 0, Bullet 3: +3 |
| `-1 0 0` | Bullet 1: -1 word, Bullets 2-3: no change |

**Balancing technique:** When two bullets in a section have uneven lengths (one wraps mid-line while the other fits cleanly), the user may say "选两行做减法 两行做加法 你取舍一下" — choose one bullet to subtract from and another to add to, using judgment. Prioritize keeping the more substantive/technical bullet and trimming redundant filler from the other. Common cuttable filler in ZH: `的`, `了`, `进行`, `实现`, `使用`, `完成`, `通过`, `以`, `与`, `在`, `来`, `于`, `覆盖`, `算法`, `模型`. Common additions: qualifiers, context phrases, domain terms that were previously trimmed. Balance such that both bullets have approximately the same rendered line count.

### 6. Hide/Show Entries

To hide a project without deleting its file, comment out the `\input{}` line in `resume.tex`:
```latex
%\input{entries/research-numerical-hierarchy}
```
To restore, remove the `%`.

### 7. Compile

Compile both EN and ZH versions. Always two passes each:

```bash
cd /Users/minimx/Documents/resumes/resume-alex
xelatex -interaction=nonstopmode resume-en.tex
xelatex -interaction=nonstopmode resume-en.tex
xelatex -interaction=nonstopmode resume-zh.tex
xelatex -interaction=nonstopmode resume-zh.tex
```

Show PDF after every compile via `MEDIA:resume-en.pdf`.

### 8. Commit and Push (Immediate)

Per AGENTS.md: **every file change must be committed and pushed immediately**, including word-count micro-tweaks. No batching.

```bash
git add entries/<changed-entry>.tex   # explicit paths only — no git add .
git commit -m "<type>: <description>"   # feat/fix/docs/chore/reorg
git push origin main
```

⚠️ Git root is `/Users/minimx/Documents/resumes/`, not the per-project subdir. Always cd to the git root before git commands. Never `git add .` or `git add -A` — use explicit file paths. Never force push.

### 9. Reorder Sections

Each section lists entries by time descending (most recent end date first). Same end date → later start date first.

**Date-change rule:** Whenever a date is modified on any entry, immediately re-check the ordering of that section. Move the updated entry to its correct position, then recompile. Do not leave a date-changed entry in its old position.

### 10. Skills Section Maintenance

Skills should only list tools/languages actually used in the resume's projects. Four lines: Languages, Programming, AI/ML, Infrastructure. If user says "tech超字数了" or "ML/AI也是", simplify to bare language names without parentheses/framework details.

For aligned labels, use `\makebox[7em][l]{\textbf{Label:}} content` inside itemize:
```latex
  \item \makebox[7em][l]{\textbf{Languages:}} English (TOEFL 109), Mandarin (native), Cantonese (fluent)
  \item \makebox[7em][l]{\textbf{Programming:}} Python, Java, JavaScript, SQL, Bash, \LaTeX, Git
  \item \makebox[7em][l]{\textbf{AI/ML:}} PyTorch, HuggingFace, Transformers/LLMs, GNN, Bayesian inference
  \item \makebox[7em][l]{\textbf{Infrastructure:}} Docker, Linux, MongoDB, DuckDB, FastAPI, Flask, Nginx
```
Note: `pdfminer` extraction of PDFs with `\makebox` may show content in wrong reading order despite correct visual rendering. Use `vision_analyze` on a screenshot thumbnail (generated via `qlmanage -t`) to verify visual layout when in doubt.

### 11. Justification

For better text alignment, add to `resume.cls`:
```latex
\usepackage{microtype}
\usepackage{ragged2e}
```
And `\justifying` after `\begin{document}` in `resume.tex`.

## Quick Reference

| Action | Command |
|--------|---------|
| Compile | `xelatex -interaction=nonstopmode resume.tex` × 2 |
| New entry | `entries/<prefix>-<name>.tex` + `\input{}` in resume.tex |
| Entry with URL | `\ResumeItem{\textbf{\ResumeUrl{url}{Title}}}` |
| Hide entry | `%\input{entries/<name>}` in resume.tex |
| Date format | `[MM/2026\textendash MM/2026]` |
| Bullet tuning | `+N +M +K` or `-N -M -K` |
| Commit | `git add -A && git commit -m "<type>: <desc>" && git push` |

## Education Entry Linking

The university name in `education-*.tex` can link to the specific programme page:

```latex
\ResumeItem{\ResumeUrl{https://www.ie.cuhk.edu.hk/programmes/bsc-in-mieg/}{Chinese University of Hong Kong}}
```

Find the programme page by navigating from the department website (e.g., ie.cuhk.edu.hk → Programmes → Undergraduate → MIEG), not from CUHK's central admissions site which often returns 404 on sub-pages.

## Pitfalls

- **Never force push or initialize a repo without explicit user permission.** `git status` showing "No commits yet" may indicate a stale branch reference, not an empty repo. Check `git reflog` for existing history before creating any root commit. A force push destroys the entire remote history — irreversible without local reflog. Always verify the actual git history before any destructive operation.
- **One page limit**: Adding too much text overflows to page 2. Default to 1 page unless user accepts 2.
- **`(expected)` dates**: Remove when the month has passed. Current date is July 2026.
- **Supervisor NOT Advisor**: Always use "Supervisor" in the role line.
- **Verify source metrics**: docx numbers may differ from actual report data. Always verify against the source repo.
- **Single-pass compile**: Always run xelatex twice — second pass resolves hyperref outlines and cross-refs.
- **Entry not in resume.tex**: Creating an entry file alone is not enough; it must be `\input{}`-ed.
- **\\ResumeItem location**: Location #5 uses `[]` brackets, not `{}`.
- **Bare `%` in LaTeX**: In entry `.tex` files, every `%` outside math mode must be `\%`. Forgetting this silently comments out the rest of the line. Always escape `%` in Chinese bullets (`60%` → `60\%`).

## Verification

```bash
cd /Users/minimx/Documents/resumes/resume-alex && xelatex -interaction=nonstopmode resume-en.tex | grep "Output written"
```

Should show `resume-en.pdf (1 page)`. Check both EN and ZH outputs.

## Reference Files

- `references/post-investment-bullets.md` — Domain-specific bullet templates for FOF post-investment / compliance roles (this session).

---

## Research Entry from a Codebase

Use when the user has a code repository (project, research code, course project) and needs a formatted LaTeX `\ResumeItem` entry for the Research & Projects section of their CUHK-style LaTeX resume.

## Workflow

### 1. Scan the Codebase

Read in this order:

- **README.md** — problem statement, motivation, key results, high-level architecture
- **TASK.md / plan.md / PHASES.md** — structured development plan with per-phase metrics
- **Core source files** — focus on architecture and key results:
  - `model/model.py` or equivalent — entry point, forward pass, loss function
  - `model/encoder.py` — message-passing structure
  - `eval/metrics.py` — evaluation metrics definitions
  - `graph/` or `data/` — data representation
- **Experiment results** — `experiments/`, `results/`, benchmark files

### 2. Extract Key Information

| Category | What to Extract |
|----------|-----------------|
| Problem | What gap or limitation does this address? |
| Approach | Model architecture, graph construction, loss formulation |
| Key Metrics | Accuracy, AUROC, F1 change (in pp), MSE, speedup, cross-domain transfer |
| Unique Contribution | Novel technique, ablation finding, architectural insight |

Prioritize **quantified results with baselines** — "92% acc" without context is weak. "92% acc (+3pp over baseline)" is strong.

### 3. Format as LaTeX Entry

Match the existing file convention (`entries/research-<shortname>.tex`):

```latex
\ResumeItem{\textbf{Project Title}}
[Role | Supervisor: Prof. Name]
[MM/YYYY\textendash MM/YYYY]
[Location]

\begin{itemize}
  \item Architecture/approach description with \LaTeX math notation —
        graph definition $G = (V, E)$, loss $\mathcal{L}$, key parameters
  \item Key metric-driven result with baseline comparison and specific numbers
  \item Additional contribution — ablation study, cross-domain transfer,
        architectural innovation
  \item (optional) Advanced feature — multi-modal fusion, self-supervised pretraining
\end{itemize}
```

### 4. Tone Guidelines

- **Supervisor, not Advisor** — always use "Supervisor: Prof. Name" in the role line. Never "Advisor". If no supervisor is known, use "Independent Research".
- Each bullet: dense, single sentence, starts with action verb (Designed / Built / Introduced / Achieved)
- Use \LaTeX math for: loss functions, variables, arrows ($\to$, $\Delta$, $\mathcal{L}$, $O(N^{2.807})$)
- Specific percentages over vague adjectives
- Date range format: `[MM/YYYY\textendash MM/YYYY]` — use \textendash (not `--`), no extra spaces around it
- Do NOT fabricate supervisor names — use "Independent Research" if unclear
- 4 bullets max — pick highest-impact contributions; user may request fewer after trimming/merging

### 5. Content Polishing (Post-Draft, when user requests)

- **Trim bullets**: shorten each line by ~3 words — remove filler (various, several, very, significant, comprehensive), keep metrics and technical specifics
- **Merge related bullets**: combine approach + architecture into one when they share a logical thread. Example: graph construction + multi-head prediction pipeline merge naturally — the graph IS the input to the pipeline. Don't split them.
- **Remove "(expected)"**: once the end date has passed (reference: 2026-07-22), strip "(expected)" from EVERY entry with a past end date. Check globally.
- **Remove unrealistic entries**: skip projects the user deems not practical to include (e.g. says "不现实")
- **Word-count micro-adjustments**: user may request precise per-bullet changes with syntax like `+2 +2 +2` or `+1 +2 +2` or `-1 0 0`. Each number = words to add/remove on that bullet index (1-indexed). Apply exactly — do not round. See `latex-resume-workflow` for full pattern.

### 6. Valid Bullet Content Types

When constructing bullets, draw from these categories (pick 3–4 highest impact):

- **Architecture** — graph design, message-passing scheme, loss formulation with LaTeX math
- **Key metrics** — accuracy, AUROC, F1 change (in pp), MSE, speedup — always with baseline comparison
- **Cross-modal fusion** — attention-based fusion between modalities (e.g. structural features querying visual features), architectural decisions (pre-encoder vs post-encoder), ablation results
- **Cross-domain transfer** — zero-shot and fine-tuned performance on out-of-distribution datasets
- **Real-world validation** — metrics on real (not synthetic) data, pipeline improvements on production-grade inputs

### 7. Company Name Verification

For internship/company entries, **verify the full legal name** by visiting the official website:
1. Navigate to the company's site (use the URL the user provides or look it up)
2. Check footer, about page, or English-language version for the registered name
3. Cross-reference with email signatures from correspondence when available
4. Use the full legal name (e.g. "Oakcean Capital Limited", "Guangdong Yuecai Trust Co., Ltd.")
5. Wrap in `\ResumeUrl{url}{Legal Name}`

### 7. Compilation & Review Loop

After creating the entry:
1. Add `\input{}` to `resume.tex` at the correct time-descending position
2. Run `xelatex -interaction=nonstopmode resume.tex` twice
3. Present the compiled PDF — do not skip this step

## Pitfalls

- **Don't list all features** — pick 3-4 most impressive contributions
- **Baseline context required** — "93.2% acc" without baseline is weak; "93.2% acc, AUROC 0.989" is acceptable if metric is standard
- **Don't guess supervisor** — without explicit mention, use "Independent Research"; never fabricate a name
- **Terminology consistency**: normalize all role labels to "Supervisor" (never "Advisor") across all entries in the same resume
- **Date formatting**: use `\textendash` (not `--`) for date ranges; remove "(expected)" once the end date has passed
- **File path convention** — save as `entries/research-<project-shortname>.tex` matching existing entries
- **Verify format** — read back the file to ensure no broken LaTeX, and check bullet length against existing entries for consistency
- **Codebase conventions** — if the project has a TASK.md with structured phases, prioritize Phase summaries and Results tables over README prose

## Related Skills

- `resume-bullet-writer` — fine-tuning individual bullet strength
- `resume-section-builder` — overall section structure (non-agent-created, read-only)

---

## Version Management

Use when the user needs to manage multiple resume versions for different applications.

## Version Management System

1. **Master Resume**: complete, unedited version with all experience
2. **Tailored Versions**: one per job application, derived from master
3. **Version Tracking**: maintain a changelog explaining what changed and why

## Master Resume Rules

- Contains ALL experience (no length limit)
- Includes both current and past roles
- Documents all projects and achievements
- Acts as single source of truth
- Updated when new experience is gained

## Tailored Version Process

1. Copy master resume for each application
2. Reorder or rephrase bullets for relevance
3. Add missing keywords from job description
4. Delete irrelevant bullets
5. Save with naming convention: LastName_Role_Company_Date
6. Log changes in version tracking document

## Version Tracking Template

| Date | Version | Target | Changes Made |
|------|---------|--------|-------------|
| 2024-01-15 | v1 | Master | Initial |
| 2024-01-20 | v2 | Google PM | Reordered bullets, added product keywords |
