#!/usr/bin/env python3
from pathlib import Path
import re, sys, html

SITE = Path("./_site").resolve()
ATTR = re.compile(r'(?:href|src)="([^"#]+)(#[^"]*)?"', re.IGNORECASE)

def main():
    errors = []
    for htmlf in SITE.rglob("*.html"):
        text = htmlf.read_text(encoding="utf-8", errors="ignore")
        for m in ATTR.finditer(text):
            url = html.unescape(m.group(1))
            if url.startswith(("http://", "https://", "mailto:")):
                continue
            if url.startswith("/"):
                target = (SITE / url.lstrip("/")).resolve()
            else:
                target = (htmlf.parent / url).resolve()
            if not target.exists():
                errors.append(f"[BROKEN] {htmlf.relative_to(SITE)} -> {url}")
    if errors:
        print("::error::Internal link check failed:\n" + "\n".join(errors[:300]))
        sys.exit(1)
    print("[OK] Internal links passed")

if __name__ == "__main__":
    main()
