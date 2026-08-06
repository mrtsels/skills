# HTML 报告重构 Prompt 示例

From session 2026-05-26: 知识工程领导汇报 Page 5 表格→四卡片重构 + 三导迁移。

## 任务概述

**项目**: 知识工程领导汇报 HTML (`公司知识工程实践汇报大纲-领导版.html`)
**改动**: 
1. Page 5: 替换 4 行的问题/选择/理论依据表格为 2×2 核心逻辑卡片
2. Page 6: 将三导「额外的管理创新」从 Page 5 迁移到 Page 6
3. 更新桥接文字 5→6
4. 添加新的 CSS 类

## Prompt 结构解析

### 前置声明
```
TASK: Redesign Page 5 and relocate the "三导" section in the knowledge engineering leadership report HTML.
CONTEXT: Read CLAUDE.md at repo root if it exists first.
```

### 强制 Worktree 工作流
```
WORKTREE WORKFLOW (MANDATORY):
1. git worktree add /tmp/page5-redesign HEAD
2. cd /tmp/page5-redesign
3. Work on file: 公司知识工程实践汇报大纲-领导版.html
4. Commit with clear messages
5. cp file back to main repo, git worktree remove
```

### 精确改动描述（每个改动独立编号）
```
=== CHANGE 1: Redesign Page 5 ===
Current Page 5 (around line 1123-1175) has:
- A 3-column table (问题/我们的选择/理论依据) with 4 rows
- A "额外的管理创新" insight box

Replace with a 2×2 grid of 4 "核心逻辑模块" cards.
Add NEW CSS before .maturity-grid section (~line 448).

Card 1 (gold): 
  Icon: 🧠 | Title: 知识图谱
  Subtitle: 为什么用知识图谱而非纯向量库？
  Body: 知识图谱承载的不只是语义相似度，更是因果关系和任务范式结构。解决问题需要识别因果性，而非仅靠相关性。
  Tag: 第3章「因果确定」
  [其他 3 个卡片同理]
```

### 精确 CSS 代码
```
/* ===== Core Logic Modules (Page 5) ===== */
.core-logic-grid { ... }
.core-card { ... }
.core-card.gold::before { background: var(--gold); }
[所有 CSS 类完整给出]
```

### 提交策略
```
=== COMMITS (2 commits, do NOT push) ===
1. "feat: Replace Page-5 table with 4 core-logic modules"
2. "feat: Relocate 三导 management method from Page-5 to Page-6, update bridge 5→6"
```

## 关键要点

1. **行号范围辅助定位**：给出 approximate line numbers (around line 1123-1175) 帮助 Claude 快速定位
2. **锚点文本精确匹配**：给出确切的可匹配文本（如 `<!-- ===== PAGE 5 ===== -->`）
3. **CSS 完整给出**：不要在 prompt 里写"参考现有样式仿照设计"——直接把完整 CSS 代码写进 prompt
4. **不推送到远程**：明确 `do NOT push`（用户选择什么时候推送）
5. **Worktree 清理**：明确要求 `git worktree remove`
6. **验证步骤明确**：列出具体检查项（broken tags, card count, bridge text）

## 成本参考

本次 session（47 turns, 包含大量缓存命中）：
- input tokens: 36,475 (非缓存) + 1,082,368 (缓存命中)
- output tokens: 14,835
- 总花费: **¥0.09**（deepseek-v4-flash）
- 缓存命中率 97% 大幅降低成本

HTML/设计稿修改类任务通常不涉及复杂推理，始终用 flash 模型即可。
