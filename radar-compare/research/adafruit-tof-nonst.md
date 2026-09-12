# Lane: adafruit-tof-nonst — Non-ST ranging and proximity products at Adafruit

Scope: every distance / proximity / ranging product Adafruit Industries sells that is **not** built on an
STMicroelectronics VL53Lxx or VL6180X part, evaluated against one specific robot:

- footprint 350 mm square or 350 mm round
- height 600–1200 mm
- must see (a) any collidable obstacle, (b) humans, (c) pets 200–500 mm tall, (d) tell them apart

All Adafruit prices and stock states were read from `adafruit.com` on **2026-09-12**. All silicon numbers
below come from the manufacturer datasheet PDF unless the row says otherwise. Where a number is not
published, the document says **not published** — nothing here is estimated or rounded from a guess.

> **Adversarial spec check, 2026-09-12.** Every hard number in this document was re-verified against the
> manufacturer datasheet PDF or the vendor product page. Four claims did not survive and are corrected
> in place, each marked **Correction** where it appears:
>
> 1. **TMF8806 §2.2** — the 10 m and 7 m rows of DS001097 Table 5 are specified against a **white wall**,
>    not the 1.5 m × 1.5 m object that conditions the rest of the table.
> 2. **Garmin LIDAR-Lite v3 §5.1** — Garmin *does* publish a target condition (**70 % reflective**) on
>    both the 40 m range and the 270 Hz update rate. The previously quoted "±2.5 cm above 1 m" accuracy
>    and "up to 500 Hz" update rate were Adafruit's numbers and both are wrong against Garmin's manual.
> 3. **Sharp analog IR §6** — Sharp *does* publish the reflectivity condition (**Kodak R-27 gray card,
>    white face, 90 % reflectance**) and *does* publish a 90 %-vs-18 % response plot showing the two are
>    nearly identical. The former "reflectance sensitivity" objection is retracted.
> 4. **TMF8828 §2.3** — the 8×8 table is taken at **125 k iterations**, not the 550 k of the 3×3 and 4×4
>    tables, so the 8×8 numbers are not directly comparable to the ones above them.
>
> Everything else checked out: TMF8801 DS000648 Figure 19 and §7.8, TMF8806 Table 5 (5 m and 2.5 m rows)
> and Tables 9–10, TMF8828 DS000693 Figures 30–32, 34, 36 and 38, RPLIDAR A1 Figure 2-1, TFmini
> SJ-PM-TFmini-T-01 A03 Tables 1–2, MaxBotix PD11832e, and all Adafruit prices, stock counts and status
> strings listed here.

---

## 1. The distinction that decides this lane: scanning lidar vs fixed single-point ranger

This matters more than any other spec on the page, so it goes first.

**True scanning lidar** puts one ranging head on a motor and spins it. One unit produces a full 360°
planar point cloud with no mounting arithmetic, no per-sensor calibration, and no bus arbitration. In
Adafruit's entire catalogue there is exactly **one** such product: the **Slamtec RPLIDAR A1 (PID 4010,
$99.95)**. Nothing else Adafruit stocks rotates.

**Fixed single-point rangers** report one number: the distance to the nearest thing inside a narrow cone
pointed wherever you bolted the sensor. Perimeter coverage is then an *N*-sensor tiling problem, and *N*
is set by the cone width:

| Sensor | Cone (published) | Sensors needed for 360° (no overlap margin) |
|---|---|---|
| Benewake TFmini (discontinued at Adafruit) | 2.3° full (1.15° receive half-angle) | 157 |
| Garmin LIDAR-Lite v3 | 8 mrad = 0.46° | 785 |
| Garmin LIDAR-Lite v4 | 4.77° | 76 |
| HC-SR04 / RCWL-1601 | 15° (vendor page) | 24 |
| ams TMF8801 (long-range mode) | 24° FWHM | 15 |
| ams TMF8806 (long-range) | 30° | 12 |
| ams TMF8828 8x8 (Adafruit does **not** stock) | 41° × 52° | 7–9 |
| RPLIDAR A1 | 360° | **1** |

