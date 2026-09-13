# fable-r2d2 electrical design, harness and commissioning

Written 2026-09-12 and revised the same day for revision D (the motorized,
interlocked stance change: section 11 and sheet 05). This document, the five
sheets in `electronics/` and
`electronics/wiring.csv` are one drawing set; the numbers behind them are in
`electronics/calculations.json`, which `electronics/generate.py` writes from
`research/loads.md` section 6 and `research/components-electronics.md`.

**Nothing here has been built or measured.** Every current, drop and runtime is
arithmetic on published ratings. Treat the commissioning section as the first real
measurement, not as a confirmation.

Regenerate everything with:

```
python scripts/electronics.py
```

That script runs the generator and then fails loudly if any KB2040 pin in
`wiring.csv` disagrees with `firmware/kb2040/code.py` (the `DRIVES` table, the
`ACTUATOR` entry and every single pin), if a KB2040 pin carries two nets, if a
firmware pin is not wired, or if the RP2040 PWM or ADC plan is illegal.

---

## 1. Power design

One 12 V sealed lead acid pack feeds one switched bus. Three switching regulators hang
off that bus, each behind its own fuse, and nothing else touches the bus except the
battery sense divider.

```
BT1 12 V 7 Ah SLA
  +--F2 blade--> J10 Powerpole --> FH1 [F1 15 A] --> SW1 rocker --+--> 12 V BUS
  |                                      ^                        |
  |                          FH2 [F2 3 A] |                        +--> FH3 [F3 3 A] --> U5  12 V -> 5 V
  |                                      |                        +--> FH4 [F4 5 A] --> U6  12 V -> 6 V (rail A)
  |                          J1 charge jack                       +--> FH5 [F5 5 A] --> U7  12 V -> 6 V (rail B)
  |                                                               +--> R2 100k / R3 15k --> U9 ADS1115 A0
  |                                                               +--> FH7 [F7 2 A] --> U10 DRV8871 --> ACT1 (rev D)
  |                                                               +--> R9 100k / R10 15k --> KB2040 A1 (rev D)
  +--F2 blade--> J10 Powerpole --> TB2 star ground
```

- **The charge branch joins the battery side of SW1.** The charger therefore reaches the
  battery with the robot switched off, and SW1 still isolates every load.
- **U5 (Pololu D36V50F5, 5 V)** feeds the Raspberry Pi through a USB-C plug breakout
  (J12), the PAM8302 amplifier (U8), and the whole dome through FH6 (F6 2 A) and the slip
  ring.
- **U6 (D36V50F6, 6 V, rail A)** feeds DRV8833 U1 (left foot) and U3 (centre foot).
- **U7 (D36V50F6, 6 V, rail B)** feeds DRV8833 U2 (right foot) and U4 (head drive).
  Splitting the two rails keeps a stalled foot from pulling the head drive down.
  In revision D it also feeds the two MG995 release servos (SV1, SV2). The servos
  move only while ground drive and the dome are refused, so rail B carries either
  3 A of motors or 3 A of servo stall, never both.
- **U10 (DRV8871) is fed straight from the 12 V bus through FH7 (F7 2 A).** The
  actuator is a 12 V part; the DRV8833 boards stop at 10.8 V and cannot drive it.
- **Never feed a DRV8833 from the 12 V bus.** Its maximum motor supply is 10.8 V.
- **The KB2040 is powered only by the Pi's USB port** (cable J11). Do not also connect
  its RAW pin to the 5 V rail.
- **The Pi is powered only through its USB-C input** (J12). Do not also feed 5 V into
  header pins 2 and 4.

### Rail currents (from `electronics/calculations.json`)

| Rail | Load | Current | Source |
| --- | --- | --- | --- |
| 5 V | Pi 0.60 A, four matrices 0.15 A, NeoPixels 0.30 A average, TFT 0.10 A, KB2040 0.05 A, amplifier 0.20 A | **1.40 A at 5 V = 7.0 W** | loads.md section 6 |
| 12 V | the 5 V rail at 90 percent converter efficiency | **0.648 A** | calculated |
| 12 V | driving: six drive motors at 0.385 A / 6 V plus the head motor | **1.422 A** on top of idle | loads.md section 2 |
| 12 V | worst case, seven motors at the DRV8833 1 A limit, plus idle | **4.537 A** | calculated |
| 12 V | stance change (rev D): idle, actuator stall 1.0 A, two servo stalls of 1.5 A at 6 V; ground and dome motors refused | **3.315 A** | calculated |

