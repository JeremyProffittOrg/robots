"""Generate the fable-r2d2 electrical drawing set, harness list and rail calculations.

Standard library only.  Run it with ``python scripts/electronics.py``, which also
checks the result against the firmware pin map.

Outputs, all written next to this file in ``electronics/``:

============================  =========================================================
``01-power-and-charging.svg`` battery, main fuse, switch, charge port, the three
                              regulators with their fuses, the star ground and the
                              charger plug polarity
``02-motor-drive.svg``        KB2040 to the four DRV8833 boards with the final firmware
                              pin names, the seven motors, the shared SLP line and the
                              JST-XH connectors
``03-head-electronics.svg``   the twelve slip-ring wires, both PSI jewels, the three
                              holoprojectors, the four matrix backpacks with their
                              addresses and jumper settings, and the radar-eye TFT
``04-pi-audio-and-links.svg`` the Raspberry Pi header pins in use, the USB link to the
                              KB2040, the amplifier and speaker, the 5 V feed and the
                              ADS1115 battery divider
``wiring.csv``                one row per wire
``calculations.json``         rail currents, fuse ratings, ampacity checks and runtime
============================  =========================================================

Sources for every number: ``research/loads.md`` section 6 (currents, fuses, wire
gauge, runtime), ``research/components-electronics.md`` ("12 V power tree and
fusing"), ``firmware/kb2040/code.py`` (the motor pin map), ``firmware/pi/displays.py``
(I2C addresses and SPI pins), ``firmware/pi/battery.py`` (the ADS1115 divider) and
``cad/params.scad`` (where each part sits, which sets the length estimates).
"""

import csv
import json
import xml.etree.ElementTree as ET
from html import escape
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent

# ---------------------------------------------------------------------------
# Harness
# ---------------------------------------------------------------------------

ROWS = []

# Motor table, mirrored from firmware/kb2040/code.py MOTORS.  scripts/electronics.py
# re-reads that file and fails if these two ever drift apart.
MOTORS = [
    # ref,  name,       driver, channel, pwm pin, digital pin, foot,          route
    ("M1", "lf-front", "U1", "A", "D3", "D2", "left foot", "body_upper tray -> left leg -> left foot"),
    ("M2", "lf-rear", "U1", "B", "D5", "D4", "left foot", "body_upper tray -> left leg -> left foot"),
    ("M3", "rf-front", "U2", "A", "D7", "D6", "right foot", "body_upper tray -> right leg -> right foot"),
    ("M4", "rf-rear", "U2", "B", "D9", "D8", "right foot", "body_upper tray -> right leg -> right foot"),
    ("M5", "cf-front", "U3", "A", "D10", "MOSI", "centre foot", "body_upper tray -> body_lower -> centre leg -> centre foot"),
    ("M6", "cf-rear", "U3", "B", "SCK", "MISO", "centre foot", "body_upper tray -> body_lower -> centre leg -> centre foot"),
    ("M7", "head", "U4", "A", "A1", "A0", "head drive", "body_upper tray -> under the body top plate"),
]

SLP_PIN = "D1"
PIXEL_PIN = "A2"
INDEX_PIN = "A3"

# The twelve Adafruit 1195 slip-ring wires, in the order they are documented.
SLIP_RING = [
    (1, "5V-DOME", "5 V dome feed, leg 1 of 2", "red", "F6 fuse output (5 V rail)"),
    (2, "5V-DOME", "5 V dome feed, leg 2 of 2", "red", "F6 fuse output (5 V rail)"),
    (3, "GND", "dome return, leg 1 of 2", "black", "star ground TB2"),
    (4, "GND", "dome return, leg 2 of 2", "black", "star ground TB2"),
    (5, "NEOPIXEL", "NeoPixel data to LED1", "green", "KB2040 A2"),
    (6, "SDA", "I2C-1 data, four backpacks", "white", "Pi GPIO2 (header pin 3)"),
    (7, "SCL", "I2C-1 clock, four backpacks", "yellow", "Pi GPIO3 (header pin 5)"),
    (8, "SPI-MOSI", "SPI0 MOSI to the TFT", "blue", "Pi GPIO10 (header pin 19)"),
    (9, "SPI-SCLK", "SPI0 clock to the TFT", "blue", "Pi GPIO11 (header pin 23)"),
    (10, "TFT-CS", "SPI0 CE0 chip select", "green", "Pi GPIO8 (header pin 24)"),
    (11, "TFT-DC", "TFT data/command", "white", "Pi GPIO25 (header pin 22)"),
    (12, "TFT-RST", "TFT reset", "yellow", "Pi GPIO24 (header pin 18)"),
]

MATRICES = [
    ("DS1", 0x70, "front logic, upper window", "none bridged"),
    ("DS2", 0x71, "front logic, lower window", "A0 bridged"),
    ("DS3", 0x72, "rear logic, left half", "A1 bridged"),
    ("DS4", 0x73, "rear logic, right half", "A0 and A1 bridged"),
]

PI_HEADER = [
    ("1", "3V3", "U9 ADS1115 VDD"),
    ("3", "GPIO2 / SDA1", "slip ring 6 -> four HT16K33 backpacks; U9 SDA"),
    ("5", "GPIO3 / SCL1", "slip ring 7 -> four HT16K33 backpacks; U9 SCL"),
    ("6", "GND", "star ground TB2 and U9 GND"),
    ("12", "GPIO18", "radar-eye backlight control (not wired: see note)"),
    ("18", "GPIO24", "slip ring 12 -> TFT RST"),
    ("19", "GPIO10 / MOSI", "slip ring 8 -> TFT MOSI"),
    ("22", "GPIO25", "slip ring 11 -> TFT DC"),
    ("23", "GPIO11 / SCLK", "slip ring 9 -> TFT SCLK"),
    ("24", "GPIO8 / CE0", "slip ring 10 -> TFT CS"),
]


def wire(net, source, source_pin, target, target_pin, gauge, colour, length, route):
    """Append one harness row."""
    ROWS.append({
        "wire_id": "W{0:03d}".format(len(ROWS) + 1),
        "net": net,
        "source": source,
        "source_pin": source_pin,
        "target": target,
        "target_pin": target_pin,
        "gauge_awg": gauge,
        "colour": colour,
        "length_mm_estimate": length,
        "route": route,
    })


