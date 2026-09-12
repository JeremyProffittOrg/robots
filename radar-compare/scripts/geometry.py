"""Perimeter coverage geometry for a 350 mm mobile robot.

Every number this project quotes for beam width, ring count, blind wedge,
vertical intercept and stopping distance is computed here, not copied from a
vendor page. Output: radar-compare/data/geometry.json
"""
from pathlib import Path
import json
import math

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'data' / 'geometry.json'

FT = 304.8                                   # mm per foot
DISTANCES_FT = [1, 3, 5, 8, 10]
DISTANCES_MM = [d * FT for d in DISTANCES_FT]

# Field-of-view values that appear in the real catalogue, plus round numbers.
FOVS = [15, 20, 25, 27, 30, 45, 55, 60, 63, 65, 80, 90, 100, 110, 120, 150, 180]

PLATFORM = {
    'square': {'across_face': 350.0, 'across_corner': 350.0 * math.sqrt(2),
               'perimeter': 4 * 350.0, 'inscribed_radius': 175.0,
               'circumscribed_radius': 350.0 * math.sqrt(2) / 2},
    'round': {'diameter': 350.0, 'radius': 175.0, 'perimeter': math.pi * 350.0},
}

# Target subjects. Width is the horizontal extent presented to a perimeter sensor.
TARGETS = {
    'adult_human_standing': {'width_mm': 450, 'height_mm': 1700, 'floor_gap_mm': 0,
                             'note': 'torso width; shoulders 400-500 mm'},
    'adult_human_leg': {'width_mm': 140, 'height_mm': 800, 'floor_gap_mm': 0,
                        'note': 'single leg - what a low perimeter ring actually sees'},
    'toddler': {'width_mm': 250, 'height_mm': 850, 'floor_gap_mm': 0,
                'note': '2 to 3 years old'},
    'large_dog': {'width_mm': 250, 'height_mm': 650, 'floor_gap_mm': 0,
                  'note': 'labrador at the shoulder'},
    'small_dog': {'width_mm': 160, 'height_mm': 330, 'floor_gap_mm': 0,
                  'note': 'terrier at the shoulder'},
    'cat': {'width_mm': 140, 'height_mm': 250, 'floor_gap_mm': 0,
            'note': 'standing cat at the shoulder'},
    'cat_lying': {'width_mm': 300, 'height_mm': 130, 'floor_gap_mm': 0,
                  'note': 'the worst case - a sleeping cat'},
    'chair_leg': {'width_mm': 30, 'height_mm': 430, 'floor_gap_mm': 0,
                  'note': 'thin vertical obstacle'},
    'power_cable': {'width_mm': 6, 'height_mm': 6, 'floor_gap_mm': 0,
                    'note': 'the classic robot killer'},
    'table_top': {'width_mm': 900, 'height_mm': 40, 'floor_gap_mm': 700,
                  'note': 'overhang - invisible to any ring mounted below it'},
}


def beam_width_mm(fov_deg, distance_mm):
    """Full lateral width of a symmetric cone of angle fov_deg at range distance_mm."""
    if fov_deg >= 180:
        return float('inf')
    return 2.0 * distance_mm * math.tan(math.radians(fov_deg) / 2.0)


def zone_width_mm(fov_deg, distance_mm, zones_across):
    """Lateral footprint of ONE centre zone of a zones_across grid imager.

    The cone is angular, so outer zones cover more ground than centre zones.
    This returns the CENTRE zone, the narrowest and therefore the limiting case
    for resolving a small target. Rectilinear (pinhole) projection, which is how
    a SPAD array and a thermopile array both map.
    """
    t_edge = math.tan(math.radians(fov_deg) / 2.0)
    t_zone = t_edge / (zones_across / 2.0)
    return 2.0 * distance_mm * t_zone


def ring_count(fov_deg, overlap_deg):
    """Sensors needed to close a 360 degree ring with a guaranteed angular overlap."""
    effective = fov_deg - overlap_deg
    if effective <= 0:
        return None
    return math.ceil(360.0 / effective)


