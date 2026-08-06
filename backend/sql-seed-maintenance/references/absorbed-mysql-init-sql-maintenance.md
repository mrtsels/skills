---
name: mysql-init-sql-maintenance
category: devops
description: Maintain, verify, and convert monolithic MySQL init.sql files — single-file DDL + DML management, column count consistency checks, version compatibility (8.0↔5.7), and INSERT-to-CSV extraction for LOAD DATA INFILE.
---

# MySQL init.sql Maintenance

Manage a monolithic `init.sql` that combines DDL (CREATE TABLE) and DML (INSERT) into a single source of truth for database initialization.

## When to use

- You maintain a project where a single `init.sql` is the canonical schema + seed data source
- You need to verify column count consistency between CREATE TABLE and INSERT VALUES
- You need to produce a MySQL 5.7-compatible version of an 8.0-authored init.sql
- You need to split a monolithic init.sql into schema.sql + data CSV files
- You encounter "Column count doesn't match value count" errors on import

## Core techniques

### 1. Verify column count consistency

The most common init.sql bug: a column was added/removed from CREATE TABLE but the INSERT VALUES weren't updated to match. Use Python to parse and verify:

```python
import re

with open("init.sql") as f:
    content = f.read()

# Parse all CREATE TABLEs
tables = {}
for m in re.finditer(
    r"CREATE TABLE IF NOT EXISTS `(\w+)`\s*\((.*?)\)\s*ENGINE=",
    content, re.DOTALL
):
    cols = re.findall(r"^\s*`(\w+)`", m.group(2), re.MULTILINE)
    tables[m.group(1)] = cols

# Parse all INSERT blocks and count VALUES per row
def count_values(row_text, handle_quotes=True):
    """Count top-level comma-separated SQL values in a row."""
    v = 1
    in_q = False
    bd = 0
    i = 0
    while i < len(row_text):
        c = row_text[i]
        if in_q:
            if c == '\\' and i+1 < len(row_text):
                i += 2; continue
            elif c == "'":
                if i+1 < len(row_text) and row_text[i+1] == "'":
                    i += 2; continue
                in_q = False
            i += 1
        else:
            if c == "'": in_q = True; i += 1
            elif c in ('[', '{'): bd += 1; i += 1
            elif c in (']', '}'): bd -= 1; i += 1
            elif c == ',' and bd == 0: v += 1; i += 1
            else: i += 1
    return v
```