def build_harness():
    """Fill ROWS with every wire in the robot."""
    body = "body_lower"
    tray = "body_upper tray"
    lower_to_tray = "body_lower -> body_upper tray"
    plate = "body_upper tray -> body top plate"
    dome = "dome (after the slip ring)"

    # -- 12 V distribution ------------------------------------------------
    wire("BAT-POS", "BT1", "+ (F2 blade)", "J10", "red housing", 16, "red", 200,
         body + " (battery shelf)")
    wire("BAT-POS", "J10", "red housing", "FH1", "in", 16, "red", 150, body)
    wire("BAT-FUSED", "FH1", "out (F1 15 A)", "SW1", "term 1 (battery side)", 16, "red", 260,
         body + " -> rear lower band")
    wire("12V-BUS", "SW1", "term 2 (load side)", "TB2", "12V+ stud", 16, "red", 420, lower_to_tray)
    wire("BAT-NEG", "BT1", "- (F2 blade)", "J10", "black housing", 16, "black", 200,
         body + " (battery shelf)")
    wire("GND", "J10", "black housing", "TB2", "star ground stud", 16, "black", 420, lower_to_tray)

    # -- charging branch, battery side of the switch -----------------------
    wire("CHG-POS", "J1", "centre pin (+)", "FH2", "in", 16, "red", 180,
         "rear lower band of " + body)
    wire("CHG-FUSED", "FH2", "out (F2 3 A)", "SW1", "term 1 (battery side)", 16, "red", 160,
         "rear lower band of " + body)
    wire("GND", "J1", "sleeve (-)", "TB2", "star ground stud", 16, "black", 430, lower_to_tray)

    # -- regulators --------------------------------------------------------
    wire("12V-BUS", "TB2", "12V+ stud", "FH3", "in", 16, "red", 120, tray)
    wire("5V-REG-IN", "FH3", "out (F3 3 A)", "U5", "VIN", 16, "red", 120, tray)
    wire("GND", "TB2", "star ground stud", "U5", "GND", 16, "black", 120, tray)
    wire("12V-BUS", "TB2", "12V+ stud", "FH4", "in", 16, "red", 120, tray)
    wire("6VA-REG-IN", "FH4", "out (F4 5 A)", "U6", "VIN", 16, "red", 120, tray)
    wire("GND", "TB2", "star ground stud", "U6", "GND", 16, "black", 120, tray)
    wire("12V-BUS", "TB2", "12V+ stud", "FH5", "in", 16, "red", 120, tray)
    wire("6VB-REG-IN", "FH5", "out (F5 5 A)", "U7", "VIN", 16, "red", 120, tray)
    wire("GND", "TB2", "star ground stud", "U7", "GND", 16, "black", 120, tray)

    # -- 5 V rail ----------------------------------------------------------
    wire("5V", "U5", "VOUT", "J12", "VBUS", 16, "red", 220, tray)
    wire("GND", "U5", "GND", "J12", "GND", 16, "black", 220, tray)
    wire("5V-USB", "J12", "USB-C plug", "A1", "USB-C power input", 16, "red", 0,
         tray + " (the plug is the connector, not a wire)")
    wire("5V", "U5", "VOUT", "FH6", "in", 22, "red", 140, tray)
    wire("5V", "U5", "VOUT", "U8", "VIN", 22, "red", 260, tray)
    wire("GND", "TB2", "star ground stud", "U8", "GND", 22, "black", 260, tray)

    # -- 6 V motor rails ---------------------------------------------------
    for regulator, drivers in (("U6", ("U1", "U3")), ("U7", ("U2", "U4"))):
        for driver in drivers:
            wire("6V-" + regulator, regulator, "VOUT", driver, "VMOTOR", 22, "red", 150, tray)
            wire("GND", "TB2", "star ground stud", driver, "GND", 22, "black", 150, tray)

    # -- battery sense divider (firmware/pi/battery.py) ---------------------
    wire("12V-BUS", "TB2", "12V+ stud", "R2", "100k leg 1", 22, "red", 150, tray)
    wire("VBAT-SENSE", "R2", "100k leg 2", "R3", "15k leg 1", 22, "white", 20, tray)
    wire("VBAT-SENSE", "R3", "15k leg 1", "U9", "A0", 22, "white", 120, tray)
    wire("GND", "R3", "15k leg 2", "TB2", "star ground stud", 22, "black", 150, tray)
    wire("3V3", "A1", "header pin 1 (3V3)", "U9", "VDD", 22, "red", 180, tray)
    wire("GND", "A1", "header pin 6 (GND)", "U9", "GND", 22, "black", 180, tray)
    wire("SDA", "A1", "header pin 3 (GPIO2)", "U9", "SDA", 22, "white", 180, tray)
    wire("SCL", "A1", "header pin 5 (GPIO3)", "U9", "SCL", 22, "yellow", 180, tray)

    # -- Pi to KB2040 ------------------------------------------------------
    wire("USB-LINK", "A1", "USB 2.0 type A port", "A2", "USB-C", 0, "cable J11", 1000,
         tray + " (5 V power and the USB CDC serial link)")

    # -- motor control signals --------------------------------------------
    for ref, name, driver, channel, pwm_pin, dig_pin, foot, route in MOTORS:
        wire("SIG-{0}-PWM".format(name), "A2", pwm_pin, driver,
             "{0}IN2".format(channel), 22, "green", 140, tray)
        wire("SIG-{0}-DIR".format(name), "A2", dig_pin, driver,
             "{0}IN1".format(channel), 22, "white", 140, tray)
    for driver in ("U1", "U2", "U3", "U4"):
        wire("SIG-SLP", "A2", SLP_PIN, driver, "SLP", 22, "yellow", 140, tray)

    # -- motor power pairs -------------------------------------------------
    lengths = {"left foot": 820, "right foot": 820, "centre foot": 760, "head drive": 300}
    for ref, name, driver, channel, pwm_pin, dig_pin, foot, route in MOTORS:
        length = lengths[foot]
        wire("MOT-{0}-A".format(name), driver, "{0}OUT1".format(channel), ref,
             "terminal + (JST-XH pin 1)", 22, "yellow", length, route)
        wire("MOT-{0}-B".format(name), driver, "{0}OUT2".format(channel), ref,
             "terminal - (JST-XH pin 2)", 22, "blue", length, route)
    wire("GND", "TB2", "star ground stud", "U4", "BIN1 and BIN2 (tied low)", 22, "black", 150,
         tray + " (driver 4 channel B is unused)")

    # -- dome index sensor (optional) --------------------------------------
    wire("3V3", "A2", "3V3 pad", "SQ1", "pin 1 (VCC)", 22, "red", 420, plate)
    wire("GND", "A2", "GND pad", "SQ1", "pin 2 (GND)", 22, "black", 420, plate)
    wire("SIG-DOME-INDEX", "A2", INDEX_PIN, "SQ1", "pin 3 (open drain out)", 22, "green", 420,
         plate + " (magnet on the dome plate)")

    # -- slip ring, body side ---------------------------------------------
    sources = {
        1: ("FH6", "out (F6 2 A)"), 2: ("FH6", "out (F6 2 A)"),
        3: ("TB2", "star ground stud"), 4: ("TB2", "star ground stud"),
        5: ("A2", PIXEL_PIN),
        6: ("A1", "header pin 3 (GPIO2)"), 7: ("A1", "header pin 5 (GPIO3)"),
        8: ("A1", "header pin 19 (GPIO10)"), 9: ("A1", "header pin 23 (GPIO11)"),
        10: ("A1", "header pin 24 (GPIO8)"), 11: ("A1", "header pin 22 (GPIO25)"),
        12: ("A1", "header pin 18 (GPIO24)"),
    }
    for number, net, purpose, colour, _origin in SLIP_RING:
        source, pin = sources[number]
        wire(net, source, pin, "SR1", "stator wire {0}".format(number), 22, colour, 520,
             plate + " -> slip-ring post")

    # -- dome: NeoPixel chain ---------------------------------------------
    wire("NEOPIXEL", "SR1", "rotor wire 5", "LED1", "DIN", 22, "green", 260, dome)
    chain = [("LED1", "LED2", 300), ("LED2", "LED3", 260), ("LED3", "LED4", 150),
             ("LED4", "LED5", 150)]
    for upstream, downstream, length in chain:
        wire("NEOPIXEL", upstream, "DOUT", downstream, "DIN", 22, "green", length, dome)
    for index, pixel in enumerate(("LED1", "LED2", "LED3", "LED4", "LED5")):
        wire("5V-DOME", "SR1", "rotor wire {0}".format(1 + index % 2), pixel, "5V", 22, "red",
             240 + 30 * index, dome)
        wire("GND", "SR1", "rotor wire {0}".format(3 + index % 2), pixel, "GND", 22, "black",
             240 + 30 * index, dome)

    # -- dome: matrix backpacks -------------------------------------------
    for index, (ref, address, place, jumper) in enumerate(MATRICES):
        wire("SDA", "SR1", "rotor wire 6", ref, "SDA (0x{0:02x})".format(address), 22, "white",
             220 + 40 * index, dome)
        wire("SCL", "SR1", "rotor wire 7", ref, "SCL (0x{0:02x})".format(address), 22, "yellow",
             220 + 40 * index, dome)
        wire("5V-DOME", "SR1", "rotor wire 2", ref, "+", 22, "red", 220 + 40 * index, dome)
        wire("GND", "SR1", "rotor wire 4", ref, "-", 22, "black", 220 + 40 * index, dome)

    # -- dome: radar eye TFT ----------------------------------------------
    for net, rotor, pin, colour in (
        ("SPI-MOSI", 8, "MOSI", "blue"), ("SPI-SCLK", 9, "SCK", "blue"),
        ("TFT-CS", 10, "CS", "green"), ("TFT-DC", 11, "DC", "white"),
        ("TFT-RST", 12, "RST", "yellow"),
    ):
        wire(net, "SR1", "rotor wire {0}".format(rotor), "DS5", pin, 22, colour, 300, dome)
    wire("5V-DOME", "SR1", "rotor wire 1", "DS5", "VIN", 22, "red", 300, dome)
    wire("GND", "SR1", "rotor wire 3", "DS5", "GND", 22, "black", 300, dome)
    wire("5V-DOME", "SR1", "rotor wire 1", "R1", "100 ohm leg 1", 22, "red", 300, dome)
    wire("TFT-BL", "R1", "100 ohm leg 2", "DS5", "LITE (backlight)", 22, "white", 30, dome)

    # -- audio -------------------------------------------------------------
    wire("AUDIO-L", "A1", "3.5 mm jack, tip (left)", "R4A", "10k leg 1", 22, "white", 260,
         tray + " (short shielded lead)")
    wire("AUDIO-R", "A1", "3.5 mm jack, ring (right)", "R4B", "10k leg 1", 22, "yellow", 260, tray)
    wire("AUDIO-SUM", "R4A", "10k leg 2", "U8", "A+", 22, "white", 40, tray)
    wire("AUDIO-SUM", "R4B", "10k leg 2", "U8", "A+", 22, "yellow", 40, tray)
    wire("GND", "A1", "3.5 mm jack, sleeve", "U8", "A-", 22, "black", 260, tray)
    wire("SPK+", "U8", "OUT+", "LS1", "+ tab", 22, "yellow", 420,
         tray + " -> front vent of body_lower")
    wire("SPK-", "U8", "OUT-", "LS1", "- tab", 22, "blue", 420,
         tray + " -> front vent of body_lower")


