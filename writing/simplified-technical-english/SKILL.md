---
name: simplified-technical-english
description: >-
  Check and fix technical documentation against ASD-STE100 Simplified Technical
  English and equivalent controlled-language standards.  Active voice, short
  sentences, consistent terminology, no vague terms, present tense for
  procedures.
trigger: docs
---

# Simplified Technical English (ASD-STE100) — Document Audit Skill

## Overview

ASD-STE100 is a controlled-language specification for writing technical
documentation.  Apply it when the user asks to audit or fix all `.md` files
against a writing standard, or when switching from research notes to
public-facing docs.

## Core Rules — Quick Reference

### 1. Sentence Length

Maximum 20–25 words per sentence.  Split longer sentences at natural
break points (conjunctions, relative clauses).  For bilingual documents,
check only the English portions.

### 2. Active Voice

Do NOT use passive voice in procedural technical writing.

| ❌ Passive | ✅ Active |
|-----------|----------|
| The model is trained on RICO data. | Train the model on RICO data. |
| The config file is read at startup. | The system reads the config file at startup. |
| Elements are detected by the VLM. | The VLM detects elements. |
| The checkpoint was loaded from disk. | The script loads the checkpoint from disk. |

Exceptions: when the agent is unknown ("the button was pressed") or in
academic abstracts where passive is conventional.

### 3. Vocabulary — Banned Terms

| Banned | Use Instead |
|--------|-------------|
| `etc.` | Remove, or replace with "such as" + specific items |
| `e.g.` | "for example" |
| `i.e.` | "that is" or rephrase |
| `approximately` | A specific value or range |
| `several` / `various` | A specific number or "multiple" |
| `quite` / `rather` / `somewhat` | Remove or quantify |
| `will` (future tense) | Present tense ("the system does" not "the system will do") |
| `shall` (requirement) | "must" |

### 4. Tense

- **Procedures**: simple present imperative ("Run the script.")
- **Descriptions**: simple present ("The model loads 220K parameters.")
- **Future**: do NOT use "will" for future events.  Use present tense with
  a time marker ("The next release **adds** this feature" not "…will add…").

### 5. Word Choice

- Use the SAME word for the SAME concept throughout a document (do not
  alternate "train" / "trainer" / "training process" / "learning procedure").
- Use articles (a, an, the) correctly.
- Use "must" for requirements, not "shall" (STE100 limits "shall" to
  official/legal statements).
