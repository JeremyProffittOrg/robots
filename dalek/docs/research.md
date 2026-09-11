# Design research and engineering decisions

This package describes a small, original Dalek-shaped indoor robot. The design uses the requested Adafruit TT motors and orange wheels, an original TTGO T-Display ESP32, a printed shell, two moving arms, and a head that can turn through repeated full revolutions. It is a fabrication design for a first prototype. The CAD and software can be checked digitally. Their operation under actual load still needs the commissioning tests in `assembly.md`.

## Source method and date

Product facts were checked against manufacturer product pages, dimensional drawings, component datasheets, and official board source files on 11 September 2026. The required motor and wheel pages were checked first. Component research and exact links are also recorded in `electronics-research.md`, `mechanical.md`, and the BOM CSV files. Prices exclude shipping, tax and regional differences. A product being listed does not guarantee stock when an order is placed.

Quoted electrical ratings describe a specific part and operating condition. Design targets, calculated limits, and assumptions below are identified separately. Neither a successful firmware compile nor a closed STL mesh establishes that a physical robot is safe to drive.

## Size and shape

The revised design is nominally 543.8 mm tall, below 914.4 mm, or three feet. Its single-piece base has a 300 x 280 mm rounded rectangular footprint. Six complete body sections stack vertically: base, lower skirt, upper skirt, shoulder, neck and head. Raised hemispheres, neck supports, rear-board retention, dome details and several actuator mounts are integrated into those prints. A common pitch carrier, two decorative arms and a servo pulley complete the ten-STL set. The carrier is printed twice. These parts form an original interpretation of the character rather than a dimensionally exact replica of a television prop.

Each body section fits upright on the H2D. Bambu specifies 325 x 320 x 325 mm for single-nozzle printing and 300 x 320 x 325 mm for dual-nozzle printing. The 350 mm combined width is not available to either nozzle individually. The base plus an 8 mm brim occupies 316 x 296 mm, so the base uses the single-nozzle area. The actual exported dimensions and slice placement are checked for each tested part. Use the supplied print manifest at 100% scale. Scaling changes motor pockets, holes and the stacking registers. [1]

The strong base uses PETG, a 6 mm floor, continuous walls and ribs, and integrated motor pockets. Loads pass through continuous printed material rather than base-quarter bolts or tall motor pillars. The selected structural slice uses six perimeter lines, six top and bottom layers, 40% gyroid infill, and removable support beneath the wheel-well roofs. This geometry and material choice is a design specification, not a measured load rating. The assembly guide specifies a physical proof-load test with the small gearmotors removed from the load path.

The reinforcement has a weight cost. Final H2D slices estimate 916.956 g of installed base plastic and 2,117.055 g for the six body pieces together. About 1,144.88 g of known catalogue component weights brings that subtotal to 3,261.935 g before the arms, remaining electronics, bearing and fastener hardware, wires and finish. Thus the earlier 3 kg planning target is not met. This is a documented target miss, not a measured final mass or proof of a motor payload limit. The original motors remain as requested. Their ability to drive and turn this heavier assembly must be established with the actual programmed commands, current and temperature measurements on the intended floor. Support and brim waste are excluded from these installed-plastic estimates.

PLA is suitable for indoor cosmetic body sections, while the base and loaded actuator structures use PETG. The skirt and shoulder are complete rings, with register features that align each tier and fasteners that retain it. Small functional parts are printed first for fit checks. No separate coupon STL is required. Paint remains clear of the registers, bearing seats and motor pockets.

## The requested drive parts set the operating limit

Adafruit 3777 is a low-cost 1:48 plastic gearbox motor. Its allowed supply is 3-6 V. Adafruit reports 1.5 A stalled at 6 V and 0.8 kg.cm stall torque at that voltage. Adafruit 3766 is a 63 mm diameter, 29 mm wide press-fit wheel for the TT shaft. Four separate motors drive four wheels. The wheel page was out of stock when checked; the design retains that exact requested wheel. [2,3]

Stall torque is a brief limiting value, not a continuous operating rating. At the 6 V specification, 0.8 kg.cm is approximately 0.0785 N.m. With a 31.5 mm wheel radius, four motors give an ideal combined stall force of 4 x 0.0785 / 0.0315 = 9.97 N. At the chosen 5 V supply and with current limiting, the available force is lower. Gear loss, shaft friction, unequal load and warm windings lower it further. This calculation is an upper bound; it is not a payload rating.

For a design example, a 3 kg robot on a smooth floor with an assumed rolling resistance coefficient of 0.03 requires about 0.88 N just to roll. An acceleration of 0.15 m/s² adds 0.45 N. That 1.33 N example is plausible for gentle straight motion but does not include steering scrub. The coefficients and acceleration are engineering assumptions, not measurements of the supplied wheels. Carpet, door thresholds and slopes are outside the initial operating envelope.

