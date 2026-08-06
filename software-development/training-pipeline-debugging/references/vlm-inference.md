# VLM Inference (Qwen3-VL via DashScope)

## API
- **Base URL**: `https://dashscope.aliyuncs.com/compatible-mode/v1`
- **Format**: OpenAI-compatible
- **Key**: `DASHSCOPE_API_KEY` in `.env`
- **Script**: `scripts/generate_vlm_predictions.py`

## Models
- `qwen3-vl-plus`: default, ~10 img/min (4 workers)
- `qwen3-vl-flash`: faster, slightly lower quality

## Batch (490 images, 4 workers)
- 489 OK, 6 errors (timeout/parse), 7,312 elements, 15/img
- 46 min total. Timeouts are normal — 3x retry with backoff.

## Training with --vlm-dir
1. Load VLM JSON by image stem
2. Hungarian match VLM→GT (IoU 0.3)
3. Build graph from VLM elements + GT constraints
4. Delta targets for matched pairs, zero-existence for unmatched