"""Revision D stance interlock for the fable-r2d2 KB2040.  Hardware-free.

The centre leg is moved by a 12 V linear actuator with a potentiometer.  The
actuator stroke sets both the centre-leg position and the body tilt:

    two-foot stance    retracted end, body tilt 0 deg, centre wheels lifted,
                       stationary only
    three-foot stance  deployed end, body tilt 18 deg, centre foot to the front

A spring-return shoulder lock pin seats in a receiver at each endpoint.  A
servo pulls the pin (the "release").  An SPDT lock switch wired NO + NC reports
whether the pin is seated.  The lock state always comes from that switch and is
never inferred from actuator position.

This module has no CircuitPython imports.  ``supervisor.py`` feeds it sensor
samples and applies its outputs; ``test_stance.py`` runs it against a simulated
plant on CPython.  Port of the state machine in fable-r2d3
``firmware/include/stance.h``, reduced to this robot's single-segment stroke
(no separate foot-lift phase) and without hardware travel-limit switches.

States     THREE_FOOT, RETRACTING, TWO_FOOT, DEPLOYING, HELD, FAULT
Phases     UNLOCKING  actuator stopped, release pulled, wait for the switch
           TRAVEL     actuator at full duty toward the far receiver; the
                      release drops once the pin is clear of the departure
                      receiver so the spring rides the pin on the ring face
           LOCKING    settle, then creep through the receiver until the switch
                      reads seated
"""

# ===== MECHANISM CONSTANTS =====
# Every value that depends on the chosen actuator, lock and servo lives in this
# block.  Status: PROVISIONAL (2026-09-12).  Reference parts: Actuonix
# P16-100-256-12-P, Omron SS-01GL wired NO + NC, TowerPro MG995 release.
# Replace the whole block together when stance-mechanism reports its values.

ACTUATOR_PART = "Actuonix P16-100-256-12-P"
ACTUATOR_STROKE_MM = 100.0          # full mechanical stroke
ACTUATOR_NO_LOAD_SPEED_MM_S = 4.8   # datasheet, 12 V
ACTUATOR_STALL_A = 1.0              # at 12 V
ACTUATOR_REST_PER_RUN = 4           # 20 % duty: 4 ms rest per ms of travel

TWO_FOOT_MM = 5.0                   # stroke at the two-foot receiver (tilt 0 deg)
THREE_FOOT_MM = 95.0                # stroke at the three-foot receiver (tilt 18 deg)
TWO_FOOT_TILT_DEG = 0.0
THREE_FOOT_TILT_DEG = 18.0

POT_ZERO_MV = 0.0                   # wiper millivolts at stroke 0 (2.2 k top resistor)
POT_FULL_MV = 2750.0                # wiper millivolts at full stroke, 11 k pot
POT_MIN_VALID_MV = 40.0             # open wiper or open ref+ reads below this
POT_MAX_VALID_MV = 3000.0           # open ref- reads above this

STOP_TOLERANCE_MM = 0.4             # a movement goal counts as reached inside this band
HOLD_TOLERANCE_MM = 2.5             # a parked stance faults if the actuator drifts further
LOCK_WINDOW_MM = 2.5                # band round each receiver where either lock state is legal
SEEK_MM = 1.5                       # TRAVEL stops this far before the far receiver
OVERSHOOT_MM = 0.8                  # LOCKING creeps this far past the nominal receiver
OVERTRAVEL_MM = 1.5                 # beyond an endpoint by more than this is a fault
RELEASE_CLEAR_MM = 8.0              # stroke off the departure receiver before the release drops
PROGRESS_MM = 0.5                   # stall: less than this ...
PROGRESS_MS = 750                   # ... within this many ms while driven
TRAVEL_TIMEOUT_MS = 40000           # per phase
LOCK_SETTLE_MS = 400                # pin drop time before the LOCKING creep starts
LOCK_TIMEOUT_MS = 1500              # pin must leave or enter a receiver within this
REVERSE_DWELL_MS = 150              # stopped time before the actuator reverses
SEEK_DUTY_PERCENT = 60              # LOCKING creep duty

LOCK_SEATED_CONTACT = "NO"          # switch contact that closes when the pin is seated
LOCK_LEGAL_MS = 30                  # debounce for a legal NO/NC pair
LOCK_ILLEGAL_MS = 150               # both open or both closed must persist this long

