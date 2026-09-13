"""fable-r2d2 Raspberry Pi control server.

Serves the phone control page over Wi-Fi, carries the joystick over a WebSocket,
mixes it into three foot channels plus the head channel, and hands the result to
the KB2040 over USB CDC.  It also animates the head displays and plays the sound
clips.

Run:

    python3 firmware/pi/server.py --host 0.0.0.0 --port 8080

Options are also read from the environment so the systemd unit does not need a
long command line:

    R2D2_HOST, R2D2_PORT, R2D2_SERIAL_PORT, R2D2_NO_DISPLAYS, R2D2_NO_BATTERY
"""

import argparse
import asyncio
import json
import logging
import os
import sys
import time

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import mixing
from audio import SoundPlayer
from battery import BatteryMonitor
from displays import DisplayWorker
from serial_link import SerialLink
from stance_link import STANCE_LEASE_SECONDS, StanceControl

try:
    from aiohttp import WSMsgType, web
except ImportError as error:  # pragma: no cover - depends on the host
    raise SystemExit(
        "aiohttp is required: pip install -r firmware/pi/requirements.txt ({0})".format(error)
    )

LOGGER = logging.getLogger("r2d2.server")

HERE = os.path.dirname(os.path.abspath(__file__))
STATIC_DIR = os.path.join(HERE, "static")

STATUS_HZ = 5
"""Status frames a second pushed to every connected page."""

CLIENT_TIMEOUT = 0.5
"""Stop driving if the page has said nothing for this long."""

BATTERY_PERIOD = 5.0
"""Seconds between battery readings; the ADC is slow and the pack is not."""


class Robot:
    """The control state shared by every connected page."""

    def __init__(self, link, player, battery):
        self.link = link
        self.player = player
        self.battery = battery
        self.stance = StanceControl(link)

        self.speed_cap = mixing.SPEED_CAP_DEFAULT
        self.head_duty = mixing.HEAD_DUTY_DEFAULT
        self.head_direction = 0
        self.x = 0.0
        self.y = 0.0
        self.enabled = False
        self.last_client_input = 0.0
        self.nudge_until = 0.0
        self.nudge_direction = 0

        self.battery_state = {"available": False, "volts": None, "charge": None,
                              "critical": False, "reason": None}
        self._battery_checked = 0.0

    # -- commands from the page ------------------------------------------

    def set_joystick(self, x, y):
        """Record a joystick position and push the mixed channels down the link."""
        self.x = mixing.clamp(float(x), -1.0, 1.0)
        self.y = mixing.clamp(float(y), -1.0, 1.0)
        if not self.stance.drive_permitted():
            # Refused: during a stance change, on two feet, or in an unknown or
            # fault state.  The KB2040 refuses it again on its own.
            self.x = 0.0
            self.y = 0.0
        self.last_client_input = time.monotonic()
        self.push_drive()

    def set_stance(self, target):
        """The page holds (2, 3) or releases (0) a stance control.  False if ignored."""
        return self.stance.request(target)

    def set_speed_cap(self, value):
        """Change the global speed cap (0.20 to 1.00)."""
        self.speed_cap = mixing.clamp(float(value), mixing.SPEED_CAP_MIN, mixing.SPEED_CAP_MAX)
        self.push_drive()

    def set_head_duty(self, value):
        """Change the duty used for head spin and nudge."""
        self.head_duty = mixing.clamp(float(value), 0.0, 1.0)
        self.push_drive()

    def set_head_direction(self, direction):
        """Spin the dome continuously: -1, 0 or +1."""
        self.head_direction = int(mixing.clamp(int(direction), -1, 1))
        self.last_client_input = time.monotonic()
        self.push_drive()

    def nudge_head(self, direction):
        """Spin the dome for ``mixing.HEAD_NUDGE_SECONDS`` and stop."""
        self.nudge_direction = int(mixing.clamp(int(direction), -1, 1))
        self.nudge_until = time.monotonic() + mixing.HEAD_NUDGE_SECONDS
        self.last_client_input = time.monotonic()
        self.push_drive()

    def set_enabled(self, enabled):
        """Raise or drop the DRV8833 enable line."""
        self.enabled = bool(enabled)
        if not self.enabled:
            self.x = 0.0
            self.y = 0.0
            self.head_direction = 0
            self.nudge_until = 0.0
        self.link.set_enabled(self.enabled)
        self.push_drive()

    def stop(self):
        """Emergency stop: zero everything and tell the controller at once."""
        self.x = 0.0
        self.y = 0.0
        self.head_direction = 0
        self.nudge_until = 0.0
        self.nudge_direction = 0
        self.stance.stop()
        self.link.stop()
        LOGGER.warning("emergency stop")

    def play(self, name):
        """Play a sound clip by name."""
        return self.player.play(name)

    def set_lights(self, red, green, blue):
        """Set every dome pixel."""
        self.link.set_all_pixels(red, green, blue)

    # -- periodic --------------------------------------------------------

    def current_head(self):
        """The head channel permille this instant, nudge included."""
        if time.monotonic() < self.nudge_until:
            return mixing.head_permille(self.nudge_direction, self.head_duty)
        if self.nudge_direction and time.monotonic() >= self.nudge_until:
            self.nudge_direction = 0
        return mixing.head_permille(self.head_direction, self.head_duty)

    def push_drive(self):
        """Mix the current inputs and hand them to the serial link."""
        left, right, centre = mixing.drive_permille(self.x, self.y, self.speed_cap)
        self.link.set_drive(*self.stance.gate(left, right, centre, self.current_head()))

    def tick(self):
        """Called at the status rate: apply the client watchdog and refresh sensors."""
        now = time.monotonic()
        self.stance.tick()
        moving = self.x or self.y or self.head_direction or self.nudge_direction
        if moving and now - self.last_client_input > CLIENT_TIMEOUT:
            LOGGER.warning("no input for %.1f s, stopping", now - self.last_client_input)
            self.x = 0.0
            self.y = 0.0
            self.head_direction = 0
            self.nudge_direction = 0
            self.nudge_until = 0.0
        self.push_drive()

        if now - self._battery_checked >= BATTERY_PERIOD:
            self._battery_checked = now
            self.battery_state = self.battery.snapshot()

    def snapshot(self):
        """Everything the page needs for its status line."""
        link = self.link.snapshot()
        return {
            "type": "status",
            "link": link,
            "battery": self.battery_state,
            "speed_cap": self.speed_cap,
            "head_duty": self.head_duty,
            "enabled": self.enabled,
            "joystick": {"x": round(self.x, 3), "y": round(self.y, 3)},
            "head_direction": self.head_direction,
            "stance": self.stance.snapshot(),
        }

    def display_status(self):
        """Compact status for the radar eye text."""
        link = self.link.snapshot()
        return {
            "connected": link["connected"],
            "fresh": link["fresh"],
            "commanded": link["commanded"],
            "speed_cap": self.speed_cap,
        }


