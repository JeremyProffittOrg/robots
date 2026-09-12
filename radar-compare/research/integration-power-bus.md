# Integration, Power and Bus Engineering for a 4–12 Sensor Perimeter Ring

**Lane:** integration-power-bus
**Platform assumed:** 350 mm square or 350 mm diameter round footprint, 600–1200 mm tall, 0.3–0.5 m/s ground speed, indoor/home environment with humans and pets.
**Date of all price reads:** 2026-09-12.
**Scope:** this document is about *building the ring*, not about choosing the sensor. It covers I2C address collisions, bus capacitance over real cable lengths, optical crosstalk between neighbouring Time-of-Flight (ToF) sensors, mounting radar behind a printed shell, cutting optical apertures through a printed shell, getting 4–8 UART radars into one microcontroller, the power budget, and the update-rate/latency budget.

Every record carries a confidence marker:

- **datasheet-verified** — read from the silicon or module datasheet/manual PDF in this pass.
- **vendor-page-verified** — read from the vendor product page or wiki in this pass.
- **computed** — arithmetic performed here from datasheet-verified inputs; the inputs are cited.
- **inferred** — engineering judgement or widely-documented practice; not a published spec.
- **not published** — the vendor does not publish it. No number is invented in its place.

---

## 1. I2C address collisions: the VL53 family all boot to 0x29

### 1.1 The primitive fact

