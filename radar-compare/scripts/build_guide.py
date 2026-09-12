"""Build the perimeter-sensing reference PDF from the checked-in markdown and CSV.

Content comes from radar-compare/docs/*.md in the order named in CHAPTERS, from
radar-compare/data/*.csv for the comparison grids, and from
radar-compare/data/geometry.json for every computed figure. Nothing is typed
into this script that is not layout.

Run: python scripts/build_guide.py
Output: radar-compare/output/perimeter-sensing-for-small-robots.pdf
"""
from pathlib import Path
import csv
import html
import json
import re
import sys

import fitz
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter, landscape
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import (BaseDocTemplate, PageTemplate, Frame, Paragraph,
                                Spacer, PageBreak, NextPageTemplate, Table,
                                TableStyle, KeepTogether)

ROOT = Path(__file__).resolve().parents[1]
DOCS = ROOT / 'docs'
DATA = ROOT / 'data'
OUT = ROOT / 'output' / 'perimeter-sensing-for-small-robots.pdf'

PORTRAIT = letter                       # 612 x 792
WIDE = landscape(letter)                # 792 x 612
XWIDE = (1224, 792)                     # double-wide for the master grids

MARGIN = 40
INK = colors.HexColor('#111827')
MUTED = colors.HexColor('#4b5563')
RULE = colors.HexColor('#c3cbd6')
ACCENT = colors.HexColor('#0f4c81')
HEAD_BG = colors.HexColor('#dde8f3')
ZEBRA = colors.HexColor('#f4f6f9')

FONT_DIR = Path('C:/Windows/Fonts')
for name, filename in [('Text', 'arial.ttf'), ('Text-Bold', 'arialbd.ttf'),
                       ('Text-Italic', 'ariali.ttf'), ('Mono', 'consola.ttf'),
                       ('Mono-Bold', 'consolab.ttf')]:
    pdfmetrics.registerFont(TTFont(name, str(FONT_DIR / filename)))
pdfmetrics.registerFontFamily('Text', normal='Text', bold='Text-Bold',
                              italic='Text-Italic', boldItalic='Text-Bold')

S = getSampleStyleSheet()
S.add(ParagraphStyle('Body', fontName='Text', fontSize=9.6, leading=13.4,
                     textColor=INK, spaceAfter=6.5, splitLongWords=True))
S.add(ParagraphStyle('Title1', parent=S['Body'], fontName='Text-Bold', fontSize=30,
                     leading=34, textColor=ACCENT, spaceAfter=12))
S.add(ParagraphStyle('Subtitle', parent=S['Body'], fontSize=13, leading=18,
                     textColor=MUTED, spaceAfter=16))
S.add(ParagraphStyle('Chapter', parent=S['Body'], fontName='Text-Bold',
                     fontSize=19, leading=23, textColor=ACCENT, spaceBefore=2,
                     spaceAfter=11, keepWithNext=True))
S.add(ParagraphStyle('Section', parent=S['Body'], fontName='Text-Bold', fontSize=12.5,
                     leading=16, spaceBefore=11, spaceAfter=5, keepWithNext=True))
S.add(ParagraphStyle('Minor', parent=S['Body'], fontName='Text-Bold', fontSize=10.6,
                     leading=14, spaceBefore=8, spaceAfter=4, keepWithNext=True))
S.add(ParagraphStyle('Small', parent=S['Body'], fontSize=7.6, leading=10, spaceAfter=3))
S.add(ParagraphStyle('Cell', parent=S['Body'], fontSize=7.0, leading=8.8, spaceAfter=0))
S.add(ParagraphStyle('CellHead', parent=S['Cell'], fontName='Text-Bold'))
S.add(ParagraphStyle('CellTiny', parent=S['Cell'], fontSize=6.0, leading=7.4))
S.add(ParagraphStyle('CellTinyHead', parent=S['CellTiny'], fontName='Text-Bold'))
S.add(ParagraphStyle('CodeBlk', fontName='Mono', fontSize=7.2, leading=9.2, textColor=INK,
                     spaceAfter=0, splitLongWords=True))
S.add(ParagraphStyle('Li1', parent=S['Body'], leftIndent=13, firstLineIndent=-10,
                     spaceAfter=3.5))
