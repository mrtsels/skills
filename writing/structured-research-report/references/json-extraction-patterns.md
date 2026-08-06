# JSON Multi-Document Extraction Patterns

This reference captures the techniques used in a session analyzing 10 liquid cooling whitepapers from a pre-extracted JSON file.

## Pattern Overview

Source: `extracted_texts.json` containing 19 entries, each with fields:
- `"file"`: filename (str)
- `"pages"`: page count (int)
- `"size_mb"`: file size (float)
- `"text_len"`: text length in chars (int)
- `"text"`: extracted plain text (str)

## Step 1 — List all entries

Write a quick Python script to see exact filenames (crucial — partial matching requires exact strings):

```python
import json
with open('extracted_texts.json') as f:
    data = json.load(f)
for i, entry in enumerate(data):
    print(f"{i:3d}. [{entry['pages']:3d}p, {entry['text_len']:5d}ch] {entry['file']}")
```

## Step 2 — Filter target entries

Match by partial filename against a known list:

```python
target_filenames = ["keyword1", "keyword2", ...]
def match(entry_file, targets):
    return any(t in entry_file for t in targets)
matched = [e for e in data if match(e["file"], target_filenames)]
```

## Step 3 — Extract to separate files

Write individual text files for clean `read_file` access:

```python
for i, entry in enumerate(matched):
    fname = entry["file"].replace("prefix/", "").replace(".pdf", "")
    outpath = f"/tmp/report_{i:02d}_{fname}.txt"
    with open(outpath, 'w') as f:
        f.write(entry["text"])
```

## Step 4 — Navigate large documents

- **Short docs (<10K chars)**: `read_file` with default limit (500 lines).
- **Medium docs (10-30K chars)**: Read first 500 lines, then continue with `offset`.
- **Large docs (40K+ chars)**: Use `search_files` with `context=3-5` and targeted regex patterns to find relevant sections — e.g., search for `液冷|冷板|浸没|PUE.*1\.[0-9]|散热|功率密度` to locate the liquid cooling parts of a broader document.

## Step 5 — Synthesize

Output a single structured Markdown file with:
- Each report as a numbered section
- Source/type/year metadata header
- Core insights (bullet points)
- Key data table or data bullets
- Standardized data units for cross-report comparison

## Utility Scripts Used in This Session

All scripts were short single-purpose Python files written via `write_file` and run via `python3 <path>`:
- `list_files.py` — list all JSON entries with index, pages, text_len
- `extract_reports.py` — extract matched entries to individual files
- `analyze_liquid_cooling.py` — initial matching + preview

## Pitfalls

- The JSON may be truncated by the tool output display (the `read_file` hint line shows if it's truncated). Always load it with `json.load()` in a Python script to get the full dataset.
- Filenames may contain slashes (directory paths) that need stripping or replacing when writing output filenames.
- Very large entries (50K+ chars) may cause memory/display issues — use offset/limit in `read_file` or search with `context` parameter.
- Document texts from PDF extraction may have layout artifacts (page numbers, headers repeated, OCR errors) — be aware when extracting numbers.
