---
name: quant-lecture-notes
title: quant-lecture-notes
description: >
  Transform Asia Quant Academy lecture PDFs into bilingual (English+Chinese)
  structured Markdown notes with LaTeX formulas, term tables, and summary.
---

# quant-lecture-notes

Convert AQA course lecture PDFs into comprehensive, structured Markdown notes following the established style from Lecture 7 Notes.md and Lecture 8 Notes.md in `/Users/minimx/quant-academy/`.

## When to trigger

- User says "make notes from Lecture N.pdf"
- User says "need notes for lecture X-Y" (batch: multiple lectures)
- User says "按照Lecture X.pdf -> Lecture X Notes.md的标准做一份笔记md"  
- User drops a lecture PDF and asks for structured notes
- User says "中文化" / "rewrite in Chinese" referring to a notebook or markdown file that needs conversion

### Style variants: two supported formats

The user has two distinct format preferences depending on context:

**Format A — Bilingual body (default, for conceptual/finance lectures):**
- English body text, Chinese translations in term tables
- Chinese numerals for sections: 一、二、三
- Term tables with `英文 | 中文 | 解说`
- Blockquotes for supplementary insights
- Quick Reference summary table at end

**Format B — Chinese-body with inline annotations (for technical/programming lectures):**
- Chinese body text, English terminology in parentheses `（English Term）`
- Arabic numerals for sections: 1, 2, 3
- No per-section term tables; instead annotate inline on first use
- Still end with a summary / quick-reference table
- Used when user says "中文化" or "用中文写" or the content is code/algorithm-heavy

**Detection:**
- If user says "中文化" or "用中文写一遍" → Format B
- If the source material is a Jupyter notebook or code-heavy (Lecture 3, Lecture 5) → Format B
- If the source is a conceptual finance lecture with many new English terms → Format A
- When in doubt, ask. But prefer Format A for quant lectures, Format B for programming/math lectures.

## Workflow

### 0. Check for existing skill before relying on Notes.md

The `quant-lecture-notes` skill itself is the authoritative reference for the format. If the user has also loaded specific Notes.md files, read those too for style nuance — but the skill's instructions take precedence when the two diverge.

### 1. Read existing reference notes for style (then extract lecture text)

```bash
# Read the most recent Notes.md as the style template
# e.g. read_file('Lecture 11 Notes.md') if it's the latest
```

Always read an existing Notes.md first (the most recent one) to internalize the exact format before writing — do not guess the style.

### 2. Extract text from lecture PDFs

For a single lecture:
```bash
python3 << 'PYEOF'
import fitz
doc = fitz.open('/Users/minimx/quant-academy/Lecture N.pdf')
text = ""
for page in doc:
    text += page.get_text() + "\n---PAGE BREAK---\n"
doc.close()
with open('/tmp/lectureN.txt', 'w') as f:
    f.write(text)
print(f"Extracted {len(text)} chars")
PYEOF
```

Then inspect with `read_file('/tmp/lectureN.txt')` — this gives you line numbers for reference.

> **CRITICAL: Do NOT echo the extracted text to the user.** Read it internally (read_file), understand it, then write the notes file directly with write_file. Displaying raw extraction output confuses the user — they expected markdown notes, not PyMuPDF output.

**For batch (multiple lectures):** use a loop:
```bash
python3 << 'PYEOF'
import fitz
for n in [9, 10, 11, 12]:
    doc = fitz.open(f'/Users/minimx/quant-academy/Lecture {n}.pdf')
    text = ""
    for page in doc:
        text += page.get_text() + "\n---PAGE BREAK---\n"
    doc.close()
    with open(f'/tmp/lecture{n}.txt', 'w') as f:
        f.write(text)
    print(f"Lecture {n}: {len(text)} chars extracted")
PYEOF
```

Then batch-read all temp files before writing anything.

### 3. Understand the full content before writing

