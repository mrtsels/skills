---
name: docx-edit-rules
description: "yuecai 项目 python-docx 编辑铁律：只改 run.text，不动段落/runs/格式结构。合并单元格的 text extraction 与实际坐标不同。替换图片前先确认内容。估值表数据提取方法。"
version: 0.6.0
author: Hermes
metadata:
  hermes:
    tags: [docx, python-docx, yuecai, office]
---

# Docx 编辑铁律（yuecai 项目适用）

> 用户对此类问题极其敏感，违反会直接挨骂。**严格遵守。**

---

## 规则一：只改 run.text，不动任何结构

- `python-docx` 中，只允许修改 `run.text` 属性
- **禁止**：`p.clear()`、`cell.paragraphs[0].clear()`、`while len(cell.paragraphs) > 1: remove`
- **禁止**：增删段落、合并段落、修改段落顺序 —— 除非模板明确预留了插入位置
- **禁止**：`cell.add_paragraph()` 或 `p.add_run()`（除非文档本来就是空的要新建）
- **验证方法**：编辑前后对比 `len(cell.paragraphs)` 和每段的 `len(p.runs)`，必须一致

### 错误做法
```python
for p in cell.paragraphs:
    p.clear()
cell.paragraphs[0].add_run(new_text)
```

### 正确做法
```python
for p in cell.paragraphs:
    for run in p.runs:
        if "旧文字" in run.text:
            run.text = run.text.replace("旧文字", "新文字")
```

---

## 规则二：跨多个 run 的文本也要精准定位

```python
full = ""
for run in p.runs:
    full += run.text

if "2026年3月31日" in full:
    for run in p.runs:
        if "3月31日" in run.text:
            run.text = run.text.replace("3月31日", "6月30日")
```

### 处理 "一→二" 跨 run 替换
```python
for i in range(len(runs) - 1):
    if runs[i].text == '一' and '季度' in runs[i+1].text[:4]:
        runs[i].text = '二'
```

---

## 规则三：替换截图（docx 内嵌图片）

### 致命陷阱：替换前不确认图片内容

**2026-07-23 教训**：航长 docx 中有 image1.png（282KB）和 image2.png（117KB）。用户提供的新截图是 image2 的内容，但直接替换了 image1。

### 正确流程

1. 列出 media 文件并提取：
   ```python
   import zipfile
   with zipfile.ZipFile('doc.docx', 'r') as zf:
       for name in zf.namelist():
           if 'media' in name:
               with open(f'/tmp/{name.replace("/", "_")}', 'wb') as f:
                   f.write(zf.read(name))
   ```

2. 用 `vision_analyze` 确认每张图的内容再写替换代码，不要靠文件大小猜。

3. 确认对应关系后，用 zipfile 直接替换：
   ```python
   import zipfile, shutil
   with zipfile.ZipFile('doc.docx', 'r') as zin:
       data = {name: zin.read(name) for name in zin.namelist()}
   data['word/media/image2.png'] = new_img_bytes
   with zipfile.ZipFile('doc.docx.tmp', 'w', zipfile.ZIP_DEFLATED) as zout:
       for name, content in data.items():
           zout.writestr(name, content)
   shutil.move('doc.docx.tmp', 'doc.docx')
   ```

---

## 规则四：多段落 Cell——追加不离段

多段落 cell（如 R14 有 18-23 段）不能合并或删除段落结构。

```python
# 替换 P0 全部内容
cell.paragraphs[0].runs[0].text = new_full_text

# 清空其他段
for pi in range(1, len(cell.paragraphs)):
    for run in cell.paragraphs[pi].runs:
        run.text = ""
```

**追加内容不离段**：续在最后一个 run，不写进新段落。

```python
# ❌ 错误：写入新段落 P11
cell.paragraphs[11].runs[0].text = holdings_list

# ✅ 正确：续在 P10 最后一个 run
p10 = cell.paragraphs[10]
p10.runs[-1].text = p10.runs[-1].text + "\n" + holdings_list
```

---

## 规则五：追加新段落（仅当模板预留了插入位置）

