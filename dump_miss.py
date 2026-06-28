import json, re, importlib.util

spec = importlib.util.spec_from_file_location("ap", "autopair.py")
ap = importlib.util.module_from_spec(spec)
spec.loader.exec_module(ap)
res = {}
total = 0
for pid in range(1, 101):
    orig = json.load(open(f"out/out_{pid:03d}.json", encoding="utf-8"))
    wl = json.load(open(f"passages/words_{pid:03d}.json", encoding="utf-8"))["words"]
    word_defs = [(w["word"], w["def"]) for w in wl]
    zhmarked, pairs, missed = ap.auto_mark_chinese(orig["translation"], word_defs)
    if missed:
        dmap = {w: d for w, d in word_defs}
        res[pid] = [(w, dmap[w]) for w in missed]
        total += len(missed)
json.dump(
    res, open("/tmp/miss.json", "w", encoding="utf-8"), ensure_ascii=False, indent=1
)
print("total missed", total, "over", len(res), "passages")
# distribution
for pid in sorted(res, key=lambda p: -len(res[p]))[:20]:
    print(pid, len(res[pid]), [w for w, _ in res[pid]])
