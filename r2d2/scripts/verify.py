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

def firmware_checks():
 """Revision D controls: host tests, phone UI, DFR0994 pin/wiring agreement and image sizes. Drives no hardware."""
 results=[]
 with tempfile.TemporaryDirectory(prefix='r2-verify-') as tmp:
  env=os.environ.copy();env['PATH']=r'C:\msys64\mingw64\bin;'+env['PATH']
  for name in ['control_test','stance_test']:
   exe=Path(tmp)/(name+'.exe')
   run([r'C:\msys64\mingw64\bin\g++.exe','-std=c++11','-Wall','-Wextra','-Werror','-I','firmware/include',f'firmware/test/{name}.cpp','-o',str(exe)],env=env)
   results.append(run([str(exe)],env=env))
 results.append(run(['node','--check','firmware/data/app.js']) or 'JavaScript syntax: PASS')
 results.append(run(['node','firmware/test/ui_test.js']))
 wires=list(csv.DictReader((ROOT/'electronics/wiring.csv').open(encoding='utf-8')))
 config=(ROOT/'firmware/include/config.h').read_text(encoding='utf-8')
 def pin(name):
  found=re.search(fr'\b{name}=(\d+)\b',config);assert found,name;return int(found.group(1))
 onboard={'LEFT_EN':12,'LEFT_PH':13,'RIGHT_EN':14,'RIGHT_PH':21,'CENTER_EN':9,'CENTER_PH':10,'HEAD_EN':47,'HEAD_PH':11}
 for name,value in onboard.items():assert pin(name)==value,(name,'DFR0994 V1.1.0 onboard motor pin')
 wired={'POST_EXTEND':'U7 pin2 / 1A','POST_RETRACT':'U7 pin5 / 2A','STEER':'U7 pin9 / 3A','LOCK_SERVO':'U7 pin12 / 4A','BCLK':'U8 BCLK','LRCLK':'U8 LRC','AUDIO':'U8 DIN',
  'LIMIT_EXTEND_OPEN':'U7 pin1 / 1OE','LIMIT_RETRACT_OPEN':'U7 pin4 / 2OE','LOCK_NO':'LS_LOCK NO','LOCK_NC':'LS_LOCK NC','POST_POSITION':'ACT purple / pin2','PACK':'R_PACK_TOP 100k pin2','POWER':'R_RUN_TOP 10k pin2'}
 def edge(a,b):assert any({r['source'],r['target']}=={a,b} for r in wires),(a,b)
 for name,other in wired.items():edge(f'U1 GPIO{pin(name)}',other)
 used=[pin(n) for n in list(onboard)+list(wired)]
 assert len(used)==len(set(used)),'GPIO assigned twice'
 gpios={int(g) for r in wires for g in re.findall(r'U1 GPIO(\d+)\b',r['source']+' '+r['target'])}
 assert gpios=={pin(n) for n in wired},gpios
 assert not set(used)&({0,3,19,20,43,44,45,46}|set(range(26,38))),'strapping, USB, UART0, flash or PSRAM pin used'
 for a,b in [('U7 pin3 / 1Y','D5 IN1'),('U7 pin6 / 2Y','D5 IN2'),('U7 pin8 / 3Y','SV1 signal'),('U7 pin11 / 4Y','SV2 signal'),
  ('U7 pin1 / 1OE','LS_EXT COM'),('B1 PP30 -','LS_EXT NC'),('U7 pin4 / 2OE','LS_RET COM'),('B1 PP30 -','LS_RET NC'),('B1 PP30 -','U7 pin10 / 3OE'),('B1 PP30 -','U7 pin13 / 4OE'),
  ('B1 PP30 -','LS_LOCK SS-01GL COM'),('LS_LOCK NO','R_LOCK_NO 3.3k pin1'),('LS_LOCK NC','R_LOCK_NC 3.3k pin1'),
  ('P2 VOUT','D5 DRV8871 VM'),('D5 OUT1','ACT red / pin3'),('D5 OUT2','ACT black / pin4'),('D5 ILIM','R_ILIM 71.5k pin2'),
  ('R_POT_TOP 2.2k pin2','ACT yellow / pin5'),('B1 PP30 -','ACT orange / pin1'),('ACT purple / pin2','R_POT_FAIL 470k pin1'),
  ('S1 output','U1 VIN+ / P23 pin1'),('P1 OUT+','U1 VM+ / P22 pin1'),('P1 OUT+','SV1 steering red'),('P1 OUT+','SV2 lock release red'),
  ('U1 M1 OUT1','M1 red'),('U1 M1 OUT1','M2 red'),('U1 M2 OUT1','M3 red'),('U1 M2 OUT1','M4 red'),('U1 M3 OUT1','M5 red'),('U1 M3 OUT1','M6 red'),('U1 M4 OUT1','M7 red')]:edge(a,b)
 assert not any('VM' in r['target'] and r['source']!='P1 OUT+' and r['net']!='GND' and 'D5' not in r['target'] for r in wires),'Romeo VM fed from anything but the motor regulator'
 assert not any(k in r['source']+' '+r['target'] for r in wires for k in ['HUZZAH','DRV8833','ADS1115','INA219','U9 ','U10 ','J_USB','D1 ','D4 ','5V_Servo'])
 assert 14.6*22/122<2.9 and 6.0*10/20<3.3 and 5.5*10/20>.75*3.3 and 3300*16.5/(16.5+2.2)<3000
 assert len(wires)==98,len(wires)
 results.append(f'{len(wires)} wiring rows: DFR0994 pins match config.h, gated NC post limits, NO/NC lock sensor, P16 feedback, isolated VM and divider bounds PASS')
 fs=ROOT/'firmware/.pio/build/romeo/littlefs.bin';fw=ROOT/'firmware/.pio/build/romeo/firmware.bin'
 assert fs.exists() and fs.stat().st_size<=2097152 and fw.exists() and fw.stat().st_size<=2031616,'run pio run and pio run -t buildfs first'
 results.append(f'Firmware image {fw.stat().st_size} bytes; filesystem image {fs.stat().st_size} bytes: fit partitions')
 return results

