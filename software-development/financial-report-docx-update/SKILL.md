---
name: financial-report-docx-update
description: "Update Chinese financial reports (.docx) from valuation table (.xls) data. Covers precise docx editing, date text split across runs, valuation table extraction, and holdings description."
version: 1.0.0
tags: [docx, python-docx, xlrd, financial-report, yuecai, 1-3a]
related_skills: [post-investment-data-maintenance]
---

# Financial Report Docx Update

Update 1-3a / 附件2 reports (docx) from valuation table (xls) data. Covers precise docx cell editing without breaking formatting, valuation table extraction via keyword search, and holdings description generation.

## Pre-Requisites

```bash
pip install python-docx xlrd
```

Both libraries must be available in the project's Python environment.

## Critical Rule: NEVER Clear + Recreate Paragraphs

**The user has explicitly corrected this FOUR TIMES in one session (2026-07-23).** This is the most commonly violated rule. When updating docx cell text:

> *"你改就改不要动别的格式和内容啊 精准替换知道吗"*
> *"不要给我改字体改格式"*
> *"你的框为什么要动我原来的格式？"*
> *"我说的是文本样式 style 你只能替换纯文本内容 不要改整个cell"*

Translation: **Only replace the characters that need changing. Never touch paragraphs, runs, fonts, sizes, spacing, or any other formatting.**

### ❌ WRONG PATTERNS (all destroy formatting — user will complain)

```python
# Pattern 1: clear + add_run (destroys font, size, bold, spacing)
p = cell.paragraphs[0]
p.clear()
p.add_run(new_text)

# Pattern 2: helper function that deepcopies font then recreates
def set_cell_safe(cell, new_text):
    p = cell.paragraphs[0]
    fmt = deepcopy(p.runs[0].font)
    p.clear()
    run = p.add_run(new_text)       # STILL changes paragraph structure

# Pattern 3: clearing entire cell content paragraph-by-paragraph
for p in cell.paragraphs: p.clear()
while len(cell.paragraphs) > 1:
    cell.paragraphs[-1]._element.getparent().remove(...)
target_cell.paragraphs[0].add_run(big_block_of_text)
```

All three destroy original run structure, paragraph spacing, font associations, and character-level formatting. **Do not use any of them on existing content.**

### ✅ RIGHT — only modify existing run text

```python
# Simple string replacement within a run:
for p in cell.paragraphs:
    for run in p.runs:
        if "3月31日" in run.text:
            run.text = run.text.replace("3月31日", "6月30日")

# Replacing an entire paragraph's text (single-run para):
if len(p.runs) == 1:
    p.runs[0].text = new_text

# For multi-run paragraphs: debug first, then target exact runs
for pi, p in enumerate(cell.paragraphs):
    for ri, run in enumerate(p.runs):
        print(f"P{pi} run[{ri}]: {repr(run.text)}")
```

### Common Pitfall: Multi-run Cleanup

When a paragraph has MULTIPLE runs (e.g. P16 of R14: run[0]="\u3000", run[1]=old_content), replacing only run[0] leaves old text in run[1] intact. Always check ALL runs in the paragraph:

```python
# DEBUG: show all runs
for ri, run in enumerate(p.runs):
    print(f"  run[{ri}]: len={len(run.text)}, text='{run.text[:60]}'")

# CLEAR old content from runs that weren't replaced
for run in p.runs:
    if "old keyword" in run.text:
        run.text = ""
```

### Common Pitfall: Period Split Across Runs

"一季度" may be split as run[i]="一" + run[i+1]="季度权益市场E". A simple `"一季度" in run.text` check fails because neither run alone contains the full string. Handle with adjacent-run detection:

```python
for i in range(len(runs) - 1):
    if runs[i].text == "一" and "季度" in runs[i+1].text[:4]:
        runs[i].text = "二"
```

### Common Pitfall: Creating New Paragraphs Instead of Appending

**2026-07-23 教训：** 在 R14C3 "持仓明细如下："段落（P10）后面添加持仓明细列表时，**不要写入新段落 P11**，而是续在 P10 最后一个 run 的文本里：

