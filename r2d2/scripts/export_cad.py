"""Export bounded OpenSCAD jobs, then verify actual STL geometry."""
import argparse, csv, hashlib, json, os, shutil, subprocess
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor, as_completed
import trimesh
ROOT = Path(__file__).resolve().parents[1]
PARTS = {'body_lower':(1,'PETG'),'body_upper':(1,'PETG'),'dome':(1,'PLA'),
 'leg':(2,'PETG'),'outer_foot':(2,'PETG'),'rear_foot':(1,'PETG'),
 'drive_cassette':(3,'PETG'),'head_motor_mount':(1,'PETG'),
 'bearing_tower':(1,'PETG'),'bearing_cap':(1,'PETG')}
DEVELOPMENT_PARTS = {'frame_chassis':1,'rail_key':4,'rail_key_pin':4,
 'outer_foot_core':2,'center_foot_core':1,'post_adapter':1}
EXE=os.environ.get('OPENSCAD') or shutil.which('openscad') or r'C:\Program Files\OpenSCAD\openscad.com'
def export(name):
 folder=ROOT/'stl'/'development' if name in DEVELOPMENT_PARTS else ROOT/'stl'
 folder.mkdir(parents=True,exist_ok=True)
 result=subprocess.run([EXE,'--export-format','binstl','-o',str(folder/f'{name}.stl'),'-D',f'part="{name}"',str(ROOT/'cad/r2d2.scad')],capture_output=True,text=True,timeout=600)
 if result.returncode or 'ERROR:' in result.stderr: raise RuntimeError(name+': '+result.stderr)
 print('Exported '+name,flush=True)
def validate():
 rows=[]
 for name,(quantity,material) in PARTS.items():
  m=trimesh.load_mesh(ROOT/'stl'/f'{name}.stl',process=True)
  components=sum(s.volume>0 for s in m.split(only_watertight=False))
  okay=bool(m.is_watertight and m.is_winding_consistent and m.volume>0 and components==1 and all(m.extents<=300.001) and m.bounds[0,2]>=-.001)
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
def validate_development():
 rows=[]
 for name,quantity in DEVELOPMENT_PARTS.items():
  p=ROOT/'stl/development'/f'{name}.stl';mesh=trimesh.load_mesh(p,process=True)
  solids=sum(s.volume>0 for s in mesh.split(only_watertight=False))
  passed=bool(mesh.is_watertight and mesh.is_winding_consistent and mesh.volume>0 and solids==1
              and all(mesh.extents<=300.001) and abs(mesh.bounds[0,2])<=.001)
  rows.append({'part':name,'development_quantity':quantity,'closed':bool(mesh.is_watertight),
   'positive_solids':int(solids),'dimensions_mm':[round(float(v),3) for v in mesh.extents],
   'bed_min_z_mm':round(float(mesh.bounds[0,2]),6),'sha256':hashlib.sha256(p.read_bytes()).hexdigest(),'passed':passed})
 report={'revision':'D-development','geometry_pass':all(r['passed'] for r in rows),'fabrication_release':False,
  'full_robot_integration_verified':False,'physical_load_tested':False,'purchased_piece_limit':99,
  'purchased_piece_limit_verified':False,'rows':rows}
 (ROOT/'cad/development-check.json').write_text(json.dumps(report,indent=2))
 assert report['geometry_pass'],[r['part'] for r in rows if not r['passed']]
 print(f'PASS: {len(rows)} development STL designs are closed single solids, on the bed and within300mm per axis')
 print('Not a fabrication release: assembly, H2D slicing, load and99-piece checks remain incomplete.')
if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('--check-only',action='store_true');p.add_argument('--check-development',action='store_true');p.add_argument('--views',action='store_true');p.add_argument('--part');a=p.parse_args()
 for d in ['stl','bom','cad']:(ROOT/d).mkdir(exist_ok=True)
 if a.check_development:validate_development()
 elif a.views:views()
 elif a.part:export(a.part)
 else:
  if not a.check_only:
   with ThreadPoolExecutor(max_workers=3) as pool:
    for f in as_completed([pool.submit(export,n) for n in PARTS]):f.result()
  validate()
