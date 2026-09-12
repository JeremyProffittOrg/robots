// fable-r2d2 — head_drive.scad — dome friction-drive mount (ONE printed part: base + swing arm)
//
// GEOMETRY
//   A friction drive for the dome. One Adafruit 3777 TT motor is held with its shaft axis
//   horizontal and RADIAL (along the native Y axis, pointing at the body axis) so its Adafruit
//   3766 wheel (63 x 29 mm, tt_wheel) turns about a radial axis. The wheel is outboard of the
//   motor (wheel mid-plane wheel_x = 23.8 mm from the motor mid-plane, as in the feet). The top
//   of the wheel pushes up through the head_slot in the body top plate and presses on the flat
//   underside of the dome plate, which is susan_t (7.9 mm) above the top face of the body top
//   plate. Rolling the wheel drags the dome round on the lazy susan.
//   1. BASE: a 5 mm plate (hd_base_t) hanging under the body top plate, a U-frame around the
//      wheel slot, held by four M4 x 12 countersunk screws that come DOWN through plain holes
//      in the body top plate into M4 heat-set inserts in 3 mm pads under the base (hd_mount,
//      see INTERFACE). Two hinge lugs hang from its inner (toward the axis) edge. The M5 x 60
//      hex-head tension bolt hangs head-up in a hex pocket on the mating face (the top plate
//      captures the head) through a 3 mm boss on the underside of the right rail.
//   2. ARM: swings on an M4 x 70 hinge bolt (axis tangential = X) through the base lugs.
//      It carries the motor in an open-top saddle: 8 mm inboard wall with two M3 clearance
//      holes (17.6 mm apart; lower nut in a blind hex pocket on the inboard face, upper nut in
//      a hex slot open to the wall's top face) and a slot for the free shaft stub, 8 mm floor,
//      end wall at the gearbox front, half-pipe cradle under the motor can with a cable-tie
//      tunnel; the cradle ends at the can's end cap so the solder tabs, the rear tab and the
//      leads are free (axial location = front end wall + M3 bolts). A side beam on the right
//      (x 36..52) carries the tension ear (a Y slot for the M5, see 3) and, below its far end,
//      a 15 mm boss with an M5 insert for the lift-stop screw whose tip bears UP on the base.
//   3. TENSION (compliant, spring under the ear): base pocket -> M5 x 60 hex bolt hanging
//      down -> ear (slot) -> 15 mm OD washer -> compression spring 10 OD x 25 free -> plain
//      washer -> M5 knurled thumb nut. Turning the nut UP compresses the spring against the
//      underside of the ear, which lifts the arm and presses the tyre on the dome plate with
//      the spring force (design 4-6 mm of compression = 8-12 N at the ear = 4-6 N at the tyre,
//      loads.md section 5 asks for 3-5 N). The wheel floats on the spring and follows the
//      runout of the dome plate. With the dome off, the lift-stop screw (M5 x 20 in the arm,
//      tip on the base underside) limits the lift to hd_theta_max so the gearbox never touches
//      the base. Backing the thumb nut off ~8 mm lets the arm fall under its own weight until
//      the bolt shank meets the end of the ear slot at hd_theta_release (7 deg): the wheel top
//      is then 4 mm below the dome plate so the dome can be lifted off or dropped on without
//      dragging the tyre. The slot in the ear is the swept path of the fixed vertical bolt over
//      hd_theta_max-1 .. hd_theta_release, so the arm never binds on the bolt.
//
// FRAME (see r2d2.scad FRAMES): head_drive_native() — origin on the body axis at the top face
//   of the body top plate, +Y = front, Z up. The whole mount is on the -Y (rear) side around
//   radius head_wheel_r and hangs below z = -body_top_plate_t. head_drive_native(theta) takes
//   the arm angle in degrees about the hinge (0 = working, +ve = wheel lowered).
//   Arm frame (internal): hinge axis = X axis through the origin, -Y = outboard, wheel axle at
//   (0, -hd_lever, 0). The motor sits with the tt_motor() convention (shaft along Y, body
//   toward -X = droid's left).
//
// PRINT ORIENTATION: head_drive() = the native part flipped about X so the base's mating face
//   (the face against the top plate) is on the bed at z = 0, the lugs, the pads and the arm
//   rising above it, arm at hd_theta_print (4 deg lowered so no arm face is nearer than 2.5 mm
//   to the base). The base and the arm are printed as ONE solid: two sacrificial webs
//   (hd_web_t = 0.8 mm thick, 6 mm long, ~3.5 mm tall) join the arm's hinge-boss ridge to the
//   base plate's hidden underside at x = +/-15. AFTER PRINTING: cut both webs with a knife,
//   file the stubs flush (the arm needs 3 mm of clearance to the plate at the ridge), fit the
//   M4 x 70 hinge bolt.
//   SUPPORTS: the base, its pads, the tension boss and the lugs need none. The arm is a
//   suspended body: tree supports (enabled in scripts/slice_check.py) are unavoidable under
//   the arm — inside the open motor pocket (they land on the base plate's hidden underside),
//   under the side beam, and under the boss-to-wall bridge. All supported faces are hidden
//   inside the body. The stop boss and its insert hole face UP in print (no support); the
//   ear slot and the hinge teardrop bores need none. Remove the pocket supports after cutting
//   the webs and swinging the arm down.
//
// FASTENERS
//   4 x M4 x 12 countersunk (DIN 7991), from the TOP face of the body top plate, into
//       4 x M4 heat-set inserts (5.6 mm pilot, 8 deep) pressed into the base from its mating
//       face at hd_mount (the inner pair lies under the lazy-susan bottom race: heads flush)
//   1 x M4 x 70 socket head + 2 x M4 washers + M4 nyloc: hinge bolt through both lugs and
//       the arm boss (hd_boss_half 20.8 leaves 0.2 mm each side; snug the nyloc, do not
//       torque it, the arm must swing freely)
//   2 x M3 x 30 button head + 2 x M3 hex nuts: gearbox to the arm wall (heads on the wheel
//       side, fitted before the wheel is pressed on; lower nut into the blind hex pocket on
//       the inboard face, upper nut dropped into the hex slot from the wall top)
//   1 x cable tie 3.6 mm: round the motor can through the tunnel
//   1 x M5 x 60 hex head (DIN 933 full thread; a socket cap head would spin in the pocket)
//       1 x M5 washer 15 mm OD (DIN 9021) under the ear, 1 x compression spring 10 OD x
//       25 free x 1.0 wire (rate ~2 N/mm), 1 x M5 plain washer, 1 x M5 knurled thumb nut
//       (DIN 466, ~9 tall): tension adjuster on head_drive_tension_m
//   1 x M5 x 20 socket cap + 1 x M5 heat-set insert (6.4 pilot, 9.5 deep) in the arm's stop
//       boss: lift stop. Screwed fully home its tip stands hd_stop_proud (5 mm) above the
//       beam top and meets the base underside after hd_stop_travel (1 mm) of lift =
//       hd_theta_max (-1.4 deg). A 1 mm washer under its head adds 1 mm of travel.
//
// INTERFACE (all in the native frame; body.scad must use these names, not copies):
//   hd_mount = four plain holes the body top plate must carry, countersunk 90 deg x 9 mm on
//     its TOP face, clearance_d(4) through, underside FLAT (no bosses, no ribs) over the base
//     footprint x +/-56, y -148..-74: (+/-45, hd_hinge_y - 2 = -84) and
//     (+/-42, -(head_wheel_r + 6) = -139). The base pads under the inserts are d 12, 3 mm.
//   Wheel: x +/-31.5, y -147.5..-118.5, top at susan_t + hd_squeeze = 8.5 (working), 10.1
//     (lift stop, dome off), 3.8 (released 7 deg, rim at r 150.9). Chord at the top-plate
//     underside 51.7 (working), 53.4 (lift stop). head_slot must be [36, >= hd_slot_min = 58];
//     recommended [36, 60]; params.scad has 42 (echo warns). The 36 mm radial size (slot edge
//     r 151) is what caps the release at 7 deg: with head_slot = [38, 60] the release could be
//     10 deg (wheel top 1.7, rim r 152.0, measured clean against a 38 x 60 slot).
//   Nothing of this part is between the plates except the wheel (r >= 118.5 > 116).
//   Swept keep-out under the top plate: the wheel reaches r 150.9 at the 7 deg release and
//     r 152.0 if the release is later opened to 10 deg (body inner wall = body_r - body_wall
//     = 154.9). Nothing of the body (ring ribs, vertical ribs, rod bosses, susan nuts) may
//     enter x +/-64, y -153..-72, z -80..-5 on the -Y side; in particular no rib on the rear
//     inner wall between z -80 and -5 for |x| <= 40.
//   The bracket itself stays inside r <= hd_r_max = body_r - body_wall - 3.9 = 151.
//   The lazy-susan access hole at (0, -110.9) is covered by the base plate itself (solid for
//     |x| <= 34, y > -113) and is permanently unusable; the three other access holes at
//     0/90/180 deg must be used for the top-race screws.
//   Assembly order (base first, so every screw is reachable): press the four M4 inserts into
//     the base mating face and the M5 insert into the stop boss; drop the M5 x 60 head into
//     its pocket; hold the base under the plate (bolt hanging through the ear slot is not yet
//     possible, the arm is separate after the webs are cut) and fit the four M4 x 12 from the
//     top; slide the arm's ear slot over the hanging M5 and push the M4 x 70 through the lugs
//     and the boss from inside the open body ring, washers + nyloc snug; drop the motor in,
//     fit the two M3 x 30 from the wheel side, press the wheel on, cable-tie the can; fit the
//     15 mm washer, spring, washer and thumb nut on the M5; screw the M5 x 20 stop fully home;
//     fit the susan and the dome; then turn the thumb nut up until the spring is compressed
//     4-6 mm (20 mm long) and the tyre bites. Back the nut off 8 mm (10 turns) to release:
//     the arm drops until the bolt meets the slot end (7 deg); the nut stays on the M5 x 60.

