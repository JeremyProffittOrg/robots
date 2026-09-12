# Options beyond the two catalogues: the rest of ST, and scanning lidar

Two things are worth buying outside the Adafruit and DFRobot catalogues this reference has covered so
far, and only two. The first is the **ST VL53L3CX multi-target ranger** on a Pololu carrier, at
`$19.95`. The second is a **360 deg planar dTOF scanning lidar** - the Slamtec RPLIDAR C1 at `$69.00`
or the LDROBOT LD19 at `$99.00`. Everything else in this chapter is either a part with no hobby
breakout, a part whose datasheet could not be read, or a scanner that costs more mass, more power or
more money than the two named above for no gain on a 350 mm robot.

The second half of the chapter answers the question the operator actually asked: a spinning lidar is
not a better ToF ring, it is a different sensor with a different blind spot, and the two blind spots
are complementary rather than overlapping.

## Part 1 - the rest of ST's FlightSense portfolio

### VL53L3CX: the only ST part worth leaving the Adafruit catalogue for

The VL53L3CX reports **up to four ranges at once inside one cone** (datasheet-verified, ST DS13204
Rev 2, [mirror](https://www.pololu.com/file/0J1765/vl53l3cx.pdf)). No other single-cone ST part does
this, and Adafruit does not stock it.

| Parameter | Value | Condition |
|---|---|---|
| Field of view | 25 deg, the datasheet's single cone figure | full FoV assumed covered by all range rows |
| Range, white 88 % | 310 cm typical at 94 % detection | 30 ms budget, 23 C, indoor, no infrared |
| Range, grey 17 % | 170 cm typical | same |
| Range, outdoor overcast | 100 cm at 88 %, 70 cm at 17 % | ST equates this to about 5 kLux daylight |
| Active current | 16 mA typical, 40 mA peak | 23 C, 2v8 |
| Host cost | not recommended for 8-bit MCUs | histogram driver needs RAM and code space |

**Vendor overclaim, flagged.** Pololu's carrier [#3416](https://www.pololu.com/product/3416) is titled
"500cm Max" and its body text says 5 m. There is no 5 m row anywhere in DS13204 Rev 2. Use **310 cm
against white 88 % and 170 cm against grey 17 %, both indoors with no infrared**, both
datasheet-verified.

The multi-target output is a weak but free classification cue. A cone that reports "something at
0.6 m **and** something at 2.4 m" is looking at a thin object with the room still visible behind it;
a cone that reports only 0.6 m is looking at something broad enough to occlude the background. That
separates a chair leg from a human torso. It does not separate a sleeping cat from a handbag.

**Verdict: worth it, for one or two positions.** Not for a whole ring - at `$19.95` against the
VL53L4CX's `$14.95` it costs more and reaches less far.

### VL53L1CB and VL53L4ED: not verified, and that is a tooling limit

Both parts' datasheets are hosted only on `st.com`, which was **unreachable from the research machine
in every pass** (`curl` returned `Recv failure: Connection was reset` and a 40 s timeout; `WebFetch`
timed out at 60 s). Nothing about either is asserted here beyond what ST's own product page text
carries.

- **VL53L1CB** - ST's cover-glass-optimised sibling of the VL53L1X ranging core. **No VL53L1CB-specific
  number is verified.** No Pololu or Adafruit breakout exists. If you want the VL53L1X ranging core,
  buy the VL53L1X: Pololu [#3415](https://www.pololu.com/product/3415), `$22.95`, read 2026-09-12.
- **VL53L4ED** - ST's low-power variant of the VL53L4CD. ST's product page states **18 deg FoV, 1 mm to
  1300 mm in standard conditions, and accurate measurement to 800 mm under 5 klx ambient with special
  settings**. That is **vendor-page-verified, not datasheet-verified**. There is no hobby breakout; it
  is a bare module aimed at battery-powered consumer products.

Neither part changes a design decision on this robot. Skip both.

Two traps worth restating while ST parts are on the page. First, the **VL53L1X's receiver field is
programmable from 15 deg to 27 deg, and the 27 deg figure is a diagonal** (DocID031281 Rev 3). The
horizontal field is narrower than the diagonal, so sizing a ring from 27 deg overstates coverage;
`coverage-geometry.md` owns that arithmetic. Second, the VL53L1X's headline reach is a dark-room
number: long mode gives **360 cm typical in the dark but collapses to 73 cm under strong ambient**
(200 kcps/SPAD, 100 ms budget, white 88 % target), while short mode barely moves, **136 cm dark to
135 cm ambient**. Size any single-cone perimeter on the ambient column, not the dark column.

### SATEL evaluation boards

ST sells postage-stamp "satellite" carriers - `VL53L4CX-SATEL`, `VL53L3CX-SATEL`, `VL53L1CB-SATEL`,
`VL53L5CX-SATEL` - that plug into the matching `X-NUCLEO-53L*A1` expansion shield for evaluation on a
Nucleo board. **Their pack quantity, contents and prices are not verified**: every SATEL page lives on
`st.com`. They are listed here so the option is not silently omitted. Their real use is ST's reference
cover-glass geometry and calibration flow, which matters if you intend to put a window in front of a
ring. Price them at Mouser or DigiKey before committing to a custom carrier.

ST's **automotive and industrial FlightSense** parts are in the same unverified position and are
practically irrelevant: AEC-Q100 extended-temperature parts on broker MOQ, offering no more range and
no wider cone than the VL53L4CX. Qualification does not solve an information problem.

### The two short-range ST parts, for completeness

The brief names them, so state the role and move on.

- **VL6180X** (DocID026171 Rev 7) is specified to **0 to 100 mm**, with the datasheet noting that
  ranging beyond 100 mm depends on target reflectance and external conditions. Under **5 kLux diffuse
  halogen** it holds **> 70 mm at 88 % and > 60 mm at 17 %** reflectance. On a 350 mm robot that means
  the obstacle is already under the bumper, so its only defensible role is bump-imminent or cliff
  detection. Pololu's carrier is **End-of-Life Rationing**, so do not design it in. That listing also
  markets **20 cm** by default and **60 cm** "at the cost of reduced resolution" - both above the
  datasheet's 100 mm, and neither carries a reflectance condition.
- **VL53L4CD** (DS13812 Rev 8) reaches **typ 1200 mm against white 88 % at 90 % detection indoors and
  typ 450 mm against grey 17 %**, falling to **550 mm and 400 mm** outdoor overcast. 45 cm against a
  dark target is a bumper sensor too.

### Where to buy, and at what price

| Part | Vendor and SKU | Price (read 2026-09-12) | Status |
|---|---|---|---|
| VL53L3CX | Pololu 3416 | `$19.95` | active |
| VL53L1X | Pololu 3415 | `$22.95` | active |
| VL53L4CD | Pololu 3692 | `$13.95` | active |
| VL6180X | Pololu 2489 | `$19.95` | **End-of-Life Rationing** |
| VL53L4CX | Adafruit 5425 | `$14.95` | in stock |
| SATEL boards | ST / Mouser / DigiKey | **not published in this pass** | unverified |

**Gap, stated plainly.** Mouser's datasheet mirrors returned anti-bot JavaScript and a segfault, and
no DigiKey page was read in this pass, so **no Mouser or DigiKey price is quoted in this chapter**. SparkFun sells a Qwiic dToF Imager built on the ams-OSRAM TMF8820/8821, not on an ST
part; **its price was not read**. Pololu is the only non-Adafruit vendor with verified prices here.

## Part 2 - scanning lidar under 500 USD

A scanning lidar puts one ranging head on a motor and spins it. One part, one cable, a full planar
point cloud with no tiling arithmetic. Three tables follow because a portrait page will not carry
thirteen columns.

### Scan geometry and rate

| Model | Scan Hz | Points/s | Ang. res. | Points/rev | Principle |
|---|---|---|---|---|---|
| RPLIDAR A1M8 (R5/R6) | 5.5 typ | 8000 | see conflict below | see conflict below | triangulation |
| RPLIDAR C1 | 10 typ (8-12) | 5000 | 0.72 deg | 500 | dTOF |
| RPLIDAR A2M12 | 10 (5-15) | 16 000 | 0.225 deg | 1600 | not stated |
| RPLIDAR S2 / S2E | 10 | 32 000 | 0.1125 deg | 3200 | not stated |
| LDROBOT LD06 | 10 typ (5-13) | 4500 | 1 deg | 450 | dTOF |
| LDROBOT LD19 | 10 | 4500 | <= 1 deg | 450 | dTOF |
| YDLIDAR X2 | 6 default | 3000 | 0.72 deg at 6 Hz | 500 | triangulation |
| YDLIDAR X4 PRO | 6-12 | 5000 | 0.43 deg at 6 Hz | 833 | triangulation |
| YDLIDAR G4 | 5-12 (max 16) | 9000 | 0.2 deg at 5 Hz | 1800 | triangulation |
| YDLIDAR T-mini Plus | 6 default (6-12) | 4000 | 0.54 deg | 666 | ToF |
| Benewake TF-Luna | not scanning | 1-250 Hz frame | single beam | 1 | ToF |
| Benewake TFmini-S | not scanning | not published | single beam | 1 | ToF |

**The two research lanes disagree about the RPLIDAR A1, and the disagreement matters.** The
`other-st-tof-and-lidar` lane says the current R5/R6 part is an 8 kHz unit, so at 5.5 Hz it produces
about **1450 points per revolution, 0.25 deg**, and cites DFRobot's own A1M8-R6 listing wording to
that effect. The `adafruit-tof-nonst` lane says the datasheet conditions its 1 deg figure on 5.5 Hz
and its 5.5 Hz figure on **360 samples per scan**, that 360 x 5.5 is 1980 and not 8000, and that the
1450 figure is therefore an unverified product of two specs measured under different conditions.
**Prefer the conservative reading: design to 1 deg / about 360 points per revolution.** Slamtec's
current spec page prints "Angular Resolution <= 1 deg" beside "Sampling Frequency 8K", which cannot
both be true of one part, and a perimeter design must not be sized on the optimistic half of a
contradiction. The C1 at 0.72 deg and 500 points/rev has no such ambiguity and is a better buy anyway.

### Range and accuracy, with the reflectance condition

| Model | Min | Max range | Condition | Low-reflectance range | Accuracy |
|---|---|---|---|---|---|
| RPLIDAR A1M8 | 0.15 m | 12 m (R5+); 6 m (R4) | "White objects" | **not published** | < 1 % of distance |
| RPLIDAR C1 | 0.05 m | 12 m | 70 % reflection | 6 m at 10 % | +/-30 mm |
| RPLIDAR A2M12 | 0.2 m | 12 m | **no condition on page** | not published | not captured |
| RPLIDAR S2 / S2E | 0.05 m | 30 m | 90 % | 10 m at 10 % | not captured |
| LDROBOT LD06 | 0.02 m | 12 m | 70 % reflectivity | not published | 30 mm typ, 45 mm max |
| LDROBOT LD19 | 0.02 m | 12 m | **no condition stated** | not published | 10 mm, 300-12000 mm |
| YDLIDAR X2 | 0.12 m | 8 m | 80 %, indoor | not published | 2 cm below 1 m |
| YDLIDAR X4 PRO | 0.12 m | 10 m | 80 %, indoor | not published | 2 cm below 1 m |
| YDLIDAR G4 | 0.12 m | 16 m | 80 %, at 4 kHz | not published | 2 cm below 1 m |
| YDLIDAR T-mini Plus | 0.05 m | 12 m | 80 % | **4 m at 10 %** | 20 mm, 0.05-12 m |
| Benewake TF-Luna | 0.2 m | 8 m | not published | not published | +/-6 cm, 0.2-3 m |
| Benewake TFmini-S | not published | 12 m | not published | not published | not published |

The LD19's `0.02-12 m` carries **no reflectivity condition at all** on the Waveshare wiki, while the
LD06 datasheet ties its identical 12 m to a **70 % target**. Assume the LD19 number is the same
70 %-class figure until LDROBOT says otherwise - that is inferred, not verified.

### Physical, power, interface, eye safety, price

| Model | Size (mm) | Mass | Power | Ambient | Class / price |
|---|---|---|---|---|---|
| RPLIDAR A1M8 | 96.8 x 70.3 x 55 kit | 170 g | ~2 W derived; 0.5 W on spec page | "no direct sunlight" | Class I; `$99.00` DFRobot, `$99.95` Adafruit |
| RPLIDAR C1 | not captured | 110 g | 230 mA at 5 V (~1.15 W), reseller | 40 000 lux | Class 1; `$69.00` DFRobot |
| RPLIDAR S2 / S2E | 18 mm optical band | not captured | not captured | 80 klux, IP65 | Class 1; **no USD price published** |
| LDROBOT LD06 | 38.6 x 38.6 x 33.3 | 42 g | 180 mA at 5 V, 0.9 W | 30 kLux | Class 1; **no price confirmable** |
| LDROBOT LD19 | 38.6 x 38.6 x 33.5 | not stated | 180 mA at 5 V, 0.9 W | 30 kLux | FDA Class 1; `$99.00` |
| Waveshare D500 | 38.6 x 38.6 x 33.5 | not stated | 290 mA, 1.45 W | not stated | Class 1; not read |
| YDLIDAR X2 | 60.5 dia x 50.3 x 96 | 126 g | 300 mA typ, 1000 mA start | **0-2000 lux** | Class I; not published |
| YDLIDAR T-mini Plus | 38.6 x 38.6 x 33.9 | not captured | 340 mA typ | 60 kLux | Class 1; not published |
| Benewake TF-Luna | 35 x 21.25 x 13.5 | < 5 g | <= 0.35 W | not published | not published; ~`$29.90` |
| Livox Mid-360 | not captured | 265 g | 6.5 W avg, 14 W heating | not captured | Class 1; not published |

**Interface and driver support.** A1M8, C1, LD06, LD19, D500 and every YDLIDAR unit here stream over
UART - 115200 (A1), 230400 (LD-class) or 460800 baud (C1). The Livox Mid-360 needs **100BASE-TX
Ethernet** and a host that can take it. **Driver maturity is not published in the sources read for any
unit in this table** - the wire protocols are documented, and community drivers are likely but
unverified. The one host-side feature that is datasheet-verified is the A1M8's self-protection: it
shuts the laser down on over-power, on an unstable or slow scan speed, or on a sensor fault, and the
host can query that health state over the same UART. The A1 also needs **two independent 5 V rails**,
one for the scanner and one for the motor, which is real BOM on a small chassis.

Two entries should change a decision on their own. **YDLIDAR X4 PRO's published service life is
1500 hours**, about 62 days of continuous running - a consumable, not a component. **YDLIDAR X2's own
datasheet lists a lighting environment of 0 to 2000 lux** - a triangulation scanner is not a sunlight
sensor. Avoid the whole triangulation group (A1M8, X2, X4 PRO, G4) for a robot that will ever see a
sunlit room, and avoid the A2 family's **0.2 m minimum range** on a 350 mm chassis whose skin is only
0.175 m from the centre.

The **Benewake TF-Luna and TFmini-S do not belong in this table as perimeter sensors** and are listed
only because the brief names them. Both are single-beam rangers with roughly a 2 deg cone. Their
honest role here is one cheap, long, low-power guard beam - a forward step detector or a beam on a
servo. Nothing about them helps with classification.

### Considered and set aside: Hokuyo, Unitree, the S3, and the one 3D unit

The brief names these, so each gets a line rather than a silent omission.

- **Hokuyo URG entry parts - not verified in this pass.** `hokuyo-aut.jp` returned PHP fatal errors
  instead of a page and the `hokuyo-usa.com` URG-04LX-UG01 path returned 404, so **no Hokuyo number is
  asserted here**. Two things can be said without inventing anything: the URG family is a **sector**
  scanner, not a full 360 deg one, and it is positioned a long way above the Chinese units on price.
  Confirm both against Hokuyo's own PDF before designing around it.
- **Unitree 4D LiDAR L1 / L2 - not verified.** `unitree.com/LIDAR` returned 404. No specification and
  no price is asserted.
- **Slamtec S3 - specs not captured in this pass.** It exists in the product line; nothing more is
  claimed here.
- **Livox Mid-360** is the only unit in this chapter that is not planar: **horizontal 360 deg with a
  vertical field of -7 deg to +52 deg**, 200 000 points/s on the first return, **40 m at 10 %
  reflectivity and 70 m at 80 %**, 0.1 m blind zone, angular precision below 0.15 deg. It genuinely
  sees the space above the robot. It costs 265 g, 6.5 W and an Ethernet host to do it, and its
  vertical field looks **up, not down**: mounted at 1000 mm, its lowest ray reaches the floor only at
  1000/tan(7 deg), about **8.1 m** out, so everything on the floor inside an 8 m radius is below the
  beam. That is the wrong blind spot for a cat.

## Part 3 - the honest comparison

### What a planar 360 deg lidar gives you that a ToF ring does not

1. **Angular density, by two orders of magnitude.** A C1 delivers 500 measurements per revolution with
   an angle attached to each. A 20-sensor VL53L4CX ring delivers 20 numbers. `coverage-geometry.md`
   owns the tiling arithmetic; the result it hands this chapter is that an 18 deg cone needs about
   20 units to close 360 deg edge to edge, and more with overlap margin.
2. **Cluster width, therefore the only non-camera classification feature that works.** Because returns
   carry angles, a scan segments into clusters with measurable chord width. Two clusters 80-160 mm
   wide and 150-400 mm apart moving together are a person's shins. A cat is one 60-120 mm cluster low
   down. A ToF ring produces one distance per cone and no width at all.
3. **Scan matching, hence a background map.** 450-500 points per revolution is enough for SLAM.
   Once a map exists, anything that does not fit it is dynamic, and dynamic is the strongest
   animate-versus-inanimate cue available without a camera or a thermal sensor. A ToF ring has far too
   few points to scan-match, so it can never build that model.
4. **Range against dark targets.** C1: **6 m at 10 % reflection**. T-mini Plus: **4 m at 10 %**. The
   best single-cone ST part, the VL53L4CX, gives **2.1 m against a grey 17 % target indoors** and
   1.1 m outdoors. A dTOF scanner sees a dark-trousered leg across a room; the ring sees it at arm's
   length.
5. **Ambient light.** Scanners quote 30 kLux (LD06/LD19), 40 kLux (C1), 60 kLux (T-mini Plus),
   80 klux (S2). ST's "outdoor overcast" condition is only about **5 kLux**, and the VL53L4CX drops
   from 5.0 m to 1.6 m on white and 2.1 m to 1.1 m on grey-17 % there.
6. **One wire.** One UART, against 20 I2C devices that all boot at the same address and need 20 XSHUT
   lines or an expander plus a power-sequencing state machine.

### What it fails at

1. **It sees exactly one plane, and the blindness does not shrink with distance.** A forward ToF cone
   narrows as you approach it. A planar lidar's blind region is a **half-space above and a half-space
   below, at every range**. A 300 mm standing cat is equally invisible at 0.3 m and at 8 m if the plane
   sits at 400 mm. The A1's scan field flatness is **+/-1.5 deg**, about +/-52 mm at 2 m - that does
   not help.
2. **No single plane works on this robot.** A 350 mm robot 600-1200 mm tall has a tall body to protect
   and a cat to avoid. A plane at 60-120 mm sees cat, floor clutter and ankles and misses every table
   top, counter overhang and leaning torso. A plane at 700-1000 mm sees torsos and worktops and misses
   the entire floor and every pet. Two planes means two lidars, two motors, and still no vertical
   continuity between them.
3. **It cannot separate a static pet from a static object at all.** Cluster width overlaps completely
   between a curled cat and a shoe. No temperature, no vertical extent, no micro-Doppler.
4. **Glass and mirrors.** Glass returns nothing or a ghost from the far side; a mirror produces a
   phantom room. The A1 datasheet publishes nothing on either - **not published**.
5. **It is a motor.** LD06 rated **10 000 h**, about 14 months continuous. YDLIDAR X4 PRO **1500 h**.
   A solid-state ToF ring has no wear-out mechanism.
6. **It needs an unobstructed optical window** at exactly its scan height, with no bracket or cable
   crossing it - a real industrial-design constraint on a 350 mm shell.

### The penalty, in numbers

| Quantity | Planar lidar | 20 x VL53L4CX ring | Penalty |
|---|---|---|---|
| Hardware cost | `$69` (C1) to `$99` (LD19) | 20 x `$14.95` = `$299` | lidar is **$230 cheaper** |
| Mass | 42 g (LD19-class), 110 g (C1), 170 g (A1) | ~20 g of breakouts | **+22 g to +150 g** |
| Power | 0.9 W (LD19), ~1.15 W (C1), ~2 W (A1) | 1.06 W continuous; ~0.2 W at 5 Hz duty | **+0 to +0.95 W** |
| Height intrusion | 33 mm body plus a 360 deg window | none | a slot in the shell |
| Moving parts | 1 motor, 1500-10 000 h rated | none | a wear item |
| Host compute | SLAM and clustering | trivial | a real CPU budget |

**Power is close to a wash** - that is the surprise. An LD19 at 0.9 W costs about the same as a
20-sensor ring run flat out. The real penalties are **mass, the motor, the optical window and the CPU
budget**. Cost runs the other way: the lidar is **three to four times cheaper** than a ring dense
enough to close the perimeter.

### Recommendation

- **Choose a planar dTOF lidar** when the robot needs to know where it is and what is around it -
  requirement (a), plus the static map that makes everything else tractable. Buy the **RPLIDAR C1
  (`$69`, dTOF, 0.05-12 m at 70 %, 6 m at 10 %, 0.72 deg, 40 klux, IP54, 110 g)** or the **LD19
  (`$99`, 0.02-12 m with no reflectivity condition published, 450 points/rev, 30 kLux, 0.9 W, 42 g
  class)**. Buy the LD19 rather than the LD06:
  no LD06 price was confirmable anywhere, and Inno-Maker's LD06 URL now sells an LD19P.
- **Choose the ToF ring** when the robot must see vertical extent - overhangs, table tops, a hand
  reaching in, a lying cat - or when a spinning part is unacceptable. A ring has no wear-out mechanism
  and no optical window requirement.
- **Use both, and this is the right answer for this robot.** Mount the lidar plane **low, 60-120 mm**,
  where it catches the cat, the floor clutter and human ankles. Cover what it misses with a second
  sensor that has vertical extent - a multizone ToF, a thermal array or mmWave - not with a second
  lidar. Within ST's single-cone family the **VL53L4CX (`$14.95`, 18 deg, 5.0 m white / 2.1 m grey-17 %
  indoors, 19 mA)** is the only part worth a perimeter position, with one or two **VL53L3CX** where
  depth-behind-the-obstacle earns its `$19.95`.
- **Neither option meets the classification requirement.** A planar lidar gives moving-versus-static
  and cluster width, which separates a walking human from a walking cat. It gives nothing for a
  sleeping cat against a backpack. That gap closes only with a sensor that measures something other
  than range: temperature, micro-motion or appearance.
