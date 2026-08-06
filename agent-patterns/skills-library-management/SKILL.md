---
name: skills-library-management
description: "Agent skills library: SSOT, stand-ins, git manifest."
---

# Skills Library Management

Maintain the user's skills across tools (Claude Code, Codex, Hermes, cc-switch). Real content lives in `~/.hermes/skills/`; `~/.agents/skills/` is the Agent-Skills-standard SSOT whose entries are mostly **symlink stand-ins** pointing back to `.hermes`; `~/.claude/skills/` is symlinked to `.agents/skills`.

## Architecture

- `~/.hermes/skills/` — canonical content (category/name nesting allowed, e.g. `writing/humanizer`, `mlops/hf-mem`)
- `~/.agents/skills/` — SSOT git repo (private: mrtsels/agents-skills); real dirs for bundles, symlink stand-ins for everything else
- Symlink targets must be **relative** (`../../.hermes/skills/...`) so they work on this machine; clone elsewhere = broken link (acceptable, content intentionally not pushed)

## Git manifest repo pattern (core)

`.agents/skills` is a git repo tracking ONLY metadata: `.gitignore`, `README.md`, `skills-manifest.md`, and allowlisted symlinks/bundles. Skill content stays ignored.

`.gitignore` skeleton:
```gitignore
*
!.gitignore
!README.md
!skills-manifest.md
!<symlink-stand-in-name>      # one line per symlink
!latex-skills/                # tracked bundles
!latex-skills/**
```

Pitfalls (both bit this session):
- `!dir/` un-ignores the directory entry but NOT files inside it — need `!dir/**` to track a bundle's contents.
- A bare `*` matches names at ANY depth (git check-ignore confirmed `latex-skills/SKILL.md` matched by root `*`), so allowlist entries must cover nested paths explicitly.

Verify before commit: `git check-ignore -v <path>` (exit 1 + empty = not ignored, good).

## Adding a symlink stand-in

```bash
cd ~/.agents/skills
ln -s ../../.hermes/skills/<category>/<name> <name>   # relative!
# append !<name> to .gitignore
# regenerate manifest, then:
git add .gitignore skills-manifest.md <name>
git commit -m "add stand-in: <name>"
git push
```

Manifest regeneration (dirs + symlinks):
```bash
ls -d */ 2>/dev/null | sed 's|/$||'; ls -l | grep '^l' | awk '{print $9}' | sort -u
```
Write into `skills-manifest.md` with header (count, date, update command).

## Aggregation bundle (latex-skills pattern)

To group related skills under one index: create a real directory (e.g. `latex-skills/`) with an index `SKILL.md` whose body is a markdown table linking `./<sub-skill>/SKILL.md`. Track it in full with `!bundle/` + `!bundle/**` (the user explicitly asked "latex-skills加到追踪里" — full tracking, not just the index). Sub-skills that already exist elsewhere become relative symlinks inside the bundle (e.g. `latex-debugging -> ../../../.hermes/skills/software-development/latex-debugging` — depth changes when moved into a subdir!).

**Two tracking modes, know which one the user wants:**
- Full bundle: `!bundle/` + `!bundle/**` — real dir contents (index + all sub-skill SKILL.md files) enter git; symlinks inside stay symlinks. This is what the user chose for latex-skills.
- Index-only: `bundle/*` + `!bundle/SKILL.md` — only the index is tracked, sub-skill content stays ignored. Use this when the bundle aggregates skills whose content should not be published.
Ask or infer from the user's phrasing ("加到追踪里" / "全量" = full; silence about content = ask).

## Merging two skills (de-ai-ify-writing + humanizer → humanizer)

1. Decide the surviving name by the user's stated preference (they renamed to `humanizer` after the merge — ask or use the one already auto-injected).
2. **USER PREFERENCE (explicit correction): blend merged content BY TOPIC — do NOT keep "第一部分/第二部分" (part 1 / part 2) sections.** The user rejected that structure with "不要分两部分，把这些混在一起写". Organize the merged SKILL.md as unified topic sections (判断必须有依据 / 禁止夸大与情绪化 / 禁止戏剧化句式 / 精简冗余 / 格式痕迹 / 灵魂与声音 / 自检), with Chinese and English rules side by side inside each topic; only the verbatim absorbed original goes to `references/<name>-full.md`.
3. Keep the main SKILL.md lean: original domain rules + a condensed cross-language pattern list.
4. Full content of the absorbed skill → `references/<name>-full.md`; copy its LICENSE → `references/LICENSE-<name>.txt`; preserve attribution in SKILL.md.
5. Update every reference to the old name: `grep -rl old-name ~/.hermes ~/yuecai/AGENTS.md`; patch AGENTS.md/CLAUDE.md `skill=...` lines, memory entries, manifest, .gitignore allowlist, and the stand-in symlink itself.
6. `rm -rf` the absorbed source dir; keep a backup copy before destructive steps (`~/tmp-skill-merge-backup/`).

**Merging narrow siblings INTO an existing umbrella** (github pattern): copy each absorbed skill's SKILL.md → umbrella `references/<name>.md`, add References-table rows, append a compact summary section to the umbrella SKILL.md, then delete the standalone skills (both `~/.hermes/skills/` source and `.agents/skills` stand-in). Example: `install-skill-from-github` + `install-binary-from-github-releases` → `github/` references + "## N. Install from GitHub" section.

## Pitfalls

- Moving a symlink into a subdir breaks its relative target — recompute depth (`../../` → `../../../`).
- After renaming/removing a stand-in: `git rm --cached <name>` then allowlist refresh; the old name lingers in .gitignore otherwise.
- cc-switch can manage this SSOT (see `references/cc-switch-skill-storage.md` for its path/sync logic) — unified mode targets `~/.agents/skills`, per-app defaults match the layout above.
- `git add .` is banned in this repo (and user's repos generally) — add explicit paths only.
