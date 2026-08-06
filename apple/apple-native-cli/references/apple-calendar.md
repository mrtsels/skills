# Apple Calendar SQLite DB Reference

## Database Location

macOS 27+ stores Calendar data at:
```
~/Library/Group Containers/group.com.apple.calendar/Calendar.sqlitedb
```

## Time Encoding

macOS Calendar uses **Mac Absolute Time** — seconds since 2001-01-01 00:00:00 UTC.

**Conversion:** `unix_epoch = mac_absolute_time + 978307200`

```sql
-- Mac Absolute Time → human-readable
SELECT datetime(start_date + 978307200, 'unixepoch', 'localtime') FROM CalendarItem;

-- Filter by "recent and future"
WHERE start_date + 978307200 >= strftime('%s', 'now')
```

## Key Tables

### `Calendar` — calendar folders

| Column | Type | Description |
|--------|------|-------------|
| `rowid` | INTEGER | PK |
| `title` | TEXT | Calendar name (e.g., "個人", "工作", "Chloe") |

### `CalendarItem` — individual events

| Column | Type | Description |
|--------|------|-------------|
| `rowid` | INTEGER | PK |
| `summary` | TEXT | Event title |
| `start_date` | REAL | Mac Absolute Time |
| `start_tz` | TEXT | Timezone (e.g., "Asia/Shanghai") |
| `end_date` | REAL | End time (Mac Absolute Time) |
| `end_tz` | TEXT | End timezone |
| `all_day` | INTEGER | 0 or 1 |
| `calendar_id` | INTEGER | FK → Calendar.rowid |
| `location_id` | INTEGER | FK → Location.rowid |
| `url` | TEXT | Associated URL |
| `hidden` | INTEGER | 0 = visible, 1 = hidden/deleted |
| `UUID` | TEXT | Unique identifier |
| `has_recurrences` | INTEGER | 1 if event has recurrence rules |
| `description` | TEXT | Event body/notes |

### `Recurrence` — recurrence rules for repeating events

| Column | Type | Description |
|--------|------|-------------|
| `rowid` | INTEGER | PK |
| `owner_id` | INTEGER | FK → CalendarItem.rowid |
| `frequency` | INTEGER | 1=day, 2=week, 3=month, 4=year |
| `interval` | INTEGER | Every N periods (1=every period) |
| `week_start` | INTEGER | 1=Sunday, 2=Monday |
| `count` | INTEGER | Max occurrences (0=unlimited, bounded by end_date) |
| `end_date` | REAL | Recurrence end (Mac Absolute Time) |
| `specifier` | TEXT | Day specifier: `D=0MO` (Monday), `D=0WE` (Wednesday), `D=0SA` (Saturday), etc. |

### `ExceptionDate` — exceptions (cancelled/rescheduled instances)

| Column | Type | Description |
|--------|------|-------------|
| `owner_id` | INTEGER | FK → CalendarItem.rowid |
| `date` | REAL | Cancelled instance date (Mac Absolute Time) |

## Common Queries

### Upcoming personal events (exclude system calendars)
```bash
sqlite3 "$HOME/Library/Group Containers/group.com.apple.calendar/Calendar.sqlitedb" "
SELECT datetime(ci.start_date + 978307200, 'unixepoch', 'localtime') AS dt,
       ci.summary,
       c.title AS calendar
FROM CalendarItem ci
JOIN Calendar c ON ci.calendar_id = c.rowid
WHERE ci.start_date + 978307200 >= strftime('%s','now')
  AND ci.hidden = 0
  AND c.title NOT IN ('中國節日','台灣節日','Facebook Birthdays','生日')
ORDER BY ci.start_date
LIMIT 30;"
```

### All calendars with event counts
```bash
sqlite3 "$HOME/Library/Group Containers/group.com.apple.calendar/Calendar.sqlitedb" "
SELECT c.title, count(ci.rowid) AS events
FROM Calendar c
LEFT JOIN CalendarItem ci ON ci.calendar_id = c.rowid AND ci.hidden = 0
GROUP BY c.rowid
ORDER BY c.title;"
```

### Events in a date range
```bash
sqlite3 "$HOME/Library/Group Containers/group.com.apple.calendar/Calendar.sqlitedb" "
SELECT datetime(start_date + 978307200, 'unixepoch', 'localtime'),
       summary
FROM CalendarItem
WHERE hidden = 0
  AND start_date + 978307200 BETWEEN strftime('%s','2026-07-01')
                                  AND strftime('%s','2026-07-31')
ORDER BY start_date;"
```

### Recurrence: decode repeating events' schedule

Useful for understanding weekly/monthly programs. Join CalendarItem with Recurrence on `CalendarItem.rowid = Recurrence.owner_id`.

```bash
sqlite3 "$HOME/Library/Group Containers/group.com.apple.calendar/Calendar.sqlitedb" "
SELECT ci.summary,
       r.frequency,
       r.interval,
       r.count,
       datetime(r.end_date + 978307200, 'unixepoch', 'localtime') AS end_dt,
       r.specifier
FROM Recurrence r
JOIN CalendarItem ci ON r.owner_id = ci.rowid
WHERE r.owner_id IN (<event_rowids>);"
```

**Decoding specifier:** `D=0SA` = Every Saturday, `D=0WE` = Every Wednesday, `D=0MO` = Every Monday.
Format: `D=<offset><day_code>` where offset is 0 (no offset) and day codes are MO/TU/WE/TH/FR/SA/SU.

**Frequency codes:** 1=Daily, 2=Weekly, 3=Monthly, 4=Yearly.

**Count = 0** means "no occurrence limit, bounded by end_date".

**Example:** An event with frequency=2, interval=1, specifier=`D=0SA`, end_date = 2026-08-01 = Every Saturday from start_date through August 1.

### Schema inspection
```bash
sqlite3 "..." ".tables"                         # List tables
sqlite3 "..." "PRAGMA table_info(CalendarItem);"  # Show columns
```

## Calendar Types (common on Chinese/HK systems)

| Calendar Name | Type | Notes |
|---------------|------|-------|
| 個人 | Personal | User's own events |
| 工作 | Work | Work schedule |
| 行事曆 | Calendar | General (often iCloud synced) |
| 家庭共享 | Family | Family sharing calendar |
| Chloe | Person | Shared calendar with partner |
| 中國節日 | System | PRC public holidays |
| 台灣節日 | System | Taiwan public holidays |
| 生日 | System | Contact birthdays |
| Google / iCloud | Sync | Synced from cloud accounts |
| Found in Mail | Auto | Detected from email |
| Found in Natural Language | Auto | Detected from text |
| Scheduled Reminders | Auto | Reminders integration |

## Privacy Notes

- Calendar.sqlitedb may require Full Disk Access permission to query
- The database file is locked while Calendar.app is open (read-only queries still work)
- Holiday calendars (中國節日, 台灣節日) contain all future dates — always filter them out for personal queries
