// fable-r2d2 — top-level CAD. Select a part with -D part="name" (see scripts/parts.json).
// part="assembly" places every part in the three-leg operating stance; "exploded" separates
// them; "section" cuts the assembly at X=0. Each printable part module sits on z=0 in its
// print orientation.
//
// FRAMES
//  Assembly frame: Z up, floor at z=0, +Y = droid front, +X = droid right.
//  Body frame: body cylinder axis is Z, origin at the skirt-bottom centre, +Y front. In the
//    three-leg stance the body frame is rotated body_tilt about X (top toward the rear) around
//    the shoulder axis, which sits shoulder_z above the body origin and shoulder_z_three_leg
//    above the floor.
//  body_lower print frame = body frame (z=0 at the skirt bottom).
//  body_upper print frame = body frame shifted down by body_lower_h (z=0 at the seam).
//  Dome frame: Z up the dome axis, z=0 at the band bottom edge, +Y front. Print frame = dome frame.
//  Leg native frame (right leg): shoulder pivot axis = X axis through the origin; Z up along
//    the leg (ankle pivot at z=-leg_len); +Y front; inboard face of the strut at x=0, outboard
//    toward +X. leg_upper_native()/leg_lower_native() are modelled here; the print modules
//    leg_upper()/leg_lower() lay them flat with the inboard face on the bed. The left leg is
//    the mirror image (mirror in the slicer).
//  Foot native frame: z=0 at the shell bottom edge (foot_clear above the floor), +Y front,
//    X across the foot, origin at the ankle slot centre (outer foot) or the foot centre
//    (centre foot). Print frame = native frame.
//  Centre leg native frame: Z up, origin on the caster pivot axis at the centre-foot top
//    plane (foot_clear + foot_center_h above the floor). The flange top is the plane
//    z = (skirt-bottom height above floor - that plane) - y*tan(body_tilt). leg_center() is the
//    print module (flange face down); leg_center_native() is used by the assembly.
//  Head drive native frame: origin on the body axis at the top face of the body top plate,
//    +Y front. head_drive() is the print module; head_drive_native() the assembly module.

include <params.scad>
include <lib.scad>
include <dome.scad>
include <body.scad>
include <legs.scad>
include <feet.scad>
include <head_drive.scad>

part = "assembly";

skirt_bottom_z_three_leg = shoulder_z_three_leg - shoulder_z * cos(body_tilt);   // 164.5
skirt_bottom_y_three_leg = shoulder_z * sin(body_tilt);                          // 97.0
ankle_y_three_leg = leg_len * sin(leg_lean);                                     // 116.2
center_foot_top_z = foot_clear + foot_center_h;                                  // 98.9

// ---------- placement helpers (assembly frame) ----------
module at_body() { translate([0, 0, shoulder_z_three_leg]) rotate([body_tilt, 0, 0]) translate([0, 0, -shoulder_z]) children(); }
module at_body_upper() { at_body() translate([0, 0, body_lower_h]) children(); }
module at_dome() { at_body() translate([0, 0, body_height + dome_gap]) rotate([0, 0, dome_spin]) children(); }
module at_leg(side) {
    translate([side * (body_r + shoulder_spacer), 0, shoulder_z_three_leg]) rotate([leg_lean, 0, 0])
        mirror([side < 0 ? 1 : 0, 0, 0]) children();
}
module at_foot(side) { translate([side * leg_offset_x, ankle_y_three_leg, foot_clear]) mirror([side < 0 ? 1 : 0, 0, 0]) children(); }
module at_center_leg() { translate([0, skirt_bottom_y_three_leg, center_foot_top_z]) children(); }
module at_center_foot() { translate([0, skirt_bottom_y_three_leg - caster_trail, foot_clear]) children(); }
module at_head_drive() { at_body() translate([0, 0, body_top_plate_z]) children(); }

// ---------- purchased-part envelopes for renders ----------
module wheels_and_motors(center = false) {
    // motor placement follows feet.scad (ft_motor_at, ft_motor_tilt_o, ft_phi_c_*)
    for (sy = [-1, 1]) {
        phi = center ? (sy > 0 ? ft_phi_c_front : ft_phi_c_rear) : sy * (90 + ft_motor_tilt_o);
        color("gold") ft_motor_at(sy * foot_axle_y, phi) tt_motor();
        for (x = [-wheel_x, wheel_x]) color("orange") translate([x, sy * foot_axle_y, wheel_axle_z]) rotate([0, 0, 90]) tt_wheel();
    }
}

module assembly(explode = 0) {
    e = explode;
    color("white") at_body() translate([0, 0, -e * 0.3]) body_lower();
    color("white") at_body_upper() translate([0, 0, e]) body_upper();
    color("silver") at_dome() translate([0, 0, e * 2.2]) dome();
    color("darkgray") at_head_drive() translate([0, 0, e * 1.6]) head_drive_native();
    for (s = [-1, 1]) {
        color("white") at_leg(s) translate([s * e * 0.8, 0, 0]) { leg_upper_native(); translate([0, 0, -e * 0.5]) leg_lower_native(); }
        color("white") at_foot(s) translate([s * e * 0.8, 0, -e * 0.5]) { foot_outer(); wheels_and_motors(); }
    }
    color("white") at_center_leg() translate([0, 0, -e * 0.8]) leg_center_native();
    color("white") at_center_foot() translate([0, 0, -e * 1.3]) { foot_center(); wheels_and_motors(true); }
}

if (part == "assembly") assembly();
else if (part == "exploded") assembly(explode = 120);
else if (part == "section") difference() { assembly(); translate([0, -2000, -100]) cube([4000, 4000, 4000]); }
else if (part == "dome") dome();
else if (part == "body_upper") body_upper();
else if (part == "body_lower") body_lower();
else if (part == "leg_upper") leg_upper();
else if (part == "leg_lower") leg_lower();
else if (part == "foot_outer") foot_outer();
else if (part == "leg_center") leg_center();
else if (part == "foot_center") foot_center();
else if (part == "head_drive") head_drive();
// interference checks: each must produce an empty (or exact contact-plane only) result
else if (part == "check_seam") at_body() intersection() { body_lower(); translate([0, 0, body_lower_h]) body_upper(); }
else if (part == "check_dome") intersection() { at_body_upper() body_upper(); at_dome() dome(); }
else if (part == "check_head_drive") intersection() { at_head_drive() head_drive_native(); union() { at_body_upper() body_upper(); at_dome() dome(); } }
else if (part == "check_shoulder") intersection() { at_body_upper() body_upper(); at_leg(1) leg_upper_native(); }
else if (part == "check_ankle") intersection() { at_leg(1) leg_lower_native(); at_foot(1) foot_outer(); }
else if (part == "check_leg_split") intersection() { at_leg(1) leg_upper_native(); at_leg(1) leg_lower_native(); }
else if (part == "check_center") intersection() { at_center_leg() leg_center_native(); union() { at_body() body_lower(); at_center_foot() foot_center(); } }
else echo(str("Unknown part: ", part));
