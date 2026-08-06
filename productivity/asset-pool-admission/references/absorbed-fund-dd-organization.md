---
name: fund-dd-organization
description: "Organize fund due diligence materials for FOF/trust pool access reviews — match access conditions to evidence, produce Chinese-named numbered deliverables, generate DOCX application forms from templates. Covers AMAC filing, paid-in capital, product track record, compliance, team qualifications, and risk controls."
version: 1.1.0
author: Hermes Agent
license: MIT
metadata:
  hermes:
    tags: [fund, due-diligence, fof, trust, compliance, document-organization, chinese-finance]
    related_skills: [handover-document, project-handover-documentation, database-schema-documentation]
---

# Fund DD Organization

## Overview

When performing FOF/trust fund access reviews（私募基金基础池/备选池准入），you receive a condition list（准入条件）and a DD material pack. You need to select the correct evidence files for each condition, copy to a working directory, and prefix with numbered labels (01-, 02-, etc.).

### ⚠ CRITICAL: Read existing conditions.md FIRST

**Before doing any research or file hunting, always read the existing `conditions.md` first.** This file already contains the evidence-to-condition mapping from the prior planning session. Re-researching from scratch duplicates work already done — the user will correct you ("conditions.md里面有提示的").

The conditions.md for a given manager lives in the working directory (e.g. `docs/jul-06-duohemei/conditions.md`). It contains:
- The full condition text for each numbered condition
- The planned evidence mapping (which files satisfy which condition)
- Quick-reference data tables (performance, team stats, dates)

Read it first, then follow the mapping it provides. Only go hunting in references/ for clarification, not for the initial map.

The DD pack is typically organized into subdirectories (company-profiles/, audit-reports/, fund-contracts/, fund-fact-sheets/, valuation-reports/, etc.) with English filenames.

## User Interaction Pattern

This user processes conditions **sequentially**, one at a time. Never batch-respond with multiple conditions unless explicitly asked. After each condition:
- Copy the evidence files
- Report briefly what was done
- Wait for the next condition ("继续") or next instruction

### ⚠ Critical: Directory Naming

Company names in pinyin must be **correct** — 多和美 = duohemei, NOT heduomei (reversed syllables). Verify the correct company name order before naming directories.

## Workflow

### Step 0: Create Working Directory

Create a date-stamped directory for the review batch:

```
jul-6/duohemei/
```

Use the correct company pinyin (duohemei, NOT heduomei). The final deliverables folder structure mirrors the numbered evidence in the application form.

### Step 1: Understand the Conditions

Read each condition carefully. Common conditions for fund access review:

| Condition | What to look for | Notes |
|-----------|-----------------|-------|
| 备案/许可 | AMAC filing (manager-info-disclosure), business license (business-license-copy) | Both are needed — filing proves AMAC registration, license proves legal entity |
| 实缴资本 ≥ 1000万 | Financial reports showing 实收资本 ≥ 10,000,000 (financial-report-filing, audit reports) | Search for "实收资本" value inside the file before copying |
| 成立 ≥ 1年 + ≥ 3只产品 | AMAC filing (成立时间: check establishment date), fund contracts + NAV data + valuation reports for ≥ 3 products | Must have both contract (proves product exists) + NAV history (proves traceable performance) for each product |
| 无违法违规/诉讼 | Due diligence questionnaire ("未出现过风险事件" section), AMAC integrity info (机构诚信信息 with no negative entries), fact sheets ("最近三年无不良诚信记录") | Cross-reference multiple sources for completeness |
| 按尽调问卷提供材料 | Materials listed in the questionnaire's Section VIII checklist: audit report, articles of association, internal policies, etc. | Copy the questionnaire itself plus all items from its checklist that haven't been copied under other conditions |
| 投研人员≥50% + 核心经验≥3年 + 离职率≤1/3 | Due diligence questionnaire 团队 section (投研人员 list, 人员流动 table), AMAC filing (全职员工人数) | Calculate: 投研人数/总人数 ≥ 50%; check each member's experience (all ≥ 3yr); check 人员变动 table for turnover ≤ 3-4 people |
| 产品收益持续一年以上为正 + 指数增强正超额 | Performance attribution reports from third-party platforms (08-performance-attribution/), NAV history fact sheets (05-fund-fact-sheets/) | **Index-enhanced products require excess return over benchmark, not just positive return** — check 超额 column in attribution reports. Hedge products just need positive absolute return over 1+ year. Attribution reports serve as 私募排排网/第三方平台 evidence. |
| 风险控制制度健全 + 无风险事件 | Risk management policy, information disclosure policy, due diligence questionnaire ("未出现过风险事件"), AMAC filing (机构诚信信息无负面) | Requires proof of system EXISTENCE + proof of no incidents |

