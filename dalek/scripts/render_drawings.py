"""Render MATLAB-style PNG engineering views of the unchanged ROUND-9 STL set.

Uses the installed Matplotlib/trimesh tools. No MATLAB licence or CAD edit is needed.
Run from any directory: python C:/dev/robots/dalek/scripts/render_drawings.py
"""
from pathlib import Path
import csv
import hashlib
import json
import zipfile

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.lines import Line2D
from mpl_toolkits.mplot3d import proj3d
from PIL import Image
import numpy as np
import trimesh

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'output/drawings'
DPI = 180
NAMES = ['01_base', '02_skirt', '04_shoulder', '05_neck',
         '06_head', '07_pitch_carrier', '08_plunger_arm', '09_emitter_arm', '10_head_motor_carriage']
LABELS = ['Motor base', 'One-piece skirt', 'Shoulder', 'Neck',
          'Integrated head', 'Pitch carrier', 'Plunger arm', 'Emitter arm', 'Head motor carriage']
# MATLAB default colour-order family; the merged skirt retains the cyan lower-skirt colour.
COLORS = np.array([[0, .447, .741], [.301, .745, .933],
                   [.494, .184, .556], [.45, .48, .52], [.929, .694, .125],
                   [.10, .63, .57], [.85, .325, .098], [.635, .078, .184], [.28, .49, .80]])
FINISH = np.array([[.24, .24, .22], [.65, .46, .25],
                   [.65, .46, .25], [.41, .42, .40], [.76, .57, .31],
                   [.35, .38, .40], [.69, .70, .70], [.69, .70, .70], [.41, .42, .40]])
GRAY = np.array([.62, .65, .69])
ARM_ROTATION = np.array([[0, 0, -1], [-1, 0, 0], [0, 1, 0]], dtype=float)
BASE_Z, SHOULDER_Z, NECK_Z, HEAD_Z, HEIGHT = 13.8, 277.8, 397.8, 449.8, 563.8
BOARD_LAYOUT = [
    ('Buffer prototype', (-35, -93), (81, 51, 1.6)),
    ('Divider prototype', (-35, 93), (81, 51, 1.6)),
    ('U10 PCA9685', (40, -80), (62.5, 25.4, 3)),
    ('U5 left DRV8833', (65, -106), (26, 18, 3)),
    ('U2 motor regulator', (26, -107), (25.4, 25.4, 9.5)),
    ('U3 servo regulator', (24, 81), (25.4, 25.4, 9.5)),
    ('U6 right DRV8833', (62, 78), (26, 18, 3)),
    ('U11 head DRV8833', (62, 104), (26, 18, 3)),
    ('U7 amplifier', (23, 107), (19.4, 17.8, 3)),
    ('U4 logic regulator', (41, 105), (10.16, 17.145, 3)),
]
LIGHT = np.array([-.3, -.6, 1.0]); LIGHT /= np.linalg.norm(LIGHT)
plt.rcParams.update({'font.family': 'Arial', 'font.size': 10, 'axes.titlesize': 12,
                     'axes.labelsize': 10, 'axes.edgecolor': '#646970',
                     'axes.linewidth': .6, 'xtick.color': '#555b63', 'ytick.color': '#555b63',
                     'figure.facecolor': 'white', 'savefig.facecolor': 'white',
                     'grid.color': '#d9dde2', 'grid.linewidth': .45})


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def moved(mesh, translation=(0, 0, 0), rotation=None, print_offset=(0, 0, 0)):
    result = mesh.copy()
    vertices = result.vertices - np.array(print_offset)
    if rotation is not None:
        vertices = vertices @ np.asarray(rotation).T
    result.vertices = vertices + np.asarray(translation)
    return result


def box(minimum, size):
    return trimesh.creation.box(extents=size,
        transform=trimesh.transformations.translation_matrix(np.array(minimum) + np.array(size)/2))


def cylinder(center, diameter, length, axis='z'):
    mesh = trimesh.creation.cylinder(radius=diameter/2, height=length, sections=48)
    rotation = {'z': np.eye(3), 'x': np.array([[0, 0, 1], [0, 1, 0], [-1, 0, 0]]),
                'y': np.array([[1, 0, 0], [0, 0, -1], [0, 1, 0]])}[axis]
    return moved(mesh, center, rotation)


