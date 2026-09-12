// fable-r2d2 — feet: foot_outer() (right outer foot; mirror in the slicer for the left) and
// foot_center(). Included by r2d2.scad after params.scad and lib.scad. All names carry the
// prefix ft_ so they do not collide with the other part files.
//
// FRAME (foot native = print frame): z = 0 at the shell bottom edge (foot_clear above the
// floor), +Y front, X across the foot, origin at the ankle slot centre (outer) or the foot
// centre (centre foot). Right outer foot: inboard = -X (battery box side), outboard = +X.
//
// GEOMETRY
//  Shell: open box with no floor, hull of two rounded rectangles (bottom foot_*_l_bot x
//  foot_*_w_bot, top foot_*_l_top x foot_*_w_top at foot_*_h), wall foot_wall, closed by a
//  5 mm top plate. Every decorative recess is <= 0.8 mm so the wall never drops below 2.4 mm.
//  Outer foot details (club shell drawings mc.foot.shell pg1/pg2 and the photo review):
//  outboard side door (0.6 mm framed trapezoid recess, raised door 0.3 below the face,
//  scribe line), panel trim strip and two corner trims above the door, inboard straight side
//  panel scribe with the ankle notch (visible on the rear half), apron stripe slots along the
//  bottom of every face (7 per side, 2 per end; the three under the battery box are omitted),
//  one large half-moon plate (tombstone r 22, 1.2 proud) on the outboard half of each end face
//  with a raised inner plate carrying two slots, ankle notch scribes and trim strips on both
//  end faces, two knurled hose-socket bosses (13 mm 12-gon, 8.7 mm socket) in the front trim
//  strip, and one battery box (hollow loaf shell, wall foot_wall, one internal web, rounded
//  top ends, two harness straps with blue tips, two knurled fittings with hose stubs and
//  45 deg gussets) on the inboard side at the front.
//  Ankle (outer): raised block 60 x 120 x 18 on the top plate, slot foot_slot_w wide x
//  2*ft_slot_hl long through block and plate, widened for the 18 deg tongue swing; pivot bore
//  clearance_d(ankle_bolt_m) along X at z = foot_outer_h + ft_pivot_up through both block
//  cheeks with ankle_cyl_d bosses (4 mm proud) and an M8 nut pocket in the inboard boss; lock
//  bore of the same size on the pivot plane ft_lock_r = ankle_bolt_spacing = 40 mm ahead of the
//  pivot (Y = +40), also through both cheeks with bosses and an inboard nut pocket. The leg
//  tongue carries two 9 mm lock holes 40 mm from the pivot: A at (y +40, z 0) for the two-leg
//  stance and B at (y +38.04, z -12.36) for the 18 deg three-leg lean (12.5 mm apart, 3.5 mm
//  web). RESOLVED: cad/legs.scad now cuts exactly those two holes (lg_lock_r, lg_lock_holes)
//  and its old bore 25 mm below the pivot is gone; an assert() below ties ft_lock_r to
//  ankle_bolt_spacing so a params change cannot move one part without the other.
//  Tongue length is 48 mm from the block top (18 block + 30 below the plate). The interior tongue
//  sweep (0 to +/-18 deg, 2.5 mm margin) is cut out of every internal rib.
//  Drive: two Adafruit 3777 motors, shafts along X at z = wheel_axle_z, centre planes at
//  Y = +/-foot_axle_y, four 3766 wheels at X = +/-wheel_x in 3 mm clearance cavities that are
//  open to the bottom and clipped to the shell inner surface (full wall kept). Every motor
//  pocket is a vertical drop-in channel: each envelope piece (gearbox, can, shafts, tab) is
//  hulled with a copy translated to the bed, so the motor + wheel unit is pushed straight up
//  into the foot from the open sole. The gearbox pocket ceiling is the tilted gearbox top face
//  (face contact, 12 mm wide spine beam simply supported by the centre rib pillar and the end
//  column), the can sits under a round arch through the transverse can wall and end block with
//  a cable-tie saddle groove, and on the outer feet the rear tab is pinned by an M3 x 35 bolt
//  across the channel (head on the -X end-block cheek, nut in a slot open to the bed in the +X
//  cheek). Outer feet: cans point outward and 13 deg below horizontal (can bottom at z -3.7,
//  8 mm above the floor). Centre foot: front can inward and up 45 deg, rear can inward and
//  10 deg below horizontal; both tied through the 22 mm central rib. The wheel load pushes
//  each gearbox up into its ceiling; the ties hold the motors when the foot is lifted.
//  Internal ribs (outer): 12 mm centre rib, 12 mm spines, 8 mm can walls, 36 x 42 x 32 end blocks.
//  Centre foot top: caster stem block ft_stem (50 x 60 x 25) centred on the caster axis
//  (caster_trail = 35, so the block is Y 5..65) with a prow over the sloped front face,
//  vertical clearance_d(caster_bolt_m) bore on the axis, M12 NUT slot (nut_slot, 19.4 AF x
//  8.4 deep) under the plate opening toward +X (the pocket's rear half is open to the shell
//  interior, so the nut goes in from the open sole before the motors do; the bolt comes down
//  from the leg), and a 6 mm swivel-stop pin ft_pin_h = 8 mm tall at radius ft_stop_r = 22
//  ahead of the axis (Y = caster_trail + 22 = 57) standing ON THE STEM BLOCK TOP
//  (z H+25 .. H+33), with 8 mm of block ahead of it.
//  PROW (RESOLVED for caster_trail = 35): the centre foot's top face is only
//  +/- foot_center_l_top/2 = 29.3 long and its end faces slope ft_end_ang_c = 35.0 deg, so the
//  block front at Y 65 overhangs the sloped front face by ft_prow_over = 35.7 mm - nearly
//  twice the 20.7 mm it overhung at caster_trail = 20. The prow therefore drops
//  ft_prow_step = 5 mm vertically from the block front and then runs at exactly 45 deg for
//  ft_prow_drop = 30 mm total, reaching the sloped face 24.0 mm below the top face (24.7 mm
//  at the rounded front corners, still inside the 30 mm): the block is fully carried to the
//  shell and no underside is steeper than 45 deg. The 5 mm vertical skirt is not cosmetic -
//  it is what keeps 8.5 mm of wall between the M12 nut slot and the prow face; without it the
//  45 deg face would pass 4.9 mm from the nut. The M12 bore keeps 23.5 mm of block wall in Y
//  and 18.5 mm in X, and 12.4 mm to the prow face at its lowest point.
//  RESOLVED, the leg groove is the reference: the pin moved in from radius 35 to 22 to meet
//  cad/legs.scad lg_stop_r = 22. The leg groove was not moved out to 35 because the leg's
//  bottom boss is only 83.3 x 64, so half its depth in Y is 32 mm and a radius-35 groove would
//  break out of its front face mid-sweep. At radius 22 the pin sits on solid stem block
//  (block Y -10..50, 5 mm of wall ahead of it), so the old 16 mm ledge fin is DELETED and no
//  45 deg underside is needed - the pin now rises from a flat horizontal face. The pin top is
//  1 mm below the groove floor and 7 mm of it is inside the 8 mm deep groove, which spans
//  +/- caster_stop_deg (60) about forward with solid leg beyond: those are the hard stops.
//  Centre foot details: tombstone half-moon (r 27.5) with slotted inner plate on both end
//  faces, framed door recess with raised door and scribe on both sides, side trim strips,
//  apron slots (4 per side, 2 per end).
//  Wires: 8 mm hole through the top plate and ankle block at (X 20, Y -38) on the outer foot.
//  Centre foot, RESOLVED (the leg's arc slot is the reference and this hole moved onto it): the
//  8 mm hole is at (X 0, Y caster_trail - ft_wire_r) = (0, 14), i.e. leg-frame radius 21 at
//  270 deg, dead behind the caster axis; it runs down through the stem block, the top plate and
//  the front spine to z 70, where a hulled 8 mm tunnel runs out to X -20. The Y tunnel that
//  crosses the centre rib at X -20, z 70 is NOT hung on the wire hole any more: with
//  caster_trail = 35 the wire hole sits 4 mm AHEAD of the rib (the rib spans Y -12..10), so
//  the pass is centred on the rib mid-plane ft_rib_c_y = -1 and is ft_wire_pass = 36 long
//  (Y -19..17). It still meets the hulled tunnel at Y 14 and still opens into the rear bay,
//  so both motors reach the wire. It used to be at
//  (X -18.5, Y caster_trail), which left the leg's arc as soon as the caster swivelled.
//  cad/legs.scad now carries the matching arc slot at r 16.6..25.4, 199..341 deg: the wire stays
//  covered through the whole +/-60 deg swivel, the arc never merges with the stop groove ahead
//  of the axis, and a 2.5 mm web keeps the wire clear of the lower bearing seat.
//
// PRINT ORIENTATION: sole (open side) down on the bed, as modelled. No supports: the sloped
//  walls are 19.7 / 34.6 deg from vertical (centre foot 22.3 / 35.0), every internal rib rises
//  from the bed, gearbox pocket ceilings are 12 mm wide tilted bridges over a 19.4 mm pocket,
//  can pockets are 21 mm round arches with 1 mm sag allowance, the centre-foot front pocket
//  faces are 45 deg, the battery-box cavity roof is two 22-25 mm bridges plus a 45 deg wedge
//  roof, hose bosses and fittings have 45 deg gussets, the caster prow has a 5 mm vertical
//  skirt and then a 45 deg underside all the way down to the sloped shell face, and the
//  swivel-stop pin stands on the flat stem-block top (no ledge, no overhang). The
//  centre-foot wire tunnel at z 70 is an 8 mm round bore inside the 22 mm centre rib. Top plate: the two 20 mm strips beside the ankle slot bridge 51 mm from
//  the centre rib to the end column and the plate bridges the side walls (58 mm outer,
//  45 mm centre) - use bridge settings with 100 % fan; if the slicer will not bridge that, add
//  tree supports under the top plate only.
// FASTENERS: outer foot - 2 x M8 x 80 hex bolt + nut (ankle pivot and ankle lock, heads
//  outboard), 2 x M3 x 35 tab bolts + 2 x M3 nuts, 2 cable ties 4.8 mm; centre foot - M12 nut in
//  the stem slot + M12 x ~70 hex bolt from the leg side (or an M12 stud with two nuts),
//  2 cable ties. Motors and wheels: 2 x 3777, 4 x 3766 per foot. Hoses (two, 8.7 mm) push
//  onto the battery-box stubs and into the front-face sockets.

