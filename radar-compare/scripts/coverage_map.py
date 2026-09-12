"""Render the Option B coverage map for page 3 of the final answer.

Three panels on one sheet: the time-of-flight ring in plan, the thermal ring in
plan, and an elevation through the whole stack showing what each of the four
mounting heights actually intersects. Coverage is evaluated point by point using
the same functions as the geometry engine, so the picture cannot disagree with
the tables.

Output: radar-compare/figures/option_b_coverage.png
"""
from pathlib import Path
import math
import sys

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import Wedge, Circle, Rectangle, Polygon
from matplotlib.lines import Line2D
import matplotlib.gridspec as gridspec

sys.path.insert(0, str(Path(__file__).resolve().parent))
from geometry import (blind_wedge_range_mm, target_visible, TARGETS, FT,
                      DISTANCES_FT, DISTANCES_MM)
from diagrams import _sensor_positions, _covered, INK, MUTED, ACCENT, COVER, BLIND, GRID

ROOT = Path(__file__).resolve().parents[1]
FIG = ROOT / 'figures'
FIG.mkdir(exist_ok=True)
OUT = FIG / 'option_b_coverage.png'

THERM = '#f0a202'
LIDAR = '#1b7f4b'
CLIFF = '#7b3fa0'
RADIUS = 175.0

# The Option B build, exactly as the recommendation specifies it.
BUILD = [
    ('ToF ring',  12, 45, 200, 0,  COVER, 'VL53L8CX 8x8, 45 x 45 deg'),
    ('Thermal',    8, 60, 250, 0,  THERM, 'AMG8833 8x8, 60 x 60 deg'),
    ('Lidar',      1, 360, 100, 0, LIDAR, 'RPLIDAR C1, 360 deg plane'),
    ('Cliff',      6, 18, 150, 23, CLIFF, 'VL53L4CD, 23 deg down-cant'),
]

plt.rcParams.update({
    'font.family': 'DejaVu Sans', 'font.size': 7.6,
    'text.color': INK, 'figure.facecolor': 'white', 'axes.facecolor': 'white',
    'savefig.facecolor': 'white', 'savefig.dpi': 230,
})


def plan_panel(ax, n, fov, colour, title, limit=1150.0, res=300):
    ax.set_aspect('equal')
    ax.set_xlim(-limit, limit)
    ax.set_ylim(-limit, limit)
    sensors = _sensor_positions(n, RADIUS, 'round')

    step = 2.0 * limit / res
    xs, ys = [], []
    for i in range(res):
        px = -limit + (i + 0.5) * step
        for j in range(res):
            py = -limit + (j + 0.5) * step
            if px * px + py * py <= RADIUS * RADIUS:
                continue
            if not _covered(px, py, sensors, fov):
                xs.append(px); ys.append(py)
    ax.scatter(xs, ys, s=(step * 0.9) ** 2 * 0.40, c=BLIND, alpha=0.34,
               marker='s', linewidths=0, zorder=1)

    for sx, sy, bore in sensors:
        ax.add_patch(Wedge((sx, sy), limit * 2.2, bore - fov / 2, bore + fov / 2,
                           facecolor=colour, alpha=0.15, edgecolor=colour,
                           lw=0.4, zorder=2))
    for sx, sy, bore in sensors:
        ax.plot([sx], [sy], marker='s', ms=4.2, color=colour, mec=INK, mew=0.4,
                zorder=7)

    for ft, mm in zip(DISTANCES_FT, DISTANCES_MM):
        if mm > limit:
            continue
        ax.add_patch(Circle((0, 0), mm, fill=False, ec=MUTED, lw=0.5,
                            ls=(0, (4, 3)), zorder=6))
        ax.text(mm * 0.707, mm * 0.707, ' %d ft' % ft, fontsize=5.8, color=MUTED,
                ha='left', va='bottom', zorder=7)

    ax.add_patch(Circle((0, 0), RADIUS, facecolor='#e2e6eb', ec=INK, lw=1.0,
                        zorder=5))
    b = blind_wedge_range_mm(n, fov, RADIUS)
    sub = ('wedges close %d mm past the skin' % round(b['from_edge_mm'])
           if b['closes'] else 'wedges never close')
    ax.set_title('%s\n%s' % (title, sub), fontsize=7.6, pad=5)
    ax.set_xticks([]); ax.set_yticks([])
    for s in ax.spines.values():
        s.set_visible(False)


