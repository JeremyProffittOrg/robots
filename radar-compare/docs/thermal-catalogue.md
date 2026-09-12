# Thermal and infrared people sensing

No thermal or infrared part in this catalogue can serve the obstacle requirement. A chair leg, a
door frame and a cardboard box all sit at room temperature, so their radiated contrast against the
wall behind them is approximately zero, which is below the noise floor of every device listed here.
A thermopile or TMOS array measures radiated flux, not geometry. Thermal is an animate-versus-
inanimate channel and nothing else, and it is the only modality here that answers that question
about a motionless body. Everything below decides whether that one answer is worth its price, its
aperture and its frame rate on a 350 mm robot.

## The catalogue

Multi-pixel arrays, the only thermal parts that can classify anything. All prices and stock read
from adafruit.com on 2026-09-12.

| Part | ID | Price | Array | FoV H x V | Stock |
|---|---|---|---|---|---|
| MLX90640 IR Thermal Camera Breakout, 55 Degree | 4407 | $74.95 | 32x24, 768 px | 55 x 35 deg | 4 in stock |
| MLX90640 24x32 Breakout, 110 Degree FoV | 4469 | $74.95 | 32x24, 768 px | 110 x 75 deg | Out of stock |
| AMG8833 Grid-EYE Breakout, STEMMA QT | 3538 | $44.95 | 8x8, 64 px | 60 x 60 deg | 57 in stock |
| AMG8833 Grid-EYE FeatherWing | 3622 | $44.95 | 8x8, 64 px | 60 x 60 deg | In stock |
| UTi165H handheld imager | 4578 | $250.00 | 160x120 | 56 x 42 deg | 5 in stock |
| UTi165K handheld imager, USB video | 4579 | $499.95 | 160x120 | 56 x 42 deg | 91 in stock |

The MLX90640 field of view is datasheet-verified from Melexis Rev 12 Table 15 at the 50 %
sensitivity point, the wider figure being the X axis across the 32-pixel direction. The Grid-EYE
60 deg is the Panasonic "Typical 60 deg" viewing angle, horizontal and vertical alike. Neither is a
diagonal.

Single-element presence parts, which detect but cannot locate or classify.

| Part | ID | Price | FoV | Stated range | Stock |
|---|---|---|---|---|---|
| STHS34PF80 IR Presence / Motion (ST TMOS) | 6426 | $14.95 | 80 deg full, at 50 % IR intensity | 4 m for a 700 x 250 mm object, no lens | In stock |
| MLX90614 contact-less IR, 3 V (ESF-BAA) | 1747 | $15.95 | 90 deg | Not published | No longer stocked |
| MLX90614 contact-less IR, 5 V (ESF-AAA) | 1748 | $15.95 | 90 deg | Not published | No longer stocked |
| PIR (motion) sensor | 189 | $9.95 | 120 deg | About 7 m, vendor-stated | Out of stock |
| Breadboard-friendly Mini PIR, 3-pin | 4871 | $3.95 | 100 deg | 2 to 5 m, vendor-stated | In stock |
| Mini PIR with time and sensitivity, BS612 | 5578 | $1.95 | 120 deg | About 5 m, lens focused at 5 m | In stock |

Both MLX90614 boards are xAA optics at 90 deg, datasheet-verified from Melexis Rev 021 Table 19,
although they carry different order codes. The same datasheet says the reading is "the average
temperature of all objects in the Field Of View", which across a 90 deg cone is the room, not the
person. Adafruit redirects 1747 to the AMG8833 and 1748 to the STHS34PF80. The three PIR modules
report motion only: none holds a static body, and on a driving robot the whole scene moves, so the
output saturates.

The two UNI-T handhelds publish no detection range at all, only a 15 cm minimum and a 1 m optimal
measuring distance, and their 30 to 45 degC window clips everything at room temperature. They are
battery handhelds with no embeddable output, and are excluded from every table below.

## Parts the search returns that are not thermal sensors

