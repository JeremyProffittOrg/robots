"""Unit tests for the hardware-free KB2040 protocol module.

Run from anywhere:

    python firmware/kb2040/test_protocol.py
"""

import os
import sys
import unittest

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import protocol  # noqa: E402


class TestClamp(unittest.TestCase):
    def test_inside_range_is_unchanged(self):
        self.assertEqual(protocol.clamp(5, -10, 10), 5)

    def test_below_and_above(self):
        self.assertEqual(protocol.clamp(-99, -10, 10), -10)
        self.assertEqual(protocol.clamp(99, -10, 10), 10)

    def test_bounds_are_inclusive(self):
        self.assertEqual(protocol.clamp(-10, -10, 10), -10)
        self.assertEqual(protocol.clamp(10, -10, 10), 10)


class TestSplitLines(unittest.TestCase):
    def test_complete_lines_and_remainder(self):
        lines, rest = protocol.split_lines("M 1 2 3 4\nS\n?")
        self.assertEqual(lines, ["M 1 2 3 4", "S"])
        self.assertEqual(rest, "?")

    def test_crlf_does_not_produce_blank_lines(self):
        lines, rest = protocol.split_lines("S\r\nS\r\n")
        self.assertEqual(lines, ["S", "S"])
        self.assertEqual(rest, "")

    def test_no_terminator_yields_no_lines(self):
        lines, rest = protocol.split_lines("M 1 2 3")
        self.assertEqual(lines, [])
        self.assertEqual(rest, "M 1 2 3")


class TestParseCommand(unittest.TestCase):
    def test_drive(self):
        self.assertEqual(
            protocol.parse_command("M 100 -200 0 550"),
            ("M", [100, -200, 0, 550]),
        )

    def test_drive_clamps_out_of_range(self):
        self.assertEqual(
            protocol.parse_command("M 5000 -5000 1000 -1000"),
            ("M", [1000, -1000, 1000, -1000]),
        )

    def test_drive_wrong_arity(self):
        with self.assertRaises(protocol.CommandError):
            protocol.parse_command("M 1 2 3")

    def test_drive_rejects_non_numeric(self):
        with self.assertRaises(protocol.CommandError):
            protocol.parse_command("M 1 2 3 fast")

    def test_lights_all(self):
        self.assertEqual(protocol.parse_command("L 0 255 128"), ("L", [0, 255, 128]))

    def test_lights_clamps_colour(self):
        self.assertEqual(protocol.parse_command("L -5 999 7"), ("L", [0, 255, 7]))

    def test_single_pixel(self):
        self.assertEqual(protocol.parse_command("P 16 1 2 3"), ("P", [16, 1, 2, 3]))

    def test_single_pixel_index_out_of_range(self):
        with self.assertRaises(protocol.CommandError):
            protocol.parse_command("P 17 1 2 3")
        with self.assertRaises(protocol.CommandError):
            protocol.parse_command("P -1 1 2 3")

    def test_enable(self):
        self.assertEqual(protocol.parse_command("E 1"), ("E", [1]))
        self.assertEqual(protocol.parse_command("E 0"), ("E", [0]))

    def test_enable_rejects_other_values(self):
        with self.assertRaises(protocol.CommandError):
            protocol.parse_command("E 2")

    def test_stop_and_status(self):
        self.assertEqual(protocol.parse_command("S"), ("S", []))
        self.assertEqual(protocol.parse_command("?"), ("?", []))

    def test_stop_rejects_arguments(self):
        with self.assertRaises(protocol.CommandError):
            protocol.parse_command("S 1")

    def test_surrounding_whitespace_is_ignored(self):
        self.assertEqual(protocol.parse_command("  M 1 2 3 4  "), ("M", [1, 2, 3, 4]))

    def test_unknown_verb(self):
        with self.assertRaises(protocol.CommandError):
            protocol.parse_command("X 1")

    def test_empty_line(self):
        with self.assertRaises(protocol.CommandError):
            protocol.parse_command("   ")


class TestRampStep(unittest.TestCase):
    def test_small_difference_reaches_target(self):
        self.assertEqual(protocol.ramp_step(0, 10, 40), 10)

    def test_large_positive_difference_is_limited(self):
        self.assertEqual(protocol.ramp_step(0, 1000, 40), 40)

    def test_large_negative_difference_is_limited(self):
        self.assertEqual(protocol.ramp_step(0, -1000, 40), -40)

    def test_already_at_target(self):
        self.assertEqual(protocol.ramp_step(500, 500, 40), 500)

    def test_full_reversal_takes_fifty_ticks(self):
        value = -1000
        ticks = 0
        while value != 1000:
            value = protocol.ramp_step(value, 1000, protocol.RAMP_STEP)
            ticks += 1
            self.assertLess(ticks, 100)
        self.assertEqual(ticks, 50)

    def test_ramp_never_overshoots(self):
        value = 0
        for _ in range(10):
            previous = value
            value = protocol.ramp_step(value, 55, 40)
            self.assertLessEqual(abs(value - previous), 40)
        self.assertEqual(value, 55)

    def test_zero_step_is_rejected(self):
        with self.assertRaises(ValueError):
            protocol.ramp_step(0, 100, 0)


