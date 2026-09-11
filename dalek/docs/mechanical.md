# STACK-10 mechanical design and assembly

The revised Dalek has one reinforced motor base and complete body sections that stack vertically. There are exactly ten STL files. Print one of each, except `07_pitch_carrier.stl`, which is printed twice. This makes eleven printed pieces. Each STL is one connected physical part. The base is 300 x 280 mm. Nominal assembled height is 543.8 mm (21.4 inches), below the 914.4 mm limit.

The four Adafruit 3777 motors, four Adafruit 3766 wheels, rear original TTGO T-Display, four MG92B arm servos, FS5103R head servo, selected battery and electrical system are retained. Motor pockets, battery retention, body bumps, display frame, yaw mounts, neck rings, bearing housing, head hub, eye and lamps are integral features. Purchased fasteners, spacers, clamp strips and two FR4 electronics mounting plates complete the assembly. There are no quarter-panel seams or separate printed mounting blocks.

No component has been physically printed or load-tested. Mesh and slicer checks establish digital acceptance. They do not establish layer strength, hub engagement, motor capability or runtime. Complete the physical gates below.

## Print inventory and H2D settings

Use a 0.4 mm nozzle and 0.20 mm layers. The base uses single-nozzle mode with an 8 mm brim. Rotate the base and lower ring 90 degrees about Z so their 300 mm dimension runs along printer Y. The base plus brim then occupies296 x316 mm. Centre these parts at X175,Y160 in the H2D machine coordinates. This fits both nozzle-specific areas. Keep the floor on the bed; for CLI use include --ensure-on-bed. The H2D single-nozzle volume is325 x320 x325 mm. Do not accept auto-arrangement that clips the brim at a nozzle-specific edge. [Bambu Lab H2D specification sheet](https://cdn1.bambulab.com/documentation/h2d/en/H2D_Laser_Full_Combo_20250305.pdf).

1. `01_base.stl`: one PETG base, floor down and rotated90 degrees about Z. Use six walls, six top and bottom layers, 40% gyroid and an 8 mm outer brim. Enable normal automatic supports beneath wheel-well roofs and clamp overhangs. Remove them through the bottom wells. The base has a 6 mm floor, 4 mm perimeter wall and 4 mm main ribs. Ribs reach local Z26. The perimeter reaches Z54; its tongue reaches Z57.
2. `02_lower_skirt.stl`: one complete PLA ring, large opening down and rotated90 degrees about Z. Use four walls, 15% infill, 5 mm brim and normal automatic supports under the integral bumps. Body height is 110 mm plus a 3 mm tongue. It changes from a rounded 300 x 280 mm rectangle to a 250 mm circle.
3. `03_upper_skirt.stl`: one complete PLA ring, large opening down without the90-degree rotation. Use four walls,15% infill,5 mm brim and tree supports under bumps. It changes from250 to220 mm diameter over100 mm, plus a3 mm tongue.
4. `04_shoulder.stl`: one PETG ring, bottom flange down. Use four walls, 25% infill, 5 mm brim and tree supports under the arm shelves. Display frame, speaker baffle and both yaw mounts are integral.
5. `05_neck.stl`: one PETG part, bottom flange down. Use four walls, 30% infill, 5 mm brim and supports under the deck and suspended servo floor. All rings, posts, bearing seats and the head-servo cradle are integral.
6. `06_head.stl`: one PLA head, hub foot down. Use four walls, 15% infill, 5 mm brim and tree supports beneath the pulley, inside the dome and below the eye. Remove supports through the open underside and 24 mm crown hole. Clear the bearing foot and belt groove completely.
7. `07_pitch_carrier.stl`: two identical PETG carriers, floor down, four walls, 30% infill and 5 mm brim.
8. `08_plunger_arm.stl`: one PLA arm in its supplied orientation. Use four walls, 15% infill, 5 mm brim and supports below the cup.
9. `09_emitter_arm.stl`: one PLA decorative arm in its supplied orientation. Use four walls, 15% infill, 5 mm brim and supports below the rods. It has no projectile mechanism.
10. `10_servo_pulley.stl`: one PETG pulley, large rim down, four walls, 30% infill and 5 mm brim. The supplied servo horn provides the spline connection.

Paint the integral bumps, eye and lamps after support removal. No extra decorative print files are needed. The assembled arms and eye extend outside the base. Every individual part fits the stated printer volume; the complete assembled robot does not fit as one print.

## Evidence and coordinate map

`cad/validation.json` checks the ten-file inventory, positive volume, watertight surfaces, one connected positive solid per file, and H2D fit with brim allowance. `bom/printed-parts.csv` records actual mesh dimensions. `cad/h2d-slice-check.json` records real local slicing and exact STL hashes. `docs/revision-review.md` records independent interface sampling and tool-access checks.

The combined solid-volume material bound is 2876.1 g, using 1.24 g/cm3 for PLA and 1.27 g/cm3 for PETG. This is not installed print mass. Use the slicer report for predicted deposition, separate removable support from installed material, then weigh the real build. Add the approximately 0.7 kg battery, motors, wheels, electronics and hardware. The stronger base increases drive load. A loaded-mass target and drive performance have not been proven.

The floor is world Z0. Positive Y is rear; positive X is right. Base local Z0 is nominal world Z13.8. This follows 31.5 mm wheel radius minus 6 mm support floor minus approximately 11.7 mm case-bottom-to-axle height interpreted from the motor drawing. Measure the actual motor and any pad before accepting this ground clearance.

- Base: world Z13.8-67.8, with tongue to70.8.
- Lower skirt: Z67.8-177.8, plus tongue.
- Upper skirt: Z177.8-277.8, plus tongue.
- Shoulder: Z277.8-377.8, plus tongue. Speaker centre Z327.8; rear PCB centre approximately Z342.3.
- Neck starts Z377.8. Its rings occupy local Z0-6,15-19 and30-34. The bearing deck begins local Z40.
- Lower bearing: world Z417.8-424.8. Upper bearing: Z436.8-443.8. A 12 mm metal spacer sits between their inner races.
- Head hub foot: Z444.8. Dome rim: Z468.8. Crown: Z533.8. Lamp tops: Z543.8.
- Wheel axes: Y+60 and-60, world Z31.5. Illustrative wheel centres are X+122.5 and-122.5. The wells accommodate centres from120 to125 mm in magnitude. Actual centres follow fully seated purchased hubs.

Each body interface uses four M4x20 bolts. Flanges are 18 mm wide and 6 mm thick. Base-to-lower holes are X+137/X-137 at Y0 and Y+127/Y-127 at X0. Lower-to-upper holes are at radius112. Upper-to-shoulder and shoulder-to-neck holes are at radius97. All circular patterns use angles0,90,180,270 degrees.

The tongue is 2 mm wide, 3 mm high and starts 4.5 mm inward from the outline. Its groove is 2.6 mm wide and 3.3 mm deep, giving 0.3 mm side clearance. Flange faces must seat fully. The tongue locates the joint; through bolts retain it. No structural joint depends on glue.

## Check actual components before a large print

Adafruit3777 is a 3-6 V TT motor. Its drawing shows 70 mm length, 18.60 mm gearbox width, 22.44 mm case height and 36.60 mm across axle ends. Motor-end tabs can reach22.40 mm across. The saddle has24 mm clear width, with padding for the narrower gearbox. Both shaft ends remain clear. [Motor](https://www.adafruit.com/product/3777), [dimension drawing](https://cdn-shop.adafruit.com/product-files/3777/3777_diagram.jpg).

Adafruit3766 is the specified63 x29 mm press-fit wheel. Fit one fully to one motor before printing the base. Measure its inner and outer tyre faces, shaft engagement and gearbox clearance. The120-125 mm model range is an accommodation envelope, not a measured hub dimension. Never leave a wheel partly engaged to match a picture. If the actual fully seated wheel lies outside the well, change the local well dimension and re-export the base before printing. Preserve the full6 mm floor beneath the gearbox. [Wheel](https://www.adafruit.com/product/3766).

Use the four MG92B servos' supplied horns and centre screws. Measure case and horn-face height before choosing pads. Mounts use pads and cable ties rather than copied spline teeth or uncertain ear holes. [MG92B](https://www.adafruit.com/product/2307).

The FS5103R drawing gives a40.15 x20.15 mm case,54 mm across ears,37.2 mm case height and42.85 mm to spline top. Its output is10.05 mm from the case centre along the length. The neck's support face is local Z34. Target horn mounting face is Z79; select pads from the measured horn. Target output is X72.5,Y0. Case envelope is X62.425-82.575,Y-10.025-30.125. [Adafruit servo](https://www.adafruit.com/product/154), [FeeTech drawing](https://evelta.com/content/datasheets/501-FS5103R.pdf).

The rear pocket is for the original ESP32 TTGO T-Display. The assumed PCB is51.52 x25.04 mm; the pocket is52.2 x26 mm. Measure the actual revision. The S3 and AMOLED boards are different. Screen, both buttons and USB must remain accessible. [Original board files](https://github.com/Xinyuan-LilyGO/TTGO-T-Display).

The speaker is Adafruit1313,77.8 x77.8 x25.49 mm with60 mm mounting centres. The battery pocket gives116 x76 mm plan clearance for the selected Bioenno BLF-1206A6Ah pack and padding. Reserve30 mm behind the battery connector and restrain its lead separately. [Speaker drawing](https://cdn-shop.adafruit.com/product-files/1313/C2464-001_datasheet.pdf).

## Prepare the base and fit the motors

1. Remove support from each wheel well, saddle, axle port, cable exit and bolt bore. Check the6 mm motor floor is clear. Inspect the floor, ribs and perimeter for cracks or incomplete layers. Reject a warped base that puts motor cases at different heights. Gauge M3/M4 holes with real screws; never scale the whole base to adjust one fit.
2. Mate each wheel fully with its motor outside the base. Keep the hub free of glue. Insert the four pairs from above. Motor X centres are+95/-95; axle Y coordinates are+60/-60. Bodies point toward the middle, with wire ends near Y+3/-3. The central notches let wires turn upward. Reserve approximately25 mm above the case for the wire bend and strain relief.
3. Cases sit directly on the main floor. Use thin side pads to locate them. Keep pads off both shafts. Under-case pads change ground clearance; use them only for a measured axle correction and apply the same correction at all four wheels.
4. Put two43 x8 x1 mm stainless strips across each motor end. Drill two3.4 mm holes37 mm apart in each strip,3 mm from the ends. Deburr them. In each mirrored motor quadrant, bolt centres are X76/X113 at Y8 andY18. Put nonconductive foam between strip and motor. Keep strips away from terminals. Adjust pad thickness so each strip sits flat on its29 mm-high bosses while holding the case gently.
5. Install four M3x40 bolts per motor with washers above strips and below the floor, then M3 nuts. Tighten evenly without crushing the gearbox. The pocket walls resist sideways motion. Strips retain the motor directly against the floor; there are no hanging printed motor towers.
6. Turn every wheel by hand through a full revolution. Confirm complete shaft engagement, both shaft-end clearances, tyre runout and free wiring. Each well spans outer-quadrant X105-142,Y26-96 and reaches local Z52. At X120 the nominal tyre inside face is X105.5. The nominal tyre top is Z49.2, giving2.8 mm roof clearance. Actual runout must still leave clearance; any rubbing fails the fit gate.
7. Route suppression capacitors and wires through the upper exits. Add strain relief to the fixed base. Do not route wiring through a wheel well. Recheck wheel freedom after wiring.

## Attach the lower ring and electronics

1. Attach the complete lower ring to the empty base before mounting electronics. Put M4 nuts and washers below the base's upper flange. Seat the tongue, then install four M4x20 bolts and washers through the skirt. A150 mm long3 mm ball-end driver rated for at least20 degrees reaches the heads through the smaller top opening. The X bolts need about18.4 degrees inward angle; Y bolts need13.3 degrees. Hold nuts with a7 mm spanner. Seat faces evenly; do not pull a misaligned tongue into place with bolt force.
2. Make two electronics plates from purchased unclad FR4 sheet,180 x72 x2 mm. Round and deburr edges. Front plate spans X-90 to90,Y-123 to-51. Rear plate spans X-90 to90,Y51 to123. Drill2.8 mm base-mount holes at X+54/X-54 with front Y-91/Y-63 and rear Y65/Y93. These align with the base's slotted mounts. The plates are purchased hardware, not additional prints.
3. Mount plates with eight25 mm nylon spacers and eight M2.5x40 screws, nuts and washers. The integral mounting pads reach local Z9, placing plate undersides at Z34. This clears26 mm ribs and28.44 mm nominal motor tops. Confirm two full threads beyond each nut and keep fasteners clear of motor terminals. Each plate can be removed separately.
4. Lay out actual boards and connectors before drilling PCB holes. Each Adafruit1609 protoboard is51 x81 mm with73.7 mm mounting-hole spacing. Put one on each plate, nominal centre X-35,Y-87 orY87. Put the PCA9685 near front X52,Y-70; the two motor/servo regulators near X32,Y-101 and X32,Y101; drivers near X65,Y-101 and X65,Y101. Use the rear plate's remaining right-hand area for the small logic regulator and audio amplifier.
5. Mark actual PCB holes on the FR4 plates, then drill them. This avoids assuming one mounting pattern for all boards. Do not drill a PCB. Mount boards on6 mm nylon spacers with M2.5x16 screws. The hardware kit supplies up to32 PCB fixing points; unused pieces are spares. Leave connector access and airflow around regulators. No fastener may touch a trace or component.
6. Keep the battery removable through the open body. Reserve30 mm beyond its rear connector; route its lead above the rear electronics plate where needed. Keep heavy-current wiring separate from small signal wires. Add labelled disconnects and service loops for the upper body.
7. Pad the116 x76 mm battery pocket. Thread two independent20 mm straps through the22 x4 mm slots at X+35/X-35,Y+34/Y-34. Strap the pack firmly enough to stop movement during a gentle manual tilt. Remove it for charging and transport. Do not add ballast.
8. Complete electrical tests with upper body sections off. The electronics remain attached to the base when the body rings are lifted.

## Stack the body and fit rear controls

1. Seat the upper skirt on the lower tongue. Fit four M4x20 bolts, eight washers and four nuts at radius112. Reach lower heads with the ball-end driver at about14.6 degrees inward. Do not force a warped ring.
2. Before fitting the shoulder, mount the speaker in its integral baffle with the cone facing forward. Use four M3x20 screws, eight washers and four nuts. Holes are X+30/-30, shoulder-local Z20/Z80. The sound opening is69 mm. Add a thin foam gasket and tab shims only if needed for surround clearance. Confirm two full threads beyond each nut. Nothing may contact the moving cone. Acoustic cloth outside the baffle can protect it.
3. Insert the T-Display from inside the shoulder. PCB back is nominal Y108 and front Y110. Orient USB toward the side notch. Confirm that both buttons move and glass carries no retaining load.
4. Use four nonconductive20 x8 x1 mm retaining tabs cut from nylon or polycarbonate strip. Each has a3.4 mm hole3 mm from its outer end, leaving17 mm inward reach. Bolts are at X+34/-34 and shoulder-local Z56/Z73. The tabs reach across the8.24 mm gap to the PCB edge; normal small M3 washers alone cannot retain it. Place tiny pads only at bare PCB edges, keeping the remainder of the tab clear of components.
5. Fit the four M3x25 bolts with washers and nuts. Tighten without bowing the board. Check USB cable insertion with the board retained. The integral frame stays attached to the shoulder; only tabs and PCB are removed for service.
6. Mount both switches in12.5 mm rear holes at X+30/-30, local Z23, using supplied panel hardware. Preserve MAIN and ACTUATORS OFF labels and wiring. Keep terminals clear of the board and harness.
7. Attach the shoulder to the upper skirt with four M4x20 bolts, eight washers and four nuts at radius97. The front head has a9 mm baffle recess. Use about5.6 degrees inward driver angle. Connect labelled harness plugs and leave slack to lift the shoulder.

## Build and calibrate the arms

1. Centre the four MG92B servos with firmware before fitting horns. Use the electrical guide's5 V signal levels. Shelf tops are shoulder-local Z58 at X+48/-48. Pad each yaw servo so its output lies at Y-131 and the supplied horn mounting face is near Z90. Measure the actual case and horn.
2. Secure each yaw servo with two ties through shelf slots. Keep ties clear of the horn. The case must sit against fixed cheeks without sideways shaft load. Integral gussets carry shelf load into the shoulder.
3. Attach one pitch carrier to each yaw horn with two M2x10 screws, washers and nuts through opposite radial slots. Use the supplied spline centre screw through the5 mm access hole. If needed, drill two2.1 mm holes in the removable horn using the carrier as a template. Never drill the servo or replace the spline with printed teeth.
4. Pad each pitch servo against its carrier's vertical wall, output toward negative X. Output centre is nominal30 mm above carrier floor on carrier Y0. Secure it with two ties. Route its cable in a loose U-shaped loop to the fixed shoulder, with strain relief at both ends.
5. Attach the plunger and emitter to the pitch horns, pointing forward at neutral. Use two M2x10 screws per arm through the slots perpendicular to its tube, plus the supplied centre screw. Check unpowered movement first.
6. Begin with plus/minus2 degrees at0.10 Hz. Run20 slow circles before increasing to the firmware limit. The two axes use sine and cosine commands one quarter-cycle apart. The tips trace circles; shafts do not spin continuously. Stop for contact, taut cables or continuous servo buzzing.

## Install the neck and rotating head

1. Bolt the complete neck to the shoulder first, with four M4x20 bolts, eight washers and four nuts at radius97. Use a3 mm L-key with short leg18 mm or less. Its vertical leg reaches the head at local Z6-10 while its handle turns between ring1 top Z19 and ring2 bottom Z30. The integral suspended servo cradle blocks a straight driver. Tighten these bolts before fitting the servo.
2. Insert the lower608 from below into the local Z40-47 seat. Insert the upper bearing from above into Z59-66. Put the purchased12 mm-long metal spacer,8.1 mmID and12 mmOD, between their inner races. Bearings should enter22.2 mm seats by hand pressure without cracking the tower.
3. Retain each outer race with three9 mm-OD steel washers and M3x8 plastic thread-forming screws in the2.6 mm pilots at radius14. Three washers go below the lower race and three above the upper race. They must clear the moving12 mm spacer and hub foot. Tighten gently; the housing supports the outer races and washers prevent axial escape.
4. Place an8 x12 x1 mm shim above the M8 bolt head. Insert the bolt from below through the lower bearing, metal spacer and upper bearing. Put the other narrow shim above the upper inner race. A standard wide washer against an inner race can lock the bearing; do not substitute one.
5. Seat the head's12 mm-diameter foot on the upper shim. Its8.5 mm bore passes the bolt. Drop the16 mm-OD washer and M8 nyloc nut through the24 mm crown opening. Use a13 mm socket with outside diameter no more than23 mm.
6. The axial stack above the bolt head is:1 mm shim;7 mm lower bearing;12 mm spacer;7 mm upper bearing;1 mm shim;27 mm printed hub; ordinary M8 washer; nyloc nut. M8x70 gives thread allowance. Confirm two full threads beyond the nut. Tighten only until play is removed, then check free rotation. Bolt, inner races, spacer and head rotate together; outer races and neck stay fixed. Do not hide bearing drag with more power.
7. Fit FS5103R in its lowered cradle, case bottom at local Z34, output near X72.5,Y0. Its case extends about10 mm forward and30 mm rearward of the shaft. Do not centre the54 mm ear span on the shaft. Pad it to put the actual horn mounting face at Z79, then retain it with two ties. Keep the output and wire clear.
8. Attach the printed servo pulley to the supplied horn using two M2x16 screws, washers and nuts, plus the supplied centre screw. The small groove root is20 mm diameter; the integrated head groove root is59 mm. Both groove centres must be at neck-local Z83.5.
9. Fit the83 mm-ID,3 mm-cord O-ring. Shaft spacing is nominal72.5 mm. Adjust the padded servo position for light tension. The servo shaft does not support head weight. Turn the head through two full turns by hand and check tracking. Then power it slowly in each direction and calibrate neutral.
10. Keep all wiring below the moving head. Eye and lamps are integral, decorative and unlit. No slip ring is needed. Check the eye's complete sweep. Optional removable opaque tape can cover the crown hole after commissioning; no printed cap is required.

## Physical acceptance and maintenance

These are proposed builder tests, not completed measurements or certified load ratings.

- Before installing motors, support all four motor-pocket floor regions on equal rigid blocks. Distribute twice the intended complete robot mass across the battery floor and stack-support positions for10 minutes. Keep the test close to the ground. Unload and inspect for cracks, loose layers or permanent distortion with a straightedge. Reject damage. This tests the intended base load path without loading motor shafts.
- Verify fully seated hubs and complete wheel clearance unpowered. Run on a stand first. Check polarity, current limits and stop response. Repeat with the finished robot.
- Weigh the loaded robot. Start on a level hard floor with slow starts and broad turns. Measure current and motor temperature during repeated starts and turns. Four wide tyres resist tight turns. Do not assume the TT motors can pivot in place, climb thresholds or drive on carpet because the base is strong.
- Run20 slow arm circles and a full head turn in each direction. Recheck fasteners after the first10 minutes.
- Confirm Wi-Fi loss and closing the browser stop motion, and ACTUATORS OFF remains reachable. Complete the electrical commissioning checklist before a demonstration.

To service the body, disconnect labelled harness plugs, remove the four bolts at the required horizontal joint and lift the complete section vertically. Remove shoulder before accessing upper-skirt bolts. Lift the upper skirt for access through the lower ring. Remove electronics plates for motor clamps or base nuts. Motor clamps are reached from above; the base remains one piece. Release four retaining tabs for PCB service. Remove the crown spindle nut for head removal and release belt tension. Inspect clamps, bearing retainers, belt, wire loops and printed layers before use.

Regenerate with `C:/Python314/python.exe scripts/export_cad.py --jobs 3`. Check with `C:/Python314/python.exe scripts/export_cad.py --check-only`. Each export has a240 second timeout. On Windows the script starts the actual hidden renderer so a timeout terminates it. A failed export stops the check. Regenerate STLs before rendering assembly views, which import the delivered meshes to avoid preview occlusion errors.
