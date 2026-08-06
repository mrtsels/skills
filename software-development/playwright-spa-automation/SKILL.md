---
name: playwright-spa-automation
category: software-development
description: Patterns for automating legacy ExtJS/SPA enterprise applications with Playwright — auth flows, navigation, grid extraction, session persistence.
---

# Playwright SPA 自动化 — ExtJS 企业应用

## 何时使用

- 目标系统是 ExtJS / Vue / React SPA（单页应用）
- 菜单/DOM 通过 JS 动态渲染，直接 click 不生效
- 数据通过 WebSocket / AJAX 加载，页面结构复杂
- 需要持久化登录状态（cookie + localStorage）
- 需要从 ExtJS 表格组件提取数据

---

## 核心原则

1. **查 DOM 结构再写选择器** — 不要猜 class 名。先 `page.evaluate()` 打印 parent 链
2. **优先用 JS 调 SPA 内部函数** — 比模拟点击更可靠（如 `addPanelByPath()`）
3. **持久化 profile** — 用 `launch_persistent_context` + `user_data_dir`，不用手动管理 cookie
4. **容器 ID 定位** — ExtJS 页面容器有固定 ID，用 `#containerId .x-grid-row` 精准定位
5. **验证过的路径必须写进脚本，不是手动演示** — browser 工具只用于发现流程（查 DOM、找 handler、确认路径可行）。**知道怎么走之后立即关掉 browser，写 Playwright 脚本使之可复现。** 用户不需要你用 browser 工具汇报结果，需要你写好脚本。再次 fallback 到 browser 工具会被骂「傻逼」。
6. **持久 profile 走通后别删** — 首次登录后 session 持久化，后续启动秒级复用。清理 profile 会丢掉登录状态。
7. **改代码必改文档** — 每次修改脚本后，必须同步更新所有相关文档（CLI 用法、数据格式、账号信息、新功能说明）。用户会检查，遗漏会被批评。数据存在哪里、怎么存、怎么用，文档必须交代清楚。账号 userId 等信息所有相关文档都要写，不能只写一个地方。

---

## 一、启动配置

### 持久化用户目录（关键）

```python
from playwright.sync_api import sync_playwright

with sync_playwright() as p:
    context = p.chromium.launch_persistent_context(
        user_data_dir="/path/to/profile",  # 固定目录，非临时
        headless=True,
        args=["--no-sandbox", "--disable-blink-features=AutomationControlled"],
        viewport={"width": 1920, "height": 1080},
        locale="zh-CN",
    )
    page = context.pages[0] if context.pages else context.new_page()
```

**效果**：Cookie + localStorage + 扩展全部持久化，二次启动秒级复用 session。

---

## 二、导航 — 调用 SPA 内部函数

ExtJS 菜单项通常有 `onclick` 调用内部函数：

```html
<a onclick="addPanelByPath('XIRJS.workflow.order.OrderMainContainerPlus')">
  投资指令申请Plus
</a>
```

### 批量抓取所有 handler

```python
handlers = page.evaluate("""JSON.stringify(
  Array.from(document.querySelectorAll('a[onclick*="addPanelByPath"]'))
    .reduce((acc, el) => {
      acc[el.textContent.trim()] = el.getAttribute('onclick');
      return acc;
    }, {})
)""")
```

### 直接用 JS 调用（比 click 可靠）

```python
page.evaluate("addPanelByPath('XIRJS.workflow.order.OrderMainContainerPlus')")
page.wait_for_timeout(3000)
```

**注意**：`addPanelByPath()` 返回 ExtJS 组件引用，Playwright 序列化时会报 `Cannot serialize result: object reference chain is too long`。用 `void()` 包裹：

```python
page.evaluate("void(addPanelByPath('XIRJS.workflow.order.OrderMainContainerPlus'))")
```

**不要通过 click DOM 展开子菜单** — ExtJS 的事件绑定在 wrapper 元素上，`<a>` 点击可能不触发展开。

### Tab 已存在时切换（不是重新打开）

当 tab 已经存在（如第二次调用相同菜单），`addPanelByPath` 可能静默失败或报序列化错误。应先检测再切换：

