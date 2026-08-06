# US Macro Primary-Source URL Patterns (verified July 2026)

All fetchable via `curl -s "https://r.jina.ai/https://<url>"` (save to /tmp, then grep).

## Federal Reserve
- **FOMC statement**: `federalreserve.gov/newsevents/pressreleases/monetaryYYYYMMDDa.htm` (e.g. `monetary20260729a.htm`). Decision + vote count near top ("The Committee decided to maintain/raise/lower the target range..."); dissents near bottom ("Voting against the monetary policy action were ..."). Also `monetaryYYYYMMDDa1.htm` = implementation note.
- **SEP projections**: `federalreserve.gov/monetarypolicy/fomcprojtablYYYYMMDD.htm` (e.g. `fomcprojtabl20260617.htm`). Table 1 rows: "Change in real GDP", "Unemployment rate", "PCE inflation", "Core PCE inflation", "Memo: Projected appropriate policy path — Federal funds rate". Each row has a "March projection" comparison line. Median columns per year + longer run. Note: dots are the *midpoint* of the target range at end of calendar year.
- **Balance sheet / QT**: `federalreserve.gov/releases/h41/current/` (H.4.1). Grep "U.S. Treasury securities" and "Mortgage-backed securities" for held-outright + weekly & y/y deltas; "Total assets" for size. Also `federalreserve.gov/monetarypolicy/bst_recenttrends.htm`.
- **Term premium**: `frbsf.org/research-and-insights/data-and-indicators/treasury-yield-premiums/` — Christensen–Rudebusch model, "Most Recent / Last FOMC / 1 year ago" columns; rows "Treasury Yield (Observed)", "Average Expected Overnight Rate", "Term Premium" for 2Y and 10Y. Updated ~daily.

## BLS
- **CPI**: `bls.gov/news.release/cpi.nr0.htm` — headline m/m + y/y in first paragraphs; Table A rows give 6 months of SA m/m + 12-mo NSA.
- **Payrolls**: `bls.gov/news.release/empsit.nr0.htm` — "Both total nonfarm payroll employment (+NNN,000) and the unemployment rate (X.X percent)"; AHE y/y later in release.
- **Release dates**: `bls.gov/schedule/news_release/cpi.htm` (and `empsit.htm`) — exact dates (e.g. June 2026 CPI released Jul. 14, 2026; July 2026 CPI Aug. 12).

## FRED CSV (no key)
`https://fred.stlouisfed.org/graph/fredgraph.csv?id=<SERIES>` → plain CSV, daily or monthly rows.
- DGS10, DFF (effective fed funds), T10YIE (10Y breakeven), UNRATE (monthly), PAYEMS (nonfarm, thousands; month-over-month diff = jobs added).

