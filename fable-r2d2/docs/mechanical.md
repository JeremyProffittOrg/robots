# fable-r2d2 mechanical guide

Written 2026-09-12. This is the mechanical half of the fabrication package. It covers the
printed parts, the joints, the fits, the load screening and the finish. The build sequence is
in [assembly.md](assembly.md). The harness is in [electrical.md](electrical.md). The software
is in [firmware.md](firmware.md). Nothing here is duplicated from those three documents.

**Nothing in this package has been built or measured.** Every mass, time and force below is
either a computer prediction or arithmetic on a published rating. Each number says which.

Every dimension comes from `cad/params.scad`. That file is the single source. Where a part
file adds a dimension of its own, the name is given (for example `lg_rod_bottom_z` in
`cad/legs.scad`) so it can be found.

---

## 1. Design envelope and stance

### 1.1 Print envelope

| Axis | Machine | Rule | Limit used |
| --- | --- | --- | --- |
| X | H2D left extruder 325 mm | minus the 3 mm buffer the operator asked for | `env_x` = 322 mm |
| Y | H2D left extruder 320 mm | minus the 3 mm buffer | `env_y` = 317 mm |
| Z | H2D left extruder 320 mm | "print at max height minus 5 mm" | `env_z` = 315 mm |

Two rules follow from this and they drive the whole design.

- **Maximum height rule.** Every part is made as tall as its geometry allows, up to 315 mm.
  A taller part is a part that does not need a joint.
- **Minimal part rule.** The package is nine STL files and twelve printed pieces. The
  electronics tray was folded into `body_upper` as an integral deck for this reason. The body
  is two rings because 381.1 mm of body cannot be one 315 mm print. The outer leg is two
  prints because it is 480 mm long and no bed axis or diagonal reaches 480 mm.

The body diameter is set by the envelope: `body_od` = 317.0 mm = `env_y`. A cylinder is
limited by the smaller bed axis. The whole model is then scaled 0.68386 from the club-standard
463.55 mm R2-D2 (`scale_factor`, `research/proportions.md` section 6).

### 1.2 Principal sizes

| Item | Parameter | Value mm |
| --- | --- | --- |
| Body outside diameter | `body_od` | 317.0 |
| Body height, skirt bottom to top edge | `body_height` | 381.1 |
| Ring seam, measured down from the body top | `body_seam_from_top` | 246.0 |
| Upper ring height | `body_upper_h` | 246.0 |
| Lower ring height, skirt included | `body_lower_h` | 135.1 |
| Skirt height | `skirt_h` | 41.3 |
| Body skin wall | `body_wall` | 3.6 |
| Dome outside diameter | `dome_od` | 317.0 |
| Dome height, band bottom to crown | `dome_height` | 196.8 |
| Dome wall | `dome_wall` (shell 3.2 in `cad/dome.scad`) | 3.0 |
| Dome gap above the body top edge | `dome_gap` | 1.9 |
| Outer leg, shoulder axis to ankle pivot | `leg_len` | 375.9 |
| Leg strut section (fore-aft x thickness) | `leg_strut_w` x `leg_strut_t` | 74.6 x 30.4 |
| Foot track, centre to centre | `leg_track` | 363.4 |
| Shell bottom edge above the floor | `foot_clear` | 12 |
| Ankle pivot above the floor, legs vertical | `ankle_z` | 105.5 |

### 1.3 Revision D stances (user-confirmed 2026-09-12)

Revision D makes the stance change motorized and interlocked. The requirement is:

- The centre leg deploys toward the **front** for the three-leg stance.
- For the two-foot stance the centre leg retracts fully and its wheels lift clear of the floor.
  Two-foot is for standing still only.
- A linear actuator moves the centre leg and changes body tilt between 0 and 18 degrees.
- A positive shoulder lock engages at both endpoints. Its state is read from a switch, never
  inferred from actuator position. Release is powered.

The outer legs now stay **vertical in both stances** (`leg_lean` = 0). The body pitches about
the two shoulder axes. The hinge-to-floor geometry and not the legs sets the tilt, so the
ankles never move and the ankle lock bolt stays in tongue hole A.

| Measure | Two-foot stance | Three-leg stance | Source |
| --- | --- | --- | --- |
| Actuator stroke (P16 extension) | 5.0 mm (`st_s_two`) | 81.29 mm (`st_s_three`) | `cad/params.scad` |
| Body tilt, top toward the rear | 0 deg | 18.00 deg | `st_tilt()` in `cad/stance.scad` |
| Shoulder axis above the floor | 481.4 mm | 481.4 mm | `shoulder_z_two_leg` |
| Outer foot centres forward of the shoulder axis | 0 mm | 0 mm | legs vertical |
| Centre-foot caster axis forward of the shoulder axis | 34 mm, lifted | 187.1 mm, on the floor | `st_hinge_world()` |
| Centre wheels above the floor | 25.0 mm | 0 | `st_stow_lift` |
| Dome crown above the floor | 747.3 mm | 481.4 + 265.9 cos 18 = 734.3 mm | computed |

Why the legs stay vertical: with the legs fixed and the body hanging from the shoulders, the
body centre of gravity is about 125 mm below the shoulder axis, so the unlocked body is a
pendulum that always wants to return toward upright. The centre leg pushes on the floor to hold
the tilt, so the leg is always in compression and the robot is held even with the locks out.
Revision C leaned the legs 18 degrees and pivoted the robot about the ankles, which has no
stable unlocked state.

Why the outer-foot battery boxes moved outboard: between two vertical legs the inboard boxes
left only 4.9 mm on each side of the 123.3 mm centre foot, so the caster could not swivel. On
the outboard side the gap from a centre foot swivelled 30 degrees to an outer shell is 4.1 mm
at the sole and 15.6 mm at the stowed height. This is a deliberate departure from the club
drawings.

### 1.4 The transition

`scripts/check_stance.py` models this sequence. The controls workstream owns the firmware that
runs it.

Deploy, two-foot to three-leg:

1. Locked at 5.0 mm, centre foot lifted 25 mm.
2. Extend, still locked, to 33.9 mm: the wheels touch the floor (`st_s_contact`). The body stays at 0 deg.
3. Release both pins (MG995 16.3 deg). Hold the release until 44.4 mm, where the pins have cleared the bores.
4. Extend, unlocked, to 81.29 mm. The pins ride the leg faces. The body tilts to 18 deg and the
   centre foot rolls forward from 48 mm to 187 mm ahead of the shoulders. Drive the centre-foot
   motors at that ground speed.
5. Creep through 81.29 +/- 1.5 mm until both switches read seated.

Retract is the reverse: release at 81.29 mm, hold the release to 54.5 mm, retract unlocked, creep
through 33.9 mm until both switches read seated, then lift, locked, to 5.0 mm.

The robot **cannot drive in the two-foot stance.** It has no balance system. Drive is refused
during a transition.

---

## 2. The nine STL files

Ten files. Thirteen printed pieces. `leg_upper`, `leg_lower` and `foot_outer` are each printed
twice, the second one mirrored in the slicer. The supplied file is the right-hand part.

Revision D adds one file, `leg_carriage.stl`. The pitch hinge must join the two guide
bearings, the actuator rod eye and the caster housing, and no purchased joint does all three.
Every other revision D function uses a purchased joint or a feature of an existing print. The
table below is the revision C measurement; `cad/validation.json` and `bom/printed-parts.csv`
carry the current sizes.

| File | Qty | Printed size X x Y x Z mm | Orientation | Material | Supports |
| --- | --- | --- | --- | --- | --- |
| `dome.stl` | 1 | 316.8 x 316.8 x 199.1 | Lip down, crown up | PETG (PLA Basic option) | Tree, **inside** the crown only |
| `body_upper.stl` | 1 | 317.0 x 317.0 x 264.0 | Seam face down | PETG (PETG-CF option) | Tree, under the deck only |
| `body_lower.stl` | 1 | 317.0 x 317.0 x 141.1 | Skirt bottom down | PETG | Tree, under the battery shelf only |
| `leg_upper.stl` | 2 | 289.7 x 139.4 x 50.8 | Inboard face down | PETG (PETG-CF option) | None |
| `leg_lower.stl` | 2 | 232.0 x 100.0 x 58.3 | Inboard face down | PETG | 6.5 mm block under the tongue |
| `foot_outer.stl` | 2 | 181.8 x 265.0 x 105.2 | Sole down | PETG | None, if the slicer bridges |
| `leg_center.stl` | 1 | 140.0 x 100.0 x 47.5 | Flange face down | PETG | None |
| `foot_center.stl` | 1 | 123.3 x 180.2 x 119.9 | Sole down | PETG | None, if the slicer bridges |
| `head_drive.stl` | 1 | 116.5 x 72.3 x 39.9 | Base mating face down | PETG | Tree, under the arm |

Every size above is measured from the mesh by `scripts/export_cad.py` and recorded in
`cad/validation.json`, which now reports **nine of nine parts passing**: watertight, one
connected solid, consistent winding, inside the envelope.

`body_upper` measures 264.0 mm tall, not the 246.0 mm of the ring skin, because the shoulder
fairing and its gussets stand below the seam plane in the print frame. Both rings still sit
well inside the 315 mm Z limit.

