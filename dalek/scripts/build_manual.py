"""Build the self-contained fabrication manual from the checked-in design files."""
from pathlib import Path
import csv
import html
import re

import fitz
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import (BaseDocTemplate, PageTemplate, Frame, Paragraph,
                               Spacer, PageBreak, NextPageTemplate, Image)

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'output/pdf/dalek-design-and-assembly.pdf'
DRAWING_PAGE = (17*inch, 11*inch)
FONT_DIR = Path('C:/Windows/Fonts')
for name, filename in [('Text', 'arial.ttf'), ('Text-Bold', 'arialbd.ttf'),
                       ('Text-Italic', 'ariali.ttf'), ('Mono', 'consola.ttf')]:
    pdfmetrics.registerFont(TTFont(name, str(FONT_DIR / filename)))
pdfmetrics.registerFontFamily('Text', normal='Text', bold='Text-Bold', italic='Text-Italic', boldItalic='Text-Bold')
styles = getSampleStyleSheet()
styles.add(ParagraphStyle('Body', fontName='Text', fontSize=10, leading=14,
                         textColor=colors.HexColor('#19212b'), spaceAfter=7,
                         splitLongWords=True))
styles.add(ParagraphStyle('Chapter', parent=styles['Body'], fontName='Text-Bold',
                         fontSize=21, leading=25, spaceAfter=15, keepWithNext=True))
styles.add(ParagraphStyle('Section', parent=styles['Body'], fontName='Text-Bold',
                         fontSize=13, leading=17, spaceBefore=12, spaceAfter=7, keepWithNext=True))
styles.add(ParagraphStyle('Minor', parent=styles['Section'], fontSize=11, leading=15))
styles.add(ParagraphStyle('CodeBlock', fontName='Mono', fontSize=8, leading=11,
                         spaceAfter=8, backColor=colors.HexColor('#f0f2f4'),
                         borderPadding=6, splitLongWords=True))
styles.add(ParagraphStyle('Small', parent=styles['Body'], fontSize=8, leading=11, spaceAfter=4))
styles.add(ParagraphStyle('ListItem', parent=styles['Body'], leftIndent=12, firstLineIndent=-9))


def clean(text):
    return text.replace('\u2011', '-').replace('\u2013', '-').replace('\u2014', ' - ').replace('\u00a0', ' ')


def inline(text):
    text = html.escape(clean(text))
    text = re.sub(r'`([^`]+)`', r'<font name="Mono">\1</font>', text)
    text = re.sub(r'\*\*([^*]+)\*\*', r'<b>\1</b>', text)
    text = re.sub(r'\[([^\]]+)\]\((https?://[^)]+)\)', r'<link href="\2" color="#184c7a">\1</link>', text)
    text = re.sub(r'\[([^\]]+)\]\(([^)]+)\)', r'\1 (\2)', text)
    return text


def para(text, style='Body'):
    return Paragraph(inline(text), styles[style])


class Manual(BaseDocTemplate):
    def afterFlowable(self, flowable):
        if isinstance(flowable, Paragraph) and flowable.style.name in ('Chapter', 'Section'):
            title = flowable.getPlainText()
            key = f'entry-{self.page}-{len(getattr(self, "outline_entries", []))}'
            self.canv.bookmarkPage(key)
            level = 0 if flowable.style.name == 'Chapter' else 1
            self.canv.addOutlineEntry(title, key, level=level, closed=(level == 0))
            if not hasattr(self, 'outline_entries'):
                self.outline_entries = []
            self.outline_entries.append((title, self.page))


def page_footer(canvas, doc):
    width, height = canvas._pagesize
    canvas.setStrokeColor(colors.HexColor('#ccd0d4'))
    canvas.line(42, 35, width-42, 35)
    canvas.setFont('Text', 8)
    canvas.setFillColor(colors.HexColor('#4b5563'))
    canvas.drawString(42, 22, 'Dalek fabrication design | Prototype: physical commissioning required')
    canvas.drawRightString(width-42, 22, str(doc.page))


