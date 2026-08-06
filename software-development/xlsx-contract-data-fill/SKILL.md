---
name: xlsx-contract-data-fill
description: Fill bank product xlsx templates from contract PDFs.
version: 0.1.0
author: Hermes
platforms: [macos, linux]
metadata:
  hermes:
    tags: [XLSX, PDF, DataEntry, BankProducts, Contracts]
---

# Fill Bank Product Entry XLSX from Contract PDFs

Fill a bank product (代销业务新增产品审批表) xlsx template by extracting dates, codes, and terms from contract PDFs (理财产品说明书). Handles multi-sheet templates with redundant shared-string entries. Uses stdlib `zipfile` to directly edit the xlsx OOXML — no openpyxl needed.

## When to Use

- User provides an xlsx template (光大银行/other bank 代销业务新增产品审批表) and one or more product contract PDFs.
- Need to fill product registration codes, validity periods, subscription periods, and contract end dates.
- The xlsx has multiple sheets (Sheet1, Sheet3) with duplicate shared-string entries for the same data.

## Prerequisites

- `fitz` (PyMuPDF) installed for PDF text extraction: `pip install pymupdf`
- Python stdlib `zipfile`, `re`, `io` available (stdlib, no install).
- xlsx template at a known path, product contract PDF at a known path.

## How to Run

1. Extract dates from the PDF using `fitz`.
2. Read the xlsx shared strings to locate template placeholders.
3. Map values to the correct indices — separate range fields from single-date fields.
4. Patch shared strings via `zipfile`.
5. Verify and commit.

## Quick Reference

| Field | Format | Example |
|-------|--------|---------|
| 产品证件有效期 (cert validity) | Date range `YYYY年M月D日—YYYY年M月D日 □长期` | `2026年7月23日—2027年8月11日    □长期` |
| 合同结束日期 (end date) | Single date `YYYY年M月D日 □长期` | `2027年8月11日    □长期` |
| 募集期 (subscription) | Range `YYYY年M月D日-YYYY年M月D日` | `2026年7月15日-7月21日` |

## Procedure

### 1. Extract dates from the contract PDF

Use `terminal` to run PyMuPDF and read the product terms page (typically page 28):

```bash
python3 -c "
import fitz
doc = fitz.open('path/to/contract.pdf')
page = doc[27]  # page 28 = index 27
text = page.get_text()
# Look for: 产品成立日, 产品预计到期日, 募集期, 运作期限
print(text)
"
```

Key dates to extract:
- **产品成立日** → start of contract period
- **产品预计到期日** → end date
- **募集期** → subscription period
- **运作期限** → operation days (e.g. 385天)

### 2. Read the xlsx shared strings and sheet data

```bash
python3 -c "
import zipfile, re
with zipfile.ZipFile('path/to/template.xlsx') as z:
    raw = z.read('xl/sharedStrings.xml').decode()
    items = []
    for m in re.finditer(r'<si>.*?<t[^>]*>([^<]*)</t>.*?</si>', raw, re.DOTALL):
        items.append(m.group(1))
    
    # Print all date-related shared strings
    for i, s in enumerate(items):
        if any(k in s for k in ['产品证件', '合同结束', '募集', '运作天数', '业绩比较']):
            print(f'Index {i}: [{s}]')
"
```

### 3. Locate the correct cells for each field

Check both Sheet1 and Sheet3 (and any other sheets):

```bash
python3 -c "
import zipfile, re
with zipfile.ZipFile('path/to/template.xlsx') as z:
    for sname in z.namelist():
        if 'sheet' in sname.lower() and sname.endswith('.xml'):
            content = z.read(sname).decode()
            for row_tag in ['产品证件', '合同结束']:
                for m in re.finditer(f'<v>(\\d+)</v>', content):
                    # check if the index matches a target label
                    pass
"
```

Or more simply: find each label's shared string index, then search for `<v>INDEX</v>` in each sheet's XML.

### 4. Patch shared strings (CRITICAL: range vs single date)