The `count_values` function is the critical piece. It must handle:
- Single-quoted strings (track `in_q`)
- JSON brackets `[]` and `{}` inside values (track `bd` — don't count commas inside JSON)
- MySQL escape sequences (`\'`, `''`, `\\`, `\n`)

### 2. MySQL 5.7 compatibility conversion

Three changes needed when converting from MySQL 8.0 to 5.7:

| Issue | MySQL 8.0 | MySQL 5.7 | Why |
|-------|-----------|-----------|-----|
| Collation | `utf8mb4_0900_ai_ci` | `utf8mb4_general_ci` | `_0900_*` collations require MySQL 8.0 |
| Bit true | `_binary '\x01'` or `_binary '\u0001'` | `b'1'` | `\u` Unicode escapes need 8.0.19+; `_binary` byte literals can cause encoding issues |
| Bit false | `_binary '\0'` | `b'0'` | `_binary` is usable in 5.7 but `b'0'` is cleaner and more portable |

Python byte-level replacement (safest approach — works on raw file):

```python
with open("init.sql", "rb") as f:
    data = f.read()

data = data.replace(b"utf8mb4_0900_ai_ci", b"utf8mb4_general_ci")
data = data.replace(b"_binary '\\0'", b"b'0'")
data = data.replace(b"_binary '\x01'", b"b'1'")  # literal byte 0x01

with open("init_compatible.sql", "wb") as f:
    f.write(data)
```

### 3. Long-line splitting (MySQL 5.7 client buffer)

The MySQL 5.7 command-line client (especially on Windows through DBeaver) has a limited input line buffer (~64KB). A single multi-row INSERT with text columns (e.g., policy `content`) can exceed this.

**Fix:** Split into individual INSERT statements per row.

```python
# Parse multi-row INSERT and emit single-row INSERTs
rows = []  # parse row by row
for row_inner in rows:
    print(f"INSERT INTO `{table}` VALUES ({row_inner});")
```

### 4. SQL-to-CSV extraction

Extract INSERT data into CSV files for `LOAD DATA INFILE`.

Key rules for the CSV converter:
- `NULL` → `\N` (MySQL LOAD DATA convention)
- SQL strings → unescaped with `\\n`→newline, `\\t`→tab, `\\`→`\`, `''`→`'`, `\\"`→`"`
- **Do NOT pre-quote CSV fields** — let `csv.writer` handle quoting
- Bit literals `b'0'`/`b'1'` → `0`/`1`

```python
import csv

def sql_value_to_csv(val):
    """Convert SQL literal to raw value for csv.writer."""
    val = val.strip()
    if val.upper() == 'NULL':
        return None  # csv.writer writes empty → \N
    
    if val.startswith("'") and val.endswith("'"):
        inner = val[1:-1]
        inner = inner.replace("\\n", "\n")
        inner = inner.replace("\\t", "\t")
        inner = inner.replace("\\\\", "\\")
        inner = inner.replace("\\'", "'")
        inner = inner.replace('\\"', '"')
        inner = inner.replace("''", "'")
        return inner
    
    if val.startswith("b'") and val.endswith("'"):
        return val[2:-1]
    
    return val
```

### 5. LOAD DATA INFILE generation

```sql
LOAD DATA LOCAL INFILE 'data/table.csv'
  INTO TABLE `table`
  CHARACTER SET utf8mb4
  FIELDS TERMINATED BY ',' OPTIONALLY ENCLOSED BY '"'
  LINES TERMINATED BY '\n'
  IGNORE 1 LINES
  (col1, col2, ...);
```

Note: `OPTIONALLY ENCLOSED BY '"'` means CSV fields are only quoted when needed (contain comma, newline, or quote). Fields without special chars are bare.

## Pitfalls

### Column count mismatch after column deletion

A column was removed from CREATE TABLE but the INSERT VALUES still have the corresponding value. **Always verify** after any DDL change that touches the column list.

The mismatch often manifests as:
```
ERROR 1136 (21S01): Column count doesn't match value count at row 1
```

On MySQL 8.0 and 5.7 — no version difference here, this is a pure file bug.

### `\u` in string literals

In MySQL 8.0.19+, `'\u0001'` inside a single-quoted string is a Unicode escape (U+0001). In MySQL < 8.0.19 and 5.7, it's the literal string `\u0001`. This means `_binary '\u0001'` inserts different bytes depending on MySQL version.

**Don't use `\u` in MySQL string literals** if you need version compatibility. Use `b'1'` for bit values or `x'01'` for hex bytes.

### mysql.exe line buffer on Windows

The MySQL 5.7 client on Windows reads input line-by-line with a fixed buffer (~64KB). Single-line INSERT statements exceeding this will be truncated, and the tail content (often starting with `\"`) gets interpreted as MySQL client backslash-commands (`Unknown command '\"'`).

**Fix:** Ensure no single line exceeds ~50KB, or split into individual INSERT statements.

### utf8mb4_0900_ai_ci not available on MySQL 5.7

The `utf8mb4_0900_ai_ci` collation was introduced in MySQL 8.0.16. On MySQL 5.7, all CREATE TABLE statements using it will fail with:
```
ERROR 1273 (HY000): Unknown collation: 'utf8mb4_0900_ai_ci'
```

Replace with `utf8mb4_general_ci` or `utf8mb4_unicode_ci` before running on 5.7.

## References

- [MySQL 5.7 String Literals](https://dev.mysql.com/doc/refman/5.7/en/string-literals.html)
- [MySQL LOAD DATA INFILE](https://dev.mysql.com/doc/refman/5.7/en/load-data.html)
- [MySQL Bit-Value Literals](https://dev.mysql.com/doc/refman/5.7/en/bit-value-literals.html)
