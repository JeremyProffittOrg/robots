// fable-r2d2 — legs: leg_upper / leg_lower (right outer leg, two prints; mirror in the slicer
// for the left) and leg_center (centre leg with the caster ankle). Included by r2d2.scad after
// params.scad and lib.scad. Every local name carries the prefix lg_ so it cannot collide.
//
// FRAME (outer leg, native = leg_upper_native() / leg_lower_native()): shoulder pivot axis = X
//  through the origin, Z up the leg (ankle pivot at z = -leg_len), +Y = droid front, inboard
//  face of the strut at x = 0, outboard toward +X. The foot slot centre plane is
//  x = leg_strut_t/2 (at_foot puts the foot at leg_offset_x = body_r + shoulder_spacer +
//  leg_strut_t/2, the leg at body_r + shoulder_spacer), so the ankle tongue is centred there.
//
// GEOMETRY (all sizes from params.scad unless a lg_ name says otherwise)
//  Shoulder plate: a U-shaped plate, leg_strut_t (30.4) thick, inboard face flat at x = 0,
//   outline = the club horseshoe outline (horseshoe_w wide, semicircle R horseshoe_w/2 on the
//   shoulder axis, arms down to lg_hs_bottom, 53 deg corner chamfers) inset 1.4 mm so its top
//   circle is exactly leg_disc_d, tapering into the strut over lg_taper (club 1.345 in). The
//   horseshoe (horseshoe_t proud, arm width horseshoe_arm_w, window = leg_hub_d circle opening
//   into the horseshoe_gap slot) is a raised ring on the OUTBOARD face of this plate, so it
//   turns with the leg exactly as the club horseshoe drawings show. The body builder must NOT
//   model a second horseshoe on the shoulder pad: the pad is a flat shoulder_pad_d disc and the
//   shoulder_spacer stack sits between it and this flat inboard face.
//   NOTE horseshoe_above (93.4) is not used: the club sheet CSR SHOULDER - HORSESHOE 20140601
//   dimensions the top arc R4.013 in = horseshoe_w/2 concentric with the hub and 6.513 in below;
//   the plate keeps the params total height (horseshoe_above + horseshoe_below = 182.8).
//  Hub: three concentric rings (56/46/36 dia) inside the window, M12 hex head recessed in a
//   26 mm counterbore (10 deep), clearance_d(shoulder_bolt_m) bore through the plate.
//  Index: the LEG carries the dowel holes, shoulder_index_d at radius shoulder_index_r, one per
//   angle in shoulder_index_angles, measured from straight below the axis; angle a is placed
//   with rotate([-a,0,0]) so the hole sits toward the REAR (-Y). The body pad carries ONE hole
//   straight below the axis. Rotating the leg by +a about X (foot forward, the sense of
//   leg_lean in at_leg) brings the leg hole a onto the body hole: dowel in hole 0 = two-leg
//   stance, hole 18 = three-leg stance. Both holes go through the plate and the booster cover
//   so the 6 mm dowel is pushed in from outboard.
//  Booster cover: booster_cover [41.7 x 78.2 x 17.4] raised panel under the hub (curved top
//   following the hub circle) with a hex fitting; below it the strut channel with two 8 mm
//   strut rods (club leg struts), continued on leg_lower down to the ankle.
//  Strut: leg_strut_w x leg_strut_t, two leg_rod_d bores at y = +/-leg_rod_offset, x =
//   leg_strut_t/2, from the ankle counterbores up to leg_rod_top_z (blind). Top nuts sit in
//   captive hex traps (nut_slot) opening on the inboard face at z 40..48.4; the rod is fed in
//   from the ankle end, threaded through the captive nut, and the bottom nut + washer tightened
//   with a 13 mm socket in a 22 mm counterbore in the ankle underside (ceiling lg_rod_bottom_z).
//   NOTE leg_rod_bottom_z (-370) lies inside the outer foot's ankle block sweep at y = +/-20, so
//   the rods end at about -346 (M8 x 400 threaded rod); reported to the integrator.
//  Split at leg_split_z: comb joint. leg_lower carries a centre tongue 2*lg_finger_hw wide,
//   full thickness, leg_splice_len tall; leg_upper has the matching slot between two fingers
//   that carry the rod bores. Four M4 x 80 bolts through the whole strut width (Y) at
//   x = 5 / 25.4, z = -210 / -190, heads counterbored in the front face, hex nut pockets in the
//   rear face. Both halves print flat with no floating lap piece.
//  Ankle: leg_ankle_w x leg_ankle_t x (leg_ankle_start .. tip) block, flush with the inboard
//   face (x 0..leg_ankle_t) so leg_lower prints on a flat face; arched top (club AC ring),
//   40 deg bottom taper to a 16 mm flat 20 mm above the pivot so the outer foot's ankle block
//   (top 11.7 above the pivot, rear corner 29.6 above it at the 18 deg swing) never touches;
//   bracelet band, ankle cylinder pair (ankle_cyl_d x ankle_cyl_l and a 12 mm companion) with
//   its wedge holder on the outboard face, two hose holes on the front face. leg_tip_z is the
//   club outline datum; the tongue goes deeper because the foot slot needs it.
//  Tongue: leg_tongue_t x leg_tongue_w plate centred on x = leg_strut_t/2, from inside the
//   ankle down to -leg_len - lg_pivot_up - leg_tongue_depth (36.3 below the pivot, the slot
//   floor feet.scad expects), top corners cut back 3:1 above the block top and the front edge
//   cut back 11..30 below the pivot so the 18 deg swing clears the slot ends; clearance_d(ankle_bolt_m) pivot bore at z = -leg_len and lock bore
//   lg_lock_drop = 25 below it (feet.scad ft_lock_drop; params ankle_bolt_spacing = 50 is NOT
//   what the foot drills - reported).
//  Wires: 9 mm bore up the strut at (leg_strut_t/2, 0) from the ankle to z = -75, exiting the
//   inboard face at (0, 0, -75) (outside the shoulder pad); entry from the ankle underside at
//   (35, -38) above the outer foot's wire hole.
//
// FRAME (centre leg, native = leg_center_native()): Z up, origin on the caster axis at the
//  centre-foot top plane. The body skirt-bottom plane passes lg_center_plane_z (65.6) above
//  the origin, tilted body_tilt about X exactly as at_body() tilts it (front edge higher).
//  The flange center_leg_flange is built in that tilted frame with its top face on the plane
//  and four through_hole(center_leg_bolt_m) at center_leg_bolts (heads below in 19 mm socket
//  notches cut through the collar corners; nuts inside the body). Collar center_leg_section x 14 under the flange,
//  column 83.3 x 64 (club centre-ankle plate width) down to z = 26, 1 mm above the foot's
//  stem block. Bearings: two caster_bearing_od x caster_bearing_t seats on the caster_bolt_m
//  axis, lower one open to the bottom face (z 26..34.2), upper one open to the 28 mm head
//  counterbore, centres lg_bearing_cc = 18 apart (12 x 28 x 8 = 6001-2RS; 9.8 mm spacer tube
//  between the inner races). NOTE caster_bearing_gap (20) cannot fit: stem block 25 + 8 + 20 +
//  8 + washer + head = 72 > 65.6 - 10.4 tan(18) = 62.2 available under the tilted plane at the
//  head's rear edge. M12 x 70 hex bolt comes down from the leg (head in the counterbore,
//  tightened from above BEFORE the body is fitted; nut in the foot's slot).
//  Swivel stop: arc groove in the bottom face, pin-centre radius lg_stop_r = 22, +/-
//  caster_stop_deg about +Y, 7.6 wide, 8 deep, for a 6 mm x 8 pin ON THE STEM BLOCK TOP at
//  (0, caster_trail + 22) in the foot frame. NOTE feet.scad currently puts the pin at radius
//  35 on the top plane (z 0..8): no leg feature can reach it because the stem block corners
//  sweep radius 39 - reported to the feet owner.
//  Wires: arc slot r 16.5..22.5 from 168 to 340 deg (around -Y) in the bottom face, joined to a
//  12 x 12.5 vertical channel at y -29.5..-17 that exits the flange top as a 12 x 13 opening
//  centred near body-frame (0, -22); feet.scad's wire hole at (-18.5, caster_trail) is inside
//  the slot only near zero swivel - it should move to (0, caster_trail - 18.5). The body skirt
//  floor needs a matching wire hole (14 x 20 slot or 20 mm round) at body-frame (0, -22).
//
// PRINT ORIENTATION
//  leg_upper(): inboard face on the bed (native rotate([0,-90,0])), leg length along print X:
//   289.7 x 139.4 x 50.8 mm. No supports: horseshoe, hub, cover, rods and channel all rise from
//   the plate; horizontal bores are round (M12 13 mm, dowels 6.2, wire 9); the captive nut
//   traps are 13.4 x 8.4 mm tunnels bridged at 23 mm; the finger slot is vertical.
//  leg_lower(): inboard face on the bed, 232 x 100 x 58.2 mm. Supports: the tongue plate lies
//   leg_strut_t/2 - leg_tongue_t/2 = 6.5 mm above the bed (it must stay centred on the foot
//   slot), so a 6.5 mm normal support block under the tongue area (about 100 x 60 mm) is
//   needed; everything else rises from the bed. The 22 mm rod counterbores are horizontal
//   round holes.
//  leg_center(): flange face down (native rotate([-body_tilt,0,0]) then rotate([180,0,0])),
//   140 x 100 x 47.5 mm. No supports: the column leans 18 deg (its rear face is an 18 deg
//   overhang), the bearing seat, groove and wire slot open upward, the head counterbore is a
//   28 mm hole from the bed with a 2 mm ledge ring at 13 mm.
// FASTENERS (per outer leg): M12 x 130 hex shoulder bolt (head in the hub), 1 x 6 mm dowel,
//  2 x M8 x 400 threaded rod + 4 nuts + 2 washers, 4 x M4 x 80 + nuts, M8 x 80 pivot bolt and
//  M8 x 90 lock bolt (supplied with the foot). Centre leg: M12 x 70 hex bolt + 2 washers + 1 mm
//  thrust washer + 2 x 6001-2RS + 12 mm ID x 9.8 spacer tube, 4 x M8 x 30 + nuts to the body.

