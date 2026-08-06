# Claude Code Dynamic Workflows — 小红书社区见闻

> 来源：小红书搜索 "Claude Code 动态工作流" / "Claude Code 自动模式" / "Dynamic Workflow" (2026-05-29)
> 社区称其为"动态工作流"而非"cowork自动模式"

## 概述

Claude Code v2.1.154+ 引入 **Dynamic Workflows** — 根据用户任务自动生成工作流脚本，调度多个甚至几十上百个子 Agent 并行执行，交付整理后的结果。小红书中文社区称之为"动态工作流"。

## 发现的关键帖子

### 1. AI随风 — "Claude Code动态工作流，让AI协作更高效" (45分钟前)
- 视频教程，保姆级讲解 Dynamic Workflows
- 解释了：它是什么、与普通对话/子代理/Agent Teams 的区别
- 如何开启、查看/暂停/恢复工作流
- 什么任务适合/不适合 Dynamic Workflows
- 评价："AI 编程从单次对话走向自动化编排、多智能体协作、长时间执行"

### 2. Steve的AI观察室 — "Claude 新功能炸了：Dynamic Workflow"
- 观点："把 Agent 编排逻辑搬进代码里，比 Opus 4.8 本身还重要"

### 3. 搞哥爱分享 — "Claude Code 又升级了" (v2.1.154+v2.1.156)
- 多 Agent 工作流：一条指令自动拆成前端/后端/测试/文档，几十个 Agent 后台跑
- `/workflows` 命令查看进度
- Fast 模式费率从 5x 砍到 2x

### 4. Addy张无为 — "ClaudeCode技能第5集：防AI摸鱼技能"
- 推荐 Skills——PUA
- **下集预告：**「安全设置：提升CC持续自动工作」— 值得关注

### 5. 其他相关帖子
- "Claude Code Dynamic Workflow + Opus4.8" (VibeCoder)
- "Claude Code这个新功能太狠了！" (一页繁华)
- "Claude Code 更新了！修bug" (用人摸AI的鱼)

## 社区评价

- 普遍认为是 "重要方向" 而非简单更新
- 中文技术社区称其为从"单次对话"到"自动化编排、多智能体协作、长时间执行"的转变
- 搜索量和讨论热度较高（多个独立创作者都在讲这个功能）
- 操作方式统一：`/workflows` 命令

## 与 Hermes + Claude Code 协作的关系

Dynamic Workflows 是 Claude Code 自身的多 Agent 编排能力，与 Hermes 的规划协调角色有重叠但不同：

| 维度 | Hermes 编排 | Claude Code Dynamic Workflows |
|------|-------------|-------------------------------|
| 适用范围 | 跨会话、跨工具 | 单次 Claude Code 会话内 |
| 协调范围 | Hermes + Claude Code + 其他工具 | Claude Code 内部子 Agent |
| 执行方式 | Hermes 逐个派发任务 | Claude Code 自动生成工作流脚本 |
| 适用场景 | 需要 Hermes 搜索/分析/记忆的任务 | 纯编码任务的多 Agent 并行 |

两者可以互补：Hermes 做高层分解，Complex 子任务交给 Claude Code Dynamic Workflows 内部编排。
