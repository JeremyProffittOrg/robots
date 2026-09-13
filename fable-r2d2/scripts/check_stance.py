"""Revision D stance-transition check: two-foot <-> three-leg, sampled both ways.

The design numbers are read from cad/params.scad (st_* and the stance section); placement and the
mass model come from scripts/stability.py, which uses the exported STL meshes. Interference is the
exact intersection volume of the meshes (manifold3d) at every sampled pose.

Failure classes (any failure exits 1). Every threshold is in CRITERIA below.
  clearance     two-foot stance lifted centre-foot wheel/shell floor clearance < min_floor_clearance_mm;
                foot at the toe stop below min_stop_clearance_mm; foot touching the floor before the
                contact stroke; lifted foot not resting on its heel stop
  support       static support margin < min_support_margin_mm in the two-foot stance, the three-leg
                stance and every transition pose where the centre foot bears load, over the body CG
                uncertainty box and the caster yaw samples
  force         actuator transition force > actuator_rating_N / actuator_safety_factor; holding load
                > actuator_backdrive_N / actuator_safety_factor
  lock          a lock not engaged at an endpoint: receiver misaligned beyond the pin clearance,
                engagement short, switch unable to sense it, release pull or release force short,
                receiver webs too thin, the unlocked body not held by the post
  interference  any printed or purchased part of the centre leg, actuator or lock intersecting the body,
                the legs or the outer feet (or each other) by more than max_interference_mm3

This is a calculated screen. It is not a physical test, a weighing or a printed-strength rating.

Usage: python scripts/check_stance.py [--poses 60] [--no-interference]
"""
from __future__ import annotations

import argparse
import json
import math
import sys
from functools import lru_cache
from pathlib import Path

import numpy as np
import trimesh

sys.path.insert(0, str(Path(__file__).resolve().parent))
import stability as stab  # noqa: E402
from assembly_layout import MX, R, T  # noqa: E402

ROOT = Path(__file__).resolve().parents[1]
REPORT = ROOT / "docs/stance-check.json"
G = 9.81
KGCM = 0.0980665

CRITERIA = {
    "poses_each_way": 60,                   # sampled strokes per direction, plus contact and both endpoints
    "min_floor_clearance_mm": 20.0,         # two-foot stance: lowest centre wheel or shell point above the floor
    "min_stop_clearance_mm": 0.0,           # two-foot stance: foot swung to the toe stop must not touch the floor
    "foot_rest_margin_mm": 2.0,             # lifted foot + housing CG at least this far behind the hinge (heel stop)
    "min_support_margin_mm": 15.0,          # CG projection inside the wheel-contact polygon
    "cg_uncertainty_mm": [8.0, 8.0, 40.0],  # body-group CG box half size, body frame X, Y, Z
    "actuator_rating_N": 300.0,             # Actuonix P16 256:1 max force lifted (datasheet Rev B)
    "actuator_backdrive_N": 500.0,          # Actuonix P16 256:1 back-drive force (datasheet Rev B)
    "actuator_safety_factor": 3.0,          # dynamic and model factor on the calculated quasi-static force
    "actuator_position_error_mm": 0.7,      # P16-100 repeatability 0.4 + backlash 0.3
    "guide_friction": 0.05,                 # LM12LUU on a hardened shaft, 10x the catalogue 0.002-0.004
    "rolling_resistance": 0.03,             # floor force / centre-foot load during the tilt phase: hard-floor rolling
                                            # resistance with the centre-foot motors driven at the kinematic ground
                                            # speed (firmware); coasting TT gearboxes are not assumed
    "hinge_friction_moment_Nmm": 150.0,     # M8 spacer-tube pitch hinge, 0.3 x 50 N x 10 mm lever, both sides
    "min_post_compression_N": 5.0,          # unlocked body must push the foot down (post never in tension)
    "pin_radial_clearance_mm": 0.1,         # (GN 412.2 bore 6.2 - GN 412 pin 6.0) / 2
    "lock_window_mm": 1.5,                  # firmware creep window either side of each receiver stroke
    "min_lock_engagement_mm": 3.0,          # half the 6 mm pin diameter
    "switch_overtravel_max_mm": 1.2,        # Omron SS-01GL OT min
    "switch_differential_mm": 0.8,          # Omron SS-01GL MD max
    "pin_release_clearance_mm": 0.5,        # pin tip clear of the receiver face after the release pull
    "min_receiver_web_mm": 2.0,             # printed web between the two receiver hex pockets
    "servo_stall_torque_Nm": 10.0 * KGCM,   # MG995 (Adafruit 1142) 10 kg-cm at 6.0 V servo supply
    "release_factor": 1.5,
    "spring_end_N": 15.0,                   # GN 412 end spring load
    "switch_force_N": 0.49,                 # Omron SS-01GL OF max
    "pin_friction": 0.10,                   # greased steel pin in the hardened GN 412.2 bushing (assumption)
    "caster_yaw_samples": "minus stop, 0, plus stop",
    "max_interference_mm3": 1.0,            # intersection volume allowed per pair (coincident contact faces)
}