Read the complete extracted text (all pages) before drafting. The extracted text from PyMuPDF (fitz) is clean but:
- Slide headers/footers (e.g. "Lecture 9 Version 2026 41 / 41") appear on every page — ignore them
- Bullet points and table text are preserved but may lose some formatting
- **IMPORTANT: Figures/images are not extractable** — slides with embedded images produce no useful text (e.g. Lecture 11's algo descriptions just say "Details will be covered during the lecture"). For these, reconstruct the content from context: the slide title, surrounding text, and your knowledge of the concept

### 4. Structure the notes

Use this canonical layout:

```
# Lecture N — English Title（中文标题）

> 讲师：Henry Chan | Asia Quant Academy
> 拓展笔记（基于课堂内容 + 补充知识）

---

## 一、Topic One（中文翻译）

### Subtopic（中文翻译）

#### Term Table (if needed)

| English（英文） | 中文 | 解说 |
|---------|------|------|
| **Term** | 术语 | 简洁解说 |

#### Formulas

$$ ... $$

> **Blockquote for supplementary insights, caveats, or deeper intuition**

### Next Subtopic

...
```

#### Section numbering

- Use **Chinese numerals** for top-level sections: 一、二、三、四、五、六
- Use **###** for subsections
- Use **####** for sub-subsections (rare — only for term tables or formula groups)
- Maximum depth: ####

#### Concrete examples — REQUIRED alongside every formula

The user explicitly rejected abstract notation without examples. Every formula block MUST be followed by AT LEAST one of:

1. **Numerical example** — plug in real numbers and show the computed result
2. **Scenario walkthrough** — describe in words what the formula does, using a concrete market situation
3. **Matrix/vector as actual matrix** — when the notation involves vectors or matrices, display them as `\begin{pmatrix} ... \end{pmatrix}` with labeled row annotations, NOT as inline tuples like `(X1, X2, ..., Xn)`

Bad (got corrected):
```
X(t) = (X1(t), ..., Xn(t))
```

Good:
```
\mathbf{X}(t) =
\begin{pmatrix}
-500  & \text{买二价 399.8} \\
-300  & \text{买一价 399.9} \\
+200  & \text{卖一价 400.0}
\end{pmatrix}
```

Bad (got corrected):
```
Q^B_i(t): distance i from ask
```

Good:
```
Q^B_1 = X_{400.0-1} = X_{399.9} = -300  (距离卖一 1 档的买单)
```

#### Formula formatting — CRITICAL RULE

DO NOT write formulas in ASCII code blocks. Use **LaTeX** exclusively:

- **Display math** (important standalone formulas): `$$ ... $$`
- **Inline math** (references in text): `$ ... $`
- **Environments**: use `\begin{aligned} ... \end{aligned}` for multi-line equations
- **Cases**: use `\begin{cases} ... \end{cases}` for piecewise definitions
- **Vectors/sets**: use `\mathbb{E}`, `\sum`, `\prod`, `\frac`, `\cdot`
- **Subscripts/superscripts**: `S_{t+\Delta t}`, `S^u_{t+\Delta t}`
- **Text in math**: `\text{...}` for words inside formulas
- **Arrows**: `\to` not ASCII `→` inside math

Bad (user will correct): 
```
S_t+∆t − S_t
──────────── = µ∆t + σ√∆t
    S_t
```

Good:
```latex
\frac{S_{t+\Delta t} - S_t}{S_t} = \mu \Delta t + \sigma \sqrt{\Delta t}\, \varepsilon_B
```

#### KaTeX pitfalls (markdown+math conflicts)

These cause silent parse errors — the markdown engine interprets characters before KaTeX processes `$...$` or `$$...$$`:

1. **Bare `*` inside `$...$` inline math** — `$f^*(\cdot)$` breaks because `*` is parsed as markdown emphasis before reaching KaTeX. Fix: use `\ast`: `$f^\ast(\cdot)$`.

2. **Numbered list items with `$$` display math** — `1. $$...$$` on the same line or indented inside a list causes `ParseError: Can't use function '$' in math mode`. Fix: keep `$$` at top level, no indentation. Use `**(N)**` instead of markdown `N.`:

   ```markdown
   **(1)**

   $$
   G = \sigma \frac{Q}{V} \times f(\cdot)
   $$

   **(2) Next:**

   $$
   G = \text{const} \times \sigma \sqrt{\frac{Q}{V}}
   ```
   NOT:
   ```markdown
   1. $$
   G = ...
   $$
   ```

3. **Italic `*...*` wrapping `$...$`** — `*[P.S. ... $f(\cdot)$]*` creates nested emphasis boundaries. Fix: use `_[...]_` (underscore) or `> P.S. ...` blockquote instead.

4. **`\!` negative thin space** — valid in KaTeX but keep inside `\left`/`\right` pairs to avoid unexpected spacing in some renderers.

#### Term table conventions

- Three columns: `English（英文） | 中文 | 解说`
- Bold the English term: `**Term**`
- Keep 解说 concise (1-2 sentences max)
- For supplementary tables (comparisons, features), use a simpler two-column format

#### Deep-dive incorporation

When the user asks for a detailed explanation of a topic covered in the lecture (e.g., "IRS讲一讲"): write a comprehensive subsection into the notes. Include:

- Conceptual diagram (ASCII art if helpful)
- Real-world use cases (table: scenario → problem → solution)
- Step-by-step derivation
- Numerical example with computed values
- Supporting theory (e.g., swap rate = weighted avg of forward rates)
- Key terms glossary at end of section

#### Summary table

End every notes file with:

```
---

## Summary — Quick Reference（快速对照表）

| 英文 | 中文 | 一句话核心 |
|------|------|-----------|
| **Term** | 术语 | 一句话 |
```

Every term introduced in the body should appear here. One row per concept.

## Pitfalls

1. **ASCII formulas** — user HATES these. Never use ```` ``` ```` for math. Always LaTeX.
2. **Skipping the reference note** — always re-read an existing Notes.md first. The format evolves subtly between lectures.
3. **Tables without 中文 column** — the bilingual layout is mandatory, not optional. Every table must have a 中文 translation column.
4. **Too shallow** — the notes are *拓展笔记*, not a slide transcription. Add supplementary knowledge, cross-references to prior lectures, and financial intuition (blockquotes).
5. **Missing 解说 on terms** — every table row needs a real explanation, not just a literal translation.
6. **Burying the hook** — start each section with a one-line "what is this and why does it matter" before diving into details. The user reads these as study notes.
7. **No numerical example** — where possible, add a concrete worked example. Quant notes need numbers to make theory concrete.
8. **Figure-heavy PDFs** — Some lectures (especially Lecture 11 on algorithms) embed content as images. fitz extracts little to no text from these slides. When you see a slide that's just a title + image caption, reconstruct the content: use the slide title + your knowledge of the concept + related slides. Do NOT leave a blank section or just the title.
9. **Mixed-content lectures** — Some lectures are conceptual (Lecture 9: market structure), others are math-heavy (Lecture 12: stochastic modeling). Adjust the balance: conceptual lectures get more terminology tables and intuition callouts; math-heavy lectures get more step-by-step derivations and formula explanations. Keep Quick Reference tables in both.
10. **Slide headers pollute the output** — PyMuPDF extracts footer text like "Lecture 9 Version 2026 41 / 41" on every page. Strip these mentally; they are not content. Only include slide content that carries information.
11. **Multi-lecture batch: write sequentially, not all at once** — When producing 3-4 lecture notes, write them one at a time with write_file. Each file is long enough that writing all in one pass risks truncation. Write → verify content with a quick look → move to next.
12. **The PDF may use a different structure than slides suggest** — Lecture 12's PDF is formatted as a paper (numbered sections 1.1-2.6) while the notes should use Chinese numerals (一、二). Always restructure: flatten the paper/slide hierarchy into the canonical note format.
13. **fitz text extraction misses structured tables and side-by-side comparisons** — PDF slides often embed critical content as visual elements (e.g. "Figure 7: Quote-driven vs Order-driven comparison" in Lecture 9). fitz.get_text() extracts the text but can flatten or lose multi-column table layouts, color-coded state transitions, and hierarchical visual comparisons. **Detection**: scan the raw extracted text for "Figure", "Table", "Comparison", "Diagram" — if you see a caption but no substantive data below, that slide was visual-only. **Reconstruction**: use the slide title + surrounding labels (column/row headers from bullet-point context) + domain knowledge to rebuild the full comparison in table form. Better to catch these in the first pass than wait for the user to flag them.
14. **Cross-reference related content from other lectures** — When a concept naturally connects to another lecture (e.g. Lecture 9 introduces Algorithmic Trading as a type, Lecture 11 dives into execution algorithms), add a cross-reference or a callout box. The user may ask for this distinction to be added — pre-empt it if you spot the connection. Also watch for **easily-confused concept pairs** that span lectures (e.g. Quantitative Trading vs Algorithmic Execution; Agency Trading vs Principal Trading) — call these out explicitly with a comparison table right where the first concept is introduced, so the user has the distinction clear from the start.
15. **Abstract notation without concrete examples** — The user will correct you if formulas stand alone without a worked example. Every formula must be followed by a concrete numerical scenario (see "Concrete examples" section above). This is non-negotiable.
16. **Vector displayed as row tuple** — Never write vectors as `(X1, ..., Xn)`. Always use `\begin{pmatrix}` column vector with row annotations showing the actual data.
17. **Fragmented formulas** — Never split a single formula across multiple lines with one symbol per line. Write the complete expression in one `$$...$$` block.
18. **English body when user wants Chinese** — For "中文化" requests or Jupyter notebook conversions, use Format B (Chinese body with English parenthetical annotations). Detecting which format to use is part of the workflow.
19. **Inline vs display math** — Standalone important formulas get `$$...$$`. Short references like variable names or numeric values in running text get `$...$`. Do not overuse display math for simple inline references.
20. **Missing row annotations on matrix examples** — When showing a matrix example, add a text annotation on each row explaining what that row represents (e.g. 买一价 399.9).
21. **KaTeX markdown conflicts** — Bare `*` inside `$...$` (e.g. `$f^*$`), numbered lists with `$$` blocks, and `*...*` italic wrapping `$...$` all cause parse errors. See the KaTeX pitfalls subsection under Formula formatting.

## Reference files

- `references/lecture-7-format.md` — Full template anatomy from Lecture 7 Notes.md
- `references/visual-slide-reconstruction.md` — Patterns for rebuilding content from slides where fitz.get_text() extracted no useful data (side-by-side comparisons, flow diagrams, screenshots)
