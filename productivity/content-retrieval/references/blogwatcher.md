# Blogwatcher — Reference

## Installation

Pick one:
- **Go:** `go install github.com/JulienTant/blogwatcher-cli/cmd/blogwatcher-cli@latest`
- **Binary:** Download from https://github.com/JulienTant/blogwatcher-cli/releases
- **Docker:** `docker run --rm -v blogwatcher-cli:/data -e BLOGWATCHER_DB=/data/blogwatcher-cli.db ghcr.io/julientant/blogwatcher-cli scan`

## Managing blogs

```bash
blogwatcher-cli add "My Blog" https://example.com
blogwatcher-cli add "Blog" https://example.com --feed-url https://example.com/feed.xml
blogwatcher-cli add "Blog" https://example.com --scrape-selector "article h2 a"
blogwatcher-cli blogs                                   # List all
blogwatcher-cli remove "My Blog" --yes                  # Remove
blogwatcher-cli import subscriptions.opml               # Import OPML
```

## Scanning and reading

```bash
blogwatcher-cli scan                                    # Scan all blogs
blogwatcher-cli scan "My Blog"                          # Scan one
blogwatcher-cli articles                                # Unread articles
blogwatcher-cli articles --all                          # All articles
blogwatcher-cli articles --blog "My Blog"               # Filter by blog
blogwatcher-cli read 1                                  # Mark read
blogwatcher-cli read-all --yes                          # Mark all read
```

## Environment variables

| Variable | Description |
|---|---|
| `BLOGWATCHER_DB` | Path to SQLite database |
| `BLOGWATCHER_WORKERS` | Concurrent scan workers (default: 8) |
| `BLOGWATCHER_SILENT` | Only output "scan done" |
| `BLOGWATCHER_YES` | Skip confirmation prompts |
| `BLOGWATCHER_CATEGORY` | Default article category filter |