With four fixed wheels, steering requires the tires to slide sideways. For an example friction coefficient of 0.6, mass 3 kg and the revised 120 mm nominal wheelbase, a rough upper bound for stationary scrub resistance is 0.6 x 3 x 9.81 x 0.120 / 2 = 1.06 N.m. The ideal differential drive torque at the 6 V stall specification with a 250 mm track is about 1.25 N.m. The small margin disappears at 5 V and reduced current. A stationary pivot therefore cannot be promised on a high-grip floor. Use broad moving arcs first; release the control immediately if a wheel stops. The comparatively short wheelbase reduces this resistance while the wide track supports stability. Final track also depends on wheel insertion depth.

Motor speed is also open loop. The motors have no encoders. A PWM percentage controls electrical drive, not a measured speed in metres per second. Motors may need polarity and trim checks. The firmware ramps drive commands and limits their range. Wheel diameter and unloaded motor speed can estimate an upper speed, but loaded speed and stopping distance must be measured on the completed robot. [2]

## Driver selection

Two Adafruit DRV8833 boards provide four H-bridges, one bridge for each motor. Each pair of motors on a side receives the same logical direction command. The motor outputs are not wired together. The Adafruit breakout has a nominal 1 A current limit per bridge. Retain its current-sense resistors. A current limit reduces damage during a fault but does not make a stalled motor acceptable for continuous operation. [4]

The DRV8833 operating supply range includes 5 V. The TI datasheet distinguishes continuous, peak and package-dependent current values. The actual breakout's default limit and heat dissipation govern this build. It is not valid to choose a driver merely because a catalogue headline says 2 A peak. Reset-state wiring also matters: the shared sleep line must be low at ESP32 reset, not left to firmware that has not yet started. [4,5]

## Battery and power distribution

The selected pack is the Bioenno BLF-1206A, a protected 12 V, 6 Ah LiFePO4 pack with a stated 72 Wh energy rating. The manufacturer lists a 12 A continuous discharge limit, approximately 0.7 kg mass, and the BPC-1502DC 14.6 V, 2 A charger. Its internal protection and large energy reserve are useful for a mobile prop. It supplies converters; it must never connect directly to a 5 V rail, a TT motor, or the T-Display battery socket. [6]

This is the main deliberate exception to an Adafruit-only shopping list. Adafruit's 3.7 V, 6600 mAh pack has a much smaller energy reserve and a stated 3.3 A maximum discharge. Its own page recommends a substantially lower sustained draw. Boosting its output to 5 V while driving four motors and five servos would demand more battery current than the output current. Capacity in mAh alone is not a sufficient selection rule. A protected ready-built pack avoids assembling and balancing loose cells. [7]

Separate regulated 5 V supplies feed the wheel motors, servos, and logic/audio. This prevents a servo pulse or motor start from drawing through the ESP32 board's small power path. All returns meet at the common ground distribution point. The physical actuator switch removes energy from both movement supplies while leaving the controller display available. The main fuse is close to the battery. Wire size, connector ratings, branch fuses and the actual switch DC rating appear in the electrical package.

Runtime is an estimate until measured. With 72 Wh nominal and an assumed 75% usable energy allowance, 54 Wh remain. At an estimated average load of 15 W, that is 3.6 hours; at 25 W, 2.16 hours. These values cover energy only. Temperature, battery condition, low-voltage shutdown, repeated starts and actual servo load change the result. Do not call any of these a guaranteed runtime. Record the first full discharge test with voltage, duration, activity and temperature. [6]

## Arms and head

Each arm has two perpendicular positional servo axes. The controller varies the two angles using sine and cosine signals. For small angles, the arm tip follows a near-circular orbit. At large angles, the geometry becomes a spatial curve, so the firmware uses a modest amplitude. Equal pulse amplitudes do not guarantee equal physical angles until the servo centres and directions have been calibrated. The two assemblies can share a phase offset without needing a cam mechanism.

Four MG92B servos provide the arm axes. Their power and signal requirements must both be met: the Adafruit product page specifically calls for 5 V control signals. A PCA9685 running at 3.3 V does not provide a 5 V HIGH just because its separate servo power terminal has 5 V. Two AHCT buffers translate the five control signals. The rear electronics drawing shows their enable pins, power bypassing, and unused inputs. [8]

The head uses an FS5103R continuous-rotation servo to drive a bearing-supported rotating assembly. The servo controls speed and direction, not an absolute compass angle. Neutral pulse width needs calibration to stop creep. A continuous servo cannot provide a reliable “face forward” command without a separate reference sensor; no such positioning claim is made. The bearing carries the dome load. The servo supplies rotation rather than supporting the full head as a cantilever. [9]

The eye and dome decorations contain no moving electrical wires. Audio comes from a speaker fixed in the body. This permits repeated complete rotations without a slip ring. It also removes rotating contacts and their noise from the audio power path. All belt, bearing, shaft, retention and horn hardware is enumerated in the mechanical bill of materials.

