#!/usr/bin/env python3
"""Regenerate the Skill 清单 section of README.md from the current tree."""
import os, re, datetime, sys

AGENTS = os.path.expanduser("~/.agents/skills")
README = os.path.join(AGENTS, "README.md")


def collect(cdir):
    direct, bundles = [], []
    for sub in sorted(os.listdir(cdir)):
        if sub.startswith("."):
            continue
        p = os.path.join(cdir, sub)
        if os.path.isdir(p) and not os.path.islink(p) and os.path.isfile(os.path.join(p, "SKILL.md")):
            if sub.endswith("-skills"):
                children = sorted(
                    x for x in os.listdir(p)
                    if not x.startswith(".")
                    and os.path.isdir(os.path.join(p, x))
                    and not os.path.islink(os.path.join(p, x))
                    and os.path.isfile(os.path.join(p, x, "SKILL.md"))
                )
                bundles.append((sub, children))
            else:
                direct.append(sub)
    return direct, bundles


def build_manifest():
    lines = []
    for cat in sorted(os.listdir(AGENTS)):
        if cat.startswith("."):
            continue
        cdir = os.path.join(AGENTS, cat)
        if not os.path.isdir(cdir) or cat in ("best-practices", "ego-browser"):
            continue
        direct, bundles = collect(cdir)
        lines.append(f"### {cat}")
        for d in direct:
            lines.append(f"- {d}")
        for b, children in bundles:
            if children:
                lines.append(f"- **{b}**（bundle: {', '.join(children)}）")
            else:
                lines.append(f"- **{b}**（bundle）")
    lsp = os.path.join(AGENTS, "latex-skills")
    latex = sorted(
        x for x in os.listdir(lsp)
        if not x.startswith(".")
        and os.path.isdir(os.path.join(lsp, x))
        and not os.path.islink(os.path.join(lsp, x))
        and os.path.isfile(os.path.join(lsp, x, "SKILL.md"))
    )
    lines.append("### latex-skills")
    for x in latex:
        lines.append(f"- {x}")
    return "\n".join(lines)


def main():
    manifest = build_manifest()
    txt = open(README, encoding="utf-8").read()
    date = datetime.date.today().isoformat()
    new_block = f"> 生成时间: {date}。bundle 子 skill 通过其索引 SKILL.md 访问。\n\n{manifest}"
    # 替换 "## Skill 清单" 与 "## 命名规范" 之间的内容
    pat = re.compile(r"(## Skill 清单\n\n).*?(\n## 命名规范)", re.S)
    if not pat.search(txt):
        print("README.md 中未找到 Skill 清单段", file=sys.stderr)
        return 1
    txt = pat.sub(lambda m: m.group(1) + new_block + m.group(2), txt)
    open(README, "w", encoding="utf-8").write(txt)
    print(f"README.md 清单已更新（{len(manifest)} 行）")


if __name__ == "__main__":
    sys.exit(main())