```python
# ❌ 错误：写入 P11（新段落），用户视为破坏格式
cell.paragraphs[11].runs[0].text = holdings_list

# ✅ 正确：续在 P10 最后一个 run
p10 = cell.paragraphs[10]
p10.runs[-1].text = p10.runs[-1].text + "\n" + holdings_list

# 清空后面的空段落
if len(cell.paragraphs) > 11:
    for r in cell.paragraphs[11].runs:
        r.text = ""
```

**经验法则：** 在段落末尾追加新内容时，永远用 `last_run.text += new_content`，不创建新段落或新 run。

### Common Pitfall: Chinese Quote Characters in Heredoc

**2026-07-23 教训：** 当 Python 代码中的字符串包含中文引号（`\u201c` `\u201d`）时，不能使用 `terminal()` heredoc 方式执行——Python 解析会失败。正确做法：写成 `.py` 文件后用 `terminal("python3 script.py")` 执行，或使用 unicode 转义。

**经验法则：** 含中文引号的 Python 代码一律写成文件再执行。纯英文字符串的 heredoc 无此问题。

### Common Pitfall: Trailing Punctuation in Separate Run

When the old text is "0。" (number + period in one run) but the docx has them as separate runs `"0"` + `"。 "`, and you replace the `"0"` run with text ending in `"。 "`, you get double periods. Check:

```python
# Before replacing, check if period is in same or different run
for i in range(len(runs) - 1):
    if runs[i].text.endswith("。") and runs[i+1].text == "。":
        runs[i+1].text = ""  # clear the duplicate
```

### When CAN you clear + recreate?

Only for **brand-new cells with no existing content to preserve** (writing content into an empty template, or creating a docx from scratch). If the cell has ANY existing formatted text, use `run.text` assignment exclusively.

## Date Text Split Across Runs

Chinese date strings like "2026年3月31日" are commonly split across runs in docx files generated by Chinese Office software. Two common patterns:

### Pattern A — year in 3 parts, day as "31"
```
run[i]: "202", run[i+1]: "6", run[i+2]: "年", run[i+3]: "3", run[i+4]: "月", run[i+5]: "31", run[i+6]: "日"
```
To update: `run[i+3].text = "6"`, `run[i+5].text = "30"` (for →6月30日)

### Pattern B — year in 2 parts, day as "3"+"1"
```
run[i]: "20", run[i+1]: "2", run[i+2]: "6", run[i+3]: "年", run[i+4]: "3", run[i+5]: "月", run[i+6]: "3", run[i+7]: "1", run[i+8]: "日"
```
To update: `run[i+4].text = "6"`, `run[i+6].text = "2"`, `run[i+7].text = "6"` (for →6月26日)

### Detection Strategy

Always debug the run structure first:

```python
for pi, p in enumerate(cell.paragraphs):
    for ri, run in enumerate(p.runs):
        print(f"  run[{ri}]: {repr(run.text)}")
```

Then target the exact runs containing month/day characters.

## Checkbox Updates (☑/□)

Checkboxes are individual characters in separate runs. To toggle:

```python
# Change ☑无 → □无
# ☑ is at run[i], 无 is at run[i+1]
runs[i].text = "□"  

# Change □为本季度新增项目 → ☑为本季度新增项目
runs[i].text = "☑"
```

Always verify the exact run positions by debugging first.

## Valuation Table Data Extraction (xlrd)

Use keyword search across ALL cells — never hardcode row numbers:

```python
import xlrd
wb = xlrd.open_workbook("valuation.xls")
ws = wb.sheet_by_index(0)

# Search all cells for keywords
for r in range(ws.nrows):
    for c in range(ws.ncols):
        val = str(ws.cell(r, c).value).strip()
        if "实收信托" in val:
            ssrj = ws.cell(r, 2).value  # col 2 = quantity/amount
        if "信托资产净值:" in val:
            nav = ws.cell(r, 8).value   # col 8 = market value
```

Standard column layout (恒生电子 valuation tables):
- Col 0: 科目代码 (account code)
- Col 1: 科目名称 (account name)
- Col 2: 数量 (quantity)
- Col 4: 成本 (cost price)
- Col 8: 市值 (market value) ← **preferred for net asset value**
- Col 11: 估值增值 (valuation gain/loss)

