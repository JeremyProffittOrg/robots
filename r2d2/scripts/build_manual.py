"""Build, render and text-check the self-contained design PDF."""
from pathlib import Path
import csv, html, json, re
import fitz
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import BaseDocTemplate,PageTemplate,Frame,Paragraph,Spacer,PageBreak,NextPageTemplate,Image,Table,TableStyle
ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'output/pdf/r2d2-design-and-assembly.pdf'
FONT=Path('C:/Windows/Fonts')
for name,file in [('Text','arial.ttf'),('Text-Bold','arialbd.ttf'),('Mono','consola.ttf')]:pdfmetrics.registerFont(TTFont(name,str(FONT/file)))
pdfmetrics.registerFontFamily('Text',normal='Text',bold='Text-Bold',italic='Text',boldItalic='Text-Bold')
styles=getSampleStyleSheet()
for name,size,lead in [('Body',9.5,13.2),('Small',7.5,10),('TitleR2',32,37),('Chapter',20,25),('Section',12.5,17),('CodeR2',8,11)]:
 styles.add(ParagraphStyle(name,fontName='Mono' if name=='CodeR2' else 'Text-Bold' if name in ['TitleR2','Chapter','Section'] else 'Text',fontSize=size,leading=lead,textColor=colors.HexColor('#152338'),spaceAfter=8 if name!='Small' else 3,keepWithNext=name in ['Chapter','Section']))
def inline(t):
 t=t.replace('\u2011','-').replace('\u2013','-').replace('\u2014',' - ').replace('\u00a0',' ')
 t=html.escape(t)
 t=re.sub(r'`([^`]+)`',r'<font name="Mono">\1</font>',t)
 t=re.sub(r'\[([^]]+)\]\((https?://[^)]+)\)',r'<link href="\2" color="#144b89">\1</link>',t)
 return t
def para(t,style='Body'):return Paragraph(inline(str(t)),styles[style])
def markdown(path):
 result=[];buffer=[];code=False
 def flush():
  if buffer:result.append(para(' '.join(buffer)));buffer.clear()
 for line in path.read_text(encoding='utf-8-sig').splitlines():
  if line.startswith('```'):flush();code=not code
  elif code:result.append(para(line,'CodeR2'))
  elif not line.strip():flush()
  elif line.startswith('# '):flush();result.append(para(line[2:],'Chapter'))
  elif line.startswith('## '):flush();result.append(para(line[3:],'Section'))
  elif line.startswith('- '):flush();result.append(para('• '+line[2:]))
  elif re.match(r'^\d+\.',line):flush();buffer.append(line)
  else:buffer.append(line.strip())
 flush();return result
class Manual(BaseDocTemplate):
 def afterFlowable(self,f):
  if isinstance(f,Paragraph) and f.style.name in ['Chapter','Section']:
   level=0 if f.style.name=='Chapter' else 1;key='b'+str(len(self.bookmarks));title=f.getPlainText()
   self.canv.bookmarkPage(key);self.canv.addOutlineEntry(title,key,level=level,closed=bool(level));self.bookmarks.append((title,self.page))
def footer(c,d):
 w,h=c._pagesize;c.setStrokeColor(colors.HexColor('#c7d0da'));c.line(38,34,w-38,34);c.setFont('Text',7.5);c.setFillColor(colors.HexColor('#405166'))
 c.drawString(38,22,'R2-24 | Digital prototype - physical commissioning required');c.drawRightString(w-38,22,str(d.page))
def table(headers,rows,widths):
 data=[[para(s,'Small') for s in headers]]+[[para(s,'Small') for s in row] for row in rows]
 t=Table(data,colWidths=widths,repeatRows=1,hAlign='LEFT');t.setStyle(TableStyle([('BACKGROUND',(0,0),(-1,0),colors.HexColor('#dfeaf7')),('VALIGN',(0,0),(-1,-1),'TOP'),('LINEBELOW',(0,0),(-1,0),1,colors.HexColor('#52769d')),('ROWBACKGROUNDS',(0,1),(-1,-1),[colors.white,colors.HexColor('#f5f7fa')]),('LEFTPADDING',(0,0),(-1,-1),5),('RIGHTPADDING',(0,0),(-1,-1),5),('TOPPADDING',(0,0),(-1,-1),4),('BOTTOMPADDING',(0,0),(-1,-1),4)]));return t
def readcsv(path):return list(csv.DictReader(path.open(encoding='utf-8-sig')))
def picture(path,width=530,height=590):
 im=Image(str(path));im._restrictSize(width,height);return im
