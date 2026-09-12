"""Assembly placement of every printed part, mirrored from cad/r2d2.scad.

Reads the numeric parameters from cad/params.scad and the few placement constants the part
files define, then returns 4x4 matrices that move each STL (print frame) into the assembly
frame (floor z=0, +Y front, +X droid right, three-leg stance). Used by draw_robot.py and
render_video.py so both use exactly the placement the CAD assembly uses.

    from assembly_layout import Layout
    lay = Layout()
    for inst in lay.instances():   # dict(name, stl, matrix, mirrored, group)
        mesh = lay.load(inst)      # trimesh already transformed into the assembly frame
"""
import math
import re
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[1]


def _read_scad_assignments(path, names=None, base=None):
    """Evaluate `name = expr;` statements (OpenSCAD syntax subset) into a dict."""
    text = Path(path).read_text(encoding="utf-8")
    text = re.sub(r"//[^\n]*", "", text)
    text = re.sub(r"/\*.*?\*/", "", text, flags=re.S)
    env = dict(base or {})
    scope = {
        "sin": lambda a: math.sin(math.radians(a)), "cos": lambda a: math.cos(math.radians(a)),
        "tan": lambda a: math.tan(math.radians(a)), "asin": lambda v: math.degrees(math.asin(v)),
        "acos": lambda v: math.degrees(math.acos(v)), "atan": lambda v: math.degrees(math.atan(v)),
        "atan2": lambda y, x: math.degrees(math.atan2(y, x)), "sqrt": math.sqrt, "abs": abs,
        "min": min, "max": max, "floor": math.floor, "ceil": math.ceil, "round": round, "pow": pow,
        "true": True, "false": False, "PI": math.pi,
    }
    for chunk in text.split(";"):
        match = re.match(r"\s*([A-Za-z_$][A-Za-z0-9_]*)\s*=\s*(.+)$", chunk.strip(), flags=re.S)
        if not match:
            continue
        name, expr = match.group(1), match.group(2).strip()
        if name.startswith("$") or (names is not None and name not in names):
            continue
        try:
            value = eval(expr, {"__builtins__": {}}, {**scope, **env})
        except Exception:
            continue
        env[name] = value
    return env


def T(x=0, y=0, z=0):
    m = np.eye(4)
    m[:3, 3] = [x, y, z]
    return m


def R(ax=0, ay=0, az=0):
    """OpenSCAD rotate([ax, ay, az]) = Rz * Ry * Rx (degrees)."""
    a, b, c = map(math.radians, (ax, ay, az))
    rx = np.array([[1, 0, 0], [0, math.cos(a), -math.sin(a)], [0, math.sin(a), math.cos(a)]])
    ry = np.array([[math.cos(b), 0, math.sin(b)], [0, 1, 0], [-math.sin(b), 0, math.cos(b)]])
    rz = np.array([[math.cos(c), -math.sin(c), 0], [math.sin(c), math.cos(c), 0], [0, 0, 1]])
    m = np.eye(4)
    m[:3, :3] = rz @ ry @ rx
    return m


def MX():
    m = np.eye(4)
    m[0, 0] = -1
    return m


