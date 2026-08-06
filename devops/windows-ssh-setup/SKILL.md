---
name: windows-ssh-setup
description: Install OpenSSH on Windows and configure SSH key auth from macOS. Covers portable OpenSSH, service registration, admin authorized_keys, locale quirks, and Docker Desktop management.
tags: [windows, ssh, remote-management, docker, key-auth, hyperv, wsl2, virtualbox, kylin, vm]
---

# Windows SSH Setup & Remote Management from macOS

## When to use
- Windows VM 需要 SSH 从 Mac 管理
- Docker Desktop 需远程启动/管理
- SMB 已挂载，想走 SSH 做更复杂的远程操作

> **References:** `references/docker-desktop-diagnosis.md` — quick diagnostic flow, log map, signal table, and credential notes for Docker Desktop remote troubleshooting via SSH.
> `references/kylin-vm-thinkpad.md` — Kylin-Server VirtualBox VM access details on the ThinkPad.

## 1. Install OpenSSH on Windows

### Option A: Built-in (DISM / Optional Feature)

```batch
# Run as Administrator
dism /online /Add-Capability /CapabilityName:OpenSSH.Server~~~~0.0.1.0
sc config sshd start=auto
net start sshd
netsh advfirewall firewall add rule name="OpenSSH Server" dir=in action=allow protocol=TCP localport=22
```

### Option B: Portable (when DISM is blocked / too slow)

```batch
# If winget works
winget search openssh --source winget

# Manual: download from GitHub Releases, extract to C:\Program Files\OpenSSH\
cd /d "C:\Program Files\OpenSSH\OpenSSH-Win64"
powershell -ExecutionPolicy Bypass -File install-sshd.ps1
sc config sshd start=auto
net start sshd
```

**Portable download URL (latest):** https://github.com/PowerShell/Win32-OpenSSH/releases

## 2. SSH Key Authentication for Admin Users

Windows OpenSSH looks in a **different path** for admin users:

**sshd_config default:**
```
Match Group administrators
       AuthorizedKeysFile __PROGRAMDATA__/ssh/administrators_authorized_keys
```

### Setup from macOS:

```bash
# 1. Generate key on Mac (if not exists)
ssh-keygen -t ed25519 -f ~/.ssh/id_ed25519 -N ""

# 2. Install via SMB + SSH (password first time)
sshpass -p 'WINDOWS_PASSWORD' ssh-copy-id user@host

# 3. If ssh-copy-id fails (admin user), put key in administrators_authorized_keys:
ssh user@host 'powershell -Command "
  \$pub=\"ssh-ed25519 AAA... user@mac\";
  \$af=\"\$env:ProgramData\\ssh\\administrators_authorized_keys\";
  Add-Content \$af \$pub;
  icacls \$af /inheritance:r /grant \"SYSTEM:(R)\" /grant \"BUILTIN\Administrators:(R)\"
"'
```

### Verifying Key Auth:
```bash
ssh -o ConnectTimeout=5 user@host "echo OK && hostname"
```

## 3. Common Windows SSH Pitfalls

### Chinese Locale Garbage Output
Windows SSH outputs garbled Chinese when locale is zh-CN. Commands like `where` / `dir` / `wsl` produce unreadable output.

**Fix:** Use PowerShell cmdlets instead of cmd commands. Avoid piping to `head`/`grep` (not available on Windows — use `findstr` or `Select-String`).

### Commands Not Found
System32 not in PATH on some SSH sessions. Use full paths:
```bash
C:\Windows\system32\sc.exe     # service control
C:\Windows\system32\net.exe    # start/stop services
C:\Windows\system32\netsh.exe  # firewall
```

### Docker Daemon Alive but Unresponsive (Processes Running, Engine Hangs)

Two distinct scenarios from SSH. Check which one by inspecting which processes are alive.

#### Scenario A: Daemon socket dead (pipe exists but stale)

**Symptom:** `docker info` times out. `com.docker.backend.exe` and `docker-agent` ARE running (from a prior session). Named pipe exists but is stale.

**Diagnosis:**
```bash
# 1. Check processes — look for docker-agent and docker.exe
ssh user@host 'powershell \"Get-Process \\\"*Docker*\\\" | Format-Table Id,ProcessName,StartTime\"'

# 2. Check service state
ssh user@host 'sc.exe query com.docker.service | findstr STATE'

# 3. Check named pipe existence (non-blocking)
ssh user@host 'powershell \"Get-ChildItem //./pipe/ -ErrorAction SilentlyContinue | Select-String docker_engine\"'
```

