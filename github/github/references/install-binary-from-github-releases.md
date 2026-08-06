---
name: install-binary-from-github-releases
description: Download and install a pre-built CLI binary from a GitHub repository's latest release. Handles platform detection, download, checksum verification, and PATH installation.
tags: [github, binary, install, release, cli, download, darwin, arm64, amd64]
---

# Install Pre-built Binary from GitHub Releases

Use this when the user wants to install a CLI tool from a GitHub repo that publishes pre-built binaries in its releases page.

## Trigger

- User says "install X from github.com/owner/repo" or provides a GitHub URL for a tool
- The tool has pre-built binaries (not just source code) in GitHub Releases
- You've confirmed there's no homebrew/apt/pkg manager route first

## Steps

### 1. Check for package manager alternatives first

```bash
# Homebrew (macOS)
brew search <tool-name>

# If exists, prefer that instead
```

### 2. Identify platform and architecture

```bash
uname -m
# darwin-arm64 on Apple Silicon Mac
# darwin-amd64 on Intel Mac
# linux-amd64 / linux-arm64 on Linux
```

Also detect OS: `uname -s` (Darwin, Linux) then lowercase.

### 3. Check GitHub Releases via API

```bash
# Get latest release info
curl -s https://api.github.com/repos/OWNER/REPO/releases/latest | python3 -c "
import sys, json
d = json.load(sys.stdin)
print('Tag:', d.get('tag_name', ''))
for a in d.get('assets', []):
    print(f'{a[\"name\"]}  ({a[\"size\"]} bytes)')
"
```

### 4. Download the matching binary

Look for the asset that matches `<tool-name>-<os>-<arch>` (e.g. `ccx-darwin-arm64`).

```bash
cd /tmp
curl -sLO https://github.com/OWNER/REPO/releases/latest/download/ASSET_NAME
```

### 5. Verify checksum

Download the `.sha256` file and verify:

```bash
cd /tmp
EXPECTED=$(cat ASSET_NAME.sha256 | awk '{print $1}')
ACTUAL=$(shasum -a 256 ASSET_NAME | awk '{print $1}')
echo "Expected: $EXPECTED"
echo "Actual:   $ACTUAL"
if [ "$EXPECTED" = "$ACTUAL" ]; then echo "OK - checksum matches"; else echo "FAIL - checksum mismatch"; fi
```

Some `.sha256` files have the path in the second field; the `awk '{print $1}'` handles both formats.

### 6. Install to PATH

```bash
chmod +x /tmp/ASSET_NAME
sudo mv /tmp/ASSET_NAME /usr/local/bin/TOOL_NAME
```

### 7. Verify installation

```bash
# Run the tool with version/help flag
TOOL_NAME version
TOOL_NAME --help
# Or whatever the tool supports
```

## Pitfalls

- **Go binaries** usually respond to `toolname version` not `toolname --version`. Try both.
- **sha256sum format varies**: sometimes `hash filename`, sometimes just `hash`. The `awk '{print $1}'` approach handles both.
- **macOS permissions**: after `sudo mv`, you need `sudo chmod +x` because mv preserves original permissions, but the binary may lose execute bit across filesystems.
- **Not all repos use semantic versioning**: Check the tag name format (v1.2.3 vs 1.2.3).
- **Some repos name assets differently**: Check for patterns like `tool_os_arch.tar.gz`, `tool-os-arch.zip`, etc. May need to extract from archive first.
- **Corporate VPN/GFW / SSL failures**: If curl to GitHub gives `SSL_ERROR_SYSCALL` or hangs, try these alternatives in order:
  1. **`gh` CLI** (if configured with stored token) — `gh release download -R owner/repo` or `gh api repos/owner/repo/releases/latest` may work even when direct curl fails, because `gh` uses a different auth path.
  2. **HTTP proxy** — If the user has a VPN/proxy (e.g. Shadowrocket on port 1082), set `export https_proxy=http://127.0.0.1:1082` before curl. Note: **SOCKS5 proxy at the same port often fails** to resolve GitHub domains — HTTP proxy is the right one.
  3. **Install to `~/.local/bin/` instead of `/usr/local/bin/`** — Avoids sudo requirement when the one-line `curl | sh` installation fails. This also works around sudo password prompts.
  4. **Fallback: raw.githubusercontent.com may be blocked** even when github.com works. Always try the Release download URL (github.com/OWNER/REPO/releases/latest/download/) instead.
