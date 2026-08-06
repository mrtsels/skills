# ScreenSpot Data Adapter Prompt (2026-06-22)

**Context:** Bipartite GNN for GUI Correction project. Screenshot-level task within Phase 4.
**Model:** `deepseek-v4-pro` (user requested `--model opus`, mapped per CCX routing rule)
**Worktree:** Independent git worktree for isolation

## Prompt Structure

```
TASK: ScreenSpot Data Adapter — make the existing ground_truth loader handle the actual
ScreenSpot data format on disk.

CONTEXT:
You are in a WORKTREE at /tmp/bgg-worktree/feat/screenspot-adapter/

Read ALL these files for context before coding:
- src/bipartite_gnn_gui/data/ground_truth.py
- src/bipartite_gnn_gui/data/dataset.py
- src/bipartite_gnn_gui/data/vlm_output.py
- src/bipartite_gnn_gui/utils/bbox.py
- docs/requirements/gt_format.md
- configs/default.yaml
- tests/test_data_ground_truth.py
- tests/test_data_dataset.py

The .venv is at /Users/minimx/bipartite-gnn-gui/.venv/

REAL DATA (mounted via SMB, read-only):
- data/raw/screenspot/ScreenSpot_combined.json — ARRAY of 610 entries
  Each: {"image": "...", "annotations": [{"bounding_box": [x,y,w,h], "data_type": "...", ...}]}

CURRENT GAP:
load_screenspot_annotation() expects per-image dicts with {image_id, image_width, image_height, ...}.
Real data is a combined JSON array with xywh bbox + different field names.

WHAT YOU NEED TO DO:
1. Add load_screenspot_combined(path, images_dir) — reads array, opens PNGs for dims,
   converts xywh→xyxy, maps field names
2. Update load_ground_truth() factory to dispatch
3. Update GUIDataset._build_cache() and _resolve_gt_path() for combined JSON
4. Write comprehensive tests

VERIFY:
1. .venv/bin/python -m pytest tests/test_data_ground_truth.py -v
2. .venv/bin/python -m pytest tests/test_data_dataset.py -v
3. .venv/bin/python -m pytest tests/ -v

GIT WORKFLOW:
cd /tmp/bgg-worktree/feat/screenspot-adapter
git add ... && git commit -m "data: adapt ScreenSpot loader for combined JSON format"
git push origin feat/screenspot-adapter
gh pr create --title "data: adapt ScreenSpot data loader for combined JSON format" --body "..."
```

## Key Design Decisions

1. **PIL for image dimensions** — JSON lacks `image_width`/`image_height`, so open each `.png` to read actual pixel dims. Caching the result is a future optimisation.
2. **xywh→xyxy** — `[x, y, w, h]` → `[x, y, x+w, y+h]`, then normalise by image dims.
3. **Field mapping** — `bounding_box`→`bbox`, `data_type`→`type`, `objective_reference`→`text`, `data_source`→`group`.
4. **Combined JSON detection** — `load_ground_truth()` checks if input is a list (array) instead of dict, then dispatches to new loader.

## Risks

| Risk | Mitigation |
|------|------------|
| PNG I/O on every call | Handled at build time (cache build), not on every epoch |
| Image dims may be inconsistent with JSON origin | Pick one source as ground truth (the PNG) |
| Combined JSON has 610 entries — single file load | One-time load, fine for dataset init |
