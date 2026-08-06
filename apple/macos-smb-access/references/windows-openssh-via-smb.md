# Windows OpenSSH Install via SMB (No Internet on VM)

When a Windows VM has no internet access (company network restrictions) but SMB is accessible, use this portable approach: download OpenSSH on the Mac, copy via SMB, install on Windows.

## Prerequisites

- Mac has internet (via Shadowrocket proxy, port 1082)
- SMB mount to Windows VM is active (`mount_smbfs //USER:PASS@IP/Share /path/to/mount`)
- curl with proxy: `-x http://127.0.0.1:1082`

## Step 1: Download Portable OpenSSH on Mac

```bash
# Find the latest release URL
curl -skL -x http://127.0.0.1:1082 \
  "https://github.com/PowerShell/Win32-OpenSSH/releases" 2>&1 | \
  grep -o 'href="[^"]*Win64[^"]*\.zip"' | head -1

# Example result: /PowerShell/Win32-OpenSSH/releases/download/10.0.0.0p2-Preview/OpenSSH-Win64.zip

# Download (construct full GitHub URL)
curl -skL -x http://127.0.0.1:1082 \
  -o /tmp/OpenSSH-Win64.zip \
  "https://github.com/PowerShell/Win32-OpenSSH/releases/download/10.0.0.0p2-Preview/OpenSSH-Win64.zip"
```

**Verify:** `ls -lh /tmp/OpenSSH-Win64.zip` — should be ~5.4MB, not 9 bytes (9B = redirect/error page).

> ⚠️ **API rate limit:** Don't use the GitHub API (`api.github.com/.../releases/latest`) — it's ratelimited. Scrape the releases HTML page instead.

> ⚠️ **Release URL format changes:** The URL `v9.5.0.0p1-Beta/OpenSSH-Win64-v9.5.0.0.zip` returns 404. Use the actual release tag (e.g. `10.0.0.0p2-Preview`).

## Step 2: Copy via SMB to Windows Desktop

```bash
cp /tmp/OpenSSH-Win64.zip /path/to/smb/mount/User/Desktop/
```

## Step 3: Batch Install Script (to run on Windows)

Place this as `install-openssh.bat` alongside the ZIP on the Windows Desktop:

```batch
@echo off
set ZIP=%USERPROFILE%\Desktop\OpenSSH-Win64.zip
set DEST=%ProgramFiles%\OpenSSH

if not exist "%ZIP%" (
    echo ERROR: %ZIP% not found!
    pause & exit /b 1
)

echo [1/5] Extracting...
if not exist "%DEST%" mkdir "%DEST%"
powershell -Command "Expand-Archive -Path '%ZIP%' -DestinationPath '%DEST%' -Force"

echo [2/5] Installing sshd service...
cd /d "%DEST%\OpenSSH-Win64"
powershell -ExecutionPolicy Bypass -File install-sshd.ps1

echo [3/5] Setting auto-start...
sc.exe config sshd start=auto
sc.exe config ssh-agent start=auto

echo [4/5] Starting services...
net start sshd
net start ssh-agent

echo [5/5] Firewall rule...
netsh.exe advfirewall firewall add rule name="OpenSSH Server" dir=in action=allow protocol=TCP localport=22

echo DONE. Connect: ssh USER@IP
pause
```

On the Windows machine, **right-click** the .bat file → **Run as administrator**.

## Step 4: SSH Key Authentication (Windows Quirks)

Windows OpenSSH uses a **different authorized_keys file for admin users**:

```bash
# On Mac: copy public key to Windows
sshpass -p 'PASSWORD' ssh-copy-id -o StrictHostKeyChecking=no USER@IP
# If that doesn't work, manually add the key:
```

On Windows OpenSSH, the key file path depends on the user's admin status:

| User Type | authorized_keys Location | 
|-----------|------------------------|
| Non-admin | `%USERPROFILE%\.ssh\authorized_keys` |
| **Admin** (default) | **`%ProgramData%\ssh\administrators_authorized_keys`** |

The `sshd_config` has a `Match Group administrators` section that overrides the key file:

```
AuthorizedKeysFile .ssh/authorized_keys
...
Match Group administrators
       AuthorizedKeysFile __PROGRAMDATA__/ssh/administrators_authorized_keys
```

If the Windows user is in the Administrators group (which is typical), keys go to `administrators_authorized_keys`:

```powershell
# Run these on Windows as Administrator, or push via SSH with sshpass:
$pub = "ssh-ed25519 AAAAC3NzaC1lZDI1NTE5AAAA... user@host"
Add-Content "$env:ProgramData\ssh\administrators_authorized_keys" $pub
icacls "$env:ProgramData\ssh\administrators_authorized_keys" /inheritance:r /grant "SYSTEM:(R)" /grant "BUILTIN\Administrators:(R)"
```

**Permissions are critical** — Windows OpenSSH refuses to use the authorized_keys file if SYSTEM or Administrators don't have Read access, or if the file inherits wider permissions.

## Verification

```bash
# Test passwordless login
ssh -o ConnectTimeout=5 USER@IP "hostname"
# Should return the Windows hostname without prompting for password

# Test remote command execution
ssh USER@IP "powershell -Command Get-Service sshd | Format-Table Status,Name"
```

## Common Pitfalls

| Issue | Fix |
|-------|-----|
| `install-sshd.ps1` execution policy blocks | Use `-ExecutionPolicy Bypass` flag |
| DISM hangs on "映像版本" | DISM is slow in VM — use portable ZIP method instead (bypasses Windows component store) |
| `sc config sshd` fails with "not a command" | The batch file's PATH doesn't include `C:\Windows\System32\`. Use hardcoded paths: `C:\Windows\System32\sc.exe` |
| SSH connects but pubkey fails | Check `administrators_authorized_keys` permissions with `icacls` |
| SSH refuses connection | Check Windows Defender Firewall: `netsh advfirewall firewall show rule name="OpenSSH"` |
| Chinese text in batch shows garbled / SSH output is unreadable | Remove `chcp 65001` — it breaks default Chinese Windows console. Use `chcp 437` instead for English output. Keep all script content ASCII-only. |
