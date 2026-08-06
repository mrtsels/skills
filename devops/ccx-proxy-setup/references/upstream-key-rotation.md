# CCX Upstream Key Rotation Recovery

## Scenario

The DeepSeek API key was rotated (due to GitHub Secret Scanning leak detection). CCX's upstream channel had the old key, which was auto-disabled after getting `authentication_error` responses. Result: Claude Code failed in both terminal and VS Code.

## Diagnostic Commands

```bash
# 1. Check if CCX is running
lsof -i :3000

# 2. Check if system role proxy is running
lsof -i :4567

# 3. Test proxy → CCX chain
curl -s --connect-timeout 5 http://127.0.0.1:4567/v1/messages \
  -H "Content-Type: application/json" \
  -H "x-api-key: 061127" \
  -H "anthropic-version: 2023-06-01" \
  -d '{"model":"deepseek-v4-flash","max_tokens":5,"messages":[{"role":"user","content":"hi"}]}'

# Expected symptom: {"type":"error","error":{"type":"proxy_error","message":"connect ECONNREFUSED 127.0.0.1:3000"}}
# CCX not running
```

## Root Cause Chain

1. DeepSeek API key rotated (user disabled old key at DeepSeek console)
2. `.ds-key` file updated with new key, but CCX config.json never updated
3. CCX received `authentication_error` from DeepSeek with old key
4. CCX auto-moved old key to `disabledApiKeys[]` and set `status: "suspended"`
5. No one noticed until Claude Code started failing
6. Additionally, CCX itself had stopped running (reason unknown — possibly crash or manual stop)

## CCX Config State (before fix)

```json
{
  "upstream": [
    {
      "baseUrl": "https://api.deepseek.com/anthropic",
      "apiKeys": [],
      "historicalApiKeys": ["sk-OLDKEY...b7cf"],
      "disabledApiKeys": [
        {
          "key": "sk-OLDKEY...b7cf",
          "reason": "authentication_error",
          "message": "Authentication Fails, Your api key: ****b7cf is invalid",
          "disabledAt": "2026-06-01T17:10:03+08:00"
        }
      ],
      "serviceType": "claude",
      "name": "DeepSeek Claude",
      "priority": 1,
      "status": "suspended"
    }
  ]
}
```

## Config Fix (3 changes needed)

```bash
# Fix 1: Replace apiKeys with new key
# Fix 2: Clear disabledApiKeys and historicalApiKeys to []
# Fix 3: Change status from "suspended" to "active"
```

Updated block:
```json
{
  "baseUrl": "https://api.deepseek.com/anthropic",
  "apiKeys": ["sk-NEWKEY...759c"],
  "historicalApiKeys": [],
  "disabledApiKeys": [],
  "serviceType": "claude",
  "name": "DeepSeek Claude",
  "priority": 1,
  "status": "active"
}
```

## Co-occurring Config Issues (Triple Config Drift)

When Claude Code fails everywhere, rarely just one thing is wrong. In this case:

| Config | Issue | Fix |
|--------|-------|-----|
| `~/.claude/settings.json` env.BASE_URL | Pointed to `127.0.0.1:15721` (CC Switch, dead) | Changed to `127.0.0.1:4567` (proxy) |
| `~/.claude/settings.json` models | `claude-sonnet-4-6[1M]` suffix | Removed `[1M]` |
| `~/.claude/settings.json` AUTH_TOKEN | `PROXY_MANAGED` (stale) | Changed to `061127` (CCX key) |
| VS Code `claudeCode.environmentVariables` BASE_URL | `http://localhost:3000` (direct CCX) | Changed to `http://127.0.0.1:4567` (via proxy) |
| CCX upstream config | key disabled, status suspended | New key + active |
| CCX process itself | Not running | Started |
| `.ds-key` file | Content was truncated `sk-e7c...759c` (verbatim) | Fixed with full key |

## Prevention

When rotating the DeepSeek API key, always perform this checklist:
1. [ ] Update `~/.hermes/.ds-key`
2. [ ] Update `~/.ccx/.config/config.json` upstream apiKeys
3. [ ] Verify CCX auto-reload: `curl :3000/health`
4. [ ] Test with `curl :3000/v1/messages`
5. [ ] Test full chain through proxy: `curl :4567/v1/messages`
6. [ ] Verify `.ds-key` content: `xxd ~/.hermes/.ds-key`

## Key File Verification

`cat` may truncate long keys. Use `xxd` or `wc -c` for verification:

```bash
# Check key length — should be ~35-40 chars for DeepSeek key (sk- prefix + hex)
cat ~/.hermes/.ds-key | wc -c

# Check actual bytes
xxd ~/.hermes/.ds-key

# If it shows literal "..." (sk-e7c...759c), the truncated form was written verbatim
# The actual full key must be retrieved from the user or DeepSeek console
```
