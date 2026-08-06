# DOCX Template Filling (python-docx)

Filling regulatory form templates (信托/私募资产池申请表, 尽调问卷等) by starting from an existing filled template and adapting it.

## Workflow

### 1. Read the source template

```python
from docx import Document

doc = Document('source-template.docx')
for i, p in enumerate(doc.paragraphs):
    if p.text.strip():
        print(f'{i:>4} | {p.text}')

for ti, table in enumerate(doc.tables):
    print(f'\nTable {ti}:')
    for ri, row in enumerate(table.rows):
        cells = [c.text.strip() for c in row.cells]
        print(f'  Row {ri}: {cells}')
```

### 2. Create a new document from scratch

python-docx cannot easily clone a table structure from one doc to another. For regulatory forms with complex merged-cell tables, **rebuild from scratch** by recreating the table row by row.

```python
from docx import Document
from docx.shared import Pt, Cm
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_TABLE_ALIGNMENT
from docx.oxml.ns import qn

doc = Document()

# Page margins
for section in doc.sections:
    section.top_margin = Cm(2.5)
    section.bottom_margin = Cm(2.5)
    section.left_margin = Cm(2.5)
    section.right_margin = Cm(2.5)

# Default font
style = doc.styles['Normal']
font = style.font
font.name = '黑体'
font.size = Pt(10.5)
style.element.rPr.rFonts.set(qn('w:eastAsia'), '黑体')
```

### 3. Set cell text (with proper CJK font)

```python
def set_cell(cell, text, bold=False, size=8, align=WD_ALIGN_PARAGRAPH.LEFT):
    cell.text = ''
    p = cell.paragraphs[0]
    p.alignment = align
    run = p.add_run(text)
    run.bold = bold
    run.font.size = Pt(size)
    run.font.name = '黑体'
    run.element.rPr.rFonts.set(qn('w:eastAsia'), '黑体')
```

### 4. Merge cells

```python
def merge_row_cells(table, row_idx, start, end):
    cell = table.cell(row_idx, start)
    for c in range(start + 1, end):
        cell = cell.merge(table.cell(row_idx, c))
    return cell

def merge_col_cells(table, col, start, end):
    cell = table.cell(start, col)
    for r in range(start + 1, end):
        cell = cell.merge(table.cell(r, col))
    return cell
```

### 5. Set column widths

```python
col_widths = [Cm(2.0), Cm(1.0), Cm(4.0), Cm(3.5), Cm(3.5), Cm(2.0)]
for row in table.rows:
    for idx, width in enumerate(col_widths):
        row.cells[idx].width = width
```

## Critical: Readback is NOT the same as Word rendering

When you read `table.cell(r, c).text` back after merging, merged cells may show duplicated text from each original cell — this is a python-docx readback artifact. **The actual DOCX renders correctly in Word.** Always verify by opening the file in Word, not by re-reading with python-docx.

## Chinese Content Rules

- **辅证材料文件名必须用中文清晰描述名** — e.g. "私募基金管理人公示信息" not "01-amac-filing"
- Include specific details in parentheses: "2025年第四季度财务报表（资产负债表，实收资本10,000,000.00元）"
- Use 《》 for document titles: 《广东粤财信托有限公司私募管理人尽职调查问卷》
- Use `\\n` in set_cell() for multi-line cell content; avoid manual paragraph breaks

## Evidence Column Wording Pattern

When filling the "对应申请辅证材料明细" column, use this style:

```
材料中文名（关键数据）
```

Examples:
- `私募基金管理人公示信息（含协会备案编号P1004868、成立日期、全职员工数等）`
- `2025年第四季度财务报表（资产负债表，实收资本10,000,000.00元）`
- `基金合同（对冲1号/2号/A500指数增强/全市场选股增强，共4只）`
- `投资合作机构尽职调查问卷（粤财信托出具，明确记载"未出现过风险事件"）`

## File Naming Convention for Evidence

Evidence filenames use hierarchical prefix + en dash:

```
0–申请表.docx                ← cover form, sorts first
1-1–私募基金管理人公示信息.pdf ← condition-item-description
1-2–营业执照副本.pdf
2–财务报表.pdf               ← single-item condition, no sub-index
3-1-1–对冲1号基金合同.pdf      ← condition-item-file#
3-1-2–对冲2号基金合同.pdf
```

Numbering must exactly match the application form's evidence column. The en dash (U+2013) separates the prefix from the Chinese name.