# ---------------------------------------------------------------------------
# SVG sheet drawing
# ---------------------------------------------------------------------------

INK = "#12283d"
RULE = "#5b7c99"
PANEL = "#f2f7fb"
NET = "#00507f"
COLOURS = {
    "12v": "#c62828", "6v": "#ef6c00", "5v": "#ad1457", "gnd": "#263238",
    "signal": "#1565c0", "data": "#2e7d32", "note": "#5b7c99",
}
FONT_SIZES = {"title": 27, "sub": 16, "head": 19, "body": 15, "small": 13, "net": 14}
CHAR_WIDTH = {"title": 0.58, "sub": 0.52, "head": 0.56, "body": 0.52, "small": 0.52,
              "net": 0.60}


OVERFLOW = []


def text_width(content, style):
    """Rough rendered width in pixels, used to keep text inside its box."""
    return len(content) * FONT_SIZES[style] * CHAR_WIDTH[style]


def fits(content, style, limit, context):
    """Record any text that would run outside its box.  main() raises on the list."""
    width = text_width(content, style)
    if width > limit:
        OVERFLOW.append("{0}: {1:.0f}px > {2:.0f}px  |  {3}".format(
            context, width, limit, content))
    return content


class Sheet:
    """One schematic sheet.  Every helper returns the y it finished at."""

    def __init__(self, title, subtitle, width=1680, height=1150):
        self.width = width
        self.height = height
        self.parts = []
        self.parts.append(
            '<svg xmlns="http://www.w3.org/2000/svg" width="{0}" height="{1}" '
            'viewBox="0 0 {0} {1}">'.format(width, height))
        self.parts.append('<rect width="{0}" height="{1}" fill="#ffffff"/>'.format(width, height))
        self.text(36, 46, title, "title")
        self.text(36, 74, subtitle, "sub", fill=RULE)
        self.rule(36, 88, width - 36)

    # -- primitives -------------------------------------------------------

    def text(self, x, y, content, style="body", fill=None, anchor="start", bold=None):
        weight = "bold" if (bold if bold is not None else style in ("title", "head")) else "normal"
        family = "Consolas, monospace" if style == "net" else "Arial, Helvetica, sans-serif"
        self.parts.append(
            '<text x="{0}" y="{1}" font-family="{2}" font-size="{3}" font-weight="{4}" '
            'fill="{5}" text-anchor="{6}">{7}</text>'.format(
                x, y, family, FONT_SIZES[style], weight, fill or INK, anchor, escape(content)))

    def rule(self, x1, y, x2, colour=None):
        self.parts.append(
            '<line x1="{0}" y1="{1}" x2="{2}" y2="{1}" stroke="{3}" stroke-width="1.2"/>'.format(
                x1, y, x2, colour or RULE))

    def line(self, x1, y1, x2, y2, colour=None, dash=None, width=2.2):
        extra = ' stroke-dasharray="{0}"'.format(dash) if dash else ""
        self.parts.append(
            '<line x1="{0}" y1="{1}" x2="{2}" y2="{3}" stroke="{4}" stroke-width="{5}" '
            'stroke-linecap="round"{6}/>'.format(x1, y1, x2, y2, colour or INK, width, extra))

    def path(self, points, colour=None, width=2.2):
        d = "M{0},{1}".format(*points[0]) + "".join(" L{0},{1}".format(x, y) for x, y in points[1:])
        self.parts.append(
            '<path d="{0}" fill="none" stroke="{1}" stroke-width="{2}" stroke-linecap="round" '
            'stroke-linejoin="round"/>'.format(d, colour or INK, width))

    def dot(self, x, y, colour=None):
        self.parts.append('<circle cx="{0}" cy="{1}" r="4.5" fill="{2}"/>'.format(
            x, y, colour or INK))

    def arrow(self, x1, y1, x2, y2, colour=None):
        colour = colour or INK
        self.line(x1, y1, x2, y2, colour)
        if x2 >= x1:
            self.path([(x2 - 11, y2 - 6), (x2, y2), (x2 - 11, y2 + 6)], colour, 2.2)
        else:
            self.path([(x2 + 11, y2 - 6), (x2, y2), (x2 + 11, y2 + 6)], colour, 2.2)

    def ground(self, x, y, colour=None):
        colour = colour or COLOURS["gnd"]
        self.line(x, y, x, y + 14, colour)
        for dy, half in ((14, 16), (21, 10), (28, 4)):
            self.line(x - half, y + dy, x + half, y + dy, colour)

    # -- blocks -----------------------------------------------------------

    def box(self, x, y, width, title, lines, accent=None, style="body"):
        """Draw a titled block whose height follows its content.  Returns bottom y."""
        pad = 14
        line_height = FONT_SIZES[style] + 7
        height = pad + 26 + line_height * len(lines) + pad - (6 if lines else 18)
        self.parts.append(
            '<rect x="{0}" y="{1}" width="{2}" height="{3}" rx="7" fill="{4}" stroke="{5}" '
            'stroke-width="1.6"/>'.format(x, y, width, height, PANEL, accent or RULE))
        if accent:
            self.parts.append(
                '<rect x="{0}" y="{1}" width="6" height="{2}" rx="3" fill="{3}"/>'.format(
                    x, y, height, accent))
        fits(title, "head", width - 2 * pad, "box title")
        self.text(x + pad + 6, y + pad + 16, title, "head")
        for index, content in enumerate(lines):
            fits(content, style, width - 2 * pad - 6, "box " + title)
            self.text(x + pad + 6, y + pad + 26 + line_height * (index + 1) - 6, content, style)
        return y + height

    def pin_table(self, x, y, width, title, rows, left_width=None, accent=None):
        """Two-column connector pinout.  Returns bottom y."""
        pad = 14
        line_height = 22
        left_width = left_width or int(width * 0.34)
        height = pad + 26 + line_height * len(rows) + pad - 6
        self.parts.append(
            '<rect x="{0}" y="{1}" width="{2}" height="{3}" rx="7" fill="#ffffff" stroke="{4}" '
            'stroke-width="1.6"/>'.format(x, y, width, height, accent or RULE))
        self.text(x + pad, y + pad + 16, title, "head")
        for index, (left, right) in enumerate(rows):
            row_y = y + pad + 26 + line_height * (index + 1) - 6
            fits(left, "net", left_width - 10, "pin name in " + title)
            fits(right, "small", width - left_width - pad - 10, "pin note in " + title)
            self.text(x + pad, row_y, left, "net", fill=NET)
            self.text(x + left_width, row_y, right, "small")
            if index < len(rows) - 1:
                self.rule(x + pad, row_y + 7, x + width - pad, "#dde7ef")
        return y + height

    def legend(self, x, y, width, entries, title="Legend"):
        pad = 14
        line_height = 22
        height = pad + 26 + line_height * len(entries) + pad - 6
        self.parts.append(
            '<rect x="{0}" y="{1}" width="{2}" height="{3}" rx="7" fill="#ffffff" stroke="{4}" '
            'stroke-width="1.6"/>'.format(x, y, width, height, RULE))
        self.text(x + pad, y + pad + 16, title, "head")
        for index, (colour, label) in enumerate(entries):
            row_y = y + pad + 26 + line_height * (index + 1) - 6
            self.line(x + pad, row_y - 5, x + pad + 34, row_y - 5, colour, width=4)
            fits(label, "small", width - pad - 52, "legend " + title)
            self.text(x + pad + 46, row_y, label, "small")
        return y + height

    def fuse(self, x, y, label, colour=None):
        """Fuse symbol drawn left to right from (x, y); returns the x it ends at."""
        colour = colour or COLOURS["12v"]
        self.line(x, y, x + 14, y, colour)
        self.parts.append(
            '<rect x="{0}" y="{1}" width="58" height="18" rx="4" fill="#ffffff" stroke="{2}" '
            'stroke-width="2"/>'.format(x + 14, y - 9, colour))
        self.line(x + 14, y, x + 72, y, colour, width=1.6)
        self.line(x + 72, y, x + 86, y, colour)
        self.text(x + 43, y - 16, label, "small", anchor="middle")
        return x + 86

    def switch(self, x, y, label, colour=None):
        colour = colour or COLOURS["12v"]
        self.line(x, y, x + 16, y, colour)
        self.dot(x + 16, y, colour)
        self.line(x + 16, y, x + 58, y - 22, colour)
        self.dot(x + 74, y, colour)
        self.line(x + 74, y, x + 96, y, colour)
        self.text(x + 48, y - 44, label, "small", anchor="middle")
        return x + 96

    def motor(self, x, y, label):
        self.parts.append(
            '<circle cx="{0}" cy="{1}" r="22" fill="#ffffff" stroke="{2}" stroke-width="2"/>'
            .format(x, y, INK))
        self.text(x, y + 7, "M", "head", anchor="middle")
        self.text(x, y + 42, label, "small", anchor="middle")

    def save(self, name, footer):
        self.rule(36, self.height - 44, self.width - 36)
        self.text(36, self.height - 22, footer, "small", fill=RULE)
        content = "\n".join(self.parts + ["</svg>"])
        ET.fromstring(content)  # fail loudly on malformed XML
        (HERE / name).write_text(content, encoding="utf-8")
        return name


