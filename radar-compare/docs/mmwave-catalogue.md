# mmWave radar catalogue: every DFRobot part

DFRobot sells ten radar-class modules and not one of them is designed to move. Nine are buyable
as of 2026-09-12, one is retired, and every human-presence part in the line is an indoor
occupancy sensor specified for a fixed mount. The catalogue below is organised by what each
module puts on the wire - a bare flag, a range, a range with velocity, or a 60 GHz vital-signs
record - because the output decides whether a mobile robot can use it at all.

Five catalogue facts first, to stop wasted searching. There is no DFRobot SKU `SEN0611`; the
storefront resolves it to SEN0609 or SEN0610. Those two are usually quoted the wrong way round:
SEN0609 is the 25 m UART part and SEN0610 is the 12 m I2C-and-UART part, confirmed on both
product pages. `MR24HPC1`, `MR60BHA2` and `MR60FDA2` are Seeed Studio modules DFRobot mentions
in blog posts and sells no board based on. DFRobot does not stock the Hi-Link LD2450, the cheap
radar that does report target x/y, so nothing here reports a bearing. Two kits, KIT0216-EN
($89.00) and KIT0234 ($79.90), contain an unnamed "mmWave Human Presence" module whose SKU is
not published.

The two Seeed 60 GHz parts get a paragraph because they are the usual suggestion once the
DFRobot line runs out. Both are built on the ADT6101P, which integrates a 57-64 GHz transceiver
and a 2T2R microstrip antenna; the module datasheets specify 58-62 GHz, 12 dBm typical, 4 dBi
of antenna gain and a -3 dB beam of +/-60 deg in both planes. MR60BHA2 measures breathing and
heart rate at a chest distance of 0.4-1.5 m. MR60FDA2 detects a fall out to a maximum radius of
2 m, top-mounted at a hanging height of 2.2-3.0 m, and its datasheet is marked Beta Version.
Power is the disqualifier on a battery robot: the ICC table says 600 mA maximum, but the same
datasheet's Precautions section requires 3.1-3.5 V with ripple of 50 mV or less and current of
1 A or more. Budget 1 A, not 600 mA.

## Class A - bare presence flag

These report one bit. They answer "is something alive-ish in the cone" and nothing else.

| SKU | Band and chipset | Moving range | Static range | FoV H x V | Price USD |
|---|---|---|---|---|---|
| SEN0395 | 24 GHz; chipset not published | 9 m | 9 m (not split) | 100 x 40 deg | 29.00 |
| SEN0192 | 10.525 GHz X-band CW Doppler | 2-16 m, pot-set | none - cannot see a still target | 72 x 36 deg (-3 dB) | 8.90 |
| SEN0521 | 5.8 GHz FMCW and CW | 11 m | 11 m | 120 x 120 deg | retired, listed 0.00 |

SEN0395 outputs GPIO2 high for present plus a serial `$JYBSS` frame. No distance, no bearing,
no speed. Factory latencies are 2.5 s to assert and 10 s to clear, reprogrammable in 25 ms
steps - 10 s of latched presence on a driving robot is meaningless. Supply 3.6-5 V at 90 mA,
24 x 28 mm, UART 115200. It is the most expensive bare-bit part DFRobot sells, at three times
the price of a richer module.

SEN0192 is X-band Doppler, not mmWave, and appears only because the search index returns it. It
fires on relative motion, so it cannot see a standing person, and its 48.5 x 63 mm board is
large for a 350 mm chassis. SEN0521's page still publishes specifications (11 m, 120 x 120 deg,
22 mA, 20 x 18 mm) but the part is unbuyable. Do not design it in.

The `-3 dB` note matters. SEN0192 and SEN0306 are the only DFRobot radars publishing beamwidth
as an explicit half-power figure; every other angle in this chapter is an unconditioned "beam
angle" from a spec table. The two are not comparable, so a ring sized from one is not sized the
same way as a ring sized from the other.

## Class B - presence plus range

One part sits here: SEN0557, at $9.90, in stock.

