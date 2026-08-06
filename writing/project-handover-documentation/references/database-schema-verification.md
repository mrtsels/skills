# Database Schema Verification & Documentation

When a handover doc needs its database section verified or created from scratch, follow this audit pipeline.

## 1. Schema Extraction

Source files to read:
- **`init.sql`** or equivalent DDL — the single-source-of-truth for schema (if Flyway is not used in production)
- **`backend/src/main/resources/db/migration/*.sql`** — the migration chain (may contain drift vs init.sql)
- **Java Entity classes** (`@Entity` + `@Table(name=...)`) — the JPA mappings

## 2. Entity ↔ SQL Cross-Reference

### Field mapping convention

JPA entity fields follow camelCase; SQL columns follow snake_case. But `@Column(name="...")` can override:
- Plain field `private String creditCode;` → SQL column `credit_code`
- Custom mapping `@Column(name="group_name") private String materialType;` → SQL column `group_name`

### Cross-reference approach (Python)

```python
import re

def camel_to_snake(name):
    """Convert camelCase to snake_case, handling edge cases like ipClass1Self."""
    return re.sub(r'([a-z0-9])([A-Z])', r'\1_\2', name).lower()

# 1. Read entity file, extract:
#    - @Table(name) for table name
#    - @Column(name="...") overrides → {javaField: sqlColumn}
#    - All private field names → Set[str]

# 2. Read init.sql, extract column names per CREATE TABLE block

# 3. Cross-reference:
#    - For each Java field: convert to expected SQL col → check exists in DDL
#    - For each SQL col: reverse-lookup a matching Java field
#    - Flag orphans (SQL cols with no Java field) and missing (Java fields with no SQL col)
```

### Common pitfalls

| Pattern | What to flag |
|---------|-------------|
| Repeated `ALTER TABLE ADD COLUMN` across migrations | Should use `IF NOT EXISTS` on re-runnable migrations |
| `CREATE TABLE` with same name in two different migrations | First one creates it, second one FAILS |
| Chinese characters in column names (`fin精细化_score`) | Worked by accident, breaks tooling |
| Near-duplicate column names (`ip_class1self` vs `ip_class1_self`) | Java entity maps to only one — the other is a dead column |
| `@Column(name=...)` where the name doesn't match expected snake_case | Intentional or confusing? Check with context |

## 3. Migration Chain Audit

When Flyway migrations are present, do NOT just read init.sql — the migration chain has its own failure modes:

### Sequential correctness

```bash
# For each migration file in version order:
# 1. Does it CREATE a table that a PREVIOUS migration already created?
# 2. Does it ALTER TABLE ADD COLUMN (without IF NOT EXISTS) on a table
#    that a LATER migration might also alter?
# 3. Does it DROP a table that a later migration still references?
```

### Special case: init.sql as snapshot

If the project uses `init.sql` (not Flyway) for production DB setup, the migrations can have bugs that never surface in production. Document this in the Known Issues section.

## 4. ER Diagram Generation

Generate a standalone HTML/SVG that shows tables with entity class names annotated.

### Layout pattern

```
enterprise (Enterprise.java)        sys_user (UserAccount.java)         policy (Policy.java)
    ├── declaration (Declaration.java)
    │     ├── declaration_material (DeclarationMaterial.java)
    │     │     └── document (Document.java)
    │     └── predeclare (Predeclare.java)
    │
    ├── activity_registration (ActivityRegistration.java)
    │     └── activity_participant (ActivityParticipant.java)
    │           └── activity (Activity.java)
    │
    └── document (Document.java)
```

### Implementation approach

Write inline SVG inside a standalone HTML file. Each table is a rounded rectangle with:
- Header: table name (bold) + entity class name (italic, smaller, right-aligned)
- Body: key fields (PK, FK, UNIQUE annotations)
- Arrow lines between tables for FK relations

Use a dark theme (`#0f172a` background) with color-coded borders per table type (database=violet, backend=emerald, frontend=cyan, security=rose).

Self-contained: embed all CSS/JS/SVG inline, load only Google Fonts externally.

## 5. Documentation Deduplication

When multiple docs reference the same DB schema (HANDBOOK.md + SCHEMA.md + README.md), choose ONE authoritative location and redirect others:

| Role | File | Content density |
|------|------|----------------|
| Full reference | `docs/DATABASE.md` | Every field, type, constraint, business meaning |
| Quick overview | `docs/SCHEMA.md` | Table relationships diagram + enum values + redirect |
| Handover compact | `HANDBOOK.md` | Single-line summary per table + link to DATABASE.md |
| Index | `README.md` | One-line link in doc table |

Procedure:
1. Create DATABASE.md with full field tables (auto-generated from cross-reference)
2. Update SCHEMA.md to be a redirect/quick-reference
3. In HANDBOOK.md, replace all detailed field tables with a table-of-tables + link
4. Add DATABASE.md to README.md document index
