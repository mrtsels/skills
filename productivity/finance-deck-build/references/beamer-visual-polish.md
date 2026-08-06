# Beamer (mtheme) pure-rendering cleanup pass — verified recipe

Context: user hands a "visual polish only" spec (no content/wording/storyline/
order/chart/conclusion changes) with a 12-point checklist. This file is the
verified implementation from the Aug-2026 Fed Funds & SOFR deck pass
(23 pages, 0 errors, 0 overflow pages, 0 underfull, 3 sub-millimetre overfulls
remaining and accepted). Distilled so a future pass starts from the working
system instead of rediscovering it.

## 1. Global style system (route everything through it)

```latex
% typography scale
\newcommand{\decktitle}[1]{#1}                        % headline text; styling via frametitle template
\newcommand{\keylabel}[1]{{\bfseries\color{teal}#1}}  % module header, 10pt bold teal
\newcommand{\decktext}[1]{{\small #1}}                % secondary body, 9pt
\newcommand{\decklabel}[1]{{\footnotesize\color{steel}#1}} % small grey label, 8pt
\newcommand{\decknote}[1]{{\footnotesize #1}}         % small note, 8pt
\newcommand{\decknum}[1]{{\large\bfseries\color{navy}#1}}    % primary number, 14.4pt navy
\newcommand{\deckaccent}[1]{{\large\bfseries\color{teal}#1}} % accent number, 14.4pt teal
\newcommand{\deckcover}[3]{{\LARGE\bfseries\color{navy}#1}\\[14pt]{\large\color{steel}#2}\\[22pt]{\small\color{steel}#3}}

% spacing rhythm — fixed steps, no arbitrary values
\newcommand{\vcard}{\vspace{6pt}}    % card-to-card
\newcommand{\vblock}{\vspace{8pt}}   % block-to-block
\newcommand{\vthin}{\vspace{2pt}}    % micro adjustment

\setlength{\parindent}{0pt}                 % REQUIRED: 15pt indent before a row of
                                            % minipages wraps the last card to a new line
\setlength{\emergencystretch}{1.5em}        % relax tight paragraphs
\newcommand{\sourcesline}[1]{{\fontsize{7}{8.4}\selectfont\color{steel}Source: #1}\par}
```

Component macros (all minipages that fill their column via `\linewidth`):
`\kpicard{label}{value}{note}` (teal rule + 8pt label + 14.4pt number + 8pt note),
`\tradecard{name}{view}{catalyst}{payoff}{risk}` (fields VIEW/CATALYST/PAYOFF/RISK),
`\instcard{name}{role}{line}`, `\scenariobox{width}{name}{prob}{path}{trade}`,
`\takeawaybar{tag}{text}` (bottom hairline + amber tag + 9pt text),
`\callout{text}` (light band). All card minipages start with `\raggedright`.

Then bulk-replace frame-level `\small`/`\footnotesize`/`\Large`/`\LARGE`/
`\vspace{Npt}` with the macros. Wrap every frame title in `\decktitle{…}`
(`\begin{frame}{\decktitle{...}}`) — all titles then share one template.

## 2. Table/column fixes (each cost real time)

- **`>{\raggedright\arraybackslash}p{...}` on every column** — kills Underfull
  hbox (badness 4000–10000) from justification stretching short cells.
- **`@{}p{a} p{b}@{}` column sums must be ≤ ~0.96, not 1.00** — each
  inter-column gap carries `\tabcolsep` (12pt for two columns), so p-columns
  summing to 1.00\textwidth overflow by exactly ~12pt (`Overfull \hbox
  (11.99998pt too wide)`).
- **Unbroken URLs in p{} cells overflow silently** (real case:
  `newyorkfed.org/markets/reference-rates` = 142.7pt in a 139pt column →
  3.7pt overfull, invisible). Fix: `\allowbreak` after slashes
  (`newyorkfed.org/\allowbreak markets/\allowbreak reference-rates`) — display
  unchanged, breaks only when needed. Widening the column trades one overflow
  for a taller table.
