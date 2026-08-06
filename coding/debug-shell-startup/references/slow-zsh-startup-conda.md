# Case: Conda 26.1.1 Causing 30s zsh Startup

## Environment
- macOS 27.0 (ARM / Apple Silicon)
- Homebrew-installed Miniconda at `/opt/homebrew/Caskroom/miniconda/base/`
- conda 26.1.1 (has known bug: `TypeError` in `_get_deactivate_scripts`)
- `auto_activate_base: True`

## Symptoms
- Every new zsh startup takes ~30 seconds before accepting input
- Conda initialization crashes on every shell start:

```
TypeError: expected str, bytes or os.PathLike object, not NoneType
  File "conda/activate.py", line 778, in _get_deactivate_scripts
    for entry in os.scandir(join(prefix, "etc", "conda", "deactivate.d"))
```

## Diagnostic Output

### Before fix: cold start timing
```
Run 1: 30.94 real
Run 2: 30.87 real
Run 3:  9.83 real  (partial warming)
```

Conda `shell.zsh hook` needs to launch CPython (~0.6s user + 0.2s sys CPU), but the I/O wait for loading Python + conda package from cold is ~30s on this system.

### After fix: lazy loading
```
Run 1: 0.08 real
Run 2: 0.06 real
Run 3: 0.07 real
```

### After fix: conda still works
```
$ conda --version
conda 26.1.1
```

## Additional Issues Found

1. **Broken export line** — two `export` statements concatenated without separator:
   ```zsh
   export CLAUDE_CODE_SUBAGENT_MODEL="deepseek-v4-flash"export JAVA_HOME=$(/usr/libexec/java_home -v 17)
   ```
   Result: `CLAUDE_CODE_SUBAGENT_MODEL` had value `deepseek-v4-flashexport`.

2. **Redundant `npm prefix -g`** — `export PATH="$(npm prefix -g)/bin:$PATH"` ran Node.js on every startup for a path already set statically by the line above it.

## Lazy Conda Implementation

```zsh
export PATH="/opt/homebrew/Caskroom/miniconda/base/bin:$PATH"
conda() {
  unfunction conda
  if [ -f "/opt/homebrew/Caskroom/miniconda/base/etc/profile.d/conda.sh" ]; then
    . "/opt/homebrew/Caskroom/miniconda/base/etc/profile.d/conda.sh"
  fi
  conda "$@"
}
```

## Files Touched
- `.zshrc` — replaced conda init block with lazy function, fixed broken export, removed redundant npm prefix call
- `.zshenv` — unchanged (only sources `.cargo/env`, fast)
- `.zprofile` — unchanged (only adds Python PATH, fast)
