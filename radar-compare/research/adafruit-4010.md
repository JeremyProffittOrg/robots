# Adafruit 4010 — Slamtec RPLIDAR A1 (A1M8) 360° Laser Range Scanner

**Lane:** `adafruit-4010` — single-product deep dive
**Date of research:** 2026-09-12
**Adversarial spec check:** 2026-09-12 — hard numbers re-verified against the primary sources. The LD108 A1M8 datasheet rev 2.1 (Adafruit-hosted) and v2.2 were downloaded and their full text extracted and searched; the Adafruit 4010 page, the Slamtec `a1spec` parameter page, the Slamtec A1 product page and the DFRobot A1M8-R6 page were re-read. Range, "White objects", 360° angular range, $99.95, 19 in stock and $99.00 at DFRobot all held. Two claims were corrected: the 1450-points-per-revolution figure is **published**, not inferred, and the "70 % reflectivity" phrasing is **not** attributable to DFRobot. The "A1M8-R6" label is downgraded to inferred.
**Verdict in one line:** Adafruit 4010 is a 360° 2D spinning triangulation LiDAR. It is the single best "see every obstacle around me" sensor in this price class for a 350 mm robot, and it is **not** a human sensor, **not** a pet sensor, and **cannot** classify anything. Everything in categories (b), (c) and (d) of the brief has to be built in software on top of a 360-point range ring, and some of it cannot be built at all from one horizontal plane.

---

## 1. Product identification

Adafruit product ID 4010 is **"Slamtec RPLIDAR A1 - 360 Laser Range Scanner"**.