```python
def open_menu(menu_label):
    tab_id = _MENU_TAB_IDS.get(menu_label, "")

    # 检查 tab 是否已存在
    if tab_id:
        exists = page.evaluate(f"!!document.querySelector('#{tab_id}')")
        if exists:
            # 用 ExtJS API 激活已有 tab
            page.evaluate(f"""
                var tp = Ext.getCmp('centerTabPanel');
                if (tp) {{
                    var tab = tp.down('[tabId={tab_id}]');
                    if (tab) tp.setActiveTab(tab);
                }}
            """)
            page.wait_for_timeout(2000)
            return True

    # 不存在则用 addPanelByPath 打开
    ...
```

回退方案：点击 tab header

```python
page.click(f".x-tab:has-text('{menu_label}')", timeout=3000)
```

### 用 JS 点击 ExtJS 隐藏的元素

当目标按钮在**非活动 tab panel** 中时，Playwright 的 `page.click` 会因 `display:none` 报 `element not visible`。即使 `force=True` 在某些 ExtJS 版本下也不生效。

**方案：用 `page.evaluate()` 执行 JS 原生 click**

```python
page.evaluate("""
    var container = document.querySelector('#NewInvestmentInstructionApplication');
    if (container) {
        var spans = container.querySelectorAll('.x-btn-inner');
        for (var s of spans) {
            if (s.textContent.trim() === '新增') {
                var btn = s.closest('.x-btn') || s.parentElement;
                if (btn) { btn.click(); break; }
            }
        }
    }
""")
page.wait_for_timeout(2000)
```

### 菜单项文本与 grid 数据冲突

当浮动菜单项的文字（如"回购到期"）也出现在 grid 行中时，`page.click("text=回购到期")` 可能匹配到 grid 里的隐藏元素。

**方案：先用 page.click 尝试，失败后用 JS 按 getBoundingClientRect 筛选**

```python
try:
    page.click(f"text={item_name}", timeout=5000)
except Exception:
    page.evaluate(f"""
        var all = document.querySelectorAll('a, span');
        for (var el of all) {{
            if (el.textContent.trim() === '{item_name}') {{
                var rect = el.getBoundingClientRect();
                if (rect.width > 0 && rect.height > 0) {{
                    el.click();
                    break;
                }}
            }}
        }}
    """)
    page.wait_for_timeout(3000)
```

### 回退方案

```python
# 如果 addPanelByPath 失败，回退到 DOM 点击
_MENU_PATHS = {
    "投资指令申请Plus": "XIRJS.workflow.order.OrderMainContainerPlus",
    "交易执行及确认Plus": "XIRJS.settle.confirm.ConfirmMainPlus",
}

def open_menu(menu_label):
    path = _MENU_PATHS.get(menu_label)
    if path:
        try:
            page.evaluate(f'addPanelByPath("{path}")')
            page.wait_for_timeout(3000)
            return True
        except Exception:
            pass
    # fallback to DOM click
    page.click(f"text={menu_label}", timeout=8000)
    page.wait_for_timeout(2000)
```

---

## 三、定位 ExtJS 表格数据

### 调试步骤

```python
# 1. 打印所有 grid view 的 parent 链
info = page.evaluate("""
JSON.stringify(Array.from(document.querySelectorAll('.x-grid-view')).map(function(gv) {
  var rows = gv.querySelectorAll('.x-grid-row').length;
  var path = [];
  var el = gv;
  while (el && path.length < 8) {
    var tag = el.tagName.toLowerCase();
    var id = el.id ? '#' + el.id : '';
    path.unshift(tag + id);
    el = el.parentElement;
  }
  return {rows: rows, path: path.join(' > ')};
}).filter(function(x) { return x.rows > 0; }))
""")
```

### 用容器 ID 精准定位

找到目标 grid 所在的容器 ID（如 `#NewInvestmentInstructionApplication`），然后：

```python
rows = page.query_selector_all("#NewInvestmentInstructionApplication .x-grid-row")
for row in rows:
    cells = row.query_selector_all(".x-grid-cell")
    row_data = {f"col_{i}": cell.inner_text().strip()
                for i, cell in enumerate(cells)
                if cell.inner_text().strip()}
```

---

## 四、认证流程逆向

很多企业系统不是简单 form login，而是：

```
① GET /getPublicKey.action    → RSA 公钥
② JSEncrypt 加密密码           → RSA-OAEP
③ POST /doLogin.action        → JWT token
④ WebSocket 连接               → 用 JWT 认证
⑤ 所有数据走 WebSocket
```

