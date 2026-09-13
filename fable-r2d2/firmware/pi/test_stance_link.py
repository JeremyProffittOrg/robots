"""Tests for the Pi side of the revision D stance change.

The end-to-end cases run the real Pi ``SerialLink`` and ``StanceControl``
against the real KB2040 ``Supervisor`` and the simulated plant from
``firmware/kb2040/test_stance.py``, joined by an in-memory serial pair.

    python -m unittest discover -s firmware/pi -v
"""

import os
import sys
import unittest

HERE = os.path.dirname(os.path.abspath(__file__))
KB2040 = os.path.join(os.path.dirname(HERE), "kb2040")
sys.path.insert(0, HERE)
sys.path.append(KB2040)

import stance_link  # noqa: E402
from serial_link import SerialLink  # noqa: E402

import protocol  # noqa: E402  (firmware/kb2040)
import stance  # noqa: E402  (firmware/kb2040)
import supervisor  # noqa: E402  (firmware/kb2040)
import test_stance as kb  # noqa: E402  (firmware/kb2040: Plant and receiver positions)


class Clock:
    def __init__(self, start=100.0):
        self.now = start

    def __call__(self):
        return self.now


def status_line(state="THREE_FOOT", drive=True, head=True, two=True, three=False,
                reason="ready", two_block="", three_block="already on three feet"):
    return protocol.format_stance(state, "NONE", "NONE", 62.5, "EE", 12600, drive, head, two, three,
                                  reason, two_block, three_block)


class FakeLink:
    def __init__(self, clock):
        self.clock = clock
        self.requests = []
        self.clears = 0
        self.status = None
        self.status_at = None

    def set_stance_request(self, target):
        self.requests.append(target)

    def clear_stance_fault(self):
        self.clears += 1

    def stance_status(self):
        if self.status is None:
            return None, None
        return self.status, self.clock() - self.status_at

    def report(self, line):
        self.status = stance_link.parse_stance_line(line)
        self.status_at = self.clock()


class TestParseStanceLine(unittest.TestCase):
    def test_round_trip_from_the_kb2040_formatter(self):
        parsed = stance_link.parse_stance_line(protocol.format_stance(
            "RETRACTING", "TILT", "NONE", 51.26, "RR", 12603, False, False, False, False,
            "retracting the centre leg", "stance change in progress",
            "release the active stance control first"))
        self.assertEqual(parsed["state"], "RETRACTING")
        self.assertEqual(parsed["phase"], "TILT")
        self.assertAlmostEqual(parsed["position_mm"], 51.3)
        self.assertEqual(parsed["lock_label"], "left released, right released")
        self.assertAlmostEqual(parsed["pack_volts"], 12.603)
        self.assertFalse(parsed["drive_allowed"])
        self.assertEqual(parsed["two_foot_block"], "stance change in progress")

    def test_invalid_readings_become_none(self):
        parsed = stance_link.parse_stance_line(protocol.format_stance(
            "FAULT", "NONE", "FEEDBACK", None, "XE", None, False, False, False, False,
            "actuator position feedback out of range", "fault latched; clear it first",
            "fault latched; clear it first"))
        self.assertIsNone(parsed["position_mm"])
        self.assertIsNone(parsed["pack_volts"])
        self.assertEqual(parsed["fault"], "FEEDBACK")
        self.assertEqual(parsed["lock_label"], "left switch invalid, right seated")

    def test_rejects_other_lines(self):
        for line in ("st 1 0 0 0 0 0", "ss", "ss BOGUS NONE NONE 1 E 1 0 0 0 0 a|b|c",
                     "ss HELD NONE NONE 1 Q 1 0 0 0 0 a|b|c", "ss HELD NONE NONE 1 EQ 1 0 0 0 0 a|b|c",
                     "ss HELD NONE NONE 1 E 1 0 2 0 0 a|b|c",
                     "ss HELD NONE NONE x E 1 0 0 0 0 a|b|c", "ss HELD NONE NONE 1 E 1 0 0 0 0 a|b"):
            self.assertIsNone(stance_link.parse_stance_line(line), line)

    def test_request_line(self):
        self.assertEqual(stance_link.format_request(2), "T 2\n")
        with self.assertRaises(ValueError):
            stance_link.format_request(1)