# ---------------------------------------------------------------- geometry helpers
def manifold(mesh):
    import manifold3d as m3d
    mesh = mesh.copy()
    mesh.merge_vertices()
    return m3d.Manifold(m3d.Mesh(vert_properties=np.asarray(mesh.vertices, np.float32),
                                 tri_verts=np.asarray(mesh.faces, np.uint32)))


def moved(man, matrix):
    return man.transform(np.asarray(matrix, float)[:3, :])


@lru_cache(maxsize=None)
def stl_manifold(part, mirrored):
    mesh = trimesh.load_mesh(ROOT / "stl" / f"{part}.stl", process=True)
    if mirrored:
        mesh.apply_transform(MX())
    return manifold(mesh)


def box(lo, hi):
    lo, hi = np.asarray(lo, float), np.asarray(hi, float)
    return trimesh.creation.box(extents=hi - lo, transform=T(*((lo + hi) / 2)))


def cyl(p0, p1, d, sections=32):
    return trimesh.creation.cylinder(radius=d / 2, segment=[p0, p1], sections=sections)


def union(meshes):
    return trimesh.util.concatenate(meshes)


def env(meshes, matrix):
    """Purchased envelope made of primitives (each its own manifold), placed by matrix."""
    out = []
    for mesh in (meshes if isinstance(meshes, list) else [meshes]):
        mesh = mesh.copy()
        mesh.apply_transform(matrix)
        out.append(manifold(mesh))
    return out


def overlap(a_list, b_list):
    vol = 0.0
    for a in a_list:
        ab = a.bounding_box()
        for b in b_list:
            bb = b.bounding_box()
            if any(ab[i] > bb[i + 3] or bb[i] > ab[i + 3] for i in range(3)):
                continue
            vol += (a ^ b).volume()
    return vol


# ---------------------------------------------------------------- purchased envelopes (local frames)
def lock_env(p, pull, pressed, servo_angle):
    """GN 412, SS-01GL and MG995 in the lock frame (right side), matching stance.scad."""
    fl, hexl, knob = p["st_flange"], p["st_hex"], p["st_knob"]
    xh = -22 + 8.8 + p["st_switch_ot"]
    parts = {
        "plunger": [box([-fl[0], -fl[1] / 2, -fl[2] / 2], [0, fl[1] / 2, fl[2] / 2]),
                    trimesh.creation.cylinder(radius=hexl[1] / 2 / math.cos(math.pi / 6), sections=6,
                                              segment=[[-fl[0] - hexl[0], 0, 0], [-fl[0], 0, 0]])],
        "pin": [cyl([-fl[0] - hexl[0] - pull, 0, 0], [p["st_pin_ext"] - pull, 0, 0], p["st_pin_d"])],
        "knob": [cyl([-fl[0] - hexl[0] - knob[0] - pull, 0, 0], [-fl[0] - hexl[0] - pull, 0, 0], knob[1], 48)],
        "switch": [box([xh - 7.3, -3.2, 13.5], [xh + 2.9, 3.2, 33.3]),
                   box([-22 if pressed else xh - 13.6, -1.5, 10], [(-22 if pressed else xh - 13.6) + 0.3, 1.5, 24.5])],
    }
    sx = -22 + p["st_horn_rest_gap"] + p["st_horn_tip_r"] - p["st_horn_arm"][0]
    sz = -12 - p["st_horn_arm"][1]
    w, h, l, se = p["st_servo_w"], p["st_servo_h"], p["st_servo_l"], p["st_servo_shaft_end"]
    rot = T(sx, 0, sz) @ R(0, -servo_angle, 0)
    arm_len = math.hypot(*p["st_horn_arm"])
    arm_ang = math.degrees(math.atan2(p["st_horn_arm"][0], p["st_horn_arm"][1]))
    arm = box([-2.5, -1.5, 0], [2.5, 1.5, arm_len])
    arm.apply_transform(R(0, arm_ang, 0))
    tip = cyl([p["st_horn_arm"][0], -4, p["st_horn_arm"][1]], [p["st_horn_arm"][0], 4, p["st_horn_arm"][1]], 2 * p["st_horn_tip_r"], 24)
    for mesh in (arm, tip):
        mesh.apply_transform(rot)
    parts["servo"] = [box([sx - w / 2, 7, sz - (l - se)], [sx + w / 2, 7 + h, sz + se]),
                      box([sx - w / 2, 19, sz - (l - se) - 6.75], [sx + w / 2, 21.5, sz + se + 6.75])]
    parts["horn"] = [arm, tip]
    return parts


