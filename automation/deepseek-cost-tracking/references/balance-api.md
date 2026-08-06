# DeepSeek 余额 & 用量查询 API

文档来源：https://api-docs.deepseek.com/zh-cn/api/get-user-balance

## 查询余额

```
GET https://api.deepseek.com/user/balance
Authorization: Bearer <TOKEN>
Accept: application/json
```

返回示例：
```json
{
  "is_available": true,
  "balance_infos": [
    {
      "currency": "CNY",
      "total_balance": "10.00",
      "granted_balance": "10.00",
      "topped_up_balance": "0.00"
    }
  ]
}
```

## Token 用量

DeepSeek API 的响应中包含 `usage` 字段（来源：https://api-docs.deepseek.com/zh-cn/quick_start/token_usage）：

```json
{
  "usage": {
    "prompt_tokens": 100,
    "completion_tokens": 50,
    "total_tokens": 150,
    "prompt_cache_hit_tokens": 0,
    "prompt_cache_miss_tokens": 100
  }
}
```

字段说明：
- `prompt_tokens` — 输入 tokens（含缓存命中的）
- `prompt_cache_hit_tokens` — 缓存命中的 tokens
- `prompt_cache_miss_tokens` — 缓存未命中的 tokens（= prompt_tokens - prompt_cache_hit_tokens）
- `completion_tokens` — 输出 tokens
- `total_tokens` — 总 tokens

## Pitfalls

- CCX 会截断 API key，config 中看到的 `sk-7c4...b7cf` 不是完整 key
- Hermes 的 `.hermes/.env` 中 `DEEPSEEK_API_KEY` 字段可能存有完整 key
- 如果 key 不可获取，通过比较相邻两次余额差值来推算周期花费
- Key 提示：已知部分格式为 `sk-xxx...xxxx`（约 30-40 字符），以 `sk-` 开头
