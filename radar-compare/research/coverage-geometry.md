# Coverage Geometry for a 350 mm Perimeter Sensing Ring

**Lane:** coverage-geometry
**Date of computation:** 2026-09-12
**Platform under study:** mobile robot, footprint 350 mm square **or** 350 mm diameter round, overall height 600–1200 mm
**Targets:** any collidable obstacle; humans; pets 200–500 mm tall; and the human / pet / inanimate discrimination problem

All arithmetic in this document was produced by a Python script and the raw output is pasted verbatim. The script lives at
`C:/Users/Jeremy/AppData/Local/Temp/claude/c--dev-robots/cd75d6eb-5036-4579-a69b-e95996c940ed/scratchpad/geom.py`.
Every number below is **derived**, not quoted from a vendor, so its confidence class is **datasheet-verified only where a
field-of-view figure is attributed to a part**; the geometry itself is exact arithmetic.

> **Adversarial spec check, 2026-09-12 — corrections applied in place.**
> All pure-geometry results in this document were independently recomputed and **every one reproduced exactly**
> (blind-wedge formula, the 350 mm square constants, `N_min`, all four round-platform `D_tip` tables, the mixed 8-ring
> ray intersection, both beam-footprint tables, and the floor-strike table). **The errors are all in the FoV attribution,
> not in the arithmetic:**
> 1. **The VL53L1X's 27° is a DIAGONAL FoV**, not a horizontal one — ST DS DocID031281 Rev 3 Table 1 reads "Receiver
>    Field Of View **(diagonal FOV)** Programmable from 15 to 27 degrees". Horizontal is **19.270°**. This document's own
>    §6 warns about exactly this trap and then falls into it everywhere 27° is used as a ring FoV.
> 2. **The VL53L5CX's horizontal FoV is 45.0°, published directly** (DS13754 Rev 2 Table 2: 45° H / 45° V / 63°
>    diagonal) — the earlier "~46.9–48.5° horizontal" was a pinhole estimate that the datasheet supersedes, and the
>    "65° diagonal" product-page figure could not be confirmed against any ST primary source.
> 3. **Every ST FoV figure is a conditioned measurement**, not a hard cone. The VL53L5CX 45°/45°/63° is measured at
>    88 % white reflectance, 1 m, **dark**, 8x8, 14 % sharpener, 15 Hz. Against 17 % grey in 5 klux it is smaller.
> 4. **The HLK-LD2410's "±60°" is a marketing coverage bullet for a human-presence radar**, with no beamwidth, no
>    −3 dB contour and no target condition. It reports no azimuth and detects only moving/micro-moving humans in 0.75 m
>    gates. It cannot serve as the 120° perimeter obstacle sensor this document's tables imply.
> 5. **The VL53L0X "25°" could not be verified** — ST's server did not respond during this check. Do not design on it.
>
> Consequences are stated inline at §3, §6, §7 and §10. Headline: the "27° ring needs 27 sensors, 63° ring needs 12"
> conclusion is wrong; the real parts need **38 VL53L1X** or **16 VL53L5CX**.

---

## 1. Conventions and primitives

| Symbol | Meaning | Value used |
|---|---|---|
| `r` | mount radius — distance from platform centre to the sensor aperture | 175.000 mm |
| `R_c` | circumscribed (corner) radius of the 350 mm square | 247.487 mm |
| `N` | number of sensors in the perimeter ring | 4, 6, 8, 12 |
| `Δ` (Delta) | angular spacing between adjacent boresights, `Δ = 360/N` | derived |
| `Φ` (FoV) | full horizontal field of view of one sensor | 15…180° |
| `θ` | horizontal half-angle, `θ = Φ/2` | derived |
| `Ω` (Omega) | **angular overlap**, `Ω = Φ − Δ` | derived |
| `h` | sensor mounting height above the floor | 100, 200, 400, 800 mm |
| `Φ_v` | full **vertical** field of view | 25, 45, 63, 90° |
| `θ_v` | vertical half-angle, `θ_v = Φ_v/2` | derived |
| `ψ` (psi) | downward cant of the boresight below horizontal | 10…60° |

Platform geometry that matters and is easy to get wrong:

- **Round 350 mm:** every point of the skin is at `r = 175.000 mm`. There is one radius and no corners.
- **Square 350 mm:** the **inscribed** radius (face centre) is `175.000 mm`; the **circumscribed** radius (corner) is
  `175 × √2 = 247.487 mm`; the **diagonal across corners is 494.975 mm**, i.e. **41.4 % wider than the face**.
  The corner protrudes **72.487 mm** beyond the inscribed circle. A perimeter sensing scheme that reasons about
  "a 350 mm robot" and forgets the 495 mm diagonal will clip door frames with its corners.

**Self-occlusion limit.** A sensor mounted flush on a flat face of the square can see, at most, the outward half-plane:
usable half-angle ≤ 90°, i.e. usable `Φ ≤ 180°`, and the ±90° rays graze along the side walls where they are useless.
A sensor mounted flush and tangential on the **round** body sees a clear 180° because a convex circle curves away from its
own tangent plane and touches it at exactly one point. **Round is geometrically superior** for a perimeter ring; the square
only wins if sensors go on 45° corner chamfers, which buys 270° of clear space per sensor but moves the mount radius out
to 247.487 mm.

---

## 2. Ring sizing — why `N = 360/Φ` is wrong

The naive formula treats each sensor as a point at the platform centre emitting a perfect angular sector, and tiles
`360/Φ` of them edge to edge. Three separate things break it.

### 2.1 The parallel-edge failure (pure geometry)

Put two sensors on a ring of radius `r`, spacing `Δ`, each with half-angle `θ`. Sensor A's left edge is a ray leaving A at
`+θ` from A's boresight. Sensor B's right edge leaves B at `−θ` from B's boresight. The angle between those two rays is
`Δ − 2θ = Δ − Φ = −Ω`. When `Ω = 0` the two edges are **exactly parallel** and never intersect at any finite range:
the wedge between them is blind forever, no matter how far you go out. `N = 360/Φ` sets `Δ = Φ`, i.e. `Ω = 0` exactly.
It is the *one value that must be avoided*.

Closure therefore requires **`Φ > Δ`**, i.e. `Φ > 360/N`, i.e.

```
N_min = floor(360/Φ) + 1
```

which equals `ceil(360/Φ)` **except** when `360/Φ` is an integer — precisely the case people reach for.

### 2.2 The datasheet-edge failure

A published FoV is almost always the **half-power / 50 %-detection** contour, not a hard cut-off. At the edge the
received signal is 3 dB down; against a 17 % grey target in bright ambient there may be no detection at all at the nominal
edge angle. Designing to `Ω = 0` designs to the weakest possible part of both beams meeting at the weakest possible
geometry. A useful engineering rule is to discard 5–10° off each edge before doing the arithmetic.

### 2.3 The mechanical-tolerance failure

Boresight azimuth error of ±2° per sensor from PCB placement, connector strain and bracket tolerance is normal. Two
adjacent sensors can therefore be 4° further apart than nominal. With `Ω = 0` nominal, that is a permanently open wedge on
a real unit that passed on the CAD model.

### 2.4 The design formula

```
N = ceil( 360 / (Φ − overlap) )
```

where `overlap` is the deliberate angular margin (recommended 10–20° for consumer ToF/radar edges).

**Table 1 — minimum closed ring** (verbatim script output):

```
   FoV   360/FoV    ceil()  N_min(closed)   Delta=360/Nmin  overlap Omega
    15    24.000        24             25           14.400         0.600
    25    14.400        15             15           24.000         1.000
    27    13.333        14             14           25.714         1.286
    45     8.000         8              9           40.000         5.000
    63     5.714         6              6           60.000         3.000
    65     5.538         6              6           60.000         5.000
    90     4.000         4              5           72.000        18.000
   100     3.600         4              4           90.000        10.000
   120     3.000         3              4           90.000        30.000
   180     2.000         2              3          120.000        60.000
```

