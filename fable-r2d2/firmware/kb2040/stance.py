"""Revision D stance interlock for the fable-r2d2 KB2040.  Hardware-free.

A 12 V linear actuator, parallel to the centre-leg guide, moves the centre leg.
Its stroke ``s`` (mm from fully closed) sets the stance:

    s = TWO_FOOT_MM     two-foot stance: centre foot stowed, wheels lifted,
                        body tilt 0 deg, stationary only
    s = CONTACT_MM      centre foot touches the floor, body tilt still 0 deg
    s = THREE_FOOT_MM   three-foot stance: body tilt 18 deg, centre foot forward

Between touchdown and three feet the centre foot rolls forward on the floor.
The tilt force check assumes almost no floor drag, so the centre wheels are
driven at the kinematic ground speed (CAD table below times the measured
actuator speed) during TILT and LOCKING, and stop whenever the actuator stops.
A command below the TT gearbox's minimum turning duty is delivered as short
bursts at that duty with the same average speed (``BurstFeed``).

Two shoulder locks, one per outer leg, mirror images.  Each is a spring-return
plunger pin in the body with two receivers in its leg: one at tilt 0 (seated for
every s up to CONTACT_MM) and one at tilt 18 deg (seated at THREE_FOOT_MM).  A
servo per lock pulls the pin (the "release").  An SPDT switch per lock, wired
NO + NC, reports "seated".  Lock state always comes from those switches and is
never inferred from actuator position.

Regions of the stroke:
    LIFT      s < CONTACT - window   body upright, foot in the air: both locks
                                     must read seated
    CONTACT   window round CONTACT   tilt-0 receivers: any lock state is legal
    TILT      between the windows    no receiver: no lock may read seated
    DEPLOYED  window round THREE     tilt-18 receivers: any lock state is legal

Phases of a change:
    retract  UNLOCKING -> TILT -> LOCKING (at CONTACT) -> LIFT -> TWO_FOOT
    deploy   LOWER -> UNLOCKING -> TILT -> LOCKING (at THREE) -> THREE_FOOT
    UNLOCKING  actuator stopped, releases pulled, wait until no lock reads seated
    TILT       full duty toward the far receiver, stopping SEEK short of it; the
               releases drop once the pins have cleared their bores
    LOCKING    settle, then creep through the receiver until both locks read seated
    LIFT/LOWER both locks seated, full duty between TWO_FOOT and CONTACT

No CircuitPython imports: ``supervisor.py`` feeds samples and applies outputs;
``test_stance.py`` runs it against a simulated plant on CPython.  Port of the
state machine in fable-r2d3 ``firmware/include/stance.h`` to two locks.
"""

# ===== MECHANISM CONSTANTS =====
# Source: stance-mechanism design values for the fable-r2d2 CAD, 2026-09-12,
# third geometry (30 deg guide, stowed hinge at y 34).
# (actuator datasheet Actuonix P16 Rev B, Omron SS series, Adafruit 1142).
# Replace every value in this block together if the CAD changes them.

ACTUATOR_PART = "Actuonix P16-100-256-12-P"
ACTUATOR_STROKE_MM = 100.0          # full mechanical stroke
ACTUATOR_NO_LOAD_SPEED_MM_S = 4.8   # 12 V; 3.4 mm/s at 150 N, 2.5 mm/s at 250 N
ACTUATOR_STALL_A = 1.0              # at 12 V
ACTUATOR_REST_PER_RUN = 4           # 20 % duty: 4 ms rest per ms of travel

TWO_FOOT_MM = 5.0                   # two-foot stance: wheels 25 mm above the floor
CONTACT_MM = 33.9                   # centre-foot touchdown at tilt 0 (CAD 33.87); tilt-0 receivers
THREE_FOOT_MM = 81.3                # tilt 18.00 deg (CAD 81.29); tilt-18 receivers
COMMAND_MIN_MM = 0.7                # never command outside 0.7 .. 99.3 mm
COMMAND_MAX_MM = 99.3
HARD_STOP_MM = 86.0                 # carriage on the bottom shaft bosses
TWO_FOOT_TILT_DEG = 0.0
THREE_FOOT_TILT_DEG = 18.0

