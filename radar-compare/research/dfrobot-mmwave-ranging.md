# DFRobot mmWave Ranging and Velocity Radars — Lane Report

**Lane:** `dfrobot-mmwave-ranging`
**Scope:** DFRobot radar modules that report *numbers* (target range, radial speed, direction, per-gate energy) rather than a bare presence bit, plus the 60 GHz posture/vital-sign class often cited for human-vs-pet discrimination.
**Target platform:** mobile robot, 350 mm square or 350 mm round footprint, 600–1200 mm tall.
**Date all prices were read:** 2026-09-12.
**Currency:** USD list price from `dfrobot.com`.

---

## 0. Correction to the lane brief, stated first

The lane brief says "SEN0609 12m, SEN0610 25m". **That is backwards.** Verified on both the DFRobot wiki and the DFRobot store:

- **SEN0609** = C4001 **25 m**, UART + OUT only, beam `100*40°`, board `26*30mm`, $13.90.
- **SEN0610** = Gravity C4001 **12 m**, I2C **and** UART, beam `100*80°`, board `22*30mm`, $12.90.

The brief also names **SEN0611**. No DFRobot SKU `SEN0611` exists in the DFRobot radar catalogue as of 2026-09-12. Searching `dfrobot.com/search-radar.html` returns SEN0192, SEN0306, SEN0395, SEN0557, SEN0609, SEN0610, SEN0676, SEN0691 — no SEN0611. **MR60BHA2 and MR60FDA2 are Seeed Studio products, not DFRobot products.** They are covered here anyway because the brief asked for them, but they are marked with their real vendor.

---

## 1. Quick verdict for a 350 mm robot

| Question | Answer |
|---|---|
| Does any DFRobot radar give usable obstacle range on a moving robot? | Only **SEN0306**, and only as a single forward-looking 1D ranger. |
| Does any give target x/y or an angle? | **No. Not one DFRobot radar in this lane reports azimuth, elevation, x/y, or a point cloud.** All are 1D range-only. |
| Does any track more than one target? | **No** for C4001 (datasheet: "This module supports up to one target only") and C4002. SEN0306 gives a raw 126-bin spectrum you can post-process into multiple targets yourself. |
| Human vs pet discrimination? | Not possible from these outputs. Best available proxy is C4002's per-gate energy plus C1001's fall/posture flag — both weak, both indoor-static-mount designs. |
| Do they survive being driven around? | **Largely no.** See section 7. This is the dominant finding of this lane. |

---

## 2. Product matrix — headline specs

| SKU | Product | Chip/band | Max range (condition) | Beam H × V | Reports | Interface | Price | Confidence |
|---|---|---|---|---|---|---|---|---|
| SEN0609 | C4001 mmWave Presence Sensor 25 m | 24 GHz FMCW (silicon not published; HW string `JYSJ_5807_A01`) | Presence 16 m; motion + ranging 25 m; ranging 1.2–25 m. **Condition: human target ("Human detection: Detection range up to 16 meters and motion detection range up to 25 meters"); 25 m needs "a significant movement" and is "depending on the target characteristics"; no RCS or reflectivity figure published** | 100° × 40° | range (m), radial speed (m/s), energy, 1 target max | UART ASCII + OUT pin | $13.90 | datasheet-verified |
| SEN0610 | Gravity C4001 mmWave Presence Sensor 12 m | 24 GHz FMCW (same family) | Presence 8 m; motion 12 m; ranging 1.2–12 m | 100° × 80° | range, speed, energy, target count 0/1 | I2C 0x2A/0x2B + UART | $12.90 | vendor-page-verified |
| SEN0691 | Fermion C4002 Motion & Static Presence | 24–24.25 GHz FMCW | Motion 11 m; micro-motion/static 10 m; configurable 0–1100 cm. **Condition: target published as "Motion, Micro-Motion/Stationary Human Body"; no RCS figure. Note the store SKU headline is "(10m)", not 11 m** | 120° × 120° | target state, presence distance + energy, motion distance + speed + direction + energy, ambient lux, per-gate energy | UART (57.6 k–1 M) + OUT pin | $8.90 | datasheet-verified (library header) |
| SEN0306 | 24 GHz Microwave Radar Distance Sensor 20 m | 24 GHz FMCW, 6 dBm typ (10 dBm max) | 0.5–20 m | 78° × 23° (−3 dB) | distance (cm) + optional 126-bin spectrum | UART 57600 8N1 | $65.90 | vendor-page-verified |
| SEN0623 | C1001 60 GHz Fall / Sleep Detection | 61–61.5 GHz, 6 dBm | 11 m presence; sleep chest 0.4–2.5 m; breath/HR chest 0.4–1.5 m | 100° × 100° | presence flag, movement, moving range, fall state, static-residency state, breath/HR | UART 115200 | $29.00 | vendor-page-verified |
| SEN0676 | 80 GHz Liquid Level Radar 40 m | 77–81 GHz, 4 GHz bandwidth | 0.15–40 m | ±25° × ±25° (±3° with lens) | level distance, ±5 mm accuracy, 1 mm resolution | UART Modbus | $59.00 | vendor-page-verified |
| (Seeed) | MR60BHA2 Breathing & Heartbeat | **ADT6101P**, 57–64 GHz FMCW, 2T2R | breath/HR chest 0.4–1.5 m | ±60° × ±60° (−3 dB) | has_target, num_targets, distance, breath_rate, heart_rate | UART | not a DFRobot SKU | datasheet-verified |
| (Seeed) | MR60FDA2 Fall Detection | **ADT6101P**, 57–64 GHz FMCW, 2T2R | fall detection radius **2 m max**. **Condition published: "The detection range of the radar module is closely related to the target RCS and environmental factors... it is normal for the effective detection range to fluctuate within a certain range"** | ±60° × ±60° (−3 dB) | fall flag, presence | UART | not a DFRobot SKU | **beta**-datasheet-verified |

