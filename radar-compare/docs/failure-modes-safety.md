# Failure modes and safe behaviour

A single-modality perimeter system will eventually hit something. Every candidate sensor has at
least one **fail-to-danger** mode, where it reports "clear" while a person, a pet or a stair edge is
there, and each has one physics cause, so a second sensor of the same physics does not remove it.
Nothing here is safety-rated: a VL53L5CX, an RPLIDAR C1, an LD2410 and an MLX90640 are sensors, not
electro-sensitive protective equipment. Each has one output, an undeclared failure behaviour, and a
response time that varies with the target.

## The failure catalogue

### Time-of-flight (VL53L0X / L1X / L5CX / L7CX)

Measured values are from Caroleo, Albini and Maiolino, Sensors 26(5):1639, 2026
([MDPI](https://www.mdpi.com/1424-8220/26/5/1639)).

| Failure | Cause and condition | Mitigation |
|---|---|---|
| Dark absorbing surfaces | Measured, black vinyl: **18.8 % valid returns at 25 cm, 20.3 % at 40 cm, 34.4 % at 60 cm**; deviation on a black board peaks near 50 mm past 400 mm. | Never read "no return" as "clear". Use the per-zone `target_status`; slow as valid zones fall; cover with radar. |
| Mirrors and glass | Vendor-stated: through a transparent barrier it ranges **to the barrier**; a 45 deg mirror returns the folded path, so the corridor seems to continue ([US10594920B2](https://patents.google.com/patent/US10594920B2/en)). | One forward ultrasonic, the one modality that sees glass reliably; lidar return intensity can also flag it. Map mirrors and glass doors as keep-out zones. |
| Direct sunlight | Measured: 270 to 0.5 lux negligible, but a **500 W halogen at about 3 klux** drove rejection to almost **45 %**. A VL53L1X at 14 to 93.6 klux gave **33 % useful data** ([ST Community](https://community.st.com/t5/imaging-sensors/has-anyone-tested-the-vl53l1x-to-measure-pastures-pointing-down/td-p/70905)). ST publish 0 and 5 klux only. | Indoor duty. Treat a sunlit patch or patio door as a blind patch, not free space. |
| Cover-glass crosstalk | Vendor-stated: immune beyond 60 cm, but **below 60 cm crosstalk can exceed the true return** ([AN5856](https://www.st.com/resource/en/application_note/an5856-guidelines-for-the-cover-glass-of-the-vl53l5cx-timeofflight-8x8-multizone-sensor-with-wide-field-of-view-stmicroelectronics.pdf)) -- the band the protective field occupies. | Calibrate with the final cover glass fitted, again after any shell change. Keep the AN5856 air gap. |
| Dusty or greasy window | Vendor-stated: grease on the cover glass raises crosstalk, so day-one calibration drifts. | Track baseline crosstalk on a clear bearing; angle the window down so dust sheds. |
| Retroreflectors | Datasheet-verified: certified practice adds a `Z_refl` term unless retroreflectors are excluded ([Banner AG4](https://info.bannerengineering.com/cs/groups/public/documents/literature/147900.pdf)). Hi-vis tape and reflective collars saturate a SPAD. | Add **Z_refl = 200 mm** in a home. |
| Multipath | Inferred: in a corner two surfaces return a path longer than either. Magnitude here is **not published**. | Reject zones beyond the geometric maximum for their bearing; one odd zone among consistent neighbours is suspect. |
| Thermal drift | Measured: the part self-heats to **52 deg C after about 900 s**; within-frame variability is **0.5 to 2 mm**. | Calibrate warm, not cold. Allow 15 min before trusting sub-centimetre accuracy. |

The safety lane calls this part "65 deg diagonal". Prefer the catalogue, **45 x 45 deg horizontal by
vertical, 63 deg diagonal** (VL53L7CX **60 x 60 deg, 90 deg diagonal**), and quote the horizontal
figure: the diagonal is separately measured and cannot be converted.

### mmWave radar (24 GHz LD2410 class, 60 GHz IWR6843 class)

| Failure | Cause and condition | Mitigation |
|---|---|---|
| Ego-motion clutter | Measured: a moving radar gives every static return a Doppler shift, so every wall reads as moving ([EM-Fall](https://arxiv.org/html/2606.11109)). | Subtract ego-Doppler from odometry and IMU. Real signal work, not a config flag. |
| Metal ghosts | Measured: reflective static objects create **multipath and shadow ghosts**, placing false targets further away than the real one ([PMC12158235](https://pmc.ncbi.nlm.nih.gov/articles/PMC12158235/)). | Require track persistence; drop tracks outside known room bounds. Ghosts cost availability, not safety. |
| Vibration | Measured: a 60 GHz radar resolves micron-scale motion ([arXiv 2107.10993](https://arxiv.org/pdf/2107.10993)), and the drivetrain is inside that sensitivity; TI warn that strong vibration or moving debris needs filtering ([TI SWRA818](https://www.ti.com/lit/ab/swra818/swra818.pdf)). | Isolate the module; notch motor and gearbox frequencies; validate with the drive running. |
| Fans and curtains | Vendor-stated: fan blades give Doppler signatures like human motion, and fabric in an air current triggers alarms. | Range-Doppler filtering; reject fixed-position periodic returns. |
| Wall penetration | Vendor-stated: the LD2410 detects a person **through two layers of sheetrock**, and through panelling **up to 5 cm** ([ESPHome](https://www.sudo.is/docs/esphome/components/ld2410/)). A moving robot cannot tune a fixed gate. | Range-gate hard, or use 60 GHz: TI state higher absorption and **reduced wall penetration**. |
| Blind to a still person | Vendor-stated: detection then rests on respiration and heartbeat signatures, with a **1 to 2 s dwell**. | Never let radar be the last thing between the robot and a person. |
| Pets read as humans | Vendor-stated: TI list pets and small animals as motion signatures resembling human presence; removing them takes a trained non-human filter, not a threshold. | Treat a moving thing at pet height as stop-and-yield, not as a classification to settle before braking. |

### Thermal arrays (MLX90640 class)

| Failure | Cause and condition | Mitigation |
|---|---|---|
| Ambient near body temperature | Vendor-stated: person logic keys on **35 to 40 deg C**; the part is **+/-2 deg C over 0 to 100 deg C** ([Adafruit 4407](https://www.adafruit.com/product/4407)). At 35 deg C ambient a clothed person sits inside the error bar, and 40 deg C is ISO 3691-4's own declared short-term ambient maximum, so the failure sits inside the standard's operating envelope. | Corroborating channel only, allowed to fail silent. Threshold on the scene median. |
| Sun-warmed floor | Vendor-stated: heat sources degrade performance. A sunlit rug at 38 deg C reads as a person. | Require shape and motion consistency; 32x24 can reject a large uniform blob. |
| Glass opacity | Vendor-stated: optical glass is **opaque at 8 to 14 microns**; LWIR needs germanium, zinc selenide or silicon. | No normal shell window. Budget a germanium aperture or an open hole, and its cleaning. |
| Slow frames | Datasheet-verified: 4 or 8 Hz on I2C for noise. Chain latency **255 ms at 8 Hz, 380 ms at 4 Hz**; at 4 Hz and 0.5 m/s separation is **1060 mm**. | Warning field and classification only, never the stop path. |
| Pets too small at range | Inferred: a 32x24 array over 55 deg puts a 300 mm cat at 1 m across 2 to 3 pixels, and fur insulates, so the coat surface is much cooler than the core. | Expect no pet detection beyond about **1.5 m**. Thermal sees pets at close range only. |

### PIR

Vendor-stated: two pyroelectric elements cancel in a stable scene, and the chain responds only to
changes faster than about 1 to 2 s, so **a motionless person is invisible by design**. Warm air from
a vent moves infrared energy across a zone boundary and triggers falsely
([Industrial Monitor Direct](https://industrialmonitordirect.com/blogs/knowledgebase/pir-motion-sensor-false-triggers-industrial-application-troubleshooting)).
Inferred: on a moving robot the differential principle fires continuously. **PIR is disqualified as
a safety sensor**; it is a wake-from-sleep trigger while parked.

### 2D lidar (RPLIDAR A1 / C1 class)

| Failure | Cause and condition | Mitigation |
|---|---|---|
| Planar blind slice | Inferred from datasheet geometry. Below the plane: a cat lying flat, a toy, a step edge. Above it: a table top, an open drawer, a 900 mm counter overhang. Certified practice keeps the plane below **200 mm**. | Insufficient alone on a 600 to 1200 mm robot. Add a downward-tilted ToF array below, and an upward element for overhangs. |
| Black absorbing surfaces | Datasheet-verified by omission: the A1M8-R4 range of 0.15 to 6 m (0.15 to 12 m on the R5) is qualified **"White objects"**; low-reflectance range is **not published**. | As for ToF. IEC 61496 Type 3 closes this gap; a hobby lidar never proves it. |
| Dust and window film | Datasheet-verified: Type 3 devices must prove resistance to dirt, backgrounds and obstruction. | Scheduled cleaning, plus a self-test on a known static feature's return intensity. |
| Shadows and mutual interference | Datasheet-verified: certified practice makes the installer remove the shadow effect and needle- or cone-shaped field artefacts, and offset two scanners **100 mm or more** vertically, or shield them ([Banner AG4](https://info.bannerengineering.com/cs/groups/public/documents/literature/147900.pdf)). A pillar or a table leg casts a radial shadow. | Use more than one sensor position; never claim 360 deg from a single vantage point. |
| Eye safety | Datasheet-verified: **Class I**, 785 nm typical, 3 mW typical and 5 mW peak maximum, per 21 CFR 1040.10 and 1040.11 with Laser Notice 50. | Safe as supplied. Replacing the housing or driving the emitter from your own firmware voids it. |

### Ultrasonic

Ultrasonic is here because it answers glass and mirrors, so its own failures must be stated.
Vendor-stated: soft materials absorb sound, and most HC-SR04 units are unreliable on soft, uneven
targets such as people beyond about **1 m**, where the successful-measurement rate falls below
**50 %**. Angling the sensor more than about **15 deg** off perpendicular removes the echo, and an
object closer than **2 cm** returns 0 or an erratic reading. Two units fired together saturate each
other, so a **33 ms** interleave is needed and eight sensors round-robin take **264 ms**, about
3.8 Hz ([Last Minute Engineers](https://lastminuteengineers.com/arduino-sr04-ultrasonic-sensor-tutorial/)).
That latency is fatal in the stop path. Use ultrasonic for hard specular targets only -- glass,
mirrors, gloss doors -- in the warning field, and read a missing echo as "unknown", never "clear".

### Failure direction

**Fail-to-danger** modes report clear when occupied: a black sock to a ToF, a still person to a
radar, a cat under the lidar plane. Each needs a second modality with different physics.
**Fail-to-safe** modes report occupied when clear: radar ghosts, PIR on a draught, a dark rug read
as a cliff. Those cost availability only. So: **OR the stop signals, AND the clear signals.** Any
sensor may stop the robot; all must agree before it resumes.

## Safe behaviour

### The standards worth knowing

**ISO 13482:2014** classifies a 350 mm household machine as a *mobile servant robot*. It gives no
number for how hard a robot may hit a person, only a process: risk estimation per ISO 12100, then
inherently safe design before safeguarding, with software limits on space, speed and force and a
mandatory protective stop. The often-cited line that the standard admits no injury limits exist
**could not be confirmed at a primary source**; treat it as unverified.

**ISO 3691-4** carries the usable numbers. Clause 4.8.2 requires that trucks *"shall stop before
contact between the rigid parts of the truck or load and a stationary person"*
([TUV Rheinland](https://www.tuv.com/content-media-files/master-content/services/industrial-services/pdf/tuv-rheinland-automatic-guided-vehicles-whitepaper-en_neu.pdf)),
replacing EN 1525's weaker wording, which required only a signal enabling a stop. Personnel
detection and braking must both reach **PL d**, implying a Category 3 redundant architecture. Keep
**0.3 m/s**, the speed accepted when personnel detection is muted, with floor marking required in
the same row. Those Annex A values are verified against the **2020 first edition**, not the 2023
text, whose free preview stops at Clause 3.

**ANSI/A3 R15.08** is the North American analogue. Part 1 (R15.08-1-2020) covers the vehicle,
Part 2 (ANSI/A3 R15.08-2-2023) the system and the application, and Part 3, for users, is in
preparation. It separates an AGV, which follows a fixed guide path, from an AMR, which generates
its path from the environment; a household robot is an AMR. Its numeric zone and stopping values
are paywalled and **not published** in any free source.

**IEC 61496** governs the sensor as a safety device. A safety laser scanner is Type 3 and must
detect **1.8 % reflectance minimum** in its protective zone; the certified Keyence SZ-V declares
minimum detectable objects of 20, 30, 40, 50, 70 or 150 mm, depending on the setting, at
*"Reflectance 1.8 % min."*
([Keyence](https://www.keyence.com/products/safety/laser-scanner/sz-v/specs/)). That is why a
certified scanner sees a black sock and a VL53L5CX does not. The same sheet requires **20 % or more
in the warning zone**, so even certified hardware degrades on dark targets in the slow-down tier.

**Protective versus warning field.** The warning field is outer and triggers a non-safety reaction:
slow, announce, illuminate. The protective field is inner and triggers the stop within the declared
response time. **Speed and separation monitoring** ties them to motion: the protective field must be
at least the stopping distance, and must grow with speed. The builder's version is three speed
tiers, each with its own derived polygons.

### Stopping distance

The computed appendix carries the tables; two facts govern them. The deceleration ceiling is
**tip-over, not traction**: 175 mm from centre to leading edge caps braking at **2.86 m/s2** with
the centre of gravity at 600 mm, and **5.72 m/s2** at 300 mm. And the closing speed is not the
robot's: ISO 13855 uses **K = 1600 mm/s** for a walking person, so a robot at 0.5 m/s closes at
**2.1 m/s**. Separation including that approach term, at 2.0 m/s2 with 100 mm measurement and 100 mm
degradation allowances, inferred from datasheet-verified frame rates:

| Sensor chain | Reaction | S at 0.3 m/s | S at 0.5 m/s | S at 1.0 m/s |
|---|---|---|---|---|
| VL53L5CX, 60 Hz, 4x4 | 97 ms | 406 mm | 466 mm | 701 mm |
| VL53L5CX, 15 Hz | 147 ms | 501 mm | 571 mm | 831 mm |
| RPLIDAR C1, 15 Hz | 167 ms | 539 mm | 613 mm | 883 mm |
| LD2410 or IWR6843 | 200 ms | 602 mm | 682 mm | 970 mm |
| MLX90640, 4 Hz | 380 ms | 944 mm | 1060 mm | 1438 mm |
| Certified scanner | 120 ms | 450 mm | 514 mm | 762 mm |

In protective-field form a VL53L5CX ring at 15 Hz and 0.5 m/s needs **386 mm**, or **586 mm** with
the retroreflector adder; adding the 175 mm half-width, the sensor must see reliably to **561 mm**,
and to **822 mm** at 1.0 m/s. Measure your own braking distance and substitute it.

**Classification must never gate the stop.** With the warning field at twice the protective field,
the gap between edges is **167 to 323 ms** for a moving target. A 4 Hz thermal frame is 250 ms; a
micro-Doppler classifier needs 1 to 2 s. Neither fits. Stop on geometry, using the fastest and
dumbest sensor available, and let classification modulate behaviour after the stop. A design that
identifies before it brakes is a design that hits people.

**Compliance is cheap and not optional.** A 15 kg robot at 1.0 m/s with a rigid shell delivers about
**1500 N** mean into a shin, against the ISO/TS 15066 transient limit of **130 N** for a lower leg.
At 0.5 m/s with a **50 mm** crushable bumper it delivers **38 N**. Those are collaborative-robot
human limits, the nearest published tolerance data; no pet limit exists.

### Cliff detection is separate and mandatory

A horizontal scanner at 150 to 200 mm sees nothing at a stair nosing: the floor simply stops. Travel
after the edge is seen, at 3.0 m/s2 (inferred):

| Speed | 50 ms loop | 100 ms loop | 150 ms loop | 250 ms loop |
|---|---|---|---|---|
| 0.3 m/s | 30 mm | 45 mm | 60 mm | 90 mm |
| 0.5 m/s | 67 mm | 92 mm | 117 mm | 167 mm |
| 1.0 m/s | 217 mm | 267 mm | 317 mm | 417 mm |

At 1.0 m/s every row exceeds the 175 mm half-footprint: the robot goes over at every plausible
latency. At 0.5 m/s and 100 ms it must look at least **92 mm** ahead of the front contact patch, and preferably 150 mm.
Use **four to six downward ToF sensors at 50 Hz or better**, wired so a lost reading counts as a
cliff. Downward ToF measures a distance, so a black floor still returns a range; reflective IR is
intensity-only and is the classic failure. **Never disable cliff detection to cure a dark-rug false
positive.** That turns a nuisance into a fall.

### The minimum set, and what a thinner one hits

Below this the robot will eventually hit something: a 0.5 m/s speed cap, dropping to 0.3 m/s in
unmapped or occupied space; a 20 to 50 mm compliant leading surface over a bumper switch; four to
six downward cliff sensors; a 360 deg geometric field from a six to eight module ToF ring, or lidar plus a ToF array; a
physical emergency stop; and two-tier speed-dependent field logic. Worth adding: 60 GHz radar for
presence, never 24 GHz; one or two forward ultrasonic sensors for glass, warning field only, since
an eight-sensor round-robin at a 33 ms interleave takes 264 ms; a thermal array for classification
after the stop.

- **Lidar only.** A cat asleep on its side at 120 mm is below the plane, as are a black boot, a
  glass table leg and a stair edge.
- **ToF only.** A person in black jeans at 600 mm returns valid data in under a fifth of zones. The
  robot reads an empty corridor and walks into a shin at about 250 N.
- **mmWave only.** A person still in a doorway while the robot moves: ego-Doppler swamps the return,
  micro-motion needs 1 to 2 s, the budget is 184 ms. Meanwhile it brakes for a fan two rooms away.
- **Thermal only.** At 35 deg C indoors the contrast is inside the +/-2 deg C error bar.
- **Ultrasonic only.** A human in a wool coat at 1.2 m is detected under half the time.
- **PIR only.** Disqualified.

You will not reach PL d with uncertified parts. Use the industrial arithmetic anyway, adopt the
Z-factor discipline at the larger hobby values, cap speed so residual risk stays small when
detection fails completely, and test the adversarial set: a black sock, a mirror, a glass door, a
sunlit patch, a 120 mm sleeping-cat mannequin, and a person standing still in black clothing.
