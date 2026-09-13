// fable-r2d2 — body.scad: body_lower() and body_upper(), the two stacked body rings.
// Included by r2d2.scad after params.scad and lib.scad. Every local name carries the prefix
// bd_ so it cannot collide with dome.scad / legs.scad / feet.scad / head_drive.scad.
//
// FRAMES (see r2d2.scad FRAMES)
//   Both modules are MODELLED in the body frame (z = 0 at the skirt bottom, +Y front,
//   +X droid's right) and body_upper() then translates by -body_lower_h so its print frame
//   has z = 0 at the seam, exactly as r2d2.scad expects.
//     body_lower: body-frame z 0 .. body_lower_h (135.1) plus the seam lip to 141.1;
//       printed height 141.1.
//     body_upper: body-frame z 135.1 .. body_height (381.1) for the ring, but the slip-ring
//       post stands slip_ring_post_h above the top plate to body z 399.1, so the PRINTED
//       height is 264.0, not body_upper_h (246.0). Still inside env_z = 315. params.scad's
//       body_upper_h is the skin height at the seam, not the part height (m1).
//   Skin features are quoted from research/proportions.md 2.3 / 2.4 as (s, y): s = arc
//   distance from the front (or rear) centreline, positive to the viewer's right when the
//   viewer faces that skin; y = distance down from the top of the body. Helpers:
//     bd_a(s) = azimuth in degrees, used as rotate([0,0,a]) so a point sits at
//               [-r sin a, r cos a] — the same convention dome.scad uses. Positive front s
//               therefore lands on -X (the droid's LEFT), which matches
//               research/drawings/photos/body-front.jpg (six coin slots on the viewer's left
//               = droid's right = negative s; octagon port on the viewer's right = +s).
//     bd_z(y) = body_height - y.
//   Rear features add base = 180 deg, so positive rear s lands on +X (the droid's right),
//   again "viewer's right" for someone standing behind the droid.
//
// INTERFACE (what every mating part may rely on; nothing here is a copy of another file's
// numbers — the names come from params.scad / head_drive.scad)
//   SEAM (body_lower top <-> body_upper bottom), body-frame z = body_lower_h = 135.1:
//     NOTE the flange is bd_flange_w = 16 wide and the bolt circle bd_bolt_r = 145.9, NOT
//     params.scad's seam_flange_w = 12 / r 148.9: at 148.9 the M4 clearance bore reached
//     r 151.15 and the lip socket wall is r 151.3, a 0.15 mm wall (B3). Measured wall now
//     3.15 mm outboard and 4.75 mm inboard. scripts/draw_robot.py still draws r 148.9.
//     - body_lower: internal flange r 138.9..156.5, z 130.1..135.1, seam_bolt_n M4 clearance
//       holes on r 145.9 at 22.5 + i*45 deg, hex nut pockets INSIDE the flange, opening DOWN,
//       z 130.1..133.7, with the bore carried on down to z 121.1 for the screw tip (M2).
//     - body_lower: locating lip, r 151.6..154.6, z 135.1..141.1 (seam_lip_h tall,
//       seam_lip_t thick), 15 deg lead-in chamfer on its top outer edge.
//     - body_upper: flange r 138.9..151.3, z 135.1..146.5, same bolt circle, plain holes.
//       The lip socket is the groove r 151.3..156.5, z 135.1..141.5 -> 0.3 mm each side.
//     - M4 x 20 socket cap from above, nut captive in the lower flange. Eight places. Each
//       bolt has a clear vertical column from the open top of body_upper: the integral deck
//       carries a 28 x 22 relief on every bolt azimuth out to the wall (M4), so the first
//       obstruction above a bolt head is 52.4 mm up (the ring rib at z 200).
//   SHOULDER (body_upper, both +X and -X), axis z = shoulder_z (313.9) = local 178.8:
//     - flat pad shoulder_pad_d (116) whose outer face is exactly |X| = body_r = 158.5, i.e.
//       the tangent plane; it is the face the shoulder_spacer stack bears on. The leg's
//       inboard face sits at |X| = body_r + shoulder_spacer = 166.5, so 8 mm of stack.
//     - internal boss shoulder_boss_d (120) behind it, but bd_sh_boss_t = 49 deep, not
//       params.scad's shoulder_boss_t = 30, because the fastener stack needs the length (M8):
//       from the pad face inwards, 16.2 counterbore for a 16 OD x 12 ID x 30 mm STEEL CRUSH
//       SLEEVE (|X| 128.5..158.5), a 40.5 x 3 seat for an M12 flat washer (125.5..128.5), then
//       a 16 mm M12 hex pocket (109.5..125.5). The sleeve, not the PETG, takes the clamp load
//       and the nyloc never bears on a printed floor. clearance_d(12) bore through the sleeve.
//       FASTENERS per flank: M12 x 130 class 8.8, one 16 x 12 x 30 steel sleeve, one 40 mm
//       flat washer, one DIN 985 M12 nyloc.
//     - SERVICE ACCESS to that nyloc (M3): a bd_sh_acc_d (26) vertical bore on the nut axis
//       (|X| 117.5, y 0) runs from z = shoulder_z up through the top plate, giving a straight
//       26 mm line of sight and turning the hex pocket into a drop-in nut trap (the lower half
//       of the hex still keys the nut). A skin window is impossible here: the pad is a 116 dia
//       disc on the skin (arc +/-58 about azimuth 90/270), so a 70 mm window would have to sit
//       at least 93 mm of arc off the axis and could not see down the bolt axis at all. The
//       bore is at r 104.5..130.5; it passes under the lazy-susan bottom race (r 57..114.3) for
//       26 x 10 mm at two azimuths 45 deg away from every race screw, and the dome hides it.
//     - TWO shoulder_index_d dowel holes, 20 mm deep from the pad face, at radius
//       shoulder_index_r, at shoulder_index_angles measured from straight below the axis
//       TOWARD THE FRONT: (y, z) = (0, -45) and (45 sin 18, -45 cos 18) = (13.90, -42.80).
//       legs.scad places its holes toward the REAR; rotating the leg forward by leg_lean
//       (the three-leg stance) puts leg hole 18 on body hole 0 AND leg hole 0 on body hole
//       18, so the operating stance takes two dowels and the two-leg stance takes one.
//     - The body carries NO horseshoe: the pad is a plain disc (legs.scad owns the horseshoe).
//   TOP PLATE (body_upper), top face z = body_top_plate_z (375.1), t = body_top_plate_t:
//     - central opening top_plate_opening_r, 3-spoke spider to a 30 mm hub with a
//       bd_slip_bore (13.0) bore and an M3 pinch clamp; slip-ring post bore is open top and
//       bottom. 13.0, not params.scad's slip_ring_d 12.5: the Adafruit 1195 body is 12.4 and
//       12.5 left the pinch clamp nothing to close (m6).
//     - 4 x M5 heat-set pockets from ABOVE at susan_hole_r on susan_hole_angles (bottom race
//       of the lazy susan), each in a 14 mm boss hanging 8 mm under the plate.
//     - susan_access_d access holes at susan_access_angles EXCEPT 180 deg: head_drive.scad
//       states that hole (0, -110.9) is covered by the drive base and is unusable.
//     - head_slot (radial x tangential) centred at radius head_wheel_r on -Y.
//     - the four hd_mount holes, clearance_d(hd_mount_m) through, 90 deg x 9 mm countersink
//       on the TOP face; the underside is flat (no ribs, no bosses) over x +/-56,
//       y -148..-74, and nothing of the body enters the swept keep-out x +/-66, y -160..-70,
//       z 160..378 (body frame) except the wall itself and the top plate.
//     - 4 x M8 rod nut counterbores (18 dia x 4 deep) from above at rod_r on
//       rod_angle0 + i*90; the nut stands 2.8 mm proud, 5.1 mm clear of the dome plate. The
//       rod_d + 0.6 bore now runs the WHOLE height of the ring under each counterbore (B1).
//     - NO harness pass-through: the 44 x 24 slot at y 100 lay under the lazy-susan bottom
//       race (r 57..114.3) and is deleted. The harness uses the 100 mm central opening (M9).
//     - 2 x bd_sh_acc_d (26) shoulder service bores at (+/-117.5, 0) - see SHOULDER.
//     - the wall continues body_lip_h above the plate as the dome-centring lip; its inner
//       face is r 154.9, so dome_plate_r_out (153.5) clears it by 1.4 mm.
//   DECK (body_upper), integral, top face at local tray_z_upper (40) = body frame 175.1:
//     annulus r 50..154.9 cut off by a chord at y = -114.9 (the 40 mm harness gap).
//   FLOOR (body_lower): four clearance_d(center_leg_bolt_m) holes at bd_leg_bolts = the
//     center_leg_bolts pattern offset by [0, center_leg_y_in_body] (-45), i.e. (+/-50, -77)
//     and (+/-50, -13), with hex nut pockets on TOP (bosses 7 mm tall so the 7.5 mm pocket
//     for the 6.8 mm M8 nut is inside them and still open at the top, m7). BOLT THE CENTRE LEG
//     ON BEFORE THE BATTERY GOES IN. The four holes are clear of the battery pocket now that
//     battery_y = 45 (pocket y -3.5..113.5), but a fitted battery still blocks a socket swing.
//     Every floor opening is cut by bd_floor_cuts() at the TOP level of body_lower(), because
//     difference(bd_lower_outer, bd_lower_cavity) leaves a solid slab z 0..floor_t-2.5 that
//     would otherwise plug them. The battery shelf carries 26 mm access
//     holes over all four so a socket reaches them (they stop at the shelf top face, so the
//     battery curb is not notched). The floor plate is SOLID under the whole 140 x 100 flange
//     footprint (x +/-70, y -95..+5): the skirt-bottom flats are at y = +/-94.85, so the
//     flange's rear edge is flush with the rear flat. The only cut inside that footprint is
//     the 14 x 20 wire slot at (0, -67) that meets the centre leg's wire channel exit
//     (legs.scad lg_wire_chan at leg-frame (0, -22)). The 60 x 40 cable opening moved from
//     Y = -60 to bd_cable_y = +55 (y 35..75), clear of the flange, still under the battery
//     shelf and clear of the rod columns (r 138); the radial shelf support ribs are cut back
//     to its edges so none of them starts in mid-air over it.
//
// DEVIATIONS from the brief, all forced by geometry and all deliberate:
//   1. The M8 rod nut in body_lower is NOT under the floor: rod_r = 138 lies outside the
//      skirt-bottom plate (max radius skirt_bottom_r = 116.6), so the rod column starts on
//      the battery shelf. The nut is a captive hex trap at z 46, opened downward with a slot
//      that faces the body axis; slide the nut in, feed the rod down, and tighten at the top
//      plate nut (18 mm counterbore) which is reachable before the lazy susan goes on.
//   2. The side vent notch is y 139..228, not 139..243.2: the lower 15 mm would have cut the
//      seam flange. The lower seam notch (y 270.3..340.9) is a recess, not a cut-out.
//   3. Both side notches are modelled on BOTH flanks: the club sheets dimension one notch per
//      skin edge and the front and rear skins meet at +/-90 deg, so front half + rear half
//      form one opening on each side (sheet note "combined side-vent opening 4.50 x 6.00 in").
//   4. The utility-arm relief is 165 x 38 x 8, not 165 x 43: the bay is only 41.3 mm tall.
//   5. The 78 mm speaker grille is nine 5 mm VERTICAL louvres in the front pocket vent door,
//      not a 5 x 5 grid: vertical slots in a vertical wall need no bridging at all, and the
//      photographs (research/drawings/photos/body-front.jpg item 6) show vertical slats.
//   6. The rear access opening is 120 x 90 at y 126..216 (body-frame z 165.1..255.1), well
//      below the head-drive wheel sweep, so its 10 mm inner lip cannot foul the tyre. Its head
//      is NOT a 120 mm flat bridge: the top bu_acc_ch (30) mm steps in at 45 deg on both sides
//      in 2 mm risers, so the longest span over the opening is 60 mm and the lip underside
//      carries a 45 deg chamfer (M5).
//   7. The club rear CENTRE TALL PANEL (s +/-62, y 118.3..241.1) is not modelled as a recess -
//      the access opening occupies it. Its outline is scribed 0.6 mm into the cover rebate
//      floor instead, so the cover can be cut to the club line (m5).
//   8. Three params.scad values are overridden locally, each with its reason at the constant:
//      seam_flange_w 12 -> bd_flange_w 16 with the bolt circle at 145.9 (B3), skirt_bottom_r
//      116.6 -> bd_skirt_br 118.5 so the skirt flare is 44.1 deg not 45.4 (m2), and
//      slip_ring_d 12.5 -> bd_slip_bore 13.0 (m6). shoulder_boss_t 30 is extended locally to
//      bd_sh_boss_t 49 for the crush-sleeve stack (M8).
//   9. The battery pocket is 20 mm longer than the cell on its +Y face (clear envelope
//      154 x 117 x 65, y -3.5..113.5) because the F2 terminals and their spade bodies stand
//      off that face; the curb keeps all four walls (M10).
//  10. Each flank carries a 20 mm cable grommet at azimuth 110 / 250, body z 240, NOT on the
//      shoulder azimuth: the shoulder pad is a 116 dia disc on the skin there and the side
//      louvre band runs azimuth 75.9..104.1 (M14).
//
// PRINTING. body_lower: skirt down, 135 mm + 6 mm lip tall. body_upper: seam face down,
//   246 mm tall. Everything on the skin is a recess or a through cut, so the outside needs
//   no support. Inside, tree supports are needed under the battery shelf (body_lower) and
//   under the electronics deck (body_upper); both are hidden. The skirt flares 41.9 mm out
//   over 41.3 mm of height (45.4 deg from vertical) — right at the limit, printable in PETG
//   at 0.20 mm but it is the one external surface that benefits from a 45 deg slowdown.
//   SUPPORT, body_lower: NONE. The battery shelf (z 41..45) now stands on bd_shelf_rib_n (24)
//   radial ribs, so the longest unsupported rim span is 40.9 mm and the shelf bridges it
//   (M11). Skirt, skirt ribs, floor, rod bosses, ring ribs (undersides steeper than 45 deg),
//   seam flange and lip are all self-supporting.
//   SUPPORT, body_upper: tree supports under the electronics deck inside r 131 (the sixteen
//   45 deg gussets carry r 131..156) and under the four regulator/DRV pads' overhang-free
//   tops — none needed there in practice. Both are reached through the open top of the ring
//   after printing. The horizontal louvre slots bridge 45 mm (front vents) and 30.4 mm (side
//   vents - each is split by a 6 mm post on the centreline, M5); the rear access opening
//   bridges 60 mm at the peak of its 45 deg head. No support is needed on any outside surface.