JWT 通常存 `localStorage`：

```python
token = page.evaluate("localStorage.getItem('xtims-token')")
```

Playwright 持久 profile 会自动保留 localStorage，无需额外处理。

---

## 五、数据导出 — CSV + JSON

### 提取列头（中文表头）

从 ExtJS grid 的列头行读取中文列名：

```python
header_els = page.query_selector_all("#ContainerId .x-column-header-text")
headers = [h.inner_text().strip() for h in header_els if h.inner_text().strip()]
```

### 导出为 CSV（utf-8-sig，Excel 直接开）

```python
import csv
with open("output.csv", "w", newline="", encoding="utf-8-sig") as f:
    w = csv.writer(f)
    w.writerow(headers)  # 中文列名第一行
    for row in rows:
        w.writerow(row.get(f"col_{i}", "") for i in range(len(headers)))
```

### 数据目录约定

```
docs/{date-dir}/data/
├── {dataset_name}_{account}_{yyyymmdd}.csv   ← 主文件
├── {dataset_name}_{account}_{yyyymmdd}.json  ← 原始数据含 meta
```

JSON 的 meta 结构：

```python
meta = {
    "source": "dataset_name",
    "account": "zhouyixin01",
    "timestamp": "2026-07-24 15:30:00",
    "row_count": 100,
    "columns": ["选择", "提交审批日期", ...],
}
```

### 保存函数模式

```python
def _save_data(data, name, account, to_stdout=False):
    meta = {
        "source": name,
        "account": account,
        "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
        "row_count": len(data.get("rows", [])),
        "columns": data.get("headers", []),
    }
    data["meta"] = meta
    # CSV
    csv_path = DATA_DIR / f"{name}_{account}_{date}.csv"
    _write_csv(csv_path, data["headers"], data["rows"])
    # JSON
    json_path = DATA_DIR / f"{name}_{account}_{date}.json"
    json_path.write_text(json.dumps(data, ensure_ascii=False, indent=2))
```

---

## 六、处理浮动菜单（popup / dropdown）

某些操作按钮（如"新增"）点击后会弹出 ExtJS 浮动菜单，该菜单不在容器 ID 内，位于 DOM 顶层。

### 操作步骤

```python
# 1. 点击按钮弹出菜单
page.click("text=新增", timeout=10000)
page.wait_for_timeout(1500)

# 2. 直接全文搜索菜单项（不用容器限定）
page.click("text=回购续期快速下单", timeout=10000)
page.wait_for_timeout(3000)
```

浮动菜单的 `<a>` 标签有 onclick handler，Playwright 的 `text=` 选择器能直接匹配。

### 验证新 tab 已打开

```python
tabs = page.evaluate(
    "Array.from(document.querySelectorAll('.x-tab')).map(t => t.textContent.trim())"
)
assert "回购续期快速下单" in tabs
```

### 完整示例：新增 → 各类下单页面

通用方法（支持所有菜单项，循环调用时自动切回 tab）：

```python
def click_new_menu_item(page, item_name, category=None):
    # Step 1: 打开投资指令申请Plus（如 tab 已存在则切换）
    open_menu(page, "投资指令申请Plus")
    page.wait_for_timeout(1500)

    # Step 2: 用 JS 点击新增（解决 display:none 问题）
    page.evaluate('''
        var ct = document.querySelector("#NewInvestmentInstructionApplication");
        if (ct) {
            var spans = ct.querySelectorAll(".x-btn-inner");
            for (var s of spans) {
                if (s.textContent.trim() === "\u65b0\u589e") {
                    var btn = s.closest(".x-btn") || s.parentElement;
                    if (btn) { btn.click(); break; }
                }
            }
        }
    ''')
    page.wait_for_timeout(2000)

    # Step 3: 点击目标菜单项
    try:
        page.click(f"text={item_name}", timeout=5000)
    except Exception:
        # 回退：JS 按 getBoundingClientRect 找可见元素
        page.evaluate(f'''
            var els = document.querySelectorAll("a, span");
            for (var el of els) {{
                if (el.textContent.trim() === "{item_name}") {{
                    var r = el.getBoundingClientRect();
                    if (r.width > 0 && r.height > 0) {{ el.click(); break; }}
                }}
            }}
        ''')
    page.wait_for_timeout(3000)
```

