"""fable-r2d2 motor, dome-light and stance controller, Adafruit KB2040 (product 5302).

CircuitPython 9.  Copy this file, ``boot.py``, ``protocol.py``, ``stance.py`` and
``supervisor.py`` to CIRCUITPY, plus ``neopixel.mpy`` from the CircuitPython 9
library bundle (see README.md).

Responsibilities
    * drive the three foot pairs and the dome motor through four DRV8833 (3297)
    * drive the 12 V centre-leg actuator through a DRV8871 (3190)
    * drive the lock-release servo and read the lock switch (NO + NC)
    * read the actuator potentiometer and the battery divider
    * drive the 17 pixel dome NeoPixel chain, read the dome index sensor
    * speak the line protocol in ``protocol.py`` over USB CDC data
    * everything that decides what moves is in ``supervisor.py`` and ``stance.py``

Pin map (KB2040 silkscreen name, RP2040 GPIO), verified against
ports/raspberrypi/boards/adafruit_kb2040/pins.c in the CircuitPython tree:

    D0=GP0  D1=GP1  D2=GP2  D3=GP3  D4=GP4  D5=GP5  D6=GP6  D7=GP7
    D8=GP8  D9=GP9  D10=GP10  SCK=GP18  MOSI=GP19  MISO=GP20
    A0=GP26  A1=GP27  A2=GP28  A3=GP29  SDA=GP12  SCL=GP13 (STEMMA QT)

Revision D pin budget
    The revision C map used every header pin: one PWM and one digital pin for
    each of seven motors.  Both motors in a foot always receive the same value,
    so revision D drives each foot's two DRV8833 channels from one pin pair
    (AIN1 jumpered to BIN1, AIN2 to BIN2 on the board).  That frees D4, D5, D8,
    D9, SCK, MISO, A0 and A1.  The head moves to D4/D5 so that A0 and A1, two of
    only four ADC pins, can read the actuator pot and the battery.

One PWM pin and one plain digital pin per output
    GPIO n uses PWM slice (n >> 1) & 7, channel n & 1.  The five 20 kHz PWM
    pins below occupy five different slice/channel pairs, and the 50 Hz servo
    sits alone on slice 0 (its partner GP1 is the plain SLP output), because
    both channels of a slice share one frequency.  ``_check_pin_plan`` re-verifies
    this at boot.
"""

import time

import analogio
import board
import digitalio
import pwmio
import usb_cdc

import protocol
import stance
import supervisor

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
# The PWM pin is the driver input that is modulated; the digital pin is held
# high for the slow-decay direction.  Each foot pin pair feeds both DRV8833
# channels of that foot's board.
DRIVES = (
    ("left", LEFT, board.D3, 3, board.D2, 2, False),
    ("right", RIGHT, board.D7, 7, board.D6, 6, False),
    ("centre", CENTRE, board.D10, 10, board.MOSI, 19, False),
    ("head", HEAD, board.D5, 5, board.D4, 4, False),
)

# DRV8871 IN2 is modulated, IN1 is the digital level.  Positive percent extends
# the actuator (toward the three-foot stance).  If the pot reads backwards the
# stance machine latches REVERSED_FEEDBACK; swap the actuator's motor leads.
ACTUATOR = ("actuator", board.D9, 9, board.D8, 8, False)

ENABLE_PIN = board.D1  # all four DRV8833 SLP pins, high = awake
PIXEL_PIN = board.A2
INDEX_PIN = board.A3  # optional dome home sensor, active low
RELEASE_SERVO_PIN = board.D0  # through level shifter U11 to the MG995 signal
RELEASE_SERVO_GPIO = 0
LOCK_NO_PIN = board.SCK  # lock switch NO contact, 3.3 k pull-up, low = closed
LOCK_NO_GPIO = 18
LOCK_NC_PIN = board.MISO  # lock switch NC contact, 3.3 k pull-up, low = closed
LOCK_NC_GPIO = 20
POSITION_PIN = board.A0  # actuator pot wiper, 470 k pull-down
POSITION_GPIO = 26
BATTERY_PIN = board.A1  # 12 V bus through 100 k over 15 k
BATTERY_GPIO = 27

PIXEL_BRIGHTNESS = 0.4
ADC_SAMPLES = 4


# ---------------------------------------------------------------------------
# Hardware wrappers
# ---------------------------------------------------------------------------


class Motor:
    """One H-bridge input pair: a DRV8833 channel pair or the DRV8871."""

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
        # Digital level first: every change passes through coast or brake,
        # never through the opposite drive direction.
        self._digital.value = high
        self._pwm.duty_cycle = duty

    def apply(self, permille):
        high, duty = protocol.outputs_for_permille(permille, self.invert)
        self._write(high, duty)
        self.applied = permille

    def coast(self):
        high, duty = protocol.outputs_for_coast()
        self._write(high, duty)
        self.applied = 0


class DomeLights:
    """The 17 pixel dome chain: front PSI 0-6, rear PSI 7-13, holoprojectors 14-16."""

    def __init__(self, pin, count=protocol.PIXEL_COUNT, brightness=PIXEL_BRIGHTNESS):
        self.count = count
        self._pixels = None
        if neopixel is not None:
            self._pixels = neopixel.NeoPixel(pin, count, brightness=brightness, auto_write=False)

    def fill(self, red, green, blue):
        if self._pixels is None:
            return False
        self._pixels.fill((red, green, blue))
        self._pixels.show()
        return True

    def set_pixel(self, index, red, green, blue):
        if self._pixels is None:
            return False
        self._pixels[index] = (red, green, blue)
        self._pixels.show()
        return True

    def boot_sweep(self):
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


