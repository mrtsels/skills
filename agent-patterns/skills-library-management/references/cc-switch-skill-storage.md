# cc-switch Skill Storage Internals

Source: farion1231/cc-switch (Tauri desktop app), read 2026-08-06.

## Storage location setting (SSOT dir)

`skill_storage_location` in settings, two modes:

| Mode | SSOT dir |
|------|----------|
| `cc_switch` (default) | `~/.cc-switch/skills/` |
| `unified` | `~/.agents/skills/` |

Home dir resolution: `CC_SWITCH_TEST_HOME` env override → `dirs::home_dir()`.
App config dir: override → `~/.cc-switch` (Windows: falls back to legacy `HOME/.cc-switch` only if default has no DB).

## Per-app skills dirs (get_app_skills_dir)

Each app has an optional settings override, else default:

- Claude: `~/.claude/skills/`
- Codex: `~/.codex/skills/`
- Gemini: `~/.gemini/skills/`
- OpenCode: `~/.config/opencode/skills/`
- OpenClaw: `~/.openclaw/skills/`
- Hermes: `~/.hermes/skills/` — resolved via: CCS override → `HERMES_HOME` env → platform default (`~/.hermes` mac/linux, `%LOCALAPPDATA%\hermes` windows)
- ClaudeDesktop: `~/.claude-desktop/skills/` (sync skips it)

## Sync method (skill_sync_method)

SSOT → app dir: `Auto` (default), `Symlink`, `Copy`.

Auto logic: dest exists as real dir → copy; dest is symlink → remove then try symlink, fallback to copy. Copy path uses tmp name + atomic replace.

## Migration (migrate_storage)

Order matters: move files FIRST (per-skill `rename`, fallback copy+delete, path-traversal validation, per-skill error collection), persist setting ONLY after all moves, then refresh symlinks for all apps. Crash mid-migration leaves setting pointing at old dir.

Backups: always `~/.cc-switch/skill-backups/`, independent of storage location.

## Relevance to this machine

User's `~/.agents/skills/` already IS the unified SSOT (210+ skills, real dirs + symlink stand-ins to `~/.hermes/skills/`). cc-switch unified mode would adopt it without moving files. Hermes skills land flat in `~/.hermes/skills/` via cc-switch (no category nesting) — Hermes reads both flat and nested.
