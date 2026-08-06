# Run Splitting Patterns Observed in Chinese Docx Files

These are actual splittings captured from Coremail-generated docx tables. Use as lookup when diagnosing.

## Date Strings

| Full Text | Run Contents |
|-----------|-------------|
| `2026年3月31日` | `202` / `6` / `年` / `3` / `月` / `31` / `日` |
| `2026年3月31日` (alt) | `20` / `2` / `6` / `年` / `3` / `月` / `3` / `1` / `日` |
| `2026年6月30日` | `202` / `6` / `年` / `6` / `月` / `30` / `日` |

When replacing `3月31日` → `6月30日`:
- Pattern A (replacement target `31` is one run): `3` `月` `31` `日` → `6` `月` `30` `日`
- Pattern B (`31` split): `3` `月` `3` `1` `日` → `6` `月` `2` `6` `日`

## Period References

| Full Text | Run Contents |
|-----------|-------------|
| `一季度` (as section title) | `一` / `季度权益市场E` / `TF` / `概况` |
| `一季度` (in running text) | `一季度` (single run) or `一` / `季度` / `固收市场概况` |

Replace `一` with `二` only when followed by `季度` in the next run — don't blindly replace all `一` runs.

## Holdings Label

| Full Text | Run Contents |
|-----------|-------------|
| `本季度末权益资产仓位占比为0。` | `本季度` / `末` / `权益` / `资产` / `仓位占比为` / `0` / `。` |

To replace the number while keeping structure: change run `0` → `new text`, clear the other label runs to `""`.

## Checkboxes (☑/□)

| Full Text | Run Contents |
|-----------|-------------|
| `□有   ☑无    □为本季度新增项目，不适用` | `□` / `有` / `  ` / `  ` / `☑` / `无 ` / `   ` / `□` / `为本季度新增项目，不适用` |

Each checkbox character is its own run. Toggle by changing `☑` ↔ `□` in the specific run.
