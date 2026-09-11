"""Export the real OpenSCAD solids and check the printable mesh contract.

Run: C:\\Python314\\python.exe scripts/export_cad.py
Requires existing OpenSCAD and Python trimesh. No dependencies are installed.
Each export is bounded at 180 seconds; a failed export stops, never retries silently.
"""
import argparse
import csv
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import time
from concurrent.futures import ThreadPoolExecutor, as_completed

ROOT = Path(__file__).resolve().parents[1]
PARTS = {
    "fit_coupon": (1, "PETG", "Flat", "Print first; gauge M3/M8/bearing/switch fits"),
    "chassis_quarter": (4, "PETG", "Flat", "5mm deck; flip flat plates to mirror X/Y holes; do not rotate90 degrees"),
    "bumper_quarter": (4, "PLA", "Lower edge down", "15mm floor clearance"),
    "skirt_lower_quarter": (4, "PLA", "Lower flange down", "90mm height; M3 seam joints"),
    "skirt_upper_quarter": (4, "PLA", "Lower flange down", "90mm height; rear quarters removable"),
    "splice": (12, "PETG", "Flat", "Three plates per chassis radial seam"),
    "motor_cradle": (4, "PETG", "Base down", "55mm pillars; M3x65 through bolts"),
    "battery_tray": (1, "PETG", "Flat", "116x72mm pocket; 2x20mm straps"),
    "deck_post": (4, "PETG", "Upright", "95mm; M3x110 through bolt"),
    "electronics_deck": (1, "PETG", "Flat", "M2.5 insulated standoffs on slots"),
    "pcb_standoff": (32, "PETG", "Flat", "6mm insulated PCB spacers; quantity includes spares"),
    "shoulder_front": (1, "PLA", "Bottom flange down", "Flat front retains both arm brackets"),
    "shoulder_rear": (1, "PLA", "Bottom flange down", "Display and two switches; removable"),
    "screen_frame": (1, "PETG", "As exported", "52.2x26 board pocket; USB side opening"),
    "screen_clamp": (1, "PETG", "Flat", "Rear cover; foam pads contact PCB edges"),
    "arm_base": (2, "PETG", "Base down", "MG92B upright cradle; two cable ties"),
    "pitch_carrier": (2, "PETG", "Base down", "MG92B axis horizontal; supplied yaw horn"),
    "plunger_arm": (1, "PLA", "As exported; supports under cup", "Decorative hollow tube; no load"),
    "gun_arm": (1, "PLA", "As exported; supports under rods", "Solid decorative muzzle; no projectile function"),
    "neck_adapter": (1, "PLA", "Flat", "Shoulder 110mm PCD-radius to neck104mm radius"),
    "neck_ring": (2, "PLA", "Flat", "Three supports at30/150/270 degrees"),
    "neck_post": (6, "PETG", "Upright", "11mm spacing"),
    "neck_deck": (1, "PETG", "Flat", "Bearing and belt motor support"),
    "bearing_tower": (1, "PETG", "Flange down", "608 bearings22x8x7; lower bearing inserts from bottom"),
    "bearing_cap": (1, "PETG", "Flat", "3xM3x8 thread-forming screws"),
    "inner_spacer": (1, "PETG", "Flat", "12mm between bearing inner races"),
    "head_hub": (1, "PETG", "Foot down; supports under first rim", "M8 spindle;3mm round belt groove"),
    "head_servo_mount": (1, "PETG", "Flat", "FS5103R clamp; belt-tension slots"),
    "servo_pulley": (1, "PETG", "Flat", "Attach supplied horn; no printed spline"),
    "head_plate": (1, "PETG", "Flat", "Spokes retain dome with4M3 bolts"),
    "dome": (1, "PLA", "Open base down; tree support inside", "220mm diameter hollow dome; stationary wiring excluded"),
    "eye": (1, "PLA", "Base flange down", "Rear two M3 bolts; black pupil paint"),
    "lamp": (2, "Translucent PLA", "Flat", "Decorative unlit lamps; no head wires"),
    "hemisphere": (48, "PLA", "Open circular face down", "M3 captive nut; print6first to confirm seam access"),
    "speaker_mount": (1, "PETG", "As exported", "85mm speaker envelope; bolts to deck front"),
}