### Runtime, to 50 percent depth of discharge (3.35 Ah usable)

| Profile | 12 V current | Runtime |
| --- | --- | --- |
| Idle, displays running | 0.65 A | 5.2 h |
| Continuous driving | 2.07 A | 1.6 h |
| Mixed, half the time driving | 1.36 A | 2.5 h |
| Worst case, every motor at its limit | 4.54 A | 0.7 h |

Running down to 11.2 V gives more minutes and fewer cycles. `firmware/pi/battery.py`
calls 12.70 V full, 11.60 V empty and 11.20 V critical.

---

## 2. Charging procedure

The charger is a PowerStream PST-P2012-A12B: three stage, 1.5 A bulk, 14.75 V absorb,
13.75 V float, with a 5.5 mm OD x 2.1 mm ID **centre positive** barrel plug. The robot's
jack is a Switchcraft L722A (J1) in the rear lower band of `body_lower`, next to the
rocker switch.

1. **Switch the robot OFF at SW1.** The charge path does not need the switch, and a
   running robot confuses the charger's stage detection.
2. Stand the robot upright, or lay it on its back with the battery shelf horizontal.
   **Never charge it inverted** and never inside a closed box or bag.
3. Check the ambient temperature: **do not charge below 0 C**, and do not charge above
   40 C. A cold SLA accepts charge badly and can be damaged.
4. Plug the charger into J1, then into the mains. Plugging into the mains first puts a
   live plug into your hand.
5. Read the charger LED: **red = bulk or absorption in progress, green = float**. Red
   that never turns green after about eight hours means the pack, the fuse F2, or the
   plug polarity is wrong; unplug and investigate rather than leaving it.
6. Expect **6 to 7 hours** from a half-flat pack: about 2.6 h of bulk at 1.5 A, then the
   absorption tail. Leaving it on float overnight is safe and is how an SLA likes to live.
7. Unplug the mains first, then J1.
8. Optional check: with the charger off and the robot off, the pack should settle to
   12.7-12.9 V within an hour. Below 12.4 V after a full charge means the pack is tired.

A reversed plug blows F2 immediately. Check the plug with a meter before the first
charge: centre pin positive with respect to the sleeve.

---

## 3. Fuse table

Every fuse is an ATO/ATC blade in a Littelfuse FHAC0001ZXJ in-line holder.

| Fuse | Holder | Rating | Circuit | Worst-case load | Part |
| --- | --- | --- | --- | --- | --- |
| F1 | FH1 | 15 A | Main, battery positive lead, within 100 mm of the terminal | 4.54 A | Littelfuse 0287015.PXCN |
| F2 | FH2 | 3 A | Charge jack J1 to the battery side of SW1 | 1.5 A (charger) | 0287003.PXCN |
| F3 | FH3 | 3 A | 12 V bus to U5 (5 V regulator) | 0.65 A idle, 1.4 A peak | 0287003.PXCN |
| F4 | FH4 | 5 A | 12 V bus to U6 (6 V rail A, four motors) | 2.2 A | 0287005.PXCN |
| F5 | FH5 | 5 A | 12 V bus to U7 (6 V rail B, three motors) | 1.7 A | 0287005.PXCN |
| F6 | FH6 | 2 A | 5 V rail to the slip ring (the whole dome) | 1.62 A | 0287002.PXCN |
| F7 | FH7 | 2 A | 12 V bus to the DRV8871 actuator driver U10 (rev D) | 1.0 A stall, 0.895 A driver limit | 0287002.PXCN |

Notes.

- F1 is sized for the 16 AWG lead and the 20 A switch, not for the load. `loads.md`
  section 6 would allow 7.5 A; the larger fuse still protects the cable (22 A chassis
  rating) and avoids nuisance blows on motor inrush.
- F6 replaces the 1.5 A polyfuse `loads.md` proposed. The dome worst case (1.02 A of
  NeoPixels at full white, 0.50 A of matrices, 0.10 A of TFT) is 1.62 A, which a 1.5 A
  device would eventually trip. The firmware caps NeoPixel brightness at 0.4, so the
  normal figure is nearer 0.4 A.
- Keep two spares of each value in the robot. They cost $0.44 each.

---

## 4. Wire gauge table

Chassis ratings are the Powerstream table quoted in `loads.md` section 6.

