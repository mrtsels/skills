---
name: resume-latex-cn-workflow
description: Edit LaTeX resumes (EN + CN), compile × 2, tune
  bullets, commit.
version: 0.1.0
author: Hermes
platforms: [macos]
metadata:
  hermes:
    tags: [Resume, LaTeX, Chinese, XeLaTeX, Git]
---

# Resume LaTeX Workflow (English & Chinese)

Edit modular `.tex` resume files under `entries/`. After every change: clean compile (delete old PDF first) → compile × 2 → show PDF → `git add` + `git commit` + `git push` immediately.

Covers both English (`resume-alex-en/`) and Chinese (`resume-example-zh/`) resume formats.

## When to Use

- User adds/removes/edits a resume entry (internship, research, project).
- User provides a project path and wants bullet points extracted.
- User says "+N +M +K" / "-N -M" to tune bullet length.
- User wants to reorder sections by date descending.
- User provides a supervisor name, URL, location, or date change.
- User wants a Chinese-language resume variant.
- User asks to restructure the Skills section.

## Prerequisites

- XeLaTeX (`which xelatex`)
- `resume.cls` in the resume directory.
- Modular entries under `entries/` as `\input{entries/<prefix>-<name>.tex}`.
- AGENTS.md in repo root requires immediate commit+push.

## Entry Format

```latex
\ResumeItem{\textbf{Title}}
[Role | Supervisor: Prof. Name]
[MM/2026\textendash MM/2026]
[City]

\begin{itemize}
  \item Strong verb, quantified results, no articles a/an/the.
\end{itemize}
```

**Bullet verb rule**: DO NOT wrap verbs in `\textbf{}`. Only labels like `\textbf{Coursework:}` or `\textbf{课程：}` get bold.

**URLs in titles**: `\ResumeItem{\textbf{\ResumeUrl{url}{Title}}}` or `\ResumeItem{\ResumeUrl{url}{Company Name}}`.

## Procedure

### 0. Clean Compile (always, not optional)

```bash
cd /path/to/resume-dir
rm -f resume.pdf    # force recompile — user can tell if stale
xelatex -interaction=nonstopmode resume.tex
xelatex -interaction=nonstopmode resume.tex
```
Show result with `MEDIA:resume.pdf`. Never skip this step.

### 1. Scan Project → Create Entry

Read README.md + key source files (`search_files`, `read_file`), then write `entries/<prefix>-<name>.tex` with 3 bullets. Add `\input{}` to `resume.tex` sorted by date descending.

### 2. Tune Bullets

User says `+N`, `-N` (or `#B +N`, `#B -N`): add/remove N characters from the specified bullet. Count with `python3 -c 'print(len("..."))'` stripping the `\item` prefix and LaTeX tags first.

User says `+N +M +K`: add N chars to bullet 1, M to bullet 2, K to bullet 3.

When two adjacent bullets are ~1.5 lines each, pair them: subtract from one and add to the other so both become either 1 line or 2 lines. See `references/chinese-bullet-editing.md` for detailed cut/add patterns and real examples.

### 3. Skills Section

4-row classification with `\makebox[7em][l]` (EN) or `\makebox[5em][l]` (ZH):

```
EN: Languages, Programming, AI/ML, Infrastructure
ZH: 语言, 编程, AI/ML, 基础架构
```

No parenthetical details inside items.

## Chinese Resume Special Setup

Modify the local `resume.cls` copy:
- Base font: `\LoadClass[11pt,...]{ctexart}` (was 10pt)
- Linespread: set in `resume.cls` (e.g. `\linespread{1.3}`), NOT in `main.tex`
- Name: `\fontsize{20}{25}` (was 18/22)
- Section: `\fontsize{12}{15}` (was 11/13)
- Section titles: 教育经历, 实习经历, 项目经历, 技能
- Coursework label: `\textbf{课程：}`
- Compact punctuation: `\xeCJKsetup{PunctStyle=kaiming}`

## Bilingual Resume Structure (EN + ZH shared entries)

The preferred architecture is **two separate cls files**, not a merged bilingual cls:

```
resume-alex/
├── resume-en.cls          ← Exact copy of original EN cls + \resumeenif
├── resume-zh.cls          ← Exact copy of original ZH cls + \resumeenif
├── resume-en.tex           ← Uses \documentclass{resume-en}
├── resume-zh.tex           ← Uses \documentclass{resume-zh}
└── entries/
    ├── internships-yuecai.tex  ← \resumeenif{EN content}{ZH content}
    └── ...
```

**Why separate cls:** Each language has different `\ResumeItem` (EN 5-param two-line, ZH 6-param one-line), different font sizes (10pt vs 11pt), different name/section formatting. A merged cls compromises both.

### The `\resumeenif` mechanism

Define at end of each cls:

```latex
% resume-en.cls (picks first arg = EN):
\ExplSyntaxOn
\cs_set_eq:NN \resumeenif \use_i:nn
\ExplSyntaxOff

% resume-zh.cls (picks second arg = ZH):
\ExplSyntaxOn
\cs_set_eq:NN \resumeenif \use_ii:nn
\ExplSyntaxOff
```

Entry files:

```latex
\resumeenif{
  \ResumeItem{Company}[Role][07/2026--08/2026][City]
  \begin{itemize}
    \item English bullet.
  \end{itemize}
}{
  \ResumeItem{公司}[角色][2026/07--2026/08][城市]
  \begin{itemize}
    \item 中文要点。
  \end{itemize}
}
```

### Chinese Bullet Compression (~1 line per bullet)

Chinese bullets should fit **one line** (~50-55 mixed chars at 11pt / 1.5cm margins). Iterative `+N -M` per user direction.

**Common cuts:**
- Remove filler: 「连接」「进行」「实现」「构建」when redundant
- Remove bridges: 「用于」「通过」「以」「来」
- Shorten: 「投资委员会」→「投委会」, 「面向离线环境的」→ omit
- Drop parenthetical lists: (GC001、GC002…) → omit
- Merge: 「管理…并覆盖」→「管理覆盖」

**Chinese currency:** ¥800M → 8亿元, ¥5B+ → 50亿元 (always 亿元, no trailing +).

**No em-dashes**: Never use `—` (EN) or `——` (ZH) in bullets. Replace with `:` (EN) or `，` (ZH). Check both EN and ZH branches after any edit that touches punctuation.

**Word order**: Place numeric qualifiers after the noun in Chinese (`60%缺失` → `缺失60%`), before the noun in English (`60% missing`).

**Paired balancing**: When two adjacent bullets in the same section have different line counts, perform paired adjustments — give the short bullet more detail and trim the long one. This keeps visual rhythm without requiring exact equal lengths.

**Sequence:** Write full → user says `+N -M` → user says `#1 +Word` → user says `#3 +N` → accept detail loss.

### CRITICAL: `main.tex` overrides `resume.cls`

If you edit `resume.cls` but the change doesn't appear in the PDF, `main.tex` is the culprit. It likely has settings that override the cls. This happened TWICE in one session (for both `\linespread` and `\ctexset`).

**Always grep both files before debugging:**

```bash
grep -n "linespread\\|ctexset\\|setlist" resume.cls main.tex
```

If a setting exists in BOTH files, `main.tex` wins because it's loaded after the cls. The fix: comment out the setting in `main.tex` and keep it only in `resume.cls`.

### Chinese Entry Format (single-line)

Chinese resume entries use a different layout from English — everything on one line:

**【role】company** | additional — *location · date*

The `\ResumeItem` command needs 6 parameters (not 5):

```latex
\NewDocumentCommand{\ResumeItem}{O{#2} m O{} O{} O{} O{}}
{
  \stepcounter{resumebookmark}
  \vspace{0.15em}
  \noindent
  \textbf{%
    \tl_if_blank:nF {#3} { 【#3】 }%
    #2
  }%
  \tl_if_blank:nF {#6} { | #6 }%
  \tl_if_empty:nTF {#5} {
    \tl_if_empty:nF {#4} { \hfill {\textit{#4}} }%
  }{
    \hfill {\textit{#5}}%
    \tl_if_empty:nF {#4} { ~·~ {\textit{#4}} }%
  }%
  \par
}
```

