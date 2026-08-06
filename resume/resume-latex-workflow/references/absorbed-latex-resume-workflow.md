---
name: latex-resume-workflow
description: Maintain a modular LaTeX resume with entries/ subdirectory — conventions for ordering, compilation, date handling, and entry lifecycle.
---

# LaTeX Resume Workflow

Guidelines for maintaining a LaTeX resume project that uses a `resume.cls` class file and a modular `entries/` subdirectory pattern. Covers compilation discipline, section ordering, date conventions, and entry lifecycle.

## When to Use

- User is editing `.tex` files in a resume project
- User wants to add/remove/reorder entries
- User needs to compile LaTeX resume to PDF
- User is working with `\ResumeItem` / `\input{entries/...}` patterns

## Directory Layout

```
resume-project/
├── resume.tex          # Main document — orchestrates sections via \input{}
├── resume.cls          # Document class (e.g. resume-ng or custom)
├── entries/            # One .tex file per entry
│   ├── education-cuhk.tex
│   ├── internships-yuecai.tex
│   └── research-xyz.tex
└── resume.pdf          # Compiled output
```

## Entry File Format

Core structure shared by all entry types:

```latex
\ResumeItem{\textbf{Project/Company Name}}
[Role/Type | Supervisor Info]
[Date Range]
[Location]

\begin{itemize}
  \item \textbf{Bold lead} followed by concrete detail with metrics.
\end{itemize}
```

### Format by Entry Type

**Research entries** (`entries/research-<shortname>.tex`):
- Role line: Use `Supervisor:` (never `Advisor`). If no supervisor known, use `Independent Research`.
- Date: `[MM/YYYY\textendash MM/YYYY]` — use `\textendash`, no extra spaces. Remove `(expected)` once the end date passes.
- Location: `[City]` — e.g. `[Hong Kong]`

**Internship entries** (`entries/internships-<company>.tex`):
- Company name wrapped in `\ResumeUrl{url}{Legal Name}` — use the full legal name, not a trading name.
  - E.g. `\ResumeUrl{https://www.oakceancapital.com}{Oakcean Capital Limited}`, `\ResumeUrl{https://www.yuecaitrust.com}{Guangdong Yuecai Trust Co., Ltd.}`
- **Chinese company names**: look up the official English name on the company's website (check footer, about page, or English-version site). Chinese fintech systems: e.g. 衡泰 → xQuant (xquant.com), 恒生 → Hundsun. Do not guess or machine-translate.
- Role line: `[Job Title | Additional Context]` — e.g. `[Quant Intern | Virtual Internship Program]`
- Location: Use `[(Virtual)]` for remote-only positions, `[City]` for on-site.

**Education entries** (`entries/education-<school>.tex`):
- University only — omit high school / secondary school entries.

## AGENTS.md Git Enforcement (CRITICAL)

The `resumes/` repository has an `AGENTS.md` that requires **immediate commit + push after every file change**. This rule is mandatory — do not batch changes or skip pushing.

```bash
# After every .tex edit + compilation:
git add <specific-file(s)>   # use explicit paths or git add -A
git commit -m "fix/docs/feat: <short english description>"
git push origin main
```

**Forbidden:** modifying multiple files without committing in between, bare `git add .` (prefer `git add -A` or explicit paths), empty commit messages, `git --amend`, skipping push.

## Compilation Discipline (CRITICAL)

**Recompile and show PDF after EVERY `.tex` change — no exceptions.** Run xelatex twice for stable cross-references:

```bash
cd resume-xie/
xelatex -interaction=nonstopmode resume.tex
xelatex -interaction=nonstopmode resume.tex
```

**Always present the compiled PDF** (embed via `MEDIA:/path/to/pdf`) immediately after every edit so the user can visually verify. Do not stop after editing — the compile-and-show loop is mandatory.

### Justification & Microtype

To improve body text justification (reduce ragged right edges, tighten line breaks):

1. Add to `resume.cls` preamble:
   ```latex
   \RequirePackage{microtype}
   \RequirePackage{ragged2e}
   ```
2. Add `\justifying` after `\begin{document}` in main `.tex` file.

`microtype` provides character protrusion and font expansion for tighter paragraph justification. `ragged2e` provides the `\justifying` command. Essential for bullet-heavy resumes where tight spacing makes default LaTeX justification look uneven.

## Compilation One-Liners

When iterating rapidly, use a single-line compile:

```bash
xelatex -interaction=nonstopmode resume.tex && xelatex -interaction=nonstopmode resume.tex
```

Check page count from the "Output written on resume.pdf (N page(s))" line in output.

## Word Count Adjustments

Users may request precise word count changes per bullet with numeric instructions like `+2 +2 +2` or `-1 0 0` — meaning "add 2 words to each of bullets 1/2/3" or "remove 1 word from bullet 1 only". Apply exactly as specified. Typical expansions: full name for abbreviations (SOR → smart order routing), qualifiers (strict, direct, tested), or scope details. Typical removals: filler words, collapsed phrases (risk management controls → risk controls).

## Section Ordering

Within each section, order entries **most recent first** (time descending). Move `\input{}` lines in `resume.tex` accordingly.

## Date Conventions

- **Education section**: university only — omit high school / secondary school entries.
- **"(expected)" labels**: reference date 2026-07-22. Scan ALL entries for stale "(expected)" — any end date in the past must have it stripped. This is a global check, not per-file.
- Remove entries that are not realistic or practical to include (user may say "不现实").

## Entry Lifecycle

| Action | Steps |
|--------|-------|
| **Add** | Create `.tex` in `entries/`, add `\\input{}` at correct time-descending position, recompile |
| **Remove** | Delete `\\input{}` line from `resume.tex`, optionally delete `.tex` file, recompile |
| **Reorder** | Move `\\input{}` lines in `resume.tex`, recompile |
| **Date passes** | Strip "(expected)" suffix from EVERY entry whose end date is past — check the whole resume |
| **Skip** | Don't include entries that are unrealistic or impractical — ask if unsure |

## Content Polishing

- **Trim bullet text** by ~3 words per line when the user requests — remove filler (various, several, very, significant, comprehensive), keep metrics and technical specifics.
- **Merge related bullets** into one when they share a logical thread (e.g. graph construction + multi-head prediction can merge into a single bullet).
- **Consistent terminology**: normalize role/relationship labels across all entries (e.g. all "Supervisor" not a mix of "Advisor" and "Supervisor"). Spell out abbreviations (SOR → smart order routing).
- **Remove "expected" labels** from ALL entries with past end dates — scan globally.
- **Remove unrealistic entries** — if user says a project is "不现实", remove entirely.
- **Word-count micro-adjustments**: user may request precise per-bullet word changes with syntax like `+2 +2 +2` or `+1 +2 +2` or `-1 0 0`. Each number = words to add/remove on that bullet index (1-indexed). Apply exactly — do not round or approximate.

## Contacts Section

Typical contacts line (phone, email, GitHub):

```latex
\ResumeContacts{
  phone,%
  \ResumeUrl{mailto:email@example.com}{email@example.com},%
  \ResumeUrl{https://github.com/username}{github.com/username}%
}
```

Always include the GitHub profile link after the email.

## Entry Content Guidelines

- Each bullet starts with `\item` followed by concrete technical or business contribution.
- Bold the key action: `\textbf{Designed}`, `\textbf{Built}`, `\textbf{Achieved}`.
- Include quantitative metrics (%, ×, $ amounts, speedups, accuracy).
- Reference specific algorithms, frameworks, datasets where applicable.