// ---------- local parameters (everything shared comes from params.scad) ----------
hd_squeeze = 0.6;                              // tyre compression at the working position
hd_base_top = -body_top_plate_t;               // -5: mating face against the top plate
hd_base_t = 5;
hd_base_bot = hd_base_top - hd_base_t;         // -10
hd_arm_t = 8;                                  // arm wall thickness
hd_clear = 0.3;                                // motor pocket clearance (tt_motor cutter)
hd_hinge_y = -82;                              // hinge axis position, native
hd_hinge_z = susan_t + hd_squeeze - wheel_d/2; // -23.0: wheel axle height at working
hd_lever = head_wheel_r + hd_hinge_y;          // 51: hinge axis to wheel axle (arm frame)
hd_motor_y = -(hd_lever - wheel_x);            // -27.2: motor mid-plane, arm frame
hd_theta_work = 0;
hd_theta_print = 4;
hd_theta_release = 7;                          // slot-end stop: wheel top 3.8, rim r 150.9 (inside the 36 mm slot edge r 151)
hd_stop_travel = 1.0;                          // lift above working at the stop screw (mm)
hd_stop_y = -41;                               // stop screw, arm frame y (native -123)
hd_theta_max = -asin(hd_stop_travel / -hd_stop_y);   // -1.40: wheel top 9.8, gearbox 1.9 under the base
hd_mount_m = 4;
hd_mount = [[45, hd_hinge_y - 2], [-45, hd_hinge_y - 2],
            [42, -(head_wheel_r + 6)], [-42, -(head_wheel_r + 6)]];