---

## 3. SEN0609 / SEN0610 — the C4001 family, in detail

### 3.1 What the datasheet actually says about ranging accuracy

This is the single most important quote in the lane, taken verbatim from the DFRobot C4001 datasheet (`dfimg.dfrobot.com/wiki/20522/SEN0609_..._datasheet_V1.pdf`, section 1.1):

> "Note: The C4001 millimeter wave presence sensor is **not specifically designed for distance measurement**. The distance is currently **not calibrated** in the current version, so the distance can only be used as a **reference** and may have some **deviation or error**."

DFRobot therefore publishes **no range accuracy and no range resolution for the C4001 at all**. Do not treat the `$DFDMD` distance as a metrology-grade number. The I2C transport carries it as a signed int16 in centimetres (library divides by 100.0), so the *transport* quantum is 1 cm — that is a bus quantum, not an accuracy figure, and quoting it as accuracy would be wrong.

### 3.2 The "1 m transition zone"

Verbatim from the same section:

> "The C4001 millimeter wave presence sensor module has a 1m transition zone, which means that if the maximum detection distance is set to 3 meters, it is possible to detect targets between 3~25 meters. When approaching 25 meters, a significant movement is required to be detected, and it is also possible that the target cannot be detected at the 25-meter position (depending on the target characteristics). However, no targets will be detected beyond 25 meters, such as 27 meters. Therefore, users need to pay special attention to this feature when configuring the maximum distance parameter in order to accurately define the detection area."

**Correction (adversarial re-check, 2026-09-12): an earlier revision of this file quoted only the first sentence of that passage.** The truncation mattered. The two clauses it dropped are the only measurement conditions DFRobot publishes for the 25 m figure anywhere: detection at 25 m requires *"a significant movement"* and is *"depending on the target characteristics"*, and 25 m is a **hard ceiling**, not a soft one. So the 25 m number is a best-case, large-motion, favourable-target figure — quote it that way or not at all.

So `setRange 0.6 3` does **not** produce a hard 3 m cutoff. Targets beyond the set maximum still get reported, with decreasing probability, out to the module's physical 25 m — where the detection then stops hard. For a 350 mm robot that wants "anything inside 1.5 m is a collision risk", this is a serious problem: you cannot bound the detection volume tightly in software, so a person standing 4 m away can still latch the single target slot and mask a chair leg at 0.9 m.

### 3.3 Velocity — three published numbers that disagree

| Source | Velocity spec |
|---|---|
| C4001 25 m datasheet, "Characteristics" list | "Velocity detection: Range from 0.1 meters per second to **3** meters per second." |
| Same datasheet, `$DFDMD` par4 definition | "Target speed, in meters per second (m/s): Range: **0–10** m/s" |
| `dfrobot.com/product-2793.html` (SEN0609) and `product-2795.html` (SEN0610) | "Velocity Measurement: 0.1 m/s to **10** m/s" |

**Velocity resolution is not published.** The I2C path returns a signed int16 in cm/s, so the transport quantum is 0.01 m/s and the sign carries approach/recede direction. Again: transport quantum, not measured resolution. Treat the 0.1 m/s lower bound as the real floor — below it the target is classified as static/micro-motion, not as a slow-moving target, which matters because a cat walking at 0.3 m/s and a human shuffling at 0.15 m/s both sit near that floor.

### 3.4 Target capacity

Verbatim, `$DFDMD` par1: *"Number of targets: 0: No target detected / 1: One target detected / **This module supports up to one target only**."*

One target. No arbitration rule is published for which target wins when two are in the beam — presumably highest energy. On a robot, the highest-energy return will very often be a wall, not the person.

### 3.5 Complete UART command set (C4001, ASCII, CR/LF terminated)

Serial framing per datasheet: 1 stop bit, 8 data bits, no parity, no flow control. The datasheet protocol section states *"Default baud rate: 115200 bps"* while the same document's spec table and the `setUart` default both say **9600**. The Arduino library defaults to 9600. **Assume 9600 and be ready to probe 115200** — an unresolved vendor contradiction.

Configuration commands (module must be stopped with `sensorStop` first, then `saveConfig`, then `sensorStart`):

| Command | Parameters | Range / default | Mode |
|---|---|---|---|
| `setRange p1 p2` / `getRange` | min, max detection distance in m | p1 0.6–25, default 0.6 (not recommended to modify); p2 p1<p2≤25, default 6 | both |
| `setTrigRange p1` / `getTrigRange` | trigger distance in m | 0–25, default 6 | presence only |
| `setSensitivity p1 p2` / `getSensitivity` | hold, trigger sensitivity | each 0–9; hold default 7, trigger default 5; pass 255 to leave one unchanged | presence only |
| `setLatency p1 p2` / `getLatency` | confirm delay, disappear delay, in s | p1 0–100 (default 0.050 s); p2 0.5–1500 (default 15 s) | presence only |
| `setInhibit p1` / `getInhibit` | blocking time in s | 0.1–255, default 1 | presence only |
| `setUart p1` / `getUart` | baud | 4800–115200, default 9600; needs `resetSystem 0` to take effect | both |
| `setMicroMotion p1` / `getMicroMotion` | micro-motion switch | 0 disable (default), 1 enable | **speed/ranging mode only** |
| `setThrFactor p1` / `getThrFactor` | CFAR-style threshold factor | default 5; "the larger the factor, the bigger the action and the larger the object that can be detected" | **speed/ranging mode only** |
| `setUartOutput` | report enable / period / query mode | referenced by datasheet, parameters not tabulated | both |

Control commands: `sensorStop`, `sensorStart` (or `sensorStart 1` to resume prior state), `saveConfig`, `resetCfg` (factory defaults), `resetSystem 0|1` (0 = normal restart, 1 = bootloader), `setRunApp 0|1` (**0 = presence detection mode, 1 = speed and distance measurement mode — these are mutually exclusive**), `getHWV`, `getSWV`.

