# HuggingFace Dataset Download Patterns

## Common Gotchas

### Gated/Private Repos Need a Token
```bash
export HF_TOKEN=hf_xxx
# Or login:
huggingface-cli login --token $HF_TOKEN
```

### `hf_hub_download` API

```python
from huggingface_hub import hf_hub_download

# Download to specific local directory
p = hf_hub_download(
    "org/dataset-name",
    "path/to/file.parquet",
    repo_type="dataset",
    local_dir="data/raw/dataset_name/",
    local_dir_use_symlinks=False,  # deprecated but harmless
)
```

### List Files in a Repo
```python
from huggingface_hub import list_repo_files
files = sorted(list_repo_files("org/dataset-name", repo_type="dataset"))
```

## Dataset Formats

### Simple Format (e.g. ScreenSpot: `benwiesel/ScreenSpot`)
```
screenspot.json          # metadata with bbox annotations
images/*.png             # screenshot images
```
Download: `hf_hub_download("benwiesel/ScreenSpot", "screenspot.json", ...)` + individual images.

### Parquet Format (e.g. GUI-360: `cua-verse/GUI-360`)
```
desktop/grounding/point/train/point/shard-00000-of-00039.parquet
desktop/grounding/point/test/point/...
desktop/understanding/...
```
Download individual shards. Read with `pyarrow.parquet`:
```python
import pyarrow.parquet as pq
table = pq.read_table("shard-00000-of-00039.parquet")
records = table.to_pylist()  # list of dicts
```

## When to Download Directly vs Via Claude Code

- **DO download yourself (Hermes)**: Large files (>50MB), many files (>50), datasets with complex structure, anything over SMB/NFS. Claude Code's sandbox has limited download throughput and no `resume` support.
- **DO delegate to Claude Code**: Small sample files where you need the prompt context to understand the format (e.g. "download 3 sample files to inspect the structure").

## SMB Mount for Large Datasets

When datasets are too large for local disk, mount a network share:

```bash
# macOS: mount SMB share
osascript -e 'mount volume "smb://user:pass@192.168.x.1/sharename"'

# Symlink project data dir
ln -s /Volumes/sharename data/raw
```

SMB mount quirks:
- `find` and recursive operations can be very slow
- `rm -rf` may fail on nested directories — use `rmdir` or delete from Windows side
- `.DS_Store` files appear — harmless
- If mount disconnects (sleep/wake), remount via Finder: Go → Connect to Server
