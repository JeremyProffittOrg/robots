# DFRobot mmWave / Radar Catalogue — Complete Grid

**Lane:** `dfrobot-mmwave-full-grid`
**Objective:** exhaustive breadth. Every radar-class product sold or catalogued on dfrobot.com, with the
specification each vendor page or wiki actually publishes, and nothing invented.
**Catalogue read date:** 2026-09-12. All prices are DFRobot list price in USD as displayed on that date.
**Application context (for relevance notes only):** 350 mm square or round mobile robot, 600–1200 mm tall,
needing 360-degree obstacle, human and pet detection. Deep per-sensor analysis belongs to other lanes;
this document is the index and the price/spec grid.

---

## 1. How the catalogue was enumerated

DFRobot's storefront search is the only reliable index — the wiki category listing is smaller and the
"Sensors" navigation tree does not expose a dedicated "Radar" leaf that contains all of these parts.
The following queries were each walked to the end of their result set:

| Query URL | Items reported by the page | Radar-class products surfaced |
|---|---|---|
| `https://www.dfrobot.com/search-mmwave%20radar.html` | 10 | SEN0306, SEN0395, SEN0557, SEN0610, SEN0609, SEN0691, SEN0192, SEN0676, SEN0521 (+ KIT0216-EN) |
| `https://www.dfrobot.com/search-mmwave.html` | 11 | same set **plus SEN0623** |
| `https://www.dfrobot.com/search-radar.html` | 41 total, 20 rendered | adds nothing new that is radar; remainder are ToF/LiDAR |
| `https://www.dfrobot.com/search-24GHz.html` | 6 | SEN0306, SEN0557, SEN0395, SEN0610, SEN0609, SEN0691 |
| `https://www.dfrobot.com/search-60GHz.html` | 1 | SEN0623 |
| `https://www.dfrobot.com/search-77GHz.html` | 0 | none |
| `https://www.dfrobot.com/search-microwave.html` | 5 | SEN0192, SEN0306, SEN0623, SEN0557, SEN0521 |
| `https://www.dfrobot.com/search-millimeter%20wave.html` | 10 | adds KIT0234 |
| `https://www.dfrobot.com/search-presence%20detection.html` | 12 | no new radar |
| `https://www.dfrobot.com/search-motion%20sensor.html` | 67 | 4 radar, all already found |
| `https://www.dfrobot.com/search-Doppler.html` | 1 | SEN0192 |
| `https://www.dfrobot.com/search-LD2450.html` | 0 | **DFRobot does not sell the LD2450 tracking radar** |
| `https://wiki.dfrobot.com/category-36/` | 9 radar entries | confirms the same 9 active SKUs |

**Important enumeration finding:** the obvious query — `search-mmwave radar` — **misses SEN0623**, the
60 GHz C1001. A single-query sweep of this vendor is incomplete. Likewise `search-radar.html` returns
"41 items" but renders only 20 and lazy-loads the rest; the unrendered tail was recovered by the
narrower frequency-specific queries rather than by pagination, because `?p=2` returns the same first
page.

**Result: 10 distinct radar-class SKUs (9 active, 1 retired) plus 2 kits that contain or may contain a
radar module.** No 77 GHz automotive-class radar, no multi-target tracking radar (no LD2450 / no
MR24HPC-class point-cloud module), and no 360-degree scanning radar exists in the DFRobot catalogue as
of 2026-09-12. Every 360-degree scanner DFRobot sells is optical (RPLIDAR A1M8-R6, A2M12, C1, S2L,
STL-19P) and therefore out of this lane's scope.

---

## 2. THE COMPLETE TABLE

Read this table with the conditions in Section 3. A single number without its condition is not a
specification.

