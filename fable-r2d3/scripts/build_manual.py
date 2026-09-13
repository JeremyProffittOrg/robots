"""Build, render and text-check the self-contained design PDF.

`--revision C` (default) rebuilds the published revision C manual; `--revision D`
writes the revision D manual to its own path with revision D labels and links.
"""
from pathlib import Path
import argparse, csv, html, json, re, hashlib
import fitz
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import BaseDocTemplate,PageTemplate,Frame,Paragraph,Spacer,PageBreak,NextPageTemplate,Image,Table,TableStyle
from package import ROOT,DEFAULT_REVISION,profile,path,label,public_url,release_date,add_revision_argument,read_json,catalog_rows,printed_counts,assembly_steps,drawing_index,revision_key
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
 c.drawString(38,22,label(d.revision)+' | Digital prototype - physical commissioning required');c.drawRightString(w-38,22,str(d.page))
def table(headers,rows,widths):
 data=[[para(s,'Small') for s in headers]]+[[para(s,'Small') for s in row] for row in rows]
 t=Table(data,colWidths=widths,repeatRows=1,hAlign='LEFT');t.setStyle(TableStyle([('BACKGROUND',(0,0),(-1,0),colors.HexColor('#dfeaf7')),('VALIGN',(0,0),(-1,-1),'TOP'),('LINEBELOW',(0,0),(-1,0),1,colors.HexColor('#52769d')),('ROWBACKGROUNDS',(0,1),(-1,-1),[colors.white,colors.HexColor('#f5f7fa')]),('LEFTPADDING',(0,0),(-1,-1),5),('RIGHTPADDING',(0,0),(-1,-1),5),('TOPPADDING',(0,0),(-1,-1),4),('BOTTOMPADDING',(0,0),(-1,-1),4)]));return t
def readcsv(path):return list(csv.DictReader(path.open(encoding='utf-8-sig')))
def picture(path,width=530,height=590):
 im=Image(str(path));im._restrictSize(width,height);return im
