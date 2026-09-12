# Wiring, bus, aperture and power

## I2C address collisions: every VL53 boots at 0x29

Two VL53 parts on one bus collide silently: both ACK, and a read returns their wire-AND, so you get
wrong distances rather than a fault code. The VL53L1X boots at 7-bit 0x29 (8-bit write 0x52),
400 kbit/s maximum
([VL53L1X DS DocID031281 Rev 3](https://www.pololu.com/file/0J1506/vl53l1x.pdf) Section 4,
datasheet-verified); L0X, L4CD, L4CX, L5CX, L7CX and L8CX share it. The remedy is volatile: the
address lives in RAM, not NVM, and is lost on every power cycle and every XSHUT assertion
([Adafruit](https://learn.adafruit.com/adafruit-vl53l0x-micro-lidar-distance-sensor-breakout/arduino-code),
vendor-page-verified).

### Approach A: XSHUT sequencing

All SDA/SCL on one shared bus; each sensor's XSHUT (active-low reset) on its own GPIO, driven, not
floating. Breakouts pull XSHUT to VDD, so at power-up every sensor wakes at 0x29 together. N sensors
costs N GPIOs, hence an MCP23017 expander (16 I/O at 0x20-0x27) on a 12-node ring.

```
1. Drive ALL XSHUT low.                      // every sensor in reset, bus empty
2. delay(10 ms).                             // Adafruit's published settling delay
3. for i in 0..N-1:
       drive XSHUT[i] HIGH                   // exactly one sensor wakes, at 0x29
       delay(10 ms)
       sensor[i].begin(0x29)
       VERIFY: model-ID register 0x010F      // VL53L1X returns 0xEA,0xCC,0x10
       sensor[i].setAddress(0x30 + 2*i)
       VERIFY: model-ID at the NEW address, and that 0x29 no longer ACKs
       // if either verify fails: ABORT LOUDLY. Do not continue.
```

Verify every step: a missed write leaves a second device at 0x29, and every later `begin(0x29)` then
talks to two chips silently. Space addresses by 2, because libraries are ambiguous about 7-bit versus
8-bit ([ST Community](https://community.st.com/t5/imaging-sensors/vl53l1x-address-changing/td-p/162824),
vendor-page-verified). Use 0x30-0x3F; 0x00-0x07 and 0x78-0x7F are reserved, 0x70-0x77 is the mux
block, 0x20-0x27 the MCP23017. Probe 0x29 in service - an ACK means a brown-out has reset a node,
so re-run the whole sequence.

### Approach B: TCA9548A / PCA9548 multiplexer

| Part | Channels | USD 1-off | Source |
|---|---|---|---|
| Adafruit TCA9548A, PID 2717 | 8 | 6.95 | [product/2717](https://www.adafruit.com/product/2717) |
| Adafruit PCA9546 QT, PID 5664 | 4 | 3.95 | [product/5664](https://www.adafruit.com/product/5664) |
| SparkFun Qwiic Mux, BOB-16784 | 8 | 6.95 | [sparkfun](https://www.sparkfun.com/sparkfun-qwiic-mux-breakout-8-channel-tca9548a.html) |

Vendor-page-verified, read 2026-09-12; all occupy 0x70-0x77. Host bus to the trunk, one SDn/SCn
branch per sensor, all sensors left at 0x29, XSHUT tied high.

```
void tcaselect(uint8_t ch) {          // ch = 0..7
  Wire.beginTransmission(0x70);
  Wire.write(1 << ch);                // BITMASK, not an index
  Wire.endTransmission();
}
tcaselect(i);                         // before EVERY sensor transaction
sensor.readRangeContinuousMillimeters();
```

Writing 0x03 enables two channels at once and recreates the collision the mux was bought to prevent.
Wire mux RESET to a GPIO: a wedged mux takes the ring down, and this is the only recovery short of a
power cycle. Interrupts are not muxed - the data-ready line bypasses it, so poll or give each its own
pin. A channel select costs 45 us at 400 kHz (computed), negligible against 33 ms.

### Which to use

| Sensors | Choice | Reason |
|---|---|---|
| 4 | One PCA9546, 3.95 USD | Cheaper than 4 GPIOs plus boot code |
| 8 | One 8-channel, 6.95 USD | Branch isolation keeps the bus in spec |
| 12 | 8-channel + 4-channel, 10.90 USD | Cascades to 64 branches; beats XSHUT for the remainder |

XSHUT costs N GPIOs, re-runs every boot, gives no fault isolation, and leaves every branch's cable
capacitance permanently on the bus. Recommended (inferred): mux for addressing, XSHUT still wired to
GPIOs as a per-node hardware reset.

## Bus integrity over 300-800 mm of cable

The 3.3 V ceiling is about 366 pF at 400 kHz, not the 400 pF of the I2C specification. From
`t_R = 0.8473 * R_p * C_b`, V_OL 0.4 V at 4 mA and the 3 mA sink limit, `R_p,min = 967 ohm`, so
`C_b,max = 300 ns / (0.8473 * 967) = 366 pF` at 400 kHz and 1220 pF at 100 kHz (computed from
VL53L1X DS Tables 10 and 17, datasheet-verified). Qwiic cable capacitance is **not published**;
28 AWG 4-conductor is typically 40-70 pF/m (inferred - measure yours). Adafruit tops out at 400 mm
(1.50 USD, PID 4210), SparkFun's flexible 500 mm is 2.75 USD (PRT-17257), and a base-to-dome run is
600-900 mm. Budget for 8 sensors on 800 mm branches at 60 pF/m, 10 pF per device pin, 5 pF per board
(computed):

| Topology | Cable | Devices + boards | Host | Total |
|---|---|---|---|---|
| One shared bus (XSHUT) | 384 pF | 120 pF | 20 pF | **524 pF** |
| Muxed, one branch live | 66 pF | 30 pF | 20 pF | **116 pF** |

The shared bus fails at 400 kHz and is marginal at 100 kHz. A mux divides capacitance by the branch
count; that, not addressing, is the decisive argument for it. Under 250 pF use 400 kHz with 2.2 kohm
pull-ups; at 250-366 pF use 1 kohm pull-ups or drop to 100 kHz.

Above 366 pF, inside the chassis, add one **LTC4311** active pull-up at the far trunk end, 9.95 USD
(Adafruit 4756), 1.6-5.5 V, 400 kHz maximum. Sources disagree on its ceiling: Adafruit says 4000 pF,
the [datasheet](https://cdn-learn.adafruit.com/assets/assets/000/095/254/original/4311fa.pdf) says
only "well beyond the 400 pF I2C specification limit" and tabulates one condition, 300 ns rise at
400 pF and 3 V. Prefer the datasheet and design to a measured rise time. A **P82B715** pair is for
runs leaving the chassis and is overkill on a 350 mm robot; sources disagree there too, its features claiming
3-12 V against 4.5-12 V guaranteed, so it is out of range on a 3.3 V ring
([NXP](https://www.nxp.com/docs/en/data-sheet/P82B715.pdf)). Neither part fixes an address collision
and neither raises the 400 kHz ceiling.

**A marginal bus never fails cleanly.** Reads of 0xFF; a sensor that works alone and fails with a
neighbour plugged in; faults only while driving, as cables flex; NACKs that track temperature; and
worst, stable but wrong distances. Scope SDA and measure rise time before believing any software
explanation.

## Optical crosstalk and time-multiplexed firing

Sensor-to-sensor crosstalk is not cover-glass crosstalk, and no calibration fixes it: A's 940 nm
photons reach B's SPAD array, indistinguishable from ambient. ST's engineers say sensors at different
angles do not meaningfully interfere, but that with directly overlapping fields "the interference can
be very large and the data unusable"
([ST Community](https://community.st.com/t5/imaging-sensors/multiple-sensors-generate-interference-between-each-other/td-p/206535),
vendor-page-verified). The price is in the ambient table (DS Table 7, long-distance mode, 100 ms
budget, datasheet-verified):

| Target reflectance | Dark | 50 kcps/SPAD | 200 kcps/SPAD |
|---|---|---|---|
| White 88 % | 360 cm | 166 cm | 73 cm |
| Grey 54 % | 340 cm | 154 cm | 69 cm |
| Grey 17 % | 170 cm | 114 cm | 68 cm |

Up to 80 % of range is lost on a bright target and 60 % on a dark one. Worse is the phantom close
target: an interferer's pulse inside the victim's histogram window reports a range that never
existed, and the robot stops intermittently in an empty room.

1. **Geometric separation.** Aim the cones so they do not overlap inside the first 0.5 m. ST's ROI
   table (DS Table 9) gives 27, 20 and 15 deg full field of view for 16x16, 8x8 and 4x4 regions of
   interest, and those are DIAGONAL angles; the horizontal equivalents are **not published**, so do
   not size a ring from a horizontal figure nobody publishes. A smaller ROI shrinks cone and range
   together, 170 cm to 45 cm on 17 % grey, dark, 100 ms, partial-field. An 8x8 ROI - 20 deg, 119 cm
   on 17 % grey in the dark - is the better compromise for a perimeter.
2. **Group-parallel firing.** Two optical groups of non-adjacent sensors, fired alternately: overlap
   removed at 2x latency instead of 8x. Recommended (inferred).
3. **Strict time-multiplexing**, stopping and starting ranging through the driver, never by toggling
   XSHUT, which loses the assigned address.
4. **A longer timing budget** averages interference down but opposes the latency budget;
   **decorrelated periods** (40, 41, 43, 47 ms) leave outliers a 3-of-5 median filter removes
   (inferred).

Ambient loss is worst on low-reflectance targets, so ignoring this lands hardest on a dark-furred cat
on a dark carpet.

## Apertures: a ToF sensor cannot see through a printed shell

Every ToF sensor needs its own clear aperture. A printed wall is either opaque or translucent and
scattering, and the second is worse: it diffuses emitted photons back into the receiver and the
sensor reports a fixed short range. ST specifies keep-out cones from a datum at the module cap:
emitter 36.50 deg full angle from 0.84 mm diameter, receiver 39.60 deg from 1.08 mm, optical centres
3 +/- 0.02 mm apart (DS Figure 19, drawing DM00319387 Rev 3.0, datasheet-verified). Aperture at
standoff H, from `D_em = 0.84 + 0.660*H` and `D_rx = 1.08 + 0.720*H` (computed):

| Standoff H (mm) | Emitter dia. | Receiver dia. | Single oval |
|---|---|---|---|
| 0.5 | 1.17 mm | 1.44 mm | 4.31 x 1.44 mm |
| 1.0 | 1.50 mm | 1.80 mm | 4.65 x 1.80 mm |
| 2.0 | 2.16 mm | 2.52 mm | 5.34 x 2.52 mm |
| 3.0 | 2.82 mm | 3.24 mm | 6.03 x 3.24 mm |
| 5.0 | 4.14 mm | 4.68 mm | 7.41 x 4.68 mm |

A narrower hole clips the cone, which vignettes the field, kills range asymmetrically, and raises
crosstalk as the clipped photons scatter off the aperture edge.

| Cover rule | Value | Confidence |
|---|---|---|
| Air gap, single-zone | As small as possible; gasket or light barrier above ~0.5 mm | ST engineer citing AN5231, vendor-page-verified |
| Air gap, VL53L5CX | Below 0.4 mm; gasket above 0.7 mm | AN5856 second-hand, unverified |
| Transmission, 930-950 nm | Above 85 % | AN5231 second-hand, unverified |
| Cover | About 1 mm thick; smooth and polished | Thickness ST cover-glass article, vendor-page-verified; surface inferred |
| Crosstalk calibration | Once per unit, real cover fitted, after assembly | Required, vendor-page-verified; target distance not published |
| Protective liner | Remove immediately before fitting the cover | DS page 27, datasheet-verified |

Bond the breakout to the inside face so the standoff stays at or below 0.5 mm; counterbore from
inside where the wall exceeds 1 mm, tapered wider than the cone; fit a 0.4 mm rib or black foam
septum between Tx and Rx, the highest-value part of the assembly and free. Aimed at empty space, a
good aperture returns "no target" and a bad one a stable 50-300 mm. Ignore any sub-40 mm return -
minimum ranging distance is 4 cm (DS 3.3, datasheet-verified).

## Radar through plastic

Radar suits a costume robot because it hides behind the shell where ToF cannot. Insertion loss in dB
through PLA, PETG or ABS at 24 or 60 GHz is **not published** by any source here; what is published
is permittivity, the thickness rule, and one measurement of what a wrong thickness does. Hi-Link and
Waveshare publish the same 24.125 GHz table (datasheet-verified -
[LD2410 manual](https://seengreat.com/upload/file/86/HLK+LD2410+Life+Presence+Sensor+Module+Manual+V1.03(220629).pdf)
Table 3, [Waveshare radome guide](https://files.waveshare.com/wiki/HMMD-mmWave-Sensor/HMMD-mmWave-Sensor%20Radome%20Design%20Guide%20.pdf)):

| Medium | e_r | Half-wave at 24.125 GHz | 1/8 wave |
|---|---|---|---|
| Air | 1.00 | 6.20 mm | 1.55 mm |
| ABS 1 | 1.50 | 5.06 mm | 1.27 mm |
| ABS 2 | 2.50 | 3.92 mm | 0.98 mm |
| PC | 3.00 | 3.58 mm | 0.89 mm |
| PMMA acrylic 1 | 2.00 | 4.38 mm | 1.10 mm |
| PMMA acrylic 2 | 5.00 | 2.77 mm | 0.69 mm |

PLA is absent from it. Measured work gives e_r about 2.75 from microwave through 60 GHz, so PLA
half-wave is 3.75 mm at 24.125 GHz and 1.51 mm at 60 GHz, eighth-wave 0.94 mm and 0.38 mm (computed).
The 60 GHz eighth-wave is thinner than one printed perimeter, so at 60 GHz half-wave is the only
usable option. Printed e_r falls with infill, so a 40 % infill wall is not 2.75. **PETG e_r is not
published**: bound it between the ABS 2 row (2.50, 3.92 mm) and the PC row (3.00, 3.58 mm) and measure, or print
the window in ABS or PLA.

```
Wall thickness   D = (m/2) * c0 / (f * sqrt(e_r))    m = 1, 2, 3 ...   +/- 20 %
Antenna standoff H = (m/2) * c0 / f                  (half-wave in AIR, +/- 1.2 mm)
```

Datasheet-verified from Hi-Link 7.2 and Waveshare, identical to
[TI SWRA705](https://www.ti.com/lit/an/swra705/swra705.pdf) Equations 3-5. At half-wave the
inner-face reflection cancels. If half-wave is impossible go to 1/8 wave or thinner; between the two
is the worst of both. Air half-wave at 24.125 GHz is 6.20 mm, so preferred standoff is 12.4 or
18.6 mm.

TI measured the cost of getting it wrong: a 2 mm ABS box over an IWR6843ISK at 62 GHz turned a smooth
105-120 dB pattern into nulls swinging roughly 80-125 dB (SWRA705 6.1). Correct ABS half-wave at
62 GHz is 1.53 mm (computed), so 2 mm is 1.31x optimum - a 0.47 mm error wrecked it. Sources disagree
on ABS: Hi-Link and Waveshare tabulate two point values, 1.50 and 2.50, while TI Table 3-1 gives
2.0-3.5 with tan d 0.0050-0.019.
Prefer TI's range, a material spread rather than one vendor's point value; it moves the 24 GHz
half-wave from 4.39 to 3.32 mm, a 24 % swing wider than the tolerance, so get e_r from the filament
supplier or measure it. Curvature helps too: a flat radome is tuned only at boresight, while with the
antenna at the centre of a spherical radome the path is equal at every angle (SWRA705 4.2), radius
n*lambda0/2 and wall n*lambda_m/2.

| Material | Status |
|---|---|
| Metal in the wall | Opaque (LD2410 5.5) |
| Metallic paint or any conductive coating | Opaque (SWRA705 3, 8; Waveshare) |
| CF-filled, conductive, anti-static or metal-powder filament | Opaque to attenuating (inferred from the no-conductor rule) |
| Frosted or textured surface | Degrading, raises reflection and loss (Waveshare) |
| Sparse infill, voids, multi-layer wall | Degrading, must be solid with no bubbles (SWRA705 3) |

The last row bites printing hardest: a 3-perimeter 20 %-infill wall is a solid-sparse-solid sandwich
of unknown effective e_r. Reserve a 100 %-infill puck across the aperture plus margin and print it
smooth-side-out. One deliberate use of metal: Hi-Link recommends a metal backplane behind each radar
to kill the back lobe, which on a ring also cuts radar-to-radar coupling.

No vendor here publishes a minimum separation between two 24 GHz modules: the DFRobot SEN0395 and
SEN0610 wikis and the Hi-Link LD2410 manual are silent on it, and Seeed says only that the MR60BHA2
"must avoid interference from nearby radars" without a distance (vendor-page-verified). All these
modules sit in the same 24.00-24.25 GHz band with a 250 MHz sweep (LD2410 manual Table 2,
datasheet-verified), so two overlapping beams dechirp each other and no frequency plan separates
them. The LD2410 beam is +/- 60 deg (datasheet-verified), so three radars at 120 deg spacing cover
360 deg with the -3 dB edges just meeting; three is the count that minimises overlap. Time-multiplexing
radars is not practical - they take seconds to settle their background estimate after a power cycle
and expose no gate input, so unlike ToF they cannot be round-robined.

## UART fan-in for multiple radars

These modules stream unsolicited frames rather than answering polls. The LD2410 has one UART and one
GPIO at 3.3 V (datasheet-verified); SEN0395 runs 115200 baud; C4001/SEN0610 runs 9600 baud and also
offers I2C at 0x2A or 0x2B, covering exactly two radars (vendor-page-verified).

| Ring size | Fan-in | Parts |
|---|---|---|
| 2 radars | Two hardware UARTs | ESP32 or RP2040 |
| 3-4 radars | 2 hardware + 2 PIO UARTs | One RP2040 |
| 5-8 radars | **RP2040 concentrator, 8 PIO UART RX** | One Pico-class board |
| 8+, distributed over metres | Satellite MCU + RS-485/Modbus | MAX3485, SN65HVD75 class |

The RP2040's two PIO blocks hold four state machines each, so one chip receives eight streams at
115200-256000 baud with DMA and no per-bit CPU cost. Put it in the base as a concentrator that also
owns the ToF firing schedule and publishes one sector vector upstream (inferred). `SoftwareSerial` is
reliable only to about 38400 baud and cannot receive on two instances at once. An SC16IS752 (2 UARTs,
64-byte FIFOs, 5 Mbit/s, datasheet-verified) works on SPI but not I2C: four bridges polled at 50 Hz
cost roughly 15 kB/s against about 30 kB/s usable, on the same bus as the ToF ring (computed). An
analog mux (74HC4051) suits command/response sensors only, and RS-485 needs a per-node MCU because
no module here has a node address.

## Power budget

From DS Table 16 (16 mA typ, 40 mA peak with VCSEL, 20 uA between measurements) and the LD2410 manual
Figure 11 oscilloscope capture (80.62 mA average, 152.17 mA maximum measured), plus about 3 mA per
breakout for LED and LDO (inferred). All rows computed.

| 6-sensor ring | Average | Peak | At 5 V |
|---|---|---|---|
| 6 ToF concurrent | 114 mA | 240 mA | 0.57 W |
| 6 ToF, 2 groups of 3 | 66 mA | 120 mA | 0.33 W |
| 6 ToF sequential | 34 mA | 40 mA | 0.17 W |
| 6 x LD2410 24 GHz | 484 mA | 913 mA | 2.42 W |
| 4 ToF + 2 LD2410 | 243 mA | 464 mA | 1.22 W |

| 12-sensor ring | Average | Peak | At 5 V |
|---|---|---|---|
| 12 ToF concurrent | 228 mA | 480 mA | 1.14 W |
| 12 ToF, 2 groups of 6 | 132 mA | 240 mA | 0.66 W |
| 12 x LD2410 24 GHz | 967 mA | 1.83 A | 4.84 W avg, 9.13 W peak |
| **8 ToF + 4 LD2410** | 486 mA | 929 mA | 2.43 W avg, 4.65 W peak |

ToF power is irrelevant - time-multiplex for crosstalk, never for power. Radar power is not: twelve
24 GHz modules need their own buck converter, which argues for three or four radars in a hybrid ring.
The DFRobot SEN0395 is worse again where a figure is published, 90 mA average each
(vendor-page-verified), so six of them draw 540 mA and 2.70 W. Cut the LED jumper on every breakout,
36 mA at twelve nodes.

Radar is a pulsed load, and the LD2410 manual demands a supply capable of over 200 mA per module. Do
not daisy-chain power through Qwiic cable: 28 AWG is 0.2326 ohm/m, so 0.93 A over a 1 m round trip
drops 216 mV and 1.83 A drops 426 mV, against 49 mV and 97 mV on 22 AWG (computed). Run a 22 AWG
power star from a 5 V/3 A buck, 1000 uF at the distribution board, 100 uF plus 100 nF at each radar,
and Qwiic red and black for the last 100 mm only. Treat 200 mA as the working limit per JST SH
contact (no vendor publishes a rating), and keep one common ground - a radar returning chirp current
through an I2C cable injects it into SDA.

## Latency budget

The robot tips before it skids - `a_tip = g*(t/2)/h` is 2.86 m/s2 at a 600 mm centre of gravity on a
350 mm track - so design to 1.5 m/s2, giving 30 mm braking at 0.3 m/s and 83 mm at 0.5 m/s
(computed). The chain is `T_total = T_revisit + T_integration + T_processing + T_actuation`:
integration 33 ms (the datasheet-referenced 10 Hz / 33 ms point, DS Table 16), processing 10 ms,
actuation 50 ms (inferred - measure yours). Refresh follows from motion alone, since the robot must
move no more than a quarter of its radius between looks at one bearing (inferred): 44 mm at 0.5 m/s
gives **full perimeter refresh at or below 88 ms - 10 Hz minimum, 20 Hz target**, relaxing to 146 ms
at 0.3 m/s. Reaction distance is `d_react = v_close*T_total + v^2/(2a) + d_margin`, with 83 mm
braking and 100 mm margin:

| Ring configuration | T_revisit | T_total | Human 1.9 m/s | Cat 4.5 m/s |
|---|---|---|---|---|
| 8 ToF simultaneous (zero overlap only) | 33 ms | 126 ms | 0.423 m | 0.750 m |
| 8 ToF, 2 groups of 4 | 66 ms | 159 ms | 0.485 m | 0.899 m |
| 8 ToF, 4 groups of 2 | 132 ms | 225 ms | 0.611 m | 1.196 m |
| 8 ToF sequential | 264 ms | 357 ms | 0.861 m | 1.790 m |
| 12 ToF sequential | 396 ms | 489 ms | 1.112 m | 2.384 m |

All computed. Read the cat column against the ambient table above: sequential firing of eight sensors
demands 1.79 m on a small dark animal, and the VL53L1X reaches 1.70 m on 17 % grey **in the dark**,
0.68 m at 200 kcps/SPAD. Strictly sequential firing is not viable for pet detection with this sensor
class. Two groups of four is the first configuration with real margin, and one of only two that meet
the 88 ms rule - the other is all eight fired at once, which is legal only with zero cone overlap.
Four ToF sequential (132 ms) passes at 0.3 m/s and fails at 0.5 m/s. Radar
frame rate is **not published** and community figures cluster near 10 Hz, so treat radar as a
presence layer at 100 ms-class latency and let ToF own collision avoidance (inferred).

The bus is not the bottleneck: a result read is about 17 bytes, 0.4 ms at 400 kHz, plus 45 us per mux
select, so twelve sensors per sweep is 5.3 ms - 16 % of one integration window, or 21 ms at 100 kHz,
still inside one window (computed). **Run the ring at 100 kHz**: 3.3x the capacitance headroom,
possibly no LTC4311, and nothing the latency budget can measure.
