---
name: extjs-api-discovery
description: Discover and interact with ExtJS-based enterprise web application APIs. Covers browser-based API reconnaissance, XHR interception, StoreManager proxy extraction, session/cookie reuse for curl/requests, and pattern documentation. For any enterprise system using ExtJS (common in Chinese financial/trust/securities firms).
category: software-development
triggers:
  - user wants to automate an enterprise web app
  - user asks to "find the API" of a web system
  - reverse-engineering an ExtJS-based website
  - building automation for a Chinese trust/securities system (衡泰/恒生)
---

# ExtJS Enterprise API Discovery

## Overview

Many Chinese financial enterprise systems (衡泰/恒生/金证等) use **ExtJS** as their frontend framework with a Spring MVC backend serving `.action` endpoints. Unlike modern SPAs with documented REST APIs, these systems hide their API surface behind ExtJS data stores.

This skill provides a systematic methodology to:

1. Log in and establish a session
2. Discover API endpoints via browser console instrumentation
3. Extract store proxy URLs from ExtJS internals
4. Reuse the session cookie for direct curl/requests automation
5. Document the API surface for future automation

## Prerequisites

- Browser tool access (for login and exploration)
- Terminal tool access (for curl/requests and scripting)
- Valid credentials for the target system

## Step-by-Step Methodology

### Step 1: Login and Session Establishment

Navigate to the target URL and log in. If the system uses session cookies (JSESSIONID), the browser maintains the session automatically.

```javascript
// In browser console, check login state
document.cookie  // usually empty for httpOnly cookies - that's OK
```

### Step 2: XHR Interception (API Discovery)

Set up an XHR interceptor BEFORE clicking any menu items to capture API endpoints:

```javascript
(function() {
  let seen = new Set();
  let origOpen = XMLHttpRequest.prototype.open;
  XMLHttpRequest.prototype.open = function(m, u) {
    this._method = m; this._url = u;
    return origOpen.apply(this, arguments);
  };
  let origSend = XMLHttpRequest.prototype.send;
  XMLHttpRequest.prototype.send = function(b) {
    let url = this._url || '';
    if (!url.includes('.js') && !url.includes('.css') && !url.includes('.png') && !url.includes('.gif')) {
      let key = this._method + ' ' + url;
      if (!seen.has(key)) { seen.add(key);
        console.log('XHR: ' + this._method + ' ' + url);
        if (b) console.log('  body: ' + b.substring(0, 300));
      }
    }
    return origSend.apply(this, arguments);
  };
  return 'XHR interceptor active';
})()
```

### Step 3: Extract Store Proxy URLs (Deep Discovery)

After clicking menu items and loading pages, extract all registered ExtJS store proxy URLs:

```javascript
// Basic extraction
Ext.StoreManager.each(function(s) {
  let p = s.getProxy();
  if (p && p.url) console.log(p.url);
});

// Comprehensive (handles stores inside nested components)
(function() {
  let apis = new Set();
  Ext.StoreManager.each(function(s) {
    try {
      let p = s.getProxy();
      if (p) {
        if (p.url) apis.add(p.url);
        if (p.api) Object.values(p.api).forEach(u => apis.add(u));
      }
    } catch(e) {}
  });
  console.log(JSON.stringify([...apis], null, 2));
})()
```

Alternatively, query active grid stores:

```javascript
let grids = Ext.ComponentQuery.query('grid');
let stores = grids.map(g => g.getStore && g.getStore()).filter(s => s);
let proxies = stores.map(s => s.getProxy && s.getProxy()).filter(p => p);
let urls = proxies.map(p => ({type: p.type, url: p.url, api: p.api ? Object.keys(p.api).map(k => k+':'+p.api[k]) : null}));
JSON.stringify(urls.slice(0, 10), null, 2);
```

### Step 4: Cookie Extraction for curl/requests

Since JSESSIONID cookies are httpOnly, extract them via the browser's cookie store or use the browser itself to make authenticated requests. For automation scripts, you have two options:

**Option A - Extract cookie via browser console:**
```javascript
// For non-httpOnly cookies only
document.cookie
```

**Option B - Use curl with the JSESSIONID from the browser's dev tools** (check Network tab for Cookie header on any XHR request)

**Option C - Use the browser itself for automation** (Playwright/Selenium) by replaying the session.

### Step 5: Common API Patterns

Most ExtJS enterprise systems share these patterns:

| Pattern | Typical Endpoint | Notes |
|---------|-----------------|-------|
| Grid data | `*/requestCall4Grid.action` | Main data query, POST with form-encoded params |
| Menu nav | `menuLogin.action` | Logs menu open actions |
| Tree data | `*/get*Tree.action` | Hierarchical data (accounts, orgs) |
| User list | `user/findAllUserList.action` | Often paginated (page, start, limit) |
| Task items | `taskItem/findToDoTaskItems.action` | Pending tasks |
| Combo state | `*/getComBoxState.action` | Dropdown state persistence |
| Work remind | `workRemind/*` | Reminders, alerts |
| Orders | `order/*` | Trade orders, approvals |