### Key field search terms

| Report Field | Search Keyword | Column | Notes |
|-------------|---------------|--------|-------|
| 实收信托金额 | "实收信托" (not "损益平准金") | Col 2 or Col 8 | Both should be identical |
| 信托资产净值 | "信托资产净值:" or "信托资产净额:" | **Col 8** (market value) | NOT col 11 (valuation gain) |
| 单位净值 | "今日单位净值:" or col 11 of row 2 | Col 1 or Col 8 | Header row 2 has "单位净值：X.XXXX in col 11 |
| 累计单位净值 | "累计单位净值:" | Col 1 or Col 8 | |
| 估值日期 | "估值日期" | Adjacent cell | Parse as YYYY年M月D日 |

### Unit Conversion

Valuation table values are in **元** (yuan). Reports may use either:
- **万元** (10,000 yuan): `value / 10000`
- **元** (yuan): keep as-is

The unit is specified in the docx label (e.g. "实收信托金额（万元）" vs "实收信托金额（元）").

## Updating 3-Column Merged Cells

Financial report tables often have 3 data columns that are merged or contain the same value. Update ALL of them:

```python
for ci in range(1, len(row.cells)):
    old = row.cells[ci].text.strip()
    if old == target_old_value:
        row.cells[ci].text = new_value  # BUT use run.text.replace instead!
```

Always prefer `run.text.replace()` within each paragraph's runs rather than directly assigning `cell.text`.

## R14 Holdings Description (权益市场概况及持仓明细)

The R14 cell in 1-3a reports contains the portfolio holdings description. **Base it entirely on actual valuation table data**, not generic market overview text.

### What to include

1. **ETF holdings**: product name, quantity (份), market value (元), sorted by market value descending
2. **Bond holdings**: bond name, exchange type, face value (万元), market value (元), sorted by market value
3. **Leverage ratio**: calculated from 卖出回购证券款 / 信托资产净值

### What NOT to include (unless user provides external data)

- General market overview / industry data (ETF industry size, fund company rankings — user has no source for these and will correct you)
- Speculative descriptions of market trends
- Any number not directly verifiable from the valuation table

**Default to valuation-table-only.** If you need market data (A-share index movements, sector performance, macro events), ask the user for a web-search prompt — do NOT write inferred or plausible-sounding text without real data.

When the user does provide external data via a web-search result, incorporate it precisely: replace only the numbers/dates that need changing, preserving the surrounding text structure.

### Updating R14: NEVER replace the entire cell

The R14 cell has 23+ paragraphs with preserved formatting. **Do not clear paragraphs and rewrite the whole cell.** Instead:

1. Find the specific run containing the old text
2. Replace only that run's text
3. For period refs split across runs ("一" + "季度权益市场E"), search for adjacent-run patterns
4. For paragraphs that need complete text replacement (single-run paragraphs like P3, P5, P7): replace `p.runs[0].text` directly

```python
# Find the R14 cell
for ri, row in enumerate(t.rows):
    for ci, cell in enumerate(row.cells):
        if "市场概况" in cell.text:
            target = cell
            break

# Replace dates in all runs
for p in target.paragraphs:
    for run in p.runs:
        if "2026年3月31日" in run.text:
            run.text = run.text.replace("2026年3月31日", "2026年6月30日")

# Replace holdings description paragraph
for p in target.paragraphs:
    full = "".join(r.text for r in p.runs)
    if "仓位占比" in full:
        runs = p.runs
        for i, run in enumerate(runs):
            if "0" in run.text and len(run.text) <= 3:
                run.text = new_holdings_text
            elif run.text in ["本季度","末","权益","资产","仓位占比为","。"]:
                run.text = ""
        break
```

### Text format

