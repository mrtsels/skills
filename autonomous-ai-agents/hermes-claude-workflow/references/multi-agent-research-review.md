# Multi-Agent Research Review Workflow

Used in bipartite-gnn-gui Phase 8 direction decision (2026-06-24).

## When to Use

After a batch of exploratory experiments (ABCD-style), before committing to a controlled experiment plan. Use when the user says "开三个session同时做" or "多听取不同AI的意见".

## Method

Spawn 2-3 delegate_task agents with distinct personas:

| Persona | Focus | Rating System |
|---------|-------|---------------|
| **Critical academic reviewer** | Methodology gaps, confounds, statistical rigor, alternative interpretations | STRONG KEEP / WEAK KEEP / DROP |
| **Applied ML engineer** | Practical utility, deployment cost, robustness, real-world value | STRONG KEEP / WEAK KEEP / DROP |
| **Research strategist** (optional) | Narrative, contribution, what makes a paper, what to drop | Same scale |

All receive the same context summarizing the project's findings. They independently rate each finding.

## Example from Phase 8 (bipartite-gnn-gui)

| Finding | Rating | Key Critique |
|---------|--------|-------------|
| CONTAINMENT-only > full | WEAK KEEP | Confound: changed TWO variables (constraint type + constraint count). 977 vs 3,326 test items. |
| Two-model strategy | WEAK KEEP | Same confound. Need full types × 3 head configs as control. |
| Confidence scoring (real data) | STRONG KEEP | AUROC 0.876, clearest result. |
| Type prediction impossible | WEAK DROP | Training target is incoherent: multiple elements removed — bbox averaged but type from first. |
| Cross-domain 28→72% | WEAK KEEP | 72% may just show fine-tuning works, not structural transfer. |

## Output

The reviewer's output goes into TASK.md as a direction decision phase with WEAK/STRONG KEEP/DROP ratings. The decisions guide the next controlled experiments.

## When to Skip

- Single experiment with clear result — no need for multi-agent review
- User says "直接开始" or equivalent
- Task is mechanical (coding, data cleaning, etc.)
