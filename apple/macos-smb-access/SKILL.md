---
name: macos-smb-access
description: "Access Windows SMB file shares from macOS — host discovery, port scanning, authentication, mounting, and troubleshooting. Covers mount_smbfs, smbutil, and common failure modes against Windows servers on the local network."
category: apple
---

# macOS SMB Access (Windows File Shares)

> 本技能为 SMB 挂载类技能的伞,已吸收 `smb-mount`、`thinkpad-smb-access`(2026-08 合并)。
> 完整原文见 `references/absorbed-*.md`。


Mount and access Windows SMB/CIFS file shares from macOS. Use when the user says "try SMB" after confirming a remote machine runs Windows — or for NAS (Synology etc.) shares.

## Prerequisites

macOS ships with `mount_smbfs` and `smbutil` — no additional installs needed. These sit on `/sbin/` and `/usr/bin/`.

## Quick-Start

```bash
# ⚠️  Before any SMB command: unset proxy env vars if connecting to internal IPs
unset http_proxy https_proxy HTTP_PROXY HTTPS_PROXY no_proxy NO_PROXY

# 1. Verify reachability
ping -c 1 -W 3 HOSTNAME.local

# 2. Scan common SMB ports
for port in 445 139; do nc -z -w2 IP $port && echo "Port $port: OPEN"; done

# 3. List available shares (authenticated) — URL-encode password
PASS=$(python3 -c "from urllib.parse import quote; print(quote('PASSWORD', safe=''))")
smbutil view //USER:$PASS@HOST

# 4. Mount a share — ⭐ osascript/Finder is the STANDARD method
#    mount_smbfs fails on Chinese/non-ASCII share names (URL parsing failed, exit 64)
SHARE=$(python3 -c "from urllib.parse import quote; print(quote('SHARE_NAME', safe=''))")
osascript -e "mount volume \"smb://USER:$PASS@HOST/$SHARE\""
# Mount point: /Volumes/<SHARE_NAME> (display name, unencoded)

# 5. Unmount when done
diskutil unmount "/Volumes/SHARE_NAME"

# === FALLBACK (ASCII share names only) ===
mkdir -p /tmp/mount_point
mount_smbfs //USER:$PASS@HOST/ASCII_SHARE /tmp/mount_point
# === or Finder CLI ===
open 'smb://USER:PASS@HOST/SHARE'    # mounts via Finder, /Volumes/SHARE
```

## Procedure

### 1. Host Discovery

```bash
# Try Bonjour/mDNS hostname first
ping -c 1 -W 3 THINKPAD.local
# If that resolves, note the IP from ping output
# If not, try the IP directly (check router DHCP table)
```

The `.local` suffix only works if mDNS (Bonjour) is running on the remote machine. Windows machines respond to mDNS by default in recent versions.

### 2. Port Scanning

Use `nc` (netcat, built-in on macOS) to probe SMB ports:

```bash
nc -z -w2 IP 445 2>&1 && echo "SMB (445): OPEN" || echo "SMB (445): closed"
nc -z -w2 IP 139 2>&1 && echo "NetBIOS (139): OPEN" || echo "NetBIOS (139): closed"
```

| Port | Service | Typical Windows |
|------|---------|-----------------|
| 445 | SMB over TCP (modern) | ✅ Open |
| 139 | NetBIOS (legacy) | Usually open |
| 22 | SSH | ❌ Closed (no SSH server on stock Windows) |
| 548 | AFP (Apple Filing) | ❌ Closed (macOS only) |

If SSH is closed but SMB ports are open, it's almost certainly a Windows machine (or macOS with only File Sharing enabled).

### 3. Authentication

```bash
# URL-encode the password first (special chars like ~ } ! @ break the URL)
PASS=$(python3 -c "from urllib.parse import quote; print(quote('PASSWORD', safe=''))")

# List shares with user/password
smbutil view //USER@IP          # prompts for password
smbutil view //USER:$PASS@IP    # inline, encoded password
```

