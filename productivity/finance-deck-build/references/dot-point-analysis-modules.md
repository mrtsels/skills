# Dot-point analysis modules (`\dbullet`) — recipe & worked conversions

Deck: `tasks/task-5/task5_rates_deck_mtheme.tex` (27-page Beamer rates deck).
User rule (Aug-2026): prose paragraphs inside `analysis` / `card` bodies read as
text walls — "用dot point领段" (lead paragraphs with dot points). Convert every
multi-clause paragraph to one `\dbullet{…}` per point.

## The settled macro (preamble, after the `analysis` env)

```latex
% bullet lead-in for analysis body: teal dot in a fixed-width box so
% wrapped lines hang-indent flush under the text; tight uniform leading
\newcommand{\dbullet}[1]{%
  \par\noindent\hangindent=1.2em\hangafter=1
  \setlength{\baselineskip}{11pt}%
  \makebox[1.2em][l]{{\color{teal}\textbullet}}#1\par\vspace{1pt}}
```

Three user corrections shaped it, in order:
1. **"使用悬挂缩进，文本左对齐"** (hanging indent, text left-aligned) — the naive
   `{\color{teal}\textbullet}\ #1\\[2pt]` wraps back to the LEFT EDGE under the
   dot. Fix: `\hangindent=1.2em\hangafter=1` + the dot in a fixed-width
   `\makebox[1.2em][l]` — wrapped lines then align flush under the text, not
   under the dot. Both values must match (1.2em) or the wrap column drifts.
