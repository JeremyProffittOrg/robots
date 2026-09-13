"""Host tests for the revision D stance interlock, the supervisor and the pin plan.

A simulated plant stands in for the actuator, the spring-return lock pin with a
receiver at each endpoint, the NO/NC lock switch, the battery and the motors.
The real ``supervisor.Supervisor`` and ``stance.Stance`` run against it, fed
through the real serial protocol.

    python -m unittest discover -s firmware/kb2040 -v
"""

import os
import re
import sys
import unittest

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)

import protocol  # noqa: E402
import stance  # noqa: E402
import supervisor  # noqa: E402

L = stance.Limits()
RECEIVER_TWO = L.two_foot_mm
RECEIVER_THREE = L.three_foot_mm + 0.2  # real receiver slightly off nominal: exercises the seek
SEAT_BAND_MM = 0.3


def receiver_mm(which):
    return RECEIVER_TWO if which == 2 else RECEIVER_THREE


class Plant:
    """Non-backdrivable lead-screw actuator and a spring pin with two receivers."""

    def __init__(self, mm=RECEIVER_THREE, seated=3):
        self.mm = mm
        self.seated = seated
        self.speed = stance.ACTUATOR_NO_LOAD_SPEED_MM_S / 1000.0  # mm per ms at 100 %
        self.actuator = 0
        self.release_us = 0
        self.enabled = False
        self.channels = [0, 0, 0, 0]
        self.coasted = 0
        self.pack_mv = 12600.0
        self.pot_override_mv = None
        self.contacts_override = None
        self.stalled = False
        self.jammed = False
        self.stuck_seated = False
        self.reversed_drive = False
        self.seat_delay = 60
        self.pull_delay = 250
        self.moved_pinned = False
        self.foot_output_while_not_parked = False
        self._pending_at = None

    # -- hardware object used by the supervisor ----------------------------

    def set_enabled(self, flag):
        self.enabled = bool(flag)

    def apply_drive(self, enabled, channels):
        self.channels = list(channels) if enabled else [0, 0, 0, 0]

    def coast_all(self):
        self.channels = [0, 0, 0, 0]
        self.coasted += 1

    def fill(self, red, green, blue):
        return True

    def set_pixel(self, index, red, green, blue):
        return True

    def index_detected(self):
        return False

    def read_position_mv(self):
        if self.pot_override_mv is not None:
            return self.pot_override_mv
        return L.mv_for_mm(self.mm)

    def read_lock_contacts(self):
        if self.contacts_override is not None:
            return self.contacts_override
        seated = self.seated != 0
        return (seated, not seated)  # NO closes when the pin is seated

    def read_battery_mv(self):
        return self.pack_mv

    def drive_actuator(self, percent):
        self.actuator = percent

    def set_release_pulse(self, pulse_us):
        self.release_us = pulse_us

    # -- physics ----------------------------------------------------------

    def releasing(self):
        return self.release_us == stance.RELEASE_US

    def aligned(self):
        if abs(self.mm - RECEIVER_TWO) <= SEAT_BAND_MM:
            return 2
        if abs(self.mm - RECEIVER_THREE) <= SEAT_BAND_MM:
            return 3
        return 0

    def physics(self, now, dt):
        if self.actuator and not self.stalled and self.pack_mv > 9000:
            step = (self.actuator / 100.0) * self.speed * dt
            if self.reversed_drive:
                step = -step
            following = self.mm + step
            if self.seated and abs(following - receiver_mm(self.seated)) > SEAT_BAND_MM:
                self.moved_pinned = True
            else:
                self.mm = following
        if self.stuck_seated:
            want = self.seated
        elif self.releasing():
            want = 0
        elif self.seated == 0 and not self.jammed:
            want = self.aligned()
        else:
            want = self.seated
        if want != self.seated:
            if self._pending_at is None:
                self._pending_at = now + (self.seat_delay if want else self.pull_delay)
            elif now >= self._pending_at:
                self.seated = want
                self._pending_at = None
        else:
            self._pending_at = None