### Step 2: Locate Evidence Files

Search the DD pack directories strategically:

```
due-diligence-materials/
├── 01-company-profiles/     # Business license, AMAC filing, articles, questionnaire
├── 02-internal-policies/    # Risk management, disclosure policies
├── 03-audit-reports/        # Annual audits (2022-2025)
├── 04-fund-contracts/       # Product contracts
├── 05-fund-fact-sheets/     # NAV data (CSV)
├── 06-valuation-reports/    # Valuation reports
├── 07-filing-screenshots/   # AMAC product filing proof
└── 08-performance-attribution/  # Third-party performance analysis reports (私募排排网等平台) — primary evidence for "连续一年以上正收益"

supplementary-due-diligence/
├── 02-nav-data/             # Extra NAV data for hedge 3/5/6
├── 03-level-4-valuation/    # Level-4 valuation reports
└── 04-performance-analysis/ # Performance analysis
```

Use targeted grep/search to confirm content matches the condition before copying.

### Step 3: Organize Evidence with Final Naming Convention

**Sequential processing:** Process conditions **one at a time**. Copy files for the current condition number, report what was done, then wait for the next condition ("继续"/"接下一条"). Do not auto-advance.

#### Phase A — Initial Organization

For each condition, copy relevant files from the source DD pack into `jul-6/公司名/`. Use English filenames with condition prefixes initially:

```
jul-6/duohemei/
├── 01-amac-filing.md/pdf           # 条件一证据
├── 01-business-license.md/pdf
├── 02-paid-in-capital.md/pdf       # 条件二证据
├── 03-products/                    # 条件三（多文件用子目录）
│   ├── hedge1-contract.md/pdf
│   ├── hedge1-nav.csv
│   └── ...
├── 04-compliance-statement.md      # 条件四
├── 05-questionnaire-materials/     # 条件五
└── conditions.md                   # 汇总文件
```

For conditions with multiple products/files, use subdirectories. For 1-2 files, keep flat at the directory root.

#### Phase B — Final Renaming (After Application Form Is Created)

After the asset pool adjustment application form is created (DOCX), rename files to match the form's evidence references:

**1. Numbering matches per-form evidence references:**
- Condition 1 → 1-1, 1-2 (two evidence items)
- Condition 2 → 2 (single evidence item)
- Condition 3 → 3-1, 3-2 (two categories: contracts + NAV/valuations)
- Condition 4 → 4-1, 4-2 (cross-references to 1-1 and 5-1)
- Condition 5 → 5-1 through 5-5 (five items)

**2. Chinese descriptive filenames** — never English prefixes on deliverables. Use clear Chinese names:
- ❌ `01-amac-filing.pdf` → ✅ `1-1–私募基金管理人公示信息.pdf`
- ❌ `02-paid-in-capital.pdf` → ✅ `2–2025年第四季度财务报表.pdf`
- ❌ `hedge1-contract.pdf` → ✅ `3-1–对冲1号基金合同.pdf`
- ❌ `a500-enhanced-valuation.pdf` → ✅ `3-2–A500指数增强估值报告.pdf`

