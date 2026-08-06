---
name: duo-sso-automation
description: Automate login through Duo Security-protected SSO portals (university, enterprise). Covers browser health check bypass, credential fill, push 2FA handling, and Auto-2FA extension integration for push auto-approval.
---

# Duo SSO Automation

Automate login through portals protected by Duo Security two-factor authentication. Supports any site using Duo's standard frameless auth flow.

**Two modes (Auto-2FA extension recommended):**
1. **Auto-2FA extension** (recommended) — Browser extension generates 6-digit passcodes automatically when made the active device. Does NOT auto-approve push. See `references/auto-2fa-setup.md`.
2. **Manual phone approval** (fallback) — Push sent to phone, user approves in Duo Mobile app

## Generic Duo SSO flow

Most Duo-protected portals follow this pattern:

```
portal URL → SAML/ADFS redirect → username/password → Duo browser health check → Duo push 2FA → destination page
```

### Step 1: Navigate to target URL

```js
const task = await useOrCreateTaskSpace('login to portal')
await openOrReuseTab('https://target-portal.example.com', { wait: true })
```

Most portals auto-redirect to their SAML/ADFS identity provider. After login, redirect back.

### Step 2: Fill credentials

After the SAML redirect lands on the login page, find the username/password fields:

```js
await fillInput('input[name="UserName"]', '<username>')
await fillInput('input[name="Password"]', '<password>')
await click('button:has-text("登录")')
```

Use `snapshotText()` first to inspect field names — they vary by IdP (ADFS, Okta, etc.).

### Step 3: Bypass Duo browser health check

Duo may show a page saying "更新 Chrome" / "Update Chrome" with a warning about outdated browser.

**→ Always click "暂时跳过" / "Skip"**, never try to update the browser. The skip button is a link-style button:

```js
await click('button.button--link')
```

The reason ego-lite triggers this: ego-lite ships a Chromium version that Duo's up-to-date detector may flag, even though it's fully functional. The skip bypass is safe and documented.

### Step 4: Handle Duo push 2FA (Manual Approval)

After the browser check, Duo sends a push to the user's registered mobile device. The Duo frameless auth page shows:

- "打开 Duo Mobile" / "Open Duo Mobile"
- "您需要打开应用以批准 Duo Push 通知…"
- "已发送至 Android" (or device name like "已发送至 iPhone")
- "正在等待批准…" / "Waiting for approval…"

**The user must manually approve on their phone** via Duo Mobile app. Push times out after ~10-15 seconds if not approved.

#### If push times out

The page shows "Duo Push 已超时" (Duo Push timed out) with a "重试" (Retry) button. Click "重试" to resend, then approve on phone.

#### Duo page rendering quirks (frameless mode)

The Duo frameless auth page may:
- Show empty `<body></body>` in browser console — content renders via sandboxed accessibility layer, not DOM
- Show blank screenshots — frameless rendering doesn't capture in standard screenshots
- Have few accessible elements — get the state with `get_app_state` (MCP) to see the actual labels/buttons in the accessibility tree

Key accessibility elements to look for after the push:
- "打开 Duo Mobile" heading (element ~20)
- "正在等待批准…" text
- "重试" button (element ~23) — only visible after timeout
- "其他选项" link (element ~26/27)

#### Common Duo page states

| State | Key accessibility text | Action |
|-------|----------------------|--------|
| Waiting for push | "打开 Duo Mobile", "正在等待批准…" | Approve on phone |
| Push timed out | "Duo Push 已超时", "重试" | Click "重试" → approve on phone |
| Update Chrome warning | "更新 Chrome", "暂时跳过" | Click "暂时跳过" |
| All methods | "其他选项" link | Click for dropdown of alternate auth methods |
| Approved & redirected | URL changes from `duosecurity.com` back to target site | Login complete |

### Step 4 (Alternate A): Handle Duo 2FA via HOTP Passcode (legacy — duo-bypass deprecated)

*Deprecated. Use Auto-2FA extension instead. This section kept for reference only.*

