# Sell-Side Research Report: Multi-Document Analysis Pattern

> Derived from: `AI基建-液冷报告资料.zip` analysis (2026-07-15)
> Report style reference: 广发证券《AI珠峰系列十：液冷设备》(2026-05-28)

## Multi-Document Extraction & Parallel Analysis Workflow

When given a zip of 10-20 PDFs to synthesize into a report:

### Phase 1 — Batch Extract

```python
import fitz, json, os

base = "/path/to/extracted/folder"
results = []
for root, dirs, files in os.walk(base):
    for f in sorted(files):
        if not f.endswith(".pdf"):
            continue
        path = os.path.join(root, f)
        rel = os.path.relpath(path, base)
        doc = fitz.open(path)
        text_parts = [f"=== P{i+1} ===\n{p.get_text()}" for i, p in enumerate(doc)]
        doc.close()
        results.append({"file": rel, "pages": len(doc), "text": "\n\n".join(text_parts)})

with open("extracted_texts.json", "w", encoding="utf-8") as f:
    json.dump(results, f, ensure_ascii=False)
```

### Phase 2 — Parallel Subagent Analysis

Split the extracted JSON by directory groups, dispatch one subagent per group.

Each subagent reads the JSON, filters its files, reads text, and outputs structured analysis in markdown.

### Phase 3 — Synthesize + Write

Combine all subagent outputs into a comprehensive `notes/` file, then produce the formal report in `docs/jul-NN-topic/`.

### Phase 4 — Subagent Review

After writing the report, dispatch a subagent (use deepseek-v4-pro or similar strong model) to review it. The subagent should receive:
- The report file path
- The format rules from SKILL.md's sell-side section
- Instructions to produce a structured optimization report with P0/P1/P2 priority levels

### Phase 5 — Fix + Chart Generation

1. Apply fixes from the review in priority order (P0 → P1 → P2).
2. **Chart duplication check** — Before generating, verify no two charts show the same data dimension. If fig5 and fig10 both show a timeline of the same topic, consolidate or differentiate them.
3. Generate real SVG charts with matplotlib to replace all ASCII art.
4. **Flowchart verification** — After generating flowcharts, open in browser + vision_analyze to check: all same-tier boxes have identical height, sub-items horizontally aligned, arrows connected without gaps, no light-on-light color contrast issues.
5. Update source path notes from "待补充" to actual `fig/*.svg` paths.
6. Run the Typography Polish Pass (see SKILL.md).
7. Run verify-after-passes: 0 straight quotes, 0 "我们认为", 0 absolute paths, 0 "待补充".

### Table/Figure Data Source Cross-Check

Before finalizing, verify:
- Every percentage/number in bold claims has its cited source actually supporting it. A common P0 error: citing Company A's data when describing Company B's metrics.
- When multiple companies produce the same class of product, each has a separate source annotation.
- If you only have data for one player but describe a market pattern involving multiple, either find sources for the others or narrow the claim.

## Report Structure Rules

### Section numbering
Follow the source report's scheme exactly. If the reference report uses `三、`, `四、` then match that.

### Paragraph structure (mandatory)
```
**Topic sentence — summarizes the entire paragraph in one bold claim.**
Supporting data point #1 (source: X).
Supporting data point #2 (source: Y).
Logical analysis: why this matters, what it implies.
```

### Chart/table balance
Aim for one visual element (table/chart/diagram) every ~100-150 words of text. For drafts use:
- ASCII bar charts for value comparisons
- ASCII flow diagrams for frameworks
- Markdown tables for structured data

For final delivery, replace all ASCII charts with SVG charts generated via matplotlib.

### Source tracking
```
数据来源：<organisation>，<report name>（底稿：fig/figX_description.svg）
```

### Acronym definitions
Every acronym gets Chinese + English full name on first occurrence:
```
CSP（云服务提供商，Cloud Service Provider）
AIDC（人工智能数据中心，AI Data Center）
PFAS（全氟/多氟烷基物质，Per- and Polyfluoroalkyl Substances）
```

## Sell-Side Report Tone

- **Assertive, not hedged** — "液冷已成为必选项" not "液冷可能成为趋势"
- **Data-first, judgment-second** — State the data, then state what it means for investors
- **Investor-oriented** — Every section should end with a conclusion about investment implications or competitive dynamics
- **No "will be discussed below"** — Don't preview what's coming. Just deliver the content.
- **Company/stock references** — When mentioning public companies, cite the ticker and a source for the data point

## Typography and Style Rules for CN Reports

These rules apply to ALL Chinese sell-side research reports:

### Quotation marks
Use curved Chinese quotes `" "` (U+201C / U+201D) NOT straight ASCII `" "`. Every single instance.

### Chinese-Western spacing
Insert a space between:
- CJK char + Latin letter: `3M垄断` → `3 M 垄断`
- CJK char + digit: `2025年` → `2025 年`
- Digit + CJK char: `达到4万亿` → `达到 4 万亿`

Do NOT insert inside markdown link syntax, table cells, or code blocks.

### AI-ism removal (zero tolerance)

| Remove/replace | Reason |
|---------------|--------|
| "我们认为，" | Filler, not analysis. Remove unless it's an original forecast. Run TWO passes — first pass may miss some. |
| "核心" (overused) | Replace some instances with "关键". 2-3 per page is fine; 8+ is AI-like. |
| "在...背景下" | Direct statement instead. |
| "随着..." | Present tense without temporal framing. |
| "历史性的" / "需要清醒认识到" | Simpler alternatives. |
| "根据我们的推演" | "当...后" or just state the claim. |
| "供给收缩为...创造了...窗口" | "供给收缩给...打开了...窗口" |
| "值得注意的是" | Remove entirely — empty filler. |
| "至关重要" | Replace with "关键" or just state directly. |

### Filename discipline
- Check spelling before creating: `competition` not `compitition`
- Use English lowercase + hyphens for file names
- No Chinese characters in file names if avoidable

## Common Pitfalls

- **数据来源张冠李戴 (Data citation attribution errors)** — Citing Company A's data for Company B's metric. E.g., attributing ~70% gross margin (3M's figure) to 新宙邦's annual report. Always verify the source company matches the metric claimed.
- **Timing inconsistencies** across different sections of the same report (e.g., saying "12-18 months for certification" in one section and "2-3 years of accumulation" in another for the same process).
- **ASCII charts left in the final deliverable** instead of SVG charts.
- **"待补充" source path notes** left unfilled after chart generation.
- **Acronyms used without full name definitions** on first occurrence.
- **Filename typos** (e.g., `compitition` vs `competition`).
- **No subagent review before delivery** (missing P0 issues like data citation errors).
- **Redundant charts** — Two charts showing the same data with different formatting. Only keep one.
- **Uneven flowchart boxes** — Multi-line text box taller than single-line neighbors. Force same height.
- **"我们认为" survived first pass** — Always run a second grep after removal to catch stragglers.
- **Absolute paths in deliverable** — Relative paths only. Check after path updates.
