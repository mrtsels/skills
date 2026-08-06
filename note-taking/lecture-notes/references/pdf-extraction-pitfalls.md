# PDF Extraction Pitfalls（PDF 提取常见问题）

Lecture notes 从 PDF 生成时，文本提取（PyMuPDF / fitz）会遗漏以下内容，必须人工补充：

## 遗漏的内容

### 1. 图表/示意图（Figure）

PDF slides 中的图表视觉元素不会被提取。常见类型：
- 对比图（如 quote-driven vs order-driven market comparison）
- 流程图（如 trade lifecycle overview）
- 市场结构演进图

**处理方式：** 检查提取文本中是否出现 "Figure:" 或 "图" 关键字，从上下文重建对比表。

**重建示例：** 一个 quote-driven vs order-driven 的对比图 → 提取初始状态 + 列出各个动作（take the offer, hit the bid, place limit order, improve price）→ 做成 Markdown 表格。

### 2. 表格数据

PDF 表格可能提取成断裂的行。检查原始 PDF 中是否有：
- 表格标题（"Table of Content", "Sample Order Book"）
- 数据列（如 order book 的 Size/Price 列）

**处理方式：** 在笔记中用 Markdown 表格重建。

### 3. Slide 标题与内容层次

PyMuPDF 按页面渲染顺序提取文本，slide 标题可能在页中而非首位。通读全文后手动重建层级结构。

## 图片处理（非 PyMuPDF 场景）

PyMuPDF 的 `get_text()` 提取文本，`get_pixmap()` 提取图片。如果 slides 中有重要的截图或公式图片，需要用 vision_analyze + get_pixmap 读取。

## 验证清单

笔记写完后检查：
- [ ] 所有 visible Figure 都被覆盖（检查 PDF slide 编号范围）
- [ ] 术语表完整
- [ ] 示例/场景被收录
- [ ] Quick Reference 表涵盖了主要概念