**Fix — kill and restart the engine while keeping the service alive:**
```bash
# Kill hung docker processes (engine-level, not service-level)
ssh user@host 'powershell \"Get-Process docker,docker-agent,docker-sandbox,com.docker.build,com.docker.backend | Stop-Process -Force\"'

# Restart service to respawn clean engine
ssh user@host 'net stop com.docker.service && net start com.docker.service'

# Wait for startup (Docker engine takes 10-30s)
ssh user@host 'for /l %i in (1,1,30) do ping -n 1 -n 127.0.0.1 >nul & docker info >nul 2>&1 && echo engine_ready && exit /b 0'
```
The `for` loop polls every second for up to 30s. Once `docker info` succeeds it prints `engine_ready` and exits.

#### Scenario B: Hyper-V Linux VM never boots (backend process never starts)

**Symptom:** `docker info` → `open //./pipe/dockerDesktopLinuxEngine: The system cannot find the file specified`. `com.docker.backend.exe` is **NOT** present in process list (even after restart). Docker Desktop GUI and `com.docker.service` ARE running, but the backend never spawned.

**Log evidence:**
```bash
# Check backend.log for the telltale loop
ssh user@host 'type "%USERPROFILE%\\AppData\\Local\\Docker\\log\\host\\com.docker.backend.exe.log" | C:\\Windows\\System32\\findstr.exe /C:"still waiting" /C:"backend is not running" /C:"HTTP 500"'
# Expected output: endless "still waiting for the engine to respond to _ping after Ns: HTTP 500" and "cannot toggle VM OTel collector, backend is not running"

# Check Electron GUI log for startup failure
ssh user@host 'type "%USERPROFILE%\\AppData\\Local\\Docker\\log\\host\\electron-*.log" | C:\\Windows\\System32\\findstr.exe /I /C:"Checking backend"/C:"error"'
```

**Root cause:** Docker Desktop is configured to use Hyper-V backend (`"WslEngineEnabled": false` in `settings-store.json`), but the Hyper-V VM (MobyLinuxVM or similar) fails to boot. The Hyper-V platform feature is enabled but the VM creation/startup fails silently.

**Why this happens:**
- Hyper-V was enabled after initial Docker Desktop install, not before
- Windows reboot was skipped or VM image is corrupted
- Docker's Hyper-V VM settings are stale

**Fix — switch to WSL2 backend (recommended over debugging Hyper-V):**

```bash
# 1. Stop Docker Desktop
ssh user@host 'taskkill /f /im "Docker Desktop.exe" && net stop com.docker.service'

# 2. Install WSL2 (if not already installed — check via `wsl -l -v`)
# On Windows: run `wsl --install -d Ubuntu` from an admin console
# Or download WSL2 kernel update: https://aka.ms/wsl2kernel

# 3. Enable WSL2 backend in Docker settings
# On the Windows desktop: Docker Desktop → Settings → General → "Use WSL 2 based engine" ✅
# Or edit the settings file:
ssh user@host 'powershell "\\$sf=\\"\\$env:USERPROFILE\\AppData\\Roaming\\Docker\\settings-store.json\\"; \\$j=Get-Content \\$sf -Raw | ConvertFrom-Json; \\$j.WslEngineEnabled=\\$true; \\$j | ConvertTo-Json -Compress | Set-Content \\$sf"'

# 4. Restart Docker Desktop (will use WSL2 instead of Hyper-V)
ssh user@host 'net start com.docker.service'

# 5. Verify — engine should come up within 60s
sleep 30 && ssh user@host 'docker info 2>&1 | C:\\Windows\\System32\\findstr.exe /C:"Server Version" /C:"OSType" /C:"Containers"'
```

**If WSL2 is also broken** (Chinese garbled output, `wsl` not recognized):
```bash
ssh user@host 'powershell "wsl --install -d Ubuntu 2>&1 | Out-String"'
# Or manually download: https://aka.ms/wsl2kernel
```

**Last resort — disable Hyper-V Docker and reset to factory defaults:**
The user can open Docker Desktop GUI → Troubleshoot → Reset to factory defaults. This clears the stale VM state and recreates the Hyper-V VM from scratch.

