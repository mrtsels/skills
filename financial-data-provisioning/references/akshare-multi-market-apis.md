# AKShare Multi-Market API Reference

> Verified working as of 2026-07-20. AKShare v1.18.64.

## Index Data

| Market | Function | Symbol/Filter | Key Columns |
|--------|----------|---------------|-------------|
| A股 上证指数 | `ak.stock_zh_index_daily("sh000001")` | `sh000001` | date, open, high, low, close, volume |
| A股 深证成指 | `ak.stock_zh_index_daily("sz399001")` | `sz399001` | same |
| A股 沪深300 | `ak.stock_zh_index_daily("sh000300")` | `sh000300` | same |
| A股 创业板指 | `ak.stock_zh_index_daily("sz399006")` | `sz399006` | same |
| 港股 恒生指数 | `ak.stock_hk_index_daily_em("HSI")` | `HSI` | index, date, open, high, low, latest |
| 港股 国企指数 | `ak.stock_hk_index_daily_em("HSCEI")` | `HSCEI` | same |
| 美股 标普500 | `ak.index_global_spot_em()` | 名称=="标普500" | 最新价, 涨跌额, 涨跌幅, 开盘价, 最高价, 最低价, 昨收价 |
| 美股 纳斯达克 | `ak.index_global_spot_em()` | 名称=="纳斯达克" | same |
| 美股 道琼斯 | `ak.index_global_spot_em()` | 名称=="道琼斯" | same |
| 韩国 KOSPI | `ak.index_global_spot_em()` | 名称=="韩国KOSPI" | same |
| 韩国 KOSPI200 | `ak.index_global_spot_em()` | 名称=="韩国KOSPI200" | same |

### Notes on index_global_spot_em()

Returns a DataFrame with ALL global indices (~500 rows). Filter by exact 名称. Available indices include:
- 标普500, 纳斯达克, 道琼斯, 韩国KOSPI, 韩国KOSPI200
- 日经225, 澳大利亚标普200, 德国DAX, 法国CAC40, 英国富时100
- 加拿大S&P/TSX, 印度孟买SENSEX, 恒生指数 (not available here — use `stock_hk_index_daily_em` instead)

## Individual Stock Data

### US Stocks

```python
# Daily history — preferred for per-ticker analysis
df = ak.stock_us_daily(symbol="NVDA", adjust="qfq")
# Returns: date, open, high, low, close, volume
# adjust options: "qfq" (前复权), "hfq" (后复权), "" (不复权)

# Real-time spot — AVOID for bulk, use for single lookup only
# ak.stock_us_spot_em()  # ⛔ loads 5500+ stocks, tqdm timeout risk
```

Rate limit: add `time.sleep(0.5)` between tickers. 2s is safer for a full basket.

### Pre-verified US Ticker → THSCODE Mapping

For use with thsdk (guest account limited — prefers ETFs over stocks):

| Ticker | thsdk search result (guest) | ⚠️ |
|--------|----------------------------|-----|
| AAPL | 每日2倍做多苹果ETF (wrong) | Use AKShare instead |
| MSFT | 微软每日2倍做多ETF (wrong) | Use AKShare instead |
| NVDA | 英伟达 (correct) | Data still returns "?" |

### HK Stocks

```python
# Real-time spot (all HK stocks)
df = ak.stock_hk_spot_em()
# Filter by 代码 or 名称
```

## Sub-Sector Organization

Common US tech sub-sectors for basket analysis:

| Sub-Sector | Tickers |
|------------|---------|
| 智能手机/消费电子 | AAPL |
| 大型科技/互联网 | MSFT, GOOGL, AMZN, META |
| 半导体 | NVDA, AVGO, AMD, TSM, INTC, MU, QCOM |
| 云计算/SaaS | CRM, NOW, ADBE, ORCL, WDAY |
| 网络安全 | CRWD, PANW, FTNT, ZS |
| 电动车 | TSLA, RIVN, LI |
| AI/软件 | PLTR, SNOW, DDOG, MDB |
| 硬件/数据中心 | DELL, SMCI, MRVL |
