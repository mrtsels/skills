# akshare 指数/个股数据 Fallback 参考

当 thsdk 游客账户返回 `QueryData错误:not data`（常见于 `market_data_index` 和指数 `klines`），或 US 个股查询返回空/错误标的时，切换 akshare 获取。以下函数均经过实测验证。

## A股大盘指数

```python
import akshare as ak

indices = {
    "上证指数": "sh000001",
    "深证成指": "sz399001",
    "沪深300": "sh000300",
    "创业板指": "sz399006",
    "科创50": "sh000688",
    "上证50": "sh000016",
    "中证500": "sh000905",
}

for name, code in indices.items():
    df = ak.stock_zh_index_daily(symbol=code)
    df = df.reset_index()
    last = df.iloc[-1]
    prev = df.iloc[-2] if len(df) >= 2 else last
    close = float(last["close"])
    prev_close = float(prev["close"])
    chg = close - prev_close
    pct = (chg / prev_close) * 100
    date = str(last["date"])[:10]
    print(f"{name}: {close:.2f}  {chg:+.2f} ({pct:+.2f}%) [{date}]")
```

- 返回字段：`date`, `open`, `high`, `low`, `close`, `volume`
- 需 `reset_index()` 将日期索引变为列
- 数据从 2000 年左右开始

## 港股指数

```python
# 恒生指数
df = ak.stock_hk_index_daily_em(symbol="HSI")
df = df.reset_index()
last = df.iloc[-1]
prev = df.iloc[-2]
close = float(last["latest"])
pct = (close - float(prev["latest"])) / float(prev["latest"]) * 100
print(f"恒生指数: {close:.2f} ({pct:+.2f}%) [{last['date']}]")

# 国企指数 (HSCEI)
df2 = ak.stock_hk_index_daily_em(symbol="HSCEI")

# 恒生科技指数
df3 = ak.stock_hk_index_daily_em(symbol="HSTECH")
```

- 返回字段：`index`, `date`, `open`, `high`, `low`, `latest`
- `symbol` 参数值：`"HSI"`(恒生)、`"HSCEI"`(国企)、`"HSTECH"`(科技)

## 全球指数实时快照（美股、韩国、日本等）

```python
df = ak.index_global_spot_em()
```

返回所有全球指数的实时快照，含 `名称`、`最新价`、`涨跌额`、`涨跌幅` 等字段。

| 指数 | 名称筛选 |
|------|----------|
| 标普500 | `df[df["名称"] == "标普500"]` |
| 纳斯达克 | `df[df["名称"] == "纳斯达克"]` |
| 道琼斯 | `df[df["名称"] == "道琼斯"]` |
| KOSPI | `df[df["名称"] == "韩国KOSPI"]` |
| KOSPI200 | `df[df["名称"] == "韩国KOSPI200"]` |
| 日经225 | `df[df["名称"] == "日经225"]` |
| 恒生指数 | `df[df["名称"] == "恒生指数"]` |

## 美股指数历史日线

```python
df = ak.index_us_stock_sina()
# 固定返回 S&P 500 完整历史日线
# 字段：date, open, high, low, close, volume, amount
# ⚠️ 该函数无 symbol 参数，固定为标普500。获取纳斯达克/道琼斯请用 index_global_spot_em()
```

该函数无参数，固定返回 S&P 500 历史数据。最新一个交易日的数据在 `df.iloc[-1]`。

## 全球指数历史日线

```python
import akshare as ak
df = ak.index_global_hist_em(symbol="KOSPI", start_date="20260710", end_date="20260717")
```

`symbol` 取值参考 `index_global_name_table()`。

## 美股个股日线（thsdk US stock 查询失败时首选）

thsdk 游客账户搜索 US 个股常返回杠杆 ETF 或错误标的（例如搜索 "苹果" 返回 "每日2倍做多苹果ETF"），且 `market_data_us` 返回全 `"?"`。此时用 akshare 逐只获取：

```python
import akshare as ak
import time

tickers = ["AAPL", "MSFT", "NVDA", "TSLA", "GOOGL", "AMZN", "META",
           "AVGO", "AMD", "TSM", "INTC", "MU", "QCOM", "CRM", "NOW",
           "ADBE", "ORCL", "WDAY", "CRWD", "PANW", "FTNT", "ZS",
           "RIVN", "LI", "PLTR", "SNOW", "DDOG", "MDB",
           "DELL", "SMCI", "MRVL",
           # 存储板块
           "WDC", "STX", "NTAP", "HPE", "QMCO"]

for ticker in tickers:
    df = ak.stock_us_daily(symbol=ticker, adjust="qfq")
    df = df.reset_index()
    last = df.iloc[-1]
    prev = df.iloc[-2]
    close = float(last["close"])
    pct = (close / float(prev["close"]) - 1) * 100
    date = str(last["date"])[:10]
    print(f"{ticker}: ${close:.2f} ({pct:+.2f}%) [{date}]")
    time.sleep(0.5)  # 限流保护
```

