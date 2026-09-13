// Revision D sensed shoulder stance lock (candidate design, not yet included by the assembly).
// Winco GN 412 spring plunger on the right chassis carrier, two GN 412.2 receivers in a printed ring on the
// right leg, Omron SS-01GL seat sensor pressed by a knob-collar flag, MG995 release lever.
// Every identifier carries an SL_/sl_ prefix so it cannot collide with the GN817 lock in stance-lock.scad.
// Include after exterior.scad, kinematics.scad and printed-frame.scad. Millimetres; body frame unless noted.
// scripts/check_kinematics.py parses every "SL_NAME=number;" line: keep design numbers literal.
SL_STEEL="#9aa3ab"; SL_DARK="#20262d"; SL_PRINT="#768ba0";
// Winco GN 412-6-35-B-1 plunger on the right carrier; two GN 412.2-M12X1.5-B6.2 receivers in the right leg ring.
SL_LOCK_RADIUS=55;
SL_LOCK_PIN_ANGLE=-90;       // body-frame angle in the Y-Z plane, from +Y toward +Z
SL_LOCK_RECEIVER_TWO_FOOT=0; // body pitch at which each receiver meets the pin
SL_LOCK_RECEIVER_THREE_FOOT=16.163;
SL_LOCK_PIN_EXIT_X=135;
SL_LOCK_RING_FACE_X=136;
SL_LOCK_PIN_EXTENSION=6;
SL_LOCK_BUSHING_LENGTH=13;
SL_LOCK_BUSHING_OD=12;
SL_LOCK_RING_INNER=45;
SL_LOCK_RING_OUTER=63;
SL_LOCK_RING_ARC_START=-104;
SL_LOCK_RING_ARC_END=-63;
SL_LOCK_KNOB_SEAT_X=113;     // knob underside with the pin fully seated
// Omron SS-01GL pressed by the knob collar flag only when seated: set overtravel and adjustment.
SL_LOCK_SWITCH_OVERTRAVEL=0.9;
SL_LOCK_SWITCH_ADJUST=0.2;
// MG995 release lever: pivot on the servo shaft (Y axis) and finger contact on the collar flag.
SL_RELEASE_PIVOT_X=107;
SL_RELEASE_PIVOT_Z=291;
SL_RELEASE_FINGER_X=115.5;
SL_RELEASE_FINGER_Z=308;
SL_RELEASE_ROTATION=28;
SL_LOCK_PIN_Y=SL_LOCK_RADIUS*cos(SL_LOCK_PIN_ANGLE);
SL_LOCK_PIN_Z=HIP_Z+SL_LOCK_RADIUS*sin(SL_LOCK_PIN_ANGLE);
// Lock frame: origin at the plunger pin-exit face, +X along the pin.
module sl_lock_frame(){translate([SL_LOCK_PIN_EXIT_X,SL_LOCK_PIN_Y,SL_LOCK_PIN_Z])children();}

// ---------------------------------------------------------------- revision D stance-lock purchased envelopes
// Winco GN 412-6-35-B-1. Lock-frame coordinates; pull moves the pin and knob toward -X.
module sl_gn412_plunger(pull=0){
 color(SL_STEEL)difference(){
  translate([-12,-17.5,-14])cube([12,35,26]);
  for(y=[-12.5,12.5])translate([0,y,0]){rotate([0,90,0])cylinder(d=4.3,h=30,center=true,$fn=24);
   translate([-6,0,0])rotate([0,90,0])cylinder(d=8,h=6.1,$fn=24);}
 }
 color(SL_STEEL)translate([-22,0,0])rotate([0,90,0])cylinder(d=12/cos(30),h=10,$fn=6);
 translate([-pull,0,0]){
  color(SL_STEEL)rotate([0,90,0])translate([0,0,-22])cylinder(d=6,h=28,$fn=32);
  color(SL_DARK)translate([-32,0,0])rotate([0,90,0])cylinder(d=25,h=10,$fn=48);
 }
}
// Winco GN 412.2-M12X1.5-B6.2 hardened receiver bushing: 10 mm M12 body, 3 mm hex A/F 13, 6.2 mm bore.
// Local: bore along +X, body face at X=0.
module sl_gn412_2_bushing(){color(SL_STEEL)difference(){union(){
 rotate([0,90,0])cylinder(d=12,h=10,$fn=40);translate([10,0,0])rotate([0,90,0])cylinder(d=13/cos(30),h=3,$fn=6);}
 rotate([0,90,0])translate([0,0,-1])cylinder(d=6.2,h=15,$fn=32);}}
