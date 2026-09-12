"""fable-r2d2 motor and dome-light controller, Adafruit KB2040 (product 5302).

CircuitPython 9.  Copy this file, ``boot.py`` and ``protocol.py`` to CIRCUITPY,
plus ``neopixel.mpy`` from the CircuitPython 9 library bundle (see README.md).

Responsibilities
    * drive seven Adafruit 3777 TT motors through four DRV8833 (3297) boards
    * drive the 17 pixel dome NeoPixel chain
    * read the optional dome index (home) sensor
    * speak the line protocol in ``protocol.py`` over USB CDC data
    * coast every motor if no line arrives for ``protocol.HEARTBEAT_MS``

Pin map (KB2040 silkscreen name, RP2040 GPIO).  Verified against
ports/raspberrypi/boards/adafruit_kb2040/pins.c in the CircuitPython tree:

    D0=GP0  D1=GP1  D2=GP2  D3=GP3  D4=GP4  D5=GP5  D6=GP6  D7=GP7
    D8=GP8  D9=GP9  D10=GP10  SCK=GP18  MOSI=GP19  MISO=GP20
    A0=GP26  A1=GP27  A2=GP28  A3=GP29  SDA=GP12  SCL=GP13 (STEMMA QT)

One PWM pin and one plain digital pin per motor
    The RP2040 has eight PWM slices of two channels.  GPIO n uses slice
    (n >> 1) & 7, channel n & 1, so GP2/GP18, GP3/GP19, GP4/GP20 and GP10/GP26
    are the same PWM output and cannot both be PWM at once.  Fourteen
    simultaneous PWM pins are therefore impossible on this pin map.  Each motor
    instead gets PWM on one input and a digital level on the other, which still
    reaches all four DRV8833 states (forward, reverse, brake, coast); see
    ``protocol.outputs_for_permille``.  The seven PWM pins chosen below occupy
    seven different slice/channel pairs, which ``_check_pwm_plan`` re-verifies
    at boot.
"""

import time

import board
import digitalio
import pwmio
import usb_cdc

import protocol

try:
    import neopixel

    _NEOPIXEL_IMPORT_ERROR = None
except ImportError as error:  # pragma: no cover - hardware only
    neopixel = None
    _NEOPIXEL_IMPORT_ERROR = str(error)


# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------

LEFT, RIGHT, CENTRE, HEAD = 0, 1, 2, 3

# name, drive channel, PWM pin, PWM GPIO, digital pin, digital GPIO, invert.
# The PWM pin is the DRV8833 input that is modulated; the digital pin is held
# high for the motor's slow-decay direction.  Wire each motor's leads so that
# direction drives the robot forward, or set the invert flag here instead.
MOTORS = (
    ("lf-front", LEFT, board.D3, 3, board.D2, 2, False),
    ("lf-rear", LEFT, board.D5, 5, board.D4, 4, False),
    ("rf-front", RIGHT, board.D7, 7, board.D6, 6, False),
    ("rf-rear", RIGHT, board.D9, 9, board.D8, 8, False),
    ("cf-front", CENTRE, board.D10, 10, board.MOSI, 19, False),
    ("cf-rear", CENTRE, board.SCK, 18, board.MISO, 20, False),
    ("head", HEAD, board.A1, 27, board.A0, 26, False),
)

ENABLE_PIN = board.D1  # all four DRV8833 nSLEEP pins, high = awake
PIXEL_PIN = board.A2
INDEX_PIN = board.A3  # optional dome home sensor, active low
PIXEL_BRIGHTNESS = 0.4
STATUS_PERIOD_MS = 200  # unsolicited status cadence


# ---------------------------------------------------------------------------
# Hardware wrappers
# ---------------------------------------------------------------------------


