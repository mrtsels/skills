# Converting a finance deck to LaTeX (Beamer + XeLaTeX)

User request pattern: "整个ppt做成latex的slides吧" — rebuild an existing
pptxgenjs deck as a Beamer deck (16:9, same content, same headline storyline,
native math, Anthropic fonts). This is the hard-won pitfall bank from a full
27-frame migration; treat it as the debugging map, not a tutorial.

## Environment (macOS, TeX Live BasicTeX)

- Available out of the box: beamer, tikz, fontspec, booktabs, tabularx,
  enumitem, xcolor, colortbl, amsmath. **Missing in BasicTeX: tcolorbox**
  (and its deps environ → trimspaces), pgfplots, microtype.
- Install user-level packages WITHOUT sudo:
  `curl -o X.tds.zip https://mirrors.ctan.org/install/macros/latex/contrib/X.tds.zip`
  then `unzip -o X.tds.zip -d ~/Library/texmf/` (TEXMFHOME; xelatex finds it).
  **Use the `.tds.zip`, not the plain `X.zip`** — plain zips often ship only
  `.dtx`/`.ins` sources; the `.tds.zip` contains the ready `.sty`.
  tcolorbox → needs environ; environ → needs trimspaces. Installing tcolorbox
  alone is not enough.
- `\textls` (letter-spacing) needs microtype — just avoid it in BasicTeX.
- Anthropic fonts: fontspec + `\setmainfont{Anthropic Serif}`
  `\setsansfont{Anthropic Sans}` — works, `pdffonts` confirms embedding.
  `\bfseries` on the variable fonts emits a font warning and falls back to the
  regular weight; LibreOffice synthesizes bold so QA still looks right.

## The classic failure chain (symptoms → causes)

1. **"File ended while scanning use of \frame"** — an unclosed brace group.
   Most common cause found in practice: wrapping a tcolorbox BODY in `{...}`
   (`\begin{card}[opts]{body}\end{card}`) — tcolorbox environments take the
   body WITHOUT braces. Verify with a brace-balance scan; fix by removing the
   wrapper braces.
2. **"Command \rmfamily/\bfseries invalid in math mode" + "Bad math environment
   delimiter"** — an unclosed math mode earlier in the frame. Two real causes:
   - A flattened line break: `\\[10pt]` (line break + space) became `\[10pt]`
     (`\[` = display-math OPEN). Anything after it is "in math mode".
   - A literal `$\sim$\$\sim$`-style mangle: escaped `\$` followed by a stray
     `\sim` reopens math. Scan with a `$`-pairing state machine per line
     (skipping `\$`), or grep for `\$\sim` / odd `$` counts.
3. **"There's no line here to end"** — `\\[Npt]` directly after a tcolorbox
   environment (`\end{card}\\[8pt]`). tcolorbox ends in vertical mode; replace
   with `\end{card}\vspace{8pt}`.
4. **Table rows silently missing from the PDF** (content stops mid-table,
   empty space below, `pdftotext` confirms the rows aren't there = TeX-layer
   loss, not a renderer clip). Cause: tabular column prefix
   `>{\bfseries\sffamily\color{navy}}` — the ungrouped `\color` leaks into
   booktabs `\noalign` and drops rows. Fix: drop `\color{navy}` from the
   prefix (plain `>{\bfseries\sffamily}` is safe); colour headers another way.
5. **Card stacks / long tables clipped at the frame bottom** — Beamer 16:9
   frame is 12.8×7.2cm, content area only ~5.4cm after title + footline.
   A column holding 2 stacked cards + headline overflows and the overflow is
   simply not shown (big empty area below). Fixes, in order:
   a. Restructure: one `columns` block per ROW (2×2 grids = two `columns`
      blocks, not one column of 4 stacked cards).
   b. `\documentclass[aspectratio=169,10pt]{beamer}` (default 11pt) shrinks
      everything ~10%.
   c. Compact cards (`top=4pt, bottom=4pt`), itemize
      `[itemsep=2pt,topsep=0pt,parsep=0pt,...]`, frametitle 20pt, tables
      `\arraystretch` 1.3–1.4.
