#!/usr/bin/env python3
"""Builder: read maps5/map_<pid>.json = {"plain":..., "spans":{word:zh,...}},
reuse existing English text_marked, wrap zh spans in plain (longest-first,
non-overlapping) to make translation_marked + pairs, write marked/mark_<pid>.json.
Then report any words whose span is missing/unmarked."""

import json, re, sys

L, R = "\u27e6", "\u27e7"


def wrap(plain, spans):
    # spans: dict word->zh. Need each distinct zh wrapped at least once.
    distinct = sorted(set(spans.values()), key=lambda x: -len(x))
    # mark occupied positions
    n = len(plain)
    occ = [False] * n
    placements = []  # (start, end, zh)
    marked_zh = set()
    for zh in distinct:
        if not zh:
            continue
        start = 0
        placed = False
        while True:
            i = plain.find(zh, start)
            if i < 0:
                break
            j = i + len(zh)
            if not any(occ[k] for k in range(i, j)):
                for k in range(i, j):
                    occ[k] = True
                placements.append((i, j, zh))
                marked_zh.add(zh)
                placed = True
                break
            start = i + 1
        # if couldn't place (overlap everywhere), still record absence
    # build marked string
    placements.sort()
    out = []
    pos = 0
    for i, j, zh in placements:
        out.append(plain[pos:i])
        out.append(L + plain[i:j] + R)
        pos = j
    out.append(plain[pos:])
    return "".join(out), marked_zh


def main():
    pids = [int(x) for x in sys.argv[1:]] or list(range(41, 51))
    allok = True
    for pid in pids:
        mp = json.load(open(f"maps5/map_{pid}.json", encoding="utf-8"))
        plain = mp["plain"]
        spans = mp["spans"]
        orig = json.load(open(f"out/out_{pid:03d}.json", encoding="utf-8"))
        ex = json.load(open(f"marked/mark_{pid:03d}.json", encoding="utf-8"))
        words = [
            w["word"]
            for w in json.load(
                open(f"passages/words_{pid:03d}.json", encoding="utf-8")
            )["words"]
        ]
        # validate spans present in plain
        miss_in_plain = [w for w in words if w not in spans]
        bad_substr = [w for w in words if w in spans and spans[w] not in plain]
        marked, marked_zh = wrap(plain, spans)
        not_marked = [w for w in words if w in spans and spans[w] not in marked_zh]
        pairs = [{"word": w, "zh": spans[w]} for w in words if w in spans]
        out = {
            "id": pid,
            "theme": orig["theme"],
            "text_marked": ex["text_marked"],
            "translation_plain": plain,
            "translation_marked": marked,
            "pairs": pairs,
        }
        json.dump(
            out,
            open(f"marked/mark_{pid:03d}.json", "w", encoding="utf-8"),
            ensure_ascii=False,
        )
        problems = []
        if miss_in_plain:
            problems.append(f"NO SPAN {len(miss_in_plain)}: {miss_in_plain}")
        if bad_substr:
            problems.append(f"SPAN NOT IN PLAIN {len(bad_substr)}: {bad_substr}")
        if not_marked:
            problems.append(f"SPAN NOT MARKED(overlap) {len(not_marked)}: {not_marked}")
        if problems:
            allok = False
            print(f"passage {pid}: " + " | ".join(problems))
        else:
            print(f"passage {pid}: built OK ({len(pairs)} pairs)")
    print("BUILD OK" if allok else "BUILD HAS GAPS")


if __name__ == "__main__":
    main()
