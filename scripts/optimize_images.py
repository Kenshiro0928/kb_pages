#!/usr/bin/env python3
from pathlib import Path
from PIL import Image, UnidentifiedImageError

ROOT = Path(__file__).resolve().parents[1]
DOCS_KB = ROOT / "docs" / "kb"

def optimize_image(p: Path):
    try:
        with Image.open(p) as im:
            fmt = (im.format or "").upper()
            if fmt in ("JPEG", "JPG"):
                im.save(p, format="JPEG", optimize=True, quality=85, progressive=True)
                return True
            if fmt == "PNG":
                im.save(p, format="PNG", optimize=True)
                return True
    except UnidentifiedImageError:
        return False
    except Exception:
        return False
    return False

def main():
    changed = 0
    for ext in ("*.jpg","*.jpeg","*.png"):
        for f in DOCS_KB.rglob(ext):
            if optimize_image(f):
                changed += 1
                print(f"[OPTIMIZED] {f}")
    print(f"[OK] Image optimization done ({changed} files optimized)")

if __name__ == "__main__":
    main()