- **Inside `columns`, `\textwidth` = the COLUMN width** (beamer resets it).
  Tabular p-columns inside a column must use `\linewidth`, not `\textwidth`,
  or cells wrap 2–4× more than intended.
- Two tables side by side in one frame: fine at 0.52/0.44\textwidth columns.

## 3. Beamer/mtheme gotchas hit this pass

- `\hrule` followed by `\\[Npt]` → error "There's no line here to end". Use
  `\rule{\linewidth}{0.7pt}` (a real box) instead.
- Full-bleed hairline under the frametitle without an overfull warning:
  `\noindent\rlap{\hspace*{-0.85cm}\color{teal}\rule{\paperwidth}{0.7pt}}\par`
  (rlap = zero-width box; `\rule{\paperwidth}` alone reports +48.37pt overfull
  on every frame — cosmetic but noisy).
- Never `\scriptsize` in body text (~5pt, unreadable) — `\footnotesize` (8pt)
  is the floor; sources 7pt via `\sourcesline`.
- Body/base font: 10pt (user rejects 9pt base — compress layout instead).
- KPI value size: `\large` (14.4pt) not `\Large` (17.3pt) — fits three stacked
  cards beside a chart; stack spacing `\vthin` (2pt) when the page has a
  takeaway bar, else the frame overflows by ~6–12pt (vbox too high).
- Takeaway bar (`\vfill` + hairline + tag + text) absorbs leftover space — a
  frame with 3 KPI cards + chart + takeaway + sources needs cards tightened.

## 4. xelatex HANG diagnosis (no error, just never finishes)

Bisect: write `/tmp/seg.tex` = preamble + one frame subset + `\end{document}`;
compile (≈0.7s each) and shrink until the hanging frame/macro is found.
Two self-inflicted hang causes seen:

1. **Bulk regex rewriting macro DEFINITION lines.** A global
   `\vspace{6pt|8pt|2pt} → \vcard|\vblock|\vthin` replacement also hit the
   definition lines, producing `\newcommand{\vblock}{\vblock}` — infinite
   self-recursion → hang. After ANY bulk regex: `grep -n 'newcommand' file` and
   verify definitions still contain their bodies.
2. **execute_code `read_file` → `write_file` round-trip truncation.**
   `hermes_tools.read_file` returned only the first ~490 lines; the write
   silently dropped the appendix frames AND `\end{document}`. After any
   full-file rewrite: confirm `\end{document}` exists and line count is sane.
   Prefer `patch` (replace mode) for edits; for full rewrites, read the file in
   chunks or verify integrity immediately after.

macOS traps that fake hangs:
- `timeout` does not exist (exit 127, looks like a crash/hang) — use
  `gtimeout` (coreutils) or a subprocess timeout in Python.
- `pkill -f xelatex` matches its OWN shell command line (contains "xelatex")
  and kills the shell — use `pkill -x xelatex` (exact process name).

## 5. Acceptance numbers from the verified pass

