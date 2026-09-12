# Range-Capability Modelling: What Each Sensing Modality Can Actually Tell You at 1, 3, 5, 8 and 10 Feet

Lane: `range-capability-modelling`. Written 2026-09-12.

Platform under study: a mobile robot with a 350 mm square or 350 mm diameter round footprint,
600-1200 mm tall, needing 360-degree perimeter awareness. Required outputs are (a) any collidable
obstacle, (b) humans specifically, (c) pets 200-500 mm tall specifically, and (d) the ability to tell
human from pet from inanimate object.

The five evaluation distances are fixed for the whole comparison:

| Label | mm | m |
|---|---|---|
| 1 ft | 305 | 0.305 |
| 3 ft | 914 | 0.914 |
| 5 ft | 1524 | 1.524 |
| 8 ft | 2438 | 2.438 |
| 10 ft | 3048 | 3.048 |

Two reference targets are used throughout:

- **Human torso**: 450 mm wide x 700 mm tall (the part a chest-height sensor actually sees).
- **Cat / small dog**: 250 mm long x 200 mm tall side profile.
- A third, **chair leg 40 mm x 400 mm**, is used as the hard inanimate case.

---

## 1. Master capability table

Every cell below is the *honest* answer for a target that is **not** a wall filling the field of view,
in **normal indoor lighting**, with the sensor on a moving 350 mm robot. The derivations are in
Sections 3-6. Confidence tags: **DS** = datasheet-verified, **VP** = vendor-page-verified,
**CALC** = computed in this document from datasheet inputs, **INF** = inferred.

### 1a. Human detection

| Modality (representative part) | 1 ft / 305 mm | 3 ft / 914 mm | 5 ft / 1524 mm | 8 ft / 2438 mm | 10 ft / 3048 mm |
|---|---|---|---|---|---|
| SPAD dToF single-zone (VL53L1X) | obstacle + distance | obstacle + distance | obstacle + distance (dark) | obstacle + distance (dark only) | nothing in daylight; marginal in dark |
| SPAD dToF 8x8 (VL53L5CX, 45 x 45 deg) | obstacle + distance + coarse shape | obstacle + distance | obstacle + distance (dark) | nothing reliable | nothing |
| SPAD dToF 8x8 wide (VL53L7CX, 60 x 60 deg) | obstacle + distance + coarse shape | obstacle + distance (dark) | nothing reliable | nothing | nothing |
| 24 GHz FMCW presence (HLK-LD2410) | human present (no usable distance, one 600 mm bin) | human present + 0.75 m gate | human present + gate | human present + gate | human present + gate |
| 60 GHz FMCW MIMO (IWR6843 / IWRL6432) | human + distance + angle + micro-Doppler | human + distance + angle + micro-Doppler | human + distance + angle + micro-Doppler | human + distance + angle | human + distance + angle |
| Thermal 8x8 (AMG8833, 60 deg) | full silhouette (10 x 16 px) | human vs pet (3.4 x 5.3 px) | human present + crude size (2 x 3 px) | human present (1.3 x 2 px) | warm smear, 1 x 1.6 px, presence only |
| Thermal 32x24 55 deg (MLX90640 BAB) | full silhouette (45 x 87 px) | full silhouette (15 x 29 px) | full silhouette (9 x 17 px) | human vs pet (5.7 x 11 px) | human vs pet (4.5 x 8.7 px) |
| Thermal 32x24 110 deg (MLX90640 BAA) | full silhouette (17 x 36 px) | full silhouette (5.5 x 12 px) | human vs pet (3.3 x 7.2 px) | human vs pet, marginal (2.1 x 4.5 px) | human present + crude size (1.7 x 3.6 px) |
| 2-D scanning lidar (RPLIDAR C1) | obstacle + distance, ~29 hits/leg | obstacle + distance, ~10 hits/leg | obstacle + distance, ~6 hits/leg | obstacle + distance, ~4 hits/leg | obstacle + distance, ~3 hits/leg, legs only, no torso |

### 1b. Pet (cat / small dog) detection

| Modality (representative part) | 1 ft / 305 mm | 3 ft / 914 mm | 5 ft / 1524 mm | 8 ft / 2438 mm | 10 ft / 3048 mm |
|---|---|---|---|---|---|
| SPAD dToF single-zone (VL53L1X) | obstacle + distance | obstacle + distance (dark) | nothing reliable | nothing | nothing |
| SPAD dToF 8x8 (VL53L5CX) | obstacle + distance | nothing reliable | nothing | nothing | nothing |
| SPAD dToF 8x8 wide (VL53L7CX) | obstacle + distance (dark) | nothing reliable | nothing | nothing | nothing |
| 24 GHz FMCW presence (HLK-LD2410) | motion present, *not* labelled pet | motion present | motion present | motion, weak | nothing reliable |
| 60 GHz FMCW MIMO | target + distance + angle | target + distance + angle | target + distance + angle | target + distance, class uncertain | target, class uncertain |
| Thermal 8x8 (AMG8833) | pet silhouette (5.7 x 4.5 px) | pet present + crude size (1.9 x 1.5 px) | 1 px blob, presence only | sub-pixel smear, 0.40 fill | sub-pixel smear, 0.26 fill |
| Thermal 32x24 55 deg (MLX90640 BAB) | full silhouette (25 x 25 px) | full silhouette (8.4 x 8.3 px) | pet vs human (5 x 5 px) | pet vs human (3.1 x 3.1 px) | pet present + size (2.5 x 2.5 px) |
| Thermal 32x24 110 deg (MLX90640 BAA) | full silhouette (9.2 x 10.3 px) | pet vs human (3.1 x 3.4 px) | pet present + size (1.8 x 2.1 px) | 1 px blob | sub-pixel smear, 0.94 fill |
| 2-D scanning lidar (RPLIDAR C1) | obstacle, ~65 hits, **only if the scan plane is below 250 mm** | ~22 hits | ~13 hits | ~8 hits | ~6.5 hits |

### 1c. The classification question

No single modality in this price class answers "human vs pet vs inanimate" across all five distances.
The shortest honest summary:

| Distance | What can classify human vs pet vs object | What cannot |
|---|---|---|
| 1 ft | AMG8833, both MLX90640 variants, 60 GHz MIMO | all SPAD ToF, 24 GHz presence, 2-D lidar |
| 3 ft | Both MLX90640 variants, AMG8833 (marginal), 60 GHz MIMO | all SPAD ToF, 24 GHz presence, 2-D lidar |
| 5 ft | Both MLX90640 variants, 60 GHz MIMO | AMG8833, all SPAD ToF, 24 GHz presence, 2-D lidar |
| 8 ft | MLX90640 55 deg, MLX90640 110 deg (marginal), 60 GHz MIMO (human only) | AMG8833, everything else |
| 10 ft | MLX90640 55 deg only, plus 60 GHz MIMO for "human, yes/no" | everything else |

---

## 2. Corrections to common assumptions, up front

Three numbers widely repeated in hobby robotics are wrong, and the datasheet arithmetic in this
document shows why.

1. **"Sunlight cuts SPAD ToF range by 60-75 %."** ST's own VL53L1X Table 7 says the loss at
   200 kcps/SPAD is **80 %** for an 88 % white target (360 cm to 73 cm) and **60 %** for a 17 % grey
   target (170 cm to 68 cm). At 50 kcps/SPAD the loss is **54 %** for white. The loss is worse than
   folklore for bright targets and about right for dark ones, because bright and dark targets converge
   on the same ~70 cm floor once ambient dominates.
2. **"A radar rated 12 m on a human sees a cat far closer."** The range equation is fourth-root in
   RCS, which is extremely forgiving. A 15 dB RCS deficit costs a factor of **2.37** in range, not 30.
   A 12 m human rating becomes **4.9-7.3 m** on a 0.01-0.05 m^2 pet. Radar's pet problem is not range;
   it is that the pet is *detected perfectly well* and then cannot be labelled.
3. **"An 8x8 thermal array can tell a person from a dog."** It can, up to about 3 ft. At 10 ft an
   AMG8833 pixel is **440 mm** across, so an entire 450 mm human torso is one pixel wide. There is no
   shape left to classify.

---

## 3. SPAD direct time-of-flight (VL53L0X / L1X / L5CX / L7CX / L8CX)

### 3.1 The photon budget

A SPAD dToF module fires a 940 nm VCSEL, then histograms photon arrival times across an array of
single-photon avalanche diodes. Three rates matter:

- **Signal rate** - returned laser photons per second per SPAD, proportional to `rho * f_fill / d^2`
  where `rho` is target reflectance at 940 nm, `f_fill` is the fraction of the field of view the target
  covers, and `d` is distance.
- **Ambient rate** - background 940 nm photons per second per SPAD. Independent of `d`. ST quotes
  this in **kcps/SPAD**.
- **Dark count rate** - silicon noise, negligible next to indoor ambient.

In the shot-noise limit, SNR after integration time `T` is roughly `S*T / sqrt((S + 2A)*T)`. Two
regimes follow:

- **Signal-limited (dark room):** SNR proportional to `S*sqrt(T)`, so `d_max` proportional to `sqrt(rho)`.
- **Ambient-limited (daylight):** SNR proportional to `S*sqrt(T/A)`, so `d_max` proportional to `sqrt(rho) * A^(-1/4)`.

### 3.2 ST's published tables, verbatim

**VL53L1X, Table 6 - Performances in dark conditions.** Test conditions: ambient light = dark,
timing budget = 100 ms, long distance mode, target covers the full FoV (27 deg typical), Munsell charts,
2.8 V, 23 C, detection rate 100 %.

| Parameter | Target reflectance | Min. value | Typ. value |
|---|---|---|---|
| Max distance (cm) | White 88 % | 260 | 360 (400 with TB = 140 ms) |
| Max distance (cm) | Grey 54 % | 220 | 340 |
| Max distance (cm) | Grey 17 % | 80 | 170 |
| Ranging error (mm) | - | - | +/- 20 |

