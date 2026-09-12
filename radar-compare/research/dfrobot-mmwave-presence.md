# DFRobot mmWave Radar Human Presence / Motion Sensors

Lane: `dfrobot-mmwave-presence`
Research date: **2026-09-12**. All prices are DFRobot list price in USD read from `dfrobot.com` on that date.
Target application: a 350 mm square/round mobile robot, 600–1200 mm tall, needing 360-degree obstacle,
human, and pet detection with human/pet/object discrimination.

---

## 1. Scope and method

I walked the DFRobot catalogue search endpoints `https://www.dfrobot.com/search-mmwave.html` and
`https://www.dfrobot.com/search-mmwave%20radar.html`, then fetched each product page, each
`wiki.dfrobot.com` page, each alternate wiki mirror (`wiki.dfrobot.com/SKU_...`), the DFRobot Arduino
library READMEs on GitHub (which are the only place the command parameter ranges are published), and
the ESPHome component documentation for SEN0395.

**Catalogue completeness note.** The DFRobot `search-mmwave` endpoint returns **11 results total**, on a
single page. There is no second page. Two SKUs named in the lane brief do not exist in the DFRobot
catalogue:

- **SEN0611** — no such DFRobot radar product. Searches resolve only to SEN0609/SEN0610. Treat the
  SKU as a transcription error for SEN0609/SEN0610.
- **MR24HPC1 / MR60BHA1 / MR60FDA1** — these are **Seeed Studio** modules, not DFRobot products.
  DFRobot's site mentions them only in community maker-log posts
  (`community.dfrobot.com/makelog-313708.html`) and a comparison blog
  (`dfrobot.com/blog-13927.html`). DFRobot does not sell a board based on any of them. They belong
  to a Seeed lane, not this one.

There is no "mmWave Radar - Human Presence Detection" Gravity board other than **SEN0610**.

---

## 2. Full DFRobot radar catalogue as of 2026-09-12

| SKU | Product name | Band | Price (USD) | Stock | Presence sensor? |
|---|---|---|---|---|---|
| SEN0395 | mmWave Radar - 24GHz Human Presence Detection Sensor (9 Meters) | 24 GHz | $29.00 | In stock | Yes |
| SEN0609 | mmWave - C4001 24GHz Human Presence Detection Sensor (25 m, UART) | 24 GHz | $13.90 | In stock | Yes |
| SEN0610 | Gravity: mmWave C4001 24GHz Human Presence Detection Sensor (12 m, I2C & UART) | 24 GHz | $12.90 | In stock | Yes |
| SEN0691 | Fermion: C4002 mmWave Human Presence Sensor (10 m) | 24–24.25 GHz | $8.90 | In stock | Yes |
| SEN0623 | C1001 60GHz mmWave Indoor Fall Detection Sensor (11 m) | 61–61.5 GHz | $29.00 | In stock | Yes |
| SEN0557 | mmWave - 24GHz Human Presence Sensing Module (6 Meters) | 24–24.25 GHz | $9.90 | In stock | Yes |
| SEN0306 | mmwave - 24GHz Microwave Radar Distance Sensor (20 Meters) | 24 GHz K-band | $65.90 | In stock | No — ranging only |
| SEN0676 | mmWave - 80GHz Liquid Level Detection Sensor (40 Meters, UART) | 80 GHz | $59.00 | In stock | No — liquid level |
| SEN0192 | Gravity: Digital 10.525GHz Microwave Sensor (Motion Detection) | 10.525 GHz | $8.90 | In stock | Doppler motion only |
| SEN0521 | 5.8GHz Microwave Radar Module (Discontinued) | 5.8 GHz | listed $0.00 | **DISCONTINUED** | Doppler motion only |
| KIT0216-EN | UNIHIKER K10 AIoT Starter Kit | n/a | $89.00 | In stock | Kit, contains no radar |

Volume pricing (all tiers re-read from the product pages on 2026-09-12):

| SKU | 1+ | 3+ | 5+ | 10+ |
|---|---|---|---|---|
| SEN0691 | $8.90 | $8.70 | $8.60 | $8.30 |
| SEN0557 | $9.90 | $9.70 | $9.50 | $9.20 |
| SEN0609 | $13.90 | $13.60 | $13.30 | $12.90 |
| SEN0610 | $12.90 | $12.70 | $12.40 | $11.90 |
| SEN0395 | $29.00 | — | — | — |
| SEN0623 | $29.00 | — | — | — |

SEN0395 and SEN0623 publish no volume tiers. This matters for a 360-degree ring, which needs 3–4 units.

---

## 3. Per-sensor datasheet extracts

### 3.1 SEN0395 — 24 GHz human presence, 9 m (`$29.00`)

