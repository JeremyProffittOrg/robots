"""Render the fable-r2d2 revision D assembly, simulated operation and stance change as a 1920x1080 MP4.

Every printed piece is the delivered STL, placed by scripts/assembly_layout.py exactly as
cad/r2d2.scad places it. Stance poses come from the same kinematics (scripts/stability.py Stance):
the scene receives a table of body, carriage, housing and foot matrices over the whole actuator
stroke and plays the phases the storyboard lists. Purchased hardware is drawn as nominal envelopes
from cad/params.scad and cad/lib.scad. Frames are rendered in headless Chrome with a small WebGL2
renderer (scripts/video_scene.js) and piped as JPEG into FFmpeg; the soundtrack is built by
scripts/build_video_audio.ps1 from Windows System.Speech narration and the original robot WAVs in
firmware/pi/sounds. Storyboard {TOKENS} are filled from scripts/parts.json and the CAD first.

No network, no printer, no robot and no scheduled task is touched.

    python scripts/render_video.py --preview            # keyframe PNGs into output/video/review
    python scripts/render_video.py --allow-missing      # skip STLs that are not exported yet
    python scripts/render_video.py --check-story        # validate and resolve the storyboard only
    python scripts/render_video.py                      # full render, verify, manifest, poster
"""
import argparse
import base64
from functools import partial
import hashlib
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
import io
import json
import math
from pathlib import Path
import re
import shutil
import subprocess
import sys
import tempfile
import threading
import time

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent))
from assembly_layout import REVISION, STANCE_PARAMETER, Layout, T, R, number_word, package_counts  # noqa: E402

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "output/video"
CHROME = Path("C:/Program Files/Google/Chrome/Application/chrome.exe")
STORY_PATH = ROOT / "scripts/video_storyboard.json"
SCENE_JS = ROOT / "scripts/video_scene.js"
WIDTH, HEIGHT = 1920, 1080
VIDEO = OUT / "r2d2-assembly-and-operation.mp4"
RENDER_CEILING_SECONDS = 1740  # hard stop below the 30-minute quality bar
POSE_STEP_MM = 0.1
STROKE_NAMES = ("two_foot", "contact", "three_leg")
TOKEN_RE = re.compile(r"\{([A-Z_]+)\}")
RUNTIME_TOKENS = {"HEIGHT"}


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def cm(matrix):
    """4x4 numpy (row-major) -> flat column-major list for WebGL."""
    return [float(v) for v in np.asarray(matrix, dtype=float).T.ravel()]


# ---------------------------------------------------------------- storyboard
def story_tokens(counts, lay):
    """Values for the storyboard {TOKENS}, all read from scripts/parts.json and the CAD."""
    return {
        "DESIGNS": str(counts["designs"]), "PIECES": str(counts["pieces"]),
        "DESIGNS_WORD": number_word(counts["designs"]), "PIECES_WORD": number_word(counts["pieces"]),
        "DESIGNS_WORD_CAP": number_word(counts["designs"]).capitalize(),
        "PIECES_WORD_CAP": number_word(counts["pieces"]).capitalize(),
        "TWO_FOOT_LIFT": f"{lay.centre_foot_lift(lay.endpoints()['two_foot']):.0f}",
    }


def resolve_story(story, tokens):
    """Copy of the storyboard with every {TOKEN} filled; {HEIGHT} stays for the render."""
    resolved = json.loads(json.dumps(story))
    for chapter in resolved["chapters"]:
        for field in ("title", "instruction", "narration"):
            text = chapter.get(field, "")
            unknown = sorted({name for name in TOKEN_RE.findall(text) if name not in tokens and name not in RUNTIME_TOKENS})
            if unknown:
                raise ValueError(f"storyboard chapter {chapter['name']} {field} has unknown tokens {unknown}")
            chapter[field] = TOKEN_RE.sub(lambda m: tokens.get(m.group(1), m.group(0)), text)
        if TOKEN_RE.search(chapter.get("narration", "")):
            raise ValueError(f"narration of {chapter['name']} would speak a raw token")
    return resolved


def validate_story(story):
    """Structural checks the renderer and the soundtrack rely on; raises ValueError."""
    chapters = story["chapters"]
    if story.get("revision") != REVISION:
        raise ValueError(f"storyboard revision {story.get('revision')} is not {REVISION}")
    cursor, legacy = 0.0, 0.0
    for chapter in chapters:
        name = chapter["name"]
        if abs(chapter["start"] - cursor) > 1e-9 or chapter["end"] <= chapter["start"]:
            raise ValueError(f"chapter {name} does not continue at {cursor} s")
        a, b = chapter["legacy"]
        if a < legacy - 1e-9 or (b != a and abs((b - a) - (chapter["end"] - chapter["start"])) > 1e-9):
            raise ValueError(f"chapter {name} legacy span {a}..{b} must continue the timeline and hold or play at 1x")
        legacy = b
        for phase in chapter.get("stance", {}).get("phases", []):
            if phase["stroke_to"] not in STROKE_NAMES or not 0 <= phase["start"] < phase["end"] <= chapter["end"] - chapter["start"]:
                raise ValueError(f"chapter {name} phase {phase['phase']} is outside the chapter or names an unknown stroke")
        cursor = chapter["end"]
    if abs(cursor - story["total_seconds"]) > 1e-9:
        raise ValueError(f"chapters end at {cursor} s but total_seconds is {story['total_seconds']}")
    for key in story["keyframes"]:
        if not 0 <= key < story["total_seconds"]:
            raise ValueError(f"keyframe {key} is outside the video")
    unseen = [c["name"] for c in chapters if not any(c["start"] <= k < c["end"] for k in story["keyframes"])]
    if unseen:
        raise ValueError(f"chapters without a keyframe: {unseen}")
    if not any(c.get("stance") and c["stance"]["end_state"] == "TWO_FOOT" for c in chapters) or \
            not any(c.get("stance") and c["stance"]["end_state"] == "THREE_FOOT" for c in chapters):
        raise ValueError("the storyboard must show both stance changes")
    return True