class Hardware:
    """The real pins behind the hardware object ``supervisor.Supervisor`` expects."""

    def __init__(self):
        self.enable_line = digitalio.DigitalInOut(ENABLE_PIN)
        self.enable_line.direction = digitalio.Direction.OUTPUT
        self.enable_line.value = False

        self.index_line = digitalio.DigitalInOut(INDEX_PIN)
        self.index_line.direction = digitalio.Direction.INPUT
        self.index_line.pull = digitalio.Pull.UP

        self.drives = []
        for name, channel, pwm_pin, _pwm_gpio, dig_pin, _dig_gpio, invert in DRIVES:
            self.drives.append((channel, Motor(name, pwm_pin, dig_pin, invert)))
        name, pwm_pin, _pwm_gpio, dig_pin, _dig_gpio, invert = ACTUATOR
        self.actuator = Motor(name, pwm_pin, dig_pin, invert)

        self.servo = pwmio.PWMOut(RELEASE_SERVO_PIN, frequency=protocol.SERVO_FREQUENCY,
                                  duty_cycle=0, variable_frequency=False)
        self._servo_duty = 0

        self.lock_no = digitalio.DigitalInOut(LOCK_NO_PIN)
        self.lock_no.direction = digitalio.Direction.INPUT
        self.lock_no.pull = digitalio.Pull.UP
        self.lock_nc = digitalio.DigitalInOut(LOCK_NC_PIN)
        self.lock_nc.direction = digitalio.Direction.INPUT
        self.lock_nc.pull = digitalio.Pull.UP

        self.position = analogio.AnalogIn(POSITION_PIN)
        self.battery = analogio.AnalogIn(BATTERY_PIN)
        self.lights = DomeLights(PIXEL_PIN)

    @staticmethod
    def _average(channel):
        total = 0
        for _ in range(ADC_SAMPLES):
            total += channel.value
        return total / ADC_SAMPLES

    def set_enabled(self, flag):
        self.enable_line.value = bool(flag)

    def apply_drive(self, enabled, channels):
        for channel, motor in self.drives:
            motor.apply(channels[channel] if enabled else 0)

    def coast_all(self):
        for _channel, motor in self.drives:
            motor.coast()

    def fill(self, red, green, blue):
        return self.lights.fill(red, green, blue)

    def set_pixel(self, index, red, green, blue):
        return self.lights.set_pixel(index, red, green, blue)

    def index_detected(self):
        return not self.index_line.value

    def read_position_mv(self):
        return stance.adc_to_mv(self._average(self.position))

    def read_lock_contacts(self):
        return (not self.lock_no.value, not self.lock_nc.value)

    def read_battery_mv(self):
        return stance.pack_mv_from_node(stance.adc_to_mv(self._average(self.battery)))

    def drive_actuator(self, percent):
        self.actuator.apply(int(percent) * 10)

    def set_release_pulse(self, pulse_us):
        duty = stance.servo_duty(pulse_us)
        if duty != self._servo_duty:
            self.servo.duty_cycle = duty
            self._servo_duty = duty


def _now_ms():
    """Milliseconds since boot, as an integer that does not wrap in practice."""
    return time.monotonic_ns() // 1000000


def _check_pin_plan():
    """Return a human readable problem string, or None when the plan is legal."""
    problems = []
    fast = [entry[3] for entry in DRIVES] + [ACTUATOR[2]]
    for first, second in protocol.pwm_conflicts(fast + [RELEASE_SERVO_GPIO]):
        problems.append("pwm slice clash GP{0}/GP{1}".format(first, second))
    outputs = [(gpio, protocol.PWM_FREQUENCY) for gpio in fast]
    outputs.append((RELEASE_SERVO_GPIO, protocol.SERVO_FREQUENCY))
    for first, second in protocol.pwm_frequency_conflicts(outputs):
        problems.append("pwm frequency clash GP{0}/GP{1}".format(first, second))
    for label, gpio in (("position", POSITION_GPIO), ("battery", BATTERY_GPIO)):
        if gpio not in protocol.ADC_GPIOS:
            problems.append("{0} input GP{1} has no ADC".format(label, gpio))
    return "; ".join(problems) if problems else None


# ---------------------------------------------------------------------------
# Main loop
# ---------------------------------------------------------------------------


def run(serial, core):
    """Read serial, tick the supervisor every ``protocol.TICK_MS``, forever."""
    period = protocol.TICK_MS / 1000.0
    next_tick = time.monotonic() + period
    while True:
        waiting = serial.in_waiting
        if waiting:
            chunk = serial.read(waiting)
            if chunk:
                core.feed(chunk.decode("utf-8"), _now_ms())
        core.tick(_now_ms())
        delay = next_tick - time.monotonic()
        if delay > 0:
            time.sleep(delay)
            next_tick += period
        else:
            next_tick = time.monotonic() + period


def main():
    """Entry point run by CircuitPython at boot."""
    serial = usb_cdc.data
    if serial is None:
        serial = usb_cdc.console
    serial.timeout = 0

    def write(text):
        serial.write(text.encode("utf-8"))

    problem = _check_pin_plan()
    hardware = Hardware()
    core = supervisor.Supervisor(hardware, write, _now_ms())
    if problem is not None:
        write(protocol.format_error(problem))
    if _NEOPIXEL_IMPORT_ERROR is not None:
        write(protocol.format_error("neopixel unavailable: " + _NEOPIXEL_IMPORT_ERROR))
    if usb_cdc.data is None:
        write(protocol.format_error("usb_cdc.data disabled, using console endpoint"))

    hardware.lights.boot_sweep()
    core.send_status(_now_ms())
    run(serial, core)


if __name__ == "__main__":
    main()