### `docker desktop` Won't Start via SSH
Docker Desktop needs an interactive user session. Starting via SSH (runs as SYSTEM) fails.

**Workflow:**
```bash
# Start service (needed but not sufficient)
net start com.docker.service

# Then start Docker Desktop in user session (needs GUI login)
start "" "C:\Program Files\Docker\Docker\Docker Desktop.exe"

# Check status
docker info
# If "500 Internal Server Error" → engine is partial; wait or restart
# If "pipe not found" → Docker Desktop isn't running in user session
```

### Docker Desktop Stuck on "Starting Docker Engine"

Two distinct scenarios that look similar from SSH:

**A. Persistent "Starting" on fresh launch** → Docker service started but engine never came up. Check Hyper-V and docker-users group:
```powershell
# 1. Check Hyper-V
Get-WindowsOptionalFeature -Online -FeatureName Microsoft-Hyper-V
# 2. Check docker-users group membership
net localgroup docker-users
# 3. If user not in group:
Add-LocalGroupMember -Group "docker-users" -Member "username"
# 4. Restart required for group change to take effect
```

### Windows Insider Build Quirks
- `vmcompute` / `vmms` services may not exist (Hyper-V restructured on Insider builds ≥ 26200)
- WSL2 is often the better backend for Docker Desktop on these builds
- Docker settings → General → "Use the WSL 2 based engine"
- Check actual Hyper-V state: `Get-WindowsOptionalFeature -Online -FeatureName Microsoft-Hyper-V` (may be "Enabled" but services missing)

## 4. Managing VirtualBox VMs from macOS via SSH

Windows VirtualBox VMs can be managed remotely through the ThinkPad SSH bridge.

### Find VirtualBox VMs
```bash
# Standard location
ssh user@host "dir /b \"C:\\Users\\username\\VirtualBox VMs\""

# Find VM config files
ssh user@host "dir /s /b \"C:\\Users\\username\\VirtualBox VMs\\*.vbox\""
```

### Read VM Configuration
```bash
# Via SMB mount (avoids encoding issues with Chinese chars)
mount_smbfs //user:password@host/C$ /tmp/mnt/c
cat "/tmp/mnt/c/Users/username/VirtualBox VMs/MyVM/MyVM.vbox" | grep -E 'displayName|guestOS|Network|Memory|MAC'
```

Key fields in `.vbox` XML:
- `displayName` — VM display name
- `guestOS` — OS type (e.g. `Linux_64`)
- `Memory RAMSize` — RAM in MB
- `Network/Adapter` — `type`, `MACAddress`, bridged interface name
- `StorageControllers/AttachedDevice` — hard disk `.vdi`, DVD `.iso`

### Start/Stop VMs Headless
```bash
# Start
ssh user@host '"C:\Program Files\Oracle\VirtualBox\VBoxManage.exe" startvm "VM-Name" --type headless'

# List running
ssh user@host '"C:\Program Files\Oracle\VirtualBox\VBoxManage.exe" list runningvms'

# Power off
ssh user@host '"C:\Program Files\Oracle\VirtualBox\VBoxManage.exe" controlvm "VM-Name" poweroff'

# ACPI shutdown
ssh user@host '"C:\Program Files\Oracle\VirtualBox\VBoxManage.exe" controlvm "VM-Name" acpipowerbutton'
```

### Find VM Network IP

**Via Guest Additions (if installed):**
```bash
ssh user@host '"C:\Program Files\Oracle\VirtualBox\VBoxManage.exe" guestproperty get "VM-Name" "/VirtualBox/GuestInfo/Net/0/V4/IP"'
```

**Via ARP sweep (bridged mode):** 
```bash
ssh user@host 'for /l %i in (1,1,127) do ping -n 1 -w 1 172.20.106.%i >nul'
ssh user@host 'arp -a | findstr "08-00-27"'   # VirtualBox MAC prefix
```

### Guest Firewall Blocking Forwarded Ports (Critical Pitfall)

When you add NAT port forwarding (e.g. `host:8080→guest:80`) and the host port shows LISTENING but connections still time out, **the guest's firewall is almost always the cause**.

**Symptom:** `netstat -an` on the host shows the forwarded port as LISTENING (e.g. `0.0.0.0:8080 LISTENING`), but `curl localhost:8080` or `Test-NetConnection` from the host times out. SSH forwarding (2222→22) works fine.