def main(argv=None):
 key=add_revision_argument(argparse.ArgumentParser(description='Build the R2-24 design PDF')).parse_args(argv).revision;p=profile(key)
 OUT=path(key,'pdf');OUT.parent.mkdir(parents=True,exist_ok=True);qa=path(key,'pdf_render');qa.mkdir(parents=True,exist_ok=True)
 doc=Manual(str(OUT),pagesize=letter,leftMargin=38,rightMargin=38,topMargin=40,bottomMargin=45,title='R2-24 design and assembly manual',author='Jeremy Proffitt robot project');doc.bookmarks=[];doc.revision=key
 doc.addPageTemplates([PageTemplate(id='portrait',frames=[Frame(38,45,536,707,id='p',leftPadding=0,rightPadding=0,topPadding=0,bottomPadding=0)],onPage=footer),PageTemplate(id='circuit',pagesize=(1224,792),frames=[Frame(38,45,1148,707,id='c',leftPadding=0,rightPadding=0,topPadding=0,bottomPadding=0)],onPage=footer)])
 report=json.loads((ROOT/'cad/validation.json').read_text());assert report['all_pass']
 checks=json.loads((ROOT/'docs/verification.json').read_text());assert checks['all_pass'] and checks['revision']==key,f'docs/verification.json is not an all-pass revision {key} verification'
 for name,sha in checks['source_sha256'].items():assert hashlib.sha256((ROOT/name).read_bytes()).hexdigest()==sha,name+' changed after verification'
 mass=json.loads((ROOT/'cad/mass-budget.json').read_text());slices=json.loads((ROOT/'cad/h2d-structure-check.json').read_text())
 electronics=readcsv(ROOT/'bom/electronics.csv');hardware=readcsv(ROOT/'bom/hardware.csv')
 total=sum(float(r['quantity'])*float(r['unit_usd']) for r in electronics+hardware)
 drawings=drawing_index(key);drawing_dir=path(key,'drawings');video=read_json(path(key,'delivery')/'video.json')
 profiles=f'{len(read_json(ROOT/"cad/metal/manifest.json"))} cutting profiles; ' if p['metal_profiles'] else ''
 contents=f'{report["parts"]} STL designs; {report["pieces"]} installed printed pieces; {profiles}{len(drawings["pngs"])} PNG drawings; {len(catalog_rows(ROOT/"audio/catalog.csv"))} original MP3s; {len(readcsv(ROOT/"electronics/wiring.csv"))} wiring connections; a {video["duration_s"]:g}-second CAD video.'
 story=[para('R2-24','TitleR2'),para('Design and assembly manual','Chapter'),para('Two whole body prints • One print per side leg • 24 inches tall'),picture(ROOT/'cad/assembly.png',530,435),para(f'{release_date(key)} | Revision {key} | {p["subtitle"]}','Small'),para('This is a digital prototype. Physical fit, frame strength, loaded driving, temperature, stopping distance and runtime require the commissioning tests. The video is a CAD simulation.')]
 story += [PageBreak(),para('Package and reading order','Chapter'),para(contents),para(f'Budget estimate: USD {total:.2f}, including {p["budget_scope"]}. Listed prices and allowances are distinguished in the BOM. Tax, shipping, tools and printer are excluded. No parts were purchased.'),para(f'Assembled mass estimate: {mass["estimated_total_g"]/1000:.2f} kg against the 9 kg design limit. The initial 6 kg assumption was not met. There is little mass reserve; weigh the actual parts and do not add payload. Drive performance with the specified TT motors is not physically verified.'),para(f'Read the mechanical, fabrication and electrical chapters first. Follow all {assembly_steps()} assembly steps. {p["commissioning_gates"]} Use the exact print manifest and hardware worksheet, not older revision files.'),para(f'[Watch the CAD video]({public_url(key,"motion.mp4")}) • [Download this PDF]({public_url(key,"design.pdf")})'),para('Contents','Section')]
 for title in ['Mechanical design and print guide',p['fabrication_title'],'Electrical design and wiring','Assembly and commissioning','Original robot voice collection','Digital verification and physical limits','BOM, mass, fastener and print worksheets','Full wiring schedule','Circuit sheets and engineering drawings']:
  story.append(para(title))
 for path in ['docs/mechanical.md','docs/fabrication.md','docs/electrical.md','docs/assembly.md','audio/README.md','docs/verification.md']:
  story+=[PageBreak()]+markdown(ROOT/path)
  if path=='docs/mechanical.md':
   for file,title,caption in p['manual_figures']:
    story += [PageBreak(),para(title,'Section'),picture(ROOT/'cad'/file),para(caption,'Small')]
 story += [PageBreak(),para('Electrical bill of materials','Chapter'),para('USD prices are per item or stated pack. Research dates: September 11-12, 2026. Allowances are estimates. Follow exact part/rating notes and check current availability before ordering.')]
 erows=[]
 for r in electronics:erows.append([r['quantity'],r['reference']+'\n'+r['item']+'\n'+r['part'],f"${r['unit_usd']} ({r['basis']})",r['notes']+(f" [Source]({r['url']})" if r['url'] else '')])
 story.append(table(['Qty','Component','Unit USD','Fit / rating / source'],erows,[28,180,80,248]))
 story += [PageBreak(),para('Mechanical hardware and consumables','Chapter'),para('Metal bolts, bearings and rods are purchased, not printed. STL mounts and adapters are in the print manifest. Quantities include stated spares and consumables.')]
 story.append(table(['Qty','Item','Specification','Use'],[[r['quantity'],r['item'],r['specification'],r['use']] for r in hardware],[28,135,160,213]))
 story += [PageBreak(),para('Mass budget','Chapter'),para(f'Estimated total {mass["estimated_total_g"]:.1f} g; limit {mass["design_limit_g"]:.0f} g; estimated reserve {mass["estimated_reserve_g"]:.1f} g. These figures combine calculation and allowances, not weighing. Use only installed quantities when measuring; unused stock and spares do not ride on the robot.')]
 story.append(table(['Component group','Estimated g','Basis'],[[r['component'],r['estimated_g'],r['basis']] for r in readcsv(ROOT/'bom/mass-budget.csv')],[195,65,276]))
 story += [PageBreak(),para('Fastener grip worksheet','Chapter'),para('Nominal stack checks complement the fabrication dimensions. Through joints include grip, washers and nut height. Tapped joints must have sufficient engagement and tip clearance. Measure actual hardware and never force a bottomed screw.')]
 stackrows=[]
 for r in readcsv(ROOT/'bom/fastener-stacks.csv'):
  remaining=float(r['length_mm'])-float(r['grip_mm'])-float(r['washer_mm'])
  result=f'{remaining-float(r["nut_mm"]):.2f} mm beyond full nut' if r['kind']=='through' else f'{remaining:.2f} mm in {r["usable_thread_mm"]} mm usable thread'
  stackrows.append([r['joint'],r['fastener'],f'{r["grip_mm"]} + {r["washer_mm"]} mm',result])
 story.append(table(['Joint','Fastener','Grip + washers','Nominal result'],stackrows,[175,110,95,156]))
 story += [PageBreak(),para('Print manifest','Chapter'),para(f'Solid material bound {report["solid_material_bound_g"]:.1f} g, before infill savings and without supports or purchased parts. Do not use this number as measured print or assembled mass. All dimensions below are millimetres. Use the native STL orientation and the reflection instructions in the mechanical chapter.')]
 story.append(table(['Part','Qty','Material','X x Y x Z','Solid g each'],[[r['part'],str(r['quantity']),r['material'],f"{r['x_mm']} x {r['y_mm']} x {r['z_mm']}",str(r['solid_mass_g'])] for r in report['rows']],[180,30,65,186,75]))
 story += [PageBreak(),para('H2D slice worksheet','Chapter'),para('Per-copy predictions from current G-code. Total filament includes discarded support and brim. Multiply by the quantity column for the complete set. These are not physical print measurements.')]
 story.append(table(['Part','Qty','Model g','Total filament g','Hours'],[[Path(r['part']).stem,str(r['quantity']),f'{r["installed_model_g"]:.1f}',f'{r["predicted_mass_with_support_g"]:.1f}',f'{r["predicted_time_s"]/3600:.2f}'] for r in slices['rows']],[200,35,100,120,81]))
 story += [PageBreak(),para('Point-to-point wiring schedule','Chapter'),para('One row is one connection. Identical named nets join across sheets. AWG identifies wire gauge. U7 output pin11 and unused D4 B outputs stay open. Read the complete electrical chapter before energizing.')]
 story.append(table(['Net','From','To','AWG'],[[r['net'],r['source'],r['target'],r['awg']] for r in readcsv(ROOT/'electronics/wiring.csv')],[110,185,206,35]))
 story += [NextPageTemplate('circuit'),PageBreak(),para('Circuit sheets','Chapter')]
 for i,svg in enumerate(sorted((ROOT/'electronics').glob('*.svg'))):
  if i:story.append(PageBreak())
  s=fitz.open(str(svg));png=qa/(svg.stem+'.png');s[0].get_pixmap(matrix=fitz.Matrix(1.5,1.5),alpha=False).save(str(png));s.close()
  story += [picture(png,1140,640),para(svg.name+' | Named nets connect across sheets. Full return wiring is in the schedule.','Small')]
 for row in drawings['pngs']:
  story += [PageBreak(),para('Engineering drawing: '+Path(row['file']).stem.replace('_',' ').replace('-',' '),'Section'),picture(drawing_dir/row['file'],1140,640),para(row['file']+' | Original PNG is included in the drawing collection. Cut-profile images are not paper templates.','Small')]
 doc.build(story)
 pdf=fitz.open(str(OUT));text='\n'.join(p.get_text() for p in pdf)
 for required in p['manual_required_text']+['Revision '+key]:assert required in text,required+' missing from the revision '+key+' manual'
 assert len(text)>25000 and len(pdf)>20
 for i,p in enumerate(pdf):
  assert p.get_text().strip();p.get_pixmap(matrix=fitz.Matrix(1,1),alpha=False).save(str(qa/f'page-{i+1:02d}.png'))
 path(key,'pdf_check').write_text(json.dumps({'revision':key,'pages':len(pdf),'bytes':OUT.stat().st_size,'sha256':hashlib.sha256(OUT.read_bytes()).hexdigest(),'text_characters':len(text),'all_pages_rendered':True,'budget_usd':round(total,2),'outline_entries':doc.bookmarks},indent=2))
 print(f'PASS: {label(key)} {len(pdf)} pages, {OUT.stat().st_size} bytes; required chapters, text and full-page rendering passed');pdf.close()
if __name__=='__main__':main()