def openscad_path():
    candidates = [os.environ.get("OPENSCAD"), shutil.which("openscad"),
                  r"C:\Program Files\OpenSCAD\openscad.com"]
    return next((str(p) for p in candidates if p and Path(p).exists()), None)

def export_one(name, executable):
    target = ROOT / "stl" / f"{name}.stl"
    result = subprocess.run([executable, "--export-format", "binstl", "-o", str(target),
                             "-D", f'part="{name}"', str(ROOT / "cad/dalek.scad")],
                            capture_output=True, text=True, timeout=180)
    if result.returncode or not target.exists() or "ERROR:" in result.stderr:
        raise RuntimeError(f"{name}: {result.stderr}")
    return name

def validate():
    import trimesh
    rows = []
    for name, (qty, material, orientation, notes) in PARTS.items():
        mesh = trimesh.load_mesh(ROOT / "stl" / f"{name}.stl", process=True)
        size = mesh.extents
        surfaces = mesh.split(only_watertight=False)
        # A sealed void has a negative-volume surface; it is not a loose printed part.
        components = int(sum(m.volume > 0 for m in surfaces))
        okay = bool(mesh.is_watertight and mesh.is_winding_consistent and mesh.volume > 0
                    and all(size <= 300.001) and components == 1)
        rows.append(dict(part=name, quantity=qty, material=material,
                         x_mm=round(float(size[0]),3), y_mm=round(float(size[1]),3),
                         z_mm=round(float(size[2]),3), volume_mm3=round(float(mesh.volume),2),
                         solid_mass_g=round(float(mesh.volume)/1000*(1.27 if material=="PETG" else 1.24),2),
                         watertight=bool(mesh.is_watertight), connected_components=components,
                         enclosed_void_surfaces=int(sum(m.volume < 0 for m in surfaces)),
                         pass_check=okay, orientation=orientation, notes=notes))
    (ROOT / "bom").mkdir(exist_ok=True)
    with (ROOT / "bom/printed-parts.csv").open("w", newline="", encoding="utf-8") as f:
        writer=csv.DictWriter(f,fieldnames=rows[0].keys()); writer.writeheader();writer.writerows(rows)
    report = {"mesh_count":len(rows), "all_pass":all(r["pass_check"] for r in rows),
              "printed_piece_count":sum(r["quantity"] for r in rows),
              "solid_material_upper_bound_g":round(sum(r["quantity"]*r["solid_mass_g"] for r in rows),1),
              "bed_envelope_mm":[300,300,300], "physical_fit_verified":False,
              "parts":rows}
    (ROOT / "cad/validation.json").write_text(json.dumps(report,indent=2)+"\n",encoding="utf-8")
    print(json.dumps({k:v for k,v in report.items() if k!="parts"},indent=2),flush=True)
    bad=[r["part"] for r in rows if not r["pass_check"]]
    if bad: raise SystemExit("FAILED meshes: "+", ".join(bad))

def main():
    parser=argparse.ArgumentParser();parser.add_argument("--check-only",action="store_true")
    parser.add_argument("--parts",nargs="+");parser.add_argument("--jobs",type=int,default=3)
    args=parser.parse_args()
    if not args.check_only:
        executable=openscad_path()
        if not executable: raise SystemExit("OpenSCAD executable not found; set OPENSCAD")
        (ROOT/"stl").mkdir(exist_ok=True)
        names=args.parts or list(PARTS)
        unknown=set(names)-set(PARTS)
        if unknown:raise SystemExit(f"Unknown parts: {unknown}")
        with ThreadPoolExecutor(max_workers=args.jobs) as pool:
            tasks={pool.submit(export_one,n,executable):n for n in names}
            for done in as_completed(tasks): print("EXPORTED "+done.result(),flush=True)
    if not args.parts:validate()

if __name__=="__main__": main()