// ---------- local constants ----------
bd_ri        = body_r - body_wall;              // 154.9 inner skin radius
bd_seam      = body_lower_h;                    // 135.1 body-frame z of the seam
bd_top       = body_height;                     // 381.1 top edge of the lip
bd_plate_top = body_top_plate_z;                // 375.1
bd_plate_bot = body_top_plate_z - body_top_plate_t;  // 370.1
bd_lip_or    = bd_ri - 0.3;                     // 154.6 lip outer radius
bd_lip_ir    = bd_lip_or - seam_lip_t;          // 151.6 lip inner radius
bd_sock_ir   = bd_lip_ir - 0.3;                 // 151.3 socket inner radius in body_upper
// LOCAL OVERRIDE of params.scad seam_flange_w (12): at bd_bolt_r 148.9 the M4 clearance bore
// (outer edge 151.15) left a 0.15 mm wall to the lip socket wall (bd_sock_ir 151.3). The bolt
// circle moves inboard to 145.9 and the flange widens to 16 so the inner edge distance stays
// 4.75 mm. Both rings use bd_flange_w / bd_bolt_r, so the two flanges still match.
bd_flange_w  = 16;                              // was seam_flange_w = 12
bd_bolt_r    = bd_ri - seam_flange_w / 2 - 3;   // 145.9 seam bolt circle
bd_flange_ir = bd_ri - bd_flange_w;             // 138.9
// LOCAL OVERRIDE of params.scad skirt_bottom_r (116.6): 158.5 - 116.6 = 41.9 mm of flare over
// skirt_h 41.3 is 45.4 deg from vertical. 40.0 mm of flare gives 44.1 deg (m2).
bd_skirt_br  = body_r - 40;                     // 118.5
bd_shelf_rib_n = 24; bd_shelf_rib_a0 = 7.5;     // battery-shelf support ribs (M11)
// LOCAL OVERRIDE of params.scad slip_ring_d (12.5): the Adafruit 1195 body measures 12.4, so
// 12.5 is a press fit with no room for the M3 pinch clamp to close (m6).
bd_slip_bore = slip_ring_d + 0.5;               // 13.0
// Shoulder boss stack (M8): 16 OD x 12 ID x 30 steel crush sleeve against the pad, a 40 mm
// flat washer, then the M12 nyloc in a 16 mm hex pocket. The boss grows inboard to suit.
bd_sh_sleeve_od = 16.2; bd_sh_sleeve_l = 30;
bd_sh_wash_d = 40.5; bd_sh_wash_t = 3;
bd_sh_nut_h  = 16;
bd_sh_boss_t = bd_sh_sleeve_l + bd_sh_wash_t + bd_sh_nut_h;   // 49 (params shoulder_boss_t 30)
bd_sh_acc_d  = 26;                              // vertical service bore over each nyloc (M3)
bd_deck_top  = bd_seam + tray_z_upper;          // 175.1 deck top face (body frame)
bd_deck_bot  = bd_deck_top - tray_size[2];      // 171.1
bd_deck_gap  = 40;                              // harness gap, deck chord to the wall
bd_deck_chord = -(bd_ri - bd_deck_gap);         // -114.9
bd_shelf_top = battery_shelf_z;                 // 45 battery shelf top face
bd_shelf_bot = battery_shelf_z - 4;             // 41
// Centre-leg flange pattern in the BODY frame: the leg axis sits center_leg_y_in_body (-45)
// behind the body axis, so every floor feature moves with it: (+/-50, -77) and (+/-50, -13).
bd_leg_bolts = [for (q = center_leg_bolts) [q[0], q[1] + center_leg_y_in_body]];
bd_cable = [60, 40]; bd_cable_y = 55;           // cable opening, moved off the flange footprint
bd_wire = [14, 20]; bd_wire_y = center_leg_y_in_body - 22;   // -67: centre-leg wire channel exit
bd_ko        = [66, -160, -70, 160, 378];       // rear keep-out: |x|<=66, y in [-160,-70], z
bd_speaker_c = [-158, 291];                     // pocket-vent-door centre (s, y) — speaker
bd_acc       = [120, 90, bd_seam + 30];         // rear access opening: w, h, bottom z

