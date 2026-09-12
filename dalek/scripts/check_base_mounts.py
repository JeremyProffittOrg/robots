"""MOUNT-1 finite geometry checks for the battery, motor clamps and bridge deck.

Uses the existing NumPy/trimesh stack. No load rating or physical fit is inferred
from these checks. Run after exporting the current base, clamp and platform.
"""
import hashlib
import json
from pathlib import Path

import numpy as np
import trimesh

from render_drawings import BOARD_LAYOUT
from mesh_queries import contains, METHOD

ROOT = Path(__file__).resolve().parents[1]
NAMES = ('01_base', '02_skirt', '11_motor_clamp', '12_electronics_platform')
INPUTS = [ROOT/'stl'/(n+'.stl') for n in NAMES] + [ROOT/'cad/base_mounts.scad', ROOT/'cad/dalek.scad', ROOT/'scripts/mesh_queries.py', Path(__file__)]
SOURCE_HASHES = {str(p.relative_to(ROOT)).replace('\\', '/'): hashlib.sha256(p.read_bytes()).hexdigest() for p in INPUTS}
MESHES = {n: trimesh.load_mesh(ROOT / 'stl' / (n + '.stl'), process=True) for n in NAMES}
CHECKS = []
BASE = MESHES['01_base']
PLATFORM = MESHES['12_electronics_platform'].copy()
PLATFORM.apply_transform(trimesh.transformations.rotation_matrix(np.pi, [1, 0, 0]))
PLATFORM.apply_translation([0, 0, 146])
SKIRT = MESHES['02_skirt'].copy()
SKIRT.apply_translation([0, 0, 54])


def record(name, count, failures, **extra):
    row = dict(check=name, samples=int(count), failures=int(failures), passed=bool(failures == 0), **extra)
    CHECKS.append(row)
    print(json.dumps(row), flush=True)


def grid(lo, hi, counts=(7, 7, 7)):
    return np.array(np.meshgrid(*[np.linspace(a, b, n) for a, b, n in zip(lo, hi, counts)],
                               indexing='ij')).reshape(3, -1).T


def hits(mesh, points):
    points = points[((points > mesh.bounds[0]) & (points < mesh.bounds[1])).all(axis=1)]
    return int(contains(mesh, points).sum())


def check_mesh(name, points, mesh):
    record(name, len(points), hits(mesh, points))


def inside_faces(mesh):
    return mesh.triangles_center - mesh.face_normals * .025


def bar(lo, hi):
    return grid(lo, hi, (5, 7, 5))


def loop_x(x0, x1, y, z0, z1, width=4.8, thickness=1.2):
    """Rectangular cable-tie envelope; width follows Y, thickness X/Z."""
    a, b = width / 2, thickness / 2
    return np.concatenate([bar([x0-b, y-a, z0], [x0+b, y+a, z1]),
                           bar([x1-b, y-a, z0], [x1+b, y+a, z1]),
                           bar([x0, y-a, z0-b], [x1, y+a, z0+b]),
                           bar([x0, y-a, z1-b], [x1, y+a, z1+b])])


for name, mesh in MESHES.items():
    record(name + '-valid-connected-solid', 1,
           not (mesh.is_watertight and mesh.is_winding_consistent and mesh.volume > 0 and mesh.body_count == 1))

for joint, obstacle, radius, height_offset in [('base', BASE, 137, 0), ('skirt-top', SKIRT, 97, 210)]:
    for angle in (0, 90, 180, 270):
        nut = np.array([[radius+r*np.cos(a), r*np.sin(a), z+height_offset]
                        for r in [2.4, 3.9] for a in np.deg2rad([30, 90, 150, 210, 270, 330])
                        for z in [44.15, 45.7, 47.25]])
        roof = np.array([[radius+3*np.cos(a), 3*np.sin(a), z+height_offset]
                         for a in np.linspace(0, 2*np.pi, 12, endpoint=False) for z in [47.4, 50, 53.9]])
        rotation = trimesh.transformations.rotation_matrix(np.deg2rad(angle), [0, 0, 1])[:3, :3]
        check_mesh(f'{joint}-captive-M4-nut-{angle}-pocket', nut@rotation.T, obstacle)
        record(f'{joint}-captive-M4-nut-{angle}-roof-material', len(roof), len(roof)-contains(obstacle, roof@rotation.T).sum())

