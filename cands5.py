#!/usr/bin/env python3
"""Generate per-passage candidate gloss lists (cleaned CJK phrases) for each
IELTS word, ordered longest-first. Written to /tmp/cands_<pid>.json as
{word: [gloss, ...]}. Used to auto-map an authored translation_plain.
"""

import json, re

CJK = r"\u4e00-\u9fff"


def cands_for(d):
    # remove parenthetical pos hints but keep inner cjk
    d = d.replace("（", "(").replace("）", ")")
    # split into gloss fragments
    parts = re.split(r"[，,；;。\.\s／/、:：]+", d)
    out = []
    for p in parts:
        # extract maximal CJK runs (drop latin pos tags, digits)
        for m in re.findall(rf"[{CJK}…]+", p):
            s = m.strip("…")
            if len(s) >= 2:
                out.append(s)
    # also add trimmed variants (drop trailing 的/地/了/着, leading 使/可)
    extra = []
    for s in out:
        for suf in ["的", "地", "了", "着", "性"]:
            if s.endswith(suf) and len(s) > 2:
                extra.append(s[:-1])
    out += extra
    # dedupe preserve, then sort longest first
    seen = []
    for s in out:
        if s not in seen:
            seen.append(s)
    seen.sort(key=lambda x: -len(x))
    return seen


def main():
    for pid in range(41, 51):
        words = json.load(open(f"passages/words_{pid:03d}.json", encoding="utf-8"))[
            "words"
        ]
        d = {}
        for wd in words:
            d[wd["word"]] = cands_for(wd["def"])
        json.dump(
            d,
            open(f"/tmp/cands_{pid}.json", "w", encoding="utf-8"),
            ensure_ascii=False,
            indent=0,
        )
    print("wrote cands")


if __name__ == "__main__":
    main()