// ---------- local parameters (not in params.scad; the orchestrator is asked to promote the
// ankle/caster interface values to params.scad) ----------
ft_plate_t = 5;                  // top plate
ft_wheel_clear = 3;              // clearance around every wheel
ft_spine_hw = 6.0;               // half width of the central spine ribs (inside the 6.3 wheel gap)
ft_block = [60, 120, 18];        // ankle block on the outer foot top (X, Y, Z)
ft_pivot_up = 6.3;               // pivot bore above the shell top
ft_lock_r = ankle_bolt_spacing;  // 40: lock bore ahead of the pivot, on the pivot plane
ft_swing = 18;                   // tongue swing (deg)
ft_boss_proud = 4;               // ankle cylinder bosses beyond the block faces
ft_motor_tilt_o = 13;            // outer feet: can outward, this many deg below horizontal
ft_phi_c_front = -45;            // centre foot front can: inward (-Y) and up, 45 deg from vertical
ft_phi_c_rear = 100;             // centre foot rear can: inward (+Y), 10 deg below horizontal
ft_tie_w = 5; ft_tie_deep = 2.5; // cable tie groove
ft_batt_y0 = 8;                  // battery box rear face
ft_loaf_r = 26;                  // battery box end rounding (Y-Z plane)
ft_stem = [50, 60, 25];          // caster stem block
ft_stem_y0 = caster_trail - ft_stem[1]/2;   // 5: block centred on the caster axis (Y 5..65)
ft_stop_r = 22;                  // swivel stop pin radius from the caster axis (= legs.scad lg_stop_r)
ft_pin_d = 6; ft_pin_h = 8;
ft_wire_d = 8;
ft_wire_r = 21;                  // centre-foot wire hole radius behind the caster axis (= legs.scad lg_wire_r)
ft_rib_c_y = -1;                 // centre rib mid-plane in Y (the rib spans Y -12..10)
ft_wire_pass = 36;               // length of the Y tunnel at X -20 that crosses the centre rib
ft_end_hw = 18;                  // outer foot end block half width (tab bolt cheeks)
ft_rib_hw_o = 6;                 // outer foot centre rib half thickness
ft_tab_nut_x = 11.6;             // M3 tab nut slot starts here (+X cheek)