record('base-envelope-and-six-mm-floor', 4,
       sum(abs(a-b) > .01 for a, b in zip(BASE.extents, [300, 300, 57])) +
       int(not contains(BASE, [[0, 0, 3]])[0]))
record('platform-print-envelope', 3,
       int(np.any(MESHES['12_electronics_platform'].extents > [216.01, 216.01, 112.01])))

motors, clamps, motor_ties = [], [], []
for sx in (-1, 1):
    for sy in (-1, 1):
        motor = grid([59.35, 1.05, 6.05], [81.65, 70.95, 28.39]) * [sx, sy, 1]
        motors.append(motor)
        check_mesh(f'motor-{sx}-{sy}-base', motor, BASE)
        check_mesh(f'motor-{sx}-{sy}-platform', motor, PLATFORM)
        wheel = np.array([[x, 58+r*np.cos(a), 17.7+r*np.sin(a)]
                          for x in [83.55, 98, 112.45] for r in [15, 27, 31.45]
                          for a in np.linspace(0, 2*np.pi, 32, endpoint=False)]) * [sx, sy, 1]
        unit = np.concatenate([wheel, motor])
        insertion = np.concatenate([unit+[0, 0, z] for z in np.linspace(0, 100, 21)])
        check_mesh(f'mated-motor-wheel-{sx}-{sy}-vertical-insertion', insertion, BASE)
        clamp = MESHES['11_motor_clamp'].copy()
        if sx < 0:
            clamp.apply_transform(trimesh.transformations.rotation_matrix(np.pi, [0, 0, 1]))
        clamp.apply_translation([sx*70.5, sy*11, 29])
        clamps.append(clamp)
        check_mesh(f'clamp-{sx}-{sy}-base', inside_faces(clamp), BASE)
        check_mesh(f'clamp-{sx}-{sy}-motor', motor, clamp)
        # Each clamp translates4mm toward the outer boss before its toe slides in.
        moving = np.concatenate([inside_faces(clamp) + [sx*dx, 0, 0]
                                 for dx in np.linspace(0, 4, 9)])
        check_mesh(f'clamp-{sx}-{sy}-horizontal-insertion', moving, BASE)
        # One screw per clamp, with a captive nut loaded before the motor.
        shaft = grid([sx*88.5-1.45, sy*11-1.45, 18.55],
                     [sx*88.5+1.45, sy*11+1.45, 33.45], (3, 3, 11))
        shaft = shaft[np.linalg.norm(shaft[:, :2]-[sx*88.5, sy*11], axis=1) < 1.5]
        check_mesh(f'clamp-{sx}-{sy}-single-M3-shaft', shaft, BASE)
        for x in ((62, 74) if sy > 0 else (68, 80)):
            # Rotate a transverse loop90degrees: two longitudinal straps per motor.
            tie = loop_x(-.2, 72.2, x, -.7, 30)
            tie = tie[:, [1, 0, 2]] * [sx, sy, 1]
            motor_ties.append((sx, sy, x, tie))
            check_mesh(f'motor-{sx}-{sy}-tie-{x}-base', tie, BASE)
            check_mesh(f'motor-{sx}-{sy}-tie-{x}-platform', tie, PLATFORM)

# Tolerance envelopes include the terminal height, on a2mm insulating floor pad.
BATTERIES = {'Bioenno-BLF1206A': (70, 114, 76),
             'PowerSonic-PS1270-7Ah': (67, 153, 102),
             'PowerSonic-PS12140-14Ah': (100, 153, 103)}