**Multizone dToF** is the middle ground: the TMF882x family reports a grid of independent distances
inside one wide cone, which is a real per-zone obstacle map rather than a single scalar. That is the
single most useful non-lidar technology in this lane — and Adafruit does **not** sell any of it. Adafruit's
TMF882x breakout has been shown as a prototype on the Adafruit blog (2024-08-27, "TMS8828 multi-zone
time-of-flight sensor from ams OSRAM") and marked "coming soon", but a store search on 2026-09-12 returns
no TMF8820/8821/8828 product page. Adafruit's shipping TMF parts are both **single-zone**: TMF8801 and
TMF8806.

---

## 2. Adafruit ams-OSRAM dToF parts (single-zone, in stock)

### 2.1 Adafruit TMF8801 Time of Flight Distance Sensor — PID 6522, $9.95, 75 in stock (2026-09-12)

Product page: <https://www.adafruit.com/product/6522>
Guide: <https://learn.adafruit.com/adafruit-tmf8801-time-of-flight-distance-sensor>
Silicon datasheet: ams-OSRAM **DS000648 v10-00, 2022-Dec-20**

This is the one product in this lane where the datasheet publishes a full range-versus-reflectivity-versus-
ambient-light matrix. It is worth quoting in full, because "2.5 m" on the store page is only the best
cell in the table.

**Maximum distance detection, 1.5 m × 1.5 m object, light on the target only** (DS000648 Figure 19):

| Ambient condition | Target | Max distance |
|---|---|---|
| 350 lux fluorescent on object | 18 % grey card | **2500 mm** (1) |
| 360 lux halogen (= 2.5 k lux sunlight equivalent) | 88 % white card | **2500 mm** (1) |
| 360 lux halogen (= 2.5 k lux sunlight equivalent) | 18 % grey card | **1700 mm** |
| 1400 lux halogen (= 10 k lux sunlight equivalent) | 88 % white card | **1500 mm** |
| 1400 lux halogen (= 10 k lux sunlight equivalent) | 18 % grey card | **1250 mm** |
| 14000 lux halogen (= 100 k lux sunlight equivalent) | 18 % grey card | **550 mm** |

(1) Datasheet footnote: *"To achieve the full distance, the oscillator need to be tuned to 4.7 MHz… Any
target reported above 2500 mm should be considered as no object."*

**Minimum distance detection**, 18 % grey card, 20 cm × 26 cm target: **20 mm**.

**Accuracy** (DS000648): ±5 % for object distance ≥ 200 mm; ±10 mm for 100 mm ≤ d < 200 mm;
±15 mm for 20 mm ≤ d < 100 mm. Short-to-long-mode transition at 200 mm.

**Optics** (DS000648 §7.8): VCSEL field of illumination **21° full width from 5 % of maximum**, 19° at
1/e². ToF sensor field of view **37° FWHM at short distance, 24° FWHM at long distance** — the SPAD array
is deliberately shrunk in long-range mode to reject ambient light. Optical bandpass: 940 nm centre,
56 nm FWHM.

**Rate**: default mode 33 ms (≈30 Hz) at 900 k iterations. **Power**: datasheet headline "27 mA power
consumption at 30 Hz operation", 0.23 mA at 1 Hz, 0.17 mA at 0.5 Hz. **Laser safety**: Class 1, 940 nm.
**Interface**: I²C, default 7-bit slave address **0x41**; Adafruit board carries STEMMA QT / Qwiic and a
3.3 V regulator plus level shifting. Adafruit's guide notes the part *"does require a firmware 'patch' on
boot"* — the host must push a several-kilobyte firmware image at startup.

**Pet at floor level?** Geometrically yes, photometrically marginal. Mount the sensor at 150 mm and aim
it level: the 24° FWHM long-range cone spans ±12°, so at 1.0 m it covers roughly 150 ± 212 mm, i.e. the
floor up to 362 mm — a 200 mm cat is fully inside the cone. The problem is the return: animal fur is
darker than an 18 % grey card at 940 nm, and dark fur is much darker. The 18 % grey row at 2.5 k lux
equivalent already drops to 1700 mm. Treat 1.0–1.5 m as the realistic indoor pet-detect range and expect
a black cat to be worse. Nothing about the output distinguishes a cat from a chair leg.

### 2.2 Adafruit TMF8806 Time of Flight Distance Sensor — PID 6501, $12.50, 33 in stock (2026-09-12)

Product page: <https://www.adafruit.com/product/6501>
Silicon datasheet: ams-OSRAM **DS001097 v4-00, 2025-Jun-24**

The TMF8806 is the newer, longer-reaching single-zone part, and the better default choice of the two for
this robot. Its published matrix (DS001097 v4-00 **Table 5**, default optical stack):

**Correction (verified 2026-09-12 against DS001097 v4-00 p.12):** Table 5 uses *two different targets*.
The two 10 m rows are specified against a **white wall** — the parameter name is literally "White wall,
default optical stack" — not against the 1.5 m × 1.5 m object that conditions the rest of the table. A
white wall fills the whole 30° cone; a 1.5 m × 1.5 m card at 10 m does not. **The 10 m headline number is
a wall number and must not be read as an obstacle-detection range.** The "Maximum distance detection,
1.5 m × 1.5 m object" parameter covers the 5 m and 2.5 m rows only.

| Mode | Ambient condition | Target | Target extent | Max distance |
|---|---|---|---|---|
| 10 m range, 1500 k iterations (150 ms) | 350 lux fluorescent | 90 % white card | **white wall** | **10000 mm** |
| 10 m range, 225 k iterations (33 ms) | 350 lux fluorescent | 90 % white card | **white wall** | **7000 mm** |
| 5 m range, 450 k iterations (33 ms) | 350 lux fluorescent | 90 % white card | 1.5 m × 1.5 m | **5000 mm** |
| 5 m range, 900 k iterations (66 ms) | 350 lux fluorescent | 18 % grey card | 1.5 m × 1.5 m | **3750 mm** |
| 5 m range, 450 k iterations (33 ms) | 350 lux fluorescent | 18 % grey card | 1.5 m × 1.5 m | **3250 mm** |
| 2.5 m range, 900 k, 33 ms | 350 lux fluorescent | 18 % grey or 90 % white | 1.5 m × 1.5 m | **2500 mm** |
| 2.5 m range, 900 k, 33 ms | 170 lux halogen (= 1 k lux sunlight) | 90 % white card | 1.5 m × 1.5 m | **2430 mm** |
| 2.5 m range, 900 k, 33 ms | 170 lux halogen (= 1 k lux sunlight) | 18 % grey card | 1.5 m × 1.5 m | **1840 mm** |
| 2.5 m range, 900 k, 33 ms | 170 lux halogen, **smudge on cover glass** (1 layer Scotch Magic Tape 810) | 18 % grey card | 1.5 m × 1.5 m | **1500 mm** |
| 2.5 m range, 900 k, 33 ms | 830 lux halogen (= 5 k lux sunlight) | 90 % white card | 1.5 m × 1.5 m | **1850 mm** |
| 2.5 m range, 900 k, 33 ms | 830 lux halogen (= 5 k lux sunlight) | 18 % grey card | 1.5 m × 1.5 m | **1170 mm** |
| Ultra-low-power, 10 k iterations, 2.5 m range | 350 lux fluorescent | 18 % grey | 1.5 m × 1.5 m | **665 mm** |

That smudge row is the most useful line in this whole document for a floor robot: **one layer of tape on
the cover glass costs 340 mm of range on an 18 % grey target.** A robot's front window collects dust and
pet hair continuously.

**Accuracy** (DS001097): 2.5 m range — ±3 % for d ≥ 200 mm, ±6 mm for 50 ≤ d < 200 mm, +5/−15 mm below
50 mm. 5 m range — ±3 % for d ≥ 500 mm, ±15 mm for 50 ≤ d < 500 mm, +5/−20 mm below 50 mm. 10 m range —
±2 % for d ≥ 2000 mm.

**Optics** (DS001097 §6.11, Table 9): VCSEL FOI **19° at 1/e², 21° full width from 5 % of max, 25° full
width from 1 % of max** (Table 9 gives degrees, not percent). Receiver FOV (Table 10) depends on the
optical stack:

| Optical stack | Short range (< 20 cm) | Long range |
|---|---|---|
| Default | **52°** | **30°** |
| Large airgap / thick cover glass | 30° | 30° |

Adafruit's own store page describes the shipped board as *"about 30° short range (under 200mm) and 21°
above"* and claims *"±5%"* accuracy — **the vendor page and the datasheet disagree on the FoV numbers**;
the datasheet is the higher-confidence source, and Adafruit may be quoting measured behaviour of their
specific cover-glass stack. Store page also admits *"we weren't able to get results past 5 meter"*.

**Rate**: default 33 ms (≈30 Hz). **Power**: "27 mA power consumption at 30 Hz operation". **Laser
safety**: Class 1, 940 nm. **I²C address 0x41** (datasheet default). Adafruit notes no firmware patch is
needed for 5 m mode, and that the driver fits on an ATmega328.

**Pet at floor level?** Better than the TMF8801. At 3.25 m against an 18 % grey card in 350 lux indoor
light, a 200 mm pet at 1–2 m is well inside the budget. The 30° long-range cone at 1.5 m spans about
800 mm vertically, so a single level-mounted unit covers floor-to-knee at conversational distance. It
still returns one scalar and cannot classify.

### 2.3 ams-OSRAM TMF8820 / TMF8821 / TMF8828 multizone — NOT SOLD BY ADAFRUIT

Silicon datasheet: ams-OSRAM **DS000693 v5-00, 2022-Apr-14**. Included here because the lane brief asks
for it and because it is the part you would actually want. Adafruit shows a prototype breakout on their
blog, but there is no product page and no stock as of 2026-09-12. SparkFun sells a Qwiic dToF Imager
using TMF8820/8821.

Zone maps: TMF8820 = 3×3; TMF8821 = 3×3, 4×4, 3×6; TMF8828 = 3×3, 4×4, 3×6, 8×8 (64 zones). Selectable
FoV by `spad_map_id`: 33°×32° (45° diag), 41°×52° (**63° diag**), 33°×47° (56°), 33°×42° (52°),
33°×60° (66°). Single-SPAD angular pitch 2.4° in x, 5.6° in y.

**Typical max distance, 3×3 mode, 33°×32° FoV, 550 k iterations, 30 Hz, light on target only**
(DS000693 Figure 34):

| Target | Zone | 350 lux LED | 140 lux halogen (= 1 k lux sun) | 700 lux halogen (= 5 k lux sun) | 1400 lux halogen (= 10 k lux sun) |
|---|---|---|---|---|---|
| White 90 % | Center | 5000 mm | 4500 mm | 2000 mm | 1000 mm |
| White 90 % | Edge | 5000 mm | 4000 mm | 1800 mm | 950 mm |
| White 90 % | Corner | 5000 mm | 3000 mm | 1500 mm | 750 mm |
| Grey 18 % | Center | 5000 mm | 3000 mm | 2000 mm | 1500 mm |
| Grey 18 % | Edge | 4500 mm | 2800 mm | 1500 mm | 1400 mm |
| Grey 18 % | Corner | 4000 mm | 2000 mm | 1400 mm | 1200 mm |

**4×4 mode, 41°×52° FoV, 550 k iterations, 15 Hz** (Figure 36):

| Target | Zone | 350 lux LED | 140 lux HAL | 700 lux HAL | 1400 lux HAL |
|---|---|---|---|---|---|
| White 90 % | Center | 5000 mm | 3500 mm | 2000 mm | 1000 mm |
| White 90 % | Edge | 3000 mm | 1400 mm | 900 mm | 500 mm |
| White 90 % | Corner | 2900 mm | 1300 mm | 800 mm | 400 mm |
| Grey 18 % | Center | 4000 mm | 2500 mm | 1500 mm | 1400 mm |
| Grey 18 % | Edge | 1500 mm | 1200 mm | 800 mm | 700 mm |
| Grey 18 % | Corner | 1400 mm | 1100 mm | 700 mm | 600 mm |

**8×8 mode, 41°×52° FoV, 125 k iterations, 15 Hz, light on target only** (Figure 38). **The iteration
count is not the same as the tables above**: Figure 34 is 550 k iterations at 30 Hz and Figure 36 is
550 k at 15 Hz, but Figure 38 is only **125 k iterations**, so the 8×8 numbers are depressed by a
quarter of the integration budget as well as by the smaller zones. Same four lighting columns
(350 lux LED / 140 lux HAL / 700 lux HAL / 1400 lux HAL):

| Target | Zone | 350 lux LED | 140 lux HAL | 700 lux HAL | 1400 lux HAL |
|---|---|---|---|---|---|
| White 90 % | Center | 4400 mm | 2000 mm | 1300 mm | 1000 mm |
| White 90 % | Edge | 1500 mm | 900 mm | 500 mm | 400 mm |
| White 90 % | Corner | 900 mm | 600 mm | 300 mm | 300 mm |
| Grey 18 % | Center | 2000 mm | 1500 mm | 1000 mm | 800 mm |
| Grey 18 % | Edge | 800 mm | 600 mm | 400 mm | 300 mm |
| Grey 18 % | Corner | 500 mm | 400 mm | 300 mm | 200 mm |

**The 8×8 corner zones collapse to 200–500 mm on an 18 % grey target** — 64-zone mode is a near-field
mode, not a room-scanning mode.

Short-range high-accuracy mode: minimum detection distance **10 mm** on an 18 % grey target, **25 mm** on
a 90 % white target; accuracy ±10 mm from 10–20 mm, ±5 mm from 20–200 mm; it halves max range and clips
at 1000 mm. Power: **141 mW at 30 Hz**, 8 µA standby, 2 µA powered down. Default I²C address **0x41**,
I3C-tolerant on a shared bus. Cover glass must be ≥ 85–90 % transparent at 940 nm; dynamic cover-glass
calibration is built in.

---

## 3. The one true scanning lidar Adafruit sells

### 3.1 Slamtec RPLIDAR A1 — PID 4010, $99.95, 19 in stock (2026-09-12)

Product page: <https://www.adafruit.com/product/4010>
Datasheet: Slamtec RPLIDAR A1 low-cost 360° laser range scanner, hosted at
<https://cdn-shop.adafruit.com/product-files/4010/4010_datasheet.pdf>

**Ranging principle is laser triangulation, not time of flight.** The datasheet says so explicitly:
*"RPLIDAR A1 is basically a laser triangulation measurement system."* That has a direct consequence —
triangulation resolution degrades with distance (datasheet: *"<1% of the distance"* over the full range,
*"<0.5 mm"* below 1.5 m) and the published range is conditioned on **white objects**.

**Published performance** (datasheet Figure 2-1):

| Item | Value | Condition |
|---|---|---|
| Distance range | **0.15–6 m** for A1M8-R4 "and the belowing models"; **0.15–12 m** for A1M8-R5 | "White objects" |
| Angular range | 0–360° | — |
| Distance resolution | < 0.5 mm below 1.5 m; < 1 % of distance across all range | — |
| Angular resolution | 1° | at 5.5 Hz scan rate |
| Sample duration | 0.125 ms | — |
| Sample frequency | 8000 Hz typical, 8010 Hz max | firmware 1.24+ |
| Scan rate | 1 Hz min, **5.5 Hz typical**, 10 Hz max | typical measured at 360 samples per scan |
| Laser | 775–795 nm, < 5 mW, **Class I** | *"safety to human and pet"* |
| Scanner supply | 4.9–5.5 V, ripple 20–50 mV; 300 mA work, 80 mA sleep, 500–600 mA start | — |
| Motor supply | 5–10 V, ~100 mA at 5 V | separate rail required |
| Weight | 170 g | — |
| Operating temperature | 0–45 °C | — |
| Interface | 3.3 V TTL UART; USB-serial adapter included by Adafruit | — |

Adafruit's page advertises 12 m, which implies they ship the **A1M8-R5**. Confidence on that inference:
**inferred**, not datasheet-verified per unit.

**The datasheet's own point-density numbers do not reconcile — do not compute one from the other.**
Sample frequency is 8000 Hz typical and typical scan rate is 5.5 Hz, which would give ≈1450 points per
revolution (0.25°). But the datasheet conditions both of the other two figures on a different density:
angular resolution 1° is specified *"5.5 Hz scan rate"*, and the 5.5 Hz typical scan rate is specified
*"measured when RPLIDAR A1 takes 360 samples per scan"* — 360 samples per revolution at 5.5 Hz is
1980 samples/s, not 8000. Slamtec publishes both and reconciles neither. **Quote 1° / 360 points per
revolution as the datasheet-conditioned figure, and treat any "≈1450 points per revolution" claim as an
unverified arithmetic product of two specs measured under different conditions.**

**Why this is the strongest single perimeter answer in this lane.** One unit, no tiling, 1° angular
resolution, 8000 points/s, and it is the only product here that produces an actual map rather than a
scalar. A 350 mm robot can mount it centrally and get a complete planar obstacle ring at 5.5 Hz.

**Why it is not sufficient on its own.**

1. **It is one plane.** Whatever height you bolt it at is the only height it sees. A 200 mm cat is
   invisible unless the scan plane is below 200 mm; a 350 mm dog is invisible if the plane is at 500 mm;
   a tabletop overhang at 700 mm is invisible if the plane is at 100 mm. This is the single biggest
   failure mode for a 600–1200 mm tall robot.
2. **Two separate 5 V rails and 170 g.** Motor rail and scanner rail must be independent *"in order to
   ensure data accuracy"*. That is real BOM and real mass on a 350 mm platform.
3. **Triangulation and dark targets.** Range is specified against white objects. Dark clothing, black
   fur, and matte-black furniture return far less. The datasheet publishes no black-target number —
   **not published**.
4. **Glass and mirrors.** Not addressed in the datasheet at all — **not published**. In practice a
   triangulation scanner sees straight through clear glass and sees a mirror's virtual image. Any glass
   door or full-length mirror in the robot's environment is a hazard the A1 will not report.
5. **Zero classification.** It returns (angle, distance, quality). Human vs pet vs object has to be
   inferred by your software from cluster width, height-invariance, and motion tracking across frames.
   A cat and a bin bag at the same plane height look identical in one frame.
6. **0–45 °C** operating range and a spinning bearing with a finite life.

---

## 4. Benewake lidar at Adafruit

### 4.1 TFmini Infrared Time of Flight Distance Sensor — PID 3978, $44.95, **NO LONGER STOCKED**

Product page: <https://www.adafruit.com/product/3978>
Manual: `SJ-PM-TFmini-T-01 A03`, hosted at
<https://cdn-shop.adafruit.com/product-files/3978/3978_manual_SJ-PM-TFmini-T-01_A03ProductManual_EN.pdf>

Discontinued at Adafruit. Included because the manual publishes the most explicit ambient-light /
target-reflectivity breakdown of any part in this lane, and because it quantifies the exact failure mode
that kills narrow-beam rangers for pet detection.

| Parameter | Value |
|---|---|
| Operating range (indoor) | 0.3–12 m *"under indoor standard white board condition (with reflectivity of 90%)"* |
| Blind zone | 0–30 cm, *"within which the data is unreliable"* |
| Extreme condition range | **0.3–3 m** — *"outdoor glare (…around 100klux…)"* and *"black target (with reflectivity of 10%)"* |
| Normal sunshine, white target | **0.3–7 m** at ~70 klux |
| Indoor / weak ambient | 0.3–12 m |
| Accuracy | ±4 cm @ 0.3–6 m; ±6 cm @ 6–12 m |
| Range resolution | 5 mm |
| Receiving half angle | **1.15°** |
| Transmitting half angle | **1.5°** |
| Frequency | 100 Hz (trigger must never exceed 80 Hz) |
| Interface | UART 115200 8N1, 5 V supply, 3.3 V TTL |
| Power | ≤ 120 mW average, 850 nm |

**The minimum-target-size table is the important part.** The manual gives `d = 2 · D · tan(β)` with
β = 1.15°, and tabulates:

| Detecting range | 1 m | 2 m | 3 m | 4 m | 5 m | 6 m | 8 m | 10 m | 12 m |
|---|---|---|---|---|---|---|---|---|---|
| Minimum reliable target side length | 4 cm | 8 cm | 12 cm | 16 cm | 20 cm | 24 cm | 32 cm | 40 cm | 48 cm |

At 2 m a narrow-beam lidar needs an 8 cm target. A cat's torso clears that. A cat's *tail*, a chair leg,
or a table pedestal seen edge-on may not. And a 2.3° beam scanning nothing is a 157-sensor problem for
360° coverage. Also note the manual's warning: *"The product will be subject to risk of failure if the
detecting object has high reflectivity"* — mirrors and polished floors break it.

### 4.2 TF-Luna, TFmini-S, TFmini Plus — **not sold by Adafruit**

A store search for "TF-Luna" on 2026-09-12 returns *"No products found for 'TF-Luna'"*. Adafruit's only
Benewake product was the original TFmini and it is no longer stocked. For reference, the TF-Luna is a
0.2–8 m UART/I²C single-point module sold at ~$29.90 by Benewake and third parties — **vendor-page-
verified from Benewake/RobotShop, not from Adafruit.** Out of scope for an Adafruit-sourced BOM.

---

## 5. Garmin LIDAR-Lite

### 5.1 LIDAR-Lite v3 — PID 4058, $129.95, 12 in stock, max 2 per customer (2026-09-12)

<https://www.adafruit.com/product/4058>

Primary source: **Garmin, "LIDAR-Lite v3 Operation Manual and Technical Specifications"**.

**Correction (verified 2026-09-12 against the Garmin manual):** an earlier revision of this document
said the v3 publishes no target-reflectivity condition, and repeated Adafruit's accuracy and update-rate
numbers. All three were wrong. Garmin *does* publish the condition, and it conditions two separate
specifications on it. Where Garmin and Adafruit disagree, the Garmin column is authoritative.

| Parameter | Garmin manual (primary) | Adafruit page (reseller) |
|---|---|---|
| Range | **40 m (131 ft) at a 70 % reflective target** — the condition is in the row label, "Range (70% reflective target)". The 5 cm minimum is **not** in the Garmin spec table; it is an Adafruit number only | "5 cm to 40 m", no condition |
| Accuracy | **±2.5 cm typical for < 5 m; ±10 cm typical for ≥ 5 m**; mean ±1 % of distance max, ripple ±1 % of distance max. Footnote: *"Nonlinearity present below 1 m"* | "±2.5 cm at distances > 1 m" — **wrong**, it drops Garmin's ≥ 5 m tier entirely |
| Resolution | ±1 cm | 1 cm |
| Update rate | **270 Hz typical at a 70 % reflective target**; 650 Hz "fast mode" (footnote: *"Reduced sensitivity"*); > 1000 Hz short range only. Separate **repetition rate ~50 Hz default, 500 Hz max** | "up to 500 Hz" — **wrong/conflated**: 500 Hz is Garmin's repetition-rate maximum, not the update rate |
| Beam divergence | **8 mRadian (0.46°)**; beam diameter at aperture 12 ± 2 mm | 8 m Radian |
| Interface | I²C (default 7-bit address 0x62, fast-mode 400 kbit/s) or PWM | I²C or PWM |
| Supply | **4.5 V min, 5.5 V max**, 5 Vdc nominal | 4.75–5 VDC, 6 V max |
| Current | 105 mA idle, **135 mA** continuous operation | 105 mA idle, 130 mA continuous |
| Laser | 905 nm nominal, 1.3 W peak, < 280 nJ per pulse | 905 nm, 1.3 W |
| Size / mass | 20 × 48 × 40 mm, 22 g | 40 × 48 × 20 mm, 22 g |
| Temp | −20 to 60 °C | −20 to 60 °C |

### 5.2 LIDAR-Lite v4 LED — PID 4441, $59.95, 15 in stock, max 2 per customer (2026-09-12)

<https://www.adafruit.com/product/4441>

| Parameter | Value |
|---|---|
| Range | 5 cm to 10 m (measured from back of unit) |
| Accuracy | ±1 cm to 2 m, ±2 cm to 4 m, ±5 cm to 10 m |
| Resolution | 1 cm |
| Update rate | I²C > 200 Hz typical; ANT up to 200 Hz |
| Beam divergence | **4.77°** |
| Interface | I²C or ANT; SPI configurable via Nordic SDK |
| Supply | 4.75–5.25 VDC |
| Current | 2 mA idle, 85 mA during acquisition |
| Emitter | 940 nm LED (not a laser) |
| Size / mass | 52.2 × 21.2 × 24.0 mm, 14.6 g |

**Reflectivity conditioning — corrected.** The v3 *does* carry a published target condition: **70 %
reflective**, applied by Garmin to both the 40 m range and the 270 Hz update rate. It is a single
condition, not a range-versus-reflectivity table like the ams-OSRAM and Benewake parts publish, so you
still cannot read a dark-target range off it — but the 40 m figure is explicitly a 70 %-reflective-target
figure and should always be quoted that way. A 70 % target is roughly four times as reflective as the
18 % grey card the dToF parts in §2 are specified against, so v3 and TMF8806 numbers are not comparable
as printed.

For the **v4 LED**, no Garmin-hosted specification document could be retrieved on 2026-09-12 (the
`static.garmin.com` PDF paths tried all returned HTTP 404). Every v4 number in the table above is
therefore **vendor-page-verified only**, and whether Garmin publishes a target-reflectivity condition
for the v4's 10 m is **unverified — not "not published"**. Do not repeat the v3 mistake and assume the
absence of a condition on a reseller page means the manufacturer publishes none.

**Verdict for this robot: both are the wrong tool.** v3's 0.46° beam is a laser pointer — at 2 m it
illuminates a spot roughly 16 mm across, so it will thread straight past a cat's leg and report the wall
behind. v4's 4.77° is better (≈170 mm spot at 2 m) but $59.95 × 76 sensors is absurd. They exist in the
catalogue for drone altimetry, not for perimeter sensing. Both are purchase-limited to 2 units, which by
itself rules out a tiled perimeter ring.

---

## 6. Sharp analog and digital IR rangers

**Correction (verified 2026-09-12 against the Sharp datasheets themselves):** an earlier revision of this
document said "Sharp publishes no reflectivity-conditioned range table — not published" and called these
parts "intensity-triangulation". **Both statements were wrong, and they were wrong in opposite
directions.** Sharp publishes the reflectivity condition on the face of the specification table, and
Sharp also publishes a two-reflectance response plot showing that reflectance barely moves the output.
The corrected text is below; §6 reason 2 has been rewritten.

### 6.1 GP2Y0A21YK0F — Adafruit PID 164, $14.95, 65 in stock (2026-09-12)

<https://www.adafruit.com/product/164> · Sharp datasheet sheet no. **E4-A00201EN**

**Sharp's published condition (datasheet "Electro-optical Characteristics", Note 1):** *"Using reflective
object : White paper (Made by Kodak Co., Ltd. gray cards R-27・white face, reflectance; 90%)"*, at
Ta = 25 °C, Vcc = 5 V. Every headline number carries it:

| Parameter | Symbol | Condition | Min | Typ | Max |
|---|---|---|---|---|---|
| Distance measuring range | ΔL | Note 1 (Kodak R-27 white, 90 %) | **10 cm** | — | **80 cm** |
| Output voltage | Vo | L = 80 cm, Note 1 | 0.25 V | **0.4 V** | 0.55 V |
| Output voltage differential | ΔVo | between L = 10 cm and L = 80 cm, Note 1 | 1.65 V | **1.9 V** | 2.15 V |
| Average supply current | Icc | L = 80 cm, Note 1 | — | 30 mA | 40 mA |

**Adafruit's "3 V at 10 cm" is not supportable.** Sharp's own ΔVo is 1.9 V typical between 10 cm and
80 cm, and 0.4 V typical at 80 cm, which puts 10 cm at **≈2.3 V** — exactly what Pololu's page quotes.
Use 2.3 V, not 3 V.

Supply 4.5–5.5 V recommended, 30 mA average drawn *in short bursts* — Pololu explicitly recommends *"a
10 µF capacitor or larger across power and ground close to the sensor."* Update period is **38.3 ± 9.6 ms**
per Sharp's Fig. 1 timing chart (≈26 Hz), with the first output unstable and settling within MAX 5.0 ms.
Operating temperature −10 to +60 °C. Housing is conductive; Adafruit warns to use rubber gaskets against
a metal chassis.

### 6.2 GP2Y0A02YK0F — Adafruit PID 1031, $15.95, 17 in stock (2026-09-12)

<https://www.adafruit.com/product/1031>

Same datasheet structure and the **same Note 1** — *"Using reflective object : White paper (Made by Kodak
Co., Ltd. gray cards R-27 white face, reflectance; 90%)"*. Distance measuring range **20–150 cm**; output
voltage at L = 150 cm **0.25 / 0.4 / 0.55 V** (min/typ/max); Sharp's Fig. 2 again plots white paper 90 %
against gray paper 18 %. 5 V supply. Current and update rate **not published on the Adafruit page** (they
are in the Sharp datasheet). Adafruit's own advice on that page: *use sonar above 1 metre.*

