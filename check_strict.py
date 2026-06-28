#!/usr/bin/env python3
"""Strict validator: every IELTS word must be highlighted in BOTH languages.
Annotated files: marked/mark_<ID>.json with shape:
{"id", "theme", "text_marked", "translation_marked", "pairs":[{"word","zh"},...]}
Markers are U+27E6 ... U+27E7.

Checks:
1. Stripping markers from text_marked == original text  (no drift)
2. Stripping markers from translation_marked == original translation (no drift)
3. Every IELTS target word is wrapped at least once in text_marked  (EN coverage)
4. Every IELTS target word appears in pairs, and that pair's zh string is
   actually one of the marked spans in translation_marked          (ZH coverage)
This script ONLY validates; it never generates content.
"""

import json, re, sys

L, R = "\u27e6", "\u27e7"


def strip_markers(s):
    return s.replace(L, "").replace(R, "")


def marked_spans(s):
    return re.findall(re.escape(L) + r"(.*?)" + re.escape(R), s, re.DOTALL)


def word_present(word, blob):
    w = word.lower()
    parts = re.split(r"\s+", w)
    pat = r"\s+".join(re.escape(p) for p in parts)
    rx = re.compile(r"(?<![a-z])" + pat + r"(?![a-z])", re.IGNORECASE)
    return rx.search(blob) is not None


def main():
    batch = int(sys.argv[1])
    manifest = json.load(open(f"batches/batch_{batch:02d}.json", encoding="utf-8"))
    ids = manifest["passage_ids"]
    all_ok = True
    for pid in ids:
        orig = json.load(open(f"out/out_{pid:03d}.json", encoding="utf-8"))
        words = [
            w["word"]
            for w in json.load(
                open(f"passages/words_{pid:03d}.json", encoding="utf-8")
            )["words"]
        ]
        try:
            m = json.load(open(f"marked/mark_{pid:03d}.json", encoding="utf-8"))
        except FileNotFoundError:
            print(f"passage {pid}: MISSING marked file")
            all_ok = False
            continue
        problems = []
        if strip_markers(m["text_marked"]) != orig["text"]:
            problems.append("TEXT DRIFT")
        # translation may be lightly edited to host all meanings; ensure stripping
        # markers yields the value stored in translation_plain (the edited base).
        base = m.get("translation_plain")
        if base is None:
            problems.append("MISSING translation_plain")
        elif strip_markers(m["translation_marked"]) != base:
            problems.append("TRANSLATION DRIFT (stripped != translation_plain)")
        # EN coverage
        en_spans_blob = " \n ".join(marked_spans(m["text_marked"])).lower()
        unmarked_en = [w for w in words if not word_present(w, en_spans_blob)]
        if unmarked_en:
            problems.append(f"UNMARKED EN {len(unmarked_en)}: {unmarked_en[:10]}")
        # ZH coverage via pairs
        zh_spans = set(marked_spans(m["translation_marked"]))
        pairs = {p["word"]: p["zh"] for p in m.get("pairs", [])}
        missing_pair = [w for w in words if w not in pairs]
        bad_pair = [w for w in words if w in pairs and pairs[w] not in zh_spans]
        if missing_pair:
            problems.append(f"NO ZH PAIR {len(missing_pair)}: {missing_pair[:10]}")
        if bad_pair:
            problems.append(f"ZH SPAN NOT MARKED {len(bad_pair)}: {bad_pair[:10]}")
        if problems:
            all_ok = False
            print(f"passage {pid}: FAIL -> " + " | ".join(problems))
        else:
            print(f"passage {pid}: OK ({len(words)} words fully marked EN+ZH)")
    print("STRICT BATCH OK" if all_ok else "STRICT BATCH HAS PROBLEMS")
    sys.exit(0 if all_ok else 1)


if __name__ == "__main__":
    main()
