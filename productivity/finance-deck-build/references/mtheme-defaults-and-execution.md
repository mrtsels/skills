# mtheme (Metropolis) v1.2 — Default Settings & McKinsey-Rule Execution

Session-derived (Aug 2026): pulled https://github.com/matze/mtheme, read the local
`.sty` sources (installed at `~/Library/texmf/tex/latex/metropolis/`), compiled a
verification skeleton. Use when the user says "用mtheme默认设置 / 分析模版默认设置 /
把design规则融入mtheme". Rule of thumb the user enforces: **use original template
settings (font sizes, text positions) — never hand-tune values.**

## Defaults (from source, demo = `\documentclass[10pt]{beamer}`)

| Item | Default | Source |
|------|---------|--------|
| Base size | 10pt (official demo); beamer default 4:3 — 16:9 needs `aspectratio=169` in class opts | demo.tex:1 |
| Body font | Fira Sans Light (sans), bold→Fira Sans; mono Fira Mono | font theme |
| tabular numbers | auto `Numbers={Monospaced}` (aligned digits in tables) | font:88 |
| linespread / parskip | 1.15 / 0.5em | inner:249–251 |
| frametitle | `\large` = 12pt bold, white on full-width dark-teal bar, padding 2.2ex | font/outer |
| title / section title | `\Large` = 14.4pt bold | font:96–101 |
| block title | `\normalsize` = 10pt bold | font:102 |
| caption / author / date | `\small` = 9pt | font |
| page number | `\scriptsize` = 7pt, bottom-right, `numbering=counter` | outer:65 |
| progressbar | `progressbar=none`; **sectionpage=progressbar** (divider pages have a progress bar) | outer:58 / inner:46 |
| nav symbols | removed | outer:61 |
| text colors | fg=mDarkTeal `#23373b`, bg=black!2 (near-white) | color theme |
| alert / example | mLightBrown `#EB811B` / mLightGreen `#14B03D` | color theme |
| block style | **`block=transparent`** default (title = bold text, NO box); `\metroset{block=fill}` gives light-gray cards | color:37,104 |
| itemize marker | `\textbullet` | inner:240 |
| caption | numbered, separator `: ` | inner:241–242 |
| sectionpage / subsectionpage | progressbar / none | inner:46–47 |
| titleformat | all `regular` (no smallcaps/uppercase) | font:236–240 |
| title page | title → 0.4pt rule → author → date → institute, \vfill-centered | inner:50–63 |
| standout frame | `\begin{frame}[standout]` — dark-teal full bg, `\Large` bold centered (built-in "key takeaway" page) | inner:260–292 |

Options entry point: `\metroset{...}`. Built-in helpers: `\mreducelistspacing`
(tighten lists), `\appendix` auto-disables numbering+progressbar (outer:125–132)
→ natural home for backup/detail slides.

## Machine-specific

No Fira fonts on this Mac → fontspec falls back (deck uses Anthropic Sans via
fontspec). Variable font has **no real bold** → `\textbf{}` renders as regular;
rely on structure ("Keyword: …" lead-ins), not weight, for emphasis.

## Author's design principles (blog: matze.bloerg.net/posts/a-modern-beamer-theme/)

The author's 2014 manifesto explains WHY the defaults are what they are — quote it
when the user asks to justify a "keep default" call:
1. **Minimal visual noise, max content space** (Tschichold/Butterick): no nav bar,
   no progress indicators, no heavy block elements — only frame title, frame number,
   content. → never add headers/decorations; keep `block=transparent`.
2. **Color subtraction**: dark teal (mDarkTeal) for everything; orange (mLightBrown)
   ONLY for `\alert{}`-type accents; background is near-white (black!2), not pure
   white (eye strain). → no new colors, ever.
3. **Font layering**: Light body / Book bold / Mono for code+digits; hierarchy by
   weight, not color. ⚠️ The blog-era headline style was LOWERCASE SMALL CAPS —
   v1.2 default is `regular`; do NOT re-enable smallcaps.
4. **Section pages**: auto-inserted on `\section{}` with a tiny TikZ progress bar →
   organize decks into parts with `\section{}`, don't hand-build dividers.