S.add(ParagraphStyle('Li2', parent=S['Li1'], leftIndent=27, firstLineIndent=-10))
S.add(ParagraphStyle('Quote', parent=S['Body'], leftIndent=14, textColor=MUTED,
                     fontName='Text-Italic'))
S.add(ParagraphStyle('Caption', parent=S['Small'], textColor=MUTED, spaceBefore=2))


# --------------------------------------------------------------------------
# inline markdown
# --------------------------------------------------------------------------
def clean(text):
    for bad, good in [('\u2011', '-'), ('\u2013', '-'), ('\u2014', ' - '),
                      ('\u00a0', ' '), ('\u2018', "'"), ('\u2019', "'"),
                      ('\u201c', '"'), ('\u201d', '"'), ('\u2026', '...'),
                      ('\u00b0', ' deg'), ('\u2265', '>='), ('\u2264', '<='),
                      ('\u00d7', 'x'), ('\u2192', '->'), ('\u00b5', 'u'),
                      ('\u03bc', 'u'), ('\u2248', '~'), ('\u00b1', '+/-'),
                      ('\u2122', ''), ('\u00ae', ''), ('\u2022', '-')]:
        text = text.replace(bad, good)
    return text


def inline(text):
    """Markdown inline syntax to reportlab's mini-HTML.

    Finished <link> tags are parked in placeholders as they are produced, so the
    bare-URL autolinker at the end cannot match a URL that is already inside an
    href attribute and nest a link inside a link.
    """
    parked = []

    def park(markup):
        parked.append(markup)
        return '\x00%d\x00' % (len(parked) - 1)

    text = html.escape(clean(str(text)))
    text = re.sub(r'`([^`]+)`', r'<font name="Mono">\1</font>', text)
    text = re.sub(r'\*\*([^*]+)\*\*', r'<b>\1</b>', text)
    text = re.sub(r'(?<![*\w])\*([^*\n]+)\*(?![*\w])', r'<i>\1</i>', text)
    # [label](http://...) -> a real link
    text = re.sub(r'\[([^\]]+)\]\((https?://[^)\s]+)\)',
                  lambda m: park('<link href="%s" color="#0f4c81">%s</link>'
                                 % (m.group(2), m.group(1))), text)
    # [label](anything-else) -> just the label
    text = re.sub(r'\[([^\]]+)\]\(([^)\s]+)\)', r'\1', text)
    # bare URL -> a link on itself
    text = re.sub(r'(?<![\w/"=])(https?://[^\s<>)\]"]+)',
                  lambda m: park('<link href="%s" color="#0f4c81">%s</link>'
                                 % (m.group(1), m.group(1))), text)
    return re.sub(r'\x00(\d+)\x00', lambda m: parked[int(m.group(1))], text)


def para(text, style='Body'):
    return Paragraph(inline(text), S[style])


# --------------------------------------------------------------------------
# tables
# --------------------------------------------------------------------------
def _fit_widths(headers, rows, avail, tiny):
    """Column widths proportional to the longest content, floored and capped."""
    n = len(headers)
    weights = []
    for i in range(n):
        longest = len(str(headers[i]))
        for r in rows:
            if i < len(r):
                for chunk in str(r[i]).split():
                    longest = max(longest, len(chunk))
                longest = max(longest, min(len(str(r[i])), 46))
        weights.append(max(4.0, float(longest)))
    total = sum(weights)
    floor = 26.0 if tiny else 32.0
    widths = [max(floor, avail * w / total) for w in weights]
    scale = avail / sum(widths)
    return [w * scale for w in widths]


