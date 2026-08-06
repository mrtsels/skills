# US Stock Data via Akshare (Fallback from thsdk)

## When to use

thsdk 游客账户在 US 股票数据上有严重限制：
- `market_data_us()` 返回全 `"?"` 
- `search_symbols()` 返回杠杆 ETF 而非正股（搜索"苹果"返回"每日2倍做多苹果ETF"）
- 新 IPO 公司（如 SPCX）thsdk 完全找不到

出现上述情况时，直接切换到 akshare。

## 单只股票日线

```python
import akshare as ak

df = ak.stock_us_daily(symbol="AAPL", adjust="qfq")  # adjust: qfq=前复权, hfq=后复权
df = df.reset_index()
last = df.iloc[-1]
prev = df.iloc[-2] if len(df) >= 2 else last
close = float(last["close"])
prev_close = float(prev["close"])
chg = close - prev_close
pct = (chg / prev_close) * 100
date = str(last["date"])[:10]  # 日期在 reset_index 后为 date 列
print(f"{close:.2f}  {chg:+.2f} ({pct:+.2f}%) [{date}]")
```

## 批量获取多只股票

```python
tickers = ["AAPL", "MSFT", "NVDA"]
for t in tickers:
    df = ak.stock_us_daily(symbol=t, adjust="qfq")
    df = df.reset_index()
    last = df.iloc[-1]
    ...
    time.sleep(0.5)  # 限速，避免被 ban
```

## 注意事项

- `stock_us_spot_em()` 下载全量 US 股票（5500+ 只），**极慢**（每次约 90+ 秒），不要用
- 逐只调用 `stock_us_daily()` 单次约 1-2 秒，30 只以内可行
- 新 IPO 的 ticker 可能暂时查不到，需等待数据源更新
- A-share 指数：`ak.stock_zh_index_daily(symbol="sh000001")`
- HK 指数：`ak.stock_hk_index_daily_em(symbol="HSI")` 
- 全球指数行情：`ak.index_global_spot_em()`（包含 KOSPI、标普、纳指等）
- thsdk 投资者账户不受这些限制，但需要自行配置 username/password
