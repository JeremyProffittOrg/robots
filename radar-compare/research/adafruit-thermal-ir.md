# Adafruit Thermal / Infrared People-Sensing Products — Datasheet-Grade Survey

**Lane:** `adafruit-thermal-ir`
**Application:** 360-degree perimeter detection for a mobile robot, 350 mm square or round footprint, 600–1200 mm tall.
**Requirements under test:** (a) any collidable obstacle, (b) humans, (c) pets 200–500 mm tall, (d) human vs pet vs inanimate discrimination.
**All prices read from adafruit.com on 2026-09-12.**

> **Adversarial verification pass, 2026-09-12.** Every headline number below was re-checked against the
> primary source — the manufacturer datasheet PDF where one exists, the Adafruit product page for price
> and stock. PDFs opened and text-extracted in this pass: Panasonic Grid-EYE AMG88 (02 Apr 2017),
> Melexis MLX90640 (Rev 12, 03 Dec 2019, Table 15 and Table 14), Melexis MLX90614 (doc server Rev 012 /
> datasheet Rev 021, 02-Jun-2026, Table 19), ST STHS34PF80 (DS13916, Table 3 and §1). Corrections made
> in this pass are marked inline and listed here: the Grid-EYE per-pixel 7.7° figure is a **half angle**,
> not a half-power width; the 4407 and 4469 boards have **different dimensions and weight**; the 55°
> MLX90640 does dilute a bare face beyond **6.7 m**; the 110° part dilutes a face beyond **3.3 m**, not
> ~4 m; the two MLX90614 boards carry **different Melexis order codes** (BAA and AAA) though both are
> 90° xAA optics; and **no detection range is published for the UTi165H/UTi165K** — only a 1 m optimal
> measuring distance. Everything else listed below was confirmed verbatim.

---

## 0. The headline finding, stated first

**No thermal or infrared sensor in Adafruit's catalogue can satisfy requirement (a).** A chair leg, a door frame, a cardboard box, a table edge and a wall are all at room temperature. Their apparent temperature difference from the background is approximately zero, which is below the noise floor of every device listed below. A thermopile or TMOS array measures *radiated flux*, not *geometry*. It is a human/animal channel, and nothing else. Requirement (a) must be served by a time-of-flight, ultrasonic, or optical sensor in another lane.

Within requirements (b), (c) and (d), the ordering is unambiguous and is set by **angular resolution**, not by temperature sensitivity:

| Device | Pixels | Can detect a human? | Can detect a cat? | Can discriminate human vs pet? |
|---|---|---|---|---|
| MLX90640 55° (4407) | 32×24 | Yes, to >7 m | Yes, to ~3 m | Yes, to ~3 m |
| MLX90640 110° (4469) | 32×24 | Yes, to >7 m | Yes, to ~1.5 m | Yes, to ~1.5 m |
| AMG8833 Grid-EYE (3538/3622) | 8×8 | Yes, to ~5 m | Yes, to ~2.4 m | Marginally, to ~1.2 m |
| STHS34PF80 (6426) | 1 | Yes, to 4 m | Not published | No — physically impossible |
| PIR (189 / 4871 / 5578) | 1 | Moving only | Moving only | No |
| MLX90614 (1747/1748) | 1 | Only at close range | Only at close range | No |

---

## 1. Complete product enumeration

The starting search `https://www.adafruit.com/search?q=camera+stema+ir` returns exactly four items, of which three are thermal:

| Rank | Product | ID | Price (2026-09-12) |
|---|---|---|---|
| 1 | Adafruit MLX90640 IR Thermal Camera Breakout – 55 Degree | 4407 | $74.95 |
| 2 | Adafruit AMG8833 IR Thermal Camera Breakout – STEMMA QT | 3538 | $44.95 |
| 3 | Adafruit MLX90640 24×32 IR Thermal Camera Breakout – 110 Degree FoV | 4469 | $74.95 |
| 4 | *Bots! Robotics Engineering* (book, not a sensor) | 4348 | $14.95 |

Broadening to `thermal camera`, `PIR`, `motion sensor`, `thermopile`, `Grid-EYE`, `NoIR camera` yields the full set below.

### 1.1 Multi-pixel thermal arrays (the only devices that can classify)

| Product | ID | Price | Stock (2026-09-12) | Array | FoV H×V |
|---|---|---|---|---|---|
| Adafruit MLX90640 IR Thermal Camera Breakout – 55 Degree | 4407 | $74.95 | **4 in stock** | 32×24 (768 px) | 55° × 35° |
| Adafruit MLX90640 24×32 IR Thermal Camera Breakout – 110 Degree FoV | 4469 | $74.95 | **Out of stock** | 32×24 (768 px) | 110° × 75° |
| Adafruit AMG8833 IR Thermal Camera Breakout – STEMMA QT | 3538 | $44.95 | 57 in stock | 8×8 (64 px) | 60° × 60° |
| Adafruit AMG8833 IR Thermal Camera FeatherWing | 3622 | $44.95 | In stock | 8×8 (64 px) | 60° × 60° |

### 1.2 Single-element IR presence / thermopile

| Product | ID | Price | Stock | Notes |
|---|---|---|---|---|
| Adafruit STHS34PF80 IR Presence / Motion Sensor – STEMMA QT / Qwiic | 6426 | $14.95 | In stock | ST TMOS, 80° FFOV, **new Oct 2025**; Adafruit's stated replacement for the MLX90614 |
| Melexis MLX90614 Contact-less IR Sensor – 3 V (MLX90614ESF-**BAA**) | 1747 | $15.95 | **No longer stocked** | 90° FoV; object range −70 °C to +380 °C; Adafruit redirects to the AMG8833 |
| Melexis MLX90614 Contact-less IR Sensor – 5 V (MLX90614ESF-**AAA**, per the 1748 product page — *different order code from 1747*, same x**AA** optical family) | 1748 | $15.95 | **No longer stocked** | 90° FoV; object range −70 °C to +380 °C; Adafruit redirects to the STHS34PF80 |

