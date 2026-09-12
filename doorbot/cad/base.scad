// doorbot base unit: the unibody shell and its cover.
// Print frame = unit frame: X across the jamb depth, Y vertical, Z out into the opening.
// The shell prints open-face-up with its mounting face on the bed: no supports anywhere, and
// every load path (cable chute, nose, pin bosses, jamb screws) runs in the layer plane.

include <lib.scad>

// ---------------------------------------------------------------- shared cut-outs
module pin_boss(pos, h) {
    translate([pos[0], pos[1], floor_t - eps]) difference() {
        cyl(gear_hub_d + 3, h);
        translate([0, 0, -eps]) cyl(pin_d - 0.1, h + 1);     // press fit for the steel dowel
    }
}

module motor_pocket(clear = 0.5) {
    // Body, plus the cradle mouth above it so the motor drops in from the open face.
    translate([motor_axis[0] - tt_body_w / 2 - clear,
               motor_axis[1] - tt_axis_from_gearbox_end - clear, motor_z])
        cube([tt_body_w + 2 * clear, tt_body_l + 2 * clear, base_z]);
    // Both shafts.
    translate([motor_axis[0], motor_axis[1], 0]) cyl(tt_shaft_d + 3, base_z + 1);
    // Lead exit towards the driver board.
    translate([motor_axis[0] - 4, motor_axis[1] + tt_body_l - 14, motor_z + 4])
        cube([8, 12, 10]);
}

module board_pocket(pos, w, l, t, clear = 0.6) {
    translate([pos[0] - clear, pos[1] - clear, pos[2]])
        cube([w + 2 * clear, l + 2 * clear, t + base_z]);
}

// The cable channel: drum tangent, up through the shell, out through the nose.
module cable_chute() {
    r = chute_d / 2;
    path = [[drum_axis[0] + drum_flange_d / 2 - 1, drum_axis[1], drum_z + drum_width / 2],
            [nose_x - 2, nose_y + 6, drum_z + drum_width / 2],
            [nose_x, nose_y, drum_z + drum_width / 2 + 2],
            [nose_x, nose_y, base_z + nose_l + 1]];
    for (i = [0 : len(path) - 2])
        hull() {
            translate(path[i]) sphere(r = r, $fn = 24);
            translate(path[i + 1]) sphere(r = r, $fn = 24);
        }
}

