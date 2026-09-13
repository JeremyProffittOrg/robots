# fable-r2d2 firmware

Two processors, one job each.

**Adafruit KB2040** (product 5302, RP2040, CircuitPython 9) is the motor, light
and stance controller. It drives seven Adafruit 3777 TT motors through four
DRV8833 (3297) boards, drives the 17 pixel dome NeoPixel chain, reads the dome
index sensor, and coasts every motor if the Pi stops talking for 500 ms. In
revision D it also owns the interlocked stance change: the 12 V centre-leg
actuator through a DRV8871, two lock-release servos, two NO/NC lock switches, the
actuator potentiometer and its own battery divider (section 11).

**Raspberry Pi 4** (Raspberry Pi OS Bookworm, 64 bit) is everything else. It
serves the phone control page over its own Wi-Fi access point, mixes the
joystick into three foot channels, streams commands to the KB2040 over USB CDC
at 20 Hz, animates the head displays, and plays the sound clips.

```
 phone browser ──WebSocket──► Pi: server.py ──USB CDC 115200──► KB2040: code.py
                                   │                                  │
                                   ├─ displays.py  HT16K33 x4, GC9A01A ├─ 7 x DRV8833 channels
                                   ├─ audio.py     aplay / pygame      ├─ 17 x NeoPixel
                                   ├─ battery.py   ADS1115 (optional)  ├─ DRV8871 -> actuator (+ pot)
                                   └─ stance_link.py  lease, gate      └─ 2 x servo, 2 x lock switch
```

---

## 1. Files

### KB2040 — `firmware/kb2040/`

| File | Purpose |
| ---- | ------- |
| `boot.py` | Enables the second USB CDC endpoint (the Pi's data port). |
| `code.py` | Pins and hardware: motors, actuator, servos, lock switches, pot, battery, pixels, index sensor, serial loop. |
| `supervisor.py` | Hardware-free controller core: protocol handling, heartbeat, drive ramp, drive and dome interlocks. |
| `stance.py` | Hardware-free stance state machine, sensor conditioning, the `MECHANISM CONSTANTS` block. |
| `protocol.py` | Hardware-free parser, ramp, duty and PWM-slice maths. |
| `test_protocol.py` | CPython unit tests for `protocol.py`. Not copied to the board. |
| `test_stance.py` | CPython tests: pin plan, sensor conditioning, and the supervisor against a simulated plant. Not copied. |
| `README.md` | Exact copy list, bundle libraries, pin table, bench check. |

### Raspberry Pi — `firmware/pi/`

| File | Purpose |
| ---- | ------- |
| `server.py` | aiohttp server: static page, WebSocket, control state, workers. |
| `mixing.py` | Differential drive maths, clamps, speed cap, minimum duty, ramp. |
| `serial_link.py` | Background thread owning the USB CDC port; 20 Hz command stream. |
| `displays.py` | Four 8x8 HT16K33 logic matrices and the radar eye. |
| `audio.py` | WAV playback through `aplay`, or `pygame.mixer` as a fallback. |
| `battery.py` | Optional pack voltage through an ADS1115. |
| `stance_link.py` | Stance lease (hold-to-run), `ss` parser, the Pi-side drive and dome gate. |
| `test_mixing.py` | CPython unit tests for `mixing.py`. |
| `test_stance_link.py` | CPython tests for `stance_link.py`, plus Pi-to-KB2040 end-to-end runs on the simulated plant. |
| `requirements.txt` | Pi Python dependencies. |
| `r2d2.service` | systemd unit. |
| `static/index.html`, `static/app.js`, `static/style.css` | The control page. |
| `sounds/*.wav` | Twelve generated clips, 22.05 kHz 16 bit mono. |

### Elsewhere

| File | Purpose |
| ---- | ------- |
| `scripts/generate_audio.py` | Synthesises the twelve clips and writes the catalogue. |
| `audio/catalog.csv` | `name, file, seconds, sha256` for every clip. |

### Dome display and I2C map

Everything in this table is on the **Raspberry Pi's own I2C bus 1** (header pins
3 and 5, `/dev/i2c-1`) except the radar eye, which is on the Pi's SPI0. The
KB2040 drives no display at all; in revision D its STEMMA QT pins (GP12/GP13) read
the right shoulder lock switch instead of an I2C bus.

| Device | Bus | Address | Driven as |
| ------ | --- | ------- | --------- |
| Front logic, **upper window** | I2C-1 | `0x70` | Adafruit 0.8 inch 8x8 mini matrix backpack, `Matrix8x8`, its own animation |
| Front logic, **lower window** | I2C-1 | `0x71` | Adafruit 0.8 inch 8x8 mini matrix backpack, `Matrix8x8`, its own animation |
| Rear logic, **left** (seen from behind) | I2C-1 | `0x72` | 8x8 backpack, columns 0-7 of one 16x8 strip |
| Rear logic, **right** (seen from behind) | I2C-1 | `0x73` | 8x8 backpack, columns 8-15 of the same strip |
| Battery ADC, optional | I2C-1 | `0x48` | ADS1115, channel `A0`/`P0` |
| Radar eye | SPI0 | CE0 | GC9A01A 240x240, DC GPIO25, RST GPIO24, backlight GPIO18 |