The 90° figure is **datasheet-verified, not just vendor-page**: Melexis MLX90614 datasheet (doc server Rev 012, datasheet Rev 021, 02-Jun-2026) Table 19 "FOV summary" gives "Type x**AA** … Width zone 1 = 90°", against 35° for xCC, 10° for xCF, 12° for xCH, 5° for xCI and 13° for xCK. Both 1747 and 1748 are xAA parts, so both are 90°. The same datasheet repeats the MLX90640's warning: accuracy is "valid if the object fills the FOV of the sensor completely", and "the measured value is the average temperature of all objects in the Field Of View" — which for a 90° cone is the room, not the person.

### 1.3 PIR (pyroelectric motion) — motion only, no presence, no classification

| Product | ID | Price | Stock | Range | FoV |
|---|---|---|---|---|---|
| PIR (motion) sensor | 189 | $9.95 | **Out of stock** | ~7 m (~20 ft) | 120° cone |
| Breadboard-friendly Mini PIR Motion Sensor with 3-Pin Header | 4871 | $3.95 | In stock | 2–5 m | 100° |
| Mini PIR Sensor with Time and Sensitivity Control – BS612 | 5578 | $1.95 | In stock | ~5 m (lens focused at 5 m) | 120° |

### 1.4 Handheld thermal imagers (not embeddable, listed for completeness)

| Product | ID | Price | Stock | Array | FoV | Range/accuracy |
|---|---|---|---|---|---|---|
| Thermal Camera Imager for Fever Screening – UTi165H | 4578 | $250.00 (was $524.95) | 5 in stock | 160×120 | 56° (H) × 42° (V) | 30–45 °C, ±0.5 °C at 1 m, <9 Hz |
| Thermal Camera Imager with USB Video Output – UTi165K | 4579 | $499.95 | 91 in stock | 160×120 | 56° (H) × 42° (V) | 30–45 °C, ±0.5 °C at 1 m, <9 Hz |

**No detection range is published for either imager, and none should be inferred.** The 4578 spec table gives only "Minimum measuring distance: 15cm" and "Optimal measuring distance: 1 meter", with "Accuracy ±0.5˚C @1m", "IFOV 6mrad", "Thermal imaging sensitivity ＜50mk" and "Infrared bandwidth 8~14μm". A claim that these units "work to about 10 m" appears nowhere on the vendor page and is not supported by any primary source found in this pass. Treat 1 m as the only stated working distance.

These are battery-powered handhelds with a 2.8" 320×240 LCD. The UTi165K adds USB-C real-time video out, which is in principle machine-readable, but the 30–45 °C measurement window is tuned for fever screening and clips everything at room temperature. Not suitable.

### 1.5 Explicitly excluded

- **MLX90393 (Adafruit 4022, $9.95)** — this is a **triple-axis magnetometer**, ±5–50 mT, ~500 Hz, I²C/SPI. It is **not a thermal sensor**. The similar part number to MLX90614/MLX90640 is the only connection. Excluded.
- **LIS3MDL (4479, $9.95)** — also a magnetometer. Excluded.
- **Raspberry Pi NoIR camera modules** (3100 $29.95, 5659 $25.00, 5660 $38.50, 3415, 5658) — "NoIR" means the *IR-cut filter has been removed*, extending sensitivity to roughly 850–1000 nm **near**-infrared. This is a silicon imager. It does **not** sense body heat, which radiates at 8–14 µm. A NoIR camera in a dark room sees nothing without an active 850 nm illuminator, and even then it images reflected NIR, not thermal emission. It belongs in the camera lane, not this one.
- **"Thermopile" search** on adafruit.com returns only thermoplastic and filament products. Adafruit does not stock a bare thermopile array beyond the parts above.
- **Adafruit does not sell an MLX90641 (16×12)** in any form. Verified by search; the MLX90641 is available from Seeed (Grove), Waveshare, and Evelta, but is out of lane here.

---

## 2. The two array sensors in full detail

### 2.1 Panasonic AMG8833 Grid-EYE — Adafruit 3538 / 3622

All values below are quoted from the Panasonic *Infrared Array Sensor Grid-EYE (AMG88)* datasheet dated **02 Apr. 2017**, high-performance high-gain column, which is the AMG8833 variant. Confidence: **datasheet-verified**.