The VL53L1X boots with **7-bit I2C address 0x29 (8-bit write address 0x52, 8-bit read address 0x53)**, maximum bus speed **400 kbit/s**. *(datasheet-verified — [VL53L1X datasheet DocID031281 Rev 3](https://www.pololu.com/file/0J1506/vl53l1x.pdf), Section 4, Figure 12.)*

The whole VL53 single-zone family (VL53L0X, VL53L1X, VL53L4CD, VL53L4CX) shares 0x29. The multizone parts (VL53L5CX, VL53L7CX, VL53L8CX) share the same default. Two of them on one bus is a hard collision — both ACK, and reads return the wire-AND of two devices, which is silent garbage rather than an error.

**The address change is volatile.** It is held in a RAM register, not in NVM. It is lost on every power cycle and on every XSHUT (reset) assertion, so the sequencing dance below must run on *every* boot, not once at the factory. *(vendor-page-verified — [Adafruit VL53L0X Arduino Code guide](https://learn.adafruit.com/adafruit-vl53l0x-micro-lidar-distance-sensor-breakout/arduino-code): "you must do this every time you turn on the power, the addresses are not permanent!")*

There are exactly two ways out, and they have different failure modes, different capacitance behaviour, and different GPIO costs.

### 1.2 Approach A — XSHUT sequencing

**Parts**

| Part | Role | Price (USD, 2026-09-12) | Source |
|---|---|---|---|
| MCP23017 I2C GPIO expander breakout | 16 extra GPIO for XSHUT lines when the MCU is short | not read this pass | Adafruit 5346 |
| Any 3.3 V MCU GPIO | one per sensor | — | — |

**Wiring**

- Every sensor's SDA/SCL goes to the single shared bus.
- Every sensor's **XSHUT** goes to its own MCU GPIO. XSHUT is active-low reset; it must be *driven*, not left floating. Adafruit and Pololu breakouts fit a pull-up to VDD on XSHUT so the sensor runs when the pin is unconnected — which means at power-up **all** sensors come out of reset at 0x29 simultaneously.
- N sensors costs **N GPIOs**. For a 12-sensor ring that is 12 GPIOs, which is why an MCP23017 (16 I/O at address 0x20–0x27) is normally added. The expander is on the same bus but at a different address, so there is no chicken-and-egg problem.

**Code pattern (the only order that works)**

```
1. Drive ALL XSHUT low.                      // every sensor in reset, bus is empty
2. delay(10 ms).                             // Adafruit's published settling delay
3. for i in 0..N-1:
       drive XSHUT[i] HIGH                   // exactly one sensor wakes, at 0x29
       delay(10 ms)                          // boot
       sensor[i].begin(0x29)
       VERIFY: read model-ID register 0x010F // VL53L1X returns 0xEA,0xCC,0x10
       sensor[i].setAddress(0x30 + 2*i)      // move it off 0x29
       VERIFY: read model-ID at the NEW address, and confirm 0x29 no longer ACKs
       // if either verify fails: ABORT LOUDLY. Do not continue.
4. All N sensors are now at 0x30, 0x32, 0x34 ...
```

**Rules that are not optional**

- **Verify after every step.** If one sensor misses its address write, a second device is still sitting at 0x29 and every subsequent `begin(0x29)` talks to two chips at once. The symptom is not an error — it is plausible-looking but wrong distance data. An explicit model-ID read after each move is the only cheap detection.
- **Space addresses by 2.** Several community libraries are ambiguous about whether they take 7-bit or 8-bit addresses; leaving a gap means an off-by-one-bit shift lands on an empty address rather than on a neighbour. *(vendor-page-verified — [ST community: VL53L1X address changing](https://community.st.com/t5/imaging-sensors/vl53l1x-address-changing/td-p/162824): "change the first one to be at least 2 away for the others".)*
- **Stay out of reserved space.** 0x00–0x07 and 0x78–0x7F are reserved by the I2C specification. 0x70–0x77 is the TCA9548A/PCA954x block. 0x20–0x27 is MCP23017. A safe ToF block is **0x30–0x3F** — sixteen addresses, enough for a 12-sensor ring with slack.

**Failure modes**

- Brown-out or an ESD event resets one sensor back to 0x29 mid-run, silently colliding with nothing (it just disappears from its assigned address). Detect by periodically probing 0x29; if it ACKs during normal operation, re-run the whole sequence.
- **All the cable capacitance is always on the bus.** This is the decisive disadvantage; see Section 2.

### 1.3 Approach B — I2C multiplexer

**Parts and current prices (read 2026-09-12)**

| Part | Channels | Address range | Price 1-off USD | Stock | Source |
|---|---|---|---|---|---|
| Adafruit TCA9548A breakout (PID 2717) | 8 | 0x70–0x77 | **$6.95** ($6.26 @10, $5.56 @100) | In stock | [adafruit.com/product/2717](https://www.adafruit.com/product/2717) *(vendor-page-verified)* |
| Adafruit PCA9548 8-channel STEMMA QT (PID 5626) | 8 | 0x70–0x77 | **$6.95** | 68 in stock | [adafruit.com/product/5626](https://www.adafruit.com/product/5626) *(vendor-page-verified)* |
| Adafruit PCA9546 4-channel STEMMA QT (PID 5664) | 4 | 0x70–0x77 | **$3.95** ($3.56 @10, $3.16 @100) | In stock | [adafruit.com/product/5664](https://www.adafruit.com/product/5664) *(vendor-page-verified)* |
| SparkFun Qwiic Mux TCA9548A (BOB-16784) | 8 | 0x70–0x77 | **$6.95** | In stock | [sparkfun.com Qwiic Mux](https://www.sparkfun.com/sparkfun-qwiic-mux-breakout-8-channel-tca9548a.html) *(vendor-page-verified)* |

The SparkFun board carries **ten Qwiic connectors** — one per channel plus two for daisy-chaining the trunk — and runs 1.65–5.5 V. The Adafruit PCA9546/PCA9548 boards carry an onboard 3.3 V 500 mA regulator so they level-shift a 5 V host down to 3.3 V sensors. *(vendor-page-verified.)*

**Wiring**

- Host bus → mux SDA/SCL (trunk).
- Each sensor gets its own SD*n*/SC*n* pair (branch). All sensors stay at **0x29**; no XSHUT dance, no GPIOs, no per-boot sequencing.
- XSHUT can be tied to VDD or left on its pull-up.

**Code pattern**

```
void tcaselect(uint8_t ch) {          // ch = 0..7
  Wire.beginTransmission(0x70);
  Wire.write(1 << ch);                // BITMASK, not an index
  Wire.endTransmission();
}

// every single sensor transaction:
tcaselect(i);
sensor.readRangeContinuousMillimeters();
```

The control register is a **bitmask, not a channel number**. Writing `0x03` enables channels 0 *and* 1 at once and instantly recreates the 0x29 collision you bought the mux to avoid. Write exactly one bit. *(vendor-page-verified — [Adafruit TCA9548A Arduino wiring and test](https://learn.adafruit.com/adafruit-tca9548a-1-to-8-i2c-multiplexer-breakout/arduino-wiring-and-test).)*

**Cascading:** up to eight muxes at 0x70–0x77 gives 64 branches. *(vendor-page-verified.)* For a 12-sensor ring, two PCA9546 (4-channel, $3.95) plus four direct addresses, or one 8-channel plus one 4-channel, is cheaper and smaller than one 8-channel plus XSHUT sequencing for the remainder.

**Rules that are not optional**

- **Wire the mux RESET pin to an MCU GPIO.** A sensor that locks SDA low on one branch is isolated from the trunk by the mux — but a mux that has itself been wedged by a glitch takes the whole ring down. A GPIO reset is the only in-field recovery that does not require a power cycle.
- **Interrupts are not muxed.** The VL53L1X GPIO1 data-ready interrupt bypasses the mux entirely. Either route each interrupt to its own MCU pin, or wire-OR them (they are open-drain-capable push-pull outputs on most breakouts — check before OR-ing) and poll to find the source, or give up interrupts and poll on a timer.
- **Channel-select overhead is negligible.** A select is a 2-byte transaction ≈ **45 µs at 400 kHz** *(computed)*. Twelve selects per sweep = 0.54 ms against a 33 ms integration time. The mux is never the bottleneck.

### 1.4 Which to use

| Criterion | XSHUT sequencing | Multiplexer |
|---|---|---|
| Extra parts | 0 (or 1 GPIO expander) | 1–2 muxes, $3.95–$13.90 |
| GPIOs consumed | N | 0 |
| Boot complexity | High, must re-run every boot, must verify every step | None |
| Bus capacitance | **All branches always loaded** | **Only the selected branch is loaded** |
| Single point of failure | none | the mux |
| Fault isolation | none — one stuck sensor kills the bus | per branch |
| VL53L5CX firmware upload | N× serial uploads on one bus | same, but branches can be reset independently |

**Recommendation for this robot: multiplexer, with XSHUT still wired to GPIOs** *(inferred)*. The mux solves the addressing and the capacitance; keeping XSHUT under MCU control gives you a per-sensor hardware reset when one hangs, which is worth the GPIOs on a 12-node ring. Use the mux for addressing and XSHUT for recovery, not the reverse.

---

## 2. I2C bus capacitance over 300–800 mm of cable

### 2.1 The published limits

| Parameter | Value | Source |
|---|---|---|
| I2C Standard/Fast-mode maximum bus capacitance C_b | **400 pF** | I2C-bus specification; restated by [Analog Devices LTC4311](https://www.analog.com/en/products/ltc4311.html) *(vendor-page-verified)* |
| VL53L1X load capacitance C_L | typ **125 pF**, max **400 pF** | VL53L1X DS Table 10 *(datasheet-verified)* |
| VL53L1X SDA I/O capacitance C_i/o | max **10 pF** | VL53L1X DS Table 10 *(datasheet-verified)* |
| VL53L1X SCL input capacitance C_in | max **4 pF** | VL53L1X DS Table 10 *(datasheet-verified)* |
| VL53L1X SCL/SDA rise time t_R | max **300 ns** | VL53L1X DS Table 10 *(datasheet-verified)* |
| VL53L1X SCL/SDA fall time t_F | max **300 ns** | VL53L1X DS Table 10 *(datasheet-verified)* |
| VL53L1X V_OL at I_OUT = 4 mA | max **0.4 V** | VL53L1X DS Table 17 *(datasheet-verified)* |

### 2.2 The pull-up arithmetic that actually constrains you

I2C rise time is `t_R = 0.8473 · R_p · C_b` (30 %→70 % of an RC edge). At 3.3 V with V_OL = 0.4 V and the I2C Fast-mode 3 mA sink limit:

- Minimum pull-up: `R_p,min = (3.3 − 0.4) / 0.003 = 967 Ω` *(computed)*
- Maximum capacitance at 400 kHz (t_R ≤ 300 ns): `C_b,max = 300 ns / (0.8473 · 967 Ω) = 366 pF` *(computed)*
- Maximum capacitance at 100 kHz (t_R ≤ 1000 ns): `C_b,max = 1000 ns / (0.8473 · 967 Ω) = 1220 pF` *(computed)*

**The real 3.3 V ceiling is ~366 pF at 400 kHz, not 400 pF.** Dropping to 100 kHz multiplies your capacitance headroom by **3.3×**. This is the single most useful lever on a sensor ring and it costs almost nothing, because the bus is not the latency bottleneck (Section 7).

### 2.3 Cable capacitance over 300–800 mm

Neither Adafruit nor SparkFun publishes the per-metre capacitance of STEMMA QT / Qwiic cable. **Not published.** A 4-conductor 28 AWG PVC or silicone cable is typically **40–70 pF/m** conductor-to-conductor *(inferred; measure your own harness with an LCR meter before committing to 400 kHz)*.

Available stock cable lengths and prices, read 2026-09-12:

| Cable | Length | Price USD | Source |
|---|---|---|---|
| Adafruit STEMMA QT / Qwiic JST SH 4-pin | 50 mm | $0.95 | [adafruit.com/product/4210](https://www.adafruit.com/product/4210) *(vendor-page-verified)* |
| Adafruit STEMMA QT / Qwiic JST SH 4-pin | 100 mm | $0.95 | same |
| Adafruit STEMMA QT / Qwiic JST SH 4-pin | 200 mm | $1.25 | same |
| Adafruit STEMMA QT / Qwiic JST SH 4-pin | 300 mm | $1.25 | same |
| Adafruit STEMMA QT / Qwiic JST SH 4-pin | **400 mm (longest Adafruit stocks)** | $1.50 | same |
| SparkFun Flexible Qwiic Cable PRT-17257 | **500 mm**, silicone insulation | **$2.75** | [sparkfun.com/flexible-qwiic-cable-500mm.html](https://www.sparkfun.com/flexible-qwiic-cable-500mm.html) *(vendor-page-verified)* |

For a 600–1200 mm tall robot with the MCU in the base and sensors in the dome, a single run is **600–900 mm**. That exceeds Adafruit's longest stock cable; the options are the SparkFun 500 mm flexible part, chaining two cables through a pass-through board, or building a custom harness.

### 2.4 Worked capacitance budget — XSHUT ring vs muxed ring

Assumptions: 8 sensors, 800 mm average branch length, 60 pF/m cable, 10 pF per device SDA pin, 5 pF per breakout of board trace.

**All-on-one-bus (XSHUT approach):**

```
cable        8 × 0.8 m × 60 pF/m  = 384 pF
devices      8 × 10 pF            =  80 pF
breakouts    8 ×  5 pF            =  40 pF
host + trunk                      =  20 pF
------------------------------------------
TOTAL                             = 524 pF     >> 366 pF ceiling at 400 kHz
                                               >> 400 pF I2C spec limit
```
*(computed)* — **this configuration fails at 400 kHz and is marginal even at 100 kHz once you add margin.**

**Muxed (only one branch active):**

```
trunk cable  0.3 m × 60 pF/m      =  18 pF
active branch 0.8 m × 60 pF/m     =  48 pF
mux + 1 device + 1 breakout       =  30 pF
host                              =  20 pF
------------------------------------------
TOTAL                             = 116 pF     comfortably inside 366 pF
```
*(computed)* — **a mux does not merely fix the addressing; it divides the capacitance by the number of branches.** That is the strongest technical argument for Approach B on a robot this size.

### 2.5 When an extender becomes necessary

| Part | What it does | Limits | Price / source |
|---|---|---|---|
| **LTC4311** (Adafruit 4756) | Dual active pull-up / accelerator. Detects the rising edge and injects a slew-limited pull-up current, so a sawtooth edge becomes a square edge. No firmware. | **1.6–5.5 V supply**, **up to 400 kHz** *(both datasheet-verified — [LTC4311 datasheet 4311fa](https://cdn-learn.adafruit.com/assets/assets/000/095/254/original/4311fa.pdf), Features)*. **The "4000 pF" figure is Adafruit's, not ADI's** — the datasheet claims only "bus loading conditions well beyond the 400 pF I2C specification limit" and plots its pull-up-current curves out to 5000 pF; it publishes no maximum bus capacitance. Its one tabulated capacitance condition is a 300 ns rise time at **400 pF, V_CC = 3 V**. Demonstrated by Adafruit at 400 kHz over 3 m of phone wire, and over 100 ft (~3000 pF) of Ethernet at 100 kHz *(vendor-page-verified)*. | **$9.95**, in stock, STEMMA QT both ends — [adafruit.com/product/4756](https://www.adafruit.com/product/4756) *(vendor-page-verified)* |
| **P82B715** (NXP/TI) | True bidirectional current-multiplying buffer. Needs **one at each end** of the long run; Lx–Lx and Ly–Ly across the cable. | **400 pF** on each Sx/Sy (local) side, **~3000 pF** total system/cable capacitance on the Lx/Ly side. Speed: "clock speeds to at least 100 kHz, **and 400 kHz when other system delays permit**" — 400 kHz is conditional, not a rating. Length: the 50 m figure is a **100 kHz** number and the datasheet calls it theoretical — "the cable could, **in theory**, be up to 50 m long. From practical experience, **30 m** has proven a safe cable length to be driven in this simple way, **up to 100 kHz**". Supply: features say 3–12 V, but the characteristics table guarantees **4.5–12 V**, with note 1 reading "operation with reduced performance is possible down to 3 V … dynamic sink currents … are reduced and can increase fall times". **On a 3.3 V ring it is out of its guaranteed supply range.** | [NXP P82B715 datasheet](https://www.nxp.com/docs/en/data-sheet/P82B715.pdf), [AN10710](https://www.nxp.com/docs/en/application-note/AN10710.pdf) *(vendor-page-verified)* |

**Decision rule** *(inferred, from the numbers above)*:

- Total C_b under ~250 pF → plain 400 kHz, 2.2 kΩ pull-ups, nothing extra.
- 250–366 pF → 400 kHz with 1 kΩ pull-ups, or drop to 100 kHz. Still nothing extra.
- 366 pF up to the ~3000 pF Adafruit actually demonstrated (100 ft of Ethernet at 100 kHz) — **not a datasheet-guaranteed 4 nF** — all inside the chassis, ≤ 400 kHz → **one LTC4311 at the far end of the trunk**, $9.95. This is the right answer for a badly-routed 8–12 sensor ring and it is a drop-in STEMMA QT part.
- Run leaves the chassis (sensor mast, tethered base, >3 m) → **P82B715 pair**, one at each end. For a 350 mm robot this is overkill; it becomes correct only if you split the sensor ring onto a separate mast or a trailer.

An LTC4311 does **not** fix an address collision, and it does **not** extend the 400 kHz limit — it only fixes edge rates.

---

## 3. Optical crosstalk between neighbouring ToF sensors

### 3.1 Two distinct phenomena, often confused

1. **Cover-glass crosstalk (self-crosstalk)** — the sensor's own emitted photons reflecting off its own window straight into its own receiver. This is what ST's cover-glass application notes (AN5231, AN5856, AN5939, AN5962) are about, and it is fixed by geometry plus a per-unit calibration. Section 5.
2. **Sensor-to-sensor crosstalk (mutual interference)** — sensor A's 940 nm VCSEL photons landing on sensor B's SPAD array. This is what a perimeter ring creates, and no calibration fixes it.

### 3.2 What ST actually publishes about sensor-to-sensor interference

ST's published position, from their own engineers on the ST Community, is nuanced rather than a hard rule:

- Sensors pointed at **different angles do not meaningfully interfere**; stray light from A arriving at B is treated as ambient and discounted. *(vendor-page-verified — [ST Community: VL53L1X: will multiple sensors work together](https://community.st.com/t5/imaging-sensors/vl53l1x-will-multiple-sensors-be-able-to-work-together/td-p/112043).)*
- With **longer timing budgets the sensors do not interfere; at very fast rates they might.** *(vendor-page-verified, same source.)*
- With **directly overlapping fields of view the interference can be very large and the data unusable** — the reported case is a VL53L1X on one robot ranging a second robot that also carries a VL53L1X. *(vendor-page-verified — [ST Community: multiple sensors generate interference between each other](https://community.st.com/t5/imaging-sensors/multiple-sensors-generate-interference-between-each-other/td-p/206535).)*

### 3.3 What it costs you if you ignore it — the quantitative answer

Interfering photons are indistinguishable from ambient light to the SPAD array, and the VL53L1X datasheet publishes exactly what ambient does to range:

| Target reflectance | Dark | 50 kcps/SPAD ambient | 200 kcps/SPAD ambient |
|---|---|---|---|
| White 88 % | **360 cm** | 166 cm | 73 cm |
| Grey 54 % | **340 cm** | 154 cm | 69 cm |
| Grey 17 % | **170 cm** | 114 cm | 68 cm |
| Ranging error | ±20 mm | ±25 mm | ±25 mm |

*(datasheet-verified — VL53L1X DS Table 7, long-distance mode, 100 ms timing budget.)*

So the penalty for letting neighbours illuminate each other is a **range collapse of up to 80 % on a bright target and 60 % on a dark one**. On a 350 mm robot that turns a 3.6 m perimeter sensor into a 0.7 m one — below the reaction distance needed for a walking human (Section 7).

The second, worse failure mode is a **phantom close target**: if the interferer's pulse arrives inside the victim's histogram window at a short apparent time-of-flight, the victim reports a short range that never existed. The robot then emergency-stops at random in an empty room. This is a nastier fault than range collapse because it is intermittent and it looks exactly like a real detection.

### 3.4 Mitigations, in order of preference

1. **Geometric separation.** Aim the cones so they do not overlap inside the first 0.5 m. The VL53L1X full FoV is 27° diagonal at 16×16 SPAD, 20° at 8×8, and 15° at 4×4 *(datasheet-verified — DS Table 9)*. **Shrinking the region of interest (ROI) shrinks the cone** — a 4×4 ROI gives 15° instead of 27°, which lets eight sensors sit on a 350 mm ring without overlapping, at the cost of range (170 cm → 45 cm on a 17 % grey target, per the same table). **Read the condition on Table 9: those ROI ranges are dark, long-distance mode, 100 ms timing budget, target covering only the partial FoV — they are *not* ambient-light numbers.** In 200 kcps/SPAD ambient the 16×16 figure is already down to 68 cm (Table 7), so a 4×4 ROI in daylight is worth far less than 45 cm. That trade is usually wrong for a perimeter; 8×8 (20°, 119 cm on 17 % grey **in the dark**) is the better compromise.
2. **Time-multiplexed firing.** Only one sensor in an optical group ranges at a time. Implement by starting/stopping ranging via the driver, not by toggling XSHUT (an XSHUT reset loses the assigned address, Section 1.1). Cost: the full ring revisit time is multiplied by the group size. Section 7 shows this is the dominant latency term.
3. **Group-parallel firing.** Split the ring into 2 optical groups whose members never overlap (e.g. alternate sensors around the ring) and fire the groups alternately. **This is the sweet spot: it removes the overlap and costs only 2× latency instead of 8×.** *(inferred)*
4. **Longer timing budget.** Follows ST's own statement. A 100 ms budget averages the interference down; a 20 ms budget does not. Directly opposes requirement (2).
5. **Decorrelate the periods.** Give each sensor a slightly different inter-measurement period (e.g. 40, 41, 43, 47 ms) so collisions do not repeat on the same pair every cycle. Turns a systematic bias into an occasional outlier that a 3-of-5 median filter removes. *(inferred)*

**If you ignore all of it:** intermittent phantom stops, a perimeter whose usable range silently drops as you add sensors, and — because ambient-induced range loss is worst on dark, low-reflectance targets — **the failure lands hardest on exactly the object class you care about most: a dark-furred cat on a dark carpet.**

---

## 4. mmWave radar: mutual interference and mounting behind a printed shell

### 4.1 Multiple 24 GHz radars

All the cheap modules occupy the same **24.00–24.25 GHz ISM band** with a **250 MHz FMCW sweep**. *(datasheet-verified — [HLK-LD2410 user manual V1.03](https://seengreat.com/upload/file/86/HLK+LD2410+Life+Presence+Sensor+Module+Manual+V1.03(220629).pdf), Table 2: "Working frequency 24 GHz ~ 24.25 GHz", "Sweep Bandwidth 250 MHz".)*

A 250 MHz sweep gives a physical range resolution of `c / 2B = 0.6 m` *(computed)*; Hi-Link publishes 0.75 m *(datasheet-verified, same table)*. There is no room in that band for frequency-division between modules, and none of these modules expose a chirp-sync input. Two modules whose beams overlap therefore **share the band** and each dechirps the other.

**Published vendor guidance on minimum separation between two radars:**

- DFRobot SEN0395 wiki: **not published.** The wiki covers beam angle, mounting height and wall penetration, but says nothing about multiple radars. *(vendor-page-verified — [wiki.dfrobot.com/sen0395](https://wiki.dfrobot.com/sen0395/).)*
- DFRobot C4001 / SEN0610 wiki: **not published.** *(vendor-page-verified — [SEN0610 wiki](https://wiki.dfrobot.com/SKU_SEN0610_Gravity_C4001_mmWave_Presence_Sensor_12m_I2C_UART).)*
- Hi-Link LD2410 manual: **no minimum separation figure.** It warns instead about "a large area of strong reflectors in the sensing area" causing "interference to the radar antenna", about constantly-moving non-human objects, and about back-lobe detection. *(datasheet-verified — LD2410 manual Section 5.5.)*
- Seeed MR60BHA2 wiki: states the sensor "must avoid interference from nearby radars" but publishes no distance. *(vendor-page-verified.)*

**Do not let anyone quote you a number here that a vendor has not published.** The honest engineering position is:

- Hi-Link *does* publish a usable mitigation: "**Metal shielding cover or metal backplane can be used to shield the radar back lobe and reduce the influence of objects on the back of the radar.**" *(datasheet-verified — LD2410 manual Section 5.5, "Precautions during installation".)* On a 360° ring this is the key trick — a metal plate or metallised film between back-to-back radars stops each from seeing through the robot into the other's sector *and* attenuates the direct path between them.
- LD2410 beam is **±60°** *(datasheet-verified)*. Three radars at 120° spacing cover 360° with the −3 dB edges just meeting. Four at 90° spacing overlap 30° on each side. **Three is the number that minimises overlap**; use the metal backplane between them.
- Practical rule *(inferred, not a vendor spec)*: keep the −3 dB beams from overlapping inside the first 1 m, put conductive shielding between any two radars whose backs face each other, and treat any radar-to-radar spacing rule you find on a forum as unverified.
- **Time-multiplexing radars is not practical.** These modules take seconds to boot and to settle their background estimate after a power cycle, and they expose no gate input. Unlike ToF, you cannot round-robin them.

### 4.2 Radar transparency of printed plastics — the real numbers

Both Hi-Link and Waveshare publish the **same** material table, based on **24.125 GHz**:

| Medium | ε_r typ. | Half-wavelength in medium (mm) | 1/8 wavelength (mm) | 1/10 wavelength (mm) |
|---|---|---|---|---|
| Air | 1.00 | 6.20 | 1.55 | 1.24 |
| ABS 1 | 1.50 | 5.06 | 1.27 | 1.01 |
| **ABS 2** | **2.50** | **3.92** | **0.98** | **0.78** |
| PC (polycarbonate) | 3.00 | 3.58 | 0.89 | 0.72 |
| PMMA acrylic 1 | 2.00 | 4.38 | 1.10 | 0.88 |
| PMMA acrylic 2 | 5.00 | 2.77 | 0.69 | 0.55 |
| PVC hard | 4.00 | 3.10 | 0.78 | 0.62 |
| PVC soft | 8.00 | 2.19 | 0.55 | 0.44 |
| HDPE | 2.40 | 4.00 | 1.00 | 0.80 |
| LDPE | 2.30 | 4.09 | 1.02 | 0.82 |
| Quartz glass | 5.00 | 2.77 | 0.69 | 0.55 |

*(datasheet-verified — [HLK-LD2410 manual](https://seengreat.com/upload/file/86/HLK+LD2410+Life+Presence+Sensor+Module+Manual+V1.03(220629).pdf) Table 3, and the identical table in [Waveshare "Impact of Radome on HMMD-mmWave-Sensor Performance"](https://files.waveshare.com/wiki/HMMD-mmWave-Sensor/HMMD-mmWave-Sensor%20Radome%20Design%20Guide%20.pdf).)*

**PLA is not in that table.** Published complex-permittivity measurements of 3D-printed PLA give **ε_r ≈ 2.75 held across the microwave band and at 40 GHz and 60 GHz** *(inferred from the measurement literature — [Complex permittivity and anisotropy measurement of 3D-printed PLA at microwaves and millimeter-waves](https://www.researchgate.net/publication/313543263_Complex_permittivity_and_anisotropy_measurement_of_3D-printed_PLA_at_microwaves_and_millimeter-waves); note that printed ε_r falls with infill, so a 40 % infill wall is **not** 2.75)*. From ε_r = 2.75:

- **PLA half-wave thickness at 24.125 GHz = 6.213 / √2.75 = 3.75 mm** *(computed)*; 1/8 wavelength = 0.94 mm.
- **PLA half-wave thickness at 60 GHz = 2.498 / √2.75 = 1.51 mm** *(computed)*; 1/8 wavelength = 0.38 mm — thinner than one printed perimeter, so at 60 GHz the half-wave rule is the only usable option.

**PETG: ε_r is not published** in any of the vendor tables above. Bound it between the ABS row (2.5 → 3.92 mm) and the PC row (3.0 → 3.58 mm) at 24 GHz and measure, or simply print the radome window in ABS or PLA where you have a number.

### 4.3 The two thickness/standoff rules, stated exactly

**Wall thickness D** — an integer multiple of the half-wavelength *in the medium*:

```
D = (m/2) · c0 / (f · √ε_r)      m = 1, 2, 3 ...
```
*(datasheet-verified — Hi-Link LD2410 manual §7.2 and Waveshare radome guide; identical to TI's `t_optimum = n·λ_m/2`, `λ_m = c/(f·√ε_r)` in [SWRA705 mmWave Radar Radome Design Guide](https://www.ti.com/lit/an/swra705/swra705.pdf) Equations 3 and 4.)*

Why it works: at half-wave thickness, the round trip through the wall and back off the outer face introduces a net 180° phase shift, so the inner-face reflection cancels. *(datasheet-verified — SWRA705 §4.1.)*

- **Thickness error must stay within ±20 %.** *(datasheet-verified — Waveshare/Hi-Link guide.)*
- If half-wave is mechanically impossible, go the other way: **thickness ≤ 1/8 wavelength in the medium**, which minimises the path length rather than tuning it. *(datasheet-verified — Waveshare guide FAQ A1.)* Anything between 1/8 λ and 1/2 λ is the worst of both.

**Antenna-to-inner-surface standoff H** — an integer multiple of the half-wavelength *in air*:

```
H = (m/2) · c0 / f
```

- At 24.125 GHz the air half-wavelength is **6.20 mm**. *(datasheet-verified.)*
- **Preferred H is 1× or 1.5× the full wavelength: 12.4 mm or 18.6 mm.** If space is tight, use half a wavelength (6.2 mm) and tune experimentally.
- **H tolerance: ±1.2 mm.** *(datasheet-verified — Waveshare/Hi-Link guide.)*
- TI states the same rule as `D = n·λ0/2`. *(datasheet-verified — SWRA705 Equation 5.)*

### 4.4 Measured evidence that getting the thickness wrong wrecks the sensor

TI built a **2 mm-wall ABS rectangular enclosure** over an IWR6843ISK at **62 GHz** and measured Tx→Rx patterns across ±60° azimuth. With no radome the pattern is smooth, spanning roughly 105–120 dB. With the 2 mm ABS box the pattern breaks into deep ripples and nulls **swinging roughly 80–125 dB** — TI's own words: "this radome significantly degraded the antenna radiation pattern." *(datasheet-verified — SWRA705 §6.1, Figures 6-1, 6-2, 6-3.)*

Why: for ABS at ε_r = 2.5 and 62 GHz, the correct half-wave thickness is `(3e8/62e9)/(2·√2.5) = 1.53 mm` *(computed)*. **2 mm is 1.31× the optimum — squarely in the worst zone.** A 0.47 mm wall-thickness error destroyed the pattern.

By contrast a **1.524 mm PTFE** (ε_r 2.0, tan δ < 0.0002) rectangular radome showed much less ripple, and the same PTFE material formed into a **curved** radome was better still. *(datasheet-verified — SWRA705 §6.2, §6.3.)*

TI's permittivity and dissipation-factor table:

| Material | Permittivity ε_r | Dissipation factor tan δ |
|---|---|---|
| Polycarbonate | 2.9 | 0.012 |
| **ABS** | **2.0–3.5** | **0.0050–0.019** |
| PEEK | 3.2 | 0.0048 |
| PTFE (Teflon) | 2.0 | < 0.0002 |
| Plexiglass | 2.6 | 0.009 |
| Glass | 5.75 | 0.003 |
| Ceramics | 9.8 | 0.0005 |
| PE | 2.3 | 0.0003 |
| PBT | 2.9–4.0 | 0.002 |

*(datasheet-verified — SWRA705 Table 3-1.)*

Note the ABS spread: **2.0 to 3.5**. That alone moves the 24 GHz half-wave thickness from 4.39 mm to 3.32 mm *(computed)* — a 24 % swing, wider than the ±20 % tolerance. **You cannot design a 24 GHz radome from a generic "ABS" datasheet value; you must get ε_r from your filament supplier or measure it.**

### 4.5 Curved versus flat shells — this matters for a costume robot

A costume shell is usually curved, and that is **good news**:

- In a **rectangular/flat** radome the path length through the wall grows with grazing angle, so the wall is only correctly tuned at boresight. Off-boresight you get ripples, nulls and **angle-estimation errors that displace the detected object**, and the displacement worsens with range. *(datasheet-verified — SWRA705 §4.1, §4.3, Figure 4-3.)*
- In a **spherical/curved** radome with the antenna at the centre of curvature, the path length is the same at every grazing angle, so "the radome performance can be shown to be similar to the boresight". Curved radomes give "less angle dependent errors". *(datasheet-verified — SWRA705 §4.2, Figure 4-2, Figure 4-4.)*

TI's curved model uses **radius = n·λ0/2** with **wall thickness = n·λ_m/2**. *(datasheet-verified — SWRA705 Figure 4-2.)* For a 350 mm round robot this fits naturally: put the radar at the centre of a local spherical boss on the shell whose radius is a multiple of 6.2 mm.

Waveshare adds one more constraint that hits printed parts directly: **do not use frosted or textured surfaces** — "it is not recommended to use frosted materials, which will increase the reflection of electromagnetic waves and increase the loss and affect the antenna radiation patterns." *(datasheet-verified.)* **A printed radome window should be printed smooth-side-out, or sanded and filled, not textured.** A textured PEI plate finish on the radar window is a measurable loss.

### 4.6 Materials that are radar-opaque — hard no-list

| Material | Status | Source |
|---|---|---|
| Any metal in the enclosure wall | **Opaque.** "cannot contain metal materials or materials that can shield electromagnetic waves" | LD2410 manual §5.5 *(datasheet-verified)* |
| Metallic / metal-flake paint | **Opaque.** "avoid metal fixings and coatings (especially metallic paint that will reduce the signal strength significantly)"; "Paint, especially metallic-paint, used to enhance the aesthetic appearance of the radome, may further degrade the performance of the antenna." | SWRA705 §3, §8 *(datasheet-verified)* |
| Any surface coating containing metal or conductive material | **Opaque.** "If there is a surface coating, it must not contain any metal or conductive materials" | Waveshare/Hi-Link radome guide *(datasheet-verified)* |
| Carbon-fibre composites and CF-filled filaments (CF-PETG, CF-nylon) | **Opaque** — carbon fibre is conductive *(inferred; not named in the vendor docs, follows directly from the "no conductive materials" rule)* |
| Conductive / anti-static / graphite-filled filaments | **Opaque** *(inferred, same reasoning)* |
| Metallic "silk" filaments containing metal powder | **Attenuating to opaque** *(inferred)* |
| EMI-shielding sprays, ITO films, metallised Mylar | **Opaque** *(inferred)* |
| Non-uniform, composite or multi-layer walls; bubbles, voids, sparse infill | **Degrading.** "Non-uniform or composite materials can degrade radar performance"; TI: the wall should be "solid with no air bubbles or other material fragments inside" | Waveshare guide; SWRA705 §3 *(datasheet-verified)* |

**The last row is the one that bites 3D printing hardest.** A 3-perimeter, 20 %-infill printed wall is a *sandwich* of solid-sparse-solid with an unknown effective ε_r, not a homogeneous slab. **A radar window must be printed 100 % solid across its full aperture plus a margin**, at a controlled thickness. Reserve a 100 %-infill puck in the model at the radar location.

**And one deliberate use of metal:** put a metal or metallised backplane *behind* each radar to kill the back lobe, per Hi-Link. On a ring this both stops radar A seeing rearward through the robot and reduces its coupling into radar B.

---

## 5. ToF optical window: a printed shell is not optional to cut through

### 5.1 The blunt fact

A ToF sensor cannot see through a printed shell. Radar can sit behind a wall; **ToF cannot.** A 1–2 mm printed PLA or ABS wall in front of a VL53L1X is one of three things:

- **Opaque** (black or filled filament) — sensor reads nothing, or reads the wall.
- **Translucent and scattering** (natural or white PLA) — worse than opaque. The wall acts as a diffuser immediately in front of the emitter and dumps a huge fraction of the emitted photons straight back into the receiver. The sensor either reports a fixed short range (the wall), or saturates and reports failure. **This is the single most common failure in first builds.**
- Occasionally usable behind a polished IR-pass window, if and only if you follow Section 5.3.

**Each ToF sensor needs its own clear aperture in the shell.**

### 5.2 The keep-out cones, straight from the VL53L1X outline drawing

ST specifies the optical keep-out as a cone from a datum at the module cap:

| Channel | Cone full angle | Diameter at datum A |
|---|---|---|
| **EMT (emitter) keep-out cone** | **36.50°** | **Ø 0.84 mm** |
| **RTN (receiver) keep-out cone** | **39.60°** | **Ø 1.08 mm** |

*(datasheet-verified — VL53L1X DS Figure 19, "Outline drawing page 2/3", drawing DM00319387 Rev 3.0, sheet 2 of 3, read from the rendered drawing itself. **Correction 2026-09-12:** an earlier revision of this document gave the EMT cone as 36.60°; the drawing prints **36.50°**. The RTN cone is 39.60°, as printed.)* Module body is 4.9 × 2.5 × 1.56 mm *(datasheet-verified — DS cover page, Features)*; the two optical centres are spaced **3 ±0.02 mm** apart on the long axis. *(datasheet-verified — DS Figure 19.)*

**Required aperture diameter at a shell standoff H above the datum** *(computed from the cone angles above)*:

```
D_emitter(H)  = 0.84 + 2·H·tan(18.25°) = 0.84 + 0.660·H     (mm)
D_receiver(H) = 1.08 + 2·H·tan(19.80°) = 1.08 + 0.720·H     (mm)
```

| Standoff H (module cap → inside of shell) | Emitter aperture Ø | Receiver aperture Ø | Single oval aperture (long × short) |
|---|---|---|---|
| 0.5 mm | 1.17 mm | 1.44 mm | 4.31 × 1.44 mm |
| 1.0 mm | 1.50 mm | 1.80 mm | 4.65 × 1.80 mm |
| 2.0 mm | 2.16 mm | 2.52 mm | 5.34 × 2.52 mm |
| 3.0 mm | 2.82 mm | 3.24 mm | 6.03 × 3.24 mm |
| 5.0 mm | 4.14 mm | 4.68 mm | 7.41 × 4.68 mm |

*(computed from the datasheet keep-out cones; oval long axis = 3.0 mm optical-centre spacing + mean of the two diameters.)*

**Anything narrower than these numbers clips the cone**, which vignettes the field of view, kills range asymmetrically, and — because the clipped photons scatter off the aperture edge — *raises* crosstalk rather than reducing it.

### 5.3 ST's cover-glass rules

| Rule | Value | Source and confidence |
|---|---|---|
| Air gap (module cap to inside of cover) — single-zone parts | **Keep as small as possible.** Crosstalk rises with air gap. **Above ~0.5 mm a gasket or light barrier is required.** | ST Community engineer answer citing AN5231 *(vendor-page-verified)* — [thread](https://community.st.com/t5/imaging-sensors/vl53l5cx-gasket-requirements-with-cover-window-and-large-air-gap/td-p/142460) |
| Air gap — VL53L5CX | **< 0.4 mm recommended; > 0.7 mm requires a gasket** to keep crosstalk below the maximum | AN5856, quoted second-hand *(unverified — AN5856 PDF could not be opened in this pass)* |
| Cover material transmission at 930–950 nm | **> 85 %** | AN5231, quoted second-hand *(unverified)* |
| Cover thickness | **~1 mm is a good thickness.** A *thin* cover is better: the beam bounces internally many times before reaching the receiver and is attenuated at each bounce, so crosstalk ends up low | ST Community ToF cover-glass article *(vendor-page-verified)* |
| Surface | **Smooth and polished.** Textured/frosted surfaces scatter into the receiver | *(inferred, consistent with the radar guidance and with ST's crosstalk model)* |
| Gasket | Thick enough to **fill the whole air gap**; **two apertures** large enough to pass the full Tx and Rx cones unimpeded; **forms a light barrier between Rx and Tx** | ST/AN5856 via search summary *(unverified)* |
| Crosstalk calibration | **Must be run once per unit on the production line**, with the real cover fitted, to compensate part-to-part cover spread | ST Community / AN5856 *(vendor-page-verified as a requirement; exact target distance and reflectance are in the AN and were not read — **not published here**)* |
| Crosstalk immunity | VL53L5CX histogram gives immunity to cover-glass crosstalk **beyond ~600 mm** | ST Community *(vendor-page-verified)* |
| Protective liner | The module ships with a liner over the cap; **remove it immediately before mounting the cover glass**, not earlier | VL53L1X DS page 27 *(datasheet-verified)* |

### 5.4 Practical build recipe for a printed costume shell

1. Model a **through-hole** at each ToF location, sized from the table in 5.2 for your actual standoff. Do not rely on "PLA is a bit translucent".
2. Set the standoff to **≤ 0.5 mm** if you can — bond the sensor breakout directly to the inside face of the shell with the module cap almost touching it. That keeps you inside the no-gasket regime.
3. If the shell is thicker than ~1 mm at that point, **counterbore from the inside** so the *optical* air gap is the counterbore depth, not the wall thickness, and taper the bore wider than the cone so the walls never intercept the beam.
4. Fit a **light barrier / septum between the Tx and Rx apertures** — a 0.4 mm printed rib or a slice of black adhesive foam running the full standoff. This is the single highest-value part of the whole assembly and it costs nothing.
5. If the aperture must be sealed (dust, a costume finish), bond in a **1 mm polished IR-transmissive window** over the aperture only — not a full-shell panel. Black-to-visible / IR-pass acrylic looks right on a costume and is transparent at 940 nm.
6. **Run the per-unit crosstalk calibration after final assembly**, store the result in flash, and re-run it whenever the shell is disturbed. An uncalibrated covered sensor reads short — which on a robot means it stops for a wall that is not there.
7. Verify by pointing the finished assembly at empty space: a correctly built aperture returns "no target"; a bad one returns a stable 50–300 mm.
8. **Do not read anything into a sub-40 mm return.** The VL53L1X **minimum ranging distance is 4 cm**; below it "the sensor will detect a target, but the measurement will not be accurate". *(datasheet-verified — VL53L1X DS §3.3.)* A shell aperture, a gasket or a smear of adhesive inside the cone shows up as exactly that kind of stable, meaningless short reading.

---

## 6. UART fan-in: 4–8 radars into one MCU

### 6.1 The problem

Radar presence modules are UART-native and most of them **stream unsolicited frames** rather than answering polls. The LD2410 exposes "1 GPIO, IO level 3.3 V; 1 UART" *(datasheet-verified — LD2410 manual Table 2)*; the DFRobot SEN0395 runs **115200 baud** *(vendor-page-verified — [SEN0395 wiki](https://wiki.dfrobot.com/sen0395/))*; the DFRobot C4001/SEN0610 runs **9600 baud** and also offers I2C at **0x2A/0x2B** *(vendor-page-verified — [SEN0610 wiki](https://wiki.dfrobot.com/SKU_SEN0610_Gravity_C4001_mmWave_Presence_Sensor_12m_I2C_UART))*.

That last fact is worth flagging: **the C4001 family gives you an I2C option with two selectable addresses**, so two of them need no UART at all — but only two, and then you are back to a mux.

### 6.2 Option 1 — an MCU with enough hardware UARTs

| MCU | Hardware UARTs | Notes |
|---|---|---|
| ATmega328 (Uno/Nano) | 1 | Hopeless for this job |
| ESP32 / ESP32-S3 | 3 (one usually on the USB/boot console) | 2 usable radars |
| RP2040 / RP2350 | 2 hardware **+ PIO** | See Option 2 |
| Teensy 4.1 | 8 hardware serial ports | Exactly matches an 8-radar ring *(unverified — PJRC page not read in this pass)* |
| STM32H7 family | 8+ USART/UART | *(unverified)* |

**Software serial is not a solution.** Arduino `SoftwareSerial` is documented as reliable only to ~38400 baud, cannot receive on more than one instance at a time, and blocks interrupts while shifting bits. Four radars at 115200 concurrently is far outside it. *(inferred, from the long-standing Arduino `SoftwareSerial` documentation and design.)*

### 6.3 Option 2 — RP2040 PIO satellites (recommended)

The RP2040's two PIO blocks implement UART RX/TX in state machines, 4 state machines per block, 8 total — so **one RP2040 can receive 8 independent UART streams at 115200–256000 baud** with DMA into ring buffers and zero CPU cost per bit. The Pico SDK ships `uart_rx` and `uart_tx` PIO examples.

Topology: put one RP2040 (Raspberry Pi Pico class) at the base of the sensor ring as a **dedicated sensor concentrator**. It takes 8 radar UARTs in on PIO, parses the frames, and presents a single consolidated I2C-target or SPI or USB interface to the main computer.

Why this wins on this robot *(inferred)*:

- It collapses 8 async streams into one link, so the main computer's latency budget is unaffected by frame parsing.
- It gives you somewhere to put the time-multiplex scheduler for the ToF group firing, too — the concentrator can own the entire perimeter ring and publish a single 16-sector range/presence vector.
- Cost of the concentrator is the price of one Pico-class board, far below the cost of four SC16IS752 breakouts.
- Wiring from radar to concentrator is short if the concentrator sits in the base with the radars on a mid-height ring.

### 6.4 Option 3 — I2C/SPI-to-UART bridge chips

| Part | Channels | Host bus | Max baud | FIFO | Notes |
|---|---|---|---|---|---|
| **NXP SC16IS752** | 2 | I2C **400 kbit/s max** (Fast mode, target only) or SPI **4 Mbit/s** | **5 Mbit/s** in 16× clock mode | 64 B TX + 64 B RX | 3.3 V or 2.5 V, 5 V-tolerant inputs, sleep current **< 30 µA at 3.3 V**, **up to 8 programmable I/O pins**, automatic RS-485 support with RTS direction control |
| **NXP SC16IS762** | 2 | SPI **15 Mbit/s** | 5 Mbit/s | 64 B | Otherwise identical to the 752 |
| **Maxim MAX14830** | 4 | SPI | — | — | *(unverified — datasheet not read in this pass)* |

*(SC16IS752/762 rows: datasheet-verified — [NXP SC16IS752/SC16IS762 product data sheet Rev. 9.1, 5 Feb 2025](https://www.nxp.com/docs/en/data-sheet/SC16IS752_SC16IS762.pdf) §1, §2.1, §2.2, §2.3.)*

**The bandwidth check that decides it** *(computed)*:

- I2C Fast mode at 400 kbit/s carries at most `400000 / 9 ≈ 44 kB/s` of payload after the ACK bit, before any register-addressing overhead — realistically **~30 kB/s**.
- An LD2410 basic-mode frame is ~23 bytes at roughly 10 frames/s ≈ **230 B/s** per radar. Eight radars ≈ **1.8 kB/s**. Comfortable.
- An LD2410 *engineering-mode* frame is ~45 bytes and can be requested far faster; eight radars in engineering mode at 20 Hz ≈ **7.2 kB/s**. Still fine.
- But the bridge must be **polled**, and each poll is a register read with I2C overhead. Four SC16IS752 at 400 kHz polled at 50 Hz costs roughly `4 × 50 × (64 B + overhead) ≈ 15 kB/s` — **about half the usable I2C bandwidth**, on the same bus as the ToF ring.

**Conclusion:** use the SC16IS752 in **SPI mode**, not I2C mode, if you go this route, and keep it off the sensor I2C bus entirely. Four SC16IS752 on one SPI bus with four chip selects gives 8 UARTs. This is more parts and more cost than one RP2040 concentrator.

### 6.5 Option 4 — analog multiplexer on the RX lines (CD4052 / 74HC4051)

A 74HC4051 (8:1) or CD4052 (dual 4:1) can switch which radar's TX line reaches the MCU's single RX pin.

**This works only for command/response sensors.** With a streaming sensor like the LD2410 you lose every frame from every unselected channel, and you will regularly switch into the middle of a frame and desynchronise the parser. *(inferred — direct consequence of the modules' unsolicited-frame behaviour.)* Do not use an analog mux for a streaming radar ring.

### 6.6 Option 5 — RS-485 multidrop

RS-485 solves multidrop electrically (32+ nodes, 1200 m, differential noise immunity) with parts like **MAX3485**, **SN65HVD75** or **THVD1450**. But RS-485 is a *physical layer*: it needs an addressed, polled protocol (Modbus RTU) on top, and **none of these radar modules speak Modbus or have a node address**. RS-485 therefore requires a per-sensor microcontroller anyway — at which point Option 3 (satellite MCUs) is the same solution with less wiring.

RS-485 becomes correct only if the perimeter ring is physically distributed over more than a couple of metres, or crosses a slip ring / rotating joint. On a 350 mm robot: **not justified.** *(inferred)*

### 6.7 Recommendation

| Ring size | Recommended fan-in |
|---|---|
| 2 radars | Two hardware UARTs on an ESP32 or RP2040. Nothing extra. |
| 3–4 radars | One RP2040: 2 hardware UARTs + 2 PIO UARTs. Nothing extra. |
| 5–8 radars | **One RP2040 concentrator using 8 PIO UART RX state machines**, presenting one I2C/SPI/USB link upstream. |
| 8+ radars, physically distributed | Per-sensor satellite MCU + RS-485/Modbus trunk. |

---

## 7. Update rate and latency budget — what a 0.3–0.5 m/s robot actually needs

### 7.1 Deceleration ceiling set by tipping, not by traction

A 350 mm-footprint robot 600–1200 mm tall tips before it skids. With track width `t`, centre-of-gravity height `h`:

```
a_tip = g · (t/2) / h
```

| CG height | a_tip (350 mm track) | Safe working decel (50 % of a_tip) |
|---|---|---|
| 300 mm | **5.72 m/s²** | 2.9 m/s² |
| 450 mm | **3.81 m/s²** | 1.9 m/s² |
| 600 mm | **2.86 m/s²** | 1.4 m/s² |
| 800 mm | **2.15 m/s²** | 1.1 m/s² |

*(computed, g = 9.81 m/s².)*

**Use a = 1.5 m/s² as the design deceleration** for a tall costume robot — it is ~52 % of the tipping limit at a 600 mm CG. A dome-heavy costume robot that panic-stops at 3 m/s² falls on its face.

Braking distance and time:

| Speed | Braking time (a = 1.5 m/s²) | Braking distance |
|---|---|---|
| 0.3 m/s | 0.200 s | **30 mm** |
| 0.5 m/s | 0.333 s | **83 mm** |

*(computed.)*

### 7.2 The latency chain

```
T_total = T_revisit + T_integration + T_processing + T_actuation
```

- `T_revisit` — time between successive looks at the same bearing. Dominated by how many sensors must fire sequentially to avoid optical crosstalk (Section 3).
- `T_integration` — the sensor's own measurement window. VL53L1X **33 ms** is the fast datasheet-referenced operating point: the datasheet specifies "average power consumption at 10 Hz with 33 ms timing budget", confirming 33 ms / 10 Hz as a supported configuration. *(datasheet-verified — DS Table 16.)*
- `T_processing` — filtering, sector fusion, decision. Budget **10 ms**.
- `T_actuation` — command to motor controller, current rise, torque reversal. Budget **50 ms** *(inferred; measure yours)*.

**Reaction distance** at closing speed `v_close`:

```
d_react = v_close · T_total + v_robot² / (2a) + d_margin
```

### 7.3 The three closing speeds that matter

| Scenario | v_close | Why |
|---|---|---|
| Static obstacle (wall, chair leg) | 0.5 m/s | robot only |
| Walking human head-on | **1.9 m/s** | 1.4 m/s human + 0.5 m/s robot |
| Running cat | **4.5 m/s** | 4.0 m/s cat + 0.5 m/s robot |

*(inferred — human walking speed and domestic cat sprint speed are standard figures, not vendor specs.)*

### 7.4 Required detection range vs perimeter refresh — the decision table

Braking distance fixed at 83 mm (0.5 m/s, a = 1.5 m/s²); `d_margin` = 100 mm.

| Ring configuration | T_revisit | T_total | d_react static | d_react human | d_react cat |
|---|---|---|---|---|---|
| 8 ToF, **all fired simultaneously** (only legal with zero cone overlap) | 33 ms | **126 ms** | 0.246 m | 0.423 m | 0.750 m |
| 8 ToF, **2 optical groups of 4**, alternating | 66 ms | **159 ms** | 0.263 m | 0.485 m | 0.899 m |
| 8 ToF, **4 groups of 2** | 132 ms | **225 ms** | 0.296 m | 0.611 m | 1.196 m |
| 8 ToF, **strictly sequential**, 1 at a time | 264 ms | **357 ms** | 0.362 m | 0.861 m | 1.790 m |
| 12 ToF, strictly sequential | 396 ms | **489 ms** | 0.428 m | 1.112 m | 2.384 m |

*(computed from the chain in 7.2.)*

**Read the "cat" column.** Strictly sequential firing of an 8-sensor ToF ring requires the sensor to reliably see a small dark animal at **1.79 m**. The VL53L1X reaches only **1.70 m on a 17 % grey target in the dark**, and **0.68 m at 200 kcps/SPAD ambient** *(datasheet-verified — DS Table 7)*. **Strictly sequential firing is therefore not a viable architecture for pet detection with this sensor class.** The two-group scheme (0.899 m required vs 1.70 m available in the dark, 1.14 m at 50 kcps/SPAD) is the first configuration with real margin.

### 7.5 The derived refresh-rate requirement

Independent of detection range, a moving robot must not travel far between looks at the same bearing, or it will rotate a hazard out of one sector and into an unsampled one. A defensible rule *(inferred)*: **the robot must move no more than a quarter of its own radius between revisits.**

```
0.175 m / 4 = 44 mm;   44 mm / 0.5 m/s = 88 ms
```

**→ Full perimeter refresh ≤ 88 ms. Round to 10 Hz minimum, 20 Hz target.** At 0.3 m/s the same rule relaxes to 146 ms (≈ 7 Hz minimum).

That requirement is met by:

- **8 ToF in 2 optical groups at a 33 ms timing budget** (66 ms revisit). ✔
- **8 ToF simultaneously** if the cones genuinely do not overlap (33 ms). ✔
- **4 ToF sequential** at 33 ms (132 ms). ✘ at 0.5 m/s, ✔ at 0.3 m/s.
- **8 ToF sequential** (264 ms). ✘
- **Radar** — the LD2410 manual does not publish a frame rate. **Not published.** Observed community figures cluster near 10 Hz, which sits exactly on the boundary; treat radar as a *presence and classification* layer with 100 ms-class latency and let ToF own the collision-avoidance loop. *(inferred)*

### 7.6 The bus is not the bottleneck — prove it once and stop worrying

A VL53L1X result read is ~17 bytes ≈ **0.4 ms at 400 kHz**; a mux channel select adds **45 µs**. Twelve sensors per sweep = **5.3 ms**. *(computed.)* Against a 33 ms integration window that is 16 % overhead. Even at **100 kHz** — the speed you drop to for cable-capacitance headroom (Section 2.2) — twelve reads cost **21 ms**, which is still under one integration window and can be overlapped with it.

**Conclusion: run the ring at 100 kHz.** You buy 3.3× the capacitance headroom, you may skip the LTC4311, and you pay nothing you can measure in the latency budget.

---

## 8. Power budget

### 8.1 Measured and published per-node figures

| Node | Supply | Standby | Average active | Peak | Confidence / source |
|---|---|---|---|---|---|
| **VL53L1X** (bare module) | 2.8 V (AVDD + AVDDVCSEL) | HW standby **3 / 5 / 7 µA** (min/typ/max); SW standby **4 / 6 / 9 µA**; inter-measurement **20 µA** typ | **16 mA** typ, **18 mA** max, long-distance mode | **40 mA** peak including VCSEL | **datasheet-verified** — VL53L1X DS Table 16 |
| VL53L1X, 10 Hz @ 33 ms timing budget | 2.8 V | — | — | **20 mW max** | datasheet-verified — DS Table 16 |
| VL53L1X, 1 Hz @ 20 ms budget, no target | 2.8 V | — | **0.9 mW** typ | — | datasheet-verified |
| VL53L1X, 1 Hz @ 20 ms budget, target detected | 2.8 V | — | **1.4 mW** typ | — | datasheet-verified |
| Breakout overhead (LDO quiescent + power LED) | 3–5 V | — | **~3 mA** per board | — | **inferred** — typical STEMMA QT power LED |
| **HLK-LD2410** 24 GHz radar | **DC 5 V, supply must be capable of > 200 mA** | not published | **80 mA** rated; **80.62 mA measured average** | **152.17 mA measured max**; 41.25 mA measured min; 26.63 mA std dev | **datasheet-verified** — LD2410 manual Table 2 and Figure 11 (oscilloscope capture) |
| **DFRobot SEN0395** 24 GHz | 3.6–5 V | not published | **90 mA** | not published | vendor-page-verified — [SEN0395 wiki](https://wiki.dfrobot.com/sen0395/) |
| **DFRobot C4001 / SEN0610** | 3.3 V / 5 V | not published | **not published** | not published | vendor-page-verified — [SEN0610 wiki](https://wiki.dfrobot.com/SKU_SEN0610_Gravity_C4001_mmWave_Presence_Sensor_12m_I2C_UART) |
| TCA9548A / PCA9548 mux | 1.65–5.5 V | — | not read | — | — |
| LTC4311 | 1.6–5.5 V | — | not read | — | — |

The LD2410 figure deserves emphasis: Hi-Link published an actual oscilloscope current capture with **Max +152.1738 mA, Avg +80.62497 mA, Min +41.25372 mA, Std +26.62593 mA**, showing a hard-edged pulse train at roughly 30 pulses/s. *(datasheet-verified — LD2410 manual Figure 11.)* **The radar is a pulsed load, not a DC load.** That is why the manual says the supply must be capable of >200 mA for one module.

### 8.2 Six-sensor ring

| Configuration | Average current | Worst-case simultaneous peak | Average power @ 5 V |
|---|---|---|---|
| 6 × VL53L1X, all ranging concurrently | 6 × 16 = **96 mA** (+18 mA LEDs = 114 mA) | 6 × 40 = **240 mA** | 0.57 W |
| 6 × VL53L1X, **time-multiplexed 1-at-a-time** | 16 mA + 5 × 0.02 mA = **16.1 mA** (+18 mA LEDs) | **40 mA** | 0.17 W |
| 6 × VL53L1X in 2 groups of 3 | 3 × 16 = **48 mA** (+18 mA LEDs) | 3 × 40 = **120 mA** | 0.33 W |
| **6 × HLK-LD2410** | 6 × 80.6 = **484 mA** | 6 × 152.2 = **913 mA** | **2.42 W** avg / 4.57 W peak |
| 6 × DFRobot SEN0395 | 6 × 90 = **540 mA** | not published | 2.70 W |
| **Mixed: 4 ToF + 2 LD2410** | 64 + 161 = **225 mA** (+18 mA LEDs) | 160 + 304 = **464 mA** | 1.22 W |

*(all computed from the Section 8.1 figures.)*

### 8.3 Twelve-sensor ring

| Configuration | Average current | Worst-case simultaneous peak | Average power @ 5 V |
|---|---|---|---|
| 12 × VL53L1X, all concurrent | **192 mA** (+36 mA LEDs) | **480 mA** | 1.14 W |
| 12 × VL53L1X in 2 groups of 6 | **96 mA** (+36 mA LEDs) | **240 mA** | 0.66 W |
| 12 × VL53L1X strictly sequential | **16.2 mA** (+36 mA LEDs) | **40 mA** | 0.26 W |
| **12 × HLK-LD2410** | **967 mA** | **1.83 A** | **4.84 W** avg / **9.13 W** peak |
| **Mixed: 8 ToF + 4 LD2410** (the realistic build) | 128 + 322 = **450 mA** (+36 mA LEDs) | 320 + 609 = **929 mA** | **2.43 W** avg / 4.65 W peak |

*(all computed.)*

**Three conclusions fall straight out of these tables:**

1. **ToF power is irrelevant.** Even twelve of them concurrently is 192 mA. Do not time-multiplex ToF to save power; time-multiplex only to manage optical crosstalk.
2. **Radar power is not irrelevant.** Twelve 24 GHz modules is **4.84 W average and 9.13 W peak** — comparable to the whole compute load of a small robot, and enough to require a dedicated buck converter. This is the strongest practical argument for a hybrid ring with 3–4 radars rather than a radar-only ring.
3. **The power LEDs are a real line item** at 12 nodes (36 mA, 0.18 W). Cut the LED jumper on every breakout in the ring.

### 8.4 Wiring topology

**Do not daisy-chain power through STEMMA QT / Qwiic cable.** The cable is 28 AWG; **28 AWG is 0.2326 Ω/m**, **22 AWG is 0.0530 Ω/m** *(standard wire tables)*.

| Load | Wire | Round-trip length | Voltage drop |
|---|---|---|---|
| 0.93 A (12-node mixed peak) | 28 AWG | 1.0 m | **216 mV** |
| 0.93 A | 22 AWG | 1.0 m | **49 mV** |
| 1.83 A (12 radars peak) | 28 AWG | 1.0 m | **426 mV** |
| 1.83 A | 22 AWG | 1.0 m | **97 mV** |
| 0.10 A (one radar + one ToF branch) | 28 AWG | 1.0 m | **23 mV** |

*(computed.)* A 426 mV drop on a 5 V rail that a radar module needs at "DC 5 V" is not acceptable; a 23 mV drop is invisible.

**Recommended topology** *(inferred, from the arithmetic above)*:

```
        ┌──────────────── 5 V / 3 A buck ────────────────┐
        │   1000 µF bulk at the distribution board        │
        └───────┬───────────────┬───────────────┬─────────┘
       22 AWG   │      22 AWG   │      22 AWG   │      star, one leg per ring segment
        ┌───────▼──────┐ ┌──────▼───────┐ ┌─────▼────────┐
        │ ring seg. A  │ │ ring seg. B  │ │ ring seg. C  │
        │ 100 µF + 100 nF local per radar                │
        └───────┬──────┘ └──────┬───────┘ └─────┬────────┘
                │ short 28 AWG QT pigtails to each node
                ▼                ▼               ▼
        [ToF] [ToF] [radar]  [ToF] [ToF]    [radar] [ToF]

        I2C trunk (signal only) ── mux ── one 400/500 mm QT branch per ToF
        Radar UARTs ───────────── RP2040 concentrator (PIO) ── one link up
```

Rules:

- **Separate the power topology from the signal topology.** Power goes on a 22 AWG star; I2C goes on the QT branches. Use the QT cable's red/black only for the last ~100 mm to a node, or cut them entirely and power the node from the star.
- **100 µF electrolytic/polymer + 100 nF ceramic at every radar**, physically at the module, to absorb the 111 mA pulse edge (152 − 41 mA) without modulating the rail. *(inferred, standard practice for a pulsed RF load.)*
- **1000 µF bulk at the distribution point.**
- **JST SH (STEMMA QT/Qwiic) contacts are rated ~1 A** *(inferred / unverified — JST's own SH-series rating; neither Adafruit nor SparkFun publishes a current rating on the cable product pages)*. Treat 200 mA as the working limit per connector and do not trunk a ring through one.
- **One common ground reference.** A mmWave module whose ground returns through the I2C cable braid will inject its chirp pulse into SDA.

---

## 9. Integration decision summary

| Question | Answer for this robot | Confidence |
|---|---|---|
| ToF addressing | **PCA9548/TCA9548A mux** ($6.95), all sensors left at 0x29, XSHUT still wired to GPIOs for per-node recovery | inferred from vendor-verified specs |
| I2C bus speed | **100 kHz**, not 400 kHz — buys 3.3× capacitance headroom for zero measurable latency | computed |
| Bus extender | Not needed with a mux (116 pF computed). Add **LTC4311** ($9.95) only if measured C_b exceeds ~300 pF | computed |
| Cable | SparkFun 500 mm flexible Qwiic PRT-17257 ($2.75) for base-to-dome runs; Adafruit tops out at 400 mm ($1.50) | vendor-page-verified |
| ToF crosstalk | **Two optical groups fired alternately**, 8×8 ROI (20° FoV), decorrelated inter-measurement periods | inferred from ST guidance + datasheet FoV table |
| ToF window | Through-aperture per Section 5.2 table, ≤ 0.5 mm air gap, printed septum between Tx and Rx, per-unit crosstalk calibration after assembly | datasheet-verified cones, computed apertures |
| Radar count | **3 at 120° spacing** (±60° beam), metal backplane behind each | datasheet-verified beam width |
| Radar window | **100 %-infill puck**, thickness = n·λ0/(2√ε_r) ±20 %, standoff 12.4 or 18.6 mm ±1.2 mm, smooth surface, no metallic paint | datasheet-verified |
| Radar filament | ABS (ε_r 2.5 → 3.92 mm) or PLA (ε_r ≈ 2.75 → 3.75 mm) at 24.125 GHz. **PETG ε_r not published** | datasheet-verified / computed / not published |
| UART fan-in | **One RP2040 concentrator, 8 PIO UART RX** | inferred |
| Perimeter refresh target | **≤ 88 ms full ring (≥ 11 Hz); 20 Hz preferred** | computed |
| Power | 8 ToF + 4 radar = **450 mA avg, 929 mA peak, 2.43 W** on a dedicated 5 V/3 A buck with a 22 AWG star | computed |

---

## 10. Open items that a second pass should close

1. **ST AN5231** (single-zone cover glass) and **AN5856** (VL53L5CX cover glass) could not be downloaded — st.com timed out repeatedly in this pass. The exact air-gap thresholds, the 940 nm transmission requirement, the gasket dimensions and the crosstalk-calibration target distance/reflectance are all in those two documents and are currently carried here as second-hand quotes. Fetch both directly.
2. **VL53L5CX power consumption and frame rate** were not read from the datasheet. The 84 kB firmware upload at every power-up costs roughly **1.9 s per sensor at 400 kHz** *(computed: 84,000 bytes × 9 bits / 400,000 bit/s)*, which is a ~15 s boot for an 8-sensor ring — confirm against the datasheet and against a 1 MHz bus.
3. **STEMMA QT / Qwiic cable capacitance per metre** is published by nobody. Measure a 500 mm sample with an LCR meter at 100 kHz before committing to a bus speed.
4. **Minimum separation between two 24 GHz modules** is published by no vendor found in this pass. Measure it: two LD2410 on a bench, sweep the angle between them, log false-detection rate.
5. **LD2410 frame rate** is absent from the Hi-Link manual. Measure it on the UART.
6. **LTC4311 maximum bus capacitance.** No ADI-published maximum exists. The "4000 pF" that circulates is Adafruit's product-page wording; the datasheet says only "well beyond the 400 pF I2C specification limit" and its pull-up-current curves stop at 5000 pF. If the design is to depend on it, measure the built harness with an LCR meter and check the rise time on a scope — do not design to 4 nF on a reseller's sentence.
7. **SC16IS752 I2C address count** — the datasheet has an address map that was not reached in this pass; two address pins with multi-level encoding are commonly cited as giving 16 addresses. Confirm before designing a 4-bridge board.

---

## Sources

- [VL53L1X datasheet, DocID031281 Rev 3 (Pololu mirror)](https://www.pololu.com/file/0J1506/vl53l1x.pdf) — Tables 6, 7, 9, 10, 16, 17; Figures 12, 18, 19, 20
- [TI SWRA705, mmWave Radar Radome Design Guide, August 2021](https://www.ti.com/lit/an/swra705/swra705.pdf) — §2.3, §2.4, §3, §4, §6, §7, Table 3-1
- [HLK-LD2410 user manual V1.03](https://seengreat.com/upload/file/86/HLK+LD2410+Life+Presence+Sensor+Module+Manual+V1.03(220629).pdf) — §5.5, §6 Table 2, Figure 11, §7 Table 3
- [Waveshare, Impact of Radome on HMMD-mmWave-Sensor Performance](https://files.waveshare.com/wiki/HMMD-mmWave-Sensor/HMMD-mmWave-Sensor%20Radome%20Design%20Guide%20.pdf)
- [NXP SC16IS752/SC16IS762 data sheet Rev. 9.1, 5 Feb 2025](https://www.nxp.com/docs/en/data-sheet/SC16IS752_SC16IS762.pdf)
- [NXP P82B715 I2C-bus extender data sheet](https://www.nxp.com/docs/en/data-sheet/P82B715.pdf) and [AN10710](https://www.nxp.com/docs/en/application-note/AN10710.pdf)
- [Analog Devices LTC4311 product page](https://www.analog.com/en/products/ltc4311.html) — **analog.com would not respond in the 2026-09-12 pass**; the datasheet was read from the manufacturer PDF mirrored by Adafruit: [LTC4311 datasheet 4311fa](https://cdn-learn.adafruit.com/assets/assets/000/095/254/original/4311fa.pdf) (ADI's current revision is 4311fb — re-check the Features page when analog.com is reachable)
- [Adafruit TCA9548A 1-to-8 I2C Multiplexer, PID 2717](https://www.adafruit.com/product/2717)
- [Adafruit PCA9548 8-Channel STEMMA QT Multiplexer, PID 5626](https://www.adafruit.com/product/5626)
- [Adafruit PCA9546 4-Channel STEMMA QT Multiplexer, PID 5664](https://www.adafruit.com/product/5664)
- [Adafruit LTC4311 I2C Extender / Active Terminator, PID 4756](https://www.adafruit.com/product/4756)
- [Adafruit STEMMA QT / Qwiic JST SH 4-pin cable, PID 4210](https://www.adafruit.com/product/4210)
- [Adafruit VL53L4CX Time of Flight Sensor, PID 5425](https://www.adafruit.com/product/5425)
- [SparkFun Qwiic Mux Breakout 8-Channel TCA9548A, BOB-16784](https://www.sparkfun.com/sparkfun-qwiic-mux-breakout-8-channel-tca9548a.html)
- [SparkFun Flexible Qwiic Cable 500mm, PRT-17257](https://www.sparkfun.com/flexible-qwiic-cable-500mm.html)
- [Adafruit TCA9548A Arduino wiring and test guide](https://learn.adafruit.com/adafruit-tca9548a-1-to-8-i2c-multiplexer-breakout/arduino-wiring-and-test)
- [Adafruit VL53L0X Arduino code guide (XSHUT sequencing)](https://learn.adafruit.com/adafruit-vl53l0x-micro-lidar-distance-sensor-breakout/arduino-code)
- [ST Community: VL53L1X address changing](https://community.st.com/t5/imaging-sensors/vl53l1x-address-changing/td-p/162824)
- [ST Community: VL53L1X — will multiple sensors work together](https://community.st.com/t5/imaging-sensors/vl53l1x-will-multiple-sensors-be-able-to-work-together/td-p/112043)
- [ST Community: multiple sensors generate interference between each other](https://community.st.com/t5/imaging-sensors/multiple-sensors-generate-interference-between-each-other/td-p/206535)
- [ST Community: VL53L5CX gasket requirements with cover window and large air gap](https://community.st.com/t5/imaging-sensors/vl53l5cx-gasket-requirements-with-cover-window-and-large-air-gap/td-p/142460)
- [ST Community: Time-of-Flight cover glass article](https://community.st.com/t5/mems-and-sensors/time-of-flight-cover-glass/ta-p/49259)
- [ST AN5856, cover glass guidelines for the VL53L5CX](https://www.st.com/resource/en/application_note/an5856-guidelines-for-the-cover-glass-of-the-vl53l5cx-timeofflight-8x8-multizone-sensor-with-wide-field-of-view-stmicroelectronics.pdf) — **not opened in this pass**
- [ST AN5231, cover window guidelines for the VL53L1X](https://www.st.com/resource/en/application_note/an5231-cover-window-guidelines-for-the-vl53l1x-longdistance-ranging-timeofflight-sensor-stmicroelectronics.pdf) — **not opened in this pass**
- [DFRobot SEN0395 wiki](https://wiki.dfrobot.com/sen0395/)
- [DFRobot SEN0610 C4001 wiki](https://wiki.dfrobot.com/SKU_SEN0610_Gravity_C4001_mmWave_Presence_Sensor_12m_I2C_UART)
- [Complex permittivity and anisotropy measurement of 3D-printed PLA at microwaves and millimeter-waves](https://www.researchgate.net/publication/313543263_Complex_permittivity_and_anisotropy_measurement_of_3D-printed_PLA_at_microwaves_and_millimeter-waves)
