#!/usr/bin/env python3
from pathlib import Path
import re

ROOT = Path(__file__).resolve().parents[1]
TARGETS = [ROOT / "docs"]

FM_BLOCK = re.compile(r'^---\s*\n(.*?)\n---\s*\n', re.DOTALL)
CODE_FENCE = re.compile(r'```.*?```', re.DOTALL)

LIQUID_CURVY = re.compile(r'(\{\{\s*)[“”](/[^"’”\']*)[“”](\s*\|\s*relative_url\s*\}\})')
LIQUID_CURVY_SQ = re.compile(r'(\{\{\s*)[‘’](/[^"’”\']*)[‘’](\s*\|\s*relative_url\s*\}\})')
PSEUDO_LIQUID = re.compile(r'\{\s*[“”](/[^"’”\']*)[“”]\s+relative_url\s*\}')
PSEUDO_LIQUID_SQ = re.compile(r'\{\s*[‘’](/[^"’”\']*)[‘’]\s+relative_url\s*\}')
ABS_LINK = re.compile(r'\]\((/[^)]+)\)')

def sanitize_fragment(s: str) -> str:
    s = LIQUID_CURVY.sub(r'\1"\2"\3', s)
    s = LIQUID_CURVY_SQ.sub(r'\1"\2"\3', s)
    s = PSEUDO_LIQUID.sub(lambda m: '{{ "' + m.group(1) + '" | relative_url }}', s)
    s = PSEUDO_LIQUID_SQ.sub(lambda m: '{{ "' + m.group(1) + '" | relative_url }}', s)
    s = ABS_LINK.sub(lambda m: ']({{ "' + m.group(1) + '" | relative_url }})', s)
    return s

def sanitize_text(text: str) -> str:
    head = ""
    body = text
    m = FM_BLOCK.match(text)
    if m:
        head = text[:m.end()]
        body = text[m.end():]
    out = []
    pos = 0
    for m in CODE_FENCE.finditer(body):
        frag = body[pos:m.start()]
        out.append(sanitize_fragment(frag))
        out.append(m.group(0))
        pos = m.end()
    out.append(sanitize_fragment(body[pos:]))
    return head + "".join(out)

def process_file(p: Path):
    text = p.read_text(encoding="utf-8")
    new = sanitize_text(text)
    if new != text:
        p.write_text(new, encoding="utf-8")
        print(f"[SANITIZED] {p}")

def main():
    for base in TARGETS:
        for md in base.rglob("*.md"):
            process_file(md)
    print("[OK] Sanitization complete (code-fence-aware)")

if __name__ == "__main__":
    main()
