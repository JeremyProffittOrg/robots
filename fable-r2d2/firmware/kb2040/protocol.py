"""Hardware-free protocol, ramp and duty maths for the fable-r2d2 KB2040 firmware.

This module contains no CircuitPython imports so that it can be exercised by
CPython on a workstation (see ``test_protocol.py``).  ``code.py`` imports it on
the microcontroller and supplies the hardware.

Line protocol (ASCII, newline terminated, 115200 8N1 over USB CDC data):

    Pi  -> KB2040   "M <l> <r> <c> <h>"  drive permille, -1000..1000
                    "L <r> <g> <b>"      all 17 pixels
                    "P <i> <r> <g> <b>"  one pixel, i = 0..16
                    "E <0|1>"            DRV8833 nSLEEP enable
                    "S"                  stop (coast all, targets zeroed, stance held)
                    "?"                  status request
                    "T <0|2|3>"          stance request, hold-to-run: 2 two-foot,
                                         3 three-foot, 0 none.  Sent every 50 ms
                                         while the operator holds the control; a
                                         request older than HEARTBEAT_MS is none.
                    "C"                  clear a latched stance fault
    KB2040 -> Pi    "ok"
                    "st <enabled> <l> <r> <c> <h> <index>"
                    "ss <state> <phase> <fault> <pos_0.1mm> <lock> <pack_mv>
                        <drive_ok> <head_ok> <can_two> <can_three>
                        <reason>|<two_foot_block>|<three_foot_block>"
                    "err <text>"

``ss`` fields: ``pos_0.1mm`` and ``pack_mv`` are integers, -1 when invalid;
``lock`` is E (seated), R (released), X (NO/NC invalid) or W (not settled); the
four flags are 0/1; the trailing text holds three ``|`` separated strings.
"""

MAX_PERMILLE = 1000
"""Largest magnitude accepted for a motor channel."""

RAMP_STEP = 40
"""Maximum permille change applied to one channel per tick."""

TICK_MS = 10
"""Control tick period in milliseconds."""

HEARTBEAT_MS = 500
"""Motors coast if no command is received for this many milliseconds."""

PIXEL_COUNT = 17
"""Front PSI jewel (7) + rear PSI jewel (7) + three holoprojector pixels."""

FULL_DUTY = 65535
"""16 bit pwmio duty range."""

PWM_FREQUENCY = 20000
"""20 kHz, above audio and within the DRV8833 input bandwidth."""

CHANNEL_NAMES = ("left", "right", "centre", "head")

STANCE_REQUESTS = (0, 2, 3)
"""Legal ``T`` values: none, two-foot, three-foot."""

SERVO_FREQUENCY = 50
"""Release servo PWM frequency.  Its slice must carry no 20 kHz output."""

ADC_GPIOS = (26, 27, 28, 29)
"""The only RP2040 GPIOs with an ADC input (KB2040 A0-A3)."""


class CommandError(Exception):
    """Raised when an inbound line cannot be executed as written."""


def clamp(value, low, high):
    """Return ``value`` limited to the inclusive range ``low``..``high``."""
    if value < low:
        return low
    if value > high:
        return high
    return value


def parse_int(text, what):
    """Parse a signed decimal integer or raise :class:`CommandError`."""
    body = text[1:] if text[:1] in ("+", "-") else text
    if not body or not body.isdigit():
        raise CommandError("bad {0} {1}".format(what, text))
    return int(text)


def split_lines(buffer):
    """Split a text accumulation buffer into complete lines.

    Returns ``(lines, remainder)``.  ``lines`` never contains the terminator.
    Both CR and LF terminate a line so a terminal pasting CRLF still works.
    """
    lines = []
    start = 0
    for index in range(len(buffer)):
        character = buffer[index]
        if character == "\n" or character == "\r":
            piece = buffer[start:index]
            if piece:
                lines.append(piece)
            start = index + 1
    return lines, buffer[start:]


