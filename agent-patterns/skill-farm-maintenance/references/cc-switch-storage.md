# cc-switch Skill Storage Logic (from source reading, v3.19.x, Aug 2026)

Repo: `github.com/farion1231/cc-switch` (Tauri desktop app). Skill-management module lives in `src/components/skills/` (UI) + `src-tauri/src/services/skill.rs` (logic) + `src-tauri/src/settings.rs` (config).

## Two storage locations (SSOT single-source dir)

Setting `skill_storage_location` (enum `SkillStorageLocation`, default `cc_switch`), persisted in `~/.cc-switch/config.json`:

| Mode | SSOT dir | Notes |
|------|----------|-------|
| `cc_switch` (default) | `~/.cc-switch/skills/` | cc-switch private, centralized |
| `unified` | `~/.agents/skills/` | Agent Skills standard dir — Codex etc. discover natively |

`get_ssot_dir()` (skill.rs:509): matches setting, `fs::create_dir_all` before returning.

## Directory resolution

- `get_home_dir()`: `CC_SWITCH_TEST_HOME` env override (tests only) → `dirs::home_dir()`.
- `get_app_config_dir()`: `~/.cc-switch`; override via app_store; Windows falls back to legacy `HOME/.cc-switch` only if default has no `cc-switch.db`.
- Hermes dir priority (hermes_config.rs:53): CCS setting `hermes_config_dir` override → `HERMES_HOME` env → platform default (Mac/Linux `~/.hermes`, Windows `%LOCALAPPDATA%\hermes`).

## Per-app skills dirs (`get_app_skills_dir`, skill.rs:529)

Each app supports a settings override, else default:

| App | Default |
|-----|---------|
| Claude | `~/.claude/skills/` |
| ClaudeDesktop | `~/.claude-desktop/skills/` (but sync SKIPS this app) |
| Codex | `~/.codex/skills/` |
| Gemini | `~/.gemini/skills/` |
| GrokBuild | `~/.grok/skills/` |
| OpenCode | `~/.config/opencode/skills/` |
| OpenClaw | `~/.openclaw/skills/` |
| Hermes | `<hermes_dir>/skills/` (i.e. `~/.hermes/skills/`) |

## Sync method (`skill_sync_method`, default Auto)

How SSOT → per-app dirs:

- **Auto**: dest exists as real dir → copy (replace); else remove old symlink → try symlink → fallback copy.
- **Symlink**: force symlink (remove old path first).
- **Copy**: force copy via temp-name + atomic replace.

## Migration (`migrate_storage`, skill.rs:1238)

Safety ordering: **move files first, persist setting last** (crash keeps old dir). Per-skill `fs::rename`, fallback copy+delete; `require_valid_directory` guards path traversal; errors collected per-skill (soft fail); then `sync_to_app` for every `AppType` to refresh all symlinks. Backup dir is fixed `~/.cc-switch/skill-backups/` regardless of storage location.

## Implications for this machine

- User's `~/.agents/skills/` (210+ dirs) + `~/.claude/skills/` symlinks = exactly cc-switch "unified" mode, done manually.
- cc-switch flattens skills into `~/.hermes/skills/` — Hermes accepts both flat and category-nested, but categories get mixed.
- Symlinks point at `~/.hermes/skills/` locally; cloned repo stand-ins break off-machine (metadata only).
