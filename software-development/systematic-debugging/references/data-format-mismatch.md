# Data Format Mismatch Diagnosis

## The Pattern

Your code assumes data format A. The actual data on disk is format B. Neither is "wrong" — they just don't match. This is common in data-heavy projects where documentation, code, and reality diverge.

## Diagnosis Steps

### 1. Read the Code's Assumptions

Check the loader/parser code to understand what it expects:
- What keys does it look for? (`data.get("screen_width")`, `data["root"]`)
- What types does it expect? (string, list, dict)
- What format does it assume? (`"[x1,y1][x2,y2]"` vs `[x1, y1, x2, y2]`)
- What fields are REQUIRED vs OPTIONAL?

### 2. Read the Actual Data

Open the raw data files and examine them directly:
```python
import json
with open("path/to/data.json") as f:
    data = json.load(f)
print("Top keys:", list(data.keys()))
# Check types and structure of each field
for k, v in data.items():
    print(f"{k}: type={type(v).__name__}, value={str(v)[:100]}")
```

### 3. Build a Comparison Table

| Code Assumes | Actual Data | Impact |
|---|---|---|
| `data["root"]` | `data["activity"]["root"]` | KeyError |
| `bounds: "[0,0][100,100]"` | `bounds: [0, 0, 100, 100]` | ParseError |
| `"screen_width" exists` | Must derive from bounds[2] | MissingField |
| `text: ""` (string) | `text: null` (None) | Silent skip |

### 4. Fix Both Code AND Docs

**Never fix just one.** If you fix only the code, the docs remain wrong and future contributors (or future-you) will repeat the debugging. If you fix only the docs, the code remains broken.

- Fix the code to handle the actual format
- Update documentation to show the ACTUAL format (not a theoretical one)
- Update test fixtures to use the actual format

### 5. Verify with Real Data

Tests are necessary but not sufficient — they test your *synthetic fixtures*. Always smoke-test against real data:

```python
# Load a real data file through the fixed loader
result = my_loader("data/raw/actual_file_001.json")
print(f"Loaded {len(result.elements)} elements")  # Should be > 0
print(f"First element: bbox={result.elements[0].bbox}")  # Check normalization
```

### Example: RICO Dataset

| Assumption | Reality |
|---|---|
| `root` at top level | `data["activity"]["root"]` |
| `bounds` is string `"[x1,y1][x2,y2]"` | `bounds` is list `[x1, y1, x2, y2]` |
| `screen_width`/`height` in JSON | Derive from root bounds |
| `content-desc` is string | `content-desc` is `[null]` (list) |
| PNG screenshots | JPG screenshots |
| Per-app directories | Flat combined/ directory |

### Pitfalls

- **Don't trust documentation over data**: docs describe intent, data describes reality
- **Don't fix the data to match the code**: data is the source of truth
- **Don't fix only one of code/docs**: they must stay in sync
- **Synthetic test data doesn't prove the fix works**: always test with real files
- **Check multiple real files**: one file's structure might not represent all files