Four 0.8 inch **8x8** backpacks, not three 8x16 units. Set each backpack's
address with its `A0`/`A1` solder jumpers: none bridged gives `0x70`, `A0`
bridged `0x71`, `A1` bridged `0x72`, both bridged `0x73`.

The two **front** windows are independent displays and get independent
animations with separate random seeds, so the upper and lower windows never fall
into the same rhythm. The two **rear** backpacks are treated as one 16 column by
8 row strip sharing a single pattern that scrolls sideways across the seam, so
the movement carries from one unit to the other instead of stopping between
them.

Degradation is per device. A backpack that does not answer at start up, or that
stops answering later, is logged with its address and dropped while the others
keep running. If only one rear backpack answers, the strip still runs on that
half.

### Battery sensing: two dividers, two readers

Revision D adds a second, independent battery reading on the KB2040, because
the stance interlock must not depend on an optional Pi sensor.

* `firmware/pi/battery.py` still reads **only** an ADS1115 on the **Pi's** I2C-1
  bus at `0x48`, channel `A0`, through R2 100 k over R3 15 k. It is optional and
  only drives the header gauge.
* The KB2040 reads its own divider, R9 100 k over R10 15 k, on `A1` (GP27, an ADC
  pin freed by moving the head drive to D4/D5). `stance.BatteryGuard` treats a
  pack below 11.2 V for 500 ms, or above 15.2 V, or no reading, as no power; power
  returns only at 12.0 V for 500 ms. No power blocks a stance start and latches
  `POWER` during a change. The pack millivolts are in the `ss` line.
* The two dividers are separate wires to separate grounds, so either reader works
  with the other absent.

---

## 2. Serial protocol

ASCII, newline terminated, 115200 8N1 on the KB2040's second USB CDC endpoint
(`/dev/ttyACM1` on a Pi with nothing else plugged in).

### Pi to KB2040

| Line | Meaning |
| ---- | ------- |
| `M <l> <r> <c> <h>` | Drive permille, each `-1000..1000`: left foot, right foot, centre foot, head. Both motors in a foot get that foot's value. Out of range values are clamped, not rejected. |
| `L <r> <g> <b>` | Set all 17 pixels, each channel `0..255`. |
| `P <i> <r> <g> <b>` | Set one pixel, `i` in `0..16`. |
| `E <0\|1>` | Arm (1) or disarm (0) the ground and dome motors. Disarming zeroes and coasts them and holds a stance change in progress. The DRV8833 `SLP` pins are tied high in revision D, so arming is done in firmware. |
| `S` | Stop: targets and outputs to zero at once. |
| `?` | Status request. Answered with `st` and `ss`. |
| `T <0\|2\|3>` | Stance request, hold-to-run: 2 two feet, 3 three feet, 0 none. The Pi repeats it with every `M` line (20 Hz). A request older than 500 ms counts as none, but only an explicit `T 0` counts as the operator letting go. |
| `C` | Clear a latched stance fault. `ok` if fresh sensors describe a consistent mechanism, else `err fault not cleared: <reason>`. |

### KB2040 to Pi

| Line | Meaning |
| ---- | ------- |
| `ok` | The previous command was executed. |
| `st <enabled> <l> <r> <c> <h> <index>` | Status. `enabled` and `index` are 0/1; the four channels are the post-ramp permille actually applied. Sent on `?` and unsolicited every 200 ms. |
| `ss <state> <phase> <fault> <pos> <locks> <pack_mv> <drive_ok> <head_ok> <can_two> <can_three> <reason>\|<why_two>\|<why_three>` | Stance status, with `st`. `pos` is actuator stroke in 0.1 mm and `pack_mv` the KB2040 battery reading, each -1 when invalid. `locks` is one letter per lock, left first: `E` seated, `R` released, `X` switch invalid, `W` debouncing. The flags are 0/1. The texts say why each stance request is blocked, empty when it may start. |
| `err <text>` | The line could not be executed, the heartbeat expired, or a drive command was refused (`err drive refused (ground drive): stance change in progress`). |

### Rates and limits

* **Tick**: 10 ms on the KB2040.
* **Ramp**: at most 40 permille per tick per channel, so a full `-1000` to
  `+1000` reversal takes 50 ticks (500 ms). The Pi applies the same limit at
  200 permille per 50 ms command, so the value it reports is the value the
  motors are really being given.
* **Heartbeat**: no line for 500 ms and every motor coasts, with
  `err heartbeat timeout, motors coasted` sent once. The Pi's 20 Hz `M` stream
  is the heartbeat; it never stops while the server is up. A stance change in
  progress stops the actuator and holds on the same timeout.
* **Pixel index range**: `0..16`. Front PSI jewel 0-6, rear PSI jewel 7-13,
  holoprojectors 14-16.

---

## 3. Drive mixing

The web page sends a joystick position `x, y` each in `-1..1`, with `y` forward
and `x` to the right. `firmware/pi/mixing.py` computes:

```
left   = y + x * turn_gain          turn_gain = 0.70
right  = y - x * turn_gain
centre = y                          the centre foot is a driven caster
```

Each channel is then clamped to `-1..1`, run through the deadband (0.05),
multiplied by the global speed cap (default 0.60, slider range 0.20 to 1.00),
and raised to the minimum duty (0.15 of full) if it is still moving, so a
gearbox never sits buzzing below its stiction. The result is converted to
permille and sent as `M` at 20 Hz.

