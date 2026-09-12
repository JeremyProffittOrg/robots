// doorbot — single source of every dimension. Millimetres and degrees. Revision A.
// Read by OpenSCAD and by scripts/scad_params.py, so the CAD, the mechanism checks, the BOM
// and the drawings cannot drift apart.
//
// WHERE THE MACHINE SITS
// The base unit is one printed shell that screws to the hinge-side jamb reveal - the face the
// hinges are screwed to - standing in the rebate behind the closed door, on the PUSH side.
// A cable runs from a drum inside it to a printed anchor on the door face. Winding the cable
// in swings the door shut; magnets at the latch edge take over for the last few millimetres
// and hold it closed. The cover faces out along the doorway, so the display, the hand-wave
// target and both time-of-flight sensors look down the opening and are never covered by the
// door itself.
//
// DOOR FRAME used by scripts/check_mechanism.py (horizontal plane, hinge axis at the origin):
//   +x = along the closed door, into the opening
//   +y = the PUSH side, the side the door does NOT swing towards
//   The hinge axis of an ordinary butt hinge lies essentially in the door's push face, so the
//   leaf sweeps only the quarter turn at negative polar angles. Any point with x > 0 and
//   y > 0 - the whole jamb rebate - is therefore outside the swept volume at every angle.
//   theta = 0 closed, theta = door_open_deg fully open.
//
// UNIT FRAME used by the CAD (print frame, shell open face up):
//   X = across the jamb depth  (= door +y)
//   Y = vertical               (= door +z)
//   Z = out into the opening   (= door +x), so the cover is the +Z face

$fn = 64;
eps = 0.01;

// ---------- the door and frame this revision is sized for (user-locked) ----------
door_mass_kg = 40;            // worst case of the stated 30-40 kg solid-core band
door_width_mm = 914;          // 36 in leaf
door_thick_mm = 35;           // 1-3/8 in solid core
door_open_deg = 90;
frame_plumb_deg = 0.5;        // assumed installation tolerance; gravity torque scales with it
rebate_depth_mm = 51;         // free push-side depth in a 4-9/16 in jamb behind a 35 mm door

// ---------- cable geometry (algebra and every check in scripts/check_mechanism.py) ----------
// The exit is deliberately off the closed-door plane. Put it ON that plane and the exit, the
// hinge axis and the anchor are collinear when the door is shut: the moment arm is exactly
// zero and no tension whatever can close the last degree. Offsetting it keeps the included
// angle between 41 and 131 degrees, so the arm never approaches either dead centre.
anchor_a = 300;               // anchor along the leaf from the hinge axis
anchor_standoff = 25;         // anchor cable eye stands this far off the leaf face, push side
exit_x = 47;                  // cable exit, into the opening from the hinge axis
exit_y = 48;                  // cable exit, off the closed-door plane, push side
build_tol_mm = 2;             // mounting error subtracted from the arm in every check
cable_guide_deg = 40;         // total cable bend inside the shell, drum to exit chute
cable_guide_mu = 0.15;        // Dyneema on printed PLA; capstan loss is exp(mu * angle)

cable_d = 1.2;                // braided Dyneema, 150 lb test
cable_break_n = 680;
drum_r = 2.5;                 // groove bottom radius; the cable centre runs at 3.1 mm
drum_width = 10;              // grooved length available
drum_pitch = 1.3;             // one helical groove per turn
drum_flange_d = 15;

// ---------- gear train: two printed spur stages, 12:1 ----------
// Both wheels stay under 47 mm across so the shell fits the 51 mm jamb rebate. The stage
// faces come from the Lewis check in check_mechanism.py, not from taste.
module1 = 0.8;  stage1_pinion_t = 12;  stage1_gear_t = 48;  face1 = 10;
module2 = 1.0;  stage2_pinion_t = 14;  stage2_gear_t = 42;  face2 = 16;
gear_backlash = 0.24;         // removed from tooth thickness at the pitch circle, total
gear_pa = 20;                 // pressure angle
gear_clearance = 0.25;        // root clearance as a fraction of the module
pin_d = 4;                    // steel dowel shafts
pin_bore = 4.3;               // printed running bore on the dowel
gear_hub_d = 12;
gear_gap = 1.0;               // axial clearance between a gear face and a wall

