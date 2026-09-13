"""Render the revision D mock-up sheet: both stances and the stance transition, every printed part in place.

Uses the OpenSCAD assembly (cad/r2d2.scad, part="assembly") with the stance pose set by
`-D stance_s=<mm>` (assembly_layout.STANCE_PARAMETER). Row one is the three-leg operating stance,
row two the stationary two-foot stance, row three three poses of the change between them, in the
order the retract runs. Stroke, tilt, centre-foot lift and lock state in every caption come from
the same kinematics the CAD uses (scripts/stability.py Stance, through assembly_layout.Layout), so
the mock-up cannot drift from the parts.

Usage (from C:/dev/robots/fable-r2d2):
    python scripts/render_mockup.py                 # output/drawings/00_final_build_mockup.png
    python scripts/render_mockup.py --size 2000     # per-view pixel size
    python scripts/render_mockup.py --plan          # print the view plan only; renders nothing
"""
import argparse
import hashlib
import json
import os
import shutil
import subprocess
import sys
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

sys.path.insert(0, str(Path(__file__).resolve().parent))
from assembly_layout import REVISION, STANCE_PARAMETER, Layout, declared_stance_parameter, package_counts  # noqa: E402

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "output/drawings/00_final_build_mockup.png"
SCAD = ROOT / "cad/r2d2.scad"
FONTS = Path("C:/Windows/Fonts")
COLUMNS = 3

# Assembly frame: +Y is the droid's front, +X its right, floor at z=0.
CENTRE = (0, 60, 360)
EYES = {"Front": (0, 2600, 400), "Three-quarter": (2300, 2800, 1500), "Right side": (2600, 60, 400),
        "Rear": (0, -2600, 400)}