# ---------------------------------------------------------------------------
# HTTP and WebSocket
# ---------------------------------------------------------------------------


async def index(request):
    """Serve the control page."""
    return web.FileResponse(os.path.join(STATIC_DIR, "index.html"))


async def websocket_handler(request):
    """One connected phone."""
    socket = web.WebSocketResponse(heartbeat=10.0)
    await socket.prepare(request)

    robot = request.app["robot"]
    clients = request.app["clients"]
    clients.add(socket)
    peer = request.remote
    LOGGER.info("page connected from %s (%d open)", peer, len(clients))

    await socket.send_str(json.dumps({
        "type": "hello",
        "sounds": robot.player.names(),
        "audio_backend": robot.player.backend,
        "speed_cap": robot.speed_cap,
        "head_duty": robot.head_duty,
        "speed_cap_min": mixing.SPEED_CAP_MIN,
        "speed_cap_max": mixing.SPEED_CAP_MAX,
        "command_hz": mixing.COMMAND_HZ,
        "stance_lease_ms": int(STANCE_LEASE_SECONDS * 1000),
    }))

    try:
        async for message in socket:
            if message.type == WSMsgType.TEXT:
                await handle_message(robot, socket, message.data)
            elif message.type == WSMsgType.ERROR:
                LOGGER.warning("websocket error from %s: %s", peer, socket.exception())
    finally:
        clients.discard(socket)
        LOGGER.info("page disconnected from %s (%d open)", peer, len(clients))
        if not clients:
            # The specification is explicit: when the page goes away, stop.
            robot.stop()
    return socket


