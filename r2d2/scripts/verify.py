"""Focused digital checks. Does not upload firmware, print, or drive hardware."""
from pathlib import Path
import csv, hashlib, json, os, re, subprocess, sys, tempfile
import trimesh
import numpy as np
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'scripts'))
from export_cad import EXE,validate,PARTS,PURCHASED_PIECE_LIMIT

def audit_purchased_pieces(rows):
 """Count physical quantities; unknown rows cannot silently count as zero.
 This checks the submitted ledger, not whether every CAD joint is represented.
 """
 total=0;seen=set();invalid=[];unresolved=[]
 for row in rows:
  key=row.get('id','').strip();item=row.get('item','').strip()
  if not key or key in seen or not item:invalid.append(key or '(missing ID)')
  seen.add(key)
  status=row.get('count_status','').strip();quantity=str(row.get('quantity','')).strip()
  if status=='unresolved':
   unresolved.append(key)
   if quantity:invalid.append(key+': unresolved row has a quantity')
  elif status!='counted' or not re.fullmatch(r'[1-9][0-9]*',quantity):
   invalid.append(key+': expected a positive whole-piece quantity')
  else:total+=int(quantity)
 if not rows:invalid.append('empty ledger')
 return {'limit':PURCHASED_PIECE_LIMIT,'known_pieces':total,'excess_known_pieces':max(0,total-PURCHASED_PIECE_LIMIT),
  'unresolved_rows':unresolved,'invalid_rows':invalid,
  'passed':bool(rows) and not unresolved and not invalid and total<=PURCHASED_PIECE_LIMIT,
  'scope':'Arithmetic and declared gaps only; CAD/wiring completeness needs separate review'}

def check_purchased_bom():
 source=ROOT/'bom/development-purchased.csv'
 with source.open(encoding='utf-8-sig',newline='') as f:rows=list(csv.DictReader(f))
 report=audit_purchased_pieces(rows)
 report['source_sha256']=hashlib.sha256(source.read_bytes()).hexdigest()
 (ROOT/'docs/purchased-piece-check.json').write_text(json.dumps(report,indent=2),encoding='utf-8')
 print(f"Purchased-piece audit: {report['known_pieces']} known /{PURCHASED_PIECE_LIMIT} maximum; "
       f"{len(report['unresolved_rows'])} unresolved rows; {len(report['invalid_rows'])} invalid rows")
 if not report['passed']:raise SystemExit('NOT READY: purchased-piece limit or ledger completeness failed')
 print(f'PASS: submitted physical-piece ledger is complete and within{PURCHASED_PIECE_LIMIT}; assembly review is still required')
def run(args,**kwargs):
 result=subprocess.run(args,cwd=ROOT,capture_output=True,text=True,timeout=180,**kwargs)
 if result.returncode:raise RuntimeError(str(args)+'\n'+result.stdout+'\n'+result.stderr)
 return result.stdout.strip()

def nut_pocket_checks():
 def distance(mesh,origin,direction):
  triangles=mesh.triangles;e1=triangles[:,1]-triangles[:,0];e2=triangles[:,2]-triangles[:,0]
  p=np.cross(direction,e2);det=np.einsum('ij,ij->i',e1,p);good=abs(det)>1e-10
  inv=np.zeros(len(det));inv[good]=1/det[good];s=origin-triangles[:,0]
  u=np.einsum('ij,ij->i',s,p)*inv;q=np.cross(s,e1);v=(q@direction)*inv;t=np.einsum('ij,ij->i',e2,q)*inv
  hits=good&(u>=-1e-7)&(v>=-1e-7)&(u+v<=1+1e-7)&(t>1e-4)
  assert hits.any(),'No pocket wall found';return float(t[hits].min())
 dome=trimesh.load_mesh(ROOT/'stl/dome.stl');lower=trimesh.load_mesh(ROOT/'stl/body_lower.stl')
 for mesh,centers,zs,nut_af,pocket_d in [(dome,[(0,0,0)],[18.5,21,23.5],13,15.4),
   (lower,[(119*np.cos(np.deg2rad(a)),119*np.sin(np.deg2rad(a)),a) for a in [45,135,225,315]],[135.9,137,138.1],5.5,6.8)]:
  expected=pocket_d*np.sqrt(3)/4
  for x,y,angle in centers:
   for z in zs:
    for side in range(6):
     a=np.deg2rad(angle+30+side*60);r=distance(mesh,np.array([x,y,z]),np.array([np.cos(a),np.sin(a),0.]))
     assert (nut_af+.25)/2<=r and abs(r-expected)<.01,(nut_af,z,side,r,expected)
 return 'Actual STL nut pockets:90 ray measurements meet across-flats clearance and wall-location checks'
