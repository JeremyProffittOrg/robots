"""Revision D centre-leg transition screen: two-foot <-> three-foot, sampled finely.

Failure classes (any failure exits 1):
  clearance   lifted centre-foot floor clearance, stop feasibility
  support     two-foot and three-foot static support margin over a CG uncertainty box
  force       actuator transition and holding load, lock-release load, against ratings with factors
  restraint   lock alignment, engagement depth, sensing and body hold at both endpoints and while unlocked
  kinematics  stroke, guide engagement and mechanism consistency
  geometry    mechanism STL meshes are closed single solids

Design numbers are parsed from cad/kinematics.scad (stance kinematics) and cad/stance-lock-sensed.scad
(SL_ constants of the sensed GN 412 lock), so the CAD and this check share one source.
This is a calculated screen. It is not a physical test, a weighing or a printed-strength rating.
"""
from __future__ import annotations

import json
import math
import re
import sys
from functools import lru_cache
from itertools import product
from pathlib import Path

import numpy as np
import trimesh
from scipy.spatial import ConvexHull

ROOT = Path(__file__).resolve().parents[1]
SCAD = ROOT / 'cad/kinematics.scad'
LOCK_SCAD = ROOT / 'cad/stance-lock-sensed.scad'
REPORT = ROOT / 'cad/kinematic-check.json'
G = 9.81
KGCM_TO_NM = 0.0980665

# Stated acceptance criteria and catalogue ratings. Each source is named in docs/revision-d-mechanism.md.
CRITERIA = {
    'sample_step_mm': 0.25,
    'min_floor_clearance_mm': 20.0,         # resting lifted foot above a flat floor
    'min_any_stop_clearance_mm': 0.0,       # foot pushed to either ankle stop must still clear the floor
    'min_support_margin_mm': 10.0,          # CG projection inside the support polygon
    'cg_uncertainty_mm': (8.0, 8.0, 40.0),  # body-group CG box half-size, body X/Y/Z
    'min_body_hold_mm': 0.0,                # unlocked body CG must stay ahead of the hip
    'foot_rest_margin_mm': 1.0,             # centre-foot CG must be this far behind the ankle
    'actuator_moving_rating_N': 300.0,      # Actuonix P16 datasheet, max force lifted
    'actuator_backdrive_N': 500.0,          # Actuonix P16 datasheet, back drive force
    'actuator_position_error_mm': 0.7,      # P16-100 repeatability 0.4 + backlash 0.3
    'dynamic_factor': 3.0,
    'guide_friction': 0.35,                 # assumed PETG land on anodised 2020, not a measured value
    'rolling_drag_N': 10.0,                 # commissioning ceiling for the centre-foot wheels
    'servo_stall_torque_kgcm': 8.5,         # MG995, Adafruit 1142 at 4.8 V
    'release_factor': 1.5,
    'pin_friction': 0.3,                    # assumed steel pin in hardened bushing
    'spring_start_N': 5.0,                  # GN 412 initial spring load
    'spring_end_N': 15.0,                   # GN 412 end spring load
    'switch_operating_force_N': 0.49,       # Omron SS-01GL OF max
    'switch_overtravel_mm': 1.2,            # Omron SS-01GL OT min
    'switch_differential_mm': 0.8,          # Omron SS-01GL MD max
    'pin_radial_clearance_mm': 0.1,         # (GN 412.2 bore 6.2 min - GN 412 pin 6.0 max) / 2
    'min_lock_engagement_mm': 3.0,          # half the 6 mm pin diameter
    'min_receiver_web_mm': 2.0,
    'pin_release_clearance_mm': 0.5,
    'max_rail_top_z_mm': 450.0,             # below the dome ring at 456.8 mm
}

REQUIRED = '''HIP_Z ANKLE_Z SIDE_FOOT_X WHEEL_ROW_Y WHEEL_AXLE_X WHEEL_CONTACT_X WHEEL_AXLE_Z WHEEL_RADIUS
GUIDE_ANGLE GUIDE_Y GUIDE_Z GUIDE_LENGTH GUIDE_LAND_A GUIDE_LAND_B GUIDE_LAND_LENGTH
POST_ZERO POST_STROKE POST_MIN POST_MAX POST_RAIL POST_RAIL_END ACTUATOR_Y ACTUATOR_FIXED_PIN ACTUATOR_CLOSED
CENTER_YAW_LIMIT ANKLE_STOP_HEEL ANKLE_STOP_TOE BATTERY_X BATTERY_Y BATTERY_Z
ELECTRONICS_X ELECTRONICS_Y ELECTRONICS_Z'''.split()
LOCK_REQUIRED = '''SL_LOCK_RADIUS SL_LOCK_PIN_ANGLE SL_LOCK_RECEIVER_TWO_FOOT SL_LOCK_RECEIVER_THREE_FOOT
SL_LOCK_PIN_EXIT_X SL_LOCK_RING_FACE_X SL_LOCK_PIN_EXTENSION SL_LOCK_BUSHING_LENGTH SL_LOCK_BUSHING_OD
SL_LOCK_RING_INNER SL_LOCK_RING_OUTER SL_LOCK_RING_ARC_START SL_LOCK_RING_ARC_END SL_LOCK_SWITCH_OVERTRAVEL
SL_LOCK_SWITCH_ADJUST SL_LOCK_KNOB_SEAT_X SL_RELEASE_PIVOT_X SL_RELEASE_PIVOT_Z SL_RELEASE_FINGER_X
SL_RELEASE_FINGER_Z SL_RELEASE_ROTATION'''.split()


def parse_constants(text: str, required=REQUIRED, source='cad/kinematics.scad') -> dict:
    values = {m.group(1): float(m.group(2)) for m in
              re.finditer(r'^\s*([A-Z][A-Z0-9_]*)\s*=\s*(-?\d+(?:\.\d+)?)\s*;', text, re.M)}
    missing = [k for k in required if k not in values]
    if missing:
        raise ValueError(f'{source} is missing literal constants: ' + ', '.join(missing))
    return values