Common query parameters:
- `xtims-biz-date=YYYY-MM-DD` — business date (specific to 衡泰 systems)
- `_dc=timestamp` — cache buster
- `page=N&start=N&limit=N` — pagination
- `isMultiSel=true/false` — multi-select state

### Step 6: Testing API Calls via Terminal

Once you have a session cookie, test endpoints directly:

```bash
# Login form (if you need to get a session programmatically)
curl -s -c cookies.txt -b cookies.txt \
  -X POST 'https://host/login.action' \
  -d 'username=xxx&password=xxx'

# Test a grid data endpoint
curl -s -b cookies.txt \
  -X POST 'https://host/microservices/xtims-reporting-service/requestCall4Grid.action?xtims-biz-date=2026-07-24' \
  -d 'parameter1=value1&parameter2=value2'
```

## Advanced: RSA + JWT + WebSocket Auth (衡泰/恒生 Pattern)

Some ExtJS enterprise systems (notably 衡泰/恒生) implement a **multi-factor authentication** protocol instead of simple form-login:

```
Step 1: GET  /getPublicKey.action      → RSA public key (PEM)
Step 2: RSA encrypt password           → browser JSEncrypt or Python cryptography
Step 3: POST /doLogin.action           → JWT token (stored in localStorage)
Step 4: WebSocket connect (JWT auth)   → all data flows via WebSocket
Step 5: (optional) POST /login.action  → sets JSESSIONID (decoy/backup for cookie)
```

**Detection signs:**
- Console logs: `"websocket 连接成功"`, `"websocket发送成功!"`
- Globals: `window.SockJS`, `window.webSocketRequest`
- `localStorage.getItem('xtims-token')` returns a JWT
- Browser XHR shows calls to `getPublicKey.action` and `doLogin.action` during login
- HTTP `.action` endpoints return SPA shell HTML (18497 bytes) when called via curl

**JWT Payload format:**
```json
{"name": "周奕昕01", "id": "7087", "exp": 1784918244, "account": "zhouyixin01"}
```

**Implications for automation:**
- Direct HTTP API calls (curl/requests) will NOT work for data queries — all `.action` endpoints return the SPA shell HTML
- The login form POST (`/login.action`) sets a JSESSIONID but does NOT complete the real auth
- **Use Playwright browser automation** for data queries — it handles the full RSA+JWT+WS flow transparently
- The only HTTP endpoints that work standalone: `/getPublicKey.action`, `/doLogin.action` (with RSA-encrypted password), and `/login.action` (partial)

## Alternative: Playwright Browser Automation

When the system uses WebSocket/SockJS for data transport, direct HTTP API automation is infeasible. Use Playwright instead:

```python
from playwright.sync_api import sync_playwright

with sync_playwright() as p:
    browser = p.chromium.launch(headless=True)
    page = browser.new_page()
    page.goto("https://host/login.action")
    page.fill("input", "username")
    page.fill("input[type=password]", "password")
    page.click("text=确认登录")
    page.wait_for_selector("text=当天待办任务", timeout=30000)
    # WebSocket is now established, can click menus and extract data
    page.click("text=交易管理")
    page.wait_for_timeout(2000)
    rows = page.query_selector_all(".x-grid-row")
    # ... extract data from grid rows
```

**Key features of the Playwright approach:**
- Handles full auth flow (RSA → JWT → WebSocket) transparently
- Can navigate menus, click buttons, fill forms
- Can extract grid data from the rendered DOM
- Session state (cookies + JWT token) can be saved and reused
- Password expiry popups can be auto-dismissed

## Step 7: Build a Python Client (Reusable Pattern)

For production use, build a class-based client with automatic session persistence:

```python
import os, sys, json, time, requests
from http.cookiejar import MozillaCookieJar

class ApiClient:
    def __init__(self, username, password, cookie_file):
        self.username = username
        self.cookie_file = cookie_file
        os.makedirs(os.path.dirname(cookie_file), exist_ok=True)
        self.session = requests.Session()
        self._load_cookies()
        self.password = password  # keep for re-login

    def _load_cookies(self):
        """Load cookies from Mozilla-format file."""
        try:
            jar = MozillaCookieJar(self.cookie_file)
            jar.load(ignore_expires=True, ignore_discard=True)
            self.session.cookies.update(jar)  # NOT assignment
        except (FileNotFoundError, OSError):
            pass

    def _save_cookies(self):
        """Persist current session cookies."""
        try:
            jar = MozillaCookieJar(self.cookie_file)
            for c in self.session.cookies:
                jar.set_cookie(c)
            jar.save(ignore_discard=True)
        except OSError:
            pass

    def _check_session(self):
        """Quick validity test — probe a protected page."""
        try:
            r = self.session.get(f"{BASE}/default.action", timeout=10)
            return r.status_code == 200 and "欢迎" in r.text
        except Exception:
            return False

    def login(self, force=False):
        """Login, save cookie, skip if already valid."""
        if not force and self._check_session():
            return True
        resp = self.session.post(
            f"{BASE}/login.action",
            data={"username": self.username, "password": self.password},
            timeout=15,
        )
        # Enterprise login returns 200 + Set-Cookie, not 302
        jsessionid = self.session.cookies.get("JSESSIONID")
        if not jsessionid:
            return False
        # Verify by hitting a protected page
        dash = self.session.get(f"{BASE}/default.action", timeout=15)
        if dash.status_code == 200:
            self._save_cookies()
            return True
        return False
```

