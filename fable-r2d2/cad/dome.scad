// fable-r2d2 — dome.scad: the one-piece detailed dome (module dome()).
//
// FRAME (r2d2.scad "Dome frame"): Z up the dome axis, z = 0 at the band bottom edge (on the
// print bed), crown up, +Y = droid front, +X = droid right. Print frame = dome frame
// (scripts/parts.json: "Lip down on the plate; crown up", print_rotation_z = 0).
//
// ANGLE CONVENTION. research/proportions.md and the CuriousMarc dome sheets measure dome
// azimuth from the front centreline with POSITIVE toward the viewer's right when facing the
// droid. The viewer's right is the droid's LEFT, i.e. the -X side of this frame. The helper
// dome_az(a) = rotate([0, 0, a]) maps a sheet angle to the model: rotate([0,0,a]) carries the
// +Y (front) direction to (-sin a, cos a), so +25.5 deg (HP1) lands at -X and -24.7 deg (front
// logic displays, P12) lands at +X. Verified against research/drawings/photos/body-front.jpg and
// research/images/dome-01.jpg: facing the droid, the two blue logic windows are on the viewer's
// LEFT of the radar eye and the front holoprojector barrel is on the viewer's RIGHT; the rear
// view dome-03.jpg shows the rear logic display on the viewer's right (= droid's right, -angles)
// and the two dome bumps left of the rear PSI (+angles). All 2D wedges use pt(r, a) =
// [-r sin a, r cos a], the same convention. Surface-local frames (at_surface, at_eye_face):
// local Z = outward normal, local X = horizontal tangent, local +Y = DOWN the meridian / face.
//
// GEOMETRY. Outer surface: cylinder r = dome_r for z 0..dome_band_h, then the ellipsoid with
// semi-axes dome_b (horizontal) and dome_a (vertical) centred at z = dome_band_h, cut flat at
// the top-disc opening (z_flat ~193.4) so the crown region is a flat disc. Shell wall dome_wall +
// 0.2 = 3.2 mm so the 0.8 mm panel recesses leave the 2.4 mm minimum; the band inner face, rebate
// ring and ribs still reference dome_r - dome_wall.
// Outer band: mounting ring 0..16.9 (full-size 24.77 x 0.68386), a 2.2 mm x 0.8 mm decorative
// groove 16.9..19.1, the ring to dome_band_h, then a 0.4 mm deep 6 mm tall blue-band paint
// line 25.9..31.9 (both with a 45 deg sloped top edge so the rim needs no support). Fourteen side panels P1-P14 and six pie panels PP1-PP6 are 0.8 mm recesses
// (dome_panel_recess) bounded by the sheet callouts (the un-recessed dome between panels is the
// silver frame; dome_panel_frame_w sets the surrounds of the inner features). Panel spans are
// the CuriousMarc dome page 2 callouts (research/proportions.md 1.3), heights scaled from 81 /
// 53.5 / 77 / 70.5 / 88 mm (P7 = 88, dome-p5.png). The magic panel P5 carries an extra 1.5 mm
// rounded inset and the small upper panel P6 (dome-p4.png detail B: 70.5 + 6 gap + 18 tall)
// above it; P8 carries the rounded rear-PSI inset; P9 has the 12 mm bottom sub-panel strip and
// the two vertical sub-panel cuts of detail D (dome-p6.png). Both deep insets have a 3.5 mm
// conformal backing pad behind them (the inset stays 2.3 deep with a uniform wall). Radar eye per radar-eye.pdf pages 1-4: profile swept -15.57..+15.57 deg about the
// dome axis, inner surface = the dome, outer face a cone 24.09 deg from vertical, top face ~2
// deg, left side leaned 8.5 deg, bottom-left 14 deg wedge removed from -7.89 to -15.57 deg,
// lower slot -5..+10 deg, right-side shelf +15.57..+20.22 deg set back 3.0 mm (sheet 6.9: the
// envelope-limited housing is only 5.5-7 mm proud there, so the sheet value would bury the
// shelf) with the two channels (0.8 / 1.5 deep) and the 0.8 step; lens bezel 4.3 mm proud with
// a 45 deg chin fillet; lens seat (dome_eye_lens_d + 0.5) x 2 deep, 2 mm inner lip; TFT pocket
// dome_eye_lcd_pcb + 0.6 open to the INTERIOR (the 55.7 mm PCB diagonal cannot pass the 52 mm
// lens seat, so the board loads from inside against the lip) with a 45 deg gable roof (its top a
// 50 deg roof descending inward under the housing top wall) and two
// M2.5 insert bosses on the housing inner face beside the pocket for a retaining strap.
// Holoprojectors HP1/HP2/HP3: 44.1 bore in an 8 mm proud barrel with a 4 mm wall, closed back,
// 8.4 x 6 LED pocket for an 8 mm NeoPixel and an 8 x 3.5 lead slot; HP1 and HP2 carry a gusset
// under the barrel (the lower 45 deg arc hulled to a 20 mm foot 10 mm down the skin, faces >= 45
// deg true) and a teardrop cup inside; HP2 is truncated flat by the
// envelope plane y = -158.4; HP3 sits at r 69.1 inside pie panel PP3. Front/rear PSI: flat lens
// seat (d + 2.5) cut relative to the LOCAL recess floor, 27 / 34 aperture, NeoPixel Jewel pocket
// 24 x 4.5 in a teardrop boss (3.3 mm floor), 3.2 mm wire hole. Front logic displays: two
// dome_fld_window windows at dome_fld_z; behind each a 20.6 x 28.6 pocket for one dome_matrix_pcb
// backpack, CLOSED at the skin (the window is the only through-cut and the front stop), open to
// the interior, shifted 4 mm down (lower) / up (upper) so the 20 x 20 matrix is centred in its
// window and the header tail points away from the other window (no pocket overlap); two M2 insert
// bosses on the block inner face for a strap. Rear logic display: dome_rld_window at the top of
// P9 (dome-p6.png detail D) with a 40.6 x 28.6 pocket for two backpacks side by side. Every
// pocket has a 45 deg gable top and every block a 45 deg (true) roof under it. Dome buttons
// DB1/DB2: 14.4 mm discs 1.5 mm proud. Interior: bottom plate annulus dome_plate_r_in..
// dome_plate_r_out x dome_plate_t on the bed, 4 x M5 heat-set pockets from BELOW at susan_hole_r
// on susan_hole_angles (bosses 12 mm tall above the plate), a smooth flat underside ring for the
// friction wheel around head_wheel_r, a wire-anchor lug at dome_wire_anchor_r (45 deg) with two
// horizontal 4 mm zip-tie holes above the plate, four 18 mm cable notches in the plate inner edge
// (0/90/180/270), a 4 mm rebate ring inside the band above the plate and six radial ribs 6 mm
// tall. Recessed label "dome" on the plate top.
//
// LOCAL OVERRIDES OF params.scad (this file may not edit params.scad; flagged for its owner):
//   hp3_r = 69.1 (dome_hp3_r = 101 is the FULL-SIZE radius: 84.60 x 0.68386 / cos 33.15).
//   rld_z = 73.5 (dome_rld_z = 52 puts the window at the panel bottom; the sheet dimensions it
//     5.5 mm full size below the P9 top).
//   eye_lens_z = 118 (dome_eye_z = 108 mis-transcribes "0.34 D above the ring TOP"; the front
//     sheet vector gives 118.0). The housing top is eye_zt = 148 (housing 74.6 tall).
//
// ENVELOPE (env_x x env_y = 322 x 317, dome_od = env_y): raised features are clipped by the
// envelope BOX, so only features near the +/-Y axis are limited (the rear HP2 barrel front is
// sliced flat by y = -158.4; the eye bezel bottom reaches r 156.8; HP1 at 25.5 deg is untouched).
//
// FASTENERS EXPECTED: 4 x M5 heat-set inserts (lazy-susan top race, screws from below through
// the Triangle 9C race); 2 x M2.5 inserts + M2.5 x 8 screws (round TFT retaining strap, bosses
// 54.4 mm apart on the housing inner face); 6 x M2 inserts + M2 x 6 screws (three backpack
// retaining straps, printed or 2 mm acrylic); acrylic lens discs: eye 52.1 x 2, front PSI 29 x
// 1.5, rear PSI 36 x 1.5 (seats have 0.5 mm clearance, glued); zip tie through the lug.
//
// PRINT / SUPPORT: PETG, band down. The shell overhang passes 45 deg above z ~151 and reaches
// ~75 deg at the flat crown: support INSIDE under the last 25 mm of the crown (z > ~168, under the
// pie-panel ring, the 66 mm flat top and the HP3 cup). Everything else is designed to print
// support-free: eye housing underside 48 deg from horizontal, bezel chin, HP1/HP2 barrel gussets
// and cup teardrops, PSI boss teardrops, 45 deg roofs under the logic-display blocks and the inset
// pads, 45 deg gables over every pocket, the eye pocket gable with a 50 deg descending roof, and
// sloped ceilings on the rim groove and blue-band line (a flat ceiling at r 158.4 makes the slicer
// put support outside the 320 mm bed). Remaining bridges: the tops of the 44.1 mm HP bores and the
// 52.6 mm bezel bore, the 27 / 34 mm PSI apertures and seats, the 30 / 44 mm logic windows (3.2 mm
// deep) and the two deep-inset ledges (2.3 mm deep). The 14 deg wedge face at the eye's bottom-left
// corner (about 20 x 6 mm, 76 deg) is a downward face: paint a support blocker there or accept
// minor roughness. Verified with Bambu Studio 0.20 mm H2D profile, STL translated to the bed
// centre, --arrange 0: tree(auto) supports slice clean (1244 g, 35.4 h at the default threshold;
// 1465 g, 45.1 h at 46 deg with bridge_no_support); supports off slices at 1044 g / 25.4 h
// (measured before the rim-groove slope, otherwise identical geometry) with only the expected
// crown "floating regions" warning. No brim needed: the first layer is a
// 57..158.5 mm annulus.

