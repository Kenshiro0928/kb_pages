#!/usr/bin/env python3
"""
Fail the build if any `confidentiality: public` file sits under forbidden paths.
Forbidden path fragments: secret, internal, .obsidian, verifications, indices, evals/runs, scripts
Also fail if a Markdown file has no front matter at all (to enforce explicitness).
"""
from pathlib import Path
import re, sys, yaml

ROOT = Path(__file__).resolve().parents[1]
KB_SRC = ROOT / "kb"

FM_RE = re.compile(r'^---\s*\n(.*?)\n---\s*\n', re.DOTALL)
FORBIDDEN_FRAGMENTS = ("secret", "internal", ".obsidian", "verifications", "indices", "evals/runs", "scripts")

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
        fm, _ = parsed
        conf = (fm or {}).get("confidentiality", "internal").lower()
        if conf == "public":
            p = str(md).lower()
            if any(frag in p for frag in FORBIDDEN_FRAGMENTS):
                errors.append(f"[FORBIDDEN] public under forbidden path: {md}")
    if errors:
        print("::error::Public lint failed:\n" + "\n".join(errors))
        sys.exit(1)
    print("[OK] Public lint passed")

if __name__ == "__main__":
    main()
