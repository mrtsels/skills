# Multi-Batch Parallel Delegate Pattern

适用于 5+ 个完全独立的子任务（无文件冲突、无时序依赖）。因 delegate_task 最大并发为 3，需分批调度。

## 工作流

```
1. 拆分任务为 N 个独立原子任务（每个涉及不同文件）
2. 创建 N 个 worktree + 分支 + 推送到远端
3. 第一批：delegate_task(tasks=[task1, task2, task3])  → 等完成
4. 第二批：delegate_task(tasks=[task4, task5, ...])    → 等完成
5. 依次 merge 所有 PR
6. 清理 worktree + 推送主分支到双远端
```

## Worktree 设置

```bash
# 每个任务一个独立分支 + worktree
for name in task-a task-b task-c task-d task-e; do
  branch="deploy/$name"
  git checkout -b "$branch" main
  git push origin "$branch"
  git checkout main
  wt="/tmp/wt-$name"
  git worktree add "$wt" "$branch"
done
```

⚠️ **重要：** 创建 worktree 前必须 `git checkout main`，否则 worktree add 会报 "fatal: already used by worktree at <CWD>"。

## delegate_task Prompt 要点

| 字段 | 要求 |
|------|------|
| `context` | 包含绝对 worktree 路径 (`/tmp/wt-xxx/`)、分支名、目标文件、验证命令 |
| `goal` | 一句话说明任务 |
| `toolsets` | 纯文件任务用 `["terminal", "file"]`，需要网络用 `["terminal", "file", "web"]` |

每个 prompt 必须**完全自包含**——子代理没有任何会话记忆。

## PR 合并 & 清理

```bash
# 合并所有 PR
for pr in 7 8 9 10 11; do
  gh pr merge "$pr" --squash --delete-branch
done

# 清理 worktree（必须先 remove，再删本地分支）
git worktree remove /tmp/wt-task-a
git branch -d deploy/task-a

# 推送主分支到双远端（GitHub + 内网）
git push origin main
git push <internal-remote> main
```

## 适用条件

- ✅ 任务修改完全不同的文件（无 merge 冲突）
- ✅ 每个任务是机械式创建/修改（新建文件、改配置、写文档）
- ❌ 不能用于同一文件的不同区域修改（产生冲突）
- ❌ 不能用于有时序依赖的任务

## 实际案例

Enterprise MVP 部署项目：5 个独立任务并行（backup.sh, backup.md, logback.xml, nginx.conf, docker-compose.yml），5 个 worktree + 2 批 delegate_task，总耗时 ≈ 最慢任务（~59s）。所有 PR 合并后无冲突。
