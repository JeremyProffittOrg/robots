# Robot project envelopes — physical and electrical constraints for perimeter sensing

Lane: `robot-project-envelopes`. Written 2026-09-12 from the repository at `C:/dev/robots`.

This is a **repository-derived** document. Every number below was read out of a file in this
repo and the file path is given. Nothing here was measured on hardware, because none of the
three robots has been built — all three projects state this explicitly. Where the repo does not
answer a question, the entry reads **"not specified in the repo"** and nothing is substituted.

Confidence marks used here:

| Mark | Meaning |
| --- | --- |
| **repo-verified** | Read directly from a named file in this repository. |
| **repo-derived** | Arithmetic on two or more repo numbers; the inputs are shown. |
| **inferred** | Standard external knowledge (e.g. a board's published pin list) applied to repo facts. Not a repo fact. |
| **not specified in the repo** | The repo is silent. No value is offered. |

The three projects are far less alike than their shared parts list suggests. They differ by a
factor of **3.8 in mass** (about 3.5 kg vs 13.3 kg), by **152 mm in height**, by an order of
magnitude in **spare 5 V current** (0.3 A vs about 4.1 A), and — most important for sensing —
in whether a controller has *any* free GPIO at all. Two of the three have a rotating head with
**no slip ring**, which rules out a head-mounted sensor outright.

---

## 1. Side-by-side summary

| Property | `dalek` | `r2d2` (revision C) | `fable-r2d2` |
| --- | --- | --- | --- |
| Shape at floor level | Circular fender, 300 mm diameter | Three separate feet, body suspended | Three separate feet, body suspended |
| Overall height | 563.8 mm nominal | 609.6 mm nominal | 715.9 mm (driving stance) |
| Widest plan dimension | 300 mm (the base circle) | ~438 mm side-foot exterior span | ~486.7 mm outer-foot outside edges (repo-derived) |
| Estimated assembled mass | ~3.5 kg (repo-derived; 2.429 kg plastic + parts) | 8.953 kg estimated, 9 kg design ceiling | 13.273 kg nominal |
| Drive | 4 x TT 3777, skid steer, 4 x 63 mm wheels | 6 x TT 3777, 12 wheels, rear-foot steering servo | 6 x TT 3777, 12 wheels, castering rear foot |
| Controller | LilyGO TTGO T-Display (classic ESP32) | Adafruit HUZZAH32 3405 (classic ESP32) | Raspberry Pi 4 4 GB **+** Adafruit KB2040 |
| Battery | Bioenno BLF-1206A, 12 V 6 Ah LiFePO4, 72 Wh | Bioenno BLF-1206A, 12 V 6 Ah LiFePO4, 72 Wh | Power-Sonic PS-1270 F2, 12 V 7 Ah SLA, ~2 kg |
| Spare 5 V logic current | ~0.3 A | not specified in the repo | ~4.1 A |
| Free GPIO on the main MCU | essentially none | **one pin (GPIO5)** | Pi: many. KB2040: one pin (D0/GP0) |
| Free I2C bus | shared 0x40 bus only | shared bus, 0x40 + 0x48 used | Pi I2C-1 (5 addresses used) **+ an entirely unused KB2040 STEMMA QT bus** |
| Head/dome wiring path | **none** (no slip ring) | **none** (no slip ring) | 12-wire slip ring, **all 12 wires already assigned** |
| Shell wall at a candidate aperture | 1.8 mm PLA skirt / 4 mm PETG base ring | 1.2 mm PETG body skin | 3.6 mm PETG body / 3.0-3.2 mm dome |
| Existing ranging or presence sensor | none | none | none |
| CAD maturity | 10 STLs released, all checks pass | 10 STLs released, all checks pass | **`body_upper` and `body_lower` STLs do not exist yet** |

---

## 2. `dalek` — circular 300 mm base, the closest match to the 350 mm brief

Sources: `C:/dev/robots/dalek/docs/mechanical.md`, `C:/dev/robots/dalek/docs/firmware.md`,
`C:/dev/robots/dalek/docs/electronics-research.md`, `C:/dev/robots/dalek/cad/dalek.scad`,
`C:/dev/robots/dalek/cad/validation.json`, `C:/dev/robots/dalek/electronics/calculations.json`,
`C:/dev/robots/dalek/bom/electronics.csv`.

### 2.1 Footprint, height and the vertical stack

Design name is `ROUND-10`. The base is a **300 mm diameter circle** (repo-verified,
`cad/validation.json` gives `01_base` at 300.0 x 300.0 x 57.0 mm). Nominal assembled height is
**563.8 mm** (`docs/mechanical.md`). The whole robot is a stack of five rings bolted through
four M4 joints each.

World Z0 is the floor. The base datum is world **Z13.8** = wheel radius 31.5 minus 6 mm floor
thickness minus the 11.7 mm case-bottom-to-axle datum (repo-verified, `docs/mechanical.md`
"Coordinate map and stack joints").

| Section | World Z range | Height | Outside diameter | Material | Wall |
| --- | --- | --- | --- | --- | --- |
| `01_base` (fender/bumper band) | 13.8 – 67.8 | 54.0 mm | 300 (constant) | PETG | 4 mm ring wall, 6 mm floor |
| `02_lower_skirt` | 67.8 – 177.8 | 110.0 mm | 300 → 250 | PLA | **1.8 mm** |
| `03_upper_skirt` | 177.8 – 277.8 | 100.0 mm | 250 → 220 | PLA | **1.8 mm** |
| `04_shoulder` | 277.8 – 397.8 | 120.0 mm | 220 | PETG | **1.8 mm** |
| `05_neck` | 397.8 – ~449.8 | 66 mm print | 220 | PETG | rings + 1.2 mm liner |
| `06_head` (rotates) | 449.8 – ~563.8 | 114.0 mm | 198 drum / 220 dome | PLA | 3 mm drum, ~1.8 mm dome |

Wall thicknesses are repo-verified from `cad/dalek.scad` line 5 (`wall=1.8`), **line 22**
(`ring(150,146,54)` = 4 mm base band; an earlier draft of this document cited line 15, which is
the `groove()` module) and line 160 in the head module (`ring(99,96,43)` = 3 mm drum).

The section heights in the table above are **body** heights. The printed STL Z values in
`cad/validation.json` are 3 mm taller on four of the five rings (base 57.0, lower skirt 113.0,
upper skirt 103.0, shoulder 123.0) because each carries a 3 mm registry tongue above its body.

Ground clearance is **13.8 mm nominal, not measured** under the base floor (repo-derived from
the base datum). The measurement condition matters: 31.5 mm is the *catalogue* radius of an
unloaded Adafruit 3766 wheel, and `docs/mechanical.md` states "Actual motor padding and axle
height must be measured", while line 113 of the same file requires checking "bumper clearance
and ground clearance with actual tire deformation". Under a loaded 3-4 kg robot the real figure
will be below 13.8 mm. Do not size a floor-facing sensor's standoff from this number. The
wheel wells are cut inside radius 147, inboard boundary |X| = 80.5, well roof at base-local
Z52. The design rule in `docs/mechanical.md` is that **"the outside bumper remains continuous
around the full circle"**, and `cad/mechanical-checks.json` contains a passing check named
`continuous-bumper-missing-material` with 2,880 samples. Cutting a window in the base band
therefore breaks a released validation check.

### 2.2 Mass, drive and speed

- Predicted installed plastic: **2.429 kg** (repo-verified, `docs/verification.md`). Solid
  material upper bound 3,157.3 g (`cad/validation.json`).
- Battery 0.7 kg; five TT motors at 30.6 g each; five 63 mm wheels; four MG92B servos;
  electronics. **Finished mass is not specified in the repo.** The earlier 3 kg planning target
  is explicitly retired; `docs/assembly.md` uses "a 4 kg finished robot" only as a proof-load
  worked example.
- Drive: four Adafruit 3777 TT motors, 1:48 gearbox, driving four Adafruit 3766 wheels
  (63 x 29 mm), skid steer, at 5 V through DRV8833 bridges at the stock 1 A limit.
  **Supply flag: the Adafruit 3766 wheel is out of stock at Adafruit as of 2026-09-12.**
- Speed: `electronics/calculations.json` gives `ideal_6V_no_load_speed_m_s_at_250rpm` =
  **0.8247 m/s**, explicitly flagged as ideal and unverified. **That repo number rests on a
  250 rpm input the motor manufacturer does not give, and is about 25 percent high.** The
  primary source, the Adafruit 3777 product page, specifies "Min. Operating Speed (6V):
  200 +/- 10% RPM" with "Gear Ratio: 1:48" and "Rated Voltage: 3~6V". At 200 rpm no-load and
  the repo's own `wheel_radius_m` = 0.0315, the ideal 6 V no-load speed is
  **0.660 m/s (0.594 - 0.726 m/s across the +/-10% tolerance)**, not 0.8247 m/s. Both figures
  are no-load at 6 V; the robot's drive rail is 5 V, and the DRV8833 1 A limit binds before
  either. Firmware caps forward at **110/255**, reverse 90/255, turns 50/255 inside and
  120/255 outside (`docs/firmware.md` line 46), and head PWM at 100/255 at 20 kHz
  (`docs/firmware.md` line 89; `calculations.json` `head_pwm_limit_of_255` = 100,
  `head_pwm_frequency_Hz` = 20000). **Actual ground speed is not specified in the repo** —
  the calculations file states "No encoder exists; PWM duty does not prove ground speed."
- The interface deliberately omits in-place pivots; four wide tyres scrub.

### 2.3 Controller, GPIO and I2C map

One **original LilyGO TTGO T-Display, classic ESP32**, 135 x 240 ST7789, 4 MB flash
(`docs/firmware.md`). Not the S3 and not the AMOLED version.

Full pin allocation, repo-verified from `docs/firmware.md` "Electrical contract":

| Function | GPIO |
| --- | --- |
| I2C SDA / SCL | 21 / 22 |
| Servo disable (PCA9685 OE + buffer OE) | 27 |
| Left forward / reverse | 25 / 26 |
| Right forward / reverse | 32 / 33 |
| Motor enable (all three DRV8833 SLP) | 12 |
| Head PWM, 20 kHz | 2 |
| I2S BCLK / LRC / DIN | 17 / 13 / 15 |
| Actuator power sense (input only) | 36 |
| Battery voltage sense (input only) | 39 |
| Stop / forget-router button | 35 |
| Reserved for the integrated display | 5, 16, 18, 19, 23, 4 |
| BOOT button | 0 |
| Reserved, board's own battery circuit | 34, 14 |

**Free GPIO: essentially none.** Every pin the firmware names is taken, and the two remaining
classic-ESP32 pins are the UART0 pair GPIO1/GPIO3 used for the serial console. Whether the
T-Display breaks out GPIO37/38 is **not specified in the repo**.

**I2C address map: one device, PCA9685 at `0x40`** (`docs/firmware.md`). Every other 7-bit
address is free, including `0x29` (ST VL53 family), `0x30`, `0x52` and `0x70`. Note that a
second PCA9685-family part or an INA219 at its `0x40` default **would collide**.

Consequence for sensing: a new sensor on this robot must be **I2C on GPIO21/22**, or it must
take over a pin that currently does something. A UART sensor has no free UART, and an
interrupt/data-ready line has no free pin.

### 2.4 Power rails and spare current

From `electronics/calculations.json` and `bom/electronics.csv`:

| Rail | Regulator | Rating | Design load | Spare |
| --- | --- | --- | --- | --- |
| 5V_MOTOR | Pololu D36V50F5 (4091) | 5.5 A **at 36 V in only** — see below | 5.05 A | **not established** |
| 5V_SERVO | Pololu D36V50F5 (4091) | 5.5 A **at 36 V in only** — see below | 4.05 A | **not established** |
| 5V_LOGIC | Adafruit MPM3610 4739 | 1.2 A over the whole 6-21 V input range | 0.90 A | **0.30 A** (repo-derived) |
| 3.3 V | T-Display onboard regulator | not specified in the repo | — | not specified in the repo |

**Correction — the 5.5 A regulator rating is quoted in the repo without its measurement
condition.** Pololu's own specification for the D36V50F5 (item 4091) reads "Continuous output
current: 5.5 A" with footnote 3: "Typical max continuous output current **at 36 V in**. Actual
achievable continuous output current is a function of input voltage and is limited by thermal
dissipation." The family figure on the same page is "Typical maximum continuous output current:
3.5 A to 8 A (see the maximum continuous output current graph below)." This robot runs the
regulator from an 11.2 - 14.6 V LiFePO4 pack, roughly a third of the 36 V the 5.5 A is measured
at, so **5.5 A is not the applicable rating here and the 0.45 A / 1.45 A spare figures an
earlier draft of this document gave are not established.** The number that governs must be read
off Pololu's output-current graph at the real input voltage, or measured. Pololu also lists both
D36V50Fx parts as "Rationed (Active and Preferred)" — constrained supply, not discontinued.

The 5V_LOGIC spare is sound: Adafruit states the MPM3610 breakout (4739) gives "5V output with
up to 1.2A current" available "across the entire input voltage range of 6V to 21V", so the
1.2 A carries no hidden input-voltage condition and 1.2 - 0.90 = **0.30 A** stands.

Pack: Bioenno BLF-1206A, 12 V / 6 Ah / 72 Wh, 12 A continuous, 0.7 kg — **pack figures are
repo-only; no Bioenno product page or datasheet was reachable to confirm them**. Estimated peak
pack draw 5.25 A at 11.2 V (`estimated_peak_pack_A_at_11p2V_85pct` = 5.2521, at 85 percent
assumed converter efficiency). Estimated runtime 3.6 h at 15 W, 2.16 h at 25 W, both assuming
`battery_design_usable_fraction` = 0.75. Main fuse F1 is 7.5 A (`bom/electronics.csv`,
Littelfuse 025707.5). `calculations.json` heads all of these with "engineering estimates; not
measurements of a built robot".

**The binding constraint is the 0.30 A of spare 5 V logic current.** Both 5 V actuator rails
are cut by the physical S2 stop switch, so a perimeter sensor must not live on them — it would
go blind exactly when the operator hits stop.

### 2.5 Where a sensor can physically go

| Candidate location | World Z | Available area | Assessment |
| --- | --- | --- | --- |
| Base fender band | 13.8 – 67.8 | full 300 mm circumference, 54 mm tall | Best height for floor-level obstacles and for a pet at 200-500 mm. **But** the continuous-bumper rule and its passing check forbid a cut, and the 4 mm PETG ring plus internal ribs sit behind it. |
| Lower skirt | 67.8 – 177.8 | 110 mm tall band, tapering 300 → 250 | 1.8 mm PLA, the thinnest and most radar-friendly wall on the robot. Already carries 12 hemispheres per row at world Z93.8 and Z143.8 and 12 vertical seams; a panel would have to sit between two seams (30 degree pitch, so ~65 mm of clear arc at the top of the taper). |
| Upper skirt | 177.8 – 277.8 | 100 mm tall, 250 → 220 | 1.8 mm PLA. Hemispheres at world Z203.8 and Z253.8. |
| Shoulder front grille | 286.8 – 380.8 | 24 x 94 mm panel, X -12..+12 | **A real through-aperture already exists**: 27 holes of 4.2 mm diameter in a 3-wide by 9-tall grid at world Z305.8-361.8 (`cad/dalek.scad` line 86). It is the speaker grille. Far too small for optics; relevant only as proof the geometry tolerates a cut there. |
| Shoulder rear recess | 329.3 – 355.3 | 52.2 x 26 mm | Occupied by the T-Display PCB. |
| Neck slats | ~397.8 – 447.8 | 24 slats, 2 x 1.6 mm | **Blocked**: an opaque 1.2 mm liner ring at radius 96.3-97.5 sits behind the slats by design, to hide the head motor. |
| Head / dome | 449.8 – 563.8 | rotates continuously | **Impossible.** `docs/firmware.md`: "All audio stays in the fixed body, so the head can turn indefinitely without twisting an electrical cable" and `docs/research.md`: no slip ring is required because nothing electrical moves. There is also no head-angle encoder, so a head-mounted sensor would have no known bearing. |

Internal volume: the base has a battery pocket of 76 x 116 mm clear plan with a 6 mm floor, and
two FR4 electronics plates 160 x 56 x 2 mm centred at (0, -93) and (0, +93) with their
undersides at base-local Z34 (world Z47.8), each carrying an 81 x 51 mm protoboard. Space for a
new board is tight and is **not specified in the repo** as having a reserved area.

### 2.6 Existing sensors in the BOM

None for obstacles or presence. The only sensing in `bom/electronics.csv` is two resistive
voltage dividers (battery sense to GPIO39, actuator-rail sense to GPIO36). No IMU, no encoder,
no range finder, no camera.

---

## 3. `r2d2` (revision C) — 259 mm body on three feet, 9 kg ceiling, one free pin

Sources: `C:/dev/robots/r2d2/docs/mechanical.md`, `C:/dev/robots/r2d2/docs/electrical.md`,
`C:/dev/robots/r2d2/cad/exterior.scad`, `C:/dev/robots/r2d2/cad/kinematics.scad`,
`C:/dev/robots/r2d2/cad/validation.json`, `C:/dev/robots/r2d2/cad/kinematic-check.json`,
`C:/dev/robots/r2d2/bom/electronics.csv`, `C:/dev/robots/r2d2/bom/mass-budget.csv`.

### 3.1 Footprint, height and shape at floor level

Nominally **609.6 mm high with a 259.25 mm main body diameter** (`docs/mechanical.md` line 5,
verbatim: "Revision C is nominally 609.6 mm high, with a259.25 mm main body diameter", and
line 114 "raised crown reaches approximately 609.6 mm overall").
`cad/exterior.scad` line 3 sets `R=129.625` (so 259.25 mm), `H=280`, `WALL=1.2`, `BODY_Z=165`,
`DOME_Z=456.8`.

**Caveat on the source file**: `cad/exterior.scad` is modified and uncommitted in the worktree,
and its line 1 now reads `// Revision D exterior relief, mm.` The constants above are read from
that revision-D working copy, not from a released revision-C file. They still agree with
revision C's published 609.6 / 259.25 in `docs/mechanical.md`, but a further revision-D edit
could move them without touching the prose.

The shape at floor level is **three separate feet, not a skirt**:

- Side-foot centres at X = ±165, Y = 0. Ground axles at foot-local Y ±37, Z31.5.
- Side-foot **exterior span about 438 mm** (repo-verified, `docs/mechanical.md`).
- `outer_foot` STL is 131 x 197.22 x 130 mm; `rear_foot` is 108 x 197.22 x 109 mm
  (`cad/validation.json`).
- The rear foot **translates** as posture changes: its centre moves from Y = -128.926 to
  Y = -247.785 across the actuator stroke (`docs/mechanical.md`, confirmed row-by-row in
  `cad/kinematic-check.json`). The front-to-back footprint therefore changes during operation.
- Required clear floor: **at least 500 x 600 mm plus the turning radius** (repo-verified).

The body itself is suspended: the lower body mesh including the skirt starts at **world Z130**,
and the main cylindrical wall starts at **Z165**. Under Z130 there is open air between the
three feet. **This is the critical difference from the Dalek**: there is no continuous skirt to
mount a floor-level sensor in, and a low sensor on the body would still be 130 mm up.

Vertical stack (repo-verified, `docs/mechanical.md` "Body and head stack"):

| Feature | World Z |
| --- | --- |
| Ankle pivot | 113 (`ANKLE_Z`, `cad/kinematics.scad`) |
| Lower body mesh / skirt bottom | 130 |
| Main cylindrical wall starts | 165 |
| Body seam (lower/upper split) | 269.7 |
| Shoulder axis | 390 (`HIP_Z`) |
| Head floor (2 mm 6061 plate) | 413 – 415 |
| 608 bearings | 415-422 and 434-441 |
| Upper body / fixed neck top | 454.3 |
| Dome datum | 456.8 |
| Crown | ~609.6 |

### 3.2 Mass, drive and speed

- **Estimated assembled mass 8.953 kg against a 9 kg design ceiling** (repo-verified,
  `docs/verification.json` and `docs/mechanical.md`). The document states plainly: "there is
  little reserve and **no payload allowance**."
- Installed prints 1,714.8 g; metal 2,318 g across thirteen cut profiles; battery 700 g;
  thirteen wheels 494 g; seven motors 214.2 g; servo 62.4 g (`bom/mass-budget.csv`).
- Drive: six Adafruit 3777 TT motors driving **twelve** ground wheels (two wheels share each
  motor), plus a seventh 3777 as an internal head friction drive.
- Steering: Adafruit 1142 MG-995 servo on the rear foot, limited to **8 degrees** of yaw.
  **Supply flag: Adafruit 1142 ("Standard Size - High Torque - Metal Gear Servo", TowerPro
  MG-995) is out of stock at Adafruit as of 2026-09-12.**
- Posture: Actuonix P16-100-256-12-P linear actuator, 300 N dynamic, 20 percent duty, stroke
  limited in software to 5.038 – 72 mm, giving about 0 – 15.054 degrees of body tilt.
- Speed: **not specified in the repo.** Ground PWM is capped at 90/255 and head PWM at 70/255,
  and `docs/mechanical.md` says explicitly "These are duty commands, not measured speed."
- Smallest commanded turn radius **roughly 0.92 m** in the upright stance, increasing as the
  rear foot extends.
- Acceptance gate: "no more than 0.5 A steady current per ground motor during gentle travel",
  and rear-foot rolling drag at or below 10 N.

Any sensor mass matters here. **8.953 kg of 9.000 kg is already committed**, so a sensor
package heavier than roughly 47 g pushes the design over its own stated ceiling.

### 3.3 Controller, GPIO and I2C map

One **Adafruit HUZZAH32 3405** (original ESP32 Feather; explicitly not the S3 and not V2).

Repo-verified pin list from `docs/electrical.md` "GPIO and named nets":

| Function | GPIO |
| --- | --- |
| Left forward / reverse | 14 / 32 |
| Right forward / reverse | 15 / 33 |
| Rear forward / reverse | 27 / 12 |
| DRV8833 SLP (all four) | 13 |
| DRV8833 FLT (input only) | 36 / A4 |
| Rear steering servo, via AHCT125 | 25 / A1 |
| Head AIN1 / AIN2 | 26 / A0 and 17 / TX |
| Post extend / retract | 4 / A5 and 16 / RX |
| I2C SDA / SCL | 21 and 22 / SCL |
| RUN sense (input only) | 39 / A3 |
| Pack sense (input only) | 34 / A2 |
| I2S BCLK / LRC / DIN | 18 / 19 / 23 |

Note the deliberate override: the Feather's default SDA header is GPIO23, and this design uses
GPIO23 for audio DIN instead, moving SDA to GPIO21.

Comparing that list against the HUZZAH32's broken-out pins (**inferred**, from the Adafruit
pinout: 26, 25, 34, 39, 36, 4, 5, 18, 19, 16, 17, 21, 23, 22, 14, 32, 15, 33, 27, 12, 13),
**exactly one pin is free: GPIO5 (SCK)**. Everything else is assigned. GPIO12 additionally
carries a boot-strapping warning and must keep its pull-down.

