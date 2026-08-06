# GIF Search (Tenor API) — Reference

## Setup

```bash
TENOR_API_KEY=your_key_here     # Add to ~/.hermes/.env
```

Get a free key at https://developers.google.com/tenor/guides/quickstart

## Search

```bash
# Get GIF URLs
curl -s "https://tenor.googleapis.com/v2/search?q=thumbs+up&limit=5&key=${TENOR_API_KEY}" | jq -r '.results[].media_formats.gif.url'

# Smaller previews
curl -s "https://tenor.googleapis.com/v2/search?q=nice+work&limit=3&key=${TENOR_API_KEY}" | jq -r '.results[].media_formats.tinygif.url'
```

## Download

```bash
URL=$(curl -s "https://tenor.googleapis.com/v2/search?q=celebration&limit=1&key=${TENOR_API_KEY}" | jq -r '.results[0].media_formats.gif.url')
curl -sL "$URL" -o celebration.gif
```

## Full metadata

```bash
curl -s "https://tenor.googleapis.com/v2/search?q=cat&limit=3&key=${TENOR_API_KEY}" | \
  jq '.results[] | {title, url: .media_formats.gif.url, preview: .media_formats.tinygif.url}'
```

## API parameters

| Parameter | Description |
|---|---|
| `q` | Query (URL-encode spaces as `+`) |
| `limit` | Max results (1-50, default 20) |
| `media_filter` | Format filter: `gif`, `tinygif`, `mp4`, `tinymp4`, `webm` |
| `contentfilter` | Safety: `off`, `low`, `medium`, `high` |
| `locale` | Language: `en_US`, `es`, `fr`, etc. |

## Media formats

| Format | Use |
|--------|-----|
| `gif` | Full quality |
| `tinygif` | Small preview |
| `mp4` | Video version (smaller) |
| `webm` | WebM video |