**RULE**: `产品证件有效期` uses a date **range** (`开始—结束`). `合同结束日期` uses a **single date** only. Never put a range where a single date is expected.

Write a Python script to update the xlsx zip:

```python
import zipfile

with zipfile.ZipFile('template.xlsx', 'r') as z:
    entries = [(name, z.read(name)) for name in z.namelist()]

for i, (name, data) in enumerate(entries):
    if name == 'xl/sharedStrings.xml':
        text = data.decode('utf-8')
        
        # Index 9 (Sheet1 A60): 产品证件有效期 — date range
        text = text.replace(
            '2026年7月23日—2027年8月12日    □长期',  # OLD fabricated value
            '2026年7月23日—2027年8月11日    □长期'   # NEW correct range
        )
        
        # Index 66 (Sheet3 D27): 合同结束日期 — SINGLE date only
        text = text.replace(
            '2026年7月23日—2027年8月11日  □长期',    # OLD (wrong: range)
            '2027年8月11日  □长期'                     # NEW (correct: single date)
        )
        
        # Index 175 (Sheet1 D45): 合同结束日期 — single date
        text = text.replace(
            '年      月     日    □长期',              # OLD (blank template)
            '2027年8月11日    □长期'                    # NEW (filled date)
        )
        
        entries[i] = (name, text.encode('utf-8'))

with zipfile.ZipFile('template.xlsx', 'w', zipfile.ZIP_DEFLATED) as z:
    for name, data in entries:
        z.writestr(name, data)
```

### 5. Always check ALL sheets

A shared string index may be referenced in multiple sheets (Sheet1, Sheet3, etc.). After patching, verify by checking `xl/worksheets/sheet*.xml` for `<v>INDEX</v>` references. If a shared string is used in multiple sheets, one patch covers all of them.

### 6. Verify and commit

```bash
# Verify the changes
python3 -c "
import zipfile, re
with zipfile.ZipFile('template.xlsx') as z:
    raw = z.read('xl/sharedStrings.xml').decode()
    for m in re.finditer(r'<t[^>]*>([^<]*2027年8月[^<]*)</t>', raw):
        print(f'  [{m.group(1)}]')
"

# Commit and push per yuecai workflow
git add 'path/to/template.xlsx'
git commit -m "fix: update dates per contract PDF - product period, end date"
git push
```

## Pitfalls

- **NEVER fabricate dates.** Every date must come from the PDFs. If the PDF doesn't have a value, leave the template blank or mark □长期 — do not invent numbers.
- **合同结束日期 is a single date, not a range.** The end date field format may show `年 月 日 □长期` — fill only the end date, not a start-end range.
- **A shared string index may be shared across sheets.** Patching one shared string fixes all cells referencing it, which is usually correct — but verify the intent matches each sheet.
- **Spacing matters.** Different shared string entries may have the same semantic content with different whitespace (e.g. `2027年8月11日    □长期` vs `2027年8月11日  □长期`). Both must be patched independently.
- **Use `<t>text</t>` as anchor** when replacing to avoid accidentally matching similar patterns in other template fields.
- **Commit message format:** use `fix:` prefix per yuecai AGENTS.md convention. Keep under 72 chars.
- **openpyxl may not align with raw XML rows.** The openpyxl text extraction uses its own row mapping. For precise cell identification, search the raw sheet XML for `<c r="D27"` or similar.

## Verification

After patching, run:

```bash
python3 -c "
import zipfile, re
with zipfile.ZipFile('template.xlsx') as z:
    raw = z.read('xl/sharedStrings.xml').decode()
    items = []
    for m in re.finditer(r'<si>.*?<t[^>]*>([^<]*)</t>.*?</si>', raw, re.DOTALL):
        items.append(m.group(1))
    # Check the three key date fields
    for i in [9, 66, 175]:
        print(f'Index {i}: [{items[i]}]')
"
```

Expected output:
```
Index 9: [2026年7月23日—2027年8月11日    □长期]
Index 66: [2027年8月11日  □长期]
Index 175: [2027年8月11日    □长期]
```
