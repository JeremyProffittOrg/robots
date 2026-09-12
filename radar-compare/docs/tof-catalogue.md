# Time-of-flight catalogue: every Adafruit part

Adafruit sells no multizone time-of-flight sensor of any kind. Every ToF part in the store is a
single-zone rangefinder that returns one number, and the one part that returns a map - the
Slamtec RPLIDAR A1 - is a spinning triangulation scanner, not a ToF imager. That single fact
governs the whole chapter: a 350 mm robot built from the Adafruit ToF shelf is a tiling problem,
and the parts that would solve it in one purchase have to be bought somewhere else.

Nothing in this catalogue classifies. Every part here returns a scalar distance, a scalar
proximity count, or a planar point cloud, so a human at 1.5 m and a wall at 1.5 m are the same
reading. Human-versus-pet-versus-object has to come from a different modality or from software.

All prices, stock counts and status strings in this chapter were read from `adafruit.com` on
2026-09-12. Chip-level numbers are datasheet-verified unless the line says otherwise; the
ultrasonic figures, the LIDAR-Lite v4 figures and the VL6180X ranging cone are vendor-page
figures.

## ST single-zone parts

Five ST FlightSense breakouts, all in stock, none discontinued, all with STEMMA QT. Product 3317
carries the STEMMA QT connectors even though the product title does not say so.