class TestStanceLease(unittest.TestCase):
    def setUp(self):
        self.clock = Clock()
        self.link = FakeLink(self.clock)
        self.control = stance_link.StanceControl(self.link, self.clock)

    def test_phone_silence_drops_the_request(self):
        self.assertTrue(self.control.request(2))
        self.assertEqual(self.link.requests[-1], 2)
        self.clock.now += 0.45
        self.assertTrue(self.control.request(2))          # the page confirms the hold
        self.clock.now += 0.45
        self.assertFalse(self.control.tick())
        self.assertEqual(self.control.target, 2)
        self.clock.now += 0.10                             # 0.55 s since the last confirmation
        self.assertTrue(self.control.tick())
        self.assertEqual(self.link.requests[-1], 0)
        self.assertTrue(self.control.needs_release)
        self.assertIn("request dropped", self.control.notice)

    def test_a_stuck_button_cannot_restart_after_a_lapse(self):
        self.control.request(3)
        self.clock.now += 1.0
        self.control.tick()
        self.assertFalse(self.control.request(3))
        self.assertEqual(self.link.requests[-1], 0)
        self.assertTrue(self.control.request(0))
        self.assertTrue(self.control.request(3))
        self.assertEqual(self.link.requests[-1], 3)

    def test_stop_drops_a_held_request_and_needs_a_release(self):
        self.control.request(2)
        self.control.stop()
        self.assertEqual(self.link.requests[-1], 0)
        self.assertFalse(self.control.request(2))

    def test_bad_target(self):
        with self.assertRaises(ValueError):
            self.control.request(1)

    def test_clear_is_relayed(self):
        self.control.clear_fault()
        self.assertEqual(self.link.clears, 1)


class TestPiDriveGate(unittest.TestCase):
    def setUp(self):
        self.clock = Clock()
        self.link = FakeLink(self.clock)
        self.control = stance_link.StanceControl(self.link, self.clock)

    def test_no_status_refuses_everything(self):
        self.assertEqual(self.control.gate(600, 600, 600, 450), (0, 0, 0, 0))
        view = self.control.snapshot()
        self.assertFalse(view["available"])
        self.assertFalse(view["can_two_foot"])

    def test_stale_status_refuses_everything(self):
        self.link.report(status_line())
        self.clock.now += stance_link.STALE_STANCE_SECONDS
        self.assertEqual(self.control.gate(600, 600, 600, 450), (0, 0, 0, 0))

    def test_three_feet_allows_drive_and_dome(self):
        self.link.report(status_line())
        self.assertEqual(self.control.gate(600, -600, 600, 450), (600, -600, 600, 450))

    def test_two_feet_refuses_drive_and_keeps_the_dome(self):
        self.link.report(status_line("TWO_FOOT", drive=False, head=True))
        self.assertEqual(self.control.gate(600, 600, 600, 450), (0, 0, 0, 450))

    def test_transition_refuses_drive_and_dome(self):
        self.link.report(status_line("DEPLOYING", drive=False, head=False, two=False))
        self.assertEqual(self.control.gate(600, 600, 600, 450), (0, 0, 0, 0))


class FakeSerial:
    def __init__(self):
        self.written = []
        self.inbound = bytearray()

    @property
    def in_waiting(self):
        return len(self.inbound)

    def readline(self):
        index = self.inbound.find(b"\n")
        end = len(self.inbound) if index < 0 else index + 1
        data = bytes(self.inbound[:end])
        del self.inbound[:end]
        return data

    def write(self, data):
        self.written.append(data.decode("ascii"))


class TestSerialLinkStanceLines(unittest.TestCase):
    def setUp(self):
        self.clock = Clock()
        self.link = SerialLink(port="TEST", clock=self.clock)
        self.serial = FakeSerial()
        self.link._serial = self.serial

    def test_every_drive_line_carries_the_stance_request(self):
        self.link.set_stance_request(3)
        self.link._send_drive()
        self.assertEqual(self.serial.written, ["M 0 0 0 0\n", "T 3\n"])
        self.link.stop()
        self.link._send_pending()
        self.link._send_drive()
        self.assertEqual(self.serial.written[-3:], ["S\n", "M 0 0 0 0\n", "T 0\n"])

    def test_clear_is_queued(self):
        self.link.clear_stance_fault()
        self.link._send_pending()
        self.assertEqual(self.serial.written, ["C\n"])

    def test_bad_request_is_refused(self):
        with self.assertRaises(ValueError):
            self.link.set_stance_request(5)

    def test_status_lines_are_parsed_and_aged(self):
        self.serial.inbound.extend(b"st 1 0 0 0 0 0\n")
        self.serial.inbound.extend(status_line().encode("ascii"))
        self.link._read_lines()
        status, age = self.link.stance_status()
        self.assertEqual(status["state"], "THREE_FOOT")
        self.assertEqual(age, 0.0)
        self.clock.now += 0.7
        self.assertAlmostEqual(self.link.stance_status()[1], 0.7)
        self.assertTrue(self.link.snapshot()["fresh"])


class Bridge(FakeSerial):
    """The USB CDC cable: Pi writes go to the KB2040 supervisor, KB2040 writes come back."""

    def __init__(self):
        FakeSerial.__init__(self)
        self.core = None
        self.now_ms = 0
        self.connected = True

    def write(self, data):
        if self.connected:
            self.core.feed(data.decode("ascii"), self.now_ms)

    def from_kb2040(self, text):
        if self.connected:
            self.inbound.extend(text.encode("ascii"))