// Omron SS-01GL hinge lever switch. Local: mounting-hole line at X=0, lever faces -X, length along Z.
// OP is 8.8 mm from the hole line; holes are 2.35 mm at 9.5 mm pitch. Body top assumed 7.3 mm from the hole line.
module sl_ss01gl_switch(pressed=true){
 color(SL_DARK)difference(){translate([-7.3,-3.2,-9.9])cube([10.2,6.4,19.8]);
  for(z=[-4.75,4.75])translate([0,0,z])rotate([90,0,0])cylinder(d=2.35,h=8,center=true,$fn=16);}
 color(SL_STEEL)translate([-(pressed?8.8+SL_LOCK_SWITCH_OVERTRAVEL:13.6),-1.5,-9.9])cube([.3,3,14.5]);
}
// MG995 servo envelope, 40.7 x 19.7 x 42.9 mm (Adafruit 1142). Local: output shaft on the origin,
// shaft axis toward -Y, body length along -Z from 10 mm above the shaft.
module sl_mg995_servo(){
 color(SL_DARK){translate([-9.85,3,-30.7])cube([19.7,36,40.7]);
  difference(){translate([-9.85,10,-37.45])cube([19.7,2.5,54.2]);
   for(x=[-5,5])for(z=[-34.1,13.4])translate([x,0,z])rotate([90,0,0])cylinder(d=4.5,h=30,center=true,$fn=16);}}
 color("#c8ccd0")translate([0,0,0])rotate([90,0,0])cylinder(d=6,h=3,$fn=24);
}


// Revision D positive shoulder stance lock, release and engagement sensor. Right side only.
// Include after kinematics.scad and printed-frame.scad. Millimetres; body frame unless noted.
// Purchased envelopes follow the manufacturer drawings named in docs/revision-d-mechanism.md.

// ---------------------------------------------------------------- printed chassis features
// Merged into frame_chassis(): plunger mount plate, switch pad, servo ear pads and ties to the carrier.
module sl_lock_mount_positive(){
 sl_lock_frame(){
  translate([-18,-22,-16])cube([6,44,33]);                         // plunger plate, X 117..123
  translate([-18.1,-13,-38])cube([10.1,5.8,24]);                    // SS-01GL pad beside the flag
 }
 // Ties: plate to the carrier cylinder and to the side wall.
 hull(){sl_lock_frame()translate([-18,-10,15])cube([5,20,2]);translate([117,-10,370])cube([5,20,2]);}
 for(y=[-22,16])hull(){sl_lock_frame()translate([-18,y,10])cube([6,6,7]);translate([84,y,356])cube([6,6,8]);}
 // MG995 ear pads behind the two ear tabs (clear of the servo body) and the strut beside the servo.
 translate([SL_RELEASE_PIVOT_X,25.5,SL_RELEASE_PIVOT_Z])for(z=[[-37.45,-30.7],[10,16.75]])translate([-9.85,0,z[0]])cube([24.35,5.5,z[1]-z[0]]);
 translate([SL_RELEASE_PIVOT_X+10,25.5,SL_RELEASE_PIVOT_Z-37.45])cube([4.5,5.5,54.2]);
 hull(){translate([SL_RELEASE_PIVOT_X+10,25.5,SL_RELEASE_PIVOT_Z+12.75])cube([4.5,5.5,4]);sl_lock_frame()translate([-18,16,-16])cube([6,6,4]);}
}
module sl_lock_mount_negative(){
 sl_lock_frame(){
  translate([-18.1,0,0])rotate([0,90,0])cylinder(d=14.5,h=6.2,$fn=32);  // spigot clearance
  for(y=[-12.5,12.5])translate([-18.1,y,0]){rotate([0,90,0])cylinder(d=4.5,h=6.2,$fn=24);
   rotate([0,90,0])cylinder(d=7.4/cos(30),h=3.5,$fn=6);}             // M4 nut pockets from the back
  translate([-10.8,-13.1,-28.1])for(z=[-4.75,4.75])translate([0,0,z])rotate([90,0,0])cylinder(d=2.5,h=12,center=true,$fn=16);
 }
 translate([SL_RELEASE_PIVOT_X,28,SL_RELEASE_PIVOT_Z])for(x=[-5,5])for(z=[-34.1,13.4])translate([x,0,z])rotate([90,0,0])cylinder(d=4.5,h=12,center=true,$fn=16);
}