// ---------- local parameters (not in params.scad) ----------
dome_fn = $fn;                                  // 96 from params for the big revolved surfaces
sf = scale_factor;
ring_h = 24.77 * sf;                            // 16.9 bottom mounting ring
ring_groove = [16.9, 3.18 * sf, 0.8];           // z0, height 2.2, depth
blue_band = [dome_band_h + 0.5, 6, 0.4];        // z0 (0.5 above the band edge to avoid a coincident ring), height, depth
panel_top_81 = dome_panel_bottom_z + dome_side_panel_h;      // 90.5
h_53 = 53.5 * sf;                               // 36.6  P13, P14
h_77 = 77 * sf;                                 // 52.7  P9
h_70 = 70.5 * sf;                               // 48.2  P5 main
h_88 = 88 * sf;                                 // 60.2  P7 (dome-p5.png)
z_p6 = [76.5 * sf, 94.5 * sf];                  // P6 small upper panel, above the panel line (detail B: 70.5 + 6 + 18)
p9_strip = 12 * sf;                             // 8.2 bottom sub-panel strip of P9 (detail D)
subline = 1.1;                                  // un-recessed sub-panel cut line width
inset_depth = 1.5;                              // magic panel / rear PSI inset (below the recess)
shell_wall = dome_wall + 0.2;                   // 3.2: the 0.8 recesses then leave 2.4 mm (minimum wall)
backing_t = 3.5;                                // conformal pad wall behind the two deep insets
pie_clr = 2.5 * sf;                             // 1.7 pie panel cut clearance
z_flat = dome_band_h + dome_a * sqrt(1 - pow(dome_top_disc_opening_d / 2 / dome_b, 2));   // 193.4
top_button_d = 27.4 * sf;                       // 18.7 centre button
hp_barrel_proud = 8; hp_barrel_wall = 4; hp_bore_depth = 11; hp_back_t = 2.5;
hp_led_d = 8.4; hp_led_depth = 6; hp_lead_slot = [8, 3.5];
hp_gusset_run = 10;                             // gusset foot this far below the barrel edge on the skin
hp3_r = 84.6 * sf / cos(180 - dome_hp3_angle);  // 69.1  LOCAL OVERRIDE of dome_hp3_r (101 is full size)
psi_seat_extra = 2; psi_seat_clr = 0.5; psi_seat_depth = 1.5; psi_aperture_t = 2.4;
jewel_d = 24; jewel_depth = 4.5; psi_floor_t = 3.3; psi_wire_d = 3.2; psi_boss_wall = 3;
db_d = 21 * sf; db_proud = 1.5;                 // dome buttons 14.4
db_z = panel_top_81 + 2 * sf + db_d / 2;        // 99.1: 2 mm above the P8 top per detail C
rld_z = dome_panel_bottom_z + h_77 - 5.5 * sf - dome_rld_window[1] / 2;   // 73.5  LOCAL OVERRIDE of dome_rld_z
fld_dy = [4, -4];                               // pocket shift down the meridian: lower tail down, upper tail up
matrix_block_t = 14;                            // 3.2 skin + 6 matrix + 4 backpack + 0.8
matrix_wall = 3.5; matrix_side = 10;            // pocket walls (up/down) and block side width
matrix_strap_m = 2; matrix_clear = 0.6;
eye_lens_z = 118;                               // LOCAL OVERRIDE of dome_eye_z (108): sheet vector, dome-p3.png
eye_tilt = 24.09;                               // outer face generator angle from vertical
eye_half = 15.57; eye_shelf = 4.65;             // main sweep +/-15.57, shelf 15.57..20.22
eye_zbi = dome_panel_bottom_z + h_53 + 2.5 * sf;      // 73.4 housing bottom, 1.7 above P14
eye_rb = dome_r - 0.2;                          // 158.3 bottom outer corner (envelope limit)
eye_under_deg = 48;                             // underside chamfer from horizontal (48: clears a 45 deg slicer threshold)
eye_zt = 148;                                   // top of the housing (bezel top 144.5)
eye_shelf_set = 3.0;                            // shelf face set back from the main face (sheet 6.9, see header)
eye_channels = [[5.0 + 1.5, 1.5, 0.8], [5.0 + 1.5 + 13.4 + 3.8, 3.8, 1.5]];   // [from top, width, depth]
eye_step_from_top = 5.0 + 1.5 + 13.4 + 3.8 + 15.6; eye_step_depth = 0.8;
eye_bezel_od = dome_eye_lens_d + 6; eye_bezel_h = 4.3; eye_bezel_root = 4;   // ring rooted 4 mm into the face (cone sag 3 mm at the sides)
eye_seat_clr = 0.5; eye_lip = 2; eye_seat_depth = 2; eye_gable_from = 4;
eye_boss_d = 7.5; eye_boss_x = dome_eye_lcd_pcb[0] / 2 + 6; eye_boss_depth = 15; eye_boss_fin = 24;   // strap bosses beside the pocket
eye_roof_z = eye_zt - 3;                        // pocket gable roof starts here (keeps the top wall)
eye_slot = [-5, 10, 2.6 * sf * 1.4, 1.7];       // sweep a1, a2, height 2.5, depth
plate_boss_d = 14; plate_boss_h = 12;
rebate_h = 4; rebate_t = 4;
rib_n = 6; rib_h = 6; rib_t = 3;
notch_d = 18;
lug_angle = 45; lug = [14, 20, 14]; lug_hole_d = 4; lug_hole_z = dome_plate_t + 5;