2. **"统一缩窄行距，dot point"** (unify + narrow the leading) — each bullet is its
   OWN paragraph, so it also needs an explicit `\setlength{\baselineskip}{11pt}`
   (Beamer's default 12pt at 10pt font) and `\vspace{1pt}` between items
   (was 2pt).
3. **"XXX: xxx" single-word labels** (below).

## Single-word bold labels for spec rows

User: "What it does和Use case各自用一个词替代，然后用dot point，XXX: xxx替换".
`\kv{Label}{Text}` rows (label column + text column) convert to
`\dbullet{\textbf{Word:} text}` — the label is ONE word, bold, inline.

- S7 Instrument landscape: `\kv{What it does}{…}` → `\dbullet{\textbf{Role:} …}`,
  `\kv{Use case}{…}` → `\dbullet{\textbf{Use:} …}` (4 modules × 2 rows).
- S5 EFFR/SOFR cards: `\kv{Type}{…}` / `\kv{Size}{…}` / `\kv{Role}{…}` →
  `\dbullet{\textbf{Type:} …}` etc. (labels were already single words).
- The user then swept EVERY remaining `\kv` page in one sitting ("S11 -> dot
  point", "S15 inside deck -> dot point"), so the whole deck ended uniform:
  S9 Convention/What-it-means/Strip/Convexity, S11 Initial-maintenance /
  How-CME-sizes-it / Waterfall / Extras, S15 Source/Role cards, S25 recap
  Benchmarks/Toolkit/View/Expression. **The deck now has ZERO `\kv` usages
  left** — earlier note "\kv survives for other pages (e.g. S11)" is
  SUPERSEDED; multi-word phrase labels (How CME sizes it, Waterfall (loss
  absorption)) are kept VERBATIM as the bold inline label, only shortened if
  they wrap. When the user names pages one by one for the same conversion,
  scan the whole deck and convert ALL remaining instances in one pass.
- **Tables: `\dbullet` works inside tabularx cells** (S16 comparison table,
  3×3 grid of Unique-to-SR3 / Shared / Unique-to-F3M cells) — the `\par`
  + `\hangindent` operate fine inside a `p{}`/`X` cell; header row stays
  plain `\bfseries` navy, data cells each get one dot point.

## Grouped rows: NO-DOT teal header + dotted rows (`\dhead`)

User (S11): "S11 e.g.: [green] Initial / maintenance · IM xxx · Maintenance
xxx · Below maintenance" — a labelled row whose VALUE is itself a short list
decomposes one level deeper, instead of one long flat `label: a; b; c` bullet.

**First attempt FAILED (user rejected it):** `\dsub` — a dotted header bullet
(`\dbullet{\textbf{\color{teal}Header}}`) + indented `·` middle-dot sub-rows.
User: "你没有严格遵循，我说的是Initial不需要dot，下一级用dot，参考第七页" — the
header carries NO dot (like an S7 `analysis` header); the rows below carry the
dots. `\dsub` was DELETED from the preamble.

Settled pattern (S11):

```latex
% group header inside a body: teal bold line WITHOUT a dot, rows below it
% carry the dots (analysis-header style, see S7)
\newcommand{\dhead}[1]{%
  \par\noindent{\bfseries\color{teal}#1}\par\nobreak\vspace{1pt}}
```

```latex
\dhead{Initial / maintenance}
\dbullet{IM (collateral to open) $\approx$ \textbf{\$300--600}}
\dbullet{Maintenance $\approx$ \$270--550}
\dbullet{Below maintenance $\to$ margin call back to initial}
```

- S11 left: `Initial / maintenance` header + 3 `\dbullet` rows; `How CME sizes
  it` header + 2 rows (SPAN/STACER: 99%+ VaR over ~2-day liquidation horizon /
  Recalibrated daily). **Double-colon trap**: the original flat bullet
  "How CME sizes it: SPAN/STACER: 99%+ VaR …" had two colons and got flagged
  ("这个怎么回事") — header + rows is the fix.
- S11 right: `Waterfall (loss absorption)` header + 1 row (VM → members'
  default fund → CCP capital); `Extras` header + 3 rows.
- Convert EVERY group on the page to header+rows in one pass — a flat
  "Label: content" row sitting beside grouped rows reads inconsistent.
- Rule of thumb: header + rows when the value enumerates ≥2 parallel items
  (or is a 2-line formula); flat `label: value` only when it's one short
  clause.

## Prose CALLOUTS convert too (S9)

The one remaining prose paragraph was a `\callout{Worked example: buy 10 SR3
Dec-26 at 95.96; final settle 96.20 → P&L = …}` — the user's whole-deck sweep
("S9 -> dot point") converts it the same way: `\begin{analysis}{Worked
example}` + 3 bullets (Buy 10 SR3 Dec-26 at 95.96 / Final settle 96.20 /
P&L = (96.20−95.96)×100×$25×10 = **+$6,000**). Same pass: trim any takeaway
longer than ~79 chars at 10pt (S9's ~90-char takeaway threw `Overfull \hbox
(22.9pt too wide)`; "Mar-27 SR3 ~4.12% vs SOFR 3.65% ≈ 50bp of hikes by
mid-2027" at ~65 chars cleared it).

## User-named column ratio overrides the width tokens

The deck's width tokens (`\cwq/\cwt/\cwh/\cwm/\cws`) are "the only widths any
slide may use" — but when the user names an explicit ratio (S4: "左栏2/3,
右栏1/3"), raw `\textwidth` fractions win: `\begin{column}{0.66\textwidth}` +
`\begin{column}{0.31\textwidth}` (0.97 + columnsep 0.35cm ≈ \textwidth).
Stacking four modules in the wide column adds height — S4 needed a local
`\vspace{-3pt}` before the takeawaybar to clear a 2.7pt `Overfull \vbox`.

## Prose paragraphs converted this pass (before → after)

| Page | Before (prose) | After (dot points) |
|---|---|---|
| S4 Definition | "Transactions-based. Median of tri-party, GCF, and bilateral Treasury repo rates: actual trades, no bank quotes." | • Transactions-based: median of tri-party, GCF and bilateral repo<br>• Actual trades, no bank quotes |
| S4 Why it won | "Post-LIBOR. Manipulation-resistant; chosen by ARRC…" | • Post-LIBOR, manipulation-resistant<br>• Chosen by ARRC after LIBOR retired<br>• Reference for derivatives, loans, ARMs since 6/30/23 |
| S4 Repo collateral | "Treasury-backed overnight loans: the safest collateral, the deepest market." | • Treasury-backed overnight loans<br>• Safest collateral, deepest market |
| S4 Institutional role | "Benchmark of the USD derivative complex." | • Benchmark of the USD derivative complex (single bullet OK) |
| S10 Daily variation margin | "CCP marks to market each day, cash P&L exchanged: credit risk never exceeds one day." | • CCP marks to market daily, cash P&L exchanged<br>• Credit risk never exceeds one day |
| S10 Final settlement formula | "R = …; final cash flow = …" | • `R = \big(\prod_i (1+SOFR_i\cdot n_i/360)-1\big)\times 360/D`<br>• Final cash flow = (final price − last settle) × $2,500 |
| S23 Position management | 3-clause run-on | • SR3 P&L linear → options add convexity, tails, vega<br>• SR1 serials + SR3 trade the Fed meeting-by-meeting<br>• Disinflation → receivers + flatteners (compressed, see below) |
| S25 Data | "Monthly CPI & payrolls (July CPI ~mid-Aug); energy prices (geopolitics)." | • Monthly CPI & payrolls (July CPI ~mid-Aug)<br>• Energy prices (geopolitics) |
| S25 Watchlist | "Term-premium proxies (auction tails, 5y5y); SOFR−EFFR and EURIBOR−€STR spreads; repo funding at month-ends." | • Term-premium proxies: auction tails, 5y5y<br>• SOFR−EFFR and EURIBOR−€STR spreads<br>• Repo funding at month-ends |

Split on the punctuation that already carries the logic: sentence boundaries
(`.` / `:`) and semicolon-separated clauses. Never invent new content — re-word
for brevity only.

## Height trap: prose → bullets ADDS vertical space

Each bullet = one paragraph = `baselineskip 11pt` + trailing `\vspace{1pt}`.
Prose of 3 lines at 12pt = 36pt; 3 bullets of 4 wrapped lines = 4×11 + 3×1 =
47pt → ~11pt taller. S23 (Options page) overflowed 9.76pt right after the
conversion: `Overfull \vbox (9.75914pt too high) detected at line 950`.

Recovery lever, in order:
1. Compress the longest bullet to ONE line. In a `\cwh` half column at 10pt
   Times, a line fits ≤ ~40 chars. S23's third bullet:
   "If disinflation resumes, flip to receivers and front-end flatteners; the
   DV01 budget is fixed either way" (2 lines, ~115 chars)
   → "Disinflation $\to$ receivers + flatteners" (1 line, 36 chars).
   Dropping filler ("if … resumes", "front-end", the DV01 clause — that concept
   is already on the S22 title and the takeaway) is sanctioned; keep the
   scenario→action skeleton.
2. Next: shorten the module's other bullets, then the takeaway to one line.

## Bonus effect (whole-deck win)

`\baselineskip 11pt` is tighter than Beamer's default 12pt, so converting
`\kv`/prose rows can also WIPE pre-existing small overfulls: S5's lingering
13.08pt overfull (present since before this pass) vanished when its cards went
`\dbullet`, and the deck reached **0 overfull across all 27 pages**.
Verification: `grep 'Overfull \\vbox' build.log` → empty.

## Verification loop (per changed page)

```bash
xelatex -interaction=nonstopmode deck.tex >/tmp/b1.log 2>&1   # ×2 for refs
grep -c '^!' /tmp/b2.log          # 0 = no errors
grep 'Overfull \\vbox' /tmp/b2.log
pdftoppm -png -r 110 -f N -l N deck.pdf /tmp/pN && vision_analyze /tmp/pN-0N.png
```

Ask vision targeted questions: dots visible & aligned, wrapped lines hang
under TEXT (not the dot), no clipping/overflow, modules clear of the takeaway
bar. Note: the "Position management" module lives on the OPTIONS page
(S23 in the final deck, title "Options cap the tail…"), not on the page whose
title mentions positioning — count frames, don't guess from titles.

**User's slide NUMBER may not match the content they name** (real case: "S5 ->
两栏. 左栏2/3: Definition, Why it won, Repo collateral, Institutional role…"
— those modules live on the SOFR page, frame 4, while frame 5 is "EFFR and
SOFR track…"). When the number and the named content disagree, locate the page
by CONTENT (grep the module headers / first line of the frame), patch there,
and say in your summary which frame you actually changed — don't ask the user
to disambiguate, don't guess by counting.
