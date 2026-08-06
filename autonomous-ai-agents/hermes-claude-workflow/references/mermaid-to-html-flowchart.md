# Mermaid → HTML 流程图翻译模式

## 问题背景

用户用 Mermaid `flowchart LR` 描述了知识工程的角色关系图，期望 Hermes 在 HTML 报告中再现。三次实现都被用户否定。

## 教训总结

### 1. Mermaid 图就是规范

用户提供的 Mermaid 代码包含精确的节点定义、箭头流向和标签。实现时必须再现**每一个元素**：

```
A[知识生产类]   →   每个方框 = 一个 rf-node
A --> C         →   每个箭头 = 一个 rf-arrow
A -->|标签| C   →   每个标签 = rf-lbl
H & I --> G     →   组合节点 = rf-node-group
```

**禁止行为：**
- 合并/省略节点（如把「技术类工程师」和「训练类工程师」写成一行文本而非分组的子节点）
- 合并/省略箭头（如把「汇报」和「指导」合并成一条线）
- 改变因果关系（如把产品助理→产品经理变成产品经理→产品助理）

### 2. 一个流程图，不分段

三层标注应该是左侧**连续竖线**（CSS `linear-gradient` 渐变色），不是三个独立区段：

```css
/* ✅ 正确：一根线，三色渐变 */
.rf-side .rf-line {
  background: linear-gradient(var(--gold) 0%, var(--gold) 33%, 
              var(--blue) 33%, var(--blue) 66%, 
              var(--green) 66%, var(--green) 100%);
}

/* ❌ 错误：三个独立 div，中间有分隔线 */
.rf-sect.gold + .rf-sect.blue { border-top: ... }
```

### 3. 用行级布局模拟 LR 流向

Mermaid `flowchart LR` = 从左到右。HTML 实现用 flex row：

```html
<div class="rf-row">
  <span class="rf-node">知识生产类</span>
  <span class="rf-arrow"><span class="rf-sym">→</span></span>
  <span class="rf-node hl">知识运营团队</span>
  <span class="rf-arrow"><span class="rf-sym">←</span></span>
  <span class="rf-node">业务分析类</span>
</div>
```

### 4. 完整节点映射表（本会话）

| Mermaid 代码 | HTML 实现 |
|-------------|-----------|
| `A[知识生产类]` | `<span class="rf-node">知识生产类</span>` |
| `B[业务分析类]` | `<span class="rf-node">业务分析类</span>` |
| `C[知识运营团队]` | `<span class="rf-node hl">知识运营团队</span>` |
| `D[产品经理]` | `<span class="rf-node">产品经理</span>` |
| `E[产品助理]` | `<span class="rf-node">产品助理</span>` |
| `F[知识运营经理]` | `<span class="rf-node">知识运营经理</span>` |
| `G[开发团队]` | `<span class="rf-node">开发团队</span>` |
| `H[技术类工程师]` + `I[训练类工程师]` | `<span class="rf-node-group">...技术类+训练类...</span>` |
| `J[售前顾问]` | `<span class="rf-node">售前顾问</span>` |
| `K[用户]` | `<span class="rf-node">用户</span>` |
| `L[项目团队]` | `<span class="rf-node">项目团队</span>` |

### 5. 箭头类型

| 箭头 | CSS 符号 | 含义 |
|------|---------|------|
| `A --> C` | `→` | 常规流向 |
| `A -->|标签| C` | `⟶ + rf-lbl` | 带标签箭头 |
| `G --- G_Sub` | `→ + rf-lbl「包含」` | 子关系 |
| `E -.->|需求汇集| E_Note` | 虚线/标注类关系 |
