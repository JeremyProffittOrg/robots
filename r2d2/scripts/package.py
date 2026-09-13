"""Create a checked ZIP containing only this fabrication package.

Revision-aware release plumbing. `python scripts/package.py` packages the
published revision C exactly as before; `--revision D` packages revision D into
its own delivery directory. Every path, public URL and label that differs by
revision is declared once in REVISIONS and shared by build_manual.py,
render_video.py, draw_robot.py and verify.py. Revision C keeps its original
root paths, so a later revision never overwrites the published C files.
"""
from pathlib import Path
import argparse,csv,datetime,hashlib,json,re,shutil,zipfile
ROOT=Path(__file__).resolve().parents[1]
CDN='https://d1lftyhk9r30k1.cloudfront.net'
DELIVERY_FILES=('motion.mp4','design.pdf')
DEFAULT_REVISION='C'
REVISIONS={
 'C':{
  'delivery':'output/delivery','pdf':'output/pdf/r2d2-design-and-assembly.pdf','pdf_check':'docs/pdf-check.json',
  'pdf_render':'output/pdf/rendered','drawings':'output/drawings','archive':'output/r2d2-fabrication.zip',
  'video_preview':'tmp/reference/video-preview.png','release_date':'September 12, 2026',
  'subtitle':'Detailed exterior and metal moving frame','metal_profiles':True,'posture_plot':True,
  'budget_scope':'hardware, consumables, machining/welding allowances and six 1 kg filament spools',
  'commissioning_gates':'The metal frame and loaded rolling tests are gates before final finish.',
  'fabrication_title':'Metal fabrication worksheet',
  'manual_figures':[('section.png','Metal load frame','Metal shafts, spines, guide and foot frames carry body load. Electronics panels are omitted for this view; purchased hardware is shown as envelopes.'),('exploded.png','Whole stackable covers','Offsets identify the complete covers and are not assembly dimensions. The upper shell is installed before the shoulder carriers.'),('rear.png','Rear post and foot','The rear post changes supported body posture. The rear foot has a separate steering link and a load-bearing spherical joint.')],
  'manual_required_text':['Assembly and commissioning','Metal fabrication worksheet','Point-to-point wiring schedule','609.6','DRV8833','KBRM-03-MH','physical'],
  'drawing_features':'Metal shoulder pivots\nGuided rear telescoping post\nSupported body tilt\nInternal head friction wheel\nSix ground motors / 12 wheels\nPhone control over Wi-Fi',
  'mechanism_footer':'Actual mounting geometry; purchased motors/wheels/bearings are envelopes. Metal frame carries the vertical load.',
  'video_scenes':[('Detailed shell and powered head','Two whole body prints; one print per side leg.'),('Rear post extends; body tilts','Supported three-foot motion. Timing is illustrative.'),('Metal frame and rear guide exposed','12 mm shoulder shafts; separate actuator and sliding guide.'),('Printed covers separated for assembly','{designs} STL designs / {pieces} printed pieces. Metal frame stays assembled.'),(None,'609.6 mm nominal height; twelve ground wheels; phone Wi-Fi.')]},
 'D':{
  'delivery':'output/delivery/revision-d','pdf':'output/pdf/revision-d/r2d2-design-and-assembly.pdf','pdf_check':'docs/pdf-check-revision-d.json',
  'pdf_render':'output/pdf/rendered/revision-d','drawings':'output/drawings/revision-d','archive':'output/r2d2-fabrication-revision-d.zip',
  'video_preview':'tmp/reference/video-preview-revision-d.png','release_date':None,
  'subtitle':'Printed structural frame and motorized interlocked stance change','metal_profiles':False,'posture_plot':False,
  'budget_scope':'hardware, consumables, 2020 extrusion and filament',
  'commissioning_gates':'The printed frame, stance-lock interlock and loaded rolling tests are gates before final finish.',
  'fabrication_title':'Frame fabrication worksheet',
  'manual_figures':[('section.png','Printed load frame','Printed structural modules with 2020 extrusion reinforcement carry body load. Electronics panels are omitted for this view; purchased hardware is shown as envelopes.'),('exploded.png','Whole stackable covers','Offsets identify the complete covers and are not assembly dimensions.'),('rear.png','Center leg and stance lock','A linear actuator moves the center leg. Drive is refused while the stance changes, and the shoulder lock is sensed before drive is allowed.')],
  'manual_required_text':['Assembly and commissioning','Frame fabrication worksheet','Point-to-point wiring schedule','609.6','physical'],
  'drawing_features':'Printed structural frame\n2020 extrusion reinforcement\nMotorized center-leg deployment\nInterlocked two- and three-foot stance\nDFRobot Romeo ESP32-S3 control\nPhone control over Wi-Fi',
  'mechanism_footer':'Actual mounting geometry; purchased motors/wheels/bearings are envelopes. Printed frame and 2020 extrusion carry the vertical load.',
  'video_scenes':[('Detailed shell and powered head','Two whole body prints; one print per side leg.'),('Center leg deploys; stance changes','Motorized, interlocked transition. Timing is illustrative.'),('Printed frame and extrusion exposed','Printed structural modules with 2020 extrusion reinforcement.'),('Printed covers separated for assembly','{designs} STL designs / {pieces} printed pieces. Frame stays assembled.'),(None,'609.6 mm nominal height; two- and three-foot stances; phone Wi-Fi.')]},
}

