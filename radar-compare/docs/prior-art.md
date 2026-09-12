# What shipping robots actually use

Every shipping robot here splits perimeter sensing across separate sensors: non-semantic ranging to
avoid collisions, a camera classifier to name floor objects, and - only on the expensive machines -
a second camera at human height for identity. None does all three with one sensor. The two that
tried, the Roomba j-series and Ohmni, carry the documented failure modes. Sources were re-verified
against primary pages on 2026-09-12.

## The shipping platforms at a glance

| Platform | Perimeter stack (count) | Price, 2026-09-12 | Source |
| --- | --- | --- | --- |
| iRobot Create 3 | 7 IR proximity pairs, 4 cliff IR, IMU, optical odometry | ~$299 | vendor page; price unverified |
| TurtleBot 4 Standard | Create 3 set + RPLIDAR A1M8 + OAK-D-Pro | ~$2,000-2,400 | datasheet; price unverified |
| Roomba j7 / j9 | Bumper RGB camera + 2 IR windows + bumper + cliff IR | discontinued | layout inferred from photos |
| Roomba s9 | Top vSLAM camera + 3D edge sensor, no classifier | discontinued | unverified, pages dead |
| Roomba Max 715 / 875 | ClearView Pro LiDAR + PrecisionVision camera | $599.99 / $1,199.99 | vendor page |
| Roborock Saros 10R | Solid-state LiDAR + 3D ToF + RGB + structured light | $1,299.99 | vendor page |
| Ecovacs T90 Pro Omni | RGB camera + 3D structured light + dToF | $598.99-799.99 | vendor page |
| Amazon Astro | Bezel cam, periscope cam, IR + ToF suite, custom cliff | $1,599, invite-only | vendor page + teardown |
| Double 3 | 2 x RealSense D430 + 5 ultrasonic + IMU | $3,999 launch | datasheet |
| temi V3 | 360 deg LiDAR, 3 depth/ToF cams, 6 linear ToF, cliff array | EUR 9,810 incl. VAT | vendor page |
| Starship | 12 cameras incl. ToF and stereo, radar, ultrasonics | not sold to public | vendor page |
| Kiwibot 4 | 3 front cameras, 1 rear 180 deg camera, spotlights | not sold to public | unverified |
| Navimow X3 | 3 cameras / 300 deg, ToF 0.09-2.0 m (condition not published), solid-state LiDAR | ~$2,499-2,999 | vendor page |
| Pudu BellaBot | 3 RGBD cameras + LiDAR, 0.5 s stop response | ~$15,000-20,000 class | vendor page |
| Person Sensor | ESP32-S3 + 0.3 MP camera, 110 deg FOV | $9.95, discontinued | datasheet |

## iRobot: three generations, three answers

The Create 3 is the best-documented cheap perimeter system in consumer robotics. **Seven pairs of IR
proximity sensors** sit on a multizone bumper on a 339 mm chassis, spanning **+/-75 deg at 25 deg
spacing**, with four cliff sensors underneath (vendor-page-verified). Ring height is set in the
simulation URDF as `ir_intensity_z_pos = "-0.7*cm2m"`, that is **7 mm below `base_link`**
(datasheet-verified). iRobot publishes no wavelength, no coupling method and no range; the widely
repeated "940 nm, AC coupled, range depends on surface quality of the target" line is in no iRobot
source and is **unverified**.

The failure modes are severe. Anything below bumper height - cables, socks, small toys - is found by
collision, not detection. Dark IR-absorbing surfaces return nothing: a miss on the obstacle ring, a
**false cliff** on the downward sensors, which is why vacuums of every brand refuse black rugs
(inferred from reflective-IR physics, not vendor-stated). And a proximity sensor returns no class at
all - table leg, ankle and cat read the same.