**I2C address map** (repo-verified, `docs/electrical.md` and `bom/electronics.csv`):

| Address | Device |
| --- | --- |
| `0x40` | INA219 current sensor (A0/A1 strapped to ground), actuator 12 V branch |
| `0x48` | ADS1115 (ADDR to ground), AIN0 = actuator position, other inputs grounded |

Free addresses include `0x29`, `0x30`, `0x52`, `0x70`-`0x77`. A new sensor defaulting to
`0x40` (many PCA9685 and INA-family parts) or `0x48` (ADS1115, TMP102) **collides**. The
breakouts' own installed I2C pull-ups are in use; the guidance is not to add 5 V pulls.

So on `r2d2` a perimeter sensor is practical as **I2C plus at most one interrupt line on
GPIO5**, or as I2C only. There is **no free UART** — GPIO16/17 (RX/TX) are both consumed by the
post limits and the head bridge.

### 3.4 Power rails and spare current

From `docs/electrical.md` "Architecture and power":

| Rail | Source | Rating | Feeds |
| --- | --- | --- | --- |
| 5V_LOGIC | Adafruit 4739 (U6) | **1.2 A** | Feather, sensors, MAX98357A audio |
| P1-P5 | five Adafruit 1385 UBECs | 5 V / 3 A each | left drive, right drive, rear drive, steering+buffer, head |
| P6 | Pololu S13V25F12 (4984) | 12 V | actuator only |
| Battery | Bioenno BLF-1206A | 12 V 6 Ah 72 Wh, 12 A continuous | — |

