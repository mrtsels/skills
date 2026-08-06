# GitHub Profile README

A special repo named `<username>/<username>` (e.g., `mrtsels/mrtsels`) whose `README.md` appears on the user's GitHub profile page.

## Key Facts

- Repo must be **public** and **named exactly the same as the GitHub username**
- `README.md` at the root is rendered on the profile
- Supports full GitHub-flavored Markdown + HTML
- Standard `gh repo clone` / `git clone` workflow works
- Commit shows up as a repo contribution on the profile

## Git Workflow

Standard commit + push. Since the profile README renders immediately on GitHub, push after every change — there's no staging environment for the profile view.

## List Item Formatting Convention

Each bullet point follows: `- emoji verb **bold core description**`

```
- 🔭 researching **GNN-based geospatial modeling & multi-agent AI systems**
- 💼 interning **FOF due diligence & trust operations**
- 🏗️ building **enterprise government service platform**
- 🛸 research focus: **drone photogrammetry → 3D reconstruction**
```

Rules:
- **No em-dash (—)** between verb and description — the bold wraps the description directly
- **Bold** the key description only, not the verb/emoji
- Keep lines roughly the same visual length for alignment
- Describe work content, not employer name (privacy/discretion)

## User Preferences

- Describe the work content, not the employer name (privacy/discretion)
- Keep current (internship, research focus, stack icons)
- Icons via `skillicons.dev` for common tech, `simpleicons.org` for niche ones
- List item structure: `emoji verb **bold content**` — no separator characters between verb and bold