**VL53L1X, Table 7 - Typical performances in ambient light with long distance mode.**

| Parameter | Target reflectance | Dark | 50 kcps/SPAD | 200 kcps/SPAD |
|---|---|---|---|---|
| Max. distance (cm) | White 88 % | 360 | 166 | 73 |
| Max. distance (cm) | Grey 54 % | 340 | 154 | 69 |
| Max. distance (cm) | Grey 17 % | 170 | 114 | 68 |
| Ranging error (mm) | - | +/- 20 | +/- 25 | +/- 25 |

**VL53L1X, Table 8 - Short distance mode.** White 88 %: 130 cm dark, 130 cm at 200 kcps/SPAD.
Grey 17 %: 130 cm dark, 120 cm at 200 kcps/SPAD. Short mode is nearly ambient-immune and caps at
about 1.3 m - the one honest "works in sunlight" SPAD configuration.

**VL53L1X, Table 4 - Maximum distance vs. distance mode under ambient light.** Timing budget
100 ms, white target 88 %, dark = no IR ambient, ambient = 200 kcps/SPAD.

| Distance mode | Max. distance in dark (cm) | Max. distance under strong ambient light (cm) |
|---|---|---|
| Short | 136 | 135 |
| Medium | 290 | 76 |
| Long | 360 | 73 |

**VL53L1X, Table 9 - Partial ROI in dark conditions.** This is the FoV-narrowing trade:

| Parameter | Target reflectance | 16x16 SPADs | 8x8 | 4x4 |
|---|---|---|---|---|
| Max. distance (cm) | White 88 % | 360 | 308 | 170 |
| Max. distance (cm) | Grey 54 % | 340 | 254 | 143 |
| Max. distance (cm) | Grey 17 % | 170 | 119 | 45 |
| Diagonal FoV (degrees) | - | 27 | 20 | 15 |
| Ranging error (mm) | - | +/- 20 | +/- 20 | +/- 20 |

Test conditions for Table 9, verbatim: *"Ambient light = dark"*, *"**Target covers partial FoV**"*,
*"ROI centered on optical center"*, *"Long distance mode"*. Note the second line: Table 9 is the one
ST ranging table in this document whose target does **not** fill the full field of view, so it is the
exception to the fill-factor rule stated in Section 3.6, not an instance of it.

**VL53L0X, Table 11 - Max ranging capabilities with 33 ms timing budget.** Indoor = no infrared;
outdoor overcast = 10 kcps/SPAD == 1.2 W/m^2 at 940 nm == 5 kLux daylight, while ranging on a grey 17 %
chart at 40 cm. Distances guaranteed for a minimum detection rate of 94 %. The condition most often
dropped when this table is quoted: *"All distances are for a complete Field of View covered
(FOV = 25 degrees)"* - the VL53L0X cone is **25 deg**, narrower than the VL53L1X's 27 deg, and the
table assumes the target fills it.

| Target reflectance (full FoV) | Conditions | Indoor | Outdoor overcast |
|---|---|---|---|
| White Target (88 %) | Typical | 200 cm+ (long range API profile) | 80 cm |
| White Target (88 %) | Minimum | 120 cm | 60 cm |
| Grey Target (17 %) | Typical | 80 cm | 50 cm |
| Grey Target (17 %) | Minimum | 70 cm | 40 cm |

**VL53L5CX, Table 18 - Max ranging capabilities, continuous 15 Hz, 8x8.** Targets Munsell N4.75
(17 %) and N9.5 (88 %); 5 kLux == 2 W/m^2 at 940 nm; 90 % detection rate; no cover glass.
Footnote on the grey row, verbatim: *"measured 13 % in IR at 940 nm"*.

| Target | Zone | Dark (0 klux) | Ambient (5 klux) |
|---|---|---|---|
| White 88 % | Inner | Typ 3500 mm / Min 2600 mm | Typ 1100 mm / Min 950 mm |
| White 88 % | Corner | Typ 3100 mm / Min 1700 mm | Typ 1000 mm / Min 800 mm |
| Grey 17 % | Inner | Typ 1300 mm / Min 900 mm | Typ 800 mm / Min 600 mm |
| Grey 17 % | Corner | Typ 1100 mm / Min 600 mm | Typ 650 mm / Min 400 mm |

**VL53L5CX, Table 17 - Max ranging capabilities, continuous 30 Hz, 4x4.** White 88 % inner zone
Typ 4000 mm / Min 4000 mm dark, and Typ 1700 mm / Min 1400 mm at 5 klux.

The resolution-versus-range trade is real but it is **much smaller than it is usually stated, and it is
not visible at all in the dark**. Going from 8x8 to 4x4 divides the zone count by **four**, not two
(64 zones to 16). The measured effect on ST's own typical numbers, white 88 % inner zone:

| Condition | 8x8 at 15 Hz (Table 18) | 4x4 at 30 Hz (Table 17) | Change |
|---|---|---|---|
| Dark (0 klux) | Typ 3500 mm | Typ 4000 mm | **+14 %** |
| Ambient (5 klux) | Typ 1100 mm | Typ 1700 mm | **+55 %** |

So range does **not** double. Three caveats make even the +14 % figure unreliable: the 4x4 dark column
is clipped at the part's 4 m product ceiling (its *minimum* is also 4000 mm, so the measurement is
saturated and the true 4x4 dark range is unknown); the two tables are taken at different frame rates
(30 Hz versus 15 Hz), so the 4x4 case gets roughly **half** the integration time per frame, which
cancels much of the per-zone photon gain; and only the ambient-limited column - where the extra
per-zone signal buys real SNR against a fixed noise floor - shows a large gain. **Resolution and range
do trade against each other on the same silicon, but the honest exchange rate is about +50 % of range
for a 4x cut in zone count, and only in ambient light.** `CALC` from ST Tables 17 and 18.

**VL53L7CX, Table 18 - Max ranging capabilities, continuous 15 Hz, 8x8.**

| Target | Zone | Dark (0 klux) | Ambient (5 klux) |
|---|---|---|---|
| White 88 % | Inner | Typ 2000 mm / Min 1700 mm | Typ 500 mm / Min 400 mm |
| White 88 % | Corner | Typ 1900 mm / Min 1100 mm | Typ 500 mm / Min 400 mm |
| Grey 17 % | Inner | Typ 800 mm / Min 700 mm | Typ 350 mm / Min 250 mm |
| Grey 17 % | Corner | Typ 750 mm / Min 450 mm | Typ 250 mm / Min 200 mm |

The wide-FoV part loses roughly half its range against the 63-degree-diagonal VL53L5CX, and in 5 klux
the wide part is a **25-50 cm** sensor on a dark target. That is inside the robot's own turning circle.