def load_design(path: Path = SCAD, lock_path: Path = LOCK_SCAD) -> dict:
    design = parse_constants(path.read_text(encoding='utf-8'))
    lock = parse_constants(lock_path.read_text(encoding='utf-8'), LOCK_REQUIRED, 'cad/stance-lock-sensed.scad')
    design.update({k: v for k, v in lock.items() if k.startswith('SL_')})
    return design


# ---------------------------------------------------------------- kinematics
def rot_x(deg: float) -> np.ndarray:
    a = math.radians(deg)
    return np.array([[1, 0, 0], [0, math.cos(a), -math.sin(a)], [0, math.sin(a), math.cos(a)]])


def guide_axes(d: dict):
    a = math.radians(d['GUIDE_ANGLE'])
    # Columns are guide-local X, Y, Z in body coordinates; local Z points forward-down along the post.
    return np.array([[1, 0, 0], [0, math.cos(a), math.sin(a)], [0, math.sin(a), -math.cos(a)]])


def contact_stroke(d: dict) -> float:
    return (d['GUIDE_Z'] - d['ANKLE_Z']) / math.cos(math.radians(d['GUIDE_ANGLE'])) - d['POST_ZERO']


def pose(d: dict, s: float) -> dict:
    """Body pitch (deg, positive leans back), ankle position and lift for stroke s with the shoulders free."""
    a_rad = math.radians(d['GUIDE_ANGLE'])
    length = d['POST_ZERO'] + s
    a = d['GUIDE_Y'] + length * math.sin(a_rad)
    b = d['HIP_Z'] - d['GUIDE_Z'] + length * math.cos(a_rad)
    drop = d['HIP_Z'] - d['ANKLE_Z']
    on_floor = s >= contact_stroke(d)
    theta = math.acos(drop / math.hypot(a, b)) - math.atan2(a, b) if on_floor else 0.0
    ankle_y = a * math.cos(theta) + b * math.sin(theta)
    ankle_z = d['HIP_Z'] + a * math.sin(theta) - b * math.cos(theta)
    return {'theta_deg': math.degrees(theta), 'on_floor': on_floor, 'ankle_y': ankle_y,
            'ankle_z': max(ankle_z, d['ANKLE_Z']), 'lift': max(0.0, ankle_z - d['ANKLE_Z']), 'length': length}


# ---------------------------------------------------------------- mass model
PRINT_DENSITY = {'PETG': 1.27, 'PLA': 1.24}
# Sliced installed-model mass / solid mesh mass for the revision C whole prints (cad/h2d-structure-check.json,
# 0.4 mm nozzle, 4 walls, 20 % gyroid). Development prints are not sliced yet; they use DEVELOPMENT_FILL.
DEVELOPMENT_FILL = 0.5


@lru_cache(maxsize=None)
def mesh_properties(path: str):
    mesh = trimesh.load_mesh(path, process=True)
    return float(mesh.volume), np.array(mesh.center_mass), mesh.vertices.copy()


@lru_cache(maxsize=None)
def sliced_fill_ratios():
    rows = json.loads((ROOT / 'cad/h2d-structure-check.json').read_text())['rows']
    ratios = {}
    for row in rows:
        name = Path(row['part']).stem
        volume, _, _ = mesh_properties(str(ROOT / row['part']))
        density = PRINT_DENSITY[row['material']]
        ratios[name] = row['installed_model_g'] / (volume / 1000 * density)
    return ratios


def _matrix(rotation=np.eye(3), translation=(0, 0, 0)):
    m = np.eye(4)
    m[:3, :3] = rotation
    m[:3, 3] = translation
    return m


def _rz(deg):
    a = math.radians(deg)
    return np.array([[math.cos(a), -math.sin(a), 0], [math.sin(a), math.cos(a), 0], [0, 0, 1]])


def _ry(deg):
    a = math.radians(deg)
    return np.array([[math.cos(a), 0, math.sin(a)], [0, 1, 0], [-math.sin(a), 0, math.cos(a)]])


MIRROR_X = np.diag([-1.0, 1.0, 1.0])


def printed_parts(d: dict):
    """(label, STL, material, fill source, group, STL->group transform) for every installed print."""
    leg_bed = _matrix(_ry(90) @ _rz(-45)) @ _matrix(translation=(0, 0, -20))
    adapter_bed = _matrix(rot_x(-90)) @ _matrix(translation=(0, 0, -29))
    parts = [
        ('frame chassis', 'stl/development/frame_chassis.stl', 'PETG', None, 'body', _matrix(translation=(0, 0, 166))),
        ('body lower shell', 'stl/body_lower.stl', 'PETG', 'body_lower', 'body', _matrix(translation=(0, 0, 130))),
        ('body upper shell', 'stl/body_upper.stl', 'PETG', 'body_upper', 'body', _matrix(translation=(0, 0, 269.7))),
        ('dome', 'stl/dome.stl', 'PLA', 'dome', 'body', _matrix(translation=(0, 0, 441.8))),
        ('bearing cap', 'stl/bearing_cap.stl', 'PETG', 'bearing_cap', 'body', _matrix(translation=(0, 0, 441))),
        ('knob collar', 'stl/development/sl_knob_collar.stl', 'PETG', None, 'body', None),
        ('release lever', 'stl/development/sl_release_lever.stl', 'PETG', None, 'body', None),
        ('post adapter', 'stl/development/post_adapter.stl', 'PETG', None, 'post', adapter_bed),
        ('centre foot core', 'stl/development/center_foot_core.stl', 'PETG', None, 'foot', _matrix(translation=(0, 0, 12))),
        ('centre foot cover', 'stl/rear_foot.stl', 'PETG', 'rear_foot', 'foot', _matrix(translation=(0, 0, 7))),
        ('shoulder lock ring', 'stl/development/sl_lock_ring.stl', 'PETG', None, 'legs', None),
        ('right race spacer', 'stl/development/sl_race_spacer.stl', 'PETG', None, 'legs', None),
        ('left shoulder spacer', 'stl/development/sl_shoulder_spacer.stl', 'PETG', None, 'legs', None),
    ]
    for key, x in ((0, 1), (1, -1)):
        side = MIRROR_X if x < 0 else np.eye(3)
        parts += [
            (f'leg {key}', 'stl/leg.stl', 'PETG', 'leg', 'legs',
             _matrix(side, (x * d['SIDE_FOOT_X'], 0, d['HIP_Z'])) @ leg_bed),
            (f'side foot core {key}', 'stl/development/outer_foot_core.stl', 'PETG', None, 'legs',
             _matrix(side, (x * d['SIDE_FOOT_X'], 0, 12))),
            (f'side foot cover {key}', 'stl/outer_foot.stl', 'PETG', 'outer_foot', 'legs',
             _matrix(side, (x * d['SIDE_FOOT_X'], 0, 7))),
        ]
    for x, y in product((-72, 72), (-52, 52)):
        parts.append((f'rail key {x},{y}', 'stl/development/rail_key.stl', 'PETG', None, 'body',
                      _matrix(translation=(x, y, 170))))
    return parts


