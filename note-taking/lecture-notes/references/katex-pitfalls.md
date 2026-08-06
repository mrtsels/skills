# KaTeX Pitfalls — Quant/Finance Markdown

Math-heavy PDFs (assignments, lecture slides) need careful LaTeX formatting to avoid KaTeX parse errors. These rules apply when converting extracted PDF text into Markdown with math blocks.

## Critical: No bare `*` inside `$...$`

The `*` character is markdown emphasis syntax. When placed inside `$...$`, some renderers process the `*` *before* recognizing the math mode, causing a "ParseError: Can't use function '$' in math mode".

**WRONG** — will break:
```markdown
$f^*(\cdot)$
```

**RIGHT** — use `\ast` instead:
```markdown
$f^\ast(\cdot)$
```

The `\ast` command renders identically (same `*` glyph) but doesn't trigger the markdown emphasis parser.

## Don't wrap `$...$` in markdown italic

**WRONG** — the `*...*` around `$...$` conflicts:
```markdown
*P.S. No need to find $f^*(\cdot)$ for this question*
```

**RIGHT** — use `_..._` for italic, or no italic wrapper:
```markdown
_P.S. No need to find $f^\ast(\cdot)$ for this question_
```

Or just remove the italic wrapper entirely.

## Display math (`$$`) after list markers

When a numbered list item starts with a display math block:

```markdown
1. $$
G = \sigma \frac{Q}{V}
$$
```

Some renderers misparse this if `1.` and `$$` are on the same line. Safer to put the number on its own line or use a separate paragraph structure.

## Valid commands — don't over-escape

These work fine in KaTeX (no need to remove):
- `\!` — negative thin space (`f\!\left(...\right)`)
- `\text{...}` — text inside math
- `\left\{`, `\right\}` — braces
- `\begin{pmatrix} ... \end{pmatrix}` — matrices

## Quick check list

- [ ] No bare `*` inside `$...$` (use `\ast` or `\star`)
- [ ] No `*...*` italic around `$...$` blocks
- [ ] Display math `$$` separated from preceding text by blank line
