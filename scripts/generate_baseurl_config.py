#!/usr/bin/env python3
from pathlib import Path
import os

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "docs" / "_config.deploy.yml"

repo = os.getenv("GITHUB_REPOSITORY", "")
owner, _, name = repo.partition("/")
url = f"https://{owner}.github.io" if owner else ""
baseurl = "" if name.endswith(".github.io") else ("/" + name if name else "")

cfg = f"url: \"{url}\"\nbaseurl: \"{baseurl}\"\n"
OUT.write_text(cfg, encoding="utf-8")
print(f"[OK] Wrote {OUT}:\n{cfg}")
