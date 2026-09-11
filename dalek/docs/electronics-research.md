# Dalek electronics design and source record

Research date: 2026-09-11. This is a build design, not a claim that a robot was physically assembled or tested. Listed prices are USD before shipping and tax. Stock is a page observation, not an order reservation. The bill of materials separates checked prices from allowances.

## Selected build

The controller is the original 1.14-inch TTGO T-Display ESP32. It is mounted on the rear with its screen visible. Four Adafruit 3777 motors each drive one Adafruit 3766 wheel. Each motor has a separate current-limited H-bridge. Two positional servos move each arm in yaw and pitch. Their phased movement draws a circle with the arm tip. A continuous rotation servo drives the head through the mechanical bearing and belt. No wires enter the rotating head.

Power comes from one removable Bioenno BLF-1206A 12 V 6 Ah LiFePO4 pack. Three independent converters produce 5 V for drive motors, 5 V for servos, and 5 V for controller/audio. The physical ACTUATORS OFF switch removes input power from both motion converters. Logic and the display remain on. All circuit grounds join at a power distribution star.

The authoritative connection set is `electronics/wiring.csv` together with the circuit SVGs. Use the component references from those files. Pin numbers on the TTGO are GPIO numbers. Pin numbers on U8/U9 are DIP package pin numbers.

## Required motors and wheels