// ---------- TT motor, Adafruit 3777 / DAGU DG01D-A130, 1:48 ----------
tt_body_l = 64.2; tt_body_w = 22.5; tt_body_h = 18.8;
tt_shaft_d = 5.4; tt_shaft_flat = 3.6; tt_shaft_len = 9.4;
tt_collar_d = 7.2;
tt_axis_from_gearbox_end = 11.2;
tt_hole_spacing = 17.5; tt_hole_from_axis = 31.8; tt_hole_d = 3.2;

// ---------- base unit: one unibody shell plus a cover ----------
base_w = 50;                  // X, across the jamb depth (rebate allows 51)
base_h = 200;                 // Y, vertical
base_z = 36;                  // Z, out into the opening
wall = 2.4;
floor_t = 3.0;
cover_t = 2.0;
cover_lip = 1.6;
foot_h = 12;                  // integral standoff feet; also the encoder-wheel and cable space
mount_screws = 3;
mount_screw_d = 4.5;          // clearance for #8 jamb screws
mount_y = [18, 100, 182];     // screw heights up the shell
screw_boss_d = 8.4;
m3_tap_d = 2.6;               // self-tapping pilot in PLA
m3_free_d = 3.4;
cover_screws = 4;

// ---------- axis layout inside the shell (unit frame X, Y) ----------
drum_axis = [25, 25];         // drum and stage-2 wheel
compound_axis = [25, 53];     // stage-2 pinion and stage-1 wheel, cd 28 from drum_axis
motor_axis = [25, 77];        // motor shaft, cd 24 from compound_axis
// Depth planes, measured in Z from the shell's inner floor face:
plane2_z = 3;                 // stage-2 pair, face2 deep
plane1_z = 22;                // stage-1 pair, face1 deep
drum_z = 19;                  // drum, drum_width deep
motor_z = 3;                  // motor body, tt_body_h deep

// ---------- electronics ----------
tdisp_l = 51.5; tdisp_w = 25.7; tdisp_t = 8.2;
tdisp_screen_l = 26.8; tdisp_screen_w = 14.3;
tdisp_pos = [12, 138];        // lower-left of the module in the shell, unit frame
drv_l = 20.5; drv_w = 20.5; drv_t = 11.0;
drv_pos = [38, 60];
tof_l = 25.4; tof_w = 17.8; tof_t = 5.0;
tof_hole_l = 20.3; tof_hole_w = 12.7;
tof_wave_pos = [12, 108];     // VL53L4CD, hand-wave target, looks out along +Z
tof_guard_pos = [12, 176];    // VL53L1X, doorway and closing path, looks out along +Z
accel_l = 25.4; accel_w = 17.8; accel_t = 5.0;
accel_pos = [34, 100];        // LIS3DH, on the floor beside a mounting screw for a rigid path
window_d = 9.0;               // clear aperture over a ToF sensor
wave_target_d = 26;           // engraved ring around the hand-wave window
buzzer_d = 12.5; buzzer_t = 9.5;
buzzer_pos = [38, 30];
encoder_wheel_d = 26;         // Adafruit 3782 snap-on encoder wheel, on the spare shaft
encoder_slot_l = 24; encoder_slot_w = 12; encoder_slot_t = 6;

// ---------- door anchor ----------
anchor_base_l = 60;
anchor_base_w = 22;
anchor_base_t = 5.0;
anchor_screws = 3;
anchor_screw_d = 4.0;         // #8 wood screws into the stile
anchor_screw_pitch = 20;
cable_eye_wall = 5.0;
cable_eye_h = 10.0;
cable_eye_d = 3.0;

// ---------- magnet catch: one printed design, printed twice ----------
magnet_d = 12.7;              // K&J D84, 1/2 x 1/4 in N42
magnet_t = 6.35;
magnet_pocket_d = 12.85;
magnet_pocket_wall = 2.0;
magnet_cap_t = 0.6;           // three bridged layers over the working face; no adhesive
magnets_per_pod = 2;
magnet_pitch = 34;
magnet_radius_mm = 899;       // pod distance from the hinge axis, at the latch edge
magnet_gap_closed_mm = 2.0;   // two 0.6 mm caps plus as-built clearance
pod_l = 58; pod_w = 20; pod_t = 9.0;
pod_screws = 2;
pod_screw_d = 3.5;

// ---------- print envelope: smallest current Bambu bed, so every part fits every printer ----------
env_x = 256; env_y = 256; env_z = 256;
layer_h = 0.2;
nozzle = 0.4;
