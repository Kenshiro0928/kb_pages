#!/usr/bin/env python3
from pathlib import Path
import re, sys, yaml

ROOT = Path(__file__).resolve().parents[1]
KB_SRC = ROOT / "kb"

FM_RE = re.compile(r'^---\s*\n(.*?)\n---\s*\n', re.DOTALL)
FORBIDDEN_FRAGMENTS = ("secret", ".obsidian", "verifications", "indices", "evals/runs", "scripts")
FANCY_QUOTES = ("“", "”", "‘", "’")
ABSOLUTE_LINK = re.compile(r'\]\((/(?!kb_pages/)[^\)]+)\)')  # naive

def parse_front_matter(text):
    m = FM_RE.match(text)
    if not m:
        return None, text
    try:
        fm = yaml.safe_load(m.group(1)) or {}
    except Exception:
        fm = {}
    return fm, text[m.end():]

def main():
    errors = []
    for md in KB_SRC.rglob("*.md"):
        text = md.read_text(encoding="utf-8")
        parsed = parse_front_matter(text)
        if parsed is None:
            errors.append(f"[NO-FM] {md}")
            continue
        fm, body = parsed
        conf = (fm or {}).get("confidentiality", "internal").lower()
        if conf == "public":
            p = str(md).lower()
            if any(frag in p for frag in FORBIDDEN_FRAGMENTS):
                errors.append(f"[FORBIDDEN] public under forbidden path: {md}")
        for q in FANCY_QUOTES:
            if q in text and "{{" in text:
                errors.append(f"[LIQUID-QUOTE] Fancy quote {q} found near Liquid in {md}")
        if ABSOLUTE_LINK.search(text):
            errors.append(f"[ABSOLUTE-LINK] Absolute root link found in {md}; use {{ '/path' | relative_url }}")
        for req in ("title", "confidentiality"):
            if req not in (fm or {}):
                errors.append(f"[FM-MISSING] {req} missing in {md}")
    if errors:
        print("::error::Public lint failed:\n" + "\n".join(errors))
        sys.exit(1)
    print("[OK] Public lint passed")
if __name__ == "__main__":
    main()