> 2026-07-23 实战：德汇 1-3a 的 市场概况 节有 Q1 内容，需在其后插入 Q2 内容。模板在 Q1 末尾和 持仓方面 之间有一个空行段落，明确预留了插入位置。

### 何时可以加段落

- 模板在两个内容块之间有**空行段落**，且空行之后是独立节
- **不允许**：在已有内容的段落中间插入

### OxmlElement 插入法

创建全新的 `w:p` 元素，不克隆已有段落（防止文本污染）：

```python
from docx.oxml.ns import qn
from docx.oxml import OxmlElement

def make_para(text):
    """Create clean w:p with one w:r containing text."""
    p = OxmlElement('w:p')
    r = OxmlElement('w:r')
    t = OxmlElement('w:t')
    t.set(qn('xml:space'), 'preserve')
    t.text = text
    r.append(t)
    p.append(r)
    return p

# Find anchor paragraph, then insert before next element
target_elem = cell.paragraphs[target_idx]._element
parent = target_elem.getparent()
next_elem = target_elem.getnext()  # empty paragraph

for text in new_lines:
    new_p = make_para(text)
    parent.insert(parent.index(next_elem), new_p)
```

### 规则五 vs 规则四

| 场景 | 手法 | 依据 |
|------|------|------|
| Q1 末尾有空白段落，后面是独立节 | `make_para()` 种新段落 | 模板预留了插入位置 |
| 在同一节内追加内容 | 续在最后一个 run | 不能改变段落结构 |

不确定时，选续在最后一个 run（规则四），更安全。

---

## 规则六：单元格全文本替换（航长 R15 模式）

```python
cell.paragraphs[0].runs[0].text = new_full_text
for pi in range(1, len(cell.paragraphs)):
    for run in cell.paragraphs[pi].runs:
        run.text = ""
```

---

## 规则七：同表不同行的结构差异性

不同产品的 docx 模板结构可能不同。先检查再操作：

```python
p10 = cell.paragraphs[10]
if len(p10.runs) == 0:
    p10.add_run(new_text)
elif all(r.text == "" for r in p10.runs):
    p10.runs[0].text = new_text
else:
    for run in p10.runs:
        if "旧关键词" in run.text:
            run.text = new_text; break
```

---

## 规则八：估值表单位净值精度

永远从估值表取完整精度，不 truncate。定位 `R13C3`，不误写其他含小数点的单元格。

```python
raw = txt.split("：")[1].strip()  # "1.061811" 保持原样
```

---

## 规则九：跨 run 匹配进阶

```python
# 相邻 run 组合检测
for i in range(len(runs) - 1):
    if runs[i].text == "一" and "季度" in runs[i+1].text[:4]:
        runs[i].text = "二"

# 数值符号跨 run 修改
# runs: ['-', '3.', '35', '%'] → ['-', '2.', '40', '%']
for r in cell.paragraphs[0].runs:
    if r.text == '3.': r.text = '2.'
    elif r.text == '35': r.text = '40'
```

**口诀**：先用 `print` 看拆分结构 → 逐个 run 替换。

---

## 规则十：检查时间可能在文档段落里，也可能在表格 cell 里

**1-3a 投后管理报告**：检查时间在文档正文段落（通常是 P5），每段含 4-5 个 runs。

**附件 2 存续期管理要求落实情况表**：检查时间在 **表格 R1C0 / R1C1**（合并单元格，两列内容相同）。日期字符串极可能**逐字符拆分**：

```
# 附件2 常见 run 结构：'2','0','2','6','年','6','月','2','6','日'
# 每个字符/数字是一个独立 run
# 要改 26日→30日：找到月字符后的 '2' 和 '6' 两个 runs
```

```python
runs = p.runs
for ri, r in enumerate(runs):
    if r.text == '2' and ri >= 3:
        if ri + 1 < len(runs) and runs[ri+1].text == '6':
            if ri + 2 < len(runs) and runs[ri+2].text == '日':
                r.text = '3'
                runs[ri+1].text = '0'
                break
```

**调试方法**（统一适用于段落和表格 cell）：

```python
for pi, p in enumerate(target.paragraphs):
    for ri, r in enumerate(p.runs):
        if ri == 0 or r.text.strip():
            print(f"  P{pi} run[{ri}]: {repr(r.text)}")
```