// ---------- local parameters (not in params.scad) ----------
lg_hs_top = horseshoe_w/2;                                     // 69.7 top arc radius (club R4.013)
lg_hs_bottom = horseshoe_above + horseshoe_below - lg_hs_top;  // 113.1 arm bottom below the axis
lg_plate_inset = lg_hs_top - leg_disc_d/2;                     // 1.4: plate sits inside the horseshoe edge
lg_hs_x0 = leg_strut_t;                                        // horseshoe on the outboard face
lg_hs_chamfer = [18, 23.9];                                    // arm outer corner cut (club 53 deg)
lg_gap_top_z = -50;                                            // window widens to horseshoe_gap here
lg_taper = 23.4;                                               // plate to strut taper length (club)
lg_pivot_up = 6.3;                                             // feet.scad ft_pivot_up
lg_lock_drop = 25;                                             // feet.scad ft_lock_drop (params ankle_bolt_spacing 50 is not drilled by the foot)
lg_tongue_bottom_z = -leg_len - lg_pivot_up - leg_tongue_depth; // -412.2
lg_tongue_x0 = leg_strut_t/2 - leg_tongue_t/2;                 // 6.5
lg_block_top_z = -leg_len + 18 - lg_pivot_up;                  // -364.2 foot ankle block top (feet ft_block[2])
lg_ankle_crown_z = -leg_ankle_start;                           // -246
lg_ankle_arc_r = 56.5;                                         // arched ankle top, 20 mm sagitta
lg_ankle_taper_z = -326.4;                                     // taper starts (both sides)
lg_ankle_flat_z = -leg_len + 20;                               // -355.9 flat bottom, 20 above the pivot
lg_ankle_flat_hw = 8;
lg_finger_hw = 10; lg_finger_clear = 0.2;                      // comb tongue half width, fit
lg_splice_x = [5, leg_strut_t - 5];                            // M4 bolt planes (X)
lg_splice_z = [leg_split_z + 10, leg_split_z + 30];            // M4 bolt heights
lg_rod_x = leg_strut_t/2;
lg_rod_nut_z = 40;                                             // captive top nut trap bottom
lg_rod_bottom_z = -336;                                        // counterbore ceiling; rod ends ~-346
lg_rod_cbore_d = 22;
lg_wire_d = 9; lg_wire_exit_z = -75; lg_wire_entry = [35, -38];
lg_hub_rings = [[56, 6], [46, 10], [36, 13]];                  // [dia, height above the plate]
lg_hub_cbore = [26, 10];
lg_cover_top_z = -25; lg_cover_x1 = leg_strut_t + booster_cover[2];
lg_channel_hw = 18; lg_channel_deep = 3; lg_channel_top_z = lg_cover_top_z - booster_cover[1];
lg_strut_rod_d = 8; lg_strut_rod_y = 8;
lg_upper_channel_bottom_z = -172;
lg_bracelet_z = -300; lg_bracelet_h = 8.7; lg_bracelet_proud = 1.5;
// centre leg
lg_center_plane_z = (shoulder_z_three_leg - shoulder_z*cos(body_tilt)) - (foot_clear + foot_center_h);   // 65.6
lg_center_col = [83.3, 64];
lg_center_bottom_z = 26;                                       // 1 mm above the 25 mm stem block
lg_collar_h = 14;
lg_bearing_fit = 0.2;
lg_bearing1_z = lg_center_bottom_z;                            // lower bearing seat bottom
lg_bearing_cc = 18;                                            // bearing centre spacing (params gap 20 does not fit, see header)
lg_bearing2_z = lg_bearing1_z + lg_bearing_cc;                 // 44 upper bearing seat bottom
lg_head_cbore_d = 28;
lg_stop_r = 22; lg_stop_w = 7.6; lg_stop_deep = 8;
lg_wire_arc = [16.5, 22.5]; lg_wire_arc_ang = [168, 340];
lg_wire_chan = [12, 12.5]; lg_wire_chan_y = -23.25;                // channel y -29.5..-17: 2.9 from the bearing seat, 2.5 from the rear face

