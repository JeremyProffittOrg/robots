"""Turn the sensor catalogue into the master capability grid.

Input:  radar-compare/data/sensors.csv   (one row per product, filled from research)
Output: radar-compare/data/master-grid.csv
        radar-compare/data/capability.json

The capability level in each cell is COMPUTED from the sensor's own published
numbers by the rules in `capability()` below, never hand-assigned. The rules are
printed into the PDF so a reader can argue with the rule rather than the cell.

Capability levels
  0  nothing            out of range, or the subject returns too little signal
  1  presence only      something is there; no distance, no shape
  2  obstacle + range   a distance to the nearest surface in the beam
  3  living vs not      separates a warm or breathing body from furniture
  4  human vs pet       separates an adult from a cat or dog
  5  full silhouette    enough zones to read a shape and track a posture
"""
from pathlib import Path
import csv
import json
import math
import sys

sys.path.insert(0, str(Path(__file__).resolve().parent))
from geometry import (beam_width_mm, zone_width_mm, TARGETS, FT,
                      DISTANCES_FT, DISTANCES_MM)

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / 'data'
SENSORS = DATA / 'sensors.csv'
GRID_OUT = DATA / 'master-grid.csv'
CAP_OUT = DATA / 'capability.json'

LEVEL_NAME = {
    0: 'nothing',
    1: 'presence only',
    2: 'obstacle + range',
    3: 'living vs not',
    4: 'human vs pet',
    5: 'full silhouette',
}

# Radar cross-section, square metres, at 24-60 GHz. A radar's range scales with
# the fourth root of RCS, so a 20 dB smaller target is seen at 0.32x the range.
RCS_M2 = {
    'adult_human_standing': 0.70,
    'toddler': 0.20,
    'large_dog': 0.05,
    'small_dog': 0.02,
    'cat': 0.012,
    'cat_lying': 0.012,
    'chair_leg': 0.01,
    'power_cable': 0.0005,
    'table_top': 0.30,
}
RCS_REFERENCE = 'adult_human_standing'

# Subjects that are warmer than the room. A thermal array or a PIR sees only
# these; a chair leg and a cable are at room temperature and are invisible to
# both, at every range, forever.
WARM_TARGETS = {'adult_human_standing', 'adult_human_leg', 'toddler',
                'large_dog', 'small_dog', 'cat', 'cat_lying'}


def f(value, default=None):
    """First number in a messy spec string. '0.05 - 4.0 m (88% white)' -> 0.05."""
    if value is None:
        return default
    s = str(value).strip()
    if not s or s.lower() in ('n/a', 'na', '-', 'none', 'not published', 'unknown'):
        return default
    out, cur = [], ''
    for ch in s:
        if ch.isdigit() or ch == '.':
            cur += ch
        else:
            if cur:
                out.append(cur)
            cur = ''
    if cur:
        out.append(cur)
    for tok in out:
        try:
            return float(tok)
        except ValueError:
            continue
    return default


def last_number(value, default=None):
    """Largest number in the string - the useful end of a '0.05 to 4.0 m' range."""
    s = str(value or '')
    nums, cur = [], ''
    for ch in s:
        if ch.isdigit() or ch == '.':
            cur += ch
        else:
            if cur:
                nums.append(cur)
            cur = ''
    if cur:
        nums.append(cur)
    vals = []
    for n in nums:
        try:
            vals.append(float(n))
        except ValueError:
            pass
    return max(vals) if vals else default


def effective_range_m(row, target):
    """Max range on THIS target, in metres, from the sensor's rated range.

    ToF and lidar: rated range is against a stated reflectance, not a size, so it
    is used as published. Where the row carries a dark-target figure that is used
    instead, because a black sock and a dark-furred cat are the real cases.

    mmWave: rated range is against a walking adult. Scaled by the fourth root of
    the target's radar cross-section relative to an adult, which is the radar
    range equation, not a rule of thumb.
    """
    tech = (row.get('tech') or '').strip().lower()
    rated = last_number(row.get('max_range_m')) or 0.0
    if tech.startswith('mmwave'):
        ratio = RCS_M2.get(target, 0.05) / RCS_M2[RCS_REFERENCE]
        return rated * (ratio ** 0.25)
    dark = last_number(row.get('max_range_dark_m'))
    if dark:
        return dark
    return rated


def zones_across(row, target, distance_mm, axis='h'):
    """How many zones of a grid imager the target spans across."""
    n = int(f(row.get('zones_across'), 0) or 0)
    if n <= 1:
        return 0.0
    fov = f(row.get('fov_v_deg') if axis == 'v' else row.get('fov_h_deg'), 0) or 0
    if fov <= 0:
        return 0.0
    z = zone_width_mm(fov, distance_mm, n)
    if z <= 0:
        return 0.0
    extent = (TARGETS[target]['height_mm'] if axis == 'v'
              else TARGETS[target]['width_mm'])
    return extent / z


