# File Organization Workflow — 多和美尽调材料 (2026-07-06)

End-to-end example: decompress → convert → rename → categorize → cleanup → git push.

## Directory Structure Created

```
zipped/
├── 管理人尽调材料/               # 49 files → 8 categories
│   ├── 01-company-profiles/        公司基础资料
│   ├── 02-internal-policies/       内部制度
│   ├── 03-audit-reports/           审计报告
│   ├── 04-fund-contracts/          基金合同
│   ├── 05-fund-fact-sheets/        要素表（xlsx→csv）
│   ├── 06-valuation-reports/       资产估值表
│   ├── 07-filing-screenshots/      备案截图
│   └── 08-performance-attribution/ 绩效归因
│
└── 管理人-补充材料/              # 14 files → 4 categories
    ├── 01-credit-report/
    ├── 02-nav-data/               净值表
    ├── 03-level-4-valuation/      四级估值表
    └── 04-performance-analysis/   绩效分析
```

## File Renaming Pattern

| Chinese original | English name |
|---|---|
| 1-和美水豚中证A500指数增强私募证券投资基金合同20250407.pdf | a500-index-enhanced-fund-contract.pdf |
| 1-和美水豚全市场选股增强私募证券投资基金合同20250407.pdf | full-market-stock-selection-fund-contract.pdf |
| 1-和美水豚灵活对冲1号私募证券投资基金基金合同 20250708(1).pdf | flexible-hedge-1-fund-contract-20250708.pdf |
| 和美水豚灵活对冲2号基金合同.pdf | flexible-hedge-2-fund-contract-old.pdf |
| SAGW50_和美水豚灵活对冲1号...资产估值表_20251119_4级__脱敏版.pdf | flexible-hedge-1-valuation-20251119.pdf |
| 【2026-3-20】-(5273#622588)-和美水豚中证A500指数增强...pdf | a500-index-enhanced-attribution-20260318.pdf |
| 【绩效报告012026-6-10】-和美水豚灵活对冲3号...pdf | flexible-hedge-3-performance-analysis-20260608.pdf |

## Key Steps

1. **Decompress**: `unzip -q` for zip, `unar` for rar
2. **Convert**: `textutil` (Word→txt) then manual md, `openpyxl` (Excel→csv with utf-8-sig BOM)
3. **Organize**: Python `os.rename()` batch moves to numbered category dirs
4. **Cleanup**: `rm` all docx/doc when md exists, xlsx when csv exists
5. **Git**: `gh repo create <user>/yuecai --private` → `git add -A && git commit && git push`

## Source File Cleanup Rule (rm_exact pairs)

```bash
# 2 doc/md pairs
rm "manager-introduction.doc"     # manager-introduction.md exists
rm "due-diligence-questionnaire.docx"  # due-diligence-questionnaire.md exists

# 9 xlsx/csv pairs
rm a500-index-enhanced-fact-sheet-20260116.xlsx
rm full-market-stock-selection-fact-sheet-20260116.xlsx
rm flexible-hedge-1-fact-sheet.xlsx  flexible-hedge-1-fact-sheet-old.xlsx
rm flexible-hedge-2-fact-sheet.xlsx  flexible-hedge-2-fact-sheet-old.xlsx
rm flexible-hedge-6-fact-sheet.xlsx
rm flexible-hedge-3-nav.xlsx  flexible-hedge-5-nav.xlsx
```
