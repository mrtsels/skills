# Data Format Gap Analysis — Prompt Pattern

When an ML research project's code expects a certain data format but the actual dataset on disk differs, use this pattern to analyze gaps systematically before writing adapter code.

## Pattern

```
TASK: Analyze the data format discrepancy between what [PROJECT] expects and what
the actual data on disk looks like. Propose a concrete adapter plan.

CONTEXT:
- Project at [REPO_PATH]
- Data at [DATA_PATH]
- Expected format: [what the loader code expects, e.g. per-image JSONs]
- Actual format: [what's on disk, e.g. combined JSON array + images dir]

NEEDS ANALYSIS:
1. Read [LOADER_PATH] to understand expected format (function signatures, field names)
2. Examine [DATA_PATH] to understand actual format on disk
3. Identify specific gaps (field names, coordinate systems, file layout, schemas)

OUTPUT: Structured analysis covering:
- Gap table: what code expects vs what exists (per dataset)
- Proposed adapter approach (specific file changes, function signatures)
- Effort level
- Risks
```

## Real Example: ScreenSpot + GUI-360°

The prompt was sent to Claude Code as:
```
claude --model deepseek-v4-flash --bare --dangerously-skip-permissions \
  --output-format json \
  -p "$(cat /tmp/prompt_data_adapter.txt)"
```

**Key prompt elements that made it work:**
- Gap table specification (code expects X, actual = Y) as a checklist
- "READ FIRST, then analyze. Do NOT write code." — prevents Claude from jumping to coding
- Specific file paths in both codebase and data directory
- Output format explicitly specified (structured analysis, not code)

## Example Output Pattern

Returned a structured table per dataset:
| Aspect | Code Expects | Actual on Disk | Severity |
|--------|-------------|----------------|----------|
| File layout | per-image JSON | single combined file | High |
| Bbox field | bbox [x1,y1,x2,y2] | bounding_box [x,y,w,h] | Medium |
| Image dims | image_width/height | missing, need PIL | Medium |

## When to Use

- Connecting a new dataset to existing loader code
- Before writing any adapter code — understand ALL gaps first
- When the data format changed between dataset versions
- For datasets in non-standard formats (parquet, HuggingFace, combined JSONs)
