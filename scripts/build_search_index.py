#!/usr/bin/env python3
"""
Build a lightweight search index from docs/kb/**/*.md.
Outputs kb/search-index.json with entries: title, url, headings, excerpt.
"""
from pathlib import Path
import re, json, yaml

ROOT = Path(__file__).resolve().parents[1]
DOCS_KB = ROOT / "docs" / "kb"
OUT = DOCS_KB / "search-index.json"

FM_RE = re.compile(r'^---\s*\n(.*?)\n---\s*\n', re.DOTALL)

def parse_front_matter(text):
    m = FM_RE.match(text)
    fm = {}
    body = text
    if m:
        try:
            fm = yaml.safe_load(m.group(1)) or {}
        except Exception:
            fm = {}
        body = text[m.end():]
    return fm, body

def extract_headings(body):
    heads = []
    for line in body.splitlines():
        if line.startswith("## "):
            heads.append(line[3:].strip())
        elif line.startswith("### "):
            heads.append(line[4:].strip())
    return heads

def make_excerpt(body, n=300):
    body = re.sub(r'```.*?```', '', body, flags=re.DOTALL)
    body = re.sub(r'!\[[^\]]*\]\([^)]+\)', '', body)
    text = re.sub(r'\s+', ' ', body).strip()
    return text[:n]

def main():
    entries = []
    for md in DOCS_KB.rglob("*.md"):
        rel = md.relative_to(DOCS_KB)
        url = "/kb/" + str(rel).replace("\\","/").replace("index.md","")
        text = md.read_text(encoding="utf-8")
        fm, body = parse_front_matter(text)
        title = fm.get("title") or rel.stem
        entries.append({
            "title": title,
            "url": url,
            "headings": extract_headings(body),
            "excerpt": make_excerpt(body),
        })
    OUT.write_text(json.dumps(entries, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"[OK] Wrote {OUT} ({len(entries)} docs)")

if __name__ == "__main__":
    main()
