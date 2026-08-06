# PlantUML Rendering via Web API

Two common failures when rendering PlantUML from a script:

## Failure 1: Error Page Instead of Diagram

The server returns an HTML error page saying "Plugin you are using seems to generated a bad URL. This URL does not look like HEIFANO data."

**Cause:** Wrong encoding. The compressed data must use **raw deflate** (no zlib header/trailer), and the encoded string must be prefixed with `~1`.

**Fix:**
```python
import zlib

ALPHABET = "0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz-_"

def puml_encode(text):
    # Raw deflate: wbits=-15 (no zlib header)
    compress = zlib.compressobj(9, zlib.DEFLATED, -zlib.MAX_WBITS)
    raw = compress.compress(text.encode('utf-8')) + compress.flush()
    
    # Custom base64 encoding
    result = []
    i = 0
    while i < len(raw):
        if len(raw) - i >= 3:
            b = (raw[i] << 16) | (raw[i+1] << 8) | raw[i+2]
            result += [ALPHABET[(b >> 18) & 0x3F], ALPHABET[(b >> 12) & 0x3F],
                       ALPHABET[(b >> 6) & 0x3F], ALPHABET[b & 0x3F]]
            i += 3
        elif len(raw) - i == 2:
            b = (raw[i] << 16) | (raw[i+1] << 8)
            result += [ALPHABET[(b >> 18) & 0x3F], ALPHABET[(b >> 12) & 0x3F],
                       ALPHABET[(b >> 6) & 0x3F]]
            i += 2
        else:
            b = (raw[i] << 16)
            result += [ALPHABET[(b >> 18) & 0x3F], ALPHABET[(b >> 12) & 0x3F]]
            i += 1
    return '~1' + ''.join(result)

# Then:
url = 'https://www.plantuml.com/plantuml/png/' + puml_encode(source)
```

## Failure 2: Using `strip()` incorrectly on zlib output

```python
# ❌ Wrong: stripping bytes breaks the deflate stream
compressed = zlib.compress(text.encode('utf-8'))[2:-4]  # ← corrupt

# ✅ Correct: use raw deflate with wbits=-15
compress = zlib.compressobj(9, zlib.DEFLATED, -zlib.MAX_WBITS)
raw = compress.compress(text.encode('utf-8')) + compress.flush()
```

## URL Verification

A successful render produces a PNG with header `89504E47`. An error page is an HTML document. Check with:
```bash
xxd output.png | head -1
# 00000000: 8950 4e47 0d0a 1a0a  ← valid PNG
# 00000000: 3c21 444f 4354 5950  ← HTML error page
```