def scene(meshes, gap=0, spread=False, bronze=False):
    items = []
    palette = FINISH if bronze else COLORS
    for i, height in enumerate([BASE_Z, 67.8, SHOULDER_Z, NECK_Z, HEAD_Z]):
        color = palette[i]
        if bronze and i == 1:
            centers = meshes[NAMES[i]].triangles_center
            color = np.tile(color, (len(centers), 1)); color[centers[:, 2] >= 110] = [.69, .50, .28]
        if bronze and i == 3:
            centers = meshes[NAMES[i]].triangles_center
            radius = np.linalg.norm(centers[:, :2], axis=1)
            liner = (radius >= 95.8) & (radius <= 98) & (centers[:, 2] >= 5) & (centers[:, 2] <= 52)
            color = np.tile(color, (len(centers), 1)); color[liner] = [.10, .11, .10]
        if bronze and i == 4:
            centers = meshes[NAMES[i]].triangles_center
            eye = (centers[:, 1] < -110.1) & (np.abs(centers[:, 0]) < 20) & (np.abs(centers[:, 2]-63) < 20)
            radius = np.linalg.norm(centers[:, [0, 2]]-np.array([0, 63]), axis=1)
            discs = eye & (centers[:, 1] < -115) & (centers[:, 1] > -152) & (radius > 8)
            lens = eye & (centers[:, 1] < -174.5)
            color = np.tile(color, (len(centers), 1))
            color[eye] = [.14, .16, .17]; color[discs] = [.74, .76, .73]; color[lens] = [.16, .43, .64]
            drum_radius = np.linalg.norm(centers[:, :2], axis=1)
            drum = (drum_radius >= 98.4) & (drum_radius <= 99.1) & (centers[:, 2] <= 43)
            color[drum] = [.13, .14, .13]
        items.append((moved(meshes[NAMES[i]], (0, 0, height+i*gap)), color))
    for side, x in [(-1, -47), (1, 53)]:
        dx = side*60 if spread else 0
        dy = -40 if spread else 0
        items.append((moved(meshes['07_pitch_carrier'], (x+dx, -94+dy, SHOULDER_Z+42+2*gap)), palette[5]))
    for i, x in [(6, -50), (7, 50)]:
        dx = (-60 if i == 6 else 60) if spread else 0
        dy = -100 if spread else 0
        color = palette[i]
        if bronze:
            center = meshes[NAMES[i]].triangles_center - np.array([0, 0, 28])
            cap = (center[:, 0] >= 12) & (center[:, 0] <= 29) & (np.linalg.norm(center, axis=1) >= 25)
            color = np.tile(color, (len(center), 1)); color[cap] = [.19, .20, .19]
            if i == 6: color[center[:, 0] >= 104] = [.13, .14, .13]
        items.append((moved(meshes[NAMES[i]], (x+dx, -94+dy, SHOULDER_Z+77+2*gap),
                            ARM_ROTATION, (0, 0, 28)), color))
    items.append((moved(meshes['10_head_motor_carriage'], (64.5+(90 if spread else 0), 0, NECK_Z+29.2+3*gap)), palette[8]))
    return items


def hardware(gap=0, internals=True):
    items = []
    for sx in [-1, 1]:
        for sy in [-1, 1]:
            items.append((cylinder((sx*98, sy*58, 31.5), 63, 29, 'x'), np.array([.25, .27, .30])))
            if internals:
                motor = box((-11.2, -57, 0), (22.4, 70, 22.44))
                items.append((moved(motor, (sx*70.5, sy*58, BASE_Z+6), np.diag([sx, sy, 1])), GRAY))
    if internals:
        items.append((box((-35, -57, BASE_Z+6), (70, 114, 76)), GRAY))
        for y in [-121, 65]:
            items.append((box((-80, y, BASE_Z+34), (160, 56, 2)), np.array([.32, .47, .34])))
        for x in [-54, 54]:
            for y in [-93, -69, 69, 93]:
                items.append((cylinder((x, y, BASE_Z+21.5), 7, 25), GRAY))
        for ref, (x, y), (width, depth, height) in BOARD_LAYOUT:
            items.append((box((x-width/2, y-depth/2, BASE_Z+42), (width, depth, height)),
                          np.array([.20, .42, .52]) if 'prototype' not in ref else np.array([.74, .72, .53])))
        items.append((box((-38.9, -20, 281.9+2*gap), (77.8, 2, 77.8)), GRAY))
        items.append((cylinder((0, -7.25, 320.8+2*gap), 68, 25.5, 'y'), np.array([.18, .20, .22])))
    items.append((box((-25.76, 108, 329.8+2*gap), (51.52, 2, 25.04)), GRAY))
    items.append((box((-13, 114, 335.8+2*gap), (26, 1, 15)), np.array([.25, .75, .90])))
    if internals:
        for x in [-47, 53]:
            items.append((box((x-12, -100, SHOULDER_Z+8+2*gap), (24, 12, 31)), GRAY))
            items.append((box((x+4, -100, SHOULDER_Z+55+2*gap), (27, 12, 36)), GRAY))
        items.append((box((52.8, -57, NECK_Z+32.3+3*gap), (22.44, 70, 22.4)), np.array([.929, .694, .125])))
        items.append((cylinder((64.5, 0, NECK_Z+71+3*gap), 63, 29), np.array([.85, .325, .098])))
    return items


