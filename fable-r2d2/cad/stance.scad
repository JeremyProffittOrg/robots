// fable-r2d2 revision D — stance mechanism: kinematics, the printed leg_carriage, the sensed
// shoulder lock and the purchased-part envelopes. Included by r2d2.scad after params.scad and
// lib.scad. Every local name carries the prefix st_ so it cannot collide with the part files.
// scripts/check_stance.py evaluates the same formulas from params.scad and proves the transition.
//
// KINEMATICS (body frame = r2d2.scad body frame; world = assembly frame)
//  Legs stay vertical: the shoulder axis is at world (y 0, z shoulder_z_two_leg = 481.4).
//  Stroke s moves the pitch-hinge axis H along the guide unit u = (0, sin a, -cos a), a =
//  st_guide_angle (forward-down):  H(s) = (0, st_hinge_y, st_hinge_z) + (s - st_s_two) u.
//  While H is above the floor-contact height the body is locked at tilt 0 and the centre foot
//  hangs. Past contact the body pitches about the shoulder so H stays at st_floor_hinge_z:
//     y sin t + w cos t = c,  w = H.z - shoulder_z,  c = st_floor_hinge_z - shoulder_z_two_leg
//     t = atan2(y, w) - acos(c / sqrt(y^2 + w^2))
//  The leg_center housing and the foot are always world-level: hanging, they rest on the heel
//  stop (foot CG behind the hinge); on the floor, the floor keeps them level.
//
// CARRIAGE FRAME (leg_carriage_native): origin on the hinge axis, X across, +Z up the guide
//  (-u), +Y = (0, cos a, sin a). Cheeks straddle the leg_center housing (|x| 41.65) and turn on
//  12 mm OD steel spacer tubes clamped to the housing by M8 x 35 bolts into captive nuts. The
//  cross-web (z 28..58) carries the P16 rod-eye pin (M4 x 45) at z st_eye_up; its underside is
//  the pitch-stop plane that the housing top touches at 0 deg (heel) and at st_toe_stop (toe).
//  Two LM12LUU bearings (z 80..137) ride the fixed 12 mm shafts at x +/-66, each clamped by a
//  slit and an M4 x 25 screw. The top frame (z 123..139) ties the sides round the actuator.
//
// LOCK FRAME (st_lock_frame(side)): origin at the pin-exit face centre, +X outward along the pin
//  (mirrored for the left side), Y = body Y, Z = body Z. The GN 412 flange sits in a pocket in
//  the land boss on the shoulder pad with its pin face flush (|x| 165.5, 1 mm from the leg face),
//  so the pin engages 5 mm. Knob underside at X -22 (seated). The SS-01GL lever rides the knob
//  underside at Z +11.5; the MG995 horn tip pin sits 1 mm off the knob underside at Z -12 and
//  pulls the pin 5.8 mm when the servo turns st_release_angle. Both are in pockets of an
//  integral lock block inside body_upper.

st_sa = sin(st_guide_angle); st_ca = cos(st_guide_angle);
function st_hinge_body(s) = [0, st_hinge_y + (s - st_s_two)*st_sa, st_hinge_z - (s - st_s_two)*st_ca];
function st_tilt(s) = let(h = st_hinge_body(s), y = h[1], w = h[2] - shoulder_z,
                          c = st_floor_hinge_z - shoulder_z_two_leg, R = sqrt(y*y + w*w))
                      (w >= c) ? 0 : atan2(y, w) - acos(c / R);
