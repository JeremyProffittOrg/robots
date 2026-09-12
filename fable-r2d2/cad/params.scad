// fable-r2d2 — single source of dimensions. All values in mm and degrees.
// Scale 0.68386 of the 463.55 mm club-standard R2-D2 (research/proportions.md). Every
// interface between two printed parts is defined here so the part files stay independent.
// Frames: see r2d2.scad. Body frame: Z up the body axis, origin at the skirt-bottom centre,
// +Y = front of the droid, +X = droid's right.

scale_factor = 0.68386;
$fn = 96;

// ---------- print envelope ----------
// H2D left extruder 325 x 320 x 320 mm minus the requested 3 mm buffer on X and Y, and the
// operator's rule "print at max height minus 5 mm": Z limit 315. Every part is sized to use
// as much of this envelope as its geometry allows so the part count stays minimal.
env_x = 322; env_y = 317; env_z = 315;

// ---------- body ----------
body_od = 317.0;                 // = env_y; cylinder limited by the 320 mm axis
body_r = body_od / 2;            // 158.5
body_wall = 3.6;                 // skin thickness (5 x 0.42 mm perimeters plus infill)
body_skin_h = 339.8;             // top ring to skirt top (frame bottom)
skirt_h = 41.3;                  // skirt height
body_height = body_skin_h + skirt_h;   // 381.1 skirt bottom to body top edge
body_seam_from_top = 246.0;      // split between the two rings, measured down the skin
body_upper_h = body_seam_from_top;             // 246.0 (fits 320)
body_lower_h = body_height - body_upper_h;     // 135.1 incl. skirt
skirt_bottom_r = 116.6;          // circle at the skirt bottom
skirt_flat_y = 94.85;            // front/rear flats at Y = +/- 94.85 on the skirt bottom
skirt_rib_n = 12; skirt_rib_t = 8.7;
floor_t = 6;                     // skirt-bottom floor plate thickness (body_lower)
body_lip_h = 6;                  // wall continues above the top plate to hide the bearing
body_top_plate_t = 5;
body_top_plate_z = body_height - body_lip_h;   // 375.1, top face of the top plate (body frame)
seam_flange_w = 12; seam_flange_t = 5;         // internal bolt flange at the ring seam
seam_bolt_n = 8; seam_bolt_m = 4;              // M4 through both flanges, nuts below
seam_lip_h = 6; seam_lip_t = 3;                // locating lip on body_lower, socket in upper
rod_n = 4; rod_r = 138; rod_angle0 = 45;       // four M8 rods on R138 at 45/135/225/315 deg
rod_d = 8; rod_boss_d = 20;
ring_rib_w = 10; ring_rib_t = 4;               // internal horizontal ring ribs
vert_rib_n = 8; vert_rib_t = 3; vert_rib_w = 8;

// shoulder (body side)
shoulder_below_top = 67.2;
shoulder_z = body_height - shoulder_below_top;          // 313.9 in body frame
shoulder_z_upper = shoulder_z - body_lower_h;           // 178.8 in body_upper local frame
shoulder_pad_d = 116;            // flat pad on the body side, face at X = +/- body_r
shoulder_boss_d = 120; shoulder_boss_t = 30;            // internal boss behind the pad
shoulder_bolt_m = 12;            // M12 x 130 class 8.8 through leg + boss, nyloc inside
shoulder_index_r = 45; shoulder_index_d = 6.2;          // 6 mm dowel index pins
shoulder_index_angles = [0, 18];                        // 0 = two-leg, 18 = three-leg (leg forward)
shoulder_spacer = 8;             // flanged bushing + washer stack between pad and leg

// electronics deck: an INTEGRAL horizontal deck inside body_upper (no separate tray part)
tray_z_upper = 40;               // deck top face above the seam; battery top is 110 in body_lower
tray_boss_n = 4; tray_boss_r = 125;   // (kept for reference; the deck is printed into the ring)
tray_size = [230, 190, 4];

// battery (12 V 7 Ah SLA on its side: 151 long X, 94 deep Y, 65 tall)
battery = [151, 94, 65];
battery_shelf_z = 45;            // body_lower local (above the centre-leg flange nuts)
battery_y = 15;                  // shelf centre shifted toward the front for stance balance
battery_strap_w = 25;

