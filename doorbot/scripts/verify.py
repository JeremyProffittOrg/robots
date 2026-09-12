"""One command that has to pass before doorbot is considered done.

    python scripts/verify.py                 # everything
    python scripts/verify.py --no-firmware   # skip the two PlatformIO steps

Runs, in order: the mechanism analysis, the CAD analysis, the wiring check, the BOM, the
params/firmware consistency check, the host behaviour tests and the target firmware build.
Writes docs/verification.json with the result of each step and the source hashes it saw.
"""
import argparse
import hashlib
import json
import os
import re
import shutil
import subprocess
import sys
import time
from pathlib import Path

from scad_params import ROOT, params

PY = sys.executable


def find_gpp():
    """PlatformIO's native env needs a host compiler on PATH; find one if it is installed."""
    if shutil.which("g++"):
        return None
    for base in [Path(os.environ.get("LOCALAPPDATA", "")) / "Microsoft/WinGet/Packages",
                 Path("C:/msys64"), Path("C:/mingw64"), Path("C:/ProgramData/chocolatey/lib")]:
        if not base.exists():
            continue
        for candidate in base.glob("**/bin/g++.exe"):
            return str(candidate.parent)
    return None


def step(name, args, cwd=ROOT, env=None):
    start = time.time()
    try:
        result = subprocess.run(args, cwd=str(cwd), capture_output=True, text=True,
                                timeout=900, env=env)
        ok = result.returncode == 0
        tail = (result.stdout or "")[-1200:] + (result.stderr or "")[-600:]
    except subprocess.TimeoutExpired:
        ok, tail = False, "timed out after 900 s"
    print(("PASS  " if ok else "FAIL  ") + name + f"  ({time.time() - start:.1f} s)")
    if not ok:
        print("      " + tail.strip().replace("\n", "\n      ")[-1500:])
    return {"step": name, "pass": ok, "seconds": round(time.time() - start, 1),
            "output_tail": tail.strip()[-1200:]}


def params_match_firmware():
    """The firmware carries a few geometry constants; they must still match params.scad."""
    p = params()
    header = (ROOT / "firmware/include/config.h").read_text(encoding="utf-8")

    def define(name):
        m = re.search(rf"#define\s+{name}\s+([0-9.]+)f?", header)
        return float(m.group(1)) if m else None

    ratio = ((p["stage1_gear_t"] / p["stage1_pinion_t"])
             * (p["stage2_gear_t"] / p["stage2_pinion_t"]))
    drum_eff = p["drum_r"] + p["cable_d"] / 2
    mech = json.loads((ROOT / "docs/mechanism.json").read_text())
    travel = mech["summary"]["cable_travel_mm"]
    arm = mech["summary"]["arm_min_mm"]
    wants = {"GEAR_RATIO": ratio, "DRUM_EFF_R_MM": drum_eff,
             "CABLE_TRAVEL_MM": travel, "ARM_MIN_MM": arm,
             "DOOR_OPEN_DEG": p["door_open_deg"]}
    bad = [f"{k}: firmware has {define(k)}, the design says {v:.4g}"
           for k, v in wants.items()
           if define(k) is None or abs(define(k) - v) > max(0.05, abs(v) * 0.002)]
    ok = not bad
    print(("PASS  " if ok else "FAIL  ") + "firmware constants match cad/params.scad")
    for b in bad:
        print("      " + b)
    return {"step": "firmware constants match cad/params.scad", "pass": ok,
            "output_tail": "; ".join(bad)}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--no-firmware", action="store_true")
    args = ap.parse_args()

    results = [
        step("mechanism analysis", [PY, "scripts/check_mechanism.py"]),
        step("CAD analysis", [PY, "scripts/check_cad.py"]),
        step("wiring and pin map", [PY, "scripts/electronics.py"]),
        step("bill of materials", [PY, "scripts/bom.py"]),
    ]
    results.append(params_match_firmware())

    if not args.no_firmware:
        env = dict(os.environ)
        extra = find_gpp()
        if extra:
            env["PATH"] = extra + os.pathsep + env["PATH"]
            print(f"      (host compiler taken from {extra})")
        results.append(step("firmware behaviour tests", ["pio", "test", "-e", "native"],
                            cwd=ROOT / "firmware", env=env))
        results.append(step("firmware target build", ["pio", "run", "-e", "tdisplay"],
                            cwd=ROOT / "firmware", env=env))

    sources = {}
    for pattern in ["cad/*.scad", "scripts/*.py", "firmware/include/*.h", "firmware/src/*.cpp",
                    "firmware/test/*.cpp", "firmware/platformio.ini", "stl/*.stl"]:
        for path in sorted(ROOT.glob(pattern)):
            sources[str(path.relative_to(ROOT)).replace("\\", "/")] = \
                hashlib.sha256(path.read_bytes()).hexdigest()

    report = {"revision": "A", "all_pass": all(r["pass"] for r in results),
              "physical_test": False, "analysis_only": True,
              "steps": results, "source_sha256": sources}
    (ROOT / "docs").mkdir(exist_ok=True)
    (ROOT / "docs/verification.json").write_text(json.dumps(report, indent=2))
    failed = [r["step"] for r in results if not r["pass"]]
    print()
    if failed:
        raise SystemExit("FAILED: " + ", ".join(failed))
    print(f"PASS: {len(results)} verification steps. Everything here is analysis of the "
          f"design and a build of the firmware; no physical prototype has been tested.")


if __name__ == "__main__":
    main()