// ---------- helpers ----------
// 2D shape in (y, z) extruded along +X from x0 for length t
module lg_yz(x0, t) { translate([x0, 0, 0]) rotate([90, 0, 90]) linear_extrude(height = t) children(); }
module lg_bore_x(x0, len, d, fn = 48) { translate([x0, 0, 0]) rotate([0, 90, 0]) cyl(d, len, fn = fn); }

// horseshoe outer outline (y, z): semicircle top on the axis, arms to lg_hs_bottom, corner cuts
module lg_hs_outline() {
    difference() {
        hull() {
            circle(r = lg_hs_top);
            translate([-lg_hs_top, -lg_hs_bottom]) square([horseshoe_w, lg_hs_bottom]);
        }
        for (s = [-1, 1]) translate([s*lg_hs_top, -lg_hs_bottom])
            polygon([[0, -1], [0, lg_hs_chamfer[1]], [-s*lg_hs_chamfer[0], -1]]);
    }
}
// horseshoe window: hub circle opening into the arm gap
module lg_hs_window() {
    hull() {
        circle(d = leg_hub_d);
        translate([-horseshoe_gap/2, -lg_hs_bottom - 1]) square([horseshoe_gap, lg_hs_bottom + 1 + lg_gap_top_z]);
    }
}
// shoulder plate outline (y, z) down to z_end
module lg_plate_outline(z_end) {
    offset(r = -lg_plate_inset) lg_hs_outline();
    hw = leg_strut_w/2;
    polygon([[-64, -lg_hs_bottom + 1], [64, -lg_hs_bottom + 1], [hw, -lg_hs_bottom - lg_taper],
             [hw, z_end], [-hw, z_end], [-hw, -lg_hs_bottom - lg_taper]]);
}
// strut channel with two strut rods between z0 and z1 (z0 < z1), cut then added by the caller
module lg_channel_cut(z0, z1) {
    translate([leg_strut_t - lg_channel_deep, -lg_channel_hw, z0]) cube([lg_channel_deep + 1, 2*lg_channel_hw, z1 - z0]);
}
module lg_channel_rods(z0, z1) {
    for (s = [-1, 1]) translate([leg_strut_t - lg_channel_deep, s*lg_strut_rod_y, z0 + 2]) cyl(lg_strut_rod_d, z1 - z0 - 4, fn = 32);
}
// M4 splice bolt features: clearance through the full width, head counterbore front, nut pocket rear
module lg_splice_holes() {
    for (x = lg_splice_x, z = lg_splice_z) translate([x, 0, z]) {
        rotate([90, 0, 0]) cyl(clearance_d(leg_splice_bolt_m), leg_strut_w + 2, center = true, fn = 24);
        translate([0, leg_strut_w/2 - 4.5, 0]) rotate([-90, 0, 0]) cyl(8, 6, fn = 24);
        translate([0, -leg_strut_w/2 - eps, 0]) rotate([-90, 0, 0]) nut_pocket(leg_splice_bolt_m, 3.6);
    }
}

