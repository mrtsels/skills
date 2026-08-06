# Auto-2FA Setup — Duo Push Code Generation via Browser Extension

> ✅ **ACTIVE (June 2026)**: Auto-2FA is re-installed and working. It generates 6-digit passcodes but does **NOT** auto-approve Duo Push — manual approval on the physical device is required. For device selection when push goes to wrong device (e.g. iPhone 17 Pro instead of Ego Lite), see the "Device Selection" section below.

## Overview

[Auto-2FA](https://github.com/FreshSupaSulley/Auto-2FA) is a browser extension that registers itself as a Duo Mobile device and generates passcodes for Duo authentication.

**Status**: Archived March 2026 but fully functional. The author graduated and lost Duo access, not a code-break reason. Works with current Duo API.

## How it works

1. **Activation**: Calls Duo's API activation endpoint, registers as an iOS/Android tablet.
2. **Code generation**: Generates 6-digit passcodes when Duo push is detected.
3. **⚠️ No auto-approval**: You must still manually approve the push on your physical device.

## Device Selection (when push goes to wrong device)

When Duo sends a Push to the wrong device (e.g. iPhone 17 Pro instead of Ego Lite):

1. At the Duo auth prompt, click "其他选项" / "更多选项" link/button
2. Select **"Ego Lite"** from the device options
3. Push will now target Ego Lite — Auto-2FA generates the passcode, then approve manually

## Build

```bash
git clone https://github.com/FreshSupaSulley/Auto-2FA.git
cd Auto-2FA
npm install
npm run build
```

Output: `.output/chrome-mv3/`

## Install into ego-lite

The native file dialog ("Load unpacked") can't be automated via ego-browser. Use --load-extension flag:

```bash
pkill -f "ego lite" && pkill -f "ego Helper" && sleep 3
mkdir -p ~/.hermes/extensions/auto-2fa
cp -R Auto-2FA/.output/chrome-mv3/* ~/.hermes/extensions/auto-2fa/
open -n -a "ego lite" --args --load-extension="$HOME/.hermes/extensions/auto-2fa"
```

Verify with `chrome.management.getAll()` — confirm `{"name":"Auto 2FA","enabled":true}`.

## Activation

After install, the extension activates on first real Duo push encounter (auto-registers). No manual setup needed.

## Limitations

- `--load-extension` is one-shot per launch, not persistent across restarts
- Auto-2FA matches `https://*.duosecurity.com/frame/*/auth/prompt*` — NOT the frameless browser-check page. Skip the browser check manually before Auto-2FA activates.
- Auto-2FA is a content script; it runs in the Duo frame, not as a background service worker override
- **Does NOT auto-approve push** — manual approval on the physical device is always needed