def parse_command(line):
    """Turn one protocol line into ``(kind, args)``.

    Out of range motor and colour values are clamped rather than rejected: a
    drive link that jitters must not be able to stall the motor loop.  Values
    that cannot be read as numbers, unknown verbs and bad pixel indices raise
    :class:`CommandError`, which the caller reports as ``err``.
    """
    parts = line.strip().split()
    if not parts:
        raise CommandError("empty line")
    kind = parts[0]
    args = parts[1:]

    if kind == "M":
        if len(args) != 4:
            raise CommandError("M needs 4 values, got {0}".format(len(args)))
        values = []
        for index in range(4):
            raw = parse_int(args[index], CHANNEL_NAMES[index])
            values.append(clamp(raw, -MAX_PERMILLE, MAX_PERMILLE))
        return ("M", values)

    if kind == "L":
        if len(args) != 3:
            raise CommandError("L needs 3 values, got {0}".format(len(args)))
        colour = [clamp(parse_int(args[i], "colour"), 0, 255) for i in range(3)]
        return ("L", colour)

    if kind == "P":
        if len(args) != 4:
            raise CommandError("P needs 4 values, got {0}".format(len(args)))
        index = parse_int(args[0], "pixel index")
        if index < 0 or index >= PIXEL_COUNT:
            raise CommandError(
                "pixel index {0} outside 0..{1}".format(index, PIXEL_COUNT - 1)
            )
        colour = [clamp(parse_int(args[i], "colour"), 0, 255) for i in range(1, 4)]
        return ("P", [index] + colour)

    if kind == "E":
        if len(args) != 1:
            raise CommandError("E needs 1 value, got {0}".format(len(args)))
        flag = parse_int(args[0], "enable")
        if flag != 0 and flag != 1:
            raise CommandError("enable must be 0 or 1, got {0}".format(flag))
        return ("E", [flag])

    if kind == "S":
        if args:
            raise CommandError("S takes no values")
        return ("S", [])

    if kind == "?":
        if args:
            raise CommandError("? takes no values")
        return ("?", [])

    if kind == "T":
        if len(args) != 1:
            raise CommandError("T needs 1 value, got {0}".format(len(args)))
        target = parse_int(args[0], "stance")
        if target not in STANCE_REQUESTS:
            raise CommandError("stance must be 0, 2 or 3, got {0}".format(target))
        return ("T", [target])

    if kind == "C":
        if args:
            raise CommandError("C takes no values")
        return ("C", [])

    raise CommandError("unknown command {0}".format(kind))


def ramp_step(current, target, max_step=RAMP_STEP):
    """Move ``current`` towards ``target`` by at most ``max_step``.

    Called once per :data:`TICK_MS` tick, so a full -1000 to 1000 reversal takes
    50 ticks (500 ms) and the DRV8833 never sees a step change of duty.
    """
    if max_step <= 0:
        raise ValueError("max_step must be positive")
    difference = target - current
    if difference > max_step:
        return current + max_step
    if difference < -max_step:
        return current - max_step
    return target


def outputs_for_permille(permille, invert=False):
    """Return ``(digital_high, pwm_duty)`` for one motor channel.

    Each motor is driven with one PWM pin and one plain digital pin; see
    ``README.md`` for why (RP2040 PWM slices are shared between GPIOs 16 apart,
    so 14 simultaneous PWM outputs are not available on this pin map).

    DRV8833 truth table, with ``dig`` the digital pin and ``pwm`` the other:

    ===========  ==========  ==============================================
    dig / pwm    result      used for
    ===========  ==========  ==============================================
    1 / 0        forward     forward, pwm duty = FULL * (1 - m), slow decay
    0 / 1        reverse     reverse, pwm duty = FULL * m, fast decay
    1 / 1        brake       :func:`outputs_for_brake`
    0 / 0        coast       permille == 0
    ===========  ==========  ==============================================
    """
    value = clamp(int(permille), -MAX_PERMILLE, MAX_PERMILLE)
    if invert:
        value = -value
    if value == 0:
        return (False, 0)
    if value > 0:
        magnitude = (FULL_DUTY * value) // MAX_PERMILLE
        return (True, FULL_DUTY - magnitude)
    magnitude = (FULL_DUTY * (-value)) // MAX_PERMILLE
    return (False, magnitude)


def outputs_for_brake():
    """Return ``(digital_high, pwm_duty)`` that shorts the motor (both inputs high)."""
    return (True, FULL_DUTY)


def outputs_for_coast():
    """Return ``(digital_high, pwm_duty)`` that releases the motor (both inputs low)."""
    return (False, 0)


def pwm_slice(gpio):
    """Return the RP2040 PWM slice number driving ``gpio``."""
    return (gpio >> 1) & 7


