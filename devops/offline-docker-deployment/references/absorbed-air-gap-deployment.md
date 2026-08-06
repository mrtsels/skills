---
name: air-gap-deployment
description: "Deploy to offline Linux servers via Windows intermediary: build on Mac, zip → SMB → SSH → unzip → install. No network on target."
tags: [deployment, offline, docker, air-gap, linux, windows, smb]
---

# Air-Gap Deployment

Deploy software to a Linux server with no network access. The dev machine (Mac/Linux) and the target server are connected only through a Windows machine with a USB drive — no direct SSH, no SCP.

## Network Topology

```
Dev (Mac/Linux)  ──SMB──►  Windows  ──USB──►  Linux Server (offline)
                              ↑
                          (has Docker)
```

## Preferred Workflow (user-corrected sequence)

**DO NOT** cp or scp directly to a mount point. **DO NOT** assume SSH access to the target server.

```bash
# === On Dev Machine (Mac/Linux with Docker) ===

# Step 1: Prepare offline images
cd /path/to/project
bash deploy.sh           # pull base images + build app images → docker/images/*.tar

# Step 2: Zip the project (preserves Chinese filenames)
zip -r /tmp/project.zip . -x ".git/*" "backend/target/*"

# Step 3: Copy via SMB to Windows
cp /tmp/project.zip /Volumes/smb-mount/target/

# === On Windows Machine (SSH) ===

# Step 4: SSH into Windows, unzip to USB drive
ssh user@windows-host
powershell -Command "
  Add-Type -AssemblyName System.IO.Compression.FileSystem;
  Remove-Item 'F:\\project' -Recurse -Force -ErrorAction SilentlyContinue;
  [System.IO.Compression.ZipFile]::ExtractToDirectory('F:\\project.zip', 'F:\\');
"

# === Physically move USB to Linux Server ===

# Step 5: On server console
cp -r /media/USB/project /opt/project
cd /opt/project && sudo bash install.sh
```

## Why This Order

| Step | Why |
|------|-----|
| Zip first | SMB transfer of many small files is slow; single zip is faster |
| Not cp -r over SMB | Large project dirs with Chinese filenames can timeout or fail |
| PowerShell ExtractToDirectory | Handles UTF-8 Chinese filenames correctly (unlike cmd `tar` or `Expand-Archive`) |
| USB, not direct network | Target Linux server has no network at all |

## PowerShell Zip Extraction (Chinese Filenames)

```powershell
Add-Type -AssemblyName System.IO.Compression.FileSystem
if (Test-Path 'F:\target') { Remove-Item 'F:\target' -Recurse -Force }
[System.IO.Compression.ZipFile]::ExtractToDirectory('F:\source.zip', 'F:\')
```

## Pitfalls

- **Don't `cp -r` over SMB for large projects**: User corrected: "我还要说多少遍，U盘在windows电脑上，你先压缩成zip，然后smb传过去，然后ssh解压缩"
- **Windows `tar` doesn't handle Chinese UTF-8 filenames**: Use `[System.IO.Compression.ZipFile]::ExtractToDirectory()` instead
- **No SSH to target server**: The Linux server has no network; no SSH access. All deployment is via USB
- **GFW may block git push**: Use SOCKS5 proxy (`socks5://127.0.0.1:1082`) with `git -c http.proxy=... -c https.proxy=... push`
- **`patch` tool fails on CRLF files**: When adding the self-healing header to a script that already has CRLF endings, the `\r` characters break multiline old_string matching in `patch`. The multiline grep/sed pattern gets split at every `\r`. **Fix:** use Python binary processing:
  ```python
  path = '/path/to/script.sh'
  with open(path, 'rb') as f:
      raw = f.read()
  lines = raw.split(b'\\n')
  clean = [l.rstrip(b'\\r') for l in lines]
  # find target line, splice in new header, rejoin with b'\\n', write back
  ```
  After conversion the file is LF-only and subsequent edits work normally.

### CRLF Line Endings (Windows USB Transfer)

When scripts are copied from Windows to USB to Linux, `.sh` files get CRLF (`\r\n`) endings. Bash reads `set -euo pipefail\r` and errors on the unknown option `pipefail\r`.

**Fix: Self-healing header** — add this BEFORE `set -euo pipefail`:

```bash
#!/bin/bash
# CRLF self-heal: Windows USB transfer may introduce CRLF line endings
if grep -q $'\r$' "$0"; then
  sed -i 's/\r$//' "$0"
  exec bash "$0" "$@"
fi

set -euo pipefail
```

The guard checks if the file has `\r` endings, strips them with `sed -i`, then re-executes the clean script via `exec bash "$0"`. The entire operation happens before `set -euo pipefail` so the CRLF never reaches bash's option parser.

**Add to:** `install.sh`, the CLI tool, `deploy.sh` — any script that travels through Windows USB.

**Server-side manual fix** for other scripts:
```bash
sed -i 's/\r$//' /opt/project/*.sh
```

## Post-Install: Updating Code on the Server

After initial deployment, you update via USB with only 2 files. The update strategy differs between backend and frontend:

| Component | File | Server Target | Needs Image Rebuild? | Why |
|-----------|------|--------------|---------------------|-----|
| Backend | `backend/target/*.jar` → rename to `app.jar` | `/opt/project/app.jar` | **No** | docker-compose mounts `app.jar:/app/app.jar:ro` — replace file + restart container, no rebuild |
| Frontend | `index.html` | `/opt/project/index.html` | **Yes** | Dockerfile `COPY`s index.html at build time — no volume mount |

**Dev machine prep:**
```bash
# Build JAR, rename for volume mount path
cd backend && mvn clean package -DskipTests
cp backend/target/*.jar /Volumes/USB/project/app.jar
cp index.html /Volumes/USB/project/index.html
```

**Server update script (`update.sh`):**
```bash
#!/bin/bash
DIR="/opt/project"
CDIR="$DIR/docker"
cd "$DIR"

# Backend: replace JAR → restart container (volume mount, no rebuild)
[ -f app.jar ] && chmod 644 app.jar && \
  docker compose -f "$CDIR/docker-compose.yml" restart backend

# Frontend: rebuild image → restart
[ -f index.html ] && \
  docker compose -f "$CDIR/docker-compose.yml" build frontend && \
  docker compose -f "$CDIR/docker-compose.yml" up -d frontend
```

**Key insight:** The volume mount pattern (`../app.jar:/app/app.jar:ro`) makes backend updates instant — replace JAR, restart container, done. Only frontend changes require a Docker image rebuild.
