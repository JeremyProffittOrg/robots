"""Package-level digital verification for fable-r2d2. Does not print, drive, or email.

Checks (each prints PASS/FAIL and the whole run exits non-zero on any failure):
  images      >= 30 reviewed reference images exist and are listed in the three review files
  cad         every STL in scripts/parts.json exists, cad/validation.json says all_pass and
              hashes match, cad/h2d-slice-check.json says all_pass with current hashes
  bom         bom/electronics.csv, bom/hardware.csv have URL + price on every row; the xlsx exists
  wiring      electronics/wiring.csv pins match firmware/kb2040/code.py MOTORS table
  firmware    unit tests pass (kb2040 protocol, pi mixing), node --check on app.js
  audio       audio/catalog.csv hashes match the WAV files
  drawings    output/drawings/drawing-manifest.json lists PNGs that exist with matching hashes
  manual      output/pdf/r2d2-assembly-manual.pdf exists and docs/pdf-check.json says all pages rendered
  video       output/video/video-manifest.json exists, MP4 hash matches, ffprobe agrees
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

ROOT = Path(__file__).resolve().parents[1]
RESULTS = []


def sha256(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def record(name, ok, detail):
    RESULTS.append({"check": name, "pass": bool(ok), "detail": detail})
    print(f"{'PASS' if ok else 'FAIL'} {name}: {detail}", flush=True)


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
            if match and ("KB2040" in (row.get("source", "") + row.get("target", ""))):
                used.add(match.group(1))
    unknown = sorted(p for p in used if p not in board_pins and p not in ("GND", "RAW", "3V", "VBUS", "USB"))
    ok = len(rows) > 40 and not unknown
    record("wiring", ok, f"{len(rows)} wires; KB2040 pins in wiring not in code.py: {unknown}")


def run(cmd, cwd=ROOT):
    result = subprocess.run(cmd, cwd=cwd, capture_output=True, text=True, timeout=300)
    return result.returncode, (result.stdout + result.stderr).strip()


def check_firmware():
    outputs = []
    ok = True
    for cmd in ([sys.executable, "firmware/kb2040/test_protocol.py"], [sys.executable, "firmware/pi/test_mixing.py"]):
        code, out = run(cmd)
        ok &= code == 0 and "OK" in out
        outputs.append(out.splitlines()[-1] if out else "no output")
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


def check_manifest(name, manifest_path, key):
    if not manifest_path.exists():
        record(name, False, f"{manifest_path.relative_to(ROOT)} missing")
        return None
    data = json.loads(manifest_path.read_text(encoding="utf-8"))
    bad = []
    for entry in data.get(key, []):
        path = ROOT / entry["file"]
        if not path.exists() or sha256(path) != entry["sha256"]:
            bad.append(entry["file"])
    record(name, bool(data.get(key)) and not bad, f"{len(data.get(key, []))} files, mismatches={bad}")
    return data


def check_drawings():
    check_manifest("drawings", ROOT / "output/drawings/drawing-manifest.json", "pngs")


def check_manual():
    pdf = ROOT / "output/pdf/r2d2-assembly-manual.pdf"
    check = ROOT / "docs/pdf-check.json"
    data = json.loads(check.read_text(encoding="utf-8")) if check.exists() else {}
    ok = pdf.exists() and data.get("all_pass") and data.get("sha256") == (sha256(pdf) if pdf.exists() else None)
    record("manual", ok, f"pdf={'present' if pdf.exists() else 'missing'}, pages={data.get('pages')}, all_pass={data.get('all_pass')}")


def check_video():
    manifest = ROOT / "output/video/video-manifest.json"
    video = ROOT / "output/video/r2d2-assembly-and-operation.mp4"
    if not manifest.exists() or not video.exists():
        record("video", False, "manifest or MP4 missing")
        return
    data = json.loads(manifest.read_text(encoding="utf-8"))
    ok = data.get("video_sha256") == sha256(video)
    if shutil.which("ffprobe"):
        code, out = run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "default=nw=1:nk=1", str(video)])
        ok &= code == 0 and abs(float(out) - data.get("seconds", 0)) < 1
    record("video", ok, f"{data.get('seconds')} s, {data.get('frames')} frames, hash match={data.get('video_sha256') == sha256(video)}")


CHECKS = {"images": check_images, "cad": check_cad, "bom": check_bom, "wiring": check_wiring, "firmware": check_firmware,
          "audio": check_audio, "drawings": check_drawings, "manual": check_manual, "video": check_video}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--only", default="")
    args = parser.parse_args()
    names = [n for n in args.only.split(",") if n] or list(CHECKS)
    for name in names:
        try:
            CHECKS[name]()
        except Exception as error:  # a crashed check is a failed check, never a silent one
            record(name, False, f"exception: {error}")
    report = {"all_pass": all(r["pass"] for r in RESULTS), "checks": RESULTS, "physical_validation": False}
    (ROOT / "docs").mkdir(exist_ok=True)
    (ROOT / "docs/verification.json").write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print("ALL PASS" if report["all_pass"] else "FAILURES PRESENT", flush=True)
    sys.exit(0 if report["all_pass"] else 1)


if __name__ == "__main__":
    main()
