# Bloated Git History Recovery

When a repo's git history contains files too large to push (data files, binaries, compressed corpora), you have two paths depending on whether the remote already exists.

## Approach 1: Empty Remote (No History Yet)

The cleanest path — start from scratch with an orphan branch.

### 1. Diagnose the Bloat

```bash
# Find the 20 biggest blobs in history
git rev-list --objects --all | git cat-file --batch-check='%(objecttype) %(objectname) %(objectsize) %(rest)' \
  | awk '/^blob/ {size=$3; $1=$2=$3=""; sub(/^  */,""); print size, $0}' \
  | sort -rn | head -20

# Or with human-readable sizes (requires numfmt)
git rev-list --objects --all | git cat-file --batch-check='%(objecttype) %(objectname) %(objectsize) %(rest)' \
  | awk '/^blob/ {size=$3; $1=$2=$3=""; sub(/^  */,""); print size, $0}' \
  | sort -rn | head -20 \
  | numfmt --field=1 --to=iec
```

Common culprits: `.duckdb`, `.csv.zip`, large PDFs, `.parquet`, `.npy`, model weights.

### 2. Create an Orphan Branch

```bash
git checkout --orphan clean-main
git rm -rf --cached .
# Verify index is empty
git status
```

### 3. Scalpel Push (Split by File Type)

Push small/text files first, then add binaries in a second batch. This avoids timeouts and makes failures easy to retry.

```bash
# Batch 1: text files (.md, .py, .csv, .ipynb, .svg, .yaml, .json, .toml, config)
git add *.md *.py *.csv *.ipynb *.svg *.yaml *.json *.toml .gitignore
# If files are in subdirectories, be more specific:
git add AGENTS.md CLAUDE.md .gitignore lecture-notes/ assignments/ tasks/
# Remove any binaries that got accidentally staged
git reset -- assignments/assignment-1.xlsx        # xlsx
git reset -- assignments/assignment-2/Assignment\ 2.pdf  # pdf
git reset -- tasks/**/*.zip  # archives
git reset -- tasks/**/*.key  # Keynote

git commit -m "Initial commit: text files only"
git push --set-upstream origin clean-main:main
# Or if remote has a different default branch name:
git push --set-upstream origin clean-main:main
```

```bash
# Batch 2: binary assets
git add assignments/assignment-1.xlsx
git add assignments/assignment-2/Assignment\ 2.pdf
git add tasks/**/*.pdf tasks/**/*.key tasks/**/*.zip
git commit -m "Add binary assets: workbooks, slides, task PDFs"
git push origin HEAD:main
```

> **Note:** When local and remote branch names differ (`clean-main` vs `main`), use `git push origin HEAD:main` for subsequent pushes instead of bare `git push`.

### 4. Clean Up Local Branches

```bash
git branch -D main        # Delete the old bloated branch
git branch -m clean-main main  # Rename clean branch to main
```

## Approach 2: Remote Already Has History

When the repo has already been pushed and you need to purge files from history:

### Option A: git filter-repo (recommended)

```bash
pip install git-filter-repo
git filter-repo --path-glob '*.duckdb' --invert-paths
git filter-repo --path-glob '*.csv.zip' --invert-paths
git push --force --all
```

### Option B: BFG Repo-Cleaner

```bash
# Remove files larger than 10MB
java -jar bfg.jar --strip-blobs-bigger-than 10M .
# Remove specific file patterns
java -jar bfg.jar --delete-files '*.duckdb' .
git reflog expire --expire=now --all && git gc --prune=now --aggressive
git push --force
```

### Option C: Orphan Branch (Nuclear — loses all history)

Same as Approach 1 steps 2-4, then force push:

```bash
git checkout --orphan clean-main
git rm -rf --cached .
# Stage and commit (see scalpel above)
git commit -m "Initial commit: clean slate"
git branch -D main && git branch -m clean-main main
git push -f origin main
```

> **Warning:** Force-pushing to a shared repo destroys history for everyone. Coordinate with the team first. Only use this on a repo where everyone can rebase or reclone.

## Pitfalls

- **`awk` field splitting:** When filenames contain spaces, the default `$1 $2 $3 $4` approach breaks. Use the slice+sub technique: `{size=$3; $1=$2=$3=""; sub(/^  */,""); print size, $0}`.
- **`git rm -rf --cached .` clears everything:** After orphan checkout, the working tree still has files — you need to re-add what you want. The index is empty, so `git add` only re-stages the files you explicitly name.
- **Orphan branch resets .gitignore effect:** After switching to an orphan branch, git may re-include previously gitignored files in `git add -A`. Always use explicit `git add <paths>` rather than `git add -A` or `git add .` to avoid accidentally staging files you intended to ignore.
- **Branch name mismatch:** `git push --set-upstream origin clean-main:main` creates a remote branch named `main` while the local branch is `clean-main`. Subsequent `git push` fails with "upstream does not match current branch". Use `git push origin HEAD:main` or rename locally with `git branch -m clean-main main`.
- **`git push` timeout:** If `git push` times out even on text-only commits, increase the timeout (the push itself may be slow, not just the transfer) or split into even smaller batches (e.g., lecture-notes/ alone, then assignments/, then tasks/).
- **`git filter-repo` not idempotent:** Running `git filter-repo` multiple times on the same repo accumulates refs in `refs/original/`. Use `git update-ref -d refs/original/refs/heads/main` between runs, or reclone.

## Verification

After push, verify the remote has the right content:

```bash
# Check remote doesn't contain the large files
git ls-remote origin HEAD
git clone --depth 1 <remote-url> /tmp/verify-repo
du -sh /tmp/verify-repo/    # Should be small
rm -rf /tmp/verify-repo
```
