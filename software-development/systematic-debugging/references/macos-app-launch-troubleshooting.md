# macOS App Launch Troubleshooting

When an app won't launch via `open -a`, or a terminal hangs on startup.

## Terminal Hangs at Startup

**Symptom:** Opening a new terminal window/tab shows an error and hangs until Ctrl+C.

**Diagnosis:**

```bash
# Check .zshrc for unconditional source to nonexistent files
grep '^[[:space:]]*source' ~/.zshrc | while read -r line; do
  path=$(echo "$line" | sed 's/.*source *"\(.*\)"/\1/')
  [ -f "$path" ] || echo "MISSING: $line"
done
```

**Fix:** Replace naked `source` with a guarded version:

```zsh
# Before (stuck if missing):
source "/path/to/completion.zsh"

# After (skips gracefully):
[ -f "/path/to/completion.zsh" ] && source "/path/to/completion.zsh"
```

**Common culprits:**
- `~/.openclaw/completions/openclaw.zsh` — installed by OpenClaw (Research-Claw), left behind if the binary was removed
- Any completion script for a tool that was uninstalled but not cleaned from .zshrc

## `open -a` Fails with Error -600

**Symptom:** `open "/Applications/SomeApp.app"` returns `error -600` (Launch Services failure), but the app binary runs directly.

**Diagnosis:**

```bash
# 1. Check binary exists and is executable
ls -la "/Applications/SomeApp.app/Contents/MacOS/"

# 2. Check code signing
codesign -dv "/Applications/SomeApp.app" 2>&1

# 3. Check Gatekeeper
spctl -a -vv "/Applications/SomeApp.app" 2>&1
```

**Fix sequence (try in order):**

1. **Kill stuck processes:**
   ```bash
   killall "AppName" 2>/dev/null
   pkill -f "AppName" 2>/dev/null
   ```

2. **Clean lock/cache files:**
   ```bash
   rm -f ~/Library/Application Support/AppName/*.lock
   rm -rf ~/Library/Application Support/AppName/CachedData
   rm -rf ~/Library/Application Support/AppName/CachedExtensionVSIXs
   ```

3. **Refresh Launch Services registration:**
   ```bash
   /System/Library/Frameworks/CoreServices.framework/Frameworks/LaunchServices.framework/Support/lsregister -f "/Applications/SomeApp.app"
   ```

4. **Try `open` again:**
   ```bash
   open "/Applications/SomeApp.app"
   ```

5. **If still failing, run binary directly (bypasses Launch Services):**
   ```bash
   # Safe mode (disable extensions/plugins)
   "/Applications/SomeApp.app/Contents/MacOS/AppName" --disable-extensions
   ```

6. **If sandbox is the issue, try `--no-sandbox`:**
   ```bash
   "/Applications/SomeApp.app/Contents/MacOS/AppName" --no-sandbox
   ```

**Root cause patterns:**
- **Corrupt extension** — Electron apps (VS Code, Slack, Discord) hang on startup because a bad extension crashes during initialization. Safe mode `--disable-extensions` confirms this.
- **Stale Launch Services cache** — `lsregister -f` forces re-registration.
- **Stale lock files** — left behind by a force-quit, the app thinks it's still running.
- **macOS 27.0 (Sequoia+) quirk:** `open -a` error -600 with a perfectly valid code signature appears on newer macOS versions. The binary direct launch is a reliable workaround.
