# Lane: adafruit-tof-st — ST FlightSense Time-of-Flight sensors sold by Adafruit

Research date: 2026-09-12. All prices are USD list price read from the Adafruit product page
on 2026-09-12. All chip-level numbers below were read out of the ST datasheet PDF text unless
the row says otherwise.

Target application context: a 350 mm square (or 350 mm diameter) mobile robot, 600–1200 mm
tall, that must (a) avoid collisions, (b) find humans, (c) find pets 200–500 mm tall, and
(d) tell human from pet from furniture.

---

## 1. Executive summary — what this lane can and cannot do

**Adafruit sells exactly five ST FlightSense ToF breakouts as of 2026-09-12.** All five are
single-zone rangefinders. Adafruit does **not** sell any multizone ST part — no VL53L5CX,
no VL53L7CX, no VL53L8CX breakout exists in the Adafruit catalogue. Searching
`adafruit.com/search?q=VL53L5CX` and `?q=VL53L8` returns **no exact match**; the search
falls back to the five single-zone parts. Adafruit designed a "VL53LCX STEMMA QT breakout"
in September 2021 (blog post `blog.adafruit.com/2021/09/14/vl53lcx-stemma-qt-breakout-design/`)
and ran an *EYE ON NPI* segment on the VL53L5CX in October 2021, but no product ever reached
the store. Treat the Adafruit ST ToF line as **1-pixel only**.

The five products:

| PID | Product | Chip | Price (2026-09-12) | Stock | STEMMA QT |
|---|---|---|---|---|---|
| 3316 | Adafruit VL6180X Time of Flight Distance Ranging Sensor (VL6180) | VL6180X | $13.95 | In stock | Yes |
| 3317 | Adafruit VL53L0X Time of Flight Distance Sensor — ~30 to 1000 mm | VL53L0X | $14.95 | In stock | Yes |
| 3967 | Adafruit VL53L1X Time of Flight Distance Sensor — ~30 to 4000 mm | VL53L1X | $14.95 | In stock | Yes |
| 5396 | Adafruit VL53L4CD Time of Flight Distance Sensor — ~1 to 1300 mm | VL53L4CD | $14.95 | In stock | Yes |
| 5425 | Adafruit VL53L4CX Time of Flight Distance Sensor — ~1 to 6000 mm | VL53L4CX | $14.95 | In stock | Yes |

Volume pricing on all four VL53 parts: $13.46 at 10–99 units, $11.96 at 100+. None is marked
discontinued or out of stock. Product 3317 carries STEMMA QT connectors despite the product
title not saying so — the page states *"we've also added SparkFun qwiic compatible STEMMA QT
connectors for the I2C bus so you don't even need to solder."*

**Headline conclusion for the robot.** A single-zone ToF sensor returns one number: the
distance to whatever filled its cone. It has **no human/pet/object classification of any
kind**, no velocity output, and no per-pixel data. It answers requirement (a) — obstacle
avoidance — very well and cheaply, and answers (b), (c) and (d) not at all. Any classification
must come from a different sensing modality (mmWave radar, thermal array, camera) fused with
these range readings. The honest role for this lane is a **bumper-replacement ring**: a set of
cheap, fast, short-range beams that guarantee the robot does not drive into anything, including
a cat, a chair leg and a stair edge.

A secondary consequence of the 350 mm footprint: the VL53L1X's 27° figure is the **diagonal**
FoV of a square SPAD array — datasheet Table 1, verbatim: *"Receiver Field Of View (diagonal FOV)
— Programmable from 15 to 27 degrees"*. The **horizontal** cone, which is what closes a ring, is
therefore about 27°/√2 ≈ **19°** (geometric inference from the square array; ST publishes only
the diagonal). A 19° horizontal cone covers about **335 mm** of arc at 1 m range, not the 480 mm
a full 27° cone would give, so a 360° perimeter at 1 m needs roughly **19 sensors per ring**,
not 14. That is the real cost driver, not the $14.95.

---

## 2. Per-sensor datasheet detail

### 2.1 VL53L0X — Adafruit 3317, $14.95

ST datasheet DocID029104 Rev 1, read in full.

| Parameter | Value | Condition |
|---|---|---|
| Package / size | Optical LGA12, 4.40 × 2.40 × 1.00 mm | — |
| Emitter | 940 nm invisible Class 1 laser (VCSEL) | — |
| System FoV | **25°** | Fixed. Datasheet §5.1: "VL53L0X system FOV is 25degrees." Not programmable. |
| Zones | 1 | — |
| Operating voltage (chip) | 2.6 to 3.5 V | Adafruit board regulates to 2.8 V, accepts 3–5 V in |
| Operating temperature | −20 to +70 °C | — |
| I2C | Up to 400 kHz. Address **0x52** (8-bit) = **0x29** (7-bit) | Programmable, volatile |
| HW standby current | 3 / 5 / 7 µA (min/typ/max) | 23 °C, 2.8 V |
| SW standby current | 4 / 6 / 9 µA | — |
| Active ranging average | **19 mA typ** | default API settings, 33 ms timing budget, incl. VCSEL |
| Average power @ 10 Hz | 20 mW | 33 ms ranging sequence |
| Min ranging distance | ~3 cm practical (Pololu), datasheet gives no floor | Adafruit says "approximately 30 mm" |
| Timing budget | 20 ms min, 5 s max; 33 ms typical | Longer budget = longer range |

**Maximum range, Table 11 (33 ms timing budget), the numbers that matter:**

