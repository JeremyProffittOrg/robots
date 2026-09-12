# Integration round 2 — 2026-09-12

All commands run from `C:/dev/robots/fable-r2d2`. OpenSCAD nightly
(`C:/Users/Jeremy/tools/openscad-nightly/openscad.com --backend=manifold`) for every export and
render; Bambu Studio CLI (`C:/Program Files/Bambu Studio/bambu-studio.exe`) for slicing.
No `.scad` file was edited in this round.

## Headline

- 7 of 10 parts delivered and PASS export validation: `dome`, `leg_upper`, `leg_lower`,
  `foot_outer`, `leg_center`, `foot_center`, `head_drive` (legs are new since round 1).
- 3 of 10 parts are NOT delivered: `cad/body.scad` is still the 3-line stub
  (md5 `74675e4fa13c399e9079489783bfc03e`), so `body_upper`, `body_lower` and
  `tray_electronics` have no geometry and no STL. `export_cad.py` (all parts) aborts on
  `body_upper` before validation; `--check-only` writes `cad/validation.json` with
  `all_pass: false`.
- Interference: 7 of 8 `check_*` parts are empty; `check_leg_split` produces a zero-volume
  contact-only mesh (0.0 mm3, 21 open slivers on the comb-joint faces) — acceptable. Five of
  the eight checks are still vacuous on the body side (body stub).
- Slice: 6 of 7 delivered parts PASS (3783.9 g, 119.4 h quantity-weighted). `dome` FAILS in
  `slice_check.py` with return_code -50 at the `--arrange 1` step; the same STL centred on the
  bed slices with the script's own support settings: return_code 0, "Success.", no warning,
  1243.9 g, 35.37 h. The round-1 outside-footprint support problem is gone; the remaining
  failure is the script's arrange step.
- Renders: `export_cad.py --views` still writes four blank PNGs (preview CSG normalisation
  aborts). Re-rendered with `--backend=manifold --render` into `cad/assembly.png`, `cad/rear.png`,
  `cad/exploded.png`, `cad/section.png`, plus `cad/side.png` and `cad/feet_front.png`.
  Visual review: legs and feet are correct and on the floor; dome and head drive float at the
  correct stance height because the body is absent; the render-only motor envelopes in
  `r2d2.scad` `wheels_and_motors_outer()` stand the motor cans vertical and 32 mm through the
  floor (render artefact, not a part defect).

## 1. Export and validation — `python scripts/export_cad.py`

Full run (all parts, background, log `export_all.log`), verbatim tail:

```
RuntimeError: body_upper: rc=1

EXIT=1
```

The seven delivered parts were exported by the same run before the abort (all
`stl/*.stl` timestamped 11:12:16–11:12:17):

```
-rw-r--r-- 1 Jeremy 197121 2496784 11:12:17 stl/dome.stl
-rw-r--r-- 1 Jeremy 197121  422484 11:12:17 stl/foot_center.stl
-rw-r--r-- 1 Jeremy 197121  772684 11:12:17 stl/foot_outer.stl
-rw-r--r-- 1 Jeremy 197121  387684 11:12:17 stl/head_drive.stl
-rw-r--r-- 1 Jeremy 197121  372884 11:12:17 stl/leg_center.stl
-rw-r--r-- 1 Jeremy 197121  359184 11:12:17 stl/leg_lower.stl
-rw-r--r-- 1 Jeremy 197121  541084 11:12:16 stl/leg_upper.stl
```

`cad/body.scad` as found (verbatim, whole file):

```
module body_upper() { }
module body_lower() { }
module tray_electronics() { }
```

`python scripts/export_cad.py --check-only` (writes `cad/validation.json`, `bom/printed-parts.csv`):

```
PASS dome: [316.8, 316.8, 199.1] mm, solids=1, watertight=True
PASS leg_upper: [289.7, 139.4, 50.8] mm, solids=1, watertight=True
PASS leg_lower: [232.0, 100.0, 58.2] mm, solids=1, watertight=True
PASS foot_outer: [181.8, 265.0, 105.2] mm, solids=1, watertight=True
PASS leg_center: [140.0, 100.0, 47.5] mm, solids=1, watertight=True
PASS foot_center: [123.3, 180.2, 111.9] mm, solids=1, watertight=True
PASS head_drive: [116.5, 72.3, 39.9] mm, solids=1, watertight=True
{
  "design": "fable-r2d2",
  "unique_stl_files": 10,
  "printed_piece_count": 10,
  "envelope_mm": [
    322,
    317,
    320
  ],
  "all_pass": false,
  "solid_material_upper_bound_g": 8168.9,
  "physical_fit_verified": false,
  "physical_strength_verified": false
}
FAILED meshes: body_upper, body_lower, tray_electronics
EXIT_CHECKONLY=1
```