// ============================================================================ LEG UPPER
module leg_upper_native() {
    difference() {
        union() {
            // shoulder plate + strut down to the split
            lg_yz(0, leg_strut_t) lg_plate_outline(leg_split_z);
            // horseshoe ring on the outboard face
            lg_yz(lg_hs_x0, horseshoe_t) difference() { lg_hs_outline(); lg_hs_window(); }
            // horseshoe details: two buttons on the front arm, hydraulic block on the rear arm
            for (z = [-10, -28]) translate([lg_hs_x0 + horseshoe_t, 54, z]) rotate([0, 90, 0]) cyl(9, 2.2, fn = 32);
            translate([lg_hs_x0 + horseshoe_t - eps, -60, 4]) cube([2.2, 12, 8]);
            // hub rings inside the window
            for (r = lg_hub_rings) lg_bore_x(lg_hs_x0 - eps, r[1] + eps, r[0], fn = 96);
            // booster cover with its curved top and hex fitting
            lg_yz(lg_hs_x0 - eps, booster_cover[2] + eps) difference() {
                translate([-booster_cover[0]/2, lg_cover_top_z - booster_cover[1]]) square([booster_cover[0], booster_cover[1]]);
                circle(r = leg_hub_d/2 + 1.6);
            }
            translate([lg_cover_x1 - eps, 0, lg_channel_top_z + 6]) rotate([0, 90, 0]) cylinder(d = 10, h = 3, $fn = 6);
        }
        // strut channel below the cover
        lg_channel_cut(lg_upper_channel_bottom_z, lg_channel_top_z + 0.5);
        // shoulder bolt bore and hub counterbore
        lg_bore_x(-1, 60, clearance_d(shoulder_bolt_m));
        lg_bore_x(lg_hs_x0 + lg_hub_rings[2][1] - lg_hub_cbore[1], 30, lg_hub_cbore[0], fn = 64);
        // index dowel holes (through plate and cover), toward the rear for angle > 0
        for (a = shoulder_index_angles) rotate([-a, 0, 0]) translate([0, 0, -shoulder_index_r]) lg_bore_x(-1, 60, shoulder_index_d, fn = 32);
        // rod bores from the split face up to leg_rod_top_z, captive nut traps opening inboard
        for (s = [-1, 1]) translate([lg_rod_x, s*leg_rod_offset, 0]) {
            translate([0, 0, leg_split_z - 1]) cyl(leg_rod_d, leg_rod_top_z - leg_split_z + 1, fn = 32);
            translate([0, 0, lg_rod_nut_z]) mirror([1, 0, 0]) nut_slot(leg_rod_d, lg_rod_x + 1, nut_h(leg_rod_d) + 1.6);
        }
        // comb slot for the lower tongue
        translate([-1, -lg_finger_hw - lg_finger_clear, leg_split_z - 1]) cube([leg_strut_t + 2, 2*(lg_finger_hw + lg_finger_clear), leg_splice_len + 1]);
        lg_splice_holes();
        // wire bore up the strut and its exit through the inboard face
        translate([lg_rod_x, 0, leg_split_z - 1]) cyl(lg_wire_d, lg_wire_exit_z - leg_split_z + 1, fn = 32);
        translate([-1, 0, lg_wire_exit_z]) rotate([0, 90, 0]) cyl(lg_wire_d, lg_rod_x + 1, fn = 32);
        // label recessed into the inboard (bed) face
        translate([0, 0, -150]) rotate([0, -90, 0]) rotate([0, 0, -90]) label("LEG UPPER R", 5);
    }
    // strut rods inside the channel
    lg_channel_rods(lg_upper_channel_bottom_z, lg_channel_top_z);
}