def purchased_masses(d: dict):
    """(label, grams, group, position in group frame). Masses are catalogue values or stated allowances."""
    hip = d['HIP_Z']
    guide = guide_axes(d)
    origin = np.array([0, d['GUIDE_Y'], d['GUIDE_Z']])
    case_center = origin + guide @ np.array([0, d['ACTUATOR_Y'], (d['ACTUATOR_FIXED_PIN'] + 83) / 2])
    lock_z = hip + d['SL_LOCK_RADIUS'] * math.sin(math.radians(d['SL_LOCK_PIN_ANGLE']))
    lock_y = d['SL_LOCK_RADIUS'] * math.cos(math.radians(d['SL_LOCK_PIN_ANGLE']))
    rail_center = -d['POST_RAIL_END'] - d['POST_RAIL'] / 2
    rows = [
        ('4 x HFS5-2020 228 mm body rails, 0.5 kg/m', 4 * 114.0, 'body', (0, 0, 292)),
        ('Bioenno BLF-1206A battery', 700.0, 'body', (d['BATTERY_X'], d['BATTERY_Y'], d['BATTERY_Z'])),
        ('Actuonix P16-100-256-12-P', 110.0, 'body', tuple(case_center)),
        ('Winco GN 412-6-35-B-1 plunger, 0.152 lb', 68.9, 'body', (d['SL_LOCK_PIN_EXIT_X'] - 16, lock_y, lock_z)),
        ('MG995 release servo', 62.41, 'body', (d['SL_RELEASE_PIVOT_X'], 30, d['SL_RELEASE_PIVOT_Z'] - 5)),
        ('4 x SKF 6201-2RSH, 0.08 lb each', 4 * 36.3, 'body', (0, 0, hip)),
        ('ServoCity 1620-0001-0004 turntable, 4.9 oz', 138.9, 'body', (0, 0, 441)),
        ('Head TT motor 30.6 g and wheel 38 g', 68.6, 'body', (62, 0, 426)),
        ('Electronics, wiring and connectors allowance', 600.0, 'body',
         (d['ELECTRONICS_X'], d['ELECTRONICS_Y'], d['ELECTRONICS_Z'])),
        ('Paint, foam, straps and ties allowance', 100.0, 'body', (0, 0, 300)),
        ('Fastener allowance', 150.0, 'body', (0, 0, 300)),
        ('12 mm steel shaft 366 mm', 325.0, 'legs', (0, 0, hip)),
        ('2 x ServoCity 1301 hubs', 20.0, 'legs', (0, 0, hip)),
        ('2 x HFS5-2020 180 mm leg rails', 180.0, 'legs', (0, 0, 250)),
        ('4 x Adafruit 3777 side-foot motors', 4 * 30.6, 'legs', (0, 0, d['WHEEL_AXLE_Z'])),
        ('8 x Adafruit 3766 side-foot wheels', 8 * 38.0, 'legs', (0, 0, d['WHEEL_AXLE_Z'])),
        ('2 x GN 412.2 bushings, 0.022 lb each', 20.0, 'legs', (d['SL_LOCK_RING_FACE_X'] + 6.5, lock_y, lock_z)),
        ('HFS5-2020 post rail', d['POST_RAIL'] * 0.5, 'post', (0, 0, rail_center)),
        ('SKF SA12E rod end, M12 jam nut', 86.0, 'post', (0, 0, -20)),
        ('2 x Adafruit 3777 centre-foot motors', 61.2, 'foot', (0, 0, d['WHEEL_AXLE_Z'])),
        ('4 x Adafruit 3766 centre-foot wheels', 152.0, 'foot', (0, 0, d['WHEEL_AXLE_Z'])),
        ('MG995 steering servo', 62.41, 'foot', (-30, -50, 88)),
        ('Ankle bolt, locknut, washer and shim', 30.0, 'foot', (0, 0, d['ANKLE_Z'])),
        ('Steering link, two joints, screws and nuts', 20.0, 'foot', (-30, -40, 110)),
    ]
    return rows