Active reporting:

- Presence mode: `$DFHPD,par1, , , *` — par1 is `0` no person / `1` person. Three reserved placeholders.
- Ranging mode: `$DFDMD,par1,par2,par3,par4,par5, , *` — count, target id, distance (m), speed (m/s), energy. Example verbatim from the datasheet: `$DFDMD,1,1,1.817,0.129,15304, , *`.

Note the mode exclusivity: **you cannot have presence detection and ranging at the same time.** `setRunApp` switches between them, and switching requires a stop/save/start cycle. A robot that wants both "is a human near me" and "how far is the nearest thing" needs two C4001s.

### 3.6 Complete I2C register map (SEN0610, address 0x2A or 0x2B)

Extracted verbatim from `DFRobot/DFRobot_C4001` → `src/DFRobot_C4001.h`.

Common:

| Register | Address |
|---|---|
| `REG_STATUS` | 0x00 |
| `REG_CTRL0` | 0x01 |
| `REG_CTRL1` | 0x02 |
| `REG_SOFT_VERSION` | 0x03 |
| `REG_RESULT_STATUS` | 0x10 |

Presence-mode config:

| Register | Address |
|---|---|
| `REG_TRIG_SENSITIVITY` | 0x20 |
| `REG_KEEP_SENSITIVITY` | 0x21 |
| `REG_TRIG_DELAY` | 0x22 |
| `REG_KEEP_TIMEOUT_L/H` | 0x23 / 0x24 |
| `REG_E_MIN_RANGE_L/H` | 0x25 / 0x26 |
| `REG_E_MAX_RANGE_L/H` | 0x27 / 0x28 |
| `REG_E_TRIG_RANGE_L/H` | 0x29 / 0x2A |

Ranging-mode result and config:

| Register | Address |
|---|---|
| `REG_RESULT_OBJ_MUN` | 0x10 |
| `REG_RESULT_RANGE_L/H` | 0x11 / 0x12 |
| `REG_RESULT_SPEED_L/H` | 0x13 / 0x14 |
| `REG_RESULT_ENERGY_L/H` | 0x15 / 0x16 |
| `REG_CFAR_THR_L/H` | 0x20 / 0x21 |
| `REG_T_MIN_RANGE_L/H` | 0x22 / 0x23 |
| `REG_T_MAX_RANGE_L/H` | 0x24 / 0x25 |
| `REG_MICRO_MOTION` | 0x26 |

Mode bytes (`eSetMode_t`): `eStartSen 0x55`, `eStopSen 0x33`, `eResetSen 0xCC`, `eRecoverSen 0xAA`, `eSaveParams 0x5C`, `eChangeMode 0x3B`.

Decoding, verbatim from `DFRobot_C4001.cpp` `getTargetNumber()`:

```
_buffer.range  = (float)( int16_t((uint16_t)(temp[1] | ((uint16_t)temp[2]) << 8))) / 100.0;
_buffer.speed  = (float)( int16_t((uint16_t)(temp[3] | ((uint16_t)temp[4]) << 8))) / 100.0;
_buffer.energy = (uint16_t)(temp[5] | ((uint16_t)temp[6]) << 8);
```

So range is signed int16 cm, speed is signed int16 cm/s. **The sign of speed is your approach/recede bit** — the only kinematic discriminator the C4001 gives you.

There is also a debounce in the library that you must know about: the target-lost path only clears `number` after `flash_number++ > 10`, i.e. roughly ten consecutive empty polls. A robot braking on "target gone" will lag by ten poll periods.

### 3.7 API caps that disagree with the product page

The library header documents `setDetectionRange(min, max, trig)` as *"min ... range 0.3~20m (30~2000)"* and *"max ... range 2.4~20m (240~2000)"*. That is **20 m, not 25 m**, even though SEN0609 is sold as a 25 m part. `DFRobot_C4001.cpp::setDetectThres()` rejects only `max > 2500`. So the library's documented cap (2000) and its enforced cap (2500) disagree with each other and with the 25 m product claim. Verify empirically before relying on anything beyond 20 m.

`setDetectThres(min, max, thres)`: threshold is *"dimensionless unit 0.1, range 0~6553.5 (0~65535)"*. This is the CFAR threshold behind `REG_CFAR_THR`. It is the knob you would use to suppress low-RCS clutter — and, unavoidably, low-RCS pets.

---

## 4. SEN0691 / C4002 — the most robot-useful DFRobot 24 GHz part

$8.90, and despite being the cheapest it produces by far the richest data structure. Verified from `DFRobot/DFRobot_C4002` → `src/DFRobot_C4002.h`.

**Specs:** 3.6–5.5 V, 24–24.25 GHz FMCW, detection angle 120° × 120°, motion 11 m, micro-motion/stationary 10 m, ambient light sensor 0–50 lux, −20 to 85 °C, 22 × 26 mm. Current consumption **not published**.

**Range condition, verified 2026-09-12:** the DFRobot wiki spec table names the detection target explicitly — *"Motion, Micro-Motion/Stationary Human Body"*. So unlike the C4001, the C4002's 11 m / 10 m figures *are* scoped to a human body; what is still missing is any RCS, target-size or aspect condition. Do not read 11 m as a range against a chair leg or a cat. Note also that DFRobot's own store title for SEN0691 is *"Fermion: C4002 mmWave Human Presence Sensor - Static & Motion Detection for Home Assistant (10m)"* — **the SKU headline says 10 m while the wiki spec says motion 11 m**. Unresolved vendor inconsistency; plan against 10 m.

**What it reports per frame** (`getNoteInfo()` → `sRetResult_t`):

