"""Export bounded OpenSCAD jobs, then verify actual STL geometry."""
import argparse, csv, json, os, shutil, subprocess
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor, as_completed
import trimesh
ROOT = Path(__file__).resolve().parents[1]
PARTS = {
 'coupon':(1,'PETG'), 'body_quarter':(4,'PLA'), 'body_upper_quarter':(4,'PLA'), 'frame_quarter':(12,'PETG'),
 'splice':(24,'PETG'), 'body_post':(4,'PETG'), 'head_support':(4,'PETG'), 'top_post':(4,'PETG'),
 'foot_deck':(3,'PETG'), 'foot_cover':(2,'PLA'), 'motor_cradle':(6,'PETG'),
 'leg_segment':(4,'PETG'), 'shoulder_bridge':(2,'PETG'), 'shoulder_cap':(2,'PLA'),
 'rear_bracket':(1,'PETG'), 'rear_attach':(1,'PETG'), 'bearing_tower':(2,'PETG'),
 'bearing_cap':(2,'PETG'), 'race_spacer':(2,'PETG'), 'spindle_sleeve':(1,'PETG'),
 'gear_hub':(2,'PETG'), 'servo_pinion':(2,'PETG'), 'servo_mount':(2,'PETG'), 'servo_shim_1':(2,'PETG'),'servo_shim_2':(2,'PETG'),'servo_shim_4':(2,'PETG'),
 'head_deck':(1,'PETG'), 'neck':(1,'PLA'), 'head_plate':(1,'PETG'),
 'dome_spacer':(4,'PETG'), 'dome':(1,'PLA'), 'eye':(1,'PLA'), 'detail_panel':(4,'PLA'),
 'battery_tray':(1,'PETG'), 'utility_deck':(1,'PETG'), 'deck_adapter':(2,'PETG'),
 'pcb_spacer':(32,'PETG'), 'speaker_mount':(1,'PETG'), 'switch_plate':(1,'PETG')}
EXE=os.environ.get('OPENSCAD') or shutil.which('openscad') or r'C:\Program Files\OpenSCAD\openscad.com'
def export(name):
 result=subprocess.run([EXE,'--export-format','binstl','-o',str(ROOT/'stl'/f'{name}.stl'),'-D',f'part="{name}"',str(ROOT/'cad/r2d2.scad')],capture_output=True,text=True,timeout=180)
 if result.returncode or 'ERROR:' in result.stderr: raise RuntimeError(name+': '+result.stderr)
 print('Exported '+name,flush=True)
def validate():
 rows=[]
 for name,(quantity,material) in PARTS.items():
  m=trimesh.load_mesh(ROOT/'stl'/f'{name}.stl',process=True)
  components=sum(s.volume>0 for s in m.split(only_watertight=False))
  okay=bool(m.is_watertight and m.is_winding_consistent and m.volume>0 and components==1 and all(m.extents<=300.001))
  rows.append(dict(part=name,quantity=quantity,material=material,x_mm=round(float(m.extents[0]),2),y_mm=round(float(m.extents[1]),2),z_mm=round(float(m.extents[2]),2),solid_mass_g=round(float(m.volume)/1000*(1.27 if material=='PETG' else 1.24),2),watertight=bool(m.is_watertight),components=int(components),passed=okay))
 with (ROOT/'bom/printed-parts.csv').open('w',newline='') as f:
  w=csv.DictWriter(f,fieldnames=rows[0]);w.writeheader();w.writerows(rows)
 report=dict(parts=len(rows),pieces=sum(r['quantity'] for r in rows),all_pass=all(r['passed'] for r in rows),solid_material_bound_g=round(sum(r['solid_mass_g']*r['quantity'] for r in rows),1),rows=rows)
 (ROOT/'cad/validation.json').write_text(json.dumps(report,indent=2))
 print(json.dumps({k:v for k,v in report.items() if k!='rows'}))
 if not report['all_pass']: raise SystemExit('Failed meshes: '+','.join(r['part'] for r in rows if not r['passed']))
def views():
 for name,camera in [('assembly','850,1050,760,0,0,300'),('rear','800,-1050,700,0,0,280'),('section','850,1000,700,0,0,300'),('exploded','850,1100,900,0,0,350')]:
  r=subprocess.run([EXE,'-o',str(ROOT/'cad'/f'{name}.png'),'--imgsize=1400,1400','--colorscheme=Tomorrow','--projection=o','--viewall','--autocenter',f'--camera={camera}','-D',f'part="{name if name != "rear" else "assembly"}"',str(ROOT/'cad/r2d2.scad')],capture_output=True,text=True,timeout=180)
  if r.returncode: raise RuntimeError(r.stderr)
  print('Rendered '+name,flush=True)
if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('--check-only',action='store_true');p.add_argument('--views',action='store_true');p.add_argument('--part');a=p.parse_args()
 for d in ['stl','bom','cad']:(ROOT/d).mkdir(exist_ok=True)
 if a.views:views()
 elif a.part:export(a.part)
 else:
  if not a.check_only:
   with ThreadPoolExecutor(max_workers=3) as pool:
    for f in as_completed([pool.submit(export,n) for n in PARTS]):f.result()
  validate()
