# Apple Mail Envelope Index DB Reference

## Path

```
~/Library/Mail/V{9,10,11}/MailData/Envelope Index
```

Read-only connection: `sqlite3("file:path?mode=ro", uri=True)`

## Key Tables

### messages
| Column | Type | Description |
|--------|------|-------------|
| ROWID | INTEGER | Primary key — same as .emlx filename |
| subject | INTEGER | FK → subjects.ROWID |
| sender | INTEGER | FK → senders.ROWID |
| mailbox | INTEGER | FK → mailboxes.ROWID |
| date_received | INTEGER | Apple absolute time (+978307200 = Unix) |
| date_sent | INTEGER | Apple absolute time |
| read | INTEGER | 0=unread, 1=read |
| flagged | INTEGER | 0/1 |
| deleted | INTEGER | 0/1 |
| size | INTEGER | Bytes |
| document_id | TEXT | Serialized path (often binary junk, unreliable) |
| remote_id | INTEGER | IMAP/EWS UID |

### subjects
| Column | Type | Description |
|--------|------|-------------|
| ROWID | INTEGER | FK from messages.subject |
| subject | TEXT | Decoded subject line |

### mailboxes
| Column | Type | Description |
|--------|------|-------------|
| ROWID | INTEGER | FK from messages.mailbox |
| url | TEXT | e.g. `imap://<uuid>/INBOX`, `ews://<uuid>/收件匣` |
| unread_count | INTEGER | |
| total_count | INTEGER | |

### recipients
| Column | Type | Description |
|--------|------|-------------|
| message | INTEGER | FK → messages.ROWID |
| address | INTEGER | FK → addresses.ROWID |
| type | INTEGER | 0=TO, 1=FROM |
| position | INTEGER | Ordering within type |

### addresses
| Column | Type | Description |
|--------|------|-------------|
| ROWID | INTEGER | |
| address | TEXT | Email address |
| comment | TEXT | Display name |

### senders
| Column | Type | Description |
|--------|------|-------------|
| ROWID | INTEGER | FK from messages.sender |
| contact_identifier | TEXT | UUID:ABPerson (Contacts) or empty |

### sender_addresses
| Column | Type | Description |
|--------|------|-------------|
| address | INTEGER | FK → addresses.ROWID |
| sender | INTEGER | FK → senders.ROWID |

## EMLX File Structure

### Location
```
~/Library/Mail/V<ver>/<account-uuid>/<mailbox>.mbox/<folder-uuid>/Data/<n>/<m>/Messages/<id>.emlx
```

- `<id>` matches message ROWID
- `<n>`, `<m>` are opaque partition numbers
- `<folder-uuid>` is per-mailbox UUID
- `<account-uuid>` matches mailbox URL prefix

### Format
```
<content-length>\n
<RFC822 message bytes>
```

First line is the size of the RFC822 content in bytes as ASCII decimal. The rest is a standard RFC822/email message.

### Finding an emlx by message ID
```python
import glob
pattern = os.path.join(MAIL_DIR, "V10", "*", "*.mbox", "*", "Data", "*", "*", "Messages", f"{msg_id}.emlx")
matches = glob.glob(pattern, recursive=False)
# fallback: recursive glob
pattern = os.path.join(MAIL_DIR, "V10", "**", "Messages", f"{msg_id}.emlx")
```

## Timestamps

Apple absolute time → Unix: `ts + 978307200`
The offset 978307200 = seconds between 2001-01-01 (Apple epoch) and 1970-01-01 (Unix epoch).

## Chinese Mailbox URL Decoding

Common URL-encoded names in HK/TW Mail.app:
- `%E6%94%B6%E4%BB%B6%E5%8C%A3` → 收件匣 (Inbox)
- `%E5%AF%84%E4%BB%B6%E5%82%99%E4%BB%BD` → 寄件備份 (Sent)
- `%E5%9E%83%E5%9C%BE%E9%83%B5%E4%BB%B6` → 垃圾郵件 (Junk)
- `%E5%B7%B2%E5%88%AA%E9%99%A4%E7%9A%84%E9%A0%85%E7%9B%AE` → 已刪除的項目 (Trash)
- `%E8%8D%89%E7%A8%BF` → 草稿 (Drafts)
- `%E5%B0%81%E5%AD%98` → 封存 (Archive)
- `%E6%89%80%E6%9C%89%E9%83%B5%E4%BB%B6` → 所有郵件 (All Mail)
- `%E4%BA%A4%E8%AB%87%E8%A8%98%E9%8C%84` → 交談記錄 (Chats)
- `%E5%B7%A5%E4%BD%9C` → 工作 (Tasks)
- `%E6%97%A5%E8%AA%8C` → 日誌 (Logs)
- `%E8%A8%98%E4%BA%8B` → 記事 (Notes)

## AppleScript Locale Quirk

In zh-HK/zh-TW locale, `message id N` syntax fails with:
```
「數字」不能在「屬性」之後 (-2740)
預期的是行尾，但找到的是識別碼 (-2741)
```

Workaround: use `open <emlx_path>` to open in Mail.app, or get message reference via mailbox iteration (slow for large mailboxes).