### 2.1 Slicer settings

These are the settings `scripts/slice_check.py` used, recorded verbatim in
`cad/h2d-slice-check.json`.

| Setting | Value |
| --- | --- |
| Machine | Bambu Lab H2D 0.4 nozzle |
| Process | 0.20mm Standard @BBL H2D |
| Wall loops | 5 |
| Top shell layers | 6 |
| Bottom shell layers | 6 |
| Sparse infill density | 30 % |
| Sparse infill pattern | gyroid |
| Support | on, tree (auto), not build-plate only |
| Brim | none |
| Skirt loops | 0 |
| Bed | Textured PEI plate |
| Filament profile | Bambu PETG HF @BBL H2D 0.4 nozzle |

`plan.md` locks 0.20 mm layers, five walls and 30-40 percent gyroid. Use 30 percent for the
dome and the feet, 40 percent for the two body rings, the four leg pieces and the centre leg.
The Bambu PETG wiki guidance is to keep the wall count at or below 6 and the infill at or
below 50 percent, so 5 walls and 40 percent stay inside it
(`research/components-mechanical.md`, "Filament and print guidance").

### 2.2 Material choice

| Material | Where | Numbers read from the TDS |
| --- | --- | --- |
| Bambu PETG Basic | Default for every structural part | Tensile X-Y 51 +/- 1 MPa, Z 35 +/- 6 MPa; bending X-Y 75 +/- 3 MPa; HDT 68 C at 1.8 MPa; density 1.25 g/cm3 |
| Bambu PETG HF | The profile the slice check used; discontinued | Tensile X-Y 34 +/- 4 MPa, Z 23 +/- 4 MPa; bending X-Y 64 +/- 3 MPa; HDT 62 C; density 1.28 g/cm3 |
| Bambu PETG-CF | Option for `body_upper` (the shoulder bosses) and the leg cores | Tensile X-Y 59 +/- 4 MPa, Z 38 +/- 3 MPa; bending X-Y 83 +/- 4 MPa; HDT 68 C |
| Bambu PLA Basic | Option for the dome only | The dome carries only its own weight on the ring bearing |

PETG-CF needs a hardened steel nozzle, is not compatible with AMS lite, runs 240-270 C with
100 percent cooling and prints below 200 mm/s. The H2D ships with a hardened steel nozzle.
PETG Basic is the safe default and is the material the BOM buys (five 1 kg spools, `bom/hardware.csv`
H31).

PETG softens at 62-68 C. Do not leave the robot in a hot car. This is a mechanical limit, not
just an electrical one.

### 2.3 Support notes, part by part

**dome** — Lip down. The shell overhang passes 45 degrees above about z 151 and reaches about
75 degrees at the flat crown. Support goes **inside**, under the last 25 mm of the crown
(above about z 168), under the pie-panel ring, the 66 mm flat top and the HP3 cup. Everything
else is designed support-free: the eye housing underside is 48 degrees from horizontal, the
holoprojector barrels have gussets and teardrop cups, the PSI bosses are teardrops, and every
pocket has a 45 degree gable. Remaining bridges are the tops of the 44.1 mm holoprojector
bores, the 52.6 mm bezel bore, the 27 and 34 mm PSI apertures, the 30 and 44 mm logic windows
and two 2.3 mm inset ledges. The 14 degree wedge face at the eye's bottom-left corner (about
20 x 6 mm) is a downward face; paint a support blocker there or accept minor roughness. No
brim: the first layer is a 57 to 158.5 mm annulus.

**leg_upper** — No supports. The horseshoe, hub, booster cover, strut rods and channel all
rise from the plate. The horizontal bores print round (M12 13 mm, dowels 6.2 mm, wire 9 mm).
The captive nut traps are 13.4 x 8.4 mm tunnels bridged at 23 mm. The finger slot is vertical.

**leg_lower** — One support block. The ankle tongue plate lies 6.5 mm above the bed
(`lg_tongue_x0`), because it must stay centred on the foot slot. Put a 6.5 mm normal support
block under the tongue area, about 100 x 60 mm. Everything else rises from the bed. The 22 mm
rod counterbores are horizontal round holes.

**leg_center** — No supports. The column leans 18 degrees, so its rear face is an 18 degree
overhang. The bearing seats, the swivel groove and the wire slot all open upward. The M12 head
counterbore is a 28 mm hole from the bed with a 2 mm ledge ring at 13 mm.

**foot_outer and foot_center** — Sole down, as modelled, and in principle no supports. The
sloped walls are 19.7 and 34.6 degrees from vertical on the outer foot, 22.3 and 35.0 on the
centre foot. Every internal rib rises from the bed. The gearbox pocket ceilings are 12 mm wide
tilted bridges over a 19.4 mm pocket. The can pockets are 21 mm round arches with 1 mm of sag
allowance. The one real demand is the top plate: the two 20 mm strips beside the ankle slot
bridge 51 mm, and the plate bridges the side walls over 58 mm (outer foot) and 45 mm (centre
foot). Use bridge settings with 100 percent fan. **If the slicer will not bridge that, add
tree supports under the top plate only.**

**head_drive** — Base mating face down, arm 4 degrees lowered. The base, its pads, the tension
boss and the lugs need no support. The arm is a suspended body and tree supports under it are
unavoidable: inside the open motor pocket, under the side beam, and under the boss-to-wall
bridge. Every supported face is hidden inside the body. The base and the arm print as one
solid, joined by two sacrificial webs 0.8 mm thick, 6 mm long and about 3.5 mm tall at
x = +/-15 mm. **After printing, cut both webs with a knife and file the stubs flush.** The arm
needs 3 mm of clearance to the base plate at the hinge ridge.

**body_lower** — Skirt down, 135.1 mm of ring plus the 6 mm seam lip. **Tree supports under
the battery shelf only** (z 41 to 45), between the sixteen radial support ribs. Everything
else is self-supporting: the skirt, the skirt ribs, the floor, the rod bosses, the ring ribs
with their 45 degree undersides, the seam flange and the lip. The skirt flares 41.9 mm out
over 41.3 mm of height, which is 45.4 degrees from vertical. That is right at the limit. It
prints in PETG at 0.20 mm, but it is the one outside surface that benefits from a 45 degree
speed reduction.

**body_upper** — Seam face down, 246 mm of ring skin. **Tree supports under the electronics
deck only**, inside radius 131 mm; the sixteen 45 degree gussets carry the deck from radius
131 to 156 mm. Both support regions are reached through the open top of the ring after
printing. Bridges: the front vent louvre slots bridge 45 mm, the side vent slots bridge 70 mm,
and the rear access opening bridges 120 mm across its top edge.

Neither ring needs support on any outside surface. Every skin feature is a recess or a through
cut. No brim on either ring; the first layer of each is an annulus.

### 2.4 Predicted mass and time

From `cad/h2d-slice-check.json`, which is a local Bambu Studio CLI slice. No printer was
connected and nothing was printed.

| Part | Qty | Predicted mass each g | Predicted time each h |
| --- | --- | --- | --- |
| `foot_outer` | 2 | 679.9 | 19.63 |
| `foot_center` | 1 | 322.4 | 9.16 |
| `head_drive` | 1 | 81.3 | 3.00 |
| `leg_upper` | 2 | 615.0 | 20.15 |
| `leg_lower` | 2 | 314.1 | 11.14 |
| `leg_center` | 1 | 162.3 | 5.42 |
| **Sub-total, six parts, nine pieces** | | **3,783.9 g** | **119.4 h** |

The dome is not in that total. Its row failed on the script's `--arrange` step with return
code -50, not on the geometry. The same STL centred on the bed with the same support settings
slices clean: **1,243.9 g, 35.37 h** (`cad/integration-round2.md`, headline). Adding it gives
**5,027.8 g and 154.8 h for ten of the twelve pieces.**

The two body rings are modelled but not yet sliced: `cad/h2d-slice-check.json` was written
before `cad/body.scad` existed. What is known from the meshes (`cad/validation.json`) is their
solid volume: `body_upper` 2,618.6 cm3 and `body_lower` 1,537.2 cm3. At the 0.45 fill fraction
`docs/stability.json` uses for screening, that is **1,496 g and 879 g**, or 2,375 g for the
pair, against the 3,018 g `research/loads.md` budgets. Print time for the two rings is
**estimated at 60 to 90 hours**.

Whole-robot printing is therefore **estimated at about 7.4 kg of filament and 215 to 245
hours.** Buy six 1 kg spools. Re-run `python scripts/slice_check.py` now that the body exists,
and replace the estimates above with its numbers.

### 2.5 What is on the two body rings

From the header blocks of `cad/body.scad`. Skin features are quoted there as (s, y), where s
is the arc distance from the front or rear centreline and y is the distance down from the body
top. Positive front s lands on the droid's **left**.

**`body_lower`, body-frame z 0 to 141.1**

