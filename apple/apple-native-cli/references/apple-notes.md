# Apple Notes (Reference)

## Prerequisites
- macOS with Notes.app
- `brew tap antoniorodr/memo && brew install antoniorodr/memo/memo`
- Grant Automation access to Notes.app when prompted

## Commands

```bash
memo notes                        # List all notes
memo notes -f "Folder Name"       # Filter by folder
memo notes -s "query"             # Search notes (fuzzy)
memo notes -a                     # Interactive editor
memo notes -a "Note Title"        # Quick add with title
memo notes -e                     # Interactive selection to edit
memo notes -d                     # Interactive selection to delete
memo notes -m                     # Move note to folder (interactive)
memo notes -ex                    # Export to HTML/Markdown
```

## Limitations
- Cannot edit notes containing images or attachments
- Interactive prompts require terminal access (use pty=true if needed)
- macOS only — requires Apple Notes.app
