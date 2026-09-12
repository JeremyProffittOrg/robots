"""Build the doorbot bill of materials and count what actually has to be bought.

Writes bom/electronics.csv, bom/hardware.csv, bom/printed-parts.csv and docs/bom.json.
Prices are the vendor list prices read during research on 2026-09-12 and are recorded so the
total is traceable, not so it is guaranteed.

    python scripts/bom.py
"""
import csv
import json

import trimesh

from scad_params import ROOT, params

DENSITY_G_CM3 = 1.24     # Bambu Lab PLA Tough+ published density

# vendor, sku, name, qty, unit price USD, why it is here, source url
ELECTRONICS = [
    ("Adafruit", "3777", "DC gearbox 'TT' motor, 1:48, 3-6 V", 1, 2.50,
     "the single drive motor; 65.4 mN.m stall and 207 RPM at 5 V",
     "https://www.adafruit.com/product/3777"),
    ("Adafruit", "3297", "DRV8833 DC motor driver breakout", 1, 5.95,
     "3.3 V logic direct, 2.7 V motor floor, and a 1.0 A hardware current chop that caps "
     "cable tension at 151 N with no firmware in the loop",
     "https://www.adafruit.com/product/3297"),
    ("Adafruit", "5396", "VL53L4CD time-of-flight distance sensor", 1, 14.95,
     "hand-wave target; the only VL53 board published down to 1 mm, and the narrowest cone "
     "at 18 deg so a passer-by stays out of it",
     "https://www.adafruit.com/product/5396"),
    ("Adafruit", "3967", "VL53L1X time-of-flight distance sensor", 1, 14.95,
     "doorway and closing path; 4 m range and the widest published cone at 27 deg, with a "
     "programmable region of interest to trim it to the opening",
     "https://www.adafruit.com/product/3967"),
    ("Adafruit", "2809", "LIS3DH triple-axis accelerometer", 1, 4.95,
     "kick detection; the only candidate with both an on-chip click engine and a high-pass "
     "filter in front of it, so the threshold is spent on the impulse and not on gravity",
     "https://www.adafruit.com/product/2809"),
    ("LilyGO", "T-Display", "TTGO T-Display ESP32, 1.14 in ST7789 135x240", 1, 15.00,
     "the brain and the screen, powered by USB-C at 5 V",
     "https://github.com/Xinyuan-LilyGO/TTGO-T-Display"),
    ("Adafruit", "3782", "TT motor encoder wheel, 20 slots", 1, 0.95,
     "snaps onto the motor's free shaft; gives the stall watchdog a 250 ms verdict and the "
     "controller its cable position",
     "https://www.adafruit.com/product/3782"),
    ("Adafruit", "3986", "T-slot photo interrupter", 1, 2.95,
     "reads the encoder wheel", "https://www.adafruit.com/product/3986"),
    ("Adafruit", "1536", "Piezo buzzer, 12 mm", 1, 0.95,
     "the alert at the end of the retry window",
     "https://www.adafruit.com/product/1536"),
    ("Adafruit", "4399", "STEMMA QT / Qwiic JST SH 4-pin cable, 100 mm", 3, 0.95,
     "I2C daisy chain between the two time-of-flight boards and the accelerometer",
     "https://www.adafruit.com/product/4399"),
    ("Adafruit", "3564", "Silicone hook-up wire, 26 AWG, spool", 1, 4.95,
     "motor, driver, buzzer and encoder wiring", "https://www.adafruit.com/product/3564"),
    ("Adafruit", "4298", "USB-C cable, 1 m", 1, 3.95,
     "the 5 V supply into the T-Display", "https://www.adafruit.com/product/4298"),
    ("Adafruit", "753", "100 uF 16 V electrolytic capacitor", 1, 0.95,
     "across the driver's motor supply; TI's minimum is 10 uF and a 1.0 A chop on a shared "
     "USB rail earns more", "https://www.adafruit.com/product/753"),
    ("Adafruit", "753-c", "0.1 uF ceramic capacitor", 1, 0.75,
     "high-frequency bypass at the driver", "https://www.adafruit.com/product/753"),
]

