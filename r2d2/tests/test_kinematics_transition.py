"""Acceptance tests for the revision D centre-leg transition check.

Each failure class is proven by changing one real design input and confirming the check rejects it.
The unchanged design read from cad/kinematics.scad and cad/stance-lock-sensed.scad must pass.
"""
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'scripts'))
import check_kinematics as ck  # noqa: E402

FAST = {'sample_step_mm': 1.0}


def failed_classes(result):
    return {f['class'] for f in result['failures']}


def failed_checks(result):
    return {f['check'] for f in result['failures']}


class TransitionCheck(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.design = ck.load_design()
        cls.model = ck.build_mass_model(cls.design)

    def run_check(self, changes=None, model=None, criteria=None):
        design = {**self.design, **(changes or {})}
        mass_model = model if model is not None else ck.build_mass_model(design)
        return ck.evaluate(design, mass_model, {**FAST, **(criteria or {})})

    def test_chosen_design_passes_complete_transition(self):
        result = ck.evaluate(self.design, self.model)
        self.assertTrue(result['passed'], result['failures'][:5])
        directions = {row['direction'] for row in result['rows']}
        self.assertEqual(directions, {'deploy', 'retract'})
        strokes = [row['stroke_mm'] for row in result['rows'] if row['direction'] == 'deploy']
        self.assertAlmostEqual(strokes[0], self.design['POST_MIN'])
        self.assertAlmostEqual(strokes[-1], self.design['POST_MAX'])
        self.assertLessEqual(max(b - a for a, b in zip(strokes, strokes[1:])), ck.CRITERIA['sample_step_mm'] + 1e-9)

    def test_insufficient_lifted_foot_clearance_fails(self):
        # Stop retraction only 8 mm before floor contact: the foot hangs too close to the floor.
        contact = ck.contact_stroke(self.design)
        result = self.run_check({'POST_MIN': round(contact - 8, 3)})
        self.assertIn('clearance', failed_classes(result))
        self.assertIn('two-foot stance lifted-foot floor clearance (resting on heel stop)', failed_checks(result))

    def test_two_foot_support_margin_fails_with_forward_cg(self):
        extra = [('test ballast far forward', 1500.0, 'body', (0, 120, 300))]
        result = self.run_check(model=ck.build_mass_model(self.design, extra=extra))
        self.assertIn('support', failed_classes(result))
        self.assertIn('two-foot static support margin', failed_checks(result))

    def test_three_foot_support_margin_fails_with_rearward_cg(self):
        extra = [('test ballast far behind', 6000.0, 'legs', (0, -150, 300))]
        result = self.run_check(model=ck.build_mass_model(self.design, extra=extra))
        self.assertIn('three-foot static support margin', failed_checks(result))

    def test_actuator_overload_fails(self):
        # A robot twelve times heavier exceeds the P16 moving rating with the stated factors.
        result = self.run_check(model=ck.build_mass_model(self.design, mass_scale=12.0))
        self.assertIn('force', failed_classes(result))
        self.assertIn('factored actuator transition force within P16 moving rating', failed_checks(result))

    def test_lock_release_overload_fails(self):
        result = self.run_check({'SL_RELEASE_PIVOT_Z': self.design['SL_RELEASE_FINGER_Z'] - 60})
        self.assertIn('force', failed_classes(result))

    def test_misaligned_three_foot_receiver_fails(self):
        result = self.run_check({'SL_LOCK_RECEIVER_THREE_FOOT': self.design['SL_LOCK_RECEIVER_THREE_FOOT'] + 1.0})
        self.assertIn('restraint', failed_classes(result))
        self.assertIn('three-foot receiver aligned with pin', failed_checks(result))

    def test_misaligned_two_foot_receiver_fails(self):
        result = self.run_check({'SL_LOCK_RECEIVER_TWO_FOOT': 0.5})
        self.assertIn('two-foot receiver aligned with pin', failed_checks(result))

    def test_shallow_pin_engagement_fails(self):
        result = self.run_check({'SL_LOCK_RING_FACE_X': self.design['SL_LOCK_PIN_EXIT_X'] + 4})
        self.assertIn('restraint', failed_classes(result))
        self.assertIn('pin engagement in receiver', failed_checks(result))

    def test_sensor_that_can_read_engaged_too_early_fails(self):
        result = self.run_check({'SL_LOCK_SWITCH_OVERTRAVEL': 1.1, 'SL_LOCK_SWITCH_ADJUST': 0.4})
        self.assertIn('restraint', failed_classes(result))

    def test_unlocked_body_behind_hip_fails(self):
        extra = [('test ballast behind hip', 1500.0, 'body', (0, -60, 300))]
        result = self.run_check(model=ck.build_mass_model(self.design, extra=extra))
        self.assertIn('unlocked body held by post (CG ahead of hip)', failed_checks(result))

    def test_endpoint_beyond_actuator_stroke_fails(self):
        result = self.run_check({'POST_MAX': self.design['POST_STROKE']})
        self.assertIn('kinematics', failed_classes(result))

    def test_constants_must_be_literal(self):
        with self.assertRaises(ValueError):
            ck.parse_constants('HIP_Z=390;\n')


if __name__ == '__main__':
    unittest.main()