Note the three traps: `Φ = 15` needs **25** not 24; `Φ = 45` needs **9** not 8; `Φ = 90` needs **5** not 4;
`Φ = 180` needs **3** not 2.

**Table 2 — `N = ceil(360/(Φ − overlap))`:**

| FoV (°) | ov=0 | ov=5 | ov=10 | ov=15 | ov=20 | ov=30 |
|---|---|---|---|---|---|---|
| 15 | 24 | 36 | 72 | — | — | — |
| 25 | 15 | 18 | 24 | 36 | 72 | — |
| 27 | 14 | 17 | 22 | 30 | 52 | — |
| 45 | 8 | 9 | 11 | 12 | 15 | 24 |
| 63 | 6 | 7 | 7 | 8 | 9 | 11 |
| 65 | 6 | 6 | 7 | 8 | 8 | 11 |
| 90 | 4 | 5 | 5 | 5 | 6 | 6 |
| 100 | 4 | 4 | 4 | 5 | 5 | 6 |
| 120 | 3 | 4 | 4 | 4 | 4 | 4 |
| 180 | 2 | 3 | 3 | 3 | 3 | 3 |

"—" means the overlap exceeds the FoV, so it is impossible. The cost cliff is obvious: a 25° ToF sensor with a sane 15°
overlap needs **36 sensors**; a 100° sensor with the same overlap needs **5**.

---

## 3. The near-field blind wedge — full derivation

This is the single most under-appreciated result. Sensors are on the **perimeter**, not at the centre, so even a ring with
positive overlap is blind in a wedge close to the body.

### 3.1 Derivation

Work in the frame where the bisector between two adjacent sensors lies along `+x`. Then:

- Sensor A sits at `P_A = (r·cos(Δ/2), −r·sin(Δ/2))`, boresight at `−Δ/2`. Its **left** edge leaves at angle `α = θ − Δ/2`.
- Sensor B is the mirror image about the x-axis, so by symmetry the two edges meet **on the x-axis**.

Parametrise A's left edge: `(x, y) = P_A + t·(cos α, sin α)`. Set `y = 0`:

```
−r·sin(Δ/2) + t·sin α = 0        →   t = r·sin(Δ/2) / sin α
x = r·cos(Δ/2) + t·cos α         →   x = r·cos(Δ/2) + r·sin(Δ/2)·cot(α)
```

and since `α = θ − Δ/2 = (Φ − Δ)/2 = Ω/2`:

> **`D_tip = r · [ cos(Δ/2) + sin(Δ/2) · cot(Ω/2) ]`**
> with `Δ = 360/N`, `Ω = Φ − Δ`, and `D_tip = ∞` when `Ω ≤ 0`.

`D_tip` is measured **from the platform centre**. The blind depth beyond the skin of a round platform is
`d_blind = D_tip − r = D_tip − 175 mm`.

**Sanity check 1:** if `Ω = Δ` (that is, `Φ = 2Δ`), then `cot(Ω/2) = cot(Δ/2)` and
`D_tip = r[cos(Δ/2) + sin(Δ/2)·cos(Δ/2)/sin(Δ/2)] = 2r·cos(Δ/2)`. For `N = 8, Φ = 90°`:
`2 × 175 × cos 22.5° = 350 × 0.92388 = 323.4 mm`. The script returns 323.4 mm. ✔

**Sanity check 2:** `N = 4, Φ = 180°` gives `2 × 175 × cos 45° = 350 × 0.70711 = 247.487 mm`. The script returns
247.5 mm — and that is *exactly* the corner radius of the 350 mm square, a coincidence exploited in §4. ✔

### 3.2 The 1/Ω law

For small `Ω` (radians), `cot(Ω/2) ≈ 2/Ω`, so

```
D_tip ≈ r·cos(Δ/2) + 2·r·sin(Δ/2) / Ω
```

**The blind range is inversely proportional to the angular overlap.** Halving the overlap doubles the near-field blind
depth. This is why `Ω = 3°` (six 63° sensors) produces a blind wedge reaching **3.49 m** while `Ω = 30°` (six 90° sensors)
produces one reaching **0.478 m** — a 7.3× difference from a 10× change in overlap.

### 3.3 Numeric tables — ROUND platform, `r = 175.000 mm`

**N = 4 (Δ = 90.000°)**

| FoV (°) | Ω (°) | D_tip (mm) | d_blind (mm) | d_blind (in) | d_blind (ft) |
|---|---|---|---|---|---|
| 15 | −75.000 | OPEN | OPEN | OPEN | OPEN |
| 25 | −65.000 | OPEN | OPEN | OPEN | OPEN |
| 27 | −63.000 | OPEN | OPEN | OPEN | OPEN |
| 45 | −45.000 | OPEN | OPEN | OPEN | OPEN |
| 63 | −27.000 | OPEN | OPEN | OPEN | OPEN |
| 65 | −25.000 | OPEN | OPEN | OPEN | OPEN |
| 90 | 0.000 | OPEN | OPEN | OPEN | OPEN |
| 100 | 10.000 | 1538.1 | 1363.1 | 53.67 | 4.472 |
| 120 | 30.000 | 585.6 | 410.6 | 16.16 | 1.347 |
| 180 | 90.000 | 247.5 | 72.5 | 2.85 | 0.238 |

**N = 6 (Δ = 60.000°)**

| FoV (°) | Ω (°) | D_tip (mm) | d_blind (mm) | d_blind (in) | d_blind (ft) |
|---|---|---|---|---|---|
| 15 | −45.000 | OPEN | OPEN | OPEN | OPEN |
| 25 | −35.000 | OPEN | OPEN | OPEN | OPEN |
| 27 | −33.000 | OPEN | OPEN | OPEN | OPEN |
| 45 | −15.000 | OPEN | OPEN | OPEN | OPEN |
| 63 | 3.000 | 3493.0 | 3318.0 | 130.63 | 10.886 |
| 65 | 5.000 | 2155.6 | 1980.6 | 77.98 | 6.498 |
| 90 | 30.000 | 478.1 | 303.1 | 11.93 | 0.994 |
| 100 | 40.000 | 392.0 | 217.0 | 8.54 | 0.712 |
| 120 | 60.000 | 303.1 | 128.1 | 5.04 | 0.420 |
| 180 | 120.000 | 202.1 | 27.1 | 1.07 | 0.089 |

**N = 8 (Δ = 45.000°)**

| FoV (°) | Ω (°) | D_tip (mm) | d_blind (mm) | d_blind (in) | d_blind (ft) |
|---|---|---|---|---|---|
| 15 | −30.000 | OPEN | OPEN | OPEN | OPEN |
| 25 | −20.000 | OPEN | OPEN | OPEN | OPEN |
| 27 | −18.000 | OPEN | OPEN | OPEN | OPEN |
| 45 | 0.000 | OPEN | OPEN | OPEN | OPEN |
| 63 | 18.000 | 584.5 | 409.5 | 16.12 | 1.344 |
| 65 | 20.000 | 541.5 | 366.5 | 14.43 | 1.202 |
| 90 | 45.000 | 323.4 | 148.4 | 5.84 | 0.487 |
| 100 | 55.000 | 290.3 | 115.3 | 4.54 | 0.378 |
| 120 | 75.000 | 249.0 | 74.0 | 2.91 | 0.243 |
| 180 | 135.000 | 189.4 | 14.4 | 0.57 | 0.047 |

**N = 12 (Δ = 30.000°)**