def make_table(headers, rows, avail, tiny=False, widths=None, align_right=()):
    cs = 'CellTiny' if tiny else 'Cell'
    hs = 'CellTinyHead' if tiny else 'CellHead'
    if widths is None:
        widths = _fit_widths(headers, rows, avail, tiny)
    data = [[Paragraph(inline(h), S[hs]) for h in headers]]
    for r in rows:
        cells = list(r) + [''] * (len(headers) - len(r))
        data.append([Paragraph(inline(c), S[cs]) for c in cells[:len(headers)]])
    t = Table(data, colWidths=widths, repeatRows=1, hAlign='LEFT')
    style = [
        ('BACKGROUND', (0, 0), (-1, 0), HEAD_BG),
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ('LINEBELOW', (0, 0), (-1, 0), 0.9, ACCENT),
        ('LINEBELOW', (0, 1), (-1, -2), 0.25, RULE),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, ZEBRA]),
        ('LEFTPADDING', (0, 0), (-1, -1), 3.5),
        ('RIGHTPADDING', (0, 0), (-1, -1), 3.5),
        ('TOPPADDING', (0, 0), (-1, -1), 2.6),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 2.6),
    ]
    for c in align_right:
        style.append(('ALIGN', (c, 1), (c, -1), 'RIGHT'))
    t.setStyle(TableStyle(style))
    return t


# --------------------------------------------------------------------------
# markdown block parser
# --------------------------------------------------------------------------
TABLE_SEP = re.compile(r'^\s*\|?[\s:\-|]+\|[\s:\-|]+$')

FT_LABELS = ['1 ft', '3 ft', '5 ft', '8 ft', '10 ft']
FT_KEYS = [1, 3, 5, 8, 10]


def generated_block(kind, arg, avail):
    """Tables the markdown asks for by placeholder instead of transcribing.

    {{SPEC_GRID}}      every sensor, the specs that decide a design
    {{GRID:human}}     capability against an adult at each survey distance
    {{GRID:cat}}       the same against a cat
    {{GRID:object}}    the same against a 30 mm chair leg
    {{WIDTH_GRID}}     beam footprint width per sensor per distance
    {{LEVELS}}         the key to the capability levels
    """
    path = DATA / 'master-grid.csv'
    if kind in ('SPEC_GRID', 'GRID', 'WIDTH_GRID') and not path.exists():
        return [para('[%s: data/master-grid.csv has not been generated yet]'
                     % kind, 'Small')]

    if kind == 'LEVELS':
        cap = json.loads((DATA / 'capability.json').read_text(encoding='utf-8'))
        rows = [[k, v] for k, v in sorted(cap['levels'].items())]
        return [make_table(['Level', 'What the sensor can tell you'], rows, avail)]

    rows = read_csv(path)

    if kind == 'SPEC_GRID':
        hdr = ['Sensor', 'Vendor / SKU', 'Technology', 'USD', 'FoV H x V',
               'Zones', 'Rated range', 'Rate', 'Interface', 'Line of sight']
        body = [[r['name'], '%s %s' % (r['vendor'], r['sku']), r['tech'],
                 r['price_usd'], '%s x %s' % (r['fov_h_deg'] or '-',
                                              r['fov_v_deg'] or '-'),
                 r['zones'], r['max_range_m'], r['update_hz'], r['interface'],
                 r['needs_line_of_sight']] for r in rows]
        return [make_table(hdr, body, avail, tiny=True)]

    if kind == 'WIDTH_GRID':
        hdr = ['Sensor', 'FoV H'] + FT_LABELS
        body = [[r['name'], r['fov_h_deg']] +
                [str(r.get('width_%dft_mm' % k, '')) for k in FT_KEYS]
                for r in rows]
        return [make_table(hdr, body, avail, tiny=True)]

    if kind == 'GRID':
        col = {'human': 'human', 'cat': 'pet', 'pet': 'pet',
               'object': 'object'}.get(arg or 'human', 'human')
        hdr = ['Sensor', 'Technology'] + FT_LABELS
        body = [[r['name'], r['tech']] +
                [r.get('%s_%dft' % (col, k), '') for k in FT_KEYS]
                for r in rows]
        return [make_table(hdr, body, avail, tiny=True)]

    return [para('[unknown generated block %s]' % kind, 'Small')]


def split_row(line):
    line = line.strip()
    if line.startswith('|'):
        line = line[1:]
    if line.endswith('|'):
        line = line[:-1]
    return [c.strip() for c in line.split('|')]


