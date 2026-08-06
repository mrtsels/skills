# 修改建议逐条确认 → 批量执行工作流

## 场景

用户有一份外部文档（.docx/.md/截图）列出了若干修改建议/缺陷修复。需要逐条和用户确认理解无误，再批量下发给代码开发。

## 工作流

```
用户: "看这个文件，提取文字，你会发现很多这这那那，逐一跟我确认"
     ↓
Hermes: read_file(文件) 提取文字内容
     ↓
Hermes: 逐条解析，每条写成 一句话理解 + 两个选择
     ↓
for each item:
  clarify(question="确认理解..." choises=["是，...", "不是，我解释一下"])
     ↓ 用户逐条回应
  记录每条的最终决定（确认/忽略/修正）
     ↓
Hermes: 将确认的改动分组 → 建分支+worktree → 并行派发
```

## Prompt 构造原则

每条 confirm 后就地合并进 prompt，不等到最后再回溯：

## 关键经验

1. **一行一选项** — clarify 的 choices 只放两个：确认理解 / 需要解释。用户偏好简洁，不要放多个选项
2. **用户拒绝/忽略的条目直接丢弃** — 不需要在 prompt 中保留
3. **做文档提取时直接用 read_file** — .docx 文件无需额外工具，read_file 自动提取文字
4. **不开发票** — 用户要的是「逐一确认每一条改不改」，不是「听你分析」。确认就记，不确认就跳过，不分析报告
5. **这个确认流程本身不修改文件** — 所有修改由 Claude Code 一次性完成

## 触发词

用户说「看这个/读这个文件」「你会发现很多这这那那」「逐一跟我确认」时，启动此流程。

## 确认后的批量执行（二阶段模式）

确认完改动清单后，不使用一次性 Claude Code prompt，而是拆成**独立改动组 + 并行 worktree 分支**：

### 分组原则

1. 每个逻辑独立的改动分为一组（如文本替换、标题逻辑、侧拉窗行为、功能删除）
2. 同文件的改动如果修改区域不同（不同函数、不同 HTML 片段），可做独立分组
3. 后端/数据类改动与前端改动完全分开
4. 每组的最大改动量：不超 5 项原子改动

### 执行流程

```
Hermes: 分组 → 每组建独立分支 + worktree
     ↓ 批量并行
subagent 1: wt-text 分支 → Claude Code → commit + push
subagent 2: wt-title 分支 → Claude Code → commit + push
subagent 3: wt-sidebar 分支 → Claude Code → commit + push
subagent 4: wt-assoc 分支 → Claude Code → commit + push
subagent 5: wt-policy 分支 → Claude Code → commit + push
     ↓
Hermes: 逐个 squash merge → node --check 验证 → 清理 worktree
```

### 具体操作

**Hermes 侧（建分支+worktree）：**
```bash
cd ~/enterprise
git fetch origin
for br in feat/fix-text feat/fix-title feat/fix-sidebar; do
  git push origin main:refs/heads/$br
  git worktree add /tmp/wt-$br $br
done
```

**通过 delegate_task 派发（每条独立任务）：**
```python
delegate_task(
    tasks=[
        {
            "goal": "全局文本替换：「检视」→「查看详情」（政府端+协会端）",
            "context": """项目 /Users/minimx/enterprise
worktree /tmp/wt-video-fix-text，分支 feat/video-fix-text
index.html tab缩进，5000+ 行。node --check 验证。""",
            "toolsets": ["terminal", "file"]
        },
        {
            "goal": "申报页标题动态逻辑：编辑模式→编辑申报，审核模式→审核报告",
            "context": """...""",
            "toolsets": ["terminal", "file"]
        },
    ]
)
```

⚠️ **同文件禁区**：如果多个分组改同一个文件（如 index.html）的不同区域，各分支独立修改后合并不会冲突（只要修改的是不同行范围）。但如果有重叠行，必须串行执行。

### HTML 大文件精确修改策略（针对 5000+ 行 SPA）

当 patch() 反复因 tab/空格/引号不匹配失败时，采用**逐级降级策略**：

```
patch() → ✅ 最佳路径，一次成功
  ↓ 失败（3 次以上）→ git checkout 恢复后再试
execute_code + Python .replace() (精确字符串字面量)
  ↓ 注意避开 `\n` 字面量陷阱
execute_code + 文件字节级替换（find+slice, 读取确定区域再截取）
```

#### patch() 的 `\n` 字面量陷阱