The search `camera stema ir` on adafruit.com returns exactly four items, and one of them is a
book. The wider searches return magnetometers with similar part numbers. Named and excluded:

- **Bots! Robotics Engineering (4348, $14.95)** is a book.
- **MLX90393 (4022, $9.95)** is a triple-axis magnetometer, +/-5 to 50 mT. The similar Melexis part
  number is the only connection to the MLX90614 and MLX90640.
- **LIS3MDL (4479, $9.95)** is also a magnetometer.
- **Raspberry Pi NoIR camera modules (3100, 5659, 5660, 3415, 5658)** have the IR-cut filter
  removed, which extends a silicon imager to roughly 850 to 1000 nm near-infrared. Body heat
  radiates at 8 to 14 um, so a NoIR camera cannot see it, and in a dark room it sees nothing
  without an 850 nm illuminator. It belongs in the camera lane.
- **MLX90641 (16x12)** is not stocked by Adafruit in any form, verified by search. Seeed, Waveshare
  and Evelta sell it, so it is buyable, but no Adafruit price, stock or breakout exists to quote.
- A **thermopile** search on adafruit.com returns thermoplastic and filament products only.

## Pixel subtense: the argument that settles it

Angular pixel pitch is the field of view divided by the pixel count along that axis, and the
linear footprint of one pixel at range d is w = 2 x d x tan(pitch / 2).

- Grid-EYE: 60 / 8 = 7.5 deg, so w = 2 x d x tan(3.75 deg) = 0.1311 x d, or **131 mm per metre**,
  square.
- MLX90640 55 deg: 55 / 32 = 1.719 deg H and 35 / 24 = 1.458 deg V, so **30.0 mm/m H, 25.5 mm/m V**.
- MLX90640 110 deg: 110 / 32 = 3.438 deg H and 75 / 24 = 3.125 deg V, so **60.0 mm/m H,
  54.6 mm/m V**.

Worked example at the longest survey distance. Grid-EYE at 10 ft (3.048 m): one pixel covers
2 x 3048 x tan(3.75 deg) = 400 mm. A 450 mm adult torso is 450 / 400 = **1.1 pixels** wide. A
250 mm cat is 250 / 400 = **0.6 pixels**. Targets in the tables are a 450 mm torso, a 1700 mm
standing adult, and a cat 250 mm long by 200 mm tall.

Horizontal pixels across an adult torso:

| Range | Grid-EYE 8x8 | MLX90640 55 deg | MLX90640 110 deg |
|---|---|---|---|
| 1 ft (0.305 m) | 11.3 (overflows frame) | 49 (overflows) | 24.6 |
| 3 ft (0.914 m) | 3.8 | 16.4 | 8.2 |
| 5 ft (1.524 m) | 2.3 | 9.8 | 4.9 |
| 8 ft (2.438 m) | 1.4 | 6.2 | 3.1 |
| 10 ft (3.048 m) | 1.1 | 4.9 | 2.5 |

Pixels on a cat, horizontal x vertical:

| Range | Grid-EYE 8x8 | MLX90640 55 deg | MLX90640 110 deg |
|---|---|---|---|
| 1 ft (0.305 m) | 6.3 x 5.0 | 27 x 26 | 13.7 x 12.0 |
| 3 ft (0.914 m) | 2.1 x 1.7 | 9.1 x 8.6 | 4.6 x 4.0 |
| 5 ft (1.524 m) | 1.3 x 1.0 | 5.5 x 5.2 | 2.7 x 2.4 |
| 8 ft (2.438 m) | 0.8 x 0.6 | 3.4 x 3.2 | 1.7 x 1.5 |
| 10 ft (3.048 m) | 0.6 x 0.5 | 2.7 x 2.6 | 1.4 x 1.2 |