| Feature | Detail |
| --- | --- |
| Floor | 6 mm plate on the skirt bottom. Four M8 clearance holes at `center_leg_bolts` with **hex nut pockets on the top face**, each in a 22 mm boss. One 60 x 40 mm cable opening centred at Y = -60. Recessed part label. |
| Battery shelf | 4 mm plate at z 41 to 45, full ring width, on sixteen radial support ribs. An 8 mm curb runs round the SLA footprint, 11 mm outside the battery and 3 mm clear inside it. Four **26 mm socket windows** sit over the four centre-leg nuts so a socket reaches them with the shelf in place. Four 3 mm strap slots. An 80 x 26 mm harness slot front and rear. |
| M8 rod columns | Four, on radius 138 mm. **The nut is not under the floor.** See 3.1. |
| Seam flange and lip | See 3.1. |
| Side vents | The notch is y 139 to 228, not 139 to 243.2: the lower 15 mm would have cut the seam flange. Both flanks carry one, formed by the front half plus the rear half of the skin. |
| Utility-arm relief | **165 x 38 x 8 mm**, not 165 x 43: the bay is only 41.3 mm tall. |
| Speaker grille | **Nine 5 mm vertical louvres** in the front pocket vent door, centred at (s, y) = (-158, 291). Vertical slots in a vertical wall need no bridging, and the reference photographs show vertical slats. Speaker bosses are behind it. |
| Charge port and switch | Pad on the rear lower band. |

**`body_upper`, body-frame z 135.1 to 381.1**

| Feature | Detail |
| --- | --- |
| Electronics deck | Integral, 4 mm thick, **local z 36 to 40** (`tray_z_upper` is the top face). An annulus from radius 50 to 154.9 mm, cut off by a chord at y = -114.9, which leaves a 40 mm harness gap at the rear. Sixteen 45 degree gussets carry it from radius 131 to 156 mm. |
| Deck seats | Raspberry Pi 4: four M2.5 boss inserts on the `pi4_holes` pattern. KB2040: two M2 bosses. Four DRV8833: a 26 x 18 mm pad each with two M2 bosses. Three regulators: a 25.4 x 25.4 mm pad each with four 2.2 mm holes. ADS1115: two M2.5 bosses. Fuse holders: one 46 x 20 mm seat. Eight 6 x 2.5 mm cable slots through the deck, and six recessed labels: `PI4`, `KB2040`, `DRV8833`, `5V / 12V`, `ADC`, `FUSE`. |
| Rear access opening | **120 x 90 mm at y 126 to 216**, which is body-frame z 165.1 to 255.1. A 10 mm inner lip takes the cover, held by **four M3 heat-set inserts**. It sits well below the head-drive wheel sweep, so the lip cannot foul the tyre. |
| Shoulder pads and bosses | See 3.2. The fairing is clipped flat at the top plate. |
| Top plate | See 3.7 and 3.8. |
| Utility-arm bays | A backing pad behind the bay, radius 147.9 mm. |

---

## 3. Every joint and how it carries load

### 3.1 Ring seam — locating lip, 8 x M4, 4 x M8 rods

The two body rings meet 246.0 mm below the body top edge. Three features share the work.

- **Locating lip.** `body_lower` carries a lip at radius 151.6 to 154.6 mm, z 135.1 to 141.1
  (`seam_lip_h` tall, `seam_lip_t` thick), with a 15 degree lead-in chamfer on its top outer
  edge. `body_upper` has the matching socket, radius 151.3 to 154.9, z 135.1 to 141.5. That is
  **0.3 mm of clearance each side**. The lip takes the shear and sets the concentricity. It is
  not a clamping feature.
- **Eight M4 bolts.** An internal flange 12 mm wide and 5 mm thick (`seam_flange_w`,
  `seam_flange_t`) runs round both rings: radius 142.9 to 154.9, z 130.1 to 135.1 on the lower
  ring, and radius 142.9 to 151.3, z 135.1 to 140.1 on the upper. The bolt circle is radius
  **148.9 mm at 22.5, 67.5, 112.5 ... degrees** (`seam_bolt_n` = 8). Fit **M4 x 20 socket cap
  screws from above**; the hex nut pockets open downward on the lower flange.
- **Four M8 threaded rods.** Four rods on a 138 mm radius at 45, 135, 225 and 315 degrees
  (`rod_n`, `rod_r`, `rod_angle0`) run up to the top plate inside 20 mm bosses (`rod_boss_d`).
  They put the whole body in compression and carry the dome, the head drive and the shoulder
  reaction down the ring. The M4 bolts hold the seam closed; **the rods are what makes the
  body a single column.**

**The lower rod nut is not under the floor.** Radius 138 mm lies outside the skirt-bottom
plate, whose maximum radius is `skirt_bottom_r` = 116.6 mm, so there is no floor under the rod
to bolt to. Each rod column therefore starts **on the battery shelf**, and its nut is a
**captive hex trap at z 46**, opened downward with a slot facing the body axis. Slide the nut
in, feed the rod down into it, and do all the tightening at the top. The top nut sits in an
18 mm diameter x 4 mm counterbore in the top plate, reachable from above until the lazy susan
goes on; the nut then stands 2.8 mm proud and clears the dome plate by 5.1 mm.

Preload each rod to about 1 kN. `research/loads.md` section 7 gives 1.6 N.m of torque for that
on an M8 with a 16 mm washer, and 1 kN is 12 percent of the 8.2 kN proof load of an M8 class
4.6 rod. Use a 24 mm fender washer under each nut: 1 kN over 402 mm2 of washer face is
2.5 MPa, which PETG holds without creeping.

### 3.2 Shoulder — M12 bolt, bushings, index pins

Each shoulder is a bolted steel pivot. It is not motorised.

- The body side is a flat pad 116 mm across (`shoulder_pad_d`) whose outer face is exactly the
  tangent plane at |X| = `body_r` = 158.5 mm, with an internal boss 120 mm across and 30 mm
  deep behind it (`shoulder_boss_d`, `shoulder_boss_t`), 313.9 mm up the body frame
  (`shoulder_z`). A hex pocket 13 mm deep opens to the inside of the ring for the M12 nyloc.
  The fairing that blends the pad into the skin is clipped flat at the top plate, so nothing
  of it stands above z 375.1.
- The leg side is a U-shaped plate 30.4 mm thick with the horseshoe raised on its **outboard**
  face. The inboard face is flat, and it sits at |X| = 166.5 mm, which is the 8 mm
  `shoulder_spacer` stack. `cad/body.scad` carries **no horseshoe**: the pad is a plain disc,
  exactly as `cad/legs.scad` requires.
- One **M12 x 130 class 8.8 hex bolt** (`shoulder_bolt_m`, `bom/hardware.csv` H03) passes
  through the leg hub, the bushing stack and the 30 mm boss. Its head sits in a 26 mm
  counterbore 10 mm deep inside the leg hub. A nyloc goes on inside the body.
- Two **flanged bronze bushings**, 12 mm bore x 16 mm OD x 20 mm long with a 20 mm flange
  2 mm thick, plus washers, make up the 8 mm spacer stack between the pad and the leg
  (`shoulder_spacer` = 8).
- **Do not clamp printed faces with a torqued M12.** Fit a steel crush sleeve through the boss
  so the bolt clamps steel to steel, and use M12 fender washers, 37 mm OD, the closest stock
  size to the 40 mm `research/loads.md` asks for. At 5 N.m the preload is about 2.1 kN and the
  face pressure about 1.9 MPa. A 24 mm washer would give 6.6 MPa, which creeps.

**The lock pins carry the moment, not the bolt.** Revision D removes the hand-set 6 mm dowels.
Each shoulder has a sensed spring-plunger lock, described in section 3.9. The pin is 50 mm from
the axis. At that radius the two receivers are 15.6 mm apart, leaving 4.6 mm of printed web
between their 11 mm thread bores and 2.3 mm between their hex pockets.

Load screening (`research/loads.md` section 7): bolt shear 1.6 MPa against a 48.9 kN proof
load; bearing on the printed boss 0.49 MPa against about 8 MPa allowable, a 16x margin; index
pin bearing 1.2 MPa, a 7x margin. Steel is never the limit. Creep under the clamp is the risk,
and the crush sleeve retires it.

### 3.3 Leg splice — comb lap joint, 4 x M4, two full-length M8 rods

The outer leg splits at 220 mm below the shoulder axis (`leg_split_z`). The joint is a comb,
not a butt.

- `leg_lower` carries a centre tongue 20 mm wide, full strut thickness, 40 mm tall
  (`leg_splice_len`). `leg_upper` has the matching slot between two fingers, and the fingers
  carry the rod bores. Fit clearance is 0.2 mm each side (`lg_finger_clear`). Both halves
  print flat with no floating lap piece.
- **Four M4 x 80 bolts** pass through the whole strut width in Y, at x = 5 and 25.4 mm and
  z = -210 and -190 mm. Heads sit in 8 mm counterbores in the front face; hex nut pockets are
  in the rear face.
- **Two M8 threaded rods** run the full length of the leg at y = +/-20 mm (`leg_rod_offset`)
  on the strut centre plane. The top nut of each rod sits in a captive hex trap that opens on
  the inboard face at z 40 to 48.4 mm. The rod is fed in from the ankle end, threaded through
  that captive nut, and the bottom nut and washer are tightened with a 13 mm socket in a 22 mm
  counterbore in the ankle underside.

