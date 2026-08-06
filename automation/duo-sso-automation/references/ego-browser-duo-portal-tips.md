# Duo Portal + ego-browser Tips

## `click('@N')` fails on Duo portal buttons

The CUHK Duo portal's "Go to Enroll/Manage Devices" button is an `<input type="button">` with inline `onclick`, not a `<button>` element. `snapshotText()` reports it as "button" but `click('@N')` emits real mouse events that don't trigger the inline `onclick` handler.

**Symptoms:** clicking `@ref` appears to do nothing — page stays the same.

**Fix — use `js()` to directly invoke the onclick:**
```js
// Step 1: tick the checkbox via JS
await js(String.raw`document.getElementById('chkPresentation').checked = true`)
await js(String.raw`typeof persuedPresentation === 'function' && persuedPresentation()`)

// Step 2: enable and click the button via JS
await js(String.raw`document.getElementById('btnManageDevices').disabled = false`)
await js(String.raw`document.getElementById('btnManageDevices').style.filter = 'none'`)
await js(String.raw`document.getElementById('btnManageDevices').click()`)
```

**Probe first:** When `click('@N')` doesn't work, check the element type:
```js
const html = await js(String.raw`document.querySelector('form').innerHTML`)
cliLog('form html: ' + html)
```

## Duo portal flow (CUHK specific)

1. `https://duo.itsc.cuhk.edu.hk` → redirects to CUHK ADFS (sts.cuhk.edu.hk) — this IS correct, do NOT question it
2. After ADFS login, lands on enrollment page with checkbox + "Go to Enroll/Manage Devices"
3. Clicking that button triggers Duo frameless auth (push to default device, or passcode if configured)
4. After Duo auth, redirects back to Duo Device Management page

## `ERR_TUNNEL_CONNECTION_FAILED`

This error is transient when behind a VPN/proxy (Shadowrocket). **Just retry** — the same URL works on the second attempt. Do not over-diagnose.