// ---------- helpers ----------
function pt(r, a) = [-r * sin(a), r * cos(a)];                     // sheet angle -> XY
function r_surf(z) = z <= dome_band_h ? dome_b : dome_b * sqrt(max(0, 1 - pow((z - dome_band_h) / dome_a, 2)));
function z_at_r(r) = dome_band_h + dome_a * sqrt(max(0, 1 - pow(r / dome_b, 2)));
function surf_tilt(z) = z <= dome_band_h ? 90 : atan2(r_surf(z) / (dome_b * dome_b), (z - dome_band_h) / (dome_a * dome_a));
function ell_pt(off, t) = [(dome_b - off) * cos(t), dome_band_h + (dome_a - off) * sin(t)];
function t_top(off) = asin((z_flat - off - dome_band_h) / (dome_a - off));
// Meridian run per unit depth for a face that rises inward at a TRUE 45 deg on a surface whose
// normal is tilted (90 - surf_tilt) above horizontal (local 45 deg would be too shallow).
function roof_k(z) = let(t = surf_tilt(z)) (sin(t) + cos(t)) / (sin(t) - cos(t));
roof_margin = 1.15;                             // roofs 15 % steeper than 45 deg (about 41 deg overhang)
// Horizontal sag of the surface x mm off the meridian (flat seats on the curved skin).
function sag_h(z, x) = r_surf(z) - sqrt(r_surf(z) * r_surf(z) - x * x);

