---
name: project-handover-doc
description: Write comprehensive project handover/交接文档 — one-file README covering server env, code structure, business flow, DB schema, AI config, demo guide, known issues
---

# Project Handover Document (交接文档)

Write a self-contained project handover document when the user asks for one.  
**One file only** — the README.md IS the handover document. No splitting across multiple files.

## Structure (top-to-bottom, 总分 order)

### 1. 目录 (Table of Contents) — 放在最前面
List all major sections. Let the reader see the full scope at a glance.

### 2. 项目概况 — 一句话说明
- What the project does, tech stack, target users
- Production URLs, SSH info, login accounts (formatted as tables)

### 3. 服务器环境与网络拓扑 (Server Environment)
Keep it factual, not conditional:
- Architecture diagram (text-based)
- Server IPs, ports, SSH access
- Service management commands (start/stop/logs)
- Key file paths on the server
- **If server has no network/DNS, state it as a fixed fact**, not "if no network"

### 4. 从零本地启动 (Local Dev Setup)
Step-by-step numbered guide that actually works. Include:
- Prerequisites (JDK, DB, Maven, tool versions)
- Database creation + data import
- Build commands
- Run commands
- Verify commands

### 5. 服务器从零部署 (Production Deployment)
Two-part: first the concise "do this" section, then the "what happens" explanation:
- **操作步骤**: 2-3 commands the operator actually types
- **幕后解析**: Break down each step of the deploy script, explaining what it does behind the scenes

### 6. 数据库表结构与关系 (DB Schema)
- Entity relationship diagram (text-based)
- Table-by-table field descriptions (core fields only, not every column)
- Key relationships (FKs)

### 7. 业务模块与流程图 (Business Flow + Diagrams)
- Three user portals: what each can do
- Core business flow: create application → OCR → scoring → submit → review → approve/reject
- **Flowcharts as PNG images** (rendered from PlantUML, placed in docs/ subfolder)
- Permission matrix (who produces what data, who consumes it)

### 8. AI 配置与提示词 (AI Configuration)
- API endpoint, model, key location
- All prompt templates (final version)
- Configuration priority: env vars → ai-config.json
- **If server has no DNS, note that extra_hosts in docker-compose.yml is already pre-configured**

### 9. API 清单 (API Reference)
List all controllers and their endpoints in a table. One row per controller, brief description of endpoints.

### 10. 演示指南 (Demo Guide)
- Step-by-step demo for each user type
- Which data comes from seed data vs real
- Where to find screenshots/video

### 11. 已知问题与风险 (Known Issues)
**Priority-ordered by severity, NOT by topic:**

| Severity | # | Problem | Source file:line | Impact | Workaround |
|---|---|---|---|---|---|
| 🔴 P0 (emergency/security) | 1 | ... | ... | ... | ... |
| 🟡 P1 (high/robustness) | 10 | ... | ... | ... | ... |
| 🟢 P2 (medium/maintainability) | 25 | ... | ... | ... | ... |

Include a **演示翻车应急** table at the end: common failures (page blank, login fails, OCR broken) and quick fixes.

### 12. 常见问题排查 (Troubleshooting)
Pattern-based: "backend won't start → check X", "white screen → check Y", "OCR not working → check Z"

### 13. 附录：项目结构 (Appendix)
Directory tree annotated with what each directory/file does.

## Style Rules
- **No conditional language**: "server has no network" not "if server has no network"
- **No placeholder personal info**: do not include the writer's name, contact, or future plans
- **Tables > paragraphs** for accounts, ports, file paths, issue lists
- **Code blocks** for commands, config files, and API responses
- **PlantUML diagrams rendered as PNG**: use raw deflate + ~1 prefix encoding for plantuml.com
- One file is the single source of truth — no "see also other_doc.md"
