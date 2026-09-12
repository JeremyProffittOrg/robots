"""Head displays for the fable-r2d2 Raspberry Pi control server.

Five devices live in the dome and all of them are driven from here.

front logic
    Two Adafruit 0.8 inch 8x8 HT16K33 mini matrix backpacks, one behind each
    front logic window: **0x70 upper window, 0x71 lower window**.  They are
    independent displays, so each gets its own animation with its own timing.
rear logic
    Two more 8x8 backpacks side by side behind the rear logic surround,
    **0x72 left and 0x73 right as seen from behind the robot**.  Together they
    form one 16 wide by 8 high strip, so they share a single 16 column pattern
    that scrolls across the seam rather than two patterns that stop at it.
radar eye
    A 1.28 inch 240x240 round GC9A01A SPI TFT behind the radar eye lens, on the
    Pi's SPI0 with chip select CE0, DC on GPIO25, reset on GPIO24 and the
    backlight on GPIO18.

Every device is optional and is checked on its own.  A missing library, a
backpack that does not answer, or a backpack that stops answering later is
logged with the reason and dropped; the remaining displays keep running and the
rest of the robot is unaffected.  Nothing is swallowed quietly.

Battery voltage is **not** read here and **not** read through the KB2040; see
``battery.py``.
"""

import logging
import math
import random
import threading
import time

LOGGER = logging.getLogger("r2d2.displays")

MATRIX_SIZE = 8
"""An Adafruit 0.8 inch mini matrix backpack is 8 columns by 8 rows."""

FRONT_LOGIC_ADDRESSES = ((0x70, "upper window"), (0x71, "lower window"))
"""The two front logic backpacks, each animated independently."""

REAR_LOGIC_ADDRESSES = ((0x72, "left"), (0x73, "right"))
"""The two rear logic backpacks, left to right as seen from behind the robot."""

REAR_STRIP_WIDTH = MATRIX_SIZE * len(REAR_LOGIC_ADDRESSES)
"""The rear pair is treated as one 16 column strip."""

RADAR_SIZE = 240
"""The GC9A01A is 240 by 240 pixels."""

RADAR_BAUDRATE = 24000000
"""SPI clock for the GC9A01A, the driver library's own default.  At 24 MHz a
full 240x240 16 bit frame takes about 38 ms, so the 15 frames a second the sweep
asks for is comfortable."""

MATRIX_BRIGHTNESS = 0.5
"""HT16K33 brightness, 0.0 to 1.0.  Half is bright enough behind the dome
windows without washing out on camera."""

LOGIC_FPS = 8
"""Frames a second for the logic displays.  The originals are deliberately slow."""

RADAR_FPS = 15
"""Frames a second for the radar eye sweep."""

# Optional imports.  Each failure is reported once, at start up, with the pip
# name that fixes it.
try:
    import board
    import digitalio

    BLINKA_ERROR = None
except (ImportError, NotImplementedError) as error:
    board = None
    digitalio = None
    BLINKA_ERROR = str(error)

try:
    from adafruit_ht16k33 import matrix as ht16k33_matrix

    HT16K33_ERROR = None
except ImportError as error:
    ht16k33_matrix = None
    HT16K33_ERROR = str(error)

try:
    # The driver module is spelled gc9a01a: the panel's controller is the
    # GC9A01A revision, and adafruit_rgb_display has no plain "gc9a01".
    from adafruit_rgb_display import gc9a01a

    GC9A01_ERROR = None
except ImportError as error:
    gc9a01a = None
    GC9A01_ERROR = str(error)

try:
    from PIL import Image, ImageDraw, ImageFont

    PILLOW_ERROR = None
except ImportError as error:
    Image = None
    ImageDraw = None
    ImageFont = None
    PILLOW_ERROR = str(error)