def video_time(story, legacy_time):
    """Video time at which the scene plays a given legacy (assembly-timeline) time."""
    for chapter in story["chapters"]:
        a, b = chapter["legacy"]
        if b > a and a - 1e-9 <= legacy_time < b:
            return chapter["start"] + (legacy_time - a)
    raise ValueError(f"legacy time {legacy_time} is not played by any chapter")


def phase_windows(story):
    """(chapter, phase, video start, video end) for every stance phase."""
    return [(c["name"], p["phase"], c["start"] + p["start"], c["start"] + p["end"])
            for c in story["chapters"] for p in c.get("stance", {}).get("phases", [])]


# ---------------------------------------------------------------- meshes
def scad_numbers(path, names):
    """Tolerant `name = <number>;` reader for constants assembly_layout's parser drops."""
    text = re.sub(r"//[^\n]*", "", Path(path).read_text(encoding="utf-8"))
    found = {}
    for name in names:
        match = re.search(rf"(?<![A-Za-z0-9_$]){re.escape(name)}\s*=\s*([-+]?[0-9]*\.?[0-9]+)\s*;", text)
        if match:
            found[name] = float(match.group(1))
    return found


def shifted(mesh, xyz):
    mesh = mesh.copy()
    mesh.apply_translation(xyz)
    return mesh


def rotated(mesh, angle, axis):
    import trimesh
    mesh = mesh.copy()
    mesh.apply_transform(trimesh.transformations.rotation_matrix(angle, axis))
    return mesh


def tube(points, radius=1.5, sides=8, closed=False):
    import trimesh
    points = np.asarray(points, dtype=float)
    tangents = np.gradient(points, axis=0) if not closed else np.roll(points, -1, axis=0) - np.roll(points, 1, axis=0)
    tangents /= np.linalg.norm(tangents, axis=1)[:, None]
    reference = np.tile([0.0, 0.0, 1.0], (len(points), 1))
    reference[np.abs(tangents[:, 2]) > 0.9] = [1, 0, 0]
    normals = np.cross(tangents, reference)
    normals /= np.linalg.norm(normals, axis=1)[:, None]
    binormals = np.cross(tangents, normals)
    angles = np.arange(sides) * 2 * np.pi / sides
    vertices = (points[:, None, :] + radius * (np.cos(angles)[None, :, None] * normals[:, None, :]
                                               + np.sin(angles)[None, :, None] * binormals[:, None, :])).reshape(-1, 3)
    faces = []
    for j in range(len(points) if closed else len(points) - 1):
        nxt = (j + 1) % len(points)
        for k in range(sides):
            a = j * sides + k
            b = j * sides + (k + 1) % sides
            c = nxt * sides + k
            d = nxt * sides + (k + 1) % sides
            faces.extend([[a, c, b], [b, c, d]])
    return trimesh.Trimesh(vertices=vertices, faces=faces, process=False)


def bolt(diameter, length, head_diameter, head_height):
    """Head sits at z = 0..head_height; the shank runs down to z = -length."""
    import trimesh
    shank = shifted(trimesh.creation.cylinder(radius=diameter / 2, height=length, sections=16), (0, 0, -length / 2))
    head = shifted(trimesh.creation.cylinder(radius=head_diameter / 2, height=head_height, sections=6), (0, 0, head_height / 2))
    return trimesh.util.concatenate([shank, head])


def helix(radius, wire_radius, length, turns, segments=90):
    u = np.linspace(0, 1, segments)
    points = np.stack([radius * np.cos(2 * np.pi * turns * u), radius * np.sin(2 * np.pi * turns * u), length * u], axis=1)
    return tube(points, wire_radius, sides=6)


def tt_motor_mesh(p):
    """Adafruit 3777 envelope in cad/lib.scad's tt_motor() frame: shaft along Y, can toward -X."""
    import trimesh
    gear_len, gear_h, thick = p["tt_gear_len"], p["tt_gear_h"], p["tt_thick"]
    front = p["tt_axle_from_front"]
    can_len = p["tt_len"] - gear_len
    gearbox = shifted(trimesh.creation.box(extents=[gear_len, thick, gear_h]), (front - gear_len / 2, 0, 0))
    can = rotated(trimesh.creation.cylinder(radius=p["tt_can_d"] / 2, height=can_len, sections=20), np.pi / 2, [0, 1, 0])
    can = shifted(can, (front - gear_len - can_len / 2, 0, 0))
    shaft_len = p["tt_shaft_l1"] + thick + p["tt_shaft_l2"]
    shaft = rotated(trimesh.creation.cylinder(radius=p["tt_shaft_d"] / 2, height=shaft_len, sections=14), -np.pi / 2, [1, 0, 0])
    shaft = shifted(shaft, (0, -thick / 2 - p["tt_shaft_l1"] + shaft_len / 2, 0))
    tab = shifted(trimesh.creation.box(extents=[6, 8, 6]), (front - p["tt_len"] - 1.8, 0, 0))
    return trimesh.util.concatenate([gearbox, can, shaft, tab])


def wheel_mesh(p):
    """Adafruit 3766 envelope, axis along Z, centred: 63 mm diameter, 29 mm wide."""
    import trimesh
    radius, width = p["wheel_d"] / 2, p["wheel_w"]
    tyre = trimesh.creation.annulus(r_min=radius - 4.5, r_max=radius, height=width, sections=44)
    hub = trimesh.creation.annulus(r_min=7, r_max=radius - 4.5, height=width - 4, sections=44)
    return trimesh.util.concatenate([tyre, hub])


def wheel_mark_mesh(p):
    """One radial tread rib, drawn dark so the rolling direction is visible."""
    import trimesh
    radius = p["wheel_d"] / 2
    return shifted(trimesh.creation.box(extents=[3.2, 3.0, p["wheel_w"] + 0.4]), (radius - 1.4, 0, 0))