class Rig:
    """Supervisor + plant + a stand-in Pi that sends M and T lines every 50 ms."""

    def __init__(self, mm=RECEIVER_THREE, seated=3, armed=True):
        self.plant = Plant(mm, seated)
        self.t = 1000
        self.lines = []
        self.errors = []
        self.core = supervisor.Supervisor(self.plant, self._write, self.t)
        self.request = 0
        self.link = True           # Pi -> KB2040 lines flowing at all
        self.send_request = True   # T lines included
        self.drive_line = "M 0 0 0 0"
        self._next_line = self.t
        if armed:
            self.send("E 1")
        self.run(100)

    def _write(self, text):
        self.lines.append(text)
        if text.startswith("err"):
            self.errors.append(text.strip())
        if len(self.lines) > 4000:
            del self.lines[:-500]

    @property
    def s(self):
        return self.core.stance

    def send(self, line):
        self.core.feed(line + "\n", self.t)

    def step(self):
        self.plant.physics(self.t, 10)
        self.t += 10
        if self.link and self.t >= self._next_line:
            text = self.drive_line + "\n"
            if self.send_request:
                text += "T {0}\n".format(self.request)
            self.core.feed(text, self.t)
            self._next_line = self.t + 50
        self.core.tick(self.t)
        parked = self.s.state == stance.THREE_FOOT
        if not parked and any(self.plant.channels[:3]):
            self.plant.foot_output_while_not_parked = True

    def run(self, ms):
        for _ in range(ms // 10):
            self.step()

    def run_until(self, predicate, limit_ms):
        waited = 0
        while not predicate() and waited < limit_ms:
            self.step()
            waited += 10
        return predicate()

    def until_state(self, state, limit_ms):
        return self.run_until(lambda: self.s.state == state, limit_ms)

    def until_phase(self, phase, limit_ms):
        return self.run_until(lambda: self.s.phase == phase, limit_ms)

    def release(self):
        self.request = 0
        self.run(60)

    def cool(self):
        self.request = 0
        self.run_until(lambda: self.s.cooldown_ms(self.t) == 0, 400000)
        self.run(20)

    def last_status(self):
        for text in reversed(self.lines):
            if text.startswith("ss "):
                return text
        return None


KB2040_GPIO = {
    "D0": 0, "D1": 1, "D2": 2, "D3": 3, "D4": 4, "D5": 5, "D6": 6, "D7": 7, "D8": 8, "D9": 9,
    "D10": 10, "SCK": 18, "MOSI": 19, "MISO": 20, "A0": 26, "A1": 27, "A2": 28, "A3": 29,
    "SDA": 12, "SCL": 13,
}


class TestPinPlan(unittest.TestCase):
    """The KB2040 pin budget in code.py, parsed as text (it imports ``board``)."""

    @classmethod
    def setUpClass(cls):
        with open(os.path.join(HERE, "code.py"), encoding="utf-8") as handle:
            cls.source = handle.read()
        table = re.search(r"^DRIVES\s*=\s*\((.*?)^\)", cls.source, re.S | re.M).group(1)
        cls.drives = re.findall(
            r'\(\s*"(\w+)"\s*,\s*\w+\s*,\s*board\.(\w+)\s*,\s*(\d+)\s*,\s*board\.(\w+)\s*,\s*(\d+)',
            table)
        cls.actuator = re.search(
            r'^ACTUATOR\s*=\s*\("actuator"\s*,\s*board\.(\w+)\s*,\s*(\d+)\s*,\s*board\.(\w+)\s*,\s*(\d+)',
            cls.source, re.M).groups()
        cls.singles = dict(re.findall(r"^([A-Z_]+)_PIN\s*=\s*board\.(\w+)", cls.source, re.M))

    def test_four_drive_outputs(self):
        self.assertEqual([entry[0] for entry in self.drives], ["left", "right", "centre", "head"])

    def test_declared_gpio_numbers_match_the_board_names(self):
        for _name, pwm, pwm_gpio, digital, dig_gpio in self.drives:
            self.assertEqual(KB2040_GPIO[pwm], int(pwm_gpio))
            self.assertEqual(KB2040_GPIO[digital], int(dig_gpio))
        self.assertEqual(KB2040_GPIO[self.actuator[0]], int(self.actuator[1]))
        self.assertEqual(KB2040_GPIO[self.actuator[2]], int(self.actuator[3]))
        for label in ("RELEASE_SERVO", "LOCK_NO", "LOCK_NC", "POSITION", "BATTERY"):
            gpio = int(re.search(r"^{0}_GPIO\s*=\s*(\d+)".format(label), self.source, re.M).group(1))
            self.assertEqual(KB2040_GPIO[self.singles[label]], gpio, label)

    def test_no_pin_is_used_twice(self):
        used = []
        for _name, pwm, _a, digital, _b in self.drives:
            used += [pwm, digital]
        used += [self.actuator[0], self.actuator[2]]
        used += list(self.singles.values())
        self.assertEqual(len(used), len(set(used)), used)
        self.assertEqual(len(used), 18)
        self.assertNotIn("SDA", used)
        self.assertNotIn("SCL", used)

    def test_pwm_pins_do_not_share_an_output_or_a_frequency(self):
        fast = [int(entry[2]) for entry in self.drives] + [int(self.actuator[1])]
        servo = KB2040_GPIO[self.singles["RELEASE_SERVO"]]
        self.assertEqual(protocol.pwm_conflicts(fast + [servo]), [])
        outputs = [(gpio, protocol.PWM_FREQUENCY) for gpio in fast]
        outputs.append((servo, protocol.SERVO_FREQUENCY))
        self.assertEqual(protocol.pwm_frequency_conflicts(outputs), [])
        # The servo's slice partner must not be a PWM output at all.
        partner = servo ^ 1
        self.assertNotIn(partner, fast)

    def test_analogue_inputs_are_on_adc_pins(self):
        for label in ("POSITION", "BATTERY"):
            self.assertIn(KB2040_GPIO[self.singles[label]], protocol.ADC_GPIOS)

    def test_frequency_clash_is_detected(self):
        self.assertEqual(protocol.pwm_frequency_conflicts([(0, 50), (1, 20000)]), [(0, 1)])
        self.assertEqual(protocol.pwm_frequency_conflicts([(2, 20000), (3, 20000)]), [])


class TestSensorConditioning(unittest.TestCase):
    def test_mechanism_constants_are_consistent(self):
        self.assertEqual(L.problems(), [])
        self.assertIn("seek", " ".join(stance.Limits(seek_mm=5.0).problems()))

    def test_unknown_limit_is_rejected(self):
        with self.assertRaises(AttributeError):
            stance.Limits(stroke=1)

    def test_pot_window(self):
        self.assertIsNone(stance.pot_position_mm(None, L))
        self.assertIsNone(stance.pot_position_mm(0.0, L))      # open wiper or open ref+
        self.assertIsNone(stance.pot_position_mm(3250.0, L))   # open ref-
        self.assertAlmostEqual(stance.pot_position_mm(1375.0, L), 50.0)
        self.assertAlmostEqual(stance.pot_position_mm(L.mv_for_mm(5.0), L), 5.0)

    def test_pot_tolerance_stays_inside_the_window(self):
        for kohm in (5.5, 11.0, 16.5):  # 11 k +/- 50 % with the 2.2 k top resistor
            full = 3300.0 * kohm / (kohm + 2.2)
            self.assertLess(full, L.pot_max_valid_mv)
            self.assertGreater(full, 2000.0)

    def test_contact_pair(self):
        pair = stance.ContactPair(30, 150)
        pair.update(0, True, False)
        self.assertFalse(pair.settled)
        self.assertEqual(pair.code(), "W")
        pair.update(30, True, False)
        self.assertTrue(pair.valid and pair.engaged)
        self.assertEqual(pair.code(), "E")
        pair.update(40, False, False)
        pair.update(140, False, False)
        self.assertTrue(pair.valid and pair.engaged)   # changeover gap keeps the last legal state
        pair.update(150, False, True)
        pair.update(185, False, True)
        self.assertTrue(pair.valid and not pair.engaged)
        pair.update(200, False, False)
        pair.update(350, False, False)
        self.assertFalse(pair.valid)                   # broken COM or wire
        self.assertEqual(pair.code(), "X")
        pair.update(360, True, True)
        pair.update(510, True, True)
        self.assertFalse(pair.valid)                   # short
        pair.update(520, True, False)
        pair.update(550, True, False)
        self.assertTrue(pair.valid and pair.engaged)

    def test_contact_pair_with_the_nc_contact_as_seated(self):
        pair = stance.ContactPair(30, 150, "NC")
        pair.update(0, False, True)
        pair.update(30, False, True)
        self.assertTrue(pair.valid and pair.engaged)
        with self.assertRaises(ValueError):
            stance.ContactPair(30, 150, "COM")

    def test_battery_guard_debounces_dips_and_needs_rearm(self):
        guard = stance.BatteryGuard(11200, 12000, 15200, 500)
        self.assertFalse(guard.update(0, None))
        self.assertTrue(guard.update(10, 12600))
        self.assertTrue(guard.update(20, 10000))
        self.assertTrue(guard.update(320, 10000))     # 300 ms dip: still healthy
        self.assertTrue(guard.update(330, 12500))
        guard.update(340, 11000)
        self.assertFalse(guard.update(840, 11000))    # 500 ms low: unhealthy
        self.assertFalse(guard.update(1500, 11800))   # above cutoff but below re-arm
        guard.update(1510, 12100)
        self.assertFalse(guard.update(1900, 12100))
        self.assertTrue(guard.update(2010, 12100))
        self.assertFalse(guard.update(2020, None))    # sense lost: at once
        guard2 = stance.BatteryGuard()
        guard2.update(0, 12600)
        self.assertFalse(guard2.update(10, 16000))    # not a battery reading: at once

    def test_release_servo_goes_limp_after_engaging(self):
        servo = stance.ReleaseServo(1000, 1311, 1000)
        self.assertEqual(servo.update(0, True), 1000)
        self.assertEqual(servo.update(10, False), 1311)
        self.assertEqual(servo.update(1009, False), 1311)
        self.assertEqual(servo.update(1010, False), 0)
        self.assertEqual(servo.update(2000, True), 1000)

    def test_conversions(self):
        self.assertEqual(stance.servo_duty(1500), 4915)
        self.assertEqual(stance.servo_duty(0), 0)
        self.assertAlmostEqual(stance.adc_to_mv(65535), 3300.0)
        self.assertAlmostEqual(stance.pack_mv_from_node(1656.5), 12699.8, places=1)


class TestProtocolStanceLines(unittest.TestCase):
    def test_stance_request(self):
        self.assertEqual(protocol.parse_command("T 2"), ("T", [2]))
        self.assertEqual(protocol.parse_command("T 3"), ("T", [3]))
        self.assertEqual(protocol.parse_command("T 0"), ("T", [0]))
        for bad in ("T 1", "T", "T 2 3", "T two"):
            with self.assertRaises(protocol.CommandError):
                protocol.parse_command(bad)

    def test_clear(self):
        self.assertEqual(protocol.parse_command("C"), ("C", []))
        with self.assertRaises(protocol.CommandError):
            protocol.parse_command("C 1")

    def test_stance_status_line(self):
        line = protocol.format_stance("RETRACTING", "TRAVEL", "NONE", 51.26, "R", 12603.4,
                                      False, False, False, False, "retracting", "a|b", "")
        self.assertEqual(line, "ss RETRACTING TRAVEL NONE 513 R 12603 0 0 0 0 retracting|a/b|\n")
        line = protocol.format_stance("FAULT", "NONE", "FEEDBACK", None, "X", None,
                                      False, False, False, False, "bad", "x", "y")
        self.assertEqual(line, "ss FAULT NONE FEEDBACK -1 X -1 0 0 0 0 bad|x|y\n")


class TestBoot(unittest.TestCase):
    def test_boot_on_three_feet(self):
        rig = Rig()
        self.assertEqual(rig.s.state, stance.THREE_FOOT)
        self.assertTrue(rig.s.drive_allowed())
        self.assertEqual(rig.plant.actuator, 0)
        self.assertEqual(rig.plant.release_us, stance.ENGAGE_US)
        rig.run(stance.ENGAGE_HOLD_MS)
        self.assertEqual(rig.plant.release_us, 0)
        status = rig.last_status()
        self.assertTrue(status.startswith("ss THREE_FOOT NONE NONE 952 E 12600 1 1 1 0 "), status)

    def test_boot_on_two_feet(self):
        rig = Rig(RECEIVER_TWO, 2)
        self.assertEqual(rig.s.state, stance.TWO_FOOT)
        self.assertFalse(rig.s.drive_allowed())
        self.assertTrue(rig.s.head_allowed())

    def test_boot_between_stances_holds(self):
        rig = Rig(50.0, 0)
        self.assertEqual(rig.s.state, stance.HELD)
        self.assertFalse(rig.s.drive_allowed())
        self.assertFalse(rig.s.head_allowed())
        self.assertIsNone(rig.s.tilt_deg())

    def test_endpoint_without_a_seated_pin_is_not_a_stance(self):
        rig = Rig(L.three_foot_mm, 0)
        self.assertEqual(rig.s.state, stance.HELD)

    def test_stance_waits_for_the_lock_switch_debounce(self):
        plant = Plant()
        core = supervisor.Supervisor(plant, lambda text: None, 0)
        core.tick(10)
        self.assertFalse(core.stance.begun)
        self.assertFalse(core.stance.drive_allowed())
        core.tick(40)
        self.assertTrue(core.stance.begun)

    def test_open_wiper_at_boot_is_a_feedback_fault(self):
        plant = Plant()
        plant.pot_override_mv = 0.0
        core = supervisor.Supervisor(plant, lambda text: None, 0)
        for now in range(10, 100, 10):
            core.tick(now)
        self.assertEqual(core.stance.fault, stance.FEEDBACK)

    def test_inconsistent_constants_refuse_to_start(self):
        with self.assertRaises(ValueError):
            supervisor.Supervisor(Plant(), lambda text: None, 0, stance.Limits(overshoot_mm=9.0))


def retract_to_two(test, rig):
    rig.request = stance.REQUEST_TWO_FOOT
    test.assertTrue(rig.until_state(stance.TWO_FOOT, 60000), rig.s.reason)


class TestTransitions(unittest.TestCase):
    def test_three_feet_to_two_feet_and_back(self):
        rig = Rig()
        rig.request = stance.REQUEST_TWO_FOOT
        rig.run(60)
        self.assertEqual(rig.s.state, stance.RETRACTING)
        self.assertEqual(rig.s.phase, stance.UNLOCKING)
        self.assertEqual(rig.plant.actuator, 0)
        self.assertEqual(rig.plant.release_us, stance.RELEASE_US)
        self.assertFalse(rig.s.drive_allowed())
        self.assertFalse(rig.s.head_allowed())

        self.assertTrue(rig.until_phase(stance.TRAVEL, 1000))
        self.assertEqual(rig.plant.seated, 0)
        rig.run(20)
        self.assertEqual(rig.plant.actuator, -100)
        self.assertEqual(rig.plant.release_us, stance.RELEASE_US)
        clear_at = L.three_foot_mm - L.release_clear_mm
        while rig.s.phase == stance.TRAVEL and rig.plant.mm > clear_at + 0.5:
            rig.step()
            self.assertEqual(rig.plant.release_us, stance.RELEASE_US)
        rig.run(200)
        self.assertEqual(rig.s.phase, stance.TRAVEL)
        self.assertNotEqual(rig.plant.release_us, stance.RELEASE_US)  # pin rides the ring face
        self.assertEqual(rig.plant.seated, 0)

        self.assertTrue(rig.until_phase(stance.LOCKING, 30000))
        self.assertEqual(rig.plant.actuator, 0)
        rig.run(L.lock_settle_ms - 30)
        self.assertEqual(rig.plant.actuator, 0)            # the pin drops before the creep
        rig.run(60)
        self.assertEqual(rig.plant.actuator, -L.seek_duty_percent)
        self.assertTrue(rig.until_state(stance.TWO_FOOT, 5000))
        self.assertEqual(rig.plant.actuator, 0)
        self.assertEqual(rig.plant.seated, 2)
        self.assertFalse(rig.plant.moved_pinned)
        self.assertFalse(rig.plant.foot_output_while_not_parked)
        self.assertFalse(rig.s.drive_allowed())
        self.assertTrue(rig.s.head_allowed())
        self.assertEqual(rig.s.tilt_deg(), 0.0)
        rig.run(2000)
        self.assertEqual(rig.s.state, stance.TWO_FOOT)       # holding the control after arrival does nothing
        self.assertEqual(rig.plant.actuator, 0)

        rig.release()
        self.assertIn("cooling", rig.s.blocked(stance.REQUEST_THREE_FOOT, rig.t, True))
        rig.request = stance.REQUEST_THREE_FOOT
        rig.run(100)
        self.assertEqual(rig.s.state, stance.TWO_FOOT)
        rig.cool()
        self.assertIsNone(rig.s.blocked(stance.REQUEST_THREE_FOOT, rig.t, True))

        rig.request = stance.REQUEST_THREE_FOOT
        rig.run(60)
        self.assertEqual(rig.s.state, stance.DEPLOYING)
        self.assertEqual(rig.s.phase, stance.UNLOCKING)
        self.assertTrue(rig.until_phase(stance.TRAVEL, 1000))
        rig.run(20)
        self.assertEqual(rig.plant.actuator, 100)
        self.assertTrue(rig.until_phase(stance.LOCKING, 30000))
        self.assertNotEqual(rig.plant.release_us, stance.RELEASE_US)
        self.assertTrue(rig.until_state(stance.THREE_FOOT, 10000))
        self.assertEqual(rig.plant.seated, 3)
        self.assertTrue(rig.s.drive_allowed())
        self.assertEqual(rig.s.tilt_deg(), 18.0)
        self.assertFalse(rig.plant.moved_pinned)
        self.assertFalse(rig.plant.foot_output_while_not_parked)
        self.assertEqual(rig.errors, [])
        rig.run(200)
        self.assertTrue(rig.last_status().startswith("ss THREE_FOOT NONE NONE "))

    def test_drive_works_again_after_the_round_trip(self):
        rig = Rig()
        retract_to_two(self, rig)
        rig.cool()
        rig.request = stance.REQUEST_THREE_FOOT
        self.assertTrue(rig.until_state(stance.THREE_FOOT, 60000))
        rig.release()
        rig.drive_line = "M 400 400 400 0"
        rig.run(200)
        self.assertEqual(rig.plant.channels[:3], [400, 400, 400])


class TestCommandLoss(unittest.TestCase):
    def test_pi_link_lost_mid_travel_holds_and_never_restarts_alone(self):
        rig = Rig()
        rig.request = stance.REQUEST_TWO_FOOT
        self.assertTrue(rig.until_phase(stance.TRAVEL, 2000))
        rig.run(3000)
        rig.link = False
        rig.run(protocol.HEARTBEAT_MS + 60)
        self.assertEqual(rig.s.state, stance.HELD)
        self.assertIn("heartbeat", rig.s.reason)
        self.assertEqual(rig.plant.actuator, 0)
        self.assertGreaterEqual(rig.plant.coasted, 1)
        self.assertIn("err heartbeat timeout, motors coasted", rig.errors)
        before = rig.plant.mm
        rig.run(3000)
        self.assertAlmostEqual(rig.plant.mm, before, places=3)
        rig.link = True                                     # link back, control still held
        rig.run(1000)
        self.assertEqual(rig.s.state, stance.HELD)
        self.assertEqual(rig.plant.actuator, 0)
        self.assertIn("release", rig.s.blocked(stance.REQUEST_TWO_FOOT, rig.t, True))
        rig.release()
        rig.cool()
        rig.request = stance.REQUEST_TWO_FOOT
        self.assertTrue(rig.until_state(stance.TWO_FOOT, 60000))

    def test_pi_link_lost_while_unlocking(self):
        rig = Rig()
        rig.request = stance.REQUEST_TWO_FOOT
        rig.run(80)
        self.assertEqual(rig.s.phase, stance.UNLOCKING)
        rig.link = False
        rig.run(protocol.HEARTBEAT_MS + 60)
        self.assertEqual(rig.s.state, stance.HELD)
        self.assertEqual(rig.plant.actuator, 0)

    def test_stance_requests_stop_arriving_mid_deploy(self):
        # What the KB2040 sees when the phone goes silent: the Pi keeps its
        # heartbeat but its stance lease has expired, so T lines stop or read 0.
        rig = Rig(RECEIVER_TWO, 2)
        rig.request = stance.REQUEST_THREE_FOOT
        self.assertTrue(rig.until_phase(stance.TRAVEL, 2000))
        rig.run(2000)
        rig.send_request = False
        rig.run(protocol.HEARTBEAT_MS + 60)
        self.assertEqual(rig.s.state, stance.HELD)
        self.assertIn("released", rig.s.reason)
        self.assertEqual(rig.plant.actuator, 0)
        self.assertEqual(rig.s.fault, stance.NO_FAULT)

    def test_operator_release_mid_change(self):
        rig = Rig()
        rig.request = stance.REQUEST_TWO_FOOT
        self.assertTrue(rig.until_phase(stance.TRAVEL, 2000))
        rig.run(1000)
        rig.request = 0
        rig.run(60)
        self.assertEqual(rig.s.state, stance.HELD)
        self.assertEqual(rig.plant.actuator, 0)

    def test_reversal_mid_change_holds(self):
        rig = Rig()
        rig.request = stance.REQUEST_TWO_FOOT
        self.assertTrue(rig.until_phase(stance.TRAVEL, 2000))
        rig.run(2000)
        rig.request = stance.REQUEST_THREE_FOOT
        rig.run(60)
        self.assertEqual(rig.s.state, stance.HELD)
        rig.cool()
        rig.request = stance.REQUEST_THREE_FOOT
        self.assertTrue(rig.until_state(stance.THREE_FOOT, 60000))
        self.assertEqual(rig.plant.seated, 3)

    def test_stop_and_disarm_hold_a_transition(self):
        for line in ("S", "E 0"):
            rig = Rig()
            rig.request = stance.REQUEST_TWO_FOOT
            self.assertTrue(rig.until_phase(stance.TRAVEL, 2000))
            rig.run(500)
            rig.send(line)
            rig.run(10)
            self.assertEqual(rig.s.state, stance.HELD, line)
            self.assertEqual(rig.plant.actuator, 0, line)

    def test_disarmed_robot_cannot_start(self):
        rig = Rig(armed=False)
        rig.request = stance.REQUEST_TWO_FOOT
        rig.run(500)
        self.assertEqual(rig.s.state, stance.THREE_FOOT)
        self.assertEqual(rig.s.blocked(stance.REQUEST_TWO_FOOT, rig.t, True), "arm the motors first")


class TestPowerAndFeedbackFaults(unittest.TestCase):
    def test_battery_undervoltage_mid_change(self):
        rig = Rig()
        rig.request = stance.REQUEST_TWO_FOOT
        self.assertTrue(rig.until_phase(stance.TRAVEL, 2000))
        rig.run(2000)
        rig.plant.pack_mv = 10800.0
        rig.run(200)
        self.assertEqual(rig.s.state, stance.RETRACTING)   # a short sag is not a fault
        rig.plant.pack_mv = 12400.0
        rig.run(200)
        rig.plant.pack_mv = 10800.0
        rig.run(stance.BATTERY_LOW_MS + 20)
        self.assertEqual(rig.s.state, stance.FAULT)
        self.assertEqual(rig.s.fault, stance.POWER)
        self.assertEqual(rig.plant.actuator, 0)
        self.assertIn("fault", rig.s.blocked(stance.REQUEST_TWO_FOOT, rig.t, True))
        rig.plant.pack_mv = 12600.0
        rig.run(stance.BATTERY_LOW_MS + 20)
        rig.release()
        rig.send("C")
        self.assertEqual(rig.lines[-1], "ok\n")
        self.assertEqual(rig.s.state, stance.HELD)
        rig.cool()
        rig.request = stance.REQUEST_TWO_FOOT
        self.assertTrue(rig.until_state(stance.TWO_FOOT, 60000))

    def test_pot_open_mid_change_latches_until_feedback_returns(self):
        rig = Rig(RECEIVER_TWO, 2)
        rig.request = stance.REQUEST_THREE_FOOT
        self.assertTrue(rig.until_phase(stance.TRAVEL, 2000))
        rig.run(2000)
        rig.plant.pot_override_mv = 0.0
        rig.run(10)
        self.assertEqual(rig.s.fault, stance.FEEDBACK)
        self.assertEqual(rig.plant.actuator, 0)
        rig.release()
        rig.send("C")
        self.assertTrue(rig.errors[-1].startswith("err fault not cleared"))
        self.assertEqual(rig.s.state, stance.FAULT)
        rig.plant.pot_override_mv = None
        rig.run(20)
        rig.send("C")
        self.assertEqual(rig.s.state, stance.HELD)

    def test_pot_reference_open_reads_high(self):
        rig = Rig()
        rig.plant.pot_override_mv = 3250.0
        rig.run(20)
        self.assertEqual(rig.s.fault, stance.FEEDBACK)
        self.assertFalse(rig.s.drive_allowed())

    def test_reversed_actuator_wiring(self):
        rig = Rig()
        rig.plant.reversed_drive = True
        rig.request = stance.REQUEST_TWO_FOOT
        rig.run(3000)
        self.assertEqual(rig.s.fault, stance.REVERSED_FEEDBACK)
        self.assertEqual(rig.plant.actuator, 0)

    def test_drift_off_a_parked_endpoint(self):
        # The lock window lies inside the hold tolerance, so a seated reading off
        # the endpoint is LOCK_DISAGREES; DRIFT is the released-and-moved case.
        machine = stance.Stance(L)
        parked = stance.Sample(L.two_foot_mm, True, True, True, True, True)
        machine.tick(0, parked, 0, True)
        self.assertEqual(machine.state, stance.TWO_FOOT)
        moved = stance.Sample(L.two_foot_mm + L.hold_tolerance_mm + 0.5, True, False, True, True, True)
        machine.tick(10, moved, 0, True)
        self.assertEqual(machine.fault, stance.DRIFT)
        self.assertEqual(machine.actuator, 0)


class TestStallAndTimeout(unittest.TestCase):
    def test_stall_mid_travel(self):
        rig = Rig()
        rig.request = stance.REQUEST_TWO_FOOT
        self.assertTrue(rig.until_phase(stance.TRAVEL, 2000))
        rig.run(1500)
        rig.plant.stalled = True
        rig.run(L.progress_ms + 30)
        self.assertEqual(rig.s.fault, stance.STALL)
        self.assertEqual(rig.plant.actuator, 0)

    def test_travel_timeout(self):
        rig = Rig()
        rig.plant.speed = (L.progress_mm * 1.3) / L.progress_ms  # moving, far too slowly
        rig.request = stance.REQUEST_TWO_FOOT
        rig.run(L.travel_timeout_ms + 1500)
        self.assertEqual(rig.s.fault, stance.TRAVEL_TIMEOUT)
        self.assertEqual(rig.plant.actuator, 0)

    def test_pin_will_not_leave_the_receiver(self):
        rig = Rig()
        rig.plant.stuck_seated = True
        rig.request = stance.REQUEST_TWO_FOOT
        rig.run(L.lock_timeout_ms + 100)
        self.assertEqual(rig.s.fault, stance.LOCK_TIMEOUT)
        self.assertEqual(rig.plant.actuator, 0)
        self.assertFalse(rig.plant.moved_pinned)
        self.assertAlmostEqual(rig.plant.mm, RECEIVER_THREE)


class TestLockSensor(unittest.TestCase):
    def test_both_contacts_open_is_invalid_after_the_changeover_allowance(self):
        rig = Rig()
        rig.plant.contacts_override = (False, False)
        rig.run(100)
        self.assertEqual(rig.s.state, stance.THREE_FOOT)
        rig.run(80)
        self.assertEqual(rig.s.fault, stance.LOCK_SENSOR)
        self.assertFalse(rig.s.drive_allowed())

    def test_both_contacts_closed_mid_travel(self):
        rig = Rig()
        rig.request = stance.REQUEST_TWO_FOOT
        self.assertTrue(rig.until_phase(stance.TRAVEL, 2000))
        rig.run(2000)
        rig.plant.contacts_override = (True, True)
        rig.run(stance.LOCK_ILLEGAL_MS + 20)
        self.assertEqual(rig.s.fault, stance.LOCK_SENSOR)
        self.assertEqual(rig.plant.actuator, 0)

    def test_parked_on_two_feet_but_switch_reads_released(self):
        rig = Rig(RECEIVER_TWO, 2)
        rig.plant.contacts_override = (False, True)
        rig.run(60)
        self.assertEqual(rig.s.fault, stance.LOCK_DISAGREES)
        self.assertFalse(rig.s.head_allowed())
        rig.run(2000)
        self.assertEqual(rig.s.state, stance.FAULT)          # latched
        # Clearing with the pin still unseated gives HELD, not a stance: nothing
        # moves and both drive and dome stay refused.
        rig.send("C")
        self.assertEqual(rig.s.state, stance.HELD)
        self.assertFalse(rig.s.drive_allowed())
        self.assertFalse(rig.s.head_allowed())
        rig.plant.contacts_override = None
        rig.run(60)
        rig.request = stance.REQUEST_TWO_FOOT                # a fresh press re-seats nothing, it confirms
        rig.run(60)
        self.assertEqual(rig.s.state, stance.TWO_FOOT)
        self.assertEqual(rig.plant.actuator, 0)

    def test_switch_reads_seated_away_from_both_receivers(self):
        rig = Rig()
        rig.request = stance.REQUEST_TWO_FOOT
        self.assertTrue(rig.until_phase(stance.TRAVEL, 2000))
        rig.run(4000)
        rig.plant.contacts_override = (True, False)
        rig.run(60)
        self.assertEqual(rig.s.fault, stance.LOCK_DISAGREES)
        self.assertEqual(rig.plant.actuator, 0)

    def test_pin_never_seats_at_the_two_foot_endpoint(self):
        rig = Rig()
        rig.plant.jammed = True
        rig.request = stance.REQUEST_TWO_FOOT
        self.assertTrue(rig.until_phase(stance.LOCKING, 40000))
        rig.run(L.lock_settle_ms + 2000 + L.lock_timeout_ms)
        self.assertEqual(rig.s.fault, stance.LOCK_TIMEOUT)
        self.assertIn("not seated", rig.s.reason)
        self.assertEqual(rig.plant.actuator, 0)
        self.assertGreaterEqual(rig.plant.mm, L.two_foot_mm - L.overshoot_mm - L.stop_tolerance_mm - 0.1)

    def test_pin_never_seats_at_the_three_foot_endpoint_so_no_drive(self):
        rig = Rig(RECEIVER_TWO, 2)
        rig.request = stance.REQUEST_THREE_FOOT
        self.assertTrue(rig.until_phase(stance.TRAVEL, 2000))
        rig.plant.jammed = True
        self.assertTrue(rig.until_phase(stance.LOCKING, 40000))
        rig.run(L.lock_settle_ms + 2000 + L.lock_timeout_ms)
        self.assertEqual(rig.s.fault, stance.LOCK_TIMEOUT)
        self.assertFalse(rig.s.drive_allowed())
        self.assertLessEqual(rig.plant.mm, L.three_foot_mm + L.overtravel_mm)


class TestDriveRefusal(unittest.TestCase):
    def test_drive_on_three_feet_is_accepted(self):
        rig = Rig()
        rig.drive_line = "M 400 -400 400 250"
        rig.run(300)
        self.assertEqual(rig.plant.channels, [400, -400, 400, 250])
        self.assertEqual(rig.errors, [])

    def test_stance_start_waits_for_the_wheels_to_stop(self):
        rig = Rig()
        rig.drive_line = "M 400 400 400 0"
        rig.run(200)
        rig.request = stance.REQUEST_TWO_FOOT
        rig.run(300)
        self.assertEqual(rig.s.state, stance.THREE_FOOT)
        self.assertEqual(rig.plant.actuator, 0)
        self.assertIn("stop the wheels", rig.s.blocked(stance.REQUEST_TWO_FOOT, rig.t, rig.core.drive_idle))
        rig.drive_line = "M 0 0 0 0"
        rig.run(300)
        self.assertEqual(rig.s.state, stance.RETRACTING)    # still held: starts once idle

    def test_drive_refused_during_a_transition(self):
        rig = Rig()
        rig.request = stance.REQUEST_TWO_FOOT
        self.assertTrue(rig.until_phase(stance.TRAVEL, 2000))
        rig.run(500)
        rig.send("M 500 500 500 0")
        self.assertEqual(rig.errors[-1],
                         "err drive refused (ground drive): stance change in progress")
        rig.run(100)
        self.assertEqual(rig.plant.channels, [0, 0, 0, 0])
        self.assertEqual(rig.s.state, stance.HELD)
        self.assertEqual(rig.plant.actuator, 0)
        self.assertFalse(rig.plant.foot_output_while_not_parked)

    def test_dome_refused_during_a_transition(self):
        rig = Rig()
        rig.request = stance.REQUEST_TWO_FOOT
        rig.run(60)
        rig.send("M 0 0 0 300")
        self.assertEqual(rig.errors[-1], "err drive refused (dome): stance change in progress")
        self.assertEqual(rig.s.state, stance.HELD)

    def test_drive_refused_on_two_feet_but_dome_allowed(self):
        rig = Rig(RECEIVER_TWO, 2)
        rig.drive_line = "M 500 500 500 300"
        rig.run(300)
        self.assertIn("err drive refused (ground drive): the two-foot stance is stationary", rig.errors)
        self.assertEqual(rig.plant.channels, [0, 0, 0, 300])
        self.assertEqual(rig.s.state, stance.TWO_FOOT)
        self.assertFalse(rig.plant.foot_output_while_not_parked)

    def test_drive_and_dome_refused_in_fault_and_unknown_states(self):
        rig = Rig()
        rig.plant.pot_override_mv = 0.0
        rig.run(20)
        rig.drive_line = "M 500 500 500 300"
        rig.run(300)
        self.assertIn("err drive refused (ground drive and dome): stance fault latched", rig.errors)
        self.assertEqual(rig.plant.channels, [0, 0, 0, 0])
        held = Rig(50.0, 0)
        held.drive_line = "M 500 0 0 0"
        held.run(100)
        self.assertTrue(held.errors[-1].startswith("err drive refused (ground drive): stance not locked"))
        self.assertEqual(held.plant.channels, [0, 0, 0, 0])

    def test_a_fault_while_driving_stops_the_wheels_at_once(self):
        rig = Rig()
        rig.drive_line = "M 600 600 600 0"
        rig.run(300)
        self.assertEqual(rig.plant.channels[:3], [600, 600, 600])
        rig.plant.contacts_override = (False, True)
        rig.run(50)
        self.assertEqual(rig.s.fault, stance.LOCK_DISAGREES)
        self.assertEqual(rig.plant.channels, [0, 0, 0, 0])


class TestFaultLatchAndClear(unittest.TestCase):
    def test_fault_stays_latched_until_cleared_and_needs_a_fresh_press(self):
        rig = Rig()
        rig.request = stance.REQUEST_TWO_FOOT
        self.assertTrue(rig.until_phase(stance.TRAVEL, 2000))
        rig.run(1500)
        rig.plant.stalled = True
        rig.run(L.progress_ms + 30)
        self.assertEqual(rig.s.fault, stance.STALL)
        rig.plant.stalled = False
        rig.run(3000)                                        # cause gone, control still held
        self.assertEqual(rig.s.state, stance.FAULT)
        self.assertEqual(rig.plant.actuator, 0)
        self.assertFalse(rig.s.drive_allowed())
        self.assertTrue(rig.last_status().startswith("ss FAULT NONE STALL "))
        rig.send("C")                                        # clear while the control is still held
        self.assertEqual(rig.lines[-1], "ok\n")
        self.assertEqual(rig.s.state, stance.HELD)
        rig.cool()
        rig.request = stance.REQUEST_TWO_FOOT
        rig.run(10)
        # cool() released the control, so this press is fresh and resumes the retract.
        self.assertTrue(rig.until_state(stance.TWO_FOOT, 60000))

    def test_clear_after_a_hold_is_not_needed_and_clear_without_fault_is_refused(self):
        rig = Rig()
        rig.send("C")
        self.assertEqual(rig.errors[-1], "err no stance fault latched")

    def test_clear_keeps_the_press_consumed(self):
        rig = Rig()
        rig.request = stance.REQUEST_TWO_FOOT
        self.assertTrue(rig.until_phase(stance.TRAVEL, 2000))
        rig.run(1500)
        rig.plant.pot_override_mv = 0.0
        rig.run(20)
        rig.plant.pot_override_mv = None
        rig.run(20)
        rig.send("C")
        rig.run(200000)                                      # control held the whole time
        self.assertEqual(rig.s.state, stance.HELD)
        self.assertEqual(rig.plant.actuator, 0)
        self.assertIn("release", rig.s.blocked(stance.REQUEST_TWO_FOOT, rig.t, True))


if __name__ == "__main__":
    unittest.main(verbosity=2)
