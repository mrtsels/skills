---
name: schema-doc-audit
description: "Systematic audit of database schema documentation against actual DDL, entity models, and migration scripts. Cross-reference init.sql ↔ Java entities ↔ Flyway migrations ↔ docs; fix discrepancies; generate ER diagrams."
version: 1.1.0
author: Hermes Agent
license: MIT
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [database, documentation, audit, schema, migration, ER-diagram]
    related_skills: [systematic-debugging, document-sanitization]
---

# Schema Documentation Audit

## When to Use

Trigger on any of:
- User asks "扫一遍盘" (scan the whole project) for database fields
- User reports database documentation is outdated/incomplete
- After migration scripts have been modified or added
- Before project handover / documentation handoff
- When Java entities don't seem to match the actual database columns

## Workflow

### Phase 1: Gather All Sources of Truth

There are up to 4 sources that may each be independently outdated:

| Source | File(s) | What to extract |
|--------|---------|-----------------|
| DDL snapshot | `init.sql` or `schema.sql` | Full CREATE TABLE for each table |
| Java entities | `backend/.../domain/*.java` | `@Table(name=...)`, `@Column(name=...)`, field names + types |
| Flyway migrations | `resources/db/migration/V*.sql` | Sequential DELTAs that build the schema |
| Existing docs | `docs/SCHEMA.md`, `docs/DATABASE.md` | Current doc state — the thing being audited |

**Read them all before making any changes.** Use `read_file` for each source.
**Batch independent reads** into one turn (all entity files, both SQL files, all docs).

### Phase 2: Cross-Reference Fields

For each table:

1. Extract column names from `init.sql` (source of truth for final state)
2. Extract field names + `@Column(name=...)` annotations from Java entity
3. Convert Java camelCase to snake_case (handling `@Column` overrides)
4. Compare: every Java field should have a matching SQL column, every SQL column should have a matching Java field
5. Flag mismatches

**Tools:** (use python3 for cross-platform; macOS grep lacks -P)

```python
# In execute_code, use read_file() + re to parse both sources
import re

def read_file(path):
    with open(path) as f:
        return f.read()

# Get table name from entity
m = re.search(r'@Table\(name\s*=\s*"(\w+)"', entity_content)
table_name = m.group(1)

# Extract @Column(name=...) overrides
for m in re.finditer(r'@Column\([^)]*name\s*=\s*"(\w+)"[^)]*\)\s*private\s+\S+\s+(\w+)\s*[=;]', entity_content):
    java_field = m.group(2)
    sql_col = m.group(1)
    print(f"  @Column mapped: {java_field} -> {sql_col}")

# Get all field names
fields = set(re.findall(r'private\s+\S+\s+(\w+)\s*[=;]', entity_content))

# CamelCase to snake_case
def camel_to_snake(name):
    return re.sub(r'([a-z0-9])([A-Z])', r'\1_\2', name).lower()
```

### Phase 3: Validate Migration Scripts

For each Flyway migration script, check:

1. **Duplicate CREATE TABLE** — does a migration script CREATE TABLE X that was already created by a lower-version migration? MySQL will error without `IF NOT EXISTS`.
2. **Non-ASCII column names** — Chinese characters in column names break Java entity mapping.
3. **Missing `IF NOT EXISTS`** — ALTER TABLE ADD COLUMN without `IF NOT EXISTS` will fail if re-run.
4. **Column type mismatches** — different migrations defining the same column with different types.
5. **Underscore naming drift** — the most common silent inconsistency. A migration adds `revenue_growth_2y_avg` but init.sql already has `revenue_growth2y_avg` (missing underscore after `growth`). Same for `equity_financing_2y` vs `equity_financing2y`. **Extract all column names from both init.sql CREATE TABLE and V*.sql ALTER TABLE as sorted sets and diff them** — spot-checks miss these. See `references/enterprise-mvp-migration-audit-202607.md` for a real 22+ discrepancy example.

