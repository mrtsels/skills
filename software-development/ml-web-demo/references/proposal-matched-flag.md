# Proposal matched-flag annotation (demo color semantics)

Session: bipartite-gnn-gui web demo, hero-case prep script
`scripts/prepare_demo_cases.py`.

## Symptom (user-reported)

After the coordinate-baseline fix (Pitfall 25), user said:
"你这些蓝色框框了啥我怎么没看出来" / "蓝色框的逻辑很混乱 不知道在干什么".

Cause: `proposals` in `demo_data/cases.json` carried only
`{bbox, violation_score}`. The frontend's `getMatchedBoxes()` reads
`data.gt_matches` or `proposal.matched/tp/is_tp` — none existed — so EVERY
proposal rendered as uniform blue dashed. A viewer cannot distinguish
"GNN recovered a real element" (TP) from "GNN hallucinated a box" (FP).

## Fix (prep script)

In the per-image loop, after `run_gnn(...)` and the before/after Hungarian
matches:

```python
matched_gt_indices = {j for _, j in m_a}          # after-match GT indices
proposal_list = []
for p in proposals:
    matched = any(center_distance(p.bbox, ge.bbox) <= 0.1 for ge in gt_elems)
    proposal_list.append({"bbox": [r4(v) for v in p.bbox],
                          "violation_score": r4(p.confidence),
                          "matched": matched})
missed = [[r4(v) for v in gt_elems[j].bbox] for j in fn_b]   # VLM FN -> red X
# Green boxes = the GT element's REAL bbox, not the proposal's predicted bbox.
# Using p["bbox"] here drew green boxes at the GNN's (noisy) prediction — the
# user's next complaint was "绿框错位了". Match each proposal to its nearest GT
# element and draw THAT box:
gt_matches = []
for p in proposals:
    if not any(center_distance(p.bbox, ge.bbox) <= 0.1 for ge in gt_elems):
        continue
    best = min(gt_elems, key=lambda ge: center_distance(p.bbox, ge.bbox))
    gt_matches.append([r4(v) for v in best.bbox])
```

Key trap: do NOT derive `gt_matches` from `matched_gt_indices` — that set
includes VLM's own TPs (matched BEFORE GNN ran), so green boxes would swamp
the view and the "GNN recovered N" story blurs. Use only matched PROPOSALS.
Second trap: do NOT use the proposal bbox itself as the green box — proposals
carry prediction error (MSE ~0.05–0.08); the green box must sit on the GT
element's real position or the user sees "绿框错位" again.

## Aspect-ratio mismatch: GT boxes misaligned even with correct coords

The other cause of "绿框错位": the RICO view-hierarchy resolution can differ
from the screenshot in ASPECT RATIO, not just scale. Case 10005:
RICO GT = 1440×2392 (ratio 0.602), screenshot = 1080×1920 (ratio 0.5625).
GT normalized coords are relative to 1440×2392, so mapping them onto the
1080×1920 screenshot displaces every GT box (buttons only half-covered,
boxes in empty space) — with NO bug in the frontend mapping. Diagnose by
comparing ratios, never by eye:

```python
parsed = parse_rico_vh(gt_path)          # {width, height} from root bounds
rw, rh = parsed["width"], parsed["height"]
shot_w, shot_h = Image.open(jpg).size
ok = abs(rw / rh - shot_w / shot_h) <= 1e-3
```

Fix: skip such images in the hero-case prep loop (GT coords are unusable
against that screenshot):

```python
if gt_parsed is not None:
    rw, rh = gt_parsed["width"], gt_parsed["height"]
    if abs(rw / rh - shot_size[0] / shot_size[1]) > 1e-3:
        print(f"  skip {img_id}: GT ratio {rw}x{rh} != screenshot ...")
        skipped += 1
        continue
```

Fallout after adding the filter: evaluated 200 → 128 images, hero cases
6 → 5 (10005 dropped), avg ΔF1 0.1029 → 0.1092. Check ALL hero cases for
ratio consistency — most RICO files are 1440×2560 vs 1080×1920 (both 9:16,
fine), but some are 1440×2392 or 1440×1281.

## Resulting color legend (verified in browser)

- Left pane (VLM): red solid = VLM detections; red X = `missed` GT (FN).
- Right pane (VLM+GNN): red solid = VLM detections; green solid =
  `gt_matches` (GNN proposal matched GT); blue dashed = proposals with
  `matched: false` (honest FP).

Verified pixel counts for case 10005 (Travel Booking): red 1176, green 96,
blue 295 → 4 green + 3 blue mixed case renders correctly.

Post-fix distribution across 6 hero cases: 10067/10027/10179/10033 all
proposals matched (7/5/5/8 green, 0 blue); 10005 and 1013 each have 3
unmatched proposals (blue) — honest display of imperfect proposals.
