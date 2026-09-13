"""Package-level digital verification for fable-r2d2 revision D. Does not print, drive, or email.

Checks (each prints PASS/FAIL and the whole run exits non-zero on any failure):
  images      >= 30 reviewed reference images exist and are listed in the three review files
  cad         every STL in scripts/parts.json exists, cad/validation.json says all_pass and
              hashes match, cad/h2d-slice-check.json says all_pass with current hashes
  stance      docs/stance-check.json passed, and its source_sha256 covers and matches the current
              CAD (every cad/*.scad, every parts.json STL, its design_source and check_stance.py)
  bom         bom/electronics.csv, bom/hardware.csv have URL + price on every row; the xlsx exists
  wiring      electronics/wiring.csv pins match firmware/kb2040/code.py MOTORS table
  firmware    unit tests pass (kb2040, pi) with the test counts parsed from the real runs,
              node --check on app.js
  audio       audio/catalog.csv hashes match the WAV files
  drawings    output/drawings/drawing-manifest.json is revision D, lists PNGs that exist with
              matching hashes, and its CAD and STL source hashes match the current files
  mockup      output/drawings/mockup-manifest.json is revision D, the PNG hash matches, it shows
              both stance endpoints and a transition pose, and its CAD sources are current
  manual      output/pdf/r2d2-assembly-manual.pdf exists; docs/pdf-check.json is revision D, says all
              pages rendered, and its source hashes are current
  video       output/video/video-manifest.json is revision D, MP4 hash matches, ffprobe agrees, and
              its source hashes are current

docs/verification.json gets "revision": "D" only when every check ran and passed.
Usage: python scripts/verify.py [--only images,cad,...]
"""
import argparse
import csv
import hashlib
import json
import re
import shutil
import subprocess
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from assembly_layout import REVISION, read_parts  # noqa: E402

ROOT = Path(__file__).resolve().parents[1]
RESULTS = []
FIRMWARE_TESTS = {}
STANCE_CHECK = "docs/stance-check.json"


