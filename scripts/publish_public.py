#!/usr/bin/env python3
from pathlib import Path
import shutil, re, sys, yaml

ROOT = Path(__file__).resolve().parents[1]
KB_SRC = ROOT / "kb"
DOCS_DST = ROOT / "docs" / "kb"

ALLOWED_CONF = {"public"}
FM_RE = re.compile(r'^---\s*\n(.*?)\n---\s*\n', re.DOTALL)
LINK_RE = re.compile(r'\!\[[^\]]*\]\(([^)]+)\)')

FORBIDDEN_PATH_FRAGS = ("secret", ".obsidian", "verifications")

def parse_front_matter(text):
    m = FM_RE.match(text)
    if not m:
        return {}, text
    try:
        fm = yaml.safe_load(m.group(1)) or {}
    except Exception:
        fm = {}
    return fm, text[m.end():]

def should_include(md_path: Path) -> bool:
    parts = [p.lower() for p in md_path.parts]
    if any(seg in parts for seg in FORBIDDEN_PATH_FRAGS):
        return False
    try:
        text = md_path.read_text(encoding="utf-8")
    except Exception:
        return False
    fm, _ = parse_front_matter(text)
    conf = (fm or {}).get("confidentiality", "internal")
    return str(conf).lower() in ALLOWED_CONF

def copy_file(src: Path):
    rel = src.relative_to(KB_SRC)
    dst = DOCS_DST / rel
    dst.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(src, dst)

def copy_linked_assets(md_path: Path, body: str):
    base = md_path.parent
    for link in LINK_RE.findall(body):
        if "://" in link:
            continue
        asset = (base / link).resolve()
        try:
            asset.relative_to(KB_SRC.resolve())
        except ValueError:
            continue
        if asset.exists() and asset.is_file():
            copy_file(asset)

def ensure_index(dir_path: Path):
    idx = dir_path / "index.md"
    if not idx.exists():
        idx.write_text(f"---\ntitle: \"{dir_path.name}\"\n---\n\n# {dir_path.name}\n", encoding="utf-8")

def main():
    if not KB_SRC.exists():
        print(f"::error::source not found: {KB_SRC}")
        sys.exit(1)
    if DOCS_DST.exists():
        shutil.rmtree(DOCS_DST)
    DOCS_DST.mkdir(parents=True, exist_ok=True)

    count = 0
    for md in KB_SRC.rglob("*.md"):
        if should_include(md):
            text = md.read_text(encoding="utf-8")
            fm, body = parse_front_matter(text)
            copy_file(md)
            copy_linked_assets(md, body)
            count += 1

    for d in DOCS_DST.rglob("*"):
        if d.is_dir():
            ensure_index(d)

    print(f"[OK] Published {count} public docs to docs/kb/")
if __name__ == "__main__":
    main()
