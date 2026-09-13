"""Mass, centre of gravity and support screening from the actual STL geometry, in both stances.

Revision D: the outer legs stay vertical and the body pitches about the shoulder axis. The
two-foot stance is actuator stroke st_s_two (tilt 0, centre foot stowed); the three-leg stance is
st_s_three (tilt body_tilt, centre foot on the floor ahead of the outer feet). The placement below
mirrors cad/stance.scad and cad/r2d2.scad exactly; scripts/check_stance.py imports it to sample the
whole transition.

Printed-part mass = mesh volume x PETG density x an effective fill fraction (walls + infill;
default 0.45 for 5 walls and 30 % gyroid on these wall-dominated parts). Purchased parts are
point masses at their designed positions (catalogue masses, or stated allowances). Writes
docs/stability.json. This is a screening calculation, not a measurement; weigh the finished robot.

Usage: python scripts/stability.py [--fill 0.45] [--yaw 0]
"""
import argparse
import json
import math
import sys
from functools import lru_cache
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent))
from assembly_layout import MX, R, T, _read_scad_assignments  # noqa: E402

ROOT = Path(__file__).resolve().parents[1]
DENSITY = 1.27e-3  # g/mm3 PETG
LIB_NAMES = {"tt_len", "tt_gear_len", "tt_gear_h", "tt_thick", "tt_shaft_d", "tt_axle_from_front", "tt_can_d",
             "tt_shaft_l1", "tt_shaft_l2", "wheel_d", "wheel_w"}


def load_params(root=ROOT, overrides=None):
    """Numeric parameters from params.scad (+ the part-file constants the placement needs).

    overrides are applied to params.scad values BEFORE the dependent assignments are evaluated, so
    a perturbed design parameter propagates exactly as it would in OpenSCAD.
    """
    root = Path(root)
    overrides = dict(overrides or {})
    text_params = _read_with_overrides(root / "cad/params.scad", overrides)
    p = dict(text_params)
    p.update(_read_scad_assignments(root / "cad/lib.scad", names=LIB_NAMES))
    import re
    lib_text = (root / "cad/lib.scad").read_text(encoding="utf-8")
    for name in ("wheel_d", "wheel_w"):      # these follow a module body, which the generic reader skips
        p[name] = float(re.search(r"\b" + name + r"\s*=\s*([0-9.]+)\s*;", lib_text).group(1))
    legs = _read_scad_assignments(root / "cad/legs.scad", base=p)
    feet = _read_scad_assignments(root / "cad/feet.scad", base=p)
    head = _read_scad_assignments(root / "cad/head_drive.scad", base=p)
    p.update({k: legs[k] for k in ("lg_hs_top", "lg_tongue_bottom_z", "lg_center_bottom_z")})
    p.update({k: feet[k] for k in ("ft_phi_c_front", "ft_phi_c_rear", "ft_motor_tilt_o")})
    p["hd_base_top"] = head["hd_base_top"]
    return p


def _read_with_overrides(path, overrides):
    import re
    text = Path(path).read_text(encoding="utf-8")
    for name, value in overrides.items():
        pattern = re.compile(r"(^|\n)(\s*)" + re.escape(name) + r"\s*=\s*[^;]*;")
        if not pattern.search(text):
            raise KeyError(f"override {name} is not assigned in {path}")
        text = pattern.sub(lambda m: f"{m.group(1)}{m.group(2)}{name} = {value!r};", text, count=1)
    import tempfile
    with tempfile.TemporaryDirectory(prefix="r2-params-") as folder:
        tmp = Path(folder) / Path(path).name
        tmp.write_text(text, encoding="utf-8")
        return _read_scad_assignments(tmp)


