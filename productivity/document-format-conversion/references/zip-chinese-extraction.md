# Zip Extraction with Chinese Filenames (macOS)

Complete, reusable script for zips whose filenames macOS `unzip` refuses with "Illegal byte sequence".

## The Script

```python
import struct, os, shutil, zipfile

def extract_chinese_zip(zip_path: str, output_dir: str) -> list:
    """
    Extract a zip file whose filenames contain CJK characters.
    
    macOS unzip often fails with "Illegal byte sequence" because the zip
    stores UTF-8 bytes without setting bit 11 (UTF-8 flag) in the general
    purpose bit field. This function reads raw bytes from the central
    directory and tries UTF-8 → GBK → CP437 fallback decoding.
    
    Returns list of (original_raw_name, decoded_path) tuples.
    """
    os.makedirs(output_dir, exist_ok=True)
    extracted = []
    
    with open(zip_path, 'rb') as f:
        data = f.read()
    
    # Find End of Central Directory
    eocd_sig = b'\x50\x4b\x05\x06'
    eocd_pos = data.rfind(eocd_sig)
    if eocd_pos < 0:
        raise ValueError("Not a valid zip file (no EOCD)")
    
    cd_offset = struct.unpack_from('<I', data, eocd_pos + 16)[0]
    
    pos = cd_offset
    i = 0
    while pos < len(data):
        sig = data[pos:pos+4]
        if sig != b'\x50\x4b\x01\x02':
            break  # No more central directory entries
        
        filename_len = struct.unpack_from('<H', data, pos + 28)[0]
        extra_len = struct.unpack_from('<H', data, pos + 30)[0]
        comment_len = struct.unpack_from('<H', data, pos + 32)[0]
        
        raw_name = data[pos+46:pos+46+filename_len]
        
        # Auto-detect encoding
        decoded = None
        for enc in ['utf-8', 'gbk', 'cp437']:
            try:
                decoded = raw_name.decode(enc)
                break
            except (UnicodeDecodeError, LookupError):
                continue
        
        if decoded is None:
            decoded = raw_name.decode('utf-8', errors='replace')
        
        total_entry = 46 + filename_len + extra_len + comment_len
        pos += total_entry
        
        outpath = os.path.join(output_dir, decoded)
        os.makedirs(os.path.dirname(outpath), exist_ok=True)
        
        with zipfile.ZipFile(zip_path) as zf:
            zinfo = zf.infolist()[i]
            with zf.open(zinfo) as src, open(outpath, 'wb') as dst:
                shutil.copyfileobj(src, dst)
        
        extracted.append((raw_name, decoded))
        i += 1
    
    return extracted


if __name__ == '__main__':
    import sys
    if len(sys.argv) < 3:
        print(f"Usage: python {sys.argv[0]} <zip_file> <output_dir>")
        sys.exit(1)
    
    results = extract_chinese_zip(sys.argv[1], sys.argv[2])
    print(f"Extracted {len(results)} files:")
    for raw, decoded in results:
        print(f"  {decoded}")
```

## What It Handles

| Encoding | When it happens | How we detect |
|----------|-----------------|---------------|
| UTF-8 (no flag set) | macOS/Linux tools that write UTF-8 bytes but don't set bit 11 | Try UTF-8 first |
| GBK/CP936 | Windows zip tools (WinRAR, 7-Zip on Chinese Windows) | Fallback to GBK |
| CP437/OEM | Old-school zip tools | Last-resort fallback |

## After Extraction

```bash
# Clean macOS metadata
find output_dir -name '__MACOSX' -type d -exec rm -rf {} + 2>/dev/null
find output_dir -name '.~*' -delete
find output_dir -name '.DS_Store' -delete
```

## Pitfalls

1. **Central directory entry order must match zipfile.infolist() order** — they do in every well-formed zip. Malformed zips with reordered entries will fail silently (wrong content for wrong name).
2. **Large zips** — this reads the entire zip into memory (`data = f.read()`). For zips > 500MB, use mmap or streaming parser.
3. **Zips with encryption** — `zipfile.ZipFile` won't open encrypted entries without the password. This script stops at the first encrypted entry.
4. **Empty directories** — zip format stores files, not directories. Empty dirs are lost. Create them from trailing `/` entries if needed.
