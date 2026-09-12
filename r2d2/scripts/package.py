"""Create a checked ZIP containing only this fabrication package."""
from pathlib import Path
import hashlib,json,zipfile,shutil
ROOT=Path(__file__).resolve().parents[1]
def main():
 checks=json.loads((ROOT/'docs/verification.json').read_text());assert checks['all_pass'] and checks['revision']=='C'
 for name,sha in checks['source_sha256'].items():assert hashlib.sha256((ROOT/name).read_bytes()).hexdigest()==sha,name
 pdf=ROOT/'output/pdf/r2d2-design-and-assembly.pdf';review=json.loads((ROOT/'docs/pdf-check.json').read_text())
 assert review['all_pages_rendered'] and hashlib.sha256(pdf.read_bytes()).hexdigest()==review['sha256']
 delivery=ROOT/'output/delivery';delivery.mkdir(exist_ok=True)
 video=json.loads((delivery/'video.json').read_text());assert hashlib.sha256((delivery/'motion.mp4').read_bytes()).hexdigest()==video['sha256']
 shutil.copyfile(pdf,delivery/'design.pdf')
 (delivery/'manifest.json').write_text(json.dumps({'revision':'C','files':{n:hashlib.sha256((delivery/n).read_bytes()).hexdigest() for n in ['motion.mp4','design.pdf']},'pdf_pages':review['pages'],'video_simulation':True,'physical_tested':False},indent=2))
 files=[]
 for folder in ['audio','bom','cad','docs','electronics','firmware','scripts','stl']:
  files.extend(p for p in (ROOT/folder).rglob('*') if p.is_file() and not any(x in p.parts for x in ['.pio','__pycache__']))
 files.extend(ROOT/p for p in ['README.md','.gitignore','.gitattributes','output/pdf/r2d2-design-and-assembly.pdf'])
 files.extend((ROOT/'output/drawings').rglob('*.png'))
 files.extend(ROOT/p for p in ['output/drawings/index.json','output/delivery/motion.mp4','output/delivery/video.json'])
 target=ROOT/'output/r2d2-fabrication.zip'
 with zipfile.ZipFile(target,'w',zipfile.ZIP_DEFLATED,compresslevel=9) as z:
  for p in sorted(files):z.write(p,Path('r2d2')/p.relative_to(ROOT))
 with zipfile.ZipFile(target) as z:
  assert z.testzip() is None
  manifest=json.loads((ROOT/'cad/validation.json').read_text())
  expected={r['part']+'.stl' for r in manifest['rows']}
  assert {Path(n).name for n in z.namelist() if n.endswith('.stl')}==expected
  assert len([n for n in z.namelist() if n.endswith('.mp3')])==16
  assert 'r2d2/output/pdf/r2d2-design-and-assembly.pdf' in z.namelist()
  assert len([n for n in z.namelist() if '/output/drawings/' in n and n.endswith('.png')])==18
  assert 'r2d2/output/delivery/motion.mp4' in z.namelist()
 print(f'PASS: ZIP CRCs, {len(expected)} STLs, 18 PNGs, 16 MP3s, video and design PDF; {target.stat().st_size} bytes')
 print('SHA256 '+hashlib.sha256(target.read_bytes()).hexdigest())
if __name__=='__main__':main()