Classification needs shape, and shape needs at least three pixels across the short axis before an
aspect ratio means anything. That sets a hard ceiling no software can lift. **Grid-EYE: about
1.2 m for a pet and about 2.5 m for a human.** **MLX90640 55 deg: about 3 m for a pet, past 7 m for
a human.** **MLX90640 110 deg: about 1.5 m for a pet, about 3 m for a human.** Field of view is
bought with range one for one: the 110 deg part has almost exactly the pet range of the 55 deg part
at half the distance.

Below one pixel of fill, the number the sensor reports is not a temperature. A pixel returns the
flux-weighted average over its whole footprint, so apparent rise = fill fraction x surface delta T.
Against a 22 degC room and a cat at 8 degC above ambient, the Grid-EYE reports that cat as
8.00 degC out to 1.5 m, then 3.91 degC at 2.44 m, 2.51 degC at 3.05 m and 0.48 degC at 7 m, while a
clothed torso at 6 degC reads 3.77 degC at 5 m. **On an 8x8 array apparent temperature is mostly a
range measurement in disguise**, so a cat at 1 m and a human at 5 m can return the same pixel
value, and no threshold tuning fixes it. The 55 deg MLX90640 is the exception: a torso fills a
pixel out to 15 m and a cat to 7.8 m, so on that part nothing in this section dilutes except a bare
face, which at 200 mm across begins to dilute beyond 6.7 m. The 110 deg part is coarser: a bare
face dilutes beyond 3.3 m, and a cat beyond 3.7 m, where the vertical axis binds first at
200 / 54.6.

Two source disagreements, both in the reader's favour to know. The computed appendix divides the
frame width by half the column count (`scripts/geometry.py`, `zone_width_mm`), which makes its
centre-pixel footprint 88.0 mm for the Grid-EYE at 0.305 m against 40 mm from the datasheet pixel
pitch, a factor of 2.2. Prefer the pitch-derived figures above, because 60 deg across 8 pixels is a
7.5 deg sampling pitch by construction. Panasonic's per-pixel figure is not a second opinion on
that pitch: the datasheet quotes it as a half angle, 7.7 deg horizontal and 8 deg vertical, so one
pixel accepts a full cone of about 15.4 deg H, roughly twice the pitch. Adjacent pixels therefore
overlap heavily and a point target bleeds into its neighbours, which blurs the image but does not
change the 7.5 deg spacing the tables are built on. The computed appendix also models a cat as
140 mm wide at the shoulder rather than 250 mm long, so its cat capability levels are one step more
pessimistic than the table above at most distances.

## Mounting geometry: the constraint that kills pet detection first

Pixel count is not the binding limit for a pet. Frame placement is. The pet stands 200 to 500 mm
tall and the sensor sits on a robot 600 to 1200 mm tall, so take the sensor height H as 0.9 m, the
mid-point of that build range. With a vertical half field of view of alpha and a downward tilt t,
the floor first enters the frame at H / tan(alpha + t), the top of a 200 mm cat at
(H - 0.2) / tan(alpha + t), and a 1700 mm head stays in frame out to (1.7 - H) / tan(alpha - t).

| Sensor, vertical FoV | Tilt | Floor first seen | Cat top first seen | Adult head out to |
|---|---|---|---|---|
| Grid-EYE 60 deg | 0 deg | 1.56 m | 1.21 m | 1.39 m |
| Grid-EYE 60 deg | 15 deg | 0.90 m | 0.70 m | 2.99 m |
| Grid-EYE 60 deg | 25 deg | 0.63 m | 0.49 m | 9.14 m |
| MLX90640 35 deg V | 0 deg | 2.85 m | 2.22 m | 2.54 m |
| MLX90640 35 deg V | 15 deg | 1.41 m | 1.10 m | 18.3 m |
| MLX90640 75 deg V | 0 deg | 1.17 m | 0.91 m | 1.04 m |
| MLX90640 75 deg V | 25 deg | 0.47 m | 0.36 m | 3.61 m |