class Layout:
    def __init__(self, root=ROOT):
        self.root = Path(root)
        p = _read_scad_assignments(self.root / "cad/params.scad")
        p.update(_read_scad_assignments(self.root / "cad/lib.scad", names={"tt_len", "tt_gear_len", "tt_gear_h", "tt_thick", "tt_shaft_d", "tt_axle_from_front", "tt_can_d", "tt_shaft_l1", "tt_shaft_l2", "wheel_d", "wheel_w"}))
        legs = _read_scad_assignments(self.root / "cad/legs.scad", base=p)
        feet = _read_scad_assignments(self.root / "cad/feet.scad", base=p)
        head = _read_scad_assignments(self.root / "cad/head_drive.scad", base=p)
        self.p = p
        self.legs = legs
        self.feet = feet
        self.head = head
        # derived stance values (same formulas as r2d2.scad)
        p["shoulder_z_three_leg"] = p["ankle_z"] + p["leg_len"] * math.cos(math.radians(p["leg_lean"]))
        self.skirt_bottom_z = p["shoulder_z_three_leg"] - p["shoulder_z"] * math.cos(math.radians(p["body_tilt"]))
        self.skirt_bottom_y = p["shoulder_z"] * math.sin(math.radians(p["body_tilt"]))
        self.ankle_y = p["leg_len"] * math.sin(math.radians(p["leg_lean"]))
        self.center_foot_top_z = p["foot_clear"] + p["foot_center_h"]
        self.center_leg_y = self.skirt_bottom_y + p["center_leg_y_in_body"] * math.cos(math.radians(p["body_tilt"]))
        self.center_leg_plane_z = self.skirt_bottom_z - p["center_leg_y_in_body"] * math.sin(math.radians(p["body_tilt"]))

    # ---- placement helpers (native frames), mirroring r2d2.scad ----
    def at_body(self):
        p = self.p
        return T(0, 0, p["shoulder_z_three_leg"]) @ R(p["body_tilt"], 0, 0) @ T(0, 0, -p["shoulder_z"])

    def at_body_upper(self):
        return self.at_body() @ T(0, 0, self.p["body_lower_h"])

    def at_dome(self, spin=0.0):
        return self.at_body() @ T(0, 0, self.p["body_height"] + self.p["dome_gap"]) @ R(0, 0, spin)

    def at_leg(self, side):
        p = self.p
        m = T(side * (p["body_r"] + p["shoulder_spacer"]), 0, p["shoulder_z_three_leg"]) @ R(p["leg_lean"], 0, 0)
        return m @ MX() if side < 0 else m

    def at_foot(self, side):
        p = self.p
        m = T(side * p["leg_offset_x"], self.ankle_y, p["foot_clear"])
        return m @ MX() if side < 0 else m

    def at_center_leg(self):
        return T(0, self.center_leg_y, self.center_foot_top_z)

    def at_center_foot(self, swivel=0.0):
        p = self.p
        # swivel about the caster axis (which sits caster_trail ahead of the foot centre)
        return T(0, self.center_leg_y, p["foot_clear"]) @ R(0, 0, swivel) @ T(0, -p["caster_trail"], 0)

    def at_head_drive(self):
        return self.at_body() @ T(0, 0, self.p["body_top_plate_z"])

    # ---- print-frame -> native-frame inverses ----
    def print_inverse(self, name):
        p, lg, hd = self.p, self.legs, self.head
        if name == "leg_upper":
            tx = -(-p["leg_split_z"] - lg["lg_hs_top"]) / 2
            return np.linalg.inv(T(tx, 0, 0) @ R(0, -90, 0))
        if name == "leg_lower":
            tx = -(-lg["lg_tongue_bottom_z"] + p["leg_split_z"] + p["leg_splice_len"]) / 2
            return np.linalg.inv(T(tx, 0, 0) @ R(0, -90, 0))
        if name == "leg_center":
            return np.linalg.inv(R(180, 0, 0) @ R(-p["body_tilt"], 0, 0) @ T(0, 0, -lg["lg_center_plane_z"]))
        if name == "head_drive":
            return np.linalg.inv(T(0, 0, hd["hd_base_top"]) @ R(180, 0, 0))
        return np.eye(4)

    def instances(self, dome_spin=0.0, caster_swivel=0.0):
        """Every printed piece with its assembly matrix (STL print frame -> assembly)."""
        out = []

        def add(name, key, placement, group, mirrored=False):
            out.append({"name": name, "stl": f"stl/{key}.stl", "part": key, "group": group,
                        "matrix": placement @ self.print_inverse(key), "mirrored": mirrored})

        add("body_lower", "body_lower", self.at_body(), "body")
        add("body_upper", "body_upper", self.at_body_upper(), "body")
        add("dome", "dome", self.at_dome(dome_spin), "dome")
        add("head_drive", "head_drive", self.at_head_drive(), "head_drive")
        for side, label in ((1, "right"), (-1, "left")):
            add(f"leg_upper_{label}", "leg_upper", self.at_leg(side), "legs", side < 0)
            add(f"leg_lower_{label}", "leg_lower", self.at_leg(side), "legs", side < 0)
            add(f"foot_outer_{label}", "foot_outer", self.at_foot(side), "feet", side < 0)
        add("leg_center", "leg_center", self.at_center_leg(), "legs")
        add("foot_center", "foot_center", self.at_center_foot(caster_swivel), "feet")
        return out

    def load(self, inst):
        import trimesh
        mesh = trimesh.load_mesh(self.root / inst["stl"], process=False)
        mesh.apply_transform(inst["matrix"])
        return mesh

    # ---- purchased-part envelopes in assembly frame ----
    def motor_matrices(self, foot_matrix, center=False):
        """4x4 matrices placing lib.scad tt_motor() (shaft along Y, body toward -X) for one foot."""
        p, ft = self.p, self.feet
        result = []
        for sy in (-1, 1):
            if center:
                phi = ft["ft_phi_c_front"] if sy > 0 else ft["ft_phi_c_rear"]
            else:
                phi = sy * (90 + ft["ft_motor_tilt_o"])
            # ft_motor_at(y, phi) = translate([0, y, wheel_axle_z]) rotate([90 - phi, 0, 0]) rotate([0, 0, -90])
            m = T(0, sy * p["foot_axle_y"], p["wheel_axle_z"]) @ R(90 - phi, 0, 0) @ R(0, 0, -90)
            result.append(foot_matrix @ m)
        return result

    def wheel_matrices(self, foot_matrix):
        """4x4 matrices placing a wheel cylinder whose axis is Z, centred (four per foot)."""
        p = self.p
        result = []
        for sy in (-1, 1):
            for sx in (-1, 1):
                # wheel axis along X in the foot frame: rotate a Z-axis cylinder by 90 about Y
                result.append(foot_matrix @ T(sx * p["wheel_x"], sy * p["foot_axle_y"], p["wheel_axle_z"]) @ R(0, 90, 0))
        return result


if __name__ == "__main__":
    import json
    lay = Layout()
    print(json.dumps({k: lay.p[k] for k in ("body_r", "body_height", "shoulder_z", "shoulder_z_three_leg", "leg_offset_x", "leg_track", "body_tilt")}, indent=2))
    print("skirt bottom (y, z) =", round(lay.skirt_bottom_y, 1), round(lay.skirt_bottom_z, 1), "ankle y =", round(lay.ankle_y, 1))
    for inst in lay.instances():
        path = lay.root / inst["stl"]
        if path.exists():
            mesh = lay.load(inst)
            lo, hi = mesh.bounds
            print(f"{inst['name']:18s} z {lo[2]:7.1f}..{hi[2]:7.1f}  y {lo[1]:7.1f}..{hi[1]:7.1f}  x {lo[0]:7.1f}..{hi[0]:7.1f}  watertight={mesh.is_watertight}")
        else:
            print(f"{inst['name']:18s} (STL not yet exported)")
