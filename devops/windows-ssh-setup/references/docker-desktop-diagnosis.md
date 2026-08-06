# Docker Desktop on Windows — Diagnosis Reference

## Log File Locations (all under `%USERPROFILE%\AppData\Local\Docker\log\`)

| File | What it tells you |
|------|-------------------|
| `host\com.docker.backend.exe.log` | Engine health — "still waiting _ping" loop = VM won't boot |
| `host\docker-sandbox.log` | Sandbox daemon — usually starts fine even when engine is broken |
| `host\electron-YYYY-MM-DD.log` | GUI messages — "Checking backend is running" = failed handshake |
| `host\Docker Desktop.exe.stdout.log` | Electron stdout — BugSnag loader only, thin |
| `host\Docker Desktop.exe.stderr.log` | Electron stderr |
| `host\monitor.log` | Process monitor — restart counters, uptime |
| `host\com.docker.diagnose.exe.log` | Docker diagnose tool output |
| `vm\init.log` | VM boot sequence — usually empty when VM never starts |

## Quick Diagnostic Flow (SSH from Mac)

```bash
# 1. Are processes alive?
ssh user@host 'powershell "Get-Process '*Docker*' | Format-Table Id,ProcessName,StartTime"'

# EXPECTED healthy state:
#   com.docker.backend.exe   (just started or < 5 min ago)
#   com.docker.service       (just started)
#   Docker Desktop           (user-session process)
#   docker-agent             (engine proxy)
#   docker-sandbox           (sandbox daemon)

# BROKEN state (Hyper-V VM failure):
#   com.docker.backend.exe   MISSING — never started
#   Docker Desktop           RUNNING — GUI alive
#   com.docker.service       RUNNING — SCM service alive
#   docker-agent             RUNNING (but stale, from previous session)

# 2. Check service
ssh user@host 'sc.exe query com.docker.service | findstr STATE'
# Expected: "4  RUNNING"

# 3. Check engine named pipe (non-blocking)
ssh user@host 'powershell "Get-ChildItem //./pipe/ -ErrorAction SilentlyContinue | Select-String docker"'
# Healthy:  "dockerDesktopLinuxEngine"  and/or  "docker_engine"
# Broken:   nothing — pipe never created

# 4. Check backend setting (Hyper-V vs WSL2)
ssh user@host 'type "%USERPROFILE%\AppData\Roaming\Docker\settings-store.json" | findstr /I "WslEngineEnabled"'
# "WslEngineEnabled": false → Hyper-V backend (harder to fix remotely)
# "WslEngineEnabled": true  → WSL2 backend (easier to fix)

# 5. Check Hyper-V state
ssh user@host 'powershell "Get-WindowsOptionalFeature -Online -FeatureName Microsoft-Hyper-V | Format-Table State"'
# "Enabled" → Hyper-V VM is expected but may have failed

# 6. Check if WSL is installed
ssh user@host 'powershell "wsl -l -v 2>&1" | findstr /I "Ubuntu"'
```

## Signal Table

| Symptom | `com.docker.backend` present? | Named pipe exists? | `docker info` result | Likely cause |
|---------|------------------------------|--------------------|--------------------|-------------|
| Engine ok | ✅ | ✅ | Returns data | Normal |
| Daemon socket death | ✅ (stale) | ✅ (dead) | Times out | Wedged kernel module |
| Hyper-V VM failure | ❌ (never started) | ❌ | "cannot find the file specified" | VM boot failure |
| Docker not installed | ❌ | ❌ | "docker: command not found" | Install needed |

## Non-blocking Engine Health Check

Avoid hanging the SSH session with a blocking `docker info`:

```bash
# Light probe — checks named pipe existence only
ssh user@host 'powershell "if (Test-Path //./pipe/docker_engine) { echo OK } else { echo PIPE_MISSING }"'

# Exit-code friendly version
ssh user@host 'powershell "Test-Path //./pipe/docker_engine" | findstr True'
```

## Credential Notes (this specific install)

- Hostname: ThinkPad
- User: `1007`
- IP: `192.168.137.1`
- SSH: key-based auth (already configured)
- Docker Desktop path: `C:\Program Files\Docker\Docker\Docker Desktop.exe`
- Docker config: `%USERPROFILE%\AppData\Roaming\Docker\`
- Settings store: `%USERPROFILE%\AppData\Roaming\Docker\settings-store.json`