| Parameter | Value (verbatim) | Condition |
|---|---|---|
| Number of pixels | "64 (Vertical 8 × Horizontal 8 Matrix)" | — |
| Viewing angle | "Typical 60 °" | horizontal **and** vertical, per the viewing-field figure |
| Each pixel's viewing angle | "Central 4 pixels (Pixel No. 28, 29, 36, 37) viewing angle (half angle): horizontal direction 7.7 ° (Typical) vertical direction 8 ° (Typical)" | the datasheet figure is titled "Each pixel's viewing angle (**half angle**)" — **not** half-power. Read literally, one pixel's full acceptance cone is 15.4 ° H, roughly twice the 7.5 ° pixel pitch, so adjacent pixels overlap heavily and a point target bleeds into its neighbours. Verified against the PDF, 02 Apr 2017, "Optical properties" figure (2) |
| Optical axis gap | "Sensor's optical center (the origin of graph below) gap: within ±5.6 ° (Typical) (Both horizontal and vertical directions)" — spec table wording is "Within Typical ±5.6 °" | both H and V — **this is 0.75 of a pixel of boresight error** |
| Temperature accuracy | "Typical ±2.5 °C" | high-gain part |
| Temperature range of measuring object | "0 °C to 80 °C" | high-gain part |
| Temperature output resolution | "0.25 °C" | LSB size |
| **NETD** | "Typ. 0.05 °C … 1 Hz" / "Typ. 0.16 °C … 10 Hz" | "It is calculated from 4 pixels of centers" |
| **Human detection distance** | "7 m or less (reference value)" | "To have more than 4 °C of temperature difference from background. Detection object size: 700 × 250 mm (Assumable human body size)" |
| Frame rate | "Typical 10 frames/sec or 1 frame/sec" | only these two |
| Current consumption | "Typical 4.5 mA (normal mode)", "Typical 0.2 mA (sleep)", "Typical 0.8 mA (stand-by)" | — |
| Setup time | "Typical 50 ms (Time to enable communication after setup)"; **"Typical 15 s (Time to stabilize output after setup)"** | — |
| Supply | "3.3 V.DC ±0.3 V.DC or 5.0 V.DC ±0.5 V.DC" | AMG8833 is the 3.3 V part |
| Interface | "I²C (fast mode)" | 400 kHz |
| I²C addresses | "2 (I²C slave address)": `1101000` = 0x68 (AD_SELECT to GND), `1101001` = 0x69 (AD_SELECT to VDD) | **only two devices per bus** |
| Thermistor (die temp) | range −20 °C to 80 °C, resolution "0.0625 °C" | on-chip reference |

On the Adafruit breakout 3538 the default address is **0x69**, changeable to **0x68** by bridging the `Addr` jumper (vendor-page/learn-guide verified). The board regulates to 3.3 V and accepts 3–5 V in, with STEMMA QT / Qwiic connectors and an interrupt pin.

**Read the human-detection condition carefully.** 7 m is *not* a classification range. It is the range at which a 700 × 250 mm body, 4 °C hotter than its background, still produces a signal distinguishable from noise in a single pixel. At 7 m one Grid-EYE pixel covers 918 mm square. The 700 × 250 mm target fills 21 % of it, so the apparent rise is 0.21 × 4 = **0.83 °C**, which is about 5× the 10 Hz NETD of 0.16 °C. The arithmetic checks out — and it also tells you that at 7 m the datasheet's own 700 mm-wide body is **0.76 of a pixel wide** (700 ÷ 918), and the 450 mm torso used in §4 is **0.49 of a pixel** wide. Either way it is under one pixel. Nothing can be classified from that.

### 2.2 Melexis MLX90640 — Adafruit 4407 (55°) and 4469 (110°)

Quoted from the Melexis *MLX90640 32×24 IR array* datasheet, **Revision 12 — December 3, 2019**. Confidence: **datasheet-verified**.

| Parameter | Value (verbatim) | Condition |
|---|---|---|
| Pixels | 768 FIR pixels, "32x24 pixels IR array" | TO-39 4-lead |
| **FoV options** (Table 15) | MLX90640-ESF-**BAA**: "110°" X, "75°" Y, central pointing max 5°<br>MLX90640-ESF-**BAB**: "55°" X, "35°" Y, central pointing max 3° | "The specified FOV is calculated for the wider direction, in this case for the 32 pixels"; FoV defined at the **50 % sensitivity** point |
| NETD (front page) | "0.1K RMS @1Hz refresh rate" | best-case |
| NETD (Table 14, 1 Hz RMS, all pixels) | one variant: average **0.14 K**, min 0.1 K, σ 0.05 K; other variant: average **0.25 K**, min 0.2 K, σ 0.05 K | "To=Ta=25 °C". *The PDF table layout makes the row-to-variant assignment ambiguous under text extraction; treat the front-page 0.1 K as the best pixel, not the frame average.* |
| Refresh rate | "Programmable refresh rate 0.5Hz…64Hz" | **per subpage** — see below |
| Accuracy | frame accuracy ±1 °C to ±2 °C by zone; non-uniformity "NU zone1 ±1 °C ± 2%*abs(To−Ta)" etc. | **"All accuracy specifications apply under settled isothermal conditions only. Furthermore, the accuracy is only valid if the object fills the FOV of the sensor completely."** |
| Supply | VDD min 3 V, typ 3.3 V, max 3.6 V | — |
| Supply current | "Current consumption less than 23mA"; datasheet table IDD max 25 mA | — |
| I²C address | 0x33 default, programmable 0x01–0xFF (stored in EEPROM) | — |
| Operating temperature | "−40 °C ÷ 85 °C" | — |
| Target temperature | "−40 °C ÷ 300 °C" | — |
| **First valid data after POR** | ~40 ms at the 2 Hz default | — |
| **Thermal stabilisation** | "there is thermal stabilization time necessary before the device can reach the specified accuracy – **up to 4 min**" | §12.2.2 |
| Noise caveat | "it is normal that the noise will decrease for high temperature and increase for lower temperatures"; "pixels in the corner of the frame are noisier" | §12.3 |

Adafruit's own board pages list, verbatim: "−40°C to 300°C" target, "−40°C to 85°C" operating, "±2°C (in the 0-100°C range)" accuracy, "Maximum frame rate of 16 Hz" (4407), "0.5Hz…64Hz (0.25 ~ 32 FPS)" (4469), "3.3V-5V supply voltage, regulated to 3.3V", "Less than 23mA", STEMMA QT. **The two boards are not the same size**: 4407 is 25.7 × 17.7 × 16.0 mm, 3.5 g (the 55° can is taller); 4469 is 25.8 × 17.8 × 10.5 mm, 3.0 g. Read from each product page on 2026-09-12.

