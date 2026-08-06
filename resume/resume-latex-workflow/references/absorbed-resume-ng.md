---
name: resume-ng
description: LaTeX resume template for optimal information density and aesthetic appeal (fky2015/resume-ng)
category: resume
---

# Resume-NG: LaTeX Resume Template

A LaTeX resume template designed for optimal information density and aesthetic appeal. Based on [fky2015/resume-ng](https://github.com/fky2015/resume-ng).

## When to Use

Use this skill when the user needs to:
- Create a new LaTeX resume from scratch
- Format an existing resume using the resume-ng template
- Compile a .tex resume to PDF
- Understand resume-ng commands and macros

## Prerequisites

- LaTeX distribution (TeXLive, MiKTeX, etc.)
- `latexmk` command available
- XeLaTeX engine (default)

## Template Files

This skill includes:
- `templates/main.tex` — example resume with all macros demonstrated
- `templates/resume.cls` — the LaTeX document class
- `templates/latexmkrc` — latexmk configuration for xelatex
- `references/readme.md` — original project readme

## Resume-NG Macros Reference

### Header

| Command | Description | Example |
|---------|-------------|---------|
| `\ResumeName{name}` | Set resume title (your name) | `\ResumeName{John Doe}` |
| `\ResumeContact{text}` | Add one contact item | `\ResumeContact{email@example.com}` |
| `\ResumeContacts{itemA, itemB, ...}` | Add multiple contacts | `\ResumeContacts{phone, email, website}` |
| `\ResumeTitle` | Render the title + contacts section | Call after defining contacts |

### Content

| Command | Description | Example |
|---------|-------------|---------|
| `\section{title}` | Section heading | `\section{Education}` |
| `\ResumeItem[bookmark]{title}[subtitle][date][location]` | Experience entry (date right on subtitle line, location right on title line) | `\ResumeItem{Company}[Role][2020-2021][City]` |
| `\GrayText{text}` | Gray-colored text (less important) | `\GrayText{optional info}` |
| `\ResumeUrl{url}{text}` | Underlined hyperlink | `\ResumeUrl{mailto:a@b.com}{Email me}` |

### Structure

```latex
\documentclass{resume}
\ResumeName{Your Name}

\ResumeContacts{
  phone,%
  \ResumeUrl{mailto:email@example.com}{email@example.com},%
  \ResumeUrl{https://github.com/username}{github.com/username}%
}

\begin{document}
\ResumeTitle

\section{Education}
\ResumeItem{University}[Degree][2020-2024][City]
Bullet points with \textbf{bold} for emphasis.

\section{Experience}
\ResumeItem{Company Name}[Role][2021-2023][City]
\begin{itemize}
  \item \textbf{Achievement description} with measurable results.
\end{itemize}

\end{document}
```

## Compilation

```bash
# From the project directory (with latexmkrc):
latexmk

# Or manually:
xelatex main.tex
```

## Design Principles

- **Information density**: tight margins (1cm), compact spacing, no wasted space
- **Aesthetic**: clean serif/sans-serif mix via ctexart, subtle horizontal rules
- **ATS-friendly**: text-based PDF, no graphics, standard section headers
- **Flexible**: optional photo, gray text for low-priority content, footnotes
