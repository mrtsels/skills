# macOS System Settings Navigation

Practical patterns for driving System Settings via computer-use tools (MCP or Hermes `computer_use` wrapper).

## Opening System Settings

Use `list_apps` to check if System Settings is running. If available in the list (even as "last-used"), `get_app_state(app="System Settings")` launches it.

## The Sidebar: getting to specific panes

System Settings has a sidebar with ~39 items. There are two strategies:

### Strategy A: Tab → Arrow Down (reliable, works every time)

1. Capture (`get_app_state("System Settings")`)
2. If the search text field has focus, press **Tab** once — focus moves to the sidebar `collectionView` (AX list)
3. Press **Down** (or **Up**) repeatedly to scroll through items. Each press moves to the next sidebar entry and loads that pane
4. After reaching the target, **click** on the selected item button to ensure the right pane loads

### Strategy B: Search (unreliable — search may not filter)

- Use `set_value` on the search text field (element with `Placeholder: Search`)
- In some macOS versions, the search may not actually filter the sidebar
- If it doesn't work, fall back to Strategy A

### Sidebar item order (approximate from top)

General → Accessibility → Appearance → Desktop & Dock → Displays → Menu Bar → Siri → Spotlight → Wallpaper → Notifications → Sound → Focus → Screen Time → Lock Screen → **Privacy & Security** → …

Privacy & Security is roughly at position 20-22 of 39 (about 44% down).

## Authentication dialogs

Many sensitive settings (Location Services, Full Disk Access, accessibility permissions, etc.) trigger a system authentication sheet:

```
Touch ID or enter your password to continue with Privacy & Security.
Buttons: [Use Password…] [Cancel]
```

**These cannot be bypassed programmatically** — there is no API, no CLI, and no credential the computer-use tools can provide. Always:

1. Cancel the dialog (click the Cancel button)
2. Report to the user: "I can open the relevant settings pane for you, but toggling this setting requires your password. I've left it open — please authenticate to complete the change."

## Click targets in Privacy & Security

When the "Privacy & Security" pane is loaded, sub-items include:

- "Location Services, N apps" — button that opens the Location Services sub-pane
- "Calendars", "Contacts", "Files & Folders" — each has its own sub-pane
- "Full Disk Access", "Camera", "Microphone", etc.

These are **buttons** in the scroll area, not list items. Click them by element index.

## Location Services sub-pane

- Main toggle: `switch ID: Location_Services_Toggle`
- Individual app toggles follow the pattern `switch ID: <bundle_or_name>_Toggle`
- "System Services" section at bottom has a "Details…" button
- Scroll to see all apps (there can be 50+)

## Common pitfalls

- **Stale element indices**: After navigating to a new pane, re-capture the state before clicking. The AX tree changes completely when the right pane content switches.
- **Right pane doesn't update immediately**: After pressing Down to select the sidebar item, you may still see old right-pane content. Click the selected button to force the pane to load.
- **Element 30 is the search field**: The initial capture always shows the search at element 30. Don't confuse it with the text entry field element in the right pane.
- **Arrow key moves both selection AND loads pane**: Each Down key press advances selection by 1 and loads that pane. You don't need to click separately if the right pane content loads — but clicking is safer.