def receiver_ring(p):
    """GN 412.2 bushing reduced to the part a misaligned pin would hit: 6.2 bore in an 11 mm ring, leg frame."""
    ring = trimesh.creation.annulus(r_min=p["st_recv"][4] / 2, r_max=5.5, height=p["st_recv"][0], sections=48)
    ring.apply_transform(T(p["st_recv"][0] / 2, 0, 0) @ R(0, 90, 0))
    return ring


def wheel_meshes(stance, foot_matrix):
    p = stance.p
    return [cyl((m @ np.array([0, 0, -p["wheel_w"] / 2, 1]))[:3], (m @ np.array([0, 0, p["wheel_w"] / 2, 1]))[:3], p["wheel_d"], 48)
            for m in stance.wheel_matrices(foot_matrix)]


# ---------------------------------------------------------------- model
class Model:
    def __init__(self, overrides=None, criteria=None):
        self.p = stab.load_params(overrides=overrides)
        self.c = {**CRITERIA, **(criteria or {})}
        self.st = stab.Stance(self.p)
        self._items = {}

    # ---- mass ----
    def items(self, s, yaw=0.0):
        key = (round(s, 5), round(yaw, 3))
        if key not in self._items:
            self._items[key] = stab.mass_items(self.st, s, yaw)
        return self._items[key]

    def potential(self, s, groups):
        return sum(i["grams"] / 1000 * G * i["centre"][2] for i in self.items(s) if i["group"] in groups)

    # ---- lock state ----
    def lock_state(self, s, direction):
        p = self.p
        sc, s3 = self.st.contact_stroke(), p["st_s_three"]
        if s <= sc + 1e-9 or abs(s - s3) < 1e-9:
            return "engaged"
        return "riding"


def sample_strokes(model, n):
    p = model.p
    sc = model.st.contact_stroke()
    base = np.linspace(p["st_s_two"], p["st_s_three"], n)
    extra = [p["st_s_two"], sc, sc + 0.05, p["st_s_three"] - 0.05, p["st_s_three"]]
    return sorted(set(np.round(np.concatenate([base, extra]), 5).tolist()))