Worked examples at the default cap:

| Joystick | `M` line |
| -------- | -------- |
| full forward `x=0, y=1` | `M 600 600 600 <head>` |
| full reverse `x=0, y=-1` | `M -600 -600 -600 <head>` |
| spin right `x=1, y=0` | `M 420 -420 0 <head>` |
| centred | `M 0 0 0 <head>` |

Head: the spin buttons hold the dome motor at the head-duty slider value
(default 0.45) while pressed; a nudge runs it for 200 ms. The same 0.15 minimum
duty applies so the friction wheel does not stall against the dome ring.

**Safety.** The page sends a `drive` message or a `ping` at least five times a
second. If the server hears nothing for 500 ms it zeroes the drive; if the page
closes, the server sends `S`; if the server dies, the KB2040's own heartbeat
coasts the motors 500 ms later. The STOP button zeroes the drive and disarms the
motors in one press.

**Interlock (revision D).** Ground drive is allowed only when the KB2040 reports
`THREE_FOOT`; the dome only in `THREE_FOOT` or `TWO_FOOT`. The Pi zeroes the
refused channels before they are sent (`StanceControl.gate`) whenever the `ss`
status is missing, older than 1 s, or does not allow them. The KB2040 refuses them
again on its own, answers `err drive refused (...)`, and holds a stance change in
progress.

---

## 4. KB2040 pin map and why it changed

`firmware/kb2040/README.md` has the full revision D table. All 20 KB2040 GPIOs are
used. `test_stance.py` (class `TestPinPlan`) and `python scripts/electronics.py`
both parse `code.py` and fail if a pin is used twice, a PWM plan collides, an
analogue input leaves the ADC pins, or `wiring.csv` disagrees.

| Signal | Pin | GPIO | PWM slice |
| ------ | --- | ---- | --------- |
| Left foot PWM / direction (U1 A+B jumpered) | D3 / D2 | 3 / 2 | 1B, 20 kHz |
| Right foot PWM / direction (U2 A+B jumpered) | D7 / D6 | 7 / 6 | 3B, 20 kHz |
| Centre foot PWM / direction (U3 A+B jumpered) | D10 / MOSI | 10 / 19 | 5A, 20 kHz |
| Head PWM / direction (U4 A) | D5 / D4 | 5 / 4 | 2B, 20 kHz |
| Actuator DRV8871 IN2 (PWM) / IN1 | D9 / D8 | 9 / 8 | 4B, 20 kHz |
| Release servo left / right (via U11) | D0 / D1 | 0 / 1 | 0A / 0B, 50 Hz |
| Left lock switch NO / NC | SCK / MISO | 18 / 20 | input |
| Right lock switch NO / NC (STEMMA QT, J14) | SDA / SCL | 12 / 13 | input |
| Actuator pot wiper / battery divider | A0 / A1 | 26 / 27 | ADC |
| NeoPixel data / dome index | A2 / A3 | 28 / 29 | — |
| DRV8833 SLP (all four) | 3V3 pad | — | tied high |

### 4.1 One PWM pin per output

The RP2040 has eight PWM slices of two channels. GPIO *n* is hard-wired to slice
`(n >> 1) & 7`, channel `n & 1`, so GPIOs sixteen apart are the *same* output, and
both channels of one slice share one counter and so one frequency. Revision C
already met the first rule: fourteen simultaneous PWM inputs collide at GP2/GP18,
GP3/GP19, GP4/GP20 and GP10/GP26, so each motor gets **one** PWM pin and **one**
plain digital pin (`test_protocol.py` still asserts both facts). All four H-bridge
states remain reachable on the DRV8833 and the DRV8871:

| Digital pin | PWM duty | Bridge | Used for |
| ----------- | -------- | ------ | -------- |
| low | 0 | both low | coast (the DRV8871 also sleeps) |
| high | `65535 * (1 - m)` | forward | forward or extend at magnitude `m`, slow decay |
| low | `65535 * m` | reverse | reverse or retract at magnitude `m`, fast decay |
| high | `65535` | both high | brake |

Revision D adds the second rule: the 50 Hz servos cannot share a slice with a
20 kHz output. They take both channels of slice 0 (GP0, GP1), and the five 20 kHz
outputs sit on slices 1-5. `protocol.pwm_frequency_conflicts()` checks this at
boot and in the tests; `code.py` answers `err pwm frequency clash ...` if the table
is edited into a collision.

### 4.2 Where the twelve new signals came from

Revision C used 17 GPIOs and the stance change needs 12 more. Three changes make
room without adding a board:

1. **Foot channel pairs.** Both motors in a foot always received the same value.
   Each foot's two DRV8833 channels are now driven from one pin pair: jumper AIN1 to
   BIN1 and AIN2 to BIN2 on U1, U2 and U3. That frees D4, D5, D8, D9, SCK and MISO.
   The per-motor `invert` flags go with it: wire each motor so that the slow-decay
   direction drives the robot forward, and swap its two leads at the driver output
   if it does not.
2. **Head off the ADC pins.** The head drive moves from A0/A1 to D4/D5, so A0 and
   A1, two of only four ADC pins, read the actuator pot and the battery.
3. **SLP tied high.** The four DRV8833 SLP pins go to the KB2040 3V3 pad, freeing D1
   for the second servo. `E 0`, `S` and the heartbeat still coast every motor in
   firmware. SLP was driven by the same MCU, so tying it high removes no independent
   safety path; the drivers still sleep when the KB2040 is unpowered.