*Skip this section if not using duo-bypass. See `references/duo-bypass-setup.md` for full setup.*

After the browser check, instead of waiting for push:

1. At the Duo auth prompt, click **"其他选项"** (Other options) link
2. Select **"Duo Mobile 密码"** from the list of methods
3. Run the duo-bypass generator:
   ```bash
   cd /Users/minimx/duo-bypass
   ./duo_gen.py
   ```
4. Type the 6-digit code into the passcode input field
5. Submit — login proceeds immediately without phone interaction

**Pros**: Survives browser restarts, works offline, no notifications needed.
**Cons**: HOTP counter must stay in sync; re-enrollment needed if too far out of sync.

### Step 4 (Alternate B): Handle Duo push 2FA (Auto-2FA Extension)

*Skip this section if not using Auto-2FA.*

Auto-2FA (https://github.com/FreshSupaSulley/Auto-2FA) is a browser extension that registers itself as a Duo Mobile device and generates 6-digit passcodes.

**⚠️ Auto-2FA does NOT auto-approve push notifications.** Manual approval on the physical device is still required.

**When push goes to the wrong device** (e.g. shows iPhone 17 Pro instead of Ego Lite):
1. Click "其他选项" / "更多选项" link/button
2. Select **"Ego Lite"** from the device options
3. Push goes to Ego Lite, Auto-2FA generates the code, then approve manually on device

With Auto-2FA working, the push is detected within seconds. If it shows "已发送至 Android" but doesn't proceed, manually approve on your phone.

#### Critical Rule
- **Do not auto-pilot during Duo auth.** Wait for the user's explicit next-step instruction. If unsure, ask — do not assume.

#### Verify after 2FA (all modes)

```js
await wait(5)
const info = await pageInfo()
// Check url — should redirect back to the portal, not stay on duo.com
cliLog('post-2fa url: ' + info.url)
```

## Common pitfalls

- **Use ego-browser, NOT mcp_open_computer_use.** All browser interactions must use `ego-browser nodejs <<'EOF'` heredocs. mcp_open_computer_use_* tools are banned for browser tasks.
- **Do not question expected navigation.** When a site redirects (e.g. duo.itsc.cuhk.edu.hk → ADFS/sts.cuhk.edu.hk), that IS the intended flow. Do NOT report it as an error or question it. If the page has a connection error, retry first before asking the user.
- **Auto-2FA does not auto-approve push** — it's a code generator, not a push auto-approver. Manual approval on the actual device is still required.
- **Device selection matters** — if Duo pushes to iPhone 17 Pro by default, click "其他选项" → "Ego Lite". Do NOT proceed without switching devices.
- **Never preempt the user** — during Duo auth, wait for explicit step-by-step instruction. Do not fill, click, or navigate without being told. The user will say "下一步" / "点X" / "然后做Y" — do NOT assume the next step. "我说一步你做一步" is the operating rule.
- **Duo frameless auth renders visually** — `snapshotText()` may return `root > form` or near-empty DOM. Use `captureScreenshot()` for visual inspection.
- **Push timing** — push arrives 3-5s after login. Don't bail before 10s.
- **Session persists per task space** — reuse the same `useOrCreateTaskSpace` name across rounds; the session cookie lives in the task space.
- **Different Duo prompts** — Some orgs use SMS codes, phone callbacks, or WebAuthn instead of push. Check with `captureScreenshot()` if push doesn't arrive.
- **Duo may show prompt types other than push** — the frameless auth endpoint URL contains `/auth/prompt?sid=...`. The prompt type is decided by the org's Duo policy.

## Auto-2FA activation

After installing Auto-2FA (see reference), the extension activates itself when you first encounter a Duo login during a live session. It registers as a new Duo Mobile device automatically. It generates 6-digit passcodes but does **NOT** auto-approve push — manual approval on the physical device is still required.

## CUSIS (CUHK) reference

For a worked example with specific selectors and URLs, see `references/cusis-cuhk.md`.
