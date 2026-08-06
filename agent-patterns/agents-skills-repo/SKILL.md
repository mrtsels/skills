---
name: agents-skills-repo
description: Manage ~/.agents/skills SSOT (stand-ins, manifest, merge).
---

# Agents-Skills SSOT Repo (skill library management)

`~/.agents/skills/` is the single-source-of-truth (SSOT) skill directory shared by Claude Code, Codex, Hermes, etc. On this machine it is also a **git repo pushed to a private GitHub repo** (`mrtsels/agents-skills`) that tracks only metadata, NOT skill content.

## Repository Layout

```
~/.agents/skills/
├── .git/                    # git repo (private: mrtsels/agents-skills)
├── .gitignore               # ignore-all + allowlist (see below)
├── README.md                # tracked
├── skills-manifest.md       # tracked — list of every skill dir + symlink stand-in
├── <skill-dir>/             # real skill directories (NOT tracked)
└── <skill-name> -> ../../.hermes/skills/<cat>/<skill>   # symlink stand-ins (tracked)
```

Real skill dirs come from `git clone`/`npx skills add`/manual copies. **Symlink stand-ins** point at user-crafted skills living in `~/.hermes/skills/` — they make a skill visible to all agents AND listable in the GitHub repo without duplicating content.

For cc-switch (the desktop skill manager) internals — storage modes, per-app dirs, sync methods, migration safety — see `references/cc-switch-storage.md`.

## .gitignore Pattern

> **SUPERSEDED 2026-08-06**: the repo now tracks ALL skill content; `.gitignore` is explicit exclusions only (system junk, nested `.git/`, sensitive dirs/files). The ignore-all+allowlist mode below is retired. Authoritative current workflow: the `skill-farm-maintenance` skill (audit script + PII gate).

```gitignore
# Ignore everything except the manifest files and skill stand-ins (symlinks)
*
!.gitignore
!README.md
!skills-manifest.md
!<stand-in-name-1>
!<stand-in-name-2>
```

- `*` ignores ALL content (9.4MB of skill dirs stay out of git)
- The `!<name>` lines allowlist symlink stand-ins so git tracks them (`create mode 120000` = symlink)
- **Every time you add/remove a stand-in, regenerate this allowlist** from the actual symlinks:
  ```python
  links = sorted(e for e in os.listdir(agents_dir) if os.path.islink(os.path.join(agents_dir, e)))
  # write `!{name}\n` for each
  ```

## Regenerating the Manifest

```python
import os, datetime
entries = []
for e in sorted(os.listdir(agents_dir)):
    if e.startswith('.') or e == '.git': continue
    p = os.path.join(agents_dir, e)
    if os.path.islink(p) or os.path.isdir(p): entries.append(e)
# write "# Skills Manifest\n...- {e}" per entry
```

Plain `ls -d */` misses symlinks — must check `os.path.islink` too.

## Adding a Stand-In (showcase a Hermes skill in the repo)

1. Pick a high-value, general-purpose, **non-sensitive** user-crafted skill from `~/.hermes/skills/<cat>/<name>`
2. Symlink with a RELATIVE path so the link works on the same machine:
   ```python
   rel = os.path.relpath(src_abs, agents_dir)   # ../../.hermes/skills/<cat>/<name>
   os.symlink(rel, os.path.join(agents_dir, name))
   ```
3. Regenerate `.gitignore` allowlist + `skills-manifest.md`
4. `git add .gitignore skills-manifest.md $(ls -l | grep '^l' | awk '{print $9}') && git commit && git push`

**Selection rules for stand-ins:** exclude company-specific / sensitive skills (yuecai, coremail, thinkpad, cuhk, anything with passwords, internal domains, or personal emails). Verify with a regex scan before adding. Don't add skills that already exist as real dirs in `.agents/skills` (name conflict).

## Merging Two Overlapping Skills

When the user says two skills "应该合并（包括原始的），统一改":