The right lock switch uses GP12/GP13 on the STEMMA QT connector through cable J14
(Adafruit 4209); `board.SDA` and `board.SCL` are GPIO 12 and 13 on this board.

Two corrections from revision C still stand, both verified against
`ports/raspberrypi/boards/adafruit_kb2040/pins.c` and the library source:
`board.SDA`/`board.SCL` are GP12/GP13, not D2/D3; and the round TFT driver module
in `adafruit_rgb_display` is spelled **`gc9a01a`** (class `GC9A01A`).

---

## 5. Flashing the KB2040

1. Download CircuitPython 9.x for the KB2040 from
   <https://circuitpython.org/board/adafruit_kb2040/> — a `.uf2` file.
2. Plug the KB2040 into a computer with USB-C. Press the `BOOT` button, tap
   `RESET` while holding it, then release `BOOT`. A drive named `RPI-RP2`
   appears.
3. Copy the `.uf2` onto `RPI-RP2`. The board reboots and a drive named
   `CIRCUITPY` appears.
4. Copy `firmware/kb2040/boot.py`, `code.py`, `supervisor.py`, `stance.py` and
   `protocol.py` to the root of `CIRCUITPY`. Do **not** copy `test_protocol.py` or
   `test_stance.py`. If the board reports `MemoryError` on import, copy
   `mpy-cross`-compiled `stance.mpy` and `supervisor.mpy` instead.
5. Download the CircuitPython **9.x** library bundle from
   <https://circuitpython.org/libraries>, and copy **`neopixel.mpy`** from its
   `lib/` folder into `CIRCUITPY/lib/`. That is the only bundle file needed;
   everything else `code.py` uses is built into the firmware. In particular the
   four HT16K33 logic matrices and the radar eye are driven from the **Pi**, so
   `adafruit_ht16k33` and `adafruit_rgb_display` are pip packages in
   `firmware/pi/requirements.txt` and must **not** be copied into
   `CIRCUITPY/lib/`.
6. Unplug and replug the board, or press `RESET`. A power cycle is required for
   `boot.py` to take effect; a soft reload is not enough.

`firmware/kb2040/README.md` has the full pin table and a terminal bench check
that needs no Pi.

---

## 6. Setting up the Raspberry Pi

Raspberry Pi OS Bookworm, 64 bit, with the user `pi`.

### 6.1 Buses and groups

```bash
sudo raspi-config nonint do_i2c 0        # enable I2C  (logic displays)
sudo raspi-config nonint do_spi 0        # enable SPI  (radar eye)
sudo usermod -aG dialout,i2c,spi,gpio,audio pi
sudo reboot
```

After the reboot, confirm the displays answer:

```bash
i2cdetect -y 1        # expect 70, 71, 72, 73, and 48 if the ADS1115 is fitted
ls /dev/spidev0.*     # expect /dev/spidev0.0 and /dev/spidev0.1
```

### 6.2 Code and dependencies

```bash
git clone <this repository> /home/pi/fable-r2d2
cd /home/pi/fable-r2d2
python3 -m venv --system-site-packages /home/pi/r2d2-venv
/home/pi/r2d2-venv/bin/pip install -r firmware/pi/requirements.txt
```

Check the parts that matter:

```bash
/home/pi/r2d2-venv/bin/python -c "import aiohttp, serial; print('core ok')"
/home/pi/r2d2-venv/bin/python -c "from adafruit_rgb_display import gc9a01a; print('radar ok')"
/home/pi/r2d2-venv/bin/python -c "from adafruit_ht16k33.matrix import Matrix8x8; print('logic ok')"
which aplay
```

Anything missing here only disables that one feature: the server logs the exact
reason and the pip command that fixes it, then carries on.

### 6.3 Controller port

With the KB2040 plugged in:

```bash
ls -l /dev/ttyACM*    # ACM0 is the REPL console, ACM1 is the data endpoint
```

`serial_link.find_port()` picks the data endpoint on its own. To pin it, set
`R2D2_SERIAL_PORT=/dev/ttyACM1` in the systemd unit.

### 6.4 Sound

The clips are committed, so nothing needs generating on the Pi. To rebuild them:

```bash
/home/pi/r2d2-venv/bin/python scripts/generate_audio.py
```

Pick the output device with `sudo raspi-config` (System Options, Audio) and test
with `aplay firmware/pi/sounds/greet.wav`.

### 6.5 Wi-Fi access point named `R2-FABLE`

Bookworm uses NetworkManager, so one command creates the hotspot. Replace the
password with your own; it must be at least eight characters.

```bash
sudo nmcli device wifi hotspot ifname wlan0 ssid R2-FABLE password <your-password>
sudo nmcli connection modify Hotspot connection.autoconnect yes \
                              connection.autoconnect-priority 100
sudo nmcli connection modify Hotspot ipv4.method shared ipv4.addresses 192.168.4.1/24
sudo nmcli connection up Hotspot
```

The phone then joins `R2-FABLE` and opens **http://192.168.4.1:8080/**.

`hostapd` is not needed on Bookworm. If you are on an older image that does not
have NetworkManager, install `hostapd` and `dnsmasq` instead and give `wlan0`
the static address `192.168.4.1/24`.

