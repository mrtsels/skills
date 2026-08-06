---
name: install-skill-from-github
description: Install an agent skill from a GitHub repository URL or ClawHub registry. Handles raw file discovery, dependency installation, security verification, and validation. Use when the user asks to install a skill from a GitHub URL, ClawHub page, or any third-party skill registry.
---

# Install Skill from Registry (GitHub / ClawHub)

## When to Use

Load this skill when the user asks to install a skill from a GitHub URL, ClawHub, or any third-party skill registry — whether given a raw file URL, a registry page like `clawhub.ai/...`, a repo page, or just a repo name. Covers both skills with install guides (INSTALL.md) and self-contained skill repos.

**First step: identify the source.** GitHub and ClawHub have different workflows. If in doubt, try `hermes skills search <name>` — it searches ClawHub and skills.sh.

### GitHub Triggers

- "install this skill" + GitHub URL
- "curl the README and install"
- "install from https://github.com/.../skill"
- "fetch and follow instructions from" + raw URL
- "install the X skill from GitHub"

### ClawHub Triggers

- ClawHub URLs (`clawhub.ai/<publisher>/<skill>`)
- "install from ClawHub"
- "install the X skill" without a GitHub URL (try ClawHub first via `hermes skills search <name>`)

## ClawHub Verification & Install Workflow

**User prefers a step-by-step verification process before any ClawHub install.** Do not skip steps. Do not install before checks pass.

### Step 1 — Visit the ClawHub Page

Navigate to the skill page and read the overview, requirements, and security audit.

```bash
browser_navigate(url="https://clawhub.ai/<publisher>/<skill>")
```

Capture:
- Publisher name and trust level (community/verified/official)
- Skill description and version
- **Requirements section** — list all required packages/binaries
- **Hardware requirements** — GPU, RAM, disk
- **Browser setup** — any cookie/captcha dependencies
- **Security audit badge** — click to view NVIDIA SkillSpector findings
- File listing on the Files tab — note the file count and types

### Step 2 — Inspect with Hermes Before Install

Run `hermes skills inspect` to see the SKILL.md content *and* trigger Hermes' own security scan:

```bash
hermes skills inspect "https://clawhub.ai/<publisher>/<skill>"
```

Read the preview output carefully:
- **Hermes security scan verdict** (SAFE / DANGEROUS / SUSPICIOUS)
- **Scan findings** — specific file + line number + pattern matched
- **SKILL.md preview** — confirm frontmatter (name, version, description)

### Step 3 — Verify Source and Contents

Check three things:

1. **Publisher credibility** — click the publisher link on ClawHub. Do they have multiple skills? How long have they been publishing? Is the account new/suspicious?
2. **Package contents** — the Files tab shows every file. Check:
   - Script files (`.sh`, `.py`, `.js`) — what do they do? Any network calls?
   - `python3 -c` inline code in shell scripts — is it JSON parsing (normal) or obfuscation?
   - Any `curl | bash` patterns, hidden eval, or suspicious file writes
3. **Dependencies** — from the Requirements section and SKILL.md. Only trust well-known packages (yt-dlp, ffmpeg, whisper, opencc, etc.)

### Step 4 — Read the Security Audit

Click the "View Security Audit" link on the ClawHub page. Pay attention to:

- **High severity findings** — especially TP4 (documented behavior understates real behavior)
- **Missing User Warnings** — does the skill auto-access browser cookies without informing the user?
- **Context-Inappropriate Capability** — doing things not described in the overview
- **Natural-Language Policy Violations** — misleading descriptions
- **VirusTotal** — any malware flag on the download archive

### Step 5 — Assess Platform Compatibility

ClawHub skills are often written for WSL/Windows (cookie extraction from WSL Chromium, Windows Edge). Check if the skill works on the user's platform (macOS). Note any platform-specific limitations.

### Step 6 — Present Findings and Ask

Before installing, present a concise summary to the user:

```
## 技能校验结果

### 发布者 / 来源
- **发布者**: <name> (社区/已验证/官方)
- **来源**: ClawHub
- **文件**: N 个文件 (<file types>)

### 安全扫描
- **Hermes 扫描**: <SAFE/DANGEROUS> — <findings summary>
- **ClawHub 审计**: <findings summary>
- **注意**: <key concern>

### 依赖
- **需安装包**: <list>
- **macOS 兼容**: <yes/no/partial>

### 建议
<recommendation>
```

