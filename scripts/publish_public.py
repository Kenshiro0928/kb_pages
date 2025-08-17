#!/usr/bin/env python3
from pathlib import Path
import shutil, re, sys
import yaml

ROOT = Path(__file__).resolve().parents[1]
KB_SRC = ROOT / "kb"
DOCS_DST = ROOT / "docs" / "kb"

PERSONAL_FRAGS = (
    "/corpus/secret/",
    "/corpus/internal/",
    "/periodic_notes/",
    "/.obsidian/",
    "/canvas/",
)

FM_RE = re.compile(r'^---\s*\n(.*?)\n---\s*\n', re.DOTALL)
H1_RE = re.compile(r'^\s*#\s+(.+?)\s*$', re.MULTILINE)
IMG_LINK_RE = re.compile(r'\!\[[^\]]*\]\(([^)]+)\)')

def parse_front_matter(text):
    m = FM_RE.match(text)
    if not m:
        return {}, text
    try:
        fm = yaml.safe_load(m.group(1)) or {}
    except Exception:
        fm = {}
    return fm, text[m.end():]

def synthesize_fm(path: Path, fm: dict, body: str):
    norm = "/" + str(path).replace("\\","/")
    is_personal = any(frag in norm.lower() for frag in PERSONAL_FRAGS)
    default_conf = "internal" if is_personal else "public"
    title = fm.get("title")
    if not title:
        m = H1_RE.search(body)
        title = m.group(1).strip() if m else path.stem
    fm = dict(fm) if fm else {}
    fm.setdefault("title", title)
    fm.setdefault("confidentiality", default_conf)
    fm.setdefault("route_hint", "Balanced")
    return fm, body

def write_with_fm(dst: Path, fm: dict, body: str):
    dst.parent.mkdir(parents=True, exist_ok=True)
    front = yaml.safe_dump(fm, allow_unicode=True, sort_keys=False).strip()
    content = f"---\n{front}\n---\n\n{body}"
    dst.write_text(content, encoding="utf-8")

def copy_asset(src: Path):
    rel = src.relative_to(KB_SRC)
    out = DOCS_DST / rel
    out.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(src, out)

def copy_linked_assets(md_path: Path, body: str):
    base = md_path.parent
    for link in IMG_LINK_RE.findall(body):
        if "://" in link:
            continue
        asset = (base / link).resolve()
        try:
            asset.relative_to(KB_SRC.resolve())
        except ValueError:
            continue
        if asset.exists() and asset.is_file():
            copy_asset(asset)

def ensure_index(dir_path: Path):
    idx = dir_path / "index.md"
    if not idx.exists():
        idx.write_text(f"---\ntitle: \"{dir_path.name}\"\nconfidentiality: public\n---\n\n# {dir_path.name}\n", encoding="utf-8")

def main():
    if not KB_SRC.exists():
        print(f"::error::source not found: {KB_SRC}")
        sys.exit(1)
    if DOCS_DST.exists():
        shutil.rmtree(DOCS_DST)
    DOCS_DST.mkdir(parents=True, exist_ok=True)

    published = 0
    skipped_personal = 0

    for md in KB_SRC.rglob("*.md"):
        norm = "/" + str(md).replace("\\","/").lower()
        if any(frag in norm for frag in PERSONAL_FRAGS):
            skipped_personal += 1
            continue
        text = md.read_text(encoding="utf-8")
        fm, body = parse_front_matter(text)
        fm2, body2 = synthesize_fm(md, fm, body)
        rel = md.relative_to(KB_SRC)
        dst = DOCS_DST / rel
        write_with_fm(dst, fm2, body2)
        copy_linked_assets(md, body2)
        published += 1

    for d in DOCS_DST.rglob("*"):
        if d.is_dir():
            ensure_index(d)

    print(f"[OK] Published {published} docs to docs/kb/ (skipped personal: {skipped_personal})")

if __name__ == "__main__":
    main()