class Motor:
    """One DRV8833 half-bridge pair driving one Adafruit 3777 TT motor."""

    def __init__(self, name, pwm_pin, digital_pin, invert=False):
        self.name = name
        self.invert = invert
        self.applied = 0
        self._pwm = pwmio.PWMOut(
            pwm_pin,
            frequency=protocol.PWM_FREQUENCY,
            duty_cycle=0,
            variable_frequency=False,
        )
        self._digital = digitalio.DigitalInOut(digital_pin)
        self._digital.direction = digitalio.Direction.OUTPUT
        self._digital.value = False

    def _write(self, high, duty):
        # Set the digital level first: every transition then passes through
        # coast or brake rather than through the opposite drive direction.
        self._digital.value = high
        self._pwm.duty_cycle = duty

    def apply(self, permille):
        """Drive the motor at ``permille`` (-1000..1000)."""
        high, duty = protocol.outputs_for_permille(permille, self.invert)
        self._write(high, duty)
        self.applied = permille

    def coast(self):
        """Release the motor (both inputs low)."""
        high, duty = protocol.outputs_for_coast()
        self._write(high, duty)
        self.applied = 0

    def brake(self):
        """Short the motor windings (both inputs high)."""
        high, duty = protocol.outputs_for_brake()
        self._write(high, duty)
        self.applied = 0


class DomeLights:
    """The 17 pixel dome chain: front PSI 0-6, rear PSI 7-13, holoprojectors 14-16."""

    FRONT_PSI = (0, 7)
    REAR_PSI = (7, 14)
    HOLOPROJECTORS = (14, 17)

    def __init__(self, pin, count=protocol.PIXEL_COUNT, brightness=PIXEL_BRIGHTNESS):
        self.count = count
        self.available = neopixel is not None
        self._pixels = None
        if self.available:
            self._pixels = neopixel.NeoPixel(
                pin, count, brightness=brightness, auto_write=False
            )

    def fill(self, red, green, blue):
        """Set every pixel and show."""
        if self._pixels is None:
            return False
        self._pixels.fill((red, green, blue))
        self._pixels.show()
        return True

    def set_pixel(self, index, red, green, blue):
        """Set one pixel and show."""
        if self._pixels is None:
            return False
        self._pixels[index] = (red, green, blue)
        self._pixels.show()
        return True

    def boot_sweep(self):
        """Walk one white pixel along the chain once, as a power-on indicator."""
        if self._pixels is None:
            return False
        for index in range(self.count):
            self._pixels.fill((0, 0, 0))
            self._pixels[index] = (40, 40, 40)
            self._pixels.show()
            time.sleep(0.02)
        self._pixels.fill((0, 0, 0))
        self._pixels.show()
        return True


def _now_ms():
    """Milliseconds since boot, as an integer that does not wrap in practice."""
    return time.monotonic_ns() // 1000000


def _check_pwm_plan(motors):
    """Return a human readable problem string, or None when the plan is legal."""
    gpios = [entry[3] for entry in motors]
    clashes = protocol.pwm_conflicts(gpios)
    if not clashes:
        return None
    parts = []
    for first, second in clashes:
        parts.append(
            "GP{0}/GP{1}=slice{2}{3}".format(
                first, second, protocol.pwm_slice(first), protocol.pwm_channel(first)
            )
        )
    return "pwm slice clash " + " ".join(parts)


# ---------------------------------------------------------------------------
# Controller
# ---------------------------------------------------------------------------