| FoV (°) | Ω (°) | D_tip (mm) | d_blind (mm) | d_blind (in) | d_blind (ft) |
|---|---|---|---|---|---|
| 15 | −15.000 | OPEN | OPEN | OPEN | OPEN |
| 25 | −5.000 | OPEN | OPEN | OPEN | OPEN |
| 27 | −3.000 | OPEN | OPEN | OPEN | OPEN |
| 45 | 15.000 | 513.1 | 338.1 | 13.31 | 1.109 |
| 63 | 33.000 | 321.9 | 146.9 | 5.79 | 0.482 |
| 65 | 35.000 | 312.7 | 137.7 | 5.42 | 0.452 |
| 90 | 60.000 | 247.5 | 72.5 | 2.85 | 0.238 |
| 100 | 70.000 | 233.7 | 58.7 | 2.31 | 0.193 |
| 120 | 90.000 | 214.3 | 39.3 | 1.55 | 0.129 |
| 180 | 150.000 | 181.2 | 6.2 | 0.24 | 0.020 |

**Read this table the right way.** An 8-ring of 27° ToF sensors — the classic "eight VL53L1X around the base" layout —
is `Ω = −18°`. **It has eight permanently blind wedges open to infinite range.** It is not a perimeter ring; it is eight
independent bumper pokers. An 8-ring of 63° array sensors closes only at 584 mm from centre (409 mm past the skin) — a
cat can sit 400 mm from the robot, dead on a wedge bisector, and be completely invisible.

> **Correction — the two rows people will actually build are worse than the 27° and 63° rows above.** Those two rows use
> the *marketing* FoV. Both ST parts publish a **diagonal** or a separately-measured horizontal number (see §6):
>
> - **VL53L1X**: the datasheet figure is **27° diagonal** (DS DocID031281 Rev 3, Table 1), so the horizontal FoV is
>   **19.270°**. An 8-ring is `Ω = −25.73°`, not −18°. The ring does not close at **any N below 19**
>   (`N_min = floor(360/19.270)+1 = 19`), and even N = 19 puts the wedge tip at **10 418.8 mm** from centre. N = 20
>   gives 2 643.8 mm. **The smallest VL53L1X ring that bounds the tip within 350 mm of centre is N = 38 (343.0 mm).**
> - **VL53L5CX**: the datasheet horizontal figure is **45.0°** (DS13754 Rev 2, Table 2, at 88 % white / 1 m / dark /
>   8x8 / 14 % sharpener / 15 Hz), not 63°. An 8-ring is `Ω = 0` — **OPEN, infinite blind wedges**, the exact failure
>   §2.1 warns about. It is not 584 mm; it never closes. N = 9 is the first closed ring; **N = 12 closes at 513.1 mm
>   from centre (338.1 mm past the skin)**, and **N = 16 is the smallest that bounds the tip within 350 mm (343.3 mm).**

**Table 12 — smallest N that bounds the wedge tip** (round platform):

| FoV (°) | tip ≤ 247 mm | tip ≤ 350 mm | tip ≤ 500 mm | tip ≤ 1000 mm |
|---|---|---|---|---|
| 15 | N/A (>48) | N=48 (349 mm) | N=37 (497 mm) | N=30 (873 mm) |
| 25 | N/A (>48) | N=29 (346 mm) | N=23 (465 mm) | N=18 (868 mm) |
| 27 | N=46 (245 mm) | N=27 (343 mm) | N=21 (476 mm) | N=17 (804 mm) |
| 45 | N=27 (245 mm) | N=16 (343 mm) | N=13 (445 mm) | N=10 (854 mm) |
| 63 | N=19 (244 mm) | N=12 (322 mm) | N=9 (459 mm) | N=7 (907 mm) |
| 65 | N=18 (246 mm) | N=11 (338 mm) | N=9 (434 mm) | N=7 (796 mm) |
| 90 | N=13 (239 mm) | N=8 (323 mm) | N=6 (478 mm) | N=5 (791 mm) |
| 100 | N=11 (242 mm) | N=7 (326 mm) | N=6 (392 mm) | N=5 (554 mm) |
| 120 | N=9 (236 mm) | N=6 (303 mm) | N=5 (373 mm) | N=4 (586 mm) |
| 180 | N=5 (216 mm) | N=3 (350 mm) | N=3 (350 mm) | N=3 (350 mm) |

If the acceptance criterion is "nothing bigger than a cat can hide within 350 mm of the robot centre" then a 27° ToF ring
needs **27 sensors** and a 63° array ring needs **12**. That is the honest cost of the geometry.

**But those are the wrong two rows for real parts.** Table 12 is indexed by *horizontal* FoV, and 27° and 63° are the
*diagonal* headline numbers of the VL53L1X and VL53L5CX. Read the table at the datasheet horizontal FoV instead:

| part | datasheet FoV as published | horizontal FoV to size the ring with | smallest N with tip ≤ 350 mm |
|---|---|---|---|
| VL53L1X | 27° **diagonal**, ROI-reducible to 20°/15° (DS DocID031281 Rev 3, Tables 1 and 9) | 19.270° | **N = 38** (343.0 mm) |
| VL53L5CX | 45° H / 45° V / 63° diagonal (DS13754 Rev 2, Table 2; 88 % white, 1 m, dark, 8x8, 14 % sharpener, 15 Hz) | 45.0° | **N = 16** (343.3 mm) |

**That is the honest cost of the geometry: 38 VL53L1X, or 16 VL53L5CX — not 27 and 12.** Both are far past the point
where a ring of single-point or single-array ToF modules is the right architecture.

---

## 4. Corner effects — the SQUARE 350 mm platform

### 4.1 Four sensors on the face centres (`r = 175.000`, boresights 0/90/180/270°)

The wedge bisector points **exactly at a corner**, which sits at 247.487 mm.

| FoV (°) | Ω (°) | D_tip (mm) | D_tip − 247.487 (mm) | verdict |
|---|---|---|---|---|
| 15 | −75.000 | OPEN | — | corner never covered |
| 25 | −65.000 | OPEN | — | corner never covered |
| 27 | −63.000 | OPEN | — | corner never covered |
| 45 | −45.000 | OPEN | — | corner never covered |
| 63 | −27.000 | OPEN | — | corner never covered |
| 65 | −25.000 | OPEN | — | corner never covered |
| 90 | 0.000 | OPEN | — | corner never covered |
| 100 | 10.000 | 1538.140 | 1290.653 | corner blind to 1290.7 mm past the corner |
| 120 | 30.000 | 585.561 | 338.074 | corner blind to 338.1 mm past the corner |
| 180 | 90.000 | 247.487 | 0.000 | **wedge tip lands exactly on the corner** |

The 180° row is a genuinely elegant result: four flush 180° sensors on the face centres of a 350 mm square produce a
coverage boundary whose four cusps land **precisely on the four corner points**. Every point strictly outside the square
is seen. Nothing less than 180° achieves that with four sensors.

### 4.2 Four sensors on the corners (`r = 247.487`, boresights 45/135/225/315°)

Now the blind bisector points at a **face centre**, whose skin is only 175 mm out.

| FoV (°) | Ω (°) | D_tip (mm) | blind depth past face skin (mm) |
|---|---|---|---|
| 15–90 | ≤ 0 | OPEN | OPEN |
| 100 | 10.000 | 2175.259 | 2000.259 |
| 120 | 30.000 | 828.109 | 653.109 |
| 180 | 90.000 | 350.000 | 175.000 |

Corner mounting is **strictly worse for a square** at equal FoV: the larger mount radius `247.487` multiplies the whole
`D_tip` expression. Four 120° sensors on faces leave a 338 mm hole at the corners; the same four on corners leave a
**653 mm** hole at the face midpoints — and the face midpoint is where the robot actually drives into things.

### 4.3 Eight sensors, alternating face and corner (Δ = 45°, radii alternate 175.000 / 247.487)

