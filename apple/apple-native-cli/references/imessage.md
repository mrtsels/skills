# iMessage (Reference)

## Prerequisites
- macOS with Messages.app signed in
- `brew install steipete/tap/imsg`
- Grant Full Disk Access for terminal
- Grant Automation permission for Messages.app

## List Chats

```bash
imsg chats --limit 10 --json
```

## View History

```bash
imsg history --chat-id 1 --limit 20 --json
imsg history --chat-id 1 --limit 20 --attachments --json
```

## Send Messages

```bash
imsg send --to "+141****1212" --text "Hello!"
imsg send --to "+141****1212" --text "Check this" --file /path/to/image.jpg
imsg send --to "+141****1212" --text "Hi" --service imessage
imsg send --to "+141****1212" --text "Hi" --service sms
imsg send --to "+141****1212" --text "Hi" --service auto
```

## Watch for New Messages

```bash
imsg watch --chat-id 1 --attachments
```

## Service Options
- `--service imessage` — Force iMessage (blue bubble)
- `--service sms` — Force SMS (green bubble)
- `--service auto` — Let Messages.app decide (default)

## Workflow Example

```bash
# 1. Find recipient's chat
imsg chats --limit 20 --json | jq '.[] | select(.displayName | contains("Mom"))'

# 2. Confirm with user, then send
imsg send --to "+155****3456" --text "I'll be late"
```