5. **Data-ink ratio (Tufte)**: charts show only data; built-in pgfplots styles
   `mbarplot` / `mlineplot` strip boxes/grids. → use those for all charts.
6. **Content first**: "even if the theme makes your presentation look professional,
   focus on the content." — the deck text rules (McKinsey mapping below) outrank
   any styling impulse.

## McKinsey text rules → mtheme execution (condensed)

1. **Headline = conclusion** → put it in `\frametitle{}` (default style, don't touch);
   1 line preferred, hard max 2 (10pt, 4:3 ≈ 55–60 chars/line). No `titleformat frame=allcaps|smallcaps`.
2. **One page, one message** → frametitle + evidence + bottom takeaway. No custom
   `\framesubtitle` template (mtheme doesn't style it) — write the one-line
   elaboration as the first body line. Overflow → split frames, never shrink fonts.
3. **Pyramid ≤3 levels** → L1 frametitle; L2 `\begin{block}{point}` titles (default
   transparent = bold text, no box — exactly the McKinsey look); L3 nested itemize.
4. **Short sentences + keywords** → plain itemize (`\textbullet` default); keep
   defaults; `\mreducelistspacing` if lists feel loose — never hand `\vspace` numbers.
5. **Parallel bullets** → same `\textbf{Keyword:} explanation` skeleton per group.
6. **Selective bold** → `\textbf{Keyword:} …`; only conclusion words / figures /
   objects / direction. Never whole lines.
7. **Data embedded in conclusions** → `up \textbf{35\%}` (escape `%`); groups of
   figures → tabular (auto monospaced digits) or blocks; each figure needs
   metric/time/base/meaning.
8. **Horizontal alignment** → three columns `\begin{columns}[t]` + three
   `\column{0.30\textwidth}`; text-left-chart-right `0.30` + `0.65` +
   `\includegraphics[width=\textwidth]`; conclusion-top-evidence-bottom via frametitle
   + `\vfill` + Implication. Chart source: `{\footnotesize Source: …}` under chart,
   caption is `\small` numbered.
9. **Whitespace** → 3–5 blocks/frame, 2–4 lines/block, ≤5 bullets; detail → appendix
   (auto no page numbers) or `\note{}`.
10. **Fixed size hierarchy** → use template defaults only: 12pt bold / 10pt bold /
    10pt / 9pt caption / 8pt `\footnotesize` source. No custom sizes, ≤4 levels/page.
11. **Mini-heading per module** → `\begin{block}{Heading}` … `\end{block}`, or
    bold first word of bullet. No bare prose paragraphs.
12. **Implication line** → `\vfill` + `\alert{Implication:} …` (alert = built-in
    mLightBrown, no custom color); final takeaway → `[standout]` frame.

## Verified frame skeleton (compiled clean, 0 errors)

```latex
\begin{frame}{Lower-tier cities will drive half of new coffee consumption}
  \begin{columns}[t]
    \column{0.30\textwidth}
      \textbf{Market expansion:} industry growing at double-digit rates
    \column{0.30\textwidth}
      \textbf{Competition intensifying:} incumbents keep raising spending
    \column{0.30\textwidth}
      \textbf{Costs rising:} fulfilment and acquisition costs up together
  \end{columns}
  \vfill
  \alert{Implication:} shift growth strategy from more spending to higher retention
  {\footnotesize Source: …}
\end{frame}
```

Note: `columns[t]` (lowercase) is correct for text columns; the mtheme port skill
uses `columns[T]` for chart+itemize mixes — see `mtheme-beamer-deck.md` for why.

## Brief intake: collapsed pastes

User pastes big blocks that arrive in the transcript COLLAPSED (`[[ N lines ]]`).
Never reconstruct/fabricate the text — recover verbatim from the original source:
sender email via `agently-cli message +read --id msg_…` (parse with
`json.JSONDecoder().raw_decode` — CLI output has a trailing tip line after the JSON),
or `session_search` for the user's earlier paste; if neither has it, ask for a
re-paste. Save as `task.md` in the task folder (repo convention: briefs live in
`tasks/task-N/task.md`, verbatim from the mentor email).
