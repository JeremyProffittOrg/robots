"""Slice current Dalek meshes with isolated installed H2D profiles; no printer access."""
import argparse
from datetime import datetime, timezone
import hashlib
import json
import os
from pathlib import Path
import re
import shutil
import subprocess
import tempfile
import time
import zipfile
import xml.etree.ElementTree as ET

from analyze_gcode import deposition_bounds
from export_cad import PARTS

ROOT = Path(__file__).resolve().parents[1]
PROFILES = Path('C:/Program Files/Bambu Studio/resources/profiles/BBL')
EXE = Path('C:/Program Files/Bambu Studio/bambu-studio.exe')
OUT = ROOT/'cad/h2d-slice-check.json'


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def flatten(kind, name, seen=()):
    if name in seen:
        raise ValueError('Profile inheritance cycle')
    own = json.loads((PROFILES/kind/(name+'.json')).read_text(encoding='utf-8-sig'))
    result = {}
    if own.get('inherits'):
        result.update(flatten(kind, own['inherits'], seen+(name,)))
    includes = own.get('include', [])
    if isinstance(includes, str):
        includes = [includes]
    for item in includes:
        result.update(flatten(kind, item, seen+(name,)))
    result.update({k:v for k,v in own.items() if k not in ('inherits','include')})
    return result


