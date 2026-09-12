# Shopping lists

Three buildable lists follow: `collision-ring` at about **$455**, `collision-ring + animate-layer`
at about **$909**, and `full-classification-stack` at about **$1,440**. Every **[V]** price below was
read from a vendor page by a source lane on **2026-09-12** and is in USD; the **[U]** prices were
read from no vendor page at all. Prices **exclude tax and shipping**. **Nothing
in these lists has been purchased, and no sensor named here has been physically tested** - every
performance figure supporting these choices is datasheet-verified or vendor-stated, not measured.

Two markers are used in every table. **[V]** means the unit price was read on the vendor's own page
in a source lane. **[U]** means no source lane priced the part: the figure is budgetary and must be
confirmed before ordering. All three tier totals contain some [U] lines, so all three totals are
approximate at the stated precision.

## Tier 1 - `collision-ring`, about $455

This tier answers "will I hit it?" and nothing else. It has no human channel and no pet channel.

| Qty | Part | Vendor | SKU | Unit | Ext | What the line is for |
|---|---|---|---|---|---|---|
| 12 | VL53L8CX 8x8 multizone dToF carrier | Pololu | #3419 | $24.95 [V] | $299.40 | 360 deg perimeter ring, h = 200 mm, level, 30.0 deg spacing |
| 6 | VL53L4CD 1-1300 mm dToF carrier | Pololu | #3692 | $13.95 [V] | $83.70 | Cliff and stair-edge, h = 150 mm, 23 deg down-cant |
| 2 | PCA9548 8-channel I2C mux | Adafruit | #5626 | $6.95 [V] | $13.90 | Addressing: every VL53 boots at 0x29 |
| 12 | Flexible Qwiic cable, 500 mm | SparkFun | PRT-17257 | $2.75 [V] | $33.00 | Mux to ring |
| 6 | STEMMA QT cable, 100 mm | Adafruit | #4210 | $0.95 [V] | $5.70 | Mux to cliff sensors |
| 1 | RP2040 concentrator, Pico class | not priced | - | ~$4 [U] | ~$4 | Ring timing and I2C concentration |
| 1 set | Closed-cell foam bumper, 20-50 mm, plus 4 microswitches | not priced | - | ~$15 [U] | ~$15 | Catches the 35 mm chair leg the ring can hide |
| **Total** | **18 ToF modules, 0 people sensors** | | | **verified $435.70** | **approx. $455** | **724 mA average / 1.61 A peak at 5 V** |

## Tier 2 - `collision-ring + animate-layer`, about $909

Tier 1 in full, plus the three sensor additions below and their support parts. This is the
recommended build.

| Qty | Part | Vendor | SKU | Unit | Ext | What the line is for |
|---|---|---|---|---|---|---|
| 1 set | Everything in Tier 1 | - | - | - | ~$455 | Collision layer, unchanged |
| 1 | Slamtec RPLIDAR C1 360 deg dTOF scanner | DFRobot | RPLIDAR C1 | $69.00 [V] | $69.00 | Dark targets (6 m at 10 pct reflectivity), 40,000 lux, cat lying at 120 mm, static map |
| 8 | AMG8833 Grid-EYE 8x8 thermal array | Adafruit | #3538 | $44.95 [V] | $359.60 | Animate vs inanimate ring, h = 250 mm, level, 45.0 deg spacing |
| 2 | RCWL-1601 ultrasonic ranger, 3 V/5 V | Adafruit | #4007 | $3.95 [V] | $7.90 | Glass and mirrors, forward arc, warning field only |
| 1 | PCA9548 8-channel I2C mux, third unit | Adafruit | #5626 | $6.95 [V] | $6.95 | Thermal ring branch |
| 8 | STEMMA QT cable, 300 mm | Adafruit | #4210 | $1.25 [V] | $10.00 | Mux to thermal ring |
| **Total** | **19 ToF modules, 8 people sensors** | | | **addition $453.45** | **approx. $909** | **999 mA average / 1.95 A peak at 5 V** |

## Tier 3 - `full-classification-stack`, about $1,440

Labelled human / pet / object to 10 ft in light, and the same classes by thermal in darkness.

