# HTML 流程图 / 三层框选 Prompt 示例

From session 2026-05-26: 知识工程领导汇报 Page 6 三层实践体系可视化。

## 迭代教训：从复杂到简洁

### ❌ 第一次尝试（用户评分：乱）

设计的横向三区段（`.hband gold/blue/green`）有复杂的节点排列、多种箭头方向、子节点内嵌。用户反应："好乱"。

### ✅ 最终方案（用户认可）

保持 Mermaid-style 的**干净节点+箭头**流程图，在左侧加三个**彩色括弧**标注分层归属。

**核心原则：不要用复杂的 CSS 布局来做流程图。用户更喜欢简洁的节点-箭头-括弧组合。**

## Final Prompt 结构解析

### 前置声明
```
TASK: Rewrite the 三层实践体系 on Page 6 into a clean flowchart with three layer brackets.
I have made a previous attempt that was too messy with horizontal bands. Discard that completely.
```

### 流程图布局参照（Mermaid-style）
给出用户认可的 Mermaid 参考图，然后逐行描述 HTML 节点布局：

```
Row 1: [知识生产类] → [知识运营团队] ← [业务分析类]
Row 2: [产品助理] ─汇报→ [产品经理]
         [产品助理] ─配置管理/考核→ [知识运营经理]
         [知识运营团队] ─汇报→ [知识运营经理]
Row 3: [技术类+训练类工程师] → [开发团队] ─汇报→ [知识运营经理]
Row 4: [知识运营经理] ─指导→ [售前顾问] ─汇报→ [用户]
Row 5: [用户] ─落地→ [项目团队]
         [知识运营团队] ─组建→ [项目团队] ←组建─ [开发团队]
```

### 三层括弧（关键创新）
不要试图用色块/框包围节点，而是用竖线+垂直文字标注：

```css
/* 三层括弧布局 */
.rf-bracket::before {
  content: "";
  position: absolute;
  left: 0; top: 0; bottom: 0;
  width: 3px;
  border-radius: 2px;
}
.rf-bracket .rf-b-name {
  font-size: 0.65rem;
  font-weight: 600;
  writing-mode: vertical-lr;
  /* 纵向文字 */
}
.rf-bracket.gold::before { background: var(--gold); }
.rf-bracket.blue::before { background: var(--blue); }
.rf-bracket.green::before { background: var(--green); }
```

### 避免的陷阱

| 陷阱 | 用户反应 | 正确做法 |
|------|---------|---------|
| 复杂的水平分区（横向区段嵌套节点+箭头+分组） | "好乱" | 简洁的节点+箭头排成行，不要嵌套布局 |
| 自定义复杂 CSS 定位 | 不直观 | 用简单的 flex row 排列，自然换行 |
| 花哨的 hover 效果和渐变 | 分散注意力 | 仅用 border-color hover 保持干净 |
| 过小的间距导致元素挤在一起 | 难以阅读 | 适当使用 gap + padding 保证可读性 |

## 关键要点

1. **给 Claude 展示 Mermaid 参考图** — 用 `flowchart LR` 格式描述期望的布局，让 Claude 精确理解节点位置关系
2. **明确说明"不要做什么"** — "不要复杂的水平分区，只加三个括弧" 比只描述目标更有效
3. **括弧用 absolute 定位** — 放在父容器的左侧，通过 top/bottom 控制高度
4. **跨层节点用边框高亮** — 知识运营经理/知识运营团队出现在多个层时，用 `border-color:var(--gold)` 突出显示
5. **垂直文字用 `writing-mode: vertical-lr`** — CSS 原生支持，比 transform:rotate 更稳健

## 成本参考

第二次迭代（27 turns，复用缓存）：
- input tokens: 33,695 (非缓存) + 616,832 (缓存命中)
- output tokens: 15,711
- 总花费: **¥0.08**（deepseek-v4-flash）
