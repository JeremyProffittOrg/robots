# The best three options

**Build option B.** Twelve VL53L8CX in a ring at 200 mm, six VL53L4CD cliff sensors at 150 mm, one
RPLIDAR C1 at 100 mm, and eight AMG8833 thermal arrays at 250 mm. USD 909, about 1.0 A at 5 V. It
is the cheapest build that answers all four questions the robot has to ask, and every part of it
is in stock today.

| | **A - Collision only** | **B - Collision + animate** | **C - Full classification** |
|---|---|---|---|
| Time-of-flight modules | 18 | 19 | 24 |
| People sensors | 0 | 8 thermal | 6 thermal + 4 cameras |
| Cost | USD 455 | **USD 909** | USD 1,440 |
| Average current at 5 V | 724 mA | 999 mA | 3.8 A |
| Compute needed | RP2040 | RP2040 | Pi 5 + Hailo-8L |
| Will I hit it? | Yes, 360 deg | Yes, plus dark targets and sunbeams | Yes |
| Is it alive? | **No** | Yes, ~2.4 m pet / ~5 m human | Yes, in darkness too |
| Human or pet? | **No** | By fusion, to about 5 ft | Labelled, to 10 ft |
| Sees a black cat on dark carpet | To 1.55 m | **To 6 m** | To 6 m |
| Sees a sleeping cat | Only as an obstacle | **Yes, as an animal** | Yes |

## Option A - `collision-ring`, USD 455

Twelve VL53L8CX multizone carriers (Pololu 3419, USD 24.95) in a ring at 200 mm on 30 deg
spacing, six VL53L4CD (Pololu 3692, USD 13.95) canted 23 deg down at 150 mm for cliffs, two
PCA9548 multiplexers, and a compliant foam bumper.

**What it buys.** A bumper made of light. Full 360 deg obstacle detection with range, closing its
blind wedges 338 mm past the skin, refreshing fast enough to stop a 0.5 m/s robot.

**What it cannot do.** Anything in the brief except collision avoidance. It has no human channel
and no pet channel, and it loses a dark target past about 1.55 m in a lit room. In a patch of
direct sun it reports *empty space*, not noise, which is the dangerous failure.

## Option B - `collision-ring + animate-layer`, USD 909 - RECOMMENDED

Option A plus one Slamtec RPLIDAR C1 (USD 69) with its scan plane at 100 mm, eight AMG8833
thermal arrays (Adafruit 3538, USD 44.95) level at 250 mm on 45 deg spacing, and two RCWL-1601
ultrasonic rangers forward for glass.

**Why the C1 is the best USD 69 in the study.** It fixes both structural weaknesses of a ToF ring
with one cable: 6 m against a 10 percent black target where the ring manages 1.55 m, a 40,000 lux
rating where the ring is only characterised to 5 kLux, a plane low enough to cut a cat lying on
its side, and 500 points per revolution - enough to scan-match a background map, after which
anything that does not fit the map is dynamic. That is the strongest animate cue available
without a camera.

**Why thermal and not radar.** Thermal is the only modality that separates animate from
inanimate, and the only one that sees a *motionless* target. A sleeping cat is invisible to
motion-gated radar and invisible to PIR, and obvious to thermal.

**What it cannot do.** Cat versus dog. Classification in a dark room beyond thermal's pixel
limit. Anything at all in direct sunlight.

## Option C - `full-classification-stack`, USD 1,440

Sixteen VL53L8CX, six MLX90640 32x24 thermal arrays, a VL53L8CH histogram head, the C1, four
wide-angle cameras and a Raspberry Pi 5 with a Hailo-8L.

**What the extra USD 531 buys.** Labelled classification out to 10 ft, and a ring tight enough
that the blind wedge closes 168 mm past the skin - inside the robot's own footprint - which lets
the compliant bumper stop being part of the safety argument.

**Why it is third.** It costs 2.8 A more and needs a Pi 5 to run. One of its six MLX90640 arrays
is out of stock as of 2026-09-12, and two of its line items have no published price. Buy it only
if labelled classification is a requirement rather than a wish.

## How to choose

Pick **A** if the robot only has to not hit things and you will keep it away from people and
animals. Pick **B** in every other case. Pick **C** only if you need the robot to say the word
"person" or "pet" out loud and act differently on each, at ten feet, reliably.

The gap that matters is A to B: USD 454 and 275 mA buys the entire animate layer plus the two
fixes - dark targets and sunlit floors - that would otherwise put the robot on the floor or on
the cat. The gap from B to C buys one capability for USD 531 and a different computer.

## What your three robots should actually do

None of the three projects in this repository can take Option B as drawn. Their electronics, not
their mechanics, are the binding constraint.

| Project | What fits | Cost | Deciding constraint |
|---|---|---|---|
| `dalek` | 2 x SEN0610 radar, 1 x VL53L4CX | USD 40.75 | 0.30 A spare and zero free GPIO. Its bumper cannot be cut, so radar behind the 1.8 mm skirt is the only sensor that needs no aperture. |
| `r2d2` | 1 x VL53L8CX, 1 x SEN0610 | USD 37.85 | 47 g of mass margin against a 9 kg ceiling, and one free pin. |
| `fable-r2d2` | 9 x VL53L8CX, 1 x MLX90640, 1 x STHS34PF80 | USD 314.45 | Nothing binds - a Pi 4, 4.1 A spare and an entirely unused STEMMA QT bus. Its body STLs are not drawn yet, so the apertures can still be designed in. |

Build the full Option B on `fable-r2d2`. It is the only one with the current, the bus and the
unwritten CAD to absorb it.

## Four things no option does

- **Direct sunlight.** ST publishes to 5 kLux and the C1 to 40 kLux. Direct sun is 100 to 120
  kLux. No number exists beyond that; do not extrapolate one.
- **Mirrors.** A mirror at 45 deg returns a folded path and the robot believes the corridor
  continues. Map them as permanent keep-out zones.
- **Cat versus dog**, without a camera.
- **Any safety rating.** A certified IEC 61496 Type 3 scanner must detect an 1.8 percent
  reflectance target in its protective field. A VL53L8CX does not meet that. Use the industrial
  arithmetic; do not claim the rating.

## Three decisions worth more than the parts list, and they are free

1. **Make the platform round.** A 350 mm square has a 72.487 mm corner protrusion that four
   45 deg sensors on the face centres leave permanently uncovered.
2. **Cap speed at 0.5 m/s.** A 15 kg robot at 1.0 m/s with a rigid shell delivers about 1500 N
   into a shin against a 130 N ISO/TS 15066 limit. At 0.5 m/s with a 50 mm foam bumper it
   delivers 38 N. Speed is the cheapest safety component in the build.
3. **Never let classification gate the stop.** There are 167 to 323 ms between the warning field
   and the protective field. Thermal needs 250 ms for one frame. Brake on raw geometry at frame
   rate; classify in parallel and change behaviour only after the robot has stopped.

*Before ordering either radar, measure the C4001 supply current. DFRobot does not publish it, and
it is the one number that can still move the `dalek` and `r2d2` totals. That is a one-meter
measurement, not a research problem. Prices read 2026-09-12; nothing has been purchased or
physically tested.*