```
权益市场概况及持仓明细：

1、信托计划权益资产配置情况
本季度末权益资产通过ETF配置，合计市值约XXX万元，占信托资产净值约X.X%。具体持仓如下：

ETF持仓明细（按市值排序）：
- XXXETF，持有XXX份，市值XXX元
- ...

2、固收资产配置情况
本产品以城投类私募债为主要配置方向，合计债券市值约XXX万元。主要债券持仓如下：

债券持仓明细：
- XXX（上交所私募债），面值XX万元，市值XXX元
- ...

组合通过债券质押式回购进行杠杆操作，整体杠杆率约XXX%。

其他固收类资产详见附件"持仓明细"及"持仓投后分析"。
```

## Checking Product-Specific Row Numbers

Different products may have different table structures. Always FIND rows by keyword, not by hardcoded row index:

```python
def find_row_by_keyword(table, keyword):
    for ri, row in enumerate(table.rows):
        for ci, cell in enumerate(row.cells):
            if keyword in cell.text:
                return ri, ci
    return None, None
```

Key rows to find in 1-3a:
- "实收信托" → R5 (value in data columns 1-3)
- "当前净值" → R13 (value in col 3)
- "市场概况" → R14 (full content in col 3)
- "增长" → R15/R16 (growth rate in data column)
- "检查时间" → P5 (paragraph)

Key rows in 附件2:
- "项目名称" → R3
- "实收信托" → R6
- "检查时间" → R1

## Garbled Chinese Filename Decoding (Coremail Attachments)

Files downloaded from Coremail (粤财信托 email) may show garbled filenames (`��` characters) — the raw bytes were stored as Latin-1 instead of GBK. Two ways to identify the actual file:

**By xls content:**
```python
import xlrd
for f in os.listdir(dirpath):
    if "2026-06" not in f: continue
    wb = xlrd.open_workbook(os.path.join(dirpath, f))
    ws = wb.sheet_by_index(0)
    name = str(ws.cell(1, 0).value).split("___")[1] if "___" in str(ws.cell(1,0).value) else str(ws.cell(1,0).value)
    print(name)
```

**By file size matching (for 2026-06-30 恒生估值表 xls):**
- ~25KB → 天勤1号 (NAV ~3.1181)
- ~21.5KB → 粤选有财2号FOF (NAV ~1.2219)
- ~23KB → 粤选有财FOF (NAV ~1.5255)
- ~22.5KB → 航长常春藤 (NAV ~1.9714)

## Pitfalls

- **Check date runs**: "检查时间" text is split across many runs. Debug before editing.
- **检查时间在文档段落而非表格中** (2026-07-23 FOF session): The 1-3a may have "检查时间" in document body paragraphs (e.g. P5), NOT in any table cell. Always search BOTH `doc.paragraphs` AND `doc.tables` for date references — not just tables.
- **Empty runs**: Some cells have empty runs at the start. Always loop through all runs.
- **Cell text vs run text**: `cell.text` reconstructs from all runs. `run.text` is the actual editable content.
- **3 data columns**: Cells 1, 2, 3 may all contain the same value in merged tables. Update all matching cells.
- **Font format loss**: The number one cause of user frustration is losing font formatting. Always use run.text.replace(), never clear+add_run for existing content.
- **Copy template first**: When creating a new product, copy from the nearest sibling product's docx, then update product name + data.
- Verify after each save: Re-open the saved docx and verify the changed text is correct.
- **Chinese quote characters break Python heredocs** (2026-07-23): When Python code contains Chinese left/right double quotes (\u201c \u201d), `terminal()` heredoc execution fails with SyntaxError. Always write such scripts as `.py` files and execute via `terminal("python3 script.py")`. Pure ASCII scripts can use heredoc safely.
- **FOF 1-3a R14C3 structure**: FOF 1-3a reports have 23-26 paragraphs in R14C3, comprising market overview (P1-P8: issuance data, strategy performance by category, summary), holdings section (P9-P12: asset size, fund count, holdings list), operations section (P12+). The paragraph indices differ between 1号FOF and 2号FOF by 1 offset. Always print ALL paragraphs with content before editing.
- For the full quarterly refresh workflow (IMAP download, dedup, file replacement), see `workflow/post-investment-data-maintenance` — this skill covers the docx editing component only.
- The reference files in `post-investment-data-maintenance` (`references/docx-update-pattern.md`, `references/valuation-extraction-pattern.md`) contain complementary detail on date splits and extraction.