| Target | Indoor (no infrared) | Outdoor overcast |
|---|---|---|
| White 88 % (N9.5 Munsell), typical | **200 cm+** (using long-range API profile) | **80 cm** |
| White 88 %, minimum | 120 cm | 60 cm |
| Grey 17 % (N4.74 Munsell), typical | **80 cm** | **50 cm** |
| Grey 17 %, minimum | 70 cm | 40 cm |

"Outdoor overcast" is defined precisely: 10 kcps/SPAD of parasitic noise, equal to 1.2 W/m²
at 940 nm, equivalent to **5 kLux daylight** while ranging on a grey 17 % chart at 40 cm.
All distances are guaranteed at a minimum 94 % detection rate with the full 25° FoV covered.

**Ranging accuracy, Table 12 (standard deviation, including part-to-part spread):**

| Target | Indoor, 33 ms | Indoor, 66 ms | Outdoor, 33 ms | Outdoor, 66 ms |
|---|---|---|---|---|
| White 88 % @ 120 cm indoor / 60 cm outdoor | 4 % | 3 % | 7 % | 6 % |
| Grey 17 % @ 70 cm indoor / 40 cm outdoor | 7 % | 6 % | 12 % | 9 % |

**Range profiles, Table 13 — the four modes the Adafruit Arduino library exposes** as
`VL53L0X_SENSE_DEFAULT`, `VL53L0X_SENSE_LONG_RANGE`, `VL53L0X_SENSE_HIGH_SPEED`,
`VL53L0X_SENSE_HIGH_ACCURACY` (verified in `Adafruit_VL53L0X.h`):

| Profile | Timing budget | Typical performance | Intended use |
|---|---|---|---|
| Default | 30 ms | 1.2 m, accuracy per Table 12 | standard |
| High accuracy | 200 ms | 1.2 m, accuracy < ±3 % | precise measurement |
| Long range | 33 ms | **2 m**, accuracy per Table 12 | long ranging, **only for dark conditions (no IR)** |
| High speed | 20 ms | 1.2 m, accuracy ±5 % | high speed where accuracy is not priority |

Note the datasheet's own caveat on long range: *"only for dark conditions (no IR)"*. A robot
in a sunlit room will not get 2 m out of a VL53L0X.

Ranging offset drift (Table 14, offset calibrated at 10 cm): ±10 mm typical from nominal,
< 3 % max over distance; ±15 mm max over 2.6–3.5 V; ±30 mm max over −20 to +70 °C.

### 2.2 VL53L1X — Adafruit 3967, $14.95

ST datasheet **DocID031281 Rev 3 (November 2018)**, the ST-published PDF at
`www.st.com/resource/en/datasheet/vl53l1x.pdf`, read in full on 2026-09-12 (35 pages, text
extracted locally; st.com itself times out on most requests). **Correction:** an earlier draft of
this lane cited *Rev 2*; Rev 3 is the current ST revision. Every number in this section was
re-checked against Rev 3 and is unchanged. **This is the most useful part in the lane for a
mobile robot** because of the programmable region of interest.

| Parameter | Value | Condition |
|---|---|---|
| Package / size | Optical LGA12, 4.9 × 2.5 × 1.56 mm | — |
| Emitter | 940 nm Class 1 VCSEL; 16×16 SPAD receiving array | — |
| Receiver FoV (**diagonal**) | **Programmable from 15° to 27°** | Table 1 verbatim: "Receiver Field Of View (diagonal FOV) — Programmable from 15 to 27 degrees". 27° is the full 16×16 array. The FoV is **square**, so horizontal ≈ vertical ≈ 27°/√2 ≈ **19°** — use 19°, not 27°, for ring arithmetic (inference; ST publishes only the diagonal) |
| Zones | 1 at a time, but the ROI can be *moved* across the array — ST calls this "multizone operation control from the host" | — |
| Operating voltage (chip) | 2.6 to 3.5 V | — |
| Operating temperature | −20 to +85 °C | — |
| I2C | Up to 400 kHz (datasheet Table 1) / up to 1 MHz (Features page). Address **0x52** (8-bit) = **0x29** (7-bit), programmable | — |
| HW standby | 3 / 5 / 7 µA | — |
| SW standby | 4 / 6 / 9 µA | +0.6 µA in 2v8 IOVDD mode |
| Ranging average current | **16 mA typ, 18 mA max** | long distance mode, incl. AVDD + AVDDVCSEL |
| **Peak current** | **40 mA** | including VCSEL |
| Average power @ 10 Hz, 33 ms TB | 20 mW | — |
| Average power @ 1 Hz, 20 ms TB | 0.9 mW no target / 1.4 mW target detected | — |
| Min ranging distance | **4 cm.** Below this a target is detected but the measurement is not accurate | — |
| Max ranging rate | 50 Hz | short mode |
| Timing budget | 20 ms to 1000 ms. 20 ms is short-mode only; 33 ms is the minimum that works in all modes; **140 ms is required to reach the full 4 m** in long mode on a white chart in the dark | — |

**Distance modes, Table 4 (timing budget 100 ms, white 88 % target):**

| Distance mode | Max distance in dark | Max distance under strong ambient light (200 kcps/SPAD) |
|---|---|---|
| Short | **136 cm** | **135 cm** |
| Medium | **290 cm** | **76 cm** |
| Long | **360 cm** | **73 cm** |

This table is the single most important result in this lane. **Under direct sun the long mode
collapses from 3.6 m to 0.73 m, while short mode barely moves.** For an outdoor or
conservatory-capable robot, short mode is the only honest setting.

**Performance in dark, Table 6 (long mode, 100 ms TB):**

| Target | Min max-distance | Typical max-distance |
|---|---|---|
| White 88 % | 260 cm | **360 cm** (400 cm with TB = 140 ms) |
| Grey 54 % | 220 cm | 340 cm |
| Grey 17 % | 80 cm | **170 cm** |

