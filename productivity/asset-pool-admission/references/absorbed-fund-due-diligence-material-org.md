---
name: fund-due-diligence-material-org
description: "Organize private fund admission due diligence materials for FOF trust channels. Covers: decompress WeChat-sent zip/rar with Chinese encoding, structure materials by conditions with numbered prefixes, create application forms from templates, apply user's strict naming conventions."
version: 1.0.0
author: Hermes Agent
license: MIT
metadata:
  hermes:
    tags: [fund, due-diligence, fof, trust, naming-convention, workspace-org]
    related_skills: [document-format-conversion, scanned-pdf-ocr]
---

# 私募基金准入尽调材料整理

## Overview

粤财信托 FOF 业务中，接收私募管理人（多和美、辰元等）的尽调材料包，按照准入条件逐条整理编号归档，填写资产池调整申请表。材料通常通过微信发送（zip/rar），需处理中文编码问题。

## Critical Rule: Follow Existing conditions.md

**If conditions.md already exists in the workspace directory with an evidence mapping, follow it exactly.** Do NOT re-analyze or re-derive what evidence goes where. Read conditions.md, then:
- Copy the listed evidence files from references/
- Fill in the application form per the plan
- Renumber per-pool (see pitfalls below)

The evidence mapping was already done in a prior session — redoing it wastes time and introduces inconsistencies.

## When to Use

- 收到新管理人尽调材料包（zip/rar 格式，通过微信传输）
- 需要按粤财信托准入条件（基础池5条+备选池3条）整理归档
- 需要填写资产池调整申请表
- 需要打包发送给同事审核
- 有另一家管理人的已完成申请表可复用为模板

## Workflow

### 0. Template Reuse (if applicable)

If another manager's completed application form for the same pool type exists (e.g. 辰元's 备选池 form → 多和美's), reuse it rather than building from scratch:

1. Copy the template into the new manager's dir as `0–广东粤财信托有限公司资产池调整申请表+<新管理人>+调入<池类型>.docx`
2. In python-docx:
   - `doc.paragraphs[4].text`: update date
   - Table 0, R2 cells containing old manager name: replace with new name
   - Table 0, R4-R6 cells: replace evidence column with the new manager's file references
   - **Keep** condition standard text in R4-R6 columns — that's the fixed template
   - Leave 调出/保留/复核意见 rows empty
3. Evidence condition text is the same across managers (粤财固定模板); only the evidence file names and manager-specific details change.

### 1. 材料接收与解压

See `references/chinese-zip-extract.md` for encoding handling. Extract to `tmp/<manager>/` initially.

### 2. 文件编号与归档

Copy evidence files from `references/<manager>/` into the workspace directory per the conditions.md mapping. Follow naming rules below.

### 3. Screenshot-to-PDF consolidation

When collecting evidence from government query platforms (信用查询、执行信息、企业信用等), screenshots arrive as individual PNGs. Merge them into a single multipage PDF before using as evidence:

```python
from PIL import Image

files = ['screenshot1.png', 'screenshot2.png', ...]
images = [Image.open(f).convert('RGB') for f in files]
images[0].save('4–第三方查询结果汇总.pdf', save_all=True, append_images=images[1:])
```

Then delete the originals. This keeps the working directory clean (one PDF per evidence item instead of 6+ PNGs).

### 4. Zip final package to tmp/

After all files are placed, create a flat zip for sharing:

```bash
cd docs/jul-XX-manager-alternative-pool/
zip -j /Users/minimx/yuecai/tmp/<manager>备选池准入材料.zip 0-*.docx 1-*.pdf 1-*.doc 2-*.pdf 3-*.pdf 3-*.png
```

En-dash in filenames may break bash globs — fallback with Python:

```python
import zipfile, os
with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zf:
    for f in os.listdir(srcdir):
        if f == "conditions.md":
            continue
        zf.write(os.path.join(srcdir, f), f)
```

Exclude conditions.md from the zip — it's your working doc, not evidence.

