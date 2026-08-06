# Intraday Dual-DB Benchmark: DuckDB vs MongoDB

## Session Context

Built intraday market data infrastructure for Nifty 50 1-min OHLCV data
(96 tickers, 2015–2024, ~76.6M rows). Two databases: DuckDB (time-series
columnar) and MongoDB (NoSQL document), with a unified FastAPI REST API
and comprehensive performance comparison.

## Dataset

| Attribute | Value |
|---|---|
| Tickers | 96 (Nifty 50 stocks + NIFTY50, NIFTYBANK indices) |
| Time range | 2015-01 to 2024-01 |
| Bar interval | 1 minute |
| Fields | date, open, high, low, close, volume |
| Total rows | 76,665,434 |
| Data format | CSV inside zip files (~8 MB each) |
| Source | Indian NSE 1-min OHLCV data |

## Database Details

### DuckDB (Time-Series Columnar)

- Version 1.5.4
- Embedded, single-file: `intraday.duckdb` (~6.2 GB on disk)
- Schema:
  ```sql
  CREATE TABLE intraday (
      ticker    VARCHAR,
      timestamp TIMESTAMP,
      open      DOUBLE,
      high      DOUBLE,
      low       DOUBLE,
      close     DOUBLE,
      volume    BIGINT
  );
  CREATE INDEX idx_ticker_ts ON intraday (ticker, timestamp);
  CREATE INDEX idx_ts ON intraday (timestamp);
  ```

### MongoDB (NoSQL Document)

- Version 7.x (community)
- Database: `intraday`, Collection: `ticks`
- Document structure:
  ```json
  {
    "_id": "RELIANCE_2023-06-01 09:15:00",
    "ticker": "RELIANCE",
    "timestamp": "2023-06-01 09:15:00",
    "open": 2348.5, "high": 2352.3,
    "low": 2347.1, "close": 2350.6,
    "volume": 104030
  }
  ```
- Indexes: `(ticker, timestamp)` unique compound, `timestamp` single-field

### REST API

- Framework: FastAPI + uvicorn on port 8000
- Endpoint: `GET /api/{duckdb|mongodb}/query`
- Parameters: tickers (comma-sep), start, end, fields (comma-sep)

## Ingestion Performance

| Database | Rows | Time | Throughput |
|---|---|---|---|
| DuckDB | 76,665,434 | ~240s* | ~319K rows/s |
| MongoDB | 76,665,434 | 377s | ~203K rows/s |

*DuckDB ingested successfully but hit OOM on index creation (fixed by
reconnecting with `PRAGMA memory_limit='6GB'; PRAGMA threads=4`)

### DuckDB Ingestion — Key Technique

Extract CSV from zip, then use DuckDB's native `read_csv_auto`:

```python
with tempfile.TemporaryDirectory() as tmp:
    for fpath in get_ticker_files():
        # Extract CSV from zip
        with zipfile.ZipFile(fpath) as z:
            z.extract(csv_name, tmp_dir)
        # Bulk insert via native CSV reader
        con.execute(f"""
            INSERT INTO intraday
            SELECT '{ticker}', CAST(date AS TIMESTAMP),
                   CAST(open AS DOUBLE), CAST(high AS DOUBLE),
                   CAST(low AS DOUBLE), CAST(close AS DOUBLE),
                   CAST(volume AS BIGINT)
            FROM read_csv_auto('{csv_path}', header=true)
        """)
```

This processes ~800K rows per file in ~1 second. Row-by-row `executemany`
takes 10x+ longer.

### MongoDB Ingestion — Key Technique

Bulk writes with ordered=False, batch size 20,000:

```python
BATCH_SIZE = 20000
batch = []
for row in reader:
    batch.append(InsertOne({"_id": f"{ticker}_{row['date']}", ...}))
    count += 1
    if len(batch) >= BATCH_SIZE:
        col.bulk_write(batch, ordered=False)
        batch = []
if batch:
    col.bulk_write(batch, ordered=False)
```

## Benchmark Results

### Query Patterns Tested

| Pattern | Description | Expected rows |
|---|---|---|
| 15-min slice | 1 ticker, 15 min | 16 |
| 1 day | 1 ticker, full session (375 min) | 375 |
| 1 month | 1 ticker, 22 trading days | 7,875 |
| 1 year | 1 ticker, ~250 trading days | 91,930 |
| 5 tickers, 1 day | 5 tickers, full session | 1,875 |
| 5 tickers, 1 month | 5 tickers, 22 days | 39,375 |
| 10 tickers, 1 day | 10 tickers, full session | 3,750 |
| Full day all fields | 1 ticker, 1 day, 5 OHLCV fields | 375 |

### Timing (ms) — 5 runs each, warm cache

| Query Pattern | DuckDB | MongoDB | Ratio |
|---|---|---|---|
| Single ticker, 15 min | 0.7 | 0.7 | 1.0x |
| Single ticker, 1 day | 0.9 | 1.7 | 1.9x |
| Single ticker, 1 month | 5.1 | 23.4 | 4.6x |
| Single ticker, 1 year | 40.8 | 149.6 | 3.7x |
| 5 tickers, 1 day | 2.2 | 10.6 | 4.9x |
| 5 tickers, 1 month | 17.3 | 64.5 | 3.7x |
| 10 tickers, 1 day | 4.2 | 14.0 | 3.3x |
| Full day all fields | 0.9 | 2.5 | 2.9x |

### Analysis

**Why DuckDB wins for time-series:**

| Factor | DuckDB | MongoDB |
|---|---|---|
| Storage layout | Columnar (read only requested fields) | Row-based (read whole document) |
| Query execution | Vectorized (batch of rows) | Iterator (one doc at a time) |
| Compression | Column-level (high ratio) | Document-level (limited) |
| Parallelism | Multi-threaded by default | Single-threaded per query |
| Data locality | Sequential scan on contiguous columns | Scattered document access |
| Serialization | Minimal (native binary) | Significant (BSON encode/decode) |

**When MongoDB still makes sense:**
- Schema varies across records
- Documents contain nested sub-structures (order book snapshots)
- Full-document retrieval is common
- Need flexible query patterns beyond time-series

## Hardware

- Mac mini, Apple M1, 16 GB RAM
- macOS 27.0
- Python 3.14.2 (homebrew) / 3.13.12 (conda)