**The subpage trap.** Adafruit's own parenthetical "(0.25 ~ 32 FPS)" against "0.5Hz…64Hz" is the give-away: the programmed refresh rate applies **per subpage**, and the device alternates subpage 0 and subpage 1 ("It is always subpage 0 to be measured first after POR then subpage 1 and so on alternating"). A *complete* frame therefore arrives at **half** the programmed refresh rate. "16 Hz" means **8 full frames per second**. In the default chess reading pattern, a fast-moving target produces a checkerboard tearing artifact across the two half-frames, which will corrupt any blob-shape classifier unless you either drop to a low rate or classify on a single subpage at half vertical resolution.

**The fill-the-FOV trap.** The ±2 °C accuracy is qualified as valid "only if the object fills the FOV of the sensor completely". For a perimeter sensor watching a human who occupies 5 of 32 columns, that qualification does not hold. Use the MLX90640 for *relative* thermal contrast against a per-pixel background model. Do not use it as a thermometer of people.

---

## 3. The STHS34PF80 (Adafruit 6426) — the interesting new part

ST *STHS34PF80* datasheet **DS13916 Rev 2, July 2023**. Confidence: **datasheet-verified**.

| Parameter | Value (verbatim) |
|---|---|
| Technology | "matrix of floating vacuum thermal transistors MOS (TMOS) connected together and **acting as a single sensing element**" |
| Detection range | "Reach up to 4 meters **without lens for objects measuring 70 x 25 cm²**" |
| Full field of view | "80" degrees — footnote: "Angle to have 50% IR intensity" |
| Operating wavelength | "5 µm to 20 µm" (optical band-pass filter deposited over the sensor, "making it insensitive to visible light and other bands") |
| Object temperature sensitivity | "2000 LSB/°C" (15 °C to 35 °C) |
| Ambient temperature sensitivity | 100 LSB/°C |
| RMS noise | "25 LSBrms" at AVG_TMOS = 32; Table 19 spans 90 LSBrms (2 samples averaged) down to 10 LSBrms (2048 samples) |
| **Equivalent temperature noise** | 25 LSBrms ÷ 2000 LSB/°C = **0.0125 °C RMS** — derived, ~4× better than a Grid-EYE pixel at 1 Hz |
| Ambient temp sensor accuracy | "±0.3 °C" (15 °C to 35 °C), "±0.6 °C" (−10 °C to 60 °C) |
| ODR | 0.25 / 0.5 / 1 / 2 / 4 / 8 / 15 / 30 Hz, plus one-shot |
| Supply voltage | "1.7 V to 3.6 V" |
| Supply current | "10 µA" (128 average @ 1 Hz ODR) |
| I²C address | "The slave address of the STHS34PF80 is SAD=**1011010**" = **0x5A** (also 3-wire SPI) |
| Package | LGA-10L, 3.2 × 4.2 × 1.455 mm |
| Embedded algorithms | presence detection, motion detection, ambient temperature shock detection; "Capable of detecting **stationary** objects"; "Capable of **distinguishing between stationary and moving objects**" |

This part is genuinely better than a PIR: it holds a static human (a PIR cannot), it needs no Fresnel lens (so it fits behind a small aperture), it draws 10 µA, and it costs $14.95. **But it has exactly one sensing element.** It reports "something warm is somewhere in an 80° cone." It cannot say where in the cone, how far, how big, or what shape. For requirement (d) it contributes nothing. Its honest role on this robot is a **cheap always-on wake-up trigger** that gates a more expensive sensor, or a rear-facing "someone is behind me" flag.

Note the I²C address collision: 0x5A is also the fixed MLX90614 address. Not a problem here since the MLX90614 is discontinued.

---

## 4. Pixel-subtense arithmetic — the core of this report

Angular pixel pitch θ = FoV / N. Linear pixel footprint at range *d*: **w = 2·d·tan(θ/2)**.

- Grid-EYE: 60°/8 = 7.5°/px → **w = 0.1311 × d** (131 mm per metre), square.
- MLX90640 55° (BAB): 55°/32 = 1.719° H, 35°/24 = 1.458° V → **30.0 mm/m H, 25.5 mm/m V**.
- MLX90640 110° (BAA): 110°/32 = 3.438° H, 75°/24 = 3.125° V → **60.0 mm/m H, 54.6 mm/m V**.

Targets: human torso 450 mm wide, standing adult 1700 mm tall; cat 250 mm long × 200 mm tall.

### 4.1 AMG8833 Grid-EYE, 8×8, 60° × 60°

| Range | Pixel footprint | Frame width | Torso (450 mm) | Standing adult (1700 mm) | Cat (250×200 mm) | Verdict |
|---|---|---|---|---|---|---|
| 1 ft (0.305 m) | 40 mm | 352 mm | 11.3 px — overflows | 42.6 px — overflows | 6.3 × 5.0 px | Human overfills frame; cat well resolved |
| 3 ft (0.914 m) | 120 mm | 1056 mm | 3.8 px | 14.2 px — overflows | 2.1 × 1.7 px | Human: tall blob, classifiable. Cat: ~3 px blob, marginal |
| 5 ft (1.524 m) | 200 mm | 1.76 m | 2.3 px | 8.5 px — fills column | 1.3 × 1.0 px | Human yes. **Cat = 1 pixel. Shape gone.** |
| 8 ft (2.438 m) | 320 mm | 2.82 m | 1.4 px | 5.3 px | 0.8 × 0.6 px (49 % fill) | Human = 1×5 warm strip. Cat = 1 diluted pixel |
| 10 ft (3.048 m) | 400 mm | 3.52 m | 1.1 px | 4.3 px | 0.6 × 0.5 px (31 % fill) | Human = 1×4 strip out of 64. Cat indistinguishable from a mug of tea |
| 7 m (datasheet limit) | 918 mm | 8.08 m | 0.49 px | 1.9 px | 0.27 × 0.22 px (6 % fill) | Single-pixel flicker. Detection only |

**Grid-EYE classification ceiling: about 1.2 m for a pet, about 2.5 m for a human**, where "classify" means at least a 3 × 3 blob with a measurable aspect ratio.

