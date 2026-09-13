# Revision D controls: DFR0994 migration and interlocked stance change

Status 2026-09-12: digital design and host verification complete. No hardware was purchased,
flashed, wired or driven. Mechanism constants are provisional until
`scripts/check_kinematics.py` passes on the committed CAD. They live in one block,
`PROVISIONAL MECHANISM CONSTANTS`, in `firmware/include/config.h`.

## Controller: DFRobot Romeo ESP32-S3 (DFR0994)

Primary sources: [wiki](https://wiki.dfrobot.com/dfr0994/),
[product page](https://www.dfrobot.com/product-2743.html),
[schematic V1.1.0](https://dfimg.dfrobot.com/wiki/22811/DFR0994_romeo-esp32-s3_schematics_V1.1.zip), dated 2025-09-08.

- ESP32-S3-WROOM-1U-N16R8: 16 MB flash, 8 MB PSRAM. PlatformIO board `dfrobot_romeo_esp32s3`, `espressif32@6.5.0`.
- Four onboard TI DRV8876 H-bridges, U1-U4, on one shared VREF: 5.1k over 20k from 3.3 V, 2.629 V, which gives a nominal 2.629 A trip. IPROPI is 1k per channel. nFAULT and IPROPI are not routed to the MCU. nSLEEP is pulled high.
- VIN (P23) is 7-24 V into the SCT2650 buck, through onboard FUSE1, 3 A. VM (P22) is 5-24 V. **JP6** joins them when fitted. The wiki page labels this link "JP1".
- `5V_Servo` is the same SCT2650 5 V logic rail (2 A), fed through diode D14. The servos therefore do not use it.
- No IMU, accelerometer or gyroscope is fitted or listed.
- PMODE link fitted: PH/EN mode (EN = PWM, PH = direction).

Required board setup: **remove JP6** (VIN on MAIN, VM on the RUN-switched 5.70 V rail). **Fit PMODE.**
**Replace R9 20k with 5.60k 1% and R10 1k with 2.00k 1%.** Match the footprint on the delivered board; it has not been checked.

### Channel and current check

| Load | Supply | Stall current | Driver | Protection |
|---|---|---|---|---|
| Left foot: two Adafruit 3777 in parallel | 5.70 V VM | ≤1.5 A each at 6 V, ≈2.85 A pair at 5.7 V | DRV8876 M1 | 1.73 A trip after R9 rework (stock 2.63 A does not limit a stalled pair) |
| Right foot pair | 5.70 V VM | ≈2.85 A | M2 | 1.73 A |
| Centre foot pair | 5.70 V VM | ≈2.85 A | M3 | 1.73 A |
| Head 3777 | 5.70 V VM | ≈1.43 A | M4 | 0.86 A after R10 rework |
| Actuonix P16-100-256-12-P | 12 V | 1.0 A | **extra** Adafruit DRV8871 (3190) | ILIM 71.5k: 0.82-0.98 A |

The four onboard channels are enough for the three foot pairs and the head. The 12 V actuator needs the minimum extra driver hardware:
one DRV8871 breakout, whose terminal blocks come pre-soldered, and one 71.5k ILIM resistor.
The DRV8876 short-circuit OCP is at least 3.5 A, so a stalled pair does not nuisance-trip it.
Parallel motors share a trip, not equal current. Loaded wheel-jam temperature tests remain a commissioning gate.

Motor-rail budget, ICStation 11060 rated 8 A: with the rework, three pairs + head = 6.05 A, plus the steering MG995 ≈1.2 A, gives ≈7.25 A.
Firmware allows the lock-release servo to move only while wheels and head are idle.
Without the rework the four trips alone total 10.5 A.

## Pin map (firmware/include/config.h)

| Function | GPIO | Path |
|---|---|---|
| Left pair EN / PH | 12 / 13 | onboard M1 |
| Right pair EN / PH | 14 / 21 | onboard M2 |
| Centre pair EN / PH | 9 / 10 | onboard M3 |
| Head EN / PH | 47 / 11 | onboard M4 |
| I2S BCLK / LRC / DIN | 15 / 16 / 17 | MAX98357A |
| Steering servo | 40 | 74AHCT125 gate 3 → SV1 |
| Lock-release servo | 41 | 74AHCT125 gate 4 → SV2 |
| Post extend / retract | 38 / 42 | AHCT125 gates 1/2 → DRV8871 IN1/IN2 |
| Extend / retract limit open | 7 / 8 | NC limit on the gate OE node, 10k to 3.3 V |
| Lock NO / NC | 18 / 5 | SS-01GL, COM to GND, 3.3k pull-ups |
| Post position | 4 (ADC1_CH3) | P16 wiper; ref+ through 2.2k to 3.3 V; 470k pulldown |
| Battery | 6 (ADC1_CH5) | 100k/22k divider |
| RUN rail present | 39 | 10k/10k from the 5.70 V rail |

The map avoids strapping pins (0, 3, 45, 46), USB (19, 20), UART0 (43, 44), and flash/PSRAM (26-37).
Camera, GDI display and microSD functions are unused. `verify.py --firmware-only` checks
that every configured GPIO matches `electronics/wiring.csv`.

## Power and wiring

`python scripts/electronics.py` writes `electronics/wiring.csv` (98 connections), seven connection sheets and
`00-power-overview.svg`. The layout: B1 → F1 7.5 A → S1 MAIN. MAIN feeds Romeo VIN (logic, audio,
buffer) and S2 RUN. RUN feeds F2 5 A → ICStation 11060 at 5.70 V (Romeo VM plus both MG995 servos), and
F3 2 A → Pololu S13V25F12 at 12 V (DRV8871 → P16). RUN off removes all motor, servo and actuator power.

The NC travel limits, set at about 0.3 and 99.7 mm, hold each 74AHCT125 enable low while closed. An open switch
or a broken wire disables that actuator direction in hardware. The MCU also reads both nodes.

## Stance state machine (firmware/include/stance.h)

States: `THREE_FOOT`, `RETRACTING`, `DEPLOYING`, `TWO_FOOT`, `HELD`, `FAULT`. The logic is pure C++11 behind
`StanceHal`: position feedback, lock-engaged sensor, travel limits, power, heartbeat, actuator drive and
lock release. The same code runs in the host tests and on the ESP32-S3.

Post stroke s in mm: two-foot 2, upright floor contact 36.647 (the 0° receiver), three-foot 98 (the 16.163° receiver).
The GN 412 spring plunger seats in a receiver at **both** endpoints: GN 412.2 bushings at pin radius 55 mm.
The sensed lock geometry is `cad/stance-lock-sensed.scad`, using the `SL_` constants. It is not yet in the assembly.
Until it is, `cad/stance-lock.scad` holds a different GN817 study that this firmware does not model.

Three feet to two feet (`RETRACTING`):
1. UNLOCKING: post stopped, release servo pulls the pin, wait for the sensor to read out.
2. TILT: retract at 100%. The release is held until the pin has swept 7.2 mm of arc (bore + 1 mm) off the receiver, at s ≤ 62. It then drops so the pin rides the ring face.
3. LOCKING at contact + 1.5: settle 400 ms, then creep at 60% duty toward contact − 0.8 until the sensor reads seated.
4. LIFT: retract to 2 mm, only while the sensor reads seated → `TWO_FOOT`.

Two feet to three feet (`DEPLOYING`): LOWER to contact with the pin seated → UNLOCKING → TILT (release
dropped at s ≥ 60) → LOCKING creep through 98 → pin seated → `THREE_FOOT`.

Interlocks:
- Lock state comes only from the SS-01GL NO/NC pair. Exactly one closed contact is valid; the reading is debounced 30 ms, and an invalid pair must persist 150 ms before it counts. Post position never implies a lock state.
- A seated reading is required whenever s < contact − 2.5. A seated reading between the two receiver windows is a fault.
- Ground drive only in `THREE_FOOT`. Head only in `THREE_FOOT` or `TWO_FOOT`. The API refuses drive/head commands in other states, and the motion task gates outputs again.
- A start needs RUN power and a valid battery reading, a fresh armed heartbeat, wheels and head stopped with steering centred, a fresh button press, and the actuator cooldown elapsed. The P16 is rated 20% duty, so 4 ms of rest follows each ms of travel.
- The stance change is hold-to-run. Releasing the button, losing the 500 ms command heartbeat, reversing the request or sending a drive/head/steer command stops the actuator immediately in `HELD`. The lock command is left unchanged. Recovery never restarts automatically.
- These faults stop the actuator and latch `FAULT`: `POWER` (lost mid-change), `FEEDBACK` (pot out of window or band), `LOCK_SENSOR`, `TRAVEL_LIMIT`, `OVERTRAVEL`, `STALL` (less than 0.5 mm in 750 ms), `TRAVEL_TIMEOUT` (40 s per phase), `LOCK_TIMEOUT` (pin not in or out within 1.5 s), `LOCK_DISAGREES`, `DRIFT`, `REVERSED_FEEDBACK`. A new fault disarms the phone. Clearing requires an armed lease, and succeeds only if fresh sensors describe a consistent mechanism. Clearing never moves the lock.
- The spring-return lock re-seats itself when release power is lost.

## Posture estimate (firmware/include/posture.h)

The board has no IMU, so the estimate is **state-based**:
- Pin seated at contact or below: the body is held at 0° by the 0° receiver ("shoulder lock geometry").
- Centre foot on the floor with the pin out, or seated in the three-foot receiver: pitch comes from the three-foot kinematics in `cad/kinematics.scad` ("three-foot post kinematics"). At 98 mm this gives 16.163°.
- Fault, invalid sensor, or a contradiction (foot raised without a seated pin, or a seated reading between receivers): `unknown`.

The lifted foot rests on its heel stop at +1°. That is foot pitch, not body pitch, and does not change the estimate.
The estimate cannot detect a tip-over or an external push. Stationary two-foot standing only.

## Phone UI and API

`/api/status` reports `stance`, `phase`, `fault`, `reason`, `post_mm`, `lock_valid`, `lock_engaged`, `limits_closed`,
`pitch_deg`, `pitch_source`, `drive_allowed`, `head_allowed`, `can_two_foot`, `can_three_foot` and the blocking interlock text.
`/api/command` accepts `stance` values -1, 2 or 3. A stance request must carry zero speed, turn and head.
`/api/stance/clear` needs the current lease.
The page greys out stance, drive and head buttons whenever an interlock forbids them and shows why.
The held stance button stays enabled during its own change.

## Verification (2026-09-12)

```
pio run -d C:/dev/robots/r2d2/firmware                 -> exit 0, Flash 44.9%, RAM 13.9%
pio run -d C:/dev/robots/r2d2/firmware -t buildfs      -> exit 0
python scripts/verify.py --firmware-only               -> exit 0
python -m unittest discover -s tests -p "test_firmware*.py"   -> OK (3 tests)
python -m unittest discover -s tests -p "test_ui*.py"         -> OK (3 tests)
```

`firmware/test/stance_test.cpp` (1087 checks) runs the real state machine against a plant model:
a non-backdrivable post and a spring pin with two receivers. It covers:
- both normal transitions;
- command loss in LIFT, TILT and UNLOCKING, and operator release;
- power loss, feedback loss, travel-limit open and reversed feedback;
- actuator stall, travel timeout, and a pin stuck in either receiver;
- a pin that never seats at contact or at three-foot;
- lock-sensor disagreement at both endpoints and mid-change;
- drive requested during a transition, and reversal;
- `millis()` wraparound, NO/NC debounce, pot open-circuit windows, and posture geometry.

`firmware/test/ui_test.js` executes the real `app.js` against a simulated DOM and network.

## Commissioning gates and open items

- Bind the final mechanism constants when `check_kinematics.py` passes, then rerun `verify.py --firmware-only`.
- Measure `POT.zeroMv`/`fullMv` on the detached P16; its pot tolerance is ±50%. Calibrate `LOCK_RELEASE_US`/`LOCK_ENGAGE_US` on the lever.
- Lock seek: at contact the pin crosses its 0.1 mm clearance in about 0.15 s at 60% duty. If the pin does not catch, lower `seekDutyPercent`; try 40% first.
- Check SS-01GL contact reliability at 3.3 V/1 mA, below Omron's 5 V/1 mA reference point.
- Before connecting VM, measure the 5.70 V rail (accept 5.50-6.00 V, including braking transients), all four DRV8876 trips after rework, and the DRV8871 limit.
- Test open-wire behaviour on each NC limit and the lock contacts, reset/brown-out with the actuator loaded, and loaded wheel-jam temperatures.
- `scripts/build_manual.py` still asserts revision C electrical text ("220 wiring connections", "DRV8833"). The integration step must update it before a revision D manual build.
