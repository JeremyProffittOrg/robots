"""Run electronics/generate.py and check what it wrote against the firmware pin map.

Checks, in order:

1. ``electronics/generate.py`` runs and exits zero.
2. The four SVG sheets, ``wiring.csv`` and ``calculations.json`` exist, are not empty,
   and every SVG parses as XML.
3. Every KB2040 pin that ``wiring.csv`` uses agrees with the ``MOTORS`` table, the
   enable pin, the NeoPixel pin and the index pin in ``firmware/kb2040/code.py``.
   The firmware file is parsed with regular expressions, not imported, because it is
   CircuitPython and imports ``board``.

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

SHEETS = [
    "01-power-and-charging.svg",
    "02-motor-drive.svg",
    "03-head-electronics.svg",
    "04-pi-audio-and-links.svg",
]
KB2040 = "A2"  # the KB2040's reference designator in wiring.csv

MOTOR_ENTRY = re.compile(
    r'\(\s*"(?P<name>[a-z0-9\-]+)"\s*,\s*(?P<channel>[A-Z]+)\s*,\s*'
    r'board\.(?P<pwm>\w+)\s*,\s*(?P<pwm_gpio>\d+)\s*,\s*'
    r'board\.(?P<digital>\w+)\s*,\s*(?P<dig_gpio>\d+)\s*,\s*(?P<invert>True|False)\s*\)')
SINGLE_PIN = r'^{0}\s*=\s*board\.(\w+)'


def fail(message):
    """Print the problem and stop with a non-zero status."""
    print("FAIL: " + message)
    sys.exit(1)


def read_firmware_pins():
    """Return (motor map, enable pin, pixel pin, index pin) from firmware/kb2040/code.py."""
    if not FIRMWARE.is_file():
        fail("{0} is missing, so the pin map cannot be checked".format(FIRMWARE))
    source = FIRMWARE.read_text(encoding="utf-8")

    table = re.search(r"^MOTORS\s*=\s*\((?P<body>.*?)^\)", source, re.S | re.M)
    if table is None:
        fail("no MOTORS = ( ... ) table found in {0}".format(FIRMWARE))
    motors = {}
    for match in MOTOR_ENTRY.finditer(table.group("body")):
        motors[match.group("name")] = (match.group("pwm"), match.group("digital"))
    if not motors:
        fail("the MOTORS table in {0} parsed to zero motors".format(FIRMWARE))

    singles = {}
    for name in ("ENABLE_PIN", "PIXEL_PIN", "INDEX_PIN"):
        match = re.search(SINGLE_PIN.format(name), source, re.M)
        if match is None:
            fail("{0} is not assigned a board pin in {1}".format(name, FIRMWARE))
        singles[name] = match.group(1)
    return motors, singles["ENABLE_PIN"], singles["PIXEL_PIN"], singles["INDEX_PIN"]


def check_wiring(motors, enable_pin, pixel_pin, index_pin):
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

    found = {}
    seen_pins = set()
    for row in rows:
        for side, pin_key in (("source", "source_pin"), ("target", "target_pin")):
            if row[side] != KB2040:
                continue
            pin = row[pin_key]
            seen_pins.add(pin)
            match = re.match(r"^SIG-(?P<name>[a-z0-9\-]+)-(?P<kind>PWM|DIR)$", row["net"])
            if match:
                found.setdefault(match.group("name"), {})[match.group("kind")] = pin

    problems = []
    for name, (pwm_pin, digital_pin) in sorted(motors.items()):
        if name not in found:
            problems.append("motor {0}: no SIG-{0}-PWM / SIG-{0}-DIR rows in wiring.csv".format(name))
            continue
        actual = found[name]
        if actual.get("PWM") != pwm_pin:
            problems.append("motor {0} PWM pin: wiring.csv says {1}, code.py says {2}".format(
                name, actual.get("PWM"), pwm_pin))
        if actual.get("DIR") != digital_pin:
            problems.append("motor {0} direction pin: wiring.csv says {1}, code.py says {2}".format(
                name, actual.get("DIR"), digital_pin))
    for name in sorted(set(found) - set(motors)):
        problems.append("wiring.csv drives a motor {0} that code.py does not have".format(name))

    for net, pin, label in ((r"^SIG-SLP$", enable_pin, "DRV8833 SLP"),
                            (r"^NEOPIXEL$", pixel_pin, "NeoPixel data"),
                            (r"^SIG-DOME-INDEX$", index_pin, "dome index sensor")):
        pins = {row["source_pin"] for row in rows
                if row["source"] == KB2040 and re.match(net, row["net"])}
        if pins != {pin}:
            problems.append("{0}: wiring.csv uses {1}, code.py says {2}".format(
                label, sorted(pins) or "nothing", pin))

    allowed = set()
    for pwm_pin, digital_pin in motors.values():
        allowed.update((pwm_pin, digital_pin))
    allowed.update({enable_pin, pixel_pin, index_pin, "3V3 pad", "GND pad", "USB-C"})
    unknown = sorted(seen_pins - allowed)
    if unknown:
        problems.append("wiring.csv uses KB2040 pins the firmware never mentions: "
                        + ", ".join(unknown))

    if problems:
        for problem in problems:
            print("FAIL: " + problem)
        sys.exit(1)
    return len(rows)


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

    motors, enable_pin, pixel_pin, index_pin = read_firmware_pins()
    wires = check_wiring(motors, enable_pin, pixel_pin, index_pin)

    print("PASS: {0} SVG sheets parse, wiring.csv has {1} wires, and all {2} KB2040 pins "
          "match firmware/kb2040/code.py".format(len(SHEETS), wires, 2 * len(motors) + 3))


if __name__ == "__main__":
    main()
