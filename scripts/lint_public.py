#!/usr/bin/env python3
from pathlib import Path
import re, sys, yaml

ROOT = Path(__file__).resolve().parents[1]
KB_SRC = ROOT / "kb"

FM_RE = re.compile(r'^---\s*\n(.*?)\n---\s*\n', re.DOTALL)

# 個人メモ判定のみ厳格ブロック（ここにpublicが混入していたらfail）
PERSONAL_FRAGS = (
    "/corpus/secret/",
    "/corpus/internal/",
    "/periodic_notes/",
    "/.obsidian/",
    "/canvas/",
)

FANCY_QUOTES = ("“", "”", "‘", "’")
ABSOLUTE_LINK = re.compile(r'\]\((/(?!kb_pages/)[^\)]+)\)')  # naive

def parse_front_matter(text):
    m = FM_RE.match(text)
    if not m:
        return None, text
    try:
        fm = yaml.safe_load(m.group(1)) or {}
    except Exception:
        fm = {}
    return fm, text[m.end():]

def main():
    errors = []
    warnings = []
    for md in KB_SRC.rglob("*.md"):
        text = md.read_text(encoding="utf-8")
        parsed = parse_front_matter(text)
        path_l = "/" + str(md).replace("\\","/").lower()

        fm = parsed[0] if parsed else {}
        conf = (fm or {}).get("confidentiality", None)
        is_public = (str(conf).lower() == "public")

        is_personal = any(frag in path_l for frag in PERSONAL_FRAGS)
        if is_personal and is_public:
            errors.append(f"[FORBIDDEN] personal memo marked public: {md}")

        # 非公開やFM無しはOK（publish側でpublicに自動化）
        if parsed is None:
            warnings.append(f"[WARN:NO-FM] {md} (will be defaulted at publish unless personal)")

        # 情報だけは流す（ビルド停止まではしない）
        for q in FANCY_QUOTES:
            if q in text and "{{" in text:
                warnings.append(f"[WARN:LIQUID-QUOTE] Fancy quote {q} near Liquid in {md}")
        if ABSOLUTE_LINK.search(text):
            warnings.append(f"[WARN:ABSOLUTE-LINK] Absolute root link in {md}; will rewrite to relative_url")

    if warnings:
        print("\n".join(warnings))
    if errors:
        print("::error::Lint failed:\n" + "\n".join(errors))
        sys.exit(1)
    print("[OK] Lint passed (personal memos protected; others default-public)")

if __name__ == "__main__":
    main()