| Qty | Part | Vendor | SKU | Unit | Ext | What the line is for |
|---|---|---|---|---|---|---|
| 16 | VL53L8CX carrier | Pololu | #3419 | $24.95 [V] | $399.20 | Tighter ring, h = 200 mm, 22.5 deg spacing |
| 6 | VL53L4CD carrier | Pololu | #3692 | $13.95 [V] | $83.70 | Cliff, h = 150 mm, 23 deg down |
| 1 | VL53L8CH CNH histogram head | bare part, carrier needed | VL53L8CH | ~$35 [U] | ~$35 | Material and shape, h = 900 mm, own I2C bus |
| 6 | MLX90640-ESF-BAA 32x24 thermal, 110 x 75 deg | Adafruit (out of stock) | #4469 | $74.95 [V] | $449.70 | Thermal classification ring, h = 250 mm, 60 deg spacing |
| 1 | Slamtec RPLIDAR C1 | DFRobot | RPLIDAR C1 | $69.00 [V] | $69.00 | Dark targets and ambient light |
| 2 | RCWL-1601 ultrasonic | Adafruit | #4007 | $3.95 [V] | $7.90 | Glass, forward arc |
| 4 | PCA9548 8-channel I2C mux | Adafruit | #5626 | $6.95 [V] | $27.80 | Bus splitting |
| 1 | Raspberry Pi 5 | not stated | - | $80.00 [V] | $80.00 | Camera host and inference |
| 1 | Hailo-8L AI Kit | not stated | - | $70.00 [V] | $70.00 | YOLOv8n at 136.7 FPS, batch 8, on COCO classes |
| 4 | Wide-FoV camera, about 120 deg horizontal | not priced | - | ~$35 [U] | ~$140 | Labelled human / cat / dog, h = 900-1000 mm, 90 deg spacing |
| 1 set | RP2040 concentrator, cabling, bumper | not priced | - | ~$79 [U] | ~$79 | Concentration, harness, contact backstop |
| **Total** | **24 ToF modules, 10 people sensors** | | | **verified $1,187.30** | **approx. $1,440** | **3.8 A average / 5.2 A peak at 5 V** |

## Shared support parts

These lines already appear inside the tier tables above - itemised in Tiers 1 and 2, and folded
into Tier 3's single `~$79 [U]` concentrator-cabling-bumper line. The table is a cross-check, not an
addition. Quantities scale with the sensor count, not with the tier name.

| Support item | SKU | Tier 1 | Tier 2 | Tier 3 | Note |
|---|---|---|---|---|---|
| PCA9548 8-channel I2C mux | Adafruit #5626, $6.95 [V] | 2 | 3 | 4 | Mandatory. Every VL53 part boots at 0x29 and the address change is volatile |
| Qwiic cable, 500 mm | SparkFun PRT-17257, $2.75 [V] | 12 | 12 | in the ~$79 line | Mux to ring. Harness capacitance is not published by anyone; measure it |
| STEMMA QT cable, 100 mm | Adafruit #4210, $0.95 [V] | 6 | 6 | in the ~$79 line | Mux to cliff sensors |
| STEMMA QT cable, 300 mm | Adafruit #4210, $1.25 [V] | - | 8 | in the ~$79 line | Mux to thermal ring. See the SKU caution below |
| RP2040 concentrator | not priced, ~$4 [U] | 1 | 1 | in the ~$79 line | Ring timing, XSHUT GPIO per sensor |
| Level shifters | not priced in any source lane | - | - | - | Neither priced nor specified in any source lane |
| Mounting hardware, apertures, septa | not priced in any source lane | - | - | - | Printed into the shell. 1.50 mm dia. emitter / 1.80 mm dia. receiver at 1.0 mm standoff, with a septum |
| Compliant bumper and microswitches | not priced, ~$15 [U] | 1 set | 1 set | in the ~$79 line | Covers the object small enough to hide in a ring seam |

## Cautions before any order is placed

- **The 300 mm cable SKU is doubtful.** The source lists Adafruit **#4210** against both the 100 mm
  line at $0.95 and the 300 mm line at $1.25. One part number cannot be two lengths. Confirm the
  300 mm part number on the vendor page before ordering; the $1.25 unit price is [V] but the SKU it
  is attached to is not consistent.
- **Adafruit #4469 (MLX90640, 110 deg) was out of stock on 2026-09-12.** Tier 3's thermal ring must
  be sourced from Melexis, Waveshare or a distributor. The $74.95 is the Adafruit list price.
- **The VL53L8CH price is not published in any source lane.** Confirm it, or substitute
  SATEL-VL53L8 at $32.95 and lose the histogram output. SATEL-VL53L8 carries a 13-week lead time;
  VL53L5CX-SATEL carries **51 weeks**.
- **Every thermal aperture must be an open hole or thin LDPE.** Ordinary glass, polycarbonate,
  acrylic and PET are all opaque at 8 to 14 micrometres, so a visually clear cosmetic window
  silently zeroes the sensor. Budget the aperture, not a window, for every AMG8833 and MLX90640.
- **Two of Tier 3's four cameras must be USB.** The Pi 5 has two CSI ports. Confirm the camera
  choice against that before ordering four.
- **No tier fits `dalek`'s present 5 V budget.** The repo records about 0.30 A spare against the
  724 mA of Tier 1. A second 5 V buck, or a separate regulator off the 12 V pack, is a precondition,
  not an accessory. `fable-r2d2` has about 4.1 A spare and is the right host, but its
  centre-of-gravity and tip-back figures are marked *unknown* in its own `docs/mechanical.md` and
  must be re-run before any mass goes high.