// ============================================================================ LEG LOWER
// ankle block outline (y, z): arched top, straight sides, 40 deg taper to the flat
module lg_ankle_outline() {
    hw = leg_ankle_w/2;
    intersection() {
        union() {
            translate([0, lg_ankle_crown_z - lg_ankle_arc_r]) circle(r = lg_ankle_arc_r);
            translate([-hw, -400]) square([leg_ankle_w, 400 + lg_ankle_crown_z - lg_ankle_arc_r]);
        }
        polygon([[-hw, -240], [hw, -240], [hw, lg_ankle_taper_z], [lg_ankle_flat_hw, lg_ankle_flat_z],
                 [-lg_ankle_flat_hw, lg_ankle_flat_z], [-hw, lg_ankle_taper_z]]);
    }
}
// tongue outline (y, z)
module lg_tongue_outline() {
    hw = leg_tongue_w/2;
    // front (+Y) lower edge cut back from 11 to 30 below the pivot: at the 18 deg swing the
    // front-bottom of the tongue moves forward in the foot's plate slot (y_f = y cos18 - h sin18)
    polygon([[-hw + 15, lg_tongue_bottom_z], [hw - 15, lg_tongue_bottom_z], [hw - 8, -leg_len - 30],
             [hw, -leg_len - 11], [hw, lg_block_top_z], [hw - 10, lg_block_top_z + 31], [hw - 10, -296],
             [-hw + 10, -296], [-hw + 10, lg_block_top_z + 31], [-hw, lg_block_top_z], [-hw, lg_tongue_bottom_z + 15]]);
}

