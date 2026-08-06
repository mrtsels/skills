# Pre-Push Secret Audit for Dotfiles / Config Repos

When pushing a personal config or dotfiles repo (e.g. `~/.hermes/`), scan for secrets **first** — once pushed, git history never forgets.

## Audit Checklist

Before `git push origin main`, verify these categories are NOT tracked and are in `.gitignore`:

| Category | Examples |
|----------|----------|
| Bot tokens / API keys | `weixin/accounts/*.json`, `*.env` |
| Conversation sessions | `sessions/*.json`, `sessions/*.jsonl`, `hermes-usage.jsonl` |
| Shell / CLI history | `.hermes_history`, `.bash_history` |
| System logs | `logs/*.log*` |
| Memory / identity files | `memories/USER.md`, `memories/MEMORY.md`, `SOUL.md` |
| Runtime state | `processes.json`, `gateway_state.json`, `*.lock` |
| Caches | `image_cache/`, `audio_cache/`, `cache/` |
| Old backups | `config.yaml.bak.*`, `state-snapshots/` |
| Migration archives | `migration/` |

## Scan Command

```bash
cd ~/.hermes
git ls-files | grep -iE 'key|token|secret|password|credential|auth|\.env|cookie|\.pkl|\.pem|cert|jwt|login|session'
```

## Finding Inline API Keys in Tracked Config

```bash
cd ~/.hermes
git ls-files | xargs grep -n 'api_key:' 2>/dev/null | grep -v "api_key: ''" | grep -v 'node_modules'
```

## Moving Inline Secrets Out of Tracked Config

```bash
# Blank inline keys
sed -i '' 's/api_key: sk-.*/api_key: ""/' config.yaml
```

## Fixing a Transient Leak

```bash
git rm --cached leaked-file.sh
echo "leaked-file.sh" >> .gitignore
git add -A && git commit -m "fix: remove accidentally committed secrets"
git push
```

## Building the .gitignore

```gitignore
# === Secrets ===
.env
auth.json
*_key*
*_token*
*_secret*
weixin/accounts/

# === Conversations & sessions ===
sessions/
hermes-usage.jsonl

# === Runtime state ===
gateway_state.json
processes.json
*.lock

# === System logs ===
logs/*.log
logs/*.log.*

# === Temp / cache ===
image_cache/
audio_cache/
__pycache__/
```

## Removing Secrets Already Tracked

```bash
git rm --cached <path>
git add .gitignore
git commit -m "chore: scrub secrets from tracking"
git push
```

## ⚠️ Limitation

`git rm --cached` only stops **future** tracking. The old commit **still contains the secret**. For repos already pushed:
- **API keys, tokens that can authenticate**: ROTATE them immediately
- **Personal data**: Use `git filter-repo` / BFG or orphan branch rewrite

## GitHub Secret Scanning Alert Response

When GitHub alerts you that credentials were pushed:

### 1. Verify scope
Check which files/commits are flagged, scan the repo broadly.

### 2. Rotate the key immediately
```bash
# Generate new key at provider console, update local files
```

### 3. Patch all local files
```bash
sed -i '' 's/sk-old-key/""/' config.yaml
git rm --cached config.yaml.bak.*
```

### 4. Verify .gitignore
```bash
git check-ignore config.yaml.bak.*  # exit 1 = not ignored
```

### 5. Rewrite history (nuclear option)
```bash
git checkout --orphan clean-main
git add -A
git commit -m "initial: clean state (history rewritten)"
git branch -D main
git branch -m clean-main main
git push -f origin main
```

### ⚠️ Regression: orphan branch may re-include gitignored files
After orphan checkout, run `git ls-files 'config.yaml.bak.*'` to check. If they appear, `git rm --cached` + `git commit --amend` to strip them, then force push.