Ranging error in dark: **± 20 mm**.

**Performance in ambient light, long mode, Table 7:**

| Target | Dark | 50 kcps/SPAD | 200 kcps/SPAD |
|---|---|---|---|
| White 88 % | 360 cm | 166 cm | **73 cm** |
| Grey 54 % | 340 cm | 154 cm | 69 cm |
| Grey 17 % | 170 cm | 114 cm | **68 cm** |
| Ranging error | ± 20 mm | ± 25 mm | ± 25 mm |

**Performance in ambient light, short mode, Table 8:**

| Target | Dark | 200 kcps/SPAD |
|---|---|---|
| White 88 % | 130 cm | 130 cm |
| Grey 54 % | 130 cm | 130 cm |
| Grey 17 % | 130 cm | **120 cm** |
| Ranging error | ± 20 mm | ± 25 mm |

ST defines the ambient light levels explicitly (datasheet §3.1): dark = no IR light in the
940 nm ± 30 nm band; 50 kcps/SPAD = "lighting on a sunny day from behind a window";
200 kcps/SPAD = "lighting on a sunny day from behind a window, **with direct illumination on
the sensor**"; usual office lighting is around 5 kcps/SPAD.

**Partial ROI in dark, Table 9 — the pseudo-multizone trade:**

| ROI (SPADs) | 16×16 | 8×8 | 4×4 |
|---|---|---|---|
| Diagonal FoV | **27°** | **20°** | **15°** |
| Max distance, White 88 % | 360 cm | 308 cm | 170 cm |
| Max distance, Grey 54 % | 340 cm | 254 cm | 143 cm |
| Max distance, Grey 17 % | 170 cm | 119 cm | 45 cm |
| Ranging error | ± 20 mm | ± 20 mm | ± 20 mm |

You can sweep a 4×4 ROI across the 16×16 array to build a coarse 3×3 or 4×4 depth "image" from
one sensor, at the cost of range (a 17 % grey target — a dark cat — drops to 45 cm) and of
frame rate (each ROI position is a separate ranging cycle).

**Library reality check.** Adafruit's own Arduino wrapper `Adafruit_VL53L1X.h` exposes only
`setTimingBudget()` / `getTimingBudget()`; `SetDistanceMode` is present but commented out in
the wrapper. The class inherits from the STM32duino `VL53L1X` class, which does provide
`VL53L1X_SetDistanceMode()`, `VL53L1X_SetROI(X, Y)`, `VL53L1X_SetROICenter()`,
`VL53L1X_SetTimingBudgetInMs()`, `VL53L1X_SetInterMeasurementInMs()` and
`VL53L1X_SetI2CAddress()`. The CircuitPython driver `adafruit_vl53l1x.py` exposes
`distance_mode`, `timing_budget`, `roi_xy`, `roi_center` and `set_address()`. Two caveats
found by reading the source:

- The CircuitPython driver supports **only short (1) and long (2)** distance modes. Medium is
  not implemented. Its own docstring says "1=short (up to 136cm), 2=long (up to 360cm)".
- Legal timing budget values in that driver: **15 ms (short mode only), 20, 33, 50, 100, 200,
  500 ms**. Default 50 ms.

### 2.3 VL53L4CD — Adafruit 5396, $14.95

ST datasheet DS13812 Rev 3 (January 2022), read in full.

| Parameter | Value | Condition |
|---|---|---|
| Package / size | Optical LGA12, 4.4 × 2.4 × 1 mm | pin-to-pin with VL53L0X, VL53L1X, VL53L1CB, VL53L3CX, VL53L4CX |
| Emitter | 940 nm Class 1 VCSEL | FoI (field of illumination) 16° × 16° at 1/e² |
| **Detection volume (system FoV)** | **18°** at a 1000 mm white-88 % target; **22°** at a 100 mm target | dark, default driver config |
| Collector exclusion cone | 25° | drives the cover-window opening size |
| Zones | 1 | — |
| Range | **0 to 1300 mm** full FoV; linear response from 1 mm | — |
| Max ranging rate | **100 Hz** | — |
| Operating voltage | 2.6 to 3.5 V | — |
| Operating temperature | −30 to +85 °C | — |
| I2C | up to 1 MHz (fast mode plus), address **0x52** (8-bit) = 0x29 (7-bit) | — |
| HW / SW standby | 3–7 µA / 4–9 µA | — |
| Active ranging average | **22 mA typ, 24 mA max** | default driver settings |
| **Peak current** | **40 mA** | incl. VCSEL |

**Max ranging, Table 14 (33 ms timing budget), stated with detection rate:**

| Target | Indoor (no IR) | Outdoor overcast (10 kcps/SPAD ≈ 5 kLux) |
|---|---|---|
| White 88 % | 1200 mm @ 90 % min detection; **1300 mm @ 50 %** | 550 mm @ 90 %; 600 mm @ 50 % |
| Grey 17 % | **450 mm @ 90 %**; 475 mm @ 50 % | 400 mm @ 90 %; 450 mm @ 50 % |

The advertised "1300 mm" is a 50 %-detection-rate number against an 88 % white chart indoors.
Against a dark grey target it is 450 mm. That is the number to design a robot to.

**Ranging accuracy, Table 15 (33 ms TB), at least 90 % of values within:**

| Target | 1–100 mm | 101–200 mm | > 200 mm |
|---|---|---|---|
| White 88 %, indoor | ± 7 mm | ± 8 mm | ± 3 % |
| White 88 %, outdoor overcast | ± 8 mm | ± 9 mm | ± 8 % |
| Grey 17 %, indoor | ± 6 mm | ± 8 mm | ± 4 % |
| Grey 17 %, outdoor overcast | ± 7 mm | ± 9 mm | ± 8 % |

