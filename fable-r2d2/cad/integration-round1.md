# Integration round 1 — 2026-09-12

All commands run from `C:/dev/robots/fable-r2d2`. OpenSCAD nightly 2026.09.11
(`C:/Users/Jeremy/tools/openscad-nightly/openscad.com --backend=manifold`) for every export and
render; Bambu Studio CLI (`C:/Program Files/Bambu Studio/bambu-studio.exe`) for slicing.

## Headline

- 4 of 10 parts delivered and PASS export validation: `dome`, `foot_outer`, `foot_center`, `head_drive`.
- 6 of 10 parts are NOT delivered: `cad/body.scad` (3 lines) and `cad/legs.scad` (6 lines) contain
  only empty stub modules, so `body_upper`, `body_lower`, `tray_electronics`, `leg_upper`,
  `leg_lower`, `leg_center` export as "Current top level object is empty" and have no STL.
- Interference: all eight `check_*` parts are empty. Only `check_head_drive` (head_drive vs dome) is
  a real result; the other seven are vacuous because one side is an empty stub.
- Slice: `foot_outer`, `foot_center`, `head_drive` PASS. `dome` FAILS in Bambu Studio because
  auto-generated supports for the outer-skin overhangs fall outside the 320 mm bed axis (the dome is
  316.83 mm across, 1.6 mm margin each side). With supports off the same STL slices (1018.7 g,
  24.3 h) but with a "floating regions" warning.
- Renders: `scripts/export_cad.py --views` produced four identical blank PNGs (12512 bytes, md5
  `d94b54a3134c9dfd90e717b45c9ed499`) because the preview path hits "Normalized tree is growing past
  100000 elements. Aborting normalization / CSG normalization resulted in an empty tree". The four
  views were re-rendered with `--backend=manifold --render` and the same cameras and saved as
  `cad/assembly.png`, `cad/rear.png`, `cad/exploded.png`, `cad/section.png`.

## 1. Export and validation — `python scripts/export_cad.py`

Full run (all parts) aborted on the first stub part:

```
RuntimeError: body_lower: rc=1
EXIT=1
```

Manual re-run of that part shows the reason (stdout, not stderr):

```
"C:/Users/Jeremy/tools/openscad-nightly/openscad.com" --backend=manifold -o <scratch>/body_lower.stl -D part="body_lower" cad/r2d2.scad
Current top level object is empty.
```

`cad/body.scad` and `cad/legs.scad` as found (verbatim, whole files):

```
module body_upper() { }
module body_lower() { }
module tray_electronics() { }
```

```
module leg_upper_native() { }
module leg_lower_native() { }
module leg_upper() { }
module leg_lower() { }
module leg_center_native() { }
module leg_center() { }
```

Delivered parts — `python scripts/export_cad.py --parts dome foot_outer foot_center head_drive`:

```
EXPORTED head_drive
EXPORTED foot_center
EXPORTED foot_outer
EXPORTED dome
PASS dome: [316.8, 316.8, 195.4] mm, solids=1, watertight=True
PASS foot_outer: [181.8, 265.0, 105.2] mm, solids=1, watertight=True
PASS foot_center: [123.3, 180.2, 111.9] mm, solids=1, watertight=True
PASS head_drive: [116.5, 73.1, 39.9] mm, solids=1, watertight=True
EXIT_PARTS=0
```

`python scripts/export_cad.py --check-only` (writes `cad/validation.json` and `bom/printed-parts.csv`):

```
PASS dome: [316.8, 316.8, 195.4] mm, solids=1, watertight=True
PASS foot_outer: [181.8, 265.0, 105.2] mm, solids=1, watertight=True
PASS foot_center: [123.3, 180.2, 111.9] mm, solids=1, watertight=True
PASS head_drive: [116.5, 73.1, 39.9] mm, solids=1, watertight=True
{
  "design": "fable-r2d2",
  "unique_stl_files": 10,
  "printed_piece_count": 5,
  "envelope_mm": [322, 317, 320],
  "all_pass": false,
  "solid_material_upper_bound_g": 5134.9,
  "physical_fit_verified": false,
  "physical_strength_verified": false
}
FAILED meshes: body_upper, body_lower, leg_upper, leg_lower, leg_center, tray_electronics
EXIT_CHECKONLY=1
```