def _placed_print_transform(label: str, d: dict):
    """Inverse of the bed placements in cad/r2d2.scad for the stance-lock prints (STL -> body or leg frame)."""
    hip = d['HIP_Z']
    lock_origin = (d['SL_LOCK_PIN_EXIT_X'], d['SL_LOCK_RADIUS'] * math.cos(math.radians(d['SL_LOCK_PIN_ANGLE'])),
                   hip + d['SL_LOCK_RADIUS'] * math.sin(math.radians(d['SL_LOCK_PIN_ANGLE'])))
    if label == 'shoulder lock ring':   # rotate([0,-90,0])translate([-LOCK_RING_FACE_X,0,-HIP_Z])
        return _matrix(translation=(d['SL_LOCK_RING_FACE_X'], 0, hip)) @ _matrix(_ry(90))
    if label == 'right race spacer':    # rotate([0,-90,0])translate([-122,0,-HIP_Z])
        return _matrix(translation=(122, 0, hip)) @ _matrix(_ry(90))
    if label == 'left shoulder spacer':  # rotate([0,90,0])translate([-153,0,-HIP_Z]), then mirrored to -X
        return _matrix(MIRROR_X) @ _matrix(translation=(153, 0, hip)) @ _matrix(_ry(-90))
    if label == 'knob collar':          # rotate([0,-90,0])translate([33.5,0,0]) in the lock frame
        return _matrix(translation=lock_origin) @ _matrix(translation=(-33.5, 0, 0)) @ _matrix(_ry(90))
    if label == 'release lever':        # rotate([90,0,0])translate([0,-1.5,0])
        return _matrix(translation=(0, 1.5, 0)) @ _matrix(rot_x(-90))
    raise KeyError(label)


def build_mass_model(d: dict, mass_scale: float = 1.0, extra=()):
    ratios = sliced_fill_ratios()
    components = []
    for label, rel, material, fill_key, group, transform in printed_parts(d):
        path = ROOT / rel
        if not path.exists():
            raise FileNotFoundError(f'{rel} is required for the mass model')
        volume, centroid, _ = mesh_properties(str(path))
        fill = ratios[fill_key] if fill_key else DEVELOPMENT_FILL
        grams = volume / 1000 * PRINT_DENSITY[material] * fill
        matrix = transform if transform is not None else _placed_print_transform(label, d)
        position = (matrix @ np.append(centroid, 1))[:3]
        components.append({'label': label, 'grams': grams, 'group': group, 'position': position,
                           'basis': f'mesh volume x {PRINT_DENSITY[material]} g/cm3 x fill {fill:.3f}'})
    for label, grams, group, position in list(purchased_masses(d)) + list(extra):
        components.append({'label': label, 'grams': grams, 'group': group, 'position': np.array(position, float),
                           'basis': 'catalogue mass or stated allowance'})
    for c in components:
        c['grams'] *= mass_scale
    return components


# ---------------------------------------------------------------- state evaluation
def world_positions(d: dict, model, s: float, foot_pitch: float):
    p = pose(d, s)
    hip = np.array([0, 0, d['HIP_Z']])
    body_rot = rot_x(p['theta_deg'])
    guide = guide_axes(d)
    origin = np.array([0, d['GUIDE_Y'], d['GUIDE_Z']])
    ankle = np.array([0, p['ankle_y'], p['ankle_z']])
    foot_rot = rot_x(foot_pitch)
    out = {}
    for c in model:
        q = c['position']
        if c['group'] == 'body':
            w = hip + body_rot @ (q - hip)
        elif c['group'] == 'post':
            body_point = origin + guide @ (q + np.array([0, 0, p['length']]))
            w = hip + body_rot @ (body_point - hip)
        elif c['group'] == 'foot':
            w = ankle + foot_rot @ (q - np.array([0, 0, d['ANKLE_Z']]))
        else:
            w = q
        out.setdefault(c['group'], []).append((c['grams'], w))
    return p, out


def group_cg(groups, names):
    items = [item for n in names for item in groups.get(n, [])]
    mass = sum(m for m, _ in items)
    return mass, sum(m * w for m, w in items) / mass


def foot_points():
    points = [mesh_properties(str(ROOT / rel))[2] + np.array(offset) for rel, offset in
              (('stl/development/center_foot_core.stl', (0, 0, 12)), ('stl/rear_foot.stl', (0, 0, 7)))]
    return np.vstack(points)


def lowest_foot_z(d: dict, p: dict, pitch: float, vertices: np.ndarray):
    rot = rot_x(pitch)
    ankle = np.array([0, p['ankle_y'], p['ankle_z']])
    rel = vertices - np.array([0, 0, d['ANKLE_Z']])
    body = float((rel @ rot.T)[:, 2].min() + ankle[2])
    wheels = []
    for x, y in product((-d['WHEEL_AXLE_X'], d['WHEEL_AXLE_X']), (-d['WHEEL_ROW_Y'], d['WHEEL_ROW_Y'])):
        centre = ankle + rot @ (np.array([x, y, d['WHEEL_AXLE_Z']]) - np.array([0, 0, d['ANKLE_Z']]))
        wheels.append(centre[2] - d['WHEEL_RADIUS'])
    return min(body, min(wheels))


def support_margin(points, xy):
    hull = ConvexHull(np.array(points))
    return float(-(hull.equations[:, :2] @ xy + hull.equations[:, 2]).max())


def side_contacts(d):
    return [[sx * d['SIDE_FOOT_X'] + x, y] for sx in (-1, 1)
            for x in (-d['WHEEL_CONTACT_X'], d['WHEEL_CONTACT_X']) for y in (-d['WHEEL_ROW_Y'], d['WHEEL_ROW_Y'])]


def centre_contacts(d, ankle_y, yaw):
    a = math.radians(yaw)
    return [[x * math.cos(a) - y * math.sin(a), ankle_y + x * math.sin(a) + y * math.cos(a)]
            for x in (-d['WHEEL_CONTACT_X'], d['WHEEL_CONTACT_X']) for y in (-d['WHEEL_ROW_Y'], d['WHEEL_ROW_Y'])]


