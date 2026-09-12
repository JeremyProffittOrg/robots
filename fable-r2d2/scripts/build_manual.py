#!/usr/bin/env python3
"""Build the illustrated fable-r2d2 fabrication and assembly manual.

Every page is generated from the checked-in package sources at run time: the Markdown
documents in docs/, the bills of material in bom/, the CAD reports in cad/, the circuit
sheets in electronics/ and the MATLAB-style drawing set in output/drawings/. Nothing in
this file hard-codes design content.

Outputs:
    output/pdf/r2d2-assembly-manual.pdf
    output/pdf/rendered/page-NNN.png   (60 dpi render check, git-ignored)
    docs/pdf-check.json

Usage:
    python scripts/build_manual.py
    python scripts/build_manual.py --allow-missing-figures   (development only)

A referenced drawing that is missing on disk is a hard failure: the build lists every
missing file and exits non-zero. --allow-missing-figures substitutes a labelled grey
placeholder instead and forces all_pass false, for use while the drawings are still
being rendered.
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import html
import json
import re
import sys
from datetime import date
from pathlib import Path

import fitz
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.units import inch
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import (BaseDocTemplate, Flowable, Frame, Image, KeepTogether,
                                NextPageTemplate, PageBreak, PageTemplate, Paragraph,
                                Preformatted, Spacer, Table, TableStyle)
from reportlab.platypus.tableofcontents import TableOfContents

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'output/pdf/r2d2-assembly-manual.pdf'
RENDER_DIR = ROOT / 'output/pdf/rendered'
SVG_DIR = RENDER_DIR / '_svg'
CHECK_JSON = ROOT / 'docs/pdf-check.json'

TITLE = 'fable-r2d2 - R2-D2 fabrication and assembly manual'
FOOTER_NOTE = 'CAD design; not physically validated'
REQUIRED_TEXT = ['317', 'lazy susan', 'KB2040', 'charge port', 'tip-back']
MIN_PAGES = 40
RENDER_DPI = 60

PORTRAIT = letter                                   # 612 x 792 pt
LANDSCAPE = (17 * inch, 11 * inch)                  # 1224 x 792 pt
MARGIN_X = 40.0
MARGIN_TOP = 54.0
MARGIN_BOTTOM = 48.0
PORTRAIT_W = PORTRAIT[0] - 2 * MARGIN_X             # 532
PORTRAIT_H = PORTRAIT[1] - MARGIN_TOP - MARGIN_BOTTOM
LANDSCAPE_W = LANDSCAPE[0] - 2 * MARGIN_X           # 1144
LANDSCAPE_H = LANDSCAPE[1] - MARGIN_TOP - MARGIN_BOTTOM

INK = colors.HexColor('#131a24')
MUTED = colors.HexColor('#4b5563')
RULE = colors.HexColor('#c3ccd6')
ACCENT = colors.HexColor('#12446f')
HEAD_BG = colors.HexColor('#dde8f4')
ZEBRA = colors.HexColor('#f4f7fa')
CODE_BG = colors.HexColor('#f1f4f7')

FONT_DIR = Path('C:/Windows/Fonts')
FONT_FILES = [('Text', 'arial.ttf'), ('Text-Bold', 'arialbd.ttf'),
              ('Text-Italic', 'ariali.ttf'), ('Text-BoldItalic', 'arialbi.ttf'),
              ('Mono', 'consola.ttf'), ('Mono-Bold', 'consolab.ttf')]


def register_fonts() -> None:
    for name, filename in FONT_FILES:
        path = FONT_DIR / filename
        if not path.is_file():
            raise FileNotFoundError(f'Required font missing: {path}')
        pdfmetrics.registerFont(TTFont(name, str(path)))
    pdfmetrics.registerFontFamily('Text', normal='Text', bold='Text-Bold',
                                  italic='Text-Italic', boldItalic='Text-BoldItalic')
    pdfmetrics.registerFontFamily('Mono', normal='Mono', bold='Mono-Bold',
                                  italic='Mono', boldItalic='Mono-Bold')


STYLES: dict[str, ParagraphStyle] = {}


def build_styles() -> None:
    def add(name, **kw):
        kw.setdefault('fontName', 'Text')
        kw.setdefault('textColor', INK)
        STYLES[name] = ParagraphStyle(name, **kw)

    add('Body', fontSize=9.3, leading=12.8, spaceAfter=6.5, splitLongWords=True)
    add('Small', fontSize=7.6, leading=10.2, spaceAfter=4, textColor=MUTED)
    add('Caption', fontSize=8.0, leading=10.8, spaceBefore=4, spaceAfter=10,
        fontName='Text-Italic', textColor=MUTED, alignment=1)
    add('CoverTitle', fontSize=25, leading=30, fontName='Text-Bold', spaceAfter=8)
    add('CoverSub', fontSize=12.5, leading=17, spaceAfter=14, textColor=ACCENT)
    add('H1', fontSize=18.5, leading=23, fontName='Text-Bold', spaceBefore=2,
        spaceAfter=12, keepWithNext=True, textColor=ACCENT)
    # H1x looks like H1 but is deliberately invisible to the table of contents.
    add('H1x', fontSize=18.5, leading=23, fontName='Text-Bold', spaceBefore=2,
        spaceAfter=12, keepWithNext=True, textColor=ACCENT)
    add('H2', fontSize=12.6, leading=16, fontName='Text-Bold', spaceBefore=12,
        spaceAfter=6, keepWithNext=True)
    add('H3', fontSize=10.6, leading=14, fontName='Text-Bold', spaceBefore=9,
        spaceAfter=4, keepWithNext=True)
    add('H4', fontSize=9.6, leading=13, fontName='Text-Bold', spaceBefore=7,
        spaceAfter=3, keepWithNext=True)
    add('Code', fontName='Mono', fontSize=7.4, leading=9.8, textColor=colors.HexColor('#1d2733'))
    add('Cell', fontSize=7.3, leading=9.4, spaceAfter=0)
    add('CellHead', fontSize=7.3, leading=9.4, fontName='Text-Bold', spaceAfter=0)
    add('TOC0', fontSize=10.2, leading=15, fontName='Text-Bold', spaceBefore=7)
    add('TOC1', fontSize=8.8, leading=12.2, leftIndent=18, textColor=MUTED)
    for level in range(3):
        add(f'List{level}', fontSize=9.3, leading=12.8, spaceAfter=4.5,
            leftIndent=16 + level * 15, bulletIndent=3 + level * 15,
            bulletFontName='Text', splitLongWords=True)


# --------------------------------------------------------------------------- text

DASHES = {'\u2011': '-', '\u2012': '-', '\u2013': '-', '\u2014': ' - ', '\u2018': "'",
          '\u2019': "'", '\u201c': '"', '\u201d': '"', '\u00a0': ' ', '\u2212': '-',
          '\u2026': '...', '\u00b7': '-', '\u2022': '-'}


def clean(text: str) -> str:
    for bad, good in DASHES.items():
        text = text.replace(bad, good)
    return text


def inline(text: str) -> str:
    """Convert Markdown inline markup to ReportLab paragraph markup.

    Callers pass Markdown, never ReportLab markup: everything is escaped first, so a raw
    tag in the input would be printed literally.
    """
    text = html.escape(clean(str(text))).replace('\n', '<br/>')
    text = re.sub(r'`([^`]+)`', r'<font name="Mono" size="8.4">\1</font>', text)
    text = re.sub(r'\*\*([^*]+)\*\*', r'<b>\1</b>', text)
    text = re.sub(r'(?<!\*)\*([^*\n]+)\*(?!\*)', r'<i>\1</i>', text)
    text = re.sub(r'\[([^\]]+)\]\((https?://[^)\s]+)\)',
                  r'<link href="\2" color="#12446f"><u>\1</u></link>', text)
    text = re.sub(r'\[([^\]]+)\]\([^)\s]*\)', r'\1', text)
    return text


def plain(text: str) -> str:
    """Markdown stripped to bare text, for column-width measurement."""
    text = re.sub(r'\[([^\]]+)\]\([^)]*\)', r'\1', str(text))
    return re.sub(r'[`*]', '', clean(text))


def P(text: str, style: str = 'Body') -> Paragraph:
    return Paragraph(inline(text), STYLES[style])


class Rule(Flowable):
    """A thin horizontal rule that fills the frame width."""

    def __init__(self, thickness: float = 0.6, space: float = 5.0, colour=RULE):
        super().__init__()
        self.thickness, self.space, self.colour = thickness, space, colour
        self.width = 0.0
        self.height = thickness + 2 * space

    def wrap(self, availWidth, availHeight):
        self.width = availWidth
        return availWidth, self.height

    def draw(self):
        self.canv.setStrokeColor(self.colour)
        self.canv.setLineWidth(self.thickness)
        self.canv.line(0, self.space, self.width, self.space)


# --------------------------------------------------------------------------- tables

CELL_PAD = 4.0


def grid_table(header: list[str], rows: list[list[str]], widths: list[float],
               align: str = 'LEFT') -> Table:
    data = [[Paragraph(inline(c), STYLES['CellHead']) for c in header]]
    data += [[Paragraph(inline(c), STYLES['Cell']) for c in row] for row in rows]
    table = Table(data, colWidths=widths, repeatRows=1, hAlign=align)
    table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), HEAD_BG),
        ('LINEBELOW', (0, 0), (-1, 0), 0.8, ACCENT),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, ZEBRA]),
        ('GRID', (0, 0), (-1, -1), 0.25, RULE),
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ('LEFTPADDING', (0, 0), (-1, -1), CELL_PAD),
        ('RIGHTPADDING', (0, 0), (-1, -1), CELL_PAD),
        ('TOPPADDING', (0, 0), (-1, -1), 2.6),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 2.6),
    ]))
    return table


def column_widths(rows: list[list[str]], width: float,
                  floor: int = 6, ceiling: int = 46) -> list[float]:
    ncol = max(len(r) for r in rows)
    weights = []
    for index in range(ncol):
        longest = max((len(plain(r[index])) for r in rows if index < len(r)), default=1)
        weights.append(min(max(longest, floor), ceiling))
    total = float(sum(weights))
    return [width * w / total for w in weights]


SEP_CELL = re.compile(r'^:?-{2,}:?$')


def markdown_table(raw: list[str], width: float) -> Table:
    rows = [[cell.strip() for cell in line.strip().strip('|').split('|')] for line in raw]
    rows = [r for r in rows if not (r and all(SEP_CELL.match(c) or not c for c in r))]
    if not rows:
        return Spacer(1, 0)
    ncol = max(len(r) for r in rows)
    rows = [r + [''] * (ncol - len(r)) for r in rows]
    return grid_table(rows[0], rows[1:], column_widths(rows, width))


def code_block(lines: list[str], width: float) -> Table:
    text = '\n'.join(clean(line) for line in lines) or ' '
    per_char = STYLES['Code'].fontSize * 0.552
    limit = max(40, int((width - 2 * 7) / per_char))
    body = Preformatted(text, STYLES['Code'], maxLineLength=limit,
                        splitChars=' ,;:/=)]}>-')
    table = Table([[body]], colWidths=[width], hAlign='LEFT')
    table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, -1), CODE_BG),
        ('BOX', (0, 0), (-1, -1), 0.4, RULE),
        ('LEFTPADDING', (0, 0), (-1, -1), 7),
        ('RIGHTPADDING', (0, 0), (-1, -1), 7),
        ('TOPPADDING', (0, 0), (-1, -1), 5),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 5),
    ]))
    return table


# --------------------------------------------------------------------------- figures

class Figures:
    """Resolves every image the manual references and records what was embedded."""

    def __init__(self, allow_missing: bool):
        self.allow_missing = allow_missing
        self.embedded: list[str] = []
        self.missing: list[str] = []

    def _record(self, rel: str, present: bool) -> None:
        bucket = self.embedded if present else self.missing
        if rel not in bucket:
            bucket.append(rel)

    def image(self, rel: str, max_w: float, max_h: float):
        path = ROOT / rel
        if path.is_file():
            self._record(rel, True)
            picture = Image(str(path))
            picture._restrictSize(max_w, max_h)
            picture.hAlign = 'CENTER'
            return picture
        self._record(rel, False)
        return self._placeholder(rel, max_w, min(max_h, max_w * 0.62))

    @staticmethod
    def _placeholder(rel: str, width: float, height: float) -> Table:
        label = Paragraph(f'<b>figure pending: {html.escape(Path(rel).name)}</b>',
                          ParagraphStyle('ph', fontName='Text-Bold', fontSize=11,
                                         leading=15, alignment=1,
                                         textColor=colors.HexColor('#3c4654')))
        table = Table([[label]], colWidths=[width], rowHeights=[height], hAlign='CENTER')
        table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor('#d6dae0')),
            ('BOX', (0, 0), (-1, -1), 1.0, colors.HexColor('#8d97a3')),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ]))
        return table

    def figure(self, rel: str, caption: str, max_w: float, max_h: float,
               keep: bool = True) -> list:
        flow = [self.image(rel, max_w, max_h)]
        if caption:
            flow.append(Paragraph(inline(caption), STYLES['Caption']))
        return [KeepTogether(flow)] if keep else flow

    def landscape_page(self, rel: str, heading: str, caption: str) -> list:
        """One 17 x 11 in drawing page.

        It does not end with a page break: the next flowable decides what follows. Two of
        these in a row give two landscape pages, and a caller that needs portrait text
        afterwards adds `PageBreak()` itself. Emitting a break here as well produced an
        empty page between every pair of drawings.
        """
        return [NextPageTemplate('landscape'), PageBreak(), P(heading, 'H2'),
                self.image(rel, LANDSCAPE_W, LANDSCAPE_H - 74),
                Paragraph(inline(caption), STYLES['Caption']),
                NextPageTemplate('portrait')]


# --------------------------------------------------------------------------- markdown

IMG_RE = re.compile(r'^\s*!\[([^\]]*)\]\(([^)]+)\)\s*$')
CAPTION_START = re.compile(r'^\s*\*(?!\*)\S')
CAPTION_MAX_LINES = 4
LIST_RE = re.compile(r'^(\s*)([-*+]|\d{1,3}\.)\s+(.*)$')
HEAD_STYLE = {1: 'H2', 2: 'H2', 3: 'H3', 4: 'H4', 5: 'H4', 6: 'H4'}


def read_lines(path: Path) -> list[str]:
    if not path.is_file():
        raise FileNotFoundError(path)
    return path.read_text(encoding='utf-8-sig').splitlines()


def sections(path: Path) -> list[tuple[str | None, list[str]]]:
    """Split a Markdown file on its level-2 headings, preamble first."""
    blocks: list[tuple[str | None, list[str]]] = [(None, [])]
    for line in read_lines(path):
        if line.startswith('## '):
            blocks.append((line[3:].strip(), [line]))
        else:
            blocks[-1][1].append(line)
    return blocks


def select(path: Path, keep=None, drop=None) -> list[str]:
    """Return the lines of the level-2 sections whose title passes `keep`/`drop`."""
    out: list[str] = []
    for title, lines in sections(path):
        if title is None:
            if keep is None:
                out.extend(lines)
            continue
        if drop is not None and drop(title):
            continue
        if keep is None or keep(title):
            out.extend(lines)
    return out


def starts_with(*prefixes):
    return lambda title: title.startswith(prefixes)


def render_markdown(lines: list[str], figures: Figures, width: float,
                    source_dir: Path, skip_images: frozenset[str] = frozenset(),
                    image_width: float | None = None) -> list:
    """Convert Markdown lines to flowables, placing figures where the links sit."""
    out: list = []
    buffer: list[str] = []
    img_w = image_width if image_width is not None else width
    index, count = 0, len(lines)

    def flush():
        if buffer:
            out.append(P(' '.join(buffer)))
            buffer.clear()

    while index < count:
        line = lines[index]
        stripped = line.strip()

        if stripped.startswith('```'):
            flush()
            index += 1
            block: list[str] = []
            while index < count and not lines[index].strip().startswith('```'):
                block.append(lines[index])
                index += 1
            index += 1
            out.append(code_block(block, width))
            out.append(Spacer(1, 5))
            continue

        if not stripped:
            flush()
            index += 1
            continue

        match = IMG_RE.match(line)
        if match:
            flush()
            alt, target = match.group(1), match.group(2).split(' ')[0]
            rel = resolve(source_dir, target)
            caption = alt
            index += 1
            probe = index
            while probe < count and not lines[probe].strip():
                probe += 1
            # A caption is the italic line under the link. It may wrap over source lines,
            # so collect until the line that closes the italic run.
            if probe < count and CAPTION_START.match(lines[probe]):
                collected: list[str] = []
                cursor = probe
                while cursor < count and cursor - probe < CAPTION_MAX_LINES:
                    piece = lines[cursor].strip()
                    if not piece:
                        break
                    collected.append(piece)
                    cursor += 1
                    if piece.endswith('*'):
                        break
                joined = ' '.join(collected)
                if joined.startswith('*') and joined.endswith('*') and len(joined) > 2:
                    caption = joined.strip('*').strip()
                    index = cursor
            if Path(rel).name in skip_images:
                out.append(P(f'{caption.rstrip(". ")}. This drawing has a full-size '
                             'landscape page of its own in this manual.', 'Small'))
                continue
            out.extend(figures.figure(rel, caption, img_w, PORTRAIT_H - 150))
            continue

        if stripped.startswith('#'):
            flush()
            hashes = len(stripped) - len(stripped.lstrip('#'))
            out.append(P(stripped.lstrip('#').strip(), HEAD_STYLE.get(hashes, 'H4')))
            index += 1
            continue

        if stripped.startswith('|'):
            flush()
            raw = []
            while index < count and lines[index].strip().startswith('|'):
                raw.append(lines[index])
                index += 1
            out.append(markdown_table(raw, width))
            out.append(Spacer(1, 7))
            continue

        if stripped in ('---', '***', '___', '* * *'):
            flush()
            out.append(Rule())
            index += 1
            continue

        match = LIST_RE.match(line)
        if match:
            flush()
            indent, marker, text = len(match.group(1)), match.group(2), match.group(3)
            index += 1
            while index < count:
                nxt = lines[index]
                if not nxt.strip() or LIST_RE.match(nxt):
                    break
                lead = len(nxt) - len(nxt.lstrip())
                if lead < indent + 2 or nxt.lstrip().startswith(('#', '|', '```', '![')):
                    break
                text += ' ' + nxt.strip()
                index += 1
            level = 0 if indent < 2 else 1 if indent < 6 else 2
            bullet = '\u2022' if marker in ('-', '*', '+') else marker
            out.append(Paragraph(inline(text), STYLES[f'List{level}'],
                                 bulletText=bullet))
            continue

        buffer.append(stripped)
        index += 1

    flush()
    return out


def resolve(source_dir: Path, target: str) -> str:
    """Map a Markdown link target to a repository-relative POSIX path."""
    path = (source_dir / target).resolve()
    try:
        return path.relative_to(ROOT).as_posix()
    except ValueError:
        return target


# --------------------------------------------------------------------------- data

def read_csv(path: Path) -> list[dict]:
    if not path.is_file():
        raise FileNotFoundError(path)
    with path.open(newline='', encoding='utf-8-sig') as handle:
        return list(csv.DictReader(handle))


def read_json(path: Path):
    if not path.is_file():
        raise FileNotFoundError(path)
    return json.loads(path.read_text(encoding='utf-8-sig'))


def number(value, default: float = 0.0) -> float:
    try:
        return float(str(value).strip())
    except (TypeError, ValueError):
        return default


def linked(text: str, url: str) -> str:
    url = (url or '').strip()
    if not url.startswith('http'):
        return text
    return f'{text} [source]({url})'


def human_bytes(size: int) -> str:
    for unit, scale in (('MB', 1 << 20), ('kB', 1 << 10)):
        if size >= scale:
            return f'{size / scale:.1f} {unit}'
    return f'{size} B'


def package_files() -> list[tuple[str, int]]:
    skip_dirs = {'.git', '__pycache__', 'rendered', 'qa', 'node_modules', '.venv', 'tmp'}
    found: list[tuple[str, int]] = []
    for path in sorted(ROOT.rglob('*')):
        if not path.is_file():
            continue
        rel = path.relative_to(ROOT)
        if any(part in skip_dirs for part in rel.parts[:-1]):
            continue
        found.append((rel.as_posix(), path.stat().st_size))
    return found


def svg_to_png(svg: Path, scale: float = 2.0) -> str:
    """Rasterise a circuit sheet so ReportLab can embed it; returns a repo path."""
    SVG_DIR.mkdir(parents=True, exist_ok=True)
    target = SVG_DIR / (svg.stem + '.png')
    document = fitz.open(str(svg))
    try:
        document[0].get_pixmap(matrix=fitz.Matrix(scale, scale), alpha=False).save(str(target))
    finally:
        document.close()
    return target.relative_to(ROOT).as_posix()


# --------------------------------------------------------------------------- document

class Manual(BaseDocTemplate):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.outline: list[tuple[str, int, int]] = []

    def afterFlowable(self, flowable):
        if not isinstance(flowable, Paragraph):
            return
        name = flowable.style.name
        if name not in ('H1', 'H2'):
            return
        level = 0 if name == 'H1' else 1
        text = flowable.getPlainText()
        key = f'sec{len(self.outline)}-{self.page}'
        self.canv.bookmarkPage(key)
        self.canv.addOutlineEntry(text, key.encode('utf-8'), level=level, closed=(level == 0))
        self.outline.append((text, level, self.page))
        self.notify('TOCEntry', (level, text, self.page))


def chrome(canvas, doc):
    width, height = canvas._pagesize
    canvas.saveState()
    canvas.setFont('Text', 7.4)
    canvas.setFillColor(MUTED)
    canvas.setStrokeColor(RULE)
    canvas.setLineWidth(0.5)
    canvas.line(MARGIN_X, height - MARGIN_TOP + 16, width - MARGIN_X, height - MARGIN_TOP + 16)
    canvas.drawString(MARGIN_X, height - MARGIN_TOP + 22, TITLE)
    canvas.drawRightString(width - MARGIN_X, height - MARGIN_TOP + 22,
                           f'{int(width / 72 + 0.5)} x {int(height / 72 + 0.5)} in page'
                           if width > 700 else 'US Letter')
    canvas.line(MARGIN_X, MARGIN_BOTTOM - 14, width - MARGIN_X, MARGIN_BOTTOM - 14)
    canvas.drawString(MARGIN_X, MARGIN_BOTTOM - 26, FOOTER_NOTE)
    canvas.drawRightString(width - MARGIN_X, MARGIN_BOTTOM - 26, str(doc.page))
    canvas.restoreState()


def blank(canvas, doc):
    return None


def frame(width, height):
    return Frame(MARGIN_X, MARGIN_BOTTOM, width, height, id='f',
                 leftPadding=0, rightPadding=0, topPadding=0, bottomPadding=0)


# --------------------------------------------------------------------------- chapters

def cover(figures: Figures, validation: dict, stability: dict, manifest: dict,
          slices: dict) -> list:
    mass_kg = number(stability.get('total_mass_g')) / 1000.0
    printed_kg = number(stability.get('printed_mass_g')) / 1000.0
    stl_count = validation.get('unique_stl_files', len(validation.get('parts', [])))
    pieces = validation.get('printed_piece_count')
    diameter = max(number(p.get('x_mm')) for p in validation['parts'])
    key_rows = [
        ['Body and dome diameter', f'{diameter:.0f} mm (317 mm body ring, H2D 320 mm bed axis less 3 mm)'],
        ['Overall height, three-leg driving stance', '713 mm (dome crown above the floor)'],
        ['Printed design files', f'{stl_count} STL files / {pieces} printed pieces'],
        ['Estimated assembled mass', f'{mass_kg:.2f} kg total, of which {printed_kg:.2f} kg is printed'],
        ['Estimated printing', f'{number(slices.get("total_predicted_time_h")):.0f} h and '
                               f'{number(slices.get("total_predicted_mass_g")) / 1000:.1f} kg of filament '
                               'for the sliced parts'],
        ['Static tip-back margin', f'{number(stability.get("tip_back_margin_mm")):.1f} mm '
                                   f'({number(stability.get("tip_back_angle_deg")):.1f} degrees)'],
        ['Drawing set', f'{len(manifest.get("pngs", []))} MATLAB-style PNG drawings, '
                        f'generated {str(manifest.get("generated", ""))[:10]}'],
    ]
    notice = Table([[Paragraph(
        '<b>Digital design; no physical build or test.</b><br/>Nothing in this package has been '
        'printed, assembled, wired or driven. Every mass, current, runtime, torque and margin in '
        'this manual is arithmetic on CAD geometry and published component ratings. The acceptance '
        'tests in chapter 8 are the first real measurements, not a confirmation of these numbers.',
        ParagraphStyle('notice', fontName='Text', fontSize=9, leading=12.6, textColor=INK))]],
        colWidths=[PORTRAIT_W])
    notice.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor('#fdf3d8')),
        ('BOX', (0, 0), (-1, -1), 0.9, colors.HexColor('#c9a227')),
        ('LEFTPADDING', (0, 0), (-1, -1), 9), ('RIGHTPADDING', (0, 0), (-1, -1), 9),
        ('TOPPADDING', (0, 0), (-1, -1), 8), ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
    ]))
    return [
        Spacer(1, 6),
        P('fable-r2d2', 'CoverTitle'),
        P('R2-D2 fabrication and assembly manual', 'CoverSub'),
        Rule(thickness=1.1, colour=ACCENT),
        figures.image('cad/assembly.png', PORTRAIT_W, 300),
        Spacer(1, 10),
        grid_table(['Key number', 'Value'], key_rows, column_widths(
            [['Key number', 'Value']] + key_rows, PORTRAIT_W, floor=14, ceiling=64)),
        Spacer(1, 12),
        notice,
        Spacer(1, 10),
        P(f'Built {date.today().isoformat()} from the package sources by '
          '`scripts/build_manual.py`. Design repository: JeremyProffittOrg/robots, '
          'directory `fable-r2d2/`.', 'Small'),
    ]


def contents_page(toc: TableOfContents) -> list:
    return [PageBreak(), P('Contents', 'H1x'), toc]


def chapter_overview(figures: Figures, stability: dict, validation: dict) -> list:
    flow = [PageBreak(), P('1  Overview and stance', 'H1')]
    readme = ROOT / 'README.md'
    if readme.is_file():
        lines = read_lines(readme)
        body: list[str] = []
        for line in lines:
            if line.startswith('## ') and body:
                break
            body.append(line)
        flow += render_markdown([l for l in body if not l.startswith('# ')],
                                figures, PORTRAIT_W, ROOT)
    span = stability.get('wheel_contact_y_range_mm', [0, 0])
    stance_rows = [
        ['Centre of gravity, forward of the shoulder axis',
         f'{number(stability["centre_of_gravity_mm"][1]):.1f} mm', 'docs/stability.json'],
        ['Centre of gravity, above the floor',
         f'{number(stability["centre_of_gravity_mm"][2]):.1f} mm', 'docs/stability.json'],
        ['Support polygon, fore and aft',
         f'{number(span[0]):.1f} to {number(span[1]):.1f} mm forward of the shoulder axis',
         'wheel contact patches'],
        ['Tip-back margin (rearward)',
         f'{number(stability["tip_back_margin_mm"]):.1f} mm / '
         f'{number(stability["tip_back_angle_deg"]):.1f} degrees', 'the tightest margin'],
        ['Tip-forward margin',
         f'{number(stability["tip_forward_margin_mm"]):.1f} mm / '
         f'{number(stability["tip_forward_angle_deg"]):.1f} degrees', 'docs/stability.json'],
        ['Sideways tip angle', f'{number(stability["tip_side_angle_deg"]):.1f} degrees',
         'docs/stability.json'],
        ['Centre-foot static load share',
         f'{number(stability["center_foot_static_share"]):.2f} of the total mass '
         '(the rear foot carries more than its geometric share)', 'docs/stability.json'],
        ['Print envelope check',
         'pass' if validation.get('all_pass') else 'FAIL',
         f'cad/validation.json, envelope {validation.get("envelope_mm")} mm'],
    ]
    flow += [
        P('1.1 Stance and stability screening', 'H2'),
        P('These figures come from `docs/stability.json`, which '
          'sums the STL volumes at the modelled fill fraction and treats every purchased item as a '
          'point mass. It is a screening calculation, not a weighing. The tip-back margin is the '
          'number that governs how this robot may be handled: it is small, so never push the dome '
          'rearward and never lift the robot by the dome.'),
        grid_table(['Measure', 'Value', 'Source'], stance_rows,
                   column_widths([['Measure', 'Value', 'Source']] + stance_rows,
                                 PORTRAIT_W, floor=12, ceiling=52)),
        P(f'Method: {stability.get("method", "")}', 'Small'),
    ]
    flow += figures.landscape_page(
        'output/drawings/01_robot_assembled.png',
        'Figure 1 - the assembled robot in its three-leg driving stance',
        'output/drawings/01_robot_assembled.png. Rendered from the nine package STL files with '
        'purchased parts drawn as nominal envelopes. Millimetre axes.')
    flow += figures.landscape_page(
        'output/drawings/02_robot_exploded.png',
        'Figure 2 - the whole robot, separated along its assembly axes',
        'output/drawings/02_robot_exploded.png. The offsets identify the parts; they are not '
        'assembly dimensions.')
    flow += figures.landscape_page(
        'output/drawings/03_robot_orthographic.png',
        'Figure 3 - orthographic views',
        'output/drawings/03_robot_orthographic.png. Front, side, rear and top views with '
        'millimetre axes. Use the mechanical chapter for dimensions, not this drawing.')
    return flow


def chapter_printing(figures: Figures, validation: dict, slices: dict) -> list:
    parts = read_csv(ROOT / 'bom/printed-parts.csv')
    slice_rows = {Path(r.get('part', '')).stem: r for r in slices.get('rows', [])}
    table_rows, total_pieces, total_solid = [], 0, 0.0
    for row in parts:
        name = row['part']
        quantity = int(number(row.get('quantity'), 1))
        total_pieces += quantity
        total_solid += number(row.get('solid_mass_g')) * quantity
        sliced = slice_rows.get(name)
        if sliced and sliced.get('pass'):
            predicted = (f'{number(sliced.get("predicted_mass_g")):.0f} g / '
                         f'{number(sliced.get("predicted_time_h")):.1f} h each')
        elif sliced:
            predicted = 'slice FAILED: ' + str(sliced.get('error_string', ''))[:60]
        else:
            predicted = 'not sliced in this run'
        table_rows.append([
            f'`{name}`', str(quantity), row.get('material', ''),
            f'{number(row.get("x_mm")):.1f} x {number(row.get("y_mm")):.1f} x '
            f'{number(row.get("z_mm")):.1f}',
            f'{number(row.get("solid_mass_g")):.0f}', predicted,
            row.get('orientation', '') + ('; mirror for the second'
                                          if str(row.get('mirror_for_second')).lower() == 'true' else ''),
        ])
    header = ['Part', 'Qty', 'Material', 'X x Y x Z mm', 'Solid g', 'H2D slice prediction',
              'Plate orientation']
    widths = column_widths([header] + table_rows, PORTRAIT_W, floor=5, ceiling=34)
    profiles = slices.get('profiles', {})
    overrides = ', '.join(f'{k} = {v}' for k, v in profiles.get('overrides', {}).items())

    flow = [PageBreak(), P('2  Printing', 'H1'),
            P(f'{validation.get("unique_stl_files")} STL files make '
              f'{total_pieces} printed pieces. Solid-material upper bound for the whole set is '
              f'{total_solid / 1000:.2f} kg before infill savings, supports and brim; the sliced '
              'prediction column is the number to buy filament against. Print the one outer foot '
              'first and assemble stage 1 on it before committing the rest.'),
            P('2.1 Part manifest', 'H2'),
            grid_table(header, table_rows, widths),
            P('Source: bom/printed-parts.csv and cad/h2d-slice-check.json.', 'Small')]

    unsliced = [r['part'] for r in parts if Path(r['part']).stem not in
                {Path(s.get('part', '')).stem for s in slices.get('rows', []) if s.get('pass')}]
    flow += [P('2.2 Slicer profile actually used', 'H2'),
             P(f'Machine: {profiles.get("machine", "unknown")}. Process: '
               f'{profiles.get("process", "unknown")}. Plate: {profiles.get("bed", "unknown")}.'),
             P(f'Overrides: {overrides}.' if overrides else 'No profile overrides recorded.'),
             P(f'Check run: {slices.get("test_type", "")} on '
               f'{str(slices.get("checked_at_utc", ""))[:19]} UTC. Totals for the parts that '
               f'sliced: {number(slices.get("total_predicted_mass_g")):.0f} g of filament and '
               f'{number(slices.get("total_predicted_time_h")):.1f} printer hours.')]
    if unsliced:
        flow.append(P('**Not confirmed by the slicer in that run:** ' +
                      ', '.join(f'`{u}`' for u in unsliced) +
                      '. Slice these yourself before buying filament, and treat their times and '
                      'masses in the manifest as estimates from mesh volume only.'))

    mech = ROOT / 'docs/mechanical.md'
    flow += [PageBreak(), P('2.3 Orientation and support notes', 'H2'),
             P('Reproduced from docs/mechanical.md section 2.', 'Small')]
    flow += render_markdown(select(mech, keep=starts_with('2.')), figures, PORTRAIT_W, mech.parent)

    flow += figures.landscape_page(
        'output/drawings/04_printed_components.png',
        'Figure 4 - every printed component in the package',
        'output/drawings/04_printed_components.png. One tile per STL file, at a common scale.')

    flow += [PageBreak(), P('2.4 Component sheets', 'H2'),
             P('One page per STL file: the part as it is modelled, with the numbers the slicer '
               'and the assembly stages need.')]
    # The part list comes from the BOM, never from a directory listing: globbing the
    # drawings folder would drop a part whose sheet is missing instead of failing on it.
    by_name = {r['part']: r for r in parts}
    names = [r['part'] for r in parts]
    for position, name in enumerate(names):
        row = by_name[name]
        sliced = slice_rows.get(name)
        detail = [
            ['Quantity', row.get('quantity', ''), 'Material', row.get('material', '')],
            ['Envelope mm', f'{number(row.get("x_mm")):.2f} x {number(row.get("y_mm")):.2f} x '
                            f'{number(row.get("z_mm")):.2f}',
             'Solid mass', f'{number(row.get("solid_mass_g")):.1f} g'],
            ['Mesh volume', f'{number(row.get("volume_cm3")):.1f} cm3',
             'Triangles', row.get('faces', '')],
            ['Watertight', row.get('watertight', ''), 'Solids', row.get('connected_solids', '')],
            ['Plate orientation', row.get('orientation', ''),
             'Mirror for the pair', row.get('mirror_for_second', '')],
            ['Sliced mass', f'{number(sliced.get("predicted_mass_g")):.1f} g'
             if sliced and sliced.get('pass') else 'not sliced',
             'Sliced time', f'{number(sliced.get("predicted_time_h")):.2f} h'
             if sliced and sliced.get('pass') else 'not sliced'],
        ]
        flow += ([PageBreak()] if position else []) + \
                [P(f'{name}', 'H3'),
                 figures.image(f'output/drawings/components/{name}.png', PORTRAIT_W, 360),
                 Paragraph(inline(f'output/drawings/components/{name}.png - '
                                  f'{row.get("notes", "")}'), STYLES['Caption']),
                 grid_table(['Field', 'Value', 'Field', 'Value'], detail,
                            [PORTRAIT_W * f for f in (0.19, 0.31, 0.19, 0.31)])]
    return flow


def bom_chapter(figures: Figures) -> list:
    flow = [PageBreak(), P('3  Purchased parts', 'H1'),
            P('Every item that is not printed. Prices were researched on 2026-09-12 and are '
              'listed per item or per stated pack; they are not quotations. Nothing has been '
              'ordered. Check availability and the exact rating notes before buying, because a '
              'substitute with a different envelope will not fit the printed pockets.')]
    grand = 0.0
    for filename, title, blurb in [
        ('electronics.csv', '3.1 Electronics, motors and power',
         'Reference designators match the four circuit sheets in chapter 5 and '
         'electronics/wiring.csv.'),
        ('hardware.csv', '3.2 Mechanical hardware, bearings and fasteners',
         'Steel carries every load path that matters: the shoulder bolts, the threaded rods, '
         'the caster bearings and the lazy susan.'),
    ]:
        rows_in = read_csv(ROOT / 'bom' / filename)
        rows, subtotal = [], 0.0
        for row in rows_in:
            quantity = number(row.get('quantity'), 1.0)
            unit = number(row.get('unit_usd'))
            line_total = quantity * unit
            subtotal += line_total
            origin = ' - '.join(part for part in (str(row.get('part_number', '')).strip(),
                                                  str(row.get('supplier', '')).strip()) if part)
            rows.append([
                row.get('reference', ''),
                f'{quantity:g}',
                str(row.get('item', '')) + ('\n*' + origin.replace('*', '') + '*' if origin else ''),
                f'{unit:,.2f}',
                f'{line_total:,.2f}',
                linked(str(row.get('notes', '')), row.get('url', '')),
            ])
        grand += subtotal
        header = ['Ref', 'Qty', 'Item, part number and supplier', 'Unit USD', 'Line USD',
                  'Fit, rating and source']
        rows.append(['', '', f'**Subtotal, {len(rows_in)} line items**', '',
                     f'**{subtotal:,.2f}**', ''])
        flow += [PageBreak() if filename.startswith('hardware') else Spacer(1, 2),
                 P(title, 'H2'), P(blurb),
                 grid_table(header, rows,
                            [PORTRAIT_W * f for f in (0.055, 0.045, 0.315, 0.075, 0.075, 0.435)]),
                 P(f'Source: bom/{filename}. Subtotal USD {subtotal:,.2f}, quantity times unit '
                   'price, tax, shipping, tools and filament excluded.', 'Small')]
    flow += [P('3.3 Purchased-parts total', 'H2'),
             P(f'**USD {grand:,.2f}** for both lists together, computed from the CSV files at '
               'build time. Filament, tools, the printer, paint, tax and shipping are not in that '
               'number. The consumables table in chapter 6 lists what else you must have on hand.')]
    return flow


def chapter_mechanical(figures: Figures) -> list:
    mech = ROOT / 'docs/mechanical.md'
    flow = [PageBreak(), P('4  Mechanical design', 'H1'),
            P('The design envelope and stance, every load-carrying joint, the fits that make the '
              'printed parts go together, and the load screening. Reproduced from '
              'docs/mechanical.md sections 1, 3, 4 and 5.', 'Small')]
    flow += render_markdown(select(mech, keep=starts_with('1.')), figures, PORTRAIT_W, mech.parent)
    for rel, heading, caption in [
        ('cad/section.png', 'Section through the assembly',
         'cad/section.png - the native OpenSCAD model cut on the centre plane. Battery bay, '
         'electronics deck, ring seam and the dome bearing seat.'),
        ('cad/exploded.png', 'Assembly order',
         'cad/exploded.png - the offsets identify the parts and are not assembly dimensions.'),
        ('cad/rear.png', 'Rear access',
         'cad/rear.png - keep the charge port, the switch and the service fasteners reachable '
         'with the robot standing.'),
    ]:
        flow.append(KeepTogether([P(heading, 'H3'),
                                  figures.image(rel, PORTRAIT_W, 400),
                                  Paragraph(inline(caption), STYLES['Caption'])]))
    for section, drawings in [
        ('3.', [('05_body_rings', 'Figure 5 - the two body rings',
                 'Ring seam, shoulder bosses, integral electronics deck and the lazy-susan seat.'),
                ('06_dome', 'Figure 6 - the dome',
                 'One-piece dome with the display, holoprojector and PSI cut-outs.'),
                ('07_legs', 'Figure 7 - the legs',
                 'Outer leg upper and lower, the comb splice and the centre leg.'),
                ('08_feet', 'Figure 8 - the feet',
                 'Outer foot and centre foot with the motor pockets and wheel positions.'),
                ('09_head_drive', 'Figure 9 - the head friction drive',
                 'Pivoting motor mount, tension screw and lift stop.')]),
        ('4.', []), ('5.', []),
    ]:
        flow += [PageBreak()]
        flow += render_markdown(select(mech, keep=starts_with(section)), figures,
                                PORTRAIT_W, mech.parent)
        for stem, heading, caption in drawings:
            flow += figures.landscape_page(
                f'output/drawings/{stem}.png', heading,
                f'output/drawings/{stem}.png. {caption} Millimetre axes; purchased parts are '
                'nominal envelopes, not manufacturer CAD.')
    return flow


def chapter_electrical(figures: Figures) -> list:
    doc = ROOT / 'docs/electrical.md'
    flow = [PageBreak(), P('5  Electrical', 'H1')]
    flow += render_markdown(read_lines(doc), figures, PORTRAIT_W, doc.parent)
    sheets = sorted((ROOT / 'electronics').glob('*.svg'))
    if not sheets:
        raise RuntimeError('No circuit sheets found in electronics/')
    for sheet in sheets:
        rel = svg_to_png(sheet)
        title = sheet.stem.split('-', 1)[-1].replace('-', ' ')
        flow += figures.landscape_page(
            rel, f'Circuit sheet {sheet.stem.split("-")[0]} - {title}',
            f'electronics/{sheet.name}. Named nets join across all four sheets; the wire-by-wire '
            'list is electronics/wiring.csv. Nothing here has been built or measured.')
    wiring = ROOT / 'electronics/wiring.csv'
    if wiring.is_file():
        rows = read_csv(wiring)
        header = list(rows[0].keys())
        data = [[str(r.get(k, '')) for k in header] for r in rows]
        flow += [PageBreak(), P('5.1 Point-to-point wiring schedule', 'H2'),
                 P(f'One row is one connection; {len(rows)} in total. Identical net names join '
                   'across the four sheets.'),
                 grid_table([h.replace('_', ' ') for h in header], data,
                            column_widths([header] + data, PORTRAIT_W, floor=5, ceiling=30)),
                 P('Source: electronics/wiring.csv.', 'Small')]
    return flow


def chapter_assembly(figures: Figures) -> list:
    doc = ROOT / 'docs/assembly.md'
    lines = select(doc, drop=lambda t: t.startswith('Stage 11'))
    flow = [PageBreak(), P('6  Assembly', 'H1')]
    flow += render_markdown(lines, figures, PORTRAIT_W, doc.parent,
                            skip_images=frozenset({'16_exploded_robot.png'}))
    flow += figures.landscape_page(
        'output/drawings/16_exploded_robot.png',
        'Figure 16 - the whole robot exploded',
        'output/drawings/16_exploded_robot.png. Dome, two body rings, head drive, two outer legs, '
        'the centre leg and the three feet, separated along the assembly axes.')
    return flow


def chapter_firmware(figures: Figures) -> list:
    doc = ROOT / 'docs/firmware.md'
    flow = [PageBreak(), P('7  Firmware and first power-on', 'H1'),
            P('Reproduced from docs/firmware.md sections 1, 2 and 3 (what runs where, the serial '
              'protocol and the drive mixing) and sections 5 and 6 (flashing the KB2040 and '
              'setting up the Raspberry Pi).', 'Small')]
    flow += render_markdown(select(doc, keep=starts_with('1.', '2.', '3.')), figures,
                            PORTRAIT_W, doc.parent)
    flow += [PageBreak()]
    flow += render_markdown(select(doc, keep=starts_with('5.', '6.', '7.')), figures,
                            PORTRAIT_W, doc.parent)
    return flow


def chapter_tests(figures: Figures) -> list:
    assembly = ROOT / 'docs/assembly.md'
    flow = [PageBreak(), P('8  Tests and acceptance', 'H1'),
            P('These are the first physical measurements made on the robot. Every number '
              'elsewhere in this manual is a calculation waiting to be checked here. Do not skip '
              'a test because the calculation looked comfortable, and do not carry the robot by '
              'the dome before the tilt test has been done.')]
    flow += render_markdown(select(assembly, keep=starts_with('Stage 11')), figures,
                            PORTRAIT_W, assembly.parent,
                            skip_images=frozenset({'16_exploded_robot.png'}))
    loads = ROOT / 'research/loads.md'
    if loads.is_file():
        flow += [PageBreak(), P('8.1 Ranked risks and the test that retires each', 'H2'),
                 P('Reproduced from research/loads.md section 8.', 'Small')]
        flow += render_markdown(select(loads, keep=starts_with('8.')), figures,
                                PORTRAIT_W, loads.parent)
    else:
        mech = ROOT / 'docs/mechanical.md'
        flow += [PageBreak(), P('8.1 Ranked risks', 'H2'),
                 P('research/loads.md is not in this package; the ranked risks below come from '
                   'docs/mechanical.md section 5 instead.', 'Small')]
        flow += render_markdown(select(mech, keep=starts_with('5.')), figures,
                                PORTRAIT_W, mech.parent)
    return flow


def chapter_verification(figures: Figures, validation: dict, stability: dict,
                         slices: dict) -> list:
    flow = [PageBreak(), P('9  Verification record', 'H1'),
            P('What was actually checked by a program, and what was not. Every row below was '
              'produced by a script in scripts/ or electronics/ and written to a file in this '
              'package. No row is a physical measurement.')]

    verification = ROOT / 'docs/verification.json'
    if verification.is_file():
        record = read_json(verification)
        rows = [[c.get('check', ''), 'pass' if c.get('pass') else 'FAIL', c.get('detail', '')]
                for c in record.get('checks', [])]
        flow += [P('9.1 Package checks', 'H2'),
                 grid_table(['Check', 'Result', 'Detail'], rows,
                            [PORTRAIT_W * f for f in (0.16, 0.1, 0.74)]),
                 P(f'docs/verification.json: all_pass = {record.get("all_pass")}, '
                   f'physical_validation = {record.get("physical_validation")}.', 'Small')]

    parts = validation.get('parts', [])
    mesh_rows = [[f'`{p.get("part")}`', str(p.get('quantity')),
                  'yes' if p.get('watertight') else 'NO',
                  'yes' if p.get('winding_consistent') else 'NO',
                  str(p.get('connected_solids')),
                  'yes' if p.get('fits_envelope') else 'NO',
                  'pass' if p.get('pass_check') else 'FAIL'] for p in parts]
    flow += [P('9.2 CAD and mesh validation', 'H2'),
             P(f'cad/validation.json: {validation.get("unique_stl_files")} unique STL files, '
               f'{validation.get("printed_piece_count")} printed pieces, print envelope '
               f'{validation.get("envelope_mm")} mm, solid-material upper bound '
               f'{number(validation.get("solid_material_upper_bound_g")) / 1000:.2f} kg. '
               f'all_pass = {validation.get("all_pass")}. '
               f'physical_fit_verified = {validation.get("physical_fit_verified")}; '
               f'physical_strength_verified = {validation.get("physical_strength_verified")}.'),
             grid_table(['Part', 'Qty', 'Watertight', 'Winding', 'Solids', 'Fits plate', 'Result'],
                        mesh_rows, [PORTRAIT_W * f for f in
                                    (0.26, 0.08, 0.14, 0.13, 0.11, 0.14, 0.14)])]

    interference = ROOT / 'cad/interference-final.txt'
    if interference.is_file():
        text = interference.read_text(encoding='utf-8-sig').strip().splitlines()
        rows = []
        for line in text:
            name = line.split()[0] if line.split() else ''
            volume = re.search(r'volume=([0-9.]+)', line)
            if volume:
                litres = float(volume.group(1))
                verdict = 'clear' if litres <= 0.0 else f'INTERFERENCE {litres:.3f} mm3'
            else:
                verdict = 'no solid produced; check not evaluated'
            rows.append([f'`{name}`', verdict, line])
        flow += [P('9.3 Interference checks', 'H2'),
                 P('Each row is a boolean intersection between two mating parts in the assembled '
                   'model. An empty result means the two bodies do not overlap. A check that '
                   'produced no solid at all was not evaluated and is not evidence of clearance.'),
                 grid_table(['Check', 'Verdict', 'Raw output'], rows,
                            [PORTRAIT_W * f for f in (0.2, 0.24, 0.56)]),
                 P('Source: cad/interference-final.txt.', 'Small')]

    items = stability.get('items', [])
    mass_rows = [[i.get('name', ''), i.get('kind', ''), f'{number(i.get("mass_g")):.1f}',
                  ', '.join(f'{number(v):.1f}' for v in i.get('centre_mm', []))]
                 for i in items]
    mass_rows.append(['**Total**', '', f'**{number(stability.get("total_mass_g")):.1f}**',
                      ', '.join(f'{number(v):.1f}' for v in
                                stability.get('centre_of_gravity_mm', []))])
    flow += [PageBreak(), P('9.4 Mass and stability screening', 'H2'),
             P(f'docs/stability.json. Printed mass {number(stability.get("printed_mass_g")):.0f} g '
               f'at fill fraction {stability.get("fill_fraction")}, purchased mass '
               f'{number(stability.get("purchased_mass_g")):.0f} g, total '
               f'{number(stability.get("total_mass_g")) / 1000:.2f} kg. Centres are millimetres in '
               'the model frame (X across, Y forward of the shoulder axis, Z above the floor).'),
             grid_table(['Item', 'Kind', 'Mass g', 'Centre X, Y, Z mm'], mass_rows,
                        [PORTRAIT_W * f for f in (0.36, 0.14, 0.16, 0.34)])]

    slice_rows = [[f'`{Path(r.get("part", "")).stem}`',
                   'pass' if r.get('pass') else 'FAIL',
                   f'{number(r.get("predicted_mass_g")):.1f}' if r.get('pass') else '-',
                   f'{number(r.get("predicted_time_h")):.2f}' if r.get('pass') else '-',
                   str(r.get('error_string', ''))[:70]] for r in slices.get('rows', [])]
    flow += [P('9.5 Slicer check', 'H2'),
             P(f'cad/h2d-slice-check.json, all_pass = {slices.get("all_pass")}. '
               f'{slices.get("test_type", "")}. A FAIL row means the slicer would not produce '
               'G-code for that mesh in this run; slice it yourself before printing.'),
             grid_table(['Part', 'Result', 'Filament g', 'Hours', 'Slicer message'], slice_rows,
                        [PORTRAIT_W * f for f in (0.2, 0.1, 0.13, 0.1, 0.47)]),
             P('9.6 What is not verified', 'H2'),
             P('No part has been printed. No assembly has been made. No motor has been run, no '
               'current measured, no temperature taken, no distance driven and no mass weighed. '
               'Fit between mating printed parts is checked only as CAD geometry at nominal '
               'dimensions, with no allowance for printer tolerance, warp or shrinkage. Strength, '
               'traction, runtime, stopping distance and dome-drive slip are calculations against '
               'published ratings. Chapter 8 is where those become measurements.')]
    return flow


def appendix(figures: Figures) -> list:
    files = package_files()
    by_dir: dict[str, list[tuple[str, int]]] = {}
    for rel, size in files:
        parent = str(Path(rel).parent).replace('\\', '/')
        by_dir.setdefault('.' if parent == '.' else parent, []).append((Path(rel).name, size))
    total = sum(size for _, size in files)
    flow = [PageBreak(), P('Appendix A  Package file list', 'H1'),
            P(f'{len(files)} files, {human_bytes(total)} in total, as built on '
              f'{date.today().isoformat()}. Generated caches, the git database and the '
              'page-render directory used by the manual build are excluded.')]
    for folder in sorted(by_dir):
        entries = sorted(by_dir[folder])
        rows = []
        for index in range(0, len(entries), 2):
            pair = entries[index:index + 2]
            row = []
            for name, size in pair:
                row += [f'`{name}`', human_bytes(size)]
            while len(row) < 4:
                row.append('')
            rows.append(row)
        flow += [P(f'{folder}/  -  {len(entries)} files', 'H3'),
                 grid_table(['File', 'Size', 'File', 'Size'], rows,
                            [PORTRAIT_W * f for f in (0.32, 0.18, 0.32, 0.18)]),
                 Spacer(1, 4)]
    return flow


# --------------------------------------------------------------------------- build

def build_story(figures: Figures, toc: TableOfContents) -> list:
    validation = read_json(ROOT / 'cad/validation.json')
    stability = read_json(ROOT / 'docs/stability.json')
    slices = read_json(ROOT / 'cad/h2d-slice-check.json')
    manifest_path = ROOT / 'output/drawings/drawing-manifest.json'
    manifest = read_json(manifest_path) if manifest_path.is_file() else {}

    story = [NextPageTemplate('portrait')]
    story += cover(figures, validation, stability, manifest, slices)
    story += contents_page(toc)
    story += chapter_overview(figures, stability, validation)
    story += chapter_printing(figures, validation, slices)
    story += bom_chapter(figures)
    story += chapter_mechanical(figures)
    story += chapter_electrical(figures)
    story += chapter_assembly(figures)
    story += chapter_firmware(figures)
    story += chapter_tests(figures)
    story += chapter_verification(figures, validation, stability, slices)
    story += appendix(figures)
    return story


def render_pages(pdf: fitz.Document) -> tuple[int, list[str]]:
    for old in RENDER_DIR.glob('page-*.png'):
        old.unlink()
    zoom = RENDER_DPI / 72.0
    errors: list[str] = []
    rendered = 0
    for index, page in enumerate(pdf, 1):
        try:
            pixmap = page.get_pixmap(matrix=fitz.Matrix(zoom, zoom), alpha=False)
            pixmap.save(str(RENDER_DIR / f'page-{index:03d}.png'))
            rendered += 1
        except Exception as error:                      # noqa: BLE001 - reported, not hidden
            errors.append(f'page {index}: {error!r}')
    return rendered, errors


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--allow-missing-figures', action='store_true',
                        help='substitute a grey placeholder for a missing drawing and force '
                             'all_pass false (development only)')
    args = parser.parse_args()

    register_fonts()
    build_styles()
    OUT.parent.mkdir(parents=True, exist_ok=True)
    RENDER_DIR.mkdir(parents=True, exist_ok=True)

    figures = Figures(args.allow_missing_figures)
    toc = TableOfContents()
    toc.levelStyles = [STYLES['TOC0'], STYLES['TOC1']]
    toc.dotsMinLevel = 0

    story = build_story(figures, toc)

    if figures.missing and not args.allow_missing_figures:
        print('FAIL: referenced figures are missing from the package:', file=sys.stderr)
        for rel in sorted(figures.missing):
            print(f'  {rel}', file=sys.stderr)
        print(f'{len(figures.missing)} missing figure(s). Render the drawing set, or rerun with '
              '--allow-missing-figures for a development build.', file=sys.stderr)
        return 2

    doc = Manual(str(OUT), pagesize=PORTRAIT, leftMargin=MARGIN_X, rightMargin=MARGIN_X,
                 topMargin=MARGIN_TOP, bottomMargin=MARGIN_BOTTOM, title=TITLE,
                 author='fable-r2d2 design package', subject=FOOTER_NOTE)
    doc.addPageTemplates([
        PageTemplate(id='cover', pagesize=PORTRAIT,
                     frames=[frame(PORTRAIT_W, PORTRAIT_H)], onPage=blank),
        PageTemplate(id='portrait', pagesize=PORTRAIT,
                     frames=[frame(PORTRAIT_W, PORTRAIT_H)], onPage=chrome),
        PageTemplate(id='landscape', pagesize=LANDSCAPE,
                     frames=[frame(LANDSCAPE_W, LANDSCAPE_H)], onPage=chrome),
    ])
    doc.multiBuild(story)

    pdf = fitz.open(str(OUT))
    pages = len(pdf)
    text = '\n'.join(page.get_text() for page in pdf)
    flat = re.sub(r'\s+', ' ', text)
    text_checks = {needle: (needle in flat) for needle in REQUIRED_TEXT}
    blank_pages = [i + 1 for i, page in enumerate(pdf) if not page.get_text().strip()]
    rendered, render_errors = render_pages(pdf)
    pdf.close()

    digest = hashlib.sha256(OUT.read_bytes()).hexdigest()
    all_pass = bool(
        not args.allow_missing_figures          # a development build never claims a pass
        and not figures.missing
        and not render_errors
        and rendered == pages
        and pages >= MIN_PAGES
        and all(text_checks.values())
        and not blank_pages
    )
    report = {
        'pages': pages,
        'sha256': digest,
        'all_pass': all_pass,
        'figures_embedded': sorted(figures.embedded),
        'missing_figures': sorted(figures.missing),
        'text_checks': text_checks,
        'bytes': OUT.stat().st_size,
        'text_characters': len(text),
        'pages_rendered': rendered,
        'render_dpi': RENDER_DPI,
        'render_errors': render_errors,
        'blank_pages': blank_pages,
        'min_pages_required': MIN_PAGES,
        'development_build': bool(args.allow_missing_figures),
        'built': date.today().isoformat(),
    }
    CHECK_JSON.write_text(json.dumps(report, indent=2) + '\n', encoding='utf-8')

    print(f'{"PASS" if all_pass else "FAIL"}: {pages} pages, {OUT.stat().st_size:,} bytes, '
          f'{len(figures.embedded)} figures embedded, {len(figures.missing)} missing, '
          f'{rendered}/{pages} pages rendered at {RENDER_DPI} dpi')
    print(f'text checks: ' + ', '.join(f'{k}={"ok" if v else "MISSING"}'
                                       for k, v in text_checks.items()))
    if blank_pages:
        print(f'blank pages: {blank_pages}')
    if render_errors:
        print('render errors: ' + '; '.join(render_errors))
    print(f'{OUT}')
    print(f'sha256 {digest}')
    return 0 if all_pass else 1


if __name__ == '__main__':
    sys.exit(main())
