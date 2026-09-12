"""Check MOUNT-1 merged-upper assembly access and compact arm clearances."""
import argparse
import hashlib
import json
from pathlib import Path

import numpy as np
import trimesh
from mesh_queries import contains, METHOD

ROOT = Path(__file__).resolve().parents[1]
parser = argparse.ArgumentParser()
parser.add_argument("--shoulder", type=Path, default=ROOT / "stl/04_shoulder.stl")
parser.add_argument("--carrier", type=Path, default=ROOT / "stl/07_pitch_carrier.stl")
args = parser.parse_args()
paths = {"04_shoulder": args.shoulder, "07_pitch_carrier": args.carrier}
paths.update({n: ROOT / "stl" / f"{n}.stl" for n in
              ("08_plunger_arm", "09_emitter_arm", "10_head_motor_carriage")})
meshes = {n: trimesh.load_mesh(p, process=True) for n, p in paths.items()}
hashes = {n: hashlib.sha256(p.read_bytes()).hexdigest() for n, p in paths.items()}
upper, carrier = meshes["04_shoulder"], meshes["07_pitch_carrier"]
results = []
root_sections = {}


def record(name, points, obstacle=upper):
    points = np.asarray(points).reshape(-1, 3)
    hits = sum(int(contains(obstacle, batch).sum()) for batch in np.array_split(points, max(1, (len(points)+2047)//2048)))
    row = dict(check=name, samples=len(points), interior_hits=hits, passed=hits == 0)
    results.append(row)
    print(json.dumps(row), flush=True)


def grid(lo, hi, count=5):
    return np.array(np.meshgrid(*(np.linspace(a, b, count) for a, b in zip(lo, hi)),
                                indexing="ij")).reshape(3, -1).T


def rot(degrees, axis):
    return trimesh.transformations.rotation_matrix(np.radians(degrees), axis)[:3, :3]


def moved(points, poses):
    return np.concatenate([points + pose for pose in poses])


turn = rot(-90, [0, 0, 1]) @ rot(90, [1, 0, 0])
arms = {n: (meshes[n].vertices - [0, 0, 28]) @ turn.T
        for n in ("08_plunger_arm", "09_emitter_arm")}
pitch_case = grid([1.05, -5.95, 18.75], [31.95, 5.95, 41.25], 7)
yaw_case = grid([-16.25, -5.95, 7.05], [6.25, 5.95, 37.95], 9)
# Ear and fastener envelopes include the slotted, measured-fit M2 option.
yaw_ears = np.concatenate([grid([a, -5.95, 29.85], [b, 5.95, 31.75], 5)
                           for a, b in ((-20.7, -16.35), (6.35, 10.7))])
pitch_ears = np.concatenate([grid([7.25, -5.95, a], [9.15, 5.95, b], 5)
                             for a, b in ((14.3, 18.65), (41.35, 45.7))])
for x in (-47, 53):
    record(f"yaw-ears-{x}", yaw_ears + [x, -94, 0])
    for yaw in (-8, 0, 8):
        record(f"pitch-ears-{x}-{yaw}", pitch_ears @ rot(yaw, [0,0,1]).T + [x,-94,42])
    poses = [(x, 0, z) for z in np.linspace(-50, 38, 24)]
    poses += [(x, y, 38) for y in np.linspace(0, -94, 25)]
    poses += [(x, -94, z) for z in np.linspace(38, 0, 20)]
    record(f"yaw-servo-bottom-entry-{x}", moved(np.concatenate([yaw_case, yaw_ears]), poses))
record("pitch-body-against-carrier", pitch_case, carrier)
record("pitch-ears-against-carrier", pitch_ears, carrier)


def cylinder_points(radius, lo, hi, axis=2):
    angles = np.linspace(0, 2*np.pi, 24, endpoint=False)
    p = np.concatenate([np.column_stack([radius*np.cos(angles), radius*np.sin(angles),
                                         np.full(24, z)]) for z in np.linspace(lo, hi, 12)])
    return p if axis == 2 else p[:, [2, 1, 0]]


def rod(start, end, radius, sections=25):
    start, end = np.array(start, dtype=float), np.array(end, dtype=float)
    axis = end-start
    axis /= np.linalg.norm(axis)
    cross = np.cross(axis, [0,0,1] if abs(axis[2]) < .9 else [0,1,0])
    cross /= np.linalg.norm(cross)
    other = np.cross(axis, cross)
    a = np.linspace(0, 2*np.pi, 12, endpoint=False)
    circle = radius*(np.cos(a)[:,None]*cross + np.sin(a)[:,None]*other)
    return np.concatenate([circle + start + (end-start)*t for t in np.linspace(0,1,sections)])


for x in (-47, 53):
    for offset in (-19.5, 9.5):
        hardware = np.concatenate([cylinder_points(.99, 22.1, 32.05),
                                   cylinder_points(2.3, 23.95, 25.5),
                                   cylinder_points(2.49, 25.51, 25.79),
                                   cylinder_points(2.49, 31.81, 32.09),
                                   cylinder_points(1.89, 32.11, 34.09)])
        record(f"yaw-M2x10-stack-{x}-{offset}", hardware + [x+offset, -94, 0])
        # Wiha01121:1.5mm AF,46mm long leg,15mm short leg. Introduce
        # from below, advance above the screw, lower and turn in60deg arcs.
        key = np.concatenate([rod([0,0,-15], [0,0,0], .87, 12),
                               rod([0,0,0], [0,46,0], .87, 25)])
        poses = [(x+offset, -34, z) for z in np.linspace(-20, 51, 24)]
        poses += [(x+offset, y, 51) for y in np.linspace(-34, -94, 25)]
        poses += [(x+offset, -94, z) for z in np.linspace(51,48,5)]
        q = moved(key, poses)
        q = np.concatenate([q] + [key @ rot(a,[0,0,1]).T + [x+offset,-94,48]
                                   for a in np.linspace(-30,30,13)])
        record(f"yaw-socket-key-entry-and-turn-{x}-{offset}", q)
        nose = grid([-2.99,0,-1.19], [2.99,24,1.19], 7)
        poses = [(x+offset, -34, z) for z in np.linspace(-5,24.5,15)]
        poses += [(x+offset, y,24.5) for y in np.linspace(-34,-94,25)]
        record(f"yaw-nut-tool-window-{x}-{offset}", moved(nose, poses))
    for xx in (-11, 3):
        tie = np.concatenate([grid([xx-1.24, y-.49, 2.8], [xx+1.24, y+.49, 39.4], 9)
                               for y in (-10, 10)] +
                              [grid([xx-1.24, -10, z-.49], [xx+1.24, 10, z+.49], 9)
                               for z in (2.8, 39.4)])
        record(f"yaw-tie-loop-{x}-{xx}", tie + [x, -94, 0])
for z in (15.75, 44.25):
    hardware = np.concatenate([cylinder_points(.99, 6.9, 16.9, axis=0),
                               cylinder_points(2.3, 13.55, 15.05, axis=0),
                               cylinder_points(2.49, 6.91, 7.19, axis=0),
                               cylinder_points(2.49, 13.21, 13.49, axis=0),
                               cylinder_points(1.89, 4.91, 6.89, axis=0)])
    record(f"pitch-M2x10-stack-{z}", hardware + [0, 0, z], carrier)
for z in (24, 36):
    tie = np.concatenate([grid([-.6, y-.49, z-1.24], [36.6, y+.49, z+1.24], 9)
                           for y in (-7, 13)] +
                          [grid([x-.49, -7, z-1.24], [x+.49, 13, z+1.24], 9)
                           for x in (-.6, 36.6)])
    record(f"pitch-tie-loop-{z}", tie, carrier)

# The root flat clears the servo front without moving the arm shaft or socket.
# Both parts share parent yaw, so only relative pitch changes this clearance.
for name in ("08_plunger_arm", "09_emitter_arm"):
    q = np.concatenate([(np.concatenate([pitch_case, pitch_ears])-[-3, 0, 35]) @
                         rot(a, [1,0,0]) @ turn + [0,0,28]
                         for a in np.linspace(-8, 8, 17)])
    record(f"servo-against-arm-at17-pitch-poses-{name}", q, meshes[name])
    for y in (-8, 8):
        record(f"arm-M2-horn-hole-{name}-{y}",
               cylinder_points(.99, 16, 40)+[0,y,0], meshes[name])
    sections = []
    for x in np.linspace(.25, 11.75, 47):
        section = meshes[name].section(plane_normal=[1,0,0], plane_origin=[x,0,28])
        planar, _ = section.to_2D()
        sections.append(dict(x_mm=float(x), net_area_mm2=float(planar.area)))
    root_sections[name] = dict(sample_count=len(sections),
                               minimum=min(sections, key=lambda row: row["net_area_mm2"]),
                               physical_load_rating=None)

# Feed each detached arm vertically through the rear part of the lower bore,
# turn above the baffle, then use the original centered socket approach.
for x, name in ((-50, "08_plunger_arm"), (50, "09_emitter_arm")):
    poses = [(10, 90, z) for z in np.linspace(-35, 45, 33)]
    poses += [(y, 90, 45) for y in np.linspace(10, 25, 9)]
    poses += [(25, 90, z) for z in np.linspace(45, 110, 27)]
    poses += [(25, a, 110) for a in np.linspace(90, 13.5, 39)]
    poses += [(25, 13.5, z) for z in np.linspace(110, 77+140*np.tan(np.radians(13.5)), 5)]
    poses += [(y, 13.5, 77+(y+115)*np.tan(np.radians(13.5)))
              for y in np.linspace(25, -20, 24)]
    poses += [(-20, a, 77+95*np.tan(np.radians(a))) for a in np.linspace(13.5, 0, 15)]
    poses += [(y, 0, 77) for y in np.linspace(-20, -94, 30)]
    q = np.concatenate([arms[name] @ rot(angle, [1, 0, 0]).T + [x, y, z]
                        for y, angle, z in poses])
    record(f"bottom-detached-arm-insertion-{x}", q)

# Complete carriage, motor and wheel lower vertically through the open head.
# The new99.1mm liner bore admits the existing98mm carriage perimeter.
slide = meshes["10_head_motor_carriage"].vertices
motor = np.concatenate([grid([-9.25, -30.95, .05], [9.25, 12.95, 22.39], 7),
                        grid([-11.15, -56.95, .05], [11.15, -31.05, 22.39], 7)])
motor = np.column_stack([64.5 + motor[:, 2]-11.7, motor[:, 1], 163.5+motor[:, 0]])
angles = np.linspace(0, 2*np.pi, 64, endpoint=False)
wheel = np.concatenate([np.column_stack([64.5 + 31.49*np.cos(angles),
                                         31.49*np.sin(angles), np.full(64, z)])
                        for z in np.linspace(176.51, 205.49, 12)])
for label, points in (("carriage", slide + [64.5, 0, 149.2]),
                      ("motor", motor), ("wheel", wheel)):
    record(f"head-top-insertion-{label}", moved(points, [[0, 0, z] for z in np.linspace(100, .01, 65)]))

# Captured skirt nuts allow assembly with the upper shell complete and head
# removed. The rear shaft passes between the rear speaker and display frame.
speaker = trimesh.creation.box([77.8,25.49,77.8])
speaker.apply_translation([0,69.245,43])
record("rear-speaker-envelope", grid([-38.85,56.55,4.15], [38.85,81.94,81.85], 13))
assembled_slide = meshes["10_head_motor_carriage"].copy()
assembled_slide.apply_translation([61.5,0,149.2])
motor_mesh = trimesh.creation.box([22.44,70,22.4])
motor_mesh.apply_translation([61.5-11.7+11.22,-22,163.5])
wheel_mesh = trimesh.creation.cylinder(radius=31.5, height=29, sections=64)
wheel_mesh.apply_translation([61.5,0,191])
for label, anchor, angle, horizontal in [
        ("front", [0,-97,9.2],16,[0,1]),
        ("left", [-97,0,9.2],16,[1,0]),
        ("rear", [0,97,9.2],6.5,[0,-1]),
        ("right", [97,0,9.2],16,[-2**-.5,2**-.5])]:
    direction = np.array([horizontal[0]*np.sin(np.radians(angle)),
                          horizontal[1]*np.sin(np.radians(angle)), np.cos(np.radians(angle))])
    q = rod(anchor, np.array(anchor)+250*direction,1.74,150)
    for obstacle_name, obstacle in (("upper",upper), ("speaker",speaker),
                                    ("retracted-carriage",assembled_slide),
                                    ("head-motor",motor_mesh), ("wheel",wheel_mesh)):
        record(f"upper-joint-driver-{label}-{obstacle_name}",q,obstacle)

# Lower bearing and its three straight driver approaches enter through the
# open bottom, before the speaker and the complete upper shell are installed.
bearing = np.concatenate([np.column_stack([11*np.cos(angles), 11*np.sin(angles),
                                           np.full(64, z)]) for z in (.05, 3.5, 6.95)])
record("lower-bearing-bottom-insertion", moved(bearing, [[0, 0, z] for z in np.linspace(-10, 160, 90)]))
for a in (0, 120, 240):
    x, y = 14*np.cos(np.radians(a)), 14*np.sin(np.radians(a))
    q = np.concatenate([np.column_stack([x+1.2*np.cos(angles), y+1.2*np.sin(angles),
                                         np.full(64, z)]) for z in np.linspace(-20, 159, 90)])
    record(f"lower-bearing-driver-{a}", q)

assert hashes == {n: hashlib.sha256(p.read_bytes()).hexdigest() for n, p in paths.items()}, "Input mesh changed"
report = dict(design="MOUNT-1", method="Deterministic nominal mesh vertices and component grids; finite path samples",
              all_pass=all(r["passed"] for r in results), mesh_sha256=hashes, checks=results, query_method=METHOD,
              arm_box_outer_mm=[90, 52, 103], previous_arm_box_outer_mm=[94, 58, 106],
              upper_height_mm=float(upper.extents[2]),
              sampled_arm_root_sections=root_sections,
              limits=["No physical strength or hardware fit has been measured.",
                      "Manufacturer does not dimension MG92B shaft offset or ear-hole centers; verify actual parts against slots.",
                      "Fit the opaque arm liners and inspect their folds at every eight-degree extreme.",
                      "All lower access is with the upper shell removed; install speaker last."])
(ROOT / "cad/upper-mounts-checks.json").write_text(json.dumps(report, indent=2)+"\n", encoding="utf-8")
raise SystemExit(0 if report["all_pass"] else "Upper mount checks failed")
