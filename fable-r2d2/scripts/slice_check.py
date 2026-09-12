"""Slice every STL with the installed Bambu Studio CLI using the H2D 0.4 nozzle profile.

Proves each part fits the H2D single-extruder bed and slices without error or warning, and
records predicted filament mass and print time. No printer connection; settings, state and
G-code stay in a temporary directory that is removed afterwards.

Usage (from C:/dev/robots/fable-r2d2):
    python scripts/slice_check.py              # all parts in scripts/parts.json
    python scripts/slice_check.py --parts dome
"""
import argparse
import datetime
import hashlib
import json
import os
import subprocess
import tempfile
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PROFILES = Path("C:/Program Files/Bambu Studio/resources/profiles/BBL")
EXE = Path("C:/Program Files/Bambu Studio/bambu-studio.exe")
MANIFEST = json.loads((ROOT / "scripts/parts.json").read_text(encoding="utf-8"))
PARTS = MANIFEST["parts"]
FILAMENT = {"PETG": "Bambu PETG HF @BBL H2D 0.4 nozzle", "PLA": "Bambu PLA Basic @BBL H2D", "PETG-CF": "Bambu PETG-CF @BBL H2D 0.4 nozzle"}
OVERRIDES = {
    "wall_loops": "5", "top_shell_layers": "6", "bottom_shell_layers": "6",
    "sparse_infill_density": "30%", "sparse_infill_pattern": "gyroid",
    "enable_support": "1", "support_type": "tree(auto)", "support_on_build_plate_only": "0",
    "brim_type": "no_brim", "skirt_loops": "0",
}


def flatten(kind, name, seen=()):
    if name in seen:
        raise ValueError("Profile inheritance cycle")
    path = PROFILES / kind / (name + ".json")
    own = json.loads(path.read_text(encoding="utf-8-sig"))
    result = {}
    if own.get("inherits"):
        result.update(flatten(kind, own["inherits"], seen + (name,)))
    includes = own.get("include", [])
    if isinstance(includes, str):
        includes = [includes]
    for item in includes:
        result.update(flatten(kind, item, seen + (name,)))
    result.update({k: v for k, v in own.items() if k not in ("inherits", "include")})
    return result


def filament_profile(material):
    wanted = FILAMENT[material]
    if (PROFILES / "filament" / (wanted + ".json")).exists():
        return wanted
    fallback = {"PETG": "Generic PETG @BBL H2D", "PLA": "Generic PLA @BBL H2D", "PETG-CF": "Generic PETG @BBL H2D"}[material]
    return fallback


