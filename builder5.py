#!/usr/bin/env python3
"""Builder for batch 5.

For a passage it takes an authored `translation_plain` (Chinese, edited to host
every IELTS word's dictionary gloss) plus an optional explicit overrides map
{word: span}. It then:
  - assigns each word a target span: override if given else the longest
    candidate gloss that occurs in plain;
  - reports words with NO hostable span (so the author can edit plain);
  - greedily wraps non-overlapping occurrences (longest spans first) so every
    target span is wrapped at least once;
  - writes marked/mark_<pid>.json reusing existing text_marked.

Authored content lives in authored5.py as AUTHORED = {pid: {"plain":..., "map":{...}}}.
"""

import json, re, sys

L, R = "\u27e6", "\u27e7"
CJK = r"\u4e00-\u9fff"


def load_cands(pid):
    return json.load(open(f"/tmp/cands_{pid}.json", encoding="utf-8"))


def assign_spans(pid, plain, override):
    words = [
        w["word"]
        for w in json.load(open(f"passages/words_{pid:03d}.json", encoding="utf-8"))[
            "words"
        ]
    ]
    cands = load_cands(pid)
    span_of = {}
    missing = []
    for w in words:
        if w in override:
            s = override[w]
            if s not in plain:
                missing.append((w, "OVERRIDE-NOT-IN-PLAIN:" + s))
                continue
            span_of[w] = s
            continue
        chosen = None
        for c in sorted(cands.get(w, []), key=lambda x: -len(x)):
            if c in plain:
                chosen = c
                break
        if chosen:
            span_of[w] = chosen
        else:
            missing.append((w, cands.get(w, [])))
    return words, span_of, missing


def wrap(plain, spans):
    # spans: set of distinct target substrings. mark one non-overlapping
    # occurrence of each (longest first). Returns marked string or raises with
    # the span that couldn't be placed.
    mask = [False] * len(plain)
    intervals = []
    unplaced = []
    for s in sorted(set(spans), key=lambda x: -len(x)):
        placed = False
        start = 0
        while True:
            i = plain.find(s, start)
            if i < 0:
                break
            if not any(mask[i : i + len(s)]):
                for k in range(i, i + len(s)):
                    mask[k] = True
                intervals.append((i, i + len(s)))
                placed = True
                break
            start = i + 1
        if not placed:
            unplaced.append(s)
    if unplaced:
        return None, unplaced
    intervals.sort()
    out = []
    prev = 0
    for a, b in intervals:
        out.append(plain[prev:a])
        out.append(L + plain[a:b] + R)
        prev = b
    out.append(plain[prev:])
    return "".join(out), []


def build(pid, plain, override):
    words, span_of, missing = assign_spans(pid, plain, override)
    if missing:
        print(f"passage {pid}: MISSING {len(missing)} -> need plain edits:")
        for w, info in missing:
            print(f"    {w} :: {info}")
        return False
    spans = set(span_of.values())
    marked, unplaced = wrap(plain, spans)
    if unplaced:
        print(f"passage {pid}: UNPLACED spans (add another occurrence): {unplaced}")
        return False
    existing = json.load(open(f"marked/mark_{pid:03d}.json", encoding="utf-8"))
    out = {
        "id": pid,
        "theme": existing["theme"],
        "text_marked": existing["text_marked"],
        "translation_plain": plain,
        "translation_marked": marked,
        "pairs": [{"word": w, "zh": span_of[w]} for w in words],
    }
    json.dump(
        out,
        open(f"marked/mark_{pid:03d}.json", "w", encoding="utf-8"),
        ensure_ascii=False,
    )
    print(f"passage {pid}: BUILT ok ({len(words)} words)")
    return True


def main():
    from authored5 import AUTHORED

    target = [int(x) for x in sys.argv[1:]] or list(range(41, 51))
    okall = True
    for pid in target:
        if pid not in AUTHORED:
            print(f"passage {pid}: no authored data yet")
            okall = False
            continue
        a = AUTHORED[pid]
        if not build(pid, a["plain"], a.get("map", {})):
            okall = False
    print("ALL BUILT" if okall else "BUILD INCOMPLETE")


if __name__ == "__main__":
    main()
