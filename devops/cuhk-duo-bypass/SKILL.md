---
name: cuhk-duo-bypass
description: Use revalo/duo-bypass Python scripts to generate Duo 2FA HOTP passcodes for CUHK, replacing extension-based auto-approval.
---

# CUHK Duo 2FA via duo-bypass

**⚠️ SUPERSEDED (June 2026):** Auto-2FA extension now handles code generation instead. The Ego Lite device in Duo Device Management serves Auto-2FA. Keep this skill for reference only — do NOT use duo_gen.py unless Auto-2FA fails.

When the user needs to pass Duo 2FA authentication at CUHK (duo.itsc.cuhk.edu.hk), use this manual passcode approach instead of waiting for push approval.

## Setup (one-time)

```bash
cd ~ && git clone https://github.com/revalo/duo-bypass.git
cd duo-bypass && pip install -r requirements.txt
```

## First-time enrollment (one-time per device)

1. In ego-lite, navigate to Duo Device Management (via duo.itsc.cuhk.edu.hk → log in via ADFS OnePass → tick checkbox → "Go to Enroll/Manage Devices")
2. Click "添加设备" → "Duo Mobile" → "我有平板电脑"
3. The page shows a QR code. Click "改为获取激活链接" to see the activation URL, or copy the QR image URL directly
4. Extract host and code from the activation URL: `https://HOST/activate/CODE`
5. Run activation with app_version=5.0.0 (older versions rejected as deprecated):

```bash
cd ~/duo-bypass
python3 -c "
import requests, json, base64
from Crypto.PublicKey import RSA
host = 'HOST'  # e.g. m-08dc11c9.duosecurity.com
code = 'CODE'  # e.g. Q9Agl5rLzw6A07eRoLjS

# Actually use api- version of host
api_host = host.replace('m-', 'api-', 1)
url = f'https://{api_host}/push/v2/activation/{code}?customer_protocol=1'
headers = {'User-Agent': 'okhttp/2.7.5'}
data = {'pkpush': 'rsa-sha512', 'jailbroken': 'false', 'architecture': 'arm64',
        'region': 'US', 'app_id': 'com.duosecurity.duomobile',
        'full_disk_encryption': 'true', 'passcode_status': 'true',
        'platform': 'Android', 'app_version': '5.0.0',
        'app_build_number': '500001', 'version': '15',
        'manufacturer': 'unknown', 'language': 'en', 'model': 'Pixel 9 Pro',
        'security_patch_level': '2025-06-01'}
data['pubkey'] = RSA.generate(2048).public_key().export_key('PEM').decode()

r = requests.post(url, headers=headers, data=data, timeout=15)
resp = json.loads(r.text)
akey = resp['response']['akey']
print(f'akey: {akey}')
with open('duotoken.hotp', 'w') as f:
    f.write(akey + '\n0')
"
```

## Generate a passcode (every time you need 2FA)

```bash
cd ~/duo-bypass && python3 duo_gen.py
# Output: "Code: XXXXXX"
```

## Enter the passcode

In the Duo "输入密码" page: type the 6-digit code into the text field, click "验证".

## Pitfalls

- Activation codes are one-time use. If you get "Unknown activation code" (40403), the code was already consumed or expired.
- The `m-` host in the activation URL must be replaced with `api-` for the API call.
- Duo version 3.49.0 and 4.x are rejected as deprecated — use 5.0.0 or check `current_app_version` in the response for the latest supported version.
- HOTP uses a counter. Each `duo_gen.py` call increments it. If you generate codes without using them, the counter gets out of sync with the server and codes will be rejected. To fix: delete duotoken.hotp and re-enroll.