module dome_az(a) { rotate([0, 0, a]) children(); }
// Local frame on the outer surface: origin at (angle a, height z), local Z = outward normal,
// local X = horizontal tangent (toward -angle), local Y = down the meridian.
module at_surface(a, z) { dome_az(a) translate([0, r_surf(z), z]) rotate([-surf_tilt(z), 0, 0]) children(); }

// Revolved half a facet out of phase so no panel or pie edge coincides with a meridian facet line.
module dome_solid(off = 0, z0 = 0, n = 60) {
    rotate([0, 0, 180 / dome_fn]) rotate_extrude($fn = dome_fn)
        polygon(concat([[0, z0], [dome_b - off, z0]], [for (i = [0 : n]) ell_pt(off, i * t_top(off) / n)], [[0, z_flat - off]]));
}
module outside_of(off) { difference() { translate([-400, -400, -20]) cube([800, 800, 400]); dome_solid(off, -5); } }
module under_skin() { intersection() { children(); dome_solid(1.0, -5); } }   // keep inner features 1 mm under the outer surface
module wedge2d(a1, a2, r = 400) {
    n = max(2, ceil((a2 - a1) / 5));
    polygon(concat([[0, 0]], [for (i = [0 : n]) pt(r, a1 + (a2 - a1) * i / n)]));
}
module wedge_prism(a1, a2, z0, z1) { translate([0, 0, z0]) linear_extrude(height = z1 - z0) wedge2d(a1, a2); }
module sweep(a1, a2) { rotate([0, 0, 90 + a1]) rotate_extrude(angle = a2 - a1, $fn = dome_fn) children(); }
module half_plane(a, w) { rotate(90 + a) translate([0, w]) square([500, 500]); }                // CCW of the ray a, inset w
module half_plane_cw(a, w) { rotate(90 + a) translate([0, -w]) mirror([0, 1]) square([500, 500]); }
module rrect_prism(x, y, r, z0, z1) { translate([0, 0, z0]) linear_extrude(height = z1 - z0) rrect(x, y, r); }
// Band between z0 and z1 whose top face rises outward at 45 deg through (dome_r, z1): a shallow
// groove cut with it has a sloped ceiling instead of a flat one (no support at the r = 158.4 rim).
module band_prism(z0, z1) { rotate([0, 0, 180 / dome_fn]) rotate_extrude($fn = dome_fn) polygon([[0, z0], [600, z0], [600, z1 + 600 - dome_r], [0, z1 - dome_r]]); }
// Print envelope: the 322 x 317 box (not a cylinder), 0.1 mm inside on Y and 1 mm on X.
module clip_env() { intersection() { children(); translate([-(env_x / 2 - 1), -(dome_r - 0.1), -10]) cube([env_x - 2, 2 * (dome_r - 0.1), 400]); } }
// 2D teardrop: circle d with a 45 deg point toward +Y (local "down") so horizontal bores print.
module teardrop2d(d, fn = 48) { hull() { circle(d = d, $fn = fn); polygon([[-d / 2 * 0.7071, d / 2 * 0.7071], [0, d / 2 * 1.4142], [d / 2 * 0.7071, d / 2 * 0.7071]]); } }
// 2D pocket outline w x h with a 45 deg gable toward -Y (local "up") so the pocket ceiling prints.
module gable2d(w, h) { polygon([[-w / 2, h / 2], [w / 2, h / 2], [w / 2, -h / 2], [0, -h / 2 - w / 2], [-w / 2, -h / 2]]); }
// Prism along local X from a (y, z) polygon.
module yz_prism(pts, w = 400) { rotate([90, 0, 90]) linear_extrude(height = w, center = true) polygon(pts); }
// Rectangular through-window: straight cut through the skin only (the 3.2 mm ceiling is a
// bridge; a sloped ceiling would thin the 5 mm frame between the two front windows to a knife edge).
module window_cut(w, h) { translate([-w / 2, -h / 2, -(shell_wall + 0.6)]) cube([w, h, shell_wall + 0.6 + 12]); }