### 4.2 MLX90640, 55° × 35° (Adafruit 4407)

| Range | Pixel H / V | Frame at that range | Torso | Standing adult | Cat blob |
|---|---|---|---|---|---|
| 1 ft (0.305 m) | 9.1 / 7.8 mm | 317 × 192 mm | 49 px (overflows) | 219 px (overflows) | 27 × 26 px |
| 3 ft (0.914 m) | 27.4 / 23.3 mm | 952 × 577 mm | 16.4 px | 73 px (overflows) | 9.1 × 8.6 ≈ 78 px |
| 5 ft (1.524 m) | 45.7 / 38.8 mm | 1.59 × 0.96 m | 9.8 px | 43.8 px (overflows) | 5.5 × 5.2 ≈ 28 px |
| 8 ft (2.438 m) | 73.2 / 62.1 mm | 2.54 × 1.54 m | 6.2 px | 27.4 px (head clipped) | 3.4 × 3.2 ≈ 11 px |
| 10 ft (3.048 m) | 91.4 / 77.6 mm | 3.17 × 1.92 m | 4.9 px | 21.9 px | 2.7 × 2.6 ≈ 7 px |
| 7 m | 210 / 178 mm | 7.29 × 4.41 m | 2.1 px | 9.5 px | 1.2 × 1.1 ≈ 1.3 px |

### 4.3 MLX90640, 110° × 75° (Adafruit 4469, out of stock)

| Range | Pixel H / V | Frame at that range | Torso | Standing adult | Cat blob |
|---|---|---|---|---|---|
| 1 ft (0.305 m) | 18.3 / 16.6 mm | 871 × 468 mm | 24.6 px | 102 px | 13.7 × 12.0 ≈ 164 px |
| 3 ft (0.914 m) | 54.9 / 49.9 mm | 2.61 × 1.40 m | 8.2 px | 34.1 px | 4.6 × 4.0 ≈ 18 px |
| 5 ft (1.524 m) | 91.5 / 83.1 mm | 4.35 × 2.34 m | 4.9 px | 20.4 px | 2.7 × 2.4 ≈ 6.6 px |
| 8 ft (2.438 m) | 146 / 133 mm | 6.97 × 3.74 m | 3.1 px | 12.8 px | 1.7 × 1.5 ≈ 2.6 px |
| 10 ft (3.048 m) | 183 / 166 mm | 8.71 × 4.68 m | 2.5 px | 10.2 px | 1.4 × 1.2 ≈ 1.6 px |
| 7 m | 420 / 382 mm | 20.0 × 10.7 m | 1.1 px | 4.5 px | 0.6 × 0.5 ≈ 0.3 px |

**Interpretation.** For a 10-pixel-tall human silhouette — roughly the minimum for an aspect-ratio classifier to separate "tall and narrow" from "long and low" — the 55° part reaches well past 7 m, and the 110° part reaches about 3 m. For a 3 × 3 pet blob, the 55° part reaches about 3 m and the 110° part about 1.5 m. **A 110°-FoV MLX90640 has almost exactly the pet-classification range of a 55° part at half the distance.** FoV is bought with range, one for one.

### 4.4 Apparent-temperature dilution (sub-pixel fill)

A pixel reports the flux-weighted average across its whole footprint. If the target covers fraction *f* of the pixel, the apparent rise is *f* × ΔT_surface. Using ΔT = 6 °C for a clothed torso, 12 °C for a bare face and 8 °C for a cat against a 22 °C room:

**Grid-EYE:**

| Target | 0.30 m | 0.91 m | 1.52 m | 2.44 m | 3.05 m | 5.0 m | 7.0 m |
|---|---|---|---|---|---|---|---|
| Clothed torso 450×600, ΔT 6 °C | 6.00 | 6.00 | 6.00 | 6.00 | 6.00 | 3.77 | 1.92 |
| Bare face 200×250, ΔT 12 °C | 12.00 | 12.00 | 12.00 | 5.87 | 3.76 | 1.40 | 0.71 |
| Cat 250×200, ΔT 8 °C | 8.00 | 8.00 | 8.00 | 3.91 | 2.51 | 0.93 | **0.48** |

**MLX90640 55°:** a clothed torso (450 mm) fills a pixel out to 15 m and a cat (250 × 200 mm) out to 7.8 m, so neither is diluted anywhere in this table. The one exception is the **bare face**: the 200 mm horizontal dimension equals the 55° part's H pixel footprint at 200 ÷ 30.0 = **6.7 m**, so at 7 m the face fills 0.95 of a pixel and reads 11.4 °C instead of 12 °C. For practical purposes the 55° part reports the true surface ΔT across the whole range of interest. **110° part:** the H pixel footprint is 60.0 mm/m, so a bare face begins to dilute beyond **3.3 m** (200 ÷ 60.0) and a cat beyond **3.7 m** (V-limited: 200 ÷ 54.6). Corrected 2026-09-12 — the earlier "~4 m and ~4 m" was rounded the wrong way and the "no dilution at all" for the 55° part was true only out to 6.7 m.

This is the single most important practical difference. **On a Grid-EYE, apparent temperature encodes range as much as it encodes species.** A cat at 1 m and a human at 5 m can produce the same pixel value. Any threshold-based classifier built on Grid-EYE absolute values will be wrong in a way that no amount of tuning fixes.

---

## 5. Mounting geometry — the constraint that actually kills pet detection

The pet is 200–500 mm tall. The sensor sits on a 600–1200 mm robot. Assume the sensor is at H = 0.9 m, the mid-point of the stated build height. Vertical half-FoV is α; downward tilt is *t*. The floor first enters the frame at H / tan(α + t); the top of a 200 mm cat first enters at (H − 0.2) / tan(α + t); a 1700 mm head stays in frame out to (1.7 − H) / tan(α − t).