def sha256(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def record(name, ok, detail):
    RESULTS.append({"check": name, "pass": bool(ok), "detail": detail})
    print(f"{'PASS' if ok else 'FAIL'} {name}: {detail}", flush=True)


def cad_sources(root=ROOT):
    """Repository paths of every OpenSCAD source."""
    root = Path(root)
    return sorted(p.relative_to(root).as_posix() for p in (root / "cad").glob("*.scad"))


def stl_sources(root=ROOT):
    """Repository paths of every STL that scripts/parts.json lists."""
    return sorted(f"stl/{name}.stl" for name in read_parts(root))


def source_problems(hashes, required, root=ROOT):
    """Why a recorded {path: sha256} map does not describe the current files; empty when it does."""
    root = Path(root)
    if not isinstance(hashes, dict) or not hashes:
        return ["no source hashes recorded"]
    problems = []
    missing = sorted(set(required) - set(hashes))
    if missing:
        problems.append("source hashes do not cover " + ", ".join(missing))
    stale = sorted(rel for rel, digest in hashes.items()
                   if not (root / rel).is_file() or sha256(root / rel) != digest)
    if stale:
        problems.append("sources changed since the output was built: " + ", ".join(stale))
    return problems


def check_images():
    files = sorted(p for p in (ROOT / "research/images").glob("*") if p.suffix.lower() in (".jpg", ".jpeg", ".png"))
    listed = set()
    for review in (ROOT / "research").glob("image-review-*.md"):
        listed.update(re.findall(r"(?:dome|legs|body)-\d+\.(?:jpg|png)", review.read_text(encoding="utf-8", errors="replace")))
    present = [p for p in files if p.name in listed]
    hashes = {sha256(p) for p in present}
    ok = len(present) >= 30 and len(hashes) >= 30
    record("images", ok, f"{len(present)} listed files present, {len(hashes)} distinct by hash (>= 30 required)")


def check_cad():
    parts = json.loads((ROOT / "scripts/parts.json").read_text(encoding="utf-8"))["parts"]
    missing = [n for n in parts if not (ROOT / "stl" / f"{n}.stl").exists()]
    validation = json.loads((ROOT / "cad/validation.json").read_text(encoding="utf-8")) if (ROOT / "cad/validation.json").exists() else {}
    slices = json.loads((ROOT / "cad/h2d-slice-check.json").read_text(encoding="utf-8")) if (ROOT / "cad/h2d-slice-check.json").exists() else {}
    stale = []
    for row in slices.get("rows", []):
        path = ROOT / row["part"]
        if not path.exists() or sha256(path) != row["sha256"]:
            stale.append(row["part"])
    sliced = {Path(r["part"]).stem for r in slices.get("rows", [])}
    ok = (not missing and validation.get("all_pass") and validation.get("unique_stl_files") == len(parts)
          and slices.get("all_pass") and not stale and sliced == set(parts))
    record("cad", ok, f"{len(parts) - len(missing)}/{len(parts)} STLs, validation all_pass={validation.get('all_pass')}, "
                      f"slice all_pass={slices.get('all_pass')}, stale slices={stale}, missing={missing}")


def stance_check_problems(root=ROOT):
    """Reasons docs/stance-check.json cannot support revision D; empty when it can.

    The report must say passed=true and carry source_sha256 {path: sha256} for every file the
    transition was checked against: each cad/*.scad, each STL in scripts/parts.json, each path in
    its design_source list and scripts/check_stance.py itself. Every hash must match today's file.
    """
    root = Path(root)
    path = root / STANCE_CHECK
    if not path.is_file():
        return [f"{STANCE_CHECK} missing; run python scripts/check_stance.py"]
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except ValueError as error:
        return [f"{STANCE_CHECK} is not valid JSON: {error}"]
    problems = []
    if data.get("passed") is not True:
        problems.append(f"passed={data.get('passed')} with {len(data.get('failures') or [])} failure rows")
    required = set(cad_sources(root)) | set(stl_sources(root)) | {"scripts/check_stance.py"}
    required |= set(data.get("design_source") or [])
    problems += [f"source_sha256: {p}" for p in source_problems(data.get("source_sha256"), required, root)]
    return problems


def check_stance():
    problems = stance_check_problems()
    data = {}
    if (ROOT / STANCE_CHECK).is_file():
        try:
            data = json.loads((ROOT / STANCE_CHECK).read_text(encoding="utf-8"))
        except ValueError:
            data = {}
    record("stance", not problems,
           f"{STANCE_CHECK}: passed={data.get('passed')}, {data.get('samples')} sampled poses, "
           f"{len(data.get('source_sha256') or {})} source hashes; problems={problems[:4]}")


def check_bom():
    problems = []
    total = 0.0
    for name in ("electronics.csv", "hardware.csv"):
        path = ROOT / "bom" / name
        if not path.exists():
            problems.append(f"{name} missing")
            continue
        with path.open(newline="", encoding="utf-8") as handle:
            rows = list(csv.DictReader(handle))
        for row in rows:
            if not row.get("url", "").startswith("http") or not row.get("unit_usd"):
                problems.append(f"{name}:{row.get('reference')} lacks url/price")
            try:
                total += float(row.get("quantity", 0)) * float(row.get("unit_usd", 0))
            except ValueError:
                problems.append(f"{name}:{row.get('reference')} non-numeric")
    xlsx = ROOT / "bom/bill-of-materials.xlsx"
    ok = not problems and xlsx.exists()
    record("bom", ok, f"purchased subtotal ${total:,.2f}; xlsx={'present' if xlsx.exists() else 'missing'}; problems={problems[:5]}")


def check_wiring():
    code = (ROOT / "firmware/kb2040/code.py").read_text(encoding="utf-8")
    board_pins = set(re.findall(r"board\.([A-Z0-9_]+)", code))
    wiring = ROOT / "electronics/wiring.csv"
    if not wiring.exists():
        record("wiring", False, "electronics/wiring.csv missing")
        return
    with wiring.open(newline="", encoding="utf-8") as handle:
        rows = list(csv.DictReader(handle))
    used = set()
    for row in rows:
        for field in ("source_pin", "target_pin"):
            match = re.match(r"(?:board\.)?([A-Z][A-Z0-9]*)$", (row.get(field) or "").strip())
            side = field[:-len("_pin")]
            if match and ("KB2040" in (row.get("source", "") + row.get("target", ""))
                          or row.get(side) == "A2"):  # A2 is the KB2040 designator in wiring.csv
                used.add(match.group(1))
    unknown = sorted(p for p in used if p not in board_pins and p not in ("GND", "RAW", "3V", "VBUS", "USB"))
    ok = len(rows) > 40 and not unknown
    record("wiring", ok, f"{len(rows)} wires; KB2040 pins in wiring not in code.py: {unknown}")


def run(cmd, cwd=ROOT):
    result = subprocess.run(cmd, cwd=cwd, capture_output=True, text=True, timeout=300)
    return result.returncode, (result.stdout + result.stderr).strip()


def parse_test_count(output):
    """Number from unittest's "Ran N tests in" line, or None when the run printed none."""
    match = re.search(r"(?m)^Ran (\d+) tests? in ", output)
    return int(match.group(1)) if match else None


def check_firmware():
    outputs = []
    ok = True
    for suite in ("firmware/kb2040", "firmware/pi"):  # every test_*.py, stance tests included
        code, out = run([sys.executable, "-m", "unittest", "discover", "-s", suite])
        count = parse_test_count(out)
        FIRMWARE_TESTS[suite] = count
        ok &= code == 0 and out.rstrip().endswith("OK") and bool(count)
        ran = next((line for line in out.splitlines() if line.startswith("Ran ")), "no test count")
        outputs.append("{0}: {1}, exit {2}".format(suite, ran, code))
    if shutil.which("node"):
        code, out = run(["node", "--check", "firmware/pi/static/app.js"])
        ok &= code == 0
        outputs.append("app.js syntax OK" if code == 0 else out)
    for path in (ROOT / "firmware").rglob("*.py"):
        code, out = run([sys.executable, "-m", "py_compile", str(path)])
        ok &= code == 0
    record("firmware", ok, "; ".join(outputs))


def check_audio():
    catalog = ROOT / "audio/catalog.csv"
    if not catalog.exists():
        record("audio", False, "audio/catalog.csv missing")
        return
    with catalog.open(newline="", encoding="utf-8") as handle:
        rows = list(csv.DictReader(handle))
    bad = []
    for row in rows:
        path = ROOT / row["file"] if (ROOT / row["file"]).exists() else ROOT / "firmware/pi/sounds" / Path(row["file"]).name
        if not path.exists() or sha256(path) != row["sha256"]:
            bad.append(row.get("name"))
    record("audio", bool(rows) and not bad, f"{len(rows)} clips, mismatches={bad}")


def revision_problem(data, label):
    return [] if data.get("revision") == REVISION else [f"{label} is revision {data.get('revision')}, not {REVISION}"]


def check_drawings():
    manifest = ROOT / "output/drawings/drawing-manifest.json"
    if not manifest.exists():
        record("drawings", False, f"{manifest.relative_to(ROOT)} missing")
        return
    data = json.loads(manifest.read_text(encoding="utf-8"))
    bad = [e["file"] for e in data.get("pngs", []) if not (ROOT / e["file"]).exists() or sha256(ROOT / e["file"]) != e["sha256"]]
    problems = revision_problem(data, "drawing-manifest.json")
    problems += source_problems(data.get("source_sha256"), set(cad_sources()) | set(stl_sources()))
    ok = bool(data.get("pngs")) and not bad and not problems
    record("drawings", ok, f"{len(data.get('pngs', []))} files, mismatches={bad}, problems={problems[:3]}")


def check_mockup():
    manifest = ROOT / "output/drawings/mockup-manifest.json"
    if not manifest.exists():
        record("mockup", False, f"{manifest.relative_to(ROOT)} missing")
        return
    data = json.loads(manifest.read_text(encoding="utf-8"))
    png = ROOT / data.get("file", "output/drawings/00_final_build_mockup.png")
    problems = revision_problem(data, "mockup-manifest.json")
    if not png.is_file() or sha256(png) != data.get("sha256"):
        problems.append("mock-up PNG missing or hash mismatch")
    ends = data.get("stance_endpoints_mm") or {}
    strokes = [pose.get("stroke_mm") for pose in data.get("poses", [])]
    if not ends or not all(any(abs(s - ends[k]) < 1e-6 for s in strokes if s is not None) for k in ("two_foot", "three_leg")):
        problems.append("mock-up does not show both stance endpoints")
    elif not any(ends["two_foot"] < s < ends["three_leg"] for s in strokes if s is not None):
        problems.append("mock-up shows no transition pose")
    problems += source_problems(data.get("source_sha256"), set(cad_sources()))
    record("mockup", not problems, f"{len(strokes)} poses {strokes}; problems={problems[:3]}")


def manual_sources(root=ROOT):
    """Files the manual is generated from, whose change makes the PDF stale."""
    root = Path(root)
    fixed = ["README.md", "docs/stability.json", STANCE_CHECK, "cad/validation.json", "cad/h2d-slice-check.json",
             "electronics/wiring.csv", "output/drawings/drawing-manifest.json", "scripts/parts.json"]
    docs = sorted(p.relative_to(root).as_posix() for p in (root / "docs").glob("*.md"))
    boms = sorted(p.relative_to(root).as_posix() for p in (root / "bom").glob("*.csv"))
    return sorted(set(fixed + docs + boms))


def check_manual():
    pdf = ROOT / "output/pdf/r2d2-assembly-manual.pdf"
    check = ROOT / "docs/pdf-check.json"
    data = json.loads(check.read_text(encoding="utf-8")) if check.exists() else {}
    problems = revision_problem(data, "pdf-check.json")
    if not pdf.exists() or data.get("sha256") != sha256(pdf):
        problems.append("PDF missing or hash mismatch")
    problems += source_problems(data.get("source_sha256"), manual_sources())
    ok = data.get("all_pass") is True and not problems
    record("manual", ok, f"pdf={'present' if pdf.exists() else 'missing'}, pages={data.get('pages')}, "
                         f"all_pass={data.get('all_pass')}, problems={problems[:3]}")


def check_video():
    manifest = ROOT / "output/video/video-manifest.json"
    video = ROOT / "output/video/r2d2-assembly-and-operation.mp4"
    if not manifest.exists() or not video.exists():
        record("video", False, "manifest or MP4 missing")
        return
    data = json.loads(manifest.read_text(encoding="utf-8"))
    problems = revision_problem(data, "video-manifest.json")
    ok = data.get("video_sha256") == sha256(video)
    if shutil.which("ffprobe"):
        code, out = run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "default=nw=1:nk=1", str(video)])
        ok &= code == 0 and abs(float(out) - data.get("seconds", 0)) < 1
    problems += source_problems(data.get("source_sha256"), set(stl_sources()) | {"cad/params.scad", "cad/stance.scad"})
    record("video", ok and not problems, f"{data.get('seconds')} s, {data.get('frames')} frames, "
                                         f"hash match={data.get('video_sha256') == sha256(video)}, problems={problems[:3]}")


