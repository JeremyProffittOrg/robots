"""USB CDC link from the Raspberry Pi to the KB2040 motor controller.

One background thread owns the serial port.  It sends an ``M`` drive line every
50 ms (20 Hz), which doubles as the heartbeat the KB2040 watches, ramps the
commanded values so the Pi reports what the motors are really being given, reads
``ok``/``st``/``err`` lines back, and reconnects on its own if the port
disappears.

Everything the web server touches goes through :class:`SerialLink`, which is
safe to call from the asyncio loop: the public methods only take a lock and
update small pieces of state.
"""

import glob
import logging
import os
import threading
import time

import mixing
import stance_link

LOGGER = logging.getLogger("r2d2.serial")

BAUD_RATE = 115200
"""Matches the KB2040 USB CDC endpoint.  USB CDC ignores the rate, but pyserial
still wants one and a mismatched value confuses anyone reading the code."""

READ_TIMEOUT = 0.02
"""Seconds pyserial waits for an inbound line."""

RECONNECT_SECONDS = 2.0
"""Delay between reconnection attempts after the port is lost."""

STALE_STATUS_SECONDS = 1.0
"""A status older than this means the controller has stopped answering."""

try:
    import serial
    from serial.tools import list_ports

    SERIAL_IMPORT_ERROR = None
except ImportError as error:  # pragma: no cover - depends on the host
    serial = None
    list_ports = None
    SERIAL_IMPORT_ERROR = str(error)


def find_port(preferred=None):
    """Return the device path of the KB2040 data endpoint, or ``None``.

    CircuitPython with ``usb_cdc.enable(console=True, data=True)`` presents two
    CDC interfaces.  The console is the first and the data endpoint the second,
    so on Raspberry Pi OS the console is normally ``/dev/ttyACM0`` and the data
    endpoint ``/dev/ttyACM1``.  The search prefers a port whose USB interface
    string names the second CDC interface, then the highest numbered Adafruit
    ACM port, then any ACM port at all.
    """
    if preferred:
        return preferred
    environment = os.environ.get("R2D2_SERIAL_PORT")
    if environment:
        return environment

    candidates = []
    if list_ports is not None:
        for port in list_ports.comports():
            if port.vid == 0x239A or (port.manufacturer or "").lower().startswith("adafruit"):
                interface = (port.interface or "") + " " + (port.product or "")
                score = 2 if "CDC2" in interface or "data" in interface.lower() else 1
                candidates.append((score, port.device))
    if not candidates:
        for device in sorted(glob.glob("/dev/ttyACM*")):
            candidates.append((0, device))
    if not candidates:
        return None
    candidates.sort()
    return candidates[-1][1]