| Sensor (V FoV) | Tilt | Floor first seen | Cat top (200 mm) first seen | Adult head in frame out to |
|---|---|---|---|---|
| Grid-EYE 60° | 0° | 1.56 m | **1.21 m** | 1.39 m |
| Grid-EYE 60° | 15° | 0.90 m | 0.70 m | 2.99 m |
| Grid-EYE 60° | 25° | 0.63 m | 0.49 m | 9.14 m |
| MLX90640 35° V | 0° | 2.85 m | **2.22 m** | 2.54 m |
| MLX90640 35° V | 15° | 1.41 m | 1.10 m | 18.3 m |
| MLX90640 35° V | 25° | 0.98 m | 0.76 m | ∞ |
| MLX90640 75° V | 0° | 1.17 m | **0.91 m** | 1.04 m |
| MLX90640 75° V | 15° | 0.69 m | 0.54 m | 1.93 m |
| MLX90640 75° V | 25° | 0.47 m | 0.36 m | 3.61 m |

Read the first row of each block. **Mounted level, a 55°-FoV MLX90640 at 0.9 m is blind to a cat inside 2.2 m** — the animal is simply below the frame. That is worse than the classification limit computed in §4. Geometry, not optics, is the binding constraint.

The fix is a **15–25° downward tilt**, which pulls the cat-visible boundary in to 0.5–1.1 m and, for the narrow part, simultaneously extends head-in-frame to effectively unlimited range because the upper FoV edge still clears 1.7 m. The 55° × 35° part tilted 20° is the best single configuration in this catalogue for a robot of this size. The 110° part tilted 25° sees a cat from 0.36 m but loses a standing adult's head beyond 3.6 m.

Also note the **Grid-EYE optical axis gap, "within typical ±5.6°"**. On a 7.5° pixel pitch, that is three-quarters of a pixel of unit-to-unit boresight error. If you build a ring of six and want to fuse their frames into one panorama, each unit needs individual extrinsic calibration. The MLX90640's equivalent spec is tighter: max 5° for the 110° part (1.5 px) and max 3° for the 55° part (1.7 px).

---

## 6. Building 360° coverage

| Option | Units for 360° H | Unit price | Ring cost | I²C viability | Practical verdict |
|---|---|---|---|---|---|
| AMG8833 3538 (60°) | 6 | $44.95 | **$269.70** | Only 2 addresses (0x68/0x69) → **needs a TCA9548A mux**; 128 B/frame × 10 Hz × 6 = 7.7 kB/s, trivial | Affordable, in stock, but 8×8 cannot classify |
| MLX90640 4407 (55°) | 7 | $74.95 | **$524.65** | EEPROM-programmable address, but bandwidth-bound (below); only 4 in stock | Best optics, worst cost and bus load |
| MLX90640 4469 (110°) | 4 (20° overlap/seam) | $74.95 | **$299.80** | Same bandwidth issue | Best cost-per-degree — **but out of stock** |
| STHS34PF80 6426 (80°) | 5 | $14.95 | **$74.75** | Single fixed address 0x5A → needs a mux | Cheapest by far, zero classification ability |

**MLX90640 I²C bandwidth arithmetic.** One frame is 768 pixels × 2 bytes = 1536 bytes plus auxiliary registers, call it ~1668 bytes. At 400 kHz fast mode with ACK and addressing overhead, usable throughput is roughly 40 kB/s, so one frame takes **~42 ms of bus time**. Four sensors each delivering 8 full frames/s = 32 frames/s × 42 ms = **1.34 s of bus time per second** — over capacity. A four-sensor MLX90640 ring on a single 400 kHz bus is limited to roughly **5–6 full frames per second aggregate**, i.e. ~1.4 Hz per sensor. Either split across multiple I²C peripherals, or run FM+ at 1 MHz if the host supports it (*not verified against the MLX90640 datasheet in this pass*), or accept the low rate. A Grid-EYE ring has no such problem.

**Latency against closing speed.** Grid-EYE at 10 Hz gives a 100 ms frame. A human walks at ~1.4 m/s; a robot of this class runs at ~0.5 m/s; closing speed ~1.9 m/s. Two frames to confirm a detection costs 200 ms and 380 mm of closure. For a 350 mm footprint that is acceptable at ranges beyond ~1 m and marginal below it. The MLX90640 at a bus-limited 1.4 Hz per sensor gives 714 ms per frame and **1.36 m of closure per confirmed detection** — unusable as a collision-avoidance input, though fine as a slow "there is a person in the room" classifier running behind a fast ToF ring.

---

## 7. Glass, plastic, and windows — why these sensors are blind through them

All three array/presence devices operate in the **long-wave infrared**. The STHS34PF80 states its band explicitly: "operating wavelength between 5 µm and 20 µm", with "an optical band-pass filter … deposited over the sensor". The Grid-EYE uses a silicon lens; the MLX90640 is a silicon-optics TO-39 can. Body heat at 34 °C peaks near 9.4 µm by Wien's law.

Ordinary **soda-lime glass at 1 mm thickness transmits roughly 0.25–3 µm and is opaque above about 3 µm**. Standard optical glass is opaque across 8–14 µm, which is exactly why thermal optics use **germanium** (transmission window roughly 2.5–12 µm at 25 °C) or chalcogenide.

Consequences for this robot, all of them operational, not academic:

1. **A human behind a glass door is thermally invisible.** The sensor sees only the glass surface, which sits near room temperature. No amount of gain helps.
2. **A glass door is also not detectable as an obstacle** by these sensors, because it radiates at room temperature just like the wall beside it. Glass is a double failure: it hides people and it hides itself.
3. **You cannot put a clear dome over the sensor.** Polycarbonate, acrylic (PMMA) and PET are all opaque in LWIR. A visually clear cosmetic window will silently zero the sensor. The only common transparent-in-LWIR plastic is **polyethylene** (LDPE/HDPE film), which is hazy to the eye, is soft, and has absorption bands near 3.4 µm and 6.8 µm. The practical answer is an **open aperture**, or a thin PE window accepting a transmission loss.
4. **Thermal reflections create ghosts.** Polished floors, stainless-steel appliance fronts, mirrors and glossy cabinet doors are good LWIR reflectors. A person standing beside a fridge produces a second, dimmer warm blob in the fridge door. On an 8×8 array, that ghost is indistinguishable from a second person. Expect false positives near kitchens and bathrooms.
5. **Sunlit patches on the floor read as hot.** Direct sun through a window heats floor material well above room temperature — commonly 35–45 °C on dark flooring — which is squarely in the human range. A thermal-only classifier will chase sunbeams. This is the classic Roomba-era failure and it has not gone away.

---

## 8. Ambient drift and its effect on presence detection

Three separate drift mechanisms attack these parts:

**Warm-up drift.** The Grid-EYE datasheet gives "Typical 15 s (Time to stabilize output after setup)". The MLX90640 is far worse: "there is thermal stabilization time necessary before the device can reach the specified accuracy — up to 4 min". A robot that sleeps between patrols and wakes to check a room will produce systematically wrong absolute temperatures for the first several minutes of every wake cycle.

**Self-heating.** Both parts derive absolute temperature by referencing an on-die ambient sensor (Grid-EYE thermistor, 0.0625 °C resolution; MLX90640 integrated Ta sensor). A robot chassis contains motor drivers, a battery and a compute board. Enclosure air temperature rising 8–10 °C above room over a 20-minute run shifts the *whole frame* and, worse, shifts it non-uniformly if airflow is uneven. The MLX90640 accuracy spec is explicitly conditioned on "settled isothermal conditions only" — a moving robot is by definition not isothermal.

**Seasonal / room ambient.** A human's clothed-surface ΔT against a 22 °C room is about 6 °C. Against a 28 °C room in summer it is about 1–2 °C, which on a Grid-EYE at 10 Hz (NETD 0.16 °C) is still detectable but on a heavily diluted sub-pixel target at 3 m collapses to ~0.4 °C — comparable to noise. **Detection range for a thermal sensor is a function of room temperature and drops sharply in warm rooms.** Report this to the user as a design limit, not a bug.

**The only robust mitigation** is to never threshold on absolute temperature. Build a slow-updating per-pixel background model (exponential moving average with a time constant of tens of seconds), subtract it, and threshold on the residual. This automatically cancels warm-up drift, self-heating and room ambient, at the cost of making a perfectly stationary person slowly fade into the background — which is precisely the failure mode the STHS34PF80's dedicated "presence" (as opposed to "motion") algorithm is designed to fix, and which is why ST separates the two.

---

## 9. Can a pet at 38 °C be separated from a human at 34 °C?

**No — and the premise is wrong.** The 4 °C core-temperature gap is real but unobservable by these sensors, for three independent reasons.

**Reason 1: you measure surface, not core.** A cat's core is 38–39.2 °C, but fur is an excellent insulator. Measured fur-surface temperature is typically **30–36 °C** depending on coat density; ears, nose and paw pads run hotter (35–38 °C) because they are thinly furred and used for thermoregulation. A human's *exposed skin* is 31–35 °C, but a clothed torso in a sweater reads **25–28 °C** in a 22 °C room. The observable distributions overlap almost completely, and the clothed human is frequently the *cooler* of the two.

**Reason 2: fill fraction swamps the signal.** From §4.4, a Grid-EYE reports a cat at 3 m as a 2.5 °C rise and a clothed human at 5 m as a 3.8 °C rise. Change either range by a metre and the ordering flips. On an 8×8 array, **apparent temperature is mostly a range measurement in disguise.** Only the MLX90640 — where targets fully fill pixels out to 7 m — reports anything close to true surface temperature, and even there the datasheet's own accuracy qualification ("only valid if the object fills the FOV of the sensor completely") withholds the ±2 °C guarantee.

**Reason 3: absolute accuracy is worse than the gap you are trying to measure.** Grid-EYE accuracy is "Typical ±2.5 °C". MLX90640 frame accuracy is ±1 to ±2 °C with non-uniformity of up to ±3 °C ± 2 % of abs(To−Ta) in the outer zone. The alleged human/pet gap is 4 °C of *core* temperature, which maps to perhaps 1–3 °C of surface difference. **The measurement uncertainty is the same size as the effect.**

### What actually separates them

Geometry and kinematics, both of which need pixels:

| Cue | Human | Cat / small dog | Minimum sensor to see it |
|---|---|---|---|
| Height of warm blob above floor | centroid 0.9–1.2 m | centroid 0.1–0.25 m | any array with the floor in frame |
| Aspect ratio (tall:wide) | ~3.8:1 standing | ~1.25:1, long and low | ≥3 px in the short axis |
| Blob area vs measured range | large | small | needs a range estimate from a ToF lane |
| Gait / motion frequency | 1.7–2.2 Hz step rate | 2.5–4 Hz | ≥8 full frames/s |
| Vertical extent as a fraction of frame | large | small | ≥3 px tall |

Against the §4 tables: the **height-above-floor cue alone** is decisive and cheap, and it works on a Grid-EYE out to about 2.4 m provided the floor is in the frame (which requires the downward tilt of §5). The **aspect-ratio cue** needs a 3 × 3 blob, so ~1.2 m on a Grid-EYE, ~3 m on the 55° MLX90640, ~1.5 m on the 110° MLX90640. The **gait cue** needs ≥8 full frames/s, which the Grid-EYE has (10 Hz) and a multi-sensor MLX90640 ring, bus-limited to ~1.4 Hz each, does not.

