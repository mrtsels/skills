---
name: cuhk-poster-latex
description: Use for CUHK LaTeX posters and TeX Live basic dep fixes.
version: 1.0.0
---

# CUHK LaTeX Poster (zyzheng17 template)

Build and iterate on CUHK internship/research posters using the gemini-based
`CUHK-Poster-Template` (github.com/zyzheng17/CUHK-Poster-Template). Covers
local compilation on TeX Live basic (missing packages/fonts), the block
structure, and this user's header/footer format preferences.

## When to Use

- User asks to prepare/set up the CUHK poster template or write a poster.
- Compiling `poster.tex` fails on missing `.sty` or fonts (Raleway/Lato).
- User asks to fill poster blocks from report content.

## Setup (one-time)

1. Clone template: `git clone https://github.com/zyzheng17/CUHK-Poster-Template.git`
2. Copy working files into project `poster/`: `poster.tex`, `beamerthemegemini.sty`,
   `beamercolorthemecuhk.sty`, `poster.bib`, `Makefile`, `logos/` (CUHK-Logo.pdf/png).
3. **User preference: keep the pristine template inside the project `tmp/`**
   (`tmp/CUHK-Poster-Template/`, gitignored) as reference — do NOT delete the
   template's lorem ipsum body; future sessions use it as a copy-paste reference
   for block/alertblock/exampleblock/table/TikZ syntax.
4. Compile: `make` (latexmk + lualatex) or
   `lualatex -interaction=nonstopmode poster.tex` ×2 (2nd pass resolves refs),
   `bibtex poster` between passes if `\nocite{*}` references are used.
5. Verify visually: `pdftoppm -png -r 60 poster.pdf /tmp/pv` + vision check
   (header, both columns, footer; look for overflow/overlap/tofu).

## TeX Live basic: missing packages & fonts

This machine's TeX Live (2026basic) lacks several packages the template needs.
System `tlmgr install` fails (no admin) — install into the **user texmf tree**
`~/Library/texmf/tex/latex/<pkg>/<pkg>.sty` instead. Exact working commands,
CTAN URLs, and the docstrip/filecontents extraction workarounds live in
`references/texlive-basic-deps.md`. Required: beamerposter, type1cm,
changepage, anyfontsize.

Fonts: gemini theme requires **Raleway** (headline/block titles) and **Lato**
(body). Without them lualatex errors `fontspec: The font "Raleway" cannot be found`.
- `brew install --cask font-raleway` downloads but does NOT place TTFs in
  `~/Library/Fonts` — copy static TTFs from the caskroom cache dir:
  `/opt/homebrew/var/homebrew/tmp/.caskroom/font-raleway/<ver>/.../static/TTF/*.ttf`
- `brew install --cask font-lato` FAILS (latofonts.com 403). Download static
  TTFs from google/fonts GitHub raw: `github.com/google/fonts/raw/main/ofl/lato/Lato-{Light,LightItalic,Regular,Italic}.ttf`
  into `~/Library/Fonts/`.

## Poster structure & user format preferences (as of 2026-08)

Header (`\title` / `\author` / `\institute`):
- Title split across two lines with `\\` (user-specified break point, e.g.
  after "...Neural Networks" / "for GUI Structure Error Correction").
- `\author` = side-by-side tabular:
  `\author{\begin{tabular}{@{}l@{\hspace{3cm}}l@{}}Author: Alex Licheng Xie & Supervisor: Prof.\ Wing Cheong Lau\end{tabular}}`
- `\institute` = `Information Engineering, The Chinese University of Hong Kong`
  (full name; user rejected the CUHK abbreviation; no `\inst{1}` — it renders
  "1Department" with no space).
- Footer = email | `Summer Research Internship` | GitHub repo link
  (user swapped the supervisor name for the repo link).

Body: **7 numbered blocks, FINAL layout is THREE columns** (user: "两栏改三栏",
then "proposed methodologies放第一栏" 2026-08): left = 1 Introduction,
2 Existing Benchmarks, 3 Research Objectives, 4 Proposed Methodologies
(moved to the first column — user wants the methodology content up front);
middle = 5 Models; right = 6 Results, 7 Conclusion + References. As of the
final 2026-08 state, block 4's "Two alternating hops" + "Element features"
paragraphs were moved OUT of the left column to the TOP of the middle column
as bare content (before the standalone VLM-error figure) — do not re-add them
to block 4. Column widths `\colwidth=0.32\paperwidth`,
`\sepwidth=0.01\paperwidth` (3×0.32 + 4×0.01 = 1.0). Fill by copying from the
report — the plain-text `report/report.md` is the best source (numbers already
verified against experiment JSONs). Reuse `report/references.bib` as
`poster/poster.bib` (References block uses `\nocite{*}`).

**All block titles left-aligned (final, user: "不止是References 是所有")**:
edit `beamerthemegemini.sty` once — change
`colsep*=0ex,dp=2ex,center]{block` → `colsep*=0ex,dp=2ex,left]{block` in ALL
THREE places (block title / block alerted title / block example title, ~lines
164/188/215). Do NOT add per-block `\begingroup\setbeamertemplate{block begin}`
overrides — the user rejected the References-only special case
("references不要单独调整了"). References stays a plain block at the bottom of
the right column; the earlier experiment of pinning it full-width at page
bottom (`\vfill` + bare `{\usebeamerfont{block title}...References\par}`) was
REVERTED ("References改回正常的block位置吧，遵循三栏，该有的分割线和居中都恢复").

**Block-title underline rule is ORANGE and slightly thicker (user, 2026-08:
"1 2 3节标题下面的横线用cuhk-orange颜色，稍微粗一点点")**: the rule under
each block title is `\begin{beamercolorbox}[colsep=0.025ex]{block
separator}`. Change the color once in `beamercolorthemecuhk.sty`:
`\setbeamercolor{block separator}{bg=black}` →
`\setbeamercolor{block separator}{bg=cuhk-orange}`, and thicken in
`beamerthemegemini.sty`: `colsep=0.025ex` → `colsep=0.06ex` (≈2.4×).
This is GLOBAL (all blocks share the template) — the user asked for
sections 1/2/3 but the uniform look across all blocks is what they want
(consistent with the earlier "all titles" global preference).

## Real dataset sample images for the Benchmarks block (2026-08)