// ---------------------------------------------------------------- printed moving parts
// Shoulder lock ring on the right leg, world coordinates. Clamped by the four hub screws; its tube
// is the printed inner-race spacer against the outer 6201 bearing. Receivers sit at the two stance angles.
module sl_lock_ring(){
 difference(){union(){
  translate([SL_LOCK_RING_FACE_X,0,HIP_Z])rotate([0,90,0])linear_extrude(149-SL_LOCK_RING_FACE_X)
   rotate(90)hull(){circle(r=16.5,$fn=48);sl_lock_ring_sector();}
  translate([143,0,HIP_Z])rotate([0,90,0])cylinder(r=16.5,h=10,$fn=48);
 }
 translate([121,0,HIP_Z])rotate([0,90,0])cylinder(d=12.4,h=40,$fn=40);
 for(y=[-8,8])for(z=[-8,8])translate([0,y,HIP_Z+z]){rotate([0,90,0])translate([0,0,130])cylinder(d=4.5,h=30,$fn=20);
  translate([SL_LOCK_RING_FACE_X-.1,0,0])rotate([0,90,0])cylinder(d=8.2,h=143.1-SL_LOCK_RING_FACE_X,$fn=24);}
 for(a=[SL_LOCK_RECEIVER_TWO_FOOT,SL_LOCK_RECEIVER_THREE_FOOT])sl_lock_receiver_at(a){
  translate([-.1,0,0])rotate([0,90,0])cylinder(d=12.2,h=10.2,$fn=40);
  translate([9.9,0,0])rotate([0,90,0])cylinder(d=13.3/cos(30),h=3.3,$fn=6);
 }
 }
}
module sl_lock_ring_sector(){
 // 2D in the ring plane: (Y, Z) relative to the shoulder axis.
 polygon(concat([for(a=[SL_LOCK_RING_ARC_START:2:SL_LOCK_RING_ARC_END])[SL_LOCK_RING_OUTER*cos(a),SL_LOCK_RING_OUTER*sin(a)]],
  [for(a=[SL_LOCK_RING_ARC_END:-2:SL_LOCK_RING_ARC_START])[SL_LOCK_RING_INNER*cos(a),SL_LOCK_RING_INNER*sin(a)]]));
}
// Receiver pose: at body pitch a the pin sits at world angle SL_LOCK_PIN_ANGLE+a on the lock radius.
module sl_lock_receiver_at(a){translate([SL_LOCK_RING_FACE_X,SL_LOCK_RADIUS*cos(SL_LOCK_PIN_ANGLE+a),HIP_Z+SL_LOCK_RADIUS*sin(SL_LOCK_PIN_ANGLE+a)])children();}
// Right side: printed inner-race spacer between the outer 6201 inner race and the lock ring face.
module sl_race_spacer(){difference(){translate([122,0,HIP_Z])rotate([0,90,0])cylinder(d=16.5,h=SL_LOCK_RING_FACE_X-122,$fn=48);
 translate([121,0,HIP_Z])rotate([0,90,0])cylinder(d=12.4,h=20,$fn=40);}}