Per-part rows from `cad/validation.json`:

| part | pass | size x,y,z mm | volume cm3 | solid mass g | faces | watertight | winding | solids | fits |
|---|---|---|---|---|---|---|---|---|---|
| dome | PASS | 316.83, 316.83, 195.36 | 993.84 | 1262.2 | 47494 | True | True | 1 | True |
| body_upper | FAIL | missing STL | | | | | | | |
| body_lower | FAIL | missing STL | | | | | | | |
| leg_upper | FAIL | missing STL | | | | | | | |
| leg_lower | FAIL | missing STL | | | | | | | |
| foot_outer | PASS | 181.8, 265.0, 105.2 | 1285.42 | 1632.5 | 11032 | True | True | 1 | True |
| leg_center | FAIL | missing STL | | | | | | | |
| foot_center | PASS | 123.3, 180.2, 111.9 | 394.77 | 501.4 | 8744 | True | True | 1 | True |
| head_drive | PASS | 116.5, 73.099, 39.914 | 83.73 | 106.3 | 6666 | True | True | 1 | True |
| tray_electronics | FAIL | missing STL | | | | | | | |

STL bounds (trimesh, native/print frame):

```
dome        [[-158.42 -158.42 0.], [158.42 158.42 195.36]]
foot_outer  [[-120.15 -121.6  0.], [ 61.65 143.4  105.2 ]]
foot_center [[ -61.65  -90.1  0.], [ 61.65  90.1  111.9 ]]
head_drive  [[ -60.5    74.   0.], [ 56.   147.1   39.91]]
```

## 2. Interference checks

Command per check:
`"C:/Users/Jeremy/tools/openscad-nightly/openscad.com" --backend=manifold -o <scratch>/check_x.stl -D part="check_x" cad/r2d2.scad`

```
=== check_seam
Current top level object is empty.
NO STL
=== check_dome
Current top level object is empty.
NO STL
=== check_head_drive
Current top level object is empty.
NO STL
=== check_shoulder
Current top level object is empty.
NO STL
=== check_ankle
Current top level object is empty.
NO STL
=== check_leg_split
Current top level object is empty.
NO STL
=== check_center
Current top level object is empty.
NO STL
=== check_tray
Current top level object is empty.
NO STL
CHECKS_EXIT=0
```

| check | operands | verdict |
|---|---|---|
| check_seam | body_lower vs body_upper | empty — VACUOUS (both operands are empty stubs) |
| check_dome | body_upper vs dome | empty — VACUOUS (body_upper is an empty stub) |
| check_head_drive | head_drive_native vs (body_upper + dome) | empty — head_drive vs dome: NO INTERFERENCE (real); vs body_upper: vacuous |
| check_shoulder | body_upper vs leg_upper_native | empty — VACUOUS (both stubs) |
| check_ankle | leg_lower_native vs foot_outer | empty — VACUOUS (leg_lower_native is an empty stub) |
| check_leg_split | leg_upper_native vs leg_lower_native | empty — VACUOUS (both stubs) |
| check_center | leg_center_native vs (body_lower + foot_center) | empty — VACUOUS (leg_center_native is an empty stub) |
| check_tray | tray_electronics vs body_upper | empty — VACUOUS (both stubs) |

Wheel-to-floor arithmetic (params): `foot_clear = 12`, `wheel_axle_z = 31.5 - foot_clear = 19.5`
in the foot frame, wheel diameter 63 mm (radius 31.5) — wheel bottom sits at z = 12 + 19.5 - 31.5 = 0.0,
exactly on the floor. Consistent in the section render.