def lidar_points_on(row, target, distance_mm):
    """Points a scanning lidar puts on the target in one revolution."""
    ares = f(row.get('angular_resolution_deg'), 0) or 0
    if ares <= 0:
        return 0.0
    subtend = math.degrees(2 * math.atan(
        TARGETS[target]['width_mm'] / (2.0 * distance_mm)))
    return subtend / ares


def capability(row, target, distance_mm):
    """The computed capability level, with the reason it came out that way."""
    tech = (row.get('tech') or '').strip().lower()
    d_m = distance_mm / 1000.0
    reach = effective_range_m(row, target)
    min_m = (f(row.get('min_range_m'), 0) or 0)

    if d_m > reach:
        return 0, 'beyond %.2f m reach on this target' % reach
    if d_m < min_m:
        return 0, 'inside the %.2f m dead zone' % min_m

    # --- thermal arrays ---------------------------------------------------
    if tech.startswith('thermal-ir-array') or tech.startswith('thermal-ir-point'):
        if target not in WARM_TARGETS:
            return 0, 'no thermal contrast: furniture sits at room temperature'
        if tech.startswith('thermal-ir-point'):
            return 1, 'single thermopile: one temperature in a cone, no position'
        px = zones_across(row, target, distance_mm, 'h')
        pv = zones_across(row, target, distance_mm, 'v')
        if px < 0.35:
            return 0, ('subject fills %.2f of a pixel; the contrast is diluted '
                       'below the noise floor' % px)
        if px < 1.5:
            return 1, 'about one pixel (%.2f x %.2f) - a warm smear, no shape' % (px, pv)
        if px < 3:
            return 3, 'warm body over %.1f px, but size is not yet separable' % px
        if px < 6:
            return 4, '%.1f x %.1f px - size separates an adult from a pet' % (px, pv)
        return 5, '%.1f x %.1f px - a thermal silhouette' % (px, pv)

    # --- passive infrared -------------------------------------------------
    if tech.startswith('pir'):
        if target not in WARM_TARGETS:
            return 0, 'PIR responds only to a moving heat source'
        return 1, 'motion of a warm body; no range, no classification, no static hold'

    # --- mmWave radar -----------------------------------------------------
    # A vendor presence module reports presence, range and sometimes speed. None
    # of them reports a SPECIES. Telling a cat from a toddler needs micro-Doppler
    # on raw IQ or a point cloud, which these modules do not expose - so level 4
    # is reachable only where the row names a classifying output.
    if tech.startswith('mmwave'):
        out = (row.get('output_type') or '').lower()
        cls = (row.get('classification_output') or '').lower()
        reports_range = 'range' in out or 'distance' in out
        micro = (row.get('static_human_detect') or '').strip().lower()[:1] == 'y'
        why = ['reports %s' % (row.get('output_type') or 'presence'),
               'RCS-scaled reach %.1f m on this target' % reach]
        # A presence radar suppresses motionless returns on purpose. That is what
        # makes it immune to a curtain, and it is also why it cannot see a table.
        if target not in WARM_TARGETS:
            static_ok = (row.get('detects_static_objects') or '').strip().lower()
            if not static_ok.startswith('y'):
                return 0, ('static clutter rejection removes motionless furniture: '
                           'this module is a presence sensor, not an obstacle sensor')
            return 2, 'ranges a static object; ' + why[1]
        level = 2 if reports_range else 1
        if micro:
            level = max(level, 3)
            why.append('micro-motion separates a living body from furniture')
        if ('point' in out or 'cloud' in out or 'doppler' in out) and cls:
            level = max(level, 4)
            why.append('vendor firmware reports a class: %s' % cls)
        elif not cls:
            why.append('no species output: adult-versus-pet needs micro-Doppler '
                       'work on raw data, which this module does not expose')
        return level, '; '.join(why)

    # --- scanning lidar ---------------------------------------------------
    # A 2D scanner sees exactly one horizontal plane. Anything whose top is below
    # that plane, or whose bottom is above it, is invisible at any range.
    if tech.startswith('tof-lidar-scanning'):
        plane = f(row.get('scan_plane_height_mm'), None)
        if plane is not None:
            t = TARGETS[target]
            if t['floor_gap_mm'] + t['height_mm'] < plane:
                return 0, ('top of the subject is %d mm, below the %d mm scan '
                           'plane: invisible at every range'
                           % (t['floor_gap_mm'] + t['height_mm'], plane))
            if t['floor_gap_mm'] > plane:
                return 0, ('subject starts at %d mm, above the %d mm scan plane'
                           % (t['floor_gap_mm'], plane))
        pts = lidar_points_on(row, target, distance_mm)
        if pts < 1:
            return 0, 'under one scan point on the subject (%.2f)' % pts
        if pts < 3:
            return 2, '%.1f points - a range return, no shape' % pts
        if pts < 8:
            return 2, ('%.1f points - an outline; one plane cannot tell a human '
                       'leg from a chair leg' % pts)
        return 3, ('%.0f points - enough for leg-pair and gait inference in '
                   'software, which is a program you write, not a sensor output' % pts)

    # --- fixed single-point lidar / ToF ------------------------------------
    if tech.startswith('tof-lidar'):
        return 2, 'single ranging beam, distance only'

    # --- direct time of flight --------------------------------------------
    if tech.startswith('tof-multizone'):
        zh = zones_across(row, target, distance_mm, 'h')
        zv = zones_across(row, target, distance_mm, 'v')
        if zh < 0.5:
            return 2, ('fills %.2f of a zone - still a valid range return, but '
                       'partial fill and no shape at all' % zh)
        if zh < 1.2:
            return 2, 'fills about one zone (%.2f) - a range, no shape' % zh
        if zh < 2.5:
            return 3, '%.1f x %.1f zones - height profile separates tall from low' % (zh, zv)
        if zh < 5:
            return 4, '%.1f x %.1f zones - width and height separate adult from pet' % (zh, zv)
        return 5, '%.1f x %.1f zones - a depth silhouette' % (zh, zv)
    if tech.startswith('tof'):
        return 2, 'single zone, nearest surface in a %.0f deg cone' % (
            f(row.get('fov_h_deg'), 0) or 0)

    # --- ultrasonic / analog IR / proximity --------------------------------
    if tech.startswith('ultrasonic'):
        return 2, 'echo range to the nearest strong reflector in the cone'
    if tech.startswith('proximity'):
        return 1, 'reflected-light proximity, no calibrated distance'
    if tech.startswith('camera'):
        return 4, 'classification is whatever model runs on the host, not the sensor'
    return 1, 'unclassified technology'