RELEASE_US = 1000                   # servo pulse that pulls the pin
ENGAGE_US = 1311                    # servo pulse that lets the spring seat the pin
ENGAGE_HOLD_MS = 1000               # engage pulse is held this long, then the servo goes limp
SERVO_PERIOD_US = 20000             # 50 Hz

# ===== END MECHANISM CONSTANTS =====

# Battery sense on KB2040 A1: 12 V bus -> 100 k -> A1 node -> 15 k -> KB2040 GND.
BATTERY_TOP_OHMS = 100000
BATTERY_BOTTOM_OHMS = 15000
BATTERY_CUTOFF_MV = 11200           # below this for BATTERY_LOW_MS: no power
BATTERY_REARM_MV = 12000            # power returns only above this for BATTERY_LOW_MS
BATTERY_MAX_MV = 15200              # above this the reading is not a battery (fault)
BATTERY_LOW_MS = 500
ADC_REFERENCE_MV = 3300
ADC_FULL_SCALE = 65535

# States, phases, faults and requests as short ASCII words for the serial line.
THREE_FOOT = "THREE_FOOT"
RETRACTING = "RETRACTING"
TWO_FOOT = "TWO_FOOT"
DEPLOYING = "DEPLOYING"
HELD = "HELD"
FAULT = "FAULT"
STATES = (THREE_FOOT, RETRACTING, TWO_FOOT, DEPLOYING, HELD, FAULT)

NO_PHASE = "NONE"
UNLOCKING = "UNLOCKING"
TRAVEL = "TRAVEL"
LOCKING = "LOCKING"
PHASES = (NO_PHASE, UNLOCKING, TRAVEL, LOCKING)

NO_FAULT = "NONE"
POWER = "POWER"
FEEDBACK = "FEEDBACK"
LOCK_SENSOR = "LOCK_SENSOR"
STALL = "STALL"
TRAVEL_TIMEOUT = "TRAVEL_TIMEOUT"
LOCK_TIMEOUT = "LOCK_TIMEOUT"
LOCK_DISAGREES = "LOCK_DISAGREES"
DRIFT = "DRIFT"
OVERTRAVEL = "OVERTRAVEL"
REVERSED_FEEDBACK = "REVERSED_FEEDBACK"
FAULTS = (NO_FAULT, POWER, FEEDBACK, LOCK_SENSOR, STALL, TRAVEL_TIMEOUT, LOCK_TIMEOUT,
          LOCK_DISAGREES, DRIFT, OVERTRAVEL, REVERSED_FEEDBACK)

REQUEST_NONE = 0
REQUEST_TWO_FOOT = 2
REQUEST_THREE_FOOT = 3

READY_TWO = "standing on two feet; shoulder lock engaged"
READY_THREE = "on three feet; shoulder lock engaged; ready to drive"


