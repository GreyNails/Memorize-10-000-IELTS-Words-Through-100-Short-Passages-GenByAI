#!/usr/bin/env python3
"""Semi-automatic re-annotation.

For each passage it:
  - marks every IELTS word in the English text (EN side, reuses annotate logic)
  - auto-matches each word's Chinese meaning fragment inside the ORIGINAL
    translation and wraps it, building an explicit `pairs` list
  - sets translation_plain = original translation (markers only, no drift)

Words whose Chinese meaning cannot be found automatically are reported as
`missed_zh` so they can be patched by hand (overrides/ov_<ID>.json).

Run:  python3 autopair.py            -> rebuild all, print per-passage stats
      python3 autopair.py <pid>      -> single passage, verbose missed list
"""

import json, re, sys, os
from annotate import mark_english, zh_candidates, choose_nonoverlap, insert_markers

L, R = "\u27e6", "\u27e7"

# Function words / grammatical particles that must never be highlighted alone.
STOP = set(
    "的地得了着过和与及或之其此该使可被把将就都也很还又再不没无是有在为以于对从向往"
)
CJK = re.compile(r"[\u4e00-\u9fff]")


def single_chars(defn):
    """Content single characters extracted from a definition, excluding POS tags
    and stop/grammatical characters. Used as a fallback when no >=2-char gloss
    fragment matches the prose."""
    s = re.sub(r"[（(][^（）()]*[)）]", " ", defn)
    out = []
    for frag in re.split(r"[，,；;、。\.／/:：\s]+", s):
        frag = re.sub(r"^[a-zA-Z\. ]+", "", frag).strip()
        for ch in frag:
            if CJK.match(ch) and ch not in STOP and ch not in out:
                out.append(ch)
    return out


def auto_mark_chinese(trans, word_defs, forced=None):
    """Return (marked_translation, pairs, missed).
    pairs: list of {"word","zh"} where zh is exactly the wrapped span.
    `forced`: optional dict {word: zh_string} giving the exact span actually
    used in the prose (from an override file). Such spans get top priority.
    """
    forced = forced or {}
    spans_by_word = {}
    for w, defn in word_defs:
        cands = []
        if w in forced and forced[w]:
            cands.append(forced[w])  # highest priority: human-confirmed wording
        cands += [c for c in zh_candidates(defn) if len(c) >= 2]
        # fallback to content single chars if no multi-char gloss exists
        cands = cands + single_chars(defn)
        positions = []
        seen_pos = set()
        for c in cands:
            for m in re.finditer(re.escape(c), trans):
                key = (m.start(), m.end())
                if key not in seen_pos:
                    seen_pos.add(key)
                    positions.append(key)
        if positions:
            spans_by_word[w] = positions
    chosen, missed = choose_nonoverlap(spans_by_word)
    spans = [(s, e) for (s, e, w) in chosen]
    marked = insert_markers(trans, spans)
    pairs = [{"word": w, "zh": trans[s:e]} for (s, e, w) in chosen]
    missed_all = [w for (w, d) in word_defs if w in missed or w not in spans_by_word]
    return marked, pairs, missed_all


def build(pid):
    orig = json.load(open(f"out/out_{pid:03d}.json", encoding="utf-8"))
    wl = json.load(open(f"passages/words_{pid:03d}.json", encoding="utf-8"))["words"]
    words = [w["word"] for w in wl]
    word_defs = [(w["word"], w["def"]) for w in wl]
    # optional override: may replace the translation prose and/or force the exact
    # Chinese span used for specific words (word -> wording actually in prose).
    forced = {}
    trans = orig["translation"]
    ov_path = f"overrides/ov_{pid:03d}.json"
    if os.path.exists(ov_path):
        ov = json.load(open(ov_path, encoding="utf-8"))
        if ov.get("translation_plain"):
            trans = ov["translation_plain"]
        forced = ov.get("map", {})
    tmarked, en_missed = mark_english(orig["text"], words)
    zhmarked, pairs, zh_missed = auto_mark_chinese(trans, word_defs, forced)
    out = {
        "id": pid,
        "theme": orig["theme"],
        "text_marked": tmarked,
        "translation_plain": trans,
        "translation_marked": zhmarked,
        "pairs": pairs,
    }
    json.dump(
        out,
        open(f"marked/mark_{pid:03d}.json", "w", encoding="utf-8"),
        ensure_ascii=False,
    )
    return len(words), len(en_missed), zh_missed


def main():
    if len(sys.argv) > 1:
        pid = int(sys.argv[1])
        n, enm, zhm = build(pid)
        print(f"passage {pid}: words={n} en_missed={enm} zh_missed={len(zhm)}")
        print("MISSED ZH:", zhm)
        return
    total_words = total_zh_missed = total_en_missed = 0
    worst = []
    for pid in range(1, 101):
        n, enm, zhm = build(pid)
        total_words += n
        total_en_missed += enm
        total_zh_missed += len(zhm)
        worst.append((len(zhm), pid))
    print(f"total words={total_words}")
    print(f"EN missed total={total_en_missed}")
    print(f"ZH missed total={total_zh_missed}")
    cov = 100 * (total_words - total_zh_missed) / total_words
    print(f"ZH auto-coverage={cov:.1f}%")
    worst.sort(reverse=True)
    print("worst 15 (zh_missed, pid):", worst[:15])


if __name__ == "__main__":
    main()