def evaluate(overrides=None, criteria=None, poses_each_way=None, interference=True):
    model = Model(overrides, criteria)
    p, c, st = model.p, model.c, model.st
    failures = []

    def fail(cls, check, value, limit, s=None, detail=None):
        failures.append({"class": cls, "check": check, "value": round(float(value), 4), "limit": round(float(limit), 4),
                         "stroke_mm": None if s is None else round(float(s), 3), "detail": detail})

    n = int(poses_each_way or c["poses_each_way"])
    strokes = sample_strokes(model, n)
    sc, s2, s3 = st.contact_stroke(), p["st_s_two"], p["st_s_three"]
    yaws = [-p["caster_stop_deg"], 0.0, p["caster_stop_deg"]]
    ux, uy, uz = c["cg_uncertainty_mm"]
    summary = {"contact_stroke_mm": sc, "two_foot_stroke_mm": s2, "three_leg_stroke_mm": s3,
               "three_leg_tilt_deg": st.tilt(s3), "guide_angle_deg": p["st_guide_angle"]}

    # ------------------------------------------------ lock geometry and endpoint engagement
    r = p["st_lock_r"]
    s_align3 = st.stroke_for_tilt(p["body_tilt"])
    for label, s_end, tilt_target in (("two-foot", s2, 0.0), ("three-leg", s3, p["body_tilt"])):
        err = r * math.radians(abs(st.tilt(s_end) - tilt_target))
        summary[f"{label}_receiver_misalignment_mm"] = err
        if err > c["pin_radial_clearance_mm"]:
            fail("lock", f"{label} endpoint: receiver aligned with the pin", err, c["pin_radial_clearance_mm"], s_end)
    window_need = abs(s_align3 - s3) + c["actuator_position_error_mm"]
    summary["three_leg_alignment_stroke_mm"] = s_align3
    if window_need > c["lock_window_mm"]:
        fail("lock", "three-leg receiver inside the creep window", window_need, c["lock_window_mm"], s3)
    if not s2 < sc:
        fail("lock", "two-foot endpoint is a locked lifted pose (s_two < contact)", s2, sc, s2)
    engagement = p["st_pin_ext"] - p["st_land_gap"]
    summary["pin_engagement_mm"] = engagement
    if not c["min_lock_engagement_mm"] <= engagement <= p["st_recv"][0]:
        fail("lock", "pin engagement in the receiver", engagement, c["min_lock_engagement_mm"])
    press = p["st_switch_ot"] + p["st_switch_adj"]
    if press > c["switch_overtravel_max_mm"] or p["st_switch_ot"] - p["st_switch_adj"] <= 0:
        fail("lock", "switch set overtravel within the SS-01GL rating", press, c["switch_overtravel_max_mm"])
    sensed = engagement - (press + c["switch_differential_mm"])
    summary["sensed_minimum_engagement_mm"] = sensed
    if sensed < c["min_lock_engagement_mm"]:
        fail("lock", "switch reads engaged only with sufficient engagement", sensed, c["min_lock_engagement_mm"])
    if p["st_release_pull"] < engagement + c["pin_release_clearance_mm"] or p["st_release_pull"] > p["st_pin_ext"]:
        fail("lock", "release pull clears the receiver inside the plunger stroke", p["st_release_pull"],
             engagement + c["pin_release_clearance_mm"])
    chord = 2 * r * math.sin(math.radians(p["body_tilt"] / 2))
    web = chord - (p["st_recv"][2] + 0.3)
    summary["receiver_web_mm"] = web
    if web < c["min_receiver_web_mm"]:
        fail("lock", "printed web between the receiver hex pockets", web, c["min_receiver_web_mm"])
    # servo force at the horn tip (worst lever over the release rotation)
    R_h = math.hypot(*p["st_horn_arm"])
    d0 = math.atan2(p["st_horn_arm"][1], p["st_horn_arm"][0])
    rel = math.acos((p["st_horn_arm"][0] - p["st_release_pull"] - p["st_horn_rest_gap"]) / R_h) - d0
    summary["release_angle_deg"] = math.degrees(rel)
    lever = max(R_h * abs(math.sin(d0 + b)) for b in np.linspace(0, rel, 20))
    servo_force = c["servo_stall_torque_Nm"] / (lever / 1000)
    events = []
    for label, s_rel in (("release at contact (deploy)", sc), ("release at three-leg (retract)", s3)):
        items = model.items(s_rel)
        body = [i for i in items if i["group"] in ("body", "carriage")]
        mass = sum(i["grams"] for i in body) / 1000
        cg = sum(i["grams"] * i["centre"] for i in body) / (mass * 1000)
        t = math.radians(st.tilt(s_rel))
        worst_y = max(abs(cg[1] + a * (uy * math.cos(t) - b * uz * math.sin(t)))
                      for a in (-1, 1) for b in (-1, 1))
        torque = mass * G * worst_y / 1000
        shear = torque / (2 * r / 1000)
        need = c["release_factor"] * (c["spring_end_N"] + c["switch_force_N"] + c["pin_friction"] * shear)
        events.append({"event": label, "stroke_mm": s_rel, "body_torque_Nm": torque, "pin_shear_each_N": shear,
                       "factored_release_force_N": need, "servo_tip_force_N": servo_force})
        if need > servo_force:
            fail("lock", f"release force ({label}) within the MG995 stall force", need, servo_force, s_rel)

    # ------------------------------------------------ heel stop and floor clearance
    foot_items = [i for i in model.items(s2) if i["group"] in ("housing", "foot")]
    fm = sum(i["grams"] for i in foot_items)
    fcg = sum(i["grams"] * i["centre"] for i in foot_items) / fm
    behind = st.hinge_world(s2)[1] - fcg[1]
    summary["lifted_foot_cg_behind_hinge_mm"] = behind
    if behind < c["foot_rest_margin_mm"]:
        fail("clearance", "lifted foot rests on the heel stop (CG behind the hinge)", behind, c["foot_rest_margin_mm"], s2)
    foot_mesh = trimesh.load_mesh(ROOT / "stl/foot_center.stl", process=False)

    def lowest(s, yaw, pitch=0.0):
        m = st.at_center_foot(s, yaw, pitch)
        shell = float((foot_mesh.vertices @ m[:3, :3].T + m[:3, 3])[:, 2].min())
        wheels = min(float((w @ np.array([0, 0, 0, 1]))[2]) - p["wheel_d"] / 2 for w in st.wheel_matrices(m))
        return min(shell, wheels)

    rest = min(lowest(s2, y) for y in yaws)
    toe = min(lowest(s2, y, -p["st_toe_stop"]) for y in yaws)
    summary["two_foot_floor_clearance_mm"] = rest
    summary["two_foot_toe_stop_clearance_mm"] = toe
    if rest < c["min_floor_clearance_mm"]:
        fail("clearance", "two-foot stance lifted centre-foot floor clearance", rest, c["min_floor_clearance_mm"], s2)
    if toe < c["min_stop_clearance_mm"]:
        fail("clearance", "two-foot stance foot at the toe stop clears the floor", toe, c["min_stop_clearance_mm"], s2)

    # ------------------------------------------------ sampled transition
    rows = []
    extrema = {"min_two_foot_margin_mm": math.inf, "min_three_leg_margin_mm": math.inf, "min_loaded_margin_mm": math.inf,
               "max_actuator_force_N": 0.0, "max_holding_load_N": 0.0, "min_post_compression_N": math.inf,
               "max_interference_mm3": 0.0}
    lever_guide = 1 + 2 * (p["st_brg_t"] + p["st_brg"][2] / 2) / p["st_brg"][2]
    moving_lifted = ("carriage", "housing", "foot")
    moving_floor = ("body", "carriage")
    h = 0.02
    for direction in ("deploy", "retract"):
        seq = strokes if direction == "deploy" else strokes[::-1]
        sign = 1 if direction == "deploy" else -1
        for s in seq:
            tilt = st.tilt(s)
            loaded = st.on_floor(s)
            items = model.items(s)
            total = sum(i["grams"] for i in items)
            row = {"direction": direction, "stroke_mm": round(s, 4), "body_tilt_deg": round(tilt, 4),
                   "centre_foot_loaded": loaded, "lock": model.lock_state(s, direction),
                   "hinge_world_mm": [round(float(v), 2) for v in st.hinge_world(s)]}
            if not loaded and s > s2 + 1e-9:
                low = lowest(s, 0.0)
                row["centre_floor_clearance_mm"] = round(low, 3)
                if low < -1e-3:
                    fail("clearance", "lifted foot touches the floor before the contact stroke", low, 0.0, s)
            # support
            t = math.radians(tilt)
            body_mass = sum(i["grams"] for i in items if i["group"] in ("body", "carriage"))
            margins = []
            for yaw in (yaws if loaded else [0.0]):
                its = model.items(s, yaw) if yaw else items
                _, cg = stab.centre_of_gravity(its)
                outer, centre = st.contacts(s, yaw)
                pts = np.vstack([outer, centre]) if len(centre) else outer
                for dx in (-ux, ux):
                    for dy in (-uy, uy):
                        for dz in (-uz, uz):
                            shift = np.array([dx, dy * math.cos(t) - dz * math.sin(t)]) * body_mass / total
                            margins.append(stab.polygon_margin(pts, cg[:2] + shift))
            margin = min(margins)
            row["support_margin_mm"] = round(margin, 3)
            key = "min_loaded_margin_mm" if loaded else "min_two_foot_margin_mm"
            extrema[key] = min(extrema[key], margin)
            if abs(s - s3) < 1e-9:
                extrema["min_three_leg_margin_mm"] = margin
            if (loaded or abs(s - s2) < 1e-9 or s <= sc) and margin < c["min_support_margin_mm"]:
                stance_label = "three-leg stance" if abs(s - s3) < 1e-9 else ("two-foot stance" if not loaded else "loaded transition pose")
                fail("support", f"static support margin, {stance_label}", margin, c["min_support_margin_mm"], s)
            # actuator force by virtual work
            groups = moving_floor if loaded else moving_lifted
            lo, hi = (s - h, s) if (s >= s3 - 1e-9 or (loaded and s - h > sc)) else (s, s + h)
            dE = (model.potential(hi, groups) - model.potential(lo, groups)) / (hi - lo)   # N (N.mm / mm)
            hinge_lo, hinge_hi = st.hinge_world(lo), st.hinge_world(hi)
            dy = (hinge_hi[1] - hinge_lo[1]) / (hi - lo)
            u_world = (R(tilt, 0, 0)[:3, :3] @ st.u)
            if loaded:
                body_items = [i for i in items if i["group"] in moving_floor]
                hw = st.hinge_world(s)
                lever_y = hw[1]
                compression = []
                for drag_sign in (-1, 1):
                    k = drag_sign * c["rolling_resistance"]
                    for dyc in (-uy, uy):
                        for dzc in (-uz, uz):
                            shift_y = dyc * math.cos(t) - dzc * math.sin(t)
                            moment = sum(i["grams"] / 1000 * G * (i["centre"][1] + shift_y) for i in body_items)
                            # moments about the shoulder axis with floor force F_y = k R on the hinge:
                            #   y_h R - (z_h - S) k R - sum(m g y) = 0
                            denom = lever_y - (hw[2] - st.S) * k
                            compression.append(moment / denom if denom > 0 else -math.inf)
                reaction = max(compression)
                post = min(compression)
                extrema["min_post_compression_N"] = min(extrema["min_post_compression_N"], post)
                row["post_compression_N"] = round(post, 3)
                if abs(s - s3) > 1e-9 and post < c["min_post_compression_N"]:
                    fail("lock", "unlocked body held by the post (post in compression)", post, c["min_post_compression_N"], s)
                drag = c["rolling_resistance"] * max(reaction, 0.0)
                force_vec = np.array([0.0, drag, max(reaction, 0.0)])
                drag_work = drag * abs(dy)
            else:
                hanging = sum(i["grams"] for i in items if i["group"] in moving_lifted) / 1000 * G
                force_vec = np.array([0.0, 0.0, hanging])
                drag_work = 0.0
            perp = np.linalg.norm(force_vec - (force_vec @ u_world) * u_world)
            hinge_rate = math.radians(abs(st.tilt(hi) - st.tilt(lo)) / (hi - lo))
            friction = c["guide_friction"] * perp * lever_guide + c["hinge_friction_moment_Nmm"] * hinge_rate
            force = abs(dE) + drag_work + friction          # gravity, drag and friction all taken as opposing
            holding = abs(dE)
            row.update({"actuator_force_N": round(force, 3), "holding_load_N": round(holding, 3)})
            extrema["max_actuator_force_N"] = max(extrema["max_actuator_force_N"], force)
            extrema["max_holding_load_N"] = max(extrema["max_holding_load_N"], holding)
            limit = c["actuator_rating_N"] / c["actuator_safety_factor"]
            if force > limit:
                fail("force", "actuator transition force within rating / safety factor", force, limit, s)
            hold_limit = c["actuator_backdrive_N"] / c["actuator_safety_factor"]
            if holding > hold_limit:
                fail("force", "holding load within back-drive force / safety factor", holding, hold_limit, s)
            rows.append(row)

    # ------------------------------------------------ interference
    inter_rows = []
    if interference:
        inter_rows = interference_scan(model, strokes, yaws, fail, extrema)
    summary.update({k: (None if v in (math.inf, -math.inf) else v) for k, v in extrema.items()})
    return {"passed": not failures, "failures": failures, "summary": summary, "lock_events": events,
            "rows": rows, "interference": inter_rows, "criteria": c, "samples": len(rows)}


