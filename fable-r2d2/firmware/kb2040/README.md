# KB2040 controller — files to copy to CIRCUITPY

Board: Adafruit KB2040 (product 5302, RP2040).
Firmware: CircuitPython 9.x for `adafruit_kb2040`.
Revision D: the board also runs the interlocked, motorized stance change.

## Files from this directory

Copy these five to the **root** of the CIRCUITPY drive:

| File            | Purpose |
| --------------- | ------- |
| `boot.py`       | Enables the second USB CDC endpoint so the Pi has a data port separate from the REPL. Takes effect only after a hard reset or power cycle. |
| `code.py`       | Pins and hardware: four drive outputs, the DRV8871 actuator, two release servos, two lock switches, the actuator pot, the battery divider, 17 NeoPixels, the dome index sensor, and the serial loop. |
| `supervisor.py` | Hardware-free controller core: protocol, Pi heartbeat, drive ramp, ground-drive and dome interlocks. |
| `stance.py`     | Hardware-free stance state machine, sensor conditioning and the one `MECHANISM CONSTANTS` block. |
| `protocol.py`   | Hardware-free parsing, ramp, duty and RP2040 PWM-slice maths. |

`test_protocol.py` and `test_stance.py` run on a workstation and are **not**
copied to the board.

If the board reports `MemoryError` while importing `stance.py` or
`supervisor.py`, compile them with `mpy-cross` from the CircuitPython 9
release (`mpy-cross stance.py` gives `stance.mpy`) and copy the `.mpy` files
instead of the `.py` files. The behaviour is identical.

## Library files from the CircuitPython 9 bundle

Download `adafruit-circuitpython-bundle-9.x-mpy-<date>.zip` from
<https://circuitpython.org/libraries>, then copy from its `lib/` folder into
`CIRCUITPY/lib/`:

| Bundle file    | Needed by |
| -------------- | --------- |
| `neopixel.mpy` | The dome NeoPixel chain (`L` and `P` commands). |

Everything else — `board`, `digitalio`, `analogio`, `pwmio`, `usb_cdc`, `time` —
is built into the CircuitPython binary. If `neopixel.mpy` is missing the
firmware still drives every motor and the stance change, and answers
`err neopixel library missing` to `L` and `P`.

Resulting layout:

```
CIRCUITPY/
    boot.py
    code.py
    supervisor.py
    stance.py
    protocol.py
    lib/
        neopixel.mpy
```

## Pin map (revision D, all 20 GPIOs used)

Verified against `ports/raspberrypi/boards/adafruit_kb2040/pins.c`.
Silkscreen name = `board` attribute = RP2040 GPIO. `test_stance.py` checks that
every GPIO is used once, that the PWM plan is legal and that both analogue
inputs are on ADC pins; `python scripts/electronics.py` checks the same pins
against `electronics/wiring.csv`.

| Function | `board` name | GPIO | Role |
| -------- | ------------ | ---- | ---- |
| Left foot, U1 AIN1 + BIN1 (jumpered) | `board.D2` | 2 | digital |
| Left foot, U1 AIN2 + BIN2 (jumpered) | `board.D3` | 3 | **PWM** 20 kHz, slice 1B |
| Head, U4 AIN1 | `board.D4` | 4 | digital |
| Head, U4 AIN2 | `board.D5` | 5 | **PWM** 20 kHz, slice 2B |
| Right foot, U2 AIN1 + BIN1 (jumpered) | `board.D6` | 6 | digital |
| Right foot, U2 AIN2 + BIN2 (jumpered) | `board.D7` | 7 | **PWM** 20 kHz, slice 3B |
| Actuator, U10 DRV8871 IN1 | `board.D8` | 8 | digital |
| Actuator, U10 DRV8871 IN2 | `board.D9` | 9 | **PWM** 20 kHz, slice 4B |
| Centre foot, U3 AIN2 + BIN2 (jumpered) | `board.D10` | 10 | **PWM** 20 kHz, slice 5A |
| Centre foot, U3 AIN1 + BIN1 (jumpered) | `board.MOSI` | 19 | digital |
| Left release servo SV1, via U11 channel 1 | `board.D0` | 0 | **PWM** 50 Hz, slice 0A |
| Right release servo SV2, via U11 channel 2 | `board.D1` | 1 | **PWM** 50 Hz, slice 0B |
| Left lock switch SW2, NO | `board.SCK` | 18 | input, 3.3 k pull-up, low = closed |
| Left lock switch SW2, NC | `board.MISO` | 20 | input, 3.3 k pull-up, low = closed |
| Right lock switch SW3, NO (STEMMA QT, J14 blue) | `board.SDA` | 12 | input, 3.3 k pull-up, low = closed |
| Right lock switch SW3, NC (STEMMA QT, J14 yellow) | `board.SCL` | 13 | input, 3.3 k pull-up, low = closed |
| Actuator pot wiper | `board.A0` | 26 | ADC, 470 k pull-down |
| Battery divider, 100 k over 15 k | `board.A1` | 27 | ADC |
| NeoPixel data (17 pixels) | `board.A2` | 28 | front PSI 0-6, rear PSI 7-13, holoprojectors 14-16 |
| Dome index sensor, active low | `board.A3` | 29 | optional, internal pull-up |
| All four DRV8833 `SLP` | 3V3 pad | — | tied high; arming is done in firmware |