**Common patterns:**
- Windows username is typically the local user account name
- No domain needed for local accounts; omit `-W` or use `-W WORKGROUP`
- Empty password usually rejected by modern Windows

### 4. Mounting

**⭐ Standard: osascript/Finder mount** — works for ALL share names, including Chinese:

```bash
PASS=$(python3 -c "from urllib.parse import quote; print(quote('PASSWORD', safe=''))")
SHARE=$(python3 -c "from urllib.parse import quote; print(quote('共享名', safe=''))")
osascript -e "mount volume \"smb://USER:$PASS@IP/$SHARE\""
ls "/Volumes/共享名"
```

The mount appears at `/Volumes/<display name>` (unencoded). Chinese share names mounted this way work fine.

**Fallback: mount_smbfs (ASCII share names only)**

`mount_smbfs` fails on Chinese share names with `URL parsing failed, please correct the URL and try again: Invalid argument` (exit 64).

```bash
mount_smbfs //USER:$PASS@IP/SHARE /mount/path
```

**Share name conventions:**
- `Users` — the default Windows share for user profiles (contains user directories)
- `C$` — admin share for the entire C: drive (requires admin credentials)
- Custom share — any folder the user explicitly shared on Windows

**After mounting:**
- Files appear under `/mount/path/` with read/write access
- Performance is sufficient for inspecting and copying data (typically 50-200 MB/s on LAN)
- NOT suitable for live training — copy data locally first for repeated access

### ⚠️ Large File / Archive Performance

**Do NOT extract archives directly to SMB mounts.** Extracting a 6 GB tar.gz with 72K small files to SMB took ~2.4 hours and was still only 12% complete. Each file write goes over the network.

**Correct approach:**
```bash
# ❌ Slow: extract to SMB directly
tar xzf /smb/path/archive.tar.gz -C /smb/path/  # 2+ hours for 6 GB

# ✅ Fast: extract locally on macOS SSD
mkdir -p /tmp/local_extract
tar xzf /smb/path/archive.tar.gz -C /tmp/local_extract  # ~20 minutes

# Optional: copy back to SMB after extraction
cp -r /tmp/local_extract/ /smb/path/
```

**Detection:** If tar seems stuck, use `lsof -p <PID>` to check if file descriptor 5w (write) is changing. If no change in 60 seconds, I/O is blocked.

### 5. Cleanup

```bash
diskutil unmount /tmp/thinkpad_data
# or
umount /tmp/thinkpad_data
```

The mount disappears on reboot automatically.

## Mounting via Finder (Alternative)

For a GUI approach:
1. Open Finder → Go → Connect to Server (Cmd+K)
2. Enter: `smb://IP/SHARE`
3. Enter credentials when prompted
4. Share appears in Finder sidebar

## Common Failure Modes

