"""Export every doorbot part and view from cad/doorbot.scad, then hash what was produced.

    python scripts/export_cad.py            # all STLs, then all PNG views
    python scripts/export_cad.py --part drum_gear
    python scripts/export_cad.py --views    # views only

Bounded: 600 s per part, 180 s per view, matching the plan's stop conditions.
"""
import argparse
import hashlib
import json
import os
import shutil
import subprocess
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path

from scad_params import ROOT

EXE = (os.environ.get("OPENSCAD") or shutil.which("openscad")
       or r"C:\Program Files\OpenSCAD\openscad.com")
SCAD = ROOT / "cad/doorbot.scad"

PARTS = ["base_shell", "base_cover", "motor_pinion", "compound_gear", "drum_gear",
         "door_anchor", "magnet_pod"]

# name -> (part, gimbal rotation "rx,ry,rz", extra -D flags, image size). Every view uses
# --viewall --autocenter so the framing follows the geometry instead of a hand-tuned distance.
VIEWS = {
    "assembly":       ("assembly", "58,0,28", [], "1500,1700"),
    "assembly_rear":  ("assembly", "58,0,208", [], "1500,1700"),
    "assembly_front": ("assembly", "90,0,0", [], "1200,1700"),
    "exploded":       ("exploded", "62,0,28", [], "1700,1700"),
    "section":        ("section", "58,0,28", [], "1500,1700"),
    "drive_train":    ("drive_train", "58,0,28", [], "1600,1300"),
    "installed_shut": ("installed", "0,0,0", ["door_deg=0"], "1700,1300"),
    "installed_mid":  ("installed", "0,0,0", ["door_deg=45"], "1700,1300"),
    "installed_open": ("installed", "0,0,0", ["door_deg=90"], "1700,1300"),
    "installed_iso":  ("installed", "62,0,28", ["door_deg=35"], "1700,1300"),
}
# One straight-on print-orientation shot per part, for the build guide.
PART_VIEWS = {p: (p, "58,0,30", [], "1100,1100") for p in PARTS}

def run(args, timeout, label):
    result = subprocess.run(args, capture_output=True, text=True, timeout=timeout)
    bad = result.returncode or "ERROR" in result.stderr
    if bad:
        raise RuntimeError(f"{label}: {result.stderr.strip()[:400]}")
    if "WARNING" in result.stderr:
        raise RuntimeError(f"{label} produced a geometry warning: "
                           + " | ".join(l for l in result.stderr.splitlines()
                                        if "WARNING" in l)[:400])
    return label


def export_part(name):
    out = ROOT / "stl" / f"{name}.stl"
    return run([EXE, "--export-format", "binstl", "-o", str(out), "-D", f'part="{name}"',
                str(SCAD)], 600, f"stl/{name}")


def render(out, part, rot, extra, size, timeout=180):
    args = [EXE, "-o", str(out), f"--imgsize={size}", "--colorscheme=Tomorrow",
            "--projection=o", "--viewall", "--autocenter", f"--camera=0,0,0,{rot},0",
            "-D", f'part="{part}"']
    for e in extra:
        args += ["-D", e]
    args.append(str(SCAD))
    return run(args, timeout, str(out.name))


def export_view(name, spec):
    part, rot, extra, size = spec
    return render(ROOT / "cad" / f"{name}.png", part, rot, extra, size)


def export_part_view(name, spec):
    part, rot, extra, size = spec
    return render(ROOT / "cad" / f"part_{name}.png", part, rot, extra, size)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--part")
    ap.add_argument("--views", action="store_true")
    ap.add_argument("--stl-only", action="store_true")
    args = ap.parse_args()
    for d in ["stl", "cad", "docs"]:
        (ROOT / d).mkdir(exist_ok=True)

    if args.part:
        print(export_part(args.part))
        return

    jobs = []
    with ThreadPoolExecutor(max_workers=4) as pool:
        if not args.views:
            jobs += [pool.submit(export_part, p) for p in PARTS]
        if not args.stl_only:
            jobs += [pool.submit(export_view, n, s) for n, s in VIEWS.items()]
            jobs += [pool.submit(export_part_view, n, s) for n, s in PART_VIEWS.items()]
        done = 0
        for f in as_completed(jobs):
            print("  " + f.result(), flush=True)
            done += 1
    digests = {}
    for pattern in ["cad/*.scad", "stl/*.stl", "cad/*.png"]:
        for path in sorted(ROOT.glob(pattern)):
            digests[str(path.relative_to(ROOT)).replace("\\", "/")] = \
                hashlib.sha256(path.read_bytes()).hexdigest()
    (ROOT / "docs/export.json").write_text(json.dumps(
        {"jobs": done, "sha256": digests}, indent=2))
    print(f"Exported {done} artefacts; {len(digests)} files hashed into docs/export.json")


if __name__ == "__main__":
    main()