### What changed from revision C, and why

Revision C used 17 GPIOs: one PWM and one digital pin for each of seven motors,
plus SLP, NeoPixel and index. The stance change needs 12 more signals. They fit
because:

* both motors in a foot always get the same value, so each foot's two DRV8833
  channels share one pin pair (jumper AIN1 to BIN1 and AIN2 to BIN2 on the
  board); that frees D4, D5, D8, D9, SCK and MISO;
* the head moves from A0/A1 to D4/D5, so two of the only four ADC pins can read
  the actuator pot and the battery;
* SLP is tied to the KB2040 3V3 pad, freeing D1 for the second servo; disarmed
  outputs are held at coast by firmware, which is the same MCU that drove SLP;
* the right lock switch uses GP12/GP13 through the STEMMA QT connector and cable
  J14.

Per-motor `invert` flags are gone with the pairing: wire each motor so the
slow-decay direction (digital pin high) drives the robot forward, and swap its
two leads at the driver output if it does not.

## Why one PWM pin per output

The RP2040 has eight PWM slices of two channels. GPIO *n* is slice
`(n >> 1) & 7`, channel `n & 1`, so GPIOs sixteen apart are the *same* output,
and both channels of one slice share one frequency. The five 20 kHz outputs use
five different slice/channel pairs; the two 50 Hz servos use both channels of
slice 0 and nothing else. Each output gets one PWM pin and one digital pin, which
still reaches all four H-bridge states on both the DRV8833 and the DRV8871:

| Digital pin | PWM pin duty | State | Used for |
| ----------- | ------------ | ----- | -------- |
| low  | 0            | both low  | coast (the DRV8871 also sleeps) |
| high | `FULL*(1-m)` | forward   | forward / extend at magnitude `m`, slow decay |
| low  | `FULL*m`     | reverse   | reverse / retract at magnitude `m`, fast decay |
| high | `FULL`       | both high | brake |

`code.py` re-checks the plan at boot and answers
`err pwm slice clash ...` or `err pwm frequency clash ...` if the pin table is
ever edited into a collision.

## Bench check without the Pi

Open the data endpoint at 115200 with any terminal and type:

```
E 1
M 300 300 300 0
S
E 0
?
```

The board answers `ok` to each line, and to `?` it sends two status lines:
`st <enabled> <l> <r> <c> <h> <index>` and
`ss <state> <phase> <fault> <pos_0.1mm> <locks> <pack_mv> <drive_ok> <head_ok> <can_two> <can_three> <reason>|<why_two>|<why_three>`.
Both also arrive unsolicited every 200 ms. Stop typing for half a second and it
answers `err heartbeat timeout, motors coasted`.

`M` values are refused unless `ss` reports `THREE_FOOT`: the board then answers
`err drive refused (...)`. A stance change needs `E 1` and a `T 2` or `T 3`
line repeated at least every 500 ms; a terminal cannot comfortably do that, so
exercise the stance change from the control page.
