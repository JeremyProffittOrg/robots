# Standalone guide: Adafruit 4010, the Slamtec RPLIDAR A1

## What this part is, and what it is not

Adafruit product **4010** is the **Slamtec RPLIDAR A1**, manufacturer model **A1M8**: a 360 deg
two-dimensional spinning laser triangulation scanner
([product page](https://www.adafruit.com/product/4010), read 2026-09-12). It is
96.8 x 70.3 x 55 mm on the [Slamtec parameter page](https://www.slamtec.com/en/lidar/a1spec) and
170 g in the datasheet; Adafruit's own page lists the outline differently, as 98.5 mm wide by 60 mm
high. In the box: the scanner head, a USB-to-serial adapter board, and a cable.

**Do not confuse product 4010 with the Vishay VCNL4010**, a single-point infrared proximity and
ambient-light sensor sold by Adafruit as product **466**. A parts search for "4010" returns both. If
it is a small breakout board it is the wrong part; if it spins, it is the LiDAR.

Revision matters for the range figure. Adafruit states only that "As of June 2, 2021" Slamtec
revised the unit, labelled A1M8. No suffix is printed and neither Slamtec page mentions "R6", which
appears only on reseller pages, so **treat "R6" as inferred, not vendor-stated**. What matters is R5
or later, which the 2021 date and the 12 m figure both imply.

## Specification, with every stated condition

From the Slamtec LD108 A1M8 datasheet rev 2.1 (2018-02-05, Adafruit-hosted) and v2.2 (2019-02-14).
Every row is datasheet-verified except the accuracy row, which is vendor-page-verified.

| Item | Typical | Min / Max | Stated condition |
| --- | --- | --- | --- |
| Range, R5 and later | 0.15 - 12 m | - | Comments column reads only "White objects" |
| Range, R4 and earlier | 0.15 - 6 m | - | Comments column reads only "White objects" |
| Angular range | 0 - 360 deg | - | - |
| Scan field flatness | - | -1.5 / +1.5 deg | Plane wobble; v2.2 only |
| Distance resolution | < 0.5 mm | - | Below 1.5 m only |
| Distance resolution | < 1 % of distance | - | All distance range |
| Angular resolution | 1 deg | - | At 5.5 Hz scan rate |
| Sample frequency | 8000 Hz | 8010 Hz | R1/R2 capped at 2000 Hz; R3/R4 need firmware 1.24+ |
| Scan rate | 5.5 Hz | 1 - 10 Hz | "measured when RPLIDAR A1 takes 360 samples per scan" |
| Points per revolution | 1450 | - | Datasheet Introduction, at 5.5 Hz, needs 8 kHz sampling |
| Laser | 785 nm, 3 mW peak | 775 - 795 nm, 5 mW | Class I, 110 us pulse, 21 CFR 1040.10/.11, Notice 50 |
| Accuracy | 1 % of range | - | To 3 m; 2 % from 3 - 5 m (parameter page) |

**The field of view is 360 deg horizontal and effectively zero vertical.** There is no vertical fan
and no diagonal figure to misread; the only vertical extent is the +/-1.5 deg flatness wobble, a
defect tolerance rather than coverage.

**Reflectance is this datasheet's weak point.** Slamtec states only "White objects" against the 12 m
figure: no reflectivity percentage, no dark-target range, no ambient figure in lux. The phrase "white
objects with 70 % reflectivity" circulates in third-party copy, but full-text search of rev 2.1 and
v2.2 on 2026-09-12 returned zero hits for "70", "reflectivity" or "reflectance" in any specification
row, and the parameter page does not carry it either. **Dark-target range is not published.** Derate
substantially for a black cat, a dark jacket or a matte bumper, and verify empirically.

The datasheet claims only operation "in all kinds of indoor environment and outdoor environment
**without sunlight**". Adafruit's page lists "Distance Resolution: 0.2cm" - where page and datasheet
differ, **use the datasheet**. Class I with an invisible 785 nm beam is the right rating for a
machine scanning at cat eye height, and the datasheet says the short pulse "can make sure its safety
to human and pet." The unit shuts the laser down on excess transmit power, power-on failure,
unstable rotation or abnormal sensor behaviour, and the host can query that health state.

## Output and rate

Each sample carries `Distance` in mm from the rotating core, `Heading` in degrees, `Quality` as a
signal-strength proxy, and a `Start Flag` marking a new revolution. That is the entire output.
**There is no object, no track, no velocity, no classification and no presence flag.**

Two published sampling conditions coexist: **1 deg resolution at 360 samples per scan** in the
specification table, and, in the Introduction, "5.5 hz when sampling 1450 points each round" - about
0.25 deg, but needing 8 kHz sampling and so R5 or later. **Design to 1 deg.** The Adafruit guide also
warns that "a single revolution is not guaranteed to give a reading for each possible angle": scans
are sparse and irregular, with float angles, not a clean 360-element array.

## Power, wiring and the USB adapter

All rows datasheet-verified.

| Rail | Typical | Max | Comment |
| --- | --- | --- | --- |
| Scanner voltage | 5 V | 4.9 - 5.5 V | "may damage the core" above max |
| Scanner ripple | 20 mV | 50 mV | "High ripple may cause the core working failure" |
| Scanner start current | 500 mA | 600 mA | "Underpower may cause the startup failure" |
| Scanner run current | 300 mA | 350 mA | Work mode, 5 V input |
| Motor voltage | 5 V | 5 - 10 V | Adjust voltage according to speed |
| Motor current | 100 mA | - | 5 V input |

**Budget 400 mA at 5 V, so 2.0 W continuous, with about 700 mA and 3.5 W of inrush at start** -
twenty to forty times a single-zone ToF part, and it never stops while scanning. Waveshare's A1 page
lists "System Current: 100 mA, Power Consumption: 0.5 W", which cannot be reconciled with 300 mA
scanner plus 100 mA motor and looks like a reseller transcription error. **Design to the datasheet:
2 W.** Slamtec requires the scanner and motor to be **powered separately** "in order to ensure data
accuracy". Sharing a rail with drive motors is the commonest cause of flaky scans.

Data interface: **3.3 V TTL UART, 115200 bps, 8N1** on a PH2.54 7-pin connector, outputs 2.9 - 3.5 V
high and 0.4 V or less low, inputs accepting 1.6 - 3.5 V high. Motor enable is `MOTOCTL`, a 0 - 5 V
PWM signal; through the bundled adapter the driver asserts **DTR** to spin the motor, unlike the A2
and A3 which use PWM.

**To a Raspberry Pi:** use the bundled adapter, confirm `/dev/ttyUSB0`, and feed it from a supply
that holds up under the 600 mA start current - under-volting gives the classic fault of a motor that
spins while health never reaches `Good`. Without the adapter the Pi GPIO UART is 3.3 V and directly
compatible, but you supply both 5 V rails and drive `MOTOCTL` yourself.

**To an ESP32:** UART pins are 3.3 V, so TX, RX and ground connect straight to the header with no
level shifting; supply both 5 V rails from the robot, not the ESP32 board. Note that the Adafruit
library's docstring says "The Current Version does NOT support CircuitPython", so on a
microcontroller you port the packet parser yourself. Note also that the link is fixed at 115200 bps,
and that the 1450-point condition needs 8000 samples per second, so the driver's express mode
(`scan_type=2`) is the path to it. **Design to 1 deg and verify the denser mode on your own unit
with `iter_measurements` before relying on it.**

## Drivers, libraries and ROS

`pip install adafruit-circuitpython-rplidar` gives a thin MIT-licensed wrapper adopted from the
Skoltech `rplidar` library: `.info`, `.health` returning `('Good'|'Warning'|'Error', code)`,
`.start_motor()`, `.set_pwm()`, `.start(scan_type)`, `.iter_measurements()` yielding
`(new_scan, quality, angle, distance)`, and `.iter_scans()` yielding one list per revolution.
**Maturity: adequate, not strong** - still linked from a guide edited 2024-06-03, but the
CircuitPython port promised in 2019 has not landed.

Past a demo, use the vendor stack: the C++ [rplidar_sdk](https://github.com/Slamtec/rplidar_sdk) and
[rplidar_ros](https://github.com/Slamtec/rplidar_ros) for ROS 1, or `sllidar_ros2` for ROS 2, both
publishing `sensor_msgs/LaserScan`. **That output format is the A1's real advantage** - the hardware
is not special, but `slam_toolbox`, `nav2` costmaps and the leg-detection packages consume
`LaserScan` already. Reported field problems: the **bundled USB adapter is the most common failure
item** (motor spins, no data, adapter LED dark), missing cables, enumeration failures on SBCs
lacking the USB-UART kernel driver, and under-volting at startup.

## Price, stock and service life

Read 2026-09-12: Adafruit lists **USD $99.95**, **19 in stock**, actively stocked, not discontinued,
not end-of-life. DFRobot sells the same scanner at **$99.00**.

**This is the only sensor in this document with a wear-out mechanism, and its service life is not
published.** The rotor turns continuously whenever the unit scans. Slamtec's product page states it
uses **OPTMAG optical-magnetic coupling instead of a slip ring**, removing the sliding contact that
normally limits a spinning LiDAR's life; that is the only durability claim either document makes.
**No MTBF and no service-life hours are published for the A1M8**, and neither document gives a
replacement interval for the spinning assembly. Treat the rotor as a consumable of unknown life: log
run hours and hold a spare. Operating temperature is 0 - 45 deg C in the datasheet and 0 - 40 deg C on the
parameter page; design to 0 - 40 deg C.

## On a 350 mm robot: mounting and the planar slice

Mount the A1 on the **rotational centre axis** with a clear 360 deg optical window. This is not a
sensor you distribute; it is one sensor you centre, and any mast, handle or antenna in the plane is
a permanent dead sector to mask in software. The 150 mm blind radius is harmless - the 175 mm body
half-radius exceeds it, so the blind zone hides inside the footprint - but the corollary is
unforgiving: anything that gets under or against the chassis was never seen, so bumpers and cliff
sensors are not optional.

**Mounting height decides what the robot can see, and no height works for everything.** Target
dimensions from `geometry.json`:

| Target | Height above floor | Plane at 200 mm | Plane at 400 mm |
| --- | --- | --- | --- |
| Adult, standing | 1700 mm | Seen - two ankle clusters | Seen - two shin/knee clusters |
| Toddler | 850 mm | Seen - shins | Seen - thigh or hip |
| Large dog (labrador) | 650 mm at shoulder | Seen - body | Seen - upper body |
| Small dog (terrier) | 330 mm at shoulder | Seen - body | **Missed entirely** |
| Cat, standing | 250 mm at shoulder | Seen - top 50 mm above plane | **Missed entirely** |
| Cat, lying | 130 mm profile | **Missed** - plane passes 70 mm over | **Missed entirely** |
| Table overhang | 40 mm slab, 700 mm gap | Legs seen, slab invisible | Legs seen, slab invisible |

**A sleeping cat is invisible at any plane height you can usefully pick.** Clearing a 130 mm lying
profile needs a plane below about 130 mm, and there the -1.5 deg flatness edge strikes the floor at
130 / tan(1.5 deg) = about 5.0 m, filling the far field with floor returns. At 200 mm the floor
strike is about 7.6 m; at 400 mm about 15 m, beyond range. *Arithmetic from the published flatness
spec, not a Slamtec table.* **The table overhang is never visible**: a plane below the slab sees the
legs and reports clear air where the tabletop is, which is how a robot drives its mast into a table
edge. The plane is a wedge, not a sheet: 26 mm thick at 0.5 m, 52 mm at 1 m, 128 mm at 2.4 m.

## Scan points on target

Counts for the adult, the leg or cat and the chair leg are from the computed catalogue in
`capability.json`; the toddler column is the same angular-subtense arithmetic applied to the 250 mm
toddler width in `geometry.json`. All are at 1 deg resolution. Arc spacing per degree is 5.3 mm at 1 ft, 16.0 mm at 3 ft, 26.6 mm at
5 ft, 42.6 mm at 8 ft, 53.2 mm at 10 ft.

| Distance | Adult torso 450 mm | Leg or cat 140 mm | Toddler 250 mm | Chair leg 30 mm |
| --- | --- | --- | --- | --- |
| 1 ft (0.30 m) | 73 pts | 26 pts | 45 pts | 5.6 pts |
| 3 ft (0.91 m) | 28 pts | 9 pts | 16 pts | 1.9 pts |
| 5 ft (1.52 m) | 17 pts | 5.3 pts | 9 pts | 1.1 pts |
| 8 ft (2.44 m) | 11 pts | 3.3 pts | 6 pts | **0.7 pts, nothing** |
| 10 ft (3.05 m) | 8 pts | 2.6 pts | 5 pts | **0.6 pts, nothing** |

`geometry.json` gives a human leg and a standing cat the same 140 mm width, so **at every distance a
human leg and a cat return the same number of points.** The research lane file assumed a 120 mm shin
and reported about 23, 8, 5, 3 and 2 points - the same calculation on a narrower target. Prefer the
table above: it uses the document's shared target dimensions and angular subtense rather than a flat
arc division. Read the chair-leg column twice. **A 30 mm chair leg falls below one scan point beyond
about 6 ft and can be missed entirely between samples.**

## What 5.5 Hz means on a moving robot

One revolution takes **182 ms**. At 0.5 m/s the robot travels 91 mm while a revolution is collected,
so its first and last points came from positions 91 mm apart - compensate with odometry or accept
about 90 mm of angular smear. Targets move too: a person approaching at the ISO 13855 walking speed
of 1.6 m/s covers 291 mm per revolution, more than half a 450 mm torso width.

**Worst-case data age is a full revolution**, because any bearing is sampled once per 182 ms. The
computed stopping appendix sizes this chain at 5.5 Hz with a firm 2.0 m/s2 brake: about **107 mm of
stopping distance at 0.3 m/s, 203 mm at 0.5 m/s and 532 mm at 1.0 m/s**, against 136 mm at 0.5 m/s
for a VL53L5CX ToF chain at 15 Hz on the same robot. *Computed, not vendor-stated.* At 1.0 m/s that
is more than a robot length, so the A1 alone should not be the last line of defence at speed.

The consumer must keep up: the Adafruit guide warns that if the
callback "takes too long to process a scan, data from the RPLIDAR will eventually be dropped."
There is no flow control. **Finish the whole perimeter decision inside 180 ms.**

## From a range ring to a perimeter decision

None of this ships with the sensor.

1. **Ingest and de-skew** - consume `iter_scans()` or the ROS `LaserScan` fast enough to avoid
   drops, with odometry compensation across the revolution.
2. **Mask dead sectors** from the robot's own structure; discard returns inside the chassis radius.
3. **Filter by quality** - the main defence against specular ghosts from glass and mirrors.
4. **Cluster** with adaptive-breakpoint or DBSCAN segmentation on a distance-dependent threshold,
   because arc spacing grows with range.
5. **Extract cluster features** - width, depth, curvature, point count, mean range, linearity: what
   the classical ROS `leg_detector` random forest consumes.
6. **Track** with a constant-velocity Kalman filter, so every cluster carries a velocity.
   **Velocity is the only strong life-versus-furniture cue available.**
7. **Classify** - leg-pair geometry for humans, small low moving clusters for pets, stationary
   non-leg shapes as inanimate. Treat every unclassified cluster as potentially a person.
8. **Decide** on the minimum range in the swept corridor ahead, not the global minimum.
9. **Fuse** with bumpers, cliff sensors and a presence channel.

Steps 4 to 7 are a multi-week software project, or a decision to adopt ROS 2 and take `nav2` plus an
off-the-shelf person detector. Budget for that, not for the $99.95.

## Direct answers

**Any obstacle it could collide with? Yes - within the plane, and only within the plane.** That is
what the sensor is for, and it does it well: 360 deg, 5.5 - 10 Hz, millimetre-class range on every
surface that returns 785 nm light. What it misses is categorical, not marginal:

- Anything **below** the plane - a doorstep, a shoe, a power strip, a sleeping cat.
- Anything **above** the plane - a tabletop, a counter overhang, an open drawer, an outstretched arm.
- **Glass, mirrors, polished metal and still water.** A glass door returns almost nothing at normal
  incidence and a phantom object at the mirrored distance off-axis. The A1 has no defence against
  this, and it is the classic domestic-robot failure.
- **Matte black and dark fabric at range**, where no derated range is published and dropouts, not
  wrong ranges, are the expected symptom.
- **Thin objects** - chair legs at range, cable runs, pedestal spokes - which fall between 1 deg
  samples from about 3 m out.
- **Descending edges.** A horizontal plane cannot see a hole.

One more coverage risk, **inferred from the multi-LiDAR crosstalk literature and the absence of any
published mitigation, not vendor-stated**: Slamtec publishes no crosstalk specification and no
multi-unit coordination mechanism for the A1, so two of these robots in one room should be expected
to produce spurious returns.

**It classifies nothing on its own.** Any statement about what an object *is* is your software, and
the 2D-LiDAR person-detection literature is unanimous that "the lack of identifying information in
2D range data" is the core drawback. `DR-SPAAM`, `PeTra` and the FROG dataset beat the geometric
baseline, but all infer over time with known false-positive rates. A chair leg and a cat leg at 3 m
are the same two points.

| Distance | Moving human | Moving cat | Static human | Static pet |
| --- | --- | --- | --- | --- |
| 1 ft | Yes, 73 pts, high confidence | Yes, 26 pts, plane at 200 mm | Object only | Object only |
| 3 ft | Yes, 28 pts, good leg-pair | Yes, 9 pts | Object only | Object only |
| 5 ft | Yes, 17 pts | Yes, 5.3 pts, shape marginal | Object only | Object only |
| 8 ft | Yes, 11 pts, pair separation poor | Yes, 3.3 pts, chair-leg confusable | Object only | Object only |
| 10 ft | Yes, 8 pts | Yes, 2.6 pts, dark fur may drop out | Object only | Object only |

**A human?** Yes, as a human-sized object, at all five distances, provided the plane crosses the
body. As a *human* specifically, only by inference from leg-pair geometry and motion over time, and
only reliably to roughly 4 - 5 m indoors. *Inferred from the sampling geometry and the
people-tracking literature, not a vendor figure.*

**A pet?** Only with the plane low enough to cross a standing animal, so at or below 200 mm for a
cat. A lying cat is missed at every usable height, and a black cat is the worst optical case for a
785 nm triangulation LiDAR with no derated range published.

**A static human? No, not as a human, ever.** The A1 measures geometry, not life: no micro-motion
channel, no respiration signal, no thermal signature. A person standing still at 3 m is a pair of
unmoving clusters, which is also the description of a table leg. **The A1 cannot meet a
"motionless person in the room" requirement and no software will make it.**

## Verdict

**Buy it, and buy it as the obstacle layer, not the presence layer.** On a 350 mm robot, an A1 at
the rotational centre at knee height, **350 - 450 mm above the floor**, is the correct primary
obstacle sensor: it captures the human leg-pair signature the tracking literature is built around,
crosses a standing labrador, and sits below most tabletops so it sees table legs. It explicitly
sacrifices the standing cat, the small dog, the sleeping cat and every overhang. If pets matter more
than reach, drop the plane to 200 mm and accept floor strike at about 7.6 m. The pairing that fixes
the weaknesses is three layers:

1. **RPLIDAR A1**, $99.95 - 360 deg obstacle geometry, mapping, navigation, moving-target tracking.
2. **A presence channel** - a 60 GHz mmWave presence radar or a thermal IR array - for the static
   human and the sleeping pet, which one horizontal plane structurally cannot do.
3. **Contact and cliff** - bumpers for the sub-plane blind zone, downward ToF or IR for descending
   edges, which a horizontal plane cannot see because it cannot see a hole.

If only one sensor fits and the requirement is "do not collide with anything," the A1 is the right
choice and nothing in this price class is close. If the requirement is "know whether a person or a
cat is in the room," the A1 is the wrong anchor, and a presence radar or thermal array should be.