def slice_part(name):
    import trimesh
    quantity, material, orientation, notes = PARTS[name]
    stl = ROOT/'stl'/(name+'.stl')
    digest = sha(stl)
    mesh = trimesh.load_mesh(stl, process=False)
    base = name == '01_base'
    infill = 40 if base else 25 if name == '04_shoulder' else 30 if material == 'PETG' else 15
    overrides = dict(wall_loops='6' if base else '4', top_shell_layers='6' if base else '5',
        bottom_shell_layers='6' if base else '4', sparse_infill_density=f'{infill}%',
        sparse_infill_pattern='gyroid', enable_support='1', support_type='normal(auto)',
        support_on_build_plate_only='0', brim_type='outer_only', brim_width='8' if base else '5',
        skirt_loops='0')
    settings = {'machine':flatten('machine','Bambu Lab H2D 0.4 nozzle'),
        'process':dict(flatten('process','0.20mm Standard @BBL H2D'),**overrides),
        'filament':flatten('filament','Generic PETG @BBL H2D' if material=='PETG' else 'Bambu PLA Basic @BBL H2D')}
    row = dict(part=name, path=f'stl/{name}.stl', sha256=digest, quantity=quantity,
        material=material, process_overrides=overrides, mesh_bounds_mm=mesh.extents.tolist(),
        checked_at_utc=datetime.now(timezone.utc).isoformat(), pass_check=False)
    with tempfile.TemporaryDirectory(prefix='dalek-round-h2d-') as folder:
        tmp = Path(folder).resolve()
        assert tmp.parent == Path(tempfile.gettempdir()).resolve()
        for kind, data in settings.items():
            (tmp/(kind+'.json')).write_text(json.dumps(data),encoding='utf-8')
        row['flattened_profile_sha256']={kind:sha(tmp/(kind+'.json')) for kind in settings}
        env = os.environ.copy()
        env['APPDATA']=str(tmp/'app'); env['LOCALAPPDATA']=str(tmp/'local')
        (tmp/'app').mkdir(); (tmp/'local').mkdir()
        (tmp/'state').mkdir()
        common=[str(EXE),'--datadir',str(tmp/'state'),'--load-settings',str(tmp/'machine.json')+';'+str(tmp/'process.json'),
            '--load-filaments',str(tmp/'filament.json'),'--curr-bed-type','Textured PEI Plate','--debug','2']
        # Supported CLI assembly-list input supplies placement without a native
        # project reload or changing the H2D's machine/nozzle printable areas.
        placement={'plates':[{'plate_name':name,'need_arrange':False,
            'plate_params':{'curr_bed_type':'Textured PEI Plate'},
            'objects':[{'path':str(stl),'count':1,'filaments':[1],
                'pos_x':[float(162.5-mesh.bounds[:,0].mean())],
                'pos_y':[float(160-mesh.bounds[:,1].mean())],
                'pos_z':[float(-mesh.bounds[0,2])]}]}]}
        (tmp/'assemble.json').write_text(json.dumps(placement),encoding='utf-8')
        row['placement_input']=placement
        argv=common+['--load-assemble-list',str(tmp/'assemble.json'),'--ensure-on-bed','--allow-rotations=0','--arrange','0','--slice','0',
            '--export-3mf',str(tmp/'part.3mf')]
        row['argv']=argv
        started=time.monotonic()
        with (tmp/'stdout.txt').open('w') as stdout, (tmp/'stderr.txt').open('w') as stderr:
            process=subprocess.Popen(argv,cwd=tmp,env=env,stdout=stdout,stderr=stderr,creationflags=subprocess.CREATE_NO_WINDOW)
            row['process_id']=process.pid
            print(f'START {name}: PID {process.pid}; 300s timeout',flush=True)
            try:
                row['process_exit_code']=process.wait(timeout=300)
            except subprocess.TimeoutExpired:
                process.kill();process.wait()
                raise RuntimeError(f'{name}: 300s slicing timeout; process terminated')
        row['elapsed_seconds']=round(time.monotonic()-started,2)
        row['slicer_stdout_tail']=(tmp/'stdout.txt').read_text(errors='replace')[-4000:]
        row['slicer_stderr_tail']=(tmp/'stderr.txt').read_text(errors='replace')[-4000:]
        result=json.loads((tmp/'result.json').read_text(encoding='utf-8-sig')) if (tmp/'result.json').exists() else {}
        row['result_code']=result.get('return_code')
        row['error_string']=result.get('error_string')
        if row['process_exit_code'] or row['result_code']!=0:
            diagnostics=Path(tempfile.mkdtemp(prefix='dalek-round-h2d-failed-')).resolve()
            assert diagnostics.parent==Path(tempfile.gettempdir()).resolve()
            for filename in ['machine.json','process.json','filament.json','assemble.json','result.json']:
                if (tmp/filename).exists():shutil.copyfile(tmp/filename,diagnostics/filename)
            row['diagnostic_directory']=str(diagnostics)
            row['diagnostic_argv']=[a.replace(str(tmp),str(diagnostics)) for a in argv]
            (diagnostics/'failure.json').write_text(json.dumps(row,indent=2),encoding='utf-8')
            raise RuntimeError(f'{name}: {json.dumps(row)}')
        plates=result['sliced_plates']
        assert len(plates)==1,name
        plate=plates[0]
        assert not plate.get('warning_message'),plate.get('warning_message')
        objects=plate['objects']; assert len(objects)==1,name
        bbox=objects[0]['bbox']; row['loaded_bbox']=bbox
        assert abs(bbox['z'])<.001 and abs(bbox['height']-mesh.extents[2])<.01,(name,bbox)
        assert abs(bbox['width']-mesh.extents[0])<.01 and abs(bbox['depth']-mesh.extents[1])<.01,(name,bbox)
        assert abs(bbox['x']+bbox['width']/2-162.5)<.01 and abs(bbox['y']+bbox['depth']/2-160)<.01,(name,bbox)
        assert objects[0]['triangle_count']==len(mesh.faces),name
        row['loaded_triangle_count']=objects[0]['triangle_count']
        transforms=[]
        with zipfile.ZipFile(tmp/'part.3mf') as package:
            gcode=package.read('Metadata/plate_1.gcode').decode('utf-8')
            model=ET.fromstring(package.read('3D/3dmodel.model'))
            for element in model.iter():
                if element.get('transform'):
                    values=[float(v) for v in element.get('transform').split()]
                    basis=[values[i:i+3] for i in [0,3,6]]
                    assert all(abs(sum(a*b for a,b in zip(basis[i],basis[j]))-(1 if i==j else 0))<1e-5 for i in range(3) for j in range(3))
                    transforms.append(values)
        row['rigid_model_transforms']=transforms
        config=dict(re.findall(r'^; ([\w]+) = (.*)$',gcode,re.MULTILINE))
        assert config['printer_model']=='Bambu Lab H2D'
        assert config['filament_type']==material
        assert config['extruder_printable_area']=='0x0,325x0,325x320,0x320#25x0,350x0,350x320,25x320'
        assert config['printable_area']=='0x0,350x0,350x320,0x320'
        for key,value in overrides.items():
            assert config[key]==value,(name,key,config[key],value)
        max_z=float(re.search(r'max_z_height: ([0-9.]+)',gcode)[1])
        assert max_z>=mesh.extents[2]-.201,(name,max_z,mesh.extents[2])
        analysis=deposition_bounds(gcode)
        assert analysis['verified'] and 'left' in analysis['single_nozzle_areas_containing_all_paths'],(name,analysis['conservative_bead_bounds_xy_mm'])
        assert abs(analysis['model_deposition_z_range_mm'][1]-mesh.extents[2])<=.201,(name,analysis['model_deposition_z_range_mm'],mesh.extents[2])
        assert config['filament_map']=='1' and config['physical_extruder_map']=='1,0',(name,config['filament_map'],config['physical_extruder_map'])
        assert analysis['tools_in_sliced_features']==['T0'],(name,analysis['tools_in_sliced_features'])
        row['selected_nozzle']='left: logical filament T0 -> filament_map1 -> physical_extruder_map[0]=1'
        row['gcode_extrusion_bounds']=analysis
        row['gcode_sha256']=hashlib.sha256(gcode.encode()).hexdigest()
        row['gcode_verified_config']={k:config[k] for k in sorted(set(overrides)|{'printer_model','filament_type','printable_area','extruder_printable_area','filament_map','physical_extruder_map','print_extruder_id','master_extruder_id'})}
        row['complete_printed_height_verified']=True
        row['filament_mass_g']=sum(f['total_used_g'] for f in plate['filaments'])
        row['total_time_seconds']=plate['total_predication']
        usage=analysis['feature_extrusion_estimates']
        assert abs(row['filament_mass_g']-usage['all_labelled_moving_extrusion_mass_g'])<=max(.1,row['filament_mass_g']*.01)
        row['estimated_installed_printed_model_mass_g']=usage['estimated_installed_printed_model_mass_g']
        assert sha(stl)==digest,name
        with tempfile.NamedTemporaryFile(prefix='dalek-round-h2d-'+name+'-',suffix='.3mf',delete=False) as archive:
            archive_path=Path(archive.name).resolve()
        assert archive_path.parent==Path(tempfile.gettempdir()).resolve()
        shutil.copyfile(tmp/'part.3mf',archive_path)
        row['temporary_slice_archive']=str(archive_path)
        row['temporary_slice_archive_sha256']=sha(archive_path)
        row['pass_check']=True
    print(f"PASS {name}: {row['filament_mass_g']:.1f}g total; {row['estimated_installed_printed_model_mass_g']:.1f}g model; complete height and left nozzle bounds",flush=True)
    return row