def shaded(mesh, color):
    amount = .53 + .47*np.maximum(mesh.face_normals @ LIGHT, 0)
    base = np.asarray(color)
    return np.clip((base[None, :] if base.ndim == 1 else base)*amount[:, None], 0, 1)


def draw_meshes(ax, items, edges=True):
    # Matplotlib's mean-depth painter ordering is insufficient for long triangles in
    # hollow STL shells. Save the geometry for a true per-pixel depth buffer at export.
    ax._drawing_items = items
    ax._drawing_edges = edges


def rasterize(ax, dpi):
    items = ax._drawing_items
    triangles = np.concatenate([mesh.triangles for mesh, _ in items])
    facecolors = np.concatenate([shaded(mesh, color) for mesh, color in items])
    ratio = dpi/ax.figure.dpi
    width = max(1, int(np.ceil(ax.bbox.width*ratio)))
    height = max(1, int(np.ceil(ax.bbox.height*ratio)))
    depth_buffer = np.full((height, width), -np.inf, dtype=np.float32)
    rgba = np.zeros((height, width, 4), dtype=np.uint8)

    def project(points):
        shape = points.shape
        flat = points.reshape(-1, 3)
        if hasattr(ax, '_ortho_spec'):
            horizontal, vertical, depth, near_sign, xsign = ax._ortho_spec
            xy = flat[:, [horizontal, vertical]].copy(); xy[:, 0] *= xsign
            values = flat[:, depth]*near_sign
        else:
            projected = np.c_[flat, np.ones(len(flat))] @ ax.get_proj().T
            xy = projected[:, :2]/projected[:, 3, None]
            azimuth, elevation = np.deg2rad([ax.azim, ax.elev])
            camera = np.array([np.cos(elevation)*np.cos(azimuth),
                               np.cos(elevation)*np.sin(azimuth), np.sin(elevation)])
            values = flat @ camera
        pixels = (ax.transData.transform(xy)-ax.bbox.p0)*ratio
        return pixels.reshape(*shape[:-1], 2), values.reshape(shape[:-1])

    pixels, values = project(triangles)
    for triangle, z, color in zip(pixels, values, facecolors):
        x0 = max(0, int(np.floor(triangle[:, 0].min())))
        x1 = min(width-1, int(np.ceil(triangle[:, 0].max())))
        y0 = max(0, int(np.floor(triangle[:, 1].min())))
        y1 = min(height-1, int(np.ceil(triangle[:, 1].max())))
        if x1 < x0 or y1 < y0:
            continue
        (ax0, ay0), (bx, by), (cx, cy) = triangle
        denominator = (by-cy)*(ax0-cx)+(cx-bx)*(ay0-cy)
        if abs(denominator) < 1e-8:
            continue
        xx = np.arange(x0, x1+1)[None, :]+.5
        yy = np.arange(y0, y1+1)[:, None]+.5
        first = ((by-cy)*(xx-cx)+(cx-bx)*(yy-cy))/denominator
        second = ((cy-ay0)*(xx-cx)+(ax0-cx)*(yy-cy))/denominator
        third = 1-first-second
        incoming = first*z[0]+second*z[1]+third*z[2]
        region = depth_buffer[y0:y1+1, x0:x1+1]
        mask = (first >= -1e-7) & (second >= -1e-7) & (third >= -1e-7) & (incoming > region)
        region[mask] = incoming[mask]
        rgba[y0:y1+1, x0:x1+1][mask] = np.r_[np.rint(color*255).astype(np.uint8), 255]
    if ax._drawing_edges:
        for mesh, _ in items:
            hard = mesh.face_adjacency_angles > np.deg2rad(32)
            segments = mesh.vertices[mesh.face_adjacency_edges[hard]]
            endpoints, distances = project(segments)
            for segment, z in zip(endpoints, distances):
                count = max(2, int(np.linalg.norm(segment[1]-segment[0])*1.4))
                fraction = np.linspace(0, 1, count)
                points = np.rint(segment[0]+fraction[:, None]*(segment[1]-segment[0])).astype(int)
                depths = z[0]+fraction*(z[1]-z[0])
                valid = (points[:, 0] >= 0) & (points[:, 0] < width) & (points[:, 1] >= 0) & (points[:, 1] < height)
                points, depths = points[valid], depths[valid]
                x, y = points[:, 0], points[:, 1]
                visible = (rgba[y, x, 3] > 0) & (depths >= depth_buffer[y, x]-.15)
                x, y = x[visible], y[visible]
                rgba[y, x, :3] = (rgba[y, x, :3]*.65).astype(np.uint8)
    return rgba