def primitives(p):
    import trimesh
    meshes = {
        "cube": trimesh.creation.box(extents=[1, 1, 1]),
        "cylinder": trimesh.creation.cylinder(radius=1, height=1, sections=32),
        "disc": trimesh.creation.cylinder(radius=1, height=1, sections=44),
        "motor": tt_motor_mesh(p),
        "wheel": wheel_mesh(p),
        "wheel_mark": wheel_mark_mesh(p),
        "spring": helix(p["hd_spring_od"] / 2, 1.1, p["hd_spring_free"], 6),
    }
    # Unit annulus: outer radius 1, inner radius 0.5, height 1 (scaled per use).
    meshes["ring"] = trimesh.creation.annulus(r_min=0.5, r_max=1.0, height=1.0, sections=64)
    meshes["ring_thin"] = trimesh.creation.annulus(r_min=0.88, r_max=1.0, height=1.0, sections=72)
    meshes["bearing"] = trimesh.creation.annulus(r_min=p["caster_bearing_od"] / 2 - 8,
                                                 r_max=p["caster_bearing_od"] / 2,
                                                 height=p["caster_bearing_t"], sections=36)
    for name, m, length in [("bolt3", 3, 16), ("bolt4", 4, 30), ("bolt4l", 4, 86), ("bolt5", 5, 44),
                            ("bolt8", 8, 95), ("bolt8m", 8, 66), ("bolt12", 12, 150), ("bolt8s", 8, 34),
                            ("bolt4p", 4, 45), ("bolt8h", 8, 35)]:
        meshes[name] = bolt(m, length, m * 1.85, m * 0.7)
    for name, m in [("nut3", 3), ("nut4", 4), ("nut5", 5), ("nut8", 8), ("nut12", 12)]:
        meshes[name] = trimesh.creation.annulus(r_min=m / 2, r_max=m * 0.95, height=m * 0.8, sections=6)
    meshes["washer"] = trimesh.creation.annulus(r_min=0.55, r_max=1.0, height=1.0, sections=24)
    meshes["thumbnut"] = trimesh.util.concatenate([
        trimesh.creation.annulus(r_min=2.6, r_max=9, height=7, sections=18),
        *[shifted(trimesh.creation.box(extents=[2, 2.4, 7]), (9 * math.cos(a), 9 * math.sin(a), 0))
          for a in np.linspace(0, 2 * np.pi, 12, endpoint=False)]])
    return meshes


def roll_sign(matrix, radius):
    """Sign that makes a wheel roll the right way for forward (+Y) travel.

    video_scene.js rotates each wheel by spin_sign * (-distance / radius) about the mesh's own
    Z axis. Mirrored (negative determinant) foot matrices flip both the axis direction and the
    handedness, so the determinant alone does not decide this. Measure it instead: rotate a rim
    material point and require the one touching the floor to travel backwards.
    """
    matrix = np.asarray(matrix, dtype=float)
    angles = np.linspace(0, 2 * np.pi, 720, endpoint=False)
    points = np.stack([radius * np.cos(angles), radius * np.sin(angles),
                       np.zeros_like(angles), np.ones_like(angles)], axis=1)
    world = points @ matrix.T
    contact = int(np.argmin(world[:, 2]))
    step = 1e-3
    spin = np.eye(4)
    spin[0, 0] = spin[1, 1] = math.cos(step)
    spin[0, 1] = -math.sin(step)
    spin[1, 0] = math.sin(step)
    moved = matrix @ spin @ points[contact]
    per_radian = (moved[1] - world[contact, 1]) / step
    sign = 1.0 if per_radian > 0 else -1.0
    # applied local angle for one metre forward must drive the contact point backwards
    assert per_radian * sign * (-1000.0 / radius) < 0
    return sign


# cad/legs.scad, feet.scad and head_drive.scad define constants inside files that also contain
# modules. assembly_layout._read_scad_assignments splits those files on ";" and silently drops any
# assignment whose chunk begins with a leftover "}", so a constant can disappear whenever the CAD
# owner moves code. Refill the gaps from the formulas the .scad files document, and refuse to
# render if anything the scene needs is still missing.
def backfill(lay):
    """Restore CAD constants the scad reader dropped; raise if any are unrecoverable."""
    p, legs, feet, head = lay.p, lay.legs, lay.feet, lay.head
    pivot_up = feet.get("ft_pivot_up", 6.3)
    restored = []

    def fill(store, key, value):
        if key not in store:
            store[key] = value
            restored.append(key)

    fill(legs, "lg_hs_top", p["horseshoe_w"] / 2)
    fill(legs, "lg_tongue_bottom_z", -p["leg_len"] - pivot_up - p["leg_tongue_depth"])
    fill(legs, "lg_rod_x", p["leg_strut_t"] / 2)
    fill(legs, "lg_splice_x", [5, p["leg_strut_t"] - 5])
    fill(legs, "lg_splice_z", [p["leg_split_z"] + 10, p["leg_split_z"] + 30])
    fill(legs, "lg_bearing1_z", p["lg_center_bottom_z"])
    fill(legs, "lg_bearing2_z", p["lg_center_bottom_z"] + p["caster_bearing_gap"])
    fill(head, "hd_base_top", -p["body_top_plate_t"])
    fill(head, "hd_hinge_y", -82)
    fill(head, "hd_motor_y", -(p["head_wheel_r"] + head.get("hd_hinge_y", -82) - p["wheel_x"]))
    fill(head, "hd_tension_xy", [44, head["hd_hinge_y"] - 26])
    fill(head, "hd_stop_xy", [44, head["hd_hinge_y"] - 41])
    fill(head, "hd_spring_od", 10)
    fill(head, "hd_spring_free", 25)
    fill(feet, "ft_pivot_z", p["foot_outer_h"] + pivot_up)
    fill(feet, "ft_lock_r", p["ankle_bolt_spacing"] * 0.8)
    fill(feet, "ft_stop_r", 22)
    fill(feet, "ft_pin_d", 6)
    fill(feet, "ft_pin_h", 8)
    if restored:
        print("!! CAD constants not parsed by assembly_layout; refilled from the documented "
              f"formulas: {', '.join(sorted(restored))}", flush=True)
    return restored


