# Debugging Hermes TUI Slash Commands

## Architecture

```
Python backend (hermes_cli/commands.py)   <-- canonical COMMAND_REGISTRY
       │
       ▼
TUI gateway (tui_gateway/server.py)       <-- slash.exec / command.dispatch
       │
       ▼
TUI frontend (ui-tui/src/app/slash/)      <-- local handlers + fallthrough
```

The Python `COMMAND_REGISTRY` is the source of truth for CLI dispatch, gateway help, Telegram BotCommand menu, Slack mapping, and autocomplete data shipped to Ink.

## Investigation steps

1. Check TUI frontend: `search_files(pattern="/commandname", file_glob="*.ts*", path="ui-tui/")`
2. Check Python backend: `search_files(pattern="/commandname", path="hermes_cli/commands.py")`
3. Check gateway: `search_files(pattern="complete.slash|slash.exec", path="tui_gateway/")`

## Fix: Missing command autocomplete

Add `CommandDef` entry to `COMMAND_REGISTRY` in `hermes_cli/commands.py`:
```python
CommandDef("commandname", "Description", "Session",
           cli_only=True, args_hint="[arg1|arg2]",
           subcommands=("arg1", "arg2")),
```

- `cli_only=True` — only in interactive CLI/TUI
- `gateway_only=True` — only in messaging platforms
- Both omitted — available everywhere

Add handler in `HermesCLI.process_command()` in `cli.py` and/or `gateway/run.py`.

## Common issues

1. **Command shows in TUI but not autocomplete** — missing from `COMMAND_REGISTRY`
2. **Shows in autocomplete but doesn't work** — missing handler in `tui_gateway/server.py` or `app.tsx`
3. **Behavior differs CLI vs TUI** — may have different implementations in `cli.py` vs TUI local handler
4. **Config persists but UI doesn't update** — also patch `patchUiState()` nanostore, not just `config.set`

## Verification

```bash
cd /path/to/hermes-agent && npm --prefix ui-tui run build
hermes --tui
# Type / and verify command appears in autocomplete
```