## User Preferences

### File Naming (strict — do not deviate)

Format: `N–中文描述.ext`

- Use **en dash (U+2013, –)** between number and name, NOT space or hyphen
- Chinese descriptive names only for evidence files
- .md reference files keep English names; .pdf/.docx get Chinese names

Numbering hierarchy:
- `0–` = 申请表（排最前）
- `X–` = 第 X 个条件（单文件）
- `X-Y–` = 第 X 个条件的第 Y 项
- `X-Y-Z–` = 第 X 个条件 Y 项的第 Z 个文件

Example: `3-1-1–对冲1号基金合同.pdf`

### Alternative Checklist-Based Organization (for materials matching 尽调问卷 Section 8)

When organizing files to match the questionnaire's required materials checklist (Section 8 of the standard 粤财 尽调问卷), use letter-prefixed numbering:

**Naming rule: single file = letter prefix only, no number. Multiple files = letter + sub-number.**
- `a–` = 营业执照（single file: `a–营业执照.pdf` NOT `a-1–`; only add sub-number for multiple copies）
- `b–` = 金融许可证（only for bank/trust/public fund/期货 — skip for private fund managers）
- `c–` = 私募登记证明 / 管理人信息公示
- `d–` = 上一年度审计报告（single file: `d–2025年审计报告.pdf`; if multiple years: `d-1–2025年`, `d-2–2024年` etc.）
- `e–` = 公司章程（single file: `e–公司章程.pdf`; if separate partnership agreement: `e-1–章程`, `e-2–合伙协议`）
- `f-1–` / `f-2–` / `f-3–` = 内部管理制度（风险、信息披露、投资、交易等 — sub-number when multiple files）
- `g-1–` through `g-N–` = 尽调问卷提及的支持材料, organized into **category subdirectories**:
  - `g-1–基金合同/` + individual contract files (use product name as filename)
  - `g-2–要素表/` + individual fact sheet files
  - `g-3–备案截图/` + individual screenshot files
  - `g-4–基金经理介绍.doc` (single file at top level)
  - `g-5–四级估值表/` + individual valuation report files
  - `g-6–绩效归因报告/` + individual performance report files (can keep original filenames or rename)
  - `g-7–净值表/` + individual NAV table files
  - `g-8–…` / `g-9–…` (single files at top level when only one)

This scheme is for the raw supporting materials, not the condition-numbered evidence package. Use when the user says "按这个要求整理" pointing to the questionnaire's Section 8 checklist.

### Workspace Structure

```
jul-6/duohemei/     ← 日期目录/管理人名称
├── conditions.md   ← 条件汇总（唯一留档的 md）
├── 0–申请表.docx
├── 1-1–私募基金管理人公示信息.pdf
├── 1-2–营业执照副本.pdf
├── 2–2025年第四季度财务报表.pdf
├── 3-1-1–对冲1号基金合同.pdf
├── 3-1-2–对冲2号基金合同.pdf
└── ...
```

- `tmp/` 放临时文件（zip打包、中间产物），不在 git 中追踪
- 只有最终版才放日期目录提交

### Conditions Reference

**基础池（5条）：**
1. 管理人协会备案 / 资产管理业务许可
2. 实缴资本不低于1000万元
3. 成立时间≥1年，可追溯业绩产品≥3只
4. 近一年无违法违规/内幕交易/利益输送
5. 按《粤财信托私募管理人尽职调查问卷》提供材料

**备选池（3条，独立编号01-03）：**
1. 投研技术人员≥50%，核心成员3年+经验，离职率≤1/3
2. 产品平均收益持续一年以上正收益
3. 健全风控制度，无风险事件导致法律/监管/财务损失

## Common Pitfalls

