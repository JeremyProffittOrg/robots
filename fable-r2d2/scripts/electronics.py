"""Run electronics/generate.py and check what it wrote against the firmware pin map.

Checks, in order:

1. ``electronics/generate.py`` runs and exits zero.
2. The five SVG sheets, ``wiring.csv`` and ``calculations.json`` exist, are not empty,
   and every SVG parses as XML.
3. Every KB2040 pin that ``wiring.csv`` uses agrees with ``firmware/kb2040/code.py``:
   the ``DRIVES`` table, the ``ACTUATOR`` entry, and the NeoPixel, index, both
   release-servo, all four lock-switch, actuator-position and battery pins.  No
   KB2040 pin carries two nets, and every firmware pin is wired.
4. The firmware pin plan is legal on the RP2040: no two PWM outputs share a slice
   output, the 50 Hz servo does not share a slice with a 20 kHz output, and both
   analogue inputs are on ADC pins.
   The firmware file is parsed with regular expressions, not imported, because it is
   CircuitPython and imports ``board``; ``protocol.py`` is pure and is imported.

Any mismatch prints what was expected, what was found, and exits non-zero.

Usage: ``python scripts/electronics.py``
"""

import csv
import re
import subprocess
import sys
import xml.etree.ElementTree as ET
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
ELECTRONICS = ROOT / "electronics"
GENERATOR = ELECTRONICS / "generate.py"
FIRMWARE = ROOT / "firmware/kb2040/code.py"

sys.path.insert(0, str(ROOT / "firmware/kb2040"))
import protocol  # noqa: E402  (hardware-free)

SHEETS = [
    "01-power-and-charging.svg",
    "02-motor-drive.svg",
    "03-head-electronics.svg",
    "04-pi-audio-and-links.svg",
    "05-stance-actuator-and-lock.svg",
]
KB2040 = "A2"  # the KB2040's reference designator in wiring.csv
NON_GPIO = {"3V3 pad", "GND pad", "USB-C", "STEMMA QT GND"}

DRIVE_ENTRY = re.compile(
    r'\(\s*"(?P<name>[a-z]+)"\s*,\s*[A-Z]+\s*,\s*board\.(?P<pwm>\w+)\s*,\s*(?P<pwm_gpio>\d+)\s*,\s*'
    r'board\.(?P<digital>\w+)\s*,\s*(?P<dig_gpio>\d+)\s*,\s*(?:True|False)\s*\)')
ACTUATOR_ENTRY = re.compile(
    r'^ACTUATOR\s*=\s*\(\s*"actuator"\s*,\s*board\.(?P<pwm>\w+)\s*,\s*(?P<pwm_gpio>\d+)\s*,\s*'
    r'board\.(?P<digital>\w+)\s*,\s*(?P<dig_gpio>\d+)', re.M)

# net in wiring.csv -> the code.py name that assigns its KB2040 pin
SINGLE_NETS = {
    "NEOPIXEL": "PIXEL_PIN",
    "SIG-DOME-INDEX": "INDEX_PIN",
    "SIG-RELEASE-SERVO-L": "RELEASE_SERVO_LEFT_PIN",
    "SIG-RELEASE-SERVO-R": "RELEASE_SERVO_RIGHT_PIN",
    "SIG-LOCK-L-NO": "LOCK_LEFT_NO_PIN",
    "SIG-LOCK-L-NC": "LOCK_LEFT_NC_PIN",
    "SIG-LOCK-R-NO": "LOCK_RIGHT_NO_PIN",
    "SIG-LOCK-R-NC": "LOCK_RIGHT_NC_PIN",
    "SIG-ACT-POS": "POSITION_PIN",
    "SIG-VBAT-KB": "BATTERY_PIN",
}


def fail(message):
    """Print the problem and stop with a non-zero status."""
    print("FAIL: " + message)
    sys.exit(1)


def read_firmware_pins():
    """Return ({net: pin}, gpio facts) from firmware/kb2040/code.py."""
    if not FIRMWARE.is_file():
        fail("{0} is missing, so the pin map cannot be checked".format(FIRMWARE))
    source = FIRMWARE.read_text(encoding="utf-8")

    table = re.search(r"^DRIVES\s*=\s*\((?P<body>.*?)^\)", source, re.S | re.M)
    if table is None:
        fail("no DRIVES = ( ... ) table found in {0}".format(FIRMWARE))
    expected = {}
    fast_gpios = []
    for match in DRIVE_ENTRY.finditer(table.group("body")):
        expected["SIG-{0}-PWM".format(match.group("name"))] = match.group("pwm")
        expected["SIG-{0}-DIR".format(match.group("name"))] = match.group("digital")
        fast_gpios.append(int(match.group("pwm_gpio")))
    if len(fast_gpios) != 4:
        fail("the DRIVES table in {0} parsed to {1} outputs, expected 4".format(
            FIRMWARE, len(fast_gpios)))

    actuator = ACTUATOR_ENTRY.search(source)
    if actuator is None:
        fail("no ACTUATOR = (\"actuator\", ...) entry found in {0}".format(FIRMWARE))
    expected["SIG-ACT-PWM"] = actuator.group("pwm")
    expected["SIG-ACT-DIR"] = actuator.group("digital")
    fast_gpios.append(int(actuator.group("pwm_gpio")))

    for net, name in SINGLE_NETS.items():
        match = re.search(r"^{0}\s*=\s*board\.(\w+)".format(name), source, re.M)
        if match is None:
            fail("{0} is not assigned a board pin in {1}".format(name, FIRMWARE))
        expected[net] = match.group(1)

    gpios = {}
    for name in ("RELEASE_SERVO_LEFT", "RELEASE_SERVO_RIGHT", "POSITION", "BATTERY"):
        match = re.search(r"^{0}_GPIO\s*=\s*(\d+)".format(name), source, re.M)
        if match is None:
            fail("{0}_GPIO is not assigned in {1}".format(name, FIRMWARE))
        gpios[name] = int(match.group(1))
    return expected, fast_gpios, gpios