hd_pad_d = 12; hd_pad_h = 3;                   // insert pads under the base (5 + 3 = insert_depth(4))
hd_tension_xy = [44, hd_hinge_y - 26];         // (44, -108) native; ear at arm y -26
hd_tension_boss_d = 12; hd_tension_boss_h = 3; // under the base: 4 mm floor below the 4 mm head pocket
hd_head_pocket = 4.0;                          // ISO 4017 M5 head k max 3.65 + first-layer squish
hd_stop_xy = [44, hd_hinge_y + hd_stop_y];     // (44, -123) native, where the tip meets the base
hd_stop_boss_d = 12; hd_stop_screw_l = 20; hd_stop_proud = 5;
hd_spring_od = 10; hd_spring_free = 25; hd_washer_od = 15;
hd_lug_x0 = 21; hd_lug_t = 8; hd_lug_r = 8;    // base lugs at x = +/-(21..29)
hd_boss_d = 14; hd_boss_half = 20.8;           // arm hinge boss, 0.2 mm to each lug
hd_bore_d = clearance_d(head_drive_hinge_m);   // 4.5
hd_window_hw = 34; hd_window_y = -113;         // wheel window in the base (x +/-34, y < -113)
hd_base_size = [112, 74]; hd_base_cy = -111;   // base outline before trimming: y -148..-74
hd_r_max = body_r - body_wall - 3.9;           // 151: 3.9 mm inside the body's inner wall
hd_web_t = 0.8; hd_web_len = 6; hd_web_x = 15;
hd_gear_recess = [[-27, -121], [13, -98]];     // 1 mm relief in the base over the gearbox top
hd_slot_min = 58;                              // tangential head_slot the wheel chord needs
// arm members (arm frame)
hd_wall_y1 = hd_motor_y + tt_thick/2 + hd_clear;      // -17.6 outboard face of the inboard wall
hd_wall_y0 = hd_wall_y1 + hd_arm_t;                   // -9.6 inboard face
hd_floor_top = -tt_gear_h/2 - hd_clear;               // -11.52
hd_floor_bot = hd_floor_top - hd_arm_t;               // -19.52
hd_wall_z = [hd_floor_bot, 11];                       // wall bottom = floor bottom (one face)
hd_wall_x = [-45, 52];
hd_sad_x = [-60.5, 20]; hd_sad_yo = -35;              // saddle block; outboard face 1.5 from the wheel rim; rear end open
hd_can_x0 = tt_axle_from_front - tt_gear_len - hd_clear;   // -26.05 gearbox rear = can start
hd_can_r = tt_can_d/2 + hd_clear;                     // 10.5
hd_beam_x = [36, 52]; hd_beam_z = [-1, 7]; hd_beam_y_end = hd_stop_y - 8;   // beam top native -16 (6 under the base)
hd_stop_boss_z = [hd_beam_z[1] - (hd_stop_screw_l - hd_stop_proud), hd_beam_z[1]];   // [-8, 7]: 15 tall
hd_bridge = [[-hd_boss_half, -11, -5], [hd_boss_half, 0, 5]];   // bottom at -5 clears the lower nut pocket (top flat -5.85)
hd_tie_x = [-50.5, -46]; hd_tie_z = [-13.5, -10.0];
hd_m3_x = -11.3;                                      // gearbox holes, arm frame x