def elevation_panel(ax):
    far = 3400.0
    BAR = 30.0          # drawing width of a subject, mm - a silhouette, not a bar
    SPREAD = 92.0       # spacing between subjects within one distance group

    def clip(poly, inside, cut):
        """One Sutherland-Hodgman pass against a half-plane."""
        out = []
        for i, a in enumerate(poly):
            b = poly[i - 1]
            if inside(a):
                if not inside(b):
                    out.append(cut(b, a))
                out.append(a)
            elif inside(b):
                out.append(cut(b, a))
        return out

    def beam(h, fov, tilt, colour, fill, zorder, ceiling=2010.0):
        """The wedge from (0, h), clipped to the panel box.

        Clipping matters twice over. An unclipped beam that leaves the bottom of
        the panel closes itself against the right-hand edge and draws a spurious
        vertical line; and a down-canted cliff beam physically ENDS where it
        strikes the floor rather than running along it.
        """
        lo = math.radians(-fov / 2.0 - tilt)
        hi = math.radians(+fov / 2.0 - tilt)
        reach = far * 4.0
        poly = [(0.0, h),
                (reach, h + reach * math.tan(hi)),
                (reach, h + reach * math.tan(lo))]
        for inside, cut in (
            (lambda p: p[1] >= 0.0,
             lambda b, a: (b[0] + (a[0] - b[0]) * (0.0 - b[1]) / (a[1] - b[1]), 0.0)),
            (lambda p: p[1] <= ceiling,
             lambda b, a: (b[0] + (a[0] - b[0]) * (ceiling - b[1]) / (a[1] - b[1]),
                           ceiling)),
            (lambda p: p[0] <= far,
             lambda b, a: (far, b[1] + (a[1] - b[1]) * (far - b[0]) / (a[0] - b[0]))),
        ):
            poly = clip(poly, inside, cut)
            if not poly:
                return
        if fill:
            ax.add_patch(Polygon(poly, closed=True, facecolor=colour, alpha=0.16,
                                 edgecolor=colour, lw=0.7, zorder=zorder))
        else:
            # outline only: draw the two beam edges, never the clip boundary
            for ang in (hi, lo):
                x_end = far
                y_end = h + x_end * math.tan(ang)
                if y_end > ceiling:
                    x_end, y_end = (ceiling - h) / math.tan(ang), ceiling
                elif y_end < 0:
                    x_end, y_end = -h / math.tan(ang), 0.0
                ax.plot([0, x_end], [h, y_end], color=colour, lw=0.9,
                        ls=(0, (5, 3)), zorder=zorder)

    # thermal outlined only, so it cannot bury the collision ring beneath it
    beam(250, 60, 0, THERM, False, 2)
    # the collision ring, filled, on top
    beam(200, 45, 0, COVER, True, 3)

    # the lidar plane is a line, not a wedge
    for label, n, fov, h, tilt, colour, spec in BUILD:
        if label != 'Lidar':
            continue
        ax.plot([0, far], [h, h], color=colour, lw=1.8, zorder=6)

    # the cliff wedge, which strikes the floor almost immediately by design
    beam(150, 18, 23, CLIFF, True, 5)

    ax.axhline(0, color=INK, lw=1.3, zorder=7)
    ax.add_patch(Rectangle((-RADIUS, 0), RADIUS, 700, facecolor='#e2e6eb',
                           ec=INK, lw=1.0, zorder=8))
    ax.text(-RADIUS / 2, 745, '350 mm\nrobot', fontsize=6.2, ha='center',
            va='bottom', color=INK, linespacing=1.1)

    subjects = [('adult_human_standing', 'adult'), ('toddler', 'toddler'),
                ('large_dog', 'dog'), ('cat', 'cat'), ('cat_lying', 'cat lying')]
    for ft, mm in zip(DISTANCES_FT, DISTANCES_MM):
        ax.axvline(mm, color=GRID, lw=0.5, ls=(0, (3, 3)), zorder=1)
        ax.text(mm, -105, '%d ft' % ft, fontsize=6.4, color=MUTED, ha='center',
                va='top')
        for j, (key, label) in enumerate(subjects):
            t = TARGETS[key]
            x = mm + (j - 2) * SPREAD
            seen = target_visible(200, 45, 0, t, mm)['visible']
            # what the same ring would miss if it were mounted at body height
            high = target_visible(800, 45, 0, t, mm)['visible']
            col = '#1b7f4b' if seen else BLIND
            ax.add_patch(Rectangle((x - BAR / 2, t['floor_gap_mm']), BAR,
                                   t['height_mm'], facecolor=col,
                                   alpha=0.62 if seen else 0.42,
                                   ec=BLIND if not high else col,
                                   lw=1.3 if not high else 0.5,
                                   ls=(0, (2, 1.4)) if not high else 'solid',
                                   zorder=9))

    for key, label in subjects:
        t = TARGETS[key]
        ax.text(far + 60, t['floor_gap_mm'] + t['height_mm'],
                '%s %d' % (label, t['height_mm']), fontsize=6.0, color=MUTED,
                va='center', ha='left')

    # mount-height callouts, stacked so they cannot collide
    for k, (label, n, fov, h, tilt, colour, spec) in enumerate(
            sorted(BUILD, key=lambda b: -b[3])):
        y = 1830 - k * 168
        ax.plot([0], [h], marker='s', ms=5.4, color=colour, mec=INK, mew=0.4,
                zorder=10)
        ax.annotate('%s %d mm' % (label, h), (0, h), (-700, y), fontsize=6.3,
                    color=colour, ha='left', va='center',
                    arrowprops=dict(arrowstyle='-', color=colour, lw=0.6,
                                    shrinkA=0, shrinkB=2))

    ax.set_xlim(-720, far + 430)
    ax.set_ylim(-230, 2020)
    ax.set_ylabel('height above floor (mm)', fontsize=6.8)
    ax.set_yticks([0, 250, 650, 850, 1700])
    ax.set_xticks([])
    ax.set_title('Elevation: why the ring goes at 200 mm. Solid green = the 200 mm '
                 'ring reaches it. Red dashed outline = the same ring at body '
                 'height (800 mm) would miss it entirely.', fontsize=7.4, pad=5)
    for s in ('top', 'right', 'bottom'):
        ax.spines[s].set_visible(False)


