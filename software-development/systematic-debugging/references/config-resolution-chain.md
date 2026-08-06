# Config Resolution Chain Debugging

When a config value isn't being picked up, the problem is usually at one hop in the resolution chain. Trace the actual value at each layer.

## The Chain (Spring Boot + Docker Compose)

```
docker/.env (gitignored, real values)
  └── Docker Compose auto-loads .env from compose file's directory
        └── container environment variables (docker-compose.yml environment:)
              └── application.yml ${VAR_NAME:-default} SPEL
                    └── @ConfigurationProperties(prefix) Java POJO
```

## Diagnostic Steps

### 1. Find where the value SHOULD be

```bash
# Check .env file (source of truth)
grep "^VAR_NAME=" docker/.env

# Check docker-compose.yml (should only have ${VAR:-default} references, not real values)
grep "VAR_NAME" docker/docker-compose.yml
# → VAR_NAME: ${VAR_NAME:-}   ← variable reference, NOT the value
```

**⚠️ Pitfall:** `${VAR:-default}` in compose files yields the **variable name** when parsed with grep/sed, not the value. Never parse compose files for config values in diagnostic scripts — read `.env` instead.

### 2. Check container environment

```bash
docker exec <container> sh -c "echo \$VAR_NAME"
```

### 3. Check Spring Boot actuator (if enabled)

```bash
curl -s http://localhost:8080/actuator/env/<property-path> | python3 -m json.tool
```

### 4. Check ai-config.json (runtime override in Docker volume)

```bash
# File is inside Docker volume, not on host filesystem
docker exec <container> cat /app/uploads/ai-config.json | python3 -c \
  "import json,sys; d=json.load(sys.stdin); print(d.get('apiKey',''))"
```

## Common Root Causes

| Symptom | Likely Cause |
|---------|-------------|
| Script extracts literal `VAR_NAME` string | Parsing `${VAR:-}` from compose file instead of reading `.env` |
| Application uses placeholder value | application.yml has literal default (not `${VAR:}` SPEL syntax) |
| Variable name mismatch | docker-compose.yml uses `FOO_KEY` but application.yml expects `foo.api-key` |
| Runtime override not found | `ai-config.json` is inside Docker volume, not on host path |
| Empty value in container | `.env` not created or not in compose file's directory |