def render_markdown(path, avail, page_id='portrait', wide_table_threshold=7):
    """Parse a restricted GitHub-markdown subset into reportlab flowables.

    Supported: # ## ### #### headings, - and * bullets (two levels), 1. ordered
    lists, ``` fenced code, > blockquote, --- rule, pipe tables, and inline
    **bold** *italic* `code` [link](url).
    """
    story = []
    buf = []
    code = []
    in_code = False
    table_head = None
    table_rows = []
    item = [None, []]        # [style, parts] of the list item currently open

    def flush_item():
        """Emit the open list item. A wrapped bullet is one paragraph, not two.

        GitHub markdown lets a list item run on over following lines - indented
        or not - until a blank line or a new block. Without this, every wrapped
        bullet in the document set its tail as a separate body paragraph at the
        left margin, which reads as a broken hanging indent.
        """
        if item[0]:
            story.append(para(' '.join(item[1]), item[0]))
        item[0], item[1] = None, []

    def flush_text():
        flush_item()
        if buf:
            story.append(para(' '.join(buf)))
            buf.clear()

    def flush_table():
        nonlocal table_head, table_rows
        if table_head:
            tiny = len(table_head) >= wide_table_threshold
            story.append(Spacer(1, 3))
            story.append(make_table(table_head, table_rows, avail, tiny=tiny))
            story.append(Spacer(1, 7))
        table_head, table_rows = None, []

    def flush_code():
        if code:
            body = [Paragraph(inline(l) if l.strip() else '&nbsp;', S['CodeBlk'])
                    for l in code]
            box = Table([[body]], colWidths=[avail], hAlign='LEFT')
            box.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor('#f2f4f7')),
                ('BOX', (0, 0), (-1, -1), 0.4, RULE),
                ('LEFTPADDING', (0, 0), (-1, -1), 7),
                ('RIGHTPADDING', (0, 0), (-1, -1), 7),
                ('TOPPADDING', (0, 0), (-1, -1), 5),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 5)]))
            story.append(box)
            story.append(Spacer(1, 7))
            code.clear()

    lines = path.read_text(encoding='utf-8-sig').splitlines()
    for i, raw in enumerate(lines):
        line = raw.rstrip()

        if line.strip().startswith('```'):
            flush_text(); flush_table()
            if in_code:
                flush_code()
            in_code = not in_code
            continue
        if in_code:
            code.append(raw)
            continue

        stripped = line.strip()

        # generated-table placeholder, e.g. {{GRID:human}}
        m = re.match(r'^\{\{([A-Z_]+)(?::([a-z_]+))?\}\}$', stripped)
        if m:
            flush_text(); flush_table()
            story.extend(generated_block(m.group(1), m.group(2), avail))
            continue

        # pipe table
        if stripped.startswith('|') and stripped.count('|') >= 2:
            nxt = lines[i + 1].strip() if i + 1 < len(lines) else ''
            if table_head is None:
                if TABLE_SEP.match(nxt):
                    flush_text()
                    table_head = split_row(stripped)
                    continue
            else:
                if TABLE_SEP.match(stripped):
                    continue
                table_rows.append(split_row(stripped))
                continue
        if table_head is not None and not stripped.startswith('|'):
            flush_table()

        if not stripped:
            flush_text()
            continue
        if stripped.startswith('#### '):
            flush_text(); story.append(para(stripped[5:], 'Minor')); continue
        if stripped.startswith('### '):
            flush_text(); story.append(para(stripped[4:], 'Minor')); continue
        if stripped.startswith('## '):
            flush_text(); story.append(para(stripped[3:], 'Section')); continue
        if stripped.startswith('# '):
            flush_text(); story.append(para(stripped[2:], 'Chapter')); continue
        if stripped in ('---', '***', '___'):
            flush_text()
            story.append(Spacer(1, 4))
            rule = Table([['']], colWidths=[avail], rowHeights=[0.6])
            rule.setStyle(TableStyle([('BACKGROUND', (0, 0), (-1, -1), RULE)]))
            story.append(rule)
            story.append(Spacer(1, 6))
            continue
        if stripped.startswith('> '):
            flush_text(); story.append(para(stripped[2:], 'Quote')); continue
        m = re.match(r'^(\s*)[-*+]\s+(.*)$', line)
        if m:
            flush_text()
            depth = len(m.group(1)) // 2
            item[0] = 'Li2' if depth else 'Li1'
            item[1] = ['- ' + m.group(2)]
            continue
        m = re.match(r'^(\s*)(\d+)\.\s+(.*)$', line)
        if m:
            flush_text()
            depth = len(m.group(1)) // 2
            item[0] = 'Li2' if depth else 'Li1'
            item[1] = [m.group(2) + '. ' + m.group(3)]
            continue
        if item[0]:
            # a run-on line belongs to the list item above it, not to a new
            # paragraph; a blank line is what ends an item
            item[1].append(stripped)
            continue
        buf.append(stripped)

    flush_text(); flush_table()
    if in_code:
        flush_code()
    return story


