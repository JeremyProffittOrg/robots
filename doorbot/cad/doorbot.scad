// doorbot top level. One file selects every printable part and every view, so the exporter,
// the drawings and the video all read the same geometry.
//
//   openscad -D part="base_shell"  -o ../stl/base_shell.stl doorbot.scad
//   openscad -D part="assembly"    -o ../cad/assembly.png   doorbot.scad
//
// part = base_shell | base_cover | motor_pinion | compound_gear | drum_gear | door_anchor
//        | magnet_pod | assembly | exploded | section | installed

include <lib.scad>
use <base.scad>
use <drive.scad>
use <mounts.scad>

part = "assembly";
explode = 0;            // 0 = assembled, 1 = fully exploded
door_deg = 0;           // door angle for the installed view

// ---------------------------------------------------------------- placement in the unit frame
module at_drum(z) { translate([drum_axis[0], drum_axis[1], z]) children(); }
module at_compound(z) { translate([compound_axis[0], compound_axis[1], z]) children(); }
module at_motor(z) { translate([motor_axis[0], motor_axis[1], z]) children(); }

module motor_stand_in() {
    color("#4b5563") at_motor(motor_z) {
        translate([-tt_body_w / 2, -tt_axis_from_gearbox_end, 0])
            cube([tt_body_w, tt_body_l, tt_body_h]);
        translate([0, 0, -tt_shaft_len]) cyl(tt_shaft_d, tt_shaft_len + tt_body_h + tt_shaft_len);
    }
}

module board_stand_in(pos, w, l, t, c = "#166534") {
    color(c) translate([pos[0], pos[1], pos[2]]) cube([w, l, t]);
}

module dowel(pos) {
    color("#9ca3af") translate([pos[0], pos[1], 0]) cyl(pin_d, base_z - 1);
}

module assembly_core(e = 0) {
    color("#e2e8f0") base_shell();
    translate([0, 0, e * 190]) color("#cbd5e1") base_cover();
    translate([0, 0, e * 60]) motor_stand_in();
    translate([0, 0, e * 120]) color("#b45309") at_motor(plane1_z) motor_pinion();
    translate([0, 0, e * 145]) color("#0369a1") at_compound(plane1_z) compound_gear();
    translate([0, 0, e * 95]) color("#7c3aed") at_drum(drum_z) drum_gear();
    translate([0, 0, e * 165]) { dowel(drum_axis); dowel(compound_axis); }
    translate([0, 0, e * 40]) {
        board_stand_in(tdisp_pos, tdisp_w, tdisp_l, tdisp_t, "#111827");
        board_stand_in(drv_pos, drv_w, drv_l, drv_t);
        board_stand_in(accel_pos, accel_w, accel_l, accel_t);
        board_stand_in(tof_wave_pos, tof_w, tof_l, tof_t, "#1d4ed8");
        board_stand_in(tof_guard_pos, tof_w, tof_l, tof_t, "#1d4ed8");
    }
}

// ---------------------------------------------------------------- views
module view_assembly() { assembly_core(0); }

module view_exploded() {
    assembly_core(1);
    translate([-95, 10, 0]) color("#b45309") door_anchor();
    translate([-95, 70, 0]) color("#be123c") magnet_pod();
    translate([-95, 100, 0]) color("#be123c") magnet_pod();
}

module view_section() {
    difference() {
        assembly_core(0);
        translate([-1, base_h / 2, -1]) cube([base_w + 2, base_h, base_z + 30]);
    }
}

// A plan view of the installed machine, looking down on the doorway. Door frame, not unit
// frame: +x along the closed door into the opening, +y the push side.
module view_installed() {
    a_r = sqrt(anchor_a * anchor_a + anchor_standoff * anchor_standoff);
    phi = atan2(anchor_standoff, anchor_a);
    ax = a_r * cos(phi - door_deg);
    ay = a_r * sin(phi - door_deg);
    // leaf, drawn to 420 mm so the plan view stays readable at the hinge end
    leaf = 420;
    color("#a16207") rotate([0, 0, -door_deg])
        translate([0, -door_thick_mm, 0]) cube([leaf, door_thick_mm, 8]);
    // hinge jamb and the wall behind it
    color("#d6d3d1") translate([-90, -40, 0]) cube([90, 130, 8]);
    color("#a8a29e") translate([-6, -40, 0]) cube([6, 90, 12]);
    // the unit, standing in the rebate on the push side
    color("#e2e8f0") translate([0, 0, 0]) cube([base_z, base_w, 10]);
    color("#cbd5e1") translate([base_z, nose_x - nose_w / 2, 0]) cube([nose_l, nose_w, 10]);
    // the cable, exit to anchor
    hull() {
        translate([exit_x, exit_y, 4]) cyl(2, 3);
        translate([ax, ay, 4]) cyl(2, 3);
    }
    // the anchor on the leaf
    color("#b45309") translate([ax, ay, 0]) cyl(10, 10);
    // the hinge axis itself, for orientation
    color("#1f2937") cyl(6, 14);
}

// ---------------------------------------------------------------- dispatch
if (part == "base_shell") base_shell();
else if (part == "base_cover") base_cover();
else if (part == "motor_pinion") motor_pinion();
else if (part == "compound_gear") compound_gear();
else if (part == "drum_gear") drum_gear();
else if (part == "door_anchor") door_anchor();
else if (part == "magnet_pod") magnet_pod();
else if (part == "assembly") view_assembly();
else if (part == "exploded") view_exploded();
else if (part == "section") view_section();
else if (part == "installed") view_installed();
else assert(false, str("unknown part: ", part));