Per-part rows from `cad/validation.json`:

| part | pass | qty | size x,y,z mm | volume cm3 | solid mass g | faces | watertight | winding | solids | fits |
|---|---|---|---|---|---|---|---|---|---|---|
| dome | PASS | 1 | 316.83, 316.83, 199.139 | 1027.01 | 1304.3 | 49934 | True | True | 1 | True |
| body_upper | FAIL | | missing STL | | | | | | | |
| body_lower | FAIL | | missing STL | | | | | | | |
| leg_upper | PASS | 2 | 289.7, 139.4, 50.79 | 1137.99 | 1445.2 | 10820 | True | True | 1 | True |
| leg_lower | PASS | 2 | 232.0, 100.0, 58.25 | 525.47 | 667.3 | 7182 | True | True | 1 | True |
| foot_outer | PASS | 2 | 181.8, 265.0, 105.2 | 673.21 | 855.0 | 15452 | True | True | 1 | True |
| leg_center | PASS | 1 | 140.0, 100.0, 47.518 | 258.43 | 328.2 | 7456 | True | True | 1 | True |
| foot_center | PASS | 1 | 123.3, 180.2, 111.9 | 389.49 | 494.6 | 8448 | True | True | 1 | True |
| head_drive | PASS | 1 | 116.5, 72.283, 39.914 | 84.11 | 106.8 | 7752 | True | True | 1 | True |
| tray_electronics | FAIL | | missing STL | | | | | | | |

STL bounds (trimesh, print frame):

```
dome         [[-158.42, -158.42, 0.0], [158.42, 158.42, 199.14]]
leg_upper    [[-144.85, -69.7, 0.0], [144.85, 69.7, 50.79]]
leg_lower    [[64.1, -50.0, 0.0], [296.1, 50.0, 58.25]]
foot_outer   [[-120.15, -121.6, 0.0], [61.65, 143.4, 105.2]]
leg_center   [[-70.0, -50.0, -0.0], [70.0, 50.0, 47.52]]
foot_center  [[-61.65, -90.1, 0.0], [61.65, 90.1, 111.9]]
head_drive   [[-60.5, 74.0, 0.0], [56.0, 146.28, 39.91]]
```

Changes since round 1: dome height 195.36 -> 199.14 mm (volume 993.84 -> 1027.01 cm3);
foot_outer volume 1285.42 -> 673.21 cm3 (hollowed); head_drive y 73.099 -> 72.283 mm.

Every OpenSCAD run also echoes this from `cad/head_drive.scad` line 169:

```
ECHO: "WARNING head_drive: params head_slot[1] = 42 is narrower than the 58 mm the 63 mm wheel chord needs (recommended 60)"
```

`cad/params.scad` line 105: `head_slot = [36, 42];`. The head_drive file asks for `[36, >= 58]`.
The body top plate slot is cut by `body_upper` (not yet delivered), so the mismatch is between
params and head_drive and lands on the body owner when the slot is cut.

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
   Top level object is a 3D object (manifold):
   Status:     NoError
   Genus:      -20
   Vertices:      101
   Facets:        118