Temperature drift is an offset, not a gain; the driver provides a manual temperature update
function (UM2931).

### 2.4 VL53L4CX — Adafruit 5425, $14.95

ST datasheet DS13805 Rev 2 (March 2022), read in full. Histogram-based, **multi-object capable**.

| Parameter | Value | Condition |
|---|---|---|
| Package / size | Optical LGA12, 4.4 × 2.4 × 1 mm | pin-to-pin with VL53L0X/L1X/L1CB/L3CX/L4CD |
| Emitter | 940 nm Class 1 VCSEL; FoI 16° × 16° (1/e²) | — |
| **Detection volume (system FoV)** | **18°** at 1000 mm white-88 %; **22°** at 100 mm | dark, default config |
| Collector exclusion cone | 25° | — |
| Zones | 1, but **multiobject detection within that cone** | histogram algorithm returns more than one target distance |
| Range | **0 mm to 6 m**, linear down to 10 mm | — |
| Operating voltage | 2.6 to 3.5 V | — |
| Operating temperature | −30 to +85 °C | — |
| I2C | up to 1 MHz, address **0x52** (8-bit) | — |
| Active ranging average | **19 mA typ, 21 mA max** | — |
| **Peak current** | **40 mA** | — |
| Cover-glass crosstalk | Targets **beyond 80 cm are immune** to cover-glass crosstalk and smudge; dynamic smudge compensation below 80 cm; live crosstalk correction | — |
| Temperature drift | 1.3 mm per °C offset; removed by a self-calibration run at ranging start | — |

**Max ranging, Table 14 (33 ms timing budget):**

| Target | Indoor (no IR) | Outdoor overcast (10 kcps/SPAD ≈ 5 kLux) |
|---|---|---|
| White 88 % | 5000 mm @ 90 %; **6000 mm @ 50 %** | 1600 mm @ 90 %; 1800 mm @ 50 % |
| Light grey 54 % | 4200 mm @ 90 %; 4600 mm @ 50 % | 1400 mm @ 90 %; 1600 mm @ 50 % |
| Grey 17 % | **2100 mm @ 90 %**; 2500 mm @ 50 % | 1100 mm @ 90 %; 1300 mm @ 50 % |

**Ranging accuracy, Table 15 (33 ms TB):**

| Target | 10–110 mm indoor | > 110 mm indoor | 10–110 mm outdoor | > 110 mm outdoor |
|---|---|---|---|---|
| White 88 % | ± 8 mm | ± 3 % | ± 9 mm | ± 5 % |
| Light grey 54 % | ± 8 mm | ± 4 % | ± 9 mm | ± 6 % |
| Grey 17 % | ± 7 mm | ± 5 % | ± 8 mm | ± 8 % |

**This is the best single-zone choice for the robot's forward-looking beams.** 2.1 m against a
dark 17 % target indoors at 90 % detection is the most useful "will I see the black cat" number
in the whole lane. Multi-object output also lets a beam report both a chair back at 1.2 m and
the wall at 3 m, which single-target parts cannot.

Practical caution from the Adafruit product page: the VL53L4CX driver needs about **50 KB of
flash**, so it will not fit on an ATmega328 (Arduino Uno). The Adafruit guide uses the
**STM32duino VL53L4CX** Arduino library; Adafruit publishes no Arduino library of its own for
this part (Adafruit's own repos for this chip are PCB files only:
`adafruit/Adafruit-VL53L4CX-PCB`).

### 2.5 VL6180X — Adafruit 3316, $13.95

ST datasheet DocID026171 Rev 6, read in full. Different silicon generation and a different
emitter wavelength; it is a **proximity** sensor, not a rangefinder.

| Parameter | Value | Condition |
|---|---|---|
| Package / size | Optical LGA12, 4.8 × 2.8 × 1.0 mm | — |
| **Emitter** | **850 nm** IR LED/VCSEL (not 940 nm) | visible as a faint red glow to some cameras |
| Ranging | **0 to 100 mm** guaranteed | "Ranging beyond 100 mm is possible with certain target reflectances and ambient conditions but not guaranteed" |
| Ranging FoV | **25°** (Pololu carrier page; the ST datasheet gives the ALS cone, not a numeric ranging cone) | vendor-page-verified |
| ALS FoV | **42° half angle at 40 % of peak**, in both X and Y | datasheet §2.13.1 |
| Ambient light sensor | < 1 Lux up to 100 kLux, 16-bit output, 8 manual gain settings | under a cover glass with 10 % visible transmission |
| Operating voltage | functional 2.6–3.0 V; **optimum 2.7–2.9 V** | narrower than the VL53 family |
| Operating temperature | functional −20 to +70 °C; optimum −10 to +60 °C | — |
| I2C | 400 kHz, address **0x29 (7-bit)** | — |
| HW standby / SW standby | < 1 µA / < 1 µA | — |
| ALS current | 300 µA | during integration |
| **Ranging current** | **1.7 mA typical average** | 10 Hz sampling, 17 % target at 50 mm |
| Max update rate | ~150 Hz | Pololu carrier page |

**Ranging specification, Table 19** (23 °C, 2.8 V, dark, average of 100 measurements on a
17 % target at 50 mm): noise max 2.0 mm; range offset error max 13 mm (after 3 reflow cycles,
removable by re-calibration); temperature-dependent drift 9 mm typ / 15 mm max; voltage-dependent
drift 3 mm typ / 5 mm max; convergence time max 15 ms (based on a 3 % target at 100 mm).