function st_rotx(t, p) = [p[0], p[1]*cos(t) - p[2]*sin(t), p[1]*sin(t) + p[2]*cos(t)];
function st_hinge_world(s) = [0, 0, shoulder_z_two_leg] + st_rotx(st_tilt(s), st_hinge_body(s) - [0, 0, shoulder_z]);
st_s_contact = st_s_two + st_stow_lift / st_ca;                         // 31.6 foot touches the floor
// fixed actuator eye in the body frame (the actuator is parallel to the guide)
st_act_a = st_hinge_body(st_s_two) + (st_eye_up + st_act_closed + st_s_two) * [0, -st_sa, st_ca];
st_lock_y = st_lock_r*cos(st_lock_angle);
st_lock_z = shoulder_z + st_lock_r*sin(st_lock_angle);
// servo release angle: rotate the horn tip st_release_pull + st_horn_rest_gap toward -X
st_horn_R = sqrt(st_horn_arm[0]*st_horn_arm[0] + st_horn_arm[1]*st_horn_arm[1]);
st_horn_d = atan2(st_horn_arm[1], st_horn_arm[0]);
st_release_angle = acos((st_horn_arm[0] - st_release_pull - st_horn_rest_gap) / st_horn_R) - st_horn_d;   // 16.3
st_horn_tip0 = [-22 + st_horn_rest_gap + st_horn_tip_r, -12];            // (X, Z) tip-pin centre at rest
st_servo_s = st_horn_tip0 - st_horn_arm;                                 // (X, Z) servo shaft
st_switch_xh = -22 + 8.8 + st_switch_ot;                                 // SS-01GL hole line X (lever pressed at X -22)

// ---------- placement ----------
module st_at_body(s) { translate([0, 0, shoulder_z_two_leg]) rotate([st_tilt(s), 0, 0]) translate([0, 0, -shoulder_z]) children(); }
module st_at_carriage(s) { st_at_body(s) translate(st_hinge_body(s)) rotate([st_guide_angle, 0, 0]) children(); }
module st_at_housing(s) { translate(st_hinge_world(s) - [0, 0, st_hinge_up]) children(); }
module st_at_center_foot(s, yaw = 0) { st_at_housing(s) rotate([0, 0, yaw]) translate([0, -caster_trail, -foot_center_h]) children(); }
// guide-aligned frame on the fixed shaft line / actuator line, t along -u from the stowed hinge
module st_guide_at(t, x = 0) { translate(st_hinge_body(st_s_two) + [x, -t*st_sa, t*st_ca]) rotate([st_guide_angle, 0, 0]) children(); }
module st_lock_frame(side) { translate([side*st_land_x, st_lock_y, st_lock_z]) mirror([side < 0 ? 1 : 0, 0, 0]) children(); }

// ============================================================================ LEG CARRIAGE (printed)
st_brg_wall_out = 19.5;          // bearing housing extends this far outboard of the shaft (clamp screw room)
module leg_carriage_native() {
    cx0 = st_cheek_in; cx1 = st_cheek_in + st_cheek_t;
    difference() {
        union() {
            for (sx = [-1, 1]) {
                // cheek: round end on the hinge, up to the top frame
                translate([sx > 0 ? cx0 : -cx1, 0, 0]) rotate([90, 0, 90]) linear_extrude(height = st_cheek_t)
                    hull() { circle(r = 15.5); translate([-21, 0]) square([36.5, st_top[1]]); }
                // bearing housing (flush with the -Y print face at y -21)
                translate([sx > 0 ? st_shaft_x - 15.5 : -st_shaft_x - st_brg_wall_out, -21, st_brg_t - 2])
                    cube([15.5 + st_brg_wall_out, 36.5, st_top[1] - st_brg_t + 2]);
            }
            translate([-cx0 - eps, -21, st_web[0]]) cube([2*cx0 + 2*eps, 36.5, st_web[1] - st_web[0]]);   // cross-web
            // top frame: front face flush with the carriage front (y +15.5) so the frame, which reaches
            // battery height at the three-leg end of the 30 deg guide, never passes the battery rear
            translate([-(st_shaft_x + st_brg_wall_out), -21, st_top[0]])
                cube([2*(st_shaft_x + st_brg_wall_out), 36.5, st_top[1] - st_top[0]]);
        }
        // hinge bores for the 12 mm OD spacer tubes
        for (sx = [-1, 1]) translate([sx > 0 ? cx0 - 1 : -cx1 - 1, 0, 0]) rotate([0, 90, 0]) cyl(12.4, st_cheek_t + 2, fn = 48);
        // rod-eye slot (open to the top of the web) and the M4 x 45 pin: head counterbore -X, nut pocket +X
        translate([-5, -16, st_eye_up - 8]) cube([10, 32, st_web[1] - st_eye_up + 9]);
        translate([-cx1 - 1, 0, st_eye_up]) rotate([0, 90, 0]) cyl(st_act_pin_d, 2*cx1 + 2, fn = 24);
        translate([-cx1 - 1, 0, st_eye_up]) rotate([0, 90, 0]) cyl(8.5, cx1 + 1 - 20, fn = 32);
        translate([20, 0, st_eye_up]) rotate([0, 90, 0]) cylinder(d = nut_af(4)/cos(30), h = cx1 - 19, $fn = 6);
        // actuator passage through the top frame
        translate([-(st_act_case[0]/2 + 2), -(st_act_case[1]/2 + 1), st_top[0] - 1]) cube([st_act_case[0] + 4, st_act_case[1] + 2, st_top[1] - st_top[0] + 2]);
        for (sx = [-1, 1]) translate([sx*st_shaft_x, 0, 0]) {
            translate([0, 0, st_brg_t]) cyl(st_brg[1] + 0.1, st_top[1], fn = 96);            // LM12LUU seat, bottom lip below
            translate([0, 0, -1]) cyl(st_brg[0] + 3, st_top[1] + 2, fn = 48);                 // shaft passage
            // clamp slit on the outboard wall and the M4 x 25 clamp screw across it
            translate([sx > 0 ? 9 : -st_brg_wall_out - 1, -0.75, st_brg_t]) cube([st_brg_wall_out - 8, 1.5, st_top[1]]);
            for (z = [st_brg_t + 12, st_brg_t + 37]) translate([sx*15.5, 0, z]) {    // both below the top frame (st_top[0])
                rotate([90, 0, 0]) cyl(clearance_d(4), 50, center = true, fn = 24);
                translate([0, 11.5, 0]) rotate([-90, 0, 0]) cyl(8, 10, fn = 32);
                translate([0, -11.5, 0]) rotate([90, 0, 0]) cylinder(d = nut_af(4)/cos(30), h = 10, $fn = 6);
            }
        }
        translate([0, -15.5, 100]) rotate([90, 0, 0]) label("LEG CARRIAGE", 4);
    }
}
// print: -Y face (the rear face) on the bed
module leg_carriage() { translate([0, 0, 21]) rotate([90, 0, 0]) leg_carriage_native(); }

