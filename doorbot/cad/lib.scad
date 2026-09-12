// Shared helpers for the doorbot CAD. OpenSCAD 2021.01 compatible - no manifold-only syntax.
// Units mm, and every printable part module puts its print bed on z = 0.

include <params.scad>

// ---------------------------------------------------------------- primitives
module rbox(size, r = 3) {
    linear_extrude(height = size[2])
        offset(r = r) offset(delta = -r) square([size[0], size[1]], center = true);
}

module rbox_corner(size, r = 3) {
    translate([size[0] / 2, size[1] / 2, 0]) rbox(size, r);
}

module cyl(d, h, center = false) {
    cylinder(d = d, h = h, center = center, $fn = max(24, ceil(d * 3)));
}

module tube(od, id, h) {
    difference() { cyl(od, h); translate([0, 0, -eps]) cyl(id, h + 2 * eps); }
}

// Screw features -------------------------------------------------------------
module through_hole(d, h) { translate([0, 0, -eps]) cyl(d, h + 2 * eps); }

module tap_boss(h, od = screw_boss_d, id = m3_tap_d) {
    difference() { cyl(od, h); translate([0, 0, 2]) cyl(id, h); }
}

module countersink(d, h, head_d) {
    translate([0, 0, -eps]) cyl(d, h + 2 * eps);
    translate([0, 0, h - head_d / 2 + eps]) cylinder(d1 = d, d2 = head_d, h = head_d / 2);
}

// A pocket for a PCB with its four mounting holes as tapping bosses.
module pcb_pocket(l, w, t, clear = 0.5) {
    translate([-clear, -clear, -eps]) cube([l + 2 * clear, w + 2 * clear, t + eps]);
}

// ---------------------------------------------------------------- involute spur gear
// Standard 20 degree involute, generated as one polygon so 2021.01 stays fast.
// The involute at radius r has polar angle t - atan(t) where t = sqrt((r/rb)^2 - 1) in radians.
function inv_ang(rb, r) = let (q = (r / rb) * (r / rb) - 1, t = q > 0 ? sqrt(q) : 0)
    (t - atan(t) * PI / 180) * 180 / PI;      // degrees

function gear_rp(m, n) = m * n / 2;
function gear_ro(m, n) = m * n / 2 + m;
function gear_rr(m, n) = m * n / 2 - m * (1 + gear_clearance);
function gear_rb(m, n) = gear_rp(m, n) * cos(gear_pa);

// Half the tooth's angular width at the pitch circle, after taking out the backlash.
function gear_half(m, n) = ((PI * m / 2 - gear_backlash) / 2) / gear_rp(m, n) * 180 / PI;

// One flank, root to tip, as a list of points. Below the base circle the flank runs radially,
// which is what an FDM tooth ends up as anyway.
function flank(m, n, steps = 9, sign = 1) = let (
    rb = gear_rb(m, n), rp = gear_rp(m, n), ro = gear_ro(m, n), rr = gear_rr(m, n),
    half = gear_half(m, n), ap = inv_ang(rb, rp)
) [ for (i = [0 : steps])
      let (r = rr + (ro - rr) * i / steps,
           a = half + ap - inv_ang(rb, max(r, rb)))
      [r * cos(sign * a), r * sin(sign * a)] ];

function gear_outline(m, n) = let (
    rr = gear_rr(m, n), half = gear_half(m, n), step = 360 / n,
    up = flank(m, n, 9, -1), down = flank(m, n, 9, 1)
) [ for (k = [0 : n - 1]) each
      [ for (p = up) [p[0] * cos(k * step) - p[1] * sin(k * step),
                      p[0] * sin(k * step) + p[1] * cos(k * step)],
        for (p = [for (i = [len(down) - 1 : -1 : 0]) down[i]])
                     [p[0] * cos(k * step) - p[1] * sin(k * step),
                      p[0] * sin(k * step) + p[1] * cos(k * step)],
        for (j = [1 : 4])
          let (a = k * step + half + (step - 2 * half) * j / 5)
          [rr * cos(a), rr * sin(a)] ] ];

module spur_gear(m, n, face, bore = 0, hub_d = 0, hub_h = 0) {
    difference() {
        union() {
            linear_extrude(height = face) polygon(gear_outline(m, n));
            if (hub_d > 0) cyl(hub_d, hub_h > 0 ? hub_h : face);
        }
        if (bore > 0) through_hole(bore, max(face, hub_h) + 1);
    }
}

// ---------------------------------------------------------------- TT motor envelope
// Body plus both shafts, origin on the output shaft axis, shaft along +z.
module tt_motor_envelope(clear = 0.4) {
    translate([-tt_body_w / 2 - clear, -tt_axis_from_gearbox_end - clear, 0])
        cube([tt_body_w + 2 * clear, tt_body_l + 2 * clear, tt_body_h + 2 * clear]);
    translate([0, 0, -tt_shaft_len - clear]) cyl(tt_shaft_d + 2 * clear, tt_shaft_len + clear);
    translate([0, 0, tt_body_h]) cyl(tt_shaft_d + 2 * clear, tt_shaft_len + clear);
}

// The double-D bore that grips the motor shaft.
module tt_shaft_bore(h, clear = 0.15) {
    intersection() {
        cyl(tt_shaft_d + 2 * clear, h);
        translate([-(tt_shaft_flat + 2 * clear) / 2, -tt_shaft_d, 0])
            cube([tt_shaft_flat + 2 * clear, tt_shaft_d * 2, h]);
    }
}

// ---------------------------------------------------------------- magnet pocket
// Pocket with a bridged cap: print pauses at full depth, magnet drops in, three layers close
// over it. No adhesive, and the magnet cannot walk out towards the steel it is attracted to.
module magnet_pocket() {
    // The working face is the pod's TOP face, so the cap goes on top: the printer pauses at
    // the pocket roof, the magnet drops in, and three layers bridge over it.
    translate([0, 0, pod_t - magnet_cap_t - magnet_t - 0.2]) cyl(magnet_pocket_d, magnet_t + 0.2);
}