**Worst-case max range vs ambient, Table 20** (integrating sphere, halogen source, 80 × 80 mm
targets, SNR limit 0.1). ST notes 5 kLux halogen approximates **10–15 kLux natural sunlight**
because of its high IR content:

| Target reflectance | In the dark | Worst case indoor (1 kLux diffuse halogen) | High ambient (5 kLux diffuse halogen) |
|---|---|---|---|
| 3 % | > 100 mm | > 80 mm | > 40 mm |
| 5 % | > 100 mm | > 90 mm | > 45 mm |
| 17 % | > 100 mm | > 100 mm | > 60 mm |
| 88 % | > 100 mm | > 100 mm | > 70 mm |

The VL6180X is the lowest-power part in the lane by a factor of ten (1.7 mA vs 16–22 mA) and
the only one with a calibrated lux output. It is useless as a perimeter sensor — 100 mm is
inside the robot's own bumper line — but it is excellent as a **cliff / stair-edge detector**
pointing down from the chassis, and as an "am I about to scrape the wall" wall-follower.

---

## 3. The parts Adafruit does NOT sell (and why it matters)

These are the multizone ST parts a perimeter designer will actually want. **None is stocked by
Adafruit** (verified 2026-09-12: `adafruit.com/search?q=VL53L7CX` returns no exact match and falls
back to the five single-zone parts).

**Correction to an earlier draft of this lane.** That draft said the VL53L5CX / VL53L7CX /
VL53L8CX datasheets "were not retrievable" and that every figure for these three parts was
vendor-page-only. All three **were** retrieved on 2026-09-12 and the table below is now
datasheet-grade: **VL53L5CX DS13754 Rev 5 (December 2021)**, **VL53L7CX DS13865 Rev 6
(March 2023)**, **VL53L8CX DS14161 Rev 2 (March 2023)**. The correction matters, because the
vendor-page "63°" and "90°" figures are **diagonal** FoV of a square detection volume, and the
horizontal FoV — the number a perimeter ring is built from — is much smaller.

| Chip | Zones | FoV, detection volume (datasheet Table 2) | Headline range | Where to buy | Price read 2026-09-12 | Confidence |
|---|---|---|---|---|---|---|
| VL53L5CX | 4×4 or 8×8 | **H 45°, V 45°, diagonal 63°.** Collector exclusion zone 55.5° / 61° / 82°. "63° diagonal square FoV using diffractive optical elements (DOE) on both transmitter and receiver" | "up to 400 cm" — **only at 4×4, 30 Hz, in the dark, white 88 %** (conditioned tables below) | SparkFun Qwiic ToF Imager (SEN-18642); Pimoroni breakout | $32.50, **Backorder** at SparkFun; £16.25, in stock at Pimoroni | **datasheet-verified**, DS13754 Rev 5 |
| VL53L7CX | 4×4 or 8×8 | **H 60°, V 60°, diagonal 90°.** Collector exclusion zone 74° / 74° / 105° | "Up to 350 cm ranging" (features page), 60 Hz frame-rate capability | not Adafruit | not read | **datasheet-verified**, DS13865 Rev 6 |
| VL53L8CX | 4×4 or 8×8 | **H 45°, V 45°, diagonal 65°.** Collector exclusion zone 57.9° / 57.9° / 86.6° | 60 Hz frame-rate capability | not Adafruit | not read | **datasheet-verified**, DS14161 Rev 2 |

**The "400 cm" headline, with the conditions that make it mean something.** Neither SparkFun nor
Pimoroni publishes a target reflectance or an ambient-light level next to "up to 400 cm" /
"2–400 cm range", so the vendor number on its own is not usable. DS13754 Rev 5 gives it properly.
Maximum range capability is stated at a **90 % detection rate**, with the target filling 100 % of
the FoV, Munsell N9.5 (88 %) and N4.75 (17 %) charts, 23 °C, no cover glass, and "5 klux" defined
as 2 W/m² target irradiance at 940 nm.

Table 17 — **4×4, continuous 30 Hz:**

| Target | Zone | Dark | 5 klux ambient |
|---|---|---|---|
| White 88 % | inner | 4000 mm typ / 4000 mm min | 1700 mm typ / 1400 mm min |
| White 88 % | corner | 4000 mm typ / 4000 mm min | 1400 mm typ / 1100 mm min |
| Grey 17 % | inner | 2400 mm typ / 1900 mm min | 1000 mm typ / 900 mm min |
| Grey 17 % | corner | 2200 mm typ / 1800 mm min | 950 mm typ / 850 mm min |

Table 18 — **8×8, continuous 15 Hz** (the grey 17 % chart measures 13 % in IR at 940 nm):

| Target | Zone | Dark | 5 klux ambient |
|---|---|---|---|
| White 88 % | inner | **3500 mm typ / 2600 mm min** | 1100 mm typ / 950 mm min |
| White 88 % | corner | 3100 mm typ / 1700 mm min | 1000 mm typ / 800 mm min |
| Grey 17 % | inner | 1300 mm typ / 900 mm min | 800 mm typ / 600 mm min |
| Grey 17 % | corner | **1100 mm typ / 600 mm min** | **650 mm typ / 400 mm min** |

So the honest VL53L5CX numbers for a robot are: 4 m only at 4×4 in a dark room against white;
**3.5 m at 8×8 in the dark**; and **0.65 m for a dark-grey target in a corner zone under 5 klux**.
That last cell — a black cat at the edge of the frame in a sunlit room — is the design number.