Adafruit's "3 V at 20 cm" is the same reseller rounding as PID 164 — Sharp specifies the far-end point,
not the near-end point.

### 6.3 Sharp digital carriers — both **no longer stocked**

- **GP2Y0D810Z0F with Pololu carrier, PID 1927, $8.95 — "No longer stocked".** Adafruit's status string
  read on 2026-09-12 is *"No longer stocked"*, not *"Discontinued"*; the practical effect is the same
  (unbuyable) but the page does not use the word "discontinued". 20–100 mm, digital high/low
  (not a distance), ~400 Hz sample rate, 2.56 ms steady-state update, 2.7–6.2 V, ~5 mA. Adafruit
  recommends the ST VL6180X as the replacement.
- **GP2Y0D805Z0F with Pololu carrier, PID 3025 — No longer stocked.** 0.5–5 cm digital.

**These are the Pololu products Adafruit carries.** Adafruit does not stock Pololu's own OPT3101 or
VL53L1X-based distance modules (e.g. Pololu 4064, 4071); those must be bought from Pololu directly and
are out of this lane's Adafruit scope.

**Why analog Sharp IR is disqualified for this robot.** Two reasons, both structural — and one former
reason that the datasheet refutes:

1. **The response curve is non-monotonic below the minimum range.** Sharp's Fig. 2 shows the output
   rising from 0 V at 0 cm to a peak of about **3.13 V at 5–6 cm**, then falling monotonically to 0.4 V
   at 80 cm. Every voltage on the falling limb therefore has a twin on the rising limb. The correct
   pairing is **not** "5 cm reads like 25 cm": 25 cm reads ≈1.05 V, and 1.05 V on the rising limb is
   about **1.6 cm**. Likewise ≈2.5 V is either ~3.5 cm or ~10 cm. Either way a robot that drives into a
   wall gets a reading that says "not close", and you must guarantee nothing ever gets nearer than 10 cm
   — which for a mobile robot is exactly the case you are trying to detect.