**批量调用示例**：

```python
items = ["银行间现券买卖", "场内固收交易", "银行间质押式回购",
         "场内通用质押式回购", "回购到期", "回购提前到期"]
for item in items:
    tab = click_new_menu_item(page, item)
    if tab:
        print(f"  ✓ {item} → tab: {tab}")
```

---

## 七、CLI 调度模式

将每个功能作为独立 CLI 子命令，方便测试和重用：

```python
if __name__ == "__main__":
    cmd = sys.argv[1] if len(sys.argv) > 1 else "login"
    account_name, extra_args = _resolve_account(sys.argv[2:])
    to_stdout = "--stdout" in extra_args

    if cmd == "login":
        ...
    elif cmd == "grid":
        data = hb.get_grid_data("投资指令申请Plus")
        _save_data(data, "investment_instructions", account_name, to_stdout)
    elif cmd == "orders":
        data = hb.get_grid_data("交易执行及确认Plus")
        _save_data(data, "trade_execution", account_name, to_stdout)
    elif cmd == "repo-renew":
        hb.open_repo_renew_quick_order()
        hb.screenshot()
    elif cmd == "new-order":
        items = extra_args if extra_args else ["银行间现券买卖"]
        for item in items:
            tab = hb.click_new_menu_item(item)
            if tab:
                print(f"  ✓ {item}")
    elif cmd == "fill":
        page_name = extra_args[0] if extra_args else "回购续期快速下单"
        from form_filler import FormFiller
        ff = FormFiller(hb)
        ff.fill(page_name, fields_from_natural_language)
```

**--stdout 标志**：默认存文件，--stdout 打印 CSV 到终端用于快速验证。

---

## 八、常见坑

| 问题 | 原因 | 修复 |
|------|------|------|
| 登录状态不保持 | 每次启动新临时 profile | 用 launch_persistent_context + 固定 user_data_dir |
| click 菜单没反应 | ExtJS 事件绑在父元素 | 用 page.evaluate("addPanelByPath(...)") |
| grid 数据混了 dashboard | 选择器匹配了所有 grid | 用容器 ID 限定范围 |
| is_visible() 返回 False | ExtJS CSS 隐藏子菜单 | 直接调内部函数或用 force=True |
| API 返回 HTML 而非 JSON | 缺请求头或 SPA 未初始化 | 用浏览器，不要直接 curl |
| 脚本超时（120s+） | 残留 Chrome 进程或 stale profile | pkill -f chrome 清除残留再试 |
| CSV 中文乱码 | 缺 BOM | 用 utf-8-sig 编码 |
| grid 混入 dashboard 数据 | 选择器匹配了所有可见 grid | 先查 parent 链找容器 ID，再用 #ContainerId .x-grid-row |
| 浮动菜单点不到 | 菜单不在容器 ID 内 | 不用容器限定，全文搜索 text=菜单项 |
| addPanelByPath 无反应 | 函数不存在或路径错误 | 先 typeof window.addPanelByPath 确认存在 |
| 第二次运行卡死 | Chrome 进程残留 | pkill -f chrome 再重试 |
| **新增按钮点不到** | tab 切换后 panel 被 ExtJS display:none | 用 page.evaluate() JS 原生 click，不用 Playwright click |
| **click 匹配到 grid 数据而非菜单项** | 菜单文字与 grid 单元格内容重复 | 回退到 JS 按 getBoundingClientRect 筛选可见元素点击 |
| **addPanelByPath 报序列化错误** | ExtJS 返回组件引用不可序列化 | 用 void(addPanelByPath(...)) 包裹 |
| **tab 重复打开** | 未检测 tab 是否存在 | 先查 #ContainerId 在 DOM 中是否存在，存在则用 Ext.getCmp 切换 |
| **page.evaluate 报 Illegal return statement** | JS 裸 return 在 Playwright 箭头函数内非法 | 用 IIFE: `(() => { ... })()` 包裹 |
| **字段 ID 每次加载不同** | ExtJS 动态生成 ID（自增序列号） | 每次运行时实时扫描 label→id 映射 |
| **表单字段找不到** | 表单条件渲染，不在初始 DOM 中 | 先选记录/点搜索，等渲染完再扫描 |
| **click 菜单项匹配到 grid 数据** | 文字相同（如"回购到期"） | 回退 JS 按 getBoundingClientRect 筛选可见元素 |
| **菜单项点不到** | 定位到隐藏的 grid 行（可见性为 false 但有尺寸） | 先用 `page.click` 尝试，失败后用 `page.evaluate` JS 点击 |
| **新增按钮在非活动 tab 中不可点击** | ExtJS display:none 隐藏非活动 tab panel | 用 `page.evaluate()` JS 原生 click，不用 Playwright click 或 force=True |

