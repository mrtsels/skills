# Parallel Independent Task Dispatch

## When to Use

Two or more coding tasks with **no overlapping file paths** can run
in parallel via `delegate_task(tasks=[...])`. No branches or worktrees
needed — each subagent modifies disjoint files in the same checkout.

**Rule of thumb:** If `git diff --stat` after both subagents would show
different files (no overlap), they're independent enough for parallel
dispatch.

## When NOT to Use

- Tasks modify the same file
- Tasks modify different methods of the same class that share a caller
- Tasks add imports to a shared `__init__.py`
- One task depends on the other's output

In these cases, dispatch sequentially or use worktree-based parallel
(Mode C in the parent skill).

## Batch Dispatch Pattern

```python
from hermes_tools import delegate_task, terminal

# Dispatch both in parallel
results = delegate_task(
    tasks=[
        dict(
            goal="Implement feature A (modify existing modules)",
            context="""
            Files to modify: module_a.py, module_b.py
            Modifications don't touch feature B's files.
            Verify with: pytest tests/test_a.py
            """,
            toolsets=["terminal", "file"],
        ),
        dict(
            goal="Implement feature B (create new file)",
            context="""
            Files to create: scripts/feature_b.py
            No overlap with feature A.
            Verify with: python scripts/feature_b.py --n 10 --epochs 2
            """,
            toolsets=["terminal", "file"],
        ),
    ]
)

# Each result is dict with task_index, status, summary
for r in results:
    print(r["status"], r["summary"][:200])
```

## After Both Complete: Resolve Conflicts

Even "independent" tasks can conflict if both modify the same
`__init__.py` (adding different imports) or the same test file.
If `pytest` shows failures after parallel dispatch:

1. `git diff --name-only` to find conflicted files
2. Read each file, fix any missing imports/keys
3. Re-run full test suite
4. Commit merged changes

## Why Not Worktrees

Worktrees are necessary when subagents modify the **same** code paths
and you need clean isolation. For truly independent tasks, single-checkout
parallel dispatch is simpler:

- No worktree creation/cleanup overhead
- No stash-pop dance to move files between checkouts
- Each subagent works directly in the project root
- The final test run catches any cross-task interference

## Signals It's Working

- Both subagents return `status: "completed"` with no tool errors
- `pytest tests/ -q` passes without changes
- `git diff --stat` shows each subagent's expected file list

## Post-Merge Integration (Critical Step)

After parallel subagents return, **re-read every file that either subagent
modified** before editing. Hermes emits a warning when you try to patch
a file a sibling agent changed without re-reading it first, because your
stale in-memory copy can overwrite the sibling's work.

**Mandatory workflow after parallel dispatch:**

```python
# After both subagents complete:

# 1. Check what changed
terminal("git diff --name-only")

# 2. Re-read modified files (critical — avoid overwriting sibling changes)
#    Use read_file on EACH file both agents touched.
read_file("module_a.py")
read_file("module_b.py")
read_file("test_integration.py")

# 3. Run full test suite (not just individual tests)
terminal("pytest tests/ -q")

# 4. Fix test failures — expect 2-5 API compatibility issues:
#    - Changed function output shapes (e.g. 4 → 12 dims)
#    - Changed dict keys in targets
#    - Mismatched test expectations
# 5. Commit merged result
terminal("git add -A && git commit -m '...'")
```

**Without step 2, you'll hit this error:**
`_warning: path was modified by sibling subagent '<id>' but this agent never read it.`
Followed by a failed or corrupted patch.

## Signals Something Went Wrong

- One subagent fails with an import error → the other subagent's
  modifications aren't visible yet (sequential dispatch needed)
- `KeyError` in test → test file was modified by both, manual merge needed
- `AssertionError` on output shape → model change by one subagent
  broke an assumption in the other's eval script. Fix: update the test's
  expected shape, don't revert the subagent's API change.
- **Hermes warning about sibling subagent file modification** → you tried
  to patch a file without re-reading it. Drop the patch, re-read, retry.
