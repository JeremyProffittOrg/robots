"""MATLAB-style engineering drawing set for the fable-r2d2 printed R2-D2 package.

Every surface comes from the exported STL files placed by scripts/assembly_layout.py.
Purchased parts (motors, wheels, battery, lazy susan, slip ring, boards, bolts, rods,
bearings, springs) are nominal envelopes built from the cad/params.scad values.

Writes output/drawings/NN_*.png, output/drawings/components/<part>.png,
output/drawings/drawing-manifest.json and r2d2-matlab-style-drawings.zip.

    python scripts/draw_robot.py [--allow-missing] [--date <iso>] [--only 01,05,components]

--allow-missing skips STL files that are not exported yet and prints a loud warning.
The delivered run must be made without it.
"""
import argparse
import hashlib
import json
import math
import sys
import zipfile
from datetime import datetime, timezone
from pathlib import Path

import matplotlib
import matplotlib.ticker
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.lines import Line2D
from matplotlib.patches import Rectangle, Patch, Circle
from mpl_toolkits.mplot3d import proj3d
from PIL import Image
import numpy as np
import trimesh

sys.path.insert(0, str(Path(__file__).resolve().parent))
from assembly_layout import Layout, T, R, MX, _read_scad_assignments  # noqa: E402

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "output/drawings"
DPI = 170
LAY = Layout(ROOT)
P = LAY.p
LEGS = LAY.legs
FEET = LAY.feet
HEAD = LAY.head
PARTS = json.loads((ROOT / "scripts/parts.json").read_text(encoding="utf-8"))["parts"]
ORDER = ["dome", "body_upper", "body_lower", "leg_upper", "leg_lower",
         "leg_center", "foot_outer", "foot_center", "head_drive"]
TITLES = {"dome": "Dome", "body_upper": "Body upper ring", "body_lower": "Body lower ring",
          "leg_upper": "Outer leg, upper", "leg_lower": "Outer leg, lower",
          "leg_center": "Centre leg", "foot_outer": "Outer foot",
          "foot_center": "Centre foot", "head_drive": "Head friction drive"}

# ---------------------------------------------------------------- palette
BLUE, ORANGE, GOLD, PURPLE, GREEN, CYAN, MAROON = (
    "#0072BD", "#D95319", "#EDB120", "#7E2F8E", "#77AC30", "#4DBEEE", "#A2142F")
INK = "#23384D"
MUTED = "#526779"
PRINTED = "#E1E7EC"          # printed PETG in the finish views
DOME_SILVER = "#C5CDD6"
PART_COLOR = {"dome": BLUE, "body_upper": CYAN, "body_lower": "#2F6E9E",
              "leg_upper": GREEN, "leg_lower": "#4B8B22", "leg_center": "#1AA08F",
              "foot_outer": PURPLE, "foot_center": "#B45CC4", "head_drive": "#D95398"}
MOTOR, WHEEL, BATTERY = GOLD, ORANGE, "#23282E"
STEEL, BEARING, SUSAN = "#93A1AE", "#5F6B77", "#A9B4BF"
BOARD, SLIPRING, SPRING = "#2E7D57", MAROON, "#6E7B8B"
SPEAKER, TFT, LEDC, JEWEL = "#3A3F45", "#1F3B57", "#39B54A", "#2A9BD8"
FOOTER_TEXT = ("STL-derived geometry; purchased parts are nominal envelopes; "
               "no physical build")
LIGHT = np.array([-.35, -.55, 1.0])
LIGHT /= np.linalg.norm(LIGHT)

plt.rcParams.update({"font.family": "Arial", "font.size": 10, "axes.titlesize": 12,
                     "axes.labelsize": 10, "axes.edgecolor": "#63788C", "axes.linewidth": .7,
                     "xtick.color": "#4F5B66", "ytick.color": "#4F5B66",
                     "figure.facecolor": "white", "axes.facecolor": "white",
                     "savefig.facecolor": "white", "figure.dpi": 100,
                     "grid.color": "#CED7E0", "grid.linewidth": .5, "grid.alpha": .8})

ARGS = argparse.Namespace(allow_missing=False, date=None, only="")
MISSING = []
ARTIFACTS = []
_CACHE = {}

# ORTHO view specs: (horizontal axis, vertical axis, depth axis, near sign, horizontal sign)
ORTHO = {"front": (0, 2, 1, 1, -1), "rear": (0, 2, 1, -1, 1),
         "right": (1, 2, 0, 1, 1), "left": (1, 2, 0, -1, -1),
         "top": (0, 1, 2, 1, 1), "bottom": (0, 1, 2, -1, -1)}
ORTHO_TITLE = {"front": "Front / looking toward -Y", "rear": "Rear / looking toward +Y",
               "right": "Right side / looking toward -X", "left": "Left side / looking toward +X",
               "top": "Top / looking toward -Z", "bottom": "Bottom / looking toward +Z"}


def _scad_env(path, base=None):
    """Evaluate the `name = expr;` constants of an OpenSCAD file.

    Layout's own parser drops an assignment whose ';'-chunk starts with a closing brace
    (cad/lib.scad `tt_len`, `wheel_d`) and raises on an expression that runs over two
    lines (cad/legs.scad `lg_center_plane_z`), so the drawing set parses the files here.
    """
    import re
    text = re.sub(r"//[^\n]*", "", Path(path).read_text(encoding="utf-8"))
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
    pattern = re.compile(r"(?:^|[;{}\n])\s*([A-Za-z_$][A-Za-z0-9_]*)\s*=\s*(.+)$", re.S)
    for chunk in text.split(";"):
        match = pattern.search(chunk)
        if not match:
            continue
        name, expression = match.group(1), " ".join(match.group(2).split())
        if name.startswith("$"):
            continue
        try:
            env[name] = eval(expression, {"__builtins__": {}}, {**scope, **env})
        except Exception:
            continue
    return env


for _name, _value in _scad_env(ROOT / "cad/lib.scad").items():
    P.setdefault(_name, _value)
# Re-evaluate the part files with the complete base, then hand them back to the Layout so
# its print_inverse() uses the same constants the sheets do.
LEGS = LAY.legs = _scad_env(ROOT / "cad/legs.scad", base=P)
FEET = LAY.feet = _scad_env(ROOT / "cad/feet.scad", base=P)
HEAD = LAY.head = _scad_env(ROOT / "cad/head_drive.scad", base=P)