**Common bug patterns to grep for:**
```bash
# Check for CREATE TABLE that may duplicate an earlier migration
grep -c "^CREATE TABLE" V*.sql

# Check for Chinese characters in column names
grep -nP '[^\x00-\x7F]' V*.sql

# Check ALTER TABLE ADD COLUMN without IF NOT EXISTS
grep "^ALTER TABLE.*ADD COLUMN" V*.sql | grep -v "IF NOT EXISTS"
```

**Pitfalls:**
- If migration V5_1 creates `declaration_material` and V5_2 also creates `declaration_material` with a different column set, V5_2 will fail. Fix: replace the duplicate CREATE TABLE with ALTER TABLE ADD COLUMN IF NOT EXISTS for only the genuinely new columns.
- Migration scripts that add columns mentioned nowhere else (e.g. `ip_class1self` as a typo of `ip_class1_self`) are orphaned — document as known issue then drop from init.sql.

### Phase 4: Fix Discrepancies

Fix in priority order:

1. **Migration scripts** — fix bugs (duplicate CREATE TABLE, Chinese column names, missing IF NOT EXISTS)
2. **init.sql** — fix typos (duplicate columns, missing columns) — but CHECK if the production DB has the typo column before dropping
3. **Docs** — update field lists, migration history, known issues

