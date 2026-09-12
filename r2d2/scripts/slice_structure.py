"""Slice all ten revision C prints with installed H2D profiles.
No printer connection; settings and generated G-code stay in temporary storage.
"""
from pathlib import Path
import hashlib,json,os,subprocess,tempfile,zipfile,re,math
from export_cad import PARTS
ROOT=Path(__file__).resolve().parents[1]
PROFILES=Path('C:/Program Files/Bambu Studio/resources/profiles/BBL')
def flatten(kind,name,seen=()):
 if name in seen:raise ValueError('Profile inheritance cycle')
 own=json.loads((PROFILES/kind/(name+'.json')).read_text(encoding='utf-8-sig'));result={}
 if own.get('inherits'):result.update(flatten(kind,own['inherits'],seen+(name,)))
 includes=own.get('include',[])
 if isinstance(includes,str):includes=[includes]
 for item in includes:result.update(flatten(kind,item,seen+(name,)))
 result.update({k:v for k,v in own.items() if k not in ('inherits','include')});return result

def extrusion_masses(gcode):
 current={'X':0.,'Y':0.,'E':0.};absolute=True;xy_absolute=True;started=False;feature='Custom';lengths={}
 for line in gcode.splitlines():
  if line.startswith('; CHANGE_LAYER'):started=True
  if line.startswith('; FEATURE: '):feature=line.split(': ',1)[1]
  text=line.split(';',1)[0].strip()
  if not text:continue
  cmd=text.split()[0];v={k:float(n) for k,n in re.findall(r'([XYE])\s*(-?(?:\d+(?:\.\d*)?|\.\d+))',text)}
  if cmd=='M82':absolute=True
  elif cmd=='M83':absolute=False
  elif cmd=='G90':xy_absolute=True
  elif cmd=='G91':xy_absolute=False
  elif cmd=='G92':current.update(v)
  elif cmd in ['G0','G1','G2','G3']:
   before=current.copy()
   for k,n in v.items():current[k]=n if (absolute if k=='E' else xy_absolute) else current[k]+n
   amount=current['E']-before['E'];moving=any(abs(current[k]-before[k])>1e-8 for k in ['X','Y']) or cmd in ['G2','G3']
   if started and moving and amount>0 and feature not in ['Custom','Flush']:lengths[feature]=lengths.get(feature,0)+amount
 density=re.search(r'^; filament_density\s*[:=]\s*([0-9.]+)',gcode,re.M)
 diameter=re.search(r'^; filament_diameter\s*[:=]\s*([0-9.]+)',gcode,re.M)
 assert density and diameter and lengths,'Missing extrusion/filament metadata'
 factor=math.pi*(float(diameter[1])/2)**2*float(density[1])/1000
 masses={k:v*factor for k,v in lengths.items()}
 support=sum(v for k,v in masses.items() if k.startswith('Support'))
 brim=sum(v for k,v in masses.items() if k in ['Brim','Skirt'])
 return {'installed_model_g':round(sum(masses.values())-support-brim,3),'support_g':round(support,3),'brim_g':round(brim,3),
         'gcode_sha256':hashlib.sha256(gcode.encode()).hexdigest(),
         'method':'Positive filament on XY-moving labelled paths; excludes machine Custom/Flush and stationary unretraction; profile density; not a physical mass measurement'}
