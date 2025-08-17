#!/usr/bin/env python3
from pathlib import Path
import re, sys, html, yaml

SITE = Path("./_site").resolve()
DEPLOY_CFG = Path("./docs/_config.deploy.yml")

ATTR = re.compile(r'(?:href|src)="([^"#?]+)(?:\?[^"#]*)?(#[^"]*)?"', re.IGNORECASE)

def load_baseurl():
    baseurl = ""
    if DEPLOY_CFG.exists():
        try:
            data = yaml.safe_load(DEPLOY_CFG.read_text(encoding="utf-8")) or {}
            baseurl = str(data.get("baseurl") or "").strip()
        except Exception:
            baseurl = ""
    return baseurl

def norm_url(u: str, baseurl: str) -> str:
    if baseurl and u.startswith(baseurl + "/"):
        return u[len(baseurl):] or "/"
    return u

def candidate_paths(root: Path, url: str, html_file: Path):
    if url.startswith("/"):
        p = (root / url.lstrip("/")).resolve()
    else:
        p = (html_file.parent / url).resolve()
    cands = [p]
    if p.is_dir() or url.endswith("/"):
        cands.append(p / "index.html")
    else:
        if p.suffix == "":
            cands.append(p.with_suffix(".html"))
            cands.append(p / "index.html")
    return cands

def main():
    baseurl = load_baseurl()
    errors = []
    for htmlf in SITE.rglob("*.html"):
        text = htmlf.read_text(encoding="utf-8", errors="ignore")
        for m in ATTR.finditer(text):
            raw = html.unescape(m.group(1))
            if raw.startswith(("http://", "https://", "mailto:")):
                continue
            url = norm_url(raw, baseurl)
            if url == "":
                url = "/"
            ok = False
            for cand in candidate_paths(SITE, url, htmlf):
                if cand.exists():
                    ok = True
                    break
            if not ok:
                errors.append(f"[BROKEN] {htmlf.relative_to(SITE)} -> {raw} (fs:{url})")
    if errors:
        print("::error::Internal link check failed:\n" + "\n".join(errors[:400]))
        sys.exit(1)
    print(f"[OK] Internal links passed (baseurl={baseurl or '(empty)'})")

if __name__ == "__main__":
    main()
