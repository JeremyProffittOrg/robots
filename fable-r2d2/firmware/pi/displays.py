"""Head displays for the fable-r2d2 Raspberry Pi control server.

Three things live in the dome and all three are driven from here:

front logic
    Two Adafruit 8x16 LED matrices on HT16K33 backpacks, I2C 0x70 and 0x71,
    side by side behind the front logic surround.
rear logic
    One Adafruit 8x16 LED matrix on an HT16K33 backpack, I2C 0x72.
radar eye
    A 1.28 inch 240x240 round GC9A01 SPI TFT behind the radar eye lens, on the
    Pi's SPI0 with chip select CE0, DC on GPIO25, reset on GPIO24 and the
    backlight on GPIO18.

Every device is optional.  A missing library or a device that does not answer is
logged once with the reason and the rest of the robot carries on; nothing is
swallowed quietly.
"""

import logging
import math
import random
import threading
import time

LOGGER = logging.getLogger("r2d2.displays")

FRONT_LOGIC_ADDRESSES = (0x70, 0x71)
"""The two front logic backpacks."""

REAR_LOGIC_ADDRESS = 0x72
"""The single rear logic backpack."""

MATRIX_WIDTH = 16
"""Columns on an Adafruit 8x16 matrix."""

MATRIX_HEIGHT = 8
"""Rows on an Adafruit 8x16 matrix."""

RADAR_SIZE = 240
"""The GC9A01 is 240 by 240 pixels."""

RADAR_BAUDRATE = 24000000
"""SPI clock for the GC9A01A, the driver library's own default.  At 24 MHz a
full 240x240 16 bit frame takes about 38 ms, so the 15 frames a second the sweep
asks for is comfortable."""

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


class LogicPanel:
    """One 8x16 HT16K33 matrix animated as an R2-D2 logic display.

    The animation is the one the films use: short horizontal bars that appear,
    grow, shrink and vanish on their own timing, so no two columns are in step.
    """

    def __init__(self, device, seed):
        self.device = device
        self.random = random.Random(seed)
        self.length = [self.random.randint(0, MATRIX_HEIGHT) for _ in range(MATRIX_WIDTH)]
        self.direction = [self.random.choice((-1, 1)) for _ in range(MATRIX_WIDTH)]
        self.wait = [self.random.randint(0, 4) for _ in range(MATRIX_WIDTH)]

    def advance(self):
        """Step the pattern one frame."""
        for column in range(MATRIX_WIDTH):
            if self.wait[column] > 0:
                self.wait[column] -= 1
                continue
            self.length[column] += self.direction[column]
            if self.length[column] >= MATRIX_HEIGHT:
                self.length[column] = MATRIX_HEIGHT
                self.direction[column] = -1
                self.wait[column] = self.random.randint(0, 3)
            elif self.length[column] <= 0:
                self.length[column] = 0
                self.direction[column] = 1
                self.wait[column] = self.random.randint(0, 6)
            if self.random.random() < 0.08:
                self.direction[column] = -self.direction[column]

    def draw(self):
        """Write the current pattern to the matrix."""
        self.device.fill(0)
        for column in range(MATRIX_WIDTH):
            for row in range(self.length[column]):
                self.device[column, MATRIX_HEIGHT - 1 - row] = 1
        self.device.show()


class RadarEye:
    """The round GC9A01 behind the radar eye lens.

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
        self.front_panels = []
        self.rear_panel = None
        self.radar = None
        self.backlight = None
        self.problems = []

    # -- setup ------------------------------------------------------------

    def _note(self, text):
        """Record and log a display that will not be used."""
        self.problems.append(text)
        LOGGER.error("%s", text)

    def _open_logic(self):
        """Open the three HT16K33 backpacks that answer."""
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

        for index, address in enumerate(FRONT_LOGIC_ADDRESSES):
            device = self._open_matrix(i2c, address, "front logic")
            if device is not None:
                self.front_panels.append(LogicPanel(device, seed=1000 + index))
        device = self._open_matrix(i2c, REAR_LOGIC_ADDRESS, "rear logic")
        if device is not None:
            self.rear_panel = LogicPanel(device, seed=2000)

    def _open_matrix(self, i2c, address, what):
        """Open one HT16K33 matrix, or report why it could not be opened."""
        try:
            device = ht16k33_matrix.Matrix8x16(i2c, address=address, auto_write=False)
        except (OSError, ValueError, RuntimeError) as error:
            self._note("{0} matrix at 0x{1:02x} not responding: {2}".format(
                what, address, error))
            return None
        device.brightness = 0.5
        device.fill(0)
        device.show()
        LOGGER.info("%s matrix ready at 0x%02x", what, address)
        return device

    def _open_radar(self):
        """Open the GC9A01 round TFT."""
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
            self._note("radar eye disabled: cannot start the GC9A01 ({0}); is SPI "
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
                for panel in self.front_panels:
                    panel.advance()
                    self._safe_draw(panel)
                if self.rear_panel is not None:
                    self.rear_panel.advance()
                    self._safe_draw(self.rear_panel)
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

    def _safe_draw(self, panel):
        """Draw one logic panel, dropping it if the bus stops answering."""
        try:
            panel.draw()
        except (OSError, RuntimeError) as error:
            LOGGER.error("logic panel write failed, stopping it: %s", error)
            if panel is self.rear_panel:
                self.rear_panel = None
            elif panel in self.front_panels:
                self.front_panels.remove(panel)

    # -- lifecycle --------------------------------------------------------

    def start(self):
        """Open every display that answers and start animating."""
        self._open_logic()
        self._open_radar()
        if not self.front_panels and self.rear_panel is None and self.radar is None:
            LOGGER.warning("no head displays are available; the robot runs without them")
            return
        self._stop_event.clear()
        self._thread = threading.Thread(target=self._run, name="displays", daemon=True)
        self._thread.start()

    def close(self):
        """Stop animating, blank the panels and turn the backlight off."""
        self._stop_event.set()
        if self._thread is not None:
            self._thread.join(timeout=2.0)
            self._thread = None
        for panel in list(self.front_panels) + ([self.rear_panel] if self.rear_panel else []):
            try:
                panel.device.fill(0)
                panel.device.show()
            except (OSError, RuntimeError) as error:
                LOGGER.warning("could not blank a logic panel: %s", error)
        if self.backlight is not None:
            try:
                self.backlight.value = False
            except (OSError, RuntimeError) as error:
                LOGGER.warning("could not turn the radar backlight off: %s", error)