The rods are the joint. `research/loads.md` section 7: the moment at mid-leg under a 35 N side
push at the foot is 7.6 N.m, across a layer-line face whose interlayer strength is 18-23 MPa.
Two rods preloaded to 1 kN with a 25 mm lever to the face edge hold the joint closed to
50 N.m, a 6.6x margin. Preload each to **1.6 N.m**.

Rod length: the bore runs from `lg_rod_bottom_z` = -336 mm up to `leg_rod_top_z` = +55 mm,
391 mm. `cad/legs.scad` names M8 x 400 stock. Cut each leg rod to **390 mm**.
`bom/hardware.csv` H09 currently plans 425 mm cuts; 425 mm does not fit the bore and the cut
plan needs correcting.

### 3.4 Ankle — tongue in a slot, M8 pivot, M8 lock, two stance holes

The leg ends in a tongue 17.4 mm thick and 100 mm wide (`leg_tongue_t`, `leg_tongue_w`) that
drops 30 mm into a slot in the foot (`foot_slot_depth`). The slot is 17.6 mm wide
(`foot_slot_w`) and is widened for the 18 degree swing.

- The foot carries a raised ankle block 60 x 120 x 18 mm on its top plate. The **pivot bore**
  runs along X through both block cheeks at 6.3 mm above the shell top (`ft_pivot_up`), with
  21.7 mm bosses 4 mm proud (`ankle_cyl_d`) and an M8 nut pocket in the inboard boss.
- The **lock bore** is the same size, on the pivot plane, 40 mm ahead of the pivot
  (`ft_lock_r` = `ankle_bolt_spacing` = 40), also through both cheeks with bosses and an
  inboard nut pocket. It is a **single** bore in the foot.
- The tongue carries **two 9 mm lock holes on the same 40 mm arc** about the pivot
  (`lg_lock_r`, `lg_lock_holes`): **hole A** at (y +40, z 0) for the two-leg display stance,
  and **hole B** at (y +38.04, z -12.36) for the 18 degree three-leg lean. They are 12.5 mm
  apart with a 3.5 mm web between them. Swinging the leg brings each in turn onto the foot's
  single lock bore.
- Fasteners per outer foot: the **M8 x 80 pivot bolt** and the **M8 x 90 lock bolt**, heads
  outboard, nuts in the inboard boss pockets.

This interface is now closed on both sides. `cad/legs.scad` cuts exactly the two holes
`cad/feet.scad` expects; its old single bore 25 mm below the pivot is gone; `params.scad` sets
`ankle_bolt_spacing` = 40; and an `assert()` in each file ties its own radius to
`ankle_bolt_spacing`, so a change to params cannot move one part without the other.

The pivot bolt takes the shear. The lock bolt takes the moment and sets the stance. Neither is
torqued against the printed cheeks; the nyloc is run down until the play is gone and the
tongue still turns by hand with the lock bolt out.

### 3.5 Centre leg — guide shafts, carriage and pitch hinge

Revision D replaces the bolted flange with a guided, driven centre leg (section 3.9).

- **Guide.** Two 12 mm hardened shafts (cut to 182 mm) are fixed in `body_lower` at x = +/-66 mm
  on a guide inclined **30 degrees forward-down** from the body axis (`st_guide_angle`). Each
  shaft sits in a blind bottom boss on the floor and an open top boss tied to the skin by a
  sloped arm, with an M4 set screw in a heat-set insert.
- **Carriage.** `leg_carriage` rides the shafts on two LM12LUU bearings (12 x 21 x 57 mm), each
  clamped by a slit and two M4 x 25 screws. Its cross-web carries the P16 rod eye on an M4 x 45
  pin, 45 mm above the hinge.
- **Pitch hinge.** The carriage cheeks turn on two 8 x 12 x 12 mm bronze sleeves. M8 x 35 bolts
  clamp each sleeve to the `leg_center` housing through captive M8 nuts. The housing stays level:
  hanging, it rests on its heel stop face; on the floor, the floor keeps it level while the body
  tilts. The toe stop face allows 19.5 degrees of relative pitch against 18 needed.
- **Floor.** The four flange bolts, their bosses and the socket windows are gone. The floor and
  the battery shelf are cut by the swept envelope of the carriage and housing with 2 mm
  clearance (`st_carriage_sweep`, `st_housing_sweep`).
- **Hard stops.** The actuator closed stop is at s = 0, 5 mm short of the two-foot endpoint. The
  bearing housings land on the bottom shaft bosses at s = 86 mm, 4.7 mm past the three-leg
  endpoint.
- **Battery.** The shelf rose from z 45 to z 67 (`battery_shelf_z`) and the battery centre sits
  at y 60 (`battery_y`), so the battery clears the sloping carriage face and the seam flange.

### 3.6 Centre foot caster — M12 bolt, two 6001 bearings, swivel stop pin

The centre ankle is a vertical caster pivot. This is why six fixed-axle drive motors can turn
the robot without scrubbing the centre foot.

- Two **6001-2RS bearings, 12 x 28 x 8 mm** (`caster_bearing_od`, `caster_bearing_t`), sit in
  seats in the centre leg: the lower one open to the bottom face at z 26 to 34.2 mm, the upper
  one open to the 28 mm head counterbore. Centres are **18 mm apart**
  (`caster_bearing_gap` = `lg_bearing_cc` = 18). A 20 mm spacing does not fit: the stack would
  be 72 mm against the 62.2 mm available under the tilted plane. `params.scad` now carries 18
  and an `assert()` in `cad/legs.scad` holds the two in step.
- A **12 mm ID x 9.8 mm steel spacer tube** goes between the inner races, so the M12 preload
  never squeezes the outer races.
- One **M12 x 70 hex bolt** comes down from the leg, head in the counterbore. **It is
  tightened from above before the body is fitted.** Its nut sits in a nut slot under the centre
  foot's top plate (19.4 mm across flats, 8.4 mm deep), which is loaded from +X through the
  open sole before the motors go in.
- The **swivel stop** is an arc groove in the leg's bottom face, 7.6 mm wide and 8 mm deep,
  at a pin radius of 22 mm (`lg_stop_r`), spanning +/-30 degrees about forward
  (`caster_stop_deg`; revision D, see section 1.3). At 30 degrees the minimum turn radius about
  the outer-foot midpoint is about 270 mm. The foot's **6 x 8 mm pin stands on the stem-block top** at
  (0, `caster_trail` + 22) and runs in that groove. The pin moved in from radius 35 to 22 so
  the leg groove could reach it; radius 22 also puts it on solid stem-block material, so the
  16 mm ledge fin the old radius needed is gone. `ft_stop_r` and `lg_stop_r` are tied by an
  `assert()` in each file.
- Trail is 20 mm (`caster_trail`): the pivot axis stands ahead of the foot's axle midpoint so
  the caster follows.

Load screening: the caster carries roughly 117 N with a 3x dynamic factor, against a 6001
static rating of 2,390 N. The bearings are sized by the 12 mm bolt, not by load.

**Wire route.** The centre-foot wire hole is at (X 0, Y `caster_trail` - 21) = (0, -1), which
is leg-frame radius 21, on the leg's wire arc slot (radius 16.5 to 22.5 mm) at every swivel
angle. It moved there from (-18.5, `caster_trail`), which was only on the slot near zero
swivel. `ft_wire_r` and `lg_wire_r` are tied by an `assert()` in each file. The skirt floor
carries the matching 60 x 40 mm cable opening at Y = -60.

### 3.7 Dome bearing — Triangle 9C lazy susan, 8 x M5

The dome turns on a purchased steel ring bearing, not on a printed race.

- **Triangle 9C round lazy susan**: 228.6 mm OD (`susan_od`), 114.3 mm centre hole
  (`susan_id`), 7.9 mm thick (`susan_t`), 22 gauge steel, 750 lb rating. Four mounting holes
  per race on a 156.9 mm square, which is a radius of 110.9 mm (`susan_hole_r`) at 45, 135,
  225 and 315 degrees (`susan_hole_angles`).
- **Bottom race**: four M5 x 12 screws down into four M5 heat-set inserts in the body top
  plate. The pockets are pressed from **above**, each in a 14 mm boss that hangs 8 mm under
  the plate.
- **Top race**: four M5 x 12 screws up into four M5 heat-set inserts in the dome plate. The
  dome plate carries 12 mm tall bosses for these.
- **Access holes**: 12 mm holes at 0, 90 and 270 degrees in the body top plate
  (`susan_access_angles`, `susan_access_d`). You rotate the dome to bring each top-race screw
  over an access hole and drive it from below. **`cad/body.scad` omits the 180 degree hole
  altogether**, because `cad/head_drive.scad` shows the drive base covers (0, -110.9) and
  makes it unusable. Three holes reach all four screws.

The dome plate is an annulus from 57 mm to 153.5 mm radius, 5 mm thick (`dome_plate_r_in`,
`dome_plate_r_out`, `dome_plate_t`), printed as the first layers on the bed. Its outer edge
clears the body lip inner face by 1.5 mm.

