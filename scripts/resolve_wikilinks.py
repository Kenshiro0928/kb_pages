#!/usr/bin/env python3
from pathlib import Path
import re, yaml

ROOT = Path(__file__).resolve().parents[1]
DOCS_KB = ROOT / "docs" / "kb"

WIKI = re.compile(r'\[\[([^\]|#]+)(?:#([^\]|]+))?(?:\|([^\]]+))?\]\]')
EMBED = re.compile(r'!\[\[([^\]]+)\]\]')

def build_index():
    idx = {}
    for md in DOCS_KB.rglob("*.md"):
        rel = md.relative_to(DOCS_KB).as_posix()
        name = md.stem.lower()
        title = None
        text = md.read_text(encoding="utf-8")
        if text.startswith("---"):
            end = text.find("\n---", 4)
            if end != -1:
                head = text[:end+4]
                try:
                    fm = yaml.safe_load(head.strip("-\n")) or {}
                    title = str(fm.get("title") or "").strip().lower() or None
                except Exception:
                    pass
        keys = set([name])
        if title:
            keys.add(title)
        for k in keys:
            idx.setdefault(k, rel)
    return idx

def repl_wikilink(match, idx):
    target = match.group(1).strip().lower()
    hashfrag = match.group(2)
    alias = match.group(3)
    rel = idx.get(target)
    label = alias or match.group(1).strip()
    if not rel:
        return label
    url = "{{ \"" + ("/kb/" + rel.replace("index.md","")) + "\" | relative_url }}"
    if hashfrag:
        url += "#" + hashfrag
    return f"[{label}]({url})"

def main():
    idx = build_index()
    for md in DOCS_KB.rglob("*.md"):
        text = md.read_text(encoding="utf-8")
        head = ""
        body = text
        if text.startswith("---"):
            end = text.find("\n---", 4)
            if end != -1:
                head = text[:end+4]
                body = text[end+4:]
        body = WIKI.sub(lambda m: repl_wikilink(m, idx), body)
        body = EMBED.sub(lambda m: "[" + m.group(1) + "]()", body)
        md.write_text(head + body, encoding="utf-8")
        print(f"[WIKILINK] {md.relative_to(DOCS_KB)}")
    print("[OK] Wikilinks resolved (best-effort)")

if __name__ == "__main__":
    main()
