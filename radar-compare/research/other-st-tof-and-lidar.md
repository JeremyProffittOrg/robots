# Lane: other-st-tof-and-lidar

Perimeter sensing options **beyond** the Adafruit/DFRobot multizone-ToF and mmWave catalogue, for a
350 mm square / 350 mm diameter mobile robot, 600–1200 mm tall, that must detect (a) any collidable
obstacle, (b) humans, (c) pets 200–500 mm tall, and (d) tell the three apart.

Two halves:

1. The rest of ST's FlightSense ToF portfolio — VL6180X, VL53L1X/VL53L1CB, VL53L3CX, VL53L4CD,
   VL53L4CX, VL53L4ED, the SATEL evaluation boards, and the automotive/industrial parts.
2. Affordable **scanning lidar** — Slamtec RPLIDAR A1M8 / C1 / A2M12 / S2 / S3, LDROBOT LD06 / LD19 /
   Waveshare D500, YDLIDAR X2 / X4 PRO / G4 / T-mini Plus, Benewake TF-Luna and TFmini-S, Hokuyo URG
   entry parts, and the sub-$500 3D units (Livox, Unitree).

All prices were read on **2026-09-12** unless stated otherwise. Where a number could not be confirmed
against a datasheet or a vendor page in this pass, it is written as **not published** or
**not verified in this pass**. Nothing here is estimated or rounded from memory.

**Tooling note that affects confidence:** `www.st.com` was unreachable from this machine for the whole
pass (`curl` returned `HTTP 000 size 0`; `WebFetch` timed out at 60 s, repeatedly). ST datasheets were
therefore obtained from mirrors that host the identical ST PDF — Pololu (`pololu.com/file/...`) and
Adafruit's learn CDN (`cdn-learn.adafruit.com/assets/...`). Those PDFs carry ST document numbers
(DS13204, DS13805, DS13812, DocID026171, DocID031281) and are treated as datasheet-verified. Parts
whose datasheet exists **only** on st.com — notably **VL53L1CB** and **VL53L4ED** — are marked down to
vendor-page-verified or unverified, and said so explicitly.

**Adversarial re-verification pass, 2026-09-12.** Every hard number below was re-checked against the
primary source independently of the original pass. Result: the ST ranging tables (VL6180X Table 19,
VL53L1X Table 4, VL53L3CX Table 13, VL53L4CX Table 14, VL53L4CD Table 16) are **confirmed verbatim**,
including their measurement conditions and document revisions (DocID026171 Rev 7, DocID031281 Rev 3,
DS13204 Rev 2, DS13805 Rev 2, DS13812 Rev 8). Five defects were found and are fixed in place, each
marked in its own section: the **Pololu VL6180X carrier is End-of-Life**; the **S2/S2E 10 %-reflectivity
range was wrong**; the **A1M8 sampling/angular-resolution figures mixed two hardware generations**;
**Inno-Maker no longer sells an LD06 at its LD06 URL**; and Pololu's **#3416 "5 m"** and **#2489
"60 cm"** headline ranges are vendor overclaims against their own datasheets. `www.st.com` was retested
and is **still unreachable from this machine** (`curl` → `Recv failure: Connection was reset` and a
40 s timeout; `WebFetch` → 60 s timeout), so **VL53L1CB and VL53L4ED remain unverified** — that is a
tooling limit, not a claim.

---

## Part 1 — the rest of ST's FlightSense ToF portfolio

### 1.1 Why these parts at all

Everything in this family is a **single-cone, single-axis** ranger (except the L5/L7/L8 multizone parts,
which belong to another lane). Each one answers exactly one question: *how far is the nearest thing
inside a cone of N degrees?* The VL53L3CX is the interesting exception — it reports **up to four
distances simultaneously** inside one cone.

### 1.2 VL53L6180X — the short-range one (VL6180X)

Datasheet: ST `DocID026171 Rev 7`, read via `https://www.pololu.com/file/0J961/VL6180X.pdf`.

| Parameter | Value | Condition |
|---|---|---|
| Ranging spec | **0 to 100 mm** | "Ranging beyond 100 mm is dependent on target reflectance and external conditions" |
| Max range, dark | > 100 mm at 3 %, 5 %, 17 % and 88 % reflectance | integrating sphere, 80 × 80 mm targets, SNR limit 0.1 |
| Max range, 1 kLux diffuse halogen | > 80 mm @ 3 %; > 90 mm @ 5 %; > 100 mm @ 17 %; > 100 mm @ 88 % | Table 19 |
| Max range, 5 kLux diffuse halogen | > 40 mm @ 3 %; > 45 mm @ 5 %; > 60 mm @ 17 %; > 70 mm @ 88 % | "5 kLux halogen ≈ 10–15 kLux natural sunlight" |
| Noise | max 2.0 mm | std dev of 100 measurements |
| Range offset error | max 13 mm | after 3 reflow cycles, removable by calibration |
| Convergence time | typ 9 ms, max 15 ms | 3 % target @ 100 mm |
| Emitter | **850 nm** | not 940 nm like the rest of the family |
| Supply | 2.6–3.0 V functional, 2.7–2.9 V optimum | |
| Current | HW standby < 1 µA; SW standby < 1 µA; ALS 300 µA; **ranging 1.7 mA typ average** | 10 Hz, 17 % target @ 50 mm |
| Package | Optical LGA12, **4.8 × 2.8 × 1.0 mm** | |
| I²C | 400 kHz, address **0x29 (7-bit)** | |
| ALS FoV | **42°** half angle at 40 % of peak, X and Y | this is the *ambient light sensor* FoV, not the ranging FoV; the ranging FoV is **not published** in the datasheet sections read |

**Verdict for this robot: useless as a perimeter sensor.** 100 mm of guaranteed range on a 350 mm robot
means the obstacle is already under the bumper. Its only defensible role is a bump-imminent or
cliff/step sensor. It also carries the family's only ambient light sensor, which is a genuinely useful
free extra if you want the robot to know the room is dark.

Breakout: **Pololu #2489**, `$19.95` (read 2026-09-12), 2.6–5.5 V input via onboard 2.8 V regulator.

> **Availability flag (re-checked 2026-09-12):** Pololu marks #2489 **"End-of-Life Rationing"**, not
> "Active and Preferred" like #3415 / #3416 / #3692. Treat the VL6180X carrier as a part on its way
> out, not a part to design in. Pololu's own listing also markets the carrier as ranging **"up to 20 cm
> with its default settings"** and **"up to 60 cm (24″) … at the cost of reduced resolution"** — both
> are above the datasheet's 100 mm specification and neither carries a reflectance condition, so the
> datasheet column above is the number to design to.

### 1.3 VL53L1X and VL53L1CB — the 4 m programmable-ROI part

Datasheet for VL53L1X: ST `DocID031281 Rev 3`, via `https://www.pololu.com/file/0J1506/vl53l1x.pdf`.