def main():
 OUT.parent.mkdir(parents=True,exist_ok=True);qa=OUT.parent/'rendered';qa.mkdir(exist_ok=True)
 doc=Manual(str(OUT),pagesize=letter,leftMargin=38,rightMargin=38,topMargin=40,bottomMargin=45,title='R2-24 design and assembly manual',author='Jeremy Proffitt robot project');doc.bookmarks=[]
 doc.addPageTemplates([PageTemplate(id='portrait',frames=[Frame(38,45,536,707,id='p',leftPadding=0,rightPadding=0,topPadding=0,bottomPadding=0)],onPage=footer),PageTemplate(id='circuit',pagesize=(1224,792),frames=[Frame(38,45,1148,707,id='c',leftPadding=0,rightPadding=0,topPadding=0,bottomPadding=0)],onPage=footer)])
 report=json.loads((ROOT/'cad/validation.json').read_text());assert report['all_pass']
 checks=json.loads((ROOT/'docs/verification.json').read_text());assert checks['all_pass']
 electronics=readcsv(ROOT/'bom/electronics.csv');hardware=readcsv(ROOT/'bom/hardware.csv')
 total=sum(float(r['quantity'])*float(r['unit_usd']) for r in electronics+hardware)
 story=[para('R2-24','TitleR2'),para('Design and assembly manual','Chapter'),para('Two stackable body prints • One print per arm • 24 inches tall'),picture(ROOT/'cad/assembly.png',530,450),para('September 11, 2026 | Revision B | Fewer printed pieces','Small'),para('Digital checks passed. Physical fit, motor load, temperature, stopping distance and runtime still require the commissioning tests. This PDF is not proof of a built or tested robot.')]
 story += [PageBreak(),para('Package and reading order','Chapter'),para(f'{report["parts"]} distinct STL files; {report["pieces"]} printed pieces including fit parts and shim options; 16 original MP3 clips; 154 point-to-point wire connections.'),para(f'Budget estimate: USD {total:.2f}, including the listed hardware, consumables and six 1 kg filament spools. This mixes researched component prices with explicit allowances. It excludes shipping, tax, tools and printer. Unused fasteners and filament are expected.'),para('Start with the mechanical and electrical chapters. Complete the 50 assembly steps in order. Stop at the loaded-chassis gate before printing all cosmetic skins. Use the final BOM, print manifest and circuit sheets during construction.'),para('Contents','Section')]
 for title in ['Mechanical design and print guide','Electrical design and wiring','Assembly and commissioning','Original robot voice collection','Digital verification and physical limits','Electrical BOM, hardware BOM and print manifest','Full wiring schedule','Circuit sheets']:
  story.append(para(title))
 for path in ['docs/mechanical.md','docs/electrical.md','docs/assembly.md','audio/README.md','docs/verification.md']:
  story+=[PageBreak()]+markdown(ROOT/path)
  if path=='docs/mechanical.md':
   for file,title,caption in [('section.png','Integrated body structure','The frames, rod sleeves, adapters, head deck, neck and battery tray are features of the two full body prints.'),('exploded.png','Stackable body sections','The two complete body prints are separated vertically. Use the height stack for actual positions.'),('rear.png','Rear foot and service access','The rear foot stays open for gear service. Remove the complete upper body for internal service; its rear wall carries the switch plate.')]:
    story += [PageBreak(),para(title,'Section'),picture(ROOT/'cad'/file),para(caption,'Small')]
 story += [PageBreak(),para('Electrical bill of materials','Chapter'),para('USD prices are per item. Listed prices were researched on September 11, 2026; allowances are estimates. Follow the exact rating and part notes.')]
 erows=[]
 for r in electronics:erows.append([r['quantity'],r['reference']+'\n'+r['item']+'\n'+r['part'],f"${r['unit_usd']} ({r['basis']})",r['notes']+(f" [Source]({r['url']})" if r['url'] else '')])
 story.append(table(['Qty','Component','Unit USD','Fit / rating / source'],erows,[28,180,80,248]))
 story += [PageBreak(),para('Mechanical hardware and consumables','Chapter'),para('Metal bolts, bearings and rods are purchased, not printed. STL mounts and adapters are in the print manifest. Quantities include stated spares and consumables.')]
 story.append(table(['Qty','Item','Specification','Use'],[[r['quantity'],r['item'],r['specification'],r['use']] for r in hardware],[28,135,160,213]))
 story += [PageBreak(),para('Print manifest','Chapter'),para(f'Solid material bound {report["solid_material_bound_g"]:.1f} g, before infill savings and without supports or purchased parts. Do not use this number as measured print or assembled mass. All dimensions below are millimetres. Use the native STL orientation and the reflection instructions in the mechanical chapter.')]
 story.append(table(['Part','Qty','Material','X x Y x Z','Solid g each'],[[r['part'],str(r['quantity']),r['material'],f"{r['x_mm']} x {r['y_mm']} x {r['z_mm']}",str(r['solid_mass_g'])] for r in report['rows']],[180,30,65,186,75]))
 story += [PageBreak(),para('Point-to-point wiring schedule','Chapter'),para('One row is one connection. Join identical net names. AWG identifies wire gauge; read the complete electrical chapter before energizing. Unused AHCT125 outputs pin8 and pin11 remain open.')]
 story.append(table(['Net','From','To','AWG'],[[r['net'],r['source'],r['target'],r['awg']] for r in readcsv(ROOT/'electronics/wiring.csv')],[110,185,206,35]))
 story += [NextPageTemplate('circuit'),PageBreak(),para('Circuit sheets','Chapter')]
 for i,svg in enumerate(sorted((ROOT/'electronics').glob('*.svg'))):
  if i:story.append(PageBreak())
  s=fitz.open(str(svg));png=qa/(svg.stem+'.png');s[0].get_pixmap(matrix=fitz.Matrix(1.5,1.5),alpha=False).save(str(png));s.close()
  story += [picture(png,1140,640),para(svg.name+' | Named nets connect across sheets. Full return wiring is in the schedule.','Small')]
 doc.build(story)
 pdf=fitz.open(str(OUT));text='\n'.join(p.get_text() for p in pdf)
 for required in ['Assembly and commissioning','Point-to-point wiring schedule','609.6','DRV8833','physical']:assert required in text
 assert len(text)>25000 and len(pdf)>20
 for i,p in enumerate(pdf):
  assert p.get_text().strip();p.get_pixmap(matrix=fitz.Matrix(1,1),alpha=False).save(str(qa/f'page-{i+1:02d}.png'))
 (ROOT/'docs/pdf-check.json').write_text(json.dumps({'pages':len(pdf),'bytes':OUT.stat().st_size,'text_characters':len(text),'all_pages_rendered':True,'budget_usd':round(total,2),'outline_entries':doc.bookmarks},indent=2))
 print(f'PASS: {len(pdf)} pages, {OUT.stat().st_size} bytes; required chapters, text and full-page rendering passed');pdf.close()
if __name__=='__main__':main()