// ---------- skin helpers (all take club sheet coordinates) ----------
function bd_a(s) = s * 57.2957795 / body_r;     // arc mm -> azimuth deg
function bd_z(y) = body_height - y;             // down-from-top mm -> body-frame z

// 2D pie sector of radius r between two azimuths, using pt(r,a) = [-r sin a, r cos a].
module bd_sec2d(r, a0, a1) {
    n = max(4, ceil(abs(a1 - a0) / 2));
    polygon(concat([[0, 0]],
        [for (i = [0 : n]) let (a = a0 + (a1 - a0) * i / n) [-r * sin(a), r * cos(a)]]));
}
module bd_prism(a0, a1, z0, z1, r = body_r + 8) {
    translate([0, 0, z0]) linear_extrude(z1 - z0) bd_sec2d(r, a0, a1);
}
// The shell of skin between body_r-depth and the outside, inside one (azimuth, z) window.
module bd_band(a0, a1, z0, z1, depth) {
    difference() {
        bd_prism(a0, a1, z0, z1);
        translate([0, 0, z0 - 1]) cylinder(r = body_r - depth, h = z1 - z0 + 2, $fn = 240);
    }
}
// Recess/cut on the skin from sheet coordinates. base = 0 front, 180 rear.
module skin_recess(s0, s1, y0, y1, d = 0.8, base = 0) {
    bd_band(base + bd_a(s0), base + bd_a(s1), bd_z(y1), bd_z(y0), d);
}
// Panel: 0.8 recess with a 2 mm frame and a deeper centre (the club double outline).
module skin_panel(s0, s1, y0, y1, base = 0, d1 = 0.8, w = 2, d2 = 1.2) {
    skin_recess(s0, s1, y0, y1, d1, base);
    if (d2 > d1 && s1 - s0 > 2.2 * w && y1 - y0 > 2.2 * w)
        skin_recess(s0 + w, s1 - w, y0 + w, y1 - w, d2, base);
}
// Outline groove only (used for the rear door, which carries panels inside it).
module skin_groove(s0, s1, y0, y1, w = 2.5, d = 1.2, base = 0) {
    difference() {
        skin_recess(s0, s1, y0, y1, d, base);
        skin_recess(s0 + w, s1 - w, y0 + w, y1 - w, d + 4, base);
    }
}
// Louvred vent: a 0.8 recess with n slots. thru > 0 cuts right through the skin.
module skin_louvres(s0, s1, y0, y1, n, base = 0, thru = 1, slot = 5, margin = 4) {
    skin_recess(s0, s1, y0, y1, 0.8, base);
    pitch = (y1 - y0 - 2 * margin) / n;
    for (i = [0 : n - 1]) {
        yy = y0 + margin + i * pitch + (pitch - slot) / 2;
        skin_recess(s0 + margin, s1 - margin, yy, yy + slot, thru > 0 ? 16 : 2.6, base);
    }
}
// Local thickening of the skin inwards to r_in with 45 deg top and bottom ramps.
module bd_pad(s0, s1, y0, y1, r_in, base = 0, zlo = -1e4) {
    z0 = max(bd_z(y1), zlo); z1 = bd_z(y0); c = body_r - r_in;
    intersection() {
        bd_prism(base + bd_a(s0), base + bd_a(s1), z0 - c - 1, z1 + c + 1);
        rotate_extrude($fn = 240)
            polygon([[r_in, z0], [body_r, z0 - c], [body_r, z1 + c], [r_in, z1]]);
        translate([0, 0, zlo > -1e3 ? zlo : z0 - c - 2])
            cylinder(r = body_r + 9, h = z1 + c + 4, $fn = 12);
    }
}

// ---------- shared structural helpers ----------
// Internal horizontal ring rib: 4 mm shelf with a 45 deg underside so it needs no support.
module bd_ring_rib(z0, w = ring_rib_w, t = ring_rib_t) {
    rotate_extrude($fn = 240)
        polygon([[bd_ri + 0.8, z0 - w - 2], [bd_ri + 0.8, z0 + t], [bd_ri - w, z0 + t], [bd_ri - w, z0]]);
}
// Vertical stiffening ribs on the inner skin.
module bd_vribs(z0, z1, n = vert_rib_n, t = vert_rib_t, w = vert_rib_w) {
    for (i = [0 : n - 1]) rotate([0, 0, i * 360 / n])
        translate([-t / 2, bd_ri - w, z0]) cube([t, w + 0.4, z1 - z0]);
}
// Put children on the axis of threaded rod i, with local -Y pointing at the body axis.
module bd_at_rod(i) { rotate([0, 0, rod_angle0 + i * 90]) translate([0, rod_r, 0]) children(); }
// Captive M8 hex nut, pocket open downward with a slot to slide the nut in from the axis side.
module bd_rod_nut(z0) {
    h = nut_h(8) + 0.7;
    translate([0, 0, z0 - eps]) {
        cylinder(d = nut_af(8) / cos(30), h = h, $fn = 6);
        translate([-nut_af(8) / 2, -34, 0]) cube([nut_af(8), 34, h]);
    }
}
// Rod column tied to the skin by a radial web.
module bd_rod_column(z0, z1) {
    for (i = [0 : rod_n - 1]) bd_at_rod(i) {
        cylinder(d = rod_boss_d, h = z1 - z0, $fn = 64);
        translate([-3, -1, 0]) cube([6, bd_ri - rod_r + 3.0, z1 - z0]);
    }
}

