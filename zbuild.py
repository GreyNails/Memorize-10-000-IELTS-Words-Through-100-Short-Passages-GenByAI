#!/usr/bin/env python3
"""Build marked/mark_<ID>.json from an inline-tagged Chinese translation.

Source file: zhsrc/zh_<ID>.txt  -- the Chinese translation where every IELTS
word's meaning is wrapped in a tag:  [[english_word|中文片段]]
  - "中文片段" is the exact prose that appears in the translation (and gets marked)
  - "english_word" is the IELTS key it covers
Plain text = tags replaced by their 中文片段 only.
Marked text = tags replaced by ⟦中文片段⟧.
pairs = one {word, zh} per tag.

Reuses text_marked (English) from the existing marked/mark_<ID>.json.
Validates full word coverage and no drift, then writes the file.
"""

import json, re, sys

L, R = "\u27e6", "\u27e7"
TAG = re.compile(r"\[\[([^|\]]+)\|([^\]]+)\]\]")


def build(pid):
    src = open(f"zhsrc/zh_{pid:03d}.txt", encoding="utf-8").read()
    orig = json.load(open(f"out/out_{pid:03d}.json", encoding="utf-8"))
    words = [
        w["word"]
        for w in json.load(open(f"passages/words_{pid:03d}.json", encoding="utf-8"))[
            "words"
        ]
    ]
    existing = json.load(open(f"marked/mark_{pid:03d}.json", encoding="utf-8"))
    text_marked = existing["text_marked"]

    assert text_marked.replace(L, "").replace(R, "") == orig["text"], "EN DRIFT"

    plain = TAG.sub(lambda m: m.group(2), src)
    marked = TAG.sub(lambda m: L + m.group(2) + R, src)
    pairs = [{"word": m.group(1), "zh": m.group(2)} for m in TAG.finditer(src)]

    assert marked.replace(L, "").replace(R, "") == plain, "ZH DRIFT"

    have = {p["word"] for p in pairs}
    missing = [w for w in words if w not in have]
    extra = [w for w in have if w not in set(words)]
    if missing:
        raise SystemExit(f"[{pid}] MISSING {len(missing)}: {missing}")
    if extra:
        raise SystemExit(f"[{pid}] EXTRA (not in word list) {len(extra)}: {extra}")

    # ensure every marked span is exactly recoverable (it is, by construction)
    out = {
        "id": pid,
        "theme": orig["theme"],
        "text_marked": text_marked,
        "translation_plain": plain,
        "translation_marked": marked,
        "pairs": pairs,
    }
    json.dump(
        out,
        open(f"marked/mark_{pid:03d}.json", "w", encoding="utf-8"),
        ensure_ascii=False,
    )
    print(f"[{pid}] OK {len(pairs)} tags / {len(words)} words")


if __name__ == "__main__":
    for a in sys.argv[1:]:
        build(int(a))