Then ask the user: **"要装吗？还有安装依赖需要我搞定吗？"**

### Step 7 — Install

Only proceed after user confirmation. Use:

```bash
hermes skills install "https://clawhub.ai/<publisher>/<skill>"
```

This auto-downloads the skill, copies it to `~/.hermes/skills/<name>/`, and registers it.

If the skill references system packages (yt-dlp, ffmpeg, whisper, opencc), install them:

```bash
# macOS
brew install yt-dlp ffmpeg  # video/audio tools
pip install openai-whisper  # speech-to-text (requires GPU)
brew install opencc          # Traditional→Simplified Chinese

# Verify
which yt-dlp ffmpeg
python3 -c "import whisper; print(whisper.__version__)"
```

### ClawHub Pitfalls

- **Security scans can false-positive** — `python3 -c` inline JSON parsing (common in shell scripts for parsing yt-dlp output) gets flagged as "obfuscation". It's usually legitimate JSON parsing, not malware. Judge based on context, not just the scanner label.
- **WSL/Windows-centric skills** — many ClawHub skills target WSL Chromium cookie access. On macOS, cookie detection and member-only video access won't work without adaptation.
- **Automated cookie access without consent** — some skills silently read browser cookies. Flag this to the user during the verification step.
- **Don't install without user confirmation** — the user explicitly requires being asked before any install.

## Workflow

### Step 1 — Identify the Skill Files

Fetch the README (or INSTALL.md if present) to understand what files to download and whether there are dependencies.

```bash
# Try README first, fall back to INSTALL.md
curl -sL "https://raw.githubusercontent.com/{owner}/{repo}/main/README.md"
# or
curl -sL "https://raw.githubusercontent.com/{owner}/{repo}/main/INSTALL.md"
```

Use `browser_navigate` if curl times out.

Inspect the repo file listing (via GitHub web UI or API) to identify all required skill files. Common patterns:
- Standard skill: `SKILL.md`, `README.md`, `LICENSE`
- Tool skill with code: `main.py`, `requirements.txt`, `skill.json`, `README.md`
- Some repos use: `SKILL.md`, `README.md`, `LICENSE`, plus supporting scripts/configs

### Step 2 — Detect the Skills Directory

Check which agent family is running to resolve the correct skills directory:

```bash
# OpenCode
ls ~/.config/opencode/skills/ 2>/dev/null && echo "opencode" || true
# Claude Code
ls ~/.claude/skills/ 2>/dev/null && echo "claude-code" || true
# .agents/skills style (Hermes/default)
ls ~/.agents/skills/ 2>/dev/null && echo "agents-skills" || true
```

Default if ambiguous: `~/.agents/skills/`

### Step 3 — Download Files

Create the target folder and download each required file:

```bash
SKILL_NAME="<skill-name>"  # e.g. summarize-slides, pdf-convert-to-image
SKILLS_DIR="${HOME}/.agents/skills"
TARGET_DIR="${SKILLS_DIR}/${SKILL_NAME}"

mkdir -p "${TARGET_DIR}"
cd "${TARGET_DIR}"

# Download identified files (common pattern)
for f in README.md SKILL.md LICENSE main.py requirements.txt skill.json; do
  curl -sL -O "https://raw.githubusercontent.com/{owner}/{repo}/main/$f" 2>/dev/null
done
```

**Naming rule**: folder name is the skill name (e.g. `summarize-slides`), NOT `*-skill`.

### Step 4 — Install Dependencies

Check for and install dependencies:
- Python deps: `pip install -r requirements.txt` or `pip install <package>`
- System deps (poppler for PDF tools, etc.): note them for the user

```bash
# Install Python deps if requirements.txt exists
pip install -r "${TARGET_DIR}/requirements.txt" -q
```

### Step 5 — Validate

```bash
# Confirm files exist
ls -la "${TARGET_DIR}/"

# Confirm deps importable (for Python skills)
python3 -c "import <package_name>" 2>/dev/null && echo "deps OK"
```

### Step 6 — Report

Report: skills directory, installed path, files, install result (`strictly validated` / `path-validated` / `incomplete`), and any capability warnings (missing deps, runtime requirements not met).