def pwm_channel(gpio):
    """Return ``B`` or ``A``, the RP2040 PWM channel driving ``gpio``."""
    return "B" if gpio & 1 else "A"


def pwm_conflicts(gpios):
    """Return a sorted list of ``(gpio_a, gpio_b)`` pairs that cannot both be PWM.

    Two RP2040 GPIOs share one PWM output whenever they have the same slice and
    the same channel, which happens for every pair 16 apart (and 32 apart).  An
    empty list means the supplied set can be allocated with ``pwmio`` at once.
    """
    seen = {}
    clashes = []
    for gpio in gpios:
        key = (pwm_slice(gpio), pwm_channel(gpio))
        if key in seen:
            clashes.append((seen[key], gpio))
        else:
            seen[key] = gpio
    clashes.sort()
    return clashes


def pwm_frequency_conflicts(outputs):
    """Return sorted ``(gpio_a, gpio_b)`` pairs on one slice at different frequencies.

    ``outputs`` is a list of ``(gpio, frequency_hz)``.  Both channels of an
    RP2040 PWM slice share one counter, so the servo at 50 Hz cannot sit on a
    slice whose other channel runs a motor at 20 kHz.
    """
    by_slice = {}
    clashes = []
    for gpio, frequency in outputs:
        key = pwm_slice(gpio)
        if key in by_slice and by_slice[key][1] != frequency:
            clashes.append((by_slice[key][0], gpio))
        elif key not in by_slice:
            by_slice[key] = (gpio, frequency)
    clashes.sort()
    return clashes


def format_stance(state, phase, fault, position_mm, lock, pack_mv, drive_ok, head_ok,
                  can_two, can_three, reason, two_block, three_block):
    """Stance status line, terminator included.  See the module docstring."""
    texts = []
    for text in (reason, two_block, three_block):
        texts.append((text or "").replace("|", "/").replace("\n", " ").replace("\r", " "))
    return "ss {0} {1} {2} {3} {4} {5} {6} {7} {8} {9} {10}\n".format(
        state,
        phase,
        fault,
        -1 if position_mm is None else int(round(position_mm * 10)),
        lock,
        -1 if pack_mv is None else int(round(pack_mv)),
        1 if drive_ok else 0,
        1 if head_ok else 0,
        1 if can_two else 0,
        1 if can_three else 0,
        "|".join(texts),
    )


def format_ok():
    """Acknowledgement line, terminator included."""
    return "ok\n"


def format_error(text):
    """Error line, terminator included."""
    return "err {0}\n".format(text)


def format_status(enabled, left, right, centre, head, index):
    """Status line, terminator included.

    ``enabled`` and ``index`` are reported as 0/1, the four channels as the
    current (post ramp) permille actually being applied to the motors.
    """
    return "st {0} {1} {2} {3} {4} {5}\n".format(
        1 if enabled else 0,
        int(left),
        int(right),
        int(centre),
        int(head),
        1 if index else 0,
    )


class DriveState:
    """Ramped targets for the four logical drive channels.

    ``left``, ``right`` and ``centre`` each feed two motors; ``head`` feeds the
    single dome friction-drive motor.
    """

    def __init__(self, max_step=RAMP_STEP):
        self.max_step = max_step
        self.target = [0, 0, 0, 0]
        self.current = [0, 0, 0, 0]

    def set_targets(self, values):
        """Set the four channel targets from an ``M`` command payload."""
        if len(values) != 4:
            raise ValueError("expected 4 channel values")
        for index in range(4):
            self.target[index] = clamp(int(values[index]), -MAX_PERMILLE, MAX_PERMILLE)

    def stop(self):
        """Zero the targets.  The ramp still walks the outputs down."""
        for index in range(4):
            self.target[index] = 0

    def hard_stop(self):
        """Zero targets and outputs at once, for the heartbeat timeout."""
        for index in range(4):
            self.target[index] = 0
            self.current[index] = 0

    def tick(self):
        """Advance every channel one ramp step and return the new currents."""
        for index in range(4):
            self.current[index] = ramp_step(
                self.current[index], self.target[index], self.max_step
            )
        return list(self.current)

    def is_moving(self):
        """True while any channel output is non-zero."""
        for value in self.current:
            if value != 0:
                return True
        return False