def build():
    if not SENSORS.exists():
        print('no %s yet - nothing to grid' % SENSORS)
        return 1
    with SENSORS.open(encoding='utf-8-sig', newline='') as fh:
        rows = list(csv.DictReader(fh))

    out_rows = []
    cap = {}
    for row in rows:
        sku = row.get('sku') or row.get('name')
        fov = f(row.get('fov_h_deg'), 0) or 0
        rec = {'name': row.get('name'), 'sku': sku, 'vendor': row.get('vendor'),
               'tech': row.get('tech'), 'per_distance': {}}
        line = {
            'name': row.get('name'),
            'vendor': row.get('vendor'),
            'sku': sku,
            'tech': row.get('tech'),
            'price_usd': row.get('price_usd'),
            'fov_h_deg': row.get('fov_h_deg'),
            'fov_v_deg': row.get('fov_v_deg'),
            'zones': row.get('zones'),
            'max_range_m': row.get('max_range_m'),
            'update_hz': row.get('update_hz'),
            'interface': row.get('interface'),
            'needs_line_of_sight': row.get('needs_line_of_sight'),
            'sees_through_plastic': row.get('sees_through_plastic'),
        }
        for ft, mm in zip(DISTANCES_FT, DISTANCES_MM):
            # A scanning sensor has no single cone width: it sweeps the whole
            # circle, so the useful figure is the arc between adjacent samples.
            ares = f(row.get('angular_resolution_deg'), 0) or 0
            if fov >= 180 and ares > 0:
                w = 2.0 * mm * math.tan(math.radians(ares) / 2.0)
                line['width_%dft_mm' % ft] = '%d (sample pitch)' % round(w)
            elif not fov or fov >= 180:
                w = float('inf')
                line['width_%dft_mm' % ft] = 'full circle' if fov >= 180 else ''
            else:
                w = beam_width_mm(fov, mm)
                line['width_%dft_mm' % ft] = round(w)
            per = {}
            for target in ('adult_human_standing', 'cat', 'chair_leg'):
                lvl, why = capability(row, target, mm)
                per[target] = {'level': lvl, 'label': LEVEL_NAME[lvl], 'why': why}
            line['human_%dft' % ft] = '%d %s' % (
                per['adult_human_standing']['level'],
                per['adult_human_standing']['label'])
            line['pet_%dft' % ft] = '%d %s' % (per['cat']['level'],
                                               per['cat']['label'])
            line['object_%dft' % ft] = '%d %s' % (per['chair_leg']['level'],
                                                  per['chair_leg']['label'])
            rec['per_distance']['%dft' % ft] = {
                'beam_width_mm': None if math.isinf(w) or not w else round(w, 1),
                'targets': per}
        out_rows.append(line)
        cap[sku] = rec

    GRID_OUT.parent.mkdir(parents=True, exist_ok=True)
    with GRID_OUT.open('w', encoding='utf-8', newline='') as fh:
        w = csv.DictWriter(fh, fieldnames=list(out_rows[0].keys()))
        w.writeheader()
        w.writerows(out_rows)
    CAP_OUT.write_text(json.dumps({'levels': LEVEL_NAME, 'rcs_m2': RCS_M2,
                                   'sensors': cap}, indent=1), encoding='utf-8')
    print('wrote %s (%d sensors)' % (GRID_OUT, len(out_rows)))
    print('wrote %s' % CAP_OUT)
    return 0


if __name__ == '__main__':
    sys.exit(build())
