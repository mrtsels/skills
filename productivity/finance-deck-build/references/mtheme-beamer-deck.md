# Porting a finance deck to stock Metropolis (mtheme)

User request pattern: "把现有的tex只采纳内容，移植到mtheme模版" — take the CONTENT
of an existing Beamer deck verbatim and re-render it with the stock Metropolis
(mtheme) template: dark-teal frametitle + amber accent, native `\maketitle`,
`\section` page dividers, `block`/`alertblock` containers, plain `\textbullet`
bullets. Companion to `beamer-latex-deck.md` (the tcolorbox/custom-palette
variant); this file is the mtheme-specific pitfall bank from a full 30-frame
port. All items below cost real debugging time.

## Preamble that works (xelatex ×2, verified at 10pt)

**User-verified size rule: base font stays 10pt.** An earlier pass shipped the
deck at 9pt to make everything fit; the user rejected it outright
("标题正文的字号也要改啊 现在太离谱了" — the sizes were absurd). Accepted sizes:
10pt body, mtheme's DEFAULT frametitle `\Large` (~17.28pt at 10pt) — do NOT
override the frametitle size upward (19pt made long storyline titles wrap to 2
lines and cost ~23pt per frame), do NOT drop the base font. Compress LAYOUT,
never the font.

```latex
\documentclass[aspectratio=169,10pt]{beamer}
\usepackage{fontspec}
\setmainfont{Anthropic Sans}
\setsansfont{Anthropic Sans}
\setmonofont{Anthropic Sans}
\usepackage{amsmath, amssymb, mathtools}
\usepackage{graphicx}
\usepackage{booktabs, tabularx, array, ragged2e}
\usepackage[shortlabels]{enumitem}

\usetheme{metropolis}
\metroset{
  numbering=fraction,
  progressbar=frametitle,
  sectionpage=progressbar,
  block=fill,          % NOT blockbg — see pitfall 1
}

% content helpers (names that do NOT collide with beamer)
\setlength{\medskipamount}{0.5pt}          % tighten block-to-block spacing
\makeatletter
\setlength{\metropolis@blocksep}{0.1ex}    % tighten block padding
\setlength{\metropolis@blockadjust}{0.05ex}
\setlength{\metropolis@frametitle@padding}{1.0ex} % slimmer title bar (2.2ex default)
\makeatother
\newcommand{\fnote}[1]{{\footnotesize\color{black!55}#1}}  % NOT \note — pitfall 2
\newcommand{\src}[1]{\vspace{1pt}{\scriptsize\color{black!55}#1}\par}
```

Cover → `\title/\subtitle/\author/\institute/\date + \maketitle`; part
dividers → `\section{<storyline sentence>}` (auto section page, noframenumbering);
cards → `\begin{block}{Title}` / `\begin{alertblock}{...}` for worked examples;
stat chips → small blocks with `\centering{\Large\bfseries <number>}` + `\fnote`.

## Pitfalls (each one broke the build or the layout)

1. **`blockbg` metroset alias does not exist in some mtheme versions**
   (`pgfkeys Error: I do not know the key '/metropolis/inner/block'`), then a
   cascading "TeX capacity exceeded". Use `\metroset{block=fill}` — the
   `color/block` choice key is what actually fills block bodies.
2. **`\note` is already defined by beamer** (LaTeX Error: Command \note already
   defined). Name the small-text helper anything else (`\fnote`, `\sml`).
3. **enumitem `enumerate` WITHOUT an explicit `label=` infinite-loops under
   beamer**: `! TeX capacity exceeded ... \labelenumi ->{\labelenumi}` at the
   `\end{frame}`. The original deck's enumerate had `label={...}` so it worked;
   a bare `\begin{enumerate}[itemsep=...,leftmargin=...]` recurses. Fix: always
   pass `label=\arabic*.` (or any explicit label). `itemize` is unaffected.
