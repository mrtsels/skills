# Beamer bibliography `\newblock` line-splitting — full diagnosis

Session: 2026-08, CUHK poster (`poster/poster.tex`, beamer + beamerposter +
gemini theme, LuaLaTeX, BibTeX/plain.bst).

## Symptom

Each citation rendered as three stacked lines:

```
[1] Jinze Bai, Shuai Bai, ... et al.
    Qwen Technical Report.
    arXiv preprint arXiv:2309.16609, 2023.
```

User requirement: one citation = one continuous block (natural wrapping
allowed, but no forced author/title/journal splits, no orphan DOI lines).

## Root cause (found by reading beamer source, not by guessing font sizes)

`/usr/local/texlive/<year>/texmf-dist/tex/latex/beamer/beamerbaselocalstructure.sty`
lines ~455-490: beamer redefines `\newblock` as a nested state machine.

```latex
\def\newblock{\beamer@newblock}
\def\beamer@newblock{%
  \usebeamerfont{bibliography entry author}%      % 1st \newblock: author slot
  \def\newblock{%
    \usebeamerfont{bibliography entry title}%     % 2nd: title slot
    \def\newblock{%
      \usebeamerfont{bibliography entry location}%  % 3rd: location
      \def\newblock{%
        \usebeamerfont{bibliography entry note}%    % 4th: note
        ...}}}
  \leavevmode\setbox\beamer@tempbox=\hbox{}%
  \ht\beamer@tempbox=1.5em\box\beamer@tempbox}      % <- the 1.5em box
```

`plain.bst` emits exactly 3 `\newblock` per entry (after authors, after
title, after journal), so every entry gets forced vertical breaks.
Additionally, beamer's `\@bibitem` re-`\def\newblock{\beamer@newblock}` at
EVERY item, which is why preamble-level `\renewcommand{\newblock}` is
clobbered.

## Working fix

In the preamble, AFTER `\usetheme{gemini}` (any theme loading):

```latex
\setbeamertemplate{bibliography entry title}{}
\setbeamertemplate{bibliography entry location}{}
\setbeamertemplate{bibliography entry note}{}
```

Leaves the `bibliography entry author` template intact; the state machine
still runs but produces no visible break, so each entry flows as one
paragraph. Verified: 14 entries continuous, no garbled text.

## Failed approaches (do not repeat)

| Approach | Result |
|---|---|
| `\footnotesize`→`\scriptsize`→`\tiny` | No effect — not a font-size problem |
| `\def\beamer@newblock{}` | Unreliable (state-machine internals) |
| `\renewcommand{\newblock}{\hskip .11em...}` | Overridden by `\@bibitem` per item |
| `\let\beamer@newblock\@empty` | Renders literal "newblockempty" garbage |

## Verification commands

```bash
# confirm entries are continuous (line breaks only at natural wrap points)
pdftotext -layout poster.pdf - | sed -n '/References/,/^\[4\]/p'
# visual check
pdftoppm -f 1 -l 1 -png -r 100 poster.pdf /tmp/ref_check.png
```

## Related layout notes

- Moving the whole References block below `\end{columns}` (full page width)
  helps long entries fit on one line, but does NOT fix the forced 3-line
  split — the template fix is the actual cure.
- Keep `\setbeamertemplate{bibliography item}[text]` (from gemini) as-is.
- If the user instead wants "one entry = one unbreakable line, move whole
  entry to next line if too long", that is a different requirement
  (parbox/minipage per item) — confirm before implementing.