Field-of-view figures. The VL53L5CX and VL53L7CX numbers are the **detection volume** row of Table 2
"FoV angles" in each datasheet. The VL53L1X number is **not** in a Table 2 - it is in Table 1
"Technical specification" ("Receiver Field Of View (diagonal FOV): Programmable from 15 to 27
degrees"), with the "typically 27 deg" wording in section 3.1 item 1:

| Part | Horizontal | Vertical | Diagonal | Source | Measurement condition (verbatim) |
|---|---|---|---|---|---|
| VL53L1X | - | - | 27 deg typical, programmable 15-27 | Table 1 + section 3.1 | full FoV, 16x16 SPAD ROI |
| VL53L5CX | 45 deg | 45 deg | 63 deg | Table 2, detection volume | "white 88 % reflectance perpendicular target in full FoV, located at 1 m from the sensor, without ambient light (dark conditions), with an 8x8 resolution and 14 % sharpener (default value), in Continuous mode at 15 Hz" |
| VL53L7CX | 60 deg | 60 deg | 90 deg | Table 2, detection volume | same condition text as above |

The same Table 2 in each part also gives a **collector exclusion zone** that is much wider than the
detection volume - 55.5 x 61 deg (82 deg diagonal) for the VL53L5CX, 74 x 74 deg (105 deg diagonal)
for the VL53L7CX. That is the number that sizes the cover-window aperture, not the sensing cone; ST's
note is explicit that *"The cover window opening must be equal to or wider than the exclusion zone."*
Designing a robot shell to the 45- or 60-degree figure will vignette the sensor. `DS`

### 3.3 What "200 kcps/SPAD" means in lux

ST publishes the conversion in two places, and they agree.

```
========================================================================================================
A. ST AMBIENT UNITS CONVERTED TO LUX (using ST's own published equivalences)
========================================================================================================
  VL53L0X DS note 2 : 10 kcps/SPAD == 1.2 W/m^2 at 940 nm == 5 kLux daylight
  VL53L5CX/L7CX DS  : 2 W/m^2 at 940 nm == 5 kLux daylight
       5 kcps/SPAD  ->     0.6 W/m^2 @940nm  ->      2.5 kLux-equivalent daylight
      10 kcps/SPAD  ->     1.2 W/m^2 @940nm  ->      5.0 kLux-equivalent daylight
      50 kcps/SPAD  ->     6.0 W/m^2 @940nm  ->     25.0 kLux-equivalent daylight
     200 kcps/SPAD  ->    24.0 W/m^2 @940nm  ->    100.0 kLux-equivalent daylight
  Reference points: office lighting ~5 kcps/SPAD (ST); overcast outdoors ~10 kcps/SPAD (ST);
  full direct sunlight is ~100-120 kLux, i.e. ST's 200 kcps/SPAD case is roughly full sun.
```

ST's own verbal definitions from VL53L1X section 3.1, quoted: *"Dark = no IR light in the band 940 nm
+/-30 nm"*; *"50 kcps/SPAD = lighting on a sunny day from behind a window"*; *"200 kcps/SPAD = lighting
on a sunny day from behind a window, with direct illumination on the sensor"*; *"For reference, usual
office lighting is around 5 kcps/SPAD"*.

So the ST tables bracket the real world well: office at about 5 kcps (barely any loss), a bright window
at about 50 kcps (half the range), a sunbeam on the floor at about 200 kcps (one fifth the range).
**A pool of sunlight on a wooden floor is the single worst place a SPAD-only robot can be.**

### 3.4 Does the physics match the datasheet?

```
========================================================================================================
B. HOW MUCH RANGE AMBIENT ACTUALLY COSTS (VL53L1X Table 7, long mode, TB=100 ms)
========================================================================================================
  target       dark cm  50 kcps cm  200 kcps cm  loss @50  loss @200
  White 88%        360         166           73       54%        80%
  Grey 54%         340         154           69       55%        80%
  Grey 17%         170         114           68       33%        60%

  Fitted power law d_max ∝ A^(-n) between the 50 and 200 kcps columns:
    White 88%   exponent n = 0.593   (pure shot-noise theory predicts n = 0.25)
    Grey 54%    exponent n = 0.579   (pure shot-noise theory predicts n = 0.25)
    Grey 17%    exponent n = 0.373   (pure shot-noise theory predicts n = 0.25)
  Measured decay is 2-3x steeper than shot-noise theory. Cause: SPAD dead-time pile-up plus
  the 100% detection-rate requirement, not photon statistics alone.

========================================================================================================
C. REFLECTANCE LAW: does d_max ∝ sqrt(rho) hold? (VL53L1X Table 6, dark, TB=100 ms)
========================================================================================================
  rho=  54%  predicted  282.0 cm   datasheet  340.0 cm   error  -17.1%
  rho=  17%  predicted  158.2 cm   datasheet  170.0 cm   error   -6.9%
  ST footnote (VL53L5CX Table 18): the '17 %' Munsell N4.75 chart 'measured 13 % in IR at 940 nm'.
  rho=  13% (IR)  predicted  138.4 cm   datasheet  170.0 cm   error  -18.6%
```

Two conclusions:

- The **sqrt(rho) reflectance law is real**: predicting 17 % grey from 88 % white gets within 7 % of
  the published number.
- The **ambient law is not a clean A^(-1/4)**. The measured exponent is 0.37-0.59, two to three times
  steeper than shot noise predicts. This is the **ambient-rate saturation limit**: every ambient
  photon that fires a SPAD holds that SPAD in dead time (tens of nanoseconds), so at high ambient the
  array loses effective sensor area *as well as* gaining noise. The two effects compound. This is why
  every SPAD vendor quotes an "ambient immunity" ceiling rather than a graceful roll-off, and it is
  why short distance mode - which uses a narrower histogram window and rejects most ambient - is
  almost flat from dark to 200 kcps/SPAD (136 cm to 135 cm).

### 3.5 The validity thresholds that actually gate a reading

A SPAD reading is not returned unless it passes fixed checks. These are the numbers that turn
"the sensor can see 3.6 m" into "the sensor returns a number".

| Part | Check | Default | Source |
|---|---|---|---|
| VL53L1X (ULD API) | Signal threshold | **1024 kcps** | `VL53L1X_SetSignalThreshold` - "This function programs a new signal threshold in kcps (default=1024 kcps" |
| VL53L1X (ULD API) | Sigma threshold | **15 mm** | `VL53L1X_SetSigmaThreshold` - "This function programs a new sigma threshold in mm (default=15 mm)" |
| VL53L0X (Pololu API) | Return signal rate limit | **0.25 MCPS** | "This limit is initialized to 0.25 MCPS by default" |
| VL53L0X | On-chip checks | signal value check, offset correction, cross-talk correction | VL53L0X DS section 2.6.3 |
| VL53L0X | API-side checks | Return Ignore Threshold (RIT, signal vs cross-talk), **sigma check (accuracy condition)** | VL53L0X DS section 2.6.3 |
| VL53L5CX / L7CX | Per-zone target status | see below | UM3038 Table 4 |

VL53L5CX/L7CX per-zone `target_status` codes, the **complete** Table 4 list (UM3038 Rev 2 for the
VL53L7CX, and the identical Table 4 in UM2884 Rev 2 for the VL53L5CX):

| Status | Meaning |
|---|---|
| 0 | Ranging data are not updated |
| 1 | Signal rate too low on SPAD array |
| 2 | Target phase |
| 3 | Sigma estimator too high |
| 4 | Target consistency failed |
| 5 | **Range valid** |
| 6 | Wrap around not performed (typically the first range) |
| 7 | Rate consistency failed |
| 8 | Signal rate too low for the current target |
| 9 | Range valid with large pulse (may be due to a merged target) |
| 10 | Range valid, but no target detected at previous range |
| 11 | Measurement consistency failed |
| 12 | Target blurred by another one, due to sharpener |
| 13 | Target detected but inconsistent data. Frequently happens for secondary targets. |
| 255 | No target detected (only if number of target detected is enabled) |

Statuses 7, 8, 11, 12 and 13 are real and are easy to miss - an abridged copy of this table is the
usual reason a filter written from a blog post lets bad zones through. UM3038 section 5.5 states
verbatim: *"To have consistent data, the user needs to filter invalid target
status. To give a confidence rating, a target with status 5 is considered as 100 % valid. A status of 6
or 9 can be considered with a confidence value of 50 %. All other statuses are below 50 % confidence
level."* A robot that does not filter on status 5 will drive into things while reading plausible
distances.

Practical consequence: **at the edge of the published range the sensor does not report a wrong
distance - it reports nothing.** Range collapse under sunlight shows up as a wall of status-1
("signal rate too low on SPAD array") zones, not as noisy numbers. That is good for safety and bad for
coverage: a sunlit corridor reads as empty space.

### 3.6 The fill-factor trap - the biggest single error in ToF robot design

Every ST range number above **except VL53L1X Table 9** assumes a target that fills the field of view:
verbatim from VL53L5CX section 5.2.1, *"The specified target fills 100 % of the field of view of the
device (in all zones)"*; from VL53L1X section 3.1 item 5d, *"Target covers the full FoV"*; from VL53L0X
Table 11, *"All distances are for a complete Field of View covered (FOV = 25 degrees)"*. VL53L1X
Table 9 is the single exception - its condition line reads *"Target covers partial FoV"*. A cat does
not fill a field of view. Here is
what the field of view actually covers at each distance, and what fraction each target fills:

```
========================================================================================================
D. THE FILL-FACTOR TRAP: ST ranges are quoted for a target that FILLS the FoV
========================================================================================================

  VL53L1X full ROI, 27 deg diagonal (~19x19 deg square)
    range      FoV footprint mm  FoV area m^2      human fill        cat fill      chair fill
    1 ft              103 x 103         0.011           1.000           1.000           1.000
    3 ft              308 x 308         0.095           1.000           0.529           0.169
    5 ft              513 x 513         0.263           1.000           0.190           0.061
    8 ft              820 x 820         0.673           0.468           0.074           0.024
    10 ft           1026 x 1026         1.052           0.299           0.048           0.015

  VL53L5CX, 45 x 45 deg detection volume
    range      FoV footprint mm  FoV area m^2      human fill        cat fill      chair fill
    1 ft              253 x 253         0.064           1.000           0.783           0.251
    3 ft              757 x 757         0.573           0.549           0.087           0.028
    5 ft            1263 x 1263         1.594           0.198           0.031           0.010
    8 ft            2020 x 2020         4.079           0.077           0.012           0.004
    10 ft           2525 x 2525         6.376           0.049           0.008           0.003

  VL53L7CX, 60 x 60 deg detection volume
    range      FoV footprint mm  FoV area m^2      human fill        cat fill      chair fill
    1 ft              352 x 352         0.124           1.000           0.403           0.129
    3 ft            1055 x 1055         1.114           0.283           0.045           0.014
    5 ft            1760 x 1760         3.097           0.102           0.016           0.005
    8 ft            2815 x 2815         7.925           0.040           0.006           0.002
    10 ft           3520 x 3520        12.387           0.025           0.004           0.001
```

Because `f_fill` falls as `1/d^2` once the target is smaller than the FoV, the received signal for a
**fixed-size** target falls as `1/d^4`, not `1/d^2` - the same fourth-power law radar obeys. Setting
`S_min = k*rho*d_cross^2/d^4` equal to the full-FoV limit `S_min = k*rho/d_full^2` gives

**`d_small = sqrt(d_cross * d_full)`**

where `d_cross` is the distance at which the target exactly fills the FoV. Applying that to the ST
numbers:

```
========================================================================================================
E. WHAT FILL FACTOR DOES TO RANGE: signal ∝ rho * f_fill / d^2, and f_fill ∝ 1/d^2
========================================================================================================
  VL53L1X full ROI, 27 deg diagonal (~19x19 deg square)
    human torso 450 x 700 mm cross-over   1668 mm | dark, white 88%                        full-FoV   3600 mm -> real   2450 mm ( 8.0 ft)
    human torso 450 x 700 mm cross-over   1668 mm | dark, grey 17%                         full-FoV   1700 mm -> real   1684 mm ( 5.5 ft)
    human torso 450 x 700 mm cross-over   1668 mm | 200 kcps/SPAD (~100 kLux), white 88%   full-FoV    730 mm -> real    730 mm ( 2.4 ft) (target still fills FoV at the full-FoV limit)
    cat 250 x 200 mm         cross-over    665 mm | dark, white 88%                        full-FoV   3600 mm -> real   1547 mm ( 5.1 ft)
    cat 250 x 200 mm         cross-over    665 mm | dark, grey 17%                         full-FoV   1700 mm -> real   1063 mm ( 3.5 ft)
    cat 250 x 200 mm         cross-over    665 mm | 200 kcps/SPAD (~100 kLux), white 88%   full-FoV    730 mm -> real    697 mm ( 2.3 ft)
    chair leg 40 x 400 mm    cross-over    376 mm | dark, white 88%                        full-FoV   3600 mm -> real   1163 mm ( 3.8 ft)
    chair leg 40 x 400 mm    cross-over    376 mm | dark, grey 17%                         full-FoV   1700 mm -> real    799 mm ( 2.6 ft)
    chair leg 40 x 400 mm    cross-over    376 mm | 200 kcps/SPAD (~100 kLux), white 88%   full-FoV    730 mm -> real    524 mm ( 1.7 ft)

  VL53L5CX, 45 x 45 deg detection volume
    human torso 450 x 700 mm cross-over    677 mm | dark, white 88%                        full-FoV   3600 mm -> real   1562 mm ( 5.1 ft)
    human torso 450 x 700 mm cross-over    677 mm | dark, grey 17%                         full-FoV   1700 mm -> real   1073 mm ( 3.5 ft)
    cat 250 x 200 mm         cross-over    270 mm | dark, white 88%                        full-FoV   3600 mm -> real    986 mm ( 3.2 ft)
    cat 250 x 200 mm         cross-over    270 mm | dark, grey 17%                         full-FoV   1700 mm -> real    677 mm ( 2.2 ft)
    chair leg 40 x 400 mm    cross-over    153 mm | dark, white 88%                        full-FoV   3600 mm -> real    741 mm ( 2.4 ft)
    chair leg 40 x 400 mm    cross-over    153 mm | dark, grey 17%                         full-FoV   1700 mm -> real    509 mm ( 1.7 ft)

  VL53L7CX, 60 x 60 deg detection volume
    human torso 450 x 700 mm cross-over    486 mm | dark, white 88%                        full-FoV   3600 mm -> real   1323 mm ( 4.3 ft)
    cat 250 x 200 mm         cross-over    194 mm | dark, white 88%                        full-FoV   3600 mm -> real    835 mm ( 2.7 ft)
    chair leg 40 x 400 mm    cross-over    110 mm | dark, white 88%                        full-FoV   3600 mm -> real    628 mm ( 2.1 ft)
```

**Read that table as the real answer for a robot.** The advertised "4 m" VL53L1X sees a 40 mm chair
leg at about **1.16 m in a dark room** and **0.52 m in a sunbeam**. The much-loved 8x8 multizone
parts are *worse* at range for small targets, because their wider field of view dilutes the same
laser power over more solid angle.

Two caveats, stated so the model is not over-trusted:

- The model assumes the unfilled part of the FoV returns nothing. In a real room it returns the wall
  behind, and the VL53L5CX and VL53L7CX do multi-target histogram separation per zone, so the *closer*
  target can still be extracted if its signal clears the threshold. The numbers above are therefore a
  **conservative lower bound**, not a hard wall. `INF`
- The per-zone geometry of an 8x8 part means each zone has only 1/64 of the total field. A cat at 3 ft
  fills about 5.6 zones of a VL53L5CX, so per-zone fill is much better than whole-array fill. The
  practical effect sits between the single-zone and whole-array cases. `INF`

Also note the 940 nm reflectance problem: `rho` at 940 nm is **not** visible lightness. Black cotton
denim is often 30-50 % at 940 nm while black leather, black velvet and matte-black ABS can be under
10 %. A robot that navigates by SPAD ToF will fail specifically on dark matte plastics - bin lids,
speaker grilles, pet carriers - rather than on "dark things" generally. `INF`

---

## 4. mmWave FMCW radar

### 4.1 The range equation

The monostatic radar range equation, as published by RFbeam:

```
P_r = (P_t * G_t * G_r * lambda^2 * sigma) / ((4*pi)^3 * R^4 * L)
```

Setting `P_r` equal to a fixed minimum detectable power and solving for `R` gives the only law that
matters for target discrimination:

**`R_max` proportional to `sigma^(1/4)`** - and therefore
**`R_pet / R_human = (sigma_pet / sigma_human)^(1/4)`**.

### 4.2 Radar cross section - measured values, not folklore

```
====================================================================================================
2. RCS REFERENCE VALUES (m^2 and dBsm)
====================================================================================================
  Adult human, JRC measured mean, 23-28 GHz        sigma =   0.3715 m^2 =   -4.30 dBsm   (-4.3 dBsm measured)
  Adult human, JRC measured mean, 28 GHz           sigma =   0.3162 m^2 =   -5.00 dBsm   (-5.0 dBsm measured)
  Adult human, 79 GHz median at 6.2 m              sigma =   0.0776 m^2 =  -11.10 dBsm   (-11.1 dBsm measured, 90% spread -20.7..-4.8)
  Pedestrian, RFbeam vendor range low              sigma =   0.1000 m^2 =  -10.00 dBsm   (0.1 m^2 vendor)
  Pedestrian, RFbeam vendor range high             sigma =   1.0000 m^2 =    0.00 dBsm   (1.0 m^2 vendor)
  Cat / small dog, lane estimate LOW               sigma =   0.0100 m^2 =  -20.00 dBsm   (inferred)
  Cat / small dog, lane estimate HIGH              sigma =   0.0500 m^2 =  -13.01 dBsm   (inferred)

  Geometric sanity check on the pet estimate:
    human frontal projected area  = 1.70 x 0.40 m = 0.680 m^2
    cat   side   projected area   = 0.25 x 0.20 m = 0.050 m^2
    implied backscatter efficiency sigma/A for human at 24 GHz = 0.372/0.680 = 0.546
    same efficiency applied to the cat -> sigma_cat = 0.0273 m^2 = -15.6 dBsm
    human-to-cat RCS ratio = 13.6x = 11.3 dB
```

RFbeam's published table of typical RCS values, verbatim:

| Object | RCS (m^2) |
|---|---|
| Pedestrian | 0.1 .. 1 |
| Bicycle | 0.4 .. 1 |
| Motorcycle | 1 .. 5 |
| Car | 10 .. 50 |
| Truck | 100 .. 200 |

That table **does not include values for dogs, cats, or small animals**. No published measured pet RCS
at 24 or 60 GHz was located in this lane.

Points worth keeping:

- The widely quoted **"human = 1 m^2"** (Analog Devices) is the *upper* end of the RFbeam pedestrian
  band (0.1-1 m^2). The EU Joint Research Centre's controlled 24/77 GHz measurement campaign puts the
  frequency/azimuth-averaged mean at **-4.3 dBsm, about 0.37 m^2**, in the 23-28 GHz band. Use
  0.37 m^2, not 1 m^2. `INF` from a published campaign summary.
- Human RCS at **79 GHz is much lower** than at 24 GHz for a real standing person: a published median
  of **-11.1 dBsm (0.078 m^2)** at 6.2 m, with a 90 % spread of -20.7 to -4.8 dBsm. That **16 dB
  spread** is the pose and aspect fluctuation of a single human body, and it is **larger than the
  entire human-to-pet RCS gap**. This is the key finding for classification: amplitude alone cannot
  separate a human from a pet, because one human's own variation swamps the difference.
- A geometric estimate puts a cat at **-15.6 dBsm (0.027 m^2)**, an **11.3 dB** deficit versus a human.
  The lane brief's 15-20 dB is the pessimistic end; 10-15 dB is better supported.

### 4.3 The arithmetic the brief asked for, explicitly

```
====================================================================================================
3. RANGE EQUATION AND THE FOURTH-ROOT LAW
====================================================================================================
   Pr = Pt Gt Gr lambda^2 sigma / ((4 pi)^3 R^4 L)      ->      R_max ∝ sigma^(1/4)
   R_pet / R_human = (sigma_pet / sigma_human)^(1/4)

     radar rated on a HUMAN |  -10 dB pet |  -15 dB pet |  -20 dB pet |  -25 dB pet
                     3.0 m |      1.69 m |      1.27 m |      0.95 m |      0.71 m |
                     5.0 m |      2.81 m |      2.11 m |      1.58 m |      1.19 m |
                     6.0 m |      3.37 m |      2.53 m |      1.90 m |      1.42 m |
                     8.0 m |      4.50 m |      3.37 m |      2.53 m |      1.90 m |
                    12.0 m |      6.75 m |      5.06 m |      3.79 m |      2.85 m |
                    16.0 m |      9.00 m |      6.75 m |      5.06 m |      3.79 m |
                    25.0 m |     14.06 m |     10.54 m |      7.91 m |      5.93 m |

   Explicit case asked for: a module rated 12 m on a human.
     sigma_pet = 0.05 m^2   ratio to human  0.135 (  -8.7 dB) -> max range  7.27 m ( 23.8 ft)
     sigma_pet = 0.03 m^2   ratio to human  0.081 ( -10.9 dB) -> max range  6.40 m ( 21.0 ft)
     sigma_pet = 0.01 m^2   ratio to human  0.027 ( -15.7 dB) -> max range  4.86 m ( 15.9 ft)
```

**Conclusion: range is not radar's pet problem.** Even at the pessimistic 0.01 m^2, a 12 m human rating
still yields 4.9 m - comfortably beyond the 3.05 m evaluation limit. Across all five evaluation
distances, any commodity 24 or 60 GHz module that detects a human also detects a cat.

What actually stops a hobby radar seeing a pet is the **antenna elevation pattern**, not RCS. A
DFRobot C4001 has a published beam of **100 x 40 degrees**: mounted 600 mm up on the robot and aimed
level, the lower half-power edge reaches the floor at `600 / tan(20 deg) = 1.65 m`. A cat closer than
1.65 m is **below the beam**, and a cat lying down is below it at any range. `CALC`

### 4.4 Range resolution - the number that eliminates 24 GHz ISM radar for this robot

```
====================================================================================================
1. RANGE RESOLUTION dR = c / (2B)
====================================================================================================
  B =  0.25 GHz  ->  dR =   599.6 mm   [24.00-24.25 GHz ISM (LD2410, C4001, RCWL-0516 class)]
  B =  1.00 GHz  ->  dR =   149.9 mm   [60-64 GHz unlicensed, 1 GHz sweep]
  B =  4.00 GHz  ->  dR =    37.5 mm   [60-64 GHz unlicensed, full 4 GHz sweep (IWR6843/IWRL6432)]
  B =  4.00 GHz  ->  dR =    37.5 mm   [76-81 GHz automotive, 4 GHz sweep]

  Robot footprint = 350 mm. A 600 mm range bin is 1.7 robot-widths deep.
```

The HLK-LD2410 manual confirms this directly: **"Sweep Bandwidth 250 MHz"**, **"Distance resolution
0.75 m"**, **"Working frequency 24 GHz ~ 24.25 GHz"**, **"Detection angle +/-60 deg"**, and this
warning, verbatim: *"The theoretical distance accuracy of radar is the result obtained through special
algorithm processing on the basis of the physical resolution of 0.75 meters. Due to the difference of
the target's body shape, state, RCS, etc., the target distance accuracy will fluctuate; at the same
time, the maximum distance will also be slightly fluctuation."*

The 24.00-24.25 GHz ISM allocation is only 250 MHz wide, so **every** 24 GHz ISM module - LD2410,
LD2450, C4001, and the rest - is stuck at roughly a 600 mm physical range cell. A robot 350 mm across
cannot use a 600 mm range cell for collision avoidance. It can use it for "is a person in the room".

TI's SWRA818 note confirms the 60 GHz side: *"range resolution of approximately 5 cm"* with
*"7 GHz of bandwidth"*, and human detection *"up to 5 meters"*.

The DFRobot C4001, for contrast, claims *"a presence detection range of 16 meters and a motion
detection and distance measurement range of 25 meters"* with *"Beam angle: 100*40 deg"* and
*"Operating frequency: 24GHz"*, and *"Distance detection: Range from 1.2 meters to 25 meters"*. Note
the **1.2 m minimum distance** - two range bins. Below 1.2 m the C4001 reports nothing, which is
precisely the zone a 350 mm robot cares about most.

### 4.5 Cross-range resolution - why 24 GHz presence modules cannot localise

```
====================================================================================================
4. ANGULAR (CROSS-RANGE) RESOLUTION OF SMALL MIMO ARRAYS
====================================================================================================
   theta_3dB ~ 2/N rad for an N-element lambda/2 virtual ULA (unwindowed).
   1TX x 1RX (LD2410 class, no angle at all)     -> no angle estimate; single range/Doppler bin only
   2TX x 2RX  (LD2450, 4 virtual)                -> theta_3dB ~  28.6 deg
        cross-range spot at  1 ft =     156 mm
        cross-range spot at  3 ft =     467 mm
        cross-range spot at  5 ft =     778 mm
        cross-range spot at  8 ft =    1245 mm
        cross-range spot at 10 ft =    1557 mm
   3TX x 4RX  (IWR6843 azimuth, 8 virtual used)  -> theta_3dB ~  14.3 deg
        cross-range spot at  1 ft =      77 mm
        cross-range spot at  3 ft =     230 mm
        cross-range spot at  5 ft =     383 mm
        cross-range spot at  8 ft =     613 mm
        cross-range spot at 10 ft =     766 mm
   3TX x 4RX  (IWR6843, 12 virtual)              -> theta_3dB ~   9.5 deg
        cross-range spot at  1 ft =      51 mm
        cross-range spot at  3 ft =     153 mm
        cross-range spot at  5 ft =     255 mm
        cross-range spot at  8 ft =     407 mm
        cross-range spot at 10 ft =     509 mm
```

A cat 250 mm long and a human leg 110 mm wide are both **inside one angular cell** at every distance
beyond 1 ft for every part in this table. Radar's spatial picture of a room is a handful of fat blobs,
not a point cloud.

### 4.6 Micro-Doppler - the only real classification channel

```
====================================================================================================
5. VELOCITY / MICRO-DOPPLER FLOOR
====================================================================================================
   f0=24.12 GHz lambda=12.43 mm  frame 100 ms -> dv = lambda/(2*Tf) =   62.1 mm/s
   f0=60.00 GHz lambda= 5.00 mm  frame 50 ms -> dv = lambda/(2*Tf) =   50.0 mm/s
   f0=60.00 GHz lambda= 5.00 mm  frame 100 ms -> dv = lambda/(2*Tf) =   25.0 mm/s
   A cat's chest wall moves ~1 mm at 0.5-2 Hz; a human chest ~4-12 mm at 0.2-0.5 Hz.
   Both are far below one velocity bin: they are recovered as PHASE, not as a Doppler bin.
```

Radar tells human from pet by *gait*, not by size. A walking human's limb micro-Doppler spans roughly
+/-2 to 3 m/s around a 1.2 m/s torso line with a roughly 1 Hz stride; a trotting cat has a roughly
2.5 Hz stride, much lower torso velocity, and a limb envelope under +/-1.5 m/s. That difference is
real and separable - but it requires a velocity-resolved spectrogram and a trained classifier, and it
disappears the moment the animal stops moving. `INF`

TI states the split explicitly in SWRA818. Its low-power mode filters are listed as *"Location
filtering"*, *"Proximity filtering"*, *"Height filtering"*, *"Doppler filtering: removes stationary and
low-speed reflections"*, and *"Threshold filtering: uses SNR and number of points to filter the signal
from noise"*. Then, only under high-performance mode: *"Classification filtering: uses the motion
signature (micro Doppler) to identify an object and filter"*. The false-detection cause list includes
*"Animals (pets, squirrels, rabbits, etc.)"* and it is the high-performance column that addresses it.

Translation: **a radar that can reject pets is a radar running a full micro-Doppler classifier, not a
$6 presence module.** The LD2410's own description - *"high-sensitivity 24GHz human presence status
sensing module"*, *"can identify human bodies in motion and stationary states"* - makes no pet claim at
all, correctly.

### 4.7 24 versus 60 GHz for a fixed, small antenna aperture

```
====================================================================================================
6. 24 vs 60 GHz LINK BUDGET, SAME PHYSICAL APERTURE
====================================================================================================
   lambda(24.125 GHz) = 12.43 mm ; lambda(61 GHz) = 4.91 mm
   lambda^2 term alone favours 24 GHz by 8.1 dB
   but G ∝ A/lambda^2 twice (Tx and Rx) favours 60 GHz by 16.1 dB for a FIXED aperture
   net for fixed physical aperture: 60 GHz wins by 8.1 dB
   O2 absorption at 60 GHz ~15 dB/km -> over 3.05 m two-way (6.10 m) = 0.091 dB. Negligible indoors.
```

The common claim that "60 GHz has higher path loss so shorter range" is only true at **fixed antenna
gain**. At **fixed physical aperture** - which is what a 350 mm robot actually constrains - 60 GHz
wins by about 8 dB, plus four times the usable bandwidth, plus a quarter-size antenna array. The
60 GHz oxygen absorption line is irrelevant at 3 m (0.09 dB two-way).

For this robot, **60 GHz is the correct radar band and 24 GHz ISM is not**, on range resolution alone.

One physical caveat that applies to both bands: a radome changes the link budget. TI's radome design
guide and Hilink's own section 7 both warn that *"Radar waves will suffer loss when propagated in the
medium. In theory, the higher the frequency, the greater the loss will be."* Hilink recommends the
radome inner surface sit at 1x or 1.5x wavelength (12.4 or 18.6 mm at 24.125 GHz, error +/-1.2 mm) and
the radome thickness be a half wavelength, error +/-20 %. A 3D-printed robot shell that ignores this
will silently eat several dB - which, at the fourth root, costs about 10 % of range per 1.5 dB.

---

## 5. Thermal IR array: the pixel-subtense limit

A thermal array cannot resolve anything smaller than one pixel footprint. Everything about thermal
classification at range follows from that single geometric fact.

Using the flat focal-plane model - field width `W = 2*d*tan(FOV/2)`, pixel pitch `W/N`:

```
============================================================================================================
PIXEL SUBTENSE - flat focal-plane model, w = 2*d*tan(FOV/2), pitch = w/N
============================================================================================================

AMG8833 Grid-EYE  8x8   60 x 60 deg
  range             H field (mm)  V field (mm)  H pitch (mm)  V pitch (mm)   ang pitch H (deg)
  1 ft (305)                 352           352          44.0          44.0                7.50
  3 ft (914)                1055          1055         131.9         131.9                7.50
  5 ft (1524)               1760          1760         220.0         220.0                7.50
  8 ft (2438)               2815          2815         351.9         351.9                7.50
  10 ft (3048)              3520          3520         439.9         439.9                7.50

MLX90640 BAB     32x24  55 x 35 deg
  range             H field (mm)  V field (mm)  H pitch (mm)  V pitch (mm)   ang pitch H (deg)
  1 ft (305)                 318           192           9.9           8.0                1.72
  3 ft (914)                 952           576          29.7          24.0                1.72
  5 ft (1524)               1587           961          49.6          40.0                1.72
  8 ft (2438)               2538          1537          79.3          64.1                1.72
  10 ft (3048)              3173          1922          99.2          80.1                1.72

MLX90640 BAA     32x24 110 x 75 deg
  range             H field (mm)  V field (mm)  H pitch (mm)  V pitch (mm)   ang pitch H (deg)
  1 ft (305)                 871           468          27.2          19.5                3.44
  3 ft (914)                2611          1403          81.6          58.4                3.44
  5 ft (1524)               4353          2339         136.0          97.5                3.44
  8 ft (2438)               6964          3741         217.6         155.9                3.44
  10 ft (3048)              8706          4678         272.1         194.9                3.44
```

Target fill:

```
============================================================================================================
TARGET FILL - how many pixels the target covers (H x V), and solid-angle fill fraction of ONE pixel
============================================================================================================

AMG8833 Grid-EYE  8x8   60 x 60 deg
  target: human torso 450 x 700 mm
    range             px across   px tall  total px  1-px fill frac  apparent dT (K)*
    1 ft (305)            10.22     15.90    162.54           1.000              8.00
    3 ft (914)             3.41      5.31     18.10           1.000              8.00
    5 ft (1524)            2.05      3.18      6.51           1.000              8.00
    8 ft (2438)            1.28      1.99      2.54           1.000              8.00
    10 ft (3048)           1.02      1.59      1.63           1.000              8.00
  target: cat/small dog 250 x 200 mm
    range             px across   px tall  total px  1-px fill frac  apparent dT (K)*
    1 ft (305)             5.68      4.54     25.80           1.000              8.00
    3 ft (914)             1.90      1.52      2.87           1.000              8.00
    5 ft (1524)            1.14      0.91      1.03           1.000              8.00
    8 ft (2438)            0.71      0.57      0.40           0.404              3.23
    10 ft (3048)           0.57      0.45      0.26           0.258              2.07

MLX90640 BAB     32x24  55 x 35 deg
  target: human torso 450 x 700 mm
    range             px across   px tall  total px  1-px fill frac  apparent dT (K)*
    1 ft (305)            45.35     87.35   3961.08           1.000              8.00
    3 ft (914)            15.13     29.15    441.08           1.000              8.00
    5 ft (1524)            9.08     17.48    158.65           1.000              8.00
    8 ft (2438)            5.67     10.93     61.99           1.000              8.00
    10 ft (3048)           4.54      8.74     39.66           1.000              8.00
  target: cat/small dog 250 x 200 mm
    range             px across   px tall  total px  1-px fill frac  apparent dT (K)*
    1 ft (305)            25.19     24.96    628.74           1.000              8.00
    3 ft (914)             8.41      8.33     70.01           1.000              8.00
    5 ft (1524)            5.04      4.99     25.18           1.000              8.00
    8 ft (2438)            3.15      3.12      9.84           1.000              8.00
    10 ft (3048)           2.52      2.50      6.30           1.000              8.00

MLX90640 BAA     32x24 110 x 75 deg
  target: human torso 450 x 700 mm
    range             px across   px tall  total px  1-px fill frac  apparent dT (K)*
    1 ft (305)            16.53     35.89    593.28           1.000              8.00
    3 ft (914)             5.52     11.98     66.06           1.000              8.00
    5 ft (1524)            3.31      7.18     23.76           1.000              8.00
    8 ft (2438)            2.07      4.49      9.29           1.000              8.00
    10 ft (3048)           1.65      3.59      5.94           1.000              8.00
  target: cat/small dog 250 x 200 mm
    range             px across   px tall  total px  1-px fill frac  apparent dT (K)*
    1 ft (305)             9.18     10.25     94.17           1.000              8.00
    3 ft (914)             3.06      3.42     10.49           1.000              8.00
    5 ft (1524)            1.84      2.05      3.77           1.000              8.00
    8 ft (2438)            1.15      1.28      1.47           1.000              8.00
    10 ft (3048)           0.92      1.03      0.94           0.943              7.54

* apparent dT = 8 K true contrast x single-pixel fill fraction (clothed body ~30 C, room ~22 C).
  AMG8833 NETD 0.05 C typ @1 Hz, absolute accuracy +/-2.5 C typ.  MLX90640 NETD 0.1 K RMS @1 Hz.
```

### 5.1 The distance beyond which a human is a single sub-pixel warm smear

For the **AMG8833**, one pixel subtends 7.5 degrees and covers **440 mm** at 10 ft. A 450 mm human
torso is therefore **1.02 pixels wide and 1.59 pixels tall** at 3048 mm.

- **Below 3 ft**: 3.4 x 5.3 pixels - a recognisable vertical warm bar. Human vs pet is possible from
  aspect ratio.
- **At 5 ft**: 2.05 x 3.18 pixels. Aspect ratio survives, detail does not.
- **Beyond about 2.0 m (6.6 ft)**: fewer than 3 pixels tall. The blob is a warm smudge with no shape.
- **At 10 ft**: one pixel wide. **Classification is impossible.** The array reports "something warm in
  that direction", which is exactly what a two-dollar PIR reports.

The Panasonic Grid-EYE datasheet's *"Human detection distance: 7 m or less (reference value)"*, its
*"Viewing angle: Typical 60 deg"*, *"NETD Typ. 0.05 C @ 1 Hz"*, *"Temperature accuracy Typical
+/-2.5 C"* and *"Typical 10 frames/sec or 1 frame/sec"*, and Adafruit's *"can detect a human from a
distance of up to 7 meters (23 feet)"*, are all **detection**, not classification. They are not wrong;
they answer a different question.

The pet case adds a second failure mode. Beyond 5 ft a cat is sub-pixel, so the pixel averages the cat
with the cooler floor behind it and the *apparent* temperature rise falls with fill fraction:
3.23 K at 8 ft, 2.07 K at 10 ft against an 8 K true contrast. That is still far above the
**0.05 C NETD**, so it is detectable - but it is comparable to a sunlit patch of carpet, a laptop
charger, or a radiator, and the AMG8833's **+/-2.5 C absolute accuracy** gives no help in separating
them. A real cat is worse than modelled here, because fur is an insulator: coat surface temperature in
a 22 C room is closer to 26-29 C than to 34 C skin, so the true contrast is nearer 4-6 K and the
10 ft apparent rise is nearer **1.0-1.6 K**. `INF`

### 5.2 The MLX90640 trade, and what 360-degree coverage costs

Melexis publishes the two lens options in Table 15, verbatim: *"MLX90640-ESF-BAA: 110 deg X, 75 deg Y,
central pointing from normal max 5 deg"* and *"MLX90640-ESF-BAB: 55 deg X, 35 deg Y, max 3 deg"*, with
the note *"The specified FOV is calculated for the wider direction, in this case for the 32 pixels"*
and the definition that FOV is the 50 % sensitivity angle for a point heat source. The sensitivity
falls off across the field, so pixels near the edge see a weaker signal than the pixel-subtense
arithmetic alone implies. `DS`

The **55 x 35 degree BAB** part keeps a human at 4.5 x 8.7 pixels and a cat at 2.5 x 2.5 pixels at
10 ft. It is the only thermal option in this study that can still classify at 3 m. But 55 degrees
horizontal needs **7 units** for 360-degree coverage: 7 x $74.95 = **$524.65** (adafruit.com, read
2026-09-12, 4 in stock).

The **110 x 75 degree BAA** part needs only **4 units** (4 x $74.95 = $299.80) but is **out of stock**
(adafruit.com, read 2026-09-12), and its coarser 3.44-degree pitch puts a cat at 0.92 x 1.03 pixels at
10 ft - sub-pixel, the same failure the AMG8833 hits at 5 ft.

The **AMG8833** at 60 degrees needs **6 units**: 6 x $44.95 = **$269.70** (adafruit.com, read
2026-09-12, 57 in stock) - the cheapest 360-degree thermal ring, and the one that gives up
classification beyond about 5 ft.

| Ring option | Units for 360 deg | Total USD (2026-09-12) | Classifies human vs pet out to |
|---|---|---|---|
| AMG8833, 60 deg | 6 | $269.70 | about 5 ft |
| MLX90640 BAA, 110 deg | 4 | $299.80 (out of stock) | about 8 ft, marginal |
| MLX90640 BAB, 55 deg | 7 | $524.65 | 10 ft and beyond |

One further constraint that no datasheet states plainly: **all of these are slow.** AMG8833 runs at
10 fps maximum, and the MLX90640's NETD of 0.1 K RMS is specified at **1 Hz** - its programmable
refresh rate spans 0.5 Hz to 64 Hz, and noise rises with rate (Melexis plots it across Figures 19-23).
A robot moving at 0.5 m/s travels 50 mm per AMG8833 frame and 500 mm per MLX90640 1 Hz frame. Thermal
arrays are a **classification** sensor, not a **collision-avoidance** sensor.

### 5.3 Single-element thermal for comparison

The ST **STHS34PF80** TMOS presence sensor states its range with the condition attached, which is
unusually honest: *"Reach up to 4 meters without lens for objects measuring 70 x 25 cm^2"*, with an
**80 degree field of view**, *"Operating wavelength: 5 um to 20 um"*, *"IR sensitivity: 2000 LSB/C"*,
and *"Programmable ODRs from 0.25 Hz to 30 Hz"*. A 70 x 25 cm object is a human torso. Scale that
to a 25 x 20 cm cat by area (0.05/0.175 = 0.286) and the square-root-of-area law gives about
`4 * sqrt(0.286) = 2.14 m` for a pet, before accounting for the lower coat temperature. `CALC`/`INF`
It gives presence and motion, zero position, and zero classification.

---

## 6. Scanning lidar: reflectance-tolerant, but sliced

### 6.1 Why range is far less reflectance-dependent than SPAD ToF

The RPLIDAR C1 datasheet quotes range **with the reflectivity attached**:

| Item | Value |
|---|---|
| Distance range | White object: 0.05-12 meters (under 70 % reflection); Black object: 0.05-6 meters (under 10 % reflection) |
| Sample rate | 5 kHz |
| Scanning frequency | 8-12 Hz, 10 Hz typical |
| Angular resolution | 0.72 deg typical (0-1.5 deg, can be customized) |
| Accuracy | +/-30 mm |
| Resolution | 15 mm |
| Ambient light limit | **40,000 lux** |
| Degree of protection | IP54 |

Note [1] on that table, verbatim: *"If the target distance is <0.05m or >12m, the lidar can detect and
output point cloud data. Because the detection accuracy cannot be guaranteed, this data is only for
reference."*

A **7x reflectance change costs only 2x in range** (12 m to 6 m). The sqrt(rho) law would have
predicted `12 * sqrt(10/70) = 4.5 m`, so the C1 does *better* than the shot-noise law. Two reasons: the
12 m figure is a specification cap rather than a photon-budget limit, and a scanning lidar concentrates
all its optical power into one narrow beam at a time instead of flood-illuminating a 45-degree cone. A
SPAD flood illuminator must spread the same emitter power over the whole field on every shot.

The ambient number is the decisive one. **40,000 lux** versus the VL53L1X's collapse at an equivalent
of about 25,000 lux (50 kcps/SPAD), and the lidar keeps 6-12 m while the SPAD keeps 1.66 m. A scanning
lidar is the only modality in this study that does not care much about indoor sunbeams. The A1
datasheet makes the mechanism explicit: *"The modulated laser can effectively prevent ambient light and
sunlight during..."* - the beam is modulated and the receiver is synchronous, which a free-running
SPAD histogram is not.

The RPLIDAR A1 datasheet is less rigorous - it gives 0.15-6 m (A1M8-R4 and below) or 0.15-12 m
(A1M8-R5) with the single qualifier *"White objects"* and **no reflectance percentage**, distance
resolution *"<0.5"* mm under 1.5 metres and *"<1% of the distance"* over all distance range, 1 degree
angular resolution at 5.5 Hz scan rate, 8000 Hz sample frequency, scan rate 1-10 Hz. The A1 uses
**triangulation**, not direct ToF, and its own datasheet notes *"the triangulation range system
resolution changes along with distance"* - so its accuracy degrades with range in a way the dToF C1
does not.

### 6.2 The planar-slice problem, which dominates everything else

```
================================================================================================
SCANNING LIDAR: angular sample spacing and hits per target (2-D slice)
================================================================================================

  RPLIDAR A1  1.0 deg @ 5.5 Hz (datasheet Fig 2-1)
    range    arc spacing mm   human leg 110 mm   cat body 250 mm   chair leg 40 mm
    1 ft                5.3               20.7              47.0               7.5
    3 ft               16.0                6.9              15.7               2.5
    5 ft               26.6                4.1               9.4               1.5
    8 ft               42.6                2.6               5.9               0.9
    10 ft              53.2                2.1               4.7               0.8

  RPLIDAR C1  0.72 deg @ 10 Hz (datasheet Fig 2-1)
    range    arc spacing mm   human leg 110 mm   cat body 250 mm   chair leg 40 mm
    1 ft                3.8               28.7              65.2              10.4
    3 ft               11.5                9.6              21.8               3.5
    5 ft               19.2                5.7              13.1               2.1
    8 ft               30.6                3.6               8.2               1.3
    10 ft              38.3                2.9               6.5               1.0

  STL-27L     0.167 deg @ 10 Hz (DFRobot page)
    range    arc spacing mm   human leg 110 mm   cat body 250 mm   chair leg 40 mm
    1 ft                0.9              123.7             281.2              45.0
    3 ft                2.7               41.3              93.8              15.0
    5 ft                4.4               24.8              56.3               9.0
    8 ft                7.1               15.5              35.2               5.6
    10 ft               8.9               12.4              28.1               4.5
```

A 40 mm chair leg draws **0.8 returns** per sweep at 10 ft on an A1 and **1.0** on a C1. Any cluster
filter with a minimum of two points deletes it. The $160 STL-27L (DFRobot, read 2026-09-12,
*"0.03~25m"*, *"0.167 deg @10Hz"*, *"10Hz"*) gives **4.5** returns on the same leg - a 4.5x improvement
that comes purely from angular sampling, not from range.

The geometry that actually decides whether a pet is seen at all:

```
================================================================================================
PLANAR-SLICE MISS GEOMETRY
================================================================================================
  A 2-D lidar mounted at height h sees ONLY the horizontal plane at h (plus beam thickness).
  Beam vertical divergence is NOT published for RPLIDAR A1/C1. Assume 1.0 deg full angle as a
  working figure; slice thickness t = 2*d*tan(0.5 deg):
    1 ft    slice thickness =    5.3 mm
    3 ft    slice thickness =   16.0 mm
    5 ft    slice thickness =   26.6 mm
    8 ft    slice thickness =   42.6 mm
    10 ft   slice thickness =   53.2 mm

  Targets and the mounting heights that see them (robot 350 mm footprint, 600-1200 mm tall):
    cat standing, back at 250-300 mm     sensor height band that sees it: 40-300 mm
    cat lying, back at 120 mm            sensor height band that sees it: 40-150 mm
    small dog, back at 350-450 mm        sensor height band that sees it: 40-450 mm
    human ankle/shin                     sensor height band that sees it: 40-450 mm
    human torso                          sensor height band that sees it: 900-1500 mm
    table top edge at 720 mm             sensor height band that sees it: 700-740 mm
    sofa edge at 400 mm                  sensor height band that sees it: 150-420 mm
    dropped shoe, 100 mm tall            sensor height band that sees it: 40-100 mm
    floor-level cable/threshold, 15 mm   sensor height band that sees it: misses at any practical height
```

There is **no single mounting height** that sees a lying cat (120 mm), a human torso (1000 mm) and a
table edge (720 mm). A 2-D lidar mounted low sees pets and table legs and misses table tops; mounted
high it sees torsos and misses everything the robot will actually hit. This is why every serious robot
vacuum pairs a low 2-D lidar with a forward-facing depth sensor or a bumper.

And the slice carries **no class information at all**. A 110 mm circular return is a human shin, a
table leg, or a cat sitting upright. Lidar answers (a) - obstacle and distance - extremely well, and
contributes nothing to (b), (c) or (d) except through motion tracking of leg-like clusters.

---

## 7. What this means for the robot

1. **No single-modality answer exists.** The capability table has no row that is non-empty across all
   five distances for all four requirements.
2. **Collision avoidance and classification are different problems with different physics, and should
   be bought separately.** Collision avoidance is a 0-1.5 m, fast, reflectance-tolerant problem -
   scanning lidar plus short-mode SPAD ToF. Classification is a 1-3 m, slow, thermal-and-Doppler
   problem - thermal array plus 60 GHz radar.
3. **Short distance mode is undervalued.** VL53L1X short mode holds 1.30-1.36 m from dark to full sun
   (136 cm to 135 cm, Table 4). For a 350 mm robot that needs half a second of stopping distance, a
   rock-solid 1.3 m is worth more than a conditional 3.6 m.
4. **If radar is used, use 60 GHz.** 24 GHz ISM is bandwidth-limited to a roughly 600 mm range cell by
   regulation, which is 1.7 robot-widths. This is not a vendor quality issue; it is the spectrum
   allocation. The C4001's 1.2 m minimum measurable distance compounds it.
5. **If thermal is used for classification, resolution beats field of view.** A 32x24 at 55 degrees
   classifies at 10 ft; an 8x8 at 60 degrees stops classifying at 5 ft. The 55-degree ring costs about
   $525 in 2026-09-12 Adafruit list prices versus $270 for the AMG8833 ring, and buys classification
   out to the full 10 ft.
6. **The honest classification envelope for a sub-$600 sensor suite is roughly 3 ft.** Inside 1 m,
   cheap thermal plus ToF distinguishes human from pet from object with high confidence. Past 2 m it
   degrades to "warm moving thing" plus "obstacle at range R", and past 3 m it degrades to presence.

---

## 8. Confidence register

| Claim | Confidence | Source |
|---|---|---|
| VL53L1X Tables 4, 6, 7, 8, 9 range values; section 3.1 ambient definitions | datasheet-verified | ST **DocID031281 Rev 3**, November 2018 (re-checked 2026-09-12) |
| VL53L0X Table 11 (incl. FOV = 25 deg full-FoV condition), Table 13, RIT/sigma checks | datasheet-verified | ST DocID029104 Rev 1 |
| VL53L5CX Tables 2, 17-22 and section 5.2.1 conditions | datasheet-verified | ST **DS13754 Rev 5** (re-checked 2026-09-12) |
| VL53L7CX Tables 2, 17-18 | datasheet-verified | ST DS13865 Rev 6, March 2023 |
| VL53L5CX/L7CX target_status semantics and confidence weighting | user-manual-verified | ST UM3038 Rev 2 (Sept 2022) Table 4 / section 5.5; identical text in ST UM2884 Rev 2 (Aug 2021) for the VL53L5CX |
| VL53L1X signal threshold 1024 kcps, sigma threshold 15 mm | driver-source-verified | ST ULD API header as shipped by stm32duino, `vl53l1x_class.h` |
| VL53L0X default signal rate limit 0.25 MCPS | **ST-API-source-verified**, not merely vendor page | ST VL53L0X API sets `VL53L0X_CHECKENABLE_SIGNAL_RATE_FINAL_RANGE` to `(FixPoint1616_t)(0.25*65536)`; Pololu's driver comment reads *"Defaults to 0.25 MCPS as initialized by the ST API and this library"* |
| 8x8 to 4x4 is a **4x** zone-count cut giving about **+14 %** dark (saturated at the 4 m ceiling) and **+55 %** ambient range, not a doubling | calculated from ST Tables 17 and 18 | corrected 2026-09-12; the two tables also differ in frame rate (30 Hz vs 15 Hz) |
| kcps/SPAD to lux conversion | datasheet-verified inputs, arithmetic CALC | ST VL53L0X DS note 2; VL53L5CX/L7CX section 5.2.1 |
| Ambient exponent 0.37-0.59; sqrt(rho) fit within 7 % | calculated in this document | `spad.py`, from ST tables |
| Fill-factor `d_small = sqrt(d_cross*d_full)` model | calculated, then inferred to parts | derived here; conservative lower bound |
| AMG8833 60 deg FoV, 8x8, NETD 0.05 C, +/-2.5 C, 10 fps, 7 m human detection | datasheet-verified | Panasonic Grid-EYE AMG88 datasheet |
| MLX90640 110x75 (BAA) and 55x35 (BAB), NETD 0.1 K @1 Hz, 32x24, 0.5-64 Hz | datasheet-verified | Melexis MLX90640 datasheet Rev 12, Table 15 |
| Pixel subtense and target-fill arithmetic | calculated in this document | `thermal.py` |
| Human RCS -4.3 dBsm at 23-28 GHz | inferred from a published measurement campaign summary | EC JRC, JRC78619 |
| Human RCS -11.1 dBsm median at 79 GHz, 90 % spread -20.7 to -4.8 | inferred, single study | 79 GHz measurement report |
| Pedestrian RCS band 0.1-1 m^2; range equation form | vendor-page-verified | RFbeam detection-range article |
| Cat/dog RCS 0.01-0.05 m^2; geometric estimate -15.6 dBsm | **inferred** | computed here; **no measured pet RCS at 24/60 GHz was found** |
| Radar sigma^(1/4) law and all range arithmetic | calculated in this document | `radar.py` |
| HLK-LD2410: 24-24.25 GHz, 250 MHz sweep, 0.75 m resolution, 0.75-6 m adjustable, +/-60 deg, 80 mA | datasheet-verified | Hilink LD2410 manual V1.03, 2022-06-29 |
| DFRobot C4001: 24 GHz, 16 m presence / 25 m motion, 100x40 deg beam, 1.2 m minimum | vendor-page-verified | DFRobot C4001 documentation |
| TI 60 GHz: ~5 cm range resolution, 7 GHz BW, 5 m human, micro-Doppler classification only in high-performance mode | datasheet-verified | TI SWRA818, May 2024 |
| STHS34PF80: 4 m for a 70x25 cm object, 80 deg FoV, 5-20 um, 0.25-30 Hz | datasheet-verified | ST DS13916 Rev 2, July 2023 |
| RPLIDAR C1: 12 m @70 %, 6 m @10 %, 0.72 deg, 40,000 lux, +/-30 mm, IP54 | datasheet-verified | Slamtec C1M1 datasheet rev 1.1, 2024-03-12 |
| RPLIDAR A1: 6 m (R4) / 12 m (R5) white objects, 1 deg @5.5 Hz, triangulation | datasheet-verified | Slamtec A1M8 datasheet rev 2.1, 2018-02-05 |
| Lidar slice thickness (1.0 deg assumed divergence) | **inferred - divergence not published** | computed here |
| Micro-Doppler gait figures for human and cat | **inferred** | no primary source located |
| Prices and stock, all read 2026-09-12 | vendor-page-verified | see next section |

### Prices read 2026-09-12 (USD list, 1 unit)

| Part | Price | Stock | Vendor |
|---|---|---|---|
| Pololu VL53L1X carrier (#3415) | $22.95 | Active and Preferred | pololu.com |
| Pololu VL53L5CX carrier (#3417) | $19.95 | Active and Preferred | pololu.com |
| Pololu VL53L7CX carrier (#3418) | $19.95 | Active and Preferred | pololu.com |
| Adafruit AMG8833 breakout (#3538) | $44.95 | 57 in stock | adafruit.com |
| Adafruit MLX90640 55 deg (#4407) | $74.95 | 4 in stock | adafruit.com |
| Adafruit MLX90640 110 deg (#4469) | $74.95 | **Out of stock** | adafruit.com |
| Adafruit RPLIDAR A1 (#4010) | $99.95 | 19 in stock | adafruit.com |
| DFRobot STL-27L 360 deg dToF lidar | $160.00 | not stated on page | dfrobot.com |

No part in this lane was found marked discontinued or "no longer manufactured". The MLX90640
110-degree variant is out of stock at Adafruit as of 2026-09-12. The VL53L0X remains in production but
is superseded by the VL53L1X for any new design - the VL53L1X datasheet states it is *"Pin-to-pin
compatible with the VL53L0X FlightSense ranging sensor"*.

---

## 9. Open questions this lane could not close

1. **No measured pet RCS at 24 or 60 GHz was found in public literature.** Every pet number in this
   document is a geometric inference. A measured cat or small-dog RCS at 60 GHz would change the radar
   conclusions by up to 6 dB either way - and a 6 dB error moves a 12 m human rating's pet range
   between 4.9 m and 9.8 m.
2. **RPLIDAR A1/C1 beam divergence is not published.** The 1.0-degree assumption drives the
   slice-thickness table. Slamtec support could supply it.
3. **VL53L8CX ranging tables were not obtained.** ST's servers timed out repeatedly and Mouser blocks
   automated fetches; no working mirror of the VL53L8CX datasheet was found. Its published headline
   (4 m, 65-degree diagonal, 60 Hz) suggests it sits between the L5CX and L7CX, but its ranging tables
   are not quoted here and should not be assumed.
4. **No vendor publishes a human-versus-pet confusion matrix.** TI states that pet rejection requires
   high-performance-mode micro-Doppler classification but gives no false-positive rate. Every
   pet-immunity claim in this price class is unverified.
5. **Human and pet micro-Doppler gait envelopes** are quoted from general knowledge, not from a primary
   source read in this lane. They should be confirmed before any classifier design depends on them.

---

## Sources

- [ST VL53L1X datasheet, DocID031281 Rev 3 (Pololu mirror, verified 2026-09-12)](https://www.pololu.com/file/0J1506/vl53l1x.pdf)
- [ST VL53L0X datasheet, DocID029104 Rev 1 (SparkFun mirror)](https://cdn.sparkfun.com/assets/d/f/5/d/6/vl53l0x-sensor-datasheet.pdf)
- [ST VL53L5CX datasheet, DS13754 Rev 5 (Pololu mirror, verified 2026-09-12)](https://www.pololu.com/file/0J1878/vl53l5cx.pdf)
- [ST VL53L7CX datasheet, DS13865 Rev 6 (Pololu mirror)](https://www.pololu.com/file/0J1992/vl53l7cx.pdf)
- [ST UM3038 Rev 2, VL53L7CX ULD user manual (target status Table 4, section 5.5)](https://www.pololu.com/file/0J1993/um3038-a-guide-to-using-the-vl53l7cx-timeofflight-multizone-ranging-sensor-with-90-fov-stmicroelectronics.pdf)
- [ST UM2884 Rev 2, VL53L5CX ULD user manual (identical target status Table 4, section 5.5)](https://www.pololu.com/file/0J1885/um2884-a-guide-to-using-the-vl53l5cx-multizone-timeofflight-ranging-sensor-with-wide-field-of-view-ultra-lite-driver-uld-stmicroelectronics.pdf)
- [ST STHS34PF80 datasheet, DS13916 Rev 2](https://www.st.com/resource/en/datasheet/sths34pf80.pdf)
- [stm32duino VL53L1X driver header, threshold defaults](https://raw.githubusercontent.com/stm32duino/VL53L1X/main/src/vl53l1x_class.h)
- [Pololu vl53l0x-arduino README, signal rate limit default](https://raw.githubusercontent.com/pololu/vl53l0x-arduino/master/README.md)
- [Panasonic Grid-EYE AMG88 datasheet](https://cdn-learn.adafruit.com/assets/assets/000/043/261/original/Grid-EYE_SPECIFICATIONS%28Reference%29.pdf)
- [Melexis MLX90640 datasheet, Rev 12](https://www.melexis.com/en/documents/documentation/datasheets/datasheet-mlx90640)
- [RFbeam, Understanding detection range of radar sensors](https://rfbeam.ch/understanding-detection-range-of-radar-sensors/)
- [EC JRC, Radar Cross Section Measurements of Pedestrian Dummies and Humans in the 24/77 GHz Frequency Bands, JRC78619](https://publications.jrc.ec.europa.eu/repository/handle/JRC78619)
- [Analog Devices, How to Build a 24 GHz FMCW Radar System](https://www.analog.com/en/resources/technical-articles/how-to-build-a-24-ghz-fmcw-radar-system.html)
- [TI SWRA818, How 60GHz Radar Sensors Reduce False Detections for Sensing Applications, May 2024](https://www.ti.com/lit/an/swra818/swra818.pdf)
- [TI mmWave Radar Radome Design Guide](https://www.ti.com/lit/an/swra705/swra705.pdf)
- [Hilink HLK-LD2410 manual V1.03, 2022-06-29](https://www.hlktech.net/index.php?id=988)
- [DFRobot C4001 mmWave presence sensor documentation](https://wiki.dfrobot.com/SKU_SEN0609_C4001_mmWave_Presence_Sensor_25m)
- [Slamtec RPLIDAR C1 datasheet, rev 1.1, 2024-03-12](https://bucket-download.slamtec.com/datasheet/RPLIDAR_C1_Datasheet.pdf)
- [Slamtec RPLIDAR A1 datasheet, rev 2.1, 2018-02-05](https://bucket-download.slamtec.com/datasheet/RPLIDAR_A1_Datasheet.pdf)
- [Pololu VL53L1X carrier, product 3415](https://www.pololu.com/product/3415)
- [Pololu VL53L5CX carrier, product 3417](https://www.pololu.com/product/3417)
- [Pololu VL53L7CX carrier, product 3418](https://www.pololu.com/product/3418)
- [Adafruit AMG8833 breakout, product 3538](https://www.adafruit.com/product/3538)
- [Adafruit MLX90640 55 degree, product 4407](https://www.adafruit.com/product/4407)
- [Adafruit MLX90640 110 degree, product 4469](https://www.adafruit.com/product/4469)
- [Adafruit RPLIDAR A1, product 4010](https://www.adafruit.com/product/4010)
- [DFRobot STL-27L 360 degree dToF lidar](https://www.dfrobot.com/product-2726.html)
