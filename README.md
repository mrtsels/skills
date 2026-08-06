# ~/.agents/skills — Skill 库 SSOT

所有 agent（Claude Code / Codex / Hermes）共享的 skill 单一真源目录。

- 真身：本目录（分类结构，`<category>/<skill>/SKILL.md`）
- `~/.hermes/skills`、`~/.claude/skills` 只放相对 symlink 指向本目录
- git 追踪全部内容（私有仓库 mrtsels/agents-skills），敏感文件由 `.gitignore` 显式排除

## 目录结构

```
~/.agents/skills/
├── .gitignore          # 系统垃圾 + 敏感文件排除（无 ignore-all）
├── README.md           # 本文件
├── skills-manifest.md  # skill 清单（脚本生成）
├── latex-skills/       # bundle：索引 SKILL.md + 子 skill 目录
├── finance/            # 分类目录
│   └── tonghuashun/
│       └── SKILL.md
└── ego-browser         # 唯一 symlink（指向 /Applications/ego lite.app）
```

分类：`academic` `agent-patterns` `apple` `automation` `autonomous-ai-agents` `creative` `data-science` `devops` `email` `finance` `github` `infrastructure` `latex-skills` `mcp` `note-taking` `productivity` `research` `resume` `software-development` `workflow` `writing`

## 命名规范

1. **一律 kebab-case**：小写 + 连字符，禁下划线/驼峰（`pdf-extraction-guide` ✓，`pdfExtraction` ✗）
2. **名称即主题**：以领域关键词开头，让同类可聚合（`arxiv-api`、`arxiv-batch-reporting`）
3. **后缀表示形态**：
   - `-guide`：教程/方法论（`pytorch-guide`）
   - `-api`：API 集成（`openalex-api`）
   - `-template`：模板（`conference-paper-template`）
   - `-skills`：聚合 bundle 索引（`search-skills`）
   - `-builder/-generator`：产出物生成器
   - 其余默认动词短语（`pdf-extraction-guide`）
4. **长度 ≤ 35 字符**，超长需精简
5. **bundle 索引**：`<主题>-skills`，子 skill 用独立名词

## SKILL.md 写作规范

### frontmatter（必填）

```yaml
---
name: <目录名一致>
description: "<单行，≤150 字符，说明触发条件与功能>"
---
```

- `name` 必须与目录名完全一致
- `description` 必须双引号包裹；以触发场景开头（"Use when …" / "当用户需要…"），不用句号结尾
- 可选：`tags`（小写复数）、`metadata`（保留第三方原作者信息）

### 正文结构

```markdown
# <Title>

Trigger: <什么场景触发本 skill>

## <工作流/步骤>        # 按执行顺序，编号步骤
## Pitfalls            # 坑点，每条一行
## References          # 引用文件表（可选）
```

规则：
- 标题层级从 `#`（skill 名）开始，正文小节用 `##`
- 步骤用有序列表（1. 2. 3.），关键命令给完整代码块
- Pitfalls 每条一行，写"发生了什么 → 怎么避免"
- 中文 skill 正文用中文，英文 skill 用英文，不混写
- 长度控制：主 SKILL.md ≤ 10KB，长内容放 `references/`
- 合并 skill 时按主题混写，禁止"第一部分/第二部分"式分段

### 敏感信息红线

- 禁出现：个人姓名、电话、个人/公司邮箱、密码、内网 IP、内部系统账号
- 必须写示例时用占位符（`{Author Name}`、`example.com`）
- 引用私有系统（粤财/衡泰/NAS）的 skill 整体加入 `.gitignore`

## 维护命令

```bash
# 清单重新生成
python3 -c "
import os
for e in sorted(os.listdir('.')):
    if e.startswith('.'): continue
    p = os.path.join('.', e)
    print(e if os.path.islink(p) or os.path.isfile(os.path.join(p,'SKILL.md')) else f'{e}/ ({len(os.listdir(p))} skills)')
" > skills-manifest.md

# git（禁 add .）
git add <具体路径> && git commit -m "type: subject" && git push
```

提交前必须跑 PII 扫描（见 `agent-patterns/skill-farm-maintenance`）。
