# 管理人尽调材料 — 实际转换案例

来源：2026-07-06 会话，处理了"管理人尽调材料.zip"和"管理人-补充材料.rar"

## 解压

```bash
mkdir -p zipped
unzip -q "管理人尽调材料.zip" -d zipped/
unar /path/to/管理人-补充材料.rar  # brew install unar
```

## 清理

```bash
cd zipped/管理人尽调材料
rm -rf __MACOSX
find . -name '.~*' -delete
find . -name '.DS_Store' -delete
```

## Word → Markdown

```bash
# 基金经理介绍.doc (10 lines, 3 fund managers)
textutil -convert txt "3-基金经理介绍.doc" -output /tmp/经理介绍.txt

# 尽职调查问卷.docx (702 lines, 8 sections)
textutil -convert txt "投资合作机构尽职调查问卷（结构化）- 20250417.docx" -output /tmp/尽职调查.txt
```

## Excel → CSV (共 9 个)

**管理人尽调材料** — 7个要素表(.xlsx)，均为16行×7-8列结构

| 原文 | 产品策略 |
|------|---------|
| 1-和美水豚中证A500指数增强（要素表）20260116.xlsx | 指数增强 |
| 1-和美水豚全市场选股增强（要素表）20260116.xlsx | 全市场选股 |
| 1-和美水豚灵活对冲1号（要素表）.xlsx | 灵活对冲1号 |
| 1-和美水豚灵活对冲2号（要素表）.xlsx | 灵活对冲2号 |
| 和美水豚灵活对冲1号（要素表）.xlsx | 灵活对冲1号(可能不同版本) |
| 和美水豚灵活对冲2号（要素表）.xlsx | 灵活对冲2号(可能不同版本) |
| 和美水豚灵活对冲6号（要素表）.xlsx | 灵活对冲6号 |

**管理人-补充材料** — 2个产品净值表(.xlsx)，15-16行×5列

| 原文 | 产品 |
|------|------|
| 【产品净值】_BTE30A(A级)_和美水豚灵活对冲3号...xlsx | 灵活对冲3号 |
| 【产品净值】_BTS55A(A级)_和美水豚灵活对冲5号...xlsx | 灵活对冲5号 |

## Python 批量转换示例

```python
import csv, openpyxl, os

base = '/path/to/dir'
for fn in os.listdir(base):
    if not fn.endswith('.xlsx'):
        continue
    path = os.path.join(base, fn)
    csv_name = fn.replace('.xlsx', '.csv')
    csv_path = os.path.join(base, csv_name)

    wb = openpyxl.load_workbook(path, data_only=True)
    ws = wb.active
    max_col = max(c.column for row in ws.iter_rows() for c in row if c.value is not None)

    with open(csv_path, 'w', newline='', encoding='utf-8-sig') as f:
        w = csv.writer(f)
        for row in ws.iter_rows(min_col=1, max_col=max_col, values_only=True):
            w.writerow(list(row))
    wb.close()
    print(f'{fn} -> {csv_name}')
```
