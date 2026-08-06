# Model Asset Size Reference

Reference sizes from a Mac16,8 (M3 Max, macOS 27.0 26A5378n) with RegionSpoof kext active.

## Actual Measurements

| Directory | Size | Notes |
|-----------|------|-------|
| `com_apple_MobileAsset_UAF_FM_GenerativeModels` | ~20 GB | Core generative models |
| `com_apple_MobileAsset_UAF_FM_Visual` | ~3.0 GB | Visual models (Image Playground) |
| `com_apple_MobileAsset_UAF_FM_CodeLM` | ~4.9 GB | Code language model |
| `com_apple_MobileAsset_UAF_FM_Overrides` | ~6.5 MB | Config overrides |
| **Total** | **~27.96 GB** | As measured on this machine |

## Context

- Full expected size: ~30 GB+ (some assets may be downloaded incrementally or vary by model type)
- 27.96 GB = ~93% complete — sufficient for most models to be operational
- Missing ~2-3 GB typically includes `ModelCatalog` or other incremental packages
- Model size being sub-full does NOT cause 32080 — it only affects feature availability for specific model capabilities

## Detection Path

The diagnose script finds models at:
```
/System/Library/AssetsV2/com_apple_MobileAsset_UAF_FM_*
```

The find patterns:
```bash
find /System/Library/AssetsV2 -maxdepth 1 -type d \( \
  -iname '*Generative*' -o \
  -iname '*UAF_FM*' -o \
  -iname '*Visual*' -o \
  -iname '*CodeLM*' -o \
  -iname '*ModelCatalog*' \
\) -print0 | xargs -0 du -sk
```

Exact size command:
```bash
kb=$( { find /System/Library/AssetsV2 -maxdepth 1 -type d \
  \( -iname '*Generative*' -o -iname '*UAF_FM*' -o \
     -iname '*Visual*' -o -iname '*CodeLM*' -o \
     -iname '*ModelCatalog*' \) -print0 2>/dev/null \
  | xargs -0 du -sk 2>/dev/null; } \
  | awk '{s+=$1} END{print s+0}')
awk "BEGIN{printf \"%.3f GB\\n\", $kb/1024/1024}"
```
