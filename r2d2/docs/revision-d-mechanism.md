# Revision D centre-leg mechanism

Status: calculated and modelled on 2026-09-12. Not built, not weighed, not load tested.
The sensed lock source is `cad/stance-lock-sensed.scad`. It is not yet included by the assembly;
see "Two lock designs" for the hunks that swap it in.
This note covers the `mechanical` milestone: front deployment, full retraction, the
positive shoulder stance lock and its sensor, and the two-foot centre of gravity.

## Requirement (user-confirmed 2026-09-12)

- The centre foot deploys toward the front. For the two-foot stance the post retracts
  fully and all four centre wheels leave the floor. Standing still on two feet is
  required; driving on two feet is not.
- The stance change is motorized and interlocked. A positive shoulder lock holds each
  stance. A switch senses the engaged lock; actuator position never stands in for it.
  Loss of command or power must leave the robot held.

## Selected parts

| Function | Part | Qty | Primary data used | Source |
|---|---|---|---|---|
| Post actuator | Actuonix P16-100-256-12-P | 1 | 100 mm stroke; 147 mm closed eye to eye; eye bore 4.25 mm; 300 N maximum lifted force; >500 N back-drive; 4.8 mm/s no load; 1000 mA stall at 12 V; 20 % duty; 110 g; 11 kΩ ±50 % feedback potentiometer; repeatability 0.4 mm, backlash 0.3 mm; listed $90, backordered | [product](https://www.actuonix.com/p16-100-256-12-p), [datasheet](https://www.actuonix.com/assets/images/datasheets/ActuonixP16Datasheet.pdf) |
| Shoulder lock | J.W. Winco GN 412-6-35-B-1 indexing plunger | 1 | 6 mm pin, 0/−0.06; minimum extension 6 mm; spring 5 N initial, 15 N end; flange 35 × 26 × 12 mm, counterbored M4 bores at 25 mm; knob Ø25 mm, 32 mm from the flange underside; 0.152 lb; US$11.77 | [drawing](https://live-catalog.jwwinco.com/pdf/winco/us/412.pdf?dispositiontype=attachment), [product](https://www.jwwinco.com/en-us/products/3.1-Indexing-locking-blocking-with-pins-and-ball-shaped-elements/Indexing-plungers/GN-412-Zinc-Die-Cast-Indexing-Plungers-with-Screw-On-Flange) |
| Lock receivers | J.W. Winco GN 412.2-M12X1.5-B6.2 hardened bushing | 2 | bore 6.2 +0.1 mm; M12 × 1.5 body 10 mm; overall 13 mm; hex A/F 13; 0.022 lb; US$5.66 | [drawing](https://live-catalog.jwwinco.com/pdf/winco/us/412_2.pdf?dispositiontype=attachment) |
| Lock sensor | Omron SS-01GL hinge-lever switch, gold contact | 1 | SPDT; 0.1 A 30 VDC; minimum load 5 VDC 1 mA; OF ≤0.49 N; OT ≥1.2 mm; MD ≤0.8 mm; OP 8.8 ±0.8 mm; holes Ø2.35 mm at 9.5 mm; US$4.23 at Digi-Key | [datasheet](https://omronfs.omron.com/en_US/ecb/products/pdf/en-ss.pdf) |
| Lock release | MG995 servo (existing ledger servo) | 1 | 8.5 kg·cm at 4.8 V; 10 kg·cm at 6 V; 62.41 g | [Adafruit 1142](https://www.adafruit.com/product/1142) |
| Post | MISUMI HFS5-2020, 290 mm | 1 | 20 × 20 mm; 0.5 kg/m | [drawing](https://us.misumi-ec.com/pdf/fa/2019/2019_US_2686.pdf) |

Plunger flange screws are 2 × ISO 4762 M4×16 with 2 × M4 nuts captured in the printed
mount. The P16 uses the existing 2 clevis pins and 4 R-clips. The SS-01GL uses the existing
limit-switch screws and nuts. The MG995 uses the existing servo mount screws, nuts, horn and
horn screw.

## Geometry

Stance values are literals in `cad/kinematics.scad`. The lock values are `SL_`-prefixed
literals in `cad/stance-lock-sensed.scad`. `scripts/check_kinematics.py` reads both files.

- Post guide: printed into the chassis at Y 40, Z 240 mm, inclined 30° from vertical and
  pointing forward-down. Two printed sliding lands, 21.0 mm square and 20 mm long, are centred
  at −130 and −10 mm along the guide. This replaces the acetal pads and their screws.
- Stroke use: two-foot endpoint 2 mm, three-foot endpoint 98 mm, inside the 100 mm stroke
  with 0.7 mm position error at each end. Floor contact with the body upright is at
  36.647 mm.
- Three-foot stance: body pitch 16.163° back, centre ankle 230.2 mm ahead of the hip.
- Two-foot stance: ankle lifted 30.0 mm. The retracted rail top passes a slot in the upper
  deck and stays below Z 450 mm, under the dome ring.
- Actuator: parallel to the post, 40 mm in front of it. Fixed eye 70 mm up the guide, rod eye
  33 mm up the post adapter. Pin spacing is 147 mm at stroke 0.
- Centre foot: printed bars across the fork gap meet the M12 rod-end shank. They limit the
  hanging foot to 1° heel-down and 17.5° toe-down. The toe limit is what lets the foot stand
  flat while the body leans 16.2°. The foot CG from the meshes and masses is 10.6 mm behind
  the ankle, so a lifted foot rests on the heel stop.

## Shoulder lock, release and sensor

- The plunger bolts to a printed plate on the right chassis shoulder carrier. Its pin is
  parallel to X, 55 mm below the shoulder axis. The flange passes through a 39 mm wide slot in
  the upper shell. The slot is open to the shell's bottom edge, so the shell slides down over the
  installed plunger; the leg hides the slot from the side.
- A printed lock ring is clamped to the right leg by the four existing hub screws. It holds
  both receivers at radius 55 mm: one aligned at 0° body pitch, one at 16.163°. The receiver
  chord is 15.5 mm, which leaves a 3.5 mm web between the 12 mm bushings. Each bushing hex is
  trapped between the ring and the leg core, so no nut is needed.
- Between the receivers the ring face is continuous, from −104° to −63° at radius 45-63 mm. The spring pin rides
  this face while the body pitches and can seat only in a receiver.
- Pin engagement is 5.0 mm: pin exit face at X 135, ring face at X 136.
- The printed ring hub, a printed race spacer on the right and a printed shoulder spacer on
  the left bear on the outer 6201 inner races. They replace the purchased collars and
  inner-race spacers.
- A printed snap collar on the plunger knob carries a flag. The flag presses the SS-01GL lever
  only when the pin is fully seated. Set overtravel is 0.9 ±0.2 mm, within the 1.2 mm rating.
  With the 0.8 mm differential, the switch cannot read "engaged" with less than 3.1 mm of pin
  in the bushing.
- Release: a printed lever on the MG995 horn pushes the flag. Finger arm is 17 mm and
  rotation 28°. It pulls the pin 7.98 mm, which clears the 5 mm engagement.
- Loss of power: the plunger spring holds or re-seats the pin. The unpowered servo does not
  hold it out. The post is held by the P16 back-drive rating.

## Transition sequence the check models

Deploy (two-foot to three-foot):
1. Locked at 2 mm, foot lifted.
2. Extend to contact at 36.647 mm with the lock engaged.
3. Release the pin.
4. Extend, unlocked, to 98 mm. The pin rides the ring.
5. The pin seats in the three-foot receiver and is sensed.

Retract (three-foot to two-foot):
1. Release at 98 mm.
2. Retract, unlocked, to contact.
3. The pin seats in the two-foot receiver and is sensed.
4. Retract, locked, to 2 mm.

Drive is refused during a transition. Firmware implements this; it is not part of this
milestone.

## Check results

`python scripts/check_kinematics.py` samples both directions every 0.25 mm plus the exact
contact stroke. It writes `cad/kinematic-check.json` and exits 1 on any failure.

| Class | Criterion | Result |
|---|---|---|
| Clearance | resting two-foot foot clearance ≥20 mm; no floor contact at either ankle stop; no early touchdown | PASS: resting 29.37 mm; either stop 12.44 mm |
| Support | two-foot and three-foot CG margin ≥10 mm, over a ±8/±8/±40 mm body CG box and ±8° centre yaw | PASS: two-foot 15.47 mm; three-foot 47.51 mm |
| Force | 3 × (gravity + guide friction μ 0.35 + 10 N rolling drag) ≤300 N; 3 × gravity ≤500 N back-drive; 1.5 × (15 N spring + 0.49 N switch + 0.3 × pin shear) ≤ MG995 stall force | PASS: actuator 91.1 N factored, holding 22.6 N; release 36.3 N (contact) and 45.4 N (three-foot) against 49.0 N |
| Restraint | receivers within 0.1 mm radial clearance at both endpoints; engagement 3-13 mm; sensor limits above; unlocked body CG ahead of the hip | PASS: engagement 5.00 mm, sensed minimum 3.10 mm; unlocked body CG at least 5.02 mm ahead of the hip |

## CAD interference evidence

OpenSCAD CGAL intersections were run on 2026-09-12 against the exported `frame_chassis`,
`post_adapter` and `center_foot_core` meshes and the mechanism source modules. Empty means
there is no shared volume. Contact means the shared region has zero volume.

- Chassis against GN 412, SS-01GL and MG995 envelopes, pin seated: contact, at the flange and
  pad faces only.
- Chassis against the pulled plunger, knob collar and rotated release lever: contact, at the
  flange back face only.
- Chassis against the standing battery: contact, on the rail-tie top face at Z 189 only.
- Chassis against the post, adapter, rod end and P16 envelope at 2 mm and 98 mm: empty.
- Knob collar and release lever against the switch, servo and plunger: contact.
- Lock ring and bushings against the plunger region at 0°, 8° and 16.163°: empty.
- Battery against the release servo and the post at both endpoints: empty.
- Centre foot core against the adapter and rod end: empty at 2 mm on the heel stop, at contact,
  at 60 mm and at 98 mm. At the 17.5° toe stop it is empty; the stop bars are tangent to the
  shank.

These checks fixed four real clashes before release:
- MG995 ear pads inside the servo body
- P16 fixed clevis 1 mm into the case
- the post-adapter steering tab 0.5 mm into the fork plate
- the steering arm against the chassis tray at 2 mm, fixed by widening the tray opening

- Right leg source (exterior and core) against the lock ring, race spacer and bushings: contact,
  on the leg-core backing face at X 149 only. The first run found a 0.8 mm³ overlap with the
  leg cup wall; the ring was trimmed to 63 mm radius and a -63° arc end.
- Stowed centre foot (core and cover mesh, heel stop, 2 mm) against the chassis and P16 case:
  empty.

The body shells and dome were not intersected as whole prints. The upper shell plunger
opening is modelled in source only; its STL is not re-exported in this milestone.

## Two lock designs (swap pending)

Two shoulder-lock designs exist in the working tree on 2026-09-12:

- `cad/stance-lock.scad`: a GN817 direct-pull pin at Z 345 into a drilled steel receiver block, from a
  separate Codex session. It is included by the assembly now. No release actuator and no engagement
  sensor are modelled.
- `cad/stance-lock-sensed.scad`: this milestone's sensed design. The GN 412 spring plunger seats in
  one of two GN 412.2 receivers, an SS-01GL switch is pressed only by the seated knob, and an MG995
  lever does the release.

Why the sensed design meets the locked requirement:

- The requirement is that engagement is SENSED and never inferred from actuator position. The switch
  is pressed through the knob collar, and the knob is rigid with the pin. With 0.9 ±0.2 mm set
  overtravel and the 0.8 mm differential, a closed switch guarantees at least 3.1 mm of pin in the
  bushing. A pin that is blocked on the ring face, pulled, or partly in reads "not engaged".
- Post position plays no part in the reading. The release is motorized, so the transition can be
  interlocked.
- The plunger spring holds or re-seats the pin when power is lost.

The GN817 model has no sensor or motorized release, so it does not yet show either property.

The swap is authorised only after the Codex session stops. It needs exactly these anchored hunks.

`cad/r2d2.scad`:

1. `include <stance-lock.scad>` becomes `include <stance-lock-sensed.scad>`.
2. `front_clearance()`: `guide_frame()translate([-42,-34,5])cube([120,58,235]);` becomes
   `guide_frame()translate([-30,-34,5])cube([60,94,235]);`.
3. `body_upper()`: `lock_shell_clearance();` becomes `sl_shell_clearance();`.
4. `leg()`: delete `lock_receiver_pad();`.
5. `assembly()`: delete the `lock_receiver_metal()` and `lock_receiver_keeper()` lines.
6. `assembly()`: before the centre foot, insert `sl_stance_lock_leg();color(SL_PRINT)scale([-1,1,1])sl_shoulder_spacer();`.
7. `assembly()`: in `body_pose(...)`, replace `stance_lock_assembly(...)` with `sl_stance_lock_body(0);`.
8. `assembly()`: replace the battery cube with
   `translate([BATTERY_X-35.5,BATTERY_Y-33,BATTERY_Z-56])cube([71,66,112]);`.
9. Part selectors: replace `lock_mount`, `lock_receiver_keeper` and `lock_drill_jig` with `sl_lock_ring`,
   `sl_knob_collar`, `sl_release_lever`, `sl_shoulder_spacer` and `sl_race_spacer`. Their bed
   transforms are in `scripts/check_kinematics.py` `_placed_print_transform`.

`scripts/export_cad.py`: in `DEVELOPMENT_PARTS`, replace `'lock_mount':1,'lock_receiver_keeper':1,'lock_drill_jig':1`
with `'sl_lock_ring':1,'sl_race_spacer':1,'sl_shoulder_spacer':1,'sl_knob_collar':1,'sl_release_lever':1`.

`cad/printed-frame.scad`: the hunks below were applied in scratch to the 2026-09-12 21:22 file
(sha256 prefix fb580bebfdae). Each anchor matched exactly once. The old text is the anchor.

- P1 guide at GUIDE_ANGLE with printed lands, no pad screws: 26 anchor line(s) replaced by 23 line(s).
  Old: the whole block starting `module pf_front_guide_frame(){`.
  New:
  ```
  module pf_front_guide_frame(){guide_frame()children();}
  module printed_post_guide(){
   difference(){union(){
    pf_front_guide_frame(){
     translate([-23,-23,-GUIDE_LENGTH])cube([46,46,GUIDE_LENGTH]);
     printed_post_mount();
    }
    // Diagonal ties to the 2020 uprights: the front pair clears the standing battery.
    for(level=[[320,52],[340,-52]])for(x=[-72,72]){
     translate([x,level[1],level[0]-14])pf_round_box(33.2,33.2,28,3);
     hull(){translate([x-5,level[1]-10,level[0]-10])cube([10,20,20]);
      translate([-23,GUIDE_Y+(GUIDE_Z-level[0])*tan(GUIDE_ANGLE)-10,level[0]-10])cube([46,20,20]);}
    }
   }
   // Printed sliding lands, 21.0 mm square, with 26 mm relief between them; no pads or pad screws.
   pf_front_guide_frame(){
    translate([-10.5,-10.5,-GUIDE_LENGTH-1])cube([21,21,GUIDE_LENGTH+2]);
    for(span=[[-GUIDE_LENGTH-1,GUIDE_LAND_A-GUIDE_LAND_LENGTH/2],[GUIDE_LAND_A+GUIDE_LAND_LENGTH/2,GUIDE_LAND_B-GUIDE_LAND_LENGTH/2],[GUIDE_LAND_B+GUIDE_LAND_LENGTH/2,1]])
     translate([-13,-13,span[0]])cube([26,26,span[1]-span[0]]);
   }
   for(level=[[320,52],[340,-52]])for(x=[-72,72])pf_rail_socket(x,level[1],level[0]-15,30);
   }
  }
  ```
- P2 post adapter and fixed clevis for the front actuator: 25 anchor line(s) replaced by 33 line(s).
  Old: the whole block starting `module printed_post_adapter(){`.
  New:
  ```
  module printed_post_adapter(){
   // Guide-local coordinates about the rod-end centre. The M12 nut is captured; two printed pins retain the drilled rail.
   difference(){union(){
    translate([-20,-20,-97.5])cube([40,40,65]);
    translate([-12,18,ACTUATOR_ROD_EYE-9])cube([24,ACTUATOR_Y-26,18]);
    for(x=[-12,5])translate([x,ACTUATOR_Y-8,ACTUATOR_ROD_EYE-9])cube([7,16,18]);
    translate([-37.5,-29,-7])cube([17,10,14]);
    translate([-37.5,-20,-7])cube([4,30,14]);
    // Steering-link arm web: joins the block only below the ankle-stop sweep (guide-local Z < -32.5).
    translate([-37.5,-29,-40])cube([17,10,47]);
    translate([-21,-29,-40])cube([2,10,7]);
   }
   translate([-10.6,-10.6,-97.6])cube([21.2,21.2,35.2]);
   translate([0,0,-56])cylinder(d=12.5,h=24);
   translate([0,0,-49])cylinder(d=22.4,h=10.5,$fn=6);
   // Accessible nut insertion from the side; load bears on an integral10mm ledge.
   translate([-12,-30,-49])cube([24,30,10.5]);
   for(z=[-87,-73])translate([0,0,z])pf_xhole(4.3,44);
   translate([0,ACTUATOR_Y,ACTUATOR_ROD_EYE])pf_xhole(4.5,36);
   translate([-5,ACTUATOR_Y-10,ACTUATOR_ROD_EYE-10])cube([10,20,20]);
   translate([-35.5,0,0])pf_xhole(3.4,8);
   }
  }
  module printed_post_mount(){
   // Fixed clevis for the Actuonix P16 rear eye, in front of the guide (guide-local +Y).
   difference(){union(){
    translate([-12,20,ACTUATOR_FIXED_PIN-9])cube([24,12,16]);
    for(x=[-12,5])translate([x,ACTUATOR_Y-8,ACTUATOR_FIXED_PIN-9])cube([7,16,16]);
   }
   translate([0,ACTUATOR_Y,ACTUATOR_FIXED_PIN])pf_xhole(4.5,40);
   translate([-5,ACTUATOR_Y-10,ACTUATOR_FIXED_PIN-10])cube([10,20,20]);
   }
  }
  ```
- P3 front_post rail length and actuator envelope: 1 anchor line(s) replaced by 1 line(s).
  Old:
  ```
   color("#a3adb7")translate([0,0,L-372.5])extrusion_2020(310);
  ```
  New:
  ```
   color("#a3adb7")translate([0,0,L-POST_RAIL_END-POST_RAIL])extrusion_2020(POST_RAIL);
  ```
- P3b front_post actuator and pads: 3 anchor line(s) replaced by 5 line(s).
  Old:
  ```
   color("#252e38")translate([44.5,-10,-29])cube([36,20,112]);
   color("#a3adb7"){translate([55,0,-37])pf_xhole(9,8);translate([55,0,83])cylinder(d=8,h=L-83);translate([55,0,L])pf_xhole(9,6);}
   for(t=[-130,-20])for(a=[0:90:270])color("#333e49")rotate([0,0,a])translate([10.6,-9,t-10])cube([2.4,18,20]);
  ```
  New:
  ```
   // Actuonix P16-100 envelope in front of the post: case, rod and both eyes; pins along guide-local X.
   color("#252e38")translate([-18,ACTUATOR_Y-10,ACTUATOR_FIXED_PIN+8])cube([36,20,112]);
   color("#a3adb7"){translate([0,ACTUATOR_Y,ACTUATOR_FIXED_PIN])pf_xhole(9,8);
    translate([0,ACTUATOR_Y,ACTUATOR_FIXED_PIN+120])cylinder(d=8,h=L+ACTUATOR_ROD_EYE-ACTUATOR_FIXED_PIN-120);
    translate([0,ACTUATOR_Y,L+ACTUATOR_ROD_EYE])pf_xhole(9,6);}
  ```
- P4 centre-foot ankle stop bars: 1 anchor line(s) replaced by 6 line(s).
  Old:
  ```
     for(x=[-20,8])translate([x,-15,76])cube([12,30,52]);
  ```
  New:
  ```
     for(x=[-20,8])translate([x,-15,76])cube([12,30,52]);
     // Printed ankle stops: bars across the fork gap meet the M12 rod-end shank (radius 24, shank + bar = 9 mm).
     for(psi=[GUIDE_ANGLE-ANKLE_STOP_HEEL-asin(9/24),GUIDE_ANGLE+ANKLE_STOP_TOE+asin(9/24)])let(y=-24*sin(psi),z=ANKLE_Z+24*cos(psi)){
      translate([0,y,z])pf_xhole(6,40);
      for(x=[-20,8])hull(){translate([x,y-3,z-3])cube([12,6,6]);translate([x,max(-15,min(9,y-3)),min(z-3,122)])cube([12,6,6]);}
     }
  ```
- P5 purchased collars and spacer replaced by printed spacers: 2 anchor line(s) replaced by 0 line(s).
  Old:
  ```
   color("#a3adb7")translate([122,0,390])rotate([0,90,0])ring(8,6.35,6.5);
   color("#66717b")translate([128.5,0,390])rotate([0,90,0])ring(14,6,11);
  ```
  New: deleted.
- P6 clevis now part of printed_post_guide: 1 anchor line(s) replaced by 1 line(s).
  Old:
  ```
    printed_post_guide();pf_front_guide_frame()printed_post_mount();
  ```
  New:
  ```
    printed_post_guide();
  ```
- P7 remove GN817 frame anchor (swap only): 1 anchor line(s) replaced by 0 line(s).
  Old:
  ```
    lock_frame_anchor();
  ```
  New: deleted.
- P8 sensed lock mount, rail deck slot: 2 anchor line(s) replaced by 6 line(s).
  Old:
  ```
    translate([-88,0,390])rotate([0,90,0])cylinder(d=36,h=176);
   }
  ```
  New:
  ```
    translate([-88,0,390])rotate([0,90,0])cylinder(d=36,h=176);
    sl_lock_mount_positive();
   }
   sl_lock_mount_negative();
   // The retracted post rail passes up through the upper deck.
   guide_frame()translate([-12,-12,POST_ZERO+POST_MIN-POST_RAIL_END-POST_RAIL-3])cube([24,24,POST_RAIL+POST_RAIL_END-POST_ZERO-POST_MIN-GUIDE_LENGTH+3.5]);
  ```
- P9 tray opening for the steering arm: 1 anchor line(s) replaced by 1 line(s).
  Old:
  ```
   translate([-28,27,165])cube([56,49,65]);
  ```
  New:
  ```
   translate([-40,27,165])cube([68,49,65]);
  ```
- P10 leg-core backing face for the receiver bushings: 2 anchor line(s) replaced by 3 line(s).
  Old:
  ```
  module leg_core(){
   difference(){union(){translate([-16,-19.5,-277])cube([32,39,236]);
  ```
  New:
  ```
  module leg_core(){
   difference(){union(){translate([-16,-19.5,-277])cube([32,39,236]);
   translate([-16,-26,-72])cube([6,52,34]); // backing face for the two sensed-lock receiver bushings
  ```

After the swap, re-export these meshes from the assembly and re-run both kinematic checks:
`frame_chassis`, `post_adapter`, `center_foot_core`, the upper shell with the slot, and the `sl_` prints.

## Mass and centre of gravity

The CG comes from actual meshes plus catalogue masses:
- Printed parts use mesh volume × PETG 1.27 or PLA 1.24 g/cm³.
- The fill ratio of each revision C print comes from its sliced installed-model mass in
  `cad/h2d-structure-check.json`. Unsliced development prints use 0.5 of solid.
- Purchased parts use catalogue masses at their CAD positions.
- Allowances: electronics and wiring 600 g, at the front upper bay (Y 45, Z 340); paint and
  straps 100 g; fasteners 150 g.

Estimated total: 7.31 kg, from the shared meshes present on 2026-09-12. This is not a weighing.

Two layout decisions set the CG:
- The Bioenno battery stands beside the post at X 60, Y 0 (71 × 66 × 112 mm).
- The electronics bay is at the front.

Together these put the unlocked body CG ahead of the hip. The post can then hold the body
during the lean while the whole-robot CG stays over the side feet. The ±8 mm box stands for
layout and mass error. The built robot must be weighed and its CG measured before any stance
change. The battery position is the trim.

## Electrical requirements for the DFR0994 controller

- P16: 12 V supply; stall 1.0 A at 12 V; 20 % duty.
  - The Romeo DRV8876 channels are all allocated and share a 5.7 V VM rail, so the P16 needs
    its own H-bridge rated ≥12 V and ≥1 A continuous, with two 3.3 V logic inputs.
  - Feed the feedback potentiometer from 3.3 V: the wiper gives 0-3.3 V to an ESP32-S3 ADC1
    input or the ADS1115.
  - Two NC travel limits open at 0.3 mm and 99.7 mm.
- Lock sensor: SS-01GL dry contact.
  - COM to GND, NO and NC to two 3.3 V GPIO inputs with 3.3 kΩ pull-ups (controls agent
    wiring).
  - Engaged means NO closed. A broken wire reads "not engaged".
  - 3.3 V at 1 mA is below Omron's 5 VDC 1 mA minimum-load reference, so verify contact
    reliability.
- Release servo: 5 V servo supply; 5 V-buffered PWM. It needs no current path when unpowered.

## Assumptions

Each assumption below is stated in the check. None is measured.

- Guide land friction μ = 0.35 (PETG on anodised aluminium).
- Pin friction μ = 0.3.
- Rolling drag ≤10 N.
- Dynamic factor 3; release factor 1.5.
- Development-print fill 0.5.
- Electronics, fastener and paint allowances and their positions.
- SS-01GL body top 7.3 mm from the hole line: an envelope assumption. OP and OT are catalogue
  values.
- MG995 ear and horn geometry is an envelope; fit the delivered horn to the lever pocket.
- Heel-stop resting depends on the computed foot CG; weigh the built foot.
- The pin tip chamfer is drawn but not dimensioned. Seating relies on the 0.1 mm clearance and
  a slow creep.

## Not physically validated

- The masses, CG, friction, rolling drag and actuator force are calculated.
- Printed land wear, printed lock ring and mount strength, pin bending, bushing retention and
  creep are untested. No printed strength rating is claimed.
- Switch calibration, lock seating during the creep, and power loss during a transition need
  the built prototype.
- The rev C covers `stl/body_upper.stl` and `stl/rear_foot.stl` are outside this milestone. The
  upper shell needs the plunger opening added in `cad/r2d2.scad` before it is re-exported.
- The five `sl_` prints (`stl/development/sl_*.stl`) are checked as closed single solids by
  `check_kinematics.py`. Until the swap they are not in `export_cad.py --check-development`, and
  they are not sliced for the H2D.
