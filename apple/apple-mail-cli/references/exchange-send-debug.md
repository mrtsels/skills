# Exchange (EWS) Send Debugging Notes

## Root Cause of Draft Artifacts

Exchange/EWS accounts in Mail.app process outgoing messages asynchronously on the server. When AppleScript calls `send newMsg`:

1. Mail.app creates an `outgoing message` object locally
2. `send` queues it in the local Outbox (`local://.../Outbox`)
3. Exchange server picks up the Outbox, creates a **server-side draft** in `ews://<uuid>/草稿` (Drafts)
4. Exchange processes the SMTP delivery via its own MTA
5. On success, the message moves to `ews://<uuid>/寄件備份` (Sent Items)
6. The draft **remains** in the Drafts folder — Exchange keeps it as a sent-artifact

### Why cleanup fails

AppleScript `delete msg` on an Exchange draft:
```
tell application "Mail"
    delete msg in mailbox "草稿" of account "CUHK"
end tell
```

This deletes the local representation. On the next Exchange folder sync, the server re-creates the draft entry because the server-side copy wasn't deleted. Exchange doesn't expose a "delete draft after send" flag through EWS AppleScript.

## AppleScript Limitations for SMTP Relay

| Attempt | Result |
|---------|--------|
| `set account of newMsg to acct` | Error -10006: cannot set property on outgoing message after creation |
| `make new outgoing message at end of outgoing messages of acct` | Error -1728: cannot access outgoing messages of account through AppleScript |
| `make new outgoing message with properties {account:acct}` | Error: cannot make properties (account is not a valid property of outgoing message) |

## Account Routing Behavior

When `sender` is set in AppleScript's `make new outgoing message with properties`:

- **Without `sender`**: Uses the account at position 0 in AccountOrdering
- **With `sender` matching an existing account**: Routes through THAT account's outbound server
- **With `sender` not matching any account**: Uses AccountOrdering[0]'s SMTP with custom From header

**AccountOrdering location:**
```
~/Library/Containers/com.apple.mail/Data/Library/Preferences/com.apple.mail.plist
→ key "AccountOrdering" (array of URL strings)
```

## Delivery Behavior

| From → To | Latency | Draft Artifact | Notes |
|-----------|---------|----------------|-------|
| Exchange → same Exchange | Instant | Yes | Inbox delivery |
| Exchange → iCloud | 10-60s | Yes | May hit iCloud Junk on rapid repeats |
| Exchange → Gmail | 10-60s | Yes | Standard cross-provider |
| iCloud → iCloud | Near-instant | No | Clean send |
| Gmail → Gmail | Near-instant | No | Clean send |

## Workarounds

1. **Accept the draft**: Inform the user that Exchange draft artifacts are normal.
2. **Use iCloud as default**: Rearrange AccountOrdering so iCloud is position 0. Then without `sender`, all sends go through iCloud SMTP (clean, instant).
3. **Reply-To approach**: Send via iCloud (clean), set Reply-To to CUHK address. The From will be iCloud but replies go to CUHK.
4. **Delete after delay**: Send, wait 5-10s for Exchange draft to appear, then call delete. Unreliable due to server sync timing.

## Verification Commands

After sending, check message location in DB:
```sql
SELECT s.subject,
  CASE
    WHEN mb.url LIKE '%草稿%' THEN 'DRAFT'
    WHEN mb.url LIKE '%寄件備份%' THEN 'SENT(Exch)'
    WHEN mb.url LIKE '%Sent%' THEN 'SENT'
    WHEN mb.url LIKE '%INBOX%' OR mb.url LIKE '%收件匣%' THEN 'INBOX'
    WHEN mb.url LIKE '%Junk%' OR mb.url LIKE '%垃圾%' THEN 'JUNK'
    WHEN mb.url LIKE '%Outbox%' THEN 'OUTBOX'
  END as location
FROM messages m
JOIN subjects s ON m.subject = s.ROWID
JOIN mailboxes mb ON m.mailbox = mb.ROWID
WHERE s.subject LIKE '%query%';
```

Check AccountOrdering:
```bash
defaults read ~/Library/Containers/com.apple.mail/Data/Library/Preferences/com.apple.mail.plist AccountOrdering
```

List accounts via AppleScript:
```applescript
tell application "Mail"
    set out to ""
    repeat with a in every account
        set out to out & name of a & " | id: " & id of a & return
    end repeat
    return out
end tell
```