FOOTER = ("fable-r2d2 electrical set, 2026-09-12  |  sheets 01-04 and electronics/wiring.csv "
          "are one drawing set  |  pin names are the final firmware names in "
          "firmware/kb2040/code.py  |  not yet validated on hardware")


# ---------------------------------------------------------------------------
# Sheet 01 - power and charging
# ---------------------------------------------------------------------------

def sheet_power():
    s = Sheet("01  Power and charging",
              "12 V 7 Ah SLA, one main fuse, one switch, three regulators, one star ground. "
              "Charging reaches the battery with the switch off.",
              1680, 1235)

    # Schematic chain across the top.
    y = 208
    s.text(36, 128, "A.  Battery, main fuse, switch and the 12 V bus", "head")
    s.box(36, 152, 250, "BT1  12 V 7 Ah SLA",
          ["Power-Sonic PS-1270 F2", "F2 blades, 6.35 mm", "on the body_lower shelf"],
          COLOURS["12v"])
    s.line(286, y, 330, y, COLOURS["12v"])
    s.parts.append('<rect x="330" y="{0}" width="72" height="34" rx="5" fill="#ffffff" '
                   'stroke="{1}" stroke-width="2"/>'.format(y - 17, COLOURS["12v"]))
    s.text(366, y + 5, "J10", "net", fill=NET, anchor="middle")
    s.text(366, y + 44, "Powerpole", "small", anchor="middle")
    end = s.fuse(412, y, "F1  15 A  (holder FH1)")
    node_x = end + 22
    s.line(end, y, node_x, y, COLOURS["12v"])
    s.dot(node_x, y, COLOURS["12v"])
    end = s.switch(node_x, y, "SW1  Carling 20 A rocker")
    s.line(end, y, end + 80, y, COLOURS["12v"])
    s.dot(end + 80, y, COLOURS["12v"])
    s.text(end + 94, y + 5, "12V-BUS", "net", fill=NET)
    s.line(end + 80, y, end + 80, y + 132, COLOURS["12v"])
    s.text(end + 94, y + 136, "to the three regulator fuses (B)", "small")

    # Charge branch enters on the battery side of the switch.
    charge_y = 340
    s.box(36, 288, 250, "J1  charge jack",
          ["Switchcraft L722A", "5.5 x 2.1 mm, centre +", "rear lower band"], COLOURS["12v"])
    s.line(286, charge_y, 330, charge_y, COLOURS["12v"])
    end = s.fuse(330, charge_y, "F2  3 A  (holder FH2)")
    s.path([(end, charge_y), (node_x, charge_y), (node_x, y)], COLOURS["12v"])
    s.text(end + 60, charge_y - 16, "joins the BATTERY side of SW1", "small")
    s.text(end + 60, charge_y + 16, "so the charger works with the robot switched off,",
           "small", fill=RULE)
    s.text(end + 60, charge_y + 38, "and SW1 still isolates every load.", "small", fill=RULE)

    s.ground(160, 418)
    s.text(196, 440, "J1 sleeve and BT1 minus go straight to the star ground (C)", "small")

    # Regulators.
    top = 508
    s.text(36, top - 16, "B.  Regulators, each behind its own fuse", "head")
    bottom = s.box(36, top, 520, "U5  Pololu D36V50F5  12 V -> 5 V 5.5 A", [
        "12V-BUS -> FH3 (F3 3 A) -> VIN",
        "VOUT -> J12 USB-C plug breakout -> Pi USB-C power",
        "VOUT -> FH6 (F6 2 A) -> slip ring wires 1 and 2 (dome)",
        "VOUT -> U8 PAM8302 amplifier",
        "Load: 0.65 A from 12 V idle, 1.40 A at 5 V worst case",
        "Keep the Pi feed under 250 mm of 16 AWG: 31 mV drop at 3 A",
    ], COLOURS["5v"])
    s.box(576, top, 520, "U6  D36V50F6  12 V -> 6 V 5.5 A  (rail A)", [
        "12V-BUS -> FH4 (F4 5 A) -> VIN",
        "VOUT -> U1 VMOTOR (left foot) and U3 VMOTOR (centre foot)",
        "Four motors, DRV8833 limited to 1 A each: 4 A worst case",
        "24 W at 6 V is 2.2 A from 12 V at 90 percent efficiency",
        "Never feed a DRV8833 from the 12 V bus: 10.8 V maximum",
        "Pololu stock is rationed; order this part early",
    ], COLOURS["6v"])
    s.box(1116, top, 528, "U7  D36V50F6  12 V -> 6 V 5.5 A  (rail B)", [
        "12V-BUS -> FH5 (F5 5 A) -> VIN",
        "VOUT -> U2 VMOTOR (right foot) and U4 VMOTOR (head drive)",
        "Three motors at the 1 A limit: 3 A worst case",
        "18 W at 6 V is 1.7 A from 12 V at 90 percent efficiency",
        "Splitting the rails keeps a stalled foot off the head drive",
        "Both 6 V rails share the star ground, nothing else",
    ], COLOURS["6v"])

    # Star ground and charger polarity.
    mid = bottom + 52
    s.text(36, mid - 20, "C.  Star ground, charger polarity and the battery sense divider",
           "head")
    s.box(36, mid, 520, "TB2  star ground on the electronics tray", [
        "One stud. Every return lands here and nowhere else:",
        "BT1 minus, J1 sleeve, U5/U6/U7 GND, U1-U4 GND, U8 GND,",
        "slip-ring wires 3 and 4, the Pi (through J12) and the KB2040",
        "(through the USB cable J11).",
        "16 AWG for battery and regulator returns, 22 AWG for the rest.",
        "Never daisy-chain a motor return through a logic board.",
    ])
    s.box(576, mid, 520, "G1  charger, PowerStream PST-P2012-A12B", [
        "Bulk 1.5 A, absorb 14.75 V, float 13.75 V, 3 stage.",
        "Plug: 5.5 mm OD x 2.1 mm ID barrel, CENTRE POSITIVE.",
        "J1 centre pin = +12 V, sleeve = ground. Check with a meter",
        "before the first plug-in: a reversed plug blows F2 at once.",
        "Charge 6-7 h from 50 percent. Never below 0 C, never inverted,",
        "never in a sealed box: an SLA vents hydrogen.",
    ], COLOURS["12v"])

    divider_y = mid
    s.parts.append('<rect x="1116" y="{0}" width="528" height="218" rx="7" fill="#ffffff" '
                   'stroke="{1}" stroke-width="1.6"/>'.format(divider_y, RULE))
    s.text(1130, divider_y + 30, "Battery sense divider -> U9 ADS1115", "head")
    s.text(1130, divider_y + 58, "12.7 V pack -> 1.657 V at A0; ratio 7.6667; "
                                 "address 0x48 on Pi I2C-1.", "small")
    node_y = divider_y + 108
    s.text(1136, node_y + 5, "12V-BUS", "net", fill=NET)
    s.line(1226, node_y, 1258, node_y, COLOURS["12v"])
    s.parts.append('<rect x="1258" y="{0}" width="64" height="18" rx="3" fill="#ffffff" '
                   'stroke="{1}" stroke-width="2"/>'.format(node_y - 9, INK))
    s.text(1290, node_y - 16, "R2 100k", "small", anchor="middle")
    s.line(1322, node_y, 1400, node_y, INK)
    s.dot(1400, node_y)
    s.line(1400, node_y, 1490, node_y, COLOURS["signal"])
    s.text(1500, node_y + 5, "U9.A0", "net", fill=NET)
    s.line(1400, node_y, 1400, node_y + 26, INK)
    s.parts.append('<rect x="{0}" y="{1}" width="18" height="52" rx="3" fill="#ffffff" '
                   'stroke="{2}" stroke-width="2"/>'.format(1391, node_y + 26, INK))
    s.text(1420, node_y + 58, "R3 15k", "small")
    s.line(1400, node_y + 78, 1400, node_y + 84, INK)
    s.ground(1400, node_y + 84)

    bottom2 = mid + 244
    s.legend(36, bottom2, 520, [
        (COLOURS["12v"], "12 V, fused and switched (16 AWG red)"),
        (COLOURS["6v"], "6 V motor rails A and B (22 AWG red)"),
        (COLOURS["5v"], "5 V logic, dome and audio rail (16/22 AWG red)"),
        (COLOURS["gnd"], "ground, star connected (16/22 AWG black)"),
        (COLOURS["signal"], "analogue sense"),
    ])
    s.pin_table(576, bottom2, 520, "Fuses, in order from the battery", [
        ("F1  15 A", "main, at the battery lead, holder FH1"),
        ("F2  3 A", "charge port branch, holder FH2"),
        ("F3  3 A", "5 V regulator U5 input, holder FH3"),
        ("F4  5 A", "6 V regulator U6 input, holder FH4"),
        ("F5  5 A", "6 V regulator U7 input, holder FH5"),
        ("F6  2 A", "5 V dome feed to the slip ring, holder FH6"),
    ], left_width=140, accent=COLOURS["12v"])
    s.box(1116, bottom2, 528, "Safety, before the battery goes in", [
        "1. F1 within 100 mm of the battery positive terminal.",
        "2. Short-circuit current of this pack is about 457 A. Fuse",
        "   first, then wire: never test a rail with a bridged fuse.",
        "3. Insulate every F2 blade; a dropped spanner welds itself on.",
        "4. Charge upright, in free air, above 0 C.",
        "5. Meter every rail before any load is connected (sheet 04).",
    ], COLOURS["12v"])
    return s.save("01-power-and-charging.svg", FOOTER)