def _draw_bars(device, heights, first_column):
    """Paint eight bottom-anchored bars onto one 8x8 backpack.

    ``heights`` is the whole pattern; ``first_column`` says which slice of it
    this backpack shows.  Returns True when the write succeeded.
    """
    try:
        device.fill(0)
        for column in range(MATRIX_SIZE):
            height = heights[first_column + column]
            for row in range(height):
                device[column, MATRIX_SIZE - 1 - row] = 1
        device.show()
    except (OSError, RuntimeError) as error:
        LOGGER.error("matrix write failed: %s", error)
        return False
    return True


class FrontLogicWindow:
    """One 8x8 backpack behind a front logic window.

    The animation is the one the films use: short bars that appear, grow,
    shrink and vanish on their own timing, so no two columns are in step.  Each
    window has its own random seed, so the upper and lower windows never fall
    into the same rhythm.
    """

    def __init__(self, device, address, label, seed):
        self.device = device
        self.address = address
        self.label = label
        self.random = random.Random(seed)
        self.heights = [self.random.randint(0, MATRIX_SIZE) for _ in range(MATRIX_SIZE)]
        self.direction = [self.random.choice((-1, 1)) for _ in range(MATRIX_SIZE)]
        self.wait = [self.random.randint(0, 4) for _ in range(MATRIX_SIZE)]

    def describe(self):
        """Short name for the log."""
        return "front logic {0} (0x{1:02x})".format(self.label, self.address)

    def advance(self):
        """Step the pattern one frame."""
        for column in range(MATRIX_SIZE):
            if self.wait[column] > 0:
                self.wait[column] -= 1
                continue
            self.heights[column] += self.direction[column]
            if self.heights[column] >= MATRIX_SIZE:
                self.heights[column] = MATRIX_SIZE
                self.direction[column] = -1
                self.wait[column] = self.random.randint(0, 3)
            elif self.heights[column] <= 0:
                self.heights[column] = 0
                self.direction[column] = 1
                self.wait[column] = self.random.randint(0, 6)
            if self.random.random() < 0.08:
                self.direction[column] = -self.direction[column]

    def draw(self):
        """Write the current pattern.  Returns False when the backpack has died."""
        if not _draw_bars(self.device, self.heights, 0):
            LOGGER.error("%s stopped answering, dropping it", self.describe())
            return False
        return True

    def blank(self):
        """Best effort clear, used on shutdown."""
        try:
            self.device.fill(0)
            self.device.show()
        except (OSError, RuntimeError) as error:
            LOGGER.warning("could not blank %s: %s", self.describe(), error)


class RearLogicStrip:
    """The rear pair driven as one 16 wide by 8 high display.

    A single 16 column pattern scrolls sideways across both backpacks, so the
    movement carries over the seam between them instead of stopping at it.  A
    fresh random bar is pushed in at the leading edge each frame and the scroll
    direction reverses now and then.

    If one of the two backpacks stops answering, the other keeps showing its
    half of the same pattern.
    """

    def __init__(self, units, seed):
        # units: list of (first_column, device, address, label)
        self.units = list(units)
        self.random = random.Random(seed)
        self.heights = [self.random.randint(0, MATRIX_SIZE) for _ in range(REAR_STRIP_WIDTH)]
        self.rightwards = True

    def describe(self):
        """Short name for the log."""
        return "rear logic strip ({0})".format(
            ", ".join("0x{0:02x} {1}".format(unit[2], unit[3]) for unit in self.units)
        )

    def advance(self):
        """Scroll one column and push a new bar in at the leading edge."""
        if self.random.random() < 0.03:
            self.rightwards = not self.rightwards
        fresh = self.random.randint(0, MATRIX_SIZE)
        if self.rightwards:
            self.heights = [fresh] + self.heights[:-1]
        else:
            self.heights = self.heights[1:] + [fresh]
        # A slow flicker on one random column keeps the strip from looking like
        # a plain conveyor belt.
        if self.random.random() < 0.25:
            column = self.random.randrange(REAR_STRIP_WIDTH)
            self.heights[column] = self.random.randint(0, MATRIX_SIZE)

    def draw(self):
        """Write both halves.  Returns False once no unit is left."""
        for unit in list(self.units):
            first_column, device, address, label = unit
            if not _draw_bars(device, self.heights, first_column):
                LOGGER.error("rear logic %s unit at 0x%02x stopped answering, dropping it",
                             label, address)
                self.units.remove(unit)
        if not self.units:
            LOGGER.error("every rear logic unit has stopped answering")
            return False
        return True

    def blank(self):
        """Best effort clear, used on shutdown."""
        for _first_column, device, address, _label in self.units:
            try:
                device.fill(0)
                device.show()
            except (OSError, RuntimeError) as error:
                LOGGER.warning("could not blank rear logic 0x%02x: %s", address, error)


