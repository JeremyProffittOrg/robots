"""Proves that every failure class of scripts/check_stance.py fails on a perturbed design and that the
chosen design passes.

Run from C:/dev/robots/fable-r2d2:
    python -m unittest discover -s tests -p "test_stance*.py" -v

Perturbed cases sample 12 strokes each way to stay quick; the nominal case uses the full CRITERIA
sampling (60 strokes each way plus contact and both endpoints) and the full interference scan.
"""
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

import check_stance  # noqa: E402

QUICK = 12


def classes(result):
    return {f["class"] for f in result["failures"]}


def checks(result, cls):
    return [f["check"] for f in result["failures"] if f["class"] == cls]


class StanceCheckFailureClasses(unittest.TestCase):
    def test_clearance_fails_when_the_stowed_foot_is_too_low(self):
        # Stowing only 8 mm above the floor leaves the lifted wheels below the 20 mm minimum.
        result = check_stance.evaluate(overrides={"st_stow_lift": 8}, poses_each_way=QUICK, interference=False)
        self.assertIn("clearance", classes(result))
        self.assertTrue(any("two-foot stance lifted centre-foot floor clearance" in c for c in checks(result, "clearance")))

    def test_support_fails_when_the_wheel_rows_are_too_close(self):
        # Axles 22 mm either side of each foot centre (design 45) leave the two-foot CG under 15 mm from the edge.
        result = check_stance.evaluate(overrides={"foot_axle_y": 22}, poses_each_way=QUICK, interference=False)
        self.assertIn("support", classes(result))
        self.assertTrue(any("two-foot stance" in c for c in checks(result, "support")))

    def test_force_fails_when_the_actuator_rating_is_too_small(self):
        # A 22:1 P16 lifts 50 N (datasheet); divided by the factor 3 it cannot move the body.
        result = check_stance.evaluate(criteria={"actuator_rating_N": 50.0, "actuator_backdrive_N": 75.0},
                                       poses_each_way=QUICK, interference=False)
        self.assertIn("force", classes(result))

    def test_lock_fails_when_the_three_leg_endpoint_misses_the_receiver(self):
        # Stopping at 63 mm leaves the body 0.6 deg short of 18: the pin is 0.5 mm off the bushing.
        result = check_stance.evaluate(overrides={"st_s_three": 63.0}, poses_each_way=QUICK, interference=False)
        self.assertIn("lock", classes(result))
        self.assertTrue(any("three-leg endpoint: receiver aligned" in c for c in checks(result, "lock")))

    def test_lock_fails_when_the_switch_cannot_sense_engagement(self):
        # With 2 mm of set overtravel the SS-01GL is outside its rating and can read "engaged" too early.
        result = check_stance.evaluate(overrides={"st_switch_ot": 2.0}, poses_each_way=QUICK, interference=False)
        self.assertIn("lock", classes(result))

    def test_interference_fails_when_the_carriage_hits_the_battery(self):
        # Moving the battery 45 mm rearward puts it inside the carriage sweep.
        result = check_stance.evaluate(overrides={"battery_y": 21}, poses_each_way=QUICK, interference=True)
        self.assertIn("interference", classes(result))

    def test_chosen_design_passes(self):
        result = check_stance.evaluate()
        self.assertEqual(result["failures"], [], result["failures"][:5])
        self.assertGreaterEqual(sum(1 for r in result["rows"] if r["direction"] == "deploy"), 50)
        self.assertGreaterEqual(sum(1 for r in result["rows"] if r["direction"] == "retract"), 50)
        self.assertTrue(result["passed"])


if __name__ == "__main__":
    unittest.main()