def sha256(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def cad_hashes():
    return {p.relative_to(ROOT).as_posix(): sha256(p) for p in sorted((ROOT / "cad").glob("*.scad"))}


def lock_text(pose):
    return "both shoulder locks seated" if pose.locks_seated_cad() else "shoulder locks released"


def view_plan(lay):
    """Rows of (view, stroke) tiles with captions computed from the stance kinematics."""
    ends = lay.endpoints()
    stance = lay.stance
    half_tilt = stance.stroke_for_tilt(lay.p["body_tilt"] / 2)
    lifting = (ends["two_foot"] + ends["contact"]) / 2
    rows = [
        ("Three-leg operating stance", [("Front", ends["three_leg"], "The droid faces +Y"),
                                        ("Three-quarter", ends["three_leg"], "Centre foot ahead, body tilted back"),
                                        ("Right side", ends["three_leg"], "Drive allowed only here")]),
        ("Two-foot stance: stationary, centre foot stowed", [("Rear", ends["two_foot"], "Charge port and main switch"),
                                                             ("Three-quarter", ends["two_foot"], "Body upright"),
                                                             ("Right side", ends["two_foot"], "Drive refused")]),
        ("Stance change, three-leg to two-foot (deploy runs in reverse)",
         [("Right side", half_tilt, "1 Unlocked, tilting on the floor"),
          ("Right side", ends["contact"], "2 Upright, locks re-seated"),
          ("Right side", lifting, "3 Lifting the centre foot")]),
    ]
    plan = []
    for row_title, tiles in rows:
        for view, stroke, lead in tiles:
            pose = lay.at_stroke(stroke)
            caption = (f"{lead}. {STANCE_PARAMETER} {stroke:.1f} mm, tilt {pose.tilt:.1f} deg, "
                       f"centre foot {pose.centre_foot_lift():.0f} mm up, {lock_text(pose)}")
            plan.append({"row": row_title, "view": view, "eye": EYES[view], "stroke_mm": round(stroke, 3),
                         "tilt_deg": round(pose.tilt, 3), "centre_foot_lift_mm": round(pose.centre_foot_lift(), 2),
                         "locks_seated": pose.locks_seated_cad(), "caption": caption})
    return plan


def openscad():
    nightly = Path.home() / "tools/openscad-nightly/openscad.com"
    for candidate in [os.environ.get("OPENSCAD"), str(nightly), r"C:\Program Files\OpenSCAD\openscad.com", shutil.which("openscad")]:
        if candidate and Path(candidate).is_file():
            return candidate
    raise SystemExit("OpenSCAD not found; set OPENSCAD")


def font(size, bold=False):
    for name in (("arialbd.ttf", "arial.ttf") if bold else ("arial.ttf",)):
        path = FONTS / name
        if path.is_file():
            return ImageFont.truetype(str(path), size)
    return ImageFont.load_default()


def render(executable, index, tile, size, scratch):
    target = scratch / f"view-{index:02d}.png"
    camera = ",".join(str(v) for v in (*tile["eye"], *CENTRE))
    backend = ["--backend=manifold", "--render"] if "nightly" in executable.lower() else []
    result = subprocess.run(
        [executable, *backend, "-o", str(target), f"--imgsize={size},{size}",
         "--colorscheme=Tomorrow", "--projection=o", f"--camera={camera}", "--viewall", "--autocenter",
         "-D", 'part="assembly"', "-D", f"{STANCE_PARAMETER}={tile['stroke_mm']}", str(SCAD)],
        capture_output=True, text=True, timeout=3600)
    if result.returncode or not target.exists():
        raise RuntimeError(f"{tile['view']} at {STANCE_PARAMETER}={tile['stroke_mm']}: rc={result.returncode}\n{result.stderr[-2000:]}")
    print(f"rendered {tile['row']} / {tile['view']} at {STANCE_PARAMETER}={tile['stroke_mm']}", flush=True)
    return target


def trim_white(image, pad=14):
    """Crop the uniform border OpenSCAD leaves around the model."""
    grey = image.convert("L")
    mask = grey.point(lambda v: 255 if v < 246 else 0)
    box = mask.getbbox()
    if not box:
        return image
    left, top, right, bottom = box
    return image.crop((max(0, left - pad), max(0, top - pad),
                       min(image.width, right + pad), min(image.height, bottom + pad)))


def wrapped(draw, text, width, typeface):
    lines, line = [], ""
    for word in text.split():
        trial = f"{line} {word}".strip()
        if draw.textlength(trial, font=typeface) > width and line:
            lines.append(line)
            line = word
        else:
            line = trial
    return lines + ([line] if line else [])


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--size", type=int, default=1700)
    parser.add_argument("--cell-width", type=int, default=1250)
    parser.add_argument("--plan", action="store_true", help="print the view plan and exit")
    args = parser.parse_args()
    if declared_stance_parameter(ROOT) is None:
        raise SystemExit(f"cad/r2d2.scad does not declare {STANCE_PARAMETER}; the stance poses cannot be rendered")
    lay = Layout(ROOT)
    plan = view_plan(lay)
    if args.plan:
        print(json.dumps(plan, indent=2))
        return
    executable = openscad()
    sources = cad_hashes()
    scratch = ROOT / "output/drawings/_mockup"
    scratch.mkdir(parents=True, exist_ok=True)
    try:
        tiles = [trim_white(Image.open(render(executable, i, tile, args.size, scratch)).convert("RGB"))
                 for i, tile in enumerate(plan)]
        if cad_hashes() != sources:
            raise RuntimeError("cad/*.scad changed while the mock-up was rendering")
        counts = package_counts(ROOT)
        rows = [plan[i:i + COLUMNS] for i in range(0, len(plan), COLUMNS)]
        cell_w, cell_h = args.cell_width, int(args.size * 0.82)
        margin, gap, header, footer, band, label = 56, 44, 168, 118, 70, 150
        width = margin * 2 + cell_w * COLUMNS + gap * (COLUMNS - 1)
        height = header + len(rows) * (band + cell_h + label) + (len(rows) - 1) * gap + footer
        sheet = Image.new("RGB", (width, height), "white")
        draw = ImageDraw.Draw(sheet)
        draw.text((margin, 44), f"fable-r2d2 revision {REVISION}  /  final build mock-up and stance change",
                  font=font(58, True), fill="#13202c")
        draw.text((margin, 116),
                  f"Every printed part in its assembled place: {counts['designs']} STL files, {counts['pieces']} printed "
                  f"pieces. Stance set by the actuator stroke {STANCE_PARAMETER}.", font=font(29), fill="#4b5b68")
        draw.line([(margin, header - 14), (width - margin, header - 14)], fill="#9fb0be", width=3)
        caption_font = font(25)
        for r, row in enumerate(rows):
            y_row = header + r * (band + cell_h + label + gap)
            draw.text((margin, y_row + 14), row[0]["row"], font=font(38, True), fill="#12446f")
            for c, tile in enumerate(row):
                image = tiles[plan.index(tile)].copy()
                image.thumbnail((cell_w, cell_h), Image.LANCZOS)
                x0 = margin + c * (cell_w + gap)
                y0 = y_row + band
                sheet.paste(image, (x0 + (cell_w - image.width) // 2, y0 + (cell_h - image.height) // 2))
                draw.text((x0, y0 + cell_h + 12), tile["view"], font=font(33, True), fill="#1d5a7a")
                for n, line in enumerate(wrapped(draw, tile["caption"], cell_w, caption_font)[:3]):
                    draw.text((x0, y0 + cell_h + 56 + n * 31), line, font=caption_font, fill="#54636f")
        note = (f"Rendered from cad/r2d2.scad part=\"assembly\" with -D {STANCE_PARAMETER}=<stroke>, the same source the "
                "STL files are exported from. Motors, wheels, actuator, bearings and locks are nominal purchased envelopes. "
                "Digital design: nothing printed, assembled or driven.")
        draw.line([(margin, height - footer + 6), (width - margin, height - footer + 6)], fill="#9fb0be", width=3)
        for n, line in enumerate(wrapped(draw, note, width - 2 * margin, caption_font)[:2]):
            draw.text((margin, height - footer + 26 + n * 32), line, font=caption_font, fill="#54636f")

        OUT.parent.mkdir(parents=True, exist_ok=True)
        sheet.save(OUT)
        digest = sha256(OUT)
        manifest = {"revision": REVISION, "file": OUT.relative_to(ROOT).as_posix(), "pixels": list(sheet.size),
                    "sha256": digest, "stance_parameter": STANCE_PARAMETER, "stance_endpoints_mm": lay.endpoints(),
                    "poses": [{k: tile[k] for k in ("row", "view", "stroke_mm", "tilt_deg", "centre_foot_lift_mm",
                                                     "locks_seated", "caption")} for tile in plan],
                    "projection": "orthographic", "source": f"cad/r2d2.scad part=assembly -D {STANCE_PARAMETER}",
                    "source_sha256": sources, "physical_build": False}
        (ROOT / "output/drawings/mockup-manifest.json").write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
        print(f"PASS: {OUT} {sheet.size[0]}x{sheet.size[1]} revision {REVISION}, {len(plan)} poses, sha256 {digest[:16]}")
    finally:
        shutil.rmtree(scratch, ignore_errors=True)


if __name__ == "__main__":
    main()