// ---------- interface asserts (a params or legs.scad change must not silently diverge) ----------
assert(ft_lock_r == ankle_bolt_spacing, "feet/params: ankle lock bore radius != ankle_bolt_spacing");
assert(ft_stop_r == lg_stop_r, "feet/legs: swivel stop pin radius != the leg groove radius lg_stop_r");
assert(ft_wire_r == lg_wire_r, "feet/legs: centre-foot wire hole radius != the leg wire arc radius lg_wire_r");

ft_pivot_z = foot_outer_h + ft_pivot_up;
ft_slot_hl = leg_tongue_w/2 * cos(ft_swing) + (ft_block[2] - ft_pivot_up) * sin(ft_swing) + 1;   // 52.2
ft_c = motor_pocket_clear;

ft_side_ang_o = atan((foot_outer_w_bot - foot_outer_w_top) / 2 / foot_outer_h);   // 19.7
ft_end_ang_o = atan((foot_outer_l_bot - foot_outer_l_top) / 2 / foot_outer_h);    // 34.6
ft_side_ang_c = atan((foot_center_w_bot - foot_center_w_top) / 2 / foot_center_h); // 22.3
ft_end_ang_c = atan((foot_center_l_bot - foot_center_l_top) / 2 / foot_center_h);  // 35.0

// Caster prow. caster_trail = 35 puts the stem block's front edge at Y 65 while the centre
// foot's top face only reaches foot_center_l_top/2 = 29.3, so the block overhangs the sloped
// front face by ft_prow_over = 35.7 mm. The prow drops ft_prow_step straight down from the
// block front (this vertical skirt is what keeps 8.5 mm of wall between the M12 nut slot and
// the prow face) and then runs at 45 deg until it meets the face, which happens
// (ft_prow_over + ft_prow_step) / (1 + tan(ft_end_ang_c)) = 24.0 mm below the top; the extra
// 6 mm buries the prow's bottom inside the shell so nothing is left unsupported.
ft_prow_over = ft_stem_y0 + ft_stem[1] - foot_center_l_top/2;                    // 35.7
ft_prow_step = 5;
ft_prow_drop = (ft_prow_over + ft_prow_step) / (1 + tan(ft_end_ang_c)) + 6;      // 30.0

// ---------- generic shell helpers ----------
// half extent of the shell at height z (linear taper)
function ft_hx(z, wb, wt, h) = wb/2 - (wb - wt)/2 * z / h;

