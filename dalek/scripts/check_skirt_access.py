"""Focused nominal access checks for the merged ROUND-9 skirt.

Uses the existing trimesh/NumPy stack. Bounded batches avoid allocating a large
ray scene for the full assembly. These are finite envelope samples, not physical
fit, strength or a proof of collision-free continuous motion.
"""
import hashlib
import json
import sys
from pathlib import Path

import numpy as np
import trimesh


ROOT = Path(__file__).resolve().parents[1]
if sys.argv[1:] not in ([], ["--plates-only"]):
    raise SystemExit("Usage: check_skirt_access.py [--plates-only]")
PLATES_ONLY = sys.argv[1:] == ["--plates-only"]
SOURCE_HASHES = {name: hashlib.sha256((ROOT / "stl" / f"{name}.stl").read_bytes()).hexdigest()
                 for name in ("01_base", "02_skirt")}
PARTS = {name: trimesh.load_mesh(ROOT / "stl" / f"{name}.stl", process=True)
         for name in ("01_base", "02_skirt")}
for name, mesh in PARTS.items():
    if not (mesh.is_watertight and mesh.is_winding_consistent and mesh.volume > 0
            and mesh.body_count == 1):
        raise SystemExit(f"Refusing access samples against invalid solid: {name}")
PARTS["02_skirt"].apply_translation([0, 0, 54])
CHECKS = []
MOUNTS = np.array([[x, y] for x in (-54, 54) for y in (-93, -69, 69, 93)])
PLATE_INFO = {
    "slide_underside_z_mm": 44,
    "seated_underside_z_mm": 34,
    "maximum_retained_nut_washer_adhesive_projection_mm": 3,
    "underside_hardware_keepout_radius_about_base_mount_axes_mm": 8,
    "pcb_installation": "Retain thin M2.5 nuts (maximum1.6mm) with0.5mm underside washers; Pololu4091 uses M2 nuts (maximum1.6mm) and0.3mm washers. Fit no upper spacers or PCBs until the plate is seated.",
    "pcb_screw_stack": "M2.5x14 from above with two0.5mm head washers. Pololu4091 uses M2 screws trimmed to the measured stack with two0.3mm head washers (nominal13.5mm working length). Verify two complete threads and at least2mm actual motor-case clearance.",
    "physical_gate": "Keep every underside nut/washer/adhesive wholly within the plate outline and outside8mm mount keepouts; check actual PCB hole templates before assembly.",
}


def record(name, samples, hits):
    row = {"check": name, "samples": int(samples), "interior_hits": int(hits),
           "passed": bool(hits == 0)}
    CHECKS.append(row)
    print(json.dumps(row), flush=True)


def mesh_hits(mesh, points):
    points = points[((points > mesh.bounds[0]) & (points < mesh.bounds[1])).all(axis=1)]
    return sum(int(mesh.contains(points[i:i + 150]).sum())
               for i in range(0, len(points), 150))


def mesh_check(label, points):
    for name, mesh in PARTS.items():
        record(f"{label}-against-{name}", len(points), mesh_hits(mesh, points))


def grid(lo, hi, counts=(3, 3, 3)):
    return np.array([[x, y, z]
                     for x in np.linspace(lo[0], hi[0], counts[0])
                     for y in np.linspace(lo[1], hi[1], counts[1])
                     for z in np.linspace(lo[2], hi[2], counts[2])])


def box_hits(points, lo, hi):
    return int(((points > lo) & (points < hi)).all(axis=1).sum())


def mount_hits(points, radius, zmin, zmax):
    hits = np.zeros(len(points), dtype=bool)
    for mount in MOUNTS:
        hits |= ((np.linalg.norm(points[:, :2] - mount, axis=1) < radius)
                 & (points[:, 2] > zmin) & (points[:, 2] < zmax))
    return int(hits.sum())


def rotate(points, angle):
    matrix = trimesh.transformations.rotation_matrix(np.radians(angle), [0, 0, 1])[:3, :3]
    return points @ matrix.T