def main():
    fig = plt.figure(figsize=(7.45, 8.55))
    gs = gridspec.GridSpec(2, 2, height_ratios=[1.00, 0.92], hspace=0.13,
                           wspace=0.05)
    plan_panel(fig.add_subplot(gs[0, 0]), 12, 45, COVER,
               '12 x VL53L8CX at 200 mm, 45 deg H, 30 deg apart')
    plan_panel(fig.add_subplot(gs[0, 1]), 8, 60, THERM,
               '8 x AMG8833 at 250 mm, 60 deg H, 45 deg apart')
    elevation_panel(fig.add_subplot(gs[1, :]))

    handles = [Line2D([], [], marker='s', ls='', ms=6, mec=INK, mew=0.4,
                      color=c, label=s)
               for _, _, _, _, _, c, s in BUILD]
    handles.append(Line2D([], [], marker='s', ls='', ms=6, color=BLIND,
                          alpha=0.5, label='blind wedge, in plan'))
    handles.append(Line2D([], [], marker='s', ls='', ms=6, color='#1b7f4b',
                          alpha=0.62, label='reached by the 200 mm ring'))
    handles.append(Line2D([], [], marker='s', ls='', ms=6, mfc='none',
                          mec=BLIND, mew=1.4, color='none',
                          label='a ring at 800 mm would miss it'))
    fig.legend(handles=handles, loc='lower center', ncol=3, frameon=False,
               fontsize=6.8, bbox_to_anchor=(0.5, 0.002))
    fig.savefig(OUT, bbox_inches='tight', pad_inches=0.12)
    plt.close(fig)
    print('wrote %s' % OUT)


if __name__ == '__main__':
    main()
