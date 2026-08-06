# Rates & Policy Data — Source Playbook (verified Jul 2026)

Condensed playbook for fetching CURRENT rates/policy data for reports and decks.
Every source below was actually used and returned data on 30–31 Jul 2026.
Rules: fetch live, never quote from memory; sanity-check every number's date.

## 1. FRED CSV (bulk history, no API key)

```
curl -s "https://fred.stlouisfed.org/graph/fredgraph.csv?id=<ID>" -o <id>.csv
# header: date,value ; daily rows, most series start 1950s-2000s
```

| Series ID | Meaning | Notes |
|---|---|---|
| EFFR | Effective fed funds rate (daily) | ~$100bn/day market |
| SOFR | Secured overnight financing rate (daily) | ~$3.0T/day market |
| DFF | Fed funds effective (daily, alt source) | same as EFFR |
| DFEDTARU / DFEDTARL | Target range upper / lower | **The policy path** — diff to find each FOMC move |
| DGS3MO, DGS6MO, DGS1, DGS2, DGS5, DGS10, DGS30 | Treasury constant-maturity yields | curve snapshots |
| T10Y2Y | 10Y − 2Y spread | steepness history |
| ECBDFR | ECB deposit facility rate | step series; check date of last change (may be a HIKE — verify direction from data, don't assume) |
| WFII10 | ACM 10y term premium | long-end story |

Patterns that work:
- Policy path: `tar["chg"] = df["value_u"].diff().ne(0)` then filter — do NOT use awk (this session's awk printed 2008-era changes instead of recent ones).
- Curve y/y change: take last value ≤ date-365 for each DGS series.
- Monthly averages: `df.groupby(df.date.dt.to_period("M"))["value"].mean()`.
- EFFR can print below the target range on a few month-end days (plumbing artifact, worth one footnote, not a policy signal).

## 2. NY Fed reference rates (latest print + VOLUME)

- `newyorkfed.org/markets/reference-rates/effr` — table: DATE | RATE | 1ST/25TH/75TH/99TH PERCENTILE | VOLUME | TARGET RANGE
- `newyorkfed.org/markets/reference-rates/sofr` — same shape, no target range column
- SOFR volume ≈ $3.0T vs EFFR ≈ $100bn (30× — a headline stat for benchmark slides).

## 3. Meeting-by-meeting policy pricing (best free FedWatch)

- `rateprobability.com/fed` — table per FOMC meeting: Implied Rate (post-meeting), Probability of Hike(Cut), # of Hikes(Cuts), Δ vs Current (bps). Example output shape (30 Jul 2026):
  `Sep 16, 2026 | 3.78% | 62.4% | 0.62 | 15.6` ... `Dec 09, 2026 | 3.97% | 37.2% | 1.38 | 34.4`
- `rateprobability.com/ecb` — same for ECB meetings; also lists DFR/MRO/MLF and **Last €STR**.
- Note: this is one vendor's model of 30d-futures-implied odds; label as "FedWatch-style pricing", not official CME FedWatch.

## 4. EUR money-market levels

- `euribor-rates.eu/en/current-euribor-rates` — EURIBOR 1W/1M/3M/6M/12M table (plain HTML, jina-friendly).
- €STR level: rateprobability.com/ecb shows "Last €STR" (e.g. 2.185%); €STR typically trades a few bp BELOW the deposit rate (≈ DFR − 6bp). EURIBOR 3M − €STR ≈ 27bp = panel/credit premium (partly forward-looking).

## 5. CME futures (specs / quotes / settlements)

Base URL pattern: `cmegroup.com/markets/interest-rates/stirs/three-month-sofr.<page>.html`
- `.contractSpecs.html` — full spec table. Verified SR3 facts (Jul 2026): contract unit **$2,500 × contract-grade IMM Index** (NOT "$1M notional" — official wording); price = 100 − R, R = business-day compounded SOFR over the Reference Quarter (3rd Wed of 3rd month prior → 3rd Wed of delivery month); tick 0.0025 = $6.25 (≤4 months to expiry) / 0.005 = $12.50; **39 quarterly + 6 serial months**; last trading day = business day BEFORE the 3rd Wednesday (not the IMM date itself); cash-settled, final 100 − R on last trading day.
- `.quotes.html` — current quotes (via r.jina.ai); e.g. `SR3Z6 last 95.96, volume 43,123` (Z6 = Dec-26; letter = month, digit = year).
- `.settlements.html`, `.volume_oi.html` — settlements and volume/OI.
- 1M SOFR (SR1): `one-month-sofr.contractSpecs.html` — unit $4,167 × IMM Index, arithmetic (not compounded) SOFR average settlement.
- Margin: CME's own `CmeWS/mvc/...` API returns HTTP 422; use broker pages (e.g. `help.metrotrade.com/kb/three-month-sofr-futures-sr3-contract-specifications`: SR3 IM ≈ $300–600, MM ≈ $270–550, "varies with volatility") — label as broker estimates.
- Rulebook PDF: `cmegroup.com/content/dam/cmegroup/rulebook/CME/IV/400/460.pdf` (via r.jina.ai) — exact final-settlement wording.

## 6. Eurex €STR futures (FST3)

- Product page: `eurex.com/ex-en/markets/int/mon/3m-euro-str-futures/estr/Three-Month-Euro-STR-Futures-3402480` (via r.jina.ai) — quotes table (Monthly contracts, settle prices per IMM date) + total volume/OI.
- Product code is **FST3** (Three-Month Euro STR Futures), not "FESTR". Also: ECB-Dated €STR futures (FEMP) launched Dec-2025 for ECB-meeting hedging, Prisma-margined.
- ICE EURIBOR 3M futures code: **F3M** (ice.com product page is nav-heavy; contract unit €1M, tick 0.005 = €12.50, 1bp = €25 — standard contract knowledge).

## 7. Central-bank documents

- FOMC SEP: `federalreserve.gov/monetarypolicy/fomcprojtablYYYYMMDD.htm` — grep the markdown tables: `| Federal funds rate | 3.8 | 3.6 | 3.4 | 3.1 |` = median dots 2026/2027/2028/longer-run. Compare with the "March projection" row for the revision.
- FOMC statement coverage: news wire via r.jina.ai (foxbusiness.com worked; Reuters often paywalls).
- BLS CPI: `bls.gov/news.release/cpi.nr0.htm` — grep `increased X percent over the last 12 months` for headline y/y; also m/m SA line.
- ECB statements: `ecb.europa.eu/press/govcdec/mopo/html/ecb.mpYYMMDD.en.html` via r.jina.ai (e.g. ecb.mp260723.en.html); presser transcripts have "START: ..." marker.
- ECB data portal / SDW REST: blocks automated curl (HTTP 400 "access has been blocked due to security concerns") — route around it (rateprobability, euribor-rates.eu, tradingeconomics).

## 8. Subagent research briefs — proven template

Each parallel leaf subagent gets: (1) today's date; (2) verified baseline facts (target range, latest prints) so it doesn't re-derive or contradict; (3) numbered questions; (4) the zero-fabrication rule: *"every number MUST be sourced to a URL you actually fetched — curl with r.jina.ai/URL prefix or the browser; if you cannot verify a number, mark it UNVERIFIED and say what you found instead; do NOT invent levels"*; (5) output format: compact markdown brief, numbers + source URLs. Split by domain: (a) US policy/outlook, (b) futures quotes/specs/margins (slowest — has to hit many pages), (c) EUR policy/outlook. When a task times out, recover from its log + /tmp files instead of rerunning.

## 9. Deck slides that consume this data

See the `finance-deck-build` skill: RESEARCH-object + rd() guard pattern, matplotlib dual SVG/PNG export, validate → soffice → pdftoppm → vision QA loop, and the slide-layout pitfalls (chip-stack overflow, table cell-count mismatches, narrow bullet columns).