def main():
 settings={k:flatten(k,n) for k,n in [('machine','Bambu Lab H2D 0.4 nozzle'),('process','0.20mm Standard @BBL H2D'),('filament','Generic PETG @BBL H2D')]}
 overrides={'wall_loops':'4','top_shell_layers':'5','bottom_shell_layers':'5','sparse_infill_density':'20%','sparse_infill_pattern':'gyroid','enable_support':'1','support_type':'normal(auto)','support_on_build_plate_only':'0','brim_type':'outer_only','brim_width':'5'}
 settings['process'].update(overrides);rows=[]
 report_path=ROOT/'cad/h2d-structure-check.json'
 cached={Path(r['part']).stem:r for r in json.loads(report_path.read_text()).get('rows',[])} if report_path.exists() else {}
 for part,(_,material) in PARTS.items():
  settings['filament']=flatten('filament',f'Generic {material} @BBL H2D')
  profile_sha=hashlib.sha256(json.dumps(settings,sort_keys=True).encode()).hexdigest()
  mesh_sha=hashlib.sha256((ROOT/'stl'/f'{part}.stl').read_bytes()).hexdigest()
  if part in cached and cached[part].get('profile_sha256')==profile_sha and cached[part]['sha256']==mesh_sha and 'installed_model_g' in cached[part]:
   rows.append(cached[part]);print('Retained verified unchanged H2D slice '+part,flush=True);continue
  with tempfile.TemporaryDirectory(prefix='r2-structure-') as name:
   tmp=Path(name).resolve();assert tmp.parent==Path(tempfile.gettempdir()).resolve()
   for kind,data in settings.items():(tmp/(kind+'.json')).write_text(json.dumps(data))
   env=os.environ.copy();env['APPDATA']=str(tmp/'app');env['LOCALAPPDATA']=str(tmp/'local');(tmp/'state').mkdir()
   args=[r'C:\Program Files\Bambu Studio\bambu-studio.exe','--datadir',str(tmp/'state'),'--arrange','1','--load-settings',str(tmp/'machine.json')+';'+str(tmp/'process.json'),'--load-filaments',str(tmp/'filament.json'),'--curr-bed-type','Textured PEI Plate','--slice','0','--debug','2','--export-3mf',str(tmp/'part.3mf'),str(ROOT/'stl'/f'{part}.stl')]
   si=subprocess.STARTUPINFO();si.dwFlags|=subprocess.STARTF_USESHOWWINDOW;si.wShowWindow=0
   r=subprocess.run(args,cwd=tmp,env=env,stdout=subprocess.PIPE,stderr=subprocess.PIPE,timeout=300,startupinfo=si,creationflags=subprocess.CREATE_NO_WINDOW)
   d=json.loads((tmp/'result.json').read_text());assert r.returncode==0 and d['return_code']==0,(part,d.get('error_string'))
   plate=d['sliced_plates'][0]
   with zipfile.ZipFile(tmp/'part.3mf') as z:
    assert 'Metadata/plate_1.gcode' in z.namelist();usage=extrusion_masses(z.read('Metadata/plate_1.gcode').decode())
   rows.append({'part':f'stl/{part}.stl','quantity':PARTS[part][0],'material':material,'sha256':hashlib.sha256((ROOT/'stl'/f'{part}.stl').read_bytes()).hexdigest(),'return_code':d['return_code'],'error_string':d['error_string'],'warning':plate['warning_message'],'predicted_mass_with_support_g':plate['filaments'][0]['total_used_g'],'predicted_time_s':plate['total_predication'],'bbox':plate['objects'][0]['bbox']})
   rows[-1].update(usage);rows[-1]['profile_sha256']=profile_sha
   (ROOT/'cad/h2d-structure-check.json').write_text(json.dumps({'profile':'H2D 0.4mm / 0.20mm / per-part Generic material / Textured PEI','overrides':overrides,'rows':rows,'physical_print':False},indent=2))
   assert not plate['warning_message'],(part,plate['warning_message'])
   print('PASS: H2D '+material+' slice '+part+'; '+str(round(rows[-1]['predicted_mass_with_support_g'],1))+' g including support',flush=True)
 report_path.write_text(json.dumps({'profile':'H2D0.4mm /0.20mm / per-part Generic material / Textured PEI','overrides':overrides,'rows':rows,'physical_print':False},indent=2))
 print('Installed-model prediction: '+str(round(sum(r['installed_model_g']*r['quantity'] for r in rows),1))+' g',flush=True)
if __name__=='__main__':main()