**3. En-dash separator** between numbering and name (NOT space, NOT hyphen):
- ✅ `1-1–私募基金管理人公示信息.pdf`
- ✅ `3-1–对冲1号基金合同.pdf`

**4. PDF-only renaming rule:** if a file has both `.md` and `.pdf` versions, **only rename the `.pdf`**. Keep `.md` as English-named reference for CLI readability. Example:
- ✅ `01-amac-filing.md` stays (English reference)
- ✅ `1-1–私募基金管理人公示信息.pdf` (renamed PDF deliverable)

**5. Clean up superseded files** — after renaming, remove old English-named .md files that were superseeded by numbered PDFs, and remove any non-referenced directories (06-~08- etc.) that were intermediate work products.

### Step 4: Create Summary Document

Create `conditions.md` in the output directory documenting the full condition-to-evidence mapping:

```markdown
## 入选基础池标准（条件 01-05）

| 条件 | 内容 | 佐证材料 |
|------|------|---------|
| 01 | ... | `1-1–私募基金管理人公示信息.pdf`, `1-2–营业执照副本.pdf` |

## 入选备选池标准（条件 06-08）

| 条件 | 内容 | 佐证材料 |
|------|------|---------|
| 06 | ... | 尽调问卷团队表+AMAC备案员工数 |
```

The summary should also include a quick-reference data table (performance summary, team stats, establishment dates).

### Step 5: Extract Financial Data from Audit Reports

See `references/financial-data-extraction.md` for the full reference.

**Quick checklist:**
1. Classify PDF as scanned or text-based (fitz text vs image count on first 3 pages)
2. Scanned → render at 250dpi and use `vision_analyze` (reads Chinese financial tables more accurately than tesseract for column-aligned numbers)
3. Extract: 营业收入, 营业成本, 税金及附加, 管理费用, 财务费用, 投资收益, 营业利润, 净利润 from 利润表; 资产总计, 负债合计, 所有者权益 from 资产负债表
4. ⚠ **投资咨询/私募基金管理人的 营业成本 通常为0**（"-"或"—"），成本主要在管理费用中

### Step 6: Find Fund Product AUM

Fund AUM is scattered across multiple document types — never rely on a single source:

| Source | What it gives | Caveat |
|--------|--------------|--------|
| 尽调问卷 Table 10 | 存续规模（万元） | 表头可能误写"亿"，用总规模交叉验证；可能只列出部分产品 |
| 四级估值表（非脱敏） | 精确资产净值 | 脱敏版（****）不可读；优先找非脱敏版 |
| 净值表 XLSX | 单位净值 | 无总份额数，无法计算总规模 |
| 要素表 XLSX | 无规模数据 | 只有费率/策略/开放日等要素 |

**关键原则：产品即规模。** 逐个产品查到资产净值后，按策略归类汇总。多和美这类公司通常有多个产品同属一个策略（如灵活对冲1/2/3/5/6号）。

### Step 7: Search All Files, Not Just One Type

When asked to find specific data, search **all** files in the material pack — different data lives in different documents:
- 财务数据 → 审计报告 PDF
- 前瞻计划 → 尽调问卷 DOCX
- 基金规模 → 四级估值表 PDF
- 产品要素 → 要素表 XLSX
- 业绩表现 → 绩效归因报告 PDF

If a search comes up empty in one document type, the data likely lives in another. The user will correct you if you only checked the audit report.

### Step 8: Verify Evidence

Quick-check each copied file contains the right data:
- For 实收资本: search the financial report for "实收资本" value ≥ 10,000,000
- For products: verify at least 3 distinct products with contracts + NAV data
- For compliance: confirm "未出现过风险事件" or "最近三年无不良诚信记录"
- For index-enhanced products: confirm **超额** column shows positive excess over benchmark (not just absolute return)

### Step 9: Fill Application Form (DOCX Template)

After organizing evidence, create an asset pool adjustment application form based on the Chenyuan template:

1. Read the reference template (e.g. `references/chenyuan/08-asset-pool-adjustment-application-20250213.docx`) with python-docx
2. Identify the table structure: 调入/调出/保留 sections, each with condition text + evidence reference + completeness column
3. Fill in:
   - Manager name (Chinese, e.g. "深圳市多和美投资顾问有限公司")
   - Pool type (基础池/备选池)
   - Direction (调入/调出)
   - Condition rows 1-5 with evidence references
4. **Evidence column content**: use **clear Chinese descriptive filenames** matching the final renamed files (e.g. "私募基金管理人公示信息" NOT "01-amac-filing"). This column tells someone what physical file to grab.
5. The form serves as the canonical evidence index — evidence filenames in the directory should be renamed to match the form's references.

```python
from docx import Document
from docx.shared import Pt, Cm
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.oxml.ns import qn

doc = Document('template.docx')
table = doc.tables[0]

def set_cell(cell, text, bold=False, size=8):
    cell.text = ''
    p = cell.paragraphs[0]
    run = p.add_run(text)
    run.bold = bold
    run.font.size = Pt(size)
    run.font.name = '黑体'
    run.element.rPr.rFonts.set(qn('w:eastAsia'), '黑体')

set_cell(table.cell(4, 4), '私募基金管理人公示信息\\n营业执照副本')
doc.save('output.docx')
```

### Step 10: Final Cleanup

After the application form is finalized and evidence files are renamed to match:

1. Delete old English-named `.md` reference files that are superseded by numbered PDFs
2. Delete all non-referenced intermediate directories (06-team/, 07-performance/, 08-risk-control/ etc.)
3. Delete duplicate/draft version of the application form (keep only the Chinese-named canonical version)
4. Commit with `git commit -m "cleanup: remove superseded raw files"`

The final directory should contain ONLY the files referenced in the application form's evidence column + conditions.md + the form itself.

## Chinese ZIP Files

DD packs often come as Chinese-named ZIP files from WeChat/email. macOS `unzip` cannot handle GBK-encoded filenames ("Illegal byte sequence").

Fix: extract with Python decoding the raw bytes:

```python
import zipfile, os, shutil

with zipfile.ZipFile(src, 'r') as z:
    for info in z.infolist():
        raw = info.filename.encode('cp437')
        try:
            decoded = raw.decode('gbk')
        except:
            decoded = raw.decode('utf-8', errors='replace')
        outpath = os.path.join(dst, decoded)
        os.makedirs(os.path.dirname(outpath), exist_ok=True)
        with z.open(info) as sf, open(outpath, 'wb') as df:
            shutil.copyfileobj(sf, df)
```

If the file header bytes are already valid UTF-8 (common on macOS-created zips), cp437 encode will fail — fall back to direct UTF-8 decode of the raw central-directory bytes:

```python
import struct

# Read raw filename bytes from central directory
with open(src, 'rb') as f:
    data = f.read()
eocd_pos = data.rfind(b'\x50\x4b\x05\x06')
cd_offset = struct.unpack_from('<I', data, eocd_pos + 16)[0]
# ... iterate central directory entries, extract raw_name bytes
decoded = raw_name.decode('utf-8', errors='replace')
```

## Common Pitfalls

