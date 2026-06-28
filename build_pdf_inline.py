#!/usr/bin/env python3
"""Build an inline-gloss PDF (one passage per page).

Unlike build_pdf.py (which shows a separate Chinese translation block), this
version annotates the English passage IN PLACE: every IELTS word is shown in
red, immediately followed by its short Chinese meaning in blue parentheses,
e.g.  physicist(物理学家).

Source:
  out/out_*.json        -> original English text (no markers)
  passages/words_*.json -> the IELTS words for that passage + their definitions

The English word matching reuses annotate.py's non-overlapping placement so the
same occurrences chosen for highlighting get the inline gloss. Dual font
(Latin + CJK) is handled exactly like build_pdf.py.
"""

import json, glob, html, re
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import mm
from reportlab.lib.enums import TA_JUSTIFY
from reportlab.lib.styles import ParagraphStyle
from reportlab.platypus import Paragraph, Frame
from reportlab.pdfgen import canvas
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from fontTools.ttLib import TTFont as FTFont

from annotate import en_word_regex, choose_nonoverlap

LATIN_PATH = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
CJK_PATH = "/usr/share/fonts/truetype/droid/DroidSansFallbackFull.ttf"
RED = "#cc0000"
BLUE = "#1763b8"
OUT = "雅思词汇100短文_内联注释版.pdf"

pdfmetrics.registerFont(TTFont("Latin", LATIN_PATH))
pdfmetrics.registerFont(TTFont("CJK", CJK_PATH))
_LATIN_CMAP = set(FTFont(LATIN_PATH).getBestCmap().keys())

POS = re.compile(
    r"^\s*((?:n|v|a|ad|adj|adv|vt|vi|num|pron|prep|conj|int|aux)\.\s*)+", re.I
)
CJK = re.compile(r"[\u4e00-\u9fff]")

PAGE_W, PAGE_H = A4
MARGIN = 16 * mm
FRAME_W = PAGE_W - 2 * MARGIN
FRAME_H = PAGE_H - 2 * MARGIN


def font_for(ch):
    if ch == "\n":
        return "Latin"
    return "Latin" if ord(ch) in _LATIN_CMAP else "CJK"


def clean_gloss(d):
    """Short Chinese gloss: first CJK fragment of the definition, trimmed."""
    d = re.sub(r"[（(][^（）()]*[)）]", "", d)
    while True:
        n = POS.sub("", d)
        if n == d:
            break
        d = n
    for frag in re.split(r"[，,；;、。\.／/:：\s\[\]]+", d):
        frag = frag.strip()
        if frag and CJK.search(frag):
            return frag[:8]
    return d.strip()[:8]


# sentinel markers placed into the plain text, later turned into colored markup.
WL, WR = "\u0001", "\u0002"  # english red word boundaries
GL, GR = "\u0003", "\u0004"  # chinese gloss boundaries


def annotate_inline(text, word_defs):
    """Return text with chosen IELTS occurrences wrapped as
    WL word WR GL gloss GR, using non-overlapping placement."""
    spans_by_word = {}
    gloss = {}
    for w, d in word_defs:
        rx = en_word_regex(w)
        cands = [(m.start(), m.end()) for m in rx.finditer(text)]
        if cands:
            spans_by_word[w] = cands
        gloss[w] = clean_gloss(d)
    chosen, _ = choose_nonoverlap(spans_by_word)
    chosen.sort(key=lambda x: x[0])
    out = []
    prev = 0
    for s, e, w in chosen:
        out.append(text[prev:s])
        out.append(WL + text[s:e] + WR + GL + gloss[w] + GR)
        prev = e
    out.append(text[prev:])
    return "".join(out)


def to_markup(s):
    """Convert sentinel-annotated text into reportlab markup with per-character
    font switching, red English words and blue Chinese glosses."""
    out = []
    color = None  # None | RED | BLUE
    cur_font = None
    buf = []

    def flush():
        if not buf:
            return
        seg = html.escape("".join(buf))
        col = f' color="{color}"' if color else ""
        out.append(f'<font name="{cur_font}"{col}>{seg}</font>')
        buf.clear()

    for c in s:
        if c == WL:
            flush()
            color = RED
            continue
        if c == WR:
            flush()
            color = None
            continue
        if c == GL:
            flush()
            color = BLUE
            cur_font = "Latin"  # parens live in the Latin font (CJK font lacks them)
            buf.append("(")
            continue
        if c == GR:
            flush()
            color = BLUE
            cur_font = "Latin"
            buf.append(")")
            flush()
            color = None
            continue
        f = font_for(c)
        if f != cur_font:
            flush()
            cur_font = f
        buf.append(c)
    flush()
    return "".join(out).replace("\n", "<br/>")


def build_flowables(p, fs):
    title = ParagraphStyle(
        "t",
        fontName="CJK",
        fontSize=fs + 4,
        leading=(fs + 4) * 1.25,
        spaceAfter=fs * 0.6,
        textColor="#1a1a1a",
    )
    body = ParagraphStyle(
        "b",
        fontName="CJK",
        fontSize=fs,
        leading=fs * 1.6,
        alignment=TA_JUSTIFY,
        wordWrap="CJK",
    )
    return [
        Paragraph(to_markup(f"{p['id']}. " + p.get("theme", "")), title),
        Paragraph(to_markup(p["inline"]), body),
    ]


def total_height(flow, w):
    h = 0.0
    for f in flow:
        _, fh = f.wrap(w, 100000)
        h += fh
        st = getattr(f, "style", None)
        if st is not None:
            h += getattr(st, "spaceBefore", 0) + getattr(st, "spaceAfter", 0)
    return h


def fit_font(p):
    fs = 11.5
    while fs >= 6.0:
        if total_height(build_flowables(p, fs), FRAME_W) <= FRAME_H:
            return fs
        fs -= 0.5
    return 6.0


def load_passages():
    data = []
    for f in sorted(glob.glob("out/out_*.json")):
        orig = json.load(open(f, encoding="utf-8"))
        pid = orig["id"]
        wl = json.load(open(f"passages/words_{pid:03d}.json", encoding="utf-8"))[
            "words"
        ]
        word_defs = [(w["word"], w["def"]) for w in wl]
        inline = annotate_inline(orig["text"], word_defs)
        data.append({"id": pid, "theme": orig.get("theme", ""), "inline": inline})
    data.sort(key=lambda x: x["id"])
    return data


def main():
    data = load_passages()
    c = canvas.Canvas(OUT, pagesize=A4)
    c.setTitle("IELTS Vocabulary - 100 Passages (inline gloss)")
    sizes = []
    for p in data:
        fs = fit_font(p)
        sizes.append(fs)
        frame = Frame(
            MARGIN,
            MARGIN,
            FRAME_W,
            FRAME_H,
            leftPadding=0,
            rightPadding=0,
            topPadding=0,
            bottomPadding=0,
        )
        frame.addFromList(build_flowables(p, fs), c)
        c.showPage()
    c.save()
    print(f"Built {OUT}: {len(data)} pages")
    print("font sizes -> min %.1f max %.1f" % (min(sizes), max(sizes)))
    small = [(data[i]["id"], sizes[i]) for i in range(len(sizes)) if sizes[i] <= 6.0]
    if small:
        print("at floor size (6.0):", small)


if __name__ == "__main__":
    main()
