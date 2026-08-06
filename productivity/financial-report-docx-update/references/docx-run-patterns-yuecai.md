# Docx Run Patterns — yuecai 1-3a / 附件2

Recorded 2026-07-23 during Q2 update of 9 乾元 products.

## Paragraph 5 (检查时间)

All products use the same P5 structure. Runs in cell T0R1C0 (and C1):

```
run[0]: "信托经理："
run[1]: "李智圆"
run[2]: "\t"
run[3]: "\t      检查时间："
run[4]: "202"   (or "20" in some versions)
run[5]: "6"     (or "2" in some versions)
run[6]: "年"
run[7]: "3"     (month)
run[8]: "月"
run[9]: "31"    (day, or "3" then "1" in separate runs)
run[10]: "日"
```

航长 variant (31 split as "3"+"1"):
To update: `run[7].text="6"`, `run[9].text="2"`, `run[10].text="6"` (->6月26日)

## Table R30 (风险分类更新)

R30 checkbox row in 附件1-3a has 9 runs per cell:
```
run[0]: "□"
run[4]: "☑" -> "□" to uncheck 无
run[7]: "□" -> "☑" to check 新增项目
```

## R14 Key Patterns

P10 (holdings, 7 runs): "本季度末权益资产仓位占比为0。"
```
run[5]: "0" -> replaced with holdings description
run[0..4]: cleared (set to "")
```

Product data (Q2 2026 June 30):
| Product | NAV(万) | ETF | Bonds | 
|---------|---------|-----|-------|
| 乾元增利2 | 11,530 | 690万 | 9,129万+2,889万 |
| 乾元增利3 | 18,436 | 879万 | 16,139万+5,472万 |
| 乾元增利5 | 1,352 | 33万 | 1,324万 |
| 乾元增利6 | 5,328 | 49万 | 5,081万 |
| 乾元增利7 | 6,125 | 44万 | 4,596万 |
| 乾元增利8 | 853 | 9万 | 709万 |
| 乾元增利9 | 1,703 | 39万 | 1,303万 |
| 乾元增利10 | 1,594 | 16万 | 1,100万 |
| 乾元增利11 | 6,762 | 0 | 4,009万+1,199万(债基) |
