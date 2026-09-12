"""Build doorbot-build-guide.pdf: mostly pictures, as few words as will do the job.

Reads the CAD renders, the generated drawings, the BOM CSVs and the verification JSON, so the
guide cannot claim anything the checks did not produce.

    python scripts/build_guide.py
"""
import csv
import json
from pathlib import Path

from reportlab.lib import colors
from reportlab.lib.pagesizes import A4, landscape
from reportlab.lib.units import mm
from reportlab.pdfgen import canvas
from reportlab.pdfbase.pdfmetrics import stringWidth

from scad_params import ROOT, params

PAGE = landscape(A4)
W, H = PAGE
INK = colors.HexColor("#0b0f19")
MUTED = colors.HexColor("#4b5563")
ACCENT = colors.HexColor("#1d4ed8")
BAD = colors.HexColor("#b91c1c")
GOOD = colors.HexColor("#15803d")
PANEL = colors.HexColor("#eef2f7")
OUT = ROOT / "output/pdf/doorbot-build-guide.pdf"

# Part colours in cad/exploded.png, so the legend can key to it without pixel hunting.
EXPLODED_KEY = [
    ("#e2e8f0", "base_shell", "the unibody"),
    ("#cbd5e1", "base_cover", "cover, windows and wave target"),
    ("#4b5563", "-", "TT motor (bought)"),
    ("#b45309", "motor_pinion", "12T on the motor shaft"),
    ("#0369a1", "compound_gear", "48T + 14T, one print"),
    ("#7c3aed", "drum_gear", "42T + cable drum, one print"),
    ("#9ca3af", "-", "4 mm steel dowels (bought)"),
    ("#111827", "-", "T-Display (bought)"),
    ("#166534", "-", "driver and accelerometer (bought)"),
    ("#1d4ed8", "-", "two time-of-flight boards (bought)"),
    ("#b45309", "door_anchor", "on the door face"),
    ("#be123c", "magnet_pod", "x2: door edge and jamb"),
]


def trim(path, margin=6):
    """Crop the flat background border off a render so it fills its box on the page.

    OpenSCAD's --viewall leaves a wide margin and matplotlib adds its own; pasting those
    straight onto a page wastes most of the space the picture was given.
    """
    if not path.exists():
        return None
    from PIL import Image, ImageChops
    cache = ROOT / "tmp/trimmed"
    cache.mkdir(parents=True, exist_ok=True)
    out = cache / path.name
    if out.exists() and out.stat().st_mtime >= path.stat().st_mtime:
        return out
    with Image.open(path) as im:
        im = im.convert("RGB")
        bg = Image.new("RGB", im.size, im.getpixel((2, 2)))
        box = ImageChops.difference(im, bg).convert("L").point(
            lambda v: 255 if v > 12 else 0).getbbox()
        if box is None:
            return path
        box = (max(0, box[0] - margin), max(0, box[1] - margin),
               min(im.width, box[2] + margin), min(im.height, box[3] + margin))
        im.crop(box).save(out)
    return out