User asked for a ScreenSpot sample image ("ScreenSpot的图给我搞一张") — the
Existing Benchmarks block (pure text itemize: RICO / ScreenSpot / End-to-end)
is the natural home for a dataset sample screenshot. ScreenSpot original
images are NOT in the repo (only code + data/vlm_predictions/screenspot_qwen_flash/*.json).
Source them from the HuggingFace mirror `benwiesel/ScreenSpot`:
https://huggingface.co/datasets/benwiesel/ScreenSpot/resolve/main/images/mobile_*.png
(~600 images, 2360x1640). PICK THE IMAGE WHOSE image_id MATCHES A LOCAL
prediction JSON (e.g. mobile_043c3a5e-c12c-4991-bb7f-676c617b2f9b.png <-> 
data/vlm_predictions/screenspot_qwen_flash/mobile_043c3a5e...json) so the
screenshot is a REAL sample this project actually evaluated — and the same
file can later carry Qwen overlay boxes. Convert to jpg for size
(9.3MB png -> ~337KB jpg, quality=90) into poster/figures/.

Insert inside the itemize:
```
\item \textbf{ScreenSpot:} GUI grounding benchmark spanning mobile,
  PC, and web layouts, used to test cross-domain transfer.
  \begin{center}
  \includegraphics[width=0.30\linewidth]{figures/screenspot_sample.jpg}
  \end{center}
```
Width matters: 0.55\linewidth of a 2360x1640 portrait image overflowed the
left column (Overfull vbox 71pt) — use ~0.30 in the narrow 3-col layout.
\includegraphics scales pixels only; text inside a PNG is rasterized so the
"no resizebox" rule does not apply to real screenshots.

**FINAL: RICO and ScreenSpot shown as a PAIRED figure with rounded corners,
thick black border, and dataset captions** (user: "把安卓截图也放过来，然后这两张图
各自用适当圆角包裹，并设置3pt黑色边框，同时在图片下方标注数据集名称", 2026-08;
evolved the same session). RICO sample comes from `demo_data/screenshots/10027.jpg`
(Android news/weather app) — NOT 10067, which the VLM-error figure is based on
(user: "RICO的例子不要用现在这个，换一张"). Copy to `poster/figures/rico_sample.jpg`.
Both images sit in ONE TikZ with the clip+frame pattern (rounded clip for the
corners, then a thick `draw` on the same rect for the border), captions below each:
```
\begin{center}
\begin{tikzpicture}[
    frame/.style={draw=black, line width=8pt, rounded corners=20pt},
    labcap/.style={font=\bfseries}]
  \begin{scope}
    \clip[rounded corners=20pt] (0,0) rectangle (6.0,10.66);
    \node[anchor=south west, inner sep=0] at (0,0)
      {\includegraphics[width=6.0cm]{figures/rico_sample.jpg}};
    \draw[frame] (0,0) rectangle (6.0,10.66);
  \end{scope}
  \node[labcap] at (3.0,-1.3) {RICO};
  \begin{scope}[xshift=7.0cm]
    \clip[rounded corners=20pt] (0,0) rectangle (14.4,10.02);
    \node[anchor=south west, inner sep=0] at (0,0)
      {\includegraphics[width=14.4cm]{figures/screenspot_sample.jpg}};
    \draw[frame] (0,0) rectangle (14.4,10.02);
  \end{scope}
  \node[labcap] at (7.0+7.2,-1.3) {ScreenSpot};
\end{tikzpicture}
\end{center}
```
Rules that cost iterations (all user-enforced 2026-08):
- **NEVER force both width AND height on `\includegraphics`** (user: "iPad的截图别改
  比例，原始比例是多少就用多少"): `[width=3.2cm, height=4.6cm]` silently stretches
  the 2360×1640 landscape iPad shot into portrait. Specify width ONLY
  (`[width=6.0cm]`); height follows the native aspect automatically (RICO
  1080×1920 → 6.0cm × 10.66cm; ScreenSpot 2360×1640 → 14.4cm × 10.02cm). The
  clip rect must match the computed height exactly.
- **Clip radius must equal frame radius** — `\clip[rounded corners=20pt]` and
  `frame/.style={rounded corners=20pt}`; if the clip radius is smaller than the
  border radius the image corners show as white under the thicker border.
- **Final sizes are LARGE** (user: "放大到2x" then ScreenSpot "再+50%"):
  RICO 6.0cm wide, ScreenSpot 14.4cm wide, total ≈21.4cm ≈ the whole left column.
  This produces `Overfull \vbox (149pt too high)` warnings that the user
  ACCEPTED ("现在这样是OK的") — an overflow warning is not automatically a
  failure; if the user says it's fine, stop trimming.
- **Later shrunk 30% to make room for added data-viz figures** (user, 2026-08:
  "RICO和ScreenSpot的截图大小都缩小30%"): width-only again (rule above) —
  RICO 6.0→4.2cm (height 10.66→7.47, clip rect updated), ScreenSpot
  14.4→10.08cm (height 10.02→7.0, clip rect updated), `xshift=7.0cm→5.2cm`,
  caption centers recomputed (`at (2.1,-1.3)` and `at (5.2+5.04,-1.3)`).
  Always recompute the clip rect height from the NEW width × native aspect
  and move the caption to the new midpoint — never leave the old numbers.
- **Captions use BODY text size** (user: "RICO ScreenSpot字样用正常正文文字大小"):
  `labcap/.style={font=\bfseries}` — no `\scriptsize`. With body-size glyphs the
  caption must sit lower: y=-1.3, not -0.45, or it overlaps the frame.
- Style name `labcap` (NOT `cap` — `cap` is a reserved pgfkeys key: "The key
  '/tikz/cap' requires a value"). Placing the figure between two itemize
  halves: close the first `\begin{itemize}`, put the `\begin{center}` figure,
  then re-open `\begin{itemize}` for the remaining items — a bare `\item`
  after the closed list errors `Lonely \item--perhaps a missing list
  environment`.

.gitignore: global `figures/` rule (line ~53) ignores poster/figures/. Add
exceptions next to the other poster rules:
```
!poster/figures/
!poster/figures/*.jpg
```
(also !poster/*.bbl for references — see bibliography section). Verify with
`git check-ignore -v poster/figures/x.jpg` showing the ! rule, then `git add`
the file explicitly (plain `git add poster/figures/` is refused as ignored).

## Porting report figures to the poster (2026-08, user: "做字号适配风格适配的")

Report figures are A4-sized with `\tiny`/`\scriptsize` fonts; poster is A0.
The poster blocks that got figures: block 4 gets the pipeline diagram (full
width), the bipartite graph, and the 10-constraint table; block 5 gets the
training-objective dual-panel chart; block 6 gets the constraint-ablation
bars, completion IoU grouped bars, and end-to-end before/after bars.

**Constraint table (FINAL format, user-driven 2026-08)**: `\begin{tabularx}
{0.8\linewidth}{XX}` — 80% of line width inside `\begin{center}` so it sits
centered with ~10% whitespace on each side, and **NO `\footnotesize`** (user:
"这个图标撑满宽度，文字大小不要刻意缩小，用和正文相同的大小" then "列宽也均匀铺开"
then "整个表格撑满80%宽度，左右各留10%空白"). Equal column widths come from
`XX` (two X columns), not `lX`. Body font size = same as block prose
(normalsize), NOT shrunk. **LATER REPLACED by a dot-point itemize (user,
2026-08: "这个表格改为dot point")** — the 10-type table is now a bulleted
list with **10 SEPARATE items, one per constraint** (user: "10 dot points is
OK" — my first pass merged the four `ALIGN_*` into one item and
`CENTER_X, CENTER_Y` into one; the user rejected the merge and wanted each
constraint on its own line: `\texttt{ALIGN\_LEFT}: $|x_1-x_1'|<\varepsilon$`
... through `\texttt{SAME\_SIZE}: similar widths/heights`). Do NOT restore
the tabularx table version; do NOT re-merge the items.

**Final layout: two UNEQUAL columns** (user: "这一部分分左右两栏" + "挤压中间
间隙，右栏给多10%空间", 2026-08): wrap the itemize in
`\begin{tabularx}{\linewidth}{@{} >{\hsize=0.9\hsize}X >{\hsize=1.1\hsize}X @{}}`
with `\begingroup\setlength{\tabcolsep}{0pt}` around it — `\hsize` weights
give the right column 10% more width (0.9 vs 1.1; the weights must sum to
2.0 for two X columns), `\tabcolsep 0pt` + `@{}` squeeze the inter-column
gap. (multicols{2}
also works but gives EQUAL columns with a fixed `\columnsep` — it cannot do
the "right column +10%" the user asked for; tabularx `\hsize` is the form
to use.) **FINAL STATE after user iteration (2026-08)**: the user walked the
weights 0.9/1.1 → 0.8/1.2 ("右栏要变宽啊 充分利用空间") → back to **50/50**
(`@{} X X @{}`, "改回50/50吧") — do NOT default to unequal widths; equal
columns were the accepted end state. Item split also changed: **CENTER_Y
moved to the LEFT column** ("center y放到左边") so left = ALIGN_LEFT/RIGHT/
TOP/BOTTOM + CENTER_X + CENTER_Y (6 items), right = SPACING / CONTAINMENT /
GRID / SAME_SIZE (4 items).

**Other report tables reuse the same style** (user: "使用这个排版，把report中另外
两个表格也找地方搬上来"): port `tab:ablation` (constraint set vs violation acc,
2 cols → `XX`) after the constraint-ablation bars in block 6, and `tab:real`
(end-to-end, 4 cols → `XXXX`) after the end-to-end bars. Same
`tabularx{0.8\linewidth}` + center + body-size recipe. **Long numeric cells
overflow**: `TP / FP / FN & 1126/1821/3663 ...` blew a 53.6pt Overfull in the
narrow column — split it into separate rows (user: "那你就分三行写嘛"):
`TP & 1126 & 1232 & $+106$`, `FP & 1821 & 1905 & $+84$`, `FN & 3663 & 3557 &
$-106$`. Also, prose that lists long `\texttt` constraint names
("Ten spatial constraint types are extracted (e.g. ALIGN_LEFT, CONTAINMENT...)")
overflows once tables carry that info — trim to the definition sentence only
(same info lives in the table; the report had both, the poster doesn't need the
duplicate).

**KPI cards (user-driven design, 2026-08 — user: "复制一份，用KPI card展示（原模版可能没有 你要自己设计一下）")**: the constraint-ablation table gets a second presentation as 6 KPI cards (3×2 grid), designed from scratch (template has none). Hard requirements the user enforced in sequence:
- **Solid color blocks, NO outlined light-fill cards** (first attempt was `draw` + `fill=cuhk-purple!8` — rejected: "不要这种，要纯色方块底的"). Use `fill=cuhk-purple!85` / `fill=cuhk-orange!80` with `text=white`. **LATER OVERRIDDEN — final design is LIGHT backgrounds** (user: "所有元素底色都用淡色"): `fill=cuhk-purple!12` / `fill=cuhk-orange!15`, card text `text=black` (user: "非大数字用黑色"), large values explicitly `{\Large\bfseries\color{cuhk-purple!90}...}`. Purple blocks = control/improving sets, orange = hurting sets.
- **Text LEFT-aligned with real padding — never centered** (user: "什么叫padding不明白吗 为什么还在用中心对齐"). Style: `align=left, inner sep=10pt`.
- **Equal-size grid, equal padding on all sides**: `node distance=0.6cm` (positioning lib: `right=of a`, `below=of a`) for identical gaps; **equal heights** via `minimum height=3.0cm` PLUS a transparent filler row `{\scriptsize\bfseries\color{white!75}\phantom{-1.9pp}}` on the control card — the card WITHOUT a delta line otherwise renders shorter and breaks the grid.
- **80% column width**: `\pgfmathsetlengthmacro{\cardw}{\dimexpr(0.8\colwidth - 1.2cm)/3\relax}` before `\begin{tikzpicture}`, then `text width=\cardw` (1.2cm = 2 gaps of 0.6cm). Total = 80% of column, centered.
- **Card titles on ONE line — no `\\` breaks**: `\textbf{All 10 types (control)}` and `Remove all \texttt{ALIGNMENT}` must not wrap (user: "(control) & remove all不要单独成行"). Pick `\cardw` big enough for the longest title.
- **No nested `\node` inside a `\node{...}` body** — TikZ errors. Format value/delta lines inline: `{\Large\bfseries 0.889}\\[2pt]{\scriptsize\bfseries\color{white!75}$-$1.9pp}`.
- **Value + delta on ONE line, delta colored green/red** (user: "±xx pp和大数字在同一行 用红色或绿色表示"): `{\Large\bfseries\color{cuhk-purple!90}0.889}\quad{\scriptsize\bfseries\color{red!80!black}$-$1.9pp}` — improving sets `\color{green!60!black}$+$`, hurting sets `\color{red!80!black}$-$`. Control card (All 10 types) has no delta line.
- **Bold policy on cards (user: "0.908 加粗" then "那其他大数字不用粗体 ±也不用粗体")**: ONLY the control card's value (0.908) is `\bfseries`; the other five values are regular weight (`{\Large\color{cuhk-purple!90}0.889}`), and the ± deltas are regular weight too (`{\scriptsize\color{red!80!black}$-$1.9pp}` — color only, no bold). The 0.908 bold in the constraint-ablation horizontal-bar chart label (`{\bfseries 0.908}`) is separate from the cards; do not bold 0.889/0.903/0.916/0.939/0.878 anywhere.
- **Do NOT define `up/.style=` / `dn/.style=` TikZ styles** (2026-08): `\up`/`\dn` collide with TeX control sequences, so `{\up $+$0.8pp}` in a node body errors `Undefined control sequence`. Inline the full formatting instead: `{\scriptsize\bfseries\color{green!60!black}$+$0.8pp}`.

**FINAL WORKING APPROACH — coordinate-only TikZ scaling (user: "检查文字大小
我告诉你的是全是错的" after the resizebox variant):** do NOT use
`\resizebox{...}{!}` and do NOT use `transform shape` — both scale the figure
TEXT along with the coordinates, so ported A4 figures end up 12–27pt vs the
11pt body (giant fonts, user: "图标的字跟个巨无霸一样"). Instead:
- Open each `\begin{tikzpicture}` and set **`[xscale=N, yscale=1]`** (NOT
  `scale=N`, NOT `transform shape`, NOT `\resizebox`) — `transform shape` and
  `resizebox` scale the figure TEXT along with coordinates (giant fonts);
  `scale=N` alone stretches height too, which the user rejected
  ("等比缩放导致上下拉得太宽了 这个维度不要缩放" — final ask: stretch width
  only, keep natural height). With `xscale=N, yscale=1` coordinates stretch
  horizontally while node text keeps its real LaTeX size (`\small`≈9pt,
  `\footnotesize`≈8pt, `\scriptsize`≈7pt), proportional to body normalsize (11pt).
- Choose N so the figure's natural width × N ≈ column width: pipeline
  (snake layout, natural ~9cm) → 2.5; bipartite graph (~7cm) → 3;
  phase9 dual panel (~11cm) → 2; ablation bars (~7.5cm) → 2.8; completion
  (~9.5cm) → 2.2; end-to-end (~7.5cm) → 2.8.
- **Bipartite graph figure (final layout, user-driven 2026-08)**: elements and
  constraints go in TWO HORIZONTAL ROWS, not left/right columns — element nodes
  on top (`e1..e5` at x=0/2.2/4.4/6.6/8.8, y=1.5), constraint nodes centered
  below (`c1..c4` at x=1.1/3.3/5.5/7.7, y=-1.5). Uniform spacing: both rows use
  the same 2.2 step and the constraint row is centered on the element row's
  midpoint (4.4), NOT offset to align with e1. Partition labels center over the
  FULL row: `above=0.25cm of e3` (e3 is the row midpoint) and an explicit
  `\node[font=\small\itshape] at (4.4,-2.7) {Constraint nodes $V_c$};` — do NOT
  anchor to the first node (`of e1` / `of c1`) or offset from a middle node with
  `xshift`, both look off-center.
- **Fixed node widths in bipartite figure**: `minimum width=1.9cm` silently
  widens any node whose text exceeds it (`\texttt{CONTAINMENT}` is wider), so
  the 4 constraint boxes end up different widths → spacing looks inconsistent
  and the row midpoint drifts (user: "c1～c4各自间距完全不一致，Constraint Node也没有在
  正确的对齐居中位置上"). IMPORTANT NUANCE: `minimum width` is only a LOWER
  bound — it does NOT force equal width (user: "节点等宽并没有做到" when width
  was measured at 263–340px across nodes; `CONTAINMENT` at beamerposter A0
  `\footnotesize` renders ≈4.9cm, way past any sane minimum). "等宽 vs 等间距"
  is NOT either/or: the fix must deliver BOTH equal box widths AND equal edge
  gaps. FINAL WORKING FIX (per external-AI advice, verified): use **`text
  width=2.6cm` + `align=center` + `inner sep=0pt`** on elem/cons styles —
  `text width` FORCES the box (not a lower bound) and `inner sep=0pt` makes
  the outer box exactly equal `text width`; then add manual hyphenation points
  `\-` in long constraint words so they wrap to two centered lines inside the
  box instead of overflowing: `\texttt{ALIGN\_\-LEFT}`, `\texttt{CONTAIN\-MENT}`,
  `\texttt{SPAC\-ING}`, `\texttt{SAME\_\-SIZE}`. Measured boxes then render
  145–149px at 150dpi ≈ uniform. Do NOT use `\resizebox{\linewidth}{!}{...}`
  per node — it stretches short words and shrinks long ones (non-uniform fonts).
- **Bipartite node dimensions (user's final numbers, 2026-08)**: after the
  text-width fix the user iterated sizes: element (purple) nodes `text
  width=3.2cm`, constraint (orange) nodes `text width=5.0cm` (widen 60% then
  +20% = ×1.6 ×1.2 from the 2.6cm base), both `minimum height=0.99cm`
  (0.55 ×1.8, user: "黄色和紫色都增高80%"), constraint row step widened
  +30%. Coordinates are pre-scaled ×2.2 (no xscale transform, so text width
  applies strictly): elements at x=1.32/6.16/11/15.84/20.68, constraints at
  x=1.565/7.855/14.145/20.435, row center x=11 (labels: `above of e3` and
  `at (11,-2.7)`).
- **Keep the report's original figure font sizes untouched** (do NOT bump
  `\tiny`→`\scriptsize`→...; chained bumps are what produced the mess).
- **Adapt colors to the theme** (report's blue/gray → CUHK purple/orange):
  `\fill[blue!60]` → `\fill[cuhk-purple!75]`, `\fill[gray!60]` →
  `\fill[cuhk-orange!45]`, `\fill[gray!50]` → `\fill[cuhk-orange!30]`, node
  fills `blue!8`/`blue!10` → `cuhk-purple!20`/`cuhk-purple!12`, `red!8` →
  `cuhk-lightorange`, `green!10` → `cuhk-yellow!70`. NOTE TikZ `\fill[...]`
  uses bracket syntax; a naive `fill=blue!60` replace misses every bar.
- Porting needs extra preamble: `\usepackage{tabularx}` (report tables),
  `\usetikzlibrary{arrows.meta, positioning}` (Stealth tips + `below=... of`
  syntax) — missing these errors as `Unknown arrow tip kind 'Stealth'` /
  `Unknown operator 'of'`.
- After adding figures, watch for `Overfull \vbox (NNNpt too high)` at
  `\end{frame}` — right column overflowed 684pt after 3 charts; reducing the
  scale factors cleared it (79pt remaining → 0).
- **Bar-chart label spacing (user: \"柱状图的数据标签离柱子太近了，横轴的标签距离也太近\n了\", 2026-08)**: the report's chart label offsets are tuned for A4 and sit\n  too tight on A0. Bump them: data labels above bars/error-bars from\n  `+0.12`/`+0.18` → `+0.4`/`+0.5`; x-axis group labels below the axis from\n  `-0.28`/`-0.45` → `-0.7`/`-0.9`; horizontal-bar value labels right of the\n  bar from `+0.1` → `+0.4`; axis tick labels from `-0.65` → `-0.9`. Apply\n  consistently across ALL ported charts (end-to-end, completion IoU, phase9\n  dual panel, constraint-ablation horizontal bars), not just one.\n- **Same-typed horizontal-bar charts must share ONE coordinate convention**\n  (user, 2026-08: \"这个图的位置坐标数值有点怪，学习一下...Violation accuracy这个图\"):\n  when a poster has two horizontal-bar charts over the SAME 6 configs\n  (constraints-per-graph in block 4, violation-accuracy ablation in block 6),\n  write them with identical conventions or the user flags the odd one out.\n  The violation-accuracy chart's convention (the reference): define\n  `\\def\\base{0.0}` and reference every x as `\\base` / `(\\base+value*\\sc)`;\n  rows top-to-bottom with **row spacing 1.0** (y=5.0,4.0,...,0.0), bar height\n  0.35, label y = bar mid (row+0.175); value label `anchor=west` at\n  `(\\base+bar_length+0.4)`; y-axis `(\\base,5.75)--(\\base,-0.5)`, x-axis\n  `(\\base,-0.65)--(max,-0.65)`; tick marks at y=-0.9 with `\\tiny` labels;\n  axis title at y=-2.2. The constraints chart originally used row spacing\n  0.8 bottom-to-top, `+0.3` label offset, ticks at -0.25, title at -1.0 —\n  all subtly different; user asked to copy the violation-accuracy style.\n  When porting/creating a sibling chart, COPY the existing chart's full\n  coordinate block and change only the values, not the offsets.
  **FINAL: constraints chart sorted DESC by value too** (user, 2026-08: "这个图
  按照倒序排列"): after copying the convention, the constraints chart rows were
  re-ordered by value descending (37.3 All 10 types top → 15.1 Remove all
  ALIGNMENT bottom), matching the violation chart's existing desc order.
  **Scatter axis titles use the reference offsets** (user, 2026-08: "这个图的
  坐标轴标签位置很奇怪 参照Drop ratio/Proposal IoU 的位置"): the 5-seed
  scatter's x-title/y-title must use the same far offsets as the bar charts
  (x at y=-1.6, y at x=-1.45) — the original (-0.75 / -0.5) sat too close to
  the ticks. **LATER TUNED: y-title came back CLOSER** (user, 2026-08:
 "Proposal MSE 离坐标轴数值太远了 稍微近一点"): final accepted y-title x =
 **-1.0** (rotate=90, mid-height y=2.7); x-title stays at y=-1.6. Also for
 scatter points: proposal-only (cuhk-yellow!70 fill) dots AND its legend
 swatch get a `draw=cuhk-orange!60, line width=0.4pt` border (user: "加一个
 深黄色边框（violation-only的颜色）") so the pale yellow reads against white.
 - **"放大20%" on a scatter = the figure FOOTPRINT (xscale/yscale), NOT the
 point dots** (user correction, 2026-08: "不是把点面积放大，是把图的「占地面积」
 point dots": my first pass enlarged `minimum size` on every dot; the user meant
 the whole plot's footprint. Area +20% ⇒ linear factor √1.2 ≈ 1.0954 —
 xscale 2→2.191, yscale 1→1.095 (xscale stretches coordinates only, text
 size untouched, per the xscale rule). Do not touch dot size unless the
 user names the dots. **Later raised to +50%** (user: "两个点状图的图表占地面积 +50%"): area +50%
 ⇒ linear √1.5 ≈ 1.2247 — xscale 2→2.449, yscale 1→1.225. **THEN the user
 corrected the intent: "说错了 我想说的是长宽各+50%" — 长宽各+N% means LINEAR
 (1+N/100) on EACH axis: xscale 2→3, yscale 1→1.5, the FINAL state of both
 scatters.** General rule: area +N% ⇒ multiply xscale AND yscale by
 √(1+N/100); 长宽各+N% ⇒ multiply both by (1+N/100). Verify the changed
 `xscale=` lines with grep (both scatters share the same numbers).
 - **When xscale/yscale changes, axis titles at ABSOLUTE coordinates stretch
   too — rescale their offsets to keep the rendered distance constant** (user,
   2026-08: "横纵轴标签离坐标轴距离不要变" after the 3/1.5 scaling): titles are
   `\node at (x,y)` with absolute coords, so a 1.5× scale pushes them 1.5×
   further from the axes. Fix: `new_offset = old_offset × (old_scale /
   new_scale)` per axis (here x-offsets ÷3, y-offsets ÷1.5). 5-seed scatter:
   x-title y=-1.6 (offset 1.75 from x-axis y=0.15) → y=-1.0167; y-title
   x=-1.0 (offset 1.3 from y-axis x=0.3) → x=-0.5667. constraints scatter:
   x-title y=-1.6 (x-axis at y=0) → y=-1.0667; y-title x=-1.0 (y-axis at
   x=0) → x=-0.6667. Compute from the axis positions, don't eyeball.
 - **Bar-chart delta annotations: control reference line + colored ± deltas +
 green overlay** (user, 2026-08: "我想让你画一点标注来体现±的对比，然后具体的文
 字用对应的颜色" then "把0.939 0.916多出来的部分用淡绿色覆盖一层，同时在上面标上
 白色的+xx pp试试" — with corrections "白色文字改成黑色 不要用formula包裹"):
 the violation-accuracy ablation chart annotates every bar relative to the
 control (0.908). Accepted design, all three pieces together:
  - DASHED purple reference line at the control value spanning the full chart
    height: `\draw[dashed, cuhk-purple!70, line width=1pt]
    ({(\base+(0.908-0.84)*\sc)},-0.5) -- ({(\base+(0.908-0.84)*\sc)},5.75);`
    (insert right before the axis draw) — bars right of it improved, left of
    it degraded, so the ± contrast reads at a glance.
  - Value labels carry colored deltas with direction arrows: gains
    `0.939 {\color{green!60!black}$\rightarrow$ $+3.1$pp}`, losses
    `0.903 {\color{red!80!black}$\leftarrow$ $-$0.5pp}`, control row
    `{\bfseries\color{cuhk-purple!90} 0.908 (control)}`.
    **FINAL: the colored ± delta text was REMOVED from the value labels**
    (user, 2026-08: "删去红绿色的pp文字"): value labels are PLAIN numbers
    (`0.939`, `0.916`, ... `0.878`; control keeps
    `{\bfseries\color{cuhk-purple!90} 0.908 (control)}`). The ± contrast is
    carried ENTIRELY by the green overlay + red boxes + dashed control line —
    no colored text on the bars. Do not re-add colored pp text.
  - GREEN OVERLAY on the segment of a bar that exceeds control:
    `\fill[green!30] ({(base+(0.908-0.84)*sc)},5.0) rectangle
    ({(base+(0.939-0.84)*sc)},5.35);` (control-x → bar-end-x, same y as
    the bar), plus a label at the segment MIDPOINT: x = (control+value)/2
    → `({(base+((0.908+0.939)/2-0.84)*sc)},5.175)`. **FINAL overlay shape:
    HALF-HEIGHT band only** (user: "淡绿色只覆盖中间一半，上下留出黄色部分") — of
    the 0.35-tall bar, the green rect spans y=row+0.0875 → row+0.2625 so the
    orange bar shows above and below; the label stays at the bar midline
    (row+0.175). Label text is **BLACK, NON-bold, PLAIN TEXT — never white,
    never math-wrapped, never \bfseries** (user rejected `white`,
    `$+3.1$pp`, AND bold: "白色文字改成黑色 不要用formula包裹" then "pp文字不要
    加粗"): `\node[font=\scriptsize, black] at (...) {+3.1pp};`.
  - RED HOLLOW boxes on the deficit side (user, 2026-08: "0.903 0.889 0.878
    左侧不足部分画一个红框（空心的），然后标注黑色非加粗文字"): for bars BELOW
    control, draw an empty (draw-only, no fill) rectangle from the bar end to
    the control line, **FULL bar height** (user: "红框高度100%" — final is
    0.35 tall like the bar, NOT the half-height band of the green overlay):
    `\draw[red!45, line width=1pt] ({(base+(0.903-0.84)*sc)},2.0)
    rectangle ({(base+(0.908-0.84)*sc)},2.35);` — **LIGHT red `red!45`,
    NOT `red!80!black`** (user: "太红了 用淡红色"). **FINAL label placement
    (user overrode the earlier "放右边" request: "不是，pp文字在红框中心对齐
    0.9xx的数值在基准线右侧")**: the −pp label sits at the RED BOX CENTER —
    `\node[font=\scriptsize, black] at ({(base+((0.903+0.908)/2-0.84)*sc)},2.175)
    {-0.5pp};` — while the VALUE labels (0.903/0.889/0.878) go to the RIGHT of
    the control line, same x as the 0.908 (control) label, left-aligned:
    `\node[font=\footnotesize, anchor=west] at
    ({(base+(0.908-0.84)*sc+0.4)},2.175) {0.903};`. So per deficit row:
    red box spans bar-end→control at full bar height, −pp text centered
    inside the box, the 0.9xx value right of the dashed line. If the user
    reports "位置还是错的" for these labels, check WHICH label they mean
    (value vs pp) — the two have different anchors on purpose.
    Green overlay + red boxes + dashed control line together make the ±
    contrast read without words.
    **FINAL value-label offset: +0.2, not +0.4** (user, 2026-08: \"0.939 0.916
    0.908等等都左移离柱状图近一点\" then \"0.903 0.889 0.878也要调啊\"): ALL six
    value labels sit closer to their anchor — above-control rows at
    `({(base+(value-0.84)*sc+0.2)},...)`, below-control rows at
    `({(base+(0.908-0.84)*sc+0.2)},...)` (right of the dashed line). The
    earlier +0.4 was too gappy; +0.2 is the accepted gap for every row.
    **FINAL: the constraint-ablation KPI cards (3×2 grid) are COMMENTED OUT**
    (user, 2026-08: \"这几个东西的KPI卡片删掉 注释掉\"): with the bar chart now
    carrying the ± deltas directly (green overlay / red boxes / control
    line), the 6 cards are redundant. Comment every line with `% ` (keep the
    design notes above for restore) — do not delete.
 - **"orange" bar fills = the LIGHT shade `cuhk-orange!30`, not `cuhk-orange!60`**
 (user correction, 2026-08: "刚刚说的orange不是这个这么深的黄色，使用Remove
 allALIGNMENT...这个柱子同款的颜色"): when the user asks to color bars orange
 "like the ablation bars", copy the ablation chart's `cuhk-orange!30` —
 `cuhk-orange!60` reads as a dark yellow and gets rejected. Same convention
 in the 4 orange bars of the dual-panel chart (joint/violation-only in the
 Violation head panel; joint/proposal-only in the Proposal head panel).
 - **Paired before/after bars: use "上右下" polyline ARROWS, not fill overlays**
   (user, 2026-08: "现在这种体现加减的形式不好看。你先去掉，然后在柱状图顶部从黄色
   到紫色加一个折线箭头（上右下）（红色或绿色）并且在箭头上方标注数值"): on the
   end-to-end charts (Precision/Recall/F1 and TP/FP/FN), each pair is
   orange=VLM only → purple=VLM+GNN, and the user REJECTED the green/red fill
   band style used on the constraint-ablation chart — for PAIRED bars the
   accepted annotation is a **polyline arrow from the orange bar top to the
   purple bar top** with path up → right → down (arrow tip lands on the purple
   top):
   ```latex
   \draw[green!60!black, line width=1pt, -{Stealth}]
     (1.0,{0.382*\sc}) -- (1.0,{0.393*\sc+0.4}) -- (2.0,{0.393*\sc+0.4}) -- (2.0,{0.393*\sc});
   \node[font=\scriptsize, green!60!black] at (1.5,{0.393*\sc+0.65}) {+1.1pp};
   ```
   (start x = orange bar center, start y = orange top; up to the higher top
   +0.4; across to the purple bar center; down to the purple top. Label at the
   midpoint x, top+0.65.) Color semantics: green = change is GOOD, red =
   change is BAD — TP +106 green, FP +84 red, FN −106 green (FN decreasing is
   good; arrow goes from the taller orange top down to the shorter purple top).
   A bare `{+106}` / `{-106}` label uses plain text (en dash `--` for
   negatives, per the en-dash rule). **Do NOT spell out the color semantics
   in prose** (user, 2026-08: "(green: good, red: bad)不用写" — I had added
   that parenthetical to the TP/FP/FN chart intro and the user deleted it):
   the arrow colors carry the good/bad reading themselves; the intro should
   state the numbers ("The recovered elements are real: **106** more true
   positives, **106** fewer false negatives, at the price of **84** new
   false positives.") and stop there.
   **FINAL TUNED GEOMETRY (user iterated twice, 2026-08: "还是离数据标签太近
   了 在调整" then "太高了 回来一点")**: the data labels sit at bar-top+0.5, so
   the first-pass arrow (start +0.4, label +0.65) COLLIDED with them; the
   over-corrected pass (+1.2/+1.6/+2.0, legend 8.4, axis 8.2) was too high.
   Accepted final: arrow start at bar-top **+0.9**, horizontal segment at
   **+1.3**, value label at **+1.35 → +1.65** (above the 0.5 data labels with
   clear air), y-axis top raised to **7.9**, legend moved up to y=8.1–8.35.
   Both charts (P/R/F1 and TP/FP/FN) share these offsets; keep the arrow
   verticals at the bar CENTERS (1.0/2.0, 3.0/4.0, 5.0/6.0), not the bar
   edges. Verify label clearance with pdftotext -bbox (data label yMax vs
   arrow-label yMin ~30pt apart).
 - **Minus signs in chart annotations use EN DASH, not hyphen** (user,
   2026-08: "刚刚图标里所有的减号用en dash"): plain-text chart labels like
   `{-0.5pp}` become `{--0.5pp}` (LaTeX en dash). Math-mode `$-$` in prose
   and tables stays as-is; the request was for the chart annotation labels
   only. The user checks BOTH prose AND chart text layers for stray hyphens
   (图标里查了吗) — grep the tikzpicture node bodies too, not just `$-`.
   Em dashes have NO spaces around them** (user, 2026-08: "em dash前后不要有
   空格"): write `---` glued to the words (`small one---training`, `wins---it
   keeps`, `ratio---the more`), never ` --- `. Sweep ALL occurrences when
   this comes up (grep ` --- `), including across line breaks (an em dash at
   end of line joins to the next line's first word with no space). CRITICAL:
   an em dash at the END of a source line followed by a newline still
   renders as "word--- nextword" WITH a space (TeX turns the newline into a
   space) — fix by ending the line with `%`: `wins---%` then the next line
   `it keeps...` renders "wins---it". Check for `---$` at line ends after any
   em-dash sweep (grep -n -- "---$" poster.tex).
 - **Poster numbers: NO math-mode wrapping — plain text with real glyphs**
   (user, 2026-08, 数字不要用公式包裹, on the Conclusion bullets AND KPI
   cards): `$+56\%$` → `+56\%`, `$+2.0$pp` → `+2.0pp` in both the Conclusion
   itemize and the three KPI cards. This extends the earlier label rule
   (green-overlay text is `{+3.1pp}`, not `{$+3.1$pp}`) to ALL displayed
   numbers poster-wide. En dash for negatives in the same plain-text style
   (`--106`, `--0.5pp`).
 - **Large counts get thousands separators** (user, 2026-08, TP FP FN的图
   数字要有三位分割的逗号): in the TP/FP/FN chart write data labels and axis
   ticks as `{1{,}126}` / `{3{,}557}` / `{1{,}000}` (LaTeX thin-group `{,}`)
   — data labels AND the axis tick labels (use a `\foreach \v/\l in
   {1000/1{,}000, 2000/2{,}000, ...}` pair list so the numeric \v still
   drives the tick position while \l is the formatted label).
 - **Scatter groups can be circled with TikZ ellipses computed from the point
   data** (user, 2026-08, 把三组点阵用一个明显的椭圆圈起来提示读者): compute
   per-group center = mean(x)*sx, mean(y)*sy and radii = (max−min)/2 ×
   scale × padding (x-pad ~1.35, y-pad ~1.45 so no point sits on the line),
   then `\draw[<group color>, line width=1pt] (cx,cy) ellipse (rx and ry);`
   placed BEFORE the `\node[circle,...]` dots so dots render on top. Colors
   match the group dots (purple/orange/deep-yellow). All coordinates use the
   same scaled formulas as the dots (here x*8−2.8, y*40).
 - **Chart-intro prose: replace AI-flavored filler with the concrete
   statistic** (user, 2026-08: "去AI味" on my added line): a lead-in like
   "More extracted constraints lead to more detected violations --- the two
   are strongly correlated across screenshots:" is pure AI slop (vague
   "lead to" + em-dash + no numbers). Rewrite with the actual figure:
   "Violation counts track constraint counts (correlation 0.96 across 32
   screenshots):" — a specific number beats a vague claim, and it primes the
   reader for the scatter that follows. When adding intro prose before a
   figure, lead with the data point the figure shows.
 - **Results prose: OPINIONATED, conclusion-first sentences** (user, 2026-08:
   "result的正文部分，尽量讲有观点指向性的结论"): every Results paragraph
   leads with a judgment, then supports it with numbers — never a neutral
   recitation of what the chart shows. Patterns that passed:
   - Training ablation: "joint training is clearly the right choice --- it
     keeps both heads strong, while single-objective training collapses
     whichever head is not supervised (0.116 vs. 0.051; 0.489 vs. 0.876)."
   - Constraint ablation: "containment is the most valuable single
     constraint (removing it hurts most, --1.9pp), yet alignment
     constraints actively hurt --- dropping all of them helps (+3.1pp)."
   - Completion: "the GNN wins exactly where it should --- the more
     elements are masked, the more structure the graph exploits (39% / 56%)."
   - End-to-end: "recall improves most, exactly the failure mode it was
     designed for; precision gains less (+1.1pp) because some recovered
     candidates are false positives, the price of aggressive completion."
     This last one also TEACHES the TP/FP/FN color semantics: green =
     change in the GOOD direction (TP up, FN down), red = change in the BAD
     direction (FP up) — FN −106 is green even though negative, FP +84 is
     red even though positive. When the user asks why a color, explain
     direction-of-good, not sign-of-number.
   **"这个图前面加说明" is ambiguous when a block holds MULTIPLE figures —
   confirm WHICH one** (user, 2026-08: "说错了，不是这个图，是那个线性回归的
   图" — I added prose before the constraints-per-graph bars, the user meant
   the regression scatter right below): when the user asks for a lead-in
   ("加一小段说明文字吧"), and the block contains two or more charts, either
   ask which figure or check the most recently discussed one; an intro
   inserted before the WRONG figure reads as orphaned text ("没看见啊 在哪").
   **Same for multi-figure COLOR edits — "这两个图/这部分两个流程图都加入红绿色
   指示" needs a clarify() when the natural interpretation spans more than
   two charts** (user, 2026-08: I asked which two and the answer was
   "就是这两个：P/R/F1 柱状图 + TP/FP/FN 柱状图（已加好）"): do the work on
   the confirmed pair, then continue — a wrong guess means redoing the
   annotation pass on the wrong figure.
   Also: an intro the user rejects gets deleted on request ("Each constraint
   set yields...删掉") — don't argue, remove it.
   **SECOND de-AI pass: numbers go to the CHARTS, prose keeps ONE bolded
   headline number per paragraph** (user, 2026-08, right after the
   opinionated rewrite: "去AI味。具体数字不要频繁提及，重点数字加粗"): the
   first-pass opinionated prose still carried a number soup (e.g. "0.116 vs.
   0.051; 0.489 vs. 0.876" inline, "39% / 56%", "0.235→0.257"). The accepted
   final style leaves detail numbers to the figures and keeps only the
   conclusion + ONE bolded key figure per paragraph:
   - Training ablation: "joint training wins --- it keeps both heads strong,
     whereas single-objective training lets the unsupervised head collapse
     (proposal MSE \textbf{0.116}, violation accuracy \textbf{0.489})."
   - Constraint ablation: "dropping them all improves accuracy by
     \textbf{+3.1pp}, and keeping only ALIGNMENT is the worst configuration."
     (the −1.9pp/−3.0pp detail lives on the chart's red boxes)
   - Completion: "reaching \textbf{+56\%} IoU over nearest-neighbor" (drop
     0.6/0.8 numbers dropped).
   - End-to-end: "recovers \textbf{106} missed elements and lifts recall most
     (\textbf{+2.2pp}) ... Precision rises less (\textbf{+1.1pp}) ...
     at under 1~ms per screenshot" (before/after values dropped).
     **\"One bolded headline number\" is about DENSITY, not a literal single
     bold** (user, 2026-08: \"这几段还有问题\" after the de-AI pass): when a
     paragraph names SEVERAL key figures, ALL of them get `\\textbf{}` — my
     first pass left `106` and `+1.1pp` unbolded next to a bolded `+2.2pp`
     and the user flagged the paragraph. Same in the TP/FP/FN chart intro
     (final accepted text): \"The recovered elements are real: \\textbf{106}
     more true positives, \\textbf{106} fewer false negatives, at the price
     of \\textbf{84} new false positives.\" — every named count bolded.
     When the user pastes a paragraph back saying \"还有问题\", first check
     bold consistency across ALL named numbers, then wording/em-dash.
   Judgment sentence + bolded key number + no number clutter: that's the
   target. If a number is not the headline, it belongs on the chart, not in
   the prose.
   **THIRD pass: full-text AI-flavor sweep ("全文检查AI味") — concrete
   word-level replacements** (user, 2026-08): after targeted de-AI edits, the
   user may ask to scan the WHOLE poster's prose for AI tells. Actual finds
   from the sweep (fix all of these, not just the section in hand):
   "stem from" → "come from" (AI-favored verb phrase); repeated verb
   "refines...refined boxes" → "outputs...repaired boxes" (elegant-variation
   trap and weak verb); "The gains appear when" → "show up" (weak verb
   "appear"). Re-read every block's prose once, list the finds, fix, compile.
   Watch also for: "Additionally/Moreover/leverage/underscore", em-dash
   runs, and "-ing" filler phrases — none survived in this poster's final
   text.
   **Parenthetical audit: classify every `(...)` — fold-in what reads better,
   keep what must stay, delete duplicates** (user, 2026-08: "检查所有括号内内容
   是否可以去掉，注意，并非用破折号替代，而是融入句子，汇报给我，并且推荐我哪些地方
   值得改，哪些地方必须用括号"): scan the prose for ALL parentheticals (regex
   `\(([^()]{2,120})\)` on comment-stripped source, skipping tikzpicture bodies
   and LaTeX commands) and report in three classes BEFORE editing — the user
   explicitly wants a recommendation list first, then approves ("BCD类直接按照
   你的想法改"):
   - **MUST KEEP as parens**: math-set notation `(e_i,c_j)`; hyperparameter
     blocks `(hidden dim 128, AdamW + cosine annealing)`; evidence numbers
     supporting a judgment `(proposal MSE 0.116, ...)`; experiment setup
     `(200 real RICO screenshots, Qwen3-VL Flash)`; illustrative examples
     `(small icons, dividers, nested containers)`.
   - **FOLD INTO THE SENTENCE** (worth changing): a subject list used as the
     example of "programs" → make the list the subject ("Programs that look
     at a phone screen (screen readers, UI testers, agents)..." → "Screen
     readers, automated UI testers, and software agents that look at a phone
     screen..."); attribute phrases → "message passing (mean aggregation)" →
     "mean-aggregation message passing", "features (DINOv2)" → "frozen
     DINOv2 visual features"; loss names → "deltas (smooth L1)" → "deltas
     with a smooth-L1 loss", "(binary cross-entropy)" → "via binary
     cross-entropy"; section-scope tags → "ablation (violation accuracy)" →
     "ablation on violation accuracy".
   - **DELETE duplicates**: "(57K parameters, CPU-only)" in End-to-end
     duplicated the 57K already stated in Research Objectives — drop the
     repeat. Never substitute em dashes for the removed parens (user
     explicitly forbade that); the parenthetical content either joins the
     clause or disappears.
   Fold-in edits must keep the sentence grammatical and preserve all
   information; when in doubt between classes, put it in the recommendation
   table and let the user pick.
   **Constraint-type names in PROSE use `\texttt{}` uppercase, same as chart
   labels** (user, 2026-08: "这一段注意ALIGNMENT GRID SPACING CONTAINMENT和
   ALIGNMENT的格式应该怎么样" after I wrote them as plain lowercase words):
   `\texttt{CONTAINMENT}`, `\texttt{ALIGNMENT}`, `\texttt{GRID}`,
   `\texttt{SPACING}` — monospace + all-caps everywhere (bar labels, dot
   points, prose), never plain "containment"/"alignment" in body text.
   Check the whole poster for stray naked constraint names after any rewrite.
 - **Dual-panel chart category labels: HORIZONTAL with `\\` line breaks, never
 rotate=45** (user, 2026-08: "横轴不要用斜向标签，就横写，然后在violation-后面和
 proposal后面加换行符"): `\node[font=\scriptsize, anchor=center] at (1.1,-0.9)
 {joint};` and `\node[font=\scriptsize, anchor=center, align=center] at
 (2.5,-0.9) {violation-\\only};` (align=center required for the `\\` break).
 Rotated labels were the initial ported style; the user wants straight
 reading labels on both panels.
- **Tick marks: mirror the reference chart's tick GEOMETRY, not just its
  style** (user, 2026-08: "这两个图的坐标轴刻度风格参照新图，在坐标轴外侧" then
  "再仔细读代码检查坐标数值 现在还没有完全还原"): the dual-panel ablation
  chart's y-ticks originally straddled the axis (`\draw (-0.1,y) -- (0.1,y)`).
  The accepted "outside" style (from the 5-seed scatter) is floating short
  ticks LEFT of the axis: y-axis at x=0.3 → `\draw (0.15,{\v*40}) -- ++(-0.1,0);`
  (line from axis−0.15 to axis−0.25) with labels
  `\node[anchor=east, font=\tiny] at (0.1,{\v*40}) {\v};` (right edge at
  axis−0.2). Mirroring onto an axis at x=0: `\draw (-0.15,{\v*\sc}) -- ++(-0.1,0);`
  + labels at `(-0.2,{\v*\sc})`. Axis TITLES mirror at the same offset too:
  scatter title x=−1.0 with axis at 0.3 ⇒ offset 1.3 ⇒ panel title at x=−1.3.
  When the user says "参照新图", mirror EVERY numeric offset (tick start,
  tick length, label x, title x) from the reference figure — a first pass
  that flipped direction but kept different offsets got called out
  ("还没有完全还原").
- **Label collisions CASCADE — after bumping offsets, check the neighbors** (user: "Drop ratio with 0.4, 0.6几乎重叠了，End-to-end图例和数据标签几乎重叠了"): moving tick labels DOWN to `-0.9` puts the x-axis TITLE (which sat at `-0.75`, same line) on top of them — move the title further down to `-1.6`. Moving data labels UP to `+0.5` puts the tallest label (e.g. `0.393*14+0.5 = 6.0`) exactly at the LEGEND's y=6.0 band — move the legend up to y=6.8 (legend rect 6.8–7.05, above the axis top).
- **ROUND 2 of the same cascade (user: "Violation accuracy 和0.88 0.90重叠了" then "Violation head Proposal head 和数据标签重叠了 拉大间距")**: after tick labels moved to `-0.9` in the constraint-ablation horizontal chart, its x-axis TITLE at `-1.5` still overlaps the tick text (A0 `\footnotesize` glyphs are ~0.7cm tall) — move the title to `-2.2`. And in the phase9 dual-panel chart, the PANEL TITLES (`Violation head` / `Proposal head`) at y=4.5 collide with the tallest bar's data label (0.898 bar top ≈3.59 + error cap + 0.45 label offset ≈4.36) — move both panel titles to y=5.4. General rule: after ANY label-offset bump, re-derive the vertical extents of (a) the label text itself, (b) the element it now neighbors (axis title, legend, panel title) at A0 font sizes — offsets that looked fine on A4 are ~2× too small on A0.
- Text + figure numbers must stay consistent with the report (same ablation
  values, IoU, F1 in both places).
- **Every chart gets BOTH axis titles** (user, 2026-08: "横纵轴没有明显的标题" →
  add the missing one): x-axis title `\node[font=\footnotesize] at (cx,-0.95)
  {...}` below the axis; y-axis title `\node[font=\footnotesize, rotate=90] at
  (-0.55,cy) {...}` rotated, positioned left of the y-axis around mid-height
  (1.7 for a 3.55-tall plot). Match the existing figures' style exactly
  (`\footnotesize`, same offsets). Count-style y-axis labels use `\# of
  screenshots` (literal `\#`, user spelling: "写成# of screenshots") — not
  "Number of ...".
  **After raising an axis top (e.g. to fit arrow labels), re-center the
  rotated y-axis title at the NEW mid-height** (user, 2026-08: "score和count的
  标签没有对齐图表中间"): the title sat at y=2.7 while the axis had grown to
  0–7.9 — move it to y=3.95. Whenever the axis range changes, recompute
  cy=(ymax+ymin)/2 for the y-title; don't leave the old mid guess.
- **Single-series histogram: graduated purple opacity, darker = larger value**
  (user, 2026-08: "4 - 94 依次用不同透明度的紫色"): for a one-series bar chart
  (the missed-fraction histogram, bars 4/12/36/54/94), the user wants each
  bar in a different purple shade instead of a uniform fill. Encode the
  tint as a third `\foreach` field: `\foreach \i/\c/\t in {1/4/30,2/12/45,
  3/36/60,4/54/75,5/94/90}` then `\fill[cuhk-purple!\t] ...` — value-driven
  opacity from light (`!30`) to dark (`!90`). Applies to single-series
  histograms only; paired-series charts keep the fixed purple/orange pair.
- **Wrap every figure in `\begin{center}...\end{center}`** — a bare
  `\begin{tikzpicture}` (or resizebox) is an inline box that sits left-aligned;
  without the center wrapper every figure hugs the left margin (user: "对齐也是
  乱七八糟的"). Applies to the table too.
- Pipeline figure: user asked to REDESIGN it in CUHK style — the A4
  single-row 6-node flow gets crushed in a narrow column. Use a two-row snake
  layout: row 1 `Screenshot → Lightweight VLM → Noisy JSON` (left→right), then
  down to row 2 `Bipartite Graph → GraphSAGE → Corrected JSON` (right→left).
  CUHK colors: start/end nodes `cuhk-yellow!40`, noisy `cuhk-orange!25`,
  graph/GNN `cuhk-purple!25`, arrows `cuhk-purple!70`. **Node text is BLACK**
  (`text=black` in the box style — user: "流程图的node文字用黑色"; no colored
  node text). Also: an intro paragraph describing the pipeline goes ABOVE the
  figure inside block 4 (user: "把流程图说明放在流程图上放" — they meant a prose
  intro, not the per-node labels; copy the report's pipeline paragraph), and
  the old duplicated intro below the figure shrinks to just the formal
  definition ("Formally, $G=(\mathcal{V},\mathcal{E}_{\text{edge}},\phi,\psi)$:
  element nodes on one side...").
- **Pipeline labels: TOP-row labels go ABOVE their nodes, BOTTOM-row labels
  stay BELOW** (user fixes: "你把上面三个label的描述放在label上方不就好了"
  then "下面三个Bipartite GNN GraphSAGE还是维持原样"): a label
  `below=0.22cm of noisy` sits exactly on the vertical `noisy → graph` arrow
  and overlaps it, so move the TOP-row labels (detection / 10--30% omissions)
  to `above=0.22cm of <node>`. The BOTTOM-row labels (constraint extraction /
  Δx, proposals) keep `below=0.22cm of graph/gnn` — the user explicitly wants
  them unchanged. Do NOT try to route the arrow around the label with
  `(noisy.south) -- (10.8,-1.7) -- (graph.north)` — user rejected that detour;
  moving the label is the simple fix. Keep row-1 arrows (`shot--vlm`,
  `vlm--noisy`) explicit — easy to drop them accidentally when rewriting the
  arrow block.
- **All 6 pipeline nodes are single-line text** (user: "Lightweight VLM，Noisy
  JSON等不用拆成两行" + "CorrectedJSON BipartiteGraph 也顺带改"): node bodies
  are `{Screenshot}`, `{Lightweight VLM}`, `{Noisy JSON}`, `{Bipartite Graph}`,
  `{GraphSAGE}`, `{Corrected JSON}` — NO `\\` line breaks in any node. Single-
  line nodes are wider; after making them all single-line the pipeline's
  `xscale` needed trimming 2.5 → 2.4 to clear the 18.7pt Overfull at the right
  edge ("Bipartite Graph" is the widest node). The two bottom-row labels are
  also single-line: `{constraint extraction}` and `{$\Delta\mathbf{x}$,
  proposals}` (user: "∆x,proposals constraintextraction 单行就可以").
- **"Shorten the arrow" means close the ROW GAP, not truncate the arrow**
  (user: "我不是只要缩短箭头长度 那你下面的东西也得移上来接上啊"): when asked
  to shorten the `noisy → graph` vertical arrow by 1/3, do NOT end the arrow
  mid-air at `(noisy.south) -- (8.8,-2.12)` — that leaves a dangling arrow tip
  and the user rejected it. Instead move the WHOLE second row up (y -3.4 →
  -2.27, i.e. 3.4 × 2/3) and keep `\draw[arr] (noisy) -- (graph);` so the arrow
  still connects node-to-node. "Shorten the gap" is the semantic the user
  wants; the arrow length follows from node positions.

## GPT-generated poster figures (2026-08, user: "这部分让GPT画吧，你直接把提示词给我")

User workflow: Hermes writes a **self-contained figure prompt** → user forwards it to
ChatGPT → image lands in `~/Downloads/` (name pattern `ChatGPT Image <date> at <time>.png`)
→ Hermes reviews with vision_analyze and proposes a block placement. This is how the two
real-demo figures for this poster were produced.

**Same pattern for MECHANISM problems: when the user is tired of debugging
locally, they ask for a PROMPT to forward to GPT themselves** (user, 2026-08:
"别搞了，给我提示词我问gpt吧" — after repeated failed side-by-side layout
attempts). Write the same self-contained problem report used in the
external-AI pitfall (environment, exact symptom, code, what was tried, the
precise question) as a **copy-paste prompt for the user** — not a prose
summary of your plan. The user forwards it, pastes the answer back, and
expects you to implement it verbatim. When the answer comes back with
competing variants (tabularx vs tblr vs fixed minipage), the working one is
the tabularx recipe below; and when the user later asks to revert
("恢复原有的"), revert — even if the fix verified side-by-side via bbox.

Prompt-writing requirements (all were needed for usable output):
- **Exact source paths** for real-data figures: `demo_data/overlays/demo_10067.png`
  (BEFORE/AFTER overlay), `demo_data/screenshots/10067.jpg`, `demo_data/confidence/10067.json`
  + `summary.json` (bbox format must be read from the JSON before drawing). Never let GPT
  invent a UI from scratch when real RICO data exists — credibility depends on it.
- **Style rules that match this poster**: solid fills, no transparency/gradients/shadows,
  no `\resizebox`/`transform shape`, real LaTeX font sizes, CUHK purple/orange palette,
  flat minimal academic look.
- **Output spec**: resolution/DPI, side-by-side halves pixel-aligned, legend with EXACTLY
  N entries, save path.
- **For PIL-overlay figures**: dashed lines aren't native to PIL — either draw segments
  manually or use an RGBA overlay layer with ~40% alpha; line widths ≥4px for poster scale;
  print chosen element pairs + bboxes to stdout so a human can verify the constraint is real.

**Demo BEFORE/AFTER diff — the two-color design (user: "蓝色框很混乱")**: the original
overlay used THREE colors (red=VLM, green=GT, blue=GNN) and read as clutter; the user
rejected it. The clean diff keeps exactly two visual levels: thin GRAY boxes = VLM
detections (both halves), thick BRIGHT BLUE boxes + white circled numbers 1..N = GNN
recovered (AFTER half only). No GT boxes, no third color. Top captions keep the counts:
`BEFORE (VLM only): 17 detections` / `AFTER (VLM + GNN): 24 detections (+7 recovered)`.
Numbered labels let the caption reference specific recoveries.

**Review GPT output for domain errors**: the generated diff had a blue box on the status
bar (time/battery) — status-bar chrome is not a real GUI element, flag it. Also check that
omission markers carry an explicit "omission" word, not just a "?" (ambiguous).

**Native TikZ redraw of GPT schematic figures (user: "14:52这个你可以用代码直接复刻吧")**:
when the GPT figure is a SCHEMATIC mockup (not real data), the user prefers it redrawn as
native TikZ inside the poster — keeps text at real LaTeX sizes and style identical to the
other figures. Only real-data figures (screenshots with overlays) stay as PNG. Recipe for
the VLM-error example (Recipe App two-panel): `\checkmark` requires `\usepackage{amssymb}`
in the preamble (undefined otherwise); the external-AI version (two equal panels, left =
gray correct box + red shifted/rotated wrong box + "box misalignment" callout + dashed
circle `?` on the missed Share button, right = all elements green-filled/cuhk-purple with
`\checkmark`s) is the accepted reference — its coordinate design makes right panel =
left panel + 8.6 in x, so keeping panels aligned is trivial. When the external version is
TALLER than the space (8.15cm vs ~7cm column headroom → Overfull \vbox 29.5pt), compress
ALL y-coordinates by a factor (×0.82, then ×0.72 for safety) with a line-based Python
regex — x stays, text sizes untouched, boxes shrink proportionally; verify one compile to
0 Overfull. Width 15.4 units fits the left column as-is (1 unit = 1cm in beamerposter).
When the user pastes an external AI's complete TikZ code saying it's "更适合作为参考实现",
adopt it (with fit adjustments) rather than defending your simpler version.

**Figure placement INSIDE a block — "移到中间栏" means TOP, following the block
content, NOT the bottom** (user, angry: "傻逼，不是让你放在中间栏最下面，是让你放在中间栏
最上面，接着内容的"): when the user asks to move a figure into another column, the default
position is right after the block title / at the top of the block content flow. I placed it
at the block END (after the phase9 chart) and got corrected. Insert between `\begin{block}`
and the block's intro prose. Same rule applies to any "放XX栏" request.

**BUT: standalone figures that don't belong to any numbered section go at the top of the
COLUMN, OUTSIDE all blocks** (user: "VLM output vs After GNN的图不属于第五部分，不要放在
5. Models下面啊", 2026-08): the VLM-error example is motivation/illustration, not Models
content — putting it inside `\begin{block}{5. Models}` was wrong even at the top of that
block. Fix: move the whole `\begin{center}...\end{center}` figure block to sit right after
`\begin{column}{\colwidth}` and BEFORE `\begin{block}{5. Models}`. A bare figure in a
column (no block wrapper) renders fine; a standalone one-line prose intro (`\emph{VLM
output errors vs.\ GNN-corrected layout}:`) can precede it — but do NOT wrap it in an
extra `\begin{center}` (the figure block already has its own → double center = unbalanced,
"File ended while scanning use of \beamer@collect@@body").

**When moving a figure to a roomier column, scale it UP** (user: "整体拉宽拉高一些，
这部分可以移到中间栏"): y-coordinate regex scaling works both directions — compress
(×0.72–0.82) when the target column is tight, expand (×1.15) when it has headroom.
CRITICAL ORDERING: if you also need to reposition detail marks (checkmarks etc.) to the
boxes' corners, run the y-scale FIRST, then compute the new corner positions from the
SCALED box geometry — otherwise your hand-computed positions get re-scaled and drift.

**Detail placement rules for the error-example figure (user-verified, 2026-08)**:
- Omission circle must sit ON the missed button's top edge: center_y = button_top + radius
  (with ~0.05 slack so the circle line clears the button's border); the first attempt left
  a 0.19 gap and the user said "扣紧上下边". The `?` inside needs
  `\raisebox{0.3ex}{?}` or the glyph sits visibly below the circle's visual center (baseline
  effect at `\scriptsize`).
- The "box misalignment" callout goes on the RIGHT of its arrow: `anchor=west` label with
  the arrow starting at the label's left edge and pointing left-up at the red box
  (user: "box misalignment在箭头右边"). First version was `anchor=east` label left of the
  arrow — wrong side.
- Right-panel `\checkmark`s go in each box's BOTTOM-RIGHT corner, not right-middle:
  `(right_edge - 0.25, bottom_edge + 0.05)` for buttons; tall boxes (title bar, img) use
  their own bottom edge (user: "右侧的勾放到方框右下方").

**Locating a figure for verification — color-mask first, then crop** (2026-08): when
vision_analyze crops keep landing on the wrong region (it repeatedly reported the Models
formulas instead of the figure below), locate the figure by its fill colors FIRST:
numpy/scipy mask on the signature colors (green!30 fills, cuhk-yellow!40 boxes,
cuhk-purple!25) + `scipy.ndimage.label` connected components to get the true y-range, then
crop and vision-check ONCE. Don't guess y offsets from the page layout.

## Adding data-viz figures computed from experiment JSONs (2026-08)

When the user asks to add charts for results NOT in the report (e.g. "都做"
= make all six: GT-vs-VLM element-count histogram, per-image missed-fraction
histogram, constraints-per-graph bars, 5-seed trade-off scatter, constraints-
vs-violated scatter, conclusion KPI cards), compute ALL numbers first in one
Python pass over the experiment JSONs (`experiments/vlm_completion/*.json`),
print bins/means/scatter coords, then hand-write each TikZ figure with those
values hardcoded. Conventions that keep new figures consistent with ported ones:
- Same axis-title style as every other figure: x `\node[font=\footnotesize]
  at (cx,-0.95) {...}`, y `\node[font=\footnotesize, rotate=90] at (-0.55,cy)
  {...}` (cy ≈ mid-height of the plot), tick labels `\tiny`, data labels
  `\scriptsize`. Count axes are labeled `\# of screenshots` (literal `\#`,
  user spelling — not "Number of ...").
- Histogram bars: `\def\sc{...}` scale, `\fill[cuhk-purple!75]` for the
  primary series; paired-series charts (GT vs VLM) use `cuhk-purple!75` +
  `cuhk-orange!45` with a legend in the top-right.
- Scatter: `\node[circle, fill=<color>, inner sep=0pt, minimum size=0.18cm]
  at ({formula},{formula}) {};` — points as circle nodes so `xscale` doesn't
  stretch them; legend as `\fill` swatches + `\scriptsize` labels.
- Six figures ≈ +425pt of column height; expect `Overfull \vbox` and plan to
  reclaim space (compress prose, shrink screenshots, or drop a figure the
  user reconsiders). The Intro GT-vs-VLM histogram was added then REMOVED by
  user ("introduction部分的图去掉") — Intro stays text-only.
- **Sibling charts must render at the SAME width — equalize x-scale, don't
  guess** (user, 2026-08: "Constraints per graph学Violation accuracy一样撑满
  90%宽度"): when a poster has two horizontal-bar charts over the same 6
  configs and the user wants one to fill the column like the other, compute
  the target xscale so the x-axis SPANS match: `new_xscale = (ref_xrange ×
  ref_xscale) / own_xrange`. Concrete: violation chart x-axis 0→6.6 @
  xscale=2.8 ⇒ span 18.5cm; constraints chart x-axis 0→5.4 @ 2.2 ⇒ 11.9cm;
  user asked it to fill like the reference → xscale = (6.6×2.8)/5.4 ≈ 3.4,
  measured 25.0cm = 93% of the 26.9cm column (verify with `pdftotext -bbox`
  max xMax of the tick labels, not vision). Same chart type ⇒ same rendered
  width is the expectation.
- **Regression line on a TikZ scatter: compute OLS in Python, draw UNDER the
  dots** (user, 2026-08: "画一根线性回归线（orange色），可能要先计算"): run
  `numpy.linalg.lstsq` on the raw (x,y) pairs before touching the figure,
  print slope/intercept/r², then add ONE `\draw` line BEFORE the `\node[circle,...]`
  dots (dots render on top of it): `\draw[cuhk-orange!70, line width=1.2pt]
  (0,{intercept*sc_y}) -- ({xmax*sc_x},{(slope*xmax+intercept)*sc_y});` —
  endpoints written in the SAME scaled coordinate formulas as the dots
  (sc_x/sc_y are the per-axis scale factors), so the line spans the full
  plot. Example: 32 RICO points, y = 0.83x − 1.49, r² = 0.92.
  **Label the correlation value ON the plot** (user, 2026-08: "线性回归图里标记
  0.96"): one `\node[font=\scriptsize, cuhk-orange!90!black] at (x,y) {r = 0.96};`
  placed in an empty region of the scatter (top-right), same color family as
  the regression line — the reader shouldn't have to infer r from the r² in a
  comment. Keep it near the line it describes.

**User rejected the side-by-side text+figure layout in the end** ("Missed
fraction of GT elements恢复原有的"): after the tabularx fix verified side-by-
side via pdftotext -bbox, the user still asked to revert to the original
VERTICAL layout (itemize paragraph, then `\begin{center}` figure below it).
Don't argue — revert. The tabularx recipe remains in the Pitfalls for when
side-by-side IS wanted.

## Porting poster figures BACK to the report (2026-08, user: "poster中有一个图...我想在report.tex适当位置也插入")

Reverse direction of the porting section above. The poster's VLM-output-vs-After-GNN motivating figure (Recipe App two-panel) was inserted into `report/report.tex` §1.2 (Two Systematic Failure Modes), right after the failure-modes paragraph, with a lead-in sentence citing `Fig.~\ref{fig:motivating}`.

Recipe:
- **Copy the absolute-coordinate tikzpicture verbatim** from `poster/poster.tex` (it spans x=0..20.79, y=0..9.33 with two panels offset by +8.6 in x — the +8.6 offset keeps the right panel aligned with zero effort, reuse it).
- **Wrap in `\resizebox{\textwidth}{!}{...}`** — in the REPORT this is the accepted convention (fig:pipeline already does it); the poster's "no resizebox, no transform shape" rule is poster-specific (A0 text scaling). On A4, resizebox is exactly right.
- **Replace the CUHK theme colors** — the report has no `cuhk-*` definitions: `cuhk-purple` → `violet!80!black`, `fill=cuhk-purple!25` → `fill=violet!12`, `text=cuhk-purple` → `text=violet!70!black`. Standard colors (green!55!black / green!30 / green!45!black, red!75!black, gray!60) carry over unchanged.
- **`$\checkmark$` requires `\usepackage{amssymb}`** — the report preamble already loads amsmath/amssymb/amsfonts, so it compiles; if a fresh doc errors, add amssymb.
- **Placement by content semantics**: the motivating before/after figure belongs where the failure modes are introduced (§1.2), not in the method section — it demonstrates the two error types (misaligned OK box + omitted Share button) the prose just described. Write 2–3 sentences pointing at the figure before it.
- **Verify with the report's engine**: `latexmk -xelatex -interaction=nonstopmode report.tex` (report = xelatex for fontspec/Times New Roman; poster = lualatex). Check exit 0, `pdfinfo ... | grep Pages` (page count may stay flat if the figure fits a gap), and `pdftotext report.pdf - | grep -c 'After GNN'` to confirm the figure rendered.
- **git add from inside the subdir**: after `cd report`, stage with the relative path (`git add report.tex`) — `git add report/report.tex` fails "pathspec did not match".
- xelatex produces `*.xdv` intermediates — add `*.xdv` to .gitignore (global LaTeX artifact block) so the build leaves no untracked noise.

**Provenance of the poster's missed-fraction histogram** (in case the user asks again or the figure needs regenerating): bars 4/12/36/54/94 are hardcoded in `poster/poster.tex` with no generating script committed. The authoritative 200-image source is `experiments/vlm_completion/pipeline_per_image.json` (aggregates match the report exactly: 4789 GT / 2947 VLM / 3663 FN / 1126 TP / 1821 FP); recomputing `fn/n_gt` buckets gives ≈[5,12,35,57,91], which does NOT exactly reproduce the poster values — the generating run is lost. The histogram uses the matching-failure 口径 (≈76.5%), distinct from the abstract's not-detected 38%. Full detail in `repo-documentation` skill → `references/figure-data-provenance.md`.

## Beamer bibliography: keep each citation on one line (2026-08)

References in this template split into author-line / title-line / journal-line
per entry. ROOT CAUSE (verified in `beamerbaselocalstructure.sty` ~line 472):
beamer redefines `\newblock` as a nested state machine — each `\newblock`
switches `bibliography entry author → title → location → note` template AND
emits a 1.5em-high empty box, forcing a line break. `plain.bst` emits 3
`\newblock` per entry, hence the 3-line split.

WORKING FIX (preamble, after `\usetheme` — this is NOT a font-size problem,
do not touch sizes):
```latex
\setbeamertemplate{bibliography entry title}{}
\setbeamertemplate{bibliography entry location}{}
\setbeamertemplate{bibliography entry note}{}
```
Empty templates make the state machine walk through without emitting breaks;
`author` template is left alone so entries render as one continuous block.
Dead ends (do NOT repeat): `\def\beamer@newblock{}` → renders literal
"newblockempty" text; `\renewcommand{\newblock}{...}` → silently overwritten
by beamer's `\@bibitem` per item; per-block `\begingroup\setbeamertemplate`
title overrides → rejected by user.

**"References 部分是空白的" almost always = `.bbl` missing, not a layout bug**
(2026-08): a single `lualatex` pass never produces the bibliography — the
References block then renders as a title with empty space below (and the
space collapses weirdly because beamer reserves nothing). Fix is always the
full chain: `lualatex → bibtex → lualatex → lualatex`. VERIFY with
`pdftotext poster.pdf - | grep -n -i references` or `ls poster.bbl` — do not
trust a vision crop of the bottom-right corner: on a tall poster the
References block can sit well below the fold of a naive crop, making it look
blank when it actually rendered 14 entries fine. Before concluding "blank",
check the text layer first.

**ROOT FIX — track `poster.bbl` in git so references survive rebuilds**
(user: "References又没了 以后避免重新编译之后消失的问题", 2026-08): the
`.bbl` was gitignored (global `*.bbl` rule), so every build-artifact cleanup
deleted it and the next single `lualatex` pass rendered References blank.
Permanent fix: add `!poster/*.bbl` to `.gitignore` (a more-specific pattern
overrides the global `*.bbl` — verify with `git check-ignore -v
poster/poster.bbl` showing the `!` rule) and COMMIT the `.bbl`. Then any
single lualatex pass renders References; bibtex is only needed when
`poster.bib` actually changes. Rule to keep: after editing `poster.bib`, rerun
the full chain AND commit the regenerated `.bbl` so repo and bib stay in sync.
Keep `!poster/*.bbl` INSIDE the poster-specific block of .gitignore (next to
`poster/*.aux` etc.) so the exception reads clearly.

## Pitfalls

- **American spelling + Oxford comma enforced poster-wide** (user, 2026-08:
  "全篇扫一遍，是否全部使用美式拼写和语法，没有的全部改过来"): run ONE Python
  pass over the prose (strip `\` commands and `%` comments, collect words,
  check against a British→American dict like
  {neighbourhood:neighborhood, colour:color, centre:center, organise:organize,
  realise:realize, grey:gray, towards:toward, whilst:while, learnt:learned,
  ...}). Actual find in this poster: `neighbourhood` → `neighborhood` (in the
  Hop-2 prose: "forming its ``spatial neighborhood.''"). Also check Oxford
  comma on three-or-more item lists (regex `, X and Y` without a preceding
  comma) — this poster's lists ("mobile, PC, and web", "coordinate
  correction, violation detection, existence scoring, and ...") all had it.
  Fix the one-off spelling, then confirm the sweep found nothing else;
  don't assume the whole poster is clean because one section was.
- **Stuck on a LaTeX mechanism? Package the problem for an external AI**
  (user-endorsed workflow, 2026-08): when repeated local attempts fail (e.g.
  the node-equal-width problem), write a self-contained problem report —
  environment (Beamer + beamerposter A0 scale=1.0 + LuaLaTeX, packages,
  theme), the exact symptom, what was tried and why it failed, the root cause
  found in source (.sty/beamer macros), and a precise question. The external
  answer (`text width` + `inner sep=0pt` + `\-` hyphenation) solved it in one
  shot. Include the caveat that beamerposter A0 renders `\footnotesize`
  much larger than in normal documents so font-width estimates are unreliable.
- **Side-by-side text+figure inside a block: use `tabularx`, NOT `minipage +
  \hfill`** (2026-08, GPT-sourced fix, user-verified): in the gemini block
  template (block body = `beamercolorbox`), `\begin{minipage}[t]{0.42\linewidth}`
  silently breaks: (a) `\linewidth` is redefined at each nesting level so the
  two minipage widths don't sum to what you think (probe with
  `\typeout{linewidth = \the\linewidth}` at each level — block content width
  vs minipage-internal width differ drastically); (b) whitespace/newline
  between `\end{minipage}` and `\begin{minipage}` becomes a paragraph break →
  the two boxes stack VERTICALLY instead of side by side, or each word gets
  force-broken onto its own line ("End-" "to-" "end" hyphenated) when the
  width is tiny; (c) the outer `\begin{center}` adds glue that fights
  `\hfill`. WORKING RECIPE:
  ```latex
  \begingroup
  \setlength{\tabcolsep}{0pt}
  \begin{tabularx}{\linewidth}{@{} X >{\centering\arraybackslash}X @{}}
  \begin{itemize}
    \item \textbf{...} text ...
  \end{itemize}
  &
  \begin{tikzpicture}[xscale=2, yscale=1]
    ... bars/axis ...
  \end{tikzpicture}
  \end{tabularx}
  \endgroup
  ```
  `@{}` kills the outer padding, `\tabcolsep 0pt` kills the inter-column gap,
  `X` columns split remaining width 50/50. If the user then says "还是上下排"
  or "没有并排", verify with `pdftotext -bbox` word coordinates (see below)
  BEFORE re-rendering — the layout may actually be side-by-side but visually
  gapped; and if the user keeps rejecting it, REVERT to the vertical layout
  (itemize, then `\begin{center}` figure) rather than fighting — the user
  ultimately preferred the original stacked form (2026-08: "Missed fraction
  恢复原有的").
- **Truncated paste from the user → read the file instead of re-asking**
  (2026-08): when the user forwards an external AI's answer and the paste
  arrives truncated (`[[ ... [126 lines] .. ]]` repeated three times — only
  fragments visible), the user then saves the full text to a project file
  (e.g. `tmp/tmp.md`) and the answer is there. Ask ONCE for the file path;
  do not demand re-paste. Also: do not infer the solution from fragments and
  guess-implement — the truncated fragments (`\resizebox{\linewidth}` + a
  `/bin/sh` error) looked like a resizebox suggestion but the real fix was
  `text width`.
- **Patch tool backslash double-escape**: `patch` rewrites `\\\\\\\\` to `\\\\\\\\\\\\\\\\`
  (causes "There's no line here to end"). After any edit touching a line with
  backslashes, verify with `sed -n '<n>'p | od -c`; safest is a Python script
  with `chr(92)` or raw strings doing the replace. Same rule as report/main.tex.
- **Moving a whole block between columns — do it with a LINE-BASED Python
  script, and keep the block INSIDE a column** (user: "proposed
  methodologies放第一栏", 2026-08). Two failed attempts taught the rules:
  (1) `patch` with a multi-hundred-line old/new string double-escapes every
  backslash (`\begin` → `\\begin`) and corrupts the whole block — `git
  checkout poster/poster.tex` and redo. (2) A Python script that spliced the
  block AFTER the left column's `\end{column}` left it floating between
  columns → `Missing \endgroup inserted`, 43 errors, 2-page PDF. Correct
  splice: insert the block between the previous block's `\end{block}` and the
  column's `\end{column}`, then keep `\separatorcolumn` + `\begin{column}{...}`
  for the next column; verify with `grep -n "begin{block}\|end{column}"` that
  every block sits between a column open/close pair. Blocks cannot live
  outside a column in this template.
- **"撑满80%" means 80% of the COLUMN width, not the paper** (user: "你在干什么
  本来是三栏分布 撑满不是让你撑满整个A0纸 是那一栏", 2026-08): when the user
  asks a figure/table to fill 80%, target `0.8 × \colwidth` (A0 3-col:
  \colwidth=0.32×84.1≈26.9cm → ~21.5cm), centered, ~10% whitespace each side —
  NOT 80% of the page. For the pipeline diagram the width ≈ 2×gap + 3×box
  width, gap = 4.4×xscale; node boxes keep natural width (xscale stretches
  coordinates, not text), so pick xscale ≈ 2.15 for 80%. Compute from the
  source coordinates instead of iterating renders (user: "你直接读代码啊，为什么
  要老看来看去的" — read the tikzpicture code and derive the number; one
  compile to verify).
- **Porting report equations to a block** (user: "report里还有一些重要公式
  能不能适当多展示几个", 2026-08): display equations in `equation*`
  (unnumbered, beamer auto-loads amsmath so no preamble needed). If a display
  equation is present, the surrounding prose must NOT also carry the same
  formula inline — user flagged "这一段的公式重复了" when the block intro said
  "trained jointly with $\mathcal{L}=w_c\mathcal{L}_{coord}+...$:" and the
  `equation*` below repeated it. Intro becomes "trained jointly on a weighted
  sum of losses:" and the equation stands alone. The Models block got the two
  GraphSAGE hop equations + the joint-loss equation, placed after the
  four-head itemize.
- **Display equations must have NO blank lines around them — they belong to
  the same paragraph as the surrounding prose** (user, 2026-08: "整行公式上下不
  应有额外段距，名义上它和上下文属于同一段"): a blank line before/after
  `\begin{equation*}` inserts `\parskip` (1ex in this theme's block body),
  so the three Models equations each gained ~1ex of extra spacing above and
  below. Remove the blank lines — prose line, `equation*`, `equation*`,
  prose line, all consecutive. This also applies between consecutive
  `equation*` blocks (no blank line between them).
- **Content belongs to its numbered section; a column is just where it flows**
  (user: "7. End-to-end是在干什么？这不是第六部分的吗 你不要这个头会死吗" then
  "属于第六部分，没让你硬挤到第二栏，你就放第三栏顶部。换句话说，不要擅自排列不同的栏，让它自己适配",
  2026-08): when sections get reorganized across columns, keep the NUMBERED
  identity of each piece. End-to-end results are part of section 6 (Results) —
  do NOT invent a new header "7. End-to-end" for them (and then renumber
  Conclusion to 8). And do NOT hard-squeeze a section's content into the column
  where the rest of its section lives if that column overflows (Overfull vbox
  544pt when all four Results subsections were packed into the middle column).
  User's accepted structure: middle column = 5. Models + 6. Results (training
  ablation, constraint ablation, element completion), right column = **bare**
  End-to-end content at the top (no block header — it visually continues
  section 6) + 7. Conclusion + References. When a section spans two columns,
  the continuation can be bare content in the next column's `\begin{column}`
  (like the standalone VLM figure) — the user prefers that over a fabricated
  numbered header. Section numbers must stay unique and sequential; after any
  column reshuffle, renumber all blocks and verify `grep -n "begin{block}"`.
- **Section titles: "Conclusion" became "Conclusion & Future Work" (user,
  2026-08) and its content gained a Future Work paragraph.** Two preferences:
  (1) the block title uses `\&` (`{7. Conclusion \& Future Work}`); (2) the
  Future Work paragraph is FLOWING PROSE, no colon and no parenthetical list
  after a bold lead-in (user: "不要写冒号，你就直接写一个自然段 自然叙述"). Write
  `\textbf{Future work} includes visual feature fusion with cross-attention,
  which early experiments show improves proposal MSE by 18--22\%, domain
  adaptation to ScreenSpot, and temporal context...` — content copied from
  report/main.tex's Future Work subsection with numbers intact.
- **Baseline skip in beamerposter A0 is NOT TeX's 13.6pt** (2026-08): at
  `size=a0, scale=1.0`, beamerposter redefines every font size command —
  `\normalsize` = 24.88pt font with **30pt baselineskip** (see
  `beamerposter.sty` lines ~241-244: `fontSizeX{24.88} fontSizeY{30}`). A
  preamble `\setlength{\baselineskip}{14pt}` is silently overridden by the
  `\renewcommand{\normalsize}` at frame start — probe with
  `\typeout{BL: \the\baselineskip}` after `\begin{frame}` to see the real
  value (30.0pt). Any "try baselineskip 14pt" request is impossible as stated:
  14pt < 24.88pt font = overlapping lines. If the user wants tighter line
  spacing, offer 26–28pt (≈1.05–1.12×) or edit the `fontSizeY` pairs in
  beamerposter.sty — and say WHY 14pt is physically impossible rather than
 silently "fixing" it to something else.
 - **Global line-spacing tweak for reclaiming vertical space: `\linespread{0.97}`**
 (user, 2026-08: "整个海报的行距-3%"): add `\linespread{0.97}` in the preamble
 right after `\setlength{\baselineskip}{14pt}` to compress ALL prose line
 spacing by 3% poster-wide — one line, no per-block edits. -3% cut the
 persistent `Overfull \vbox` from 136pt to 34pt in one compile. `\linespread`
 is the RIGHT tool for a uniform fractional tweak; it scales every font's
 baselineskip by the factor (0.97 = -3%, 1.0 = default) and survives
 beamerposter's `\normalsize` redefinition (unlike a direct
 `\setlength{\baselineskip}` which beamerposter overrides at frame start —
 see previous pitfall). This is the escape hatch when the user asks for a
 percentage line-spacing change without touching font sizes.
- **All itemize paragraphs: force justify + allow hyphenation — REDEFINE
  `\itemize`, do NOT use `\AtBeginEnvironment`** (user, 2026-08: "dot point
  段落允许连字和两端对齐", confirmed scope = ALL itemize incl. long-text
  entries in blocks 3/5/7, not just the block-4 constraint dots):
  `\AtBeginEnvironment{itemize}{\justifying \hyphenpenalty=300
  \emergencystretch=1em}` DOES NOT WORK — beamer's itemize re-definition
  forces `\raggedright` INSIDE the list (from beamerbaselocalstructure.sty),
  which executes AFTER the etoolbox hook (hook inserts at environment start,
  before the internal `\raggedright`), so the justify is immediately
  overridden. Symptom: `pdftotext -bbox` shows itemize first lines stopping
  short of the right margin (777 vs 787) while plain prose hits 787. A
  hardcoded `\justifying` right after `\begin{itemize}` (before first
  `\item`) DOES work because it lands after the internal `\raggedright`.
  WORKING GLOBAL FIX (GPT-sourced, verified 2026-08): redefine `\itemize`
  with `\justifying` in place of `\raggedright` (copy the full beamer
  `\itemize` definition from beamerbaselocalstructure.sty, change the one
  line `\raggedright` → `\justifying`, wrap in
  `\makeatletter...\makeatother`, put after packages):
  ```latex
  \makeatletter
  \renewcommand{\itemize}[1][]{%
    \beamer@ifempty{#1}{}{\def\beamer@defaultospec{#1}}%
    \ifnum \@itemdepth >2\relax\@toodeep\else
      \advance\@itemdepth\@ne
      \beamer@computepref\@itemdepth%
      \usebeamerfont{itemize/enumerate \beameritemnestingprefix body}%
      \usebeamercolor[fg]{itemize/enumerate \beameritemnestingprefix body}%
      \usebeamertemplate{itemize/enumerate \beameritemnestingprefix body begin}%
      \list
        {\usebeamertemplate{itemize \beameritemnestingprefix item}}
        {\def\makelabel##1{{%
            \hss\llap{{%
              \usebeamerfont*{itemize \beameritemnestingprefix item}%
              \usebeamercolor[fg]{itemize \beameritemnestingprefix item}##1}}%
          }}%
        }%
    \fi%
    \beamer@cramped%
    \justifying%   % replaces the original \raggedright
    \beamer@firstlineitemizeunskip%
  }
  \makeatother
  ```
  Remove the now-useless `\AtBeginEnvironment{itemize}` line. Verify by
  pdftotext -bbox that multi-line items hit the right margin (~787 in the
  left column) on their non-last lines AND that long words hyphenate
  ("alignment" → "align- ment"); short one-line items legitimately end early
  (last-line behavior), don't "fix" those. Do NOT set `\hyphenpenalty=300`
  — it suppresses needed hyphenation and makes lines stop short again; leave
  the default (50). Sweep the whole file for STALE `\hyphenpenalty=300`
 lines left over from earlier experiments (e.g. inside the block-4 tabularx
 `\begingroup` group) and reset them to 50 too — the user checks charts AND
 prose ("允许连字"). This pitfall overrides the earlier
 `\AtBeginEnvironment` note — that version was the pre-GPT wrong answer.
 **Awkward hyphenation in justified prose → replace the phrase with a
 single word, don't fight the penalty** (user, 2026-08: "message pass-ing ->
 xxx messaging"): "message passing" hyphenated as "pass-ing" across a line
 break looked wrong; the user's fix was to write "messaging" (one word,
 no break). When a multi-word phrase keeps hyphenating at an ugly point
 under justify, prefer a synonym that won't break — not more penalty tuning.
- **Bare paragraphs in ANY column (OUTSIDE any block) don't justify — add
  `\justifying` right after `\begin{column}{\colwidth}`** (user, 2026-08:
  "不是说加粗的问题，我在说对齐" — the right column's Element completion /
  End-to-end / "The recovered elements are real" paragraphs were ragged
  right at 2266–2339 while block-wrapped prose hit the 2360 margin; the
  SAME bug later showed up in the MIDDLE column's bare paragraphs at the
  top, "Two alternating hops" / "Element features", before block 5 starts): the
  gemini `block begin` template applies `\justifying` only INSIDE
  `\begin{block}...\end{block}`. Content placed BARE in a column (the
  section-6-continues pattern, see the Content-belongs-to-its-numbered-section
  pitfall) inherits nothing, so multi-line paragraphs render left-aligned
  with a ragged right edge. Fix: one line after the column opens —
  `\justifying` (optionally `\hyphenpenalty=50` for explicit hyphenation).
  Verify with pdftotext -bbox: every non-last line hits the column's right
  margin (left col ~787, right col ~2360). Don't confuse this with the
  itemize case above — this is about PLAIN paragraphs outside blocks, not
  list internals.
- **Moving block content across columns with a Python script — watch for a
  doubled `\end{block}` and unbalanced counts** (2026-08): when extracting a
  section from the END of one block to make a new block, the extracted span
  often INCLUDES the original block's `\end{block}` — then appending a fresh
  `\end{block}` leaves two consecutive ones and the file ends with
  `File ended while scanning use of \beamer@collect@@body` / `Missing
  \endgroup` / 36 errors at `\end{frame}`. Always verify after any block
  splice: `grep -c 'begin{block}'` == `grep -c 'end{block}'` (and same for
  `begin{column}`/`end{column}`), and eyeball the seam with `read_file`.
  Also: when moving a text intro to sit BEFORE a figure, splice it outside the
  figure's `\begin{center}...\end{center}` — dropping it between `\begin{center}`
  and the first tikz node compiles but is structurally wrong.
- **End-to-end table gets moved as a unit with its figure — and "comment out"
  means only the table the user points at** (2026-08): the user said
  "Results部分的表格可以注释掉" and then immediately "端到端不要注释" — the
  constraint-ablation table was redundant (KPI cards carry the same data) but
  the end-to-end table is NOT (TP/FP/FN only exist there). Comment out with
  `% ` on every line (keep the code, don't delete) so it can be restored.
  **FINAL STATE: the end-to-end table WAS commented out too** (user,
  2026-08: "然后把原来的表格注释掉") — but only AFTER a **TP/FP/FN grouped bar
  chart** (same before/after paired-bar style as the P/R/F1 chart: orange
  VLM-only vs purple VLM+GNN, `\sc=0.0015` for counts, axis labeled `Count`)
  was added right below it to carry the same numbers (TP 1126→1232,
  FP 1821→1905, FN 3663→3557). Sequence matters: chart first, table
  commented out only once the numbers live elsewhere.
- **Empty blocks look broken**: with `% TODO` bodies the poster renders as
  titles only with huge white gaps — fine mid-edit, but confirm with the user
  before committing a skeleton.
- **User hates wasted token/time**: when user gives a one-line change request,
  do exactly that change, compile once, verify, commit. Do not run extra
  experiments, do not re-verify unrelated parts (see also memory: 只按指令修改).
- **"跟着我的指令慢慢改" — when the user says STOP, stop all autonomous work**
  (user, 2026-08: "停下所有任务，不要自己改内容，现在跟着我的指令慢慢改，明白了吗"):
  after a "stop" directive the user drives one small change at a time; every
  edit is a single awaited instruction (e.g. "加纵轴" → add the y-axis label
  only; "写成# of screenshots" → rename only). Do NOT batch pending changes,
  do NOT proactively fix the remaining Overfull warnings, do NOT push
  improvements. Confirm understanding once ("明白，你说我照做"), then apply
  each instruction literally and compile-verify before the next one. This
  overrides earlier "ship incrementally" instincts until the user lifts the
  stop.
- **"别瞎检查" — don't loop vision_analyze verification** (user frustration
  signal, 2026-08): after a change, verify via the compile log (`grep -c "^!"`,
  `Overfull`/`Underfull` checks) and one render; do NOT repeatedly screenshot +
  vision_analyze the same region fishing for approval. The user sees real
  problems the vision pass reports as "fine" — when they say something is
  broken, read the source (theme file, .bbl, beamer macros) and fix the
  mechanism, don't run another visual check round.
- **Layout disputes: verify with `pdftotext -bbox` word coordinates, not
  vision** (user, 2026-08: "不要再用vision了，直接问我" then "你遇到这种问题难道不是
  应该逐级检查代码吗？模版都在那里啊"): when the user claims two elements are
  not side-by-side / misaligned / overlapping, get ground truth from the PDF
  text layer:
  `pdftotext -bbox poster.pdf /tmp/b.xml`, then regex the `<word xMin= yMin=
  xMax= yMax=>` entries and print x/y ranges for the keywords. Same-y-band +
  left/right x proves side-by-side objectively; y-diff ≈ one baseline (30pt
  at A0) reveals a top-alignment offset. This catches layout truth that
  vision misreports, and it's exactly what the user wants: read the code/
  coordinates level by level (block template in `beamerthemegemini.sty`,
  `\linewidth` semantics) instead of screenshot-cycling. Pixel-mask passes
  are a fallback only when the element has no text (e.g. bar fills); one
  scripted pass, then move on.
- **Match paragraph→list spacing by MEASURING the gap in pt, then add a
  `\vspace`** (user, 2026-08: "mistakes:Element omission:之间的行距就很好，应用
  到within a tolerance.ALIGN_LEFT之间"): when the user says one
  paragraph-to-itemize gap looks right and another is too big, get both gaps
  from `pdftotext -bbox` (first word's yMin minus previous line's yMax) and
  add the exact negative `\vspace{-Npt}` before the list — e.g. Intro's
  "mistakes:"→"Element omission:" measured 31pt vs block 4's
  "tolerance."→"ALIGN_LEFT:" 37pt, fixed with `\vspace{-6pt}` before
  `\begingroup`. Re-measure once to confirm 31pt.
- **Measure from the .tex source, not from screenshots** (user: "你直接读代码啊，
  为什么要老看来看去的", 2026-08): for geometry questions (width %, gaps,
  overlaps) compute from the tikzpicture coordinates + known scale factors and
  verify with ONE compile + `pdftotext`/grep — not by repeated `pdftoppm` +
  pixel scans or vision crops. When pixel measurement IS unavoidable (e.g.
  checking the pipeline really spans ~80%), do one scripted pass (150dpi: 1cm
  ≈ 59px; label connected color components) and move on — don't iterate
  renders.
- **Do NOT bulk-edit the poster with Python find-replace scripts — read the
  file and patch surgically** (user: "放屁吧 你总是改不掉用脚本改东西的习惯
  你自己读一下代码明明可以发现很多问题 文字大小基本都乱套了 对齐也是乱七八糟的",
  reiterated 2026-08: "你总是改不掉用脚本改东西的习惯"). Session failures from
  script-based edits: font-size regexes chained (tiny→scriptsize→footnotesize→small)
  double-bumping fonts; `fill=blue!60` replacement silently missed all
  `\fill[blue!60]` bracket-syntax occurrences (zero matches); reverting the bump
  then wrongly downgraded the pipeline's original `font=\small` to `\footnotesize`;
  and the resizebox width "fix" kept the double-scaling root cause. For
  multi-line TikZ figures, open the block, read each figure's styles/nodes, and
  patch per-figure. Scripts are only acceptable for the mechanical
  backslash-unescape fix (chr(92) replace), never for styling/format adaptation.
- **Python `%`-format collides with LaTeX `%` comments in edit scripts**
  (2026-08): when building a replacement string with
  `"..." % (xs, ys)`, a LaTeX comment line inside the string (e.g.
  `% 5 seeds per training objective`) makes `%`-formatting raise
  `TypeError: not enough arguments for format string` — the `% 5` parses as
  a format spec. Fix: plain string concatenation (`"\\begin{tikzpicture}[xscale=" + xs + ...]`)
  or f-strings; never `%`-format a string that contains `%`. Same trap bit
  twice (plots_bigger.py, plots_150.py).
- **Anchor uniqueness in mechanical replaces: same block appears TWICE**
  (2026-08): the dual-panel chart's category-label block and the `% axis`
  header both occur once per panel (2×). A `src.count(old) == 1` assertion
  fails on the second occurrence. Use a LONGER anchor that includes the
  distinguishing line (e.g. the x-axis extent `-- (6.6,-0.65)` for the
  violation chart vs `-- (5.4,-0.65)` for the constraints chart), or assert
  `== 2` and let `str.replace` handle both.
- **TikZ node line breaks need `align=center` in the style**: `\\` inside a
  node body errors as `LaTeX Error: Not allowed in LR mode` / `Missing }
  inserted` unless the node style (or the node itself) declares
  `align=center`. Every style that contains `\\` text — `box`, `lab`, `elem`,
  `cons` — must set it. When porting report figures, check each new style.
- `\texttt{ALIGN\_LEFT}` etc. keep the underscore escaped in texttt.
- After `git clone`, remove `tmp/CUHK-Poster-Template/.git` if copying into a
  gitignored tmp dir.

## Related

- `internship-report` skill: report writing format requirements, citation
  standards, and the poster presentation milestone (requirements side).
- `latex-debugging` skill: TikZ figure layout pitfalls.