class TestOutputs(unittest.TestCase):
    def test_coast(self):
        self.assertEqual(protocol.outputs_for_permille(0), (False, 0))
        self.assertEqual(protocol.outputs_for_coast(), (False, 0))

    def test_brake_is_both_high(self):
        self.assertEqual(protocol.outputs_for_brake(), (True, protocol.FULL_DUTY))

    def test_full_forward(self):
        self.assertEqual(protocol.outputs_for_permille(1000), (True, 0))

    def test_full_reverse(self):
        self.assertEqual(
            protocol.outputs_for_permille(-1000), (False, protocol.FULL_DUTY)
        )

    def test_half_forward_is_slow_decay(self):
        high, duty = protocol.outputs_for_permille(500)
        self.assertTrue(high)
        self.assertEqual(duty, protocol.FULL_DUTY - (protocol.FULL_DUTY * 500) // 1000)

    def test_half_reverse_is_fast_decay(self):
        high, duty = protocol.outputs_for_permille(-500)
        self.assertFalse(high)
        self.assertEqual(duty, (protocol.FULL_DUTY * 500) // 1000)

    def test_duty_stays_inside_the_sixteen_bit_range(self):
        for permille in range(-1000, 1001, 7):
            _high, duty = protocol.outputs_for_permille(permille)
            self.assertGreaterEqual(duty, 0)
            self.assertLessEqual(duty, protocol.FULL_DUTY)

    def test_invert_swaps_direction(self):
        self.assertEqual(
            protocol.outputs_for_permille(600, invert=True),
            protocol.outputs_for_permille(-600),
        )

    def test_out_of_range_input_is_clamped(self):
        self.assertEqual(protocol.outputs_for_permille(9000), (True, 0))


class TestPwmPlan(unittest.TestCase):
    def test_slice_and_channel_maths(self):
        self.assertEqual(protocol.pwm_slice(0), 0)
        self.assertEqual(protocol.pwm_channel(0), "A")
        self.assertEqual(protocol.pwm_slice(3), 1)
        self.assertEqual(protocol.pwm_channel(3), "B")
        self.assertEqual(protocol.pwm_slice(19), protocol.pwm_slice(3))
        self.assertEqual(protocol.pwm_channel(19), protocol.pwm_channel(3))

    def test_the_seven_firmware_pwm_pins_do_not_clash(self):
        # GP3 GP5 GP7 GP9 GP10 GP18 GP27, the PWM column of MOTORS in code.py.
        self.assertEqual(protocol.pwm_conflicts([3, 5, 7, 9, 10, 18, 27]), [])

    def test_the_fourteen_input_pins_would_clash(self):
        every_input = [2, 3, 4, 5, 6, 7, 8, 9, 10, 19, 20, 18, 26, 27]
        self.assertEqual(
            protocol.pwm_conflicts(every_input),
            [(2, 18), (3, 19), (4, 20), (10, 26)],
        )


class TestFormatting(unittest.TestCase):
    def test_ok_and_error(self):
        self.assertEqual(protocol.format_ok(), "ok\n")
        self.assertEqual(protocol.format_error("nope"), "err nope\n")

    def test_status(self):
        self.assertEqual(
            protocol.format_status(True, 100, -100, 0, 250, False),
            "st 1 100 -100 0 250 0\n",
        )
        self.assertEqual(
            protocol.format_status(False, 0, 0, 0, 0, True),
            "st 0 0 0 0 0 1\n",
        )


class TestDriveState(unittest.TestCase):
    def test_targets_are_clamped(self):
        state = protocol.DriveState()
        state.set_targets([2000, -2000, 0, 0])
        self.assertEqual(state.target, [1000, -1000, 0, 0])

    def test_tick_ramps_every_channel(self):
        state = protocol.DriveState(40)
        state.set_targets([1000, 1000, 1000, 1000])
        self.assertEqual(state.tick(), [40, 40, 40, 40])
        self.assertEqual(state.tick(), [80, 80, 80, 80])

    def test_stop_ramps_down_but_hard_stop_is_immediate(self):
        state = protocol.DriveState(40)
        state.set_targets([1000, 1000, 1000, 1000])
        for _ in range(10):
            state.tick()
        self.assertEqual(state.current, [400, 400, 400, 400])
        state.stop()
        self.assertEqual(state.tick(), [360, 360, 360, 360])
        state.hard_stop()
        self.assertEqual(state.current, [0, 0, 0, 0])
        self.assertFalse(state.is_moving())

    def test_is_moving(self):
        state = protocol.DriveState(40)
        self.assertFalse(state.is_moving())
        state.set_targets([0, 0, 100, 0])
        state.tick()
        self.assertTrue(state.is_moving())

    def test_wrong_arity_is_rejected(self):
        state = protocol.DriveState()
        with self.assertRaises(ValueError):
            state.set_targets([1, 2, 3])


if __name__ == "__main__":
    unittest.main(verbosity=2)