# ---------------------------------------------------------------------------
# Sheet 02 - motor drive
# ---------------------------------------------------------------------------

def sheet_motors():
    s = Sheet("02  Motor drive: KB2040, four DRV8833 boards, seven TT motors",
              "Pin names are exactly those in firmware/kb2040/code.py. Each motor has ONE "
              "PWM input and ONE plain digital input.",
              1680, 1380)

    rows = []
    for ref, name, driver, channel, pwm_pin, dig_pin, foot, _route in MOTORS:
        rows.append(("{0:<5}".format(pwm_pin),
                     "{0} {1}IN2  PWM  ->  {2} {3}".format(driver, channel, ref, name)))
        rows.append(("{0:<5}".format(dig_pin),
                     "{0} {1}IN1  direction (high = slow decay)".format(driver, channel)))
    rows.append((SLP_PIN, "SLP on all four DRV8833 boards, high = awake"))
    rows.append((PIXEL_PIN, "NeoPixel data out, 17 pixels, to slip ring wire 5"))
    rows.append((INDEX_PIN, "dome index sensor SQ1, active low, internal pull-up"))
    rows.append(("D0", "spare, no connection"))
    rows.append(("SDA/SCL", "STEMMA QT, GPIO12/13, reserved and unused"))
    bottom = s.pin_table(36, 120, 780, "A2  Adafruit KB2040 - every external connection",
                         rows, left_width=110, accent=COLOURS["data"])

    s.box(836, 120, 400, "Power into the KB2040", [
        "USB-C from the Pi (cable J11):",
        "5 V and the USB CDC serial link.",
        "Do NOT also feed RAW from U5.",
        "3V3 pad feeds only SQ1.",
    ], COLOURS["5v"])
    s.box(1256, 120, 388, "Why one PWM pin per motor", [
        "RP2040 GPIO n uses PWM slice",
        "(n >> 1) & 7, channel n & 1, so",
        "GP2/GP18, GP3/GP19, GP4/GP20 and",
        "GP10/GP26 collide. Fourteen PWM",
        "outputs are impossible here.",
        "The seven PWM pins above sit on",
        "seven different slice/channels.",
    ], COLOURS["data"])

    s.box(836, 316, 808, "DRV8833 states reachable with one PWM and one digital pin", [
        "digital low  + duty 0        -> both inputs low   -> coast",
        "digital high + duty FULL*(1-m) -> forward at m    -> slow decay",
        "digital low  + duty FULL*m     -> reverse at m    -> fast decay",
        "digital high + duty FULL       -> both inputs high -> brake",
        "Forward is the slow-decay direction, so wire each motor so that direction",
        "drives the robot forward; if not, swap its two leads at the driver output.",
    ])

    top = max(bottom, 520) + 52
    s.text(36, top - 18, "Driver boards, motor rails and the seven motors", "head")
    columns = [
        ("U1  DRV8833 #1  left foot", "U6 (6 V rail A)",
         [("A", "M1 lf-front", "D3", "D2"), ("B", "M2 lf-rear", "D5", "D4")]),
        ("U2  DRV8833 #2  right foot", "U7 (6 V rail B)",
         [("A", "M3 rf-front", "D7", "D6"), ("B", "M4 rf-rear", "D9", "D8")]),
        ("U3  DRV8833 #3  centre foot", "U6 (6 V rail A)",
         [("A", "M5 cf-front", "D10", "MOSI"), ("B", "M6 cf-rear", "SCK", "MISO")]),
        ("U4  DRV8833 #4  head drive", "U7 (6 V rail B)",
         [("A", "M7 head", "A1", "A0")]),
    ]
    x = 36
    width = 388
    for title, rail, channels in columns:
        lines = ["VMOTOR <- {0}".format(rail), "GND <- TB2 star ground", "SLP <- KB2040 D1"]
        for channel, motor, pwm_pin, dig_pin in channels:
            lines.append("{0}IN1 <- {1} / {0}IN2 <- {2}".format(channel, dig_pin, pwm_pin))
            lines.append("{0}OUT1/{0}OUT2 -> {1}".format(channel, motor))
        if len(channels) == 1:
            lines.append("BIN1/BIN2 tied to ground")
            lines.append("BOUT1/BOUT2 not connected")
        lines.append("Keep both 0.2 ohm sense resistors")
        s.box(x, top, width, title, lines, COLOURS["6v"], style="small")
        x += width + 24

    motor_y = top + 300
    positions = [(140, "M1 lf-front"), (320, "M2 lf-rear"), (552, "M3 rf-front"),
                 (732, "M4 rf-rear"), (964, "M5 cf-front"), (1144, "M6 cf-rear"),
                 (1376, "M7 head")]
    for x_pos, label in positions:
        s.line(x_pos - 26, motor_y - 66, x_pos - 26, motor_y - 18, COLOURS["6v"])
        s.line(x_pos + 26, motor_y - 66, x_pos + 26, motor_y - 18, COLOURS["signal"])
        s.parts.append('<rect x="{0}" y="{1}" width="52" height="20" rx="3" fill="#ffffff" '
                       'stroke="{2}" stroke-width="1.6"/>'.format(x_pos - 26, motor_y - 18, RULE))
        s.text(x_pos, motor_y - 4, "JST-XH", "small", anchor="middle")
        s.line(x_pos, motor_y + 2, x_pos, motor_y + 18, INK)
        s.motor(x_pos, motor_y + 40, label)

    foot = motor_y + 102
    s.box(36, foot, 800, "Motor wiring rules", [
        "Each output pair goes to one JST-XH 2 pin connector (J2-J9) and then to",
        "the motor's own leads.",
        "Every motor lead pair is twisted 22 AWG, yellow = OUT1, blue = OUT2.",
        "Leave the stock 28 AWG motor leads as short as the foot allows: they drop",
        "85 mV over 200 mm at 1 A. Splice to 22 AWG inside the foot shell.",
        "One 100 nF ceramic across each motor's own tabs if brush noise upsets the",
        "NeoPixel chain; it is not needed for the drivers themselves.",
        "Bridge outputs never join each other and never see the 12 V bus.",
    ])
    s.legend(856, foot, 380, [
        (COLOURS["6v"], "6 V motor rail"),
        (COLOURS["data"], "PWM input"),
        (COLOURS["signal"], "direction / SLP input"),
        (COLOURS["gnd"], "ground"),
    ])
    s.box(1256, foot, 388, "Stop behaviour", [
        "KB2040 drops SLP on E 0, on S,",
        "and after 500 ms with no line",
        "from the Pi: every motor coasts.",
        "SLP low is coast, not a brake.",
        "Power off at SW1 is the only",
        "guaranteed disconnect.",
    ], COLOURS["12v"])
    return s.save("02-motor-drive.svg", FOOTER)