| Gauge | Chassis rating | Used for | Worst case | Margin |
| --- | --- | --- | --- | --- |
| 16 AWG silicone | 22 A | Battery leads, F1, SW1, charge branch, the three regulator inputs, regulator grounds, the 5 V feed to the Pi | 4.54 A | 4.8x |
| 22 AWG silicone | 7 A | 6 V branches to the drivers, motor extensions, dome feed, display and NeoPixel signals, audio | 4.0 A | 1.8x |
| 28 AWG (factory) | 1.4 A | The TT motors' own leads and the slip-ring leads | 1.0 A (DRV8833 limit) | 1.4x, keep them short |

Voltage drop that matters:

- **Pi 5 V feed**: 16 AWG under 250 mm gives 31 mV of loop drop at 3 A. The Pi wants
  more than 4.75 V at its connector, so this run must stay short and must not be
  daisy-chained through anything.
- **Motor leads**: the stock 28 AWG pair drops 85 mV over 200 mm at 1 A. Splice to
  22 AWG inside the foot shell and keep the thin part as short as the foot allows.
- **Slip ring**: 28 AWG leads, 2 A per ring. Two rings carry 5 V and two carry the
  return, so the dome has 4 A of capacity against a 1.62 A worst case.

Colour code used in `wiring.csv`, matching the six-colour 22 AWG kit:

| Colour | Meaning |
| --- | --- |
| red | any positive supply (12 V, 6 V, 5 V, 3V3) |
| black | ground, every return |
| yellow | motor OUT1, SCL, SLP, TFT RST, audio right, speaker plus |
| blue | motor OUT2, SPI MOSI and SCLK, speaker minus, lock switch NC (rev D) |
| green | PWM inputs, NeoPixel data, TFT CS, index sensor |
| white | direction inputs, SDA, TFT DC, audio left and summed, lock switch NO (rev D) |

Because colours repeat across functions, flag both ends of every signal wire with a
printed or written heat-shrink label. In the motor pairs, **yellow is OUT1 and blue is
OUT2**.

---

## 5. Connector list

| Ref | Connector | Where | Notes |
| --- | --- | --- | --- |
| J10 | Anderson Powerpole 15 A, two pairs (red and black housings) | Battery lead to the harness | 16-20 AWG contacts; the only disconnect between the pack and the robot |
| TB1 | Six insulated 0.250 inch female spades (TE 3-520408-2) | Battery terminals and SW1 | Two battery, two switch, two spare |
| J1 | Switchcraft L722A panel jack | Rear lower band of `body_lower` | 5.5 x 2.1 mm, centre positive |
| SW1 | Carling rocker, 20 A | Rear lower band, cutout 36.83 x 21.08 mm | 0.250 inch quick connects |
| FH1-FH7 | In-line ATO holders | On the tray, except FH1 which sits at the battery | Label each holder with its fuse value |
| J2-J9 | JST-XH 2 pin pairs (Adafruit 4872) | One per motor at its DRV8833 output, plus one spare | Male half at the driver |
| J11 | USB A to USB C, 1 m (Adafruit 4474) | Pi USB 2.0 port to the KB2040 | Power and the CDC serial link |
| J12 | USB Type C plug breakout (Adafruit 5978) | U5 VOUT to the Pi USB-C power input | Its 5.1 k CC1 resistor is what makes the Pi accept the supply |
| J13A, J13B | 300 mm servo extensions (Pololu 2184) | Tray to the left and right release servos | Signal from U11 HV1/HV2, V+ from U7, GND to TB2 (rev D) |
| J14 | STEMMA QT to male headers, 150 mm (Adafruit 4209) | KB2040 STEMMA QT to the right lock switch SW3 | Blue SDA = NO, yellow SCL = NC, black = COM; red 3V3 insulated (rev D) |
| SR1 | Adafruit 1195 slip ring, 12 wires | Clamped in the printed post on the body top plate | See the wire table below |
| TB2 | Star ground stud | Electronics tray | Every return lands here and nowhere else |

---

## 6. Slip-ring wire table (Adafruit 1195, 12 wires, 2 A each)

