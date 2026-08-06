# Infrastructure Benchmark Report — Slide Format

For infrastructure/tool benchmarking reports (DB comparison, API performance, system evaluation). Differs from algorithm/process research reports — focuses on quantitative comparison rather than logic flow.

## Format

6–8 slides, each a horizontal rule `---`. One message per slide. No slide numbers in body — `## NN Topic` + `---` imply sequence.

## Slide Elements

### DB/Logo Icons
- DB logos: Wikipedia Commons SVGs (`upload.wikimedia.org/wikipedia/commons/...`)
- Concept icons: Bootstrap Icons CDN (`cdn.jsdelivr.net/npm/bootstrap-icons/icons/NAME.svg`)
- Place in `<img src="icons/NAME.svg" height="NN">` tags
- Use `height="22"` for header icons, `height="14"` or `height="16"` for inline
- Good convention icons: `database` (embedded/DB), `file-earmark` (single file), `server` (server-based), `lightning-fill` (faster), `columns-gap` (columnar), `cpu` (parallelism), `layers` (compound/stacked), `bar-chart-fill` (benchmark), `diagram-2` (patterns), `sort-up` (index/sorted)
- Keep icons in an `icons/` subdirectory in the report folder

### Data Representation
- Show concrete data forms side-by-side (table vs document, columnar vs row)
- Use separate code blocks for each format, not a single combined layout
- Each code block has a header line identifying the format, then sample data, then a one-line annotation
- DuckDB: ASCII table with columns and row values
- MongoDB: JSON document showing one tick
- Annotation line: `columnar: each column stored separately → read only requested fields` / `row-based: each tick is a full document, always reads whole doc`

### Results Table
- Latency results: 3-column table (Pattern | DB-A | DB-B | Ratio)
- Bold the most significant ratios
- Always include the unit (ms) in the header
- 1 decimal place for sub-10ms values, 1 decimal for 10-100ms values
- Before the results table, include a short **Performance requirements** section explaining why these metrics matter for the domain (real-time vs backtesting vs research)

### Comparison Tables
- Factor rows: left column = concept (with icon), right columns = each DB's approach
- Keep factor names short (1-2 words)
- Description: one line per cell, no wrap
- Mark the winning side with a `<img src="icons/lightning-fill.svg">` inline

### Code References
- Each implementation slide gets a code reference line at the bottom
- Format: `` `filename.py` — one action-oriented sentence what it does ``
- Action-oriented: "starts a REST server on :8000", "extracts CSV.zip → loads into both DBs", "sends HTTP requests to both backends, aggregates timing stats"
- Do NOT inline code blocks — reference by filename only
- Prepend a tech-stack icon: `<img src="icons/fastapi.svg" height="14">` for FastAPI, etc.

### Centered Elements
- Key conclusions: `<p align="center">...</p>` with bold
- Summary ratios: icon + bolt icon + bold text

### Headings
- `## NN Description` — no verb prefix, just the topic name
- "Why & Summary" can be the final merged slide (combine comparison table + conclusion in one)

### Performance Requirements Context
Before showing results, add 2-3 bullet points explaining the domain constraints:
- Real-time dashboards / trading screens → sub-10ms queries for short windows
- Backtesting / research → 1yr+ scans across multiple tickers
- REST API response time → affects strategy iteration speed

### Merging Slides
When asked to merge "Why" and "Conclusion" into one:
- Top half: comparison table (factors explaining performance difference)
- Bottom half: summary rows (one per DB, icon + verdict + icon attributes)
- Single divider `Columnar layout + vectorized execution = faster time-series range scans.` between them

## Differences from Algorithm Research Reports

| Aspect | Infrastructure Benchmark | Algorithm Research |
|--------|------------------------|-------------------|
| Format | Slides (`---` separated) | Sections with subsections |
| Content | Tables, icons, data samples | Mermaid + Python code blocks |
| Tone | Minimal, data-driven | Explanatory with edge cases |
| Code refs | Filename-only references | Inline code blocks |
| Structure | Flat slide sequence | Hierarchical (01 → A, B, C) |