# ---------------------------------------------------------------------------
# Sheet 03 - head electronics
# ---------------------------------------------------------------------------

def sheet_head():
    s = Sheet("03  Head electronics: slip ring, PSIs, holoprojectors, logic matrices, radar eye",
              "Twelve slip-ring wires carry everything into the dome. No multiplexer: the four "
              "backpacks use four addresses on Pi I2C-1.",
              1680, 1120)

    rows = [("{0:>2}  {1}".format(number, net), "{0}  <-  {1}".format(purpose, origin))
            for number, net, purpose, colour, origin in SLIP_RING]
    bottom = s.pin_table(36, 120, 760, "SR1  Adafruit 1195 slip ring, 12 wires, 2 A each",
                         rows, left_width=176, accent=COLOURS["5v"])

    s.box(816, 120, 400, "SR1 mechanical", [
        "Body 12.4 mm dia x 19.5 mm, no flange.",
        "Clamped in the printed post on the",
        "body top plate; rotor stub 4 mm.",
        "Stator (body) leads: 6 in / 150 mm.",
        "Rotor (dome) leads: 6 in / 150 mm.",
        "300 RPM maximum; the head drive",
        "turns the dome far slower than that.",
        "Strain-relieve both bundles with a",
        "cable tie within 40 mm of the body.",
    ], COLOURS["note"], style="small")
    s.box(1236, 120, 408, "Current budget in the dome", [
        "17 NeoPixels, worst case white",
        "at 60 mA each: 1.02 A",
        "(firmware caps brightness at 0.4,",
        "so about 0.41 A in practice).",
        "Four HT16K33 backpacks: 0.50 A.",
        "Radar-eye TFT: 0.10 A.",
        "Total worst case 1.62 A on F6 2 A.",
        "Two wires carry 5 V and two carry",
        "the return: 4 A of slip-ring capacity.",
    ], COLOURS["5v"], style="small")

    top = max(bottom, 430) + 54
    s.text(36, top - 20, "A.  NeoPixel chain, one data wire, five devices", "head")
    chain_y = top + 74
    s.text(36, chain_y - 34, "KB2040 A2", "net", fill=NET)
    s.arrow(36, chain_y, 150, chain_y, COLOURS["data"])
    s.parts.append('<rect x="150" y="{0}" width="96" height="42" rx="5" fill="#ffffff" '
                   'stroke="{1}" stroke-width="2"/>'.format(chain_y - 21, COLOURS["5v"]))
    s.text(198, chain_y + 5, "SR1 w5", "net", fill=NET, anchor="middle")
    previous = 246
    devices = [("LED1", "front PSI", "jewel, 7 px, 0-6"), ("LED2", "rear PSI", "jewel, 7 px, 7-13"),
               ("LED3", "HP1", "8 mm, px 14"), ("LED4", "HP2", "8 mm, px 15"),
               ("LED5", "HP3", "8 mm, px 16")]
    for ref, place, detail in devices:
        s.arrow(previous, chain_y, previous + 66, chain_y, COLOURS["data"])
        x = previous + 66
        s.parts.append('<rect x="{0}" y="{1}" width="180" height="62" rx="6" fill="{2}" '
                       'stroke="{3}" stroke-width="1.6"/>'.format(x, chain_y - 31, PANEL, RULE))
        s.text(x + 12, chain_y - 8, "{0}  {1}".format(ref, place), "body")
        s.text(x + 12, chain_y + 16, detail, "small")
        previous = x + 180
    s.text(36, chain_y + 66, "DIN to DOUT in that order. 5 V and ground for every device come "
                             "from the dome 5 V bus (slip-ring wires 1-4), never from the data "
                             "wire's neighbour.", "small", fill=RULE)

    top2 = chain_y + 108
    s.text(36, top2 - 10, "B.  Logic matrices on Pi I2C-1 and the radar-eye TFT on Pi SPI0",
           "head")
    matrix_rows = [("0x{0:02x}  {1}".format(address, ref),
                    "{0}  -  address jumpers: {1}".format(place, jumper))
                   for ref, address, place, jumper in MATRICES]
    s.pin_table(36, top2, 760, "DS1-DS4  Adafruit 0.8 inch 8x8 HT16K33 backpacks",
                matrix_rows, left_width=176, accent=COLOURS["data"])
    s.box(36, top2 + 156, 760, "Matrix wiring", [
        "All four share slip-ring wires 6 (SDA) and 7 (SCL), daisy-chained backpack to",
        "backpack inside the dome, plus 5 V (wire 2) and ground (wire 4).",
        "The HT16K33 has its own 3.3 V-tolerant I2C and runs from 5 V: no level shifter.",
        "Bridge the address pads with solder BEFORE the backpacks go behind the windows.",
        "firmware/pi/displays.py drives 0x70/0x71 as two independent front windows and",
        "0x72/0x73 as one 16 x 8 rear strip that scrolls across the seam.",
    ], COLOURS["data"], style="small")

    s.pin_table(816, top2, 828, "DS5  Adafruit 6178 round TFT (GC9A01A) behind the radar lens", [
        ("VIN", "slip-ring wire 1, dome 5 V bus"),
        ("GND", "slip-ring wire 3, dome ground"),
        ("MOSI", "slip-ring wire 8  <-  Pi GPIO10, header pin 19"),
        ("SCK", "slip-ring wire 9  <-  Pi GPIO11, header pin 23"),
        ("CS", "slip-ring wire 10  <-  Pi GPIO8 (CE0), header pin 24"),
        ("DC", "slip-ring wire 11  <-  Pi GPIO25, header pin 22"),
        ("RST", "slip-ring wire 12  <-  Pi GPIO24, header pin 18"),
        ("LITE", "R1 100 ohm to the dome 5 V bus: always on"),
    ], left_width=128, accent=COLOURS["signal"])
    s.box(816, top2 + 232, 828, "Backlight: tied on, not switched", [
        "There is no thirteenth slip-ring wire, so the backlight is not switched from",
        "the Pi. LITE goes to 5 V through R1 (100 ohm), which sets a steady, slightly",
        "reduced brightness and survives the dome turning. firmware/pi/displays.py still",
        "drives GPIO18 as its backlight pin; with the resistor fitted that pin controls",
        "nothing and can be left unconnected. If a dimmable backlight is wanted later,",
        "give up the dome index sensor wire or move to a 2-wire dome controller.",
    ], COLOURS["note"], style="small")
    return s.save("03-head-electronics.svg", FOOTER)