---

## 九、调试推荐流程

```
1. page.evaluate() 打印 DOM 结构      → 找唯一标识
2. 查 onclick / addPanelByPath 映射   → 找内部函数
3. 用容器 ID + .x-grid-row 提取数据   → 精准定位
4. 持久 profile 保存 session          → 不用重复登录
5. 出错时 page.screenshot() 看现场    → 比猜错误快
6. 用 `--stdout` 打印 CSV 到终端         → 快速验证数据格式

---

## 十、表单字段扫描（form field mapping）

当需要预填 ExtJS 表单时，先扫描页面的 label↔id 映射，再通过 JS 设值。

### 扫描脚本

```python
def scan_form_fields(page):
    """Extract ExtJS form fields with labels. Returns JSON string."""
    return page.evaluate('''
        var result = [];
        var seen = new Set();
        var containers = document.querySelectorAll(".x-field");
        for (var ct of containers) {
            var input = ct.querySelector(".x-form-field, input, select, textarea");
            if (!input) continue;
            var id = input.id || "";
            if (!id || seen.has(id)) continue;
            seen.add(id);
            var label = "";
            var labelEl = ct.querySelector(".x-form-item-label");
            if (labelEl) label = labelEl.textContent.trim().replace(/[*:]/g, "").trim();
            result.push({
                label: label || "",
                id: id,
                type: input.type || input.tagName || "",
                value: input.value || "",
                required: labelEl ? !!labelEl.querySelector(".x-item-required") : false,
            });
        }
        var allInputs = document.querySelectorAll("input:not([type=hidden]), select, textarea");
        for (var inp of allInputs) {
            if (seen.has(inp.id)) continue;
            var label = "";
            if (inp.id) {
                var lbl = document.querySelector('label[for="' + inp.id + '"]');
                if (lbl) label = lbl.textContent.trim().replace(/[*:]/g, "").trim();
            }
            result.push({
                label: label || "",
                id: inp.id || "",
                type: inp.type || inp.tagName,
                value: inp.value || "",
                required: inp.hasAttribute("required"),
            });
        }
        return JSON.stringify(result, null, 2);
    ''')
```

### 映射文件格式

保存到 `docs/{date-dir}/form-maps/{page-slug}.json`：

```json
{
  "page": "银行间质押式回购",
  "fields": [
    {"label": "所在产品", "id": "accountTree-1367-inputEl", "type": "text", "value": ""},
    {"label": "交易方向", "id": "combobox-1890-inputEl", "type": "text", "value": "0158101"},
    {"label": "产品名称", "id": "accountTree-1889-inputEl", "type": "text", "value": ""},
    {"label": "质押券名称", "id": "textfield-1854-inputEl", "type": "text", "value": ""},
    ...
  ]
}
```

### 映射文件格式

保存到 `docs/{date-dir}/form-maps/{page-slug}.json`：

```json
{
  "page": "银行间质押式回购",
  "fields": [
    {"label": "所在产品", "id": "accountTree-1367-inputEl", "type": "text", "value": ""},
    {"label": "交易方向", "id": "combobox-1890-inputEl", "type": "text", "value": "0158101"},
    {"label": "产品名称", "id": "accountTree-1889-inputEl", "type": "text", "value": ""},
    {"label": "质押券名称", "id": "textfield-1854-inputEl", "type": "text", "value": ""},
    ...
  ]
}
```

### 表单预填 — FormFiller

**关键问题**：ExtJS 的表单控件 ID 是每次页面加载时动态生成的（如 `textfield-1885-inputEl` 中的 1885 是自增序列号），不能保存静态映射直接用。必须实时扫描 DOM 做 label→id 映射。

**推荐使用独立脚本** [`scripts/form_filler.py`](../scripts/form_filler.py)，核心逻辑：

```python
class FormFiller:
    def __init__(self, browser):
        self.browser = browser

    @property
    def page(self):
        return self.browser.page

    def fill(self, page_name, field_values):
        """Open page via 新增 menu, scan fields, fill each."""
        tab = self.browser.click_new_menu_item(page_name)
        time.sleep(2)
        field_map = self._scan_current_page()
        for label, value in field_values.items():
            self._fill_field(label, value, field_map)
            time.sleep(0.3)
