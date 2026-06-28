#!/usr/bin/env python3
"""Generate clean candidate Chinese glosses per word -> /tmp/cands_<pid>.json"""

import json, re

CJK = r"\u4e00-\u9fff"


def variants(d):
    # collect all maximal CJK phrases, then add trimmed forms
    raw = re.findall(rf"[{CJK}…]+", d)
    out = set()
    for p in raw:
        p = p.strip("…")
        if len(p) >= 2:
            out.add(p)
        # drop a single leading 使/可/不/被 to expose root sometimes useful
        for pre in ("使", "可", "被"):
            if p.startswith(pre) and len(p) > 2:
                out.add(p[1:])
        # drop trailing 的/地/者
        for suf in ("的", "地"):
            if p.endswith(suf) and len(p) > 2:
                out.add(p[:-1])
    return sorted(out, key=lambda x: -len(x))


def main():
    for pid in range(41, 51):
        words = json.load(open(f"passages/words_{pid:03d}.json", encoding="utf-8"))[
            "words"
        ]
        cands = {}
        for wd in words:
            cands[wd["word"]] = variants(wd["def"])
        json.dump(
            cands,
            open(f"/tmp/cands_{pid}.json", "w", encoding="utf-8"),
            ensure_ascii=False,
        )
    print("cands written")


if __name__ == "__main__":
    main()