| Wire | Net | Body (stator) side | Dome (rotor) side |
| --- | --- | --- | --- |
| 1 | 5V-DOME | FH6 output (F6 2 A), 5 V rail | dome 5 V bus: DS5 VIN, LED1/LED3/LED5 |
| 2 | 5V-DOME | FH6 output, second leg | dome 5 V bus: DS1-DS4, LED2/LED4 |
| 3 | GND | TB2 star ground | dome ground: DS5, LED1/LED3/LED5 |
| 4 | GND | TB2 star ground, second leg | dome ground: DS1-DS4, LED2/LED4 |
| 5 | NEOPIXEL | KB2040 `A2` | LED1 DIN (front PSI), then the chain |
| 6 | SDA | Pi GPIO2, header pin 3 | DS1-DS4 SDA (0x70, 0x71, 0x72, 0x73) |
| 7 | SCL | Pi GPIO3, header pin 5 | DS1-DS4 SCL |
| 8 | SPI-MOSI | Pi GPIO10, header pin 19 | DS5 MOSI |
| 9 | SPI-SCLK | Pi GPIO11, header pin 23 | DS5 SCK |
| 10 | TFT-CS | Pi GPIO8 (CE0), header pin 24 | DS5 CS |
| 11 | TFT-DC | Pi GPIO25, header pin 22 | DS5 DC |
| 12 | TFT-RST | Pi GPIO24, header pin 18 | DS5 RST |

The TFT backlight is **not** on the slip ring. `LITE` is tied to the dome 5 V bus
through R1 (100 ohm) inside the dome, which gives a steady, slightly reduced brightness
and one less wire to lose. `firmware/pi/displays.py` still drives GPIO18 as its backlight
pin; with R1 fitted that pin controls nothing and can be left unconnected.

Mechanical: body 12.4 mm diameter x 19.5 mm, no flange, 150 mm of 28 AWG lead each side,
300 RPM maximum. Clamp the body in the printed post on the body top plate and cable-tie
both bundles within 40 mm of the ring so no ring lead ever takes a pull.

---

## 7. Harness assembly order

Build the harness on the bench, in this order, before anything goes into the body. Do
not connect the battery until step 11.

1. **Star ground first.** Fit TB2 on the electronics tray. Everything below returns here.
2. **Tray boards.** Mount U5, U6, U7, the four DRV8833 boards (U1-U4), U9 (ADS1115),
   U8 (PAM8302), U10 (DRV8871) and U11 (BSS138 level shifter) on M3 nylon standoffs.
   Leave room for the fuse holders. On U10, replace the factory 30 k ILIM resistor
   with R5 71.5 k before mounting.
3. **12 V bus.** Make up the 16 AWG bus: SW1 load side to TB2's 12 V stud, then FH3, FH4
   and FH5 from that stud to the three regulator inputs. Fit no fuses yet.
4. **Battery branch.** Crimp the Powerpole pair (J10), the spade terminals (TB1) and
   FH1. Keep FH1 within 100 mm of where the battery's positive terminal will be.
5. **Charge branch.** J1 centre pin to FH2 to the *battery* side of SW1; J1 sleeve to
   TB2. Check the polarity with a meter now, while it is easy to reach.
6. **Regulator outputs.** U5 to J12 (Pi), U5 to FH6, U5 to U8; U6 and U7 to their two
   DRV8833 boards each. Ground each regulator back to TB2 with 16 AWG.
7. **Signal harness.** KB2040 to the four drivers: one PWM and one direction wire per
   foot and for the head, with AIN1-BIN1 and AIN2-BIN2 jumpers on U1, U2 and U3, and
   the four SLP pins tied to the KB2040 3V3 pad, per `wiring.csv` and sheet 02. Then
   the stance signals per sheet 05: D8/D9 to U10, D0/D1 through U11 to J13A/J13B,
   the pull-ups R6A-R6D, R7 and R8 at the KB2040, R9/R10 on A1, and J14 on the STEMMA
   QT connector. Label both ends.
8. **Motor leads.** Crimp a JST-XH pair per motor. Route through the legs with the
   ankle bolts loose so the wires are not trapped. Splice 28 AWG to 22 AWG inside each
   foot. Run the actuator's five leads down the centre leg (red/black to U10, yellow
   through R7, orange to the KB2040 GND pad, purple to A0) and the SW2/SW3 leads and
   servo extensions to the shoulders, with slack for the full 5-86 mm stroke (hard stop at 86.0 mm).
9. **Dome harness.** Solder the slip ring's twelve stator leads to the body side per the
   table in section 6, then the twelve rotor leads to the dome devices. Do the dome
   soldering with the dome off the robot and the backpack address jumpers already
   bridged.
10. **Audio.** Pi jack to R4A and R4B into U8 A+, jack sleeve to U8 A-, U8 to LS1. The
    two speaker leads go nowhere near ground.
