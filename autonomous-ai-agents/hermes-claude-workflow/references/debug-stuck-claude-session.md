# 诊断卡住的 Claude Code Session

当 Claude Code 会话看起来"卡住"时——进程存活但无响应、输出不动、等了很久没结果——可以用以下流程诊断根因。

## 1. 定位目标进程

```bash
ps aux | grep claude | grep -v grep
```

输出类似：
```
minimx  57807  0.9  1.8  562425472 452432 s005  S+   9:47AM  9:40.69 claude --dangerously-skip-permissions
```

关注点：
- **PID**（57807）——后续所有操作需要
- **TTY**（s005）——终端会话号，告诉你在哪个终端
- **CPU**——如果 0.x% 持续很久，大概率在等外部事件
- `S+` 表示前台进程组，`S` 表示可中断睡眠

## 2. 读 session 状态文件

```bash
cat ~/.claude/sessions/<PID>.json
```

关键字段：

| 字段 | 含义 | 异常值 |
|------|------|--------|
| `status` | 当前状态 | `"waiting"` = 卡住 |
| `waitingFor` | 等待原因 | `"dialog open"` = 有交互对话框 |
| `name` | session 名称（如果有） | 帮助理解上下文 |
| `updatedAt` | 最后更新时间 | 太旧 = 真卡住 |
| `cwd` | 工作目录 | 知道它在哪个项目下运行 |

示例（卡住状态）：
```json
{
  "pid": 57807,
  "sessionId": "98cff4a0-...",
  "cwd": "/Users/minimx/enterprise",
  "status": "waiting",
  "waitingFor": "dialog open",
  "name": "apple-container-docker-build"
}
```

## 3. 读任务清单（如果有）

Claude Code 的任务文件在：

```bash
ls -la ~/.claude/tasks/<sessionId>/
```

每个 `.json` 文件是一个子任务：

```json
{
  "id": "12",
  "subject": "Build and export Docker images",
  "description": "Rebuild backend jar ...",
  "status": "in_progress",
  "blocks": [],
  "blockedBy": []
}
```

通过多个任务的状态（哪个是 `in_progress`，哪些是 `completed`）可以推断当前进度。

## 4. 读对话历史（JSONL）

Claude Code 对话记录在项目目录下：

```bash
less ~/.claude/projects/<project-dir>/<sessionId>.jsonl
```

每条记录包含 `role`、`content` 和 `createdAt`。

重点寻找：
- 最近一条 Claude 的**带实际文本的回复**——它最后说了什么
- 工具调用失败记录（如 `docker pull` failed）
- 请求用户交互的消息（如 "需要你确认"、"需要一个决定"）

使用 Python 快速提取关键消息：

```python
import json
with open('/path/to/session.jsonl') as f:
    for i, line in enumerate(f):
        try:
            entry = json.loads(line)
            role = entry.get('role', '?')
            content = str(entry.get('content', ''))
            ts = entry.get('createdAt', '')
            if len(content) > 100:
                content = content[:100] + '...'
            if content.strip():
                print(f'[{i}] {role} [{ts}]: {content}')
        except:
            pass
```

## 5. 综合判断

| 状况 | 判断 | 推荐操作 |
|------|------|----------|
| `status: waiting`, `waitingFor: dialog open` | 有终端对话框等用户确认 | 切到对应 TTY 回答对话框，或告诉用户去处理 |
| `status: idle`, 最近无 `updatedAt` 更新 | 正常空闲，等输入 | 用户需要主动输入 |
| 对话最后一条是工具调用的重试循环 | 工具报错后 Claude 在盲目重试 | 杀掉 session，修正参数后重新开始 |
| 对话最后一条是 "需要你确认" | 卡在用户决策点 | 直接告诉用户需要决策什么 |
| 对话记录为空（全部空 content） | JSONL 可能未完整保存 | 直接用 `strace`/`lsof` 看进程在等什么 |
| 进程已不存在但 session 文件残留 | session 已被关闭 | 忽略 |

## 6. 处理方案

### 如果卡在对话框
```bash
# 切到对应终端回答
# 或者直接 kill 掉：
kill <PID>
# 然后修正 prompt 重新启动
```

### 如果部分工作已做完
检查文件系统确认已完成的工作（如多次 session rename 后生成的 tar.gz），然后决定是继续还是重新开始。

### 如果 session 已无价值
```bash
kill <PID>
# 清理 session 文件（可选）
rm ~/.claude/sessions/<PID>.json
```

## 相关文件路径速查

| 路径 | 内容 |
|------|------|
| `~/.claude/sessions/<PID>.json` | 该会话的元数据（状态、等待原因、名称） |
| `~/.claude/tasks/<sessionId>/` | 子任务清单（如果有任务系统） |
| `~/.claude/projects/<project-dir>/<sessionId>.jsonl` | 完整对话记录 |
| `~/.claude/history.jsonl` | 所有 session 的聚合历史（可能包含同步的工具调用记录） |
| `/dev/tty<编号>` | process 所在的终端设备文件 |
