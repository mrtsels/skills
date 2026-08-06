# CCX/cc-switch 代理诊断记录

## 链路拓扑

```
Claude Code → settings.json(ANTHROPIC_BASE_URL) → [代理] → DeepSeek API
```

## DeepSeek Anthropic 兼容 API

DeepSeek 提供 Anthropic Messages API 兼容端点：

```
POST https://api.deepseek.com/anthropic/v1/messages
Authorization: Bearer sk-xxx
Content-Type: application/json
anthropic-version: 2023-06-01
```

支持模型：`deepseek-v4-flash`、`deepseek-v4-pro`

也兼容标准 OpenAI Chat 格式：
```
POST https://api.deepseek.com/v1/chat/completions
Authorization: Bearer sk-xxx
```

Auth：`Authorization: Bearer` 头。API key 以 `sk-` 开头。

⚠️ CCX 内部的 `baseUrl` 设为 `https://api.deepseek.com/anthropic` 即可自动拼接 `/v1/messages`。无需手动加路径。

## 两种代理的区别

| 软件 | 默认端口 | 类型 | 配置文件位置 |
|------|---------|------|-------------|
| **CCX** (`/usr/local/bin/ccx`) | 3000 | CLI 代理 | `~/.ccx/.config/config.json`，key 在 `upstream[0].apiKeys`；端口在 `.env` 的 `PORT` |
| **cc-switch** (GUI 应用) | 15721 | 桌面 GUI | `~/.cc-switch/settings.json`；provider DB 在 `~/.cc-switch/cc-switch.db` |

## 故障场景：DeepSeek 404 / Auth Failed

### 症状
- Claude CLI 报错：`There's an issue with the selected model (claude-sonnet-4-6)`
- CCX 日志：`upstream 404`
- cc-switch 日志：`上游 HTTP 404` + 熔断器触发

### 根因
cc-switch 和 CCX 各自维护独立的 API key。cc-switch GUI 中的 DeepSeek key 可能过期，而 CCX CLI 中的 key 仍然有效。两个软件可能使用不同的 key。

### 修复步骤

```bash
# 1. 检查两个代理的进程
lsof -i :3000   # CCX
lsof -i :15721  # cc-switch

# 2. 如果 CCX 未运行，启动它
cd ~/.ccx && /usr/local/bin/ccx

# 3. 测试 CCX 能否直连 DeepSeek
curl -s http://127.0.0.1:3000/v1/messages \
  -H "Content-Type: application/json" \
  -H "x-api-key: 061127" \
  -H "anthropic-version: 2023-06-01" \
  -d '{"model":"deepseek-v4-flash","max_tokens":5,"messages":[{"role":"user","content":"hi"}]}'

# 4. 更新 settings.json 指向 CCX
# ANTHROPIC_BASE_URL → http://127.0.0.1:3000
# ANTHROPIC_AUTH_TOKEN → 061127 (CCX 的 PROXY_ACCESS_KEY)

# 5. 清除 [1M] 后缀
# ANTHROPIC_DEFAULT_SONNET_MODEL → "claude-sonnet-4-6" (不是 "claude-sonnet-4-6[1M]")
```

### 验证
```bash
cd ~/bipartite-gnn-gui && claude --model deepseek-v4-flash --bare \
  --dangerously-skip-permissions --output-format json \
  -p 'Say "ok" if working.'
```

## ⚠️ 模型名别名坑：`--model opus` 不触发 `_NAME` 映射

通过 CCX 转 DeepSeek 时，Claude Code 的 `_NAME` 环境变量（如 `ANTHROPIC_DEFAULT_OPUS_MODEL_NAME=deepseek-v4-pro`）只在**未使用 `--model` 参数时生效**。

当使用 `--model opus` 时，Claude Code 把 `opus` 解析为 `claude-opus-4-7`，然后原样发送给 CCX。**`_NAME` 映射被跳过。**

| 命令 | 实际发送给 CCX 的模型名 | 结果 |
|------|------------------------|------|
| `--model opus` | `claude-opus-4-7` | 靠 CCX fuzzy 匹配，慢（200s+） |
| `--model deepseek-v4-pro` | `deepseek-v4-pro` | 直发，快（4.8s） |
| `--model sonnet` | `claude-sonnet-4-6` | 靠 fuzzy 匹配，略慢 |
| `--model deepseek-v4-flash` | `deepseek-v4-flash` | 直发，快 |

**结论：通过 CCX 走 DeepSeek 时，始终用 DeepSeek 模型名直写 `--model`，别用 Anthropic 别名。**