POT_ZERO_MV = 0.0                   # wiper millivolts at stroke 0 (2.2 k top resistor)
POT_FULL_MV = 2750.0                # wiper millivolts at full stroke, 11 k pot
POT_MIN_VALID_MV = 40.0             # open wiper or open pot + reads below this
POT_MAX_VALID_MV = 3000.0           # open pot - reads above this

STOP_TOLERANCE_MM = 0.3             # a movement goal counts as reached inside this band
HOLD_TOLERANCE_MM = 2.0             # a parked stance faults if the actuator drifts further
LOCK_WINDOW_MM = 1.5                # band round each receiver where either lock state is legal
SEEK_MM = 1.2                       # TILT stops this far before the far receiver
OVERSHOOT_MM = 1.0                  # LOCKING creeps this far past the nominal receiver
OVERTRAVEL_MM = 1.5                 # beyond an endpoint by more than this is a fault
RELEASE_DROP_DEPLOY_MM = 44.4       # deploy: pins clear of the tilt-0 bores at or above this
RELEASE_DROP_RETRACT_MM = 54.5      # retract: pins clear of the tilt-18 bores at or below this
PROGRESS_MM = 0.3                   # stall: less than this ...
PROGRESS_MS = 1000                  # ... within this many ms while driven
LIFT_TIMEOUT_MS = 18000             # LIFT / LOWER phase, 28.9 mm at 2.5 mm/s x 1.5 = 17.3 s
TILT_TIMEOUT_MS = 29000             # TILT and LOCKING phase, 47.4 mm at 2.5 mm/s x 1.5 = 28.4 s
LOCK_SETTLE_MS = 150                # pin drop time before the LOCKING creep starts
LOCK_RELEASE_TIMEOUT_MS = 400       # 0.3 s pin pull plus the switch debounce
LOCK_SEAT_TIMEOUT_MS = 3000         # after the creep ends, both pins must read seated
REVERSE_DWELL_MS = 150              # stopped time before the actuator reverses
SEEK_DUTY_PERCENT = 20              # LOCKING creep duty, about 1 mm/s with no load

LOCK_NAMES = ("left", "right")
LOCK_SEATED_CONTACT = "NO"          # switch contact that closes when a pin is seated
LOCK_LEGAL_MS = 50                  # debounce for a legal NO/NC pair
LOCK_ILLEGAL_MS = 150               # both open or both closed must persist this long

ENGAGE_US = (1500, 1500)            # left, right: horn parked 1 mm clear of the knob
RELEASE_US = (1321, 1679)           # left, right: 16.3 deg toward the knob at ~11 us/deg, mirrored
ENGAGE_HOLD_MS = 1000               # engage pulse is held this long, then no pulse
SERVO_PERIOD_US = 20000             # 50 Hz
SERVO_SUPPLY_V = 6.0                # 19 % release-force margin at 6.0 V; the check still passes at 4.8 V

# Centre-foot ground travel, from the CAD kinematics (scripts/stability.py
# Stance.at_center_foot, caster yaw 0, geometry of 2026-09-12): (stroke mm,
# foot world y mm).  138.7 mm of rolling over the 47.4 mm tilt stroke; dy/ds is
# 6.5 just past touchdown and 2.0 at three feet.
CENTRE_FOOT_TRAVEL = (
    (33.868, 13.437), (34.118, 15.066), (34.368, 16.645), (34.868, 19.670), (35.368, 22.540),
    (35.868, 25.278), (36.868, 30.423), (37.868, 35.205), (39.868, 43.944), (41.868, 51.853),
    (44.868, 62.598), (47.868, 72.356), (51.868, 84.248), (55.868, 95.180), (59.868, 105.376),
    (63.868, 114.987), (68.868, 126.336), (73.868, 137.083), (77.868, 145.320), (81.290, 152.147),
)
WHEEL_DIAMETER_MM = 63.0            # Adafruit 3766 wheel
TT_NO_LOAD_RPM = 200.0              # Adafruit 3777 TT motor at 6 V
CENTRE_FEED_GAIN = 1.0              # commissioning trim on the kinematic wheel command
SPEED_WINDOW_MS = 250               # actuator speed is measured over this window
WHEEL_MIN_PERMILLE = 150            # TT gearbox minimum turning duty (firmware/pi/mixing.py MIN_DUTY)
WHEEL_BURST_MS = 100                # below that duty, the feed is sent as bursts this long