2. **Beam width not published.** Neither the Sharp datasheet, the Adafruit page, nor the Pololu page
   gives a beam angle or spot size. You cannot compute perimeter coverage from an unpublished cone. This
   remains the binding objection.
3. ~~**Reflectance sensitivity.**~~ **Retracted — the datasheet says the opposite.** These are
   *position*-sensitive-detector (PSD) triangulation parts, not intensity parts: the distance is read
   from where the spot lands on the PSD, so signal amplitude is largely divided out. Sharp's **Fig. 2,
   "Example of distance measuring characteristics (output)"**, plots two curves — *"White paper
   (Reflectance ratio 90 %)"* and *"Gray paper (Reflectance ratio 18 %)"* — and they are **very nearly
   coincident across the whole 10–80 cm span** (same plot and same result in the GP2Y0A02YK0F datasheet
   over 20–150 cm). A 5× change in target reflectance barely moves the output. So the claim that black
   fur "reads far short" on a Sharp analog part is unsupported, and the claim that Sharp publishes no
   reflectivity data is simply false — Sharp publishes both the 90 % Kodak R-27 condition on the
   specification table and the 90 %-vs-18 % comparison plot. **Reflectance-blindness is in fact these
   parts' one advantage over the dToF parts in §2**; it is the beam width and the near-field ambiguity
   that disqualify them, not the colour of the target.

