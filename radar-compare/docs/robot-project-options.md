# Options for the three robot projects in this repository

The three robots in `C:/dev/robots` need three different perimeter builds, and the reason is
electrical, not mechanical. `dalek` has the best shell for sensing and the worst electronics to
hang off it. `r2d2` has the thinnest shell of the three and 47 g of mass margin. `fable-r2d2` has
an entirely unused I2C bus, eighteen free GPIO, about 4.1 A of spare 5 V, and two body rings that
have not been drawn yet. One answer repeated three times would be wrong on two of them.

Envelope figures are repo-verified from `research/robot-project-envelopes.md`, which cites the
file each came from. Part figures are datasheet-verified or vendor-page-verified from
`data/sensors.csv`. Coverage arithmetic is not repeated here; `coverage-geometry.md` and the
computed appendix own it.

## The three envelopes side by side

| Property | `dalek` | `r2d2` (revision C) | `fable-r2d2` |
| --- | --- | --- | --- |
| Shape at floor level | Circular fender, 300 mm diameter | Three separate feet, body suspended | Three separate feet, body suspended |
| Overall height | 563.8 mm nominal | 609.6 mm nominal | 715.9 mm (driving stance) |
| Widest plan dimension | 300 mm | ~438 mm side-foot span | ~486.7 mm (repo-derived) |
| Estimated assembled mass | ~3.5 kg (repo-derived) | 8.953 kg of a 9 kg ceiling | 13.273 kg nominal |
| Drive | 4 x TT 3777, skid steer | 6 x TT 3777, 12 wheels, steering servo | 6 x TT 3777, 12 wheels, castering rear |
| Controller | LilyGO TTGO T-Display (classic ESP32) | Adafruit HUZZAH32 3405 | Raspberry Pi 4 4 GB + Adafruit KB2040 |
| Battery | Bioenno BLF-1206A 12 V 6 Ah LiFePO4 | Bioenno BLF-1206A 12 V 6 Ah LiFePO4 | Power-Sonic PS-1270 F2 12 V 7 Ah SLA |
| Spare 5 V logic current | ~0.3 A | not specified in the repo | ~4.1 A |
| Free GPIO on the main MCU | essentially none | one pin (GPIO5) | Pi: 18. KB2040: one (D0/GP0) |
| Free I2C bus | shared 0x40 bus only | shared bus, 0x40 + 0x48 used | Pi I2C-1 + an unused KB2040 STEMMA QT bus |
| Head/dome wiring path | none (no slip ring) | none (no slip ring) | 12-wire slip ring, all 12 assigned |
| Shell wall at a candidate aperture | 1.8 mm PLA skirt / 4 mm PETG base ring | 1.2 mm PETG body skin | 3.6 mm PETG body / 3.0-3.2 mm dome |
| Existing ranging or presence sensor | none | none | none |

## `dalek` - the robot that must not be cut

### Mounting surfaces and apertures

The base fender band, world Z13.8 to Z67.8, is the right height for a pet and a forbidden place
to work. `docs/mechanical.md` states the rule that "the outside bumper remains continuous around
the full circle", and `cad/mechanical-checks.json` carries a passing 2,880-sample check named
`continuous-bumper-missing-material`. A window there breaks a released validation check.

That leaves the lower skirt, world Z67.8 to Z177.8, 110 mm tall, tapering 300 mm to 250 mm in
1.8 mm PLA. It is the thinnest wall on any of the three robots. It already carries twelve
vertical seams at 30 deg pitch and twelve hemispheres per row at world Z93.8 and Z143.8, so a
panel has to sit in the roughly 65 mm of clear arc between two seams. The head is unusable: no
slip ring, and no head-angle encoder, so a head sensor would have no known bearing.

Because the bumper cannot be cut and the skirt is crowded, this is the one project where seeing
*through* the shell is worth more than seeing through a hole. The 24 GHz parts in
`data/sensors.csv` are recorded as `sees_through_plastic = yes` and need no aperture at all.

### Bus, pins and current