Sources: [product page](https://www.dfrobot.com/product-2282.html),
[wiki](https://wiki.dfrobot.com/mmwave_radar_human_presence_detection_sku_sen0395),
[API/protocol reference](https://wiki.dfrobot.com/sen0395/docs/21398),
[ESPHome component](https://esphome.io/components/dfrobot_sen0395/).

| Parameter | Published value | Condition |
|---|---|---|
| Operating frequency | 24 GHz | — |
| Modulation | FMCW, CW | — |
| Equivalent transmit power | 9–12 dBm | — |
| Detection distance | 9 m | condition **not published** (no target RCS, no reflectivity, no clutter statement) |
| Moving vs stationary range | **not published separately** — one figure covers both | — |
| Beam angle | 100° × 40° (width × height) | quoted on both product page and wiki |
| Range quantisation | 15 cm per index, indices 0–127 | from `detRangeCfg` grammar |
| Supply | 3.6–5 V | — |
| Operating current | 90 mA | steady-state figure; peak not published |
| UART | 115200 baud, 8N1, no flow control | — |
| Output | GPIO2 high = present, low = absent; plus serial | no pull-down resistor needed |
| Operating temperature | −40 to +85 °C | — |
| Dimensions | 24 × 28 mm | — |

**Output type.** Boolean presence on GPIO plus a serial `$JYBSS` presence frame. **It does not output
distance, target coordinates, speed, or energy.** This is the single most important limitation for a
robot: SEN0395 answers "is something alive-ish in the configured zone" and nothing else.

**Command set** (`wiki.dfrobot.com/sen0395/docs/21398`, verbatim grammar):

| Command | Syntax | Range / units |
|---|---|---|
| `detRangeCfg` | `detRangeCfg par1 parA_s parA_e [parB_s parB_e] [parC_s parC_e] [parD_s parD_e]` | `par1` always `-1`; segment indices 0–127, each index = 15 cm; up to four segments. **Correction (2026-09-12):** the grammar's index ceiling is 127 × 15 cm = **19.05 m**, not 9 m. The wiki does not cap `detRangeCfg` at the 9 m spec figure. Indices above 60 (9 m) are accepted by the parser but exceed the published detection distance, so they are not usable range. |
| `outputLatency` | `outputLatency par1 par2 par3` | `par1` = −1 reserved; `par2` = delay after target detected, 0–65535 in 25 ms steps; `par3` = delay after target disappears, 0–65535 in 25 ms steps |
| `sensorCfgStart` | `sensorCfgStart par1` | 0 = requires explicit start; 1 = auto-start on power-up (default) |
| `sensorStart` / `sensorStop` | no parameters | must stop before reconfiguring |
| `saveCfg` | `saveCfg 0x45670123 0xCDEF89AB 0x956128C6 0xDF54AC89` | fixed magic constants |
| `factoryReset` | `factoryReset 0x45670123 0xCDEF89AB 0x956128C6 0xDF54AC89` | fixed magic constants |
| `resetSystem` | no parameters | reboot |

ESPHome adds a `sensitivity` field, **range 0 to 9**, and documents the factory latency defaults:
**delay after detect = 2.5 s, delay after disappear = 10 s**. Those defaults are the *latency to
detect* and *latency to clear* — 10 s of hold-off is catastrophic for a moving robot and must be
reprogrammed down (minimum step 25 ms).

**Silicon.** DFRobot does not name the chip or OEM module. The CLI grammar (`sensorStart`,
`detRangeCfg`, `saveCfg` with those four magic words) matches the Shenzhen Leapmmw HS2xx3A-series
24 GHz presence module family. **Inferred, not datasheet-verified** — I did not obtain a Leapmmw
datasheet, so I will not assert it.

**Human vs pet vs object — vendor's own words.** The DFRobot wiki FAQ asks *"Can this mmWave radar
sensor (SKU: SEN0395) only detect human body?"* and answers verbatim:

> "No, the sensor detects movement of all objects within range by detecting mmWave radar and is very
> sensitive."

That is an explicit vendor disclaimer that the word "Human" in the product name is application
framing, not a classifier. The same FAQ warns *"Due to the high sensitivity of this millimeter-wave
radar sensor, please ensure that the sensor is fixed firmly when using it"* — i.e. vibration of the
sensor itself produces false presence. On a driving robot that is a direct problem.

---

### 3.2 SEN0609 — C4001, 24 GHz, 25 m motion / 16 m presence, UART (`$13.90`)

Sources: [product page](https://www.dfrobot.com/product-2793.html),
[wiki](https://wiki.dfrobot.com/sen0609/),
[library README](https://github.com/DFRobot/DFRobot_C4001).

| Parameter | Published value |
|---|---|
| Operating frequency | 24 GHz |
| Modulation | FMCW |
| **Max motion detection range** | 25 m |
| **Human presence (static) detection range** | 16 m |
| Distance measurement range | **1.2 m to 25 m** |
| Velocity measurement range | 0.1 m/s to 10 m/s |
| Beam angle | 100° × 40° |
| Supply | 3.3 V / 5 V |
| Supply current | **not published** |
| Interface | UART (9600 baud default) + I/O level output |
| Operating temperature | −40 to +85 °C |
| Dimensions | 26 × 30 mm |

Conditions for the 25 m / 16 m figures are **not published**: no target RCS, no reflectivity, no
indoor/outdoor qualification.

**Output type.** Unlike SEN0395, C4001 reports real data: `getTargetNumber()` (count),
`getTargetRange()` (float, metres), `getTargetSpeed()` (float, m/s, signed = approach/recede), and
`getTargetEnergy()` (uint32). **It reports radial range and radial velocity only — no azimuth, no
elevation, no x/y coordinates.** A single C4001 cannot tell you *where* in its 100° fan the target is.

**API and configurable zone/threshold commands** (verbatim from the library README):

| Method | Parameters, ranges, units |
|---|---|
| `setSensorMode(eMode_t)` | `eExitMode` (0x00, presence) or `eSpeedMode` (0x01, motion+speed) |
| `setDetectionRange(uint16_t min, uint16_t max)` | `min` 30–2000 cm; `max` 240–2000 cm |
| `setDetectThres(uint16_t min, uint16_t max, uint16_t thres)` | `min` 30–2000 cm, `max` 240–2000 cm, `thres` 0–65535 in 0.1 units |
| `setTrigSensitivity(uint8_t)` | 0–9 |
| `setKeepSensitivity(uint8_t)` | 0–9 |
| `setDelay(uint8_t trig, uint16_t keep)` | `trig` 0–200 in 0.01 s steps (0–2 s **latency to detect**); `keep` 4–3000 in 0.5 s steps (2–1500 s **latency to clear**) |
| `setSensor(eSetMode_t)` | `eStartSen`, `eStopSen`, `eResetSen`, `eRecoverSen`, `eSaveParams`, `eChangeMode` |
| `motionDetection()` | returns bool |

**Defect worth flagging.** The product page advertises 25 m, but the library's own
`setDetectionRange` accepts a maximum of **2000 cm = 20 m**. The configurable zone therefore cannot
be set to the advertised range. Not a blocker for a robot (which needs metres, not tens of metres),
but it means the marketing number and the programmable number disagree.

**Human vs pet vs object.** C4001 applies no classification. It thresholds reflected energy and
radial velocity. A ceiling fan, a curtain in a draught, or a rolling ball all produce a valid
`getTargetSpeed()`. DFRobot publishes nothing about animal rejection for this part.

---

### 3.3 SEN0610 — Gravity C4001, 12 m, I2C + UART (`$12.90`)

Sources: [product page](https://www.dfrobot.com/product-2795.html),
[wiki](https://wiki.dfrobot.com/sen0610/),
[wiki mirror](https://wiki.dfrobot.com/SKU_SEN0610_Gravity_C4001_mmWave_Presence_Sensor_12m_I2C_UART).

Same C4001 silicon as SEN0609 on a Gravity PH2.0 carrier, with a **wider vertical beam** and a
shorter range binning.

| Parameter | Published value |
|---|---|
| **Presence (static) detection range** | 8 m |
| **Motion detection range** | 12 m |
| Distance measurement range | 1.2 m to 12 m |
| Speed detection range | 0.1 m/s to 10 m/s |
| Beam angle | **100° × 80°** |
| Operating frequency | 24 GHz, FMCW |
| Supply | 3.3 V / 5 V |
| Supply current | **not published** |
| I2C address | 0x2A / 0x2B (selectable) |
| UART baud | 9600 |
| Operating temperature | −40 to +85 °C |
| Dimensions | 22 × 30 mm |

Same `DFRobot_C4001` API as SEN0609 (I2C constructor instead of UART). The **80° vertical beam** is
the single most robot-relevant difference from SEN0609's 40° — see the geometry analysis in §5.

---

### 3.4 SEN0691 — Fermion C4002, 11 m motion / 10 m static (`$8.90`)

Sources: [product page](https://www.dfrobot.com/product-3081.html),
[wiki](https://wiki.dfrobot.com/sen0691/),
[quick-start](https://wiki.dfrobot.com/sen0691/docs/23399),
[library README](https://github.com/DFRobot/DFRobot_C4002).

| Parameter | Published value |
|---|---|
| Operating frequency | 24 GHz – 24.25 GHz |
| Detection capability | "Motion, Micro-Motion/Stationary Human Body" |
| **Max detection distance** | **Motion 11 m, Micro-Motion/Stationary 10 m** |
| **Detection angle** | **120° × 120°** |
| Supply | 3.6 – 5.5 V |
| Supply current | **not published** |
| Output | OUT (configurable IO) + UART |
| Integrated ambient light sensor | 0 – 50 lux |
| Operating temperature | −20 to +85 °C |
| Dimensions | 22 × 26 mm |

**This is the widest-FoV and cheapest presence part DFRobot sells, and the only one with a
120-degree vertical beam.** It is also the most configurable.

**API, thresholds and detection zones** (verbatim ranges from the library README):

| Method | Parameters, ranges, units |
|---|---|
| `setDetectRange(uint16_t closest, uint16_t farthest)` | 0 – 1100 cm |
| `setResolutionMode(eResolutionMode_t)` | 80 cm gates or 20 cm gates |
| `configureGate(eDistanceGateType_t, uint8_t *gateData)` | enable/disable individual distance gates |
| `setGateThresh(eDistanceGateType_t, uint8_t *thresh)` | per-gate threshold 0–99 |
| `setSensitivity(eDistanceGateType_t, eThreshGroup_t)` | low / medium / high / custom |
| `setLightThresh(float)` | 0 – 50 lux (0 = always active) |
| `setLockTime(float)` | **0.2 – 10 s**, dwell between occupied/unoccupied transitions |
| `setTargetDisappearDelay(uint16_t)` | **0 – 65535 s**, hold after loss (**latency to clear**) |
| `setReportPeriod(uint8_t)` | 0 – 255 in 0.1 s steps (update rate) |
| `setBaudrate(eBaudrate_t)` | 57600 – 1 000 000 bps |
| `startEnvCalibration(uint16_t delayTime, uint16_t contTime)` | 15 – 65535 s each |
| `setOutPinMode(eOutpinMode_t)` | OUT asserts on motion-only / presence-only / either |
| `getTargetState()` | no target / presence / motion |
| `getPresenceTargetInfo()` | distance (m), energy 0–99 |
| `getMotionTargetInfo()` | distance (m), speed (m/s), energy, **direction** |
| `getPresenceGateIndex()` | active-zone bitmap, bits 0–15 (80 cm mode) or 0–25 (20 cm mode) |
| `getLightIntensity()` | lux |

**`setReportPeriod` down to 0.1 s gives a 10 Hz nominal update rate** — the fastest published update
of any DFRobot presence radar. `setLockTime` minimum 0.2 s is the practical floor on detect latency.

**Calibration caveat that matters for a robot.** The wiki states: *"During calibration, ensure that
the room where the sensor is located is unoccupied to avoid affecting accuracy"* and requires *"no
one on either side of the sensor directly in front of the transmitter."* The C4002 learns a static
clutter background. A robot that drives changes its background continuously, invalidating the
calibration. DFRobot publishes no guidance for a moving mount.

**Human vs pet vs object.** No classifier. `getMotionTargetInfo()` returns distance, speed, energy
and direction; `getPresenceTargetInfo()` returns distance and energy. Those four scalars are the
entire feature vector available. DFRobot publishes no pet immunity, no animal rejection, and no
false-trigger guidance for fans or curtains.

---

### 3.5 SEN0623 — C1001, 60 GHz fall detection / sleep monitoring (`$29.00`)

Sources: [product page](https://www.dfrobot.com/product-2861.html),
[wiki](https://wiki.dfrobot.com/sen0623/),
[library README](https://github.com/DFRobot/DFRobot_HumanDetection).

| Parameter | Published value |
|---|---|
| Working frequency | **61 – 61.5 GHz** |
| Transmit power | 6 dBm |
| Farthest detection distance | 11 m — **condition IS published**: the product page states *"When mounted on the ceiling at a height of 2.7 meters, the C1001 ensures precise fall detection"* across the 11 m range. This is the only measurement condition DFRobot publishes for any range figure in this lane. Target RCS and reflectivity are still not given. |
| Radar detection angle | 100° × 100° (no mode-dependent narrowing is published — see correction below) |
| Sleep-mode detection distance (chest) | 0.4 – 2.5 m |
| Breathing / heartbeat detection distance (chest) | 0.4 – 1.5 m |
| Breathing measurement range | 10 – 25 breaths/min |
| Heartbeat measurement range | 60 – 100 beats/min |
| Working voltage | 5 V |
| Working current | ≤ 100 mA |
| UART baud | 115200 (from wiki sample code; not in the spec table) |
| Working temperature | −20 to +60 °C |

**Correction (2026-09-12, adversarial re-check).** An earlier revision of this file stated that the
DFRobot comparison blog gives the C1001 sleep mode a **40° × 40°** cone versus 100° × 100° in
fall-detection mode. **That is not in the source.** Re-fetching
`https://www.dfrobot.com/blog-22042.html` and `https://wiki.dfrobot.com/sen0623/` on 2026-09-12
returns only `100°×100°` for the C1001; neither page states any mode-dependent narrowing, and the
blog's comparison table has no detection-angle column for the C4001 variants at all. **The 40° sleep-mode
figure is withdrawn as unsourced.** DFRobot publishes one detection angle for the C1001, 100° × 100°,
and constrains sleep mode by *distance* only (chest 0.4–2.5 m), not by angle.

**This is the only DFRobot radar that outputs target coordinates.** The library exposes
`track(uint16_t *x, uint16_t *y)`. It also exposes posture/fall state (`getFallData`, `getFallTime`,
`staticResidencyTime`, `unmannedTime`), installation geometry (`dmInstallHeight`,
`dmInstallAngle(x,y,z)`, `dmAutoMeasureHeight`), and vital signs (`getHeartRate`, `getBreatheValue`,
`getBreatheState` returning normal/fast/slow/none). Work mode is selected by `configWorkMode()`
between fall-detection mode and sleep mode.

**Critical constraint: this part is designed for a fixed ceiling or high-wall mount looking down.**
The whole fall-detection algorithm is a point-cloud posture classifier referenced to a configured
installation height and tilt. Mounting it on a moving 1 m robot breaks the reference frame it
depends on. DFRobot also carries a disclaimer that it is *"not a certified medical device."*

**Human vs pet.** The C1001 is the closest thing DFRobot sells to a classifier, because it classifies
*posture* (standing, lying) and measures respiration. But nothing in the API returns a species label,
and the respiration bands overlap heavily with pets (see §6). It cannot distinguish a dog lying on
the floor from a fallen human on the published feature set.

---

### 3.6 SEN0557 — 24 GHz presence module, 6 m (`$9.90`)

Sources: [product page](https://www.dfrobot.com/product-2648.html),
[wiki](https://wiki.dfrobot.com/sen0557/).

| Parameter | Published value |
|---|---|
| Operating frequency range | 24 GHz – 24.25 GHz |
| Sweep bandwidth | **250 MHz** |
| Modulation | FMCW |
| Detection distance | 0.75 m – 6 m |
| **Measured blind zone** | **30 cm** |
| Detection angle | ±60° |
| Distance resolution | 0.75 m |
| Operating voltage | DC 5 – 12 V |
| Average operating current | 80 mA |
| Default baud rate | 57600 ("Best 256000") |
| Interface | UART + GPIO, 3.3 V logic |
| Ambient temperature | −40 to +85 °C |
| Dimensions | 7 × 35 mm |

GPIO behaviour: high (3.3 V) when a human is detected, low (0 V) when not.

**Silicon.** DFRobot does not name the OEM module. The specification set — 24–24.25 GHz, 250 MHz
sweep, 0.75 m gate resolution, 8 gates to 6 m, ±60°, 256000 baud option — matches the **Hi-Link
HLK-LD2410** family exactly. **Inferred, not vendor-confirmed.** If that inference holds, the raw
module reports separate *moving target distance + energy* and *stationary target distance + energy*
per 0.75 m gate, with per-gate sensitivity and an unmanned-duration timer — but **DFRobot does not
publish the protocol or the separate moving/static ranges on either its product page or its wiki**,
and its Arduino library exposes only sensitivity adjustment. DFRobot's own moving-versus-stationary
ranges for SEN0557 are **not published**.

Note the resolution physics check: range resolution ΔR = c / (2·B) = 3×10⁸ / (2 × 250×10⁶) = **0.60 m**.
The quoted 0.75 m is the gate spacing, slightly coarser than the theoretical limit. The numbers are
internally consistent, which is a good sign for the datasheet's honesty.

---

### 3.7 SEN0306 — 24 GHz ranging radar, 20 m (`$65.90`) — the obstacle sensor, not a presence sensor

Source: [product page](https://www.dfrobot.com/product-1882.html).

| Parameter | Published value |
|---|---|
| Frequency | 24 GHz (K-band) |
| Detection range | 0.5 – 20 m |
| Range resolution | 0.01 m (reporting resolution) |
| Accuracy | ±0.1 m |
| H-plane beam angle | 78° (−3 dB) |
| V-plane beam angle | 23° (−3 dB) |
| Output | asynchronous serial, 57600 baud |
| Supply voltage | 4 – 8 V DC |
| Current | > 100 mA |
| Power consumption | 400 mW |
| Data update rate | 10 Hz |
| Working temperature | 0 – 70 °C |

This part measures **distance to any reflector**, including multiple targets, and penetrates
non-metallic materials, dust, smoke and fog. It does **not** do micro-motion presence and makes no
human claim. For requirement (a) — "any obstacle it could collide with" — this is the only DFRobot
radar that is honestly aimed at the job, and its 0.5 m minimum range and 23° vertical beam make it
poorly suited to a 350 mm robot detecting a cat at 400 mm.

---

### 3.8 SEN0192 (`$8.90`) and SEN0521 (discontinued) — Doppler, not mmWave

- **SEN0192**, Gravity Digital 10.525 GHz Microwave Sensor
  ([product page](https://www.dfrobot.com/product-1403.html), [wiki](https://wiki.dfrobot.com/sen0192/)):
  X-band Doppler, sensing range **"2-16M continuously adjustable"** (verbatim) via potentiometer,
  3 dB beamwidth **72° horizontal × 36° vertical**, 5 V ± 0.25 V, **working current 60 mA max /
  37 mA typical** (this *is* published — an earlier revision of this file wrongly recorded it as
  "not published"), 13 dBm EIRP minimum output power, −86 dBm receive sensitivity, 3–80 Hz
  bandwidth, single digital output, 48.5 × 63 mm. It outputs **one bit: something moved**. No range,
  no speed, no presence-while-still. It is a motion switch, and its 63 mm board is large for a
  350 mm robot. Measurement condition for the 2–16 m figure is **not published**, and DFRobot does
  not say where on the board the trimmer sits.
- **SEN0521**, 5.8 GHz Microwave Radar Module: listed as **DISCONTINUED** with price $0.00. Do not
  design it in. **Correction (2026-09-12):** the product page is **not delisted** — it is live and
  reachable at `https://www.dfrobot.com/product-2585.html`, it still appears in the
  `search-mmwave` results, its title is now literally *"5.8GHz Microwave Radar Module
  (Discontinued)"*, and it **does still publish specifications**: detection distance **11 m**, beam
  angle **120° × 120°**, 4.5–5.5 V, 22 mA, 5.8 GHz, 115200 baud, −40 to 85 °C, 20 × 18 mm. The
  measurement condition for the 11 m figure is not published. Those numbers are recorded here only
  so the part is not re-researched; it remains unbuyable.

**SEN0676**, the 80 GHz Liquid Level Detection Sensor (40 m, UART, $59.00), is a tank-level radar. It
is listed here only for catalogue completeness; it is not a presence or obstacle sensor.

---

## 4. Consolidated comparison

| SKU | Band | Moving range | Static/micro-motion range | Min range / blind zone | H FoV | V FoV | Outputs | Detect latency | Clear latency | Supply | Current | Price |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| SEN0395 | 24 GHz | 9 m (combined) | 9 m (combined, not split) | 0 cm nominal, 15 cm index step | 100° | 40° | boolean only | 2.5 s default, 25 ms step | 10 s default, 25 ms step | 3.6–5 V | 90 mA | $29.00 |
| SEN0609 | 24 GHz | 25 m | 16 m | 1.2 m (distance meas.) | 100° | 40° | count, range, speed, energy | 0–2 s (10 ms step) | 2–1500 s (0.5 s step) | 3.3/5 V | not published | $13.90 |
| SEN0610 | 24 GHz | 12 m | 8 m | 1.2 m (distance meas.) | 100° | **80°** | count, range, speed, energy | 0–2 s | 2–1500 s | 3.3/5 V | not published | $12.90 |
| SEN0691 | 24–24.25 GHz | 11 m | 10 m | 0 cm per `setDetectRange` | **120°** | **120°** | state, range, speed, energy, direction, gate bitmap, lux | lock time 0.2–10 s | 0–65535 s | 3.6–5.5 V | not published | $8.90 |
| SEN0623 | 61–61.5 GHz | 11 m (**at 2.7 m ceiling mount**) | 11 m; vitals 0.4–1.5 m | 0.4 m (vitals) | 100° | 100° | **x/y track**, posture, fall, breathing, heart rate | not published | `unmannedTime` configurable | 5 V | ≤100 mA | $29.00 |
| SEN0557 | 24–24.25 GHz | not split | not split (6 m combined) | **30 cm measured** | ±60° | not published | boolean GPIO + UART | not published | not published | 5–12 V | 80 mA | $9.90 |
| SEN0306 | 24 GHz | any reflector to 20 m | n/a | 0.5 m | 78° | 23° | distance to multiple targets | 10 Hz frame | 10 Hz frame | 4–8 V | >100 mA | $65.90 |
| SEN0192 | 10.525 GHz | 2–16 m (pot) | none | not published | 72° | 36° | single bit | not published | not published | 5 V | 60 mA max / 37 mA typ | $8.90 |

Every "not published" above is genuinely absent from the product page, the wiki, the wiki mirror and
the library README. I did not estimate any of them.

**Measurement-condition caveat that applies to every range column above.** With the single exception
of SEN0623 (11 m *"when mounted on the ceiling at a height of 2.7 meters"*), DFRobot publishes **no
target RCS, no target reflectivity, no clutter description and no indoor/outdoor qualification** for
any range figure in this table. Every range number here is therefore a bare marketing maximum and
must be treated as an upper bound measured under conditions the vendor declines to state.

---

## 5. Fit for a 350 mm, 600–1200 mm tall mobile robot

### 5.1 Vertical beam geometry versus a 200–500 mm tall pet

This is the decisive constraint, and it is pure trigonometry from the published beam angles. Put the
sensor at height `h` with a symmetric vertical beam of total angle `2θ`. The lower beam edge reaches
a target of height `t` at horizontal distance `d = (h − t) / tan θ`. Closer than `d`, the target is
**below the beam**.

For a sensor at h = 900 mm and a cat with its back at t = 300 mm:

| Sensor | Total V FoV | θ (half-angle) | `d` where a 300 mm pet enters the beam |
|---|---|---|---|
| SEN0395 / SEN0609 | 40° | 20° | **1.65 m** |
| SEN0306 | 23° | 11.5° | **2.95 m** |
| SEN0610 | 80° | 40° | **0.72 m** |
| SEN0623 | 100° | 50° | **0.50 m** |
| SEN0691 | 120° | 60° | **0.35 m** |

A 350 mm robot needs to see a cat that is 300–600 mm from its skin. **SEN0395, SEN0609 and SEN0306
cannot physically see a floor-level pet inside their own stopping distance when mounted at torso
height.** Only SEN0691 (120°) and SEN0623 (100°) have the vertical coverage, and only if mounted low.
Mounting SEN0395 low, at h = 400 mm, moves its 300 mm-pet threshold to 0.27 m — which works, but then
a standing adult's torso leaves the beam beyond about 3.3 m.

### 5.2 360-degree coverage cost

| Sensor | H FoV | Units for 360° (no overlap) | Units with 20% overlap | Unit price | Ring cost |
|---|---|---|---|---|---|
| SEN0691 | 120° | 3 | 4 | $8.30 at 10+ | **$33.20** |
| SEN0610 | 100° | 4 | 5 | $12.90 | $64.50 |
| SEN0609 | 100° | 4 | 5 | $13.90 | $69.50 |
| SEN0557 | 120° (±60°) | 3 | 4 | $9.20 at 10+ | $36.80 |
| SEN0395 | 100° | 4 | 5 | $29.00 | $145.00 |
| SEN0623 | 100° | 4 | 5 | $29.00 | $145.00 |

SEN0691 is the clear cost and coverage winner for a ring.

### 5.3 The moving-platform problem — the real blocker

**Every DFRobot presence radar in this lane is designed for a static mount, and none of them
documents behaviour on a moving platform.** The physics is unambiguous:

1. **Static/micro-motion presence depends on static-clutter cancellation.** FMCW presence radars
   build a background model of the zero-Doppler return and then look for small residual phase
   modulation (a chest wall moving a few millimetres). When the radar itself translates, every
   stationary scatterer in the room acquires a radial velocity equal to the robot's own speed
   component. The clutter map is invalidated on every frame. The "stationary human, 10 m" and
   "micro-motion" specifications do not survive ego-motion.
2. **The C4002 makes this explicit without meaning to.** `startEnvCalibration()` exists precisely
   because the part learns a static environment, and the wiki instructs that the room must be empty
   during calibration. A robot drives its environment model out from under itself.
3. **The SEN0395 FAQ makes it explicit too:** *"please ensure that the sensor is fixed firmly when
   using it"*, offered as the cure for an output stuck at 1. Sensor vibration alone produces false
   presence; a drivetrain provides continuous vibration.
4. **Motion detection inverts.** On a moving robot, a *stationary* wall produces a strong Doppler
   return and a *human walking at the robot's speed in the same direction* produces near-zero
   Doppler. Without ego-motion compensation, the motion channel reports the world and misses the
   person. Compensation requires wheel odometry fused with the radial-velocity output — which the
   C4001 and C4002 do provide (`getTargetSpeed`, `getMotionTargetInfo().speed`) but which DFRobot
   provides no guidance or firmware support for.

None of that is a DFRobot defect. It is the wrong sensor class for the mount. These parts are
room-occupancy sensors.

### 5.4 Mutual interference between units in a ring

All 24 GHz parts occupy the **same 24.00–24.25 GHz ISM band with FMCW chirps**. Three or four of
them firing at 100–120° apart on a 350 mm chassis will illuminate each other's sidelobes.
**DFRobot publishes no interference-mitigation information, no chirp-randomisation option, no
synchronisation pin, and no multi-sensor deployment guidance for any of SEN0395, SEN0557, SEN0609,
SEN0610 or SEN0691.** This is an unresolved, unpublished risk that must be settled by bench test
before committing to a ring. The 60 GHz SEN0623 would not interfere with the 24 GHz parts, which is
an argument for mixing bands if a ring is built.

### 5.5 Power budget

Only SEN0395 (90 mA), SEN0557 (80 mA) and SEN0623 (≤100 mA) publish current. A four-unit SEN0395
ring draws **360 mA at 5 V = 1.8 W** continuously. A four-unit SEN0557 ring draws 320 mA = 1.6 W. The
C4001 and C4002 currents are **not published** and must be measured.

---

## 6. Human versus pet versus inanimate object — the plain answer

**No DFRobot mmWave radar can distinguish a human from a pet from a moving inanimate object.**

### What the vendor claims

DFRobot names these parts "Human Presence Detection Sensor". That naming is application framing. The
only place DFRobot addresses the question directly, the SEN0395 wiki FAQ, answers it against itself:

> "No, the sensor detects movement of all objects within range by detecting mmWave radar and is very
> sensitive."

Across SEN0395, SEN0557, SEN0609, SEN0610, SEN0691 and SEN0623, I found **zero** mentions of pet
detection, pet immunity, animal filtering, or false triggers from fans, curtains or rolling objects,
on the product pages, the wikis, the wiki mirrors, the library READMEs, or the C4001/C4002/C1001
comparison blog. The topic is simply absent from DFRobot's documentation.

### What the underlying physics supports

Species discrimination on radar is a real, published capability, but it needs data these modules do
not emit:

- **Micro-Doppler classification works.** The dominant discriminative feature between humans and
  animals is limb micro-Doppler — the gait signature of a four-legged 400 mm animal differs
  measurably from a two-legged 1700 mm human. Published work applies convolutional networks to
  range-Doppler spectrograms to separate humans, dogs, cats and pigs
  ([RayPet, Springer 2024](https://link.springer.com/chapter/10.1007/978-981-97-3289-0_25);
  [IR-UWB human/animal vital-sign discrimination, PMC6888617](https://www.ncbi.nlm.nih.gov/pmc/articles/PMC6888617/)).
- **But it needs the raw range-Doppler map or raw ADC samples.** Not one DFRobot module exposes raw
  IQ, an ADC stream, or a range-Doppler matrix. The richest output in the whole lane is the C4002's
  `{state, distance, speed, energy, direction, per-gate energy bitmap}`. Those scalars are
  post-processed, threshold-derived, and throw away the spectrogram that a classifier would need.
  **A custom human/pet classifier is therefore not implementable on any DFRobot mmWave part.**
- **Energy alone is not a species discriminator.** Radar cross-section scales with target size, but
  received power falls as 1/R⁴. A cat at 1 m and a human at 3 m can return identical energy. This is
  the same ambiguity that has defeated microwave Doppler intrusion detectors for decades — a dog at
  15 feet and a person at 30 feet look alike.
- **Vital signs are not a species discriminator either.** The C1001 measures respiration over
  10–25 breaths/min. Resting cats run roughly 20–30/min and resting dogs roughly 15–30/min. The
  bands overlap the human band almost entirely, and the published literature explicitly names this
  as the reason animals trigger false alarms in non-contact vital-sign monitoring.
- **Height gating is the only lever these parts give you, and they do not give you height.** The
  practical industry mitigation for pet immunity is mounting the sensor at ≥2 m and narrowing the
  vertical beam so floor-level animals fall below it. That is geometry, not classification, and it
  requires a tall fixed mount. It is unavailable to a 350 mm robot that must see both a 1.8 m adult
  and a 0.3 m cat within 1 m.
- **Moving inanimate objects are indistinguishable by construction.** A ceiling fan, a curtain in a
  draught and a rolling ball all produce non-zero radial velocity and a threshold-crossing energy
  return. The C4001/C4002 will report them as motion targets with a distance and a speed. There is
  no mechanism in the published API to reject them.

### Summary verdict per sensor

| SKU | Detects any obstacle? | Detects moving human? | Detects still human? | Detects pet? | Distinguishes human/pet/object? |
|---|---|---|---|---|---|
| SEN0395 | Only as "presence" bit | Yes | Yes (claimed) | Yes, undifferentiated | **No** — vendor states it detects all moving objects |
| SEN0609 | Yes, as range+speed target | Yes | Yes to 16 m | Yes, undifferentiated | **No** |
| SEN0610 | Yes, as range+speed target | Yes | Yes to 8 m | Yes, undifferentiated | **No** |
| SEN0691 | Yes, range+speed+energy+direction | Yes | Yes to 10 m | Yes, undifferentiated | **No** |
| SEN0623 | Partially — x/y track | Yes | Yes | Yes, undifferentiated | **No** — posture and vitals only, no species label |
| SEN0557 | Only as presence bit | Yes | Yes (claimed) | Yes, undifferentiated | **No** |
| SEN0306 | **Yes — true ranging to any reflector** | Yes (as a moving reflector) | No | Only as a reflector | **No** |
| SEN0192 | Only moving reflectors | Yes | **No** | Yes, undifferentiated | **No** |

---

## 7. What is not published, and must be bench-measured

1. **Supply current for C4001 (SEN0609, SEN0610) and C4002 (SEN0691).** Not on any page. (SEN0192's
   current *is* published — 60 mA max, 37 mA typical — and was wrongly listed here before.)
2. **Moving-versus-stationary detection range split for SEN0395 and SEN0557.** Both quote one number.
3. **Measurement conditions for every published range, except one.** No target RCS, no reflectivity,
   no indoor/outdoor qualification, no clutter description, on any DFRobot radar page in this lane.
   **The one exception is SEN0623**, whose product page ties the 11 m figure to a 2.7 m ceiling mount.
4. **Vertical FoV for SEN0557.** Only "±60°" is given, without saying whether that is azimuth,
   elevation, or both.
5. **Detect and clear latency for SEN0557 and SEN0623.** Not published.
6. **Angular resolution for every part.** None published; none of the 24 GHz parts outputs azimuth,
   so the practical angular resolution equals the full beamwidth.
7. **Multi-sensor interference behaviour.** Nothing published for any part.
8. **Behaviour on a moving platform.** Nothing published for any part.
9. **The silicon inside SEN0395, SEN0557, C4001 and C4002.** DFRobot names no chip vendor for any of
   them. My Leapmmw (SEN0395) and Hi-Link LD2410 (SEN0557) identifications are **inferred from
   matching specification fingerprints, not confirmed**.

---

## 8. Recommendation for this robot

**For requirement (b), humans:** SEN0691 (C4002) at $8.90 is the only sensible DFRobot choice. It has
the widest beam (120° × 120°), the lowest price, 20 cm range gates, per-gate thresholds, the fastest
update (0.1 s report period), and it reports distance, speed, energy and direction rather than a bare
bit. Three units cover 360°; four cover it with overlap for about $33.

**For requirement (c), pets:** no DFRobot part solves this. SEN0691's 120° vertical beam at least
*illuminates* a floor-level animal from 0.35 m outward when mounted at 900 mm, which is more than any
other part in the lane manages. It still cannot label it a pet.

**For requirement (d), human/pet/object discrimination:** **this lane cannot satisfy it.** Not
because DFRobot picked bad parts, but because none of these modules exposes the range-Doppler data
that species classification requires. Discrimination must come from a different modality in the
sensor fusion — a thermal IR array (a 38 °C human torso versus a fur-covered pet versus a
room-temperature object is separable), a multizone ToF height profile, or a camera. Radar's
contribution to the fusion is range and radial velocity through-clothing and in the dark, not
identity.

**For requirement (a), obstacles:** none of the presence parts is suitable, and SEN0306 at $65.90
with a 0.5 m blind zone and a 23° vertical beam is not either. Collision avoidance for a 350 mm
chassis belongs to a ToF or ultrasonic lane.

**The one caution that overrides all of the above:** every DFRobot presence radar here assumes a
static mount, and the entire static/micro-motion capability — the reason to choose mmWave over PIR —
depends on clutter cancellation that ego-motion destroys. Before committing, bench-test one SEN0691
on the actual drivetrain, moving, and measure what fraction of its static-presence claim survives.
If the answer is "none", these parts degrade to expensive Doppler motion switches and the lane's
value collapses.

---

## 9. Sources

- DFRobot catalogue search: https://www.dfrobot.com/search-mmwave.html
- SEN0395 product: https://www.dfrobot.com/product-2282.html
- SEN0395 wiki: https://wiki.dfrobot.com/mmwave_radar_human_presence_detection_sku_sen0395
- SEN0395 wiki (FAQ): https://wiki.dfrobot.com/sen0395/
- SEN0395 API/protocol reference: https://wiki.dfrobot.com/sen0395/docs/21398
- SEN0395 ESPHome component: https://esphome.io/components/dfrobot_sen0395/
- SEN0609 product: https://www.dfrobot.com/product-2793.html
- SEN0609 wiki: https://wiki.dfrobot.com/sen0609/
- SEN0609 wiki mirror: https://wiki.dfrobot.com/SKU_SEN0609_C4001_mmWave_Presence_Sensor_25m
- SEN0610 product: https://www.dfrobot.com/product-2795.html
- SEN0610 wiki: https://wiki.dfrobot.com/sen0610/
- SEN0610 wiki mirror: https://wiki.dfrobot.com/SKU_SEN0610_Gravity_C4001_mmWave_Presence_Sensor_12m_I2C_UART
- DFRobot_C4001 library: https://github.com/DFRobot/DFRobot_C4001
- SEN0691 product: https://www.dfrobot.com/product-3081.html
- SEN0691 wiki: https://wiki.dfrobot.com/sen0691/
- SEN0691 quick start: https://wiki.dfrobot.com/sen0691/docs/23399
- DFRobot_C4002 library: https://github.com/DFRobot/DFRobot_C4002
- SEN0623 product: https://www.dfrobot.com/product-2861.html
- SEN0623 wiki: https://wiki.dfrobot.com/sen0623/
- DFRobot_HumanDetection library: https://github.com/DFRobot/DFRobot_HumanDetection
- SEN0557 product: https://www.dfrobot.com/product-2648.html
- SEN0557 wiki: https://wiki.dfrobot.com/sen0557/
- SEN0306 product: https://www.dfrobot.com/product-1882.html
- SEN0192 wiki: https://wiki.dfrobot.com/sen0192/
- DFRobot C4001 vs C4002 vs C1001 guide: https://www.dfrobot.com/blog-22042.html
- Hi-Link HLK-LD2410 manual (for the SEN0557 OEM inference): https://www.hlktech.net/index.php?id=988
- RayPet, pet activity/posture recognition with FMCW mmWave radar: https://link.springer.com/chapter/10.1007/978-981-97-3289-0_25
- Distinguishing humans and animals in vital-sign monitoring with IR-UWB radar: https://www.ncbi.nlm.nih.gov/pmc/articles/PMC6888617/