def evaluate(d: dict, model, criteria: dict | None = None) -> dict:
    global CRITERIA
    saved = CRITERIA
    if criteria is not None:
        CRITERIA = {**CRITERIA, **criteria}
    try:
        return _evaluate(d, model)
    finally:
        CRITERIA = saved


def _evaluate(d: dict, model) -> dict:
    c = CRITERIA
    failures = []

    def require(cls, check, value, limit, ok, stroke=None):
        if not ok:
            failures.append({'class': cls, 'check': check, 'value': round(float(value), 4),
                             'limit': round(float(limit), 4), 'stroke_mm': None if stroke is None else round(stroke, 3)})

    s_contact = contact_stroke(d)
    rad = math.radians
    total_mass = sum(x['grams'] for x in model) / 1000
    ux, uy, uz = c['cg_uncertainty_mm']

    # ---- kinematics: stroke range and guide engagement
    require('kinematics', 'two-foot endpoint lifts the foot (POST_MIN < contact)', d['POST_MIN'], s_contact,
            d['POST_MIN'] < s_contact)
    require('kinematics', 'three-foot endpoint on floor (POST_MAX > contact)', d['POST_MAX'], s_contact,
            d['POST_MAX'] > s_contact)
    require('kinematics', 'endpoints inside actuator stroke with position error',
            d['POST_MAX'] + c['actuator_position_error_mm'], d['POST_STROKE'],
            d['POST_MIN'] - c['actuator_position_error_mm'] >= 0
            and d['POST_MAX'] + c['actuator_position_error_mm'] <= d['POST_STROKE'])
    for s in (d['POST_MIN'], d['POST_MAX']):
        length = d['POST_ZERO'] + s
        rail_top, rail_bottom = length - d['POST_RAIL_END'] - d['POST_RAIL'], length - d['POST_RAIL_END']
        for land in (d['GUIDE_LAND_A'], d['GUIDE_LAND_B']):
            lo, hi = land - d['GUIDE_LAND_LENGTH'] / 2, land + d['GUIDE_LAND_LENGTH'] / 2
            require('kinematics', 'post rail fully engages both guide lands', rail_top - lo, 0,
                    rail_top <= lo and rail_bottom >= hi, s)
        top_z = d['GUIDE_Z'] - rail_top * math.cos(rad(d['GUIDE_ANGLE']))
        require('kinematics', 'retracted rail top stays below the dome ring', top_z, c['max_rail_top_z_mm'],
                top_z <= c['max_rail_top_z_mm'], s)
    theta_max = pose(d, d['POST_MAX'])['theta_deg']
    require('kinematics', 'ankle toe stop admits the flat three-foot foot', d['ANKLE_STOP_TOE'], theta_max + 0.5,
            d['ANKLE_STOP_TOE'] >= theta_max + 0.5)

    # ---- restraint: lock geometry at endpoints (engagement is sensed, never inferred from stroke)
    r = d['SL_LOCK_RADIUS']
    two_foot_error = r * abs(rad(pose(d, d['POST_MIN'])['theta_deg'] - d['SL_LOCK_RECEIVER_TWO_FOOT']))
    three_foot_error = r * abs(rad(theta_max - d['SL_LOCK_RECEIVER_THREE_FOOT']))
    require('restraint', 'two-foot receiver aligned with pin', two_foot_error, c['pin_radial_clearance_mm'],
            two_foot_error <= c['pin_radial_clearance_mm'], d['POST_MIN'])
    require('restraint', 'three-foot receiver aligned with pin', three_foot_error, c['pin_radial_clearance_mm'],
            three_foot_error <= c['pin_radial_clearance_mm'], d['POST_MAX'])
    chord = 2 * r * math.sin(rad(abs(d['SL_LOCK_RECEIVER_THREE_FOOT'] - d['SL_LOCK_RECEIVER_TWO_FOOT'])) / 2)
    require('restraint', 'receiver bushings do not overlap', chord - d['SL_LOCK_BUSHING_OD'], c['min_receiver_web_mm'],
            chord - d['SL_LOCK_BUSHING_OD'] >= c['min_receiver_web_mm'])
    engagement = d['SL_LOCK_PIN_EXIT_X'] + d['SL_LOCK_PIN_EXTENSION'] - d['SL_LOCK_RING_FACE_X']
    require('restraint', 'pin engagement in receiver', engagement, c['min_lock_engagement_mm'],
            c['min_lock_engagement_mm'] <= engagement <= d['SL_LOCK_BUSHING_LENGTH'])
    seat_press = d['SL_LOCK_SWITCH_OVERTRAVEL'] - d['SL_LOCK_SWITCH_ADJUST']
    require('restraint', 'lock switch operates when the pin is seated', seat_press, 0, seat_press > 0)
    worst_press = d['SL_LOCK_SWITCH_OVERTRAVEL'] + d['SL_LOCK_SWITCH_ADJUST']
    require('restraint', 'lock switch overtravel within rating', worst_press, c['switch_overtravel_mm'],
            worst_press <= c['switch_overtravel_mm'])
    indicated = engagement - (worst_press + c['switch_differential_mm'])
    require('restraint', 'switch reads engaged only with sufficient engagement', indicated,
            c['min_lock_engagement_mm'], indicated >= c['min_lock_engagement_mm'])
    require('restraint', 'plunger spring seats pin against the switch', c['spring_start_N'],
            2 * c['switch_operating_force_N'], c['spring_start_N'] >= 2 * c['switch_operating_force_N'])
    arm = np.array([d['SL_RELEASE_FINGER_X'] - d['SL_RELEASE_PIVOT_X'], d['SL_RELEASE_FINGER_Z'] - d['SL_RELEASE_PIVOT_Z']])
    phi = rad(d['SL_RELEASE_ROTATION'])
    finger_dx = arm[0] * math.cos(phi) - arm[1] * math.sin(phi) - arm[0]
    gap = d['SL_RELEASE_FINGER_X'] - (d['SL_LOCK_KNOB_SEAT_X'] + 1.5)
    pull = -finger_dx - gap
    require('restraint', 'release lever withdraws the pin clear of the receiver', pull,
            engagement + c['pin_release_clearance_mm'], pull >= engagement + c['pin_release_clearance_mm'])

    # ---- centre-foot resting pitch when lifted
    foot_mass, foot_cg = group_cg({'foot': [(x['grams'], x['position']) for x in model if x['group'] == 'foot']},
                                  ['foot'])
    foot_cg_y = float(foot_cg[1])
    heel_heavy = foot_cg_y <= -c['foot_rest_margin_mm']
    rest_pitch = d['ANKLE_STOP_HEEL'] if heel_heavy else -d['ANKLE_STOP_TOE']
    require('clearance', 'lifted centre foot rests on the heel stop (CG behind ankle)', foot_cg_y,
            -c['foot_rest_margin_mm'], heel_heavy)
    vertices = foot_points()
    flat_reference = pose(d, s_contact - 1.0)
    # Resting on the heel stop lowers the heel slightly; that heel lands first and the foot rotates flat.
    landing_allowance = (lowest_foot_z(d, flat_reference, 0.0, vertices)
                         - lowest_foot_z(d, flat_reference, rest_pitch, vertices))

    # ---- sampled transition, forward (two-foot -> three-foot) and back
    step = c['sample_step_mm']
    strokes = sorted(set(np.round(np.arange(d['POST_MIN'], d['POST_MAX'] + 1e-9, step), 6).tolist()
                         + [d['POST_MIN'], d['POST_MAX'], s_contact, s_contact - 1e-3, s_contact + 1e-3]))
    rows = []
    extrema = {'min_resting_clearance_mm': math.inf, 'min_any_stop_clearance_mm': math.inf,
               'min_two_foot_margin_mm': math.inf, 'min_three_foot_margin_mm': math.inf,
               'min_body_hold_mm': math.inf, 'max_actuator_force_N': 0.0, 'max_holding_load_N': 0.0}
    guide_angle = rad(d['GUIDE_ANGLE'])
    land_span = d['GUIDE_LAND_B'] - d['GUIDE_LAND_A']
    for direction in ('deploy', 'retract'):
        sequence = strokes if direction == 'deploy' else strokes[::-1]
        for s in sequence:
            p, groups = world_positions(d, model, s, rest_pitch)
            theta = rad(p['theta_deg'])
            airborne = not p['on_floor'] or s < s_contact
            row = {'direction': direction, 'stroke_mm': round(s, 4), 'body_pitch_deg': round(p['theta_deg'], 4),
                   'centre_ankle_y_mm': round(p['ankle_y'], 3), 'ankle_lift_mm': round(p['lift'], 3),
                   'lock': 'engaged two-foot receiver' if airborne else 'released, riding ring face'}
            if s == d['POST_MIN']:
                row['lock'] = 'engaged two-foot receiver (sensed)'
            if s == d['POST_MAX']:
                row['lock'] = 'engaged three-foot receiver (sensed)'

            body_mass, body_cg = group_cg(groups, ['body', 'post'])
            corners = []
            for dx, dy, dz in product((-ux, ux), (-uy, uy), (-uz, uz)):
                shift = rot_x(p['theta_deg']) @ np.array([dx, dy, dz])
                corners.append(shift)
            all_mass = sum(m for items in groups.values() for m, _ in items)
            _, robot_cg = group_cg(groups, list(groups))

            if airborne:
                resting = lowest_foot_z(d, p, rest_pitch, vertices)
                row['resting_floor_clearance_mm'] = round(resting, 3)
                # While lowering to contact the foot must not touch the floor early.
                require('clearance', 'lifted foot does not touch the floor before contact', resting,
                        -landing_allowance, resting >= -landing_allowance - 1e-6, s)
                if s == d['POST_MIN']:
                    any_stop = min(lowest_foot_z(d, p, pitch, vertices)
                                   for pitch in (d['ANKLE_STOP_HEEL'], -d['ANKLE_STOP_TOE']))
                    extrema['min_resting_clearance_mm'] = resting
                    extrema['min_any_stop_clearance_mm'] = any_stop
                    require('clearance', 'two-foot stance lifted-foot floor clearance (resting on heel stop)',
                            resting, c['min_floor_clearance_mm'], resting >= c['min_floor_clearance_mm'], s)
                    require('clearance', 'two-foot stance foot clears floor at either ankle stop', any_stop,
                            c['min_any_stop_clearance_mm'], any_stop >= c['min_any_stop_clearance_mm'], s)
                polygon = side_contacts(d)
                margin = min(support_margin(polygon, robot_cg[:2] + corner[:2] * body_mass / all_mass)
                             for corner in corners)
                extrema['min_two_foot_margin_mm'] = min(extrema['min_two_foot_margin_mm'], margin)
                row['support'] = 'two-foot'
                require('support', 'two-foot static support margin', margin, c['min_support_margin_mm'],
                        margin >= c['min_support_margin_mm'], s)
            else:
                margin = min(support_margin(side_contacts(d) + centre_contacts(d, p['ankle_y'], yaw),
                                            robot_cg[:2] + corner[:2] * body_mass / all_mass)
                             for corner in corners
                             for yaw in (-d['CENTER_YAW_LIMIT'], 0, d['CENTER_YAW_LIMIT']))
                extrema['min_three_foot_margin_mm'] = min(extrema['min_three_foot_margin_mm'], margin)
                row['support'] = 'three-foot'
                require('support', 'three-foot static support margin', margin, c['min_support_margin_mm'],
                        margin >= c['min_support_margin_mm'], s)
                if s < d['POST_MAX']:
                    hold = min(float(body_cg[1] + corner[1]) for corner in corners)
                    extrema['min_body_hold_mm'] = min(extrema['min_body_hold_mm'], hold)
                    row['unlocked_body_cg_ahead_of_hip_mm'] = round(hold, 3)
                    require('restraint', 'unlocked body held by post (CG ahead of hip)', hold,
                            c['min_body_hold_mm'], hold >= c['min_body_hold_mm'], s)
            row['support_margin_mm'] = round(margin, 3)

            # actuator: virtual work on moving masses, plus guide friction and rolling drag
            h = 0.01
            lo, hi = (s - h, s) if (s > s_contact and s - h >= s_contact) or s >= d['POST_MAX'] else (s, s + h)
            moving = ['post', 'foot'] if airborne else ['body', 'post', 'foot']

            def potential(v):
                _, g2 = world_positions(d, model, v, rest_pitch)
                return sum(m / 1000 * G * w[2] / 1000 for n in moving for m, w in g2.get(n, []))
            gravity_axial = abs(potential(hi) - potential(lo)) / ((hi - lo) / 1000)
            angle = guide_angle + theta
            if airborne:
                hanging = sum(m for n in ('post', 'foot') for m, _ in groups.get(n, [])) / 1000 * G
                transverse = hanging * math.sin(angle)
                drag_axial = 0.0
            else:
                moment = sum(m / 1000 * G * w[1] for n in ('body', 'post') for m, w in groups.get(n, []))
                tip_vertical = abs(moment) / p['ankle_y']
                transverse = tip_vertical * math.sin(angle) + c['rolling_drag_N'] * math.cos(angle)
                drag_axial = c['rolling_drag_N'] * math.sin(angle)
            lever = 1 + 2 * (p['length'] - d['GUIDE_LAND_B']) / land_span
            friction = c['guide_friction'] * transverse * lever
            force = c['dynamic_factor'] * (gravity_axial + friction + drag_axial)
            holding = c['dynamic_factor'] * gravity_axial
            extrema['max_actuator_force_N'] = max(extrema['max_actuator_force_N'], force)
            extrema['max_holding_load_N'] = max(extrema['max_holding_load_N'], holding)
            row['factored_actuator_force_N'] = round(force, 3)
            require('force', 'factored actuator transition force within P16 moving rating', force,
                    c['actuator_moving_rating_N'], force <= c['actuator_moving_rating_N'], s)
            require('force', 'factored holding load within P16 back-drive force (power loss)', holding,
                    c['actuator_backdrive_N'], holding <= c['actuator_backdrive_N'], s)
            rows.append(row)

    # ---- restraint and release load at the lock events
    servo_force = c['servo_stall_torque_kgcm'] * KGCM_TO_NM / (min(abs(arm[1]),
                  abs(arm[0] * math.sin(phi) + arm[1] * math.cos(phi))) / 1000)
    events = []
    for label, s, groups_used in (('release at two-foot/contact', s_contact, ['body', 'post', 'foot']),
                                  ('release at three-foot endpoint', d['POST_MAX'], ['body', 'post'])):
        p, groups = world_positions(d, model, s, rest_pitch)
        mass, cg = group_cg(groups, groups_used)
        body_mass = sum(m for n in ('body', 'post') for m, _ in groups.get(n, []))
        worst_y = max(abs(cg[1] + sign * uy * body_mass / mass + sign2 * uz * math.sin(rad(p['theta_deg'])))
                      for sign in (-1, 1) for sign2 in (-1, 1))
        torque = mass / 1000 * G * worst_y / 1000
        shear = torque / (r / 1000)
        needed = c['release_factor'] * (c['spring_end_N'] + c['switch_operating_force_N'] + c['pin_friction'] * shear)
        events.append({'event': label, 'stroke_mm': round(s, 3), 'pin_shear_N': round(shear, 3),
                       'factored_release_force_N': round(needed, 3), 'servo_force_N': round(servo_force, 3)})
        require('force', f'lock release force ({label}) within MG995 stall force', needed, servo_force,
                needed <= servo_force, s)

    # lock ring must carry the pin face everywhere between the receivers
    ring_lo = d['SL_LOCK_RING_ARC_START'] - d['SL_LOCK_PIN_ANGLE']
    ring_hi = d['SL_LOCK_RING_ARC_END'] - d['SL_LOCK_PIN_ANGLE']
    pin_half_angle = math.degrees(math.asin(3.0 / r))
    theta_lo = min(0.0, d['SL_LOCK_RECEIVER_TWO_FOOT'])
    theta_hi = max(theta_max, d['SL_LOCK_RECEIVER_THREE_FOOT'])
    bushing_half = math.degrees(math.asin(d['SL_LOCK_BUSHING_OD'] / 2 / r))
    covered = ring_lo <= theta_lo - bushing_half - pin_half_angle and ring_hi >= theta_hi + bushing_half + pin_half_angle
    require('restraint', 'lock ring arc covers the pin sweep and both receivers', ring_hi - ring_lo,
            theta_hi - theta_lo + 2 * (bushing_half + pin_half_angle), covered)
    radial_ok = d['SL_LOCK_RING_INNER'] <= r - d['SL_LOCK_BUSHING_OD'] / 2 - 2 and d['SL_LOCK_RING_OUTER'] >= r + d['SL_LOCK_BUSHING_OD'] / 2 + 2
    require('restraint', 'lock ring radial band surrounds the receivers', d['SL_LOCK_RING_OUTER'] - d['SL_LOCK_RING_INNER'],
            d['SL_LOCK_BUSHING_OD'] + 4, radial_ok)

    summary = {
        'post_contact_mm': s_contact, 'three_foot_pitch_deg': theta_max,
        'three_foot_centre_ankle_y_mm': pose(d, d['POST_MAX'])['ankle_y'],
        'two_foot_ankle_lift_mm': pose(d, d['POST_MIN'])['lift'],
        'estimated_mass_kg': total_mass, 'centre_foot_cg_y_from_ankle_mm': foot_cg_y,
        'resting_foot_pitch_deg': rest_pitch, 'lock_engagement_mm': engagement,
        'lock_indicated_min_engagement_mm': indicated, 'receiver_chord_mm': chord,
        'release_pull_mm': pull, **{k: (None if v == math.inf else v) for k, v in extrema.items()},
    }
    return {'passed': not failures, 'failures': failures, 'summary': summary, 'lock_events': events,
            'rows': rows, 'samples': len(rows)}