def setup_3d(ax, bounds, elev=24, azim=-56, tick_step=None):
    lower, upper = np.asarray(bounds)
    span = upper-lower
    ax.set_xlim(lower[0], upper[0]); ax.set_ylim(lower[1], upper[1]); ax.set_zlim(lower[2], upper[2])
    ax.set_box_aspect(span)
    ax.set_proj_type('ortho')
    ax.view_init(elev=elev, azim=azim)
    for axis in [ax.xaxis, ax.yaxis, ax.zaxis]:
        axis.set_pane_color((.965, .973, .98, .55))
        axis._axinfo['grid'].update(color=(.78, .80, .83, .6), linewidth=.45)
    ax.set_xlabel('X (mm)', labelpad=9); ax.set_ylabel('Y (mm)', labelpad=9)
    ax.set_zlabel('Z (mm)', labelpad=11)
    ax.tick_params(labelsize=8, pad=1)
    if tick_step:
        for setter, lo, hi in zip([ax.set_xticks, ax.set_yticks, ax.set_zticks], lower, upper):
            setter(np.arange(np.ceil(lo/tick_step)*tick_step, hi+1, tick_step))


def title(fig, heading, subtitle):
    fig.text(.05, .963, heading, fontsize=18, color='#202b36', ha='left')
    fig.text(.05, .934, subtitle, fontsize=10, color='#535e69', ha='left')


def footer(fig, text='Actual ROUND-9 STL geometry | Dimensions in mm | +Y is rear; -Y is front'):
    fig.text(.05, .035, text, fontsize=9, color='#626b74')


def callout(fig, ax, point, text, label_position, color='#334858'):
    if hasattr(ax, '_ortho_spec'):
        horizontal, vertical, _, _, xsign = ax._ortho_spec
        projected = (point[horizontal]*xsign, point[vertical])
    else:
        projected = proj3d.proj_transform(*point, ax.get_proj())[:2]
    start = fig.transFigure.inverted().transform(ax.transData.transform(projected))
    x, y = label_position
    finish_x = x-.007 if x > .5 else x+.14
    fig.add_artist(Line2D([start[0], finish_x], [start[1], y+.004],
                         transform=fig.transFigure, color=color, linewidth=.8))
    fig.add_artist(Line2D([start[0]], [start[1]], transform=fig.transFigure,
                         marker='o', markersize=2.5, color=color))
    fig.text(x, y, text, fontsize=10, color=color, ha='left', va='center',
             bbox={'facecolor': 'white', 'edgecolor': 'none', 'pad': 2})


def save(fig, path):
    path.parent.mkdir(parents=True, exist_ok=True)
    fig.canvas.draw()
    for ax in list(fig.axes):
        if not hasattr(ax, '_drawing_items'):
            continue
        rgba = rasterize(ax, DPI)
        overlay = fig.add_axes(ax.get_position(), zorder=1, frameon=False)
        overlay.imshow(rgba, extent=(0, 1, 0, 1), origin='lower', interpolation='nearest', aspect='auto')
        overlay.set_xlim(0, 1); overlay.set_ylim(0, 1); overlay.set_axis_off()
    fig.savefig(path, dpi=DPI)
    plt.close(fig)
    with Image.open(path) as check:
        check.verify()
    print('PNG '+str(path.relative_to(ROOT)), flush=True)


