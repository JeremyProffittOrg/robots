"""Pi side of the revision D stance change.  Standard library only.

The KB2040 owns the interlock.  The Pi only:

* relays the operator's held stance control as a ``T <0|2|3>`` line every
  50 ms, under a 0.5 s lease: if the page stops confirming the hold, the
  request drops to 0 and the KB2040 holds the actuator;
* after a lease expiry, ignores a stance request until the page has sent an
  explicit release (target 0), so a page that comes back with a stuck button
  cannot restart the actuator;
* relays ``C`` to clear a latched fault;
* parses the ``ss`` status line and refuses ground drive and dome commands
  whenever that status is missing, stale, or does not allow them.
"""

import logging
import time

LOGGER = logging.getLogger("r2d2.stance")

REQUEST_NONE = 0
REQUEST_TWO_FOOT = 2
REQUEST_THREE_FOOT = 3
REQUESTS = (REQUEST_NONE, REQUEST_TWO_FOOT, REQUEST_THREE_FOOT)

STANCE_LEASE_SECONDS = 0.5
"""A held stance control must be re-confirmed by the page within this time."""

STALE_STANCE_SECONDS = 1.0
"""An ``ss`` line older than this means the interlock state is unknown."""

STATE_LABELS = {
    "THREE_FOOT": "Three feet",
    "TWO_FOOT": "Two feet",
    "RETRACTING": "Retracting centre leg",
    "DEPLOYING": "Deploying centre leg",
    "HELD": "Held between stances",
    "FAULT": "FAULT",
}

LOCK_LABELS = {"E": "seated", "R": "released", "X": "switch invalid", "W": "settling"}


LOCK_SIDES = ("left", "right")


def describe_locks(codes):
    """``"ER"`` becomes ``"left seated, right released"``."""
    parts = []
    for index, code in enumerate(codes):
        side = LOCK_SIDES[index] if index < len(LOCK_SIDES) else "lock {0}".format(index + 1)
        parts.append("{0} {1}".format(side, LOCK_LABELS[code]))
    return ", ".join(parts)


def format_request(target):
    """The ``T`` line for the KB2040, terminator included."""
    if target not in REQUESTS:
        raise ValueError("stance request must be 0, 2 or 3")
    return "T {0}\n".format(target)


CLEAR_LINE = "C\n"


def parse_stance_line(line):
    """Parse a KB2040 ``ss`` line into a dictionary, or return ``None``."""
    text = line.rstrip("\r\n")
    if not text.startswith("ss "):
        return None
    parts = text.split(" ", 11)
    if len(parts) != 12:
        return None
    _tag, state, phase, fault, position, lock, pack_mv, drive, head, two, three, tail = parts
    if state not in STATE_LABELS or not lock or any(code not in LOCK_LABELS for code in lock):
        return None
    try:
        position = int(position)
        pack_mv = int(pack_mv)
        flags = [int(drive), int(head), int(two), int(three)]
    except ValueError:
        return None
    if any(flag not in (0, 1) for flag in flags):
        return None
    texts = tail.split("|")
    if len(texts) != 3:
        return None
    return {
        "state": state,
        "label": STATE_LABELS[state],
        "phase": phase,
        "fault": fault,
        "position_mm": None if position < 0 else position / 10.0,
        "lock": lock,
        "lock_label": describe_locks(lock),
        "pack_volts": None if pack_mv < 0 else pack_mv / 1000.0,
        "drive_allowed": flags[0] == 1,
        "head_allowed": flags[1] == 1,
        "can_two_foot": flags[2] == 1,
        "can_three_foot": flags[3] == 1,
        "reason": texts[0],
        "two_foot_block": texts[1],
        "three_foot_block": texts[2],
    }


class StanceControl:
    """The operator's stance lease and the Pi-side drive gate.

    ``link`` provides ``set_stance_request(target)``, ``clear_stance_fault()``
    and ``stance_status()`` returning ``(status dict or None, age seconds or None)``.
    """

    def __init__(self, link, clock=time.monotonic, lease=STANCE_LEASE_SECONDS):
        self.link = link
        self.clock = clock
        self.lease = lease
        self.target = REQUEST_NONE
        self.last_input = 0.0
        self.needs_release = False
        self.notice = None

    def request(self, target):
        """The page holds (2 or 3) or lets go of (0) a stance control.

        Returns False when the request was ignored because the lease expired
        and the page has not released the control since.
        """
        target = int(target)
        if target not in REQUESTS:
            raise ValueError("stance request must be 0, 2 or 3")
        if target == REQUEST_NONE:
            self.needs_release = False
            self._set(REQUEST_NONE)
            return True
        if self.needs_release:
            return False
        if target != self.target:
            LOGGER.info("stance control held: %d", target)
        self.last_input = self.clock()
        self._set(target)
        return True

    def _set(self, target):
        self.target = target
        self.link.set_stance_request(target)

    def stop(self):
        """Emergency stop or page gone: drop the request at once."""
        if self.target != REQUEST_NONE:
            self.needs_release = True
        self._set(REQUEST_NONE)

    def clear_fault(self):
        self.link.clear_stance_fault()

    def tick(self):
        """Apply the lease.  Returns True when a held request was just dropped."""
        if self.target != REQUEST_NONE and self.clock() - self.last_input > self.lease:
            self.notice = "stance control not confirmed for {0:.1f} s; request dropped".format(
                self.lease)
            LOGGER.warning("%s", self.notice)
            self.needs_release = True
            self._set(REQUEST_NONE)
            return True
        return False

    def status(self):
        """The last ``ss`` status when it is fresh, else ``None``."""
        status, age = self.link.stance_status()
        if status is None or age is None or age >= STALE_STANCE_SECONDS:
            return None
        return status

    def drive_permitted(self):
        status = self.status()
        return status is not None and status["drive_allowed"]

    def head_permitted(self):
        status = self.status()
        return status is not None and status["head_allowed"]

    def gate(self, left, right, centre, head):
        """Zero whatever the interlock does not allow.  Returns the four values."""
        if not self.drive_permitted():
            left = right = centre = 0
        if not self.head_permitted():
            head = 0
        return left, right, centre, head

    def snapshot(self):
        """Everything the page needs to render and grey out the stance controls."""
        status = self.status()
        view = {
            "available": status is not None,
            "request": self.target,
            "needs_release": self.needs_release,
            "notice": self.notice,
        }
        if status is None:
            view.update({
                "state": None, "label": "Stance unknown", "phase": None, "fault": None,
                "position_mm": None, "lock": None, "lock_label": "unknown", "pack_volts": None,
                "drive_allowed": False, "head_allowed": False,
                "can_two_foot": False, "can_three_foot": False,
                "reason": "no fresh stance status from the KB2040",
                "two_foot_block": "no fresh stance status from the KB2040",
                "three_foot_block": "no fresh stance status from the KB2040",
            })
        else:
            view.update(status)
        return view