**Key LaTeX3 conditional rules:**
- Use `\tl_if_blank:nF` for optional args (`#3`). `\tl_if_empty:nF` treats `[]` as non-empty because `{}` is a group. `\tl_if_blank:nF` correctly handles empty optionals.
- Use `\tl_if_empty:nTF` (two-branch) when you need true/false logic. `\tl_if_empty:nF` takes ONE code argument — adding a second `{}` causes it to be output as literal text, producing duplicate date lines in the PDF.
- The pipe separator in `#6` needs a forced space: `\ | #6` not `| #6`, otherwise it runs into the bold text.

Entry examples:
| Type | Code |
|------|------|
| Education | `\ResumeItem{【本科】某大学}[] [YYYY/MM\textendash YYYY/MM] [City] [专业 \| GPA]` |
| Internship | `\ResumeItem{Company}[Role] [YYYY/MM\textendash YYYY/MM] [City]` |
| Research | `\ResumeItem{Project}[Role] [YYYY/MM\textendash YYYY/MM] [City] [导师：某某教授]` |

### CJK Font Setup (Songti SC on macOS)

Do NOT use `\setCJKmainfont{Songti SC}[BoldFont=...]` — fontspec strips spaces from font names ("Songti SC" → "SongtiSC"), causing font-not-found errors. Instead, let `ctexart` auto-detect the system font, and use the TTC file path + `FontIndex` for specific weights:

```latex
% ctexart auto-detects Songti SC by default. No \setCJKmainfont needed.
% Black weight for all-caps name and section titles:
\newCJKfontfamily\SongtiBlack{/System/Library/Fonts/Supplemental/Songti.ttc}[FontIndex=0]
```

Apply `\SongtiBlack` in the name render command and section format:
**Critical**: `\normalfont` resets `\SongtiBlack` to the default font family, losing the Black weight. Always omit `\normalfont` when using `\SongtiBlack`.

```latex
% CORRECT — no \normalfont (keeps Black weight):
{ \centering \SongtiBlack \fontsize{20}{25}\selectfont \bfseries \MakeUppercase{\name} \par }
% Section format:
format = \noindent \SongtiBlack \fontsize{12}{15}\selectfont \bfseries \MakeUppercase{#1},
```

#### Justification

If text looks ragged, add to `resume.cls`:
```latex
\RequirePackage{microtype}
\RequirePackage{ragged2e}
```
And add `\justifying` right after `\begin{document}` in the main `.tex`.

### 5. Verify and Deliver

```bash
cd resume-dir && rm -f resume.pdf && xelatex -interaction=nonstopmode resume.tex && xelatex -interaction=nonstopmode resume.tex
```
Check `grep "Output written"` shows `1 page`. Then show with `MEDIA:resume.pdf`.

Then `git add -A && git commit && git push`. Check `git status` before declaring done.

## Pitfalls

- **Stale PDF**: Always `rm -f resume.pdf` before first compile.
- **Forgotten git**: Check `git status` before declaring done. The most common mistake.
- **Bold on bullet verbs**: `\item \textbf{Designed}` is WRONG. Use `\item Designed`.
- Stale read_file cache: Re-read explicitly after external edits don't seem to apply.
- Skills overflowing: AI label is shortest, check it doesn't orphan content. \makebox[5em] for Chinese.
- fontspec strips spaces: Font names with spaces become SongtiSC internally. Use TTC file path + FontIndex to specify weights.
- Company legal names: To find full Chinese names, check website title tag and copyright footer via curl. See references/company-legal-names.md for verified names.
- PDF not refreshed: Always rm -f resume.pdf before first compile, then compile x 2. Show with MEDIA:.
- **PDF not refreshed**: Always `rm -f resume.pdf` before first compile, then compile × 2. Show with `MEDIA:`.
- **`%` escaping after sed**: After any bulk sed edit, verify all `%` signs are `\\%`. Sed can strip the backslash from `\\%` in content, causing silent PDF truncation. Run `grep -n '%' entries/*.tex | grep -v '\\\\\\\\%'` to catch stray ones. Check both EN and ZH branches.
