#!/usr/bin/env python3
"""Annotate passages for a batch: wrap IELTS target words in EN text and the
corresponding Chinese meaning spans in the translation with U+27E6..U+27E7.
Inserts ONLY markers; stripping them reproduces the original exactly.
"""

import json, re, sys

L, R = "\u27e6", "\u27e7"

POS = re.compile(
    r"^\s*((?:n|v|a|ad|adj|adv|vt|vi|num|pron|prep|conj|int|aux)\.\s*)+", re.I
)
CJK = re.compile(r"[\u4e00-\u9fff]")


def en_word_regex(word):
    parts = re.split(r"\s+", word.strip().lower())
    pat = r"\s+".join(re.escape(p) for p in parts)
    return re.compile(r"(?<![a-zA-Z])" + pat + r"(?![a-zA-Z])", re.IGNORECASE)


def choose_nonoverlap(spans_by_word):
    """spans_by_word: dict word -> list[(s,e)] candidate spans (ordered by pref).
    Returns list of (s,e,word) chosen, non-overlapping. Words with more
    constrained options get priority."""
    order = sorted(spans_by_word, key=lambda w: len(spans_by_word[w]))
    chosen = []
    occupied = []

    def overlaps(s, e):
        for a, b in occupied:
            if s < b and a < e:
                return True
        return False

    missed = []
    for w in order:
        placed = False
        for s, e in spans_by_word[w]:
            if not overlaps(s, e):
                chosen.append((s, e, w))
                occupied.append((s, e))
                placed = True
                break
        if not placed:
            missed.append(w)
    return chosen, missed


def insert_markers(text, spans):
    """spans: list of (s,e) sorted; insert L at s and R at e."""
    spans = sorted(spans, key=lambda x: x[0])
    out = []
    prev = 0
    for s, e in spans:
        out.append(text[prev:s])
        out.append(L)
        out.append(text[s:e])
        out.append(R)
        prev = e
    out.append(text[prev:])
    return "".join(out)


def mark_english(text, words):
    spans_by_word = {}
    for w in words:
        rx = en_word_regex(w)
        cands = [(m.start(), m.end()) for m in rx.finditer(text)]
        spans_by_word[w] = cands
    chosen, missed = choose_nonoverlap(spans_by_word)
    spans = [(s, e) for (s, e, w) in chosen]
    return insert_markers(text, spans), missed


TRAIL = "的地得了着过性者们"


def _variants(f):
    """Generate matchable variants of a meaning fragment, longest/most-specific
    first. The translation prose often uses the stem without trailing 的/地/性,
    or the noun before 的 (e.g. 说谎的人 -> 说谎)."""
    vs = []

    def add(x):
        x = x.strip()
        if x and CJK.search(x) and x not in vs:
            vs.append(x)

    add(f)
    # portion before the first 的 (e.g. 说谎的人 -> 说谎)
    if "的" in f:
        pre = f.split("的", 1)[0]
        if len(pre) >= 2:
            add(pre)
    # iteratively strip trailing grammatical chars
    g = f
    while g and g[-1] in TRAIL:
        g = g[:-1]
        if len(g) >= 2:
            add(g)
    # prefix substrings down to length 2 (compound head), e.g. 公民权 -> 公民.
    # Prefixes are semantically safer than arbitrary internal substrings.
    for ln in range(len(f) - 1, 1, -1):
        add(f[:ln])
    return vs


def zh_candidates(defn):
    s = defn
    # drop parentheticals
    s = re.sub(r"[（(][^（）()]*[)）]", " ", s)
    # strip POS markers (may repeat)
    while True:
        ns = POS.sub("", s)
        if ns == s:
            break
        s = ns
    # split on separators
    frags = re.split(r"[，,；;、。\./|　 \t\u2026]+", s)
    out = []
    for f in frags:
        f = f.strip()
        # strip non-CJK edges
        f = re.sub(r"^[^\u4e00-\u9fff]+", "", f)
        f = re.sub(r"[^\u4e00-\u9fff]+$", "", f)
        if f and CJK.search(f):
            for v in _variants(f):
                out.append(v)
    # dedupe preserve order, then sort by length desc for matching preference
    seen = set()
    uniq = []
    for f in out:
        if f not in seen:
            seen.add(f)
            uniq.append(f)
    uniq.sort(key=len, reverse=True)
    return uniq


def mark_chinese(trans, word_defs):
    # For each word, gather candidate (s,e) spans from its def fragments.
    spans_by_word = {}
    for w, defn in word_defs:
        cands = zh_candidates(defn)
        positions = []
        for c in cands:
            if len(c) < 2:
                continue
            for m in re.finditer(re.escape(c), trans):
                positions.append((m.start(), m.end()))
        # prefer longer matches first (already from longer cands), keep order
        if positions:
            spans_by_word[w] = positions
    chosen, missed = choose_nonoverlap(spans_by_word)
    spans = [(s, e) for (s, e, w) in chosen]
    return insert_markers(trans, spans), [
        w for (w, d) in word_defs if w in missed or w not in spans_by_word
    ]


def main():
    batch = int(sys.argv[1])
    manifest = json.load(open(f"batches/batch_{batch:02d}.json", encoding="utf-8"))
    ids = manifest["passage_ids"]
    for pid in ids:
        orig = json.load(open(f"out/out_{pid:03d}.json", encoding="utf-8"))
        wl = json.load(open(f"passages/words_{pid:03d}.json", encoding="utf-8"))[
            "words"
        ]
        words = [w["word"] for w in wl]
        word_defs = [(w["word"], w["def"]) for w in wl]
        tmarked, en_missed = mark_english(orig["text"], words)
        zhmarked, zh_missed = mark_chinese(orig["translation"], word_defs)
        out = {
            "id": pid,
            "theme": orig["theme"],
            "text_marked": tmarked,
            "translation_marked": zhmarked,
        }
        json.dump(
            out,
            open(f"marked/mark_{pid:03d}.json", "w", encoding="utf-8"),
            ensure_ascii=False,
        )
        if en_missed:
            print(f"passage {pid}: EN MISSED {en_missed}")
        print(f"passage {pid}: en_missed={len(en_missed)} zh_missed={len(zh_missed)}")


if __name__ == "__main__":
    main()