def markdown(path):
    lines = path.read_text(encoding='utf-8-sig').splitlines()
    flow, paragraph, code = [], [], None
    def flush():
        if paragraph:
            flow.append(para(' '.join(paragraph)))
            paragraph.clear()
    for line in lines:
        if line.lstrip().startswith('```'):
            flush()
            if code is None:
                code = []
            else:
                for code_line in code:
                    flow.append(Paragraph(html.escape(clean(code_line)).replace(' ', '&nbsp;') or ' ', styles['CodeBlock']))
                code = None
            continue
        if code is not None:
            code.append(line)
        elif not line.strip():
            flush()
        elif line.startswith('#'):
            flush()
            count = len(line) - len(line.lstrip('#'))
            flow.append(para(line.lstrip('# ').strip(), 'Chapter' if count == 1 else 'Section' if count == 2 else 'Minor'))
        elif re.match(r'^\s*[-*]\s+', line):
            flush()
            flow.append(para('• ' + re.sub(r'^\s*[-*]\s+', '', line), 'ListItem'))
        elif re.match(r'^\d+\.\s+', line):
            flush()
            flow.append(para(line, 'ListItem'))
        elif line.startswith('|'):
            flush()
            if not re.match(r'^\|[\s|:\-]+$', line):
                flow.append(para(' | '.join(cell.strip() for cell in line.strip('|').split('|')), 'Small'))
        elif line.startswith('!['):
            flush() # The figures are placed at full legible size in their own appendix.
        elif line.strip() not in ('---', '***'):
            paragraph.append(line)
    flush()
    if code is not None:
        raise ValueError('Unclosed code block: ' + str(path))
    return flow


def csv_section(path, title):
    with path.open(newline='', encoding='utf-8-sig') as source:
        reader = csv.DictReader(source)
        rows = list(reader)
        columns = reader.fieldnames
    flow = [para(title, 'Chapter'), para(str(path.relative_to(ROOT)), 'Small')]
    for index, row in enumerate(rows, 1):
        cells = [f'<b>{html.escape(key.replace("_", " "))}:</b> {inline(str(row.get(key, "")))}'
                 for key in columns if str(row.get(key, '')).strip()]
        flow.append(Paragraph(f'<b>{index}.</b> ' + ' &nbsp; | &nbsp; '.join(cells), styles['Small']))
        flow.append(Spacer(1, 4))
    return flow