`docs/firmware.md` allocates every pin the T-Display breaks out. No free interrupt line, no free
UART, no free XSHUT line. The I2C bus on GPIO21/22 carries one device, a PCA9685 at `0x40`;
everything else is free, including `0x29`, `0x2A` and `0x2B`.

That decides the part. A UART radar is unusable. A ring of ST multizone parts is unusable,
because every VL53 unit boots at `0x29` with a volatile address and so needs one XSHUT GPIO per
unit or an I2C multiplexer. The DFRobot SEN0610 is the one presence radar in the catalogue with
a native I2C interface, strapped to `0x2A` or `0x2B`. Two addresses exist, so two units is a hard
ceiling, not a budget choice.

Spare current is 0.30 A on the 5V_LOGIC rail (Adafruit MPM3610 4739, 1.2 A unconditional over
6-21 V in, against a 0.90 A design load). That is the binding constraint on the whole robot. The
two 5 V actuator rails are cut by the S2 stop switch, so a sensor must never sit on them: it
would go blind at the moment the operator hits stop.

### Recommendation

- 2 x DFRobot SEN0610 Gravity mmWave C4001, 100 x 80 deg (horizontal x vertical), I2C at `0x2A`
  and `0x2B`. USD 12.90 each.
- 1 x Adafruit 5425 VL53L4CX single-zone ToF, 18 x 18 deg, I2C `0x29`, 19 mA. USD 14.95.
- Total USD 40.75.

Mount both radars flat inside the lower skirt, boresight horizontal, centred at world Z120, each
between two seams, one on the front centreline and one at 180 deg. No aperture, no cut, no change
to any released STL. Two 100 deg beams leave two side gaps; that is the honest cost of the
two-address ceiling.

The VL53L4CX closes the radar's own blind zone, and that is why it is in the list. The C4001
datasheet gives no output below 1.2 m, which is exactly the collision zone on a 300 mm robot.
Fit it on the front centreline at world Z120, tilted 5 deg down, through a single window in the
same 1.8 mm skirt, sized from the ST package drawing. Put nothing over that window: the
ams-OSRAM TMF8806 datasheet shows one layer of tape costing 340 mm of range - 1840 mm down to
1500 mm - on an 18 percent grey target under 170 lux halogen, the 1 klux sunlight-equivalent
condition, and the same physics applies to any dToF cover.

Wiring is four conductors from the GPIO21/22 header to each module, powered from 5V_LOGIC only,
with no new pull-ups.

**Where this does not fit.** DFRobot does not publish a supply current for the C4001, so the
build cannot be closed against 0.30 A on paper. Measure one unit before buying the second. If the
pair exceeds about 280 mA, the option that fits is a second Adafruit MPM3610 4739 off the 12 V
bus upstream of the stop switch, giving the sensors their own 1.2 A rail. The MPM3610 rating
carries no input-voltage condition, so that rail is honest at 12 V, unlike the D36V50F5 figures.

## `r2d2` - 47 g of margin and one free pin

### Mounting surfaces and apertures

There is no skirt. The lower body mesh starts at world Z130 and the cylindrical wall at Z165;
below Z130 is open air between three feet. The rear foot translates 119 mm fore-aft with posture
(centre from Y = -128.926 to Y = -247.785), so anything mounted in it moves relative to the body.
A floor-level ring is mechanically awkward here in a way it is not on `dalek`.

The body skin is a clean 1.2 mm PETG cylinder of 259.25 mm diameter, the thinnest shell of the
three. Every "radar eye", logic display and utility arm on it is painted relief, and
`cad/exterior.scad` `body_panel_channels()` engraves only to a remaining wall of 0.75 mm or
more, so there is no existing through-cut to reuse. Cutting a fresh one disturbs no validated
mechanism, unlike the Dalek's bumper. The dome is unusable: no wire crosses the rotating joint.

### Mass, bus, pins and current