The j7 and j9 added PrecisionVision, a visible-light RGB camera on the bumper at about 60 mm (height
inferred from the vacuum class, not vendor-published), recognising cords, socks, shoes and solid pet
waste. iRobot backed that last class with the **P.O.O.P. promise**, a free replacement robot if a
covered Roomba fails to avoid solid pet waste
within one year - the only warranty in consumer robotics paying out on a perception failure. The
dominant reported failure is light: reviewers say the camera cannot identify floor objects in a dark
room, and whether the j9 has an illumination LED is **not published by iRobot**. Reports of dog toys
missed and avoidance regressing after firmware updates are **unverified**.

The s9 is the counter-example: a 3D ranging sensor for edge work and **no object classifier**. Its
headline figures are unrecoverable and its pages return HTTP 404, so both are **unverified**. The
current Max line reverses the camera-only bet and pairs LiDAR with the camera - the company that
argued hardest for one camera now ships ranging and classification on separate parts.

## Roborock and Ecovacs: the pet-waste benchmark

Avoiding dog waste on a dark floor is the same perception problem as avoiding a sleeping cat, which
makes this the most relevant prior art for pets. Roborock's StarSight 2.0 is a dual-transmitter
solid-state LiDAR plus a **QVGA 3D ToF giving 21,600 points**, plus RGB, plus **vertical structured
light** added to catch tall and narrow obstacles a floor-plane sensor misses - all in a 79.8 mm-tall
robot. It sees objects "down to as small as 2cm wide and 2cm tall", conditioned only on "internal
testing carried out by the manufacturer", which is a disclaimer, not a measurement condition.
**Roborock publishes no detection range at all**; any "1-5 m" figure in circulation has no primary
source. Class counts disagree: 301 on the StarSight page, 108 for the Saros 10R per Vacuum Wars.

Ecovacs pairs RGB with 3D structured light, names the method - "a mix of RGB cameras and infrared
sensors" trained on "thousands of image datasets" - and states the ceiling: **"there is no 100%
guarantee they will avoid pet waste in all situations"**. In the only consistent public
obstacle-avoidance benchmark, **every top scorer pairs an active depth sensor with a camera
classifier**; no camera-only or depth-only robot is in the top group. Quote it carefully: it is a
24-**point** score over five scenarios, not 24 objects, and **no fleet average on that scale is
published**.

## Delivery, telepresence and the research bases

Starship's 697 x 569 mm sidewalk robot carries **12 cameras including ToF and stereo, plus radar,
plus ultrasonics**, and grades behaviour: an adjacent object slows it, an object in front stops it.
A classifying 360 deg perimeter fit for public sidewalks needed twelve sensors and three modalities.
Kiwibot 4 runs three front cameras and one rear 180 deg camera and historically leaned on **remote
human supervisors**. A thin stack is viable only when a teleoperator is the fallback classifier.
Indoors, Pudu's BellaBot carries **three RGBD cameras plus LiDAR** and a stop response "as short as
0.5 seconds". Three depth cameras exist for one stated reason: to catch **low-lying and overhanging
obstacles**, the two cases a single floor-plane scan misses. A tall robot on a narrow base has to
answer that case deliberately.

temi V3 matches the target form factor exactly at **350 x 450 mm and 1000 mm tall**: a 360 deg LiDAR
at the base front, two depth cameras, one ToF depth camera (5 m, 90 deg field of view, target
reflectivity and ambient light not published), six linear ToF sensors, a 13 MP RGB camera on the
motorised head at the top of the 1000 mm column, and a downward cliff array - for **EUR 9,810**.
Double 3 backfills two active-IR stereo modules (0.2-10 m, **no reflectivity or ambient-light
condition published**) with **five ultrasonic rangefinders**, because active IR stereo fails on
glass, mirrors and dark matte surfaces; it classifies nothing and leaves judgment to the pilot.
Ohmni is the other end: **$1,995** and **no depth sensor at all**.

Astro does all four jobs with four mechanisms - Visual ID face recognition at screen height, one
combined cat-and-dog model with no per-animal identity, an IR and ToF suite for geometry, and
**custom** cliff sensors, which implies stock reflective parts were not good enough for a 9 kg robot.
Its periscope camera reaches **1067 mm** at 132 deg **diagonal** field of view. **No teardown source
identifies mmWave radar in Astro.**