- `targetState`: `eNoTarget` 0, `ePresence` 1, `eMotion` 2 (plus OUT-pin combination states 3–5)
- ambient light in lux
- **presence target**: `distance` in m, `energy` 0–99
- **motion target**: `distance` in m, `speed` in m/s, `energy` 0–99, `direction` ∈ {`eAway` 0, `eNoDirection` 1, `eApproaching` 2}
- presence countdown in s
- `getPresenceGateIndex()` — a 32-bit mask of which range gates are occupied

**Range gates — the genuinely useful feature.** `setResolutionMode()` picks `eResolution80Cm` or `eResolution20Cm`. Per the header:

> "When the resolution mode is 80cm, 0 to 15 bits may be set to 1 to represent the presence of the target. When the resolution mode is 20cm, 0 to 25 bits may be set to 1."

So: **16 gates × 0.80 m = 12.8 m of gate span**, or **26 gates × 0.20 m = 5.2 m of gate span**.

**Correction (adversarial re-check, 2026-09-12): "12.8 m coverage" is arithmetic, not a capability, and an earlier revision of this file presented it as a capability.** Two published limits sit below it. `setDetectRange(closest, farthest)` is capped at **1100 cm**, and the wiki spec is **motion 11 m / micro-motion 10 m** against a human body. The 80 cm mode therefore cannot deliver 12.8 m of usable detection: gates above index 13 (≈11.2 m) lie outside both the configurable window and the specified range. Read the 80 cm mode as **≤11 m of usable span in 16 gates**, and treat the top one or two gates as unspecified. The 20 cm mode's 5.2 m span sits well inside every published limit and is unaffected.

The 20 cm mode is the interesting one for a robot — 20 cm range bins out to 5.2 m is a coarse 1D occupancy vector, and `setGateThresh(gateType, thresh[])` lets you set a **per-gate threshold 0–99** independently for motion gates and presence gates.

That per-gate threshold array is the closest thing in this entire lane to a mechanism for tolerating a moving platform: you can blind the first two or three gates (0–60 cm) so the robot's own shell and its own bumper hardware stop dominating the CFAR window, without giving up sensitivity at 1–3 m.

**Other configuration:** `setDetectRange(closest, farthest)` in cm, 0–1100; `setReportPeriod(0–255)` in units of 0.1 s (so 0.1–25.5 s per report — this is a *slow* sensor by default and the header gives **no maximum frame rate**); `setLockTime(0.2–10 s, 0.1 s steps)` during which detection is disabled after occupied→unoccupied; `setTargetDisappearDelay(0–65535 s)`; `startEnvCalibration(delayTime, contTime)` in seconds; `setLightThresh(0–50 lux)`; UART baud selectable 57600 / 115200 / 230400 / 460800 / 500000 / 921600 / 1000000, with the header warning *"The baud rate should not be too high; otherwise, it will lead to data loss."*

**`startEnvCalibration()` is the trap.** It learns a static background so that furniture stops reading as presence. That calibration is valid for exactly one pose of the sensor. A robot that drives invalidates it continuously. See section 7.

---

## 5. SEN0306 — the only real ranging radar DFRobot sells

$65.90, five times the price of a C4001, and it is the only DFRobot 24 GHz part that publishes ranging performance.

| Parameter | Value (condition) |
|---|---|
| Measurement range | 0.5–20 m |
| **Ranging accuracy** | **±0.1 m** (condition not stated) |
| **Range resolution** | **0.01 m** |
| Frequency / modulation | 24 GHz, FMCW |
| Transmit power | 6 dBm typical, 10 dBm max |
| Beam width | **78° horizontal, 23° vertical, both at −3 dB** |
| Update rate | 10 Hz |
| Supply | 4–8 V DC, **>100 mA** |
| Logic | 3.3 V TTL, UART 57600, 8 data bits, 1 stop, no parity |
| Size / mass | 34 × 44 × 5 mm, 8 g |
| Temperature | 0–70 °C operating (note: **not** the −40/85 °C of the C4001) |

**Output frame.** Header `0xFF 0xFF 0xFF`, then 16-bit distance in **centimetres**, high byte first. If the mode pin (pin 6) is tied to ground, the frame continues with **126 spectral line amplitudes, each in the range 1–44**, then a tail.

That 126-bin spectrum is the only raw radar data any DFRobot part exposes. DFRobot's own wording, verbatim from `wiki.dfrobot.com/sen0306/docs/20390`: *"After post-processing, users can use these spectral lines to realize mutilple targets detection."* (vendor's spelling). The same wiki also claims the module *"can detect up to 5 obstacles"* — that is a vendor claim about what the spectrum supports after your own peak-finding, **not** a reported target list on the wire. The wire gives one distance plus the spectrum. In other words, DFRobot ships you a range-FFT magnitude vector and tells you to do your own CFAR. For a robot this is the correct primitive — you can implement your own ego-motion-aware detector instead of fighting a black-box presence algorithm. It is also the only part here where you can see a static wall and a moving person in the same frame and separate them yourself.

The 78° × 23° beam is well matched to a robot: wide enough in azimuth to cover a sector, narrow enough in elevation that floor and ceiling multipath is reduced. Mounted at 300–400 mm on a 600–1200 mm robot, a 23° vertical beam illuminates roughly 0.4 m of height at 1 m and 2.0 m at 5 m, which covers a cat's body at short range and a standing human's torso at medium range.

**Weaknesses:** >100 mA is 3–6× the power of the alternatives, 0–70 °C rules out cold outdoor use, and the 10 Hz update rate gives only one measurement per 5 cm of travel at 0.5 m/s. There is no velocity output — you would differentiate range yourself, which on a moving base is exactly the wrong thing to do.

---

## 6. 60 GHz posture / vital-sign class — and why it fails on this robot

### 6.1 SEN0623 / C1001 (DFRobot, $29.00)