| PID | Part | Price | Emitter | Field of view (horizontal) | Condition |
|---|---|---|---|---|---|
| 3316 | [VL6180X](https://www.adafruit.com/product/3316) | $13.95 | 850 nm | 25 deg ranging cone | vendor-stated (Pololu); ST gives no numeric ranging cone |
| 3317 | [VL53L0X](https://www.adafruit.com/product/3317) | $14.95 | 940 nm | 25 deg system FoV, fixed | datasheet-verified, DocID029104 Rev 1 sec 5.1 |
| 3967 | [VL53L1X](https://www.adafruit.com/product/3967) | $14.95 | 940 nm | about 19 deg (27 deg is the **diagonal**) | 27 deg diagonal is datasheet-verified; 19 deg horizontal is inferred from the square array |
| 5396 | [VL53L4CD](https://www.adafruit.com/product/5396) | $14.95 | 940 nm | 18 deg detection volume | datasheet-verified at a 1000 mm white-88 % target; 22 deg at 100 mm |
| 5425 | [VL53L4CX](https://www.adafruit.com/product/5425) | $14.95 | 940 nm | 18 deg detection volume | datasheet-verified at a 1000 mm white-88 % target; 22 deg at 100 mm |

Volume pricing on the four VL53 parts is $13.46 at 10-99 units and $11.96 at 100+; the VL6180X is
$12.56 and $11.16 at the same breaks.

Maximum range, with the reflectance and the ambient-light condition that make each number mean
something. Every VL53L0X, VL53L4CD and VL53L4CX row is a 33 ms timing budget; the VL53L1X rows
are a 100 ms budget; the VL6180X rows are its worst-case table, measured in an integrating
sphere against 80 x 80 mm targets at an SNR limit of 0.1.

| Chip and mode | Target | Dark or indoor, no IR | Bright ambient | Ambient condition |
|---|---|---|---|---|
| VL53L0X | white 88 % | 200 cm typ (long-range profile) | 80 cm | outdoor overcast, 10 kcps/SPAD = 5 kLux |
| VL53L0X | grey 17 % | 80 cm typ | 50 cm | as above |
| VL53L1X long | white 88 % | 360 cm | 73 cm | 200 kcps/SPAD, direct sun on the sensor |
| VL53L1X long | grey 17 % | 170 cm | 68 cm | as above |
| VL53L1X short | grey 17 % | 130 cm | 120 cm | as above |
| VL53L4CD | white 88 % | 1200 mm at 90 % detection | 550 mm at 90 % | outdoor overcast, 5 kLux |
| VL53L4CD | grey 17 % | 450 mm at 90 % detection | 400 mm at 90 % | as above |
| VL53L4CX | white 88 % | 5000 mm at 90 % detection | 1600 mm at 90 % | as above |
| VL53L4CX | grey 17 % | 2100 mm at 90 % detection | 1100 mm at 90 % | as above |
| VL6180X | grey 17 % | > 100 mm | > 60 mm | 5 kLux diffuse halogen, about 10-15 kLux sun |
| VL6180X | 3 % black | > 100 mm | > 40 mm | as above |

**VL53L0X (3317).** Do not specify it for new work. The VL53L4CD costs the same, has better
accuracy, 100 Hz instead of about 30 Hz, and a wider temperature range; the VL53L0X keeps only the
wider 25 deg cone and a smaller code footprint. Its advertised 2 m is a white-88 % figure the
datasheet itself restricts to "dark conditions (no IR)".

**VL53L1X (3967).** The most interesting ST part for a robot, because the region of interest can
be moved across the 16x16 SPAD array: a 4x4 window swept across it builds a coarse depth image
from one sensor, at the cost of range (grey-17 % drops to 45 cm) and of rate (every window
position is a separate cycle). Its short distance mode is the only setting in the ST lane that is
nearly immune to sunlight, 130 cm dark and 120 cm on grey-17 % under direct sun through a window.
It is not for long range in daylight: long mode collapses about 5x under that condition.

**VL53L4CD (5396).** A 100 Hz short-range beam, best used low on the chassis for pets and low
furniture. The store headline of 1300 mm is a 50 %-detection-rate figure against a white chart
indoors; against a dark-grey target at 90 % detection it is 450 mm. It is not a room sensor.

**VL53L4CX (5425).** The best single-zone choice for forward obstacle beams. 2100 mm against a
grey-17 % target indoors at 90 % detection is the most useful "will I see the black cat" number in
the ST lane, and the histogram algorithm reports more than one target inside the cone, so one beam
returns both a chair back at 1.2 m and the wall behind it. It is not for an Arduino Uno: the
driver needs about 50 KB of flash, and Adafruit publishes no Arduino library for it.

**VL6180X (3316).** A proximity sensor, not a rangefinder: 850 nm instead of 940 nm, 1.7 mA
average instead of 16-22 mA, a calibrated lux output, and a guaranteed range of only 0 to 100 mm.
It is useless on a perimeter - 100 mm is inside the robot's own bumper line - and excellent
pointed down as a cliff and stair-edge detector. Sitting at 850 nm behind its own bandpass filter,
it does not interfere with a 940 nm ring (inferred from the filter, not a stated spec).

## ST multizone parts, none of which Adafruit sells

A store search for `VL53L5CX`, `VL53L7CX` or `VL53L8` returns no exact match and falls back to the
five single-zone parts. Adafruit designed a VL53LCX STEMMA QT breakout in September 2021 and ran
an EYE ON NPI segment on the VL53L5CX, but no product reached the store.

| Chip | Zones | FoV H x V | Diagonal | Where to buy | Price read 2026-09-12 |
|---|---|---|---|---|---|
| VL53L5CX | 4x4 or 8x8 | 45 x 45 deg | 63 deg | SparkFun SEN-18642; Pimoroni | $32.50 (backorder); GBP 16.25 in stock |
| VL53L7CX | 4x4 or 8x8 | 60 x 60 deg | 90 deg | not Adafruit | not read |
| VL53L8CX | 4x4 or 8x8 | 45 x 45 deg | 65 deg | not Adafruit | not read |

Quote the horizontal figure and say which one it is. ST prints the diagonal on the front page of
every datasheet, and the vendor pages repeat it, but Table 2 of each datasheet publishes the
horizontal and vertical figures separately - 45 x 45 deg behind the VL53L5CX "63 deg", 60 x 60 deg
behind the VL53L7CX "90 deg". For the VL53L1X, ST publishes only the diagonal, so its 19 deg
horizontal is inferred as 27 deg divided by the square root of two. A ring is closed with the
horizontal number: at zero overlap that is six VL53L7CX, eight VL53L5CX or VL53L8CX, against
roughly nineteen VL53L1X beams. Those are bare tiling counts; `coverage-geometry.md` computes the
overlap a ring needs to actually close its wedges. Sizing from the diagonal overstates the
multizone advantage.

The VL53L5CX "up to 400 cm" headline needs its conditions. DS13754 Rev 5 specifies maximum range
at a 90 % detection rate, target filling the field of view, 23 deg C, no cover glass, with 5 klux
defined as 2 W/m2 of 940 nm target irradiance.

| Mode and rate | Target and zone | Dark | 5 klux ambient |
|---|---|---|---|
| 4x4, 30 Hz | white 88 %, inner | 4000 mm typ | 1700 mm typ |
| 4x4, 30 Hz | grey 17 %, inner | 2400 mm typ | 1000 mm typ |
| 8x8, 15 Hz | white 88 %, inner | 3500 mm typ | 1100 mm typ |
| 8x8, 15 Hz | grey 17 %, corner | 1100 mm typ / 600 mm min | 650 mm typ / 400 mm min |

That last cell - a dark target in a corner zone of a sunlit room at 650 mm - is the number to
design to. Note also that the performance tables are specified at 30 Hz for 4x4 and 15 Hz for 8x8;
the vendor pages advertise "60 Hz" without saying which map it applies to.

## Non-ST direct time of flight: the ams-OSRAM TMF family

Adafruit ships two TMF parts, both single-zone. The multizone TMF882x family appeared as a
prototype on the Adafruit blog in August 2024 marked "coming soon" and has no product page.

| PID | Part | Price | Stock | Receiver FoV | I2C address |
|---|---|---|---|---|---|
| 6522 | [TMF8801](https://www.adafruit.com/product/6522) | $9.95 | 75 | 37 deg FWHM short, 24 deg FWHM long | 0x41 |
| 6501 | [TMF8806](https://www.adafruit.com/product/6501) | $12.50 | 33 | 52 deg short, 30 deg long (default stack) | 0x41 |

The TMF8801 datasheet publishes a full range-versus-reflectivity-versus-ambient matrix: on an
18 % grey card, 2500 mm under 350 lux fluorescent, 1700 mm at a 2.5 klux sunlight equivalent,
1250 mm at 10 klux and 550 mm at 100 klux. All rows use a 1.5 m x 1.5 m target with light on the
target only. Minimum distance 20 mm on an 18 % grey card, about 30 Hz, 27 mA at 30 Hz.

The TMF8806 is the better default of the two. Its conditioned table, from DS001097 v4-00 Table 5:

| Mode and iterations | Ambient | Target | Target extent | Max distance |
|---|---|---|---|---|
| 10 m, 1500 k (150 ms) | 350 lux fluorescent | 90 % white | **white wall** | 10000 mm |
| 5 m, 450 k (33 ms) | 350 lux fluorescent | 90 % white | 1.5 x 1.5 m | 5000 mm |
| 5 m, 450 k (33 ms) | 350 lux fluorescent | 18 % grey | 1.5 x 1.5 m | 3250 mm |
| 2.5 m, 900 k (33 ms) | 830 lux halogen (5 klux sun) | 18 % grey | 1.5 x 1.5 m | 1170 mm |
| 2.5 m, 900 k, tape on glass | 170 lux halogen (1 klux sun) | 18 % grey | 1.5 x 1.5 m | 1500 mm |

Two things in that table matter more than the headline. The 10 m row is a **white wall** number,
not an obstacle number - a wall fills the whole 30 deg cone and a 1.5 m card at 10 m does not, so
10 m must never be quoted as a detection range. And one layer of Scotch Magic Tape on the cover
glass costs 340 mm of range on an 18 % grey target at the 1 klux condition, from 1840 mm to
1500 mm. A floor robot's front window collects dust and pet hair continuously.

Adafruit's own store page describes the shipped TMF8806 board as "about 30 degrees short range
(under 200 mm) and 21 degrees above" and claims +/-5 % accuracy. That contradicts the datasheet,
which gives 52 deg short and 30 deg long for the default optical stack and a tiered accuracy of
+/-3 % beyond 200 mm. Prefer the datasheet; Adafruit may be describing their specific cover-glass
stack. The same page admits "we weren't able to get results past 5 meter".

**The multizone TMF882x, which Adafruit does not sell.** TMF8820 is 3x3, TMF8821 adds 4x4 and
3x6, TMF8828 adds 8x8 for 64 zones, with the field of view selected by `spad_map_id` - 33 x 32 deg
(45 deg diagonal) or 41 x 52 deg (63 deg diagonal) among five choices. DS000693 v5-00 conditions
the range on zone position, ambient light and iteration count, and the three maps are **not taken
at the same iteration count**: the 3x3 and 4x4 tables are 550 k iterations, the 8x8 table only
125 k, so the 8x8 numbers are depressed by a quarter of the integration budget as well as by the
smaller zones. On an 18 % grey card, light on the target only:

| Map, FoV, iterations, rate | Zone | 350 lux LED | 700 lux halogen (5 klux sun) | 1400 lux halogen (10 klux sun) |
|---|---|---|---|---|
| 3x3, 33 x 32 deg, 550 k, 30 Hz | centre | 5000 mm | 2000 mm | 1500 mm |
| 3x3, 33 x 32 deg, 550 k, 30 Hz | corner | 4000 mm | 1400 mm | 1200 mm |
| 4x4, 41 x 52 deg, 550 k, 15 Hz | centre | 4000 mm | 1500 mm | 1400 mm |
| 4x4, 41 x 52 deg, 550 k, 15 Hz | corner | 1400 mm | 700 mm | 600 mm |
| 8x8, 41 x 52 deg, 125 k, 15 Hz | centre | 2000 mm | 1000 mm | 800 mm |
| 8x8, 41 x 52 deg, 125 k, 15 Hz | corner | 500 mm | 300 mm | 200 mm |

The 8x8 corner zones collapse to 200-500 mm on an 18 % grey target, so 64-zone mode is a
near-field mode, not a room-scanning mode. Minimum detection distance is 10 mm on an 18 % grey
target and 25 mm on a 90 % white one; power is 141 mW at 30 Hz; the default I2C address is 0x41
again, so the family collides with the two TMF parts Adafruit does ship.

## Single-point and scanning lidar modules

| PID | Part | Price | Stock | Range and condition | Beam |
|---|---|---|---|---|---|
| 4010 | [RPLIDAR A1](https://www.adafruit.com/product/4010) | $99.95 | 19 | 0.15-6 m (R4) or 0.15-12 m (R5), white objects | 360 deg |
| 3978 | [TFmini](https://www.adafruit.com/product/3978) | $44.95 | **No longer stocked** | 0.3-12 m at 90 % white indoors; 0.3-3 m at 10 % black or 100 klux glare | 2.3 deg full |
| 4058 | [LIDAR-Lite v3](https://www.adafruit.com/product/4058) | $129.95 | 12, max 2 per customer | 40 m at a 70 % reflective target | 0.46 deg |
| 4441 | [LIDAR-Lite v4](https://www.adafruit.com/product/4441) | $59.95 | 15, max 2 per customer | 5 cm to 10 m, reflectivity condition unverified | 4.77 deg |

**RPLIDAR A1.** The only rotating product Adafruit sells and the strongest single perimeter answer
in the catalogue: one unit, 1 deg angular resolution, 8000 samples/s, 5.5 Hz typical. It is laser
triangulation, not time of flight, so resolution degrades with distance and the range is
conditioned on white objects. It sees exactly one plane, so a 200 mm cat is invisible unless the
scan plane sits below 200 mm, and a 700 mm table overhang is invisible to a plane at 100 mm. It needs two independent 5 V
rails and adds 170 g. The datasheet's own point-density figures do not reconcile: 8000 Hz at
5.5 Hz implies about 1450 points per revolution, but both the 1 deg resolution and the 5.5 Hz rate
are specified at 360 samples per scan. Quote 1 deg and 360 points.

**Garmin LIDAR-Lite v3 and v4.** Both are the wrong tool here. The v3's 0.46 deg beam lights a
16 mm spot at 2 m and threads straight past a cat's leg to report the wall behind. The v4's
4.77 deg is better but $59.95 per beam is absurd for a ring, and both are limited to two units per
customer, which by itself rules out tiling. Where Adafruit and Garmin disagree, Garmin wins:
accuracy is +/-2.5 cm below 5 m and +/-10 cm at and above 5 m, not Adafruit's flat "+/-2.5 cm above
1 m", and 270 Hz is the update rate at a 70 % target while 500 Hz is the repetition-rate maximum.

**TFmini, discontinued.** Kept here for one table. Its manual publishes the minimum reliable
target size as `d = 2 D tan(1.15 deg)`: 4 cm at 1 m, 8 cm at 2 m, 20 cm at 5 m. A cat's torso
clears that at 2 m; a chair leg or a cat's tail does not. That is the failure mode of every
narrow-beam ranger, and a 2.3 deg beam is a 157-sensor problem for 360 deg coverage.

## Ultrasonic

Ultrasonic is the only technology here indifferent to optical colour, and the only one that
reliably sees clear glass. It is the natural cross-check for a dToF ring, not a replacement.

| PID | Part | Price | Stock | Range | Beam |
|---|---|---|---|---|---|
| 3942 | [HC-SR04](https://www.adafruit.com/product/3942) | $3.95 | In stock | 2-400 cm, best 10-250 cm | 15 deg |
| 4007 | [RCWL-1601 3V/5V](https://www.adafruit.com/product/4007) | $3.95 | In stock | 2-450 cm, best 10-250 cm | +/-15 to +/-20 deg |
| 4019 | [US-100](https://www.adafruit.com/product/4019) | $6.95 | In stock | 2-450 cm, best 10-250 cm | under 15 deg |
| 979 | [MaxBotix LV-EZ0](https://www.adafruit.com/product/979) | $29.95 | 44 | 0-254 in (6.45 m), reports from 6 in | widest in the LV-EZ line |
| 982 | [MaxBotix LV-EZ4](https://www.adafruit.com/product/982) | $28.50 | 48 | 0-254 in (6.45 m) | narrowest in the line |
| 4742 | RCWL-1601 with I2C | $3.95 | **Out of stock** | not read | not read |
| 4664 | Large ultrasonic with horn, UART | $28.95 | **No longer stocked** | 28-750 cm with horn | 40 deg with horn, 75 deg without |

The LV-EZ1, LV-EZ2, LV-EZ3, HRLV-EZ0/1/4, MB7092, HR-USB-EZ1 and the panel-mount sonar are all no
longer stocked. Of what remains, the LV-EZ0 is the one with published human-detection evidence:
MaxBotix states it "can detect people up to approximately 10 feet" and defines the 1-inch dowel
beam pattern as the reliable people-detection zone. Against that, a MaxSonar range cycle is 49 ms,
so eight sensors round-robin at about 2.5 Hz; 40 kHz transducers on one 350 mm chassis hear each
other; fur and wool absorb 40 kHz; and a smooth wall approached at a shallow angle bounces the
ping away and reads clear.

## The parts people mistake for rangefinders

| PID | Part | Price | Stock | Published reach | What it actually is |
|---|---|---|---|---|---|
| 164 | [Sharp GP2Y0A21YK0F](https://www.adafruit.com/product/164) | $14.95 | 65 | 10-80 cm at a Kodak R-27 90 % white card | analog PSD triangulation |
| 1031 | [Sharp GP2Y0A02YK0F](https://www.adafruit.com/product/1031) | $15.95 | 17 | 20-150 cm, same 90 % condition | analog PSD triangulation |
| 1927 | Sharp GP2Y0D810Z0F carrier | $8.95 | **No longer stocked** | 20-100 mm | digital high/low, not a distance |
| 3025 | Sharp GP2Y0D805Z0F carrier | - | **No longer stocked** | 0.5-5 cm | digital high/low |
| 6064 | [VCNL4200](https://www.adafruit.com/product/6064) | $6.95 | **Out of stock** | 0 to 1.5 m, target size not published | reflected-IR count |
| 6491 | [VCNL4030](https://www.adafruit.com/product/6491) | $5.95 | In stock | 0 to 300 mm | reflected-IR count |
| 4161 | [VCNL4040](https://www.adafruit.com/product/4161) | $5.95 | In stock | 0 to 200 mm | reflected-IR count |
| 3595 | [APDS9960](https://www.adafruit.com/product/3595) | $7.50 | In stock | "a few centimeters" | 8-bit proximity plus gesture |
| 5913 | [TCRT1000](https://www.adafruit.com/product/5913) | $4.95 | 86 | millimetres | reflective photo-interrupter |

The Sharp analog parts fail for two structural reasons, and one commonly repeated reason that is
wrong. The response curve is non-monotonic below the minimum range: output rises to about 3.13 V
at 5-6 cm, then falls to 0.4 V at 80 cm, so every far reading has a near twin - about 1.05 V is
either 25 cm or 1.6 cm. A robot that drives into a wall gets a reading saying "not close". And the
beam width is not published by Sharp, Adafruit or Pololu, so coverage cannot be computed from it.
The wrong reason is reflectance sensitivity: these are position-sensitive-detector parts, and
Sharp's Figure 2 plots 90 % white and 18 % grey almost coincident across the whole span.
Reflectance-blindness is in fact their one advantage over every dToF part here. Adafruit's "3 V at
10 cm" is also not supportable - Sharp's 1.9 V typical differential puts 10 cm at about 2.3 V.

The VCNL and APDS parts report a reflected-IR count, not a calibrated distance, and their reach
depends on how much LED current you burn and how reflective the target is. Adafruit's own VCNL4200
page tempers the 1.5 m datasheet claim to a "practical range 50-100 cm", and Vishay publishes no
target size or reflectivity behind the 1.5 m figure. Their legitimate role is cliff detection at
the chassis skirt, where every ToF part here fails inside its own minimum range: a VCNL4040
pointed down catches a stair drop-off inside 200 mm, and the TCRT1000 photo-interrupter does the
same job at millimetre standoff. The VCNL4010 (PID 466) is no longer stocked. The LTR-329
(5591, $4.50), LTR-303 (5610, $4.50) and MAX44009 (6498, $12.50) have no proximity function at
all, but earn a place for another reason: every range figure in this chapter is conditioned on
ambient light, and a lux sensor lets the robot detect a sunbeam and derate its own trust
accordingly.

## What the store page will not tell you

**Every VL53 and VL6180X boots at the same address.** All five ST parts power up at 0x29 7-bit
(0x52 8-bit), and the address is volatile. Adafruit's guide states the trap outright: "You must do
this every time you turn on the power, the addresses are not permanent!" The sequence is one
microcontroller GPIO per sensor wired to XSHUT; hold all low for 10 ms then high; bring sensor one
up alone and assign it an address in 0x30-0x3F; repeat. Every part exposes the call -
`Adafruit_VL53L0X::setAddress()`, `VL53L1X_SetI2CAddress()`, `set_address()` in CircuitPython. The
practical bus limit is spare GPIOs and the 400 pF bus capacitance a daisy chain of STEMMA QT
cables around a 350 mm chassis will approach; 12-16 on one bus is plausible with short cables
(inferred - no document read here states a maximum). A TCA9548A multiplexer removes the per-sensor
XSHUT GPIO entirely. The same collision hits both TMF parts, which share 0x41.

**The timing budget buys range and spends rate.** The VL53L1X accepts 20 ms to 1000 ms; 20 ms is
short-mode only, 33 ms is the minimum that works in all modes, and 140 ms is required to reach the
full 4 m in long mode on a white chart in the dark. The CircuitPython driver accepts only 15, 20,
33, 50, 100, 200 and 500 ms and implements short and long modes only - medium is missing. The
VL53L0X exposes four profiles: 20 ms high speed at +/-5 %, 30 ms default, 33 ms long range at 2 m
but "only for dark conditions (no IR)", and 200 ms high accuracy at better than +/-3 %. On the
TMF8806 the budget is an iteration count: 450 k iterations in 33 ms reaches 3250 mm on an 18 %
grey card, 900 k in 66 ms reaches 3750 mm, and the ultra-low-power 10 k setting reaches 665 mm.
The budget also sets the ring's update rate, because sensors sharing overlapping space should be
time-multiplexed - a 12-sensor ring at a 20-33 ms budget round-robins at roughly 2.5-4 Hz each.

**One part needs a firmware blob at every boot.** Adafruit's TMF8801 guide states the part "does
require a firmware 'patch' on boot" - the host pushes a several-kilobyte image at startup, costing
both flash and boot time. Adafruit notes the TMF8806 needs no patch for 5 m mode and that its
driver fits on an ATmega328. No ST part here is documented as needing a boot blob in the sources
read for this reference; the VL53L4CX constraint is simpler, a 50 KB driver that will not fit an
Arduino Uno.

**Cover glass is a calibration step, not a cosmetic one.** "Crosstalk" in these datasheets means
cover-glass optical crosstalk, not sensor-to-sensor interference. The VL53L1X requires RefSPAD,
offset and crosstalk calibration whenever a cover glass is added; the VL53L4CX is immune beyond
80 cm and compensates for smudge below it; the TMF882x family needs a window at least 85-90 %
transparent at 940 nm.

**Glass and mirrors are an unpublished blind spot.** No datasheet read for this chapter publishes
behaviour against a specular or transparent target - all reflectance data uses diffuse Munsell or
grey-card charts. Physically, a mirror at an angle returns nothing to the receiver and clear glass
is largely transparent at 850 and 940 nm, so both are usually missed. That is inference from the
absence of a spec, not a published result, and it is the strongest argument for keeping one
ultrasonic sensor in the design.
