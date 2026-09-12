"""Stage the two deliverables and a full source ZIP, with hashes the publish workflow checks.

Writes output/delivery/{doorbot-assembly-and-usage.mp4, doorbot-build-guide.pdf,
manifest.json} and output/doorbot-package.zip. The names and the manifest shape are what
.github/workflows/publish-doorbot.yml verifies, so this script is the last gate before a
push publishes anything.

    python scripts/package.py
"""
import hashlib
import json
import shutil
import zipfile

from scad_params import ROOT

DELIVERY = ROOT / "output/delivery"
VIDEO = "doorbot-assembly-and-usage.mp4"
PDF = "doorbot-build-guide.pdf"


def sha256(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    checks = json.loads((ROOT / "docs/verification.json").read_text())
    if not checks["all_pass"]:
        raise SystemExit("docs/verification.json is not all_pass - run scripts/verify.py")
    if checks["revision"] != "A":
        raise SystemExit("unexpected revision " + checks["revision"])
    for name, digest in checks["source_sha256"].items():
        actual = sha256(ROOT / name)
        if actual != digest:
            raise SystemExit(f"{name} changed since verification: re-run scripts/verify.py")

    pdf_meta = json.loads((ROOT / "docs/pdf.json").read_text())
    pdf = ROOT / pdf_meta["path"]
    if sha256(pdf) != pdf_meta["sha256"]:
        raise SystemExit("the PDF changed since it was built - re-run scripts/build_guide.py")

    video_meta = json.loads((DELIVERY / "video.json").read_text())
    video = DELIVERY / video_meta["file"]
    if sha256(video) != video_meta["sha256"]:
        raise SystemExit("the video changed since it was rendered")
    if video_meta["file"] != VIDEO:
        raise SystemExit(f"the video must be named {VIDEO}")

    DELIVERY.mkdir(parents=True, exist_ok=True)
    shutil.copyfile(pdf, DELIVERY / PDF)
    manifest = {
        "project": "doorbot",
        "revision": "A",
        "files": {VIDEO: sha256(DELIVERY / VIDEO), PDF: sha256(DELIVERY / PDF)},
        "pdf_pages": pdf_meta["pages"],
        "video_seconds": video_meta["seconds"],
        "video_simulation": True,
        "physical_tested": False,
        "verification_steps": len(checks["steps"]),
    }
    (DELIVERY / "manifest.json").write_text(json.dumps(manifest, indent=2))

    files = []
    for folder in ["bom", "cad", "docs", "electronics", "firmware", "infra", "scripts", "stl",
                   "output/drawings", "output/pdf", "output/delivery"]:
        base = ROOT / folder
        if not base.exists():
            continue
        files += [q for q in base.rglob("*") if q.is_file()
                  and not any(x in q.parts for x in [".pio", "__pycache__", "tmp"])]
    for name in ["README.md", ".gitignore", ".gitattributes"]:
        if (ROOT / name).exists():
            files.append(ROOT / name)
    target = ROOT / "output/doorbot-package.zip"
    with zipfile.ZipFile(target, "w", zipfile.ZIP_DEFLATED, compresslevel=9) as z:
        for q in sorted(set(files)):
            z.write(q, "doorbot/" + str(q.relative_to(ROOT)).replace("\\", "/"))
    with zipfile.ZipFile(target) as z:
        if z.testzip() is not None:
            raise SystemExit("the ZIP failed its own CRC check")
        names = z.namelist()
        stls = {n.rsplit("/", 1)[-1] for n in names if n.endswith(".stl")}
        expected = {"base_shell.stl", "base_cover.stl", "motor_pinion.stl",
                    "compound_gear.stl", "drum_gear.stl", "door_anchor.stl",
                    "magnet_pod.stl"}
        if stls != expected:
            raise SystemExit(f"ZIP STLs are {sorted(stls)}")
        for needed in [f"doorbot/output/delivery/{VIDEO}", f"doorbot/output/delivery/{PDF}",
                       "doorbot/firmware/src/main.cpp", "doorbot/cad/params.scad"]:
            if needed not in names:
                raise SystemExit(f"{needed} is missing from the ZIP")
        drawings = len([n for n in names if "/output/drawings/" in n and n.endswith(".png")])

    print(f"PASS: 7 STLs, {drawings} drawings, {pdf_meta['pages']}-page PDF and a "
          f"{video_meta['seconds']:.0f} s video staged")
    print(f"  {VIDEO}  {manifest['files'][VIDEO]}")
    print(f"  {PDF}  {manifest['files'][PDF]}")
    print(f"  {target.name}  {target.stat().st_size / 1e6:.1f} MB  {sha256(target)}")


if __name__ == "__main__":
    main()
