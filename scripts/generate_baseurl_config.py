#!/usr/bin/env python3
from pathlib import Path
import os

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "docs" / "_config.deploy.yml"

url = os.getenv("PAGES_URL")
baseurl = os.getenv("PAGES_BASEURL")

if not url or not baseurl:
    repo = os.getenv("GITHUB_REPOSITORY", "")
    owner, _, name = repo.partition("/")
    url = url or (f"https://{owner}.github.io" if owner else "")
    baseurl = baseurl or ("" if name.endswith(".github.io") else ("/" + name if name else ""))

OUT.write_text(f'url: "{url}"\nbaseurl: "{baseurl}"\n', encoding="utf-8")
print(f"[OK] Wrote {OUT}:\nurl={url}\nbaseurl={baseurl}\n")