### 6.6 Service

```bash
sudo cp firmware/pi/r2d2.service /etc/systemd/system/r2d2.service
sudo systemctl daemon-reload
sudo systemctl enable --now r2d2.service
systemctl status r2d2.service
journalctl -u r2d2.service -f
```

The unit runs as `pi`, restarts on failure at most five times a minute, and is
stopped with `SIGINT` so the aiohttp cleanup handlers stop the motors, drop the
enable line and blank the displays before the process exits.

To run it by hand instead:

```bash
/home/pi/r2d2-venv/bin/python firmware/pi/server.py --host 0.0.0.0 --port 8080
```

Useful switches: `--serial-port`, `--no-displays`, `--no-battery`,
`--log-level DEBUG`.

---

## 7. Using the control page

Open **http://192.168.4.1:8080/** on a phone.

1. Tick **Motors armed**. That sends `E 1` and arms the motors in firmware.
   Nothing moves, and no stance change starts, until it is ticked.
2. Drag the round joystick. Forward is up; the knob returns to centre and the
   robot stops when you lift your finger.
3. **Speed cap** limits every channel; 60 % is the default and is sensible
   indoors.
4. **Spin left / Spin right** turn the dome while held. **Nudge** turns it for
   200 ms.
5. The dome light buttons set all 17 pixels; the sound buttons are built from
   whatever the Pi actually found in `firmware/pi/sounds`.
6. The red **STOP** bar is always on screen. It zeroes the drive, sends `S` and
   un-arms the motors.

7. **Stance** (revision D). The panel shows the state, the phase, the actuator
   stroke, both locks and the KB2040 pack voltage. **Hold: two feet** and **Hold:
   three feet** are hold-to-run: keep a finger on the button until the state reads
   `Two feet` or `Three feet`. Letting go, locking the phone or losing Wi-Fi for
   0.5 s stops the actuator and holds the robot where it is; press again to finish.
   A button is greyed out, with the reason printed below it, whenever the
   interlock forbids that change.
8. The joystick is greyed out except on three feet with both locks seated; the
   dome buttons except on two or three feet.
9. A fault shows in red with its name (for example `Fault STALL: actuator
   stalled`). Fix the cause, then press **Clear fault**. The clear is refused while
   the sensors still disagree, and a cleared change never restarts by itself.

The header shows link state and, when an ADS1115 is fitted, pack voltage and a
rough state of charge.

---

## 8. Sound clips

Twelve original synthesized clips, 22.05 kHz, 16 bit, mono, built by
`scripts/generate_audio.py` from swept oscillators and envelopes — nothing is
sampled or copied. `audio/catalog.csv` records `name, file, seconds, sha256` for
each.

| Clip | Seconds | Character |
| ---- | ------- | --------- |
| `greet` | 0.550 | rising three note hello |
| `acknowledge` | 0.195 | flat double blip |
| `alarm` | 0.720 | two tone klaxon over a growl |
| `question` | 0.410 | blip then a long rise |
| `sad` | 0.850 | slow descending wobble |
| `happy` | 0.490 | ascending arpeggio with a flourish |
| `scan` | 1.000 | five sonar sweeps |
| `whistle-up` | 0.400 | clean rising whistle |
| `whistle-down` | 0.400 | clean falling whistle |
| `chirp-double` | 0.160 | two quick up-chirps |
| `power-on` | 1.000 | long rise settling into a warble |
| `power-off` | 0.850 | everything winding down |

Regenerating is deterministic: the same script produces byte-identical files and
the same hashes.

---

## 9. Verification run on 2026-09-12

Windows 11, Python 3.14.0, Node v24.11.1, from `C:/dev/robots/fable-r2d2`. No
hardware was connected and no network service was started; the tests are
hardware-free by construction.

### 9.1 Byte-compile every Python file

```
$ python -m py_compile firmware/kb2040/boot.py firmware/kb2040/code.py \
    firmware/kb2040/protocol.py firmware/kb2040/test_protocol.py \
    firmware/pi/audio.py firmware/pi/battery.py firmware/pi/displays.py \
    firmware/pi/mixing.py firmware/pi/serial_link.py firmware/pi/server.py \
    firmware/pi/test_mixing.py scripts/generate_audio.py
exit 0
```

### 9.2 KB2040 protocol tests

```
$ python firmware/kb2040/test_protocol.py
----------------------------------------------------------------------
Ran 47 tests in 0.001s

OK
```

Covers the command parser (every verb, arity errors, non-numeric values, clamping,
pixel index bounds), `split_lines` with CR and LF, the ramp (limit, no overshoot,
50 ticks for a full reversal), the duty maths for all four DRV8833 states, the
RP2040 slice arithmetic including the assertion that the seven chosen PWM pins do
not clash and the fourteen input pins do, the `ok`/`err`/`st` formatters, and
`DriveState`.

### 9.3 Pi mixing tests

```
$ python firmware/pi/test_mixing.py
----------------------------------------------------------------------
Ran 44 tests in 0.005s

OK
```

Covers `clamp`, the differential mix (straight, reverse, spin, arc, mirrored
turns, custom turn gain, input and output clamping), the deadband, the speed cap,
the minimum duty, permille conversion and rounding, both swept-grid invariants
(no channel ever leaves ±1000; a moving channel is never below the minimum duty),
head duty, the ramp, `format_drive` and `parse_status`.