// Swept envelopes of the carriage and the stowed-to-contact housing, in the body frame, used by
// body_lower to cut its floor, shelf and ribs. Travel s = 0 (actuator closed) .. 68 (bearing
// housing on the bottom shaft boss). 2 mm clearance.
st_s_hard_stop = st_s_two + (st_brg_t - 2 - st_shaft_boss_bot);          // bearing housings land on the bottom bosses
module st_carriage_sweep() {
    for (i = [0 : 2]) hull() for (s = [0, st_s_hard_stop])
        translate(st_hinge_body(s)) rotate([st_guide_angle, 0, 0]) st_carriage_env(i);
}
module st_carriage_env(i) {
    c = 2;
    if (i == 0) translate([-(st_cheek_in + st_cheek_t + c), -21 - c, -15.5 - c]) cube([2*(st_cheek_in + st_cheek_t + c), 36.5 + 2*c, st_brg_t + 15.5]);
    if (i == 1) translate([-(st_shaft_x + st_brg_wall_out + c), -21 - c, st_brg_t - 2 - c]) cube([2*(st_shaft_x + st_brg_wall_out + c), 36.5 + 2*c, st_top[1] - st_brg_t + 2 + 2*c]);
    if (i == 2) translate([-(st_shaft_x + st_brg_wall_out + c), -21 - c, st_top[0] - c]) cube([2*(st_shaft_x + st_brg_wall_out + c), 36.5 + 2*c, st_top[1] - st_top[0] + 2*c]);
}
// leg_center housing (world-level) from stow down past contact, with its pitch sweep
// (the housing stays level in the world, so in the body frame it turns by -tilt about the hinge)
module st_housing_sweep() {
    hull() for (s = [0, st_s_contact, st_s_contact + 4, st_s_contact + 10, st_s_contact + 18, st_s_three])
        translate(st_hinge_body(s)) rotate([-st_tilt(s), 0, 0]) translate([0, 0, -st_hinge_up])
            translate([-43.7, -34, lg_center_bottom_z - 2]) cube([87.4, 68, st_hinge_up + 55 - lg_center_bottom_z]);   // to 55 above the hinge (heel-stop lug)
}
// actuator case envelope (body-fixed) with 2 mm clearance
module st_act_case_env(c = 2) {
    translate(st_act_a) rotate([st_guide_angle, 0, 0]) translate([-st_act_case[0]/2 - c, -st_act_case[1]/2 - c, -st_act_case_t[1]]) cube([st_act_case[0] + 2*c, st_act_case[1] + 2*c, st_act_case_t[1] - st_act_case_t[0]]);
}