## Special Case: Iwencai/SkillHub Square Skills

Some skills come from the 同花顺 iwencai SkillHub square (not GitHub/ClawHub). The download mechanism differs.

**Detection:** The user asks to install a skill by Chinese or English name (e.g. "模拟炒股", "hithink-astock-selector", "report-search", "量化因子选股"). Skills from iwencai square may NOT be on ClawHub/GitHub.

### Step 1 — Try the Iwencai Square Direct Download

```bash
curl -s "http://ms.10jqka.com.cn/gateway/market/api/v1/skills/square/download?name={slug}" -o /tmp/{slug}.zip -w "HTTP %{http_code}"
file /tmp/{slug}.zip
```

- If it returns `Zip archive data` → proceed to Step 2
- If it returns `JSON data` (not a zip) → the skill is NOT on the iwencai square. Try ClawHub via `https://lightmake.site/api/v1/download?slug={slug}` instead.

### Step 2 — Get the Slug

Search the skill by Chinese/English name on the lightmake registry:

```bash
curl -s "https://lightmake.site/api/v1/search?q={name}" | python3 -c "import sys,json; [print(r.get('slug','')) for r in json.load(sys.stdin).get('results',[]) if 'keyword' in str(r)]"
```

Try the slug directly if known, or infer from the iwencai square download name.

### Step 3 — Extract and Inspect

```bash
unzip -o /tmp/{slug}.zip -d /tmp/{slug}/
find /tmp/{slug} -type f
```

Most iwencai square skills have this structure:
- `SKILL.md` (or `skill.md`) — YAML frontmatter with name, description, API spec
- `scripts/cli.py` — CLI for API calls (pure Python stdlib, no external deps)
- `references/api.md` — API reference (optional)
- `LICENSE.txt` — MIT license (optional)

### Step 4 — Create Hermes Skill

```bash
# Create the skill
skill_manage(action='create', category='tonghuashun', name='{slug}', content='{converted SKILL.md}')

# Copy scripts
skill_manage(action='write_file', name='{slug}', file_path='scripts/cli.py', file_content='{script content}')

# Copy references (if any)
skill_manage(action='write_file', name='{slug}', file_path='references/api.md', file_content='{api doc content}')
```

**SKILL.md conversion:** Replace `{baseDir}` placeholders with empty string or `scripts/` path. Simplify clawhub-specific metadata. Keep the API endpoint, headers, and CLI usage sections intact.

### Step 5 — Set Required Environment Variables

Most iwencai skills need:

```bash
export IWENCAI_BASE_URL=https://openapi.iwencai.com
export IWENCAI_API_KEY=<key-from-skillhub-page>
```

Add to shell profile (`~/.zshrc` / `~/.bashrc`) if not present.

### Iwencai Skill Endpoint Patterns

Two API endpoints used by iwencai skills:

| Endpoint | Skill Series | Body Pattern |
|----------|-------------|-------------|
| `/v1/query2data` | `hithink-astock-selector`, `hithink-market-query`, `hithink-industry-query` | `{"query":"...","page":"1","limit":"10","is_cache":"1","expand_index":"true"}` |
| `/v1/comprehensive/search` | `report-search`, `announcement-search`, `news-search` | `{"query":"...","channels":["report"|"announcement"|"news"],"app_id":"AIME_SKILL","size":10}` |

All share the same Claw headers pattern (`Authorization: Bearer`, `X-Claw-Skill-Id`, `X-Claw-Trace-Id`, etc.).

### Iwencai Install Pitfalls

- **Download URL mismatch**: The iwencai square URL returns JSON (not a zip) for skills NOT hosted on their square (e.g., clawhub skills). Always check `file` output after download.
- **metadata.json URL needs override**: The `iwencai-skillhub-cli` metadata defaults to the iwencai square URL. For clawhub skills, override with `--primary-download-url-template "https://lightmake.site/api/v1/download?slug={slug}"`.
- **Chinese slug names**: Some iwencai square slugs are Chinese (URL-encoded). Use the URL-encoded form in the download URL.
- **Scripts are pure stdlib**: iwencai CLI scripts use zero external dependencies (only `urllib.request`, `json`, `secrets`). No `pip install` needed.

## Special Case: Vercel Labs Agent-Skills Package (npx skills add)