def digest(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def have(part):
    return (ROOT / f"stl/{part}.stl").exists()


def stl(part, process=False):
    key = (part, process)
    if key not in _CACHE:
        _CACHE[key] = trimesh.load_mesh(ROOT / f"stl/{part}.stl", process=process)
    return _CACHE[key]


def placed(part, matrix=None, offset=None):
    mesh = stl(part).copy()
    if matrix is not None:
        mesh.apply_transform(matrix)
    if offset is not None:
        mesh.apply_translation(offset)
    return mesh


# ---------------------------------------------------------------- primitives
def _finish(mesh, center, matrix):
    mesh.apply_translation(np.asarray(center, dtype=float))
    if matrix is not None:
        mesh.apply_transform(matrix)
    return mesh


def moved(mesh, offset):
    mesh.apply_translation(np.asarray(offset, dtype=float))
    return mesh


def prim_box(size, center=(0, 0, 0), matrix=None):
    return _finish(trimesh.creation.box(extents=np.asarray(size, dtype=float)), center, matrix)


def prim_cyl(d, h, center=(0, 0, 0), axis="z", matrix=None, sections=40):
    mesh = trimesh.creation.cylinder(radius=d / 2.0, height=h, sections=sections)
    if axis == "x":
        mesh.apply_transform(R(0, 90, 0))
    elif axis == "y":
        mesh.apply_transform(R(-90, 0, 0))
    return _finish(mesh, center, matrix)


def prim_ring(od, idia, h, center=(0, 0, 0), axis="z", matrix=None, sections=72):
    mesh = trimesh.creation.annulus(r_min=idia / 2.0, r_max=od / 2.0, height=h, sections=sections)
    if axis == "x":
        mesh.apply_transform(R(0, 90, 0))
    elif axis == "y":
        mesh.apply_transform(R(-90, 0, 0))
    return _finish(mesh, center, matrix)


def prim_hex(af, h, center=(0, 0, 0), axis="z", matrix=None):
    return prim_cyl(af / math.cos(math.radians(30)), h, center, axis, matrix, sections=6)


def bolt_mesh(dia, length, head_at=(0, 0, 0), axis="z", sign=-1, matrix=None, head="hex"):
    """Head face at head_at; shank runs `length` in sign * axis."""
    head_h = max(0.7 * dia, 2.4)
    pieces = [prim_hex(1.6 * dia, head_h, (0, 0, -sign * head_h / 2.0)) if head == "hex"
              else prim_cyl(1.8 * dia, head_h, (0, 0, -sign * head_h / 2.0)),
              prim_cyl(dia, length, (0, 0, sign * length / 2.0))]
    mesh = trimesh.util.concatenate(pieces)
    if axis == "x":
        mesh.apply_transform(R(0, 90, 0))
    elif axis == "y":
        mesh.apply_transform(R(-90, 0, 0))
    mesh.apply_translation(np.asarray(head_at, dtype=float))
    if matrix is not None:
        mesh.apply_transform(matrix)
    return mesh


def tt_motor_mesh(matrix=None):
    """Adafruit 3777 envelope from cad/lib.scad: shaft along Y, body toward -X."""
    front = P["tt_axle_from_front"]
    gear_len, gear_h, thick = P["tt_gear_len"], P["tt_gear_h"], P["tt_thick"]
    shaft = P["tt_shaft_l1"] + thick + P["tt_shaft_l2"]
    pieces = [prim_box((gear_len, thick, gear_h), (front - gear_len / 2.0, 0, 0)),
              prim_cyl(P["tt_can_d"], P["tt_len"] - gear_len,
                       (front - gear_len - (P["tt_len"] - gear_len) / 2.0, 0, 0), axis="x"),
              prim_cyl(P["tt_shaft_d"], shaft, (0, 0, 0), axis="y"),
              prim_box((6, 8, 6), (front - P["tt_len"] - 1.8, 0, 0))]
    mesh = trimesh.util.concatenate(pieces)
    if matrix is not None:
        mesh.apply_transform(matrix)
    return mesh


def wheel_mesh(matrix=None):
    """Adafruit 3766 envelope: 63 x 29, axis along Z before the layout matrix."""
    return prim_cyl(P["wheel_d"], P["wheel_w"], (0, 0, 0), matrix=matrix, sections=48)


def dome_radius(z):
    if z <= P["dome_band_h"]:
        return P["dome_r"]
    t = (z - P["dome_band_h"]) / P["dome_a"]
    return P["dome_b"] * math.sqrt(max(0.0, 1.0 - t * t))


def dome_point(angle, z, radius=None, out=0.0):
    """Dome feature position. The CAD places features with OpenSCAD rotate([0, 0, angle])
    applied to a feature on +Y, so the angle runs from the front toward the droid's left."""
    r = (dome_radius(z) if radius is None else radius) + out
    a = math.radians(angle)
    return (-r * math.sin(a), r * math.cos(a), z)


def dome_mount(angle, z, size, radius=None, inset=None):
    """Place a board/LED envelope tangentially just inside the dome skin."""
    base = dome_radius(z) if radius is None else radius
    r = base - P["dome_wall"] - size[1] / 2.0 if inset is None else base - inset
    return R(0, 0, angle) @ T(0, r, z)


# ---------------------------------------------------------------- rendering
def view_light(cam, up=(0, 0, 1.0)):
    """A light that always comes over the viewer's shoulder for the given camera."""
    cam = np.asarray(cam, float) / np.linalg.norm(cam)
    up = np.asarray(up, float)
    right = np.cross(up, cam)
    if np.linalg.norm(right) < 1e-6:
        right = np.array([1.0, 0, 0])
    right /= np.linalg.norm(right)
    vertical = np.cross(cam, right)
    light = .78 * cam + .48 * vertical - .34 * right
    return light / np.linalg.norm(light)


def shaded(mesh, color, light=None):
    amount = .55 + .45 * np.maximum(mesh.face_normals @ (LIGHT if light is None else light), 0)
    base = np.asarray(matplotlib.colors.to_rgb(color)) if isinstance(color, str) else np.asarray(color)
    if base.ndim == 1:
        base = base[None, :]
    return np.clip(base * amount[:, None], 0, 1)


def draw_meshes(ax, items, edges=False):
    """Store geometry for the per-pixel depth buffer used at save() time.

    mplot3d's mean-depth painter ordering cannot resolve the long thin triangles of
    hollow printed shells, so the triangles are rasterised into the axes bounding box
    with a real z-buffer instead of plot_trisurf.
    """
    ax._drawing_items = [it for it in items if it is not None and len(it[0].faces)]
    ax._drawing_edges = edges


def rasterize(ax, dpi):
    items = ax._drawing_items
    if not items:
        return None
    light = getattr(ax, "_light", None)
    triangles = np.concatenate([mesh.triangles for mesh, _, _ in items])
    facecolors = np.concatenate([shaded(mesh, color, light) for mesh, color, _ in items])
    ratio = dpi / ax.figure.dpi
    width = max(1, int(np.ceil(ax.bbox.width * ratio)))
    height = max(1, int(np.ceil(ax.bbox.height * ratio)))
    depth_buffer = np.full((height, width), -np.inf, dtype=np.float32)
    rgba = np.zeros((height, width, 4), dtype=np.uint8)

    def project(points):
        shape = points.shape
        flat = points.reshape(-1, 3)
        if hasattr(ax, "_ortho_spec"):
            horizontal, vertical, depth, near_sign, xsign = ax._ortho_spec
            xy = flat[:, [horizontal, vertical]].copy()
            xy[:, 0] *= xsign
            values = flat[:, depth] * near_sign
        else:
            projected = np.c_[flat, np.ones(len(flat))] @ ax.get_proj().T
            xy = projected[:, :2] / projected[:, 3, None]
            azimuth, elevation = np.deg2rad([ax.azim, ax.elev])
            camera = np.array([np.cos(elevation) * np.cos(azimuth),
                               np.cos(elevation) * np.sin(azimuth), np.sin(elevation)])
            values = flat @ camera
        pixels = (ax.transData.transform(xy) - ax.bbox.p0) * ratio
        return pixels.reshape(*shape[:-1], 2), values.reshape(shape[:-1])

    pixels, values = project(triangles)
    for triangle, z, color in zip(pixels, values, facecolors):
        x0 = max(0, int(np.floor(triangle[:, 0].min())))
        x1 = min(width - 1, int(np.ceil(triangle[:, 0].max())))
        y0 = max(0, int(np.floor(triangle[:, 1].min())))
        y1 = min(height - 1, int(np.ceil(triangle[:, 1].max())))
        if x1 < x0 or y1 < y0:
            continue
        (ax0, ay0), (bx, by), (cx, cy) = triangle
        denominator = (by - cy) * (ax0 - cx) + (cx - bx) * (ay0 - cy)
        if abs(denominator) < 1e-9:
            continue
        xx = np.arange(x0, x1 + 1)[None, :] + .5
        yy = np.arange(y0, y1 + 1)[:, None] + .5
        first = ((by - cy) * (xx - cx) + (cx - bx) * (yy - cy)) / denominator
        second = ((cy - ay0) * (xx - cx) + (ax0 - cx) * (yy - cy)) / denominator
        third = 1 - first - second
        incoming = first * z[0] + second * z[1] + third * z[2]
        region = depth_buffer[y0:y1 + 1, x0:x1 + 1]
        mask = (first >= -1e-7) & (second >= -1e-7) & (third >= -1e-7) & (incoming > region)
        if not mask.any():
            continue
        region[mask] = incoming[mask]
        rgba[y0:y1 + 1, x0:x1 + 1][mask] = np.r_[np.rint(color * 255).astype(np.uint8), 255]
    if ax._drawing_edges:
        for mesh, _, _ in items:
            try:
                hard = mesh.face_adjacency_angles > np.deg2rad(34)
                segments = mesh.vertices[mesh.face_adjacency_edges[hard]]
            except Exception:
                continue
            if not len(segments):
                continue
            endpoints, distances = project(segments)
            for segment, z in zip(endpoints, distances):
                count = max(2, int(np.linalg.norm(segment[1] - segment[0]) * 1.3))
                fraction = np.linspace(0, 1, count)
                points = np.rint(segment[0] + fraction[:, None] * (segment[1] - segment[0])).astype(int)
                depths = z[0] + fraction * (z[1] - z[0])
                valid = ((points[:, 0] >= 0) & (points[:, 0] < width)
                         & (points[:, 1] >= 0) & (points[:, 1] < height))
                points, depths = points[valid], depths[valid]
                x, y = points[:, 0], points[:, 1]
                visible = (rgba[y, x, 3] > 0) & (depths >= depth_buffer[y, x] - .2)
                x, y = x[visible], y[visible]
                rgba[y, x, :3] = (rgba[y, x, :3] * .62).astype(np.uint8)
    return rgba


def camera_vector(elev, azim):
    e, a = np.deg2rad([elev, azim])
    return np.array([np.cos(e) * np.cos(a), np.cos(e) * np.sin(a), np.sin(e)])


def surface_anchor(mesh, elev=22, azim=-58):
    """A point on the camera-facing surface, near the middle of the part's silhouette."""
    cam = camera_vector(elev, azim)
    centers = mesh.triangles_center
    facing = (mesh.face_normals @ cam) > .05
    if not facing.any():
        facing = np.ones(len(centers), dtype=bool)
    relative = centers - mesh.centroid
    perpendicular = relative - np.outer(relative @ cam, cam)
    distance = np.linalg.norm(perpendicular, axis=1)
    distance[~facing] = np.inf
    return centers[int(np.argmin(distance))]


def anchor_of(items, label, elev=22, azim=-58):
    for mesh, _, name in items:
        if name == label:
            return surface_anchor(mesh, elev, azim)
    return None


def items_bounds(items, pad=.06):
    stack = np.array([mesh.bounds for mesh, _, _ in items])
    lower, upper = stack[:, 0].min(axis=0), stack[:, 1].max(axis=0)
    span = np.maximum(upper - lower, 6.0)
    return lower - span * pad, upper + span * pad


def setup_3d(ax, bounds, elev=22, azim=-58, tick_step=None, labels=True, zoom=1.0):
    lower, upper = np.asarray(bounds[0], float), np.asarray(bounds[1], float)
    span = np.maximum(upper - lower, 1e-6)
    ax.set_xlim(lower[0], upper[0])
    ax.set_ylim(lower[1], upper[1])
    ax.set_zlim(lower[2], upper[2])
    ax.set_box_aspect(span, zoom=zoom)
    ax.set_proj_type("ortho")
    ax.view_init(elev=elev, azim=azim)
    ax._light = view_light(camera_vector(elev, azim))
    for axis in (ax.xaxis, ax.yaxis, ax.zaxis):
        axis.set_pane_color((.966, .974, .981, .6))
        axis._axinfo["grid"].update(color=(.79, .82, .86, .65), linewidth=.45)
    if labels:
        ax.set_xlabel("X (mm)", labelpad=8)
        ax.set_ylabel("Y (mm)", labelpad=8)
        ax.set_zlabel("Z (mm)", labelpad=10)
    ax.tick_params(labelsize=8, pad=1)
    if tick_step:
        for setter, lo, hi in zip([ax.set_xticks, ax.set_yticks, ax.set_zticks], lower, upper):
            setter(np.arange(math.ceil(lo / tick_step) * tick_step, hi + 1, tick_step))
    else:
        for axis in (ax.xaxis, ax.yaxis, ax.zaxis):
            axis.set_major_locator(matplotlib.ticker.MaxNLocator(nbins=4))


def setup_ortho(ax, view, xlim, ylim, caption=None):
    spec = ORTHO[view]
    ax._ortho_spec = spec
    xsign = spec[4]
    camera = np.zeros(3)
    camera[spec[2]] = spec[3]
    vertical = np.zeros(3)
    vertical[spec[1]] = 1.0
    ax._light = view_light(camera, up=vertical)
    lo, hi = sorted((xlim[0] * xsign, xlim[1] * xsign))
    ax.set_xlim(lo, hi)
    ax.set_ylim(ylim[0], ylim[1])
    ax.set_aspect("equal")
    ax.set_axisbelow(True)
    ax.grid(True)
    ax.set_xlabel(("-" if xsign < 0 else "") + "XYZ"[spec[0]] + " (mm)")
    ax.set_ylabel("XYZ"[spec[1]] + " (mm)")
    ax.set_title(caption if caption else ORTHO_TITLE[view], pad=7)


def project_figure(fig, ax, point):
    if hasattr(ax, "_ortho_spec"):
        horizontal, vertical, _, _, xsign = ax._ortho_spec
        flat = (point[horizontal] * xsign, point[vertical])
    else:
        flat = proj3d.proj_transform(*point, ax.get_proj())[:2]
    return fig.transFigure.inverted().transform(ax.transData.transform(flat))


def callout(fig, ax, point, text, label_position, color="#2C4457", fontsize=9.5, exit_right=None):
    start = project_figure(fig, ax, point)
    x, y = label_position
    width = max(len(line) for line in text.split("\n")) * .0092 * fontsize / fig.get_figwidth()
    if exit_right is None:
        exit_right = x <= .5
    finish_x = x + width if exit_right else x - .006
    lines = text.count("\n") + 1
    fig.add_artist(Line2D([start[0], finish_x], [start[1], y + (.004 if lines == 1 else .006)],
                          transform=fig.transFigure, color=color, linewidth=.8, zorder=5))
    fig.add_artist(Line2D([start[0]], [start[1]], transform=fig.transFigure, marker="o",
                          markersize=2.6, color=color, zorder=5))
    fig.text(x, y, text, fontsize=fontsize, color=color, ha="left", va="center", zorder=6,
             bbox={"facecolor": "white", "edgecolor": "none", "pad": 1.6, "alpha": .86})


def callouts(fig, ax, entries, left_x=.035, right_x=.775, top=.84, bottom=.20, fontsize=9.5,
             auto=False):
    """Place labelled leader lines down both margins without overlapping."""
    fig.canvas.draw()
    if auto:
        entries = [(point, text, "L" if project_figure(fig, ax, point)[0] < .5 else "R")
                   for point, text, _ in entries]
    for side, x in (("L", left_x), ("R", right_x)):
        rows = [e for e in entries if e[2] == side]
        if not rows:
            continue
        rows.sort(key=lambda e: -project_figure(fig, ax, e[0])[1])
        step = (top - bottom) / max(len(rows) - 1, 1)
        for index, (point, text, _) in enumerate(rows):
            y = top - index * step if len(rows) > 1 else (top + bottom) / 2
            callout(fig, ax, point, text, (x, y), fontsize=fontsize)


def side_callouts(fig, ax, entries, x, top, bottom, fontsize=8.2, exit_right=True):
    """Every label in one vertical column beside a panel, ordered so leaders never cross."""
    fig.canvas.draw()
    rows = sorted(entries, key=lambda e: -project_figure(fig, ax, e[0])[1])
    step = (top - bottom) / max(len(rows) - 1, 1)
    for index, (point, text) in enumerate(rows):
        y = top - index * step if len(rows) > 1 else (top + bottom) / 2
        callout(fig, ax, point, text, (x, y), fontsize=fontsize, exit_right=exit_right)


def dimension(ax, p1, p2, label, rotation=0, offset=(0, 0), fontsize=9):
    ax.annotate("", xy=p1, xytext=p2, annotation_clip=False,
                arrowprops={"arrowstyle": "<->", "color": "#1F3D52", "lw": .9})
    middle = (np.asarray(p1, float) + np.asarray(p2, float)) / 2 + np.asarray(offset, float)
    ax.text(*middle, label, ha="center", va="center", rotation=rotation, fontsize=fontsize,
            color="#1F3D52", bbox={"facecolor": "white", "edgecolor": "none", "pad": 1.5})


def balloon(fig, ax, point, number, position, color=INK):
    start = project_figure(fig, ax, point)
    x, y = position
    fig.add_artist(Line2D([start[0], x], [start[1], y], transform=fig.transFigure,
                          color=color, linewidth=.8, zorder=5))
    fig.add_artist(Line2D([start[0]], [start[1]], transform=fig.transFigure, marker="o",
                          markersize=2.6, color=color, zorder=5))
    radius = .0125
    fig.add_artist(Circle((x, y), radius, transform=fig.transFigure, facecolor="white",
                          edgecolor=color, linewidth=1.0, zorder=6))
    fig.text(x, y, str(number), fontsize=10, color=color, ha="center", va="center", zorder=7)


def heading(fig, title_text, subtitle):
    fig.text(.035, .955, title_text, fontsize=19, color="#1B2733", ha="left", va="center")
    fig.text(.035, .923, subtitle, fontsize=10.5, color=MUTED, ha="left", va="center")


def clip(text, limit):
    return text if len(text) <= limit else text[:limit - 1] + "…"


def title_block(fig, number, name, parts, sizes, scale, note=None):
    x0, y0, w, h = .600, .032, .378, .098
    fig.add_artist(Rectangle((x0, y0), w, h, transform=fig.transFigure, facecolor="white",
                             edgecolor="#63788C", linewidth=1.0, zorder=5))
    fig.add_artist(Line2D([x0, x0 + w], [y0 + h * .655] * 2, transform=fig.transFigure,
                          color="#63788C", linewidth=.7, zorder=6))
    limit = int(fig.get_figwidth() * 11.5)
    fig.text(x0 + .008, y0 + h * .82, "fable-r2d2  /  printable R2-D2  /  MATLAB-style drawing set",
             fontsize=8.4, color="#1B2733", va="center", zorder=6)
    fig.text(x0 + w - .008, y0 + h * .82, f"SHEET {number}", fontsize=9, color="#1B2733",
             ha="right", va="center", zorder=6)
    fig.text(x0 + .008, y0 + h * .50, clip(f"{name}", limit), fontsize=8.6, color=INK,
             va="center", zorder=6)
    fig.text(x0 + .008, y0 + h * .30, clip("Parts: " + parts, limit), fontsize=7.6,
             color=MUTED, va="center", zorder=6)
    fig.text(x0 + .008, y0 + h * .11, clip(f"{sizes}  |  {scale}", limit), fontsize=7.6,
             color=MUTED, va="center", zorder=6)
    if note:
        fig.text(x0 - .012, y0 + h * .5, note, fontsize=8, color=MUTED, ha="right", va="center")


def footer(fig, extra=None):
    fig.text(.035, .072, FOOTER_TEXT, fontsize=9.2, color=MUTED)
    if extra:
        fig.text(.035, .046, extra, fontsize=8.6, color=MUTED)
    if MISSING:
        fig.text(.035, .020, "DEVELOPMENT RUN - missing STL: " + ", ".join(MISSING),
                 fontsize=9, color="#B3261E")


def frame(fig):
    fig.add_artist(Rectangle((.018, .015), .964, .968, transform=fig.transFigure, fill=False,
                             edgecolor="#8FA0B0", linewidth=1.0, zorder=4))


def legend(fig, entries, position=(.795, .50), fontsize=9.5, title_text="Legend", ncol=1,
           loc="center left"):
    handles = [Patch(facecolor=color, edgecolor="#8593A2", label=label) for label, color in entries]
    leg = fig.legend(handles=handles, loc=loc, bbox_to_anchor=position,
                     frameon=True, fontsize=fontsize, title=title_text, borderpad=.8,
                     labelspacing=.75, handlelength=1.6, ncol=ncol, columnspacing=1.6)
    leg.get_frame().set_edgecolor("#8FA0B0")
    leg.get_frame().set_linewidth(.8)
    leg.get_title().set_fontsize(fontsize + .5)
    leg.get_title().set_color(INK)
    return leg


def missing_banner(ax, names):
    ax.set_axis_off()
    writer = ax.text2D if hasattr(ax, "text2D") else ax.text
    writer(.5, .5, "STL not exported yet:\n" + "\n".join(names), transform=ax.transAxes,
           ha="center", va="center", fontsize=13, color="#B3261E",
           bbox={"facecolor": "#FDECEA", "edgecolor": "#B3261E", "pad": 10})


def save(fig, relative):
    path = OUT / relative
    path.parent.mkdir(parents=True, exist_ok=True)
    fig.canvas.draw()
    for ax in list(fig.axes):
        if not hasattr(ax, "_drawing_items"):
            continue
        rgba = rasterize(ax, DPI)
        if rgba is None:
            continue
        overlay = fig.add_axes(ax.get_position(), zorder=1, frameon=False)
        overlay.imshow(rgba, extent=(0, 1, 0, 1), origin="lower", interpolation="nearest",
                       aspect="auto")
        overlay.set_xlim(0, 1)
        overlay.set_ylim(0, 1)
        overlay.set_axis_off()
    fig.savefig(path, dpi=DPI)
    plt.close(fig)
    with Image.open(path) as check:
        assert check.format == "PNG" and check.width >= 1800, (path, check.size)
        size = check.size
    ARTIFACTS.append(path)
    print(f"PNG {path.relative_to(ROOT)}  {size[0]}x{size[1]}", flush=True)


# ---------------------------------------------------------------- assembly scenes
def printed_items(finish=True, explode=None):
    items = []
    for inst in LAY.instances():
        if not have(inst["part"]):
            continue
        offset = (explode or {}).get(inst["name"], (0, 0, 0))
        mesh = placed(inst["part"], inst["matrix"], offset)
        if finish:
            color = DOME_SILVER if inst["part"] == "dome" else PRINTED
        else:
            color = PART_COLOR[inst["part"]]
        items.append((mesh, color, inst["name"]))
    return items


def drive_items(explode=None):
    """Motors and wheels in all three feet, from the Layout helpers."""
    items = []
    shift = explode or {}
    feet = [(LAY.at_foot(1), shift.get("foot_outer_right", (0, 0, 0)), False),
            (LAY.at_foot(-1), shift.get("foot_outer_left", (0, 0, 0)), False),
            (LAY.at_center_foot(), shift.get("foot_center", (0, 0, 0)), True)]
    for matrix, offset, center in feet:
        for m in LAY.motor_matrices(matrix, center=center):
            items.append((moved(tt_motor_mesh(m), offset), MOTOR, "TT motor"))
        for m in LAY.wheel_matrices(matrix):
            items.append((moved(wheel_mesh(m), offset), WHEEL, "Wheel"))
    return items


def body_hardware(explode=None):
    """Purchased envelopes carried by the body, in the assembly frame."""
    shift = explode or {}
    body = LAY.at_body()
    lower = np.asarray(shift.get("body_lower", (0, 0, 0)), float)
    upper = np.asarray(shift.get("body_upper", (0, 0, 0)), float)
    items = []
    bx, by, bz = P["battery"]
    items.append((moved(prim_box((bx, by, bz), (0, P["battery_y"], P["battery_shelf_z"] + bz / 2),
                                 body), lower), BATTERY, "Battery 12 V 7 Ah"))
    for y in (P["battery_y"] - 45, P["battery_y"] + 45):
        items.append((moved(prim_box((bx + 8, P["battery_strap_w"], 3),
                                     (0, y, P["battery_shelf_z"] + bz + 1.5), body), lower),
                      STEEL, "Battery strap"))
    items.append((moved(prim_cyl(P["speaker_d"], P["speaker_depth"], (0, 122, 108), axis="y",
                                 matrix=body), lower), SPEAKER, "Speaker envelope"))
    deck = P["body_lower_h"] + P["tray_z_upper"]
    px, py, pz = P["pi4"]
    items.append((moved(prim_box((px, py, pz), (0, -38, deck + pz / 2), body), upper),
                  BOARD, "Raspberry Pi 4"))
    items.append((moved(prim_box(P["kb2040"], (66, 8, deck + P["kb2040"][2] / 2), body), upper),
                  BOARD, "KB2040"))
    for x, y in [(-70, 20), (-70, -14), (-70, -48), (66, -30)]:
        items.append((moved(prim_box(P["drv8833"], (x, y, deck + P["drv8833"][2] / 2), body),
                            upper), BOARD, "DRV8833"))
    items.append((moved(prim_box(P["regulator"], (66, 44, deck + P["regulator"][2] / 2), body),
                        upper), BOARD, "Buck regulator"))
    for index in range(int(P["rod_n"])):
        angle = math.radians(P["rod_angle0"] + index * 360.0 / P["rod_n"])
        length = P["body_top_plate_z"] - P["floor_t"]
        items.append((moved(prim_cyl(P["rod_d"], length,
                                     (P["rod_r"] * math.cos(angle), P["rod_r"] * math.sin(angle),
                                      P["floor_t"] + length / 2), matrix=body), upper),
                      STEEL, "M8 rod"))
    items.append((moved(prim_ring(P["susan_od"], P["susan_id"], P["susan_t"],
                                  (0, 0, P["body_top_plate_z"] + P["susan_t"] / 2), matrix=body),
                        upper), SUSAN, "Lazy susan"))
    items.append((moved(prim_cyl(P["slip_ring_d"], P["slip_ring_l"],
                                 (0, 0, P["body_top_plate_z"] + P["slip_ring_post_h"]
                                  - P["slip_ring_l"] / 2), matrix=body), upper),
                  SLIPRING, "Slip ring"))
    return items


def head_drive_items(frame_matrix, explode=(0, 0, 0)):
    """Head friction drive motor and wheel, head-drive native frame times frame_matrix."""
    motor_y = HEAD["hd_motor_y"] + HEAD["hd_hinge_y"]
    axle_z = HEAD["hd_hinge_z"]
    return [(moved(tt_motor_mesh(frame_matrix @ T(0, motor_y, axle_z)), explode),
             MOTOR, "TT motor 3777"),
            (moved(prim_cyl(P["wheel_d"], P["wheel_w"], (0, -P["head_wheel_r"], axle_z), axis="y",
                            matrix=frame_matrix), explode), WHEEL, "Friction wheel 3766")]


# ---------------------------------------------------------------- sheets
def sheet_01():
    items = printed_items(finish=True) + drive_items() + body_hardware()
    hd = LAY.at_head_drive()
    items += head_drive_items(hd)
    fig = plt.figure(figsize=(16, 13))
    ax = fig.add_axes([.11, .13, .60, .75], projection="3d")
    draw_meshes(ax, items)
    lo, hi = items_bounds(items, pad=0)
    setup_3d(ax, ([-265, lo[1] - 15, 0], [265, hi[1] + 15, hi[2] + 15]), elev=20, azim=-60,
             tick_step=100, zoom=1.12)
    heading(fig, "fable-r2d2 / assembled robot, three-leg stance",
            f"Nine printed designs / twelve printed pieces | Overall height "
            f"{hi[2]:.1f} mm | Body diameter {P['body_od']:.0f} mm | Foot track "
            f"{P['leg_track']:.1f} mm")
    def point(label):
        return anchor_of(items, label, 20, -60)
    entries = [(point("dome"), "Dome, one piece\nPETG, 199.1 mm tall", "L"),
               (point("body_upper"), "Body upper ring\nintegral electronics deck", "R"),
               (point("body_lower"), "Body lower ring\nbattery bay and skirt", "R"),
               (point("leg_upper_right"), "Outer leg upper\nshoulder pivot M12", "L"),
               (point("leg_lower_right"), "Outer leg lower\nspliced on two M8 rods", "L"),
               (point("foot_outer_right"), "Outer foot\ntwo motors, four wheels", "R"),
               (point("leg_center"), "Centre leg on caster\nbearings, behind the skirt", "L"),
               (point("foot_center"), "Centre foot\ntwo motors, four wheels", "R"),
               (point("head_drive"), "Head friction drive\nunder the top plate", "R")]
    callouts(fig, ax, [e for e in entries if e[0] is not None],
             left_x=.030, right_x=.745, top=.860, bottom=.30, auto=True)
    legend(fig, [("Printed PETG parts", PRINTED), ("Dome (printed, silver finish)", DOME_SILVER),
                 ("Wheels, Adafruit 3766", WHEEL), ("TT motors, Adafruit 3777", MOTOR),
                 ("Battery 12 V 7 Ah SLA", BATTERY), ("Steel rods, straps, bolts", STEEL),
                 ("Lazy susan ring bearing", SUSAN), ("Electronics boards", BOARD)],
           position=(.050, .095), ncol=2, loc="lower left", fontsize=9)
    footer(fig, "Seven TT motors and thirteen wheels: two motors and four wheels per foot, plus the head friction drive.")
    title_block(fig, "01", "Assembled robot / isometric",
                "dome, body_upper, body_lower, leg_upper x2, leg_lower x2, leg_center, "
                "foot_outer x2, foot_center, head_drive",
                f"Height {hi[2]:.1f} mm, track {P['leg_track']:.1f} mm",
                "Scale: fit to sheet, axes in mm")
    frame(fig)
    save(fig, "01_robot_assembled.png")


EXPLODE = {"dome": (0, 0, 300), "body_upper": (0, 0, 170), "body_lower": (0, 0, 45),
           "head_drive": (0, -310, 150),
           "leg_upper_right": (250, 0, 60), "leg_upper_left": (-250, 0, 60),
           "leg_lower_right": (310, 60, -50), "leg_lower_left": (-310, 60, -50),
           "foot_outer_right": (350, 130, 0), "foot_outer_left": (-350, 130, 0),
           "leg_center": (0, 250, 90), "foot_center": (0, 320, 0)}


def sheet_02():
    items = printed_items(finish=False, explode=EXPLODE) + drive_items(EXPLODE) \
        + body_hardware(EXPLODE)
    items += head_drive_items(LAY.at_head_drive(), EXPLODE["head_drive"])
    fig = plt.figure(figsize=(17, 13))
    ax = fig.add_axes([.10, .22, .62, .68], projection="3d")
    draw_meshes(ax, items)
    lo, hi = items_bounds(items, pad=.03)
    setup_3d(ax, ([lo[0], lo[1], 0], [hi[0], hi[1], hi[2]]), elev=18, azim=-60, tick_step=200,
             zoom=1.05)
    heading(fig, "fable-r2d2 / exploded assembly",
            "Separated along the axis each joint is assembled on | Vertical stack for the body "
            "and dome, outboard for the legs and feet, rearward for the head drive")
    def point(label):
        return anchor_of(items, label, 18, -60)
    entries = [(point("dome"), "Dome\nlazy susan and slip ring below", "L"),
               (point("body_upper"), "Body upper ring\ndeck, shoulder bosses, top plate", "R"),
               (point("body_lower"), "Body lower ring\nbattery bay and skirt", "R"),
               (point("head_drive"), "Head friction drive\nmount, motor and wheel", "R"),
               (point("leg_upper_right"), "Outer leg upper x2\nmirror for the second", "L"),
               (point("leg_lower_right"), "Outer leg lower x2\nM8 rods through both", "L"),
               (point("foot_outer_right"), "Outer foot x2\nmirror for the second", "R"),
               (point("leg_center"), "Centre leg\n6001 bearings, M12 caster bolt", "L"),
               (point("foot_center"), "Centre foot\ncaster stem into the leg", "R")]
    callouts(fig, ax, [e for e in entries if e[0] is not None],
             left_x=.028, right_x=.735, top=.86, bottom=.30, auto=True)
    legend(fig, [(TITLES[name], PART_COLOR[name]) for name in ORDER]
           + [("TT motors", MOTOR), ("Wheels", WHEEL), ("Battery", BATTERY),
              ("Steel hardware", STEEL)], position=(.33, .105), title_text="Printed parts",
           ncol=5, loc="lower center", fontsize=9)
    footer(fig, "Explosion offsets are for clarity only; assembled positions are on sheet 01.")
    title_block(fig, "02", "Exploded assembly / isometric",
                "all nine printed designs plus purchased envelopes",
                "Explosion 45-350 mm along the joint axes",
                "Scale: fit to sheet, axes in mm")
    frame(fig)
    save(fig, "02_robot_exploded.png")


def sheet_03():
    items = printed_items(finish=True) + drive_items() + body_hardware()
    items += head_drive_items(LAY.at_head_drive())
    lo, hi = items_bounds(items, pad=0)
    height = hi[2]
    width = hi[0] - lo[0]
    depth = hi[1] - lo[1]
    span = 820.0
    fig = plt.figure(figsize=(19, 10.5))
    axes = []
    rects = [[.045, .27, .28, .60], [.365, .27, .28, .60], [.685, .27, .28, .60]]
    views = ["front", "right", "top"]
    for rect, view in zip(rects, views):
        ax = fig.add_axes(rect)
        draw_meshes(ax, items)
        axes.append(ax)
        if view == "top":
            cx, cy = (lo[0] + hi[0]) / 2, (lo[1] + hi[1]) / 2
            setup_ortho(ax, view, (cx - span / 2, cx + span / 2), (cy - span / 2, cy + span / 2),
                        "Top / looking toward -Z")
        elif view == "front":
            cx = (lo[0] + hi[0]) / 2
            setup_ortho(ax, view, (cx - span / 2, cx + span / 2), (-60, span - 60),
                        "Front / looking toward -Y (droid faces +Y)")
        else:
            cy = (lo[1] + hi[1]) / 2
            setup_ortho(ax, view, (cy - span / 2, cy + span / 2), (-60, span - 60),
                        "Right side / looking toward -X")
    front, side, top = axes
    dimension(front, (-(lo[0] - 55), 0), (-(lo[0] - 55), height),
              f"Overall height {height:.1f} mm", rotation=90)
    dimension(front, (-lo[0], height + 18), (-hi[0], height + 18),
              f"Overall width {width:.1f} mm")
    dimension(front, (P["leg_offset_x"], -35), (-P["leg_offset_x"], -35),
              f"Track {P['leg_track']:.1f} mm")
    dimension(side, (lo[1], -35), (hi[1], -35), f"Overall depth {depth:.1f} mm")
    dimension(side, (hi[1] + 55, 0), (hi[1] + 55, P["shoulder_z_three_leg"]),
              f"Shoulder axis {P['shoulder_z_three_leg']:.1f} mm", rotation=90)
    dimension(top, (-P["body_r"], hi[1] + 30), (P["body_r"], hi[1] + 30),
              f"Body dia {P['body_od']:.1f} mm")
    dimension(top, (hi[0] + 45, -P["leg_offset_x"] * 0 + lo[1]), (hi[0] + 45, hi[1]),
              f"Footprint depth {depth:.1f} mm", rotation=90)
    heading(fig, "fable-r2d2 / orthographic drawings",
            "Three principal views of the same STL assembly | All three panels share one scale "
            f"({span:.0f} mm across each panel) | Dimensions read from the assembly bounds")
    footer(fig, "Datum: floor Z = 0, body axis X = Y = 0, +Y is the front of the droid.")
    title_block(fig, "03", "Orthographic views / front, right side, top",
                "complete assembly, printed parts and purchased envelopes",
                f"H {height:.1f} x W {width:.1f} x D {depth:.1f} mm",
                f"Scale: equal on all panels, {span:.0f} mm field")
    frame(fig)
    save(fig, "03_robot_orthographic.png")


def sheet_04():
    fig = plt.figure(figsize=(19, 13))
    for index, name in enumerate(ORDER):
        ax = fig.add_subplot(3, 3, index + 1, projection="3d")
        row = PARTS[name]
        if not have(name):
            ax.set_axis_off()
            ax.text2D(.5, .5, f"{name}.stl\nnot exported yet", transform=ax.transAxes,
                      ha="center", va="center", fontsize=12, color="#B3261E")
            continue
        mesh = stl(name, process=True)
        draw_meshes(ax, [(mesh, PART_COLOR[name], name)], edges=True)
        pad = np.maximum(mesh.extents * .10, 2)
        setup_3d(ax, [mesh.bounds[0] - pad, mesh.bounds[1] + pad], elev=26, azim=-56,
                 labels=False, zoom=1.45)
        ax.set_axis_off()
        extents = mesh.extents
        mirror = "  |  mirror in the slicer for the second" if row["mirror"] else ""
        ax.set_title(f"{index + 1:02d}  {TITLES[name]}  /  {name}.stl\n"
                     f"Qty {row['quantity']}  |  {row['material']}{mirror}",
                     fontsize=10.5, pad=1, color=INK)
        ax.text2D(.5, -.035, f"{extents[0]:.1f} x {extents[1]:.1f} x {extents[2]:.1f} mm  |  "
                             f"{row['orientation']}", transform=ax.transAxes, ha="center",
                  fontsize=8.8, color=MUTED)
    fig.subplots_adjust(left=.02, right=.98, bottom=.19, top=.87, wspace=.04, hspace=.26)
    heading(fig, "fable-r2d2 / printed components",
            "Nine STL designs, twelve printed pieces | Each part shown in its print orientation "
            "on the plate (Z up) | Each panel has its own scale")
    footer(fig, "Bounding boxes are the exported STL extents. H2D left-extruder field "
                f"{P['env_x']:.0f} x {P['env_y']:.0f} x {P['env_z']:.0f} mm.")
    title_block(fig, "04", "Printed components / print orientation",
                ", ".join(ORDER), "Sizes are STL bounding boxes in mm",
                "Scale: per panel, axes omitted")
    frame(fig)
    save(fig, "04_printed_components.png")


def _section(mesh, keep_positive_x=True):
    try:
        cut = mesh.slice_plane([0, 0, 0], [1, 0, 0] if keep_positive_x else [-1, 0, 0])
    except Exception:
        return None
    return cut if cut is not None and len(cut.faces) else None


PANEL_W = .26
COL_X = (.145, .665)
LABEL_X = (.008, .425)


def sheet_05():
    fig = plt.figure(figsize=(17, 13))
    fig.text(COL_X[0] + PANEL_W / 2, .885, "Body lower ring  /  body_lower.stl", fontsize=13,
             color=INK, ha="center")
    fig.text(COL_X[1] + PANEL_W / 2, .885, "Body upper ring  /  body_upper.stl", fontsize=13,
             color=INK, ha="center")
    for column, name in enumerate(("body_lower", "body_upper")):
        iso = fig.add_axes([COL_X[column], .525, PANEL_W, .33], projection="3d")
        sec = fig.add_axes([COL_X[column], .135, PANEL_W, .33])
        if not have(name):
            missing_banner(iso, [name + ".stl"])
            missing_banner(sec, [name + ".stl"])
            continue
        mesh = stl(name, process=True)
        draw_meshes(iso, [(mesh, PART_COLOR[name], name)])
        pad = np.maximum(mesh.extents * .06, 2)
        setup_3d(iso, [mesh.bounds[0] - pad, mesh.bounds[1] + pad], elev=24, azim=-58,
                 tick_step=100, zoom=1.15)
        iso.set_title("Isometric, print orientation", fontsize=10.5, pad=2)
        half = _section(mesh)
        if half is not None:
            draw_meshes(sec, [(half, PART_COLOR[name], name)], edges=True)
            lo, hi = mesh.bounds
            setup_ortho(sec, "left", (lo[1] - 12, hi[1] + 12), (lo[2] - 8, hi[2] + 8),
                        "Section X = 0, looking toward +X")
        if name == "body_lower":
            height = P["body_lower_h"]
            entries = [((0, P["battery_y"], P["battery_shelf_z"]),
                        "Battery shelf Z %.0f mm\n%.0f x %.0f x %.0f mm bay"
                        % (P["battery_shelf_z"], *P["battery"])),
                       ((0, 0, P["floor_t"] / 2),
                        "Skirt floor plate %.0f mm\ncentre-leg flange bolts" % P["floor_t"]),
                       ((0, -P["rod_r"], height * .62),
                        "M8 rod boss dia %.0f mm\nfour on R%.0f mm" % (P["rod_boss_d"], P["rod_r"])),
                       ((0, -P["skirt_flat_y"], 18),
                        "Skirt flat Y %.1f mm\nskirt height %.1f mm"
                        % (P["skirt_flat_y"], P["skirt_h"])),
                       ((0, 120, height - P["seam_lip_h"] / 2),
                        "Seam lip %.0f x %.0f mm\n%d x M%d flange bolts"
                        % (P["seam_lip_h"], P["seam_lip_t"], P["seam_bolt_n"], P["seam_bolt_m"]))]
        else:
            height = P["body_upper_h"]
            entries = [((0, 0, P["tray_z_upper"]),
                        "Integral electronics deck\nZ %.0f mm above the seam" % P["tray_z_upper"]),
                       ((P["body_r"] - 24, 0, P["shoulder_z_upper"]),
                        "Shoulder boss dia %.0f mm\nM%d pivot + index pins"
                        % (P["shoulder_boss_d"], P["shoulder_bolt_m"])),
                       ((0, 0, height - P["body_lip_h"]),
                        "Lazy-susan seat %.1f mm\ntop plate %.0f mm thick"
                        % (P["susan_od"], P["body_top_plate_t"])),
                       ((0, P["top_plate_opening_r"], height - P["body_lip_h"]),
                        "Plate opening R%.0f mm\nhead slot %.0f x %.0f mm"
                        % (P["top_plate_opening_r"], *P["head_slot"])),
                       ((0, -P["rod_r"], height * .5),
                        "M8 rod boss dia %.0f mm\nfour rods tie the rings" % P["rod_boss_d"])]
        side_callouts(fig, sec, entries, LABEL_X[column], .455, .155, fontsize=8.2)
    heading(fig, "fable-r2d2 / body rings",
            "The two stacked body rings printed skirt-down and lip-down | Sections on the X = 0 "
            "plane with the left half removed")
    footer(fig, "Ring seam 246.0 mm below the body top; four M8 rods and eight M4 flange bolts "
                "carry the joint.")
    title_block(fig, "05", "Body rings / isometric and X = 0 section", "body_lower, body_upper",
                "Lower %.1f mm, upper %.1f mm tall, dia %.1f mm"
                % (P["body_lower_h"], P["body_upper_h"], P["body_od"]),
                "Scale: per panel, axes in mm")
    frame(fig)
    save(fig, "05_body_rings.png")


def sheet_06():
    fig = plt.figure(figsize=(17, 13))
    if not have("dome"):
        ax = fig.add_axes([.1, .2, .8, .6])
        missing_banner(ax, ["dome.stl"])
    else:
        mesh = stl("dome", process=True)
        lo, hi = mesh.bounds
        layout = [("front", 0, .52), ("rear", 1, .52), ("top", 0, .13), ("bottom", 1, .13)]
        axes = {}
        for view, column, y0 in layout:
            ax = fig.add_axes([COL_X[column], y0, PANEL_W, .34])
            draw_meshes(ax, [(mesh, PART_COLOR["dome"], "dome")], edges=True)
            if view in ("front", "rear"):
                setup_ortho(ax, view, (lo[0] - 10, hi[0] + 10), (lo[2] - 8, hi[2] + 12))
            else:
                setup_ortho(ax, view, (lo[0] - 10, hi[0] + 10), (lo[1] - 10, hi[1] + 10))
            axes[view] = ax
        front = [(dome_point(P["dome_eye_angle"], P["dome_eye_z"]),
                  "Radar eye lens dia %.1f mm\nround TFT %.1f x %.1f behind"
                  % (P["dome_eye_lens_d"], P["dome_eye_lcd_pcb"][0], P["dome_eye_lcd_pcb"][1])),
                 (dome_point(P["dome_fld_angle"], P["dome_fld_z"][1]),
                  "Front logic display\ntwo %.0f x %.0f mm windows" % tuple(P["dome_fld_window"])),
                 (dome_point(P["dome_front_psi"][0], P["dome_front_psi"][1]),
                  "Front PSI dia %.0f mm\nNeoPixel jewel behind" % P["dome_front_psi"][2]),
                 (dome_point(P["dome_hp1"][0], P["dome_hp1"][1]),
                  "Holoprojector dia %.1f mm\nthree per dome" % P["dome_hp_d"]),
                 ((0, 0, P["dome_plate_t"] / 2),
                  "Internal plate %.0f mm\nR%.0f-%.1f annulus"
                  % (P["dome_plate_t"], P["dome_plate_r_in"], P["dome_plate_r_out"]))]
        side_callouts(fig, axes["front"], front, LABEL_X[0], .845, .555)
        rear = [(dome_point(P["dome_rld_angle"], P["dome_rld_z"]),
                 "Rear logic display\n%.0f x %.0f mm window" % tuple(P["dome_rld_window"])),
                (dome_point(P["dome_rear_psi"][0], P["dome_rear_psi"][1]),
                 "Rear PSI dia %.0f mm" % P["dome_rear_psi"][2]),
                (dome_point(P["dome_hp2"][0], P["dome_hp2"][1]), "Rear holoprojector"),
                ((0, 0, P["dome_band_h"] / 2),
                 "Cylindrical band %.1f mm\nfriction ring for the\nhead drive" % P["dome_band_h"])]
        side_callouts(fig, axes["rear"], rear, LABEL_X[1], .845, .565)
        top = [((0, 0, P["dome_height"]),
                "Top disc dia %.1f mm\nopening %.1f mm"
                % (P["dome_top_disc_d"], P["dome_top_disc_opening_d"])),
               (dome_point(P["dome_hp3_angle"], 157.9, radius=P["dome_hp3_r"]),
                "Top holoprojector\nR%.0f mm from the axis" % P["dome_hp3_r"]),
               ((P["dome_pie_r_out"] * .66, P["dome_pie_r_out"] * .66, P["dome_height"] - 26),
                "Pie panels\nR%.1f-%.1f mm" % (P["dome_pie_r_in"], P["dome_pie_r_out"]))]
        side_callouts(fig, axes["top"], top, LABEL_X[0], .430, .190)
        bottom = [(dome_point(45, 2.5, radius=P["susan_hole_r"]),
                   "Lazy-susan top-race screws\n4 x M%d on R%.1f mm"
                   % (P["susan_screw_m"], P["susan_hole_r"])),
                  ((0, 0, P["dome_plate_t"]),
                   "Plate bore dia %.0f mm\nslip-ring rotor passes" % (2 * P["dome_plate_r_in"])),
                  (dome_point(0, 2.5, radius=P["dome_wire_anchor_r"]),
                   "Wire anchor lug R%.0f mm\nheat-set inserts" % P["dome_wire_anchor_r"])]
        side_callouts(fig, axes["bottom"], bottom, LABEL_X[1], .430, .190)
    heading(fig, "fable-r2d2 / dome",
            "One-piece printed dome, %.1f mm diameter x %.1f mm tall | Every display, "
            "holoprojector and PSI opening is modelled in the STL"
            % (P["dome_od"], P["dome_height"]))
    footer(fig, "Displays, jewels and the slip ring mount to the internal plate on heat-set "
                "inserts; sheet 15 is the dome exploded view.")
    title_block(fig, "06", "Dome / front, rear, top and bottom views", "dome",
                "%.1f dia x %.1f mm tall, wall %.1f mm"
                % (P["dome_od"], P["dome_height"], P["dome_wall"]),
                "Scale: per panel, axes in mm")
    frame(fig)
    save(fig, "06_dome.png")


LEG_X = (.105, .430, .755)
LEG_LABEL_X = (.006, .315, .640)
LEG_W = .20


def sheet_07():
    fig = plt.figure(figsize=(18, 12.5))
    names = ["leg_upper", "leg_lower", "leg_center"]
    for column, name in enumerate(names):
        fig.text(LEG_X[column] + LEG_W / 2, .885, "%s  /  %s.stl" % (TITLES[name], name),
                 fontsize=12, color=INK, ha="center")
        iso = fig.add_axes([LEG_X[column], .495, LEG_W, .34], projection="3d")
        side = fig.add_axes([LEG_X[column], .135, LEG_W, .32])
        if not have(name):
            missing_banner(iso, [name + ".stl"])
            missing_banner(side, [name + ".stl"])
            continue
        mesh = stl(name, process=True)
        native = mesh.copy()
        native.apply_transform(LAY.print_inverse(name))
        draw_meshes(iso, [(mesh, PART_COLOR[name], name)], edges=True)
        pad = np.maximum(mesh.extents * .06, 2)
        setup_3d(iso, [mesh.bounds[0] - pad, mesh.bounds[1] + pad], elev=26, azim=-56,
                 tick_step=100, zoom=1.2)
        iso.set_title("Isometric, print orientation", fontsize=10, pad=1)
        lo, hi = native.bounds
        draw_meshes(side, [(native, PART_COLOR[name], name)], edges=True)
        setup_ortho(side, "right", (lo[1] - 12, hi[1] + 12), (lo[2] - 12, hi[2] + 12),
                    "Side view, assembled frame")
        if name == "leg_upper":
            entries = [((0, 0, 0), "Shoulder disc dia %.1f\nM%d pivot bolt"
                        % (P["leg_disc_d"], P["shoulder_bolt_m"])),
                       ((0, P["leg_rod_offset"], P["leg_rod_top_z"]),
                        "Two M8 rod channels\nY +/- %.0f mm, nut trap\nZ %.0f mm"
                        % (P["leg_rod_offset"], LEGS["lg_rod_nut_z"])),
                       ((0, 0, P["leg_split_z"] + P["leg_splice_len"] / 2),
                        "Splice lap %.0f mm\n4 x M%d bolts"
                        % (P["leg_splice_len"], P["leg_splice_bolt_m"])),
                       ((0, -40, LEGS["lg_channel_top_z"]),
                        "Booster cover channel\n%.1f x %.1f mm"
                        % (P["booster_cover"][0], P["booster_cover"][1]))]
        elif name == "leg_lower":
            entries = [((0, 0, P["leg_split_z"] + 22),
                        "Splice face Z %.0f mm\nprinted flat for\nlayer strength" % P["leg_split_z"]),
                       ((0, 0, LEGS["lg_ankle_crown_z"]),
                        "Ankle starts Z %.0f mm\n%.1f x %.1f mm section"
                        % (LEGS["lg_ankle_crown_z"], P["leg_ankle_w"], P["leg_ankle_t"])),
                       ((0, 0, -P["leg_len"] - LEGS["lg_pivot_up"]),
                        "Ankle pivot bore M%d\nZ %.1f mm"
                        % (P["ankle_bolt_m"], -P["leg_len"] - LEGS["lg_pivot_up"])),
                       ((0, 0, LEGS["lg_tongue_bottom_z"] + P["leg_tongue_depth"] / 2),
                        "Tongue %.0f x %.1f mm\n%.0f mm into the foot"
                        % (P["leg_tongue_w"], P["leg_tongue_t"], P["leg_tongue_depth"])),
                       ((0, 0, LEGS["lg_bracelet_z"]),
                        "Bracelet band\nankle detail")]
        else:
            entries = [((0, 0, LEGS["lg_bearing1_z"]),
                        "Lower 6001 bearing\nseat 28 x 12 x 8 mm"),
                       ((0, 0, LEGS["lg_bearing2_z"]),
                        "Upper 6001 bearing\ncentres %.0f mm apart" % LEGS["lg_bearing_cc"]),
                       ((0, 0, LEGS["lg_center_plane_z"] + P["center_leg_flange"][2]),
                        "Body flange %.0f x %.0f\n4 x M%d into the floor"
                        % (P["center_leg_flange"][0], P["center_leg_flange"][1],
                           P["center_leg_bolt_m"])),
                       ((0, 0, LEGS["lg_center_bottom_z"]),
                        "Caster bore M%d\nfoot stem from below" % P["caster_bolt_m"]),
                       ((0, -LEGS["lg_stop_r"], LEGS["lg_center_bottom_z"] + 8),
                        "Swivel stops\n+/- %.0f deg" % P["caster_stop_deg"])]
        side_callouts(fig, side, entries, LEG_LABEL_X[column], .430, .155, fontsize=8.0)
    heading(fig, "fable-r2d2 / legs",
            "Outer leg %.1f mm shoulder to ankle, printed in two pieces and spliced over two M8 "
            "rods | The centre leg carries the caster ankle" % P["leg_len"])
    footer(fig, "Leg frame: Z = 0 at the shoulder axis, +Y forward, the leg leaning %.0f deg in "
                "the three-leg stance." % P["leg_lean"])
    title_block(fig, "07", "Legs / isometric and side views",
                "leg_upper (x2, mirrored), leg_lower (x2, mirrored), leg_center",
                "Leg length %.1f mm, split at Z %.0f mm" % (P["leg_len"], P["leg_split_z"]),
                "Scale: per panel, axes in mm")
    frame(fig)
    save(fig, "07_legs.png")


def sheet_08():
    fig = plt.figure(figsize=(17, 12.5))
    for column, name in enumerate(("foot_outer", "foot_center")):
        fig.text(COL_X[column] + PANEL_W / 2, .855, "%s  /  %s.stl" % (TITLES[name], name),
                 fontsize=12.5, color=INK, ha="center")
        iso = fig.add_axes([COL_X[column], .490, PANEL_W, .33], projection="3d")
        bottom = fig.add_axes([COL_X[column], .135, PANEL_W, .31])
        if not have(name):
            missing_banner(iso, [name + ".stl"])
            missing_banner(bottom, [name + ".stl"])
            continue
        mesh = stl(name, process=True)
        matrix = LAY.at_foot(1) if name == "foot_outer" else LAY.at_center_foot()
        local = np.linalg.inv(matrix)
        drive = []
        for m in LAY.motor_matrices(matrix, center=(name == "foot_center")):
            drive.append((tt_motor_mesh(local @ m), MOTOR, "TT motor"))
        for m in LAY.wheel_matrices(matrix):
            drive.append((wheel_mesh(local @ m), WHEEL, "Wheel"))
        allitems = [(mesh, PART_COLOR[name], name)] + drive
        draw_meshes(iso, allitems)
        lo, hi = items_bounds(allitems, pad=.06)
        setup_3d(iso, (lo, hi), elev=24, azim=-58, tick_step=50, zoom=1.15)
        iso.set_title("Isometric with motor and wheel envelopes", fontsize=10, pad=2)
        draw_meshes(bottom, allitems)
        setup_ortho(bottom, "bottom", (lo[0], hi[0]), (lo[1], hi[1]))
        if name == "foot_outer":
            entries = [((0, P["foot_axle_y"], P["wheel_axle_z"]),
                        "Motor channel Y +%.0f\ncan %.0f deg below\nhorizontal"
                        % (P["foot_axle_y"], FEET["ft_motor_tilt_o"])),
                       ((P["wheel_x"], -P["foot_axle_y"], P["wheel_axle_z"]),
                        "Wheel cavity %.0f x %.0f\nfour per foot"
                        % (P["wheel_d"], P["wheel_w"])),
                       ((0, 0, P["foot_outer_h"] + FEET["ft_block"][2] / 2),
                        "Ankle block %.0f x %.0f x %.0f\nslot %.1f mm wide"
                        % (*FEET["ft_block"], P["foot_slot_w"])),
                       ((-60, 0, 30), "Battery box detail\n%.1f x %.1f mm"
                        % (P["battery_box"][0], P["battery_box"][1])),
                       ((0, 0, 2), "Sole %.1f x %.1f mm\nwall %.1f mm"
                        % (P["foot_outer_l_bot"], P["foot_outer_w_bot"], P["foot_wall"]))]
        else:
            entries = [((0, P["foot_axle_y"], P["wheel_axle_z"]),
                        "Front motor %.0f deg\nfrom vertical" % FEET["ft_phi_c_front"]),
                       ((0, -P["foot_axle_y"], P["wheel_axle_z"]),
                        "Rear motor %.0f deg\nfrom vertical" % FEET["ft_phi_c_rear"]),
                       ((P["wheel_x"], P["foot_axle_y"], P["wheel_axle_z"]),
                        "Wheel cavity %.0f x %.0f\nfour per foot" % (P["wheel_d"], P["wheel_w"])),
                       ((0, P["caster_trail"], P["foot_center_h"] + FEET["ft_stem"][2] / 2),
                        "Caster stem %.0f x %.0f x %.0f\nM%d bolt on the trail"
                        % (*FEET["ft_stem"], P["caster_bolt_m"])),
                       ((0, 0, 2), "Sole %.1f x %.1f mm"
                        % (P["foot_center_l_bot"], P["foot_center_w_bot"]))]
        side_callouts(fig, bottom, entries, LABEL_X[column], .430, .150, fontsize=8.2)
    legend(fig, [("Printed foot shell", PART_COLOR["foot_outer"]), ("TT motor 3777", MOTOR),
                 ("Wheel 3766", WHEEL)], position=(.50, .898), title_text=None, ncol=3,
           loc="center")
    heading(fig, "fable-r2d2 / feet",
            "Each foot carries two Adafruit 3777 TT motors and four 3766 wheels | Shell bottom "
            "edge %.0f mm above the floor, axle height %.1f mm"
            % (P["foot_clear"], P["wheel_axle_z"] + P["foot_clear"]))
    footer(fig, "Foot frame: Z = 0 at the shell bottom edge, +Y forward. Wheels press on to the "
                "TT D-shafts; the motor cans tie into the printed channels.")
    title_block(fig, "08", "Feet / isometric and bottom views",
                "foot_outer (x2, mirrored), foot_center",
                "Outer %.1f x %.1f x %.1f mm"
                % (P["foot_outer_l_bot"], P["foot_outer_w_bot"], P["foot_outer_h"]),
                "Scale: per panel, axes in mm")
    frame(fig)
    save(fig, "08_feet.png")


def _head_drive_hardware(matrix, explode=None):
    """Hinge bolt, tension screw, spring, thumb nut and stop screw envelopes."""
    shift = explode or {}
    axle_z = HEAD["hd_hinge_z"]
    hinge_y = HEAD["hd_hinge_y"]
    tx, ty = HEAD["hd_tension_xy"]
    sx, sy = HEAD["hd_stop_xy"]
    plate = P["body_top_plate_t"]
    return [
        (moved(bolt_mesh(P["head_drive_hinge_m"], 62, (-31, hinge_y, axle_z), axis="x", sign=1,
                         matrix=matrix), shift.get("hinge", (0, 0, 0))), STEEL, "M4 hinge bolt"),
        (moved(bolt_mesh(P["head_drive_tension_m"], 40, (tx, ty, -plate), axis="z", sign=-1,
                         matrix=matrix), shift.get("tension", (0, 0, 0))), STEEL,
         "M5 x 40 tension screw"),
        (moved(prim_ring(HEAD["hd_spring_od"], P["head_drive_tension_m"] + 1,
                         HEAD["hd_spring_free"],
                         (tx, ty, -plate - 8 - HEAD["hd_spring_free"] / 2), matrix=matrix),
               shift.get("spring", (0, 0, 0))), SPRING, "Compression spring"),
        (moved(prim_hex(18, 8, (tx, ty, -plate - 36), matrix=matrix),
               shift.get("thumbnut", (0, 0, 0))), STEEL, "Thumb nut"),
        (moved(bolt_mesh(5, HEAD["hd_stop_screw_l"], (sx, sy, -plate), axis="z", sign=-1,
                         matrix=matrix), shift.get("stop", (0, 0, 0))), STEEL, "Stop screw")]


def sheet_09():
    body_frame = T(0, 0, P["body_top_plate_z"])
    matrix = body_frame @ LAY.print_inverse("head_drive")
    plate_z = P["body_top_plate_z"]
    items = []
    if have("head_drive"):
        items.append((placed("head_drive", matrix), PART_COLOR["head_drive"], "head_drive"))
    items += head_drive_items(body_frame)
    items += _head_drive_hardware(body_frame)
    items.append((prim_ring(P["susan_od"], P["susan_id"], P["susan_t"],
                            (0, 0, plate_z + P["susan_t"] / 2)), SUSAN, "Lazy susan"))
    if have("body_upper"):
        upper = placed("body_upper", T(0, 0, P["body_lower_h"]))
        band = upper.slice_plane([0, 0, plate_z - 9], [0, 0, 1])
        if band is not None and len(band.faces):
            items.append((band, PART_COLOR["body_upper"], "body_upper"))
    if have("dome"):
        dome = placed("dome", T(0, 0, P["body_height"] + P["dome_gap"]))
        plate = dome.slice_plane([0, 0, P["body_height"] + P["dome_gap"] + P["dome_plate_t"] + 4],
                                 [0, 0, -1])
        if plate is not None and len(plate.faces):
            items.append((plate, DOME_SILVER, "dome plate"))
    fig = plt.figure(figsize=(16, 11))
    iso = fig.add_axes([.050, .19, .37, .60], projection="3d")
    draw_meshes(iso, items)
    setup_3d(iso, ([-170, -190, plate_z - 55], [170, 60, plate_z + 22]), elev=-22, azim=-108,
             tick_step=50, zoom=1.1)
    iso.set_title("Isometric from below, looking up at the top plate", fontsize=11, pad=6)
    sec = fig.add_axes([.500, .30, .33, .44])
    half = []
    for mesh, color, label in items:
        cut = mesh.slice_plane([0, 0, 0], [1, 0, 0])
        if cut is not None and len(cut.faces):
            half.append((cut, color, label))
    draw_meshes(sec, half if half else items, edges=True)
    setup_ortho(sec, "left", (-195, 45), (plate_z - 52, plate_z + 24),
                "Section X = 0 / tension train")
    axle_z = plate_z + HEAD["hd_hinge_z"]
    tx, ty = HEAD["hd_tension_xy"]
    entries = [((0, -P["head_wheel_r"], axle_z),
                "Friction wheel %.0f x %.0f mm on R%.0f mm\n%.1f mm tyre squeeze on the dome plate"
                % (P["wheel_d"], P["wheel_w"], P["head_wheel_r"], HEAD["hd_squeeze"])),
               ((0, HEAD["hd_motor_y"] + HEAD["hd_hinge_y"], axle_z),
                "TT motor 3777, can pointing -X\nfour M3 screws into the arm"),
               ((0, HEAD["hd_hinge_y"], axle_z),
                "Hinge axis M%d at Y %.0f mm\nthe arm swings in the Y-Z plane"
                % (P["head_drive_hinge_m"], HEAD["hd_hinge_y"])),
               ((0, ty, plate_z - 22),
                "M%d x 40 tension screw\nspring OD %.0f mm, thumb nut below"
                % (P["head_drive_tension_m"], HEAD["hd_spring_od"])),
               ((0, ty, plate_z - 40),
                "Thumb nut sets the squeeze\nno tools needed"),
               ((0, 0, plate_z + P["susan_t"] / 2),
                "Lazy susan %.1f / %.1f x %.1f mm\ncarries the dome"
                % (P["susan_od"], P["susan_id"], P["susan_t"])),
               ((0, HEAD["hd_stop_xy"][1], plate_z - 14),
                "Stop screw limits lift to\n%.1f mm above the working height"
                % HEAD["hd_stop_travel"])]
    side_callouts(fig, sec, entries, .845, .820, .300, fontsize=8.6, exit_right=False)
    legend(fig, [("Head-drive mount (printed)", PART_COLOR["head_drive"]), ("TT motor 3777", MOTOR),
                 ("Wheel 3766", WHEEL), ("Lazy susan", SUSAN), ("Spring", SPRING),
                 ("Steel fasteners", STEEL), ("Body upper (section)", PART_COLOR["body_upper"]),
                 ("Dome plate (section)", DOME_SILVER)], position=(.070, .155),
           title_text=None, ncol=3, loc="lower left", fontsize=8.8)
    heading(fig, "fable-r2d2 / head friction drive",
            "The seventh TT motor turns the dome through a 63 mm tyre pressed on the underside of "
            "the dome plate | Body frame, Z = 0 at the skirt bottom")
    footer(fig, "Tension: slacken the thumb nut, seat the dome, then tighten until the tyre "
                "compresses %.1f mm; the stop screw prevents over-lift." % HEAD["hd_squeeze"])
    title_block(fig, "09", "Head friction drive / working position",
                "head_drive, body_upper (section), dome plate (section)",
                "Wheel radius %.0f mm, squeeze %.1f mm" % (P["head_wheel_r"], HEAD["hd_squeeze"]),
                "Scale: per panel, axes in mm")
    frame(fig)
    save(fig, "09_head_drive.png")


def sheet_10():
    fig = plt.figure(figsize=(18, 12))
    for column, name in enumerate(("foot_outer", "foot_center")):
        x0 = .045 + column * .48
        ax = fig.add_axes([x0, .17, .44, .66], projection="3d")
        if not have(name):
            missing_banner(ax, [name + ".stl"])
            continue
        matrix = LAY.at_foot(1) if name == "foot_outer" else LAY.at_center_foot()
        local = np.linalg.inv(matrix)
        items = [(stl(name, process=True), PART_COLOR[name], name)]
        for index, m in enumerate(LAY.motor_matrices(matrix, center=(name == "foot_center"))):
            mesh = tt_motor_mesh(local @ m)
            mesh.apply_translation((-150, 0, 90 + index * 30))
            items.append((mesh, MOTOR, "TT motor"))
        for index, m in enumerate(LAY.wheel_matrices(matrix)):
            mesh = wheel_mesh(local @ m)
            sign = 1 if mesh.centroid[0] > 0 else -1
            mesh.apply_translation((sign * 120, 0, 0))
            items.append((mesh, WHEEL, "Wheel"))
        if name == "foot_outer":
            for sign in (-1, 1):
                items.append((bolt_mesh(3, 22, (sign * FEET["ft_end_hw"], 165, 60), axis="y",
                                        sign=-1), STEEL, "M3 tab bolt"))
                items.append((bolt_mesh(3, 22, (sign * FEET["ft_end_hw"], -165, 60), axis="y",
                                        sign=1), STEEL, "M3 tab bolt"))
            items.append((bolt_mesh(P["ankle_bolt_m"], 70, (-60, 0, P["foot_outer_h"] + 9),
                                    axis="x", sign=1), STEEL, "M8 ankle bolt"))
        else:
            stem_z = P["foot_center_h"] + FEET["ft_stem"][2]
            items.append((bolt_mesh(P["caster_bolt_m"], 90, (0, P["caster_trail"], stem_z + 150),
                                    axis="z", sign=-1), STEEL, "M12 caster bolt"))
            for index, z in enumerate((stem_z + 70, stem_z + 100)):
                items.append((prim_ring(P["caster_bearing_od"], 12, P["caster_bearing_t"],
                                        (0, P["caster_trail"], z)), BEARING, "6001 bearing"))
        draw_meshes(ax, items)
        lo, hi = items_bounds(items, pad=.06)
        setup_3d(ax, (lo, hi), elev=20, azim=-58, tick_step=50)
        ax.set_title(f"{TITLES[name]} / exploded", fontsize=12, pad=6)
        if name == "foot_outer":
            entries = [((-150, 45, 120), "Two TT motors 3777\npressed into the printed channels", "L"),
                       ((120 + P["wheel_x"], 45, P["wheel_axle_z"]),
                        "Four wheels 3766\npress fit on the D-shafts", "R"),
                       ((FEET["ft_end_hw"], 165, 60), "M3 tab bolts\nclose the motor channels", "L"),
                       ((-60, 0, P["foot_outer_h"] + 9),
                        f"M{int(P['ankle_bolt_m'])} ankle bolts through\nthe block and leg tongue", "R")]
        else:
            entries = [((-150, 45, 120), "Two TT motors 3777", "L"),
                       ((120 + P["wheel_x"], 45, P["wheel_axle_z"]), "Four wheels 3766", "R"),
                       ((0, P["caster_trail"], stem_z + 85),
                        "Two 6001 bearings\n28 x 12 x 8 mm", "R"),
                       ((0, P["caster_trail"], stem_z + 150),
                        f"M{int(P['caster_bolt_m'])} caster bolt\ninto the centre leg", "R"),
                       ((0, P["caster_trail"], stem_z - 10),
                        f"Caster stem block\ntrail {P['caster_trail']:.0f} mm", "L")]
        callouts(fig, ax, entries, left_x=x0 - .028, right_x=x0 + .355, top=.79, bottom=.22,
                 fontsize=8.6)
    heading(fig, "fable-r2d2 / feet exploded",
            "Outer foot with its two motors, four wheels and tab bolts; centre foot with the "
            "M12 caster bolt and two 6001 bearings")
    footer(fig, "Motors are retained by printed straps and cable ties in the channel grooves; "
                "wheels press on without adhesive.")
    title_block(fig, "10", "Feet exploded / drive install", "foot_outer, foot_center",
                "4 x TT 3777, 8 x wheel 3766 shown", "Scale: per panel, axes in mm")
    frame(fig)
    save(fig, "10_exploded_feet.png")


def sheet_11():
    fig = plt.figure(figsize=(16, 13))
    ax = fig.add_axes([.10, .14, .58, .74], projection="3d")
    items = []
    for name, shift in (("leg_upper", (0, 0, 0)), ("leg_lower", (0, 60, -150))):
        if have(name):
            mesh = placed(name, LAY.print_inverse(name), shift)
            items.append((mesh, PART_COLOR[name], name))
    rod_len = LEGS["lg_rod_nut_z"] - LEGS["lg_rod_bottom_z"]
    for sign in (-1, 1):
        items.append((prim_cyl(P["leg_rod_d"], rod_len,
                               (LEGS["lg_rod_x"] + 150, sign * P["leg_rod_offset"],
                                (LEGS["lg_rod_nut_z"] + LEGS["lg_rod_bottom_z"]) / 2)),
                      STEEL, "M8 rod"))
    for x in LEGS["lg_splice_x"]:
        for z in LEGS["lg_splice_z"]:
            items.append((bolt_mesh(P["leg_splice_bolt_m"], 40, (x, -110, z), axis="y", sign=1),
                          STEEL, "M4 splice bolt"))
    if have("foot_outer"):
        foot = np.linalg.inv(LAY.at_leg(1)) @ LAY.at_foot(1)
        mesh = placed("foot_outer", foot, (0, 110, -260))
        items.append((mesh, PART_COLOR["foot_outer"], "foot_outer"))
    if not items:
        missing_banner(ax, ["leg_upper.stl", "leg_lower.stl"])
    else:
        draw_meshes(ax, items)
        lo, hi = items_bounds(items, pad=.05)
        setup_3d(ax, (lo, hi), elev=16, azim=-64, tick_step=100)
        entries = [((0, 0, 0), f"Shoulder disc\nM{int(P['shoulder_bolt_m'])} pivot bolt", "L"),
                   ((LEGS["lg_rod_x"] + 150, P["leg_rod_offset"], LEGS["lg_rod_nut_z"]),
                    f"Two M8 rods, {rod_len:.0f} mm\ncaptive nuts at the top", "R"),
                   ((LEGS["lg_splice_x"][1], -110, LEGS["lg_splice_z"][1]),
                    f"4 x M{int(P['leg_splice_bolt_m'])} splice bolts\n"
                    f"{P['leg_splice_len']:.0f} mm lap joint", "R"),
                   ((0, 60, P["leg_split_z"] - 150),
                    f"Lower leg, split at Z {P['leg_split_z']:.0f} mm", "L"),
                   ((0, 60 + 0, LEGS["lg_tongue_bottom_z"] - 150 + 15),
                    f"Tongue {P['leg_tongue_w']:.0f} x {P['leg_tongue_t']:.1f} mm\ninto the foot "
                    f"slot", "L"),
                   ((0, 170, -430), f"Outer foot ankle block\n2 x M{int(P['ankle_bolt_m'])} "
                                    "through bolts", "R")]
        callouts(fig, ax, entries, left_x=.028, right_x=.705, top=.83, bottom=.22, fontsize=9)
    legend(fig, [("leg_upper", PART_COLOR["leg_upper"]), ("leg_lower", PART_COLOR["leg_lower"]),
                 ("foot_outer", PART_COLOR["foot_outer"]), ("M8 rods and bolts", STEEL)],
           position=(.775, .55), title_text=None)
    heading(fig, "fable-r2d2 / outer leg exploded",
            f"Leg frame, Z = 0 at the shoulder axis | Two prints joined by a "
            f"{P['leg_splice_len']:.0f} mm lap splice and two full-length M8 rods")
    footer(fig, "Assembly order: thread the rods into the upper leg nut traps, slide the lower "
                "leg on, fit the four M4 splice bolts, then bolt the tongue into the foot.")
    title_block(fig, "11", "Outer leg exploded", "leg_upper, leg_lower, foot_outer",
                f"Leg {P['leg_len']:.1f} mm, rods {rod_len:.0f} mm",
                "Scale: fit to sheet, axes in mm")
    frame(fig)
    save(fig, "11_exploded_leg.png")


def sheet_12():
    fig = plt.figure(figsize=(16, 12.5))
    ax = fig.add_axes([.10, .14, .58, .73], projection="3d")
    items = []
    if have("leg_center"):
        items.append((placed("leg_center", LAY.print_inverse("leg_center")),
                      PART_COLOR["leg_center"], "leg_center"))
    for index, z in enumerate((LEGS["lg_bearing1_z"], LEGS["lg_bearing2_z"])):
        items.append((prim_ring(P["caster_bearing_od"], 12, P["caster_bearing_t"],
                                (0, -110 - index * 45, z + P["caster_bearing_t"] / 2)),
                      BEARING, "6001 bearing"))
    items.append((bolt_mesh(P["caster_bolt_m"], 80, (0, 0, LEGS["lg_center_bottom_z"] - 120),
                            axis="z", sign=1), STEEL, "M12 caster bolt"))
    for x, y in P["center_leg_bolts"]:
        items.append((bolt_mesh(P["center_leg_bolt_m"], 30,
                                (x, y, LEGS["lg_center_plane_z"] + P["center_leg_flange"][2] + 70),
                                axis="z", sign=-1), STEEL, "M8 flange bolt"))
    if have("foot_center"):
        foot = np.linalg.inv(LAY.at_center_leg()) @ LAY.at_center_foot()
        items.append((placed("foot_center", foot, (0, 0, -150)), PART_COLOR["foot_center"],
                      "foot_center"))
    if not items:
        missing_banner(ax, ["leg_center.stl"])
    else:
        draw_meshes(ax, items)
        lo, hi = items_bounds(items, pad=.06)
        setup_3d(ax, (lo, hi), elev=18, azim=-60, tick_step=50)
        entries = [((0, 0, LEGS["lg_center_plane_z"] + P["center_leg_flange"][2] + 70),
                    f"4 x M{int(P['center_leg_bolt_m'])} flange bolts\ninto the body floor plate", "R"),
                   ((0, 0, LEGS["lg_center_plane_z"]),
                    f"Body flange {P['center_leg_flange'][0]:.0f} x "
                    f"{P['center_leg_flange'][1]:.0f} x {P['center_leg_flange'][2]:.0f} mm", "L"),
                   ((0, -110, LEGS["lg_bearing1_z"] + 4), "Two 6001 bearings\n28 x 12 x 8 mm, "
                                                          f"{LEGS['lg_bearing_cc']:.0f} mm apart", "L"),
                   ((0, 0, LEGS["lg_center_bottom_z"] - 120),
                    f"M{int(P['caster_bolt_m'])} caster bolt\nvertical swivel axis", "R"),
                   ((0, 0, -120), f"Centre foot stem\ntrail {P['caster_trail']:.0f} mm, stops "
                                  f"+/- {P['caster_stop_deg']:.0f} deg", "R")]
        callouts(fig, ax, entries, left_x=.028, right_x=.705, top=.80, bottom=.24, fontsize=9)
    legend(fig, [("leg_center", PART_COLOR["leg_center"]), ("foot_center", PART_COLOR["foot_center"]),
                 ("6001 bearings", BEARING), ("Steel bolts", STEEL)], position=(.775, .55),
           title_text=None)
    heading(fig, "fable-r2d2 / centre leg exploded",
            "Vertical caster ankle on two 6001 ball bearings so the six fixed-axle drive wheels "
            "can steer the robot without scrubbing the centre foot")
    footer(fig, "The centre leg is fully retracted in the three-leg stance; the flange bolts up "
                "into the skirt floor plate.")
    title_block(fig, "12", "Centre leg exploded / caster ankle", "leg_center, foot_center",
                f"Bearings 28 x 12 x 8 mm, M{int(P['caster_bolt_m'])} bolt",
                "Scale: fit to sheet, axes in mm")
    frame(fig)
    save(fig, "12_exploded_center_leg.png")


def sheet_13():
    fig = plt.figure(figsize=(16.5, 13))
    ax = fig.add_axes([.09, .13, .60, .75], projection="3d")
    items = []
    lift = 330
    if have("body_lower"):
        items.append((placed("body_lower"), PART_COLOR["body_lower"], "body_lower"))
    if have("body_upper"):
        items.append((placed("body_upper", T(0, 0, P["body_lower_h"] + lift)),
                      PART_COLOR["body_upper"], "body_upper"))
    bx, by, bz = P["battery"]
    items.append((prim_box((bx, by, bz), (0, P["battery_y"], P["battery_shelf_z"] + bz / 2 + 150)),
                  BATTERY, "Battery"))
    for y in (P["battery_y"] - 45, P["battery_y"] + 45):
        items.append((prim_box((bx + 8, P["battery_strap_w"], 3),
                               (0, y, P["battery_shelf_z"] + bz + 205)), STEEL, "Strap"))
    items.append((prim_cyl(P["speaker_d"], P["speaker_depth"], (0, 190, 108), axis="y"),
                  SPEAKER, "Speaker"))
    for index in range(int(P["rod_n"])):
        angle = math.radians(P["rod_angle0"] + index * 360.0 / P["rod_n"])
        length = P["body_top_plate_z"] - P["floor_t"]
        items.append((prim_cyl(P["rod_d"], length,
                               (P["rod_r"] * math.cos(angle), P["rod_r"] * math.sin(angle),
                                P["floor_t"] + length / 2 + lift + 320)), STEEL, "M8 rod"))
    for index in range(int(P["seam_bolt_n"])):
        angle = math.radians(index * 360.0 / P["seam_bolt_n"] + 22.5)
        radius = P["body_r"] - P["seam_flange_w"] / 2
        items.append((bolt_mesh(P["seam_bolt_m"], 24,
                                (radius * math.cos(angle), radius * math.sin(angle),
                                 P["body_lower_h"] + 150), axis="z", sign=-1), STEEL,
                      "M4 seam bolt"))
    for sign in (-1, 1):
        items.append((bolt_mesh(P["shoulder_bolt_m"], 120,
                                (sign * (P["body_r"] + 190), 0, P["shoulder_z"] + lift),
                                axis="x", sign=-sign), STEEL, "M12 shoulder bolt"))
        for angle in P["shoulder_index_angles"]:
            a = math.radians(angle)
            items.append((prim_cyl(6, 22, (sign * (P["body_r"] + 120),
                                           P["shoulder_index_r"] * math.sin(a),
                                           P["shoulder_z"] + lift + P["shoulder_index_r"] * math.cos(a)),
                                   axis="x"), STEEL, "Index pin"))
    if not any(label.startswith("body") for _, _, label in items):
        missing_banner(ax, ["body_lower.stl", "body_upper.stl"])
    else:
        draw_meshes(ax, items)
        lo, hi = items_bounds(items, pad=.05)
        setup_3d(ax, (lo, hi), elev=18, azim=-60, tick_step=100)
        entries = [((0, 0, P["body_lower_h"] / 2), "Body lower ring\nbattery bay and skirt", "L"),
                   ((0, P["battery_y"], P["battery_shelf_z"] + bz / 2 + 150),
                    f"Battery 12 V 7 Ah SLA\n{bx:.0f} x {by:.0f} x {bz:.0f} mm, 2.26 kg", "R"),
                   ((0, P["battery_y"] + 45, P["battery_shelf_z"] + bz + 205),
                    "Two hook-and-loop straps\n25 mm wide", "R"),
                   ((0, 190, 108), f"Speaker dia {P['speaker_d']:.1f} mm", "L"),
                   ((0, 0, P["body_lower_h"] + lift + 120), "Body upper ring\nlocating lip into "
                                                            "the lower ring", "R"),
                   ((P["body_r"] - P["seam_flange_w"] / 2, 0, P["body_lower_h"] + 150),
                    f"{int(P['seam_bolt_n'])} x M{int(P['seam_bolt_m'])} seam bolts", "L"),
                   ((P["rod_r"] * .7, P["rod_r"] * .7, lift + 520),
                    f"{int(P['rod_n'])} x M8 rods on R{P['rod_r']:.0f} mm\ntie both rings together", "R"),
                   ((P["body_r"] + 190, 0, P["shoulder_z"] + lift),
                    f"M{int(P['shoulder_bolt_m'])} shoulder bolt\nplus two 6 mm index pins", "L")]
        callouts(fig, ax, entries, left_x=.026, right_x=.715, top=.83, bottom=.20, fontsize=9)
    legend(fig, [("body_lower", PART_COLOR["body_lower"]), ("body_upper", PART_COLOR["body_upper"]),
                 ("Battery", BATTERY), ("Speaker", SPEAKER), ("Steel hardware", STEEL)],
           position=(.785, .55), title_text=None)
    heading(fig, "fable-r2d2 / body exploded",
            "Two printed rings, the 12 V 7 Ah battery on its shelf, the seam bolts, the four M8 "
            "tie rods and the shoulder pivots")
    footer(fig, "Fit the battery and its straps before closing the rings; the shoulder bolts and "
                "index pins set the two-leg or three-leg stance angle.")
    title_block(fig, "13", "Body exploded / battery, seam and shoulders",
                "body_lower, body_upper + battery, straps, speaker, rods, bolts, pins",
                f"Battery {bx:.0f} x {by:.0f} x {bz:.0f} mm on shelf Z "
                f"{P['battery_shelf_z']:.0f} mm", "Scale: fit to sheet, axes in mm")
    frame(fig)
    save(fig, "13_exploded_body.png")


def sheet_14():
    body_frame = T(0, 0, 0)
    matrix = LAY.print_inverse("head_drive")
    fig = plt.figure(figsize=(16.5, 12))
    ax = fig.add_axes([.09, .15, .58, .72], projection="3d")
    items = []
    if have("head_drive"):
        mesh = placed("head_drive", matrix)
        centers = mesh.triangles_center
        colors = np.tile(np.asarray(matplotlib.colors.to_rgb(PART_COLOR["head_drive"])),
                         (len(centers), 1))
        colors[centers[:, 2] < HEAD["hd_base_bot"]] = matplotlib.colors.to_rgb("#8E4F8F")
        items.append((mesh, colors, "head_drive"))
    items += head_drive_items(body_frame, explode=(0, -60, -90))
    items += _head_drive_hardware(body_frame, {"hinge": (-120, 0, 0), "tension": (0, 0, 70),
                                               "spring": (0, 0, -70), "thumbnut": (0, 0, -120),
                                               "stop": (0, 0, 60)})
    items.append((prim_box((P["head_slot"][1], P["head_slot"][0], P["body_top_plate_t"]),
                           (0, -P["head_wheel_r"], 60)), PART_COLOR["body_upper"],
                  "Top plate slot"))
    draw_meshes(ax, items)
    lo, hi = items_bounds(items, pad=.08)
    setup_3d(ax, (lo, hi), elev=20, azim=-62, tick_step=50)
    tx, ty = HEAD["hd_tension_xy"]
    entries = [((0, -P["head_wheel_r"], 60), f"Body top plate slot\n{P['head_slot'][0]:.0f} x "
                                             f"{P['head_slot'][1]:.0f} mm", "R"),
               ((0, HEAD["hd_hinge_y"], HEAD["hd_base_top"]),
                "Printed base, bolts up to\nthe top plate on four M4 inserts", "L"),
               ((0, HEAD["hd_hinge_y"] - 30, HEAD["hd_base_bot"] - 12),
                "Printed arm, pivots on\nthe hinge bolt", "L"),
               ((0, HEAD["hd_motor_y"] + HEAD["hd_hinge_y"] - 60, HEAD["hd_hinge_z"] - 90),
                "TT motor 3777\nfour M3 screws into the arm", "L"),
               ((0, -P["head_wheel_r"] - 60, HEAD["hd_hinge_z"] - 90),
                "Wheel 3766 press fit\non the D-shaft", "R"),
               ((-120 - 31, HEAD["hd_hinge_y"], HEAD["hd_hinge_z"]),
                f"M{int(P['head_drive_hinge_m'])} hinge bolt\nthrough both base lugs", "L"),
               ((tx, ty, -P["body_top_plate_t"] + 70),
                f"M{int(P['head_drive_tension_m'])} x 40 tension screw", "R"),
               ((tx, ty, -P["body_top_plate_t"] - 8 - HEAD["hd_spring_free"] / 2 - 70),
                f"Spring OD {HEAD['hd_spring_od']:.0f} mm\nfree length "
                f"{HEAD['hd_spring_free']:.0f} mm", "R"),
               ((tx, ty, -P["body_top_plate_t"] - 40 + 4 - 120),
                "Thumb nut\nsets the tyre squeeze", "R"),
               ((HEAD["hd_stop_xy"][0], HEAD["hd_stop_xy"][1], -P["body_top_plate_t"] + 60),
                "Stop screw\nlimits the lift", "L")]
    callouts(fig, ax, entries, left_x=.026, right_x=.700, top=.83, bottom=.20, fontsize=8.8)
    legend(fig, [("Printed base", PART_COLOR["head_drive"]), ("Printed arm", "#8E4F8F"),
                 ("TT motor 3777", MOTOR), ("Wheel 3766", WHEEL), ("Spring", SPRING),
                 ("Steel fasteners", STEEL), ("Body top plate slot", PART_COLOR["body_upper"])],
           position=(.765, .55), title_text=None)
    heading(fig, "fable-r2d2 / head drive exploded",
            "The base and arm print as one piece joined by 0.8 mm breakaway webs; snap them apart "
            "and rebuild the hinge on the M4 bolt")
    footer(fig, "Head-drive native frame: Z = 0 is the top face of the body top plate, -Y is the "
                "rear of the droid.")
    title_block(fig, "14", "Head drive exploded / tension train",
                "head_drive + motor, wheel, hinge bolt, tension screw, spring, thumb nut",
                f"Wheel R{P['head_wheel_r']:.0f} mm, squeeze {HEAD['hd_squeeze']:.1f} mm",
                "Scale: fit to sheet, axes in mm")
    frame(fig)
    save(fig, "14_exploded_head_drive.png")


def _dome_electronics(out):
    """Display, jewel and LED envelopes pushed `out` mm radially out of their openings."""
    items = []
    tft = P["dome_eye_lcd_pcb"]
    tft_size = (tft[0], tft[2], tft[1])
    items.append((prim_box(tft_size, (0, 0, 0),
                           dome_mount(P["dome_eye_angle"], P["dome_eye_z"], tft_size)
                           @ T(0, out, 0)), TFT, "Round TFT"))
    mat = P["dome_matrix_pcb"]
    mat_size = (mat[0], mat[2], mat[1])
    for z in P["dome_fld_z"]:
        items.append((prim_box(mat_size, (0, 0, 0),
                               dome_mount(P["dome_fld_angle"], z, mat_size) @ T(0, out, 0)),
                      BOARD, "8x8 matrix"))
    for offset in (-11, 11):
        items.append((prim_box(mat_size, (0, 0, 0),
                               dome_mount(P["dome_rld_angle"] + offset, P["dome_rld_z"], mat_size)
                               @ T(0, out, 0)), BOARD, "8x8 matrix"))
    for angle, z, _ in (P["dome_front_psi"], P["dome_rear_psi"]):
        items.append((prim_cyl(23, 3, (0, 0, 0), axis="y",
                               matrix=dome_mount(angle, z, (23, 3, 23)) @ T(0, out, 0)),
                      JEWEL, "NeoPixel jewel"))
    for angle, z in ((P["dome_hp1"][0], P["dome_hp1"][1]), (P["dome_hp2"][0], P["dome_hp2"][1])):
        items.append((prim_cyl(12, 5, (0, 0, 0), axis="y",
                               matrix=dome_mount(angle, z, (12, 5, 12)) @ T(0, out, 0)),
                      LEDC, "HP LED"))
    items.append((prim_cyl(12, 5, (0, 0, 0), axis="y",
                           matrix=dome_mount(P["dome_hp3_angle"], 150,
                                             (12, 5, 12), radius=P["dome_hp3_r"]) @ T(0, out, 0)),
                  LEDC, "HP LED"))
    return items


def sheet_15():
    fig = plt.figure(figsize=(17, 12.5))
    lift = 150
    stack = []
    if have("dome"):
        stack.append((placed("dome", T(0, 0, lift)), PART_COLOR["dome"], "dome"))
    stack.append((prim_ring(P["susan_od"], P["susan_id"], P["susan_t"], (0, 0, 40)), SUSAN,
                  "Lazy susan"))
    stack.append((prim_cyl(P["slip_ring_d"], P["slip_ring_l"], (0, 0, -25)), SLIPRING, "Slip ring"))
    for angle in P["susan_hole_angles"]:
        a = math.radians(angle)
        stack.append((bolt_mesh(P["susan_screw_m"], 18,
                                (P["susan_hole_r"] * math.sin(a), P["susan_hole_r"] * math.cos(a),
                                 105), axis="z", sign=-1), STEEL, "M5 top-race screw"))
    ax = fig.add_axes([.120, .155, .30, .66], projection="3d")
    draw_meshes(ax, stack)
    lo, hi = items_bounds(stack, pad=.04)
    setup_3d(ax, (lo, hi), elev=14, azim=-62, tick_step=100, zoom=1.1)
    ax.set_title("Dome, ring bearing and slip ring", fontsize=11, pad=4)
    stack_entries = [((0, 0, lift + P["dome_height"] * .55), "Dome, one printed piece"),
                     ((0, 0, 40 + P["susan_t"] / 2),
                      "Lazy susan %.1f / %.1f x %.1f mm\ncarries the dome on the body top plate"
                      % (P["susan_od"], P["susan_id"], P["susan_t"])),
                     ((P["susan_hole_r"] * .71, P["susan_hole_r"] * .71, 105),
                      "4 x M%d top-race screws\nthrough the dome plate"
                      % P["susan_screw_m"]),
                     ((0, 0, -25), "Slip ring dia %.1f x %.1f mm\n12 wires into the dome"
                      % (P["slip_ring_d"], P["slip_ring_l"]))]
    side_callouts(fig, ax, stack_entries, .006, .760, .230, fontsize=8.4)
    out = 95
    top_items = ([(stl("dome", process=True), PART_COLOR["dome"], "dome")] if have("dome") else [])
    top_items += _dome_electronics(out)
    top = fig.add_axes([.600, .195, .315, .56])
    draw_meshes(top, top_items, edges=True)
    span = P["dome_r"] + out + 40
    setup_ortho(top, "top", (-span, span), (-span, span),
                "Top view / displays pulled radially out")
    def feature(angle, z, radius=None):
        base = (dome_radius(z) if radius is None else radius)
        return dome_point(angle, z, radius=base + out)
    top_entries = [(feature(P["dome_eye_angle"], P["dome_eye_z"]),
                    "Round TFT %.1f x %.1f mm\nbehind the radar eye lens"
                    % (P["dome_eye_lcd_pcb"][0], P["dome_eye_lcd_pcb"][1])),
                   (feature(P["dome_fld_angle"], P["dome_fld_z"][1]),
                    "Front logic matrices\ntwo 8x8 I2C backpacks"),
                   (feature(P["dome_rld_angle"], P["dome_rld_z"]),
                    "Rear logic matrices\ntwo 8x8 I2C backpacks"),
                   (feature(P["dome_front_psi"][0], P["dome_front_psi"][1]),
                    "PSI NeoPixel jewels\n23 mm, front and rear"),
                   (feature(P["dome_hp1"][0], P["dome_hp1"][1]),
                    "Holoprojector NeoPixels\nthree per dome")]
    side_callouts(fig, top, top_entries, .472, .740, .250, fontsize=8.4)
    heading(fig, "fable-r2d2 / dome exploded",
            "Dome, ring bearing, slip ring and every display envelope pulled out of the openings "
            "modelled in the STL")
    footer(fig, "Display envelopes are nominal board outlines; they mount to the internal dome "
                "plate on heat-set inserts. Blue-green = matrices, cyan = PSI jewels, "
                "green = holoprojector LEDs.")
    title_block(fig, "15", "Dome exploded / bearing, slip ring and displays",
                "dome + lazy susan, slip ring, TFT, matrices, jewels, HP LEDs",
                "Susan %.1f / %.1f x %.1f mm" % (P["susan_od"], P["susan_id"], P["susan_t"]),
                "Scale: per panel, axes in mm")
    frame(fig)
    save(fig, "15_exploded_dome.png")


TABLE = [("1", "dome", "1", "PETG", "printed"),
         ("2", "body_upper", "1", "PETG", "printed"),
         ("3", "body_lower", "1", "PETG", "printed"),
         ("4", "leg_upper", "2", "PETG", "mirrored"),
         ("5", "leg_lower", "2", "PETG", "mirrored"),
         ("6", "foot_outer", "2", "PETG", "mirrored"),
         ("7", "leg_center", "1", "PETG", "printed"),
         ("8", "foot_center", "1", "PETG", "printed"),
         ("9", "head_drive", "1", "PETG", "printed"),
         ("10", "Battery 12 V 7 Ah", "1", "bought", "151x94x65"),
         ("11", "TT motor 3777", "7", "bought", "70x22x19"),
         ("12", "Wheel 3766", "14", "bought", "63x29"),
         ("13", "Lazy susan bearing", "1", "bought", "228.6 dia"),
         ("14", "Slip ring 1195", "1", "bought", "12.5 dia")]


def sheet_16():
    tall = {"dome": (0, 0, 640), "body_upper": (0, 0, 430), "body_lower": (0, 0, 250),
            "head_drive": (0, -120, 330),
            "leg_upper_right": (120, 0, 190), "leg_upper_left": (-120, 0, 190),
            "leg_lower_right": (150, 40, 90), "leg_lower_left": (-150, 40, 90),
            "foot_outer_right": (170, 80, 0), "foot_outer_left": (-170, 80, 0),
            "leg_center": (0, 120, 120), "foot_center": (0, 170, 0)}
    items = printed_items(finish=False, explode=tall) + drive_items(tall) + body_hardware(tall)
    items += head_drive_items(LAY.at_head_drive(), tall["head_drive"])
    fig = plt.figure(figsize=(18, 13.5))
    ax = fig.add_axes([.045, .13, .52, .75], projection="3d")
    draw_meshes(ax, items)
    lo, hi = items_bounds(items, pad=.03)
    setup_3d(ax, ([lo[0], lo[1], 0], [hi[0], hi[1], hi[2]]), elev=16, azim=-62, tick_step=200,
             zoom=1.08)
    fig.canvas.draw()
    names = {"1": "dome", "2": "body_upper", "3": "body_lower", "4": "leg_upper_right",
             "5": "leg_lower_right", "6": "foot_outer_right", "7": "leg_center",
             "8": "foot_center", "9": "head_drive", "10": "Battery 12 V 7 Ah",
             "11": "TT motor", "12": "Wheel", "13": "Lazy susan", "14": "Slip ring"}
    left = ["4", "5", "6", "7", "8"]
    right = ["1", "2", "3", "9", "13", "14", "10", "11", "12"]
    for group, x, top, bottom in ((left, .050, .84, .30), (right, .600, .87, .30)):
        rows = []
        for number in group:
            point = anchor_of(items, names[number], 16, -62)
            if point is not None:
                rows.append((number, point))
        rows.sort(key=lambda row: -project_figure(fig, ax, row[1])[1])
        step = (top - bottom) / max(len(rows) - 1, 1)
        for index, (number, point) in enumerate(rows):
            balloon(fig, ax, point, number, (x, top - index * step))
    x0, y0 = .655, .150
    widths = [.028, .132, .028, .056, .066]
    headers = ["No", "Part", "Qty", "Material", "Size / note"]
    rows = len(TABLE) + 1
    row_h = .0325
    top = y0 + rows * row_h
    fig.add_artist(Rectangle((x0, y0), sum(widths), rows * row_h, transform=fig.transFigure,
                             facecolor="white", edgecolor="#63788C", linewidth=1.0, zorder=5))
    fig.add_artist(Line2D([x0, x0 + sum(widths)], [top - row_h] * 2, transform=fig.transFigure,
                          color="#63788C", linewidth=.9, zorder=6))
    cursor = x0
    for width in widths[:-1]:
        cursor += width
        fig.add_artist(Line2D([cursor] * 2, [y0, top], transform=fig.transFigure,
                              color="#AFBCC7", linewidth=.6, zorder=6))
    for index, header in enumerate(headers):
        fig.text(x0 + sum(widths[:index]) + .005, top - row_h / 2, header, fontsize=8.6,
                 color="#1B2733", va="center", zorder=6)
    for row, entry in enumerate(TABLE):
        y = top - row_h * (row + 1.5)
        for index, value in enumerate(entry):
            fig.text(x0 + sum(widths[:index]) + .005, y, value, fontsize=8.0, color=INK,
                     va="center", zorder=6)
    fig.text(x0, top + .011, "Parts table", fontsize=11, color=INK)
    true_lo, true_hi = items_bounds(printed_items(finish=True) + drive_items(), pad=0)
    heading(fig, "fable-r2d2 / complete exploded robot",
            "Every printed piece and the major purchased items, exploded vertically | Balloon "
            "numbers match the parts table on the right")
    footer(fig, "Twelve printed pieces from nine STL designs; purchased quantities are the totals "
                "for one robot.")
    title_block(fig, "16", "Complete exploded robot / balloons and parts table",
                "all printed and major purchased items",
                "Assembled height %.1f mm, track %.1f mm" % (true_hi[2], P["leg_track"]),
                "Scale: fit to sheet, axes in mm")
    frame(fig)
    save(fig, "16_exploded_robot.png")


def component_sheets():
    for index, name in enumerate(ORDER):
        if not have(name):
            print(f"SKIP components/{name}.png (STL missing)", flush=True)
            continue
        mesh = stl(name, process=True)
        lo, hi = mesh.bounds
        extents = mesh.extents
        row = PARTS[name]
        fig = plt.figure(figsize=(13, 10))
        iso = fig.add_axes([.040, .55, .355, .33], projection="3d")
        draw_meshes(iso, [(mesh, PART_COLOR[name], name)], edges=True)
        pad = np.maximum(extents * .09, 2)
        setup_3d(iso, [lo - pad, hi + pad], elev=26, azim=-56, tick_step=None, zoom=1.12)
        iso.set_title("Isometric", fontsize=11, pad=2)
        specs = [("front", [.530, .55, .40, .33]), ("right", [.055, .20, .40, .28]),
                 ("top", [.530, .20, .40, .28])]
        margin = np.maximum(extents * .08, 3)
        for view, rect in specs:
            ax = fig.add_axes(rect)
            draw_meshes(ax, [(mesh, PART_COLOR[name], name)], edges=True)
            spec = ORTHO[view]
            h, v = spec[0], spec[1]
            setup_ortho(ax, view, (lo[h] - margin[h], hi[h] + margin[h]),
                        (lo[v] - margin[v], hi[v] + margin[v]))
            if view == "front":
                dimension(ax, (-(lo[0] - margin[0] * .55), lo[2]), (-(lo[0] - margin[0] * .55), hi[2]),
                          f"{extents[2]:.1f} mm", rotation=90, fontsize=9)
                dimension(ax, (-lo[0], hi[2] + margin[2] * .55), (-hi[0], hi[2] + margin[2] * .55),
                          f"{extents[0]:.1f} mm", fontsize=9)
            if view == "top":
                dimension(ax, (lo[0], hi[1] + margin[1] * .55), (hi[0], hi[1] + margin[1] * .55),
                          f"{extents[0]:.1f} mm", fontsize=9)
                dimension(ax, (hi[0] + margin[0] * .55, lo[1]), (hi[0] + margin[0] * .55, hi[1]),
                          f"{extents[1]:.1f} mm", rotation=90, fontsize=9)
        mirror = "  |  mirror in the slicer for the second piece" if row["mirror"] else ""
        heading(fig, f"fable-r2d2 / {TITLES[name]}  ({name}.stl)",
                f"Quantity {row['quantity']}  |  {row['material']}  |  {row['orientation']}{mirror}")
        footer(fig, row["notes"])
        title_block(fig, f"{index + 1:02d}", f"{TITLES[name]} / component drawing", name + ".stl",
                    f"{extents[0]:.1f} x {extents[1]:.1f} x {extents[2]:.1f} mm",
                    "Scale: per panel, axes in mm")
        frame(fig)
        save(fig, f"components/{name}.png")


SHEETS = {"01": sheet_01, "02": sheet_02, "03": sheet_03, "04": sheet_04, "05": sheet_05,
          "06": sheet_06, "07": sheet_07, "08": sheet_08, "09": sheet_09, "10": sheet_10,
          "11": sheet_11, "12": sheet_12, "13": sheet_13, "14": sheet_14, "15": sheet_15,
          "16": sheet_16, "components": component_sheets}


def write_manifest(generated):
    pngs = sorted(OUT.glob("*.png")) + sorted((OUT / "components").glob("*.png"))
    records = []
    for path in pngs:
        with Image.open(path) as png:
            assert png.format == "PNG" and png.width >= 1800, (path, png.size)
            records.append({"file": str(path.relative_to(ROOT)).replace("\\", "/"),
                            "pixels": list(png.size), "sha256": digest(path)})
    manifest = {
        "style": "MATLAB-style engineering drawings rendered with Matplotlib and a per-pixel "
                 "depth buffer; white background, MATLAB colour order, millimetre axes",
        "generated": generated,
        "units": "mm",
        "dpi": DPI,
        "printed_designs": len(PARTS),
        "printed_pieces": sum(int(row["quantity"]) for row in PARTS.values()),
        "purchased_parts": "nominal envelopes from cad/params.scad; not manufacturer CAD",
        "missing_stl": MISSING,
        "sources": {f"stl/{name}.stl": digest(ROOT / f"stl/{name}.stl")
                    for name in ORDER if have(name)},
        "pngs": records}
    path = OUT / "drawing-manifest.json"
    path.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
    print(f"JSON {path.relative_to(ROOT)}  {len(records)} PNG entries", flush=True)
    archive = OUT / "r2d2-matlab-style-drawings.zip"
    with zipfile.ZipFile(archive, "w", compression=zipfile.ZIP_DEFLATED) as package:
        for png in pngs:
            package.write(png, str(png.relative_to(OUT)).replace("\\", "/"))
        package.write(path, "drawing-manifest.json")
    with zipfile.ZipFile(archive) as package:
        assert package.testzip() is None
        count = len(package.namelist())
    print(f"ZIP  {archive.relative_to(ROOT)}  {count} entries", flush=True)
    return records


def main():
    global ARGS, MISSING
    parser = argparse.ArgumentParser()
    parser.add_argument("--allow-missing", action="store_true",
                        help="skip STL files that are not exported yet (development only)")
    parser.add_argument("--date", default=None, help="ISO date recorded in the manifest")
    parser.add_argument("--only", default="", help="comma separated sheet keys, e.g. 01,05")
    ARGS = parser.parse_args()
    MISSING = [name for name in ORDER if not have(name)]
    if MISSING:
        if not ARGS.allow_missing:
            print("ERROR missing STL files: " + ", ".join(MISSING), flush=True)
            print("Export them, or re-run with --allow-missing for a development set.", flush=True)
            return 1
        bar = "!" * 78
        print(bar, flush=True)
        print("!! WARNING --allow-missing: " + ", ".join(MISSING)
              + " are NOT in this drawing set.", flush=True)
        print("!! This is a DEVELOPMENT run. The delivered set must be produced without the "
              "flag.", flush=True)
        print(bar, flush=True)
    OUT.mkdir(parents=True, exist_ok=True)
    keys = [k for k in ARGS.only.split(",") if k] or list(SHEETS)
    for key in keys:
        SHEETS[key]()
    if ARGS.only:
        print("Partial run; manifest not rewritten.", flush=True)
        return 0
    generated = ARGS.date or datetime.now(timezone.utc).replace(microsecond=0).isoformat()
    records = write_manifest(generated)
    print(f"PASS {len(records)} PNG drawings, manifest and ZIP written to "
          f"{OUT.relative_to(ROOT)}", flush=True)
    return 0


if __name__ == "__main__":
    sys.exit(main())