async def handle_message(robot, socket, raw):
    """Act on one JSON message from the page."""
    try:
        message = json.loads(raw)
    except ValueError:
        LOGGER.warning("ignoring malformed message: %r", raw[:120])
        return
    kind = message.get("type")

    if kind == "drive":
        robot.set_joystick(message.get("x", 0.0), message.get("y", 0.0))
    elif kind == "head":
        robot.set_head_direction(message.get("direction", 0))
    elif kind == "nudge":
        robot.nudge_head(message.get("direction", 1))
    elif kind == "cap":
        robot.set_speed_cap(message.get("value", mixing.SPEED_CAP_DEFAULT))
    elif kind == "head_duty":
        robot.set_head_duty(message.get("value", mixing.HEAD_DUTY_DEFAULT))
    elif kind == "enable":
        robot.set_enabled(bool(message.get("value", False)))
    elif kind == "stop":
        robot.stop()
    elif kind == "sound":
        name = message.get("name", "")
        if not robot.play(name):
            await socket.send_str(json.dumps({
                "type": "notice",
                "text": "could not play {0}".format(name),
            }))
    elif kind == "lights":
        robot.set_lights(message.get("r", 0), message.get("g", 0), message.get("b", 0))
    elif kind == "stance":
        try:
            accepted = robot.set_stance(message.get("target", 0))
        except (TypeError, ValueError):
            LOGGER.warning("ignoring bad stance target %r", message.get("target"))
            return
        if not accepted:
            await socket.send_str(json.dumps({
                "type": "notice",
                "text": "stance request ignored: release the stance control, then press again",
            }))
    elif kind == "clear_fault":
        robot.stance.clear_fault()
    elif kind == "ping":
        robot.last_client_input = time.monotonic()
    else:
        LOGGER.warning("unknown message type %r", kind)


async def status_broadcaster(app):
    """Push a status frame to every page ``STATUS_HZ`` times a second."""
    robot = app["robot"]
    clients = app["clients"]
    period = 1.0 / STATUS_HZ
    try:
        while True:
            robot.tick()
            if clients:
                payload = json.dumps(robot.snapshot())
                for socket in list(clients):
                    if socket.closed:
                        clients.discard(socket)
                        continue
                    try:
                        await socket.send_str(payload)
                    except (ConnectionResetError, RuntimeError) as error:
                        LOGGER.info("dropping a page: %s", error)
                        clients.discard(socket)
            await asyncio.sleep(period)
    except asyncio.CancelledError:
        LOGGER.info("status broadcaster stopped")
        raise


async def on_startup(app):
    """Start the background workers once the loop is running."""
    app["broadcaster"] = asyncio.create_task(status_broadcaster(app))


async def on_cleanup(app):
    """Stop everything in the right order: motors first."""
    robot = app["robot"]
    robot.stop()
    task = app.get("broadcaster")
    if task is not None:
        task.cancel()
        try:
            await task
        except asyncio.CancelledError:
            pass
    robot.link.close()
    app["displays"].close()
    robot.player.close()


def build_app(serial_port=None, use_displays=True, use_battery=True):
    """Create the aiohttp application with every worker attached."""
    link = SerialLink(port=serial_port)
    link.start()

    player = SoundPlayer()
    battery = BatteryMonitor() if use_battery else _DisabledBattery()
    robot = Robot(link, player, battery)

    displays = DisplayWorker(status_provider=robot.display_status)
    if use_displays:
        displays.start()
    else:
        LOGGER.info("head displays disabled by configuration")

    app = web.Application()
    app["robot"] = robot
    app["clients"] = set()
    app["displays"] = displays
    app.router.add_get("/", index)
    app.router.add_get("/ws", websocket_handler)
    app.router.add_static("/static/", STATIC_DIR, name="static")
    app.on_startup.append(on_startup)
    app.on_cleanup.append(on_cleanup)
    return app


class _DisabledBattery:
    """Stand-in used when battery sensing is switched off on the command line."""

    def snapshot(self):
        """Report the sensor as absent, with the reason."""
        return {
            "available": False,
            "volts": None,
            "charge": None,
            "critical": False,
            "reason": "battery sensing disabled on the command line",
        }


def parse_arguments(argv=None):
    """Read the command line, falling back to the environment."""
    parser = argparse.ArgumentParser(description="fable-r2d2 control server")
    parser.add_argument("--host", default=os.environ.get("R2D2_HOST", "0.0.0.0"))
    parser.add_argument("--port", type=int, default=int(os.environ.get("R2D2_PORT", "8080")))
    parser.add_argument("--serial-port", default=os.environ.get("R2D2_SERIAL_PORT"))
    parser.add_argument("--no-displays", action="store_true",
                        default=bool(os.environ.get("R2D2_NO_DISPLAYS")))
    parser.add_argument("--no-battery", action="store_true",
                        default=bool(os.environ.get("R2D2_NO_BATTERY")))
    parser.add_argument("--log-level", default=os.environ.get("R2D2_LOG_LEVEL", "INFO"))
    return parser.parse_args(argv)


def main(argv=None):
    """Entry point."""
    options = parse_arguments(argv)
    logging.basicConfig(
        level=getattr(logging, options.log_level.upper(), logging.INFO),
        format="%(asctime)s %(levelname)-7s %(name)-14s %(message)s",
    )
    app = build_app(
        serial_port=options.serial_port,
        use_displays=not options.no_displays,
        use_battery=not options.no_battery,
    )
    LOGGER.info("serving the control page on http://%s:%d/", options.host, options.port)
    web.run_app(app, host=options.host, port=options.port, print=None)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
