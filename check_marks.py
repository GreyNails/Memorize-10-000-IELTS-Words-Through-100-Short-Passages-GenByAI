#!/usr/bin/env python3
"""Validate annotated passages for a batch.
Annotated files live in marked/mark_<ID>.json with shape:
{"id":N, "theme":..., "text_marked":..., "translation_marked":...}
where IELTS words (English) and their corresponding Chinese spans are wrapped
in U+27E6 ... U+27E7 markers.

Checks:
1. Stripping markers from text_marked == original text  (NO content drift)
2. Stripping markers from translation_marked == original translation
3. Every IELTS target word for that passage is wrapped at least once in text_marked
4. translation_marked has at least one marked span (sanity)
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
            problems.append("TEXT DRIFT (stripped != original)")
        if strip_markers(m["translation_marked"]) != orig["translation"]:
            problems.append("TRANSLATION DRIFT (stripped != original)")
        # every IELTS word wrapped at least once
        spans = marked_spans(m["text_marked"])
        spans_blob = " \n ".join(spans).lower()
        unmarked = [w for w in words if not word_present(w, spans_blob)]
        if unmarked:
            problems.append(f"UNMARKED EN WORDS {len(unmarked)}: {unmarked[:15]}")
        if not marked_spans(m["translation_marked"]):
            problems.append("NO MARKED CHINESE SPANS")
        if problems:
            all_ok = False
            print(f"passage {pid}: FAIL -> " + " | ".join(problems))
        else:
            print(
                f"passage {pid}: OK ({len(words)} words, "
                f"{len(marked_spans(m['translation_marked']))} zh spans)"
            )
    print("MARK BATCH OK" if all_ok else "MARK BATCH HAS PROBLEMS")
    sys.exit(0 if all_ok else 1)


if __name__ == "__main__":
    main()