`docs/verification.json` gives 8.953 kg against a 9.000 kg design ceiling, and
`docs/mechanical.md` states there is "no payload allowance". **47 g is the entire sensor budget,
brackets and cable included.** That rules out an eight-unit ring before any electrical argument
is made; the right answer is the fewest parts that reach capability level 2.

The HUZZAH32 has exactly one free pin, GPIO5. There is no free UART: GPIO16/17 are the post
limits and the head bridge. The I2C bus uses `0x40` (INA219) and `0x48` (ADS1115), so a part
defaulting to either collides; `0x29` and `0x2A` are free. One free pin buys an interrupt line
or one XSHUT line, not both, and that is the design decision on this robot.

Spare current is not specified in the repo. `docs/electrical.md` allots the whole 1.2 A of the
5V_LOGIC rail (Adafruit 4739, U6) to logic in its 60.9 W sizing, but never states what the
Feather plus ADS1115 plus INA219 plus MAX98357A actually draw.

### Recommendation

- 1 x Pololu 3419 VL53L8CX 8x8 multizone ToF, 45 x 45 deg, I2C `0x29`, 93 mA. USD 24.95.
- 1 x DFRobot SEN0610 Gravity mmWave C4001, 100 x 80 deg, I2C `0x2A`. USD 12.90.
- Total USD 37.85.

Cut one window in the lower body band at world Z200 on the front centreline and set the VL53L8CX
behind it, tilted 8 deg down. One unit keeps its factory `0x29` and needs no XSHUT, so **spend
GPIO5 on its interrupt line**, which is what makes a 15 Hz 64-zone part usable on a busy ESP32.
Choose it over the cheaper VL53L5CX for ambient-light performance: 1650 mm inner and 1550 mm
corner against a 17 percent grey target under 5 klux at 4x4 and 30 Hz.

Mount the radar behind the intact 1.2 mm skin at world Z220 on the rear centreline, with no
aperture. Rearward is deliberate: the rear foot moves 119 mm during posture changes and nothing
else on this robot can see behind it. Power both from 5V_LOGIC (U6). `docs/electrical.md` forbids
powering anything through the Feather BAT/JST socket, and warns against adding 5 V pull-ups on
top of the breakouts' own.

**Where this does not fit.** Two unknowns multiply: the rail's real headroom and the SEN0610's
unpublished current. Measure the idle 5V_LOGIC draw before ordering. If the spare is below about
100 mA, drop the VL53L8CX and fit 2 x Adafruit 5425 VL53L4CX instead (USD 29.90, 38 mA, 18 x
18 deg each), using GPIO5 to hold the second in reset at boot so it can be readdressed. One XSHUT
pin brings up exactly two units, which is why two is the count. That trades a 64-zone grid for
two narrow beams and stays inside a 100 mA rail.

One further caution: `cad/printed-frame.scad` and `docs/printed-frame-research.md` are
uncommitted and describe a revision D that would replace the cut-metal frame. Any bracket keyed
to the revision C chassis may not survive it. Both mounts above are keyed to the skin instead.

## `fable-r2d2` - the only project that can take the full build

### Mounting surfaces, apertures, and a door still open

`cad/body.scad` is a three-line stub, and `cad/validation.json` and `bom/printed-parts.csv` both
record `body_upper` and `body_lower` as `"pass_check": false, "error": "missing STL"`. **The two
body rings have not been designed.** Apertures, flat mounting bosses and locally thinned panels
go into them now at zero rework cost. Nowhere else in the repository is that true.

The lower body ring runs from about 205.8 mm to 341 mm above the floor in the driving stance,
3.6 mm PETG on a 317 mm diameter; the rear band carries the J1 charge jack and the SW1 rocker,
and the front is clear. The skirt below, 164.5 to 205.8 mm, has flats only at Y = +/-94.85. The
dome has real through-cuts and every one of them is occupied.

The stance is the trap. The body is tilted back 18 deg in the three-leg driving stance, so a
sensor normal to the skin points 18 deg **up** at the front, level at the sides, and 18 deg down
at the rear. A ring of identical bosses would aim the forward units at the ceiling. Each boss
angle must carry its own azimuth correction on top of the common downtilt, and that correction
is the single most important thing to get into `body.scad` before it is released.

