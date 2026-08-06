# HTML/JS 单文件项目调试指南

适用于 5000+ 行单文件 `index.html`（所有 JS/CSS/HTML 混在一起）的调试场景。

## 核心原则：先行号，后编辑

单文件大项目中，LLM Edit tool 的模糊匹配极不可靠（tab vs 空格、缩进层级变化）。**绝对不能**让 Claude Code 去 "find the function"。

### 调试流程

1. **用 grep 定位精确行号**
   ```bash
   grep -n "function\|target_text\|关键代码" index.html
   ```
   输出格式：`行号: 代码内容`

2. **用 sed 查看上下文**
   ```bash
   sed -n 'START_LINE,+20p' index.html
   ```
   看目标函数前后 20 行，确认修改边界。

3. **检查缩进格式**
   ```bash
   sed -n 'LINE_NUMBER,+1p' index.html | cat -A
   # ^I = tab, 空白 = 空格
   ```

4. **用精确的 sed 替换（比 Edit 工具可靠）**
   ```bash
   # 替换整行
   sed -i '' 'LINE_NUMBER c\替换后的内容' index.html
   
   # 对某行做局部替换
   sed -i '' 'LINE_NUMBER s/旧字符串/新字符串/' index.html
   ```

5. **语法验证**
   ```bash
   # JS 语法检查（最关键的一步）
   node --check index.html
   ```

6. **修改后的完整性检查**
   ```bash
   python3 -c "
   with open('index.html') as f:
       c = f.read()
   print('style:', c.count('<style'), '</style>:', c.count('</style>'))
   print('head:', '</head>' in c, 'body:', '<body' in c)
   import re
   d = len(re.findall(r'<div[\s>]', c))
   dc = len(re.findall(r'</div>', c))
   print('div:', d, '/div:', dc, 'diff:', d - dc)
   "
   ```

## Edit Tool 适配注意事项

当使用 LLM 的 Edit 工具（find-and-replace）修改大文件时：

- **tab 缩进问题是头号杀手** — 先用 `cat -A` 确认真实缩进字符
- **越短的 old_string 越容易唯一匹配** — 取函数签名 + 前 1-2 行足够，不用全文
- **改完后必做 node --check** — 这是最快发现 Edit 截断问题的办法
- **每次改完一个点就验证**，不要攒一批再验证

## 常见陷阱

| 陷阱 | 表现 | 修复 |
|------|------|------|
| Edit 匹配到错误位置 | 改了 A 函数却改了 B | 缩小 old_string 范围，加行号锚点 |
| tab 换成空格后缩进不对 | JS 语法错误（缩进坏习惯不会导致 JS 报错，但拼接后格式会乱） | 保持原始 tab 数量 |
| Edit 替换跨了函数边界 | 删了函数体末尾或 return | 验证 `}` 数量、`return ` 存在 |
| 写了代码但忘记调函数 | 按钮点击无响应 | 检查事件绑定 `onclick="fn"` 是否存在 |