# ===== END MECHANISM CONSTANTS =====

# Battery sense on KB2040 A1: 12 V bus -> 100 k -> A1 node -> 15 k -> KB2040 GND.
BATTERY_TOP_OHMS = 100000
BATTERY_BOTTOM_OHMS = 15000
BATTERY_CUTOFF_MV = 11200           # below this for BATTERY_LOW_MS: no power
BATTERY_REARM_MV = 12000            # power returns only above this for BATTERY_LOW_MS
BATTERY_MAX_MV = 15200              # above this the reading is not a battery
BATTERY_LOW_MS = 500
ADC_REFERENCE_MV = 3300
ADC_FULL_SCALE = 65535

THREE_FOOT = "THREE_FOOT"
RETRACTING = "RETRACTING"
TWO_FOOT = "TWO_FOOT"
DEPLOYING = "DEPLOYING"
HELD = "HELD"
FAULT = "FAULT"
STATES = (THREE_FOOT, RETRACTING, TWO_FOOT, DEPLOYING, HELD, FAULT)

NO_PHASE = "NONE"
UNLOCKING = "UNLOCKING"
TILT = "TILT"
LOCKING = "LOCKING"
LIFT = "LIFT"
LOWER = "LOWER"
PHASES = (NO_PHASE, UNLOCKING, TILT, LOCKING, LIFT, LOWER)

# Regions of the stroke (LIFT and TILT share their phase names).
CONTACT = "CONTACT"
DEPLOYED = "DEPLOYED"

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

READY_TWO = "standing on two feet; both shoulder locks seated"
READY_THREE = "on three feet; both shoulder locks seated; ready to drive"


FOOT_FULL_SPEED_MM_S = 3.14159265 * WHEEL_DIAMETER_MM * TT_NO_LOAD_RPM / 60.0
"""Centre-foot ground speed at 1000 permille with no load, mm/s."""


class Limits:
    """The mechanism constants as one object, so tests can build variants."""

    def __init__(self, **overrides):
        self.two_foot_mm = TWO_FOOT_MM
        self.contact_mm = CONTACT_MM
        self.three_foot_mm = THREE_FOOT_MM
        self.command_min_mm = COMMAND_MIN_MM
        self.command_max_mm = COMMAND_MAX_MM
        self.hard_stop_mm = HARD_STOP_MM
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
        self.release_drop_deploy_mm = RELEASE_DROP_DEPLOY_MM
        self.release_drop_retract_mm = RELEASE_DROP_RETRACT_MM
        self.progress_mm = PROGRESS_MM
        self.progress_ms = PROGRESS_MS
        self.lift_timeout_ms = LIFT_TIMEOUT_MS
        self.tilt_timeout_ms = TILT_TIMEOUT_MS
        self.lock_settle_ms = LOCK_SETTLE_MS
        self.lock_release_timeout_ms = LOCK_RELEASE_TIMEOUT_MS
        self.lock_seat_timeout_ms = LOCK_SEAT_TIMEOUT_MS
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
        window = self.lock_window_mm

        def need(condition, text):
            if not condition:
                found.append(text)

        need(self.pot_full_mv > self.pot_zero_mv, "pot full mV must exceed zero mV")
        need(self.mm_for_mv(self.pot_min_valid_mv) < self.two_foot_mm - self.overtravel_mm,
             "pot minimum valid reading must lie below the two-foot overtravel limit")
        need(self.mm_for_mv(self.pot_max_valid_mv) > self.three_foot_mm + self.overtravel_mm,
             "pot maximum valid reading must lie above the three-foot overtravel limit")
        need(self.two_foot_mm - self.overtravel_mm >= self.command_min_mm,
             "two-foot overtravel limit must stay inside the command range")
        need(self.three_foot_mm + self.overtravel_mm <= self.command_max_mm,
             "three-foot overtravel limit must stay inside the command range")
        need(self.three_foot_mm + self.overtravel_mm < self.hard_stop_mm,
             "three-foot overtravel fault must trip before the hard mechanical stop")
        need(self.three_foot_mm + self.overshoot_mm + tol < self.hard_stop_mm,
             "the three-foot creep must end before the hard mechanical stop")
        need(CENTRE_FOOT_TRAVEL[0][0] <= self.contact_mm + tol
             and CENTRE_FOOT_TRAVEL[-1][0] >= self.three_foot_mm - window,
             "the centre-foot travel table must cover touchdown to three feet")
        need(self.seek_mm + tol <= window, "seek point must sit inside the lock window")
        need(self.overshoot_mm + tol < window, "overshoot must stay inside the lock window")
        need(self.overshoot_mm + tol < self.overtravel_mm, "overshoot must stay short of overtravel")
        need(window <= self.hold_tolerance_mm, "lock window must not exceed hold tolerance")
        need(self.contact_mm + window < self.release_drop_deploy_mm,
             "deploy release drop must lie above the contact lock window")
        need(self.release_drop_retract_mm < self.three_foot_mm - window,
             "retract release drop must lie below the three-foot lock window")
        need(self.two_foot_mm + self.hold_tolerance_mm < self.contact_mm - window,
             "two-foot hold band must lie below the contact lock window")
        need(self.contact_mm + window < self.three_foot_mm - window,
             "the two lock windows must not overlap")
        need(self.progress_mm > 0 and self.progress_ms > 0, "stall detection needs positive values")
        need(self.lift_timeout_ms > self.progress_ms and self.tilt_timeout_ms > self.progress_ms,
             "travel timeouts must exceed the stall window")
        need(self.lock_release_timeout_ms > LOCK_LEGAL_MS and self.lock_seat_timeout_ms > LOCK_LEGAL_MS,
             "lock timeouts must exceed the switch debounce")
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


