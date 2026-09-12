# The answer, first

A 350 mm robot needs **twelve multizone time-of-flight sensors in the perimeter ring, six
downward cliff sensors, and eight thermal arrays** to do the whole job the brief describes:
avoid every obstacle through 360 degrees, never fall down a stair, know a person is there, and
know the difference between a person and a pet. That is nineteen ToF modules and eight people
sensors, about USD 909 and about 1.0 A at 5 V.

If the budget only stretches to collision avoidance, the number is **eighteen ToF modules and
zero people sensors**, about USD 455. That build is honest about what it is: a bumper made of
light. It cannot tell you anything is alive.

| | Minimum: collision only | Recommended: collision + animate | Maximum: full classification |
|---|---|---|---|
| ToF modules | 18 (12 ring, 6 cliff) | 19 (12 ring, 6 cliff, 1 scanner) | 24 (16 ring, 6 cliff, 1 head, 1 scanner) |
| People sensors | 0 | 8 thermal arrays | 6 thermal + 4 cameras |
| Hardware cost | USD 455 | USD 909 | USD 1,440 |
| Average current at 5 V | 724 mA | 999 mA | 3.8 A |
| "Will I hit it?" | Yes, 360 deg | Yes, plus dark targets and sunbeams | Yes |
| "Is it alive?" | No | Yes, to about 2.4 m for a pet, 5 m for a human | Yes, in darkness too |
| "Human or pet?" | No | By fusion, to about 5 ft | Labelled, to 10 ft |

## The five things that decide this design

**1. Use the horizontal field of view, never the diagonal.** Every ST VL53 datasheet leads with a
diagonal figure. It is a separately measured number, not the geometric diagonal of the square
detection volume, so it cannot be converted by dividing by the square root of two. The VL53L5CX
is 63 deg diagonal and **45 deg horizontal**. The VL53L7CX is 90 deg diagonal and **60 deg
horizontal**. The VL53L1X is 27 deg diagonal and about **19 deg horizontal**. Sizing a ring from
the diagonal understates the count by three to six sensors, and this document's own first-pass
research made exactly that error before the verification pass caught it.

**2. A ring closes only when `n x FoV > 360`, and "exactly 360" is the one value to avoid.** At
exactly 360 the edge rays of adjacent sensors are parallel, so they never meet at any finite
range and the wedge between them is blind forever. Eight VL53L5CX at 45 deg is exactly 360 deg
and it does not work.

**3. The sensors sit on the rim, not at the centre, so even a closed ring is blind near the
robot.** On a 175 mm radius the wedges between adjacent sensors close at a range

```
u = r sin(a) / sin(a - s)
    a = half the horizontal field of view
    s = pi / n
    r = the mounting radius, 175 mm
```

measured from the platform centre. Twelve VL53L5CX close at 513 mm from the centre, 338 mm past
the edge. Sixteen close at 343 mm from the centre, inside the robot's own 350 mm footprint. Both
figures appear in this document and they do not disagree: **twelve** is the recommended build,
whose near-field wedge is covered by a compliant bumper, and **sixteen** is what it costs to
close the wedge inside the footprint and drop the bumper from the safety argument.

These closure figures were derived twice, independently and by different algebra - once by a
research agent working from the platform geometry, once by `radar-compare/scripts/geometry.py`
solving the bisector intersection directly. They agree to the tenth of a millimetre at every
count checked: 513.1 mm for twelve at 45 deg, 343.3 mm for sixteen at 45 deg, 670.4 mm for eight
at 60 deg, 1170.9 mm for seven at 60 deg, and 343.0 mm for the thirty-eight single-zone VL53L1X
sensors it would take to close a ring at 19.27 deg.

**4. Mounting height decides what the robot runs over, and it is not a detail.** A ring at 800 mm
with a 45 deg vertical field of view cannot see a standing cat at 1 ft or at 3 ft at all - the
animal is entirely beneath the beam. A ring at 100 to 200 mm sees everything from a sleeping cat
upward, at the price of a floor return in every frame. Put the collision ring low.

**5. Classification must never gate the stop.** There are 167 to 323 ms between the warning-field
edge and the protective-field edge for a target walking toward the robot. Micro-Doppler needs
about 250 ms of dwell to reach 75 percent; ST's own people-counting reference uses a 2.1 s
window; a thermal frame at 4 Hz is 250 ms by itself. Braking runs on raw geometry at ring frame
rate. Classification runs in parallel and changes only what the robot does *after* it has
stopped.

## What this costs you to ignore

- **24 GHz presence radar is rejected for this robot**, despite being the obvious answer for
  people sensing. Those modules assume a fixed installation. Their static-clutter rejection is
  the only thing that makes them useful, and a driving robot gives every static object an
  apparent velocity, which leaves the filter nothing to reject. They also see through walls, so
  they report the person in the next room as a perimeter contact. Radar earns its place on this
  robot only where it can hide behind a printed shell that a ToF sensor cannot see through.
- **Nothing here carries a safety rating.** A certified IEC 61496 Type 3 scanner must prove
  detection against a 1.8 percent reflectance target inside its protective field. A VL53L8CX does
  not meet that, which is exactly why a certified scanner sees a black sock and this stack does
  not. Use the industrial arithmetic; do not claim the rating.
- **No combination in this document tells a cat from a dog without a camera.** Nor does any of it
  work in direct sunlight above about 5 kLux, which is where ST's published tables stop and
  direct sun is 100 to 120 kLux. Mirrors defeat all of it.

## Two standalone product guides

The operator asked for two parts to be assessed on their own, independent of the ring
recommendation. Both chapters read without the rest of the document.

- **ST multizone grid time-of-flight.** The latest grid part as of 2026-09-12 is the **VL53L9CX**,
  a 54 x 42 zone, 2268-zone stacked imager with MIPI output, announced with mass production from
  early July 2026. It is a camera module, not a microcontroller peripheral, and it is not a
  drop-in for anything. The part to actually build with is the **VL53L8CX**.
- **Adafruit 4010** is the **Slamtec RPLIDAR A1M8**, a 360 deg spinning laser scanner at USD
  99.95, in stock. It is not a proximity sensor and it is easily confused with the unrelated
  Vishay VCNL4010. It is the best single "see everything around me" part in its price class and
  it classifies nothing at all.

## How to read the rest

The catalogue chapters list every candidate part with its measurement conditions. The master
grid rates each one against an adult, a cat and a 30 mm chair leg at 1, 3, 5, 8 and 10 ft, by a
published rule rather than by opinion. The computed appendix carries every geometry table, all of
it generated by `radar-compare/scripts/geometry.py` from first principles rather than copied from
a vendor page. The last chapter gives a different answer for each of the three robot projects in
this repository, because their pin, bus and shell budgets are genuinely different.
