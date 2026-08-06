# Core Pool Evidence Patterns

## Three Conditions (per 粤财核心池准入制度)

**⚠ Numbering rule: conditions are labeled 01-03, not continuing from any previous pool. The file numbering follows the condition number (1- files don't exist yet, 2- = 尽调问卷, 3- = 评分表).**

| # | Condition Title | Evidence File | Source | Notes |
|---|----------------|--------------|--------|-------|
| 01 | 现场尽职调查 | **空置**（待后续现场尽调后补充） | — | On-site DD hasn't happened yet. **Do not fabricate or copy another manager's DD record.** Leave the 1- slot empty. |
| 02 | 综合评分 | `2–尽调问卷（结构化）——管理人.docx` | The manager's original structured DD questionnaire (e.g. `投资合作机构尽职调查问卷（结构化）- 日期.docx`). | The questionnaire serves as the INPUT/scoring basis for the evaluation. It's the most comprehensive single document covering all 5 scoring dimensions. |
| 03 | 评分 ≥ 75 | `3–评分表——管理人.xls` | Created from a scoring table template (from other manager's core pool), filled with **actual data from the target manager's references/**. | This is the OUTPUT document containing scores and total. **Once filled, remove individual performance PDFs that were used as raw data** — the scoring table already captures the data. |

### How the actual duohemei core pool ended up (for reference)

```
0–申请表+调入核心池.docx          ← 唯一 0-
2–尽调问卷（结构化）.docx          ← 条件02 评分依据
3–评分表——多和美.xls             ← 条件03 评分结果 83.5分
conditions.md
```

Notable: The 1- slot is empty (on-site DD not yet done). No compliance screenshots/PDFs — those were removed when the numbering changed. No performance attribution PDFs — removed after scoring table was filled.

## Core Rules (learned from user corrections)

### 申请表（0–）是唯一可复制的文件
- ✅ 从其他管理人的申请表改公司名 → 新管理人的申请表
- ❌ 把其他管理人的尽调记录、评分表、尽调报告复制过来充数
- "不准复制，没有就没有"

### 证据来源只能从 references/ 取
- `references/<目标管理人>/due-diligence-materials/` (primary)
- `references/<目标管理人>/supplementary-due-diligence/` (supplementary)
- `docs/jul-<date>-<manager>-basic-pool/` (already organized materials from basic/alternative pools — reuse rather than re-copying from references)

### Core Pool Initial Prep Scope
The core pool materials in initial prep (before actual on-site DD) should only contain:
- `0–申请表.docx` (application form with company name updated)
- Evidence files drawn from the manager's EXISTING reference materials (尽调问卷, 绩效归因, 备案截图)
- `conditions.md`

DO NOT include:
- Other managers' filled DD records, scoring tables, or comprehensive DD reports
- Template-only files that contain another manager's data (team bios, strategy descriptions, performance numbers)

### File Structure Comparison

**Basic Pool:**
```
0–申请表+调入基础池.docx
1-1–私募基金管理人公示信息.pdf
1-2–营业执照副本.pdf
2–2025年第四季度财务报表.pdf  
3-1-X–基金合同.pdf
3-2-X–估值报告.pdf
5-1–尽调问卷.docx
5-2–公司章程.pdf
5-3–审计报告.pdf
5-4–信息披露制度.pdf
5-5–风险管理制度.pdf
conditions.md
duohemei.md
```

**Alternative Pool:**
```
0–申请表+调入备选池.docx
1-1–私募基金管理人公示信息.pdf
1-2–基金经理介绍.doc
2-1–2-6 绩效归因报告.pdf
3-1–风险管理制度.pdf
3-2–信息披露制度.pdf
3-3–备案截图.png
conditions.md
```

**Core Pool (updated from multiple user corrections — 1- slot empty for future onsite DD):**
```
0–申请表+调入核心池.docx
2–尽调问卷（结构化）——管理人.docx
3–评分表——管理人.xls
conditions.md
```
