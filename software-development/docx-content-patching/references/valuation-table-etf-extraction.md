# 估值表 ETF 持仓提取与 Docx 更新

从证券投资基金估值表 .xls 提取 ETF 持仓明细，更新到 1-3a 投后管理报告的"信托计划权益资产配置情况"段落。

## 估值表结构

- 估值表使用 `xlrd` 读取（.xls 格式）
- ETF 基金持仓在科目代码 `11010433` 下
- 汇总行：`11010433` = "ETF基金"
- 成本行：`1101043301` = "ETF基金成本"
- 公允价值变动：`1101043399`
- 个体持仓：`11010433` + 8 位产品代码（如 `1101043301159131`）
- ETF 全称在 B 列，份额在 C 列，市值在 I 列

## 提取个体 ETF 持仓

```python
# Filter for individual ETF positions (not aggregate rows)
etfs = []
for r in range(ws.nrows):
    code = str(ws.cell(r, 0).value).strip()
    name = str(ws.cell(r, 1).value).strip()
    qty = ws.cell(r, 2).value if ws.cell(r, 2).ctype == 2 else 0
    mkt = ws.cell(r, 8).value if ws.cell(r, 8).ctype == 2 else 0
    
    if not code.startswith("11010433"):
        continue
    if len(code) <= 10:  # skip aggregate rows (11010433, 1101043301, 1101043399)
        continue
    if float(qty) <= 0:
        continue
    
    pct = float(mkt) / nav * 100
    etfs.append((name, float(qty), float(mkt), pct))

total_mkt = sum(e[2] for e in etfs)
total_pct = total_mkt / nav * 100
```

## 更新 Docx P10

P10（信托计划权益资产配置情况）的更新模式：

```python
# Build detailed ETF listing
lines = []
for e in sorted(etfs, key=lambda x: -x[2]):
    lines.append(f"{e[0]}：{e[1]:,.0f}份，市值{e[2]:,.0f}元，占比{e[3]:.2f}%")

# Build analysis summary
if total_pct < 1:
    analysis = f"本产品ETF配置规模较小..."
elif total_pct < 5:
    analysis = f"本产品适度配置ETF资产..."
else:
    analysis = f"本产品ETF配置比例较高..."

new_text = "\n".join(lines) + f"\n\n合计ETF市值{total_mkt:,.0f}元，占信托资产净值{total_pct:.2f}%。\n{analysis}"

# Update the run
for run in cell.paragraphs[10].runs:
    if "通过ETF" in run.text or "合计" in run.text or run.text.strip():
        run.text = new_text
        break
```

## 注意事项

- 部分 ETF 在名称列不包含"ETF"字样（如"机器人"、"中证2000"），需按科目代码 `11010433` 筛选而不用名称关键词
- 汇总行 `11010433`（无子科目代码）和成本/公允价值变动行要排除
- 部分产品 P10 的 run 已被清空，此时用 `p10.runs[0].text = new_text` 并清空其他 runs
