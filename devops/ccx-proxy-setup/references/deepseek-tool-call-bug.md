# DeepSeek V4 Tool Call & Thinking Content Issues (through CC Switch/CCX)

Relevant upstream issue: [deepseek-ai/DeepSeek-V3#1244](https://github.com/deepseek-ai/DeepSeek-V3/issues/1244)

## Symptom 1: Tool calls appear as plain text in content

Claude Code receives `finish_reason: "stop"`, `tool_calls: null`, but the response's `content` field contains JSON text like `batch_web_search({"queries":[...]})` instead of executing the tool.

### Reproduction rate (from community data)

In a 19-turn multi-tool session with DeepSeek-V4-Pro via OpenAI Chat API:
- **79%** (15/19) — correct: `finish_reason: "tool_calls"`, proper `tool_calls` array
- **11%** (2/19) — bug: tool calls leaked into `content` as plain text
- **10%** (2/19) — normal text reply (no tool call intended)

### Root cause

Mode locking during **prefill** — before generating the first token, the model decides whether to operate in "text mode" or "tool_calls mode". Once locked, it stays in that mode for the entire generation.

**Trigger threshold**: cumulative byte size of (tool schemas + conversation context) crossing some threshold. Not tool count — it's the **serialized payload size** of the schema definitions.

- In schema-heavy setups (~40 tools), the failure begins around turn 15
- The threshold is probabilistic, not hard: near the boundary you get ~10-30% failure rate, not 100%
- Turn position shifts the probability: later turns (more context) make failure more likely
- "Fail then OK on next try" can happen because of variance in prefill mode selection

### Workaround: Schema compression

Reducing tool schema payload by ~35% (removing `description` fields, shortening parameter names) pushed the failure zone from turn ~15 to turn ~40+.

Example compression — remove the `description` field from each parameter and consider shorter parameter names:

```json
// Before (verbose)
{
  "name": "web_search",
  "description": "Search the web for information",
  "parameters": {
    "type": "object",
    "properties": {
      "queries": {
        "type": "array",
        "items": { "type": "string" },
        "description": "List of search queries"
      }
    },
    "required": ["queries"]
  }
}

// After (compressed)
{
  "name": "web_search",
  "parameters": {
    "type": "object",
    "properties": {
      "queries": {
        "type": "array",
        "items": { "type": "string" }
      }
    },
    "required": ["queries"]
  }
}
```

### Temperature does NOT help

Tested by community: lowering temperature to 0.3-0.5 doesn't fix this. The root cause is in prefill phase mode selection, which isn't affected by sampling temperature.

### Official status

Open issue, no DeepSeek response, no fix, no assignee. Community is still waiting.

## Symptom 2: Thinking/reasoning content not visible in Claude Code

When using DeepSeek through CC Switch proxy (with `?beta=true` enabling thinking mode), Claude Code's interactive TUI may not display DeepSeek's reasoning/thinking tokens. The user sees "Thinking..." or the response appears to stop mid-way.

### Chain

```
Claude Code → CC Switch (:15721, ?beta=true) → api.deepseek.com/anthropic/v1/messages
```

### Why thinking doesn't appear

1. **`?beta=true` is required** — without it, DeepSeek never returns thinking blocks. CC Switch proxy appends this automatically when forwarding to the Anthropic endpoint.
2. **CC Switch recognizes thinking blocks internally** — binary strings confirm it handles `thinking blocks`, `redacted_thinking`, `content_block_delta`, `content_block_start`, `response.reasoning.delta`. But the proxy is fundamentally a transparent pipe — it doesn't transform content.
3. **Claude Code CLI's TUI** may not render `thinking` content blocks from non-Anthropic providers. The thinking blocks may get consumed (redacted) by Claude Code's internal processing without being displayed.
4. **`streaming_idle_timeout` setting** — CC Switch defaults to 180s (`streaming_idle_timeout` in proxy_config table). DeepSeek's long reasoning sessions can hit this timeout, cutting the stream mid-response. The user sees "Thinking..." followed by silence.
5. **`streaming_first_byte_timeout`** — defaults to 60s. If DeepSeek takes >60s to start generating (e.g., during heavy reasoning prefill), the proxy drops the connection.

### Diagnostics

To check if thinking content is arriving at all, test directly against DeepSeek's Anthropic endpoint (bypassing CC Switch):

```bash
curl -N -X POST "https://api.deepseek.com/anthropic/v1/messages?beta=true" \
  -H "x-api-key: $DEEPSEEK_KEY" \
  -H "anthropic-version: 2023-06-01" \
  -H "Content-Type: application/json" \
  -d '{"model":"deepseek-v4-pro","max_tokens":2048,"messages":[{"role":"user","content":"Think step by step: what is 23*47?"}]}'
```

Watch for `event: content_block_start` with `"type":"thinking"` in the SSE stream. If thinking blocks appear in the direct response but not through CC Switch, the proxy is stripping them.

### Mitigation

- Increase `streaming_idle_timeout` in CC Switch's `proxy_config` table (180s → 600s)
- Increase `streaming_first_byte_timeout` (60s → 120s)
- Bypass CC Switch for thinking-heavy prompts by switching `ANTHROPIC_BASE_URL` directly to DeepSeek
- Or use a thinner proxy (mimo-proxy on port 4567) that has no timeout configuration at all

## Configuration drift: settings.json vs DB mismatch

When CC Switch is in takeover mode, it rewrites `settings.json` from its DB provider config. But if you manually edited `settings.json` first, then changed the provider in CC Switch's GUI, or the `proxy_live_backup` table is stale, you end up with different model names in two places.

| Env var | settings.json | CC Switch DB |
|---------|---------------|-------------|
| `ANTHROPIC_DEFAULT_OPUS_MODEL` | `claude-opus-4-8[1M]` | `deepseek-v4-pro[1M]` |
| `ANTHROPIC_DEFAULT_SONNET_MODEL` | `claude-sonnet-4-6[1M]` | `deepseek-v4-flash[1M]` |

The `[1M]` suffix is additionally problematic — Claude Code ≥2.1.159 validates model names against a local pricing table and rejects unknown suffixes.

**Fix:** Align all three sources:
1. CC Switch DB provider `settings_config`
2. `proxy_live_backup` table
3. `~/.claude/settings.json`

Remove `[1M]` suffixes everywhere. Use the split model approach (Claude model name in `_MODEL`, DeepSeek name in `_NAME`).