module ft_shell_hull(lb, wb, lt, wt, h, r = 4) {
    hull() {
        linear_extrude(height = 0.01) rrect(wb, lb, r);
        translate([0, 0, h - 0.01]) linear_extrude(height = 0.01) rrect(wt, lt, r);
    }
}
// interior cavity (from below the bed up to the plate underside), walls `wall` thick
module ft_shell_inner(lb, wb, lt, wt, h, ang_s, ang_e, wall = foot_wall) {
    wx = wall / cos(ang_s); wy = wall / cos(ang_e);
    z1 = h - ft_plate_t;
    hull() {
        translate([0, 0, -1]) linear_extrude(height = 0.01)
            rrect(2*ft_hx(-1, wb, wt, h) - 2*wx, 2*ft_hx(-1, lb, lt, h) - 2*wy, 2);
        translate([0, 0, z1 - 0.01]) linear_extrude(height = 0.01)
            rrect(2*ft_hx(z1, wb, wt, h) - 2*wx, 2*ft_hx(z1, lb, lt, h) - 2*wy, 2);
    }
}
// shell hull grown outward by one wall (keeps the wall when a cavity is cut beside it)
module ft_shell_grown(lb, wb, lt, wt, h, ang_s, ang_e) {
    wx = foot_wall / cos(ang_s); wy = foot_wall / cos(ang_e);
    ft_shell_hull(lb + 2*wy, wb + 2*wx, lt + 2*wy, wt + 2*wx, h, 7);
}
// Local frame on a sloped side face (sx = +1 outboard/+X): children 2D-style with local x = Y
// along the face, local y = up the slope from the bottom edge, local z = outward normal.
module ft_on_side(sx, ang, hw_b) {
    multmatrix([[0, -sx*sin(ang), sx*cos(ang), sx*hw_b],
                [1, 0, 0, 0],
                [0, cos(ang), sin(ang), 0],
                [0, 0, 0, 1]]) children();
}
// Local frame on a sloped end face (sy = +1 front): local x = sy*X, local y = up the slope.
module ft_on_end(sy, ang, hl_b) {
    multmatrix([[sy, 0, 0, 0],
                [0, -sy*sin(ang), sy*cos(ang), sy*hl_b],
                [0, cos(ang), sin(ang), 0],
                [0, 0, 0, 1]]) children();
}
module ft_trap(b, t, h, v0 = 0) { polygon([[-b/2, v0], [b/2, v0], [t/2, v0 + h], [-t/2, v0 + h]]); }
// recess a 2D shape `depth` into the face (face plane at local z = 0)
module ft_recess(depth) { translate([0, 0, -depth]) linear_extrude(height = depth + 2) children(); }
// raise a 2D shape `height` proud of the face (starts 1 mm inside the face)
module ft_raise(height) { translate([0, 0, -1]) linear_extrude(height = height + 1) children(); }
module ft_outline(w = 1.2) { difference() { offset(delta = w/2) children(); offset(delta = -w/2) children(); } }
// half-moon "tombstone": rectangle from v0 up to vc, semicircle of radius r on top (centred on u = 0)
module ft_tombstone(r, v0, vc) { translate([-r, v0]) square([2*r, vc - v0]); translate([0, vc]) circle(r); }
// apron stripe slot (20 x 4, 0.8 deep) centred at u, bottom edge 5.5 up the face
module ft_apron_slot(u) { ft_recess(0.8) translate([u - 10, 5.5]) square([20, 4]); }
// knurled hose-socket boss on a sloped end face: 13 mm 12-gon 5 mm proud with a 45 deg gusset
// below and a 4 mm root inside the wall (the 8.7 mm socket is cut by the caller)
module ft_hose_boss(u, v) {
    translate([u, v, 0]) {
        hull() { cylinder(d = 13, h = 5, $fn = 12); translate([-6.5, -14.5, -0.5]) cube([13, 8, 0.5]); }
        translate([0, 0, -4]) cylinder(d = 13, h = 4.5, $fn = 12);
    }
}