class Stance:
    """Kinematics and placement of revision D (cad/stance.scad KINEMATICS)."""

    def __init__(self, p):
        self.p = p
        a = math.radians(p["st_guide_angle"])
        self.sa, self.ca = math.sin(a), math.cos(a)
        self.S = p["shoulder_z_two_leg"]
        self.u = np.array([0.0, self.sa, -self.ca])

    # ---- kinematics ----
    def hinge_body(self, s):
        p = self.p
        q = s - p["st_s_two"]
        return np.array([0.0, p["st_hinge_y"] + q * self.sa, p["st_hinge_z"] - q * self.ca])

    def contact_stroke(self):
        return self.p["st_s_two"] + self.p["st_stow_lift"] / self.ca

    def tilt(self, s):
        p = self.p
        h = self.hinge_body(s)
        y, w = h[1], h[2] - p["shoulder_z"]
        c = p["st_floor_hinge_z"] - self.S
        if w >= c:
            return 0.0
        r = math.hypot(y, w)
        return math.degrees(math.atan2(y, w)) - math.degrees(math.acos(c / r))

    def on_floor(self, s):
        return s > self.contact_stroke() + 1e-9

    def stroke_for_tilt(self, tilt):
        lo, hi = self.contact_stroke(), self.p["st_act_stroke"]
        for _ in range(80):
            mid = (lo + hi) / 2
            if self.tilt(mid) < tilt:
                lo = mid
            else:
                hi = mid
        return (lo + hi) / 2

    # ---- placement (4x4, local -> assembly) ----
    def at_body(self, s):
        return T(0, 0, self.S) @ R(self.tilt(s), 0, 0) @ T(0, 0, -self.p["shoulder_z"])

    def at_carriage(self, s):
        return self.at_body(s) @ T(*self.hinge_body(s)) @ R(self.p["st_guide_angle"], 0, 0)

    def hinge_world(self, s):
        return (self.at_body(s) @ np.append(self.hinge_body(s), 1.0))[:3]

    def at_housing(self, s, pitch=0.0):
        """leg_center native frame; pitch rotates about the hinge (positive = toe up)."""
        h = self.hinge_world(s)
        return T(*h) @ R(pitch, 0, 0) @ T(0, 0, -self.p["st_hinge_up"])

    def at_center_foot(self, s, yaw=0.0, pitch=0.0):
        p = self.p
        return self.at_housing(s, pitch) @ R(0, 0, yaw) @ T(0, -p["caster_trail"], -p["foot_center_h"])

    def at_leg(self, side):
        p = self.p
        m = T(side * (p["body_r"] + p["shoulder_spacer"]), 0, self.S)
        return m @ MX() if side < 0 else m

    def at_foot(self, side):
        p = self.p
        m = T(side * p["leg_offset_x"], 0, p["foot_clear"])
        return m @ MX() if side < 0 else m

    def lock_y_z(self):
        p = self.p
        a = math.radians(p["st_lock_angle"])
        return p["st_lock_r"] * math.cos(a), p["shoulder_z"] + p["st_lock_r"] * math.sin(a)

    def lock_frame(self, side):
        """Lock frame in the BODY frame (origin at the pin-exit face, +X outward)."""
        y, z = self.lock_y_z()
        m = T(side * self.p["st_land_x"], y, z)
        return m @ MX() if side < 0 else m

    def act_fixed_eye(self):
        p = self.p
        return self.hinge_body(p["st_s_two"]) + (p["st_eye_up"] + p["st_act_closed"] + p["st_s_two"]) * (-self.u)

    def guide_point(self, t, x=0.0):
        """Body-frame point t along -u from the stowed hinge, at lateral offset x."""
        return self.hinge_body(self.p["st_s_two"]) + t * (-self.u) + np.array([x, 0.0, 0.0])

    # ---- print frame -> native frame ----
    def print_inverse(self, part):
        p = self.p
        if part == "leg_upper":
            return np.linalg.inv(T(-(-p["leg_split_z"] - p["lg_hs_top"]) / 2, 0, 0) @ R(0, -90, 0))
        if part == "leg_lower":
            return np.linalg.inv(T(-(-p["lg_tongue_bottom_z"] + p["leg_split_z"] + p["leg_splice_len"]) / 2, 0, 0) @ R(0, -90, 0))
        if part == "leg_center":
            return np.linalg.inv(T(0, 0, -p["lg_center_bottom_z"]))
        if part == "leg_carriage":           # stance.scad leg_carriage(): translate([0, 0, 21]) rotate([90, 0, 0])
            return np.linalg.inv(T(0, 0, 21) @ R(90, 0, 0))
        if part == "head_drive":
            return np.linalg.inv(T(0, 0, p["hd_base_top"]) @ R(180, 0, 0))
        return np.eye(4)

    def instances(self, s, yaw=0.0):
        """Every printed piece: dict(name, part, group, matrix print->assembly, mirrored)."""
        p = self.p
        out = []

        def add(name, part, placement, group, mirrored=False):
            out.append({"name": name, "part": part, "group": group, "mirrored": mirrored,
                        "matrix": placement @ self.print_inverse(part)})

        body = self.at_body(s)
        add("body_lower", "body_lower", body, "body")
        add("body_upper", "body_upper", body @ T(0, 0, p["body_lower_h"]), "body")
        add("dome", "dome", body @ T(0, 0, p["body_height"] + p["dome_gap"]), "body")
        add("head_drive", "head_drive", body @ T(0, 0, p["body_top_plate_z"]), "body")
        for side, label in ((1, "right"), (-1, "left")):
            add(f"leg_upper_{label}", "leg_upper", self.at_leg(side), "legs", side < 0)
            add(f"leg_lower_{label}", "leg_lower", self.at_leg(side), "legs", side < 0)
            add(f"foot_outer_{label}", "foot_outer", self.at_foot(side), "feet", side < 0)
        add("leg_carriage", "leg_carriage", self.at_carriage(s), "carriage")
        add("leg_center", "leg_center", self.at_housing(s), "housing")
        add("foot_center", "foot_center", self.at_center_foot(s, yaw), "foot")
        return out

    # ---- purchased parts ----
    def motor_points(self, foot_matrix, center):
        p = self.p
        pts = []
        for sy in (-1, 1):
            if center:
                phi = p["ft_phi_c_front"] if sy > 0 else p["ft_phi_c_rear"]
            else:
                phi = sy * (90 + p["ft_motor_tilt_o"])
            pts.append(foot_matrix @ T(0, sy * p["foot_axle_y"], p["wheel_axle_z"]) @ R(90 - phi, 0, 0) @ R(0, 0, -90))
        return pts

    def wheel_matrices(self, foot_matrix):
        p = self.p
        return [foot_matrix @ T(sx * p["wheel_x"], sy * p["foot_axle_y"], p["wheel_axle_z"]) @ R(0, 90, 0)
                for sy in (-1, 1) for sx in (-1, 1)]

    def purchased(self, s, yaw=0.0):
        """(name, grams, local point, group). group frames: body, carriage, housing, foot, world."""
        p = self.p
        u = self.u
        rows = [
            ("battery 12 V 7 Ah SLA", 2260.0, (0, p["battery_y"], p["battery_shelf_z"] + p["battery"][2] / 2), "body"),
            ("electronics and harness allowance", 750.0, (0, 0, p["body_lower_h"] + p["tray_z_upper"] + 15), "body"),
            ("lazy susan", 250.0, (0, 0, p["body_top_plate_z"] + p["susan_t"] / 2), "body"),
            ("dome electronics allowance", 200.0, (0, 0, p["body_height"] + 60), "body"),
            ("body rods and fasteners allowance", 850.0, (0, 0, p["body_height"] / 2), "body"),
            ("head drive motor and wheel", 69.0, (0, -p["head_wheel_r"], p["body_top_plate_z"] - 25), "body"),
        ]
        a = self.act_fixed_eye()
        case_mid = a + u * (p["st_act_case_t"][0] + p["st_act_case_t"][1]) / 2
        rows.append(("Actuonix P16-100 case (110 g less 15 g rod)", 95.0, tuple(case_mid), "body"))
        rows.append(("Actuonix P16-100 rod and eye", 15.0, (0, 0, p["st_eye_up"] + 20), "carriage"))
        for sx in (-1, 1):
            rows.append((f"12 mm x 182 mm steel guide shaft {sx:+d}", 162.0,
                         tuple(self.guide_point((p["st_shaft_t"][0] + p["st_shaft_t"][1]) / 2, sx * p["st_shaft_x"])), "body"))
            rows.append((f"LM12LUU bearing {sx:+d}", 42.0, (sx * p["st_shaft_x"], 0, p["st_brg_t"] + p["st_brg"][2] / 2), "carriage"))
            rows.append((f"hinge M8 x 35 bolt, spacer tube, washer, nut {sx:+d}", 28.0, (sx * 48, 0, 0), "carriage"))
        rows.append(("rod-eye M4 x 45 pin and nut", 5.0, (0, 0, p["st_eye_up"]), "carriage"))
        rows.append(("caster M12 x 70 bolt, 2 x 6001, spacer, washers", 60.0, (0, 0, 40), "housing"))
        sx_servo = p["st_horn_arm"]
        servo_x = -22 + p["st_horn_rest_gap"] + p["st_horn_tip_r"] - sx_servo[0]
        servo_z = -12 - sx_servo[1]
        for side in (-1, 1):
            lf = self.lock_frame(side)
            rows.append((f"Winco GN 412-6-35-B-1 plunger {side:+d}", 68.9, tuple((lf @ np.array([-17.0, 0, 0, 1]))[:3]), "body"))
            rows.append((f"MG995 release servo {side:+d}", 62.41, tuple((lf @ np.array([servo_x, 28.0, servo_z - 10, 1]))[:3]), "body"))
            rows.append((f"Omron SS-01GL switch {side:+d} (allowance)", 2.0, tuple((lf @ np.array([-15.0, 0, 23.0, 1]))[:3]), "body"))
        rows.append(("lock and guide fasteners and inserts allowance", 40.0, (0, 0, p["shoulder_z"] - 60), "body"))
        la = math.radians(p["st_lock_angle"])
        for side in (-1, 1):
            for extra in (0.0, p["body_tilt"]):
                ang = la + math.radians(extra)
                pt = self.at_leg(side) @ np.array([6.5, p["st_lock_r"] * math.cos(ang), p["st_lock_r"] * math.sin(ang), 1])
                rows.append((f"GN 412.2 receiver {side:+d} {extra:.0f}", 10.0, tuple(pt[:3]), "world"))
            rows.append((f"leg M8 rods {side:+d}", 320.0, tuple((self.at_leg(side) @ np.array([15, 0, -150, 1]))[:3]), "world"))
            fm = self.at_foot(side)
            for m in self.motor_points(fm, False):
                rows.append((f"outer foot motor {side:+d}", 30.6, tuple(m[:3, 3]), "world"))
            for m in self.wheel_matrices(fm):
                rows.append((f"outer foot wheel {side:+d}", 38.0, tuple(m[:3, 3]), "world"))
        foot_local = T(0, 0, 0)
        for m in self.motor_points(foot_local, True):
            rows.append(("centre foot motor", 30.6, tuple(m[:3, 3]), "foot"))
        for m in self.wheel_matrices(foot_local):
            rows.append(("centre foot wheel", 38.0, tuple(m[:3, 3]), "foot"))
        return rows

    def group_matrix(self, group, s, yaw=0.0):
        if group == "body":
            return self.at_body(s)
        if group == "carriage":
            return self.at_carriage(s)
        if group == "housing":
            return self.at_housing(s)
        if group == "foot":
            return self.at_center_foot(s, yaw)
        return np.eye(4)

    # ---- support ----
    def contacts(self, s, yaw=0.0):
        p = self.p
        pts = []
        for side in (-1, 1):
            fm = self.at_foot(side)
            for sy in (-1, 1):
                for sx in (-1, 1):
                    pts.append((fm @ np.array([sx * p["wheel_x"], sy * p["foot_axle_y"], 0, 1]))[:2])
        centre = []
        if self.on_floor(s):
            cm = self.at_center_foot(s, yaw)
            for sy in (-1, 1):
                for sx in (-1, 1):
                    centre.append((cm @ np.array([sx * p["wheel_x"], sy * p["foot_axle_y"], 0, 1]))[:2])
        return np.array(pts), np.array(centre) if centre else np.zeros((0, 2))