XeLaTeX ×2 → 23 pages, 0 errors, 0 overflow pages (fitz measurement: every
page's text bottom ≤232pt on a 255pt page), 0 underfull, Overfull 30 → 3
(all < 8pt: one environment artifact that doesn't reproduce when the frame is
compiled alone, one 3.6pt vbox, one 3.7pt URL — accepted as invisible).
`\footnotesize` stays ONLY inside appendix tables; main-page body is 10pt.

## 6. Second pass (Aug-2026): 14pt bold top-aligned titles + variable-font bold

User then iterated the headline: 8pt → 18pt → **14pt bold** (`\setbeamerfont{frametitle}{size={\fontsize{14}{16}\selectfont},series=\bfseries}`).
18pt pushed takeaway pages into real overflow (sources 243→262pt); 14pt balances.

### Working frametitle template (top-aligned)

```latex
\setbeamertemplate{frametitle}{%
  \nointerlineskip
  \parbox[t]{\dimexpr\paperwidth-1.7cm\relax}{\usebeamerfont{frametitle}\bfseries\insertframetitle}\par
  \vspace{4pt}%
  \noindent\rlap{\hspace*{-0.85cm}\color{teal}\rule{\paperwidth}{0.7pt}}\par
  \vspace{3pt}%
}
```

`beamercolorbox` centering is the trap: it vertically centers the title in
ht+dp, so the title floats near the rule. `\parbox[t]` pins it to the page top
(y≈0). Multi-line titles wrap inside the parbox (line gap = \fontsize baseline).

### Variable-font bold — the fix that makes ALL deck bold real

Anthropic Sans is a variable font (single `AnthropicSans-Romans-Variable-25x258.ttf`);
fontconfig lists `style=Display Bold` but XeTeX/fontspec never applies it —
`\bfseries` renders REGULAR everywhere (titles, `\textbf`, teal labels), silently.
Dead ends:
- `RawFeature={weight=700}` → `Unknown feature` (silently dropped)
- `RawFeature={wght=700}` → same
- `BoldFont` by filename → `cannot be found` (XeTeX kpathsea does not search
  `~/Library/Fonts` by filename — use the fontconfig family name)
- `FakeBold=0.35` → compiles clean, visually INVISIBLE (+4% density)

Working preamble:

```latex
\setmainfont{Anthropic Sans}[
  BoldFont={Anthropic Sans},
  BoldFeatures={FakeBold=1.0},
]
\setsansfont{Anthropic Sans}[
  BoldFont={Anthropic Sans},
  BoldFeatures={FakeBold=1.0},
]
```

Verification: vision models say "regular" on small bold text (unreliable), and
fitz span `flags` never mark synthetic bold (embolden). Measure pixel density —
render the title strip at dpi 150 and count dark pixels:

```python
import fitz
pix = fitz.open('deck.pdf')[2].get_pixmap(dpi=150, clip=fitz.Rect(0, 0, 453, 30))
dark = sum(1 for y in range(pix.height) for x in range(pix.width)
           if pix.pixel(x, y)[0] < 120) / (pix.width * pix.height)
# FakeBold 0.0 → 0.0540 · 0.35 → 0.0563 · 1.0 → 0.0676  (1.0 = clearly bold, +20%)
```

### Takeaway pages: vfill bottom-anchoring (don't fight it)

`\takeawaybar`'s `\vfill` pins takeaway+sources to the frame bottom. Content
height changes above do NOT move it (vfill absorbs); enlarging a chart to
"fill" the page causes REAL overflow (sofr_path 0.52→0.72\textwidth: sources
243.5→262pt, off-page). The sources line sits on the page-number row,
x-separated (sources x24, page number x≈437) — fine, not an overlap.
232pt overflow threshold is conservative; real limit = page-number top + x-sep.

### Divider & line-spacing values (user: "好好排个版…好好想想怎么设置数值")

- Card top rules UNIFIED 1.2pt teal (was 1.0 / 1.4 mixed); frametitle rule
  0.7pt teal; takeaway bar 0.7pt cloud-grey.
- Callout padding: `\colorbox` has NO padding (text touches the grey edge) —
  use `\fcolorbox{paper}{paper}` + `\setlength{\fboxsep}{3pt}` (same fill+border
  = invisible border, fboxsep pads all four sides).
- kpicard: rule→label 2pt / label→value 1.5pt / value→note 1.5pt.
- tradecard: rule→name 2pt / name→fields 3pt / field gaps 2pt.
- With 14pt titles, module rhythm compresses: `\vcard` 4pt / `\vblock` 6pt /
  `\vthin` 2pt (was 6/8/2 — the taller title area eats the budget).
- A1 glossary two-column pages: `\footnotesize\setlength{\baselineskip}{9pt}`
  to keep a 10-row column under the page-number row.