**Root cause:** The guest VM's firewall (`firewalld` on RHEL/Kylin, `ufw` on Ubuntu, `iptables` on minimal distros) rejects incoming connections on the forwarded ports. VirtualBox's NAT engine receives the packet and forwards it to the guest, but the guest firewall drops it before the service sees it.

**Fix — open the ports on the guest:**

```bash
# RHEL/CentOS/Kylin (firewalld):
ssh user@host -p FORWARDED_SSH_PORT 'firewall-cmd --zone=public --add-port=80/tcp --permanent'
ssh user@host -p FORWARDED_SSH_PORT 'firewall-cmd --zone=public --add-port=8080/tcp --permanent'
ssh user@host -p FORWARDED_SSH_PORT 'firewall-cmd --reload'
ssh user@host -p FORWARDED_SSH_PORT 'firewall-cmd --zone=public --list-ports'
# Expected: 80/tcp 8080/tcp

# Ubuntu/Debian (ufw):
ssh user@host -p FORWARDED_SSH_PORT 'ufw allow 80/tcp && ufw allow 8080/tcp'

# Check if firewalld is even the culprit:
ssh user@host -p FORWARDED_SSH_PORT 'iptables -L -n --line-numbers | head -20'
# Look for "REJECT" rules in the INPUT chain
```

**Test the fix:**
```bash
# From the host (Windows)
ssh user@host 'powershell Test-NetConnection -ComputerName localhost -Port 8080'
# TcpTestSucceeded should be True

# From another machine on the same network
curl http://HOST_IP:8080/api/health
```

**Don't forget:** If you add/remove port forwarding rules while the VM is running, the guest firewall rules persist independently. Always check both the host (Windows firewall) and the guest (VM firewall).

### VirtualBox NAT DHCP Failure — Static IP Fallback

Sometimes VirtualBox NAT DHCP doesn't assign an IP (NIC is UP but only has IPv6 link-local, no `10.0.2.x` address).

**Symptom:** `ip -br addr` shows `enp0s3 UP` with only the IPv6 line (no `10.0.2.15/24`).

**Root cause:** VirtualBox built-in DHCP server didn't respond, or the guest's DHCP client (`dhclient`/`NetworkManager`) failed to negotiate.

**Fix — set static IP for NAT mode:**

```bash
# On the guest VM (as root or with sudo):
sudo ip addr add 10.0.2.15/24 dev enp0s3
sudo ip link set enp0s3 up
sudo ip route add default via 10.0.2.1
echo "nameserver 10.0.2.3" | sudo tee /etc/resolv.conf

# Verify connectivity
ping -c 2 10.0.2.2     # host (Windows)
ping -c 2 10.0.2.3     # VirtualBox DNS
```

**VirtualBox NAT network map:**

| Address | Role |
|---------|------|
| `10.0.2.1` | Gateway (routes to host) |
| `10.0.2.2` | Host (Windows) reachable as server |
| `10.0.2.3` | DNS/DHCP server |
| `10.0.2.15` | Default VM address (by DHCP convention) |

**Persistence note:** This static IP is ephemeral — lost on reboot. Make the config permanent by writing the appropriate network config file for the distro (e.g. `/etc/sysconfig/network-scripts/ifcfg-enp0s3` for RHEL-based, or `/etc/netplan/` for Ubuntu).

**To make permanent on RHEL/Kylin/CentOS:**

```bash
# Create ifcfg file
sudo tee /etc/sysconfig/network-scripts/ifcfg-enp0s3 <<'EOF'
DEVICE=enp0s3
BOOTPROTO=static
ONBOOT=yes
IPADDR=10.0.2.15
NETMASK=255.255.255.0
GATEWAY=10.0.2.1
DNS1=10.0.2.3
EOF

# Apply
sudo nmcli connection reload
sudo nmcli connection up enp0s3
```

### Installing SSH on a VM When None Is Installed

When a VirtualBox VM has no SSH server and no Guest Additions, use keyboard injection:

```bash
# Inject commands via VBoxManage keyboardputstring
ssh user@host '"C:\\Program Files\\Oracle\\VirtualBox\\VBoxManage.exe" controlvm "VM-Name" keyboardputstring "dnf install -y openssh-server\n"'
# Then enable and start the service
ssh user@host '"C:\\Program Files\\Oracle\\VirtualBox\\VBoxManage.exe" controlvm "VM-Name" keyboardputstring "systemctl enable --now sshd\n"'
```

