"""Host tests for the revision D stance interlock, the supervisor and the pin plan.

A simulated plant stands in for the actuator, the two spring-return shoulder
lock pins (each with a tilt-0 receiver and a tilt-18 receiver), the two NO/NC
lock switches, the release servos, the battery and the motors.  The real
``supervisor.Supervisor`` and ``stance.Stance`` run against it, fed through the
real serial protocol.

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
TWO_FOOT_POS = L.two_foot_mm
CONTACT_POS = L.contact_mm
RECEIVER_THREE = L.three_foot_mm + 0.2  # real receiver slightly off nominal: exercises the seek
BAND_CONTACT = 0.05  # 0.1 mm radial pin clearance at 2.2 deg/mm
BAND_THREE = 0.3     # the same clearance at 0.31 deg/mm


class Pin:
    """One spring-return plunger pin and its lock switch."""

    def __init__(self, seated):
        self.seated = seated      # 0 out, 2 tilt-0 receiver, 3 tilt-18 receiver
        self.stuck = False        # will not leave its receiver
        self.jammed = False       # will not enter a receiver
        self.override = None      # forced (no_closed, nc_closed) switch reading
        self.pending_at = None


class Plant:
    """Non-backdrivable lead-screw actuator and two shoulder lock pins."""

    def __init__(self, mm=RECEIVER_THREE, seated=3):
        self.mm = mm
        self.pins = [Pin(seated), Pin(seated)]
        self.speed = stance.ACTUATOR_NO_LOAD_SPEED_MM_S / 1000.0  # mm per ms at 100 %
        self.actuator = 0
        self.release_us = [0, 0]
        self.enabled = False
        self.channels = [0, 0, 0, 0]
        self.coasted = 0
        self.pack_mv = 12600.0
        self.pot_override_mv = None
        self.stalled = False
        self.reversed_drive = False
        self.seat_delay = 30
        self.pull_delay = 80
        self.pinned_ms = 0
        self.foot_output_while_not_parked = False

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
        readings = []
        for pin in self.pins:
            if pin.override is not None:
                readings.append(pin.override)
            else:
                readings.append((pin.seated != 0, pin.seated == 0))  # NO closes when seated
        return readings

    def read_battery_mv(self):
        return self.pack_mv

    def drive_actuator(self, percent):
        self.actuator = percent

    def set_release_pulses(self, pulses_us):
        self.release_us = list(pulses_us)

    # -- physics ----------------------------------------------------------

    def releasing(self, index):
        return self.release_us[index] == stance.RELEASE_US[index]

    def pulled(self):
        return self.releasing(0) and self.releasing(1)

    def seated(self):
        return [pin.seated for pin in self.pins]

    def aligned(self):
        if self.mm <= CONTACT_POS + BAND_CONTACT:
            return 2  # the body is upright for every stroke up to touchdown
        if abs(self.mm - RECEIVER_THREE) <= BAND_THREE:
            return 3
        return 0

    def blocked(self, following):
        for pin in self.pins:
            if pin.seated == 2 and following > CONTACT_POS + BAND_CONTACT:
                return True
            if pin.seated == 3 and abs(following - RECEIVER_THREE) > BAND_THREE:
                return True
        return False

    def physics(self, now, dt):
        if self.actuator and not self.stalled and self.pack_mv > 9000:
            step = (self.actuator / 100.0) * self.speed * dt
            if self.reversed_drive:
                step = -step
            following = self.mm + step
            if self.blocked(following):
                self.pinned_ms += dt
            else:
                self.mm = following
        for index, pin in enumerate(self.pins):
            if pin.stuck:
                want = pin.seated
            elif self.releasing(index):
                want = 0
            elif pin.seated == 0 and not pin.jammed:
                want = self.aligned()
            else:
                want = pin.seated
            if want != pin.seated:
                if pin.pending_at is None:
                    pin.pending_at = now + (self.seat_delay if want else self.pull_delay)
                elif now >= pin.pending_at:
                    pin.seated = want
                    pin.pending_at = None
            else:
                pin.pending_at = None


class Rig:
    """Supervisor + plant + a stand-in Pi that sends M and T lines every 50 ms."""

    def __init__(self, mm=RECEIVER_THREE, seated=3, armed=True, jammed=False):
        self.plant = Plant(mm, seated)
        for pin in self.plant.pins:
            pin.jammed = jammed  # keep deliberately unseated pins out of an aligned receiver
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
        if self.s.state != stance.THREE_FOOT and any(self.plant.channels[:3]):
            self.plant.foot_output_while_not_parked = True

    def run(self, ms):
        for _ in range(int(ms) // 10):
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

    def gpio(self, label):
        return int(re.search(r"^{0}_GPIO\s*=\s*(\d+)".format(label), self.source, re.M).group(1))

    def test_four_drive_outputs(self):
        self.assertEqual([entry[0] for entry in self.drives], ["left", "right", "centre", "head"])

    def test_declared_gpio_numbers_match_the_board_names(self):
        for _name, pwm, pwm_gpio, digital, dig_gpio in self.drives:
            self.assertEqual(KB2040_GPIO[pwm], int(pwm_gpio))
            self.assertEqual(KB2040_GPIO[digital], int(dig_gpio))
        self.assertEqual(KB2040_GPIO[self.actuator[0]], int(self.actuator[1]))
        self.assertEqual(KB2040_GPIO[self.actuator[2]], int(self.actuator[3]))
        for label in ("RELEASE_SERVO_LEFT", "RELEASE_SERVO_RIGHT", "LOCK_LEFT_NO", "LOCK_LEFT_NC",
                      "LOCK_RIGHT_NO", "LOCK_RIGHT_NC", "POSITION", "BATTERY"):
            self.assertEqual(KB2040_GPIO[self.singles[label]], self.gpio(label), label)

    def test_every_gpio_is_used_exactly_once(self):
        used = []
        for _name, pwm, _a, digital, _b in self.drives:
            used += [pwm, digital]
        used += [self.actuator[0], self.actuator[2]]
        used += list(self.singles.values())
        self.assertEqual(len(used), len(set(used)), used)
        self.assertEqual(sorted(used), sorted(KB2040_GPIO))
        self.assertNotIn("ENABLE_PIN", self.source)  # SLP is tied to 3V3 in revision D

    def test_pwm_pins_do_not_share_an_output_or_a_frequency(self):
        fast = [int(entry[2]) for entry in self.drives] + [int(self.actuator[1])]
        servos = [self.gpio("RELEASE_SERVO_LEFT"), self.gpio("RELEASE_SERVO_RIGHT")]
        self.assertEqual(protocol.pwm_conflicts(fast + servos), [])
        outputs = [(gpio, protocol.PWM_FREQUENCY) for gpio in fast]
        outputs += [(gpio, protocol.SERVO_FREQUENCY) for gpio in servos]
        self.assertEqual(protocol.pwm_frequency_conflicts(outputs), [])
        for servo in servos:
            self.assertNotIn(servo ^ 1, fast)

    def test_analogue_inputs_are_on_adc_pins(self):
        for label in ("POSITION", "BATTERY"):
            self.assertIn(KB2040_GPIO[self.singles[label]], protocol.ADC_GPIOS)

    def test_frequency_clash_is_detected(self):
        self.assertEqual(protocol.pwm_frequency_conflicts([(0, 50), (1, 20000)]), [(0, 1)])
        self.assertEqual(protocol.pwm_frequency_conflicts([(0, 50), (1, 50)]), [])


class TestSensorConditioning(unittest.TestCase):
    def test_mechanism_constants_are_consistent(self):
        self.assertEqual(L.problems(), [])
        self.assertIn("seek", " ".join(stance.Limits(seek_mm=5.0).problems()))
        self.assertIn("overlap", " ".join(stance.Limits(three_foot_mm=33.0).problems()))

    def test_unknown_limit_is_rejected(self):
        with self.assertRaises(AttributeError):
            stance.Limits(stroke=1)

    def test_pot_window(self):
        self.assertIsNone(stance.pot_position_mm(None, L))
        self.assertIsNone(stance.pot_position_mm(0.0, L))      # open wiper or open pot +
        self.assertIsNone(stance.pot_position_mm(3250.0, L))   # open pot -
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

    def test_lock_set_needs_both_locks(self):
        locks = stance.LockSet(2, 50, 150)
        locks.update(0, [(True, False), (True, False)])
        self.assertFalse(locks.settled())
        locks.update(50, [(True, False), (True, False)])
        self.assertTrue(locks.settled() and locks.all_engaged() and locks.any_engaged())
        self.assertEqual(locks.code(), "EE")
        locks.update(60, [(True, False), (False, True)])
        locks.update(110, [(True, False), (False, True)])
        self.assertTrue(locks.valid())
        self.assertFalse(locks.all_engaged())
        self.assertTrue(locks.any_engaged())
        self.assertEqual(locks.code(), "ER")
        locks.update(120, [(True, True), (False, True)])
        locks.update(270, [(True, True), (False, True)])
        self.assertFalse(locks.valid())
        self.assertFalse(locks.any_engaged())
        self.assertEqual(locks.code(), "XR")
        with self.assertRaises(ValueError):
            locks.update(280, [(True, False)])

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
        other = stance.BatteryGuard()
        other.update(0, 12600)
        self.assertFalse(other.update(10, 16000))     # not a battery reading: at once

    def test_release_servo_goes_limp_after_engaging(self):
        servo = stance.ReleaseServo(1310, 1500, 1000)
        self.assertEqual(servo.update(0, True), 1310)
        self.assertEqual(servo.update(10, False), 1500)
        self.assertEqual(servo.update(1009, False), 1500)
        self.assertEqual(servo.update(1010, False), 0)
        self.assertEqual(servo.update(2000, True), 1310)

    def test_mirrored_release_pulses(self):
        self.assertEqual(stance.RELEASE_US[0] + stance.RELEASE_US[1], 2 * stance.ENGAGE_US[0])

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
        line = protocol.format_stance("RETRACTING", "TILT", "NONE", 51.26, "RR", 12603.4,
                                      False, False, False, False, "retracting", "a|b", "")
        self.assertEqual(line, "ss RETRACTING TILT NONE 513 RR 12603 0 0 0 0 retracting|a/b|\n")
        line = protocol.format_stance("FAULT", "NONE", "FEEDBACK", None, "XE", None,
                                      False, False, False, False, "bad", "x", "y")
        self.assertEqual(line, "ss FAULT NONE FEEDBACK -1 XE -1 0 0 0 0 bad|x|y\n")


class TestBoot(unittest.TestCase):
    def test_boot_on_three_feet(self):
        rig = Rig()
        self.assertEqual(rig.s.state, stance.THREE_FOOT)
        self.assertTrue(rig.s.drive_allowed())
        self.assertEqual(rig.plant.actuator, 0)
        self.assertEqual(rig.plant.release_us, list(stance.ENGAGE_US))
        rig.run(stance.ENGAGE_HOLD_MS)
        self.assertEqual(rig.plant.release_us, [0, 0])
        status = rig.last_status()
        self.assertTrue(status.startswith("ss THREE_FOOT NONE NONE 625 EE 12600 1 1 1 0 "), status)
        self.assertEqual(rig.s.tilt_deg(), 18.0)

    def test_boot_on_two_feet(self):
        rig = Rig(TWO_FOOT_POS, 2)
        self.assertEqual(rig.s.state, stance.TWO_FOOT)
        self.assertFalse(rig.s.drive_allowed())
        self.assertTrue(rig.s.head_allowed())
        self.assertEqual(rig.s.tilt_deg(), 0.0)

    def test_boot_between_stances_holds(self):
        rig = Rig(45.0, 0)
        self.assertEqual(rig.s.state, stance.HELD)
        self.assertFalse(rig.s.drive_allowed())
        self.assertFalse(rig.s.head_allowed())
        self.assertIsNone(rig.s.tilt_deg())

    def test_endpoint_without_seated_pins_is_not_a_stance(self):
        rig = Rig(L.three_foot_mm, 0, jammed=True)
        self.assertEqual(rig.s.state, stance.HELD)

    def test_raised_foot_without_seated_locks_is_a_fault(self):
        rig = Rig(20.0, 0, jammed=True)
        self.assertEqual(rig.s.fault, stance.LOCK_DISAGREES)

    def test_stance_waits_for_the_lock_switch_debounce(self):
        plant = Plant()
        core = supervisor.Supervisor(plant, lambda text: None, 0)
        core.tick(10)
        self.assertFalse(core.stance.begun)
        self.assertFalse(core.stance.drive_allowed())
        core.tick(60)
        self.assertTrue(core.stance.begun)

    def test_open_wiper_at_boot_is_a_feedback_fault(self):
        plant = Plant()
        plant.pot_override_mv = 0.0
        core = supervisor.Supervisor(plant, lambda text: None, 0)
        for now in range(10, 120, 10):
            core.tick(now)
        self.assertEqual(core.stance.fault, stance.FEEDBACK)

    def test_inconsistent_constants_refuse_to_start(self):
        with self.assertRaises(ValueError):
            supervisor.Supervisor(Plant(), lambda text: None, 0, stance.Limits(overshoot_mm=9.0))


class TestTransitions(unittest.TestCase):
    def test_three_feet_to_two_feet_and_back(self):
        rig = Rig()
        rig.request = stance.REQUEST_TWO_FOOT
        rig.run(60)
        self.assertEqual(rig.s.state, stance.RETRACTING)
        self.assertEqual(rig.s.phase, stance.UNLOCKING)
        self.assertEqual(rig.plant.actuator, 0)
        self.assertTrue(rig.plant.pulled())
        self.assertFalse(rig.s.drive_allowed())
        self.assertFalse(rig.s.head_allowed())

        self.assertTrue(rig.until_phase(stance.TILT, 1000))
        self.assertEqual(rig.plant.seated(), [0, 0])
        rig.run(20)
        self.assertEqual(rig.plant.actuator, -100)
        self.assertTrue(rig.plant.pulled())
        while rig.s.phase == stance.TILT and rig.plant.mm > L.release_drop_retract_mm + 0.5:
            rig.step()
            self.assertTrue(rig.plant.pulled())
        rig.run(200)
        self.assertEqual(rig.s.phase, stance.TILT)
        self.assertFalse(rig.plant.releasing(0) or rig.plant.releasing(1))  # pins ride the ring face
        self.assertEqual(rig.plant.seated(), [0, 0])

        self.assertTrue(rig.until_phase(stance.LOCKING, 30000))
        self.assertEqual(rig.plant.actuator, 0)
        rig.run(L.lock_settle_ms - 30)
        self.assertEqual(rig.plant.actuator, 0)               # the pins drop before the creep
        rig.run(60)
        self.assertEqual(rig.plant.actuator, -L.seek_duty_percent)
        self.assertTrue(rig.until_phase(stance.LIFT, 5000))
        self.assertEqual(rig.plant.seated(), [2, 2])
        rig.run(20)
        self.assertEqual(rig.plant.actuator, -100)            # lifting the foot, locks carry the body
        self.assertTrue(rig.until_state(stance.TWO_FOOT, 30000))
        self.assertEqual(rig.plant.actuator, 0)
        self.assertEqual(rig.plant.seated(), [2, 2])
        self.assertLessEqual(rig.plant.pinned_ms, 100)
        self.assertFalse(rig.plant.foot_output_while_not_parked)
        self.assertFalse(rig.s.drive_allowed())
        self.assertTrue(rig.s.head_allowed())
        rig.run(2000)
        self.assertEqual(rig.s.state, stance.TWO_FOOT)        # holding the control after arrival does nothing
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
        self.assertEqual(rig.s.phase, stance.LOWER)
        self.assertEqual(rig.plant.actuator, 100)
        self.assertFalse(rig.plant.releasing(0) or rig.plant.releasing(1))
        self.assertTrue(rig.until_phase(stance.UNLOCKING, 20000))
        self.assertEqual(rig.plant.actuator, 0)
        self.assertTrue(rig.plant.pulled())
        self.assertTrue(rig.until_phase(stance.TILT, 1000))
        rig.run(20)
        self.assertEqual(rig.plant.actuator, 100)
        while rig.s.phase == stance.TILT and rig.plant.mm < L.release_drop_deploy_mm - 0.5:
            rig.step()
            self.assertTrue(rig.plant.pulled())
        self.assertTrue(rig.until_phase(stance.LOCKING, 30000))
        self.assertFalse(rig.plant.releasing(0) or rig.plant.releasing(1))
        self.assertTrue(rig.until_state(stance.THREE_FOOT, 10000))
        self.assertEqual(rig.plant.seated(), [3, 3])
        self.assertTrue(rig.s.drive_allowed())
        self.assertLessEqual(rig.plant.pinned_ms, 100)
        self.assertFalse(rig.plant.foot_output_while_not_parked)
        self.assertEqual(rig.errors, [])
        rig.run(200)
        self.assertTrue(rig.last_status().startswith("ss THREE_FOOT NONE NONE "))

    def test_drive_works_again_after_the_round_trip(self):
        rig = Rig()
        rig.request = stance.REQUEST_TWO_FOOT
        self.assertTrue(rig.until_state(stance.TWO_FOOT, 60000))
        rig.cool()
        rig.request = stance.REQUEST_THREE_FOOT
        self.assertTrue(rig.until_state(stance.THREE_FOOT, 60000))
        rig.release()
        rig.drive_line = "M 400 400 400 0"
        rig.run(200)
        self.assertEqual(rig.plant.channels[:3], [400, 400, 400])


class TestCommandLoss(unittest.TestCase):
    def test_pi_link_lost_while_the_locks_carry_the_raised_foot(self):
        rig = Rig()
        rig.request = stance.REQUEST_TWO_FOOT
        self.assertTrue(rig.until_phase(stance.LIFT, 40000))
        rig.run(1000)
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
        self.assertEqual(rig.plant.seated(), [2, 2])
        self.assertEqual(rig.s.tilt_deg(), 0.0)
        rig.link = True                                      # link back, control still held
        rig.run(1000)
        self.assertEqual(rig.s.state, stance.HELD)
        self.assertEqual(rig.plant.actuator, 0)
        self.assertIn("release", rig.s.blocked(stance.REQUEST_TWO_FOOT, rig.t, True))
        rig.release()
        rig.cool()
        rig.request = stance.REQUEST_TWO_FOOT
        rig.run(60)
        self.assertEqual(rig.s.phase, stance.LIFT)
        self.assertTrue(rig.until_state(stance.TWO_FOOT, 60000))

    def test_pi_link_lost_mid_tilt(self):
        rig = Rig()
        rig.request = stance.REQUEST_TWO_FOOT
        self.assertTrue(rig.until_phase(stance.TILT, 2000))
        rig.run(2000)
        rig.link = False
        rig.run(protocol.HEARTBEAT_MS + 60)
        self.assertEqual(rig.s.state, stance.HELD)
        self.assertEqual(rig.plant.actuator, 0)
        self.assertIsNone(rig.s.tilt_deg())

    def test_pi_link_lost_while_unlocking(self):
        rig = Rig()
        rig.request = stance.REQUEST_TWO_FOOT
        rig.run(60)
        self.assertEqual(rig.s.phase, stance.UNLOCKING)
        rig.link = False
        rig.run(protocol.HEARTBEAT_MS + 60)
        self.assertEqual(rig.s.state, stance.HELD)
        self.assertEqual(rig.plant.actuator, 0)

    def test_stance_requests_stop_arriving_mid_deploy(self):
        # What the KB2040 sees when the phone goes silent: the Pi keeps its
        # heartbeat but its stance lease has expired, so T lines stop or read 0.
        rig = Rig(TWO_FOOT_POS, 2)
        rig.request = stance.REQUEST_THREE_FOOT
        self.assertTrue(rig.until_phase(stance.TILT, 20000))
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
        self.assertTrue(rig.until_phase(stance.TILT, 2000))
        rig.run(1000)
        rig.request = 0
        rig.run(60)
        self.assertEqual(rig.s.state, stance.HELD)
        self.assertEqual(rig.plant.actuator, 0)

    def test_reversal_mid_change_holds(self):
        rig = Rig()
        rig.request = stance.REQUEST_TWO_FOOT
        self.assertTrue(rig.until_phase(stance.TILT, 2000))
        rig.run(2000)
        rig.request = stance.REQUEST_THREE_FOOT
        rig.run(60)
        self.assertEqual(rig.s.state, stance.HELD)
        rig.cool()
        rig.request = stance.REQUEST_THREE_FOOT
        self.assertTrue(rig.until_state(stance.THREE_FOOT, 60000))
        self.assertEqual(rig.plant.seated(), [3, 3])

    def test_stop_and_disarm_hold_a_transition(self):
        for line in ("S", "E 0"):
            rig = Rig()
            rig.request = stance.REQUEST_TWO_FOOT
            self.assertTrue(rig.until_phase(stance.TILT, 2000))
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
        self.assertTrue(rig.until_phase(stance.TILT, 2000))
        rig.run(2000)
        rig.plant.pack_mv = 10800.0
        rig.run(200)
        self.assertEqual(rig.s.state, stance.RETRACTING)    # a short sag is not a fault
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

    def test_pot_open_while_lowering_latches_until_feedback_returns(self):
        rig = Rig(TWO_FOOT_POS, 2)
        rig.request = stance.REQUEST_THREE_FOOT
        self.assertTrue(rig.until_phase(stance.LOWER, 2000))
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
        rig = Rig(TWO_FOOT_POS, 2)
        rig.plant.reversed_drive = True
        rig.request = stance.REQUEST_THREE_FOOT
        rig.run(3000)
        self.assertEqual(rig.s.fault, stance.REVERSED_FEEDBACK)
        self.assertEqual(rig.plant.actuator, 0)

    def test_drift_off_a_parked_endpoint(self):
        machine = stance.Stance(L)
        parked = stance.Sample(L.two_foot_mm, True, True, True, True, True, True)
        machine.tick(0, parked, 0, True)
        self.assertEqual(machine.state, stance.TWO_FOOT)
        moved = stance.Sample(L.two_foot_mm + L.hold_tolerance_mm + 0.5, True, True, True, True, True, True)
        machine.tick(10, moved, 0, True)
        self.assertEqual(machine.fault, stance.DRIFT)
        self.assertEqual(machine.actuator, 0)


class TestStallAndTimeout(unittest.TestCase):
    def test_stall_mid_tilt(self):
        rig = Rig()
        rig.request = stance.REQUEST_TWO_FOOT
        self.assertTrue(rig.until_phase(stance.TILT, 2000))
        rig.run(1500)
        rig.plant.stalled = True
        rig.run(L.progress_ms + 30)
        self.assertEqual(rig.s.fault, stance.STALL)
        self.assertEqual(rig.plant.actuator, 0)

    def test_tilt_timeout(self):
        rig = Rig()
        rig.plant.speed = (L.progress_mm * 1.3) / L.progress_ms  # moving, far too slowly
        rig.request = stance.REQUEST_TWO_FOOT
        rig.run(L.tilt_timeout_ms + 1500)
        self.assertEqual(rig.s.fault, stance.TRAVEL_TIMEOUT)
        self.assertIn("TILT", rig.s.reason)
        self.assertEqual(rig.plant.actuator, 0)

    def test_lift_timeout(self):
        rig = Rig(TWO_FOOT_POS, 2)
        rig.plant.speed = (L.progress_mm * 1.3) / L.progress_ms
        rig.request = stance.REQUEST_THREE_FOOT
        rig.run(L.lift_timeout_ms + 1500)
        self.assertEqual(rig.s.fault, stance.TRAVEL_TIMEOUT)
        self.assertIn("LOWER", rig.s.reason)
        self.assertEqual(rig.plant.seated(), [2, 2])

    def test_a_pin_will_not_leave_the_tilt_18_receiver(self):
        rig = Rig()
        rig.plant.pins[1].stuck = True
        rig.request = stance.REQUEST_TWO_FOOT
        rig.run(L.lock_release_timeout_ms + 100)
        self.assertEqual(rig.s.fault, stance.LOCK_TIMEOUT)
        self.assertEqual(rig.plant.actuator, 0)
        self.assertEqual(rig.plant.pinned_ms, 0)
        self.assertAlmostEqual(rig.plant.mm, RECEIVER_THREE)

    def test_a_pin_will_not_leave_the_tilt_0_receiver(self):
        rig = Rig(TWO_FOOT_POS, 2)
        rig.request = stance.REQUEST_THREE_FOOT
        self.assertTrue(rig.until_phase(stance.UNLOCKING, 20000))
        rig.plant.pins[0].stuck = True
        rig.run(L.lock_release_timeout_ms + 100)
        self.assertEqual(rig.s.fault, stance.LOCK_TIMEOUT)
        self.assertEqual(rig.plant.actuator, 0)
        self.assertLessEqual(rig.plant.mm, L.contact_mm + L.stop_tolerance_mm)


class TestLockSensor(unittest.TestCase):
    def test_one_switch_with_both_contacts_open(self):
        rig = Rig()
        rig.plant.pins[0].override = (False, False)
        rig.run(100)
        self.assertEqual(rig.s.state, stance.THREE_FOOT)     # inside the changeover allowance
        rig.run(80)
        self.assertEqual(rig.s.fault, stance.LOCK_SENSOR)
        self.assertFalse(rig.s.drive_allowed())

    def test_both_contacts_closed_mid_tilt(self):
        rig = Rig()
        rig.request = stance.REQUEST_TWO_FOOT
        self.assertTrue(rig.until_phase(stance.TILT, 2000))
        rig.run(2000)
        rig.plant.pins[1].override = (True, True)
        rig.run(stance.LOCK_ILLEGAL_MS + 20)
        self.assertEqual(rig.s.fault, stance.LOCK_SENSOR)
        self.assertEqual(rig.plant.actuator, 0)

    def test_parked_on_two_feet_but_one_switch_reads_released(self):
        rig = Rig(TWO_FOOT_POS, 2)
        rig.plant.pins[1].override = (False, True)
        rig.run(80)
        self.assertEqual(rig.s.fault, stance.LOCK_DISAGREES)
        self.assertFalse(rig.s.head_allowed())
        rig.run(2000)
        self.assertEqual(rig.s.state, stance.FAULT)           # latched
        rig.send("C")                                         # the raised foot still lacks a lock
        self.assertTrue(rig.errors[-1].startswith("err fault not cleared"))
        self.assertEqual(rig.s.state, stance.FAULT)
        rig.plant.pins[1].override = None
        rig.run(80)
        rig.send("C")
        self.assertEqual(rig.s.state, stance.TWO_FOOT)

    def test_parked_on_three_feet_but_one_switch_reads_released(self):
        rig = Rig()
        rig.plant.pins[0].override = (False, True)
        rig.run(80)
        self.assertEqual(rig.s.fault, stance.LOCK_DISAGREES)
        self.assertFalse(rig.s.drive_allowed())

    def test_one_switch_reads_seated_away_from_the_receivers(self):
        rig = Rig()
        rig.request = stance.REQUEST_TWO_FOOT
        self.assertTrue(rig.until_phase(stance.TILT, 2000))
        rig.run(3000)
        rig.plant.pins[0].override = (True, False)
        rig.run(80)
        self.assertEqual(rig.s.fault, stance.LOCK_DISAGREES)
        self.assertEqual(rig.plant.actuator, 0)

    def test_one_pin_never_seats_at_touchdown_so_the_foot_is_never_lifted(self):
        rig = Rig()
        rig.plant.pins[1].jammed = True
        rig.request = stance.REQUEST_TWO_FOOT
        self.assertTrue(rig.until_phase(stance.LOCKING, 40000))
        rig.run(L.lock_settle_ms + 3000 + L.lock_seat_timeout_ms)
        self.assertEqual(rig.s.fault, stance.LOCK_TIMEOUT)
        self.assertIn("not seated", rig.s.reason)
        self.assertEqual(rig.plant.actuator, 0)
        self.assertEqual(rig.plant.seated(), [2, 0])
        self.assertGreaterEqual(rig.plant.mm, L.contact_mm - L.overshoot_mm - L.stop_tolerance_mm - 0.1)

    def test_pins_never_seat_at_three_feet_so_no_drive(self):
        rig = Rig(TWO_FOOT_POS, 2)
        rig.request = stance.REQUEST_THREE_FOOT
        self.assertTrue(rig.until_phase(stance.TILT, 20000))
        rig.plant.pins[0].jammed = True
        rig.plant.pins[1].jammed = True
        self.assertTrue(rig.until_phase(stance.LOCKING, 40000))
        rig.run(L.lock_settle_ms + 3000 + L.lock_seat_timeout_ms)
        self.assertEqual(rig.s.fault, stance.LOCK_TIMEOUT)
        self.assertFalse(rig.s.drive_allowed())
        self.assertLessEqual(rig.plant.mm, L.three_foot_mm + L.overtravel_mm)

    def test_a_lock_reads_released_while_lifting(self):
        rig = Rig()
        rig.request = stance.REQUEST_TWO_FOOT
        self.assertTrue(rig.until_phase(stance.LIFT, 40000))
        rig.run(500)
        rig.plant.pins[1].override = (False, True)
        rig.run(80)
        self.assertEqual(rig.s.fault, stance.LOCK_DISAGREES)
        self.assertEqual(rig.plant.actuator, 0)
        self.assertFalse(rig.plant.releasing(0) or rig.plant.releasing(1))


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
        self.assertEqual(rig.s.state, stance.RETRACTING)     # still held: starts once idle

    def test_drive_refused_during_a_transition(self):
        rig = Rig()
        rig.request = stance.REQUEST_TWO_FOOT
        self.assertTrue(rig.until_phase(stance.TILT, 2000))
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
        rig = Rig(TWO_FOOT_POS, 2)
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
        held = Rig(45.0, 0)
        held.drive_line = "M 500 0 0 0"
        held.run(100)
        self.assertTrue(held.errors[-1].startswith("err drive refused (ground drive): stance not locked"))
        self.assertEqual(held.plant.channels, [0, 0, 0, 0])

    def test_a_fault_while_driving_stops_the_wheels_at_once(self):
        rig = Rig()
        rig.drive_line = "M 600 600 600 0"
        rig.run(300)
        self.assertEqual(rig.plant.channels[:3], [600, 600, 600])
        rig.plant.pins[0].override = (False, True)
        rig.run(80)
        self.assertEqual(rig.s.fault, stance.LOCK_DISAGREES)
        self.assertEqual(rig.plant.channels, [0, 0, 0, 0])


class TestFaultLatchAndClear(unittest.TestCase):
    def test_fault_stays_latched_until_cleared_and_needs_a_fresh_press(self):
        rig = Rig()
        rig.request = stance.REQUEST_TWO_FOOT
        self.assertTrue(rig.until_phase(stance.TILT, 2000))
        rig.run(1500)
        rig.plant.stalled = True
        rig.run(L.progress_ms + 30)
        self.assertEqual(rig.s.fault, stance.STALL)
        rig.plant.stalled = False
        rig.run(3000)                                         # cause gone, control still held
        self.assertEqual(rig.s.state, stance.FAULT)
        self.assertEqual(rig.plant.actuator, 0)
        self.assertFalse(rig.s.drive_allowed())
        self.assertTrue(rig.last_status().startswith("ss FAULT NONE STALL "))
        rig.send("C")                                         # clear while the control is still held
        self.assertEqual(rig.lines[-1], "ok\n")
        self.assertEqual(rig.s.state, stance.HELD)
        rig.run(1000)
        self.assertEqual(rig.plant.actuator, 0)               # the held control does not restart it
        rig.cool()
        rig.request = stance.REQUEST_TWO_FOOT
        self.assertTrue(rig.until_state(stance.TWO_FOOT, 60000))

    def test_clear_without_a_fault_is_refused(self):
        rig = Rig()
        rig.send("C")
        self.assertEqual(rig.errors[-1], "err no stance fault latched")

    def test_clear_keeps_the_press_consumed(self):
        rig = Rig()
        rig.request = stance.REQUEST_TWO_FOOT
        self.assertTrue(rig.until_phase(stance.TILT, 2000))
        rig.run(1500)
        rig.plant.pot_override_mv = 0.0
        rig.run(20)
        rig.plant.pot_override_mv = None
        rig.run(20)
        rig.send("C")
        rig.run(200000)                                       # control held the whole time
        self.assertEqual(rig.s.state, stance.HELD)
        self.assertEqual(rig.plant.actuator, 0)
        self.assertIn("release", rig.s.blocked(stance.REQUEST_TWO_FOOT, rig.t, True))


if __name__ == "__main__":
    unittest.main(verbosity=2)