1. **Backup both originals first**: `mkdir -p ~/tmp-skill-merge-backup && cp -R ~/.hermes/skills/<cat>/<a> ~/tmp-skill-merge-backup/` (both sides)
2. **Merge into the primary skill** — keep the one that is `auto_inject`/`mandatory`/has the trigger; fold the other's content in as a section, and store the absorbed skill's FULL original SKILL.md as `references/<name>-full.md` (don't bloat the merged SKILL.md)
3. **USER PREFERENCE (explicit correction): blend merged content BY TOPIC — do NOT split it into "第一部分/第二部分" labeled sections.** The user rejected a merged humanizer SKILL.md structured as "Part 1: 中文金融规范" + "Part 2: 通用 AI patterns" with "不要分两部分，把这些混在一起写". Write unified topic sections (e.g. 判断必须有依据 / 禁止夸大与情绪化 / 禁止戏剧化句式 / 精简冗余 / 格式痕迹 / 灵魂与声音 / 自检), with Chinese and English rules side by side inside each topic. Only the verbatim absorbed original goes to `references/<name>-full.md`.
4. Copy any LICENSE into `references/` (e.g. `LICENSE-<source>.txt`) and keep attribution (original author, upstream repo, version)
5. Delete the absorbed skill's original dir: `rm -rf ~/.hermes/skills/<cat>/<absorbed>`
6. Update the `.agents/skills` side: `rm -f <absorbed>` stand-in, regenerate `.gitignore` allowlist + manifest
7. `git add .gitignore skills-manifest.md && git rm --cached <absorbed> 2>/dev/null; git commit && git push`
8. Tell the user the backup location so they can delete it after confirming

**Merging narrow siblings INTO an existing umbrella** (github pattern): when the absorbed skills are narrow siblings of an existing class-level skill, copy each absorbed SKILL.md body into the umbrella's `references/<name>.md`, add a References-table row for each, and append a compact summary section to the umbrella SKILL.md (key points + pointer to the reference). Then delete the standalone skills on both sides as above. Example: `install-skill-from-github` + `install-binary-from-github-releases` → `github/` skill's `references/` + a "## N. Install from GitHub" section.

**Overlap warning pattern:** check for a THIRD overlapping skill (e.g. `ai-writing-humanizer` from a different author also overlaps de-ai-ify-writing) and flag it — don't merge it unprompted.

## Renaming a Skill (and its stand-in)

User may prefer a different name than the current one ("还是叫做humanizer比较好"). Propagate through EVERY layer:

1. `mv ~/.hermes/skills/<cat>/<old> ~/.hermes/skills/<cat>/<new>` (or a different cat if the merge changed it)
2. Update frontmatter in the new SKILL.md: `name:` and `description:` (grep the old name across `~/.hermes/skills/` for other pointers first)
3. `.agents/skills` side: `rm -f <old> && ln -s ../../.hermes/skills/<cat>/<new> <new>`
4. Regenerate `.gitignore` allowlist + manifest
5. **Update cross-references**: project `AGENTS.md`/`CLAUDE.md` files that say `skill=<cat>/<old>` (e.g. yuecai/AGENTS.md "加载 skill=writing/humanizer"), and memory entries. Grep: `grep -rl "<old>" ~/<projects> --include=AGENTS.md`
6. `git add .gitignore skills-manifest.md <new> && git rm --cached <old> 2>/dev/null; git commit && git push` — then commit+push the project file changes separately

## Aggregating Skills into a Subdirectory with an Index (e.g. latex-skills/)

When the user wants all skills of a topic collected under one folder with a `SKILL.md` index that links each sub-skill:

1. Check for duplicates first: `diff -r <root-dir> <agg-dir>/<same>` — delete root copies only when IDENTICAL
2. Move unique real dirs: `mv <root-dir> <agg-dir>/`
3. **Moving a symlink stand-in into a subdir changes relative-path depth**: `../../` becomes `../../../` (one more level). Recreate: `ln -sf ../../../.hermes/skills/<cat>/<name> <agg-dir>/<name>`
4. Update the index `SKILL.md` table with the new entries
5. `.gitignore` — TWO tracking modes, pick per user intent:
   - **Full bundle** (user chose this for latex-skills, "加到追踪里"): `!latex-skills/` + `!latex-skills/**` — index AND all sub-skill contents enter git (sub-skills stay symlinks if they are). A bare `*` matches names at ANY depth, so the `!dir/**` line is required — `!dir/` alone un-ignores the dir entry but NOT files inside it (git check-ignore confirms).
   - **Index-only**: `!latex-skills/` + `latex-skills/*` + `!latex-skills/SKILL.md` — only the index is tracked, sub-skill content stays ignored. Use when the bundle aggregates skills whose content should not be published.
6. Regenerate manifest, commit, push

## Populating from a Multi-Skill Bundle Repo (e.g. huggingface/skills)

When a publisher ships a repo of many SKILL.md dirs (huggingface/skills, vercel-labs/agent-skills), the standard install is: clone once, then symlink the individual skill dirs into each agent's skills dir — no per-skill download:

```bash
git clone https://github.com/<owner>/<repo>.git ~/hf-skills
mkdir -p ~/.claude/skills ~/.agents/skills
for skill in <skill-name-1> <skill-name-2>; do
  ln -sf ~/hf-skills/skills/$skill ~/.claude/skills/$skill   # Claude Code sees it
  ln -sf ~/hf-skills/skills/$skill ~/.agents/skills/$skill   # SSOT sees it (tracked via stand-in)
done
```

- Symlinks keep one source of truth; content lives in the clone, agents see links.
- If the skill is meant for Hermes only, create a Hermes skill instead (skill_manage) or symlink under `~/.hermes/skills/`.
- Some bundles ship an `.mcp.json` — register the MCP server with `hermes config set mcp_servers.<name> '<json>'` (direct config.yaml edits are refused as security-sensitive).

## Pitfalls

- **Nested `.git` dirs**: skills cloned as whole repos (`git clone` into `.agents/skills`) keep their own `.git/`. They don't conflict with the outer repo (ignore-all covers them) but `git add -A` inside the subdir commits to the WRONG repo. Leave them; just don't recurse.
- **Not every dir is a skill**: `best-practices/` was a docs wiki (no SKILL.md) cloned into the skills dir — agents won't load it. Flag to user, don't silently delete.
- **Symlink stand-ins break on other machines**: relative symlinks point at `~/.hermes/skills/` which only exists locally — content is NOT uploaded. If the user wants distributable content, copy the dir instead.
- **`git add .`/`git add -A` forbidden** in this repo per user rule — add explicit paths only.
- **Private vs public**: repo is private by default; stand-ins are metadata, not content, so no IP risk — but scan SKILL.md bodies before ANY upload anyway.
