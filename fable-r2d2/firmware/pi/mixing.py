"""Drive mixing for the fable-r2d2 Raspberry Pi control server.

Pure arithmetic with no imports outside the standard library, so it is testable
on any machine (see ``test_mixing.py``) and can be reasoned about without the
robot present.

The robot has three driven feet.  The left and right feet each hold two Adafruit
3777 TT motors on fixed axles; the centre foot holds two more on a vertical
caster pivot, so it follows the turn instead of scrubbing.  Differential drive
therefore needs three channel values:

    left   = y + x * turn_gain
    right  = y - x * turn_gain
    centre = y

``x`` and ``y`` arrive from the touch joystick in the browser, each -1..1, with
``y`` positive forward and ``x`` positive to the right.  Every channel is then
clamped, scaled by the global speed cap, and pushed up to the minimum duty that
actually breaks the gearbox stiction.
"""

import math

MAX_PERMILLE = 1000
"""Permille value sent to the KB2040 for full duty."""

TURN_GAIN = 0.70
"""How much of the joystick x axis is added to and taken from the forward term."""

SPEED_CAP_DEFAULT = 0.60
"""Default global speed cap: 60 percent of full duty."""

SPEED_CAP_MIN = 0.20
"""Lowest cap the web page slider may select."""

SPEED_CAP_MAX = 1.00
"""Highest cap the web page slider may select."""

MIN_DUTY = 0.15
"""A moving channel is never driven below 15 percent of full duty."""

DEADBAND = 0.05
"""Channel magnitudes at or below this count as stopped."""

HEAD_DUTY_DEFAULT = 0.45
"""Default duty for the dome friction-drive motor."""

HEAD_NUDGE_SECONDS = 0.20
"""Length of a head nudge."""

COMMAND_HZ = 20
"""Drive commands per second sent to the KB2040."""

COMMAND_PERIOD = 1.0 / COMMAND_HZ
"""Seconds between drive commands."""

RAMP_PER_COMMAND = 200
"""Permille of change allowed per 50 ms command.

The KB2040 ramps at 40 permille per 10 ms tick, which is the same rate.  The Pi
applies the identical limit so the value it reports is the value the motors are
actually being given, rather than a target the controller has not reached.
"""


def clamp(value, low, high):
    """Return ``value`` limited to the inclusive range ``low``..``high``."""
    if value < low:
        return low
    if value > high:
        return high
    return value


def mix(x, y, turn_gain=TURN_GAIN):
    """Return the raw ``(left, right, centre)`` channel values, each clamped to -1..1.

    ``x`` and ``y`` are clamped on the way in, so a browser that sends 3.0
    cannot produce a value outside the range.
    """
    x = clamp(float(x), -1.0, 1.0)
    y = clamp(float(y), -1.0, 1.0)
    left = clamp(y + x * turn_gain, -1.0, 1.0)
    right = clamp(y - x * turn_gain, -1.0, 1.0)
    centre = clamp(y, -1.0, 1.0)
    return (left, right, centre)


def apply_limits(value, speed_cap=SPEED_CAP_DEFAULT, min_duty=MIN_DUTY, deadband=DEADBAND):
    """Apply the deadband, the speed cap and the minimum duty to one channel.

    Order matters and follows the control specification: anything inside the
    deadband is stopped, what is left is scaled by the cap, and a channel that
    is still moving is raised to ``min_duty`` of full duty so the gearbox
    actually turns instead of buzzing.
    """
    value = clamp(float(value), -1.0, 1.0)
    if abs(value) <= deadband:
        return 0.0
    speed_cap = clamp(float(speed_cap), SPEED_CAP_MIN, SPEED_CAP_MAX)
    scaled = value * speed_cap
    magnitude = abs(scaled)
    if magnitude < min_duty:
        magnitude = min_duty
    if magnitude > 1.0:
        magnitude = 1.0
    return math.copysign(magnitude, scaled)


def to_permille(value):
    """Convert a -1..1 duty fraction to the integer permille the KB2040 expects."""
    return int(round(clamp(float(value), -1.0, 1.0) * MAX_PERMILLE))


def drive_permille(
    x,
    y,
    speed_cap=SPEED_CAP_DEFAULT,
    turn_gain=TURN_GAIN,
    min_duty=MIN_DUTY,
    deadband=DEADBAND,
):
    """Return ``(left, right, centre)`` permille for one joystick position."""
    channels = mix(x, y, turn_gain)
    return tuple(
        to_permille(apply_limits(channel, speed_cap, min_duty, deadband))
        for channel in channels
    )


def head_permille(direction, duty=HEAD_DUTY_DEFAULT, min_duty=MIN_DUTY):
    """Return the head motor permille for a spin direction.

    ``direction`` is -1 (anticlockwise), 0 (stop) or +1 (clockwise); anything
    else is treated by its sign.  ``duty`` is the fraction of full duty chosen
    on the web page, raised to ``min_duty`` so the friction wheel does not stall
    against the dome ring.
    """
    if direction == 0:
        return 0
    magnitude = clamp(abs(float(duty)), 0.0, 1.0)
    if magnitude < min_duty:
        magnitude = min_duty
    sign = 1.0 if direction > 0 else -1.0
    return to_permille(sign * magnitude)


def ramp_step(current, target, max_step=RAMP_PER_COMMAND):
    """Move ``current`` towards ``target`` by at most ``max_step`` permille."""
    if max_step <= 0:
        raise ValueError("max_step must be positive")
    difference = target - current
    if difference > max_step:
        return current + max_step
    if difference < -max_step:
        return current - max_step
    return target


def ramp_channels(current, target, max_step=RAMP_PER_COMMAND):
    """Ramp a four channel list ``[left, right, centre, head]`` towards ``target``."""
    if len(current) != len(target):
        raise ValueError("current and target must be the same length")
    return [ramp_step(current[i], target[i], max_step) for i in range(len(current))]


def format_drive(left, right, centre, head):
    """Build the ``M`` line for the KB2040, terminator included."""
    return "M {0} {1} {2} {3}\n".format(
        clamp(int(left), -MAX_PERMILLE, MAX_PERMILLE),
        clamp(int(right), -MAX_PERMILLE, MAX_PERMILLE),
        clamp(int(centre), -MAX_PERMILLE, MAX_PERMILLE),
        clamp(int(head), -MAX_PERMILLE, MAX_PERMILLE),
    )


def parse_status(line):
    """Parse a KB2040 ``st`` line into a dictionary, or return ``None``.

    ``"st 1 100 -100 0 250 0"`` becomes
    ``{"enabled": True, "left": 100, "right": -100, "centre": 0, "head": 250,
    "index": False}``.  Anything that is not a well formed status line returns
    ``None`` so the caller can log it rather than crash the reader thread.
    """
    parts = line.strip().split()
    if len(parts) != 7 or parts[0] != "st":
        return None
    try:
        numbers = [int(part) for part in parts[1:]]
    except ValueError:
        return None
    return {
        "enabled": numbers[0] == 1,
        "left": numbers[1],
        "right": numbers[2],
        "centre": numbers[3],
        "head": numbers[4],
        "index": numbers[5] == 1,
    }
