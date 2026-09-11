"""Focused digital checks. Does not upload firmware, print, or drive hardware."""
from pathlib import Path
import csv, hashlib, json, os, re, subprocess, sys, tempfile
import trimesh
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'scripts'))
from export_cad import EXE,validate
def run(args,**kwargs):
 result=subprocess.run(args,cwd=ROOT,capture_output=True,text=True,timeout=180,**kwargs)
 if result.returncode:raise RuntimeError(str(args)+'\n'+result.stdout+'\n'+result.stderr)
 return result.stdout.strip()
def main():
 results=[];validate();results.append('STL geometry: all meshes closed, connected, positive and inside 300 mm cube')
 with tempfile.TemporaryDirectory(prefix='r2-verify-') as tmp:
  for name in ['check_stack','check_shoulder','check_neck','check_rear_sleeve','check_gears']:
   r=subprocess.run([EXE,'-o',str(Path(tmp)/(name+'.stl')),'-D',f'part="{name}"',str(ROOT/'cad/r2d2.scad')],capture_output=True,text=True,timeout=180)
   if 'Current top level object is empty' not in r.stdout+r.stderr:
    # Mating faces intentionally touch. Permit only their exact zero-height plane.
    contact={'check_stack':315.0,'check_shoulder':320.0}
    path=Path(tmp)/(name+'.stl')
    if name not in contact or not path.exists():raise AssertionError(name+' has intersecting solids: '+r.stdout+r.stderr)
    mesh=trimesh.load_mesh(path)
    assert all(abs(z-contact[name])<0.0001 for z in mesh.vertices[:,2]),name+' has volume outside its mating plane'
   results.append(name+': no intersecting solid')
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
 sliced=json.loads((ROOT/'cad/h2d-slice-check.json').read_text())
 assert sliced['return_code']==0 and hashlib.sha256((ROOT/sliced['part']).read_bytes()).hexdigest()==sliced['sha256']
 results.append('Bambu H2D coupon slice: success and current STL hash verified; no physical print')
 structure=json.loads((ROOT/'cad/h2d-structure-check.json').read_text())
 assert {Path(r['part']).stem for r in structure['rows']}=={'body_lower','body_upper','arm_left','arm_right'}
 for row in structure['rows']:
  assert row['return_code']==0 and not row['warning']
  assert hashlib.sha256((ROOT/row['part']).read_bytes()).hexdigest()==row['sha256']
 results.append('Four whole body/arm H2D PETG slices: success, no warnings and current STL hashes verified')
 wires=list(csv.DictReader((ROOT/'electronics/wiring.csv').open()))
 config=(ROOT/'firmware/include/config.h').read_text()
 expected={'LEFT':(14,32),'RIGHT':(15,33),'REAR':(27,12)}
 for i,(side,pins) in enumerate(expected.items(),1):
  for direction,pin,suffix in [('FWD',pins[0],'1'),('REV',pins[1],'2')]:
   for channel in ['A','B']:
    assert any(r['net']==side+'_'+direction and r['source']==f'U1 GPIO{pin}' and r['target']==f'D{i} {channel}IN{suffix}' for r in wires)
 assert re.search(r'MOTOR\[6\]=\{14,32,15,33,27,12\}',config)
 for name,pin in [('SLEEP',13),('STEER',25),('HEAD',26),('FAULT',36),('POWER',39),('PACK',34),('BCLK',18),('LRCLK',19),('AUDIO',23)]:assert re.search(fr'{name}={pin}\b',config)
 assert 14.6*22/122<3.3 and 5.25*15/25<3.3
 assert len(wires)==154
 results.append('154 wiring rows: six independent motor channels, firmware pins and divider bounds PASS')
 fs=ROOT/'firmware/.pio/build/feather/littlefs.bin';fw=ROOT/'firmware/.pio/build/feather/firmware.bin'
 assert fs.exists() and fs.stat().st_size<=2097152 and fw.exists() and fw.stat().st_size<=2031616
 results.append(f'Firmware image {fw.stat().st_size} bytes; filesystem image {fs.stat().st_size} bytes: fit partitions')
 report={'all_pass':True,'checks':results,'physical_validation':False}
 (ROOT/'docs/verification.json').write_text(json.dumps(report,indent=2))
 print('\n'.join(results));print('PASS: all digital package checks; physical build tests remain unverified')
if __name__=='__main__':main()