---

## 7. Ultrasonic

Ultrasonic is the only technology in this lane that is indifferent to colour and reflectivity in the
optical sense, which makes it the natural complement to dToF for dark fur and dark clothing. It is also
the only one that sees clear glass reliably.

| Product | PID | Price | Stock (2026-09-12) | Range | Beam | Resolution | Supply | Interface |
|---|---|---|---|---|---|---|---|---|
| HC-SR04 + 2 × 10K resistors | 3942 | $3.95 | In stock | 2–400 cm (best 10–250 cm) | 15° | not published | 5 V, 15 mA measuring | trigger/echo GPIO, 40 kHz |
| Ultrasonic Distance Sensor 3V/5V, RCWL-1601 | 4007 | $3.95 | In stock | 2–450 cm (best 10–250 cm) | ±15° to ±20° | 1 mm | 3–5.5 V, 2.2 mA | trigger/echo GPIO |
| US-100 3V/5V | 4019 | $6.95 | In stock | 2–450 cm (best 10–250 cm) | < 15° | 0.3 cm ±1 % | 2.4–5.5 V, 2 mA | HC-SR04 mode **or** 9600 baud UART |
| Maxbotix LV-EZ0 (MB1000) | 979 | $29.95 | 44 in stock | 0–254 in (6.45 m), reports from 6 in | widest in LV-EZ line | 1 inch | 2.5–5.5 V, 2 mA typ | analog Vcc/512 per inch, PWM 147 µs/in, 9600 baud serial |
| Maxbotix LV-EZ4 (MB1040) | 982 | $28.50 | 48 in stock | 0–254 in (6.45 m) | narrowest in LV-EZ line | 1 inch | 2.5–5.5 V, 2 mA typ | analog / PWM / serial |
| Ultrasonic Distance Sensor with I²C, RCWL-1601 | 4742 | $3.95 | **Out of stock** | — | — | — | — | I²C |
| Large Ultrasonic with Horn, UART | 4664 | $28.95 | **No longer stocked** | 28–750 cm with horn, 28–450 cm without | **40° with horn, 75° without** | 1 mm | 3.3–5 V, ≤15 mA avg / ≤50 mA peak | UART 9600 |
| LV-EZ1 (172), LV-EZ2 (980), LV-EZ3 (981), HRLV-EZ0/1/4 (983/984/985), MB7092 (1137), HR-USB-EZ1 (1343), Panel-mount sonar (4665) | — | — | **All no longer stocked** | — | — | — | — | — |

