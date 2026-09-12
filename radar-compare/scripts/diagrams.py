"""Render the coverage diagrams for the perimeter-sensing guide.

Every diagram is drawn from the same functions the geometry engine uses, so a
picture can never disagree with a table. Output: radar-compare/figures/*.png
"""
from pathlib import Path
import math
import sys

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import Wedge, Circle, Rectangle, Polygon, FancyArrow

sys.path.insert(0, str(Path(__file__).resolve().parent))
from geometry import (blind_wedge_range_mm, beam_width_mm, zone_width_mm,
                      target_visible, TARGETS, FT, DISTANCES_FT, DISTANCES_MM)

ROOT = Path(__file__).resolve().parents[1]
FIG = ROOT / 'figures'
FIG.mkdir(exist_ok=True)

INK = '#111827'
MUTED = '#4b5563'
ACCENT = '#0f4c81'
COVER = '#2d7dd2'
BLIND = '#d1495b'
WARM = '#f0a202'
GRID = '#c3cbd6'

plt.rcParams.update({
    'font.family': 'DejaVu Sans', 'font.size': 8,
    'axes.edgecolor': GRID, 'axes.labelcolor': INK,
    'text.color': INK, 'xtick.color': MUTED, 'ytick.color': MUTED,
    'figure.facecolor': 'white', 'axes.facecolor': 'white',
    'savefig.facecolor': 'white', 'savefig.dpi': 220,
})


def _save(fig, name):
    path = FIG / name
    fig.savefig(path, bbox_inches='tight', pad_inches=0.16)
    plt.close(fig)
    print('  %s' % path.name)
    return path


# --------------------------------------------------------------------------
# 1. plan view of a sensor ring, showing the blind wedges
# --------------------------------------------------------------------------
def _sensor_positions(n, radius, shape):
    """Where the sensors sit and which way each looks.

    Round platform: evenly spaced on the circle, each aimed radially outward.
    Square platform: spread evenly around the square perimeter, each aimed along
    the outward normal of the face it sits on (a corner sensor is aimed along
    the diagonal), which is how one is actually mounted to a flat panel.
    """
    out = []
    for k in range(n):
        bore = 360.0 * k / n
        br = math.radians(bore)
        if shape == 'round':
            out.append((radius * math.cos(br), radius * math.sin(br), bore))
        else:
            # project the ray onto the square of half-width `radius`
            c, s = math.cos(br), math.sin(br)
            t = radius / max(abs(c), abs(s))
            out.append((t * c, t * s, bore))
    return out


def _covered(px, py, sensors, fov):
    half = math.radians(fov) / 2.0
    for sx, sy, bore in sensors:
        dx, dy = px - sx, py - sy
        if dx == 0 and dy == 0:
            return True
        ang = math.atan2(dy, dx) - math.radians(bore)
        ang = (ang + math.pi) % (2 * math.pi) - math.pi
        if abs(ang) <= half:
            return True
    return False