| SKU | Product name | Band | Chipset | Modulation / detection type | Max range — moving | Max range — static | FoV H | FoV V | Output data | Interface | Price USD | Stock (2026-09-12) |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| **SEN0192** | Gravity: Digital 10.525GHz Microwave Sensor (Motion Detection) | 10.525 GHz (X-band) | not published | CW Doppler, motion only | 2–16 m, "continuously adjustable" | **none — cannot detect static** | 72° | 36° | 1 digital bit (motion / no motion) | Gravity digital pin (3-wire) | $8.90 | In Stock |
| **SEN0306** | mmwave – 24GHz Microwave Radar Distance Sensor (20 Meters) | 24 GHz | not published | FMCW, ranging to any reflector | 0.5–20 m | ranging works on static reflectors; no human-presence claim | 78° (−3 dB, H-plane half-power) | 23° (−3 dB, V-plane half-power) | distance to up to 5 obstacles, 10 Hz | UART TX only, 57600 bit/s | $65.90 | In Stock |
| **SEN0395** | mmWave Radar – 24GHz Human Presence Detection Sensor (9 Meters) | 24 GHz | not published | FMCW + CW, human presence | 9 m | 9 m (stated to detect a sleeping/sitting person) | 100° | 40° | **presence boolean only — no distance** | UART 115200 + GPIO2 level | $29.00 | In Stock |
| **SEN0521** | 5.8GHz Microwave Radar Module (**Discontinued**) | 5.8 GHz | not published | FMCW + CW, human presence | 11 m | 11 m (breathing-level micro-motion claimed) | 120° | 120° | presence level + serial | UART or digital I/O | $0.00 (retired) | **Discontinued — retired from catalogue** |
| **SEN0557** | mmWave – 24GHz Human Presence Sensing Module (6 Meters) — Hi-Link LD2410 | 24–24.25 GHz, 250 MHz sweep | **Hi-Link LD2410** | FMCW, moving + stationary human | 6 m | 6 m | ±60° (120° total) | not published | per-gate moving/stationary energy, target distance, presence bit | UART (wiki: default 57600, "optimized 256000") + GPIO OUT 3.3 V | $9.90 | In Stock |
| **SEN0609** | mmWave – C4001 24GHz Human Presence Detection Sensor for Arduino & ESPHome (25 Meters, UART) | 24 GHz | "C4001" module; silicon vendor **not published** | FMCW, presence + ranging + speed | **25 m** | **16 m** | 100° | 40° | target count, distance (1.2–25 m), speed (0.1–10 m/s), target energy | UART 9600 default + configurable I/O | $13.90 ($13.60 @3+, **$13.30 @5+**, $12.90 @10+) | In Stock |
| **SEN0610** | Gravity: mmWave C4001 24GHz Human Presence Detection Sensor (12 Meters, I2C & UART) | 24 GHz | "C4001" module; silicon vendor **not published** | FMCW, presence + ranging + speed | **12 m** | **8 m** | 100° | 80° | target count, distance (1.2–12 m), speed (0.1–10 m/s), target energy | I2C 0x2A/0x2B + UART 9600, Gravity PH2.0 | $12.90 ($12.70 @3+, $12.40 @5+, $11.90 @10+) | In Stock |
| **SEN0623** | C1001 60GHz mmWave Indoor Fall Detection Sensor (11 Meters) | **61–61.5 GHz** | "C1001" module; silicon vendor **not published** | FMCW + point-cloud posture algorithm | 11 m (presence) | 11 m (presence); sleep/posture 0.4–2.5 m chest | 100° (fall mode) / 40° (sleep mode) | 100° (fall mode) / 40° (sleep mode) | presence, motion, fall state, posture, sleep state, respiration 10–25 br/min, heart rate 60–100 bpm | UART + IO1 (fall level) + IO2 (presence level) | $29.00 | In Stock |
| **SEN0676** | mmWave – 80GHz Liquid Level Detection Sensor (40 Meters, UART) | **77–81 GHz, 4 GHz bandwidth** | not published | FMCW, surface ranging (liquid level) | n/a — level metrology, not motion | 0.15–40 m | ±3° (with lens) / ±25° (no lens) | ±3° (with lens) / ±25° (no lens) | range in mm, ±5 mm accuracy, 1 mm resolution | UART, Modbus protocol | $59.00 | In Stock |
| **SEN0691** | Fermion: C4002 mmWave Human Presence Sensor – Static & Motion Detection for Home Assistant (10m) | 24–24.25 GHz | "C4002" module; silicon vendor **not published** | FMCW, motion + micro-motion/static human | **11 m** | **10 m** (micro-motion / stationary) | 120° | 120° | target state (none/presence/motion), distance, speed, direction, energy 0–99, ambient light lux | UART 115200 + OUT (configurable IO) | $8.90 ($8.70 @3+, $8.60 @5+, $8.30 @10+) | In Stock |
| **KIT0216-EN** | UNIHIKER K10 AIoT Starter Kit — 35-in-1 | contains a "mmWave Human Presence Detection Sensor"; **exact SKU not published** | — | — | — | — | — | — | — | — | $89.00 | In Stock |
| **KIT0234** | WIAnode Sensor Kit for New Media Interactive Art | BOM published: contains "Millimeter Wave Sensor (Human Presence) x1"; **exact SKU not published** | — | — | — | — | — | — | — | — | $79.90 | In Stock |

