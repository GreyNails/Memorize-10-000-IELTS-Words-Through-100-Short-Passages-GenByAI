#!/usr/bin/env python3
"""Generate marked/mark_<ID>.json for a batch. Drift-safe: only inserts
U+27E6 / U+27E7 markers around spans; never alters any other character."""

import json, re, sys

L, R = "\u27e6", "\u27e7"


def whole_word_spans(word, text):
    parts = re.split(r"\s+", word.lower())
    pat = r"\s+".join(re.escape(p) for p in parts)
    rx = re.compile(r"(?<![a-z])" + pat + r"(?![a-z])", re.IGNORECASE)
    return [(m.start(), m.end()) for m in rx.finditer(text)]


def overlaps(a, claimed):
    for b in claimed:
        if a[0] < b[1] and b[0] < a[1]:
            return True
    return False


def apply_markers(text, intervals):
    # insert right-to-left so earlier offsets stay valid
    for s, e in sorted(intervals, key=lambda x: x[0], reverse=True):
        text = text[:s] + L + text[s:e] + R + text[e:]
    return text


def mark_english(text, words):
    claimed = []
    # multi-word phrases first so they win priority
    order = sorted(words, key=lambda w: (-len(w.split()), -len(w)))
    for w in order:
        for sp in whole_word_spans(w, text):
            if not overlaps(sp, claimed):
                claimed.append(sp)
                break
    return apply_markers(text, claimed)


def zh_fragments(definition):
    # maximal Chinese runs of length >= 2, longest first
    frags = re.findall(r"[\u4e00-\u9fff]{2,}", definition)
    seen, out = set(), []
    for f in sorted(frags, key=len, reverse=True):
        if f not in seen:
            seen.add(f)
            out.append(f)
    return out


def mark_chinese(trans, word_defs):
    claimed = []
    for definition in word_defs:
        for frag in zh_fragments(definition):
            placed = False
            start = 0
            while True:
                idx = trans.find(frag, start)
                if idx < 0:
                    break
                sp = (idx, idx + len(frag))
                if not overlaps(sp, claimed):
                    claimed.append(sp)
                    placed = True
                    break
                start = idx + 1
            if placed:
                break
    return apply_markers(trans, claimed)


def main():
    batch = int(sys.argv[1])
    manifest = json.load(open(f"batches/batch_{batch:02d}.json", encoding="utf-8"))
    for pid in manifest["passage_ids"]:
        orig = json.load(open(f"out/out_{pid:03d}.json", encoding="utf-8"))
        wl = json.load(open(f"passages/words_{pid:03d}.json", encoding="utf-8"))[
            "words"
        ]
        words = [w["word"] for w in wl]
        defs = [w.get("def", "") for w in wl]
        out = {
            "id": pid,
            "theme": orig["theme"],
            "text_marked": mark_english(orig["text"], words),
            "translation_marked": mark_chinese(orig["translation"], defs),
        }
        with open(f"marked/mark_{pid:03d}.json", "w", encoding="utf-8") as f:
            json.dump(out, f, ensure_ascii=False)
        print(f"wrote marked/mark_{pid:03d}.json")


if __name__ == "__main__":
    main()