When the repo contains multiple SKILL.md files under a `skills/` directory (like taste-skill, vercel-labs/agent-skills), **do NOT download individual files**. Use `npx skills add` instead — it handles discovery, installs all skills, and symlinks to Claude Code / Hermes / Codex automatically:

```bash
# From a local clone
npx skills add /path/to/repo -y -g

# From GitHub URL
npx skills add https://github.com/{owner}/{repo} -y -g
```

| Flag | Meaning |
|------|---------|
| `-y` | Skip interactive skill-selection prompt (install all) |
| `-g` | Install globally (available to all agents) |

**Detection:** check if the repo has a `skills/` directory with multiple `SKILL.md` files. If yes → use `npx skills add`. If only a single `SKILL.md` at root → use the standard download approach below.

**Install locations:** puts skills in `~/.agents/skills/` and symlinks to `~/.claude/skills/`, Hermes Agent, Codex, Cursor, GitHub Copilot, and others automatically.

## Special Case: MCP-Server + Skill Combos

Some GitHub repos ship a Claude Code skill that **requires a companion MCP server** (usually an npm package). The skill directory lives under `skills/<name>/` inside the repo while the MCP server is a separate npm package. **Detect this** by checking `package.json` at the repo root and looking for `mcp`, `mcp-server`, or `@modelcontextprotocol` keywords.

**Detection checklist:**
- Repo has `skills/<name>/SKILL.md` under a single subfolder (NOT multiple SKILL.md files at `skills/` level — that's the `npx skills add` case)
- Repo has `package.json` with a `bin` field naming CLI commands
- README mentions MCP configuration for Claude Desktop / Claude Code / Hermes

**Installation workflow:**

```bash
# 1. Install the MCP server globally
npm install -g <npm-package-name>

# 2. Copy the skill for Claude Code
cp -r skills/<skill-name> ~/.claude/skills/<skill-name>/

# 3. Copy the skill for Hermes
cp -r skills/<skill-name> ~/.hermes/skills/<skill-name>/
# Adapt SKILL.md for Hermes if needed (remove Claude Code slash-command patterns)

# 4. Configure MCP server in Claude Desktop (3p mode — note the special path!)
#    Path: ~/Library/Application Support/Claude-3p/claude_desktop_config.json
#    Add under mcpServers: { "server-name": { "command": "global-command" } }

# 5. Configure MCP server in Hermes
#    Edit ~/.hermes/config.yaml, add under mcp_servers:
#    server-name:
#      command: global-command
#      timeout: 120

# 6. Install MCP SDK for Hermes (if not already)
pip install mcp
```

**Claude Desktop config locations:**

| Mode | Config path |
|------|-------------|
| Standard | `~/Library/Application Support/Claude/claude_desktop_config.json` |
| 3p mode | `~/Library/Application Support/Claude-3p/claude_desktop_config.json` |

**Hermes config.yaml editing pitfall:** Avoid using Python `yaml.dump()` to programmatically edit `~/.hermes/config.yaml`. PyYAML re-serializes the entire file, changing key order and possibly breaking formatting (e.g., inline JSON strings, flow mappings, comments). Prefer the `patch` tool for surgical edits. If you must use a script, verify the output is syntactically valid and all expected keys are present.

**Naming convention for Hermes MCP tools:** Tools are prefixed `mcp_{server_name}_{tool_name}`. E.g., server `rednote` with tool `search_notes_by_keyword` becomes `mcp_rednote_search_notes_by_keyword`. Use this when instructing the agent how to invoke them.

## Notes

- Use `browser_navigate` as fallback when `curl` times out on GitHub raw URLs
- Some repos have very large READMEs with embedded code — fetch once, don't re-fetch per step
- If the repo has an INSTALL.md with its own step-by-step guide, prefer following that guide exactly over this generic workflow
- For skills with companion/dependency skills (like `pdf` for document processing), install those too if the platform and license permit
- GitHub unauthenticated rate limit is 60 req/hour for API, but raw content URLs are less restrictive
- If the repo has a `skills/<name>/` directory (single skill in a subfolder, NOT multiple SKILL.md files at `skills/` level), manually copy the subfolder — `npx skills add` only handles flat multiplies
- When installing for both Claude Code AND Hermes, do all agent configs in parallel: copy both skill directories, configure MCP servers in both configs, verify both
