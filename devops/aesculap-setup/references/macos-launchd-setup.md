# macOS launchd Setup for Aesculap

Since macOS has no systemd, Aesculap's self-healing daemon must be managed via launchd (LaunchAgent).

## Architecture

```
launchd (PID 1)
  └─ com.aesculap.daemon (LaunchAgent)
       └─ ~/.hermes/bin/aesculap-launcher.sh (wrapper)
            └─ python3 -m aesculap start ... (daemon)
```

## Files Created

| File | Purpose |
|------|---------|
| `~/Library/LaunchAgents/com.aesculap.daemon.plist` | LaunchAgent definition |
| `~/.hermes/bin/aesculap-launcher.sh` | Wrapper that sources ~/.hermes/.env |
| `~/.hermes/logs/aesculap-stdout.log` | Daemon stdout |
| `~/.hermes/logs/aesculap-stderr.log` | Daemon stderr |

## Why a Wrapper Script?

launchd does NOT inherit the user's shell environment. Environment variables like `DEEPSEEK_API_KEY` defined in `~/.hermes/.env` are not available to the daemon process. The wrapper script sources `.env` before launching Aesculap:

```bash
#!/bin/bash
set -e
if [ -f ~/.hermes/.env ]; then
    set -a     # auto-export all sourced variables
    source ~/.hermes/.env
    set +a
fi
exec /opt/homebrew/Caskroom/miniconda/base/bin/python3.13 \
    -m aesculap start /Users/minimx/.hermes/aesculap.yaml
```

## State Directory

**Critical pitfall:** The default `state_dir: /var/lib/aesculap` requires root. On macOS with a user-scope daemon this causes an immediate `PermissionError` crash loop.

Fix: Change to a user-writable path:
```yaml
state_dir: /Users/minimx/.hermes/aesculap/state
audit_log_path: /Users/minimx/.hermes/aesculap/audit.jsonl
```

## Troubleshooting

### Daemon fails immediately (exit code != 0)

```bash
# Check exit status
launchctl list | grep aesculap
# Format: PID  EXIT_CODE  Label
# EXIT_CODE 0 = running, non-zero = last exit code
# - means process no longer exists

# Check logs
cat ~/.hermes/logs/aesculap-stderr.log
cat ~/.hermes/logs/aesculap-stdout.log
```

### Common failures

1. **PermissionError: '/var/lib/aesculap'** — state_dir needs to be user-writable
2. **ModuleNotFoundError: aesculap** — wrapper script uses wrong Python; verify `which python3` or use absolute path
3. **API auth failure** — wrapper not sourcing `.env`; test manually:
   ```bash
   source ~/.hermes/.env && python3 -m aesculap probe ~/.hermes/aesculap.yaml
   ```
4. **launchctl load fails silently** — check syntax:
   ```bash
   plutil -lint ~/Library/LaunchAgents/com.aesculap.daemon.plist
   ```

### Full restart cycle

```bash
launchctl bootout gui/$(id -u)/com.aesculap.daemon 2>/dev/null
launchctl bootstrap gui/$(id -u) ~/Library/LaunchAgents/com.aesculap.daemon.plist 2>/dev/null
# Fallback if above fails:
launchctl unload ~/Library/LaunchAgents/com.aesculap.daemon.plist
launchctl load ~/Library/LaunchAgents/com.aesculap.daemon.plist
```
