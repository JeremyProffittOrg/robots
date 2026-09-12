# fable-r2d2 — a 317 mm printable R2-D2

A digital fabrication package for a 713 mm tall R2-D2 robot sized to a Bambu Lab H2D:
the body and dome are 317 mm in diameter (the 320 mm bed axis minus the 3 mm buffer), every
print stays under 315 mm tall (max height minus 5 mm), and the whole robot is nine STL files
(twelve printed pieces). Three feet each carry two Adafruit 3777 TT motors and four Adafruit
3766 wheels; a seventh motor and wheel spin the dome through a spring-tensioned friction
drive; a Raspberry Pi 4 runs the Wi-Fi control page, displays and sounds and an Adafruit
KB2040 drives the motors and lights; a 12 V 7 Ah sealed lead-acid battery lives on a shelf in
the lower body and charges through a panel port.

This is a design package. Nothing has been printed, assembled or driven. The physical tests
in the manual are part of the build.

## Start here

- `output/pdf/r2d2-assembly-manual.pdf` — the illustrated manual (overview, printing,
  purchased parts, mechanical and electrical design, step-by-step assembly with exploded
  diagrams, firmware, tests).
- `output/video/r2d2-assembly-and-operation.mp4` — narrated CAD animation of the assembly
  and simulated operation (captions in `assembly-captions.srt`).
- `output/drawings/` — MATLAB-style PNG drawing set and `r2d2-matlab-style-drawings.zip`.
- `bom/bill-of-materials.xlsx` — purchased parts with sources and prices, printed parts,
  filament; `bom/*.csv` are the sources.
- `stl/` — the nine printable meshes; `scripts/parts.json` gives quantity, orientation and
  which files are mirrored in the slicer for the left side.
- `docs/` — `mechanical.md`, `assembly.md`, `electrical.md`, `firmware.md`,
  `stability.json`, `verification.json`.
- `electronics/` — four circuit sheets (SVG) and the wire-by-wire schedule.
- `firmware/pi/` and `firmware/kb2040/` — control server and CircuitPython motor firmware.
- `research/` — the 59 reviewed reference images, club-drawing proportions, verified
  component facts and the load screening the design rests on.
- `cad/` — parametric OpenSCAD source (`params.scad` holds every dimension).

## Rebuild

From `C:/dev/robots/fable-r2d2` (OpenSCAD nightly at `~/tools/openscad-nightly`, Bambu
Studio, Python 3.14 with the packages listed in `plan.md`, FFmpeg, Chrome, Node):

```powershell
python scripts/export_cad.py          # nine STLs + cad/validation.json
python scripts/slice_check.py         # Bambu Studio H2D slice of every STL
python scripts/stability.py           # mass, centre of gravity, tip margins
python scripts/electronics.py         # circuit sheets and wiring.csv
python scripts/build_bom.py           # bill-of-materials.xlsx
python scripts/draw_robot.py          # MATLAB-style drawings
python scripts/build_manual.py        # assembly manual PDF
python scripts/render_video.py        # assembly and operation video
python scripts/verify.py              # package checks -> docs/verification.json
```

## Key numbers

See `plan.md` (locked decisions, verified facts, execution log) and `docs/mechanical.md`.
