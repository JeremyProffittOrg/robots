"""Assembly placement of every printed part for fable-r2d2 revision D, at any stance pose.

Revision D moves the robot between two stances with a linear actuator. The pose is one number,
the actuator stroke `stance_s` (mm from fully closed): cad/params.scad `st_s_two` is the two-foot
stance (body upright, centre foot stowed) and `st_s_three` the three-leg stance (body tilted
`body_tilt`, centre foot on the floor). cad/r2d2.scad renders any pose with
`-D stance_s=<mm>`; the name of that variable is STANCE_PARAMETER below.

The kinematics, the print-frame inverses and the list of printed instances are NOT copied here:
they come from scripts/stability.py `Stance`, which mirrors cad/stance.scad and is owned by the
CAD. This module wraps that class for the drawing, video and mock-up scripts, checks it against
scripts/parts.json, and adds the purchased mechanism envelopes those scripts draw.

    from assembly_layout import Layout
    lay = Layout()                      # three-leg stance
    two = Layout(stroke=two.endpoints()["two_foot"])
    for inst in lay.instances():        # dict(name, stl, part, group, matrix, mirrored)
        mesh = lay.load(inst)           # trimesh already transformed into the assembly frame
"""
import json
import math
import re
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[1]

REVISION = "D"
"""Package revision every generated output is labelled with."""

STANCE_PARAMETER = "stance_s"
"""OpenSCAD variable in cad/r2d2.scad that sets the actuator stroke of the rendered pose."""

NUMBER_WORDS = ["zero", "one", "two", "three", "four", "five", "six", "seven", "eight", "nine", "ten",
                "eleven", "twelve", "thirteen", "fourteen", "fifteen", "sixteen", "seventeen",
                "eighteen", "nineteen", "twenty"]


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


def number_word(count):
    """English word for a small count ("nine"); digits above twenty."""
    count = int(count)
    return NUMBER_WORDS[count] if 0 <= count < len(NUMBER_WORDS) else str(count)


def read_parts(root=ROOT):
    """scripts/parts.json `parts` mapping, in file order."""
    return json.loads((Path(root) / "scripts/parts.json").read_text(encoding="utf-8"))["parts"]


def package_counts(root=ROOT):
    """Printed-part counts read from scripts/parts.json (never hard-coded)."""
    parts = read_parts(root)
    return {
        "designs": len(parts),
        "pieces": sum(int(row["quantity"]) for row in parts.values()),
        "mirrored": [name for name, row in parts.items() if row.get("mirror")],
        "names": list(parts),
    }


def declared_stance_parameter(root=ROOT):
    """Default expression of STANCE_PARAMETER in cad/r2d2.scad, or None when it is not declared."""
    text = re.sub(r"//[^\n]*", "", (Path(root) / "cad/r2d2.scad").read_text(encoding="utf-8"))
    match = re.search(rf"(?m)^\s*{re.escape(STANCE_PARAMETER)}\s*=\s*([^;]+);", text)
    return match.group(1).strip() if match else None


def _stance_module():
    # scripts/stability.py imports T, R, MX and _read_scad_assignments from this module, so it is
    # imported lazily here (by then this module is fully initialised).
    import stability
    return stability


# Which stance frame each Stance.instances() group moves with.
GROUP_FRAME = {"body": "body", "carriage": "carriage", "housing": "housing", "foot": "foot",
               "legs": "fixed", "feet": "fixed"}