class Limits:
    """The mechanism constants as one object, so tests can build variants."""

    def __init__(self, **overrides):
        self.two_foot_mm = TWO_FOOT_MM
        self.three_foot_mm = THREE_FOOT_MM
        self.stroke_mm = ACTUATOR_STROKE_MM
        self.pot_zero_mv = POT_ZERO_MV
        self.pot_full_mv = POT_FULL_MV
        self.pot_min_valid_mv = POT_MIN_VALID_MV
        self.pot_max_valid_mv = POT_MAX_VALID_MV
        self.stop_tolerance_mm = STOP_TOLERANCE_MM
        self.hold_tolerance_mm = HOLD_TOLERANCE_MM
        self.lock_window_mm = LOCK_WINDOW_MM
        self.seek_mm = SEEK_MM
        self.overshoot_mm = OVERSHOOT_MM
        self.overtravel_mm = OVERTRAVEL_MM
        self.release_clear_mm = RELEASE_CLEAR_MM
        self.progress_mm = PROGRESS_MM
        self.progress_ms = PROGRESS_MS
        self.travel_timeout_ms = TRAVEL_TIMEOUT_MS
        self.lock_settle_ms = LOCK_SETTLE_MS
        self.lock_timeout_ms = LOCK_TIMEOUT_MS
        self.reverse_dwell_ms = REVERSE_DWELL_MS
        self.rest_per_run = ACTUATOR_REST_PER_RUN
        self.seek_duty_percent = SEEK_DUTY_PERCENT
        for name in overrides:
            if not hasattr(self, name):
                raise AttributeError("unknown limit " + name)
            setattr(self, name, overrides[name])

    def mm_for_mv(self, mv):
        """Stroke in mm for a wiper voltage, ignoring the validity window."""
        return (mv - self.pot_zero_mv) * self.stroke_mm / (self.pot_full_mv - self.pot_zero_mv)

    def mv_for_mm(self, mm):
        """Wiper voltage for a stroke, for the simulated plant and for commissioning."""
        return self.pot_zero_mv + mm * (self.pot_full_mv - self.pot_zero_mv) / self.stroke_mm

    def problems(self):
        """Return a list of inconsistencies.  An empty list means the set is usable."""
        found = []
        tol = self.stop_tolerance_mm

        def need(condition, text):
            if not condition:
                found.append(text)

        need(self.pot_full_mv > self.pot_zero_mv, "pot full mV must exceed zero mV")
        need(self.mm_for_mv(self.pot_min_valid_mv) < self.two_foot_mm - self.overtravel_mm,
             "pot minimum valid reading must lie below the two-foot overtravel limit")
        need(self.mm_for_mv(self.pot_max_valid_mv) > self.three_foot_mm + self.overtravel_mm,
             "pot maximum valid reading must lie above the three-foot overtravel limit")
        need(self.seek_mm + tol <= self.lock_window_mm, "seek point must sit inside the lock window")
        need(self.overshoot_mm + tol < self.lock_window_mm, "overshoot must stay inside the lock window")
        need(self.overshoot_mm + tol < self.overtravel_mm, "overshoot must stay short of overtravel")
        need(self.lock_window_mm <= self.hold_tolerance_mm, "lock window must not exceed hold tolerance")
        need(self.two_foot_mm + self.lock_window_mm < self.three_foot_mm - self.release_clear_mm,
             "retract release drop must lie outside the two-foot lock window")
        need(self.three_foot_mm - self.lock_window_mm > self.two_foot_mm + self.release_clear_mm,
             "deploy release drop must lie outside the three-foot lock window")
        need(self.release_clear_mm > self.lock_window_mm, "release must stay pulled across the lock window")
        need(self.progress_mm > 0 and self.progress_ms > 0, "stall detection needs positive values")
        need(self.travel_timeout_ms > self.progress_ms, "travel timeout must exceed the stall window")
        need(self.lock_timeout_ms > 0 and self.lock_settle_ms >= 0, "lock timings must be positive")
        need(0 < self.seek_duty_percent <= 100, "seek duty must be 1..100 percent")
        return found


def pot_position_mm(mv, limits):
    """Return the stroke in mm, or ``None`` when the wiper reading is not credible."""
    if mv is None:
        return None
    if mv < limits.pot_min_valid_mv or mv > limits.pot_max_valid_mv:
        return None
    return limits.mm_for_mv(mv)


def adc_to_mv(raw):
    """RP2040 ``analogio.AnalogIn.value`` (0..65535) to millivolts."""
    return raw * ADC_REFERENCE_MV / ADC_FULL_SCALE


def pack_mv_from_node(node_mv, top=BATTERY_TOP_OHMS, bottom=BATTERY_BOTTOM_OHMS):
    """Battery millivolts from the divider node voltage."""
    return node_mv * (top + bottom) / bottom


