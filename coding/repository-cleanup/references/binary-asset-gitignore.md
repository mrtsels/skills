# Binary Asset Gitignore Patterns

Common patterns for repos with large binary files (research data, PDFs, archives).

## Standard Patterns

```gitignore
# All PDFs — external source material, not code
*.pdf

# Archives and staged deliverables
*.zip
*.tar.gz
*.7z
*.rar

# Presentation/Keynote binaries
*.key
*.pptx
*.pages

# Data files (DB, checkpoints, models)
*.duckdb
*.db
*.sqlite
*.sqlite3
*.ckpt
*.pth
*.pt
*.h5
*.onnx

# Compiled / build
*.class
*.jar
*.dll
*.so
*.dylib
*.exe
```

## Directory-Level Ignores

```gitignore
# Large data directories
data/
checkpoints/
models/
datasets/
```

## When to Use Each

| Pattern | When | Example repos |
|---------|------|---------------|
| `*.pdf` | Lecture slides, research papers, deliverables | quant-academy, research repos |
| `*.zip` / `*.tar.gz` | Dataset archives, assignment bundles | ML projects, course repos |
| `*.key` / `*.pptx` | Presentation source files | project deliverables |
| `*.duckdb` / `*.db` | Large database files | data pipelines, backtesting |
| `*.pth` / `*.ckpt` | Model weights | ML/GNN research |
| `data/` | Raw datasets | ML projects |
| `checkpoints/` | Training checkpoints | GNN, deep learning |

## Verification

After adding patterns, check nothing broke with:

```bash
git ls-files | grep -E '\.(pdf|zip|key|pptx)$'    # Should be empty
git status                                          # Confirm clean
```
