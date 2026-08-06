---
name: deepseek-cost-tracking
description: DeepSeek 用量追踪 — 每次 Claude Code 调用后记入 cost-tracking.json；每日 cron 只查余额比差。
tags: [cost, tracking, deepseek, billing, automation]
---

# DeepSeek 用量追踪

两个独立机制：

| 机制 | 触发 | 做什么 | 数据源 |
|------|------|--------|--------|
| **每次调用追踪** | Hermes 每次 delegate Claude Code 后 | 从 JSON usage 算花费，追加到 `<project>/.hermes/cost-tracking.json` | Claude Code JSON 输出 |
| **每日余额报告** | cron `0 18 * * 1-5` | 查 DeepSeek API 余额，对比上次余额算出消耗 | `GET /user/balance` |

互不依赖，各司其职。

---

## 机制 1：每次调用追踪（Hermes 强制规则）

**不可跳过。** 每次 Hermes 通过 `terminal(claude ...)` 或 `delegate_task` 调用 Claude Code 后，必须：

1. 从返回 JSON 提取 `usage` 下的 `input_tokens` / `cache_read_input_tokens` / `output_tokens`
2. 按官价算花费（¥）
3. 追加到项目 `.hermes/cost-tracking.json`

### 价格表

来源：https://api-docs.deepseek.com/zh-cn/quick_start/pricing/

| 模型 | 输入(缓存命中) | 输入(未命中) | 输出 |
|------|---------------|-------------|------|
| **flash** | ¥0.02/百万tokens | ¥1/百万tokens | ¥2/百万tokens |
| **pro** | ¥0.025/百万tokens | ¥3/百万tokens | ¥6/百万tokens |

### 计算公式

```python
cost = (
    cache_read / 1_000_000 * INPUT_CACHE_HIT_PRICE
    + input_tokens / 1_000_000 * INPUT_CACHE_MISS_PRICE
    + output_tokens / 1_000_000 * OUTPUT_PRICE
)
```

**不要用** `total_cost_usd`（那是 Anthropic 牌价，比实际贵几十倍）。

### 追踪文件格式

`<project_root>/.hermes/cost-tracking.json`

```json
[
  {"task": "review PR #123", "source": "ccx", "model": "flash",
   "input_tokens": 5331, "cache_read_tokens": 7040, "output_tokens": 7, "cost_cny": 0.01},
  ...
]
```

---

## 机制 2：每日余额报告（cron）

脚本：`~/.hermes/scripts/daily-cost-report.py`

### 做什么

只做一件事：**查余额 → 对比上次 → 输出差额。** 完全不解析日志。

```
💰 本次  ¥8.14
📅 05/28 18:45  上次  ¥8.14
📉 消耗  ¥0.03
```

### 怎么跑

```bash
python3 ~/.hermes/scripts/daily-cost-report.py
```

### Cron 配置

- 调度：`0 18 * * 1-5`（工作日 18:00）
- `script: daily-cost-report.py`
- `no_agent: true` — 脚本自输出完整报告，无需 LLM 处理
- `deliver: weixin`
- 提醒：cron 的 `wrap_response` 必须关（默认 auto 在 no_agent=true 时自动关）

### 状态文件

`~/.hermes/daily-cost-state.json`

记录上一次余额和报告时间，用于下次算差额。

## 余额查询（国内网络）

DeepSeek 是国内 API，直连即可，**不需要 VPN**。可靠方案是用 `subprocess` 调 `curl`：

```python
import subprocess, json
r = subprocess.run(["curl", "-s", "--max-time", "10",
    "https://api.deepseek.com/user/balance",
    "-H", f"Authorization: Bearer {key}"],
    capture_output=True, text=True, timeout=15)
balance = json.loads(r.stdout)
```

Shadowrocket SOCKS5 代理对 DeepSeek 反而会 503。

## Pitfalls

- **用完即走：** 每次重活前后跑 `python3 ~/.hermes/scripts/daily-cost-report.py` 可以实时看消耗，cron 是保底的
- **余额刷新延迟：** API 余额可能有数分钟延迟，小额消耗不一定会立刻体现在余额变化上
- **不要用 CCX 日志算总量：** 正则匹配 CCX 日志的 model/usage 字段极易全失败（格式不固定），导致"全部归类为 unknown"无法聚合。直接看余额差最准。
- **pro 打折后价已体现在价格表：** pro 缓存命中价 ¥0.025/百万tokens（已打 2.5折），直接用
- DeepSeek API key 在 CCX 配置中被截断，手动调 API 用完整 key
- **输出格式偏好：用户要求 token 按 M（百万）统计，不分模型类别。** 手工脚本输出时，tokens 显示为 `输入 X.XXM / 输出 Y.YYM`（不分 flash/pro），钱只看余额差（不按 token 估算）。cron 报告同理，不要出现模型分类。