if (head_slot[1] < hd_slot_min)
    echo(str("WARNING head_drive: params head_slot[1] = ", head_slot[1], " is narrower than the ",
             hd_slot_min, " mm the 63 mm wheel chord needs (recommended 60)"));

// ---------- helpers ----------
// 2D teardrop: circle d with a 45-degree point at distance d/2*sqrt(2) along +y (dir=1) or -y.
module hd_teardrop2d(d, dir = 1, fn = 48) {
    hull() { circle(d = d, $fn = fn); translate([0, dir * d/2 * sqrt(2)]) square(0.02, center = true); }
}
// Teardrop prism along X (2D y -> Z), centred on the X axis, from x0 to x1.
module hd_teardrop_x(d, x0, x1, dir = 1, fn = 48) {
    translate([x0, 0, 0]) rotate([90, 0, 90]) linear_extrude(x1 - x0) hd_teardrop2d(d, dir, fn);
}
// The fixed vertical tension bolt (native frame, clearance size) seen from the arm frame at angle t.
module hd_bolt_in_arm(t) {
    rotate([-t, 0, 0]) translate([0, -hd_hinge_y, -hd_hinge_z])
        translate([hd_tension_xy[0], hd_tension_xy[1], -36]) cyl(clearance_d(head_drive_tension_m), 26, fn = 32);
}