4. **Theme-internal lengths need `\makeatletter`** in the document preamble:
   `\setlength{\metropolis@blocksep}{...}` without it parses as `\metropolis` +
   `@blocksep` → "Undefined control sequence" + a cascade of "Missing number /
   Illegal unit" errors that corrupt the whole build. Wrap in
   `\makeatletter ... \makeatother`. The lengths ARE overridable after
   `\usetheme{metropolis}` (they're plain `\newlength` in the inner theme).
5. **`columns[t]` vs `columns[T]` — the ~55pt silent misalignment.** In frames
   mixing a chart/box column with an itemize column, `[t]` (box-top align) can
   drop the itemize ~2–3 lines (≈55pt) below where it should start, pushing
   content off the bottom while the chart column stays high. `[T]` (first-line
   baseline align) fixes it and moved the bullets up 60pt on the worst frame.
   Use `[T]` everywhere on mixed chart+list columns (the original deck did).
6. **`\geometry{top=...,bottom=...}` in beamer shifts ALL content DOWN by
   exactly the margin value** (beamer's own layout overrides the geometry
   intent) — verified as a uniform +22.7pt downward shift with `top=0.8cm`.
   Do not use geometry to reclaim vertical space; use the fit levers below.
7. **Fira fonts absent**: mtheme warns "Could not find Fira Sans/Mono fonts" but
   builds fine with fontspec fonts; `\bfseries` on the installed Anthropic
   *variable* fonts warns "Font shape .../b/n undefined" and substitutes the
   regular weight — same behaviour as the tcolorbox variant, cosmetic only.
8. **Title page emits an invisible `Overfull \vbox` (~13pt)**: the mtheme
   `\maketitle` template's internal vbox; renders fine, nothing clipped — don't
   chase it.
9. **Overriding the frametitle size upward backfires.** `\setbeamerfont
   {frametitle}{size=\fontsize{19}{23},...}` pushed already-long storyline
   titles onto a second line, costing ~23pt of content space on every wrapped
   frame — worse than the size gain. Keep mtheme's default `\Large`.
10. **`p{}` tables WITHOUT `\scriptsize` are the hidden tall-element.** Two
    strategy tables kept at default size (cells wrap to 2–3 lines) measured
    ~41pt per row — each table alone consumed the whole frame budget. Every
    dense table in a 16:9 deck needs explicit `\scriptsize` + `arraystretch
    1.0` (see lever 3).

## Fit levers at 10pt (measured impact, apply in this order)

The dense finance content (3-block columns, 4–5-col tables, chart+5-bullet
frames) does NOT fit Beamer 16:9 at 10pt without compression. The original
tcolorbox deck overflowed 22 of 27 pages (up to 24pt below the page edge).
Levers that actually work at 10pt, in order of measured gain:

1. **`columns[T]`** — biggest single win on chart+itemize frames (≈60pt).
   Mixed chart/box + itemize columns are the frames that overflow first.
2. **`\metropolis@frametitle@padding` 2.2ex → 1.0ex** (inside `\makeatletter`)
   — slimmer title bar reclaims ~10pt on EVERY frame (the bar's padding is
   2.2ex above AND below the title text).
3. **Tables: `\renewcommand{\arraystretch}{1.0}` AND an explicit `\scriptsize`
   on EVERY dense table.** Wrapped `p{}`-column cells make rows huge: default
   (10pt) cells measured ~41pt per row; even `\scriptsize` + `arraystretch
   1.28` was ~41pt. Missing `\scriptsize` on just two strategy tables cost
   ~35pt each and they were the last frames to overflow.
4. **Block padding**: `\metropolis@blocksep 0.1ex` + `\medskipamount 0.5pt`
   (~5–6pt per block). Keep `blockadjust 0.05ex` so `blocksep−blockadjust` is
   non-negative.
5. **`\footnotesize` on the block bodies of the 3 densest frames** (pricing /
   margin / risk 3-block columns) and on frame-level bullets of chart+bullets
   frames (≈10–20pt each). `\small` on those same bodies is NOT enough.
6. **Source lines: place them where they are FREE.** A `\src` row below the
   columns costs a full extra row (columns must end ~20pt earlier). Options:
   (a) full-width below the columns IF the tall column ends ≤ limit−20pt;
   (b) inside the SHORTER column — a 2-line `\scriptsize` src in a narrow
   0.37 col wraps to 5 lines (~50pt, worse), so keep src full-width and shrink
   the tall column instead; (c) as a `\tiny` line under a short column only as
   a last resort. NEVER leave it full-width below an already-tall frame.
7. **Spacing hygiene**: inter-block `\vspace{2pt}`→1pt, itemize
   `itemsep=0–1pt`, `topsep/parsep=0`, alertblock `itemsep` 4→2pt.
8. **Split a frame only if the page budget allows** (20–30-page cap): the
   settlement frame's formula block moved to its own full-width frame.
   Re-ordering content (formula banner below the columns instead of on top,
   formula line into the worked-example column) is acceptable; inventing NEW
   content is not (see rule below).

Not usable: `\geometry{top=...,bottom=...}` (shifts everything down — pitfall
6), base font < 10pt (user-rejected), frametitle size > default `\Large`
(makes long titles wrap → −23pt/frame).

## Fit QA: measure with the text layer, never trust vision or stale images

- **THE trap that misled twice**: a filter like "ignore spans with
  `y > page_height − 18`" (meant to skip the footline) ALSO hides real
  off-page text — builds looked clean while 7 frames had text at y 250–292 on a
  255pt page (the worst was fully clipped). Exclude ONLY the framenumber zone:
  `if y0 > 228 and x0 > 400: continue` (bottom-right corner), then flag any
  span bottom > content-area limit (~226.5pt on 16:9).
- **Vision at contact-sheet (60dpi) resolution is noisy** — it returns generic
  "text cut off / misaligned" boilerplate for dense tables. Use text-layer
  measurements for fit, then 110dpi+ targeted vision on the worst pages for the
  final look (look for framenumber collisions: text ending within ~10pt above
  y≈235 on the right side).
- **Existing QA screenshots go stale** — the repo's `qa_tex/` images were from
  an older build; the current original PDF overflowed 22/27 pages. Always
  re-measure the CURRENT build.
- Also verify no horizontal overflow: `span.bbox.x1 > page_width − 3` catches
  tables spilling off the right edge.
- Goal state: every content frame bottom ≤ content-area limit; a 2pt intrusion
  into the 28.5pt bottom margin is invisible and acceptable (glyphs still
  ~20pt above the page edge, no footline collision).

## Content-only port rule (user preference — enforced)

"只采纳内容" means the port carries content VERBATIM and adds ZERO invented
content. Adding an explanatory "Compounding vs simple" block that was not in
the original got reverted immediately. Allowed: restructuring layout
(blocks ↔ plain lines, moving elements between frames), fixing an obvious
duplication bug in the source (S6 had the same two bullets twice — keep once
and flag it), mechanical tightening. Not allowed: new sentences, new
examples, new sections. Every word of text/numbers/tables/source lines must
trace to the original file.