### Bus, pins and current

Pi I2C-1 uses `0x70`-`0x73` (four HT16K33) and `0x48` (ADS1115). Confirmed free: `0x29`, `0x30`,
`0x40`, `0x52`, `0x68`, `0x74`, `0x75`, `0x76`, `0x77` - nine addresses for a nine-unit ring, an
exact fit. Eighteen Pi GPIOs are free, so each unit gets its own XSHUT line and no multiplexer
is needed. Separately, the KB2040's STEMMA QT connector is unpopulated and its whole I2C bus is
unused, because `board.SDA`/`board.SCL` are GP12/GP13 while the motors use D2 to D10. Every
address on it is free.

About 4.1 A of 5 V is spare against a 1.40 A design load. The Pololu measurement-condition caveat
applies here as on the Dalek - 5.5 A is quoted "at 36 V in" against a family range of 3.5 A to
8 A - but the conclusion survives, because 1.40 A is a quarter of even the pessimistic 3.5 A end.

### Recommendation

- 9 x Pololu 3419 VL53L8CX, 45 x 45 deg, 93 mA each, USD 24.95 each = USD 224.55.
- 1 x Adafruit 4407 MLX90640 32x24 thermal array, 55 x 35 deg, I2C `0x33`, 23 mA. USD 74.95.
- 1 x Adafruit 6426 STHS34PF80 IR presence sensor, 80 deg, I2C `0x5A`, 10 uA. USD 14.95.
- Total USD 314.45, about 860 mA.

Nine VL53L8CX close the circle at 40 deg boresight pitch. Nine is the count, not eight:
`coverage-geometry.md` shows that eight 45 deg sensors total exactly 360 deg, which leaves each
pair of adjacent edge rays parallel and eight wedges open to infinite range. Nine gives 5 deg of
overlap and a ring that closes at a finite distance. Set them in body-frame bosses 90 mm above
the skirt bottom edge, in the lower body ring, with a common 5 deg downtilt plus the per-azimuth
stance correction. Height above the floor then varies around the circumference by up to about
+/-49 mm (repo-derived: the 158.5 mm body radius times the sine of the 18 deg stance tilt); take
the per-unit figure from the stance transform in CAD. Each boss is a flat pad with a
through-window, not a thinned panel - for dToF the window is a hole.

Put the ring on Pi I2C-1 at 1 MHz, with nine Pi GPIOs as XSHUT lines, bringing each unit up in
turn and readdressing it to one of `0x29`, `0x30`, `0x40`, `0x52`, `0x68`, `0x74`, `0x75`,
`0x76`, `0x77`. The addresses are volatile, so that sequence runs on every boot. Nine XSHUT lines
still leave nine of the eighteen free Pi GPIOs unspent.

Put the MLX90640 and the STHS34PF80 on the **KB2040 STEMMA QT bus**, which is the point of that
free resource. The MLX90640 is a 400 kHz part whose single frame costs about 42 ms of bus time;
on the Pi bus it would drag the ring down from 1 MHz and cost it frame rate. On its own bus it
costs nothing. Mount it on the front centreline tilted 20 deg down, which the catalogue records
as the best single thermal configuration available, and it is what lifts this robot from
capability level 2 to level 3-4 across its 55 deg forward field. The STHS34PF80 is the 10 uA
always-on wake-up layer for a parked robot, and it holds a stationary human, which no PIR does.