Read the level rows. **Mounted level at 0.9 m, the 55 deg MLX90640 is blind to a cat inside
2.2 m**, because the animal is below the frame, and that is worse than the 3 m optical limit
computed above. The fix is a 15 to 25 deg downward tilt, which pulls the cat-visible boundary in to
0.5 to 1.1 m and, on the narrow part, extends head-in-frame to effectively unlimited range because
the upper edge still clears 1.7 m. The 55 x 35 deg part tilted 20 deg is the best single
configuration in this catalogue for a robot of this size. The 110 deg part tilted 25 deg sees a cat
from 0.36 m but loses a standing adult's head beyond 3.6 m.

One more geometry term applies to a ring. The Grid-EYE optical axis gap is "within typical
+/-5.6 deg", which on a 7.5 deg pitch is three-quarters of a pixel of unit-to-unit boresight error,
so fusing six frames into one panorama needs per-unit extrinsic calibration. The MLX90640 is
tighter: max 5 deg on the 110 deg part and max 3 deg on the 55 deg part.

## Why temperature alone cannot separate a pet from a human

The premise that a 38 degC cat can be told from a 34 degC human fails three times over.

First, these sensors measure surface, not core. A cat's core is 38 to 39.2 degC, but fur insulates:
measured fur surface is typically 30 to 36 degC, with ears, nose and paw pads at 35 to 38 degC
because they are thinly furred. Human exposed skin is 31 to 35 degC, and a clothed torso in a
sweater reads 25 to 28 degC in a 22 degC room. The two distributions overlap almost completely, and
the clothed human is often the cooler of the two.

Second, fill fraction swamps the signal, as the dilution figures above show.

Third, the absolute accuracy is the same size as the effect. Grid-EYE accuracy is "Typical
+/-2.5 degC". MLX90640 frame accuracy is +/-1 to +/-2 degC, with non-uniformity up to +/-3 degC
plus 2 % of abs(To - Ta) in the outer zone. The claimed 4 degC core gap maps to perhaps 1 to 3 degC
of surface difference, which is inside that uncertainty.

What does separate them is geometry and kinematics, and every cue needs pixels.

| Cue | Human | Cat or small dog | Minimum sensor to see it |
|---|---|---|---|
| Blob centroid above floor | 0.9 to 1.2 m | 0.1 to 0.25 m | any array with the floor in frame |
| Aspect ratio, tall to wide | about 3.8:1 standing | about 1.25:1, long and low | 3 px in the short axis |
| Gait or step frequency | 1.7 to 2.2 Hz | 2.5 to 4 Hz | 8 full frames/s |

The height-above-floor cue is the cheap decisive one, and it works on a Grid-EYE out to about 2.4 m
provided the tilt of the section above puts the floor in frame. The aspect-ratio cue needs a 3 x 3
blob, so about 1.2 m on a Grid-EYE, about 3 m on the 55 deg MLX90640 and about 1.5 m on the 110 deg
part. The gait cue needs 8 full frames per second, which a Grid-EYE has at 10 Hz and a
bandwidth-bound MLX90640 ring at about 1.4 Hz each does not.

## The four limits that decide whether thermal earns its place

**It cannot see through glass or a printed shell.** Body heat at 34 degC peaks near 9.4 um. Thermal
optics use germanium, which transmits roughly 2.5 to 12 um, which is why a germanium window costs
what it does. Soda-lime glass transmits about 0.25 to 3 um and is opaque above roughly 3 um.
Polycarbonate, acrylic and PET are all opaque in the long-wave infrared, so a clear cosmetic dome
silently zeroes the sensor. A human behind a glass door is thermally invisible, and the door itself
is undetectable as an obstacle, because it radiates at room temperature like the wall beside it.
The shell needs an **open aperture** at every thermal sensor, or a thin LDPE window with an
accepted transmission loss. Polished floors, stainless appliance fronts and glossy cabinets are
good long-wave reflectors, so expect ghost blobs beside kitchen appliances that an 8x8 array cannot
tell from a second person.