## 3. Slice — `python scripts/slice_check.py --parts dome foot_outer foot_center head_drive`

```
FAIL dome: 0 g, 0.0 h, One of the plate is empty or has no object fully inside it. Please check that the 3mf contains no empty plate in Bambu Studio before uploading.
PASS foot_outer: 811 g, 25.8 h, Success.
PASS foot_center: 314 g, 9.5 h, Success.
PASS head_drive: 81 g, 3.1 h, Success.
{
  "checked_at_utc": "2026-09-12T12:41:43.022506+00:00",
  "test_type": "Local Bambu Studio CLI slicing of package meshes; no printer connection or physical print",
  "profiles": {
    "machine": "Bambu Lab H2D 0.4 nozzle",
    "process": "0.20mm Standard @BBL H2D",
    "overrides": {
      "wall_loops": "5", "top_shell_layers": "6", "bottom_shell_layers": "6",
      "sparse_infill_density": "30%", "sparse_infill_pattern": "gyroid",
      "enable_support": "1", "support_type": "tree(auto)", "support_on_build_plate_only": "0",
      "brim_type": "no_brim", "skirt_loops": "0"
    },
    "bed": "Textured PEI Plate"
  },
  "all_pass": false,
  "total_predicted_mass_g": 2017.9,
  "total_predicted_time_h": 64.1
}
Slice check failed
EXIT_SLICE=1
```

| part | pass | predicted mass g | predicted time s | h | bbox (x, y, w, d, h) |
|---|---|---|---|---|---|
| dome | FAIL | — | — | — | return_code -50 |
| foot_outer | PASS | 811.27 | 92797.49 | 25.78 | 42.5, 69.1, 265.0, 181.8, 105.2 |
| foot_center | PASS | 314.14 | 34233.19 | 9.51 | 113.35, 69.9, 123.3, 180.2, 111.9 |
| head_drive | PASS | 81.26 | 11053.78 | 3.07 | 116.75, 123.45, 116.5, 73.1, 39.9 |

Total for the four delivered parts (quantity-weighted, from the script): 2017.9 g, 64.1 h.
The six missing parts were not sliced (no STL).

### Dome slice diagnosis (scratch experiments, same machine/process/filament profiles)

