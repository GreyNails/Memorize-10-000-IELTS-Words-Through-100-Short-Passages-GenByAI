#!/usr/bin/env python3
"""Coverage verifier. Checks that every word from the master xls appears in
passages.json. This script ONLY verifies; it never generates content."""

import json, re, sys, xlrd

XLS = "雅思词汇9400词EXCEL版-顺序版.xls"
PASSAGES = "passages.json"


def master_words():
    b = xlrd.open_workbook(XLS)
    s = b.sheet_by_index(0)
    out = []
    for r in range(s.nrows):
        w = str(s.cell_value(r, 1)).strip()
        if w:
            out.append(w)
    return out


def normalize(text):
    return text.lower()


def word_present(word, blob):
    """Case-insensitive presence check tolerant of word boundaries."""
    w = word.lower()
    # exact token search with boundaries that treat hyphen/dot/space as part of token
    # Build a regex: escape, allow flexible whitespace for multiword
    parts = re.split(r"\s+", w)
    pat = r"\s+".join(re.escape(p) for p in parts)
    # boundary: not preceded/followed by a letter
    rx = re.compile(r"(?<![a-z])" + pat + r"(?![a-z])", re.IGNORECASE)
    return rx.search(blob) is not None


def main():
    words = master_words()
    data = json.load(open(PASSAGES, encoding="utf-8"))
    blob = normalize(" \n ".join(p["text"] for p in data))
    missing = [w for w in words if not word_present(w, blob)]
    print(f"master words: {len(words)}")
    print(f"passages: {len(data)}")
    print(f"covered: {len(words) - len(missing)}")
    print(f"missing: {len(missing)}")
    if missing:
        json.dump(
            missing,
            open("missing.json", "w", encoding="utf-8"),
            ensure_ascii=False,
            indent=1,
        )
        print("--- first 60 missing ---")
        print(missing[:60])
        sys.exit(1)
    print("ALL WORDS COVERED ✓")


if __name__ == "__main__":
    main()