STL PRODUCED 37703 bytes
=== check_center
Current top level object is empty.
NO STL
=== check_tray
Current top level object is empty.
NO STL
CHECKS_EXIT=0
```

`check_leg_split.stl` measured with trimesh:

```
volume mm3: 0.0 watertight: False faces: 118
bounds: [[166.5, 32.509, 242.243], [196.9, 97.365, 263.316]] extents: [30.4, 64.856, 21.073]
components: 21   (every component volume 0.0; largest bounds [[166.5, 32.51, 242.24], [196.9, 58.28, 250.62]])
```

The 21 zero-volume slivers lie on the comb-joint faces at the `leg_split_z = -220` split
(assembly frame x 166.5–196.9 = the 30.4 mm strut thickness, z 242–263), i.e. exact contact
planes between the leg_lower tongue and the leg_upper slot. Accepted.

| check | operands | volume mm3 | verdict |
|---|---|---|---|
| check_seam | body_lower vs body_upper | — (empty) | VACUOUS (both operands are empty stubs) |
| check_dome | body_upper vs dome | — (empty) | VACUOUS (body_upper is an empty stub) |
| check_head_drive | head_drive_native vs (body_upper + dome) | — (empty) | head_drive vs dome: NO INTERFERENCE (real); vs body_upper: vacuous |
| check_shoulder | body_upper vs leg_upper_native | — (empty) | VACUOUS (body_upper is an empty stub) |
| check_ankle | leg_lower_native vs foot_outer | — (empty) | NO INTERFERENCE (real) |
| check_leg_split | leg_upper_native vs leg_lower_native | 0.0 | CONTACT PLANES ONLY (real) — accepted |
| check_center | leg_center_native vs (body_lower + foot_center) | — (empty) | leg_center vs foot_center: NO INTERFERENCE (real); vs body_lower: vacuous |
| check_tray | tray_electronics vs body_upper | — (empty) | VACUOUS (both stubs) |

Wheel-to-floor check (render envelopes in the assembly frame, right outer foot, trimesh
bounds of `at_foot(1) wheels_and_motors_outer()` split into wheels and motors):

```
wheels_only bounds (assembly frame): [[143.4, 39.66, 0.0], [220.0, 192.66, 63.0]]
motors_only bounds (assembly frame): [[163.7, 59.94, -32.05], [200.3, 172.38, 42.75]]
```

Wheel bottoms sit at z = 0.0 exactly (on the floor). The motor envelope in `r2d2.scad`
`wheels_and_motors_outer()` (`rotate([0, 0, 90]) rotate([0, -90, 0]) tt_motor()`) stands the
motor can vertically and reaches z = -32.05, 32 mm below the floor. `cad/feet.scad`
`ft_motor_at()` tilts the real motor pockets (`rotate([90 - phi, 0, 0]) rotate([0, 0, -90])`),
so this is a render-envelope mismatch in `r2d2.scad`, not a foot defect; it shows as pegs under
every foot in `cad/assembly.png`, `cad/rear.png`, `cad/side.png` and `cad/feet_front.png`.

## 3. Slice — `python scripts/slice_check.py`

Full run (all parts) aborted on the first missing STL:

```
FAIL dome: 0 g, 0.0 h, One of the plate is empty or has no object fully inside it. Please check that the 3mf contains no empty plate in Bambu Studio before uploading.
...
FileNotFoundError: [Errno 2] No such file or directory: 'C:\\dev\\robots\\fable-r2d2\\stl\\body_upper.stl'
EXIT_SLICE=1
```

`python scripts/slice_check.py --parts dome leg_upper leg_lower foot_outer leg_center foot_center head_drive`
(writes `cad/h2d-slice-check.json`):

```
FAIL dome: 0 g, 0.0 h, One of the plate is empty or has no object fully inside it. Please check that the 3mf contains no empty plate in Bambu Studio before uploading.
PASS leg_upper: 615 g, 20.1 h, Success.
PASS leg_lower: 314 g, 11.1 h, Success.
PASS foot_outer: 680 g, 19.6 h, Success.
PASS leg_center: 162 g, 5.4 h, Success.
PASS foot_center: 322 g, 9.2 h, Success.
PASS head_drive: 81 g, 3.0 h, Success.
{
  "checked_at_utc": "2026-09-12T15:34:46.670514+00:00",
  "test_type": "Local Bambu Studio CLI slicing of package meshes; no printer connection or physical print",
  "profiles": {
    "machine": "Bambu Lab H2D 0.4 nozzle",
    "process": "0.20mm Standard @BBL H2D",
    "overrides": {
      "wall_loops": "5",
      "top_shell_layers": "6",
      "bottom_shell_layers": "6",
      "sparse_infill_density": "30%",
      "sparse_infill_pattern": "gyroid",
      "enable_support": "1",
      "support_type": "tree(auto)",
      "support_on_build_plate_only": "0",
      "brim_type": "no_brim",
      "skirt_loops": "0"
    },
    "bed": "Textured PEI Plate"
  },
  "all_pass": false,
  "total_predicted_mass_g": 3783.9,
  "total_predicted_time_h": 119.4
}
Slice check failed
EXIT_SLICE=1
```

| part | pass | predicted mass g | predicted time s | h | bbox (x, y, w, d, h) |
|---|---|---|---|---|---|
| dome | FAIL | — | — | — | return_code -50 |
| leg_upper | PASS | 615.00 | 72535.35 | 20.15 | 105.3, 15.15, 139.4, 289.7, 50.79 |
| leg_lower | PASS | 314.09 | 40108.17 | 11.14 | 59.0, 110.0, 232.0, 100.0, 58.25 |
| foot_outer | PASS | 679.87 | 70663.71 | 19.63 | 42.5, 69.1, 265.0, 181.8, 105.2 |
| leg_center | PASS | 162.31 | 19503.63 | 5.42 | 105.0, 110.0, 140.0, 100.0, 47.52 |
| foot_center | PASS | 322.41 | 32988.68 | 9.16 | 113.35, 69.9, 123.3, 180.2, 111.9 |
| head_drive | PASS | 81.27 | 10788.55 | 3.00 | 116.75, 123.86, 116.5, 72.28, 39.91 |

Quantity-weighted total for the six passing parts: 3783.9 g, 119.4 h. The three body parts
were not sliced (no STL).

### Dome slice probe (scratch, same machine/process/filament profiles and overrides as the script)

The dome STL was translated so its footprint is centred on the plate (162.5, 160) and sliced
with `--arrange 0`:

```
{"variant": "centred_supports_on", "return_code": 0, "error_string": "Success.", "warning": "", "mass_g": 1243.9029541015625, "time_h": 35.37}
```

Result: with the script's own settings (tree(auto) supports ON, no brim) the dome slices
cleanly — no warning, 1243.9 g, 35.4 h. The round-1 failure (support outside the 320 mm bed
axis) no longer occurs. The remaining FAIL is `slice_check.py`'s `--arrange 1` step, which
does not place a 316.83 mm object on the 320 mm axis (return_code -50). Adding the dome's
predicted 1243.9 g / 35.4 h to the six passing parts gives 5027.8 g and 154.8 h for the seven
delivered STLs (body parts excluded).

## 4. Renders

`OPENSCAD=C:/Users/Jeremy/tools/openscad-nightly/openscad.com python scripts/export_cad.py --views`:

```
Rendered assembly
Rendered rear
Rendered exploded
Rendered section
EXIT_VIEWS=0
d94b54a3134c9dfd90e717b45c9ed499 *cad/assembly.png
d94b54a3134c9dfd90e717b45c9ed499 *cad/rear.png
d94b54a3134c9dfd90e717b45c9ed499 *cad/exploded.png
d94b54a3134c9dfd90e717b45c9ed499 *cad/section.png
-rw-r--r-- 1 Jeremy 197121 12512 Sep 12 11:33 cad/assembly.png
-rw-r--r-- 1 Jeremy 197121 12512 Sep 12 11:33 cad/exploded.png
-rw-r--r-- 1 Jeremy 197121 12512 Sep 12 11:33 cad/rear.png
-rw-r--r-- 1 Jeremy 197121 12512 Sep 12 11:33 cad/section.png
```

Same blank 12512-byte image as round 1 (preview path: "Normalized tree is growing past 100000
elements"). Re-rendered with `--backend=manifold --render` and the script's cameras, all rc=0:

```
assembly: Genus 146, Vertices 72374, Facets 145328   -> cad/assembly.png  4700a32c9d75e6d6df1f4b40ed2518bc
rear:     Genus 146, Vertices 72374, Facets 145328   -> cad/rear.png      2173acb626a2a2015b0dbae5a2827591
exploded: Genus 148, Vertices 72588, Facets 145764   -> cad/exploded.png  4ba1c594e06e61b79e440822446eb851
section:  Genus 71,  Vertices 38883, Facets 78046    -> cad/section.png   15c98a3383726ff0100338a1e66c16b1
```

Extra evidence renders (same backend, part="assembly"):

```
cad/side.png       camera=1800,0,300,0,0,300  (droid right side)      c52e899156dab4ebe252e4d2575f8f41
cad/feet_front.png camera=0,900,120,0,0,80    (front, low, feet only) acec0bdd84c1f0c86d3cfc472e6ec79a
```

Visual review against `research/drawings/photos/lucasfilm-r2.jpeg` and `body-front.jpg`:

1. No body: both body rings and the electronics tray are absent. The dome and head drive float
   at the stance height (shoulder 463 mm, 18 deg tilt) with nothing under them; the centre-leg
   flange and the leg shoulder discs have nothing to bolt to. Owner: body.
2. Legs: outer legs are present, recognisable (shoulder disc with hub bolt pattern, strut with
   the booster-cover and hydraulic-line details, ankle bracket with the ankle cylinders), lean
   18 deg with the feet forward, and meet the outer feet at the ankle slot with no gap or
   overlap (check_ankle empty). The centre leg sits over the centre foot with the caster boss
   engaged (check_center empty on the foot side). Owner: legs, no defect seen.
3. Feet: three feet are on the floor; wheel bottoms measured at z = 0.0. Foot spacing
   (leg_track 363.4) and the centre foot ahead of the outer feet match the photo. Owner: feet,
   no defect seen.
4. Dome: radar eye, front logic display windows, front PSI, holoprojectors, pie panels, top
   disc and rear logic display are all present; the dome tilts with the body. The dome band
   bottom sits above the head-drive at dome_gap; nothing floats within the dome/head-drive
   pair (check_head_drive empty). Owner: dome, no defect seen.
5. Render envelopes: the purchased-part motor envelopes in `r2d2.scad`
   `wheels_and_motors_outer()` stand the motor cans vertical and 32 mm through the floor
   (pegs under every foot in all renders; in `cad/section.png` the yellow cut faces below the
   centre foot are these cans). The real motor pockets in `feet.scad` are tilted; the envelope
   does not match them. Render-only. Owner: r2d2.scad (integrator).
6. Camera labels remain inverted relative to the FRAMES comment (+Y = front): `cad/rear.png`
   (camera y = +1700) shows the front (radar eye, front logic displays) and `cad/assembly.png`
   (camera y = -1700) shows the rear. Owner: scripts/export_cad.py views() (integrator).
7. `scripts/export_cad.py views()` still writes blank PNGs (preview path). Owner: scripts
   (integrator).

## Problems by owner

- body — `cad/body.scad` is still the 3-line empty stub: body_upper, body_lower,
  tray_electronics have no geometry and no STL; full export and full slice abort on them;
  check_seam, check_dome, check_shoulder, check_tray and the body halves of check_head_drive
  and check_center are vacuous. When the top-plate `head_slot` is cut, params has
  `head_slot = [36, 42]` while `cad/head_drive.scad` requires the tangential width >= 58
  (recommended 60): the 63 mm drive wheel will not pass through a 42 mm slot.
- scripts (integrator) — `slice_check.py --arrange 1` fails to place the 316.83 mm dome on the
  320 mm axis (return_code -50); the same STL centred at (162.5, 160) with `--arrange 0` and
  the script's support settings slices cleanly (1243.9 g, 35.4 h, no warning).
- scripts (integrator) — `export_cad.py views()` writes blank PNGs (preview CSG normalisation
  aborts; needs `--backend=manifold --render`); "assembly"/"rear" camera labels are swapped
  relative to +Y = front; the all-parts export and all-parts slice abort at the first missing
  part instead of reporting every part.
- r2d2.scad (integrator) — `wheels_and_motors_outer()` render envelope places the motor cans
  vertical, 32 mm below the floor (z -32.05), and does not match the tilted pockets in
  `feet.scad`; render-only.
- head_drive / params — `head_slot[1] = 42` vs required 58: the head_drive file echoes the
  warning on every run; the resolution is a params change (owner: integrator) that the body
  top plate must then use.

## Files written by this round

- `cad/validation.json`, `bom/printed-parts.csv` (by export_cad.py --check-only)
- `cad/h2d-slice-check.json` (by slice_check.py --parts ...)
- `cad/assembly.png`, `cad/rear.png`, `cad/exploded.png`, `cad/section.png` (manifold --render)
- `cad/side.png`, `cad/feet_front.png` (extra evidence renders)
- `cad/integration-round2.md` (this file)
- `stl/dome.stl`, `stl/leg_upper.stl`, `stl/leg_lower.stl`, `stl/foot_outer.stl`,
  `stl/leg_center.stl`, `stl/foot_center.stl`, `stl/head_drive.stl` (re-exported)