Adafruit 3777 accepts 3–6 V. The vendor measured 160 mA unloaded and 1.5 A stalled at 6 V on a sample. The listing gives 0.8 kg·cm stall torque at 6 V, a 48:1 gearbox, 70×22×18 mm body and 30.6 g mass. There is no encoder. The selected 5 V rail stays within the motor voltage range. Four motors cost $11.80 at the checked $2.95 each. These numbers do not establish continuous load torque. [Adafruit 3777](https://www.adafruit.com/product/3777)

The required orange/clear 3766 is a press-fit TT wheel, 63 mm diameter by 29 mm wide, 38 g. The checked price is $1.50 each. Adafruit marked it out of stock. This design retains the user's exact wheel. Obtain the wheels before accepting the final motor-to-shell fit. Do not buy a different wheel from a similar photograph. [Adafruit 3766](https://www.adafruit.com/product/3766)

A nominally stronger DRV8871 was rejected because its minimum motor supply is 6.5 V. That is above the required motor's 6 V maximum. Feeding the motors an overvoltage and merely lowering PWM duty is not used here. [Adafruit DRV8871](https://www.adafruit.com/product/3190)

The selected two DRV8833 boards each contain two bridges. They support the 5 V motor supply. Each stock 0.2 ohm sense resistor sets approximately 1 A limit through 0.2 V/R. Keep the factory resistors and leave their bypass jumpers open. Tie AIN1 to BIN1 and AIN2 to BIN2 on each side. Do not tie the bridge outputs together. This gives the controller one forward/reverse input pair per side while each motor has its own current limit. SLP is active high, with an internal weak pull-down. Add the specified external 10k pull-down. [DRV8833 product](https://www.adafruit.com/product/3297), [DRV8833 pinouts](https://learn.adafruit.com/adafruit-drv8833-dc-stepper-motor-driver-breakout-board/pinouts)

The four-wheel skid-steer layout has no precise speed or distance measurement. The body must be light. Three kilograms is a design ceiling to test, not a proven payload. Use hard flat indoor flooring. Wide silicone tires can resist turning. A short wheelbase reduces this resistance. Do not use the robot on stairs, ramps, carpet, or outdoors.

## Servos and movement

The four arm servos are MG92B units, Adafruit 2307. The listing specifies 5 V signals as well as 5 V power. Direct 3.3 V PWM is therefore not the chosen wiring. The listed torque is 3.1 kg·cm at 4.8 V and 3.5 kg·cm at 6 V; weight 14 g; envelope 36×12×31 mm; 20-tooth horn spline. The listing also says this servo has no mechanical end stops. Use its supplied horn rather than printing a nominal spline. Begin with a small software travel window and check every linkage. [MG92B](https://www.adafruit.com/product/2307)

The head uses the FS5103R, Adafruit 154, which controls speed and direction rather than shaft angle. The source lists 4.8–6 V power, 3 kg·cm stall torque at 4.8 V, 40 g weight and 25-tooth horn spline. It is currently out of stock. Its source contradicts itself about the calibration screw and explicitly notes that newer units lack the adjustment hole. Set neutral in firmware; do not instruct the builder to drill or open the servo. The bearing carries the head mass. [FS5103R](https://www.adafruit.com/product/154)

U10 is Adafruit 815 PCA9685. Use 3.3 V VCC and its default I2C address 0x40. The board's I2C pull-ups then stay at the ESP32 logic voltage. Leave the V+ rail disconnected because servo power is distributed separately. The board's output-enable pin is active low and normally pulled down. Remove that pull-down resistor, then fit an external 10k resistor from OE to 3.3 V. Identify it by continuity to OE and GND against the actual PCB revision; do not remove a resistor by guessed reference number. Measure the result before connecting servos. [PCA9685 pinouts](https://learn.adafruit.com/16-channel-pwm-servo-driver/pinouts)

U8/U9 are 74AHCT125 buffers. Power them from 5V_SERVO. Their inputs recognize the 3.3 V PWM; outputs provide 5 V pulses. Use the AHCT version, not HC. Verify the actual purchased chip marking and its data sheet. The TI SN74AHCT125 specifies input leakage at VCC=0 through 5.5 V and input thresholds compatible with 3.3 V. This matters because the controller remains on when servo power is disconnected. The buffer input must not power its dead supply through a positive clamp diode. Every used buffer OE joins SERVO_DISABLE. Every unused input has an explicit tie. Two 100 nF capacitors sit at the IC supply pins. [Adafruit 1787](https://www.adafruit.com/product/1787), [TI SN74AHCT125 data sheet](https://www.ti.com/lit/ds/symlink/sn74ahct125.pdf)

The channel order is 0 left yaw, 1 left pitch, 2 right yaw, 3 right pitch, 4 head speed. Use 50 Hz. With horns removed, start at 1500 µs. Fit arm horns at the mechanical center. Start circular motion with a 2-degree angular radius at 0.10 Hz. Increase only after checking clearance. The normal default is 8 degrees at 0.40 Hz. Phase the pitch 90 degrees from yaw. This is a conical arm-tip path, not continuous rotation of the entire arm shaft. Head neutral is calibrated separately. Continuous rotation cannot command an absolute head angle without feedback, which this design does not include.

## Power and battery

The selected BLF-1206A provides 12 V nominal, 6 Ah, 72 Wh by nominal multiplication, 12 A continuous discharge, and internal protection and cell balancing. The source gives 0.7 kg mass. Its metric and inch dimensions differ: 108×64×69 mm versus 4.4×2.6×2.8 in, which converts to 111.8×66.0×71.1 mm. The design uses the larger converted dimensions and a minimum 116×71×76 mm padded cavity, plus cable clearance. It uses the factory PP30 discharge connector. Never open or modify the pack. [Bioenno BLF-1206A](https://www.bioennopower.com/products/12v-6ah-lifepo4-battery-pvc)

Use only the matched BPC-1502DC charger for this build: 14.6 V, 2 A with the specified DC charge plug. Switch off, unplug the PP30 discharge connection, and remove the pack from the printed shell before charging. Charge on a nonflammable surface with the pack and charger visible. Do not charge through TTGO's lithium battery connector. This robot has no onboard charging circuit. [Bioenno matched charger](https://www.bioennopower.com/products/lithium-12v-2a-amp-lifepo4-battery-charger)

U2/U3 are Pololu 4091 D36V50F5 regulators. Their fixed 5 V outputs, input range and current capability give substantially more supply margin than the rejected low-voltage pack arrangement. The manufacturer's output-current rating depends on input voltage and temperature. The 5.5 A name is not an unconditional guarantee inside a printed enclosure. Leave the boards ventilated and solder thick power conductors directly to their duplicated power pads. Do not send more than 3 A through one ordinary header pin. The board is 25.4×25.4×9.5 mm and has M2 mounting holes. Leave EN, PG and VRP unconnected. [Pololu 4091](https://www.pololu.com/product/4091)

U4 is the Adafruit 4739 MPM3610 fixed 5 V regulator. It is rated for 1.2 A and up to 21 V input. The checked price is $6.95. This lower-power converter is sufficient only with the specified audio limit. CAD from the manufacturer's board repository gives 10.16×17.145 mm outline and a 2.5 mm mount hole at (5.08, 14.605) mm. The 5 V variant uses the same outline; verify the actual board before fastening. [MPM3610 product](https://www.adafruit.com/product/4739), [Adafruit board CAD](https://github.com/adafruit/Adafruit-MPM3610-PCB)

Use NKK S1A switches for MAIN and ACTUATORS OFF. Their source rating is 20 A at 30 VDC; the panel opening is 12.5 mm. ON joins terminals 1 and 3. The small Adafruit covered toggle was rejected because Adafruit recommends only 1–2 A despite the 20 A marking. Each battery/branch fuse has a stated value. The main 7.5 A fuse protects the harness close to the battery. Branch fuses are 3 A at each motion converter input and 1 A at the logic converter input. These are wire-fault protection, not a precision current limiter or motor thermal model. [NKK S1A](https://www.nkkswitches.com/wp-content/themes/impress-blank/search/inc/part.php?part_no=S1A), [Adafruit covered toggle](https://www.adafruit.com/product/3308)

Current allowances at 5 V are 4 A drive, 5 A servos and 0.9 A logic/audio. Total peak output allowance is 49.5 W. At 11.2 V battery and an assumed 85% conversion efficiency, estimated input current is 5.20 A. This leaves margin below the 12 A battery limit. The 5 A servo allowance is a design allowance because the vendor pages do not provide an authoritative stall-current value. Measure the delivered units. Sustained stall of all servos is not an operating condition. If a rail falls below 4.8 V, a fuse opens, or a driver repeatedly shuts down, stop and remove the mechanical obstruction; do not increase fuse or sense-current limits.

The 100 ohm 1 W discharge resistors each consume 0.25 W. They reduce residual actuator voltage after S2 opens. Capacitors still contain energy for a fraction of a second. The disconnect causes coasting; it is not an instantaneous mechanical brake or a certified emergency-stop system. Prove that both actuator rails fall below 0.5 V within 1 second during the commissioning test, including the no-load case.

## Controller and Wi-Fi connections

The original board uses ST7789 display pins 19, 18, 5, 16, 23 and 4. Buttons use 0 and 35. Its onboard single-cell battery measurement is GPIO34 with GPIO14 power control; that circuit must not measure the 12 V pack. The chosen separate ADC is GPIO39(SVN). GPIO36(SVP) reads actuator power state. Both are input-only. The pin map source confirms those pins are exposed. [LILYGO pin map and source](https://github.com/Xinyuan-LilyGO/TTGO-T-Display), [manufacturer pin-map image](https://raw.githubusercontent.com/Xinyuan-LilyGO/TTGO-T-Display/master/image/pinmap.jpg)

External assignments are I2C 21/22, servo-disable 27, motor-enable 12, left drive 25/26, right drive 32/33, audio 17/13/15, battery 39 and actuator sense 36. GPIO12 has a 10k pull-down to keep the normal boot strap state. GPIO15 connects only to the amplifier input without added bias. No GPIO receives 5 V. Use 2.4 GHz Wi-Fi. The firmware provides its own access point and a configuration page to join an existing network. Keep the rear antenna area clear of the battery, motor cans, foil paint and metal fasteners; use an uncoated plastic region around it.

The pack divider is 100k top/22k bottom, 1% resistors, with 100 nF at GPIO39. At 14.6 V it gives 2.633 V. Multiplier is 122/22. A 100k/33k divider is NOT used; it would exceed the intended ADC range on this pack. A second 10k/15k divider maps 5V_MOTOR to 3.0 V at GPIO36, with 100 nF filtering. Firmware stops on a sustained 11.2 V reading and permits re-arm only above 12.0 V. LiFePO4 voltage does not provide a reliable linear charge percentage. Display voltage or a conservative low-battery state, not a claimed precise fuel gauge.

## Sound

The ESP32 decodes the supplied MP3 files and sends I2S to Adafruit 3006 MAX98357A. It needs BCLK on GPIO17, LRC on GPIO13 and DIN on GPIO15. It does not require MCLK. OUT+ and OUT- go only to the speaker. Neither speaker lead connects to ground. Use a 100k resistor from GAIN to 5V_LOGIC for 3 dB gain, and leave SD at its factory mono-mix configuration. [MAX98357 pinouts](https://learn.adafruit.com/adafruit-max98357-i2s-class-d-mono-amp/pinouts)

The speaker is Adafruit 1313, 8 ohm 1 W, 77.8 × 77.8 × 25.49 mm. Its four mounting tabs are 60 mm apart. It costs $1.95 and was in stock. The supplied firmware uses fixed digital gain 0.28. This is a design setting, not an acoustic measurement. Verify that continuous test audio is below 2.83 Vrms across the 8 ohm load, using a suitable differential measurement and audio-band filtering. Never attach a grounded oscilloscope clip to an amplifier output. Normal spoken clips have lower average power than a continuous test tone. [Adafruit 1313](https://www.adafruit.com/product/1313)

## Harness assembly

1. Disconnect the battery. Fit the switches, fuse holders and ground-star block. Label every rail and both switch OFF positions. Protect all exposed lugs with heat shrink.
2. Fit U2/U3 on insulated standoffs with air space around them. Fit U4 and the two prototype boards. Fit U1 in the rear holder with the display facing outward. Keep the USB connector accessible.
3. Assemble the buffer board without ICs installed. Use DIP14 sockets. Check pin 14 to 5V_SERVO and pin 7 to GND. Check every channel against sheet 03. Add one 100 nF capacitor per socket. Fit the input and output pull-downs and 220 ohm output resistors.
4. Modify PCA OE as described above. With the board unpowered and isolated, check that OE is not still tied to ground through its original resistor. Add the external 10k to 3.3 V. Record the actual board revision and removed resistor location for later service.
5. Wire the power branches in 18 AWG. Wire one 22 AWG positive/ground pair from the servo distribution block to each servo plug. Do not route aggregate servo current through the PCA header rail or prototype-board strips.
6. Wire each motor to its own bridge. Add 100 nF directly at each motor's solder tabs. Retain only short lengths of the supplied 28 AWG leads. Twist the two motor conductors. Add strain relief near the plastic gearbox, not on the motor tabs.
7. Wire signals from the CSV. Keep I2C and I2S away from motor wiring. Add service loops at the removable rear hatch. Keep wires out of belts, wheels and arm linkages. The head must have no wiring.
8. Fit and label the removable J_USB_ISO run-power connection. To program: switch MAIN off, unplug the battery, open the run-power link, then attach USB. Unplug USB before reconnecting the link and battery. No external battery is connected to the TTGO JST socket.

## Bench acceptance before the shell is closed

Use a current-limited bench supply for first power where available. Otherwise leave the motors and servos unplugged until the polarity and rail checks pass. Keep the robot raised so all wheels are clear. Keep hands clear of the arm and belt paths.

1. With no power, check for shorts between each positive rail and GND. Check for no direct connection between the three 5 V outputs. Check capacitor polarity and fuse values. Check each power connection by meter, not wire color alone.
2. MAIN on and ACTUATORS off: measure logic 5 V; verify rear screen boots. Verify both actuator rails discharge below 0.5 V within 1 second. Check no servo power appears through a signal wire.
3. ACTUATORS on but disarmed: measure all three rails 4.8–5.2 V. Confirm the battery reading agrees with a meter within 0.2 V after calibration. Verify GPIO36 is about 3.0 V.
4. Hold the TTGO reset button. Verify motor SLP below 0.3 V and PCA OE above 3.0 V. Motors must not run. Release reset; robot stays disarmed. Power-cycle several times with ACTUATORS on and watch for unintended movement.
5. Fit one motor at a time. At low duty, verify direction and the commanded stop. Do not deliberately stall a motor. Then connect all four and repeat with wheels raised.
6. Fit servos with horns removed. Verify neutral and channel mapping. Fit horns at the mechanical center, then make slow small circles. Check every linkage and head belt for binding. Set the head neutral until it stops without creep.
7. While moving at low speed, close the browser, turn off Wi-Fi and disconnect the control device in separate tests. The firmware timeout must stop all motion. It sends a calibrated head-neutral pulse for 100 ms before disabling servo outputs. Reconnection must require manual arming. Turn ACTUATORS off and verify physical power removal while the display remains on.
8. Simulate low battery with an adjustable supply rather than over-discharging the pack. Confirm sustained 11.2 V causes stop, 12.0 V is required before re-arm, and an invalid ADC prevents arming.
9. Weigh the finished robot. First drive on a hard flat floor at low duty. Test straight motion and broad forward turns. The supplied control interface intentionally uses arcs rather than in-place turns. Log loaded pack voltage, each 5 V rail minimum and motor-driver temperature. No rail may drop below 4.8 V; there must be no reset or repeated thermal shutdown. Stop if the robot binds while turning. A smaller/lighter shell or lower-friction floor is required if the specified motors cannot turn it reliably.
10. Run 15 minutes of representative driving and animation with pauses. Confirm regulator and driver package cases remain below 60°C with a thermometer. Motors, servos and printed mounts must stay below the assembly guide's more conservative 50°C limit. Wire joints must remain cool and wheels must not rub. These are project acceptance limits, not claimed vendor maximums. Test audio with drive and arms active. Check there is no reboot or audible power noise.

## Calculations and limits

`electronics/calculations.json` is generated from the documented assumptions by `python electronics/generate.py`. At the 1 A current limit, a simple linear interpolation from the vendor's 6 V current/torque data estimates 0.0492 N·m per motor, or 6.25 N combined wheel force at 31.5 mm radius. Gearbox losses, current ripple and unit variation reduce confidence in this estimate. It is not a continuous-torque rating. The unloaded 6 V, 250 RPM sample would imply 0.825 m/s wheel speed; the actual 5 V loaded robot will differ. PWM limits are not a speed governor without encoders.

With 75% of nominal 72 Wh treated as useful energy, runtime estimates are 3.6 hours at 15 W average and 2.16 hours at 25 W average. These are planning values. The builder must measure loaded current and an actual discharge cycle to state runtime. Do not describe the result as verified until the physical checks above have passed.

Open procurement items are the required 3766 wheels and selected 154 head servo, both marked out of stock. The two Pololu regulators are rationed with backorders allowed. The pin assignment, circuit files and firmware can be checked now. Hardware fit, turning ability, noise, servo current and runtime still require the physical build.