### 7.1 MaxBotix LV-MaxSonar-EZ series, datasheet-level detail

Datasheet: MaxBotix `PD11832e`, "LV-MaxSonar-EZ Series", copyright 2005–2015.

- Detects objects **0 to 254 inches (6.45 m)**; reports range from **6 inches** out to 254 inches at
  1-inch resolution. *"Objects from 0-inches to 6-inches typically range as 6-inches."*
- Datasheet explicitly disclaims sub-6-inch reliability: *"Applications requiring 100% reading-to-reading
  reliability should not use MaxSonar sensors at a distance closer than 6 inches… MaxBotix Inc. does not
  guarantee operational reliability for objects closer than the minimum reported distance."*
- **Read rate 20 Hz.** Power-up runs a 49 ms calibration cycle, then a 49 ms range cycle; the first
  reading takes an extra ~100 ms; *"Range data can be acquired once every 49mS."*
- Supply 2.5–5.5 V, 2 mA typical; *"Recommended current capability of 3mA for 5V, and 2mA for 3V."*
- Outputs: analog **(Vcc/512) per inch** (≈9.8 mV/in at 5 V, ≈6.4 mV/in at 3.3 V), pulse width
  **147 µs/inch**, and 9600 8N1 serial as ASCII `R` + three digits + CR.
- **The beam patterns are published as four detection zones (A, B, C, D) against four calibrated dowel
  targets on a 30 cm grid** — not as a single beam angle. *"The actual beam angle changes over the full
  range… smaller targets are detected over a narrower beam angle and a shorter distance."*
- **MaxBotix publishes people-detection guidance directly.** For the EZ0 (MB1000), the widest and most
  sensitive of the line: *"Can detect people up to approximately 10 feet"* (≈3.05 m), and it is listed
  as *"Great for people detection"*, *"Autonomous navigation"*, *"Collision avoidance"*. The datasheet
  also states that *"the detection area to the 1-inch diameter dowel, in general, represents the area
  that the sensor will reliably detect people."*
- The EZ4 (MB1040) is *"the narrowest beam width sensor that is also the least sensitive to side objects"*
  — good for a corridor, bad for perimeter.

**Ultrasonic verdict for this robot.** The LV-EZ0's ~3 m people-detection claim and its colour-blindness
make it the best non-optical human detector in the Adafruit catalogue. Against that:

- **Mutual interference is severe.** N ultrasonic transducers at 40 kHz on one 350 mm chassis will hear
  each other. MaxBotix parts support chained triggering to time-multiplex; HC-SR04 clones do not, so you
  must sequence them in firmware. With a 49 ms cycle and 8 sensors round-robin you get a 2.5 Hz perimeter
  update — too slow for a moving robot.
- **Specular reflection.** A smooth surface at a shallow angle bounces the ping away and reads "clear".
  This is the ultrasonic equivalent of the lidar mirror problem and it hits walls approached at an angle.
- **Soft targets absorb.** Fur, wool, and thick coats attenuate 40 kHz. A cat is acoustically much
  quieter than a cardboard box of the same size. MaxBotix markets the EZ0 as *"Best sensor to detect soft
  object in LV-MaxSonar-EZ line"* precisely because this is a known weakness of the class.
- **Dead zone.** 2 cm (HC-SR04 family) to 15 cm (MaxBotix reported minimum) to 28 cm (the discontinued
  horn sensor). Anything inside that is invisible.
- **No classification whatsoever.**

---

## 8. Short-range optical proximity (VCNL / APDS) and ambient light

These are **not rangers**. They report a reflected-IR count, not a calibrated distance, and their useful
distance is set by how much IR LED current you are willing to burn and how reflective the target is.
None of them should be treated as an obstacle sensor. They are listed here for completeness because the
lane brief names them and because two of them have a legitimate secondary role.

