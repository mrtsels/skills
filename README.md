# ~/.agents/skills — SSOT Skill 目录

本目录是 Agent Skills 标准单源目录（SSOT），存放所有 agent（Claude Code、Codex、Hermes 等）共享的 skills。

- **Skill 内容不入库**（见 `.gitignore`），全部 ignore
- 只跟踪 `.gitignore`、`README.md`、`skills-manifest.md`（skill 清单）
- 清单由 cc-switch / 手动分发时维护

## 查看已安装 skills

```bash
ls ~/.agents/skills/
```

## 更新清单

```bash
cd ~/.agents/skills && ls -d */ | sed 's|/$||' | sort > skills-manifest.md
```
