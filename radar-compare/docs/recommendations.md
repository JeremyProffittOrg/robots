# Recommendation: three builds, one per budget

Each tier below is one recommendation, not a menu. Prices are USD as read on 2026-09-12 and
exclude tax and shipping. Nothing here has been purchased or physically tested; every figure is
from a datasheet or a vendor page, and the ones that are not are marked as estimates.

## Tier 1 - `collision-ring`: do not hit anything

USD 455, 724 mA average at 5 V. This tier answers requirement (a) and nothing else. It has no
human channel and no pet channel and it is not honest to claim otherwise.

| Qty | Part | Vendor / SKU | Unit | Extended |
|---|---|---|---|---|
| 12 | VL53L8CX 8x8 multizone dToF carrier | Pololu 3419 | 24.95 | 299.40 |
| 6 | VL53L4CD 1-1300 mm dToF carrier (cliff) | Pololu 3692 | 13.95 | 83.70 |
| 2 | PCA9548 8-channel I2C mux, STEMMA QT | Adafruit 5626 | 6.95 | 13.90 |
| 12 | Flexible Qwiic cable, 500 mm | SparkFun PRT-17257 | 2.75 | 33.00 |
| 6 | STEMMA QT cable, 100 mm | Adafruit 4210 | 0.95 | 5.70 |
| 1 | RP2040 concentrator, Pico class | estimate | 4.00 | 4.00 |
| 1 | Compliant bumper, 20-50 mm closed-cell foam plus 4 microswitches | estimate | 15.00 | 15.00 |
| | **Total** | | | **about 455** |

**Mounting.** The twelve ring sensors go at **200 mm** height, boresight **horizontal with no
cant**, at **30 deg azimuth spacing**. The six cliff sensors go at **150 mm** with a **23 deg
down-cant**, four across the front arc at plus and minus 20 and 60 deg, and two at the rear at
150 and 210 deg.

**Why twelve and not eight.** The VL53L8CX is 45 deg horizontal. Eight of them total exactly
360 deg, which is the one count that must be avoided: at exactly 360 the edge rays of adjacent
sensors are parallel and the wedge between them never closes at any range. Twelve gives 180 deg
of designed overlap and closes the wedges 513 mm from the platform centre, 338 mm past the skin.
The compliant bumper covers what is left, which is why the bumper is in the bill of materials
rather than in a list of nice-to-haves.

**Why 200 mm and level.** Low enough that a 250 mm standing cat is inside the vertical beam from
the skin outward; high enough that the floor does not enter the frame until 483 mm, so the ring
is not reporting carpet in every zone.

## Tier 2 - `collision-ring + animate-layer`: the recommendation

USD 909, 999 mA average at 5 V. This is the build to make. It adds requirements (b) and (c), and
it closes the two failure modes that would otherwise put the robot on the floor or on the cat:
dark targets in a lit room, and glass.

| Qty | Part | Vendor / SKU | Unit | Extended |
|---|---|---|---|---|
| - | Everything in Tier 1 | | | 455.00 |
| 1 | Slamtec RPLIDAR C1 360 deg dToF scanner | DFRobot | 69.00 | 69.00 |
| 8 | Panasonic AMG8833 8x8 thermal array, STEMMA QT | Adafruit 3538 | 44.95 | 359.60 |
| 2 | RCWL-1601 ultrasonic ranger | Adafruit 4007 | 3.95 | 7.90 |
| 1 | PCA9548 8-channel I2C mux, third | Adafruit 5626 | 6.95 | 6.95 |
| 8 | STEMMA QT cable, 300 mm | Adafruit 4210 | 1.25 | 10.00 |
| | **Total** | | | **about 909** |

### Why the scanner, at 100 mm, and why the C1 rather than the A1

The RPLIDAR C1 is the highest value per dollar in the whole study, because one USD 69 part covers
both structural weaknesses of a ToF ring:

- **Dark targets.** The C1 is specified 0.05 to 12 m at 70 percent reflectivity and 0.05 to 6 m
  at 10 percent. A black cat on a dark carpet is a 10 percent class target: the ToF ring loses it
  past about 1.55 m in a lit room and the C1 holds it to 6 m.
- **Ambient light.** The C1 is rated to 40,000 lux. The VL53L8CX is characterised at 0 and 5 kLux
  only, and a sunlit patch of floor at roughly 100 kLux reads as *empty space* - a wall of zones
  reporting "signal rate too low", not noisy numbers. Empty space is the dangerous failure.
- **A lying cat.** A scan plane at 100 mm intersects a cat lying on its side at 120 mm. No fixed
  ring at 200 mm does.