| Symptom | Likely Cause | Fix |
|---------|-------------|-----|
| `mount_smbfs: URL parsing failed, please correct the URL and try again: Invalid argument` (exit 64) | **Chinese/non-ASCII share name**, or special chars in password not URL-encoded | URL-encode password AND share name with `urllib.parse.quote(..., safe='')`, then use `osascript mount volume` — never `mount_smbfs` for Chinese share names |
| `server rejected the connection: Authentication error` | Wrong username or password | Try different user/pass combos; check caps lock |
| `mount_smbfs: server rejected the connection: Authentication error` | Same — Windows rejected creds | Verify the user exists on the Windows machine |
| `ping: cannot resolve HOST.local` | mDNS not running on target | Use IP directly instead of hostname |
| SMB port open but no shares visible | No shares configured or firewall blocking | Check Windows "Turn on file and printer sharing" |
| `mount_smbfs: mount point not available` | Target directory doesn't exist | Create it first with `mkdir -p` |
| Timeout on `smbclient` command | macOS Homebrew samba conflicts with system tools | Use native `mount_smbfs`/`smbutil` instead |
| TCP port open (ping works) but mount/view times out at app layer | **Proxy env var intercepting traffic** (`http_proxy`/`https_proxy`). Python raw sockets bypass proxy (showing OPEN) but terminal SMB/HTTP tools route through proxy, which can't reach internal IPs | Check `env | grep -i proxy`. Fix: `unset http_proxy https_proxy HTTP_PROXY HTTPS_PROXY` before running SMB commands. For curl: `--noproxy '*'`. Add internal IP ranges (`100.0.0.0/8`, `10.0.0.0/8`) to `no_proxy` env var |
| `mount_smbfs` hangs/times out from terminal, but Finder can connect | macOS terminal session has proxy env set; or SMB protocol version mismatch. `mount_smbfs` sometimes exits with code 64 / "File exists" misleading error | **Fix A (proxy):** unset http_proxy/https_proxy in shell. **Fix B (Finder CLI):** use `open 'smb://user:pass@host/share'` which launches Finder and mounts correctly. **Fix C (script):** `subprocess.run(['osascript', '-e', 'mount volume "smb://user:pass@host/share"'])` |
| VPN client (Shadowrocket/Clash) intercepts internal NAS traffic | Proxy tool routes `100.x.x.x` or `192.168.x.x` through external proxy instead of direct | Shadowrocket: Config → Rules → add `IP-CIDR,100.198.0.0/24,DIRECT` at top. Clash: add `ip-cidr: 100.198.0.0/24` to direct section |
| Web API works but SMB mount from terminal always fails | macOS mount_smbfs doesn't support the server's SMB dialect, or password encoding in the URL is wrong | Use Synology DSM Web API via Python as reliable fallback (see `references/synology-dsm-web-api.md`). Or use `open smb://` via Finder which handles auth correctly |

## Techniques

### Parsing Windows .lnk Shortcuts

When browsing a mounted SMB share, you may find .lnk files pointing to other NAS paths. Parse them to extract the target UNC path:

```python
# Quick UTF-16LE string extraction from .lnk binary
with open("shortcut.lnk", "rb") as f:
    data = f.read()
texts = []
i = 0
while i < len(data) - 1:
    if data[i] != 0 and data[i+1] == 0:
        j = i
        while j < len(data) - 1 and not (data[j] == 0 and data[j+1] == 0):
            j += 2
        if j > i:
            s = data[i:j].decode('utf-16-le', errors='replace')
            if len(s) > 3: texts.append(s)
        i = j + 2
    else: i += 1
for t in texts:
    if '\\\\' in t: print(repr(t))
```

Full reference: `references/lnk-shortcut-parsing.md`

## References

- `references/lnk-shortcut-parsing.md` — Parse Windows .lnk shortcuts to extract SMB UNC paths
- `references/windows-openssh-via-smb.md` — Install OpenSSH on a Windows VM when only SMB file access is available (no internet, no WinRM, no existing SSH). Covers portable OpenSSH download, batch script install, and Windows admin authorized_keys quirk.
- `references/windows-docker-via-ssh.md` — Install Docker Desktop and load images on a remote Windows machine via SSH. Covers winget install, Docker Desktop via SMB, WSL2 setup, engine-start issues via SSH, and common encoding/architecture pitfalls.
- `references/synology-dsm-web-api.md` — Synology NAS DSM Web API: browse shares, list directories, and download files via HTTP when SMB mount fails. Covers authentication (SYNO.API.Auth), FileStation.List, and FileStation.Download endpoints.

## Windows ↔ macOS Notes

- macOS SMB client can access Windows servers without SMB protocol version negotiation issues (SMB2/3 auto-negotiated)
- No need to install anything on the Windows machine — just enable File Sharing in Windows Settings
- `mount_smbfs` uses your macOS user's UID/GID for file ownership; all files appear owned by you