class ReleaseNotReady(RuntimeError):
 """A release gate failed; nothing was written for that revision."""

def revision_key(value):
 key=str(value).strip().upper()
 if key not in REVISIONS:raise ValueError(f'unknown release revision {value!r}; expected one of {sorted(REVISIONS)}')
 return key
def profile(revision):return REVISIONS[revision_key(revision)]
def path(revision,name,root=ROOT):return Path(root)/profile(revision)[name]
def delivery_dir(revision,root=ROOT):return path(revision,'delivery',root)
def s3_prefix(revision):return 'r2d2/revision-'+revision_key(revision).lower()
def public_url(revision,name):
 if name not in DELIVERY_FILES:raise ValueError(f'{name!r} is not a published delivery file')
 return f'{CDN}/{s3_prefix(revision)}/{name}'
def label(revision):return 'R2-24 revision '+revision_key(revision)
def video_title(revision):return 'R2-24 | revision '+revision_key(revision)
def release_date(revision,today=None):
 fixed=profile(revision)['release_date']
 if fixed:return fixed
 day=today or datetime.date.today();return f'{day:%B} {day.day}, {day.year}'
def cli_revision(argv):
 """Read `--revision X` or `--revision=X` from an argv list; default is revision C."""
 for i,arg in enumerate(argv):
  if arg=='--revision':
   if i+1>=len(argv):raise ValueError('--revision needs a value')
   return revision_key(argv[i+1])
  if arg.startswith('--revision='):return revision_key(arg.split('=',1)[1])
 return DEFAULT_REVISION
def add_revision_argument(parser):
 parser.add_argument('--revision',type=revision_key,default=DEFAULT_REVISION,choices=sorted(REVISIONS),help='release revision (default C, the published revision)')
 return parser

def read_json(file):return json.loads(Path(file).read_text())
def sha256(file):return hashlib.sha256(Path(file).read_bytes()).hexdigest()
def catalog_rows(file):
 with Path(file).open(encoding='utf-8-sig',newline='') as f:return list(csv.DictReader(f))
def printed_counts(root=ROOT):
 rows=read_json(Path(root)/'cad/validation.json')['rows']
 return {'designs':len(rows),'pieces':sum(int(r['quantity']) for r in rows)}
def assembly_steps(root=ROOT):
 return sum(1 for line in (Path(root)/'docs/assembly.md').read_text(encoding='utf-8-sig').splitlines() if re.match(r'^\d+\.',line))
def drawing_index(revision,root=ROOT):
 key=revision_key(revision);index=read_json(path(key,'drawings',root)/'index.json')
 if index.get('revision')!=key:raise ReleaseNotReady(f"{path(key,'drawings',root)/'index.json'} is revision {index.get('revision')!r}, not {key}")
 if not index.get('pngs'):raise ReleaseNotReady(f'revision {key} drawing index lists no PNGs')
 return index
def recorded_revision_matches(report,key):
 # Revision C reports were written before reports carried a revision field.
 recorded=report.get('revision')
 return recorded==key or (recorded is None and key=='C')