Sizing: "At 5.25 V, seven channels plus 2 A steering and 1.2 A logic give 60.9 W. With 85
percent assumed converter efficiency and 11.2 V pack voltage, that is 6.40 A input." Main fuse
7.5 A. Estimated runtime 2.0 – 3.3 h at 15 – 25 W average and 70 percent usable energy.

**Spare current on the 1.2 A logic rail is not specified in the repo** — the document allots
the whole 1.2 A to logic in its sizing arithmetic but never states what the Feather plus
ADS1115 plus INA219 plus amplifier actually consume. The 3.3 V supply comes from the Feather's
onboard regulator; its capacity is **not specified in the repo** (the HUZZAH32's regulator is
an AP2112K-3.3, 600 mA — **inferred**, from Adafruit's pinout guide, not from this repo).

A hard rule from `docs/electrical.md`: "Do not power any motor or servo through the Feather.
The Feather BAT/JST socket stays empty."

### 3.5 Where a sensor can physically go

| Candidate location | World Z | Assessment |
| --- | --- | --- |
| Feet (outer, X ±165) | 0 – 130 | The only structure at floor level. Each outer foot is a 131 x 197 x 130 mm PETG shell already holding two motors and four wheels. A forward-facing sensor in a foot points along the floor but is **not on the robot's yaw centre**, and the rear foot moves 119 mm fore-aft with posture. |
| Body skin, lower band | 165 – 269.7 | 1.2 mm PETG cylinder, 259.25 mm diameter. The thinnest wall of the three projects — good for a radar panel. The surface relief is **cosmetic only**: `cad/exterior.scad` `body_panel_channels()` engraves closed-door perimeters and states "remaining wall >= 0.75 mm", so there is no existing through-cut to reuse. |
| Body skin, upper band | 269.7 – 454.3 | Same 1.2 mm skin. This is roughly eye height for a standing adult's torso but well above a cat. |
| Front centreline | any | The body is a clean cylinder with no functional openings. Every "radar eye", logic display and utility arm is **painted relief, not a working part** (`docs/mechanical.md`: "These details are actual mesh relief and paint guides. They are not functioning display lamps, utility arms or projectors."). |
| Dome | 456.8 – 609.6 | **Impossible.** `docs/electrical.md`, first paragraph: "No wire crosses the rotating dome joint. Its display details are painted relief." The dome sits on two 608 bearings and is turned by a friction wheel with no encoder. |
| Head floor / electronics bay | 413 – 415 | 2 mm 6061 plate. Routine electronics access is through the removable dome and top plate, so this is the serviceable bay — but it is under the dome, not looking out. |

The single most useful mechanical fact: on `r2d2` the **body skin is 1.2 mm PETG**, and cutting
a fresh aperture in it does not disturb a validated mechanism, unlike the Dalek's bumper.

### 3.6 Existing sensors in the BOM

Repo-verified, `bom/electronics.csv`:

| Ref | Part | What it senses |
| --- | --- | --- |
| U9 | Adafruit ADS1115 (1085), `0x48` | Actuator potentiometer position on AIN0 |
| U10 | Adafruit INA219 (904), `0x40` | Actuator branch current on the 12 V rail |
| LS_EXT / LS_RET | Omron SS-01GL gold-contact | Hard end limits on the post, wired as a hardware gate |
| — | resistive dividers | Pack voltage (GPIO34), RUN-rail presence (GPIO39) |
| — | Actuonix P16 internal pot | Actuator stroke |

No obstacle, presence or ranging sensor of any kind. No IMU. No encoder on any wheel or on the
dome.

### 3.7 Uncommitted work in the worktree

`git status` shows `r2d2/cad/exterior.scad`, `r2d2/cad/r2d2.scad` and six STLs modified, plus
new untracked files `r2d2/cad/printed-frame.scad`, `r2d2/docs/printed-frame-research.md` and
eleven new STLs (`frame_chassis`, `frame_lower`, `frame_upper`, `printed_leg_core`,
`shoulder_carrier`, `post_mount`, and others). `docs/printed-frame-research.md` is dated
2026-09-12 and describes a **revision D** that would replace the cut-metal frame with printed
structure plus optional MISUMI HFS5-2020 extrusion. It is labelled "source research, not a
released joint design". Any sensor recommendation keyed to revision C's metal chassis may not
survive revision D.

---

## 4. `fable-r2d2` — 317 mm body, 13.3 kg, and the only project with real electrical headroom

Sources: `C:/dev/robots/fable-r2d2/cad/params.scad`, `C:/dev/robots/fable-r2d2/docs/mechanical.md`,
`C:/dev/robots/fable-r2d2/docs/electrical.md`, `C:/dev/robots/fable-r2d2/docs/firmware.md`,
`C:/dev/robots/fable-r2d2/firmware/kb2040/README.md`,
`C:/dev/robots/fable-r2d2/electronics/calculations.json`,
`C:/dev/robots/fable-r2d2/bom/electronics.csv`, `C:/dev/robots/fable-r2d2/cad/validation.json`.

`cad/params.scad` is the single source of dimensions and is unusually complete. Everything in
this section is repo-verified from it unless marked otherwise.

### 4.1 Footprint, height and stance

The model is scaled **0.68386** from the club-standard 463.55 mm R2-D2. The body diameter is
set by the printer, not by the scale: `body_od` = 317.0 mm = `env_y` (the H2D's 320 mm Y axis
minus a 3 mm buffer).

| Item | Parameter | Value |
| --- | --- | --- |
| Body outside diameter | `body_od` | 317.0 mm |
| Body height, skirt bottom to top edge | `body_height` | 381.1 mm |
| Skirt height | `skirt_h` | 41.3 mm |
| Skirt bottom radius | `skirt_bottom_r` | 116.6 mm |
| Skirt front/rear flats | `skirt_flat_y` | Y = ±94.85 mm |
| Body skin wall | `body_wall` | **3.6 mm** (5 x 0.42 mm perimeters plus infill) |
| Dome outside diameter | `dome_od` | 317.0 mm |
| Dome height, band bottom to crown | `dome_height` | 196.8 mm |
| Dome wall | `dome_wall` | 3.0 mm (shell 3.2 mm in `cad/dome.scad`) |
| Dome gap above body top edge | `dome_gap` | 1.9 mm |
| Body top plate thickness / Z | `body_top_plate_t` / `body_top_plate_z` | 5 mm at 375.1 |
| Foot track, centre to centre | `leg_track` | 363.4 mm |
| Shell bottom edge above floor | `foot_clear` | 12 mm |
| Outer foot, bottom footprint | `foot_outer_l_bot` x `foot_outer_w_bot` | 243.2 x 123.3 mm |
| Centre foot, bottom footprint | `foot_center_l_bot` x `foot_center_w_bot` | 180.2 x 123.3 mm |

**Three-leg driving stance** (the stance it actually moves in; body tilted back 18 degrees,
outer legs leaning 18 degrees):

| Measure | Value |
| --- | --- |
| Shoulder axis above floor | 463.0 mm |
| **Skirt bottom above floor** | **164.5 mm** |
| Skirt bottom forward of shoulder axis | 97.0 mm |
| Outer foot centre forward of shoulder axis | 116.2 mm |
| Centre foot centre forward of shoulder axis | 77.0 mm |
| Support polygon, fore-aft | 32.0 to 161.2 mm forward of the shoulder axis |
| **Dome crown above floor** | **715.9 mm** |

**Two-leg display stance**: shoulder axis 481.4 mm, dome crown 747.3 mm. The robot **cannot
drive in the two-leg stance** — it has no balance system.

Overall width, repo-derived: leg centre planes at `leg_offset_x` = ±181.7 mm, each foot 123.3
mm wide, so the outside edges are at ±243.35 mm — **486.7 mm overall**.

An important caveat the repo flags itself: in the built geometry the centre foot **trails** the
outer feet by 39.2 mm, where `research/loads.md` assumed it led them by 290 mm. Every
centre-of-gravity, foot-share and tip-back number derived from that section is marked "not
valid for this geometry and must be re-run". Tip-back is the governing instability
(1.55 m/s² and a 9.0 degree static tilt in the old geometry) and is currently **unknown**.

### 4.2 Mass, drive and speed

- **13.273 kg nominal** (range 11.610 – 14.960 kg), repo-verified from the mass table in
  `docs/mechanical.md` section 5.1. The document notes this is above the 8-11 kg originally
  expected and that "The cause is wall thickness on a 317 mm cylinder."
- Battery alone is **2,260 g** (Power-Sonic PS-1270 F2 SLA, 151 x 65 x 94 mm, ~2 kg).
- Drive: six Adafruit 3777 TT motors, two per foot, four wheels per foot, 63 mm wheels, off two
  independent 6 V rails through four DRV8833 boards at the stock 1 A limit. A seventh 3777 is
  the head friction drive.
- **Speed is computed here, unlike the other two projects** (`docs/mechanical.md` section 5.2):

| Case | Rolling resistance | Per-motor current | **Speed** | Margin at the 1 A limit |
| --- | --- | --- | --- | --- |
| 13.3 kg, Crr 0.02 | 2.60 N | 0.385 A | **0.54 m/s** | 3.6x |
| 13.3 kg, Crr 0.04 | 5.21 N | 0.620 A | **0.43 m/s** | 1.8x |
| 11.0 kg, Crr 0.02 | 2.16 N | 0.345 A | 0.56 m/s | 4.4x |
| 11.0 kg, Crr 0.04 | 4.31 N | 0.540 A | 0.47 m/s | 2.2x |

- Grade capability 2-3 degrees at the 1 A limit. Carpet, thresholds above about 5 mm, and ramps
  are **outside the envelope**.
- **Turning is the limit, not straight driving.** Spin-in-place needs 4.1 – 9.3 N per side
  against 4.7 N available. The default command is an arc of **0.5 m radius or more**.
- Drive acceleration is 0.5 – 0.9 m/s². The stated hazard is that "a 20 mm bump at speed can"
  tip it back.

At 0.43 – 0.56 m/s with 13.3 kg of momentum and coast-only stopping (SLP low is coast, not a
brake), this is by far the most demanding stopping case of the three robots.

### 4.3 Controllers, GPIO and I2C map

Two processors. This is the only project with real spare I/O, and it is all on the Pi side.

**Adafruit KB2040 (RP2040), product 5302, CircuitPython 9** — motors and pixels. Repo-verified
from `firmware/kb2040/README.md`:

| Function | Pin | GP |
| --- | --- | --- |
| Driver 1 (left foot) AIN1 / AIN2 | D2 / D3 | 2 / 3 |
| Driver 1 BIN1 / BIN2 | D4 / D5 | 4 / 5 |
| Driver 2 (right foot) AIN1 / AIN2 | D6 / D7 | 6 / 7 |
| Driver 2 BIN1 / BIN2 | D8 / D9 | 8 / 9 |
| Driver 3 (centre foot) AIN1 | D10 | 10 |
| Driver 4 (head) AIN1 / AIN2 | A0 / A1 | 26 / 27 |
| All four DRV8833 SLP | D1 | 1 |
| NeoPixel data, 17 pixels | A2 | 28 |
| Dome index sensor, active low | A3 | 29 |
| **Spare** | **D0** | **0** |

`docs/firmware.md` states the limitation directly: "No KB2040 pin is free for this anyway. Its
only ADC pins are A0-A3 (GP26-GP29) ... The one spare pin, D0/GP0, has no ADC on the RP2040."

**But** — `board.SDA` and `board.SCL` are GP12 and GP13 on this board, and the README records
that "The STEMMA QT connector therefore stays free while D2 and D3 drive a motor." The KB2040's
**entire I2C bus is unused and unpopulated**. That is the single largest free resource across
all three projects.

**Raspberry Pi 4 Model B, 4 GB** — server, displays, audio, battery. Used Pi pins
(repo-verified, `docs/electrical.md` section 6 and `docs/firmware.md`):

| Function | Pi GPIO | Header pin |
| --- | --- | --- |
| I2C-1 SDA / SCL | 2 / 3 | 3 / 5 |
| SPI0 MOSI / SCLK | 10 / 11 | 19 / 23 |
| TFT CS (CE0) | 8 | 24 |
| TFT DC | 25 | 22 |
| TFT RST | 24 | 18 |
| TFT backlight (nominal; unconnected, R1 ties LITE to 5 V) | 18 | 12 |

Everything else on the 40-pin header is free (**inferred** from the standard Pi 4 header
against that list): GPIO4, 5, 6, 7, 9, 12, 13, 14, 15, 16, 17, 19, 20, 21, 22, 23, 26, 27.
That includes the primary UART on GPIO14/15 and a second SPI chip select on GPIO7 (CE1). Three
of the Pi's four USB ports are also free — only one is used, for the KB2040 link (cable J11).

**I2C address map** — Pi I2C-1 (`/dev/i2c-1`), repo-verified:

| Address | Device |
| --- | --- |
| `0x70` | HT16K33, front logic upper window |
| `0x71` | HT16K33, front logic lower window |
| `0x72` | HT16K33, rear logic left |
| `0x73` | HT16K33, rear logic right |
| `0x48` | ADS1115, battery divider on A0 (optional) |

Free on the Pi bus: `0x29`, `0x30`, `0x40`, `0x52`, `0x68`, `0x74`-`0x77`. A second ADS1115 at
its `0x48` default **would collide**; a VL53-family part at `0x29` would not. On the KB2040
STEMMA QT bus, **every address is free**.

Radar eye (Adafruit 6178, GC9A01A 240x240) is on **SPI0 CE0** through the slip ring, not I2C.

### 4.4 Power rails and spare current

From `docs/electrical.md` section 1 and `electronics/calculations.json`:

| Rail | Regulator | Rating | Design load | Spare (repo-derived) |
| --- | --- | --- | --- | --- |
| 5 V | Pololu D36V50F5 (4091) | **5.5 A at 36 V in** | **1.40 A** (Pi 0.60, matrices 0.15, NeoPixels 0.30 avg, TFT 0.10, KB2040 0.05, amp 0.20) | **~4.1 A** |
| 6 V rail A | Pololu D36V50F6 (4092) | 5.5 A at 36 V in | 4.0 A (four motors at the 1 A limit) | 1.5 A |
| 6 V rail B | Pololu D36V50F6 (4092) | 5.5 A at 36 V in | 3.0 A (three motors) | 2.5 A |
| 12 V bus | PS-1270 SLA | 15 A fuse F1 | 4.537 A worst case | — |
| Dome 5 V via slip ring | F6 2 A fuse | 2 A | 1.62 A worst case, 1.01 A at firmware brightness 0.4 | ~0.4 A |

The 5 V rail's input fuse F3 is 3 A on the 12 V side; at 90 percent converter efficiency that
is about 6.4 A at 5 V, so **the regulator, not the fuse, is the binding limit**, and roughly
**4.1 A of 5 V headroom exists**. This is more than an order of magnitude more headroom than
the Dalek's 0.30 A.

**The same measurement condition applies here as on the Dalek.** Pololu's footnote for both the
D36V50F5 (4091) and the D36V50F6 (4092) reads "Typical max continuous output current at 36 V
in. Actual achievable continuous output current is a function of input voltage and is limited by
thermal dissipation", against a family range of 3.5 A to 8 A. This robot feeds those regulators
from a 12 V PS-1270 SLA, so **the 5.5 A is not the rating at the real operating point** and the
4.1 A / 1.5 A / 2.5 A spares above inherit that uncertainty. The conclusion that fable-r2d2 has
by far the most 5 V headroom of the three survives — its 1.40 A design load is only a quarter of
even the pessimistic 3.5 A end of the family range — but the exact spare figure does not.
The P6 12 V supply is a Pololu S13V25F12 (4984), whose page gives "Typical maximum continuous
output current: 0.5 A to 3 A, depending on input voltage"; the repo's flat "12 V" entry omits
that too.

Runtime to 50 percent depth of discharge (3.35 Ah usable): idle 5.2 h, mixed 2.5 h, continuous
driving 1.6 h, worst case 0.7 h.

Three hard rules from `docs/electrical.md` that a sensor must not break:
1. "**Never feed a DRV8833 from the 12 V bus.** Its maximum motor supply is 10.8 V."
2. "**The KB2040 is powered only by the Pi's USB port.** Do not also connect its RAW pin to
   the 5 V rail."
3. "**The Pi is powered only through its USB-C input** (J12)." The J12 run must stay under
   250 mm and must not be daisy-chained.

### 4.5 Where a sensor can physically go

| Candidate location | Height above floor (driving stance) | Assessment |
| --- | --- | --- |
| Outer feet | 12 – 99 mm (foot shell) | 3.2 mm PETG (`foot_wall`), 243.2 x 123.3 mm sole. Already packed with two motors and four wheels each, plus decorative battery boxes 119.4 x 53.5 x 84.7 mm. |
| Centre foot | 12 – 99 mm | Castering, ±60 degree swivel limit, 20 mm trail. A sensor here would swing with the caster. |
| **Body skirt** | 164.5 – 205.8 mm | 41.3 mm tall, bottom radius 116.6 mm with **flats at Y ±94.85** front and rear. Twelve ribs at 8.7 mm. The flats are naturally flat panel real estate. |
| **Body skin, lower ring** | ~205.8 – 341 mm | 3.6 mm PETG, 317 mm diameter. Carries J1 charge jack and the SW1 rocker (36.83 x 21.08 mm cutout) in the **rear** lower band. The front is clear. |
| Body skin, upper ring | ~341 – 546 mm | 3.6 mm PETG, 246 mm tall. Interrupted by two M12 shoulder pads 116 mm across at ±body_r, and by the seam flange. |
| Body top plate | 375.1 (body frame) | 5 mm plate, central opening r = 50 mm, head-drive slot 36 x 60 mm, lazy-susan holes on a 156.9 mm square. Under the dome. |
| **Dome** | 546 – 715.9 mm | Real through-cuts exist, but **all are occupied**: eye lens bore 52.1 mm (GC9A01A TFT), three holoprojector openings 44.1 mm (8 mm NeoPixels), PSI apertures 27.0 and 34.0 mm (NeoPixel Jewels), front logic windows 30 x 21 mm x2, rear logic window 44 x 21 mm. |

**The dome wiring budget is full.** The Adafruit 1195 slip ring has 12 wires at 2 A each, and
`docs/electrical.md` section 6 assigns **all twelve**: two 5 V, two ground, one NeoPixel data,
SDA, SCL, SPI MOSI, SPI SCLK, TFT CS, TFT DC, TFT RST. A dome-mounted sensor needs either a
larger slip ring or a sensor that shares the existing I2C pair (SDA/SCL, slip-ring wires 6 and
7) with an address that does not collide with `0x70`-`0x73`. Ring maximum is 300 RPM.

**The one genuinely open door**: `cad/body.scad` is a **3-line stub**, and `cad/validation.json`
and `bom/printed-parts.csv` both record `body_upper` and `body_lower` as
`"pass_check": false, "error": "missing STL"`. `docs/mechanical.md` says "`cad/body.scad` is
being authored in parallel". **The two body rings have not been designed yet**, so an aperture,
a recess, a flat mounting boss or a radar-transparent thin panel can be designed into them at
zero rework cost. This is the only place across all three projects where that is true.

One radar note, marked **inferred** rather than repo-verified: the 3.6 mm body wall is the
thickest of the three robots. At 60 GHz the free-space wavelength is 5.0 mm, so in PETG
(relative permittivity roughly 3.0, hence about 2.9 mm in-material wavelength) a 3.6 mm wall is
neither a half-wavelength nor a full one, which is the worst case for transmission loss. A
locally thinned panel would be a design choice to make **now**, while `body.scad` is still
being written. This is engineering guidance, not a repo fact, and the actual permittivity of
Bambu PETG Basic is not published in any file here.

### 4.6 Existing sensors in the BOM

Repo-verified, `bom/electronics.csv`:

| Ref | Part | What it senses | Status |
| --- | --- | --- | --- |
| U9 | Adafruit ADS1115 (1085), `0x48` on Pi I2C-1 | 12 V pack voltage through a 100 k / 15 k divider | Optional per `docs/firmware.md` |
| SQ1 | Allegro US5881LUA Hall switch (Adafruit 158) | Dome index / home position, open drain to KB2040 A3 | **Optional** |

No obstacle, presence or ranging sensor. No IMU. No wheel encoder. The head has an index
sensor but no continuous angle measurement.

---

## 5. What this means for sensor selection, per project

These are constraints extracted from the repo, not recommendations — the recommendation is
another lane's job.

**`dalek`** is the closest physical match to the 350 mm brief (300 mm circle) and the easiest
robot to ring with sensors, because it is the only one with a continuous 360-degree skirt at
1.8 mm PLA. It is also the **hardest electrically**: no free GPIO, one I2C bus with one device
on it, and **0.30 A of spare 5 V**. Anything chosen here must be I2C, must draw well under
300 mA, and must not need an interrupt pin. The base bumper is off limits by a released
validation rule; the lower skirt between two of the twelve vertical seams is the realistic
panel. The head cannot be used at all.

**`r2d2`** has the thinnest shell (1.2 mm PETG) and one free pin (GPIO5), but it is **47 g from
its own 9 kg ceiling** and has no skirt at floor level — the body starts 130 mm up and the rear
foot translates 119 mm fore-aft during posture changes, so a floor-level 360-degree ring is
mechanically awkward. Its logic rail is rated 1.2 A but the actual headroom is not published.
The dome is unusable. Revision D work in the worktree may change the frame under any mount.

**`fable-r2d2`** is the heaviest and fastest (13.3 kg at 0.43-0.56 m/s), which makes it the one
that most needs the sensing, and it is the only one with the resources to do it well: about
**4.1 A of spare 5 V**, an **entirely unused KB2040 I2C bus**, eighteen free Pi GPIOs including
a free UART on GPIO14/15, three free USB ports, and **two body rings that have not been
designed yet**. Its constraints are the full 12-wire slip ring (no new dome wiring), the 3.6 mm
wall thickness, and the fact that its centre-of-gravity and tip-back numbers are currently
invalid and must be re-run before any mass is added high up.

---

## 6. Open questions the repo cannot answer

1. Does the LilyGO T-Display break out GPIO37/38? If it does, `dalek` gains two input-only
   pins. `docs/firmware.md` does not list them.
2. What does the `r2d2` 5 V logic rail actually draw? The 1.2 A figure is the rail's rating,
   used as the allotment in the 60.9 W sizing; the real consumption of the Feather plus
   ADS1115 plus INA219 plus MAX98357A is never stated.
3. What is the assembled mass of `dalek`? Only the 2.429 kg plastic prediction exists.
4. What are `fable-r2d2`'s corrected foot-share and tip-back figures for the built
   (centre-foot-trailing) geometry? `docs/mechanical.md` marks both **unknown**.
5. Will `r2d2` revision D (`cad/printed-frame.scad`, `docs/printed-frame-research.md`, both
   uncommitted) replace the cut-metal chassis, and does the head floor survive it?
6. What is the dielectric constant and loss tangent of Bambu PETG Basic at 24 and 60 GHz? Not
   published in any file here, and it governs whether any of these shells can hide a radar.
