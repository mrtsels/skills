# yuecai FOF / 1-3a 数据源处理

> 用于 yuecai 项目中从各种数据源（火富牛 docx、估值表 xls）提取数据更新 1-3a 的参考。
> 关联技能：`docx-edit-rules`（编辑铁律）、`yuecai-git-workflow`（git 提交）

---

## 一、火富牛绩效报告（docx）作为数据源

用户可能提供两个火富牛导出的 docx 文件"当估值表用"。这些 docx 包含绩效分析表格。

### 1.1 识别产品

```python
from docx import Document

doc = Document('report.docx')
t = doc.tables[0]
# R1C0 是基金名称
fund_name = t.rows[1].cells[0].text.strip()
# "粤财信托·粤选有财FOF配置型集合资金信托计划" => 1号FOF
# "粤财信托·粤选有财2号FOF配置型集合资金信托计划" => 2号FOF
```

### 1.2 关键数据提取（Table 0）

| 字段 | 单元格 | 说明 |
|------|--------|------|
| 基金名称 | R1C0 | 产品标识 |
| 年化波动率 | R1C3 | 带%号 |
| 夏普比率 | R1C4 | 数值 |
| 卡玛比率 | R1C5 | 数值 |
| 下行风险 | R1C7 | 带%号 |
| 最大回撤 | R1C8 | 带%号 |
| 回撤天数 | R1C9-10 | 最大回撤回补期、连续不创新高天数 |

**注意**：R1C1（区间收益）和 R1C2（年化收益）可能为空，需从估值表 NAV 计算增长率。

### 1.3 Table 2 — 风险指标

- Alpha: R1C4
- Beta: R1C5
- 相关系数: R1C0
- 跟踪误差: R1C2
- VaR(95%): R1C7

### 1.4 Table 3 — 最大回撤明细

| 序号 | 最大回撤 | 起止区间 |
|------|---------|---------|
| 1 | 2.40% | 2026-05-08~2026-06-26 |

用于更新 R15（最大回撤值）—— 取序号 1 的最大回撤值。

### 1.5 Table 6 — 基金基础信息

| 字段 | 单元格 |
|------|--------|
| 基金全称 | R0C1 |
| 备案编码 | R2C1 |
| 成立日期 | R2C3 |

### 1.6 Table 5 — 逐年收益

R1 行是 2026 年全年表现（含Q1+Q2）。Q2 区间收益需要从 NAV 增长率计算，
因为 Table 0 的"区间收益"字段可能为空。

---

## 二、FOF 1-3a 表格结构（关键行）

FOF 和 2号FOF 的 1-3a 表格结构与乾元系列不同（33 行，非 31 行）。

| 行号 | 标签 | 说明 |
|------|------|------|
| R5 | 实收信托金额（万元） | 从 2026-06-30 估值表 R46 C8 获取 |
| R13 | 当前净值（季度末） | 从 2026-06-30 估值表 R2 C11 或 R54 C8 获取 |
| R14 | 当前持仓明细 | 需要更新为 Q2 市场概况文本 |
| R15 | 报告期间内最大回撤 | 从火富牛 Table 3 序号1 获取 |
| R16 | 报告期增长率 | 计算：(Q2NAV - Q1NAV) / Q1NAV × 100 |
| R22 | 持仓证券重大异常 | 通常为 ☑不涉及 |
| R24 | 信息披露 | 通常为 ☑是 |
| R30 | 项目风险分类 | 通常为 ☑较低风险 |

---

## 三、估值表数据提取（xls）

### 3.1 FOF 估值表关键行

```
R46: 实收信托     C8=64237429.67 (市值)
R53: 信托资产净值  C8=78489586.12
R54: 今日单位净值  C8=1.2219
R55: 累计单位净值  C8=1.2219
R69: 现金类占净值比 = 31.46%
```

### 3.2 提取代码

```python
import xlrd

wb = xlrd.open_workbook('估值表.xls')
ws = wb.sheet_by_index(0)

nav = None
for r in range(ws.nrows):
    code = str(ws.cell(r, 0).value).strip()
    name = str(ws.cell(r, 1).value).strip()
    if "实收信托" in name:
        trust_amount = ws.cell(r, 8).value  # C8 = 市值
        trust_wan = trust_amount / 10000     # 万元
    if "信托资产净值" in code:
        total_nav = ws.cell(r, 8).value
    if "今日单位净值" in code:
        unit_nav = str(ws.cell(r, 8).value)  # 完整精度
```

### 3.3 增长率计算

```python
# 从 Q1 估值表取旧净值
q1_nav = 1.2235  # Q1 今日单位净值
q2_nav = 1.2219  # Q2 今日单位净值
growth = (q2_nav - q1_nav) / q1_nav * 100  # -0.13%
```

---

## 四、ETF 持仓数据提取（乾元系列）

乾元系列产品的 11010433（ETF基金）科目支持以下提取模式：

### 4.1 提取所有 ETF 持仓

```python
etfs = []
for r in range(ws.nrows):
    code = str(ws.cell(r, 0).value).strip()
    name = str(ws.cell(r, 1).value).strip()
    qty = ws.cell(r, 2).value   # C2 = 数量
    mkt = ws.cell(r, 8).value   # C8 = 市值
    
    # 筛选规则：code 以 11010433 开头、非汇总行、数量 > 0
    if code.startswith("11010433") and len(code) > 10 and float(qty) > 0:
        pct = float(mkt) / nav * 100
        etfs.append((name, float(qty), float(mkt), pct))
```

**注意**：
- 汇总行（code=11010433、1101043301、1101043399）要跳过
- 部分 ETF 名称不含"ETF"字样（如"机器人"、"中证2000"），所以不能靠名字过滤
- 总市值 = sum(etf[2])，对比汇总行 11010433 的 C8 确认一致性

### 4.2 更新 P10（信托计划权益资产配置情况）

替换 `cell.paragraphs[10]` 中存放旧文本的 run 的 text：

```python
p10 = cell.paragraphs[10]
for run in p10.runs:
    if "通过ETF" in run.text or "合计" in run.text or "本季度末" in run.text:
        run.text = new_text  # 新文本包含每只ETF的明细+合计+分析
```

新文本格式：
```
ETF名称：x份，市值x元，占比x.xx%
ETF名称2：x份，市值x元，占比x.xx%
...

合计ETF市值x元，占信托资产净值x.xx%。
分析：本产品适度配置ETF资产...
```