| Product | PID | Price | Stock (2026-09-12) | Proximity range | Light range | Notes |
|---|---|---|---|---|---|---|
| VCNL4200 Long Distance IR Proximity + Light | 6064 | $6.95 | **Out of stock** | 0 to **1.5 m** (Vishay datasheet 84430 rev 1.8, product summary "0 to 1500" mm; *"Proximity distance up to 1.5 m"*) | 0.003 to 1570 lux, selectable 197/393/786/1573 lux | 940 nm IRED, up to **800 mA** IRED drive, 2.5–3.6 V, I²C slave address **0x51**. Adafruit's own page tempers the claim to a *"practical range 50-100cm"*. Datasheet does **not publish the target reflectivity or size** behind the 1.5 m figure. |
| VCNL4030 Proximity + Lux | 6491 | $5.95 | In stock | 0 to 300 mm | 0.004 to 16 768 lux | I²C address not stated on product page |
| VCNL4040 Proximity + Lux | 4161 | $5.95 | In stock | 0 to 200 mm | 0.0125 to 6553 lux | I²C address not stated on product page |
| VCNL4020 Proximity + Light | 5810 | not read | listed | not read | not read | listed in catalogue, not fetched |
| APDS9960 Proximity, Light, RGB, Gesture | 3595 | $7.50 | In stock | *"Up to a few centimeters"*, 8-bit proximity | RGB + clear | Gesture range **not published**; I²C address **not published on the product page** |
| APDS9999 Proximity, Lux, Colour | 6461 | $7.50 | In stock | not read | not read | newer part |
| Proximity Trinkey (USB APDS9960 dev board) | 5022 | $9.95 | 5 in stock | as APDS9960 | — | USB dev board, not a robot part |
| VCNL4010 | 466 | — | **No longer stocked** | — | — | — |
| LTR-329 Light Sensor | 5591 | $4.50 | In stock | **none — light only** | visible + IR | no proximity function at all |
| LTR-303 Light Sensor | 5610 | $4.50 | 9 in stock | **none — light only** | visible + IR | no proximity function at all |
| MAX44009 Wide-range Lux | 6498 | $12.50 | In stock | **none — light only** | lux | no proximity function |
| STEMMA Reflective Photo Interrupt TCRT1000 | 5913 | $4.95 | 86 in stock | millimetres | — | cliff / edge detection only |

**The legitimate role for these parts on this robot is cliff detection and bumper-skirt last-inch
detection, not perimeter sensing.** A VCNL4040 pointed down at the floor from the chassis edge detects a
stair drop-off in under 200 mm, which every optical ranger in §2 handles badly because of its own minimum
range. Two or four of them around the skirt costs $12–24 and closes the near-field hole.

**LTR-329 and LTR-303 answer a different question entirely.** They measure ambient lux. That is
operationally useful here — every dToF range number in §2 and §3 is conditioned on ambient light, so an
LTR-329 lets the robot *know* when it has moved from a 350-lux room into a 10-klux sunbeam and derate its
own trust in the TMF8806 accordingly. That is a genuine system-level reason to spend $4.50, but it is not
obstacle detection.

---

## 9. Answering the four detection requirements

### (a) Any collidable obstacle

Only the RPLIDAR A1 delivers this from one part, and only in one plane. Every fixed ranger in this lane
leaves a cone-shaped hole between adjacent sensors and above/below its own cone. A 350 mm chassis with a
12-sensor TMF8806 ring (12 × $12.50 = $150, 12 I²C addresses all fixed at 0x41, so you need a TCA9548A
multiplexer or per-sensor enable pins) covers 360° horizontally at one height only. Neither approach sees
a table overhang at 700 mm on a 1200 mm robot.

### (b) Humans

- Best published evidence in the lane: **MaxBotix LV-EZ0, "Can detect people up to approximately 10
  feet"**, with the 1-inch dowel pattern defined as the reliable people-detection zone. Colour-blind, so
  dark clothing does not defeat it.
- TMF8806 at 3.25 m against an 18 % grey card in 350 lux indoor light will see a person in normal clothing
  across a room. Dark clothing behaves worse than the 18 % grey card.
- RPLIDAR A1 sees the leg cross-section at whatever height the plane sits.
- **Nothing in this lane identifies a human as a human.** No part here does thermal, no part here does
  mmWave vital-sign or micro-Doppler. That capability is entirely absent from Adafruit's non-ST ranging
  catalogue and must come from another lane (PIR, thermal IR array, mmWave, or camera).

### (c) Pets, 200–500 mm tall

This is the hardest requirement and the one that eliminates most of the lane.

| Sensor | Verdict for a 200 mm pet at floor level |
|---|---|
| RPLIDAR A1 | **Only if the scan plane is mounted below 200 mm.** At 100 mm mounting height the A1 sees the cat's body. At 300 mm it sees nothing. The A1's own body is ~60 mm tall, so a 100 mm plane is mechanically achievable on a 350 mm chassis. Dark fur degrades a triangulation scanner specified against white objects; magnitude **not published**. |
| TMF8806 | Yes within ~1.5–3 m. 30° long-range cone mounted at 150 mm covers floor to ~950 mm at 1.5 m. Fur is darker than 18 % grey; derate the 3250 mm figure hard. |
| TMF8801 | Yes within ~1.0–1.7 m. Same geometry, less budget. |
| MaxBotix LV-EZ0 | Marginal. Widest and most sensitive beam in the line, and marketed as the best soft-object detector, but fur absorbs 40 kHz and the 1-inch-dowel zone is the people zone, not the cat zone. **Not published** for animals. |
| HC-SR04 / RCWL-1601 / US-100 | Marginal at best. 15° cone, soft-target absorption, 2 cm–4.5 m nominal but "best 10–250 cm". |
| Garmin v3 | **No.** 0.46° beam threads past a cat entirely. |
| Garmin v4 | Possible at short range, economically absurd, purchase-limited to 2. |
| TFmini (discontinued) | Needs an 8 cm target at 2 m — a cat's body qualifies, a cat's leg does not. 2.3° beam, so useless for coverage. |
| Sharp GP2Y0A21 / A02 | **No.** Non-monotonic below minimum range and unpublished beam width. Note the corrected reason: these PSD parts are *not* strongly reflectance-dependent — Sharp's Fig. 2 shows 90 % white and 18 % grey giving almost the same curve — so dark fur is not what defeats them. Range (80 cm / 150 cm) and the unpublished cone are. |
| VCNL / APDS | **No.** Centimetres, not metres. |

### (d) Distinguish human vs pet vs inanimate object

**Nothing in this lane can do this at the sensor.** Every product here returns either a scalar distance, a
scalar proximity count, or a planar point cloud. Classification must be inferred in software:

- **Height profile** — the strongest available cue, and it requires *at least two* scan planes or a
  multizone sensor. Two RPLIDAR-class planes at 100 mm and 800 mm will separate "returns at both heights"
  (human) from "returns only low" (pet or low furniture) from "returns only high" (table top). Adafruit
  does not sell a second affordable scanning plane, so this means either two A1s at $99.95 each with the
  rotational-interference problem unaddressed, or one A1 plus a ring of fixed rangers at a second height.
- **Motion across frames** — pets and humans move, furniture does not. The A1 at 5.5 Hz supports frame
  differencing; a 20 Hz ultrasonic ring does not resolve shape well enough.
- **Cluster width** — a human leg pair is a distinctive double-blob at 1° angular resolution; a cat body
  is a single 150–300 mm blob. This is real but fragile.

If genuine human/pet/object classification is a hard requirement, this lane cannot supply it and the
answer has to come from thermal IR array, mmWave presence radar, or a camera.

---

## 10. Recommendation for a 350 mm, 600–1200 mm robot

1. **RPLIDAR A1 (PID 4010, $99.95) mounted with the scan plane at ≈100 mm** as the primary 360° obstacle
   ring. This is the only single-purchase 360° map in the catalogue and the only thing that will see a
   200 mm pet all the way around the robot. Budget two 5 V rails and 170 g.
