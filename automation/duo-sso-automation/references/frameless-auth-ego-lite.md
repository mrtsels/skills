# Duo Frameless Auth via ego-lite

## Page rendering behavior

Duo's frameless auth (`/frame/v4/auth/prompt?sid=...`) uses a sandboxed renderer that does NOT appear in standard DOM:

- `document.documentElement.outerHTML` → `<html><head></head><body></body></html>`
- No iframes
- No shadow DOM accessible via standard JS
- Screenshots may be blank/white

Content IS visible through the **accessibility tree** (`get_app_state`), which renders text labels, buttons, and links that standard `browser_console` can't see.

## URL patterns

| Stage | URL pattern |
|-------|-------------|
| Initial Duo redirect | `api-08dc11c9.duosecurity.com/frame/frameless/v4/auth?sid=...&tx=...` |
| Auth prompt (after "暂时跳过") | `api-08dc11c9.duosecurity.com/frame/v4/auth/prompt?sid=...` |
| All methods | `api-08dc11c9.duosecurity.com/frame/v4/auth/all_methods?sid=...` |

Note: The subdomain `api-08dc11c9` is CUHK-specific.

## Ego-lite specific quirks

### URL bar: type_text APPENDS instead of replaces
In CEF-based browsers like ego-lite, `type_text` on the URL bar **concatenates** to the existing value instead of replacing it. Always use `set_value` first, then `press_key(Return)`.

### Duo "更新 Chrome" warning
Duo detects ego-lite's bundled Chromium as outdated and shows a warning overlay:
```
標題: "更新 Chrome" (element ~21)
文字: "浏览器更新有助于保护您的信息。"
按鈕: "暂时跳过" (element ~25)
```
Click "暂时跳过" to dismiss. This is safe — the browser is fully functional.

### Ego menu intercepting clicks
If the ego dropdown menu is open (clicked element 15/16), subsequent clicks on the page may be intercepted by menu items instead of reaching the page content. Close menu by clicking a non-interactive area first.

## Accessibility element indices (typical)

These vary by session but are usually consistent within one auth flow:

| Element | Approx index | Type |
|---------|-------------|------|
| "暂时跳过" button | 25 | button |
| "打开 Duo Mobile" heading | 20 | heading (level 1) |
| "正在等待批准…" text | 25 | static text |
| "重试" button | 23 | button |
| "其他选项" link | 26 or 24 | link |
| "需要帮助？" section | 27 | container |
| "Duo Push 已超时" heading | 20 | heading (level 1) |
