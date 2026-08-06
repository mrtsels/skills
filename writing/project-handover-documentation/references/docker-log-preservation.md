# Docker Log Preservation

## Question: Does `docker compose down` + `up` clear log files?

**No.** Logs mounted via bind mount survive container lifecycle changes.

### Bind Mount vs Named Volume

Bind mounts are host directories mounted into the container. Named volumes are Docker-managed storage at `/var/lib/docker/volumes/`.

| Operation | Named Volume | Bind Mount |
|-----------|-------------|------------|
| `docker compose down` | Survives | Survives |
| `docker compose down -v` | **Deleted** | **Survives** |
| `docker compose up` | New container, same data | New container, same file |
| `rm -rf logs/` on host | N/A | **Deleted** |

### How it works

Docker Compose bind mount syntax:
```yaml
volumes:
  - ../logs/backend:/app/logs       # bind mount from host
```

The path `../logs/backend` is relative to the compose file's directory. When compose is in `docker/`:
- `../logs/backend` → `logs/backend/` at project root
- `../logs/access` → `logs/access/` at project root

### Verification

```
Before: 283 lines in enterprise.json  (old session shutdown)
After:  256+ lines in enterprise.json (new session appended)
                                         ↑ old lines preserved, new ones added
```

The log file is opened in append mode by Logback. New container processes write to the same file descriptor. Old content is never truncated.

### Practical implication

- `enterprise restart` (which does `docker compose down` then `up`) does NOT lose logs
- `enterprise uninstall` (which does `docker compose down -v` then `rm -rf logs/`) DOES delete logs via explicit `rm`

### Two log directories gotcha (previously)

When compose was at project root, then moved to `docker/` with `./logs`, there were TWO `logs/` directories:
- `logs/` at project root — from the old compose setup
- `docker/logs/` — the active one from the moved compose file

**Fix:** Use `../logs` (instead of `./logs`) in docker-compose.yml's LOG_DIR defaults. This makes the compose file in `docker/` write logs to the project root `logs/`, matching what the CLI and logclean.sh expect. See the main skill section "Cross-File Path Consistency Audit" for the full audit pattern.
