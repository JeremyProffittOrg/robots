"""Export and validate the ten FACET-1 designs. Existing OpenSCAD/trimesh only."""
import argparse
import csv
import json
import os
from pathlib import Path
import shutil
import subprocess
from concurrent.futures import ThreadPoolExecutor, as_completed

ROOT = Path(__file__).resolve().parents[1]
PARTS = {
    "01_base": (1, "PETG", "Floor down; single nozzle", "Diameter300 circular unibody;6mm floor;4mm wall/ribs;6walls6top/bottom40%gyroid;8mmbrim;normal auto supports for captured pockets and ledges;clear through wheel wells"),
    "02_skirt": (1, "PLA", "Large opening down", "Twelve full-height planar faces;linear300-to220mm vertex-diameter taper over210mm plus3mm register;four hemisphere rows;faceted240mm-clear rib;captured M4 nuts;4walls15%infill;normal auto supports"),
    "04_shoulder": (1, "PETG", "Bottom flange down", "Shoulder and neck one print; concealed compact servo boxes; integrated bearing tower and fixed friction deck; assemble through open bottom before seating;4walls25%infill;normal auto supports"),
    "06_head": (1, "PLA", "Drum rim down", "Dome eye discs tilted lamps hub friction drum spokes integrated; normal auto supports inside dome under eye and hub;4walls15%infill"),
    "07_pitch_carrier": (2, "PETG", "Floor down", "Print this same file twice;4walls30%infill; actual horn and servo fit gate"),
    "08_plunger_arm": (1, "PLA", "As exported; ensure on bed", "Spherical root and telescoping rings integrated; support cup and root; supplied servo horn; decorative arm only"),
    "09_emitter_arm": (1, "PLA", "As exported; ensure on bed", "Spherical root eight rods muzzle rings integrated; normal auto supports; supplied servo horn; decorative arm only"),
    "10_head_motor_carriage": (1, "PETG", "Floor down", "Radial slots padded TT saddle and cable-tie slots;4walls30%infill"),
    "11_motor_clamp": (4, "PETG", "As exported", "Four identical hook clamps;one M3 screw each;omit all four clamps for alternative two-ties-per-motor retention;4walls30%infill"),
    "12_electronics_platform": (1, "PETG", "Deck down; legs up", "One216mm platform with integral legs above battery;invert for assembly;6mm deck;4walls30%infill;four feet retained by screws or ties"),
}

def openscad_path():
    candidates = [os.environ.get("OPENSCAD"), r"C:\Program Files\OpenSCAD\openscad.exe", shutil.which("openscad")]
    return next((str(p) for p in candidates if p and Path(p).exists()), None)

def export_one(name, executable):
    target = ROOT / "stl" / f"{name}.stl"
    startup=None
    if os.name=="nt":
        startup=subprocess.STARTUPINFO();startup.dwFlags|=subprocess.STARTF_USESHOWWINDOW
    command=[executable,"--export-format","binstl","-o",str(target),"-D",f'part="{name}"',str(ROOT/"cad/dalek.scad")]
    process=subprocess.Popen(command,stdout=subprocess.PIPE,stderr=subprocess.PIPE,text=True,startupinfo=startup)
    timeout=600 if name=="02_skirt" else 240
    print(f"START {target.name}: PID {process.pid}; {timeout}s timeout",flush=True)
    try:stdout,stderr=process.communicate(timeout=timeout)
    except subprocess.TimeoutExpired:
        process.kill();process.communicate();raise
    if process.returncode or not target.exists() or "ERROR:" in stderr:
        raise RuntimeError(f"{target.name}: {stderr}")
    return name

def validate():
    import trimesh
    expected={name+".stl" for name in PARTS}
    found={p.name for p in (ROOT/"stl").glob("*.stl")}
    if found != expected: raise SystemExit(f"STL inventory mismatch: extra={sorted(found-expected)} missing={sorted(expected-found)}")
    rows=[]
    for name,(qty,material,orientation,notes) in PARTS.items():
        mesh=trimesh.load_mesh(ROOT/"stl"/f"{name}.stl",process=True)
        size=mesh.extents;surfaces=mesh.split(only_watertight=False)
        components=int(sum(m.volume>0 for m in surfaces))
        brim=8 if name=="01_base" else 5
        rotation=0
        print_size=size[[1,0,2]] if rotation else size
        fit=bool(print_size[0]+2*brim<=325.001 and print_size[1]+2*brim<=320.001 and print_size[2]<=325.001)
        okay=bool(mesh.is_watertight and mesh.is_winding_consistent and mesh.volume>0 and components==1 and fit)
        rows.append(dict(part=name,quantity=qty,material=material,x_mm=round(float(size[0]),3),y_mm=round(float(size[1]),3),z_mm=round(float(size[2]),3),volume_mm3=round(float(mesh.volume),2),solid_mass_g=round(float(mesh.volume)/1000*(1.27 if material=="PETG" else 1.24),2),watertight=bool(mesh.is_watertight),connected_components=components,enclosed_void_surfaces=int(sum(m.volume<0 for m in surfaces)),brim_mm_per_side=brim,print_rotation_z_degrees=rotation,h2d_single_nozzle_with_brim=fit,pass_check=okay,orientation=orientation,notes=notes))
    with (ROOT/"bom/printed-parts.csv").open("w",newline="",encoding="utf-8") as f:
        writer=csv.DictWriter(f,fieldnames=rows[0].keys(),lineterminator="\n");writer.writeheader();writer.writerows(rows)
    report={"design":"FACET-1","mesh_count":len(rows),"maximum_stl_files":10,"all_pass":all(r["pass_check"] for r in rows) and len(rows)<=10,"printed_piece_count":sum(r["quantity"] for r in rows),"printed_piece_count_motor_tie_option":sum(r["quantity"] for r in rows if r["part"]!="11_motor_clamp"),"solid_material_upper_bound_g":round(sum(r["quantity"]*r["solid_mass_g"] for r in rows),1),"bed_envelope_mm":[325,320,325],"body_height_limit_with_5mm_margin_mm":320,"base_brim_envelope_mm":[316,316],"base_print_rotation_z_degrees":0,"nozzle_mode":"single","physical_fit_verified":False,"physical_strength_verified":False,"parts":rows}
    (ROOT/"cad/validation.json").write_text(json.dumps(report,indent=2)+"\n",encoding="utf-8")
    print(json.dumps({k:v for k,v in report.items() if k!="parts"},indent=2),flush=True)
    bad=[r["part"] for r in rows if not r["pass_check"]]
    if bad:raise SystemExit("FAILED meshes: "+", ".join(bad))

def main():
    parser=argparse.ArgumentParser();parser.add_argument("--check-only",action="store_true");parser.add_argument("--parts",nargs="+");parser.add_argument("--jobs",type=int,default=3);args=parser.parse_args()
    if not args.check_only:
        executable=openscad_path()
        if not executable:raise SystemExit("OpenSCAD executable not found; set OPENSCAD")
        names=args.parts or list(PARTS)
        if set(names)-set(PARTS):raise SystemExit("Unknown parts")
        with ThreadPoolExecutor(max_workers=args.jobs) as pool:
            tasks={pool.submit(export_one,n,executable):n for n in names}
            for done in as_completed(tasks):print("EXPORTED "+done.result(),flush=True)
    if not args.parts:validate()

if __name__=="__main__":main()