def foot_ground_rate(mm, table=CENTRE_FOOT_TRAVEL):
    """Centre-foot ground travel per mm of stroke (dy/ds) at ``mm``; 0 before touchdown."""
    if mm is None or mm < table[0][0]:
        return 0.0
    index = len(table) - 1
    for candidate in range(1, len(table)):
        if mm <= table[candidate][0]:
            index = candidate
            break
    s0, y0 = table[index - 1]
    s1, y1 = table[index]
    return (y1 - y0) / (s1 - s0)


def centre_feed_permille(rate, speed_mm_s, direction, gain=CENTRE_FEED_GAIN,
                         full_speed=FOOT_FULL_SPEED_MM_S):
    """Centre-channel permille that rolls the foot at ``rate`` x ``speed_mm_s``.

    ``direction`` is +1 while extending (the foot rolls forward) and -1 while
    retracting.  Positive centre permille drives the robot forward.
    """
    value = int(round(direction * rate * speed_mm_s * 1000.0 * gain / full_speed))
    if value > 1000:
        return 1000
    if value < -1000:
        return -1000
    return value


class BurstFeed:
    """Delivers a small wheel command as bursts at the minimum turning duty.

    A command at or above ``minimum`` permille passes straight through.  Below
    it, the command is integrated, and each time a full burst's worth has built
    up the output runs at ``minimum`` for ``burst_ms``: the average matches the
    command, and the gearbox never sits at a duty too low to turn.  A zero
    command or a reversal stops the output at once and starts over.
    """

    def __init__(self, minimum=WHEEL_MIN_PERMILLE, burst_ms=WHEEL_BURST_MS):
        self.minimum = minimum
        self.burst_ms = burst_ms
        self.output = 0
        self._sign = 0
        self._debt = 0.0
        self._burst_left = 0

    def reset(self):
        self.output = 0
        self._sign = 0
        self._debt = 0.0
        self._burst_left = 0

    def update(self, wanted, dt_ms):
        if wanted == 0:
            self.reset()
            return 0
        sign = 1 if wanted > 0 else -1
        if sign != self._sign:
            self.reset()
            self._sign = sign
        magnitude = abs(wanted)
        if magnitude >= self.minimum:
            self._debt = 0.0
            self._burst_left = 0
            self.output = wanted
            return self.output
        self._debt += magnitude * dt_ms
        quantum = self.minimum * self.burst_ms
        if self._burst_left <= 0 and self._debt >= quantum:
            self._burst_left = self.burst_ms
            self._debt -= quantum
        if self._burst_left > 0:
            self._burst_left -= dt_ms
            self.output = sign * self.minimum
        else:
            self.output = 0
        return self.output