| Parameter | Value |
|---|---|
| Supply | 5 V, **≤100 mA** |
| Frequency | **61–61.5 GHz** (0.5 GHz band, not the full 57–64) |
| Transmit power | 6 dBm |
| Max detection distance | 11 m |
| Detection angle | 100° × 100° |
| Sleep detection (chest) | 0.4–2.5 m |
| Breath / heart rate (chest) | **0.4–1.5 m** |
| Breath measurement range | 10–25 breaths/min |
| Heart rate measurement range | 60–100 bpm |
| Operating temperature | −20 to 60 °C |
| UART | 115200 8N1 |
| Optimal fall-detection mount | **ceiling, 2.7 m, sensor facing straight down** |

DFRobot markets it with *"point cloud imaging algorithm"* — the algorithm is internal. **The published API exposes no point cloud and no coordinates.** The `DFRobot_HumanDetection` API surface is:

`configWorkMode(eFallingMode | eSleepMode)` — mutually exclusive; `dmInstallHeight(cm)`; `dmFallTime(s)`; `dmUnmannedTime(s)`; `dmFallConfig(eResidenceTime | eFallSensitivityC, value)` with fall sensitivity **0–3**; `smHumanData(eHumanPresence | eHumanMovement | eHumanMovingRange)`; `getFallData(eFallState | eStaticResidencyState | eFallSensitivity)`; `getStaticResidencyTime()`; `configLEDLight()`; `sensorRet()`.

That is: a presence bit, a movement class, a "moving range" scalar, and a fall bit. No x, no y, no z, no azimuth, no target list. The DFRobot wiki FAQ adds two disqualifying statements: *"the C1001 can only detect if an object is moving"*, and it **cannot count multiple individuals** in a space.

**Verdict for a 350 mm robot: unusable.** The fall function is defined relative to a 2.7 m ceiling mount pointing down. Mounted at 0.3–1.0 m on a moving robot the geometry that the fall algorithm assumes does not exist, and `dmInstallHeight()` will not fix that — the algorithm thresholds point-cloud height above floor, which on a horizontally-mounted forward-looking radar is meaningless. The 0.4–1.5 m vital-sign window is also the window in which the robot is already about to collide.

### 6.2 MR60BHA2 and MR60FDA2 (Seeed Studio, not DFRobot)

Both are built on the **ADT6101P**: *"monolithically integrates a 57~64GHz radio frequency transceiver system, 2T2R PCB microstrip antenna, 1MB flash, radar signal processing unit, and ARM Cortex-M3 core."* Module 25 × 31.5 mm.

| Parameter | MR60BHA2 | MR60FDA2 |
|---|---|---|
| Working frequency | 58–62 GHz (min 58, max 62) | 58–62 GHz |
| Transmit power | 12 dBm typ | 12 dBm typ |
| Antenna gain | 4 dBi | 4 dBi |
| Horizontal beam (−3 dB) | ±60° | ±60° |
| Vertical beam (−3 dB) | ±60° | ±60° |
| Operating voltage | 3.1 / 3.3 / 3.5 V | 3.1 / 3.3 / 3.5 V |
| Operating current | ICC table **max 600 mA**; Precautions demand a supply of **≥1 A** | ICC table **max 600 mA**; Precautions demand a supply of **≥1 A** |
| Function | breath/HR chest 0.4–1.5 m, breath accuracy **90 % typical** | **fall detection radius max 2 m**, fall recognition accuracy **90 % typical** |
| Mounting | — | **top-mounted, hanging height 2.2–3.0 m**, "maximum sensing radius 2m" |

**Correction (adversarial re-check, 2026-09-12): an earlier revision of this file gave the MR60 power budget as "600 mA max" only.** That is the ICC row of section 4.2. Section 7 (Precautions) of the same datasheet says something harder, verbatim:

> "The radar module has extremely high power requirements, requiring an input voltage of 3.1~3.5V, power supply ripple ≤50mV, and current ≥1A. If a DCDC power supply is used, the switching frequency is required to be no less than 2MHZ."

**Budget ≥1 A at 3.3 V with ≤50 mV ripple, not 600 mA.** On a battery robot that is the difference between a shared rail and a dedicated regulator. The two numbers are a vendor contradiction; the Precautions figure is the design-safe one.

**Document-quality warning.** The MR60FDA2 file is titled *"Fall detection module technical specifications (Beta Version)"*, Revision History `V1.0 / 2024/03/05 / Beta version`, and its own section 1 opens *"MR60FDC1 is a radar sensing module developed based on the ADT6101P chip"* — a **different part number from the one on the cover**. Treat every MR60FDA2 number here as beta-grade and unconfirmed against a released datasheet.

The ESPHome `seeed_mr60bha2` component exposes exactly five entities: `has_target`, `breath_rate`, `heart_rate`, `distance`, `num_targets`. **No x/y/z.** `distance` is documented as *"straight-line distance between the radar and the monitoring object"* — 1D again.

**Verdict: unusable on this robot.** MR60FDA2's 2 m sensing radius and 2.2–3.0 m ceiling requirement are structural, not tunable. 600 mA max is also a real battery cost. The datasheet even warns that any radome *"will cause the antenna beam to be distorted"* and *"may cause receiver saturation"* — relevant because a robot shell *is* a radome.

### 6.3 SEN0676 — 80 GHz, and the one with real precision

77–81 GHz, **4 GHz chirp bandwidth** — the only module in this lane with a published bandwidth, and the reason it achieves **±5 mm accuracy and 1 mm resolution over 0.15–40 m**. Beam ±25° × ±25°, or ±3° × ±3° with the optional lens. 3.5–5 V at 30 mA. UART Modbus. 35 × 35 × 1.2 mm, 5 g bare / 46 g with lens.

Physics note worth stating plainly: range resolution ≈ c / (2 × B). At 4 GHz bandwidth that is 37.5 mm of native resolution; the quoted 1 mm is interpolated sub-bin precision on a single dominant specular return, which is what a liquid surface gives you. **A human body does not give you that return.** This part is a level gauge; it is designed for one flat perpendicular reflector at a known bearing. It will not behave like a 1 mm obstacle detector pointed at a room. The ±3° lens version is however genuinely interesting as a single forward "is the floor still there / is there a wall at X" beam.

