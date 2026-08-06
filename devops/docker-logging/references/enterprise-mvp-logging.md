# Enterprise MVP Logging Implementation

## Background

Enterprise MVP is a Docker-deployed Spring Boot + Nginx app for managing SME innovation declarations. The server has no network access and runs on a Kylin VM. All images are packaged as tar files via `deploy.sh` and deployed via USB.

## Log File Layout

```
enterprise/logs/
├── backend/enterprise.json        # Spring Boot JSON lines (LoggingFilter + app logs)
├── access/access.log              # Nginx JSON lines only (no Apache combined format)
└── access/error.log               # Nginx error log
```

## Docker Compose Volume Mapping

From `docker/docker-compose.yml`:
```yaml
services:
  backend:
    volumes:
      - ${LOG_DIR:-./logs}/backend:/app/logs
  frontend:
    volumes:
      - ${LOG_DIR:-./logs}/access:/var/log/nginx
```

## Nginx Config

`docker/nginx.conf` — Server block only overrides combined format:
```nginx
server {
    listen 80;
    access_log /var/log/nginx/access.log json_escape;
    ...
}
```

No `access_log off;` — that permanently disables. Just the server-level `access_log` overrides the inherited http-level one.

## Dockerfile fix for volume permissions

`docker/Dockerfile.frontend`:
```dockerfile
RUN mkdir -p /var/log/nginx && chown -R nginx:nginx /var/log/nginx
```

Without this, nginx worker (user=nginx, UID 101) can't create access.log in a volume mounted from the macOS host (owned by UID 501). error.log is created by the root master process during startup, but access.log is opened lazily by the worker.

## Spring Boot LoggingFilter

File: `backend/src/main/java/.../logging/LoggingFilter.java`

- `OncePerRequestFilter` intercepts all `/api/**` paths
- Uses `ContentCachingRequestWrapper` for POST/PUT body capture (non-multipart)
- Uses `ContentCachingResponseWrapper` for response body capture (200 char truncation)
- Must call `copyBodyToResponse()` in finally block
- Logs: `[REQ] METHOD /api/path?query -> STATUS (DURATIONms) body={...} res={...} uid=ID`

Log output enhanced from:
```
[REQ] POST /api/declarations -> 200 (45ms)
```
To:
```
[REQ] POST /api/declarations?page=1&size=10 -> 200 (45ms) body={"name":"xx"} res={"id":1,"status":"OK"} uid=3
```

## CLI `enterprise logs` Commands

From `enterprise` script (bash):

| Command | Implementation |
|---------|---------------|
| `enterprise logs` | Python3: parses JSON lines from all sources, sorts by timestamp, shows last 50 |
| `enterprise logs -f` | Python3 subprocess: `tail -f --retry` on each file, `select.select()` loops, labels output `[backend]`/`[nginx]` |
| `enterprise logs backend` | `tail -n 50 $LOG_DIR/backend/enterprise.json` |
| `enterprise logs nginx` | `grep '^{' $LOG_DIR/access/access.log \| tail -n 50` |
| `enterprise logs search <word>` | `grep -i` across all log files |

## Arg passthrough fix

```bash
# In the main case statement:
case "${1:-}" in
  logs)    shift; cmd_logs "$@" ;;    # ← pass ALL remaining args
esac
```

Without `shift`, only `$2` was passed — `enterprise logs search login` only passed `search` to cmd_logs(), losing `login`.

## Build verification

- Java 17 at `/opt/homebrew/opt/openjdk@17` (Homebrew)
- `mvn clean package -DskipTests` with JAVA_HOME pointed to Java 17
- Rebuild Docker images: `docker-compose -f docker/docker-compose.yml build backend frontend`
- Restart: `docker-compose -f docker/docker-compose.yml down && docker-compose -f docker/docker-compose.yml up -d`