| Parameter | Published value | Basis |
|---|---|---|
| Band and sweep | 24-24.25 GHz, 250 MHz sweep | vendor-page-verified |
| Detection range | 0.75 m to 6 m, moving and static not split | vendor-page-verified |
| Blind zone | 30 cm | vendor-stated as measured |
| Distance resolution | 0.75 m, eight gates | vendor-page-verified |
| FoV | +/-60 deg; **axis not stated**, vertical not published | vendor-page-verified |
| Output | presence bit on GPIO, plus per-gate moving and stationary energy over UART | vendor-page-verified |

The per-gate energy vector is the most information-rich cheap output in the catalogue: each
0.75 m gate carries a moving-target energy and a stationary-target energy. That is a crude range
profile, and the only place in the DFRobot line where moving and static returns are separated
per range cell. Supply 5-12 V at 80 mA average, 7 x 35 mm - the smallest radar footprint DFRobot
sells. Its stated 57600 baud default conflicts with the Hi-Link LD2410 datasheet default of
256000; verify on the bench before writing firmware.

The chipset is an inference. The fingerprint - 24-24.25 GHz, 250 MHz sweep, 0.75 m gates, eight
gates to 6 m, +/-60 deg, a 256000 baud option - matches the Hi-Link HLK-LD2410 exactly. One
source file records that as datasheet-identified, another as inferred. Prefer the cautious
reading: DFRobot names no silicon vendor anywhere, so the identification is inferred and the
moving-versus-static range split remains not published.

## Class C - range plus velocity

This is the useful class, and the cheapest part in it is the best one.

| SKU | Band | Moving range | Static range | FoV H x V | Price USD |
|---|---|---|---|---|---|
| SEN0691 | 24-24.25 GHz | 11 m | 10 m micro-motion | 120 x 120 deg | 8.90 |
| SEN0610 | 24 GHz | 12 m | 8 m | 100 x 80 deg | 12.90 |
| SEN0609 | 24 GHz | 25 m | 16 m | 100 x 40 deg | 13.90 |
| SEN0306 | 24 GHz | 0.5-20 m, any reflector | n/a - no presence claim | 78 x 23 deg (-3 dB) | 65.90 |
| SEN0676 | 77-81 GHz, 4 GHz sweep | n/a - liquid level | 0.15-40 m | +/-25 deg, +/-3 deg with lens | 59.00 |

SEN0691 (C4002) reports target state, presence distance and energy 0-99, motion distance, speed,
energy and an approach/recede direction, ambient lux, and a per-gate occupancy bitmap. Gates are
selectable: 16 of 80 cm, or 26 of 20 cm spanning 5.2 m, with per-gate thresholds 0-99 set
independently for motion and presence. Report period is 0.1 s to 25.5 s - DFRobot's example code
ships at 1 Hz. Price falls to $8.30 at 10 or more. The wiki scopes the 11 m and 10 m figures to
a named target, "Motion, Micro-Motion/Stationary Human Body", which is more than DFRobot states
for most of the line. It still gives no RCS, no target size and no aspect, so 11 m is not a
reach against a cat or a chair leg.

SEN0609 and SEN0610 (C4001) report target count, range, signed radial speed and energy, one
target maximum, with presence and ranging modes mutually exclusive. Both have a 1.2 m ranging
floor - exactly the zone a 350 mm robot cares about - and DFRobot's own C4001 datasheet
disclaims the distance verbatim: the sensor is "not specifically designed for distance
measurement", the distance is "not calibrated" and "can only be used as a reference". The same
datasheet documents a 1 m transition zone, so a configured maximum is soft: set 3 m and targets
out to 25 m are still reported with falling probability, while nothing past 25 m is reported at
all. The 25 m figure carries the only condition DFRobot puts on it - detection at 25 m needs "a
significant movement" and is "depending on the target characteristics" - so it is a best-case,
large-motion number. No range accuracy or resolution is published for either.

SEN0306 is the only honest obstacle radar here. It ranges any reflector, static included, at
+/-0.1 m accuracy and 0.01 m reporting resolution at 10 Hz, and with the mode pin grounded it
emits a 126-line range-FFT magnitude spectrum - the only pre-detection data any DFRobot radar
exposes. The costs are a 0.5 m blind zone, over 100 mA, 0-70 degC only, no velocity, and $65.90.