def robot_figures(meshes):
    for exploded in [False, True]:
        gap = 44 if exploded else 0
        fig = plt.figure(figsize=(14, 12))
        ax = fig.add_axes([.16, .09, .66, .81], projection='3d')
        items = scene(meshes, gap, spread=exploded, bronze=not exploded) + hardware(gap, internals=True)
        draw_meshes(ax, items, edges=False)
        bounds = [[-205, -370 if exploded else -270, 0], [215, 175, 765 if exploded else 590]]
        setup_3d(ax, bounds, elev=22, azim=-58, tick_step=100)
        title(fig, 'Dalek ROUND-9 / '+('exploded assembly' if exploded else 'assembled robot'),
              '9 printed designs / 10 printed pieces' +
              (' | Body separation 44 mm; hidden arms and carriage offset for clarity' if exploded
               else ' | Bronze finish | Nominal height 563.8 mm | Round base diameter 300 mm'))
        footer(fig, 'STL surfaces are exact | Gray purchased-part envelopes are illustrative | Orthographic 3D projection')
        fig.canvas.draw()
        labels = [((145, -80, 51.8), '01  Motor base', (.04, .18)),
                  ((105, -80, 157.8+gap), '02  One-piece skirt', (.82, .36)),
                  ((95, -45, 337.8+2*gap), '04  Shoulder', (.82, .59)),
                  ((-75, -60, 429.8+3*gap), '05  Neck', (.04, .75)),
                  ((60, -55, 524.8+4*gap), '06  Integrated head', (.82, .84))]
        for point, label, position in labels:
            callout(fig, ax, point, label, position)
        if exploded:
            for point, label, position in [((-107, -134, 411.8), '07  Hidden carriers x2', (.04, .64)),
                                           ((-110, -300, 442.8), '08  Plunger arm', (.04, .49)),
                                           ((110, -300, 442.8), '09  Emitter arm', (.82, .70)),
                                           ((154.5, -35, 568), '10  Head motor carriage', (.80, .77))]:
                callout(fig, ax, point, label, position)
        else:
            fig.text(.05, .08, 'Bronze finish shown. The exploded and component sheets use colours to identify individual parts.',
                     fontsize=10, color='#535e69')
        save(fig, OUT / ('02_robot_exploded.png' if exploded else '01_robot_assembled.png'))


def dimension(ax, p1, p2, label, offset=(0, 0), rotation=0):
    ax.annotate('', xy=p1, xytext=p2, arrowprops={'arrowstyle': '<->', 'color': '#263e50', 'lw': .8})
    middle = (np.array(p1)+np.array(p2))/2 + np.asarray(offset)
    ax.text(*middle, label, ha='center', va='center', rotation=rotation, fontsize=9,
            color='#263e50', bbox={'facecolor': 'white', 'edgecolor': 'none', 'pad': 1.5})


def orthographics(meshes):
    items = scene(meshes, bronze=True) + hardware()
    fig, axes = plt.subplots(2, 2, figsize=(15, 13))
    fig.subplots_adjust(left=.07, right=.96, bottom=.09, top=.88, wspace=.24, hspace=.22)
    specifications = [('Front / looking toward +Y', 0, 2, 1, -1, 1),
                      ('Right side / looking toward -X', 1, 2, 0, 1, 1),
                      ('Rear / looking toward -Y', 0, 2, 1, 1, -1),
                      ('Top / looking toward -Z', 0, 1, 2, 1, 1)]
    for ax, (caption, horizontal, vertical, depth, near_sign, xsign) in zip(axes.flat, specifications):
        draw_meshes(ax, items, edges=False)
        ax._ortho_spec = (horizontal, vertical, depth, near_sign, xsign)
        ax.set_aspect('equal'); ax.set_axisbelow(True); ax.grid(True)
        ax.set_title(caption, pad=8)
        ax.set_xlabel(('-' if xsign < 0 else '')+'XYZ'[horizontal]+' (mm)')
        ax.set_ylabel('XYZ'[vertical]+' (mm)')
        if vertical == 2:
            ax.set_xlim((-220, 200) if horizontal == 0 else (-285, 190)); ax.set_ylim(-18, 590)
        else:
            ax.set_xlim(-200, 210); ax.set_ylim(-280, 190)
    dimension(axes[0, 0], (-188, 0), (-188, HEIGHT), '563.8 mm', rotation=90)
    dimension(axes[1, 1], (-150, 166), (150, 166), 'Base diameter 300 mm')
    dimension(axes[1, 1], (181, -150), (181, 150), 'Base 300 mm', rotation=90)
    title(fig, 'Dalek ROUND-9 / orthographic drawings',
          'Projected from the same STL assembly | Axis units are millimetres | View directions are labelled')
    footer(fig, 'Assembled dimensions are nominal CAD values. Individual panels have their own axis limits.')
    save(fig, OUT / '03_robot_orthographic.png')