// ---------- motor helpers ----------
// Place children in the 3777 frame used by lib.tt_motor: shaft along foot X at the axle,
// can pointing along d = (0, sin(phi), cos(phi)) in the Y-Z plane (phi = 0 up, 90 = +Y).
module ft_motor_at(y, phi) { translate([0, y, wheel_axle_z]) rotate([90 - phi, 0, 0]) rotate([0, 0, -90]) children(); }
// motor envelope pieces in the motor local frame (same placement as lib.tt_motor)
module ft_gb(c) { translate([tt_axle_from_front - tt_gear_len - c, -tt_thick/2 - c, -tt_gear_h/2 - c]) cube([tt_gear_len + 2*c, tt_thick + 2*c, tt_gear_h + 2*c]); }
module ft_can(c) { translate([tt_axle_from_front - tt_gear_len - c + 1, 0, 0]) rotate([0, -90, 0]) cyl(tt_can_d + 2*c, tt_len - tt_gear_len + c + 1, fn = 48); }
module ft_shafts(c) { translate([0, -tt_thick/2 - tt_shaft_l1 - c, 0]) rotate([-90, 0, 0]) cyl(tt_shaft_d + 2*c, tt_shaft_l1 + tt_thick + tt_shaft_l2 + 2*c); }
module ft_tab(c) { translate([tt_axle_from_front - tt_len - 4.8 - c, -4 - c, -3 - c]) cube([6 + 2*c, 8 + 2*c, 6 + 2*c]); }
function ft_tab_s() = tt_len - tt_axle_from_front + 4.8 - 3;   // tab hole distance from the axle (60.55, matches lib.tt_motor)
// drop-in channel: hull of the child with a copy on the bed (vertical insertion path)
module ft_drop() { hull() { children(); translate([0, 0, -150]) children(); } }
module ft_bed_clip() { intersection() { children(); translate([-250, -250, -1]) cube([500, 500, 400]); } }
// complete motor cut: every envelope piece as a vertical drop-in channel (gearbox with 0.5 mm
// bridge sag, can with 1 mm sag), plus the cable-tie saddle groove around the can at tie_s
module ft_motor_cut(y, phi, tie_s) {
    ft_bed_clip() {
        ft_drop() translate([0, 0, 0.5]) ft_motor_at(y, phi) ft_gb(ft_c);
        ft_drop() translate([0, 0, 1]) ft_motor_at(y, phi) ft_can(ft_c);
        ft_drop() ft_motor_at(y, phi) ft_shafts(ft_c);
        ft_drop() ft_motor_at(y, phi) ft_tab(ft_c);
        ft_motor_at(y, phi) translate([-tie_s, 0, 0]) rotate([0, 90, 0]) cyl(tt_can_d + 2*ft_c + 2*ft_tie_deep, ft_tie_w, center = true);
    }
}
// outer foot M3 tab pin: clearance hole along X through both end-block cheeks, nut slot open
// to the bed in the +X cheek (nut at X ft_tab_nut_x .. +2.8)
module ft_tab_bolt(y, phi) {
    tc = [0, y + ft_tab_s()*sin(phi), wheel_axle_z + ft_tab_s()*cos(phi)];
    translate([-ft_end_hw - 1, tc[1], tc[2]]) rotate([0, 90, 0]) cyl(clearance_d(3), 2*ft_end_hw + 2, fn = 24);
    translate([ft_tab_nut_x, tc[1], tc[2]]) rotate([0, 90, 0]) nut_slot(3, tc[2] + 1, nut_h(3) + 0.4);
}
// wheel cavity: 3 mm clearance all round, open to the bottom (caller clips it to the shell inner)
module ft_wheel_cut(y) {
    for (sx = [-1, 1]) translate([sx*(wheel_x - wheel_w/2 - ft_wheel_clear), y, wheel_axle_z])
        rotate([0, sx*90, 0]) cyl(wheel_d + 2*ft_wheel_clear, wheel_w + 2*ft_wheel_clear);
}

// ============================================================================ OUTER FOOT
module ft_hull_o() { ft_shell_hull(foot_outer_l_bot, foot_outer_w_bot, foot_outer_l_top, foot_outer_w_top, foot_outer_h); }
module ft_inner_o() { ft_shell_inner(foot_outer_l_bot, foot_outer_w_bot, foot_outer_l_top, foot_outer_w_top, foot_outer_h, ft_side_ang_o, ft_end_ang_o); }
module ft_grown_o() { ft_shell_grown(foot_outer_l_bot, foot_outer_w_bot, foot_outer_l_top, foot_outer_w_top, foot_outer_h, ft_side_ang_o, ft_end_ang_o); }
module ft_side_o(sx) { ft_on_side(sx, ft_side_ang_o, foot_outer_w_bot/2) children(); }
module ft_end_o(sy) { ft_on_end(sy, ft_end_ang_o, foot_outer_l_bot/2) children(); }
ft_face_h_side_o = foot_outer_h / cos(ft_side_ang_o);   // 92.6 along the slope
ft_face_h_end_o = foot_outer_h / cos(ft_end_ang_o);     // 105.9

// tongue swept volume (below the plate only), 1 mm side and 2.5 mm bottom margin
module ft_tongue_sweep() {
    d = ft_pivot_up + foot_slot_depth + 2.5;
    intersection() {
        hull() for (a = [-ft_swing, 0, ft_swing]) translate([0, 0, ft_pivot_z]) rotate([a, 0, 0])
            translate([-foot_slot_w/2 - 1, -leg_tongue_w/2 - 1, -d]) cube([foot_slot_w + 2, leg_tongue_w + 2, d + 40]);
        translate([-60, -120, -1]) cube([120, 240, foot_outer_h - ft_plate_t + 1]);
    }
}

// internal ribs (clipped to the shell hull by the caller)
module ft_interior_o() {
    H = foot_outer_h;
    for (sy = [-1, 1]) mirror([0, sy < 0 ? 1 : 0, 0]) {
        translate([-ft_spine_hw, ft_rib_hw_o - 0.5, 0]) cube([2*ft_spine_hw, 80.5 - ft_rib_hw_o, 40.5]);   // spine: gearbox ceiling beam, joined to the centre rib
        translate([-ft_spine_hw, 61, 0]) cube([2*ft_spine_hw, 19, H]);      // column to the plate
        translate([-70, 80, 0]) cube([140, 8, H]);                           // can wall (tie groove)
        translate([-ft_end_hw, 88, 0]) cube([2*ft_end_hw, 42, 32]);          // end block (tab pin cheeks)
    }
    translate([-70, -ft_rib_hw_o, 0]) cube([140, 2*ft_rib_hw_o, H]);          // centre rib
}