// ============================================================================ body_lower: fixed shafts
// Bottom boss (blind shaft seat, hard stop for the bearing housings) and top boss (open seat,
// M4 set screw in an M4 heat-set insert) tied to the skin by a sloped arm that stays outboard of
// the carriage (|x| > 88) and below the seam flange.
st_arm_wall_y = st_hinge_y - st_shaft_t[1]*st_sa;                          // arm meets the skin behind the top boss
st_arm_wall_x = sqrt(pow(body_r - body_wall - 1, 2) - st_arm_wall_y*st_arm_wall_y) - 6;   // params only: body.scad is included later
module st_shaft_bosses() {
    for (sx = [-1, 1]) {
        hull() {
            intersection() {
                st_guide_at(0, sx*st_shaft_x) cyl(24, st_shaft_boss_bot, fn = 64);
                translate([-200, -200, 0]) cube([400, 400, 200]);
            }
            translate([sx*st_shaft_x - 12, st_hinge_y - 20, 0]) cube([24, 22, floor_t]);
        }
        st_guide_at(st_shaft_boss_top, sx*st_shaft_x) cyl(24, st_shaft_t[1] - st_shaft_boss_top, fn = 64);
        hull() {
            st_guide_at(st_shaft_boss_top + 4, sx*st_shaft_x) translate([sx > 0 ? 10 : -26, -9, 0]) cube([16, 18, st_shaft_t[1] - st_shaft_boss_top - 4]);
            translate([sx > 0 ? st_arm_wall_x : -st_arm_wall_x - 6, st_arm_wall_y - 9, 100]) cube([6, 18, 12]);
        }
    }
}
module st_shaft_boss_cuts() {
    for (sx = [-1, 1]) {
        st_guide_at(st_shaft_t[0], sx*st_shaft_x) cyl(st_shaft_d + 0.05, st_shaft_t[1] - st_shaft_t[0] + 10, fn = 64);
        st_guide_at(st_shaft_t[1] - 8, sx*st_shaft_x) rotate([0, sx*90, 0]) translate([0, 0, 5.5]) cyl(insert_d(4), 8, fn = 32);
    }
}

// ============================================================================ body_upper: actuator mount
// The fixed eye is just below the integral deck: two cheeks hang from the deck underside, each
// continued by a rib under the deck, and the eye pin (M4 x 60) runs through both cheeks.
st_act_mount_x = [20, 28];
module st_act_mount() {
    assert(st_act_a[2] + st_act_eye_d/2 < bd_deck_bot + 1.5, "stance: actuator fixed eye must sit under the deck");
    for (sx = [-1, 1]) {
        translate([sx > 0 ? st_act_mount_x[0] : -st_act_mount_x[1], st_act_a[1] - 14, st_act_a[2] - 9])
            cube([st_act_mount_x[1] - st_act_mount_x[0], 28, bd_deck_bot - st_act_a[2] + 9 + eps]);
        translate([sx > 0 ? st_act_eye_w/2 + 0.25 : -st_act_mount_x[0] - eps, st_act_a[1], st_act_a[2]]) rotate([0, 90, 0])
            cyl(10, st_act_mount_x[0] - st_act_eye_w/2 - 0.25 + eps, fn = 40);
        translate([sx > 0 ? st_act_mount_x[0] : -st_act_mount_x[1], st_act_a[1] - 45, bd_deck_bot - 12]) cube([st_act_mount_x[1] - st_act_mount_x[0], 59, 12 + eps]);
    }
}
module st_act_mount_cuts() {
    translate([-40, st_act_a[1], st_act_a[2]]) rotate([0, 90, 0]) cyl(st_act_pin_d, 80, fn = 24);
    // relief in the deck underside over the eye, and clearance wherever the case would meet the deck
    translate([-st_act_eye_w/2 - 1, st_act_a[1] - st_act_eye_d/2 - 1.5, bd_deck_bot - 1]) cube([st_act_eye_w + 2, st_act_eye_d + 3, 2.5]);
    intersection() { st_act_case_env(1.5); translate([-100, -200, bd_deck_bot - eps]) cube([200, 400, tray_size[2] + 2*eps]); }
}