## Controller and network

The design is for the original ESP32 TTGO T-Display with a 1.14-inch ST7789 display and 4 MB flash. LilyGO publishes the TFT pins, button pins, battery-monitor pins and board drawings. The S3 and other T-Display models have different dimensions and pin assignments and cannot use this firmware and rear mount unchanged. The screen faces outward at the back. Leave its antenna area clear of wires, metal tape and the battery. [10]

ESP32 Wi-Fi supports station mode, access-point mode and their combined use. The robot serves its own browser interface. A nearby phone can connect directly without an Internet connection, or the robot can join an existing 2.4 GHz network. Station credentials are entered locally. No cloud broker or paid service is needed. The exact setup, fallback behavior and displayed addresses are described in `firmware.md`. [11]

Motion needs a current command stream and an explicit arm action. A lost connection, stale command sequence, browser release, physical actuator power loss or safety fault must remove drive commands. Software timeout is an additional control, not a substitute for the physical power switch. The network is local and HTTP is unencrypted; do not expose it through router port forwarding. The Wi-Fi and application password must remain private to the operator.

## Voice collection

The package includes 24 newly synthesized MP3s, about 99 seconds total. Their measured file sizes and durations are recorded in `audio/catalog.json`. They use original short transcripts, the installed desktop speech engine, and a reproducible metallic voice effect. They do not contain ripped television clips. The source list is editable and the generation scripts are supplied. All clips are stored in ESP32 flash, so a memory card or network download is unnecessary.

A MAX98357A converts digital audio to speaker power. The selected 8 ohm, 1 W speaker and limited playback gain keep demand within the logic supply budget. The two speaker terminals form a bridge output: neither is a ground terminal. Fix the speaker to the stationary body and route its wires away from the analog voltage-sense leads. Refer to the electrical source notes for amplifier gain and speaker limit calculations.

## What is established, and what must be measured

Digital checks establish that the delivered files exist, mesh volumes are positive, exported parts fit the selected print envelope, audio decodes, and firmware compiles. Inspection checks that connector names and pins agree across code and diagrams. These checks are valuable but cannot detect actual servo backlash, moulding variation, printer shrinkage, real traction, bearing friction, battery noise or a loose screw.

The first build must measure fit, loaded mass, wheel clearance, free head travel, arm current, supply sag, temperature and stopping behavior. The assembly guide makes those checks before closing the shell and before the first floor run. If the requested drive parts cannot move the actual mass on the actual surface, the correct response is to reduce mass or change the operating surface. Do not remove current protection or raise motor voltage above its rating to force a result.

## References

1. Bambu Lab. H2D technical specifications, single/dual nozzle build volumes. https://cdn1.bambulab.com/documentation/h2d/en/H2D_Laser_Full_Combo_20250305.pdf and https://eu.store.bambulab.com/products/h2d . Manufacturer PDF indexed text and regional product specifications checked 2026-09-11; direct fetch intermittently unavailable.
2. Adafruit Industries. DC Gearbox Motor - TT Motor, product 3777. https://www.adafruit.com/product/3777 . Checked 2026-09-11.
3. Adafruit Industries. Orange and Clear TT Motor Wheel, product 3766. https://www.adafruit.com/product/3766 . Checked 2026-09-11.
4. Adafruit Learning System. DRV8833 motor driver overview and pinouts. https://learn.adafruit.com/adafruit-drv8833-dc-stepper-motor-driver-breakout-board/overview and https://learn.adafruit.com/adafruit-drv8833-dc-stepper-motor-driver-breakout-board/pinouts . Guide published 2016, page checked 2026-09-11.
5. Texas Instruments. DRV8833 datasheet, SLVSAR1E, July 2015 revision. https://www.ti.com/lit/ds/symlink/drv8833.pdf . Checked 2026-09-11.
6. Bioenno Power. BLF-1206A pack and compatible charger specifications. https://www.bioennopower.com/products/12v-6ah-lifepo4-battery-pvc . Checked 2026-09-11.
7. Adafruit Industries. Lithium Ion Battery Pack, product 353. https://www.adafruit.com/product/353 . Checked 2026-09-11.
8. Adafruit Industries. TowerPro MG92B servo, product 2307. https://www.adafruit.com/product/2307 . Checked 2026-09-11.
9. Adafruit Industries. FeeTech FS5103R servo, product 154. https://www.adafruit.com/product/154 . Checked 2026-09-11.
10. LilyGO. TTGO-T-Display original board repository, pinout, schematic and CAD. https://github.com/Xinyuan-LilyGO/TTGO-T-Display . Checked 2026-09-11.
11. Espressif Systems. Arduino ESP32 Wi-Fi API. https://docs.espressif.com/projects/arduino-esp32/en/latest/api/wifi.html . Current API concepts checked 2026-09-11; the compiled firmware pins the older compatible platform version in `firmware/platformio.ini`.
