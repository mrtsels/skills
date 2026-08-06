# _ycxtcwb 目录乱码文件名处理

## 文件来源

`mail-attachments/_ycxtcwb/` 是粤财信托 Coremail 邮箱下载附件的目录。文件名因编码问题（CP437→GBK 转换失败）显示为乱码（`��������` 字符）。

## 文件识别方法

不能靠文件名判断内容。必须读取 xls 文件头：

```python
import xlrd, os

yc = "/path/to/mail-attachments/_ycxtcwb"
for f in sorted(os.listdir(yc)):
    path = os.path.join(yc, f)
    wb = xlrd.open_workbook(path)
    ws = wb.sheet_by_index(0)
    full_name = str(ws.cell(1, 0).value)
    name = full_name.split("___")[1] if "___" in full_name else full_name
    nav_info = str(ws.cell(2, 11).value)
    print(f"产品: {name} | {nav_info}")
```

## 文件对应关系（2026-06-30）

| 估值表内容 | 典型大小 | 对应目录 |
|-----------|---------|---------|
| 天勤1号 | 25KB | Q2-2026/天勤/ |
| 粤选有财2号FOF | 21KB | Q2-2026/粤选有财2号FOF/ |
| 粤选有财FOF | 23KB | Q2-2026/粤选有财FOF/ |
| 航长常春藤 | 22KB | Q2-2026/航长/ |

## 复制并命名

```python
import xlrd, os, shutil

src_dir = "docs/jul-22-post-investment/mail-attachments/_ycxtcwb"
dst_base = "docs/jul-22-post-investment/Q2-2026"

dst_map = {
    "天勤": "天勤",
    "2号FOF": "粤选有财2号FOF",
    "FOF配置型": "粤选有财FOF",
    "航长": "航长",
}

for f in os.listdir(src_dir):
    if "2026-06-30" not in f:
        continue
    wb = xlrd.open_workbook(os.path.join(src_dir, f))
    ws = wb.sheet_by_index(0)
    full_name = str(ws.cell(1, 0).value)
    name = full_name.split("___")[1] if "___" in full_name else full_name
    
    dst = None
    for key, val in dst_map.items():
        if key in name:
            dst = val
            break
    if not dst:
        continue
    
    trustee_name = name.replace("粤财信托·", "")
    proper_name = f"2026-06-30_{trustee_name}_证券投资基金估值表.xls"
    shutil.copy2(os.path.join(src_dir, f),
                 os.path.join(dst_base, dst, proper_name))
```

## 注意

- 同一个产品可能有多个日期的估值表（如航长有 2026-06-26 和 2026-06-30）
- 文件名中的中点符号在不同系统显示可能不同，不影响读取
