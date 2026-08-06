# HuggingFace Model Download via Proxy (macOS, Shadowrocket)

When downloading HF/torchvision/timm models through a Chinese proxy (Shadowrocket :1082):

## Symptoms
- `transformers` `from_pretrained()` hangs for 60+ seconds
- `torchvision.models.resnet18(weights='DEFAULT')` downloads at ~600KB/s
- `pip install open-clip-torch` succeeds but `create_model_and_transforms` hangs
- Zero-byte .safetensors files in `~/.cache/huggingface/hub/` (interrupted downloads)

## Diagnostics

```bash
# Check if model is already cached
ls ~/.cache/huggingface/hub/models--facebook--dinov2-base/ 2>/dev/null
find ~/.cache/huggingface/hub/ -name "*.safetensors" -not -empty 2>/dev/null

# Test network reachability
curl -sI --max-time 10 "https://huggingface.co/facebook/dinov2-base/resolve/main/config.json"

# Check cache for corrupt partial downloads
du -sh ~/.cache/huggingface/hub/models--openai--clip-vit-base-patch32/
```

## Fixes

1. **Clean corrupt cache**:
```bash
rm -rf ~/.cache/huggingface/hub/models--<model-name>/
```

2. **Use proxy explicitly**:
```bash
http_proxy=http://127.0.0.1:1082 https_proxy=http://127.0.0.1:1082 python3 -c "from transformers import ..."
```

3. **Fallback: use whatever is already cached**:
   - `timm` models (`create_model('vit_tiny_patch16_224', pretrained=True)`) are smaller (~5MB) and download faster
   - `torchvision` models (`resnet18(weights='DEFAULT')`) are 44MB, takes ~70s at 600KB/s
   - Check `~/.cache/torch/hub/checkpoints/` for partial downloads

4. **Fallback: tiny model proof of concept**:
```python
import timm
model = timm.create_model('vit_tiny_patch16_224', pretrained=True)  # 5.7M params, 5MB
```

## Best Practice

Always check local cache before downloading. The proxy is functional but slow (600KB-1MB/s). Large models (>100MB) may time out. Use small models for proof of concept, then switch to larger ones only if needed.