def ring_plan(n, fov, radius=175.0, limit=1600.0, shape='round', title=None,
              name=None, res=420):
    """Plan view. Coverage is evaluated point by point, not assumed."""
    fig, ax = plt.subplots(figsize=(4.6, 4.6))
    ax.set_aspect('equal')
    ax.set_xlim(-limit, limit)
    ax.set_ylim(-limit, limit)

    sensors = _sensor_positions(n, radius, shape)

    # numeric coverage map: red where no sensor cone reaches
    step = 2.0 * limit / res
    xs, ys = [], []
    for i in range(res):
        px = -limit + (i + 0.5) * step
        for j in range(res):
            py = -limit + (j + 0.5) * step
            if shape == 'round':
                if px * px + py * py <= radius * radius:
                    continue
            elif abs(px) <= radius and abs(py) <= radius:
                continue
            if not _covered(px, py, sensors, fov):
                xs.append(px); ys.append(py)
    ax.scatter(xs, ys, s=(step * 0.9) ** 2 * 0.42, c=BLIND, alpha=0.30,
               marker='s', linewidths=0, zorder=1)
    covered_fraction = 1.0 - len(xs) / float(res * res)

    # each sensor cone, outlined so overlap is readable
    for sx, sy, bore in sensors:
        ax.add_patch(Wedge((sx, sy), limit * 2.2, bore - fov / 2, bore + fov / 2,
                           facecolor=COVER, alpha=0.13, edgecolor=COVER, lw=0.45,
                           zorder=2))
    for sx, sy, bore in sensors:
        ax.plot([sx], [sy], marker='s', ms=4.6, color=ACCENT, zorder=7)

    # range rings at the five survey distances
    for ft, mm in zip(DISTANCES_FT, DISTANCES_MM):
        if mm > limit:
            continue
        ax.add_patch(Circle((0, 0), mm, fill=False, ec=MUTED, lw=0.55,
                            ls=(0, (4, 3)), zorder=6))
        ax.text(mm * 0.707, mm * 0.707, ' %d ft' % ft, fontsize=6.2, color=MUTED,
                ha='left', va='bottom', zorder=7)

    # the platform
    if shape == 'round':
        ax.add_patch(Circle((0, 0), radius, facecolor='#e2e6eb', ec=INK, lw=1.1,
                            zorder=5))
    else:
        ax.add_patch(Rectangle((-radius, -radius), 2 * radius, 2 * radius,
                               facecolor='#e2e6eb', ec=INK, lw=1.1, zorder=5))
    ax.text(-limit * 0.97, -limit * 0.97, '350 mm robot, sensors on the perimeter',
            ha='left', va='bottom', fontsize=6.4, color=INK, zorder=7)

    b = blind_wedge_range_mm(n, fov, radius)
    if b['closes']:
        sub = ('blind wedges close %d mm (%.1f ft) past the edge  |  %.0f%% of the '
               '%.1f ft square covered'
               % (round(b['from_edge_mm']), b['from_edge_mm'] / FT,
                  covered_fraction * 100, 2 * limit / FT))
    else:
        sub = ('blind wedges NEVER close: %d x %d deg = %d deg < 360 deg  |  '
               '%.0f%% covered'
               % (n, fov, n * fov, covered_fraction * 100))
    ax.set_title((title or '%d sensors x %d deg field of view' % (n, fov)) +
                 '\n' + sub, fontsize=8.2, color=INK, pad=8)
    ax.set_xticks([]); ax.set_yticks([])
    for s in ax.spines.values():
        s.set_visible(False)
    return _save(fig, name or 'ring_%dx%d.png' % (n, fov))


# --------------------------------------------------------------------------
# 2. vertical profile: what a ring at height h actually intersects
# --------------------------------------------------------------------------
def vertical_profile(mount_h, fov_v, tilt, name, title=None):
    fig, ax = plt.subplots(figsize=(7.4, 2.9))
    far = 3300.0
    half = fov_v / 2.0
    lo = math.radians(-half - tilt)
    hi = math.radians(+half - tilt)
    ax.add_patch(Polygon([(0, mount_h),
                          (far, mount_h + far * math.tan(hi)),
                          (far, mount_h + far * math.tan(lo))],
                         facecolor=COVER, alpha=0.18, edgecolor=COVER, lw=0.6))

    # floor and the robot
    ax.axhline(0, color=INK, lw=1.2)
    ax.add_patch(Rectangle((-175, 0), 175, max(mount_h + 60, 200),
                           facecolor='#e7ebf0', ec=INK, lw=1.0))
    ax.plot([0], [mount_h], marker='s', ms=6, color=ACCENT, zorder=6)
    ax.annotate('sensor\n%d mm' % mount_h, (0, mount_h), (-560, mount_h + 260),
                fontsize=6.6, color=ACCENT, ha='left',
                arrowprops=dict(arrowstyle='->', color=ACCENT, lw=0.7))

    # the subjects, at the five survey distances
    subjects = [('adult_human_standing', 'adult'), ('toddler', 'toddler'),
                ('large_dog', 'dog'), ('cat', 'cat'), ('cat_lying', 'cat lying')]
    for ft, mm in zip(DISTANCES_FT, DISTANCES_MM):
        if mm > far:
            continue
        ax.axvline(mm, color=GRID, lw=0.5, ls=(0, (3, 3)))
        ax.text(mm, -60, '%d ft' % ft, fontsize=6.2, color=MUTED, ha='center', va='top')
    step = 190
    for j, (key, label) in enumerate(subjects):
        t = TARGETS[key]
        for ft, mm in zip(DISTANCES_FT, DISTANCES_MM):
            if mm > far:
                continue
            x = mm + (j - 2) * step * 0.42
            r = target_visible(mount_h, fov_v, tilt, t, mm)
            col = '#1b7f4b' if r['visible'] else BLIND
            ax.add_patch(Rectangle((x - t['width_mm'] / 6, t['floor_gap_mm']),
                                   t['width_mm'] / 3, t['height_mm'],
                                   facecolor=col, alpha=0.55 if r['visible'] else 0.35,
                                   ec=col, lw=0.6))
    # legend of subject heights
    for j, (key, label) in enumerate(subjects):
        t = TARGETS[key]
        ax.text(far + 60, t['floor_gap_mm'] + t['height_mm'],
                '%s %d mm' % (label, t['height_mm']), fontsize=6.2, color=MUTED,
                va='center', ha='left')

    ax.set_xlim(-700, far + 620)
    ax.set_ylim(-170, 2050)
    ax.set_ylabel('height above floor (mm)', fontsize=7)
    ax.set_yticks([0, 250, 650, 850, 1700])
    ax.set_xticks([])
    ax.set_title(title or ('sensor at %d mm, %d deg vertical field of view, '
                           '%d deg down-tilt   '
                           '(green = inside the beam, red = missed)'
                           % (mount_h, fov_v, tilt)),
                 fontsize=8.5, pad=7)
    for s in ('top', 'right', 'bottom'):
        ax.spines[s].set_visible(False)
    return _save(fig, name)