module leg_lower_native() {
    hw = leg_strut_w/2;
    difference() {
        union() {
            // strut stub from the split down into the ankle, plus the comb tongue
            translate([0, -hw, lg_ankle_crown_z - 30]) cube([leg_strut_t, leg_strut_w, 30 + leg_split_z - lg_ankle_crown_z]);
            translate([0, -lg_finger_hw, leg_split_z - eps]) cube([leg_strut_t, 2*lg_finger_hw, leg_splice_len - lg_finger_clear + eps]);
            // ankle block, flush with the inboard face
            lg_yz(0, leg_ankle_t) lg_ankle_outline();
            // tongue
            lg_yz(lg_tongue_x0, leg_tongue_t) lg_tongue_outline();
            // bracelet band (not proud on the inboard face)
            translate([0, -leg_ankle_w/2 - lg_bracelet_proud, lg_bracelet_z - lg_bracelet_h/2])
                cube([leg_ankle_t + lg_bracelet_proud, leg_ankle_w + 2*lg_bracelet_proud, lg_bracelet_h]);
            // ankle cylinder pair and wedge holder on the outboard face
            translate([leg_ankle_t + 2, 10, -330]) rotate([45, 0, 0]) cyl(ankle_cyl_d, ankle_cyl_l, center = true, fn = 48);
            translate([leg_ankle_t + 1, -16, -318]) rotate([45, 0, 0]) cyl(12, 30, center = true, fn = 32);
            translate([leg_ankle_t - 1, -36, -346]) cube([7, 20.8, 32]);
            for (s = [-1, 1]) translate([leg_ankle_t + 2, 10 - s*10.85, -330 + s*10.85]) rotate([45, 0, 0]) cyl(ankle_cyl_d + 4, 4, center = true, fn = 48);
        }
        // strut channel continuation with rods (added below)
        lg_channel_cut(lg_ankle_crown_z + 2, leg_split_z - 4);
        // rod bores from the split face down to the ankle counterbores
        for (s = [-1, 1]) translate([lg_rod_x, s*leg_rod_offset, 0]) {
            translate([0, 0, lg_rod_bottom_z]) cyl(leg_rod_d, leg_split_z + leg_splice_len - lg_rod_bottom_z + 1, fn = 32);
            translate([0, 0, lg_rod_bottom_z - 16]) cyl(lg_rod_cbore_d, 16, fn = 48);
        }
        lg_splice_holes();
        // ankle pivot and lock bores through the tongue
        for (z = [-leg_len, -leg_len - lg_lock_drop]) translate([0, 0, z]) lg_bore_x(-5, leg_ankle_t + 10, clearance_d(ankle_bolt_m), fn = 32);
        // wire route: up from the foot's wire hole, diagonal into the strut centre, up through the split
        translate([lg_wire_entry[0], lg_wire_entry[1], -340]) cyl(lg_wire_d, 42, fn = 32);
        hull() {
            translate([lg_wire_entry[0], lg_wire_entry[1], -300]) sphere(d = lg_wire_d, $fn = 24);
            translate([lg_rod_x, 0, -280]) sphere(d = lg_wire_d, $fn = 24);
        }
        translate([lg_rod_x, 0, -281]) cyl(lg_wire_d, leg_split_z + leg_splice_len + 282, fn = 32);
        // hose holes on the front face of the ankle
        for (x = [12, 30]) translate([x, leg_ankle_w/2 + 1, -322]) rotate([90, 0, 0]) cyl(9, 13, fn = 24);
        // label recessed into the inboard (bed) face
        translate([0, 0, -300]) rotate([0, -90, 0]) rotate([0, 0, -90]) label("LEG LOWER R", 5);
    }
    lg_channel_rods(lg_ankle_crown_z + 2, leg_split_z - 4);
}

