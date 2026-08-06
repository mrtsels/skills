# JS 空值/假值合并陷阱

## 问题模式

JavaScript 中 `||` 和 `&&` 不是「空值合并」运算符——它们是 **假值短路** 运算符。

```js
// ❌ 错误——"" 是假值，会穿透
rc.globalReview || d.reviewComment
// 当 globalReview="" 时，返回 d.reviewComment（原始 JSON 字符串）

// ✅ 正确——只排除 null/undefined
rc.globalReview ?? d.reviewComment
// 或明确兜底到空字符串
rc.globalReview ?? ''
```

## 常见假值

以下值在 `||` 中全部为 **假**，会穿透到右侧：

| 值 | 类型 | 业务上可能是有效值吗？ |
|---|---|---|
| `""` | 空字符串 | ✅ 用户清空了输入、字符串字段重置 |
| `0` | 数字零 | ✅ 计数器、评分、价格 |
| `false` | 布尔假 | ✅ 开关状态 |
| `null` | 空值 | ❌ 通常是缺失 |
| `undefined` | 未定义 | ❌ 通常是缺失 |

## 适用场景

在 SPA 中解析 JSON 字段时最容易踩这个坑：

### 解析审核意见/备注

```js
// JSON.parse 后的对象
var rc = JSON.parse(d.reviewComment);
// rc.globalReview 可能是 ""（审核员清空了意见）

// ❌ 错误——"" 穿透导致显示原始 JSON 字符串
textbox.value = rc.globalReview || d.reviewComment;

// ✅ 正确——明确处理空字符串
textbox.value = rc.globalReview ?? '';
// 或
textbox.value = rc.globalReview != null ? rc.globalReview : '';
```

### 表单字段还原

```js
// ❌ false 穿透，checkbox 不回显
checkbox.checked = rc.someFlag || false;
// 当 someFlag=false 时，右侧 false 覆盖了

// ✅ 使用 nullish coalescing
checkbox.checked = rc.someFlag ?? false;

// ✅ 或显式判断
checkbox.checked = rc.someFlag === true;
```

### 数字字段

```js
// ❌ 0 穿透
price = data.price || 100;
// 当 price=0 时，显示 100

// ✅
price = data.price ?? 100;
```

## 调试方法

当 UI 显示意外内容时：

1. **确认是什么值** — 在浏览器 console 或加断点打印：
   ```js
   console.log('globalReview:', JSON.stringify(rc.globalReview), 'type:', typeof rc.globalReview);
   ```

2. **检查是 `||` 还是 `??`** — 搜代码中的 `||` 看看是否应该用 `??`

3. **修复后兜底值要合理**：
   - 文本框 → `''` 或 `''`
   - checkbox → `false`
   - 数字 → `0` 或 `null`
   - 下拉框 → `null` 表示「未选择」

## 完整对比

| 运算符 | 名称 | 对 `""` | 对 `0` | 对 `false` | 对 `null` | 对 `undefined` |
|--------|------|---------|--------|------------|-----------|----------------|
| `a \|\| b` | 逻辑或 | b (穿透) | b (穿透) | b (穿透) | b | b |
| `a ?? b` | 空值合并 | a (保留) | a (保留) | a (保留) | b | b |
| `a ? a : b` | 三元 | a (保留) | a (保留) | a (保留) | b | b |
