"""Mass, centre of gravity and support-polygon screening from the actual STL geometry.

Printed-part mass = mesh volume x PETG density x an effective fill fraction (walls + infill;
default 0.45 for 5 walls and 30 % gyroid on these wall-dominated parts). Purchased parts are
point masses at their designed positions. Writes docs/stability.json and prints a summary.
This is a screening calculation, not a measurement; weigh the finished robot.

Usage: python scripts/stability.py [--fill 0.45]
"""
import argparse
import json
import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent))
from assembly_layout import Layout, T  # noqa: E402

ROOT = Path(__file__).resolve().parents[1]
DENSITY = 1.27e-3  # g/mm3 PETG


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--fill", type=float, default=0.45)
    args = parser.parse_args()
    lay = Layout()
    p = lay.p
    items = []
    for inst in lay.instances():
        mesh = lay.load(inst)
        mass = abs(mesh.volume) * DENSITY * args.fill
        items.append((inst["name"], mass, mesh.center_mass, "printed"))
    # purchased masses (g) at assembly positions
    body = lay.at_body()

    def body_point(x, y, z):
        return (body @ T(x, y, z))[:3, 3]

    battery_c = body_point(0, p["battery_y"], p["battery_shelf_z"] + p["battery"][2] / 2)
    items.append(("battery", 2260, battery_c, "purchased"))
    deck_c = body_point(0, 0, p["body_lower_h"] + p["tray_z_upper"] + 15)
    items.append(("electronics_and_harness", 750, deck_c, "purchased"))
    susan_c = body_point(0, 0, p["body_top_plate_z"] + p["susan_t"] / 2)
    items.append(("lazy_susan", 250, susan_c, "purchased"))
    items.append(("dome_electronics", 200, body_point(0, 0, p["body_height"] + 60), "purchased"))
    rods_c = body_point(0, 0, p["body_height"] / 2)
    items.append(("body_rods_and_fasteners", 850, rods_c, "purchased"))
    for inst in lay.instances():
        if inst["group"] != "feet":
            continue
        for m in lay.motor_matrices(inst["matrix"] if not inst["mirrored"] else inst["matrix"], center=inst["part"] == "foot_center"):
            items.append((inst["name"] + "_motor", 30.6, m[:3, 3], "purchased"))
        for m in lay.wheel_matrices(inst["matrix"]):
            items.append((inst["name"] + "_wheel", 38, m[:3, 3], "purchased"))
    items.append(("head_drive_motor_wheel", 69, (lay.at_head_drive() @ T(0, -p["head_wheel_r"], -25))[:3, 3], "purchased"))
    for side in (-1, 1):
        items.append((f"leg_rods_{side}", 320, (lay.at_leg(side) @ T(15, 0, -150))[:3, 3], "purchased"))
    total = sum(m for _, m, _, _ in items)
    cog = sum(m * np.asarray(c) for _, m, c, _ in items) / total
    # support polygon: outer feet contact patches (wheels) and centre foot wheels
    contacts = []
    for inst in lay.instances():
        if inst["group"] == "feet":
            for m in lay.wheel_matrices(inst["matrix"]):
                contacts.append(m[:3, 3][:2])
    contacts = np.array(contacts)
    y_min, y_max = contacts[:, 1].min(), contacts[:, 1].max()
    x_min, x_max = contacts[:, 0].min(), contacts[:, 0].max()
    # load share (static, moments about the outer-foot axle line): solve three supports
    outer_y = np.mean([c[1] for c in contacts if abs(c[0]) > 100])
    center_y = np.mean([c[1] for c in contacts if abs(c[0]) <= 100])
    # two-point statics in Y: outer line at outer_y, centre foot at center_y
    if abs(center_y - outer_y) > 1e-6:
        center_share = (cog[1] - outer_y) / (center_y - outer_y)
    else:
        center_share = float("nan")
    tip_back_margin = cog[1] - y_min
    tip_forward_margin = y_max - cog[1]
    tip_back_angle = np.degrees(np.arctan2(tip_back_margin, cog[2]))
    tip_forward_angle = np.degrees(np.arctan2(tip_forward_margin, cog[2]))
    tip_side_angle = np.degrees(np.arctan2(min(cog[0] - x_min, x_max - cog[0]), cog[2]))
    report = {
        "method": "STL volumes x 1.27 g/cm3 x fill fraction; purchased parts as point masses; screening only",
        "fill_fraction": args.fill,
        "total_mass_g": round(total, 1),
        "printed_mass_g": round(sum(m for _, m, _, k in items if k == "printed"), 1),
        "purchased_mass_g": round(sum(m for _, m, _, k in items if k == "purchased"), 1),
        "centre_of_gravity_mm": [round(float(v), 1) for v in cog],
        "wheel_contact_y_range_mm": [round(float(y_min), 1), round(float(y_max), 1)],
        "wheel_contact_x_range_mm": [round(float(x_min), 1), round(float(x_max), 1)],
        "outer_foot_axle_mean_y_mm": round(float(outer_y), 1),
        "center_foot_axle_mean_y_mm": round(float(center_y), 1),
        "center_foot_static_share": round(float(center_share), 3) if center_share == center_share else None,
        "tip_back_margin_mm": round(float(tip_back_margin), 1),
        "tip_forward_margin_mm": round(float(tip_forward_margin), 1),
        "tip_back_angle_deg": round(float(tip_back_angle), 1),
        "tip_forward_angle_deg": round(float(tip_forward_angle), 1),
        "tip_side_angle_deg": round(float(tip_side_angle), 1),
        "items": [{"name": n, "mass_g": round(float(m), 1), "centre_mm": [round(float(v), 1) for v in c], "kind": k} for n, m, c, k in items],
    }
    (ROOT / "docs/stability.json").write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    for key in ("total_mass_g", "printed_mass_g", "centre_of_gravity_mm", "wheel_contact_y_range_mm", "center_foot_static_share",
                "tip_back_margin_mm", "tip_forward_margin_mm", "tip_back_angle_deg", "tip_forward_angle_deg", "tip_side_angle_deg"):
        print(f"{key}: {report[key]}")


if __name__ == "__main__":
    main()