SEN0676 is a tank-level gauge, listed for completeness. Its 1 mm figure is interpolated sub-bin
precision on a specular return from a flat liquid surface that a human body does not give;
native resolution from the 4 GHz sweep is 37.5 mm.

## Class D - 60 GHz vital signs and fall detection

SEN0623 (C1001), $29.00, in stock, is the only DFRobot radar that reports anything resembling
a class.

| Parameter | Published value |
|---|---|
| Band, power | 61-61.5 GHz, 6 dBm |
| Farthest detection | 11 m, **condition published**: ceiling mount at 2.7 m |
| Detection angle | 100 x 100 deg |
| Sleep mode, chest | 0.4-2.5 m |
| Breathing and heart rate, chest | 0.4-1.5 m |
| Measurement bands | 10-25 breaths/min; 60-100 bpm |
| Supply | 5 V, 100 mA or less; UART 115200 |

The 11 m figure is the only range in this chapter tied to a published mounting geometry. Two
others carry a weaker condition: the C4002's 11 m and 10 m are scoped to a "Motion,
Micro-Motion/Stationary Human Body", and the C4001's 25 m is qualified by "a significant
movement" and "depending on the target characteristics". Every other range number in Class A,
B and C is a bare maximum. No figure anywhere in this chapter, the 11 m included, publishes a
target RCS, a reflectivity, a clutter description or an indoor/outdoor qualification, so every
range here is an upper bound measured under conditions the vendor declines to state.

The C1001 exposes posture and fall state, static-residency and unmanned timers, install height
and tilt configuration, and vital signs. One source file records an `x`/`y` track method in the
library; another records the API as presence, movement class, moving range and fall bit with no
coordinates. Neither reading changes the verdict: the fall algorithm is a posture classifier
referenced to a configured downward ceiling geometry, which a horizontally mounted radar on a
moving 1 m robot does not have. Its wiki FAQ also says it cannot count multiple individuals, and
DFRobot states it is not a certified medical device.

## Interface, power and stock

| SKU | Interface | Supply V | Current mA | Size mm | Stock |
|---|---|---|---|---|---|
| SEN0395 | UART 115200 + GPIO | 3.6-5 | 90 | 24 x 28 | in stock |
| SEN0557 | UART 57600 + GPIO | 5-12 | 80 | 7 x 35 | in stock |
| SEN0609 | UART 9600 + IO | 3.3-5 | not published | 26 x 30 | in stock |
| SEN0610 | I2C 0x2A/0x2B + UART | 3.3-5 | not published | 22 x 30 | in stock |
| SEN0691 | UART 57.6k-1M + OUT | 3.6-5.5 | not published | 22 x 26 | in stock |
| SEN0623 | UART 115200 + IO1/IO2 | 5 | 100 or less | not published | in stock |
| SEN0306 | UART 57600 TX only | 4-8 | over 100 | 34 x 44 x 5 | in stock |
| SEN0192 | Gravity digital pin | 5 +/-0.25 | 60 max, 37 typ | 48.5 x 63 | in stock |
| SEN0676 | UART Modbus | 3.5-5 | 30 | 35 x 35 x 1.2 | in stock |

Supply current is not published for any C4001 or C4002 part. That is three of the four parts
a robot would actually consider, so a ring's power budget cannot be computed from datasheets
and must be measured.

Ring sizing for 360 deg coverage follows from the azimuth beam. With a 120 deg beam,
three SEN0691 nominally close the circle and four give overlap: $26.70 to $35.60 at the
single-unit price of $8.90, or $33.20 for four at the 10-or-more price of $8.30. SEN0557's
+/-60 deg gives the same three-or-four count, $36.80 for four at its 10-or-more price of $9.20.
The 100 deg parts need four with no overlap and five with it: $64.50 for five SEN0610, $69.50
for five SEN0609, and $145.00 for five SEN0395 or five SEN0623, neither of which publishes a
volume tier. Power follows the same split. A four-unit SEN0395 ring draws 360 mA at 5 V, or
1.8 W, and a four-unit SEN0557 ring 320 mA, or 1.6 W. A C4001 or C4002 ring cannot be budgeted
at all until the current is measured.