---

## 7. The ego-motion problem — the central issue, and what the vendors do not say

Every DFRobot 24 GHz presence part in this lane is architecturally a **static-mounted indoor occupancy sensor**. The consequences of bolting one to a moving 350 mm robot are specific and severe.

### 7.1 Why a moving platform breaks these sensors

An FMCW presence radar separates "person" from "furniture" by Doppler. Anything with zero radial velocity is background; anything with non-zero radial velocity is a candidate target. When the radar itself translates at velocity `v`, every static scatterer in the scene acquires an apparent radial velocity of `−v·cos(θ)`, where θ is the angle between the robot's heading and the bearing to that scatterer. Three things follow:

1. **The whole room becomes a moving target.** Walls, doorframes, table legs and the floor all enter the Doppler passband. The C4001's single target slot will be captured by whichever static object has the highest energy — usually a wall — not by the human.
2. **A standing human becomes invisible in exactly the worst case.** A person standing still directly ahead of a robot moving at `v` has an apparent radial velocity of `−v`. A wall directly ahead has the *same* apparent radial velocity, `−v`. They are Doppler-identical. Any static-clutter rejection tuned on `v = 0` either passes both or rejects both. This is the answer to the brief's question, and the answer is: **yes, static-clutter rejection on these parts does make them unreliable for a standing human while the robot drives — not because the human is filtered out specifically, but because the human's Doppler signature becomes indistinguishable from the clutter's.**
3. **Angle-blind sensors cannot compensate.** The standard fix in radar odometry is to fit the `v·cos(θ)` curve across azimuth, solve for ego-velocity, and subtract it. **That requires azimuth. No DFRobot part in this lane reports azimuth.** With a single range-Doppler pair and no bearing, there is no closed-form ego-motion compensation available. You would need external odometry to even guess at `v`, and you still could not separate two targets at the same range with different bearings.

### 7.2 Vendor features that actively make this worse

- **C4002 `startEnvCalibration()`** learns the static background for one pose. Driving invalidates it. Re-running it while moving learns the motion, not the room.
- **C4001 `setInhibit`** (default 1 s) suppresses detection for up to 255 s after each OUT transition, specifically to ride out relay/motor interference. On a robot with drive motors, the temptation is to raise it — and every second of inhibit is a second of blindness at walking speed.
- **C4001 `setLatency` disappearance delay** defaults to **15 s**. Fifteen seconds of latched "person present" on a vehicle that has already driven 7 m.
- **C4001 `setTrigRange`** and the **1 m transition zone** together mean the detection volume has soft, non-deterministic edges — bad for any safety envelope.
- **C4002 `setLockTime`** disables detection for 0.2–10 s after every occupied→unoccupied transition, which on a moving platform will fire constantly.
- **C4002 `setReportPeriod`** minimum is 0.1 s. At 0.5 m/s that is 5 cm per frame at best, and the default example in DFRobot's own code is `setReportPeriod(10)` = **1 second**.
- The **C4001 library's 10-poll debounce** before clearing a lost target adds further lag.

### 7.3 Mounting on a 350 mm robot

| Consideration | Guidance |
|---|---|
| Height for obstacle detection | 150–250 mm. A cat 200–500 mm tall and a chair leg both intersect this band. Below 150 mm the floor enters the main lobe and dominates. |
| Height for human detection | 900–1100 mm (torso). On a 600 mm robot this is unreachable; on a 1200 mm robot it is the top plate. |
| Vertical beam and the floor | SEN0306's 23° vertical beam is the only one narrow enough to keep the floor out of the main lobe at short range. The C4001 25 m at 40° and the C4002 at 120° will both illuminate the floor within 1 m and get a strong specular return. The C4001 12 m at 80° and C1001 at 100° are worse. |
| Radome | Mount behind ABS/PC/PP, thickness tuned near a half-wavelength multiple (≈6.25 mm at 24 GHz, ≈2.5 mm at 60 GHz). **No metal, no carbon fill, no metallic paint.** Seeed's datasheet warning about radome-induced beam distortion, isolation loss and receiver saturation applies to every part here. |
| 360° coverage | With 100–120° azimuth beams, three C4002s at 120° spacing nominally covers 360°. But all three are monostatic 24 GHz FMCW with no published sync or interference-avoidance mechanism — **multi-sensor interference behaviour is not published for any DFRobot radar in this lane**, and co-located same-band FMCW radars routinely ghost each other. Unverified and high risk. |
| Power budget | C4001/C4002 current **not published** — plan a measurement. C1001 ≤100 mA. SEN0306 >100 mA. SEN0676 30 mA. MR60xx: ICC table says 600 mA max, but the datasheet's own Precautions section requires a **≥1 A supply at 3.1–3.5 V with ≤50 mV ripple**. Budget 1 A. |

### 7.4 Human vs pet vs inanimate — the honest assessment

Nothing in this lane discriminates. The available signals are: range, signed radial speed, a scalar "energy", and (C4002 only) a 16- or 26-element gate occupancy mask.

- **Energy** is RCS-dominated, and RCS varies with aspect, clothing, and wetness more than with species. A human in a wool coat and a cat on a tile floor can produce comparable returns.
- **Speed** overlaps completely: a cat walks at 0.3–1.0 m/s, a human at 0.5–1.5 m/s.
- **Height** is the one feature that *would* separate a 200–500 mm pet from a 1500–1900 mm human, and **no DFRobot radar here reports elevation.** Two radars at different heights with different elevation tilts could infer it crudely, and the C4002's per-gate masks would let you compare gate occupancy between the two units at the same range. That is a build-it-yourself feature, not a product feature, and it is not verified.
- **C1001's fall state** is the only posture-aware output, and it is geometrically locked to a 2.7 m downward ceiling mount.

---

## 8. Recommendation for this robot

