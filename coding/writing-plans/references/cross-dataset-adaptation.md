# Cross-Dataset Domain Adaptation (GNN + VLM Pseudo-GT)

## Problem

A GNN trained on one dataset (e.g., RICO mobile screens) may not generalize to
another domain (e.g., ScreenSpot PC/web screens) due to:
- Different element density (22 elem/img → 2.1 elem/img)
- Different spatial layout patterns
- Different annotation style (view hierarchy vs. reference annotations)

## Solution: VLM Pseudo-GT Fine-Tuning

### Protocol

1. **Generate VLM predictions on target dataset**
   - Run Qwen3-VL Flash (or equivalent) on target images
   - Expect ~15-25 elements per image (much denser than manual annotations)
   - Save in same format: `{image_id, image_width, image_height, elements: [{bbox_xyxy, label, text}]}`

2. **Use VLM predictions as pseudo-GT**
   - Treat VLM outputs as if they were ground-truth layouts
   - Apply the same self-supervised training (random drop + violation detection)
   - The GNN learns target-domain layout patterns from VLM's detections

3. **Fine-tune RICO-trained model**
   - Start from the source-domain checkpoint (not from scratch)
   - Low learning rate (5e-5 vs. 1e-3 for training from scratch)
   - 20-30 epochs on target (fewer than full training 50-100 epochs)

4. **Evaluate**
   - Pre-fine-tuning: measure target-domain accuracy before adaptation
   - Post-fine-tuning: measure gain
   - Compare: source-domain baseline → target-domain zero-shot → adapted

### Expected Results

| Stage | Violation Acc |
|-------|--------------|
| Source-trained on target (zero-shot) | ~37% (near random, scores ~0.53, all predicted violated) |
| Fine-tuned on target pseudo-GT | ~69% (recovers ~3/4 of source-domain accuracy) |

### Pitfalls

- **VLM errors become pseudo-GT errors** — if VLM misses elements, those errors
  propagate into training. Acceptable because VLM still captures the dominant
  spatial patterns of the target domain.
- **Sparse target annotations don't matter** — VLM produces denser detections
  than manual annotations. Use VLM detections, not the sparse GT.
- **Learning rate too high** — the model forgets source-domain patterns.
  Start low (5e-5) and track validation loss for early stopping.
- **Cross-dataset zero-shot is always worse** — structural GNN patterns are
  domain-specific. Expect drop when source and target have different element
  densities (2x → 10x fewer elements per image).

### Tools

Project scripts:
- `scripts/generate_screenspot_predictions.py` — VLM inference on ScreenSpot
- `experiments/finetune_screenspot.py` — fine-tuning pipeline
- `experiments/cross_dataset.py` — side-by-side RICO vs. fine-tuned eval
