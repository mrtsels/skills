# Windows .lnk Shortcut Parsing (Python)

Windows shortcut (.lnk) files can point to SMB network paths (\\server\share\folder). Useful when the user has a .lnk on a mounted SMB share and you need to find the actual target.

## Quick Script

```python
import struct

with open("shortcut.lnk", "rb") as f:
    data = f.read()

# Extract UTF-16LE strings from the binary
texts = []
i = 0
while i < len(data) - 1:
    if data[i] != 0 and data[i+1] == 0:
        j = i
        while j < len(data) - 1 and not (data[j] == 0 and data[j+1] == 0):
            j += 2
        if j > i:
            s = data[i:j].decode('utf-16-le', errors='replace')
            if len(s) > 3 and all(ord(c) < 0x10000 for c in s):
                texts.append(s)
        i = j + 2
    else:
        i += 1

# Filter for network paths
for t in texts:
    if any(kw in t for kw in ['\\\\', '\\', 'PC', 'DESKTOP', 'Users']):
        print(repr(t))
```

## What to Look For

The target SMB path appears as a raw UNC string:

```
\\\\SERVER\\SHARE\\path\\to\\target
```

Chinese characters in share/folder names are preserved correctly in UTF-16LE.

## Caveats

- `file` command on macOS identifies .lnk correctly: `MS Windows shortcut, Points to a file or directory`
- Use `--noproxy '*'` for curl/mount if the .lnk points to an internal IP
- Mount the target share separately — .lnk just tells you where, it doesn't mount it
