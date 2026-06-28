#!/usr/bin/env python3
import json, re, sys

L, R = "\u27e6", "\u27e7"

POS = re.compile(r"\b(?:n|v|vt|vi|a|ad|adj|adv|prep|conj|pron|num|int|abbr|aux)\b\.?")


def en_word_regex(word):
    parts = re.split(r"\s+", word.strip().lower())
    pat = r"\s+".join(re.escape(p) for p in parts)
    return re.compile(r"(?<![A-Za-z])" + pat + r"(?![A-Za-z])", re.IGNORECASE)


def wrap_english(text, words):
    # collect one non-overlapping match span per word
    claimed = []  # list of (start,end)

    def overlaps(s, e):
        for a, b in claimed:
            if s < b and a < e:
                return True
        return False

    unmarked = []
    for w in words:
        rx = en_word_regex(w)
        placed = False
        for m in rx.finditer(text):
            if not overlaps(m.start(), m.end()):
                claimed.append((m.start(), m.end()))
                placed = True
                break
        if not placed:
            unmarked.append(w)
    # insert markers right to left
    claimed.sort()
    out = text
    for s, e in sorted(claimed, key=lambda x: -x[0]):
        out = out[:s] + L + out[s:e] + R + out[e:]
    return out, unmarked


def zh_candidates(defstr):
    s = POS.sub(" ", defstr)
    # split on separators
    toks = re.split(r"[；;，,、\s()（）<>《》/\.…]+", s)
    cands = set()
    for t in toks:
        t = t.strip()
        # keep only chinese chars
        t = re.sub(r"[^\u4e00-\u9fff]", "", t)
        if len(t) >= 2:
            cands.add(t)
            # progressive prefixes (>=2 chars) so prose's shorter form can match
            for k in range(2, len(t)):
                cands.add(t[:k])
    return cands


def wrap_chinese(trans, wordobjs):
    claimed = []

    def overlaps(s, e):
        for a, b in claimed:
            if s < b and a < e:
                return True
        return False

    # gather all (candidate, length) sorted longest first to prefer specific matches
    # but assign per word; we want each word to claim at most one span.
    matched = 0
    # Build candidate list with word index
    entries = []
    for wo in wordobjs:
        cands = zh_candidates(wo["def"])
        for c in cands:
            entries.append((len(c), c, wo["word"]))
    entries.sort(key=lambda x: -x[0])
    used_words = set()
    for ln, c, w in entries:
        if w in used_words:
            continue
        idx = trans.find(c)
        while idx != -1:
            if not overlaps(idx, idx + ln):
                claimed.append((idx, idx + ln))
                used_words.add(w)
                matched += 1
                break
            idx = trans.find(c, idx + 1)
    out = trans
    for s, e in sorted(claimed, key=lambda x: -x[0]):
        out = out[:s] + L + out[s:e] + R + out[e:]
    return out, matched


def main():
    batch = int(sys.argv[1])
    ids = json.load(open(f"batches/batch_{batch:02d}.json", encoding="utf-8"))[
        "passage_ids"
    ]
    for pid in ids:
        orig = json.load(open(f"out/out_{pid:03d}.json", encoding="utf-8"))
        wordobjs = json.load(open(f"passages/words_{pid:03d}.json", encoding="utf-8"))[
            "words"
        ]
        words = [w["word"] for w in wordobjs]
        tm, unmarked = wrap_english(orig["text"], words)
        trm, nz = wrap_chinese(orig["translation"], wordobjs)
        out = {
            "id": pid,
            "theme": orig["theme"],
            "text_marked": tm,
            "translation_marked": trm,
        }
        json.dump(
            out,
            open(f"marked/mark_{pid:03d}.json", "w", encoding="utf-8"),
            ensure_ascii=False,
        )
        print(f"{pid}: en_unmarked={len(unmarked)} {unmarked[:10]} zh_spans={nz}")


if __name__ == "__main__":
    main()
