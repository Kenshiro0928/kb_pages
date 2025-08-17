#!/usr/bin/env python3
from pathlib import Path
import re, sys

ROOT = Path(__file__).resolve().parents[1]
TARGETS = [ROOT / "docs"]

def fix_liquid_quotes(s: str) -> str:
    s = re.sub(r'(\{\{\s*)[“”](/[^"’”\']*)[“”](\s*\|\s*relative_url\s*\}\})',
               r'\1"\2"\3', s)
    s = re.sub(r'(\{\{\s*)[‘’](/[^"’”\']*)[‘’](\s*\|\s*relative_url\s*\}\})',
               r'\1"\2"\3', s)
    return s

LINK_PAT = re.compile(r'\]\((/[^)]+)\)')
def rewrite_absolute_links(s: str) -> str:
    def repl(m):
        path = m.group(1)
        return ']({{ "' + path + '" | relative_url }})'
    return LINK_PAT.sub(repl, s)

def process_file(p: Path):
    text = p.read_text(encoding="utf-8")
    orig = text
    text = fix_liquid_quotes(text)
    text = rewrite_absolute_links(text)
    if text != orig:
        p.write_text(text, encoding="utf-8")
        print(f"[SANITIZED] {p}")

def main():
    for base in TARGETS:
        for md in base.rglob("*.md"):
            process_file(md)
    print("[OK] Sanitization complete")
if __name__ == "__main__":
    main()
