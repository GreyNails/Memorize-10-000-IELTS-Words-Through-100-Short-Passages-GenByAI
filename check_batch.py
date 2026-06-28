#!/usr/bin/env python3
"""Per-batch coverage verifier.
Usage: python3 check_batch.py <batch_number>
Checks that each passage file out_<id>.json contains ALL of its target words
from passages/words_<id>.json. Verification only -- never generates content."""

import json, re, sys


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
        words = [
            w["word"]
            for w in json.load(
                open(f"passages/words_{pid:03d}.json", encoding="utf-8")
            )["words"]
        ]
        try:
            out = json.load(open(f"out/out_{pid:03d}.json", encoding="utf-8"))
        except FileNotFoundError:
            print(f"passage {pid}: MISSING output file")
            all_ok = False
            continue
        blob = out["text"].lower()
        missing = [w for w in words if not word_present(w, blob)]
        if missing:
            all_ok = False
            print(f"passage {pid}: MISSING {len(missing)}/{len(words)} -> {missing}")
        else:
            wc = len(out["text"].split())
            print(f"passage {pid}: OK ({len(words)} words, {wc} words long)")
    print("BATCH OK" if all_ok else "BATCH HAS MISSING WORDS")
    sys.exit(0 if all_ok else 1)


if __name__ == "__main__":
    main()
