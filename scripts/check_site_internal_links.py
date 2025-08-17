#!/usr/bin/env python3
from pathlib import Path
import re, sys, html

SITE = Path("./_site").resolve()
HREF_RE = re.compile(r'href="([^"#]+)(#[^"]*)?"', re.IGNORECASE)

def main():
    errors = []
    for htmlf in SITE.rglob("*.html"):
        text = htmlf.read_text(encoding="utf-8", errors="ignore")
        for m in HREF_RE.finditer(text):
            href = html.unescape(m.group(1))
            if href.startswith(("http://", "https://", "mailto:")):
                continue
            target = (htmlf.parent / href).resolve()
            if href.startswith("/"):
                target = (SITE / href.lstrip("/")).resolve()
            if not target.exists():
                errors.append(f"[BROKEN] {htmlf.relative_to(SITE)} -> {href}")
    if errors:
        print("::error::Internal link check failed:\n" + "\n".join(errors[:200]))
        sys.exit(1)
    print("[OK] Internal links passed")
if __name__ == "__main__":
    main()
