#!/usr/bin/env python3
"""Strict bilingual mark builder for batch 4 (passages 31-40).

Reuses EN marking already present (re-derives it deterministically, drift-safe).
Assigns each IELTS word a distinct, meaningful Chinese span.

Per-passage overrides live in OV (translation edits + explicit word->span map).
"""

import json, re, os, sys

L, R = "\u27e6", "\u27e7"
POS = re.compile(r"\b(?:n|v|vt|vi|a|ad|adj|adv|prep|conj|pron|num|int|abbr|aux)\b\.?")


def en_word_regex(word):
    parts = re.split(r"\s+", word.strip().lower())
    pat = r"\s+".join(re.escape(p) for p in parts)
    return re.compile(r"(?<![A-Za-z])" + pat + r"(?![A-Za-z])", re.IGNORECASE)


def wrap_english(text, words):
    claimed = []

    def ov(s, e):
        return any(s < b and a < e for a, b in claimed)

    unmarked = []
    for w in words:
        placed = False
        for m in en_word_regex(w).finditer(text):
            if not ov(m.start(), m.end()):
                claimed.append((m.start(), m.end()))
                placed = True
                break
        if not placed:
            unmarked.append(w)
    out = text
    for s, e in sorted(claimed, key=lambda x: -x[0]):
        out = out[:s] + L + out[s:e] + R + out[e:]
    return out, unmarked


def def_fragments(defstr):
    s = POS.sub(" ", defstr)
    toks = re.split(r"[；;，,、\s()（）<>《》/\.…。!！?？:：'\"\[\]]+", s)
    runs = []
    for t in toks:
        t = re.sub(r"[^\u4e00-\u9fff]", "", t.strip())
        if t:
            runs.append(t)
    return runs


def candidate_spans(defstr):
    runs = def_fragments(defstr)
    pool, singles = [], []
    for r in runs:
        if len(r) == 1:
            singles.append(r)
            continue
        for size in range(len(r), 1, -1):
            for i in range(0, len(r) - size + 1):
                pool.append(r[i : i + size])
    return sorted(set(pool), key=lambda x: -len(x)) + sorted(set(singles))


# OV[pid] = {"edits": [[old,new],...], "map": {word: span}}
OV = {}


def build(pid):
    orig = json.load(open(f"out/out_{pid:03d}.json", encoding="utf-8"))
    wordobjs = json.load(open(f"passages/words_{pid:03d}.json", encoding="utf-8"))[
        "words"
    ]
    words = [w["word"] for w in wordobjs]
    ov = OV.get(pid, {})
    trans = orig["translation"]
    for old, new in ov.get("edits", []):
        if old not in trans:
            return [f"EDIT MISS: {old!r}"]
        trans = trans.replace(old, new, 1)
    omap = ov.get("map", {})

    problems = []
    targets = {}
    forced = {}
    for w in words:
        if w in omap:
            span = omap[w]
            if span not in trans:
                problems.append(f"OVERRIDE span not in trans '{w}': {span!r}")
            targets[w] = span
            forced[w] = span

    defmap = {w["word"]: w["def"] for w in wordobjs}
    cand_map = {}
    for w in words:
        if w in targets:
            continue
        cand_map[w] = [c for c in candidate_spans(defmap[w]) if c in trans]
    no_match = [w for w in cand_map if not cand_map[w]]

    used = set(forced.values())
    order = sorted([w for w in cand_map if cand_map[w]], key=lambda w: len(cand_map[w]))
    for w in order:
        chosen = None
        for c in cand_map[w]:
            if c not in used:
                chosen = c
                break
        if chosen is None:
            chosen = cand_map[w][0]
        targets[w] = chosen
        used.add(chosen)

    for w in no_match:
        problems.append(f"NO MATCH '{w}' :: {defmap[w]}")

    distinct = sorted(set(targets.values()), key=lambda x: -len(x))
    claimed = []

    def ov2(s, e):
        return any(s < b and a < e for a, b in claimed)

    for span in distinct:
        idx = trans.find(span)
        ok = False
        while idx != -1:
            if not ov2(idx, idx + len(span)):
                claimed.append((idx, idx + len(span)))
                ok = True
                break
            idx = trans.find(span, idx + 1)
        if not ok:
            problems.append(f"CANNOT PLACE (overlap) {span!r}")

    tm = trans
    for s, e in sorted(claimed, key=lambda x: -x[0]):
        tm = tm[:s] + L + tm[s:e] + R + tm[e:]

    text_marked, en_unmarked = wrap_english(orig["text"], words)
    if en_unmarked:
        problems.append(f"EN UNMARKED: {en_unmarked}")

    pairs = [{"word": w, "zh": targets.get(w, "")} for w in words]
    out = {
        "id": pid,
        "theme": orig["theme"],
        "text_marked": text_marked,
        "translation_plain": trans,
        "translation_marked": tm,
        "pairs": pairs,
    }
    json.dump(
        out,
        open(f"marked/mark_{pid:03d}.json", "w", encoding="utf-8"),
        ensure_ascii=False,
    )
    return problems


def load_ov():
    global OV
    if os.path.exists("ov4.json"):
        raw = json.load(open("ov4.json", encoding="utf-8"))
        OV = {int(k): v for k, v in raw.items()}


def main():
    load_ov()
    ids = range(31, 41)
    if len(sys.argv) > 1:
        ids = [int(x) for x in sys.argv[1:]]
    for pid in ids:
        probs = build(pid)
        if probs:
            print(f"passage {pid}: {len(probs)} problems")
            for p in probs:
                print("   ", p)
        else:
            print(f"passage {pid}: clean")


if __name__ == "__main__":
    main()