// ============================================================================ sensed shoulder lock
// Integral block inside body_upper (right-side geometry in the lock frame; mirrored for the left).
st_block = [[-48, -7], [-30, 56], [-76, 36]];                           // X, Y, Z ranges in the lock frame
module st_lock_block(side) {
    intersection() {
        st_lock_frame(side) translate([st_block[0][0], st_block[1][0], st_block[2][0]])
            cube([st_block[0][1] - st_block[0][0], st_block[1][1] - st_block[1][0], st_block[2][1] - st_block[2][0]]);
        union() {
            translate([0, 0, 243]) cylinder(r = bd_ri + 0.5, h = 100, $fn = 240);
            translate([0, 0, 150]) cylinder(r = 147, h = 95, $fn = 240);   // clear of the louvre slot depth below z 243
        }
    }
    // No printed land: the body must stay inside the 322 x 317 bed. The purchased GN 412 flange
    // (12 thick) sits 5 mm deep in the pad and stands 7 mm proud of it, so its pin face is the
    // land, 1 mm from the leg face.
}
module st_lock_cuts(side) {
    st_lock_frame(side) {
        // flange pocket (pin face flush with the land face) and the two M4 heat-set inserts behind it
        translate([-st_flange[0], -st_flange[1]/2 - 0.2, -st_flange[2]/2 - 0.2]) cube([st_flange[0] + 1, st_flange[1] + 0.4, st_flange[2] + 0.4]);
        for (y = [-st_flange_bolt, st_flange_bolt]) translate([-st_flange[0] - 9.5, y, 0]) rotate([0, 90, 0]) cyl(insert_d(4), 9.6, fn = 32);
        translate([-22.5, 0, 0]) rotate([0, 90, 0]) cyl(16, 11, fn = 48);                 // plunger hex passage
        translate([-60, 0, 0]) rotate([0, 90, 0]) cyl(29, 39, fn = 96);                   // knob cavity (open inboard)
        // horn slot under the knob and the horn sweep
        hull() for (b = [-2, st_release_angle / 2, st_release_angle + 3])
            translate([st_servo_s[0], 0, st_servo_s[1]]) rotate([0, -b, 0]) translate([0, -4, -7]) cube([st_horn_arm[0] + 5, 8, st_horn_arm[1] + 10]);
        // MG995 case, ears and the ear-screw access bores to the -Y face of the block
        translate([st_servo_s[0], 0, st_servo_s[1]]) {
            translate([-st_servo_w/2 - 0.5, 6.5, -(st_servo_l - st_servo_shaft_end) - 0.5]) cube([st_servo_w + 1, st_servo_h + 1, st_servo_l + 1]);
            translate([-st_servo_w/2 - 0.5, 18.5, -(st_servo_l - st_servo_shaft_end) - 7.5]) cube([st_servo_w + 1, 3.5, st_servo_l + 14.5]);
            translate([0, 3, 0]) rotate([-90, 0, 0]) cyl(8, 5, fn = 32);                   // spline and horn hub
            for (x = [-5, 5], z = [st_servo_shaft_end + 3.4, -(st_servo_l - st_servo_shaft_end) - 3.4]) translate([x, 0, z]) {
                translate([0, 21, 0]) rotate([-90, 0, 0]) cyl(insert_d(3), 6, fn = 24);      // M3 insert behind the ear
                translate([0, st_block[1][0] - 1, 0]) rotate([-90, 0, 0]) cyl(6, 19.5 - st_block[1][0] + 1, fn = 24);  // driver access
            }
        }
        // SS-01GL pocket, lever sweep and M2 screw access from +Y, thread-forming pilots toward -Y
        translate([st_switch_xh - 7.8, -3.5, 13.2]) cube([10.8, 7, 20.6]);
        translate([-26.5, -2, 9.5]) cube([17.4, 4, 15.5]);
        for (z = [18.65, 28.15]) translate([st_switch_xh, 0, z]) {
            rotate([-90, 0, 0]) cyl(4.5, st_block[1][1] + 10, fn = 24);
            rotate([90, 0, 0]) cyl(1.6, 10, fn = 16);
        }
        // harness exit from the knob cavity to the body interior
        translate([-60, -4, -30]) cube([22, 8, 30]);
    }
}