@lru_cache(maxsize=None)
def mesh_props(path):
    import trimesh
    mesh = trimesh.load_mesh(path, process=False)
    return float(abs(mesh.volume)), np.array(mesh.center_mass)


def mass_items(stance, s, yaw=0.0, fill=0.45, root=ROOT):
    """Every mass as dict(name, grams, world centre, kind, group)."""
    items = []
    for inst in stance.instances(s, yaw):
        vol, centre = mesh_props(str(Path(root) / "stl" / f"{inst['part']}.stl"))
        world = (inst["matrix"] @ np.append(centre, 1.0))[:3]
        items.append({"name": inst["name"], "grams": vol * DENSITY * fill, "centre": world, "kind": "printed",
                      "group": inst["group"]})
    for name, grams, local, group in stance.purchased(s, yaw):
        world = (stance.group_matrix(group, s, yaw) @ np.append(np.asarray(local, float), 1.0))[:3]
        items.append({"name": name, "grams": grams, "centre": world, "kind": "purchased", "group": group})
    return items


def centre_of_gravity(items, groups=None):
    chosen = [i for i in items if groups is None or i["group"] in groups]
    mass = sum(i["grams"] for i in chosen)
    return mass, sum(i["grams"] * i["centre"] for i in chosen) / mass


def polygon_margin(points, xy):
    """Signed distance from xy to the edge of the convex hull of points (positive inside)."""
    from scipy.spatial import ConvexHull
    hull = ConvexHull(np.asarray(points))
    return float(-(hull.equations[:, :2] @ np.asarray(xy) + hull.equations[:, 2]).max())


