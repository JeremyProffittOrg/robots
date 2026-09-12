"""Unit tests for the fable-r2d2 drive mixing maths.

Run from anywhere:

    python firmware/pi/test_mixing.py
"""

import os
import sys
import unittest

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import mixing  # noqa: E402


class TestClamp(unittest.TestCase):
    def test_inside_range(self):
        self.assertEqual(mixing.clamp(0.5, -1.0, 1.0), 0.5)

    def test_outside_range(self):
        self.assertEqual(mixing.clamp(-3.0, -1.0, 1.0), -1.0)
        self.assertEqual(mixing.clamp(3.0, -1.0, 1.0), 1.0)


class TestMix(unittest.TestCase):
    def test_straight_forward_drives_all_three_feet_equally(self):
        left, right, centre = mixing.mix(0.0, 1.0)
        self.assertAlmostEqual(left, 1.0)
        self.assertAlmostEqual(right, 1.0)
        self.assertAlmostEqual(centre, 1.0)

    def test_straight_back(self):
        left, right, centre = mixing.mix(0.0, -1.0)
        self.assertAlmostEqual(left, -1.0)
        self.assertAlmostEqual(right, -1.0)
        self.assertAlmostEqual(centre, -1.0)

    def test_spin_on_the_spot_opposes_the_outer_feet_and_idles_the_caster(self):
        left, right, centre = mixing.mix(1.0, 0.0)
        self.assertAlmostEqual(left, mixing.TURN_GAIN)
        self.assertAlmostEqual(right, -mixing.TURN_GAIN)
        self.assertAlmostEqual(centre, 0.0)

    def test_left_turn_mirrors_a_right_turn(self):
        right_turn = mixing.mix(0.6, 0.3)
        left_turn = mixing.mix(-0.6, 0.3)
        self.assertAlmostEqual(right_turn[0], left_turn[1])
        self.assertAlmostEqual(right_turn[1], left_turn[0])
        self.assertAlmostEqual(right_turn[2], left_turn[2])

    def test_forward_arc(self):
        left, right, centre = mixing.mix(0.5, 0.5, turn_gain=0.7)
        self.assertAlmostEqual(left, 0.85)
        self.assertAlmostEqual(right, 0.15)
        self.assertAlmostEqual(centre, 0.5)

    def test_channels_are_clamped_to_one(self):
        left, right, centre = mixing.mix(1.0, 1.0, turn_gain=0.7)
        self.assertAlmostEqual(left, 1.0)
        self.assertAlmostEqual(right, 0.3)
        self.assertAlmostEqual(centre, 1.0)

    def test_out_of_range_input_is_clamped_before_mixing(self):
        self.assertEqual(mixing.mix(5.0, 5.0), mixing.mix(1.0, 1.0))
        self.assertEqual(mixing.mix(-5.0, -5.0), mixing.mix(-1.0, -1.0))

    def test_custom_turn_gain(self):
        left, right, _centre = mixing.mix(1.0, 0.0, turn_gain=0.25)
        self.assertAlmostEqual(left, 0.25)
        self.assertAlmostEqual(right, -0.25)


class TestApplyLimits(unittest.TestCase):
    def test_deadband_stops_the_channel(self):
        self.assertEqual(mixing.apply_limits(0.0), 0.0)
        self.assertEqual(mixing.apply_limits(mixing.DEADBAND), 0.0)
        self.assertEqual(mixing.apply_limits(-mixing.DEADBAND), 0.0)

    def test_speed_cap_limits_full_stick(self):
        self.assertAlmostEqual(mixing.apply_limits(1.0, speed_cap=0.6), 0.6)
        self.assertAlmostEqual(mixing.apply_limits(-1.0, speed_cap=0.6), -0.6)

    def test_minimum_duty_is_enforced_when_moving(self):
        # 0.1 * 0.6 = 0.06, below the 0.15 floor.
        self.assertAlmostEqual(mixing.apply_limits(0.1, speed_cap=0.6), mixing.MIN_DUTY)
        self.assertAlmostEqual(
            mixing.apply_limits(-0.1, speed_cap=0.6), -mixing.MIN_DUTY
        )

    def test_minimum_duty_does_not_apply_to_a_stopped_channel(self):
        self.assertEqual(mixing.apply_limits(0.01, speed_cap=0.6), 0.0)

    def test_speed_cap_is_itself_clamped(self):
        self.assertAlmostEqual(mixing.apply_limits(1.0, speed_cap=9.0), 1.0)
        self.assertAlmostEqual(
            mixing.apply_limits(1.0, speed_cap=0.0), mixing.SPEED_CAP_MIN
        )

    def test_output_never_leaves_the_range(self):
        step = 0.013
        value = -1.0
        while value <= 1.0:
            for cap in (0.2, 0.6, 1.0):
                result = mixing.apply_limits(value, speed_cap=cap)
                self.assertGreaterEqual(result, -1.0)
                self.assertLessEqual(result, 1.0)
            value += step


class TestToPermille(unittest.TestCase):
    def test_edges(self):
        self.assertEqual(mixing.to_permille(1.0), 1000)
        self.assertEqual(mixing.to_permille(-1.0), -1000)
        self.assertEqual(mixing.to_permille(0.0), 0)

    def test_rounds_to_nearest(self):
        self.assertEqual(mixing.to_permille(0.1234), 123)
        self.assertEqual(mixing.to_permille(0.1236), 124)

    def test_clamps_out_of_range(self):
        self.assertEqual(mixing.to_permille(4.0), 1000)
        self.assertEqual(mixing.to_permille(-4.0), -1000)


