# Reading Claude Code Conversation Files

Claude Code stores each session as a JSONL file under `~/.claude/projects/`. All Claude Code frontends (CLI, VS Code plugin, Desktop) share this storage — so you can read conversations from any source.

## Path Structure

```
~/.claude/projects/
  <project-hash>/          # One directory per project (hash of absolute path)
     *.jsonl               # One file per conversation
     <uuid>/               # (Optional) directory with same UUID
```

Project hashes look like: `-Users-minimx-bipartite-gnn-gui`

## Format

Each `.jsonl` file has one JSON object per line. Key event types:

| `type` field | Represents |
|---|---|
| `"user"` | User message (has `message.content`) |
| `"message"` | Assistant message (has `message.role`, `message.content[]`) |
| `"queue-operation"` | Internal queue events (enqueue/dequeue) — skip these for reading |

**User message format:**
```json
{
  "type": "user",
  "message": { "role": "user", "content": "text..." },
  "promptId": "...",
  "parentUuid": "...",
  "timestamp": "2026-05-26T11:32:00Z"
}
```

**Assistant message format:**
```json
{
  "type": "message",
  "message": {
    "id": "...",
    "role": "assistant",
    "model": "deepseek-v4-flash",
    "content": [
      { "type": "thinking", "thinking": "..." },
      { "type": "text", "text": "..." },
      { "type": "tool_use", "name": "Read", "input": { "file_path": "..." } }
    ]
  }
}
```

## Quick Reference Commands

### List recent sessions across all projects
```bash
cd ~/.claude/projects && python3 -c "
import os, glob
for d in sorted(os.listdir('.')):
    dd = os.path.join('.', d)
    if not os.path.isdir(dd): continue
    files = sorted(glob.glob(os.path.join(dd, '*.jsonl')), key=os.path.getmtime, reverse=True)
    if not files: continue
    sz = os.path.getsize(files[0])
    name = d.replace('-Users-minimx-','').replace('-',' ').strip()
    if not name: name = 'home'
    from datetime import datetime
    dt = datetime.fromtimestamp(os.path.getmtime(files[0])).strftime('%m-%d %H:%M')
    print(f'{dt} | {sz/1024:>6.1f}K | {name}')
"
```

### Extract user/assistant text from a session
```bash
python3 -c "
import json
for l in open('<file>.jsonl'):
    if not l.strip(): continue
    m = json.loads(l)
    if m.get('type') == 'user':
        print(f\"👤 {m['message']['content'][:200]}\")
    elif m.get('type') == 'message' and m['message'].get('role') == 'assistant':
        texts = [c.get('text','') for c in m['message'].get('content',[]) if isinstance(c,dict) and c.get('type')=='text']
        if ''.join(texts).strip():
            print(f\"  🤖 {''.join(texts)[:300]}\")
"
```

### Search across all sessions (by project)
```bash
cd ~/.claude/projects/<project> && grep -l 'keyword' *.jsonl
```

## Why This Matters for Hermes+CC Workflow

- **Debug CC failures**: Read the exact conversation to see what CC tried, what tools it used, and where it got stuck
- **Verify CC completed correctly**: Confirm tool_use calls and results matched what was expected
- **Recover context**: If a Hermes session restarted mid-project, reading CC sessions tells you where CC left off
- **Compare model behavior**: Check which model (`deepseek-v4-flash` vs `deepseek-v4-pro`) was used in each session

## Bonus: Session-level summary via `history.jsonl`

`~/.claude/history.jsonl` provides a lightweight index of recent sessions without reading full sessions:

```json
{
  "display": "fix: update genAIBrief button text",
  "pastedContents": [],
  "timestamp": 1781571601171,  // ms epoch
  "project": "/Users/minimx/enterprise",
  "sessionId": "bae402b8-..."
}
```

Use it to find the right session fast:

```bash
python3 -c "
import json
for l in open('/Users/minimx/.claude/history.jsonl'):
    d = json.loads(l)
    disp = d.get('display','')[:200]
    ts = d.get('timestamp','')
    proj = d.get('project','').split('/')[-1]
    sid = d.get('sessionId','')[:12]
    from datetime import datetime
    dt = datetime.fromtimestamp(ts/1000).strftime('%m-%d %H:%M')
    print(f'{dt} {proj:20s} {sid} | {disp}')
"
```

## Tool Result Analysis: Diagnosing CC Failures

When Claude Code is "stupid" (repeated failures, tool error loops), parse the session for error patterns:

### Finding all tool errors in a session