# Every params.scad / derived name scripts/video_scene.js reads. A missing one is a NaN matrix,
# so the render stops instead of producing a silently wrong frame.
SCENE_KEYS = [
    "ankle_y", "caster_axis_y", "caster_trail", "leg_offset_x", "body_tilt", "foot_clear",
    "foot_center_h", "foot_outer_h", "caster_stop_deg", "body_r", "body_wall", "body_height",
    "body_lower_h", "body_top_plate_z", "shoulder_z", "shoulder_spacer", "leg_strut_t", "leg_rod_offset",
    "leg_rod_top_z", "leg_rod_bottom_z", "battery", "battery_y", "battery_shelf_z", "battery_strap_w", "speaker_d",
    "tray_z_upper", "rod_n", "rod_r", "rod_angle0", "rod_d", "seam_bolt_n", "seam_flange_w",
    "seam_lip_h", "susan_od", "susan_t", "susan_hole_r", "susan_hole_angles", "slip_ring_d",
    "slip_ring_l", "dome_r", "dome_a", "dome_b", "dome_band_h", "dome_plate_t", "dome_eye_lens_d",
    "dome_eye_lcd_pcb", "dome_matrix_pcb", "dome_hp_d", "dome_hp3_r", "head_wheel_r", "tt_thick",
    "wheel_d", "wheel_x", "lg_rod_x", "lg_splice_x", "lg_splice_z", "lg_bearing1_z", "lg_bearing2_z",
    "ft_pivot_z", "ft_lock_r", "ft_stop_r", "ft_pin_d", "ft_pin_h", "ft_stem",
    "hd_hinge_y", "hd_hinge_z", "hd_motor_y", "hd_tension_xy", "hd_stop_xy",
    "st_shaft_d", "st_shaft_t", "st_shaft_x", "st_act_closed", "st_act_case", "st_act_case_t", "st_act_rod_d",
    "st_act_eye_d", "st_act_eye_w", "st_brg", "st_cheek_in", "st_cheek_t", "st_eye_up", "st_flange", "st_hex",
    "st_knob", "st_pin_d", "st_pin_ext", "st_release_pull", "st_horn_arm", "st_horn_rest_gap", "st_horn_tip_r",
    "st_servo_h", "st_servo_l", "st_servo_w", "st_servo_shaft_end", "st_switch_ot", "st_recv",
    "st_release_angle_deg",
]


def release_angle_deg(p):
    """MG995 horn rotation that pulls the lock pin st_release_pull (cad/stance.scad st_release_angle)."""
    arm_x, arm_z = p["st_horn_arm"]
    radius = math.hypot(arm_x, arm_z)
    return math.degrees(math.acos((arm_x - p["st_release_pull"] - p["st_horn_rest_gap"]) / radius)) - \
        math.degrees(math.atan2(arm_z, arm_x))


def bake(mesh, matrix):
    """Transform an STL into the assembly frame and pack interleaved position+normal floats.

    The left-hand Layout matrices have a negative determinant, so the triangle winding is
    reversed and the face normals are recomputed from the corrected winding.
    """
    matrix = np.asarray(matrix, dtype=float)
    vertices = mesh.vertices @ matrix[:3, :3].T + matrix[:3, 3]
    faces = np.asarray(mesh.faces)
    if np.linalg.det(matrix[:3, :3]) < 0:
        faces = faces[:, ::-1]
    triangles = vertices[faces]
    normals = np.cross(triangles[:, 1] - triangles[:, 0], triangles[:, 2] - triangles[:, 0])
    lengths = np.linalg.norm(normals, axis=1)
    lengths[lengths == 0] = 1.0
    normals = normals / lengths[:, None]
    positions = triangles.reshape(-1, 3)
    return np.concatenate([positions, np.repeat(normals, 3, axis=0)], axis=1).astype("<f4")


def pack(array):
    return {"count": int(len(array)), "buffer": base64.b64encode(np.ascontiguousarray(array).tobytes()).decode("ascii")}


def load_story(lay=None):
    """The storyboard validated and resolved against scripts/parts.json and the CAD."""
    lay = lay or Layout(ROOT)
    story = json.loads(STORY_PATH.read_text(encoding="utf-8"))
    validate_story(story)
    return resolve_story(story, story_tokens(package_counts(ROOT), lay))