## Where the sources disagree

- **SEN0691 range.** Store title says 10 m, wiki spec says motion 11 m and static 10 m, the
  GitHub repository says 11 m motion and 11 m static. Three vendor numbers. Plan against 10 m.
- **C4001 velocity.** The datasheet characteristics list says 0.1 to 3 m/s; the same datasheet's
  `$DFDMD` frame definition says 0 to 10 m/s and both product pages say 0.1 to 10 m/s. Treat
  10 m/s as the reported field range and 3 m/s as the specified band. Velocity resolution is not
  published for any part; the I2C transport carries speed as a signed int16 in cm/s, which is a
  bus quantum and not an accuracy figure.
- **C4001 configurable maximum.** Sold as 25 m; the library documents a 2000 cm cap and enforces
  2500. Anything past 20 m is unverified.
- **SEN0395 transmit power.** Wiki says 13-15 dBm, product page says 9-12 dBm. Both first-party,
  unresolved.
- **SEN0623 field of view.** One source records 100 x 100 deg only and withdraws an earlier
  40 x 40 deg sleep-mode figure as unsourced after a re-fetch on 2026-09-12. Another quotes wiki
  installation text describing sleep mode as a tilted install covering 40 deg horizontal and
  40 deg pitch. The likely reconciliation is a spec-table number and a narrower usable sleep
  volume in the install guidance. Use 100 x 100 deg as the specification.

## Ego-motion clutter

These modules assume a fixed installation, and driving the robot destroys the one capability
that justifies choosing mmWave over a passive infrared detector.

An FMCW presence radar separates a person from furniture by Doppler: zero radial velocity is
background, non-zero is a candidate. When the radar translates at velocity `v`, every static
scatterer acquires an apparent radial velocity of `-v cos(theta)`, theta being the angle between
heading and bearing. Three consequences follow.

The whole room becomes a target. Walls, doorframes and table legs enter the Doppler passband,
and the C4001's single target slot goes to whichever return has the highest energy - usually a
wall, not the person.

A standing person becomes invisible in the worst case. Someone standing still directly ahead of
a robot moving at `v` has apparent radial velocity `-v`. So does the wall behind them. They are
Doppler-identical, so clutter rejection tuned at `v = 0` passes both or rejects both.

Nothing here can compensate. The standard fix is to fit the `v cos(theta)` curve across azimuth
and subtract the ego-velocity. No DFRobot radar reports azimuth, elevation or x/y, so with one
range-Doppler pair and no bearing there is no closed-form correction.

Several vendor features make it worse. The C4002's `startEnvCalibration()` learns a static
background and the wiki requires an empty room while it runs. The C4001's disappearance delay
defaults to 15 s, and its library clears a lost target only after about ten empty polls. The
C4002's lock time disables detection for 0.2 to 10 s after every occupied-to-unoccupied
transition. The SEN0395 FAQ offers "please ensure that the sensor is fixed firmly when using it"
as the cure for an output stuck high - a drivetrain supplies exactly that vibration.

DFRobot publishes nothing about moving-platform behaviour for any part. That is not a vendor
defect; it is the wrong sensor class for the mount. Only SEN0306 offers a way out, because its
126-bin spectrum lets you run your own ego-motion-aware detector against wheel odometry.

## Wall penetration

A radar that works through a plastic shell also works through a plasterboard partition. On a
wall-mounted occupancy sensor that is the selling point. On a robot it is a false positive that
never clears and cannot be filtered out by anything the module exposes.

DFRobot publishes no penetration figure, no attenuation table and no wall-material guidance for
any part, and no through-wall measurement was obtained for any part in this study. The only
first-party statement on the subject is SEN0306's, which is described as penetrating
non-metallic materials, dust, smoke and fog. What follows from it is a radome specification -
ABS, PC or PP, no metal, no carbon fill, no metallic paint - and a radome specification is not
a wall-rejection specification. How much of a stud wall these parts see through is unmeasured,
so treat the through-wall false positive as an untested risk rather than a quantified one.