SparkFun's page states "60 Hz frame rate capability" for the VL53L5CX; Pimoroni's page states
"2–400 cm range", "up to 60Hz ranging frequency", "63° diagonal", I2C address 0x29 (7-bit) /
0x52 (8-bit), 3–6 V compatible. Neither vendor publishes a per-zone
range-vs-reflectance-vs-ambient table, and **neither publishes the 4×4 / 8×8 frame-rate split**,
so do not take "60 Hz" as an 8×8 figure. DS13754 Rev 5 settles it: the performance tables are
specified at **30 Hz for 4×4 and 15 Hz for 8×8**.

For a 350 mm robot a multizone part still changes the arithmetic, but **not by as much as the
diagonal figures suggest, and an earlier draft of this lane got this wrong.** A 360° ring is
closed with *horizontal* FoV, not diagonal FoV. The VL53L7CX is **60° horizontal** (90° is its
diagonal), so **six** sensors close the ring, not four. The VL53L5CX and VL53L8CX are **45°
horizontal** (63° and 65° diagonal), so **eight** are needed. Against roughly **nineteen**
19°-horizontal VL53L1X beams, six VL53L7CX still wins clearly on wiring, GPIO count and
information content — but the ratio is about 3:1, not the 3.5:1 a false 4-versus-14 comparison
suggested.

Also found in the Adafruit "time of flight" search but **not ST silicon** (out of lane, noted
for completeness): Adafruit TMF8806 (PID 6501, $12.50, 33 in stock, 10 mm–5 m) and TMF8801
(PID 6522, $9.95, 75 in stock, 20 mm–2.5 m), both ams-OSRAM; Garmin LIDAR-Lite v4 (PID 4441,
$59.95, 15 in stock); Slamtec RPLIDAR A1 (PID 4010, $99.95, 19 in stock).

---

## 4. Cross-cutting behaviour: the questions a perimeter designer actually asks

### 4.1 Dark, white and mirror/glass targets

- **Dark (17 % grey) targets are the binding constraint.** Every ST table shows roughly a
  2× to 4× range loss from 88 % white to 17 % grey. A black cat, dark jeans, a matte-black
  speaker cabinet and a charcoal rug are all closer to 17 % than to 88 %. Use the grey-17 %
  column for every design calculation. Worst case in this lane: VL53L1X long mode, grey 17 %,
  200 kcps/SPAD ambient → **68 cm**.
- **White (88 %) numbers are marketing numbers.** "4 m" (VL53L1X) and "6 m" (VL53L4CX) are both
  white-88 %, dark-room figures, and the 6 m figure is additionally a 50 %-detection-rate figure.
- **Mirror and glass: not published.** No ST datasheet in this lane publishes behaviour against
  a specular or transparent target. All published reflectance data uses diffuse Munsell charts
  (N4.74 grey 17 %, N8.25 grey 54 %, N9.5 white 88 %). Physics says a mirror at a non-normal
  angle returns no signal to the receiver and the sensor reports "no target" or a phantom
  reflection of whatever the mirror points at; clear glass is largely transparent at 940 nm and
  850 nm and will usually be missed. **Treat glass doors and mirrors as a known blind spot for
  this entire lane and cover them with a different modality (ultrasonic or bumper).** This is
  inference from the absence of a spec, not a published result.
- Adafruit's own VL53L0X guide says it plainly: *"if the object absorbs the laser light you
  won't get good readings"* and *"some experimentation will be necessary"*.
- The word **"crosstalk" in these datasheets means cover-glass optical crosstalk, not
  sensor-to-sensor interference.** VL53L4CX advertises immunity to cover-glass crosstalk beyond
  80 cm plus dynamic smudge compensation below 80 cm; VL6180X has
  `SYSRANGE__CROSSTALK_COMPENSATION_RATE` and `SYSRANGE__CROSSTALK_VALID_HEIGHT` (default 20 mm)
  registers; VL53L1X requires RefSPAD, offset and crosstalk calibration whenever a cover glass
  is added. If the robot has a cosmetic window in front of the sensors, **that calibration is
  mandatory, not optional.**

### 4.2 Sunlight vs indoors

Summarised from the tables above:

| Chip | Dark / indoor headline | Under strong ambient | Loss |
|---|---|---|---|
| VL53L0X | 200 cm+ white, 80 cm grey-17 | 80 cm white, 50 cm grey-17 (5 kLux equiv.) | ~2.5× |
| VL53L1X long | 360 cm white, 170 cm grey-17 | 73 cm white, 68 cm grey-17 (200 kcps/SPAD) | **~5×** |
| VL53L1X short | 130 cm | 130 cm white / 120 cm grey-17 | ~1× |
| VL53L4CD | 1200 mm white @90 %, 450 mm grey-17 @90 % | 550 mm white, 400 mm grey-17 (5 kLux equiv.) | ~2× |
| VL53L4CX | 5000 mm white @90 %, 2100 mm grey-17 @90 % | 1600 mm white, 1100 mm grey-17 (5 kLux equiv.) | ~3× |
| VL6180X | > 100 mm all targets | > 40–70 mm at 5 kLux halogen (≈ 10–15 kLux sun) | ~2× |

Note the tables are not directly comparable: VL53L1X uses kcps/SPAD (200 kcps/SPAD = direct
sun on the sensor through a window), while VL53L0X/L4CD/L4CX use "outdoor overcast" = 10
kcps/SPAD ≈ 5 kLux. **Direct full sun (100 kLux+) is far outside every table here.** No ST
datasheet in this lane publishes a number at 100 kLux or 200 kLux. If the robot goes outside,
specify from the 200 kcps/SPAD column and expect worse.

### 4.3 How many on one I2C bus, and mutual interference