- Avoid "-ing" participle modifiers ("the training process" not "the
  training process using…").

### 6. Procedures

- Number each step (1. 2. 3. …).
- One instruction per step.
- Include the agent/actor when useful ("The user enters the path").

## What to Preserve (Always)

| Content | Preserve As-Is |
|---------|---------------|
| Code blocks | Triple backtick blocks, inline single-backtick code |
| Tables | Markdown pipe tables, alignment markers (`:---`, `:---:`) |
| LaTeX math | `$$...$$`, `$...$` environments |
| Non-English text | Chinese, Japanese, Korean — do not touch |
| Mermaid diagrams | All nodes, edges, labels |
| Checkboxes | `[x]`, `[ ]` task list markers |
| URLs and links | `[text](url)` syntax |
| Reference citations | `[1]`, `[Author, Year]` |
| Math notation | All formulas and delimiters |
| File paths / code IDs | Anything inside backticks is not prose |

## Common Fix Patterns

### Pattern 1: Passive → Active
```
- The data is loaded by the parser.
+ The parser loads the data.
- Constraints are extracted from the element graph.
+ The system extracts constraints from the element graph.
```

### Pattern 2: Remove "etc."
```
- Supports types: button, text, icon, etc.
+ Supports types: button, text, and icon.
```

### Pattern 3: Split Long Sentence
```
- This module handles data parsing, normalization, and loading into the dataset format and is used by all downstream components during training and evaluation.
+ This module handles data parsing, normalization, and loading into the dataset format. All downstream components use it during training and evaluation.
```

### Pattern 4: Future → Present
```
- Phase 4.2.1 will reconcile the loader with the requirements spec.
+ Phase 4.2.1 reconciles the loader with the requirements spec.
```

## Audit Workflow

### Phase 0: Inventory

Collect all markdown files in the project:

```bash
find . -name '*.md' -not -path './.venv/*' -not -path './node_modules/*' | sort
```

Read each file header to determine language mix:
- **English-only** — full STE100 rules apply
- **Bilingual** (Chinese + English) — fix only English prose, leave Chinese text exactly as-is
- **Chinese-only** — no STE100 violations in English terms (acronyms, library names, file paths are not English prose); declare clean

### Phase A: Scan for Violations

Run this scan on each file's English prose (outside code blocks, tables, and math):

```python
import re

# Core violation patterns
issues = {
    "passive": r'\b(?:is|are|was|were|been|being|be)\s+(?:\w+ed|built|set|made|known|found|given|kept|sent|run|done)\b',
    "vague":   r'\b(?:etc\.|e\.g\.|i\.e\.|approximately|roughly|several|various|somewhat|quite|rather)\b',
    "future":  r'\bwill\b(?!\s+(?:be\s+)?(?:not|never))',
    "shall":   r'\bshall\b',
}

for name, pat in issues.items():
    for m in re.finditer(pat, content, re.IGNORECASE):
        ...
```

**Important:** Exclude code blocks (triple backtick), inline code (single backtick), LaTeX math (`$$…$$`, `$…$`), and markdown table lines (start with `|`) from the scan. These are structural elements, not narrative prose.

### Phase B: Fix Files (batch by size and language)

Build a worklist sorted by file size ascending:

1. **Small files (< 50 lines, English-only or bilingual)** — `write_file` (full rewrite with fixed content)
2. **Medium files (50–300 lines)** — `patch` (targeted string replacement, one patch per violation type)
3. **Large files (> 300 lines)** — dispatch to subagents via `delegate_task()` with a **self-contained prompt** that includes:
   - Exact file path and line count
   - Specific rules (which apply: active voice vs academic passive, short sentences, banned terms)
   - Preservation scopes: "Preserve ALL code blocks, ALL tables, ALL Chinese text, ALL LaTeX math, ALL checklist boxes `[x]`/`[ ]`"
   - A re-read-verify step before writing back

**Subagent worklist pattern** (one per file, up to 3 concurrently):

| File | Lines | Language | Strategy |
|------|-------|----------|----------|
| small.md | 30 | English | write_file |
| medium.md | 150 | Bilingual | patch × N |
| large.md | 650 | Bilingual | delegate_task |

For Chinese-dominated technical documents (dev plans, research notes), skip — they contain only technical acronyms (VLM, GNN, API) and file paths, not English prose sentences. Report as "no violations found."

### Phase C: Fix Rules (order of application)

Apply fixes in this priority order to avoid cascading false positives:

1. **Banned terms** first (`etc.` → remove, `e.g.` → `for example`, `i.e.` → `that is`) — these are exact matches
2. **Active voice** — identify passive (is/was/are + past participle), rewrite with explicit subject
3. **Sentence splitting** — after fixing voice, re-check sentence length; split at conjunctions
4. **Future/will** → present tense
5. **Shall** → must

### Phase D: Verify

- `git diff --stat` — confirm only target files changed, check insertions/deletions ratio
- Re-scan the fixed file with the same regex patterns — should return 0 matches
- Visually spot-check:
  - Code blocks still parse correctly (no broken backticks)
  - Table alignment markers (`:---`, `:---:|`) unchanged
  - Chinese text unchanged (for bilingual files)
  - LaTeX math expressions intact
- Run `git diff` on a few files to confirm only prose changed, not structural elements

### Phase E: Commit

Each file gets its own commit with `docs:` prefix. Commit message format:

```
docs: apply asd-ste100 to <filename>
```

Group closely related files only when they share a directory and the user has not specified per-file commits. Push immediately after each commit.

## Handling Bilingual Documents

When a mix of languages exists in the same file:

- **Fix only the English prose** outside code blocks and tables.
- **Do not touch** Chinese, Japanese, Korean, or other non-English text.
- **Do not touch** code, shell commands, YAML/JSON/TOML examples.
- **Do not touch** LaTeX math (`$$…$$`, `$…$`).
- **Do not touch** markdown tables or their alignment markers.

Preserve each block exactly as-is.  Fix only the English narrative
sentences between structural elements.

## Pitfalls

1. **When the user specifies a model, library, or tool by name, use exactly that.** Do not substitute alternatives or suggest different approaches. If the specified one fails, find a way to make it work (patch, downgrade, workaround). Reporting "this doesn't work, use X instead" is disrespectful unless you have exhausted all options and can prove impossibility with evidence.

2. **Passive voice is conventional in academic writing** (abstracts, related
   work sections).  Apply active-voice fixes primarily to procedural sections
   and technical descriptions.  Leave academic-abstract conventions unless
   the user explicitly asks for full STE100 compliance.

3. **Chinese text mixed with English terms.**  "模型使用等参数" (model uses
   "etc." inside Chinese) — only fix the English word "etc.", not the
   surrounding Chinese sentence.

4. **Long file + many violations = infinite loop on patches.**  For files
   with 50+ violations across many lines, use `delegate_task()` rather than
   sequential `patch` calls.  Each subagent gets one file and does a
   targeted read → fix → write pass.

5. **Bullet-list sentences may trigger false-positive "sentence length."**
   A bullet item with 40 words is a sentence, not a bullet — split it.
   But a bullet item that is a code path or filename is fine.

5. **"etc." inside code comments or inline code.**  Only fix prose `etc.`,
   not `etc.` inside backtick code spans or code blocks.

6. **Table rows with long content > 25 words.**  Table cells are not
   sentences — do not split table content unless the user specifically
   asks.  The rule applies to narrative prose, not tabular data.

## Related Skills

- `de-ai-ify-writing` — Chinese writing style audit (AI-ism removal),
  complementary to STE100 which targets English technical prose
- `repo-documentation` — AGENTS.md / README.md conventions

## References

- ASD-STE100 official specification (ASD-STE100 Issue 7, 2017)
- Simplified Technical English — Wikipedia
