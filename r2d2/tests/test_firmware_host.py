"""Compile and run every firmware host test (firmware/test/*.cpp) with warnings as errors.

Run: python -m unittest discover -s tests -p "test_firmware*.py" -v
The stance, interlock and posture logic in firmware/include is the same code the ESP32-S3 build uses.
"""
import os
import shutil
import subprocess
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MSYS_GXX = Path(r'C:\msys64\mingw64\bin\g++.exe')


def compiler():
    configured = os.environ.get('R2_GXX')
    if configured:
        return configured
    if MSYS_GXX.exists():
        return str(MSYS_GXX)
    found = shutil.which('g++')
    if not found:
        raise RuntimeError('No g++ found: install MSYS2 mingw64 g++ or set R2_GXX')
    return found


def build_and_run(source):
    gxx = compiler()
    env = os.environ.copy()
    env['PATH'] = str(Path(gxx).parent) + os.pathsep + env['PATH']
    with tempfile.TemporaryDirectory(prefix='r2-host-') as folder:
        exe = Path(folder) / (source.stem + '.exe')
        build = subprocess.run([gxx, '-std=c++11', '-Wall', '-Wextra', '-Werror', '-I', str(ROOT / 'firmware/include'),
                                str(source), '-o', str(exe)], capture_output=True, text=True, timeout=240, env=env)
        if build.returncode:
            raise AssertionError(f'{source.name} failed to compile:\n{build.stdout}\n{build.stderr}')
        result = subprocess.run([str(exe)], capture_output=True, text=True, timeout=240, env=env)
        return result


class FirmwareHostTests(unittest.TestCase):
    def check(self, name):
        result = build_and_run(ROOT / 'firmware/test' / name)
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertIn('PASS', result.stdout)
        print(result.stdout.strip())

    def test_control_lease_mixing_and_ramps(self):
        self.check('control_test.cpp')

    def test_stance_state_machine_and_interlocks(self):
        self.check('stance_test.cpp')

    def test_every_host_test_is_covered(self):
        self.assertEqual(sorted(p.name for p in (ROOT / 'firmware/test').glob('*.cpp')),
                         ['control_test.cpp', 'stance_test.cpp'])


if __name__ == '__main__':
    unittest.main()