module ft_loaf_profile(y0, L, Hb, r) {
    hull() {
        translate([y0, 0]) square([L, Hb - r]);
        translate([y0 + r, Hb - r]) circle(r);
        translate([y0 + L - r, Hb - r]) circle(r);
    }
}
// shell hull profile widened across X (clips the battery-box wedge to the end slopes); grow > 0
// offsets the end faces outward, < 0 inward
module ft_hull_wide_o(grow = 0) {
    g = grow / cos(ft_end_ang_o);
    ft_shell_hull(foot_outer_l_bot + 2*g, 400, foot_outer_l_top + 2*g, 400, foot_outer_h + (grow > 0 ? 3 : 0));
}
module ft_battery_box() {
    L = battery_box[0]; W = battery_box[1]; Hb = battery_box[2];
    x_edge = -foot_outer_w_bot/2; x_out = x_edge - W; y0 = ft_batt_y0; ym = y0 + L/2;
    x_end = -25;                                   // wedge fill reaches into the shell wall
    w = foot_wall;
    module loaf(x0, x1, yy0, LL, HH, rr, ext = 0) { translate([x0, 0, 0]) rotate([90, 0, 90]) linear_extrude(height = x1 - x0) { ft_loaf_profile(yy0, LL, HH, rr); translate([yy0, -ext]) square([LL, ext + 1]); } }
    difference() {
        union() {
            loaf(x_out, x_edge + 0.5, y0, L, Hb, ft_loaf_r);
            intersection() { loaf(x_edge - 0.5, x_end, y0, L, Hb, ft_loaf_r); ft_hull_wide_o(); }
            // harness straps over the top and down the outer face, blue tips at the bottom
            for (ys = [ym - 20, ym + 20]) {
                translate([x_out - 2.5, ys - 5, 0]) cube([W + 3, 10, Hb + 2.5]);
                intersection() { translate([x_edge, ys - 5, 0]) cube([x_end - x_edge, 10, Hb + 2.5]); ft_hull_wide_o(2.5); }
                translate([x_out - 5, ys - 5, 6]) cube([5, 10, 14]);
            }
            // knurled fittings and hose stubs on the front end, 45 deg gussets underneath
            for (xf = [x_out + 15, x_out + 38]) translate([xf, y0 + L - 0.5, 24]) {
                rotate([-90, 0, 0]) cylinder(d = 13, h = 6.5, $fn = 12);
                hull() {
                    rotate([-90, 0, 0]) cyl(8.7, 16.5, fn = 32);
                    translate([-4.35, -1.0, -20.35]) cube([8.7, 1.0, 20.35]);
                }
            }
        }
        ft_inner_o();
        // hollow shell: inner loaf one wall in, open at the bottom, stopped one wall short of
        // the foot shell and its end slopes, 45 deg roof over the wedge, one internal web
        difference() {
            intersection() {
                loaf(x_out + w, x_end, y0 + w, L - 2*w, Hb - w, ft_loaf_r - w, 2);
                rotate([90, 0, 0]) linear_extrude(height = 400, center = true)
                    polygon([[x_out - 1, -2], [x_out - 1, Hb - w], [x_edge + 0.3, Hb - w], [x_edge + Hb - w + 2.3, -2]]);
                union() { translate([x_out - 1, -200, -3]) cube([x_edge - x_out + 0.5, 400, Hb + 5]); ft_hull_wide_o(-w); }
            }
            ft_grown_o();
            translate([x_out + W/2 - 1.5, y0, -2]) cube([3, L, Hb]);
        }
        // door-panel scribe on the outer face (runs from the front end back to the rear)
        translate([x_out + 0.6, y0 + L - 6, 6]) rotate([90, 0, -90]) linear_extrude(height = 2) ft_outline(1.2) square([L - 12, Hb - 12 - 8]);
    }
}

module ft_ankle_block() {
    H = foot_outer_h;
    translate([0, 0, H]) rbox([ft_block[0], ft_block[1], ft_block[2]], 3);
    for (y = [0, ft_lock_r]) translate([0, y, ft_pivot_z]) rotate([0, 90, 0]) cyl(ankle_cyl_d, ft_block[0] + 2*ft_boss_proud, center = true);
}

