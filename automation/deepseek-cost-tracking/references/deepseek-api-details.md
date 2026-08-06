# DeepSeek API 参考

从官方文档和实际使用中收集。

## 余额查询

```http
GET https://api.deepseek.com/user/balance
Authorization: Bearer <API_KEY>
Accept: application/json
```

响应示例：
```json
{
  "is_available": true,
  "balance_infos": [
    {"currency": "USD", "total_balance": "0.00", "granted_balance": "0.00", "topped_up_balance": "0.00"},
    {"currency": "CNY", "total_balance": "27.66", "granted_balance": "0.00", "topped_up_balance": "27.66"}
  ]
}
```

余额是人民币的不要奇怪——DeepSeek 是中国公司，以 CNY 结算。

## Chat Completions API 返回的 usage 字段

```json
{
  "usage": {
    "prompt_tokens": 6,
    "completion_tokens": 5,
    "total_tokens": 11,
    "prompt_tokens_details": {"cached_tokens": 0},
    "completion_tokens_details": {"reasoning_tokens": 5},
    "prompt_cache_hit_tokens": 0,
    "prompt_cache_miss_tokens": 6
  }
}
```

关键字段（用在 cost 计算中）：
- `prompt_cache_hit_tokens` — 缓存命中的输入 token（按缓存命中价）
- `prompt_cache_miss_tokens` — 缓存未命中的输入 token（按未命中价）
- `completion_tokens` — 输出 token（按输出价）

## CCX 日志中的 usage 格式（Anthropic 格式）

CCX 日志 `~/.ccx/logs/app.log` 中的 usage 使用 Anthropic 格式：

### 日志结构

日志包含两种行类型：

**① 请求行** — 有时间戳前缀：
```
2026/05/26 17:38:20.823623 [Messages-Request-Body] 实际请求体:
{"model":"deepseek-v4-flash","messages":[...]}
```

**② 响应行** — JSON 体，**无**时间戳前缀：
```
{"id":"4159c827-...","type":"message","role":"assistant","model":"deepseek-v4-flash",
 "content":[...],"usage":{"input_tokens":5331,"cache_creation_input_tokens":0,
 "cache_read_input_tokens":7040,"output_tokens":7}}
```

Usage 数据只出现在响应行。解析时必须跟踪最近一条请求行的时间戳来定位。

### Usage 字段

```json
{"model":"deepseek-v4-flash","usage":{"input_tokens":5331,"cache_creation_input_tokens":0,"cache_read_input_tokens":7040,"output_tokens":7}}
{"model":"deepseek-v4-flash","usage":{"input_tokens":18,"cache_creation_input_tokens":0,"cache_read_input_tokens":0,"output_tokens":1}}
```

关键字段：
- `input_tokens` — 缓存未命中输入
- `cache_read_input_tokens` — 缓存命中输入
- `output_tokens` — 输出

CCX 日志会轮转，旧日志压缩为 `.gz` 文件存在同目录下。