1. **If you buy one DFRobot radar for this robot, buy SEN0691 (C4002, $8.90)** — for the 20 cm gate mode, the per-gate thresholds (mask out your own chassis), the approach/recede direction bit, and the price. Accept that it is a 1D sensor, that env-calibration is worthless while driving, and set `setReportPeriod(1)` for 10 Hz rather than DFRobot's example default of 1 Hz.
2. **If you need real range numbers, buy SEN0306 ($65.90)** and use the 126-bin raw spectrum with your own CFAR fused to wheel odometry. It is the only part in the DFRobot catalogue that lets you do ego-motion compensation at all, because it is the only one that gives you pre-detection data.
3. **Do not buy C4001 (SEN0609/SEN0610) for ranging.** DFRobot's own datasheet disclaims the distance output as uncalibrated and reference-only, it tracks one target, and its presence and ranging modes are mutually exclusive.
4. **Do not buy C1001, MR60BHA2 or MR60FDA2 for this robot.** All three are ceiling-mounted static-installation products whose core algorithms assume a fixed downward geometry the robot cannot provide.
5. **Do not rely on radar alone for pets.** Radar in this price class gives range and radial speed. Height discrimination — the feature that actually separates a cat from a person — needs a multi-zone ToF array or a thermal array, which belong to other lanes.

---

## 9. Fields DFRobot does not publish for any part in this lane

Recorded explicitly so no downstream reader assumes these were missed rather than absent:

- **Operating current** for SEN0609, SEN0610, SEN0691 — not published anywhere on the wiki, product page or datasheet.
- **FMCW chirp bandwidth** for every 24 GHz part (C4001, C4002, SEN0306). Only SEN0676 publishes one (4 GHz at 77–81 GHz).
- **Range resolution and range accuracy** for C4001 and C4002. SEN0306 publishes ±0.1 m / 0.01 m.
- **Velocity resolution** for every part.
- **Maximum frame/update rate** for C4001 and C4002. SEN0306 publishes 10 Hz.
- **Azimuth or elevation of the target** — not reported by any part.
- **Multi-sensor interference behaviour** — not addressed by any DFRobot document found.
- **Behaviour on a moving platform** — not addressed by any DFRobot document found.
- **Silicon part number** for C4001, C4002 and SEN0306. The C4001 reports `HardwareVersion:JYSJ_5807_A01` and `SoftwareVersion:JYSJ_02.08.08.010827`; the vendor prefix `JYSJ` is not resolved to a public silicon datasheet. Only the Seeed MR60 modules name their chip (**ADT6101P**).

---

## 10. Adversarial verification log — 2026-09-12

Every headline number below was re-checked against the manufacturer datasheet PDF or the vendor product page, not against a reseller listing.

| Claim | Verdict | Primary source checked |
|---|---|---|
| SEN0609 25 m motion + ranging, 16 m presence, 1.2–25 m, 100° H, $13.90, 1 target | **MISLEADING** — every number confirmed, but the transition-zone quote was truncated. Datasheet adds "a significant movement is required", "depending on the target characteristics", and a hard ceiling "no targets will be detected beyond 25 meters". Fixed in §3.2. | `dfrobot.com/product-2793.html`; SEN0609 datasheet V1 §Characteristics, §Technical Specifications, §1.1 |
| SEN0610 12 m motion, 8 m presence, 1.2–12 m, 100° H, $12.90, 1 target | **CONFIRMED** verbatim: "Maximum Detection Range: 12m", "presence detection range of 8 meters", "motion detection and ranging range of 12 meters", "can measure distances from 1.2m to 12m", "Beam Angle: 100*80°", $12.90 | `dfrobot.com/product-2795.html` |
| SEN0691 motion 11 m, static 10 m, 0–1100 cm window, 120° H, $8.90, 16×80 cm or 26×20 cm gates, per-gate threshold 0–99 | **MISLEADING** — gate counts, window and threshold confirmed in `DFRobot_C4002.h`; 11 m/10 m/120° confirmed on wiki; $8.90 confirmed in catalogue. But "16 gates × 0.80 m = 12.8 m of coverage" exceeds both the 1100 cm config cap and the 11 m spec. Also the target condition **is** published ("Motion, Micro-Motion/Stationary Human Body"), and the store SKU headline says "(10m)". Fixed in §2 and §4. | `wiki.dfrobot.com/SKU_SEN0691_...`; `DFRobot_C4002.h`; `dfrobot.com/search-radar.html` |
| SEN0306 20 m, 78° H at −3 dB, $65.90, 126-bin spectrum | **CONFIRMED** — "0.5-20m", "78（-3db）" H / "23（-3db）" V, "±0.1m", "0.01m", "10Hz", $65.90; "The first three Oxff are data headers", 126 spectral lines, "The amplitude ranges from 1 to 44". Reflectivity condition genuinely not published. Added the vendor's "up to 5 obstacles" claim and its correct scope in §5. | `dfrobot.com/product-1882.html`; `wiki.dfrobot.com/sen0306/`; `wiki.dfrobot.com/sen0306/docs/20390` |
| SEN0623 11 m presence, sleep 0.4–2.5 m, breath/HR 0.4–1.5 m, 100° H, $29.00, no zones | **CONFIRMED** — "11m", "100×100 degrees", "0.4-2.5m", "0.4-1.5m", "10-25 breaths per minute", "60-100 beats per minute", 2.7 m ceiling mount, $29.00 | `dfrobot.com/product-2861.html` |
| SEN0676 40 m against a liquid surface, ±25° standard / ±3° with lens, $59.00 | **CONFIRMED** — "0.15–40m", "±5mm", "1mm", "77–81GHz, 4GHz bandwidth", "Horizontal ±25°, Vertical ±25°", lens "±3°", "30mA", $59.00. Non-liquid target behaviour genuinely not addressed. | `wiki.dfrobot.com/sen0676/`; `dfrobot.com/search-radar.html` |
| MR60BHA2 breath/HR chest 0.4–1.5 m, ±60° at −3 dB, not a DFRobot SKU | **CONFIRMED** — §4.1 "Breathing and heartbeat detection distance (chest)" min 0.4 max 1.5 m; §4.3 horizontal and vertical beam (−3 dB) −60/+60°; 58–62 GHz, 12 dBm, 4 dBi, ICC max 600 mA. **No human-presence range appears anywhere in the datasheet** — the 6 m figure is not vendor-datasheet material. Accuracy corrected from "≥90%" to "90 % typical". | MR60BHA2 datasheet §4.1–4.3 |
| MR60FDA2 fall radius max 2 m, RCS caveat, ±60°, not a DFRobot SKU | **CONFIRMED** — §4.1 "Fall detection detection radius" maximum 2 m; §6.4 "Top-mounted hanging height 2.2-3.0m, maximum sensing radius 2m"; §7 Precautions carries the RCS sentence verbatim. Two defects found in this file instead: the 600 mA figure understates the datasheet's own "current ≥1A" requirement, and the document is a **Beta Version** whose §1 names the part "MR60FDC1". Both fixed in §6.2 and §7.3. | MR60FDA2 datasheet §4.1, §4.2, §6.4, §7, Revision History |

