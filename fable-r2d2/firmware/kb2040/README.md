# KB2040 controller — files to copy to CIRCUITPY

Board: Adafruit KB2040 (product 5302, RP2040).
Firmware: CircuitPython 9.x for `adafruit_kb2040`.

## Files from this directory

Copy all three to the **root** of the CIRCUITPY drive:

| File          | Purpose |
| ------------- | ------- |
| `boot.py`     | Enables the second USB CDC endpoint so the Pi has a data port separate from the REPL. Takes effect only after a hard reset or power cycle. |
| `code.py`     | The controller: seven motors, 17 NeoPixels, dome index sensor, serial protocol, heartbeat. |
| `protocol.py` | Hardware-free parsing, ramp and duty maths. `code.py` imports it; `test_protocol.py` tests it on a workstation and is **not** copied to the board. |

## Library files from the CircuitPython 9 bundle

Download `adafruit-circuitpython-bundle-9.x-mpy-<date>.zip` from
<https://circuitpython.org/libraries>, then copy from its `lib/` folder into
`CIRCUITPY/lib/`:

| Bundle file    | Needed by |
| -------------- | --------- |
| `neopixel.mpy` | The dome NeoPixel chain (`L` and `P` commands). |

That is the whole list. Everything else `code.py` uses — `board`, `digitalio`,
`pwmio`, `usb_cdc`, `time` — is built into the CircuitPython binary, so no other
bundle file is required. If `neopixel.mpy` is missing the firmware still drives
all seven motors and answers `err neopixel unavailable: ...` to `L` and `P`.

Resulting layout:

```
CIRCUITPY/
    boot.py
    code.py
    protocol.py
    lib/
        neopixel.mpy
```

## Pin map

Verified against `ports/raspberrypi/boards/adafruit_kb2040/pins.c` in the
CircuitPython source tree. Silkscreen name = `board` attribute = RP2040 GPIO.

| Function                      | `board` name | GPIO | Role |
| ----------------------------- | ------------ | ---- | ---- |
| Driver 1 (left foot) AIN1     | `board.D2`   | 2    | LF-front, digital |
| Driver 1 (left foot) AIN2     | `board.D3`   | 3    | LF-front, **PWM** |
| Driver 1 (left foot) BIN1     | `board.D4`   | 4    | LF-rear, digital |
| Driver 1 (left foot) BIN2     | `board.D5`   | 5    | LF-rear, **PWM** |
| Driver 2 (right foot) AIN1    | `board.D6`   | 6    | RF-front, digital |
| Driver 2 (right foot) AIN2    | `board.D7`   | 7    | RF-front, **PWM** |
| Driver 2 (right foot) BIN1    | `board.D8`   | 8    | RF-rear, digital |
| Driver 2 (right foot) BIN2    | `board.D9`   | 9    | RF-rear, **PWM** |
| Driver 3 (centre foot) AIN1   | `board.D10`  | 10   | CF-front, **PWM** |
| Driver 3 (centre foot) AIN2   | `board.MOSI` | 19   | CF-front, digital |
| Driver 3 (centre foot) BIN1   | `board.MISO` | 20   | CF-rear, digital |
| Driver 3 (centre foot) BIN2   | `board.SCK`  | 18   | CF-rear, **PWM** |
| Driver 4 (head) AIN1          | `board.A0`   | 26   | head, digital |
| Driver 4 (head) AIN2          | `board.A1`   | 27   | head, **PWM** |
| All four DRV8833 `SLP`        | `board.D1`   | 1    | high = drivers awake |
| NeoPixel data (17 pixels)     | `board.A2`   | 28   | front PSI 0-6, rear PSI 7-13, holoprojectors 14-16 |
| Dome index sensor, active low | `board.A3`   | 29   | optional, internal pull-up |
| Spare                         | `board.D0`   | 0    | unused |
| STEMMA QT SDA / SCL           | `board.SDA` / `board.SCL` | 12 / 13 | reserved, unused |

**`board.SDA` and `board.SCL` are GPIO 12 and 13 on this board, not `D2` and
`D3`.** The STEMMA QT connector therefore stays free while `D2` and `D3` drive a
motor.

## Why one PWM pin per motor instead of two

The RP2040 has eight PWM slices of two channels each. GPIO *n* is hard-wired to
slice `(n >> 1) & 7`, channel `n & 1`, so any two GPIOs sixteen apart are the
*same* PWM output. In this pin map that makes four unavoidable collisions:

```
GP2 / GP18  -> slice 1 channel A
GP3 / GP19  -> slice 1 channel B
GP4 / GP20  -> slice 2 channel A
GP10 / GP26 -> slice 5 channel A
```

Fourteen simultaneous `pwmio.PWMOut` objects are therefore impossible here;
`pwmio` raises on the fifth allocation and the firmware would not start.

`code.py` instead gives each motor **one** PWM pin and **one** plain digital
pin, choosing the PWM pin so that the seven land on seven different
slice/channel pairs (GP3, GP5, GP7, GP9, GP10, GP18, GP27). All four DRV8833
states are still reachable:

| Digital pin | PWM pin duty | DRV8833 state | Used for |
| ----------- | ------------ | ------------- | -------- |
| low  | 0            | both low  | coast |
| high | `FULL*(1-m)` | forward   | forward at magnitude `m`, slow decay |
| low  | `FULL*m`     | reverse   | reverse at magnitude `m`, fast decay |
| high | `FULL`       | both high | brake |

`protocol.pwm_conflicts()` re-checks the plan and `code.py` reports
`err pwm slice clash ...` over serial if anyone edits `MOTORS` into a collision.

### Consequence for wiring

Forward uses slow decay and reverse uses fast decay, so a motor is slightly
stronger in the slow-decay direction at the same duty. That direction is the one
where the digital pin is high. **Wire each motor's two leads to its DRV8833
output pair so the slow-decay direction drives the robot forward.** If a motor
turns the wrong way, swap its two leads at the driver output (preferred), or set
its `invert` flag to `True` in the `MOTORS` table in `code.py` — the flag works,
but it moves that motor's slow-decay direction to reverse.

## Bench check without the Pi

Open the data endpoint at 115200 with any terminal and type:

```
E 1
M 300 300 300 0
S
E 0
?
```

The board answers `ok` to each and `st <enabled> <l> <r> <c> <h> <index>` to
`?`, plus an unsolicited `st` line every 200 ms. Stop typing for half a second
and it answers `err heartbeat timeout, motors coasted`, which is the watchdog
doing its job.
