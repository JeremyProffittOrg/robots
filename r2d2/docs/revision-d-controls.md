# Revision D controls and commissioning

Status2026-09-13: host control tests and the ESP32-S3 firmware/filesystem builds pass. No hardware has been wired, flashed or operated. Firmware deliberately starts with potentiometer calibration uncommissioned and refuses arming until actual measurements are entered. A compiled binary is not proof of physical operation.

## Controller and power

Use DFRobot Romeo ESP32-S3 DFR0994, schematic V1.1.0. Its four DRV8876 channels run in PH/EN mode. Remove the VIN/VM link JP6 and fit PMODE. VIN receives the MAIN battery branch; VM receives only the regulated RUN motor branch. The official wiki calls the VIN/VM link JP1; identify it from the delivered schematic and meter continuity before applying power.

Replace Romeo R9 with5.60k1% and R10 with2.00k1%. The intended nominal current trips are approximately1.73A for each ground pair and0.86A for the head. Confirm the delivered board revision and footprints before rework. Neither nFAULT nor IPROPI provides MCU motor-jam feedback in this design. Parallel motors share a channel current limit, not equal current.

Power path: BioennoBLF-1206A → F1 10A → MAIN switch. MAIN feeds Romeo VIN and RUN switch. RUN feeds F2 10A, which supplies both the ICStation11060 motor regulator and Pololu5573 six-volt servo regulator. RUN also feeds F3 2A → Pololu4984 twelve-volt regulator → Adafruit3190 DRV8871 → P16 actuator. Replace the DRV8871 ILIM resistor with71.5k1%; calculated current limit0.82–0.98A. Use the exact returns and gauges in electronics/wiring.csv.

Set the motor rail to5.70V before connecting Romeo VM; accept5.50–6.00V at VM during commissioning. The two goBILDA2000-0025-0002 servos use the separate6V Pololu5573. Do not connect their positive supply to Romeo5V_Servo. Both may draw approximately2.5A each at stall according to their supplier; verify actual aggregate input current, rail sag and temperature with this wiring and battery. Regulator headline ratings and fuse values do not replace the loaded test.

MAIN off isolates loads for charging through the battery's charger lead. Use the matching Bioenno charger and do not operate while charging. The final access route and lead fit must be verified on the assembled body.

## Connections and input truth

Motor EN/PH pairs: left12/13, right14/21, centre9/10, head47/11. I2S BCLK/LRC/DIN are15/16/17. Steering and lock pulses are40/41. Post extend/retract are38/42 through separate74AHCT125 channels. Hardware limit-open inputs are7/8. Engaged NO/NC are18/5; withdrawn NO/NC are43/44; floor NO is48. Post ADC is4, battery ADC6, RUN sense39.

Use OmronSS-01 direct-plunger switches for both lock endpoints, both travel limits and the floor probe. Each lock switch has COM grounded and separate3.3k pull-ups on NO/NC. GPIO43 is ROM UART TX during reset: put the1k series resistor between the MCU and the switch-side pull-up. Do not connect it directly to the grounded switch. Camera, GDI and microSD must remain disconnected. Physical header locations are documented in printed-frame-research.md and must be checked against the delivered board.

The two travel switches use NC contacts. Closed means permitted travel. Opening one contact, including a broken cable, raises its74AHCT125 OE and disables that direction in hardware. Adjust cutoffs to0.8mm retracted and99.2mm extended. Software endpoints are2 and98mm.

P16 yellow reference+ receives3.3V through2.2k; orange reference− returns through1k to ground. Purple wiper goes to ADC4 with470k pull-down. The bottom resistor gives valid retraction a nonzero voltage. An open wiper or reference+ reads near zero; open reference− tends high. Verify each fault physically. Battery sensing is100k/22k; RUN sensing10k/10k.

The floor probe is an independent NO input. It must indicate support before withdrawing the shoulder lock and throughout tilt. Actuator position alone does not establish contact with the floor.

## State sequence

The guide is35degrees. Upright floor contact is45.038373mm, stationary two-foot endpoint2mm and deployed endpoint98mm. The GN817 pin locks both upright and deployed shoulder positions at45mm radius. The deployed angle is12.832480degrees.

Retracting begins only with wheels/head stopped and steering centred. UNLOCKING stops the post and waits for the independent withdrawn signal. TILT keeps the pin withdrawn while retracting toward upright contact. LOCKING stops, returns the servo, waits400ms, then searches slowly within the defined receiver window until the engaged signal is stable. LIFT retracts to2mm only while the shoulder remains engaged.