// ---------- base bracket (native frame) ----------
module hd_base_outline2d() {
    // morphological opening (r 3) rounds every convex corner, incl. the rail tips at the r151 arc
    offset(r = 3) offset(delta = -3) difference() {
        intersection() {
            translate([0, hd_base_cy]) rrect(hd_base_size[0], hd_base_size[1], 6);
            circle(r = hd_r_max, $fn = 180);
        }
        translate([0, hd_window_y - 30]) rrect(2 * hd_window_hw, 60, 4);   // open toward the wall
    }
}

module hd_base_lug(side) {
    // lug hangs from the plate to the hinge axis with a round bottom; 8 thick along X
    translate([side > 0 ? hd_lug_x0 : -(hd_lug_x0 + hd_lug_t), hd_hinge_y, hd_hinge_z])
        rotate([90, 0, 90]) linear_extrude(hd_lug_t) hull() {
            translate([-hd_lug_r, 0]) square([2 * hd_lug_r, hd_base_bot - hd_hinge_z + 0.5]);
            circle(r = hd_lug_r, $fn = 48);
        }
    // gusset on the outboard face, above the bolt head
    gx = side > 0 ? hd_lug_x0 + hd_lug_t : -(hd_lug_x0 + hd_lug_t);
    translate([gx, hd_hinge_y, 0]) mirror([side > 0 ? 0 : 1, 0, 0])
        rotate([90, 0, 0]) linear_extrude(2 * hd_lug_r, center = true)
            polygon([[-eps, hd_base_bot + 0.5], [5, hd_base_bot + 0.5], [-eps, hd_hinge_z + 6]]);
}

module hd_base() {
    difference() {
        union() {
            translate([0, 0, hd_base_bot]) linear_extrude(hd_base_t) hd_base_outline2d();
            for (s = [-1, 1]) hd_base_lug(s);
            // inboard stiffening rib (clear of the arm boss envelope r 9.9)
            translate([-52, hd_base_cy + hd_base_size[1]/2 - 3, hd_base_bot - 4]) cube([104, 3, 4.5]);
            // insert pads under the four mount points (5 + 3 = 8 mm for the M4 insert)
            for (p = hd_mount) translate([p[0], p[1], hd_base_bot - hd_pad_h]) cyl(hd_pad_d, hd_pad_h + eps, fn = 48);
            // boss under the tension bolt: 4 mm floor under the hex-head pocket
            translate([hd_tension_xy[0], hd_tension_xy[1], hd_base_bot - hd_tension_boss_h])
                cyl(hd_tension_boss_d, hd_tension_boss_h + eps, fn = 48);
        }
        // four M4 heat-set inserts from the mating face, screw clearance on through the pad
        for (p = hd_mount) translate([p[0], p[1], 0]) {
            translate([0, 0, hd_base_top + eps]) mirror([0, 0, 1]) insert_hole(hd_mount_m);
            translate([0, 0, hd_base_bot - hd_pad_h - 1]) cyl(clearance_d(hd_mount_m), hd_base_t + hd_pad_h + 2, fn = 32);
        }
        // tension bolt: hex head pocket from the mating face (4.0 deep, 0.5 mm wider mouth
        // chamfer against elephant foot), 5.5 shank clearance through the plate and the boss
        translate([hd_tension_xy[0], hd_tension_xy[1], hd_base_top - hd_head_pocket]) nut_pocket(head_drive_tension_m, hd_head_pocket);
        translate([hd_tension_xy[0], hd_tension_xy[1], hd_base_top - 0.5])
            cylinder(d1 = nut_af(head_drive_tension_m)/cos(30), d2 = (nut_af(head_drive_tension_m) + 1.0)/cos(30), h = 0.5 + eps, $fn = 6);
        translate([hd_tension_xy[0], hd_tension_xy[1], hd_base_bot - hd_tension_boss_h - 1])
            cyl(clearance_d(head_drive_tension_m), hd_base_t + hd_tension_boss_h + 2, fn = 32);
        // 1 mm relief over the gearbox top (max-lift clearance)
        translate([hd_gear_recess[0][0], hd_gear_recess[0][1], hd_base_bot - 1])
            cube([hd_gear_recess[1][0] - hd_gear_recess[0][0], hd_gear_recess[1][1] - hd_gear_recess[0][1], 2]);
        // hinge bore through the lugs (teardrop, point toward the bed in the print frame)
        translate([0, hd_hinge_y, hd_hinge_z]) hd_teardrop_x(hd_bore_d, -40, 40, dir = -1, fn = 32);
    }
}

