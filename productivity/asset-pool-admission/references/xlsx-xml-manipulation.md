# .xlsx 评分表 XML 直接修改方案

## 问题

当模板 .xlsx 含图片（如 470KB PNG 图章/logo）时，`openpyxl.load_workbook()` → `wb.save()` 会损坏图片的 XML 锚点引用，导致打开时报：

```
Cannot read properties of undefined (reading 'anchors')
```

## 原因

- 模板的 M 列使用**共享字符串**（shared strings），不是内联字符串
- sheet2.xml 中 M 列格式：`<c r="M5" t="s"><v>{index}</v></c>`，index 指向 sharedStrings.xml 中的 `<si>` 元素
- openpyxl 保存时会重写共享字符串表，同时破坏 `xl/drawings/drawing1.xml` 中的锚点引用

## 解决方案：zipfile 直接操作 XML

完全绕过 openpyxl，用 zipfile 解包、修改 XML、重新打包。

### 步骤

```python
import zipfile, re

dst = "path/to/file.xlsx"

# 1. 读取全部文件
with zipfile.ZipFile(dst, 'r') as z:
    data = {name: z.read(name) for name in z.namelist()}

# 2. 删除图片/绘图（可选——如果含图片且不需要）
for key in list(data.keys()):
    if 'drawing' in key or 'media' in key:
        del data[key]

# 3. 清理图片引用
import re

# [Content_Types].xml
ct = data['[Content_Types].xml'].decode('utf-8')
ct = re.sub(r'<Override PartName="[^"]*drawing[^"]*"[^/]*/>', '', ct)
ct = re.sub(r'<Default Extension="png"[^>]*/>', '', ct)
data['[Content_Types].xml'] = ct.encode('utf-8')

# sheet2.xml.rels - 删除 drawing 关系
rel = data['xl/worksheets/_rels/sheet2.xml.rels'].decode('utf-8')
rel = re.sub(r'<Relationship[^>]*drawing[^>]*/>', '', rel)
data['xl/worksheets/_rels/sheet2.xml.rels'] = rel.encode('utf-8')

# sheet2.xml - 删除 drawing 标签
s2 = data['xl/worksheets/sheet2.xml'].decode('utf-8')
s2 = re.sub(r'<drawing[^>]*/>', '', s2)

# 4. 修改 sharedStrings.xml - 追加新字符串
ss = data['xl/sharedStrings.xml'].decode('utf-8')
si_count = ss.count('<si>')
# 在 </sst> 前插入
ss = ss.replace('</sst>', '')
text = "新评价意见文字"
lines = text.split('\n')
si_xml = '<si>'
for li, line in enumerate(lines):
    if li > 0:
        si_xml += '<r><rPr><sz val="10"/></rPr><t xml:space="preserve">\n</t></r>'
    si_xml += f'<r><rPr><sz val="10"/></rPr><t xml:space="preserve">{line}</t></r>'
si_xml += '</si>'
ss += si_xml + '</sst>'
new_idx = si_count
data['xl/sharedStrings.xml'] = ss.encode('utf-8')

# 5. 修改 sheet2.xml - 更新 M 列引用
# 旧: <c r="M5" t="s"><v>144</v></c>
# 新: <c r="M5" t="s"><v>196</v></c>  (new_idx)
s2 = re.sub(
    r'(<c r="M7"[^>]*>.*?<v>)\d+(</v>.*?</c>)',
    rf'\g<1>{new_idx}\g<2>',
    s2)

# 6. 更新 N 列数值
s2 = re.sub(
    r'(<c r="N7"[^>]*>.*?<v>)[^<]+(</v>.*?</c>)',
    r'\g<1>0\g<2>',  # 新分数
    s2)

data['xl/worksheets/sheet2.xml'] = s2.encode('utf-8')

# 7. 重新打包
with zipfile.ZipFile(dst, 'w', zipfile.ZIP_DEFLATED) as zout:
    for name, content in data.items():
        zout.writestr(name, content)
```

## 关键数据结构

- `xl/sharedStrings.xml`：共享字符串表，每个 `<si>` 元素是一个共享字符串
- `xl/worksheets/sheet2.xml`：数据工作表，`<c>` 元素定义每个单元格
  - `t="s"` 表示该单元格值引用共享字符串，`<v>{index}</v>` 是索引
  - 无 `t` 属性表示数值
- `<r>` 元素是富文本运行（rich text run），用于在同一单元格内混合格式
- `<rPr>` 是运行属性（字体、字号等），修改时保持不动