class Controller:
    """Owns the hardware, the ramp state and the serial conversation."""

    def __init__(self, serial):
        self.serial = serial
        self.drive = protocol.DriveState(protocol.RAMP_STEP)
        self.enabled = False
        self.timed_out = False
        self.buffer = ""
        self.last_command_ms = _now_ms()
        self.last_status_ms = 0

        self.enable_line = digitalio.DigitalInOut(ENABLE_PIN)
        self.enable_line.direction = digitalio.Direction.OUTPUT
        self.enable_line.value = False

        self.index_line = digitalio.DigitalInOut(INDEX_PIN)
        self.index_line.direction = digitalio.Direction.INPUT
        self.index_line.pull = digitalio.Pull.UP

        self.motors = []
        for name, channel, pwm_pin, _pwm_gpio, dig_pin, _dig_gpio, invert in MOTORS:
            self.motors.append((channel, Motor(name, pwm_pin, dig_pin, invert)))

        self.lights = DomeLights(PIXEL_PIN)

    # -- output helpers ---------------------------------------------------

    def send(self, text):
        """Write one already terminated protocol line."""
        self.serial.write(text.encode("utf-8"))

    def send_status(self, now_ms=None):
        """Emit the ``st`` line and remember when it went out."""
        current = self.drive.current
        self.send(
            protocol.format_status(
                self.enabled,
                current[LEFT],
                current[RIGHT],
                current[CENTRE],
                current[HEAD],
                self.index_detected(),
            )
        )
        self.last_status_ms = _now_ms() if now_ms is None else now_ms

    def index_detected(self):
        """True while the dome index sensor is pulled low."""
        return not self.index_line.value

    # -- command handling -------------------------------------------------

    def handle(self, line):
        """Execute one protocol line and answer on the serial port."""
        try:
            kind, args = protocol.parse_command(line)
        except protocol.CommandError as error:
            self.send(protocol.format_error(str(error)))
            return

        self.last_command_ms = _now_ms()
        self.timed_out = False

        if kind == "M":
            self.drive.set_targets(args)
            self.send(protocol.format_ok())
        elif kind == "S":
            self.drive.hard_stop()
            self.apply_outputs()
            self.send(protocol.format_ok())
        elif kind == "E":
            self.set_enabled(args[0] == 1)
            self.send(protocol.format_ok())
        elif kind == "L":
            if self.lights.fill(args[0], args[1], args[2]):
                self.send(protocol.format_ok())
            else:
                self.send(protocol.format_error("neopixel library missing"))
        elif kind == "P":
            if self.lights.set_pixel(args[0], args[1], args[2], args[3]):
                self.send(protocol.format_ok())
            else:
                self.send(protocol.format_error("neopixel library missing"))
        elif kind == "?":
            self.send_status()

    def set_enabled(self, flag):
        """Raise or drop the shared DRV8833 nSLEEP line."""
        if not flag:
            self.drive.hard_stop()
            self.apply_outputs()
        self.enabled = bool(flag)
        self.enable_line.value = self.enabled

    # -- motor output -----------------------------------------------------

    def apply_outputs(self):
        """Push the current ramp values to every motor."""
        current = self.drive.current
        for channel, motor in self.motors:
            motor.apply(current[channel] if self.enabled else 0)

    def coast_all(self):
        """Release every motor immediately."""
        for _channel, motor in self.motors:
            motor.coast()

    # -- main loop --------------------------------------------------------

    def read_serial(self):
        """Drain the USB CDC buffer and execute every complete line."""
        waiting = self.serial.in_waiting
        if waiting:
            chunk = self.serial.read(waiting)
            if chunk:
                self.buffer += chunk.decode("utf-8")
        lines, self.buffer = protocol.split_lines(self.buffer)
        if len(self.buffer) > 256:
            # A line this long is noise, not a command.  Drop it and say so.
            self.buffer = ""
            self.send(protocol.format_error("input line too long, discarded"))
        for line in lines:
            self.handle(line)

    def tick(self):
        """One control tick: serial, heartbeat, ramp, outputs, status."""
        self.read_serial()
        now = _now_ms()

        if now - self.last_command_ms > protocol.HEARTBEAT_MS:
            if not self.timed_out:
                self.timed_out = True
                self.drive.hard_stop()
                self.coast_all()
                self.send(protocol.format_error("heartbeat timeout, motors coasted"))
        else:
            self.drive.tick()
            self.apply_outputs()

        if now - self.last_status_ms >= STATUS_PERIOD_MS:
            self.send_status(now)

    def run(self):
        """Run the control loop forever at ``protocol.TICK_MS``."""
        period = protocol.TICK_MS / 1000.0
        next_tick = time.monotonic() + period
        while True:
            self.tick()
            delay = next_tick - time.monotonic()
            if delay > 0:
                time.sleep(delay)
                next_tick += period
            else:
                # Fell behind: resynchronise instead of accumulating lateness.
                next_tick = time.monotonic() + period


def main():
    """Entry point run by CircuitPython at boot."""
    serial = usb_cdc.data
    if serial is None:
        # boot.py did not enable the data endpoint; fall back to the console so
        # the robot still answers, and say so rather than failing silently.
        serial = usb_cdc.console
    serial.timeout = 0

    problem = _check_pwm_plan(MOTORS)
    controller = Controller(serial)
    if problem is not None:
        controller.send(protocol.format_error(problem))
    if _NEOPIXEL_IMPORT_ERROR is not None:
        controller.send(
            protocol.format_error("neopixel unavailable: " + _NEOPIXEL_IMPORT_ERROR)
        )
    if usb_cdc.data is None:
        controller.send(
            protocol.format_error("usb_cdc.data disabled, using console endpoint")
        )

    controller.lights.boot_sweep()
    controller.send_status()
    controller.run()


if __name__ == "__main__":
    main()
