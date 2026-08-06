# Live market-data sources (US / rates) — verified 31 Jul 2026

All curl-able without API keys. Pattern that worked end-to-end on the Task-5
rates deck (Fed funds/SOFR/ECB levels, curves, futures quotes, policy pricing).

## 1. FRED CSV endpoint (no key) — the workhorse for hard numbers

```
curl -s "https://fred.stlouisfed.org/graph/fredgraph.csv?id=<SERIES>" -o <SERIES>.csv
# returns: DATE,VALUE  (daily; DGS* are business-daily, ECBDFR steps on change days)
```

Useful series (all verified live):
| Series | What it is |
|---|---|
| `EFFR` | effective fed funds rate, daily |
| `SOFR` | SOFR, daily |
| `DFEDTARU` / `DFEDTARL` | fed funds target range upper / lower (daily; changes = policy moves) |
| `DFF` | daily fed funds effective (same as EFFR) |
| `DGS3MO` `DGS6MO` `DGS1` `DGS2` `DGS5` `DGS10` `DGS30` | Treasury constant-maturity yields |
| `T10Y2Y` | 10Y−2Y spread |
| `ECBDFR` | ECB deposit facility rate (daily; changes = ECB moves) |
| `WFII10` | ACM 10y term premium estimate |

Worked analysis pattern (pandas):
- Policy path: diff on DFEDTARU → list of target-range changes with dates (don't
  eyeball; the monthly EFFR average can sit *below* the lower bound on
  quarter-end days — the range series is the ground truth, not EFFR).
- Monthly averages: `df.groupby(df.date.dt.to_period("M")).value.mean()`.
- Curve snapshot: last value on-or-before a date per maturity → compare y/y.

## 2. NY Fed reference rates (EFFR/SOFR daily tables incl. VOLUME)

- `https://www.newyorkfed.org/markets/reference-rates/effr`
- `https://www.newyorkfed.org/markets/reference-rates/sofr`
via `r.jina.ai` gives the full table: `DATE | RATE | 1ST | 25TH | 75TH | 99TH PCTL | VOLUME ($B) | TARGET RANGE`.
Volume stats are gold for decks: EFFR ≈ $100bn/day vs SOFR ≈ $3,000bn/day (Jul-2026).

## 3. CME contract specs & quotes (via r.jina.ai — page is JS but jina renders it)

- Specs: `https://www.cmegroup.com/markets/interest-rates/stirs/three-month-sofr.contractSpecs.html`
  Official SR3 facts: contract unit **$2,500 × contract-grade IMM Index**; price = 100 − R
  (R = business-day compounded SOFR, act/360, over Reference Quarter = 3rd Wed of 3rd month
  prior → 3rd Wed of delivery month); tick 0.0025 = $6.25 (≤4 months to expiry) else 0.005 = $12.50;
  **39 quarterly + 6 serial months**; **last trading day = business day PRIOR to the 3rd Wednesday**.
- Quotes: `.../three-month-sofr.quotes.html` (last price, change, volume, timestamp).
- Rule 460 (settlement wording): `https://www.cmegroup.com/content/dam/cmegroup/rulebook/CME/IV/400/460.pdf` via jina.
- **CME margin API returns 422** (HTTP/2 stream error) — do NOT build a loop on it; use
  broker/third-party estimates clearly labeled, or CME's own `.../three-month-sofr.margins.html`.

## 4. Eurex / ICE futures (EUR)

- Eurex Three-Month €STR futures product code is **FST3** (not FESTR); page
  `https://www.eurex.com/ex-en/markets/int/mon/3m-euro-str-futures/estr/Three-Month-Euro-STR-Futures-3402480`
  via jina → full settlement table (contract | settle | volume | OI) + total volume/OI.
  Also: **ECB-Dated €STR futures (FEMP)** launched Dec-2025 (ECB-meeting-date hedging).
- ICE 3M EURIBOR futures (F3M): `https://www.ice.com/products/28/Three-Month-Euribor-Futures`
  (product page; quotes need JS — use EURIBOR cash fixings instead, see below).
- EURIBOR fixings (1W/1M/3M/6M/12M): `https://www.euribor-rates.eu/en/current-euribor-rates/`
  via jina — plain table. EURIBOR 3M − €STR ≈ the panel/credit premium.

## 5. FedWatch-style meeting-by-meeting pricing (hike/cut probabilities)

- `https://rateprobability.com/fed` and `https://rateprobability.com/ecb` via jina —
  table: `Meeting | Implied Rate (post) | P(Hike/Cut) | # hikes priced | Δbp`.
  CME's own FedWatch tool is JS-heavy; rateprobability mirrors it and is curl-friendly.
  Reads like: "Sep-26 62.4% hike · Dec-26 1.38 hikes (+34bp) · peak 4.09% mid-2027".

## 6. BLS releases (CPI/payrolls) — y/y number

`https://www.bls.gov/news.release/cpi.nr0.htm` via jina, then grep
`increased [0-9.]+ percent over the last 12 months` — first hit = headline CPI-U y/y;
core/other indexes appear further down. Payrolls/U-rate: same page pattern or BLS news
release for employment situation.

## 7. Sell-side views / news

- Goldman insights: `https://www.goldmansachs.com/insights/articles/<slug>` via jina (works).
- FOMC/ECB statements: federalreserve.gov `fomcprojtabl20260617.htm` (SEP tables — grep
  `Federal funds rate |` row: median dots by year), ecb.europa.eu press releases (URLs carry
  a hash — see euro-area-rates-data-sources.md for the include-file trick).

## Failure/fallback map (verified 31 Jul 2026)

| Source | Failure | Fallback |
|---|---|---|
| investing.com | 403 via jina (DDoS protection) | euribor-rates.eu / rateprobability / exchange sites directly |
| barchart.com futures quotes | 404 via jina for `SR3*0` style URLs | CME/Eurex official quote pages |
| ECB SDW / data-api.ecb.europa.eu | 400 "access blocked" from some networks | ECB press pages via jina, tradingeconomics, rateprobability |
| CME margin API | 422 | broker estimates (label as such) + CME margins page |
| jina on heavy pages | 15s networkidle timeout | plain `curl -A "Mozilla/5.0"` direct |

## Deck-pipeline notes (see SKILL.md variant section)

- Keep every fetched page as `/tmp/<name>.txt` (curl -o) — survives subagent timeouts.
- Put all verified numbers in one `R` object, `rd(v, fb)` guard, rebuild = one command.
- Chart annotations: place labels in empty curve areas (above the band), never across data lines.