> `adjust` 参数：`"qfq"`(前复权)、`"hfq"`(后复权)、`""`(不复权)
>
> ⛔ **不要用 `stock_us_spot_em()` 批量拉取个股**——它下载全量 5500+ 只美股，tqdm 进度条在非交互式 shell 中约 2min+ 超时。逐只 `stock_us_daily` 每只约 1s，更可控。

## 新股/新上市公司代码查询

刚 IPO 的公司 akshare/thsdk 可能还不知道其代码。使用浏览器访问 Yahoo Finance 查找：

1. 搜索 `finance.yahoo.com/lookup?s=公司名`
2. 从结果列表中获取正确的美股代码
3. 再回 akshare 用 `stock_us_daily(symbol=找到的代码, adjust="qfq")` 获取数据

**已知新上市公司：**
- **SpaceX**: 代码 `SPCX` (Space Exploration Technologies Corp.)，NasdaqGS 上市
- 其他新 IPO 需通过 Yahoo Finance lookup 确认

## 美股子板块分组查询模式

当需要按子板块分析美股科技板块（如每日大盘回顾中的板块细分），按子板块分组逐只查询：

```python
import akshare as ak
import time

sectors = [
    ("大型科技/互联网", ["AAPL", "MSFT", "GOOGL", "AMZN", "META"]),
    ("半导体", ["NVDA", "AVGO", "AMD", "TSM", "INTC", "MU", "QCOM"]),
    ("云计算/SaaS", ["CRM", "NOW", "ADBE", "ORCL", "WDAY"]),
    ("网络安全", ["CRWD", "PANW", "FTNT", "ZS"]),
    ("电动车", ["TSLA", "RIVN", "LI"]),
    ("AI/软件", ["PLTR", "SNOW", "DDOG", "MDB"]),
    ("硬件/数据中心", ["DELL", "SMCI", "MRVL"]),
    ("存储", ["WDC", "STX", "NTAP", "HPE", "QMCO"]),
    ("航天", ["SPCX"]),
]

print("=== 美股科技板块 — 涨跌幅 ===")
for sector_name, tickers in sectors:
    print(f"\n{sector_name}:")
    for ticker in tickers:
        df = ak.stock_us_daily(symbol=ticker, adjust="qfq")
        df = df.reset_index()
        last = df.iloc[-1]
        prev = df.iloc[-2]
        close = float(last["close"])
        pct = (close / float(prev["close"]) - 1) * 100
        date = str(last["date"])[:10]
        print(f"  {ticker:6s}: ${close:>8.2f} ({pct:+.2f}%) [{date}]")
        time.sleep(0.5)
```

> ⚠️ **Pitfall：部分股票可能返回旧数据（交易暂停/退市）。**
> 例如 `PSTG (Pure Storage)` 在 2026-07 查询时仅返回 2026-04 数据，疑似停牌。
> 处理方式：检查返回的日期列，若与预期最后一个交易日差距超过 5 个交易日，
> 标记为"数据异常/疑似停牌"并尝试其他数据源验证。

## 多市场大盘回顾的数据方案

当用户要求跨市场大盘回顾时，采用以下混合方案（按市场优先级排列）：

当用户要求跨市场大盘回顾时，优先采用以下混合方案：

| 市场 | 方法 | 说明 |
|------|------|------|
| A股指数 | `ak.stock_zh_index_daily(code)` | thsdk `market_data_index` 常返回空 |
| A股个股 | `thsdk.market_data_cn(code, "汇总")` | thsdk 在这块最稳定 |
| 港股指数 | `ak.stock_hk_index_daily_em(symbol)` | 支持 HSI/HSCEI/HSTECH |
| 港股个股 | `thsdk.market_data_hk(code)` | 或 `ak.stock_hk_spot_em()` |
| 美股指数 | `ak.index_global_spot_em()` + 名称筛选 | 含标普/纳斯达克/道琼斯/KOSPI |
| 美股个股 | `ak.stock_us_daily(ticker, adjust="qfq")` | thsdk 在此处不可靠 |
| 韩国 KOSPI | `ak.index_global_spot_em()` 过滤"韩国KOSPI" | — |
| 新股代码 | Yahoo Finance lookup | thsdk/akshare 均未及时收录 |
