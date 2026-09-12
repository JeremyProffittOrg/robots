# fable-r2d2 firmware

Two processors, one job each.

**Adafruit KB2040** (product 5302, RP2040, CircuitPython 9) is the motor and
light controller. It drives seven Adafruit 3777 TT motors through four DRV8833
(3297) boards, drives the 17 pixel dome NeoPixel chain, reads the dome index
sensor, and coasts every motor if the Pi stops talking for 500 ms.

**Raspberry Pi 4** (Raspberry Pi OS Bookworm, 64 bit) is everything else. It
serves the phone control page over its own Wi-Fi access point, mixes the
joystick into three foot channels, streams commands to the KB2040 over USB CDC
at 20 Hz, animates the head displays, and plays the sound clips.

```
 phone browser ──WebSocket──► Pi: server.py ──USB CDC 115200──► KB2040: code.py
                                   │                                  │
                                   ├─ displays.py  HT16K33 x3, GC9A01A ├─ 7 x DRV8833 channels
                                   ├─ audio.py     aplay / pygame      └─ 17 x NeoPixel
                                   └─ battery.py   ADS1115 (optional)
```

---

## 1. Files

### KB2040 — `firmware/kb2040/`

| File | Purpose |
| ---- | ------- |
| `boot.py` | Enables the second USB CDC endpoint (the Pi's data port). |
| `code.py` | Controller: motors, pixels, index sensor, serial loop, heartbeat. |
| `protocol.py` | Hardware-free parser, ramp and duty maths. Imported by `code.py`. |
| `test_protocol.py` | CPython unit tests for `protocol.py`. Not copied to the board. |
| `README.md` | Exact copy list, bundle libraries, pin table, bench check. |

### Raspberry Pi — `firmware/pi/`

| File | Purpose |
| ---- | ------- |
| `server.py` | aiohttp server: static page, WebSocket, control state, workers. |
| `mixing.py` | Differential drive maths, clamps, speed cap, minimum duty, ramp. |
| `serial_link.py` | Background thread owning the USB CDC port; 20 Hz command stream. |
| `displays.py` | Front/rear logic matrices and the radar eye. |
| `audio.py` | WAV playback through `aplay`, or `pygame.mixer` as a fallback. |
| `battery.py` | Optional pack voltage through an ADS1115. |
| `test_mixing.py` | CPython unit tests for `mixing.py`. |
| `requirements.txt` | Pi Python dependencies. |
| `r2d2.service` | systemd unit. |
| `static/index.html`, `static/app.js`, `static/style.css` | The control page. |
| `sounds/*.wav` | Twelve generated clips, 22.05 kHz 16 bit mono. |

### Elsewhere

| File | Purpose |
| ---- | ------- |
| `scripts/generate_audio.py` | Synthesises the twelve clips and writes the catalogue. |
| `audio/catalog.csv` | `name, file, seconds, sha256` for every clip. |

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
| `E <0\|1>` | DRV8833 `SLP` line: 1 wakes the drivers, 0 sleeps them and zeroes the motors. |
| `S` | Stop: targets and outputs to zero at once. |
| `?` | Status request. |

### KB2040 to Pi

| Line | Meaning |
| ---- | ------- |
| `ok` | The previous command was executed. |
| `st <enabled> <l> <r> <c> <h> <index>` | Status. `enabled` and `index` are 0/1; the four channels are the post-ramp permille actually applied. Sent on `?` and unsolicited every 200 ms. |
| `err <text>` | The line could not be executed, or the heartbeat expired. |

### Rates and limits

* **Tick**: 10 ms on the KB2040.
* **Ramp**: at most 40 permille per tick per channel, so a full `-1000` to
  `+1000` reversal takes 50 ticks (500 ms). The Pi applies the same limit at
  200 permille per 50 ms command, so the value it reports is the value the
  motors are really being given.
* **Heartbeat**: no line for 500 ms and every motor coasts, with
  `err heartbeat timeout, motors coasted` sent once. The Pi's 20 Hz `M` stream
  is the heartbeat; it never stops while the server is up.
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
coasts the motors 500 ms later. The STOP button zeroes the drive and drops the
enable line in one press.

---

## 4. Deviation from the specified pin map, and why

The pin map is wired exactly as specified. **What changed is which of each
motor's two DRV8833 inputs carries the PWM.**

The RP2040 has eight PWM slices of two channels. GPIO *n* is hard-wired to slice
`(n >> 1) & 7`, channel `n & 1`, so any two GPIOs sixteen apart are the *same*
PWM output. Four collisions fall inside the specified map:

```
GP2 (D2, LF-front AIN1)  / GP18 (SCK, CF-rear BIN2)  -> slice 1 channel A
GP3 (D3, LF-front AIN2)  / GP19 (MOSI, CF-front AIN2)-> slice 1 channel B
GP4 (D4, LF-rear BIN1)   / GP20 (MISO, CF-rear BIN1) -> slice 2 channel A
GP10 (D10, CF-front AIN1)/ GP26 (A0, head AIN1)      -> slice 5 channel A
```

Fourteen simultaneous `pwmio.PWMOut` objects are therefore impossible on this
board. `pwmio` raises on the first colliding allocation and the firmware would
not start at all.

`code.py` gives each motor **one** PWM pin and **one** plain digital pin,
choosing the PWM pin so the seven land on seven different slice/channel pairs:
GP3, GP5, GP7, GP9, GP10, GP18, GP27. All four DRV8833 states are still
reachable, so nothing in the protocol or the behaviour changes:

| Digital pin | PWM duty | DRV8833 | Used for |
| ----------- | -------- | ------- | -------- |
| low | 0 | both low | coast |
| high | `65535 * (1 - m)` | forward | forward at magnitude `m`, slow decay |
| low | `65535 * m` | reverse | reverse at magnitude `m`, fast decay |
| high | `65535` | both high | brake |

`protocol.pwm_conflicts()` re-checks the plan at boot and `code.py` answers
`err pwm slice clash ...` if anyone edits the `MOTORS` table into a collision.
`test_protocol.py` asserts both that the seven chosen pins are clash-free and
that the fourteen input pins are not.

**Wiring consequence.** Forward uses slow decay and reverse fast decay, so a
motor is a little stronger in the slow-decay direction at equal duty. That is
the direction where the digital pin is high. Wire each motor's leads so that
direction drives the robot forward. If one runs backwards, swap its two leads at
the DRV8833 output (preferred) or set its `invert` flag in `MOTORS`.

Two smaller corrections, both verified against
`ports/raspberrypi/boards/adafruit_kb2040/pins.c`:

* On the KB2040, `board.SDA` and `board.SCL` are **GPIO 12 and 13** (the STEMMA
  QT connector), not `D2` and `D3`. Reserving the STEMMA QT bus therefore costs
  nothing; `D2` and `D3` stay free for the left foot. Every other `board` name
  in the specified map exists and is used as written.
* The round TFT driver module in `adafruit_rgb_display` is spelled **`gc9a01a`**
  with a trailing `a` (class `GC9A01A`); there is no plain `gc9a01` module in
  that library. `displays.py` imports `gc9a01a`.

---

## 5. Flashing the KB2040

1. Download CircuitPython 9.x for the KB2040 from
   <https://circuitpython.org/board/adafruit_kb2040/> — a `.uf2` file.
2. Plug the KB2040 into a computer with USB-C. Press the `BOOT` button, tap
   `RESET` while holding it, then release `BOOT`. A drive named `RPI-RP2`
   appears.
3. Copy the `.uf2` onto `RPI-RP2`. The board reboots and a drive named
   `CIRCUITPY` appears.
4. Copy `firmware/kb2040/boot.py`, `code.py` and `protocol.py` to the root of
   `CIRCUITPY`. Do **not** copy `test_protocol.py`.
5. Download the CircuitPython **9.x** library bundle from
   <https://circuitpython.org/libraries>, and copy **`neopixel.mpy`** from its
   `lib/` folder into `CIRCUITPY/lib/`. That is the only bundle file needed;
   everything else `code.py` uses is built into the firmware.
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
i2cdetect -y 1        # expect 70, 71, 72, and 48 if the ADS1115 is fitted
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
/home/pi/r2d2-venv/bin/python -c "from adafruit_ht16k33 import matrix; print('logic ok')"
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

1. Tick **Motors armed**. That sends `E 1` and wakes the four DRV8833 boards.
   Nothing moves until it is ticked.
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

### 9.7 What is *not* verified

No motor has turned, no pixel has lit, no display has been written and no audio
has been played: there is no hardware on this machine. Everything above is a
syntax check, a unit test, or an in-process test of hardware-free logic. The
first real checks are the terminal bench check in
`firmware/kb2040/README.md` and `aplay firmware/pi/sounds/greet.wav` on the Pi.

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
| Logic displays blank | `i2cdetect -y 1` should show `70`, `71`, `72`. The server logs which address did not answer. |
| Radar eye blank | SPI not enabled, or `adafruit_rgb_display` too old to contain `gc9a01a`. The startup log names the exact reason. |
| `battery --` in the header | No ADS1115 fitted, or the library is absent. Optional; the rest runs normally. |
| No sound | `aplay` missing and pygame absent. `which aplay`; the startup log says which back end was chosen. |
| Dome pixels ignore `L` and `P` | `neopixel.mpy` not in `CIRCUITPY/lib/`. The board answers `err neopixel library missing`. |