for name, (w, d, h) in BATTERIES.items():
    points = grid([-w/2+.05, -d/2+.05, 8.05], [w/2-.05, d/2-.05, 8+h-.05], (11, 11, 9))
    check_mesh(name+'-base', points, BASE)
    check_mesh(name+'-platform', points, PLATFORM)
    for i, clamp in enumerate(clamps):
        check_mesh(name+f'-clamp-{i}', points, clamp)
    # Battery lowers into the exposed chassis before the platform is installed.
    moving = np.concatenate([points + [0, 0, z] for z in np.linspace(0, 150, 13)])
    check_mesh(name+'-vertical-installation', moving, BASE)

headroom = grid([-49.95, -76.45, 111.05], [49.95, 76.45, 139.95], (19, 21, 9))
check_mesh('full-14Ah-footprint-29mm-terminal-headroom', headroom, PLATFORM)
headroom_with_hardware = grid([-49.95, -76.45, 111.05], [49.95, 76.45, 136.95], (19, 21, 9))
check_mesh('full-14Ah-footprint-26mm-headroom-after-fasteners', headroom_with_hardware, PLATFORM)
check_mesh('platform-feet-and-legs-base', inside_faces(PLATFORM), BASE)
platform_points = inside_faces(PLATFORM)
platform_path = np.concatenate([platform_points + [0, 0, z] for z in np.linspace(0, 160, 17)])
check_mesh('platform-lowers-over-14Ah-base', platform_path, BASE)
record('platform-lowers-over-14Ah-case', len(platform_path),
       ((np.abs(platform_path[:, 0]) < 50) & (np.abs(platform_path[:, 1]) < 76.5) &
        (platform_path[:, 2] > 8) & (platform_path[:, 2] < 111)).sum())

for sx in (-1, 1):
    for sy in (-1, 1):
        for dy in (-8, 8):
            y = sy*48 + dy
            tie = loop_x(sx*56.5-4.7, sx*56.5+4.7, y, 31.5, 40.85)
            check_mesh(f'platform-foot-{sx}-{sy}-{dy}-tie-base', tie, BASE)
            check_mesh(f'platform-foot-{sx}-{sy}-{dy}-tie-platform', tie, PLATFORM)
            shaft = grid([sx*56.5-1.45, y-1.45, 29.85], [sx*56.5+1.45, y+1.45, 40.95], (3, 3, 9))
            shaft = shaft[np.linalg.norm(shaft[:, :2]-[sx*56.5, y], axis=1) < 1.5]
            check_mesh(f'platform-foot-{sx}-{sy}-{dy}-M3-shaft-base', shaft, BASE)
            check_mesh(f'platform-foot-{sx}-{sy}-{dy}-M3-shaft-platform', shaft, PLATFORM)
            # Side-entry2.5mm L key runs alongY, away from the adjacent leg.
            # Fixed|X|56.5 clears the wheels, which can remain installed.
            end = y + np.sign(dy)*79
            key = np.concatenate([grid([55, y-1.5, 43], [58, y+1.5, 61], (3, 3, 10)),
                                  grid([55, min(y, end), 59.5], [58, max(y, end), 62.5], (3, 35, 3))])
            key[:, 0] *= sx
            check_mesh(f'platform-foot-{sx}-{sy}-{dy}-side-L-key-base', key, BASE)
            check_mesh(f'platform-foot-{sx}-{sy}-{dy}-side-L-key-platform', key, PLATFORM)
            record(f'platform-foot-{sx}-{sy}-{dy}-side-L-key-battery', len(key),
                   ((np.abs(key[:, 0]) < 50) & (np.abs(key[:, 1]) < 76.5) &
                    (key[:, 2] > 8) & (key[:, 2] < 111)).sum())
            record(f'platform-foot-{sx}-{sy}-{dy}-side-L-key-wheels', len(key),
                   ((np.abs(key[:, 0]) >= 83.5) & (np.abs(key[:, 0]) <= 112.5)).sum())

