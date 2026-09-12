"""Check carrier/pitch-servo insertion after both detached arms are supported.

Run separately from check_mechanical.py for this assembly-order regression.
No geometry is exported or changed.
"""
import hashlib
import json
from pathlib import Path

import numpy as np
import trimesh
from mesh_queries import contains, METHOD

ROOT = Path(__file__).resolve().parents[1]
NAMES = ("04_shoulder", "07_pitch_carrier", "08_plunger_arm", "09_emitter_arm")
meshes = {name: trimesh.load_mesh(ROOT / "stl" / f"{name}.stl", process=True) for name in NAMES}
rotation = (trimesh.transformations.rotation_matrix(np.radians(-90), [0, 0, 1]) @
            trimesh.transformations.rotation_matrix(np.radians(90), [1, 0, 0]))[:3, :3]
arms = []
for x, name in ((-47, "08_plunger_arm"), (53, "09_emitter_arm")):
    arm = meshes[name].copy()
    arm.vertices = (arm.vertices - [0, 0, 28]) @ rotation.T + [x - 3, -94, 77]
    arms.append(arm)
held_arms = trimesh.util.concatenate(arms)
case_points = np.array(np.meshgrid(np.linspace(1.05, 31.95, 6),
                                  np.linspace(-5.95, 5.95, 5),
                                  np.linspace(18.75, 41.25, 8), indexing="ij")).reshape(3, -1).T
results = []
for x, entry_x in ((-47, -29), (53, -29)):
    poses = [(entry_x, 25, z) for z in np.linspace(-55, 88, 60)]
    poses += [(entry_x, y, 88) for y in np.linspace(25, -44, 30)]
    poses += [(entry_x, -44, z) for z in np.linspace(88, 46, 20)]
    poses += [(entry_x + (x - entry_x) * t, -44, 46) for t in np.linspace(0, 1, 13)]
    poses += [(x, y, 46) for y in np.linspace(-44, -94, 26)]
    poses += [(x, -94, z) for z in np.linspace(46, 42, 5)]
    for label, points in (("carrier", meshes["07_pitch_carrier"].vertices), ("pitch-case", case_points)):
        for obstacle_name, obstacle in (("held-arms", held_arms), ("shoulder", meshes["04_shoulder"])):
            hits = 0
            for pose in poses:
                hits += int(contains(obstacle, points + np.array(pose)).sum())
            result = dict(check=f"{label}-insertion-{x}-against-{obstacle_name}", poses=len(poses),
                          samples=len(poses) * len(points), interior_hits=hits, passed=hits == 0)
            results.append(result)
            print(json.dumps(result), flush=True)
report = dict(design="MOUNT-1", assembly_order="Remove upper shell; install yaw servos; feed and support both arms through lower opening; insert both carriers through the left lower opening, then forward and down; horns and liners; rear speaker last.",
              method="Deterministic mesh vertices and nominal pitch-servo interior grid at 154 insertion poses per side.",
              all_pass=all(row["passed"] for row in results), query_method=METHOD,
              mesh_sha256={name: hashlib.sha256((ROOT / "stl" / f"{name}.stl").read_bytes()).hexdigest() for name in NAMES},
              checks=results,
              limits=["Finite sampling does not prove continuous-path clearance.",
                      "Actual horns, wiring, fabric, supports and print tolerances require a careful hand fit."])
(ROOT / "cad" / "arm-assembly-checks.json").write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
raise SystemExit(0 if report["all_pass"] else "Arm assembly-order clearance failed")