// ---------- body_lower: shell ----------
module bd_skirt_bot2d() {
    intersection() {
        circle(r = bd_skirt_br, $fn = 240);
        square([2 * bd_skirt_br + 4, 2 * skirt_flat_y], center = true);
    }
}
// One convex hull: truncated cone (skirt) capped by the cylindrical ring, so there is no
// union seam at z = skirt_h for the CSG to trip over.
module bd_lower_outer() {
    hull() {
        linear_extrude(0.02) bd_skirt_bot2d();
        translate([0, 0, skirt_h]) linear_extrude(0.02) circle(r = body_r, $fn = 240);
        translate([0, 0, bd_seam - 0.02]) linear_extrude(0.02) circle(r = body_r, $fn = 240);
    }
}
module bd_lower_cavity() {
    hull() {
        translate([0, 0, floor_t - 2.5]) linear_extrude(0.02) offset(r = -5) bd_skirt_bot2d();
        translate([0, 0, skirt_h]) linear_extrude(0.02) circle(r = bd_ri, $fn = 240);
        translate([0, 0, bd_seam + 22]) linear_extrude(0.02) circle(r = bd_ri, $fn = 240);
    }
}
// Twelve club skirt ribs, six on each curved flank, proud 3.2 mm at the bottom and flush at
// the top, so their outer face never passes body_r and the print needs no support.
module bd_skirt_ribs() {
    a_flat = atan(sqrt(bd_skirt_br * bd_skirt_br - skirt_flat_y * skirt_flat_y) / skirt_flat_y);
    span = 180 - 2 * a_flat;
    rt = skirt_h - 6;                                    // ribs stop short of the skirt top
    r_top = bd_skirt_br + (body_r - bd_skirt_br) * rt / skirt_h + 3.2;
    difference() {
        intersection() {
            hull() {
                linear_extrude(0.02) circle(r = bd_skirt_br + 3.2, $fn = 240);
                translate([0, 0, rt - 0.02]) linear_extrude(0.02) circle(r = r_top, $fn = 240);
            }
            union() for (i = [0 : 5]) for (m = [1, -1])
                rotate([0, 0, m * (a_flat + (i + 0.5) * span / 6)])
                    translate([-skirt_rib_t / 2, 40, 0]) cube([skirt_rib_t, body_r - 35, rt]);
        }
        bd_lower_cavity();
    }
}
// 60 x 40 cable opening, ahead of the centre-leg flange and under the battery shelf.
module bd_cable_cut(h) {
    translate([-bd_cable[0]/2, bd_cable_y - bd_cable[1]/2, -eps]) cube([bd_cable[0], bd_cable[1], h]);
}
// Floor plate with the centre-leg bolt pattern, the wire slot and the cable opening.
module bd_floor() {
    difference() {
        union() {
            intersection() {
                bd_lower_outer();
                translate([-200, -200, -eps]) cube([400, 400, floor_t + eps]);
            }
            // revision D: the bolted centre-leg flange bosses are gone; the carriage passes
            // through the floor (stance.scad st_carriage_sweep, st_housing_sweep).
        }
        translate([0, 0, floor_t]) rotate([0, 0, 180]) label("body_lower", size = 12);
    }
}
// Everything that must pass right through the floor. Subtracted at the top level of
// body_lower() because the skirt-bottom slab (z 0..floor_t - 2.5) is built by
// difference(bd_lower_outer, bd_lower_cavity) and would otherwise plug every one of them.
module bd_floor_cuts() {
    bd_cable_cut(floor_t + 2 * eps);
    // revision D centre-leg mechanism: carriage and housing sweeps and the actuator case
    st_carriage_sweep();
    st_housing_sweep();
    st_act_case_env();
}

// Battery shelf: 4 mm plate at battery_shelf_z with 8 mm curbs round the SLA footprint,
// four 26 mm socket windows over the centre-leg nuts and four strap slots.
module bd_battery_shelf() {
    bx = battery[0] / 2; by = battery[1] / 2;
    difference() {
        union() {
            translate([0, 0, bd_shelf_bot]) cylinder(r = bd_ri + 1.2, h = 4, $fn = 240);
            // M10: the F2 terminals stand 6 mm proud of the +Y face with 12-15 mm spade
            // bodies on them, so the pocket is 20 mm longer than the cell on that side: the
            // clear envelope is 154 x 117 x 65 at y -3.5..113.5. The curb keeps all four walls.
            translate([0, battery_y + 10, bd_shelf_top - eps])      // curbs
                difference() {
                    rbox([battery[0] + 11, battery[1] + 31, 8], r = 4);
                    translate([0, 0, -1]) rbox([battery[0] + 3, battery[1] + 23, 10], r = 3);
                }
            difference() {                                          // support ribs below
                for (i = [0 : bd_shelf_rib_n - 1]) rotate([0, 0, bd_shelf_rib_a0 + i * 360 / bd_shelf_rib_n])  // M11
                    translate([-2, 26, floor_t - 2]) cube([4, bd_ri - 26 + 1.2, bd_shelf_bot - floor_t + 2 + eps]);
                bd_cable_cut(bd_shelf_bot + 1);      // no rib may start in mid-air over the opening
            }
        }
        for (mx = [-1, 1]) for (yy = [-5, 40])
            translate([mx * (bx + 9.5) - 1.5, battery_y + yy - battery_strap_w / 2, bd_shelf_bot - 1])
                cube([3, battery_strap_w, 8]);
        translate([-40, -120, bd_shelf_bot - 1]) cube([80, 26, 8]);     // rear harness slot
        translate([-40, 121, bd_shelf_bot - 1]) cube([80, 26, 8]);      // front harness slot
    }
}
// Ribs and shelves are kept out of the space behind every through-vent so the slot cuts
// never meet an internal face tangentially.
// B4: only the nine vertical louvre slots of each pocket vent door cut right through the
// lower skin (body z 52.9..127.4, azimuth 290.2..315.6 and 110.2..135.6). The keepout is
// clipped to that band: 16 mm deep (clear of the ring rib at r 144.9 and the vertical ribs at
// r 146.9) and stopping at z 130.1, the seam-flange underside, so the flange, its bolt holes
// and its nut seats survive all the way round.
module bd_lower_rib_keepout() {
    for (b = [0, 180]) skin_recess(-201, -115, 251, 335, 16, base = b);
}
// Everything that hangs on the inside of the lower ring. Clipped to the outer loft by the
// caller so nothing can break the skin.
module bd_lower_inner() {
    difference() {
        union() {
            bd_lower_ribs();
            for (i = [0 : rod_n - 1]) bd_at_rod(i)                 // rod-column webs only
                translate([-3, -1, 41.5]) cube([6, bd_ri - rod_r + 3.0, bd_seam - 41.5]);
        }
        bd_lower_rib_keepout();
    }
    // The four rod bosses stand OUTSIDE the keepout: two of them (135 and 315 deg) sit on the
    // louvre-door azimuths and the old 26 mm deep keepout removed them completely (B4).
    for (i = [0 : rod_n - 1]) bd_at_rod(i)
        translate([0, 0, 41.5]) cylinder(d = rod_boss_d, h = bd_seam - 41.5, $fn = 64);
    bd_lower_pads();
}
module bd_lower_ribs() {
    bd_battery_shelf();
    bd_ring_rib(80);
    bd_ring_rib(bd_seam - seam_flange_t - ring_rib_t + 1);
    bd_vribs(bd_shelf_bot, bd_seam);
    translate([0, 0, bd_seam - seam_flange_t])                       // seam flange
        ring(2 * (bd_ri + 1.6), 2 * bd_flange_ir, seam_flange_t, fn = 240);
}
module bd_lower_pads() {
    bd_pad(bd_speaker_c[0] - 45, bd_speaker_c[0] + 45, bd_speaker_c[1] - 48, bd_speaker_c[1] + 48, 147.0, zlo = 43);
    bd_pad(136.8, 189.4, 280.1, 332.2, 147.5, zlo = 43);                       // front octagon port
    bd_pad(118.7, 171.4, 280.2, 332.3, 147.5, base = 180, zlo = 43);           // rear octagon port
    bd_pad(-26.6, 26.6, 280.1, 332.2, 150.5, zlo = 43);                        // front power coupling
    bd_pad(-26.6, 26.6, 280.2, 332.3, 150.5, base = 180, zlo = 43);            // rear power coupling
    bd_pad(-70, 70, 275, 307, 149.0, base = 180);                    // charge port + switch pad
}
// Locating lip above the seam face, with a 1.5 mm lead-in chamfer.
module bd_lower_lip() {
    rotate_extrude($fn = 240) polygon([
        [bd_lip_ir, bd_seam - 4], [bd_lip_or, bd_seam - 4], [bd_lip_or, bd_seam + seam_lip_h - 1.5],
        [bd_lip_or - 1.5, bd_seam + seam_lip_h], [bd_lip_ir, bd_seam + seam_lip_h]]);
}