# ---------------------------------------------------------------- mechanism print meshes
# Sensed-lock prints owned by this milestone. The shared chassis, adapter and foot-core meshes feed the mass
# model but are validated by export_cad.py --check-development.
MECHANISM_PRINTS = ('sl_lock_ring', 'sl_race_spacer', 'sl_shoulder_spacer', 'sl_knob_collar', 'sl_release_lever')


def validate_mechanism_meshes():
    failures, rows = [], []
    for name in MECHANISM_PRINTS:
        path = ROOT / 'stl/development' / f'{name}.stl'
        if not path.exists():
            failures.append({'class': 'geometry', 'check': f'{name}.stl exported', 'value': 0, 'limit': 1,
                             'stroke_mm': None})
            continue
        mesh = trimesh.load_mesh(path, process=True)
        solids = int(sum(part.volume > 0 for part in mesh.split(only_watertight=False)))
        ok = bool(mesh.is_watertight and mesh.is_winding_consistent and mesh.volume > 0 and solids == 1
                  and all(mesh.extents <= 300.001) and abs(mesh.bounds[0, 2]) <= 1e-3)
        rows.append({'part': name, 'closed': bool(mesh.is_watertight), 'positive_solids': solids,
                     'dimensions_mm': [round(float(v), 3) for v in mesh.extents], 'passed': ok})
        if not ok:
            failures.append({'class': 'geometry', 'check': f'{name}.stl is one closed solid on the bed within 300 mm',
                             'value': solids, 'limit': 1, 'stroke_mm': None})
    return failures, rows