# Plates carry only retained PCB nuts/washers below them. No upper spacers,
# PCBs or battery are present. The raised44mm underside leaves retained
# fittings above41mm, clearing both34mm spacer tops and40mm screw tips.
plate = grid([-79.95, -27.95, .05], [79.95, 27.95, 1.95], (5, 5, 2))
for side in (-1, 1):
    poses = [(0, 0, z) for z in np.linspace(280, 44, 30)]
    poses += [(0, side * y, 44) for y in np.linspace(0, 93, 30)]
    poses += [(0, side * 93, z) for z in np.linspace(44, 34, 8)]
    points = np.concatenate([plate + pose for pose in poses])
    mesh_check(f"bare-plate-{side}-lower-slide-seat", points)
    record(f"bare-plate-{side}-preinstalled-spacers", len(points),
           mount_hits(points, 4, 9, 34))
    # During the final seating stage, the predrilled 2.8 mm holes intentionally
    # surround the 2.5 mm screws. Earlier stages must stay above their tips.
    moving = np.concatenate([plate + pose for pose in poses[:60]])
    record(f"bare-plate-{side}-preinstalled-screw-tips", len(moving),
           mount_hits(moving, 1.25, 0, 40))
    record(f"bare-plate-{side}-other-installed-plate", len(points),
           box_hits(points, [-80, -side * 93 - 28, 34],
                    [80, -side * 93 + 28, 36]))

    hardware = grid([-79.95, -27.95, -2.95], [79.95, 27.95, -.05], (9, 7, 3))
    critical = np.array([[x, y, z] for x in (-57, -55, 55, 57)
                         for y in (-27.95, -24, -20, 20, 24, 27.95)
                         for z in (-2.9, -1.9, -.1)])
    hardware = np.concatenate([hardware, critical])
    allowed = np.ones(len(hardware), dtype=bool)
    for mount in MOUNTS:
        relative = mount - [0, side * 93]
        allowed &= np.linalg.norm(hardware[:, :2] - relative, axis=1) > 8
    hardware = hardware[allowed]
    points = np.concatenate([hardware + pose for pose in poses])
    mesh_check(f"bare-plate-{side}-retained-hardware", points)
    record(f"bare-plate-{side}-retained-hardware-spacers", len(points),
           mount_hits(points, 4, 9, 34))
    record(f"bare-plate-{side}-retained-hardware-screw-tips", len(points),
           mount_hits(points, 1.25, 0, 40))
    record(f"bare-plate-{side}-retained-hardware-other-plate", len(points),
           box_hits(points, [-80, -side * 93 - 28, 34],
                    [80, -side * 93 + 28, 36]))

if PLATES_ONLY:
    path = ROOT / "cad" / "skirt-access-checks.json"
    previous = json.loads(path.read_text(encoding="utf-8"))
    if previous["mesh_sha256"] != SOURCE_HASHES:
        raise SystemExit("Cannot retain access results from different source meshes")
    for name, expected in SOURCE_HASHES.items():
        if hashlib.sha256((ROOT / "stl" / f"{name}.stl").read_bytes()).hexdigest() != expected:
            raise SystemExit(f"Source mesh changed during access checks: {name}")
    retained = [row for row in previous["checks"] if not row["check"].startswith("bare-plate-")]
    if not all(row["passed"] for row in retained):
        raise SystemExit("Cannot retain failed checks; run the full checker")
    previous["checks"] = CHECKS + retained
    previous["all_pass"] = all(row["passed"] for row in previous["checks"])
    previous["plate_assembly"] = PLATE_INFO
    previous["focused_refresh"] = {
        "command": "C:/Python314/python.exe scripts/check_skirt_access.py --plates-only",
        "rerun_checks": len(CHECKS), "retained_unchanged_checks": len(retained),
        "basis": "Only plate preparation/path changed; both exact source meshes and all tool/battery paths are unchanged.",
    }
    previous["limits"] = [line for line in previous["limits"] if "slides atZ41" not in line]
    if PLATE_INFO["physical_gate"] not in previous["limits"]:
        previous["limits"].append(PLATE_INFO["physical_gate"])
    path.write_text(json.dumps(previous, indent=2) + "\n", encoding="utf-8")
    raise SystemExit(0 if previous["all_pass"] else "Merged-skirt plate access sampling failed")

# The centered battery passes after both bare plates are secured. Leads and
# straps must be held above the pack, not allowed to trail into a wheel.
pack = grid([-34.95, -56.95, .05], [34.95, 56.95, 75.95], (5, 5, 5))
points = np.concatenate([pack + [0, 0, z] for z in np.linspace(280, 6, 35)])
mesh_check("battery-after-plates", points)
for side in (-1, 1):
    record(f"battery-against-installed-plate-{side}", len(points),
           box_hits(points, [-80, side * 93 - 28, 34],
                    [80, side * 93 + 28, 36]))
record("battery-against-preinstalled-spacers", len(points),
       mount_hits(points, 4, 9, 34))

# Bahco 677-7: 7 mm jaws, 5 mm jaw thickness, 22 mm width and 17.5 mm
# nut-to-square-drive offset. Additional unlabelled body dimensions below are
# explicit maximum acceptance envelopes to check on the physical tool.
# All coordinates in this script are base-local; the nut axis is radius 137.
crowfoot = np.concatenate([
    grid([128, -11, 42.05], [143, 11, 46.95]),
    grid([112.5, -7, 42.05], [128, 7, 51]),
    grid([112.5, -7, 47], [126.5, 7, 82]),
])
angles = np.linspace(0, 2 * np.pi, 16, endpoint=False)
shaft = []
for z in np.linspace(82, 324, 65):
    r = 119.5 - (z - 82) * np.tan(np.radians(16))
    shaft.extend(np.column_stack([r + 7 * np.cos(angles), 7 * np.sin(angles),
                                  np.full(len(angles), z)]))