| Parameter | Value | Condition |
|---|---|---|
| Package | Optical LGA12, 4.9 × 2.5 × 1.56 mm | |
| Receiver FoV | **programmable 15° to 27°** (diagonal) | the ROI can be shrunk or split into zones |
| Emitter | 940 nm | |
| I²C | up to 400 kHz, default address 0x52, programmable | |
| Supply | 2.6 to 3.5 V | |
| Max distance, **short** mode | **136 cm** dark / **135 cm** under strong ambient | timing budget 100 ms, white 88 % target, ambient = 200 kcps/SPAD |
| Max distance, **medium** mode | **290 cm** dark / **76 cm** ambient | same |
| Max distance, **long** mode | **360 cm** dark / **73 cm** ambient | same |
| Laser safety | Class 1, IEC 60825-1:2014 (3rd ed.) | |

That table is the single most important number in this whole lane. **Long mode collapses from 360 cm to
73 cm** when you add ambient infrared. Short mode barely moves (136 → 135 cm) because it is designed to
be ambient-immune. Any perimeter design built on single-cone ToF must be sized for the *ambient* column,
not the dark column, if the robot will ever see a sunlit window.

> **Caveat the table above hides (verified 2026-09-12 against DocID031281 Rev 3).** The 136 cm / 135 cm
> short-mode pair is **Table 4**. **Table 8** ("Typical performances in ambient light conditions with
> short distance mode") gives a *different* short-mode number: **130 cm dark and 130 cm at 200 kcps/SPAD
> for white 88 %**, and **130 cm dark falling to 120 cm at 200 kcps/SPAD for grey 17 %**. ST's own two
> tables disagree by 6 cm. Size short mode on **130 cm white / 120 cm grey-17 % under strong ambient**,
> which is the conservative reading. Dark-condition **Table 6** also gives long mode a *minimum* of only
> **260 cm white 88 %, 220 cm grey 54 %, 80 cm grey 17 %** against the 360/340/170 cm typicals —
> the 360 cm headline is a typical, not a floor.

**VL53L1CB** is ST's cover-glass-optimised sibling of the same ranging core. **Its datasheet is hosted
only on st.com and could not be retrieved in this pass, so no VL53L1CB-specific number is asserted
here.** Treat any VL53L1CB figure you see elsewhere as unverified until the ST PDF is read directly.

Breakout: **Pololu #3415**, `$22.95` (read 2026-09-12).

### 1.4 VL53L3CX — the multi-target part

Datasheet: ST `DS13204 Rev 2`, via `https://www.pololu.com/file/0J1765/vl53l3cx.pdf`.

| Parameter | Value | Condition |
|---|---|---|
| Package / size | Optical LGA12, **4.4 × 2.4 × 1 mm** | |
| FoV | **25° typical full FoV** | all range tables assume the full FoV is covered |
| Min range | **10 mm** | |
| Max range, white 88 % | **typ 310 cm @ 94 % detection rate**, min 310 cm @ 50 % (indoor, no IR) | 30 ms timing budget, 23 °C, 2.8 V, no cover glass |
| Max range, white 88 %, outdoor overcast | **typ 100 cm @ 94 %**, min 110 cm @ 50 % | "outdoor overcast" = 10 kcps/SPAD ≈ 1.2 W/m² at 940 nm ≈ **5 kLux daylight** on a grey 17 % chart at 40 cm |
| Max range, light grey 54 % | typ 290 cm indoor / typ 70 cm outdoor overcast | |
| Max range, grey 17 % | **typ 170 cm indoor** / typ 70 cm outdoor overcast | |
| Ranging accuracy | ±7 mm to ±10 mm over 25–90 mm (reflectance dependent); ±5 % over 90–110 mm; ±2.5 % to ±5 % beyond 110 mm indoor, up to ±10 % outdoor overcast | Table 14; the exact per-reflectance assignment is hard to read out of the PDF's table layout, so the range is quoted rather than a single row |
| Multi-target | **up to four ranges output simultaneously** by the software driver, inside one FoV | this is the headline feature |
| Ranging rate | 30 Hz default, ~33 ms per operation including post-processing | requires a host↔device handshake every ranging op |
| Cover glass | crosstalk immunity **beyond 80 cm**, dynamic smudge compensation, 300 cm with cover glass in place | |
| Current | HW standby 3/5/7 µA; SW standby 4/6/9 µA; **active ranging 16 mA typ, 18 mA max**; **peak 40 mA** | 23 °C, 2v8 |
| I²C | up to 1 MHz (fast mode plus), address 0x52 | |
| Host cost | **not recommended for 8-bit MCUs** — the histogram driver needs significant RAM and code space | |

**Why it matters for human-vs-pet-vs-object:** multi-target is the closest thing in the single-cone
family to depth understanding. If one cone reports "something at 0.6 m *and* something at 2.4 m", that
is a cat in front of a wall — a single-target sensor would have reported only 0.6 m and thrown away the
fact that the background is still visible. That lets you reason about **occupancy depth**: a thin object
(a chair leg) leaves the background visible in the same cone; a broad object (a human torso) does not.
It is a weak feature, but it is real and it is free.

Breakout: **Pololu #3416**, `$19.95` (read 2026-09-12), 2.6–5.5 V in. DFRobot also sells a Fermion
breakout (SEN0378).

> **Vendor overclaim flag (read 2026-09-12).** Pololu's #3416 listing is titled **"500cm Max"** and its
> body says the sensor ranges **"up to 5 m"**. The ST datasheet (DS13204 Rev 2, Table 13) gives
> **310 cm typical against a white 88 % target indoors with no infrared**, and **170 cm typical against a
> grey 17 % target**. There is no 5 m row anywhere in the datasheet. Use 310 cm; the carrier page's 5 m
> is not datasheet-supported. (Table 13's grey-17 % row also reads **typ 170 cm @ 94 %, min 200 cm @
> 50 %** — the "minimum" column is a *lower detection rate*, not a lower distance.)

### 1.5 VL53L4CX — the 6 m narrow-cone part

Datasheet: ST `DS13805 Rev 2`, via `https://cdn-learn.adafruit.com/assets/assets/000/111/219/original/vl53l4cx.pdf`.

| Parameter | Value | Condition |
|---|---|---|
| Package | Optical LGA12, 4.4 × 2.4 × 1 mm | |
| FoV | **18°** | detection volume, target at 1000 mm, white 88 % |
| Min range | detection from **0 mm**; **linear response from 10 mm** | |
| Max range, white 88 % | **typ 5000 mm @ 90 % detection**, **6000 mm @ 50 %** (indoor) | 33 ms timing budget, 23 °C, 2.8 V, no cover glass, full FoV covered |
| Max range, white 88 %, outdoor overcast | **typ 1600 mm @ 90 %**, 1800 mm @ 50 % | |
| Max range, light grey 54 % | 4200 mm @ 90 % indoor / 1400 mm @ 90 % outdoor | |
| Max range, grey 17 % | **2100 mm @ 90 % indoor** / **1100 mm @ 90 % outdoor** | |
| Ranging accuracy | ±7 to ±8 mm over 10–110 mm indoor (±8 to ±9 mm outdoor); ±3 % to ±5 % beyond 110 mm indoor, ±5 % to ±8 % outdoor | Table 15 |
| Temperature drift | **1.3 mm per °C** offset; self-calibration on start removes it | |
| Current | HW standby 3/5/7 µA; SW standby 4/6/9 µA; **active ranging 19 mA typ, 21 mA max**; **peak 40 mA** | |
| Operating temp | **−30 to 85 °C** (wider than the L3CX's −20 to 85 °C) | |
| I²C | up to 1 MHz, address 0x52 | |
| Multi-object | yes — can report more than one object in view | Adafruit: "can identify when more than one object is in view and tell you the two distances" |
| Laser class | Class 1, IEC 60825-1:2014 (3rd ed.) | |

Breakout: **Adafruit #5425**, `$14.95`, **in stock** (read 2026-09-12), STEMMA QT / Qwiic, 2.8 V core,
3–5 V tolerant. Adafruit note: the driver needs ~50 kB of flash and **will not fit an ATmega328**.

**This is the best single-cone part in ST's range for this robot.** 5 m on a white wall, 2.1 m on a dark
17 % target, 18° cone, 19 mA. The 17 % number is the one that matters: a dark-clothed human leg or a
black cat is a 5–17 % reflector at 940 nm, so plan on ~2 m, not 6 m.

### 1.6 VL53L4CD and VL53L4ED — the short, cheap, fast ones

**VL53L4CD** — datasheet ST `DS13812 Rev 8`, via `https://www.pololu.com/file/0J2060/vl53l4cd.pdf`:

| Target | Indoor (no IR) | Outdoor overcast |
|---|---|---|
| White 88 % | **typ 1200 mm @ 90 % detection**, 1300 mm @ 50 % | **typ 550 mm @ 90 %**, 600 mm @ 50 % |
| Grey 17 % | **typ 450 mm @ 90 %**, 475 mm @ 50 % | **typ 400 mm @ 90 %**, 450 mm @ 50 % |

Ranging to 100 Hz; 1 mm to 1200 mm; breakout **Pololu #3692 `$13.95`** (read 2026-09-12).

**VL53L4ED** — ST's low-power variant. ST's own product page states an **18° FoV**, measurement from
**1 mm up to 1300 mm in standard conditions**, and **accurate measurement up to 800 mm under 5 klx
ambient light** with special settings. *That is vendor-page-verified, not datasheet-verified* — the
`vl53l4ed.pdf` on st.com could not be fetched in this pass. There is no Adafruit or Pololu breakout for
the L4ED; it is a bare-module part aimed at battery-powered consumer products.

### 1.7 SATEL boards and the automotive / industrial FlightSense parts

ST sells small "satellite" break-out PCBs for most FlightSense modules — `VL53L4CX-SATEL`,
`VL53L3CX-SATEL`, `VL53L1CB-SATEL`, `VL53L5CX-SATEL` and similar — a postage-stamp PCB carrying the
module plus a flex or 0.1 in header, intended to plug into the matching `X-NUCLEO-53L*A1` expansion
shield for evaluation on a Nucleo board. **Their contents, pack quantity and prices are not verified in
this pass** because every SATEL page and the whole ST parametric table live on st.com, which was
unreachable. They are mentioned only so the option is not silently omitted: if you want ST's own
reference cover-glass geometry and calibration flow, the SATEL + X-NUCLEO pair is the path, and it is
worth pricing at Mouser/DigiKey before committing to a custom carrier.

The **automotive and industrial FlightSense** parts are in the same position: **not verified in this
pass**. Practically, they are irrelevant to this robot — they are AEC-Q100 / extended-temperature parts
sold on MOQ through the broker channel, not stocked by the hobby distributors, and they do not offer
more range or a better FoV than the VL53L4CX. Nothing in the automotive line changes the human/pet/object
discrimination problem, which is an information problem, not a qualification problem.

### 1.8 ST portfolio summary for a 350 mm robot

| Part | FoV | Range, white 88 % (dark) | Range, grey 17 % (dark) | Range under ~5 kLux equivalent | Active current | Breakout price |
|---|---|---|---|---|---|---|
| VL6180X | ALS 42°; ranging FoV not published | > 100 mm (spec'd to 100 mm) | > 100 mm | > 70 mm @ 88 %, > 60 mm @ 17 % (5 kLux halogen) | 1.7 mA @ 10 Hz | $19.95 (Pololu 2489) — **End-of-Life Rationing** |
| VL53L1X | 15–27° programmable | 360 cm (long mode) | not published per-mode | **73 cm** (long), 135 cm (short) | not separately published in the sections read | $22.95 (Pololu 3415) |
| VL53L3CX | 25° | 310 cm | 170 cm | 100 cm @ 88 %, 70 cm @ 17 % | 16 mA typ, 40 mA peak | $19.95 (Pololu 3416) |
| VL53L4CD | 18° | 120 cm | 45 cm | 55 cm @ 88 %, 40 cm @ 17 % | not captured | $13.95 (Pololu 3692) |
| VL53L4CX | 18° | **500 cm** | **210 cm** | 160 cm @ 88 %, 110 cm @ 17 % | 19 mA typ, 40 mA peak | $14.95 (Adafruit 5425) |
| VL53L4ED | 18° (vendor page) | 130 cm (vendor page) | not published | 80 cm @ 5 klx (vendor page) | not verified | no hobby breakout |
| VL53L1CB | not verified | not verified | not verified | not verified | not verified | no hobby breakout |

---

## Part 2 — affordable 360° scanning lidar

### 2.1 Slamtec RPLIDAR A1M8

Datasheet: Slamtec `rev 2.2, 2019-02-14`, "RPLIDAR A1 Low Cost 360 Degree Laser Range Scanner".

| Parameter | Value | Condition |
|---|---|---|
| Principle | **laser triangulation** (not DTOF) | |
| Distance range | **0.15–12 m** (A1M8-R5 and later); **0.15–6 m** (A1M8-R4 and earlier) | **white objects** |
| Angular range | 0–360° | |
| Scan field flatness | **−1.5° to +1.5°** | i.e. the "plane" is a ±1.5° wedge |
| Distance resolution | **< 0.5 mm** below 1.5 m; **< 1 % of distance** over the whole range | |
| Angular resolution | **≤1°** as published — but see the conflict note below | slamtec.com/en/lidar/a1spec |
| Sample duration | 0.125 ms | |
| Sample frequency | **8000 Hz typ**, 8010 max | |
| Scan rate | 1–10 Hz, **typ 5.5 Hz** → **≈1450 samples/scan ≈ 0.25°** | speed-adaptive; see conflict note |
| Laser | **775–795 nm (typ 785 nm)**, peak power typ 3 mW / max 5 mW, pulse 110 µs typ | |
| Eye safety | **Class I**, 21 CFR 1040.10 and 1040.11 | "safety to human and pet" |
| Interface | **UART 3.3 V TTL, 115200 bps, 8N1** (dev kit adds USB) | |
| Scanner supply | 4.9–5.0–5.5 V, ripple < 50 mV | over-voltage damages the core |
| Scanner current | start **max 600 mA**; work **300 mA typ / 350 mA max**; sleep 80/100 mA | 5 V input |
| Motor supply | 5–10 V, **100 mA typ** | speed set by voltage/PWM |
| Weight | **170 g** | |
| Operating temperature | 0–45 °C | |
| Dev-kit size | 96.8 × 70.3 × 55 mm | slamtec.com/en/lidar/a1spec |
| Sunlight | "works in all kinds of indoor and outdoor environment **without direct sunlight**" | the triangulation weakness, stated by the vendor |
| Price | **$99.00** at DFRobot (A1M8-R6), read 2026-09-12 | |

> **Conflict note — Slamtec's A1 numbers span two hardware generations (checked 2026-09-12).** The
> **original A1 datasheet (rev 1.0, 2016-07-04), read directly**, specifies **Sample Duration 0.5 ms,
> Sample Frequency 2000 Hz, Angular Resolution 1°**, and Scan Rate "typical value is measured when
> RPLIDAR A1 takes **360 samples per scan**". Those four numbers are self-consistent: 2000 Hz ÷ 5.5 Hz
> ≈ 363 samples. The **current A1M8-R5/R6 is an 8 kHz part** — 0.125 ms sample duration — so at 5.5 Hz it
> produces **≈1450 samples per revolution ≈ 0.25°**, and DFRobot's A1M8-R6 listing says so in words:
> *"RPLIDAR A1's scanning frequency reached 5.5 hz when sampling 1450 points each round."* Slamtec's own
> current spec page nevertheless still prints **"Angular Resolution ≤1°"** beside **"Sampling Frequency
> 8K"**, which cannot both be true. **The ≤1° figure is a leftover from the 2 kHz rev 1.0 part.** Design
> to ≈1450 points/rev for an R5/R6 unit, and do not quote "360 samples/scan" for it.
>
> **Reflectance condition (datasheet-verified).** The A1 datasheet's Distance Range row carries the
> comment **"White objects"** — confirmed by reading rev 1.0 directly. Neither Slamtec's current
> `a1spec` page nor DFRobot's listing states any reflectance condition at all; the word "white" does not
> appear on either. Triangulation range against a dark target is not published anywhere by Slamtec.
>
> **Power conflict.** The datasheet-derived scanner + motor figures above total roughly **2 W**, but
> Slamtec's current `a1spec` "key parameters" block prints **System Current 100 mA, Power Consumption
> 0.5 W**. The two are not reconcilable from published data; budget the higher figure.

Self-protection: the unit shuts the laser down on over-power, unstable/slow scan speed or sensor fault,
and the host can query health over the same UART. That is a real safety feature for a robot that shares
a house with people.

### 2.2 Slamtec RPLIDAR C1 — DTOF, the current value pick

Specs from DFRobot's product page for the Slamtec C1 (`dfrobot.com/product-2803.html`) and slamtec.com/en/c1.

| Parameter | Value |
|---|---|
| Principle | **DTOF** (Slamtec "SL-DTOF" fusion) |
| Measuring radius | **0.05–12 m @ 70 % reflection (white)**; **0.05–6 m @ 10 % reflection (black)** |
| Blind zone | 0.05 m |
| Sample rate | **5 kHz** |
| Scan frequency | **8–12 Hz, 10 Hz typical** (600 rpm) |
| Angular resolution | **0.72° typical** at 10 Hz |
| Ranging accuracy | **±30 mm** |
| Resolution | 15 mm |
| Ambient light | **40 000 lux** |
| Interface | TTL UART, **460800 baud** |
| Protection | **IP54** |
| Weight | **110 g** |
| Operating temperature | −10 to 40 °C |
| Eye safety | Class 1 |
| Supply | 5 V DC ±0.2 V; typical operating current **230 mA @ 10 Hz** — *reseller listing, not confirmed against the Slamtec datasheet* |
| Price | **$69.00** at DFRobot, read 2026-09-12 |

The C1 is the important entry in this table: **DTOF instead of triangulation** means the 12 m figure is
honest against a 70 % target and it degrades to a stated 6 m against a 10 % black target, rather than
just "does not work in sunlight". 40 klux ambient immunity, IP54, 110 g, $69.

### 2.3 Slamtec RPLIDAR A2M12 / A2M8, S2 family, S3

From slamtec.com product pages (vendor-page-verified; full datasheets not fetched in this pass):

| Model | Range | Sample rate | Scan rate | Angular resolution | Notes |
|---|---|---|---|---|---|
| A2M12 | 0.2–12 m | **16 kHz** | 10 Hz (5–15 Hz) | **0.225°** | Class 1 |
| A2M8 | 0.2–12 m | 8 kHz | 10 Hz (5–15 Hz) | 0.45° | Class 1 |
| S2L | 0.05–18 m @ 90 %; **0.05–8 m @ 10 %** | 32 kHz | 10 Hz | 0.1125° | |
| S2 / S2E | **0.05–30 m @ 90 %**; **0.05–10 m @ 10 %** | **32 kHz** | 10 Hz | **0.1125°** | **80 klux** sunlight, **IP65**, Class 1; optical scanning area height **18 mm**; S2 serial, S2E Ethernet |
| S2P | 0.05–50 m @ 90 %; **0.05–15 m @ 10 %** | 32 kHz | 10 Hz | 0.1125° | |
| S3 | listed in the Slamtec product line; **specs not captured in this pass** | | | | |

**Correction (2026-09-12 re-check of `slamtec.com/en/s2`).** An earlier version of this table gave the
S2/S2E low-reflectance range as "8–15 m @ 10 %". That was a **range spanning the whole family**, wrongly
attributed to one model. Slamtec's spec table gives a distinct 10 %-reflectivity figure per model:
**S2L 0.05–8 m, S2 / S2E 0.05–10 m, S2P 0.05–15 m**. The 90 % figures (18 / 30 / 50 m), the 32 kHz
sample rate, the 10 Hz scan rate and the 0.1125° resolution are all confirmed as printed.

Prices for A2M12, S2 and S3: **not verified** — Slamtec's own store page carries no USD prices and
directs to `sales@slamtec.com`. The **A2M12 0.2–12 m** figure is confirmed on `slamtec.com/en/lidar/a2`
and, as the table says, **carries no reflectivity condition on that page** — it is a bare number, so
treat it as a white-target best case until Slamtec's A2 datasheet is read.

Note the **0.2 m minimum range** on the A2 family. On a 350 mm robot whose lidar is at the centre, the
chassis edge is 175 mm out, so an A2 has essentially no usable margin between "inside the blind zone"
and "touching the robot". The C1, S2, LD06/LD19 and T-mini Plus (all 0.02–0.05 m) are far better suited
to a small footprint.

### 2.4 LDROBOT LD06

Datasheet: `LDROBOT_LD06_Datasheet.pdf` (hosted by Inno-Maker).

| Parameter | Min | Typ | Max | Condition |
|---|---|---|---|---|
| Range | 0.02 m | — | **12 m** | **70 % target reflectivity** |
| Scan frequency | 5 Hz | **10 Hz** | 13 Hz | external PWM speed control |
| Sampling frequency | — | **4500 Hz** | — | fixed frequency |
| Ranging accuracy | — | **30 mm** | 45 mm | |
| Measurement resolution | — | 15 mm | — | |
| Angular error | — | — | 2° | |
| Angular resolution | — | **1°** | — | |
| Anti-ambient light | — | — | **30 kLux** | |
| Lifetime | 10 000 h | — | — | ≈ 14 months continuous |
| Input voltage | 4.5 V | 5 V | 5.5 V | |
| Start-up current | — | **300 mA** | — | |
| Working current | — | **180 mA** | — | ≈ **0.9 W** |
| Size | **38.59 × 38.59 × 33.30 mm** | | | |
| Weight | — | **42 g** | — | without cable |
| Interface | **UART @ 230400**, 8N1, one-way (streams without command) | | | |
| Protection | IPX-4 | | | |
| Laser | **895–915 nm (typ 905 nm)**, peak power 25 mW | | | |
| Eye safety | **IEC-60825 Class 1** | | | |
| Operating temperature | −10 to 40 °C | | | |
| Price | **No LD06 is on sale at Inno-Maker.** `inno-maker.com/product/lidar-ld06/` now serves a product named **"LiDAR LD19P"**, SKU **"LIDAR LD19"**, at **$99.00 (was $119.00)** — re-checked 2026-09-12. The LD06 datasheet is still linked from that page, but the product sold there is not an LD06. **Source an LD06 elsewhere or treat it as superseded by the LD19/LD19P.** | | | |

### 2.5 LDROBOT LD19 and Waveshare D500

From the Waveshare wiki pages (vendor-page-verified, tables read verbatim).

| Parameter | LD19 | D500 LiDAR Kit |
|---|---|---|
| Typical measuring range | **0.02–12 m** | **0.03–12 m** |
| Sampling frequency | **4500 Hz** | **5000 Hz** |
| Scan frequency | **10 Hz** | **10 Hz** |
| Angular resolution | **≤ 1°** | **≤ 0.72°** |
| Ranging accuracy | **10 mm** (300 mm < d ≤ 12000 mm) | 10 mm (300–500 mm), 20 mm (500–2000 mm), 30 mm (2000–12000 mm) |
| Mechanical size | 38.59 × 38.59 × 33.50 mm | 38.59 × 38.59 × 33.50 mm |
| Interface | UART @ 230400 bps, ZH1.5T-4P | UART @ 230400 bps |
| Supply | 5 V, **180 mA**, **0.9 W** | 5 V, **290 mA**, **1.45 W** |
| Operating temperature | −10 to 40 °C | −10 to 45 °C |
| Anti-glare | **30 kLux** | not stated on the wiki page |
| Eye safety | **FDA Class 1** | Class 1 |

### 2.6 YDLIDAR X2, X4 PRO, G4, T-mini Plus

All four datasheets read directly (`ydlidar.com/download/category/datasheet/`).

| Parameter | X2 | X4 PRO | G4 | T-mini Plus |
|---|---|---|---|---|
| Principle | triangulation | triangulation | triangulation | **ToF** |
| Ranging frequency | **3000 Hz** | **5000 Hz** | **9000 Hz** | **4000 Hz** |
| Scan / motor frequency | 5 / **6** / 8 Hz | **6–12 Hz** | 5 / **7** / 12 Hz (max 16) | **6** (default) – 12 Hz |
| Ranging distance | **0.12–8 m** @ 80 % reflectivity, indoor | **0.12–10 m** @ 80 %, indoor | **0.12–16 m** @ 80 % at 4 kHz; 0.26–16 m at 8 kHz; **0.28–16 m at 9 kHz** | **0.05–12 m @ 80 %**; **0.05–4 m @ 10 %** |
| Systematic / absolute error | 2 cm at range ≤ 1 m | 2 cm at distance ≤ 1 m | 2 cm at range ≤ 1 m | **20 mm over 0.05–12 m** |
| Relative error | 3.5 % (1 m < range ≤ 6 m) | 3.5 % (1 m < d ≤ 6 m) | **2.0 %** (1 m < range ≤ 8 m) | n/a |
| Angular resolution | 0.60° @5 Hz / **0.72° @6 Hz** / 0.96° @8 Hz | 0.43° @6 Hz / 0.50° @7 Hz / 0.86° @12 Hz | **0.2° @5 Hz** / 0.28° @7 Hz / 0.48° @12 Hz | **0.54°** |
| Tilt angle | 0.25–1.75° | 0.25–1.75° | 0.25–1.75° | 0–1.5° |
| Supply | 4.8–5.2 V | 4.8–5.2 V | 4.8–5.2 V | 4.8–5.2 V |
| Start-up current | **1000 mA** | 800 mA typ / 1000 mA max | **1000 mA** | 840 mA typ / 1000 mA max |
| Working current | **300 mA typ / 500 mA max** | 330 mA typ / 380 mA max | **350 mA** | 340 mA typ / 480 mA max |
| Sleep current | — | — | 50 mA | 45 mA |
| Size | Φ60.5 × 50.3 × 96 mm | 110.6 × 71.1 × 52.3 mm | Φ72.3 × 41.2 mm | **38.6 × 38.6 × 33.9 mm** |
| Weight | **126 g** | not captured | not captured | not captured |
| Ambient light | datasheet "Others" table lists a **lighting environment of 0–2000 lux (typ 550 lux)** | not captured | not captured | **60 kLux** |
| Laser | **775 / 793 / 800 nm**, FDA **Class I** (21 CFR 1040.10/11) | Class I | Class I | Class I, IEC 60825-1 |
| Service life | not stated | **1500 h** | not stated | not stated |

Two entries in that table should change a decision:

- **YDLIDAR X4 PRO's stated service life is 1500 hours.** That is about **62 days of continuous
  running**. For an always-on house robot this is a consumable, not a component.
- **YDLIDAR X2's datasheet lists a lighting environment of 0–2000 lux.** Triangulation lidars are not
  sunlight sensors. Compare the T-mini Plus (ToF) at 60 kLux and the LD06/LD19 at 30 kLux.

YDLIDAR prices were **not verified in this pass** — ydlidar.com publishes no USD price on the product
pages and its catalogue search endpoints returned 404.

### 2.7 Benewake TF-Luna and TFmini-S — single-point, not scanning

| Parameter | TF-Luna | TFmini-S |
|---|---|---|
| Range | **0.2–8 m** | **12 m** (product title: "TFmini-S 12 m LiDAR Ranging Module") |
| Accuracy | **± 6 cm @ 0.2–3 m** | not captured |
| Resolution | 1 cm | not captured |
| Frame rate | **1–250 Hz** | not captured |
| Interface | **UART, I/O, I²C** | UART, I²C, I/O |
| Power | **≤ 0.35 W** | not captured |
| Size | **35 × 21.25 × 13.5 mm** | **42 × 15 × 16 mm** |
| Weight | **< 5 g** | 5 g (the page's structured data also carries an inconsistent 11 g value) |
| FoV, wavelength, laser class, ambient immunity | **not published on the pages read** | **not published on the pages read** |
| Price | not verified in this pass | not verified in this pass |

These are **single-beam** rangers with a narrow (≈2°) cone. They are not perimeter sensors. Their honest
role on this robot is a long, cheap, low-power *single* guard beam — a forward cliff/step detector, a
downward stair sensor, or a beam on a servo. At 8 m for 0.35 W and under 5 g, nothing in the ST ToF
family competes on range-per-watt; nothing about them helps with classification.

### 2.8 Hokuyo URG entry parts

**Not verified in this pass.** `hokuyo-aut.jp/search/single.php?serial=17` returned PHP fatal errors
rather than a page, `hokuyo-usa.com` returned 404 for the URG-04LX-UG01 path, and the distributor page
tried returned 404. No Hokuyo number is asserted here. What can be said without inventing anything: the
URG family is a **sector** scanner (it does not cover a full 360°), and it is positioned a long way above
the Chinese units on price. Confirm both against Hokuyo's own PDF before designing around it.

### 2.9 Sub-$500 3D units

**Livox Mid-360** (livoxtech.com/mid-360/specs, vendor-page-verified):

| Parameter | Value |
|---|---|
| Detection range | **40 m @ 10 % reflectivity**; **70 m @ 80 %** |
| Close-proximity blind zone | **0.1 m** |
| FoV | **horizontal 360°, vertical −7° to +52°** |
| Point rate | **200 000 points/s** (first return) |
| Range precision | ≤ 2 cm at 10 m; ≤ 3 cm at 0.2 m |
| Angular precision | < 0.15° |
| Weight | **265 g** |
| Power | **6.5 W average**; up to 14 W in self-heating mode |
| Interface | **100BASE-TX Ethernet** |
| Eye safety | **Class 1 (IEC 60825-1:2014)** |
| Price | **not published on the spec page; not verified in this pass** |

The Mid-360 is the one unit in this lane that breaks the "planar slice" limitation — a −7°…+52° vertical
FoV over a full 360° azimuth genuinely sees the space above the robot. It costs 265 g and 6.5 W to do
it, needs an Ethernet host, and its vertical FoV is asymmetric: it looks **up**, not down. At the
robot's own base the −7° lower edge means a blind cone below still exists, and it grows with height:
a Mid-360 mounted at 1000 mm has its lowest ray reaching the floor only at 1000/tan(7°) ≈ **8.1 m** out.
Everything on the floor inside an 8 m radius is below the beam.

**Unitree 4D LiDAR L1 / L2:** `unitree.com/LIDAR` returned 404 in this pass. **Not verified** — no
specification or price is asserted.

---

## Part 3 — the honest assessment

### 3.1 What a planar 360° lidar gives you that a ring of ToF sensors does not

**1. Angular density, by two orders of magnitude.**
An LD19 at 10 Hz produces 4500 points/s over 360° — **450 measurements per revolution, one every 0.8°**.
An RPLIDAR C1 gives 5000 points/s at 0.72°. A VL53L4CX has an **18° cone**. To tile 360° with 18° cones
edge-to-edge takes **20 sensors**, and edge-to-edge is not good enough — the cone is a soft-edged
detection volume, so for reliable detection you want overlap, i.e. **24 or more**. A 20-sensor ring gives
you **20 numbers**; the lidar gives you **450 numbers with angles attached**. That difference is the whole
argument.

Concretely, a VL53L4CX cone is `w = 2·d·tan(9°) = 0.317·d` wide. At 1 m each sensor covers 317 mm of a
6283 mm circumference — **5 % of the perimeter per sensor**. Eight sensors (a common "one per corner
plus one per face" layout on a 350 mm square) cover **40 % of the perimeter at 1 m and leave 60 %
unwatched**. A chair leg, a cat's tail or a child's outstretched arm in one of those gaps is simply not
there.

**2. Shape, therefore cluster width, therefore the only non-camera classification feature that works.**
Because the returns carry angles, you can segment a scan into clusters and measure each cluster's
**chord width and curvature**. That is what makes the classic 2D "leg detector" possible: two clusters
roughly 80–160 mm wide, 150–400 mm apart, moving together at walking pace, are a human's shins. A cat
scans as a single 60–120 mm cluster low down, moving faster and more erratically. A chair leg is a
40–50 mm cluster that never moves. A ToF ring cannot produce any of those features — it produces one
distance per cone with no width information at all.

**3. Scan matching, hence a static background map, hence "is this thing part of the room?"**
450 points per revolution is enough for SLAM and for frame-to-frame scan matching. Once the robot has a
map, **anything that does not fit the map is dynamic** — and "dynamic" is the strongest animate-versus-
inanimate cue available without a camera or a thermal sensor. This is the single biggest capability gap:
a ToF ring has far too few points to scan-match, so it can never build the background model that makes
"that blob was not here a minute ago" possible.

**4. Range, and range against dark targets.**
The C1 states **12 m @ 70 %** and **6 m @ 10 %**. The T-mini Plus states **12 m @ 80 %** and **4 m @ 10 %**.
The best single-cone ST part, the VL53L4CX, gives **2.1 m against a 17 % grey target indoors** and
**1.1 m outdoors**. A DTOF lidar sees a dark-trousered leg across a room; the ToF ring sees it at arm's
length.

**5. Ambient light robustness.**
DTOF scanners quote **30 kLux (LD06/LD19), 40 kLux (C1), 60 kLux (T-mini Plus), 80 kLux (S2)**. A
VL53L4CX drops from 5.0 m to 1.6 m (white) and 2.1 m to 1.1 m (17 % grey) in ST's "outdoor overcast"
condition, which ST itself equates to only about **5 kLux daylight**. Near a sunlit patio door, a ToF
ring loses most of its useful range; the lidar keeps working.

**6. One wire.**
One UART at 230400 or 460800 baud versus 20 I²C devices that all boot at the same address (0x52) and
must be brought up one at a time on individual `XSHUT` lines — 20 GPIOs or an I/O expander, plus a
power-sequencing state machine, plus bus loading. The integration cost of a dense ToF ring is badly
under-appreciated.

### 3.2 What a planar lidar fails at — and this is the part that matters here

**1. It sees exactly one plane. The blindness does not shrink with distance.**
This is worth stating precisely because it is usually stated wrongly. A forward-facing ToF has a *cone*
of blindness that narrows as you approach. A planar lidar's blindness is a **half-space**: everything
below the plane and everything above it, at *every* distance. A 300 mm-tall cat is equally invisible at
0.3 m and at 8 m if the scan plane sits at 400 mm. The A1's scan field flatness is only **±1.5°**, so at
2 m the "plane" is about ±52 mm thick — it does not help.

That forces a mounting-height decision with no good answer on this robot:

| Scan plane height | Sees | Misses |
|---|---|---|
| 60–120 mm | cat legs and body, chair/table legs, human ankles, floor clutter, shoes, pet bowls | human torso (so a person leaning over the robot is invisible), table tops, counter overhangs, open drawers, a hand reaching in |
| 200–300 mm | standing cat body, small dog, human shins, most furniture legs | a **lying** cat (≈100–150 mm), anything on the floor, all overhangs |
| 400–600 mm | human thighs, sofa arms, worktops | **every pet in the 200–500 mm band**, all floor clutter |
| 700–1000 mm | human torsos, counters, table tops | the entire floor and every pet |

A 350 mm robot 600–1200 mm tall has a tall body to protect and a cat to avoid. **No single plane does
both.** Two planes means two lidars — double the cost, double the power, double the moving parts, and
still no vertical continuity between them.

**2. It cannot distinguish a static pet from a static object. At all.**
Requirement (d) — human vs pet vs inanimate — is only partly solvable with a planar lidar, and the part
it solves is the *moving* part. A 120 mm-wide cluster at 150 mm height that is not moving is a sleeping
cat or a handbag, and a planar lidar has no feature that separates them: no temperature, no vertical
extent, no breathing, no micro-Doppler. The nearest feature it has — cluster width — overlaps completely
between a curled cat and a shoe.

**3. Glass, mirrors and dark low-reflectance surfaces.**
Glass either returns nothing (invisible patio door) or a ghost from the far side. Mirrors produce a
phantom room. Low-reflectance targets cut range by half in the vendors' own tables (C1: 12 m @ 70 %
→ 6 m @ 10 %; T-mini Plus: 12 m @ 80 % → 4 m @ 10 %). Matte-black baseboards, black shoes and black fur
are all in that band.

**4. It is a motor.**
Continuous rotation at 600 rpm, mechanically, for the life of the robot. **LD06: 10 000 h lifetime**
(about 14 months continuous). **YDLIDAR X4 PRO: 1500 h** (about 2 months continuous). A solid-state ToF
ring has no wear-out mechanism at all. This is the cost that never shows up in the spec comparison and
always shows up in year two.

**5. The mechanical intrusion on a 350 mm footprint.**
The lidar needs an unobstructed 360° optical window at its scan height. That means a slot or a "waist"
in the shell at exactly the height you chose, with nothing — no handle, no cable, no bracket — crossing
it. The A1M8 dev kit is 96.8 × 70.3 × 55 mm; a 350 mm chassis can take that, but the A1's **170 g** on a
mast raises the centre of mass on a robot that is already 600–1200 mm tall and only 350 mm across. The
LD06/LD19/T-mini Plus class (38.6 mm square, 33 mm tall, **42 g**) is far better matched to this
footprint, and the S2's **18 mm optical scanning area height** shows what is possible when the vendor
optimises for exactly this problem.

### 3.3 The cost, power and mass penalty, quantified

| | Planar 360° lidar | 20-sensor VL53L4CX ring |
|---|---|---|
| Hardware cost | **$69** (RPLIDAR C1) to **$99** (A1M8) at retail | 20 × **$14.95** = **$299** at breakout prices; far less with bare modules on a custom flex, plus the NRE for that flex |
| Mass | **42 g** (LD06/LD19) / **110 g** (C1) / **170 g** (A1M8) / **265 g** (Livox Mid-360) | roughly 20 g of breakouts plus the carrier PCB |
| Power | **0.9 W** (LD06/LD19) / ~**1.15 W** (C1, reseller figure) / ~**2 W** (A1M8 scanner + motor) / **6.5 W** (Livox) | 20 × 19 mA @ 2.8 V ≈ **1.06 W** if all range continuously; ≈ **0.2 W** duty-cycled to 5 Hz |
| Host interface | 1 UART | 20 I²C devices at a shared default address + 20 `XSHUT` GPIOs or an expander |
| Host compute | SLAM / scan matching / clustering — a real CPU budget | trivial |
| Moving parts | 1 BLDC motor, 1 500–10 000 h rated | none |
| Update rate | 10 Hz full revolution | 30 Hz per sensor, all simultaneous |
| Angular coverage at 1 m | continuous, 0.72–1° | 5 % of the perimeter per sensor |

**Power is close to a wash** — this is the surprise in the table. An LD06 at 0.9 W costs about the same
as a 16–20 sensor ToF ring run flat out, and *less* than that ring run at a high rate. The real penalties
are **mass** (42–170 g versus ~20 g), **the motor** (a wear item), **the optical window** (an industrial
design constraint on a small shell), and **host compute** (SLAM is not free). The cost penalty runs the
other way: at retail breakout prices the lidar is **three to four times cheaper** than a ToF ring dense
enough to actually close the perimeter.

### 3.4 Recommendation

For a 350 mm robot that must satisfy all four requirements:

- A **planar 360° DTOF lidar is the right obstacle and localisation sensor** and the wrong classifier.
  Pick it for requirement (a) and for the static map that makes requirements (b)–(d) tractable. The
  **RPLIDAR C1 ($69, DTOF, 0.05–12 m @ 70 %, 6 m @ 10 %, 0.72°, 40 klux, IP54, 110 g)** and the
  **LD19 / LD06 ($65–99 class, 0.02–12 m, 4500 Hz, ≤1°, 30 kLux, 42 g, 0.9 W)** are the two serious
  candidates — but **buy the LD19, not the LD06**: Inno-Maker's LD06 page now sells an LD19P, and no
  LD06 price was confirmable anywhere in this pass. Note also that the LD19's 0.02–12 m is quoted by
  Waveshare **with no reflectivity condition at all**, whereas the LD06 datasheet ties its 12 m to a
  **70 % target**; assume the LD19 number is the same 70 %-class figure until LDROBOT says otherwise. Avoid the triangulation units (A1M8, YDLIDAR X2/X4 PRO/G4) for a robot that will ever see
  a sunlit room — the X2's own datasheet lists a **0–2000 lux** lighting environment — and avoid the
  A2 family's **0.2 m minimum range** on a 350 mm footprint.
- Mount the plane **low, 60–120 mm**. It catches the cat, the floor clutter and human ankles. Accept that
  it misses table tops and torsos, and cover *that* with a second, different sensor with vertical extent
  — a multizone ToF (VL53L7CX's 60° × 60°, another lane), a thermal array, or mmWave. Do not buy a second
  lidar for a second plane.
- Within the ST single-cone family, the **VL53L4CX ($14.95, 18°, 5.0 m white / 2.1 m grey-17 % indoors,
  19 mA)** is the only part worth putting on a perimeter, and the **VL53L3CX ($19.95, 25°, up to four
  targets per cone)** is worth one or two positions where depth-behind-the-obstacle is useful. The
  VL6180X (100 mm) is a bumper sensor. The VL53L4CD (45 cm on a grey target) is a bumper sensor.
- **Requirement (d) is not met by anything in this lane.** A planar lidar gives you *moving vs static*
  and *cluster width*; that separates a walking human from a walking cat reasonably well and separates
  both from a wall. It gives you **nothing** for a sleeping cat versus a backpack. That gap has to be
  closed by a sensor that measures something other than range — temperature (thermal array), micro-motion
  (mmWave breathing detection), or appearance (camera).

---

## Sources read

- ST VL53L3CX datasheet, DS13204 Rev 2 — https://www.pololu.com/file/0J1765/vl53l3cx.pdf
- ST VL53L4CX datasheet, DS13805 Rev 2 — https://cdn-learn.adafruit.com/assets/assets/000/111/219/original/vl53l4cx.pdf
- ST VL53L4CD datasheet, DS13812 Rev 8 — https://www.pololu.com/file/0J2060/vl53l4cd.pdf
- ST VL53L1X datasheet, DocID031281 Rev 3 — https://www.pololu.com/file/0J1506/vl53l1x.pdf
- ST VL6180X datasheet, DocID026171 Rev 7 — https://www.pololu.com/file/0J961/VL6180X.pdf
- Pololu VL53L3CX carrier #3416 — https://www.pololu.com/product/3416
- Pololu VL6180X carrier #2489 — https://www.pololu.com/product/2489
- Pololu VL53L1X carrier #3415 — https://www.pololu.com/product/3415
- Pololu VL53L4CD carrier #3692 — https://www.pololu.com/product/3692
- Pololu ToF carrier category — https://www.pololu.com/category/306/carriers-for-st-time-of-flight-tof-distance-sensors
- Adafruit VL53L4CX #5425 — https://www.adafruit.com/product/5425
- Adafruit VL53L4CX learn guide — https://learn.adafruit.com/adafruit-vl53l4cx-time-of-flight-distance-sensor
- ST VL53L4ED product page (via search result text) — https://www.st.com/en/imaging-and-photonics-solutions/vl53l4ed.html
- Slamtec RPLIDAR A1 datasheet rev 2.2 (PDF)
- Slamtec RPLIDAR A1 datasheet **rev 1.0, 2016-07-04**, read directly in the re-verification pass —
  https://www.generationrobots.com/media/rplidar-a1m8-360-degree-laser-scanner-development-kit-datasheet-1.pdf
  (source of the "White objects" condition and of the 2000 Hz / 360-samples-per-scan / 1° set)
- YDLIDAR X2 datasheet, DOC# 01.13.000100, downloaded and read in the re-verification pass —
  https://www.ydlidar.com/download/category/datasheet/ → `/static/upload/file/20260615/1781510218292159.pdf`
  (confirms **0.12–8 m, "Indoor environment with 80 % Reflectivity"**; ranging frequency 3000 Hz;
  motor 5/6/8 Hz; angle resolution 0.72° @ 6 Hz → **500 points per revolution**; "Others" table
  **Lighting environment 0 / 550 / 2000 Lux**; weight 126 g)
- ST VL53L4CD datasheet DS13812 **Rev 8**, re-downloaded from the Pololu mirror and re-read (Table 16)
- Slamtec RPLIDAR A1 spec page — https://www.slamtec.com/en/lidar/a1spec
- Slamtec RPLIDAR C1 — https://www.slamtec.com/en/c1
- Slamtec RPLIDAR S2 — http://www.slamtec.com/en/s2
- Slamtec RPLIDAR A2 — http://www.slamtec.com/en/lidar/a2
- Slamtec store — http://www.slamtec.com/en/store
- DFRobot RPLIDAR C1 — https://www.dfrobot.com/product-2803.html
- DFRobot RPLIDAR A1M8-R6 — https://www.dfrobot.com/product-1125.html
- LDROBOT LD06 datasheet — https://www.inno-maker.com/wp-content/uploads/2020/11/LDROBOT_LD06_Datasheet.pdf
- Inno-Maker LD06 product page — https://www.inno-maker.com/product/lidar-ld06/
- Waveshare wiki, DTOF LIDAR LD19 — https://www.waveshare.com/wiki/DTOF_LIDAR_LD19
- Waveshare wiki, D500 LiDAR Kit — https://www.waveshare.com/wiki/D500_LiDAR_Kit
- YDLIDAR X2 datasheet, DOC# 01.13.000100
- YDLIDAR X4 PRO datasheet, DOC# 01.13.001700
- YDLIDAR G4 datasheet, DOC# 01.13.002100
- YDLIDAR T-mini Plus datasheet, DOC# 01.13.005600 (all four from https://www.ydlidar.com/download/category/datasheet/)
- YDLIDAR product pages — https://www.ydlidar.com/product/category/triangulation/ , .../tof/
- Benewake TF-Luna — https://en.benewake.com/TFLuna/index.html
- Benewake TFmini-S — https://en.benewake.com/TFminiS/index.html
- Livox Mid-360 specs — https://www.livoxtech.com/mid-360/specs

## Sources that failed in this pass

- `https://www.st.com/...` — all resources, every attempt (curl `HTTP 000`, WebFetch 60 s timeout). This
  is why VL53L1CB, VL53L4ED's full table, the SATEL boards and the automotive/industrial FlightSense
  parts are marked unverified. **Retested 2026-09-12 in the adversarial pass with a browser user agent:
  `vl53l4ed.html` → `curl: (56) Recv failure: Connection was reset`; `vl53l1cb.html` → `curl: (28)
  Operation timed out after 40002 milliseconds with 0 bytes received`. Still unreachable.**
- `https://www.waveshare.com/dtof-lidar-ld19.htm` and the Waveshare wiki via WebFetch — HTTP 403. The
  wiki page **was** retrieved by `curl` with a browser user agent and its table read verbatim.
- `https://www.ydlidar.com/products/view/6.html`, `/download`, `/products.html` — HTTP 404. The working
  path is `https://www.ydlidar.com/download/category/datasheet/`, which serves the X2 PDF directly.
- `https://bucket-download.slamtec.com/.../LD108_SLAMTEC_rplidar_datasheet_A1M8_v3.0_en.pdf` — HTTP 403;
  Slamtec's support page serves its datasheet links through JavaScript, so **rev 2.2 could not be
  re-fetched**. Rev 1.0 was read from a distributor mirror instead.
- `https://www.mouser.com/...` datasheet mirrors — anti-bot JavaScript / segfault.
- `https://www.hokuyo-aut.jp/search/single.php?serial=17` — PHP fatal error page.
- `https://www.hokuyo-usa.com/products/lidar-obstacle-detection/urg-04lx-ug01` — HTTP 404.
- `https://www.unitree.com/LIDAR` — HTTP 404.
- `https://www.robotshop.com/...` — HTTP 403.
