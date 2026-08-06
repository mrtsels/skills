# 新浪 / 东方财富直连 API（akshare 被代理阻断时使用）

当 `http_proxy`/`https_proxy` 环境变量导致 akshare HTTP 请求全部返回 None 时，
直接用以下 API 获取指数和个股行情。**必须传 `proxies={"http": None, "https": None}` 绕过代理。**

## 新浪财经 CSV API

**端点：** `http://hq.sinajs.cn/list=<market><code>`

| 市场 | 前缀 | 示例 |
|------|------|------|
| 上证指数 | `sh` | `sh000001` |
| 深证指数 | `sz` | `sz399001` |
| 上证股票 | `sh` | `sh600519` |
| 深证股票 | `sz` | `sz300033` |
| 港股 | `hk` | `hk00700` |

**请求示例：**

```python
import requests
r = requests.get(
    "http://hq.sinajs.cn/list=sh000001,sz399001,sh000300,sh000016,sh000905,sh000688",
    headers={"Referer": "https://finance.sina.com.cn"},
    proxies={"http": None, "https": None},
    timeout=10
)
# 返回多行 CSV，每行结构：
# var hq_str_sh000001="名称,开盘,前收,最新价,最高,最低,...,日期,时间";
```

**字段顺序（按逗号分割，14个核心字段）：**

| 索引 | 含义 |
|:----:|------|
| 0 | 名称 |
| 1 | 开盘价 |
| 2 | 前收盘价 |
| 3 | **最新价** |
| 4 | 最高价 |
| 5 | 最低价 |
| 6-7 | 预留 |
| 8 | 成交量（手） |
| 9 | 成交额（元） |
| ... | ... |
| 30 | 日期 |
| 31 | 时间 |

**解析示例：**

```python
raw = r.text.strip()
for line in raw.split(";"):
    if not line.strip():
        continue
    data = line.split("=")[1].strip('"').split(",")
    name, open_, prev_close, current, high, low = data[0], data[1], data[2], data[3], data[4], data[5]
    chg = float(current) - float(prev_close)
    pct = chg / float(prev_close) * 100
    date = data[30]
    print(f"{name}: {current} {chg:+.2f} ({pct:+.2f}%) [{date}]")
```

## 东方财富 Push API（JSON 格式，无需 parse）

**端点：** `https://push2.eastmoney.com/api/qt/ulist.np/get`

**参数：**

| 参数 | 说明 | 示例 |
|------|------|------|
| `secids` | 逗号分隔，格式 `<市场>.<代码>` | `1.000001,0.399001`（1=沪, 0=深） |
| `fields` | 所需字段，f2=最新价 f3=涨跌幅 f4=涨跌额 f12=代码 f14=名称 | `f2,f3,f4,f12,f14` |
| `fltt` | 精度保留，2=两位小数 | `2` |

**请求示例：**

```python
import requests, time
url = "https://push2.eastmoney.com/api/qt/ulist.np/get"
params = {
    "fltt": 2,
    "fields": "f2,f3,f4,f12,f14",
    "secids": "1.000001,0.399001,0.399006,1.000300,1.000016,1.000905,1.000688",
    "_": int(time.time() * 1000)
}
r = requests.get(url, params=params, timeout=10,
                 proxies={"http": None, "https": None})
data = r.json()
for item in data["data"]["diff"]:
    print(f"{item['f14']}: {item['f2']}  {item['f4']} ({item['f3']}%)")
```

**常用 secids：**

| 指数 | secid |
|------|-------|
| 上证指数 | `1.000001` |
| 深证成指 | `0.399001` |
| 创业板指 | `0.399006` |
| 沪深300 | `1.000300` |
| 上证50 | `1.000016` |
| 中证500 | `1.000905` |
| 科创50 | `1.000688` |

**字段映射：**

| 字段 | 含义 |
|:----:|------|
| f2 | 最新价 |
| f3 | 涨跌幅（%） |
| f4 | 涨跌额 |
| f12 | 股票代码 |
| f14 | 股票名称 |

## 适用场景决策树

```python
def get_index_data(name_code_pairs: dict) -> dict:
    """
    name_code_pairs = {"上证指数": "sh000001", ...}
    返回 {name: {"close": float, "chg": float, "pct": float, "date": str}}
    """
    import requests, time
    proxies = {"http": None, "https": None}
    
    # 方法1：新浪 API（最稳定）
    codes = ",".join(name_code_pairs.values())
    r = requests.get(f"http://hq.sinajs.cn/list={codes}",
                     headers={"Referer": "https://finance.sina.com.cn"},
                     proxies=proxies, timeout=10)
    results = {}
    for line in r.text.strip().split(";"):
        if not line.strip(): continue
        data = line.split("=")[1].strip('"').split(",")
        name, prev_close, current = data[0], data[2], data[3]
        chg = float(current) - float(prev_close)
        pct = chg / float(prev_close) * 100
        results[name] = {"close": float(current), "chg": round(chg, 2), "pct": round(pct, 2), "date": data[30]}
    return results
```