Solved by explicit ray–ray intersection because the closed form assumes equal radii.

| FoV (°) | Ω (°) | tip dist from centre (mm) | tip bearing (°) | tip clear of square skin (mm) |
|---|---|---|---|---|
| 15 | −30.000 | OPEN | — | — |
| 25 | −20.000 | OPEN | — | — |
| 27 | −18.000 | OPEN | — | — |
| 45 | 0.000 | OPEN | — | — |
| 63 | 18.000 | 705.824 | 24.06 | 514.179 |
| 65 | 20.000 | 653.926 | 24.23 | 462.016 |
| 90 | 45.000 | 391.312 | 26.57 | 195.656 |
| 100 | 55.000 | 351.850 | 27.60 | 154.371 |
| 120 | 75.000 | 303.109 | 30.00 | 101.036 |
| 180 | 135.000 | OPEN | — | — |

Two things to notice. First, the tip **bearing is not 22.5°** — it drifts to 24–30° because the corner sensor is further
out, so the wedge is asymmetric and skewed toward the face sensor. Second, the 180° row is OPEN: a flush 180° sensor on a
face centre cannot see past its own side wall, so the mixed 8-ring cannot close with flat 180° modules. Either chamfer
the corners or stay at ≤ 120°.

**Practical conclusion for the square:** mount on **face centres**, use `Φ ≥ 120°`, and treat the four corners as
mechanically protected (bumper, compliant skirt, or a 45° chamfer that pulls `R_c` down toward 175 mm). Equivalently —
**make the robot round**. A 350 mm round platform removes the 72.487 mm corner protrusion and the whole class of problem.

---

## 5. Beam footprint width at range

```
w = 2 · d · tan(Φ/2)
```

Worked example, `Φ = 63°` at `d = 1524 mm` (5 ft): `2 × 1524 × tan(31.5°) = 3048 × 0.61280 = 1867.8 mm ≈ 1868 mm = 73.5 in`.

| FoV (°) | 1 ft (305 mm) | 3 ft (914 mm) | 5 ft (1524 mm) | 8 ft (2438 mm) | 10 ft (3048 mm) |
|---|---|---|---|---|---|
| 15 | 80 mm / 3.2 in | 241 mm / 9.5 in | 401 mm / 15.8 in | 642 mm / 25.3 in | 803 mm / 31.6 in |
| 25 | 135 mm / 5.3 in | 405 mm / 16.0 in | 676 mm / 26.6 in | 1081 mm / 42.6 in | 1351 mm / 53.2 in |
| 27 | 146 mm / 5.8 in | 439 mm / 17.3 in | 732 mm / 28.8 in | 1171 mm / 46.1 in | 1464 mm / 57.6 in |
| 45 | 253 mm / 9.9 in | 757 mm / 29.8 in | 1263 mm / 49.7 in | 2020 mm / 79.5 in | 2525 mm / 99.4 in |
| 63 | 374 mm / 14.7 in | 1120 mm / 44.1 in | 1868 mm / 73.5 in | 2988 mm / 117.6 in | 3736 mm / 147.1 in |
| 65 | 389 mm / 15.3 in | 1165 mm / 45.8 in | 1942 mm / 76.4 in | 3106 mm / 122.3 in | 3884 mm / 152.9 in |
| 90 | 610 mm / 24.0 in | 1828 mm / 72.0 in | 3048 mm / 120.0 in | 4876 mm / 192.0 in | 6096 mm / 240.0 in |
| 100 | 727 mm / 28.6 in | 2179 mm / 85.8 in | 3632 mm / 143.0 in | 5811 mm / 228.8 in | 7265 mm / 286.0 in |
| 120 | 1057 mm / 41.6 in | 3166 mm / 124.7 in | 5279 mm / 207.8 in | 8445 mm / 332.5 in | 10559 mm / 415.7 in |
| 180 | infinite | infinite | infinite | infinite | infinite |

Same widths in **feet**:

| FoV (°) | 1 ft | 3 ft | 5 ft | 8 ft | 10 ft |
|---|---|---|---|---|---|
| 15 | 0.26 | 0.79 | 1.32 | 2.11 | 2.63 |
| 25 | 0.44 | 1.33 | 2.22 | 3.55 | 4.43 |
| 27 | 0.48 | 1.44 | 2.40 | 3.84 | 4.80 |
| 45 | 0.83 | 2.48 | 4.14 | 6.63 | 8.28 |
| 63 | 1.23 | 3.68 | 6.13 | 9.80 | 12.26 |
| 65 | 1.27 | 3.82 | 6.37 | 10.19 | 12.74 |
| 90 | 2.00 | 6.00 | 10.00 | 16.00 | 20.00 |
| 100 | 2.39 | 7.15 | 11.92 | 19.06 | 23.84 |
| 120 | 3.47 | 10.39 | 17.32 | 27.71 | 34.64 |

**The discrimination consequence.** A single-zone wide sensor returns one number for the whole footprint. At 5 ft a 90°
sensor is integrating over a **3048 mm wide** swath — a human, a cat and a sofa are all inside it simultaneously. Wide FoV
buys coverage and destroys localisation. That is why the human/pet/inanimate question (task item *d*) cannot be answered
by a ring of single-zone wide sensors at any N: it needs **angular resolution inside** the FoV (a zoned array, a radar
that reports azimuth per target, or a camera), not more sensors around the ring.

**Table 16 — how many degrees a target subtends** (`α = 2·atan(W/2d)`):

| target | W (mm) | 1 ft | 3 ft | 5 ft | 8 ft | 10 ft |
|---|---|---|---|---|---|---|
| human torso | 450 | 72.83° | 27.66° | 16.80° | 10.55° | 8.44° |
| human leg | 150 | 27.63° | 9.38° | 5.63° | 3.52° | 2.82° |
| cat body length | 450 | 72.83° | 27.66° | 16.80° | 10.55° | 8.44° |
| cat body height | 200 | 36.31° | 12.49° | 7.51° | 4.70° | 3.76° |
| chair leg | 35 | 6.57° | 2.19° | 1.32° | 0.82° | 0.66° |
| table edge | 25 | 4.69° | 1.57° | 0.94° | 0.59° | 0.47° |

A **chair leg at 5 ft subtends 1.32°**. To resolve it as an object rather than as a weak average you need angular cells
of roughly that size. **Table 17**, an 8×8 array with `Φ_h = 45°`, gives a per-zone pitch of `45/8 = 5.625°`:

| range | zone width (mm) | zone width (in) |
|---|---|---|
| 1 ft | 30.0 | 1.18 |
| 3 ft | 89.8 | 3.54 |
| 5 ft | 149.7 | 5.90 |
| 8 ft | 239.5 | 9.43 |
| 10 ft | 299.5 | 11.79 |

So an 8×8 array resolves a 150 mm human leg into roughly one zone at 5 ft — detectable, not classifiable.

---

## 6. The diagonal-FoV trap

Square zone arrays quote a **diagonal** FoV. Under a pinhole projection the half-diagonal on the image plane is `√2 ×`
the half-width, so

```
tan(Φ_d/2) = √2 · tan(Φ_h/2)    →    Φ_h = 2·atan( tan(Φ_d/2) / √2 )
```

**Not** `Φ_d/√2`, which is only a small-angle approximation.

| Φ_d (diag, °) | true Φ_h = Φ_v (°) | naive Φ_d/√2 (°) | error (°) |
|---|---|---|---|
| 25.0 | 17.819 | 17.678 | 0.141 |
| 27.0 | 19.270 | 19.092 | 0.178 |
| 45.0 | 32.650 | 31.820 | 0.830 |
| 63.0 | 46.856 | 44.548 | 2.308 |
| 65.0 | 48.501 | 45.962 | 2.539 |
| 90.0 | 70.529 | 63.640 | 6.889 |
| 100.0 | 80.241 | 70.711 | 9.531 |
| 120.0 | 101.537 | 84.853 | 16.684 |

