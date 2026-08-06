# 2026-06-22: Training Pipeline + Hyperparameter Sweep

## Context

bipartite-gnn-gui project — PyG Heterogeneous GNN for GUI structure correction.
Phase 4.6 (experiments): training pipeline standardization + hyperparameter sweep.

## Key Pattern: delegate_task for Experiment Runners

Instead of terminal(claude --bare ...), used Hermes delegate_task() for each experiment task:

```python
# Phase 4.6.1: Training pipeline
delegate_task(
    goal="Create a proper training pipeline integrating all existing components",
    context="Detailed file paths, what exists, what to build, verification steps...",
    toolsets=["terminal", "file", "search", "coding"],
)

# Phase 4.6.2: Hyperparameter sweep
delegate_task(
    goal="Build and run a hyperparameter sweep across 6 configs",
    context="Refactor run_experiment.py, create sweep.py, run 6 configs...",
    toolsets=["terminal", "file", "search", "coding"],
)
```

## delegate_task Prompt Structure (proven to work)

```python
delegate_task(
    goal="<single sentence — what to accomplish>",
    context="""<everything else — must be self-contained>:

1. Worktree path (absolute)
2. Existing files the agent must read
3. What to build / change (detailed)
4. Verification commands (exact shell commands)
5. Git workflow (add → commit → push → PR)
6. Key constraints and pitfalls

IMPORTANT: 
- Use absolute paths for data dirs (relative paths break in worktree)
- Use absolute path to .venv Python
- Write flush-aware logging (python -u flag) for long-running scripts
- Subagent has NO memory of parent conversation
""",
    toolsets=["terminal", "file", "search", "coding"],
)
```

## Git Proxy Fix

When git push returns 503 through Shadowrocket:

```bash
# Bypass proxy for git only (empty string overrides env var)
git config --global http.proxy ""
git config --global https.proxy ""

# Restore when proxy is working again
git config --global http.proxy http://127.0.0.1:1082
git config --global https.proxy http://127.0.0.1:1082
```

Difference: `--unset` causes git to fall back to `$http_proxy` env var which still goes through the down proxy. Empty string overrides the env var with empty (direct connection).

## Hyperparameter Sweep Pattern

### Architecture
```
experiments/
  sweep.py           ← 6-config sweep runner
  test_sweep.py       ← 4 tests for sweep pipeline
  results.json        ← append-only results log (one entry per run)
checkpoints/sweep/<name>/
  best_model.pt
```

### What sweep.py does (proven pattern)
1. Define CONFIGS list: (name, hidden_dim, lr, noise_scale, epochs)
2. For each config: patch ExperimentConfig → call run_experiment() → append to results.json
3. Print formatted comparison table at end
4. Raise exception on config failure but continue sweep

### Key Implementation Details
- `run_experiment()` returns a dict with structured keys (not just logs)
- Results are append-only JSON, one entry per config with timestamp
- Error handling per config so one failure doesn't kill the sweep
- Table includes: name, best_val, recall, precision, f1, pos_err, noop_rec, % improvement

### Results Table Format
```
name                   | best_val | recall | precision |     f1 | pos_err | noop_rec |     improv
────────────────────────────────────────────────────────────────────────────────────────────────
  hd64_small-noise     |   0.0561 |  0.150 |     0.531 |  0.234 |   0.244 |    0.999 |    -841.2%
  hd128_big-noise      |   0.0537 |  0.204 |     0.534 |  0.295 |   0.249 |    0.917 |    -310.5%
```

## Learnings about RICO Data Pipeline

- 66K JSON files in `data/rico_local/combined/`
- Parsing 200 files + constraint extraction + HeteroData build: ~0.4s
- 198/200 (99%) produce valid graphs
- Training 200 graphs × 50 epochs on CPU: ~50s per config
- hidden_dim (64 vs 128 vs 256) makes minimal difference — model converges to same ~0.054 val_loss
- Bigger noise scale (0.20) → marginally worse metrics (expected: harder task)
- The model DOES learn (loss decreases, recall improves) but starts with hand-crafted noise not real VLM errors