// ---------- dome ----------
dome_od = body_od; dome_r = body_r;
dome_wall = 3.0;
dome_a = 171.2;                  // ellipsoid vertical semi-axis
dome_b = 158.5;                  // ellipsoid horizontal semi-axis
dome_band_h = 25.9;              // straight cylindrical band: z 0..25.9, ellipse above
dome_height = dome_band_h + 170.9;   // 196.8 total (band bottom to crown)
dome_plate_t = 5;                // internal bottom annulus (first layers on the bed)
dome_plate_r_in = 57;            // matches lazy-susan 114.3 mm centre hole
dome_plate_r_out = 153.5;        // clears the body lip inner face (155) by 1.5 mm
dome_gap = 1.9;                  // dome band bottom above the body top edge
dome_top_disc_d = 63.1; dome_top_disc_opening_d = 65.9;
dome_pie_r_in = 42.05; dome_pie_r_out = 92.3; dome_pie_divider_w = 5.9;
dome_panel_recess = 0.8; dome_panel_frame_w = 3;
dome_panel_bottom_z = 35.1;      // side-panel bottom line above the band bottom
dome_side_panel_h = 55.4;
dome_hp_d = 44.1;                // three holoprojector openings
dome_hp1 = [25.5, 63.4];         // [angle deg from front, z]
dome_hp2 = [-170.8, 68.2];
dome_hp3_angle = 146.85;         // top holoprojector, in pie panel PP3, centre radius ~101 mm
dome_hp3_r = 101;
dome_front_psi = [7.19, 53.4, 27.0];   // angle, z, opening dia (NeoPixel Jewel 23 mm behind)
dome_rear_psi = [159.5, 62.8, 34.0];
dome_fld_angle = -24.7;          // centre of the front logic display panel P12
dome_fld_window = [30, 21];      // two stacked windows, one 0.8 in 8x8 matrix (20x20) each
dome_fld_z = [48, 74];           // centre heights of the two windows
dome_rld_angle = -135.2;         // rear logic display P9
dome_rld_window = [44, 21];      // two 8x8 matrices side by side (40 x 20)
dome_rld_z = 52;
dome_eye_angle = 0;              // radar eye on the front centreline
dome_eye_lens_d = 52.1;          // 3.000 in scaled
dome_eye_z = 108;                // lens centre height (0.34 D above the ring per image review)
dome_eye_housing = [117, 79];    // width, height of the raised housing
dome_eye_lcd_pcb = [42.4, 36.2, 5.4]; dome_eye_lcd_holes = 22.8;  // Adafruit 6178 round TFT
dome_matrix_pcb = [20, 28, 4];   // Adafruit 872/870 mini 8x8 backpack
dome_wire_anchor_r = 70;         // lug on the plate for the slip-ring rotor wire bundle

// ---------- dome bearing and head drive ----------
susan_od = 228.6; susan_id = 114.3; susan_t = 7.9;   // Triangle 9C lazy susan
susan_hole_r = 156.9 / sqrt(2) / 1;                  // 110.9 mm: 4 holes on a square 156.9 mm
susan_hole_angles = [45, 135, 225, 315];
susan_access_angles = [0, 90, 180, 270];              // access holes for the top-race screws
susan_screw_m = 5; susan_access_d = 12;
top_plate_opening_r = 50;        // central opening in the body top plate
head_wheel_r = 133;              // friction wheel centre radius under the dome plate
head_slot = [36, 60];            // slot in the body top plate (radial x tangential; 63 mm wheel chord)
head_drive_hinge_m = 4;          // hinge bolt through the mount lugs
head_drive_tension_m = 5;        // M5 x 40 adjuster with spring and thumb nut
slip_ring_d = 12.5; slip_ring_l = 19.5;               // Adafruit 1195 body, clamped at the axis
slip_ring_post_h = 24;           // post top above the body top plate

