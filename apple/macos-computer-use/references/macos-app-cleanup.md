# macOS App Cleanup Reference

Detailed paths, sizes, and risk assessment for cleaning storage-heavy macOS apps.

## WeChat (微信)

| Item | Path | Typical Size | Safe to Delete? |
|------|------|-------------|-----------------|
| App data | `~/Library/Containers/com.tencent.xinWeChat/` | 8-15GB | ❌ Use in-app cleanup |
| Cache | WeChat → Settings → General → Storage | 3-8GB | ✅ Cache is safe |
| Chat history | Same menu → Manage chat history | 5-10GB | ⚠️ Personal data |

**Pitfall:** Never `rm -rf` the Containers directory. Tears app state.

## iMessage

| Item | Path | Typical Size | Safe to Delete? |
|------|------|-------------|-----------------|
| Caches | `~/Library/Messages/Caches/` | 3-5GB | ✅ Regenerates |
| Attachments | `~/Library/Messages/Attachments/` | 500MB-2GB | ⚠️ Actual photos/videos in chats |
| Sync state | `~/Library/Messages/Sync/` | 200-500MB | ✅ Sync will recreate |

## Google Chrome — Selective Cleanup

| Item | Path | Safe? | Notes |
|------|------|-------|-------|
| History | `Default/History` + `History-journal` | ✅ Safe | `rm` these files |
| Visited Links | `Default/Visited Links` | ✅ Safe | Navigation cache |
| Cookies | `Default/Cookies` + `Cookies-journal` | ⚠️ Keep unless asked | Logins stored here |
| Code Cache | `Default/Code Cache/` | ✅ Safe | JS compilation cache |
| Entire Default/ | `Default/` | ❌ Destructive | Nukes bookmarks, passwords, profiles |

## Google DriveFS (Offline Cache)

| Path | Typical | Safe? |
|------|---------|-------|
| `~/Library/Application Support/Google/DriveFS/<hash>/` | 500MB-5GB | ✅ Re-syncs on next launch |

## Docker

| Item | Path / Command | Typical | Notes |
|------|--------------|---------|-------|
| VM disk | `~/Library/Containers/com.docker.docker/Data/vms/0/data/Docker.raw` | 500MB-5GB real | Sparse file — check with `ls -ls` |
| Images | `docker system df` | Varies | `docker system prune -a` |
| Unused containers | `docker container prune` | Varies | |

## UTM Virtual Machines

| Path | Action |
|------|--------|
| `~/Library/Containers/com.utmapp.UTM/Data/Documents/<name>.utm/` | Delete entire `.utm` folder to remove VM |
| Cache: `...com.utmapp.UTM/Data/Library/Caches/` | ✅ Safe, clears QEMU caches (~316MB) |

## AI App Data

| App | Path | Typical | Notes |
|-----|------|---------|-------|
| Claude Code | `~/Library/Application Support/Claude-3p/claude-code/` | 200MB-2GB | Old version binaries safe to prune |
| codex-plusplus | `~/Library/Application Support/codex-plusplus/` | 1-2GB | `backup/` directory is old app bundles |

## Updater Caches

```bash
rm -rf ~/Library/Application\ Support/Google/GoogleUpdater/*
rm -rf ~/Library/Application\ Support/Quark/updates/*
rm -rf ~/Library/Application\ Support/TorBrowser-Data/UpdateInfo/*
```

## Apple Intelligence Caches (macOS 27+)

```bash
rm -rf ~/Library/Caches/com.apple.callintelligenced/*
rm -rf ~/Library/Caches/com.apple.textunderstandingd/*
```

## Time Machine Local Snapshots

```bash
tmutil listlocalsnapshots /
tmutil deletelocalsnapshots /
```

## Common Development Caches

| Cache | Path | Clean Command |
|-------|------|--------------|
| Homebrew | `~/Library/Caches/Homebrew/` | `brew cleanup --prune=all` |
| pip | `~/Library/Caches/pip/` | `pip cache purge` |
| npm | `~/.npm/` | `npm cache clean --force` |
| Electron | `~/Library/Caches/electron/` | `rm -rf` |