CHECKS = {"images": check_images, "cad": check_cad, "stance": check_stance, "bom": check_bom, "wiring": check_wiring,
          "firmware": check_firmware, "audio": check_audio, "drawings": check_drawings, "mockup": check_mockup,
          "manual": check_manual, "video": check_video}


def build_report(results, names, firmware_tests=None):
    """verification.json content. Revision D is claimed only by a complete run that passed."""
    complete = set(names) == set(CHECKS)
    all_pass = bool(results) and all(r["pass"] for r in results)
    report = {"all_pass": all_pass, "revision": REVISION if (all_pass and complete) else None,
              "revision_target": REVISION, "checks": results,
              "firmware_tests": dict(firmware_tests if firmware_tests is not None else FIRMWARE_TESTS),
              "physical_validation": False}
    if not complete:
        report["partial_run"] = list(names)
    return report


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--only", default="")
    args = parser.parse_args()
    names = [n for n in args.only.split(",") if n] or list(CHECKS)
    unknown = [n for n in names if n not in CHECKS]
    if unknown:
        raise SystemExit(f"Unknown check(s): {', '.join(unknown)}; choose from {', '.join(CHECKS)}")
    for name in names:
        try:
            CHECKS[name]()
        except Exception as error:  # a crashed check is a failed check, never a silent one
            record(name, False, f"exception: {error}")
    report = build_report(RESULTS, names)
    (ROOT / "docs").mkdir(exist_ok=True)
    (ROOT / "docs/verification.json").write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print(f"ALL PASS: revision {report['revision']}" if report["revision"] else
          ("ALL PASS (partial run; revision not claimed)" if report["all_pass"] else "FAILURES PRESENT"), flush=True)
    sys.exit(0 if report["all_pass"] else 1)


if __name__ == "__main__":
    main()
