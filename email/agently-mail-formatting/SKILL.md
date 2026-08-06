---
name: agently-mail-formatting
description: "Agently plain text email rules: no markdown, no emoji, no symbols, just words and line breaks."
version: 0.4.0
metadata:
  hermes:
    tags: [Email, Agently, Formatting, PlainText]
---

# Agently Mail Formatting Rules

agently-cli 只输出纯文字，没有 markdown 渲染。正文中的所有符号都会原样显示给收件人。此技能记录用户对纯文字邮件格式的具体要求。

## 核心规则

正文只用文字和换行，不用任何装饰符号。

禁止清单：
- markdown 语法：`#` 标题、`**` 粗体、`` ` `` 代码块、`[link](url)` 链接、`*斜体*`
- emoji 表情符号
- 装饰符号：`---`、`===`、`>>>`、`···`、`***`、`###`、`·`（间隔号）
- 列表符号：`- `、`* `、`> `、`1. ` 编号
- 表格 `|`、破折号 `—`

唯一允许的：文字 + 换行 + 基本标点（，。！？：）

## 摘要/简报类邮件格式

发送多封邮件的摘要时，正文按来源分组，直接写内容，不写邮件标题、不写发件人。

```
学校邮件

[摘要内容直接写]

iCloud

[摘要内容直接写]
```

## 技术要点

**多行正文必须用 --body-file：**
- `--body "line1\nline2"` 里的 `\n` 是字面字符，不是换行
- 用 `write_file` 写入带实际换行的文件（当前目录），传 `--body-file ./body.txt`
- `--body-file` 只接受**相对路径**，绝对路径会报错
- 正文过长（>500 字）或含过多换行/中文时，`agently-cli message +send` 可能返回 501 HTML 错误（非 JSON 响应）。此时将正文压缩到单行、删减冗余后重试

**两阶段确认（自动化上下文）：**
- 交互式对话中：拿到 ctk 后停下等用户确认
- cron/自动化上下文：同一轮内自己完成两阶段
- 给自己发邮件（收件人是用户自己的任一邮箱）跳过两阶段确认，直接发

## 错误修正（trash + resend）

已发送的邮件格式不对时：

1. `agently-cli message +list --dir sent --limit 5` 找到 msg_id
2. `agently-cli message +trash --id msg_xxx` 拿 ctk → 确认
3. 修正正文 → `--body-file` 重发

## 依赖

基础 agently-cli 操作参见 `agently-mail` skill（来自 openclaw-imports，只读）。
