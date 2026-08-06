# `set -euo pipefail` Pitfalls in Bash CLI Tools

## 1. `ls` with unmatched glob → silent exit

When `ls` is called with a glob pattern that matches nothing, bash passes the literal pattern to `ls`, which exits with code 2. Under `set -e`, this kills the script even inside `$(...)`:

```bash
# BROKEN: ls fails → subshell exits → parent exits
jar=$(ls "$dir/enterprise-mvp-"*.jar 2>/dev/null | head -1)

# FIXED: || true swallows the non-zero exit
jar=$(ls "$dir/enterprise-mvp-"*.jar 2>/dev/null | head -1) || true
```

The `2>/dev/null` silences stderr but does NOT change the exit code. Always add `|| true` after `$()` containing `ls` + glob that may not match.

## 2. Empty array expansion inside function → "unbound variable"

With `set -u`, accessing `"${array[@]}"` inside a **function** when the array is **empty** triggers "unbound variable" — even though the same access works fine at the global scope.

```bash
# BROKEN: set -uo pipefail, empty array, function context
JAR_OPTS=()
add_jar() { for existing in "${JAR_OPTS[@]}"; do ... done; }
add_jar "test"  # → JAR_OPTS[@]: unbound variable

# FIXED: check length first (length always works)
add_jar() {
  local p="$1"
  if [ ${#JAR_OPTS[@]} -gt 0 ]; then
    for existing in "${JAR_OPTS[@]}"; do
      [ "$existing" = "$p" ] && return
    done
  fi
  JAR_OPTS+=("$p")
}
```

`${#array[@]}` works correctly under `set -u` because it reads the count without iterating. `"${array[@]}"` fails because bash treats an empty array expansion inside a `for` loop header as an unbound variable reference.

## 3. `read` in non-TTY → EOF kills script

`read` returns non-zero when stdin is closed (EOF/pipe, cron, CI). With `set -e`, this kills the script.

```bash
# BROKEN: read fails on EOF → script exits
echo -n "Continue? [Y/n] "; read -r ans

# FIXED: guard with TTY check
if [ -t 0 ]; then
  echo -n "Continue? [Y/n] "; read -r ans
fi
```

Non-TTY mode should auto-accept defaults (typically Y/update).

## 4. macOS `sed` doesn't support backreferences in pattern

macOS `sed -E` does NOT support backreferences (`\1`, `\2`) in the PATTERN part of a substitution — only in the REPLACEMENT:

```bash
# GNU sed (Linux): works
sed -E 's|\[([A-Z.]+)\]\(\1|[\1)](path/\1|g' file

# macOS sed: \1 in pattern is NOT evaluated — use individual literals
for f in ARCH DATABASE DEPLOY; do
  sed -i '' "s|\[$f\.md\]($f\.md|[${f}.md](path/${f}.md|g" file
done
```

Or use Python for complex patterns that need backreferences in the match.