- **A static background map.** 500 points per revolution is enough to scan-match. Once the robot
  has a map, anything that does not fit it is dynamic, and dynamic is the strongest animate cue
  available without a camera. A ToF ring has far too few points to ever do this.

The runner-up, **rejected**, is the RPLIDAR A1 - Adafruit 4010, the part this document also
covers as a standalone guide. It is triangulation rather than direct time of flight; its own
datasheet qualifies the range as "White objects" with no low-reflectance figure published and
says "without direct sunlight exposure"; it is 170 g against 110 g, 5.5 Hz against 10 Hz, and
0.15 m minimum range against 0.05 m. On a 350 mm chassis the A1's blind radius nearly reaches the
skin. It costs USD 31 more to be worse on every axis that matters here. Buy the A1 if you already
own it or you want the better-documented ROS path; buy the C1 for this robot.

### Why eight thermal arrays, at 250 mm, level

Thermal is the **only** modality that separates animate from inanimate, and the only one that
sees a *motionless* target. A sleeping cat is invisible to motion-gated radar and invisible to
PIR, and plainly visible to thermal.

At 250 mm with a 60 x 60 deg array, the floor first enters frame at 433 mm, the top of a 200 mm
cat enters the beam 87 mm from the skin so the animal is in frame essentially always, and a
standing adult's head stays in frame to 2.51 m with the torso held beyond that. Ring closure
needs `floor(360/60) + 1 = 7`; eight gives 15 deg of overlap, closes at 670 mm, and leaves a
largest hideable sphere of 117.5 mm, smaller than a cat in any dimension.

**Rejected: the STHS34PF80** (Adafruit 6426, USD 14.95). A genuinely good part - 10 uA, no Fresnel
lens, holds a static human - but it has exactly one sensing element. It reports that something
warm is somewhere in an 80 deg cone: no bearing, no size, no contribution to human versus pet.
Keep it as a parked-robot wake-up layer only.

**Rejected: PIR of every kind, including pet-immune PIR.** Pet immunity is a geometric trick -
the lens's lowest beam is cut away and the unit is mounted at 2.2 to 2.75 m. At 1.0 m on a robot
that elevation separation collapses, and the human's torso and head are now above a
downward-fanning lens, so a pet-immune PIR on a low robot can see the pet and miss the person,
the exact inversion of its purpose. Worse, PIR responds to the rate of change of flux, so on a
driving robot every scene moves and the output is a random number generator.

**Two ultrasonic sensors forward, USD 7.90.** Glass and mirrors are the one target class the
entire optical stack fails on: a ToF sensor ranges to the pane, a lidar returns a dropout or a
phantom room, a thermal array sees room-temperature glass. Ultrasonic sees glass reliably.
Constrain it hard - warning field only, never in the protective-stop path, and never as the human
detector, because soft targets absorb 40 kHz.

### The fusion logic

Two rings, both body-fixed, extrinsically calibrated once so a bearing in one is a bearing in the
other. The thresholds are a starting point to be calibrated in place.

```
# Tier 0: collision. Geometry alone, at ring frame rate. No classifier in this path.
if min_range_in_swept_corridor < protective_field(v):   STOP
elif min_range_in_swept_corridor < warning_field(v):    SLOW to 0.3 m/s and announce

# Tier 1..4: classification. Runs in parallel. Changes behaviour only AFTER the stop.
match clusters across modalities by bearing (+/-10 deg) and range (+/-150 mm):

if dT < 1.5 K and jitter < 8 mm and planar and world_velocity ~ 0:
    OBJECT              # box, wall, furniture, door frame

elif dT >= 2.0 K and (h_top > 900 mm or cluster touches the top zone row) and width > 250 mm:
    HUMAN               # tall AND warm - the high-confidence rule

elif dT >= 1.5 K and h_top < 450 mm and width < 600 mm and (jitter > 8 mm or moving):
    PET                 # low AND warm AND non-rigid. Cat versus dog is NOT attempted.

elif dT >= 1.5 K:
    UNKNOWN_LIVING      # crouching adult, toddler, large dog -> BEHAVE AS HUMAN

else:
    UNKNOWN_OBSTACLE    # stop anyway
```

Three rules are embedded in that, and each one is worth more than the code around it:

- **Height is the primary human-versus-pet discriminator, not temperature and not breathing
  rate.** A resting beagle breathes at 13 to 25 per minute and a resting human at 12 to 20. The
  distributions overlap almost completely, so a rule of the form `if rate > 20 then pet` will
  call a calm human a dog. Temperature says *alive*; height says *which*.