# --------------------------------------------------------------------------
# CSV-driven grids
# --------------------------------------------------------------------------
def read_csv(path):
    with path.open(encoding='utf-8-sig', newline='') as fh:
        return list(csv.DictReader(fh))


def csv_table(path, columns, avail, tiny=True, headers=None):
    """columns: list of CSV field names. headers: display names, defaults to columns."""
    rows = read_csv(path)
    hdr = headers or columns
    body = [[r.get(c, '') for c in columns] for r in rows]
    return make_table(hdr, body, avail, tiny=tiny)


# --------------------------------------------------------------------------
# document
# --------------------------------------------------------------------------
class Guide(BaseDocTemplate):
    def __init__(self, *a, **kw):
        BaseDocTemplate.__init__(self, *a, **kw)
        self.outline = []

    def afterFlowable(self, f):
        if isinstance(f, Paragraph) and f.style.name in ('Chapter', 'Section'):
            level = 0 if f.style.name == 'Chapter' else 1
            key = 'sec%d' % len(self.outline)
            title = f.getPlainText()
            self.canv.bookmarkPage(key)
            self.canv.addOutlineEntry(title, key, level=level, closed=bool(level))
            self.outline.append((level, title, self.page))


def decorate(canvas, doc):
    w, h = canvas._pagesize
    canvas.saveState()
    canvas.setStrokeColor(RULE)
    canvas.setLineWidth(0.5)
    canvas.line(MARGIN, 30, w - MARGIN, 30)
    canvas.setFont('Text', 7.2)
    canvas.setFillColor(MUTED)
    canvas.drawString(MARGIN, 19,
                      'Perimeter detection for a 350 mm mobile robot  |  '
                      'revision A  |  research date 2026-09-12')
    canvas.drawRightString(w - MARGIN, 19, str(canvas.getPageNumber()))
    canvas.restoreState()


def frame_for(pagesize):
    w, h = pagesize
    return Frame(MARGIN, 38, w - 2 * MARGIN, h - 38 - 42, id='f',
                 leftPadding=0, rightPadding=0, topPadding=0, bottomPadding=0)


AVAIL = {
    'portrait': PORTRAIT[0] - 2 * MARGIN,
    'wide': WIDE[0] - 2 * MARGIN,
    'xwide': XWIDE[0] - 2 * MARGIN,
}


# --------------------------------------------------------------------------
# geometry-derived tables, straight from data/geometry.json
# --------------------------------------------------------------------------
def geom():
    return json.loads((DATA / 'geometry.json').read_text(encoding='utf-8'))


def t_beam_width(g, avail):
    hdr = ['Field of view'] + ['%d ft' % f for f in g['survey_distances_ft']]
    rows = []
    for r in g['beam_width']:
        cells = ['%d deg' % r['fov_deg']]
        for f in g['survey_distances_ft']:
            w = r['widths']['%dft' % f]
            cells.append('unbounded' if w['mm'] is None
                         else '%s mm / %s in' % (round(w['mm']), w['in']))
        rows.append(cells)
    return make_table(hdr, rows, avail, tiny=True)


def t_ring_count(g, avail):
    hdr = ['Field of view', 'Bare 360 deg', 'With 5 deg overlap',
           'With 10 deg overlap', 'With 25 percent overlap']
    rows = [['%d deg' % r['fov_deg'], str(r['no_overlap'] or '-'),
             str(r['overlap_5deg'] or '-'), str(r['overlap_10deg'] or '-'),
             str(r['overlap_25pct'] or '-')] for r in g['ring_count']]
    return make_table(hdr, rows, avail)