---

## 规则十一：百分比数字跨 run 拆分

`"仓位占比约73%"` 拆为 `'7'` + `'3%'`。用前文 run 确认目标：

```python
for i, r in enumerate(runs):
    if r.text == '7' and i > 0 and runs[i-1].text == '占比约':
        r.text = '6'
```

---

## 规则十二：中文引号/特殊字符的 Python 执行

含 `\u201c` `\u201d` 的 Python 代码不能在 `terminal()` heredoc 中执行。必须写成 `.py` 文件：

```python
# ❌ 错误
result = terminal("""python3 << 'PYEOF'\nrun.text = run.text.replace("a", "...策略...")\nPYEOF""")

# ✅ 正确
write_file("scripts/update.py", '''\
run.text = run.text.replace("a", "...策略...")
''')
terminal("python3 scripts/update.py")
```

---

## 规则十三：合并单元格陷阱——text extraction ≠ 实际表格坐标

### 核心陷阱

`read_file` 对 docx 的提取按**单元格 XML 顺序**输出，**不是视觉布局**。合并单元格（`gridSpan` / `vMerge`）使得一个单元格占据多列，但 python-docx 只把它作为一个。

```python
# read_file 输出：
# 56|总经理
# 57|莫敏秋（法定代表人）
#
# 实际表格：R20 只有一行，但含 3 个合并区
# C0-C1 (span=2): 纵向合并自上行 → text="主要管理人信息"
# C2-C4 (span=3): "总经理"
# C5-C6 (span=2): "莫敏秋"（数据值）
```

text extraction 把同一 row 的多个合并区拆为多行输出。不要根据 text extraction 的行号推断 cell 位置。

### 标准操作流程

**第一步：dump 完整结构**

```python
from docx.oxml.ns import qn

for ri, row in enumerate(table.rows):
    for ci, cell in enumerate(row.cells):
        tc = cell._tc
        tcPr = tc.find(qn('w:tcPr'))
        gs = tcPr.find(qn('w:gridSpan')) if tcPr is not None else None
        vm = tcPr.find(qn('w:vMerge')) if tcPr is not None else None
        if gs is not None or vm is not None or cell.text.strip():
            s = f"s{gs.get(qn('w:val'))}" if gs is not None else ""
            v = f"v" if vm is not None else ""
            print(f"R{ri:02d}C{ci} [{s}{v}]: {cell.text.strip()[:40]}")
```

**第二步：确认目标单元格不是纵向从属**

`vMerge`（无 val 或 `val="continue"`）表示该格是纵向合并的从属格——它的视觉内容来自上方主格。不要写入这类单元格；找到合并组的第一个单元格（行号最小者）。

**第三步：写数据用行列坐标，不用文本查找**

```python
# ❌ 错误：按文本搜索 → 匹配到 vMerge 的从属格
text_map = {}
for ri, row in enumerate(table.rows):
    for ci, cell in enumerate(row.cells):
        text_map[cell.text.strip()] = ri, ci
ri, ci = text_map.get("姓名", (0, 0))

# ✅ 正确：从 dump 确认坐标后直接写
table.rows[20].cells[5].paragraphs[0].text = "莫敏秋（法定代表人）"
```

### 典型合并模式

```
# 管理人信息区：C0-C1 纵向合并，C2-C4 为行标签
R19: C0[s2]="主要管理人信息"   C2[s3]="职务"  C5[s2]="姓名"  C7="联系方式"
R20: C0       (vMerge)         C2[s3]="总经理" C5[s2] (vMerge) C7 (vMerge)
R21: C0       (vMerge)         C2[s3]="投资经理"
R22: C0       (vMerge)         C2[s3]="风控/合规主管"
```

R20 C5 的 `cell.text` 读到的是"姓名"（来自 R19 vMerge 主格），但该格是数据输入位。写入即可，不破坏 R19 表头。

### 多表识别

一个 docx 可能含多个独立表格：
```python
print(f"Tables: {len(doc.tables)}")
for ti, t in enumerate(doc.tables):
    print(f"  T{ti}: {len(t.rows)}r × {len(t.columns)}c")
```