class ContactPair:
    """One SPDT lock switch: COM to ground, NO and NC each to a pulled-up input.

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
        """One letter: E seated, R released, X invalid, W waiting for the debounce."""
        if not self.settled:
            return "W"
        if not self.valid:
            return "X"
        return "E" if self.engaged else "R"


class LockSet:
    """Both shoulder lock switches, read together."""

    def __init__(self, count=len(LOCK_NAMES), legal_ms=LOCK_LEGAL_MS, illegal_ms=LOCK_ILLEGAL_MS,
                 seated_contact=LOCK_SEATED_CONTACT):
        self.pairs = [ContactPair(legal_ms, illegal_ms, seated_contact) for _ in range(count)]

    def update(self, now, contacts):
        """``contacts`` is one ``(no_closed, nc_closed)`` per lock, left first."""
        if len(contacts) != len(self.pairs):
            raise ValueError("expected {0} lock readings".format(len(self.pairs)))
        for pair, reading in zip(self.pairs, contacts):
            pair.update(now, reading[0], reading[1])

    def settled(self):
        return all(pair.settled for pair in self.pairs)

    def valid(self):
        return all(pair.valid for pair in self.pairs)

    def all_engaged(self):
        return self.valid() and all(pair.engaged for pair in self.pairs)

    def any_engaged(self):
        return self.valid() and any(pair.engaged for pair in self.pairs)

    def code(self):
        """One letter per lock, left first, for the status line."""
        return "".join(pair.code() for pair in self.pairs)


class BatteryGuard:
    """Debounced battery health from the KB2040's own divider.

    A reading below the cutoff for ``low_ms`` removes power; a missing or
    above-maximum reading removes it at once.  Power returns only after the pack
    reads at or above the re-arm level for ``low_ms``.  Short motor-start dips
    therefore do not fault a change, but a sagging pack does.
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
    """Pulse width for one lock-release servo.

    Release: the release pulse, held.  Engage: the engage pulse for
    ``hold_ms``, then no pulse, so the horn stays parked clear of the knob and
    the servo draws no holding current.  The pin is spring return either way.
    """

    def __init__(self, release_us, engage_us, hold_ms=ENGAGE_HOLD_MS):
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

    def __init__(self, position_mm=None, lock_valid=False, lock_all=False, lock_any=False,
                 power=False, heartbeat=False, armed=False):
        self.position_mm = position_mm
        self.lock_valid = lock_valid
        self.lock_all = lock_all
        self.lock_any = lock_any
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

    Call :meth:`tick` once per control tick, then apply :attr:`actuator` (-100
    retract .. +100 extend) and :attr:`release` (True pulls both pins).  Ground
    drive is allowed only in ``THREE_FOOT``; the dome only in ``THREE_FOOT`` or
    ``TWO_FOOT``.
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
        self.lock_all = False
        self.lock_any = False
        self.power = False
        self.heartbeat = False
        self.armed = False
        self.speed_mm_s = 0.0
        self.centre_permille = 0
        self.begun = False
        self._track = []
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
        """Body tilt known from the state and the locks, or ``None`` when unknown."""
        if self.state == THREE_FOOT:
            return THREE_FOOT_TILT_DEG
        if self.state == FAULT or self.position_mm is None:
            return None
        if self.lock_all and self.region(self.position_mm) in (LIFT, CONTACT):
            return TWO_FOOT_TILT_DEG
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
        lim = self.lim
        if mm < lim.contact_mm - lim.lock_window_mm:
            return LIFT
        if mm <= lim.contact_mm + lim.lock_window_mm:
            return CONTACT
        if mm < lim.three_foot_mm - lim.lock_window_mm:
            return TILT
        return DEPLOYED

    # -- commands ---------------------------------------------------------

    def tick(self, now, sample, request, drive_idle, request_fresh=True):
        """Advance one tick, then update :attr:`centre_permille`.

        See :meth:`_advance` for the arguments.
        """
        self._advance(now, sample, request, drive_idle, request_fresh)
        self._update_feed()

    def _update_speed(self, now):
        """Actuator speed from the pot over the last ``SPEED_WINDOW_MS``, mm/s."""
        if self.position_mm is None:
            self._track = []
            self.speed_mm_s = 0.0
            return
        self._track.append((now, self.position_mm))
        while len(self._track) > 2 and now - self._track[1][0] >= SPEED_WINDOW_MS:
            self._track.pop(0)
        first_t, first_mm = self._track[0]
        span = now - first_t
        self.speed_mm_s = abs(self.position_mm - first_mm) * 1000.0 / span if span > 0 else 0.0

    def _update_feed(self):
        """Centre wheels at the kinematic ground speed while the foot rolls; else 0."""
        rolling = (self.transitioning() and (self.phase == TILT or self.phase == LOCKING)
                   and self.actuator != 0 and self.position_mm is not None
                   and self.position_mm > self.lim.contact_mm)
        if not rolling:
            self.centre_permille = 0
            return
        direction = 1 if self.actuator > 0 else -1
        self.centre_permille = centre_feed_permille(
            foot_ground_rate(self.position_mm), self.speed_mm_s, direction)

    def _advance(self, now, sample, request, drive_idle, request_fresh):
        """Advance the state machine one tick.

        ``request`` is the operator's held stance control (0 none, 2, 3).
        ``request_fresh`` is False when no request has arrived recently: the
        request then counts as none for a running change, but NOT as the
        operator letting go, so a link that comes back with the control still
        held can never restart the actuator by itself.
        """
        self.position_mm = sample.position_mm
        self.lock_valid = sample.lock_valid
        self.lock_all = sample.lock_valid and sample.lock_all
        self.lock_any = sample.lock_valid and sample.lock_any
        self.power = sample.power
        self.heartbeat = sample.heartbeat
        self.armed = sample.armed
        self._update_speed(now)
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
        """Stop the actuator and hold.  The release command is left as it is."""
        self._stop_actuator(now)
        self._start_rest(now)
        self.state = HELD
        self.phase = NO_PHASE
        self.reason = text
        self.target = REQUEST_NONE
        self._released = False

    def interrupt(self, now, text):
        """Hold if a change is running; otherwise do nothing."""
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
            self._fail(now, LOCK_SENSOR, "a shoulder lock switch is invalid: NO and NC agree")
            return False
        mm = self.position_mm
        if mm < lim.two_foot_mm - lim.overtravel_mm or mm > lim.three_foot_mm + lim.overtravel_mm:
            self._fail(now, OVERTRAVEL, "actuator beyond its stance endpoints")
            return False
        where = self.region(mm)
        if where == LIFT and not self.lock_all:
            self._fail(now, LOCK_DISAGREES, "centre foot raised but a shoulder lock is not seated")
            return False
        if where == TILT and self.lock_any:
            self._fail(now, LOCK_DISAGREES, "a shoulder lock reads seated where no receiver exists")
            return False
        return True

    def _check_stable(self, now):
        two = self.state == TWO_FOOT
        end = self.lim.two_foot_mm if two else self.lim.three_foot_mm
        if abs(self.position_mm - end) > self.lim.hold_tolerance_mm:
            self._fail(now, DRIFT, "actuator left the two-foot endpoint" if two
                       else "actuator left the three-foot endpoint")
            return False
        if not self.lock_all:
            self._fail(now, LOCK_DISAGREES, "two-foot stance but a shoulder lock is not seated" if two
                       else "three-foot stance but a shoulder lock is not seated")
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
        self.release = False  # spring-return locks: recovery never holds a pin out
        mm = self.position_mm
        if self.lock_all and abs(mm - self.lim.two_foot_mm) <= self.lim.hold_tolerance_mm:
            self.state = TWO_FOOT
            self.reason = READY_TWO
        elif self.lock_all and abs(mm - self.lim.three_foot_mm) <= self.lim.hold_tolerance_mm:
            self.state = THREE_FOOT
            self.reason = READY_THREE
        else:
            self.reason = "between stances; hold a stance control to finish"

    def _pins_clear(self):
        """True once the pins have left the bores they were released from."""
        if self.state == RETRACTING:
            return self.position_mm <= self.lim.release_drop_retract_mm
        return self.position_mm >= self.lim.release_drop_deploy_mm

    def _enter_phase(self, now, phase):
        self.phase = phase
        self._phase_start = now
        self._phase_pos = self.position_mm
        self._progress_at = now
        self._progress_pos = self.position_mm
        self._seek_reached = False
        self.release = phase == UNLOCKING or phase == TILT
        if phase == TILT and self._pins_clear():
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
            if where == LIFT:
                first = LIFT
            elif where == CONTACT:
                if self.lock_all:
                    first = LIFT
                elif mm <= lim.contact_mm + lim.seek_mm or self.lock_any:
                    first = LOCKING
                else:
                    first = TILT
            elif where == TILT:
                first = TILT
            else:
                first = UNLOCKING if self.lock_any else TILT
        else:
            self.state = DEPLOYING
            self.reason = "deploying the centre leg to the three-foot stance"
            if where == LIFT:
                first = LOWER
            elif where == CONTACT:
                if self.lock_all:
                    at_contact = abs(mm - lim.contact_mm) <= lim.stop_tolerance_mm
                    first = UNLOCKING if at_contact else LOWER
                else:
                    first = UNLOCKING if self.lock_any else TILT
            elif where == TILT:
                first = TILT
            elif self.lock_all:
                self._complete(now, THREE_FOOT)
                return
            else:
                first = LOCKING if mm >= lim.three_foot_mm - lim.seek_mm or self.lock_any else TILT
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

    def _move(self, now, goal, duty, timeout_ms):
        """Drive toward ``goal``.  True once inside the stop band with the actuator stopped."""
        lim = self.lim
        error = goal - self.position_mm
        if abs(error) <= lim.stop_tolerance_mm:
            self._stop_actuator(now)
            return True
        direction = 1 if error > 0 else -1
        if now - self._phase_start >= timeout_ms:
            self._fail(now, TRAVEL_TIMEOUT, "actuator travel timeout in the {0} phase".format(self.phase))
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
        if self.phase == UNLOCKING:
            if self._stopped_drift(now, "actuator moved while the locks were releasing"):
                return
            if not self.lock_any:
                self._enter_phase(now, TILT)
            elif now - self._phase_start >= lim.lock_release_timeout_ms:
                self._fail(now, LOCK_TIMEOUT, "releases pulled but a shoulder lock still reads seated")
            return
        if self.phase == TILT:
            if self.lock_any:
                destination = CONTACT if retracting else DEPLOYED
                if self.region(self.position_mm) == destination:
                    self._stop_actuator(now)
                    self._enter_phase(now, LOCKING)
                else:
                    self._fail(now, LOCK_DISAGREES, "a shoulder lock reads seated while leaving its receiver")
                return
            if self._pins_clear():
                self.release = False
            goal = lim.contact_mm + lim.seek_mm if retracting else lim.three_foot_mm - lim.seek_mm
            if self._move(now, goal, 100, lim.tilt_timeout_ms):
                self._enter_phase(now, LOCKING)
            return
        if self.phase == LOCKING:
            if self.lock_all:
                self._stop_actuator(now)
                if retracting:
                    self._enter_phase(now, LIFT)
                else:
                    self._complete(now, THREE_FOOT)
                return
            if now - self._phase_start < lim.lock_settle_ms:
                self._stopped_drift(now, "actuator moved while the lock pins were dropping")
                return
            if not self._seek_reached:
                goal = lim.contact_mm - lim.overshoot_mm if retracting else lim.three_foot_mm + lim.overshoot_mm
                if self._move(now, goal, lim.seek_duty_percent, lim.tilt_timeout_ms):
                    self._seek_reached = True
                    self._seek_reached_at = now
                return
            self._stop_actuator(now)
            if now - self._seek_reached_at >= lim.lock_seat_timeout_ms:
                self._fail(now, LOCK_TIMEOUT, "actuator passed the receivers but a shoulder lock is not seated")
            return
        if self.phase == LIFT or self.phase == LOWER:
            if not self.lock_all:
                self._fail(now, LOCK_DISAGREES, "a shoulder lock released while it must carry the body")
                return
            if retracting:
                if self.phase == LOWER:
                    self._enter_phase(now, LIFT)
                elif self._move(now, lim.two_foot_mm, 100, lim.lift_timeout_ms):
                    self._complete(now, TWO_FOOT)
            else:
                if self.phase == LIFT:
                    self._enter_phase(now, LOWER)
                elif self._move(now, lim.contact_mm, 100, lim.lift_timeout_ms):
                    self._enter_phase(now, UNLOCKING)
            return
        self.hold(now, "no stance phase; stance held")