# --------------------------------------------------------------------------
# 3. beam width against range
# --------------------------------------------------------------------------
def beam_width_chart():
    fig, ax = plt.subplots(figsize=(7.0, 3.4))
    d = [x * 40 for x in range(1, 80)]
    palette = ['#0f4c81', '#2d7dd2', '#4fa3e3', '#1b7f4b', '#f0a202', '#d1495b',
               '#7b3fa0']
    for i, fov in enumerate([19, 27, 45, 60, 90, 100, 120]):
        ax.plot([x / FT for x in d], [beam_width_mm(fov, x) / 25.4 for x in d],
                color=palette[i], lw=1.5, label='%d deg' % fov)
    for ft in DISTANCES_FT:
        ax.axvline(ft, color=GRID, lw=0.5, ls=(0, (3, 3)))
    ax.axhline(450 / 25.4, color=MUTED, lw=0.8, ls=(0, (5, 3)))
    ax.text(10.2, 450 / 25.4, ' adult torso 450 mm', fontsize=6.4, color=MUTED, va='center')
    ax.axhline(140 / 25.4, color=MUTED, lw=0.8, ls=(0, (5, 3)))
    ax.text(10.2, 140 / 25.4, ' cat 140 mm', fontsize=6.4, color=MUTED, va='center')
    ax.set_xlim(0, 10.4); ax.set_ylim(0, 260)
    ax.set_xlabel('range from the sensor (ft)', fontsize=7.5)
    ax.set_ylabel('beam footprint width (in)', fontsize=7.5)
    ax.set_title('One sensor sees a cone, not a ray: footprint width = 2 d tan(FoV/2)',
                 fontsize=8.5, pad=7)
    ax.legend(fontsize=6.6, frameon=False, ncol=4, loc='upper left')
    ax.grid(True, color=GRID, lw=0.4, alpha=0.5)
    for s in ('top', 'right'):
        ax.spines[s].set_visible(False)
    return _save(fig, 'beam_width.png')


# --------------------------------------------------------------------------
# 4. how many pixels a subject fills in a grid imager
# --------------------------------------------------------------------------
def pixel_fill_chart():
    grids = [('VL53L5CX 8x8, 45 deg H', 45, 8), ('VL53L7CX 8x8, 60 deg H', 60, 8),
             ('AMG8833 8x8, 60 deg', 60, 8), ('MLX90640 32x24, 55 deg', 55, 32)]
    fig, axes = plt.subplots(1, len(grids), figsize=(9.4, 2.7), sharey=True)
    subjects = [('adult_human_standing', '#0f4c81'), ('toddler', '#2d7dd2'),
                ('large_dog', '#1b7f4b'), ('cat', '#d1495b')]
    for ax, (label, fov, n) in zip(axes, grids):
        for key, col in subjects:
            t = TARGETS[key]
            ys = [t['width_mm'] / zone_width_mm(fov, mm, n) for mm in DISTANCES_MM]
            ax.plot(DISTANCES_FT, ys, marker='o', ms=3.4, lw=1.4, color=col,
                    label=key.replace('_', ' '))
        ax.axhline(1.0, color=MUTED, lw=0.9, ls=(0, (4, 3)))
        ax.axhline(3.0, color='#1b7f4b', lw=0.7, ls=(0, (2, 2)))
        ax.set_yscale('log')
        ax.set_title(label, fontsize=7.2)
        ax.set_xlabel('ft', fontsize=7)
        ax.set_xticks(DISTANCES_FT)
        ax.grid(True, color=GRID, lw=0.4, alpha=0.5, which='both')
        for s in ('top', 'right'):
            ax.spines[s].set_visible(False)
    axes[0].set_ylabel('zones across the subject', fontsize=7.2)
    axes[0].text(1.1, 1.06, '1 zone = detected, not classified', fontsize=5.8,
                 color=MUTED)
    axes[0].text(1.1, 3.2, '3 zones = a shape', fontsize=5.8, color='#1b7f4b')
    axes[-1].legend(fontsize=6.2, frameon=False, loc='lower left')
    fig.suptitle('A subject must fill several zones before its SHAPE can be read',
                 fontsize=8.6, y=1.04)
    return _save(fig, 'pixel_fill.png')