### 9.4 Browser script

```
$ node --check firmware/pi/static/app.js
exit 0
```

### 9.5 Sound generation

```
$ python scripts/generate_audio.py
greet           0.550 s  C:\dev\robots\fable-r2d2\firmware\pi\sounds\greet.wav
acknowledge     0.195 s  C:\dev\robots\fable-r2d2\firmware\pi\sounds\acknowledge.wav
alarm           0.720 s  C:\dev\robots\fable-r2d2\firmware\pi\sounds\alarm.wav
question        0.410 s  C:\dev\robots\fable-r2d2\firmware\pi\sounds\question.wav
sad             0.850 s  C:\dev\robots\fable-r2d2\firmware\pi\sounds\sad.wav
happy           0.490 s  C:\dev\robots\fable-r2d2\firmware\pi\sounds\happy.wav
scan            1.000 s  C:\dev\robots\fable-r2d2\firmware\pi\sounds\scan.wav
whistle-up      0.400 s  C:\dev\robots\fable-r2d2\firmware\pi\sounds\whistle-up.wav
whistle-down    0.400 s  C:\dev\robots\fable-r2d2\firmware\pi\sounds\whistle-down.wav
chirp-double    0.160 s  C:\dev\robots\fable-r2d2\firmware\pi\sounds\chirp-double.wav
power-on        1.000 s  C:\dev\robots\fable-r2d2\firmware\pi\sounds\power-on.wav
power-off       0.850 s  C:\dev\robots\fable-r2d2\firmware\pi\sounds\power-off.wav
wrote 12 clips, 7.03 s total, catalogue C:\dev\robots\fable-r2d2\audio\catalog.csv
```

### 9.6 In-process smoke test

A throwaway script (kept out of the repository) built a `Robot` on stub
link/player/battery objects and drove `server.handle_message` directly — no
sockets, no threads, no hardware:

```
wav+catalog OK: 12 clips, 22050 Hz mono 16 bit, sha256 match
audio.load_catalogue OK: acknowledge, alarm, chirp-double, greet, happy,
  power-off, power-on, question, sad, scan, whistle-down, whistle-up
server message handling OK: drive/cap/head/nudge/lights/sound/stop/watchdog
ramp implementations agree across kb2040 and pi
```

It confirmed every catalogue hash against the file on disk, that the twelve WAVs
are 22050 Hz mono 16 bit, that `drive` at full forward produces `600 600 600` at
the default cap and `1000 1000 1000` at a cap of 1.0, that a full spin at a cap
of 1.0 produces `700 -700 0`, that head spin and nudge reach the head channel, that a malformed
message is logged and ignored rather than raising, that the 500 ms client
watchdog zeroes the drive, and that `mixing.ramp_step` and `protocol.ramp_step`
agree for every sampled pair.

### 9.7 Four-backpack logic display change, re-verified 2026-09-12

`displays.py` was changed from three 8x16 matrices to four 0.8 inch 8x8 mini
matrix backpacks (`Matrix8x8`): front `0x70` upper and `0x71` lower as
independent animations, rear `0x72` left and `0x73` right as one 16x8 scrolling
strip.

```
$ python -m py_compile firmware/pi/displays.py firmware/pi/test_mixing.py
exit 0
$ python firmware/pi/test_mixing.py
----------------------------------------------------------------------
Ran 44 tests in 0.005s

OK
$ python firmware/kb2040/test_protocol.py
----------------------------------------------------------------------
Ran 47 tests in 0.001s

OK
$ node --check firmware/pi/static/app.js
exit 0
```

A headless animation check (throwaway script, fake matrix objects that assert
every coordinate is inside 8x8, no I2C):

```
addresses: front 0x70 upper / 0x71 lower, rear 0x72 left / 0x73 right, 8x8 each
front windows: 400 frames each, bars in range, patterns differ in 400/400 frames
rear strip: 400 frames, 16-wide pattern scrolled coherently in 309/400 frames
degradation: rear 0x73 dropped, strip survived on 0x72, then both dropped;
  front window dropped
```

The two front windows never produced the same pattern in 400 frames. The rear
strip's 16 column pattern shifted as a whole in 309 of 400 frames; the other 91
are the deliberate single-column flicker that keeps the strip from looking like
a conveyor belt. Degradation was exercised by making a fake backpack raise
`OSError`: the strip dropped `0x73` and kept scrolling on `0x72` alone, reported
itself finished only when both were gone, and a front window dropped itself the
same way.

### 9.8 What is *not* verified

No motor has turned, no pixel has lit, no display has been written and no audio
has been played: there is no hardware on this machine. Everything above is a
syntax check, a unit test, or an in-process test of hardware-free logic. The
first real checks are the terminal bench check in
`firmware/kb2040/README.md` and `aplay firmware/pi/sounds/greet.wav` on the Pi.

### 9.9 Revision D stance controls, verified 2026-09-12

Same machine. No hardware was connected: every result below is a host test on
simulated hardware.

