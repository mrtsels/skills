---
name: python-code-conventions
description: Python code style conventions for this user's quant assignments — no AI-isms, minimal comments, clean tests.
---

# Python Code Conventions

## No AI-isms in code

- No A/B/C/D section labels in comments
- No `# Create a function that...` or `# Given a sector, return...` explanations
- No docstrings that restate obvious code logic — function name IS the doc for simple functions
- No section-separator comment lines (`# A)`, `# ---`, etc.)
- Type hints where helpful, otherwise minimal
- No verbose print statements for production code (print progress for data collection scripts is fine)

## Assignment patterns

### Flask REST API (Question 1)
- Read CSV once at module level with pandas
- `/Sector` returns sorted unique sectors as JSON
- `/EBITDA` accepts `?Sector=` query param, returns integers (cast with `astype(int)` after `dropna()`)
- Missing param → 400 with error JSON
- Invalid sector → empty `[]`
- Wrap `app.run()` in a `main()` function per assignment requirements

### Dash Dashboard (Question 2)
- No direct CSV loading — query Flask API via `requests`
- `_sectors` populated at module level via `requests.get("/Sector")`
- Use `dmc.MultiSelect` for sector selection
- `dcc.Graph(id="pie-chart")` in layout
- Callback sums EBITDA per sector, plots pie chart
- Edge case: empty selection → `go.Figure()` (empty chart)
- Edge case: sector with zero/total-zero data → skip that sector

## Data pipeline patterns

### yfinance + MongoDB batch fetch

For fetching and storing historical stock data:

**Proxy env vars:** macOS profiles often set `http_proxy`/`https_proxy`. yfinance (via requests) picks these up and fails with `ConnectionError: Remote end closed connection without response`. Always clear at script top:

```python
import os
os.environ.pop('http_proxy', None)
os.environ.pop('https_proxy', None)
os.environ.pop('HTTP_PROXY', None)
os.environ.pop('HTTPS_PROXY', None)
```

**Batch download (fast):** `yf.download()` with multiple tickers is 30–50x faster than looping `yf.Ticker(t).history()` per stock. Use `group_by="ticker"`, `threads=False`:

```python
data = yf.download(tickers, start="2010-01-01", group_by="ticker", threads=False, progress=False)
```

When `group_by="ticker"` and multiple tickers, `data.columns` is a MultiIndex with levels `(Ticker, Price)`. Extract per-stock:

```python
if isinstance(data.columns, pd.MultiIndex):
    df = pd.DataFrame({
        'Close': data.get((yf_ticker, 'Close'), pd.Series(dtype=float)),
    }).dropna(subset=['Close'])
```

**Batch size:** 50 tickers per batch. Rate-limit: 1 second between batches.

**MongoDB bulk write:** Use `InsertOne` or `UpdateOne` with `ordered=False` for upsert, `bulk_write()` for throughput:

```python
from pymongo import InsertOne
ops = [InsertOne({"_id": f"{code}_{date}", **record}) for record in records]
col.bulk_write(ops, ordered=False)
```

**Aggregation over find_one loops:** When you need the latest date per stock, use a single aggregation pipeline instead of `col.distinct("code")` + per-stock `find_one()`:

```python
pipeline = [
    {"$group": {"_id": "$code", "last_date": {"$max": "$date"}}},
    {"$match": {"last_date": {"$lt": today}}},
]
need_update = [doc["_id"] for doc in col.aggregate(pipeline, allowDiskUse=True)]
```

**Gotcha: `$in` in aggregation.** The `{"$in": codes}` syntax requires `codes` to be a Python list, not a numpy array or generator. When using `$in` with numerical codes in shell-quoted strings, the `$` signs can cause shell interpolation — construct the pipeline programmatically, not via f-strings.

**Gotcha: column types from pivot_table.** `pivot_table(index="date", columns="code", values="close")` with integer codes produces int64 column dtype. Access with `pivot[600000]` (int) not `pivot["600000"]` (str). When code comes from CSV, force type with `str(int(c1))` or use `iloc` + `col_map` dict for positional access.