// ---------- print modules (inboard face on the bed, leg length along X) ----------
module leg_upper() { translate([-(-leg_split_z - lg_hs_top)/2, 0, 0]) rotate([0, -90, 0]) leg_upper_native(); }
module leg_lower() { translate([-(-lg_tongue_bottom_z + leg_split_z + leg_splice_len)/2, 0, 0]) rotate([0, -90, 0]) leg_lower_native(); }

// ============================================================================ CENTRE LEG
// children placed in the tilted body-skirt frame (z = 0 on the skirt-bottom plane)
module lg_at_plane() { translate([0, 0, lg_center_plane_z]) rotate([body_tilt, 0, 0]) children(); }

module lg_wedge2d(a0, a1, r = 200) { polygon([[0, 0], [r*cos(a0), r*sin(a0)], [r*cos((a0 + a1)/2), r*sin((a0 + a1)/2)], [r*cos(a1), r*sin(a1)]]); }

module leg_center_native() {
    fl = center_leg_flange;
    difference() {
        union() {
            // column from the bearing housing up past the plane, clipped to the plane below
            intersection() {
                translate([0, 0, lg_center_bottom_z]) rbox([lg_center_col[0], lg_center_col[1], 120], 8);
                lg_at_plane() translate([0, 0, -100]) cube([400, 400, 200], center = true);
            }
            // collar and flange in the tilted frame
            lg_at_plane() {
                translate([0, 0, -fl[2] - lg_collar_h]) rbox([center_leg_section[0], center_leg_section[1], lg_collar_h + 1], 12);
                translate([0, 0, -fl[2]]) rbox([fl[0], fl[1], fl[2]], 8);
            }
        }
        // flange bolts, wire hole and label on the flange top (against the body floor)
        lg_at_plane() {
            for (p = center_leg_bolts) translate([p[0], p[1], -fl[2] - 1]) cyl(clearance_d(center_leg_bolt_m), fl[2] + 2, fn = 32);
            // bolt head / 13 mm socket notches through the collar corners
            for (p = center_leg_bolts) translate([p[0], p[1], -fl[2] - lg_collar_h - 2]) cyl(19, lg_collar_h + 2.5, fn = 48);
            translate([45, 0, 0]) rotate([0, 0, 90]) label("LEG CENTER", 4);
        }
        // bearing seats, bolt bore, head counterbore
        translate([0, 0, lg_bearing1_z - 1]) cyl(caster_bearing_od + lg_bearing_fit, caster_bearing_t + lg_bearing_fit + 1, fn = 96);
        translate([0, 0, lg_bearing2_z]) cyl(caster_bearing_od + lg_bearing_fit, caster_bearing_t + lg_bearing_fit, fn = 96);
        translate([0, 0, lg_bearing1_z]) cyl(caster_bearing_od - 4, 100, fn = 64);
        translate([0, 0, lg_bearing2_z + caster_bearing_t + lg_bearing_fit - eps]) cyl(lg_head_cbore_d, 100, fn = 64);
        // swivel stop groove (pin on the stem block top at lg_stop_r ahead of the axis)
        translate([0, 0, lg_center_bottom_z - 1]) linear_extrude(height = lg_stop_deep + 1)
            for (a = [90 - caster_stop_deg : 10 : 90 + caster_stop_deg - 1]) hull()
                for (b = [a, a + 10]) translate([lg_stop_r*cos(b), lg_stop_r*sin(b)]) circle(d = lg_stop_w, $fn = 32);
        // wire arc slot in the bottom face and the vertical channel to the flange
        translate([0, 0, lg_center_bottom_z - 1]) linear_extrude(height = 14) intersection() {
            difference() { circle(r = lg_wire_arc[1]); circle(r = lg_wire_arc[0]); }
            lg_wedge2d(lg_wire_arc_ang[0], lg_wire_arc_ang[1]);
        }
        translate([-lg_wire_chan[0]/2, lg_wire_chan_y - lg_wire_chan[1]/2, lg_center_bottom_z + 10]) cube([lg_wire_chan[0], lg_wire_chan[1], 60]);
        // club centre-ankle detail: two vertical slots and a scribe on each side face
        for (sx = [-1, 1], y = [-14, 14]) translate([sx*lg_center_col[0]/2 - 1.5, y - 2.15, 30]) cube([3, 4.3, 24]);
        for (sx = [-1, 1]) translate([sx*lg_center_col[0]/2 - 0.6, -25, 62]) cube([1.2, 50, 1.5]);
    }
}

// print module: flange face down
module leg_center() { rotate([180, 0, 0]) rotate([-body_tilt, 0, 0]) translate([0, 0, -lg_center_plane_z]) leg_center_native(); }