// ---------------------------------------------------------------- the shell
module base_shell() {
    difference() {
        union() {
            rbox_corner([base_w, base_h, base_z], r = 4);
            // Integral nose: a solid corner column that carries the cable exit out past the
            // cover. It is rooted all the way to the floor and to both outer walls, in the
            // one corner of the cavity no wheel ever sweeps, so the 151 N at its tip goes
            // straight into the shell and the jamb screws.
            translate([nose_x - nose_w / 2, 0, 0])
                cube([nose_w + (base_w - nose_x - nose_w / 2), nose_y + nose_h / 2, base_z]);
            translate([nose_x - nose_w / 2, nose_y - nose_h / 2, base_z - eps])
                rbox_corner([nose_w, nose_h, nose_l], r = 4);
        }

        // main cavity, minus the nose corner so that column stays solid
        difference() {
            translate([wall, wall, floor_t])
                rbox_corner([base_w - 2 * wall, base_h - 2 * wall, base_z], r = 2);
            translate([nose_x - nose_w / 2 - 1, -1, floor_t - 1])
                cube([base_w, nose_y + nose_h / 2 + 1, base_z + 2]);
        }
        // cover lip: a ledge the cover drops into
        translate([wall - cover_lip, wall - cover_lip, base_z - cover_t])
            rbox_corner([base_w - 2 * (wall - cover_lip), base_h - 2 * (wall - cover_lip),
                         cover_t + eps], r = 2);

        motor_pocket();
        board_pocket(tdisp_pos, tdisp_w, tdisp_l, tdisp_t);
        board_pocket(drv_pos, drv_w, drv_l, drv_t);
        board_pocket(accel_pos, accel_w, accel_l, accel_t);
        board_pocket(tof_wave_pos, tof_w, tof_l, tof_t);
        board_pocket(tof_guard_pos, tof_w, tof_l, tof_t);
        translate([buzzer_pos[0], buzzer_pos[1], buzzer_pos[2]]) cyl(buzzer_d + 0.6, base_z);

        // No local gear sweeps are cut: every wheel already clears the plain cavity, which
        // is checked by scripts/check_cad.py. Cutting them was what removed the floor under
        // the pin bosses.
        // encoder wheel on the free front shaft
        translate([motor_axis[0], motor_axis[1], motor_z + tt_body_h])
            cyl(encoder_wheel_d + 2, base_z);
        // slot sensor straddling it
        translate([motor_axis[0] - encoder_slot_w / 2 - 0.5,
                   motor_axis[1] + encoder_wheel_d / 2 - 4, base_z - encoder_slot_t - 2])
            cube([encoder_slot_w + 1, encoder_slot_l + 1, encoder_slot_t + 3]);

        cable_chute();

        // jamb mounting screws, counterbored so the heads sit below the gear planes
        for (y = mount_y) translate([base_w - 9, y, 0]) {
            through_hole(mount_screw_d, floor_t);
            translate([0, 0, floor_t - eps]) cyl(9.5, 2.6);
        }
        // USB-C cable slot, bottom wall
        translate([base_w / 2 - usb_slot_w / 2, -eps, floor_t + 3])
            cube([usb_slot_w, wall + 2 * eps, usb_slot_h]);
        // vent slots behind the motor
        for (i = [0 : 3]) translate([6 + 10 * i, 70 + 45, -eps]) cube([4, 16, floor_t + 2 * eps]);
    }

    // things that stand up inside the cavity
    pin_boss(drum_axis, plane1_z);
    pin_boss(compound_axis, plane1_z);
    // motor cradle ribs
    for (s = [-1, 1])
        translate([motor_axis[0] + s * (tt_body_w / 2 + 1.4),
                   motor_axis[1] - tt_axis_from_gearbox_end, floor_t])
            cube([2.8, tt_body_l, motor_z - floor_t], center = false);
    // cover screw bosses
    for (p = cover_boss_xy())
        translate([p[0], p[1], floor_t - eps]) tap_boss(base_z - floor_t - cover_t);
    // sensor shelf: two full-width ribs off the floor with a plate bridging between them,
    // so both time-of-flight boards sit right behind the cover with nothing below to foul.
    difference() {
        union() {
            for (y = [shelf_y0, shelf_y1 - shelf_t])
                translate([wall, y, floor_t - eps]) cube([base_w - 2 * wall, shelf_t, shelf_z]);
            translate([wall, shelf_y0, shelf_z]) cube([base_w - 2 * wall, shelf_y1 - shelf_y0, shelf_t]);
        }
        for (p = [tof_wave_pos, tof_guard_pos])
            translate([p[0] + tof_w / 2, p[1] + tof_l / 2, shelf_z - eps])
                cyl(window_d + 3, shelf_t + 2 * eps);
    }
    // board tapping bosses
    for (p = board_boss_xy()) translate([p[0], p[1], p[2]]) tap_boss(p[3], 7.0, m3_tap_d);
}

function cover_boss_xy() = [[8, 8], [base_w - 8, 8], [8, base_h - 8], [base_w - 8, base_h - 8]];