module foot_outer() {
    H = foot_outer_h;
    door_v0 = 12; door_h = 68;
    hose_u = [-15.3, 15.3]; hose_v = 60.7;
    difference() {
        union() {
            difference() {
                union() {
                    difference() { ft_hull_o(); ft_inner_o(); }
                    intersection() { ft_hull_o(); ft_interior_o(); }
                    ft_ankle_block();
                    ft_battery_box();
                    // end faces: half-moon tombstone + inner plate on the outboard half, trim strip
                    // (front: hose-socket bosses, rear: two small holes)
                    for (sy = [-1, 1]) ft_end_o(sy) {
                        uo = 27 * sy;
                        ft_raise(1.2) translate([uo, 0]) ft_tombstone(22, 13, 28);
                        ft_raise(2.0) translate([uo - 11, 15]) square([22, 27.5]);
                        ft_raise(0.8) difference() {
                            translate([-30.6, 52]) square([61.2, 17.4]);
                            if (sy < 0) for (u = [-18, 18]) translate([u, 60.7]) circle(1.6);
                        }
                        if (sy > 0) for (u = hose_u) ft_hose_boss(u, hose_v);
                    }
                    // outboard side: panel trim strip and two corner trims above the door
                    ft_side_o(1) {
                        ft_raise(0.8) translate([-50, 82]) square([100, 4]);
                        for (u = [-42, 42]) ft_raise(0.8) translate([u, 0]) polygon([[-10, 81.5], [10, 81.5], [7, 89.5], [-7, 89.5]]);
                    }
                }
                // recesses: side door frame (outboard), straight side panel scribe (inboard),
                // end notch scribes, inner-plate slots, apron slots
                ft_side_o(1) ft_recess(0.6) ft_trap(206, 122, door_h, door_v0);
                ft_side_o(-1) ft_recess(0.6) ft_outline(1.5) difference() {
                    ft_trap(198.9, 198.9 - 2*54.3*tan(35.1), 54.3, 12);
                    translate([-34.75, 66.3 - 26]) square([69.5, 30]);
                }
                for (sy = [-1, 1]) ft_end_o(sy) {
                    uo = 27 * sy;
                    ft_recess(0.8) ft_outline(1.5) translate([-8.7, ft_face_h_end_o - 31.6]) square([17.4, 40]);
                    for (v = [33.5, 38]) translate([uo - 8, v, 1.0]) cube([16, 2.5, 3]);
                    for (u = [-40, 40]) ft_apron_slot(u);
                }
                ft_side_o(1) for (u = [-96 : 32 : 96]) ft_apron_slot(u);
                ft_side_o(-1) for (u = [-96, -64, -32]) ft_apron_slot(u);
            }
            // side door panel raised inside its frame recess, 0.3 below the face
            ft_side_o(1) translate([0, 0, -0.8]) linear_extrude(height = 0.5) ft_trap(201.6, 117.6, 63.6, door_v0 + 2.2);
        }
        // door inner scribe (0.5 into the panel, wall stays >= 2.4)
        ft_side_o(1) translate([0, 0, -0.7]) linear_extrude(height = 2) ft_outline(1.2) ft_trap(193, 109, 59, door_v0 + 4.5);
        // hose sockets in the front bosses
        ft_end_o(1) for (u = hose_u) translate([u, hose_v, -3]) cylinder(d = 8.7, h = 9, $fn = 32);
        // ankle slot through block and plate, tongue sweep below the plate
        translate([-foot_slot_w/2, -ft_slot_hl, H - ft_plate_t - 1]) cube([foot_slot_w, 2*ft_slot_hl, ft_plate_t + ft_block[2] + 2]);
        ft_tongue_sweep();
        // pivot and lock bores on the pivot plane, inboard nut pockets
        for (y = [0, ft_lock_r]) {
            translate([0, y, ft_pivot_z]) rotate([0, 90, 0]) cyl(clearance_d(ankle_bolt_m), 200, center = true, fn = 32);
            translate([-ft_block[0]/2 - ft_boss_proud - eps, y, ft_pivot_z]) rotate([0, 90, 0]) nut_pocket(ankle_bolt_m, 8);
        }
        // motors (drop-in channels), tab pins, wheels (cavities clipped to the shell inner)
        for (sy = [-1, 1]) {
            phi = sy * (90 + ft_motor_tilt_o);
            ft_motor_cut(sy*foot_axle_y, phi, 42);
            ft_tab_bolt(sy*foot_axle_y, phi);
            intersection() { ft_wheel_cut(sy*foot_axle_y); ft_inner_o(); }
        }
        // wire route: through the plate and block inside the ankle footprint, pass through the rib
        translate([20, -38, H - ft_plate_t - 1]) cyl(ft_wire_d, ft_plate_t + ft_block[2] + 2, fn = 32);
        translate([20, 0, 70]) rotate([90, 0, 0]) cyl(ft_wire_d, 30, center = true, fn = 32);
        // part label recessed into the rear face of the centre rib (hidden inside the shell)
        translate([25, -ft_rib_hw_o, 30]) rotate([90, 0, 0]) mirror([1, 0, 0]) label("FOOT OUTER R", 3);
    }
}

// ============================================================================ CENTRE FOOT
module ft_hull_c() { ft_shell_hull(foot_center_l_bot, foot_center_w_bot, foot_center_l_top, foot_center_w_top, foot_center_h); }
module ft_inner_c() { ft_shell_inner(foot_center_l_bot, foot_center_w_bot, foot_center_l_top, foot_center_w_top, foot_center_h, ft_side_ang_c, ft_end_ang_c); }
module ft_side_c(sx) { ft_on_side(sx, ft_side_ang_c, foot_center_w_bot/2) children(); }
module ft_end_c(sy) { ft_on_end(sy, ft_end_ang_c, foot_center_l_bot/2) children(); }
ft_face_h_side_c = foot_center_h / cos(ft_side_ang_c);
ft_face_h_end_c = foot_center_h / cos(ft_end_ang_c);