def _jsonable(value):
    if isinstance(value, dict):
        return {k: _jsonable(v) for k, v in value.items()}
    if isinstance(value, (list, tuple)):
        return [_jsonable(v) for v in value]
    if isinstance(value, (np.floating, np.integer)):
        return value.item()
    if isinstance(value, float):
        return round(value, 6)
    return value


def main() -> int:
    design = load_design()
    model = build_mass_model(design)
    result = evaluate(design, model)
    mesh_failures, mesh_rows = validate_mechanism_meshes()
    failures = result['failures'] + mesh_failures
    groups = {}
    for c in model:
        groups.setdefault(c['group'], []).append({'label': c['label'], 'grams': round(c['grams'], 2),
                                                  'position_mm': [round(float(v), 2) for v in c['position']],
                                                  'basis': c['basis']})
    report = {
        'revision': 'D-development', 'configuration': 'front deployment; full retraction to two-foot stance; '
        'sensed GN 412 shoulder lock (stance-lock-sensed.scad) at both endpoints', 'passed': not failures, 'physical_tested': False,
        'printed_strength_verified': False, 'criteria': CRITERIA, 'design_source': ['cad/kinematics.scad', 'cad/stance-lock-sensed.scad'],
        'design': design, 'summary': result['summary'], 'lock_events': result['lock_events'],
        'failures': failures, 'mechanism_meshes': mesh_rows, 'mass_model': groups, 'samples': result['samples'],
        'rows': result['rows'],
    }
    REPORT.write_text(json.dumps(_jsonable(report), indent=1), encoding='utf-8')
    s = result['summary']
    print(f"Samples: {result['samples']} (deploy and retract, {CRITERIA['sample_step_mm']} mm step); "
          f"estimated mass {s['estimated_mass_kg']:.2f} kg")
    print(f"Contact {s['post_contact_mm']:.3f} mm; three-foot pitch {s['three_foot_pitch_deg']:.3f} deg; "
          f"two-foot lift {s['two_foot_ankle_lift_mm']:.2f} mm")
    print(f"Clearance: resting {s['min_resting_clearance_mm']:.2f} mm (min {CRITERIA['min_floor_clearance_mm']}), "
          f"either stop {s['min_any_stop_clearance_mm']:.2f} mm")
    print(f"Support margin: two-foot {s['min_two_foot_margin_mm']:.2f} mm, three-foot "
          f"{s['min_three_foot_margin_mm']:.2f} mm (min {CRITERIA['min_support_margin_mm']})")
    print(f"Actuator: factored {s['max_actuator_force_N']:.1f} N (rating {CRITERIA['actuator_moving_rating_N']}), "
          f"holding {s['max_holding_load_N']:.1f} N (back-drive {CRITERIA['actuator_backdrive_N']})")
    for event in result['lock_events']:
        print(f"Lock {event['event']}: factored release {event['factored_release_force_N']:.1f} N "
              f"<= servo {event['servo_force_N']:.1f} N")
    print(f"Restraint: engagement {s['lock_engagement_mm']:.2f} mm, sensed minimum "
          f"{s['lock_indicated_min_engagement_mm']:.2f} mm, unlocked body CG ahead of hip >= "
          f"{s['min_body_hold_mm']:.2f} mm")
    if failures:
        seen = set()
        for f in failures:
            key = (f['class'], f['check'])
            if key not in seen:
                seen.add(key)
                print(f"FAIL [{f['class']}] {f['check']}: {f['value']} vs {f['limit']} at stroke {f['stroke_mm']}")
        print('NOT ACCEPTED: calculated transition screen failed; see cad/kinematic-check.json')
        return 1
    print('PASS: calculated transition screen. Physical mass, CG, friction, strength and lock tests remain required.')
    return 0


if __name__ == '__main__':
    sys.exit(main())
