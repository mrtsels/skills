# Ablation Experiment Design

## Pattern: component ablation study

Used when you need to measure the contribution of individual components
(e.g., constraint types, model heads, feature groups) to overall performance.

## Protocol

1. **Define baseline**: Full configuration (all components)
2. **Define groups**: Ablate one component at a time
   - Each group removes exactly one component (not cumulative)
   - "One-out" is cleaner than "only-X" for identifying dependencies
   - Only-"only-X" as a separate group when you need to measure minimum viable
3. **Control variables**: Keep all hyperparams fixed across groups
4. **Seed diversity**: Run each group with 2+ seeds to measure variance
5. **Metrics**: Record at minimum (primary_metric, n_components, trains_to_best_loss)
6. **Report**: Table with delta from baseline, annotation of significance

## Pitfalls

- Removing constraints ≠ making the task easier — fewer components means
  less signal, potentially higher noise in gradient
- "One-out" ablation may show no drop if other components compensate —
  in which case run "only-X" groups to measure standalone contribution
- Always report the number of remaining components (e.g., #constraints/graph)
  in the ablation table — a drop in acc might just be fewer data, not worse model

## Tools

- The `experiments/ablation_constraints.py` script in the project repo
  demonstrates this pattern for constraint type ablation
- The `experiments/run.py` entry point dispatches ablation via `ablation` subcommand
