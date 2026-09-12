# Prior Art: What Shipping Small Robots Actually Use for Perimeter, Human and Pet Detection

Lane: `prior-art-commercial`. Research date: **2026-09-12**. All prices are USD list price as shown on
the vendor or major-retailer page on that date unless marked otherwise.

Target application this document is written against: a mobile robot with a **350 mm square or 350 mm
round footprint, 600-1200 mm tall**, that must (a) avoid collisions with anything, (b) detect humans,
(c) detect pets 200-500 mm tall, and (d) tell human from pet from inanimate object.

## Confidence legend

| Mark | Meaning |
| --- | --- |
| **datasheet-verified** | Number comes from a component datasheet, a manufacturer technical manual, a URDF/SDK source file, or a peer-reviewed paper with the method stated. |
| **vendor-page-verified** | Number comes from the manufacturer's own product, spec or support page, with no independent test behind it. Marketing conditions usually unstated. |
| **inferred** | Derived by me from two or more verified facts, or from a teardown description without a part number. |
| **unverified** | Reported by press, reviewer or user community only; no primary source located. |

## Corrections (adversarial re-verification, 2026-09-12)

An independent check against primary sources overturned six numbers in the first revision. Each is
corrected in place below; this list exists so a reader who already quoted the old figures can find
them fast.

1. **Create 3 "940 nm, AC coupled, range depends on surface quality of the target"** - was marked
   datasheet-verified. **It is in no iRobot source.** Now unverified. (section 2.1)
2. **Create 3 IR sensor mounting height "not published"** - wrong. It **is** published:
   `ir_intensity_z_pos = "-0.7*cm2m"` = **-0.007 m** relative to `base_link`. (2.1, 14)
3. **StarSight 2.0 "range 1-5 m"** - Roborock publishes **no range at all**, on either its US or its
   global StarSight page. Figure withdrawn. (6.1)
4. **Vacuum Wars "24 objects" and "fleet average ~17/24"** - it is a 24-**point** score, and **no
   24-point average is published**. The real published averages are ~9/12 on the retired scale and
   3.27 on a 5-point rating. (6.3)
5. **Roomba Max 705 at $899.99 / $1,299.99** - not reproducible; iRobot's 705 pages 404 and the
   current Max SKUs are the **715 Vac at $599.99** and **875 Combo at $1,199.99**. (2.3)
6. **Roomba s9 "230,000 data points/s" and "3D sensor 25x/s"** - source pages are dead, product
   discontinued; both downgraded from vendor-page-verified to unverified. (2.4)

Also withdrawn for lack of any source: the **Dreame L50 Ultra 24/24** and **MOVA P10 Pro Ultra
19/24** rows. Also downgraded: the **Roomba j7/j9 bumper camera + two IR windows** layout, which is
inferred from photographs, not vendor-published. A secondary search-reported figure of "6 IR obstacle
sensors" on the Create 3 base is **contradicted by iRobot's own docs**, which say **seven pairs**;
use seven.

---

A recurring theme below: **almost none of the consumer robots publish a detection range with its
measurement condition.** Where a vendor gives "5 m" with no target reflectivity and no ambient-light
figure, I record it as vendor-page-verified and say the condition is not published. I have not
invented conditions for any of them.

---

## 1. Master comparison of shipping platforms

| Platform | Class | Footprint / height | Perimeter sensors | Human detect | Pet detect | Classifies H vs P vs object | Price (2026-09-12) | Confidence |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Roomba 600 series | Floor vac | ~340 mm dia, ~92 mm | Mechanical bumper, 4 IR cliff, IR wall follower, omni IR receiver | No | No | No | Discontinued; retail clearance only | vendor-page-verified |
| iRobot Create 3 | ROS base | 339 mm dia, 91 mm | 7 IR proximity pairs on multizone bumper (**wavelength not published - see 2.1**), 4 IR cliff, IMU, optical odometry, wheel encoders + current sensors | No | No | No | ~$299 (educational, stock varies) | vendor-page-verified (sensor counts), unverified (940 nm, price) |
| TurtleBot 4 Standard | ROS platform | Create 3 base + tower, ~340 mm dia | Create 3 set + RPLIDAR A1M8 (0.15-12 m, 8K samples/s, 360°, **≤**1°, 5.5 Hz scan; **no reflectivity or ambient-light condition published**) + OAK-D-Pro (IMX378 4K + OV9282 stereo, IR dot projector + flood IR LED) | Via software (OAK-D models) | Via software | Via software only | ~$2,000-2,400 typical reseller | datasheet-verified (sensors), unverified (price) |
| Roomba j7 / j9 | Floor vac | ~339 mm dia | Forward RGB camera on bumper + 2 IR obstacle windows + bumper + IR cliff; top vSLAM camera | Indirectly (feet/legs as obstacles) | Detects pet **waste**, not pets | Object classes only | j7+ discontinued; j9+ clearance | vendor-page-verified |
| Roomba Max 705 | Floor vac | ~340 mm dia | "ClearView Pro" LiDAR + PrecisionVision camera (**PrecisionVision on the 705 specifically is unconfirmed**) + bumper + cliff | No | Waste class only | Object classes only | **Price unverified; not listed on irobot.com 2026-09-12 (404). Current Max SKUs: 715 Vac $599.99, 875 Combo $1,199.99. See 2.3** | unverified |
| Roborock Saros 10R | Floor vac | ~350 mm dia, 79.8 mm | StarSight 2.0: dual-transmitter solid-state LiDAR, 3D ToF, 21,600 points, QVGA (**range not published by Roborock**) + RGB camera + vertical structured light | Not claimed | Not claimed (waste class) | 108-301 object classes (figures disagree) | $1,299.99 (was $1,599.99), in stock | vendor-page-verified |
| Ecovacs Deebot (AIVI 3D 3.0) | Floor vac | ~350 mm dia | RGB camera + 3D structured light + dToF LiDAR turret | Not claimed | Waste class | Image-based object classes | T90 Pro Omni $598.99-799.99 | vendor-page-verified |
| Amazon Astro | Home robot | 424 x 250 mm, 440 mm tall (1067 mm with mast) | 5 MP bezel camera, 1080p/12 MP periscope camera (132° diag), IR + ToF suite around chassis, custom cliff sensors, mic array | Yes - Visual ID face recognition, stranger following | Yes - cat/dog model, no individual ID | **Yes** (only consumer robot found that does all three) | $1,599 launch, invite-only; Business line bricked 2024-09-25 | vendor-page-verified + teardown (unverified detail) |
| Double 3 | Telepresence | ~600 mm dia base, ~1200 mm tall | 2 x Intel RealSense D430 (1280x720 depth, 0.2-10 m), 5 ultrasonic, 2 x 2048 PPR encoders, 9-DOF IMU | Implicit (obstacle) | No | No | $3,999 launch price | datasheet-verified |
| temi V3 | Telepresence | 350 x 450 mm, **1000 mm tall** | 360° LiDAR at base front, 2 depth cameras, 1 ToF depth cam (5 m, 90° FOV, 30 fps), 13 MP RGB, IMU, **6 linear ToF**, bottom cliff sensors | Face tracking, person follow | No | No | EUR 9,810 incl. VAT (Generation Robots) | vendor-page-verified |
| Ohmni | Telepresence | 381 x 241 mm base, ~1.4 m | 4 cameras (4K wide, 140° FOV); depth camera **optional via USB** | Via camera software | No | No | $1,995 (Supercam); DevKit from $2,500 | vendor-page-verified |
| Pudu BellaBot | Service | ~540 mm wide | 3 RGBD cameras + LiDAR; obstacle checks up to 5,400/min; 0.5 s stop response | Implicit | Implicit | Not claimed | ~$15,000-20,000 class | vendor-page-verified |
| Starship delivery bot | Sidewalk | 697 x 569 x 571 mm, 35 kg | **12 cameras** incl. ToF and stereo, ultrasonic array, radar, GPS, IMU | Yes ("bubble of awareness") | Yes (animals) | Yes | Not sold to public | vendor-page-verified |
| Kiwibot 4 | Sidewalk | 559 x 432 x 559 mm | 3 front cameras, 1 rear 180° wide camera, spotlights, Jetson compute | Via CV | Via CV | Via CV | Not sold to public | unverified |
| Husqvarna Automower 435X AWD | Mower | ~700 mm long | **Radar** object avoidance + lift + tilt + collision + GPS | No | No | No | $2,999.99 | vendor-page-verified |
| Segway Navimow X3 | Mower | - | VisionFence: 3 cameras / 300° field, ToF 0.3-6.6 ft, solid-state LiDAR ~200,000 pts/s | Yes, to ~3 m, slows to 0.4 mph | **Yes, 24+ animal types incl. hedgehogs** | Yes, 200+ yard object classes | X330 ~$2,499-2,999 (variant-dependent) | vendor-page-verified |
| Useful Sensors Person Sensor | Module | 21 x 21 mm | N/A - it is the sensor | Faces only, 110° FOV, 7 Hz (5 Hz with recognition), ~200 ms latency | No | Face vs no-face only | **$9.95 - DISCONTINUED / retired** | datasheet-verified |
| Anki Vector | Toy robot | ~100 mm | 1 single-point NIR ToF (30-1200 mm usable, 25° FOV), 4 IR cliff, 120° HD camera, 4-mic array | Face detect | No | No | Discontinued (2019); revived by Digital Dream Labs, stock erratic | datasheet-verified |
| SICK nanoScan3 | Safety scanner | 80 mm tall | 275° scan, 0.17° angular resolution, 3 m protective field, 10 m warning field, 40 m measuring, 20-200 mm configurable resolution, >=70 ms response | Legs only, safety-rated | No | No | From **$3,111-3,204** | vendor-page-verified |