# ---------------------------------------------------------------------------
# Sheet 04 - Pi, audio and links
# ---------------------------------------------------------------------------

def sheet_pi():
    s = Sheet("04  Raspberry Pi 4: header pins in use, USB link, audio and battery sense",
              "The Pi runs the web server, the head displays, the sounds and the battery "
              "gauge. It never drives a motor directly.",
              1680, 1140)

    rows = [("pin {0:<3} {1}".format(pin, name), note) for pin, name, note in PI_HEADER]
    bottom = s.pin_table(36, 120, 800, "A1  Raspberry Pi 4 Model B, 40 pin header", rows,
                         left_width=240, accent=COLOURS["data"])

    s.box(856, 120, 380, "Power into the Pi", [
        "U5 5 V -> J12 USB-C plug",
        "breakout -> Pi USB-C input.",
        "J12 carries the 5.1 k CC1",
        "resistor that makes the Pi",
        "accept the supply.",
        "16 AWG, under 250 mm.",
        "Do NOT also feed 5 V into",
        "header pins 2 and 4.",
    ], COLOURS["5v"], style="small")
    s.box(1256, 120, 388, "USB link to the KB2040", [
        "Cable J11, USB A to USB C, 1 m.",
        "Carries 5 V for the KB2040 and",
        "the CDC serial link at 115200.",
        "The Pi sees /dev/ttyACM1 once",
        "boot.py has enabled the second",
        "endpoint.",
        "It is also the KB2040's only",
        "power source.",
    ], COLOURS["signal"], style="small")

    top = max(bottom, 430) + 26
    s.text(36, top - 10, "A.  Audio: Pi jack -> summing resistors -> PAM8302 -> 3 inch speaker",
           "head")
    audio_y = top + 86
    s.box(36, top + 26, 250, "A1 3.5 mm jack",
          ["tip = left", "ring = right", "sleeve = ground"], COLOURS["note"], style="small")
    s.line(286, audio_y - 22, 330, audio_y - 22, COLOURS["signal"])
    s.line(286, audio_y + 30, 330, audio_y + 30, COLOURS["signal"])
    for index, (label, offset) in enumerate((("R4A 10k", -22), ("R4B 10k", 30))):
        s.parts.append('<rect x="330" y="{0}" width="70" height="18" rx="3" fill="#ffffff" '
                       'stroke="{1}" stroke-width="2"/>'.format(audio_y + offset - 9, INK))
        s.text(365, audio_y + offset - 15, label, "small", anchor="middle")
        s.line(400, audio_y + offset, 452, audio_y + offset, COLOURS["signal"])
    s.line(452, audio_y - 22, 452, audio_y + 30, COLOURS["signal"])
    s.dot(452, audio_y + 4, COLOURS["signal"])
    s.arrow(452, audio_y + 4, 520, audio_y + 4, COLOURS["signal"])
    s.box(520, top + 26, 320, "U8  PAM8302",
          ["A+ = summed audio", "A- = jack sleeve", "VIN = 5 V rail", "gain pot sets volume"],
          COLOURS["5v"], style="small")
    s.arrow(840, audio_y + 3, 906, audio_y + 3, COLOURS["signal"])
    s.parts.append('<rect x="906" y="{0}" width="230" height="86" rx="6" fill="{1}" '
                   'stroke="{2}" stroke-width="1.6"/>'.format(audio_y - 40, PANEL, RULE))
    s.text(920, audio_y - 14, "LS1  3 inch 4 ohm", "body")
    s.text(920, audio_y + 10, "OUT+ / OUT- only:", "small")
    s.text(920, audio_y + 32, "neither lead to ground", "small")
    s.box(1160, top + 26, 484, "Audio notes", [
        "The PAM8302 output is a bridge. Grounding either speaker lead",
        "destroys the amplifier.",
        "Summing left and right through two 10 k resistors is what makes",
        "a stereo jack drive a mono amp without loading either channel.",
        "Set the trim pot with the dome on: the vent changes the level.",
    ], COLOURS["note"], style="small")

    top2 = top + 216
    s.text(36, top2 - 10, "B.  Battery sense and the first power-on test", "head")
    s.box(36, top2, 800, "U9  ADS1115, address 0x48, on Pi I2C-1", [
        "12V-BUS -> R2 100 k -> A0 node -> R3 15 k -> star ground.",
        "A0 node -> ADS1115 A0. VDD from Pi header pin 1 (3V3), GND pin 6,",
        "SDA pin 3, SCL pin 5 - the same two wires the dome matrices use.",
        "Ratio (100k + 15k) / 15k = 7.6667, so 12.70 V reads 1.657 V and the",
        "14.75 V charge peak reads 1.924 V: inside the 4.096 V full scale.",
        "firmware/pi/battery.py: 12.70 V full, 11.60 V empty, 11.20 V critical.",
        "No KB2040 pin is involved; A0 and A1 there drive the head motor.",
    ], COLOURS["signal"])
    s.box(856, top2, 788, "Rail check with a multimeter, loads disconnected", [
        "1. Fuses out, battery connected, SW1 off: 0 V at the bus, 12.x V at F1 in.",
        "2. F1 in, SW1 on, no other fuse: 12.0-13.0 V across the bus studs.",
        "3. Fit F3 only. U5 VOUT to ground = 5.00 V +/- 0.2 V. Then power off.",
        "4. Fit F4 and F5. U6 and U7 VOUT = 6.0 V +/- 0.25 V each. Power off.",
        "5. Only now plug in J12 (Pi), the driver VMOTOR leads and FH6 (dome).",
        "6. With the Pi running, U9 must read within 0.15 V of the meter at the",
        "   battery terminals; if not, check R2 and R3 before trusting the gauge.",
    ], COLOURS["12v"])

    foot = top2 + 216
    s.legend(36, foot, 420, [
        (COLOURS["5v"], "5 V rail"),
        (COLOURS["signal"], "analogue / SPI / audio"),
        (COLOURS["data"], "I2C and digital"),
        (COLOURS["gnd"], "ground"),
    ])
    s.box(476, foot, 560, "What is NOT wired", [
        "GPIO18 backlight control (R1 ties the backlight on: sheet 03).",
        "The KB2040 STEMMA QT port (GPIO12/13): reserved, unused.",
        "KB2040 RAW: the Pi's USB port is the only 5 V source for it.",
        "Pi header pins 2 and 4: 5 V goes in through the USB-C input only.",
    ], COLOURS["note"], style="small")
    s.box(1056, foot, 588, "Ground rule for the whole robot", [
        "One star point, TB2, on the electronics tray. The Pi, the KB2040,",
        "both 6 V rails, the 5 V rail, the amplifier, the dome return and the",
        "battery minus all land there. Audio ground reaches the amplifier",
        "through the jack sleeve, not through a second path, so the speaker",
        "never shares a return with a motor.",
    ])
    return s.save("04-pi-audio-and-links.svg", FOOTER)


