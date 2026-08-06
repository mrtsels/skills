# Review Output Template

Use this as the structure for PR review summary comments.

## For PR Summary Comment

```markdown
## Code Review Summary

**Verdict: [Approved ✅ | Changes Requested 🔴 | Reviewed 💬]** ([N] issues, [N] suggestions)

**PR:** #[number] — [title]
**Author:** @[username]
**Files changed:** [N] (+[additions] -[deletions])

### 🔴 Critical
<!-- Issues that MUST be fixed before merge -->
- **file.py:line** — [description]. Suggestion: [fix].

### ⚠️ Warnings
<!-- Issues that SHOULD be fixed, but not strictly blocking -->
- **file.py:line** — [description].

### 💡 Suggestions
<!-- Non-blocking improvements, style preferences -->
- **file.py:line** — [description].

### ✅ Looks Good
<!-- Call out things done well — positive reinforcement -->
- [aspect that was done well]

---
*Reviewed by Hermes Agent*
```

## Severity Guide

| Level | Icon | When to use | Blocks merge? |
|-------|------|-------------|---------------|
| Critical | 🔴 | Security, data loss, crashes, broken core | Yes |
| Warning | ⚠️ | Bugs in non-critical, missing error handling | Usually yes |
| Suggestion | 💡 | Style, refactoring, perf hints, docs gaps | No |
| Looks Good | ✅ | Clean patterns, good tests, smart design | N/A |

## Verdict Decision

- **Approved ✅** — Zero critical/warning items
- **Changes Requested 🔴** — Any critical or warning item
- **Reviewed 💬** — Observations only (draft PRs, informational)

## For Inline Comments

Prefix with severity icon:
```
🔴 **Critical:** SQL injection — use parameterized queries.
⚠️ **Warning:** Error silently swallowed — log it.
💡 **Suggestion:** Use dict comprehension here.
✅ **Nice:** Good use of context manager.
```