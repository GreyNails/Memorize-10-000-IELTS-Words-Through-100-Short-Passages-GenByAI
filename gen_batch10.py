#!/usr/bin/env python3
import json, re

L, R = "\u27e6", "\u27e7"
IDS = list(range(91, 101))

POS_RX = re.compile(
    r"^(?:"
    r"n|v|vt|vi|a|ad|adj|adv|conj|prep|pron|num|art|int|aux|abbr"
    r")\.?[\s．.]*",
    re.IGNORECASE,
)


def overlaps(claimed, s, e):
    for a, b in claimed:
        if s < b and a < e:
            return True
    return False


def en_occurrences(text, word):
    parts = re.split(r"\s+", word.lower())
    pat = r"(?<![a-z])" + r"\s+".join(re.escape(p) for p in parts) + r"(?![a-z])"
    return [(m.start(), m.end()) for m in re.finditer(pat, text, re.IGNORECASE)]


def wrap_english(text, words):
    claimed = []
    chosen = []
    # longer phrases first so shared tokens go to the phrase
    for w in sorted(set(words), key=lambda x: -len(x)):
        occ = en_occurrences(text, w)
        placed = False
        for s, e in occ:
            if not overlaps(claimed, s, e):
                claimed.append((s, e))
                chosen.append((s, e))
                placed = True
                break
        if not placed and occ:
            # required: must wrap. fall back to first occurrence (may nest)
            chosen.append(occ[0])
    return insert(text, chosen)


CJK = r"\u4e00-\u9fff"
# POS tokens that can appear anywhere, e.g. "用旧n. 穿" or "条 vt. 闩门"
POS_ANY = re.compile(
    r"(?:^|(?<=[^a-zA-Z]))"
    r"(?:n|v|vt|vi|a|ad|adj|adv|conj|prep|pron|num|art|int|aux|abbr)\."
)


def _clean(part):
    # remove parentheticals (both half/full width)
    part = re.sub(r"[（(][^）)]*[）)]", "", part)
    # remove any latin letters / ascii leftovers
    part = re.sub(r"[a-zA-Z]+\.?", "", part)
    # strip punctuation/space
    part = part.strip(" 　。．,，、；;:：…·\"'“”‘’（）()[]")
    return part


def def_fragments(d):
    # break on POS markers anywhere, plus separators
    d2 = POS_ANY.sub("｜", d)
    raw = re.split(r"[；;，,、｜]", d2)
    frags = []
    for seg in raw:
        part = _clean(seg)
        if not (part and re.search(r"[" + CJK + r"]", part)):
            continue
        frags.append(part)
        # trimmed variants: drop common trailing function chars
        t = re.sub(r"[的地得了着们]$", "", part)
        if t and t != part and re.search(r"[" + CJK + r"]", t):
            frags.append(t)
    # unique, preserve order
    seen = set()
    out = []
    for f in frags:
        if f not in seen:
            seen.add(f)
            out.append(f)
    return out


def wrap_chinese(trans, wordobjs):
    claimed = []
    chosen = []
    for wo in wordobjs:
        frags = def_fragments(wo["def"])
        frags = sorted(frags, key=lambda x: -len(x))
        for f in frags:
            if len(f) < 1:
                continue
            placed = False
            for m in re.finditer(re.escape(f), trans):
                s, e = m.start(), m.end()
                if not overlaps(claimed, s, e):
                    claimed.append((s, e))
                    chosen.append((s, e))
                    placed = True
                    break
            if placed:
                break
    return insert(trans, chosen)


def insert(text, spans):
    spans = sorted(spans)
    out = []
    prev = 0
    for s, e in spans:
        if s < prev:
            continue  # safety: skip overlap leftovers
        out.append(text[prev:s])
        out.append(L)
        out.append(text[s:e])
        out.append(R)
        prev = e
    out.append(text[prev:])
    return "".join(out)


for pid in IDS:
    o = json.load(open(f"out/out_{pid:03d}.json", encoding="utf-8"))
    wd = json.load(open(f"passages/words_{pid:03d}.json", encoding="utf-8"))["words"]
    words = [w["word"] for w in wd]
    tm = wrap_english(o["text"], words)
    trm = wrap_chinese(o["translation"], wd)
    assert tm.replace(L, "").replace(R, "") == o["text"], pid
    assert trm.replace(L, "").replace(R, "") == o["translation"], pid
    json.dump(
        {"id": pid, "theme": o["theme"], "text_marked": tm, "translation_marked": trm},
        open(f"marked/mark_{pid:03d}.json", "w", encoding="utf-8"),
        ensure_ascii=False,
    )
    print("wrote", pid)