# ---------------------------------------------------------------------------
# Calculations
# ---------------------------------------------------------------------------

def calculations():
    """Rail currents, fuse headroom, ampacity and runtime, from research/loads.md."""
    five_volt_loads = {
        "raspberry_pi_4_A": 0.60,
        "led_matrices_four_A": 0.15,
        "neopixels_average_A": 0.30,
        "radar_tft_A": 0.10,
        "kb2040_A": 0.05,
        "audio_amplifier_average_A": 0.20,
    }
    five_volt_total_A = round(sum(five_volt_loads.values()), 3)
    five_volt_W = round(five_volt_total_A * 5.0, 2)
    efficiency = 0.90
    five_volt_from_12V_A = round(five_volt_W / efficiency / 12.0, 3)

    driving_motor_W = 6 * 0.385 * 6.0 + 0.5 * 3.0
    driving_from_12V_A = round(driving_motor_W / efficiency / 12.0, 3)
    peak_motor_W = 7 * 1.0 * 6.0
    peak_from_12V_A = round(peak_motor_W / efficiency / 12.0 + five_volt_from_12V_A, 3)

    usable_Ah = 6.7 * 0.5
    profiles = {
        "idle_displays_on": {"amps_12V": five_volt_from_12V_A},
        "continuous_driving": {"amps_12V": round(five_volt_from_12V_A + driving_from_12V_A, 3)},
        "mixed_50_percent_driving": {
            "amps_12V": round(five_volt_from_12V_A + driving_from_12V_A / 2.0, 3)},
        "worst_case_all_seven_motors_at_the_1A_limit": {"amps_12V": peak_from_12V_A},
    }
    for profile in profiles.values():
        profile["runtime_h_to_50_percent_DoD"] = round(usable_Ah / profile["amps_12V"], 2)

    fuses = [
        {"designator": "F1", "circuit": "main, battery positive lead", "rating_A": 15,
         "measured_or_estimated_load_A": peak_from_12V_A,
         "loads_md_minimum_A": 7.5,
         "note": "Sized for the 20 A switch and the 16 AWG lead rather than for the load; "
                 "loads.md section 6 would allow 7.5 A. The larger fuse still protects the "
                 "16 AWG (22 A chassis) cable."},
        {"designator": "F2", "circuit": "charge port branch to the battery side of SW1",
         "rating_A": 3, "measured_or_estimated_load_A": 1.5, "loads_md_minimum_A": 2,
         "note": "Charger G1 delivers 1.5 A maximum."},
        {"designator": "F3", "circuit": "5 V regulator U5 input", "rating_A": 3,
         "measured_or_estimated_load_A": five_volt_from_12V_A, "loads_md_minimum_A": 2,
         "note": "0.65 A idle, 1.4 A if every 5 V load peaks together."},
        {"designator": "F4", "circuit": "6 V regulator U6 input (left and centre feet)",
         "rating_A": 5, "measured_or_estimated_load_A": round(4 * 6.0 / efficiency / 12.0, 3),
         "loads_md_minimum_A": 5, "note": "Four motors at the DRV8833 1 A limit."},
        {"designator": "F5", "circuit": "6 V regulator U7 input (right foot and head)",
         "rating_A": 5, "measured_or_estimated_load_A": round(3 * 6.0 / efficiency / 12.0, 3),
         "loads_md_minimum_A": 5, "note": "Three motors at the 1 A limit."},
        {"designator": "F6", "circuit": "5 V dome feed through the slip ring", "rating_A": 2,
         "measured_or_estimated_load_A": 1.62, "loads_md_minimum_A": 1.5,
         "note": "17 NeoPixels at 60 mA (1.02 A) plus four backpacks (0.50 A) plus the TFT "
                 "(0.10 A). loads.md proposed a 1.5 A polyfuse, which the worst case exceeds; "
                 "a 2 A blade fuse is used instead."},
    ]

    ampacity = [
        {"gauge_awg": 16, "chassis_rating_A": 22, "used_for":
         "battery, main fuse, switch, charge branch, regulator inputs, Pi 5 V feed",
         "worst_case_A": peak_from_12V_A, "verdict": "pass"},
        {"gauge_awg": 22, "chassis_rating_A": 7, "used_for":
         "6 V branches, motor extensions, dome feed, display and NeoPixel signals",
         "worst_case_A": 4.0, "verdict": "pass"},
        {"gauge_awg": 28, "chassis_rating_A": 1.4, "used_for":
         "the motors' own factory leads and the slip-ring leads",
         "worst_case_A": 1.0, "verdict":
         "pass at the DRV8833 1 A limit; keep these leads short (85 mV drop over 200 mm)"},
    ]

    return {
        "status": "engineering calculation from research/loads.md section 6 and "
                  "research/components-electronics.md; no measurement on hardware",
        "date": "2026-09-12",
        "battery": {
            "part": "Power-Sonic PS-1270 F2", "nominal_V": 12.0, "capacity_Ah_20h": 7.0,
            "capacity_Ah_10h": 6.7, "usable_Ah_at_50_percent_DoD": usable_Ah,
            "short_circuit_current_A_estimated": 457,
            "datasheet_5s_rating_A": 108,
            "cycle_charge_V": [14.1, 14.7], "float_V": [13.5, 13.8],
            "maximum_charge_current_A": 2.16,
        },
        "charging": {
            "charger": "PowerStream PST-P2012-A12B", "bulk_A": 1.5, "absorb_V": 14.75,
            "float_V": 13.75,
            "bulk_hours_from_50_percent": round(usable_Ah / 1.5 / 0.85, 2),
            "total_hours_to_float": "6 to 7",
            "note": "loads.md quotes about 6 h with a 1 A charger; the 1.5 A charger reaches "
                    "float sooner but absorption still dominates the tail.",
        },
        "rails": {
            "five_volt_loads_A": five_volt_loads,
            "five_volt_total_A": five_volt_total_A,
            "five_volt_total_W": five_volt_W,
            "converter_efficiency": efficiency,
            "five_volt_draw_from_12V_A": five_volt_from_12V_A,
            "driving_motor_W": round(driving_motor_W, 2),
            "driving_draw_from_12V_A": driving_from_12V_A,
            "worst_case_motor_W": peak_motor_W,
            "worst_case_draw_from_12V_A": peak_from_12V_A,
            "six_volt_rail_A_headroom": {
                "U6_load_A": 4.0, "U7_load_A": 3.0, "regulator_rating_A": 5.5},
        },
        "fuses": fuses,
        "wire_ampacity": ampacity,
        "slip_ring": {
            "wires": 12, "rating_A_per_wire": 2.0,
            "five_volt_wires": 2, "ground_wires": 2,
            "five_volt_capacity_A": 4.0,
            "dome_worst_case_A": 1.62,
            "dome_practical_A_at_firmware_brightness_0p4": 1.01,
        },
        "runtime": profiles,
        "notes": [
            "Motor currents come from loads.md section 2: 0.385 A per drive motor at 6 V on "
            "a hard floor, and 0.5 A at 3 V for the head drive.",
            "The DRV8833 sense resistors chop each motor at 1 A, so a stall is a limit, "
            "not a fault current.",
            "Runtime is to 50 percent depth of discharge, which is the figure that keeps an "
            "SLA's cycle life; running to 11.2 V gives more time and fewer cycles.",
            "Every figure here is arithmetic on published ratings. Nothing has been measured "
            "on a built robot.",
        ],
    }


def main():
    build_harness()
    with (HERE / "wiring.csv").open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(ROWS[0]))
        writer.writeheader()
        writer.writerows(ROWS)
    (HERE / "calculations.json").write_text(
        json.dumps(calculations(), indent=2) + "\n", encoding="utf-8")
    sheets = [sheet_power(), sheet_motors(), sheet_head(), sheet_pi()]
    if OVERFLOW:
        raise SystemExit("text would overflow its box:\n  " + "\n  ".join(OVERFLOW))
    print("wiring.csv: {0} wires".format(len(ROWS)))
    print("calculations.json written")
    for name in sheets:
        print("{0} written".format(name))


if __name__ == "__main__":
    main()