### 3.8 Head drive — hinge bolt, spring tension, thumb nut, lift stop

One printed part does the whole job: a base bolted under the body top plate and an arm that
swings on it. One Adafruit 3777 motor turns one Adafruit 3766 wheel about a radial axis. The
wheel top comes up through the slot in the top plate and presses on the flat underside of the
dome plate, 7.9 mm above the plate's top face. Rolling the wheel drags the dome round.

- **Mount**: four M4 x 12 countersunk screws (DIN 7991) come down through plain,
  90 degree x 9 mm countersunk holes in the body top plate into four M4 heat-set inserts in
  the base. The holes are at (+/-45, -84) and (+/-42, -139) in the native frame
  (`hd_mount`). The plate underside must be **flat** over x +/-56, y -148 to -74: no bosses,
  no ribs.
- **Hinge**: one M4 x 70 socket head, two M4 washers and an M4 nyloc through both base lugs
  and the arm boss. The boss half-width is 20.8 mm, leaving 0.2 mm each side. **Snug the
  nyloc. Do not torque it.** The arm must swing freely.
- **Motor**: two M3 x 30 button heads and two M3 hex nuts hold the gearbox to the arm wall,
  through the two 3.0 mm holes 17.6 mm apart. Heads go on the wheel side and must be fitted
  before the wheel is pressed on. The lower nut goes into a blind hex pocket on the inboard
  face; the upper nut drops into a hex slot from the wall top. One 3.6 mm cable tie goes round
  the can through the tunnel.
- **Tension**: one M5 x 60 hex head (DIN 933, full thread; a socket cap head would spin in the
  pocket) hangs head-up in a pocket on the base's mating face, so the top plate captures the
  head. Below it: the arm's ear slot, a 15 mm OD washer, a compression spring 10 mm OD x 25 mm
  free x 1.0 mm wire (about 2 N/mm), a plain washer, and an M5 knurled thumb nut.
  Turning the nut up compresses the spring against the ear, lifts the arm, and presses the
  tyre on the dome plate. **Design compression is 4 to 6 mm**, which is 8 to 12 N at the ear
  and 4 to 6 N at the tyre. `research/loads.md` section 5 asks for 3 to 5 N.
- **Lift stop**: one M5 x 20 socket cap in an M5 insert in the arm's stop boss. Screwed fully
  home its tip stands 5 mm above the beam top and meets the base underside after 1 mm of lift.
  With the dome off, this is what stops the gearbox touching the base.
- **Release**: back the thumb nut off about 8 mm, which is 10 turns. The arm falls under its
  own weight until the bolt shank meets the end of the ear slot at 7 degrees. The wheel top is
  then 4 mm below the dome plate and the dome lifts off without dragging the tyre. The nut
  stays on the bolt.

The wheel window is x +/-31.5, y -147.5 to -118.5. The slot in the body top plate must be at
least 58 mm tangentially (`hd_slot_min`); `params.scad` sets `head_slot` = [36, 60], which
meets it. The 36 mm radial size is what caps the release at 7 degrees.

**Keep-out, honoured by `cad/body.scad`.** Nothing of the body enters the swept volume on the
rear side: |x| up to 66 mm, y -160 to -70 mm, body-frame z 160 to 378 mm, except the wall
itself and the top plate. The plate underside is flat over x +/-56, y -148 to -74: no ribs, no
bosses. The wheel sweeps to radius 150.9 mm at release and the body inner wall is at 154.9 mm.

The top plate also carries the slip-ring mount: a central opening of radius 50 mm
(`top_plate_opening_r`) with a three-spoke spider to a 30 mm hub, bored 12.5 mm for the
Adafruit 1195 body (`slip_ring_d`) and pinched by an M3 clamp screw. The bore is open top and
bottom so the ring's two lead bundles pass straight through.

Drive numbers (`research/loads.md` section 5): ratio from the dome ring to the wheel is 4.6.
Steady dome torque 0.10 N.m needs 0.69 N of tangential force and 0.86 N of normal force at
mu 0.8, so a 3 to 5 N preload is 2 to 3x. Run the head motor at **50 percent PWM off the 6 V
rail** for about 8.7 RPM loaded. Below 35 percent it stalls.

---

### 3.9 Stance mechanism and sensed shoulder lock (revision D)

Source: `cad/stance.scad` (kinematics, `leg_carriage`, lock block, purchased envelopes), with
every number in the `st_` block of `cad/params.scad`. `scripts/check_stance.py` proves the
transition and writes `docs/stance-check.json`.

#### Purchased parts