**Address assignment (verified).** Every ST FlightSense part in this lane powers up at the same
address — 0x52 8-bit / 0x29 7-bit — and the address is **volatile**. The Adafruit VL53L0X guide
documents the standard procedure and states the trap outright: *"You must do this every time
you turn on the power, the addresses are not permanent!"* The sequence is:

1. Wire every sensor's **XSHUT** pin to its own microcontroller GPIO.
2. Hold all XSHUT low for 10 ms, then high, to reset every sensor.
3. Bring sensor 1 up (XSHUT high) with all others held in shutdown (XSHUT low).
4. Assign sensor 1 a unique address with `begin(newAddress)` or `setAddress(newAddress)`.
   Adafruit's guide suggests values in **0x30–0x3F**.
5. Bring sensor 2 up, assign its address, and repeat.

Equivalent API calls exist on every part: `Adafruit_VL53L0X::setAddress()`,
`VL53L1X_SetI2CAddress()` (STM32duino class, inherited by `Adafruit_VL53L1X`),
`adafruit_vl53l1x.set_address()` and `adafruit_vl53l4cd.set_address()` in CircuitPython.

**Practical bus count (inference, not a published spec).** The limit is not the sensors, it is
(1) the number of free GPIOs for XSHUT — one per sensor, no way around it without an I2C GPIO
expander; (2) the 7-bit address space, which leaves roughly 112 usable addresses; and (3) I2C
bus capacitance, nominally 400 pF, which a long daisy chain of STEMMA QT cables around a 350 mm
chassis will approach. A ring of 12–16 sensors is electrically plausible on one bus with short
cables; beyond that, split the ring across two or more I2C buses or use a multiplexer
(Adafruit sells a TCA9548A, which also removes the need for per-sensor XSHUT GPIOs). **Mark
this as inferred — no ST or Adafruit document read in this session states a maximum count.**

**Mutual interference between sensors pointing into overlapping space: not published.** I found
no interference or mutual-blinding specification in the VL53L0X, VL53L1X, VL53L4CD, VL53L4CX or
VL6180X datasheets. The Adafruit VL53L0X guide has a warning block in its multi-sensor section
but gives no interference data. What is known from the physics and from ST's own architecture:

- All five parts emit in a narrow band (940 nm ± 30 nm; the VL6180X at 850 nm) and range by
  correlating returns from their own emitter. A second sensor's pulses appear as **ambient
  background noise in that band**, which is exactly the quantity that collapses the range in
  the ambient-light tables above. Two VL53L1X units staring into each other therefore behave
  like a modest artificial "kcps/SPAD" load on each other, not like a hard failure.
- The mitigation ST's own architecture offers is **time multiplexing**: XSHUT is already wired
  per sensor for addressing, so the same GPIOs can gate sensors into non-overlapping ranging
  windows. With a 20–33 ms timing budget, a 12-sensor ring round-robins at roughly 2.5–4 Hz per
  sensor, or faster if only opposing (non-overlapping) sensors fire together.
- The VL6180X at **850 nm does not interfere** with the 940 nm VL53 parts, and vice versa,
  because each has a physical IR bandpass filter. Mixing the two wavelengths is a legitimate way
  to run a downward cliff sensor concurrently with a forward ring.

Mark all three bullets as **inferred**. They are reasoned from the published ambient-light
mechanism, not quoted from a spec.

---

## 5. Fitness for the four requirements