The mitigation that works on a fixed installation does not transfer. You can range-gate:
SEN0691's `setDetectRange` is capped at 0-1100 cm and its per-gate thresholds run 0-99, so gates
beyond the working volume can be suppressed. But a range gate is a radial distance, and a person
2 m away on the far side of a partition sits inside any gate that also contains the room you
care about. Separating them needs bearing or a wall model, and there is neither. On the C4001
the gate is not even hard: the 1 m transition zone leaves soft, non-deterministic edges.

The 60 GHz SEN0623 is the one part where band physics should help, but DFRobot publishes no
attenuation figure for it either, so better wall rejection at 61 GHz is inferred, not verified.

## Micro-motion and the curtain problem

Static-human detection works by finding millimetre-scale chest movement in the zero-Doppler
return. The same processing that finds a breathing person sitting still is what makes a curtain
in a draught, a ceiling fan or a rolling ball read as a person, and no DFRobot module gives you
anything to tell them apart.

The entire feature vector is range, signed radial speed, a scalar energy and - on the C4002 only
- a gate occupancy mask. Energy is dominated by radar cross-section and received power falls as
the fourth power of range, so a cat at 1 m and a person at 3 m can return the same number. The
computed catalogue makes the size effect explicit: scaled by the cross sections this reference
uses (adult standing 0.7 m2, cat 0.012 m2, chair leg 0.01 m2), SEN0691's 11 m reach on an adult
becomes 4.0 m on a cat, SEN0609's 25 m becomes 9.0 m, and SEN0557's 6 m becomes 2.2 m. Speed
overlaps completely, and vital signs do not save it either: the C1001 measures 10-25
breaths/min, and resting cats at roughly 20-30/min and resting dogs at roughly 15-30/min
overlap that band almost entirely.

The vendor says so itself. The SEN0395 FAQ answers directly: "No, the sensor detects movement
of all objects within range by detecting mmWave radar and is very sensitive." Across all six
presence parts, DFRobot's pages, wikis and library READMEs contain zero mentions of pets, pet
immunity, or false triggers from fans and curtains. The topic is absent in both directions.

The filter also cuts the other way, and this is the part that surprises people. The computed
capability grid scores every presence module at level 0 - nothing - against a chair leg at every
survey distance: static clutter rejection removes motionless furniture. The processing that
admits a breathing curtain rejects a chair. Only SEN0306, which has no presence processing,
ranges a static chair leg, at level 2 out to an RCS-scaled 6.9 m.

## What radar is genuinely good for on this robot

Three things, and they are specific.

**A sealed, windowless enclosure.** Radar works through an ABS, PC or PP shell with no aperture,
no glass and no dust path. Keep metal, carbon fill and metallic paint out of the radome, and
keep the wall near a half-wavelength multiple, about 6.25 mm at 24 GHz and about 2.5 mm at
60 GHz.

**A closing-target gate that does not care about light.** The signed radial speed from a C4001
or C4002 is a direct approach/recede bit, computed in the module, in darkness or full sun, at
$8.90. Nothing optical gives velocity without differentiating position first.

**A stationary-robot watchdog.** The strongest case, because it is the duty cycle where every
objection above disappears. Parked or docked, there is no ego-motion, the C4002's environment
calibration is valid, and micro-motion presence works as specified: a still, breathing person at
up to 10 m through the shell, at 10 Hz, for under $10, with no camera and no privacy problem.
Arm it when the wheels stop; disarm it when they turn.

What radar must not be asked to do is identify anything or bound a volume. Species
discrimination needs micro-Doppler on a raw range-Doppler map, and no DFRobot module emits raw
IQ, an ADC stream or a range-Doppler matrix, so no classifier can be built on any of them.
Height, the feature that separates a 300 mm cat from a 1700 mm adult, needs elevation, and no
part reports it - a 300 mm pet does not enter a 40 deg vertical beam until 1.65 m with the
sensor at 900 mm, per the coverage-geometry chapter. A ring of three or four same-band FMCW
modules is an unverified risk too: DFRobot publishes no interference mitigation, no chirp
randomisation, no synchronisation pin and no multi-sensor guidance for any part. Mixing the
61 GHz SEN0623 with 24 GHz units is the only way in this catalogue to keep two modules off one
band, and DFRobot publishes no guidance for that combination either.