def check_release(revision,root=ROOT):
 """Gate a release. Raises ReleaseNotReady before any file is written."""
 key=revision_key(revision);root=Path(root)
 checks=read_json(root/'docs/verification.json')
 if checks.get('all_pass') is not True or checks.get('revision')!=key:
  raise ReleaseNotReady(f"NOT READY: {label(key)} needs docs/verification.json with all_pass true and revision {key}; found all_pass={checks.get('all_pass')!r}, revision={checks.get('revision')!r}")
 if not checks.get('source_sha256'):raise ReleaseNotReady(f'revision {key} verification records no source hashes')
 for name,sha in checks['source_sha256'].items():
  if sha256(root/name)!=sha:raise ReleaseNotReady(f'{name} changed after revision {key} verification')
 pdf=path(key,'pdf',root);review=read_json(path(key,'pdf_check',root))
 if not (review.get('all_pages_rendered') is True and recorded_revision_matches(review,key) and sha256(pdf)==review['sha256']):
  raise ReleaseNotReady(f'{pdf} does not match its revision {key} PDF check')
 delivery=delivery_dir(key,root);video=read_json(delivery/'video.json')
 if not (recorded_revision_matches(video,key) and sha256(delivery/'motion.mp4')==video['sha256']):
  raise ReleaseNotReady(f'{delivery/"motion.mp4"} does not match its revision {key} video report')
 validation=read_json(root/'cad/validation.json');drawings=drawing_index(key,root)
 return {'pdf':pdf,'review':review,'delivery':delivery,
  'stls':{f"r2d2/stl/{r['part']}.stl" for r in validation['rows']},
  'mp3s':len(catalog_rows(root/'audio/catalog.csv')),
  'pngs':{(Path('r2d2')/profile(key)['drawings']/row['file']).as_posix() for row in drawings['pngs']}}

def package(revision=DEFAULT_REVISION,root=ROOT):
 """Build and check the ZIP first; only a fully passing release gets design.pdf and manifest.json."""
 key=revision_key(revision);root=Path(root);gate=check_release(key,root);p=profile(key)
 delivery=gate['delivery'];review=gate['review'];manifest=delivery/'manifest.json'
 files=[]
 for folder in ['audio','bom','cad','docs','electronics','firmware','scripts','stl']:
  files.extend(f for f in (root/folder).rglob('*') if f.is_file() and not any(x in f.parts for x in ['.pio','__pycache__']))
 files.extend(root/f for f in ['README.md','.gitignore','.gitattributes',p['pdf']])
 drawings=path(key,'drawings',root)
 files.extend(drawings/row['file'] for row in drawing_index(key,root)['pngs'])
 files.extend([drawings/'index.json',delivery/'motion.mp4',delivery/'video.json'])
 target=path(key,'archive',root);partial=target.with_name(target.name+'.partial')
 delivery_member=(Path('r2d2')/p['delivery']/'motion.mp4').as_posix()
 with zipfile.ZipFile(partial,'w',zipfile.ZIP_DEFLATED,compresslevel=9) as z:
  for f in sorted(set(files)):z.write(f,Path('r2d2')/f.relative_to(root))
 with zipfile.ZipFile(partial) as z:
  names=z.namelist();problems=[]
  if z.testzip() is not None:problems.append('ZIP CRC failure')
  release_stls={n for n in names if n.endswith('.stl') and len(Path(n).parts)==3 and n.startswith('r2d2/stl/')}
  if release_stls!=gate['stls']:problems.append(f'STL set {sorted(release_stls)} != validation manifest {sorted(gate["stls"])}')
  mp3s=len([n for n in names if n.endswith('.mp3')])
  if mp3s!=gate['mp3s']:problems.append(f'{mp3s} MP3s != audio catalog {gate["mp3s"]}')
  if not gate['pngs']<=set(names):problems.append('drawing PNGs missing: '+', '.join(sorted(gate['pngs']-set(names))))
  for member in [(Path('r2d2')/p['pdf']).as_posix(),delivery_member]:
   if member not in names:problems.append(member+' missing')
  if problems:
   z.close();partial.unlink();raise ReleaseNotReady('; '.join(problems))
 partial.replace(target)
 shutil.copyfile(gate['pdf'],delivery/'design.pdf')
 manifest.write_text(json.dumps({'revision':key,'files':{n:sha256(delivery/n) for n in ['motion.mp4','design.pdf']},'pdf_pages':review['pages'],'video_simulation':True,'physical_tested':False},indent=2))
 print(f'PASS: {label(key)} ZIP CRCs, {len(gate["stls"])} STLs, {len(gate["pngs"])} PNGs, {gate["mp3s"]} MP3s, video and design PDF; {target.stat().st_size} bytes')
 print('Manifest '+manifest.relative_to(root).as_posix())
 print('SHA256 '+sha256(target))
 return manifest

def main(argv=None):
 args=add_revision_argument(argparse.ArgumentParser(description=__doc__.splitlines()[0])).parse_args(argv)
 package(args.revision)
if __name__=='__main__':main()