for i, (sx, sy, x, tie) in enumerate(motor_ties):
    record(f'motor-tie-{sx}-{sy}-{x}-wheel-inner-face', len(tie),
           (np.abs(tie[:, 0]) >= 83.5).sum())
    record(f'motor-tie-{sx}-{sy}-{x}-all-motor-cases', len(tie),
           ((np.abs(tie[:, 0]) > 59.3) & (np.abs(tie[:, 0]) < 81.7) &
            (np.abs(tie[:, 1]) > 1) & (np.abs(tie[:, 1]) < 71) &
            (tie[:, 2] > 6) & (tie[:, 2] < 28.44)).sum())
    for osx, osy, ox, _ in motor_ties[i+1:]:
        if sx == osx and sy != osy:
            record(f'opposed-motor-ties-{sx}-{x}-{ox}', 1,
                   int(abs(x-ox) <= 4.8), minimum_separation_mm=round(abs(x-ox)-4.8, 3))

for y in (-25, 25):
    tie = loop_x(-51.5, 51.5, y, -.7, 112)
    check_mesh(f'battery-tie-{y}-base', tie, BASE)
    check_mesh(f'battery-tie-{y}-platform', tie, PLATFORM)

boards = []
pcb_hardware = []
for label, (x, y), (w, d, h) in BOARD_LAYOUT:
    lo, hi = [x-w/2, y-d/2, 152], [x+w/2, y+d/2, 152+h]
    board = grid(np.array(lo)+.025, np.array(hi)-.025, (5, 5, 3))
    boards.append((label, np.array(lo), np.array(hi), board))
    # This conservative zone bounds any permitted underside washer/nut/tip.
    # Actual holes must avoid printed beams and braces; they are a bench gate.
    underside = grid([lo[0], lo[1], 137], [hi[0], hi[1], 139.95], (5, 5, 3))
    pcb_hardware.append(underside)
    record(label+'-bounded-underside-hardware-battery', len(underside),
           ((np.abs(underside[:, 0]) < 50) & (np.abs(underside[:, 1]) < 76.5) &
            (underside[:, 2] > 8) & (underside[:, 2] < 111)).sum(),
           minimum_clearance_above_maximum_terminal_height_mm=26)
    check_mesh(label+'-platform', board, PLATFORM)
    record(label+'-deck-edge-margin', 4,
           int(max(np.hypot(xx, yy) for xx in (lo[0], hi[0]) for yy in (lo[1], hi[1])) > 100),
           minimum_radial_edge_margin_mm=round(108-max(np.hypot(xx, yy) for xx in (lo[0], hi[0]) for yy in (lo[1], hi[1])), 3))
for i, (name, lo, hi, _) in enumerate(boards):
    for other, low, high, _ in boards[i+1:]:
        overlap = np.minimum(hi, high)-np.maximum(lo, low)
        record(name+'-versus-'+other, 1, int(np.all(overlap > 0)))

# The skirt is lowered around the finished chassis. Its lower opening is264mm;
# nothing on the chassis passes through the skirt's184mm upper opening.
populated = np.concatenate([PLATFORM.vertices] + pcb_hardware + [grid(b[1], b[2], (2, 2, 2)) for b in boards] +
                          [grid([59.3, 1, 6], [81.7, 71, 28.44], (2, 2, 2))*[sx, sy, 1]
                           for sx in (-1, 1) for sy in (-1, 1)] +
                          [m.vertices for m in clamps] +
                          [grid([-50, -76.5, 8], [50, 76.5, 111], (2, 2, 2))])
# Conservative continuous bound: take every skirt triangle that can reach the
# chassis during a vertical lowering. Its complete XY projection includes even
# the portion above the chassis, so the nearest projected point is a lower
# bound on available radial clearance throughout the complete lowering path.
projected = SKIRT.triangles[SKIRT.triangles[:, :, 2].min(axis=1) <= populated[:, 2].max()].copy()
projected = projected[:, :, :2]
# Include degenerate XY projections from vertical faces explicitly. Distances
# to their line segments remain well-defined even when projected area is zero.
distances, cross = [], []
for edge in range(3):
    start, end = projected[:, edge], projected[:, (edge+1) % 3]
    delta = end-start
    length_squared = (delta*delta).sum(axis=1)
    fraction = np.clip(np.divide(-(start*delta).sum(axis=1), length_squared,
                                 out=np.zeros(len(projected)), where=length_squared > 0), 0, 1)
    distances.append(np.linalg.norm(start+fraction[:, None]*delta, axis=1))
    cross.append(start[:, 0]*end[:, 1]-start[:, 1]*end[:, 0])
