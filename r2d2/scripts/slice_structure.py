"""Slice all ten revision C prints with installed H2D profiles.
No printer connection; settings and generated G-code stay in temporary storage.
"""
from pathlib import Path
import hashlib,json,os,subprocess,tempfile,zipfile
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
def main():
 settings={k:flatten(k,n) for k,n in [('machine','Bambu Lab H2D 0.4 nozzle'),('process','0.20mm Standard @BBL H2D'),('filament','Generic PETG @BBL H2D')]}
 overrides={'wall_loops':'4','top_shell_layers':'5','bottom_shell_layers':'5','sparse_infill_density':'20%','sparse_infill_pattern':'gyroid','enable_support':'1','support_type':'normal(auto)','support_on_build_plate_only':'0','brim_type':'outer_only','brim_width':'5'}
 settings['process'].update(overrides);rows=[]
 for part,(_,material) in PARTS.items():
  settings['filament']=flatten('filament',f'Generic {material} @BBL H2D')
  with tempfile.TemporaryDirectory(prefix='r2-structure-') as name:
   tmp=Path(name).resolve();assert tmp.parent==Path(tempfile.gettempdir()).resolve()
   for kind,data in settings.items():(tmp/(kind+'.json')).write_text(json.dumps(data))
   env=os.environ.copy();env['APPDATA']=str(tmp/'app');env['LOCALAPPDATA']=str(tmp/'local');(tmp/'state').mkdir()
   args=[r'C:\Program Files\Bambu Studio\bambu-studio.exe','--datadir',str(tmp/'state'),'--arrange','1','--load-settings',str(tmp/'machine.json')+';'+str(tmp/'process.json'),'--load-filaments',str(tmp/'filament.json'),'--curr-bed-type','Textured PEI Plate','--slice','0','--debug','2','--export-3mf',str(tmp/'part.3mf'),str(ROOT/'stl'/f'{part}.stl')]
   si=subprocess.STARTUPINFO();si.dwFlags|=subprocess.STARTF_USESHOWWINDOW;si.wShowWindow=0
   r=subprocess.run(args,cwd=tmp,env=env,stdout=subprocess.PIPE,stderr=subprocess.PIPE,timeout=300,startupinfo=si,creationflags=subprocess.CREATE_NO_WINDOW)
   d=json.loads((tmp/'result.json').read_text());assert r.returncode==0 and d['return_code']==0,(part,d.get('error_string'))
   plate=d['sliced_plates'][0]
   with zipfile.ZipFile(tmp/'part.3mf') as z:assert 'Metadata/plate_1.gcode' in z.namelist()
   rows.append({'part':f'stl/{part}.stl','quantity':PARTS[part][0],'material':material,'sha256':hashlib.sha256((ROOT/'stl'/f'{part}.stl').read_bytes()).hexdigest(),'return_code':d['return_code'],'error_string':d['error_string'],'warning':plate['warning_message'],'predicted_mass_with_support_g':plate['filaments'][0]['total_used_g'],'predicted_time_s':plate['total_predication'],'bbox':plate['objects'][0]['bbox']})
   (ROOT/'cad/h2d-structure-check.json').write_text(json.dumps({'profile':'H2D 0.4mm / 0.20mm / per-part Generic material / Textured PEI','overrides':overrides,'rows':rows,'physical_print':False},indent=2))
   assert not plate['warning_message'],(part,plate['warning_message'])
   print('PASS: H2D '+material+' slice '+part+'; '+str(round(rows[-1]['predicted_mass_with_support_g'],1))+' g including support',flush=True)
if __name__=='__main__':main()
