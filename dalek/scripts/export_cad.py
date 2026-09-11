"""Export and validate the ten connected STACK-10 designs. Existing OpenSCAD/trimesh only."""
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
    "01_base": (1, "PETG", "Floor down; single nozzle", "300x280 unibody;6mm floor;4mm wall/ribs;6walls6top/bottom40%gyroid;8mmbrim;tree supports below wheel-well roofs;remove through bottom wells"),
    "02_lower_skirt": (1, "PLA", "Large opening down", "Complete360degree ring; integrated bumps;3mm registry above110mm body;4walls15%infill"),
    "03_upper_skirt": (1, "PLA", "Large opening down", "Complete360degree ring; integral bumps;3mm registry above100mm body;4walls15%infill"),
    "04_shoulder": (1, "PETG", "Bottom flange down", "Integral arm shelves and rear display frame; tree supports under shelves;4walls25%infill"),
    "05_neck": (1, "PETG", "Bottom flange down", "Integrated rings posts bearing tower servo mount; support deck underside;4walls30%infill"),
    "06_head": (1, "PLA", "Hub foot down", "Dome eye lamps hub pulley spokes integrated; tree supports inside dome under eye and pulley;4walls15%infill"),
    "07_pitch_carrier": (2, "PETG", "Floor down", "Print this same file twice;4walls30%infill; actual horn and servo fit gate"),
    "08_plunger_arm": (1, "PLA", "As exported", "Support cup underside; supplied servo horn; decorative arm only"),
    "09_emitter_arm": (1, "PLA", "As exported", "Support rods underside; supplied servo horn; decorative arm only"),
    "10_servo_pulley": (1, "PETG", "Large rim down", "Supplied horn;3mm round belt;4walls30%infill"),
}

def openscad_path():
    candidates = [os.environ.get("OPENSCAD"), r"C:\Program Files\OpenSCAD\openscad.exe", shutil.which("openscad")]
    return next((str(p) for p in candidates if p and Path(p).exists()), None)

def export_one(name, executable):
    target = ROOT / "stl" / f"{name}.stl"
    startup=None
    if os.name=="nt":
        startup=subprocess.STARTUPINFO();startup.dwFlags|=subprocess.STARTF_USESHOWWINDOW
    result = subprocess.run([executable, "--export-format", "binstl", "-o", str(target), "-D", f'part="{name}"', str(ROOT / "cad/dalek.scad")], capture_output=True, text=True, timeout=240, startupinfo=startup)
    if result.returncode or not target.exists() or "ERROR:" in result.stderr:
        raise RuntimeError(f"{name}: {result.stderr}")
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
        fit=bool(size[0]+2*brim<=325.001 and size[1]+2*brim<=320.001 and size[2]<=325.001)
        okay=bool(mesh.is_watertight and mesh.is_winding_consistent and mesh.volume>0 and components==1 and fit)
        rows.append(dict(part=name,quantity=qty,material=material,x_mm=round(float(size[0]),3),y_mm=round(float(size[1]),3),z_mm=round(float(size[2]),3),volume_mm3=round(float(mesh.volume),2),solid_mass_g=round(float(mesh.volume)/1000*(1.27 if material=="PETG" else 1.24),2),watertight=bool(mesh.is_watertight),connected_components=components,enclosed_void_surfaces=int(sum(m.volume<0 for m in surfaces)),brim_mm_per_side=brim,h2d_single_nozzle_with_brim=fit,pass_check=okay,orientation=orientation,notes=notes))
    with (ROOT/"bom/printed-parts.csv").open("w",newline="",encoding="utf-8") as f:
        writer=csv.DictWriter(f,fieldnames=rows[0].keys());writer.writeheader();writer.writerows(rows)
    report={"design":"STACK-10","mesh_count":len(rows),"maximum_stl_files":10,"all_pass":all(r["pass_check"] for r in rows),"printed_piece_count":sum(r["quantity"] for r in rows),"solid_material_upper_bound_g":round(sum(r["quantity"]*r["solid_mass_g"] for r in rows),1),"bed_envelope_mm":[325,320,325],"base_brim_envelope_mm":[316,296],"nozzle_mode":"single","physical_fit_verified":False,"physical_strength_verified":False,"parts":rows}
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
