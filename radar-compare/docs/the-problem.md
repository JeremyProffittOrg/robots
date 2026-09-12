# What perimeter detection has to do

Perimeter detection on a small indoor robot is four jobs, not one. They have different targets,
different update rates and different failure directions, and the commonest error in this field is
buying one sensor and assuming it covers all four. It does not.

## The robot this document is written against

A mobile robot with a **350 mm square or 350 mm round footprint**, **600-1200 mm tall**, **5-15 kg**,
moving at **0.2-0.5 m/s** on hard floor and carpet indoors, among adults, children and pets. The
0.5 m/s upper bound is not arbitrary: it is the household speed ceiling, against which 1.0 m/s on a
10-15 kg robot in a home is called indefensible (`safety-and-failure-modes.md`).

Three consequences of that shape drive everything downstream.

- **The centre-to-skin radius is 175 mm.** Sensors sit on the perimeter, not at the centre, so a ring
  of them is blind in a wedge close to the body (computed, `coverage-geometry.md`).
- **A 350 mm square is 494.975 mm across the corners**, the corner protruding **72.487 mm** past the
  inscribed circle. A scheme that forgets the 495 mm diagonal clips door frames (computed).
- **The centre of gravity is high.** A robot with its CG at 600 mm cannot brake harder than
  **2.86 m/s2** without pitching onto its face (inferred, `safety-and-failure-modes.md`). That, not
  tyre grip, is the deceleration ceiling, and it sets the stopping distance every detection range
  must beat.

The speed band is a safety choice. ISO 3691-4 Annex A Table A.1 permits **0.3 m/s** for a driverless
industrial truck whose personnel detection is muted (standard-verified against the 2020 first
edition, via the TUV Rheinland whitepaper). A 15 kg robot at 1.0 m/s with a rigid shell delivers a
mean **1500 N** into a shin, about 11x the 130 N ISO/TS 15066 transient limit; at 0.5 m/s behind a
50 mm compliant bumper it delivers **38 N** (computed, vendor-page-verified limits).

## The four jobs

**Collision avoidance.** Do not hit anything, of any material, at any height the body occupies, in
any light. The hard targets are not people: they are a **30 mm chair leg** and a **6 mm cable**. A
chair leg at 5 ft subtends **1.32 deg** (computed, `coverage-geometry.md` Table 16, at that document's
35 mm chair-leg width), while an 8x8 zoned array at 45 deg horizontal gives **5.625 deg** cells, or
**149.7 mm** at 5 ft (computed). The array detects a leg; it cannot classify it. This job needs
geometry and coverage, not semantics.

**Cliff and drop detection.** Do not fall down a stair. It is a separate mandatory function: a
horizontal scan plane at 150-200 mm sees nothing at a stair nosing, because the floor simply stops.
At 0.5 m/s with a 100 ms loop the robot travels **92 mm** after the edge is seen; at 1.0 m/s it
overruns the 175 mm half-footprint at every plausible latency and goes over (inferred). Downward
time-of-flight at 50 Hz or better, wired so that a lost reading counts as a cliff.

**Human awareness.** Know a person is there, where, and how far, for the stop and for the
interaction. The governing number is not the robot's speed: ISO 13855 uses **K = 1600 mm/s** for a
walking approach, so a robot at 0.5 m/s meeting a walking person closes at **2.1 m/s**, not 0.5.

**Pet awareness.** Know a cat or small dog is there. This is the hardest of the four, because a cat
is small, low, fast, silent and usually **lying still**. A sleeping cat is 300 x 130 mm: below every
turret-height scan plane, and below every warm-body threshold a radiator also trips. The empirical
ceiling is published. In the Oxford robotic-mower study, 19 models were run against hedgehog
cadavers and, apart from one incidence not reproducible on retest, **all had to physically touch the
carcass to detect it** (peer-reviewed, `prior-art-commercial.md`).

## The subjects, and where their numbers come from

These are **design assumptions, not measurements**, carrying no percentile and no anthropometric
source. They are what the geometry appendix and every capability table here are computed against.

| Subject | Width (mm) | Height (mm) | Note |
|---|---|---|---|
| Adult torso | 450 | 1700 | shoulders 400-500 mm |
| Adult leg | 140 | 800 | what a low ring actually sees |
| Toddler | 250 | 850 | 2 to 3 years old |
| Large dog | 250 | 650 | labrador at the shoulder |
| Cat, standing | 140 | 250 | at the shoulder |
| Cat, lying | 300 | 130 | the worst case |
| Chair leg | 30 | 430 | thin vertical obstacle |
| Power cable | 6 | 6 | the classic robot killer |
| Table top | 900 | 40 | overhang, floor gap 700 mm |

The overhang matters as much as the cable: a 600-1200 mm robot passes its body under a 700 mm table
edge that no perimeter ring mounted below that height can see.

## Why one sensor cannot do all four

Start from the honest framing: **none of these parts is safety-rated.** Not one sensor a hobbyist can
buy is electro-sensitive protective equipment under IEC 61496, with a declared response time, a
declared minimum detectable object and dual outputs that go safe on internal fault
(`safety-and-failure-modes.md`). Every protective field in this reference is industrial arithmetic
applied to uncertified parts.

Each modality has a **fail-to-danger** mode, and each has a different physical cause.

