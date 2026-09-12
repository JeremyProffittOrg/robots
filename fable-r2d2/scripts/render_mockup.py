"""Render a mock-up sheet of the finished robot: every printed part in its assembled place.

Uses the OpenSCAD assembly (cad/r2d2.scad, part="assembly"), which places all twelve printed
pieces plus the motor and wheel envelopes in the three-leg operating stance, then tiles four
camera views into one PNG with a caption. Geometry comes from the same source the STLs are
exported from, so the mock-up cannot drift from the parts.

Usage (from C:/dev/robots/fable-r2d2):
    python scripts/render_mockup.py                 # output/drawings/00_final_build_mockup.png
    python scripts/render_mockup.py --size 2000     # per-view pixel size
"""
import argparse
import hashlib
import json
import os
import shutil
import subprocess
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "output/drawings/00_final_build_mockup.png"
SCAD = ROOT / "cad/r2d2.scad"
FONTS = Path("C:/Windows/Fonts")

# Assembly frame: +Y is the droid's front, +X its right, floor at z=0.
# camera = eyex,eyey,eyez,centrex,centrey,centrez
CENTRE = (0, 60, 360)
# (name, eye, caption, orthographic) - orthographic views use --viewall so the whole robot fits
VIEWS = [
    ("Front", (0, 2600, 400), "The droid faces +Y: data port, utility-arm bays, vents, coin slots", True),
    ("Three-quarter", (2300, 2800, 1500), "Operating stance: body tilted 18 deg onto the centre leg", True),
    ("Right side", (2600, 60, 400), "Shoulder pivot, leg splice, ankle and the 63 mm wheels", True),
    ("Rear", (0, -2600, 400), "Rear door and access opening, charge port and main switch band", True),
]


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


def render(executable, name, eye, size, scratch, ortho):
    target = scratch / f"{name}.png"
    camera = ",".join(str(v) for v in (*eye, *CENTRE))
    backend = ["--backend=manifold", "--render"] if "nightly" in executable.lower() else []
    fit = ["--viewall", "--autocenter"] if ortho else []
    result = subprocess.run(
        [executable, *backend, "-o", str(target), f"--imgsize={size},{size}",
         "--colorscheme=Tomorrow", f"--projection={'o' if ortho else 'p'}", f"--camera={camera}", *fit,
         "-D", 'part="assembly"', str(SCAD)],
        capture_output=True, text=True, timeout=3600)
    if result.returncode or not target.exists():
        raise RuntimeError(f"{name}: rc={result.returncode}\n{result.stderr[-2000:]}")
    print(f"rendered {name}", flush=True)
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


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--size", type=int, default=1700)
    parser.add_argument("--cell-width", type=int, default=1250)
    args = parser.parse_args()
    executable = openscad()
    scratch = ROOT / "output/drawings/_mockup"
    scratch.mkdir(parents=True, exist_ok=True)
    try:
        tiles = []
        for name, eye, caption, ortho in VIEWS:
            path = render(executable, name.replace(" ", "_").lower(), eye, args.size, scratch, ortho)
            tiles.append((name, caption, trim_white(Image.open(path).convert("RGB"))))

        cell_w, cell_h = args.cell_width, args.size
        margin, gap, header, footer, label = 56, 48, 168, 118, 112
        width = margin * 2 + cell_w * 2 + gap
        height = header + (cell_h + label) * 2 + gap + footer
        sheet = Image.new("RGB", (width, height), "white")
        draw = ImageDraw.Draw(sheet)
        draw.text((margin, 44), "fable-r2d2  /  final build mock-up", font=font(58, True), fill="#13202c")
        draw.text((margin, 116),
                  "Every printed part in its assembled place: 9 STL files, 12 printed pieces, "
                  "three-leg operating stance",
                  font=font(29), fill="#4b5b68")
        draw.line([(margin, header - 14), (width - margin, header - 14)], fill="#9fb0be", width=3)

        for index, (name, caption, tile) in enumerate(tiles):
            column, row = index % 2, index // 2
            x0 = margin + column * (cell_w + gap)
            y0 = header + row * (cell_h + label + gap)
            scaled = tile.copy()
            scaled.thumbnail((cell_w, cell_h), Image.LANCZOS)
            sheet.paste(scaled, (x0 + (cell_w - scaled.width) // 2, y0 + (cell_h - scaled.height) // 2))
            draw.text((x0, y0 + cell_h + 14), name, font=font(36, True), fill="#1d5a7a")
            draw.text((x0, y0 + cell_h + 62), caption, font=font(25), fill="#54636f")

        note = ("Rendered from cad/r2d2.scad part=\"assembly\", the same source the nine STL files are exported from. "
                "Motors and wheels are nominal purchased envelopes. Digital design: nothing printed, assembled or driven.")
        draw.line([(margin, height - footer + 6), (width - margin, height - footer + 6)], fill="#9fb0be", width=3)
        draw.text((margin, height - footer + 26), note, font=font(25), fill="#54636f")

        OUT.parent.mkdir(parents=True, exist_ok=True)
        sheet.save(OUT)
        digest = hashlib.sha256(OUT.read_bytes()).hexdigest()
        manifest = {"file": str(OUT.relative_to(ROOT)).replace("\\", "/"), "pixels": list(sheet.size),
                    "sha256": digest, "views": [v[0] for v in VIEWS], "projection": {v[0]: ("orthographic" if v[3] else "perspective") for v in VIEWS},
                    "source": "cad/r2d2.scad part=assembly", "physical_build": False}
        (ROOT / "output/drawings/mockup-manifest.json").write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
        print(f"PASS: {OUT} {sheet.size[0]}x{sheet.size[1]} sha256 {digest[:16]}")
    finally:
        shutil.rmtree(scratch, ignore_errors=True)


if __name__ == "__main__":
    main()