// Left side: printed inner-race spacer clamped by the left hub screws (world coordinates, mirrored in assembly).
module sl_shoulder_spacer(){
 difference(){union(){translate([143,0,HIP_Z])rotate([0,90,0])cylinder(r=16.5,h=10,$fn=48);
  translate([122,0,HIP_Z])rotate([0,90,0])cylinder(d=16.5,h=21.1,$fn=48);}
 translate([121,0,HIP_Z])rotate([0,90,0])cylinder(d=12.4,h=40,$fn=40);
 for(y=[-8,8])for(z=[-8,8])translate([142,y,HIP_Z+z]){rotate([0,90,0])cylinder(d=4.5,h=14,$fn=20);
  rotate([0,90,0])cylinder(d=8.2,h=5.1,$fn=24);}
 }
}
// Snap collar on the GN 412 knob, lock-frame coordinates at pull 0. Its flag presses the switch and
// receives the release finger. Back and front lips capture the knob axially.
module sl_knob_collar(){
 difference(){union(){
  translate([-33.5,0,0])rotate([0,90,0])cylinder(r=15.5,h=13,$fn=48);
  translate([-24.5,-8,-30])cube([4,14,17]);
 }
 translate([-32,0,0])rotate([0,90,0])cylinder(r=12.75,h=10,$fn=48);     // knob
 translate([-34,0,0])rotate([0,90,0])cylinder(r=8,h=3,$fn=32);          // back opening
 translate([-22.1,0,0])rotate([0,90,0])cylinder(r=7.6,h=2,$fn=32);      // spigot passes the front lip
 translate([-35,-8,0])cube([16,16,20]);                                   // snap-on slot from below
 }
}
// Release lever on the MG995 horn. It captures the horn arm in a pocket; the horn centre screw clamps it.
module sl_release_lever(){
 difference(){union(){
  hull(){translate([SL_RELEASE_PIVOT_X,5,SL_RELEASE_PIVOT_Z])rotate([-90,0,0])cylinder(r=8,h=4,$fn=40);
   translate([SL_RELEASE_FINGER_X,5,SL_RELEASE_FINGER_Z-3])cube([3,4,6]);}
  translate([SL_RELEASE_FINGER_X,1.5,SL_RELEASE_FINGER_Z-3])cube([3,7.5,6]);
 }
 translate([SL_RELEASE_PIVOT_X,0,SL_RELEASE_PIVOT_Z])rotate([-90,0,0])cylinder(d=3.2,h=20,$fn=16);
 translate([SL_RELEASE_PIVOT_X-3,7.5,SL_RELEASE_PIVOT_Z-22])cube([6,1.6,26]);    // horn-arm pocket
 }
}
// Body-shell slot where the plunger flange crosses the skin (right side only). It is open to the upper
// shell's bottom edge so that shell can slide down over the installed plunger; the leg hides it from the side.
module sl_shell_clearance(){translate([0,0,-BODY_Z])sl_lock_frame()translate([-16,-19.5,BODY_Z+SPLIT-SL_LOCK_PIN_Z-1])cube([20,39,SL_LOCK_PIN_Z+14-BODY_Z-SPLIT+1]);}

// ---------------------------------------------------------------- assembled mechanism views
module sl_stance_lock_body(pull=0){
 sl_lock_frame(){sl_gn412_plunger(pull);translate([-pull,0,0])color(SL_PRINT)sl_knob_collar();}
 sl_lock_frame()translate([-10.8,-4,-28.1])sl_ss01gl_switch(pull<SL_LOCK_SWITCH_OVERTRAVEL);
 translate([SL_RELEASE_PIVOT_X,13,SL_RELEASE_PIVOT_Z])sl_mg995_servo();
 color(SL_PRINT)translate([SL_RELEASE_PIVOT_X,0,SL_RELEASE_PIVOT_Z])rotate([0,pull>0?-SL_RELEASE_ROTATION:0,0])
  translate([-SL_RELEASE_PIVOT_X,0,-SL_RELEASE_PIVOT_Z])sl_release_lever();
}
module sl_stance_lock_leg(){
 color(SL_PRINT){sl_lock_ring();sl_race_spacer();}
 for(a=[SL_LOCK_RECEIVER_TWO_FOOT,SL_LOCK_RECEIVER_THREE_FOOT])sl_lock_receiver_at(a)sl_gn412_2_bushing();
}