- **Never threshold on absolute temperature.** A long-coated dog's flank reads 28.1 degC in a
  21 degC room, a 6 K contrast that falls to 2 K in a warm room, while an AMG8833's absolute
  accuracy is plus or minus 2.5 degC. Apparent temperature is mostly a range measurement in
  disguise: a cat at 3 m reads 2.5 K and a clothed human at 5 m reads 3.8 K, and moving either by
  a metre flips the ordering. Use a per-pixel background moving average at about 30 s, which
  cancels warm-up drift, chassis self-heating and room ambient in one step.
- **The ambiguous class defaults to human.** A crouching adult, a toddler and a Great Dane all
  land in `UNKNOWN_LIVING`. Over-classifying as human is the safe failure.

## Tier 3 - `full-classification-stack`

USD 1,440, 3.8 A average at 5 V. Buy this only if labelled classification out to 10 ft is a
requirement rather than a wish. The jump from Tier 2 is USD 531 and 2.8 A for one capability.

| Qty | Part | Vendor / SKU | Unit | Extended |
|---|---|---|---|---|
| 16 | VL53L8CX carrier, 22.5 deg spacing | Pololu 3419 | 24.95 | 399.20 |
| 6 | VL53L4CD carrier (cliff) | Pololu 3692 | 13.95 | 83.70 |
| 1 | VL53L8CH CNH histogram head, 900 mm, own bus | price not published | ~35 | ~35 |
| 6 | MLX90640-ESF-BAA 32x24 thermal, 110 x 75 deg | Adafruit 4469, **out of stock 2026-09-12** | 74.95 | 449.70 |
| 1 | Slamtec RPLIDAR C1 | DFRobot | 69.00 | 69.00 |
| 2 | RCWL-1601 ultrasonic | Adafruit 4007 | 3.95 | 7.90 |
| 4 | PCA9548 8-channel mux | Adafruit 5626 | 6.95 | 27.80 |
| 1 | Raspberry Pi 5 | - | 80.00 | 80.00 |
| 1 | Hailo-8L AI kit | - | 70.00 | 70.00 |
| 4 | Wide-FoV camera, about 120 deg H, at 900-1000 mm | not priced in any source | ~35 | ~140 |
| - | Concentrator, cabling, bumper | estimate | ~79 | ~79 |
| | **Total** | | | **about 1,440** |

**Sixteen ToF instead of twelve** puts the wedge tip at 343 mm from the centre - 168 mm past the
skin, inside the robot's own footprint - and drops the largest sphere that can hide in a seam from
79.4 mm to 56.0 mm. This is the tightest closure worth buying, and it is what lets the compliant
bumper stop being part of the safety argument.

## What no tier can do, at any range

- **Direct sunlight above about 5 kLux on any optical sensor.** ST publishes 0 and 5 kLux only;
  the RPLIDAR C1 stops at 40 kLux; direct sun is 100 to 120 kLux. No number exists past that. Do
  not extrapolate one.
- **Mirrors.** A mirror at 45 deg returns a folded path length and the robot believes the
  corridor continues. Map known mirrors as permanent keep-out zones.
- **Cat versus dog without a camera.** No combination of ToF, 32x24 thermal and one hobby radar
  does it.
- **Radar vital signs on a moving robot.** Ego-motion writes a Doppler bias across the scene
  orders of magnitude larger than a 5 mm chest excursion.
- **Any safety rating.** None of this is IEC 61496 electro-sensitive protective equipment. A
  certified Type 3 scanner must prove detection at 1.8 percent minimum target reflectance in its
  protective field; that is the pass mark a VL53L8CX does not meet, and the reason a certified
  scanner sees a black sock and this stack does not. Use the industrial arithmetic and the Z-factor
  discipline anyway. Do not claim the rating.

## Three decisions that override the parts list, and cost nothing

1. **Make the platform round.** A 350 mm square has a 494.975 mm diagonal and a 72.487 mm corner
   protrusion. Four 45 deg sensors on the face centres leave the corners permanently uncovered,
   and moving them to the corners is strictly worse. If it must be square, put the sensors on the
   face centres, chamfer the corners at 45 deg, and treat the corners as mechanically protected.
2. **Cap speed at 0.5 m/s, and 0.3 m/s in unmapped or occupied space.** A 15 kg robot at 1.0 m/s
   with a rigid shell delivers a mean 1500 N into a shin against a 130 N ISO/TS 15066 transient
   limit. The same robot at 0.5 m/s with a 50 mm compliant bumper delivers 38 N. Speed is the
   cheapest safety component in the build.
3. **Never let classification gate the stop.** Braking runs on raw geometry at frame rate.
   Classification runs in parallel and only changes what happens after the robot has stopped.