class TestDrivePermille(unittest.TestCase):
    def test_full_forward_at_the_default_cap(self):
        self.assertEqual(mixing.drive_permille(0.0, 1.0), (600, 600, 600))

    def test_full_reverse_at_the_default_cap(self):
        self.assertEqual(mixing.drive_permille(0.0, -1.0), (-600, -600, -600))

    def test_stopped_stick_sends_zeros(self):
        self.assertEqual(mixing.drive_permille(0.0, 0.0), (0, 0, 0))

    def test_spin_right_opposes_the_feet_and_stops_the_caster(self):
        left, right, centre = mixing.drive_permille(1.0, 0.0)
        self.assertEqual(left, 420)
        self.assertEqual(right, -420)
        self.assertEqual(centre, 0)

    def test_uncapped_full_forward(self):
        self.assertEqual(mixing.drive_permille(0.0, 1.0, speed_cap=1.0), (1000,) * 3)

    def test_no_channel_ever_exceeds_full_permille(self):
        step = 0.09
        x = -1.0
        while x <= 1.0:
            y = -1.0
            while y <= 1.0:
                for cap in (0.2, 0.6, 1.0):
                    for channel in mixing.drive_permille(x, y, speed_cap=cap):
                        self.assertGreaterEqual(channel, -mixing.MAX_PERMILLE)
                        self.assertLessEqual(channel, mixing.MAX_PERMILLE)
                y += step
            x += step

    def test_a_moving_channel_is_never_below_the_minimum_duty(self):
        floor = int(round(mixing.MIN_DUTY * mixing.MAX_PERMILLE))
        step = 0.07
        x = -1.0
        while x <= 1.0:
            y = -1.0
            while y <= 1.0:
                for channel in mixing.drive_permille(x, y):
                    if channel != 0:
                        self.assertGreaterEqual(abs(channel), floor)
                y += step
            x += step


class TestHeadPermille(unittest.TestCase):
    def test_stop(self):
        self.assertEqual(mixing.head_permille(0), 0)

    def test_directions(self):
        self.assertEqual(mixing.head_permille(1, duty=0.45), 450)
        self.assertEqual(mixing.head_permille(-1, duty=0.45), -450)

    def test_minimum_duty_is_enforced(self):
        self.assertEqual(mixing.head_permille(1, duty=0.01), 150)

    def test_duty_is_clamped(self):
        self.assertEqual(mixing.head_permille(1, duty=5.0), 1000)


class TestRamp(unittest.TestCase):
    def test_small_difference_reaches_target(self):
        self.assertEqual(mixing.ramp_step(0, 50, 200), 50)

    def test_large_difference_is_limited(self):
        self.assertEqual(mixing.ramp_step(0, 1000, 200), 200)
        self.assertEqual(mixing.ramp_step(0, -1000, 200), -200)

    def test_already_at_target(self):
        self.assertEqual(mixing.ramp_step(600, 600, 200), 600)

    def test_never_overshoots(self):
        value = 0
        for _ in range(20):
            value = mixing.ramp_step(value, 650, 200)
        self.assertEqual(value, 650)

    def test_full_reversal_takes_ten_commands(self):
        value = -1000
        ticks = 0
        while value != 1000:
            value = mixing.ramp_step(value, 1000, mixing.RAMP_PER_COMMAND)
            ticks += 1
            self.assertLess(ticks, 50)
        self.assertEqual(ticks, 10)

    def test_pi_and_controller_ramp_rates_agree(self):
        # 40 permille per 10 ms on the KB2040 is 200 permille per 50 ms here.
        self.assertEqual(mixing.RAMP_PER_COMMAND, 40 * int(round(1000 / mixing.COMMAND_HZ / 10)))

    def test_zero_step_is_rejected(self):
        with self.assertRaises(ValueError):
            mixing.ramp_step(0, 100, 0)

    def test_ramp_channels(self):
        self.assertEqual(
            mixing.ramp_channels([0, 0, 0, 0], [1000, -1000, 50, 0], 200),
            [200, -200, 50, 0],
        )

    def test_ramp_channels_rejects_mismatched_lengths(self):
        with self.assertRaises(ValueError):
            mixing.ramp_channels([0, 0], [0, 0, 0])


class TestFormatDrive(unittest.TestCase):
    def test_line_shape(self):
        self.assertEqual(mixing.format_drive(600, -600, 0, 450), "M 600 -600 0 450\n")

    def test_values_are_clamped(self):
        self.assertEqual(
            mixing.format_drive(5000, -5000, 0, 0), "M 1000 -1000 0 0\n"
        )


class TestParseStatus(unittest.TestCase):
    def test_good_line(self):
        self.assertEqual(
            mixing.parse_status("st 1 100 -100 0 250 0\n"),
            {
                "enabled": True,
                "left": 100,
                "right": -100,
                "centre": 0,
                "head": 250,
                "index": False,
            },
        )

    def test_index_flag(self):
        self.assertTrue(mixing.parse_status("st 0 0 0 0 0 1")["index"])

    def test_rejects_other_lines(self):
        self.assertIsNone(mixing.parse_status("ok"))
        self.assertIsNone(mixing.parse_status("err something"))
        self.assertIsNone(mixing.parse_status("st 1 2 3"))
        self.assertIsNone(mixing.parse_status("st a b c d e f"))
        self.assertIsNone(mixing.parse_status(""))


if __name__ == "__main__":
    unittest.main(verbosity=2)
