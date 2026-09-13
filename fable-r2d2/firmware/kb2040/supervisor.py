"""Hardware-free controller core for the fable-r2d2 KB2040 (revision D).

``code.py`` owns the pins and the USB port and hands this class a hardware
object.  ``test_stance.py`` hands it a simulated plant instead.  Everything that
decides what moves lives here: the serial protocol, the Pi heartbeat, the drive
ramp, the ground-drive and dome interlocks, and the stance state machine.

Hardware object (duck typed; ``code.Hardware`` and ``test_stance.Plant``):

    set_enabled(flag)                  arm or disarm the ground and dome motors
    apply_drive(enabled, channels)     four permille values: left, right, centre, head
    coast_all()                        release the ground and dome motors now
    fill(r, g, b) -> bool              every NeoPixel; False when unavailable
    set_pixel(i, r, g, b) -> bool      one NeoPixel; False when unavailable
    index_detected() -> bool           dome home sensor
    read_position_mv() -> float|None   actuator wiper, millivolts at KB2040 A0
    read_lock_contacts() -> [(no, nc)] one pair per shoulder lock, left first;
                                       True = that switch contact is closed
    read_battery_mv() -> float|None    pack millivolts from the KB2040 A1 divider
    drive_actuator(percent)            -100 retract .. 0 coast .. +100 extend
    set_release_pulses([us, ...])      one release-servo pulse per lock, 0 = no pulse
"""

import protocol
import stance

LEFT, RIGHT, CENTRE, HEAD = 0, 1, 2, 3

STATUS_PERIOD_MS = 200
"""Unsolicited ``st`` and ``ss`` cadence."""

MAX_LINE = 256
"""A partial line longer than this is noise and is discarded."""