// ---------- panel tables (sheet angles; positive = droid's left) ----------
// [a1, a2, z_bottom, z_top]
p9_z1 = dome_panel_bottom_z + p9_strip + subline / 2;
side_panels = [
    [35.75, 47.25, dome_panel_bottom_z, panel_top_81],                 // P1
    [48.75, 60.25, dome_panel_bottom_z, panel_top_81],                 // P2
    [61.75, 73.25, dome_panel_bottom_z, panel_top_81],                 // P3
    [74.75, 99.40, dome_panel_bottom_z, panel_top_81],                 // P4
    [101.10, 113.50, dome_panel_bottom_z, dome_panel_bottom_z + h_70], // P5 magic panel (main)
    [101.10, 113.50, dome_panel_bottom_z + z_p6[0], dome_panel_bottom_z + z_p6[1]],   // P6 small upper panel
    [118.0, 145.0, dome_panel_bottom_z, dome_panel_bottom_z + h_88],   // P7 metal panel (88 mm sheet)
    [146.5, 173.8, dome_panel_bottom_z, panel_top_81],                 // P8 rear PSI panel
    [-153.25, -100.0, dome_panel_bottom_z, dome_panel_bottom_z + p9_strip - subline / 2],   // P9 bottom sub-panel strip
    [-153.25, -150.7, p9_z1, dome_panel_bottom_z + h_77],              // P9 rear sub-panel
    [-149.9, -120.5, p9_z1, dome_panel_bottom_z + h_77],               // P9 rear logic display sub-panel
    [-119.7, -100.0, p9_z1, dome_panel_bottom_z + h_77],               // P9 front sub-panel
    [-91.70, -42.26, dome_panel_bottom_z, panel_top_81],               // P10
    [-39.04, -33.11, dome_panel_bottom_z, panel_top_81],               // P11
    [-31.38, -18.03, dome_panel_bottom_z, panel_top_81],               // P12 front logic displays
    [-16.55, -10.61, dome_panel_bottom_z, dome_panel_bottom_z + h_53], // P13
    [-9.38, 13.86, dome_panel_bottom_z, dome_panel_bottom_z + h_53],   // P14 front PSI panel
];
p5_centre = (101.10 + 113.50) / 2;
p5_w = (113.50 - 101.10) * PI / 180 * r_surf(dome_panel_bottom_z + h_70 / 2);   // ~32.9 mm
p5_inset = [p5_w - 2 * 5.5 * sf, 54 * sf, 5 * sf, dome_panel_bottom_z + h_70 / 2];  // w, h, R, z
p8_inset = [97.4 * sf, dome_side_panel_h - 2 * 9.5 * sf, 5 * sf, dome_rear_psi[1]];  // 66.6 x 42.4 R3.4

// ---------- eye housing profile (r, z) ----------
eye_rbi = r_surf(eye_zbi);                                  // 152.3
eye_zb = eye_zbi + (eye_rb - eye_rbi) * tan(eye_under_deg); // 79.4 bottom of the outer face
eye_L = (eye_zt - eye_zb) / cos(eye_tilt);                  // face length along the slant
eye_d = [-sin(eye_tilt), cos(eye_tilt)];                    // along the face, upward
eye_n = [cos(eye_tilt), sin(eye_tilt)];                     // outward face normal
eye_B = [eye_rb, eye_zb];
eye_T = eye_B + eye_L * eye_d;                              // top outer corner
eye_top_dir = [-cos(2.1), -sin(2.1)];                       // top face, 112 deg corner (2.1 deg down)
eye_Ti = eye_T + 60 * eye_top_dir;                          // well inside the wall
eye_Bi = [eye_rbi, eye_zbi];
function eye_face(s, t) = eye_B + s * eye_d + t * eye_n;    // point s along the face, t outward
eye_s_lens = (eye_lens_z - eye_zb) / cos(eye_tilt);         // lens centre along the face
eye_lens_r = eye_face(eye_s_lens, 0)[0];
eye_roof_pt = eye_face((eye_roof_z - eye_zb) / cos(eye_tilt), -eye_gable_from);   // (r, z) where the pocket gable roof starts

module eye_profile(setback = 0) {
    polygon([eye_B - setback * eye_n, eye_T - setback * eye_n, eye_Ti, [eye_rbi - 60, eye_zbi], eye_Bi]);
}
// Local frame on the eye face: origin at the lens centre, Z = face normal (outward),
// X horizontal, +Y = DOWN the face (rotate by -(90 - tilt) about X maps +Y to (0, 0.41, -0.91)).
module at_eye_face() { translate([0, eye_lens_r, eye_lens_z]) rotate([-(90 - eye_tilt), 0, 0]) children(); }

