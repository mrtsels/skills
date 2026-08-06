# Codex Lane Prompt Template

> Copy this template and fill in the placeholders for your task.

## Task
- Task ID: `{{TASK_ID}}`
- Title: {{TITLE}}
- Acceptance criteria: {{ACCEPTANCE_CRITERIA}}

## Scope
- Repo: {{REPO_PATH}}
- Worktree: {{WORKTREE}}
- Branch: {{BRANCH}}
- Allowed files: {{ALLOWED_FILES}}

## Ownership
Hermes owns the Kanban lifecycle. Codex is an input lane only. Do not call Hermes kanban tools, gateway messaging, or board CLI.

## Safety constraints
- Do not read, print, write, or require secrets/tokens/credentials
- Do not modify files outside the worktree
- Do not add unrelated refactors or dependency upgrades unless required by the task
- Do not weaken existing risk gates, safety checks, or fail-closed behavior

## Output requirements
- Concise summary of what was done
- Files changed with commit SHAs
- Tests run and their results
- Known risks or concerns

## Verification
Codex may run: {{CODEX_VERIFICATION_COMMANDS}}
Hermes will run after: {{HERMES_VERIFICATION_COMMANDS}}