// Inner pocket concentric with the skin: removes everything inside r_in in one (s, y) window.
module bd_inner_pocket(s0, s1, y0, y1, r_in, base = 0) {
    intersection() {
        bd_prism(base + bd_a(s0), base + bd_a(s1), bd_z(y1), bd_z(y0));
        cylinder(r = r_in, h = bd_top, $fn = 240);
    }
}
// Place children on the skin tangent plane: local +X tangential, +Y up, +Z into the body.
module bd_at_skin(a, z) { rotate([0, 0, a]) translate([0, body_r, z]) rotate([90, 0, 0]) children(); }
// Vertical louvre slots inside a recessed door (no bridging at all on a vertical wall).
module bd_vslots(s0, s1, y0, y1, n, base = 0, w = 5) {
    pitch = (s1 - s0) / n;
    for (i = [0 : n - 1]) {
        sc = s0 + (i + 0.5) * pitch;
        skin_recess(sc - w / 2, sc + w / 2, y0, y1, 14, base);
    }
}
// Panel recess on the body side, given directly in azimuth (used for the seam-edge notches).
module bd_side_panel(a0, a1, z0, z1, w = 2.5) {
    for (m = [1, -1]) {
        bd_band(m * a0, m * a1, z0, z1, 0.8);
        bd_band(m * (a0 + bd_a(w)), m * (a1 - bd_a(w)), z0 + w, z1 - w, 1.2);
    }
}
// ---------- body_lower: skin features ----------
module bd_lower_skin_cuts() {
    // front, row of short panels (proportions.md 2.3)
    for (p = [[-84.1, -49.4], [-32.0, 32.0], [49.4, 108.0], [118.9, 171.0]])
        skin_panel(p[0], p[1], 249.7, 271.4);
    // front pocket vent door: recessed door with nine 5 mm vertical louvres; the speaker
    // fires through it (speaker_d x speaker_depth envelope is kept clear behind).
    skin_panel(-197.0, -118.9, 249.7, 332.2, d2 = 0.8);
    bd_vslots(-193.0, -122.9, 253.7, 328.2, 9);
    // front bottom row
    skin_panel(-108.0, -39.6, 280.1, 332.2);            // coin return, left
    skin_panel(-26.6, 26.6, 280.1, 332.2);              // power coupling panel
    skin_panel(40.2, 70.6, 280.1, 332.2);               // coin return, right
    skin_panel(79.3, 96.6, 280.1, 332.2);               // small panel
    skin_panel(105.3, 122.7, 280.1, 332.2);             // small panel
    skin_panel(136.8, 189.4, 280.1, 332.2, d2 = 0.8);   // octagon port surround
    bd_at_skin(bd_a(163.1), bd_z(306.15)) {             // octagon pocket, 51 across flats
        translate([0, 0, -2]) linear_extrude(10.4) rotate(22.5) circle(d = 51 / cos(22.5), $fn = 8);
    }
    bd_at_skin(0, bd_z(306.15)) translate([0, 0, -2]) cylinder(d = 40, h = 5, $fn = 96);
    // rear (base = 180)
    skin_groove(-108.1, 108.1, bd_z(bd_seam) - 0.1, 338.6, w = 2.5, d = 1.2, base = 180);
    for (p = [[-98.3, -39.7], [-26.6, 26.6], [39.7, 98.3], [118.7, 171.1]])
        skin_panel(p[0], p[1], 249.8, 271.5, base = 180);
    skin_panel(-98.3, -39.7, 280.2, 332.3, base = 180);
    skin_panel(-26.6, 26.6, 280.2, 332.3, base = 180);
    skin_panel(39.7, 98.3, 280.2, 332.3, base = 180);
    skin_panel(118.7, 171.4, 280.2, 332.3, base = 180, d2 = 0.8);
    bd_at_skin(180 + bd_a(145.05), bd_z(306.25))
        translate([0, 0, -2]) linear_extrude(10.4) rotate(22.5) circle(d = 51 / cos(22.5), $fn = 8);
    bd_at_skin(180, bd_z(306.25)) translate([0, 0, -2]) cylinder(d = 40, h = 5, $fn = 96);
    skin_panel(-197.2, -119.0, 249.8, 332.3, base = 180, d2 = 0.8);
    bd_vslots(-193.2, -123.0, 253.8, 328.3, 9, base = 180);
    // rear panel hardware: charge jack and main rocker switch, z ~ 90
    // M7: the panel behind both is counterbored from the inside so the rocker's 0.8-3.5 mm snap
    // fingers and the L722A jack's ~6 mm bushing thread can seat. The counterbores are
    // CONCENTRIC with the skin (bd_inner_pocket), not flat slabs: a flat pocket 3 mm inside the
    // tangent plane leaves only 0.52 mm of wall 20 mm off its centre. Panel measured radially:
    // jack 3.0..4.2 mm, rocker 2.4..3.6 mm (the spread is the 0.8/1.2 club panel recesses that
    // run across both). The 5 mm hardware pad survives only as the surround.
    bd_at_skin(180 + bd_a(-40), 90) translate([0, 0, -3]) cylinder(d = 7.9, h = 16, $fn = 48);
    bd_inner_pocket(-48, -32, 283.1, 299.1, 154.3, base = 180);
    bd_at_skin(180 + bd_a(40), 90) translate([-18.4, -10.55, -3]) cube([36.8, 21.1, 8]);
    bd_inner_pocket(18, 62, 277.1, 305.1, 154.9, base = 180);
    // side seam notches, front and rear halves combined, both flanks
    bd_side_panel(73.6, 106.4, 42.5, 110.8);
}
// Proud detail that lives inside a recess (added after the cuts).
module bd_lower_proud() {
    for (q = [[bd_a(163.1), bd_z(306.15)], [180 + bd_a(145.05), bd_z(306.25)]])
        bd_at_skin(q[0], q[1]) {
            translate([0, 0, 5.5]) cylinder(d = 30, h = 3.5, $fn = 96);
            translate([0, 0, 3.0]) cylinder(d = 26, h = 2.5, $fn = 96);
            translate([0, 0, 0.5]) cylinder(d = 22, h = 2.5, $fn = 96);
        }
    for (q = [[0, bd_z(306.15)], [180, bd_z(306.25)]])
        bd_at_skin(q[0], q[1]) translate([0, 0, 0.6]) cylinder(d = 24, h = 3.4, $fn = 96);
}

// Internal cuts of the lower ring: seam bolts, rod bores and the speaker mount clearance.
module bd_lower_inner_cuts() {
    for (i = [0 : seam_bolt_n - 1]) rotate([0, 0, 22.5 + i * 45]) translate([0, bd_bolt_r, 0]) {
        // M2: the hex runs UP into the flange (z 130.1..133.7) instead of sitting below it in
        // the ring rib, and the clearance bore runs on down to z 121.1 for the M4 x 20 tip.
        translate([0, 0, bd_seam - seam_flange_t - 9]) through_hole(seam_bolt_m, seam_flange_t + 11);
        translate([0, 0, bd_seam - seam_flange_t]) nut_pocket(seam_bolt_m, nut_h(seam_bolt_m) + 0.4);
    }
    for (i = [0 : rod_n - 1]) bd_at_rod(i) {
        translate([0, 0, 45.5]) cylinder(d = rod_d + 0.6, h = bd_seam - 43, $fn = 48);
        bd_rod_nut(46);
    }
    // speaker envelope behind the front pocket vent door
    bd_at_skin(bd_a(bd_speaker_c[0]), bd_z(bd_speaker_c[1]))
        translate([0, 0, 14]) cylinder(d = speaker_d + 6, h = speaker_depth + 8, $fn = 96);
}
module bd_speaker_bosses() {
    bd_at_skin(bd_a(bd_speaker_c[0]), bd_z(bd_speaker_c[1]))
        for (mx = [-1, 1], my = [-1, 1]) translate([mx * 30, my * 30, 8])
            difference() {
                cylinder(d = 12, h = 10, $fn = 48);
                translate([0, 0, 10.001]) mirror([0, 0, 1]) insert_hole(3, 6.5);
            }
}
// Flat internal pad behind the rear charge jack and the main rocker switch.
module bd_rear_hardware_pad() {
    for (q = [[180 + bd_a(-40), 90], [180 + bd_a(40), 90]])
        bd_at_skin(q[0], q[1]) translate([0, 0, 6]) linear_extrude(5) square([56, 40], center = true);
}