module eye_housing() {
    difference() {
        union() {
            sweep(-eye_half, eye_half) eye_profile(0);
            sweep(eye_half - 0.05, eye_half + eye_shelf) eye_profile(eye_shelf_set);      // side shelf
        }
        dome_solid(shell_wall, -5);                                                         // keep the cavity
        // left side leaned 8.5 deg from vertical (narrower at the bottom)
        dome_az(-eye_half) translate([0, 0, eye_zt]) rotate([0, 8.5, 0]) translate([0, -200, -200]) cube([100, 400, 400]);
        // bottom-left 14 deg wedge from -7.89 deg to the left edge
        dome_az(-7.89) translate([0, 0, eye_zbi - 0.4]) rotate([0, -14, 0]) translate([0, -200, -200]) cube([200, 400, 200]);
        // lower slot, -5..+10 deg, cut parallel to the base
        sweep(eye_slot[0], eye_slot[1]) polygon([eye_face(1.0, -eye_slot[3]), eye_face(1.0, 3), eye_face(1.0 + eye_slot[2], 3), eye_face(1.0 + eye_slot[2], -eye_slot[3])]);
        // shelf channels (from the top down): 5.0 block, 1.5 narrow 0.8 deep, 13.4 block, 3.8 wide 1.5 deep, 15.6 block, then the step
        for (c = concat([for (ch = eye_channels) [eye_L - ch[0] - ch[1], ch[1], ch[2]]], [[0, eye_L - eye_step_from_top, eye_step_depth]]))
            sweep(eye_half + 0.5, eye_half + eye_shelf + 0.5) {
                s0 = c[0]; s1 = c[0] + c[1]; dp = c[2] + eye_shelf_set;
                polygon([eye_face(s0, -dp), eye_face(s1, -dp), eye_face(s1, 4 - eye_shelf_set), eye_face(s0, 4 - eye_shelf_set)]);
            }
        // clearance for the HP1 barrel that nestles under the shelf corner
        at_surface(dome_hp1[0], dome_hp1[1]) translate([0, 0, -30]) cyl(dome_hp_d + 2 * hp_barrel_wall + 1.5, 60);
    }
    // lens bezel: a boss rooted eye_bezel_root into the cone face (the seat and pocket cuts hollow
    // it) with a 45 deg chin under its lower edge so the 4.3 mm proud ring prints support-free
    clip_env() at_eye_face() {
        translate([0, 0, -eye_bezel_root]) cyl(eye_bezel_od, eye_bezel_h + eye_bezel_root, fn = 96);
        hull() {                                   // chin: the ring's lower 45 deg arc hulled to a foot 3.5 mm below it
            intersection() {
                translate([0, 0, -eye_bezel_root]) cyl(eye_bezel_od, eye_bezel_h + eye_bezel_root, fn = 96);
                translate([-eye_bezel_od / 2, eye_bezel_od / 2 * 0.7071, -eye_bezel_root]) cube([eye_bezel_od, eye_bezel_od, eye_bezel_h + eye_bezel_root]);
            }
            translate([-eye_bezel_od * 0.3, eye_bezel_od / 2 + 3, -eye_bezel_root]) cube([eye_bezel_od * 0.6, 0.5, 1]);
        }
    }
    // TFT retaining-strap bosses on the housing inner face beside the pocket: axis along the face
    // normal; hulled with a stub 24 mm down the face so the underside is a 45 deg (true) fin
    at_eye_face() for (x = [-1, 1]) hull() {
        translate([x * eye_boss_x, 0, -eye_boss_depth]) cyl(eye_boss_d, eye_boss_depth - eye_seat_depth, fn = 32);
        translate([x * eye_boss_x, eye_boss_fin, -6]) cyl(eye_boss_d, 6 - eye_seat_depth, fn = 32);
    }
}
module eye_cuts() {
    pw = dome_eye_lcd_pcb[0] + matrix_clear; ph = dome_eye_lcd_pcb[1] + matrix_clear;
    at_eye_face() {
        translate([0, 0, -eye_seat_depth]) cyl(dome_eye_lens_d + eye_seat_clr, 30, fn = 96);          // lens seat through the bezel
        translate([0, 0, -40]) linear_extrude(height = 40 - eye_seat_depth) rrect(pw, ph, 2);          // PCB pocket, open to the interior
        for (x = [-1, 1]) translate([x * eye_boss_x, 0, -eye_boss_depth]) insert_hole(2.5);            // strap inserts (from the inside)
    }
    // 45 deg gable over the pocket from 4 mm behind the face inward; its top is a roof that starts
    // 3 mm under the housing top and descends inward at 50 deg (stays inside the housing, prints as a buttress)
    intersection() {
        at_eye_face() translate([0, 0, -40]) linear_extrude(height = 40 - eye_gable_from) gable2d(pw, ph);
        translate([0, eye_roof_pt[0], eye_roof_pt[1]]) rotate([atan(1.2), 0, 0]) translate([-200, -200, -400]) cube([400, 400, 400]);
    }
}

// ---------- holoprojectors ----------
module hp_barrel(a, z, proud, gusset = false) {
    od = dome_hp_d + 2 * hp_barrel_wall;
    back = proud - hp_bore_depth - hp_led_depth - hp_back_t;      // cup floor + LED pocket + back plate
    clip_env() {
        at_surface(a, z) {
            translate([0, 0, back]) cyl(od, proud - back, fn = 72);
            if (gusset) hull() {                                   // gusset: the barrel's lower 45 deg arc hulled to a foot on the skin
                intersection() { cyl(od, proud, fn = 72); translate([-od / 2, od / 2 * 0.7071, 0]) cube([od, od, proud]); }
                translate([-10, od / 2 + hp_gusset_run - 1, -6]) cube([20, 2, 1]);
            }
        }
        if (gusset) under_skin() at_surface(a, z) translate([0, 0, back]) linear_extrude(height = -back - 2) teardrop2d(od, 48);   // cup inside
    }
}
module hp_cuts(a, z, proud) {
    at_surface(a, z) {
        translate([0, 0, proud - hp_bore_depth]) cyl(dome_hp_d, hp_bore_depth + 10, fn = 72);                     // bore, closed back
        translate([0, 0, proud - hp_bore_depth - hp_led_depth]) cyl(hp_led_d, hp_led_depth + eps, fn = 24);     // LED pocket
        translate([-hp_lead_slot[0] / 2, -hp_lead_slot[1] / 2, -25]) cube([hp_lead_slot[0], hp_lead_slot[1], 25 - hp_bore_depth - hp_led_depth + proud + eps]);   // lead slot
    }
}