class SerialLink:
    """Owns the serial port and the 20 Hz command stream."""

    def __init__(self, port=None, baud_rate=BAUD_RATE, clock=time.monotonic):
        self.requested_port = port
        self.baud_rate = baud_rate
        self.clock = clock
        self._stance_request = stance_link.REQUEST_NONE
        self.last_stance = None
        self.last_stance_at = 0.0

        self._lock = threading.Lock()
        self._stop_event = threading.Event()
        self._thread = None
        self._serial = None

        self._target = [0, 0, 0, 0]
        self._current = [0, 0, 0, 0]
        self._pending = []
        self._enabled = False

        self.port_name = None
        self.connected = False
        self.last_error = None
        self.last_status = None
        self.last_status_at = 0.0
        self.commands_sent = 0

        if serial is None:
            LOGGER.error(
                "pyserial is not installed (%s); the motor controller link is "
                "disabled and the robot will not move. Install it with "
                "'pip install pyserial'.",
                SERIAL_IMPORT_ERROR,
            )

    # -- public API -------------------------------------------------------

    def start(self):
        """Start the background thread.  Safe to call once."""
        if self._thread is not None:
            return
        self._stop_event.clear()
        self._thread = threading.Thread(target=self._run, name="serial-link", daemon=True)
        self._thread.start()

    def close(self):
        """Stop the motors, stop the thread and close the port."""
        self._stop_event.set()
        if self._thread is not None:
            self._thread.join(timeout=2.0)
            self._thread = None

    def set_drive(self, left, right, centre, head):
        """Set the four channel targets in permille."""
        with self._lock:
            self._target = [
                mixing.clamp(int(left), -mixing.MAX_PERMILLE, mixing.MAX_PERMILLE),
                mixing.clamp(int(right), -mixing.MAX_PERMILLE, mixing.MAX_PERMILLE),
                mixing.clamp(int(centre), -mixing.MAX_PERMILLE, mixing.MAX_PERMILLE),
                mixing.clamp(int(head), -mixing.MAX_PERMILLE, mixing.MAX_PERMILLE),
            ]

    def set_head(self, head):
        """Set only the head channel, leaving the feet as they are."""
        with self._lock:
            self._target[3] = mixing.clamp(
                int(head), -mixing.MAX_PERMILLE, mixing.MAX_PERMILLE
            )

    def stop(self):
        """Zero every channel and the stance request immediately and queue an ``S`` line."""
        with self._lock:
            self._target = [0, 0, 0, 0]
            self._current = [0, 0, 0, 0]
            self._stance_request = stance_link.REQUEST_NONE
            self._pending.append("S\n")

    def set_stance_request(self, target):
        """Set the stance request sent as ``T`` with every drive line (0, 2 or 3)."""
        stance_link.format_request(target)  # validates
        with self._lock:
            self._stance_request = target

    def clear_stance_fault(self):
        """Queue a ``C`` line."""
        with self._lock:
            self._pending.append(stance_link.CLEAR_LINE)

    def stance_status(self):
        """Return ``(last ss status dict or None, age in seconds or None)``."""
        with self._lock:
            if self.last_stance is None:
                return None, None
            return dict(self.last_stance), self.clock() - self.last_stance_at

    def set_enabled(self, enabled):
        """Queue the DRV8833 enable line change."""
        with self._lock:
            self._enabled = bool(enabled)
            if not enabled:
                self._target = [0, 0, 0, 0]
                self._current = [0, 0, 0, 0]
            self._pending.append("E {0}\n".format(1 if enabled else 0))

    def set_all_pixels(self, red, green, blue):
        """Queue an ``L`` line for the whole dome chain."""
        with self._lock:
            self._pending.append(
                "L {0} {1} {2}\n".format(
                    mixing.clamp(int(red), 0, 255),
                    mixing.clamp(int(green), 0, 255),
                    mixing.clamp(int(blue), 0, 255),
                )
            )

    def set_pixel(self, index, red, green, blue):
        """Queue a ``P`` line for one dome pixel."""
        index = mixing.clamp(int(index), 0, 16)
        with self._lock:
            self._pending.append(
                "P {0} {1} {2} {3}\n".format(
                    index,
                    mixing.clamp(int(red), 0, 255),
                    mixing.clamp(int(green), 0, 255),
                    mixing.clamp(int(blue), 0, 255),
                )
            )

    def snapshot(self):
        """Return a dictionary describing the link, for the web page status line."""
        with self._lock:
            status = dict(self.last_status) if self.last_status else None
            age = self.clock() - self.last_status_at if self.last_status_at else None
            return {
                "stance_request": self._stance_request,
                "connected": self.connected,
                "port": self.port_name,
                "enabled": self._enabled,
                "commanded": list(self._current),
                "target": list(self._target),
                "status": status,
                "status_age": age,
                "fresh": age is not None and age < STALE_STATUS_SECONDS,
                "error": self.last_error,
                "commands_sent": self.commands_sent,
            }

    # -- thread internals -------------------------------------------------

    def _open(self):
        """Try to open the port.  Returns True on success."""
        if serial is None:
            return False
        device = find_port(self.requested_port)
        if device is None:
            self._note_error("no USB CDC device found for the KB2040")
            return False
        try:
            self._serial = serial.Serial(device, self.baud_rate, timeout=READ_TIMEOUT)
        except (OSError, serial.SerialException) as error:
            self._note_error("cannot open {0}: {1}".format(device, error))
            return False
        self._serial.reset_input_buffer()
        self.port_name = device
        self.connected = True
        self.last_error = None
        LOGGER.info("KB2040 link open on %s", device)
        # Re-assert the enable state the web page last asked for.
        with self._lock:
            enabled = self._enabled
            self._pending.append("E {0}\n".format(1 if enabled else 0))
        return True

    def _note_error(self, text):
        """Record and log a link problem once per change."""
        if text != self.last_error:
            LOGGER.error("%s", text)
        self.last_error = text
        self.connected = False

    def _close_port(self):
        """Close the port if it is open."""
        if self._serial is not None:
            try:
                self._serial.close()
            except OSError as error:
                LOGGER.warning("closing the serial port failed: %s", error)
            self._serial = None
        self.connected = False

    def _read_lines(self):
        """Read and interpret whatever the controller has sent."""
        while self._serial.in_waiting:
            raw = self._serial.readline()
            if not raw:
                break
            line = raw.decode("utf-8", "replace").strip()
            if not line:
                continue
            status = mixing.parse_status(line)
            stance = stance_link.parse_stance_line(line) if status is None else None
            if status is not None:
                with self._lock:
                    self.last_status = status
                    self.last_status_at = self.clock()
            elif stance is not None:
                with self._lock:
                    self.last_stance = stance
                    self.last_stance_at = self.clock()
            elif line.startswith("err"):
                LOGGER.warning("KB2040: %s", line)
                self.last_error = line
            elif line != "ok":
                LOGGER.info("KB2040 said: %s", line)

    def _send_pending(self):
        """Write any queued non-drive lines."""
        with self._lock:
            queued = self._pending
            self._pending = []
        for line in queued:
            self._serial.write(line.encode("ascii"))

    def _send_drive(self):
        """Ramp towards the target and write one ``M`` line and one ``T`` line."""
        with self._lock:
            self._current = mixing.ramp_channels(
                self._current, self._target, mixing.RAMP_PER_COMMAND
            )
            values = list(self._current)
            request = self._stance_request
        self._serial.write(mixing.format_drive(*values).encode("ascii"))
        self._serial.write(stance_link.format_request(request).encode("ascii"))
        self.commands_sent += 1

    def _run(self):
        """Thread body: keep the port open and the command stream flowing."""
        next_command = time.monotonic()
        while not self._stop_event.is_set():
            if self._serial is None:
                if not self._open():
                    self._stop_event.wait(RECONNECT_SECONDS)
                    continue
                next_command = time.monotonic()
            try:
                self._read_lines()
                self._send_pending()
                self._send_drive()
            except (OSError, ValueError) as error:
                self._note_error("serial link lost: {0}".format(error))
                self._close_port()
                self._stop_event.wait(RECONNECT_SECONDS)
                continue
            next_command += mixing.COMMAND_PERIOD
            delay = next_command - time.monotonic()
            if delay > 0:
                self._stop_event.wait(delay)
            else:
                next_command = time.monotonic()

        # Leaving: put the robot down gently rather than letting the heartbeat
        # time out with the last duty still applied.
        if self._serial is not None:
            try:
                self._serial.write(b"T 0\n")
                self._serial.write(b"S\n")
                self._serial.write(b"E 0\n")
                self._serial.flush()
            except OSError as error:
                LOGGER.warning("could not send the final stop: %s", error)
            self._close_port()
        LOGGER.info("serial link thread finished after %d commands", self.commands_sent)
