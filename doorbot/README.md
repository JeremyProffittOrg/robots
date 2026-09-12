# doorbot

An automatic door closer built from seven 3D-printed designs in Bambu Lab PLA Tough+, one
Adafruit 3777 TT gearbox motor, and a LilyGO TTGO T-Display ESP32 powered from USB at 5 V.

It screws to the hinge-side jamb reveal, in the rebate behind the closed door on the push
side, and reels a 1.2 mm Dyneema cable in to swing the door shut. Four K&J D84 magnets at the
latch edge take the last few millimetres and hold the leaf closed.

**Read [../deploy.md](../deploy.md) before touching infrastructure.** Publication happens only
through `.github/workflows/publish-doorbot.yml` on a push to `main`.

## What it does

| trigger | what happens |
| --- | --- |
| hand wave over the engraved ring | two consecutive VL53L4CD readings inside 20-250 mm |
| two kicks on the door | two LIS3DH click events 120-900 ms apart, felt through the jamb |
| doorway clear for 30 s while open | it closes on its own |
| something in the doorway | refuses, retries every 19 s for a minute, then buzzes and shows `CLEAR THE WAY` |
| someone pulls the door open | the drum free-spools; about 1 N extra at the door edge, powered or not |

## The number that decides the design

A cable that leaves the jamb **on** the closed-door plane has a moment arm of exactly zero
when the door is shut: the exit, the hinge axis and the anchor are collinear, and no tension
whatever can close the last degree. The exit is therefore offset 40 mm off that plane, which
keeps the included angle between 29 and 119 degrees and the arm between 42 and 54 mm.

## Verify it

```
python scripts/verify.py
```

Runs, and must pass, all of: the mechanism analysis (`check_mechanism.py`), the CAD analysis
(`check_cad.py`), the wiring and pin-map check (`electronics.py`), the BOM (`bom.py`), a
consistency check between `cad/params.scad` and `firmware/include/config.h`, the host
behaviour tests (`pio test -e native`, 13 cases) and the target firmware build
(`pio run -e tdisplay`). The native environment needs a host `g++` on `PATH`; `verify.py`
finds a WinGet or MSYS2 toolchain automatically if one is installed.

Regenerate artefacts with `export_cad.py` (STLs and renders), `draw_diagrams.py` (ten
drawings), `build_guide.py` (the 14-page PDF), `render_video.py` (the MP4) and `package.py`
(the delivery manifest and ZIP).

## Present limitation

**No prototype has been built or tested.** Everything in this package is analysis of the
design plus a firmware build. Two figures in particular are modelled rather than measured and
are called out in the guide: residential butt-hinge friction, for which no published figure
was found, and how much of a kick reaches a door jamb, for which no measurement exists in the
literature searched. The accelerometer threshold must be calibrated on the actual door.

The two time-of-flight cones cover the doorway, not the swing arc on the pull side. Contact
there is caught by the encoder stall watchdog within 250 ms, and the DRV8833's own 1.0 A
hardware chop caps the push at 151 N of cable tension whatever the firmware does.