// ---------- PSIs (floor = local recess depth under the nominal surface: 0.8 in P14, 2.3 in the P8 inset) ----------
function psi_seat(z, d, floor) = floor + psi_seat_depth + sag_h(z, (d + psi_seat_extra + psi_seat_clr) / 2);   // flat seat plane depth: 1.5 step at the ring edge
module psi_boss(a, z, d, floor) {
    h = psi_seat(z, d, floor) + psi_aperture_t + jewel_depth + psi_floor_t;
    intersection() {
        at_surface(a, z) translate([0, 0, -h]) linear_extrude(height = h) teardrop2d(d + 2 * psi_boss_wall, 48);
        dome_solid(floor + 0.1, -5);
    }
}
module psi_cuts(a, z, d, floor) {
    s = psi_seat(z, d, floor);
    at_surface(a, z) {
        translate([0, 0, -s]) cyl(d + psi_seat_extra + psi_seat_clr, 20, fn = 64);                    // lens seat
        translate([0, 0, -s - psi_aperture_t]) cyl(d, psi_aperture_t + 1, fn = 64);                   // aperture
        translate([0, 0, -s - psi_aperture_t - jewel_depth]) cyl(jewel_d, jewel_depth + eps, fn = 48);   // Jewel pocket
        translate([0, 0, -30]) cyl(psi_wire_d, 30 - s - psi_aperture_t - jewel_depth + eps, fn = 16);   // wire hole
    }
}

// ---------- logic display pockets ----------
module matrix_block(a, z, w_pcb, dy = 0) {
    ph = dome_matrix_pcb[1] + matrix_clear;
    bw = w_pcb + 2 * matrix_side; k = roof_k(z) * roof_margin;
    top = ph / 2 + matrix_wall; bot = ph / 2 + matrix_wall + k * matrix_block_t;   // roof run added below
    under_skin() at_surface(a, z) translate([0, dy, 0]) difference() {
        translate([-bw / 2, -top, -matrix_block_t]) cube([bw, top + bot, matrix_block_t + 1]);
        yz_prism([[bot + 3 * k, 3], [bot - k * (matrix_block_t + 2), -(matrix_block_t + 2)], [bot + 200, -(matrix_block_t + 2)], [bot + 200, 3]], bw + 2);   // 45 deg roof
    }
}
module inset_backing(a, z, w, h, r) {           // conformal pad: inset floor .. floor + backing_t, 45 deg (true) roof under it
    k = roof_k(z) * roof_margin; bot = h / 2 + 12;
    intersection() {
        at_surface(a, z) difference() {
            translate([0, 4, 0]) rrect_prism(w + 8, h + 16, r, -14, 30);
            yz_prism([[bot + 3 * k, 3], [bot - 13 * k, -13], [bot + 200, -13], [bot + 200, 3]], w + 10);
        }
        difference() { dome_solid(dome_panel_recess + inset_depth + 0.1, -5); dome_solid(dome_panel_recess + inset_depth + backing_t, -5); }
    }
}
module matrix_cuts(a, z, window, w_pcb, dy = 0) {
    pw = w_pcb + matrix_clear; ph = dome_matrix_pcb[1] + matrix_clear;
    bw = w_pcb + 2 * matrix_side;
    at_surface(a, z) {
        window_cut(window[0], window[1]);                                                              // window through the skin (only skin cut)
        translate([0, dy, 0]) {
            translate([0, 0, -(matrix_block_t + 1)]) linear_extrude(height = matrix_block_t + 1 - shell_wall) gable2d(pw, ph);   // pocket, closed at the skin
            for (x = [-1, 1]) translate([x * (bw / 2 - 4.5), 0, -matrix_block_t]) insert_hole(matrix_strap_m);   // strap inserts on the inner face
        }
    }
}