def main():
 from package import cli_revision,path as release_path;revision=cli_revision(sys.argv)
 (ROOT/'docs/verification.json').write_text(json.dumps({'all_pass':False,'revision':'D-development','status':'checks in progress; complete purchased-piece ledger required','physical_validation':False},indent=2))
 if '--cad-only' not in sys.argv:check_purchased_bom()
 inputs=sorted((ROOT/'cad').glob('*.scad'))+sorted((ROOT/'stl').glob('*.stl'))+sorted((ROOT/'firmware/include').glob('*.h'))+[ROOT/'firmware/src/main.cpp',ROOT/'firmware/data/app.js',ROOT/'electronics/wiring.csv',ROOT/'bom/fastener-stacks.csv']+[ROOT/'scripts'/n for n in ['verify.py','check_kinematics.py','export_cad.py','slice_structure.py']]
 initial_hashes={str(p.relative_to(ROOT)):hashlib.sha256(p.read_bytes()).hexdigest() for p in inputs}
 results=[];validate();results.append('STL geometry: all meshes closed, connected, positive and inside300mm; nonnegative bed Z')
 results.extend(cad_checks())
 if '--cad-only' in sys.argv:
  (ROOT/'docs/verification.json').write_text(json.dumps({'all_pass':False,'revision':revision,'cad_checks_pass':True,'checks':results,'status':'other package checks pending','physical_validation':False},indent=2));return
 results.append(run([sys.executable,'scripts/check_kinematics.py']))
 results.append(nut_pocket_checks())
 stacks=list(csv.DictReader((ROOT/'bom/fastener-stacks.csv').open()))
 for r in stacks:
  remaining=float(r['length_mm'])-float(r['grip_mm'])-float(r['washer_mm'])
  if r['kind']=='through':assert remaining-float(r['nut_mm'])>=float(r['min_extra_mm'])-1e-6,r['joint']
  else:assert float(r['min_thread_mm'])-1e-6<=remaining<=float(r['usable_thread_mm'])-.25+1e-6,r['joint']
 assert 15.4*3**.5/2>=13.25 and 6.8*3**.5/2>=5.75
 results.append('22 fastener stacks: nut engagement, blind-depth margins and hex-pocket across-flats checks PASS')
 results.extend(firmware_checks())
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
 delivery=release_path(revision,'delivery');video=json.loads((delivery/'video.json').read_text())
 assert hashlib.sha256((delivery/'motion.mp4').read_bytes()).hexdigest()==video['sha256']
 for name,sha in video['source_sha256'].items():assert hashlib.sha256((ROOT/name).read_bytes()).hexdigest()==sha,name+' changed since video render'
 results.append('30-second CAD video: encoded bytes and source hashes match')
 drawing_dir=release_path(revision,'drawings');drawings=json.loads((drawing_dir/'index.json').read_text())
 assert drawings['revision']==revision and drawings['pngs'],f'{drawing_dir} is not a revision {revision} drawing set'
 for name,sha in drawings['cad_sources'].items():assert hashlib.sha256((ROOT/name).read_bytes()).hexdigest()==sha,name+' changed since drawings'
 for row in drawings['pngs']:assert hashlib.sha256((drawing_dir/row['file']).read_bytes()).hexdigest()==row['sha256']
 assert all(hashlib.sha256(p.read_bytes()).hexdigest()==initial_hashes[str(p.relative_to(ROOT))] for p in inputs),'Design changed while checks ran'
 results.append(f"{len(drawings['pngs'])} revision {revision} PNGs: current bytes and CAD source hashes verified")
 report={'all_pass':True,'revision':revision,'checks':results,'source_sha256':initial_hashes,'physical_validation':False}
 (ROOT/'docs/verification.json').write_text(json.dumps(report,indent=2))
 print('\n'.join(results));print('PASS: all digital package checks; physical build tests remain unverified')
if __name__=='__main__':
 if '--bom-only' in sys.argv:check_purchased_bom()
 elif '--firmware-only' in sys.argv:
  print('\n'.join(firmware_checks()));print('PASS: firmware host tests, phone UI, DFR0994 wiring and image checks; no hardware was driven')
 else:main()