def export_scene(target, allow_missing):
    import trimesh
    counts = package_counts(ROOT)
    lay = Layout(ROOT)
    story = load_story(lay)
    backfill(lay)
    p = dict(lay.p)
    p.update({k: v for k, v in lay.feet.items() if k.startswith("ft_")})
    p.update({k: v for k, v in lay.head.items() if k.startswith("hd_")})
    p.update({k: v for k, v in lay.legs.items() if k.startswith("lg_")})
    for key, value in scad_numbers(ROOT / "cad/lib.scad",
                                   ["tt_len", "tt_gear_len", "tt_gear_h", "tt_thick", "tt_shaft_d",
                                    "tt_axle_from_front", "tt_can_d", "tt_shaft_l1", "tt_shaft_l2",
                                    "wheel_d", "wheel_w"]).items():
        p.setdefault(key, value)
    for key, value in scad_numbers(ROOT / "cad/head_drive.scad", ["hd_squeeze"]).items():
        p.setdefault(key, value)
    p.setdefault("hd_hinge_z", p["susan_t"] + p["hd_squeeze"] - p["wheel_d"] / 2)
    for required in ("tt_len", "wheel_d", "hd_hinge_z", "hd_motor_y", "hd_hinge_y"):
        if required not in p:
            raise RuntimeError(f"Cannot resolve CAD constant {required}")
    numeric = {k: v for k, v in p.items()
               if isinstance(v, (int, float)) and not isinstance(v, bool)
               or (isinstance(v, list) and all(isinstance(x, (int, float)) for x in v))}
    numeric["ankle_y"] = lay.ankle_y
    numeric["caster_axis_y"] = lay.caster_axis[1]
    numeric["center_foot_top_z"] = lay.center_foot_top_z
    numeric["st_release_angle_deg"] = release_angle_deg(p)

    absent = [k for k in SCENE_KEYS if k not in numeric]
    if absent:
        raise RuntimeError("CAD constants the scene needs are missing and have no fallback: " + ", ".join(absent))

    instances = lay.instances()  # raises unless the placement matches scripts/parts.json quantities
    data = {"meshes": {}, "printed": [], "frames": {}, "params": numeric, "storyboard": story,
            "counts": {"designs": counts["designs"], "instances": counts["pieces"], "mirrored": counts["mirrored"]},
            "revision": REVISION}

    missing = []
    highest = 0.0
    for inst in instances:
        path = ROOT / inst["stl"]
        if not path.is_file():
            missing.append(inst["stl"])
            continue
        mesh = trimesh.load_mesh(path, process=False)
        data["meshes"]["p_" + inst["name"]] = pack(bake(mesh, inst["matrix"]))
        data["printed"].append({"name": inst["name"], "part": inst["part"], "group": inst["group"],
                                "frame": inst["frame"], "mirrored": bool(inst["mirrored"])})
        transformed = mesh.vertices @ np.asarray(inst["matrix"])[:3, :3].T + np.asarray(inst["matrix"])[:3, 3]
        highest = max(highest, float(transformed[:, 2].max()))
    if missing:
        if not allow_missing:
            raise SystemExit("Missing STL files (use --allow-missing while they are generated): " + ", ".join(missing))
        print("!" * 78, flush=True)
        print(f"!! WARNING: {len(missing)} STL file(s) ABSENT - this render is NOT deliverable: {', '.join(missing)}", flush=True)
        print(f"!! Printed pieces shown will be {len(data['printed'])} of {counts['pieces']}.", flush=True)
        print("!" * 78, flush=True)

    for name, mesh in primitives(p).items():
        data["meshes"][name] = pack(bake(mesh, np.eye(4)))

    data["missing_stl"] = missing
    data["overall_height_mm"] = round(highest, 1)

    for name, matrix in [("world", np.eye(4)), ("body", lay.at_body()), ("body_upper", lay.at_body_upper()),
                         ("dome", lay.at_dome(0.0)), ("head_drive", lay.at_head_drive()),
                         ("leg_r", lay.at_leg(1)), ("leg_l", lay.at_leg(-1)),
                         ("foot_r", lay.at_foot(1)), ("foot_l", lay.at_foot(-1)),
                         ("foot_c", lay.at_center_foot(0.0)), ("center_leg", lay.at_center_leg()),
                         ("carriage", lay.at_carriage()),
                         ("caster", T(lay.caster_axis[0], lay.caster_axis[1], p["foot_clear"]))]:
        data["frames"][name] = {"m": cm(matrix), "inv": cm(np.linalg.inv(matrix))}

    ends = lay.endpoints()
    table = lay.pose_table(POSE_STEP_MM)
    data["stance"] = {"parameter": STANCE_PARAMETER, "endpoints": ends, "step": POSE_STEP_MM,
                      "tilt_three_leg": lay.stance.tilt(ends["three_leg"]),
                      "table": [{"s": round(row["s"], 4), "tilt": round(row["tilt"], 4), "lift": round(row["lift"], 3),
                                 "body": cm(row["body"]), "carriage": cm(row["carriage"]),
                                 "housing": cm(row["housing"]), "foot": cm(row["foot"])} for row in table]}
    mech = lay.mechanism()
    data["mech"] = {"shafts": [cm(m) for m in mech["shafts"]], "actuator": cm(mech["actuator"]),
                    "bearings": [cm(m) for m in mech["bearings"]],
                    "locks": [{"side": side, "m": cm(m)} for side, m in sorted(mech["locks"].items())],
                    "receivers": [{"side": r["side"], "angle_deg": r["angle_deg"], "m": cm(r["matrix"])}
                                  for r in mech["receivers"]]}

    data["motors"] = []
    data["wheels"] = []
    for key, foot_matrix, center in [("r", lay.at_foot(1), False), ("l", lay.at_foot(-1), False),
                                     ("c", lay.at_center_foot(0.0), True)]:
        for matrix in lay.motor_matrices(foot_matrix, center=center):
            data["motors"].append({"foot": key, "m": cm(matrix)})
        for index, matrix in enumerate(lay.wheel_matrices(foot_matrix)):
            sign = roll_sign(matrix, p["wheel_d"] / 2)
            data["wheels"].append({"foot": key, "index": index, "spin_sign": sign, "m": cm(matrix)})

    print(f"WHEELS {len(data['wheels'])} placed; roll signs measured from the mesh: "
          f"{sorted({int(w['spin_sign']) for w in data['wheels']})}", flush=True)
    print(f"STANCE {STANCE_PARAMETER} {ends['two_foot']:.2f} / {ends['contact']:.2f} / {ends['three_leg']:.2f} mm, "
          f"{len(table)} poses, three-leg tilt {data['stance']['tilt_three_leg']:.3f} deg", flush=True)

    source_paths = sorted({ROOT / inst["stl"] for inst in instances if (ROOT / inst["stl"]).is_file()})
    source_paths += [ROOT / "cad/params.scad", ROOT / "cad/stance.scad", ROOT / "scripts/parts.json",
                     ROOT / "scripts/assembly_layout.py", ROOT / "scripts/stability.py", SCENE_JS, STORY_PATH]
    hashes = {path.relative_to(ROOT).as_posix(): sha(path) for path in source_paths}
    data["sources"] = hashes

    (target / "scene.json").write_text(json.dumps(data, separators=(",", ":")), encoding="utf-8")
    shutil.copyfile(SCENE_JS, target / "video_scene.js")
    (target / "storyboard-resolved.json").write_text(json.dumps(story, indent=2), encoding="utf-8")
    (target / "index.html").write_text(
        '<!doctype html><html><head><meta charset="utf-8"><style>html,body{margin:0;background:#fff;overflow:hidden}'
        '</style></head><body><canvas id="output"></canvas><script src="video_scene.js"></script></body></html>',
        encoding="utf-8")
    return data, hashes