class RadarEye:
    """The round GC9A01A behind the radar eye lens.

    Draws a sweeping radar line with a fading trail, range rings, a crosshair,
    and two lines of status text taken from the control server.
    """

    BACKGROUND = (4, 10, 6)
    RING = (18, 74, 40)
    SWEEP = (74, 240, 130)
    TEXT = (190, 255, 210)
    ALERT = (255, 120, 90)
    TRAIL_STEPS = 14

    def __init__(self, device):
        self.device = device
        self.angle = 0.0
        self.font = ImageFont.load_default()
        self.centre = RADAR_SIZE // 2
        self.radius = self.centre - 6
        self.blips = []
        self.random = random.Random(20260912)

    def _point(self, angle, distance):
        """Cartesian point at ``angle`` radians and ``distance`` pixels from centre."""
        return (
            self.centre + distance * math.cos(angle),
            self.centre + distance * math.sin(angle),
        )

    def _refresh_blips(self):
        """Keep a handful of contacts on the scope, replacing them slowly."""
        while len(self.blips) < 5:
            self.blips.append(
                (
                    self.random.uniform(0.0, 2.0 * math.pi),
                    self.random.uniform(0.25, 0.92) * self.radius,
                )
            )
        if self.random.random() < 0.02 and self.blips:
            self.blips.pop(0)

    def frame(self, status_lines):
        """Render and push one frame."""
        image = Image.new("RGB", (RADAR_SIZE, RADAR_SIZE), self.BACKGROUND)
        draw = ImageDraw.Draw(image)

        for fraction in (0.33, 0.66, 1.0):
            size = self.radius * fraction
            draw.ellipse(
                [
                    self.centre - size,
                    self.centre - size,
                    self.centre + size,
                    self.centre + size,
                ],
                outline=self.RING,
            )
        draw.line(
            [self.centre - self.radius, self.centre, self.centre + self.radius, self.centre],
            fill=self.RING,
        )
        draw.line(
            [self.centre, self.centre - self.radius, self.centre, self.centre + self.radius],
            fill=self.RING,
        )

        self._refresh_blips()
        for angle, distance in self.blips:
            separation = (self.angle - angle) % (2.0 * math.pi)
            brightness = max(0.0, 1.0 - separation / 1.2)
            if brightness <= 0.0:
                continue
            x, y = self._point(angle, distance)
            colour = tuple(int(channel * brightness) for channel in self.SWEEP)
            draw.ellipse([x - 3, y - 3, x + 3, y + 3], fill=colour)

        for step in range(self.TRAIL_STEPS):
            angle = self.angle - step * 0.055
            brightness = 1.0 - step / float(self.TRAIL_STEPS)
            colour = tuple(int(channel * brightness * brightness) for channel in self.SWEEP)
            draw.line([self.centre, self.centre] + list(self._point(angle, self.radius)),
                      fill=colour)

        top = status_lines[0] if status_lines else ""
        bottom = status_lines[1] if len(status_lines) > 1 else ""
        draw.text((10, 8), top, font=self.font, fill=self.TEXT)
        draw.text((10, RADAR_SIZE - 20), bottom, font=self.font,
                  fill=self.ALERT if bottom.startswith("LINK DOWN") else self.TEXT)

        self.device.image(image)
        self.angle = (self.angle + 0.18) % (2.0 * math.pi)


