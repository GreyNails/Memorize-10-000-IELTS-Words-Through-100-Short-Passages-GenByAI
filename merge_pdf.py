#!/usr/bin/env python3
"""Interleave the two single-passage-per-page PDFs into one combined PDF so each
passage's two views sit together:

  page 1 -> passage 1, translation-block version (雅思词汇100短文.pdf)
  page 2 -> passage 1, inline-gloss version      (雅思词汇100短文_内联注释版.pdf)
  page 3 -> passage 2, translation-block version
  page 4 -> passage 2, inline-gloss version
  ...

Both inputs have 100 pages in the same passage order, giving 200 pages out.
"""

from pypdf import PdfReader, PdfWriter

TRANS = "雅思词汇100短文.pdf"
INLINE = "雅思词汇100短文_内联注释版.pdf"
OUT = "雅思词汇100短文_合并版.pdf"


def main():
    a = PdfReader(TRANS)
    b = PdfReader(INLINE)
    if len(a.pages) != len(b.pages):
        raise SystemExit(f"page count mismatch: {len(a.pages)} vs {len(b.pages)}")
    w = PdfWriter()
    for i in range(len(a.pages)):
        w.add_page(a.pages[i])
        w.add_page(b.pages[i])
    with open(OUT, "wb") as f:
        w.write(f)
    print(f"Built {OUT}: {len(w.pages)} pages ({len(a.pages)} passages x 2 views)")


if __name__ == "__main__":
    main()