2. **Four to eight TMF8806 (PID 6501, $12.50 each)** as a second sensing plane at ≈700–900 mm, aimed
   level, to catch table overhangs, counter edges, and torsos that the floor plane misses. Their 30° long
   cone means four gives you 120° of forward arc; eight gives 240°. Note all TMF8806 share I²C address
   0x41, so plan a multiplexer or sequenced enable lines.
3. **One or two MaxBotix LV-EZ0 (PID 979, $29.95)** facing forward as the colour-blind cross-check: glass
   doors, black matte furniture, and dark clothing all defeat the optical sensors and not the acoustic
   one. Accept 20 Hz and sequence them against each other.
4. **Two to four VCNL4040 (PID 4161, $5.95)** pointed at the floor from the chassis skirt for cliff
   detection, which no ranger above handles inside its own minimum range.
5. **One LTR-329 (PID 5591, $4.50)** so the robot knows its own ambient-light condition and can derate
   every published dToF range accordingly.
6. **Do not buy** Garmin LIDAR-Lite v3 or v4 for perimeter work, do not buy Sharp analog IR for a robot
   that can approach closer than the sensor's minimum range, and do not treat any VCNL or APDS part as an
   obstacle sensor.
7. **Watch for an Adafruit TMF8828 breakout.** When it ships it collapses items 2 and part of 1 into a
   handful of parts with real per-zone maps. It was not purchasable on 2026-09-12.

---

## Sources

- [Adafruit TMF8801 Time of Flight Distance Sensor — PID 6522](https://www.adafruit.com/product/6522)
- [Adafruit TMF8801 Learn guide](https://learn.adafruit.com/adafruit-tmf8801-time-of-flight-distance-sensor)
- [Adafruit TMF8806 Time of Flight Distance Sensor — PID 6501](https://www.adafruit.com/product/6501)
- [ams-OSRAM TMF8801 datasheet DS000648 v10-00](https://look.ams-osram.com/m/277d0c5095367cb7/original/TMF8801-DS000648.pdf)
- [ams-OSRAM TMF8806 datasheet DS001097 v4-00](https://look.ams-osram.com/m/6df9ed5e6992daaa/original/TMF8806-Time-of-flight-sensor.pdf)
- [ams-OSRAM TMF8820/21/28 datasheet DS000693 v5-00](https://cdn.sparkfun.com/assets/0/d/8/3/a/TMF8828_datasheet.pdf)
- [ams-OSRAM TMF8821 product page](https://ams-osram.com/products/sensors/direct-time-of-flight-sensors-dtof/ams-tmf8821-configurable-4x4-multi-zone-time-of-flight-sensor)
- [ams-OSRAM TMF8828 product page](https://ams-osram.com/products/sensors/direct-time-of-flight-sensors-dtof/ams-tmf8828-configurable-8x8-multi-zone-time-of-flight-sensor)
- [Adafruit blog: TMF8828 multi-zone ToF from ams OSRAM (2024-08-27)](https://blog.adafruit.com/2024/08/27/tms8828-multi-zone-time-of-flight-sensor-from-ams-osram/)
- [Slamtec RPLIDAR A1 — Adafruit PID 4010](https://www.adafruit.com/product/4010)
- [Slamtec RPLIDAR A1 datasheet (Adafruit mirror)](https://cdn-shop.adafruit.com/product-files/4010/4010_datasheet.pdf)
- [TFmini Infrared ToF Distance Sensor — Adafruit PID 3978 (no longer stocked)](https://www.adafruit.com/product/3978)
- [TFmini product manual SJ-PM-TFmini-T-01 A03 (Adafruit mirror)](https://cdn-shop.adafruit.com/product-files/3978/3978_manual_SJ-PM-TFmini-T-01_A03ProductManual_EN.pdf)
- [Garmin LIDAR-Lite v3 — Adafruit PID 4058](https://www.adafruit.com/product/4058)
- [Garmin LIDAR-Lite v3 Operation Manual and Technical Specifications (primary)](https://static.garmin.com/pumac/LIDAR_Lite_v3_Operation_Manual_and_Technical_Specifications.pdf)
- [Garmin LIDAR-Lite v4 LED — Adafruit PID 4441](https://www.adafruit.com/product/4441) — no Garmin-hosted v4 specification document could be retrieved on 2026-09-12; all v4 numbers are reseller-page only
- [Sharp GP2Y0A21YK0F IR distance sensor — Adafruit PID 164](https://www.adafruit.com/product/164)
- [Sharp GP2Y0A02YK IR distance sensor — Adafruit PID 1031](https://www.adafruit.com/product/1031)
- [Sharp GP2Y0A21YK0F datasheet, sheet no. E4-A00201EN (primary)](https://global.sharp/products/device/lineup/data/pdf/datasheet/gp2y0a21yk_e.pdf)
- [Sharp GP2Y0A02YK0F datasheet (primary, Pololu mirror)](https://www.pololu.com/file/0J156/gp2y0a02yk_e.pdf)
- [Pololu GP2Y0A21YK0F analog distance sensor page](https://www.pololu.com/product/136)
- [Sharp GP2Y0D810Z0F with Pololu carrier — Adafruit PID 1927 (discontinued)](https://www.adafruit.com/product/1927)
- [Sharp GP2Y0D805Z0F with Pololu carrier — Adafruit PID 3025 (no longer stocked)](https://www.adafruit.com/product/3025)
- [HC-SR04 Ultrasonic Sonar Distance Sensor — Adafruit PID 3942](https://www.adafruit.com/product/3942)
- [RCWL-1601 Ultrasonic Distance Sensor 3V/5V — Adafruit PID 4007](https://www.adafruit.com/product/4007)
- [US-100 Ultrasonic Distance Sensor — Adafruit PID 4019](https://www.adafruit.com/product/4019)
- [Maxbotix LV-EZ0 — Adafruit PID 979](https://www.adafruit.com/product/979)
- [Maxbotix LV-EZ4 — Adafruit PID 982](https://www.adafruit.com/product/982)
- [LV-MaxSonar-EZ series datasheet PD11832e](https://www.fdi.ucm.es/profesor/mendias/TFE/recursos/PMOD/LV-MaxSonar-EZ_Datasheet.pdf)
- [Large Ultrasonic Sensor with Horn, UART — Adafruit PID 4664 (no longer stocked)](https://www.adafruit.com/product/4664)
- [Adafruit VCNL4200 Long Distance IR Proximity and Light Sensor — PID 6064](https://www.adafruit.com/product/6064)
- [Vishay VCNL4200 datasheet, document 84430 rev 1.8, 2025-03-17](https://www.vishay.com/docs/84430/vcnl4200.pdf)
- [Adafruit VCNL4030 Proximity and Lux Sensor — PID 6491](https://www.adafruit.com/product/6491)
- [Adafruit VCNL4040 Proximity and Lux Sensor — PID 4161](https://www.adafruit.com/product/4161)
- [Adafruit APDS9960 Proximity, Light, RGB and Gesture Sensor — PID 3595](https://www.adafruit.com/product/3595)
- [Adafruit Proximity / Light / LIDAR category 689](https://www.adafruit.com/category/689)
- [Adafruit Proximity category 57](https://www.adafruit.com/category/57)
- [Adafruit Sonar / Ultrasonic category 686](https://www.adafruit.com/category/686)