def cad_checks():
 source=(ROOT/'cad/r2d2.scad').as_posix()
 def printed(name,xyz):return 'translate('+json.dumps(xyz)+') import('+json.dumps((ROOT/'stl'/f'{name}.stl').as_posix())+');'
 lower=printed('body_lower',[0,0,130]);upper=printed('body_upper',[0,0,269.7]);dome=printed('dome',[0,0,441.8])
 holder=printed('head_motor_mount',[0,0,407.5]);cassette=printed('drive_cassette',[0,0,16])
 floor='translate([0,0,413])linear_extrude(2)headfloor_profile();'
 wheels='for(x=[-29,29])for(y=[-37,37])translate([x,y,31.5])wheel();'
 checks={
  'body_seam_source_5um_contact_allowance':('translate([0,0,165])intersection(){body_lower();translate([0,0,.005])body_upper();}',None),
  'shoulder_shell':('intersection(){'+upper+'shoulders();}',None),
  'head_neck':('intersection(){'+upper+dome+'}',None),
  'head_wheel_clearance':('intersection(){translate([76.5,0,426.32])wheel();union(){'+holder+floor+'}}',None),
  'head_motor_seat':('intersection(){translate([39.7,-57,415.1])cube([18.6,70,22.44]);'+holder+'}',('z',415.1)),
  'head_mount_floor':('intersection(){'+holder+floor+'}',('z',415)),
  'head_floor_chassis':('intersection(){'+floor+'shoulders();}',('absx',95)),
  'foot_wheel_frame':('intersection(){union(){'+wheels+'}union(){foot_arch(true);'+cassette+'}}',None),
  'outer_wheel_cover':('intersection(){union(){'+wheels+'}'+printed('outer_foot',[0,0,5])+'}',None),
  'rear_wheel_cover':('intersection(){union(){'+wheels+'}'+printed('rear_foot',[0,0,5])+'}',None),
  'outer_cover_frame':('intersection(){foot_arch();'+printed('outer_foot',[0,0,5])+'}',('z',75)),
  'rear_cover_frame':('intersection(){foot_arch(true);'+printed('rear_foot',[0,0,5])+'}',('z',75)),
  'rear_steering_cover':('for(a=[-8,0,8])intersection(){foot_assembly(true,true,a);'+printed('rear_foot',[0,0,5])+'}',('z',75)),
  'cassette_sole':('intersection(){foot_arch();'+cassette+'}',('z',16)),
  'rear_post_shell':('for(s=[5.03832,38,72])intersection(){rear_guide(s);'+lower+'}',None),
 }
 results=[];failures=[]
 with tempfile.TemporaryDirectory(prefix='r2-cad-check-') as folder:
  tmp=Path(folder)
  for name,(body,contact) in checks.items():
   script=tmp/(name+'.scad');out=tmp/(name+'.stl');script.write_text('use <'+source+'>\n'+body)
   proc=subprocess.Popen([EXE,'--export-format','binstl','-o',str(out),str(script)],stdout=subprocess.PIPE,stderr=subprocess.PIPE,text=True)
   try:stdout,stderr=proc.communicate(timeout=600 if name.startswith('body_seam') else 180)
   except subprocess.TimeoutExpired:
    subprocess.run(['taskkill','/PID',str(proc.pid),'/T','/F'],capture_output=True);proc.communicate();raise RuntimeError(name+' CAD timeout')
   log=stdout+stderr
   if 'ERROR:' in log or any(k in log for k in ['unknown module','unknown variable','undefined variable']):raise RuntimeError(name+': '+log)
   if 'Current top level object is empty' in log:
    results.append(name+': no intersecting volume');print('PASS '+results[-1],flush=True);continue
   if not out.exists():raise RuntimeError(name+': '+log)
   m=trimesh.load_mesh(out)
   if contact:
    axis,value=contact;coords=abs(m.vertices[:,0]) if axis=='absx' else m.vertices[:,2]
    if all(abs(v-value)<.0001 for v in coords):
     results.append(name+': only the specified contact plane');print('PASS '+results[-1],flush=True);continue
   failure={'check':name,'volume_mm3':float(abs(m.volume)),'bounds_mm':m.bounds.tolist()};failures.append(failure);print('FAIL '+json.dumps(failure),flush=True)
 if failures:raise AssertionError(json.dumps(failures,indent=2))
 return results

