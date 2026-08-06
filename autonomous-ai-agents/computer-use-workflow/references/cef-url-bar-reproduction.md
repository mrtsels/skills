# CEF URL 栏输入复现 & 验证

## 现象

在 ego-lite（CEF 渲染的 Chromium 浏览器）中，`mcp_open_computer_use_type_text` 往 URL 栏输入时，**不会清空原有内容**，而是把新文本**追加**到后面。

### 示例

原有 URL: `duo.itsc.cuhk.edu.hk/portal/Device`
输入: `https://duo.itsc.cuhk.edu.hk/`
结果: `duo.itsc.cuhk.edu.hk/portal/Devicehttps://duo.itsc.cuhk.edu.hk/`

## 原因

CEF 的 `AXTextField` 在收到 `type_text` 时执行的是 `AXUIElementPostKeyboardEvent`（模拟键盘事件），相当于在已有文本的光标位置逐个按键，而不是先全选再键入。而原生浏览器（Safari/Chrome）的 URL 栏收到焦点时会自动全选文字，因此 `type_text` 会直接替换。

## 解决方案

两步走：

```python
# 1. set_value 替换整个网址栏内容
mcp_open_computer_use_set_value(
    app="ego lite",
    element_index="10",  # URL 栏的 ref ID
    value="https://example.com/"
)

# 2. 按回车导航
mcp_open_computer_use_press_key(
    app="ego lite",
    key="Return"
)
```

## 验证方法

1. 输入 URL 后用 `get_app_state` 检查 URL 栏的 `value` 属性
2. 如果 value 是干净的 URL（无垃圾前缀/后缀），则 set_value 生效
3. 按 Return 后检查 tab 标题和页面 URL 是否改变