**When to fix vs. when to note:**
- Migration scripts are safe to fix anytime (they won't re-run on existing DBs)
- init.sql fixes can drop columns, but only if the production DB doesn't have data there
- Entity-to-column naming mismatches (e.g. `materialType` → `@Column(name="group_name")`) are just documentation notes, not bugs
- **Commit after each fix** without being asked. Use separate commits for: (a) docs updates, (b) migration fixes, (c) init.sql changes.

### Phase 5: Generate ER Diagram

Create a visual diagram showing:
- Each table with its entity class name (e.g. `Enterprise.java`)
- Key fields (PK, FK, UNIQUE, important columns)
- Foreign key relationships with orthogonal arrow routing
- Color coding by module

**Two approaches:**

#### Approach A: Python Script from DDL (preferred for 5+ tables)

Use a Python script to:
1. Parse `init.sql` DDL for each CREATE TABLE -- extract column names + types via regex
2. Inject FK relationships from project knowledge (JPA @ManyToOne / @JoinColumn annotations). init.sql often lacks actual FOREIGN KEY constraints. Define them as a list of tuples: `(source_table, fk_column, target_table, target_column)`.
3. Compute box positions -- layout tables in a logical parent-child tree
4. Generate SVG with dark theme (#0f172a background), colored table headers, PK (#facc15 yellow), FK (#22d3ee cyan), truncation counts for large tables
5. Write output to `docs/database-er-diagram.html` and `docs/database-er-diagram.svg`

The reusable script from the Enterprise MVP session is at `references/ddl-to-er-diagram.py`. It handles column type formatting, color per table, FK arrow routing with orthogonal polylines, dynamic box sizing, and dual HTML+SVG output. Copy and adapt for each project.

#### Approach B: Manual SVG coordinates (for small 3-5 table diagrams)

Draft SVG coordinates by hand for small schemas. Follow the layout rules below.

**SVG layout rules (dark theme, `#0f172a` background):**
- Table boxes: `<rect rx="8">`, header `<rect>` in module color with 0.6 opacity
- Header text: 13px bold in module color, entity class name 9px italic at end
- Field text: 9px `#94a3b8`, key fields like PK/FK at top
- Color scheme: declaration=`#34d399`, enterprise=`#a78bfa`, activity=`#22d3ee`, sys_user=`#fb7185`, document=`#fb923c`, predeclare=`#fbbf24`, policy=`#94a3b8`

**Arrow routing (CRITICAL — use orthogonal routing, NOT diagonal lines):**
```svg
<!-- Good: polyline with right-angle bends -->
<polyline points="310,100 650,100 650,198 338,198" fill="none" stroke="#64748b" stroke-width="1.5" marker-end="url(#arrow)"/>
<text x="480" y="96" fill="#64748b" font-size="8">fk_name</text>

<!-- Bad: diagonal line — DON'T USE -->
<line x1="170" y1="170" x2="420" y2="205" .../>
<text transform="rotate(-60,...)" .../> <!-- rotated text is hard to read -->
```

**Rules:**
- Every arrow path uses ONLY horizontal and vertical segments (right-angle bends)
- Use `<polyline points="x1,y1 x2,y2 x3,y3 x4,y4">` for multi-segment arrows
- Keep labels horizontal — never rotate text
- Route multiple FK lines from the same source table along a shared corridor then branch
- Straight vertical connections are cleanest (parent above child)
- Straight horizontal connections for sibling tables at same Y level

**Legend at bottom:**
- `<line marker-end>` = FK relationship
- Color dots explaining table type categories

### Phase 6: Update Documentation

Create/update these docs:

| File | Content |
|------|---------|
| `docs/DATABASE.md` | Complete field listing for all tables (grouped by module) — embed ER diagram SVG at top |
| `docs/SCHEMA.md` | Quick reference: table relationships + enum values + migration history — links to DATABASE.md |
| `docs/database-er-diagram.html` | Interactive ER diagram HTML (open in browser) |
| `docs/database-er-diagram.svg` | Standalone SVG for embedding in markdown |

Update `README.md` doc index and any other docs (HANDBOOK.md, BUSINESS.md, DEV.md) that reference database structure — replace inline field tables with links to `DATABASE.md`.

---

## Output Files

| File | Content |
|------|---------|
| `docs/DATABASE.md` | Complete field listing for all tables (grouped by module) |
| `docs/SCHEMA.md` | Quick reference: table relationships + enum values + migration history |
| `docs/database-er-diagram.html` | Visual ER diagram (HTML with inline SVG) |
| `docs/database-er-diagram.svg` | SVG for embedding in DATABASE.md |

---

## Pitfalls

- **init.sql vs migrations mismatch**: In projects that use init.sql directly (not Flyway migration chain), migration scripts may contain dead code or bugs that never caused problems. The answer to "迁移脚本为什么需要" is: they're historical deltas that document incremental changes, but init.sql is the source of truth. When auditing, check both and treat init.sql as authoritative. Fix migration scripts anyway for any future clean-DB setup. See `references/enterprise-mvp-migration-audit-202607.md` for a real audit with 7 categories of drift.
- **Entity field name ≠ SQL column name**: Java uses `@Column(name=...)` to remap. Always check for this annotation before asserting a mismatch.
- **Duplicated columns from "表单快照" sections**: Later migrations that add free-form field sections may introduce columns with the same meaning but different names (e.g. `ip_class1_self` in main section and `ip_class1self` in form data section). Cross-reference by content, not just column name.
- **Chinese column names**: These slip into migration scripts when developers type in Chinese IME. MySQL allows them but Java JPA field mapping breaks because camelCase doesn't apply.
- **Flyway schema_history vs actual DB state**: `flyway_schema_history` may show all migrations as "success" even if some ran partially. The only reliable source of truth is a fresh `init.sql` DDL snapshot.
- **macOS grep incompatibility**: The macOS `grep` lacks `-P` (Perl regex). Use `python3 -c` or `execute_code` for regex extraction instead of `grep -oP`.
- **Mermaid/PlantUML vs SVG**: For ER diagrams in repo docs, SVG HTML files are self-contained and render correctly on both GitHub and local. Mermaid requires a renderer.
- **Commit proactively**: User expects commits after each completed fix. Don't wait to be asked.
- **SVG arrow routing**: Users will notice messy diagonal arrows. Always use orthogonal routing (right-angle bends via `<polyline>`) and horizontal label text.
- **VARCHAR length mismatch**: Migration scripts often use narrower types (VARCHAR(64), VARCHAR(32)) while init.sql uses VARCHAR(255). Flyway-deployed DBs get narrower columns, which can cause INSERT truncation on long data. Always normalise to the wider length when syncing.
- **Reference case study**: See `references/enterprise-mvp-migration-audit-202607.md` for a complete walkthrough with 7 categories of discrepancies found in a single real project.