- **Optical time-of-flight** is defeated by black. Against black vinyl the VL53L5CX returned only
  **18.8 % valid measurements at 25 cm** (peer-reviewed-measured). A person in black jeans reads as
  an empty corridor.
- **2D lidar** is one horizontal slice. The 130 mm lying cat is under it; the 700 mm table edge is
  over it.
- **mmWave radar** cannot see a motionless person without micro-motion processing, which needs a
  **1-2 s dwell** (vendor-page-verified), and every static return acquires a Doppler shift once the
  robot itself moves.
- **Thermal arrays** lose a pet with range: of six thermal-IR arrays in the catalogue, four reach a
  standing cat at 1 and 3 ft, two at 5 ft, and **one at 8 and 10 ft** (computed from
  `capability.json`).
- **PIR** cannot see a still person at all, by design, and fires continuously on a moving platform.
- **Ultrasonic** is the one modality that sees glass and mirrors, and the one that loses people. Most
  HC-SR04 units are unreliable on soft targets such as a human beyond about **1 m**, where the
  successful-measurement rate falls **below 50 %** (vendor-page-verified), and eight of them fired
  round-robin take **264 ms** for one sweep. It is a warning-field part, never a stop part.

Two modalities with *different* physics remove the shared blind spot. That, not accuracy, is the
argument for fusion, and the prior art agrees: every top scorer in the one consistent public
obstacle-avoidance benchmark pairs an active depth sensor with a camera classifier.

Timing forces the same split. Between the warning-field edge and the protective-field edge the robot
has **167-323 ms** to classify a moving target (computed). No thermal frame at 4 Hz and no
micro-Doppler classifier fits in that. **Classification must never gate the stop.** Geometry stops
the robot; classification decides only what it does afterwards.

## The five survey distances

Every capability table here is evaluated at 1, 3, 5, 8 and 10 ft. Each earns its place.

| Distance | mm | What it is for |
|---|---|---|
| 1 ft | 305 | Inside the stop. Already too late. |
| 3 ft | 914 | Decision distance: stop, slow or steer. |
| 5 ft | 1524 | Planning distance: re-route without stopping. |
| 8 ft | 2438 | Past most ToF: 5 of 9 multizone parts still register a cat. |
| 10 ft | 3048 | Room-scale awareness, not avoidance. |

**1 ft is inside the stopping distance.** The computed protective field for a VL53L5CX at 15 Hz and
0.5 m/s is **386 mm** with hobby-grade tolerances, **586 mm** if retroreflectors cannot be excluded,
and the sensor must see reliably to **561 mm** once the 175 mm half-footprint is added (inferred).
Anything first detected at 305 mm is a contact, not a detection.

**3 ft is the decision distance**, the first survey point outside the protective field at every speed
in the band. **5 ft is the planning distance.** The conventional warning field is twice the protective
field, which at 0.5 m/s is **772 mm** (computed); 5 ft sits well outside it, so it is where a re-route
is chosen rather than where a brake is applied.

**8 and 10 ft are where the field thins out.** At 10 ft all 14 scanning lidars and 7 of 8 24 GHz
radar modules in the catalogue still register a cat; 3 of 9 multizone ToF parts do, 1 of 9
single-point ToF parts, and one thermal array (computed from `capability.json`).

One rule applies to every field-of-view figure in this reference: **say which one you mean.** ST puts
a diagonal on the front page of every VL53 datasheet, and a diagonal is not a horizontal. Where ST
publishes the horizontal directly, use it: VL53L5CX and VL53L8CX are **45 x 45 deg** (63 and 65 deg
diagonal), VL53L7CX and VL53L7CH are **60 x 60 deg** (90 deg diagonal), VL53L9CX is **55 x 42 deg**
(71 deg diagonal). Where ST publishes only a diagonal, convert it: the VL53L1X's 27 deg is labelled
diagonal, and the horizontal is **19.27 deg**. ST's 45/45/63 triple is not self-consistent under a
pinhole model, so treat the 63 deg as a separate measurement and the 45 deg as the number that sizes
a ring.

Every one of those figures is a conditioned measurement, not a hard cone. The VL53L5CX triple is
taken at **88 % white reflectance, 1 m, dark, 8x8 resolution, 14 % sharpener, 15 Hz**; against a 17 %
grey target in 5 klux the usable angular extent is smaller. Sizing a ring from a diagonal, or from a
dark-condition figure, overstates coverage badly.

## Where the sources disagree

**Cat height.** The prose in `coverage-geometry.md` models a **200 mm** cat and a **35 mm** chair leg;
`geometry.json`, and this chapter, use **250 mm** and **30 mm**. Prefer the data file, because the
computed appendix is built from it. The smaller cat is also the conservative case, so the
vertical-coverage conclusions carry over with margin.

**Stopping distance.** `geometry.json` gives **73.8 mm** at 0.5 m/s for a VL53L5CX 8x8 at 15 Hz;
`safety-and-failure-modes.md` gives a **386 mm** protective field for the same part and speed. They
are not the same quantity: the first is the bare kinematic term, reaction plus braking; the second
adds the industrial allowances for measurement tolerance, low reflectance and ground clearance. Size
a field from the second. Note also that the `geometry.json` "firm 0.5 g" column is 4.9 m/s2, well
above the 2.86 m/s2 tip-over ceiling for a CG at 600 mm; use 2.0 m/s2.