nut_tool = np.concatenate([crowfoot, np.array(shaft)])
for angle in (0, 90, 180, 270):
    # Lower through the top with the jaw centre at radius 80, then slide it
    # out under the flange. The extension remains above the open skirt.
    points = np.concatenate([rotate(nut_tool + [-57, 0, dz], angle)
                             for dz in np.linspace(240, 0, 18)])
    mesh_check(f"crowfoot-{angle}-top-insertion", points)
    points = np.concatenate([rotate(nut_tool + [d, 0, 0], angle)
                             for d in np.linspace(-57, 0, 12)])
    mesh_check(f"crowfoot-{angle}-radial-slide", points)
    record(f"crowfoot-{angle}-preinstalled-screw-tips", len(points),
           mount_hits(points, 1.25, 0, 40))

# Hold the M2.5 screw heads below the raised, unpowered chassis. Tighten plate
# nuts before adding PCBs. The 5 mm socket and universal joint are bounded
# by a 14 mm diameter; a 250 mm or longer extension leans inward by 8 degrees.
for x, y in MOUNTS:
    radius = np.hypot(x, y)
    theta = np.degrees(np.arctan2(y, x))
    socket = []
    for z in np.linspace(36.05, 82, 15):
        socket.extend(np.column_stack([radius + 7 * np.cos(angles),
                                       7 * np.sin(angles), np.full(len(angles), z)]))
    for z in np.linspace(82, 332, 60):
        r = radius - (z - 82) * np.tan(np.radians(8))
        socket.extend(np.column_stack([r + 7 * np.cos(angles),
                                       7 * np.sin(angles), np.full(len(angles), z)]))
    tool = np.array(socket)
    poses = [(75 - radius, 0, dz) for dz in (250, 230, 220, 180, 90, 9)]
    poses += [(dr, 0, 9) for dr in np.linspace(75 - radius, 0, 8)]
    poses += [(0, 0, dz) for dz in (9, 6, 3, 0)]
    points = np.concatenate([rotate(tool + pose, theta) for pose in poses])
    mesh_check(f"plate-nut-tool-{x}-{y}-insert-shift-seat", points)

for name, expected in SOURCE_HASHES.items():
    if hashlib.sha256((ROOT / "stl" / f"{name}.stl").read_bytes()).hexdigest() != expected:
        raise SystemExit(f"Source mesh changed during access checks: {name}")
report = {
    "design": "ROUND-9", "all_pass": all(row["passed"] for row in CHECKS),
    "method": "Deterministic finite envelope samples; mesh ray batches capped at150 points",
    "coordinates": "Base-local millimetres; merged skirt originZ54; physical strength untested",
    "mesh_sha256": SOURCE_HASHES,
    "plate_assembly": PLATE_INFO,
    "sources": [
        "https://www.bahco.com/int_en/1-4--square-drive-crowfoot-open-end-wrench-7-mm-677-7.html",
        "https://pimdatacdn.bahco.com/media/sub139/16a81bc02e23f83f.png",
        "https://www.bahco.com/int_en/1-4--square-drive-universal-joint-35-mm-6966.html",
        "https://www.bahco.com/gb_en/1-4--square-drive-extension-bars-pb_6960---6962l_.html",
    ],
    "checks": CHECKS,
    "limits": [
        "Finite surface/interior samples do not prove every continuous path is clear.",
        "Bareplates precede PCBs and battery; reverse that order for service.",
        "Predrill plate holes using actual base mounts; screw shafts intentionally enter those holes at seating.",
        "Check real screw tips are at or below baseZ40 before the plate slides atZ44 with its retained fittings aboveZ41.",
        PLATE_INFO["physical_gate"],
        "Crowfoot boss height and jaw projection are measured tool-fit gates; only labelled vendor dimensions are sourced.",
        "Universal joint and extension couplers must remain inside the14mm envelope at the required bend.",
        "Sockets enter with their axes at radius75, shift outward with their bottoms aboveZ45, then descend onto the nuts.",
        "Real joints, hands, cables and PCB connectors need physical checks.",
        "These tests establish no material strength, layer-bond quality or load rating.",
    ],
}
(ROOT / "cad" / "skirt-access-checks.json").write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
raise SystemExit(0 if report["all_pass"] else "Merged-skirt access sampling failed")
