"""Export every printable part from cad/r2d2.scad with the installed OpenSCAD, then validate.

Validation per STL (trimesh): watertight, consistent winding, positive volume, exactly one
connected solid, and the oriented bounding box inside the H2D envelope minus the 3 mm buffer
(322 x 317 x 320 mm) after the manifest print rotation. Writes cad/validation.json and
bom/printed-parts.csv. No printer or network access.

Usage (from C:/dev/robots/fable-r2d2):
    python scripts/export_cad.py                 # export all + validate
    python scripts/export_cad.py --parts dome    # export selected part(s) only
    python scripts/export_cad.py --check-only    # validate existing STLs
    python scripts/export_cad.py --views         # render cad/*.png preview images
"""
import argparse
import csv
import json
import os
import shutil
import subprocess
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MANIFEST = json.loads((ROOT / "scripts/parts.json").read_text(encoding="utf-8"))
PARTS = MANIFEST["parts"]
ENVELOPE = MANIFEST["envelope_mm"]
DENSITY = {"PETG": 1.27, "PLA": 1.24, "PETG-CF": 1.29}
SCAD = ROOT / "cad/r2d2.scad"


def openscad_path():
    # Prefer the portable nightly (manifold backend, much faster CSG) when it is installed.
    nightly = Path.home() / "tools/openscad-nightly/openscad.com"
    for candidate in [os.environ.get("OPENSCAD"), str(nightly), r"C:\Program Files\OpenSCAD\openscad.com", shutil.which("openscad")]:
        if candidate and Path(candidate).is_file():
            return candidate
    raise SystemExit("OpenSCAD executable not found; set OPENSCAD")


def export_one(name, executable):
    target = ROOT / "stl" / f"{name}.stl"
    target.parent.mkdir(exist_ok=True)
    startup = None
    if os.name == "nt":
        startup = subprocess.STARTUPINFO()
        startup.dwFlags |= subprocess.STARTF_USESHOWWINDOW
    backend = ["--backend=manifold"] if "nightly" in executable.lower() else []
    result = subprocess.run(
        [executable, *backend, "--export-format", "binstl", "-o", str(target), "-D", f'part="{name}"', str(SCAD)],
        capture_output=True, text=True, timeout=1800, startupinfo=startup)
    if result.returncode or not target.exists() or "ERROR:" in result.stderr:
        raise RuntimeError(f"{name}: rc={result.returncode}\n{result.stderr[-4000:]}")
    warnings = [line for line in result.stderr.splitlines() if "WARNING" in line]
    return name, warnings


def validate(names=None):
    import trimesh
    rows = []
    names = names or list(PARTS)
    for name in names:
        info = PARTS[name]
        path = ROOT / "stl" / f"{name}.stl"
        if not path.exists():
            rows.append(dict(part=name, pass_check=False, error="missing STL"))
            continue
        mesh = trimesh.load_mesh(path, process=True)
        size = mesh.extents
        surfaces = mesh.split(only_watertight=False)
        components = int(sum(m.volume > 1.0 for m in surfaces))
        rot = info.get("print_rotation_z", 0)
        print_size = size[[1, 0, 2]] if rot in (90, 270) else size
        fit = bool(print_size[0] <= ENVELOPE[0] + 1e-3 and print_size[1] <= ENVELOPE[1] + 1e-3 and print_size[2] <= ENVELOPE[2] + 1e-3)
        okay = bool(mesh.is_watertight and mesh.is_winding_consistent and mesh.volume > 0 and components == 1 and fit)
        rows.append(dict(
            part=name, quantity=info["quantity"], material=info["material"], mirror_for_second=info.get("mirror", False),
            x_mm=round(float(size[0]), 3), y_mm=round(float(size[1]), 3), z_mm=round(float(size[2]), 3),
            volume_cm3=round(float(mesh.volume) / 1000, 2),
            solid_mass_g=round(float(mesh.volume) / 1000 * DENSITY.get(info["material"], 1.27), 1),
            faces=int(len(mesh.faces)), watertight=bool(mesh.is_watertight), winding_consistent=bool(mesh.is_winding_consistent),
            connected_solids=components, print_rotation_z=rot, fits_envelope=fit, pass_check=okay,
            orientation=info["orientation"], notes=info["notes"]))
        print(f"{'PASS' if okay else 'FAIL'} {name}: {size.round(1).tolist()} mm, solids={components}, watertight={mesh.is_watertight}", flush=True)
    return rows