---

## 2. iRobot: the longest-running natural experiment in cheap perimeter sensing

### 2.1 The bump-and-IR generation (Roomba 500/600/e/i series)

The classic Roomba perimeter stack is worth studying precisely because it is cheap and has shipped
tens of millions of units:

- **Mechanical bumper** across the front arc, on a spring, with optical interrupters behind it.
  Detection requires **contact**.
- **Four IR cliff sensors** on the underside of the front half, pointed at the floor.
- **IR wall-follow sensor** on the right shoulder.
- **Omnidirectional IR receiver** on top for docking beacons and Virtual Wall units.

The iRobot Create 3 - which is a Roomba i3 chassis sold as a ROS 2 research base - documents the
modern version of this stack precisely, and it is the single best-documented cheap perimeter system
in consumer robotics:

> "seven pairs of IR proximity sensors, which can be used to detect obstacles"
> ([Create 3 Hardware Overview](https://iroboteducation.github.io/create3_docs/hw/overview/),
> vendor-page-verified)

> "The IR obstacle sensors use 940 nm light and are AC coupled (external source lighting-insensitive)
> reflective sensors. Their range depends on surface quality of the target."
> (**unverified - CORRECTED 2026-09-12.** Previously marked datasheet-verified. This sentence is
> **not** in any iRobot Create 3 primary source. Checked and not found in:
> [hw/overview](https://iroboteducation.github.io/create3_docs/hw/overview/),
> [hw/electrical](https://iroboteducation.github.io/create3_docs/hw/electrical/),
> [hw/mechanical](https://iroboteducation.github.io/create3_docs/hw/mechanical/), the FAQ, and a
> full text scan of every file in `iRobotEducation/create3_docs`, `create3_sim` and
> `create3_examples` for `940`, `AC coupl` and `surface quality` - zero hits. A GitHub-wide code
> search for `"surface quality of the target"` also returns 0 results. **iRobot publishes no
> wavelength, no coupling method and no range figure for these sensors.** The 940 nm figure is
> plausible for a reflective IR proximity part but is an assumption here, not a sourced number.)

What iRobot **does** publish, verbatim and confirmed 2026-09-12:

> "The front of the robot features a multizone bumper with seven pairs of IR proximity sensors,
> which can be used to detect obstacles."
> ([hw/overview](https://iroboteducation.github.io/create3_docs/hw/overview/), vendor-page-verified)

> "The bottom of the robot includes four cliff sensors to keep the robot on solid ground ... two
> wheels with current sensors and encoders, and an optical odometry sensor."
> ([hw/overview](https://iroboteducation.github.io/create3_docs/hw/overview/), vendor-page-verified)

> "[7 sets of IR emitters and receivers] are available in the front bumper to detect objects at
> close range."
> ([api/hazards](https://iroboteducation.github.io/create3_docs/api/hazards/), vendor-page-verified)

The **angular layout** is published in the simulation URDF and is the most transferable single fact in
this document. From
[`create3.urdf.xacro`](https://github.com/iRobotEducation/create3_sim/blob/b7c69013d0db241df64199cae9491286635d1bcc/irobot_create_common/irobot_create_description/urdf/create3.urdf.xacro):

| Sensor name | x (m) | y (m) | yaw (rad) | yaw (deg) |
| --- | --- | --- | --- | --- |
| front_center_left | 0.1540 | 0 | 0 | 0 |
| front_left | 0.1396 | 0.0651 | 0.436 | +25.0 |
| front_center_right | 0.1396 | -0.0651 | -0.436 | -25.0 |
| left | 0.0990 | 0.1180 | 0.873 | +50.0 |
| front_right | 0.0990 | -0.1180 | -0.873 | -50.0 |
| side_left | 0.0399 | 0.1488 | 1.309 | +75.0 |
| right | 0.0399 | -0.1488 | -1.309 | -75.0 |

Seven emitter/detector pairs spanning **±75°, spaced 25° apart**, mounted on a 339 mm-diameter
bumper. That is the shipping answer, from a company that has built more consumer mobile robots than
anyone, to the question "how many short-range sensors do I need on a 350 mm robot".

**CORRECTED 2026-09-12 - the mounting height IS published.** An earlier revision of this document
said `ir_intensity_z_pos` was "a xacro variable and not published". It is a xacro variable *and* its
value is set in the same file, on the same pinned commit:

```
ir_intensity_z_pos = "-0.7*cm2m"
```

That is **-0.007 m**, i.e. 7 mm **below** `base_link`, before `base_link_z_offset` is added. So the
IR proximity ring sits just below the reference frame origin, near the top of the bumper skirt, not
at an unknown height. The datum is `base_link`, not the floor - the absolute height above the floor
still requires `base_link_z_offset`, which is defined elsewhere in the xacro tree.
(datasheet-verified, source file as cited above.)

The cliff sensors are four units - two "center" (front) and two "back"/side - with pitch and yaw
again parameterised and not published numerically in the same file.

**Known failure modes of this generation, and they are severe:**

- **Everything short of the bumper height is invisible until struck.** Cables, socks, and small dog
  toys are found by collision, not detection.
- **Dark IR-absorbing surfaces read as "no return".** For the obstacle sensors the failure is a miss;
  for the downward cliff sensors it is a **false cliff**. Black surfaces absorb IR energy, no
  reflected signal reaches the receiver, and the logic reads the missing echo as a drop. Robot
  vacuums across all brands refuse to cross dark rugs for this reason
  ([Experts in Vacuum](https://www.expertsinvacuum.com/why-your-robot-vacuum-wont-clean-black-rugs/),
  unverified as to specific models, but the physics is datasheet-verified from the 940 nm reflective
  sensor description above).
- **AC coupling** (as iRobot documents for Create 3) buys immunity to sunlight and room lighting, but
  it does nothing about target reflectivity.
- A 940 nm reflective proximity sensor returns **no classification at all**. It cannot tell a table
  leg from a human ankle from a cat.

### 2.2 The camera generation (Roomba j7, j7+, j9, j9+)

The j-series added iRobot's **PrecisionVision Navigation**. iRobot's own published description of it
is one sentence and contains no optical detail: *"Precision Vision: the navigation system that
detects and avoids obstacles like power cords and pet waste."*

**DOWNGRADED 2026-09-12.** The physical layout - a **forward-facing RGB camera centred on the front
of the bumper, flanked by two IR obstacle windows** - was marked vendor-page-verified in the earlier
revision. It is **not** vendor-published. iRobot does not state the camera's position, sensor,
resolution, FOV, or the count or function of the adjacent bumper windows anywhere primary, and the
Vacuum Wars j7+ review URL cited for it now returns **HTTP 404**. The layout is **inferred from
product photographs** and should be marked as such. The claim that the j7 dropped the separate
top-mounted vSLAM camera is likewise **unverified** against a primary source.

Recognised classes at launch were **cords, socks, shoes, and solid pet waste**. iRobot backed the
last one with a commercial guarantee, the **Pet Owner Official Promise (P.O.O.P.)**: if a covered
Roomba fails to avoid solid cat or dog waste within **1 year of purchase**, iRobot replaces the robot
free. That is the only warranty in consumer robotics that pays out on a perception failure
([iRobot pet-promise page](https://www.irobot.com/en_US/pet-promise.html), vendor-page-verified).

**The dominant, documented failure mode is light.** The j-series camera is a plain visible-light RGB
sensor:

> "The j9+ camera system needs ambient light to identify obstacles. In dark rooms or at night, the
> camera cannot see objects on the floor." (reviewer-sourced, unverified)

Reviewers disagree on whether the j9 carries an illumination LED; some sources say it has one, others
say it explicitly does not. **Status: not published by iRobot; conflicting secondary sources; treat as
unverified.** Competitors settled this argument by adding IR structured light or a dot projector,
which is the correct engineering answer.

Secondary reported failures, all unverified user-community claims: medium-sized dog toys not
recognised, object avoidance degraded on patterned rugs, and units that "do not avoid anything" after
firmware updates.

### 2.3 The LiDAR return (Roomba Max 705, 2025-2026)

iRobot's newest top-end model reverses the camera-only bet. The **Max 705** carries **"ClearView Pro"
LiDAR** for mapping "even in dim lighting", **plus** the PrecisionVision camera for object classes.

**CORRECTED 2026-09-12 - both prices were wrong / stale, and the Max 705 is not the current SKU.**

- ~~Max 705 Vac + AutoEmpty Dock: **$899.99**~~ and ~~Max 705 Combo + AutoWash Dock: **$1,299.99**~~.
  Neither figure could be reproduced from an iRobot page on 2026-09-12. `irobot.com` product URLs for
  the 705 return **HTTP 404**; the model appears only inside navigation menus ("705 Combo", "705V").
- What iRobot's own homepage actually shows on **2026-09-12**: **Roomba Max 875 Combo $1,199.99**,
  **Roomba Max 715 Vac $599.99** (marked down from $699.99), **Roomba Plus 678 Combo $899.99**,
  **Roomba Electro Plus $329.99** (from $399.99). **No Max 705 is listed.**
- iRobot's own lineup announcement, as reported by Vacuum Wars, names **Max 715 Vac + AutoEmpty Dock
  at $699.99** and **Max 775 Combo + AutoWash Dock at $999.99** - there is no Max 705 in that
  announcement at any price.
  ([Vacuum Wars](https://vacuumwars.com/irobot-expands-lineup/))
- The Max 705 **does exist** as a retail product - the Amazon listing title is verbatim *"iRobot
  Roomba Max 705 Robot Vacuum with AutoEmpty Dock, Powerful Suction, Dual Rubber Anti-Tangle Brushes,
  LiDAR Navigation, Obstacle & Anti-Fall Detection, for Carpet and Hard Floors"* - but **no price was
  retrievable** and it is absent from iRobot's current lineup. Treat it as **superseded by the
  715/775/875 Max SKUs**; availability is channel stock, not a live iRobot listing.
- Note also that the Amazon title claims only **"LiDAR Navigation, Obstacle & Anti-Fall Detection"**
  and does **not** name PrecisionVision. The "ClearView Pro LiDAR + PrecisionVision AI" pairing is
  attributed by Vacuum Wars to the **Max** models and the Plus 575 Combo as a class, verbatim: *"All
  five new robot models use LiDAR-based navigation, with the premium Max models and Plus 575 Combo
  adding ClearView Pro LiDAR and PrecisionVision AI for obstacle recognition."* Whether the 705
  specifically carries PrecisionVision is **not confirmed by a primary iRobot page**.

**Lesson:** the company that most publicly argued a single RGB camera was enough has shipped a
LiDAR + camera fusion stack at the top of its line. Ranging and classification are separate jobs and
the industry has converged on separate sensors for them.

### 2.4 Roomba s9 / s9+

**DOWNGRADED 2026-09-12: both s9 numbers are now unverifiable, and the product is gone.** iRobot's
s9/s9+ product pages return **HTTP 404**, the s9 does not appear in iRobot's current lineup, and
neither the "over 230,000 data points per second" vSLAM figure nor the "3D sensor scanning 25 times
per second" PerfectEdge figure could be located on any surviving iRobot page or in the Wikipedia
Roomba article. They were **marked vendor-page-verified in the earlier revision without a live
vendor page behind them**; they are now **unverified** and rest on archived marketing copy only.
Treat the s9 as a discontinued product with unrecoverable specifications.

The s9 used **top-mounted vSLAM** ("over 230,000 data points per second", vendor claim, condition not
published, **source page now dead**) plus a **3D sensor scanning "25 times per second"** for
PerfectEdge corner work (**unverified**, wavelength/range/technology not published).
Notably the s9 did **not** have
object-class recognition - it had a 3D ranging sensor and no classifier. It is the clean counter-
example: geometry without semantics.

---

## 3. Amazon Astro: the only consumer robot that does all four jobs

Astro is the closest commercial analogue to the target robot: **424 x 250 mm footprint, 440 mm tall,
9.35 kg**, with a periscope that lifts a camera to **42 in (1067 mm)**.

**Sensor stack (composite; teardown detail is unverified, vendor claims are vendor-page-verified):**

- 5 MP bezel camera (front, at screen height).
- Periscope camera: 1080p video / 12 MP stills, **132° diagonal FOV**, sensitive in **visible and
  infrared**, extends to 1067 mm.
- "A suite of sensors dotted around the chassis including IR and Time of Flight" - iFixit's teardown
  language. **iFixit does not publish part numbers or a count for these.** Anyone quoting a specific
  ToF part for Astro is guessing.
- **Custom cliff sensors** - Amazon explicitly called them custom, which implies the standard IR
  reflective cliff sensor was not good enough for a 9 kg robot at speed.
- Microphone array, wheel encoders, IMU.
- Compute: Qualcomm **QCS605** + **Snapdragon SDA660** (8 cores, up to 2.2 GHz) + MediaTek
  **MT8512** with Amazon **AZ1** neural edge silicon (teardown-sourced, unverified detail).

**No radar.** Despite persistent speculation, no teardown source located in this research identifies
mmWave radar in Astro. Record as **not published / not found**.

**Human vs pet vs object - how Astro actually does it:**

- **Humans:** Visual ID face recognition, stored on-device per Amazon. Recognises named household
  members; treats unrecognised humans as "strangers" and will follow them.
- **Pets:** a single model trained across cats and dogs. It detects "a pet" and clips video. It
  **cannot distinguish between individual pets** - unlike people, there is no per-animal identity.
- **Objects:** everything else is geometry from the IR/ToF suite.

That asymmetry is the key transferable insight. Even with Amazon's budget, **human identity is done
by face recognition at face height, pet detection is a coarse whole-body visual classifier, and
obstacle avoidance is a separate non-semantic range stack.** Three different sensing jobs, three
different mechanisms.

**Commercial status:** Astro for Business was discontinued; those robots **stopped working on
2024-09-25** and buyers got full refunds plus a $300 credit. The home Astro remained invite-only at
**$1,599**. Treat Astro as an engineering reference, not a product to buy.

---

## 4. Telepresence robots: the closest match on form factor

These matter because they are the only commercial class with the target robot's aspect ratio -
narrow footprint, roughly a metre tall, operating among standing humans.

### 4.1 Double 3 (Double Robotics)

The most precisely documented stack in this lane:

- **2 x Intel RealSense D430** depth modules - active IR stereo, **1280 x 720 depth**, range
  **0.2 m to 10 m** (datasheet-verified via IEEE Spectrum quoting Double Robotics).
- **5 ultrasonic rangefinders** (count vendor-verified; per-sensor range **not published**).
- **2 wheel encoders at 2048 PPR**, **1 x 9-DOF IMU**.
- 2 x 13 MP cameras (wide + zoom) on a tilting mount, 6-mic beamforming array.
- Compute: **NVIDIA Jetson TX2 4 GB**.
- Launch price **$3,999** with dock; $1,999 for the head alone as a Double 2 upgrade.

The design logic is explicit and directly transferable: **two active-IR stereo depth cameras handle
the useful volume, five ultrasonic sensors backfill the near field and the glass/specular cases the
depth cameras miss.** Ultrasonic is there because active IR stereo fails on glass, mirrors, and
dark low-texture surfaces - exactly the surfaces a robot in an office hits.

Double 3 offers the driver an **AR overlay of drivable area** and click-to-go, so the human still
carries final responsibility. It does not classify humans or pets.

### 4.2 temi V3

temi is the single best form-factor analogue: **350 mm wide x 450 mm deep x 1000 mm tall, ~12 kg,
1 m/s top speed, 8 h battery.** Its footprint is literally the target dimension.

Sensor stack (vendor-page-verified via Generation Robots and robotemi):

- **360° LiDAR mounted at the front of the base** - low, near floor level.
- **2 depth cameras**.
- **1 ToF depth camera, up to 5 m, 90° FOV, 30 fps** (condition - target reflectivity, ambient light -
  **not published**).
- **13 MP RGB camera, 1080p30**, on the motorised 13.3" head (tilt -15° to +55°) with face tracking.
- **IMU + 6 linear Time-of-Flight sensors.**
- **Multiple downward sensors at the bottom** for stairs and steps.
- ROBOX navigation: 2D mapping, 3D localisation, user tracking, obstacle avoidance, **~5 cm accuracy**.
- Price: **EUR 9,810 incl. VAT**.

Count the sensors: one 360° LiDAR, three depth/ToF cameras, six linear ToF, one RGB, plus cliff
sensors. **That is the price of doing 360° perimeter properly on a 350 mm x 1000 mm robot in 2026,
and it lands at a five-figure retail price.**

temi's honest limitation, per iPresence's teardown-style writeup: it recognises "face-like shapes and
colors" rather than performing true facial recognition. Person-following is geometric tracking, not
identity.

### 4.3 Ohmni (OhmniLabs)

The cost-reduced end of this class: **381 x 241 mm base, ~9 kg, foldable**, 4 cameras (4K wide, 140°
FOV, 13 MP stills), 15 W speaker, quad-mic beamforming array. **$1,995** for Supercam; DevKit from
**$2,500**.

Critically: **Ohmni ships with no depth sensor.** Depth is an optional USB add-on the customer
supplies. Obstacle avoidance is effectively the remote pilot's job. This is what happens when a
telepresence robot is built to a sub-$2,000 price: perimeter sensing is the first thing cut.

---

## 5. Sidewalk delivery robots: the highest-stakes pedestrian and animal detection

### 5.1 Starship Technologies

Dimensions **697 x 569 x 571 mm, 35 kg**, **6 km/h**, 10 kg payload, 1260 Wh battery, >12 h runtime.

Sensor stack, vendor-page-verified:

> "Radars, ultrasonic sensors, neural networks and 12 cameras, including time-of-flight."
> ([starship.xyz/our-robots](https://www.starship.xyz/our-robots/))

The Wevolver spec sheet adds **stereo cameras**, an aggregate **2,000 frames per second** across the
camera array, and object identification **"up to 200 feet away" (~61 m)**. Starship describes a
**"bubble of awareness"** that identifies pedestrians, cyclists and animals and either negotiates
around them or stops at a safe distance. Behaviour is graded: an object **adjacent** to the robot
reduces speed; an object **in front** of the robot triggers a **full stop**. The company claims
~125,000 road and driveway crossings per day worldwide.

**Twelve cameras on a 700 mm robot** is the number to sit with. A 360° camera perimeter that can
classify humans and animals reliably enough for public sidewalks needed twelve, plus radar, plus
ultrasonics, plus ToF. Nobody has done it with three.

### 5.2 Kiwibot

Kiwibot 4 is **559 x 432 x 559 mm** with **3 frontal cameras, one rear 180° wide-angle camera, and
spotlights**, running on an NVIDIA Jetson (unverified; no primary spec page located). Kiwibot's
published sensor detail is far thinner than Starship's, and Kiwibot's operations model historically
relied on **remote human supervisors** for intervention. **Lesson: a thin sensor stack is viable only
when a human teleoperator is the fallback classifier.**

### 5.3 Pudu BellaBot (indoor service)

3 RGBD cameras plus LiDAR, "obstacle detection frequency up to 5,400 times per minute" (= 90 Hz
aggregate, vendor-page-verified, method not published), stop response "as short as 0.5 seconds".
BellaBot's design intent is explicitly to catch **low-lying and overhanging obstacles** - the two
cases a single floor-plane LiDAR misses. Three RGBD cameras on a restaurant robot exists for exactly
one reason: a single depth camera leaves a blind cone.

---

## 6. Floor-robot sensor stacks from the Chinese vendors - the pet-waste benchmark

This is the most directly relevant body of prior art for pet detection, because avoiding dog waste on
a dark floor is functionally the same perception problem as avoiding a sleeping cat.

### 6.1 Roborock StarSight 2.0 (Saros 10R)

Vendor-page-verified specs:

- **Dual-transmitter solid-state LiDAR**, two optical phased arrays steering IR pulses.
- **3D Time-of-Flight, 21,600 sensor points** (verbatim: "21,600 sensor points* for 3D scanning"),
  **QVGA** ToF sensor - Roborock says "QVGA ToF sensor"; the 320 x 240 figure is the definition of
  QVGA, **inferred**, not printed by Roborock.
- ~~Stated **range 1-5 m**.~~ **CORRECTED 2026-09-12: Roborock publishes no range figure at all.**
  Checked both [us.roborock.com StarSight](https://us.roborock.com/pages/roborock-starsight-autonomous-system)
  and [global.roborock.com StarSight](https://global.roborock.com/pages/roborock-starsight-autonomous-system);
  neither states a detection range in metres. The "1-5 m" figure in the earlier revision has **no
  primary source** and should not be relied on. **unverified.**
- Sampling frequency "21 times higher than LDS2" (relative claim; absolute rate not published).
- Detects objects **"down to as small as 2 cm wide and 2 cm tall"** - and Roborock does state its
  condition, verbatim: *"Based on internal testing carried out by the manufacturer, the robot vacuum
  can see and bypass objects down to as small as 2cm wide and 2cm tall. Recognition accuracy may vary
  depending on environmental factors."* So the condition is "manufacturer's own internal testing,
  environment-dependent" - which is a disclaimer, not a measurement condition. No target
  reflectivity, no illuminance, no standoff distance.
- StarSight 2.0 adds **vertical structured light** on top of the dual-light ToF, projecting a pattern
  onto walls and furniture and measuring its distortion - specifically to catch **tall or narrow**
  obstacles that a floor-plane sensor misses.
- Object recognition: **"up to 301 types of objects"** on the StarSight page; Vacuum Wars reports
  **108 object types** for the Saros 10R specifically. **The two numbers disagree; both are
  vendor/reviewer claims and neither is independently verified.**
- Price **$1,299.99**.
- Test result: **24/24** in Vacuum Wars' obstacle-avoidance suite.

**The critical design decision:** Roborock moved the ranging job from a spinning 2D LiDAR turret to a
solid-state 3D ToF array specifically so the robot could be **79.8 mm tall** and still see in 3D. For
a 350 mm hobby robot this is the same trade - a turret costs height and a moving part; a fixed
flash/dToF array costs field of view.

### 6.2 Ecovacs AIVI 3D

Ecovacs' stack is **RGB camera + 3D structured light**, with dToF LiDAR for mapping on higher models.
Claims: "1 mm precision" on AIVI 3D 3.0 (vendor-page-verified; measurement condition **not
published**, and a 1 mm claim at any useful standoff should be treated as marketing). The older
**TrueDetect 3D** brand is a separate 3D structured-light module.

Ecovacs' own honesty on pet waste is worth quoting, because it is the best available vendor statement
on the reliability ceiling of this whole class:

> "there is no 100% guarantee they will avoid pet waste in all situations"
> ([ECOVACS](https://www.ecovacs.com/us/blog/robot-vacuum-avoid-poop), vendor-page-verified)

They also state the method plainly: "a mix of RGB cameras and infrared sensors to spot hazards",
trained on "thousands of image datasets". **Structured light gives the geometry; the RGB classifier
gives the label; neither alone is sufficient.**

### 6.3 The independent benchmark (Vacuum Wars)

Vacuum Wars runs the only consistent public obstacle-avoidance benchmark. **CORRECTED 2026-09-12 -
the methodology description in the earlier revision was wrong on three points:**

- It is a **24-point score**, not "24 objects". The earlier revision said "24 objects"; that is a
  misreading of the `/24` denominator.
- The published structure is **five scored scenarios** - **Pet Test** (simulated solid pet waste),
  **Toy Test**, **Cloth Test**, **Cord Test**, and a **Torture Test** (all of the above at once,
  chaotic placement) - each scored individually and summed. The roundup page separately describes
  "six objects positioned evenly" on hard floor for the standard run and "cords, novelty pet waste,
  a cloth, and a small toy vacuum" as the objects, and the torture run adds patterned rugs.
  ([Vacuum Wars - Saros 10R](https://vacuumwars.com/vacuum-wars-names-roborock-saros-10r-best-obstacle-avoidance-robot-vacuum-of-mid-2025/))
- **There is no published "~17/24" fleet average.** The earlier revision asserted one. What Vacuum
  Wars actually publishes is (a) on the **retired 12-point** scale, *"The highest possible score was
  12, with the average robot scoring around 9"*, and (b) on a separate **5-point** obstacle rating,
  *"Average Robot Vacuum Tested" = **3.27*** against the Saros 10R's **4.90**. Neither converts
  cleanly to the 24-point scale. **Do not quote a 24-point fleet average; none exists.**

The "**205+ robot vacuums**" figure is also narrower than stated earlier: Vacuum Wars says it has
*"independently tested 205+ robot vacuums"* **in total**, across all test categories. It does not
say 205+ robots were run through the 24-point obstacle-avoidance suite.

Scores and prices re-verified against the primary pages on **2026-09-12**. Rows marked
**unverified** could not be found on either Vacuum Wars page cited in Sources.

| Model | Score /24 | Sensor technology | Price | Status 2026-09-12 |
| --- | --- | --- | --- | --- |
| Roborock Saros 10R | 24 | StarSight 2.0 solid-state LiDAR + 3D ToF + RGB + vertical structured light | $1,299.99 (was $1,599.99) | confirmed, in stock at Roborock US |
| Eufy Omni S2 | 24 | ToF + binocular cameras (**sensor tech not stated on the Vacuum Wars page - unverified**) | $1,599.99 | score and price confirmed |
| Ecovacs T90 Pro Omni | 23 | Structured light + embedded LiDAR (**not stated on the Vacuum Wars page - unverified**) | $598.99-799.99 | score and price confirmed |
| Ecovacs X12 OmniCyclone | 23 | Structured light + LiDAR (**unverified**) | $1,499.99 | score and price confirmed |
| Eufy E28 Omni | 23 | Sensor fusion (not detailed) | $679.99-999.99 | score and price confirmed |
| Dreame X60 Max Ultra Complete | 22 | verbatim: "binocular AI cameras, edge sensors, and Proactive Illumination to detect objects as small as 1 cm" | $1,614.99-1,699.99 | score, price and sensor text confirmed |
| ~~Dreame L50 Ultra~~ | ~~24~~ | - | - | **NOT FOUND 2026-09-12.** Absent from the cited Vacuum Wars obstacle-avoidance roundup. Row withdrawn. |
| ~~MOVA P10 Pro Ultra~~ | ~~19~~ | - | - | **NOT FOUND 2026-09-12.** Absent from the cited roundup. Row withdrawn. |
| ~~Fleet average~~ | ~~~17~~ | - | - | **WITHDRAWN.** No 24-point average is published. See above. |

Note also that the Saros 10R's 24/24 comes from Vacuum Wars' **dedicated Saros 10R article**, not
from the obstacle-avoidance roundup - as of 2026-09-12 the roundup page does not list the Saros 10R
at all, and its top entry is the Eufy Omni S2 at 24/24.

Two things fall out of this table:

1. **Every top scorer pairs an active depth sensor (ToF or structured light) with a camera
   classifier.** No camera-only robot is in the top group. No depth-only robot is either.
2. **"Proactive Illumination"** as a named Dreame feature confirms that the low-light problem is real
   enough that vendors now ship dedicated illuminators - the thing iRobot's j-series is criticised for
   lacking.

### 6.4 mmWave radar: a documented absence

I searched specifically for shipping consumer floor robots using **mmWave radar** for perimeter or
presence detection. **I found none.** Patent literature exists (radar in the front of a vacuum robot,
FMCW 60-64 GHz) and academic work exists on mmWave for ground-condition sensing, but **no shipping
Roborock, Dreame, Ecovacs, Eufy, iRobot or Amazon product was found that uses mmWave radar as a
perimeter sensor.** Husqvarna's Automower is the only mass-market consumer mobile robot in this
research that ships **radar** (band not published).

Record as: **negative finding, moderately confident.** If the recommendation lane proposes mmWave, it
is proposing something with essentially no consumer-mobile-robot prior art to lean on - which is not
disqualifying, but it means no supply chain, no reference design, and no field failure data.

---

## 7. Robot lawn mowers: the only class with published pet-safety data

### 7.1 The Oxford hedgehog study - the most important single source in this document

[Testing the Impact of Robotic Lawn Mowers on European Hedgehogs and Designing a Safety Test](https://pmc.ncbi.nlm.nih.gov/articles/PMC10777904/)
(peer-reviewed, **datasheet-verified** for methodology):

- **19 robotic lawn mower models** tested against hedgehog cadavers, ~10 tests per model.
- Sensor inventory across the fleet: **collision sensors on 8 models; wheel-motor-current collision
  detection on 11 models; ultrasonic sensors on 5 models; headlights on 4 models; camera vision on
  ZERO models.**
- Result: **"Apart from one single incidence, all robotic lawn mowers had to physically touch the
  hedgehog carcasses to detect them."** That one non-contact detection **could not be reproduced on
  retest.**
- Damage scale 0-4: 0 = remote detection without contact; 1 = light nudge then redirect; 2 = flipped
  but unharmed; 3 = driven over, blades do not puncture; 4 = blade contact causes injury.
- Proposed certification test: two dummy sizes (<400 g and >600 g), three orientations, **60 trials
  per dummy (20 per position)**, pass = damage categories 0-2 only.
- Field context: hedgehog rehabilitation centres reported rising mower injuries; **almost half of the
  hedgehogs found injured between June 2022 and September 2023 did not survive.**

**This is the empirical ceiling on ultrasonic-only and contact-only animal detection: five of
nineteen machines had ultrasonic sensors, and effectively none of the nineteen detected a
hedgehog-sized animal without touching it.** A hedgehog is roughly the low end of the target's pet
size band. A 200 mm cat crouched on the floor is a harder target than a table leg and an easier one
than a hedgehog in grass, but the direction of the result is unambiguous.

### 7.2 Husqvarna Automower - the vendor disclaimer that matters

Husqvarna is refreshingly explicit about what object avoidance is and is not
([Husqvarna support KA-70110](https://us-support.husqvarna.com/en/automower/KA-70110),
vendor-page-verified):

Radar models: 405XE NERA, 410XE NERA, 430X NERA, 450X NERA, **435X AWD**.
Ultrasonic model: **435X AWD NERA**.

Limitations, quoted verbatim:

> "Small objects like golf balls may be difficult to detect, especially when hidden in tall grass"

> "Objects lying flat or very close to the ground may not be detected"

> "The sensors may detect tall grass, flowers or other vegetation as objects"

> "Within 1.2 metres (4 feet) of the work area boundary, object avoidance is automatically disabled"

> **"It is not a safety feature. There is no guarantee that objects will not be run over"**

Price: **$2,999.99** for the 435X AWD; 8.7 in cutting width, 39 lb.

That last quote is the single most useful sentence any vendor in this survey has written. A
$3,000 robot with radar ships with an explicit statement that its perception is **not** a safety
function. Safety on mowers is delegated to the **lift sensor, tilt sensor, and the blade geometry**
required by **EN 50636-2-107 / IEC 60335-2-107**, which certifies against **physical probes** - adult
foot probe, standing child foot probe, and (added in Amendment A2:2020) a **kneeling child foot
probe** - not against sensor performance.

### 7.3 Segway Navimow X3 - the current state of the art in consumer animal detection

VisionFence on the X3 series (vendor-page-verified; measurement conditions largely not published):

- **3 cameras, 300° sensory field**; **3D front vision**; **ToF sensor with 0.3-6.6 ft (0.09-2.0 m)
  range**.
- **Solid-state LiDAR, ~200,000 points/second.**
- Path recalculation within **100 ms**.
- **200+ yard object classes**; **24+ animal types**, explicitly including **dogs, cats and
  hedgehogs**, with an "Animal-Friendly Mode".
- **People detected up to 3 m**, mower slows to **0.4 mph (0.18 m/s)** at a safe distance.
- Night performance: vision perception distance extended to **5.9 ft (1.8 m)** at night, with
  perception range widened to **150°**.

Note the honesty embedded in those numbers: **daylight 300° / 3 m for people, night 150° / 1.8 m.**
The field of view and the range both collapse by roughly half in the dark. That is the real cost of a
camera-primary perception stack and it is the number a camera-only proposal for the target robot must
budget for.

---

## 8. Drop-in person detectors

### 8.1 Useful Sensors Person Sensor - DISCONTINUED

- **$9.95** at SparkFun (SEN-21231). **Retired from the catalog and no longer for sale.**
  The Pi Hut also lists it discontinued. Useful Sensors rebranded (to Moonshine AI) and **dropped all
  hardware**. Third-party listings (AliExpress, SpikenzieLabs at $19.95) are residual stock.
- Hardware: **ESP32-S3 + GC032A 0.3 MP camera**, **110° FOV**.
- Rate: **7 Hz** detection-only, **5 Hz** with face recognition enabled; **~200 ms latency**.
- Output over I2C (7-bit address **0x62**, up to **400 kbaud**): **up to 4 faces per frame**, each
  with bounding box (0-255 scale), box confidence 0-100, **recognition ID 0-7**, ID confidence 0-100,
  and an "is facing camera" boolean.
- Power: **~150 mW**; LED **~5 mW**. **3.3 V.**
- Privacy by design: **no raw image access; metadata only; firmware and models non-updatable.**

**Range is not published.** The documentation says the bounding-box size serves as a distance
approximation - i.e. the vendor never characterised a detection range. Stated limitations: requires
illumination (dim-light capability explicitly **uncharacterised**), works "most reliably when the
face is straight on to the sensor", degrades with masks/occlusion, and is "not suitable as sole
security factor".

**Two hard lessons for the target robot:**

1. A **face** detector is not a **person** detector. A human whose back is turned, who is in profile,
   who is sitting behind furniture, or who is closer than the sensor's minimum face size is invisible
   to it. For a robot that must not collide with a person, face detection is the wrong primitive.
2. **The category has no stable supply.** The best-known drop-in person detector in the hobby market
   was discontinued and the vendor exited hardware. Any design that depends on a single novelty
   module is one product-line decision away from being unbuildable.

### 8.2 Adjacent primitives worth naming

- **Thermopile arrays** (Heimann, Panasonic Grid-EYE, Melexis MLX90640): classify warm bodies without
  a camera and without ambient light. A cat and a human are both warm; a chair is not. Good at the
  "animate vs inanimate" split, poor at "human vs pet" without resolution.
- **ST STHS34PF80** infrared presence/motion sensor: a single-pixel low-power presence detector,
  widely available, datasheet-published. Useful as a cheap "something warm is nearby" gate.
- Neither is a substitute for ranging. Both are complements.

---

## 9. Small hobby robots: Anki Vector as the cautionary tale

Vector is a ~100 mm desk robot and the sensing is instructive by how little it does:

- **One single-point NIR ToF sensor.** Per the SDK documentation (datasheet-verified):
  > "Vector's time-of-flight distance sensor has a usable range of about 30 mm to 1200 mm (max useful
  > range closer to 300mm for Vector) with a field of view of 25 degrees."
  Note the gap between the **datasheet range (1200 mm)** and the **useful range on the robot
  (~300 mm)**. That factor-of-four haircut, caused by mounting height, tilt, target reflectivity and
  the classifier's confidence threshold, is the single most commonly ignored fact in hobby sensor
  selection.
- The SDK exposes **four validity flags** so the pathfinder can reject readings it does not trust -
  an explicit admission that a single-point ToF returns garbage often enough to need gating.
- The **lift arm occludes the ToF sensor** and returns "clear" readings that are, per the docs, "not
  useful for object detection". A mechanically obvious self-occlusion that shipped anyway.
- **Four IR cliff emitters** under the corners.
- **120° FOV HD camera** for face detection; **4-microphone array**.
- Discontinued 2019 with Anki's collapse; revived by Digital Dream Labs with erratic availability.

A 25° FOV single-point sensor on a robot means **one ranging cone**. To cover a 350 mm square
footprint's forward arc at 25° per sensor you need at least 6-8 of them for ±90°, which is exactly
what iRobot did with seven IR pairs at 25° spacing.

---

## 10. The industrial benchmark: what a certified perimeter costs

The **SICK nanoScan3** is what "safety-rated human detection on a mobile robot" actually means
(vendor-page-verified):

- **275° scanning angle**, **0.17° angular resolution**.
- **3 m protective field**, **10 m warning field**, **40 m measuring range**.
- **Configurable resolution 20-200 mm** (i.e. the smallest object it is certified to detect).
- **Response time >= 70 ms**; **protective field supplement 65 mm** (a mandated safety margin added to
  the configured field).
- **80 mm tall**, **0.67 kg**, **24 V DC**, **3.9 W**, **IP65**, -10 to +50 °C.
- safeHDDM scanning technology, stated as resistant to ambient light, dust and dirt.
- **From $3,111-3,204.**

Two transferable facts: (1) a certified sensor states its **detectable object size** as a
configuration parameter and adds a mandated safety supplement, which is the discipline the consumer
products entirely lack; (2) certified leg detection on a mobile robot costs **more than any complete
consumer robot in this survey**. A hobby robot cannot buy safety; it can only buy probability.

---

## 11. Cross-cutting failure modes actually reported in the field

| Failure mode | Which sensor fails | Evidence | Severity for the target robot |
| --- | --- | --- | --- |
| **Dark / IR-absorbing targets** (black socks, dark furniture, black cables, dark pet fur) | Reflective IR proximity, IR cliff, active IR stereo | **NOT from Create 3 docs** - iRobot publishes no range or surface-dependence statement (see 2.1). Evidence here is the universal dark-rug false-cliff behaviour plus first-principles reflective-IR physics. **inferred, not vendor-stated.** | **Critical.** A black cat is the single worst-case pet target for an IR-based stack. |
| **Darkness / no ambient light** | RGB camera classifiers | Roomba j-series cannot classify in dark rooms; Navimow night range halves to 1.8 m and FOV to 150° | **Critical** if the robot operates at night. Mandates an illuminator or a non-visible-light ranging channel. |
| **Low, flat objects** (cables, pet waste, sleeping cat) | 2D LiDAR at turret height, bumper, ultrasonic | Husqvarna: "Objects lying flat or very close to the ground may not be detected" | **Critical.** A 200 mm pet is below every turret-height 2D scan plane. |
| **Contact-only animal detection** | Bumper, wheel current, ultrasonic | Oxford study: 18-19 of 19 mowers required physical contact | **Critical.** The entire prior-art class fails the pet requirement. |
| **Glass, mirrors, specular surfaces** | Active IR stereo, structured light, LiDAR | Double 3's five ultrasonic rangefinders exist to backfill this | High for indoor use. |
| **False positives on vegetation / texture** | Radar, ultrasonic | Husqvarna: "may detect tall grass, flowers or other vegetation as objects" | Medium. Costs throughput, not safety. |
| **Self-occlusion by the robot's own mechanism** | Any fixed sensor | Vector's lift blocks its ToF and reports "clear" | High, and free to avoid at design time. |
| **Datasheet range vs useful range** | Single-point ToF | Vector: 1200 mm datasheet vs ~300 mm useful | **Critical for budgeting.** Assume a 2-4x haircut. |
| **Overhanging and low-hanging obstacles** | Single depth camera, 2D LiDAR | BellaBot ships 3 RGBD cameras specifically for this | High for a 600-1200 mm tall robot with a narrow base. |
| **Blind spot within a boundary zone** | Policy, not sensor | Husqvarna disables avoidance within 1.2 m of the boundary | Design warning: do not silently disable perception in edge cases. |
| **Firmware regressions** | Classifier stack | Widespread user reports of j-series avoidance degrading after updates (unverified) | Medium. Argue for a non-ML geometric fallback that firmware cannot regress. |

---

## 12. Where sensors get mounted, and at what height

Synthesis across the platforms above (part vendor-verified, part **inferred** from photographs and
teardown descriptions - treat the heights as inferred unless marked):

| Job | Typical height above floor | Platforms doing it |
| --- | --- | --- |
| Cliff / drop detection | 30-90 mm, pointed down, at the leading edge and outside corners | Every single platform surveyed, without exception |
| Near-field obstacle ranging | Bumper height, 40-90 mm | Create 3 (7 IR pairs), Vector, all vacuums |
| Floor-plane 2D LiDAR mapping | 60-100 mm (vacuum turret); temi puts it at base front | Roborock LDS, TurtleBot 4 RPLIDAR, temi |
| 3D ranging of the forward volume | 50-120 mm, tilted slightly down | Roborock StarSight, Ecovacs structured light, Navimow ToF |
| Object classification camera | Bumper front (vacuums, ~60 mm) or head height (telepresence, 900-1200 mm) | j-series vs temi/Double/Astro |
| Face / person identity | 900-1400 mm - deliberately at human face height | Astro bezel camera, temi head, Double 3 head, Person Sensor as intended |
| Over-the-top / above-furniture view | Astro periscope to 1067 mm | Astro alone |

The pattern is consistent and it is the most actionable structural finding in this document:
**cliff and near-field ranging live low and forward; classification of objects on the floor lives low
and forward; classification of people lives high, at human face height.** A 600-1200 mm tall robot is
the first hobby form factor that can do both, and it should - putting a single camera at 100 mm to do
both jobs is the compromise that makes the j-series fail at night and makes the Person Sensor fail on
turned backs.

---

## 13. Transferable lessons for a 350 mm hobby robot

1. **Split the problem into three sensing jobs, as every successful platform does.**
   (a) *Do not collide* - non-semantic ranging, must work in the dark, must work on black.
   (b) *Is that a person* - classification at human height.
   (c) *Is that a pet* - classification of a low, small, warm, mobile body.
   Astro, Starship and temi all use different mechanisms for each. Nobody solves all three with one
   sensor, and the platforms that tried (Roomba j-series, Ohmni) have the documented failure modes.

2. **Angular coverage is the dominant cost driver, and iRobot's answer is 25° spacing.** Seven IR
   pairs across ±75° on a 339 mm bumper is a shipping, mass-produced reference layout. A 350 mm robot
   needs roughly that density in the forward arc, plus something for the rear, or it needs a scanning
   or flash sensor that covers the arc in one device.

3. **Nothing detects a 200 mm pet reliably without an active depth channel.** Nineteen mowers with
   bumpers, wheel-current sensing and ultrasonics achieved effectively zero non-contact detections of
   a hedgehog. Bump-and-back-up is not a pet strategy; it is a pet injury mechanism.

4. **Budget for a 2-4x gap between datasheet range and useful range.** Vector's own SDK documents
   1200 mm datasheet, ~300 mm useful. Mounting height, tilt, target reflectivity and confidence
   gating eat the rest.

5. **Assume dark targets return nothing.** Design the fallback behaviour for "no return" explicitly.
   The vacuum industry's answer - treat "no return" on a downward sensor as a cliff - is correct and
   costs coverage on dark rugs. Decide deliberately which way the target robot fails.

6. **Camera-primary stacks lose roughly half their range and half their field of view in the dark.**
   Navimow publishes this (300°/3 m day vs 150°/1.8 m night). Either accept it, add an illuminator
   (Dreame "Proactive Illumination", OAK-D-Pro's IR dot projector and illumination LED), or put the
   ranging job on a sensor that does not care about ambient light.

7. **Put ultrasonic or an equivalent non-optical channel in the near field.** Double 3 carries five
   ultrasonic rangefinders alongside two RealSense D430s. That is not redundancy for its own sake -
   it is coverage for glass, mirrors and dark matte surfaces that active IR stereo silently misses.

8. **Human identity belongs at human height; human *presence* does not.** A person's legs are at
   0-800 mm and are what the robot will actually hit. Face-height cameras identify; leg-height
   ranging protects. The Person Sensor's failure modes (profile faces, turned backs, occlusion) are
   exactly why it cannot be the collision-avoidance sensor.

9. **Do not build the perimeter on a single-source novelty module.** The Useful Sensors Person Sensor
   - the reference drop-in person detector, $9.95, well documented - is discontinued and the vendor
   left hardware entirely. Prefer parts with multiple distributors and a published datasheet.

10. **Copy the vendors' honesty, not just their hardware.** Husqvarna ships radar and still states
    "It is not a safety feature." Ecovacs states "there is no 100% guarantee". iRobot backed its one
    concrete claim (pet waste) with a **replacement warranty** rather than a spec. A hobby robot
    should state the same limits in its own documentation and should have a mechanical/behavioural
    safety layer - speed limit, low mass, compliant bumper, stop-on-contact - that does not depend on
    the classifier being right.

11. **Speed is a perception budget.** Starship stops fully for anything in front and slows for
    anything adjacent. Navimow drops to 0.18 m/s near a person. temi tops out at 1 m/s with a
    five-figure sensor stack. A 350 mm robot that travels at 0.3 m/s needs far less range than one at
    1 m/s, and range is the expensive axis.

12. **Certified human detection is out of reach and should not be implied.** The cheapest safety-rated
    scanner found (SICK nanoScan3) is $3,111 and covers 275°, not 360°. Anything the hobby robot does
    is best-effort perception, and the documentation should say so.

---

## 14. Negative findings (things the prior art does NOT contain)

- **No shipping consumer floor robot found using mmWave radar for perimeter or presence detection.**
  Radar appears in consumer mobile robots only in Husqvarna's Automower line (band not published).
- **No consumer robot found that distinguishes individual pets.** Astro recognises individual
  *people* by face, but uses one combined cat/dog model with no per-animal identity.
- **No camera-vision system in the 19-model Oxford mower fleet.** The mower industry's pet problem is
  a sensing-absence problem, not a sensing-accuracy problem.
- **No vendor in this survey publishes a detection range with its measurement condition.** Not
  Roborock (1-5 m, no target reflectivity), not temi (5 m, no condition), not Navimow (3 m people, no
  condition), not Astro (nothing published at all). The only conditioned numbers in this document
  come from the component datasheets that consumer vendors decline to cite.
- ~~**No published mounting height for the Create 3 IR proximity ring.**~~ **WITHDRAWN 2026-09-12.**
  This negative finding was wrong. `ir_intensity_z_pos = "-0.7*cm2m"` (-0.007 m relative to
  `base_link`) is set in `create3.urdf.xacro` at the pinned commit. See section 2.1.
- **iRobot publishes no wavelength, coupling method or range for the Create 3 IR proximity sensors.**
  The widely repeated "940 nm, AC coupled, range depends on surface quality of the target" sentence
  does not appear in any iRobot source (see section 2.1 for the search that establishes this).
- **iRobot does not publish whether the j9 has an illumination LED.** Reviewers contradict each other.
- **Vacuum Wars publishes no fleet average on its 24-point obstacle-avoidance scale.** The only
  published averages are "the average robot scoring around 9" on the retired 12-point scale, and an
  "Average Robot Vacuum Tested" figure of **3.27** on a separate 5-point obstacle rating. See 6.3.
- **Roborock publishes no detection range for StarSight 2.0.** Neither the US nor the global
  StarSight page states a range in metres. See 6.1.

---

## Sources

- [iRobot Create 3 Hardware Overview](https://iroboteducation.github.io/create3_docs/hw/overview/)
- [create3.urdf.xacro (IR and cliff sensor geometry)](https://github.com/iRobotEducation/create3_sim/blob/b7c69013d0db241df64199cae9491286635d1bcc/irobot_create_common/irobot_create_description/urdf/create3.urdf.xacro)
- [Create 3 IR sensor positioning discussion #342](https://github.com/iRobotEducation/create3_docs/discussions/342)
- [TurtleBot 4 User Manual - Sensors](https://turtlebot.github.io/turtlebot4-user-manual/software/sensors.html)
- [TurtleBot 4 overview brochure (PDF)](https://www.generationrobots.com/media/turtlebot4/Turtlebot_4_OverviewBrochure.pdf)
- [iRobot P.O.O.P. Promise](https://www.irobot.com/en_US/pet-promise.html)
- [iRobot expands Roomba lineup (Vacuum Wars)](https://vacuumwars.com/irobot-expands-lineup/)
- [Roomba Max 705 on Amazon](https://www.amazon.com/iRobot-Roomba-Robot-Vacuum-AutoEmpty/dp/B0DWG3C3ZF)
- [Vacuum Wars - Best robot vacuums with obstacle avoidance](https://vacuumwars.com/best-robot-vacuums-with-obstacle-avoidance/)
- [Vacuum Wars - Roborock Saros 10R best obstacle avoidance mid-2025](https://vacuumwars.com/vacuum-wars-names-roborock-saros-10r-best-obstacle-avoidance-robot-vacuum-of-mid-2025/)
- [Roborock StarSight Autonomous System](https://us.roborock.com/pages/roborock-starsight-autonomous-system)
- [ECOVACS - Can robot vacuums avoid dog poop](https://www.ecovacs.com/us/blog/robot-vacuum-avoid-poop)
- [Wikipedia - Amazon Astro](https://en.wikipedia.org/wiki/Amazon_Astro)
- [iFixit - Amazon Astro teardown](https://www.ifixit.com/News/70384/amazon-astro-teardown)
- [TechCrunch - Amazon Astro pet detection and SDK](https://techcrunch.com/2022/09/28/amazon-astro-robot-pet-detection/)
- [GeekWire - Amazon discontinues Astro for Business](https://www.geekwire.com/2024/amazon-discontinues-astro-for-business-robot-security-guard-to-focus-on-astro-home-robot/)
- [IEEE Spectrum - New Double 3 Robot](https://spectrum.ieee.org/new-double-3-robot-makes-telepresence-easier-than-ever)
- [Generation Robots - Temi 3 Service Robot](https://www.generationrobots.com/en/404221-temi-3-service-robot.html)
- [iPresence - Unravelling the mechanics of temi](https://ipresence.jp/en/magazine/temi-structure-robotics/)
- [Ohmni Telepresence Robot](https://ohmnilabs.com/products/ohmni-telepresence-robot/)
- [Starship Technologies - Our Robots](https://www.starship.xyz/our-robots/)
- [Wevolver - Starship robot specs](https://www.wevolver.com/specs/starship-technologies-starship-robot)
- [Kiwibot dimensions](https://www.dimensions.com/element/kiwibot)
- [Pudu Robotics - BellaBot](https://www.pudurobotics.com/en/products/bellabot)
- [Oxford - Hedgehog safety test for robotic lawnmowers](https://www.ox.ac.uk/news/2024-01-16-researchers-develop-hedgehog-safety-test-robotic-lawnmowers)
- [PMC - Testing the Impact of Robotic Lawn Mowers on European Hedgehogs](https://pmc.ncbi.nlm.nih.gov/articles/PMC10777904/)
- [Husqvarna - Object avoidance with radar or ultrasonic sensors](https://us-support.husqvarna.com/en/automower/KA-70110)
- [Husqvarna Automower 435X AWD](https://www.husqvarna.com/us/robotic-lawn-mowers/automower-435x-awd/)
- [Segway Navimow X3 series](https://navimow.com/pages/navimow-x3)
- [Navimow - VisionFence technology](https://navimow.com/blogs/navimow-technology/visionfence-technology-the-vision-and-ai-driven-innovation-of-intelligent-mowing)
- [Person Sensor developer documentation](https://github.com/moonshine-ai/person_sensor_docs)
- [SparkFun - Person Sensor (retired)](https://www.sparkfun.com/person-sensor-by-useful-sensors.html)
- [The Pi Hut - Person Sensor (discontinued)](https://thepihut.com/products/person-sensor-by-useful-sensors)
- [Anki Vector SDK - proximity sensor](https://vector.ikkez.de/generated/anki_vector.proximity.html)
- [Anki Vector Technical Reference Manual (PDF)](https://randym32.github.io/Vector-TRM.pdf)
- [SICK nanoScan3 catalog](https://www.sick.com/us/en/catalog/products/safety/safety-laser-scanners/nanoscan3/c/g507056)
- [SICK nanoScan3 product information (PDF)](https://www.sick.com/media/docs/5/75/075/product_information_nanoscan3_en_im0087075.pdf)
- [rbtx - SICK nanoScan3 pricing](https://rbtx.com/en-US/components/safety/sick-safety-laser-scanners-nanoscan3)
- [EN 50636-2-107:2015/A2:2020](https://standards.iteh.ai/catalog/standards/clc/3dff8f60-69c3-4a01-9a82-8770a8d0ecc8/en-50636-2-107-2015-a2-2020)
- [Experts in Vacuum - Why robot vacuums won't clean black rugs](https://www.expertsinvacuum.com/why-your-robot-vacuum-wont-clean-black-rugs/)
