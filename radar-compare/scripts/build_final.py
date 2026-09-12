"""Build the two-page final answer from docs/final-answer.md.

Reuses the renderer in build_guide.py so the short document and the 100-page
reference cannot drift apart typographically. Fails loudly if the result is not
exactly two pages, because "two pages" is the brief.

Run: python scripts/build_final.py
Output: radar-compare/output/best-three-options.pdf
"""
from pathlib import Path
import sys

import fitz
from reportlab.lib import colors
from reportlab.platypus import (BaseDocTemplate, PageTemplate, Frame, Paragraph,
                                Spacer)

sys.path.insert(0, str(Path(__file__).resolve().parent))
import build_guide as G

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / 'docs' / 'final-answer.md'
OUT = ROOT / 'output' / 'best-three-options.pdf'

MARGIN = 38
PAGE = G.PORTRAIT
TARGET_PAGES = 2


def footer(canvas, doc):
    w, h = canvas._pagesize
    canvas.saveState()
    canvas.setStrokeColor(G.RULE)
    canvas.setLineWidth(0.5)
    canvas.line(MARGIN, 28, w - MARGIN, 28)
    canvas.setFont('Text', 7)
    canvas.setFillColor(G.MUTED)
    canvas.drawString(MARGIN, 17,
                      'Perimeter detection for a 350 mm mobile robot  |  final answer  |  '
                      '2026-09-12  |  full 100-page reference: '
                      'radar-compare/output/perimeter-sensing-for-small-robots.pdf')
    canvas.drawRightString(w - MARGIN, 17, '%d of %d' % (canvas.getPageNumber(),
                                                         TARGET_PAGES))
    canvas.restoreState()


def build(scale):
    """Render at a given type scale. Returns the page count."""
    for name, base in [('Body', 9.6), ('Li1', 9.6), ('Li2', 9.6), ('Cell', 7.0),
                       ('CellHead', 7.0), ('CellTiny', 6.0), ('CellTinyHead', 6.0),
                       ('Section', 12.5), ('Minor', 10.6), ('Chapter', 19),
                       ('Small', 7.6), ('CodeBlk', 7.2), ('Caption', 7.6),
                       ('Quote', 9.6)]:
        st = G.S[name]
        st.fontSize = base * scale
        st.leading = base * scale * (1.40 if name in ('Body', 'Li1', 'Li2', 'Quote')
                                     else 1.26)

    doc = BaseDocTemplate(
        str(OUT), pagesize=PAGE, leftMargin=MARGIN, rightMargin=MARGIN,
        topMargin=34, bottomMargin=34,
        title='Perimeter detection for a 350 mm robot - the best three options',
        author='Jeremy Proffitt robot project',
        subject='Three costed builds, a recommendation, and what fits each of the '
                'three robot projects')
    frame = Frame(MARGIN, 34, PAGE[0] - 2 * MARGIN, PAGE[1] - 34 - 40, id='f',
                  leftPadding=0, rightPadding=0, topPadding=0, bottomPadding=0)
    doc.addPageTemplates([PageTemplate(id='p', pagesize=PAGE, frames=[frame],
                                       onPage=footer)])
    story = G.render_markdown(SRC, PAGE[0] - 2 * MARGIN, wide_table_threshold=5)
    doc.build(story)
    d = fitz.open(str(OUT))
    n = d.page_count
    d.close()
    return n


def main():
    OUT.parent.mkdir(parents=True, exist_ok=True)
    # Shrink the type scale until it fits the target page count, then stop.
    scale = 1.0
    for _ in range(14):
        n = build(scale)
        print('scale %.3f -> %d pages' % (scale, n))
        if n <= TARGET_PAGES:
            break
        scale -= 0.025
    else:
        print('WARNING: could not reach %d pages' % TARGET_PAGES)

    d = fitz.open(str(OUT))
    pages = d.page_count
    text = ''.join(p.get_text() for p in d)
    problems = []
    for i, page in enumerate(d):
        for block in page.get_text('blocks'):
            x0, _, x1, _ = block[:4]
            if x1 > page.rect.width - MARGIN + 3 or x0 < MARGIN - 3:
                problems.append('page %d: text crosses the margin' % (i + 1))
                break
    d.close()
    print('pages: %d' % pages)
    print('words: %d' % len(text.split()))
    print('type scale: %.3f (body %.1f pt)' % (scale, 9.6 * scale))
    print('file size: %.0f kB' % (OUT.stat().st_size / 1000))
    print('layout: %s' % ('; '.join(problems) if problems
                          else 'no text outside the margins'))
    return 0 if pages == TARGET_PAGES and not problems else 1


if __name__ == '__main__':
    sys.exit(main())
