"""Pin map and wiring net list for doorbot, checked against the T-Display's own constraints.

The check matters: the T-Display's display owns six GPIO, six more are wired to flash, five are
strapping pins and six are input-only. Assigning a signal to the wrong one of those fails
silently on a bench and is very hard to see in a photograph.

    python scripts/electronics.py          # print the tables, write docs/wiring.json
"""
import json
import re

from scad_params import ROOT

# LilyGO T-Display facts, from the board's schematic and the ESP32 datasheet.
DISPLAY_PINS = {4: "TFT backlight", 5: "TFT CS", 16: "TFT DC", 18: "TFT SCLK",
                19: "TFT MOSI", 23: "TFT RST"}
FLASH_PINS = {6, 7, 8, 9, 10, 11}
NOT_BROKEN_OUT = {1: "UART0 TX", 3: "UART0 RX", 14: "not routed to a header"}
STRAPPING_PINS = {0, 2, 5, 12, 15}
INPUT_ONLY = {34, 35, 36, 37, 38, 39}
ONBOARD = {35: "top button", 0: "bottom button", 34: "battery ADC"}

# signal, gpio, direction, note
PINS = [
    ("I2C SDA", 21, "bidir", "LilyGO's own I2C pin; both VL53 boards and the LIS3DH share it"),
    ("I2C SCL", 22, "out", "LilyGO's own I2C pin"),
    ("MOTOR IN1", 32, "out", "LEDC PWM channel 0, 20 kHz"),
    ("MOTOR IN2", 33, "out", "LEDC PWM channel 1, 20 kHz"),
    ("MOTOR nSLEEP", 27, "out", "add a 100k pulldown so the driver sleeps through reset"),
    ("MOTOR nFAULT", 36, "in", "input-only pin; the driver's open-drain output needs a pull-up"),
    ("TOF WAVE XSHUT", 25, "out", "held low at boot so both sensors can be addressed in turn"),
    ("TOF GUARD XSHUT", 26, "out", "as above"),
    ("ACCEL INT1", 39, "in", "input-only pin; the LIS3DH drives it push-pull"),
    ("ENCODER", 37, "in", "input-only pin; the slot sensor drives it push-pull"),
    ("BUZZER", 17, "out", "through a transistor for a magnetic buzzer; direct for a piezo"),
    ("BUTTON (close now)", 35, "in", "on-board top button, active low with a 100k pull-up"),
]

NETS = [
    ("USB-C 5 V", "T-Display USB connector",
     "the only power input. The motor's 5 V is taken from the same USB source AT THE DRIVER, "
     "not through the T-Display: the board's only VBUS path to its 5V header pin is a single "
     "1 A 1N5819, unfused, and it also feeds the 3.3 V regulator and the USB-serial bridge, so "
     "a 1 A motor step on that node browns out the ESP32"),
    ("GND star", "one point at the driver board",
     "motor return and logic return meet once, at the driver. The T-Display header GND carries "
     "logic current only"),
    ("VM decoupling", "100 uF electrolytic + 0.1 uF ceramic across the driver's VM and GND",
     "TI's minimum is 10 uF on VM; a 1.0 A chopped stall on a shared USB rail earns more"),
    ("Motor", "DRV8833 AOUT1/AOUT2 to the TT motor",
     "polarity only sets which way the drum winds. Swap the two leads if the first close pays "
     "cable out instead of taking it in"),
    ("I2C chain", "T-Display 3V3/GND/21/22 to VL53L4CD, then VL53L1X, then LIS3DH",
     "STEMMA QT cables daisy-chain all three; the two VL53 boards also need their XSHUT lines "
     "run individually to GPIO 25 and 26 or they will both sit on 0x29 and fight"),
]


def firmware_pins():
    """Read the pin numbers the firmware actually compiles with."""
    text = (ROOT / "firmware/include/config.h").read_text(encoding="utf-8")
    return {m.group(1): int(m.group(2))
            for m in re.finditer(r"#define\s+(PIN_\w+)\s+(\d+)", text)}


def main():
    problems = []
    used = {}
    for signal, gpio, direction, _ in PINS:
        if gpio in DISPLAY_PINS:
            problems.append(f"{signal} on GPIO{gpio} collides with the display "
                            f"({DISPLAY_PINS[gpio]})")
        if gpio in FLASH_PINS:
            problems.append(f"{signal} on GPIO{gpio} is wired to the flash chip")
        if gpio in NOT_BROKEN_OUT:
            problems.append(f"{signal} on GPIO{gpio} is {NOT_BROKEN_OUT[gpio]}")
        if gpio in STRAPPING_PINS:
            problems.append(f"{signal} on GPIO{gpio} is a strapping pin")
        if gpio in INPUT_ONLY and direction != "in":
            problems.append(f"{signal} drives GPIO{gpio}, which is input-only")
        if gpio in used:
            problems.append(f"GPIO{gpio} is claimed by both {used[gpio]} and {signal}")
        if gpio in ONBOARD and signal.split()[0] != "BUTTON":
            problems.append(f"{signal} on GPIO{gpio} is the on-board {ONBOARD[gpio]}")
        used[gpio] = signal

    # the firmware must agree with this table
    want = {"PIN_SDA": 21, "PIN_SCL": 22, "PIN_MOTOR_IN1": 32, "PIN_MOTOR_IN2": 33,
            "PIN_MOTOR_SLEEP": 27, "PIN_MOTOR_FAULT": 36, "PIN_TOF_WAVE_XSHUT": 25,
            "PIN_TOF_GUARD_XSHUT": 26, "PIN_ACCEL_INT": 39, "PIN_ENCODER": 37,
            "PIN_BUZZER": 17, "PIN_BUTTON_TOP": 35}
    have = firmware_pins()
    for name, gpio in want.items():
        if have.get(name) != gpio:
            problems.append(f"firmware/include/config.h has {name}={have.get(name)}, "
                            f"this table says {gpio}")

    width = max(len(s) for s, *_ in PINS)
    print(f"{'signal'.ljust(width)}  gpio  dir    note")
    for signal, gpio, direction, note in PINS:
        print(f"{signal.ljust(width)}  {gpio:>4}  {direction:<5}  {note}")
    print()
    for name, where, note in NETS:
        print(f"{name}: {where}\n    {note}")

    report = {"all_pass": not problems,
              "pins": [{"signal": s, "gpio": g, "direction": d, "note": n} for s, g, d, n in PINS],
              "nets": [{"net": n, "where": w, "note": x} for n, w, x in NETS],
              "problems": problems,
              "spare_gpio": sorted({13, 38, 2, 12, 15} - set(used)),
              "current_budget_a": {"motor_chop": 1.0, "esp32_peak": 0.5, "sensors": 0.05}}
    (ROOT / "docs").mkdir(exist_ok=True)
    (ROOT / "docs/wiring.json").write_text(json.dumps(report, indent=2))
    if problems:
        for p in problems:
            print("FAIL  " + p)
        raise SystemExit(f"{len(problems)} wiring problems")
    print("\nPASS: 12 signals, no collision with the display, flash, strapping or input-only "
          "pins, and the firmware's config.h agrees with this table.")


if __name__ == "__main__":
    main()