**Ring-size penalty for using the diagonal number:**

| Φ_d (°) | Φ_h (°) | N from Φ_d | N from Φ_h | extra sensors |
|---|---|---|---|---|
| 25.0 | 17.819 | 15 | 21 | +6 |
| 27.0 | 19.270 | 14 | 19 | +5 |
| 45.0 | 32.650 | 9 | 12 | +3 |
| 63.0 | 46.856 | 6 | 8 | +2 |
| 65.0 | 48.501 | 6 | 8 | +2 |
| 90.0 | 70.529 | 5 | 6 | +1 |
| 100.0 | 80.241 | 4 | 5 | +1 |
| 120.0 | 101.537 | 4 | 4 | 0 |

**Footnote — this table is the pinhole prediction, and for the two ST parts the datasheet beats it.** For the VL53L5CX,
ST publishes the horizontal FoV directly as **45.0°** (DS13754 Rev 2 Table 2), not the 46.856° the pinhole row predicts,
so the true penalty is **6 → 9 sensors, +3**, not +2. For the VL53L1X the datasheet's 27° is already labelled *diagonal*,
so the pinhole conversion is the right one to apply and Φ_h = **19.270°** → **N = 19**, not 14.

The ST VL53L5CX is the concrete case, and it does **not** need the pinhole conversion at all, because ST publishes the
horizontal number directly. **[VL53L5CX datasheet DS13754 Rev 2 (Aug 2021), Table 2 "FoV angles"](https://www.st.com/resource/en/datasheet/vl53l5cx.pdf)**:

| | Horizontal | Vertical | Diagonal |
|---|---|---|---|
| **Detection volume** (the usable system FoV) | **45°** | **45°** | **63°** |
| Collector exclusion zone (cover-window opening) | 55.5° | 61° | 82° |

**Measurement condition, quoted from the datasheet note — without it the number is meaningless:** "*measured with a
white 88 % reflectance perpendicular target in full FoV, located at 1 m from the sensor, without ambient light (dark
conditions), with an 8x8 resolution and 14 % sharpener (default value), in Continuous mode at 15 Hz*". The same note
adds that "*detection volume depends on the environment and sensor configuration as well as target distance,
reflectance, ambient light level, sensor resolution, sharpener, ranging mode, and integration time*". Against a 17 %
grey target in 5 klux the usable angular extent is smaller than 45°, not equal to it.

So **ST's own horizontal figure is 45.0°, not the 46.856° the pinhole conversion predicts from 63° diagonal.** ST's
45°/45°/63° triple is not self-consistent under a pinhole model (45°×45° square implies a 60.7° diagonal), so use the
measured 45° horizontal and treat the 63° diagonal as the marketing headline. UM2884 does not contradict this — its own
text says "*8x8 zones with a wide 63 ° diagonal field of view (FoV)*", i.e. it repeats the diagonal, it does not state
45°×45°. **A ring designed on "63°" needs 9 sensors, not 6 and not 8** (`floor(360/45)+1 = 9`).

A "65° diagonal" figure could not be confirmed against any ST primary source in this check (the ST product page did not
respond); the datasheet says 63°. **Confidence: 45°/45°/63° datasheet-verified with condition; 65° UNVERIFIED — do not
design on it.**

Reference FoV attributions used in this lane — **corrected against the primary datasheets**:

| part | what the primary source actually says | usable **horizontal** FoV for ring sizing | confidence |
|---|---|---|---|
| [VL53L0X](https://www.st.com/resource/en/datasheet/vl53l0x.pdf) | 25° "system FoV" (ST DS) — ST does not label it H or diagonal | 25° if system/full; **~18° if it is the diagonal** | **UNVERIFIED in this check — ST server did not respond. Do not design on 25° until Table "FoV" of the DS is read.** |
| [VL53L1X](https://www.st.com/resource/en/datasheet/vl53l1x.pdf) | DS DocID031281 Rev 3, Table 1: "Receiver Field Of View **(diagonal FOV)** Programmable from 15 to 27 degrees"; Table 9: diagonal FoV 27°/20°/15° for 16x16/8x8/4x4 ROI. Test condition: target covers full FoV, long distance mode, 100 ms budget, no cover glass, dark = no 940 nm ±30 nm IR | **19.27°** (= 2·atan(tan(13.5°)/√2)) | datasheet-verified; **the 27° is DIAGONAL, not horizontal** |
| [VL53L5CX](https://www.st.com/resource/en/datasheet/vl53l5cx.pdf) | DS13754 Rev 2, Table 2: detection volume 45° H / 45° V / 63° diagonal, measured at 88 % white, 1 m, dark, 8x8, 14 % sharpener, 15 Hz | **45.0°** | datasheet-verified **with condition** |
| [HLK-LD2410](https://www.hlktech.net/index.php?id=988) | Manual V1.03 §2.1 feature bullet: "Large detection angle, coverage up to ±60 degrees". No beamwidth, no −3 dB contour, no target RCS, no condition of any kind | ±60° is **not** a usable beam spec | **MISLEADING as used** — marketing coverage bullet for a *presence* radar that only reports moving/micro-moving **human** targets in 0.75 m distance gates. It does not range inanimate obstacles and reports no azimuth. It cannot be a perimeter collision sensor at any N. |
| [HLK-LD2450](https://www.hlktech.net/index.php?id=1157) | Vendor page: "Azimuth angle ±60°, pitch angle ±35°" — no datasheet condition published | ±60° azimuth, nominal | vendor-page-verified only; **no measurement condition stated** |

---

## 7. Vertical coverage — the cat problem (the most important result)

Level boresight, half-angle `θ_v`. The lower beam edge descends at `θ_v`, so:

```
z_lo(d) = h − d·tan(θ_v)          lowest height visible at range d
z_hi(d) = h + d·tan(θ_v)          highest height visible at range d
d_floor = h / tan(θ_v)            nearest range at which the beam first strikes the floor
```

A 200 mm cat standing on the floor occupies `0…200 mm`. It is visible iff `[max(0, z_lo), min(200, z_hi)]` is non-empty,
i.e. iff `z_lo < 200`, i.e. iff

```
d > (h − 200) / tan(θ_v)          (always true when h ≤ 200 mm)
```

**Nearest floor strike `d_floor = h/tan(θ_v)`:**

| h (mm) | Φ_v = 25° | Φ_v = 45° | Φ_v = 63° | Φ_v = 90° |
|---|---|---|---|---|
| 100 | 451.1 mm (17.76 in) | 241.4 mm (9.50 in) | 163.2 mm (6.42 in) | 100.0 mm (3.94 in) |
| 200 | 902.1 mm (35.52 in) | 482.8 mm (19.01 in) | 326.4 mm (12.85 in) | 200.0 mm (7.87 in) |
| 400 | 1804.3 mm (71.03 in) | 965.7 mm (38.02 in) | 652.7 mm (25.70 in) | 400.0 mm (15.75 in) |
| 800 | 3608.6 mm (142.07 in) | 1931.4 mm (76.04 in) | 1305.5 mm (51.40 in) | 800.0 mm (31.50 in) |

**Cat-in-beam, band of the 200 mm cat actually illuminated** (verbatim script output):

**h = 100 mm**

| Φ_v | 1 ft | 3 ft | 5 ft | 8 ft | 10 ft |
|---|---|---|---|---|---|
| 25 | 135 mm 68% part | 200 mm 100% FULL | 200 mm 100% FULL | 200 mm 100% FULL | 200 mm 100% FULL |
| 45 | 200 mm 100% FULL | 200 mm 100% FULL | 200 mm 100% FULL | 200 mm 100% FULL | 200 mm 100% FULL |
| 63 | 200 mm 100% FULL | 200 mm 100% FULL | 200 mm 100% FULL | 200 mm 100% FULL | 200 mm 100% FULL |
| 90 | 200 mm 100% FULL | 200 mm 100% FULL | 200 mm 100% FULL | 200 mm 100% FULL | 200 mm 100% FULL |

**h = 200 mm**

| Φ_v | 1 ft | 3 ft | 5 ft | 8 ft | 10 ft |
|---|---|---|---|---|---|
| 25 | 68 mm 34% part | 200 mm 100% FULL | 200 mm 100% FULL | 200 mm 100% FULL | 200 mm 100% FULL |
| 45 | 126 mm 63% part | 200 mm 100% FULL | 200 mm 100% FULL | 200 mm 100% FULL | 200 mm 100% FULL |
| 63 | 187 mm 93% part | 200 mm 100% FULL | 200 mm 100% FULL | 200 mm 100% FULL | 200 mm 100% FULL |
| 90 | 200 mm 100% FULL | 200 mm 100% FULL | 200 mm 100% FULL | 200 mm 100% FULL | 200 mm 100% FULL |

**h = 400 mm**

| Φ_v | 1 ft | 3 ft | 5 ft | 8 ft | 10 ft |
|---|---|---|---|---|---|
| 25 | 0 mm 0% **MISS** | 3 mm 1% part | 138 mm 69% part | 200 mm 100% FULL | 200 mm 100% FULL |
| 45 | 0 mm 0% **MISS** | 179 mm 89% part | 200 mm 100% FULL | 200 mm 100% FULL | 200 mm 100% FULL |
| 63 | 0 mm 0% **MISS** | 200 mm 100% FULL | 200 mm 100% FULL | 200 mm 100% FULL | 200 mm 100% FULL |
| 90 | 105 mm 52% part | 200 mm 100% FULL | 200 mm 100% FULL | 200 mm 100% FULL | 200 mm 100% FULL |

**h = 800 mm**

| Φ_v | 1 ft | 3 ft | 5 ft | 8 ft | 10 ft |
|---|---|---|---|---|---|
| 25 | 0 mm 0% **MISS** | 0 mm 0% **MISS** | 0 mm 0% **MISS** | 0 mm 0% **MISS** | 76 mm 38% part |
| 45 | 0 mm 0% **MISS** | 0 mm 0% **MISS** | 31 mm 16% part | 200 mm 100% FULL | 200 mm 100% FULL |
| 63 | 0 mm 0% **MISS** | 0 mm 0% **MISS** | 200 mm 100% FULL | 200 mm 100% FULL | 200 mm 100% FULL |
| 90 | 0 mm 0% **MISS** | 200 mm 100% FULL | 200 mm 100% FULL | 200 mm 100% FULL | 200 mm 100% FULL |

**This is the headline result of the whole lane.** A level perimeter ring at `h = 800 mm` with a 25° vertical FoV — the
obvious "put the sensors near the top where the wiring is easy" choice — **cannot see a cat anywhere inside 10 ft**. It
first grazes the cat's head at 10 ft, catching 38 % of its body. At every distance the robot could actually collide with
the cat, the cat is below the beam. Conversely, `h = 100 mm` with `Φ_v = 90°` puts the beam into the floor at **100 mm**:
past 100 mm the sensor is returning floor, not free space, and every reading is clutter.

**Table 7 — lowest visible height `z_lo(d) = h − d·tan(Φ_v/2)`** (negative = beam already below floor level):

| h (mm) | Φ_v (°) | z_lo @1 ft | z_lo @3 ft | z_lo @5 ft | z_lo @8 ft | z_lo @10 ft |
|---|---|---|---|---|---|---|
| 100 | 25 | 32 mm | −103 mm | −238 mm | −440 mm | −576 mm |
| 100 | 45 | −26 mm | −279 mm | −531 mm | −910 mm | −1163 mm |
| 100 | 63 | −87 mm | −460 mm | −834 mm | −1394 mm | −1768 mm |
| 100 | 90 | −205 mm | −814 mm | −1424 mm | −2338 mm | −2948 mm |
| 200 | 25 | 132 mm | −3 mm | −138 mm | −340 mm | −476 mm |
| 200 | 45 | 74 mm | −179 mm | −431 mm | −810 mm | −1063 mm |
| 200 | 63 | 13 mm | −360 mm | −734 mm | −1294 mm | −1668 mm |
| 200 | 90 | −105 mm | −714 mm | −1324 mm | −2238 mm | −2848 mm |
| 400 | 25 | 332 mm | 197 mm | 62 mm | −140 mm | −276 mm |
| 400 | 45 | 274 mm | 21 mm | −231 mm | −610 mm | −863 mm |
| 400 | 63 | 213 mm | −160 mm | −534 mm | −1094 mm | −1468 mm |
| 400 | 90 | 95 mm | −514 mm | −1124 mm | −2038 mm | −2648 mm |
| 800 | 25 | 732 mm | 597 mm | 462 mm | 260 mm | 124 mm |
| 800 | 45 | 674 mm | 421 mm | 169 mm | −210 mm | −463 mm |
| 800 | 63 | 613 mm | 240 mm | −134 mm | −694 mm | −1068 mm |
| 800 | 90 | 495 mm | −114 mm | −724 mm | −1638 mm | −2248 mm |

The `h = 800, Φ_v = 25` row is the cat-blind row in full: the beam floor never gets below 124 mm inside 10 ft.

**The sweet spot is `h ≈ 200 mm` with `Φ_v ≥ 45°`.** At `h = 200`:
- the sensor is level with the cat's head, so `z_lo < 200` at *every* range and the cat is never below the beam;
- a 45° vertical FoV puts first floor strike at **482.8 mm**, i.e. the first half metre is clean free-space measurement;
- a standing human (1500–1900 mm) is inside the upper half of the beam from ~1.5 m outward with `Φ_v = 63°`
  (`z_hi(1524) = 200 + 1524·tan 31.5° = 200 + 934 = 1134 mm` — only the legs and hips, which is enough to detect
  but not enough to classify by height).

> **No part in this lane has a 63° vertical FoV.** The `Φ_v = 63°` column is a hypothetical. The VL53L5CX's published
> vertical FoV is **45°** (DS13754 Rev 2, Table 2 — 45° H / 45° V / 63° diagonal), so the row that actually applies to
> it is `Φ_v = 45°`: `z_hi(1524) = 200 + 1524·tan 22.5° = 200 + 631 = 831 mm`, and first floor strike at
> **482.8 mm**. A standing human is seen only below knee-to-thigh height at 5 ft, which strengthens rather than weakens
> the two-tier conclusion below.

**The two-tier consequence.** One level ring cannot simultaneously (i) see a 200 mm cat at 300 mm and (ii) see a standing
human's torso at 3 m, unless `Φ_v` is enormous. The geometry forces **two tiers**: a low tier at `h ≈ 150–250 mm` with
wide `Φ_v` for obstacles, pets and the floor plane; and a high tier at `h ≈ 900–1100 mm` — presence radar or a camera —
for human torso detection and classification. Tier separation is what makes item (d), human-vs-pet discrimination, even
tractable: *height above floor* is the single most reliable discriminator available, and you only get it from two tiers or
from a vertically-resolved array.

### 7.1 Down-tilt to reach the cat from a high mount

If a high mount is forced, the boresight must be canted down by `ψ`. Angle below horizontal to the cat's head is
`a_top = atan((h−200)/d)`; to its feet, `a_feet = atan(h/d)`. Ideal `ψ = (a_top + a_feet)/2`, and the minimum vertical FoV
to hold the whole cat is `a_feet − a_top`.

| h (mm) | range | a_top (°) | a_feet (°) | ideal ψ (°) | min Φ_v needed (°) |
|---|---|---|---|---|---|
| 100 | 1 ft | −18.153 | 18.153 | 0.000 | 36.305 |
| 100 | 3 ft | −6.244 | 6.244 | 0.000 | 12.488 |
| 100 | 10 ft | −1.879 | 1.879 | 0.000 | 3.758 |
| 200 | 1 ft | 0.000 | 33.254 | 16.627 | 33.254 |
| 200 | 3 ft | 0.000 | 12.343 | 6.171 | 12.343 |
| 200 | 10 ft | 0.000 | 3.754 | 1.877 | 3.754 |
| 400 | 1 ft | 33.254 | 52.674 | 42.964 | 19.420 |
| 400 | 3 ft | 12.343 | 23.636 | 17.989 | 11.293 |
| 400 | 5 ft | 7.476 | 14.707 | 11.091 | 7.230 |
| 400 | 8 ft | 4.690 | 9.317 | 7.004 | 4.628 |
| 400 | 10 ft | 3.754 | 7.476 | 5.615 | 3.722 |
| 800 | 1 ft | 63.054 | 69.131 | 66.092 | 6.076 |
| 800 | 3 ft | 33.283 | 41.195 | 37.239 | 7.912 |
| 800 | 5 ft | 21.490 | 27.697 | 24.593 | 6.207 |
| 800 | 8 ft | 13.826 | 18.167 | 15.996 | 4.341 |
| 800 | 10 ft | 11.136 | 14.707 | 12.921 | 3.570 |

Read the `h = 800` block carefully: the ideal tilt swings from **66.1°** at 1 ft to **12.9°** at 10 ft. **No single fixed
tilt covers both.** To cover 1 ft through 10 ft from `h = 800 mm` you need `Φ_v ≥ 66.1 + 6.1/2 − (12.9 − 3.6/2) ≈ 58°`
of vertical FoV aimed down at about `ψ ≈ 35°` — and at that tilt the beam is buried in the floor beyond
`800/tan(35 − 29) ≈ 7.6 m`, drowning the far field in floor return. A high level ring simply is not a pet sensor.

---

## 8. Step and drop-off — downward-canted cliff sensors

Sensor at height `h`, canted `ψ` below horizontal, vertical half-angle `θ_v`:

```
L    = h / tan(ψ)                 horizontal look-ahead of the boresight
R_f  = h / sin(ψ)                 flat-floor range along the boresight
ΔR   = D / sin(ψ)                 range jump over a drop of depth D
stripe: h/tan(ψ + θ_v)  …  h/tan(ψ − θ_v)     illuminated floor band (infinite if ψ ≤ θ_v)
```

`D = 180 mm` is used as a representative residential riser; the
[IRC R311.7.5.1](https://www.cityofboise.org/media/14405/437-treads-risers_march-2022.pdf) maximum is **7¾ in =
196.85 mm** with a 10 in (254 mm) minimum tread (**confidence: code-document-verified**). Because `ΔR` is linear in `D`,
scale the table by 1.0936 for the code maximum. With `θ_v = 12.5°`:

**h = 100 mm**

| ψ (°) | L (mm) | L (in) | R_f (mm) | ΔR for 180 mm drop (mm) | stripe near (mm) | stripe far (mm) |
|---|---|---|---|---|---|---|
| 10 | 567.1 | 22.33 | 575.9 | 1036.6 | 241.4 | infinite |
| 15 | 373.2 | 14.69 | 386.4 | 695.5 | 192.1 | 2290 |
| 20 | 274.7 | 10.82 | 292.4 | 526.3 | 157.0 | 760 |
| 30 | 173.2 | 6.82 | 200.0 | 360.0 | 109.1 | 317 |
| 45 | 100.0 | 3.94 | 141.4 | 254.6 | 63.7 | 157 |
| 60 | 57.7 | 2.27 | 115.5 | 207.8 | 31.5 | 92 |

**h = 200 mm**

| ψ (°) | L (mm) | L (in) | R_f (mm) | ΔR (mm) | stripe near (mm) | stripe far (mm) |
|---|---|---|---|---|---|---|
| 10 | 1134.3 | 44.66 | 1151.8 | 1036.6 | 482.8 | infinite |
| 15 | 746.4 | 29.39 | 772.7 | 695.5 | 384.2 | 4581 |
| 20 | 549.5 | 21.63 | 584.8 | 526.3 | 313.9 | 1519 |
| 30 | 346.4 | 13.64 | 400.0 | 360.0 | 218.3 | 634 |
| 45 | 200.0 | 7.87 | 282.8 | 254.6 | 127.4 | 314 |
| 60 | 115.5 | 4.55 | 230.9 | 207.8 | 63.1 | 183 |

**h = 400 mm**

| ψ (°) | L (mm) | L (in) | R_f (mm) | ΔR (mm) | stripe near (mm) | stripe far (mm) |
|---|---|---|---|---|---|---|
| 10 | 2268.5 | 89.31 | 2303.5 | 1036.6 | 965.7 | infinite |
| 15 | 1492.8 | 58.77 | 1545.5 | 695.5 | 768.4 | 9162 |
| 20 | 1099.0 | 43.27 | 1169.5 | 526.3 | 627.9 | 3038 |
| 30 | 692.8 | 27.28 | 800.0 | 360.0 | 436.5 | 1269 |
| 45 | 400.0 | 15.75 | 565.7 | 254.6 | 254.8 | 628 |
| 60 | 230.9 | 9.09 | 461.9 | 207.8 | 126.1 | 367 |

**h = 800 mm**

| ψ (°) | L (mm) | L (in) | R_f (mm) | ΔR (mm) | stripe near (mm) | stripe far (mm) |
|---|---|---|---|---|---|---|
| 10 | 4537.0 | 178.62 | 4607.0 | 1036.6 | 1931.4 | infinite |
| 15 | 2985.6 | 117.54 | 3091.0 | 695.5 | 1536.8 | 18323 |
| 20 | 2198.0 | 86.53 | 2339.0 | 526.3 | 1255.7 | 6077 |
| 30 | 1385.6 | 54.55 | 1600.0 | 360.0 | 873.0 | 2537 |
| 45 | 800.0 | 31.50 | 1131.4 | 254.6 | 509.7 | 1256 |
| 60 | 461.9 | 18.18 | 923.8 | 207.8 | 252.2 | 733 |

**Stopping-distance budget** (`d_stop = v·t_lat + v²/2a`, `t_lat = 0.10 s`, `a = 1.0 m/s²`):

| v (m/s) | reaction (mm) | braking (mm) | d_stop (mm) |
|---|---|---|---|
| 0.20 | 20.0 | 20.0 | 40.0 |
| 0.30 | 30.0 | 45.0 | 75.0 |
| 0.50 | 50.0 | 125.0 | 175.0 |
| 0.80 | 80.0 | 320.0 | 400.0 |
| 1.00 | 100.0 | 500.0 | 600.0 |

**Design rule:** `L ≥ d_stop + front overhang`. For a 350 mm platform at 0.5 m/s, `d_stop = 175 mm`; adding the 175 mm
front overhang gives a required look-ahead of ~350 mm measured from the sensor's ground projection. From
**Table 9, h = 200 mm** that is satisfied by `ψ ≤ 30°` (L = 346.4 mm) and comfortably by `ψ = 20°` (L = 549.5 mm).

**Three competing pressures fix ψ:**

1. **Look-ahead** wants small `ψ` (L = h/tan ψ grows as ψ falls).
2. **Signal quality** wants large `ψ`. At `ψ = 10°` the beam hits the floor at 10° grazing incidence; on polished wood,
   tile or laminate the return is largely specular and walks away from the receiver, producing intermittent
   "floor missing → cliff!" false positives. IR ToF is unreliable below roughly `ψ ≈ 20°` on smooth floors.
   **Confidence: inferred from Lambertian/specular reflection geometry, not vendor-published.**
3. **Discrimination** wants large `ΔR/R_f`. At `ψ = 10°, h = 200`, the flat-floor range is 1151.8 mm and a 180 mm drop
   adds 1036.6 mm — a 90 % jump, easy to see, but only if the 1151.8 mm floor return existed in the first place.
   At `ψ = 45°, h = 200`, `R_f = 282.8 mm` and `ΔR = 254.6 mm` — also a 90 % jump, with a solid near-normal return.
   The ratio `ΔR/R_f = D/h` is **independent of ψ**: `(D/sin ψ)/(h/sin ψ) = D/h`. So the *contrast* is set purely by
   drop depth over mount height, and ψ only trades look-ahead against incidence angle.

**Recommended cliff geometry:** `h ≈ 150–250 mm`, `ψ = 25–35°`, narrow `Φ_v` (≤ 25°) so the illuminated floor stripe is
short and the range reading is unambiguous, one unit per front quadrant plus one per rear quadrant. From **h = 200,
ψ = 30**: `L = 346.4 mm`, `R_f = 400.0 mm`, stripe 218.3 → 634 mm, and a 180 mm drop moves the range to 760 mm — a
threshold at `R > 500 mm ⇒ cliff` has enormous margin on both sides.

**Step-up (threshold) detection** is the mirror case and is *not* covered by a canted-down cliff sensor: a 20 mm
threshold strip raises the floor, shortening `R_f` by `20/sin(30°) = 40 mm` — only 10 % of nominal and inside typical ToF
range noise plus floor-reflectance variation. Step-up must be handled by a **level** low sensor at `h ≈ 40–60 mm`, or by
wheel-current / IMU-pitch detection, not by the cliff ring.

---

## 9. Mechanical: the recess penalty

The published FoV assumes an unobstructed aperture. A sensor set back `z` mm behind the skin, looking through a hole of
half-width `a`, is clipped to `Φ_eff = 2·atan(a/z)`:

| z (mm) | a=3 mm | a=5 mm | a=8 mm | a=12 mm | a=20 mm |
|---|---|---|---|---|---|
| 2 | 112.6° | 136.4° | 151.9° | 161.1° | 168.6° |
| 3 | 90.0° | 118.1° | 138.9° | 151.9° | 162.9° |
| 5 | 61.9° | 90.0° | 116.0° | 134.8° | 151.9° |
| 8 | 41.1° | 64.0° | 90.0° | 112.6° | 136.4° |
| 12 | 28.1° | 45.2° | 67.4° | 90.0° | 118.1° |
| 20 | 17.1° | 28.1° | 43.6° | 61.9° | 90.0° |

A 120° module behind a 3 mm shell with a 5 mm half-width window is clipped to **118.1°** — fine. The same module set
12 mm back to clear a connector is clipped to **45.2°**, which silently converts a 4-sensor design into a 12-sensor
problem. **Every millimetre of recess must be budgeted before the ring is sized.**

---

## 10. Summary of design conclusions

1. **Use `N = ceil(360/(Φ − overlap))` with overlap 10–20°, never `N = 360/Φ`.** At `Ω = 0` the beam edges are parallel
   and the wedge never closes at any range.
2. **The blind wedge is the binding constraint, not the ring count.** `D_tip = r[cos(Δ/2) + sin(Δ/2)·cot(Ω/2)]`, and
   `D_tip ∝ 1/Ω` for small overlap. Eight 27° ToF sensors give eight infinite blind wedges.
   **Size the ring on the datasheet *horizontal* FoV, never the diagonal headline.** The VL53L1X's 27° and the
   VL53L5CX's 63° are both diagonal figures; horizontally they are **19.270°** and **45.0°**. Twelve VL53L5CX close at
   **513.1 mm** from centre (338.1 mm past the skin), not 321.9 mm; **16** are needed to reach 343.3 mm. Twelve
   VL53L1X do not close at all — that part needs **N ≥ 19** merely to close and **N = 38** to bound the tip at 350 mm.
3. **Make the platform round if you can.** The square's 494.975 mm diagonal, 72.487 mm corner protrusion, and the
   face-vs-corner mounting trade (338 mm corner hole vs 653 mm face hole at 120° FoV) are all pure cost.
   If square, mount on **face centres** at `Φ ≥ 120°` and protect the corners mechanically.
4. **Mount the obstacle/pet ring at `h ≈ 200 mm` with `Φ_v ≥ 45°`.** At `h = 800, Φ_v = 25°` a cat is invisible at
   1, 3, 5 and 8 ft and only 38 % visible at 10 ft. At `h = 200` the cat is fully in the beam from 3 ft outward and
   partially in it at 1 ft, with first floor strike at 482.8 mm.
5. **Two tiers are mandatory for human-vs-pet discrimination.** Height above floor is the discriminator, and a single
   level ring does not measure it. Low tier ≈ 200 mm for obstacles and pets; high tier ≈ 900–1100 mm for human torso.
6. **Wide FoV buys coverage and destroys localisation.** At 5 ft a 90° single-zone sensor integrates a 3048 mm swath.
   Discrimination needs angular cells near 1.3° (a chair leg at 5 ft); an 8×8 array at `Φ_h = 45°` gives 5.625° cells,
   149.7 mm at 5 ft — enough to detect a leg, not to classify it.
7. **Cliff sensors: `h ≈ 200 mm`, `ψ = 25–35°`, narrow `Φ_v`.** `ΔR/R_f = D/h` is independent of ψ, so ψ trades
   look-ahead against grazing-incidence dropout. Keep `L ≥ d_stop + 175 mm`; at 0.5 m/s that is ~350 mm, met at ψ ≤ 30°.
8. **Budget the recess.** 12 mm of setback behind a 5 mm half-window turns a 120° part into a 45° part.

---

## Sources

- [VL53L5CX datasheet (ST)](https://www.st.com/resource/en/datasheet/vl53l5cx.pdf)
- [VL53L5CX product page (ST)](https://www.st.com/en/imaging-and-photonics-solutions/vl53l5cx.html)
- UM2884 — guide to using the VL53L5CX multizone ToF sensor with wide field of view. **Note: the link previously used
  here was a [Pololu-hosted mirror](https://www.pololu.com/file/0J1885/um2884-a-guide-to-using-the-vl53l5cx-multizone-timeofflight-ranging-sensor-with-wide-field-of-view-ultra-lite-driver-uld-stmicroelectronics.pdf)
  — a reseller copy, not the primary source. It is retained only because ST's own server did not respond during
  verification. UM2884 states "8x8 zones with a wide 63 ° diagonal field of view (FoV)"; it does **not** state
  45°×45°. The 45° horizontal figure comes from the datasheet (DS13754 Rev 2, Table 2), which is primary.**
- [VL53L1X datasheet (ST)](https://www.st.com/resource/en/datasheet/vl53l1x.pdf)
- [VL53L0X datasheet (ST)](https://www.st.com/resource/en/datasheet/vl53l0x.pdf)
- [HLK-LD2410 product page (Hi-Link)](https://www.hlktech.net/index.php?id=988)
- [HLK-LD2450 product page (Hi-Link)](https://www.hlktech.net/index.php?id=1157)
- [IRC Section R311.7.5 stair treads and risers handout (City of Boise, 02/2022)](https://www.cityofboise.org/media/14405/437-treads-risers_march-2022.pdf)
- [2018 IRC Section 311.7 stairways (InspectAPedia reproduction)](https://inspectapedia.com/Stairs/2018-IRC-Stair-Code-CO.pdf)
