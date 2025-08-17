#!/usr/bin/env python3
from pathlib import Path
import re, sys, html, yaml

SITE = Path("./_site").resolve()
HREF_RE = re.compile(r'href="([^"#]+)(#[^"]*)?"', re.IGNORECASE)

def load_baseurl() -> str:
    for p in ("docs/_config.deploy.yml", "docs/_config.yml"):
        cfg = Path(p)
        if cfg.exists():
            try:
                data = yaml.safe_load(cfg.read_text(encoding="utf-8")) or {}
                v = str(data.get("baseurl") or "").strip()
                if v:
                    v = "/" + v.strip("/")
                return v
            except Exception:
                continue
    return ""

def resolve_target(html_file: Path, href: str, baseurl: str) -> Path:
    s = html.unescape(href)

    if s.startswith(("http://", "https://", "mailto:")):
        return Path("/__external__")

    if baseurl and s == baseurl:
        s = "/"
    elif baseurl and s.startswith(baseurl + "/"):
        s = s[len(baseurl):]

    if s.startswith("/"):
        target = (SITE / s.lstrip("/")).resolve()
    else:
        target = (html_file.parent / s).resolve()

    return target

def exists_with_fallbacks(p: Path) -> bool:
    if p.exists():
        return True
    if p.suffix == "" and (p / "index.html").exists():
        return True
    if p.suffix == "" and p.with_suffix(".html").exists():
        return True
    if str(p).endswith("/"):
        q = Path(str(p).rstrip("/"))
        if (q / "index.html").exists():
            return True
    return False

def main():
    baseurl = load_baseurl()
    errors = []
    for htmlf in SITE.rglob("*.html"):
        text = htmlf.read_text(encoding="utf-8", errors="ignore")
        for m in HREF_RE.finditer(text):
            href = m.group(1)
            tgt = resolve_target(htmlf, href, baseurl)
            if str(tgt) == "/__external__":
                continue
            if not exists_with_fallbacks(tgt):
                errors.append(f"[BROKEN] {htmlf.relative_to(SITE)} -> {href}")
    if errors:
        print("::error::Internal link check failed:\n" + "\n".join(errors[:200]))
        sys.exit(1)
    print("[OK] Internal links passed")

if __name__ == "__main__":
    main()
