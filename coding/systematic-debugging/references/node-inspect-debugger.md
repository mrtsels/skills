# Node.js Inspect Debugger Reference

## Tool selection

| Tool | When |
|------|------|
| `node inspect` | Built-in, zero install, CLI REPL. Best for quick poking |
| CDP via `chrome-remote-interface` | Scriptable — automate breakpoints, heap snapshots, CPU profiles |

## `node inspect` REPL commands

| Command | Action |
|---------|--------|
| `c` / `cont` | continue |
| `n` / `next` | step over |
| `s` / `step` | step into |
| `o` / `out` | step out |
| `sb('file.js', 42)` | set breakpoint |
| `sb(42)` | break at line of current file |
| `bt` | backtrace (call stack) |
| `list(5)` | show 5 lines of source |
| `watch('expr')` | auto-eval on every pause |
| `repl` | drop into REPL in current scope (Ctrl+C to exit) |
| `exec expr` | evaluate expression once |
| `.exit` | quit |

## Launch recipes

### Start paused on first line
```bash
node --inspect-brk script.js
node --inspect-brk $(which tsx) script.ts           # TypeScript
node --inspect-brk --import tsx script.ts           # tsx with --import
```

### Attach to running process
```bash
kill -SIGUSR1 <pid>                                  # Enable inspector
node inspect -p <pid>                                 # Attach debugger CLI
node inspect ws://127.0.0.1:9229/<uuid>              # Or by WS URL
```

### Debug vitest
```bash
node --inspect-brk ./node_modules/vitest/vitest.mjs run --no-file-parallelism test.tsx
```

## Debug Hermes TUI (Ink/React)

```bash
# Build then debug
cd /path/to/hermes-agent && npm --prefix ui-tui run build
node --inspect-brk dist/entry.js

# Or attach to running --tui
hermes --tui &
TUI_PID=$(pgrep -f 'ui-tui/dist/entry' | head -1)
kill -SIGUSR1 "$TUI_PID"
curl -s http://127.0.0.1:9229/json/list | jq -r '.[0].webSocketDebuggerUrl'
node inspect <ws-url>
```

## Programmatic CDP (automation)

```bash
npm i -g chrome-remote-interface
node --inspect-brk=9229 target.js &
```

Driver script pattern:
```javascript
const CDP = require('chrome-remote-interface');
(async () => {
    const client = await CDP({ port: 9229 });
    const { Debugger, Runtime } = client;
    Debugger.paused(async ({ callFrames }) => {
        const top = callFrames[0];
        console.log(`Paused at ${top.url}:${top.location.lineNumber + 1}`);
        // Inspect scopes, evaluate expressions
        await Debugger.resume();
    });
    await Debugger.enable();
    await Debugger.setBreakpointByUrl({ urlRegex: '.*app\\.tsx$', lineNumber: 119 });
    await Runtime.runIfWaitingForDebugger();
})();
```

## Heap & CPU profiles (non-interactive)

```javascript
// CPU profile (5 sec)
await client.Profiler.enable();
await client.Profiler.start();
await new Promise(r => setTimeout(r, 5000));
const { profile } = await client.Profiler.stop();
require('fs').writeFileSync('/tmp/cpu.cpuprofile', JSON.stringify(profile));

// Heap snapshot
await client.HeapProfiler.enable();
const chunks = [];
client.HeapProfiler.addHeapSnapshotChunk(({ chunk }) => chunks.push(chunk));
await client.HeapProfiler.takeHeapSnapshot();
require('fs').writeFileSync('/tmp/heap.heapsnapshot', chunks.join(''));
```

## Pitfalls
- TypeScript sourcemaps: `node inspect` CLI doesn't follow sourcemaps — break in built JS
- `--inspect` vs `--inspect-brk`: first doesn't pause; execution races past your breakpoints
- Port 9229 is default — use `--inspect=0` for random port to avoid collisions
- `--inspect` on parent doesn't inspect children — use `NODE_OPTIONS='--inspect-brk'`
- `--inspect=0.0.0.0:9229` exposes arbitrary code execution — always bind 127.0.0.1