def component_figures(meshes, manifest):
    for index, name in enumerate(NAMES):
        mesh = meshes[name]
        bounds = mesh.bounds.copy()
        span = mesh.extents
        pad = np.maximum(span*.10, 2)
        fig = plt.figure(figsize=(12, 9))
        ax = fig.add_axes([.10, .12, .80, .76], projection='3d')
        draw_meshes(ax, [(mesh, COLORS[index])])
        setup_3d(ax, [bounds[0]-pad, bounds[1]+pad], elev=28, azim=-55)
        row = manifest[name]
        title(fig, f'{name[:2]} / {LABELS[index]}',
              f'Quantity {row["quantity"]} | {row["material"]} | STL extents '+
              ' x '.join(f'{v:.1f}' for v in span)+' mm')
        footer(fig, f'{name}.stl | Exported part coordinates | No mesh simplification or geometric scaling')
        save(fig, OUT / 'components' / (name+'.png'))
    fig = plt.figure(figsize=(18, 13))
    for i, name in enumerate(NAMES):
        mesh = meshes[name]
        ax = fig.add_subplot(2, 5, i+1, projection='3d')
        draw_meshes(ax, [(mesh, COLORS[i])])
        pad = np.maximum(mesh.extents*.12, 2)
        setup_3d(ax, [mesh.bounds[0]-pad, mesh.bounds[1]+pad], elev=28, azim=-55)
        ax.set_axis_off()
        row = manifest[name]
        ax.set_title(f'{name[:2]}  {LABELS[i]}\nQty {row["quantity"]} / {row["material"]}', fontsize=11, pad=2)
        ax.text2D(.5, -.03, ' x '.join(f'{v:.1f}' for v in mesh.extents)+' mm',
                  transform=ax.transAxes, ha='center', fontsize=9, color='#515c65')
    fig.subplots_adjust(left=.035, right=.975, bottom=.12, top=.85, wspace=.07, hspace=.25)
    title(fig, 'Dalek ROUND-9 / printed components',
          'Nine distinct STL designs | Ten printed pieces | 07 is used twice | Each panel has its own scale')
    footer(fig, 'Dimensions are each STL bounding box in its exported orientation. Hardware is listed separately in the BOM.')
    save(fig, OUT / '04_printed_components.png')


def base_drive_breakout(meshes):
    fig = plt.figure(figsize=(14, 11))
    ax = fig.add_axes([.13, .12, .71, .75], projection='3d')
    items = [(moved(meshes['01_base'], (0, 0, 13.8)), COLORS[0])]
    for sx in [-1, 1]:
        for sy in [-1, 1]:
            items.append((cylinder((sx*197.5, sy*58, 65), 63, 29, 'x'), np.array([.85, .325, .098])))
            motor = box((-11.2, -57, 0), (22.4, 70, 22.44))
            items.append((moved(motor, (sx*70.5, sy*58, 120), np.diag([sx, sy, 1])), np.array([.929, .694, .125])))
    items.append((box((-35, -57, 185), (70, 114, 76)), GRAY))
    for y in [-121, 65]:
        items.append((box((-80, y, 155), (160, 56, 2)), np.array([.466, .674, .188])))
    for ref, (x, y), (width, depth, height) in BOARD_LAYOUT:
        items.append((box((x-width/2, y-depth/2, 165), (width, depth, height)),
                      np.array([.20, .42, .52]) if 'prototype' not in ref else np.array([.74, .72, .53])))
    draw_meshes(ax, items, edges=False)
    setup_3d(ax, [[-225, -165, 0], [225, 165, 285]], elev=29, azim=-55, tick_step=50)
    title(fig, 'Dalek ROUND-9 / base and drive components',
          'Actual printed base; purchased hardware shown as nominal envelopes | Exploded positions are for clarity')
    footer(fig, 'Motor/wheel hub engagement and actual electronics placement require the mechanical guide and physical fit checks.')
    fig.canvas.draw()
    for point, text, location in [((125, -75, 35), '01  One-piece base\n300 mm diameter', (.04, .20)),
                                  ((197.5, -58, 65), 'Four ground wheels\n63 mm diameter', (.84, .37)),
                                  ((70.5, -36, 131.22), 'Four TT drive motors\nNominal envelopes', (.81, .61)),
                                  ((45, -90, 156), 'Two FR4 plates\n160 x 56 x 2 mm', (.04, .60)),
                                  ((25, -25, 240), 'Rotated battery\n70 x 114 x 76 mm', (.84, .81))]:
        callout(fig, ax, point, text, location)
    save(fig, OUT / '05_base_drive_breakout.png')


