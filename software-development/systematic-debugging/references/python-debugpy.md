# Python Debugging Reference (pdb + debugpy)

## Tool selection

| Tool | When |
|------|------|
| `breakpoint()` + pdb | Local, interactive. Add in source, run normally, get REPL at that line |
| `python -m pdb` | Launch script under pdb with no source edits |
| `debugpy` | Remote / headless / attach to running process (DAP protocol) |
| `remote-pdb` | Agent-friendliest remote debug — `nc` gives full (Pdb) prompt |

## pdb quick reference

| Command | Action |
|---------|--------|
| `n` | next line (step over) |
| `s` | step into |
| `r` | return from function |
| `c` | continue |
| `l` / `ll` | list source / full function |
| `w` | where (stack trace) |
| `u` / `d` | move up/down in stack |
| `p expr` / `pp expr` | print / pretty-print |
| `b file:42` | set breakpoint |
| `cl N` | clear breakpoint N |
| `interact` | full Python REPL in current scope (most powerful) |
| `!stmt` | execute arbitrary Python (assignments included) |
| `q` | quit |

## Recipes

### Local breakpoint
```python
def compute(x, y):
    result = some_helper(x)
    breakpoint()           # drops into pdb here
    return result + y
```
**Don't forget to remove before committing:** `rg -n 'breakpoint\\(\\)' --type py`

### Launch script under pdb
```bash
python -m pdb path/to/script.py arg1 arg2
(Pdb) b path/to/script.py:42
(Pdb) c
```

### Debug pytest
```bash
scripts/run_tests.sh tests/test_file.py::test_name --pdb -p no:xdist
# xdist breaks pdb — always use -p no:xdist or -n 0
```

### Post-mortem on exception
```python
import pdb, sys
try:
    run_the_thing()
except Exception:
    pdb.post_mortem(sys.exc_info()[2])
```

### Remote debug with remote-pdb (preferred for Hermes)
```bash
pip install remote-pdb
# In code:
from remote_pdb import set_trace
set_trace(host="127.0.0.1", port=4444)  # blocks until connection

# From terminal:
nc 127.0.0.1 4444   # Full (Pdb) prompt
```

### Remote debug with debugpy (DAP)
```bash
# Process waits at start:
python -m debugpy --listen 127.0.0.1:5678 --wait-for-client script.py

# Attach to running process:
python -m debugpy --listen 127.0.0.1:5678 --pid <pid>
```

## Pitfalls
- pdb under pytest-xdist silently does nothing — use `-p no:xdist`
- `PYTHONBREAKPOINT=0` disables all `breakpoint()` calls
- `debugpy.listen` blocks only if you also call `wait_for_client()`
- pdb doesn't follow forks — each child needs its own breakpoint
- asyncio: `await` inside pdb requires Python 3.13+ or `interact` mode tricks
