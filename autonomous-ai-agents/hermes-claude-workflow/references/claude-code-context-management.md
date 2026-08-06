# Claude Code VS Code Extension Context Management

Why the context indicator fills up "too fast" and how to diagnose/debug it.

**Key fact: DeepSeek V4 has native 1M context.** The issue is NOT a model context window mismatch — DeepSeek matches Claude's large context. See user correction: "DeepSeek V4原生就是1M".

## The Root Cause

Claude Code has **no user-configurable context window limit** in VS Code settings.json (`claudeCode.*` namespace) or in `~/.claude/settings.json`. It manages context internally.

The "context is getting full" indicator reflects **Claude Code's internal context budget** — not the model's actual context window limit. It's a UX signal that the conversation is accumulating and the agent may benefit from compaction.

The proxy chain for this user:

```
VS Code → claude CLI → cc-switch (15721) → DeepSeek V4
```

cc-switch handles model name mapping and format translation directly. No CCX or mimo-proxy in the middle.

## What Actually Drives Context Consumption

### 1. Enabled plugins consume system prompt space (highest impact)

Each enabled plugin injects its own instructions into Claude Code's system prompt. With 10+ plugins, the system prompt alone can consume 10K–20K+ tokens before any conversation begins — that's 10-20% of Claude Code's internal budget gone before you type a word.

Check enabled plugins in `~/.claude/settings.json`:
```json
"enabledPlugins": {
  "claude-in-office@financial-services-plugins": true,
  "claude-md-management@claude-plugins-official": true,
  "figma@claude-plugins-official": true,
  "playwright@claude-plugins-official": true,
  "typescript-lsp@claude-plugins-official": true,
  "debugging-code@debug-skill-marketplace": true,
  ...
}
```

Each line is another chunk of system prompt. These add up.

**Mitigation:** Disable plugins not actively needed. Set unused plugins to `false` in settings.json.

### 2. Effort level drives per-turn context collection

`CLAUDE_CODE_EFFORT_LEVEL=on` / `"effortLevel": "xhigh"` causes Claude Code to:
- Read more files for context on each interaction
- Run more exploration commands (git status, file listings, directory scans)
- Keep more conversation history alive rather than pruning early

**Mitigation:** Lower to `"effortLevel": "high"` or `"default"` in `~/.claude/settings.json`.

### 3. Claude Code's natural behavior

Even with minimal effort, Claude Code intentionally packs in:
- File contents from every `Read` call
- Git status/diff on each interaction
- Terminal command output
- Full conversation history (accumulating each turn)
- System prompt from plugins and skills

This is by design. The `/compact` command exists to address this in interactive sessions.

### 4. `CLAUDE_CODE_EFFORT_LEVEL` env var paths

Two independent paths set effort level — both must be checked:

**CLI settings** (`~/.claude/settings.json`):
```json
"effortLevel": "xhigh"
```

**VS Code settings** (`~/Library/Application Support/Code/User/settings.json`):
```json
{ "name": "CLAUDE_CODE_EFFORT_LEVEL", "value": "on" }
```

The VS Code env var overrides the CLI settings.

## Debugging Path

When the user says "context keeps filling up":

### Step 1: Check the config layers

```bash
# VS Code settings
cat ~/Library/Application\ Support/Code/User/settings.json | grep -A3 claudeCode

# Claude CLI settings
cat ~/.claude/settings.json | grep -E 'model|effort|enabledPlugins|env'

# Proxy chain
lsof -i :15721   # cc-switch running? (this user's routing layer)
lsof -i :3000    # CCX running? (if CCX is in chain)
lsof -i :4567    # mimo-proxy running? (if system role fix is active)
```

### Step 2: Identify what's eating context

1. **Plugin count** — more plugins = more system prompt overhead. Count them.
2. **effortLevel** — xhigh vs default vs low makes a big difference.
3. **Conversation turns** — each turn adds history. Check how many turns in.

### Step 3: Mitigate

1. Disable unused plugins in `~/.claude/settings.json` → `enabledPlugins`
2. Lower `effortLevel` to `"high"` or `"default"`
3. Use `/compact` in interactive sessions
4. Start new sessions for focused subtasks instead of cramming into one conversation

## Quick Fixes Summary

| Fix | Where | Impact |
|-----|-------|--------|
| Disable unused plugins | `~/.claude/settings.json` → `enabledPlugins` | High — frees system prompt space immediately |
| Lower `effortLevel` to `"high"` or `"default"` | `~/.claude/settings.json` | Medium — less context per turn |
| Set `CLAUDE_CODE_EFFORT_LEVEL=off` or remove it | VS Code env vars | Medium — matches CLI setting |
| Use `/compact` command | Interactive sessions | Temporary — per-session manual action |
| Start fresh sessions | User habit | High — prevents accumulation |

## Reference

This was investigated during a session where the user asked "why does the context keep filling up". The full trace went through VS Code settings (`~/Library/Application Support/Code/User/settings.json`), Claude CLI settings (`~/.claude/settings.json`), and the cc-switch proxy at port 15721. No explicit context window limit exists as a user setting. DeepSeek V4 was confirmed to have native 1M context — not a model limitation. The cause was `effortLevel: xhigh` + 9 enabled plugins.