// ---------- outer legs ----------
leg_len = 375.9;                 // shoulder axis to ankle pivot
leg_strut_w = 74.6; leg_strut_t = 30.4;              // fore-aft width, thickness (X)
leg_ankle_w = 86.3; leg_ankle_t = 43.4; leg_ankle_len = 140.9;
leg_ankle_start = 246;           // ankle section starts this far below the shoulder axis
leg_tip_z = -386.9;              // rounded tip below the shoulder axis
leg_disc_d = 136.6;              // shoulder disc on the leg
leg_hub_d = 58.8;                // horseshoe central opening (hub detail visible)
horseshoe_w = 139.4; horseshoe_above = 93.4; horseshoe_below = 89.4; horseshoe_t = 15.2;
horseshoe_arm_w = 31.7; horseshoe_gap = 76.0;
leg_split_z = -220;              // print split between leg_upper and leg_lower
leg_rod_d = 8; leg_rod_offset = 20;                   // two M8 rods at Y = +/- 20 inside the strut
leg_rod_top_z = 55; leg_rod_bottom_z = -370;
leg_splice_bolt_m = 4; leg_splice_len = 40;           // lap joint at the split, 4 x M4
leg_tongue_t = 17.4; leg_tongue_w = 100; leg_tongue_depth = 30;   // into the foot slot
ankle_bolt_m = 8; ankle_bolt_spacing = 50;            // two M8 through foot block and tongue
leg_offset_x = body_r + shoulder_spacer + leg_strut_t/2;   // 181.7 leg centre plane from body axis
leg_track = 2 * leg_offset_x;                         // 363.4 foot centre to centre
booster_cover = [41.7, 78.2, 17.4];
ankle_cyl_d = 21.7; ankle_cyl_l = 43.4;

// ---------- stance ----------
body_tilt = 18;                  // three-leg stance: body top tilted toward the rear
leg_lean = 18;                   // outer legs lean 18 deg, feet forward of the shoulders
ankle_z = 105.5;                 // ankle pivot height above the floor (two-leg reference)
shoulder_h = shoulder_z;         // body-frame height of the shoulder axis (alias)
shoulder_y_in_body = 0;
center_leg_y_in_body = 0;
shoulder_z_three_leg = ankle_z + leg_len * cos(leg_lean);   // 463.0 above the floor

// ---------- feet ----------
foot_clear = 12;                 // shell bottom edge above the floor
wheel_axle_z = 31.5 - foot_clear;      // 19.5 in the foot frame (z=0 at the shell bottom edge)
foot_outer_l_bot = 243.2; foot_outer_l_top = 122.7;
foot_outer_w_bot = 123.3; foot_outer_w_top = 60.8;
foot_outer_h = 87.2;
foot_end_slope = 33.7; foot_side_slope = 14.9;
foot_center_l_bot = 180.2; foot_center_l_top = 58.6;
foot_center_w_bot = 123.3; foot_center_w_top = 52.1;
foot_center_h = 86.9;
foot_wall = 3.2;
foot_axle_y = 45;                // motors at Y = +/- 45 in each foot
motor_pocket_clear = 0.4;
wheel_x = 23.8;                  // wheel centre offset from the motor centre plane (each side)
foot_slot_w = 17.6; foot_slot_depth = 30;            // ankle tongue slot (outer feet)
battery_box = [119.4, 53.5, 84.7];                    // decorative boxes on the outer feet
caster_bolt_m = 12; caster_bearing_od = 28; caster_bearing_t = 8; caster_bearing_gap = 20;
caster_trail = 20;               // pivot axis ahead of the foot's axle midpoint
caster_stop_deg = 60;            // swivel limit each way
center_leg_section = [100.3, 71.7];                   // ankle ring size (X, Y)
center_leg_flange = [140, 100, 8]; center_leg_bolt_m = 8; center_leg_bolts = [[-50, -32], [50, -32], [-50, 32], [50, 32]];

// ---------- purchased envelopes (for placement and renders) ----------
pi4 = [85, 56, 20]; pi4_holes = [[3.5, 3.5], [61.5, 3.5], [3.5, 52.5], [61.5, 52.5]];
kb2040 = [35, 17.8, 5];
drv8833 = [26, 18, 3];
regulator = [25.4, 25.4, 9.5];
speaker_d = 77.8; speaker_depth = 25.5;

// ---------- derived (assembly) ----------
dome_spin = 0;