def blind_wedge_range_mm(n_sensors, fov_deg, mount_radius_mm):
    """Range at which the blind wedge between adjacent ring sensors closes.

    Each sensor sits at radius r on the platform edge, aimed radially outward,
    with half-angle a = fov/2. Adjacent sensors are separated by 2*pi/n, so the
    bisector between two of them lies at s = pi/n. The worst-covered direction
    is along that bisector.

    A point P at range u along the bisector is P = (u cos s, u sin s). Seen from
    the sensor at (r, 0), it lies at angle

        beta = atan2(u sin s, u cos s - r)

    measured from the sensor's own boresight. beta starts at 180 degrees for
    u near zero and falls monotonically to s as u goes to infinity. So the
    wedge closes only if s <= a, that is only if n*fov >= 360 - the platform
    offset r changes WHERE the wedge closes, never WHETHER it closes. Setting
    beta = a and solving:

        u = r * sin(a) / sin(a - s)

    Returns that range from the platform centre and from the platform edge.
    """
    a = math.radians(fov_deg) / 2.0
    s = math.pi / n_sensors
    if a <= s + 1e-12:
        # n*fov <= 360: the wedge never closes, at any range.
        return {'from_centre_mm': None, 'from_edge_mm': None,
                'closes': False, 'closes_at_surface': False}
    u = mount_radius_mm * math.sin(a) / math.sin(a - s)
    if u <= mount_radius_mm:
        return {'from_centre_mm': mount_radius_mm, 'from_edge_mm': 0.0,
                'closes': True, 'closes_at_surface': True}
    return {'from_centre_mm': u, 'from_edge_mm': u - mount_radius_mm,
            'closes': True, 'closes_at_surface': False}


def vertical_intercept(mount_h_mm, fov_v_deg, down_tilt_deg=0.0):
    """Where a vertically symmetric cone meets the floor, and its height at range."""
    half = fov_v_deg / 2.0
    lower_deg = -half - down_tilt_deg     # negative means below horizontal
    upper_deg = +half - down_tilt_deg
    if lower_deg < 0:
        floor_strike = mount_h_mm / math.tan(math.radians(-lower_deg))
    else:
        floor_strike = None               # beam never points down, never strikes floor
    rows = []
    for ft, mm in zip(DISTANCES_FT, DISTANCES_MM):
        lo = mount_h_mm + mm * math.tan(math.radians(lower_deg))
        hi = mount_h_mm + mm * math.tan(math.radians(upper_deg))
        rows.append({'ft': ft, 'mm': mm, 'beam_bottom_mm': lo, 'beam_top_mm': hi,
                     'beam_height_mm': hi - lo, 'sees_floor': lo <= 0})
    return {'mount_h_mm': mount_h_mm, 'fov_v_deg': fov_v_deg,
            'down_tilt_deg': down_tilt_deg, 'floor_strike_mm': floor_strike,
            'at_distance': rows}


def target_visible(mount_h_mm, fov_v_deg, down_tilt_deg, target, distance_mm):
    """Does any part of the target fall inside the vertical beam at this distance?"""
    half = fov_v_deg / 2.0
    beam_lo = mount_h_mm + distance_mm * math.tan(math.radians(-half - down_tilt_deg))
    beam_hi = mount_h_mm + distance_mm * math.tan(math.radians(+half - down_tilt_deg))
    t_lo = target['floor_gap_mm']
    t_hi = target['floor_gap_mm'] + target['height_mm']
    overlap = max(0.0, min(beam_hi, t_hi) - max(beam_lo, t_lo))
    return {'visible': overlap > 0, 'overlap_mm': overlap,
            'fraction_of_target': overlap / target['height_mm'] if target['height_mm'] else 0.0,
            'beam_bottom_mm': beam_lo, 'beam_top_mm': beam_hi}


def stopping_distance_mm(speed_mm_s, sensor_latency_s, compute_latency_s, decel_mm_s2):
    """Distance covered from the obstacle entering the beam to a full stop."""
    reaction = speed_mm_s * (sensor_latency_s + compute_latency_s)
    braking = (speed_mm_s ** 2) / (2.0 * decel_mm_s2)
    return {'reaction_mm': reaction, 'braking_mm': braking,
            'total_mm': reaction + braking, 'total_ft': (reaction + braking) / FT}