HARDWARE = [
    ("K&J Magnetics", "D84", "Neodymium disc magnet, 12.7 x 6.35 mm, N42", 4, 2.03,
     "two facing pairs at the latch edge: 70 N of pull at the as-built 2 mm gap, which is "
     "what shuts the last few millimetres and holds the leaf closed",
     "https://www.kjmagnetics.com/proddetail.asp?prod=D84"),
    ("generic", "dyneema-150", "Braided Dyneema line, 1.2 mm, 150 lb test, 2 m", 1, 8.00,
     "the cable; 680 N rating against a hardware-limited 151 N, a factor of 4.5", ""),
    ("generic", "dowel-4x35", "Steel dowel pin, 4 x 35 mm", 2, 0.60,
     "the two gear shafts, so no printed part is a bearing surface under load", ""),
    ("generic", "screw-8x32", "Wood screw, #8 x 32 mm, countersunk", 3, 0.15,
     "holds the shell to the hinge-side jamb reveal", ""),
    ("generic", "screw-8x25", "Wood screw, #8 x 25 mm, countersunk", 3, 0.15,
     "holds the cable anchor to the door face; 95 N of withdrawal per screw at full tension",
     ""),
    ("generic", "screw-6x20", "Wood screw, #6 x 20 mm, countersunk", 4, 0.12,
     "two per magnet pod", ""),
    ("generic", "m3x10", "M3 x 10 mm self-tapping screw", 8, 0.10,
     "four for the cover, two per time-of-flight board into their printed bosses", ""),
    ("generic", "m3x8", "M3 x 8 mm self-tapping screw", 4, 0.10,
     "the T-Display and the driver board into their printed bosses", ""),
    ("Bambu Lab", "pla-tough-plus", "PLA Tough+ filament, 1 kg spool", 1, 27.99,
     "every structural part; 245 g of it at 100% infill, so one spool covers several builds",
     "https://bambulab.com/en/filament/pla-tough"),
]

PRINTED = [
    ("base_shell", 1, "the whole unibody: motor cradle, both gear planes, drum bay, cable "
                      "chute, exit nose, board pockets, sensor shelf and the jamb flange"),
    ("base_cover", 1, "closes the bay, presses the motor into its cradle, carries the display "
                      "window, both sensor windows and the engraved hand-wave target"),
    ("motor_pinion", 1, "12T module 0.8 on the motor's double-D shaft"),
    ("compound_gear", 1, "48T module 0.8 and 14T module 1.0 on one print, on a steel dowel"),
    ("drum_gear", 1, "42T module 1.0 plus the grooved cable drum on one print"),
    ("door_anchor", 1, "screws to the door face and holds the cable eye 25 mm off it"),
    ("magnet_pod", 2, "one design, printed twice: latch edge of the door and the jamb facing "
                      "it, magnets loaded to attract"),
]


def main():
    (ROOT / "bom").mkdir(exist_ok=True)
    (ROOT / "docs").mkdir(exist_ok=True)
    p = params()

    with (ROOT / "bom/electronics.csv").open("w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["vendor", "sku", "item", "quantity", "unit_usd", "line_usd", "why", "source"])
        for vendor, sku, name, qty, price, why, url in ELECTRONICS:
            w.writerow([vendor, sku, name, qty, f"{price:.2f}", f"{qty * price:.2f}", why, url])

    with (ROOT / "bom/hardware.csv").open("w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["vendor", "sku", "item", "quantity", "unit_usd", "line_usd", "why", "source"])
        for vendor, sku, name, qty, price, why, url in HARDWARE:
            w.writerow([vendor, sku, name, qty, f"{price:.2f}", f"{qty * price:.2f}", why, url])

    rows = []
    for name, qty, why in PRINTED:
        mesh = trimesh.load_mesh(ROOT / "stl" / f"{name}.stl")
        grams = mesh.volume / 1000.0 * DENSITY_G_CM3
        rows.append({"part": name, "quantity": qty, "material": "Bambu Lab PLA Tough+",
                     "x_mm": round(float(mesh.extents[0]), 1),
                     "y_mm": round(float(mesh.extents[1]), 1),
                     "z_mm": round(float(mesh.extents[2]), 1),
                     "solid_mass_g": round(grams, 1),
                     "line_mass_g": round(grams * qty, 1),
                     "layer_h_mm": p["layer_h"], "purpose": why})
    with (ROOT / "bom/printed-parts.csv").open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0]))
        w.writeheader()
        w.writerows(rows)

    purchased_lines = len(ELECTRONICS) + len(HARDWARE)
    purchased_pieces = sum(r[3] for r in ELECTRONICS) + sum(r[3] for r in HARDWARE)
    report = {
        "purchased_line_items": purchased_lines,
        "purchased_pieces": purchased_pieces,
        "electronics_usd": round(sum(qty * price for _, _, _, qty, price, _, _ in ELECTRONICS), 2),
        "hardware_usd": round(sum(qty * price for _, _, _, qty, price, _, _ in HARDWARE), 2),
        "printed_designs": len(PRINTED),
        "printed_pieces": sum(q for _, q, _ in PRINTED),
        "printed_mass_g": round(sum(r["line_mass_g"] for r in rows), 1),
        "printed": rows,
    }
    report["total_usd"] = round(report["electronics_usd"] + report["hardware_usd"], 2)
    (ROOT / "docs/bom.json").write_text(json.dumps(report, indent=2))
    print(f"{report['printed_designs']} printed designs / {report['printed_pieces']} pieces, "
          f"{report['printed_mass_g']} g of PLA Tough+")
    print(f"{purchased_lines} purchased line items / {purchased_pieces} purchased pieces, "
          f"${report['electronics_usd']:.2f} electronics + ${report['hardware_usd']:.2f} "
          f"hardware = ${report['total_usd']:.2f}")


if __name__ == "__main__":
    main()