Practical recommendation for requirement (d): **do not attempt thermal-only classification.** Use the thermal channel to answer "is this warm blob alive?", and take the range and the geometry from a ToF or mmWave lane. The fusion is what works. Thermal answers *animate vs inanimate* — which no ToF sensor can do — and it answers it well, even on an 8×8 array, because a live body is the only thing in a domestic room that is reliably several degrees above the wall behind it and that moves.

---

## 10. Recommendation for this robot

1. **Do not build the perimeter obstacle ring out of thermal sensors.** They cannot see room-temperature objects at all.
2. **Add thermal as an animate/inanimate overlay** on top of whatever ToF or mmWave ring serves requirement (a).
3. **If budget allows one array: one MLX90640 4407 (55°, $74.95) on a slip ring or pan servo, tilted 20° down, facing the direction of travel.** It classifies a human past 7 m and a pet to ~3 m, suffers no sub-pixel dilution, and at one unit the I²C bandwidth problem disappears entirely (8 full frames/s comfortably). Only 4 in stock as of 2026-09-12 — buy now or expect a lead time.
4. **If a fixed 360° ring is required: six AMG8833 3538 ($269.70) plus a TCA9548A mux.** Accept that this is a detect-and-localise ring, not a classifier, and that pet classification only works inside ~1.2 m.
5. **Add five STHS34PF80 6426 ($74.75 total) as an always-on 360° wake-up layer.** 10 µA each, holds static presence, and gates the expensive sensors. It cannot classify, and that is fine because it is not being asked to.
6. **Leave an open aperture in front of every thermal sensor.** No acrylic, no polycarbonate, no glass. If a window is mandatory for ingress protection, use thin LDPE and budget for the transmission loss.
7. **Never threshold on absolute temperature.** Per-pixel background subtraction with a ~30 s time constant, every time.

---

## Sources

- [Adafruit search: "camera stema ir"](https://www.adafruit.com/search?q=camera+stema+ir)
- [Adafruit search: "thermal camera"](https://www.adafruit.com/search?q=thermal+camera)
- [Adafruit search: "PIR"](https://www.adafruit.com/search?q=PIR) / [Adafruit search: "motion sensor"](https://www.adafruit.com/search?q=motion+sensor) / [Adafruit search: "thermopile"](https://www.adafruit.com/search?q=thermopile) / [Adafruit search: "NoIR camera"](https://www.adafruit.com/search?q=NoIR+camera)
- [Adafruit 3538 — AMG8833 IR Thermal Camera Breakout, STEMMA QT](https://www.adafruit.com/product/3538)
- [Adafruit 3622 — AMG8833 IR Thermal Camera FeatherWing](https://www.adafruit.com/product/3622)
- [Adafruit 4407 — MLX90640 IR Thermal Camera Breakout, 55 Degree](https://www.adafruit.com/product/4407)
- [Adafruit 4469 — MLX90640 24x32 IR Thermal Camera Breakout, 110 Degree FoV](https://www.adafruit.com/product/4469)
- [Adafruit 6426 — STHS34PF80 IR Presence / Motion Sensor](https://www.adafruit.com/product/6426)
- [Adafruit 1747 — MLX90614 3V](https://www.adafruit.com/product/1747) / [Adafruit 1748 — MLX90614 5V](https://www.adafruit.com/product/1748)
- [Adafruit 189 — PIR (motion) sensor](https://www.adafruit.com/product/189) / [Adafruit 4871 — Mini PIR](https://www.adafruit.com/product/4871) / [Adafruit 5578 — BS612 Mini PIR](https://www.adafruit.com/product/5578)
- [Adafruit 4578 — UTi165H](https://www.adafruit.com/product/4578) / [Adafruit 4579 — UTi165K](https://www.adafruit.com/product/4579)
- [Adafruit 4022 — MLX90393 magnetometer (excluded)](https://www.adafruit.com/product/4022) / [Adafruit 4479 — LIS3MDL magnetometer (excluded)](https://www.adafruit.com/product/4479)
- [Adafruit Learn: AMG8833 8x8 Thermal Camera Sensor](https://learn.adafruit.com/adafruit-amg8833-8x8-thermal-camera-sensor/overview)
- [Adafruit Learn: STHS34PF80 IR Presence / Motion Sensor](https://learn.adafruit.com/adafruit-sths34pf80-ir-presence-motion-sensor)
- [Adafruit Learn: I2C Addresses — The List](https://learn.adafruit.com/i2c-addresses/the-list)
- [Panasonic Grid-EYE AMG88 datasheet, 02 Apr 2017 (PDF)](https://cdn.sparkfun.com/assets/4/1/c/0/1/Grid-EYE_Datasheet.pdf)
- [Panasonic AMG8833 product page](https://na.industrial.panasonic.com/products/sensors/sensors-automotive-industrial-applications/lineup/grid-eye-infrared-array-sensor/series/70496/model/72453)
- [Melexis MLX90640 32x24 IR array datasheet, Rev 12, 3 Dec 2019 (PDF)](https://www.melexis.com/-/media/files/documents/datasheets/mlx90640-datasheet-melexis.pdf)
- [STMicroelectronics STHS34PF80 datasheet DS13916 Rev 2, July 2023 (PDF)](https://cdn-shop.adafruit.com/product-files/6426/sths34pf80.pdf)
- [STMicroelectronics STHS34PF80 product page](https://www.st.com/en/mems-and-sensors/sths34pf80.html)
- [Germanium windows and LWIR optics — Workswell](https://workswell.eu/germanium-lens-lwir-optics-thermal-cameras-modules/) / [Edmund Optics germanium windows](https://www.edmundoptics.com/f/germanium-ge-windows/13137/)