class RenderHandler(SimpleHTTPRequestHandler):
    def log_message(self, *args):
        pass

    def do_GET(self):
        if self.path not in ("/", "/index.html", "/video_scene.js", "/scene.json"):
            self.send_error(404)
            return
        super().do_GET()


def timestamp(seconds):
    milliseconds = int(round(seconds * 1000))
    hours, milliseconds = divmod(milliseconds, 3600000)
    minutes, milliseconds = divmod(milliseconds, 60000)
    secs, milliseconds = divmod(milliseconds, 1000)
    return f"{hours:02}:{minutes:02}:{secs:02},{milliseconds:03}"


def write_captions(story, height_mm):
    lines = []
    for index, chapter in enumerate(story["chapters"], 1):
        instruction = chapter["instruction"].replace("{HEIGHT}", f"{height_mm:.0f}")
        lines.append(f"{index}\n{timestamp(chapter['start'])} --> {timestamp(chapter['end'])}\n"
                     f"{chapter['title']}\n{instruction}\n")
    (OUT / "assembly-captions.srt").write_text("\n".join(lines), encoding="utf-8")


def check_motion(evidence, scene, story):
    """Assertions on the keyframe evidence: every chapter, the drive demo and both stance changes."""
    names = sorted(entry["name"] for entry in scene["printed"])
    final = evidence[-1]
    assert sorted(final["printed_instances"]) == names, "final frame does not show every printed piece"
    if not scene["missing_stl"]:
        assert len(final["printed_instances"]) == scene["counts"]["instances"], "final piece count wrong"
    assert final["drive"]["action"] == "STOPPED" and abs(final["drive"]["yaw_deg"]) > 1, "robot must end stopped and turned"

    def at(mark):
        return next(e for e in evidence if abs(e["time"] - mark) < 1e-6)
    assert at(video_time(story, 152))["drive"]["action"] == "FORWARD"
    assert at(video_time(story, 158))["drive"]["action"] == "LEFT ARC"
    assert at(video_time(story, 160))["drive"]["action"] == "REVERSE"
    # The castering direction depends on whether the centre foot is ahead of (revision D) or behind
    # the outer-foot axle line; the swivel must also stay inside the CAD stop.
    params = scene["params"]
    ahead = (params["caster_axis_y"] - params["caster_trail"]) - params["ankle_y"]
    caster = at(video_time(story, 158))["drive"]["caster_deg"]
    assert caster * math.copysign(1.0, ahead) > 1, f"centre foot must caster toward the arc: {caster} deg"
    assert abs(caster) <= params["caster_stop_deg"], f"caster {caster} deg is beyond the {params['caster_stop_deg']} deg stop"
    assert at(video_time(story, 158))["stance"]["drive_allowed"] is True, "drive only in the seated three-leg stance"
    assert at(video_time(story, 145))["dome"]["spinning"] is True
    assert at(53.5)["caster_demo"] is True
    chapters_seen = {e["chapter"] for e in evidence}
    assert chapters_seen == {c["name"] for c in story["chapters"]}, f"chapters missing evidence: {chapters_seen}"

    ends, tilt_three = scene["stance"]["endpoints"], scene["stance"]["tilt_three_leg"]
    seen = set()
    for chapter, phase, begin, finish in phase_windows(story):
        inside = [e for e in evidence if begin + 0.2 < e["time"] < finish - 0.2]
        for e in inside:
            st = e["stance"]
            assert st["phase"] == phase, f"{e['time']} s: phase {st['phase']}, storyboard says {phase}"
            assert st["drive_allowed"] is False, f"{e['time']} s: drive allowed during {phase}"
            if phase == "TILT":
                assert set(st["locks"].values()) == {"RELEASED"}, f"{e['time']} s: locks {st['locks']} while tilting"
                assert 0.0 < st["tilt_deg"] < tilt_three, f"{e['time']} s: tilt {st['tilt_deg']} not between stances"
                assert st["centre_foot_lift_mm"] < 0.01, "the centre foot must stay on the floor while tilting"
            if phase in ("LIFT", "LOWER"):
                assert set(st["locks"].values()) == {"SEATED"}, f"{e['time']} s: foot moving without both locks"
                assert abs(st["tilt_deg"]) < 1e-6 and st["centre_foot_lift_mm"] > 0.0
            seen.add((chapter, phase))
    for chapter in story["chapters"]:
        for phase in chapter.get("stance", {}).get("phases", []):
            if phase["phase"] in ("TILT", "LIFT", "LOWER"):
                assert (chapter["name"], phase["phase"]) in seen, f"no keyframe inside {chapter['name']} {phase['phase']}"
    parked = [e for e in evidence if e["chapter"] == "two-foot-stance"]
    assert parked, "no keyframe in the two-foot stance"
    for e in parked:
        st = e["stance"]
        assert st["state"] == "TWO_FOOT" and abs(st["stroke_mm"] - ends["two_foot"]) < 0.01 and abs(st["tilt_deg"]) < 1e-6
        assert set(st["locks"].values()) == {"SEATED"} and st["drive_allowed"] is False
    st = final["stance"]
    assert st["state"] == "THREE_FOOT" and abs(st["stroke_mm"] - ends["three_leg"]) < 0.01
    assert abs(st["tilt_deg"] - tilt_three) < 0.05 and set(st["locks"].values()) == {"SEATED"} and st["drive_allowed"]