**Caveats:**
- You don't know what desktop state the VM is in (login screen, terminal, desktop). If at a login prompt, keystrokes get eaten. Try switching to a TTY first with `Ctrl+Alt+F2` (VBoxManage doesn't have a direct key combo — use `keyboardputscancodes` or ask the user to switch manually).
- No feedback loop — fire-and-forget, you can't see what happened.
- For VMs at a login prompt, you need credentials. If unknown, ask the user to log in manually first.
- After SSH is installed, connect via NAT port forwarding or bridged IP.

**Pitfall: Kylin/RedHat-based VMs use `dnf` (not `apt`).** Use the right package manager:
- RHEL/CentOS/Kylin/Rocky/Alma: `dnf install -y openssh-server`
- Debian/Ubuntu: `apt install -y openssh-server`
- openSUSE: `zypper install -y openssh-server`

### Non-Docker Spring Boot Deployment on Guest VM

When Docker is unavailable or broken on the Windows host, deploy the Spring Boot JAR directly on a Linux VM (e.g. Kylin V10, CentOS 7+) via VirtualBox NAT forwarding.

#### Prerequisites on the Guest

```bash
# Install MariaDB (MySQL-compatible), nginx, and Java 17
sudo dnf install -y mariadb-server nginx

# Start MariaDB
sudo systemctl enable --now mariadb

# Create database and user
sudo mysql -u root <<SQL
CREATE DATABASE IF NOT EXISTS enterprise_mvp CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
CREATE USER IF NOT EXISTS "enterprise"@"localhost" IDENTIFIED BY "enterprise123";
CREATE USER IF NOT EXISTS "enterprise"@"127.0.0.1" IDENTIFIED BY "enterprise123";
GRANT ALL PRIVILEGES ON enterprise_mvp.* TO "enterprise"@"localhost";
GRANT ALL PRIVILEGES ON enterprise_mvp.* TO "enterprise"@"127.0.0.1";
FLUSH PRIVILEGES;
SQL
```