def head_friction_breakout(meshes):
    neck = moved(meshes['05_neck'], (0, 0, NECK_Z))
    head = moved(meshes['06_head'], (0, 0, HEAD_Z))
    carriage = moved(meshes['10_head_motor_carriage'], (64.5, 0, NECK_Z+29.2))
    motor = box((52.8, -57, NECK_Z+32.3), (22.44, 70, 22.4))
    wheel = cylinder((64.5, 0, NECK_Z+71), 63, 29)
    adjustment = cylinder((42, -35, NECK_Z+38), 3, 28, 'x')
    common = [(neck, FINISH[3]), (carriage, COLORS[8]), (motor, COLORS[4]),
              (wheel, COLORS[6]), (adjustment, GRAY)]
    fig = plt.figure(figsize=(16, 10))
    ax = fig.add_axes([.07, .15, .43, .7], projection='3d')
    # Expose the fixed drive through labelled cuts in the actual STL surfaces.
    cut = head.slice_plane([0, 0, 0], [0, 1, 0])
    lower_neck = neck.slice_plane([0, 0, NECK_Z+29.2], [0, 0, -1])
    upper_neck = neck.slice_plane([0, 0, NECK_Z+29.2], [0, 0, 1]).slice_plane([0, 0, 0], [0, 1, 0])
    section_neck = trimesh.util.concatenate([lower_neck, upper_neck])
    draw_meshes(ax, [(section_neck, FINISH[3])]+common[1:]+[(cut, FINISH[4])], edges=False)
    setup_3d(ax, [[-120, -115, 390], [120, 120, 570]], elev=27, azim=-55)
    ax.set_title('Head and upper neck cut away at front', fontsize=11)
    top = fig.add_axes([.58, .2, .35, .60])
    # Horizontal slice below the dome crown retains the actual inner friction ring.
    section = head.slice_plane([0, 0, NECK_Z+85], [0, 0, -1])
    draw_meshes(top, common+[(section, FINISH[4])], edges=False)
    top._ortho_spec = (0, 1, 2, 1, 1)
    top.set_aspect('equal'); top.set_xlim(-115, 120); top.set_ylim(-110, 110)
    top.set_axisbelow(True); top.grid(True); top.set_xlabel('X (mm)'); top.set_ylabel('Y (mm)')
    top.set_title('Top section / fixed motor, rotating track', fontsize=11)
    title(fig, 'Dalek ROUND-9 / adjustable head friction drive',
          'Fifth TT3777 motor + 3766 wheel | Actual neck, carriage and head STL sections | Power off before adjusting')
    footer(fig, 'Blue: sliding carriage | Orange: 63 mm tyre | Yellow: motor envelope | Set light contact; preserve slip if obstructed.')
    fig.canvas.draw()
    callout(fig, top, (96, 0, 0), 'Tyre contact', (.83, .85))
    callout(fig, top, (42, -35, 0), 'M3 pressure screw', (.58, .12))
    callout(fig, top, (83.5, -40, 0), '3.6 mm radial slot travel', (.78, .12))
    save(fig, OUT / '06_head_friction_drive.png')