**Gotcha: pandas iloc bracket order.** In pandas 3.x, `iloc[row_range, col_idx]` uses `]` for both dimensions. Common mistake: `iloc[0:10, col_map[c1)]` → SyntaxError. Correct: `iloc[0:10, col_map[c1]]`.

**Resume / incremental mode:** Store a CSV of the stock list (`sse_stocks.csv`) so AKShare is only needed once. For update scripts, use aggregation to find stocks with `last_date < today` rather than iterating all codes.

## Statistical arbitrage pipeline (SSE China)

4-script pipeline for pair trading on A-share data:

### Script sequence

**`correlation.py`** — correlation matrix from MongoDB → `correlation.npy`
- Log returns: `np.log(prices / prices.shift(1))`
- Pearson: `returns.corr().values`
- Load all prices via single aggregation query, not per-stock loops

**`clustering.py`** — Ward hierarchical clustering → `clusters.csv`
- `squareform(1 - corr)` → `linkage(dist, method="ward")` → `fcluster(Z, t=K)`

**`strategy.py`** — Engle-Granger cointegration → `pairs.csv`
- OLS: `np.linalg.lstsq(X, y1)` → residual
- ADF: `adfuller(residual, maxlag=1, autolag=None)` — conservative (fixed lag 1)
- Zero-crossings: `sum(z[t] * z[t-1] < 0 for t in range(1, len(z)))`
- Pipeline: per-cluster → corr > 0.3 → ADF p < 0.05 → sort by zero-crossings → top 30

**`backtest.py`** — rolling 2Y+1Y backtest → `equity_curve.csv`
- Windows: `pd.date_range(start + DateOffset(years=2), end, freq="YE")`
- No look-ahead bias: re-select pairs each window on training data only
- Rules: |Z| > 2 enter, |Z| < 1 exit, |Z| > 3 for 5 days stop
- Position: 2% per pair, max 20 concurrent, cost 0.13%
- Column access: `col_map = {c: df.columns.get_loc(c) for c in codes}` + `iloc[row, col_map[c]]` avoids dtype issues
- Rolling Z-score std: slice `t-lookback:t` on both price series

### ADF gotcha

`adfuller(residual, maxlag=1, autolag=None)` is conservative. Fewer pairs pass vs auto-lag (AIC default). If too few pairs, omit `autolag` parameter.

### Output artifacts

```
correlation.npy    — N×N matrix
clusters.csv       — code, cluster label
pairs.csv          — cointegrated pairs with beta, zero-crossings
equity_curve.csv   — daily NAV
backtest_results.csv — per-trade PnL
```

## No shebang lines

Do not include `#!/usr/bin/env python3` in `.py` files. The user works across macOS and Windows; shebangs are Unix-only. If a file has one, remove it.

## English-only in scripts

All `print()`, comments, docstrings, and error messages in `.py` files must be in English. Chinese may appear in `.md` documentation or notebook cells, but never in Python source. Even if the user is writing in Chinese, script output stays English.

## Methodology docs: formulas + tables only

For documentation files (methodology.md etc.):
- Only formulas, code blocks, and parameter tables
- No explanatory prose ("this means that", "because of", "note that")
- No slide outlines or conclusion sections
- Each section: formula → optional code → optional table. Nothing else.

## Slides: reference scripts, not code blocks

When writing slide content (slides.md):
- Mention script name and function/constant name: `correlation.py — compute_correlation()`
- No ```python code blocks
- One-liner core logic snippets OK if they fit on one line (e.g. `df.corr().values`)

## Verification checklist
1. Syntax check: `python3 -m py_compile file.py`
2. CSV integrity: rows, columns, null counts, sector coverage
3. API live test: `/Sector` returns data, `/EBITDA` with valid/invalid/missing params
4. Dashboard: curl health check (HTTP 200)
5. Edge cases: missing params, invalid sector, empty selection