def main():
    OUT.parent.mkdir(parents=True, exist_ok=True)
    docs = [ROOT / 'docs' / name for name in ['assembly.md', 'mechanical.md', 'firmware.md',
                                            'electronics-research.md', 'research.md']]
    for path in docs:
        if not path.is_file():
            raise FileNotFoundError(path)
    diagrams = sorted((ROOT / 'electronics').glob('*.svg'))
    if not diagrams:
        raise RuntimeError('No circuit diagrams found.')
    preview = ROOT / 'cad/assembly.png'
    if not preview.is_file():
        candidates = sorted((ROOT / 'cad').rglob('*assembly*.png'))
        if not candidates:
            candidates = sorted((ROOT / 'docs').rglob('*assembly*.png'))
        if not candidates:
            raise RuntimeError('No assembly preview found.')
        preview = candidates[0]
    doc = Manual(str(OUT), pagesize=letter, leftMargin=46, rightMargin=46,
                 topMargin=42, bottomMargin=48, title='Dalek stacked-body design and assembly',
                 author='')
    doc.addPageTemplates([
        PageTemplate(id='portrait', frames=[Frame(46,48,letter[0]-92,letter[1]-90,id='p')],
                     onPage=page_footer, pagesize=letter),
        PageTemplate(id='landscape', frames=[Frame(40,48,DRAWING_PAGE[0]-80,
                                                 DRAWING_PAGE[1]-88,id='l')],
                     onPage=page_footer, pagesize=DRAWING_PAGE)])
    story = [para('Dalek stacked-body design and assembly', 'Chapter'),
             para('Ten STL designs form a reinforced single-piece motor base, complete body sections that stack '
                  'vertically, and the moving arm parts. The base fits the Bambu Lab H2D in one print.'),
             para('The robot keeps four TT drive motors, a rear ESP32 display, Wi-Fi access point and network controls, '
                  'circular arm motion, a continuously rotating head and 24 original MP3 voices. '
                  'The package includes editable CAD, circuits, mounting hardware lists and assembly instructions.'),
             para('This is a digitally checked design for a first prototype. Physical fit, loaded traction, '
                  'supply temperature and stopping behavior require the tests in this manual. Do not skip those gates.'),
             Spacer(1, 10)]
    pic = Image(str(preview))
    pic._restrictSize(6.8*inch, 5.5*inch)
    story += [pic, para('CAD assembly view. Purchased parts and internal features may be simplified in the preview.', 'Small'),
              PageBreak(), para('Using this package', 'Chapter'),
              para('Read the assembly sequence first, then use the exact part-specific mechanical instructions. '
                   'Read the firmware procedure before wiring or flashing. The electrical research chapter explains '
                   'the power and pin choices. Full-size circuit sheets and complete bills of materials follow the text.'),
              para('The source package is in JeremyProffittOrg/robots on main under dalek/. '
                   'Each drawing and source filename in this PDF is relative to that directory. '
                   'Original files and firmware: https://github.com/JeremyProffittOrg/robots/tree/main/dalek .'),
              para('Use the PDF bookmarks to jump between chapters. The final appendix lists parts and wires. '
                   'The supplied digital verification record reports what was actually checked and what remains unverified.'),
              PageBreak()]
    for index, path in enumerate(docs):
        if index:
            story.append(PageBreak())
        story.extend(markdown(path))
        if path.name == 'mechanical.md':
            for filename, title, caption in [
                ('base.png', 'Single-piece reinforced motor base', 'The floor, perimeter walls, ribs, motor pockets and battery support form one connected print. The base measures 300 x 280 mm before its brim.'),
                ('section.png', 'Internal assembly view', 'Section through the native CAD. The continuous base supports the motor pockets, battery and vertically stacked body.'),
                ('exploded.png', 'Vertical stacking order', 'Each body tier is one complete print. Registers align the stack; accessible fasteners retain the joints. The gaps in this view are intentional.'),
                ('rear.png', 'Rear display and access', 'The TTGO display faces outward. Keep the USB opening, operator switches and service fasteners accessible.')]:
                path_image = ROOT / 'cad' / filename
                if not path_image.exists():
                    raise FileNotFoundError(path_image)
                story += [PageBreak(), para(title, 'Section')]
                drawing = Image(str(path_image))
                drawing._restrictSize(6.95*inch, 8.1*inch)
                story += [drawing, para(caption, 'Small')]
    story += [PageBreak()] + markdown(ROOT / 'audio/README.md')
    verification = ROOT / 'docs/verification.md'
    if verification.exists():
        story += [PageBreak()] + markdown(verification)
    for filename, title in [('electronics.csv','Electrical bill of materials'),
                            ('hardware.csv','Mechanical hardware bill of materials'),
                            ('printed-parts.csv','Printed part quantities and orientations')]:
        path = ROOT / 'bom' / filename
        if not path.exists():
            raise FileNotFoundError(path)
        story += [PageBreak()] + csv_section(path,title)
    wiring = ROOT / 'electronics/wiring.csv'
    if wiring.exists():
        story += [PageBreak()] + csv_section(wiring,'Point-to-point wiring schedule')
    # Convert SVGs directly through MuPDF; keep all circuit labels and connectors intact.
    figure_paths = []
    qa_dir = ROOT / 'output/pdf/rendered'
    qa_dir.mkdir(exist_ok=True)
    for diagram in diagrams:
        svg = fitz.open(str(diagram))
        page = svg[0]
        target = qa_dir / (diagram.stem + '.png')
        page.get_pixmap(matrix=fitz.Matrix(1.4,1.4), alpha=False).save(str(target))
        figure_paths.append((diagram, target))
        svg.close()
    story += [NextPageTemplate('landscape'),PageBreak()]
    for index, (source, picture) in enumerate(figure_paths):
        if index:
            story.append(PageBreak())
        story.append(para('Circuit sheet: ' + source.stem.replace('_',' ').replace('-',' '),'Section'))
        img = Image(str(picture))
        img._restrictSize(15.7*inch, 8.70*inch)
        story += [img, para(str(source.relative_to(ROOT)) + ' | Drawing page: 17 x 11 inches. Use named nets and the wiring schedule together.', 'Small')]
    doc.build(story)
    check = fitz.open(str(OUT))
    assert len(check) >= 15
    total_text = '\n'.join(page.get_text() for page in check)
    assert 'Assembly and commissioning' in total_text and 'Point-to-point' in total_text
    assert len(total_text) > 20000
    for page in check:
        if not page.get_text().strip():
            raise ValueError('Blank page ' + str(page.number+1))
    print(f'PASS: {len(check)} pages; {OUT.stat().st_size} bytes; text and chapter checks passed')
    print(OUT)
    check.close()


if __name__ == '__main__':
    main()