def interference_scan(model, strokes, yaws, fail, extrema):
    p, c, st = model.p, model.c, model.st
    tol = c["max_interference_mm3"]
    body_lower = stl_manifold("body_lower", False)
    body_upper = stl_manifold("body_upper", False)
    carriage = stl_manifold("leg_carriage", False)
    housing = stl_manifold("leg_center", False)
    foot = stl_manifold("foot_center", False)
    legs, feet = [], []
    for side in (1, -1):
        # A left-side placement M has determinant -1. The mesh is mirrored once (stl_manifold) and
        # placed by the rigid M @ MX, which maps mirrored vertices exactly as M maps the originals.
        mirrored = side < 0
        fix = MX() if mirrored else np.eye(4)
        for part in ("leg_upper", "leg_lower"):
            legs.append(moved(stl_manifold(part, mirrored), st.at_leg(side) @ st.print_inverse(part) @ fix))
        feet.append(moved(stl_manifold("foot_outer", mirrored), st.at_foot(side) @ fix))
        feet += env(wheel_meshes(st, np.eye(4)), st.at_foot(side))
    receivers = []
    la = math.radians(p["st_lock_angle"])
    for side in (1, -1):
        for extra in (0.0, p["body_tilt"]):
            ang = la + math.radians(extra)
            receivers += env([receiver_ring(p)], st.at_leg(side) @ T(0, p["st_lock_r"] * math.cos(ang), p["st_lock_r"] * math.sin(ang)))
    y0 = p["battery_y"]
    # 12 V 7 Ah SLA on its side, plus the F2 terminal and spade zone (20 mm) on the +Y face within |x| <= 50
    battery = [box([-p["battery"][0] / 2, y0 - p["battery"][1] / 2, p["battery_shelf_z"]],
                   [p["battery"][0] / 2, y0 + p["battery"][1] / 2, p["battery_shelf_z"] + p["battery"][2]]),
               box([-50, y0 + p["battery"][1] / 2, p["battery_shelf_z"]],
                   [50, y0 + p["battery"][1] / 2 + 20, p["battery_shelf_z"] + p["battery"][2]])]
    a = st.act_fixed_eye()
    guide = T(*a) @ R(p["st_guide_angle"], 0, 0)
    case = [box([-p["st_act_case"][0] / 2, -p["st_act_case"][1] / 2, -p["st_act_case_t"][1]],
                [p["st_act_case"][0] / 2, p["st_act_case"][1] / 2, -p["st_act_case_t"][0]])]
    case[0].apply_transform(guide)
    shafts = [cyl(st.guide_point(p["st_shaft_t"][0], sx * p["st_shaft_x"]), st.guide_point(p["st_shaft_t"][1], sx * p["st_shaft_x"]),
                  p["st_shaft_d"], 48) for sx in (-1, 1)]
    body_static_local = case + shafts + battery          # body frame
    rows = []
    cache = {}

    def record(pair, s, yaw, vol, state=""):
        extrema["max_interference_mm3"] = max(extrema["max_interference_mm3"], vol)
        rows.append({"pair": pair, "stroke_mm": round(s, 3), "yaw_deg": yaw, "lock": state, "volume_mm3": round(vol, 3)})
        if vol > tol:
            fail("interference", pair, vol, tol, s, f"yaw {yaw}, lock {state}")

    # static seam pair (body frame)
    record("body_lower / body_upper", p["st_s_two"], 0.0, overlap([body_lower], [moved(body_upper, T(0, 0, p["body_lower_h"]))]))
    seam_upper = moved(body_upper, T(0, 0, p["body_lower_h"]))
    lock_states = {"engaged": (0.0, True, 0.0), "riding": (p["st_pin_ext"] - p["st_land_gap"], False, 0.0),
                   "pulled": (p["st_release_pull"], False, None)}
    rel_angle = math.degrees(math.acos((p["st_horn_arm"][0] - p["st_release_pull"] - p["st_horn_rest_gap"]) / math.hypot(*p["st_horn_arm"]))
                             - math.atan2(p["st_horn_arm"][1], p["st_horn_arm"][0]))
    for state, (pull, pressed, angle) in lock_states.items():
        parts = lock_env(p, pull, pressed, rel_angle if angle is None else angle)
        for side in (1, -1):
            lf = st.lock_frame(side)
            placed = {k: env(v, lf) for k, v in parts.items()}
            everything = [m for v in placed.values() for m in v]
            record(f"lock {side:+d} ({state}) / body_upper", p["st_s_two"], 0.0, overlap(everything, [seam_upper]))
            record(f"lock {side:+d} ({state}) knob / horn + switch", p["st_s_two"], 0.0,
                   overlap(placed["knob"], placed["switch"] + placed["servo"]) + overlap(placed["plunger"], placed["horn"] + placed["switch"]))
    body_env_local = [manifold(m) for m in body_static_local]
    record("actuator case + shafts / battery", p["st_s_two"], 0.0, overlap(body_env_local[:3], body_env_local[3:]))
    record("actuator case + shafts + battery / body_lower + body_upper", p["st_s_two"], 0.0,
           overlap(body_env_local, [body_lower, seam_upper]))
    carriage_local_parts = {}
    for s in strokes:
        tilt = st.tilt(s)
        body_m = st.at_body(s)
        car_local = st.print_inverse("leg_carriage")
        car_body = T(*st.hinge_body(s)) @ R(p["st_guide_angle"], 0, 0)          # carriage frame in the body frame
        car = moved(carriage, car_body @ car_local)
        rod = env([cyl([0, 0, p["st_eye_up"] + p["st_act_eye_d"] / 2], [0, 0, p["st_eye_up"] + p["st_act_closed"] + s - p["st_act_case_t"][1]], p["st_act_rod_d"]),
                   trimesh.creation.cylinder(radius=p["st_act_eye_d"] / 2, segment=[[-p["st_act_eye_w"] / 2, 0, p["st_eye_up"]], [p["st_act_eye_w"] / 2, 0, p["st_eye_up"]]], sections=32)],
                  car_body)
        # body-frame pairs (depend on s only)
        record("leg_carriage / body_lower + body_upper", s, 0.0, overlap([car], [body_lower, seam_upper]))
        record("leg_carriage / actuator case + shafts + battery", s, 0.0, overlap([car], body_env_local))
        record("actuator rod / body_lower + battery", s, 0.0, overlap(rod[:1], [body_lower] + body_env_local[3:]))
        # housing: world-level, expressed in the body frame
        to_body = np.linalg.inv(body_m)
        hous = moved(housing, to_body @ st.at_housing(s) @ st.print_inverse("leg_center"))
        record("leg_center / body_lower", s, 0.0, overlap([hous], [body_lower]))
        record("leg_center / leg_carriage", s, 0.0, overlap([hous], [car]))
        # centre foot and its wheels, world frame, every yaw sample
        world_body = [moved(body_lower, body_m), moved(seam_upper, body_m)]
        car_w = moved(car, body_m)
        for yaw in yaws:
            fm = st.at_center_foot(s, yaw)
            foot_parts = [moved(foot, fm)] + env(wheel_meshes(st, np.eye(4)), fm)
            record("centre foot + wheels / body + carriage", s, yaw, overlap(foot_parts, world_body + [car_w]))
            record("centre foot + wheels / legs + outer feet", s, yaw, overlap(foot_parts, legs + feet))
            record("centre foot / leg_center", s, yaw, overlap(foot_parts[:1], [moved(housing, st.at_housing(s) @ st.print_inverse("leg_center"))]))
        # body rings and lock hardware against the legs (depends on tilt)
        key = round(tilt, 4)
        state = model.lock_state(s, "deploy")
        if (key, state) not in cache:
            pull, pressed, angle = lock_states[state]
            parts = lock_env(p, pull, pressed, angle)
            lock_world = []
            pins = []
            for side in (1, -1):
                lf = body_m @ st.lock_frame(side)
                for name, meshes in parts.items():
                    placed = env(meshes, lf)
                    (pins if name == "pin" else lock_world).extend(placed)
            vol_body = overlap(world_body, legs + feet)
            vol_lock = overlap(lock_world, legs)
            vol_pin = overlap(pins, legs[0:1] + legs[2:3] + receivers)
            cache[(key, state)] = (vol_body, vol_lock, vol_pin)
        vol_body, vol_lock, vol_pin = cache[(key, state)]
        record("body_lower + body_upper / legs + outer feet", s, 0.0, vol_body, state)
        record("lock hardware / legs", s, 0.0, vol_lock, state)
        record("lock pins / leg_upper + receivers", s, 0.0, vol_pin, state)
    return rows


