# Market Daily Review — Structural Template

Source session: jul-20.md (July 17, 2026 global market selloff)

## Document Layout

```
# {Date} Market Review

> Date recorded / Data as of

## A股（China）— table
## 港股（HK）— table  
## 美股（US）— table [+ sub-sector breakdowns]
## 韩国（Korea）— table

## 小结

### Global Context
### Per-Market Analysis
### Policy/Event Catalyst Analysis  ← key: search news for explanatory factors
### Core Conclusions (3-5 numbered)
```

## Data Sources

| Source | Use For | Notes |
|--------|---------|-------|
| `akshare.stock_zh_index_daily` | A-share indices | Date column from reset_index() |
| `akshare.stock_us_daily(symbol, adjust="qfq")` | Individual US stocks | Ticker-based, reliable |
| `akshare.stock_hk_index_daily_em("HSI")` | HSI | Date + latest columns |
| `akshare.index_global_spot_em()` | KOSPI, S&P 500, Nasdaq, Dow | Filter by "名称" column |
| AP News (browser) | News context | AP blocks fewer bots than Google/Bing |

## Sub-sector Breakdown Pattern

When drilling into US tech, group stocks into logical sub-sectors. Call out:
- **Winners** (stocks/industries that bucked the trend)
- **Losers** (worst performers)
- **Divergences** (sub-sectors moving opposite directions = narrative signal)

## Policy Impact Table Format

Use for any policy/event catalyst:

```
| Dimension | Effect | Direction |
|-----------|--------|----------|
| HK equities sentiment | Short-term positive, sanctions relief | Bullish |
| A-share foreign inflows | Sentiment boost, limited substance | Neutral-positive |
| Core trade status | Not restored, structural issue remains | Bearish overhang |
```

## Analytical Style (user preference)

- Lead with **data tables** (raw facts first)
- Follow with **layered logical analysis** — connect dots across markets and sub-sectors
- Integrate **news/policy context** — search for explanatory factors published contemporaneously
- End with **actionable/testable conclusions**, not restatements of data