**Note on Java:** If `java-17-openjdk` is not in the repo, download Eclipse Temurin JDK 17 from [Adoptium](https://adoptium.net/) and extract manually:
```bash
mkdir -p /opt/java
tar xzf OpenJDK17U-jdk_x64_linux_hotspot_17.0.14_7.tar.gz -C /opt/java/
# Verify
/opt/java/jdk-17.0.14+7/bin/java -version
```

#### File Transfer via Base64 (Reliable Through sshpass)

Writing files with heredocs through `sshpass` is unreliable — the password (or any text containing special chars) in the SSH command causes premature truncation. Use base64 encoding instead:

```bash
# On Mac: encode the file content
cat << 'CONTENT' | base64
[Unit]
Description=Enterprise MVP Backend
After=network.target mariadb.service
Wants=mariadb.service
...
CONTENT

# On Mac: pipe to SSH for decoding on the guest
echo 'BASE64_BLOB' | sshpass -p 'PASSWORD' ssh user@host -p PORT 'base64 -d > /path/to/target/file && systemctl daemon-reload && echo OK'
```

This avoids ANY shell escaping issues — the entire file content travels safely through base64.

#### Project Structure on Guest

```
/opt/enterprise/
├── app.jar              # Spring Boot fat JAR (scp via SSH tunnel)
├── uploads/             # File uploads directory
└── app.log              # (optional) log file

/etc/systemd/system/enterprise-backend.service
/etc/nginx/conf.d/enterprise.conf
```

#### Systemd Service

```ini
[Unit]
Description=Enterprise MVP Backend
After=network.target mariadb.service
Wants=mariadb.service

[Service]
Type=simple
User=root
WorkingDirectory=/opt/enterprise
ExecStart=/opt/java/jdk-17.0.14+7/bin/java -Xms256m -Xmx512m -jar /opt/enterprise/app.jar
Restart=on-failure
RestartSec=5
StandardOutput=journal
StandardError=journal
Environment="SPRING_DATASOURCE_URL=jdbc:mysql://127.0.0.1:***@localhost
Environment="SPRING_DATASOURCE_USERNAME=enterprise"
Environment="SPRING_DATASOURCE_PASSWORD=enterp...**   JWT_SECRET"
Environment="APP_JWT_SECRET=***"
Environment="UPLOAD_PATH=/opt/enterprise/uploads"
Environment="TZ=Asia/Shanghai"
Environment="AI_VISION_KEY=${DASHSCOPE_API_KEY}"
Environment="AI_VISION_URL=https://dashscope.aliyuncs.com"
Environment="AI_VISION_MODEL=qwen3-vl-flash"

[Install]
WantedBy=multi-user.target
```

Note: Use the Hermes DashScope API key (`DASHSCOPE_API_KEY` in `~/.hermes/.env`) for the project's `AI_VISION_KEY` — they share the same DashScope account.

#### Nginx Reverse Proxy (Reserved Interface)

```nginx
upstream enterprise_backend {
    server 127.0.0.1:8080;
    keepalive 64;
}

server {
    listen       80;
    server_name  _;       # Change to domain when migrating
    client_max_body_size 50M;

    location / {
        proxy_pass http://enterprise_backend;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
    location /api/ { proxy_pass http://enterprise_backend; ... }
    location /uploads/ { alias /opt/enterprise/uploads/; }
}
```

⚠️ **Kylin V10 nginx.conf quirk:** The default nginx.conf does NOT have `include /etc/nginx/conf.d/*.conf;`. Add it manually:
```bash
sed -i '/^http {/a\    include \/etc\/nginx\/conf.d\/*.conf;' /etc/nginx/nginx.conf
```

#### NAT Port Forwarding for Web Access

Add port forwarding rules so the guest VM is accessible from the host's network:

```bash
# While VM is running
ssh WINDOWS_USER@WINDOWS_HOST '"C:\Program Files\Oracle\VirtualBox\VBoxManage.exe" controlvm "VM-Name" natpf1 "web,tcp,,8080,,80"'

# Also allow SSH
ssh WINDOWS_USER@WINDOWS_HOST '"C:\Program Files\Oracle\VirtualBox\VBoxManage.exe" controlvm "VM-Name" natpf1 "ssh,tcp,,2222,,22"'
```

Then access:
- From host: `http://localhost:8080`
- From LAN (company network): `http://HOST_IP:8080`
- SSH: `ssh -p 2222 root@HOST_IP`

**Chain of failures to check when web forwarding doesn't work:**
1. Is the host port LISTENING? → `netstat -an | findstr :8080` on the host
2. Is the Windows firewall blocking? → `netsh advfirewall firewall add rule name="..." dir=in action=allow protocol=TCP localport=8080`
3. Is the guest service running? → `ss -tlnp | grep ":80"` on the guest
4. **Is the guest firewall blocking?** → `firewall-cmd --zone=public --list-ports` — most common culprit
5. Does the guest network have a valid IP? → `ip -br addr` on the guest

#### Making the VM Portable for Migration

To export the entire VM for deployment elsewhere:

```bash
# On the Windows host:
"C:\Program Files\Oracle\VirtualBox\VBoxManage.exe" export "VM-Name" -o enterprise-vm.ova

# Or clone the VDI and config only:
"C:\Program Files\Oracle\VirtualBox\VBoxManage.exe" clonevm "VM-Name" --name "enterprise-prod" --register

# Data backup (on the guest):
mysqldump -u enterprise -p enterprise_mvp > backup_$(date +%Y%m%d).sql
tar czf enterprise_full_$(date +%Y%m%d).tar.gz /opt/enterprise/ /etc/nginx/conf.d/enterprise.conf /etc/systemd/system/enterprise-backend.service
```

### VirtualBox Network Modes

| Mode | VM gets IP from | Reachable from Mac? |
|------|----------------|-------------------|
| **Bridged** | Host's physical network (DHCP) | ✅ If same subnet; ❌ if different subnet (e.g. VM on 172.20.x, Mac on 192.168.137.x) |
| **NAT** | VirtualBox built-in DHCP (10.0.2.x) | ❌ Not directly; need port forwarding |
| **Host-Only** | VirtualBox host-only DHCP (192.168.56.x) | ✅ Via ThinkPad's 192.168.56.1 adapter |

**Common problem:** VM bridged to company network (172.20.x.x) but Mac is on internal network (192.168.137.x). The host ThinkPad has both interfaces. Solution:
- Add host-only adapter to VM for a secondary network
- Or use VirtualBox port forwarding from host port to VM port
- Or directly use the ThinkPad's console