**Catalogue state on 2026-09-12.** `dfrobot.com/search-radar.html` lists exactly eight radar SKUs — SEN0192, SEN0306, SEN0395, SEN0557, SEN0609, SEN0610, SEN0676, SEN0691 — **all shown In Stock, none marked discontinued, EOL or retired**. `SEN0611` does not exist, as stated in §0. MR60BHA2 and MR60FDA2 are Seeed Studio parts and correctly carry no DFRobot price.

---

## Sources

- [SEN0609 C4001 mmWave Presence Sensor 25m — DFRobot Wiki](https://wiki.dfrobot.com/SKU_SEN0609_C4001_mmWave_Presence_Sensor_25m)
- [C4001 SEN0609 datasheet PDF (DFRobot)](https://dfimg.dfrobot.com/wiki/20522/SEN0609_gravity-c4001-24ghz-mmwave-human-presence-detection-sensor_datasheet_V1.pdf)
- [SEN0609 detection capabilities — DFRobot Wiki](https://wiki.dfrobot.com/sen0609/docs/20935)
- [SEN0609 product page — DFRobot](https://www.dfrobot.com/product-2793.html)
- [SEN0610 Gravity C4001 12m — DFRobot Wiki](https://wiki.dfrobot.com/SKU_SEN0610_Gravity_C4001_mmWave_Presence_Sensor_12m_I2C_UART)
- [SEN0610 reference: API, protocol and pinout — DFRobot Wiki](https://wiki.dfrobot.com/sen0610/docs/20949)
- [SEN0610 product page — DFRobot](https://www.dfrobot.com/product-2795.html)
- [DFRobot_C4001 library (GitHub)](https://github.com/DFRobot/DFRobot_C4001)
- [SEN0691 C4002 module — DFRobot Wiki](https://wiki.dfrobot.com/SKU_SEN0691_C4002_mmWave_Motion_and_Static_Presence_Module)
- [SEN0691 Arduino example, all results — DFRobot Wiki](https://wiki.dfrobot.com/sen0691/docs/23398)
- [DFRobot_C4002 library (GitHub)](https://github.com/DFRobot/DFRobot_C4002)
- [SEN0306 24GHz Microwave Radar Distance Sensor — DFRobot Wiki](https://wiki.dfrobot.com/sen0306/)
- [SEN0306 product page — DFRobot](https://www.dfrobot.com/product-1882.html)
- [SEN0623 C1001 60GHz — DFRobot Wiki](https://wiki.dfrobot.com/SKU_SEN0623_C1001_mmWave_Human_Detection_Sensor)
- [SEN0623 C1001 reference: API, protocol and pinout — DFRobot Wiki](https://wiki.dfrobot.com/sen0623/docs/21571)
- [SEN0623 product page — DFRobot](https://www.dfrobot.com/product-2861.html)
- [SEN0676 80GHz liquid level radar — DFRobot Wiki](https://wiki.dfrobot.com/sen0676/)
- [DFRobot radar catalogue and prices](https://www.dfrobot.com/search-radar.html)
- [DFRobot C4001 vs C4002 vs C1001 comparison](https://www.dfrobot.com/blog-22042.html)
- [MR60FDA2 Fall Detection Module datasheet (Seeed)](https://files.seeedstudio.com/wiki/mmwave-for-xiao/mr60/datasheet/MR60FDA2_Fall_Detection_Module_Datasheet.pdf)
- [MR60BHA2 Breathing and Heartbeat Module datasheet (Seeed)](https://files.seeedstudio.com/wiki/mmwave-for-xiao/mr60/datasheet/MR60BHA2_Breathing_and_Heartbeat_Module.pdf)
- [ESPHome seeed_mr60bha2 component](https://esphome.io/components/seeed_mr60bha2/)
- [SEN0306 data output format (frame header, 126 spectral lines) — DFRobot Wiki](https://wiki.dfrobot.com/sen0306/docs/20390)
- [DFRobot_C4002 library header (gate resolution modes, setDetectRange, setGateThresh)](https://raw.githubusercontent.com/DFRobot/DFRobot_C4002/master/src/DFRobot_C4002.h)
- [A New Wave in Robotics: Survey on Recent mmWave Radar Applications in Robotics (arXiv 2305.01135)](https://arxiv.org/html/2305.01135v4)
- [Static Background Removal in Vehicular Radar (arXiv 2307.01444)](https://arxiv.org/pdf/2307.01444)
- [RadarTrack: Enhancing Ego-Vehicle Speed Estimation with Single-chip mmWave Radar (arXiv 2504.14495)](https://arxiv.org/html/2504.14495)