主表（T0）+ 存续产品表（T1）+ 策略表 + 风控表 + 运营表 + 业绩表。每个表格的合并结构不同，分别 dump。

### 行标签写入 vs 数据列写入

对于简单 label→value 行：
```
R01: C0[s2]="公司法定中文名称："  →  值写入 C2
R02: C0[s2]="公司注册地址："      →  值写入 C2
```
不要写入 C0（合并标签区），写入合并区后的第一个独立列（通常是 C2）。

---

## 规则十四：模板填写前先备份（防 Unicode 文件名）

shutil.copy2 比 shell cp 更安全，支持 Unicode/中文文件名：

```python
from shutil import copy2
from pathlib import Path
src = Path("模板.docx")
bak = src.with_suffix(".bak")
copy2(src, bak)
assert bak.exists(), f"备份失败: {bak}"
```

⚠️ 文件名含中文、特殊空格（U+00A0等）时 shell `cp` 可能静默失败。

---

## 规则十五：行标签即职务——不要写入重复标签

模板的「管理人信息」区（R19-R22），C2 单元格**同时是行标签和职务列**：

```
R20: C2[s3]="总经理"       ← 既是标签又是职务
R21: C2[s3]="投资经理"     ← 同上
R22: C2[s3]="风控/合规主管"
```

**禁止写入 C2 覆盖职务信息**，因为 C2 没有单独的"职务值格"——标签本身就是职务。

```python
# ✅ 正确：只写姓名到 C5
table.rows[21].cells[5].paragraphs[0].text = "王志滨"

# ❌ 错误：覆盖了"投资经理"标签
table.rows[21].cells[2].paragraphs[0].text = "资产管理部负责人兼投资经理"
```

---

## 规则十六：长文本说明格即数值格

很多金融模板把详细的占位说明（如"含当前在运行产品总规模与历史总管理产品规模"）放在**数值格**里。这些格不是标签，直接替换为实际数据：

```python
# 替换占位说明为实际值
t1.rows[2].cells[1].paragraphs[0].text = "8495.35亿元（截至2026年6月30日）"
```

**判断标准：** 如果格内不是简短标签（≤10字），而是详细说明（>15字），那它就是要填的数值格。不要去找相邻的空格。

---

## 规则十七：填错后不要修补，从备份恢复

如果第一轮填写发现大量错位：

1. **立即停止修补** — 每修补一个格可能破坏更多合并格
2. **从 .bak 恢复** — `shutil.copy2(bak, src)`；若无备份则问用户要新模板
3. **重新 dump 结构** — 先看 gridSpan/vMerge
4. **只写数据列** — 不碰标签列（C0/C2）
5. **验证** — 搜索所有行标签（总经理/投资经理/风控/合规主管）是否还在

```python
for label in ["总经理", "投资经理", "风控/合规主管"]:
    found = any(label in cell.text for row in t.rows for cell in row.cells)
    assert found, f"行标签 '{label}' 被覆盖了!"
```

---

## 关联文件

- [`references/yuecai-fof-data-sources.md`](references/yuecai-fof-data-sources.md) — FOF 1-3a 表格结构、火富牛数据提取、增长率计算
- [`references/fof-r14-structure.md`](references/fof-r14-structure.md) — FOF 1-3a R14C3 段落结构和字段映射
- [`references/ycxtcwb-files.md`](references/ycxtcwb-files.md) — 乱码文件名解码、估值表识别

---

## Excel 合同录入模板——只改值不动结构

### 核心原则
和 docx 一样：**只改 cell.value，不动行列/样式/合并单元格。**

### 复选框字符用 Unicode 转义
- `□` = `\u25a1`（未选中）
- `☑` = `\u2611`（已选中）
- 永远不要用汉字「口」

```python
ws['B6'] = "2026年7月23日—2027年8月12日    \u25a1长期"
```

### 字段定位
```python
ws['B3'] = date(2026, 7, 23)
ws['B5'] = "产品全称"
ws['D5'] = "登记编码"
ws['B26'] = date(2026, 7, 23)
```