def write_reports(rows):
    (ROOT / "bom").mkdir(exist_ok=True)
    with (ROOT / "bom/printed-parts.csv").open("w", newline="", encoding="utf-8") as handle:
        fields = list(rows[0].keys())
        for row in rows:
            for key in row:
                if key not in fields:
                    fields.append(key)
        writer = csv.DictWriter(handle, fieldnames=fields)
        writer.writeheader()
        writer.writerows(rows)
    report = {
        "design": "fable-r2d2", "unique_stl_files": len(rows),
        "printed_piece_count": sum(r.get("quantity", 0) for r in rows),
        "envelope_mm": ENVELOPE, "all_pass": all(r.get("pass_check") for r in rows),
        "solid_material_upper_bound_g": round(sum(r.get("quantity", 0) * r.get("solid_mass_g", 0) for r in rows), 1),
        "physical_fit_verified": False, "physical_strength_verified": False, "parts": rows}
    (ROOT / "cad/validation.json").write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({k: v for k, v in report.items() if k != "parts"}, indent=2), flush=True)
    bad = [r["part"] for r in rows if not r.get("pass_check")]
    if bad:
        raise SystemExit("FAILED meshes: " + ", ".join(bad))


def views(executable):
    cameras = {
        "assembly": ("assembly", "1400,-1700,1100,0,0,330"),
        "rear": ("assembly", "-1400,1700,1000,0,0,330"),
        "exploded": ("exploded", "1500,-1800,1400,0,0,450"),
        "section": ("section", "1400,-1700,900,0,0,330"),
    }
    for name, (part, camera) in cameras.items():
        result = subprocess.run(
            [executable, "-o", str(ROOT / "cad" / f"{name}.png"), "--imgsize=1600,1600", "--colorscheme=Tomorrow",
             "--projection=o", "--viewall", "--autocenter", f"--camera={camera}", "-D", f'part="{part}"', str(SCAD)],
            capture_output=True, text=True, timeout=1800)
        if result.returncode:
            raise RuntimeError(result.stderr[-4000:])
        print("Rendered " + name, flush=True)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--check-only", action="store_true")
    parser.add_argument("--views", action="store_true")
    parser.add_argument("--parts", nargs="+")
    parser.add_argument("--jobs", type=int, default=4)
    args = parser.parse_args()
    for folder in ["stl", "bom", "cad"]:
        (ROOT / folder).mkdir(exist_ok=True)
    if args.views:
        views(openscad_path())
        return
    names = args.parts or list(PARTS)
    unknown = set(names) - set(PARTS)
    if unknown:
        raise SystemExit("Unknown parts: " + ", ".join(sorted(unknown)))
    if not args.check_only:
        executable = openscad_path()
        with ThreadPoolExecutor(max_workers=args.jobs) as pool:
            futures = {pool.submit(export_one, n, executable): n for n in names}
            for done in as_completed(futures):
                name, warnings = done.result()
                print("EXPORTED " + name + (f" ({len(warnings)} warnings)" if warnings else ""), flush=True)
                for line in warnings[:5]:
                    print("   " + line, flush=True)
    rows = validate(names)
    if args.parts:
        bad = [r["part"] for r in rows if not r.get("pass_check")]
        if bad:
            raise SystemExit("FAILED meshes: " + ", ".join(bad))
    else:
        write_reports(rows)


if __name__ == "__main__":
    main()
