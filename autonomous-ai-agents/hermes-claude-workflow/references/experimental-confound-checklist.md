# Experimental Confound Checklist

## The Lesson

When comparing two experimental conditions, verify you're not changing multiple variables simultaneously. A single comparison with two changed variables cannot be attributed to either one.

## History

This session's two-model comparison originally changed **two variables at once**:
1. Constraint type set (CONTAINMENT-only vs full)
2. Head configuration (violation-only vs joint)

Result: "CONTAINMENT-only + violation-only = 98.9% > Full + joint = 88.8%"
Problem: Which variable caused the improvement? Unknown.

The critical reviewer caught this: "The comparison is fundamentally confounded by TWO variables simultaneously."

## Minimum Checklist

Before reporting any comparison result, check:

- [ ] **One variable changed**: does this comparison differ in exactly one dimension?
- [ ] **Control group**: is there a baseline that differs only in the variable of interest?
- [ ] **Confounders listed**: are any external variables (dataset size, validation set composition, training budget) different between conditions?

## Template

When designing a controlled experiment:

```
Condition A: {baseline} × {config X}
Condition B: {baseline} × {config Y}
                  ^        ^
                  Only Y changes from A. Everything else (seed, data, epochs, head config) is identical.
```

## Common Confounds in ML Research (from this project)

| Apparent Finding | Actual Confound |
|-----------------|----------------|
| "CONTAINMENT-only > full types" | Fewer constraints to predict (977 vs 3,326), different positive/negative ratio |
| "Two-model strategy > joint" | Two variables changed simultaneously (constraint type + head config) |
| "Type prediction impossible" | Incoherent training target (multiple elements → averaged bbox but single type label) |
| "Cross-domain fine-tune works" | VLM pseudo-GT evaluation is circular — training and test both from same VLM |
| "Cross-domain confidence fails" | Target distribution too different: ScreenSpot avg 2.1 elements vs RICO avg 25; VLM over-detects 17:1 ratio |
| "DINOv2 > vit_tiny for visual features" | **Wrong assumption** — 86M params / 768-dim features gave IDENTICAL results to 5.7M / 192-dim. Task bottleneck is structural, not visual quality. "Bigger encoder = better" is not guaranteed in multi-modal fusion.
| "Proposal-only > joint for proposal" | **Wrong assumption** — joint training HELPS proposal head (MSE 0.058 vs 0.062). Multi-task is asymmetric: violation head benefits from isolation (−2.2pp in joint), proposal head benefits from sharing. Always test both directions before claiming "multi-task hurts." |

## Multi-Task Asymmetry Finding

Multi-task effects are not symmetric across heads:

```
Violation head: joint < single-task  (0.876 vs 0.898, hurts −2.2pp)
Proposal head:  joint > single-task  (0.058 vs 0.062, helps)
```

**Do NOT conclude "multi-task bad" without testing every head individually.**

## Training Target Coherence Check

**Before training any multi-task model, verify each target is coherent:**

## Transfer Learning Pitfall

When claiming "cross-domain transfer" or "fine-tuning works":

```
Scenario: RICO model (90%) → fine-tune on ScreenSpot → 72%.
Claim: "Cross-domain adaptation is viable — +44pp from zero-shot"
```

**The proper test:** Compare pre-trained+fine-tuned vs random-init+trained at the same target data budget. If both achieve ~72% with 600 samples, then the pre-training contributed nothing — fine-tuning alone explains the improvement.

Checklist:
- [ ] Does the experiment compare pre-training + fine-tuning vs training from scratch at multiple data budgets (e.g., 10%, 25%, 50%, 100% of target data)?
- [ ] If only fine-tuning on the full target set is reported, the **transfer** claim is premature
- [ ] The null hypothesis is: "any model with sufficient capacity can be fine-tuned to a new domain in N samples" — pre-training only matters if it reduces the N required

## Common Confounds in ML Research (from this project)
- [ ] **Fix for incoherent targets**: use single-element removal (only drop 1 element per graph) when training type prediction, OR compute per-element targets independently.
- [ ] **Loss weight ≠ fix**: increasing type loss weight from 0.5→2.0 did NOT improve type accuracy (both gave 62%). Incoherent targets cannot be fixed by tuning weights.

## Real VLM Evaluation Protocol

Synthetic element dropping (even with realistic ratios) does NOT replicate VLM error patterns:
- VLM errors are **type-dependent** (icons missed more than text)
- VLM errors are **positionally biased** (screen edges more error-prone)
- VLM errors are **structurally correlated** (if one element in a row is missed, neighbors are more likely missed)
- VLM **over-detects** massively on low-density data (ScreenSpot: 17K detections vs 1.2K GT = 17:1 FP ratio)

**Always validate on real VLM data before claiming GNN effectiveness.**