| Requirement | Verdict | Reasoning |
|---|---|---|
| (a) Detect any obstacle it could collide with | **Good, with caveats** | 18–27° beams (and the VL53L1X's 27° is a *diagonal*, ≈ 19° horizontal), mm-accurate, 50–100 Hz. Blind to glass and to mirrors at an angle; range against dark targets is a third of the headline number. Needs roughly **19** units for a true 360° ring at 1 m. |
| (b) Detect humans specifically | **No** | Output is one distance. A human at 1.5 m and a wall at 1.5 m are the same reading. No thermal, no motion, no shape. |
| (c) Detect pets 200–500 mm tall | **Partly, as obstacles only** | A cat crossing a beam mounted at cat height produces a range step. But dark fur is a 17 %-class target — VL53L4CX gives 2.1 m indoors at 90 % detection, VL53L1X in long mode gives 1.7 m in the dark and 0.68 m under sun. Beam height matters more than the sensor: a ring mounted at 600 mm sees over a cat entirely. Budget a second ring at 150–250 mm. |
| (d) Distinguish human / pet / object | **No** | No feature in any of these five parts supports classification. VL53L1X ROI scanning or VL53L4CX multi-object gives coarse shape hints at best, not identity. Classification must come from mmWave, a thermal array, or a camera. |

**Recommended use of this lane, if it is used at all:**

- **Forward and quadrant obstacle beams:** VL53L4CX (5425) — best dark-target range (2.1 m at
  17 % grey, 90 % detection, indoors) and multi-object output. $14.95 each.
- **Low ring for pets and low furniture at 150–250 mm height:** VL53L4CD (5396) at 100 Hz, or
  VL53L1X (3967) in short mode where sunlight immunity matters. $14.95 each.
- **Downward cliff / stair-edge sensors:** VL6180X (3316) at 1.7 mA, $13.95 each.
- **Do not** specify VL53L0X (3317) for new work. VL53L4CD is the same price, has better
  accuracy, a tighter 18° cone, 100 Hz instead of ~30 Hz, and a wider temperature range; the
  VL53L0X's only advantage is a wider 25° cone and a smaller code footprint.
- **Strongly consider leaving the Adafruit catalogue** for a VL53L5CX/L7CX/L8CX multizone part.
  **Six** VL53L7CX (60° horizontal each) or **eight** VL53L5CX/L8CX (45° horizontal each) beat
  roughly **nineteen** narrow single-zone beams on cost, wiring, GPIO count and information
  content. Size the ring from the horizontal FoV in Table 2 of each datasheet, never from the
  diagonal figure the vendor pages quote.

---

## 6. Sources read

- https://www.adafruit.com/search?q=time+of+flight (pages 1 and 2)
- https://www.adafruit.com/search?q=VL53 , ?q=VL53L5CX , ?q=VL53L8
- https://www.adafruit.com/product/3316 , /3317 , /3967 , /5396 , /5425
- https://learn.adafruit.com/adafruit-vl53l0x-micro-lidar-distance-sensor-breakout/overview
- https://learn.adafruit.com/adafruit-vl53l0x-micro-lidar-distance-sensor-breakout/arduino-code
- https://learn.adafruit.com/adafruit-vl53l0x-micro-lidar-distance-sensor-breakout/downloads
- https://learn.adafruit.com/adafruit-vl53l1x/python-circuitpython , /arduino
- https://learn.adafruit.com/adafruit-vl53l4cd-time-of-flight-distance-sensor/downloads
- https://learn.adafruit.com/adafruit-vl53l4cx-time-of-flight-distance-sensor/overview , /arduino , /downloads
- https://learn.adafruit.com/adafruit-vl6180x-time-of-flight-micro-lidar-distance-sensor-breakout/downloads
- ST VL53L1X datasheet **DocID031281 Rev 3, November 2018** (PDF, full text extracted, via
  `www.st.com/resource/en/datasheet/vl53l1x.pdf`)
- ST VL53L5CX datasheet **DS13754 Rev 5, December 2021** (PDF, full text extracted)
- ST VL53L7CX datasheet **DS13865 Rev 6, March 2023** (PDF, full text extracted)
- ST VL53L8CX datasheet **DS14161 Rev 2, March 2023** (PDF, full text extracted)
- ST VL53L0X datasheet DocID029104 Rev 1 (PDF, full text extracted, via cdn-learn.adafruit.com/assets/assets/000/037/547/original/en.DM00279086.pdf)
- ST VL53L4CD datasheet DS13812 Rev 3 (PDF, full text extracted, via cdn-learn.adafruit.com/assets/assets/000/109/710/original/vl53l4cd.pdf)
- ST VL53L4CX datasheet DS13805 Rev 2 (PDF, full text extracted, via cdn-learn.adafruit.com/assets/assets/000/111/219/original/vl53l4cx.pdf)
- ST VL6180X datasheet DocID026171 Rev 6 (PDF, full text extracted, via cdn-learn.adafruit.com/assets/assets/000/037/608/original/VL6180X_datasheet.pdf)
- https://www.pololu.com/product/2490 (VL53L0X carrier), /2489 (VL6180X carrier), /3415 (VL53L1X carrier)
- https://www.sparkfun.com/sparkfun-qwiic-tof-imager-vl53l5cx.html
- https://shop.pimoroni.com/products/vl53l5cx-time-of-flight-tof-sensor-breakout
- Source code read directly: `adafruit/Adafruit_VL53L0X/src/Adafruit_VL53L0X.h`,
  `adafruit/Adafruit_VL53L1X/src/Adafruit_VL53L1X.h`,
  `stm32duino/VL53L1X/src/vl53l1x_class.h`,
  `adafruit/Adafruit_CircuitPython_VL53L1X/adafruit_vl53l1x.py`,
  `adafruit/Adafruit_CircuitPython_VL53L4CD/adafruit_vl53l4cd.py`

**Retrieval note (revised 2026-09-12).** An earlier draft of this lane recorded that
`www.st.com` did not respond and that the VL53L5CX, VL53L7CX and VL53L8CX datasheets were
therefore unread. `www.st.com` is intermittent, not dead: it times out on most requests but did
serve `vl53l1x.pdf`, and DS13754 Rev 5, DS13865 Rev 6 and DS14161 Rev 2 were all retrieved and
their text extracted. Section 3 is therefore datasheet-grade, and the horizontal-FoV correction
in it supersedes the earlier vendor-page-only "63° / 90°" figures. `www.mouser.com` still
returns a block page.

**Adversarial verification pass, 2026-09-12.** Every price and stock status in Section 1 was
re-read from the Adafruit product page on 2026-09-12 and is unchanged; all five parts are **in
stock** and none is discontinued. VL6180X volume pricing, not previously stated here, is $12.56
at 10–99 and $11.16 at 100+. The VL53L0X numbers (DocID029104 Rev 1 Table 11: 200 cm+ typical
using the long-range API profile / 120 cm minimum, white 88 % N9.5, indoor = no infrared, 33 ms
timing budget, 94 % minimum detection rate; §5.1 "VL53L0X system FOV is 25degrees"), the VL53L4CD
numbers (DS13812 Rev 3 Table 14: 1200 mm @ 90 % min detection, 1300 mm @ 50 %), the VL53L4CX
numbers (DS13805 Rev 2 Table 14: 5000 mm @ 90 %, 6000 mm @ 50 %) and both L4 FoV rows (18° at a
1000 mm white-88 % target, 22° at 100 mm, 25° collector exclusion cone) were re-checked line by
line against the datasheet PDFs and are **correct as written**. The VL6180X Table 1 note 1 was
re-checked verbatim and is correct; the 25° ranging cone stays Pololu-sourced, because the ST
datasheet gives no numeric ranging cone — only the 42° half-angle (40 % of peak) ALS field of
view in §2.13.1.
