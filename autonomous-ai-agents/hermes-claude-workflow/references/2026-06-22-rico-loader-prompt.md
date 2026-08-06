# RICO Data Loader Prompt (2026-06-22)

**Context:** Bipartite GNN for GUI Correction. New module to parse RICO dataset View Hierarchies.
**Model:** `deepseek-v4-pro`
**Worktree:** Independent git worktree for isolation

## Prompt Structure

```
TASK: RICO Data Loader — create a new module to parse RICO dataset View Hierarchy JSONs.

CONTEXT:
You are in a WORKTREE at /tmp/bgg-worktree/feat/rico-loader/

Read ALL these files:
- CLAUDE.md
- src/bipartite_gnn_gui/data/ground_truth.py
- src/bipartite_gnn_gui/data/vlm_output.py
- src/bipartite_gnn_gui/data/dataset.py
- src/bipartite_gnn_gui/data/__init__.py
- docs/requirements/gt_format.md (see §3.5 RICO Dataset)
- src/bipartite_gnn_gui/utils/bbox.py

The .venv is at /Users/minimx/bipartite-gnn-gui/.venv/

RICO FORMAT:
View Hierarchy JSON with recursive tree, each node:
{
  "bounds": "[x1,y1][x2,y2]",
  "class": "android.widget.Button",
  "text": "Submit",
  "content-desc": "",
  "visibility": "visible",
  "children": [...]
}

WHAT TO IMPLEMENT:
- parse_rico_view_hierarchy(vh_path, images_dir) -> GroundTruth
- parse_rico_semantic(ann_path) -> GroundTruth
- rico_class_to_type(android_class) -> str
- load_rico_directory(rico_dir) -> list[GroundTruth]
- Tests for all functions

GIT WORKFLOW:
[commit + push + PR]
```

## Post-Implementation Correction: Actual Data Format Differs

The loaded skill's `gt_format.md` assumed one format, but the actual downloadable RICO data (`unique_uis.tar.gz`, 6 GB from Google Cloud Storage) uses a different structure:

**Actual unique_uis format (flat `combined/` directory):**
```
combined/
  68068.json        # View Hierarchy JSON
  42231.jpg         # Screenshot (JPG not PNG!)
  29706.jpg
  ...
```

**Actual JSON structure (differs from docs):**
```json
{
  "activity_name": "com.example.MainActivity/com.example.Activity2",
  "activity": {
    "root": {
      "bounds": [0, 0, 1440, 2392],       // Array, NOT string "[x1,y1][x2,y2]"
      "class": "android.widget.FrameLayout",
      "visibility": "visible",
      "children": [
        {
          "class": "android.widget.LinearLayout",
          "bounds": [0, 0, 1440, 2392],
          "text": null,                     // null, not ""
          "content-desc": [null],           // Array of nulls, not empty string
          "visibility": "visible",
          "clickable": false,
          "enabled": true,
          "ancestors": ["android.widget.FrameLayout", "android.view.ViewGroup", ...],
          "children": [...]
        }
      ]
    },
    "added_fragments": [...],
    "active_fragments": [...]
  },
  "is_keyboard_deployed": false,
  "request_id": "xxx"
}
```

**Key differences from documented assumptions:**
| Field | Docs Assumed | Actual |
|-------|-------------|--------|
| `root` location | Top-level `root` key | Nested under `activity.root` |
| `bounds` format | String `"[0,0][1440,2392]"` | Array `[0, 0, 1440, 2392]` |
| `screen_width` | Separate field | `root["bounds"][2]` |
| `screen_height` | Separate field | `root["bounds"][3]` |
| `content-desc` | String | Array `[null]` or `["some text"]` |
| `text` | String (empty if none) | String or `null` |
| Image format | PNG | JPG (.jpg, not .png) |
| Directory structure | Per-app `com.example.app/` | Flat `combined/` with numeric filenames |
| `children` absence | No children key or empty | No children key = leaf; empty list = leaf |

**Semantic Annotations format** (`semantic_annotations.zip`, 150 MB, from `storage.googleapis.com` not `storage.cloud.google.com`):
- Already extracted and available at `data/raw/rico/semantic_annotations/`
- Flatter format: root object IS the tree root (no `activity` wrapper)
- Uses `componentLabel` key for semantic type (Icon, Text, Drawer, etc.)
- Same numeric IDs as unique_uis format — images at `semantic_annotations/68068.png`

**Loader fix needed:** The `rico_loader.py` written from prompts assumes the DOCUMENTED format. After RICO data is extracted to `data/raw/rico/combined/`, the loader needs updating to match actual format. Key changes:
1. Bounds parsing: use raw `list[int]` no regex
2. Screen dimensions: `root["bounds"][2]` and `root["bounds"][3]`
3. Top-level access: `data["activity"]["root"]` not `data.get("root")`
4. Content-desc: `node.get("content-desc", [None])[0]`
5. Text: handle `null` → `None`
6. Images: `.jpg`, not `.png`
7. Directory loading: `combined/` flat glob, not per-app recursion

## Risks

| Risk | Mitigation |
|------|------------|
| RICO data still downloading | Write loader with synthetic test data first; test on real data when download completes |
| Memory limit with 66K View Hierarchies | Load one at a time, don't hold all in memory |
| Some View Hierarchies may have malformed bounds | Robust regex + error handling per element (skip, don't crash) |
