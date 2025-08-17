#!/usr/bin/env python3
from pathlib import Path
import re, sys

ROOT = Path(__file__).resolve().parents[1]
DOCS_KB = ROOT / "docs" / "kb"

PATTERNS = {
    "AWS_ACCESS_KEY": re.compile(r'AKIA[0-9A-Z]{16}'),
    "AWS_SECRET_KEY": re.compile(r'(?i)aws(.{0,20})?(secret|access)[^\n]{0,10}[:=]\s*[A-Za-z0-9/+=]{40}'),
    "GITHUB_TOKEN": re.compile(r'ghp_[A-Za-z0-9]{36,}'),
    "SLACK_TOKEN": re.compile(r'xox[baprs]-[A-Za-z0-9-]{10,}'),
    "OPENAI_KEY": re.compile(r'sk-[A-Za-z0-9]{20,}'),
    "PRIVATE_KEY": re.compile(r'-----BEGIN (?:RSA|EC|DSA|OPENSSH) PRIVATE KEY-----'),
}

def main():
    hits = []
    for f in DOCS_KB.rglob("*"):
        if f.is_file() and f.suffix.lower() in {".md", ".txt", ".env"}:
            try:
                text = f.read_text(encoding="utf-8")
            except Exception:
                continue
            for name, rx in PATTERNS.items():
                if rx.search(text):
                    hits.append(f"[SECRET:{name}] {f}")
    if hits:
        print("::error::Potential secrets found:\n" + "\n".join(hits[:200]))
        sys.exit(1)
    print("[OK] No obvious secrets in public docs")
if __name__ == "__main__":
    main()
