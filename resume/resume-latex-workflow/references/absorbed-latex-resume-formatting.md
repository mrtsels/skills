---
name: latex-resume-formatting
description: Formatting reference for LaTeX resume-ng template — Times New Roman, XeLaTeX, fontspec, 5-param entries, bullet spacing
category: resume
---

# LaTeX Resume-NG Formatting

Formatting conventions for the resume-ng LaTeX template (based on fky2015/resume-ng).

## Layout Details

```
Title Line:        **TITLE** (bold left)                   *Location* (italic right)
Subtitle Line:     *Subtitle* (italic left)                 Date (roman right, if location present)
                   (no subtitle)                            Date (roman right, if location absent)
Bullet Line:         • text...
```

## `\ResumeItem` Macro (5 params)

```
\ResumeItem[bookmark]{title}[subtitle][date][location]
```

| Param | Line | Position | Style |
|-------|------|----------|-------|
| #2 title | 1 | left | **bold** |
| #5 location | 1 | right | *italic* |
| #3 subtitle | 2 | left | *italic* |
| #4 date | 2 (or 1 if no #5) | right | roman |

## Visual Specs

| Element | Value |
|---------|-------|
| Name | 18pt, `\bfseries`, `\MakeUppercase`, centered |
| Section headers | 11pt, `\bfseries`, `\MakeUppercase`, hrule below, beforeskip=0.5em |
| Body | 10pt (class option), `\linespread{1.0}` |
| Font | Times New Roman via `TimesNewRomanPSMT` (PostScript name for fontspec compat with ctexart) |
| Margins | A4, 1cm all sides, 0.5cm bottom (override in preamble for tighter fit) |
| Entry spacing | 0.15em `\vspace` before each `\ResumeItem`, 0 after subtitle |
| Bullet lists | `leftmargin=1.8em`, `labelsep=0.5em` |
| List spacing | all zero: `itemsep=0em, parsep=0em, topsep=0em, \parskip=0pt` |
| URL hyperlinks | `\ResumeUrl{url}{text}` renders as `\href{url}{text}` — no underline, no CJKunderline decoration. Blue clickable text only. |

## Date Placement Logic

- **Location present** (#5 non-empty) → date on **subtitle line** (right)
- **Location absent** (#5 empty) → date on **title line** (right)

## Preamble Customizations (dense one-page variant)

```latex
\geometry{margin=0.75cm, bottom=0.3cm}
\linespread{0.95}
\setlist{parsep=0em, topsep=0em, itemsep=0em, partopsep=0em, leftmargin=1.0em}
\setlength{\parskip}{0pt}
\ctexset{section={beforeskip=0.3em, afterskip=0.3em}}
```

## Pitfalls

- **Location must use `[City]` not `{City}`** — `O{}` args only parse `[...]`.
- **En dash spacing** — Unicode `–` loses trailing space in XeLaTeX inside optional args. Use `\ \textendash\ ` to preserve: `[09/2020\ \textendash\ 06/2024]`.
- **`\text{}` in math** requires `\usepackage{amsmath}` — included in cls.
- **Font name** uses PostScript `TimesNewRomanPSMT` because `ctexart` strips spaces from font names passed to fontspec.
- **XeLaTeX only** — pdfLaTeX cannot load macOS system fonts via fontspec.
- **expl3 conditional gotcha**: `\tl_if_empty:nT` = if empty (true branch); `\tl_if_empty:nF` = if NOT empty (false branch). Easy to swap when implementing conditional date placement — always double-check per the logic diagram above.
- **Blank lines before `\begin{itemize}`** trigger `\partopsep` (default non-zero). Set `partopsep=0em` in preamble to suppress, or remove blank lines between `\ResumeItem` and `\begin{itemize}`.
- **Bullet character**: `\textbullet` may render small/hollow in Times New Roman. Use `$\bullet$` for a larger, blacker math symbol bullet.

## Bullet Text Line-Fitting Technique

To optimize bullet text so lines are well-filled (no short last lines with 1-3 words):

1. Build PDF, then extract precise line positions with PyMuPDF:
   ```python
   import fitz
   doc = fitz.open('main.pdf')
   page = doc[0]
   blocks = page.get_text('dict')['blocks']
   for b in blocks:
       if 'lines' in b:
           for l in b['lines']:
               text = ''.join([s['text'] for s in l['spans']])
               x0, y0, x1, y1 = l['bbox']
               print(f'Y={y0:.0f} X=({x0:.0f}-{x1:.0f}) {text[:80]}')
   ```
2. Full-width line ≈ 553pt (page width − margins). Continuation (wrapped) line starts at leftmargin indent, max ≈ 543pt.
3. For each bullet, identify the last line. If last line length < 70% of full width, adjust text:
   - Trim words (remove redundant adverbs, merge clauses) to pull content to previous line
   - Add detail (qualify with a specific metric, tool name, or outcome) to fill the line
4. Rebuild and re-check.

Effective baseline at `\linespread{0.95}` = 12pt × 0.95 = 11.4pt line-to-line. All list spacings zero means bullet-to-bullet distance = bullet-line-to-next-line distance.

## Requirements &amp; Pitfalls

### LaTeX Packages
`ctex`, `fontspec`, `enumitem`, `geometry`, `hyperref`, `xcolor`, `amsmath`, `xeCJKfntef`, `footmisc`, `latexmk`

Install on macOS: `sudo tlmgr install ctex enumitem footmisc xcolor xeCJKfntef && sudo tlmgr install latexmk`

### Common Mistakes
- **Location must use `[City]` not `{City}`** — `O{}` args parse only `[...]`. `{City}` becomes stray un-italicized text below the subtitle.
- **En dash spacing** — Unicode `–` loses trailing space in XeLaTeX optional args. Use `\ \textendash\ ` to preserve both spaces.
- **`\text{}` in math** requires `amsmath` — added in cls.
- **Font name** uses PostScript `TimesNewRomanPSMT` because `ctexart` strips spaces in font names.
- **XeLaTeX only** — pdfLaTeX cannot load system fonts via fontspec.
- **`\ResumeUrl` no longer underlines** — `\CJKunderline` was removed from the cls. URLs render as plain `\href{url}{text}` — blue clickable text only, no decoration.