```
$ python -m unittest discover -s firmware/kb2040
Ran 119 tests in 0.621s
OK
$ python -m unittest discover -s firmware/pi
Ran 66 tests in 0.046s
OK
$ python scripts/electronics.py
PASS: 5 SVG sheets parse, wiring.csv has 184 wires, all 20 KB2040 signal pins match firmware/kb2040/code.py, and the RP2040 PWM/ADC plan is legal
$ python -c "import sys; sys.path.insert(0, 'scripts'); import verify; verify.check_wiring(); verify.check_firmware()"
PASS wiring: 184 wires; KB2040 pins in wiring not in code.py: []
PASS firmware: firmware/kb2040: Ran 119 tests in 0.619s, exit 0; firmware/pi: Ran 66 tests in 0.046s, exit 0; app.js syntax OK
```

The original 47 KB2040 and 44 Pi tests are unchanged and still pass inside those
totals. The new tests run the real `Supervisor` and `Stance` against a plant with
a non-backdrivable actuator and two spring pins, each with a tilt-0 and a tilt-18
receiver, through the real serial protocol. They cover: both transitions end to
end with every phase; Pi-to-KB2040 heartbeat loss in LIFT, TILT and UNLOCKING;
phone-to-Pi loss through the Pi lease, end to end; battery undervoltage and pot
open-circuit (low and high); actuator stall, TILT timeout and LOWER timeout; pins
that will not leave or will not enter a receiver; a lock switch with both contacts
open or both closed, one lock not seated at a parked endpoint, a seated reading
between receivers, and a lock released while lifting; drive and dome refused
during a change, on two feet, and in fault and unknown states; fault latch, clear
refused while inconsistent, and no restart without a fresh press; the KB2040 pin
plan; and the centre-foot feed (wheel speed within 5 % of the CAD rolling travel
over each tilt, backward on retract and forward on deploy, zero while the foot is
in the air, after a hold, and after a stall).

Not verified: nothing here has driven an actuator, moved a servo or read a real
switch. The mechanism constants come from the stance-mechanism CAD values of
2026-09-12; the pot calibration, servo pulses and creep duty are commissioning
values (section 11.4).

---

## 10. Troubleshooting

| Symptom | Cause and fix |
| ------- | ------------- |
| Page loads, nothing moves | **Motors armed** is unticked, or the pack switch is off. The header pill shows `controller ok` only when `st` lines are arriving. |
| `no controller` in the header | KB2040 unplugged, or `boot.py` missing so there is no data endpoint. Check `ls /dev/ttyACM*`; the serial worker retries every 2 s on its own. |
| `err heartbeat timeout` in the journal | The 20 Hz stream stopped — the server was paused, or USB dropped. The motors coast, which is the intended behaviour. |
| One motor runs backwards | Swap its two leads at the DRV8833 output, or set its `invert` flag in the `MOTORS` table in `code.py`. See section 4. |
| Motors buzz but do not turn | The minimum duty is too low for that gearbox under load, or the pack is flat. Raise the speed cap first; `MIN_DUTY` in `mixing.py` is the floor. |
| Robot veers on a straight run | Adjust `TURN_GAIN` in `mixing.py`, or check for a slipping wheel. Both motors in a foot always get the same value, so a difference is mechanical. |
| A logic window is blank | `i2cdetect -y 1` should show `70`, `71`, `72`, `73`. The server logs the address that did not answer and keeps the others running. Check that backpack's `A0`/`A1` address jumpers. |
| Half the rear strip is blank | One rear backpack is missing or mis-addressed. `0x72` is the left half and `0x73` the right half seen from behind; the surviving half keeps scrolling. |
| Radar eye blank | SPI not enabled, or `adafruit_rgb_display` too old to contain `gc9a01a`. The startup log names the exact reason. |
| `battery --` in the header | No ADS1115 fitted at `0x48` on the Pi's I2C-1, or the library is absent. Optional; the rest runs normally. The KB2040 is not involved. |
| No sound | `aplay` missing and pygame absent. `which aplay`; the startup log says which back end was chosen. |
| Dome pixels ignore `L` and `P` | `neopixel.mpy` not in `CIRCUITPY/lib/`. The board answers `err neopixel library missing`. |
| Joystick greyed out | The robot is not on three feet with both locks seated, or no fresh `ss` status. The stance panel says which. |
| Stance button greyed out | The reason is printed under the buttons: not armed, wheels still moving, cooling down, fault latched, or already there. |
| `Fault FEEDBACK` | Actuator pot wiper outside 40-3000 mV: check the purple wire to A0, R7 and R8. |
| `Fault LOCK_SENSOR` | A lock switch reads NO and NC both open or both closed for 150 ms: a broken or shorted wire. |
| `Fault LOCK_DISAGREES` or `LOCK_TIMEOUT` | A pin is not where the stroke says it must be. Check the pin, the servo pull and the switch lever before clearing. |
| `Fault STALL` or `TRAVEL_TIMEOUT` | The actuator did not move 0.3 mm in 1 s, or a phase took too long. Check for a jam, the 12 V branch fuse F7 and the DRV8871 limit resistor R5. |
| `Fault REVERSED_FEEDBACK` | The actuator moves opposite to its command: swap its red and black leads at U10. |
| `stance request ignored` notice | The phone lost the hold for 0.5 s. Lift your finger and press again. |

---

## 11. Revision D stance change

### 11.1 Mechanism, as the firmware models it