```

#### 实时扫描（解决 ID 不固定）

用 5 种策略按优先级查找 label：

```javascript
function findLabel(el, id) {
    // 1. label[for] 标准关联
    var lbl = document.querySelector('label[for="' + id + '"]');
    if (lbl) return lbl.textContent;
    // 2. ExtJS .x-field 容器里的 .x-form-item-label
    var ct = el.closest('.x-field');
    if (ct) { var l = ct.querySelector('.x-form-item-label'); if (l) return l.textContent; }
    // 3. 表格布局：前驱 td 文本
    var td = el.closest('td');
    if (td) { var prev = td.previousElementSibling; if (prev) return prev.textContent; }
    // 4. 父级的前驱兄弟
    var p = el.parentElement;
    if (p) { var prev = p.previousElementSibling; if (prev) return prev.textContent; }
    // 5. 沿父链找 .x-field-label-text / .x-form-item-label
    return '';
}
```

#### IIFE 包裹（重要 — JS 语法坑）

`page.evaluate()` 的 JS 字符串会被 Playwright 包裹成箭头函数，**裸 `return` 不合法**。必须用 IIFE：

```python
# ❌ 错误 — SyntaxError: Illegal return statement
page.evaluate("if (!el) return 'not found'; el.click();")

# ✅ 正确 — 用 IIFE 包裹
page.evaluate("""
(() => {
    var el = document.getElementById('xxx');
    if (!el) return 'not found';
    el.click();
    return 'ok';
})()
""")
```

#### 字段类型自动识别

根据 input ID 前缀（ExtJS 命名约定）分发到不同 setter：

| ID 包含 | 类型 | 设值方式 |
|---------|------|----------|
| `combobox` | 下拉框 | nativeInputValueSetter + input/change 事件 + focus/blur |
| `datefield` | 日期 | `set_text_input(value)` |
| `amountTextFiled`, `numberfield` | 金额/数字 | strip 非数字字符 + `set_text_input` |
| `checkboxfield` | 复选框 | 找到 `.x-form-cb-wrap` 点按切换 |
| `accountTree` | 产品选择器 | `set_combobox` + Tab 键触发搜索 |
| `bondCombox` | 债券选择器 | `set_combobox` |
| `counterpartyCombox` | 对手方选择器 | `set_combobox` |
| `textareafield` | 多行文本 | nativeValueSetter + input/change 事件 |

**nativeInputValueSetter 模式**（核心技巧 — 解决 React/ExtJS 不响应普通 `el.value=...` 的问题）：

```python
page.evaluate("""
(() => {
    var el = document.getElementById('my-id');
    var setter = Object.getOwnPropertyDescriptor(
        window.HTMLInputElement.prototype, 'value'
    ).set;
    setter.call(el, '新值');
    el.dispatchEvent(new Event('input', {bubbles: true}));
    el.dispatchEvent(new Event('change', {bubbles: true}));
    return 'ok';
})()
""")
```

#### 表单条件渲染

部分页面（如 回购到期/提前到期/续期快速下单）的"新开交易信息"表单只在选中某条到期合约后才渲染。首次打开时只有搜索区。必须先：

1. `fill("页面名", {搜索区字段})` — 填搜索条件
2. 点击搜索按钮 → 选中到期合约
3. 等表单渲染完 → `fill("页面名", {表单字段})`

#### 完整示例（JS 点击被 ExtJS 隐藏的按钮）

当目标在非活动 tab panel 时（display:none），Playwright click 报 not visible：

```python
page.evaluate("""
    var container = document.querySelector('#NewInvestmentInstructionApplication');
    if (container) {
        var spans = container.querySelectorAll('.x-btn-inner');
        for (var s of spans) {
            if (s.textContent.trim() === '新增') {
                var btn = s.closest('.x-btn') || s.parentElement;
                if (btn) { btn.click(); break; }
            }
        }
    }
""")
page.wait_for_timeout(2000)
```
