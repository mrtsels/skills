# qwen3-vl-flash Coordinate Baseline Bug (2026-07-31)

## Symptom

User: "红框位置和元素实际位置完全不符" / "红框之间的相对位置对，但是整体没有拉伸充满整张截图" —
all VLM bboxes on the web demo sat in the top half of the screenshot, relative
layout preserved but not stretched to fill the image.

## Root cause

`generate_vlm_predictions.py` stores the ORIGINAL image size in the JSON:

```python
img_w, img_h = _get_image_size(image_path)
output = {"image_width": img_w, "image_height": img_h, "elements": ...}
```

But the qwen3-vl-flash API internally resizes EVERY input to a fixed
1080×960 frame and returns bbox coordinates in THAT frame. Normalizing by
1080×1920 halved all y coordinates → boxes covered only the top ~48% of the
image.

## Evidence chain (do these in this order next time)

1. **Stat the coordinate range across ALL prediction files:**

```python
import json, glob
for f in sorted(glob.glob('data/vlm_predictions/rico_qwen_flash/*.json'))[:20]:
    d = json.load(open(f))
    xs2 = [e.get('bbox_xyxy') or e.get('bbox') or [0,0,0,0] for e in d['elements']]
    ...
    # key number: max_y2 / claimed image_height
```

Result: all 200 files had coords within 1080×960; y_max ≈ 907-926 while
claimed height = 1920 → y_max/1920 ≈ 0.47, y_max/960 ≈ 0.95. The 960 baseline
is the tell.

2. **Live API probe with a differently-sized input.** Sending the 540×960
   image `100.jpg` returned x_max=974 → 974/540 = 1.80 (impossible for a
   540-wide frame) while 974/1080 = 0.90 (clean). Proves the frame is fixed
   at 1080 wide, independent of input size.

3. **A/B render on one image:** draw raw coords (baseline = 1080×1920) vs
   y*2 mapped coords (baseline = 1080×960) on the same screenshot. Vision
   check confirmed the y*2 variant aligns with status bar, "View us LIVE",
   62° temperature; the raw variant is shifted up/smaller. This is the
   decisive visual confirmation.

## Fix

Normalize by the VLM frame constant everywhere, ignore JSON image size:

```python
VLM_COORD_W, VLM_COORD_H = 1080, 960
x1, x2 = x1 / VLM_COORD_W, x2 / VLM_COORD_W
y1, y2 = y1 / VLM_COORD_H, y2 / VLM_COORD_H
```

Files patched in this project:
- `api/pipeline.py` — `_vlm_json_to_element_nodes` (also added `bbox_2d`
  fallback — the live API used that field name)
- `api/main.py` — `_normalized_elements`
- `scripts/prepare_demo_cases.py` — `load_vlm_elements`
- `scripts/visualize_demo_cases.py` — `load_vlm`

## Aftermath

- Red boxes went from 48% → 96% screenshot height coverage (verified via
  vision on the live page and by `max(ys)/1920` in the data).
- Hero-case selection dropped 12 → 6: previous TPs included fake matches
  from loose matching threshold (0.1 = 192px on a 1920-tall image) against
  misaligned boxes. 6 survivors all had ΔTP≥4, ΔFP≤5.
- 942 tests still pass; upload mode also fixed (same normalizer).

## Side lesson

"Numbers round-trip losslessly" (raw px → normalized → back to px) does NOT
prove visual correctness — the bug was in the data source baseline, and every
conversion step was internally consistent. Always validate rendered output
against the actual image, not just arithmetic consistency.
