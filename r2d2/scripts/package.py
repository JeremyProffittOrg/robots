"""Create a checked ZIP containing only this fabrication package."""
from pathlib import Path
import hashlib,json,zipfile
ROOT=Path(__file__).resolve().parents[1]
def main():
 checks=json.loads((ROOT/'docs/verification.json').read_text());assert checks['all_pass']
 files=[]
 for folder in ['audio','bom','cad','docs','electronics','firmware','scripts','stl']:
  files.extend(p for p in (ROOT/folder).rglob('*') if p.is_file() and not any(x in p.parts for x in ['.pio','__pycache__']))
 files.extend(ROOT/p for p in ['README.md','.gitignore','.gitattributes','output/pdf/r2d2-design-and-assembly.pdf'])
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
 print(f'PASS: ZIP CRCs, {len(expected)} STLs, 16 MP3s and design PDF; {target.stat().st_size} bytes')
 print('SHA256 '+hashlib.sha256(target.read_bytes()).hexdigest())
if __name__=='__main__':main()
