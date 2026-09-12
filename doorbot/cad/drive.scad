// doorbot drive train: three printed rotating parts.
// All three print flat, gear axis along the print Z, so tooth loads and cable tension stay in
// the layer plane. Nothing here is cantilevered off a printed shaft: both compound parts run
// on 4 mm steel dowels.

include <lib.scad>

// ---------------------------------------------------------------- motor pinion
// 12T module 0.8, gripping the TT motor's double-D shaft. Printed flat, teeth in-plane.
module motor_pinion() {
    difference() {
        union() {
            spur_gear(module1, stage1_pinion_t, face1);
            cyl(gear_ro(module1, stage1_pinion_t) * 2 - 1.2, 1.2);   // stiffening skirt
        }
        translate([0, 0, -eps]) tt_shaft_bore(tt_shaft_len + 1);
        // grub-screw boss would need a nut; instead a slit that lets the D-bore clamp
        translate([-0.5, gear_rr(module1, stage1_pinion_t) - 2.4, 1.2]) cube([1.0, 4, face1]);
    }
}

// ---------------------------------------------------------------- compound gear
// 48T module 0.8 (stage-1 wheel) and 14T module 1.0 (stage-2 pinion) on one print.
module compound_gear() {
    h1 = face1;
    h2 = face2;
    difference() {
        union() {
            spur_gear(module1, stage1_gear_t, h1);
            translate([0, 0, h1]) cyl(gear_hub_d, plane2_z - plane1_z - h1 + eps);
            translate([0, 0, plane2_z - plane1_z]) spur_gear(module2, stage2_pinion_t, h2);
        }
        through_hole(pin_bore, plane2_z - plane1_z + h2 + 1);
        // lightening pockets in the big wheel, kept well clear of the tooth roots
        for (i = [0 : 5]) rotate([0, 0, i * 60])
            translate([gear_rp(module1, stage1_gear_t) * 0.55, 0, -eps])
                cyl(9, h1 - 1.2);
    }
}

// ---------------------------------------------------------------- drum gear
// 42T module 1.0 (stage-2 wheel) plus the grooved cable drum, on one print.
module drum_gear() {
    total = plane2_z - drum_z + face2;
    difference() {
        union() {
            // drum core and its two flanges
            cyl(drum_flange_d, 1.6);
            cyl(2 * drum_r, drum_width);
            translate([0, 0, drum_width - 1.6]) cyl(drum_flange_d, 1.6);
            translate([0, 0, plane2_z - drum_z]) spur_gear(module2, stage2_gear_t, face2);
            translate([0, 0, drum_width - eps]) cyl(gear_hub_d, plane2_z - drum_z - drum_width + eps);
        }
        through_hole(pin_bore, total + 1);
        // helical groove, one turn per drum_pitch, cut as a stack of rings
        for (i = [0 : floor((drum_width - 3.2) / drum_pitch)])
            translate([0, 0, 1.6 + 0.6 + i * drum_pitch])
                rotate_extrude($fn = 72)
                    translate([drum_r + cable_d / 2, 0, 0]) circle(d = cable_d + 0.3, $fn = 16);
        // cable dead-end: a radial hole through the core, then a knot pocket in the flange
        translate([0, 0, 2.6]) rotate([0, 90, 0]) cyl(cable_d + 0.6, drum_flange_d);
        translate([drum_r + 1.5, 0, 1.6]) cyl(4.5, 2.2);
        // lightening pockets in the wheel
        for (i = [0 : 5]) rotate([0, 0, i * 60 + 30])
            translate([gear_rp(module2, stage2_gear_t) * 0.55, 0, plane2_z - drum_z + 1.2])
                cyl(9, face2);
    }
}