**Key patterns:**
- **`session.cookies.update(jar)`** — do NOT assign `MozillaCookieJar` directly to `session.cookies` (type error)
- **`_check_session()`** — lightweight endpoint probe avoids unnecessary re-login
- **Environment vars** for credentials — `os.environ.get("SYS_USER")` / `os.environ.get("SYS_PASS")` avoids hardcoding
- **CLI dispatch** — expose `login`, `todo`, `grid`, `orders` as subcommands via `sys.argv` for easy testing

## Pitfalls

1. **httpOnly cookies** — You cannot read JSESSIONID from `document.cookie`. Extract it from browser Network tab or use the browser session directly.
2. **Business date params** — Many systems require a `xtims-biz-date` or similar query param. Without it, requests fail silently.
3. **Password expiry** — Enterprise systems often prompt password changes on first login. This may block automation. Either accept the prompt (click through via browser) or prepare to handle the change-password flow.
4. **Page blank after login** — Some ExtJS apps load asynchronously. If `browser_snapshot` returns empty, take a screenshot with `browser_vision` to check the actual state — the page may have loaded but the DOM snapshot is delayed.
5. **Menu clicks may not trigger API calls** — Clicking a top-level menu only expands sub-items; you must click a leaf menu item (e.g. "交易执行及确认Plus") to trigger data-load API calls.
6. **Form-encoded vs JSON** — Some endpoints accept form-encoded, others JSON. Check the intercepted body to determine format.
7. **Cache busters** — `_dc=timestamp` params are usually optional and can be omitted.
8. **Ext.Direct** — Some systems use Ext.Direct (RPC-style) instead of standard Ajax. Look for `ext.direct.*` patterns in intercepted calls.
9. **Session expiry** — Enterprise sessions typically expire after inactivity. Implement `_check_session()` pattern: probe a lightweight endpoint before each major operation and re-login on failure.
10. **MozillaCookieJar assignment** — `session.cookies = MozillaCookieJar(...)` raises Pyright type errors. Use `session.cookies.update(jar)` instead, plus a separate `_save_cookies()` method that iterates `session.cookies` into a new jar.
11. **Leaf vs parent menu clicks** — Clicking a top-level menu (e.g. "交易管理") only expands sub-items in the sidebar, triggering NO API calls. You must click a leaf item (e.g. "交易执行及确认Plus") to trigger the actual data-loading API calls. Save `browser_snapshot` refs after expanding a menu, then click the leaf sub-item.
12. **XSRF tokens** — Some systems include anti-CSRF tokens in headers or as request params.
13. **WebSocket/SockJS data transport** — Many ExtJS enterprise systems (especially 衡泰) use **WebSocket/SockJS** for actual data transport rather than standard HTTP API calls. HTTP `.action` endpoints return the SPA shell HTML when called WITHOUT an active WebSocket connection (e.g. via curl). However, when called via ExtJS AJAX from within the browser SPA context (with proper `X-Requested-With: XMLHttpRequest` and `Accept: application/json, text/javascript, */*; q=0.01` headers), these same endpoints DO return JSON. This means the ExtJS stores' proxy URLs ARE valid — you just need the browser context to use them. **Workaround**: Use Playwright/Selenium browser automation for data operations. The browser handles the WebSocket connection automatically.
14. **Login detection: 200 not 302** — Many enterprise login endpoints return **200 + Set-Cookie header** (not a 302 redirect) on success. The client-side JavaScript handles the redirect. To verify: check `resp.headers.get('Set-Cookie')` for `JSESSIONID=...` and then test access to a protected page (`/default.action` or similar) to verify the session is valid. Do NOT check for `resp.status_code == 302`.
15. **Per-account cookie isolation** — When multiple accounts access the same system, use per-account cookie files (e.g. `~/.hermes/cookies/heng_tai_{username}.txt`) to avoid session conflicts between accounts.
16. **`currentUserId` from browser** — In ExtJS apps, the current user's internal ID is often available as `window.currentUserId` (integer). Use this for `menuLogin.action` and other operations that require a user ID parameter.

## Reference Files

See `references/xtims-hengtai-system.md` for the concrete analysis of the 衡泰交易系统 at xtims.yuecaitrust.ltd.