## CME FedWatch
- Page is client-side JS: r.jina.ai returns only the marketing shell (no probabilities); browser navigation may fail (ERR_HTTP2_PROTOCOL_ERROR). Don't loop retries.
- Working alternatives: server-rendered mirrors `rateprobability.com/fed` (has full meeting table: implied post-meeting rate, hike/cut %, cumulative bps — label "cached, updated 3x/day"), `centralbank.watch`, `fedwatch.com/data`; or news articles quoting FedWatch (Fox/CNBC post-FOMC pieces give the next meeting's split).
- Mirror table format: rows per meeting date; "Implied Rate (Post-Meeting)" ≈ target midpoint; "Δ vs Current (bps)" = cumulative tightening priced.
- **Snapshot drift**: numbers shift within hours (post-decision Sep-hike odds 57.2% → 62.4% a day later). Always state the as-of date; prefer the primary tool's own snapshot if quoted in news.

## ⭐ Atlanta Fed Market Probability Tracker (authoritative Fed pricing — use FIRST)
`atlantafed.org/research-and-data/data/market-probability-tracker` — best Fed-pricing source: derived from CME SOFR options, updated daily from prior-day data, **server-rendered** (charts are Highcharts — full data comes through the Hermes browser accessibility tree, or `browser_console` JS on the SVG). Works when CME FedWatch and every mirror fail. Gives:
- **Hike/cut probability by meeting** (e.g. "Probability of 25bps rate hike by 2026-09-16: 78.27%", with a 6-week daily history series)
- **Target-range distribution per quarterly contract** (4 bars sum to 100: hold 21.7 / +25bp 59.1 / +50bp 17.6 / +75bp 1.6 → expected # hikes by that meeting = Σ p·n)
- **Expected 3M Average SOFR path**: 11 data points = quarterly contracts from the NEXT-expiring contract (point 0 = next contract; values in bp). Derive hike count: avg SOFR ≈ target midpoint + ~2.5bp, so hikes ≈ (path − current midpoint)/25. Example (Jul 30 2026): 3.87 → 4.03 → 4.12 → 4.15 peak → easing = ~1 hike Sep, ~1.5 Dec, ~2 by mid-2027.
- Contract combobox: option VALUES are `contract1..4` (textContent = the date) — a plain `sel.value=` set does nothing; set `selectedIndex` by matching option text, then dispatch `change`.

## Pitfall: rateprobability.com mirrors can serve MONTHS-OLD cached data
The `/fed` page once rendered a stale cache pricing ~2.3 CUTS by Dec-26 (rows for already-past meetings Jan–Jul 2026, "implied" rates contradicting the known holds) while `/ecb` on the same visit was fresh (82% Sep hike, matching the hike regime). Detection heuristics:
- table includes rows for meetings already past, with "implied post-meeting" rates that contradict actual outcomes (e.g. a Jul 29 row "3.22%" when the real hold was 3.625%)
- priced direction flips vs every other source you have (SR3 strip, Atlanta Fed MPT, news)
- header "Showing cached data"
**Always cross-check Fed pricing against Atlanta Fed MPT before trusting any mirror; never blend snapshots across days.**

## Official MPT full history (xlsx) — better than browser scraping for charts
Full daily history (2023→present; 839 dates × 12 quarterly reference windows × ~14 fields) lives in `mpt_histdata.xlsx`:
`https://www.atlantafed.org/-/media/Project/Atlanta/FRBA/Documents/cenfis/market-probability-tracker/mpt_histdata.xlsx`
- **openpyxl fails on it** (KeyError: 'xl/drawings/drawing2.xml' — corrupt drawing reference) → parse sheet XML directly; runnable parser: `scripts/extract_mpt_path.py` (zipfile + regex over sharedStrings + sheet3 rows; ~86k rows in ~1s). Outputs `MPT_sofr_path.csv` (mean/p25/p75 + hike/cut prob per window) and per-window 25bp band distribution.
- DATA sheet layout: A=date (shared string), B=reference_start (Excel serial), C=target_range, D=field, E=value (shared string). Fields: `Rate: mean` / `Rate: 25th percentile` / `Rate: 75th percentile` / `Prob: hike` / `Prob: cut` / `Prob: <lo>bps - <hi>bps`.
- Useful cross-check on band data: Sep-26 window (obs 2026-07-30) = hold 21.15% / +25bp 60.74% / +50bp 18.11% (sums 100); browser chart may show a coarser 4-bar target-range view.

## ECB + FRED bot blocks (EUR/€STR history)
ECB data-api / sdw-ws REST and FRED's `EURIBOR3MD156N` / `EURESTR` return bot-challenge HTML (or empty shell) to curl — even when other FRED graphfred.csv series succeed. Don't retry-loop. EURIBOR 3M daily ≈ last 10 rows + by-year monthly tables on euribor-rates.eu; €STR current level in the rateprobability.com/ecb page header.

## URL discovery one-liner
```bash
curl -s -m 90 -A "Mozilla/5.0" "https://r.jina.ai/https://html.duckduckgo.com/html/?q=<query>" -o /tmp/ddg.txt
grep -o 'uddg=[^"&]*' /tmp/ddg.txt | sed 's/uddg=//' | python3 -c "import sys,urllib.parse; [print(urllib.parse.unquote(l.strip())) for l in sys.stdin]" | sort -u
```

## Worked example — July 2026 FOMC brief
- Task assumed "Powell press conference"; reality: Chair Kevin Warsh (Powell's chair term ended May 2026), 2nd meeting, forward guidance removed. Confirmed via Fox Business + CNBC. **Check leadership/regime before writing.**
- July 29, 2026: HOLD 3.50–3.75% 9–3 (Hammack, Kashkari, Logan dissented for +25bp) — first 3-way unified dissent since Sept 2016. Statement dropped easing language; "The Committee will deliver price stability."
- June 2026 SEP median: fed funds 3.8% end-2026 (i.e. one hike), 3.6% end-2027, LR 3.1%; GDP 2.2/2.3; U-3 4.3/4.3; PCE 3.6/2.3; core PCE 3.3/2.5. PCE 2026 jumped from 2.7 (March) — inflation re-accelerated (Iran conflict energy shock; CPI energy +15.7% y/y, gasoline +26.7%).
- June CPI (Jul 14): −0.4% m/m (largest since Apr 2020), +3.5% y/y; core +2.6% y/y. June payrolls: +57k, U-3 4.2%, AHE +3.5% y/y.
- Market pricing: HIKES not cuts — Sep 57–62% hike, Dec 2026 implied midpoint 3.97% (+34bp), Jun 2027 4.09% (+47bp).
- 10Y 4.67% vs funds 3.63%: FRBSF 10Y term premium 1.31pp (up from 1.16 at June FOMC), breakevens 2.26%, hawkish repricing, Treasury runoff halted Dec 1 2025 (announced Oct 29 2025; "elevated short-term Treasury issuance" cited) while MBS runoff continued (~$8bn/wk); total assets $6.74tn (H.4.1, Jul 29).
- Sell-side: GS Research (Mericle) — no cuts until Jun/Dec 2027, terminal 3–3.25%, hikes "somewhat more likely than initially thought"; MS (Zentner) — "September remains a live meeting"; JPM (Camporeale) — hold through end-2026.
- **What failed**: Reuters live blog via r.jina.ai → 733-byte stub (blocked); CME FedWatch direct (JS shell) and browser navigation (HTTP2 error) → used mirrors + news quotes instead.
