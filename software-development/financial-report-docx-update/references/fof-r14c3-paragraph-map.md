# FOF R14C3 Paragraph Structure (Q2 2026)

## 2号FOF (粤选有财2号FOF) — 26 paragraphs

| P# | Content | Updated? |
|----|---------|----------|
| P0 | `一、市场发行规模方面` | Section header, keep |
| P1 | Market issuance data (私募发行) | ✅ Q2 data |
| P2 | `二、私募细分策略业绩概况` | Section header, keep |
| P3 | 股票策略 (2 runs: run[0] prefix, run[1] Q1→Q2 text) | ✅ |
| P4 | 市场中性 (3 runs: run[0] space, run[1]+run[2] Q1→Q2) | ✅ |
| P5 | CTA策略 (3 runs) | ✅ |
| P6 | 其他策略 (3 runs) | ✅ |
| P7 | 总结 (2 runs) | ✅ |
| P9 | `二、持仓情况` | Section header, keep |
| P10 | `截至季度末，资产规模...持仓明细如下：` (12 runs) | ✅ Updated NAV & holding ratio |
| P11 | (originally empty — **do NOT write here**, append to P10 last run) | ⛔ Leave empty |
| P12 | `三、本季度运作情况` | Section header |
| P13 | `1、业绩指标-净值曲线` | Sub-header |
| P15 | `2、回撤情况` | Sub-header |
| P18 | `四、基金团队和策略检查` | Section header |
| P19 | `持仓基金投研团队未出现重大变化...` | Keep |
| P21 | `五、基金投资合规情况` | Section header |
| P22 | `穿透各基金估值表检查...` | Keep |
| P24 | `六、基金负面舆情情况` | Section header |
| P25 | `本季度底层基金管理人均未出现...` | Keep |

## 1号FOF (粤选有财FOF) — same structure, offset by 1

The 1号FOF R14C3 has the same paragraph pattern but 1-index offset (the section header P0 is missing a run):

| 2号FOF P# | 1号FOF P# | Content |
|-----------|-----------|---------|
| P0 | P1 | `一、市场发行规模方面` |
| P1 | P2 | Market issuance data |
| P2 | P3 | `二、私募细分策略业绩概况` |
| P3 | P4 | 股票策略 |
| P4 | P5 | 市场中性 |
| P5 | P6 | CTA策略 |
| P6 | P7 | 其他策略 |
| P7 | P8 | 总结 |
| P9 | P10 | `二、持仓情况` |
| P10 | P11 | `截至季度末...` (asset size + holdings) |
| P11 | P12 | `持仓明细如下：` |
| P12 | P14 | `三、本季度运作情况` |
| P13 | P15 | `1、业绩指标` |
| P15 | P17 | `2、动态回撤情况` |
| P18 | P21 | `四、基金团队和策略检查` |
| P19 | P22 | `持仓基金投研团队...` |
| P24 | P27 | `六、基金管理人负面舆情情况` |
| P25 | P28 | `本季度底层基金管理人...` |

## Key differences between 1号FOF and 2号FOF

| Aspect | 1号FOF | 2号FOF |
|--------|--------|--------|
| R14C3 paragraph count | 29 | 26 |
| Holdings structure | P11=asset size, P12="明细如下:" (separate para) | P10=asset size+"明细如下:" (same para) |
| Date format in P10/P11 | `2026.3.31` (dot format) | `2026年3月31日` (Chinese format) |
| 1-3a filename | `附件1-3a：投后管理报告-证券投资V2（粤选有财FOF）.docx` | `附件1-3a：投后管理报告-证券投资（2号FOF）.docx` |
| 附件2 filename | `附件2：项目存续期管理要求落实情况表（粤选有财FOF）.docx` | `附件2：项目存续期管理要求落实情况表（粤选有财2号FOF）.docx` |

## Common edit targets in R14C3

### 2号FOF — P10 run structure (asset size paragraph)
```
run[0]='截至' run[1]='季度末' run[2]='，' run[3]='资产规模' 
run[4]='7848.96' run[5]='万元' run[6]='，' run[7]='持仓基金占比6'
run[8]='8.27%，现金占比31.46%，' run[9]='持仓' run[10]='明细如下' run[11]='：'
```
To add holdings list: **append to run[11]** (not P11):
```python
cell.paragraphs[10].runs[-1].text += "\\n" + holdings_lines
```

### 1号FOF — P11 run structure (asset size paragraph)
```
run[0]='截至' run[1]='2' run[2]='026.6.30，' run[3]='8只私募基金'
run[4]='）仓位占比约' run[5]='6' run[6]='3%，剩余资产为现金类。'
```
Note: Percentage digits are split across runs. `'6'` + `'3%'` = `'63%'`. To change to different percentage, update both runs.