def stance_report(stance, s, yaw=0.0, fill=0.45, root=ROOT):
    p = stance.p
    items = mass_items(stance, s, yaw, fill, root)
    total, cog = centre_of_gravity(items)
    outer, centre = stance.contacts(s, yaw)
    support = np.vstack([outer, centre]) if len(centre) else outer
    margin = polygon_margin(support, cog[:2])
    outer_y = float(outer[:, 1].mean())
    report = {
        "stroke_mm": round(float(s), 3),
        "body_tilt_deg": round(stance.tilt(s), 3),
        "centre_foot_on_floor": bool(stance.on_floor(s)),
        "centre_foot_yaw_deg": yaw,
        "total_mass_g": round(total, 1),
        "printed_mass_g": round(sum(i["grams"] for i in items if i["kind"] == "printed"), 1),
        "purchased_mass_g": round(sum(i["grams"] for i in items if i["kind"] == "purchased"), 1),
        "centre_of_gravity_mm": [round(float(v), 1) for v in cog],
        "wheel_contact_y_range_mm": [round(float(support[:, 1].min()), 1), round(float(support[:, 1].max()), 1)],
        "wheel_contact_x_range_mm": [round(float(support[:, 0].min()), 1), round(float(support[:, 0].max()), 1)],
        "support_margin_mm": round(margin, 1),
        "support_tip_angle_deg": round(math.degrees(math.atan2(margin, cog[2])), 1),
        "outer_foot_axle_mean_y_mm": round(outer_y, 1),
        "tip_back_margin_mm": round(float(cog[1] - support[:, 1].min()), 1),
        "tip_forward_margin_mm": round(float(support[:, 1].max() - cog[1]), 1),
    }
    report["tip_back_angle_deg"] = round(math.degrees(math.atan2(report["tip_back_margin_mm"], cog[2])), 1)
    report["tip_forward_angle_deg"] = round(math.degrees(math.atan2(report["tip_forward_margin_mm"], cog[2])), 1)
    report["tip_side_angle_deg"] = round(math.degrees(math.atan2(min(cog[0] - support[:, 0].min(), support[:, 0].max() - cog[0]), cog[2])), 1)
    if len(centre):
        centre_y = float(centre[:, 1].mean())
        report["center_foot_axle_mean_y_mm"] = round(centre_y, 1)
        report["center_foot_static_share"] = round(float((cog[1] - outer_y) / (centre_y - outer_y)), 3)
    else:
        report["center_foot_axle_mean_y_mm"] = None
        report["center_foot_static_share"] = 0.0
        report["centre_wheel_floor_clearance_mm"] = round(centre_wheel_clearance(stance, s, yaw), 2)
    report["items"] = [{"name": i["name"], "mass_g": round(float(i["grams"]), 1),
                        "centre_mm": [round(float(v), 1) for v in i["centre"]], "kind": i["kind"], "group": i["group"]}
                       for i in items]
    return report