class DisplayWorker:
    """Background thread that animates every dome display that is present."""

    def __init__(self, status_provider=None):
        self.status_provider = status_provider or (lambda: {})
        self._stop_event = threading.Event()
        self._thread = None
        self.animations = []
        self.radar = None
        self.backlight = None
        self.problems = []

    # -- setup ------------------------------------------------------------

    def _note(self, text):
        """Record and log a display that will not be used."""
        self.problems.append(text)
        LOGGER.error("%s", text)

    def _open_logic(self):
        """Open the four HT16K33 8x8 backpacks that answer."""
        if ht16k33_matrix is None:
            self._note(
                "front and rear logic displays disabled: adafruit_ht16k33 is not "
                "installed ({0}); fix with 'pip install adafruit-circuitpython-ht16k33'".format(
                    HT16K33_ERROR
                )
            )
            return
        if board is None:
            self._note(
                "logic displays disabled: Blinka is not available ({0}); fix with "
                "'pip install Adafruit-Blinka' and enable I2C in raspi-config".format(
                    BLINKA_ERROR
                )
            )
            return
        try:
            i2c = board.I2C()
        except (OSError, RuntimeError, ValueError) as error:
            self._note("logic displays disabled: cannot open I2C ({0}); is I2C "
                       "enabled in raspi-config?".format(error))
            return

        for index, (address, label) in enumerate(FRONT_LOGIC_ADDRESSES):
            device = self._open_matrix(i2c, address, "front logic " + label)
            if device is not None:
                self.animations.append(
                    FrontLogicWindow(device, address, label, seed=1000 + index)
                )

        rear_units = []
        for index, (address, label) in enumerate(REAR_LOGIC_ADDRESSES):
            device = self._open_matrix(i2c, address, "rear logic " + label)
            if device is not None:
                rear_units.append((index * MATRIX_SIZE, device, address, label))
        if rear_units:
            if len(rear_units) < len(REAR_LOGIC_ADDRESSES):
                LOGGER.warning(
                    "only %d of %d rear logic backpacks answered; the strip runs "
                    "on the half that is present",
                    len(rear_units), len(REAR_LOGIC_ADDRESSES),
                )
            self.animations.append(RearLogicStrip(rear_units, seed=2000))

    def _open_matrix(self, i2c, address, what):
        """Open one 8x8 HT16K33 backpack, or report why it could not be opened."""
        try:
            device = ht16k33_matrix.Matrix8x8(i2c, address=address, auto_write=False)
        except (OSError, ValueError, RuntimeError) as error:
            self._note("{0} matrix at 0x{1:02x} not responding: {2}".format(
                what, address, error))
            return None
        device.brightness = MATRIX_BRIGHTNESS
        device.fill(0)
        device.show()
        LOGGER.info("%s matrix ready at 0x%02x", what, address)
        return device

    def _open_radar(self):
        """Open the GC9A01A round TFT."""
        if gc9a01a is None:
            self._note(
                "radar eye disabled: adafruit_rgb_display.gc9a01a is not available "
                "({0}); fix with 'pip install adafruit-circuitpython-rgb-display'".format(
                    GC9A01_ERROR
                )
            )
            return
        if Image is None:
            self._note("radar eye disabled: Pillow is not installed ({0}); fix with "
                       "'pip install Pillow'".format(PILLOW_ERROR))
            return
        if board is None:
            self._note("radar eye disabled: Blinka is not available ({0})".format(BLINKA_ERROR))
            return
        try:
            spi = board.SPI()
            cs_pin = digitalio.DigitalInOut(board.CE0)
            dc_pin = digitalio.DigitalInOut(board.D25)
            reset_pin = digitalio.DigitalInOut(board.D24)
            self.backlight = digitalio.DigitalInOut(board.D18)
            self.backlight.switch_to_output(value=True)
            device = gc9a01a.GC9A01A(
                spi,
                dc=dc_pin,
                cs=cs_pin,
                rst=reset_pin,
                width=RADAR_SIZE,
                height=RADAR_SIZE,
                baudrate=RADAR_BAUDRATE,
            )
        except (OSError, RuntimeError, ValueError, AttributeError) as error:
            self._note("radar eye disabled: cannot start the GC9A01A ({0}); is SPI "
                       "enabled in raspi-config?".format(error))
            return
        self.radar = RadarEye(device)
        LOGGER.info("radar eye ready on SPI0 CE0")

    # -- animation --------------------------------------------------------

    def status_lines(self):
        """Two short lines of text for the radar eye."""
        status = {}
        try:
            status = self.status_provider() or {}
        except Exception as error:  # a status provider must never stop the display
            LOGGER.warning("status provider failed: %s", error)
        if status.get("connected") and status.get("fresh"):
            top = "R2-FABLE  ONLINE"
            speed = status.get("speed_cap")
            commanded = status.get("commanded") or [0, 0, 0, 0]
            bottom = "CAP {0:>3d}%  L{1:+05d} R{2:+05d}".format(
                int(round((speed or 0.0) * 100)), int(commanded[0]), int(commanded[1])
            )
        else:
            top = "R2-FABLE  STANDBY"
            bottom = "LINK DOWN"
        return [top, bottom]

    def _run(self):
        """Thread body: animate each display at its own rate."""
        logic_period = 1.0 / LOGIC_FPS
        radar_period = 1.0 / RADAR_FPS
        next_logic = time.monotonic()
        next_radar = time.monotonic()
        while not self._stop_event.is_set():
            now = time.monotonic()
            if now >= next_logic:
                for animation in list(self.animations):
                    animation.advance()
                    self._safe_draw(animation)
                next_logic = now + logic_period
            if self.radar is not None and now >= next_radar:
                try:
                    self.radar.frame(self.status_lines())
                except (OSError, RuntimeError) as error:
                    LOGGER.error("radar eye write failed, stopping it: %s", error)
                    self.radar = None
                next_radar = now + radar_period
            sleep_for = min(next_logic, next_radar) - time.monotonic()
            self._stop_event.wait(max(0.005, sleep_for))

    def _safe_draw(self, animation):
        """Draw one animation, dropping it if its hardware has stopped answering."""
        try:
            alive = animation.draw()
        except (OSError, RuntimeError) as error:
            LOGGER.error("%s failed unexpectedly, stopping it: %s",
                         animation.describe(), error)
            alive = False
        if not alive and animation in self.animations:
            self.animations.remove(animation)

    # -- lifecycle --------------------------------------------------------

    def start(self):
        """Open every display that answers and start animating."""
        self._open_logic()
        self._open_radar()
        if not self.animations and self.radar is None:
            LOGGER.warning("no head displays are available; the robot runs without them")
            return
        LOGGER.info("head displays running: %s%s",
                    ", ".join(animation.describe() for animation in self.animations) or "none",
                    ", radar eye" if self.radar is not None else "")
        self._stop_event.clear()
        self._thread = threading.Thread(target=self._run, name="displays", daemon=True)
        self._thread.start()

    def close(self):
        """Stop animating, blank the panels and turn the backlight off."""
        self._stop_event.set()
        if self._thread is not None:
            self._thread.join(timeout=2.0)
            self._thread = None
        for animation in list(self.animations):
            animation.blank()
        if self.backlight is not None:
            try:
                self.backlight.value = False
            except (OSError, RuntimeError) as error:
                LOGGER.warning("could not turn the radar backlight off: %s", error)