// ================= body_lower =================
module body_lower() {
    difference() {
        union() {
            difference() {
                union() {
                    difference() { bd_lower_outer(); bd_lower_cavity(); }
                    intersection() {
                        bd_lower_outer();
                        union() { bd_lower_inner(); bd_speaker_bosses(); bd_rear_hardware_pad(); }
                    }
                    bd_skirt_ribs();
                    bd_floor();
                    bd_lower_lip();
                }
                bd_lower_inner_cuts();
                bd_floor_cuts();
                bd_lower_skin_cuts();
            }
            bd_lower_proud();
            st_shaft_bosses();          // revision D guide shafts (stance.scad)
        }
        st_shaft_boss_cuts();
    }
}

// ================= body_upper =================
module bu_outer() { translate([0, 0, bd_seam]) cylinder(r = body_r, h = bd_top - bd_seam, $fn = 240); }
module bu_cavity() { translate([0, 0, bd_seam - 2]) cylinder(r = bd_ri, h = bd_top - bd_seam + 4, $fn = 240); }
// Rear keep-out: no rib, boss or shelf may stand on the inner skin behind the head drive or
// behind the rear access opening (head_drive.scad INTERFACE, swept wheel to r 150.9).
module bu_keepout() { translate([-bd_ko[0], bd_ko[1], bd_ko[3]])
    cube([2 * bd_ko[0], bd_ko[2] - bd_ko[1], bd_ko[4] - bd_ko[3]]); }

// Shoulder: flat pad at |X| = body_r on a 45 deg conical fairing, 30 mm boss behind it.
module bu_shoulder_solid(side) {
    intersection() {
    translate([-200, -200, bd_seam]) cube([400, 400, bd_plate_top - bd_seam]);
    translate([0, 0, shoulder_z]) rotate([0, side * 90, 0]) {
        translate([0, 0, body_r - 21.3])
            cylinder(d1 = 158.6, d2 = shoulder_pad_d, h = 21.3, $fn = 160);
        translate([0, 0, body_r - shoulder_boss_t])
            cylinder(d = shoulder_boss_d, h = shoulder_boss_t - 19.3, $fn = 160);
        // M8: the boss grows inboard from 30 to bd_sh_boss_t (49) so the crush sleeve, the
        // 40 mm washer and a 16 mm nyloc pocket each get their own length.
        translate([0, 0, body_r - bd_sh_boss_t])
            cylinder(d = 52, h = bd_sh_boss_t - shoulder_boss_t + eps, $fn = 96);
    } }
}
module bu_shoulder_gussets(side) {
    intersection() {
        cylinder(r = bd_ri + 1, h = bd_plate_bot + 3, $fn = 240);  // m3: never proud of the plate
        union() for (ang = [45, 90, 135, 225, 270, 315])
            translate([0, 0, shoulder_z]) rotate([ang, 0, 0])
                translate([side > 0 ? 120 : -155, 52, -2.5]) cube([35, 78, 5]);
    }
}
module bu_shoulder_cuts(side) {
    translate([0, 0, shoulder_z]) rotate([0, side * 90, 0]) {
        translate([0, 0, -40]) cylinder(d = clearance_d(shoulder_bolt_m), h = body_r + 42, $fn = 64);
        // M8: 16.2 counterbore for the 16 OD x 12 ID x 30 steel crush sleeve (it, not the PETG,
        // carries the clamp load), then a 40.5 x 3 seat for the M12 flat washer, then a 16 mm
        // hex pocket so the DIN 985 nyloc (12.9 tall) is captive and never bears on printed floor.
        translate([0, 0, body_r - bd_sh_sleeve_l])
            cylinder(d = bd_sh_sleeve_od, h = bd_sh_sleeve_l + eps, $fn = 64);
        translate([0, 0, body_r - bd_sh_sleeve_l - bd_sh_wash_t])
            cylinder(d = bd_sh_wash_d, h = bd_sh_wash_t + eps, $fn = 64);
        translate([0, 0, body_r - bd_sh_boss_t - eps])
            cylinder(d = nut_af(shoulder_bolt_m) / cos(30), h = bd_sh_nut_h + eps, $fn = 6);
    }
    // M3: a straight vertical service bore over each nyloc pocket, from the nut axis up through
    // the top plate. It gives a 26 mm line of sight and turns the hex pocket into a drop-in nut
    // trap (the lower half of the hex still keys the nut). It sits at r 104.5..130.5, clear of
    // the lazy-susan bottom race (r 114.3) at the two azimuths used, and is hidden by the dome.
    translate([side * (body_r - bd_sh_boss_t + bd_sh_nut_h / 2), 0, shoulder_z])
        cylinder(d = bd_sh_acc_d, h = bd_top - shoulder_z + 1, $fn = 64);
    // revision D: the index dowel holes are replaced by the sensed lock (stance.scad st_lock_cuts)
}

// Electronics deck, integral: annulus r 50..wall cut off by the harness chord at y = -114.9.
module bu_deck_2d() {
    difference() {
        circle(r = bd_ri + 1.0, $fn = 240);
        circle(r = 50, $fn = 120);
        translate([-200, -400 + bd_deck_chord]) square([400, 400]);
    }
}
// M4: six of the eight seam bolts sat under the integral deck with 24.6 mm of headroom. Each
// bolt axis now has a 32 x 30 relief through the deck and its gussets out to the wall, so a
// stubby hex driver has a clear vertical column from the open top of the ring to the bolt head.
module bu_deck_reliefs() {
    for (i = [0 : seam_bolt_n - 1]) rotate([0, 0, 22.5 + i * 45])
        translate([-14, 136, bd_deck_bot - 27]) cube([28, 22, tray_size[2] + 28]);
}
module bu_deck() { difference() { bu_deck_solid(); bu_deck_reliefs(); } }
module bu_deck_solid() {
    translate([0, 0, bd_deck_bot]) linear_extrude(tray_size[2]) bu_deck_2d();
    intersection() {
        translate([0, 0, bd_seam + 12]) linear_extrude(120) bu_deck_2d();
        union() {
            for (i = [0 : 15]) rotate([0, 0, 11.25 + i * 22.5]) translate([-1.6, 0, 0])  // 45 deg gussets
                rotate([90, 0, 90]) linear_extrude(3.2)
                    polygon([[131, bd_deck_bot], [bd_ri + 1, bd_deck_bot], [bd_ri + 1, bd_deck_bot - 25]]);
            for (i = [0 : 7]) rotate([0, 0, 22.5 + i * 45])                        // inner stiffeners
                translate([-1.6, 48, bd_deck_bot - 8]) cube([3.2, 56, 8 + eps]);
        }
    }
}