// ---------- swing arm (arm frame: hinge axis = X, wheel at (0, -hd_lever, 0)) ----------
module hd_arm_body() {
    union() {
        // hinge boss with a 45-degree ridge toward the plate (prints point-down on the webs)
        hd_teardrop_x(hd_boss_d, -hd_boss_half, hd_boss_half, dir = 1, fn = 64);
        // bridge from the boss to the wall
        translate(hd_bridge[0]) cube(hd_bridge[1] - hd_bridge[0]);
        // inboard wall / crossbar
        translate([hd_wall_x[0], hd_wall_y1, hd_wall_z[0]])
            cube([hd_wall_x[1] - hd_wall_x[0], hd_arm_t, hd_wall_z[1] - hd_wall_z[0]]);
        // saddle block: floor, end wall and can cradle (pocket cut later)
        translate([hd_sad_x[0], hd_sad_yo, hd_floor_bot])
            cube([hd_sad_x[1] - hd_sad_x[0], hd_wall_y1 - hd_sad_yo + eps, hd_wall_z[1] - hd_floor_bot]);
        // right side beam with the tension ear, rounded far end centred on the stop screw
        translate([0, 0, hd_beam_z[0]]) linear_extrude(hd_beam_z[1] - hd_beam_z[0]) hull() {
            translate([hd_beam_x[0], hd_wall_y0 - 1]) square([hd_beam_x[1] - hd_beam_x[0], 1]);
            translate([(hd_beam_x[0] + hd_beam_x[1])/2, hd_beam_y_end + (hd_beam_x[1] - hd_beam_x[0])/2])
                circle(d = hd_beam_x[1] - hd_beam_x[0], $fn = 48);
        }
        // lift-stop boss hanging under the beam end (insert from its bottom, screw tip up)
        translate([hd_stop_xy[0], hd_stop_y, hd_stop_boss_z[0]])
            cyl(hd_stop_boss_d, hd_stop_boss_z[1] - hd_stop_boss_z[0], fn = 48);
    }
}