| variant | result |
|---|---|
| as exported, `--arrange 0` | return_code -50 "One of the plate is empty or has no object fully inside it" (STL centred on 0,0 is half off the plate; the script's `--arrange 1` also fails to place it) |
| translated to bed centre (162.5, 160), supports ON (script overrides) | return_code -102 "Found G-code in unprintable area of multi-extruder printers after slicing" |
| translated to bed centre, `support_on_build_plate_only = 1` | return_code -102 (same) |
| translated to bed centre, `support_type = normal(auto)` | return_code -104 "Found G-code outside of the printable area. The issue may be caused by support, wipe tower, brim, or skirt." |
| scaled 0.99 (313.7 mm), bed centre, supports ON | return_code -102 (same) |
| translated to X=175 (right of centre) | return_code -66 "Some filaments cannot be mapped to correct extruders for multi-extruder Printer." (object leaves the left-extruder 0..325 area) |
| translated to bed centre, `enable_support = 0` | return_code 0 "Success.", 1018.70 g, 87477.7 s (24.3 h), warning "It seems object dome_full_x162.stl has floating regions. Please re-orient the object or enable support generation." |

Conclusion: the dome geometry fits the bed, but Bambu auto-support for its outer-skin overhangs is
generated outside the dome footprint and therefore outside the 320 mm bed axis (1.6 mm margin).
Outer-skin overhang faces (trimesh, normal_z < -0.5, r > 145 mm, angle measured from +Y front toward
+X, total 6366.8 mm2), largest clusters:

```
angle_from_front=  135 deg  z=  65 mm  area=  224.6 mm2  r_max= 150.0  steepest normal_z=-0.99   (rear logic display recess, upper ledge)
angle_from_front=   25 deg  z=  30 mm  area=  194.7 mm2  r_max= 158.2  steepest normal_z=-1.00   (holoprojector 1 barrel underside)
angle_from_front=  140 deg  z=  35 mm  area=  178.8 mm2  r_max= 149.1  steepest normal_z=-0.99   (rear logic display recess, lower ledge)
angle_from_front=  -25 deg  z=  45 mm  area=  163.7 mm2  r_max= 152.3  steepest normal_z=-0.84   (front logic display, lower window)
angle_from_front=  170 deg  z=  40 mm  area=  162.2 mm2  r_max= 157.9  steepest normal_z=-0.97   (rear PSI / holoprojector 2 underside)
angle_from_front=  135 deg  z=  35 mm  area=  161.5 mm2  r_max= 154.9  steepest normal_z=-0.99
angle_from_front=  -25 deg  z=  85 mm  area=  152.5 mm2  r_max= 154.8  steepest normal_z=-0.98   (front logic display, upper window)
angle_from_front=    5 deg  z=  75 mm  area=  134.3 mm2  r_max= 156.2  steepest normal_z=-1.00   (radar eye housing underside)
angle_from_front=  165 deg  z=  45 mm  area=  123.8 mm2  r_max= 158.1  steepest normal_z=-0.90
angle_from_front=   -5 deg  z=  75 mm  area=  115.9 mm2  r_max= 156.2  steepest normal_z=-1.00   (radar eye housing underside)
angle_from_front=  175 deg  z=  45 mm  area=  108.7 mm2  r_max= 158.1  steepest normal_z=-0.95
```

Interior overhang (the ellipsoid ceiling above z ~140 mm, r 90-100 mm, about 45700 mm2) is inside
the footprint and is what the parts.json note ("tree supports under the top disc only") expects.

## 4. Renders

`OPENSCAD=C:/Users/Jeremy/tools/openscad-nightly/openscad.com python scripts/export_cad.py --views`:

```
Rendered assembly
Rendered rear
Rendered exploded
Rendered section
EXIT_VIEWS=0
```

but every output was a blank 1600x1600 image:

```
d94b54a3134c9dfd90e717b45c9ed499 *cad/assembly.png
d94b54a3134c9dfd90e717b45c9ed499 *cad/rear.png
d94b54a3134c9dfd90e717b45c9ed499 *cad/exploded.png
d94b54a3134c9dfd90e717b45c9ed499 *cad/section.png
```

Re-running the assembly camera with visible stderr:

```
Compiling design (CSG Products normalization)...
WARNING: Normalized tree is growing past 100000 elements. Aborting normalization.
WARNING: CSG normalization resulted in an empty tree
```

Re-rendered with full evaluation (the script's cameras, plus `--backend=manifold --render`), all four exit 0:

```
"C:/Users/Jeremy/tools/openscad-nightly/openscad.com" --backend=manifold --render -o cad/assembly.png --imgsize=1600,1600 --colorscheme=Tomorrow --projection=o --viewall --autocenter --camera=1400,-1700,1100,0,0,330 -D part="assembly" cad/r2d2.scad
"C:/Users/Jeremy/tools/openscad-nightly/openscad.com" --backend=manifold --render -o cad/rear.png     ... --camera=-1400,1700,1000,0,0,330 -D part="assembly" cad/r2d2.scad
"C:/Users/Jeremy/tools/openscad-nightly/openscad.com" --backend=manifold --render -o cad/exploded.png ... --camera=1500,-1800,1400,0,0,450 -D part="exploded" cad/r2d2.scad
"C:/Users/Jeremy/tools/openscad-nightly/openscad.com" --backend=manifold --render -o cad/section.png  ... --camera=1400,-1700,900,0,0,330 -D part="section" cad/r2d2.scad
assembly: Genus 54, Vertices 44622, Facets 89456
exploded: Genus 55, Vertices 44648, Facets 89512
rear:     Genus 54, Vertices 44622, Facets 89456
section:  Genus 29, Vertices 23483, Facets 47078
```

Visual review against `research/drawings/photos/lucasfilm-r2.jpeg` and `body-front.jpg`:

1. No body: both body rings and the electronics tray are absent. The dome and head drive float at
   their correct stance height (~463 mm shoulder height, 18 deg tilt) with nothing under them.
   Owner: body.
2. No legs: outer legs and centre leg are absent; the three feet stand alone on the floor. Owner: legs.
3. Feet: three feet are on the floor with the wheels touching z=0 (wheel bottom = foot_clear +
   wheel_axle_z - 31.5 = 0). Foot spacing (leg_track 363.4) and the centre foot ahead of the skirt
   look plausible; a final proportion check needs the body and legs present. Owner: feet, no defect seen.
4. Dome: recognisable R2 dome — radar eye housing, front logic display windows, front PSI, three
   holoprojectors, pie panels, top disc, rear logic display. Nothing floating or missing. The dome
   tilts with the body (18 deg) as intended for the three-leg stance. Owner: dome, no defect seen.
5. Head drive: the pivoting mount hangs below the dome plate at the body top plate height; correct
   once the body exists. Owner: head_drive, no defect seen.
6. Camera labels are inverted relative to the FRAMES comment (+Y = front): `cad/rear.png` (camera at
   y = +1700) shows the droid's front (radar eye and logic displays visible) and `cad/assembly.png`
   (camera at y = -1700) shows the rear. The dome itself faces +Y correctly (dome_spin = 0). Owner:
   scripts/export_cad.py views() cameras (integrator).
7. `scripts/export_cad.py views()` renders with the OpenSCAD preview path, which the nightly aborts
   on this model (CSG tree > 100000 elements) and writes blank PNGs. The 2021.01 build would take
   the same path. Add `--render` (and `--backend=manifold` for the nightly) or lower the detail in
   the assembly module. Owner: scripts (integrator).

## Problems by owner

- body — `cad/body.scad` is an empty stub; body_upper, body_lower, tray_electronics have no geometry, no STL, and every check involving them is vacuous.
- legs — `cad/legs.scad` is an empty stub; leg_upper, leg_lower, leg_center have no geometry, no STL, and every check involving them is vacuous.
- dome — slice FAIL: outer-skin overhangs (radar eye housing underside z~75, HP1 barrel underside z~30 at +25 deg, front logic display recess ledges at -25 deg z 45/85, rear logic display recess ledges at 135-140 deg z 35/65, rear PSI/HP2 undersides at 165-180 deg z 40-50) draw auto-support outside the 316.83 mm footprint, which exceeds the 320 mm bed axis. Make those external features self-supporting (45 deg chamfers under the eye housing and HP barrels, chamfered/arched recess tops) so the dome slices with supports on; with supports off the same STL slices at 1018.7 g / 24.3 h but Bambu reports floating regions.
- scripts (integrator) — `export_cad.py` views() writes blank PNGs (preview CSG normalization aborts); the "assembly"/"rear" camera labels are swapped relative to +Y = front; full export aborts at the first stub part with an empty stderr message (the "Current top level object is empty" text is on stdout).
- scripts (integrator) — `slice_check.py` uses `--arrange 1`, which fails to place a 316.83 mm object on the 320 mm axis; centring the STL on the plate (162.5, 160) before slicing was required to get past return_code -50 in the experiments above.

## Files written by this round

- `cad/validation.json`, `bom/printed-parts.csv` (by export_cad.py --check-only)
- `cad/h2d-slice-check.json` (by slice_check.py --parts ...)
- `cad/assembly.png`, `cad/rear.png`, `cad/exploded.png`, `cad/section.png` (manifold --render)
- `cad/integration-round1.md` (this file)
- `stl/dome.stl`, `stl/foot_outer.stl`, `stl/foot_center.stl`, `stl/head_drive.stl` (re-exported)