def t_blind_wedge(g, avail):
    fovs = [15, 25, 27, 45, 63, 65, 90, 100, 120]
    hdr = ['Sensors in the ring'] + ['%d deg' % f for f in fovs]
    rows = []
    for n in [3, 4, 5, 6, 8, 10, 12, 16]:
        cells = ['%d' % n]
        for fov in fovs:
            m = next(b for b in g['blind_wedge']
                     if b['n_sensors'] == n and b['fov_deg'] == fov)
            if not m['closes']:
                cells.append('never')
            elif m['closes_at_platform_surface']:
                cells.append('0')
            else:
                cells.append('%s mm' % round(m['coverage_closes_from_edge_mm']))
        rows.append(cells)
    return make_table(hdr, rows, avail, tiny=True)


def t_zone_footprint(g, avail):
    hdr = ['Grid imager'] + ['%d ft' % f for f in g['survey_distances_ft']]
    rows = []
    for r in g['zone_footprint']:
        cells = [r['sensor']]
        for f in g['survey_distances_ft']:
            c = r['centre_zone']['%dft' % f]
            cells.append('%s mm  (adult %s, cat %s)'
                         % (round(c['mm']),
                            c['zones_across_adult_human_standing'],
                            c['zones_across_cat']))
        rows.append(cells)
    return make_table(hdr, rows, avail, tiny=True)


def t_vertical(g, avail, tilt=0):
    watch = ['adult_human_standing', 'toddler', 'large_dog', 'small_dog', 'cat',
             'cat_lying', 'power_cable', 'table_top']
    hdr = ['Mount height', 'Vertical FoV', 'Floor strike'] + \
          [w.replace('_', ' ') for w in watch]
    rows = []
    for e in g['vertical']:
        if e['down_tilt_deg'] != tilt or e['mount_h_mm'] not in (100, 200, 400, 800):
            continue
        if e['fov_v_deg'] not in (25, 45, 63, 90):
            continue
        cells = ['%d mm' % e['mount_h_mm'], '%d deg' % e['fov_v_deg'],
                 '-' if e['floor_strike_mm'] is None else '%s mm' % round(e['floor_strike_mm'])]
        for w in watch:
            flags = ''.join('Y' if e['targets'][w]['%dft' % f]['visible'] else '.'
                            for f in g['survey_distances_ft'])
            cells.append(flags)
        rows.append(cells)
    return make_table(hdr, rows, avail, tiny=True)


def t_stopping(g, avail):
    hdr = ['Speed', 'Sensor and update rate', 'Sensor lag', 'Braking',
           'Reaction distance', 'Braking distance', 'Total stop']
    rows = []
    for s in g['stopping']:
        if s['decel'] != 'firm 0.5 g':
            continue
        if s['speed_m_s'] not in (0.3, 0.5, 1.0):
            continue
        rows.append(['%.1f m/s' % s['speed_m_s'], s['sensor'],
                     '%s ms' % s['sensor_latency_ms'], s['decel'],
                     '%s mm' % round(s['reaction_mm']),
                     '%s mm' % round(s['braking_mm']),
                     '%s mm / %s in' % (round(s['total_mm']), s['total_in'])])
    return make_table(hdr, rows, avail, tiny=True)