def slice_part(name, settings_cache):
    info = PARTS[name]
    stl = ROOT / "stl" / f"{name}.stl"
    material = info["material"]
    import trimesh
    if material not in settings_cache:
        settings_cache[material] = {
            "machine": flatten("machine", "Bambu Lab H2D 0.4 nozzle"),
            "process": dict(flatten("process", "0.20mm Standard @BBL H2D"), **OVERRIDES),
            "filament": flatten("filament", filament_profile(material)),
        }
    settings = settings_cache[material]
    with tempfile.TemporaryDirectory(prefix="r2-slice-") as folder:
        tmp = Path(folder).resolve()
        assert tmp.parent == Path(tempfile.gettempdir()).resolve()
        for kind, data in settings.items():
            (tmp / (kind + ".json")).write_text(json.dumps(data), encoding="utf-8")
        env = os.environ.copy()
        env["APPDATA"] = str(tmp / "app")
        env["LOCALAPPDATA"] = str(tmp / "local")
        (tmp / "state").mkdir()
        # Centre the mesh on the left-extruder bed ourselves; the CLI arrange step rejects
        # parts that nearly fill the bed even though they fit.
        mesh = trimesh.load_mesh(stl, process=False)
        centred = tmp / f"{name}.stl"
        mesh.apply_translation([-mesh.bounds[0][0] - mesh.extents[0] / 2 + 162.5, -mesh.bounds[0][1] - mesh.extents[1] / 2 + 160, -mesh.bounds[0][2]])
        mesh.export(centred)
        args = [str(EXE), "--datadir", str(tmp / "state"), "--arrange", "0",
                "--load-settings", str(tmp / "machine.json") + ";" + str(tmp / "process.json"),
                "--load-filaments", str(tmp / "filament.json"), "--curr-bed-type", "Textured PEI Plate",
                "--slice", "0", "--debug", "2", "--export-3mf", str(tmp / "part.3mf"), str(centred)]
        startup = subprocess.STARTUPINFO()
        startup.dwFlags |= subprocess.STARTF_USESHOWWINDOW
        startup.wShowWindow = 0
        result = subprocess.run(args, cwd=tmp, env=env, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                                timeout=3600, startupinfo=startup, creationflags=subprocess.CREATE_NO_WINDOW)
        report_path = tmp / "result.json"
        if not report_path.exists():
            raise RuntimeError(f"{name}: no result.json; rc={result.returncode}\n{result.stderr.decode(errors='replace')[-3000:]}")
        data = json.loads(report_path.read_text(encoding="utf-8"))
        row = {"part": f"stl/{name}.stl", "sha256": hashlib.sha256(stl.read_bytes()).hexdigest(),
               "material": material, "filament_profile": filament_profile(material),
               "return_code": data.get("return_code"), "error_string": data.get("error_string")}
        if data.get("return_code") == 0 and data.get("sliced_plates"):
            plate = data["sliced_plates"][0]
            with zipfile.ZipFile(tmp / "part.3mf") as archive:
                row["gcode_present"] = "Metadata/plate_1.gcode" in archive.namelist()
            row.update({"warning": plate.get("warning_message", ""),
                        "predicted_mass_g": plate["filaments"][0]["total_used_g"],
                        "predicted_time_s": plate["total_predication"],
                        "predicted_time_h": round(plate["total_predication"] / 3600, 2),
                        "bbox_mm": plate["objects"][0]["bbox"]})
        row["pass"] = bool(row.get("return_code") == 0 and not row.get("warning") and row.get("gcode_present"))
        return row


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--parts", nargs="+")
    args = parser.parse_args()
    if not EXE.is_file():
        raise SystemExit("Bambu Studio executable not found")
    names = args.parts or list(PARTS)
    cache = {}
    rows = []
    for name in names:
        row = slice_part(name, cache)
        rows.append(row)
        status = "PASS" if row["pass"] else "FAIL"
        print(f"{status} {name}: {row.get('predicted_mass_g', 0):.0f} g, {row.get('predicted_time_h', 0):.1f} h, {row.get('error_string')} {row.get('warning', '')}", flush=True)
    report = {
        "checked_at_utc": datetime.datetime.now(datetime.timezone.utc).isoformat(),
        "test_type": "Local Bambu Studio CLI slicing of package meshes; no printer connection or physical print",
        "profiles": {"machine": "Bambu Lab H2D 0.4 nozzle", "process": "0.20mm Standard @BBL H2D", "overrides": OVERRIDES, "bed": "Textured PEI Plate"},
        "all_pass": all(r["pass"] for r in rows), "rows": rows,
        "total_predicted_mass_g": round(sum(r.get("predicted_mass_g", 0) * PARTS[Path(r["part"]).stem]["quantity"] for r in rows), 1),
        "total_predicted_time_h": round(sum(r.get("predicted_time_s", 0) * PARTS[Path(r["part"]).stem]["quantity"] for r in rows) / 3600, 1),
    }
    out = ROOT / "cad/h2d-slice-check.json"
    if args.parts and out.exists():
        old = json.loads(out.read_text(encoding="utf-8"))
        merged = {r["part"]: r for r in old.get("rows", [])}
        for r in rows:
            merged[r["part"]] = r
        report["rows"] = list(merged.values())
        report["all_pass"] = all(r["pass"] for r in report["rows"])
    out.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({k: v for k, v in report.items() if k != "rows"}, indent=2), flush=True)
    if not report["all_pass"]:
        raise SystemExit("Slice check failed")


if __name__ == "__main__":
    main()
