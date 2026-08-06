---
name: resumes-git-workflow
description: "resumes 仓库 Git 工作流强制规则：每次 .tex 文件修改后立即逐条 commit+push。自动加载 AGENTS.md 约束。"
version: 1.0.0
metadata:
  hermes:
    trigger_path: /Users/minimx/Documents/resumes
---

# Resumes Git Workflow — 强制规则

**适用仓库:** `mrtsels/resumes`（路径: `/Users/minimx/Documents/resumes`）

> 每次 .tex 文件操作（创建、编辑一行、改名、删除）后，**必须**立即 `git add + git commit + git push`，不得累积多个无关改动。

## 触发条件

当工作路径在 `/Users/minimx/Documents/resumes` 下时，此规则自动生效。

## 流程

1. 修改 .tex 文件后，**先编译 PDF**（`xelatex -interaction=nonstopmode resume.tex` × 2 次）
2. 编译成功后，**立即** `git add -A`
3. `git commit -m "<type>: <简短英文描述>"`
   - type: `feat` / `fix` / `docs` / `chore` / `reorg`
   - subject ≤ 72 字
4. `git push origin main`
5. 展示 PDF 给用户预览

## 不允许的行为

- ❌ 连续修改多个文件后一次性 commit
- ❌ 修改后不 commit 就切换到其他任务
- ❌ commit 后不 push（除非网络故障且已确认）
- ❌ 省略 PDF 编译直接 commit

## 验证

`git status` 确认 working tree clean 后，任务才算完成。