module ft_interior_c() {
    H = foot_center_h;
    translate([-70, -12, 0]) cube([140, 22, H]);                       // central rib: can arches, tie grooves
    translate([-ft_spine_hw, 8, 0]) cube([2*ft_spine_hw, 82, H]);      // front spine (45 deg gearbox pocket)
    translate([-ft_spine_hw, -90, 0]) cube([2*ft_spine_hw, 80, H]);    // rear spine (tilted gearbox pocket)
}
module foot_center() {
    H = foot_center_h;
    door_v0 = 14; door_h = 62;
    difference() {
        union() {
            difference() {
                union() {
                    difference() { ft_hull_c(); ft_inner_c(); }
                    intersection() { ft_hull_c(); ft_interior_c(); }
                    // caster stem block centred on the axis, 45 deg prow over the front slope
                    difference() {
                        hull() {
                            translate([-ft_stem[0]/2, ft_stem_y0, H - 0.1]) cube([ft_stem[0], ft_stem[1], 0.1]);
                            translate([-ft_stem[0]/2, ft_stem_y0, H - ft_prow_step]) cube([ft_stem[0], ft_stem[1], 0.1]);
                            translate([-ft_stem[0]/2, ft_stem_y0, H - ft_prow_drop])
                                cube([ft_stem[0], ft_stem[1] - ft_prow_drop + ft_prow_step, 0.1]);
                        }
                        ft_inner_c();
                    }
                    translate([-ft_stem[0]/2, ft_stem_y0, H]) linear_extrude(height = ft_stem[2]) offset(r = 3) offset(delta = -3) square([ft_stem[0], ft_stem[1]]);
                    // swivel-stop pin on the flat stem-block top (r 22, no ledge fin needed)
                    translate([0, caster_trail + ft_stop_r, H + ft_stem[2] - eps]) cyl(ft_pin_d, ft_pin_h + eps, fn = 32);
                    // side trim strips near the top of each side face
                    for (sx = [-1, 1]) ft_side_c(sx) ft_raise(0.8) translate([-30, ft_face_h_side_c - 14]) square([60, 6]);
                    // end faces: half-moon tombstone with a slotted inner plate
                    for (sy = [-1, 1]) ft_end_c(sy) {
                        ft_raise(1.2) ft_tombstone(27.5, 13, 38);
                        ft_raise(2.0) translate([-13, 16]) square([26, 34]);
                    }
                }
                // side door frames, apron slots, inner-plate slots
                for (sx = [-1, 1]) ft_side_c(sx) {
                    ft_recess(0.6) ft_trap(150, 60, door_h, door_v0);
                    for (u = [-60, -20, 20, 60]) ft_apron_slot(u);
                }
                for (sy = [-1, 1]) ft_end_c(sy) {
                    for (v = [42, 46.5]) translate([-9, v, 1.0]) cube([18, 2.5, 3]);
                    for (u = [-42, 42]) ft_apron_slot(u);
                }
            }
            for (sx = [-1, 1]) ft_side_c(sx) translate([0, 0, -0.8]) linear_extrude(height = 0.5) ft_trap(146, 57, 58.5, door_v0 + 1.6);
        }
        for (sx = [-1, 1]) ft_side_c(sx) translate([0, 0, -0.7]) linear_extrude(height = 2) ft_outline(1.2) ft_trap(138, 52, 53, door_v0 + 4);
        // caster bolt bore and nut slot (opens toward +X under the plate)
        translate([0, caster_trail, H - ft_plate_t - 1]) cyl(clearance_d(caster_bolt_m), ft_plate_t + ft_stem[2] + 2, fn = 48);
        translate([0, caster_trail, H - ft_plate_t - 8.4]) nut_slot(caster_bolt_m, 22, 8.4);
        // motors (drop-in channels), wheels
        ft_motor_cut(foot_axle_y, ft_phi_c_front, 55);
        ft_motor_cut(-foot_axle_y, ft_phi_c_rear, 38);
        for (sy = [-1, 1]) intersection() { ft_wheel_cut(sy*foot_axle_y); ft_inner_c(); }
        // wire route: behind the caster axis on the leg's arc, down through the stem block, the
        // plate and the centre rib to a z 70 tunnel that meets the existing pass through the rib
        translate([0, caster_trail - ft_wire_r, 70]) cyl(ft_wire_d, H + ft_stem[2] + 1 - 70, fn = 32);
        hull() for (x = [0, -20]) translate([x, caster_trail - ft_wire_r, 70]) sphere(d = ft_wire_d, $fn = 24);
        translate([-20, ft_rib_c_y, 70]) rotate([90, 0, 0]) cyl(ft_wire_d, ft_wire_pass, center = true, fn = 32);
        // label on the rear face of the central rib (inside the rear wheel bay)
        translate([-26, -12, 34]) rotate([90, 0, 0]) mirror([1, 0, 0]) label("FOOT CENTER", 2.5);
    }
}