def run():
    parser = argparse.ArgumentParser()
    parser.add_argument("--preview", action="store_true", help="render only the storyboard keyframes")
    parser.add_argument("--allow-missing", action="store_true", help="skip STL files that do not exist yet")
    parser.add_argument("--audio", type=Path, help="use an existing soundtrack WAV instead of building one")
    parser.add_argument("--frames", type=int, default=0, help="stop after N frames (timing probe only)")
    parser.add_argument("--check-story", action="store_true", help="validate and resolve the storyboard, then exit")
    args = parser.parse_args()

    if args.check_story:
        story = load_story()
        print(f"PASS storyboard revision {story['revision']}: {len(story['chapters'])} chapters, "
              f"{story['total_seconds']} s, {len(story['keyframes'])} keyframes, {len(phase_windows(story))} stance phases")
        for chapter in story["chapters"]:
            print(f"  {chapter['start']:6.1f}-{chapter['end']:6.1f}  {chapter['title']}  |  {chapter['narration']}")
        return

    from PIL import Image
    from playwright.sync_api import sync_playwright

    for executable in ("ffmpeg", "ffprobe"):
        if not shutil.which(executable):
            raise SystemExit(f"Missing installed tool: {executable}")
    if not CHROME.is_file():
        raise SystemExit("Installed Chrome executable not found.")
    OUT.mkdir(parents=True, exist_ok=True)

    with tempfile.TemporaryDirectory(prefix="r2d2-video-") as temporary:
        directory = Path(temporary).resolve()
        if not directory.is_relative_to(Path(tempfile.gettempdir()).resolve()):
            raise RuntimeError("Unexpected temporary directory")
        scene, inputs = export_scene(directory, args.allow_missing)
        story = scene["storyboard"]
        duration = int(story["total_seconds"])
        fps = int(story["fps"])
        total_frames = duration * fps
        keyframes = list(story["keyframes"])
        height_mm = scene["overall_height_mm"]

        audio = args.audio
        if not args.preview and not args.frames and audio is None:
            audio = directory / "soundtrack.wav"
            print("AUDIO building narration and robot cues", flush=True)
            result = subprocess.run(["powershell", "-NoProfile", "-ExecutionPolicy", "Bypass", "-File",
                                     str(ROOT / "scripts/build_video_audio.ps1"), "-OutputPath", str(audio),
                                     "-StoryboardPath", str(directory / "storyboard-resolved.json")],
                                    capture_output=True, text=True, timeout=300)
            print(result.stdout.strip()[-2000:], flush=True)
            if result.returncode != 0:
                raise RuntimeError("Soundtrack build failed:\n" + result.stderr.strip()[-4000:])

        server = ThreadingHTTPServer(("127.0.0.1", 0), partial(RenderHandler, directory=str(directory)))
        thread = threading.Thread(target=server.serve_forever, daemon=True)
        thread.start()
        encoder = None
        frames = 0
        began = time.monotonic()
        evidence = []
        renderer = "unknown"
        try:
            with sync_playwright() as playwright:
                browser = playwright.chromium.launch(executable_path=str(CHROME), headless=True,
                                                     args=["--use-angle=default", "--enable-unsafe-swiftshader",
                                                           "--disable-lcd-text", "--js-flags=--max-old-space-size=4096"])
                try:
                    page = browser.new_page(viewport={"width": WIDTH, "height": HEIGHT}, device_scale_factor=1)
                    page.set_default_timeout(180000)
                    page.goto(f"http://127.0.0.1:{server.server_port}/", wait_until="load")
                    page.wait_for_function("window.ready===true||Boolean(window.renderError)", timeout=180000)
                    error = page.evaluate("window.renderError||null")
                    if error:
                        raise RuntimeError(error)
                    renderer = page.evaluate(
                        "() => {const c=document.createElement('canvas'),g=c.getContext('webgl2'),"
                        "e=g.getExtension('WEBGL_debug_renderer_info');"
                        "return e?g.getParameter(e.UNMASKED_RENDERER_WEBGL):g.getParameter(g.RENDERER);}")
                    print(f"RENDERER {renderer}; {len(scene['printed'])} printed pieces packed", flush=True)

                    if args.preview or args.frames:
                        review = OUT / "review"
                        review.mkdir(exist_ok=True)
                        times = keyframes if args.preview else [i / fps for i in range(args.frames)]
                        for seconds in times:
                            jpeg = base64.b64decode(page.evaluate("t=>renderFrame(t)", seconds))
                            frames += 1
                            if args.preview:
                                Image.open(io.BytesIO(jpeg)).save(review / f"frame-{seconds:06.1f}.png")
                                evidence.append(page.evaluate("t=>frameEvidence(t)", seconds))
                                print(f"PREVIEW {seconds:.1f}s", flush=True)
                        elapsed = time.monotonic() - began
                        print(f"TIMING {frames} frames in {elapsed:.1f}s = {elapsed / max(frames, 1):.3f} s/frame; "
                              f"projected full render {elapsed / max(frames, 1) * total_frames / 60:.1f} min", flush=True)
                        if args.preview:
                            (review / "motion-checks.json").write_text(json.dumps(evidence, indent=2) + "\n", encoding="utf-8")
                    else:
                        if audio is None or not Path(audio).is_file():
                            raise RuntimeError("Soundtrack missing")
                        log = directory / "ffmpeg.log"
                        review = OUT / "review"
                        review.mkdir(exist_ok=True)
                        with log.open("wb") as errors:
                            command = ["ffmpeg", "-hide_banner", "-loglevel", "error", "-y",
                                       "-f", "image2pipe", "-framerate", str(fps), "-vcodec", "mjpeg", "-i", "pipe:0",
                                       "-i", str(audio), "-map", "0:v:0", "-map", "1:a:0",
                                       "-c:v", "libx264", "-preset", "fast", "-crf", "20", "-pix_fmt", "yuv420p",
                                       "-r", str(fps), "-c:a", "aac", "-b:a", "160k", "-t", str(duration),
                                       "-movflags", "+faststart",
                                       "-metadata", f"title=R2-D2 revision {REVISION} assembly, stance change and simulated operation (CAD animation)",
                                       str(VIDEO)]
                            encoder = subprocess.Popen(command, stdin=subprocess.PIPE, stderr=errors)
                            print(f"RENDER encoder PID {encoder.pid}; {total_frames} frames at {fps} fps", flush=True)
                            key_indices = {int(round(v * fps)): v for v in keyframes}
                            poster_index = int(round(float(story["poster_time"]) * fps))
                            for frame in range(total_frames):
                                if time.monotonic() - began > RENDER_CEILING_SECONDS:
                                    raise TimeoutError("Render exceeded the 29-minute ceiling")
                                if encoder.poll() is not None:
                                    raise RuntimeError("Encoder exited early: " + log.read_text(errors="replace"))
                                seconds = frame / fps
                                jpeg = base64.b64decode(page.evaluate("t=>renderFrame(t)", seconds))
                                encoder.stdin.write(jpeg)
                                frames += 1
                                if frame in key_indices:
                                    evidence.append(page.evaluate("t=>frameEvidence(t)", key_indices[frame]))
                                    Image.open(io.BytesIO(jpeg)).save(review / f"frame-{key_indices[frame]:06.1f}.png")
                                if frame == poster_index:
                                    Image.open(io.BytesIO(jpeg)).save(OUT / "video-poster.png")
                                if frame % (fps * 5) == 0:
                                    print(f"FRAME {frame}/{total_frames} | t {seconds:.1f}s | "
                                          f"elapsed {time.monotonic() - began:.1f}s", flush=True)
                            encoder.stdin.close()
                            if encoder.wait(timeout=300) != 0:
                                raise RuntimeError(log.read_text(errors="replace"))
                            encoder = None
                finally:
                    browser.close()
        finally:
            if encoder is not None and encoder.poll() is None:
                encoder.terminate()
                encoder.wait(timeout=30)
            server.shutdown()
            server.server_close()
            thread.join(timeout=5)

        render_seconds = round(time.monotonic() - began, 2)
        for path, value in inputs.items():
            if sha(ROOT / path) != value:
                raise RuntimeError(f"Input changed while rendering: {path}")
        if args.frames:
            print("TIMING PROBE COMPLETE", flush=True)
            return

        if evidence:
            check_motion(evidence, scene, story)

        if args.preview:
            print(f"PASS preview: {frames} keyframes, {len(scene['printed'])}/{scene['counts']['instances']} pieces, "
                  f"stance changes checked, inputs unchanged", flush=True)
            return

        probe = json.loads(subprocess.check_output(
            ["ffprobe", "-v", "error", "-show_format", "-show_streams", "-of", "json", str(VIDEO)], text=True))
        video_stream = next(s for s in probe["streams"] if s["codec_type"] == "video")
        audio_stream = next(s for s in probe["streams"] if s["codec_type"] == "audio")
        assert (video_stream["width"], video_stream["height"]) == (WIDTH, HEIGHT)
        assert video_stream["codec_name"] == "h264" and audio_stream["codec_name"] == "aac"
        assert int(video_stream["nb_frames"]) == total_frames
        assert video_stream["avg_frame_rate"] == f"{fps}/1"
        probed_duration = float(probe["format"]["duration"])
        assert abs(probed_duration - duration) < 0.1, f"duration {probed_duration}"
        assert 150 <= duration <= 240
        subprocess.run(["ffmpeg", "-v", "error", "-i", str(VIDEO), "-f", "null", "-"], check=True, timeout=600)

        write_captions(story, height_mm)
        cues = [dict(cue) for cue in story["audio_cues"]]
        manifest = {
            "revision": REVISION,
            "type": "CAD animation, simulated operation and simulated stance change, not physical footage",
            "seconds": duration,
            "fps": fps,
            "frames": frames,
            "resolution": [WIDTH, HEIGHT],
            "video_codec": video_stream["codec_name"],
            "audio_codec": audio_stream["codec_name"],
            "printed_designs": scene["counts"]["designs"],
            "printed_instances": scene["counts"]["instances"],
            "overall_height_mm": height_mm,
            "stance_parameter": STANCE_PARAMETER,
            "stance_endpoints_mm": scene["stance"]["endpoints"],
            "stance_phases": [{"chapter": c, "phase": ph, "start_s": a, "end_s": b} for c, ph, a, b in phase_windows(story)],
            "source_sha256": inputs,
            "inputs_unchanged": True,
            "video_sha256": sha(VIDEO),
            "video_bytes": VIDEO.stat().st_size,
            "render_seconds": render_seconds,
            "renderer": renderer,
            "motion_keyframes": evidence,
            "audio_source": {
                "narration": "Windows System.Speech, voice chosen from video_storyboard.json narration_voice_candidates",
                "robot_sounds": sorted({cue["file"] for cue in cues}),
                "sound_directory": story["sound_directory"],
                "cues": cues,
            },
            "wheel_roll_check": (f"{len(scene['wheels'])} wheels; the local spin sign of each was measured from its own "
                                 "mesh so the floor contact point travels backwards for forward travel "
                                 "(mirrored left-hand foot matrices flip both the axis and the handedness)"),
            "mirrored_pieces": sorted(e["name"] for e in scene["printed"] if e["mirrored"]),
            "verification": (f"ffprobe: {WIDTH}x{HEIGHT}, {video_stream['codec_name']}+{audio_stream['codec_name']}, "
                             f"{total_frames} frames, {video_stream['avg_frame_rate']}, {probed_duration:.3f} s; "
                             "full FFmpeg decode passed; every source hash unchanged during the render; "
                             "final frame shows all printed pieces seated in the three-leg stance with both locks "
                             "seated; every stance phase keyframe matched its storyboard phase"),
            "limitations": [
                "Purchased hardware (motors, wheels, battery, boards, bearings, actuator, locks, servos, lazy susan, slip ring) is drawn as a nominal envelope.",
                "Assembly motions, speeds, light patterns and stance-change phase timing are illustrative, not measured.",
                "No physical print, fit, strength, thermal, battery, driving or powered stance-change test is depicted.",
                "Wiring is not routed in the animation; follow electronics/wiring.csv and the manual.",
            ],
        }
        (OUT / "video-manifest.json").write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
        print(f"PASS: revision {REVISION} {duration}s / {frames} frames / {WIDTH}x{HEIGHT} H.264 + AAC; full decode; "
              f"{scene['counts']['instances']} printed pieces from {scene['counts']['designs']} STL files; "
              f"both stance changes checked; render {render_seconds:.1f}s", flush=True)
        print(VIDEO, flush=True)


if __name__ == "__main__":
    run()