// Top plate, spider, slip-ring post and the lazy-susan bottom-race bosses.
module bu_topplate() {
    difference() {
        translate([0, 0, bd_plate_bot]) cylinder(r = bd_ri + 1.6, h = body_top_plate_t, $fn = 240);
        translate([0, 0, bd_plate_bot - 1])
            cylinder(r = top_plate_opening_r, h = body_top_plate_t + 2, $fn = 160);
    }
    for (i = [0 : 2]) rotate([0, 0, i * 120])
        translate([-7, 11, bd_plate_bot]) cube([14, 41, body_top_plate_t]);
    translate([0, 0, bd_plate_bot]) cylinder(d = 30, h = body_top_plate_t + slip_ring_post_h, $fn = 96);
    for (a = susan_hole_angles) rotate([0, 0, a]) translate([0, susan_hole_r, bd_plate_bot - 8])
        cylinder(d = 14, h = 8 + eps, $fn = 48);
}
module bu_topplate_cuts() {
    // slip ring clamped in the post
    translate([0, 0, bd_plate_bot - 1]) cylinder(d = bd_slip_bore, h = body_top_plate_t + slip_ring_post_h + 2, $fn = 64);
    translate([-1.1, -16, bd_plate_top]) cube([2.2, 16, slip_ring_post_h + 1]);
    translate([-20, -9, bd_plate_top + 15]) rotate([0, 90, 0]) cylinder(d = clearance_d(3), h = 40, $fn = 32);
    translate([-15.01, -9, bd_plate_top + 15]) rotate([0, 90, 0]) cylinder(d = nut_af(3) / cos(30), h = 3, $fn = 6);
    // lazy susan bottom race: M5 inserts from above, access holes except the blocked one
    for (a = susan_hole_angles) rotate([0, 0, a]) translate([0, susan_hole_r, bd_plate_top - 12])
        cylinder(d = insert_d(susan_screw_m), h = 12 + eps, $fn = 32);
    for (a = susan_access_angles) if (a != 180) rotate([0, 0, a])
        translate([0, susan_hole_r, bd_plate_bot - 1]) cylinder(d = susan_access_d, h = body_top_plate_t + 2, $fn = 48);
    // friction-drive wheel slot and the four head_drive mount screws
    translate([-head_slot[1] / 2, -(head_wheel_r + head_slot[0] / 2), bd_plate_bot - 1])
        cube([head_slot[1], head_slot[0], body_top_plate_t + 2]);
    for (h = hd_mount) translate([h[0], h[1], 0]) {
        translate([0, 0, bd_plate_bot - 1]) cylinder(d = clearance_d(hd_mount_m), h = body_top_plate_t + 2, $fn = 32);
        translate([0, 0, bd_plate_top - 2.25]) cylinder(d1 = clearance_d(hd_mount_m), d2 = 9, h = 2.25 + eps, $fn = 32);
    }
    // M8 rod nut counterbores from above, and the harness pass-through
    for (i = [0 : rod_n - 1]) bd_at_rod(i) translate([0, 0, bd_plate_top - 4]) cylinder(d = 18, h = 4 + eps, $fn = 48);
    // M9: the 44 x 24 harness pass-through at y 100 is deleted - it lay under the lazy-susan
    // bottom race (r 57..114.3). The harness passes through the 100 mm central opening.
}
// Ribs (trimmed by the rear keep-out) and the seam flange / lip socket.
module bu_ribs() {
    translate([0, 0, bd_seam + 10.4]) bd_rod_column(bd_seam + 10.4, bd_plate_bot);
    bd_ring_rib(200); bd_ring_rib(262); bd_ring_rib(336);
    bd_vribs(bd_seam + 11.4, bd_plate_bot);
}
module bu_flange() {
    rotate_extrude($fn = 240) polygon([
        [bd_flange_ir, bd_seam], [bd_sock_ir, bd_seam], [bd_sock_ir, bd_seam + seam_lip_h + 0.4],
        [bd_ri + 1.6, bd_seam + seam_lip_h + 0.4], [bd_ri + 1.6, bd_seam + 11.4],
        [bd_flange_ir, bd_seam + 11.4]]);
}
module bu_flange_cuts() {
    for (i = [0 : seam_bolt_n - 1]) rotate([0, 0, 22.5 + i * 45]) translate([0, bd_bolt_r, bd_seam - 1])
        cylinder(d = clearance_d(seam_bolt_m), h = 13.4, $fn = 32);
}

// Rear access opening (120 x 90) with a 10 mm thick inner lip and four M3 cover inserts.
bu_acc_s = 60; bu_acc_y0 = 126; bu_acc_y1 = 216; bu_acc_ch = 30;
// M5: the head of the opening is not a 120 mm flat bridge any more. The top 30 mm steps in at
// 45 deg on both sides (2 mm risers), so the longest unsupported span is the 60 mm at the peak.
module bu_acc_cut(d) {
    n = 15;
    skin_recess(-bu_acc_s, bu_acc_s, bu_acc_y0 + bu_acc_ch, bu_acc_y1, d, 180);
    for (i = [0 : n - 1]) {
        yy = bu_acc_y0 + i * bu_acc_ch / n;
        hw = bu_acc_s - bu_acc_ch + (i + 1) * bu_acc_ch / n;
        skin_recess(-hw, hw, yy, yy + bu_acc_ch / n + 0.01, d, 180);
    }
}
// M5: 45 deg chamfer under the 10 mm inner lip so its underside is not a full overhang.
module bu_acc_lip_chamfer() {
    intersection() {
        bd_prism(180 - bd_a(bu_acc_s + 12), 180 + bd_a(bu_acc_s + 12),
                 bd_z(bu_acc_y1) - 1, bd_z(bu_acc_y1) + 9);
        translate([0, 0, bd_z(bu_acc_y1)]) cylinder(r1 = 155.0, r2 = 146.4, h = 8.6, $fn = 240);
    }
}
module bu_acc_lip() {
    difference() {
        intersection() {
            bd_prism(180 - bd_a(bu_acc_s + 10), 180 + bd_a(bu_acc_s + 10), bd_z(bu_acc_y1 + 10), bd_z(bu_acc_y0 - 10));
            difference() {
                cylinder(r = bd_ri + 1.6, h = bd_top, $fn = 240);
                cylinder(r = 146.5, h = bd_top, $fn = 240);
            }
        }
        bu_acc_cut(20);
        bu_acc_lip_chamfer();
    }
}
module bu_acc_lip_cuts() {
    for (ms = [-1, 1], my = [0, 1])
        bd_at_skin(180 + bd_a(ms * (bu_acc_s + 4.5)), bd_z(my > 0 ? bu_acc_y0 - 4.5 : bu_acc_y1 + 4.5))
            // B2: start at the 2.0 mm rebate floor, not 2.6, so the hole is not a sealed
            // cavity behind a 0.6 mm skin; it stops 3 mm short of the lip inner face (r 146.5).
            translate([0, 0, 2.0 - eps]) cylinder(d = insert_d(3), h = insert_depth(3) + 1, $fn = 32);
}
module bu_pads() { bd_pad(-110, 110, 16, 103, 147.5); }      // utility-arm bay backing (M1: 2.4 mm skin)

// M14: cable entry from the outer legs. The leg wire bore leaves the leg at |X| 166.5, body
// z ~239, so each flank gets a 20 mm grommet hole with a 2 mm proud lip and a tie-down lug.
// It CANNOT sit on the shoulder azimuth: the shoulder pad is a 116 dia disc on the skin
// (z 255.9..371.9, arc +/-58 about azimuth 90/270) and the side louvre band is azimuth
// 75.9..104.1 / 255.9..284.1. Azimuth 110/250 at z 240 clears the louvres by 1.6 deg (4.4 mm
// arc), the pad by 55.5 mm, the ring rib at 262 (z 252..266) by 2 mm and the rear access lip
// (azimuth 154.7..205.3) by 40 deg.
bd_grommet_a = 110; bd_grommet_z = 240; bd_grommet_d = 20;
module bu_grommets() {
    // Clipped to the inner skin: a flat disc tangent to the 158.5 cylinder reaches r 159.1 at
    // its rim, which would have left a knife edge proud of the skin (measured 0.16 mm wall).
    intersection() {
        cylinder(r = bd_ri + 0.6, h = bd_top, $fn = 240);
        union() for (m = [1, -1]) bd_at_skin(m * bd_grommet_a, bd_grommet_z) {
            translate([0, 0, body_wall - 1.4]) cylinder(d = bd_grommet_d + 8, h = 3.4, $fn = 64);
            translate([0, -22, body_wall - 1.4]) cylinder(d = 14, h = 9, $fn = 32);
        }
    }
}
module bu_grommet_cuts() {
    for (m = [1, -1]) bd_at_skin(m * bd_grommet_a, bd_grommet_z) {
        translate([0, 0, -1]) cylinder(d = bd_grommet_d, h = body_wall + 4, $fn = 64);
        translate([0, -22, 2]) cylinder(d = clearance_d(4), h = 8, $fn = 32);
    }
}