def main():
    parser=argparse.ArgumentParser();parser.add_argument('--parts',nargs='+');args=parser.parse_args()
    names=args.parts or list(PARTS)
    assert set(names)<=set(PARTS)
    previous=json.loads(OUT.read_text()) if OUT.exists() else {}
    rows={r['part']:r for r in previous.get('parts',[]) if r['part'] in PARTS and r.get('pass_check') and sha(ROOT/'stl'/(r['part']+'.stl'))==r['sha256']}
    for name in names:
        rows[name]=slice_part(name)
        rows={part:record for part,record in rows.items() if sha(ROOT/record['path'])==record['sha256']}
        ordered=[rows[n] for n in PARTS if n in rows]
        for record in ordered:
            record['generated_brim_and_skirt_mass_g']=record['gcode_extrusion_bounds']['feature_extrusion_estimates']['brim_and_skirt_mass_g']
            record['adhesion_note']=('Slicer generated a brim; the complete model/support/brim deposition footprint is checked.'
                if record['generated_brim_and_skirt_mass_g']>0 else
                'No Brim feature was generated despite the requested brim setting. The measured model/support footprint fits; inspect adhesion in the actual print preparation.')
        report=dict(design='MOUNT-1',checked_at_utc=datetime.now(timezone.utc).isoformat(),
            status='pass' if len(ordered)==len(PARTS) else 'in_progress',
            test_type='Actual isolated Bambu Studio H2D CLI slices; no printer connection or physical print',
            profiles=dict(machine='Bambu Lab H2D 0.4 nozzle',process='0.20mm Standard @BBL H2D',bed='Textured PEI Plate',
                placement='Supported assembly-list input places the complete STL atX162.5,Y160; no arrangement or machine/nozzle geometry overrides'),
            parts=ordered,unique_designs_sliced=len(ordered),printed_piece_quantity=sum(r['quantity'] for r in ordered),
            total_predicted_filament_mass_g=round(sum(r['filament_mass_g']*r['quantity'] for r in ordered),2),
            total_predicted_installed_model_mass_g=round(sum(r['estimated_installed_printed_model_mass_g']*r['quantity'] for r in ordered),2),
            total_predicted_time_seconds=round(sum(r['total_time_seconds']*r['quantity'] for r in ordered),2),physical_verified=False)
        OUT.write_text(json.dumps(report,indent=2)+'\n')
    if not args.parts:
        assert len(rows)==len(PARTS)


if __name__=='__main__':
    main()