A 12 V Actuonix P16-100-256-12-P, parallel to the centre-leg guide, sets the
stroke `s` (mm from fully closed): **5.0 mm** two feet (wheels 25 mm up, tilt 0),
**31.6 mm** centre-foot touchdown (tilt still 0), **65.1 mm** three feet (tilt 18
deg; hard mechanical stop at 68.0 mm). Two shoulder locks, left and right, each have a spring-return pin in the body
and two receivers in the leg: tilt 0 (seated for every `s` up to touchdown) and tilt
18. An MG995 servo per lock pulls its pin; an Omron SS-01GL per lock, wired NO + NC,
reads "seated". The lock state comes only from those switches. All values live in
the `MECHANISM CONSTANTS` block of `firmware/kb2040/stance.py`.

### 11.2 States and phases

| State | Meaning | Ground drive | Dome |
| ----- | ------- | ------------ | ---- |
| `THREE_FOOT` | at 65.1 mm, both locks seated | allowed | allowed |
| `TWO_FOOT` | at 5.0 mm, both locks seated, stationary | refused | allowed |
| `RETRACTING` / `DEPLOYING` | a change in progress | refused | refused |
| `HELD` | stopped between stances, or not yet confirmed | refused | refused |
| `FAULT` | latched; needs `C` | refused | refused |

Retract: `UNLOCKING` (actuator stopped, both releases pulled, wait until neither
switch reads seated) -> `TILT` (full duty toward 32.8 mm; the releases drop once
`s` <= 45.9 mm so the pins ride the ring face) -> `LOCKING` (150 ms settle, then a
20 % creep through 31.6 mm until both switches read seated) -> `LIFT` (both locks
must stay seated, full duty to 5.0 mm) -> `TWO_FOOT`.

Deploy: `LOWER` (locked, to 31.6 mm) -> `UNLOCKING` -> `TILT` (releases held until
`s` >= 38.7 mm) -> `LOCKING` (creep through 65.1 mm) -> `THREE_FOOT`.

**Centre-foot feed.** Between touchdown and three feet the centre foot rolls on the
floor: 124.9 mm of travel over the 33.5 mm tilt stroke, 10.3 mm per mm of stroke
just past touchdown and 2.4 mm per mm at three feet (table `CENTRE_FOOT_TRAVEL`,
from the CAD kinematics). The mechanism force check assumes almost no floor drag,
so during `TILT` and `LOCKING` the KB2040 drives the centre-foot motors at
`dy/ds x measured actuator speed`, forward while deploying and backward while
retracting, and stops them at once whenever the actuator stops. The operator's
centre channel stays refused; the feed is reported in the `st` line.

### 11.3 Interlocks and faults

* A start needs: no fault, battery healthy, the Pi heartbeat, `E 1`, wheels and
  dome stopped, a fresh press (released since the last stop), and the actuator
  cooldown (4 ms rest per ms of travel, the P16's 20 % duty).
* Hold-to-run. Any of these stops the actuator and holds, leaving the releases as
  they were: the control released, the phone silent for 0.5 s (the Pi lease), the
  Pi silent for 0.5 s (the KB2040 heartbeat), `S`, `E 0`, a reversed request, or a
  drive or dome command. Nothing restarts without a fresh press; after a phone
  lease lapse the Pi also ignores the button until the page releases it.
* Latched faults, each stopping the actuator: `POWER` (battery below 11.2 V for
  500 ms during a change), `FEEDBACK` (wiper outside 40-3000 mV), `LOCK_SENSOR` (a
  switch with NO and NC both open or both closed for 150 ms), `LOCK_DISAGREES` (foot
  raised without both locks seated, a lock seated between receivers, a parked
  stance without both locks, or a lock released while lifting), `LOCK_TIMEOUT`
  (pins not out within 400 ms, or not seated 3 s after the creep), `STALL` (under
  0.3 mm in 1 s while driven), `TRAVEL_TIMEOUT` (LIFT/LOWER 16 s, TILT/LOCKING 21 s),
  `DRIFT`, `OVERTRAVEL` (beyond 3.5 or 66.6 mm), `REVERSED_FEEDBACK`.
* `C` succeeds only when fresh sensors are consistent, and the stance control must
  still be released and pressed again.

### 11.4 Commissioning values to measure before the first powered change

1. Detach the actuator and measure the wiper at both ends of travel; set
   `POT_ZERO_MV` and `POT_FULL_MV` (the pot tolerance is +/-50 %).
2. Calibrate `RELEASE_US` per side on the built lock (nominal 16.3 deg, 1321 us left
   and 1679 us right): 5.8 mm of pin pull with no servo stall; keep `ENGAGE_US` with
   the horn parked 1 mm clear of the knob. The release force needs the servo's 6.0 V
   rating: measure rail B at the servo plug under the pull.
3. Check each SS-01GL at 3.3 V and 1 mA (below Omron's 5 V 1 mA reference load):
   `ss` must read `EE` seated and `RR` pulled, and `X` with either wire unplugged.
4. With the wheels off the floor, time one creep through each receiver. If a pin
   does not catch, lower `SEEK_DUTY_PERCENT`; if the creep trips `STALL`, raise it.
5. Centre-foot feed. The kinematic command is only 12-75 permille (1.2-7.5 % duty),
   below the 15 % minimum duty at which a TT gearbox reliably turns (`mixing.MIN_DUTY`).
   On a real floor, watch the centre wheels during a deploy: if they do not roll,
   the foot is dragged and the force check assumption is not met. Trim
   `CENTRE_FEED_GAIN`, or stop and revisit the mechanism, before regular use.
