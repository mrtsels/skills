# YouTube Content — Reference

## Fetch transcript

```bash
python3 SKILL_DIR/scripts/fetch_transcript.py "https://youtube.com/watch?v=VIDEO_ID"
python3 SKILL_DIR/scripts/fetch_transcript.py "URL" --text-only
python3 SKILL_DIR/scripts/fetch_transcript.py "URL" --timestamps
python3 SKILL_DIR/scripts/fetch_transcript.py "URL" --language tr,en
```

Accepts standard YouTube URLs, youtu.be shorts, embeds, live links, or raw 11-char video ID.

## Output formats

After fetching the transcript, transform based on user request:

- **Chapters**: Group by topic shifts, output timestamped chapter list
- **Summary**: Concise 5-10 sentence overview
- **Chapter summaries**: Chapters with paragraph summary each
- **Thread**: Twitter/X thread — numbered posts, each under 280 chars
- **Blog post**: Full article with title, sections, takeaways
- **Quotes**: Notable quotes with timestamps

### Example — Chapters Output

```
00:00 Introduction
03:45 Background
12:20 Core method
24:10 Results
31:55 Q&A
```

## Workflow

1. Fetch with `--text-only --timestamps`
2. Validate: non-empty, expected language. If empty, retry without --language
3. Chunk: if transcript > ~50K chars, split into overlapping ~40K chunks
4. Transform into requested format
5. Default: summary if no format specified

## Error handling

- **Transcript disabled**: Tell user; suggest checking subtitles availability
- **Private/unavailable**: Relay error, ask user to verify URL
- **No matching language**: Retry without --language, note actual language
- **Dependency missing**: `pip install youtube-transcript-api` and retry
