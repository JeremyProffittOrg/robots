# Safety and Failure Modes: Perimeter Sensing on a 350 mm Mobile Robot

**Lane:** safety-and-failure-modes
**Robot under study:** 350 mm square or 350 mm diameter round footprint, 600–1200 mm tall, 5–15 kg, indoor domestic/office, operating around humans and pets.
**Date of research:** 2026-09-12. All prices and page states read on that date.
**Confidence key:** `standard-verified` (quoted from the standard or an accredited body's published extract) · `datasheet-verified` (quoted from the silicon or product datasheet) · `vendor-page-verified` · `peer-reviewed-measured` (a published measurement study) · `inferred` (derived by me from verified inputs) · `unverified` (reported but not confirmed at a primary source).

---

## 1. Scope and the honest framing

Nothing in the parts list a hobbyist can buy is **safety-rated**. Not one. A VL53L5CX, an RPLIDAR C1, an LD2410, an MLX90640 and an HC-SR04 are all *sensors*, not *electro-sensitive protective equipment (ESPE)*. ESPE is a device certified under IEC 61496 with a proven failure behaviour, a declared response time, a declared minimum detectable object, and dual redundant outputs (OSSDs) that go safe on internal fault. A hobby sensor has none of that: it has one output, an undeclared failure mode, and a response time that varies with the target.

This document therefore does two things:

1. States what the professional standards require, at the level a hobbyist must understand to build something that is *actually* safe rather than *apparently* safe.
2. Catalogues every way each candidate modality fails, with the specific mitigation.

The governing design rule that falls out of all of it: **a single-modality perimeter system will eventually hit something.** Section 9 argues why, per modality.

---

## 2. The standards, and what they actually require

### 2.1 ISO 13482:2014 — Personal care robots

`standard-verified` (scope), `vendor-page-verified` (details)

ISO 13482:2014 *Robots and robotic devices — Safety requirements for personal care robots* is the closest existing standard to a domestic household robot. It covers three types: **mobile servant robot**, **physical assistant robot**, and **person carrier robot**. A 350 mm, 600–1200 mm tall household robot is a *mobile servant robot*.

The key honest admission attributed to the standard: *"for hazards related to impact (e.g. due to a collision) no exhaustive and internationally recognized data (e.g. pain or injury limits) exist at the time of publication of ISO 13482:2014."* `unverified` — **not** `standard-verified`. On 2026-09-12 this quotation could not be confirmed at any primary source: ISO 13482:2014 is paywalled, and both [iso.org/standard/53820.html](https://www.iso.org/standard/53820.html) and the ISO Online Browsing Platform return **HTTP 403** to an unauthenticated fetch. The phrase *"at the time of publication of ISO 13482:2014"* is itself a tell that the sentence has been relayed through a secondary source, since a standard refers to itself as "this document". See Section 10. The conclusion it supports still holds on its own: ISO 13482 **does not give you a number for how hard your robot may hit someone**. It gives you a process: hazard identification, risk estimation per ISO 12100, then protective measures — inherently safe design first, then safeguarding, then information for use.

Its concrete mechanisms that matter here: **safety-related control system** requirements, **software limits** on operating space, speed and force, and mandatory **protective stop** capability.

Status: ISO 13482 is under revision. `ISO/DIS 13482:2024 — Robotics — Safety requirements for service robots` and `ISO/FDIS 13482` are in the ISO pipeline ([ISO/FDIS 13482](https://www.iso.org/standard/83498.html)). Treat 2014 as current but expect the title to broaden from "personal care" to "service robots".

**What a hobbyist must take from it:** there is no published injury threshold you can design to. You must instead make impact energy small enough that the question does not arise, and you must be able to demonstrate a protective stop.

### 2.2 ISO 3691-4:2023 — Driverless industrial trucks

`standard-verified`

This is the standard with the actual numbers, and the one worth copying. ISO 3691-4:2023 (second edition, 2023-06) is a **Type C** standard aligned with ISO 13849. Its clause structure, read from the standard's own published table of contents ([ISO 3691-4:2023 preview](https://cdn.standards.iteh.ai/samples/83545/a3d9d057a08d4f9c8e8e87cdc947583c/ISO-3691-4-2023.pdf)):

| Clause | Title | Why it matters here |
|---|---|---|
| 4.1.10 | Electro-sensitive protective equipment | The sensor must be ESPE, not a hobby module |
| 4.1.26 / 4.1.27 | Normal stop / Operational stop | New definition in the 2023 edition |
| 4.2 | Braking system | Brake is part of the safety function, not an afterthought |
| 4.3.1 / 4.3.2 | Overspeed detection / Speed and stability | Speed itself is a safety-rated quantity |
| 4.8.1 | Emergency stop | |
| **4.8.2** | **Detection of persons in the path** | The core requirement |
| 4.11 | Safety-related parts of the control system | 27 declared safety functions, each with a required PL |
| 4.12 | Electromagnetic immunity | |

The requirement in 4.8.2 is quoted by TÜV Rheinland as: *"They shall be so designed that trucks shall stop before contact between the rigid parts of the truck or load and a stationary person…"* ([TÜV Rheinland ISO 3691-4 whitepaper](https://www.tuv.com/content-media-files/master-content/services/industrial-services/pdf/tuv-rheinland-automatic-guided-vehicles-whitepaper-en_neu.pdf))

TÜV highlight this as the major change from the superseded EN 1525:1997: EN 1525 said the detection system shall *"generate a signal enabling the truck to be stopped"*; ISO 3691-4 says the truck shall **stop**. The difference moves the whole braking chain inside the safety function.

**Required Performance Level (PL):** *"The standard clarifies that the SRP/CS of the Detection of Personnel and the Braking System have to comply with a level of PLr d."* `standard-verified` via TÜV. PL d under ISO 13849-1 implies, in practice, a Category 3 architecture: redundancy, cross-monitoring, and a single fault must not lose the safety function.

**Speed numbers from Annex A Table A.1**, as reproduced by TÜV. Column names and cell values below are transcribed verbatim from the TÜV "EXTRACT OF TABLE A.1" figure:

| Condition | Clearance C1 / C2 / C3 | Personnel detection | Max speed | Required zone classification | Reachable stop function required within 600 mm | Floor/ground marking or extra warnings required | Auto restart permitted |
|---|---|---|---|---|---|---|---|
| 1a | > 500 mm all round | **Active (PL d)** | **Rated speed** | Operating | NO | NO | NO |
| 1b | > 500 mm all round | **Muted** | **0,3 m/s** | Operating hazard | NO | **YES** | Conditional (note b) |

Note b, verbatim: *"In these specific cases, automatic restart is permitted without personnel detection means if side clearance is >500 mm on at least one side or clearance is >500 mm from the current position to the fixed closed structure/object in the direction of travel if determined to be acceptable by a risk assessment."*

`standard-verified` **against the 2020 first edition** — see the edition caveat below. The number to keep: **0,3 m/s is the speed the industrial world considers acceptable when personnel detection is muted**, and in that same row the standard requires **floor/ground marking or extra warnings**, which an earlier revision of this document omitted.

> **Correction (2026-09-12 adversarial check) — the 600 mm figure was mis-stated.** An earlier revision said *"600 mm is the maximum reach to an emergency stop device when a personnel-detection function cannot be implemented."* No verified source supports that framing. In TÜV's Table A.1 extract, "Reachable stop function required within 600 mm" is a **per-zone column**, and for **both** rows reproduced here — 1a (detection active) and 1b (detection muted) — the value is **NO**. The 600 mm requirement therefore attaches to *other* zone classifications not shown in the free extract, not to a "detection cannot be implemented" fallback. Treat 600 mm as **an unverified reading of a paywalled clause**, not as a design rule.

> **Edition caveat (2026-09-12 adversarial check).** The TÜV whitepaper this section relies on is titled *"ISO 3691-4:2020 — A Standard for Automated Guided Vehicles"*. Table A.1, the 27 safety functions, the PLr d statement and the climatic conditions below are therefore verified against the **2020 first edition**, not the **2023 second edition** named in this section's heading. Only the clause numbering (4.1.2 Normal climatic conditions, 4.2 Braking system, 4.3.1/4.3.2, 4.8.1 Emergency stop, 4.8.2 Detection of persons in the path, 4.11 Safety-related parts of the control system, 4.12 Electromagnetic immunity) is verified against the 2023 edition's own published contents page. The free 2023 preview stops at the end of Clause 3 (Terms and definitions), so no Clause 4 or Annex A value in this document has been read at the 2023 text.

Normal climatic conditions declared by the standard, quoted verbatim from TÜV: *"Avg. ambient temperature continuous duty: +25 °C · Max. ambient temperature, short term (up to 1h): +40 °C · Lowest ambient temperature, normal use indoor: +5 °C · Lowest ambient temperature, normal use outdoor: −20 °C · Altitude: 2,000 m"*. `standard-verified` (2020 edition). Note how narrow that is — the thermal-sensor failure in Section 6.3 lives exactly at the +40 °C end.

### 2.3 ANSI/RIA (now ANSI/A3) R15.08 — Industrial mobile robots

`vendor-page-verified`

- **R15.08-1-2020** — Part 1: requirements for the IMR (the vehicle itself).
- **ANSI/A3 R15.08-2-2023** — Part 2: requirements for the IMR **system(s)** and IMR **application(s)** (integration).
- **Part 3** — requirements for IMR **users**, in preparation.

([ANSI webstore R15.08-2](https://webstore.ansi.org/standards/ria/ansia3r15082023), [R15.08-1](https://webstore.ansi.org/standards/ria/ansiriar15082020))

R15.08 is the North American analogue of ISO 3691-4 and adds an explicit distinction between an **AGV** (follows a fixed physical or virtual guide path, stops at obstacles) and an **AMR** (dynamically generates paths from the current environment) ([The Robot Report](https://www.therobotreport.com/ansi-ria-r15-08-standard-redefines-industrial-mobile-robots-whats-new-and-why-it-matters/)). A household robot is an AMR. R15.08 uses a four-tier severity classification S1–S4 combined with exposure and avoidance scoring. Specific numeric zone and stopping-distance values are behind the paywall — **not published** in any free source I could verify.

### 2.4 IEC 61496 — Electro-sensitive protective equipment, and the protective/warning field distinction

`vendor-page-verified`

IEC 61496 is the product standard for the *sensor as a safety device*. Types:

| Type | Principle | Typical device |
|---|---|---|
| Type 2, Type 4 | Interruption of a beam between a separate transmitter and receiver | Safety light curtain |
| **Type 3** | **Detection by reflection of the emitted light** | **Safety laser scanner** |

A Type 3 device must additionally meet requirements for **minimum detectable target reflectance of 1.8 %**, ambient-light immunity, and resistance to the effects of dirt, background and obstruction. `datasheet-verified` at a certified product: the Keyence SZ-V series, declared to *"IEC61496-1, EN61496-1, UL61496-1 (Type 3 ESPE)"* and *"IEC61496-3, EN61496-3 (Type 3 AOPDDR)"*, specifies its minimum detectable object as *"Diameter 20, 30, 40, 50, 70, 150 mm (depends on the setting) **Reflectance 1.8 % min.**"* ([Keyence SZ-V specifications](https://www.keyence.com/products/safety/laser-scanner/sz-v/specs/)). SICK's ESPE whitepaper independently confirms the device class: *"For AOPDDR the Type 3 is defined"*, and that requirements covering *"optical sources of interference (sunlight, different lamp types, devices of the same design, etc.), reflective surfaces, misalignment during normal operation and the diffuse reflection of safety laser scanners play an important role"* ([SICK ESPE whitepaper](https://www.sick.com/media/docs/7/57/057/whitepaper_electro_sensitive_protective_devices_espe_for_safe_machines_en_im0062057.pdf)).

> **Correction (2026-09-12 adversarial check).** An earlier revision of this document cited [Hokuyo's IEC 61496 page](https://www.hokuyo-aut.jp/products/data.php?id=112) for the 1.8 % figure. That page was re-read on 2026-09-12 and contains **no** reflectance, ambient-light, dirt or background figure at all — it only distinguishes the types by detection principle. The citation has been replaced with a certified product's own declared specification.

> **The condition that makes 1.8 % meaningful, and that was missing before:** 1.8 % is the **protective-zone** figure. The same Keyence specification states that *"20 % or more reflectance is necessary for the minimum detectable object in the **warning zone**"* — an order of magnitude more light. So a certified scanner detects a black sock **inside the protective field but not reliably inside the warning field**. Quoting 1.8 % without that split overstates what the warning field in Section 2.4 and Section 3.5 actually buys you: the slow-down tier degrades on dark targets even on certified hardware.

That 1.8 % protective-zone figure is still the single most important number in this document, because it is the pass mark that a certified scanner must hit and a hobby sensor does not: **it is the reason a certified scanner sees a black sock in its protective field and a VL53L5CX does not.**

**Protective field vs warning field.** These are two independently configured polygons around the robot:

- **Warning field** (outer): an intrusion triggers a *non-safety* reaction — slow down, sound a horn, light a beacon. It buys time and reduces nuisance stops. On the Banner AG4 the warning-field intrusion drives an *alarm output*, not the OSSDs.
- **Protective field** (inner): an intrusion triggers the safety outputs and stops the machine within the declared response time. The field shape may be irregular — L-shaped, notched, curved to the hazard boundary.

([Banner AG4 Application Guide P/N 147900](https://info.bannerengineering.com/cs/groups/public/documents/literature/147900.pdf))

### 2.5 Speed-and-separation monitoring (SSM)

`inferred` from `standard-verified` inputs

SSM is the principle that the robot maintains at least a **protective separation distance** from a person at all times, and that distance is recomputed continuously from robot speed, human speed, robot stopping distance, sensor measurement uncertainty, system latency and control frequency. On a mobile robot SSM collapses into a simple rule: *the protective field must be at least as long as the stopping distance, and the field must grow with speed.*

The industrial implementation is **field-pair switchover**: a certified scanner stores up to 32 field sets and the vehicle's speed input selects which pair is live. Banner's AG4 guide states the AGV's maximum speed must be declared in the scanner configuration — for a 1200 mm/s vehicle the "up to 1500 mm/s" option is chosen — and that when field-pair switchover is used, *"the Minimum Distance D and Side Distance Z (Protective Field length and width) must be calculated individually for all Protective Field pairs."* `datasheet-verified`.

**The hobbyist version of SSM:** implement at least three speed tiers, each with its own protective and warning polygon, and *derive* the polygons from the arithmetic in Section 3 rather than guessing.

---

## 3. Stopping-distance arithmetic — the real numbers

This is the part that must not be hand-waved. All arithmetic below was computed with Python and is pasted verbatim.

### 3.1 The formula

The ISO 3691-4 / Banner AG4 form for a mobile vehicle's **protective field length** is:

```
D_SD = v × (t_sensor + t_control) + d_brake
PF   = D_SD + Z_SM + Z_refl + Z_F + Z_A
```

Banner's own worked AGV example (Example #6) gives the Z terms real values `datasheet-verified`:

> *Protective Field Length (Minimum Distance D): For this example, assume a maximum vehicle speed of 1200 mm/s (48"/s), a breaking distance of 900 mm (35"), Scanner response time of 160 ms, the response time of a vehicle drive and safety interfacing 100 ms, which results in an overall stopping distance of 1212 mm (48").*
> *DSD = [1200 mm/s x (0.1s + 0.16s)] + 900 mm.*
> *ZSM = 83 mm (3.3") The farthest point of the Protective Field from the Scanner along a radial is less than 3500 mm (138").*
> *Zrefl = 0 The possibility of retro-reflectors located within the scanning plane of the Protective Field can be excluded.*
> *ZF = 100 mm (4") … The ground clearance of the transfer cart's sides is 60 mm (2.4") and the wheels are not accessible.*
> *ZA = 500 mm (20") … crushing/trapping hazard … The total Protective Field length (Minimum Distance) from the Scanner to the leading edge of the Protective Field is 1895 mm (75").*

Every figure in that block — 1200 mm/s, 900 mm, 160 ms, 100 ms, 1212 mm, ZSM 83 mm, Zrefl 0, ZF 100 mm, ZA 500 mm, 1895 mm — was re-read from the AG4 guide PDF on 2026-09-12 and is correct as quoted. `datasheet-verified`.

> **Source-vintage caveat (2026-09-12 adversarial check).** The AG4 Applications Guide is **P/N 147900 rev. A, dated 03/2010**, and it is written against the *superseded* AGV standard: it requires, verbatim, that *"Automatic start and restart (automatic reset) function must incorporate a two-second delay after the Protective Field becomes clear (**per BS/DIN EN 1525**)."* EN 1525:1997 is exactly the standard ISO 3691-4 replaced, and Section 2.2 of this document uses that replacement as its main argument. The Z-factor *method* (Z_SM, Z_refl, Z_F, Z_A) is still the right discipline to copy, but do not treat this 2010 document as evidence of any current ISO 3691-4 requirement, and note that Example #6 guards a **rail-guided transfer cart inside fencing**, not a free-roaming AMR.

Also from the same document, and directly applicable to a small robot: the AGV application uses **70 mm resolution**; the scanner is mounted **150 mm above the floor**; and *"the plane of the Protective Field should not exceed 200 mm (7.9") above the floor."* `datasheet-verified`. Torso detection on a vertical field uses **150 mm resolution**; hand detection uses **30 mm**; leg detection in a horizontal stationary field uses **50 mm**.

### 3.2 The robot's own deceleration ceiling — it tips before it slides

A 350 mm footprint gives 175 mm from centre to leading edge. A 600–1200 mm tall robot has a high centre of gravity. Braking hard enough pitches it onto its face.

```
====================================================================================================
PART 1 -- pure robot stopping distance (target stationary), no human approach term
====================================================================================================
  tip-over decel limit, low CG 300 mm, 350 mm footprint: a_tip = 9.81*0.175/0.3 = 5.72 m/s^2
  tip-over decel limit, mid CG 450 mm, 350 mm footprint: a_tip = 9.81*0.175/0.45 = 3.81 m/s^2
  tip-over decel limit, high CG 600 mm, 350 mm footprint: a_tip = 9.81*0.175/0.6 = 2.86 m/s^2

  braking distance = v^2 / (2a), each column at the deceleration named in its header

   v (m/s) | gentle a=1.0 m/s^2 | firm a=2.0 m/s^2 | a=3.4 m/s^2 (tip limit @ CG 505 mm) | a=5.0 m/s^2
       0.3 |              45 mm |            22 mm |                               13 mm |        9 mm
       0.5 |             125 mm |            62 mm |                               37 mm |       25 mm
       1.0 |             500 mm |           250 mm |                              147 mm |      100 mm

  braking distance AT the three tip limits computed above
   v (m/s) | CG 300 mm, a=5.72 | CG 450 mm, a=3.81 | CG 600 mm, a=2.86
       0.3 |              8 mm |             12 mm |             16 mm
       0.5 |             22 mm |             33 mm |             44 mm
       1.0 |             87 mm |            131 mm |            175 mm
```

> **Correction (2026-09-12 adversarial check).** An earlier revision headed the third column *"tip-limited, CG 300 mm"* and the fourth *"hard e-stop, will tip"*. Both labels were wrong. The 13/37/147 mm column is v²/(2a) at **a = 3.4 m/s²**, which is the tip limit for a CG at **505 mm**, not 300 mm. The true CG-300 mm tip limit of 5.72 m/s² gives **8/22/87 mm**, and the 9/25/100 mm column is **a = 5.0 m/s²**, which is *below* the 5.72 m/s² CG-300 tip limit and therefore would **not** tip that robot. The arithmetic in every column was correct; only the headers lied about which deceleration produced it. The second table above is new and gives the braking distance actually reachable at each CG without pitching forward.

**Finding:** a robot with its CG at 600 mm cannot brake harder than **2.86 m/s²** without tipping. That is the real deceleration ceiling — not the tyre friction limit. Every stopping-distance calculation below uses **a = 2.0 m/s²**, comfortably inside the tip limit for a mid-height CG. `inferred`.

Mechanical braking matters too: a robot that relies only on motor back-EMF has a much softer effective decel than one with a commanded regenerative brake. On a geared drive, an unpowered coast at 1.0 m/s can carry well past 500 mm. **Design rule: the brake is part of the safety function (ISO 3691-4 clause 4.2, PLr d). Size it, measure it, do not assume it.**

### 3.3 Latency budgets per real sensor chain

```
====================================================================================================
PART 2 -- latency budgets for real candidate sensors (measured/published frame rates)
====================================================================================================
  sensor chain                        T_react |    S @0.3 m/s |    S @0.5 m/s |    S @1.0 m/s
  VL53L5CX ToF @15 Hz                   147 ms |         67 mm |        136 mm |        397 mm
  VL53L5CX ToF @60 Hz (4x4)              97 ms |         52 mm |        111 mm |        347 mm
  RPLIDAR A1 @10 Hz spin                200 ms |         82 mm |        162 mm |        450 mm
  RPLIDAR C1/A2 @15 Hz spin             167 ms |         73 mm |        146 mm |        417 mm
  LD2410 24GHz mmWave (~10 Hz)          200 ms |         82 mm |        162 mm |        450 mm
  IWR6843 60GHz + point cloud           200 ms |         82 mm |        162 mm |        450 mm
  MLX90640 thermal @8 Hz                255 ms |         99 mm |        190 mm |        505 mm
  MLX90640 thermal @4 Hz                380 ms |        136 mm |        252 mm |        630 mm
  RGB cam + person NN @10 fps CPU       350 ms |        128 mm |        238 mm |        600 mm
  Safety laser scanner (IEC61496)       120 ms |         58 mm |        122 mm |        370 mm
```

Sensor latency here is one frame period (the worst case: the event occurs just after a frame closes). Compute latency is an estimate for the decision + comms hop; brake latency is command-to-torque. `inferred` from `datasheet-verified` frame rates.

### 3.4 The number that actually governs — a human walking *into* the robot

ISO 13855 uses **K = 1600 mm/s** as the approach speed of a walking person, and Banner's worked example computes `Ds = 1600 mm/s × (0.1s + 0.08s + 0.025s) + 1200 mm + 83 mm = 1611 mm (63")` — verified verbatim in the AG4 guide. A robot at 0.5 m/s meeting a person walking at 1.6 m/s has a **2.1 m/s closing speed**, not 0.5.

**Conditions on that 1611 mm example, which an earlier revision omitted and which change how far it transfers to a robot** `datasheet-verified`:
- It is **Example #1, a *stationary* horizontal danger-zone guard**, not a mobile one: leg detection at **50 mm resolution**, scanner mounted on perimeter fencing **300 mm above the floor** "to prevent crawling under the Protective Fields". It is not the AGV case.
- The three times are *"a robot stopping time of 100 ms, Scanner response time of 80 ms, the response time of a safety interfacing device is 25 ms (UM-FA-9A safety module)"*.
- The 1200 mm term is **not** an ISO 13855 term. Banner states it as *"the Dpf adder is equal to 1200 mm (**U.S. formula**)"*, applied *"because an individual can reach over the detection plane by bending at the waist"*. Banner's guide uses the U.S./ANSI form for its worked numbers and cites EN ISO 13855 only as a positioning reference. So the equation above is **the ANSI-form separation distance, presented here in ISO 13855 shape**; the two give different Dpf adders and must not be conflated.
- K = 1600 mm/s is the correct constant here because this is **whole-body/leg detection** (detection capability > 40 mm). For hand detection (capability ≤ 40 mm) ISO 13855 requires **K = 2000 mm/s** where the resulting distance is ≤ 500 mm. The 1600 mm/s used throughout Section 3.4 is right for a robot perimeter, and wrong for a finger or hand guard.

```
====================================================================================================
PART 3 -- full ISO-13855-style separation distance INCLUDING a human walking INTO the robot
  S = (v_robot + K_human)*T_react + v_robot^2/(2a) + Zsm + Zref
  K_human = 1.6 m/s (ISO 13855 walking approach speed)
  Zsm = 100 mm (hobby-grade sensor measurement tolerance)
  Zref = 100 mm (dirt / low-reflectance degradation allowance)
====================================================================================================
  sensor chain                       |     S @0.3 m/s |     S @0.5 m/s |     S @1.0 m/s
  VL53L5CX ToF @15 Hz                |         501 mm |         571 mm |         831 mm
  VL53L5CX ToF @60 Hz (4x4)          |         406 mm |         466 mm |         701 mm
  RPLIDAR A1 @10 Hz spin             |         602 mm |         682 mm |         970 mm
  RPLIDAR C1/A2 @15 Hz spin          |         539 mm |         613 mm |         883 mm
  LD2410 24GHz mmWave (~10 Hz)       |         602 mm |         682 mm |         970 mm
  IWR6843 60GHz + point cloud        |         602 mm |         682 mm |         970 mm
  MLX90640 thermal @8 Hz             |         707 mm |         798 mm |        1113 mm
  MLX90640 thermal @4 Hz             |         944 mm |        1060 mm |        1438 mm
  RGB cam + person NN @10 fps CPU    |         888 mm |         998 mm |        1360 mm
  Safety laser scanner (IEC61496)    |         450 mm |         514 mm |         762 mm
```

### 3.5 Protective field in the ISO 3691-4 form, applied to this robot

```
PROTECTIVE FIELD LENGTH, ISO 3691-4 / Banner AG4 form
PF = v*(t_sensor + t_control) + v^2/(2a) + Zsm + Zrefl + Zf

case                                 v     D_SD   PF cert  PF hobby  PF hobby+retro
-----------------------------------------------------------------------------------
VL53L5CX 15 Hz, firm brake         0.3     67mm     250mm     317mm           517mm
VL53L5CX 15 Hz, firm brake         0.5    136mm     319mm     386mm           586mm
VL53L5CX 15 Hz, firm brake         1.0    397mm     580mm     647mm           847mm
RPLIDAR C1 15 Hz, firm brake       0.3     73mm     256mm     323mm           523mm
RPLIDAR C1 15 Hz, firm brake       0.5    146mm     329mm     396mm           596mm
RPLIDAR C1 15 Hz, firm brake       1.0    417mm     600mm     667mm           867mm
RPLIDAR A1 5.5 Hz, firm brake      0.3    107mm     290mm     357mm           557mm
RPLIDAR A1 5.5 Hz, firm brake      0.5    203mm     386mm     453mm           653mm
RPLIDAR A1 5.5 Hz, firm brake      1.0    532mm     715mm     782mm           982mm

Add the 175 mm body half-width to get the range the sensor must actually report:
  VL53L5CX 15 Hz, firm brake       v= 0.3 m/s -> sensor must see reliably to  492 mm
  VL53L5CX 15 Hz, firm brake       v= 0.5 m/s -> sensor must see reliably to  561 mm
  VL53L5CX 15 Hz, firm brake       v= 1.0 m/s -> sensor must see reliably to  822 mm
  RPLIDAR C1 15 Hz, firm brake     v= 0.3 m/s -> sensor must see reliably to  498 mm
  RPLIDAR C1 15 Hz, firm brake     v= 0.5 m/s -> sensor must see reliably to  571 mm
  RPLIDAR C1 15 Hz, firm brake     v= 1.0 m/s -> sensor must see reliably to  842 mm
  RPLIDAR A1 5.5 Hz, firm brake    v= 0.3 m/s -> sensor must see reliably to  532 mm
  RPLIDAR A1 5.5 Hz, firm brake    v= 0.5 m/s -> sensor must see reliably to  628 mm
  RPLIDAR A1 5.5 Hz, firm brake    v= 1.0 m/s -> sensor must see reliably to  957 mm

WARNING FIELD (slow-down) sizing: 2x the protective field is the common rule.
  v= 0.3 m/s: protective  317 mm, warning  633 mm, human-approach (K=1.6)  551 mm
  v= 0.5 m/s: protective  386 mm, warning  772 mm, human-approach (K=1.6)  621 mm
  v= 1.0 m/s: protective  647 mm, warning 1293 mm, human-approach (K=1.6)  881 mm
```

### 3.6 The classification-time budget — why "distinguish human vs pet" is hard

If the warning field sits at 2× the protective field, the time available to run a classifier between "something appeared" and "must have stopped" is:

```
TIME AVAILABLE TO CLASSIFY (human vs pet vs object) before the protective field is hit,
given a warning field at 2x the protective field:
  v_robot= 0.3, static object         :  1055 ms between warning edge and protective edge
  v_robot= 0.3, walking pet 1.0 m/s   :   243 ms between warning edge and protective edge
  v_robot= 0.3, walking human 1.6 m/s :   167 ms between warning edge and protective edge

  v_robot= 0.5, static object         :   772 ms between warning edge and protective edge
  v_robot= 0.5, walking pet 1.0 m/s   :   257 ms between warning edge and protective edge
  v_robot= 0.5, walking human 1.6 m/s :   184 ms between warning edge and protective edge

  v_robot= 1.0, static object         :   647 ms between warning edge and protective edge
  v_robot= 1.0, walking pet 1.0 m/s   :   323 ms between warning edge and protective edge
  v_robot= 1.0, walking human 1.6 m/s :   249 ms between warning edge and protective edge
```

**Architectural conclusion, and it is the most important one in this document:** you get **167–323 ms** to classify a moving target. A thermal frame at 4 Hz (250 ms) or an mmWave micro-Doppler classifier needing a 1–2 s dwell **cannot complete inside that window**. Therefore:

> **Classification must never gate the stop.** The stop is triggered by *geometry* — something is inside the protective field — on the fastest, dumbest, most reliable sensor you have. Classification runs in parallel and only modulates *behaviour after the stop* (back away from a cat, wait politely for a human, push past nothing). A design that waits to identify what it saw before deciding whether to brake is a design that hits people.

### 3.7 Contact energy, and why compliance is not optional

```
====================================================================================================
PART 4 -- kinetic energy and a crude contact-force check (pet-scale target)
====================================================================================================
  m= 5 kg, v=0.3 m/s : KE =   0.22 J | crush  5 mm -> F =   45 N | crush 20 mm -> F =   11 N | crush 50 mm -> F =    4 N
  m= 5 kg, v=0.5 m/s : KE =   0.62 J | crush  5 mm -> F =  125 N | crush 20 mm -> F =   31 N | crush 50 mm -> F =   12 N
  m= 5 kg, v=1.0 m/s : KE =   2.50 J | crush  5 mm -> F =  500 N | crush 20 mm -> F =  125 N | crush 50 mm -> F =   50 N
  m=10 kg, v=0.3 m/s : KE =   0.45 J | crush  5 mm -> F =   90 N | crush 20 mm -> F =   22 N | crush 50 mm -> F =    9 N
  m=10 kg, v=0.5 m/s : KE =   1.25 J | crush  5 mm -> F =  250 N | crush 20 mm -> F =   62 N | crush 50 mm -> F =   25 N
  m=10 kg, v=1.0 m/s : KE =   5.00 J | crush  5 mm -> F = 1000 N | crush 20 mm -> F =  250 N | crush 50 mm -> F =  100 N
  m=15 kg, v=0.3 m/s : KE =   0.67 J | crush  5 mm -> F =  135 N | crush 20 mm -> F =   34 N | crush 50 mm -> F =   13 N
  m=15 kg, v=0.5 m/s : KE =   1.88 J | crush  5 mm -> F =  375 N | crush 20 mm -> F =   94 N | crush 50 mm -> F =   38 N
  m=15 kg, v=1.0 m/s : KE =   7.50 J | crush  5 mm -> F = 1500 N | crush 20 mm -> F =  375 N | crush 50 mm -> F =  150 N
```

Against ISO/TS 15066 transient contact force limits (cobot values, `vendor-page-verified`; these are collaborative-robot limits, not a household-robot standard, and are used here as the nearest published human-tolerance data):

| Body region | Transient force limit |
|---|---|
| Skull / forehead | 130 N |
| Face | 65 N |
| Neck (front) | 150 N |
| Chest | 140 N |
| Abdomen | 110 N |
| Upper legs / knees | 220 N |
| Lower legs (shin) | 130 N |
| Hands / fingers | 140 N |

**Finding:** a 15 kg robot at 1.0 m/s with a rigid shell delivers a mean **1500 N** into a shin — roughly **11× the 130 N limit**. The same robot at 0.5 m/s with a **50 mm compliant bumper** delivers **38 N**, safely under. A cat's ribcage is a smaller target with a smaller tolerance than a human shin and no published limit at all — `not published`.

**Two design rules fall out, and they are cheap:**
1. **Cap the speed.** 0.5 m/s is the household ceiling; 0.3 m/s is what ISO 3691-4 permits with detection muted. 1.0 m/s on a 10–15 kg robot in a home is not defensible.
2. **Make the leading surface crush 20–50 mm.** Foam over a bumper switch, or a sprung shell. Compliance converts an energy problem into a non-problem and costs a few dollars.

---

## 4. Cliff and stair detection — a separate, mandatory function

Cliff detection is **not** a special case of obstacle detection and cannot be folded into it. A horizontal perimeter scanner at 150–200 mm above the floor sees *nothing* at a stair nosing: the floor simply stops.

```
====================================================================================================
PART 7 -- cliff detection: travel after the edge is seen
====================================================================================================
  v=0.3 m/s, T_react= 50 ms -> travel after edge seen =    30 mm
  v=0.3 m/s, T_react=100 ms -> travel after edge seen =    45 mm
  v=0.3 m/s, T_react=150 ms -> travel after edge seen =    60 mm
  v=0.3 m/s, T_react=250 ms -> travel after edge seen =    90 mm

  v=0.5 m/s, T_react= 50 ms -> travel after edge seen =    67 mm
  v=0.5 m/s, T_react=100 ms -> travel after edge seen =    92 mm
  v=0.5 m/s, T_react=150 ms -> travel after edge seen =   117 mm
  v=0.5 m/s, T_react=250 ms -> travel after edge seen =   167 mm

  v=1.0 m/s, T_react= 50 ms -> travel after edge seen =   217 mm   *** OVERRUNS a 175 mm half-footprint ***
  v=1.0 m/s, T_react=100 ms -> travel after edge seen =   267 mm   *** OVERRUNS a 175 mm half-footprint ***
  v=1.0 m/s, T_react=150 ms -> travel after edge seen =   317 mm   *** OVERRUNS a 175 mm half-footprint ***
  v=1.0 m/s, T_react=250 ms -> travel after edge seen =   417 mm   *** OVERRUNS a 175 mm half-footprint ***
```

`inferred`, at a = 3.0 m/s² (a cliff stop is worth risking a pitch-forward).

**Finding:** at **1.0 m/s the robot goes over the edge at every plausible latency.** The drive wheels leave the floor before the stop completes. At 0.5 m/s with a 100 ms loop, travel is 92 mm — the sensor must therefore look **at least 92 mm ahead of the front wheel contact patch**, and preferably 150 mm.

**Which sensors do cliff detection:**

| Sensor | Suitable for cliff? | Note |
|---|---|---|
| Downward ToF (VL53L0X/L1X/L5CX) | Yes — best choice | Measures *actual* distance to floor, so a black floor still returns a *range*, not a pure intensity. Multi-zone (L5CX 8×8) covers a wider arc from one part. `inferred` |
| Reflective IR (TCRT5000, QRE1113) | Works, but is the classic failure | Intensity-only. See Section 6.4. |
| Downward ultrasonic | Poor | 2 cm minimum range, wide beam, absorbed by carpet |
| Horizontal lidar / mmWave | **No** | Wrong plane entirely |
| Bumper / tilt switch | Backup only | Fires after the fact |

**Minimum set: three to four downward-looking ToF sensors across the leading edge (plus two rear if the robot reverses), read at ≥ 50 Hz, wired so that a *lost* reading is treated as a cliff.** Fail-safe direction matters: "no return" and "cliff" must both stop the robot.

**Do not disable cliff detection to fix a dark-rug false positive.** That is the single most common hobbyist mistake in this area and it converts a nuisance into a fall.

---

## 5. The failure catalogue — ToF (VL53L0X / L1X / L5CX / L7CX)

`peer-reviewed-measured` values below come from **Caroleo, Albini and Maiolino**, *On the Characterisation of the Time-of-Flight VL53L5CX Sensor by STMicroelectronics for Indoor Robotics Applications*, Sensors, vol. 26, no. 5, art. 1639, 2026 ([MDPI](https://www.mdpi.com/1424-8220/26/5/1639) / [PMC12986679](https://pmc.ncbi.nlm.nih.gov/articles/PMC12986679/)).

> **Correction (2026-09-12 adversarial check).** An earlier revision of this document attributed this paper to *"Cabrera et al."*. The paper was re-read at PMC on 2026-09-12; the authors are **Giammarco Caroleo, Alessandro Albini and Perla Maiolino**. There is no author named Cabrera. Every measured value cited from it below was re-checked against the paper and is correct as quoted, with one refinement: the paper reports the white-board fit as *"slopes {0.9939, 1.0384} mm/mm and offsets {24.1, 18.15} mm"* and the black board as *"slopes {0.9766, 0.9698, 0.9763} mm/mm and offsets {27.79, 32.08, 32.42} mm"*, and the self-heating figure as **51.61 ± 1.70 °C**. The "1.005 slope" quoted in T1 below is a rounded mid-point of the two published white-board slopes, not a figure printed in the paper.

| # | Failure mode | Verified evidence and condition | Mitigation |
|---|---|---|---|
| T1 | **Black / dark absorbing surfaces** — black sock, black furniture leg, charcoal rug | `peer-reviewed-measured`: against **black vinyl**, VL53L5CX returned only **18.8 % valid measurements at 25 cm, 20.3 % at 40 cm, 34.4 % at 60 cm**. Against a black board the bias is ~30 mm with 0.97 slope and the standard deviation **peaks near 50 mm beyond 400 mm** — roughly **double** the uncertainty of a white board (~18 mm bias, 1.005 slope, max deviation ~13 mm at 20 mm). Valid-measurement rate on normal targets is "consistently below 10 % invalid". | Never treat "no return" as "clear". Add a second modality (radar or ultrasonic) that does not depend on optical reflectance. Reduce speed when valid-zone count drops below a threshold. Use the per-zone `target_status` field, not just the distance. |
| T2 | **Mirrors and glass** | `vendor-page-verified`: *"when an object is being imaged through a transparent barrier such as clear plastic or glass, the sensor will sense the distance to the transparent barrier instead of to the object"*; with a mirror, *"the time-of-flight sensor senses the distance to the mirror"* ([US10594920B2](https://patents.google.com/patent/US10594920B2/en)). A mirror at 45° returns the *folded* path length — the robot believes the corridor continues. | Ultrasonic sees glass reliably ([TDK](https://product.tdk.com/en/products/sensor/ultrasonic/tof/index.html)); pair one forward ultrasonic with the ToF array. Lidar intensity can flag transparent obstacles ([TOPGN](https://arxiv.org/html/2408.05608v1)). Map known glass doors and mirrors as permanent keep-out zones. |
| T3 | **Direct sunlight / high ambient IR** | `peer-reviewed-measured`: office lighting from 270 lux down to 0.5 lux had **negligible** effect. A **500 W halogen lamp (~3 klux)** beside the unit drove the measurement rejection rate to **almost 45 %** and the standard deviation to **almost 16 mm**. `vendor-page-verified`: ST publishes performance at **0 klux and 5 klux only**; a user report of VL53L1X outdoors at 14–93.6 klux found **only 33 % useful data** ([ST Community](https://community.st.com/t5/imaging-sensors/has-anyone-tested-the-vl53l1x-to-measure-pastures-pointing-down/td-p/70905)). **200 klux figures: not published by ST for these parts.** | Keep ToF as an indoor sensor. A sunlit window or patio door is a blind patch. Shade the aperture; do not point a ToF at a west-facing window at 17:00. |
| T4 | **Cover-glass crosstalk** | `vendor-page-verified`: crosstalk is VCSEL light reflected *inside* the cover glass back onto the SPAD array. The VL53L5CX is *"immune to crosstalk beyond 60 cm thanks to a histogram algorithm"*, but **below 60 cm crosstalk can exceed the true return, giving false targets or making targets appear closer than they are** ([ST UM2884 / AN5856](https://www.st.com/resource/en/application_note/an5856-guidelines-for-the-cover-glass-of-the-vl53l5cx-timeofflight-8x8-multizone-sensor-with-wide-field-of-view-stmicroelectronics.pdf)). **This is exactly the range band your protective field lives in (250–650 mm).** | Run crosstalk calibration *with the final cover glass fitted*. Re-run after any shell change. Keep an air gap per AN5856. Prefer **no** cover glass over a badly specified one. |
| T5 | **Dirt, grease, fingerprints on the window** | `vendor-page-verified`: patent literature explicitly names *"grease on the cover glass"* as a crosstalk source. Contamination raises crosstalk over time, so a calibration valid on day one drifts. | Periodic self-check: point at a known clear direction and monitor baseline crosstalk; flag for cleaning when it rises. Angle the window downward so dust does not settle (Banner AG4: mount *"facing down… to minimize the accumulation of dust on the Scanner's front screen"*). |
| T6 | **Retroreflectors** | `datasheet-verified`: Banner assigns a **Z_refl** adder specifically for retroreflectors in the scanning plane, set to 0 only when their presence *"can be excluded"*. Bicycle reflectors, safety-vest tape and reflective pet collars saturate a SPAD and can fold range. | Add **Z_refl = 200 mm** to the protective field unless you can genuinely exclude them from a home. The Section 3.5 "PF hobby+retro" column is the right number for a house with a dog wearing a reflective collar. |
| T7 | **Multipath / wraparound** | `peer-reviewed-measured`: the Sensors paper explicitly lists glass, mirrors, crosstalk and multipath as **not investigated** and requiring future work — so for the VL53L5CX specifically, multipath magnitude is **not published**. Physically, in a corner two surfaces return a path longer than either. | Reject zones whose range exceeds the geometric maximum for that bearing. Use 8×8 spatial consistency: a single anomalous zone surrounded by consistent ones is suspect. |
| T8 | **Narrow field of view** | `peer-reviewed-measured`: VL53L5CX diagonal FoV is **65°**; VL53L7CX is 90°. A 65° cone from one corner of a 350 mm square does not cover 360°. | You need **6–8 modules minimum** for 360° with overlap, or fewer L7CX at 90°. Budget for the I²C address juggling (each needs an XSHUT line). |
| T9 | **Thermal drift** | `peer-reviewed-measured`: the part self-heats to **52 °C after ~900 s** warm-up. Within-frame variability is 0.5–2 mm. | Calibrate warm, not cold. Allow 15 min before trusting sub-centimetre accuracy. |

---

## 6. The failure catalogue — other modalities

### 6.1 mmWave radar (24 GHz LD2410-class, 60 GHz IWR6843-class)

| # | Failure mode | Verified evidence | Mitigation |
|---|---|---|---|
| M1 | **Penetration through walls — detecting people in the NEXT room** | `vendor-page-verified`, and the most-reported real-world problem with 24 GHz presence sensors. LD2410 users report it detects *"someone standing quietly right outside a closed bedroom door even though there were two layers of sheetrock between them"*, and it sees through *"glass walls and thin plywood"* and *"wood panelling or thin plasterboard up to 5 cm thick"* ([ESPHome LD2410 docs](https://www.sudo.is/docs/esphome/components/ld2410/), [ESP Easy P159](https://espeasy.readthedocs.io/en/latest/Plugin/P159.html)). | Range-gate aggressively — reduce the maximum still-detection gate so the far gates are discarded. Better: **move to 60 GHz.** TI state *"60 GHz signals experience higher atmospheric absorption and reduced wall penetration compared to 24 GHz radar"*, limiting operation largely to line-of-sight inside a room ([TI SWRA818](https://www.ti.com/lit/ab/swra818/swra818.pdf)). For a *mobile* robot the problem is worse than for a fixed sensor, because the wall geometry changes continuously and a fixed gate cannot be tuned. |
| M2 | **Ego-motion clutter** | `peer-reviewed-measured`: when the radar itself moves, every static return acquires a Doppler shift proportional to the robot's velocity component along that bearing. Every wall becomes "moving". Published systems fuse *"robot ego-motion derived from kinematics and odometry to maintain spatial consistency under mobile deployment"* ([EM-Fall, arXiv 2606.11109](https://arxiv.org/html/2606.11109)). | Feed wheel odometry / IMU into the radar processing and subtract the ego-Doppler before thresholding. This is real work, not a config option, and it is the reason cheap presence modules designed for a fixed wall mount perform badly on a robot. |
| M3 | **Metal reflections and ghost targets** | `peer-reviewed-measured`: *"static objects with non-negligible reflectance … interact with moving human subjects and generate time-varying multipath ghosts and shadow ghosts, which can be easily confused as real subjects"*; multipath creates *"false targets further away than the real one"*, worse indoors because of wall, ceiling and floor reflections ([Ghost Suppression, PMC12158235](https://pmc.ncbi.nlm.nih.gov/articles/PMC12158235/)). A fridge, a radiator, a metal table leg. | Trajectory-guided filtering; eliminate tracks that lie outside known room boundaries; require track persistence over several frames before acting. Ghosts are *extra* detections — they cause nuisance stops, not collisions, which is the safe direction to fail. |
| M4 | **Vibration-induced false presence** | `vendor-page-verified`: *"strong vibrations or moving debris may require filtering algorithms to avoid false triggers"* (TI). A 60 GHz radar resolves micron-scale motion ([arXiv 2107.10993](https://arxiv.org/pdf/2107.10993)), so a robot's own drive train and a rattling shell are within its sensitivity. | Isolate the radar module mechanically from the chassis. Notch-filter the drive-motor and gearbox frequencies. Validate with the drivetrain running and the robot blocked. |
| M5 | **Fans, curtains, HVAC reading as motion** | `vendor-page-verified` (TI SWRA818): *"rotating fan blades create Doppler signatures similar to human motion"*; *"fabric and lightweight materials moving in air currents"*; HVAC air movement triggers false alarms. | Range-Doppler filtering: *"proper range-Doppler filtering reduces false detections by rejecting stationary clutter and low-velocity noise"*. A fan has a periodic, spatially fixed signature — reject fixed-position periodic returns. |
| M6 | **Cannot see a truly still human without micro-motion processing** | `vendor-page-verified`: detection of a stationary person relies on respiration and heartbeat signatures, and *"requires specialized signal processing"*. A person holding their breath, or a sleeping cat behind a chair, may vanish. Detection of multiple stationary humans is an active research problem ([PMC5134581](https://www.ncbi.nlm.nih.gov/pmc/articles/PMC5134581/)). | **Never let radar be the only thing standing between the robot and a person.** Micro-motion dwell times are 1–2 s — far longer than the 167–323 ms classification budget from Section 3.6. |
| M7 | **Pets read as humans, or as nothing** | `vendor-page-verified`: TI list *"pets and small animals"* as a source of motion signatures resembling human presence. Conversely, published trackers apply *"a non-human target filter [to remove] returns associated with pets"* — i.e. the discrimination exists but is a trained classifier, not a threshold. | Treat "moving thing at pet height" as a stop-and-yield, not as a classification problem to be solved before braking. |

### 6.2 Lidar (RPLIDAR A1 / C1 class)

`datasheet-verified` from the RPLIDAR A1M8 datasheet rev 2.1, 2018-02-05:

| Item | Value | Condition quoted verbatim |
|---|---|---|
| Distance range | 0.15–6 m (A1M8-R4 and below); 0.15–12 m (A1M8-R5) | **"White objects"** |
| Distance resolution | < 0.5 mm (< 1.5 m); < 1 % of distance (all range) | |
| Angular resolution | ≤ 1° | at 5.5 Hz scan rate |
| Scan rate | 1 / **5.5** / 10 Hz | typical measured at 360 samples per scan |
| Sample frequency | ≥ 8000 Hz (8010 max) | R3/R4 need firmware 1.24; R1/R2 are 2 kHz only |
| Sample duration | 0.125 ms | |
| Laser wavelength | 775 / **785** / 795 nm | infrared band |
| Laser power | typ **3 mW**, max 5 mW | peak power |
| Pulse length | typ 110 µs, max 300 µs | |
| Eye safety | **Class I**, *"Complies with 21 CFR 1040.10 and 1040.11 except for deviations pursuant to Laser Notice No. 50, dated June 24, 2007"* | The datasheet states the laser is *"safety to human and pet"* |

| # | Failure mode | Verified evidence | Mitigation |
|---|---|---|---|
| L1 | **Planar blind slice — the defining limitation** | `inferred` from `datasheet-verified` geometry. A 2D lidar sees one horizontal plane. Below it: a cat lying flat, a toy, a step edge. Above it: a table top, an open drawer, a person's outstretched arm, a countertop overhang at 900 mm. Banner explicitly bound the AGV field height: *"the plane of the Protective Field should not exceed 200 mm (7.9") above the floor"* and required scanner mounting at *"300 mm above the floor to prevent crawling under"* in the stationary case — i.e. professionals control the geometry precisely because the plane is a slice. | Lidar alone is **insufficient** on a 600–1200 mm robot. Add a downward-tilted ToF array for the sub-plane volume and an upward-looking element for overhangs. Banner's Example #8 solves this in industry by adding *vertically* mounted scanners for torso detection at 150 mm resolution. |
| L2 | **Black absorbing surfaces** | `datasheet-verified` by omission: the range spec is qualified **"White objects"** and no black-target figure is given — **not published** by Slamtec for the A1. A triangulation lidar's return falls with target albedo exactly as a ToF's does. | Same as T1. This is also why IEC 61496 Type 3 mandates 1.8 % reflectance capability — a certified scanner has to prove it; a hobby lidar does not. |
| L3 | **Direct sunlight** | `datasheet-verified`: *"It can work excellent in all kinds of indoor environment and outdoor environment without direct sunlight exposure."* The A1 is a **triangulation** system, not dTOF; the C1 is dTOF and claims better ambient immunity, `vendor-page-verified`. | Indoor duty only, or move to the C1/S-series dTOF. Treat a sunlit patch of floor as a possible blind spot. |
| L4 | **Dust and window contamination** | `datasheet-verified` (Banner, general ESPE guidance): mounting orientation is chosen specifically to shed dust; IEC 61496 Type 3 requires proven *"resistance to the effects of dirt, backgrounds, and obstructions"*. | Scheduled cleaning. A degradation self-test: compare a known static feature's return intensity over time. |
| L5 | **Mutual interference between two scanners** | `datasheet-verified`: Banner requires *"a vertical offset height of 100 mm (or more), or … physical shielding to prevent one Scanner from interfering with another"*. Relevant if two robots meet, or if you mount two units. | Vertical offset, or time-multiplex. |
| L6 | **Shadow effect and needle/cone field artefacts** | `datasheet-verified`: Banner require the installer to *"Be aware of the effect of needle- and cone-shaped fields and eliminate areas of unreliable detection"* and to *"Eliminate the 'shadow effect'"*. A pillar or a table leg casts a radial shadow in which a child is invisible. | Multiple sensor positions; never rely on a single vantage point for a 360° claim. |
| L7 | **Eye safety** | `datasheet-verified`: **Class 1 / Class I**. Class 1 means *safe under all reasonably foreseeable conditions of normal use*; the term "eye-safe" may only be used of Class 1 products ([IEC 60825-1 summary](https://control.com/technical-articles/safety-considerations-for-lidar-sensors/)). | No hazard as supplied. **But**: removing or replacing the optical housing, or driving the emitter from your own firmware, voids the classification. Do not modify the optics. |

### 6.3 Thermal (MLX90640 / thermopile arrays)

| # | Failure mode | Verified evidence | Mitigation |
|---|---|---|---|
| H1 | **Ambient near body temperature destroys contrast** | `vendor-page-verified`: person-classification logic keys on temperatures *"in an expected range of about 35 to about 40 degrees C"*. The MLX90640's stated accuracy is **±2 °C in the 0–100 °C band** ([Adafruit product page 4407](https://www.adafruit.com/product/4407), [Waveshare wiki](https://www.waveshare.com/wiki/MLX90640-D55_Thermal_Camera)). At 35 °C ambient a clothed person's surface may differ from the room by less than the sensor's own error bar. ISO 3691-4's own declared short-term ambient maximum is **+40 °C** — the failure is squarely inside the standard's operating envelope. | Do not use thermal as the primary human detector. Use it as a *corroborating* channel that is allowed to fail silent. Consider adaptive thresholding on the scene's own median rather than an absolute temperature. |
| H2 | **Sun-warmed floor patches, radiators, laptops, mugs** | `vendor-page-verified`: thermal camera performance *"can be adversely affected by heat sources"*. A sunlit rug at 38 °C looks exactly like a person to a threshold detector. | Require *shape* and *motion* consistency, not just temperature. A 32×24 array is enough to reject a large uniform blob. |
| H3 | **Glass is opaque in LWIR** | `vendor-page-verified`: *"Standard optical glass is opaque in the 8–14 micron part of the spectrum"*; thermal optics use germanium, zinc selenide or silicon ([Workswell](https://workswell.eu/germanium-lens-lwir-optics-thermal-cameras-modules/), [LightPath](https://www.lightpath.com/insights/what-is-long-wave-infrared-imaging-and-where-is-it-used)). | You cannot put a thermal sensor behind a normal window in your robot's shell. It needs its own germanium/silicon aperture or an open hole. An open hole then collects dust and needs cleaning. Budget for this at design time, not after the shell is printed. |
| H4 | **Slow frame rate** | `datasheet-verified`: MLX90640 is configurable but is typically run at 4 or 8 Hz on I²C for noise reasons. Section 3.3: at 8 Hz the chain latency is **255 ms**; at 4 Hz it is **380 ms**. At 4 Hz and 0.5 m/s the required separation is **1060 mm**, three times the ToF figure. | Thermal is a *warning-field* and *classification* sensor. It must never be in the protective-stop path. |
| H5 | **Low resolution for pets at range** | `inferred`: a 32×24 array over 55° puts a 300 mm-tall cat at 1 m across roughly 2–3 pixels vertically. Fur is an insulator; a cat's coat surface is markedly cooler than its core. | Pets are a *close-range* thermal target at best. Do not expect pet detection beyond ~1.5 m. |

### 6.4 PIR (passive infrared)

| # | Failure mode | Verified evidence | Mitigation |
|---|---|---|---|
| P1 | **No static detection — structural, not fixable** | `vendor-page-verified`: PIR uses two pyroelectric elements; *"in a stable scene both receive the same amount of IR and cancel each other out"*, and the signal chain is *"filtered to respond only to rapid thermal changes — typically faster than 1–2 seconds"*. A motionless person is invisible by design. | **PIR is disqualified as a safety sensor.** It is acceptable only as a wake-from-sleep trigger. |
| P2 | **Warm-air-current false triggers** | `vendor-page-verified`: *"an HVAC vent puffing warm air or sunlight tracking across a wall"*; a uniform change across all zones is rejected, but *"localized thermal imbalances and gentle air disturbances can produce localized transport of infrared energy that may traverse the boundary of a detection zone and trigger a false activation"* ([Industrial Monitor Direct](https://industrialmonitordirect.com/blogs/knowledgebase/pir-motion-sensor-false-triggers-industrial-application-troubleshooting)). | Aim away from vents. Require corroboration before acting. |
| P3 | **Ego-motion makes every scene "move"** | `inferred`: on a moving robot the differential-zone principle fires continuously. PIR on a mobile platform is essentially a random number generator. | Gate PIR to stationary periods only. |

### 6.5 Ultrasonic — the glass/mirror mitigation, with its own failures

Included because it is the specific answer to T2/L1 and must be specified honestly.

| # | Failure mode | Verified evidence | Mitigation |
|---|---|---|---|
| U1 | **Soft/absorbing targets** | `vendor-page-verified`: *"soft materials like fabric or foam absorb sound waves, reducing effective range"*; testing indicates most HC-SR04 units are *"unreliable for detecting soft and uneven objects such as humans beyond approximately 1 metre, where successful measurement rates fall below 50 %"* ([Last Minute Engineers](https://lastminuteengineers.com/arduino-sr04-ultrasonic-sensor-tutorial/)). A person in a wool coat, or a cat, is a poor ultrasonic target. | Use ultrasonic *only* for the hard/specular targets that defeat ToF — glass, mirrors, gloss doors. Never as the human detector. |
| U2 | **Specular reflection off angled surfaces** | `vendor-page-verified`: *"angling the sensor more than ~15° from perpendicular to the target surface will reduce or eliminate the echo."* | Multiple emitters at different bearings; treat a missing echo as "unknown", not "clear". |
| U3 | **Minimum range** | `vendor-page-verified`: *"objects closer than 2 cm will return 0 or erratic readings."* | Mechanical standoff. |
| U4 | **Crosstalk between units** | `vendor-page-verified`: simultaneous firing saturates the neighbouring receiver; **a minimum 33 ms interleave** is needed (23 ms round trip at 400 cm plus 10 ms margin). Eight sensors round-robin is therefore **264 ms per full sweep — ~3.8 Hz**. | This latency is fatal in the protective-stop path. Ultrasonic is a **warning-field** sensor only. Fire them in parallel only when their cones genuinely do not overlap. |

---

## 7. Summary failure matrix

| Failure | ToF | 24 GHz | 60 GHz | Thermal | PIR | 2D Lidar | Ultrasonic |
|---|---|---|---|---|---|---|---|
| Black absorbing surface | **Fails** (18.8 % valid @ 25 cm on black vinyl) | Unaffected | Unaffected | Unaffected | Unaffected | **Fails** (spec is white-target only) | Unaffected |
| Glass / mirror | **Fails** (ranges to the pane) | Sees through glass | Partly | **Fails** (LWIR opaque) | **Fails** | **Fails** | **Works** |
| Direct sunlight | **Degrades** (45 % rejection @ 3 klux) | Unaffected | Unaffected | **Degrades** | **False triggers** | **Degrades** (A1 triangulation) | Unaffected |
| Detects through a wall (unwanted) | No | **Yes — 5 cm plasterboard** | Reduced | No | No | No | No |
| Still human | **Works** (geometric) | Micro-motion only, 1–2 s | Micro-motion only | Works if contrast exists | **Fails** | **Works** (geometric) | Marginal |
| Robot ego-motion | Unaffected | **Fails without odometry fusion** | **Fails without fusion** | Unaffected | **Fails** | Unaffected | Unaffected |
| Fans / curtains / HVAC | Unaffected | **False motion** | **False motion** | Minor | **False trigger** | Unaffected | Minor |
| Below/above the scan plane | Covered (array) | Covered (volume) | Covered | Covered | n/a | **Blind slice** | Partly |
| Cliff / stair edge | **Works** (downward) | No | No | Marginal | No | No | Poor |
| Latency in the stop path | **52–147 ms — best** | 200 ms | 200 ms | 255–380 ms | n/a | 167–200 ms | ~264 ms for 8 |

---

## 8. Failure *direction* — the rule that separates safe from unsafe

Every failure above has a direction. Classify each one before you write a line of code:

- **Fail-to-danger** (the sensor says "clear" when something is there): black sock in front of a ToF; a still person to a radar; a cat under the lidar plane; a dark rug to a horizontal sensor. **These are the ones that hurt someone.** Every fail-to-danger mode must be covered by a *second modality with a different physics*.
- **Fail-to-safe** (the sensor says "occupied" when it is clear): radar ghosts; PIR on a warm draught; a dark rug read as a cliff. These cost availability, not safety. **Never "fix" one by widening a threshold.**

The two must be handled asymmetrically: OR the stop signals (any sensor says stop → stop), AND the clear signals (all sensors must agree it is clear before resuming). That single line of logic is worth more than any individual sensor upgrade.

---

## 9. The minimum safe sensor set

### 9.1 Must have

| Function | Sensor | Why it cannot be dropped |
|---|---|---|
| **Speed cap** | Firmware + measured brake test | 0.5 m/s ceiling; 0.3 m/s in unmapped or occupied space (ISO 3691-4's own muted-detection figure). This is free and it does more for safety than any sensor. |
| **Compliant leading surface** | 20–50 mm foam/sprung bumper over a switch | Section 3.7: converts 250–1500 N into 25–100 N. The last line of defence when everything above it fails, and the only one that works against a black sock at 1 m/s. |
| **Cliff detection** | 4–6 downward ToF, ≥ 50 Hz, "no return = cliff" | Section 4. Separate mandatory function. Nothing else does it. |
| **Geometric obstacle field, 360°** | 2D lidar **plus** a ToF array, or a full ToF ring (6–8 × VL53L5CX/L7CX) | Lidar gives range and 360° cheaply; the ToF array covers the sub-plane and above-plane volume the lidar's slice misses, and the two disagree on *different* targets (lidar loses black; ToF loses at 65° FoV edges). |
| **Emergency stop reachable by a person** | Physical button on the shell | Keep the button. Do **not** justify it with the 600 mm figure: see the correction in Section 2.2 — "reachable stop function required within 600 mm" is a per-zone column in Annex A Table A.1 and reads **NO** for both rows published in the free extract, and the claim that it is a fallback for "personnel detection cannot be implemented" is unverified. On a 350 mm robot one button on top is reachable from any side regardless. |
| **Two-tier field logic** | Software | Warning field (slow + announce) at ~2× the protective field; protective field (stop) sized from Section 3.5. Speed-dependent field sets. |

### 9.2 Nice to have

| Function | Sensor | What it buys |
|---|---|---|
| Human presence corroboration | 60 GHz mmWave (not 24 GHz) | Sees a still person the geometry sensors already see, but also sees them through a chair back. **Use 60 GHz** — 24 GHz's through-wall penetration makes it detect the neighbour and is a genuine, widely reported problem. |
| Human vs pet vs object classification | Thermal array + camera + NN | Only after the stop. Section 3.6: no classifier fits in the 167–323 ms window. |
| Glass and mirror detection | 1–2 forward ultrasonic | Covers the one target class the entire optical stack fails on. Warning field only (U4 latency). |
| Wake-on-presence while parked | PIR | Power saving only. Not a safety function. |

### 9.3 Why single-modality will eventually hit something — the concrete scenarios

- **Lidar only.** A cat asleep on its side, 120 mm tall, sits entirely below a 150–200 mm scan plane. The robot drives over it. Also: a black boot, a glass coffee-table leg, a low toy box, a stair edge.
- **ToF only.** A person in black jeans at 600 mm returns valid data in under 20 % of zones (T1's 18.8 % figure is for black vinyl at 25 cm — the honest expectation is worse at 600 mm). The robot sees an empty corridor and walks into their shin at 250 N.
- **mmWave only.** A person standing perfectly still in a doorway while the robot is moving: the ego-Doppler swamps the return, micro-motion processing needs 1–2 s, the classification budget is 184 ms. Meanwhile the robot brakes for a ceiling fan two rooms away.
- **Thermal only.** August, 35 °C indoors. Contrast is inside the ±2 °C error bar. The robot sees a uniform warm field and a sun patch that looks more like a person than the person does.
- **PIR only.** Disqualified by P1 and P3.
- **Ultrasonic only.** A human in a wool coat at 1.2 m is detected under 50 % of the time, and a full 8-sensor sweep takes 264 ms.

Every one of those is a **fail-to-danger** mode with a single physics cause. Two modalities with *different* physics — optical geometry plus radio, or optical geometry plus mechanical contact — remove the common cause. **That is the whole argument for sensor fusion here: not accuracy, but the elimination of a shared blind spot.**

### 9.4 The compliance reality check

You will not achieve PL d. PL d requires a Category 3 architecture with certified components, and no hobby module is certified. What you *can* do, and should:

1. **Use the industrial arithmetic even with uncertified parts.** The Section 3.5 numbers are defensible and you can test them.
2. **Adopt the certified Z-factor discipline.** `Z_SM` for measurement tolerance, `Z_refl` for retroreflectors, `Z_F` for ground clearance. Use the hobby (larger) values.
3. **Cap the speed so the residual risk is small even when detection fails completely** — that is what ISO 3691-4's 0.3 m/s muted-detection row is for.
4. **Measure your real stopping distance** on your real floor with your real battery state, and put the measured number into the field calculation. Do not use the value in this document.
5. **Test with the adversarial targets**: a black sock on the floor, a mirror, a glass door, a sunlit patch, a sleeping cat mannequin at 120 mm, and a person standing still in black clothing.

---

## 10. Open items — explicitly not published or not verified

- **ISO 3691-4 person-detection test pieces.** The standard references the EN 1525:1997 test pieces for its two detection tests (Test A and Test B), but the dimensions are behind the paywall. **Not published** in any free source I could verify.
- **ANSI/A3 R15.08-2-2023 numeric zone and stopping requirements.** Paywalled. **Not published** free.
- **VL53L5CX ranging at 200 klux.** ST publish 0 klux and 5 klux only. **Not published** for 200 klux.
- **RPLIDAR A1/C1 maximum range against a black or 10 % grey target.** The datasheet qualifies its range as "White objects" and gives no low-reflectance figure. **Not published.**
- **VL53L5CX multipath and mirror magnitude.** The Sensors characterisation paper explicitly lists these as future work. **Not measured.**
- **Any published pain or injury limit for a pet.** **Does not exist.** ISO/TS 15066 values are human cobot values and are used here as the nearest available proxy.
- **ISO 13482 impact limits.** Section 2.1 quotes the standard as saying that no exhaustive, internationally recognised pain or injury data existed at publication. **That quotation could not be confirmed at a primary source on 2026-09-12.** ISO 13482:2014 is paywalled; `iso.org/standard/53820.html` and the ISO Online Browsing Platform both return **HTTP 403** to an unauthenticated fetch, and no free extract carrying the sentence was found. The wording itself is suspect: the quoted sentence refers to *"the time of publication of ISO 13482:2014"*, which is how a **secondary** source cites the standard, not how a standard refers to itself (it would say "this document"). Treat the sentence as **`unverified`, secondary-sourced paraphrase**, not as `standard-verified`. The conclusion drawn from it — that ISO 13482 gives no design number for impact — is unchanged and is separately supported by the fact that ISO/TS 15066 cobot values are the nearest published human-tolerance data anyone cites for this case.
- **ISO 3691-4 "180 mm" personnel-detection gap figure.** A claim circulates that personnel detection must detect persons to within 180 mm between the edge of the safety fields and surrounding objects. **No such figure appears anywhere in this document, in the TÜV whitepaper, or in the free ISO 3691-4:2023 preview** (which stops at the end of Clause 3). **Unverifiable** — do not adopt it.
- **ISO 3691-4:2023 Clause 4 and Annex A text.** The free preview ends at Clause 3. Every Clause 4 / Annex A value in Section 2.2 is second-hand from a TÜV whitepaper on the **2020 first edition**. **Not verified at the 2023 text.**

---

## Sources

- [ISO 13482:2014 — Robots and robotic devices — Safety requirements for personal care robots](https://www.iso.org/standard/53820.html)
- [ISO/FDIS 13482 — Robotics — Safety requirements for service robots](https://www.iso.org/standard/83498.html)
- [ISO/DIS 13482:2024 (ANSI webstore)](https://webstore.ansi.org/standards/iso/isodis134822024)
- [ISO 3691-4:2023 standard preview (table of contents and clause structure)](https://cdn.standards.iteh.ai/samples/83545/a3d9d057a08d4f9c8e8e87cdc947583c/ISO-3691-4-2023.pdf)
- [TÜV Rheinland — ISO 3691-4:2020, A Standard for Automated Guided Vehicles (whitepaper)](https://www.tuv.com/content-media-files/master-content/services/industrial-services/pdf/tuv-rheinland-automatic-guided-vehicles-whitepaper-en_neu.pdf)
- [ISO/DIS 3691-4 online browsing platform](https://www.iso.org/obp/ui/#iso:std:iso:3691:-4:dis:ed-2:v1:en:sec:E)
- [ANSI/A3 R15.08-2-2023 (ANSI webstore)](https://webstore.ansi.org/standards/ria/ansia3r15082023)
- [ANSI/RIA R15.08-1-2020 (ANSI webstore)](https://webstore.ansi.org/standards/ria/ansiriar15082020)
- [The Robot Report — ANSI/RIA R15.08 redefines industrial mobile robots](https://www.therobotreport.com/ansi-ria-r15-08-standard-redefines-industrial-mobile-robots-whats-new-and-why-it-matters/)
- [Banner Engineering AG4 Series Safety Laser Scanner Application Guide, P/N 147900 rev. A](https://info.bannerengineering.com/cs/groups/public/documents/literature/147900.pdf)
- [Safety Laser Scanners: How They Work, IEC 61496 Standards, and Integration Guide](https://industrialsafetysensor.com/blog/safety-laser-scanners-guide/)
- [Hokuyo — The standards for safety LiDAR (IEC 61496 types)](https://www.hokuyo-aut.jp/products/data.php?id=112)
- [SICK — Electro-sensitive protective devices (ESPE) for safe machines, whitepaper](https://www.sick.com/media/docs/7/57/057/whitepaper_electro_sensitive_protective_devices_espe_for_safe_machines_en_im0062057.pdf)
- [Pilz — EN/IEC 61496](https://www.pilz.com/en-US/iec-en-61496-1)
- [Caroleo, Albini and Maiolino, On the Characterisation of the Time-of-Flight VL53L5CX Sensor by STMicroelectronics for Indoor Robotics Applications, Sensors 26(5):1639, 2026 (MDPI)](https://www.mdpi.com/1424-8220/26/5/1639)
- [Keyence SZ-V Series safety laser scanner specifications — "Reflectance 1.8 % min.", IEC61496-3 Type 3 AOPDDR](https://www.keyence.com/products/safety/laser-scanner/sz-v/specs/)
- [Same paper, full text on PubMed Central](https://pmc.ncbi.nlm.nih.gov/articles/PMC12986679/)
- [STMicroelectronics VL53L5CX product page](https://www.st.com/en/imaging-and-photonics-solutions/vl53l5cx.html)
- [ST AN5856 — Guidelines for the cover glass of the VL53L5CX](https://www.st.com/resource/en/application_note/an5856-guidelines-for-the-cover-glass-of-the-vl53l5cx-timeofflight-8x8-multizone-sensor-with-wide-field-of-view-stmicroelectronics.pdf)
- [ST UM2884 — A guide to using the VL53L5CX](https://www.st.com/resource/en/user_manual/um2884-a-guide-to-using-the-vl53l5cx-multizone-timeofflight-ranging-sensor-with-wide-field-of-view-ultra-lite-driver-uld-stmicroelectronics.pdf)
- [ST Community — VL53L1X outdoors at 14–93.6 klux](https://community.st.com/t5/imaging-sensors/has-anyone-tested-the-vl53l1x-to-measure-pastures-pointing-down/td-p/70905)
- [ST Community — VL53L5CX sunlight range](https://community.st.com/t5/imaging-sensors/vl53l5cx-sunlight-range/td-p/602218)
- [US10594920B2 — Glass detection with time of flight sensor (Google Patents)](https://patents.google.com/patent/US10594920B2/en)
- [TOPGN: Real-time Transparent Obstacle Detection using Lidar Point Cloud Intensity (arXiv 2408.05608)](https://arxiv.org/html/2408.05608v1)
- [Real-Time Glass Detection and Reprojection using Sensor Fusion Onboard Aerial Robots (arXiv 2510.06518)](https://arxiv.org/html/2510.06518v1)
- [TDK — Ultrasonic ToF sensors (detection of transparent objects)](https://product.tdk.com/en/products/sensor/ultrasonic/tof/index.html)
- [Slamtec RPLIDAR A1M8 Introduction and Datasheet, rev 2.1, 2018-02-05](https://www.slamtec.com/en/Lidar/A1)
- [Slamtec RPLIDAR C1 datasheet (mirror)](https://static.generation-robots.com/media/slamtec-rplidar-c1-datasheet.pdf)
- [Slamtec RPLIDAR C1 product page](https://www.slamtec.com/en/c1)
- [Texas Instruments SWRA818 — How 60 GHz Radar Sensors Reduce False Detections](https://www.ti.com/lit/ab/swra818/swra818.pdf)
- [ESPHome LD2410 component documentation](https://www.sudo.is/docs/esphome/components/ld2410/)
- [ESP Easy P159 — LD2410 presence sensor](https://espeasy.readthedocs.io/en/latest/Plugin/P159.html)
- [EM-Fall: Embodied mmWave Sensing on Humanoid Robots (arXiv 2606.11109)](https://arxiv.org/html/2606.11109)
- [Indoor mmWave Radar Ghost Suppression (PMC12158235)](https://pmc.ncbi.nlm.nih.gov/articles/PMC12158235/)
- [Environment-aware Multi-person Tracking with mmWave Radars (ACM IMWUT)](https://dl.acm.org/doi/10.1145/3610902)
- [A 60-GHz Radar Sensor for Micron-Scale Motion Detection (arXiv 2107.10993)](https://arxiv.org/pdf/2107.10993)
- [Detection of Multiple Stationary Humans Using UWB MIMO Radar (PMC5134581)](https://www.ncbi.nlm.nih.gov/pmc/articles/PMC5134581/)
- [Adafruit MLX90640 IR Thermal Camera Breakout (55°) product page](https://www.adafruit.com/product/4407)
- [Adafruit MLX90640 learn guide](https://learn.adafruit.com/adafruit-mlx90640-ir-thermal-camera/overview)
- [Waveshare MLX90640-D55 wiki](https://www.waveshare.com/wiki/MLX90640-D55_Thermal_Camera)
- [Workswell — Germanium lenses and LWIR optics (glass opacity at 8–14 µm)](https://workswell.eu/germanium-lens-lwir-optics-thermal-cameras-modules/)
- [LightPath — What is long-wave infrared imaging](https://www.lightpath.com/insights/what-is-long-wave-infrared-imaging-and-where-is-it-used)
- [Industrial Monitor Direct — PIR motion sensor false triggers](https://industrialmonitordirect.com/blogs/knowledgebase/pir-motion-sensor-false-triggers-industrial-application-troubleshooting)
- [Texas Instruments TIDUCV3B — PIR sensor signal chain user guide](https://www.ti.com/lit/ug/tiducv3b/tiducv3b.pdf)
- [Last Minute Engineers — HC-SR04 ultrasonic sensor](https://lastminuteengineers.com/arduino-sr04-ultrasonic-sensor-tutorial/)
- [Industrial Monitor Direct — Multiple HC-SR04 sensors, crosstalk and interleave](https://industrialmonitordirect.com/blogs/knowledgebase/using-multiple-hc-sr04-ultrasonic-sensors-triangulation-setup-and-interference-prevention)
- [GaryDyr/HC-SR04-beam-tests — beam dispersion measurements](https://github.com/GaryDyr/HC-SR04-beam-tests)
- [Control.com — Safety considerations for LiDAR sensors (IEC 60825-1 Class 1)](https://control.com/technical-articles/safety-considerations-for-lidar-sensors/)
- [ams OSRAM — Eye safety with IR VCSELs: safe limits and measurements](https://look.ams-osram.com/m/4cc7579d06a72fe/original/Eye-safety-with-ams-OSRAM-IR-VCSELs-safe-limits-measurements-and-use-of-integrated-safety-features.pdf)
- [Alibaba product insights — robot vacuum cliff sensors on dark rugs](https://www.alibaba.com/product-insights/why-does-my-robot-vacuum-get-stuck-on-dark-rugs-and-how-to-trick-its-sensors.html)
- [Samsung Community — cliff sensor stops vacuum on dark carpet](https://eu.community.samsung.com/t5/home-appliances/cliff-sensor-problem-where-the-vacuum-won-t-go-over-dark-carpets/td-p/12980487)
