# ST Multizone "Grid" dToF Imagers — Standalone Product Guide

**Lane:** `st-grid-tof-latest`
**Date of research:** 2026-09-12
**Scope:** ST FlightSense multizone grid sensors — VL53L5CX, VL53L7CX, VL53L8CX, the histogram
(`CH`) variants, and the newest member of the line. Written as a standalone recommendation for a
350 mm-footprint, 600–1200 mm-tall mobile robot needing 360-degree obstacle, human and pet
detection.

---

## 0. Answer first

1. **The latest ST grid sensor as of 2026-09-12 is the VL53L9CX**, not the VL53L8CX. It is a
   different class of device: a 54 x 42 zone (2268-zone) BSI-stacked dToF *camera module* with
   MIPI I3C / MIPI CSI-2 output, <5 cm to 8.8 m range and 100 Hz frame rate. **The 8.8 m is ST's
   unconditioned headline figure.** ST publishes no per-reflectance, per-ambient-light maximum-range
   table for the VL53L9CX, so 8.8 m is *not* comparable with the conditioned CX numbers in
   sections 2–4, where the equivalent headline (400 cm) collapses to 950 mm under 5 kLux against a
   17% target. It was announced by
   ST with mass production starting early July 2026. It is **not** a drop-in for the VL53L8CX and
   **not** usable on a microcontroller.
2. **There is no VL53L5CH.** The histogram variants ST has actually released are the **VL53L7CH**
   (90 deg FoV) and **VL53L8CH** (65 deg FoV). No VL53L5CH product page, datasheet or driver was
   found.
3. **For the 350 mm robot, the buildable answer today is a ring of 10–12 VL53L7CX** (60 x 60 deg)
   with one **VL53L8CH** facing forward for classification. See sections 7–10 for the arithmetic.
4. **The 8x8 grid silhouette alone cannot classify human vs pet vs box.** At the ranges where the
   sensor still returns data in a lit room (1.0–1.6 m for dark targets), a cat is 1–2 zones and a
   human is a truncated blob. Classification has to come from *height above a calibrated floor
   plane*, the *per-zone motion indicator*, and (best) the **CNH histogram** of the CH parts.

---

## 1. Establishing the latest part

ST's grid-ToF line, in release order:

| Part | Grid | FoV (H x V) | Max range | Host interface | Status 2026-09-12 |
|---|---|---|---|---|---|
| VL53L5CX | 4x4 / 8x8 | 45 x 45 deg (63 deg diag) | 400 cm | I2C 1 MHz | Active, widely stocked |
| VL53L7CX | 4x4 / 8x8 | 60 x 60 deg (90 deg diag) | 350 cm | I2C 1 MHz | Active, widely stocked |
| VL53L7CH | 4x4 / 8x8 + CNH | 60 x 60 deg (90 deg diag) | 350 cm | I2C / SPI | Active (Arduino lib last touched 2024-07-24) |
| VL53L8CX | 4x4 / 8x8 | 45 x 45 deg (65 deg diag) | 400 cm | I2C 1 MHz / SPI 20 MHz | Active, widely stocked |
| VL53L8CH | 4x4 / 8x8 + CNH | 45 x 45 deg (65 deg diag) | 400 cm | I2C 1 MHz / SPI 3 MHz | Active |
| **VL53L9CX** | **54 x 42 (2268 zones)** | **55 x 42 deg (71 deg diag)** | **8.8 m** (no reflectance / ambient condition published) | **MIPI I3C / MIPI CSI-2** | **Newest. MP started early July 2026** |

Every "max range" in the column above is an unconditioned headline. The CX/CH figures are traceable
to a datasheet table that states reflectance, ambient light, resolution and frame rate (sections 2–5);
the VL53L9CX figure is not, because ST publishes no equivalent table for it.