def _jsonable(value):
    if isinstance(value, dict):
        return {k: _jsonable(v) for k, v in value.items()}
    if isinstance(value, (list, tuple)):
        return [_jsonable(v) for v in value]
    if isinstance(value, (np.floating, np.integer)):
        return value.item()
    if isinstance(value, np.bool_):
        return bool(value)
    if isinstance(value, np.ndarray):
        return [_jsonable(v) for v in value.tolist()]
    if isinstance(value, float):
        return round(value, 5)
    return value


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--poses", type=int, default=None, help="strokes sampled per direction")
    parser.add_argument("--no-interference", action="store_true")
    args = parser.parse_args()
    result = evaluate(poses_each_way=args.poses, interference=not args.no_interference)
    s = result["summary"]
    report = {"revision": "D", "configuration": "legs vertical; body pitches 0 <-> body_tilt about the shoulders; centre leg "
              "deployed forward-down on two 12 mm shafts by an Actuonix P16-100; sensed GN 412 lock on both shoulders",
              "passed": result["passed"], "physical_tested": False, "printed_strength_verified": False,
              "design_source": ["cad/params.scad", "cad/stance.scad", "scripts/stability.py"],
              "criteria": result["criteria"], "summary": s, "lock_events": result["lock_events"],
              "failures": result["failures"], "samples": result["samples"], "rows": result["rows"],
              "interference": [r for r in result["interference"] if r["volume_mm3"] > 0.0] if result["interference"] else [],
              "interference_pairs_checked": len(result["interference"])}
    REPORT.write_text(json.dumps(_jsonable(report), indent=1) + "\n", encoding="utf-8")
    c = result["criteria"]
    print(f"Samples: {result['samples']} poses ({c['poses_each_way'] if args.poses is None else args.poses} strokes each way plus contact and endpoints); "
          f"interference pairs checked: {len(result['interference'])}")
    print(f"Strokes: two-foot {s['two_foot_stroke_mm']:.2f} mm, contact {s['contact_stroke_mm']:.2f} mm, three-leg {s['three_leg_stroke_mm']:.2f} mm "
          f"(tilt {s['three_leg_tilt_deg']:.3f} deg)")
    print(f"Clearance: two-foot wheels {s['two_foot_floor_clearance_mm']:.2f} mm (min {c['min_floor_clearance_mm']}), "
          f"toe stop {s['two_foot_toe_stop_clearance_mm']:.2f} mm; lifted foot CG {s['lifted_foot_cg_behind_hinge_mm']:.1f} mm behind the hinge")
    print(f"Support margin: two-foot {s['min_two_foot_margin_mm']:.2f} mm, three-leg {s['min_three_leg_margin_mm']:.2f} mm, "
          f"loaded transition minimum {s['min_loaded_margin_mm']:.2f} mm (min {c['min_support_margin_mm']})")
    print(f"Actuator: max {s['max_actuator_force_N']:.1f} N (limit {c['actuator_rating_N'] / c['actuator_safety_factor']:.1f}), "
          f"holding {s['max_holding_load_N']:.1f} N (limit {c['actuator_backdrive_N'] / c['actuator_safety_factor']:.1f}), "
          f"post compression min {s['min_post_compression_N']:.1f} N")
    print(f"Lock: engagement {s['pin_engagement_mm']:.2f} mm, sensed minimum {s['sensed_minimum_engagement_mm']:.2f} mm, "
          f"three-leg misalignment {s['three-leg_receiver_misalignment_mm']:.3f} mm, receiver web {s['receiver_web_mm']:.2f} mm, "
          f"release angle {s['release_angle_deg']:.1f} deg")
    for e in result["lock_events"]:
        print(f"Lock {e['event']}: factored {e['factored_release_force_N']:.1f} N <= servo {e['servo_tip_force_N']:.1f} N")
    print(f"Interference: max {s['max_interference_mm3']:.3f} mm3 (limit {c['max_interference_mm3']})")
    if result["failures"]:
        seen = set()
        for f in result["failures"]:
            key = (f["class"], f["check"])
            if key not in seen:
                seen.add(key)
                print(f"FAIL [{f['class']}] {f['check']}: {f['value']} vs {f['limit']} at stroke {f['stroke_mm']} {f['detail'] or ''}")
        print("NOT ACCEPTED: see docs/stance-check.json")
        return 1
    print("PASS: calculated stance-transition screen. Physical mass, CG, friction, strength and lock tests remain required.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
