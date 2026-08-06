# 模型用量追踪

> 2026-05-26 更新：新增自动追踪脚本和余额差估算 Hermes 自身用量。

## 两路分开统计

| 路径 | 数据来源 | 统计方式 |
|------|---------|---------|
| **Claude Code** | CCX 日志 `~/.ccx/logs/app.log` | 从日志提取 usage token → ×官价 |
| **Hermes 自身** | DeepSeek 余额 API | 余额差 − 已知 Claude Code 花费 = Hermes 估算 |
| **余额** | `GET /user/balance` | API 直查（CNY + USD） |

## 自动追踪脚本

```bash
# 总览
python3 ~/.hermes/scripts/track_usage.py

# 查余额
python3 ~/.hermes/scripts/track_usage.py --balance

# 统计 Claude Code（从 CCX 日志解出历史用量）
python3 ~/.hermes/scripts/track_usage.py --claude

# 统计 Hermes（从余额差估算）
python3 ~/.hermes/scripts/track_usage.py --hermes

# 全量更新追踪文件（推荐每次重活前后跑一次）
python3 ~/.hermes/scripts/track_usage.py --update
```

## DeepSeek 官方价格（2026-05，来源于官网）

| 模型 | 输入(缓存命中) | 输入(未命中) | 输出 |
|------|---------------|-------------|------|
| **flash** | ¥0.02/百万 | ¥1/百万 | ¥2/百万 |
| **pro** | ¥0.025/百万 | ¥3/百万 | ¥6/百万 |

## 计算公式

```python
cost_cny = cache_read_tokens / 1_000_000 * input_cache_hit_price
         + input_tokens / 1_000_000 * input_cache_miss_price
         + output_tokens / 1_000_000 * output_price
```

## 目标文件

`{project_root}/.hermes/cost-tracking.json`

## 数据来源

**Claude Code 调用**：terminal(claude ...) 返回的 JSON 的 `usage` 字段
```json
{
  "usage": {
    "input_tokens": 42068,
    "cache_read_input_tokens": 1582848,
    "output_tokens": 34518
  }
}
```

**Hermes 自身调用**：通过余额 API /user/balance 查询，扣除已知 Claude Code 花费。

**CCX 日志回填**：脚本自动扫描 `~/.ccx/logs/app.log` + 轮转的 `app-*.gz`，提取所有 Anthropic-format usage 记录（去重），用于补全历史数据。

## Hermes 用量估算方法

每次调用 `track_usage.py --update` 时：
1. 从 CCX 日志解析所有 Claude Code usage → 追加到 records
2. 从 DeepSeek 余额 API 获取当前余额
3. 对比上次记录的余额 → 总消耗 = 上次余额 − 当前余额
4. Hermes 自身消耗 = 总消耗 − 本次新增的 Claude Code 花费
5. 追加 Hermes 估算记录到 tracking 文件

精度受余额刷新延迟影响。建议每次重活前后跑一次。

## 每轮 Claude Code 调用后（手动追踪，无需脚本）

每次 `terminal(claude ...)` 返回后，从 JSON 的 `usage` 字段提取 token 数，按公式计算 CNY，直接追加到 tracking 文件。这是 Hermes 的强制规则，不可跳过。

## Pitfalls

- Claude Code 的 `total_cost_usd` 按 Anthropic 牌价算的，**不是**实际 DeepSeek 费用。误用会导致成本虚高 30-60 倍。必须用 token 数×DeepSeek 官价重算。
- CCX 日志可能因轮转覆盖旧记录，定期 `--update` 确保不丢数据
- Hermes 自身用量估算基于余额差，不是精确值。最准的方式是把 Hermes 也走 CCX（`track_usage.py --route-hermes`），这样所有调用都在同一份日志里
- pro 的 2.5 折折扣已体现在表里的打折后价格
- 如果 `cache_read_input_tokens` 为 0，缓存未命中 input = `input_tokens`
- 所有金额保留 2 位小数，不累积厘级误差