class Supervisor:
    """Serial protocol, heartbeat, drive interlocks and the stance state machine."""

    def __init__(self, hal, write, now, limits=None):
        self.hal = hal
        self.write = write
        self.limits = limits if limits is not None else stance.Limits()
        problems = self.limits.problems()
        if problems:
            raise ValueError("inconsistent mechanism constants: " + "; ".join(problems))
        self.stance = stance.Stance(self.limits)
        self.lock = stance.LockSet()
        self.battery = stance.BatteryGuard()
        self.servos = [stance.ReleaseServo(stance.RELEASE_US[index], stance.ENGAGE_US[index])
                       for index in range(len(stance.LOCK_NAMES))]
        self.drive = protocol.DriveState(protocol.RAMP_STEP)
        self.enabled = False
        self.timed_out = False
        self.buffer = ""
        self.last_command_ms = now
        self.request = stance.REQUEST_NONE
        self.last_request_ms = None
        self.last_status_ms = now - STATUS_PERIOD_MS
        self.drive_idle = True
        self.hal.set_enabled(False)

    # -- output -------------------------------------------------------------

    def send(self, text):
        self.write(text)

    def send_status(self, now):
        current = self.drive.current
        self.send(protocol.format_status(self.enabled, current[LEFT], current[RIGHT],
                                         current[CENTRE], current[HEAD],
                                         self.hal.index_detected()))
        s = self.stance
        two = s.blocked(stance.REQUEST_TWO_FOOT, now, self.drive_idle)
        three = s.blocked(stance.REQUEST_THREE_FOOT, now, self.drive_idle)
        self.send(protocol.format_stance(
            s.state, s.phase, s.fault, s.position_mm, self.lock.code(), self.battery.pack_mv,
            s.drive_allowed(), s.head_allowed(), two is None, three is None,
            s.reason, two or "", three or ""))
        self.last_status_ms = now

    # -- input --------------------------------------------------------------

    def feed(self, text, now):
        """Accept raw serial text and execute every complete line."""
        self.buffer += text
        lines, self.buffer = protocol.split_lines(self.buffer)
        if len(self.buffer) > MAX_LINE:
            self.buffer = ""
            self.send(protocol.format_error("input line too long, discarded"))
        for line in lines:
            self.handle(line, now)

    def handle(self, line, now):
        try:
            kind, args = protocol.parse_command(line)
        except protocol.CommandError as error:
            self.send(protocol.format_error(str(error)))
            return

        self.last_command_ms = now
        self.timed_out = False

        if kind == "M":
            self._drive_command(args, now)
        elif kind == "S":
            self.drive.hard_stop()
            self.stance.interrupt(now, "stop command; stance held")
            self._push_drive()
            self.send(protocol.format_ok())
        elif kind == "E":
            self.set_enabled(args[0] == 1, now)
            self.send(protocol.format_ok())
        elif kind == "L":
            if self.hal.fill(args[0], args[1], args[2]):
                self.send(protocol.format_ok())
            else:
                self.send(protocol.format_error("neopixel library missing"))
        elif kind == "P":
            if self.hal.set_pixel(args[0], args[1], args[2], args[3]):
                self.send(protocol.format_ok())
            else:
                self.send(protocol.format_error("neopixel library missing"))
        elif kind == "?":
            self.send_status(now)
        elif kind == "T":
            self.request = args[0]
            self.last_request_ms = now
            self.send(protocol.format_ok())
        elif kind == "C":
            if self.stance.state != stance.FAULT:
                self.send(protocol.format_error("no stance fault latched"))
            elif self.stance.clear_fault(now):
                self.send(protocol.format_ok())
            else:
                self.send(protocol.format_error("fault not cleared: " + self.stance.reason))

    def _drive_command(self, values, now):
        values = list(values)
        s = self.stance
        refused = []
        if not s.drive_allowed() and (values[LEFT] or values[RIGHT] or values[CENTRE]):
            values[LEFT] = values[RIGHT] = values[CENTRE] = 0
            refused.append("ground drive")
        if not s.head_allowed() and values[HEAD]:
            values[HEAD] = 0
            refused.append("dome")
        self.drive.set_targets(values)
        if not refused:
            self.send(protocol.format_ok())
            return
        if s.transitioning():
            why = "stance change in progress"
        elif s.state == stance.TWO_FOOT:
            why = "the two-foot stance is stationary"
        elif s.state == stance.FAULT:
            why = "stance fault latched"
        else:
            why = "stance not locked: " + s.reason
        s.interrupt(now, "drive or dome command during stance change; stance held")
        self.send(protocol.format_error("drive refused ({0}): {1}".format(" and ".join(refused), why)))

    def set_enabled(self, flag, now):
        if not flag:
            self.drive.hard_stop()
            self.stance.interrupt(now, "motors disarmed; stance held")
        self.enabled = bool(flag)
        self.hal.set_enabled(self.enabled)
        self._push_drive()

    # -- control tick -------------------------------------------------------

    def _push_drive(self):
        current = self.drive.current
        if self.enabled:
            self.hal.apply_drive(True, list(current))
        else:
            self.hal.apply_drive(False, [0, 0, 0, 0])

    def _gate_drive(self):
        s = self.stance
        if not s.drive_allowed():
            for index in (LEFT, RIGHT, CENTRE):
                self.drive.target[index] = 0
                self.drive.current[index] = 0
        if not s.head_allowed():
            self.drive.target[HEAD] = 0
            self.drive.current[HEAD] = 0

    def tick(self, now):
        """One 10 ms control tick.  Serial input must already have been fed."""
        position = stance.pot_position_mm(self.hal.read_position_mv(), self.limits)
        self.lock.update(now, self.hal.read_lock_contacts())
        power = self.battery.update(now, self.hal.read_battery_mv())
        heartbeat = now - self.last_command_ms <= protocol.HEARTBEAT_MS
        request_fresh = (self.last_request_ms is not None
                         and now - self.last_request_ms <= protocol.HEARTBEAT_MS)
        request = self.request if request_fresh else stance.REQUEST_NONE
        targets_zero = not (self.drive.target[0] or self.drive.target[1]
                            or self.drive.target[2] or self.drive.target[3])
        self.drive_idle = targets_zero and not self.drive.is_moving()

        # Both lock switches need their debounce and the battery one reading
        # before the state machine may decide anything; until then it is "starting".
        if self.lock.settled() and self.battery.pack_mv is not None:
            sample = stance.Sample(position, self.lock.valid(), self.lock.all_engaged(),
                                   self.lock.any_engaged(), power, heartbeat, self.enabled)
            self.stance.tick(now, sample, request, self.drive_idle, request_fresh)

        if not heartbeat:
            if not self.timed_out:
                self.timed_out = True
                self.drive.hard_stop()
                self.hal.coast_all()
                self.send(protocol.format_error("heartbeat timeout, motors coasted"))
        else:
            self._gate_drive()
            self.drive.tick()
            self._push_drive()

        self.hal.drive_actuator(self.stance.actuator)
        self.hal.set_release_pulses([servo.update(now, self.stance.release)
                                     for servo in self.servos])

        if now - self.last_status_ms >= STATUS_PERIOD_MS:
            self.send_status(now)