**Source for "newest":** ST's own press release announcing the VL53L9CX
([newsroom.st.com p4783](https://newsroom.st.com/media-center/press-item.html/p4783.html)), the ST
product page [st.com/en/imaging-and-photonics-solutions/vl53l9cx.html](https://www.st.com/en/imaging-and-photonics-solutions/vl53l9cx.html),
the VL53L9CX datasheet [st.com/resource/en/datasheet/vl53l9cx.pdf](https://www.st.com/resource/en/datasheet/vl53l9cx.pdf),
and independent coverage dated 2026-06-22
([CNX Software](https://www.cnx-software.com/2026/06/22/st-vl53l9cx-direct-time-of-flight-3d-lidar-supports-5cm-to-9m-range-2-3k-zones-resolution/)).
Distributor confirmation: DigiKey lists **STEVAL-VL53L9** (P/N 29294599) as an active part at
**$80.39**, **0 in stock, 1 unit expected 2026-10-28**, 4-week factory lead time.

**No VL53L10 / VL53L9CH / any later grid part was found.** Searching ST's line, DigiKey, Mouser and
the `stm32duino` GitHub organisation returns nothing after the VL53L9CX. Treat the VL53L9CX as the
end of the line as of 2026-09-12.

> **Transparency on sourcing:** `st.com` was unreachable from the research host (all direct
> `curl`/fetch attempts to `st.com` returned zero bytes or timed out). The VL53L5CX, VL53L7CX,
> VL53L8CX and VL53L8CH datasheets below were read in full from byte-identical distributor mirrors
> (Pololu, Farnell, MikroElektronika) and are marked **datasheet-verified**. The VL53L9CX datasheet
> could **not** be retrieved; its figures below come from ST's product page, ST's press release and
> the DigiKey listing, and are marked **vendor-page-verified**.

> **Adversarial re-check, 2026-09-12.** Every hard number in sections 2, 3, 4 and 5 was
> independently re-extracted from the datasheet PDFs (`pdftotext -layout`) rather than taken from
> this document: VL53L8CX **DS14161 Rev 2, March 2023**; VL53L5CX **DS13754 Rev 5, December 2021**;
> VL53L7CX **DS13865 Rev 6, March 2023**; VL53L8CH **DS14310 Rev 3, August 2023**. All range tables,
> FoV angles, exclusion zones, accuracy figures and CNH configurations matched. Two things changed:
> the VL53L8CH range tables turned out to be published after all (new section 5.5), and three
> stock/lead-time figures in section 11 were corrected. `st.com` remains unreachable from this host
> — direct requests return HTTP 000 and zero bytes — so the VL53L9CX figures are still
> vendor-page-verified only.

---

## 2. VL53L8CX — the workhorse (datasheet-verified, DS14161 Rev 2, March 2023)

### 2.1 Headline specification (Table 1, verbatim)

| Feature | Detail |
|---|---|
| Package | Optical LGA16, 6.4 x 3.0 x 1.75 mm |
| Ranging | 2 to 400 cm per zone |
| Operating voltage | AVDD 3.3 V, CORE_1V8 1.8 V, IOVDD 1.2 / 1.8 V |
| Operating temperature | -30 to 85 degC |
| Sample rate | Up to 60 Hz |
| Infrared emitter | 940 nm, Class 1 eye-safe VCSEL |
| Interface | I2C 1 MHz, address 0x52; SPI 20 MHz |
| Ranging mode | Continuous or autonomous |

### 2.2 Field of view — read this carefully

| Table 2 row | Horizontal | Vertical | Diagonal |
|---|---|---|---|
| Detection volume | **45 deg** | **45 deg** | 65 deg |
| Collector exclusion zone | 57.9 deg | 57.9 deg | 86.6 deg |

Measurement condition for the detection volume, verbatim: *"white 88% reflectance perpendicular
target, in full FoV, located at 1 m from the sensor, without ambient light (dark conditions), with
an 8x8 resolution, with a 14% sharpener (default value), in continuous mode, at 15 Hz."*

**Critical geometry note.** ST's "diagonal" figure is a separately measured number, not the
geometric diagonal of the square FoV. A true 45 x 45 deg square has a diagonal of 60.7 deg, not
65 deg; a 60 x 60 deg square has a diagonal of 78.5 deg, not 90 deg. **Never derive zone pitch from
ST's diagonal number.** Use the H and V figures. Every calculation in this document uses 45 x 45
(L5CX/L8CX/L8CH), 60 x 60 (L7CX/L7CH) and 55 x 42 (L9CX).

Field of illumination (separate from detection volume): 43.4 x 43.4 deg at the 75%-of-peak contour,
57.9 x 57.9 deg at the 10%-of-peak contour.

### 2.3 Maximum ranging distance — the numbers that actually matter

All conditions: target fills 100% of the FoV in all zones; Munsell N4.75 (17%), N8.25 (54%),
N9.5 (88%); AVDD 3.3 V; 23 degC; **max range capability is based on a 90% detection rate**; 5 kLux
is realised as 2 W/m2 target irradiance at 940 nm; no cover glass, crosstalk margin 0 kcps.

**Table 16 — continuous, 4x4, 30 Hz**

| Target reflectance | Zone | Dark, typ | Dark, min | 5 kLux, typ | 5 kLux, min |
|---|---|---|---|---|---|
| White 88% | Inner | 4000 mm | 4000 mm | 2850 mm | 2850 mm |
| White 88% | Corner | 4000 mm | 4000 mm | 2850 mm | 2700 mm |
| Light grey 54% | Inner | 4000 mm | 4000 mm | 2600 mm | 2550 mm |
| Light grey 54% | Corner | 4000 mm | 4000 mm | 2500 mm | 2400 mm |
| Grey 17% | Inner | 4000 mm | 4000 mm | **1650 mm** | 1600 mm |
| Grey 17% | Corner | 3950 mm | 3900 mm | **1550 mm** | 1500 mm |

**Table 17 — continuous, 8x8, 15 Hz**

| Target reflectance | Zone | Dark, typ | Dark, min | 5 kLux, typ | 5 kLux, min |
|---|---|---|---|---|---|
| White 88% | Inner | 4000 mm | 4000 mm | 1550 mm | 1100 mm |
| White 88% | Corner | 3950 mm | 2900 mm | 1400 mm | 1100 mm |
| Light grey 54% | Inner | 3300 mm | 2350 mm | 1400 mm | 1000 mm |
| Light grey 54% | Corner | 3100 mm | 2100 mm | 1250 mm | 950 mm |
| Grey 17% | Inner | 2450 mm | 1500 mm | **1150 mm** | 900 mm |
| Grey 17% | Corner | 1950 mm | 1300 mm | **950 mm** | 700 mm |

**Table 20 — autonomous, 8x8, 1 Hz, 5 ms integration**

| Target reflectance | Zone | Dark, typ | Dark, min | 5 kLux, typ | 5 kLux, min |
|---|---|---|---|---|---|
| White 88% | Inner | 3600 mm | 2400 mm | 1250 mm | 1000 mm |
| White 88% | Corner | 2850 mm | 1700 mm | 1150 mm | 800 mm |
| Light grey 54% | Inner | 2600 mm | 1900 mm | 1100 mm | 900 mm |
| Light grey 54% | Corner | 2200 mm | 1350 mm | 1000 mm | 750 mm |
| Grey 17% | Inner | 1400 mm | 1200 mm | 850 mm | 800 mm |
| Grey 17% | Corner | 1350 mm | 900 mm | 700 mm | 700 mm |

**The single most important line in this whole document:** in 8x8 at 15 Hz against a 17% grey
target under 5 kLux ambient, the *corner* zones of a VL53L8CX are specified at **typical 950 mm,
minimum 700 mm**. A person in dark trousers, in an ordinary lit room, at the edge of the FoV, is a
sub-metre sensor. The "400 cm" on the box is a dark-room, white-target, inner-zone, 4x4 number.

### 2.4 Range accuracy (Table 18)

| Mode | Distance | Reflectance | Dark (0 kLux) | 5 kLux |
|---|---|---|---|---|
| 4x4, 30 Hz | 20–200 mm | White 88% | ±10 mm | ±12 mm |
| 4x4, 30 Hz | 20–200 mm | Light grey 54% | ±9 mm | ±11 mm |
| 4x4, 30 Hz | 20–200 mm | Grey 17% | ±8 mm | ±10 mm |
| 4x4, 30 Hz | 200–4000 mm | White 88% | ±3% | ±4% |
| 4x4, 30 Hz | 200–4000 mm | Light grey 54% | ±4% | ±6% |
| 4x4, 30 Hz | 200–4000 mm | Grey 17% | ±4% | ±7% |
| 8x8, 15 Hz | 20–200 mm | White 88% | ±11 mm | ±10 mm |
| 8x8, 15 Hz | 20–200 mm | Light grey 54% | ±12 mm | ±13 mm |
| 8x8, 15 Hz | 20–200 mm | Grey 17% | ±12 mm | ±14 mm |
| 8x8, 15 Hz | 200–4000 mm | White 88% | ±5% | ±5% |
| 8x8, 15 Hz | 200–4000 mm | Light grey 54% | ±5% | ±6% |
| 8x8, 15 Hz | 200–4000 mm | Grey 17% | ±5% | ±8% |

Datasheet notes, verbatim: *"The accuracy of the corner zone data compared to the center 4 zones may
degrade by up to 4%."* and *"Final assemblies should include additional tolerance for PCB assembly
tilt, and mounting of the PCB in a product housing. Typically an additional 1~2%."*

### 2.5 Current and power (Tables 12, 13, 14)

| Device state | AVDD typ | AVDD max | CORE_1V8 typ | CORE_1V8 max | IOVDD typ | IOVDD max | Unit |
|---|---|---|---|---|---|---|---|
| LP idle | 55 | 390 | 0.01 | 0.5 | 0.5 | 2 | µA |
| HP idle | 1 | 1.6 | 3 | 17 | 0.0003 | 0.002 | mA |
| Active ranging | 43 | 50 | 50 | 80 | 0.003 | 0.006 | mA |

Verbatim: *"Active ranging is when the device is actively ranging. The current consumption is not
affected by a 4x4 or 8x8 zone configuration."* Peak currents are average + 10 mA on each rail.

Typical power, continuous mode (4x4 or 8x8), AVDD 3.3 V / IOVDD+CORE 1.8 V: **215 mW**.
Autonomous mode: 4x4 @ 1 Hz / 5 ms = **1.6 mW**; 4x4 @ 5 Hz = 12.5 mW; 8x8 @ 1 Hz = **6.7 mW**;
8x8 @ 5 Hz = 32.3 mW.

That 1.6–6.7 mW autonomous figure is the reason to care about this part for a battery robot: a
64-zone depth frame once a second for under 7 mW, with an interrupt that wakes the host only when a
programmed distance or motion threshold is crossed.

---

## 3. VL53L5CX (datasheet-verified, DS13754 Rev 5, December 2021)

The older, cheaper, most widely stocked part. Same 4x4/8x8 grid, same 84 kB firmware upload, same
ULD API. Key differences from the L8CX:

- FoV detection volume **45 x 45 deg, 63 deg diagonal** (exclusion zone 55.5 x 61 deg, 82 deg
  diagonal) — note the exclusion zone is *not square* on this part.
- Size 6.4 x 3.0 x **1.5** mm.
- **I2C only** (1 MHz). No SPI.
- Flexible supply: single 3.3 V or 2.8 V, or 3.3/2.8 V AVDD with 1.8 V IOVDD.
- Only **two** reflectance levels characterised (88% and 17%). Footnote on the grey target,
  verbatim: *"measured 13% in IR at 940 nm"* — so ST's own "17%" grey is a **13% target at the
  sensor's wavelength**. Apply the same caution to the L7CX/L8CX numbers.

**Table 18 — continuous, 8x8, 15 Hz**

| Target | Zone | Dark, typ | Dark, min | 5 kLux, typ | 5 kLux, min |
|---|---|---|---|---|---|
| White 88% | Inner | 3500 mm | 2600 mm | 1100 mm | 950 mm |
| White 88% | Corner | 3100 mm | 1700 mm | 1000 mm | 800 mm |
| Grey 17% | Inner | 1300 mm | 900 mm | 800 mm | 600 mm |
| Grey 17% | Corner | 1100 mm | 600 mm | **650 mm** | **400 mm** |

**Table 17 — continuous, 4x4, 30 Hz**

| Target | Zone | Dark, typ | Dark, min | 5 kLux, typ | 5 kLux, min |
|---|---|---|---|---|---|
| White 88% | Inner | 4000 mm | 4000 mm | 1700 mm | 1400 mm |
| White 88% | Corner | 4000 mm | 4000 mm | 1400 mm | 1100 mm |
| Grey 17% | Inner | 2400 mm | 1900 mm | 1000 mm | 900 mm |
| Grey 17% | Corner | 2200 mm | 1800 mm | 950 mm | 850 mm |

Accuracy (Table 19): 20–200 mm → ±15 mm dark, 15 mm at 5 kLux (all zones, both targets);
201–4000 mm → 4x4 white ±4% dark / 7% lit, 4x4 grey ±5% / 8%, 8x8 white ±5% / 8%, 8x8 grey
±5% / **11%**.

Current: LP idle 45 µA AVDD typ; HP idle 1.3 mA; active ranging **45 mA AVDD + 50 mA IOVDD typ**.
Continuous-mode power 216 mW (2V8/1V8) to 313 mW (3V3/3V3).

**Compared to the L8CX at 8x8/15 Hz in 5 kLux, the L5CX loses roughly 30–45% of its range.** The
Pololu product page states the same thing in applied terms: in 5000 lux the VL53L8CX detects large
reflective targets to about 2.8 m versus about 1.7 m for the VL53L5CX. If the robot works in
daylight-lit rooms, the extra $5 for the L8CX is not optional.

---

## 4. VL53L7CX (datasheet-verified, DS13865 Rev 6, March 2023)

The wide-FoV part — and the one that matters most for a 360-degree ring, because FoV is what sets
the sensor count.

- Detection volume **60 x 60 deg** (90 deg diagonal). Exclusion zone 74 x 74 deg (105 deg diagonal).
- 4x4 / 8x8, up to 350 cm, 60 Hz capability, multi-target per zone, motion indicator, autonomous
  low-power mode.
- Size 6.4 x 3.0 x **1.6** mm. I2C only.
- Verbatim: *"Pin-to-pin and driver compatible with VL53L5CX."* You can swap an L5CX carrier for an
  L7CX carrier and change one library include.
- ST's own application note, verbatim: *"Applications requiring ultrawide FoV, like smart speakers,
  vacuum cleaners (three sensors can cover 180 deg x 60 deg FoV)."*

**Table 18 — continuous, 8x8, 15 Hz**

| Target | Zone | Dark, typ | Dark, min | 5 kLux, typ | 5 kLux, min |
|---|---|---|---|---|---|
| White 88% | Inner | 2000 mm | 1700 mm | 500 mm | 400 mm |
| White 88% | Corner | 1900 mm | 1100 mm | 500 mm | 400 mm |
| Lite grey 54% | Inner | 1600 mm | 1500 mm | 400 mm | 400 mm |
| Lite grey 54% | Corner | 1600 mm | 1100 mm | 400 mm | 400 mm |
| Grey 17% | Inner | 800 mm | 700 mm | 350 mm | 250 mm |
| Grey 17% | Corner | 750 mm | 450 mm | **250 mm** | **200 mm** |

**Table 17 — continuous, 4x4, 30 Hz**

| Target | Zone | Dark, typ | Dark, min | 5 kLux, typ | 5 kLux, min |
|---|---|---|---|---|---|
| White 88% | Inner | 3500 mm | 3300 mm | 650 mm | 500 mm |
| White 88% | Corner | 3500 mm | 3300 mm | 600 mm | 600 mm |
| Lite grey 54% | Inner | 2800 mm | 2600 mm | 600 mm | 600 mm |
| Lite grey 54% | Corner | 2800 mm | 2600 mm | 600 mm | 600 mm |
| Grey 17% | Inner | 1400 mm | 1300 mm | 550 mm | 500 mm |
| Grey 17% | Corner | 1400 mm | 1200 mm | 500 mm | 450 mm |

**This is the hard trade.** The wide FoV costs an enormous amount of range under ambient light. In
5 kLux the VL53L7CX at 8x8 is a **0.2–0.5 m** sensor. Even at 4x4/30 Hz it is a 0.5–0.65 m sensor
in 5 kLux. In a dark room it reaches 2 m (8x8) or 3.5 m (4x4). **Six VL53L7CX give you 360-degree
coverage that is useless in daylight.** You get 360 degrees of geometry, not 360 degrees of range.

Autonomous mode, 8x8, 1 Hz, 20 ms integration is slightly better than continuous 15 Hz for the
bright-target cases (white inner: 2000 mm dark typ / 550 mm at 5 kLux) but does not change the
conclusion.

---

## 5. The CH histogram variants — VL53L8CH and VL53L7CH

### 5.1 What CH is

Datasheet DS14310 Rev 3 (August 2023), VL53L8CH, verbatim title: *"Artificial intelligence enabler,
high performance 8x8 multizone Time-of-Flight (ToF) sensor."*

The difference between CH and CX is **firmware, not silicon**: the VL53L8CH is *pin-to-pin
compatible with VL53L8CX* and *driver compatible with VL53L7CH*. The CH firmware exposes the raw
per-zone return-signal-versus-range histogram — the **compact and normalized histogram (CNH)** —
*in addition to* all the normal processed ranging data (distance, signal amplitude, reflectance).

### 5.2 CNH numbers (Tables 16, 17, 18 — datasheet-verified)

| Ranging core histogram parameter | Value |
|---|---|
| Bin width | 250 ps |
| **Bin equivalent range** | **37.5 mm** |
| Number of bins in the core histogram | 128 |

| CNH parameter | Value |
|---|---|
| CNH buffer maximum size | **6160 bytes** |
| Bytes per histogram bin | 5 |
| Maximum zones per CNH aggregate | 64 |
| Maximum histogram binning factor | 8 |
| Bytes per ambient level | 5 |

Verbatim: *"Up to 6 KB of histogram data can be read by the host at every frame."* Ambient light is
measured during ranging and subtracted from the histogram; the removed ambient level is reported
separately per zone.

**Table 18 — example operating configurations** (I2C, SCL 1 MHz; sizes include ambient data, no
per-zone target data):

| Histograms | Bins per histogram | CNH size (bytes) | Transfer time (ms) | Frame rate (fps) |
|---|---|---|---|---|
| 8 | 80 | 3268 | 32 | 30 |
| 8 | 128 | 5188 | 48 | 20 |
| 16 | 48 | 3948 | 36 | 25 |
| 16 | 72 | 5868 | 54 | 18 |
| 32 | 36 | 6108 | 56 | 15 |
| **64** | **18** | **6108** | **56** | **15** |

Note the VL53L8CH's SPI is only **3 MHz** (Table 1), against 20 MHz on the VL53L8CX. Over I2C at
1 MHz, one CH sensor at full 64-zone CNH consumes 56 ms of bus time per frame. **Two CH sensors
saturate a 1 MHz I2C bus at 15 Hz. Ten is impossible.** This is the decisive constraint on how many
CH parts a ring can carry.

CNH configuration parameters (from ST community documentation and UM3183): `cnhStartX`, `cnhStartY`,
`cnhMergeX`, `cnhMergeY`, `cnhCols`, `cnhRows`, `cnhNumBins`, `cnhStartBin`, `cnhSubSample`.
Aggregation is available both spatially (zone merging) and temporally (bin binning).

### 5.3 Why CNH is the classification lever

A zone's histogram is a profile of returned photons against range, at 37.5 mm resolution. What that
buys you, quantitatively:

- A **flat cardboard box face** normal to the sensor puts essentially all its return into **1–2
  bins** (37.5–75 mm of depth spread).
- A **cat or small dog** is a curved, furry body roughly 200–300 mm deep front-to-back inside one
  zone at 2–3 m. Its return spreads over **250 / 37.5 ≈ 7 bins**, with fur scattering producing a
  long, low tail rather than a sharp peak.
- A **human leg** is a ~150 mm cylinder: ~4 bins, with the classic curved-surface asymmetry.
- **Multi-return structure** — a pet in front of a wall — shows as two clearly separated peaks in
  one zone, which the processed "distance" output collapses into one number.

That is a real, physically grounded feature set, and it is exactly why ST markets this part as an
AI enabler. It is also the only thing in this family that gives you material-and-shape information
rather than just range.

### 5.4 Is there a VL53L5CH?

**No.** Searching ST's line, DigiKey and the `stm32duino` GitHub organisation returns `VL53L8CH` and
`VL53L7CH` only. The ST community explicitly describes the CH/CX distinction for the **L7** and
**L8** generations. **Confidence: vendor-page-verified (absence).** If a VL53L5CH is ever needed,
the answer is "buy an L7CH or L8CH".

### 5.5 VL53L8CH maximum ranging distance — separately verified after all

An earlier revision of this document said the CH-specific range numbers were not extracted from
DS14310 and told the reader to use the VL53L8CX tables as a stand-in. **That was wrong.** DS14310
Rev 3 (August 2023) publishes its own per-reflectance, per-ambient maximum-range tables, and they
have now been read in full. Every value is identical to the VL53L8CX — which is what you expect,
because the CH and the CX share optics, VCSEL and silicon and differ only in firmware. The CH
numbers are therefore **datasheet-verified in their own right**, not inherited.

Conditions, same as the VL53L8CX: target fills 100% of the FoV in all zones; Munsell N4.75 (17%),
N8.25 (54%), N9.5 (88%); AVDD 3.3 V; 23 degC; 90% detection rate; 5 kLux realised as 2 W/m2 target
irradiance at 940 nm; no cover glass; crosstalk margin 0 kcps.

**DS14310 Table 19 — continuous, 4x4, 30 Hz**

| Target reflectance | Zone | Dark, typ | Dark, min | 5 kLux, typ | 5 kLux, min |
|---|---|---|---|---|---|
| White 88% | Inner | 4000 mm | 4000 mm | 2850 mm | 2850 mm |
| White 88% | Corner | 4000 mm | 4000 mm | 2850 mm | 2700 mm |
| Light grey 54% | Inner | 4000 mm | 4000 mm | 2600 mm | 2550 mm |
| Light grey 54% | Corner | 4000 mm | 4000 mm | 2500 mm | 2400 mm |
| Grey 17% | Inner | 4000 mm | 4000 mm | **1650 mm** | 1600 mm |
| Grey 17% | Corner | 3950 mm | 3900 mm | **1550 mm** | 1500 mm |

**DS14310 Table 20 — continuous, 8x8, 15 Hz**

| Target reflectance | Zone | Dark, typ | Dark, min | 5 kLux, typ | 5 kLux, min |
|---|---|---|---|---|---|
| White 88% | Inner | 4000 mm | 4000 mm | 1550 mm | 1100 mm |
| White 88% | Corner | 3950 mm | 2900 mm | 1400 mm | 1100 mm |
| Light grey 54% | Inner | 3300 mm | 2350 mm | 1400 mm | 1000 mm |
| Light grey 54% | Corner | 3100 mm | 2100 mm | 1250 mm | 950 mm |
| Grey 17% | Inner | 2450 mm | 1500 mm | **1150 mm** | 900 mm |
| Grey 17% | Corner | 1950 mm | 1300 mm | **950 mm** | 700 mm |

Table 1 of DS14310 also confirms the headline verbatim as *"2 to 400 cm per zone"*, the FoV table
as detection volume **45 x 45 deg (65 deg diagonal)** with a **57.9 x 57.9 deg (86.6 deg diagonal)**
collector exclusion zone, and the interface as *"I2C: 1 MHz serial bus, address: 0x52"* /
*"SPI: 3 MHz"*. The "400 cm" carries exactly the same caveat as on the CX: it is a dark-room,
white-target, inner-zone, 4x4 number.

---

## 6. VL53L9CX — the newest part (vendor-page-verified; datasheet not retrievable from this host)

| Parameter | Value | Source |
|---|---|---|
| Zones | Up to **54 x 42 = 2268** | ST product page |
| FoV | **55 x 42 deg** (71 deg diagonal), software-reducible | ST product page, CNX |
| Range | **<5 cm to 8.8 m** ("5cm ~ 9m" on the DigiKey eval listing) — **unconditioned; no per-reflectance or per-ambient-light table is published for this part** | ST product page, DigiKey |
| Accuracy | Up to 1% | CNX quoting ST |
| Frame rate | Up to **100 Hz** of processed data | ST product page |
| Technology | BSI stacked direct ToF — *"absolute distance measurement whatever the target color and reflectance"* | ST product page |
| Outputs | Depth, 2D IR with active illumination, 2D IR without active illumination, reflectance, confidence | ST product page |
| Host interface | **MIPI I3C or MIPI CSI-2** | CNX quoting ST |
| Supply | 1.2 V and 3.3 V | CNX quoting ST |
| Size | **12.8 x 6.1 x 4.6 mm** | ST product page |
| Chip part number | VL53L9CXV0VE/1 | ST eStore |
| Production | Mass production started early July 2026 | ST press release |

**What it changes and what it does not.** The VL53L9CX is a genuine generational jump: 2268 zones at
100 Hz to 8.8 m is a depth camera, not a proximity grid, and it removes the single biggest weakness
of the CX line — coarse angular resolution. Each zone subtends about **1.02 deg horizontally and
1.00 deg vertically**, versus **5.625 deg** for an 8x8 VL53L8CX.

**But it is the wrong part for this robot, for four concrete reasons:**

1. **MIPI CSI-2 / I3C only.** There is no I2C mode. A CSI-2 receiver means a Linux-class SoC
   (Raspberry Pi CM, i.MX8, Jetson) with a dedicated camera port per sensor. You cannot hang seven
   of these on a microcontroller.
2. **Cost.** The eval board alone is $80.39 at DigiKey; the X-NUCLEO-53L9A1 expansion board is
   $96.44. Seven sensors for a 360-degree ring is a four-figure BOM before the host.
3. **Availability.** DigiKey shows the STEVAL-VL53L9 at **0 in stock**, one unit expected
   **2026-10-28**, 4-week factory lead time, with a 10-per-30-days purchase cap. The
   X-NUCLEO-53L9A1 is **also 0 in stock**, and DigiKey gives it *no* estimated availability date
   ("due to market conditions"). Both read 2026-09-12. Neither VL53L9CX board can be bought today.
   This is a part you design in for 2027, not one you buy ten of this week.
4. **No microcontroller driver ecosystem.** `stm32duino` has no VL53L9 repository. There is no
   Arduino library and no CircuitPython driver.

**Where it does belong on this robot:** one, forward-facing, on the head, if the robot has a Linux
SoC. At 8.8 m and 2268 zones it is a complete replacement for a forward-looking 2D lidar plus a
depth camera, and its angular resolution is enough that a human silhouette is genuinely resolvable
(see section 8). It does not replace the 360-degree ring.

---

## 7. Zone subtense arithmetic

Zone boundaries in these sensors are linear in **tangent space** (the SPAD array maps linearly onto
the image plane), so at range *d*, on a plane perpendicular to the optical axis:

```
full FoV width   W = 2 * d * tan(FoV_H / 2)
per-zone width   w = W / N_columns
```

For a 45 x 45 deg part at 8x8: `w = 2*d*tan(22.5)/8 = 0.10355 * d`. For a 60 x 60 deg part at 8x8:
`w = 0.14434 * d`.

### 7.1 VL53L5CX / VL53L8CX / VL53L8CH — 45 x 45 deg, 8x8

| Range | FoV width | Zone size | Human torso (450 mm) | Human height (1700 mm) | Cat height (250 mm) | Cat length (500 mm) | Box (300 mm) |
|---|---|---|---|---|---|---|---|
| 1 ft / 305 mm | 253 mm | **31.6 mm** | 14.3 col → fills all 8 | 53.9 rows → fills all 8 | 7.9 rows | 15.8 col → fills all 8 | 9.5 x 9.5 → fills frame |
| 3 ft / 914 mm | 758 mm | **94.7 mm** | 4.8 col | 18.0 rows → fills all 8 | 2.6 rows | 5.3 col | 3.2 x 3.2 |
| 5 ft / 1524 mm | 1263 mm | **157.8 mm** | 2.9 col | 10.8 rows → fills all 8 | 1.6 rows | 3.2 col | 1.9 x 1.9 |
| 8 ft / 2438 mm | 2020 mm | **252.5 mm** | 1.8 col | 6.7 rows | **1.0 row** | 2.0 col | 1.2 x 1.2 |
| 10 ft / 3048 mm | 2525 mm | **315.6 mm** | 1.4 col | 5.4 rows | **0.8 row** | 1.6 col | **0.95 x 0.95** |

### 7.2 VL53L5CX / VL53L8CX at 4x4 (the mode you must use for 30–60 Hz)

| Range | Zone size | Human torso | Cat height | Box 300 mm |
|---|---|---|---|---|
| 1 ft / 305 mm | 63.1 mm | 7.1 col | 4.0 rows | 4.8 x 4.8 |
| 3 ft / 914 mm | 189.4 mm | 2.4 col | 1.3 rows | 1.6 x 1.6 |
| 5 ft / 1524 mm | 315.6 mm | 1.4 col | **0.8 row** | **0.95 x 0.95** |
| 8 ft / 2438 mm | 505.0 mm | **0.9 col** | **0.5 row** | **0.6 x 0.6** |
| 10 ft / 3048 mm | 631.3 mm | **0.7 col** | **0.4 row** | **0.5 x 0.5** |

### 7.3 VL53L7CX / VL53L7CH — 60 x 60 deg, 8x8

| Range | FoV width | Zone size | Human torso | Cat height | Cat length | Box 300 mm |
|---|---|---|---|---|---|---|
| 1 ft / 305 mm | 352 mm | **44.0 mm** | 10.2 col | 5.7 rows | 11.4 col | 6.8 x 6.8 |
| 3 ft / 914 mm | 1056 mm | **132.0 mm** | 3.4 col | 1.9 rows | 3.8 col | 2.3 x 2.3 |
| 5 ft / 1524 mm | 1760 mm | **220.0 mm** | 2.0 col | 1.1 rows | 2.3 col | 1.4 x 1.4 |
| 8 ft / 2438 mm | 2816 mm | **352.0 mm** | 1.3 col | **0.7 row** | 1.4 col | **0.85 x 0.85** |
| 10 ft / 3048 mm | 3520 mm | **440.0 mm** | **1.0 col** | **0.6 row** | 1.1 col | **0.7 x 0.7** |

### 7.4 VL53L9CX — 55 x 42 deg, 54 x 42

| Range | Zone size (H x V) | Human torso | Human height | Cat height | Box 300 mm |
|---|---|---|---|---|---|
| 1 ft / 305 mm | 5.9 x 5.6 mm | 77 col | 305 rows | 45 rows | 51 x 54 |
| 3 ft / 914 mm | 17.6 x 16.7 mm | 26 col | 102 rows | 15 rows | 17 x 18 |
| 5 ft / 1524 mm | 29.4 x 27.9 mm | 15 col | 61 rows | 9 rows | 10 x 11 |
| 8 ft / 2438 mm | 47.0 x 44.6 mm | 10 col | 38 rows | 6 rows | 6 x 7 |
| 10 ft / 3048 mm | 58.8 x 55.7 mm | 8 col | 31 rows | **4.5 rows** | 5 x 5 |

At 10 ft a cat is still 4.5 x 8 zones on a VL53L9CX versus 0.8 x 1.6 zones on a VL53L8CX. That is
the whole argument for the L9CX, in one line.

---

## 8. Mounting geometry on a 350 mm robot

### 8.1 Row elevations of an 8x8 at 45 deg V

Row centre elevations, computed with tangent-linear boundaries:

| Row (0 = bottom) | 0 | 1 | 2 | 3 | 4 | 5 | 6 | 7 |
|---|---|---|---|---|---|---|---|---|
| Centre elevation | -19.9 deg | -14.5 deg | -8.8 deg | -3.0 deg | +3.0 deg | +8.8 deg | +14.5 deg | +19.9 deg |

### 8.2 Floor intersection versus mounting height (45 deg V, axis horizontal)

| Sensor height | Row 0 floor hit (slant) | Row 1 | Row 2 | Row 3 | FoV ceiling at 1.5 m | at 3.0 m |
|---|---|---|---|---|---|---|
| 150 mm | 440 mm | 599 mm | 977 mm | 2901 mm | 771 mm | 1393 mm |
| 200 mm | 587 mm | 798 mm | 1303 mm | 3868 mm | 821 mm | 1443 mm |
| 300 mm | 880 mm | 1197 mm | 1955 mm | 5802 mm | 921 mm | 1543 mm |
| 400 mm | 1174 mm | 1596 mm | 2606 mm | 7736 mm | 1021 mm | 1643 mm |
| 900 mm | 2641 mm | 3591 mm | 5864 mm | 17406 mm | 1521 mm | 2143 mm |

Read this table as the real design constraint. **With a ring at 300 mm and the axes horizontal, the
top of the field of view at 1.5 m is only 921 mm above the floor.** A standing adult's head, chest
and shoulders are outside the frame at every useful range. The sensor sees knees and hips. You
cannot measure "how tall is it" from a low ring, so the obvious human/pet discriminator is
unavailable.

Rows 0–2 give a stable **floor baseline** at 0.88 / 1.20 / 1.96 m slant range (h = 300 mm). Anything
that returns *shorter* than the baseline in those rows is an obstacle standing on the floor;
anything *longer* or invalid is a cliff or a step down. That is free, robust, and worth building.

### 8.3 The ring parallax problem — how many sensors actually close the seam

Sensors sit on the body surface, not at the robot's centre. Model the body as a circle of radius
R = 175 mm with N sensors spaced evenly, each facing radially. Adjacent field-of-view edges do not
meet at the body; they meet at a range that depends on N. Computed by ray intersection:

| Sensor | FoV H | N sensors | Angular spacing | Seam closes at (from robot centre) | Blind slot near the body |
|---|---|---|---|---|---|
| VL53L8CX | 45 deg | 8 | 45.0 deg | **never** (edges parallel) | permanent 134 mm slot |
| VL53L8CX | 45 deg | 10 | 36.0 deg | 853 mm | 678 mm deep |
| VL53L8CX | 45 deg | 12 | 30.0 deg | 513 mm | 338 mm deep |
| VL53L8CX | 45 deg | 16 | 22.5 deg | 343 mm | 168 mm deep |
| VL53L7CX | 60 deg | 6 | 60.0 deg | **never** (edges parallel) | permanent 175 mm slot |
| VL53L7CX | 60 deg | 7 | 51.4 deg | 1171 mm | 996 mm deep |
| VL53L7CX | 60 deg | 8 | 45.0 deg | 670 mm | 495 mm deep |
| VL53L7CX | 60 deg | 10 | 36.0 deg | **421 mm** | **246 mm deep** |

**The naive arithmetic "360 / 45 = 8 sensors" and "360 / 60 = 6 sensors" is wrong.** At exactly
FoV-equals-spacing the adjacent edge rays are *parallel* and the blind wedge never closes — it is a
constant-width slot running to infinity. For real coverage you need angular overlap. Toeing the
sensors outward by a few degrees each shortens the closure distance substantially; that is the
cheapest fix if the mechanical design allows it.

**Confidence: calculated** (from datasheet FoV figures and stated body radius). Verify on the real
chassis with a target sweep before committing to a count.

---

## 9. What a human and a pet actually look like — and whether the grid can classify

### 9.1 The three ranges that matter

**At 1 ft (305 mm).** A cat, a human leg, a box and a wall all fill the entire 8x8 frame. Zone size
is 31.6 mm. There is no silhouette, only a distance field. Classification is impossible; this range
is for emergency stop only.

**At 3–5 ft (0.9–1.5 m).** This is the working envelope and the *only* range at which both
range performance and angular resolution are simultaneously adequate. A human torso is 3–5 columns;
a cat is 2.6 down to 1.6 rows tall and 3–5 columns long. The shapes are different — a cat is a wide,
low, horizontally elongated blob whose top edge is 1–3 rows above the floor line; a human is a
vertically saturated blob that runs off the top of the frame. **That top-of-frame saturation is
itself the most reliable cue available from a low-mounted CX sensor:** if the return blob touches
row 7, it is taller than the field of view, which at 1.5 m and h = 300 mm means taller than 921 mm,
which means not a cat.

**At 8–10 ft (2.4–3.0 m).** A cat is **one zone**, sometimes less. One zone has no shape. Worse,
these ranges are outside the sensor's specification in any lit room: at 8x8/15 Hz, 17% target,
5 kLux, the VL53L8CX is a 0.95–1.15 m sensor. **A cat at 8 ft in a daylit room does not appear at
all.** The correct statement to the operator is not "one zone at 8 ft" but "no detection at 8 ft in
daylight; one zone at 8 ft in a dark room".

### 9.2 Can the grid silhouette alone classify human vs pet vs box?

**No.** Four independent reasons, each sufficient:

1. **Vertical truncation.** From any ring height a 350 mm robot can carry (150–400 mm), a standing
   human's head is outside the 45 deg vertical field at every range inside 3 m. Height, the single
   most discriminative feature, is not measurable — only "taller than the frame" is.
2. **Angular starvation at range.** A pet is 1–2 zones beyond 2.4 m. Two zones cannot carry shape.
3. **Reflectance/range confound.** The sensor reports an absolute distance regardless of target
   colour, but *whether it reports at all* depends strongly on reflectance and ambient light. A
   black cat and no cat look the same in a lit room at 2 m. Absence of return is not absence of
   target.
4. **Static ambiguity.** A sleeping cat, a backpack and a cardboard box on the floor produce the
   same 2 x 3 zone blob. Nothing in the grid separates them.

### 9.3 What does work — in priority order

**1. Height above a calibrated floor plane (strongest geometric feature).** Convert every valid zone
to a 3D point using known azimuth/elevation and measured slant range, subtract the extrinsically
calibrated floor plane, cluster, and take the cluster's maximum height. Thresholds: pet if max
height < 450 mm; human if > 900 mm; ambiguous between. This *requires* the target's top to be inside
the FoV, which in turn requires either a high ring (about 900 mm — the table in 8.2 shows FoV ceiling
1521 mm at 1.5 m range, enough for a seated adult and most of a standing one) or a low ring tilted
upward by 10–15 degrees, or two rings.

**2. Per-zone motion indicator (strongest liveness feature, and it is free).** Every CX and CH part
in this family has an embedded firmware motion indicator computed between sequential frames,
reported per zone, initialised with `vl53l5cx_motion_indicator_init()`. A box has motion ≈ 0 at all
times. A human or pet does not — even a standing person breathes and sways. Combined with autonomous
ranging mode and detection thresholds programmed *on the motion value*, this gives a sub-10 mW
"something alive is in this sector" wake-up. This is the correct primitive for
animate-versus-inanimate, and it costs nothing.

**3. Temporal cadence.** A walking human's leg zones oscillate at roughly 1.8–2.2 Hz; a trotting cat
or small dog at roughly 3–5 Hz. Extracting this needs ≥15 Hz sampling, which means 8x8 at 15 Hz
(exactly at the limit) or 4x4 at 30–60 Hz (better temporally, useless spatially). Treat cadence as a
confirmation signal, not a primary classifier. **Confidence: inferred** — ST publishes no gait data.

**4. CNH histogram shape (strongest material/shape feature).** See section 5.3. Per-zone depth spread
at 37.5 mm resolution separates flat rigid surfaces (1–2 bins) from curved furry bodies (≈7 bins)
from clothing. This is the only thing in the family that can say "box" rather than "not moving".

### 9.4 Recommended classifier

```
for each zone with a valid target status:
    p = to_3d(azimuth, elevation, distance_mm)          # extrinsics per sensor
    h = height_above_floor_plane(p)                     # calibrated once, on level ground
cluster points by (azimuth, range) adjacency
for each cluster:
    max_h      = max height of cluster
    footprint  = angular width * range
    motion     = max per-zone motion indicator in the cluster
    touches_row7 = any zone in top row

    if motion < static_threshold and max_h < 500 mm:            -> INANIMATE (box, bag, chair leg)
    elif max_h > 900 mm or touches_row7:                        -> HUMAN
    elif 120 mm < max_h < 500 mm and motion > static_threshold: -> PET
    else:                                                        -> UNKNOWN OBSTACLE (stop anyway)
```

Everything outside the HUMAN/PET branches still generates an obstacle, because obstacle avoidance
must never depend on classification succeeding.

---

## 10. Integration facts you need before committing

### 10.1 Firmware upload and host memory

- `vl53l5cx_init()` *"copies the firmware (~84 kbytes) to the module by loading the code over the
  I2C interface and performing a boot routine"* (UM2884 Rev 2). SparkFun's product page states the
  practical requirement as *"approximately 90KB of firmware over I2C at power-on"*.
- The firmware image lives in host **flash** as a `const` array. **One copy serves all sensors of
  the same part number** — ten VL53L8CX cost one 84 kB image, not ten.
- Upload time: 84 kB ≈ 688 kbit; at 1 MHz I2C with protocol overhead this is roughly **0.8–1.0 s per
  sensor**. Ten sensors uploaded sequentially is an **8–10 second boot**. Use SPI (20 MHz on the
  L8CX) or parallel buses if that matters. **Confidence: calculated.**
- 8-bit MCUs are out. Both Pololu and SparkFun state this explicitly: an Arduino Uno cannot run
  these parts.

### 10.2 RAM per frame, and I2C bandwidth — the real ceiling on ring size

From the ULD header (`VL53L8CX_ResultsData`, stm32duino/VL53L8CX), with
`VL53L8CX_NB_TARGET_PER_ZONE = 1` and all outputs enabled:

| Field | Bytes |
|---|---|
| `silicon_temp_degc` | 1 |
| `ambient_per_spad[64]` (uint32) | 256 |
| `nb_target_detected[64]` (uint8) | 64 |
| `nb_spads_enabled[64]` (uint32) | 256 |
| `signal_per_spad[64]` (uint32) | 256 |
| `range_sigma_mm[64]` (uint16) | 128 |
| `distance_mm[64]` (int16) | 128 |
| `reflectance[64]` (uint8) | 64 |
| `target_status[64]` (uint8) | 64 |
| `motion_indicator` (2x uint32, 4x uint8, uint32[32]) | 140 |
| **Total** | **1357** |

Disabling `AMBIENT_PER_SPAD`, `NB_SPADS_ENABLED`, `SIGNAL_PER_SPAD`, `RANGE_SIGMA_MM` and
`REFLECTANCE_PERCENT` via the `platform.h` macros (ST recommends always keeping
`nb_target_detected` and `target_status`) brings a frame to **397 bytes**.

At 1 MHz I2C, 9 bits per byte including ACK:

| Configuration | Bytes/frame | Bus time/frame | Sensors supportable at 15 Hz (80% bus) |
|---|---|---|---|
| Full output, 1 target/zone | 1357 | ≈12.2 ms | **4** |
| Minimal output (distance + status + nb_target + motion) | 397 | ≈3.6 ms | **14** |
| VL53L8CH, 64 zones x 18 bins CNH | 6108 | 56 ms (ST's own figure) | **1** |

**Confidence: calculated** from the datasheet/header figures, except the CNH row which is ST's
published number. This table, more than anything else, sets the architecture: **run the ring in
minimal-output mode on a dedicated fast bus, and put CNH on exactly one sensor.** Raising
`NB_TARGET_PER_ZONE` to 4 multiplies the per-target arrays by four and pushes the full-output frame
past 2.8 kB.

### 10.3 I2C addressing for a ring

- Default address **0x52** (8-bit form; 0x29 in 7-bit form) on every part in this family.
- Address change procedure (UM2884), verbatim in substance: pull down the `LPn` pin of every device
  *except* the one being reprogrammed, call `vl53l5cx_set_i2c_address()`, then raise the `LPn` pins
  again, repeating per device.
- **The new address is volatile.** It must be re-applied after every power cycle.
- **Consequence:** you need one host GPIO per sensor for `LPn`. Ten sensors means ten GPIOs or an
  I2C I/O expander — and the expander must be at a fixed address that does not collide during the
  enumeration dance. Budget this in the schematic; it is the most common integration surprise with
  this family.

### 10.4 Resolution and frame rate limits (UM2884 Table 2)

| Resolution | Min ranging frequency | Max ranging frequency |
|---|---|---|
| 4x4 (16 zones) | 1 Hz | **60 Hz** |
| 8x8 (64 zones) | 1 Hz | **15 Hz** |

Default resolution is 4x4; default ranging frequency is 1 Hz. You must set resolution *before*
frequency, because the legal frequency range depends on it.

### 10.5 Other ULD features worth knowing

- **Multi-target per zone:** *"The VL53L5CX can measure up to four targets per zone."* Set
  `VL53L5CX_NB_TARGET_PER_ZONE` (1–4) in `platform.h`, not through the driver. Default is 1. More
  targets means more RAM and more bus traffic.
- **Target order:** `Closest` or `Strongest`. Default is **Strongest** — which for a robot is the
  wrong default. A dark obstacle at 400 mm in front of a white wall at 2 m will report the *wall*
  unless you call `vl53l5cx_set_target_order()` to `Closest`, or read multiple targets.
- **Sharpener:** `vl53l5cx_set_sharpener_percent()`, 0–99%, default 5% in the ULD (the datasheet FoV
  characterisation used 14%). Sharpener removes veiling-glare bleed of a near bright target into
  adjacent zones. For pet detection against a bright floor, tune this deliberately.
- **Cover-glass crosstalk:** ST's histogram algorithms give crosstalk immunity *"above 60 cm"*;
  below 60 cm crosstalk can exceed the correction. Run the Xtalk calibration plugin if you put the
  sensors behind a bezel.
- **Interrupt:** GPIO1 / pin A3, auto-cleared after ~100 µs. Works in both continuous and autonomous
  modes.

### 10.6 Driver support

| Platform | Support | Notes |
|---|---|---|
| ST ULD API (bare C) | VL53L5CX (UM2884), VL53L7CX, VL53L8CX (UM3109), VL53L8CH (UM3183) | Reference implementation, BSD-3 |
| STM32Cube | `STMicroelectronics/x-cube-tof1` | Last updated 2025-04-03 |
| Arduino | `stm32duino/VL53L8CX` (2026-07-01), `VL53L8CH` (2025-11-28), `VL53L7CX` (2025-05-09), `VL53L7CH` (2024-07-24), `VL53L5CX` (2023-08-23) | All BSD-3-Clause |
| CircuitPython | `sensebox/CircuitPython_VL53LxCX` — *"CircuitPython driver for VL53L5CX and VL53L8CX ToF sensors"*, updated 2025-09-19 | Community, 5 stars. **No official Adafruit driver.** |
| ESP-IDF | `RJRP44/VL53L8CX-Library` | Community, 11 stars |
| Linux | ST publishes a kernel/user driver for this family; no mainline IIO driver confirmed | **Confidence: unverified** |
| VL53L9CX | **Nothing.** No `stm32duino` repository, no Arduino library, no CircuitPython driver. | MIPI CSI-2 means a V4L2 SoC driver, not an MCU library |

Note the maintenance signal in those dates: the **VL53L8CX** library is the actively maintained one
(July 2026). The VL53L5CX library has not been touched since August 2023.

---

## 11. Where to buy, and what it costs (prices read 2026-09-12)

| Product | Vendor | Part / SKU | Price USD | Stock |
|---|---|---|---|---|
| VL53L5CX carrier w/ regulator, 400 cm | Pololu | #3417 | **$19.95** (qty 100: $15.53) | Active and Preferred |
| VL53L7CX carrier w/ regulator, 350 cm | Pololu | #3418 | **$19.95** | Active and Preferred |
| VL53L8CX carrier w/ regulators, 400 cm | Pololu | #3419 | **$24.95** (qty 100: $19.43) | Active and Preferred |
| Qwiic ToF Imager VL53L5CX | SparkFun | SEN-18642 | **$32.50** | **Backorder** (not in stock 2026-09-12) |
| Qwiic Mini ToF Imager VL53L5CX | SparkFun | SEN-19013 | **$25.95** | In stock (10+ $24.65, 25+ $23.36, 100+ $22.06) |
| SATEL-VL53L8 breakout | DigiKey | 497-SATEL-VL53L8-ND | **$32.95** | 190 in stock, 13 wk lead, Active |
| VL53L5CX-SATEL breakout | DigiKey | 497-VL53L5CX-SATEL-ND | **$22.70** | 437 in stock, **51 wk lead**, Active |
| X-NUCLEO-53L8A1 (VL53L8CA) | DigiKey | 497-X-NUCLEO-53L8A1-ND | **$38.24** | 40 in stock, 4 wk lead, Active |
| P-NUCLEO-53L8A1 | DigiKey | — | **$66.13** | listed |
| VL53L8CX bare chip | DigiKey | VL53L8CXV9GC/1 / VL53L8CXV0GC/1 | **$8.56 / $8.77** | listed |
| VL53L7CX bare chip | DigiKey | VL53L7CXV0GC/1 | **$8.80** | listed |
| X-NUCLEO-53L9A1 | DigiKey | 497-X-NUCLEO-53L9A1-ND | **$96.44** | **0 in stock, no ETA given**, 4 wk lead |
| STEVAL-VL53L9 (VL53L9CX eval) | DigiKey | 29294599 | **$80.39** | **0 in stock, 1 due 2026-10-28** |
| STEVAL-VL53L9 | ST (via CNX) | — | $75 | MP from early July 2026 |

**Adafruit does not stock any of the multizone grid parts.** A search of adafruit.com for VL53L5CX /
VL53L7CX / VL53L8CX on 2026-09-12 returns only the single-zone and multi-target-single-zone parts:
VL53L0X (#3317, $14.95), VL53L1X (#3967, $14.95), VL53L4CD (#5396, $14.95), VL53L4CX (#5425,
$14.95), VL6180X (#3316, $13.95). If you want a grid sensor on a breakout, the vendors are Pololu,
SparkFun, ST's own SATEL boards and the distributors.

**No part in this family is discontinued or NRND.** Every CX and CH part checked on 2026-09-12 shows
DigiKey status *Active*, and Pololu #3417 / #3418 / #3419 all show *Active and Preferred*. But
"active" is not "buyable now", and three listings need care:

- **SparkFun SEN-18642 is on backorder**, not in stock. Use SEN-19013 ($25.95, in stock) or a
  Pololu carrier if you need VL53L5CX breakouts this week.
- **VL53L5CX-SATEL carries a 51-week factory lead time** behind its 437 units of stock. Once that
  437 is gone it is effectively a year out. SATEL-VL53L8 is better placed at 13 weeks.
- **Both VL53L9CX boards are at 0 stock** (see section 6).

### 11.1 Ring BOM comparison

| Configuration | Coverage | Unit cost | Ring cost | Range in 5 kLux (17% target, 8x8) |
|---|---|---|---|---|
| 10 x Pololu #3418 (VL53L7CX) | 360 deg, seam closes 421 mm | $19.95 | **$199.50** | 250–350 mm |
| 12 x Pololu #3419 (VL53L8CX) | 360 deg, seam closes 513 mm | $24.95 | **$299.40** | 950–1150 mm |
| 12 x SATEL-VL53L8 | same | $32.95 | $395.40 | 950–1150 mm |
| 12 x bare VL53L8CX + custom PCB | same | ~$8.70 + PCB | ~$105 + NRE | 950–1150 mm |
| 1 x STEVAL-VL53L9 (forward only) | 55 deg | $80.39 | $80.39 | not published |

---

## 12. Known weaknesses, stated plainly

- **Ambient light is the dominant failure mode.** Every number above is characterised at 0 and
  5 kLux only. 5 kLux is a bright room. **Direct sunlight is 100–120 kLux and ST publishes no figure
  for it.** Do not extrapolate. For an outdoor or conservatory-facing robot, treat this whole family
  as unspecified.
- **Dark targets collapse the range.** ST's "17% grey" is footnoted in the VL53L5CX datasheet as
  *"measured 13% in IR at 940 nm"*. Black clothing and dark fur are commonly below that. There is no
  published number for a 5% target; **not published**, and guessing is not acceptable here.
- **Glass and mirrors.** A 940 nm dToF sees straight through a window or a glass door and ranges to
  whatever is behind it. ST addresses *cover*-glass crosstalk (immunity above 60 cm) but says
  nothing about specular or transparent targets in the scene. A glass coffee table is invisible.
  **Not published.**
- **Multi-sensor mutual interference.** All units emit 940 nm with no documented coded modulation.
  The VL53L8CX has a `SYNC` pin (Table 15 lists "I2C, SPI, INT, and SYNC") intended for frame
  synchronisation, documented in UM3109, but **ST publishes no mutual-interference rejection figure
  for N co-located units**. The safe architecture is to round-robin or time-slice the ring so that
  sensors with overlapping fields never integrate simultaneously; opposite pairs can fire together
  because their fields do not overlap. With 12 sensors in 4 time slots at 15 Hz, the full-ring
  refresh is about 0.27 s. **Confidence: inferred.**
- **Corner zones are the weak zones, and the ring's seams are made of corner zones.** Range at the
  corners is up to 35% shorter than at the centre, and accuracy degrades up to 4%. The places where
  two sensors' fields meet are exactly where each sensor is worst.
- **8x8 tops out at 15 Hz.** For a robot moving at 0.5 m/s, a 15 Hz frame with a 56 ms transfer plus
  time-slicing means an obstacle can close 100–200 mm between frames. Size the stopping distance
  from the *ring* refresh rate, not the sensor's 60 Hz headline.

---

## 13. Recommendation for the 350 mm robot

**Build this:**

1. **Perimeter ring: 12 x VL53L8CX** (Pololu #3419 for prototyping, bare parts on a custom flex for
   production), mounted at **300 mm**, axes horizontal, spaced 30 degrees. Seam closes at 513 mm
   from centre; rows 0–2 give a floor baseline at 0.88 / 1.20 / 1.96 m. Run 8x8 at 15 Hz in
   minimal-output mode (distance, status, nb_target, motion), target order **Closest**, four
   interference time-slices. Ring cost about $300.
   *Why the L8CX and not the L7CX:* the L7CX's wider 60-degree field would cut the count to 10, but
   its 5 kLux range at 8x8 against a 17% target is **250–350 mm** against the L8CX's
   **950–1150 mm**. A ring you cannot use in a lit room is not a ring.
2. **Classification head: 1 x VL53L8CH** facing forward, at **900 mm**, at 64 zones x 18 bins,
   15 Hz, 6108 bytes per frame **on its own I2C bus**. At 900 mm the field ceiling is 1521 mm at
   1.5 m range, so a standing adult's torso is inside the frame and height-above-floor becomes a
   usable feature. The CNH histogram supplies the box-versus-body discrimination the CX grid cannot.
3. **Wake-up: the ring in autonomous mode at 1 Hz, 8x8, 6.7 mW per sensor**, with detection
   thresholds programmed on the **motion indicator**, while the robot is parked. Twelve sensors idle
   at about 80 mW total and wake the host on any animate presence in any sector.
4. **Do not buy the VL53L9CX yet** unless the robot already has a Linux SoC with a spare CSI-2 port
   and the schedule tolerates an October 2026 evaluation board. When it is available and driven, one
   forward-facing VL53L9CX replaces the classification head and a forward lidar outright: a cat at
   10 ft is 4.5 x 8 zones instead of 0.8 x 1.6.

**Do not rely on:** grid silhouette alone for classification; the "400 cm" headline for any dark
target in a lit room; eight sensors for 360-degree coverage; or any of these parts in direct
sunlight.

---

## Sources

- [VL53L8CX datasheet, DS14161 Rev 2, March 2023 (Farnell mirror)](https://www.farnell.com/datasheets/3930859.pdf) — read in full
- [VL53L5CX datasheet, DS13754 Rev 5, December 2021 (Pololu mirror)](https://www.pololu.com/file/0J1878/vl53l5cx.pdf) — read in full
- [VL53L7CX datasheet, DS13865 Rev 6 (MikroElektronika mirror)](https://download.mikroe.com/documents/datasheets/VL53L7CX_datasheet.pdf) — read in full
- [VL53L8CH datasheet, DS14310 Rev 3, August 2023 (MikroElektronika mirror)](https://download.mikroe.com/documents/datasheets/VL53L8CH_datasheet.pdf) — read in full
- [UM2884 Rev 2 — A guide to using the VL53L5CX multizone ToF ranging sensor with wide field of view ULD (Pololu mirror)](https://www.pololu.com/file/0J1885/um2884-a-guide-to-using-the-vl53l5cx-multizone-timeofflight-ranging-sensor-with-wide-field-of-view-ultra-lite-driver-uld-stmicroelectronics.pdf) — read in full
- [ST VL53L9CX product page](https://www.st.com/en/imaging-and-photonics-solutions/vl53l9cx.html)
- [ST VL53L9CX datasheet](https://www.st.com/resource/en/datasheet/vl53l9cx.pdf) — not retrievable from this host
- [ST press release announcing the VL53L9CX](https://newsroom.st.com/media-center/press-item.html/p4783.html)
- [CNX Software, 2026-06-22 — ST VL53L9CX dToF 3D LiDAR](https://www.cnx-software.com/2026/06/22/st-vl53l9cx-direct-time-of-flight-3d-lidar-supports-5cm-to-9m-range-2-3k-zones-resolution/)
- [DigiKey STEVAL-VL53L9](https://www.digikey.com/en/products/detail/stmicroelectronics/STEVAL-VL53L9/29294599)
- [DigiKey SATEL-VL53L8 search](https://www.digikey.com/en/products/result?keywords=SATEL-VL53L8)
- [DigiKey X-NUCLEO-53L8A1 search](https://www.digikey.com/en/products/result?keywords=X-NUCLEO-53L8A1)
- [DigiKey X-NUCLEO-53L9A1 search](https://www.digikey.com/en/products/result?keywords=X-NUCLEO-53L9A1) — $96.44, 0 in stock, no ETA
- [DigiKey VL53L5CX-SATEL search](https://www.digikey.com/en/products/result?keywords=VL53L5CX-SATEL) — $22.70, 437 in stock, 51 wk lead
- [VL53L8CX datasheet, DS14161 Rev 2 (Pololu resource link for #3419)](https://a.pololu-files.com/file/0J2029/vl53l8cx.pdf)
- [Pololu #3417 — VL53L5CX carrier](https://www.pololu.com/product/3417)
- [Pololu #3418 — VL53L7CX carrier](https://www.pololu.com/product/3418)
- [Pololu #3419 — VL53L8CX carrier](https://www.pololu.com/product/3419)
- [SparkFun SEN-18642 — Qwiic ToF Imager VL53L5CX](https://www.sparkfun.com/sparkfun-qwiic-tof-imager-vl53l5cx.html)
- [SparkFun SEN-19013 — Qwiic Mini ToF Imager VL53L5CX](https://www.sparkfun.com/sparkfun-qwiic-mini-tof-imager-vl53l5cx.html)
- [Adafruit search for VL53L5CX / VL53L7CX / VL53L8CX](https://www.adafruit.com/?q=VL53L5CX&post_type=product) — no matches
- [stm32duino GitHub organisation, VL53L libraries](https://github.com/stm32duino?q=VL53L&type=all)
- [stm32duino/VL53L8CX vl53l8cx_api.h](https://raw.githubusercontent.com/stm32duino/VL53L8CX/main/src/vl53l8cx_api.h)
- [ST Community — difference between the VL53L7 CH and CX variants](https://community.st.com/t5/imaging-sensors/difference-between-the-vl53l7-ch-and-cx-variants/td-p/845353)
- [ST Community — VL53L8CH raw data](https://community.st.com/t5/imaging-sensors/vl53l8ch-raw-data/td-p/677581)