cross = np.array(cross)
inside = ((cross >= 0).all(axis=0) | (cross <= 0).all(axis=0)) & (np.abs(cross.sum(axis=0)) > 1e-10)
distance = np.array(distances).min(axis=0)
distance[inside] = 0
minimum_skirt_radius = float(distance.min())
maximum_chassis_radius = float(np.linalg.norm(populated[:, :2], axis=1).max())
record('skirt-lowers-over-populated-chassis', len(projected)+len(populated),
       int(maximum_chassis_radius >= minimum_skirt_radius),
       conservative_radial_clearance_mm=round(minimum_skirt_radius-maximum_chassis_radius, 3),
       method='Continuous conservative XY projection bound for all triangles that can reach the chassis')

# A3mm ball-end driver leans inward16degrees. A1.74mm envelope radius includes
# the hex corners and small nominal clearance. Existing250mm blade is retained.
for angle in (0, 90, 180, 270):
    direction = np.array([-np.sin(np.deg2rad(16)), 0, np.cos(np.deg2rad(16))])
    across = np.array([np.cos(np.deg2rad(16)), 0, np.sin(np.deg2rad(16))])
    points = np.array([[137, 0, 64] + direction*t +
                      1.74*(across*np.cos(a)+np.array([0, 1, 0])*np.sin(a))
                      for t in np.linspace(0, 250, 126) for a in np.linspace(0, 2*np.pi, 16, endpoint=False)])
    matrix = trimesh.transformations.rotation_matrix(np.deg2rad(angle), [0, 0, 1])[:3, :3]
    points = points @ matrix.T
    check_mesh(f'M4-driver-{angle}-platform', points, PLATFORM)
    check_mesh(f'M4-driver-{angle}-skirt', points, SKIRT)
    for name, lo, hi, _ in boards:
        record(f'M4-driver-{angle}-{name}', len(points), ((points > lo) & (points < hi)).all(axis=1).sum())

record('inputs-unchanged-through-checks', len(INPUTS),
       sum(hashlib.sha256(p.read_bytes()).hexdigest() != SOURCE_HASHES[str(p.relative_to(ROOT)).replace('\\', '/')]
           for p in INPUTS))
report = dict(design='MOUNT-1', all_pass=all(c['passed'] for c in CHECKS),
              method='Deterministic finite volume, surface and installation-path samples; millimetres in base coordinates',
              mesh_query_method=METHOD,
              mesh_sha256={n: hashlib.sha256((ROOT/'stl'/(n+'.stl')).read_bytes()).hexdigest() for n in NAMES},
              source_sha256=SOURCE_HASHES, board_layout=BOARD_LAYOUT,
              battery_envelopes_mm=BATTERIES, deck_underside_base_z_mm=140,
              board_underside_base_z_mm=152, motor_screw_count=4, motor_alternative_tie_count=8,
              maximum_pcb_underside_hardware_projection_mm=3, populated_terminal_headroom_mm=26,
              platform_screw_or_tie_count=8, battery_tie_count=2, checks=CHECKS,
              limits=['Finite sampling is not a continuous exact collision proof.',
                      'Actual PCB holes, connectors, wire routes and tie heads require bench fitting.',
                      'Clamp padding, captive-nut fit, SLA terminals and cable bend require physical checks.',
                      'No physical strength, impact, tipping, wheel grip or loaded drive test has been performed.'])
(ROOT/'cad/base-mounts-checks.json').write_text(json.dumps(report, indent=2)+'\n', encoding='utf-8')
print(json.dumps(dict(all_pass=report['all_pass'], checks=len(CHECKS),
                      sample_evaluations=sum(c['samples'] for c in CHECKS))), flush=True)
if not report['all_pass']:
    raise SystemExit('FAILED: '+', '.join(c['check'] for c in CHECKS if not c['passed']))
