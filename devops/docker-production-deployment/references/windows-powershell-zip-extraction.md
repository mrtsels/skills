# Windows PowerShell Zip Extraction for Chinese-Character Filenames

When transferring files with Chinese-character filenames from macOS to a Windows machine (e.g., via SCP/SMB → USB), standard tools fail:

- **PowerShell `Expand-Archive` cmdlet** — fails with "Illegal characters in path" on Chinese filenames from a macOS-created zip
- **Windows `tar`** — same issue, cannot decode UTF-8 encoded filenames

## Working approach: .NET API directly

```powershell
Add-Type -AssemblyName System.IO.Compression.FileSystem
[System.IO.Compression.ZipFile]::ExtractToDirectory('F:\file.zip', 'F:\')
```

This uses .NET's native `System.IO.Compression.ZipFile` class which handles UTF-8 filenames correctly.

## Full script (delete existing + extract)

```powershell
Add-Type -AssemblyName System.IO.Compression.FileSystem
if (Test-Path 'F:\target') { Remove-Item 'F:\target' -Recurse -Force }
[System.IO.Compression.ZipFile]::ExtractToDirectory('F:\file.zip', 'F:\')
```

## Creating the zip on macOS (Python, handles UTF-8 correctly)

```python
import zipfile, os

with zipfile.ZipFile('/tmp/output.zip', 'w', zipfile.ZIP_DEFLATED) as zf:
    for root, dirs, files in os.walk('.'):
        for f in files:
            zf.write(os.path.join(root, f), os.path.relpath(os.path.join(root, f), '.'))
```

Python's `zipfile` module stores filenames as UTF-8 by default, which .NET's ZipFile reads correctly.

## What NOT to use

| Tool | Result |
|------|--------|
| macOS `zip` CLI | Default encoding issues |
| PowerShell `Expand-Archive` | Fails on Chinese characters |
| Windows `tar -xf` | "Invalid empty pathname" on UTF-8 entries |
| `Compress-Archive` / `Expand-Archive` | Both broken for Chinese filenames |
