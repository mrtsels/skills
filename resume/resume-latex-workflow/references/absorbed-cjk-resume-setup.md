---
name: cjk-resume-setup
description: Set up Chinese LaTeX resumes with Songti SC
  font.
version: 0.1.0
author: Hermes
platforms: [macos]
metadata:
  hermes:
    tags: [LaTeX, XeLaTeX, CJK, Resume, Chinese]
---

# Chinese Resume Setup (resume.cls + Songti SC)

Set up and maintain Chinese-language resumes using the `resume.cls` class (ctexart-based, XeLaTeX). Covers modular `entries/` structure, CJK font configuration for Songti SC, and the Black-weight pitfall where `\normalfont` silently resets the font weight.

## When to Use

- User asks to create a Chinese resume from scratch.
- User provides a Chinese docx/PDF and wants it converted to LaTeX.
- Chinese characters render as boxes (tofu) in the PDF.
- User wants Songti SC Black for all-caps parts (name, section titles).
- User asks to create/fix `resume-example-zh/`.

## Prerequisites

- macOS with Songti SC font (built-in).
- XeLaTeX: `which xelatex`.
- `resume.cls` in the resume directory — copy from `resume-alex-en/resume.cls` as starting point.

## How to Run

```bash
xelatex -interaction=nonstopmode main.tex   # first pass
xelatex -interaction=nonstopmode main.tex   # second pass for cross-refs
```

## CJK Font Configuration

### Basic setup (no errors, no tofu)

Do NOT call `\setCJKmainfont` with font names containing spaces — fontspec strips them (`Songti SC` → `SongtiSC`, not found). Let `ctexart` auto-detect:

```latex
% In resume.cls: NO explicit \setCJKmainfont needed.
% ctexart auto-detects macOS Songti SC.
% Only needed for CJK glyphs in the resume (Chinese entries).
```

### Adding Black weight for all-caps parts

Use the TTC file path with `FontIndex`:

```latex
\newCJKfontfamily\SongtiBlack[
    Path = /System/Library/Fonts/Supplemental/,
    FontIndex = 0,
]{Songti.ttc}
```

Check the Black font index on the target system:
```bash
fc-list | grep "Songti SC" | grep Black
```

Index 0 is typically Black on macOS, but verify.

### CRITICAL: `\normalfont` resets Black to Regular

```latex
% WRONG — \normalfont resets \SongtiBlack, then \bfseries gives only Bold:
\SongtiBlack \fontsize{12}{15}\selectfont \normalfont \bfseries

% RIGHT — remove \normalfont to keep Black weight:
\SongtiBlack \fontsize{12}{15}\selectfont \bfseries
```

The `\normalfont` command resets the entire font to the document's default family and weight. When placed after `\SongtiBlack`, the Black selection is lost. Always omit `\normalfont` when using a custom font-family command for weight selection.

## Procedure

### 1. Create directory structure

```bash
mkdir -p resume-example-zh/entries
cp resume-alex-en/resume.cls resume-example-zh/
```

### 2. Create modular entry files

Each section as a separate file in `entries/`:

- `entries/education-university.tex` — education entry
- `entries/internships-company-a.tex` — internship entry
- `entries/research-cv-project.tex` — research/project entry
- `entries/skills.tex` — skills section

### 3. Write main.tex

Follow the English version's structure but use Chinese section names:

```latex
\section{教育经历}
\input{entries/education-university}

\section{实习经历}
\input{entries/internships-company-a}

\section{项目经历}
\input{entries/research-cv-project}

\input{entries/skills}
```

### 4. Configure skills alignment

Use `\makebox` for Chinese labels (shorter width than English):

```latex
\item \makebox[5em][l]{\textbf{语言：}} 内容
\item \makebox[5em][l]{\textbf{编程：}} 内容
```

### 5. Add Black weight to cls

Add the `\newCJKfontfamily` definition and apply to:

- **Section title format** (`\ctexset{section = {format = ...}}`)
- **Name rendering** (`\__resume_render_title:`)

Both must NOT have `\normalfont` after `\SongtiBlack`.

### 6. Compile and verify

```bash
xelatex -interaction=nonstopmode main.tex
xelatex -interaction=nonstopmode main.tex
```

## Quick Reference

| Task | Command/Code |
|------|-------------|
| Compile | `xelatex -interaction=nonstopmode main.tex` × 2 |
| Black font def | `\newCJKfontfamily\SongtiBlack[Path=...,FontIndex=0]{Songti.ttc}` |
| Apply Black | `\SongtiBlack \fontsize{20}{25}\selectfont \bfseries ...` |
| Check Black index | `fc-list \| grep "Songti SC" \| grep Black` |
| Section order | 教育经历 → 实习经历 → 项目经历 → 技能 |

## Pitfalls

- **fontspec strips spaces**: `Songti SC` becomes `SongtiSC` internally, which doesn't exist. Use TTC file path + `FontIndex` instead.
- **`\normalfont` kills `\SongtiBlack`**: Never use `\normalfont` after a custom font-family command. It resets the entire font, not just the shape.
- **Black vs. Bold at small sizes**: Songti SC Black at 11-12pt looks very similar to Bold. Test at 20pt+ to verify the weight switch works.
- **`FontIndex` needs file path**: Writing `\newCJKfontfamily{Songti SC}[FontIndex=0]` does NOT work — `FontIndex` is only meaningful with `Path + filename.ttc`.
- **No `\setCJKmainfont` with spaces**: It produces `SongtiSC not found` errors. Let `ctexart` auto-detect.
- **Chinese text as boxes**: Run `xelatex` with `-interaction=nonstopmode` and check `.log` for `fontspec Error: The font "..." cannot be found`.

## Verification

```bash
cd resume-example-zh && grep -c "error" main.log
# Should return 0
```
Then check PDF has readable Chinese characters (not boxes).
