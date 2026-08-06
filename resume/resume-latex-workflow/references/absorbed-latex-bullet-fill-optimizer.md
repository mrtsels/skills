---
name: latex-bullet-fill-optimizer
description: >-
  Analyze PDF bullets and edit LaTeX text to fill lines.
version: 0.1.0
author: Hermes
metadata:
  hermes:
    tags: [LaTeX, PDF, Text-Optimization, Resume]
---

# LaTeX Bullet Fill Optimizer

Analyze bullet item last-line fill in a compiled PDF, then edit the corresponding LaTeX source to minimize dangling short lines. Works entirely through text edits — no layout parameter changes, no `\emergencystretch`. Requires PyMuPDF (`fitz`).

## When to Use

- "Bullet text in my resume PDF leaves too much whitespace on the last line."
- "Make each bullet point fill its lines more evenly."
- "I want to quantify how full each line is before editing."

## Prerequisites

- PyMuPDF: `python3 -c "import fitz"` — install with `pip install PyMuPDF` if missing.
- LaTeX project that compiles to a single PDF file.

## How to Run

1. Compile the `.tex` source to produce `main.pdf`.
2. Run the analysis script via `terminal` to see the current state.
3. Edit the `.tex` source (via `patch` / `write_file`) to add or trim text.
4. Recompile and re-run the analysis — iterate.

## Quick Reference

```python
# Core analysis — run from the LaTeX project directory:
python3 -c "
import fitz
doc = fitz.open('main.pdf')
page = doc[0]
blocks = page.get_text('dict')['blocks']
# ... (see Procedure for full script)
"
```

## Procedure

### 1. Extract bullet text with line positions

Run from the LaTeX project directory:

```bash
python3 << 'PYEOF'
import fitz
doc = fitz.open('main.pdf')
page = doc[0]
blocks = page.get_text('dict')['blocks']
lines = []
for b in blocks:
    if 'lines' in b:
        for l in b['lines']:
            lines.append({
                'y': l['bbox'][1],
                'x0': l['bbox'][0],
                'x1': l['bbox'][2],
                'text': ''.join(s['text'] for s in l['spans']).strip()
            })
bullets = []
i = 0
while i < len(lines):
    if lines[i]['text'].startswith('\u2022'):
        item = [lines[i]]
        j = i + 1
        while j < len(lines) and lines[j]['y'] - lines[j-1]['y'] < 12 \
              and not lines[j]['text'].startswith('\u2022'):
            item.append(lines[j])
            j += 1
        bullets.append(item)
        i = j
    else:
        i += 1

cont_w = 496     # continuation line width (~543 - bullet indent)
first_w = 504    # first line width (~543 - bullet marker offset)
for idx, item in enumerate(bullets):
    n = len(item)
    pct = (item[-1]['x1'] - item[-1]['x0']) / (first_w if n == 1 else cont_w) * 100
    flag = 'OK' if pct >= 93 else 'NG'
    short = item[0]['text'][12:55] if item[0]['text'].startswith('\u2022') else item[0]['text'][:43]
    print(f'{flag} #{idx+1:2d} {n}lines last{round(pct)}%  {short}')
print(f'\nAbove 93%: sum(OK below) / Total')
PYEOF
```

Adjust `cont_w` and `first_w` if your `leftmargin` or `labelsep` differs. Derive them from the actual X positions of the first bullet line and continuation lines in your PDF.

### 2. Interpret the output

- **OK** — last line is ≥93% full. Acceptable.
- **NG** — last line is below 93%. Needs text editing.

For 1-line items: you have room to add text. Add keywords, modifiers, or details at the end until the next compile shows ≥93%. Do NOT add so much that the line wraps to 2 lines — build after each edit.

For 2+ line items: adding text AT THE END causes the ENTIRE paragraph to re-break, frequently pushing content to an extra line. Before editing, estimate headroom:

```
headroom_pt = (1.0 - current_fraction) × cont_w
```

If headroom is < 50pt (~5-6 words), DO NOT attempt to edit — you will overflow. Accept the item as-is.

### 3. Edit the LaTeX source

Use `patch` with `mode='replace'` to make targeted edits. Prefer adding to the VERY END of a bullet line's content — this minimizes unintended reflow. After each batch of edits, recompile and re-run the analysis.

### 4. Keep it on one page

Every text addition risks pushing total content to a second page. After each round, check page count:

```python
import fitz
doc = fitz.open('main.pdf')
print(f'Pages: {len(doc)}')
```

If the page count increases, revert the most recent edits with `git checkout <commit> -- path/to/main.tex`.

## Pitfalls

- **Line grouping heuristic** uses a 12pt Y-gap threshold. If your line spacing is tighter or looser, change the `< 12` value to match your effective `\baselineskip`.
- **Font/size changes** alter `cont_w` and `first_w`. Re-measure when you change font, `leftmargin`, or `labelsep`.
- **Adding text mid-paragraph** instead of at the end often produces worse line breaks — LaTeX reflows from scratch.
- **1-line skills items** (e.g. `\textbf{Languages:} ...`) are the safest to extend. 2-line technical bullets are almost always at capacity.
- This tool measures the LAST line only. A bullet spanning 3+ lines with a short last line needs to be trimmed, not extended.

## Verification

```bash
python3 -c "
import fitz
doc = fitz.open('main.pdf')
print(f'{len(doc)} page(s)')
page = doc[0]
# Count bullets and their line counts
blocks = page.get_text('dict')['blocks']
bullets = sum(1 for b in blocks if 'lines' in b for l in b['lines']
              if ''.join(s['text'] for s in l['spans']).strip().startswith('\u2022'))
print(f'Bullet items in PDF: {bullets}')
"
```