def check_pin_plan(fast_gpios, gpios):
    """RP2040 PWM slice, frequency and ADC rules."""
    problems = []
    servos = [gpios["RELEASE_SERVO_LEFT"], gpios["RELEASE_SERVO_RIGHT"]]
    for first, second in protocol.pwm_conflicts(fast_gpios + servos):
        problems.append("PWM GP{0} and GP{1} share one slice output".format(first, second))
    outputs = [(gpio, protocol.PWM_FREQUENCY) for gpio in fast_gpios]
    outputs += [(gpio, protocol.SERVO_FREQUENCY) for gpio in servos]
    for first, second in protocol.pwm_frequency_conflicts(outputs):
        problems.append("PWM GP{0} and GP{1} share a slice at different frequencies".format(
            first, second))
    for name in ("POSITION", "BATTERY"):
        if gpios[name] not in protocol.ADC_GPIOS:
            problems.append("{0} input GP{1} is not an ADC pin".format(name.lower(), gpios[name]))
    return problems


def check_wiring(expected):
    """Compare every KB2040 pin in wiring.csv with the firmware pin map."""
    path = ELECTRONICS / "wiring.csv"
    with path.open(newline="", encoding="utf-8") as handle:
        rows = list(csv.DictReader(handle))
    if not rows:
        fail("{0} has no data rows".format(path))

    expected_columns = ["wire_id", "net", "source", "source_pin", "target", "target_pin",
                        "gauge_awg", "colour", "length_mm_estimate", "route"]
    if list(rows[0]) != expected_columns:
        fail("wiring.csv columns are {0}, expected {1}".format(list(rows[0]), expected_columns))

    problems = []
    nets_on_pin = {}
    wired_nets = set()
    for row in rows:
        for side, pin_key in (("source", "source_pin"), ("target", "target_pin")):
            if row[side] != KB2040 or row[pin_key] in NON_GPIO:
                continue
            pin = row[pin_key]
            net = row["net"]
            nets_on_pin.setdefault(pin, set()).add(net)
            if net not in expected:
                problems.append("{0}: KB2040 pin {1} carries net {2}, which code.py does not "
                                "assign".format(row["wire_id"], pin, net))
            elif expected[net] != pin:
                problems.append("{0}: net {1} on KB2040 pin {2}, code.py says {3}".format(
                    row["wire_id"], net, pin, expected[net]))
            else:
                wired_nets.add(net)
    for pin, nets in sorted(nets_on_pin.items()):
        if len(nets) > 1:
            problems.append("KB2040 pin {0} carries several nets: {1}".format(pin, sorted(nets)))
    for net in sorted(set(expected) - wired_nets):
        problems.append("code.py assigns {0} to {1}, but wiring.csv never wires it".format(
            expected[net], net))
    return rows, problems


def main():
    result = subprocess.run([sys.executable, str(GENERATOR)], capture_output=True, text=True)
    if result.stdout:
        print(result.stdout.rstrip())
    if result.returncode != 0:
        print(result.stderr.rstrip())
        fail("electronics/generate.py exited {0}".format(result.returncode))

    for name in SHEETS:
        path = ELECTRONICS / name
        if not path.is_file() or path.stat().st_size == 0:
            fail("{0} was not written".format(path))
        try:
            ET.parse(path)
        except ET.ParseError as error:
            fail("{0} is not valid XML: {1}".format(path, error))
    for name in ("wiring.csv", "calculations.json"):
        path = ELECTRONICS / name
        if not path.is_file() or path.stat().st_size == 0:
            fail("{0} was not written".format(path))

    expected, fast_gpios, gpios = read_firmware_pins()
    rows, problems = check_wiring(expected)
    problems += check_pin_plan(fast_gpios, gpios)
    if problems:
        for problem in problems:
            print("FAIL: " + problem)
        sys.exit(1)

    print("PASS: {0} SVG sheets parse, wiring.csv has {1} wires, all {2} KB2040 signal pins "
          "match firmware/kb2040/code.py, and the RP2040 PWM/ADC plan is legal".format(
              len(SHEETS), len(rows), len(expected)))


if __name__ == "__main__":
    main()