def centre_wheel_clearance(stance, s, yaw=0.0):
    p = stance.p
    cm = stance.at_center_foot(s, yaw)
    return min(float((m @ np.array([0, 0, 0, 1]))[2]) - p["wheel_d"] / 2 for m in stance.wheel_matrices(cm))


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--fill", type=float, default=0.45)
    parser.add_argument("--yaw", type=float, default=0.0, help="centre-foot swivel for the three-leg report")
    args = parser.parse_args()
    p = load_params()
    stance = Stance(p)
    two = stance_report(stance, p["st_s_two"], 0.0, args.fill)
    three = stance_report(stance, p["st_s_three"], args.yaw, args.fill)
    report = {
        "method": "STL volumes x 1.27 g/cm3 x fill fraction; purchased parts as point masses; screening only",
        "revision": "D",
        "fill_fraction": args.fill,
        "stance_note": "Top-level figures are the three-leg operating stance; 'stances' carries both.",
    }
    report.update({k: v for k, v in three.items()})
    report["stances"] = {"two_foot": two, "three_leg": three}
    (ROOT / "docs/stability.json").write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    keys = ("stroke_mm", "body_tilt_deg", "total_mass_g", "centre_of_gravity_mm", "wheel_contact_y_range_mm",
            "support_margin_mm", "support_tip_angle_deg", "tip_back_angle_deg", "tip_forward_angle_deg",
            "tip_side_angle_deg", "center_foot_static_share")
    for label, data in (("two-foot stance", two), ("three-leg stance", three)):
        print(f"== {label} ==")
        for key in keys:
            print(f"  {key}: {data[key]}")
        if "centre_wheel_floor_clearance_mm" in data:
            print(f"  centre_wheel_floor_clearance_mm: {data['centre_wheel_floor_clearance_mm']}")


if __name__ == "__main__":
    main()