| Field | Value | Confidence |
| --- | --- | --- |
| Adafruit product ID | 4010 | vendor-page-verified |
| Adafruit title | Slamtec RPLIDAR A1 - 360 Laser Range Scanner | vendor-page-verified |
| Manufacturer | Shanghai Slamtec Co., Ltd. | datasheet-verified |
| Manufacturer model | A1M8 (development kit form) | datasheet-verified |
| Hardware revision shipped by Adafruit | Adafruit states only: "As of June 2, 2021" Slamtec revised the unit, "labeled A1M8", with PCB colour and enclosure changes. Adafruit does **not** print a revision suffix, and neither the Slamtec A1 product page nor the A1 parameter page mentions "R6" at all. The A1M8-R6 designation appears only on reseller pages (DFRobot). **Treat "R6" as inferred, not vendor-stated.** What matters for the range spec is only that the unit is A1M8-R5 **or later**, which the June 2021 revision date and the 12 m figure on Adafruit's own page both imply | vendor-page-verified for the June 2021 revision; **inferred** for "R6" |
| List price | **USD $99.95** (read 2026-09-12) | vendor-page-verified |
| Stock | **19 in stock** (read 2026-09-12). Actively stocked, **not** discontinued, **not** marked end-of-life by Adafruit or Slamtec | vendor-page-verified |
| Adafruit-hosted datasheet | [4010_datasheet.pdf](https://cdn-shop.adafruit.com/product-files/4010/4010_datasheet.pdf) — Slamtec LD108 rev. 2.1, dated 2018-02-05 | datasheet-verified |
| Newer Slamtec datasheet read | LD108 A1M8 **v2.2**, dated 2019-02-14 | datasheet-verified |
| Adafruit learn guide | [Using the Slamtec RPLIDAR on a Raspberry Pi](https://learn.adafruit.com/slamtec-rplidar-on-pi) by Dave Astels, last updated 2024-06-03 | vendor-page-verified |

**Important identification note.** The Adafruit part number 4010 is easy to confuse with the Vishay **VCNL4010** proximity sensor, which Adafruit sells as product **466**. They are unrelated. Product 4010 is the LiDAR.

**What is in the box.** The A1 development kit: the spinning scanner head, a small USB-to-serial adapter board that mates to the scanner, and a USB cable. The adapter board is described in the Adafruit guide as "functionally similar to an FTDI adapter, but does not have the same connections." The bare "batch version" sold to OEMs has no adapter board and uses PH1.25 connectors instead; Adafruit sells the development kit.

---

## 2. Measured specification — from the Slamtec datasheet, with conditions

All figures below are lifted from the Slamtec LD108 A1M8 datasheet (rev 2.1 hosted by Adafruit, cross-checked against rev 2.2). Where a condition is stated in the datasheet I have kept it verbatim. Where a condition is **not** stated I say so rather than guessing.

### 2.1 Measurement performance

| Item | Min | Typical | Max | Stated condition | Confidence |
| --- | --- | --- | --- | --- | --- |
| Distance range, A1M8-R4 **and earlier** | TBD | **0.15 – 6 m** | TBD | Comments column reads only **"White objects"** | datasheet-verified |
| Distance range, A1M8-R5 **and later** | — | **0.15 – 12 m** | — | Comments column reads only **"White objects"** | datasheet-verified |
| Angular range | n/a | 0 – 360° | n/a | — | datasheet-verified |
| Scan field flatness | −1.5° | — | +1.5° | The scan plane is not perfectly flat; it wobbles ±1.5° (rev 2.2 only) | datasheet-verified |
| Distance resolution | n/a | **< 0.5 mm** | n/a | **< 1.5 m** only | datasheet-verified |
| Distance resolution | n/a | **< 1 % of the distance** | n/a | All distance range | datasheet-verified |
| Angular resolution | n/a | **1°** | n/a | At 5.5 Hz scan rate | datasheet-verified |
| Sample duration | n/a | 0.125 ms | n/a | — | datasheet-verified |
| Sample frequency | n/a | **8000 Hz** | 8010 Hz | R1/R2 hardware is limited to 2000 Hz; R3/R4 need firmware ≥ 1.24 for 8 kHz | datasheet-verified |
| Scan rate | 1 Hz | **5.5 Hz** | 10 Hz | "Typical value is measured when RPLIDAR A1 takes 360 samples per scan" | datasheet-verified |
| Points per revolution | n/a | **1450** | n/a | Datasheet Introduction, verbatim: "RPLIDAR A1's scanning frequency reached 5.5 hz when sampling 1450 points each round." Requires 8 kHz sampling, so R5+ hardware, or R3/R4 on firmware ≥ 1.24. **Published figure, not arithmetic** | datasheet-verified |
| Points per revolution | n/a | **360** | n/a | The alternative published condition, from the Scan Rate row's Comments column — this is the condition behind the 1° angular-resolution spec | datasheet-verified |

**Note on Adafruit's "Distance Resolution: 0.2cm".** The Adafruit product page's technical-details list states "Distance Resolution: 0.2cm (If scan rate set as 5.5Hz, resolution is 0.2% of actual distance)". The Slamtec datasheet gives **< 0.5 mm below 1.5 m and < 1 % of the distance across the full range**. Where the two differ, use the datasheet. Adafruit's 0.2 % appears to be read off the datasheet's resolution trend graph (Figure 2-2) rather than from the specification table.

**The reflectivity condition is the weak point of this datasheet.** Slamtec states only the words "White objects" against the 12 m figure. It does **not** publish a reflectivity percentage, it does **not** publish a black-target or dark-target range, and it does **not** publish an ambient-light figure in lux. The phrase "white objects with 70 % reflectivity" circulates in third-party robotics copy, but **that number does not appear in the Slamtec A1M8 datasheets** (rev 2.1 and v2.2 full text searched 2026-09-12: zero hits for "70", "reflectivity" or "reflectance" in any specification row) **and it does not appear on Slamtec's own A1 parameter page either**. *Correction to an earlier draft of this file: it attributed the "70 % reflectivity" phrasing to DFRobot and Waveshare. The DFRobot A1M8-R6 page was re-read on 2026-09-12 and states no reflectivity condition of any kind — the attribution was wrong and has been withdrawn. The Waveshare page returned HTTP 403 and could not be re-checked, so no reseller is now named as the source.* Treat "70 %" as copy of unknown provenance, not as a datasheet figure.

**Dark-target range is therefore NOT PUBLISHED.** This matters enormously for the brief. A black cat, a dark jacket, a matte black robot bumper and a dark rug are all substantially harder returns than the white test board that produced the 12 m number. The physics is not in dispute — a triangulation LiDAR reading a 5 – 10 % reflectance surface at 785 nm gets roughly an order of magnitude less returned energy than from an 85 % white board — but Slamtec publishes no derated figure, so no honest number can be quoted here. Plan for it empirically, not from the datasheet.

**Ambient light.** The datasheet makes a qualitative claim only: *"The modulated laser can effectively prevent ambient light and sunlight during ranging scanning process. This make RPLIDAR A1 work excellent in all kinds of indoor environment and outdoor environment without sunlight."* Note the wording carefully — **"outdoor environment WITHOUT sunlight"**. Slamtec is explicitly not claiming direct-sunlight operation for the A1. No lux figure is published. For an indoor domestic robot this is a non-issue; near a sunlit patio door it is a real one.

### 2.2 Ranging accuracy (from the Slamtec web parameter page, not the datasheet)

The [Slamtec A1 parameter page](https://www.slamtec.com/en/lidar/a1spec) publishes an accuracy breakdown that the datasheet does not:

| Distance band | Stated accuracy | Confidence |
| --- | --- | --- |
| ≤ 3 m | 1 % of the range | vendor-page-verified |
| 3 – 5 m | 2 % of the range | vendor-page-verified |
| 5 – 25 m | 2.5 % of the range | vendor-page-verified |

That same page also states "Range Resolution: ≤ 1 % of the range (≤ 12 m), ≤ 2 % of the range (12 – 16 m)". The 12 – 25 m bands are clearly inherited from a shared Slamtec spec template and are meaningless for a unit whose maximum range is 12 m. Use the ≤ 3 m row: **1 % of range**, i.e. about ±10 mm at 1 m, ±30 mm at 3 m.

### 2.3 Optical and laser safety

| Item | Min | Typical | Max | Unit | Confidence |
| --- | --- | --- | --- | --- | --- |
| Laser wavelength | 775 | **785** | 795 | nm (infrared) | datasheet-verified |
| Laser power | TBD | **3** | 5 | mW peak power | datasheet-verified |
| Pulse length | TBD | 110 | 300 | µs | datasheet-verified |
| Laser safety class | **Class I** | | | Complies with 21 CFR 1040.10 and 1040.11 except for deviations per Laser Notice No. 50, dated 2007-06-24 | datasheet-verified |

The datasheet states explicitly that the short pulse duration "can make sure its safety to human and pet and reach Class I laser safety standard." For a robot that will operate around a cat at eye height, Class I with a 785 nm invisible beam is the right answer — there is no aversion response to an invisible beam, so Class I (eye-safe under all conditions of normal use) is the required rating, and the A1 has it.

The unit also carries self-protection: it shuts the laser down on excess transmit power, laser power-on failure, unstable or too-slow scan speed, or abnormal sensor behaviour, and the host can query that health state.

### 2.4 Electrical

| Item | Min | Typical | Max | Unit | Comment | Confidence |
| --- | --- | --- | --- | --- | --- | --- |
| Scanner system voltage | 4.9 | 5 | 5.5 | V | "If the voltage exceeds the max value, it may damage the core" | datasheet-verified |
| Scanner supply ripple | TBD | 20 | 50 | mV | "High ripple may cause the core working failure" | datasheet-verified |
| Scanner **start** current | TBD | 500 | **600** | mA | "Underpower may cause the startup failure" | datasheet-verified |
| Scanner run current | TBD | **300** | 350 | mA | Work mode, 5 V input | datasheet-verified |
| Scanner sleep current | TBD | 80 | 100 | mA | Sleep mode, 5 V input | datasheet-verified |
| Motor voltage | 5 | 5 | 10 | V | Adjust voltage according to speed | datasheet-verified |
| Motor current | TBD | 100 | TBD | mA | 5 V input | datasheet-verified |

**Total typical budget: ~400 mA at 5 V ≈ 2.0 W continuous, with a ~700 mA / 3.5 W inrush at start.** That is 20 – 40× the draw of a PIR or a single-zone ToF sensor and it is continuous — the motor never stops while you are scanning. On a battery robot this is a real budget line, not a rounding error.

Note a conflict in the field: Waveshare's A1 page lists "System Current: 100 mA, Power Consumption: 0.5 W". That figure cannot be reconciled with the Slamtec datasheet's 300 mA scanner plus 100 mA motor and appears to be a reseller transcription error. **Design to the datasheet: 2 W.**

Slamtec requires the scanner and the motor to be **powered separately** "in order to ensure data accuracy," with the scanner on a clean 4.9 – 5.5 V DC low-ripple rail (< 1 %) and the motor on a 5 – 10 V high-current rail. On a mobile robot sharing a rail with drive motors, this is the number-one cause of flaky scans. Give the scanner its own LDO or a well-decoupled buck output.

### 2.5 Interface

| Item | Value | Confidence |
| --- | --- | --- |
| Electrical interface | 3.3 V TTL UART | datasheet-verified |
| Baud rate | 115200 bps, 8N1 | datasheet-verified |
| Output high / low | 2.9 – 3.5 V / ≤ 0.4 V | datasheet-verified |
| Input high / low | 1.6 – 3.5 V / −0.3 – 0.4 V | datasheet-verified |
| RX note | "the RX input signal of A1M8 is recognized by the current… the actual control node voltage of this pin will not be lower than 1.6 V" | datasheet-verified |
| Motor control | `MOTOCTL` pin, 0 – 5 V PWM enable signal. On the A1 via USB adapter, the driver asserts **DTR** to spin the motor (unlike A2/A3 which use PWM) | datasheet-verified + community-verified |
| Dev-kit connector | PH2.54-7P, 7-pin | datasheet-verified |
| USB | Included USB-to-serial adapter board; enumerates as a USB serial port (`/dev/ttyUSB0` on Linux) | vendor-page-verified |

### 2.6 Mechanical and environmental

| Item | Value | Source | Confidence |
| --- | --- | --- | --- |
| Weight | 170 g | datasheet Fig 2-9 and Adafruit | datasheet-verified |
| Dimensions | 96.8 × 70.3 × 55 mm | Slamtec parameter page | vendor-page-verified |
| Dimensions (as listed by Adafruit) | 98.5 mm width × 60 mm height | Adafruit product page | vendor-page-verified |
| Operating temperature | 0 – 45 °C (datasheet); Slamtec parameter page says 0 – 40 °C | both | datasheet-verified / conflicting |
| Rotor bearing tech | OPTMAG optical-magnetic coupling instead of a slip ring, for longer service life | Slamtec product page | vendor-page-verified |
| MTBF / service life hours | **Not published** for the A1. Slamtec publishes lifetime figures for higher models but not for the A1M8 in either datasheet read | — | not published |

---

## 3. What the sensor actually outputs

Per the datasheet, each sample point carries four fields:

| Field | Unit | Meaning |
| --- | --- | --- |
| `Distance` | mm | Distance from the **rotating core** of the A1 to the sampled point |
| `Heading` | degree | Heading angle of that measurement |
| `Quality` | level | Quality of the measurement (signal strength proxy) |
| `Start Flag` | boolean | Flag marking the beginning of a new revolution |

That is the whole output. **A stream of (angle, distance, quality) triples and a revolution marker.** There is no object, no track, no velocity, no classification, no presence flag. Everything else is your software.

A critical subtlety from the Adafruit guide: *"a single revolution is not guaranteed to give a reading for each possible angle, but over several rotations a full scan can be assembled."* You will get dropouts at individual angles — from dark surfaces, from grazing angles, from specular reflections — and the returned scan is sparse and irregular, not a clean 360-element array. Angles arrive as floats, not integers.

At 8000 samples/s and 5.5 Hz you get roughly 1450 points per revolution (≈ 0.25° spacing) if the firmware supports 8 kHz. **This is a published Slamtec figure, not an inference.** The Introduction of the LD108 A1M8 datasheet (rev 2.1 and v2.2, identical wording) states verbatim: *"RPLIDAR A1's scanning frequency reached 5.5 hz when sampling 1450 points each round. And it can be configured up to 10 hz maximum."* The datasheet's separate "1° angular resolution" figure is a different, more conservative published condition — the Scan Rate row's Comments column reads *"Typical value is measured when RPLIDAR A1 takes 360 samples per scan."* So Slamtec publishes **both** conditions: 360 points/rev at the 1° spec row and 1450 points/rev at 5.5 Hz in the Introduction. The 8 kHz sampling condition is itself gated by hardware revision — the datasheet states *"R1 and R2 models only support the radar 2k times per second ranging frequency. R3 and R4 models need to update the firmware to 1.24 to support 8k times per second ranging frequency."* Plan for 1° and be pleased if you get better.

---

## 4. Software and library maturity

### 4.1 Adafruit's own library — `adafruit_rplidar`

Install per the Adafruit guide:

```
pip install adafruit-circuitpython-rplidar
```

API ([docs](https://docs.circuitpython.org/projects/rplidar/en/latest/), [source](https://github.com/adafruit/Adafruit_CircuitPython_RPLIDAR)):

```python
RPLidar(motor_pin: DigitalInOut, port: UART, baudrate: int = 115200,
        timeout: float = 1, logging: bool = False)
```

| Member | Behaviour |
| --- | --- |
| `.info` | dict with `model`, `firmware` (tuple), `hardware`, `serialnumber` |
| `.health` | `(status, error_code)` where status is `'Good'`, `'Warning'` or `'Error'` |
| `.connect()` / `.disconnect()` / `.reset()` | session control |
| `.start_motor()` / `.stop_motor()` / `.set_pwm(pwm)` | motor control. `DEFAULT_MOTOR_PWM = 660`, `MAX_MOTOR_PWM = 1023` |
| `.start(scan_type=0)` | 0 = normal, 1 = force, 2 = express |
| `.stop()` | halt scanning and disable the laser |
| `.iter_measurements(max_buf_meas=500, scan_type=0)` | yields `(new_scan: bool, quality: int|None, angle: float, distance: float)` |
| `.iter_scans(max_buf_meas=500, min_len=5)` | yields **lists** of `(quality, angle, distance)`, one list per assembled revolution. Starts the motor and the scan for you |
| `RPLidarException` | the one exception class |

**Maturity assessment: adequate, not strong.** It is a thin wrapper Adafruit adopted from the Skoltech `rplidar` library (the guide says so outright: "the Skoltech library provides a convenient wrapper"). It works, it is MIT-licensed, and it is maintained enough to still be linked from a guide edited in 2024. But note the caveat in the module's own docstring: **"The Current Version does NOT support CircuitPython. Future versions will."** Despite the package name, this is a CPython/Blinka library that talks to `/dev/ttyUSB0`. Do not plan to run it on a SAMD or an RP2040 through the CircuitPython name alone — the 2019 guide promised a CircuitPython port "in the near future" and as of the 2024 edit it has not landed.

Minimal working loop, straight from the Adafruit guide:

```python
from adafruit_rplidar import RPLidar
lidar = RPLidar(None, '/dev/ttyUSB0')
scan_data = [0]*360
for scan in lidar.iter_scans():
    for (_, angle, distance) in scan:
        scan_data[min([359, floor(angle)])] = distance
    process_data(scan_data)
```

The guide adds a real operational warning about `process_data`: *"The only requirement is that it be as fast as possible. If it takes too long to process a scan, data from the RPLIDAR will eventually be dropped."* The A1 streams at line rate with no flow control; a slow consumer silently loses scans. Budget your perimeter logic to finish well inside 180 ms.

### 4.2 The stronger software path

For anything beyond a demo, use the vendor stack:

- **[Slamtec/rplidar_sdk](https://github.com/Slamtec/rplidar_sdk)** — official C++ SDK, x86 Windows, x86 Linux, ARM Linux. Since SDK 1.6.0 it exposes `getAllSupportedScanModes()`.
- **[Slamtec/rplidar_ros](https://github.com/Slamtec/rplidar_ros)** (ROS 1) and **`sllidar_ros2`** (ROS 2) — publish `sensor_msgs/LaserScan`, which immediately unlocks the whole ROS navigation and perception ecosystem: `slam_toolbox`, `cartographer`, `nav2` costmaps, and the leg-detection packages discussed below.

This is the A1's real advantage over every other sensor in this comparison. It is not that the hardware is special; it is that the output format is `LaserScan`, and twenty years of open-source robotics perception already consumes `LaserScan`.

### 4.3 Known field problems

From Adafruit forum threads and community reports:

- **The bundled USB adapter is the most common failure item.** Multiple threads describe the motor spinning normally while no data arrives and the adapter's green LED never lights — the scanner is fine, the adapter is dead. Adafruit replaces these on request.
- **Missing cable in the box** has been reported more than once; the adapter pinout is documented on page 13 of the Slamtec PDF.
- **USB-serial enumeration** fails on some SBCs (reported on Jetson Xavier) where the CP-class USB-UART driver is not built into the kernel.
- **Under-volting at startup** produces the classic symptom of a motor that spins but a scanner that never delivers a health `Good` — the 600 mA start current is not optional.

---

## 5. Geometry on a 350 mm robot — the numbers that actually decide this

The A1 is a **single horizontal plane** sensor. Every performance question for this robot reduces to two geometric facts: where you put the plane, and how coarsely the plane is sampled.

### 5.1 Mounting

A 350 mm square or round chassis, 600 – 1200 mm tall, has ample room for a 97 × 70 × 55 mm, 170 g puck. But **this is not a perimeter sensor you distribute** — it is one sensor you centre. Mount it on the **rotational centre axis** of the robot, on the top deck or on a mast, with a clear 360° optical window and no mast, handle, cable or antenna intruding on the plane. Any structure in the plane creates a permanent dead sector that you must mask in software, and 170 g on a mast raises the centre of gravity on a narrow base.

Because the chassis is 350 mm across, the sensor's 150 mm minimum range sits **inside or barely outside the body**. Centre-mounted, the 175 mm body half-width already exceeds the 150 mm blind radius, so the blind zone is fully hidden inside the robot footprint — which is the ideal arrangement, but it also means the sensor provides **zero coverage from the skin of the robot outwards for 0 mm** in the best case. The corollary is unforgiving: anything that gets under or against the chassis was never seen. You still need bumpers and cliff sensors.

### 5.2 Scan-plane thickness (from the ±1.5° flatness spec)

`tan(1.5°) = 0.0262`. The plane is a wedge, not a sheet:

| Distance | Plane half-thickness | Total plane thickness |
| --- | --- | --- |
| 0.5 m | ±13 mm | 26 mm |
| 1 m (3.3 ft) | ±26 mm | 52 mm |
| 1.5 m (5 ft) | ±39 mm | 79 mm |
| 2.4 m (8 ft) | ±64 mm | 128 mm |
| 3.0 m (10 ft) | ±79 mm | 157 mm |

*Calculated from the datasheet flatness figure — arithmetic, not a published table.* This cuts both ways: a thicker plane far away means a short target is slightly more likely to be caught, but it also means the sensor may clip a floor or a ceiling it was nominally aimed past.

### 5.3 Angular sampling versus target width

Arc spacing at 1° is `d × 0.01745`:

| Distance | Arc per 1° | Returns across a 120 mm human shin | Returns across a 120 mm cat torso |
| --- | --- | --- | --- |
| 0.30 m (1 ft) | 5 mm | ~23 | ~23 |
| 0.91 m (3 ft) | 16 mm | ~8 | ~8 |
| 1.52 m (5 ft) | 27 mm | ~5 | ~5 |
| 2.44 m (8 ft) | 43 mm | ~3 | ~3 |
| 3.05 m (10 ft) | 53 mm | ~2 | ~2 |
| 6.0 m | 105 mm | ~1 | ~1 |

*Arithmetic from the 1° datasheet figure. If your unit runs 8 kHz sampling at 5.5 Hz the real spacing is nearer 0.25° and every count above roughly quadruples. The 1450-points-per-round figure behind that 0.25° is published by Slamtec in the datasheet Introduction (not inferred); the 8 kHz precondition requires R3/R4 hardware on firmware ≥ 1.24, or R5 and later. Verify on your own unit with `iter_measurements` before relying on it.*

This is the single most important table in this document. **At 10 ft a cat and a human leg are both roughly two points.** Two points is enough to say "something is there." It is nowhere near enough to say "that is a cat."

---

## 6. Answering the brief directly

### (a) Can it detect any obstacle it could collide with?

**Yes — within the plane, and only within the plane.** This is what the sensor is for and it does it very well: 360°, 5.5 – 10 Hz, millimetre-resolution range on every surface that returns 785 nm light.

What it will **miss**, categorically:

- Anything **below** the plane — a doorstep, a shoe, a power strip, a sleeping cat if the plane is high.
- Anything **above** the plane — a table top, a countertop overhang, an open drawer, an outstretched arm.
- **Glass, mirrors, polished metal, still water.** A glass door returns almost nothing at normal incidence and returns a phantom object at the mirrored distance off-axis. This is the classic domestic-robot failure and the A1 has no defence against it.
- **Matte black and dark-fabric surfaces at range.** Range against these is not published; expect a large derating and expect dropouts rather than wrong ranges.
- **Thin objects** — chair legs at range, cable runs, table pedestal spokes — which may fall between 1° samples entirely at 3 m and beyond.
- **Descending edges (stairs).** A horizontal plane cannot see a hole.

### (b) Can it detect a human?

**It can detect that a human-sized object is present. It cannot detect that it is a human.** It returns range, not identity.

Whether the return is usable depends entirely on the mounting height:

| Plane height above floor | What a standing adult presents | Usable? |
| --- | --- | --- |
| ~200 mm | Two separate ankle/shin clusters, ~80 – 120 mm each | Yes — best for leg-pair detection |
| ~400 mm (knee) | Two shin/knee clusters, wider | Yes — the classic "knee-high 2D LiDAR" configuration in the people-tracking literature |
| ~700 mm | One merged hip/thigh cluster | Yes, but the two-leg signature is lost |
| ~1000 – 1200 mm | One torso cluster, ~300 – 450 mm wide | Yes, large and easy to see — but pets are now completely invisible |

### (c) Can it detect a pet?

**Only if the scan plane is low enough to intersect the animal, and only when the animal's body is in that plane.**

A cat stands roughly 200 – 250 mm at the shoulder; a small dog 250 – 500 mm. A scan plane at 200 mm intersects both while they are standing. But:

- A **lying or sleeping** cat has a body profile of roughly 100 – 150 mm. A 200 mm plane passes clean over it. This is a severe, silent failure mode for a domestic robot.
- A **black cat** is the worst-case optical target for a 785 nm triangulation LiDAR. No derated range is published. Assume degraded detection and dropouts.
- A cat's **tail and legs** are thin enough to be missed between samples entirely.

And there is a direct conflict: the plane height that sees a standing cat (200 mm) is a poor height for detecting a **seated** human (whose legs at 200 mm are still there, fine) but is a terrible height for detecting an **overhanging** obstacle. One plane cannot serve every height.

### (d) Can it distinguish human vs pet vs inanimate object?

**Not natively. Not in a single frame. Not reliably at all from one horizontal plane.**

The sensor emits no feature that carries identity. The published literature on 2D-LiDAR person detection is unanimous on this point: *"the lack of identifying information in 2D range data is a drawback, causing modern LiDAR-based leg detectors to typically fail when applying traditional clustering techniques with geometric properties."* The standard ROS `leg_detector` applies geometric features to leg-sized clusters with a random-forest classifier, then associates and tracks the pairs with a Kalman filter. Modern work (`DR-SPAAM`, `PeTra`, FROG dataset) uses learned models on the raw range data and does noticeably better than the geometric baseline — but all of it is inference over time, and all of it is written for a knee-high plane on a moving robot in a cluttered room with known false-positive rates.

A chair leg and a cat leg at 3 m are the same two points. A coat stand and a standing person, in one frame, are the same cluster. The only separators available to you are **motion over time** and **cluster geometry**, and both degrade with range exactly as the sampling table above shows.

### (e) Static human?

**A static human is indistinguishable from furniture.** The A1 measures geometry, not life. There is no micro-motion channel, no respiration signal, no thermal signature. A person standing still at 3 m is a cluster of two points that does not move — which is precisely the description of a table leg. This is the single sharpest limitation of the A1 versus a 60 GHz mmWave presence radar or a thermal IR array.

If your requirement literally includes "detect a motionless human in the room," **the A1 cannot meet it and no amount of software will make it.** Pair it with a presence radar or a thermal array for that channel.

### (f) Range answers at 1, 3, 5, 8, 10 ft

All distances comfortably inside the A1's 0.15 – 12 m envelope. The limit is not range; it is angular sampling and target reflectance.

| Distance | Human (standing, plane at knee height) | Pet (standing cat, plane at 200 mm) | Static human | Classification |
| --- | --- | --- | --- | --- |
| 1 ft (0.30 m) | Detected — but **0.30 m is only 2× the 0.15 m blind radius**, and centre-mounted on a 350 mm chassis a target 1 ft from the skin is ~0.48 m from the sensor. Dense, ~23 pts per leg | Detected, dense | Detected as an object; not identified | Plausible from cluster shape + motion |
| 3 ft (0.91 m) | Detected, ~8 pts per leg. Good leg-pair signature | Detected, ~8 pts on torso | Object only | Plausible with a trained detector |
| 5 ft (1.52 m) | Detected, ~5 pts per leg | Detected, ~5 pts. Marginal for shape | Object only | Weak — motion required |
| 8 ft (2.44 m) | Detected, ~3 pts per leg. Leg-pair separation becomes unreliable | Detected, ~3 pts. Easily confused with a chair leg | Object only | Unreliable |
| 10 ft (3.05 m) | Detected, ~2 pts per leg | Detected, ~2 pts, **if** reflectance allows. Dark fur may drop out entirely | Object only | Not achievable |

**Summary of ranges by target:**

- Any surface, white: 0.15 – 12 m (0.15 – 6 m on A1M8-R4 and earlier hardware).
- Any surface, dark/matte: **not published**. Derate substantially; verify empirically.
- Moving human, as a *tracked* entity with motion-based confirmation: reliable to roughly 4 – 5 m indoors, degrading past that. *Inferred from the sampling geometry and the published people-tracking literature, not a vendor figure.*
- Standing cat, as a *classified* entity: realistically ≤ 2 m, and only with a low plane. *Inferred.*
- Static human, as a human: **never**.

---

## 7. Post-processing required to turn the output into a perimeter decision

You get `(quality, angle, distance)` triples. To get to "stop, slow, or steer," you need roughly this pipeline. None of it ships with the sensor.

1. **Ingest and de-skew.** Consume `iter_scans()` (or `LaserScan` from the ROS driver) fast enough to avoid drops. One revolution at 5.5 Hz takes **182 ms**; a robot at 0.5 m/s moves **91 mm** during one revolution, so each scan is motion-skewed. Compensate with odometry before treating the points as simultaneous, or accept ~90 mm of angular smear.
2. **Mask static dead sectors** created by the robot's own mast, handle, or antenna, and drop returns inside the chassis radius.
3. **Filter by quality.** Reject low-quality returns rather than believing them. This is your main defence against specular ghosts.
4. **Cluster.** Adaptive-breakpoint or DBSCAN segmentation into candidate objects, with a distance-dependent breakpoint threshold (because arc spacing grows with range — see the sampling table).
5. **Extract features per cluster** — width, depth, curvature, number of points, mean range, linearity. These are what the classical `leg_detector` random forest consumes.
6. **Track over time** with a constant-velocity Kalman filter and multiple-hypothesis or nearest-neighbour data association, so you have velocity per cluster. **Velocity is the only strong life-versus-furniture cue you have.** Furniture has zero velocity in the world frame once odometry is compensated.
7. **Classify.** Leg-pair geometry for humans; small low-lying moving cluster for pets; everything stationary and non-leg-shaped as inanimate. Accept that a static human falls into the inanimate bucket and design the safety behaviour accordingly — treat every unclassified cluster as potentially a person.
8. **Build a polar safety envelope.** Define stop/slow radii per sector, project the robot's footprint forward along the planned path, and raise the decision from the minimum range in the swept corridor rather than from the global minimum.
9. **Fuse.** Add bumpers for the sub-plane blind zone, cliff sensors for descending edges, and — if static-human or static-pet presence is a genuine requirement — a 60 GHz presence radar or a thermal IR array as an independent channel.

Realistically, steps 4 – 7 are a multi-week software project, or a decision to adopt ROS 2 and take `nav2` plus an off-the-shelf person detector. Budget for that, not for the $99.95.

---

## 8. Strengths and weaknesses

**Strengths**

- True 360° coverage from one device, one cable, one 5 V rail. No blind sectors to stitch, no multi-sensor synchronisation, no I²C address juggling.
- Millimetre-class ranging: < 0.5 mm resolution under 1.5 m, 1 % of range accuracy to 3 m.
- Detects **any** surface, not just warm or moving ones — the only technology in this comparison that reliably sees a cardboard box, a wall, a chair leg and a closed door.
- Class I eye-safe at 785 nm, explicitly rated safe for humans and pets by the manufacturer.
- Mature, ubiquitous software: official C++ SDK, ROS 1 and ROS 2 drivers, `sensor_msgs/LaserScan` output, and the entire open-source SLAM and navigation ecosystem downstream of it.
- Cheap for what it is. $99.95 for a 12 m 360° scanner.
- Actively stocked at Adafruit as of 2026-09-12 (19 units), with a current hardware revision.

**Weaknesses**

- **One plane only.** Blind above and below. This is not a limitation you can engineer around within the product.
- **No identity channel whatsoever.** Cannot distinguish human, pet, or object without substantial software, and cannot distinguish a static human from furniture at all.
- **2 W continuous and a moving part.** Ball-bearing spinning assembly, always rotating, audible whine, no published MTBF.
- **Dark-target performance is not published**, and matte black is the worst case. A black cat is the specific target this brief cares about and the specific target the sensor is worst at.
- **Glass and mirrors** produce dropouts and phantoms.
- **Not rated for direct sunlight** — the datasheet claims only "outdoor environment without sunlight."
- **Low update rate.** 5.5 Hz default means 182 ms per scan and ~90 mm of motion smear at 0.5 m/s.
- **Bundled USB adapter is the field-reported weak link.**
- **Multiple A1s in the same room can interfere.** Slamtec publishes no crosstalk specification and no multi-unit coordination mechanism for the A1. If two of these robots meet, expect spurious returns. *Inferred from the general multi-LiDAR crosstalk literature plus the absence of any published mitigation for the A1 — not a vendor statement.*
- **Physical size and mass** — 97 × 70 × 55 mm and 170 g on a 350 mm chassis, and it must be at the rotational centre with a clear optical window, which constrains everything else on the top deck.

---

## 9. Recommendation for this robot

**Buy it, and buy it as the obstacle layer — not as the presence layer.**

On a 350 mm robot, the RPLIDAR A1 mounted at the rotational centre at **knee height, roughly 350 – 450 mm above the floor**, is the correct primary obstacle sensor. That height gives the best compromise: it captures the human leg-pair signature the people-tracking literature is written around, it still intersects a standing small dog and the upper body of a standing cat, and it sits below most table tops so it sees table legs rather than nothing.

That mounting choice explicitly sacrifices the sleeping-cat case and the overhanging-obstacle case. Those must be covered by other sensors. Concretely, the A1 should be one of three layers:

1. **RPLIDAR A1** — 360° obstacle geometry, mapping, navigation, moving-human and moving-pet tracking. $99.95.
2. **A presence channel** — 60 GHz mmWave presence radar or a thermal IR array — to cover the static human and the sleeping pet, which the A1 structurally cannot do.
3. **Contact and cliff** — bumpers and downward ToF/IR — to cover the sub-plane blind zone and descending edges.

If the budget or the deck space only permits one sensor and the primary requirement is **"do not collide with anything,"** the A1 is the right single choice and nothing else in this price class is close. If the primary requirement is **"know whether a person or a cat is in the room,"** the A1 is the wrong single choice, and a 60 GHz presence radar or a thermal array should be the anchor instead.

---

## 10. Sources read

- [Adafruit product 4010 — Slamtec RPLIDAR A1 - 360 Laser Range Scanner](https://www.adafruit.com/product/4010) — price $99.95, 19 in stock, read 2026-09-12
- [Slamtec LD108 RPLIDAR A1M8 datasheet, rev 2.1 (2018-02-05), hosted by Adafruit](https://cdn-shop.adafruit.com/product-files/4010/4010_datasheet.pdf) — full text extracted
- [Slamtec LD108 RPLIDAR A1M8 datasheet, v2.2 (2019-02-14)](http://bucket.download.slamtec.com/b90ae0a89feba3756bc5aaa0654c296dc76ba3ff/LD108_SLAMTEC_rplidar_datasheet_A1M8_v2.2_en.pdf) — full text extracted; adds the Scan Field Flatness spec
- [Adafruit Learning System — Using the Slamtec RPLIDAR on a Raspberry Pi](https://learn.adafruit.com/slamtec-rplidar-on-pi) (PDF export, last updated 2024-06-03) — full text extracted
- [Adafruit CircuitPython RPLIDAR API documentation](https://docs.circuitpython.org/projects/rplidar/en/latest/)
- [adafruit/Adafruit_CircuitPython_RPLIDAR source](https://github.com/adafruit/Adafruit_CircuitPython_RPLIDAR)
- [Slamtec RPLIDAR A1 parameter page](https://www.slamtec.com/en/lidar/a1spec) — accuracy bands, dimensions, temperature
- [Slamtec RPLIDAR A1 product page](https://www.slamtec.com/en/lidar/a1) — scan-mode options, OPTMAG
- [DFRobot RPLIDAR A1M8-R6 product page](https://www.dfrobot.com/product-1125.html) — confirms a product sold as "RPLIDAR A1M8-R6 — 360 Degree LiDAR Laser Range Scanner (12m)" at $99.00, range "0.15 - 12m". Re-read 2026-09-12: this page states **no** reflectivity condition. It is not the source of the "70 % reflectivity" phrasing
- [Slamtec/rplidar_sdk](https://github.com/Slamtec/rplidar_sdk) and [Slamtec/rplidar_ros](https://github.com/Slamtec/rplidar_ros)
- [rplidar_ros on ROS Index](https://index.ros.org/p/rplidar_ros/)
- Adafruit forum threads on the A1: [missing cable](https://forums.adafruit.com/viewtopic.php?f=22&t=190482), [lidar not transmitting data](https://forums.adafruit.com/viewtopic.php?t=199483), [power requirements](https://forums.adafruit.com/viewtopic.php?t=143492), [not functional](https://forums.adafruit.com/viewtopic.php?t=159480)
- [Deep Person Detection in 2D Range Data (arXiv 1804.02463)](https://arxiv.org/pdf/1804.02463)
- [2D vs. 3D LiDAR-based Person Detection on Mobile Robots (arXiv 2106.11239)](https://arxiv.org/pdf/2106.11239)
- [FROG: A new people detection dataset for knee-high 2D range finders (arXiv 2306.08531)](https://arxiv.org/pdf/2306.08531)
- [Person Tracking and Following with 2D Laser Scanners (Leigh et al., ICRA 2015)](https://www.cs.mcgill.ca/~jpineau/files/leigh-icra15.pdf)
- [Mitigation of crosstalk effects in multi-LiDAR configurations (SPIE 2018)](https://www.marcus-hebel.de/spie18_diehm_hammer_hebel_arens.pdf)
