# Phase-Based Prompt Examples

From session 2026-05-25: bipartite-gnn-gui Phase 4.1.2–4.1.4.

## Prompt Construction Pattern

```
1. Read current scaffold files (list paths + describe contents)
2. Write prompt to /tmp/prompt_xxx.txt
3. Feed to Claude Code via terminal:
   terminal("cd <REPO> && claude --model deepseek-v4-flash --bare --dangerously-skip-permissions --output-format json -p \"$(cat /tmp/prompt_xxx.txt)\"", timeout=600)
4. Verify: test count, PR exists, no regressions
5. Merge: gh pr merge <num> --squash --delete-branch
6. Git pull, continue to next task
```

## Session Metrics

| Task | Tests | Turns | Time | Cost (USD) |
|------|-------|-------|------|------------|
| 4.1.2 Config | 29 | 19 | 93s | $0.32 |
| 4.1.3 Logging | 26 | 19 | 141s | $0.44 |
| 4.1.4 Dependencies | 24 | 19 | 63s | $0.33 |
| Claude Q&A (dataset format) | — | 4 | 29s | $0.13 |

**Total for Phase 4.1.2–4.1.4**: ~$1.09

## 4.1.2 Config System — Full Prompt

Pattern: existing scaffold (config.py), need tests + default.yaml.

```bash
cat > /tmp/prompt_412.txt << 'PROMPT_END'
TASK: Implement Phase 4.1.2 — Config system.

CONTEXT: This is a bipartite GNN project for GUI structure correction. 
Read CLAUDE.md at the repo root for behavioral rules and code style.

The config module is already scaffolded at:
- src/bipartite_gnn_gui/utils/config.py (DataConfig, ModelConfig, TrainingConfig, Config, load_config, save_config, validate_config)

WHAT YOU NEED TO CREATE:

1. tests/test_utils_config.py — Comprehensive tests covering:
   - DataConfig defaults and custom values
   - Default isolation (each instance gets own list via default_factory)
   - Config top-level composition and to_dict()
   - load_config() from YAML file (full, partial, empty, missing file errors)
   - load_config(None) returning defaults
   - save_config() and round-trip (save → reload → verify)
   - validate_config() from Config object, from dict, from empty dict, from None
   - Integration: modify → save → reload lifecycle
   Use pytest classes. Use tmp_path fixture for file tests.

2. configs/default.yaml — Default config matching all dataclass defaults

VERIFY: Run `python -m pytest tests/test_utils_config.py -v` — all tests must pass.

After implementation and verification:
1. git checkout -b phase4-4.1.2-config
2. git add tests/test_utils_config.py configs/default.yaml
3. git commit -m "utils: implement config system with tests and default.yaml"
4. git push origin phase4-4.1.2-config
5. gh pr create --title "utils: implement config system with tests and default.yaml" --body "## Summary\n\nImplements Phase 4.1.2.\n\n### Verification\n\n\`\`\`\npytest tests/test_utils_config.py -v\n\`\`\`"
PROMPT_END

terminal(command="cd /path/to/repo && claude --model deepseek-v4-flash --bare --dangerously-skip-permissions --output-format json -p \"$(cat /tmp/prompt_412.txt)\"", timeout=600)
```

Key: **include the scaffold file path and contents in the prompt**. Claude Code has no memory of what already exists.

## 4.1.3 Logging System — Prompt

Pattern: existing stubs, need real implementations + tests.

```bash
cat > /tmp/prompt_413.txt << 'PROMPT_END'
TASK: Implement Phase 4.1.3 — Logging system.

CONTEXT: This is a bipartite GNN project for GUI structure correction. 
Read CLAUDE.md at the repo root for behavioral rules and code style.

The logging module is currently scaffolded with stubs at:
- src/bipartite_gnn_gui/utils/logging.py
  Current state: setup_logger (working), get_logger (working), MetricsLogger (Base class), 
  NoopMetricsLogger (working), WandbMetricsLogger (stub — return None), 
  TensorboardMetricsLogger (stub — return None)

WHAT YOU NEED TO DO:

1. Upgrade src/bipartite_gnn_gui/utils/logging.py:
   - Keep setup_logger and get_logger as-is
   - Convert MetricsLogger to ABC with @abstractmethod
   - WandbMetricsLogger: try/except ImportError, wandb.init/log/finish, available property
   - TensorboardMetricsLogger: try/except, SummaryWriter, add_scalar, close(), available property

2. Create tests/test_utils_logging.py — 26+ tests:
   - setup_logger (basic, debug, file, dedup, append, format)
   - get_logger (default name, same instance, picks up setup)
   - ABC contract, NoopMetricsLogger, WandbMetricsLogger fallback, TensorboardMetricsLogger fallback
   - Integration: lifecycle, file content, multi-logger, interface compliance

3. Update tests/__init__.py if needed for imports

VERIFY: Run `python -m pytest tests/test_utils_logging.py -v` — all must pass.
Then `python -m pytest tests/ -v` — all existing tests must still pass (should be 80+).

After implementation and verification:
(standard git add/commit/push/PR)
PROMPT_END

terminal(command="...", timeout=600)
```

## 4.1.4 Dependency Declarations — Prompt

Pattern: simple pyproject.toml update + setup tests.

```bash
cat > /tmp/prompt_414.txt << 'PROMPT_END'
TASK: Implement Phase 4.1.4 — Dependency declarations (pyproject.toml extras).

CONTEXT: This is a bipartite GNN project for GUI structure correction.
Read CLAUDE.md at the repo root.

WHAT YOU NEED TO DO:

1. Update pyproject.toml to add:
   - wandb extra: ["wandb>=0.16.0"]
   - tensorboard extra: ["tensorboard>=2.14.0"]
   - pytest-cov>=4.1.0 to dev
   - all = [wandb, tensorboard, dev, test]

2. Create tests/test_setup.py verifying:
   - Package metadata (name=bipartite-gnn-gui, version=0.1.0, description)
   - All 8 core deps declared
   - All 5 extras declared (wandb, tensorboard, dev, test, all)

VERIFY: `pytest tests/test_setup.py -v` then `pytest tests/ -v`

After implementation and verification:
(standard git/PR)
PROMPT_END

terminal(command="...", timeout=600)
```

## Notes

- Always include "Read CLAUDE.md" in CONTEXT — this encodes the project's behavioral guidelines (Karpathy rules)
- Always include `gh pr create --title "..." --body "..."` in the prompt — don't expect Claude Code to infer the PR description format
- Timeout=600 is safe even for simple tasks (it returns instantly when done)
- After merging each PR, `git pull origin main` on Hermes' side to keep local state in sync
- For **modifying existing files** (HTML reports, docs, configs), use **git worktree** instead of branch-in-place (see `prompt-html-redesign.md`)
- For **creating new modules** (code + tests), use **branch-in-place** with PR (this file's pattern)
