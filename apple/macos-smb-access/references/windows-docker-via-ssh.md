# Docker on Windows via SSH (from macOS)

Use SSH to install and run Docker Desktop on a remote Windows machine, then load images.

## Prerequisites

- SSH access to Windows (see `references/windows-openssh-via-smb.md`)
- Windows user is in Administrators group
- Docker Desktop installer (~628MB) — download first: `~/Downloads/docker/DockerDesktopInstaller.exe`

## Installation

### 1. Install Docker Desktop

Use winget (faster than manual download on slow connections):

```bash
# Remove msstore source to avoid interactive agreement prompts
ssh USER@IP "winget source remove msstore"

# Install silently
ssh USER@IP "winget install Docker.DockerDesktop --silent --accept-package-agreements --disable-interactivity"
```

**Alternative:** If winget download is slow, download installer on Mac and copy via SMB:

```bash
# Mac side: download once (proxy: -x http://127.0.0.1:1082)
curl -skL -o ~/Downloads/docker/DockerDesktopInstaller.exe \
  "https://desktop.docker.com/win/main/amd64/229452/Docker%20Desktop%20Installer.exe"

# Copy via SMB to Windows Desktop
cp ~/Downloads/docker/DockerDesktopInstaller.exe /path/to/smb/mount/Desktop/

# Windows side: run installer silently
ssh USER@IP '"C:\Users\USER\Desktop\DockerDesktopInstaller.exe" install --quiet --accept-license'
```

### 2. Verify Installation

```bash
ssh USER@IP "docker --version"
# Expected: Docker version 29.x.x
```

### 3. Configure Docker Service for Auto-Start

```batch
ssh USER@IP "powershell -Command \"Start-Service com.docker.service; sc.exe config com.docker.service start=auto\""
```

## Starting Docker Engine (the tricky part)

Docker Desktop on Windows **requires an interactive GUI session** to start the engine. SSH runs as a service, so `Start-Process "Docker Desktop.exe"` in SSH may not work reliably.

### Method A: WSL2 + Native Docker (recommended)

Install WSL2 first, then Docker natively inside WSL:

```bash
ssh USER@IP "wsl --install -d Ubuntu"
# Wait for WSL install to complete (can take 5-10 min)
# Then install Docker inside WSL:
ssh USER@IP 'wsl -d Ubuntu -- bash -c "curl -fsSL https://get.docker.com | sh"'
```

This gives a proper Docker daemon that works over SSH without needing Docker Desktop's GUI.

### Method B: Docker Desktop via GUI (if user is interactive)

Place a batch script on the Windows Desktop:

```batch
@echo off
@set PATH=C:\Windows\system32;C:\Windows;C:\Program Files\Docker\Docker\resources\bin;%PATH%

echo Starting Docker Desktop...
start "" "C:\Program Files\Docker\Docker\Docker Desktop.exe"

echo Waiting for engine...
for /l %%i in (1,1,24) do (
    timeout /t 5 /nobreak >nul
    docker.exe info >nul 2>&1
    if !errorlevel! equ 0 (
        echo Docker started!
        docker.exe load -i "%USERPROFILE%\Desktop\enterprise-backend.tar"
        goto :eof
    )
)
echo Failed to start in 120s. Open Docker Desktop GUI manually.
```

The user double-clicks this on the Windows desktop.

## Loading a Docker Image

```bash
# Transfer image to Windows first (via SMB)
cp mac-image.tar /path/to/smb/mount/Desktop/

# Then load via SSH (after engine is running)
ssh USER@IP "docker load -i C:\Users\USER\Desktop\image-name.tar"

# Verify
ssh USER@IP "docker images"
```

## Common Pitfalls

| Issue | Cause | Fix |
|-------|-------|-----|
| `docker ps` works but `docker info` fails on engine | Docker Desktop engine not started — needs GUI session | Install Docker in WSL instead, or run `wsl --install -d Ubuntu` first |
| `com.docker.service` keeps stopping | Service set to manual start | Run `sc.exe config com.docker.service start=auto` |
| `wsl -l -v` output garbled | SSH encoding mismatch with Chinese Windows locale | Use `@chcp 437 >nul` at top of batch scripts; avoid Chinese characters in commands |
| Winget asks for msstore agreement | Interactive prompt blocks non-interactive SSH | `winget source remove msstore` before installing |
| Docker Desktop installs but engine pipe doesn't appear | WSL2 not installed | Run `wsl --install -d Ubuntu` first, restart, then Docker Desktop |
| Image is `linux/arm64` and won't run on Windows x86 | Wrong architecture | Build image with `--platform linux/amd64` or use Colima with `--arch x86_64` on Mac |
| Image tar load is very slow | Large image over network | Copy tar to Windows local disk first (via SMB), then `docker load` from there |
| `chcp 65001` breaks batch file | Windows Chinese locale + UTF-8 code page | Use `chcp 437` instead, or omit entirely. Keep all script content ASCII-only. |

## Before Installing: Check What Already Exists

Common mistake: re-downloading what's already there. Always verify first:

```bash
# Check if Docker is already installed (not just CLI, but engine)
ssh USER@IP "docker info"  # engine running?
ssh USER@IP "docker --version"  # CLI installed?

# Check if installer is already on Windows
ssh USER@IP "dir C:\Users\USER\Desktop\DockerDesktopInstaller.exe"
# Or check Mac downloads
ls ~/Downloads/docker/
ls ~/Downloads/*Docker*

# Check if WSL distros exist (Docker needs WSL2)
ssh USER@IP "wsl -l -v"

# Check Docker service
ssh USER@IP 'powershell "Get-Service *docker* | Format-Table Name,Status,StartType -AutoSize"'
```
