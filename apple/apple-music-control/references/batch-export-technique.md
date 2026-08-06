# Batch Export Technique: Large Apple Music Libraries

## Problem
AppleScript iterates through tracks one-by-one via Apple Events, making it very slow for libraries with 1000+ tracks (roughly 15-20 seconds per 250 tracks sequentially).

## Solution: Parallel Batched osascript Processes

Split the track range into chunks and run one osascript process per chunk **in parallel**.

### Script: `export_batch.applescript`

```applescript
on run argv
    set startIdx to (item 1 of argv) as integer
    set endIdx to (item 2 of argv) as integer
    
    tell application "Music"
        set output to ""
        repeat with i from startIdx to endIdx
            try
                set t to track i of library playlist 1
                set tn to name of t
                set ta to artist of t
                set tal to album of t
                set tg to genre of t
                set ty to year of t
                set output to output & i & "|" & tn & "|" & ta & "|" & tal & "|" & tg & "|" & ty & (ASCII character 10)
            end try
        end repeat
        return output
    end tell
end run
```

### Parallel Execution

Launch all batches with `background=true` to run simultaneously:

```bash
# For 2500 tracks, batch size 250:
for i in $(seq 0 9); do
  start=$((i * 250 + 1))
  end=$(((i + 1) * 250))
  osascript export_batch.applescript $start $end > /tmp/batch_$i.txt &
done
wait  # wait for all
cat /tmp/batch_*.txt > all_tracks.txt
```

This completes a 2500-track export in ~20 seconds (vs ~3 minutes sequentially).

### Pitfalls

1. **AppleScript handler functions break in `-e` strings** — Multi-line osascript with `on handler` definitions gets mangled by bash quoting. Always write complex AppleScript to a `.applescript` file and run `osascript file.applescript`.

2. **Output size limits** — osascript stdout can handle 40K+ chars per call, but individual track fields containing pipe (`|`) or newline characters break delimiter-based parsing. Escape them in the AppleScript before output.

3. **Missing tracks** — Some tracks may fail with `-1728` (object not found) errors due to data inconsistencies. Expect ~1-2% loss. Account for this in downstream analysis.

4. **MinimX playlist export** — Since `search` only works on `library playlist 1`, exporting a user playlist requires a different script that iterates `tracks of p` directly via `repeat with i from 1 to count of tracks of p`.

### Usage Example (Hermes environment)

```python
from hermes_tools import terminal

# Start parallel exports
sessions = []
for batch_start in range(1, 2501, 250):
    batch_end = min(batch_start + 249, 2500)
    r = terminal(
        f"osascript /tmp/export_batch.applescript {batch_start} {batch_end} 2>/dev/null > /tmp/batch_{batch_start}.txt",
        timeout=60, workdir="/Users/minimx", background=True,
        notify_on_complete=True
    )
    sessions.append(r.get("session_id"))

# Wait for all and combine
# ... (check process status, then cat together)
```
