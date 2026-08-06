---
name: live-meeting-notes
description: "实时口授会议纪要。用户在会议中边说边记，需要即时整理观点、搜索验证数据、按结构化格式输出 Markdown。适用于投资研究会议、专题培训、客户沟通等场景。"
version: 1.0.1
author: Hermes Agent
license: MIT
metadata:
  hermes:
    tags: [meeting, notes, real-time, dictation, research]
    related_skills: [lecture-notes]
---

# Live Meeting Notes（实时会议纪要）

## Overview

用户在会议中口授要点，Agent 实时记录、即时搜索补充数据、按结构化 Markdown 输出。与 lecture-notes（从 PDF 生成笔记）互补——本 skill 处理**无预设材料的口授场景**。

## When to Use

- 用户说"做会议纪要"、"开个会记一下"、"接下来讲XXX"
- 用户边说边停，Agent 逐段记录
- 用户提到行情/事件/数据 → 需要主动搜索验证，不能只记表面
- 会议涉及多个主题 → 分节记录，需要架标题再填充

## Workflow

### Step 0: 确认存放位置

会议纪要存 `meetings/` 目录，按 `jul-NN.md` 命名（如 `meetings/jul-09.md`）。**不要**放到 `docs/` 下。

### Step 0.5: 续接前次会议

当用户说"接着/之前的会议纪要"时：

1. 先 `read_file` 前次会议文件，了解已有内容和格式
2. 在新 `jul-NN.md` 中加一段"续接"说明，引用前次会议的数据做对比
3. 行情回顾类会议：在用户开口前先查实时价格，填入对比表格

**例子：** 用户说"接着 jul-06 回顾黄金白银" →
- 读 `meetings/jul-06.md` 提取金价、银价
- 查当前实时价格（Gold API / Yahoo Finance）
- 在新文件中建对比表格（前次 vs 当前，算涨跌幅）

### Step 1: 架标题

先创建会议纪要的基本框架（`meetings/jul-NN.md`）：

```markdown
# XXX专题 — 会议纪要

日期：YYYY-MM-DD
主讲人：
参与人：
```

### Step 2: 实时口授记录

用户每说一段话，用 `patch` 追加到文件末尾。

**记录原则：**
- 用户说的原话要提炼为要点，不要逐字复读
- 专业术语保留原文（如 AU2603C200、XAGUSD）
- 涉及具体数字、时间、价格 → 必须有精确值
- **不要只记表面现象，要记录因果链条**（用户说"查一下"时要主动搜索）
- 每个主题独立一个二级标题 `##`

### Step 2.5: 处理会议截图/照片（必做，不等提醒）

用户可能拍照或截图发来会议内容（Word/PPT 屏幕照片）：

1. `vision_analyze` 提取全部文字
2. 按结构化格式追加到 `meetings/jul-NN.md`
3. **立即删除桌面图片** — `rm /Users/minimx/Desktop/Image*.jpeg`（用户明确要求处理完即删）
4. `git add + commit + push`（每张图处理完就提交，不要攒）
5. 连续多张图片每张均执行 1-4 步
6. 注意文件名可能含空格（如 `Image 2.jpeg`），用引号包裹

### Step 3: 主动搜索验证

当用户提到"可以查一下"、"你看看"或提及具体行情/事件时：

1. 用浏览器/API 查实时数据（TradingView、Yahoo Finance 等）
2. 记录关键数据（价格、涨幅、时间范围）
3. 挖掘前因后果：
   - 事件前的走势
   - 事件后的影响
   - 与用户观点的关联

### Step 4: 结构化整理

每个主题按合适的格式组织：

| 数据类型 | 推荐格式 |
|---------|---------|
| 价格/行情 | 表格（周期|涨幅） |
| 因果链条 | 三段式（前因/事件/后果） |
| 对比 | 两栏表格 |
| 关键结论 | 加粗 |

### Step 5: 持续 commit（会议中）

会议中每记录 2-3 个主题或用户明确要求时，立即 git commit + push，**不要等到会议结束**。按 `docs:` prefix 提交，描述涵盖本次 commit 涉及的主题。

```bash
git add meetings/jul-NN.md
git commit -m "docs: add meeting notes - <主题1>, <主题2>"
git push
```

### Step 6: 最终归档

会议结束后：
1. 确认文件完整性
2. 检查是否有未推送的 commit（`git log --oneline origin/main..HEAD`）
3. 如果会议产生后续任务，记录在 `## TODO` 部分

## Common Pitfalls

1. **未确认目录结构就创建文件** — 用户说"做笔记"时，先检查项目现有的目录树（`meetings/` `notes/` `docs/`），不要假设位置。用 `ls` 或 `find` 先看一遍
2. **文件放错位置** — 会议纪要存 `meetings/` 目录，不是 `docs/`
3. **只记表面不查因果** — 用户说行情事件要查具体数据
4. **数字模糊** — 写具体值而不是概数
5. **结构不清晰** — 用户切换话题时要加 `## 新话题` 标题
6. **第一次搜索被墙** — Google/Bing 可能被拦截，备选 Yahoo Finance API、TradingView、新浪财经
- **commit 拖到会后** — 用户要求"做笔记的时候也要git"，每 2-3 个主题就 commit + push，不要攒到结束

## Verification Checklist

- [ ] 文件路径正确（meetings/jul-NN.md）
- [ ] 创建文件前确认了项目目录结构
- [ ] 所有用户提及的话题都有对应章节
- [ ] 涉及行情/数据的部分经过主动搜索验证
- [ ] 数字精确到具体值
- [ ] 因果链条完整
- [ ] 会议中已分步 commit + push（非一次性提交）

## Example

- `references/jul-06-example.md` — 口授型会议纪要（用户边说边记，Agent 搜索验证）
- `references/screenshot-meeting-flow.md` — 截图型会议纪要（用户拍照/截图发来，Agent 逐张提取整合）
