#!/usr/bin/env python3
from pathlib import Path
import os

LIMIT_MB = float(os.getenv("ASSET_LIMIT_MB", "10"))
LIMIT = int(LIMIT_MB * 1024 * 1024)

def main():
    SITE = Path("./_site")
    if not SITE.exists():
        print("[WARN] _site not found; skip budget check")
        return
    overs = []
    for f in SITE.rglob("*"):
        if f.is_file():
            sz = f.stat().st_size
            if sz > LIMIT:
                overs.append((sz, f))
    if overs:
        overs.sort(reverse=True)
        for sz, f in overs[:200]:
            print(f"::warning::[ASSET-BUDGET] {f} is {sz/1024/1024:.2f}MB > {LIMIT_MB}MB")
    else:
        print("[OK] Asset budget within limit")
if __name__ == "__main__":
    main()