```bash
python3 -c "
import json
errors = []
with open('<session>.jsonl') as f:
    for l in f:
        d = json.loads(l.strip())
        if d.get('type') == 'user':
            msg = d.get('message',{})
            content = msg.get('content',[]) if isinstance(msg, dict) else []
            if isinstance(content, list):
                for item in content:
                    if isinstance(item, dict):
                        c = item.get('content','')
                        if isinstance(c, str) and ('Error' in c or 'error' in c):
                            errors.append((d.get('timestamp','')[:19], c[:200]))
                        elif isinstance(c, list):
                            for sub in (c if isinstance(c, list) else []):
                                if isinstance(sub, dict) and sub.get('type')=='text' and ('Error' in sub.get('text','') or 'error' in sub.get('text','')):
                                    errors.append((d.get('timestamp','')[:19], sub['text'][:200]))
for ts, e in errors:
    print(f'[{ts}] {e}')
print(f'\\nTotal errors: {len(errors)}')
"
```

### Counting Edit tool failures

```bash
python3 -c "
import json, re
edit_errors = 0
total_edits = 0
with open('<session>.jsonl') as f:
    for l in f:
        d = json.loads(l.strip())
        if d.get('type') == 'user':
            content = ''
            msg = d.get('message',{})
            if isinstance(msg, dict):
                c = msg.get('content','')
                if isinstance(c, str): content = c
                elif isinstance(c, list):
                    for item in c:
                        if isinstance(item, dict):
                            t = item.get('content','')
                            if isinstance(t, str): content += t
            if 'String to replace not found' in content or 'No changes to make' in content:
                edit_errors += 1
            if 'Edit' in content or 'patch' in content.lower():
                total_edits += 1

print(f'Edit attempts: {total_edits}')
print(f'Edit failures: {edit_errors}')
print(f'Failure rate: {edit_errors/total_edits*100:.0f}%' if total_edits else 'N/A')
"
```

### Finding the last user actions before session end

```bash
python3 -c "
import json
with open('<session>.jsonl') as f:
    lines = f.readlines()
last_msgs = []
for l in lines:
    d = json.loads(l.strip())
    if d.get('type') == 'user':
        msg = d.get('message','') or ''
        if isinstance(msg, dict):
            c = msg.get('content','')
            if isinstance(c, str) and len(c) > 10:
                last_msgs.append((d.get('timestamp','')[:19], c[:300]))
        elif isinstance(msg, str):
            last_msgs.append((d.get('timestamp','')[:19], msg[:300]))
for ts, c in last_msgs[-8:]:
    print(f'[{ts}] {c}')
"
```

## Deep Parsing: User message nested format

Claude Code sessions have a non-obvious user message format. The `message` field can be EITHER:

1. **Plain string** — short user input:
   ```json
   {"type": "user", "message": "查看管理端政策管理页编辑政策页，UI是不是很乱？"}
   ```

2. **Dict with role + content** — most user messages, where content is:
   - **String**: regular chat
   - **List**: contains `tool_result` objects embedded by CC's internal mechanism. Each tool_result carries the output of a tool call that CC made in the assistant's previous turn. These are NOT standalone user messages — they're tool execution results injected as user messages for the next assistant turn.

3. **Special command wrapper** — local commands triggered by `/clear`, `/model`, etc.:
   ```json
   {"type": "user", "message": {"role": "user", "content": "<command-name>/clear</command-name>"}}
   ```

When parsing tool results, look for this nested structure:
```json
{"content": [
  {"tool_use_id": "call_xxx", "type": "tool_result",
   "content": [{"type": "text", "text": "actual output here"}],
   "is_error": false}
]}
```

The `is_error` field in tool_result is the most reliable signal for tool failures. Don't grep for "Error" in text content — some tools return Error in non-error text.

## Other session file types

| File/Type | Purpose |
|---|---|
| `*.jsonl` | Full conversation (user + assistant turns) |
| `file-history-snapshot` | Periodic snapshots of tracked files for undo |
| `history.jsonl` | Lightweight index (project, timestamp, display text) |
| `subagents/*.jsonl` | Subagent sessions — parallel or subordinate CC instances |
| `mode` | Session mode marker (first line of every .jsonl) |

## Diagnosing Running/Stuck Sessions

When a Claude Code session seems stuck (user reports "it's been sitting there for hours"), don't just read the conversation log — the session could be **running but waiting** with no new message appended to the JSONL.

### Step 1: Find active Claude Code PIDs

```bash
ps aux | grep -i claude | grep -v grep
```

Look for interactive CLI sessions (`entrypoint: cli`, not `claude-vscode`). Multiple interactive sessions mean parallel work.

### Step 2: Read session metadata

Each running session has a metadata file at `~/.claude/sessions/<pid>.json`:

```bash
cat ~/.claude/sessions/<PID>.json
```

```json
{
  "pid": 57807,
  "sessionId": "98cff4a0-4357-4fa2-8aa5-11a85192b5dd",
  "cwd": "/Users/minimx/enterprise",
  "startedAt": 1782092861847,
  "status": "waiting",
  "waitingFor": "dialog open",
  "name": "apple-container-docker-build"
}
```

Key fields for diagnosis:

| Field | Meaning | Troubleshooting |
|---|---|---|
| `"status": "idle"` | Session alive, no activity | Normal — check if user replied recently |
| `"status": "waiting"` | Blocked on something | **Look at `waitingFor`** — this is why it's stuck |
| `"waitingFor": "dialog open"` | macOS system dialog is open (permissions, AppleScript, file access) | Switch to the terminal session and check for a modal dialog; answer it to unblock |
| `"waitingFor": "tool approval"` | Claude Code asked for permission | Check terminal for the approval prompt |
| `"waitingFor": "user input"` | Claude Code asked a question | Terminal has a question awaiting your answer |
| `"status": "running"` | Actively processing | Check CPU usage — normal if high |
| `name` field | Session name set via `/name` or `--name` | Useful to identify purpose at a glance |

### Step 3: Read task files

Claude Code's task system stores progress at `~/.claude/tasks/<sessionId>/`. Each numbered JSON file is a task step:

```bash
ls ~/.claude/tasks/<sessionId>/
# → 8.json  9.json  10.json  11.json  12.json

for f in ~/.claude/tasks/<sessionId>/*.json; do
  echo "=== $(basename $f) ==="
  cat "$f"
  echo
done
```

Task format:
```json
{
  "id": "12",
  "subject": "Build and export Docker images",
  "description": "Rebuild backend jar...",
  "status": "in_progress",
  "blocks": [],
  "blockedBy": []
}
```

This reveals the task plan — what steps were planned, which are `completed`, which are `in_progress` (the current blocker), and which are `pending`.

### Step 4: Read the project conversation log

Use the session ID from Step 2 to find the conversation JSONL:

```bash
ls ~/.claude/projects/*/<sessionId>.jsonl
```

Then parse it for the last assistant summary message (Claude Code periodically summarizes what it's working on):

```bash
python3 << 'PYEOF'
import json

with open('<path>/<sessionId>.jsonl') as f:
    lines = f.readlines()

# Find assistant messages that contain summary text (not tool results)
for l in reversed(lines):
    if not l.strip(): continue
    d = json.loads(l)
    if d.get('type') != 'message': continue
    msg = d.get('message', {})
    if msg.get('role') != 'assistant': continue
    texts = [c.get('text','') for c in msg.get('content',[])
             if isinstance(c, dict) and c.get('type') == 'text']
    combined = ''.join(texts).strip()
    if combined:
        print(combined[:400])
        break
PYEOF
```

### Full diagnostic flow (one-liner)

Combine all three sources for a quick status report:

```bash
echo "=== RUNNING CLAUDE PROCESSES ==="
ps aux | grep -i claude | grep -v grep | awk '{print $2, $11, $12, $13}'

echo ""; echo "=== SESSION METADATA ==="
for f in ~/.claude/sessions/*.json; do
  pid=$(basename $f .json)
  name=$(python3 -c "import json; d=json.load(open('$f')); print(d.get('name','?'), d.get('status','?'), d.get('waitingFor',''))")
  echo "  PID $pid: $name"
done

echo ""; echo "=== TASK PROGRESS ==="
for f in ~/.claude/sessions/*.json; do
  sid=$(python3 -c "import json; print(json.load(open('$f')).get('sessionId',''))" 2>/dev/null)
  [ -n "$sid" ] && [ -d ~/.claude/tasks/"$sid" ] && for tf in ~/.claude/tasks/"$sid"/*.json; do
    python3 -c "import json; d=json.load(open('$tf')); print(f'  {d[\"status\"]:12s} {d[\"subject\"]}')" 2>/dev/null
  done
done
```

### Common stuck patterns

| Pattern | What you see | What to do |
|---|---|---|
| macOS dialog (`waitingFor: "dialog open"`) | Session status=waiting for hours, terminal has a hidden modal | Find the terminal window (check `ps -o tty,pid <PID>`), then answer the dialog |
| Tool permission loop | Session runs but JSONL shows repeated error+retry cycles of same tool with same args | Kill the session (`kill <PID>`), fix the root cause, restart. Claude Code won't self-break out of error loops |
| Image pull stuck | Waiting on `docker pull` / `container pull` behind a proxy | Kill, fix proxy (`git config http.proxy ""`), restart. Don't wait — it won't timeout for 10+ min |
| `waitingFor: "tool approval"` | User hasn't responded to a permission prompt | Type `y` or `yes` in the terminal session that owns the process |
| Process alive but no output in 5+ min | CPU at 0%, no I/O — likely hanging on a blocking system call | Check `lsof -p <PID>` for what file/fd it's waiting on; kill if unresponsive |

### Why this matters

Hermes can't use `terminal(claude --bare ...)` to interact with a running interactive Claude session — they're separate processes. The session/task metadata bridge is the only way to inspect a running CC session from outside. Use this when:

- The user says "Claude is stuck, check what's happening"
- A parallel Claude Code session (running independently) seems hung
- You need to check progress of a long-running CC task before deciding whether to intervene

## Warning

- Files are owned by `minimx` with `-rw-------` permissions (600) — only the user who ran Claude Code can read them
- CC's auto-memory (`~/.claude/projects/<project>/memory/`) is a separate system storing compacted project knowledge, not full conversations
