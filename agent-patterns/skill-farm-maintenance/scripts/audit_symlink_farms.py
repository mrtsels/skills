#!/usr/bin/env python3
"""Audit the post-flip skill symlink farms.

Post-2026-08-flip architecture: real skill content lives ONLY in
~/.agents/skills (SSOT). ~/.hermes/skills and ~/.claude/skills must be pure
symlink farms pointing back into it. This script reports:
  1. broken symlinks in each farm
  2. real (non-symlink) skill dirs left in the farms (= drift; should be symlinks)
  3. duplicate skill basenames across Hermes load paths

Note: os.walk does not follow symlinked dirs, so bundle members (e.g.
latex/latex-debugging) are not listed as separate load paths — check
bundle content directly at ~/.agents/skills/<bundle>/<name> if needed.

Usage: python3 audit_symlink_farms.py
"""
import os

FARMS = ['~/.hermes/skills', '~/.claude/skills']
SKIP_DIRS = {'.archive', '.hub', '.curator_backups', '.git', '.system'}


def walk_farm(farm):
    root = os.path.expanduser(farm)
    broken, real = [], []
    if not os.path.isdir(root):
        return broken, real
    for dirpath, dirnames, _ in os.walk(root):
        dirnames[:] = [d for d in dirnames if d not in SKIP_DIRS]
        for d in dirnames:
            p = os.path.join(dirpath, d)
            if os.path.islink(p):
                if not os.path.exists(p):
                    broken.append(os.path.relpath(p, root))
            elif os.path.exists(os.path.join(p, 'SKILL.md')):
                real.append(os.path.relpath(p, root))
    return broken, real


def find_duplicates():
    root = os.path.expanduser('~/.hermes/skills')
    names = {}
    for dirpath, dirnames, _ in os.walk(root):
        dirnames[:] = [d for d in dirnames if d not in SKIP_DIRS]
        for d in dirnames:
            p = os.path.join(dirpath, d)
            if os.path.exists(os.path.join(p, 'SKILL.md')):
                names.setdefault(d, []).append(os.path.relpath(p, root))
    return {n: ps for n, ps in names.items() if len(ps) > 1}


def main():
    for farm in FARMS:
        broken, real = walk_farm(farm)
        print(f"[{farm}]")
        print(f"  broken symlinks : {len(broken)}")
        for b in broken:
            print(f"    BROKEN {b}")
        print(f"  real skill dirs : {len(real)}")
        for r in real:
            print(f"    DRIFT  {r}")
    dupes = find_duplicates()
    print(f"[duplicate skill names across ~/.hermes/skills] {len(dupes)}")
    for n, ps in sorted(dupes.items()):
        print(f"  {n}: {ps}")


if __name__ == '__main__':
    main()