Deploying reverses that order: LOWER with the upright shoulder locked; confirm floor probe; UNLOCKING until withdrawn; TILT toward deployment; LOCKING to the deployed receiver. Neither loss of the engaged signal nor post position permits tilt by itself.

Wheel drive is disabled throughout transitions, in HELD/FAULT and in TWO_FOOT. Head motion is allowed only in a recognised stable stance. Command expiry, release, opposite stance command or conflicting drive input stops a transition. A restart requires a fresh deliberate command after interlocks and cooldown permit it. No automatic resume or re-arm is implemented.

Ground drive starts with a35% hardware ceiling and a ramp of1percentage point per20ms. The head ceiling is25%. PH/EN commands scale percent to8-bit PWM. Reversal preserves previous direction across STOP and enforces100ms off time; the output waits for PWM to go low before changing PH. EN=0 brakes on these onboard drivers.

Actuator movement requires0.5mm progress within750ms; wrong-way feedback, timeout, limits, power and sensor disagreements latch faults. Runtime cooldown is four milliseconds per millisecond of actuator operation, consistent with20% duty. That runtime history is not persisted across power loss. After a reboot following movement, leave RUN off for at least10minutes before another stance change; firmware does not measure actuator temperature. Physical power-loss holding and cooldown qualification remain required.

## Calibration and first electrical run

1. Support the body and lift all wheels. Disconnect actuator drive and both servo horns. Leave RUN off. Confirm VIN/VM isolation, fuse values, ground continuity and every power polarity with a meter.
2. Test regulators with dummy loads before connecting electronics. Record motor, servo and actuator rails and pack current. Inspect all solder joints and reworked resistors.
3. Verify both lock contact pairs, all illegal contact combinations and each open wire. Calibrate actual make and release points for engaged and withdrawn. Each asserted state must imply the required physical pin overlap or clearance. Adjust switch mounts, not nominal OP assumptions.
4. Verify the floor switch changes at the wheel tangent plane and remains protected by the probe's hard stop. Verify hardware travel limits disable the correct direction without software assistance.
5. With the P16 mechanically disconnected, use a restrained current-limited fixture to measure actual stroke and raw ADC millivolts at both ends and at intermediate measured positions. The phone status reports raw millivolts even while calibration is uncommissioned. Do not infer stroke from elapsed time.
6. Enter measured zeroMv/fullMv in calibration::POT, verify direction and interpolation error, then set commissioned=true. The nominal232/2777mV values are estimates only. Repeat open-reference and open-wiper tests. Rebuild both firmware and filesystem after source changes.
7. Configure steering with its horn off. Apply1500us, fit the trimmed horn at the documented neutral angle and set the link to62.096699mm centres. Confirm±8degree yaw without binding.
8. Configure the lock servo with the mechanism unloaded. The nominal1500us engaged and1734us withdrawn pulses require physical calibration. Confirm full6mm pull and free spring-only return; never use the switch as a hard mechanical stop.
9. Flash using the existing PlatformIO romeo environment only after the preceding checks. Connect USB, run pio run -d firmware -t upload, then pio run -d firmware -t uploadfs. These are manual commissioning commands; this design session has not executed them.
10. Join the robot's phone Wi-Fi interface. Test arming, lease expiry, stop, disconnect and every fault with wheels lifted. Verify left/right/centre direction before any floor test. Use external body restraint for the first stance transfer.
11. Measure current, voltage and temperature during progressively loaded motion. Confirm positive pin engagement, centre-foot contact, static stability and no drift after power loss. Test one failure at a time. Reject any binding, brownout, overheating or load-path damage.

## Verification evidence

python -m unittest discover -s tests -p test_firmware*.py -v passes the three host tests, including367 stance assertions. node --test firmware/test/ui_test.js passes the phone-control test suite. pio run -d firmware and pio run -d firmware -t buildfs both succeeded on2026-09-13. Firmware uses45516 bytes RAM and912221 bytes flash in that build. Commit d12fee5 contains the calibration gate, floor interlocks and phone status changes.

Sixteen original MP3s are included in the filesystem image. They are synthetic robot sounds, not movie recordings. Circuit source is scripts/electronics.py; generated wiring has113 point-to-point rows. Build success and simulated faults do not verify motors, current limits, sensors, radio range, thermal behaviour or physical strength.

Primary electrical and mechanical source evidence is retained in printed-frame-research.md. The factory-assembly candidate and its purchase-count boundary are described in control-assembly-specification.md.