Power everything from the 5 V rail. Three rules in `docs/electrical.md` must not be broken: never
feed a DRV8833 from the 12 V bus, never connect the KB2040 RAW pin to the 5 V rail (it is powered
only by the Pi's USB port), and power the Pi only through its USB-C input. Nothing crosses the
slip ring; all twelve wires are assigned.

**Two flags.** Adafruit lists 4 in stock of the 55 deg MLX90640 (4407) and the 110 deg version
(4469) is out of stock, so source the thermal part first. And the centre-of-gravity, foot-share
and tip-back figures are marked invalid in `docs/mechanical.md`, because the built geometry has
the centre foot trailing by 39.2 mm where `research/loads.md` assumed it led by 290 mm. This ring
is low and light, but that re-run is owed before any mass goes high up.

## Cliff and stair sensing - the layer none of the three builds carries

The brief asks the robot never to fall down a stair, and none of the three rings above answers
that. `docs/the-problem.md` calls drop detection "a separate mandatory function" and asks for
time-of-flight at 50 Hz or better, wired so that a lost reading counts as a cliff.
`docs/coverage-geometry.md` adds that down-canted cliff sensors "are not part of the perimeter
ring and must not be traded against it". So each build needs a second, cheap layer.

The catalogue part is the Adafruit 5396 VL53L4CD: USD 14.95, 22 mA, 18 x 18 deg, I2C `0x29`,
100 Hz, 1.3 m of range and 0.45 m against a dark target. Its 100 Hz rate clears the 50 Hz rule.
`docs/coverage-geometry.md` gives the geometry: at 200 mm mounting height and a 30 deg down-cant
the look-ahead is 346 mm, the flat-floor return 400 mm, and a 180 mm stair riser moves that
return to 760 mm, so a "beyond 500 mm means cliff" threshold has margin both ways. Below about
20 deg of cant the return off tile or polished wood goes specular and reads as a phantom cliff.

Every VL53 part boots at `0x29`, so a cliff group needs one XSHUT line per unit or a
multiplexer. That is where each robot stands.

| Project | Where a cliff group can go | What it costs |
| --- | --- | --- |
| `dalek` | Nowhere on the present pin budget. `0x29` is taken by the VL53L4CX and no GPIO is free for an XSHUT line, so the 8-channel I2C multiplexer priced at USD 6.95 in `integration.md` is the only route. Its `0x70` default is free. | 22 mA per unit against 0.30 A spare, which makes the second MPM3610 rail near-certain. |
| `r2d2` | The same multiplexer answer: GPIO5 is already spent on the VL53L8CX interrupt line, and `0x70`-`0x77` are free. | 22 mA per unit on a rail whose real headroom is unmeasured, and each unit's mass comes out of the 47 g. |
| `fable-r2d2` | The KB2040 STEMMA QT bus, where every address is free and the thermal pair uses only `0x33` and `0x5A`. Nine free Pi GPIOs remain after the ring's XSHUT lines. | 22 mA per unit against about 4.1 A spare. Nothing binds. |

How many units each robot needs is a coverage question, not an envelope question, and
`coverage-geometry.md` owns it. What this chapter can say is that `fable-r2d2` is the only one of
the three that absorbs the group without a new rail, a new multiplexer or a mass re-check.

## Summary

| Project | Tier | Parts | Cost | Current | Deciding constraint |
| --- | --- | --- | --- | --- | --- |
| `dalek` | Level 2 forward, 1-2 around | 2 x SEN0610, 1 x VL53L4CX | USD 40.75 | 19 mA plus radar (not published) | 0.30 A spare and zero free GPIO |
| `r2d2` | Level 2 forward, 1 rear | 1 x VL53L8CX, 1 x SEN0610 | USD 37.85 | 93 mA plus radar (not published) | 47 g of mass margin |
| `fable-r2d2` | Level 2 all round, 3-4 forward | 9 x VL53L8CX, 1 x MLX90640, 1 x STHS34PF80 | USD 314.45 | 860 mA | Nothing binds; `body.scad` is unwritten |

Capability levels are the `data/capability.json` scale: 1 presence only, 2 obstacle plus range,
3 living versus not, 4 human versus pet. The table covers the perimeter build only. Cliff and
stair sensing is additional on all three, at USD 14.95 and 22 mA per VL53L4CD.

Two of the three totals cannot be closed on paper, both for the same reason: DFRobot does not
publish a supply current for the C4001 modules. That is a one-meter measurement, not a research
problem. Do it before ordering either radar.