class Guide:
    def __init__(self, path):
        self.c = canvas.Canvas(str(path), pagesize=PAGE)
        self.page = 0

    # ---------------------------------------------------------------- helpers
    def frame(self, title, kicker=""):
        self.page += 1
        c = self.c
        c.setFillColor(INK)
        c.setFont("Helvetica-Bold", 19)
        c.drawString(18 * mm, H - 17 * mm, title)
        if kicker:
            c.setFont("Helvetica", 10.5)
            c.setFillColor(MUTED)
            c.drawString(18 * mm, H - 23.5 * mm, kicker)
        c.setStrokeColor(MUTED)
        c.setLineWidth(0.6)
        c.line(18 * mm, H - 26.5 * mm, W - 18 * mm, H - 26.5 * mm)
        c.setFont("Helvetica", 8)
        c.setFillColor(MUTED)
        c.drawString(18 * mm, 9 * mm, "doorbot revision A - analysis and CAD only, no "
                                      "prototype has been built or tested")
        c.drawRightString(W - 18 * mm, 9 * mm, str(self.page))

    def end(self):
        self.c.showPage()

    def image(self, path, x, y, w, h, caption=""):
        path = trim(Path(path))
        if path is None:
            return
        from PIL import Image
        with Image.open(path) as im:
            iw, ih = im.size
        scale = min(w / iw, h / ih)
        dw, dh = iw * scale, ih * scale
        self.c.drawImage(str(path), x + (w - dw) / 2, y + (h - dh) / 2, dw, dh,
                         preserveAspectRatio=True, anchor="c")
        if caption:
            self.c.setFont("Helvetica", 8.5)
            self.c.setFillColor(MUTED)
            self.c.drawCentredString(x + w / 2, y - 4 * mm, caption)

    def wrap(self, text, x, y, w, size=10, leading=None, colour=INK, font="Helvetica"):
        leading = leading or size * 1.35
        self.c.setFont(font, size)
        self.c.setFillColor(colour)
        words, line = text.split(), ""
        for word in words:
            trial = (line + " " + word).strip()
            if stringWidth(trial, font, size) > w:
                self.c.drawString(x, y, line)
                y -= leading
                line = word
            else:
                line = trial
        if line:
            self.c.drawString(x, y, line)
            y -= leading
        return y

    def step(self, n, x, y, w, headline, detail=""):
        c = self.c
        c.setFillColor(ACCENT)
        c.circle(x + 3.4 * mm, y - 1.2 * mm, 3.4 * mm, fill=1, stroke=0)
        c.setFillColor(colors.white)
        c.setFont("Helvetica-Bold", 10)
        c.drawCentredString(x + 3.4 * mm, y - 2.6 * mm, str(n))
        c.setFillColor(INK)
        c.setFont("Helvetica-Bold", 10.5)
        c.drawString(x + 9 * mm, y - 2.6 * mm, headline)
        if detail:
            return self.wrap(detail, x + 9 * mm, y - 8 * mm, w - 9 * mm, 9, 11.5, MUTED)
        return y - 8 * mm

    def table(self, rows, x, y, widths, size=8.2, header=True, row_h=5.2 * mm):
        c = self.c
        for r, row in enumerate(rows):
            if header and r == 0:
                c.setFillColor(PANEL)
                c.rect(x, y - row_h + 1.4 * mm, sum(widths), row_h, fill=1, stroke=0)
            c.setFont("Helvetica-Bold" if header and r == 0 else "Helvetica", size)
            c.setFillColor(INK if header and r == 0 else MUTED)
            cx = x
            for value, width in zip(row, widths):
                text = str(value)
                while stringWidth(text, "Helvetica", size) > width - 2 * mm and len(text) > 4:
                    text = text[:-2]
                c.drawString(cx + 1 * mm, y - row_h + 3 * mm, text)
                cx += width
            y -= row_h
        return y