class Layout:
    def __init__(self, root=ROOT, stroke=None, caster_yaw=0.0):
        self.root = Path(root)
        stability = _stance_module()
        p = stability.load_params(self.root)
        p.update(_read_scad_assignments(self.root / "cad/lib.scad", names={
            "tt_len", "tt_gear_len", "tt_gear_h", "tt_thick", "tt_shaft_d", "tt_axle_from_front", "tt_can_d",
            "tt_shaft_l1", "tt_shaft_l2", "wheel_d", "wheel_w"}))
        self.p = p
        self.stance = stability.Stance(p)
        self.legs = _read_scad_assignments(self.root / "cad/legs.scad", base=p)
        self.feet = _read_scad_assignments(self.root / "cad/feet.scad", base=p)
        self.head = _read_scad_assignments(self.root / "cad/head_drive.scad", base=p)
        ends = self.endpoints()
        self.s = ends["three_leg"] if stroke is None else float(stroke)
        if not ends["two_foot"] - 1e-6 <= self.s <= ends["three_leg"] + 1e-6:
            raise ValueError(f"{STANCE_PARAMETER}={self.s} is outside {ends['two_foot']}..{ends['three_leg']} mm")
        self.caster_yaw = float(caster_yaw)
        self.tilt = self.stance.tilt(self.s)
        body = self.at_body()
        skirt = body @ np.array([0.0, 0.0, 0.0, 1.0])
        self.shoulder_z_world = float(self.stance.S)
        self.skirt_bottom_y = float(skirt[1])
        self.skirt_bottom_z = float(skirt[2])
        self.ankle_y = float(p["leg_len"] * math.sin(math.radians(p["leg_lean"])))
        self.center_foot_top_z = float(p["foot_clear"] + p["foot_center_h"])
        self.caster_axis = [float(v) for v in self.stance.hinge_world(self.s)[:2]]

    # ---- stance ----
    def endpoints(self):
        p = self.p
        return {"two_foot": float(p["st_s_two"]), "contact": float(self.stance.contact_stroke()),
                "three_leg": float(p["st_s_three"])}

    def at_stroke(self, stroke):
        """A Layout of the same CAD at another stance pose."""
        other = Layout.__new__(Layout)
        other.__dict__.update(self.__dict__)
        other.s = float(stroke)
        ends = self.endpoints()
        if not ends["two_foot"] - 1e-6 <= other.s <= ends["three_leg"] + 1e-6:
            raise ValueError(f"{STANCE_PARAMETER}={other.s} is outside {ends['two_foot']}..{ends['three_leg']} mm")
        other.tilt = self.stance.tilt(other.s)
        skirt = other.at_body() @ np.array([0.0, 0.0, 0.0, 1.0])
        other.skirt_bottom_y, other.skirt_bottom_z = float(skirt[1]), float(skirt[2])
        other.caster_axis = [float(v) for v in self.stance.hinge_world(other.s)[:2]]
        return other

    def centre_foot_lift(self, stroke=None):
        """Height of the centre-foot hinge above its floor-contact height, mm (0 on the floor)."""
        s = self.s if stroke is None else stroke
        lift = float(self.stance.hinge_world(s)[2] - self.p["st_floor_hinge_z"])
        return 0.0 if abs(lift) < 1e-6 else lift   # on the floor: no -0.0 from rounding

    def locks_seated_cad(self, stroke=None):
        """Lock pins as cad/stance.scad st_mechanism() draws them: seated at or below touchdown and
        at the three-leg endpoint, released on the tilt path between them."""
        s = self.s if stroke is None else stroke
        ends = self.endpoints()
        return s <= ends["contact"] + 0.01 or abs(s - ends["three_leg"]) < 0.05

    def frame(self, name, stroke=None):
        """Stance frame (assembly frame) of a group at a stroke: body, carriage, housing, foot, fixed."""
        s = self.s if stroke is None else stroke
        if name == "body":
            return self.stance.at_body(s)
        if name == "carriage":
            return self.stance.at_carriage(s)
        if name == "housing":
            return self.stance.at_housing(s)
        if name == "foot":
            return self.stance.at_center_foot(s, self.caster_yaw)
        if name == "fixed":
            return np.eye(4)
        raise KeyError(f"unknown stance frame {name}")

    def delta(self, name, stroke):
        """Matrix that moves geometry placed at this Layout's pose to the pose at `stroke`."""
        return self.frame(name, stroke) @ np.linalg.inv(self.frame(name))

    # ---- placement helpers (assembly frame, at this pose) ----
    def at_body(self):
        return self.stance.at_body(self.s)

    def at_body_upper(self):
        return self.at_body() @ T(0, 0, self.p["body_lower_h"])

    def at_dome(self, spin=0.0):
        return self.at_body() @ T(0, 0, self.p["body_height"] + self.p["dome_gap"]) @ R(0, 0, spin)

    def at_head_drive(self):
        return self.at_body() @ T(0, 0, self.p["body_top_plate_z"])

    def at_leg(self, side):
        return self.stance.at_leg(side)

    def at_foot(self, side):
        return self.stance.at_foot(side)

    def at_carriage(self):
        return self.stance.at_carriage(self.s)

    def at_center_leg(self):
        return self.stance.at_housing(self.s)

    def at_center_foot(self, swivel=None):
        return self.stance.at_center_foot(self.s, self.caster_yaw if swivel is None else swivel)

    def print_inverse(self, name):
        return self.stance.print_inverse(name)

    def instances(self, dome_spin=0.0, caster_swivel=None):
        """Every printed piece with its assembly matrix, checked against scripts/parts.json."""
        yaw = self.caster_yaw if caster_swivel is None else caster_swivel
        parts = read_parts(self.root)
        out = []
        for inst in self.stance.instances(self.s, yaw):
            if inst["part"] not in parts:
                raise KeyError(f"stability.Stance places {inst['part']}, which scripts/parts.json does not list")
            entry = dict(inst)
            entry["stl"] = f"stl/{inst['part']}.stl"
            entry["frame"] = GROUP_FRAME[inst["group"]]
            if inst["part"] == "dome" and dome_spin:
                entry["matrix"] = self.at_dome(dome_spin) @ self.print_inverse("dome")
            out.append(entry)
        for name, row in parts.items():
            placed = sum(1 for inst in out if inst["part"] == name)
            if placed != int(row["quantity"]):
                raise RuntimeError(f"scripts/parts.json lists {row['quantity']} x {name}; "
                                   f"stability.Stance places {placed}")
        return out

    def load(self, inst):
        import trimesh
        mesh = trimesh.load_mesh(self.root / inst["stl"], process=False)
        mesh.apply_transform(inst["matrix"])
        return mesh

    # ---- purchased-part envelopes in the assembly frame ----
    def motor_matrices(self, foot_matrix, center=False):
        """4x4 matrices placing lib.scad tt_motor() (shaft along Y, body toward -X) for one foot."""
        return self.stance.motor_points(foot_matrix, center)

    def wheel_matrices(self, foot_matrix):
        """4x4 matrices placing a wheel cylinder whose axis is Z, centred (four per foot)."""
        return self.stance.wheel_matrices(foot_matrix)

    def mechanism(self):
        """Purchased stance-mechanism envelopes at this pose, as assembly-frame 4x4 matrices.

        shafts     frame at each guide shaft's lower end, +Z up the shaft (length st_shaft_t span)
        actuator   frame at the P16 fixed eye, +Z toward the eye along the guide (case below it)
        bearings   frame at each LM12LUU bottom face on the carriage, +Z up the guide
        locks      lock frame per side (origin at the pin-exit face, +X outward along the pin)
        receivers  frame at each GN 412.2 in the leg inboard face, +X along the bore
        """
        p, st = self.p, self.stance
        body = self.at_body()
        carriage = self.at_carriage()
        guide = R(p["st_guide_angle"], 0, 0)
        shafts = [body @ T(*st.guide_point(p["st_shaft_t"][0], sx * p["st_shaft_x"])) @ guide for sx in (-1, 1)]
        actuator = body @ T(*st.act_fixed_eye()) @ guide
        bearings = [carriage @ T(sx * p["st_shaft_x"], 0, p["st_brg_t"]) for sx in (-1, 1)]
        locks = {side: body @ st.lock_frame(side) for side in (-1, 1)}
        receivers = []
        for side in (-1, 1):
            for extra in (0.0, p["body_tilt"]):
                angle = math.radians(p["st_lock_angle"] + extra)
                receivers.append({"side": side, "angle_deg": extra,
                                  "matrix": st.at_leg(side) @ T(0, p["st_lock_r"] * math.cos(angle),
                                                                p["st_lock_r"] * math.sin(angle))})
        return {"shafts": shafts, "actuator": actuator, "bearings": bearings, "locks": locks,
                "receivers": receivers}

    def pose_table(self, step=0.25):
        """Stance deltas from this pose to strokes st_s_two..st_s_three, for animation."""
        ends = self.endpoints()
        count = int(math.ceil((ends["three_leg"] - ends["two_foot"]) / step))
        rows = []
        for index in range(count + 1):
            s = min(ends["two_foot"] + index * step, ends["three_leg"])
            rows.append({"s": s, "tilt": self.stance.tilt(s), "lift": self.centre_foot_lift(s),
                         "body": self.delta("body", s), "carriage": self.delta("carriage", s),
                         "housing": self.delta("housing", s), "foot": self.delta("foot", s)})
        return rows


if __name__ == "__main__":
    lay = Layout()
    ends = lay.endpoints()
    print(json.dumps({"revision": REVISION, "stance_parameter": STANCE_PARAMETER,
                      "declared_in_r2d2_scad": declared_stance_parameter(), "endpoints_mm": ends,
                      "tilt_deg": {k: round(lay.stance.tilt(v), 3) for k, v in ends.items()},
                      "counts": package_counts()}, indent=2))
    for label, stroke in ends.items():
        pose = lay.at_stroke(stroke)
        print(f"== {label}: {STANCE_PARAMETER} = {stroke:.2f} mm, tilt {pose.tilt:.2f} deg, "
              f"centre-foot lift {pose.centre_foot_lift():.1f} mm")
        for inst in pose.instances():
            path = lay.root / inst["stl"]
            if path.exists():
                lo, hi = pose.load(inst).bounds
                print(f"  {inst['name']:18s} z {lo[2]:7.1f}..{hi[2]:7.1f}  y {lo[1]:7.1f}..{hi[1]:7.1f}")
            else:
                print(f"  {inst['name']:18s} (STL not yet exported)")
