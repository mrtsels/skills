# Extracting Financial Data from Chinese Audit Reports (审计报告)

## Report Structure

Standard Chinese 审计报告 for investment/advisory companies follows this order:

| Page(s) | Content | Notes |
|---------|---------|-------|
| 1-2 | 审计意见 (Audit opinion) | Skip |
| 3-4 | 资产负债表 (Balance Sheet) | Assets p3, Liabilities+Equity p4 |
| 5 | 利润表 (Income Statement / 损益表) | Key page for revenue/cost/profit |
| 6 | 现金流量表 (Cash Flow Statement) | Operating/investing/financing cash flows |
| 7-8 | 所有者权益变动表 (Equity Change) | Retained earnings, dividends |
| 9+ | 会计报表附注 (Notes) | Detailed breakdowns of each line item |

**Caveat**: The exact page numbering varies. When pages are missing (e.g. the income statement comes later):
- Use the 目录 (table of contents) on page 1 to find the right page numbers
- Scan the header of each page to identify: "利润表" = Income Statement, "资产负债表" = Balance Sheet

## Vision-Analyze Extraction (Preferred)

For scanned audit reports, **do NOT use tesseract OCR for financial tables** — it garbles aligned numeric columns. Instead:

### Step 1: Render key pages
```python
import fitz
doc = fitz.open("2025年审计报告.pdf")
# Render page 5 (利润表) and pages 3-4 (资产负债表)
for i in [2, 3, 4]:  # 0-indexed
    pix = doc[i].get_pixmap(dpi=250)
    pix.save(f"page_{i+1}.png")
doc.close()
```

### Step 2: Use vision_analyze on each page
```
vision_analyze(
    "page_5.png",
    "Extract: 营业收入, 营业成本, 税金及附加, 管理费用, 财务费用,
     投资收益, 营业利润, 营业外收入, 利润总额, 所得税费用, 净利润.
     Give 本年累计数 (current year) and 上年累计数 (prior year) values."
)
```

Vision models understand Chinese financial table layout and produce structured output with correct numeric alignment, unlike tesseract.

### Step 3: Cross-reference multi-year for trust/accuracy
Always extract from each year's report, then compare the "上年累计数" (prior year column) against the prior year's "本年累计数". They should match. Discrepancies indicate:
- A reclassification or restatement in the newer report
- A misread by the vision model (verify with a second query)

## Key Rows for Due Diligence

For FOF/trust manager admission, the critical rows are:

**利润表 (Income Statement)**:
- 营业收入 (Revenue)
- 营业成本 (Operating Cost) — often 0 for advisory/asset management firms; all costs go through 管理费用
- 管理费用 (Admin Expenses)
- 净利润 (Net Profit)

**资产负债表 (Balance Sheet)**:
- 资产总计 (Total Assets)
- 负债合计 (Total Liabilities)
- 所有者权益合计 (Total Equity)

## Multi-Year Comparison Pattern

| Year | Report Name | File Location |
|------|-------------|---------------|
| 2025 | 2025年审计报告.pdf | references/XXX/ |
| 2024 | 深圳市多和美投资顾问有限公司2024年审计报告.pdf | references/XXX/ |
| 2023 | 2023年审计报告.pdf | references/XXX/ |

Extract the same rows from each and build a 3-year trend table for admission scoring.

## Pitfalls

1. **Page numbering mismatch**: The 目录 may say page 5 for 利润表, but the actual PDF page may differ if the audit opinion spans extra pages. Always scan the header text to confirm.
2. **Multiple "上年累计数" variants**: The prior-year column may be labeled 上年累计数 or 上期数. For 2025's report, this column shows 2024.
3. **营业成本 = 0**: Investment advisory/asset management firms (投资顾问, 资产管理) typically have no 营业成本 (no cost of goods sold). All employee compensation, rent, and operating expenses go into 管理费用. Do not flag as missing data.
4. **Negative figures**: 财务费用 negative = net interest income (more interest earned than paid). 应交税费 negative = tax overpayment/credit. These are normal.
5. **Owner's Equity can be negative**: Small firms with accumulated losses may show negative 所有者权益合计. This is a risk signal.

## "成本" Calculation for Advisory Firms

When user asks for "成本" (cost) but 营业成本 = 0, they typically mean **总营业支出** = 税金及附加 + 管理费用 + 财务费用.

Cross-reference against multi-year data to verify the formula. The user may provide a known figure for an earlier year (e.g. "2023年成本559万") — calculate the expense sum, if it matches, the formula is confirmed.

Example pattern from this session:
```
2023: 税金及附加 25.31 + 管理费用 5,585,698.45 + 财务费用 -262.97 = 5,585,460.79 ≈ 559万 ✓
2025: 税金及附加 144,149.52 + 管理费用 84,570,503.99 + 财务费用 -100,459.55 = 84,614,193.96
```

## Search ALL Documents First — Don't Tunnel on Audit Reports

When user asks for specific data, a common mistake is to focus on one document type (e.g. audit reports) and miss data in other files. **Always search every document in the available directory first.**

### Document Type → Data Map

| Document | Contains | Does NOT Contain |
|----------|----------|-----------------|
| 审计报告 (PDF) | Historical P&L, Balance Sheet, Cash Flow | Forward-looking plans, strategy |
| 尽调问卷 (DOCX) | Team, strategy, fundraising plans, risk controls | Audited financial figures |
| 基金合同 (PDF) | Legal terms, fee structure | Fund target sizes, AUM plans |
| 要素表 (XLSX) | Product specs (fees, lockup, strategy) | Fundraising targets |
| 估值表 (PDF) | NAV, position-level data | Business strategy |
| 绩效归因报告 (PDF) | Performance attribution, risk metrics | Future plans |
| 财务报表报送 (PDF) | Tax-filing version of financials (may differ from audit) | Explanatory notes |
| 公司章程 (PDF) | Corporate governance | Financial data |

### Workflow: Cross-Reference Multi-Source Data

1. **Classification pass**: List all files, categorize by type (see map above)
2. **Search all text-extractable files first**: DOCX, XLSX, text-based PDFs
3. **Then search scanned PDFs** for the remaining data
4. **Cross-reference audit vs tax filings**: The 4-财务报表报送 PDF (tax filing to税务局) may have slightly different numbers from the audit report due to different accounting periods (quarterly vs annual). Note discrepancies.
5. **When data appears in a template**: If the only source is a 尽调问卷 template, the numbers in it are the manager's own submission, not template defaults. Verify by checking if the document was inside the manager's original submission zip.

### Fundraising / Business Plan Data: Check 尽调问卷 (DOCX), Not Audit Reports

Audit reports only contain historical financials. Future-looking content like "募集规划" (fundraising plans), "3年50亿目标", strategy allocations, and AUM targets live in:

- **尽调问卷** (Due Diligence Questionnaire) — typically a .docx file, submitted as part of admission materials
- **投资计划书** (Investment Proposal)
- **商业计划书** (Business Plan)

When user asks for募资目标 or strategy allocation figures, search the 尽调问卷 first, not the audit report PDFs. The 尽调问卷 is a structured Q&A document covering team, strategy, performance, risk management, and future plans.