function board_boss_xy() = [
    [tdisp_pos[0] + 3, tdisp_pos[1] + 3, floor_t - eps, tdisp_pos[2] - floor_t],
    [tdisp_pos[0] + tdisp_w - 3, tdisp_pos[1] + tdisp_l - 3, floor_t - eps, tdisp_pos[2] - floor_t],
    [tof_wave_pos[0] + tof_w / 2 - tof_hole_w / 2, tof_wave_pos[1] + tof_l / 2 - tof_hole_l / 2,
     shelf_z + shelf_t - eps, tof_wave_pos[2] - shelf_z - shelf_t],
    [tof_wave_pos[0] + tof_w / 2 + tof_hole_w / 2, tof_wave_pos[1] + tof_l / 2 + tof_hole_l / 2,
     shelf_z + shelf_t - eps, tof_wave_pos[2] - shelf_z - shelf_t],
    [tof_guard_pos[0] + tof_w / 2 - tof_hole_w / 2, tof_guard_pos[1] + tof_l / 2 - tof_hole_l / 2,
     shelf_z + shelf_t - eps, tof_guard_pos[2] - shelf_z - shelf_t],
    [tof_guard_pos[0] + tof_w / 2 + tof_hole_w / 2, tof_guard_pos[1] + tof_l / 2 + tof_hole_l / 2,
     shelf_z + shelf_t - eps, tof_guard_pos[2] - shelf_z - shelf_t]];

// ---------------------------------------------------------------- the cover
module base_cover() {
    inner = [base_w - 2 * (wall - cover_lip), base_h - 2 * (wall - cover_lip)];
    difference() {
        union() {
            // plate
            translate([wall - cover_lip, wall - cover_lip, 0])
                rbox_corner([inner[0], inner[1], cover_t], r = 2);
            // rib that presses the motor into its cradle
            translate([motor_axis[0] - tt_body_w / 2,
                       motor_axis[1] - tt_axis_from_gearbox_end + 6, cover_t - eps])
                cube([tt_body_w, tt_body_l - 12, base_z - motor_z - tt_body_h - cover_t]);
            // dome over the encoder wheel and its slot sensor
            translate([motor_axis[0], motor_axis[1], cover_t - eps])
                cyl(encoder_dome_d, encoder_dome_h);
            // blind bosses that locate the top of each steel dowel
            for (a = [drum_axis, compound_axis])
                translate([a[0], a[1], cover_t - eps]) cyl(gear_hub_d, 4);
            // engraved ring around the hand-wave window
            translate([tof_wave_pos[0] + tof_w / 2, tof_wave_pos[1] + tof_l / 2, cover_t - eps])
                tube(wave_target_d + 3, wave_target_d, 1.2);
        }
        // display window
        translate([tdisp_pos[0] + tdisp_w / 2 - tdisp_screen_w / 2,
                   tdisp_pos[1] + tdisp_l / 2 - tdisp_screen_l / 2, -eps])
            cube([tdisp_screen_w, tdisp_screen_l, cover_t + 2 * eps]);
        // sensor windows
        for (p = [tof_wave_pos, tof_guard_pos])
            translate([p[0] + tof_w / 2, p[1] + tof_l / 2, -eps]) cyl(window_d, cover_t + 2 * eps);
        // dowel locating bores
        for (a = [drum_axis, compound_axis])
            translate([a[0], a[1], cover_t]) cyl(pin_d + 0.4, 4.2);
        // encoder wheel and slot-sensor pocket inside the dome
        translate([motor_axis[0], motor_axis[1], cover_t])
            cyl(encoder_wheel_d + 2, encoder_dome_h);
        translate([motor_axis[0] - encoder_slot_w / 2 - 0.5,
                   motor_axis[1] + encoder_wheel_d / 2 - 4, cover_t])
            cube([encoder_slot_w + 1, encoder_slot_l + 1, encoder_dome_h]);
        // cover screws
        for (p = cover_boss_xy())
            translate([p[0], p[1], 0]) countersink(m3_free_d, cover_t, 6.0);
        // buzzer grille
        for (i = [-1 : 1]) translate([buzzer_pos[0], buzzer_pos[1] + i * 3.5, -eps])
            cube([buzzer_d, 1.6, cover_t + 2 * eps], center = true);
    }
}
