"""Run the phone UI checks: JavaScript syntax and the simulated-DOM behaviour test.

Run: python -m unittest discover -s tests -p "test_ui*.py" -v
"""
import subprocess
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def node(*args):
    return subprocess.run(['node', *args], cwd=ROOT, capture_output=True, text=True, timeout=120)


class PhoneUiTests(unittest.TestCase):
    def test_app_javascript_syntax(self):
        result = node('--check', 'firmware/data/app.js')
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)

    def test_stance_controls_and_lease_behaviour(self):
        result = node('firmware/test/ui_test.js')
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertIn('PASS', result.stdout)
        print(result.stdout.strip())

    def test_page_exposes_stance_controls(self):
        page = (ROOT / 'firmware/data/index.html').read_text(encoding='utf-8')
        for marker in ['data-stance="2"', 'data-stance="3"', 'id="clear"', 'id="stanceState"', 'id="stanceBlocks"', 'id="fault"']:
            self.assertIn(marker, page)


if __name__ == '__main__':
    unittest.main()
