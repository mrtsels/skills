# Writing CLAUDE.md for Single-File SPA Projects

When a project is a single-file HTML/JS SPA (5000+ lines), Claude Code's default behavior struggles badly. This reference captures the CLAUDE.md structure that prevents the common failure modes.

## The Core Problem

Single-file SPAs combine HTML, CSS, and JS in one massive file. Claude Code:
- Reads only 500-line chunks → loses context across reads
- Uses Edit tool for find-and-replace → tab/space mismatches cause cascade failures
- Defaults to browser testing → wastes time on end-to-end when syntax check suffices
- Tends to overengineer → writes wrapper functions instead of surgical edits

## CLAUDE.md Sections That Matter

Based on repeated corrections from the user (session bae402b8), these sections are mandatory:

### 1. Fatal Error List (top, before anything else)

The most recently corrected mistakes must go FIRST — Claude Code reads top-down and takes the first rules most seriously.

```markdown
## ⚠️ Fatal Error List (violated before, must not repeat)

### Edit tool: stop after 2 failures
- Edit returns "String to replace not found" → STOP, grep the actual file
- This project uses TAB indentation, not spaces
- After 2 failures: switch to sed/Python, don't retry Edit

### Tool errors: brake, don't accelerate
- API error, browser crash, invalid arg → STOP, read error, don't retry
- 2 consecutive identical errors → switch approach or ask user

### Verification: node --check before browser
- After every JS change: `node --check index.html` (instant syntax check)
- Only open browser after syntax + logic both pass

### Surgical edits only
- grep line numbers before editing, don't search blindly
- No wrapper functions, no abstraction layer, no refactoring
- 5-line fix, don't write 50 lines
```

### 2. Code Location Flow

Single-file projects need grep-first discipline:

```markdown
## Code Location Flow

1. `grep -n "targetFunction|targetString" index.html` — exact line number
2. `sed -n 'START,END p' index.html` — read the context
3. Read tool at specific range — confirm before editing

Example: fix polTogglePreview → `grep -n "function polTogglePreview" index.html` → Read line 5020-5040
```

### 3. Edit Tool Priority

```markdown
## Edit Tool Priority (prefer top)

1. sed / Python script — exact replacement, won't fail on tabs
2. Patch tool — targeted context-aware replacement
3. Edit tool — LAST resort (tab matching is unreliable here)
```

### 4. Verification Order

```markdown
## Verification Order (mandatory)

1. `node --check index.html` — syntax must pass first
2. Review modified code manually — check function boundaries, return statements
3. Browser end-to-end — ONLY after steps 1+2 pass
```

## Template

Use this as a starting point when you encounter a new single-file SPA project that needs a CLAUDE.md:

```markdown
# CLAUDE.md

## ⚠️ Fatal Error List

### Edit tool: stop after 2 failures
- This project uses TAB indentation
- After 2 Edit failures → switch to sed/Python
- grep the file before guessing

### JS verification: node --check FIRST
- Never open browser before syntax check passes

### Surgical edits only
- grep line numbers before editing
- No refactoring, no wrapper functions
- Change only what was asked

## Code Location

```bash
grep -n "function|id|string" index.html
sed -n 'START,END p' index.html
```

## Verification

1. `node --check index.html`
2. Manual code review
3. Browser test (last)
```
