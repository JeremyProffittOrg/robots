"""Accelerate existing finite clearance samples without changing hit criteria.

Two nonparallel, nearly axial parity rays must agree. Disagreements use
trimesh's original contains query. Points on surfaces remain undefined, as in
trimesh; callers must express intended contacts with their existing offsets.
"""
import numpy as np
from trimesh.ray.ray_util import contains_points


METHOD = "Two independent near-axis parity rays; original trimesh.contains on disagreements"


def contains(mesh, points):
    points = np.asarray(points, dtype=float)
    result = np.zeros(len(points), dtype=bool)
    for start in range(0, len(points), 4096):
        batch = points[start:start+4096]
        first = contains_points(mesh.ray, batch, check_direction=[1, .001, .0007])
        second = contains_points(mesh.ray, batch, check_direction=[.0009, 1, .0011])
        disagree = first != second
        if disagree.any():
            first[disagree] = mesh.contains(batch[disagree])
        result[start:start+len(batch)] = first
    return result


if __name__ == "__main__":
    import hashlib
    import json
    from pathlib import Path
    import time
    import trimesh

    root = Path(__file__).resolve().parents[1]
    path = root / "stl/04_shoulder.stl"
    mesh = trimesh.load_mesh(path, process=True)
    rng = np.random.default_rng(24681357)
    samples = [rng.uniform([-90,-109,5], [90,90,185], (1800,3))]
    indices = rng.choice(len(mesh.faces), 400, replace=False)
    centers, normals = mesh.triangles_center[indices], mesh.face_normals[indices]
    for distance in (-.1, -.002, .002, .1):
        samples.append(centers + normals * distance)
    for x in (-47, 53):
        samples.append(rng.uniform([-16.2,-5.9,7.1], [6.2,5.9,37.9], (300,3)) + [x,-94,0])
        samples.append(rng.uniform([-25.8,-12.8,10], [-22.2,-7.2,24], (200,3)) + [x,-94,0])
    points = np.concatenate(samples)
    start = time.perf_counter()
    original = mesh.contains(points)
    original_time = time.perf_counter()-start
    start = time.perf_counter()
    accelerated = contains(mesh, points)
    accelerated_time = time.perf_counter()-start
    report = dict(design="MOUNT-1", method=METHOD, seed=24681357, samples=len(points),
                  inside=int(original.sum()), outside=int((~original).sum()),
                  mismatches=int(np.count_nonzero(original != accelerated)),
                  default_seconds=round(original_time,3), accelerated_seconds=round(accelerated_time,3),
                  sample_description="1800 uniform shell-envelope points;1600 face-center offsets at+/-0.002 and+/-0.1mm;600 nominal servo-case void points;400 solid yaw-wall points",
                  mesh_sha256=hashlib.sha256(path.read_bytes()).hexdigest(),
                  all_pass=bool(np.array_equal(original, accelerated)))
    (root / "cad/mesh-query-validation.json").write_text(json.dumps(report, indent=2)+"\n", encoding="utf-8")
    print(json.dumps(report), flush=True)
    raise SystemExit(0 if report["all_pass"] else "Mesh query comparison failed")