// ============================================================================ leg_upper: receivers
// GN 412.2 bushings screwed into thread-forming bores in the inboard face, hex flats toward each other.
module st_receiver_cuts() {
    for (a = [0, body_tilt]) let(ang = st_lock_angle + a) translate([0, st_lock_r*cos(ang), st_lock_r*sin(ang)]) {
        translate([-1, 0, 0]) rotate([0, 90, 0]) cylinder(d = (st_recv[2] + 0.3)/cos(30), h = st_recv[3] + 0.3 + 1, $fn = 6);
        translate([-1, 0, 0]) rotate([0, 90, 0]) cyl(st_recv[1] - 1.0, st_recv[0] + 1.5, fn = 48);
    }
}

// ============================================================================ purchased envelopes
module st_gn412(pull = 0) {             // lock frame, right side
    color("#9aa3ab") difference() {
        translate([-st_flange[0], -st_flange[1]/2, -st_flange[2]/2]) cube(st_flange);
        for (y = [-st_flange_bolt, st_flange_bolt]) translate([-st_flange[0] - 1, y, 0]) rotate([0, 90, 0]) cyl(4.3, st_flange[0] + 2, fn = 16);
    }
    color("#9aa3ab") translate([-st_flange[0] - st_hex[0], 0, 0]) rotate([0, 90, 0]) cylinder(d = st_hex[1]/cos(30), h = st_hex[0], $fn = 6);
    translate([-pull, 0, 0]) {
        color("#c8ccd0") translate([-st_flange[0] - st_hex[0], 0, 0]) rotate([0, 90, 0]) cyl(st_pin_d, st_flange[0] + st_hex[0] + st_pin_ext, fn = 32);
        color("#20262d") translate([-st_flange[0] - st_hex[0] - st_knob[0], 0, 0]) rotate([0, 90, 0]) cyl(st_knob[1], st_knob[0], fn = 48);
    }
}
module st_gn412_2() {                   // leg frame at the inboard face, bore along +X
    color("#9aa3ab") difference() {
        union() {
            rotate([0, 90, 0]) cylinder(d = st_recv[2]/cos(30), h = st_recv[3], $fn = 6);
            translate([st_recv[3], 0, 0]) rotate([0, 90, 0]) cyl(st_recv[1], st_recv[0] - st_recv[3], fn = 40);
        }
        translate([-1, 0, 0]) rotate([0, 90, 0]) cyl(st_recv[4], st_recv[0] + 2, fn = 32);
    }
}
module st_ss01gl(pressed = true) {      // lock frame, right side
    color("#20262d") difference() {
        translate([st_switch_xh - 7.3, -3.2, 13.5]) cube([10.2, 6.4, 19.8]);
        for (z = [18.65, 28.15]) translate([st_switch_xh, 0, z]) rotate([90, 0, 0]) cyl(2.35, 8, center = true, fn = 16);
    }
    color("#c8ccd0") translate([pressed ? -22 : st_switch_xh - 13.6, -1.5, 10]) cube([0.3, 3, 14.5]);
}
module st_mg995(angle = 0) {            // lock frame, right side; angle 0 = engage, st_release_angle = release
    translate([st_servo_s[0], 0, st_servo_s[1]]) {
        color("#20262d") translate([-st_servo_w/2, 7, -(st_servo_l - st_servo_shaft_end)]) cube([st_servo_w, st_servo_h, st_servo_l]);
        color("#20262d") translate([-st_servo_w/2, 19, -(st_servo_l - st_servo_shaft_end) - 6.75]) cube([st_servo_w, 2.5, st_servo_l + 13.5]);
        color("#c8ccd0") translate([0, 1.5, 0]) rotate([-90, 0, 0]) cyl(6, 5.5, fn = 24);
        color("#f0f0f0") rotate([0, -angle, 0]) {
            hull() { translate([0, -1.5, 0]) rotate([-90, 0, 0]) cyl(10, 3, fn = 32); translate([st_horn_arm[0], -1.5, st_horn_arm[1]]) rotate([-90, 0, 0]) cyl(6, 3, fn = 24); }
            translate([st_horn_arm[0], -4, st_horn_arm[1]]) rotate([-90, 0, 0]) cyl(2*st_horn_tip_r, 8, fn = 24);
        }
    }
}
module st_p16(s) {                      // body frame: case fixed at st_act_a, rod to the carriage eye
    translate(st_act_a) rotate([st_guide_angle, 0, 0]) {
        color("#252e38") translate([-st_act_case[0]/2, -st_act_case[1]/2, -st_act_case_t[1]]) cube([st_act_case[0], st_act_case[1], st_act_case_t[1] - st_act_case_t[0]]);
        color("#252e38") translate([-st_act_eye_w/2, 0, 0]) rotate([0, 90, 0]) difference() { hull() { cyl(st_act_eye_d, st_act_eye_w, fn = 32); translate([st_act_case_t[0], -st_act_eye_d/2, 0]) cube([1, st_act_eye_d, st_act_eye_w]); } translate([0, 0, -1]) cyl(st_act_pin_d, st_act_eye_w + 2, fn = 16); }
        color("#a3adb7") translate([0, 0, -(st_act_closed + s) + st_act_eye_d/2]) cyl(st_act_rod_d, st_act_closed + s - st_act_case_t[1] - st_act_eye_d/2 + 1, fn = 32);
        color("#a3adb7") translate([-st_act_eye_w/2, 0, -(st_act_closed + s)]) rotate([0, 90, 0]) difference() { cyl(st_act_eye_d, st_act_eye_w, fn = 32); translate([0, 0, -1]) cyl(st_act_pin_d, st_act_eye_w + 2, fn = 16); }
    }
}
module st_shafts() { for (sx = [-1, 1]) color("#c8ccd0") st_guide_at(st_shaft_t[0], sx*st_shaft_x) cyl(st_shaft_d, st_shaft_t[1] - st_shaft_t[0], fn = 48); }
module st_lm12luu() { color("#9aa3ab") for (sx = [-1, 1]) translate([sx*st_shaft_x, 0, st_brg_t]) difference() { cyl(st_brg[1], st_brg[2], fn = 64); translate([0, 0, -1]) cyl(st_brg[0], st_brg[2] + 2, fn = 48); } }
// hinge hardware in the carriage frame: spacer tubes and M8 bolt heads
module st_hinge_hw() { color("#9aa3ab") for (sx = [-1, 1]) translate([sx > 0 ? 41.65 : -54.15, 0, 0]) rotate([0, 90, 0]) difference() { cyl(12, 12.5, fn = 48); translate([0, 0, -1]) cyl(8.2, 14.5, fn = 24); } }

// ---------- the whole mechanism at stroke s (assembly frame) ----------
module st_mechanism(s, yaw = 0) {
    engaged = abs(s - st_s_two) < 0.01 || abs(s - st_s_contact) < 0.01 || s < st_s_contact || abs(s - st_s_three) < 0.05;
    pull = engaged ? 0 : st_pin_ext - st_land_gap;
    st_at_body(s) {
        st_shafts();
        st_p16(s);
        for (sd = [-1, 1]) st_lock_frame(sd) { st_gn412(pull); st_ss01gl(engaged); st_mg995(0); }
    }
    st_at_carriage(s) { color("white") leg_carriage_native(); st_lm12luu(); st_hinge_hw(); }
    for (sd = [-1, 1]) translate([sd*(body_r + shoulder_spacer), 0, shoulder_z_two_leg]) mirror([sd < 0 ? 1 : 0, 0, 0])
        for (a = [0, body_tilt]) let(ang = st_lock_angle + a) translate([0, st_lock_r*cos(ang), st_lock_r*sin(ang)]) st_gn412_2();
}
