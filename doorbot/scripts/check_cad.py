"""CAD authority for doorbot: mesh health, print envelope, gear meshing and internal collisions.

Every number is derived from cad/params.scad or measured off the exported STL. Run after
scripts/export_cad.py. Exit 1 on any failed check.

    python scripts/check_cad.py
"""
import itertools
import json
import math

import trimesh

from scad_params import ROOT, params, require

# part -> (quantity, is it allowed to contain sealed internal voids and how many)
PARTS = {
    "base_shell": (1, 0),
    "base_cover": (1, 0),
    "motor_pinion": (1, 0),
    "compound_gear": (1, 0),
    "drum_gear": (1, 0),
    "door_anchor": (1, 0),
    "magnet_pod": (2, 2),      # two sealed magnet pockets, closed by bridged cap layers
}
DENSITY_G_CM3 = 1.24           # Bambu Lab PLA Tough+ published density


def boxes(p):
    """Every solid thing inside the shell as an axis-aligned box in the unit frame.

    Returned as name -> (x0, y0, z0, x1, y1, z1). The point of listing them is that the
    overlap test below is then exhaustive: any two things that share space are found, instead
    of the eye being trusted on a 244 mm tall assembly.
    """
    def gear_ro(m, n):
        return m * n / 2 + m

    out = {}
    mx, my = p["motor_axis"]
    out["motor"] = (mx - p["tt_body_w"] / 2, my - p["tt_axis_from_gearbox_end"], p["motor_z"],
                    mx + p["tt_body_w"] / 2, my - p["tt_axis_from_gearbox_end"] + p["tt_body_l"],
                    p["motor_z"] + p["tt_body_h"])
    wheels = [
        ("stage1_wheel", p["compound_axis"], gear_ro(p["module1"], p["stage1_gear_t"]),
         p["plane1_z"], p["face1"]),
        ("stage1_pinion", p["motor_axis"], gear_ro(p["module1"], p["stage1_pinion_t"]),
         p["plane1_z"], p["face1"]),
        ("stage2_pinion", p["compound_axis"], gear_ro(p["module2"], p["stage2_pinion_t"]),
         p["plane2_z"], p["face2"]),
        ("stage2_wheel", p["drum_axis"], gear_ro(p["module2"], p["stage2_gear_t"]),
         p["plane2_z"], p["face2"]),
        ("drum", p["drum_axis"], p["drum_flange_d"] / 2, p["drum_z"], p["drum_width"]),
        ("encoder_wheel", p["motor_axis"], p["encoder_wheel_d"] / 2,
         p["motor_z"] + p["tt_body_h"], 3.0),
    ]
    for name, axis, r, z0, h in wheels:
        out[name] = (axis[0] - r, axis[1] - r, z0, axis[0] + r, axis[1] + r, z0 + h)
    for name, pos, w, l, t in [
            ("tdisplay", p["tdisp_pos"], p["tdisp_w"], p["tdisp_l"], p["tdisp_t"]),
            ("driver", p["drv_pos"], p["drv_w"], p["drv_l"], p["drv_t"]),
            ("accelerometer", p["accel_pos"], p["accel_w"], p["accel_l"], p["accel_t"]),
            ("tof_wave", p["tof_wave_pos"], p["tof_w"], p["tof_l"], p["tof_t"]),
            ("tof_guard", p["tof_guard_pos"], p["tof_w"], p["tof_l"], p["tof_t"])]:
        out[name] = (pos[0], pos[1], pos[2], pos[0] + w, pos[1] + l, pos[2] + t)
    out["sensor_shelf"] = (p["wall"], p["shelf_y0"], p["shelf_z"],
                           p["base_w"] - p["wall"], p["shelf_y1"], p["shelf_z"] + p["shelf_t"])
    out["nose_root"] = (p["nose_x"] - p["nose_w"] / 2, 0, 0,
                        p["base_w"], p["nose_y"] + p["nose_h"] / 2, p["base_z"])
    return out


def overlap(a, b, slack=0.0):
    """Overlap volume of two boxes, shrunk by slack on every face."""
    d = [min(a[i + 3], b[i + 3]) - max(a[i], b[i]) - 2 * slack for i in range(3)]
    return 0.0 if any(v <= 0 for v in d) else d[0] * d[1] * d[2]