module hd_arm() {
    difference() {
        hd_arm_body();
        // hinge bore
        hd_teardrop_x(hd_bore_d, -hd_boss_half - 1, hd_boss_half + 1, dir = -1, fn = 32);
        // motor pocket: gearbox, can, shafts, tab (0.3 clearance)
        translate([0, hd_motor_y, 0]) tt_motor(hd_clear);
        // can cradle extended past the tt_motor can end so the 70 mm length has 0.6 mm play
        translate([hd_sad_x[0] - 1, hd_motor_y, 0]) rotate([0, 90, 0])
            cyl(2 * hd_can_r, hd_can_x0 + 2 * hd_clear - (hd_sad_x[0] - 1), fn = 64);
        // open the top over the can (half-pipe cradle), keep the inboard wall
        translate([hd_sad_x[0] - 1, hd_sad_yo - 5, 0]) cube([hd_can_x0 - hd_sad_x[0] + 1, hd_motor_y + hd_can_r - (hd_sad_yo - 5), 30]);
        // free shaft stub: slot in the wall from the axle to the top
        translate([0, hd_wall_y0 + 1, 0]) rotate([90, 0, 0]) cyl(7, hd_arm_t + 2, fn = 32);
        translate([-3.5, hd_wall_y1 - 1, 0]) cube([7, hd_arm_t + 2, 30]);
        // two M3 clearance holes through the wall; lower nut in a blind hex pocket on the
        // inboard face, upper nut in a hex slot open to the wall top (the 0.5 mm skin there
        // was not printable; the base plate 2 mm above keeps the nut captive)
        for (dz = [-tt_hole_spacing/2, tt_hole_spacing/2]) {
            translate([hd_m3_x, hd_wall_y0 + eps, dz]) rotate([90, 0, 0]) through_hole(3, hd_arm_t + 2);
            if (dz < 0) translate([hd_m3_x, hd_wall_y0 + eps, dz]) rotate([90, 0, 0]) nut_pocket(3, 2.8);
            else {
                translate([hd_m3_x, hd_wall_y0 + eps, dz]) rotate([90, 0, 0]) rotate([0, 0, 90]) nut_slot(3, hd_wall_z[1] - dz + 1, 2.8);
                translate([hd_m3_x - clearance_d(3)/2, hd_wall_y1 - 1, dz]) cube([clearance_d(3), hd_arm_t + 2, hd_wall_z[1] - dz + 1]);
            }
        }
        // cable-tie tunnel under the can (merges with the cradle groove)
        translate([hd_tie_x[0], hd_sad_yo - 2, hd_tie_z[0]]) cube([hd_tie_x[1] - hd_tie_x[0], hd_wall_y1 - hd_sad_yo + 4, hd_tie_z[1] - hd_tie_z[0]]);
        // tension ear: slot = the fixed vertical M5 swept over the whole arm travel
        // (hd_theta_max - 1 deg .. hd_theta_release); its release end is the drop stop
        hull() for (t = [hd_theta_max - 1, (hd_theta_max + hd_theta_release)/2, hd_theta_release]) hd_bolt_in_arm(t);
        // lift-stop insert from the boss bottom, screw clearance on up through the beam
        translate([hd_stop_xy[0], hd_stop_y, hd_stop_boss_z[0]]) insert_hole(5);
        translate([hd_stop_xy[0], hd_stop_y, hd_stop_boss_z[0] + insert_depth(5) - 1])
            cyl(clearance_d(5), hd_stop_boss_z[1] - hd_stop_boss_z[0] - insert_depth(5) + 2, fn = 32);
        // part label, recessed into the floor underside (hidden, faces down inside the body)
        translate([-22, -22, hd_floor_bot]) mirror([0, 0, 1]) mirror([1, 0, 0]) label("HEAD_DRIVE", 5);
    }
}

module hd_arm_placed(theta = hd_theta_work) {
    translate([0, hd_hinge_y, hd_hinge_z]) rotate([theta, 0, 0]) hd_arm();
}

// Motor + wheel envelopes at the arm angle (for renders and interference checks; not part of the print)
module hd_envelopes(theta = hd_theta_work) {
    translate([0, hd_hinge_y, hd_hinge_z]) rotate([theta, 0, 0]) {
        color("gold") translate([0, hd_motor_y, 0]) tt_motor();
        color("orange") translate([0, -hd_lever, 0]) tt_wheel();
    }
}

// Sacrificial print webs: base underside -> arm boss ridge at the print angle
module hd_webs(theta = hd_theta_print) {
    ry = -hd_boss_d/2 * sqrt(2) * sin(theta);
    rz = hd_boss_d/2 * sqrt(2) * cos(theta);
    for (sx = [-1, 1])
        translate([sx * hd_web_x - hd_web_len/2, hd_hinge_y + ry - hd_web_t/2, hd_hinge_z + rz - 0.5])
            cube([hd_web_len, hd_web_t, hd_base_bot - (hd_hinge_z + rz - 0.5) + 0.1]);
}

// ---------- public modules ----------
module head_drive_native(theta = hd_theta_work) {
    hd_base();
    hd_arm_placed(theta);
}

module head_drive() {
    translate([0, 0, hd_base_top]) rotate([180, 0, 0]) {
        head_drive_native(hd_theta_print);
        hd_webs(hd_theta_print);
    }
}
