#!/usr/bin/env python3
from pathlib import Path
import sys, collections

ROOT = Path(__file__).resolve().parents[1]
DOCS_KB = ROOT / "docs" / "kb"

def main():
    buckets = collections.defaultdict(list)
    for f in DOCS_KB.rglob("*"):
        if f.is_file():
            buckets[f.as_posix().lower()].append(f.as_posix())
    dups = [v for v in buckets.values() if len(set(v)) > 1]
    if dups:
        lines = []
        for group in dups[:200]:
            lines.append("[CASE] " + " | ".join(group))
        print("::error::Case-collision detected:\n" + "\n".join(lines))
        sys.exit(1)
    print("[OK] No case-collision in docs/kb")
if __name__ == "__main__":
    main()
