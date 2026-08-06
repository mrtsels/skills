# Phase 11 Web Demo — Session Reference

> 2026-07-20 · Bipartite-GNN-GUI project · bipartite-gnn-gui
> Updated 2026-07-21 — Added JSON comparison mode and corrected_json

## Model

- Checkpoint: `checkpoints/violation_detection/screenspot_finetuned.pt`
- Format: `{'model': state_dict, 'val_loss': float}`
- Architecture: `BipartiteGNNCorrector(element_dim=5, constraint_dim=11, hidden_dim=128, num_layers=2)`
- Params: 220,439
- Element features: 5-d ([x1, y1, x2, y2, confidence]), no visual features
- Constraint features: 11-d (10 one-hot + 1 param)

## Checkpoint Dimension Analysis

| Checkpoint | hidden_dim | element_dim | Has fusion? |
|------------|:----------:|:-----------:|:-----------:|
| `violation_detection/best_model.pt` | 16 | 5 | No |
| `violation_detection/visual_fusion_model.pt` | 128 | 197 | No (concat) |
| `violation_detection/screenspot_finetuned.pt` | 128 | 5 | No |
| `confidence_scoring/best_model.pt` | — | 5 | No |

**Key insight:** `best_model.pt` has hidden_dim=16 (very small). The
`screenspot_finetuned.pt` version has hidden_dim=128 and is fine-tuned on
real data — much better for a demo.

## Model Behaviour on Synthetic Data

5 elements, 7 constraints, 3 violations, 3 proposals in 1.8ms (CPU).

- Existence scores: ~0.45 on non-RICO data (below 0.5 threshold)
- Violation scores: mostly 0.2–0.4, one grid constraint at 0.50
- Proposal bboxes: xywh format from model output, convert to xyxy for display
- Proposal types: logits over 20 element types

## VLM API Details

- Endpoint: `https://dashscope.aliyuncs.com/compatible-mode/v1/chat/completions`
- Models: `qwen3-vl-flash` (fast, ~2s), `qwen3-vl-plus` (accurate, ~5s)
- Auth: Bearer token from `DASHSCOPE_API_KEY` env var
- System prompt instructs JSON array of `{bbox_xyxy, label, text}` output
- Latency: 2–5s per image
- Retry: 3 attempts with 2s exponential backoff

## Python Path

The system has multiple Python installations:
- `/usr/local/bin/python3` — framework Python with pip-installed packages
- Conda base env — no packages (conda uses plugins that may fail)

Always verify with: `which python3 && python3 -c 'import fastapi'`

## Frontend Architecture

- Single file: `web/index.html` (~20KB)
- 6 sections: config bar, upload zone, action bar, loader/error, results, stats
- No CDN, no build tools, no frameworks
- Responsive: 2-column → 1-column at 720px breakpoint
- Resize handler debounced at 300ms

### Display Mode: JSON Comparison (added 2026-07-21)

User explicitly rejected the canvas overlay in favor of JSON comparison view.

**Frontend changes:**
- Replace `<canvas>` with `<pre><code>` code panels in dark theme (`#1e1e2e`)
- Left panel: raw VLM JSON (`data.vlm.elements`)
- Right panel: corrected JSON (`data.corrected_json.elements`)
- Remove legend, canvas drawing JS, resize handler for canvas
- Render via `JSON.stringify(obj, null, 2)` into `textContent`

**Backend changes:**
- Add `build_corrected_json()` method to `DemoPipeline`:
  - Annotates original VLM elements with `existence_score` from GNN
  - Appends GNN proposals tagged with `source: "gnn_proposal"`
  - Returns `{ elements, total_count, vlm_count, gnn_proposals_count }`
- Include `corrected_json` in both `/api/predict` and `/api/gnn-only` responses
- Always return both `overlay_b64` and `corrected_json` — frontend decides which to render

## API Key Handling (env var pattern)

The demo reads `DASHSCOPE_API_KEY` from environment — no frontend input field.

**Backend:**
```python
from pathlib import Path
from dotenv import load_dotenv

_env_path = Path(__file__).resolve().parent.parent / ".env"
load_dotenv(_env_path)
# Then: os.environ.get("DASHSCOPE_API_KEY", "")
```

**.env format** (shell `export` syntax, not dotenv format):
```
export DASHSCOPE_API_KEY="sk-ws-..."
```

**Rationale:** User explicitly said demo should not require manual key entry. The key is set once in `.env` (gitignored) and picked up automatically.

## HEIC Handling

Two problems with HEIC uploads, both fixed:

**a) Backend PIL can't open HEIC.** Add `pillow-heif` and call `register_heif_opener()`.
**b) Frontend canvas can't render HEIC blob URLs.** Even with PIL decoding on the server, `URL.createObjectURL(file)` creates a HEIC blob URL that browsers can't draw on `<canvas>`. Fix: backend converts the source image to JPEG base64 (`image_b64`), frontend draws from that instead of the blob URL.

## API Response Format

```json
{
  "vlm": {
    "elements": [{"bbox_xyxy": [10,20,100,50], "label": "button", "confidence": 0.9}],
    "count": 12,
    "time_ms": 2340
  },
  "gnn": {
    "proposals": [{"bbox": [0.1,0.2,0.3,0.4], "violation_score": 0.55, "predicted_type": "button"}],
    "constraints_count": 45,
    "violations_count": 3,
    "proposals_count": 3,
    "time_ms": 20.3
  },
  "overlay_b64": "data:image/png;base64,...",
  "image_b64": "data:image/jpeg;base64,...",
  "corrected_json": {
    "elements": [
      {"bbox": [10,20,100,50], "label": "button", "source": "vlm", "existence_score": 0.45},
      ...
      {"bbox": [0.1,0.22,0.4,0.5], "label": "text", "source": "gnn_proposal",
       "confidence": 0.55, "constraint_type": "grid"}
    ],
    "total_count": 15,
    "vlm_count": 12,
    "gnn_proposals_count": 3
  },
  "dimensions": {"width": 480, "height": 800}
}
```

The `corrected_json.elements` array merges original VLM elements (with
`existence_score`) and GNN proposals (with `source: "gnn_proposal"`).
This single list is what the JSON comparison view renders.