# --------------------------------------------------------------------------
# 5. modality capability heat grid
# --------------------------------------------------------------------------
def capability_grid(rows, name, title):
    """rows: list of (label, [level at 1,3,5,8,10 ft]) with level 0..5."""
    LEVELS = ['nothing', 'presence only', 'obstacle + range',
              'human vs not-human', 'human vs pet', 'full silhouette']
    COLS = ['#e6e8eb', '#cfe0f0', '#9dc6e8', '#5da5da', '#2d7dd2', '#0f4c81']
    fig, ax = plt.subplots(figsize=(7.6, 0.34 * len(rows) + 1.5))
    for r, (label, levels) in enumerate(rows):
        for c, lv in enumerate(levels):
            ax.add_patch(Rectangle((c, len(rows) - r - 1), 0.96, 0.92,
                                   facecolor=COLS[lv], ec='white', lw=1.2))
            ax.text(c + 0.48, len(rows) - r - 1 + 0.46, str(lv), ha='center',
                    va='center', fontsize=6.6,
                    color='white' if lv >= 3 else INK)
    ax.set_xlim(0, 5); ax.set_ylim(0, len(rows))
    ax.set_xticks([c + 0.48 for c in range(5)])
    ax.set_xticklabels(['%d ft' % f for f in DISTANCES_FT], fontsize=7.4)
    ax.set_yticks([len(rows) - r - 0.54 for r in range(len(rows))])
    ax.set_yticklabels([lab for lab, _ in rows], fontsize=7.0)
    ax.xaxis.set_ticks_position('top')
    for s in ax.spines.values():
        s.set_visible(False)
    ax.tick_params(length=0)
    legend = '   '.join('%d %s' % (i, t) for i, t in enumerate(LEVELS))
    ax.set_xlabel(legend, fontsize=6.4, color=MUTED, labelpad=8)
    ax.set_title(title, fontsize=8.8, pad=26)
    return _save(fig, name)


def main():
    """Every FoV below is the HORIZONTAL figure.

    ST publishes a diagonal field of view on the front page of every VL53
    datasheet, and it is a separately measured number, not the geometric
    diagonal of the square detection volume. Sizing a ring from it overstates
    coverage badly: the VL53L5CX is 63 deg diagonal but 45 x 45 deg horizontal
    and vertical, and the VL53L7CX is 90 deg diagonal but 60 x 60 deg. Using
    the diagonal would say six L7CX close a ring; they do not.
    """
    print('rendering figures')
    # single-zone ST parts: VL53L1X is 27 deg diagonal, about 19 deg horizontal
    ring_plan(8, 19, title='8 x VL53L1X (19 deg horizontal) - the naive ring',
              name='ring_8x19.png')
    ring_plan(16, 19, title='16 x VL53L1X (19 deg horizontal) - still 56 deg short',
              name='ring_16x19.png')
    # VL53L5CX / VL53L8CX: 45 x 45 deg horizontal and vertical
    ring_plan(8, 45, title='8 x VL53L5CX (45 deg H) - exactly 360 deg, no margin')
    ring_plan(10, 45, title='10 x VL53L5CX (45 deg H) - 90 deg of overlap')
    ring_plan(12, 45, title='12 x VL53L5CX (45 deg H) - the recommended ToF ring')
    ring_plan(12, 45, shape='square', name='ring_12x45_square.png',
              title='12 x 45 deg on a 350 mm SQUARE platform')
    # VL53L7CX: 60 x 60 deg horizontal and vertical
    ring_plan(6, 60, title='6 x VL53L7CX (60 deg H) - exactly 360 deg, no margin')
    ring_plan(8, 60, title='8 x VL53L7CX (60 deg H) - the cheaper closed ring')
    # mmWave presence ring
    ring_plan(4, 100, title='4 x 100 deg mmWave - a presence ring, not an obstacle ring')

    # vertical, using the real vertical FoV of each part
    vertical_profile(100, 45, 0, 'vertical_low_45.png',
                     title='VL53L5CX at 100 mm, 45 deg vertical, no tilt   '
                           '(green = inside the beam, red = missed)')
    vertical_profile(200, 45, 0, 'vertical_200_45.png')
    vertical_profile(300, 45, 0, 'vertical_300_45.png')
    vertical_profile(800, 45, 0, 'vertical_high_45.png')
    vertical_profile(800, 45, 15, 'vertical_high_45_tilt.png')
    vertical_profile(400, 60, 10, 'vertical_400_60_tilt.png')

    beam_width_chart()
    pixel_fill_chart()
    print('done')


if __name__ == '__main__':
    main()