| Function | Part | Qty | Primary data used | Source |
| --- | --- | --- | --- | --- |
| Centre-leg actuator | Actuonix P16-100-256-12-P | 1 | 100 mm stroke; 147 mm closed hole to hole; 300 N max lifted; >500 N back-drive; 4.8 mm/s no load, 250 N at 2.5 mm/s; 1000 mA stall at 12 V; 20 % duty; 110 g; 11 kOhm +/-50 % pot; 0.4 mm repeatability, 0.3 mm backlash; 15 N max side load | [datasheet Rev B](https://www.actuonix.com/assets/images/datasheets/ActuonixP16Datasheet.pdf); listed in `bom/electronics.csv` by the controls workstream |
| Shoulder lock | J.W. Winco GN 412-6-35-B-1 | 2 | 6 mm pin, 6 mm extension; spring 5 N / 15 N; flange 35 x 26 x 12 mm, M4 counterbores at 25 mm; knob 25 mm; 0.152 lb; US$11.77 | [drawing](https://live-catalog.jwwinco.com/pdf/winco/us/412.pdf), `bom/hardware.csv` H34 |
| Lock receivers | J.W. Winco GN 412.2-M12X1.5-B6.2 | 4 | bore 6.2 mm; M12 x 1.5 x 10 mm; hex 13 A/F x 3 mm; 0.022 lb; US$5.66 | [drawing](https://live-catalog.jwwinco.com/pdf/winco/us/412_2.pdf), H35 |
| Lock sensor | Omron SS-01GL | 2 | SPDT gold contact; OF 0.49 N max; OT 1.2 mm min; MD 0.8 mm max; OP 8.8 +/-0.8 mm | [datasheet](https://omronfs.omron.com/en_US/ecb/products/pdf/en-ss.pdf); `bom/electronics.csv` |
| Lock release | MG995-class servo, Adafruit 1142 | 2 | 8.5 kg-cm at 4.8 V, 10 kg-cm at 6 V; 0.20 s/60 deg at 4.8 V; 40.7 x 19.7 x 42.9 mm; 62.41 g; US$19.95 | [product](https://www.adafruit.com/product/1142); `bom/electronics.csv` |
| Guide shafts | VXB 12 mm x 200 mm hardened shaft | 2 | cut to 160 mm | [product](https://vxb.com/products/12mm-shaft-hardened-rod-linear-motion-200mm-long), H40 |
| Guide bearings | LM12LUU, 12 x 21 x 57 mm | 2 | 657 N dynamic, 1200 N static | [product](https://vxb.com/products/two-pack-lm12luu-12mm-long-linear-ball-bearing-bus), H38 |

The actuator runs well inside its rating; the check result is in the table below. The P16-100
was kept because the 81.29 mm endpoint needs more than the 50 mm version's stroke.

#### Geometry

- **Guide and stroke.** The hinge moves along the 30 degree guide from body (y 34, z -3.6) at
  s = 5.0 mm. The wheels are 25 mm above the floor there. They touch at s = 33.9 mm, with the
  hinge 48 mm ahead of the shoulder. Past contact, the body tilt follows `st_tilt(s)`: 1.0 deg/mm
  just after touchdown, 0.20 deg/mm at 18 deg. The guide angle and stowed hinge position were
  set by floor drag: the tilt jams if the floor force on the centre foot exceeds
  (hinge y at touchdown) / (shoulder height above the hinge) = 48 / 342.5 = 14 % of its load.
  With the first choice, a 20 degree guide and hinge y 15 or 22, that limit was 9 %.
- **Actuator.** Fixed eye at body (0, -64.5, 167.0) on two cheeks hanging from the underside of
  the `body_upper` deck, M4 x 60 pin. The actuator is parallel to the guide, so its stroke equals the
  centre-leg travel and it has no side load. The Raspberry Pi 4 moved 14 mm to -X to clear the
  cheeks.
- **Lock.** On each shoulder, the GN 412 flange sits 5 mm deep in the `body_upper` pad and stands
  7 mm proud, so its pin face is 1 mm from the leg face. The pin is at 50 mm radius, 261 deg in
  the body (y, z) plane. The leg carries receivers at 261 deg (tilt 0) and 279 deg (tilt 18).
  Pin engagement is 5.0 mm. The flange is proud of the pad and not the print because the ring
  already fills the 317 mm bed.
- **Sensing.** The SS-01GL lever rides the knob underside 11.5 mm above the pin axis. It is
  pressed only when the pin is fully seated. Set overtravel is 0.9 +/-0.2 mm, within the 1.2 mm
  rating. With the 0.8 mm differential, a closed switch guarantees at least 3.1 mm of pin in the
  bushing. A pin that is pulled, riding the leg face or part seated reads "not engaged".
- **Release.** A 3 mm pin on the MG995 horn sits 1 mm below the knob rim. Turning the horn 16.3
  deg pulls the pin 5.8 mm, which is 0.8 mm more than the engagement and 0.2 mm short of the
  plunger's own stop. The servo sits in a pocket of an integral lock block inside `body_upper`,
  with M3 ear screws into heat-set inserts. The unpowered spring re-seats the pin.

#### Load path

- **Three-leg stance, locked.** Body weight goes to the shoulders and down the vertical legs to
  the outer feet. The share on the centre foot goes up the carriage, through the LM12LUU
  bearings into the shafts, and into the floor and top bosses of `body_lower`. The lock pins take
  the tilting moment in shear at 50 mm radius into the leg plates. The actuator back-drive
  shares that moment.
- **Unlocked tilt.** The body centre of gravity stays ahead of the shoulder axis, so the foot is
  always pushed onto the floor and the post stays in compression. It is never less than 17 N,
  including the centre-of-gravity uncertainty box and floor friction.
- **Two-foot stance.** The lifted centre leg hangs from the carriage. The pins hold the body at
  0 deg, and the pendulum body needs only a small moment.

#### Check results (`python scripts/check_stance.py`, calculated, not measured)

Final run 2026-09-12: 126 poses (60 strokes each way plus contact and both endpoints), 1086
mesh-intersection pairs, exit 0.

| Class | Criterion | Result |
| --- | --- | --- |
| Clearance | two-foot centre wheels >= 20 mm above the floor at yaw -30, 0, 30; toe-stop swing clears the floor; lifted foot rests on the heel stop | PASS: 25.00 mm; toe stop 18.55 mm; foot CG 21.4 mm behind the hinge |
| Support | margin >= 15 mm over a +/-8, +/-8, +/-40 mm body CG box and yaw +/-30 deg | PASS: two-foot 28.1 mm; three-leg 75.9 mm; loaded transition minimum 41.8 mm |
| Force | calculated force <= 300 N / 3; holding <= 500 N / 3 | PASS: 38.3 N; holding 18.9 N |
| Lock | receiver within 0.1 mm at both endpoints; engagement >= 3 mm; sensed minimum >= 3 mm; web >= 2 mm; post compression >= 5 N; factored release <= servo tip force | PASS: misalignment 0.000 mm; engagement 5.00 mm; sensed 3.10 mm; web 2.34 mm; post 8.9 N; release 26.1 N and 32.7 N against 39.1 N |
| Interference | carriage, housing, centre foot and wheels, actuator, shafts, battery and both locks against the body rings, legs and outer feet, at every pose; <= 1 mm3 per pair | PASS: largest 0.150 mm3 |

`python scripts/stability.py` for the same meshes: 13.20 kg. Two-foot CG (0, 10.5, 315.6) mm,
support margin 34.5 mm. Three-leg CG (0, 44.2, 319.9) mm, support margin 89.2 mm, tip-back
15.6 deg. The stability margins have no CG uncertainty box, so they are larger than the check's.

#### Assumptions

None of these is measured. Each is stated in `CRITERIA` in `scripts/check_stance.py`.

- Printed fill 0.45 of solid; purchased parts as point masses; allowances as listed in `scripts/stability.py`.
- Body-group centre-of-gravity uncertainty +/-8 mm (X, Y) and +/-40 mm (Z).
- LM12LUU friction 0.05, ten times the catalogue value, times the bearing-moment lever.
- Pitch-hinge friction moment 150 N.mm.
- Floor force on the centre foot during the tilt is at most 3 % of its load. This requires the
  firmware to drive the centre-foot motors at the kinematic ground speed. Coasting TT gearboxes
  are not assumed.
- Pin friction in the bushing 0.10 (greased). Release factor 1.5. Servo supply 6.0 V.
- SS-01GL lever geometry beyond the catalogue OP, OT and MD is an envelope. MG995 horn and ear
  geometry are envelopes; drill the horn for the M3 tip pin.
- GN 412.2 receivers are held by an 11.0 mm thread-forming bore in PETG. Retention torque is not
  tested.

#### Not physically validated

- The masses, centre of gravity, friction, floor force and actuator force are calculated.
- Printed carriage, lock block, shaft bosses and receiver web strength, pin bending, bushing
  retention and creep are untested. No printed strength rating is claimed.
- Switch calibration, pin seating during the creep, and power loss during a transition need the
  built robot.
- The 30 deg caster stop and the 4.1 mm sole gap to the outer feet need a turning test.

## 4. Fits and tolerances

Every clearance, insert pocket and nut pocket below comes from the functions in `cad/lib.scad`.
If a hole size needs changing, change the function, not the part.

### 4.1 Screw clearance holes, `clearance_d(m)`

| Thread | Hole mm |
| --- | --- |
| M3 | 3.4 |
| M4 | 4.5 |
| M5 | 5.5 |
| M6 | 6.6 |
| M8 | 9.0 |
| M12 | 13.0 |

### 4.2 Heat-set insert pockets, `insert_d(m)` and `insert_depth(m)`

| Insert | Pocket diameter mm | Pocket depth mm | Insert used |
| --- | --- | --- | --- |
| M2 | 3.2 | 4.0 | ruthex, 4.0 mm tall |
| M2.5 | 3.7 (estimated from the same table) | 5.0 (estimated) | any 2.5 mm brass |
| M3 | 4.0 | 6 | Adafruit 4255, M3 x 4 mm |
| M4 | 5.6 | 8 | ruthex RX-M4x8.1, 8.1 mm tall |
| M5 | 6.4 | 9.5 | ruthex RX-M5x9.5, 9.5 mm tall |

The ruthex table reads "Insert hole (mm) 3,2 / 4,0 / 5,6 / 6,4" for M2, M3, M4 and M5, which
is what `insert_d()` returns. The design rule in `research/components-mechanical.md` is to
model the pocket about 0.2 mm over the nominal insert hole and 1 mm deeper than the insert.

### 4.3 Nut pockets, `nut_af(m)` and `nut_h(m)`

Across flats includes 0.4 mm of clearance.

| Thread | Across flats mm | Depth mm |
| --- | --- | --- |
| M3 | 5.9 | 2.4 |
| M4 | 7.4 | 3.2 |
| M5 | 8.4 | 4.7 |
| M8 | 13.4 | 6.8 |
| M12 | 19.4 | 10.8 |

### 4.4 Bearing, wheel and slot fits

| Fit | Value | Where |
| --- | --- | --- |
| 6001 bearing seat | 28.0 + 0.2 = **28.2 mm** bore, 8.2 mm deep | `lg_bearing_fit` in `cad/legs.scad` |
| Bearing bore relief | 24 mm through-hole below each seat | so the outer race seats on a ledge |
| Shoulder bushing | 12 mm bore x 16 mm OD bronze, pressed into a 16 mm printed bore | `research/components-mechanical.md` |
| Index dowel | 6.0 mm pin in a **6.2 mm** hole | `shoulder_index_d` |
| Motor pocket | envelope **+0.4 mm** all round | `motor_pocket_clear` |
| Head-drive motor pocket | envelope **+0.3 mm** | `hd_clear` |
| Wheel cavity | **3 mm** clearance around each 63 x 29 mm wheel | `ft_wheel_clear` |
| Ankle tongue in the foot slot | 17.4 mm tongue in a 17.6 mm slot = **0.2 mm** | `leg_tongue_t`, `foot_slot_w` |
| Leg comb joint | **0.2 mm** each side | `lg_finger_clear` |
| Head-drive hinge boss to lug | **0.2 mm** each side | `hd_boss_half` = 20.8 |
| Dome plate to body lip | **1.5 mm** radial | `dome_plate_r_out` 153.5 against 155 |
| Dome band to body top edge | **1.9 mm** vertical | `dome_gap` |
| Acrylic lens seats | seat diameter **+0.5 mm**, glued | `cad/dome.scad` |
| Head-drive slot | 36 x 60 mm against a 58 mm minimum | `head_slot`, `hd_slot_min` |

**The wheel press fit is the one fit you cannot control.** The Adafruit 3766 presses onto a
5.40 mm D-shaft with a 3.70 mm flat and has no retaining screw. Wheel pages quote a 3.5 mm
flat and the motor drawing quotes 3.7 mm; the press fit absorbs the difference.
`research/loads.md` section 4 warns that lateral scrub of up to 6.8 N can walk a wheel off its
shaft. Keep the wheel hub within 1 mm of the gearbox face, and check the wheel's axial
position after the first hour of driving.

---

## 5. Load screening summary

Full working is in `research/loads.md`. This is the summary and the two things it changes.

### 5.1 Mass budget

| Group | Nominal g | Low g | High g |
| --- | --- | --- | --- |
| Body | 3,018 | 2,600 | 3,400 |
| Dome | 947 | 800 | 1,100 |
| Head drive | 440 | 350 | 600 |
| Outer legs (2) | 2,457 | 2,100 | 2,800 |
| Centre leg | 500 | 400 | 600 |
| Feet (3) with motors and wheels | 2,050 | 1,800 | 2,300 |
| Electronics and wiring | 750 | 600 | 900 |
| Battery | 2,260 | 2,260 | 2,260 |
| Fasteners | 851 | 700 | 1,000 |
| **Total** | **13,273** | **11,610** | **14,960** |

13.3 kg nominal, 130.2 N. That is above the 8-11 kg the note expected. The cause is wall
thickness on a 317 mm cylinder. Every extra kilogram cuts the drive margin, cuts runtime and
raises turning scrub, so **weigh every print as it comes off the bed and keep a running
total.**

Two cross-checks now exist. The slice predictions in section 2.4 put the six sliced parts plus
the dome at 5,028 g against a 5,894 g budget for the same groups, about 15 percent under. The
whole-robot screening in `docs/stability.json` gives **11,705.5 g**, against the 13,273 g
nominal above. Both say the same thing: the package is tracking at the **low end** of the
budget range, which is the good direction.

### 5.2 Drive margin

Six drive motors, two per foot, four wheels per foot, 63 mm wheels.

| Case | Rolling resistance N | Per-motor current A | Speed m/s | Margin at the 1 A limit | Margin at stall |
| --- | --- | --- | --- | --- | --- |
| 13.3 kg, Crr 0.02 | 2.60 | 0.385 | 0.54 | **3.6x** | 5.7x |
| 13.3 kg, Crr 0.04 | 5.21 | 0.620 | 0.43 | 1.8x | 2.9x |
| 11.0 kg, Crr 0.02 | 2.16 | 0.345 | 0.56 | 4.4x | 6.9x |
| 11.0 kg, Crr 0.04 | 4.31 | 0.540 | 0.47 | 2.2x | 3.5x |

Six motors move 13.3 kg on a level hard floor. Grade capability is 2-3 degrees at the 1 A
driver limit and 4-5 degrees at stall. Carpet, thresholds above about 5 mm and ramps are
outside the envelope.

**Turning, not straight driving, is the limit.** Spin-in-place needs 4.1 to 9.3 N per side
against 4.7 N available at the 1 A limit. Command arc turns of 0.5 m radius or more by
default, and allow spin only at full 6 V with a time limit.

### 5.3 Shoulder moment and hoop strength

- **Shoulder moment.** The design case is the robot rocked back onto the rear axle contacts
  with the centre foot lifted: 6.2 N.m, times a 3x dynamic factor, is **9.4 N.m per shoulder**,
  with 176 N of vertical shear. Every printed section has a 7x margin or better (section 3.2).
- **Body ring hoop strength.** Shoulder load enters the shell as in-plane shear at 0.35 MPa.
  The worst radial case over a 100 mm shell height gives 26.7 MPa, which is marginal against
  the 34 MPa PETG HF figure; over the full ring with the ring ribs it drops to 6.9 MPa.
  **The ring ribs are what make the shell work. Keep at least one ring rib within 30 mm of
  each shoulder boss.**
### 5.4 Stability, measured from the CAD

**Revision D supersedes this section.** The legs are now vertical and the centre foot stands
ahead of the outer feet. `docs/stability.json` reports both stances, and section 3.9 gives the
checked margins: two-foot 28.1 mm, three-leg 75.9 mm, tip-back 15.6 deg. The revision C text
below is kept for the record.

The tipping numbers in `research/loads.md` section 7 assumed the centre foot stood 290 mm
**ahead** of the outer-foot line. The built geometry puts it 39.2 mm **behind** them
(section 1.3), so those numbers do not apply and are not repeated here.

`docs/stability.json` replaces them. It is a screening calculation: STL volumes at a 0.45 fill
fraction times 1.27 g/cm3, plus every purchased item as a point mass, in the three-leg stance.
Nothing was weighed.

| Measure | Value |
| --- | --- |
| Total mass | **11,705.5 g** (printed 6,046.9 g, purchased 5,658.6 g) |
| Centre of gravity (x, y, z) | **(0.1, 52.3, 301.8) mm** in the assembly frame |
| Wheel contact patch, fore-aft | y **32.0 to 161.2 mm** |
| Wheel contact patch, across | x **-205.5 to 205.5 mm** |
| Outer foot axle mean | y 116.2 mm |
| Centre foot axle mean | y 77.0 mm |
| Centre-foot static share | **1.63** |
| Tip-back margin | **20.3 mm**, **3.9 degrees** |
| Tip-forward margin | 108.8 mm, 19.8 degrees |
| Side tip | 34.2 degrees |

Two things in that table need reading carefully.

- **The centre-foot share of 1.63 is not 163 percent of the weight in practice.** It is what
  the two-line axle model gives when the centre of gravity (y 52.3) lies *behind* the
  centre-foot axle line (y 77.0). The real robot rests on the centre-foot wheels and the rear
  wheels of the outer feet, and the front wheels of the outer feet carry almost nothing. The
  model is degenerate here; the bathroom-scale test in assembly.md stage 11 is the measurement
  that settles it.
- **The tip-back angle of 3.9 degrees is the headline risk.** The centre of gravity sits only
  20.3 mm ahead of the rear contact edge, over a centre-of-gravity height of 301.8 mm. The
  acceptance criterion is 15 degrees. **The design as modelled does not meet it**, and the
  robot will rock back onto the centre foot under braking or over a bump.

The fix is to move the centre of gravity forward. The battery already sits `battery_y` = 15 mm
forward of the body axis on its shelf, inside a printed curb, and `docs/stability.json` puts
its centre at y 87.3 mm in the assembly frame. The remaining adjustments, in order of effect,
are: rake the outer legs further forward, lower the shoulder axis in the body, and move the
electronics deck load forward off the rear chord. Tip-forward (19.8 degrees) and side tip
(34.2 degrees) both have room to give.

Total mass of 11.7 kg sits at the low end of the 11.6 to 15.0 kg range in `research/loads.md`
section 1, so the drive-margin row to read in section 5.2 is the 11.0 kg case: **4.4x at
Crr 0.02** and 2.2x on a poor floor.

### 5.5 Ranked risks

1. **Turning scrub exceeds drive force.** Retired by a 0.5 m arc at 50 percent PWM without a
   stall.
2. **Mass over target.** Retired by weighing every print against the section 5.1 budget.
3. **TT gearbox bores and press-fit wheels** under 11-14 N radial and 7 N lateral. Retired by
   an hour of figure-8 driving with under 0.3 mm of shaft play growth.
4. **Tip-back.** Now the **top** structural risk: the CAD screening in section 5.4 gives
   3.9 degrees against a 15 degree criterion. Retired by moving the centre of gravity forward
   and then passing the tilt-board test and the centre-foot scale reading.
5. **Motor heating and runtime at the 1 A limit.** Retired by 20 minutes of driving with the
   motor cases below 70 C.

Lower ranked: head friction-wheel slip, retired by the rim pull test; PETG creep under the
shoulder bolt, retired by the crush sleeve and a 48 hour loaded soak at 40 C.

---

## 6. Print order

Print in this order. The first two prints are fit checks, and they exist so a wrong dimension
costs 20 hours, not 250.

| Order | Part | Why here | Check before going on |
| --- | --- | --- | --- |
| 1 | `head_drive` (3 h) | Cheapest real test of the motor pocket and the M3 hole spacing | Cut the two webs. Fit an Adafruit 3777 in the saddle and press a 3766 on. The gearbox must seat on the pocket ceiling and the two M3 x 30 must pass through both wall holes. |
| 2 | **One** `foot_outer` (20 h) | The operator's fit check: motors, wheels and the ankle before anything else is committed | Push both motors up into the pockets from the open sole. Press all four wheels on. Each wheel must turn freely in its 3 mm cavity. Fit the M3 x 35 tab bolts. Drop a `leg_lower` tongue offcut, or a 17.4 mm packer, into the ankle slot and check the pivot bore lines up. |
| 3 | `foot_center` (9 h) | Same drive fit, plus the caster nut slot | Slide the M12 nut into its slot from +X before the motors go in. It must not fall out when the foot is upright. |
| 4 | `leg_center` (5 h) | Mates to part 3 | Press both 6001 bearings into their seats. Fit the M12 x 70 and check the leg swivels +/-60 degrees on the stop. |
| 5 | `leg_lower` x2 (11 h each) | Now the ankle interface is proven | Check the tongue enters the foot slot and the lock holes A and B line up with the foot's lock bore at 0 and 18 degrees. |
| 6 | `leg_upper` x2 (20 h each) | The comb joint has a mating half to test against | Dry-fit the comb. The four M4 x 80 must pass straight through both halves. |
| 7 | The second `foot_outer` (20 h) | Only after the leg proves out | |
| 8 | `body_lower` (estimated 25-35 h) | The biggest risk print; everything below bolts to it | Check the centre-leg flange bolt pattern, the battery against the shelf curb, the four 26 mm socket windows over the centre-leg nuts, and that an M8 nut slides into each of the four captive rod traps at z 46. |
| 9 | `body_upper` (estimated 35-55 h) | The longest single print in the package | Check the shoulder bolt line, the two index holes per pad, the seam lip fit against part 8, the deck seats against the real boards, and the top plate hole circle against the real lazy susan. |
| 10 | `dome` (35 h) | Last, because it is the show surface and benefits from a tuned machine | Check the lazy-susan hole circle against the real bearing before pressing any insert. |

Print the first foot, the first leg pair and the two body rings from the **same spool batch**
so colour matches on the visible white surfaces.

---

## 7. Finishing and paint masking

The scheme is the standard one: white body, silver or brushed-aluminium dome, blue panels and
blue trim.

### 7.1 Surface preparation

1. Remove every support and every sacrificial web first. File the head-drive web stubs flush.
2. Scrape the seam lines and the bridge undersides. Do not sand a mating face, a bearing seat,
   an insert pocket or a bolt hole. Sanding those changes a fit.
3. Fill layer lines on the visible outer faces only: the dome shell, the body skin, the outer
   leg faces and the foot shells. Use a high-build filler primer, two light coats, sanded at
   320 then 400 grit. Three or four cycles are normal on PETG.
4. Wash with isopropyl alcohol and let it dry before any colour goes on.
5. **Prime before paint.** PETG is a poor bond surface. An adhesion-promoting primer is worth
   the extra step.

### 7.2 Masking

The panel recesses are 0.8 mm deep (`dome_panel_recess`) with a 3 mm frame
(`dome_panel_frame_w`). The recess edge is the mask line, so masking tape can be laid into the
recess and cut against the frame edge with a fresh blade.

| Area | Colour | Masking note |
| --- | --- | --- |
| Body skin, skirt, legs, feet | Gloss white | Mask the shoulder pads, the seam flange face, the top plate and every bolt hole. |
| Body blue band and panel trim | Blue | The lower ring's band details and the leg trim strips. |
| Dome shell | Silver or brushed aluminium | Mask the 6 mm blue-band line at z 25.9 to 31.9 (0.4 mm deep, sloped top edge) and every panel recess. |
| Dome panels P1-P14, pie panels PP1-PP6 | Blue where the reference calls for it | Paint blue first, mask the recess, then silver over it. Overspray on silver is easier to correct than blue overspray on a recess. |
| Radar eye housing | Silver, lens seat left bare | Do not paint the 52.6 mm lens seat or the 2 mm inner lip. Paint thickness there stops the acrylic disc seating. |
| Holoprojector barrels | Silver outside, flat black inside | Flat black inside the 44.1 mm bore kills reflections behind the NeoPixel. |
| Logic display windows | Flat black inside the pocket | Mask the window opening itself. |
| Ankle bracelet bands, hose fittings | Aluminium or steel | The bracelet band stands 1.5 mm proud, so it masks cleanly. |
| Foot half-moon plates and door panels | White with a blue or silver detail | The recesses are all 0.8 mm or less. |

Leave bare: every mating face, the dome plate underside where the friction wheel runs, the
lazy-susan races, both bearing seats, the ankle tongue faces and the comb joint faces. **Paint
on the dome plate underside changes the friction coefficient the head drive depends on.**

### 7.3 Order of finish

Paint the dome, the body rings, the legs and the feet **before** any insert is pressed and
before any electronics go in. The only exception is the dome plate: press its four M5 inserts
first, mask them, then paint. A brass insert is easier to mask than to clean.

---

## 8. Maintenance

### 8.1 After the first hour of driving

- Re-check every M8 nut: four body rods, four leg rods, four centre-leg flange bolts, four
  ankle bolts. New prints bed in and the preload drops.
- Check each wheel's axial position against a mark made at assembly. A wheel that has walked
  outward is the failure mode `research/loads.md` section 4 predicts.
- Measure shaft radial play with a dial indicator. Reject more than 0.3 mm of growth.

### 8.2 Every ten hours of driving

| Check | Accept |
| --- | --- |
| M12 shoulder bolts | No play at the leg when the robot is rocked; nyloc still tight |
| Index dowels | Both pins fully home, no elongation of the 6.2 mm holes |
| Ankle lock bolts | Tight, and in the stance hole you expect |
| Centre caster | Turns freely by hand, +/-60 degrees, stop pin not worn |
| Lazy susan | Dome turns by hand with no notch and no lift |
| Head-drive tyre | Spring still 4 to 6 mm compressed; tyre clean and not glazed |
| Motor case temperature after 20 minutes | Below 70 C by IR thermometer |
| Cable ties at the slip ring | Both bundles still tied within 40 mm of the ring |

### 8.3 Wear items

- **Friction wheel.** The head-drive tyre wears and glazes. Clean it with isopropyl alcohol.
  Replace when the dome slips at a 6 mm spring compression.
- **Drive wheels.** Twelve of them, press fit, 1.50 USD each. Keep spares.
- **Lazy susan.** Supplied ungreased. Add a light grease at build and again yearly.
- **Battery.** An SLA vents hydrogen when charged. Charge upright and in free air. Charging
  and its procedure are in [electrical.md](electrical.md) section 2, and they are not repeated
  here.

### 8.4 Storage

Store in the three-leg stance, on its wheels, indoors. Do not store in a hot car: PETG softens
at 62-68 C and the battery likes heat even less than the prints do. Disconnect the Powerpole
pair for any storage longer than a week and charge the battery monthly.

---

## 9. Interface conflicts

### 9.1 Closed

Five leg-and-foot conflicts are resolved in the CAD, and each is now held closed by an
`assert()` so a change to `params.scad` cannot move one part without the other.

| Was | Now |
| --- | --- |
| Ankle lock hole: foot drilled 40 mm ahead of the pivot, leg cut one bore 25 mm below it | `cad/legs.scad` cuts holes A and B on the same 40 mm arc (`lg_lock_r`, `lg_lock_holes`); the old bore is gone |
| `ankle_bolt_spacing` = 50, used by neither part | **40**, and `ft_lock_r` = `lg_lock_r` = `ankle_bolt_spacing` |
| Caster stop pin at radius 35 in the foot, groove at radius 22 in the leg | Pin moved to **radius 22 on the stem-block top**; the 16 mm ledge fin is gone |
| Centre-foot wire hole at (-18.5, 20), off the leg's arc slot | **(0, `caster_trail` - 21) = (0, -1)**, leg-frame radius 21, on the slot at every swivel angle |
| `caster_bearing_gap` = 20, which does not fit | **18**, matching `lg_bearing_cc` |
| Body rings described from the specification | `cad/body.scad` exists, 695 lines, and both rings pass validation. Sections 1, 2 and 3 are written from it |

### 9.2 Still open

| Conflict | What the files say | Build to |
| --- | --- | --- |
| Leg rod cut length | `cad/legs.scad` now says "CUT TO 390 mm (from M8 x 400 stock)". `bom/hardware.csv` H09 still plans 425 mm cuts. | **390 mm.** The BOM cut plan needs correcting. |
| Dome radii | `params.scad` `dome_hp3_r` 101, `dome_rld_z` 52, `dome_eye_z` 108. `cad/dome.scad` overrides to 69.1, 73.5 and 118. | The dome file. The params values are full-size or mis-transcribed. |
| Slice report | `cad/h2d-slice-check.json` predates `cad/body.scad` and the resolved leg and foot geometry, and its dome row still fails on the script's `--arrange` step. | Re-run `python scripts/slice_check.py`. |
| Tip-back | `docs/stability.json` gives 3.9 degrees; the acceptance criterion is 15 degrees. | Revision D closes this: 15.6 degrees in the three-leg stance (section 5.4). |
| Revision D ring slicing | On 2026-09-12 `python scripts/slice_check.py` passed 8 of 10 parts. `body_upper` and `body_lower` did not slice inside the 300 s per-part bound with tree supports. With normal supports they failed with "Found G-code outside of the printable area". | Unverified for the H2D. Slice both rings with a longer bound (revision C used 3600 s), or supply a support setting that keeps supports inside the ring. |

---

## 10. Where each number comes from

| Number | Source |
| --- | --- |
| Every dimension and angle | `cad/params.scad` |
| Frames, stance placement, interference checks | `cad/r2d2.scad` |
| Clearance, insert and nut pocket functions | `cad/lib.scad` |
| Per-part geometry, fasteners, print orientation, supports | the header comments in `cad/dome.scad`, `cad/body.scad`, `cad/legs.scad`, `cad/feet.scad`, `cad/head_drive.scad` |
| Seam, shoulder, top plate, deck and floor interfaces | the INTERFACE and DEVIATIONS blocks in `cad/body.scad` |
| Total mass, centre of gravity, foot share, tipping | `docs/stability.json` |
| Mesh sizes, watertightness, envelope fit | `cad/validation.json` |
| Predicted mass and print time | `cad/h2d-slice-check.json`, and `cad/integration-round2.md` for the dome |
| Mass budget, drive margin, shoulder moment, tipping, risks, tests | `research/loads.md` |
| Scaled club dimensions | `research/proportions.md` section 6 |
| Bearings, bolts, inserts, filament, prices | `research/components-mechanical.md` |
| Fastener quantities and cut plan | `bom/hardware.csv` |
| Harness, fuses, charging, commissioning | `docs/electrical.md` |
| Firmware, pin map, control page | `docs/firmware.md` |