**⚠️ 关键发现**：patch() 在某些情况下会**在文件中插入字面量 `\n`（反斜杠+n）** 而非真实换行符。症状：`node --check` 报 `Invalid or unexpected token`，`cat -v` 显示 `\\n`。

**原因**：patch 的 new_string 中包含 `\n` 时，如果两端引号/换行上下文导致转义层数错位，系统可能写出反斜杠+n 字符序列而非真正的换行。

**发现后的修复方法：**
```python
# ❌ 错误的做法（Python 看到 \n 当作换行运行，但文件中的 bytes 是 \\n）
content.replace('\\n', '\n')  # 会把 JS 字符串中的转义 \n 也替换了！

# ✅ 正确的修复：使用二进制模式 + 只替换文件中的字面量 \\n
with open('FILE.html', 'rb') as f:
    content = f.read()
content = content.replace(b'\\\\n', b'\n')  # bytes 级替换，只替换反斜杠+n
with open('FILE.html', 'wb') as f:
    f.write(content)
```

**预防：** 每次 patch 后立即 `cat -v FILE | grep '\\\\n'` 检查是否有字面量 `\n`。如有，用 bytes 级替换修复后重新 node --check。

#### 移除字符串拼接中一行的陷阱

当移除 HTML 模板字符串中**一行代码（如按钮）且该行末尾有 `'+` 拼接符**时，需要同时处理前一行：**将前一行末尾的 `'+'` 改为 `';'`。**

```javascript
// 原始代码：
'<span>报名: '+st+'</span></div></div>'+
'<button ...>取消报名</button></div>';

// 移除按钮后需要改成一：
'<span>报名: '+st+'</span></div></div>';
// 注意：末尾从 + 变成了 ;，否则这行末尾的 + 后续没有东西可拼接，造成 ';' 语法错误
```

**发现手段**：`node --check` 会在 `;` 处报 `SyntaxError: Unexpected token ';'`。`grep -n '^;' FILE` 快速定位孤立分号。

#### Python 字符串中的引号层数陷阱

当文件内容有 JavaScript 表达式嵌套（如 `"cancelMyReg('+actId+','+reg.id+')"`），Python 代码中写相同字符串时容易**引号层数不对导致匹配失败**：

```python
# 文件中的实际内容：
# onclick="cancelMyReg('+actId+','+reg.id+')"

# Python 字符串中正确写法（注意 " 在文件中是放在 HTML 属性里的）：
old = 'onclick="cancelMyReg(\'+actId+\',\'+reg.id+\')">取消报名</button>'
# 检查：用 html.find(old) 确认能找到再执行 replace
```

**经验法则**：不要凭记忆写 old_string。先用 `read_file` 读取精确行，然后**直接复制粘贴该行到 Python 脚本**，用 \` 或 raw string 包裹。

#### 干净的重试策略

当 patch() 反复失败（3 次以上），不要逐层叠加修复：
1. **`git checkout -- FILE` 恢复干净状态**
2. 改用 `execute_code` + 精确 `.replace()`
3. 每改完一条立即 `node --check`
4. 确认无新错误后再改下一条

**绝对不要**在已损坏的文件上继续 patch——会导致第 3 条 patch 在修复第 1 条遗留问题的残缺状态上操作，连锁失效。

### 验证要求

每个改动组必须单独验证：
1. 对 HTML/JS 文件：`node --check` 提取所有 `<script>` 块检查语法
2. `git diff --stat` 确认改动了预期文件数
3. 合并到 main 后全量语法检查

### 此模式 vs 单次 Claude Code prompt

| 维度 | 单次 prompt | 分组并行 |
|------|------------|----------|
| 总耗时 | 串行 ≈ 各任务之和 | 并行 ≈ 最慢任务 |
| 独立回滚 | ❌ 一个 PR 全部打包 | ✅ 每个改动独立分支/PR |
| 冲突风险 | 低（单次顺序执行） | 中（同文件可能冲突） |
| 代码审查 | 一大块改动 | 每项独立 review |

### 调试大型 SPA 的要点

当改动涉及 5000+ 行的单文件 HTML SPA（如 index.html）时：

- **永远不要先写 Python 字符串替换再验证**——patch 工具更可靠，不会引入 `\n` 字面量等陷阱
- 如果 patch 失败，`git checkout -- FILE` 恢复后**单条重试**，不要批量 patch
- 每次 patch 后提取 `<script>` 块做 node --check
- 优先级：`patch()` > 精确字符串替换 > ❌ 行号索引 split/join
- 文件使用 tab 缩进，old_string 中的 tab 必须与文件完全一致
