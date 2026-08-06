# GUI Element Detection Datasets — Survey (2026-06)

## Dense (15+ elts/img) — Good for GNN

| Dataset | Downloads | Notes |
|---------|:---------:|-------|
| RICO (local) | — | Mobile, 66K screens, median 88 elts/img, view hierarchy GT |
| GUI-360 (vyokky/GUI-360) | 335K | 3.5K screens, ~14 elts/img |
| GUI-Odyssey (OpenGVLab) | 29K | 99K files, GUI interaction trajectories |

## Sparse (2-10 elts/img) — Limited GNN utility

| Dataset | Downloads | Notes |
|---------|:---------:|-------|
| ScreenSpot (Voxel51, bevaya) | 1-3K | PC/web, ~2 elts/img, too sparse |
| ScreenSpot v2 (Voxel51) | 4K | Updated version |
| ScreenSpot Pro (likaixin) | 10K | Most popular ScreenSpot variant |

## Other Related

| Dataset | Downloads | Description |
|---------|:---------:|-------------|
| Voxel51/rico | 6.9K | RICO in FiftyOne format |
| RICO-WidgetCaptioning | 48K | Widget captions on RICO |
| Widget2Code (Djanghao) | 1.6K | GUI→HTML code pairs |

## Recommendation

- Best new dataset: GUI-Odyssey (check for spatial annotations)
- For cross-domain: ScreenSpot v2 / Pro (may be denser than original)
- VLM predictions must be generated separately — most datasets provide GT only