# --------------------------------------------------------------------------
# the document
# --------------------------------------------------------------------------
# (chapter file, page template, figures to place after the chapter body)
CHAPTERS = [
    ('executive-summary.md',          'portrait', []),
    ('the-problem.md',                'portrait', []),
    ('coverage-geometry.md',          'portrait', [
        ('beam_width.png', 500, 'Beam footprint width against range. A sensor does not '
         'see a ray; it sees a cone, and at 10 ft a 63 deg cone is 3.7 m wide.'),
        ('ring_8x19.png', 330, 'Eight VL53L1X at their true 19 deg horizontal cone '
         'cover 152 deg of 360 deg. Most of the perimeter is blind at every range.'),
        ('ring_16x19.png', 330, 'Sixteen of them still total only 304 deg. A ring of '
         'single-zone ST parts cannot be closed at any sane count.'),
        ('ring_8x45.png', 330, 'Eight VL53L5CX at 45 deg horizontal total exactly '
         '360 deg. Exactly is not enough: the wedges never close.'),
        ('ring_10x45.png', 330, 'Ten gives 90 deg of overlap and closes the wedges '
         '678 mm out - still beyond the robot at walking pace.'),
        ('ring_12x45.png', 330, 'Twelve closes them 338 mm past the edge. This is the '
         'ring the recommendation is built on.'),
        ('ring_12x45_square.png', 330, 'The same twelve on a 350 mm SQUARE platform. '
         'The corners push four sensors outboard and skew the wedges.'),
        ('ring_8x60.png', 330, 'Eight VL53L7CX at 60 deg horizontal close 495 mm out '
         'with four fewer parts, four fewer apertures and four fewer addresses.'),
        ('vertical_low_45.png', 520, 'Ring at 100 mm, 45 deg vertical. Everything from '
         'a lying cat upward is in the beam, at the price of constant floor return.'),
        ('vertical_high_45.png', 520, 'The same sensor at 800 mm. A standing cat at '
         '1 ft is under the beam entirely - this is what a robot runs over.'),
        ('vertical_high_45_tilt.png', 520, 'Adding 15 deg of down-tilt at 800 mm buys '
         'back the near field and costs the top of the beam.'),
    ]),
    ('modality-primer.md',            'portrait', []),
    ('tof-catalogue.md',              'portrait', []),
    ('mmwave-catalogue.md',           'portrait', []),
    ('thermal-catalogue.md',          'portrait', [
        ('pixel_fill.png', 640, 'How many zones a subject covers. Below one zone the '
         'sensor can report presence but never shape, so it can never classify.'),
    ]),
    ('master-grid.md',                'xwide',    []),
    ('range-capability.md',           'wide',     []),
    ('discrimination.md',             'portrait', []),
    ('integration.md',                'portrait', []),
    ('failure-modes-safety.md',       'portrait', []),
    ('recommendations.md',            'portrait', []),
    ('guide-st-grid-tof.md',          'portrait', []),
    ('guide-adafruit-4010.md',        'portrait', []),
    ('options-other-st-and-lidar.md', 'portrait', []),
    ('robot-project-options.md',      'portrait', []),
    ('prior-art.md',                  'portrait', []),
    ('bom.md',                        'wide',     []),
    ('sources.md',                    'portrait', []),
]


def figure(name, width, caption):
    from reportlab.platypus import Image
    path = ROOT / 'figures' / name
    if not path.exists():
        return []
    img = Image(str(path))
    ratio = img.imageHeight / float(img.imageWidth)
    img.drawWidth = width
    img.drawHeight = width * ratio
    if img.drawHeight > 560:
        img.drawHeight = 560
        img.drawWidth = 560 / ratio
    img.hAlign = 'LEFT'
    return [Spacer(1, 6), img, para(caption, 'Caption'), Spacer(1, 8)]