6. **Glued font commands** — `\footnotesizeINTEREST` is ONE control sequence.
   Any font-size/weight command followed immediately by a letter needs a
   space: `\footnotesize INTEREST`. Regex-fix pattern:
   `\\(footnotesize|scriptsize|small|...)([A-Za-z])` → `\\\1 \2`.
7. **Undefined colours** — `\color{17395C}` (raw hex as a name) errors; use
   `\definecolor{...}{HTML}{17395C}` or a defined colour.

## Escape/unescape foot-gun (the one that cost the most time)

If the generated `.tex` ever comes out double-backslash-escaped
(`\begin` → `\\begin`), the tempting fix `src.replace('\\\\', '\\')` is a
TRAP: it also flattens legitimate LaTeX line breaks `\\[Npt]` → `\[Npt]`,
which then open display-math mode (failure #2). Correct sequence:
1. First restore `\\[Npt]` line breaks:
   `re.sub(r'\\{2,}(?=\[-?\d+(?:\.\d+)?pt\])', r'\\\\', src)` (collapse 2+ → 2)
   then `re.sub(r'(?<!\\)\\\[(-?\d+(?:\.\d+)?)pt\]', r'\\\\[\1pt]', src)`.
2. Then collapse remaining `\\` → `\` and re-check with `grep '\\{3,}'`.
Do NOT use regex replacement strings with backreference groups written inline
(`r'\\[\1pt]'` in a `re.sub` replacement throws "invalid group reference") —
use a `lambda m:` substitution or literal `str.replace` with explicit
two-backslash strings.
When `read_file` output and `python repr()` disagree about backslash counts,
trust `od -c` on the exact line — one of them is escaping for display.

## Verification loops

- After any bulk fix: `xelatex -file-line-error -interaction=nonstopmode
  deck.tex`; grep `\.tex:[0-9]+: LaTeX Error` for real line numbers.
- `pdftotext -f N -l N deck.pdf - | grep <expected row text>` distinguishes
  "TeX dropped the content" (missing) from "renderer clipped it" (present).
- QA same as pptx: `pdftoppm -jpeg -r 100` → vision_analyze the dense frames
  (tables, stacked cards); the same 600s subagent-timeout caveat applies.
- Compile twice (xrefs/footers), ship the `.tex` + PDF alongside the pptx.

## Template skeleton

Minimal working preamble (all pieces verified in BasicTeX + user texmf):
```latex
\documentclass[aspectratio=169,10pt]{beamer}
\usepackage{fontspec}
\setmainfont{Anthropic Serif}
\setsansfont{Anthropic Sans}
\usepackage{amsmath, amssymb, mathtools}
\usepackage{graphicx}
\usepackage{booktabs, tabularx, array, ragged2e}
\usepackage[shortlabels]{enumitem}
\usepackage{tcolorbox}
% palette: \definecolor{navy}{HTML}{0B2545} ... amber E8A33D, light F7FAFC
% \newtcolorbox{card}[2][]{colback=white, colframe=cardborder, boxrule=0.6pt,
%   arc=1.8mm, left=9pt, right=9pt, top=4pt, bottom=4pt, coltitle=navy,
%   fonttitle=\bfseries\sffamily, title={#2}, #1}
% \newtcolorbox{cardplain}[1][]{...} for label-less boxes
% frametitle: family=\rmfamily, size=\fontsize{20}{24}, series=\bfseries
% itemize items: \textcolor{amber}{\textbullet}
% navigation symbols off; footline: deck name left, \insertframenumber right
```
Charts: matplotlib `savefig(format="pdf")` into a `charts_pdf/` dir,
`\includegraphics[width=\textwidth]{charts_pdf/name.pdf}` — vector, crisp.
