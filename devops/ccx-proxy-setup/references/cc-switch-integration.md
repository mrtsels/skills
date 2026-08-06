# CC Switch Integration

[CC Switch](https://github.com/farion1231/cc-switch) is a desktop tray app (native Rust, Mach-O) that manages AI provider configurations across multiple apps: Claude Desktop, Codex, Gemini, Hermes, OpenCode, OpenClaw. It stores configs in a SQLite database and runs a local proxy server for traffic interception.

## App Identity

```
Bundle ID: com.ccswitch.desktop
Version: 3.15.0
Binary: /Applications/CC Switch.app/Contents/MacOS/cc-switch (native Mach-O, not Electron)
URL scheme: ccswitch://
```

## Data Locations

| Path | Purpose |
|------|---------|
| `~/.cc-switch/cc-switch.db` | Main SQLite database (providers, mcp_servers, proxy_config, settings, skills, prompts) |
| `~/.cc-switch/settings.json` | UI settings (visible apps, language, proxy toggle, provider selection) |
| `~/.cc-switch/copilot_auth.json` | Copilot OAuth tokens |
| `~/.cc-switch/logs/cc-switch.log` | Runtime logs |
| `~/.cc-switch/backups/` | DB backups and Hermes config backups |
| `~/Library/Preferences/com.ccswitch.desktop.plist` | macOS preferences (window state, tray position) |
| `~/Library/WebKit/com.ccswitch.desktop/WebsiteData/.../LocalStorage/` | WebKit localStorage (theme, last-view, last-app) |

## Database Schema

The providers table is the core of CC Switch's model routing:

```sql
CREATE TABLE providers (
    id TEXT NOT NULL,              -- UUID-based ID
    app_type TEXT NOT NULL,        -- 'claude', 'codex', 'gemini', 'opencode', 'hermes',
                                  -- 'claude-desktop' (separate row for Desktop app)
    name TEXT NOT NULL,            -- 'DeepSeek', 'OpenAI Official', etc.
    settings_config TEXT NOT NULL, -- JSON with env vars, permissions, plugins
    website_url TEXT,
    category TEXT,                 -- 'aggregator', 'official', etc.
    created_at INTEGER,
    sort_index INTEGER,
    notes TEXT,
    icon TEXT, icon_color TEXT,
    meta TEXT NOT NULL DEFAULT '{}',
    is_current BOOLEAN NOT NULL DEFAULT 0,  -- 1 = active for this app_type
    in_failover_queue BOOLEAN NOT NULL DEFAULT 0,
    cost_multiplier TEXT NOT NULL DEFAULT '1.0',
    limit_daily_usd TEXT, limit_monthly_usd TEXT,
    provider_type TEXT,
    PRIMARY KEY (id, app_type)
);
```

Key distinction: there are SEPARATE rows for `claude` (Claude Code CLI) and `claude-desktop` (Claude Desktop GUI), each with their own `is_current` flag and `settings_config`. Both need to be configured independently.

### Proxy Config Table

```sql
CREATE TABLE proxy_config (
    app_type TEXT PRIMARY KEY,  -- 'claude', 'codex', 'gemini'
    proxy_enabled INTEGER NOT NULL DEFAULT 0,
    listen_address TEXT NOT NULL DEFAULT '127.0.0.1',
    listen_port INTEGER NOT NULL DEFAULT 15721,  -- All apps share port 15721
    enable_logging INTEGER NOT NULL DEFAULT 1,
    enabled INTEGER NOT NULL DEFAULT 0,          -- Proxy active?
    max_retries INTEGER NOT NULL DEFAULT 3,
    streaming_first_byte_timeout INTEGER NOT NULL DEFAULT 60,
    streaming_idle_timeout INTEGER NOT NULL DEFAULT 120,
    non_streaming_timeout INTEGER NOT NULL DEFAULT 600,
    circuit_failure_threshold, circuit_success_threshold,
    circuit_timeout_seconds, circuit_error_rate_threshold,
    circuit_min_requests,
    default_cost_multiplier TEXT NOT NULL DEFAULT '1',
    pricing_model_source TEXT NOT NULL DEFAULT 'response',
    live_takeover_active INTEGER NOT NULL DEFAULT 0
);
```

## Proxy Server

CC Switch runs a shared proxy on `127.0.0.1:15721` for Claude, Codex, and Gemini:

```
[SRV-001] 代理服务器启动于 127.0.0.1:15721
```

### Proxy Routes

| Route | Purpose |
|-------|---------|
| POST /claude/v1/messages | Claude Messages API → upstream |
| POST /codex/v1/responses | Codex Responses API → upstream |
| POST /codex/v1/chat/completions | Codex Chat Completions → upstream |
| POST /gemini/v1/... | Gemini API → upstream |

### Proxy Takeover

The proxy intercepts app traffic at the network level. The takeover flow:
1. Proxy server starts on 15721
2. For each app (claude/codex/gemini), if `enabled=1` AND `live_takeover_active=1` in proxy_config, the proxy rewrites the app's config to point to itself
3. On restart: CC Switch checks `上次代理状态需要恢复` (previous proxy state needs restoring) from `proxy_live_backup` table
4. Only Claude takeover is auto-restored on restart — Codex and Gemini need manual enablement via the GUI

### How Takeover Affects settings.json

When CC Switch takes over Claude, it:
- Rewrites `~/.claude/settings.json` to set `ANTHROPIC_BASE_URL` to `http://127.0.0.1:15721`
- Sets `ANTHROPIC_AUTH_TOKEN` to `"PROXY_MANAGED"` (meaning the proxy itself handles auth via its DB-stored key)
- May also auto-fix model name suffixes (e.g., removing `[1M]`)
- Syncs provider env vars from its database into the settings

This means **manual edits to settings.json may get overwritten** by CC Switch's takeover logic on restart. Changes should be made in CC Switch's provider config in the DB, not in settings.json.

## Direct DeepSeek Integration (Without CCX)

CC Switch can route directly to DeepSeek's Anthropic-compatible API without going through CCX. This is the cleanest setup for users who don't need CCX's protocol translation or multi-upstream orchestration.

### Architecture

```
Claude Code → CC Switch proxy (:15721) → DeepSeek API
```

No CCX, no system role proxy, no extra middleware.

### Provider Config in CC Switch DB

The `settings_config` field for a Claude provider uses an ENV-based format (not TOML like Codex):

```json
{
  "env": {
    "ANTHROPIC_BASE_URL": "https://api.deepseek.com/anthropic/v1/messages",
    "ANTHROPIC_AUTH_TOKEN": "sk-xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx",
    "ANTHROPIC_MODEL": "deepseek-v4-flash",
    "ANTHROPIC_DEFAULT_HAIKU_MODEL": "deepseek-v4-flash",
    "ANTHROPIC_DEFAULT_HAIKU_MODEL_NAME": "deepseek-v4-flash",
    "ANTHROPIC_DEFAULT_SONNET_MODEL": "claude-sonnet-4-6",
    "ANTHROPIC_DEFAULT_SONNET_MODEL_NAME": "deepseek-v4-flash",
    "ANTHROPIC_DEFAULT_OPUS_MODEL": "claude-opus-4-7",
    "ANTHROPIC_DEFAULT_OPUS_MODEL_NAME": "deepseek-v4-pro",
    "CLAUDE_CODE_ATTRIBUTION_HEADER": "0"
  },
  "permissions": { ... },
  "skipDangerousModePermissionPrompt": true,
  "effortLevel": "max",
  "enabledPlugins": { ... },
  "extraKnownMarketplaces": { ... }
}
```

### Critical: Base URL Must Be Full Path

**The `ANTHROPIC_BASE_URL` must include the full path `/v1/messages`.** DeepSeek's Anthropic endpoint only responds at `https://api.deepseek.com/anthropic/v1/messages`. Sending to just `https://api.deepseek.com/anthropic` returns **HTTP 404**.

Additionally, the `meta` column for the provider must have `isFullUrl: true` so CC Switch's proxy forwards to the full URL as-is (without stripping path components):

```json
{
  "endpointAutoSelect": false,
  "isFullUrl": true,
  "apiFormat": "anthropic"
}
```

If `endpointAutoSelect` is true, CC Switch may auto-discover and override the URL, breaking the connection.

### Setting DeepSeek as Active Provider via DB

```sql
-- Set DeepSeek as the current provider for Claude CLI
UPDATE providers SET is_current = 0 WHERE app_type = 'claude';
UPDATE providers SET is_current = 1 WHERE app_type = 'claude' AND name = 'DeepSeek';

-- Also set for Claude Desktop (separate row)
UPDATE providers SET is_current = 0 WHERE app_type = 'claude-desktop';
UPDATE providers SET is_current = 1 WHERE app_type = 'claude-desktop' AND name = 'DeepSeek';

-- Verify
SELECT name, app_type, is_current FROM providers WHERE app_type LIKE 'claude%';
```

After changing the provider, CC Switch's takeover logic applies the new config on the next request.

### Claude Code Settings

With CC Switch takeover active, `~/.claude/settings.json` should have:

```json
{
  "env": {
    "ANTHROPIC_AUTH_TOKEN": "PROXY_MANAGED",
    "ANTHROPIC_BASE_URL": "http://127.0.0.1:15721",
    "ANTHROPIC_DEFAULT_HAIKU_MODEL": "deepseek-v4-flash",
    "ANTHROPIC_DEFAULT_HAIKU_MODEL_NAME": "deepseek-v4-flash",
    "ANTHROPIC_DEFAULT_SONNET_MODEL": "claude-sonnet-4-6",
    "ANTHROPIC_DEFAULT_SONNET_MODEL_NAME": "deepseek-v4-flash",
    "ANTHROPIC_DEFAULT_OPUS_MODEL": "claude-opus-4-7",
    "ANTHROPIC_DEFAULT_OPUS_MODEL_NAME": "deepseek-v4-pro",
    "CLAUDE_CODE_ATTRIBUTION_HEADER": "0"
  }
}
```

Key points:
- `ANTHROPIC_AUTH_TOKEN` is `"PROXY_MANAGED"` — CC Switch manages the key in its DB
- `ANTHROPIC_BASE_URL` points to `127.0.0.1:15721` (CC Switch proxy), NOT directly to DeepSeek
- Model names must NOT have `[1M]` suffixes — Claude Code v2.1.159 validates these locally and will reject them

### VS Code Settings

```json
{
  "claudeCode.environmentVariables": [
    { "name": "ANTHROPIC_BASE_URL",                    "value": "http://127.0.0.1:15721" },
    { "name": "ANTHROPIC_API_KEY",                     "value": "061127" },
    { "name": "ANTHROPIC_MODEL",                       "value": "claude-sonnet-4-6" },
    { "name": "ANTHROPIC_DEFAULT_SONNET_MODEL",        "value": "claude-sonnet-4-6" },
    { "name": "ANTHROPIC_DEFAULT_SONNET_MODEL_NAME",   "value": "deepseek-v4-flash" },
    { "name": "ANTHROPIC_DEFAULT_HAIKU_MODEL",         "value": "claude-haiku-4-5" },
    { "name": "ANTHROPIC_DEFAULT_HAIKU_MODEL_NAME",    "value": "deepseek-v4-flash" },
    { "name": "ANTHROPIC_DEFAULT_OPUS_MODEL",          "value": "claude-opus-4-7" },
    { "name": "ANTHROPIC_DEFAULT_OPUS_MODEL_NAME",     "value": "deepseek-v4-pro" },
    { "name": "CLAUDE_CODE_ATTRIBUTION_HEADER",        "value": "0" }
  ],
  "claudeCode.selectedModel": "claude-sonnet-4-6"
}
```

## Integration with CCX (Alternative Path)

The CC Switch provider config can also point to a local CCX instance instead of DeepSeek directly:

```
base_url = "http://localhost:3000"
```

This means:
- CC Switch rewrites the app's config to use `http://127.0.0.1:15721` as the API endpoint
- The proxy receives the request, looks up the active provider for that app_type
- It forwards to CCX at `http://localhost:3000` (which translates protocols)
- CCX forwards to DeepSeek (or whatever upstream is configured)

The full chain:
```
Codex CLI → CC Switch Proxy (:15721) → CCX (:3000) → DeepSeek API
Claude Code → CC Switch Proxy (:15721) → CCX (:3000) → DeepSeek Claude API
```

Note: The direct DeepSeek path (without CCX) is simpler for Claude-only setups. The CCX path is useful when you need protocol translation (Responses ↔ Chat) or multi-upstream orchestration.

## Authentication

The CC Switch proxy authenticates requests using the `x-api-key` header (same as Claude's Messages API). The key is forwarded to the upstream provider's `x-api-key` header. No additional proxy-level auth is required — CC Switch relies on its provider DB config for upstream credentials.

## Troubleshooting

### Upstream 404 Error

**Symptom:** CC Switch log shows `[FWD-003] Provider DeepSeek 请求失败: 上游 HTTP 404`

**Root cause:** The `ANTHROPIC_BASE_URL` in the provider's `settings_config.env` does not include the full path. DeepSeek's endpoint only responds at `https://api.deepseek.com/anthropic/v1/messages`, not at the bare `/anthropic`.

**Fix:**
1. Update the base URL to the full path:
   ```sql
   UPDATE providers SET settings_config = json_set(settings_config,
     '$.env.ANTHROPIC_BASE_URL',
     'https://api.deepseek.com/anthropic/v1/messages'
   ) WHERE id='<provider-uuid>';
   ```
2. Set `isFullUrl: true` in the `meta` column:
   ```sql
   UPDATE providers SET meta = json_set(meta, '$.isFullUrl', json('true'))
   WHERE id='<provider-uuid>';
   ```
3. Disable `endpointAutoSelect`:
   ```sql
   UPDATE providers SET meta = json_set(meta, '$.endpointAutoSelect', json('false'))
   WHERE id='<provider-uuid>';
   ```

### Upstream 401 / Authentication Error

**Symptom:** `Authentication Fails, Your api key: ****... is invalid`

**Root cause:** The API key in the provider's `settings_config.env.ANTHROPIC_AUTH_TOKEN` is expired, rotated, or invalid.

**Fix:** Update the API key in the DB:
```sql
UPDATE providers SET settings_config = json_set(settings_config,
  '$.env.ANTHROPIC_AUTH_TOKEN', '<new-key>'
) WHERE app_type='claude' AND name='DeepSeek';
```

Also check the `claude-desktop` row — it's a separate provider entry with its own key.

### Model Validation Error

**Symptom:** Claude Code shows "There's an issue with the selected model" on startup

**Root cause:** Model name in settings.json has a `[1M]` suffix (e.g., `claude-sonnet-4-6[1M]`). Claude Code v2.1.159 validates model names against its internal pricing table and rejects unknown suffixes.

**Fix:** Remove `[1M]` suffixes from ALL model names in:
- `~/.claude/settings.json`
- VS Code's `claudeCode.environmentVariables`
- CC Switch provider DB `settings_config.env`

## Controlling Model Visibility in `claude model list`

Claude Code CLI's interactive `model list` (shown when running `claude` without `-p`) displays three tiers — haiku, sonnet, opus — based on `ANTHROPIC_DEFAULT_*_MODEL` and `ANTHROPIC_DEFAULT_*_MODEL_NAME` environment variables in `settings.json`.

To hide sonnet/opus tiers (show only haiku/flash):

### Step 1: Update CC Switch DB Provider Config

Remove the sonnet and opus env vars from the provider's `settings_config`:

```sql
-- Read current config first
SELECT settings_config FROM providers
WHERE app_type='claude' AND is_current=1;

-- Update via Python (SQLite JSON functions may not handle nested field removal)
```

Python script approach (run from `~/.cc-switch/`):

```python
import json, sqlite3
conn = sqlite3.connect('cc-switch.db')
cur = conn.cursor()

cur.execute("SELECT id, app_type, settings_config FROM providers WHERE app_type='claude' AND is_current=1")
row = cur.fetchone()
config = json.loads(row[2])
env = config.get('env', {})
for key in ['ANTHROPIC_DEFAULT_SONNET_MODEL', 'ANTHROPIC_DEFAULT_SONNET_MODEL_NAME',
            'ANTHROPIC_DEFAULT_OPUS_MODEL', 'ANTHROPIC_DEFAULT_OPUS_MODEL_NAME']:
    env.pop(key, None)
config['env'] = env
cur.execute('UPDATE providers SET settings_config=? WHERE id=? AND app_type=?',
            (json.dumps(config, ensure_ascii=False), row[0], row[1]))
conn.commit()
```

### Step 2: Update Proxy Live Backup

CC Switch restores config from `proxy_live_backup` on restart. Update it too:

```python
cur.execute('SELECT original_config FROM proxy_live_backup WHERE app_type="claude"')
backup_row = cur.fetchone()
backup_config = json.loads(backup_row[0])
backup_env = backup_config.get('env', {})
for key in ['ANTHROPIC_DEFAULT_SONNET_MODEL', 'ANTHROPIC_DEFAULT_SONNET_MODEL_NAME',
            'ANTHROPIC_DEFAULT_OPUS_MODEL', 'ANTHROPIC_DEFAULT_OPUS_MODEL_NAME']:
    backup_env.pop(key, None)
backup_config['env'] = backup_env
cur.execute('UPDATE proxy_live_backup SET original_config=? WHERE app_type="claude"',
            (json.dumps(backup_config, ensure_ascii=False),))
conn.commit()
```

### Step 3: Write Directly to settings.json

Even after DB updates, CC Switch may not immediately sync. Write directly:

```python
with open('/Users/username/.claude/settings.json') as f:
    disk = json.load(f)
disk_env = disk.get('env', {})
for key in ['ANTHROPIC_DEFAULT_SONNET_MODEL', 'ANTHROPIC_DEFAULT_SONNET_MODEL_NAME',
            'ANTHROPIC_DEFAULT_OPUS_MODEL', 'ANTHROPIC_DEFAULT_OPUS_MODEL_NAME']:
    disk_env.pop(key, None)
disk['env'] = disk_env
with open('/Users/username/.claude/settings.json', 'w') as f:
    json.dump(disk, f, indent=2)
```

### Step 4: Restart CC Switch

Kill the process and reopen. After restart, verify `settings.json` has only haiku env vars.

### What If I Want Sonnet/Opus Back?

Reverse the operation — add the env vars back to all three locations (DB `settings_config`, `proxy_live_backup`, and `settings.json`) with your desired model mapping. Then restart CC Switch.

### Important

- **Claude Desktop** (GUI app) has a **separate** model route configuration (`claudeDesktopModelRoutes`) controlled by CC Switch's Desktop-specific provider UI — this procedure only affects **Claude Code CLI** (`claude` command).
- When the user says "model list" without specifying CLI vs Desktop, always clarify first — the fix paths are completely different.
- Removing sonnet/opus env vars means `claude --model sonnet` and `claude --model opus` will fall back to haiku's model mapping.

## Limitations

- **Codex CLI WebSocket**: Codex CLI uses WebSocket (`wss://`) for the Responses API. The CC Switch proxy accepts HTTP CONNECT for WebSocket but returns 404 — it cannot proxy Codex's WebSocket transport. Only Codex desktop app (HTTP-based) is intercepted.
- **Only Claude auto-restores**: On restart, CC Switch only restores Claude proxy takeover. Codex and Gemini must be re-enabled each session.
- **Native binary**: Not Electron — the Rust binary has no asar files or web resources.

## CLI Binary Strings (diagnostic hints)

```
app_config_dir            → config directory (~/.cc-switch/)
~/.cc-switch/config.json → expected config file location (may not exist if DB is used)
ccswitch://              → deep-link URL scheme
[GlobalProxy] Initialized CC Switch proxy port to NNNN
[SRV-001] 代理服务器启动于 127.0.0.1:15721
[FWD-003] Provider DeepSeek 请求失败: 上游 HTTP 404
[FWD-003] Provider MiniMax 请求失败: 上游 HTTP 401
```