11. **Rail check.** Run section 8 before the Pi, the drivers or the dome are connected.
12. **Close up.** Cable-tie the harness to the adhesive mounts, check nothing crosses a
    wheel, a rod or the lazy susan, and fit the dome last.

---

## 8. Commissioning: rail checks with a multimeter

Do this with the loads disconnected. Each step ends with the power off.

| Step | Do this | Expect | If not |
| --- | --- | --- | --- |
| 1 | All fuses out, battery connected, SW1 off. Meter across the bus studs, then at FH1's input | 0 V at the bus, 12.4-13.0 V at FH1 | A reading at the bus means SW1 is wired through, or a fuse holder is bridged |
| 2 | Fit F1 only, SW1 on. Meter at the bus studs | 12.0-13.0 V | 0 V: check F1, SW1 terminals, the Powerpole crimps |
| 3 | SW1 off. Fit F3. SW1 on. Meter U5 VOUT to ground | 5.00 V +/- 0.2 V | Over 5.5 V or unstable: stop, the regulator is wrong or damaged |
| 4 | SW1 off. Fit F4 and F5. SW1 on. Meter U6 VOUT and U7 VOUT to ground | 6.0 V +/- 0.25 V each | More than 6.5 V at a DRV8833 input is out of spec |
| 5 | SW1 off. Connect J12 (Pi), the driver VMOTOR leads and FH6 (dome). SW1 on | Pi boots, no rail sags below its tolerance under load | A sagging 5 V rail usually means the Pi feed is too long or too thin |
| 6 | With the Pi running, compare the battery gauge to the meter at the battery terminals | Within 0.15 V | Check R2 (100 k) and R3 (15 k) and the ADS1115 address (0x48) before trusting the gauge |
| 7 | Wheels off the ground, robot on three feet. `E 1` then `M 300 0 0 0` on the KB2040's serial port | Both left-foot motors turn, forward | If a motor turns the wrong way, swap its two leads at the driver output |
| 8 (rev D) | F7 out. Resistance across U10's ILIM pads | 71.5 k (R5 fitted, factory 30 k removed) | 30 k means a 2.1 A limit: fix before fitting F7 |
| 9 (rev D) | Actuator detached. Read `ss` while moving the rod by hand end to end | `pos` follows the rod; wiper 0-2912 mV | Set `POT_ZERO_MV` / `POT_FULL_MV` in `stance.py`; a -1 reading is an open pot wire |
| 10 (rev D) | Press and release each lock lever by hand | `ss` locks read `E` pressed, `R` released; unplugging either contact wire gives `X` within 0.15 s | `X` with both wires fitted: check COM and the 3.3 k pull-ups |
| 11 (rev D) | Battery meter against `ss` pack_mv | Within 0.15 V | Check R9 (100 k) and R10 (15 k) on A1 |

Do not skip step 1. A bridged fuse holder on a pack that can deliver roughly 457 A into
a short is how harnesses catch fire.

---

## 9. Safety

- **The battery is the hazard, not the electronics.** A 12 V 7 Ah SLA delivers about
  457 A into a dead short (108 A for 5 s is the datasheet figure). Fuse first, then wire.
- **F1 goes within 100 mm of the battery's positive terminal.** A fuse further down the
  lead does not protect the lead.
- **Insulate both F2 blades** with the supplied boots or heat-shrink. A dropped spanner
  across the terminals welds itself in place.
- **An SLA vents hydrogen when it is charged.** Charge it upright, in free air, never in
  a sealed box, never inverted, never below 0 C.
- **Never charge through the main switch.** The charge branch is separate on purpose.
- **A stopped motor coasts; it does not brake.** In revision D the DRV8833 SLP pins are
  tied high and the firmware holds disarmed outputs at coast. The only guaranteed
  disconnect is SW1 off and, for any work inside the body, the Powerpole pair unplugged.
- **The actuator does not back-drive** (over 500 N). A pinch point at the centre leg
  stays pinched when power is removed: keep hands clear during a stance change.
- **The PAM8302 output is a bridge.** Grounding either speaker lead destroys it.
- **Do not connect USB to the KB2040 while the 5 V rail also feeds it.** The Pi's port is
  its only supply.
- **PETG softens at 62-68 C.** Do not leave the robot in a hot car; the battery dislikes
  it even more than the prints do.
- This is a hobby robot, not a certified machine. Nothing in this set has been validated
  on hardware.

---

## 10. Where each number comes from