// ---------- surface recesses (cut from the shell before the raised features are added) ----------
module surface_recesses() {
    // decorative ring groove and blue band paint line
    intersection() { band_prism(ring_groove[0], ring_groove[0] + ring_groove[1]); outside_of(ring_groove[2]); }
    intersection() { band_prism(blue_band[0], blue_band[0] + blue_band[1]); outside_of(blue_band[2]); }
    // side panels
    intersection() {
        union() for (p = side_panels) wedge_prism(p[0], p[1], p[2], p[3]);
        outside_of(dome_panel_recess);
    }
    // pie panels PP1..PP6 with the divider strips
    intersection() {
        linear_extrude(height = 300) for (i = [0 : 5]) intersection() {
            difference() { rotate(180 / 173) circle(r = dome_pie_r_out - pie_clr, $fn = 173); rotate(180 / 113) circle(r = dome_pie_r_in + pie_clr, $fn = 113); }
            half_plane(60 * i, dome_pie_divider_w / 2);
            half_plane_cw(60 * (i + 1), dome_pie_divider_w / 2);
        }
        outside_of(dome_panel_recess);
    }
    // magic panel P5 inset and rear PSI panel P8 inset (deeper rounded recesses)
    intersection() {
        union() {
            at_surface(p5_centre, p5_inset[3]) rrect_prism(p5_inset[0], p5_inset[1], p5_inset[2], -6, 30);
            at_surface(dome_rear_psi[0], p8_inset[3]) rrect_prism(p8_inset[0], p8_inset[1], p8_inset[2], -6, 30);
        }
        outside_of(dome_panel_recess + inset_depth);
    }
}

// ---------- interior ----------
module interior() {
    ring(2 * dome_plate_r_out, 2 * dome_plate_r_in, dome_plate_t, fn = dome_fn);                         // bottom plate
    ring(2 * (dome_r - dome_wall) + 0.2, 2 * (dome_r - dome_wall - rebate_t), dome_plate_t + rebate_h, fn = dome_fn);   // rebate ring
    translate([0, 0, dome_plate_t - eps]) radial_ribs(rib_n, dome_plate_r_out - 38, dome_r - dome_wall + 0.1, rib_h, rib_t);
    for (a = susan_hole_angles) dome_az(a) translate([0, susan_hole_r, 0]) cyl(plate_boss_d, plate_boss_h);   // M5 insert bosses
    dome_az(lug_angle) translate([0, dome_wire_anchor_r, 0]) rbox(lug, 2);                                 // wire anchor lug
}
module interior_cuts() {
    for (a = susan_hole_angles) dome_az(a) translate([0, susan_hole_r, 0]) insert_hole(susan_screw_m);
    for (a = susan_access_angles) dome_az(a) translate([0, dome_plate_r_in, -1]) cyl(notch_d, dome_plate_t + 2, fn = 48);   // cable notches
    // zip-tie holes through the lug ABOVE the plate (tangential, so the tie loops over the lug and clears the steel race below)
    dome_az(lug_angle) translate([0, dome_wire_anchor_r, 0]) for (y = [-5, 5]) translate([-lug[0] / 2 - 1, y, lug_hole_z]) rotate([0, 90, 0]) cyl(lug_hole_d, lug[0] + 2, fn = 16);
    dome_az(180) translate([0, 100, dome_plate_t]) rotate([0, 0, 180]) label("dome", 8);
}

// ---------- top disc ----------
module top_disc() {
    translate([0, 0, z_flat - 2]) cyl(dome_top_disc_d, 3, fn = 96);
    translate([0, 0, z_flat - 2]) cyl(top_button_d, 4, fn = 48);
}

// ---------- the part ----------
module dome() {
    difference() {
        union() {
            difference() {
                difference() { dome_solid(0); dome_solid(shell_wall, -1); }      // shell
                surface_recesses();
            }
            interior();
            eye_housing();
            hp_barrel(dome_hp1[0], dome_hp1[1], hp_barrel_proud, gusset = true);
            hp_barrel(dome_hp2[0], dome_hp2[1], hp_barrel_proud, gusset = true);   // truncated flat by the envelope plane
            hp_barrel(dome_hp3_angle, z_at_r(hp3_r), hp_barrel_proud);
            psi_boss(dome_front_psi[0], dome_front_psi[1], dome_front_psi[2], dome_panel_recess);
            psi_boss(dome_rear_psi[0], dome_rear_psi[1], dome_rear_psi[2], dome_panel_recess + inset_depth);
            inset_backing(p5_centre, p5_inset[3], p5_inset[0], p5_inset[1], p5_inset[2]);
            inset_backing(dome_rear_psi[0], p8_inset[3], p8_inset[0], p8_inset[1], p8_inset[2]);
            for (i = [0, 1]) matrix_block(dome_fld_angle, dome_fld_z[i], dome_matrix_pcb[0], fld_dy[i]);
            matrix_block(dome_rld_angle, rld_z, 2 * dome_matrix_pcb[0]);
            for (a = [159.5, 166.8]) at_surface(a, db_z) translate([0, 0, -2]) cyl(db_d, db_proud + 2, fn = 48);   // DB1, DB2
            top_disc();
        }
        eye_cuts();
        hp_cuts(dome_hp1[0], dome_hp1[1], hp_barrel_proud);
        hp_cuts(dome_hp2[0], dome_hp2[1], hp_barrel_proud);
        hp_cuts(dome_hp3_angle, z_at_r(hp3_r), hp_barrel_proud);
        psi_cuts(dome_front_psi[0], dome_front_psi[1], dome_front_psi[2], dome_panel_recess);
        psi_cuts(dome_rear_psi[0], dome_rear_psi[1], dome_rear_psi[2], dome_panel_recess + inset_depth);
        for (i = [0, 1]) matrix_cuts(dome_fld_angle, dome_fld_z[i], dome_fld_window, dome_matrix_pcb[0], fld_dy[i]);
        matrix_cuts(dome_rld_angle, rld_z, dome_rld_window, 2 * dome_matrix_pcb[0]);
        interior_cuts();
    }
}