class EndToEnd:
    """Phone -> Pi StanceControl/SerialLink -> cable -> KB2040 Supervisor -> plant."""

    def __init__(self, mm=kb.RECEIVER_THREE, seated=3):
        self.t = 1000
        self.clock = lambda: self.t / 1000.0
        self.plant = kb.Plant(mm, seated)
        self.bridge = Bridge()
        self.core = supervisor.Supervisor(self.plant, self.bridge.from_kb2040, self.t)
        self.bridge.core = self.core
        self.link = SerialLink(port="TEST", clock=self.clock)
        self.link._serial = self.bridge
        self.control = stance_link.StanceControl(self.link, self.clock)
        self.phone_target = None   # None: the phone sends nothing
        self.link.set_enabled(True)
        self.run(500)  # lock debounce, then the first ss line that reports a stance

    @property
    def s(self):
        return self.core.stance

    def step(self):
        self.plant.physics(self.t, 10)
        self.t += 10
        self.bridge.now_ms = self.t
        if self.t % 50 == 0:
            if self.phone_target is not None:
                self.control.request(self.phone_target)
            self.control.tick()
            self.link._read_lines()
            self.link._send_pending()
            self.link._send_drive()
        self.core.tick(self.t)

    def run(self, ms):
        for _ in range(int(ms) // 10):
            self.step()

    def run_until(self, predicate, limit_ms):
        waited = 0
        while not predicate() and waited < limit_ms:
            self.step()
            waited += 10
        return predicate()


class TestEndToEnd(unittest.TestCase):
    def test_phone_holds_two_feet_until_the_lock_seats(self):
        rig = EndToEnd()
        self.assertTrue(rig.control.drive_permitted())
        rig.phone_target = 2
        self.assertTrue(rig.run_until(lambda: rig.s.state == stance.TWO_FOOT, 60000), rig.s.reason)
        rig.run(400)
        self.assertEqual(rig.control.status()["state"], "TWO_FOOT")
        self.assertFalse(rig.control.drive_permitted())
        self.assertTrue(rig.control.head_permitted())
        self.assertEqual(rig.control.gate(600, 600, 600, 450), (0, 0, 0, 450))
        self.assertLessEqual(rig.plant.pinned_ms, 100)

    def test_phone_goes_silent_mid_transition(self):
        rig = EndToEnd(kb.TWO_FOOT_POS, 2)
        rig.phone_target = 3
        self.assertTrue(rig.run_until(lambda: rig.s.phase == stance.TILT, 20000))
        rig.run(2000)
        self.assertEqual(rig.s.state, stance.DEPLOYING)
        rig.phone_target = None                             # Wi-Fi drops, the page stops sending
        rig.run(stance_link.STANCE_LEASE_SECONDS * 1000 + 150)
        self.assertEqual(rig.s.state, stance.HELD)
        self.assertIn("released", rig.s.reason)
        self.assertEqual(rig.plant.actuator, 0)
        self.assertEqual(rig.s.fault, stance.NO_FAULT)
        rig.run(400)
        self.assertEqual(rig.control.snapshot()["state"], "HELD")
        rig.phone_target = 3                                # page returns with the button still down
        rig.run(3000)
        self.assertEqual(rig.s.state, stance.HELD)
        self.assertEqual(rig.plant.actuator, 0)
        self.assertTrue(rig.control.snapshot()["needs_release"])

    def test_pi_to_kb2040_cable_lost_mid_transition(self):
        rig = EndToEnd()
        rig.phone_target = 2
        self.assertTrue(rig.run_until(lambda: rig.s.phase == stance.TILT, 3000))
        rig.run(1500)
        rig.bridge.connected = False
        rig.run(protocol.HEARTBEAT_MS + 100)
        self.assertEqual(rig.s.state, stance.HELD)
        self.assertIn("heartbeat", rig.s.reason)
        self.assertEqual(rig.plant.actuator, 0)
        rig.run(1000)
        self.assertIsNone(rig.control.status())             # stale on the Pi side too
        self.assertEqual(rig.control.gate(600, 600, 600, 450), (0, 0, 0, 0))

    def test_fault_is_cleared_from_the_page(self):
        rig = EndToEnd()
        rig.phone_target = 2
        self.assertTrue(rig.run_until(lambda: rig.s.phase == stance.TILT, 3000))
        rig.run(1000)
        rig.plant.stalled = True
        rig.run(kb.L.progress_ms + 100)
        self.assertEqual(rig.s.fault, stance.STALL)
        rig.run(300)
        self.assertEqual(rig.control.snapshot()["fault"], "STALL")
        rig.plant.stalled = False
        rig.phone_target = 0
        rig.control.clear_fault()
        rig.run(300)
        self.assertEqual(rig.s.state, stance.HELD)
        self.assertEqual(rig.control.snapshot()["state"], "HELD")


if __name__ == "__main__":
    unittest.main(verbosity=2)