def main():
 (ROOT/'docs/verification.json').write_text(json.dumps({'all_pass':False,'revision':'D-development','status':'checks in progress; complete purchased-piece ledger required','physical_validation':False},indent=2))
 if '--cad-only' not in sys.argv:check_purchased_bom()
 inputs=sorted((ROOT/'cad').glob('*.scad'))+sorted((ROOT/'stl').glob('*.stl'))+sorted((ROOT/'firmware/include').glob('*.h'))+[ROOT/'firmware/src/main.cpp',ROOT/'firmware/data/app.js',ROOT/'electronics/wiring.csv',ROOT/'bom/fastener-stacks.csv']+[ROOT/'scripts'/n for n in ['verify.py','check_kinematics.py','export_cad.py','slice_structure.py']]
 initial_hashes={str(p.relative_to(ROOT)):hashlib.sha256(p.read_bytes()).hexdigest() for p in inputs}
 results=[];validate();results.append('STL geometry: all meshes closed, connected, positive and inside300mm; nonnegative bed Z')
 results.extend(cad_checks())
 if '--cad-only' in sys.argv:
  (ROOT/'docs/verification.json').write_text(json.dumps({'all_pass':False,'revision':'C','cad_checks_pass':True,'checks':results,'status':'other package checks pending','physical_validation':False},indent=2));return
 results.append(run([sys.executable,'scripts/check_kinematics.py']))
 results.append(nut_pocket_checks())
 stacks=list(csv.DictReader((ROOT/'bom/fastener-stacks.csv').open()))
 for r in stacks:
  remaining=float(r['length_mm'])-float(r['grip_mm'])-float(r['washer_mm'])
  if r['kind']=='through':assert remaining-float(r['nut_mm'])>=float(r['min_extra_mm'])-1e-6,r['joint']
  else:assert float(r['min_thread_mm'])-1e-6<=remaining<=float(r['usable_thread_mm'])-.25+1e-6,r['joint']
 assert 15.4*3**.5/2>=13.25 and 6.8*3**.5/2>=5.75
 results.append('22 fastener stacks: nut engagement, blind-depth margins and hex-pocket across-flats checks PASS')
 with tempfile.TemporaryDirectory(prefix='r2-verify-') as tmp:
  env=os.environ.copy();env['PATH']=r'C:\msys64\mingw64\bin;'+env['PATH'];exe=Path(tmp)/'control.exe'
  run([r'C:\msys64\mingw64\bin\g++.exe','-std=c++11','-Wall','-Wextra','-Werror','-I','firmware/include','firmware/test/control_test.cpp','-o',str(exe)],env=env)
  results.append(run([str(exe)],env=env))
 results.append(run(['node','--check','firmware/data/app.js']) or 'JavaScript syntax: PASS')
 results.append(run(['node','firmware/test/ui_test.js']))
 audio=list(csv.DictReader((ROOT/'audio/catalog.csv').open()))
 assert len(audio)==16
 for row in audio:
  p=ROOT/row['path'];assert hashlib.sha256(p.read_bytes()).hexdigest()==row['sha256']
  run(['ffmpeg','-v','error','-i',str(p),'-f','null','-'])
 results.append('16 MP3 files: hashes and full decode PASS')
 structure=json.loads((ROOT/'cad/h2d-structure-check.json').read_text())
 assert {Path(r['part']).stem for r in structure['rows']}==set(PARTS)
 for row in structure['rows']:
  assert row['return_code']==0 and not row['warning']
  assert hashlib.sha256((ROOT/row['part']).read_bytes()).hexdigest()==row['sha256']
 results.append('Ten whole-part H2D slices: success, no warnings and current STL hashes verified')
 wires=list(csv.DictReader((ROOT/'electronics/wiring.csv').open()))
 config=(ROOT/'firmware/include/config.h').read_text()
 expected={'LEFT':(14,32),'RIGHT':(15,33),'REAR':(27,12)}
 for i,(side,pins) in enumerate(expected.items(),1):
  for direction,pin,suffix in [('FWD',pins[0],'1'),('REV',pins[1],'2')]:
   for channel in ['A','B']:
    assert any(r['net']==side+'_'+direction and r['source']==f'U1 GPIO{pin}' and r['target']==f'D{i} {channel}IN{suffix}' for r in wires)
 assert re.search(r'MOTOR\[6\]=\{14,32,15,33,27,12\}',config)
 for name,pin in [('SLEEP',13),('STEER',25),('HEAD',26),('HEAD_REVERSE',17),('POST_EXTEND',4),('POST_RETRACT',16),('SDA',21),('SCL',22),('FAULT',36),('POWER',39),('PACK',34),('BCLK',18),('LRCLK',19),('AUDIO',23)]:assert re.search(fr'{name}={pin}\b',config)
 assert 14.6*22/122<3.3 and 5.25*15/25<3.3
 assert len(wires)==220
 def edge(source,target):assert any(r['source']==source and r['target']==target for r in wires),(source,target)
 for source,target in [('U1 GPIO26','D4 AIN1'),('U1 GPIO17','D4 AIN2'),('U1 GPIO4','U7 pin5'),('U7 pin6','LS_EXT COM'),('LS_EXT NC','D5 IN1'),('D5 IN1','R_LS_EXT 4.7k pin1'),('U1 GPIO16','U7 pin9'),('U7 pin8','LS_RET COM'),('LS_RET NC','D5 IN2'),('D5 IN2','R_LS_RET 4.7k pin1'),('D5 OUT1','ACT red / pin3'),('D5 OUT2','ACT black / pin4'),('ACT purple / pin2','R_POT 1k pin1'),('P6 VOUT','U10 INA219 VIN+'),('U10 VIN-','D5 DRV8871 VM')]:edge(source,target)
 for n,pin in [('SDA',21),('SCL',22)]:
  for board in ['U9','U10']:edge(f'U1 GPIO{pin}',f'{board} {n}')
 assert not any('SV2' in r['source']+r['target'] for r in wires)
 results.append('220 wiring rows: drive/head outputs, independent NC post limits, feedback, I2C, pins and divider bounds PASS')
 fs=ROOT/'firmware/.pio/build/feather/littlefs.bin';fw=ROOT/'firmware/.pio/build/feather/firmware.bin'
 assert fs.exists() and fs.stat().st_size<=2097152 and fw.exists() and fw.stat().st_size<=2031616
 results.append(f'Firmware image {fw.stat().st_size} bytes; filesystem image {fs.stat().st_size} bytes: fit partitions')
 video=json.loads((ROOT/'output/delivery/video.json').read_text())
 assert hashlib.sha256((ROOT/'output/delivery/motion.mp4').read_bytes()).hexdigest()==video['sha256']
 for name,sha in video['source_sha256'].items():assert hashlib.sha256((ROOT/name).read_bytes()).hexdigest()==sha,name+' changed since video render'
 results.append('30-second CAD video: encoded bytes and source hashes match')
 drawings=json.loads((ROOT/'output/drawings/index.json').read_text())
 assert drawings['revision']=='C' and len(drawings['pngs'])==18
 for name,sha in drawings['cad_sources'].items():assert hashlib.sha256((ROOT/name).read_bytes()).hexdigest()==sha,name+' changed since drawings'
 for row in drawings['pngs']:assert hashlib.sha256((ROOT/'output/drawings'/row['file']).read_bytes()).hexdigest()==row['sha256']
 assert all(hashlib.sha256(p.read_bytes()).hexdigest()==initial_hashes[str(p.relative_to(ROOT))] for p in inputs),'Design changed while checks ran'
 results.append('18 PNGs: current bytes and CAD source hashes verified')
 report={'all_pass':True,'revision':'C','checks':results,'source_sha256':initial_hashes,'physical_validation':False}
 (ROOT/'docs/verification.json').write_text(json.dumps(report,indent=2))
 print('\n'.join(results));print('PASS: all digital package checks; physical build tests remain unverified')
if __name__=='__main__':
 check_purchased_bom() if '--bom-only' in sys.argv else main()
