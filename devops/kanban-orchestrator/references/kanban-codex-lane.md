# Codex Lane — Full Reference

## Prompt construction

Every Codex prompt must include:
- `task_id`, title, and full Kanban acceptance criteria
- Repo path, worktree path, branch name, and allowed file scope
- Explicit statement: Hermes owns Kanban lifecycle; Codex is an input lane only
- Required output: concise summary, files changed, tests run, known risks
- Prohibited actions: secrets access, external messaging, board mutation
- Verification commands Codex may run and commands Hermes will run afterward

## Monitoring, timeout, and kill

```python
# Start Codex
result = terminal(
    command="codex exec --full-auto '$(cat /tmp/codex_prompt.md)'",
    workdir=WORKTREE, background=True, pty=True, notify_on_complete=True,
)
session_id = result["session_id"]

# Monitor
process(action="poll", session_id=session_id)
process(action="log", session_id=session_id, limit=200)
process(action="wait", session_id=session_id, timeout=300)
```

Kill conditions: no useful output for remaining budget, requests secrets, modifies files outside worktree, unrelated rewrites, near timeout with no safe artifact.

## kanban_complete metadata schema

```json
{
  "codex_lane": {
    "used": true,
    "mode": "exec | goal | skipped",
    "worktree": "/path/to/codex/worktree",
    "branch": "codex/t_caa69668/20260508100000",
    "command": "codex exec --full-auto ...",
    "result": "accepted | rejected | partial | timed_out",
    "accepted_commits": ["<sha1>", "<sha2>"],
    "rejected_reason": "reason if not fully accepted",
    "tests_run": [
      {"command": "scripts/run_tests.sh ...", "exit_code": 0, "owner": "hermes"}
    ],
    "artifacts": ["/path/to/log-or-patch"]
  }
}
```