def cad_previews(meshes):
    """Refresh the five existing PDF illustrations from the same STL scene."""
    for name in ['assembly', 'base', 'section', 'exploded', 'rear']:
        fig = plt.figure(figsize=(12, 10))
        ax = fig.add_axes([.10, .08, .80, .80], projection='3d')
        gap = 44 if name == 'exploded' else 0
        if name == 'base':
            items = [(meshes['01_base'], COLORS[0])]
            bounds = [meshes['01_base'].bounds[0]-[15, 15, 3],
                      meshes['01_base'].bounds[1]+[15, 15, 5]]
            elevation, azimuth = 33, -55
        else:
            items = scene(meshes, gap, spread=name == 'exploded', bronze=name != 'exploded')
            if name == 'section':
                cut_shells = []
                for i, (mesh, _) in enumerate(items[:5]):
                    cut = mesh.slice_plane([0, 0, 0], [-1, 0, 0])
                    if len(cut.faces): cut_shells.append((cut, FINISH[i]))
                items = cut_shells+items[5:]
            items += hardware(gap, internals=True)
            bounds = [[-205, -370 if gap else -270, 0], [215, 175, 765 if gap else 590]]
            elevation, azimuth = (12, 90) if name == 'rear' else (22, -35 if name == 'section' else -58)
        draw_meshes(ax, items, edges=False)
        setup_3d(ax, bounds, elev=elevation, azim=azimuth, tick_step=100 if name != 'base' else 50)
        title(fig, 'Dalek ROUND-9 / '+name,
              'Right shell half omitted to expose internal components' if name == 'section'
              else 'Rear-mounted original TTGO T-Display' if name == 'rear'
              else 'Actual STL geometry | Purchased hardware uses nominal envelopes')
        footer(fig)
        save(fig, ROOT/'cad'/f'{name}.png')


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    paths = [ROOT/'cad/dalek.scad', *sorted((ROOT/'stl').glob('*.stl'))]
    inputs = {str(p.relative_to(ROOT)): digest(p) for p in paths}
    assert {p.stem for p in paths[1:]} == set(NAMES)
    meshes = {name: trimesh.load_mesh(ROOT/'stl'/f'{name}.stl', process=True) for name in NAMES}
    with (ROOT/'bom/printed-parts.csv').open(newline='', encoding='utf-8') as handle:
        manifest = {row['part']: row for row in csv.DictReader(handle)}
    assert set(manifest) == set(NAMES)
    assert sum(int(row['quantity']) for row in manifest.values()) == 10
    assert abs(meshes['02_skirt'].extents[2]-213) < .1
    # Verify coordinate transforms against the published assembly datums before drawing.
    assembled_prints = scene(meshes)
    assert len(assembled_prints) == 10
    assert abs(max(mesh.bounds[1, 2] for mesh, _ in assembled_prints)-HEIGHT) < .1
    assert np.allclose(ARM_ROTATION @ np.array([120, 0, 0]), [0, -120, 0])
    board_bounds = []
    for ref, (x, y), (width, depth, _) in BOARD_LAYOUT:
        lower, upper = np.array([x-width/2, y-depth/2]), np.array([x+width/2, y+depth/2])
        assert lower[0] >= -80 and upper[0] <= 80, ref
        assert (lower[1] >= -121 and upper[1] <= -65) or (lower[1] >= 65 and upper[1] <= 121), ref
        for other, lo, hi in board_bounds:
            assert not np.all(np.minimum(upper, hi)-np.maximum(lower, lo) > 0), (ref, other)
        board_bounds.append((ref, lower, upper))
    robot_figures(meshes)
    orthographics(meshes)
    component_figures(meshes, manifest)
    for name in ['02_lower_skirt', '03_upper_skirt']:
        retired = OUT/'components'/f'{name}.png'
        if retired.exists() and (OUT/'components'/'02_skirt.png').exists():
            retired.unlink() # Remove obsolete generated views only after their successor exists.
    base_drive_breakout(meshes)
    head_friction_breakout(meshes)
    cad_previews(meshes)
    outputs = sorted(OUT.glob('*.png')) + sorted((OUT/'components').glob('*.png'))
    assert len(outputs) == 15
    records = []
    for path in outputs:
        with Image.open(path) as png:
            assert png.format == 'PNG' and min(png.size) >= 1600
            records.append({'file': str(path.relative_to(OUT)), 'pixels': list(png.size),
                            'sha256': digest(path)})
    assert all(digest(ROOT/name) == value for name, value in inputs.items())
    (OUT/'drawing-manifest.json').write_text(json.dumps({
        'style': 'MATLAB-style engineering figures, rendered with Matplotlib',
        'inputs_unchanged': True, 'input_sha256': inputs, 'units': 'mm',
        'printed_designs': 9, 'printed_piece_quantity': 10, 'png_count': 15,
        'hardware': 'Nominal envelopes; not detailed manufacturer CAD',
        'board_envelopes': [{'reference': ref, 'center_xy_mm': xy, 'size_xyz_mm': size}
                            for ref, xy, size in BOARD_LAYOUT],
        'battery_envelope_xyz_mm': [70, 114, 76], 'plate_envelope_xyz_mm': [160, 56, 2],
        'pdf_cad_previews': [{'file': f'cad/{name}.png', 'sha256': digest(ROOT/'cad'/f'{name}.png')}
                            for name in ['assembly', 'base', 'section', 'exploded', 'rear']],
        'outputs': records}, indent=2)+'\n', encoding='utf-8')
    archive = OUT/'dalek-matlab-style-pngs.zip'
    with zipfile.ZipFile(archive, 'w', compression=zipfile.ZIP_DEFLATED) as package:
        for path in outputs:
            package.write(path, str(path.relative_to(OUT)))
    with zipfile.ZipFile(archive) as package:
        assert len(package.namelist()) == 15 and package.testzip() is None
    print('PASS: 15 PNG drawings; 9 STL designs / 10 pieces; assembly transforms; unchanged CAD/STL hashes; ZIP verified', flush=True)


if __name__ == '__main__':
    main()