TurtleBot 4 adds to the Create 3 set an RPLIDAR A1M8 (0.15-12 m, 360 deg, 5.5 Hz, **no reflectivity
or ambient-light condition published**) at tower height plus an OAK-D-Pro with IR dot projector and
flood LED. Classification there is purely a software problem.

## Person detectors and mowers

The Useful Sensors Person Sensor was the reference drop-in: **$9.95**, 7 Hz detection, up to four
faces per frame over I2C, no raw image access. Its **range is never published** - the docs offer
bounding-box size as a distance proxy. It is **discontinued**; the vendor left hardware entirely.

Mowers hold the only peer-reviewed pet-safety data. An Oxford study tested **19 models** against
hedgehog cadavers: collision sensors on 8, wheel-current detection on 11, ultrasonic on 5,
headlights on 4, **camera vision on zero**. The result: "Apart from one single incidence, all robotic
lawn mowers had to physically touch the hedgehog carcasses to detect them", and that one non-contact
detection could not be reproduced. Husqvarna's radar-equipped 435X AWD costs **$2,999.99**; its
support page says near-ground objects may be missed, vegetation reads as objects, avoidance is
**disabled within 1.2 m of the boundary**, and then: **"It is not a safety feature. There is no
guarantee that objects will not be run over."** Navimow X3 is the state of the art, with 24+ animal
classes including hedgehogs and people detected to 3 m - and it publishes the honest cost of a
camera-primary stack: **300 deg and 3 m by day collapse to 150 deg and 1.8 m at night**.

## Transferable lessons, stated as rules

1. Split ranging from classification. Every successful platform uses different sensors for "do not
   collide", "is that a person" and "is that a pet".
2. Cover the forward arc at roughly 25 deg spacing, or buy one sensor that covers the arc. Seven IR
   pairs across +/-75 deg on a 339 mm bumper is the mass-produced reference layout.
3. Expect no non-contact pet detection without an active depth channel. Nineteen mowers with
   bumpers, wheel-current sensing and ultrasonics achieved effectively zero.
4. Budget a 2-4x haircut from datasheet range to useful range. Vector's SDK documents 1200 mm
   datasheet against about 300 mm useful on the robot.
5. Check that the robot's own mechanism does not occlude its sensors. Vector's lift arm blocks its
   ToF sensor, which then reports "clear" - readings the SDK itself calls not useful for object
   detection. This failure is free to avoid at design time.
6. Treat a dark target as "no return", and decide deliberately which way the robot fails on it.
7. Assume a camera-primary stack loses about half its range and half its field of view in the dark,
   or add an illuminator, or move ranging onto a sensor that ignores ambient light.
8. Add a non-optical near-field channel for glass, mirrors and dark matte surfaces.
9. Put identity at face height and protection at leg height, and copy the shipping height bands:
   cliff sensors 30-90 mm up and pointed down at the leading edge, near-field ranging at bumper
   height 40-90 mm, floor-object classification low and forward, identity at 900-1400 mm. A face
   detector is not a person detector.
10. Cover the low and the overhanging case explicitly. BellaBot ships three RGBD cameras because one
    floor-plane scan sees neither.
11. Do not build a perimeter on a single-source novelty module.
12. Treat speed as a perception budget. Less speed buys less range, and range is the expensive axis.
13. State the limits the way the vendors do, and put a mechanical layer - low mass, speed limit,
    compliant bumper, stop-on-contact - under the classifier.

What none of them attempts: **mmWave radar as an indoor perimeter sensor** (in no shipping consumer
floor robot; only Husqvarna ships radar, band not published), **individual pet identity** (Astro
identifies people, not animals), **certified human detection at hobby cost** (the cheapest
safety-rated scanner found is $3,111 for 275 deg), and **a detection range published with its
measurement condition** - not one consumer vendor here does that.