| Number | Source |
| --- | --- |
| Motor current 0.385 A at 6 V, head 0.5 A at 3 V | `research/loads.md` section 2 |
| 5 V load table, fuse minimums, wire ampacity, runtime | `research/loads.md` section 6 |
| Power tree, part numbers, prices, stock | `research/components-electronics.md` |
| KB2040 pin map, protocol, stop behaviour | `firmware/kb2040/code.py`, `docs/firmware.md` |
| Matrix addresses, SPI pins, backlight pin | `firmware/pi/displays.py` |
| Battery divider (100 k / 15 k, ADS1115 at 0x48) | `firmware/pi/battery.py` |
| Where each part sits in the robot | `cad/params.scad` |
| Wire-by-wire connections and length estimates | `electronics/wiring.csv` |
| Stance mechanism values, lock and servo timing, battery thresholds (rev D) | `firmware/kb2040/stance.py` `MECHANISM CONSTANTS`, from the stance-mechanism CAD of 2026-09-12 |
| DRV8871, BSS138, P16, SS-01GL, MG995, cable part data and prices (rev D) | the product pages listed in `bom/electronics.csv`, read 2026-09-12 |

---

## 11. Revision D stance change wiring (sheet 05)

Sheet `05-stance-actuator-and-lock.svg` draws all of it; `wiring.csv` has every wire.
Values not on the sheet are in `electronics/calculations.json` under `stance_change`.

| Part | Connections | Notes |
| --- | --- | --- |
| U10 Adafruit DRV8871 (3190) | VM <- FH7 (F7 2 A) <- 12 V bus; GND -> TB2; logic GND -> KB2040 GND pad; IN1 <- D8; IN2 <- D9; OUT1/OUT2 -> ACT1 red/black | R5 71.5 k replaces the factory 30 k ILIM resistor: I_TRIP = 64 / 71.5 = 0.895 A against the 1.0 A actuator stall. 3.3 V logic drives IN1/IN2 directly. |
| ACT1 Actuonix P16-100-256-12-P | yellow (pot +) <- R7 2.2 k <- KB2040 3V3; orange (pot -) -> GND pad; purple (wiper) -> A0 with R8 470 k to GND | 11 k pot: 0-2750 mV nominal, 2912 mV at +50 %. An open wiper or pot + reads near 0 mV, an open pot - near 3300 mV: both leave the 40-3000 mV window and latch FEEDBACK. |
| SW2 left lock, Omron SS-01GL | COM -> GND pad; NO -> SCK; NC -> MISO; R6A/R6B 3.3 k to 3V3 | Seated = NO closed. 1 mA through the closed contact at 3.3 V. |
| SW3 right lock, Omron SS-01GL | COM -> J14 black; NO -> J14 blue -> SDA (GP12); NC -> J14 yellow -> SCL (GP13); R6C/R6D 3.3 k to 3V3 | Through the STEMMA QT connector; the KB2040 has no other free pins. |
| U11 Adafruit BSS138 level shifter (757) | LV <- 3V3; HV <- U5 5 V; GND -> GND pad; LV1 <- D0, HV1 -> J13A; LV2 <- D1, HV2 -> J13B | Gives the servos a 5 V signal. Channels 3 and 4 unused. |
| SV1, SV2 TowerPro MG995 (Adafruit 1142) | signal <- J13A/J13B; V+ <- U7 6 V rail B; GND -> TB2 | 50 Hz on PWM slice 0. Engage 1500 us, release 1321 us left and 1679 us right (16.3 deg, calibrate). No pulse 1 s after engaging. 6.0 V at the plug gives 19 % release-force margin; the check still passes at 4.8 V. |
| R9 / R10 KB2040 battery divider | 12 V bus -> R9 100 k -> A1 -> R10 15 k -> GND pad | 12.70 V reads 1.657 V at A1. The bottom leg returns at the KB2040 so the USB ground offset stays out of the reading. |
| DRV8833 SLP (U1-U4) | SLP <- KB2040 3V3 pad | Tied high to free D1. Arming and stopping are done in firmware. |

Purchased pieces added for revision D, all in `bom/electronics.csv`: U10, U11, ACT1,
SW2-SW3 (2), SV1-SV2 (2), J13A-J13B (2), J14, FH7 (holder count 6 -> 7), F7, R3
(count 1 -> 2, used as R10), R5, R6A-R6D (4), R7, R8. That is 20 pieces. R9 comes
from the existing 100 k pack (R2). Nothing has been bought, built or measured.
