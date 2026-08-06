# 政策研究批量入库模式（2026-06-23 实测）

## 场景

政府政策搜索→结构化入库→多层级归档，输出是 .md 文档（原文+摘要）。30 份省级 + 2 份市级 + 2 份区级 + 5 份分析，~7,000 行，总耗时约 2 小时，总花费 ¥1.77（全 flash）。

## 核心分工

| 角色 | 做什么 |
|------|--------|
| **Hermes** | 构造搜索 prompt（部门、方向、输出格式）、创建 worktree、验证结果、更新 TASK.md、记录成本 |
| **Claude Code** | 搜索政府网站、提取原文、创建 原文+摘要 .md 文件、git add/commit/push |

## 工作流

```
Hermes: 创建分支 + worktree（单一分支，不做逐子任务 PR）
     ↓
for each department:
  1. Hermes 构造 prompt（搜索方向 + 输出格式 + 验证 + git 步骤）
  2. terminal(claude --model sonnet --bare ...) 后台启动
  3. 等 notify → 验证文件 → 继续下一轮
     ↓
全部完成后: 创建 1 个 PR → merge → 更新 TASK.md → 记录成本
```

## Prompt 模板

```bash
cat > /tmp/prompt_xxx.txt << 'PROMPT_END'
TASK: 搜索并入库XX部门专精特新配套政策

CONTEXT:
项目在 /tmp/worktree-xxx/（分支 feat/xxx）。
已有文件 01-NN 在 docs/policy-research/province/ 下，格式参考已有的 .md 文件。

WORKTREE WORKFLOW:
1. cd /tmp/worktree-xxx
2. Read existing .md files for format reference
3. Search government websites, visit URLs for full text
4. Create original text + summary files (starting from NN+1)
5. Verify: ls -la && wc -l
6. git add && git commit -m "feat(policy): add XX matching policies"
7. git push origin <BRANCH>

搜索方向（列出具体文件名/文号/关键词）：
1. ...
2. ...

Output format per file:
- -原文.md: 政策全文（含来源URL、文号）
- .md: 政策基本信息表 + 核心条款分类（含条款号） + 系统关联分析

IMPORTANT: 每条款必须标注原文条款号。每项信息必须附可验证的政府URL。不完整标"待核实"。
PROMPT_END

cd <WORKTREE_PATH> && claude --model sonnet --bare --dangerously-skip-permissions --output-format json -p "$(cat /tmp/prompt_xxx.txt)"
```

## 关键经验

1. **单一分支 + 多 commit + 最后统一 PR** — 比逐子任务创建 PR 高效很多。内容类任务不需要每个独立 PR。
2. **每次 prompt 维护起始编号** — 如前一轮到 13，下一轮从 14 开始。在 prompt 里写死。
3. **验证只需 `ls -la && wc -l`** — 不需要写测试。检查原文+摘要成对出现即可。
4. **Flash 足够** — 搜索+文档创建对推理要求低。5 轮 flash 调用共 ¥1.77（含大量缓存命中）。
5. **worktree 复用** — 不要每轮创建新 worktree。创建一次，所有 Claude 调用共享同一 worktree。
6. **`.md` 格式参考** — 先让 Claude Code 读 1-2 个已有文件，保证新文件的格式风格一致。

## 命名约定

- 原文文件: `NN-中文描述-原文.md`
- 摘要文件: `NN-中文描述.md`
- 分析文件: `analysis/NN-中文描述.md`
- 层级目录: province/ (省), city/ (市), district/ (区)
