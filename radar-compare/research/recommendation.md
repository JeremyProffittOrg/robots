# Engineering Recommendation — Perimeter Detection for a 350 mm Mobile Robot

**Written:** 2026-09-12. **Synthesised from:** all 16 lane documents in `C:/dev/robots/radar-compare/research/`.
**Platform:** 350 mm square **or** 350 mm round footprint, 600–1200 mm tall, 3.5–13.5 kg, indoor, humans and pets present.
**Prices:** USD list, as read by the source lanes on 2026-09-12. Every price is marked **[V]** (vendor-page-verified in a
source lane) or **[U]** (not priced in any source lane — budgetary, must be confirmed before ordering).

---

## 0. Answer first

| | MINIMUM VIABLE | RECOMMENDED | MAXIMUM |
|---|---|---|---|
| Name | `collision-ring` | `collision-ring + animate-layer` | `full-classification-stack` |
| ToF modules | **18** (12 ring + 6 cliff) | **19** (12 ring + 6 cliff + 1 scanning dTOF) | **24** (16 ring + 6 cliff + 1 CNH head + 1 scanning dTOF) |
| People sensors | **0** | **8** (thermal arrays) | **10** (6 thermal + 4 camera) |
| Hardware cost | **$455** | **$909** | **$1,440** |
| Average current @ 5 V | **724 mA (3.6 W)** | **999 mA (5.0 W)** | **3.8 A (19 W)** |
| Peak current @ 5 V | **1.61 A** | **1.95 A** | **5.2 A** |
| Answers "will I hit it?" | Yes, 360° | Yes, 360°, plus dark targets and sunbeams | Yes |
| Answers "is it alive?" | **No** | Yes, 360°, to ~2.4 m for a pet / ~5 m for a human | Yes, in darkness too |
| Answers "human or pet?" | **No** | Yes, to ~5 ft by fusion | Yes, labelled, to 10 ft |

**Three decisions that override everything else, and they are free:**

1. **Make the platform round.** A 350 mm square has a 494.975 mm diagonal and a 72.487 mm corner protrusion. Four 45°-FoV
   sensors on the face centres leave the corners **permanently** uncovered (`Ω = −45°`), and moving them to the corners is
   strictly worse (653 mm hole at the face midpoints vs 338 mm at the corners, at 120° FoV). If it must be square, put the
   sensors on the **face centres**, chamfer the corners at 45°, and treat the corners as mechanically protected.
2. **Cap speed at 0.5 m/s, and at 0.3 m/s in unmapped or occupied space.** A 15 kg robot at 1.0 m/s with a rigid shell
   delivers a mean **1500 N** into a shin against a 130 N ISO/TS 15066 transient limit. The same robot at 0.5 m/s with a
   50 mm compliant bumper delivers **38 N**. Speed is the cheapest safety component in the build.
3. **Classification never gates the stop.** You get **167–323 ms** between the warning-field edge and the protective-field
   edge for a moving target. Micro-Doppler gives 75 % at 250 ms of dwell; ST's own ToF people-counter uses a 2.1 s window;
   a thermal frame at 4 Hz is 250 ms on its own. Braking runs on raw geometry at frame rate; classification runs in
   parallel and only changes *behaviour after the stop*.

---

## 1. MINIMUM VIABLE RING — `collision-ring`

**What it is for:** requirement (a) only — do not collide with anything. It has no human channel and no pet channel, and
it is not honest to claim otherwise.

### 1.1 Bill of materials

| # | Part | Vendor / SKU | Qty | Unit | Ext | Mount |
|---|---|---|---|---|---|---|
| 1 | **VL53L8CX** 8×8 multizone dToF carrier with regulators | Pololu **#3419** | **12** | $24.95 **[V]** | **$299.40** | h = **200 mm**, boresight **horizontal (0° cant)**, **30.0° azimuth spacing** |
| 2 | **VL53L4CD** 1–1300 mm dToF carrier | Pololu **#3692** | **6** | $13.95 **[V]** | **$83.70** | h = **150 mm**, **23° down-cant**, 4 across the front arc (±20°, ±60°), 2 rear (150°, 210°) |
| 3 | PCA9548 8-channel I²C mux, STEMMA QT | Adafruit **#5626** | 2 | $6.95 **[V]** | $13.90 | base deck |
| 4 | Flexible Qwiic cable, 500 mm | SparkFun **PRT-17257** | 12 | $2.75 **[V]** | $33.00 | mux → ring |
| 5 | STEMMA QT cable, 100 mm | Adafruit **#4210** | 6 | $0.95 **[V]** | $5.70 | mux → cliff |
| 6 | RP2040 concentrator (Pico class) | — | 1 | ~$4 **[U]** | ~$4 | base deck |
| 7 | Compliant bumper: 20–50 mm closed-cell foam + 4 microswitches | — | 1 set | ~$15 **[U]** | ~$15 | leading 180° arc |
| | | | | **Verified** | **$435.70** | |
| | | | | **Total incl. [U]** | **≈ $455** | |

### 1.2 Geometry — why 12, why 200 mm, why level

The VL53L8CX's published **horizontal** FoV is **45.0°** (DS14161 Rev 2, Table 2 — 45° H / 45° V / 65° diagonal, measured
at 88 % white, 1 m, dark, 8×8, 14 % sharpener, 15 Hz). **The 65° is a diagonal and must never be used to size a ring.**

Ring closure requires `Φ > Δ`, i.e. `N_min = floor(360/Φ_h) + 1 = floor(360/45) + 1 = 9`. Eight sensors — the intuitive
"360 ÷ 45" answer — sets `Ω = 0`, which makes adjacent beam edges exactly parallel: **eight blind slots open to infinite
range.** The blind-wedge tip distance from the platform centre is

```
D_tip = r · [ cos(Δ/2) + sin(Δ/2) · cot(Ω/2) ]      Δ = 360/N,  Ω = Φ_h − Δ,  r = 175 mm
```

| N | Δ | Ω | D_tip from centre | Blind depth past skin | Largest sphere that fits in a seam |
|---|---|---|---|---|---|
| 8 | 45.0° | **0°** | **∞ — OPEN** | infinite | unbounded |
| 9 | 40.0° | 5° | 1535 mm | 1360 mm | huge |
| 10 | 36.0° | 9° | 853.6 mm | 678.6 mm | 232 mm |
| **12** | **30.0°** | **15°** | **513.1 mm** | **338.1 mm** | **79.4 mm** |
| 16 | 22.5° | 22.5° | 343.3 mm | 168.3 mm | 56.0 mm |

**12 is the minimum defensible count.** The residual blind region is twelve thin triangles, each with an 90.6 mm base on
the skin (the chord between adjacent apertures) tapering to a point at 513 mm. The largest object that can sit **entirely**
inside one is a **79.4 mm sphere**. A cat (minimum dimension ~150 mm), a human leg (110–150 mm), a shoe and a pet bowl all
span at least one sensor's cone. A **35 mm chair leg can hide** — that is what the compliant bumper is for, and it is a
deliberate, bounded, priced acceptance, not an oversight.

**Mount height 200 mm, level.** Vertical half-angle is 22.5°, so the visible height band is `200 ± 0.41421·d`:

| Range | 1 ft (305) | 3 ft (914) | 5 ft (1524) | 8 ft (2438) | 10 ft (3048) |
|---|---|---|---|---|---|
| Lowest height seen | **74 mm** | floor | floor | floor | floor |
| Highest height seen | 326 mm | 579 mm | 831 mm | 1210 mm | 1462 mm |

First floor strike is at **482.8 mm**, so the first half-metre is clean free-space measurement and everything beyond gives
a floor baseline in the bottom rows (anything returning *shorter* than the baseline is an obstacle; *longer* or invalid is
a cliff). At 200 mm the sensor is level with a cat's head, so a cat is **never below the beam at any range** — the failure
that kills the obvious "put the ring near the top where the wiring is easy" layout, where an `h = 800 mm`, 25°-vertical
ring **cannot see a cat anywhere inside 10 ft**.

**Cliff geometry: h = 150 mm, ψ = 23° down.** Look-ahead `L = h/tan ψ = 353 mm`, which satisfies the design rule
`L ≥ d_stop + 175 mm front overhang` at 0.5 m/s. Flat-floor slant range `R_f = 384 mm`; a 180 mm residential riser moves
it to **845 mm**. Threshold: `R > 550 mm OR target_status ≠ 5 ⇒ CLIFF`. ψ must stay **above ~20°** or the beam grazes
polished wood and tile at near-specular incidence and produces intermittent false cliffs. Note `ΔR/R_f = D/h` is
independent of ψ, so ψ only trades look-ahead against incidence angle.

### 1.3 Operating mode, timing and the number that closes the safety argument

Run the ring at **4×4 / 30 Hz**, target order **Closest** (the ULD default is *Strongest*, which reports the white wall
behind a dark obstacle), minimal output (distance + status + nb_target + motion), in **two optical groups** of six
alternating sensors so that no two overlapping cones integrate simultaneously.

```
T_total = T_revisit(66 ms) + T_integration(33 ms) + T_processing(10 ms) + T_actuation(50 ms) = 159 ms
```

Full-ring refresh is **66 ms**, inside the ≤88 ms requirement derived from "the robot must move no more than a quarter of
its own radius between revisits" at 0.5 m/s.

Required reliable detection range, for the worst case — a cat sprinting at the robot (4.5 m/s closing):

```
d_react = v_close · T_total + v² / 2a + margin  =  4.5 × 0.159 + 0.083 + 0.100  =  899 mm
```

**This single number decides the part.** VL53L8CX at 4×4 / 30 Hz, 17 % grey target, 5 kLux ambient (DS14161 Table 16):
**1650 mm inner zone, 1550 mm corner zone.** The corner zones are exactly where the ring's seams are, and even there the
margin is **+72 %**. For a static-object protective field the requirement is only 517 mm, and for a human walking in at
1.6 m/s it is 771 mm — both comfortably inside 1550 mm.

### 1.4 Power

| Item | Qty | Per unit @ 5 V | Duty | Average |
|---|---|---|---|---|
| VL53L8CX active ranging (AVDD 43 mA + CORE_1V8 50 mA) | 12 | 93 mA | 50 % (2 groups) | **582 mA** |
| VL53L4CD cliff, continuous 100 Hz | 6 | 22 mA | 100 % | **132 mA** |
| PCA9548 ×2 + RP2040 | — | — | — | **~10 mA** |
| **Total average** | | | | **724 mA = 3.6 W** |
| **Peak** (all sensors ranging at boot, +10 mA/rail peak adder) | | | | **1.61 A** |

> **The carriers waste more than half of that.** Chip-level power is 215 mW typical per VL53L8CX; through the linear
> regulators on a 5 V-fed carrier it becomes 465 mW. On a production custom flex with shared 3.3 V and 1.8 V bucks the
> ring falls to **~310 mA average**. Cut the power-LED jumper on every breakout — 12 LEDs is 36 mA / 0.18 W.

### 1.5 Bus and integration

- **All VL53 parts boot at 0x29 and the address change is volatile.** Use the **mux** for addressing (it also divides bus
  capacitance by the branch count: 116 pF muxed vs **524 pF** for eight sensors all on one bus, against a 366 pF ceiling
  at 400 kHz) and keep **XSHUT wired to a GPIO per sensor** for per-node hardware recovery. Never write more than one
  channel bit to the mux at a time — the register is a bitmask, not an index.
- Run the muxed bus at **400 kHz**: 116 pF is well inside the 366 pF ceiling, and the 84 kB firmware upload each
  VL53L8CX needs at every power-up costs ~1.9 s per sensor at 400 kHz — **budget a ~23 s I²C boot for the ring**. If the
  carrier exposes the VL53L8CX's 20 MHz SPI, use it and the boot collapses to under a second.
- Every ToF sensor needs its **own clear aperture** — a translucent printed wall in front of the emitter is worse than an
  opaque one, because it diffuses emitted photons straight back into the receiver. Aperture at 1.0 mm standoff:
  **Ø1.50 mm emitter, Ø1.80 mm receiver**, or one 4.65 × 1.80 mm oval, with a **printed septum between Tx and Rx**. Keep
  the air gap ≤0.5 mm or fit a gasket, and run the per-unit crosstalk calibration with the final shell fitted.
- Twelve sensors at 30° spacing maps **exactly** onto `dalek`'s twelve vertical skirt seams.

### 1.6 What this tier deliberately does not buy

No human channel. No pet channel. No animate/inanimate channel. Blind to glass and to mirrors at every range. Blind to a
target in a sunbeam (200 kcps/SPAD ≈ 100 kLux is outside every published ST table). Blind to anything below 74 mm tall at
1 ft — cables, socks, a flat toy — which the bumper catches by contact.

---

## 2. RECOMMENDED BUILD — `collision-ring + animate-layer`

**What it adds:** requirement (b) humans and (c) pets, 360°, plus the two failure modes that would otherwise put the robot
on the floor or on the cat — dark targets in a lit room, and glass.

### 2.1 Bill of materials — additions to the minimum tier

| # | Part | Vendor / SKU | Qty | Unit | Ext | Mount |
|---|---|---|---|---|---|---|
| 8 | **Slamtec RPLIDAR C1** 360° dTOF scanner | DFRobot (Slamtec C1) | **1** | $69.00 **[V]** | **$69.00** | scan plane at **100 mm**, at the rotational centre |
| 9 | **Panasonic AMG8833** 8×8 thermal array, STEMMA QT | Adafruit **#3538** | **8** | $44.95 **[V]** | **$359.60** | h = **250 mm**, **level (0° tilt)**, **45.0° azimuth spacing** |
| 10 | RCWL-1601 ultrasonic ranger, 3 V/5 V | Adafruit **#4007** | 2 | $3.95 **[V]** | $7.90 | h = 250 mm, forward ±30° |
| 11 | PCA9548 8-channel I²C mux (3rd) | Adafruit **#5626** | 1 | $6.95 **[V]** | $6.95 | base deck |
| 12 | STEMMA QT cable, 300 mm | Adafruit **#4210** | 8 | $1.25 **[V]** | $10.00 | mux → thermal ring |
| | **Addition subtotal** | | | | **$453.45** | |
| | **TIER TOTAL** | | | | **≈ $909** | |

### 2.2 Why these three additions and not others

**RPLIDAR C1, scan plane at 100 mm — $69.** This is the highest value-per-dollar part in the whole study. It covers the
ToF ring's two structural weaknesses with one cable:

- **Dark targets.** C1 is specified **0.05–12 m at 70 % reflectivity and 0.05–6 m at 10 % reflectivity**. A black cat on a
  dark carpet is a 10 %-class target; the ToF ring loses it past 1.55 m in a lit room, the C1 holds it to **6 m**.
- **Ambient light.** C1 is rated **40 000 lux**. The VL53L8CX is characterised at 0 and 5 kLux only, and a sunlit patch of
  floor (≈100 kLux) reads as *empty space* — a wall of status-1 "signal rate too low" zones, not noisy numbers.
- **A lying cat.** A plane at 100 mm (±1.5° flatness, so ±13 mm at 1 m) intersects a cat lying on its side at 120 mm. No
  fixed ring at 200 mm does.
- **A static background map.** 5 kHz sample rate at 0.72° gives 500 points per revolution — enough to scan-match. Once you
  have a map, *anything that does not fit it is dynamic*, and "dynamic" is the strongest animate cue available without a
  camera. A ToF ring has far too few points ever to do this.

*Runner-up rejected:* **RPLIDAR A1 (Adafruit #4010, $99.95).** It is triangulation, not dTOF; its own datasheet says
"without direct sunlight exposure"; its range spec is qualified only "White objects" with **no** low-reflectance figure
published; it is 170 g against the C1's 110 g, 5.5 Hz against 10 Hz, and 0.15 m minimum range against 0.05 m. On a 350 mm
chassis the A1's blind radius nearly reaches the skin. It costs $31 more to be worse on every axis that matters here.

**Eight AMG8833 at 250 mm, level — $359.60.** Thermal is the **only** modality that separates animate from inanimate, and
it is the only one that sees a *motionless* target: a sleeping cat is invisible to MTI radar and invisible to PIR, and
visible to thermal. Geometry at h = 250 mm with a 60° × 60° array:

- Floor first enters the frame at **433 mm**.
- The top of a 200 mm cat enters the beam at **87 mm** from the skin — the animal is in frame essentially always.
- A standing adult's head stays in frame out to **2.51 m**; beyond that the torso stays.
- Ring closure: `N_min = floor(360/60) + 1 = 7`. Eight gives `Ω = 15°` and `D_tip = 670 mm`, with the largest hideable
  sphere at **117.5 mm** — smaller than a cat in any dimension. Seven would leave `D_tip = 1171 mm`; six is `Ω = 0` and
  never closes.

*Runner-up rejected:* **STHS34PF80 (Adafruit #6426, $14.95, 5 units = $74.75).** It is a genuinely good part — 10 µA, no
Fresnel lens needed, holds a *static* human, embedded presence/motion algorithms — but it has exactly **one sensing
element**. It reports "something warm is somewhere in an 80° cone." No bearing, no size, no shape, no contribution to
human-vs-pet. Keep it in mind only as a parked-robot wake-up layer.

*Also rejected:* **PIR of any kind, including "pet-immune" PIR.** Pet immunity is a purely geometric trick — the lens's
lowest beam is cut away and the unit is mounted at **2.2–2.75 m**. At 1.0 m on a robot the elevation separation between
"cat at 3 m" and "human knees at 3 m" collapses, and the human's torso and head are now *above* a downward-fanning lens.
A pet-immune PIR on a low robot can end up seeing the pet and missing the person — the exact inversion of its purpose.
Worse, PIR responds to the *rate of change* of flux, so on a driving robot every scene "moves" and the output is a random
number generator.

**Two RCWL-1601 ultrasonic, forward — $7.90.** Glass and mirrors are the one target class the **entire optical stack**
fails on: a ToF sensor ranges to the pane, a lidar gets a dropout or a phantom room, a thermal array sees room-temperature
glass. Ultrasonic sees glass reliably. Constrain it hard: warning field only, never in the protective-stop path (a 49 ms
cycle and mutual crosstalk make an 8-sensor sweep 264 ms), and never as the human detector (soft targets absorb 40 kHz;
HC-SR04-class reliability on a person past 1 m is below 50 %).

### 2.3 Fusion logic

Two rings, both body-fixed, extrinsically calibrated once so that a bearing in one is a bearing in the other. Everything
below is a starting point to be calibrated in situ.

```
# --- per frame ---
TOF ring (12 × VL53L8CX @ 200 mm, 4×4/30 Hz):
    for each zone with target_status == 5:
        p        = to_3d(sensor_azimuth, zone_azimuth, zone_elevation, distance_mm)
        h_abs    = height_above_calibrated_floor_plane(p)
    cluster by (azimuth, range) adjacency
    per cluster: bearing, r, h_top, h_bot, angular_width, jitter(1 s stddev),
                 planar(best-fit plane residual < 15 mm), motion(max per-zone motion indicator)

LIDAR (RPLIDAR C1 @ 100 mm, 10 Hz):
    segment scan, cluster, track with a constant-velocity filter,
    subtract the static map -> per cluster: bearing, r, chord_width, world_velocity, is_new_vs_map

THERMAL ring (8 × AMG8833 @ 250 mm, 10 Hz):
    per pixel: residual = value - background_EMA(tau = 30 s)     # NEVER threshold absolute temperature
    blob-detect on residual -> per blob: bearing, dT_peak, pixel_count, aspect_ratio

# --- Tier 0: collision. Runs on geometry alone, at ring frame rate. No classifier in this path. ---
if min_range_in_swept_corridor < protective_field(v):        STOP
elif min_range_in_swept_corridor < warning_field(v):         SLOW to 0.3 m/s and announce

# --- Tier 1..4: classification. Runs in parallel, changes behaviour only AFTER the stop. ---
match clusters across modalities by bearing (±10°) and range (±150 mm):

if dT < 1.5 K and jitter < 8 mm and planar and world_velocity ~ 0:
    OBJECT            # box, wall, furniture, door frame

elif dT >= 2.0 K and (h_top > 900 mm or cluster touches the ring's top zone row) and width > 250 mm:
    HUMAN             # tall AND warm. This is the high-confidence rule.

elif dT >= 1.5 K and h_top < 450 mm and width < 600 mm and (jitter > 8 mm or motion > thresh):
    PET               # low AND warm AND non-rigid. Cat vs dog is NOT attempted.

elif dT >= 1.5 K:
    UNKNOWN_LIVING    # crouching adult, toddler, large dog, heater -> BEHAVE AS HUMAN

else:
    UNKNOWN_OBSTACLE  # stop anyway
```

Three rules embedded in that, each earned from the source lanes:

- **Height is the primary human/pet discriminator, not temperature and not breathing rate.** A resting beagle breathes at
  13–25 /min and a resting human at 12–20 /min: the distributions overlap almost completely, and `if rate > 20 then pet`
  will call a calm human a dog. Temperature says *alive*; height says *which*.
- **Never threshold on absolute temperature.** A long-coated dog's flank reads **28.1 °C** in a 21 °C room — a 6 K
  contrast that falls to 2 K in a warm room — while an AMG8833's absolute accuracy is **±2.5 °C** and its apparent
  temperature is mostly a range measurement in disguise (a cat at 3 m reads 2.5 K, a clothed human at 5 m reads 3.8 K;
  move either by a metre and the ordering flips). A per-pixel background EMA at ~30 s cancels warm-up drift, chassis
  self-heating and room ambient in one step.
- **The ambiguous class defaults to human.** A crouching adult, a toddler and a Great Dane all land in `UNKNOWN_LIVING`.
  Over-classifying as human is the safe failure.

### 2.4 Power

| Item | Average @ 5 V |
|---|---|
| Minimum tier (12 ring + 6 cliff + mux) | 724 mA |
| RPLIDAR C1 @ 10 Hz (reseller figure, **not datasheet-confirmed**) | 230 mA |
| 8 × AMG8833 normal mode, 4.5 mA each, LEDs cut | 36 mA |
| 2 × RCWL-1601 @ 2.2 mA | 4 mA |
| 3rd PCA9548 | 5 mA |
| **Total average** | **999 mA = 5.0 W** |
| **Peak** (ring boot + lidar spin-up) | **≈ 1.95 A** |

### 2.5 Mechanical constraints this tier imposes

- The lidar needs an **unobstructed 360° optical slot at 100 mm**, with no bracket, cable or handle crossing it, and
  110 g at the rotational centre.
- **Every thermal aperture must be an open hole or thin LDPE.** Ordinary glass, polycarbonate, acrylic and PET are all
  **opaque** at 8–14 µm. A visually clear cosmetic window silently zeroes the sensor.
- The AMG8833's optical-axis gap is **±5.6 °** typical — three quarters of a pixel of boresight error. Each unit needs its
  own extrinsic calibration before its frame can be fused into a panorama.

---

## 3. MAXIMUM BUILD — `full-classification-stack`

**What it adds:** labelled human / pet / object classification out to 10 ft, in light and in darkness, plus the tightest
ring closure buildable with stocked parts.

### 3.1 Bill of materials

| # | Part | Vendor / SKU | Qty | Unit | Ext | Mount |
|---|---|---|---|---|---|---|
| 1 | VL53L8CX carrier | Pololu **#3419** | **16** | $24.95 **[V]** | **$399.20** | h = 200 mm, level, **22.5° spacing** |
| 2 | VL53L4CD carrier (cliff) | Pololu **#3692** | 6 | $13.95 **[V]** | $83.70 | h = 150 mm, 23° down |
| 3 | **VL53L8CH** CNH histogram head | bare part on a carrier; **price not published in any source lane** | 1 | ~$35 **[U]** | ~$35 | **h = 900 mm**, forward, own I²C bus |
| 4 | **MLX90640-ESF-BAA** 32×24 thermal, 110° × 75° | Adafruit **#4469** **— OUT OF STOCK 2026-09-12**; source from Melexis / Waveshare / DigiKey | **6** | $74.95 **[V]** | **$449.70** | h = **250 mm**, level, **60° spacing** |
| 5 | Slamtec RPLIDAR C1 | DFRobot | 1 | $69.00 **[V]** | $69.00 | scan plane 100 mm |
| 6 | RCWL-1601 ultrasonic | Adafruit **#4007** | 2 | $3.95 **[V]** | $7.90 | h = 250 mm, forward |
| 7 | PCA9548 8-ch mux | Adafruit **#5626** | 4 | $6.95 **[V]** | $27.80 | base deck |
| 8 | Raspberry Pi 5 | — | 1 | $80 **[V]** | $80.00 | base deck |
| 9 | Hailo-8L AI Kit | — | 1 | $70 **[V]** | $70.00 | on the Pi 5 |
| 10 | Wide-FoV camera (≈120° H) | **not priced in any source lane** | **4** | ~$35 **[U]** | ~$140 | **h = 900–1000 mm**, **90° spacing**, level |
| 11 | RP2040 concentrator, cabling, bumper | — | — | ~$79 **[U]** | ~$79 | — |
| | **Verified subtotal** | | | | **$1,187.30** | |
| | **TIER TOTAL incl. [U]** | | | | **≈ $1,440** | |

### 3.2 Why each upgrade

**16 ToF instead of 12.** `D_tip = 343.3 mm` — 168 mm past the skin — and the largest sphere that can hide in a seam
falls from 79.4 mm to **56.0 mm**. This is the tightest closure that is worth buying: getting the tip inside the
247.5 mm corner radius of a 350 mm square would need **N = 27**, which is past the point where a ring of array modules is
the right architecture at all.

**Six MLX90640-110° instead of eight AMG8833.** Resolution, not field of view, is what classifies. The 32×24 array at
110° × 75° puts a cat at 3.1 × 3.4 px at 3 ft and 1.8 × 2.1 px at 5 ft, against the AMG8833's 1.9 × 1.5 px and 1.1 × 1.0 px.
Ring closure at N = 6: `Δ = 60°, Ω = 50°, D_tip = 339 mm`, largest hideable sphere **111.5 mm**. Geometry at h = 250 mm
level: floor from **326 mm**, cat top in beam from **65 mm**, adult head in frame to **1.89 m**.

> **Two hard constraints on this ring.** (i) **Bandwidth.** One MLX90640 frame is ~1668 bytes ≈ 42 ms of bus time at
> 400 kHz; six sensors on one bus is bandwidth-bound to roughly **1 Hz each**. Split them across at least two independent
> I²C peripherals, and accept that thermal is a **warning-field and classification** channel that must never appear in the
> protective-stop path (at 4 Hz the required separation distance is 1060 mm at 0.5 m/s — three times the ToF figure).
> (ii) **The subpage trap.** The programmed refresh rate applies per *subpage*; a complete frame arrives at **half** the
> programmed rate, and in the default chess pattern a fast target tears across the two half-frames.

**Four cameras + Pi 5 + Hailo-8L.** This is the only thing in the study that does the job the operator actually asked for.
**COCO contains `person`, `cat` and `dog` as separate classes**, so a stock YOLO/SSD detector does human-vs-pet-vs-object
out of the box with no custom dataset, no labelling and no radar signal processing. YOLOv8n on a Pi 5 + Hailo-8L runs at
**136.7 FPS** (batch 8) against ~7–8 FPS CPU-only. Four cameras at 120° H and 90° spacing gives `Ω = 30°` and
`D_tip = 586 mm` — adequate for a classification layer that is not in the stop path.

Three costs, stated plainly: (i) **a camera in a dark room returns nothing** — this is why the thermal ring stays; (ii)
the Pi 5 has **two CSI ports**, so two of the four cameras must be USB — confirm before ordering; (iii) **privacy** — run
the model on-device and emit only `{class, bbox, confidence}`. Never store or transmit frames. Write that constraint down
before any code.

**One VL53L8CH at 900 mm.** The CH is the CX with different firmware: pin-to-pin compatible, and it exposes the raw
per-zone **compact and normalised histogram** at **37.5 mm per bin**. That is the only feature in this study that
distinguishes *material and shape* rather than just range: a flat cardboard box face puts its whole return into 1–2 bins;
a curved, furry body ~250 mm deep spreads over ~7 bins with a long low fur tail; a pet in front of a wall shows two clearly
separated peaks in one zone that the processed "distance" output collapses into one number. At 900 mm the field ceiling is
1521 mm at 1.5 m range, so an adult torso is in frame and height-above-floor becomes a real measurement.
**Budget one, not several:** a 64-zone CNH frame is 6108 bytes = **56 ms of bus time at 1 MHz I²C**. Two CH sensors
saturate a 1 MHz bus at 15 Hz. Ten is impossible. Give it its own bus.

### 3.3 Power

| Item | Average @ 5 V |
|---|---|
| 16 × VL53L8CX, 4×4/30 Hz, 2 optical groups | 776 mA |
| 6 × VL53L4CD cliff | 132 mA |
| 1 × VL53L8CH, 8×8 CNH continuous | 93 mA |
| 6 × MLX90640 @ ≤23 mA | 138 mA |
| RPLIDAR C1 | 230 mA |
| 2 × ultrasonic + 4 × mux + RP2040 | 24 mA |
| **Sensor subtotal** | **1393 mA = 7.0 W** |
| Pi 5 + Hailo-8L + 4 cameras (**not published in any source lane — budgetary**) | ~2.4 A = 12 W |
| **Total average** | **≈ 3.8 A = 19 W** |
| **Peak** | **≈ 5.2 A** |

---

## 4. Capability tables — what each tier can and cannot detect at 1, 3, 5, 8 and 10 ft

All cells assume the **binding real-world condition**: an ordinary lit indoor room at **5 kLux**, with dark targets treated
as ST's **17 % grey** Munsell chart (footnoted in the VL53L5CX datasheet as "measured 13 % in IR at 940 nm" — black
leather, black velvet and matte-black ABS are *below* that). Where a result depends on light level or target reflectance,
the cell says so. `Y` = works, `~` = marginal, `N` = does not work.

### 4.1 TIER 1 — MINIMUM VIABLE (`collision-ring`)

| Target / capability | 1 ft (305 mm) | 3 ft (914 mm) | 5 ft (1524 mm) | 8 ft (2438 mm) | 10 ft (3048 mm) |
|---|---|---|---|---|---|
| Wall, box, door frame (88 % white) | **Y** ±10 mm | **Y** | **Y** | **Y** (limit 2850 mm = 9.3 ft) | **N** (beyond 9.3 ft in 5 kLux) |
| Dark obstacle, black jeans, black fur (17 %) | **Y** | **Y** | **~** (1650 mm inner / 1550 mm corner = 5.1–5.4 ft) | **N** | **N** |
| Chair leg, 35 mm | **Y** unless dead on a seam bisector (79 mm hide limit) | **Y** | **~** | **N** | **N** |
| Cat lying down, back at 120 mm | **Y** (band is 74–326 mm at 1 ft) | **Y** (floor in band beyond 483 mm) | **~** light coat only | **N** | **N** |
| Cat standing, 200–250 mm | **Y** | **Y** | **~** dark fur fails | **N** | **N** |
| Human, as an obstacle (legs) | **Y** | **Y** | **Y** | **~** light clothing only | **N** in 5 kLux |
| Zone resolution at 4×4 | 63 mm | 189 mm | 316 mm | 505 mm | 631 mm |
| Height band seen | 74–326 mm | 0–579 mm | 0–831 mm | 0–1210 mm | 0–1462 mm |
| Cliff / stair edge | **Y**, 353 mm look-ahead | n/a | n/a | n/a | n/a |
| Glass door, mirror | **N** | **N** | **N** | **N** | **N** |
| Target in a sunbeam (~100 kLux) | **N** | **N** | **N** | **N** | **N** |
| **Is it alive?** | **N** | **N** | **N** | **N** | **N** |
| **Human vs pet?** | **N** | **N** | **N** | **N** | **N** |

### 4.2 TIER 2 — RECOMMENDED (`collision-ring + animate-layer`)

| Target / capability | 1 ft | 3 ft | 5 ft | 8 ft | 10 ft |
|---|---|---|---|---|---|
| Wall, box, door frame | **Y** | **Y** | **Y** | **Y** | **Y** (C1: 12 m @ 70 %) |
| Dark obstacle (10–17 %) | **Y** | **Y** | **Y** | **Y** | **Y** (C1: 6 m = 19.7 ft @ 10 %) |
| Chair leg, 35 mm | **Y** (C1 ~10 returns) | **Y** (3.5) | **Y** (2.1) | **~** (1.3) | **~** (1.0 — a 2-point cluster filter deletes it) |
| Cat lying down, 120 mm | **Y** (C1 plane at 100 mm) | **Y** | **Y** | **Y** | **Y** |
| Cat standing | **Y** | **Y** | **Y** | **Y** | **Y** |
| Human present | **Y** | **Y** | **Y** | **Y** | **Y** |
| Target in a sunbeam | **Y** (C1 rated 40 000 lux) | **Y** | **Y** | **Y** | **Y** |
| Glass door / mirror | **Y** forward arc only (ultrasonic) | **Y** forward arc | **~** (specular dropout past ~2.5 m) | **N** | **N** |
| **Alive vs inanimate** | **Y** (cat 5.7 × 4.5 px) | **Y** (cat 1.9 × 1.5 px) | **Y** human; **~** cat (1 px) | **Y** human only | **~** human only (1.0 × 1.6 px) |
| **Sleeping cat vs backpack** | **Y** | **Y** | **~** | **N** | **N** |
| **Human vs pet** (ToF height + thermal ΔT) | **Y** | **Y** | **Y** | **~** human-vs-not only | **~** human-vs-not only |
| **Cat vs dog** | **N** | **N** | **N** | **N** | **N** |
| Static human, not moving | **Y** (thermal; ToF geometry) | **Y** | **Y** | **~** | **~** |
| In total darkness | **Y** (all three channels) | **Y** | **Y** | **Y** | **Y** |

### 4.3 TIER 3 — MAXIMUM (`full-classification-stack`)

| Target / capability | 1 ft | 3 ft | 5 ft | 8 ft | 10 ft |
|---|---|---|---|---|---|
| Everything in Tier 2 | **Y** | **Y** | **Y** | **Y** | **Y** |
| Largest object that can hide in a ring seam | 56 mm | 56 mm | (tip closes at 343 mm) | — | — |
| **Labelled human / pet / object, in light** | **Y** (camera, COCO) | **Y** | **Y** | **Y** | **Y** |
| **Labelled human / pet / object, in darkness** | **Y** (thermal 9.2 × 10.3 px on a cat) | **Y** (3.1 × 3.4 px) | **~** (1.8 × 2.1 px) | **~** human only (2.1 × 4.5 px) | **N** for pets; **~** human (1.7 × 3.6 px) |
| **Cat vs dog** | **Y** camera only, needs light | **Y** camera | **Y** camera | **~** | **N** |
| **Box vs body** (material/shape, CNH) | **Y** forward arc, 37.5 mm depth bins | **Y** | **Y** | **~** | **N** |
| Human height measured (not inferred) | **Y** (CH head at 900 mm) | **Y** | **Y** | **~** | **N** |
| Individual identity | **N** | **N** | **N** | **N** | **N** |

### 4.4 What **no** tier can do, at any range

- **Direct sunlight above ~5 kLux on an optical sensor.** ST publishes 0 and 5 kLux only; the RPLIDAR C1 stops at 40 kLux;
  direct sun is 100–120 kLux. No number exists. Do not extrapolate.
- **Mirrors.** A mirror at 45° returns a folded path length and the robot believes the corridor continues. Map known
  mirrors as permanent keep-out zones.
- **Cat versus dog without a camera.** No combination of ToF, 32×24 thermal and one hobby radar does it.
- **Radar vital-signs discrimination on a moving robot.** Ego-motion writes a Doppler bias across the scene orders of
  magnitude larger than a 5 mm chest excursion.
- **Any safety rating.** Nothing here is IEC 61496 electro-sensitive protective equipment. A certified Type 3 scanner must
  prove **1.8 % minimum target reflectance** in its protective field; that is the pass mark a VL53L8CX does not meet and
  the reason a certified scanner sees a black sock and this stack does not. PL d needs a Category 3 architecture with
  certified components. Use the industrial arithmetic and the Z-factor discipline anyway; do not claim the rating.

---

## 5. The explicit answer: how many ToF sensors, how many people sensors

### 5.1 The counts

| Tier | ToF modules | of which: ring / cliff / head / scanning | People sensors | of which |
|---|---|---|---|---|
| **MINIMUM** | **18** | 12 / 6 / 0 / 0 | **0** | — |
| **RECOMMENDED** | **19** | 12 / 6 / 0 / 1 | **8** | 8 × AMG8833 thermal |
| **MAXIMUM** | **24** | 16 / 6 / 1 / 1 | **10** | 6 × MLX90640 thermal + 4 × camera |

### 5.2 The geometric reasoning, step by step

**Step 1 — use the *horizontal* FoV, never the diagonal headline.** A square zone array's diagonal relates to its
horizontal as `Φ_h = 2·atan(tan(Φ_d/2)/√2)`, **not** `Φ_d/√2`. This single error is worth 3–6 extra sensors per ring:

| Part | What the datasheet says | Horizontal FoV to size the ring with | Smallest N with tip ≤ 350 mm |
|---|---|---|---|
| VL53L1X | 27° **diagonal**, ROI-reducible to 20°/15° (DS DocID031281 Rev 3, Tables 1 & 9) | **19.27°** | **N = 38** |
| VL53L5CX | 45° H / 45° V / 63° diagonal (DS13754 Rev 2, Table 2) | **45.0°** | **N = 16** |
| VL53L8CX | 45° H / 45° V / 65° diagonal (DS14161 Rev 2, Table 2) | **45.0°** | **N = 16** |
| VL53L7CX | 60° H / 60° V / 90° diagonal (DS13865 Rev 6, Table 2) | **60.0°** | **N = 11** |
| AMG8833 | 60° typical, H and V | **60.0°** | N = 11 (not required — corroborating channel) |
| MLX90640-BAA | 110° X / 75° Y (Melexis Rev 12, Table 15) | **110.0°** | N = 5 |

**Step 2 — `N = 360/Φ` is the one value that must be avoided.** Two adjacent sensors with spacing `Δ` and half-angle
`θ = Φ/2` have edge rays separated by `Δ − Φ = −Ω`. At `Ω = 0` those edges are **exactly parallel** and never intersect at
any finite range: the wedge between them is blind forever. `N = 360/Φ` sets `Ω = 0` exactly. Closure requires `Φ > Δ`:

```
N_min = floor(360 / Φ_h) + 1
```

which equals `ceil(360/Φ_h)` **except** when `360/Φ_h` is an integer — precisely the case people reach for. For the
VL53L8CX, `N_min = 9`, not 8.

**Step 3 — closure is necessary but not sufficient; size on the blind-wedge tip.** Sensors sit on the perimeter, not at
the centre, so even a ring with positive overlap is blind in a triangular wedge close to the body:

```
D_tip = r · [ cos(Δ/2) + sin(Δ/2) · cot(Ω/2) ]        r = 175 mm,  Δ = 360/N,  Ω = Φ_h − Δ
```

For small overlap `cot(Ω/2) ≈ 2/Ω`, so **`D_tip` is inversely proportional to `Ω`** — halving the overlap doubles the
blind depth. The wedge is the triangle with the two apertures as its base (chord `= 2r·sin(Δ/2)`) and its apex at `D_tip`.
The largest object that can hide entirely inside it is the triangle's inscribed circle:

| Ring | N | Δ | Ω | D_tip (from centre) | Blind depth past skin | Seam base | **Largest sphere that hides** |
|---|---|---|---|---|---|---|---|
| VL53L8CX, 45° | 8 | 45.0° | 0° | **OPEN** | ∞ | — | unbounded |
| VL53L8CX, 45° | 10 | 36.0° | 9° | 853.6 mm | 678.6 mm | 108.2 mm | 232 mm — **a cat hides** |
| **VL53L8CX, 45°** | **12** | **30.0°** | **15°** | **513.1 mm** | **338.1 mm** | **90.6 mm** | **79.4 mm** |
| **VL53L8CX, 45°** | **16** | **22.5°** | **22.5°** | **343.3 mm** | **168.3 mm** | **68.3 mm** | **56.0 mm** |
| VL53L7CX, 60° | 10 | 36.0° | 24° | 421 mm | 246 mm | 108.2 mm | 79 mm |
| **AMG8833, 60°** | **8** | **45.0°** | **15°** | **670.4 mm** | **495.4 mm** | **133.9 mm** | **117.5 mm** |
| **MLX90640, 110°** | **6** | **60.0°** | **50°** | **339.2 mm** | **164.2 mm** | **175.0 mm** | **111.5 mm** |

**Step 4 — read the answer against the smallest target you must not hide.** A cat's smallest dimension is ~150 mm; a
human leg is 110–150 mm; a pet bowl is ~150 mm; a chair leg is 35–50 mm.

- **12 VL53L8CX hides nothing bigger than 79.4 mm.** Cats, legs, shoes and bowls all span a cone. Chair legs can hide, and
  that is the compliant bumper's job. → **MINIMUM and RECOMMENDED = 12.**
- **16 VL53L8CX hides nothing bigger than 56.0 mm.** Most chair legs are now caught too. → **MAXIMUM = 16.**
- **8 AMG8833 hides nothing bigger than 117.5 mm** — under a cat in every dimension, which is all a corroborating animate
  channel needs. Seven would leave `D_tip = 1171 mm`; six never closes. → **RECOMMENDED = 8.**
- **6 MLX90640-110° hides nothing bigger than 111.5 mm.** Five would give 147 mm, which is marginal against a curled cat.
  → **MAXIMUM = 6.**
- **4 cameras at 120° H, 90° spacing**: `Ω = 30°`, `D_tip = 586 mm`. Three cameras would be `Ω = 0` — open.
  → **MAXIMUM = 4.**

**Step 5 — cliff sensors are a separate count and a separate function.** A horizontal ring at 150–200 mm sees *nothing*
at a stair nosing: the floor simply stops. Six downward VL53L4CD at ≥50 Hz — four across the leading arc, two rear —
wired so that **a lost reading is treated as a cliff**. At 1.0 m/s the robot goes over the edge at every plausible latency,
which is an independent reason for the 0.5 m/s cap.

**Step 6 — the counts that were rejected, and why.**

| Ring you might be tempted to build | Count needed | Why it is not in any tier |
|---|---|---|
| 8 × VL53L8CX ("360 ÷ 45") | — | `Ω = 0`. Eight permanently open blind slots. |
| 12 × VL53L1X | **38** for a 350 mm tip | 19.27° horizontal. Even N = 19 leaves the tip at 10.4 m. |
| 6 × VL53L7CX ("360 ÷ 60") | — | `Ω = 0`. Also fails the range requirement — see §6. |
| 10 × VL53L7CX | 10 | Geometry is fine (421 mm); **range fails** — see §6. |
| 3–4 × 24 GHz presence radar | 3–4 | Rejected outright — see §6. |
| 7 × MLX90640-55° for a thermal ring | **9** for a 619 mm tip | $674 and bus-bound to ~1 Hz. The 110° part does the same job with 6. |

---

## 6. Ranked shortlist, with the runner-up rejected at each rank

### Rank 1 — Perimeter ring element: **VL53L8CX** (Pololu #3419, $24.95)

**Why.** The ring's job is to guarantee the robot stops before contact. The binding requirement is the reaction distance
for the fastest closing target — a cat at 4.5 m/s closing — which is **899 mm** with this tier's 159 ms latency chain.
Against a 17 % grey target in a 5 kLux room at 4×4 / 30 Hz the VL53L8CX delivers **1650 mm (inner) / 1550 mm (corner)**.
The seams of a ring are made of corner zones, so the corner column is the one that counts; the margin there is **+72 %**.
It is the actively maintained part (stm32duino library touched 2026-07-01), it has 20 MHz SPI as well as I²C, and its free
per-zone **motion indicator** gives an animate/inanimate primitive at under 7 mW per sensor in autonomous mode.

**Runner-up rejected: VL53L7CX** (Pololu #3418, $19.95). Its 60° horizontal FoV cuts the ring from 12 to 10 and saves
$100 — a genuinely attractive trade until you read its range table. At 4×4 / 30 Hz, 17 % grey, 5 kLux, it is
**550 mm inner / 500 mm corner**, against the 899 mm requirement. It **fails by 44 %**. In 8×8 it is a **250–350 mm**
sensor — inside the robot's own turning circle. Wide FoV is bought with range, one for one. *A ring you cannot use in a
lit room is not a ring.*

**Second runner-up rejected: VL53L5CX** (Pololu #3417, $19.95). Same 45° horizontal, $5 cheaper, and it passes the same
test — but only just: **1000 mm inner / 950 mm corner** against 899 mm, a 6 % corner margin against the L8CX's 72 %. It is
also I²C-only (no SPI, so no fast firmware boot), its Arduino library has not been touched since 2023-08-23, and the
VL53L5CX-SATEL breakout carries a **51-week factory lead time** behind its stock. Save the $60 somewhere else.

**Rejected: VL53L9CX**, the newest and by far the best ST grid part (54 × 42 = 2268 zones, 100 Hz, 8.8 m; a cat at 10 ft is
4.5 × 8 zones instead of 0.8 × 1.6). **MIPI CSI-2 / I3C only** — no I²C mode, so one Linux-class camera port per sensor;
the eval board is **$80.39 with 0 in stock** and one unit due 2026-10-28; there is no Arduino, CircuitPython or ESP-IDF
driver. Design it in for 2027, as a single forward-facing head, not as a ring.

### Rank 2 — Ring count: **12** (minimum/recommended), **16** (maximum)

**Why.** §5 in full. 12 bounds the hideable object at 79.4 mm; 16 bounds it at 56.0 mm.

**Runner-up rejected: 8.** `Ω = 0`. This is the single most common perimeter-ring error and it produces eight blind slots
that never close at any range. **Also rejected: 27**, which would pull the tip inside a 350 mm square's 247.5 mm corner
radius — at that count a ring of array modules is the wrong architecture and a scanning lidar is cheaper and better.

### Rank 3 — Dark-target and ambient-light channel: **Slamtec RPLIDAR C1** ($69.00)

**Why.** dTOF, **12 m @ 70 % / 6 m @ 10 % reflectivity** (a published low-reflectance figure, which is itself rare),
**40 000 lux**, 0.72° at 10 Hz, **0.05 m** blind radius, IP54, 110 g, one UART. It covers the ToF ring's two structural
failures — black fur and sunbeams — and it gives 500 points per revolution, enough to scan-match and hence to know that a
cluster is *new*. At $69 it is cheaper than three VL53L8CX carriers.

**Runner-up rejected: RPLIDAR A1** (Adafruit #4010, $99.95). Triangulation, not dTOF. Its datasheet qualifies its range
as "White objects" with **no** dark-target figure published anywhere, and says it works outdoors *"without direct sunlight
exposure"*. 0.15 m blind radius on a robot whose skin is at 0.175 m. 170 g and 5.5 Hz (182 ms per scan, 91 mm of motion
smear at 0.5 m/s). Its own spec page still prints "≤1° angular resolution" beside "8 kHz sampling", two figures that
cannot both be true — a leftover from the 2 kHz rev 1.0 part. Costs $31 more to be worse.

**Also rejected: YDLIDAR X2 / X4 PRO / G4** — triangulation, and the X4 PRO's published service life is **1500 hours**
(about 62 days continuous). The X2's own datasheet lists a lighting environment of **0–2000 lux**. **Livox Mid-360** —
265 g, 6.5 W, Ethernet, and its −7° lower edge means a unit at 1000 mm first reaches the floor **8.1 m out**.

### Rank 4 — Animate/inanimate channel: **Panasonic AMG8833** (Adafruit #3538, $44.95)

**Why.** Thermal is the only modality that separates alive from not-alive, and the only one that sees a **motionless**
target — a sleeping cat is invisible to MTI radar and to PIR, and visible to thermal. It is the cheapest imaging thermal
part (8 units = $359.60 against $524.65 for a 7-unit MLX90640-55° ring), it runs at 10 Hz (fast enough for a 1.7–4 Hz gait
cue, which a bus-limited MLX90640 ring is not), it draws 4.5 mA, and at h = 250 mm it has a cat in frame from 87 mm out.
Fused with the ToF ring's height measurement it answers human-vs-pet to about 5 ft — which is exactly the honest
classification envelope for a sub-$600 sensor suite.

**Runner-up rejected: STHS34PF80** (Adafruit #6426, $14.95; 5 units = $74.75). Better silicon in every respect except the
one that matters — **it has one sensing element**. 0.0125 °C RMS equivalent noise, 10 µA, holds a static human, needs no
Fresnel lens, embedded presence/motion algorithms. And it reports "something warm is somewhere in an 80° cone." No
bearing, no size, no shape. It contributes nothing to human-vs-pet. Worth $74.75 later as a parked-robot wake-up layer;
not a replacement for the array ring.

**Also rejected: PIR, including pet-immune PIR.** Structurally cannot detect a static target; is **least** sensitive to
radial motion (a person walking straight at the robot is the worst case); does not see through glass; responds to warm
airflow, which a drivetrain provides; and on a moving platform the differential-zone principle fires continuously. The
"pet immunity" of a Bosch ISC-BPR2-WP12 or Resideo IS335 is a **geometric** trick that requires a **2.2–2.75 m** mounting
height. At 1.0 m on a robot it inverts: it can see the pet and miss the person.

### Rank 5 — Classification: **MLX90640-110° + 4 cameras on a Pi 5 + Hailo-8L**

**Why.** COCO contains `person`, `cat` and `dog` as separate classes. A stock detector does the whole job out of the box,
with no custom dataset and no signal processing, at 136.7 FPS on a $150 compute budget. That is a capability gap of an
entirely different order from anything else in this study. The thermal ring is what keeps it working at night.

**Runner-up rejected: mmWave micro-Doppler classification.** The published work is real — 97.66 % human-vs-large-quadruped
on FMCW spectrograms — but it is single-target, outdoor, clean-scene, cooperative-dwell work. In an operational
environment the measured figure is **75 % at 250 ms of dwell, rising to only ≈90 % at 1.25 s**, and the robot's own
classification budget between the warning and protective field edges is **167–323 ms**. It also needs the raw
range-Doppler map or ADC stream, which **no hobby module emits** — the richest output in the whole DFRobot catalogue is
`{state, distance, speed, energy, direction, per-gate bitmap}`, post-processed scalars that throw away the spectrogram a
classifier would need.

### Rank 6 — Rejected outright: **all 24 GHz presence radar**

This includes DFRobot SEN0395 ($29.00), SEN0557 ($9.90), SEN0609 ($13.90), SEN0610 ($12.90), SEN0691 ($8.90) and the
HLK-LD2410 inside several of them. Five independent disqualifications, any one of which is sufficient:

1. **Range resolution.** The 24.00–24.25 GHz ISM allocation is 250 MHz wide, so `ΔR = c/2B = 600 mm` for *every* module in
   the band. A 600 mm range cell on a 350 mm robot is 1.7 robot-widths deep.
2. **Ego-motion.** Every FMCW presence pipeline begins with a moving-target-indicator stage that assumes a static sensor.
   On a moving robot every wall acquires Doppler, the clutter map is invalidated every frame, and the C4002's
   `startEnvCalibration()` — which requires an empty room — exists precisely because the part learns a static background.
   The SEN0395 FAQ's own cure for a stuck output is *"please ensure that the sensor is fixed firmly."*
3. **Minimum range.** The C4001 (SEN0609/SEN0610) reports nothing below **1.2 m** — precisely the zone a 350 mm robot
   cares about most.
4. **Through-wall.** Users report the LD2410 detecting someone standing quietly behind two layers of sheetrock. On a fixed
   sensor you range-gate it away; on a robot the wall geometry changes continuously and a fixed gate cannot be tuned.
5. **The vendor says so.** DFRobot's own SEN0395 wiki FAQ: *"No, the sensor detects movement of all objects within range
   by detecting mmWave radar and is very sensitive."* Across six SKUs there are **zero** mentions of pet detection, pet
   immunity, animal filtering, or false triggers from fans and curtains.

Add to that the cost in power — twelve LD2410-class modules are **4.84 W average and 9.13 W peak** — and the finding that
**one 60 GHz radar detects a 3 kg, 400 mm dog 46.1 % of the time without tracking** (97.10 % needs four fused radars plus a
tracker). The radar-plus-ToF pair is also the **weakest pair** in the fusion analysis: both are geometric, and radar adds
only "is it moving toward me," which ToF already gives by differencing frames.

If radar is ever revisited, it must be **60 GHz**, not 24 GHz: at a *fixed physical aperture* — which is what a 350 mm
robot actually constrains — 60 GHz wins the link budget by about 8 dB, gives four times the bandwidth (37.5 mm range
cells), a quarter-size array, and far less wall penetration. Oxygen absorption at 3 m is 0.09 dB two-way and irrelevant.

### Rank 7 — Rejected: **ultrasonic as anything but a glass detector**

Colour-blind and the only technology here that sees clear glass, so two forward units earn their $7.90. But a 49 ms cycle
plus mandatory interleave makes an 8-sensor sweep **264 ms (3.8 Hz)**, which is fatal in the protective-stop path; soft
targets absorb 40 kHz, so HC-SR04-class reliability on a person past 1 m is **below 50 %**; and a smooth surface more than
~15° off perpendicular bounces the ping away and reads "clear."

---

## 7. Preconditions, blockers and things to fix before ordering

**Blocker — `dalek` cannot carry any of these tiers on its present electrical design.** The repo records **~0.30 A of
spare 5 V** on `dalek`, against **724 mA** for the minimum tier. It also has essentially no free GPIO and a single shared
I²C bus. What unblocks it: either a second 5 V buck sized for 1.0 A (the Adafruit MPM3610's 1.2 A rating is unconditional
over 6–21 V in, so a second one is the obvious move), or a decision to run the ring from the 12 V pack through its own
regulator. The operator or the `dalek` electrical owner must choose. Its twelve vertical skirt seams do map exactly onto a
12-sensor ring at 30°, and its 300 mm diameter improves `D_tip` to **440 mm** at N = 12.

**`fable-r2d2` is the right host.** ~4.1 A spare 5 V, an entirely unused KB2040 STEMMA QT bus, eighteen free Pi GPIOs
including a free UART on GPIO14/15 for the lidar, three free USB ports for cameras, and **two body rings that have not
been designed yet** — so the apertures can be modelled in rather than retrofitted. Its constraints: the 12-wire slip ring
is fully assigned (no new dome wiring), the wall is 3.6 mm, and its centre-of-gravity and tip-back figures are currently
marked *unknown* in its own `docs/mechanical.md` and **must be re-run before any mass goes high**.

**Supply flags, read 2026-09-12.** Adafruit **#4469 MLX90640-110° is out of stock** — the maximum tier's thermal ring must
be sourced from Melexis, Waveshare or a distributor. Adafruit **#4407 MLX90640-55° had 4 in stock**. **VL53L5CX-SATEL
carries a 51-week lead time**; SATEL-VL53L8 is 13 weeks. The **VL53L8CH price is not published in any source lane** —
confirm it before committing to the maximum tier, or substitute SATEL-VL53L8 ($32.95) and lose the CNH histogram.

**Measure these five things on the built robot before trusting any number above.**

1. **Your real stopping distance**, on your real floor, at your real battery state. Put the measured value into the
   protective-field calculation; do not use the figure in this document.
2. **Your harness capacitance** with an LCR meter at 100 kHz. Nobody publishes STEMMA QT / Qwiic cable capacitance.
3. **Mutual interference between adjacent ring sensors** with the final shell fitted. ST publishes no
   mutual-interference rejection figure for N co-located units.
4. **Your shell's ε_r at 24/60 GHz** if radar is ever revisited. Not published for Bambu PETG Basic, and a 3-perimeter
   20 %-infill wall is a solid-sparse-solid sandwich with an unknown effective permittivity, not a homogeneous slab.
5. **The adversarial target set**: a black sock on the floor, a mirror, a glass door, a sunlit patch, a 120 mm sleeping-cat
   mannequin, and a person standing still in black clothing. Every one of those is a *fail-to-danger* mode.

**One line of logic worth more than any sensor upgrade:** **OR** the stop signals — any sensor says stop, stop — and
**AND** the clear signals — all sensors must agree it is clear before resuming. Fail-to-danger modes (black sock to a ToF,
still person to a radar, cat under a lidar plane) must each be covered by a second modality with **different physics**.
Fail-to-safe modes (radar ghosts, a dark rug read as a cliff) cost availability, not safety, and must **never** be "fixed"
by widening a threshold or disabling the check.

---

## 8. Source lanes

`coverage-geometry.md` · `st-grid-tof-latest.md` · `adafruit-tof-st.md` · `adafruit-tof-nonst.md` · `adafruit-4010.md` ·
`adafruit-thermal-ir.md` · `other-st-tof-and-lidar.md` · `dfrobot-mmwave-presence.md` · `dfrobot-mmwave-ranging.md` ·
`dfrobot-mmwave-full-grid.md` · `human-pet-object-discrimination.md` · `range-capability-modelling.md` ·
`safety-and-failure-modes.md` · `integration-power-bus.md` · `prior-art-commercial.md` · `robot-project-envelopes.md`