---

## 3. Per-SKU detail with measurement conditions

### SEN0192 — Gravity: Digital 10.525 GHz Microwave Sensor
Confidence: **vendor-page-verified** (wiki spec table).
- Emission frequency: "10.525 GHz". Output power minimum "13 dBm EIRP".
- Working voltage: "5V +/- 0.25V". Working current (CW): "60 mA max., 37 mA typical".
- Detection distance: "2-16M continuously adjustable" — set by an on-board potentiometer, **not** a
  reported range value. The condition (target size, reflectivity) is **not published**.
- Beamwidth, **published as an explicit 3 dB (half-power) figure**: the wiki labels these
  "Vertical 3dB Beam Width: 36 degrees" and "Level 3dB Beam Width: 72 degrees". The condition is
  therefore stated — these are half-power beamwidths, not a marketing "beam angle".
- Size: "48.5x63 mm" — physically the largest radar in the catalogue, and large relative to a 350 mm robot.
- Mechanism: Doppler. It fires on **relative motion only** and the wiki states it works on "living and
  non-living materials". Consequence for a mobile robot: mounted on a moving base, everything in the
  scene has relative motion, so the output saturates to "motion". It also cannot see a standing human
  or a sleeping cat. **No human/pet/object discrimination of any kind.**

### SEN0306 — 24 GHz Microwave Radar Distance Sensor (20 m)
Confidence: **vendor-page-verified** (wiki spec table).
- Input voltage "4-8V（DC）", input current ">100mA" — the highest current draw of the radar set.
- Detection distance "0.5~20m". Frequency "24GHz". Power "6dBM(Max 10dBM)". Modulation "FMCW".
- Data update speed "10Hz".
- H-plane half-power beamwidth "78（-3db）"; V-plane half-power beamwidth "23（-3db）". This is one of
  **two** DFRobot radars that publish beamwidth as an explicit **−3 dB half-power** figure rather than a
  marketing "beam angle" — SEN0192 does the same ("Vertical 3dB Beam Width: 36 degrees", "Level 3dB Beam
  Width: 72 degrees"). Neither is directly comparable with the unconditioned 100°×40° numbers elsewhere.
- Interface: UART TX at "57600bit/s". It also supplies a 3.3 V auxiliary rail at up to 100 mA.
- Reports up to **5 obstacles** simultaneously — the only DFRobot radar with an explicitly published
  multi-obstacle output.
- Size "34mm×44mm×5mm", 8 g. Operating temperature "0℃~70℃" — the narrowest in the set.
- Relevance: this is the only DFRobot radar marketed as a general **obstacle** ranger rather than a
  human-presence detector. It has no human/pet classification. Its 23° vertical beam is narrow: mounted
  at 900 mm on a 1200 mm robot it will illuminate a band, and a 200–500 mm tall pet near the robot can
  fall below the beam. Price is $65.90, roughly 5x the C4001.

### SEN0395 — 24 GHz Human Presence Detection Sensor (9 m)
Confidence: **vendor-page-verified** (wiki spec table + pinout doc).
- Power supply "3.6~5V"; operating current "90mA"; detection distance "9m".
- Equivalent transmit power: **DFRobot publishes two conflicting figures.** The wiki spec table says
  "13-15dBM"; the product page `https://www.dfrobot.com/product-2282.html` says "9-12dBM". Both are
  first-party. Treat transmit power as unresolved. Beam angle "100×40°"; modulation "FMCW, CW".
- Operating frequency "24GHz"; operating temperature "-40~85℃"; baud "115200"; dimension "24×28mm".
- Output: UART presence value where "0 means that there is no human or object moving in sensing area, 1
  means the opposite", plus "GPIO2...outputs high when people presence detected, otherwise, output low".
- Configurable through serial commands: `DetRangeCfg(0, 9)` sets the detection distance, `OutputLatency`
  sets the on/off hold delay, `factoryReset()` restores defaults.
- **Critical limitation for this robot: it reports a boolean only. No distance, no bearing, no speed.**
  It is an occupancy switch, not a perception sensor. A first-party ESPHome component exists
  (`dfrobot_sen0395`), which is why it is over-represented in home-automation writeups.
- The chipset is **not published** on the DFRobot wiki, the product page, or the Farnell-hosted
  datasheet index; the commonly repeated "LEAPMMW" attribution could not be confirmed from a primary
  source and is recorded here as **unverified**.

### SEN0521 — 5.8 GHz Microwave Radar Module — DISCONTINUED
Confidence: **vendor-page-verified** (retired product page retained for documentation).
- Product page states: "This product has been retired from our catalog and is no longer for sale. This
  page is made available for those looking for specification and documents." Listed price $0.00.
- Frequency 5.8 GHz; detection range 11 m; beam angle "120*120°"; operating voltage "4.5~5.5V";
  operating current 22 mA — by far the lowest-power radar DFRobot ever listed; equivalent transmit power
  "3-5dBM"; modulation FMCW and CW; output serial port or digital I/O high/low; dimensions
  "20*18mm/0.79*0.71""; operating temperature "-40~85℃".
- Included for completeness. **Do not design it in.** It is unpurchasable from DFRobot.

### SEN0557 — LD2410 24 GHz Human Presence Sensing Module (6 m)
Confidence: **vendor-page-verified**, chipset **datasheet-identified** (Hi-Link LD2410).
- Frequency "24GHz-24.25GHz" with "250MHz" sweep bandwidth — the only DFRobot radar that publishes its
  sweep bandwidth, which is what sets the 0.75 m range-gate resolution.
- Voltage "DC5V-12V"; average current "80mA".
- Detection range "0.75m-6m", stated blind zone "30cm", distance resolution "0.75m" (i.e. eight 0.75 m
  range gates). Detection angle "±60°". Vertical FoV is **not published** by DFRobot.
- Output: "Object status output, human is detected: output high (3.3V); nobody is detected: output low
  (0V)", plus a UART engineering-mode frame carrying per-gate moving-target energy and per-gate
  stationary-target energy, and a computed target distance.
- Baud: the DFRobot wiki states default "57600" with "256000" as an optimised rate. **This conflicts
  with Hi-Link's own LD2410 datasheet default of 256000 baud** — treat DFRobot's figure as
  vendor-page-verified but verify empirically before writing firmware.
- Dimensions "7mm×35mm" — the smallest footprint radar in the catalogue.
- Relevance: the per-gate energy vector is the most information-rich cheap output DFRobot sells. It is
  genuinely useful as a crude "how big and how far is the thing" signal, but the classification is
  hard-wired to a human-breathing signature and the module publishes no pet model.

### SEN0609 — C4001 24 GHz Presence Sensor, 25 m, UART
Confidence: **vendor-page-verified** (product page + wiki).
- Detection ranges are published **separately by target state**, which is the reason to prefer this part
  over SEN0395: moving targets "up to 25 meters"; stationary human presence "up to 16 meters"; distance
  measurement "1.2 meters to 25 meters"; velocity "0.1 meters per second to 10 meters per second".
  **The target size and reflectivity condition behind all four figures is not published** — no RCS,
  no reference target, no test geometry. A "25 m" that does not say "on what" is not a specification.
- Price $13.90 at qty 1, with three published volume tiers: "$13.60 @3+", "$13.30 @5+", "$12.90 @10+".
- Beam angle "100° x 40°". Operating voltage "3.3V / 5V". Modulation FMCW at 24 GHz. Default baud 9600.
  Dimensions "26mm x 30mm". Operating temperature "-40℃ to 85℃".
- **Operating current is not published** on the product page or wiki. The Farnell-hosted datasheet PDF
  (`https://www.farnell.com/datasheets/4316325.pdf`) timed out on fetch and could not be read — see
  Section 5.
- Note the 1.2 m minimum ranging distance. On a 350 mm robot, anything inside 1.2 m — which is exactly
  the collision-relevant zone — is **outside the ranging spec**, even though presence may still assert.

### SEN0610 — Gravity: C4001 24 GHz Presence Sensor, 12 m, I2C & UART
Confidence: **vendor-page-verified** (product page + wiki).
- Presence (stationary) detection range 8 m; motion detection range 12 m; distance measurement
  "1.2m to 12m"; speed "0.1m/s to 10m/s".
- Beam angle "100° × 80°" — **twice the vertical coverage of SEN0609** on the same C4001 module family,
  traded against maximum range. For a robot that must see a 200–500 mm tall pet from a 600–1200 mm tall
  chassis, the 80° vertical is the materially better choice of the two.
- Operating voltage "3.3V/5V"; UART 9600; I2C address "0x2A/0x2B"; size "22 × 30 mm"; Gravity PH2.0
  connector; operating temperature "-40~85℃". Operating current **not published**.
- **Published API (from `DFRobot/DFRobot_C4001`, datasheet-verified against the library source):**
  - `bool motionDetection(void)`
  - `uint8_t getTargetNumber(void)`
  - `float getTargetSpeed(void)`
  - `float getTargetRange(void)`
  - `uint32_t getTargetEnergy(void)`
  - `bool setDetectionRange(uint16_t min, uint16_t max)` — "30-2000 cm"
  - `bool setTrigSensitivity(uint8_t sensitivity)` — "0~9"
  - `bool setKeepSensitivity(uint8_t sensitivity)` — "0~9"
  - `bool setDetectThres(uint16_t min, uint16_t max, uint16_t thres)`
  - `bool setDelay(uint8_t trig, uint16_t keep)`
  - `bool setIoPolaity(uint8_t value)`, `bool setPwm(...)`, `bool setSensorMode(eMode_t)`,
    `void setSensor(eSetMode_t)`, `void setFrettingDetection(eSwitch_t)`
  - `setDetectionRange` accepting 30 cm as a minimum contradicts the product page's "1.2m" ranging floor.
    The most likely reading is that presence can be gated from 30 cm while *ranging accuracy* is only
    specified from 1.2 m, but DFRobot does not say so. Recorded as an **open question**.
  - `getTargetNumber()` exists, but whether the C4001 reports more than one simultaneous target, or only
    a count with a single dominant target's range/speed, is **not published**. Recorded as **unverified**.

### SEN0623 — C1001 60 GHz Fall Detection / Sleep Monitoring Sensor (11 m)
Confidence: **vendor-page-verified** (product page + wiki spec table + getting-started doc).
- Working voltage 5 V; working current "≤100mA"; working frequency "61~61.5GHz"; transmission power
  6 dBm; farthest detection distance 11 m; radar detection angle "100×100 degrees"; working temperature
  "-20~60℃".
- Sleep detection distance (chest) "0.4-2.5m"; breathing-and-heartbeat detection distance (chest)
  "0.4-1.5m"; breathing measurement range "10-25 times/minute"; heartbeat measurement range
  "60-100 times/minute".
- Two working modes, and the **field of view depends on the mode**: fall-detection mode requires top
  (ceiling) installation and covers "a stereoscopic fan-shaped area with a horizontal angle of 100° and
  a pitch angle of 100°"; sleep mode requires "inclined installation (downward tilt angle 30~45°)" and
  covers only "a horizontal angle of 40° and a pitch angle of 40°".
- Pinout: VIN, GND, RX, TX, "IO2 Human Presence Level Output (3.3V Fall mode active)", "IO1 Fall Status
  Level Output (3.3V Fall mode active)".
- Uses a "point cloud imaging algorithm" for posture recognition — the only DFRobot radar that claims
  any form of shape/posture classification.
- Explicit medical disclaimer: "not a certified medical device".
- Relevance: this is the closest DFRobot part to genuine human-vs-object discrimination, because it
  keys on vital signs and posture rather than gross motion. But it is specified for **ceiling mounting
  in a static indoor installation**. A 600–1200 mm robot mounts it side-on and moving, which is outside
  every published condition. Vital-sign extraction at 0.4–1.5 m from a vibrating, translating platform
  is **not supported by any published spec**. Pets are not mentioned anywhere in its documentation.

### SEN0676 — 80 GHz Liquid Level Detection Sensor (40 m)
Confidence: **vendor-page-verified** (wiki spec table).
- Frequency band "77–81GHz, 4GHz bandwidth" — the widest bandwidth and therefore the finest range
  resolution in the catalogue. Operating voltage "3.5–5V"; operating current "30mA".
- Measuring range "0.15–40m"; accuracy "±5mm"; resolution "1mm".
- Beam angle **with lens** "Horizontal ±3°, Vertical ±3°" — a pencil beam. The **without-lens figure IS
  published** on the same wiki spec table: "Horizontal ±25°, Vertical ±25°". (Corrected 2026-09-12: an
  earlier revision of this document stated the no-lens figure was not published.) Weight with the lens
  installed is "46g" — the lens is a bolt-on optic, so ±25° is the bare-module beam.
- Interface "UART (Modbus protocol)". Startup time "100ms (fastest)". Operating temperature
  "−45°C to +85°C". Module dimensions "35×35×1.2mm".
- Blind zone, baud rate, output frame format and IP rating are **not published** on the wiki page.
- Relevance: despite being the highest-performing radar silicon DFRobot sells, it is a **level gauge**.
  ±3° means a spot, not a field. Detecting a human or a pet with it would require mechanical scanning,
  and it carries zero classification. Listed for completeness, not as a candidate.

### SEN0691 — Fermion: C4002 24 GHz Motion & Static Presence Module (10 m)
Confidence: **vendor-page-verified** (product page + wiki + library source).
- "Operating Voltage: 3.6 ~ 5.5V"; "Operating Frequency: 24GHz ~ 24.25GHz"; "Operating Temperature:
  -20 ~ 85 ˚C"; "Product Dimensions: 22mm x 26mm".
- "Detection Capability: Motion, Micro-Motion/Stationary Human Body"; "Max Detection Distance: Motion
  11m, Micro-Motion/Stationary 10m"; "Detection Angle: 120° x 120°" — the **widest published field of
  view of any active DFRobot radar**, and symmetric in both axes.
- "Output Interface: OUT (Configurable IO), UART" at 115200 baud. "Light Detection: 0 ~ 50 lux" — an
  integrated ambient light sensor, unique in this catalogue.
- **Published API (from `DFRobot/DFRobot_C4002`):**
  - `getTargetState()` → "eNoTarget, ePresence, or eMotion"
  - `getPresenceTargetInfo()` → "distance: The distance of the detected target, unit: m. energy: The
    energy of the detected target, range:0-99."
  - `getMotionTargetInfo()` → "distance, speed (m/s), energy (0-99), direction"
  - `getLightIntensity()` → lux
  - `getDetectRange()` → "range: 0-1100cm"
  - `getResolutionMode()` → 80 cm or 20 cm range-gate resolution
  - plus `getLightThresh()`, `getTargetDisappearDelay()`, `getOutPinMode()`, `getSensitivity()`,
    `getDistanceGateThresh()` ("0-99"), `getPresenceCountDown()`, `getAllConfigParams()`
- **Name/spec conflict:** the product title says "(10m)", the spec table says motion 11 m / static 10 m,
  and the GitHub repository description says "side-mounted motion detection range of 11m and a static
  detection range of 11m". Three different numbers from the same vendor. Recorded as an open question.
- Operating current is **not published** anywhere including Mouser's listing.
- Relevance: the 20 cm range-gate resolution mode plus a direction bit and a 0–99 energy value makes
  this the best information-per-dollar radar DFRobot sells at $8.90. The repo's "side-mounted" phrasing
  is the only DFRobot statement that a radar is characterised for wall/side mounting rather than ceiling.

### KIT0216-EN — UNIHIKER K10 AIoT Starter Kit
Confidence: **vendor-page-verified for inclusion, unverified for identity.** The product page lists the
kit's contents as including a "mmWave Human Presence Detection Sensor" alongside a rotation sensor, LED
module, fan module, clutch servo and two TT motors. **The mmWave module's SKU is not published**, so it
cannot be cross-referenced to one of the ten radar parts above. $89.00, In Stock.

### KIT0234 — WIAnode Sensor Kit for New Media Interactive Art
Confidence: **vendor-page-verified for radar content, unverified for identity.** (Corrected 2026-09-12:
an earlier revision of this document said the bill of materials was not published and radar content was
unconfirmed. It **is** published.) `https://www.dfrobot.com/product-3110.html` lists the kit contents as:
Gesture Sensor x1, **"Millimeter Wave Sensor (Human Presence) x1"**, Ultrasonic Distance Sensor x1,
Ambient Light Sensor x1, Sound Sensor x1, Accelerometer x1, Button Module x1, Knob Module x1, 300°
Clutch Servo x1, RGB LED Strip (7 LEDs) x1, Silicone Cable Pack x1. So the kit **does** contain a
human-presence mmWave radar. As with KIT0216-EN, **the radar module's SKU is not published**, so it
cannot be cross-referenced to one of the ten radar parts above. $79.90, In Stock.

---

## 4. Cross-cutting observations

**Nothing in this catalogue tracks multiple targets in angle.** Every active DFRobot radar outputs either
a boolean, or a single dominant target's range/speed/energy, or (SEN0306) up to five obstacle ranges with
no bearing. There is no azimuth output anywhere. That means no DFRobot radar can, by itself, tell a robot
*which direction* a person is in — only that one exists somewhere inside a 100°–120° cone. Compare this
with the Hi-Link LD2450, which does output x/y per target: **DFRobot does not stock it** (0 results).

**Human-vs-pet discrimination is not offered by any product in this catalogue.** No DFRobot radar page,
wiki page, or library README mentions pets, animals, cats or dogs in either direction — neither as a
supported detection target nor as a documented false-positive source. Every "human presence" claim rests
on breathing/micro-motion signatures, which a cat or small dog also produces. Any human-vs-pet decision
must be made above the sensor, not by it.

**Every human-presence radar here is specified for a static installation.** Ranges like "stationary
target 16 m" are derived from a stationary radar observing a stationary human. On a mobile base, the
radar's own ego-motion puts Doppler energy in every range gate, and the "static presence" mode — which is
the whole reason to choose mmWave over PIR — is the first thing to break. No DFRobot page publishes any
ego-motion or platform-vibration specification.

**Frequency spread:** 5.8 GHz (retired), 10.525 GHz, 24 GHz (six parts), 61 GHz (one part), 77–81 GHz
(one part). The 24 GHz cluster is where all the price competition is: SEN0691 at $8.90, SEN0557 at $9.90,
SEN0610 at $12.90 and SEN0609 at $13.90 are all within $5 of one another and differ mainly in field of
view and output richness, while SEN0395 at $29.00 and SEN0306 at $65.90 are legacy pricing for
strictly less capable outputs.

**Field-of-view ranking (published H × V):** SEN0691 120°×120° > SEN0521 120°×120° (retired) >
SEN0623 100°×100° (fall mode, ceiling) > SEN0610 100°×80° > SEN0609 / SEN0395 100°×40° >
SEN0306 78°×23° (−3 dB half-power) > SEN0192 72°×36° (3 dB half-power) > SEN0676 ±25°×±25° without its
lens, ±3°×±3° with it. Note the two −3 dB entries are measured at half power while every "beam angle"
entry states no condition at all, so this ranking mixes two different definitions. Covering 360° around a 350 mm robot needs
three SEN0691 at 120° nominal, or four with overlap; that is $26.70–$35.60 of radar, which is the single
most useful number in this document.

**Multi-radar interference is not documented for any DFRobot radar.** No product page addresses running
two or more 24 GHz FMCW modules in proximity, which is exactly what a 360-degree ring requires. This is
the largest unanswered engineering question for this vendor and needs bench verification.

---

## 5. Coverage audit — what could not be reached, and why

1. **`https://www.farnell.com/datasheets/4316325.pdf` (SEN0609 C4001 datasheet)** — fetch timed out at
   60 s, twice-indexed but not retrieved. This is the one document likely to contain the C4001's
   operating current, antenna gain, sweep bandwidth and UART frame format. Unresolved.
2. **C4001 and C4002 silicon identity** — DFRobot publishes only its own module names. The underlying
   radar SoC vendor is not named on any product page, wiki page, library README or distributor listing
   that was read. Recorded as "not published" rather than guessed.
3. **SEN0395 chipset** — the frequently repeated "LEAPMMW" attribution does not appear in any DFRobot
   primary source. Left as not published.
4. **Operating current for SEN0609, SEN0610, SEN0691** — not published by DFRobot, Mouser, or the wiki.
5. **Vertical FoV for SEN0557 (LD2410)** — DFRobot publishes only "±60°" without stating the axis.
   Hi-Link's own datasheet would resolve this; not read in this lane.
6. **SEN0676 blind zone, baud rate, IP rating, output frame** — the wiki spec table omits them and
   directs the reader to a PDF that was not retrieved.
7. **KIT0234 radar SKU** — the bill of materials **is** published and names a "Millimeter Wave Sensor
   (Human Presence) x1", but no SKU or model number is given for it. Radar content is confirmed;
   radar identity is not. (Corrected 2026-09-12 — previously recorded here as "BOM not published".)
8. **KIT0216-EN radar SKU** — kit contents name a "mmWave Human Presence Detection Sensor" with no SKU.
9. **`search-radar.html` tail** — the page claims 41 items and renders 20 behind a lazy loader; `?p=2`
   returns page 1 again. The tail was covered instead by eleven narrower queries, all of which returned
   only products already in the table, so the radar-class set is believed complete. It is possible a
   radar product exists on dfrobot.com whose title contains none of: mmwave, mmWave, radar, microwave,
   millimeter wave, Doppler, presence detection, motion sensor, 24GHz, 60GHz, 77GHz. That is the residual
   risk and it is small.

---

## 6. Source list

- https://www.dfrobot.com/search-mmwave%20radar.html
- https://www.dfrobot.com/search-mmwave.html
- https://www.dfrobot.com/search-radar.html
- https://www.dfrobot.com/search-24GHz.html
- https://www.dfrobot.com/search-60GHz.html
- https://www.dfrobot.com/search-77GHz.html
- https://www.dfrobot.com/search-microwave.html
- https://www.dfrobot.com/search-millimeter%20wave.html
- https://www.dfrobot.com/search-presence%20detection.html
- https://www.dfrobot.com/search-motion%20sensor.html
- https://www.dfrobot.com/search-Doppler.html
- https://www.dfrobot.com/search-LD2450.html
- https://wiki.dfrobot.com/category-36/
- https://wiki.dfrobot.com/sen0192/
- https://wiki.dfrobot.com/sen0306/
- https://wiki.dfrobot.com/sen0395/
- https://wiki.dfrobot.com/sen0395/docs/21402
- https://www.dfrobot.com/product-2282.html (SEN0395)
- https://www.dfrobot.com/product-2585.html (SEN0521, retired)
- https://wiki.dfrobot.com/SKU_SEN0557_24GHz_Human_Presence_Sensing_Module
- https://www.dfrobot.com/product-2793.html (SEN0609)
- https://wiki.dfrobot.com/sen0609/
- https://www.dfrobot.com/product-2795.html (SEN0610)
- https://wiki.dfrobot.com/sen0610/
- https://wiki.dfrobot.com/SKU_SEN0610_Gravity_C4001_mmWave_Presence_Sensor_12m_I2C_UART
- https://github.com/DFRobot/DFRobot_C4001
- https://www.dfrobot.com/product-2861.html (SEN0623)
- https://wiki.dfrobot.com/sen0623/
- https://wiki.dfrobot.com/sen0623/docs/21502
- https://wiki.dfrobot.com/sen0676/
- https://www.dfrobot.com/product-3081.html (SEN0691)
- https://wiki.dfrobot.com/sen0691/
- https://github.com/DFRobot/DFRobot_C4002
- https://www.dfrobot.com/product-3108.html (KIT0216-EN)
- https://www.dfrobot.com/search-KIT0234.html (KIT0234)
- https://www.dfrobot.com/product-3110.html (KIT0234 product page — publishes the kit bill of materials)
- https://www.dfrobot.com/product-1403.html (SEN0192)
- https://www.dfrobot.com/product-1882.html (SEN0306)
- https://www.dfrobot.com/product-2648.html (SEN0557)
- https://www.dfrobot.com/product-2959.html (SEN0676)
