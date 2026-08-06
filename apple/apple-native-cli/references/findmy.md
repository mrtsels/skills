# FindMy (Reference)

Track Apple devices and AirTags via FindMy.app on macOS. No official CLI — uses AppleScript + screencapture + optional peekaboo.

## Prerequisites
- macOS with Find My app and iCloud signed in
- Screen Recording permission for terminal
- Optional: `brew install steipete/tap/peekaboo` for better UI automation

## Open and Capture

```bash
osascript -e 'tell application "FindMy" to activate'
sleep 3
screencapture -w -o /tmp/findmy.png
# Then use vision_analyze to read the screenshot
```

## Switch Between Tabs

```bash
osascript -e '
tell application "System Events"
    tell process "FindMy"
        click button "Devices" of toolbar 1 of window 1
    end tell
end tell'

# or "Items" tab for AirTags
```

## Peekaboo UI Automation (if installed)

```bash
osascript -e 'tell application "FindMy" to activate'
sleep 3
peekaboo see --app "FindMy" --annotate --path /tmp/findmy-ui.png
peekaboo click --on B3 --app "FindMy"
peekaboo image --app "FindMy" --path /tmp/findmy-detail.png
```

## Track AirTag Location Over Time

```bash
osascript -e 'tell application "FindMy" to activate'
sleep 3
# Click on the AirTag item
while true; do
    screencapture -w -o /tmp/findmy-$(date +%H%M%S).png
    sleep 300  # Every 5 minutes
done
```

## Limitations
- AirTags only update location while page is actively displayed
- Location accuracy depends on nearby Apple devices in FindMy network
- AppleScript UI automation may break across macOS versions
