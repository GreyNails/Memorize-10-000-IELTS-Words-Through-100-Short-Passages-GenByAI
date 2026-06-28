#!/usr/bin/env python3
"""Build a 100-page PDF (one passage per page) from marked/mark_*.json.
Each page: theme heading, English passage, Chinese translation.
IELTS words (English) and corresponding Chinese spans (wrapped in
U+27E6 ... U+27E7) render in red. Chinese uses DroidSansFallbackFull.
Font size is auto-fit per page so every passage fits on exactly one page.
"""

import json, glob, html
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import mm
from reportlab.lib.enums import TA_JUSTIFY, TA_LEFT
from reportlab.lib.styles import ParagraphStyle
from reportlab.platypus import Paragraph, Frame, Spacer
from reportlab.pdfgen import canvas
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from fontTools.ttLib import TTFont as FTFont

LATIN_PATH = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
CJK_PATH = "/usr/share/fonts/truetype/droid/DroidSansFallbackFull.ttf"
L, R = "\u27e6", "\u27e7"
RED = "#cc0000"
OUT = "雅思词汇100短文.pdf"

# DroidSansFallback has NO Latin glyphs; DejaVuSans has NO CJK glyphs.
# So we register both and pick the right font per character run.
pdfmetrics.registerFont(TTFont("Latin", LATIN_PATH))
pdfmetrics.registerFont(TTFont("CJK", CJK_PATH))

_LATIN_CMAP = set(FTFont(LATIN_PATH).getBestCmap().keys())


def font_for(ch):
    """Latin font if the glyph exists there, else CJK fallback."""
    if ch in ("\n",):
        return "Latin"
    return "Latin" if ord(ch) in _LATIN_CMAP else "CJK"


PAGE_W, PAGE_H = A4
MARGIN = 16 * mm
FRAME_W = PAGE_W - 2 * MARGIN
FRAME_H = PAGE_H - 2 * MARGIN


def to_markup(s):
    """Convert the marked string into reportlab markup, wrapping each run in the
    correct font (Latin vs CJK) and applying red inside the markers."""
    out = []
    red = False
    cur_font = None
    buf = []

    def flush():
        if not buf:
            return
        seg = html.escape("".join(buf))
        color = f' color="{RED}"' if red else ""
        out.append(f'<font name="{cur_font}"{color}>{seg}</font>')
        buf.clear()

    for c in s:
        if c == L:
            flush()
            red = True
            continue
        if c == R:
            flush()
            red = False
            continue
        f = font_for(c)
        if f != cur_font:
            flush()
            cur_font = f
        buf.append(c)
    flush()
    return "".join(out).replace("\n", "<br/>")


def build_flowables(p, fs):
    """Build the flowables for one passage at body font size fs."""
    title = ParagraphStyle(
        "t",
        fontName="CJK",
        fontSize=fs + 4,
        leading=(fs + 4) * 1.25,
        spaceAfter=fs * 0.5,
        textColor="#1a1a1a",
    )
    label = ParagraphStyle(
        "l",
        fontName="CJK",
        fontSize=max(fs - 2, 6),
        leading=(fs) * 1.1,
        textColor="#3366aa",
        spaceBefore=fs * 0.45,
        spaceAfter=fs * 0.2,
    )
    en = ParagraphStyle(
        "en", fontName="CJK", fontSize=fs, leading=fs * 1.42, alignment=TA_JUSTIFY
    )
    zh = ParagraphStyle(
        "zh",
        fontName="CJK",
        fontSize=fs,
        leading=fs * 1.55,
        alignment=TA_LEFT,
        wordWrap="CJK",
    )
    flow = [
        Paragraph(to_markup(f"{p['id']}. " + p.get("theme", "")), title),
        Paragraph(to_markup("English"), label),
        Paragraph(to_markup(p["text_marked"]), en),
        Paragraph(to_markup("中文翻译"), label),
        Paragraph(to_markup(p["translation_marked"]), zh),
    ]
    return flow


def total_height(flow, avail_w):
    h = 0.0
    for f in flow:
        w, fh = f.wrap(avail_w, 100000)
        h += fh
        # account for spaceBefore/spaceAfter on Paragraph styles
        st = getattr(f, "style", None)
        if st is not None:
            h += getattr(st, "spaceBefore", 0) + getattr(st, "spaceAfter", 0)
    return h


def fit_font(p):
    """Largest font size (in 0.5 steps) such that the passage fits one frame."""
    lo, hi = 6.0, 11.5
    best = lo
    fs = hi
    while fs >= lo:
        flow = build_flowables(p, fs)
        if total_height(flow, FRAME_W) <= FRAME_H:
            best = fs
            break
        fs -= 0.5
    return best


def main():
    files = sorted(glob.glob("marked/mark_*.json"))
    data = [json.load(open(f, encoding="utf-8")) for f in files]
    data.sort(key=lambda x: x["id"])

    c = canvas.Canvas(OUT, pagesize=A4)
    c.setTitle("IELTS Vocabulary - 100 Passages")

    sizes = []
    for p in data:
        fs = fit_font(p)
        sizes.append(fs)
        flow = build_flowables(p, fs)
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
        frame.addFromList(flow, c)
        c.showPage()
    c.save()
    print(f"Built {OUT}: {len(data)} pages")
    print("font sizes -> min %.1f max %.1f" % (min(sizes), max(sizes)))
    small = [(data[i]["id"], sizes[i]) for i in range(len(sizes)) if sizes[i] <= 6.0]
    if small:
        print("at floor size (6.0):", small)


if __name__ == "__main__":
    main()
