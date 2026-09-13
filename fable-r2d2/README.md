# fable-r2d2 — a 317 mm printable R2-D2, revision D

A digital fabrication package for an R2-D2 robot sized to a Bambu Lab H2D. The body and dome
are 317 mm in diameter (the 320 mm bed axis minus the 3 mm buffer), and every print stays under
315 mm tall (max height minus 5 mm). `scripts/parts.json` lists the STL files and how many of
each to print. Three feet each carry two Adafruit 3777 TT motors and four Adafruit 3766 wheels.
A seventh motor and wheel spin the dome through a spring-tensioned friction drive. A Raspberry
Pi 4 runs the Wi-Fi control page, the displays and the sounds. An Adafruit KB2040 drives the
motors, the lights and the stance change. A 12 V 7 Ah sealed lead-acid battery sits on a shelf
in the lower body and charges through a panel port.

Revision D makes the stance change motorized and interlocked. An Actuonix P16 linear actuator
drives the centre leg along two guide shafts. Retracted, the robot stands still on two feet with
the centre wheels lifted clear of the floor. Deployed, the centre foot is on the floor ahead of
the outer feet and the body is tilted back for driving. A spring-pin lock holds each shoulder at
both stances; an MG995 servo releases it and an Omron SS-01GL switch reads it. The KB2040 refuses
drive during a change, on two feet, and in any unknown or fault state. Revision C, the unpowered
design, is frozen as git tag `fable-r2d2-revision-c` (`docs/revision-c.json`).

This is a design package. Nothing has been printed, assembled, wired or driven. The physical
tests in the manual are part of the build.

## Start here

- `output/pdf/r2d2-assembly-manual.pdf` — the illustrated manual: overview, printing, purchased
  parts, mechanical design, the stance change, electrical design, step-by-step assembly with
  exploded diagrams, firmware, tests and the verification record.
- `output/video/r2d2-assembly-and-operation.mp4` — narrated CAD animation of the assembly, a
  simulated drive and both stance changes (captions in `assembly-captions.srt`).
- `output/drawings/` — MATLAB-style PNG drawing set, the mock-up of both stances and the
  transition (`00_final_build_mockup.png`), and `r2d2-matlab-style-drawings.zip`.
- `bom/bill-of-materials.xlsx` — purchased parts with sources and prices, printed parts,
  filament, the changes since revision C and the stock notes; `bom/*.csv` are the sources.
- `stl/` — the printable meshes; `scripts/parts.json` gives quantity, orientation and which
  files are mirrored in the slicer for the left side.
- `docs/` — `mechanical.md`, `assembly.md`, `electrical.md`, `firmware.md`, `stability.json`,
  `stance-check.json`, `verification.json`.
- `electronics/` — the circuit sheets (SVG, sheet 05 is the stance change) and the wire-by-wire
  schedule.
- `firmware/pi/` and `firmware/kb2040/` — control server and CircuitPython motor and stance
  firmware.
- `research/` — the reviewed reference images, club-drawing proportions, verified component
  facts and the load screening the design rests on.
- `cad/` — parametric OpenSCAD source. `params.scad` holds every dimension; `stance.scad` holds
  the stance kinematics, the carriage and the lock. `-D stance_s=<mm>` on `r2d2.scad` renders
  any stance pose.

## Rebuild

From `C:/dev/robots/fable-r2d2` (OpenSCAD nightly at `~/tools/openscad-nightly`, Bambu
Studio, Python 3.14 with the packages listed in `plan.md`, FFmpeg, Chrome, Node), in this order:

```powershell
python scripts/export_cad.py          # STLs + cad/validation.json + bom/printed-parts.csv
python scripts/slice_check.py         # Bambu Studio H2D slice of every STL
python scripts/stability.py           # mass, centre of gravity, support margins in both stances
python scripts/check_stance.py        # sampled transition check -> docs/stance-check.json
python scripts/electronics.py         # circuit sheets and wiring.csv
python scripts/build_bom.py           # bill-of-materials.xlsx
python scripts/draw_robot.py          # MATLAB-style drawings, including sheet 17 (stance change)
python scripts/render_mockup.py       # both stances and the transition
python scripts/render_video.py        # assembly, drive and stance-change video
python scripts/verify.py --only images,cad,stance,bom,wiring,firmware,audio,drawings,mockup,video
python scripts/build_manual.py        # assembly manual PDF (embeds the verification record above)
python scripts/verify.py              # all checks -> docs/verification.json, "revision": "D" only if all pass
python scripts/deliver.py --dry-run   # the delivery email, measured, nothing sent
```

## Key numbers

See `plan.md` (locked decisions, verified facts, execution log), `docs/mechanical.md` and the
cover of the manual, which reads every count from the package manifests.
