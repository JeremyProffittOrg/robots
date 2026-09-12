// Shared helpers for the fable-r2d2 CAD. OpenSCAD 2021.01 compatible (no manifold-only syntax).
// Units: mm. Z up. Every printable part module places its print bed on z=0.

eps = 0.01;

// Rounded box centred in XY with base on z=0.
module rbox(size, r=3, center_z=false) {
    x = size[0]; y = size[1]; z = size[2];
    translate([0, 0, center_z ? -z/2 : 0])
    linear_extrude(height=z)
        offset(r=r) offset(delta=-r) square([x, y], center=true);
}

// Rounded rectangle in 2D, centred.
module rrect(x, y, r=3) { offset(r=r) offset(delta=-r) square([x, y], center=true); }

// Cylinder with base on z=0 unless center=true; d is diameter.
module cyl(d, h, center=false, fn=0) {
    cylinder(d=d, h=h, center=center, $fn = fn > 0 ? fn : max(24, ceil(d*1.2)));
}

// Through hole for a metric screw with clearance (ISO medium fit).
function clearance_d(m) = m == 3 ? 3.4 : m == 4 ? 4.5 : m == 5 ? 5.5 : m == 6 ? 6.6 : m == 8 ? 9.0 : m == 10 ? 11.0 : m == 12 ? 13.0 : m + 1;
// Heat-set insert pilot hole diameters (brass inserts, typical M3 4.0 / M4 5.6 / M5 6.4 / M6 8.0).
function insert_d(m) = m == 3 ? 4.0 : m == 4 ? 5.6 : m == 5 ? 6.4 : m == 6 ? 8.0 : m + 1.2;
function insert_depth(m) = m == 3 ? 6 : m == 4 ? 8 : m == 5 ? 9.5 : m == 6 ? 12 : m * 2;
// Nut pocket across-flats (ISO 4032) + clearance.
function nut_af(m) = (m == 3 ? 5.5 : m == 4 ? 7 : m == 5 ? 8 : m == 6 ? 10 : m == 8 ? 13 : m == 10 ? 17 : m == 12 ? 19 : m * 1.7) + 0.4;
function nut_h(m) = m == 3 ? 2.4 : m == 4 ? 3.2 : m == 5 ? 4.7 : m == 6 ? 5.2 : m == 8 ? 6.8 : m == 10 ? 8.4 : m == 12 ? 10.8 : m;

module through_hole(m, h) { translate([0, 0, -eps]) cyl(clearance_d(m), h + 2*eps); }
module insert_hole(m, h=0) { translate([0, 0, -eps]) cyl(insert_d(m), (h > 0 ? h : insert_depth(m)) + 2*eps); }
module nut_pocket(m, h=0) { translate([0, 0, -eps]) cylinder(d=nut_af(m)/cos(30), h=(h > 0 ? h : nut_h(m)) + 2*eps, $fn=6); }

// Hex nut trap with a slot to slide the nut in from +X.
module nut_slot(m, slot_len, h=0) {
    hh = h > 0 ? h : nut_h(m) + 0.4;
    translate([0, 0, -eps]) {
        cylinder(d=nut_af(m)/cos(30), h=hh + 2*eps, $fn=6);
        translate([0, -nut_af(m)/2, 0]) cube([slot_len, nut_af(m), hh + 2*eps]);
    }
}

// Adafruit 3777 TT motor envelope (from the manufacturer drawing): 70 long along +X from the
// rear of the motor can; gearbox 22.44 tall (Y here is thickness 18.6), shaft axis at X=59.9?
// The drawing places the axle 11.25 mm from the gearbox front face and the gearbox is 37 mm
// long; overall 70. Origin: shaft axis, motor body extends toward -X.
// Shaft: 5.4 mm D with 3.7 flat; 9.3 mm one side, 8.7 mm other side (36.6 tip span).
tt_len = 70; tt_gear_len = 37; tt_gear_h = 22.44; tt_thick = 18.6; tt_shaft_d = 5.4;
tt_axle_from_front = 11.25; tt_can_d = 20.4; tt_shaft_l1 = 9.3; tt_shaft_l2 = 8.7;
tt_hole_spacing = 17.6;  // two 3.0 mm holes through the gearbox, 11.3 / 11.25 from the axle
module tt_motor(clear=0) {
    // shaft axis along Y at origin; gearbox front face at x=+tt_axle_from_front
    c = clear;
    // gearbox block
    translate([tt_axle_from_front - tt_gear_len - c, -tt_thick/2 - c, -tt_gear_h/2 - c])
        cube([tt_gear_len + 2*c, tt_thick + 2*c, tt_gear_h + 2*c]);
    // motor can
    translate([tt_axle_from_front - tt_gear_len - c, 0, 0]) rotate([0, -90, 0])
        cyl(tt_can_d + 2*c, tt_len - tt_gear_len + c);
    // shafts
    translate([0, -tt_thick/2 - tt_shaft_l1 - c, 0]) rotate([-90, 0, 0]) cyl(tt_shaft_d + 2*c, tt_shaft_l1 + tt_thick + tt_shaft_l2 + 2*c);
    // strap/tab at the can end
    translate([tt_axle_from_front - tt_len - 4.8 - c, -4 - c, -3 - c]) cube([6 + 2*c, 8 + 2*c, 6 + 2*c]);
}

// Adafruit 3766 wheel envelope: 63 mm diameter, 29 mm wide, axis along Y, centred.
wheel_d = 63; wheel_w = 29;
module tt_wheel(clear=0) { rotate([90, 0, 0]) cyl(wheel_d + 2*clear, wheel_w + 2*clear, center=true); }

// Ribbed reinforcement: vertical fins between two radii, n around, on z=0.
module radial_ribs(n, r_in, r_out, h, t=3, start=0) {
    for (i = [0 : n-1]) rotate([0, 0, start + i*360/n])
        translate([r_in, -t/2, 0]) cube([r_out - r_in, t, h]);
}

// Ring (annulus) with base on z=0.
module ring(d_out, d_in, h, fn=180) {
    difference() { cylinder(d=d_out, h=h, $fn=fn); translate([0, 0, -eps]) cylinder(d=d_in, h=h + 2*eps, $fn=fn); }
}

// Countersunk/counterbored screw hole from top face at z=h going down.
module cbore_hole(m, h, head_d, head_h) {
    translate([0, 0, -eps]) cyl(clearance_d(m), h + 2*eps);
    translate([0, 0, h - head_h]) cyl(head_d, head_h + eps);
}

// Text label recessed 0.6 mm into a top face (for part identification).
module label(t, size=6, depth=0.6) {
    translate([0, 0, -depth]) linear_extrude(depth + eps) text(t, size=size, halign="center", valign="center", font="Arial:style=Bold");
}