def servo_duty(pulse_us, period_us=SERVO_PERIOD_US):
    """16 bit ``pwmio`` duty for a servo pulse; 0 means no pulse (servo limp)."""
    if pulse_us <= 0:
        return 0
    return int(pulse_us * 65535 // period_us)


class ContactPair:
    """SPDT lock switch: COM to ground, NO and NC each to a pulled-up input.

    Exactly one closed contact is a legal reading.  Both open (broken COM or a
    broken wire) or both closed (a short) is invalid once it persists longer
    than a normal changeover.  A legal pair must be stable for ``legal_ms``.
    """

    def __init__(self, legal_ms=LOCK_LEGAL_MS, illegal_ms=LOCK_ILLEGAL_MS,
                 seated_contact=LOCK_SEATED_CONTACT):
        if seated_contact not in ("NO", "NC"):
            raise ValueError("seated_contact must be NO or NC")
        self.legal_ms = legal_ms
        self.illegal_ms = illegal_ms
        self.seated_contact = seated_contact
        self.valid = False
        self.engaged = False
        self.settled = False
        self._candidate = None
        self._since = 0

    def update(self, now, no_closed, nc_closed):
        code = (1 if no_closed else 0) | (2 if nc_closed else 0)
        if code != self._candidate:
            self._candidate = code
            self._since = now
        legal = code in (1, 2)
        if now - self._since >= (self.legal_ms if legal else self.illegal_ms):
            self.valid = legal
            seated_code = 1 if self.seated_contact == "NO" else 2
            self.engaged = legal and code == seated_code
            self.settled = True

    def code(self):
        """One letter for the status line: E engaged, R released, X invalid, W waiting."""
        if not self.settled:
            return "W"
        if not self.valid:
            return "X"
        return "E" if self.engaged else "R"


class BatteryGuard:
    """Debounced battery health from the KB2040's own divider.

    A reading below the cutoff (or above the maximum, or missing) for
    ``low_ms`` removes power; power returns only after the pack reads at or
    above the re-arm level for ``low_ms``.  Short motor-start dips therefore do
    not fault a transition, but a sagging pack does.
    """

    def __init__(self, cutoff_mv=BATTERY_CUTOFF_MV, rearm_mv=BATTERY_REARM_MV,
                 max_mv=BATTERY_MAX_MV, low_ms=BATTERY_LOW_MS):
        self.cutoff_mv = cutoff_mv
        self.rearm_mv = rearm_mv
        self.max_mv = max_mv
        self.low_ms = low_ms
        self.healthy = False
        self.pack_mv = None
        self._started = False
        self._since = None

    def update(self, now, pack_mv):
        self.pack_mv = pack_mv
        bad = pack_mv is None or pack_mv < self.cutoff_mv or pack_mv > self.max_mv
        if not self._started:
            if pack_mv is None:
                return self.healthy
            self._started = True
            self.healthy = not bad
            self._since = None
            return self.healthy
        if self.healthy:
            if bad:
                if self._since is None:
                    self._since = now
                if pack_mv is None or pack_mv > self.max_mv or now - self._since >= self.low_ms:
                    self.healthy = False
                    self._since = None
            else:
                self._since = None
        else:
            good = pack_mv is not None and self.rearm_mv <= pack_mv <= self.max_mv
            if good:
                if self._since is None:
                    self._since = now
                if now - self._since >= self.low_ms:
                    self.healthy = True
                    self._since = None
            else:
                self._since = None
        return self.healthy


class ReleaseServo:
    """Pulse width for the lock-release servo.

    Release: the release pulse, held.  Engage: the engage pulse for
    ``hold_ms``, then no pulse, so the servo stops loading the spring-return
    pin and draws no holding current.
    """

    def __init__(self, release_us=RELEASE_US, engage_us=ENGAGE_US, hold_ms=ENGAGE_HOLD_MS):
        self.release_us = release_us
        self.engage_us = engage_us
        self.hold_ms = hold_ms
        self._engaged_since = None

    def update(self, now, release):
        if release:
            self._engaged_since = None
            return self.release_us
        if self._engaged_since is None:
            self._engaged_since = now
        if now - self._engaged_since < self.hold_ms:
            return self.engage_us
        return 0


class Sample:
    """One tick's conditioned inputs to :class:`Stance`."""

    def __init__(self, position_mm=None, lock_valid=False, lock_engaged=False, power=False,
                 heartbeat=False, armed=False):
        self.position_mm = position_mm
        self.lock_valid = lock_valid
        self.lock_engaged = lock_engaged
        self.power = power
        self.heartbeat = heartbeat
        self.armed = armed


def _sign(value):
    if value > 0:
        return 1
    if value < 0:
        return -1
    return 0


class Stance:
    """The interlocked stance-change state machine.

    Call :meth:`tick` once per control tick.  Read :attr:`actuator` (-100
    retract .. +100 extend) and :attr:`release` (True pulls the pin) afterwards
    and apply them.  Ground drive is allowed only in ``THREE_FOOT``; the dome
    head only in ``THREE_FOOT`` or ``TWO_FOOT``.
    """

    def __init__(self, limits=None):
        self.lim = limits if limits is not None else Limits()
        self.state = HELD
        self.phase = NO_PHASE
        self.fault = NO_FAULT
        self.target = REQUEST_NONE
        self.reason = "starting"
        self.actuator = 0
        self.release = False
        self.position_mm = None
        self.lock_valid = False
        self.lock_engaged = False
        self.power = False
        self.heartbeat = False
        self.armed = False
        self.begun = False
        self._released = True
        self._seek_reached = False
        self._seek_reached_at = 0
        self._phase_start = 0
        self._phase_pos = 0.0
        self._move_start = 0
        self._progress_at = 0
        self._progress_pos = 0.0
        self._last_stop_at = 0
        self._last_direction = 0
        self._rest_start = 0
        self._rest_ms = 0
        self._run_ms = 0

    # -- queries ----------------------------------------------------------

    def transitioning(self):
        return self.state == RETRACTING or self.state == DEPLOYING

    def drive_allowed(self):
        return self.state == THREE_FOOT

    def head_allowed(self):
        return self.state == THREE_FOOT or self.state == TWO_FOOT

    def tilt_deg(self):
        """Body tilt known from the state, or ``None`` between stances."""
        if self.state == TWO_FOOT:
            return TWO_FOOT_TILT_DEG
        if self.state == THREE_FOOT:
            return THREE_FOOT_TILT_DEG
        return None

    def cooldown_ms(self, now):
        left = self._rest_ms - (now - self._rest_start)
        return left if left > 0 else 0

    def blocked(self, wanted, now, drive_idle):
        """``None`` when a request for ``wanted`` would start now, else the interlock text."""
        if not self.begun:
            return "starting"
        if wanted != REQUEST_TWO_FOOT and wanted != REQUEST_THREE_FOOT:
            return "no stance selected"
        if self.state == FAULT:
            return "fault latched; clear it first"
        if self.transitioning():
            if self.target == wanted:
                return "stance change in progress"
            return "release the active stance control first"
        if wanted == REQUEST_TWO_FOOT and self.state == TWO_FOOT:
            return "already standing on two feet"
        if wanted == REQUEST_THREE_FOOT and self.state == THREE_FOOT:
            return "already on three feet"
        if not self.power:
            return "battery below cutoff or battery sense invalid"
        if not self.heartbeat:
            return "controller link heartbeat lost"
        if not self.armed:
            return "arm the motors first"
        if not drive_idle:
            return "stop the wheels and the dome first"
        if not self._released:
            return "release the stance control, then press again"
        left = self.cooldown_ms(now)
        if left > 0:
            return "actuator cooling down, {0} s".format((left + 999) // 1000)
        return None

    def region(self, mm):
        if mm <= self.lim.two_foot_mm + self.lim.lock_window_mm:
            return TWO_FOOT
        if mm >= self.lim.three_foot_mm - self.lim.lock_window_mm:
            return THREE_FOOT
        return TRAVEL

    # -- commands ---------------------------------------------------------

    def tick(self, now, sample, request, drive_idle, request_fresh=True):
        """Advance one tick.

        ``request`` is the operator's held stance control (0 none, 2, 3).
        ``request_fresh`` is False when no request has arrived recently: the
        request then counts as none for the running transition, but it does
        NOT count as the operator letting go, so a link that comes back with
        the control still held can never restart the actuator by itself.
        """
        self.position_mm = sample.position_mm
        self.lock_valid = sample.lock_valid
        self.lock_engaged = sample.lock_valid and sample.lock_engaged
        self.power = sample.power
        self.heartbeat = sample.heartbeat
        self.armed = sample.armed
        if not request_fresh:
            request = REQUEST_NONE
        elif request == REQUEST_NONE:
            self._released = True
        if not self.begun:
            self.begun = True
            self._derive(now)
            return
        if self.state == FAULT or not self._check_sensors(now):
            return
        if self.transitioning():
            if not self.power:
                self._fail(now, POWER, "battery below cutoff during stance change; actuator stopped")
            elif not self.heartbeat:
                self.hold(now, "controller link heartbeat lost; actuator stopped and stance held")
            elif not self.armed:
                self.hold(now, "motors disarmed during stance change; stance held")
            elif request == REQUEST_NONE:
                self.hold(now, "stance control released before completion; stance held")
            elif request != self.target:
                self.hold(now, "opposite stance requested mid-change; stance held")
            elif not drive_idle:
                self.hold(now, "drive or dome command during stance change; stance held")
            else:
                self._step(now)
        elif (self.state == HELD or self._check_stable(now)) and request != REQUEST_NONE:
            if self.blocked(request, now, drive_idle) is None:
                self._begin(now, request)

    def hold(self, now, text):
        """Stop the actuator and hold.  The lock command is left as it is."""
        self._stop_actuator(now)
        self._start_rest(now)
        self.state = HELD
        self.phase = NO_PHASE
        self.reason = text
        self.target = REQUEST_NONE
        self._released = False

    def interrupt(self, now, text):
        """Hold if a transition is running; otherwise do nothing."""
        if self.transitioning():
            self.hold(now, text)
            return True
        return False

    def clear_fault(self, now):
        """Operator acknowledgement.  Succeeds only if the last sample is consistent."""
        if self.state != FAULT:
            return False
        self._derive(now)
        if self.state == FAULT:
            return False
        self._released = False
        return True

    # -- internals --------------------------------------------------------

    def _stop_actuator(self, now):
        if self.actuator != 0:
            self._run_ms += now - self._move_start
            self._last_stop_at = now
        self.actuator = 0

    def _start_rest(self, now):
        remaining = self.cooldown_ms(now)
        wanted = self._run_ms * self.lim.rest_per_run
        self._rest_start = now
        self._rest_ms = wanted if wanted > remaining else remaining
        self._run_ms = 0

    def _fail(self, now, why, text):
        self._stop_actuator(now)
        self._start_rest(now)
        self.state = FAULT
        self.phase = NO_PHASE
        self.fault = why
        self.reason = text
        self.target = REQUEST_NONE
        self._released = False

    def _check_sensors(self, now):
        lim = self.lim
        if self.position_mm is None:
            self._fail(now, FEEDBACK, "actuator position feedback out of range")
            return False
        if not self.lock_valid:
            self._fail(now, LOCK_SENSOR, "shoulder lock switch invalid: NO and NC agree")
            return False
        mm = self.position_mm
        if mm < lim.two_foot_mm - lim.overtravel_mm or mm > lim.three_foot_mm + lim.overtravel_mm:
            self._fail(now, OVERTRAVEL, "actuator beyond its stance endpoints")
            return False
        if self.lock_engaged and self.region(mm) == TRAVEL:
            self._fail(now, LOCK_DISAGREES, "lock switch reads seated away from both receivers")
            return False
        return True

    def _check_stable(self, now):
        two = self.state == TWO_FOOT
        end = self.lim.two_foot_mm if two else self.lim.three_foot_mm
        if abs(self.position_mm - end) > self.lim.hold_tolerance_mm:
            self._fail(now, DRIFT, "actuator left the two-foot endpoint" if two
                       else "actuator left the three-foot endpoint")
            return False
        if not self.lock_engaged:
            self._fail(now, LOCK_DISAGREES, "two-foot endpoint but lock switch not seated" if two
                       else "three-foot endpoint but lock switch not seated")
            return False
        return True

    def _derive(self, now):
        self.state = HELD
        self.fault = NO_FAULT
        self.phase = NO_PHASE
        self.target = REQUEST_NONE
        self.actuator = 0
        if not self._check_sensors(now):
            return
        self.release = False  # spring-return lock: recovery never holds the pin out
        mm = self.position_mm
        if self.lock_engaged and abs(mm - self.lim.two_foot_mm) <= self.lim.hold_tolerance_mm:
            self.state = TWO_FOOT
            self.reason = READY_TWO
        elif self.lock_engaged and abs(mm - self.lim.three_foot_mm) <= self.lim.hold_tolerance_mm:
            self.state = THREE_FOOT
            self.reason = READY_THREE
        else:
            self.reason = "between stances; hold a stance control to finish"

    def _pin_clear(self):
        if self.state == RETRACTING:
            return self.position_mm <= self.lim.three_foot_mm - self.lim.release_clear_mm
        return self.position_mm >= self.lim.two_foot_mm + self.lim.release_clear_mm

    def _enter_phase(self, now, phase):
        self.phase = phase
        self._phase_start = now
        self._phase_pos = self.position_mm
        self._progress_at = now
        self._progress_pos = self.position_mm
        self._seek_reached = False
        self.release = phase == UNLOCKING or phase == TRAVEL
        if phase == TRAVEL and self._pin_clear():
            self.release = False

    def _begin(self, now, wanted):
        self.target = wanted
        self.fault = NO_FAULT
        self._run_ms = 0
        lim = self.lim
        mm = self.position_mm
        where = self.region(mm)
        if wanted == REQUEST_TWO_FOOT:
            self.state = RETRACTING
            self.reason = "retracting the centre leg to the two-foot stance"
            if where == THREE_FOOT:
                first = UNLOCKING if self.lock_engaged else TRAVEL
            elif where == TRAVEL:
                first = TRAVEL
            elif self.lock_engaged:
                self._complete(now, TWO_FOOT)
                return
            else:
                first = LOCKING if mm <= lim.two_foot_mm + lim.seek_mm else TRAVEL
        else:
            self.state = DEPLOYING
            self.reason = "deploying the centre leg to the three-foot stance"
            if where == TWO_FOOT:
                first = UNLOCKING if self.lock_engaged else TRAVEL
            elif where == TRAVEL:
                first = TRAVEL
            elif self.lock_engaged:
                self._complete(now, THREE_FOOT)
                return
            else:
                first = LOCKING if mm >= lim.three_foot_mm - lim.seek_mm else TRAVEL
        self._enter_phase(now, first)

    def _complete(self, now, done):
        self._stop_actuator(now)
        self._start_rest(now)
        self.state = done
        self.phase = NO_PHASE
        self.target = REQUEST_NONE
        self.reason = READY_TWO if done == TWO_FOOT else READY_THREE
        self.release = False
        self._released = False

    def _move(self, now, goal, duty):
        """Drive toward ``goal``.  True once inside the stop band with the actuator stopped."""
        lim = self.lim
        error = goal - self.position_mm
        if abs(error) <= lim.stop_tolerance_mm:
            self._stop_actuator(now)
            return True
        direction = 1 if error > 0 else -1
        if now - self._phase_start >= lim.travel_timeout_ms:
            self._fail(now, TRAVEL_TIMEOUT, "actuator travel timeout")
            return False
        current = _sign(self.actuator)
        if current != direction:
            if current != 0:
                self._stop_actuator(now)
            self._progress_at = now
            self._progress_pos = self.position_mm
            if (self._last_direction != 0 and self._last_direction != direction
                    and now - self._last_stop_at < lim.reverse_dwell_ms):
                return False
            self.actuator = direction * duty
            self._last_direction = direction
            self._move_start = now
            return False
        self.actuator = direction * duty
        moved = (self.position_mm - self._progress_pos) * direction
        if moved <= -lim.progress_mm:
            self._fail(now, REVERSED_FEEDBACK, "actuator position moving opposite to its drive")
            return False
        if moved >= lim.progress_mm:
            self._progress_at = now
            self._progress_pos = self.position_mm
        elif now - self._progress_at >= lim.progress_ms:
            self._fail(now, STALL, "actuator stalled")
            return False
        return False

    def _stopped_drift(self, now, text):
        self._stop_actuator(now)
        if abs(self.position_mm - self._phase_pos) > self.lim.stop_tolerance_mm + self.lim.progress_mm:
            self._fail(now, DRIFT, text)
            return True
        return False

    def _step(self, now):
        lim = self.lim
        retracting = self.state == RETRACTING
        destination = TWO_FOOT if retracting else THREE_FOOT
        if self.phase == UNLOCKING:
            if self._stopped_drift(now, "actuator moved while the lock was releasing"):
                return
            if not self.lock_engaged:
                self._enter_phase(now, TRAVEL)
            elif now - self._phase_start >= lim.lock_timeout_ms:
                self._fail(now, LOCK_TIMEOUT, "lock release commanded but lock switch still seated")
            return
        if self.phase == TRAVEL:
            if self.lock_engaged:
                if self.region(self.position_mm) == destination:
                    self._complete(now, destination)
                else:
                    self._fail(now, LOCK_DISAGREES, "lock switch seated while the release was pulled")
                return
            if self._pin_clear():
                self.release = False
            goal = lim.two_foot_mm + lim.seek_mm if retracting else lim.three_foot_mm - lim.seek_mm
            if self._move(now, goal, 100):
                self._enter_phase(now, LOCKING)
            return
        if self.phase == LOCKING:
            if self.lock_engaged:
                self._complete(now, destination)
                return
            if now - self._phase_start < lim.lock_settle_ms:
                self._stopped_drift(now, "actuator moved while the lock pin was dropping")
                return
            if not self._seek_reached:
                goal = lim.two_foot_mm - lim.overshoot_mm if retracting else lim.three_foot_mm + lim.overshoot_mm
                if self._move(now, goal, lim.seek_duty_percent):
                    self._seek_reached = True
                    self._seek_reached_at = now
                return
            self._stop_actuator(now)
            if now - self._seek_reached_at >= lim.lock_timeout_ms:
                self._fail(now, LOCK_TIMEOUT, "actuator passed the receiver but lock switch not seated")
            return
        self.hold(now, "no stance phase; stance held")
