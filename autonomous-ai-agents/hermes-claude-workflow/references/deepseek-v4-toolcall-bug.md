# DeepSeek V4 工具调用 Bug

> 来源：https://github.com/deepseek-ai/DeepSeek-V3/issues/1244
> 报告时间：2026-04-24

## 现象

DeepSeek-V4-Pro 间歇性把工具调用输出为纯文本，而非结构化 `tool_calls`：

```
finish_reason: "stop"        # 期望是 "tool_calls"
content: "..."               # 期望是 null
tool_calls: null             # 期望是有序的调用数组

# content 里出现模型"自言自语"后附加工具名+JSON：
"数据还不够完整，让我继续获取。\nbatch_crawl_url_and_answer{\"jobs\": [...]}"
```

## 发生频率（实测数据）

| 类型 | 比例 | 说明 |
|------|------|------|
| 正确 | ~79% (15/19) | `finish_reason: "tool_calls"` |
| 文本回退 | ~11% (2/19) | 工具名+JSON 写入 content |
| 正常文本 | ~10% (2/19) | 模型本意就是不调工具 |

## 根因分析（社区共识）

1. **预填充阶段锁死** — 模型在生成第一个 token 时就决定了走 text 模式还是 tool_calls 模式。一旦第一个 token 是自然语言字词，就锁死在 text 模式，中间切不回 tool_calls。加零宽字符前缀也无用。

2. **累计字节预算触发** — 不是工具数量本身，而是"工具 schema + 累积上下文"的总字节数超过某个阈值。约 30-40 个工具时开始出现，但 schema 重的瘦工具也会触发。

3. **节点级差异** — 有人观察到"好节点"95% 正确，"坏节点"仅 ~30%，暗示与部署负载均衡 / 编译缓存有关。

4. **非 MTP 问题** — 关闭多 token 预测后仍然出现。

## 对 Claude Code 用户的影响

### 影响程度加重因素

| 因素 | 你的环境 | 影响 |
|------|----------|------|
| Anthropic 翻译层 | ✅ 用 `/anthropic/v1/messages?beta=true` | 第二条代码路径增加出错机会 |
| 工具数量 | ✅ playwirght/ralph-loop/etc | ~30-40 工具在触发阈值附近 |
| beta 标记 | ✅ `?beta=true` | 说明是实验性功能 |
| 无 prompt 加固 | ❌ 未添加约束指令 | 缺少第一道防线 |
| 无客户端兜底 | ❌ CC Switch 不做 | 没有 fallback 机制 |
| streaming | ✅ 开启 | streaming 路径可能另有对齐问题 |
| effortLevel max | ✅ `"max"` / `"xhigh"` | 不影响预填充判断 |

## 缓解策略

### 策略 1：降级 Claude Code

新版可能引入更多变更，降级到已知稳定的版本：

```bash
pkill -f claude 2>/dev/null
npm uninstall -g @anthropic-ai/claude-code
npm install -g @anthropic-ai/claude-code@2.1.153
```

### 策略 2：系统 prompt 加固（最有效）

在 CC Switch 的 provider 配置或 settings.json 中注入约束：
```
"Never write function names or JSON arguments in the content field."
```
社区实测将此策略可将 fallback 率从 ~12% 降到 ~3%。

### 策略 3：精简插件

减少 `enabledPlugins` 中不必要的插件，降低每次请求的 tool schema 总字节数。每少一个插件就少一组嵌套 schema 定义。

### 策略 4：客户端兜底

在 CC Switch 或自定义代理中检测 `content` 字段是否包含已知工具名 + JSON，尝试手动兜底：

```python
import re, json

TOOL_PATTERN = re.compile(r'(\w+)\{(\{.*\})\}')

def extract_tool_from_content(content: str):
    match = TOOL_PATTERN.search(content)
    if match:
        name = match.group(1)
        try:
            args = json.loads(match.group(2))
            return name, args
        except json.JSONDecodeError:
            return None
    return None
```