// ---------- electronics deck furniture ----------
module bu_boss(x, y, d, h, m, depth) {
    translate([x, y, bd_deck_top - eps]) difference() {
        cylinder(d = d, h = h, $fn = 40);
        translate([0, 0, h - depth]) cylinder(d = insert_d(m), h = depth + eps, $fn = 32);
    }
}
module bu_deck_furniture() {
    // M6: turned 90 deg. Board x -72..-16 (56 wide), y -113..-28 (85 long); hole pitch 49 in X
    // and 58 in Y; the USB/Ethernet edge faces -Y behind the rear access window instead of
    // butting into the side wall 7.8 mm away. The board is off the centreline because the deck
    // is an annulus r 50..155.9 chopped at y -114.9: on the -Y centreline only 64.9 mm of deck
    // is left, less than the 85 mm board. All four bosses land on the deck (r 55.1..129.2).
    // revision D: board moved 14 mm to -X (x -86..-30) so it clears the actuator mount cheeks at |x| 20..28
    for (h = pi4_holes) bu_boss(-86 + h[1], -113 + h[0], 7.5, 6, 2.5, 5.2);      // Raspberry Pi 4
    // M12: the KB2040 has no mounting holes - it gets a seat pad and two zip-tie slots.
    translate([-103.5, 21, bd_deck_top - eps]) cube([35, 18, 2]);                // KB2040 seat
    for (cx = [-45, -15, 15, 45]) {                                              // four DRV8833
        translate([cx - 13, 75 - 9, bd_deck_top - eps]) cube([26, 18, 2]);
        for (dx = [-10, 10]) bu_boss(cx + dx, 75, 6.5, 5, 2, 4.0);
    }
    // M12: the Pololu D36V50Fx carries its mounting holes at two opposite corners of the 25.4
    // square, not four on a 20 mm square. Two M2 heat-set bosses on the real corners, two plain
    // feet on the other two so the board cannot rock.
    for (cx = [45, 75, 105]) {
        for (sg = [-1, 1]) bu_boss(cx + sg * 10.2, -66 + sg * 10.2, 6.5, 5, 2, 4.0);
        for (sg = [-1, 1]) translate([cx + sg * 10.2, -66 - sg * 10.2, bd_deck_top - eps])
            cylinder(d = 6.5, h = 5, $fn = 32);
    }
    for (y = [-8, 12]) bu_boss(-125, y, 6.5, 5, 2.5, 4.0);                       // ADS1115
    translate([40, -105, bd_deck_top - eps]) cube([46, 20, 2]);                  // fuse-holder seat
}
module bu_deck_cuts() {
    for (q = [[0, 96], [-70, 58], [70, 58], [-135, -35], [135, -35], [-100, -60], [-100, -105], [110, -60]])
        translate([q[0] - 3, q[1] - 1.25, bd_deck_bot - 1]) cube([6, 2.5, tray_size[2] + 2]);
    for (yy = [18.5, 41.5])                                    // M12: KB2040 zip-tie slots
        translate([-92, yy - 1.25, bd_deck_bot - 1]) cube([12, 2.5, tray_size[2] + 2]);
    for (q = [[-115, -60, "PI4"], [-86, 46, "KB2040"], [0, 92, "DRV8833"],
              [75, -46, "5V / 12V"], [-125, 28, "ADC"], [63, -110, "FUSE"]])
        translate([q[0], q[1], bd_deck_top]) label(q[2], size = 7);
}

// Vents cut right through the skin, so no internal face may stand behind them.
module bu_vent_keepout() {
    translate([-36, 128, bd_seam + 12]) cube([72, 42, 272 - bd_seam - 12]);   // M13: floor 147.1
    for (m = [1, -1]) translate([m > 0 ? 128 : -170, -46, 150]) cube([42, 92, 94]);
}
module bd_side_louvres(a0, a1, z0, z1, n, slot = 3.6, margin = 5) {
    for (m = [1, -1]) {
        bd_band(m * a0, m * a1, z0, z1, 0.8);
        bd_band(m * (a0 + bd_a(2)), m * (a1 - bd_a(2)), z0 + 2, z1 - 2, 1.2);
        pitch = (z1 - z0 - 2 * margin) / n;
        am = (a0 + a1) / 2;                 // M5: 6 mm post on the centreline halves the bridge
        for (i = [0 : n - 1]) {
            zz = z0 + margin + i * pitch + (pitch - slot) / 2;
            bd_band(m * (a0 + bd_a(margin)), m * (am - bd_a(3)), zz, zz + slot, 9);
            bd_band(m * (am + bd_a(3)), m * (a1 - bd_a(margin)), zz, zz + slot, 9);
        }
    }
}
module bu_skin_cuts() {
    // --- front (proportions.md 2.3) ---
    for (i = [0 : 6]) {                                   // large data port, seven bays
        w = (183.4 - 6 * 3.5) / 7;
        s0 = -91.7 + i * (w + 3.5);
        skin_recess(s0, s0 + w, 2.5, 16.5, 1.2);
    }
    for (yb = [[17.4, 58.6], [59.7, 101.0]])              // two utility-arm bays
        skin_recess(-106.9, 106.9, yb[0], yb[1], 8.6);
    skin_panel(-171.0, -118.9, 17.4, 243.2);              // tall doors
    skin_panel(118.9, 171.0, 17.4, 243.2);
    skin_panel(-108.0, -40.7, 110.7, 154.2);              // panel above the coin slots
    for (i = [0 : 5]) skin_panel(-108.0, -82.0, 162.9 + i * 14.11, 169.41 + i * 14.11, d1 = 1.2, d2 = 0);
    skin_panel(-73.3, -40.7, 162.9, 241.0);               // narrow panel beside the slots
    skin_recess(-32.0, 32.0, 110.7, 241.0, 0.8);          // vent column
    skin_louvres(-26.5, 26.5, 114.7, 174.1, 10, slot = 3.4, margin = 5);
    skin_louvres(-26.5, 26.5, 177.7, 237.0, 10, slot = 3.4, margin = 6);
    skin_panel(40.7, 108.0, 110.7, 241.0);                // restraining-bolt panel
    // --- rear (proportions.md 2.4) ---
    skin_groove(-108.1, 108.1, 17.2, 246.2, w = 2.5, d = 1.2, base = 180);
    skin_panel(-98.3, 98.3, 27.0, 109.6, base = 180);     // upper wide panel
    skin_panel(-98.3, -62.0, 118.3, 241.1, base = 180);   // tall panels beside the hatch
    skin_panel(62.0, 98.3, 118.3, 241.1, base = 180);
    skin_panel(-171.1, -119.0, 17.2, 243.3, base = 180);  // tall doors
    skin_panel(119.0, 171.1, 17.2, 243.3, base = 180);
    skin_recess(-(bu_acc_s + 8), bu_acc_s + 8, bu_acc_y0 - 8, bu_acc_y1 + 8, 2.0, 180);  // cover rebate
    // m5: the club rear centre tall panel (s +/-62, y 118.3..241.1) cannot be a recess - the
    // access opening occupies it. Its outline is scribed on the rebate floor instead, where the
    // 10 mm lip backs the skin, so the cover can be trimmed to the club line. See DEVIATIONS 7.
    skin_groove(-62, 62, bu_acc_y0 - 7.5, bu_acc_y1 + 7.5, w = 2, d = 2.6, base = 180);
    bu_acc_cut(10);                                                                      // opening
    // --- sides: the combined front/rear side vent, both flanks ---
    bd_side_louvres(75.9, 104.1, 153.1, 242.1, 10);
}
module bu_proud() {                                        // utility-arm reliefs in the bays
    for (yc = [38.0, 80.35]) intersection() {
        bd_band(bd_a(-82.5), bd_a(82.5), bd_z(yc + 19), bd_z(yc - 19), 8.6);
        cylinder(r = 157.9, h = bd_top, $fn = 240);
    }
}

module body_upper() { translate([0, 0, -body_lower_h]) bd_upper_bf(); }
module bd_upper_bf() {
    union() {
        difference() {
            union() {
                difference() { bu_outer(); bu_cavity(); }
                difference() {
                    union() {
                        bu_flange();
                        bu_deck();
                        bu_ribs2();
                    }
                    bu_vent_keepout();
                }
                bu_topplate();
                for (sd = [1, -1]) { bu_shoulder_solid(sd); bu_shoulder_gussets(sd); }
                bu_acc_lip();
                bu_pads();
                bu_grommets();
                bu_deck_furniture();
                for (sd = [1, -1]) st_lock_block(sd);     // revision D sensed shoulder lock
                st_act_mount();                            // revision D actuator fixed eye
            }
            for (sd = [1, -1]) st_lock_cuts(sd);
            st_act_mount_cuts();
            bu_flange_cuts();
            // B1: the four M8 rods must actually pass through the ring. bu_ribs() builds the rod
            // columns solid and the top plate only carried an 18 x 4 nut counterbore, so there
            // was no bore at all below it.
            for (i = [0 : rod_n - 1]) bd_at_rod(i) translate([0, 0, bd_seam - 1])
                cylinder(d = rod_d + 0.6, h = bd_top - bd_seam + 2, $fn = 48);
            bu_topplate_cuts();
            for (sd = [1, -1]) bu_shoulder_cuts(sd);
            bu_deck_cuts();
            bu_acc_lip_cuts();
            bu_grommet_cuts();
            bu_skin_cuts();
        }
        bu_proud();
    }
}
module bu_ribs2() { difference() { bu_ribs(); bu_keepout(); } }
