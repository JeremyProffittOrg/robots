# Standalone guide: ST multizone grid time-of-flight

This chapter stands alone. The platform it sizes for is a 350 mm-footprint indoor mobile robot,
600-1200 mm tall, that needs 360 deg obstacle detection and wants to tell a person from a pet.
Everything needed to reach a buying decision is repeated here.

## The latest part is the VL53L9CX, and it is not the one to buy

As of 2026-09-12 the newest ST grid time-of-flight sensor is the **VL53L9CX**, not the VL53L8CX.
The evidence is four independent sources: ST's own press release
([newsroom.st.com p4783](https://newsroom.st.com/media-center/press-item.html/p4783.html)), the ST
product page
([st.com vl53l9cx](https://www.st.com/en/imaging-and-photonics-solutions/vl53l9cx.html)),
independent trade coverage dated 2026-06-22
([CNX Software](https://www.cnx-software.com/2026/06/22/st-vl53l9cx-direct-time-of-flight-3d-lidar-supports-5cm-to-9m-range-2-3k-zones-resolution/)),
and a DigiKey listing for the STEVAL-VL53L9 evaluation board (P/N 29294599, status Active).
Mass production started early July 2026. This is a product, not a rumour.

Two absence findings matter as much as the presence finding.

- **There is no VL53L5CH.** Searches of ST's line, DigiKey and the `stm32duino` GitHub organisation
  return only `VL53L7CH` and `VL53L8CH`. No VL53L5CH product page, datasheet or driver exists.
  Confidence: vendor-page-verified (absence).
- **There is no VL53L10 and no VL53L9CH.** Nothing later than the VL53L9CX was found in any source.
  Treat the VL53L9CX as the end of the line on 2026-09-12.

One sourcing caveat, stated plainly because it changes how much weight each number carries. During
research `st.com` was unreachable from the research host; direct requests returned HTTP 000 and
zero bytes. The VL53L5CX, VL53L7CX, VL53L8CX and VL53L8CH datasheets were therefore read in full
from byte-identical distributor mirrors (Pololu, Farnell, MikroElektronika) and are
**datasheet-verified**. The VL53L9CX datasheet could not be retrieved at all, so every VL53L9CX
figure below is **vendor-page-verified** only.

## The family

| Part | Grid | FoV H x V | Headline range | Host interface | Status |
|---|---|---|---|---|---|
| VL53L5CX | 4x4 / 8x8 | 45 x 45 deg | 400 cm | I2C 1 MHz | Active, stocked |
| VL53L7CX | 4x4 / 8x8 | 60 x 60 deg | 350 cm | I2C 1 MHz | Active, stocked |
| VL53L7CH | 4x4 / 8x8 + CNH | 60 x 60 deg | 350 cm | I2C / SPI | Active |
| VL53L8CX | 4x4 / 8x8 | 45 x 45 deg | 400 cm | I2C 1 MHz / SPI 20 MHz | Active, stocked |
| VL53L8CH | 4x4 / 8x8 + CNH | 45 x 45 deg | 400 cm | I2C 1 MHz / SPI 3 MHz | Active |
| VL53L9CX | 54 x 42 (2268) | 55 x 42 deg | 8.8 m | MIPI I3C / MIPI CSI-2 | Newest, MP July 2026 |

**Every figure in the "headline range" column is unconditioned.** The CX and CH headlines are
dark-room, white-88%-target, inner-zone, 4x4 numbers, and the datasheets publish the conditioned
tables that replace them (below). The VL53L9CX's 8.8 m has no such table behind it at all: ST
publishes no per-reflectance or per-ambient maximum-range data for that part.

**Field of view, stated exactly.** ST prints a *diagonal* FoV on the front page of every VL53
datasheet. That diagonal is a separately measured optical figure, not the geometric diagonal of the
square detection volume, so it cannot be converted into anything and must never be used to size a
ring. The horizontal and vertical figures are the only usable ones: VL53L5CX and VL53L8CX and
VL53L8CH are **45 x 45 deg** horizontal by vertical (63 and 65 deg diagonal); VL53L7CX and VL53L7CH
are **60 x 60 deg** (90 deg diagonal); VL53L9CX is **55 x 42 deg** (71 deg diagonal). For scale, a
true 45 x 45 deg square has a geometric diagonal of 60.7 deg, not 65 deg. The numbers do not agree
because they are not the same measurement.

The VL53L8CX detection volume is characterised, verbatim, against a *"white 88% reflectance
perpendicular target, in full FoV, located at 1 m from the sensor, without ambient light (dark
conditions), with an 8x8 resolution, with a 14% sharpener (default value), in continuous mode, at
15 Hz."* The collector exclusion zone -- the angle from which stray light can reach the array -- is
wider at 57.9 x 57.9 deg.

## Zones, rate and what a frame contains

Every CX and CH part is the same 8x8 SPAD array read out in one of two modes (UM2884 Table 2):

| Resolution | Min ranging rate | Max ranging rate |
|---|---|---|
| 4x4, 16 zones | 1 Hz | 60 Hz |
| 8x8, 64 zones | 1 Hz | 15 Hz |

Default is 4x4 at 1 Hz, and resolution must be set *before* frequency because the legal frequency
range depends on it. **8x8 tops out at 15 Hz. There is no 8x8 fast mode.**

Each zone reports distance, target status, signal, ambient, reflectance, range sigma and a
per-zone firmware motion indicator. Up to **four targets per zone** are available, set by the
`VL53L5CX_NB_TARGET_PER_ZONE` macro in `platform.h` (not through the API); the default is 1. The
default target order is **Strongest**, which is the wrong default for a robot: a dark obstacle at
400 mm in front of a white wall at 2 m reports the *wall* until you call
`vl53l5cx_set_target_order()` with `Closest` or read multiple targets.

## Range, by reflectance and by ambient light

These are the numbers that decide the design. All rows: target fills 100% of the FoV; Munsell
N4.75 (17%), N8.25 (54%), N9.5 (88%); AVDD 3.3 V; 23 degC; **90% detection rate**; 5 kLux realised
as 2 W/m2 target irradiance at 940 nm; no cover glass; crosstalk margin 0 kcps. Datasheet-verified.

**VL53L8CX and VL53L8CH, continuous 8x8 at 15 Hz** (DS14161 Table 17; DS14310 Table 20 is
identical value for value, because the CH differs from the CX only in firmware):

| Target | Zone | Dark typ | Dark min | 5 kLux typ | 5 kLux min |
|---|---|---|---|---|---|
| White 88% | Inner | 4000 mm | 4000 mm | 1550 mm | 1100 mm |
| White 88% | Corner | 3950 mm | 2900 mm | 1400 mm | 1100 mm |
| Grey 54% | Inner | 3300 mm | 2350 mm | 1400 mm | 1000 mm |
| Grey 54% | Corner | 3100 mm | 2100 mm | 1250 mm | 950 mm |
| Grey 17% | Inner | 2450 mm | 1500 mm | 1150 mm | 900 mm |
| Grey 17% | Corner | 1950 mm | 1300 mm | 950 mm | 700 mm |

**VL53L8CX and VL53L8CH, continuous 4x4 at 30 Hz** (DS14161 Table 16; DS14310 Table 19):

| Target | Zone | Dark typ | Dark min | 5 kLux typ | 5 kLux min |
|---|---|---|---|---|---|
| White 88% | Inner | 4000 mm | 4000 mm | 2850 mm | 2850 mm |
| White 88% | Corner | 4000 mm | 4000 mm | 2850 mm | 2700 mm |
| Grey 54% | Inner | 4000 mm | 4000 mm | 2600 mm | 2550 mm |
| Grey 17% | Inner | 4000 mm | 4000 mm | 1650 mm | 1600 mm |
| Grey 17% | Corner | 3950 mm | 3900 mm | 1550 mm | 1500 mm |

The single most important line in this chapter: at 8x8, 15 Hz, against a 17% grey target under
5 kLux ambient, a VL53L8CX **corner** zone is specified at 950 mm typical and 700 mm minimum. A
person in dark trousers, in an ordinary lit room, at the edge of the field, is a sub-metre sensor.
Dropping to 4x4 buys back most of that range and throws away three quarters of the zones.

**VL53L5CX, continuous 8x8 at 15 Hz** (DS13754 Table 18). Only two reflectances are characterised,
and ST footnotes its own 17% grey chart as *"measured 13% in IR at 940 nm"*:

| Target | Zone | Dark typ | Dark min | 5 kLux typ | 5 kLux min |
|---|---|---|---|---|---|
| White 88% | Inner | 3500 mm | 2600 mm | 1100 mm | 950 mm |
| White 88% | Corner | 3100 mm | 1700 mm | 1000 mm | 800 mm |
| Grey 17% | Inner | 1300 mm | 900 mm | 800 mm | 600 mm |
| Grey 17% | Corner | 1100 mm | 600 mm | 650 mm | 400 mm |

**VL53L7CX and VL53L7CH, continuous 8x8 at 15 Hz** (DS13865 Table 18). This is what the wide field
costs:

| Target | Zone | Dark typ | Dark min | 5 kLux typ | 5 kLux min |
|---|---|---|---|---|---|
| White 88% | Inner | 2000 mm | 1700 mm | 500 mm | 400 mm |
| White 88% | Corner | 1900 mm | 1100 mm | 500 mm | 400 mm |
| Grey 54% | Inner | 1600 mm | 1500 mm | 400 mm | 400 mm |
| Grey 17% | Inner | 800 mm | 700 mm | 350 mm | 250 mm |
| Grey 17% | Corner | 750 mm | 450 mm | 250 mm | 200 mm |

The wide FoV is paid for one-for-one in range. **In a lit room the VL53L7CX at 8x8 is a
0.2-0.5 m sensor.** At 4x4/30 Hz it reaches only 500-650 mm in 5 kLux. Six of them give 360 deg of
geometry and almost no range.

Accuracy (VL53L8CX Table 18), 8x8 rows: from 20-200 mm, **+/-11 mm** against a white 88% target in
the dark but **+/-14 mm** against a 17% target under 5 kLux; from 200-4000 mm, **+/-5%** in the dark
at all three reflectances, degrading to **+/-8%** against a 17% target under 5 kLux. Every accuracy
figure carries a reflectance and an ambient-light condition; none of them is a single number. ST
adds, verbatim, that *"the accuracy of the
corner zone data compared to the center 4 zones may degrade by up to 4%"* and that assemblies
should allow *"typically an additional 1~2%"* for PCB tilt and housing.

Power (VL53L8CX): 215 mW in continuous mode at either resolution; **6.7 mW for 8x8 autonomous at
1 Hz**, and 1.6 mW for 4x4 at 1 Hz. That autonomous figure, with a host interrupt on a programmed
distance or motion threshold, is the reason this family suits a battery robot at all.

## The CH histogram variants

The VL53L8CH and VL53L7CH are **firmware variants, not different silicon**. The VL53L8CH is
pin-to-pin compatible with the VL53L8CX and driver compatible with the VL53L7CH, and ST titles its
datasheet (DS14310 Rev 3) *"Artificial intelligence enabler, high performance 8x8 multizone
Time-of-Flight (ToF) sensor."* The CH firmware adds the **compact and normalized histogram (CNH)**:
the raw per-zone return-signal-versus-range profile, on top of all the normal ranging outputs.

| CNH parameter | Value |
|---|---|
| Histogram bin width | 250 ps |
| Bin equivalent range | 37.5 mm |
| Bins in the core histogram | 128 |
| CNH buffer maximum size | 6160 bytes |
| Maximum zones per CNH aggregate | 64 |

This is the only part in the family that carries material and shape information rather than range
alone. A flat cardboard box face normal to the sensor puts essentially all its return into 1-2 bins
(37.5-75 mm of depth spread). A cat is a curved furry body roughly 200-300 mm deep inside one zone
at 2-3 m, so its return spreads over about seven bins with a long low fur tail. A human leg is a
roughly 150 mm cylinder, about four bins. A pet standing in front of a wall shows as two separated
peaks that the processed "distance" output collapses into one number.

The cost is bus time. ST's own Table 18 gives a 64-zone, 18-bin CNH frame as **6108 bytes and 56 ms
of transfer at 1 MHz I2C**, for 15 fps. The VL53L8CH's SPI runs at only 3 MHz against the CX's
20 MHz. **Two CH sensors saturate a 1 MHz I2C bus at 15 Hz. Ten is impossible.** Put CNH on exactly
one sensor, on its own bus.

## The VL53L9CX

Vendor-page-verified throughout; the datasheet was not retrievable.

| Parameter | Value |
|---|---|
| Zones | up to 54 x 42 = 2268 |
| FoV | 55 x 42 deg H x V, software-reducible |
| Range | under 5 cm to 8.8 m, no reflectance or ambient condition published |
| Frame rate | up to 100 Hz of processed data |
| Outputs | depth, 2D IR with and without active illumination, reflectance, confidence |
| Size | 12.8 x 6.1 x 4.6 mm |

Each zone subtends about 1.02 deg horizontally against 5.625 deg for an 8x8 VL53L8CX. That is a
genuine generational jump and it fixes the CX line's worst weakness. It is still the wrong part for
this robot, for four reasons that are each sufficient: it is **MIPI CSI-2 / I3C only**, so it needs
a Linux-class SoC with a camera port per sensor and cannot hang off a microcontroller; the
evaluation board is **$80.39** and the X-NUCLEO-53L9A1 is **$96.44**; both boards read **0 in stock**
at DigiKey on 2026-09-12, with one STEVAL unit due 2026-10-28 and no ETA at all for the X-NUCLEO;
and there is **no microcontroller driver** -- no `stm32duino` repository, no Arduino library, no
CircuitPython driver.

## Integration facts you must budget for

**Firmware upload.** `vl53l5cx_init()` *"copies the firmware (~84 kbytes) to the module by loading
the code over the I2C interface and performing a boot routine"* (UM2884 Rev 2). The image lives in
host flash as a `const` array and **one copy serves every sensor of the same part number**. At 1 MHz
I2C the upload is roughly 0.8-1.0 s per sensor, so ten sensors is an 8-10 second boot unless you use
SPI or parallel buses (calculated). Both Pololu and SparkFun state outright that 8-bit MCUs cannot
run these parts.

**RAM and bus bandwidth.** With one target per zone and all outputs enabled, a
`VL53L8CX_ResultsData` frame is **1357 bytes**. Disabling ambient-per-SPAD, SPADs-enabled,
signal-per-SPAD, range-sigma and reflectance brings it to **397 bytes**. At 1 MHz I2C, nine bits per
byte:

| Configuration | Bytes/frame | Bus time | Sensors at 15 Hz, 80% bus |
|---|---|---|---|
| Full output, 1 target/zone | 1357 | 12.2 ms | 4 |
| Minimal output | 397 | 3.6 ms | 14 |
| CH, 64 zones x 18 bins CNH | 6108 | 56 ms | 1 |

**I2C addressing.** Every part in the family boots at address 0x52 (8-bit form; 0x29 in 7-bit
form). To build a ring you pull down the `LPn` pin of every device except the one being
reprogrammed, call `vl53l5cx_set_i2c_address()`, then raise the pins, repeating per device. **The
new address is volatile and must be re-applied after every power cycle.** That means one host GPIO
per sensor, or an I/O expander at a fixed non-colliding address. This is the most common
integration surprise with this family; put it in the schematic on day one.

**Mutual interference and the real ring refresh rate.** Every unit emits at 940 nm with no
documented coded modulation, and **ST publishes no mutual-interference rejection figure for
co-located units**. The VL53L8CX does carry a `SYNC` pin for frame synchronisation, listed in
Table 15 alongside I2C, SPI and INT and documented in UM3109. The safe architecture is to time-slice
the ring so that sensors with overlapping fields never integrate at the same moment; opposite pairs
can fire together because their fields do not overlap. Twelve sensors in four time slices at 15 Hz
give a full-ring refresh of about **0.27 s**. Size the stopping distance from that number, not from
the 60 Hz headline. Confidence: inferred.

**Cover glass.** ST's histogram algorithms give crosstalk immunity *"above 60 cm"*; below 60 cm the
crosstalk can exceed the correction. Run the Xtalk calibration plugin if the sensors sit behind a
bezel.

**Drivers.**

| Platform | Support | Last touched |
|---|---|---|
| ST ULD (bare C) | UM2884 L5CX, UM3109 L8CX, UM3183 L8CH | reference, BSD-3 |
| STM32Cube | `STMicroelectronics/x-cube-tof1` | 2025-04-03 |
| Arduino | `stm32duino/VL53L8CX`, `VL53L8CH`, `VL53L7CX`, `VL53L7CH`, `VL53L5CX` | 2026-07-01 down to 2023-08-23 |
| CircuitPython | `sensebox/CircuitPython_VL53LxCX`, community, no Adafruit driver | 2025-09-19 |
| Linux | ST publishes a driver; no mainline IIO driver confirmed (unverified) | -- |

The maintenance signal is worth reading: the VL53L8CX Arduino library was updated 2026-07-01, the
VL53L5CX library not since 2023-08-23.

## Where to buy, prices read 2026-09-12

| Product | Vendor | SKU | Price USD | Stock |
|---|---|---|---|---|
| VL53L5CX carrier | Pololu | 3417 | 19.95 | Active and Preferred |
| VL53L7CX carrier | Pololu | 3418 | 19.95 | Active and Preferred |
| VL53L8CX carrier | Pololu | 3419 | 24.95 | Active and Preferred |
| Qwiic ToF Imager L5CX | SparkFun | SEN-18642 | 32.50 | Backorder |
| Qwiic Mini ToF Imager L5CX | SparkFun | SEN-19013 | 25.95 | In stock |
| SATEL-VL53L8 | DigiKey | 497-SATEL-VL53L8-ND | 32.95 | 190, 13 wk lead |
| VL53L5CX-SATEL | DigiKey | 497-VL53L5CX-SATEL-ND | 22.70 | 437, 51 wk lead |
| X-NUCLEO-53L8A1 | DigiKey | 497-X-NUCLEO-53L8A1-ND | 38.24 | 40, 4 wk lead |
| VL53L8CX bare chip | DigiKey | VL53L8CXV0GC/1 | 8.77 | listed |
| STEVAL-VL53L9 | DigiKey | 29294599 | 80.39 | 0, 1 due 2026-10-28 |

**Adafruit stocks no multizone grid part.** A search on 2026-09-12 returns only the single-zone
VL53L0X, VL53L1X, VL53L4CD, VL53L4CX and VL6180X. No VL53L8CH or VL53L7CH price is published by any
source read. Nothing in the family is discontinued or NRND, but "Active" is not "buyable": note the
51-week lead behind the VL53L5CX-SATEL stock and the SparkFun backorder.

## On a 350 mm robot

**Sensor count.** The naive arithmetic 360 / 45 = 8 is wrong. The sensors sit on the body skin, not
at the robot's centre, so with a 175 mm body radius and spacing exactly equal to the FoV the
adjacent edge rays are *parallel* and the blind wedge between them never closes. Computed by ray
intersection from the datasheet FoV figures:

| Sensor | FoV H | N | Spacing | Seam closes at | Blind slot |
|---|---|---|---|---|---|
| VL53L8CX | 45 deg | 8 | 45.0 deg | never | 134 mm, permanent |
| VL53L8CX | 45 deg | 12 | 30.0 deg | 513 mm | 338 mm deep |
| VL53L8CX | 45 deg | 16 | 22.5 deg | 343 mm | 168 mm deep |
| VL53L7CX | 60 deg | 6 | 60.0 deg | never | 175 mm, permanent |
| VL53L7CX | 60 deg | 10 | 36.0 deg | 421 mm | 246 mm deep |

**Twelve VL53L8CX is the buildable ring.** Ten VL53L7CX would also close, more tightly and for
$199.50 against $299.40, but its 5 kLux 8x8 range against a 17% target is 250-350 mm versus the
VL53L8CX's 950-1150 mm. A ring you cannot use in a lit room is not a ring. Toeing each sensor
outward a few degrees shortens the closure distance substantially and is the cheapest fix the
mechanical design can offer.

Note what the seams are made of. Two adjacent fields meet at their corner zones, and the corner zone
is the weak zone: in the 8x8 table above, under 5 kLux against a 17% target, the VL53L8CX corner is
specified at 950 mm typical against the inner zone's 1150 mm, and ST states corner accuracy may
degrade by up to 4% against the centre four zones. The ring is worst exactly where two sensors hand
over.

**Height and tilt.** Mount the ring at **300 mm with the axes horizontal**. At 45 deg vertical the
8x8 row centre elevations run -19.9, -14.5, -8.8, -3.0, +3.0, +8.8, +14.5, +19.9 deg. From 300 mm,
rows 0-2 strike the floor at 0.88, 1.20 and 1.96 m slant range, which gives a stable floor baseline:
a return shorter than baseline is an obstacle standing on the floor, and a return longer or invalid
is a step down. That is free and robust. The price is that the top of the field at 1.5 m range is
only **921 mm above the floor** -- a standing adult's head and shoulders are outside the frame at
every useful range. Tilting the ring up 10-15 deg recovers height at the cost of the floor baseline.
Do not try to do both with one ring; add a second sensor higher up instead.

**What an adult and a cat look like.** Zone boundaries are linear in tangent space, so at 8x8 a
45 x 45 deg part has a zone width of 0.10355 x range:

| Range | Zone size | Adult torso 450 mm | Adult height 1700 mm | Cat height 250 mm | Cat length 500 mm |
|---|---|---|---|---|---|
| 1 ft, 305 mm | 31.6 mm | fills all 8 | fills all 8 | 7.9 rows | fills all 8 |
| 3 ft, 914 mm | 94.7 mm | 4.8 col | fills all 8 | 2.6 rows | 5.3 col |
| 5 ft, 1524 mm | 157.8 mm | 2.9 col | fills all 8 | 1.6 rows | 3.2 col |
| 8 ft, 2438 mm | 252.5 mm | 1.8 col | 6.7 rows | 1.0 row | 2.0 col |
| 10 ft, 3048 mm | 315.6 mm | 1.4 col | 5.4 rows | 0.8 row | 1.6 col |

Read that table together with the range tables above. At 1 ft everything fills the frame and there
is no silhouette at all, only a distance field: emergency-stop range. At 3-5 ft both angular
resolution and range performance are simultaneously adequate, and this is the only working envelope.
At 8-10 ft a cat is one zone or less -- and, more to the point, at 8x8 under 5 kLux against a 17%
target the sensor is specified to 950-1150 mm, so **a cat at 8 ft in a daylit room does not appear
at all**. The honest statement is "no detection at 8 ft in daylight; one zone at 8 ft in a dark
room".

**Can the grid silhouette alone classify human, pet and box? No.** Four independent reasons, each
sufficient. Vertical truncation: from any height a 350 mm robot can carry, a standing human's head
is outside the 45 deg vertical field inside 3 m, so height -- the most discriminative feature -- is
not measurable, only "taller than the frame". Angular starvation: a pet is 1-2 zones beyond 2.4 m,
and two zones cannot carry shape. Reflectance confound: whether the sensor reports at all depends
strongly on reflectance and ambient light, so a black cat and no cat look identical in a lit room at
2 m; absence of return is not absence of target. Static ambiguity: a sleeping cat, a backpack and a
cardboard box produce the same 2 x 3 blob.

What does work, in priority order: **height above a calibrated floor plane** (pet if the cluster
maximum is under 450 mm, human if over 900 mm), which needs the target's top inside the FoV and so
needs a higher or tilted sensor; the **per-zone motion indicator**, initialised with
`vl53l5cx_motion_indicator_init()`, which is free, runs in sub-10 mW autonomous mode and is the
correct animate-versus-inanimate primitive; **temporal cadence** (a walking human's leg zones
oscillate at roughly 1.8-2.2 Hz, a trotting cat at 3-5 Hz -- inferred, ST publishes no gait data), as
confirmation only; and the **CNH histogram**, which is the one feature that can say "box" rather
than merely "not moving". Everything that falls outside the human and pet branches must still raise
an obstacle, because avoidance can never depend on classification succeeding.

## Verdict

**Buy it for:** a dense near-field obstacle and floor-plane sensor at 0.3-1.5 m, in a ring, on a
32-bit host. Twelve VL53L8CX at 300 mm, 8x8 at 15 Hz, minimal output mode, target order `Closest`,
four interference time slices, about $300 of sensors. Buy one VL53L8CH for a forward classification
head at about 900 mm on its own I2C bus, where the CNH histogram supplies the box-versus-body
discrimination the grid cannot. Use the ring's autonomous mode at 1 Hz with thresholds on the motion
indicator as an always-on presence wake-up: about 80 mW for all twelve.

**Do not buy it for:** room-scale sensing, outdoor or conservatory use (ST characterises only 0 and
5 kLux; direct sunlight is 100-120 kLux and is **not published**), dark-target detection beyond
about a metre in a lit room, glass or mirrors (a 940 nm dToF ranges straight through a window --
**not published**), or any ring built on the assumption that eight sensors cover 360 deg. Do not buy
the VL53L9CX for this robot: it needs a MIPI CSI-2 host, both evaluation boards are at zero stock,
and no microcontroller driver exists. Design it in for 2027.

**The one thing that will disappoint you:** it is not a depth camera. An 8x8 zone subtends 5.625 deg,
so the "image" is 64 blurred distance averages, not a picture -- and the 400 cm on the box is a
dark-room, white-target, inner-zone, 4x4 number that becomes 950 mm at the corner against dark
clothing in an ordinary lit room. Anyone expecting a silhouette they can classify will get a
handful of blobs whose most reliable feature is that they are moving.
