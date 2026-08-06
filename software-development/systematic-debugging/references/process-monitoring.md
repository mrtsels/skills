# Process & Build Monitoring — Is It Running or Stuck?

## The Trap

When a process (build, download, compilation) has been running for what feels like a long time, the natural assumption is "it's slow, give it time." This is wrong. **Time alone is never evidence of progress.**

## Investigation Checklist

Before deciding "it's normal, just slow," check:

### 1. Is the process actually using resources?

```bash
# Is it still alive?
ps -p <PID> -o pid,state,etime,pcpu,pmem,comm

# What is it doing right now?
lsof -p <PID> 2>/dev/null | head -20
# Look for:
# - Open file descriptors advancing (reading/writing)
# - Network connections (connecting/downloading)
# - CPU time increasing (compiling)

# File descriptors changing = progress
# Stuck on the same file descriptor for 60+ seconds = stuck
```

### 2. What has it produced so far?

```bash
# Check partial output
ls -la <expected_output_file> 2>/dev/null

# Check the build directory for intermediate artifacts
find <build_dir> -type f -mmin -10 2>/dev/null | head -10
# Files modified in last 10 minutes = progress
# No recent files = likely stuck
```

### 3. Is it waiting for input?

```bash
# Check process state: 'S' (sleeping/waiting) vs 'R' (running)
ps -o state -p <PID>
# 'S+' with no CPU = waiting for something
# 'R' = actively running

# Check if it's waiting for stdin (interactive prompt)
# Look for 'S+ in select' or similar
```

### 4. Check the output log

```bash
# Last few lines of output
tail -20 <output_file>

# Timestamp of last output
stat -f "%Sm" <output_file>
```

## Common Patterns That Look Like "Slow" But Are Actually Stuck

| What you see | Likely problem | Fix |
|---|---|---|
| `container build` running 20+ min but Dockerfile is pre-compiled JAR | Dockerfile was changed to multi-stage; Maven downloading deps inside container | Check Dockerfile content; kill and rebuild with pre-compiled pattern |
| Network download at 0 bytes for 30+ sec | Proxy blocking, DNS failure, or rate limiting | Check `lsof -p <PID>` for connection state |
| Compilation with no new files in 10+ min | Dependency resolution failure or infinite loop | Check CPU usage; kill and restart with verbose mode |
| Container build with no output for 5+ min | Might be downloading base image layers (slow but normal first time) | Check `ps` CPU; if CPU > 0% it's working |

## The Rule

**If you can't explain WHY a process is taking its current time based on concrete evidence (not assumptions), you haven't investigated enough.**

Default to: "let me check" — not "let me wait."