1. **Chinese zip encoding**: macOS `unzip -O gbk` fails on modern zip files stored as UTF-8. Use Python with `zipfile` + GBK/UTF-8 decode fallback on raw bytes from central directory.
2. **File naming consistency**: user will catch any deviation — spaces, hyphens, or English names in evidence PDFs will be flagged. Always use en dash + Chinese name for evidence files.
3. **Original source priority**: when raw WeChat materials have original .docx/.xlsx/.doc, use those over .md conversions. Check raw zip for originals before creating from markdown. If user provides an original format file directly (e.g. attaches a .doc to replace the .md), delete the .md version immediately without asking — evidence must be PDF/docx/doc, not markdown. The only .md that stays is conditions.md.
4. **Per-pool renumbering**: each pool (基础池/备选池/核心池) gets its OWN 01-N numbering. Do NOT continue the global sequence across pools. E.g. 备选池 conditions are **01-03**, not 06-08. When conditions.md lists them as 06-08, you must still rename the evidence files to 1-1 through 3-3 for the working directory. Only the global condition number in the粤财标准 matters for cross-referencing; working files use per-pool numbering. This applies to ALL文件名, conditions.md content, and the application form evidence column.
5. **Git immediately after EACH operation, not at end of day**: commit + push right after creating a file, copying, renaming, or deleting. Single-file commit is fine. Do NOT batch changes — colleagues share the same repo. If the user asks "剩下的changes", you've already fallen behind. Missing #6 intentionally (was a numbering gap in prior version).
7. **Flat structure**: after organizing, flatten subdirectories. Evidence files all sit directly in the product directory.
8. **Fundraising plan ≠ actual AUM**: The 尽调问卷's "未来1年基金募集规划" section (new scale targets by strategy) is a **future target**, NOT the manager's current AUM. Do not conflate fundraising targets with actual fund sizes. Actual AUM comes from 四级估值表 (资产净值) and 绩效报告 (期末资产净值), not from the plan text.
9. **Product existence by date**: Not all products in the material pack existed at the target date (e.g. 2025年末). Check 成立日期 from performance reports. Funds created in 2026 should be excluded from 2025年末 totals.
10. **Audit-report-only trap**: When asked to find specific financial or forward-looking data, do NOT only check the audit report. Search ALL files: 尽调问卷 DOCX (fundraising plans, product counts), 四级估值表 PDF (fund NAV), 绩效报告 PDF (performance metrics), 要素表 XLSX (strategy), 净值表 XLSX (unit NAV). Different data lives in different documents — the user will correct you if you only checked the audit report.
11. **绩效指标 table index variance**: The 中信证券 绩效归因报告 has 5 pages but the 绩效指标 timeframe table (columns: 今年以来/最近1年/成立以来) can be on either page index 2 or 3. Check both. Render all data pages at 200dpi first, then check with vision_analyze.
12. **Vision-analyze over tesseract**: For financial tables in scanned PDFs, `fitz.get_pixmap()` + `vision_analyze` reads Chinese columnar data more accurately than tesseract OCR. Reserved for key data pages (3-5 pages per report), not full-document OCR.
13. **Screenshot rename before merge**: When user drops screenshots into the working dir with default names like "Screenshot 1.png", rename to proper numbered names (e.g. `7–国家企业信用信息公示系统-1.png`) BEFORE merging into PDF. This avoids having a PDF named after a generic screenshot name. Also commit the renamed files before merging — the merge+delete is a separate logical operation.

## Related: Fund Financial Data Extraction

After materials are organized, you often need to extract financial data (NAV, performance metrics, strategy classification) from the due diligence documents. See `references/fund-financial-data-extraction.md` for the detailed workflow.

## Verification Checklist

- [ ] All 8 conditions have corresponding numbered evidence files
- [ ] Per-pool numbering: each pool (基础池/备选池/核心池) numbers from 01, not continued globally
- [ ] Application form's evidence column matches actual filenames exactly
- [ ] All PDFs have Chinese descriptive names with en dash
- [ ] No .md evidence files remain (only conditions.md stays) — original format only
- [ ] tmp/ contains no committed files
- [ ] git commit + push done