**A warm room collapses the contrast.** A clothed human against a 22 degC room is about 6 degC of
surface contrast. Against a 28 degC room it is about 1 to 2 degC, and diluted across a sub-pixel
target at 3 m that falls to roughly 0.4 degC, comparable to the Grid-EYE 10 Hz NETD of 0.16 degC.
Thermal detection range is a function of room temperature and drops sharply in summer. Two drift
terms push the same way: the MLX90640 needs up to 4 minutes of thermal stabilisation for its
accuracy spec and the Grid-EYE 15 s, and a chassis full of motor drivers warms the enclosure air 8
to 10 degC above room over a 20-minute run. Never threshold on absolute temperature; subtract a
per-pixel background model with a time constant of tens of seconds.

**A sun-warmed floor patch reads as a body.** Direct sun through a window commonly drives dark
flooring to 35 to 45 degC, squarely inside the human range. A thermal-only classifier chases
sunbeams. This is the classic robot-vacuum failure and it has not gone away.

**The frame rate is slow against a moving robot.** The Grid-EYE offers 10 Hz or 1 Hz and nothing
else. At 10 Hz, with a human walking at 1.4 m/s and the robot at 0.5 m/s, two frames to confirm a
detection costs 200 ms and 380 mm of closure: acceptable beyond about 1 m, marginal inside it. The
MLX90640 is worse than its headline, because the programmed refresh rate applies per subpage, so
"16 Hz" is 8 full frames per second and a fast target tears across the two half-frames. One frame
is about 1668 bytes, roughly 42 ms of 400 kHz bus time, so a four-sensor ring is bandwidth-bound to
about 1.4 Hz each: 714 ms and 1.36 m of closure per confirmed detection.

## Verdict at the five survey distances

| Range | Grid-EYE 3538 | MLX90640 55 deg | MLX90640 110 deg | STHS34PF80 | PIR |
|---|---|---|---|---|---|
| 1 ft | Human overfills; cat resolved | Full silhouette both | Full human; cat 13 px | Presence only | Motion only |
| 3 ft | Human blob; cat marginal | Full silhouette; cat 9 px | Human yes; cat 4 px | Presence only | Motion only |
| 5 ft | Human yes; cat = 1 px | Human yes; cat 5 px | Human yes; cat 2.7 px | Presence only | Motion only |
| 8 ft | Human 1x5 strip; cat gone | Human yes; cat 3.4 px | Human 3 px; cat gone | Presence only | Motion only |
| 10 ft | Human 1x4 strip; cat gone | Human yes; cat 2.7 px | Human 2.5 px; cat gone | Presence only | Motion only |

On a 350 mm robot, thermal is a short-range channel. The Grid-EYE separates a human from a pet only
inside about 1.2 m, and beyond 5 ft a cat is not there at all; six units close a 360 deg ring for
$269.70, but the part answers to only two I2C addresses, 0x68 and 0x69, so the ring also needs a
TCA9548A multiplexer. The 55 deg MLX90640 is the only part that holds a real silhouette across the
whole survey, and at $74.95 with 4 units in stock it buys one direction, not a ring: seven units
for 360 deg is $524.65 and a bus it cannot feed. The 110 deg part closes a ring in four units for
$299.80, but it is out of stock and it gives up the pet range to do it. The STHS34PF80 at $14.95
and 10 uA, measured at 128-sample averaging and a 1 Hz output rate, holds a **stationary** body,
which no PIR can, and is the right always-on wake-up gate; five of them cover 360 deg for $74.75,
again behind a multiplexer because the address 0x5A is fixed. The PIR modules and the discontinued
MLX90614 contribute nothing a perimeter ring can use. None of them, at any distance, sees the
chair leg.

The defensible configuration is therefore not a thermal ring. It is one MLX90640 4407 facing the
direction of travel behind an open aperture, tilted 20 deg down so the floor is in frame, taking
range and geometry from a time-of-flight lane and contributing the one bit that lane cannot
produce: whether the obstacle is alive.