# Pairs that are meant to share space: a gear pair has to overlap to mesh at all, and a
# co-axial compound part is one print. Everything else must be clear.
ALLOWED = {
    frozenset(("stage1_pinion", "stage1_wheel")),
    frozenset(("stage2_pinion", "stage2_wheel")),
    frozenset(("stage1_wheel", "stage2_pinion")),
    frozenset(("stage2_wheel", "drum")),
    frozenset(("motor", "stage1_pinion")),
    frozenset(("motor", "encoder_wheel")),
    frozenset(("sensor_shelf", "tof_wave")),
    frozenset(("sensor_shelf", "tof_guard")),
    frozenset(("tof_wave", "tof_guard")),
}


def main():
    p = params()
    checks = []

    def check(name, ok, detail):
        checks.append({"check": name, "pass": bool(ok), "detail": detail})

    # ---- meshes
    rows = []
    for name, (qty, voids) in PARTS.items():
        path = ROOT / "stl" / f"{name}.stl"
        if not path.exists():
            check(f"mesh_{name}", False, f"{path} is missing - run scripts/export_cad.py")
            continue
        mesh = trimesh.load_mesh(path)
        pieces = mesh.split(only_watertight=False)
        solids = [s for s in pieces if s.volume > 0]
        sealed = [s for s in pieces if s.volume < 0]
        fits = all(mesh.extents[i] <= [p["env_x"], p["env_y"], p["env_z"]][i] + 0.001
                   for i in range(3))
        mass = mesh.volume / 1000.0 * DENSITY_G_CM3
        rows.append({"part": name, "quantity": qty,
                     "x_mm": round(float(mesh.extents[0]), 2),
                     "y_mm": round(float(mesh.extents[1]), 2),
                     "z_mm": round(float(mesh.extents[2]), 2),
                     "solid_volume_cm3": round(mesh.volume / 1000.0, 2),
                     "solid_mass_g": round(mass, 1),
                     "watertight": bool(mesh.is_watertight),
                     "bodies": len(solids), "sealed_voids": len(sealed)})
        check(f"mesh_{name}",
              mesh.is_watertight and mesh.is_winding_consistent and len(solids) == 1
              and len(sealed) == voids and fits and mesh.bounds[0][2] >= -0.001,
              f"{name}: watertight={mesh.is_watertight} bodies={len(solids)} "
              f"sealed_voids={len(sealed)}/{voids} "
              f"{mesh.extents[0]:.1f} x {mesh.extents[1]:.1f} x {mesh.extents[2]:.1f} mm, "
              f"{mass:.0f} g solid, sits on z=0")

    # ---- part count, which the user capped
    check("part_count", len(PARTS) < 10,
          f"{len(PARTS)} distinct printed designs, {sum(q for q, _ in PARTS.values())} printed "
          f"pieces in total. The cap was fewer than 10 designs")

    # ---- print envelope of the tallest part against the smallest current Bambu bed
    shell = trimesh.load_mesh(ROOT / "stl/base_shell.stl")
    check("fits_bambu_bed",
          max(shell.extents) <= min(p["env_x"], p["env_y"], p["env_z"]),
          f"the shell is the largest part at {shell.extents[0]:.0f} x {shell.extents[1]:.0f} x "
          f"{shell.extents[2]:.0f} mm, inside a {p['env_x']:.0f} mm cube, so it prints on a P1S, "
          f"an X1C, an A1 or an H2D without splitting")

    # ---- the shell must stay inside the jamb rebate
    check("shell_within_rebate", shell.extents[0] <= p["rebate_depth_mm"],
          f"the shell measures {shell.extents[0]:.1f} mm across the jamb depth against the "
          f"{p['rebate_depth_mm']:.0f} mm rebate of a 4-9/16 in jamb")
    check("nose_reaches_exit", abs(shell.extents[2] - p["exit_x"]) <= 0.5,
          f"the nose tip stands {shell.extents[2]:.1f} mm out into the opening, which is where "
          f"check_mechanism.py puts the cable exit ({p['exit_x']:.0f} mm from the hinge axis)")

    # ---- gear meshing, from first principles
    for tag, m, pt, gt, cd_axes in [
            ("stage1", p["module1"], p["stage1_pinion_t"], p["stage1_gear_t"],
             (p["motor_axis"], p["compound_axis"])),
            ("stage2", p["module2"], p["stage2_pinion_t"], p["stage2_gear_t"],
             (p["compound_axis"], p["drum_axis"]))]:
        want = m * (pt + gt) / 2.0
        got = math.dist(cd_axes[0], cd_axes[1])
        check(f"{tag}_centre_distance", abs(want - got) < 0.05,
              f"{tag}: {pt}T on {gt}T at module {m} needs a {want:.2f} mm centre distance; the "
              f"axes in params.scad are {got:.2f} mm apart")
        # tip of each must not touch the root of the other
        tip_clear = got - (m * gt / 2 + m) - (m * pt / 2 - m * (1 + p["gear_clearance"]))
        check(f"{tag}_tip_clearance", tip_clear > 0.05,
              f"{tag}: {tip_clear:.2f} mm between the wheel's tip circle and the pinion's root "
              f"circle, so the teeth engage without bottoming")

    # ---- nothing inside the shell shares space with anything else
    box = boxes(p)
    clashes = []
    for a, b in itertools.combinations(sorted(box), 2):
        if frozenset((a, b)) in ALLOWED:
            continue
        v = overlap(box[a], box[b])
        if v > 1.0:
            clashes.append(f"{a}/{b} {v:.0f} mm3")
    check("no_internal_collisions", not clashes,
          "every board, the motor, both gear planes, the drum, the encoder wheel, the sensor "
          "shelf and the nose root occupy disjoint space"
          if not clashes else "overlapping: " + ", ".join(clashes))

    # ---- each wheel has to clear the plain cavity, since no local sweeps are cut for it
    def gear_ro(m, n):
        return m * n / 2 + m
    tight = []
    for name, axis, r in [
            ("stage1_wheel", p["compound_axis"], gear_ro(p["module1"], p["stage1_gear_t"])),
            ("stage2_wheel", p["drum_axis"], gear_ro(p["module2"], p["stage2_gear_t"]))]:
        gap_x = min(axis[0] - p["wall"] - r, p["base_w"] - p["wall"] - axis[0] - r)
        gap_y = min(axis[1] - p["wall"] - r, p["base_h"] - p["wall"] - axis[1] - r)
        if min(gap_x, gap_y) < 0.3:
            tight.append(f"{name} clears the cavity wall by only {min(gap_x, gap_y):.2f} mm")
    check("wheels_clear_cavity", not tight,
          "both wheels turn inside the plain cavity with clearance, so the shell needs no local "
          "sweep pockets - cutting those was what removed the floor under the dowel bosses"
          if not tight else "; ".join(tight))

    # ---- the two ToF sensors must not see each other's cone or the shelf edge
    sep = abs(p["tof_guard_pos"][0] - p["tof_wave_pos"][0])
    check("sensor_separation", sep >= p["window_d"] + 4,
          f"the hand-wave and doorway windows are {sep:.0f} mm apart with {p['window_d']:.0f} mm "
          f"apertures, so neither cone clips the other's bezel")

    report = {"all_pass": all(c["pass"] for c in checks), "analysis_only": True,
              "printed_designs": len(PARTS),
              "printed_pieces": sum(q for q, _ in PARTS.values()),
              "solid_mass_total_g": round(sum(r["solid_mass_g"] * r["quantity"] for r in rows), 1),
              "checks": checks, "parts": rows}
    (ROOT / "docs").mkdir(parents=True, exist_ok=True)
    (ROOT / "docs/cad.json").write_text(json.dumps(report, indent=2))
    for c in checks:
        print(("PASS  " if c["pass"] else "FAIL  ") + c["check"] + ": " + c["detail"])
    print(f"\n{report['printed_designs']} designs / {report['printed_pieces']} pieces, "
          f"{report['solid_mass_total_g']} g of PLA Tough+ at 100% infill")
    if not report["all_pass"]:
        raise SystemExit("FAILED: " + ", ".join(c["check"] for c in checks if not c["pass"]))
    print("PASS: CAD analysis.")


if __name__ == "__main__":
    main()
