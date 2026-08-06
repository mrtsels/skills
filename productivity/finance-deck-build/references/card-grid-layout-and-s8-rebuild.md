# Card-grid layout: replacing hand-placed tikz clusters (S8 case study, Aug-2026)

Deck: `tasks/task-5/task5_rates_deck_mtheme.tex` (27-page Beamer rates deck, mtheme +
custom style system). Page S8 "SR3 turns a quarter of compounded SOFR into one
auditable contract" was flagged by the user as 排版有点丑; the user's fix direction
was "第一页是个很好的例子" (page 1's uniform metric-card grid is the exemplar).

## Why the original page broke

The original S8 was a 9-node tikz diagram: one dark core box ("96.00 SR3 FUTURE /
100 − R") at (5.45, 0.55) plus 8 light `dchip` spec boxes placed at hardcoded
centers — 4 left (x=1.35, y = 2.05/1.2/0.35/−0.5), 4 right (x=9.55, same ys), one
wide note chip at (5.45, −1.35).

Root cause: `at (x,y)` anchors the node CENTER. Chips have 2–4 text lines
depending on wrapping (e.g. "0.0025 = $6.25 near \\ 0.005 = $12.50 beyond"
wraps to 4 lines; "VENUE \\ CME Globex" is 2). Fixed center-y with varying box
heights ⇒ boxes overlap vertically, gaps look uneven, and long lines clip at
`text width`. Measured overlap: TICKS (4 lines, h≈1.6cm at y=0.35, spans
±0.8) collided with its neighbors at y=1.2 and y=−0.5 (each spanning ±0.55).
The bottom note chip (4.0cm wide) floated under an 11cm-wide diagram = dead
space. A core-in-the-middle + 4 chips/side layout is also geometrically
impossible: 4 rows × ~1.4cm chips = 5.6cm leaves no room for a 2.5cm core.

## Iterations (fit budget on a 9cm paper, navy frametitle + footline ⇒ ~7.6cm body)

1. figmod hero box + 4×2 card grid + callout + takeaway → **Overfull \vbox
   70pt too high** (content clipped at the slide bottom). Hero row alone
   (≈1.7cm) + 2-row grid + callout + takeaway > body.
2. 3×3 card grid (9 cards incl. QUOTE) + callout + takeaway → **27.9pt too
   high** — still one layer too many.
3. Final: 3×2 grid (6 cards, QUOTE as darkcard hero) + callout + takeaway →
   **0 overfull**. Removing the hero row AND trimming 3 filler cards freed the
   budget. Lesson: when a frame overflows, drop a LAYER (hero row merged into
   the grid), don't shrink fonts (user rule: never shrink to fit).

## Overfull \vbox line → frame mapping

`grep 'Overfull \\vbox' build.log` reports `at line L`, where L is the line of
the overflowing frame's `\end{frame}` (the whole frame is one unbreakable
vbox). Use `grep -n '\end{frame}' file.tex` to find which frame L belongs to.
Small pre-existing overfulls (1–13pt) on other pages are noise — the deck
already shipped with them; only NEW large ones matter.

## Verification loop (per changed page)

```bash
xelatex -interaction=nonstopmode deck.tex >/tmp/b1.log 2>&1   # ×2 for refs
grep -c '^!' /tmp/b2.log          # 0 = no errors
grep 'Overfull \\vbox' /tmp/b2.log
pdftoppm -png -r 110 -f 8 -l 8 deck.pdf /tmp/s8 && vision_analyze /tmp/s8-08.png
```
Ask the vision model targeted questions: cut-off/overflow at bottom, card
grid uniformity, text clipping inside cards, whitespace balance.

## The `darkcard` environment (now in the preamble)

Same geometry as `card`, navy fill + white text — use for the ONE hero data
unit per slide. Emphasis via COLOR, never font size (user rule).

```latex
\newsavebox{\darkcardbox}
\newenvironment{darkcard}{%
  \par\noindent
  \setlength{\fboxsep}{\modpad}%
  \begin{lrbox}{\darkcardbox}%
  \begin{minipage}[t]{\dimexpr\linewidth-2\modpad-2\fboxrule\relax}%
  \color{white}%
}{%
  \end{minipage}%
  \end{lrbox}%
  \fcolorbox{navy}{navy}{\usebox{\darkcardbox}}%
  \par\vspace{\modgap}}
```
Usage: label via `{\footnotesize\bfseries\color{cloud}…}`, value via
`{\fontsize{12}{12.5}\selectfont\bfseries\color{white}…}` (same size as
`\decknum` — numbers stay uniform across cards), note via
`{\footnotesize\color{amber}…}`.

## Final S8 structure (pattern to imitate)

```
columns[T,onlytextwidth]  (3 × \cwt)
  3 columns × 2 cards each: QUOTE(darkcard) | CONTRACT UNIT | RISK UNIT
                            UNDERLYING      | TICKS         | SETTLEMENT
  every card = \decklabel{HEADER} \\[2pt] + bold navy value + \decktext note
\callout{Dec-26 SR3 ≈ 96.00 · ≈$240k notional per contract}
\takeawaybar{Implication}{…}
\sourcesline{…}
```

## User content rules captured this session

- "很多诸如39 quarterly + 6 serial这些东西是不用写的 你可以精简内容" — trim generic
  exchange boilerplate (venue, contract-months counts, last-trading-day); keep
  only core differentiating specs. 9 cards → 6.
- "96.00 and $2,500的字号为什么不一样 统一一下" — all big numbers via `\decknum`
  (12pt); no per-card ad-hoc sizes.
- "如果你想强调96.00的话可以把那个框的配色变一下" — hero emphasis = darkcard color,
  not a larger font.