def build():
    g = geom()
    doc = Guide(str(OUT), pagesize=PORTRAIT, leftMargin=MARGIN, rightMargin=MARGIN,
                topMargin=42, bottomMargin=38,
                title='Perimeter detection for a 350 mm mobile robot',
                author='Jeremy Proffitt robot project',
                subject='Time-of-flight, mmWave radar and thermal IR perimeter '
                        'sensing: catalogue, coverage geometry and recommendation')
    doc.addPageTemplates([
        PageTemplate(id='portrait', pagesize=PORTRAIT, frames=[frame_for(PORTRAIT)],
                     onPage=decorate),
        PageTemplate(id='wide', pagesize=WIDE, frames=[frame_for(WIDE)],
                     onPage=decorate),
        PageTemplate(id='xwide', pagesize=XWIDE, frames=[frame_for(XWIDE)],
                     onPage=decorate),
    ])

    story = [
        Spacer(1, 58),
        para('Perimeter detection for a 350 mm mobile robot', 'Title1'),
        para('Time-of-flight, mmWave radar and thermal infrared: a catalogue of every '
             'candidate part, the coverage geometry that decides how many of them you '
             'need, and what each one can actually tell you about a human, a pet or a '
             'box at 1, 3, 5, 8 and 10 feet.', 'Subtitle'),
        para('Revision A  |  research date 2026-09-12  |  vendors surveyed: Adafruit, '
             'DFRobot, STMicroelectronics, and the wider ToF and lidar market', 'Small'),
        Spacer(1, 20),
    ]

    missing = []
    for name, template, figs in CHAPTERS:
        path = DOCS / name
        if not path.exists():
            missing.append(name)
            continue
        story.append(NextPageTemplate(template))
        story.append(PageBreak())
        story.extend(render_markdown(
            path, AVAIL[template],
            wide_table_threshold=6 if template == 'portrait' else 9))
        for fname, width, caption in figs:
            story.extend(figure(fname, min(width, AVAIL[template]), caption))

    # computed appendix, always present because it comes from geometry.json
    story.append(NextPageTemplate('wide'))
    story.append(PageBreak())
    story.append(para('Appendix: computed coverage tables', 'Chapter'))
    story.append(para(
        'Every figure below is produced by radar-compare/scripts/geometry.py from '
        'first principles, not copied from a vendor page. Re-run that script to '
        'reproduce them.'))
    APPENDIX = [
        ('Beam footprint width', 'Full lateral width of the cone, w = 2 d tan(FoV/2).',
         t_beam_width),
        ('Sensors needed to close a 360 degree ring',
         'Bare closure needs n x FoV >= 360. The overlap columns add the margin that '
         'tolerates mounting error and one dead sensor.', t_ring_count),
        ('Where the blind wedge between adjacent sensors closes',
         'Measured outward from the platform edge, sensors on a 175 mm radius aimed '
         'radially. "never" means n x FoV < 360, where no range ever closes the gap.',
         t_blind_wedge),
        ('Centre-zone footprint of the grid imagers',
         'One zone of the array, with how many zones the subject spans across.',
         t_zone_footprint),
        ('Vertical coverage, no down-tilt',
         'Y means part of the subject is inside the beam at 1 / 3 / 5 / 8 / 10 ft; a '
         'dot means it is missed entirely. Floor strike is where the beam first '
         'reaches the floor.', lambda gg, av: t_vertical(gg, av, 0)),
        ('Vertical coverage, 15 degree down-tilt', 'Same, sensor tilted down.',
         lambda gg, av: t_vertical(gg, av, 15)),
        ('Stopping distance against sensor update rate',
         'Reaction distance is speed x (sensor period + 30 ms of compute). An obstacle '
         'closer than the total must never be the first time the robot sees it.',
         t_stopping),
    ]
    for title, note, fn in APPENDIX:
        story.append(para(title, 'Section'))
        story.append(para(note, 'Small'))
        story.append(fn(g, AVAIL['wide']))
        story.append(Spacer(1, 12))

    doc.multiBuild(story)
    return doc, missing


def qa(doc):
    """Open the built PDF and check it actually renders."""
    d = fitz.open(str(OUT))
    text = ''.join(p.get_text() for p in d)
    problems = []
    for i, page in enumerate(d):
        pw = page.rect.width
        for block in page.get_text('blocks'):
            x0, y0, x1, y1 = block[:4]
            if x1 > pw - MARGIN + 3 or x0 < MARGIN - 3:
                problems.append('page %d: text crosses the margin (x %.0f-%.0f of %.0f)'
                                % (i + 1, x0, x1, pw))
                break
    print('pages: %d' % d.page_count)
    print('characters of extractable text: %d' % len(text))
    print('outline entries: %d' % len(doc.outline))
    print('file size: %.2f MB' % (OUT.stat().st_size / 1e6))
    if problems:
        print('LAYOUT PROBLEMS: %d' % len(problems))
        for p in problems[:20]:
            print('  ' + p)
    else:
        print('layout: no text outside the margins')
    d.close()
    return problems


def main():
    OUT.parent.mkdir(parents=True, exist_ok=True)
    doc, missing = build()
    print('wrote %s' % OUT)
    if missing:
        print('MISSING CHAPTERS (skipped): %s' % ', '.join(missing))
    qa(doc)
    return 0


if __name__ == '__main__':
    sys.exit(main())
