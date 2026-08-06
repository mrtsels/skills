# Codebase Inspection (pygount)

## Install

```bash
pip install pygount
```

## Basic summary

```bash
pygount --format=summary \
  --folders-to-skip=".git,node_modules,venv,.venv,__pycache__,.cache,dist,build,.next,.tox,.eggs" \
  .
```

**Always skip dependency/build dirs** — otherwise pygount hangs or takes minutes.

## Common folder exclusions by project type

```bash
# Python
--folders-to-skip=".git,venv,.venv,__pycache__,.cache,dist,build,.tox,.eggs,.mypy_cache"

# JS/TS
--folders-to-skip=".git,node_modules,dist,build,.next,.cache,.turbo,coverage"
```

## Filter by language

```bash
pygount --suffix=py --format=summary .
pygount --suffix=py,yaml,yml --format=summary .
```

## Detail output

```bash
# Per-file (default format)
pygount --folders-to-skip=".git,node_modules,venv" .

# Top 20 by code lines
pygount --format=summary . | sort -t$'\t' -k1 -nr | head -20
```

## Column meaning

- **Language** — detected language
- **Files** — file count
- **Code** — lines of actual code
- **Comment** — comment/documentation lines
- **%** — percentage of total

## Pseudo-languages
- `__empty__` — empty files
- `__binary__` — binaries (images, compiled)
- `__generated__` — auto-generated
- `__duplicate__` — duplicate content
- `__unknown__` — unrecognized

## Pitfalls
- Markdown shows 0 code lines (all classified as comments)
- JSON counts conservatively — use `wc -l` for accurate line counts
- Large monorepos: use `--suffix` to target specific languages