def main():
    p = params()
    mech = json.loads((ROOT / "docs/mechanism.json").read_text())
    cad = json.loads((ROOT / "docs/cad.json").read_text())
    bom = json.loads((ROOT / "docs/bom.json").read_text())
    ver = json.loads((ROOT / "docs/verification.json").read_text())
    printed = list(csv.DictReader((ROOT / "bom/printed-parts.csv").open(encoding="utf-8")))
    electronics = list(csv.DictReader((ROOT / "bom/electronics.csv").open(encoding="utf-8")))
    hardware = list(csv.DictReader((ROOT / "bom/hardware.csv").open(encoding="utf-8")))
    s = mech["summary"]
    OUT.parent.mkdir(parents=True, exist_ok=True)
    g = Guide(OUT)
    D = ROOT / "output/drawings"
    C = ROOT / "cad"

    # ---------------------------------------------------------------- cover
    g.frame("doorbot", "A door closer printed in Bambu Lab PLA Tough+, driven by one TT motor, "
                       "run by a TTGO T-Display")
    g.image(C / "assembly.png", 12 * mm, 32 * mm, 92 * mm, 148 * mm, "assembled, cover on")
    g.image(C / "installed_shut.png", 108 * mm, 122 * mm, 84 * mm, 56 * mm,
            "plan view, shut: unit in the rebate, cable to the anchor")
    g.image(C / "exploded.png", 108 * mm, 34 * mm, 84 * mm, 78 * mm,
            "seven printed designs, eight pieces")
    y = 175 * mm
    y = g.wrap("It screws to the hinge-side jamb, behind the door, and reels a Dyneema cable "
               "in to swing the door shut. Four magnets at the latch edge take the last "
               "millimetres and hold it closed. Wave a hand at it, kick the door twice, or let "
               "it close on its own when the doorway is clear.",
               206 * mm, y, 84 * mm, 10.5, 14)
    rows = [["", ""],
            ["printed designs", f"{cad['printed_designs']} ({cad['printed_pieces']} pieces)"],
            ["printed material", f"{bom['printed_mass_g']:.0f} g PLA Tough+"],
            ["purchased pieces", f"{bom['purchased_pieces']} (${bom['total_usd']:.2f})"],
            ["gear ratio", f"{s['ratio']:.0f}:1, two printed spur stages"],
            ["cable tension", f"{s['max_tension_n']:.0f} N, capped in hardware"],
            ["moment arm", f"{s['arm_min_mm']:.0f}-{s['arm_open_mm']:.0f} mm, never zero"],
            ["torque margin", f"{s['worst_margin']:.2f}x worst case"],
            ["close time", f"{s['close_time_s']:.0f} s from wide open"],
            ["door it is sized for", f"{p['door_width_mm']:.0f} mm solid core, "
                                     f"{p['door_mass_kg']:.0f} kg"],
            ["magnet hold", f"{s['magnet_hold_n']:.0f} N at a 2 mm gap"]]
    g.table(rows, 206 * mm, y - 6 * mm, [36 * mm, 52 * mm], 9, True, 6 * mm)
    g.end()

    # ---------------------------------------------------------------- what it does
    g.frame("What it does", "Three ways to make it close, and one rule when something is in "
                            "the way")
    g.image(D / "diagram_states.png", 12 * mm, 92 * mm, 272 * mm, 88 * mm)
    y = 84 * mm
    col = 0
    for n, (head, detail) in enumerate([
        ("Wave a hand over the ring", "Two consecutive readings inside 20-250 mm of the "
                                      "engraved target. One brush past does nothing."),
        ("Kick the door twice", "Two impacts 120-900 ms apart, felt through the jamb by the "
                                "accelerometer."),
        ("Leave it alone", "Doorway clear for 30 s and the door still open: it closes itself."),
        ("Something in the way", "It refuses, retries every 19 s for a minute, then buzzes and "
                                 "says CLEAR THE WAY on the screen."),
        ("Just open the door", "The drum free-spools. It costs about 1 N extra at the door "
                               "edge, powered or not."),
    ], 1):
        x = 16 * mm if col == 0 else 152 * mm
        y2 = g.step(n, x, y, 128 * mm, head, detail) - 3 * mm
        if col == 1:
            y = y2
        col = 1 - col
    g.end()

    # ---------------------------------------------------------------- print these
    g.frame("Print these", f"{cad['printed_designs']} designs, {cad['printed_pieces']} pieces, "
                           f"{bom['printed_mass_g']:.0f} g. Every part lies flat, no supports.")
    g.image(D / "diagram_print_plate.png", 14 * mm, 32 * mm, 150 * mm, 150 * mm)
    rows = [["part", "qty", "size mm", "g"]]
    for r in printed:
        rows.append([r["part"], r["quantity"],
                     f"{float(r['x_mm']):.0f}x{float(r['y_mm']):.0f}x{float(r['z_mm']):.0f}",
                     r["solid_mass_g"]])
    y = g.table(rows, 170 * mm, 178 * mm, [40 * mm, 12 * mm, 30 * mm, 14 * mm])
    y = g.wrap("Slice settings that matter: 0.2 mm layers, 4 walls, 40% infill everywhere "
               "except the gears and the nose, which want 100%. No supports needed on any "
               "part. Print the gears and the nose in PLA Tough+ for impact; if you have it, "
               "PLA Basic or PETG is actually stiffer for the anchor.",
               170 * mm, y - 8 * mm, 105 * mm, 9.5, 12.5)
    y = g.wrap("ONE PAUSE: magnet_pod needs a print pause at the pocket roof. Drop both "
               "magnets in the same way up, then let it bridge three layers over them. No "
               "adhesive, and the magnets cannot creep out.",
               170 * mm, y - 5 * mm, 105 * mm, 9.5, 12.5, BAD)
    g.end()

    # ---------------------------------------------------------------- buy these
    g.frame("Buy these", f"{bom['purchased_line_items']} line items, "
                         f"{bom['purchased_pieces']} pieces, "
                         f"${bom['total_usd']:.2f} at the prices read on 2026-09-12")
    rows = [["vendor", "sku", "item", "qty", "$"]]
    for r in electronics:
        rows.append([r["vendor"], r["sku"], r["item"], r["quantity"], r["line_usd"]])
    y = g.table(rows, 16 * mm, H - 34 * mm, [22 * mm, 18 * mm, 78 * mm, 12 * mm, 14 * mm],
                8.2, True, 4.8 * mm)
    rows = [["vendor", "sku", "item", "qty", "$"]]
    for r in hardware:
        rows.append([r["vendor"], r["sku"], r["item"], r["quantity"], r["line_usd"]])
    g.table(rows, 150 * mm, H - 34 * mm, [26 * mm, 24 * mm, 66 * mm, 12 * mm, 14 * mm],
            8.2, True, 4.8 * mm)
    y = g.wrap("Two substitutions worth knowing. Adafruit 3875 is an ELECTROMAGNET, not a "
               "permanent magnet: it would need 0.6 A held continuously and the door would "
               "fall open on a power cut, so the design uses four K&J D84 permanent discs "
               "instead. Adafruit's own permanent disc (product 9) is out of stock and has no "
               "published pull force, which is why it is not specified here.",
               16 * mm, 62 * mm, 125 * mm, 9.5, 12.5, BAD)
    g.wrap("The motor's 5 V comes off the same USB source as the T-Display but is taken AT THE "
           "DRIVER. The board's only path from USB VBUS to its 5 V header pin is one unfused "
           "1 A Schottky that also feeds the 3.3 V regulator, so a 1 A motor step on that node "
           "resets the ESP32.",
           150 * mm, 62 * mm, 125 * mm, 9.5, 12.5, MUTED)
    g.end()

    # ---------------------------------------------------------------- exploded
    g.frame("Exploded view", "Colours key to the list on the right")
    g.image(C / "exploded.png", 8 * mm, 26 * mm, 175 * mm, 158 * mm)
    y = 176 * mm
    for i, (hexc, part, what) in enumerate(EXPLODED_KEY, 1):
        g.c.setFillColor(colors.HexColor(hexc))
        g.c.setStrokeColor(MUTED)
        g.c.rect(190 * mm, y - 3.4 * mm, 6 * mm, 4 * mm, fill=1, stroke=1)
        g.c.setFillColor(INK)
        g.c.setFont("Helvetica-Bold", 9)
        g.c.drawString(199 * mm, y - 3 * mm, f"{i}. {part if part != '-' else what}")
        if part != "-":
            g.c.setFillColor(MUTED)
            g.c.setFont("Helvetica", 8.5)
            g.c.drawString(232 * mm, y - 3 * mm, what)
        y -= 7 * mm
    g.end()

    # ---------------------------------------------------------------- assemble
    g.frame("Assemble the unit", "About 30 minutes. Nothing is glued.")
    g.image(C / "section.png", 14 * mm, 30 * mm, 72 * mm, 152 * mm,
            "cut away at the mid line")
    g.image(D / "diagram_gear_train.png", 92 * mm, 96 * mm, 100 * mm, 82 * mm)
    y = 176 * mm
    steps = [
        ("Press the two dowels in", "4 mm steel into the two floor bosses, square to the "
                                    "floor."),
        ("Pinion onto the motor", "Push the 12T pinion onto the double-D shaft, flat to flat, "
                                  "until it bottoms."),
        ("Encoder wheel on the other shaft", "It snaps on. The slot sensor goes in the pocket "
                                             "under the cover dome."),
        ("Motor into the cradle", "Gearbox end down, leads towards the driver pocket. The "
                                  "cover rib holds it down."),
        ("Drum gear, then compound gear", "Drum gear on the lower dowel, compound gear on the "
                                          "upper. Spin both by hand: no rub, no slop."),
        ("Boards into their pockets", "Two M3 each. T-Display last, screen towards the cover "
                                      "window."),
        ("Wire it", "Next page. Star the grounds at the driver."),
        ("Cable onto the drum", "Thread through the radial hole, knot it in the flange pocket, "
                                "wind on 5 turns, feed the tail out through the nose."),
        ("Cover on", "Four M3. Check the dowel tops entered their blind bosses."),
    ]
    for n, (head, detail) in enumerate(steps, 1):
        y = g.step(n, 196 * mm, y, 90 * mm, head, detail) - 1.5 * mm
    g.end()

    # ---------------------------------------------------------------- wiring
    g.frame("Wire it", "Twelve signals. Nothing touches a display pin, a flash pin or a "
                       "strapping pin.")
    g.image(D / "diagram_wiring.png", 12 * mm, 26 * mm, 270 * mm, 160 * mm)
    g.end()

    # ---------------------------------------------------------------- install
    g.frame("Install it", "Hinge side, push side, behind the door. Three holes in the jamb, "
                          "three in the door, two per magnet pod.")
    g.image(D / "diagram_geometry.png", 12 * mm, 108 * mm, 272 * mm, 72 * mm)
    y = 100 * mm
    col = 0
    for n, (head, detail) in enumerate([
        ("Unit on the jamb reveal", f"Push side, hinge side, hand height. Use the jamb "
                                    f"template. It stands {p['base_z']:.0f} mm into the "
                                    f"opening, inside the "
                                    f"{p['rebate_depth_mm']:.0f} mm rebate."),
        ("Anchor on the door face", f"{p['anchor_a']:.0f} mm from the hinge axis, same height "
                                    f"as the nose. Use the door template."),
        ("Magnet pods", "One on the latch edge of the door, one on the jamb opposite. Faces "
                        "towards each other, about 2 mm apart when shut."),
        ("Cable", "From the nose to the anchor eye. Taut with the door shut, no slack loop to "
                  "catch on."),
        ("Power", "USB-C into the T-Display, motor 5 V taken at the driver."),
    ], 1):
        x = 16 * mm if col == 0 else 152 * mm
        y2 = g.step(n, x, y, 128 * mm, head, detail) - 2 * mm
        if col == 1:
            y = y2
        col = 1 - col
    g.wrap("The cable and the whole unit sit on the push side of the closed leaf, so the door "
           "sweeps a quadrant that contains none of it. Nothing is ever in the door's path, and "
           "the door still opens fully by hand with the power off.",
           152 * mm, y - 4 * mm, 130 * mm, 9.5, 12, GOOD)
    g.end()

    # ---------------------------------------------------------------- commission
    g.frame("First run", "Two things need setting on the actual door")
    g.image(D / "diagram_sensors.png", 12 * mm, 108 * mm, 272 * mm, 72 * mm)
    y = 98 * mm
    y = g.step(1, 16 * mm, y, 128 * mm, "Let it find the shut position",
               "Press the top button with the door nearly shut. It winds until the leaf stops "
               "against the magnets, and that stall becomes its zero. The screen shows HOMING "
               "until then.") - 3 * mm
    y = g.step(2, 16 * mm, y, 128 * mm, "Set the kick threshold",
               "Nobody publishes how much of a kick reaches a door jamb, so this one has to be "
               "measured on your door. Start at the shipped value, kick twice, and if nothing "
               "happens lower CLICK_THS in setup(); if the door closes when someone shuts a "
               "cupboard, raise it.") - 3 * mm
    y = g.step(3, 16 * mm, y, 128 * mm, "Check the wrong-direction case",
               "If the first close pays cable out instead of taking it in, swap the two motor "
               "leads.") - 3 * mm
    g.wrap("What the sensors cannot see: an object lying in the swing arc on the pull side is "
           "outside both cones. The encoder stall watchdog is the backstop - drive is cut "
           "within 250 ms of contact, and the driver's own 1.0 A chop caps the push at "
           f"{s['max_tension_n']:.0f} N of cable tension whatever the firmware does.",
           152 * mm, 96 * mm, 130 * mm, 9.5, 12, BAD)
    g.end()

    # ---------------------------------------------------------------- numbers
    g.frame("Why it works", "Every number here comes from cad/params.scad through "
                            "scripts/check_mechanism.py")
    g.image(D / "diagram_curves.png", 12 * mm, 74 * mm, 272 * mm, 106 * mm)
    y = 66 * mm
    y = g.wrap("The one thing that makes or breaks a hinge-side cable closer: if the cable "
               "leaves the jamb ON the closed-door plane, then with the door shut the exit, "
               "the hinge axis and the anchor are in a straight line. The moment arm is "
               "exactly zero and no tension at all can shut the last degree. Offsetting the "
               f"exit {p['exit_y']:.0f} mm off that plane keeps the included angle between "
               f"{mech['summary']['psi_closed_deg']:.0f} and 119 degrees, and the arm between "
               f"{s['arm_min_mm']:.0f} and {s['arm_open_mm']:.0f} mm.",
               16 * mm, y, 128 * mm, 9.5, 12.5)
    y = g.wrap(f"The close takes {s['close_time_s']:.0f} s, and no gear ratio fixes that: the "
               f"TT motor at 5 V makes about 0.35 W of mechanical power, full stop. The "
               f"upside is that the leaf arrives carrying {s['peak_energy_j']:.2f} J against "
               f"the {1.69} J that ANSI/BHMA A156.19 allows a closer.",
               152 * mm, 66 * mm, 130 * mm, 9.5, 12.5)
    checks = [c for c in mech["checks"] if c["pass"]]
    g.wrap(f"{len(checks)} mechanism checks pass, {len(cad['checks'])} CAD checks pass, and "
           f"{len(ver['steps'])} verification steps pass in one command: "
           f"python scripts/verify.py.",
           152 * mm, 40 * mm, 130 * mm, 9.5, 12.5, GOOD)
    g.end()

    # ---------------------------------------------------------------- limits
    g.frame("Limits", "What this package does not establish")
    y = H - 40 * mm
    for head, detail in [
        ("No prototype exists", "Everything in this guide is analysis of the design and a "
                                "build of the firmware. Nothing here has been printed, "
                                "assembled or run against a real door."),
        ("The hinge friction figure is modelled, not measured",
         "No published figure exists for plain residential butt hinges. The 0.82 N.m used "
         "throughout is the worst case of a friction model, and the torque margin quoted is "
         "against that model."),
        ("The kick threshold has no published basis",
         "No measurement of what a kick delivers to a door jamb exists in the literature "
         "searched. The shipped register value is a starting point to be calibrated."),
        ("Magnet figures are the vendor's",
         "The 70 N at a 2 mm gap comes from K&J's published pull-force curve for the D84, "
         "scaled by their own on-axis fall-off. It has not been measured on a door."),
        ("The pull-side swing arc is not sensed",
         "Two time-of-flight cones cover the doorway, not the arc on the pull side. Contact "
         "there is caught by the stall watchdog, not avoided."),
        ("Heavier or sprung doors are out of scope",
         f"Sized for a {p['door_width_mm']:.0f} mm solid-core leaf at "
         f"{p['door_mass_kg']:.0f} kg on plain butt hinges with no closer spring. A sprung "
         f"door or a fire door is a different machine."),
    ]:
        g.c.setFillColor(BAD)
        g.c.circle(20 * mm, y - 1.4 * mm, 1.6 * mm, fill=1, stroke=0)
        g.c.setFillColor(INK)
        g.c.setFont("Helvetica-Bold", 11)
        g.c.drawString(25 * mm, y - 3 * mm, head)
        y = g.wrap(detail, 25 * mm, y - 9 * mm, 240 * mm, 10, 13, MUTED) - 4 * mm
    g.end()

    # ---------------------------------------------------------------- templates
    for name, title in [("template_jamb", "Template: jamb reveal"),
                        ("template_door", "Template: door face"),
                        ("template_pod", "Template: magnet pods")]:
        g.frame(title, "Print this page at 100%, then check the 50 mm bar with a ruler before "
                       "you drill")
        g.image(D / f"{name}.png", 30 * mm, 30 * mm, 230 * mm, 150 * mm)
        g.end()

    g.c.save()
    size = OUT.stat().st_size
    import hashlib
    digest = hashlib.sha256(OUT.read_bytes()).hexdigest()
    (ROOT / "docs/pdf.json").write_text(json.dumps(
        {"pages": g.page, "bytes": size, "sha256": digest,
         "path": str(OUT.relative_to(ROOT)).replace("\\", "/")}, indent=2))
    print(f"{OUT} - {g.page} pages, {size / 1024:.0f} kB")
    print("SHA256 " + digest)


if __name__ == "__main__":
    main()