1. **Over-copying** — don't blindly copy all files. Match each file to its condition.
2. **Wrong evidence type** — a contract proves product existence but not traceable performance; you need NAV data for that.
3. **Flat naming for large batches** — 20+ files in one directory is messy. Use subdirectories per condition when there are many files.
4. **Not verifying inside the file** — filenames can be misleading (e.g. "financial-report-filing" has 实收资本 data). Search within before copying.
5. **Mixing supplementary and primary** — supplementary files (level-4 valuations, performance analysis) are optional; primary evidence (contracts, fact sheets) are required.
6. **Auto-committing** — commit+push after completing each logical batch (a pool's evidence files, a summary document, or a rename pass). Per workspace convention (AGENTS.md 11), "commit and push is a single logical action; write immediately, commit immediately, push immediately." Do NOT wait for an explicit "commit" instruction. A logical batch is: all files for one admission pool (basic/alternative/core) of one manager. Smaller than that (single file copies) can accumulate until the batch is complete.
7. **English-only filenames on deliverables** — the user expects **Chinese descriptive filenames** on final evidence PDFs (e.g. "1-1–私募基金管理人公示信息.pdf"). English prefixes like "01-amac-filing.pdf" are intermediate-only.
8. **Wrong separator** — use **en-dash (–)** between numbering and Chinese name, NOT space, NOT regular hyphen. Example: `1-1–私募基金管理人公示信息.pdf` (space between 1-1 and the en-dash? no — the en-dash directly connects the number and name).
9. **Renaming .md files** — if a file has both `.md` and `.pdf`, **only rename the `.pdf`**. Keep `.md` as English reference for CLI readability.
10. **Reverse pinyin** — double-check company name order before creating the directory. 多和美 = duohemei, NOT heduomei. 深圳市辰元 = chenyuan, not yuanchen.
11. **Index-enhanced vs hedge success criteria** — index-enhanced products check the **超额** (excess return) column in attribution reports, not just absolute return. Hedge/flexible products check absolute return.
12. **Condition 5 materials overlap** — some items in the questionnaire's required checklist (营业执照, AMAC备案) are already copied under conditions 1-4. Don't re-copy; reference them in the conditions.md summary.
13. **Cross-pool evidence referencing** — when working on 备选池 (conditions 06-08), some evidence is embedded in 基础池 files (e.g. the 尽调问卷's team section and risk-event declaration are in basic pool file `5-1–尽职调查问卷`). Don't re-copy the entire questionnaire — cross-reference it in conditions.md as `见 [basic-pool-file]`. Only copy discrete standalone files (AMAC registration, performance reports, policies) into the alternative-pool directory.
14. **Alternative pool directory naming** — use `jul-<day>-<manager>-alternative-pool` for the directory. The conditions.md for alternative pool should reference the basic pool's conditions.md for shared evidence and should reuse the basic pool's numbered file scheme but start at 06.
15. **Audit-only data search** — when asked to find specific data (fundraising plans, fund sizes, forward-looking statements), do NOT only check the audit report. Search ALL files in the material pack. Financial audits are historical and won't contain plans or AUM breakdowns.
16. **Valuation report redaction** — "脱敏版" valuation reports have position-level data masked (****). The summary NAV (资产净值) at the top of the last data page may or may not be redacted. If redacted, look for non-redacted versions or other sources.
17. **Questionnaire table header units** — DOCX tables often have incorrect headers (e.g. "存续规模(亿)" when values are actually in 万元). Cross-validate with the known total AUM from the same questionnaire's strategy count table.

## Verification Checklist

- [ ] Each condition has at least one evidence file
- [ ] 实收资本 value confirmed ≥ 10M inside the file
- [ ] Product count ≥ 3 confirmed (contract + performance data for each)
- [ ] Compliance statement checked inside the file
- [ ] Index-enhanced products verified for positive **excess** return over benchmark (超额 column), not just positive absolute return
- [ ] Hedge/flexible products verified for positive absolute return over 1+ year
- [ ] Team ratio verified: 投研人数/总人数 ≥ 50%
- [ ] Team turnover verified:离职人数 ≤ 总人数/3 in past year
- [ ] File numbering matches application form's evidence references (1-1, 1-2, 2, 3-1, 3-2, 4-1, 4-2, 5-1~5-5)
- [ ] Chinese descriptive filenames on all PDF deliverables (not English prefixes)
- [ ] En-dash (–) separator between numbering and name (not space, not hyphen)
- [ ] PDF-only rename rule applied (.md files kept English)
- [ ] Superseded .md files and intermediate directories cleaned up
- [ ] conditions.md summary document created
- [ ] Git committed + pushed after batch