def main():
    data = {
        'generated_for': '350 mm square or 350 mm round mobile robot',
        'mm_per_ft': FT,
        'survey_distances_ft': DISTANCES_FT,
        'survey_distances_mm': DISTANCES_MM,
        'platform': PLATFORM,
        'targets': TARGETS,
    }

    # --- beam width at each survey distance, per FoV -------------------------
    data['beam_width'] = []
    for fov in FOVS:
        row = {'fov_deg': fov, 'widths': {}}
        for ft, mm in zip(DISTANCES_FT, DISTANCES_MM):
            w = beam_width_mm(fov, mm)
            row['widths']['%dft' % ft] = {
                'mm': None if math.isinf(w) else round(w, 1),
                'in': None if math.isinf(w) else round(w / 25.4, 1)}
        data['beam_width'].append(row)

    # --- single-zone footprint for the grid imagers --------------------------
    GRIDS = [('VL53L5CX / VL53L8CX 4x4', 63, 4), ('VL53L5CX / VL53L8CX 8x8', 63, 8),
             ('VL53L7CX 4x4', 90, 4), ('VL53L7CX 8x8', 90, 8),
             ('AMG8833 Grid-EYE 8x8', 60, 8),
             ('MLX90640 32x24 (55 deg)', 55, 32), ('MLX90640 32x24 (110 deg)', 110, 32),
             ('MLX90641 16x12 (55 deg)', 55, 16),
             ('TMF8821 3x3', 33, 3), ('TMF8821 4x4', 44, 4)]
    data['zone_footprint'] = []
    for label, fov, n in GRIDS:
        row = {'sensor': label, 'fov_deg': fov, 'zones_across': n, 'centre_zone': {}}
        for ft, mm in zip(DISTANCES_FT, DISTANCES_MM):
            z = zone_width_mm(fov, mm, n)
            cell = {'mm': round(z, 1), 'in': round(z / 25.4, 2)}
            for tname, t in TARGETS.items():
                cell['zones_across_' + tname] = round(t['width_mm'] / z, 2)
            row['centre_zone']['%dft' % ft] = cell
        data['zone_footprint'].append(row)

    # --- ring count for 360 degree closure -----------------------------------
    data['ring_count'] = []
    for fov in FOVS:
        data['ring_count'].append({
            'fov_deg': fov,
            'no_overlap': ring_count(fov, 0),
            'overlap_5deg': ring_count(fov, 5),
            'overlap_10deg': ring_count(fov, 10),
            'overlap_25pct': ring_count(fov, fov * 0.25),
        })

    # --- blind wedge between adjacent sensors on the ring --------------------
    data['blind_wedge'] = []
    for n in [3, 4, 5, 6, 8, 10, 12, 16]:
        for fov in [15, 25, 27, 45, 63, 65, 90, 100, 120]:
            b = blind_wedge_range_mm(n, fov, PLATFORM['round']['radius'])
            data['blind_wedge'].append({
                'n_sensors': n, 'fov_deg': fov,
                'total_angular_coverage_deg': n * fov,
                'angular_spacing_deg': round(360.0 / n, 1),
                'closes': b['closes'],
                'coverage_closes_from_edge_mm': (None if not b['closes']
                                                 else round(b['from_edge_mm'], 1)),
                'coverage_closes_from_edge_in': (None if not b['closes']
                                                 else round(b['from_edge_mm'] / 25.4, 1)),
                'closes_at_platform_surface': b['closes_at_surface'],
            })

    # --- vertical coverage ---------------------------------------------------
    data['vertical'] = []
    WATCH = ['adult_human_standing', 'adult_human_leg', 'toddler', 'large_dog',
             'small_dog', 'cat', 'cat_lying', 'power_cable', 'table_top']
    for h in [60, 100, 150, 200, 300, 400, 600, 800, 1000]:
        for fov_v in [15, 25, 27, 45, 63, 65, 90]:
            for tilt in [0, 5, 10, 15]:
                v = vertical_intercept(h, fov_v, tilt)
                entry = {'mount_h_mm': h, 'fov_v_deg': fov_v, 'down_tilt_deg': tilt,
                         'floor_strike_mm': (None if v['floor_strike_mm'] is None
                                             else round(v['floor_strike_mm'], 1)),
                         'targets': {}}
                for tname in WATCH:
                    t = TARGETS[tname]
                    entry['targets'][tname] = {}
                    for ft, mm in zip(DISTANCES_FT, DISTANCES_MM):
                        r = target_visible(h, fov_v, tilt, t, mm)
                        entry['targets'][tname]['%dft' % ft] = {
                            'visible': r['visible'],
                            'fraction': round(r['fraction_of_target'], 3)}
                data['vertical'].append(entry)

    # --- stopping distance ---------------------------------------------------
    data['stopping'] = []
    SENSORS = [('VL53L1X single zone @ 50 Hz', 50),
               ('VL53L5CX 4x4 @ 60 Hz', 60),
               ('VL53L5CX 8x8 @ 15 Hz', 15),
               ('VL53L8CX 8x8 @ 15 Hz', 15),
               ('typical 24 GHz mmWave @ 10 Hz', 10),
               ('AMG8833 thermal @ 10 Hz', 10),
               ('AMG8833 thermal @ 1 Hz', 1),
               ('MLX90640 32x24 @ 8 Hz', 8),
               ('RPLIDAR A1 full scan @ 5.5 Hz', 5.5)]
    for speed_ms in [0.2, 0.3, 0.5, 0.8, 1.0]:
        for sensor_label, hz in SENSORS:
            for decel_g, decel_label in [(0.25, 'gentle 0.25 g'), (0.5, 'firm 0.5 g')]:
                s = stopping_distance_mm(speed_ms * 1000.0, 1.0 / hz, 0.030,
                                         decel_g * 9810.0)
                data['stopping'].append({
                    'speed_m_s': speed_ms, 'sensor': sensor_label, 'sensor_hz': hz,
                    'sensor_latency_ms': round(1000.0 / hz, 1),
                    'compute_latency_ms': 30.0, 'decel': decel_label,
                    'reaction_mm': round(s['reaction_mm'], 1),
                    'braking_mm': round(s['braking_mm'], 1),
                    'total_mm': round(s['total_mm'], 1),
                    'total_in': round(s['total_mm'] / 25.4, 1),
                })

    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(data, indent=1), encoding='utf-8')
    print('wrote %s (%d bytes)' % (OUT, OUT.stat().st_size))

    print('\nbeam width in mm by field of view and distance')
    print('fov     1ft    3ft    5ft    8ft   10ft')
    for row in data['beam_width']:
        w = row['widths']
        cells = []
        for f in DISTANCES_FT:
            v = w['%dft' % f]['mm']
            cells.append('inf' if v is None else str(round(v)))
        print('{:>3}  {:>6} {:>6} {:>6} {:>6} {:>6}'.format(row['fov_deg'], *cells))

    print('\nsensors needed to close 360 degrees')
    print('fov  none  +5deg +10deg  +25pct')
    for row in data['ring_count']:
        print('{:>3}  {:>4}  {:>5}  {:>5}  {:>6}'.format(
            row['fov_deg'], row['no_overlap'] or 0, row['overlap_5deg'] or 0,
            row['overlap_10deg'] or 0, row['overlap_25pct'] or 0))

    print('\nrange from the platform edge at which a ring closes its blind wedges (mm)')
    print('"never" = n*fov < 360, so the wedge stays open at every range')
    print(' n     15    25    27    45    63    65    90   100   120')
    for n in [3, 4, 5, 6, 8, 10, 12, 16]:
        cells = []
        for fov in [15, 25, 27, 45, 63, 65, 90, 100, 120]:
            m = [b for b in data['blind_wedge']
                 if b['n_sensors'] == n and b['fov_deg'] == fov][0]
            if not m['closes']:
                cells.append('never')
            elif m['closes_at_platform_surface']:
                cells.append('0')
            else:
                cells.append(str(round(m['coverage_closes_from_edge_mm'])))
        print('{:>2}  {:>5} {:>5} {:>5} {:>5} {:>5} {:>5} {:>5} {:>5} {:>5}'.format(n, *cells))

    print('\nvertical reach: can a 250 mm standing cat be seen at all?')
    print('(mount height / vertical FoV / down-tilt, cat visible at 1/3/5/8/10 ft)')
    for h in [100, 200, 400, 800]:
        for fov_v in [25, 45, 63, 90]:
            for tilt in [0, 15]:
                e = [x for x in data['vertical'] if x['mount_h_mm'] == h
                     and x['fov_v_deg'] == fov_v and x['down_tilt_deg'] == tilt][0]
                flags = ''.join('Y' if e['targets']['cat']['%dft' % f]['visible'] else '.'
                                for f in DISTANCES_FT)
                print('  h={:>4} fov_v={:>2} tilt={:>2}  cat {}   floor strike {} mm'.format(
                    h, fov_v, tilt, flags,
                    '-' if e['floor_strike_mm'] is None else round(e['floor_strike_mm'])))


if __name__ == '__main__':
    main()
