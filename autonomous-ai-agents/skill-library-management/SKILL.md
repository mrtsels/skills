---
name: skill-library-management
description: Manage agent skill libraries - SSOT, symlinks, git repos.
---

# Skill Library Management

Use when installing/moving/syncing/backing up skills across Claude Code, Hermes, Codex, or explaining where skills live on this machine.

## Machine Architecture (this machine)

| Location | Role |
|----------|------|
| `~/.agents/skills/` | **SSOT** — Agent Skills standard, 210+ real skill dirs. Also a git repo (private `mrtsels/agents-skills`) |
| `~/.claude/skills/` | Claude Code — mostly **symlinks → `~/.agents/skills/<name>`** (user's unified mode) |
| `~/.hermes/skills/` | Hermes — **categorized nested dirs** (`academic/`, `mlops/`, ...). Both flat and nested load fine |
| `~/hf-skills/` | clone of `huggingface/skills`; 18 skills symlinked into `~/.claude/skills/` |
| `~/.cc-switch/` | cc-switch app config (config.json + skill-backups/) |
| `~/.hermes/config.yaml` | `mcp_servers.huggingface` — HF MCP (https://huggingface.co/mcp?login) |

**Hermes note:** skills in `~/.hermes/skills/<category>/<name>/` and flat `~/.hermes/skills/<name>/` both work; skills can also be symlinked from other dirs (e.g. `~/.agents/skills/`).

## The "Stand-in" (替身) Pattern

To expose a skill that lives elsewhere (Hermes, hf-skills clone) without duplicating content:

```bash
ln -s <abs-or-rel-source-dir> ~/.agents/skills/<skill-name>
```

- Use **relative** targets when the link lives in a git repo (portable): `../../.hermes/skills/<category>/<name>`
- Git tracks symlinks as `mode 120000` — content stays out of the repo
- On a fresh clone the links break (content not uploaded by design) — that's the point

## Manifest-Only Git Repo Pattern

Backup a skills dir to git WITHOUT uploading content:

1. `git init` in the skills dir
2. `.gitignore`:
   ```
   *
   !.gitignore
   !README.md
   !skills-manifest.md
   !<symlink-name-1>      # allowlist each stand-in
   !<symlink-name-2>
   ```
3. Regenerate manifest after changes:
   ```bash
   ls -d */ 2>/dev/null | sed 's|/$||'; ls -l | grep '^l' | awk '{print $9}' | sort -u
   ```
4. `git add` the allowlisted files + new symlinks, commit, push (private repo: `gh repo create <name> --private --source <dir> --push`)

**Pitfall:** nested `.git/` inside a skill dir (a repo cloned directly into skills/, e.g. `consulting-problem-solving/`, `best-practices/`) — leave them; the outer `.gitignore` `*` rule keeps them out of the parent repo, and `git add -A` inside them targets the wrong repo.

## cc-switch (unified skill manager)

Two storage modes (see `references/cc-switch-internals.md` for source-level detail):
- `cc_switch` (default): SSOT = `~/.cc-switch/skills/`
- `unified`: SSOT = `~/.agents/skills/` (Agent Skills standard)

It distributes each skill from SSOT to per-app dirs (`~/.claude/skills`, `~/.codex/skills`, `~/.hermes/skills`, ...) via **symlink (Auto, fallback copy)** / **Symlink** / **Copy** sync methods. Migration moves files first, persists settings after, then re-syncs all apps. Backups at `~/.cc-switch/skill-backups/`.

## Pitfalls

- **Claude Code non-interactive `/plugin` unavailable**: `claude /plugin marketplace add huggingface/skills` fails with "/plugin isn't available in this environment". Use symlinks instead: `ln -sf ~/hf-skills/skills/<name> ~/.claude/skills/<name>`.
- **Hermes config.yaml**: edit with `hermes config set` or `patch` — never Python yaml.dump (re-serializes and breaks formatting). MCP servers go under `mcp_servers:`.
- **Git commit hygiene**: only `git add` specific paths, never `add .`/`add -A` in the skills repo (nested repos + ignored content).
- **HF skills**: `huggingface/skills` repo (10.8k⭐) — 19 skills incl. `huggingface-llm-trainer` (SFT/DPO/GRPO on HF Jobs), `hf-mem` (VRAM estimate), `huggingface-datasets`, `huggingface-community-evals`, `huggingface-paper-publisher`. Hermes counterparts: `mlops/huggingface-llm-trainer`, `mlops/hf-mem`.
